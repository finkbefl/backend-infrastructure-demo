FROM python:3.8-slim

WORKDIR /data_collection

RUN apt-get update
RUN apt install -y \
gcc g++ python-dev librocksdb-dev build-essential \
libsnappy-dev zlib1g-dev libbz2-dev libgflags-dev \
liblz4-dev libzstd-dev curl

COPY ./data_collection /data_collection

RUN pip install --upgrade pip
RUN pip install -r /data_collection/requirements.txt


CMD faust -A main worker -l info