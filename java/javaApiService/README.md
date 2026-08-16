# javaApiService

Simple Java HTTP service that listens on port 8500 and responds to `/alpha/v1/info` with a JSON payload.

Build:

```bash
mvn -f java/javaApiService clean package
```

Run:

```bash
java -jar java/javaApiService/target/javaApiService-0.1.0.jar
```
