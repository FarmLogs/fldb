FROM ubuntu:wily

RUN apt-get update \
    && apt-get -y install libpq-dev python-dev python-pip \
    && apt-get -y upgrade

RUN pip install --upgrade pip

RUN apt-get clean && rm -rf /tmp/*

COPY . /

RUN pip install -r requirements.txt
