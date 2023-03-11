FROM python:3-alpine
ADD . /usr/src/hpilo_exporter
RUN pip3 install -e /usr/src/hpilo_exporter
ENTRYPOINT ["hpilo-exporter"]
EXPOSE 9416
