# javaMqService

HTTP-сервис Java 11 для запуска в контейнере, в том числе в AWS EKS. Использует JMS-клиент ActiveMQ для чтения состояния очереди Amazon MQ.

## Endpoints

- `GET /alpha/v1/info` возвращает `{"runtime":"java","app":"mq-java","version":"0.0.1"}`.
- `GET /q/v1/state` возвращает имя очереди и количество доступных для просмотра сообщений. При ошибке подключения или конфигурации отвечает `503`.

Количество вычисляется через JMS `QueueBrowser`: сообщения не извлекаются из очереди. Для больших очередей подсчет может занимать заметное время.

## Переменные среды

| Переменная | Обязательна | По умолчанию | Назначение |
| --- | --- | --- | --- |
| `HTTP_HOST` | нет | `0.0.0.0` | Адрес HTTP-сервера |
| `HTTP_PORT` | нет | `8500` | Порт HTTP-сервера |
| `AMQ_BROKER_URL` | для `/q/v1/state` | нет | JMS URL брокера, например `ssl://broker.example:61617` |
| `AMQ_QUEUE_NAME` | для `/q/v1/state` | нет | Имя очереди Amazon MQ |
| `AMQ_USERNAME` | зависит от настроек брокера | нет | Имя пользователя Amazon MQ |
| `AMQ_PASSWORD` | зависит от настроек брокера | нет | Пароль Amazon MQ; передавайте через Secret, а не в образе |

Для Amazon MQ ActiveMQ через TLS обычно используется порт `61617`. Сетевая политика/security group EKS должна разрешать соединение с брокером. Параметры клиента ActiveMQ, включая reconnect и timeout, можно задавать в `AMQ_BROKER_URL` согласно синтаксису ActiveMQ.

Топики и подписки сервис не использует: текущий API работает только с одной очередью, имя которой задается через `AMQ_QUEUE_NAME`.

## Сборка и запуск

```bash
mvn -f java/javaMqService clean package
java -jar java/javaMqService/target/javaMqService-0.0.1.jar
```

Для контейнерного запуска:

```bash
docker build -t mq-java:0.0.1 java/javaMqService
docker run --rm -p 8500:8500 \
  -e AMQ_BROKER_URL=ssl://broker.example:61617 \
  -e AMQ_QUEUE_NAME=my-queue \
  -e AMQ_USERNAME=my-user \
  -e AMQ_PASSWORD=my-password \
  mq-java:0.0.1
```