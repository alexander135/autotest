#version 0.1

FROM centos:7

MAINTAINER Oleshko Alexander <oleshko-alex@mail.ru>

WORKDIR /code/

COPY uir/requirements.txt ./

RUN yum install -y  https://centos7.iuscommunity.org/ius-release.rpm && yum clean all && rm -rf /var/cache/yum

RUN yum install -y python36u python36u-devel python36u-pip

RUN yum install -y cronie

RUN pip3.6 install --no-cache-dir -r ./requirements.txt

COPY . .

#EXPOSE 80

WORKDIR uir/

CMD python3.6 server.py
