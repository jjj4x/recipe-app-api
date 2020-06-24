FROM python:3.7-alpine

MAINTAINER max.preobrazhensky@gmail.com

ENV PYTHONUNBUFFERED=1

COPY\
    requirements.txt\
    entrypoint.sh\
    /

RUN\
    apk add --update --no-cache postgresql-client\
    && apk add --no-cache --virtual build-deps build-base postgresql-dev\
    && pip install --no-cache-dir -r /requirements.txt\
    && mkdir -p /app\
    && adduser -D user\
    && apk del build-deps \
    && rm -rf /root/.cache/* /tmp/* /var/tmp/*\
    && chmod 750 /entrypoint.sh\
    && chown user:user /entrypoint.sh

USER user
WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]

COPY ./app /app
