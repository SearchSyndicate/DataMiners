FROM python:3.10.11
ADD . /DataMiners
WORKDIR /DataMiners
RUN pip install flask
RUN pip install -r requirements.txt