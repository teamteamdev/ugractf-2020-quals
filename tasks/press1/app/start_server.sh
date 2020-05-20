#!/usr/bin/env bash

exec socat -T30 tcp-l:17493,reuseaddr,fork exec:"$(pwd)/worker.py $1"
