#! /bin/bash

set -e -x

if [ X"${1}" = X"primary" ]; then
    cd /root/board-spider
    exec python3 sync.py
else
    exec "${@}"
fi
