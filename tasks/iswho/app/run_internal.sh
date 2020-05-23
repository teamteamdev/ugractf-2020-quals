#!/bin/sh

rm -f /iswho/sock/iswho.sock
socat UNIX-LISTEN:/iswho/sock/iswho.sock,fork,mode=0666 TCP4-CONNECT:127.0.0.1:3000 &
java -jar /iswho/iswho.jar
