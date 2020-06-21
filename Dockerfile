FROM python:3.7-alpine

MAINTAINER max.preobrazhensky@gmail.com

ENV PYTHONUNBUFFERED=1

COPY requirements.txt /

RUN\
   pip install -r /requirements.txt\
   && mkdir -p /app\
   && adduser -D user

USER user
WORKDIR /app

COPY ./app /app
