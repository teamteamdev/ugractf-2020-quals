FROM openjdk:8-alpine
RUN apk add bash
EXPOSE 3000

RUN adduser -S -s /bin/bash iswho

RUN apk add curl

RUN echo "alias pwd='echo /var/lib/iswho/private'" > /etc/profile; \
    chmod +x /etc/profile

COPY target/uberjar/iswho.jar /iswho/app.jar
CMD ["java", "-jar", "/iswho/app.jar"]