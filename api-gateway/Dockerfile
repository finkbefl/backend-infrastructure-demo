FROM python:3.8-slim

WORKDIR /api_gateway

RUN apt-get update
RUN apt install -y \
gcc g++ python-dev librocksdb-dev build-essential \
libsnappy-dev zlib1g-dev libbz2-dev libgflags-dev \
liblz4-dev libzstd-dev curl

COPY ./api_gateway /api_gateway

RUN pip install --upgrade pip
RUN pip install -r /api_gateway/requirements.txt

CMD uvicorn main:fastapi_app --reload --host 0.0.0.0 --port 8007