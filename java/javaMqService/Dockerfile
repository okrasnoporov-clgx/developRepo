FROM maven:3.9.9-eclipse-temurin-11 AS build
WORKDIR /build
COPY pom.xml .
COPY src ./src
RUN mvn -B -DskipTests package

FROM eclipse-temurin:11-jre
WORKDIR /app
COPY --from=build /build/target/javaMqService-0.0.1.jar /app/app.jar
EXPOSE 8500
ENTRYPOINT ["java", "-jar", "/app/app.jar"]