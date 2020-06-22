FROM python:3.8.3-slim-buster
MAINTAINER PyDevUK

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN apt-get -y update \
    && apt-get -y install --no-install-recommends gcc groff less unzip wget curl \
    && rm -rf /var/lib/apt/lists/*
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip && rm awscliv2.zip
RUN ./aws/install
#RUN wget https://www.python.org/ftp/python/3.8.3/Python-3.8.3.tgz
#RUN tar -xf Python-3.8.3.tgz
#RUN rm Python-3.8.3.tgz
RUN pip3 install -r /requirements.txt
RUN apt-get clean
RUN python3 --version

RUN mkdir /app
WORKDIR /app
COPY ./ /app

#security to avoid root account
RUN useradd user
USER user

