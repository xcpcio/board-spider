FROM python:3.10-bullseye

USER root
WORKDIR /root
COPY . /root/board-spider

ENV DEBIAN_FRONTEND=noninteractive

RUN cd board-spider \
    && apt update \
    && apt dist-upgrade -y \
    && apt install --no-install-recommends --no-install-suggests -y \
    locales \
    && python3 -m pip install -r requirements.txt \
    && curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash \
    && export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")" \
    && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" \
    && nvm install 16 \
    && cp docker/docker_entry.sh /root/docker_entry.sh

ENTRYPOINT ["/root/docker_entry.sh"]

CMD ["primary"]
