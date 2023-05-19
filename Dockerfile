FROM python:3.10.11
ADD . /DataMiners
WORKDIR /DataMiners
RUN pip install -r requirements.txt