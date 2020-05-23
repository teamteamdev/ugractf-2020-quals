FROM openjdk:8-alpine
RUN apk add bash curl socat

RUN adduser -S -s /bin/bash iswho

RUN echo "alias pwd='echo /var/lib/iswho/private'" > /etc/profile; \
    chmod +x /etc/profile

RUN mkdir -p /iswho/sock
COPY run_internal.sh target/uberjar/iswho.jar /iswho/
VOLUME ["/iswho/sock"]
CMD ["/iswho/run_internal.sh"]
