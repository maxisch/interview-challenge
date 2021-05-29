FROM alpine:3.10

RUN apk add \
  gcc \
  libc-dev \
  python3-dev \
  uwsgi-python3 \
  mariadb-connector-c-dev \
  mariadb-client

ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 8888
