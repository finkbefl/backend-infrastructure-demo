FROM python:3.8-slim

WORKDIR /db_loader

RUN apt-get update
RUN apt install -y \
gcc g++ python-dev librocksdb-dev build-essential \
libsnappy-dev zlib1g-dev libbz2-dev libgflags-dev \
liblz4-dev libzstd-dev curl

COPY ./db_loader /db_loader

RUN pip install --upgrade pip
RUN pip install -r /db_loader/requirements.txt


CMD python3 database.py && faust -A main worker -l info