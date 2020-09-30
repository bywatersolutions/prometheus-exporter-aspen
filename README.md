# prometheus-exporter-aspen

Prometheus exporter for Aspen

## Setup

This exporter requires a single environment to be set, the FQDN of the Aspen instance to monitor ( e.g. aspen.example.com ).
It is assumed that this server will be access via https.

## Listening port

This exporter runs on port 9750 by default.

The port used can be passed to the script,
or by setting the environment variable `ASPEN_EXPORTER_PORT`

## Running the exporter

### CLI
`python3 aspen_exporter.py [port number]`

### Docker
`docker run -p 9750:9750 quay.io/bywatersolutions/prometheus-exporter-aspen`
