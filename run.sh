#!/bin/bash

# How to run gridbug
    docker run \
    -d \
    -p 8777:8777 \
    -e WEATHERCONF='/var/lib/gridbug/weather411.conf' \
    -v ${PWD}:/var/lib/gridbug \
    --name gridbug \
    --restart unless-stopped \
    jasonacox/gridbug

# Optional - pull bug list from URL
# export BUGLISTURL="http://localhost/gridbugs.json"
export GRIDBUGCONF="/var/lib/gridbug/gridbug.conf"

python3 gridbug.py
