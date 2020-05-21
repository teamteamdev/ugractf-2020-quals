#!/usr/bin/env bash
set -e

# TODO: mongo
# mongod --auth --dbpath $1/mongo/ --bind_ip $1/mongo.sock &
# mongo --host $1/mongo.sock ""
./server.py $1
