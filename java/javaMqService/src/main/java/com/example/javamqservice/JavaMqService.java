package com.example.javamqservice;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

import javax.jms.Connection;
import javax.jms.ConnectionFactory;
import javax.jms.JMSException;
import javax.jms.QueueBrowser;
import javax.jms.Session;
import javax.jms.Queue;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.Enumeration;

import org.apache.activemq.ActiveMQConnectionFactory;

public class JavaMqService {
    public static void main(String[] args) throws IOException {
        String host = env("HTTP_HOST", "0.0.0.0");
        int port = Integer.parseInt(env("HTTP_PORT", "8500"));
        QueueMonitor queueMonitor = new QueueMonitor(
                System.getenv("AMQ_BROKER_URL"),
                System.getenv("AMQ_USERNAME"),
                System.getenv("AMQ_PASSWORD"),
                System.getenv("AMQ_QUEUE_NAME"));

        HttpServer server = HttpServer.create(new InetSocketAddress(host, port), 0);
        server.createContext("/alpha/v1/info", new InfoHandler());
        server.createContext("/q/v1/state", new QueueStateHandler(queueMonitor));
        server.setExecutor(null);
        server.start();
        System.out.println("JavaMqService listening on " + host + ":" + port);

        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("Shutting down server...");
            server.stop(0);
        }));
    }

    private static String env(String name, String defaultValue) {
        String value = System.getenv(name);
        return value == null || value.isEmpty() ? defaultValue : value;
    }

    private static void sendJson(HttpExchange exchange, int status, String response) throws IOException {
        byte[] bytes = response.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        exchange.sendResponseHeaders(status, bytes.length);
        try (OutputStream output = exchange.getResponseBody()) {
            output.write(bytes);
        }
    }

    private static boolean isGet(HttpExchange exchange) throws IOException {
        if (!"GET".equalsIgnoreCase(exchange.getRequestMethod())) {
            exchange.sendResponseHeaders(405, -1);
            return false;
        }
        return true;
    }

    private static String jsonString(String value) {
        StringBuilder escaped = new StringBuilder("\"");
        for (int index = 0; index < value.length(); index++) {
            char character = value.charAt(index);
            switch (character) {
                case '"':
                    escaped.append("\\\"");
                    break;
                case '\\':
                    escaped.append("\\\\");
                    break;
                case '\b':
                    escaped.append("\\b");
                    break;
                case '\f':
                    escaped.append("\\f");
                    break;
                case '\n':
                    escaped.append("\\n");
                    break;
                case '\r':
                    escaped.append("\\r");
                    break;
                case '\t':
                    escaped.append("\\t");
                    break;
                default:
                    if (character < 0x20) {
                        escaped.append(String.format("\\u%04x", (int) character));
                    } else {
                        escaped.append(character);
                    }
            }
        }
        return escaped.append('"').toString();
    }

    static class InfoHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!isGet(exchange)) {
                return;
            }
            if (!"/alpha/v1/info".equals(exchange.getRequestURI().getPath())) {
                sendJson(exchange, 404, "{\"error\":\"not_found\"}");
                return;
            }
            sendJson(exchange, 200, "{\"runtime\":\"java\",\"app\":\"mq-java\",\"version\":\"0.0.1\"}");
        }
    }

    static class QueueStateHandler implements HttpHandler {
        private final QueueMonitor queueMonitor;

        QueueStateHandler(QueueMonitor queueMonitor) {
            this.queueMonitor = queueMonitor;
        }

        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!isGet(exchange)) {
                return;
            }
            if (!"/q/v1/state".equals(exchange.getRequestURI().getPath())) {
                sendJson(exchange, 404, "{\"error\":\"not_found\"}");
                return;
            }

            try {
                long messageCount = queueMonitor.getMessageCount();
                String response = "{\"status\":\"available\",\"queue\":"
                        + jsonString(queueMonitor.getQueueName())
                        + ",\"messageCount\":" + messageCount + "}";
                sendJson(exchange, 200, response);
            } catch (JMSException | IllegalStateException exception) {
                String configuration = queueMonitor.getSafeConfigurationJson();
                System.err.println("Queue state check failed ("
                        + exception.getClass().getSimpleName() + "): " + configuration);
                String response = "{\"status\":\"unavailable\","
                        + "\"error\":\"queue_unavailable\","
                        + "\"message\":\"Queue is not reachable. Please check configuration\","
                        + "\"configuration\":" + configuration + "}";
                sendJson(exchange, 503, response);
            }
        }
    }

    static class QueueMonitor {
        private final String brokerUrl;
        private final String username;
        private final String password;
        private final String queueName;

        QueueMonitor(String brokerUrl, String username, String password, String queueName) {
            this.brokerUrl = brokerUrl;
            this.username = username;
            this.password = password;
            this.queueName = queueName;
        }

        String getQueueName() {
            return queueName;
        }

        String getSafeConfigurationJson() {
            String safeBrokerUrl = brokerUrl == null || brokerUrl.isEmpty()
                ? "(not configured)"
                : brokerUrl.replaceAll("(?i)(://)[^/@(),]+@", "$1***@");
            int queryIndex = safeBrokerUrl.indexOf('?');
            if (queryIndex >= 0) {
            safeBrokerUrl = safeBrokerUrl.substring(0, queryIndex) + "?[redacted]";
            }

            String safeQueueName = queueName == null || queueName.isEmpty()
                ? "(not configured)"
                : queueName;
            return "{\"brokerUrl\":" + jsonString(safeBrokerUrl)
                + ",\"queueName\":" + jsonString(safeQueueName)
                + ",\"usernameConfigured\":" + (username != null && !username.isEmpty()) + "}";
        }

        long getMessageCount() throws JMSException {
            if (brokerUrl == null || brokerUrl.isEmpty() || queueName == null || queueName.isEmpty()) {
                throw new IllegalStateException("AMQ_BROKER_URL and AMQ_QUEUE_NAME must be configured");
            }

            ConnectionFactory factory = new ActiveMQConnectionFactory(brokerUrl);
            Connection connection = username == null || username.isEmpty()
                    ? factory.createConnection()
                    : factory.createConnection(username, password == null ? "" : password);
            Session session = null;
            QueueBrowser browser = null;
            try {
                connection.start();
                session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);
                Queue queue = session.createQueue(queueName);
                browser = session.createBrowser(queue);
                Enumeration<?> messages = browser.getEnumeration();
                long count = 0;
                while (messages.hasMoreElements()) {
                    messages.nextElement();
                    count++;
                }
                return count;
            } finally {
                closeQuietly(browser);
                closeQuietly(session);
                closeQuietly(connection);
            }
        }

        private static void closeQuietly(QueueBrowser browser) {
            if (browser != null) {
                try {
                    browser.close();
                } catch (JMSException ignored) {
                }
            }
        }

        private static void closeQuietly(Session session) {
            if (session != null) {
                try {
                    session.close();
                } catch (JMSException ignored) {
                }
            }
        }

        private static void closeQuietly(Connection connection) {
            try {
                connection.close();
            } catch (JMSException ignored) {
            }
        }
    }
}