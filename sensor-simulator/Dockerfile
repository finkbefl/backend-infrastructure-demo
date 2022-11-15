FROM python:3.8-slim

RUN apt-get update
RUN apt install -y \
gcc g++ python-dev librocksdb-dev build-essential \
libsnappy-dev zlib1g-dev libbz2-dev libgflags-dev \
liblz4-dev libzstd-dev curl

ADD ./temp_sensors /temp_sensors

RUN pip install --upgrade pip
RUN pip install -r /temp_sensors/requirements.txt

CMD [ "python3", "./temp_sensors/main.py" ]