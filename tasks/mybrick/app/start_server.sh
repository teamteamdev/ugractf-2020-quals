#!/usr/bin/env bash
set -e

export MONGO_USER=root
export MONGO_PASS=mybricksecretpass111

if [[ ! -d $1/mongo ]]; then
    CREATE=1
fi

[[ CREATE -eq 1 ]] && mkdir $1/mongo
mongod --auth --dbpath $1/mongo --bind_ip $1/mongo.sock --logpath $1/mongo-logs &
if [[ CREATE -eq 1 ]]; then
  while [ ! -f $1/mongo.sock ]; do
    sleep 1
  done
  mongo --host $1/mongo.sock admin --eval "db.createUser({user: \"$MONGO_USER\", pwd: \"$MONGO_PASS\", roles: [{role: \"userAdminAnyDatabase\", db: \"admin\"}]})"
fi

./server.py $1
