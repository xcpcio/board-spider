FROM python:3.10-bullseye

USER root
WORKDIR /root/board-spider
COPY . /root/board-spider

ENV DEBIAN_FRONTEND=noninteractive

RUN cd board-spider \
    && apt update \
    && apt dist-upgrade -y \
    && apt install --no-install-recommends --no-install-suggests -y \
    locales \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && poetry install \
    && curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash \
    && export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")" \
    && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" \
    && nvm install 16 \
    && cp docker/docker_entry.sh /root/docker_entry.sh \
    && chmod +x /root/*.sh

ENTRYPOINT ["/root/docker_entry.sh"]

CMD ["primary"]
