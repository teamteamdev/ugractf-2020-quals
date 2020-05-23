#!/bin/sh

rm -f /iswho/sock/iswho.sock
exec supervisord -c /iswho/supervisord.conf
