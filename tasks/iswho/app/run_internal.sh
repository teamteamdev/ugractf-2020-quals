#!/bin/sh

rm -f /iswho/sock/iswho.sock
socat UNIX-LISTEN:/iswho/sock/iswho.sock,perm-early=0666,fork TCP4-CONNECT:3000 &
java -jar /iswho/iswho.jar
