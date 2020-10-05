FROM python:3.6-alpine

ADD . /app
RUN pip install -r /app/pip-requirements.txt

WORKDIR /app
ENV PYTHONPATH '/app/'

ENV ASPEN_EXPORTER_PORT 9750
HEALTHCHECK CMD wget -q --spider 127.0.0.1:$ASPEN_EXPORTER_PORT

CMD ["python" , "/app/aspen_exporter.py"]
