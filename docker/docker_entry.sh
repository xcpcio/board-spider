#! /bin/bash

set -e -x

NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
export NVM_DIR
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

if [ X"${1}" = X"primary" ]; then
    cd /root/board-spider
    exec python3 sync.py
else
    exec "${@}"
fi
