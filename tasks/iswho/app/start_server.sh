#!/usr/bin/env bash
set -e

export SOCK_PATH=$1/sock
rm -f $SOCK_PATH/iswho.sock
exec docker-compose up
