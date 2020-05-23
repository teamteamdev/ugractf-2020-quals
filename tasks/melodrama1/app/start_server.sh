#!/usr/bin/env bash

rm -f $1/melodrama1.sock
exec socat -T30 unix-l:$1/melodrama1.sock,fork exec:"$(pwd)/worker.py $1"
