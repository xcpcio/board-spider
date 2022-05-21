#! /bin/bash

set -e -x

if [ X"${1}" = X"primary" ]; then
    /bin/bash
else
    exec "${@}"
fi
