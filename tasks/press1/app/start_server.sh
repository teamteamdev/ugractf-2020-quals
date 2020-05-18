#!/usr/bin/env bash

exec socat tcp-l:17493,reuseaddr,fork exec:"$(pwd)/worker.py $1"
