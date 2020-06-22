FROM amazonlinux:2
MAINTAINER PyDevUK

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN yum -y upgrade
RUN yum -y install gcc groff less unzip wget python37 shadow-utils
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN rm awscliv2.zip
RUN ./aws/install
#RUN wget https://www.python.org/ftp/python/3.8.3/Python-3.8.3.tgz
#RUN tar -xf Python-3.8.3.tgz
#RUN rm Python-3.8.3.tgz
RUN pip3 install -r /requirements.txt
RUN yum clean all
RUN rm -rf /var/cache/yum
RUN python3 --version

RUN mkdir /app
WORKDIR /app
COPY ./ /app

#security to avoid root account
RUN useradd user
USER user

