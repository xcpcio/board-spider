FROM python:3.10-bullseye

ARG XCPCIO_BOARD_SPIDER_VERSION="0.0.0"

USER root
WORKDIR /root/board-spider
COPY . /root/board-spider

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update \
    && apt dist-upgrade -y \
    && apt install --no-install-recommends --no-install-suggests -y \
    locales \
    && pip install xcpcio-board-spider=="${XCPCIO_BOARD_SPIDER_VERSION}" \
    && curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash \
    && export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")" \
    && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" \
    && nvm install 16 \
    && cp docker/docker_entry.sh /root/docker_entry.sh \
    && chmod +x /root/*.sh

ENTRYPOINT ["/root/docker_entry.sh"]

CMD ["primary"]
