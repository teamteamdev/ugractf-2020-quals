#!/usr/bin/env bash

exec socat -T30 unix-l:$1/melodrama1.sock,fork exec:"$(pwd)/worker.py $1"
