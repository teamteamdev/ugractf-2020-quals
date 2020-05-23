#!/bin/sh

socat UNIX-LISTEN:/iswho/sock/iswho.sock,fork TCP4-CONNECT:3000 &
java -jar /iswho/iswho.jar
