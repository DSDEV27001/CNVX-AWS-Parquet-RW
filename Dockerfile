FROM python:3.8.3-slim-buster
MAINTAINER PyDevUK

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
RUN apt-get clean
RUN python3 --version

RUN mkdir /app
WORKDIR /app
COPY ./ /app

#security to avoid root account
RUN useradd user
USER user

