FROM python:3.6

ADD . /app
RUN pip install -r /app/pip-requirements.txt

WORKDIR /app
ENV PYTHONPATH '/app/'

CMD ["python" , "/app/aspen_exporter.py"]
