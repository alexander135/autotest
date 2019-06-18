#version 0.1

FROM python:3.6-alpine

MAINTAINER Oleshko Alexander <oleshko-alex@mail.ru>

WORKDIR /code/

COPY uir/requirements.txt ./

RUN pip3.6 install --no-cache-dir -r ./requirements.txt

COPY . .

WORKDIR uir/

CMD python3.6 server.py
