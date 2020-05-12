#!/usr/bin/env bash
set -e

cleanup() {
    docker-compose down
}

trap cleanup EXIT
docker-compose up -d
./server.py $1
