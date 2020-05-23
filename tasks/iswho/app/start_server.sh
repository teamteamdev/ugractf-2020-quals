#!/usr/bin/env bash
set -e

rm -f $1/sock/iswho.sock
exec docker-compose up
