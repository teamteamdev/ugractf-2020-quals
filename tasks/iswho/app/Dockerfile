FROM openjdk:8-alpine
RUN apk add bash curl socat supervisor

RUN adduser -S -s /bin/bash iswho

RUN echo "alias pwd='echo /var/lib/iswho/private'" > /etc/profile; \
    chmod +x /etc/profile

RUN mkdir -p /iswho/sock
COPY supervisord.conf target/uberjar/iswho.jar /iswho/
WORKDIR "/iswho"
VOLUME ["/iswho/sock"]
CMD ["supervisord", "-c", "/iswho/supervisord.conf"]
