#!/usr/bin/env bash
set -e

export SOCK_PATH=$1/sock
exec docker-compose up
