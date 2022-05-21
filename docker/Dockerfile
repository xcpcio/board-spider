FROM python:3.10-bullseye

USER root
WORKDIR /root
COPY . /root/board-spider

RUN cd board-spider \
    && python3 -m pip install -r requirements.txt \
    && curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash \
    && export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")" \
    && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" \
    && nvm install 16 \
    && cp docker/docker_entry.sh /root/docker_entry.sh

ENTRYPOINT ["/root/docker_entry.sh"]

CMD ["primary"]
