#!/bin/sh

socat UNIX-LISTEN:/iswho/sock/iswho.sock,fork TCP4-CONNECT:3000 &
chmod 666 /iswho/sock/iswho.sock
java -jar /iswho/iswho.jar
