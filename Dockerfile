FROM python:3.7-alpine

MAINTAINER max.preobrazhensky@gmail.com

ENV PYTHONUNBUFFERED=1

COPY\
    requirements.txt\
    entrypoint.sh\
    /

RUN\
    apk add --update --no-cache postgresql-client jpeg-dev\
    && apk add --no-cache --virtual build-deps build-base postgresql-dev musl-dev zlib-dev\
    && pip install --no-cache-dir -r /requirements.txt\
    && mkdir -p /app /vol/web/media /vol/web/static\
    && adduser -D user\
    && apk del build-deps\
    && rm -rf /root/.cache/* /tmp/* /var/tmp/*\
    && chmod 750 /entrypoint.sh\
    && chown user:user /entrypoint.sh\
    && chmod 755 /vol/web\
    && chown user:user -R /vol /app

USER user
WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]

COPY ./app /app
