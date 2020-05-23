#!/usr/bin/env bash
set -e

NEW_UUID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
export SOCK_PATH=$1/sock
exec docker-compose -p "$NEW_UUID" up
