#!/usr/bin/env bash
set -e

export MONGO_USER=root
export MONGO_PASS=mybricksecretpass111

if [[ ! -d $1/mongo ]]; then
    mkdir $1/mongo
    mongod --dbpath $1/mongo --bind_ip $1/mongo.sock --logpath $1/mongo-logs &
    for i in seq 1 5; do
        sleep 1
        if mongo --host $1/mongo.sock admin --eval "db.createUser({user: \"$MONGO_USER\", pwd: \"$MONGO_PASS\", roles: [{role: \"userAdminAnyDatabase\", db: \"admin\"}]})"; then
            DONE=1
            break
        fi
    done

    if [[ DONE -ne 1 ]]; then
        echo "Database creation failed."
        exit 1
    fi

    mongo --host $1/mongo.sock admin --eval "db.adminCommand( { shutdown: 1 } )"
    wait
fi

mongod --auth --dbpath $1/mongo --bind_ip $1/mongo.sock --logpath $1/mongo-logs &
sleep 5

./server.py $1
