# prometheus-exporter-aspen

Prometheus exporter for Aspen

## Setup

This exporter requires a single environment to be set, the FQDN of the Aspen instance to monitor ( e.g. aspen.example.com ).
It is assumed that this server will be access via https.

## Listening port

This exporter runs on port 9750.

## Running the exporter

### CLI
`ASPEN_URL=aspen.example.com python aspen_exporter.py`

### Docker
`docker run -p 9750:9750 -e ASPEN_URL=aspen.example.com quay.io/prometheus-exporter-aspen`
