#!/bin/sh

if [ -e /iswho/sock/iswho.sock ]; then
  echo "Removing old socket"
  rm -f /iswho/sock/iswho.sock
fi
socat UNIX-LISTEN:/iswho/sock/iswho.sock,fork,mode=0666 TCP4-CONNECT:3000 &
java -jar /iswho/iswho.jar
