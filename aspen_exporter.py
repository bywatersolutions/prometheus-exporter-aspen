import os
import requests
import time
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server

class CustomCollector(object):
    def __init__(self):
        pass

    def collect(self):
        fqdn = os.environ.get('ASPEN_URL')
        if fqdn == None:
            print("No value found for environment variable ASPEN_URL!")
            exit(1)

        url = f"https://{fqdn}/API/SearchAPI?method=getIndexStatus"
        response = requests.get(url)
        data = response.json()

        # Aspen general health status
        aspen_health_status = data["result"]["aspen_health_status"];

        if aspen_health_status == "okay":
            is_ok = 1
        elif aspen_health_status == "warning":
            is_ok = .5
        else: # critical
            is_ok = 0

        ok = GaugeMetricFamily(f"aspen_check_health_status", f'Is aspen ok', labels=['instance'])
        ok.add_metric([fqdn], is_ok)
        yield ok

        # Specific aspen health checks
        for key in data["result"]["checks"].keys():
            is_ok = None
            status = data["result"]["checks"][key]["status"]

            if status == "okay":
                is_ok = 1
            elif status == "warning":
                is_ok = .5
            else: # critical
                is_ok = 0

            ok = GaugeMetricFamily(f"aspen_check_{key}", f'Is {key} ok', labels=['instance','aspen_health_check_type'])
            ok.add_metric([fqdn,key], is_ok)
            yield ok

        # Aspen server metrics
        for key in data["result"]["serverStats"].keys():
            val = str(data["result"]["serverStats"][key]["value"])
            vals = val.split(" ");
            if len(vals) > 1: # Value contains a number and a metric, i.e. "41.49 GB"
                val = vals[0]
                metric = vals[1]
                desc = data["result"]["serverStats"][key]["name"]
                ok = GaugeMetricFamily(f"aspen_stat_{key}", f'{desc} in {metric}', labels=['instance'])
                ok.add_metric([fqdn], val)
                yield ok
            else: # Value is just a cimple number, i.e. "0.31" # Value is just a cimple number, i.e. "0.31"
                val = data["result"]["serverStats"][key]["value"]
                desc = data["result"]["serverStats"][key]["name"]
                ok = GaugeMetricFamily(f"aspen_stat_{key}", desc, labels=['instance'])
                ok.add_metric([fqdn], val)
                yield ok

if __name__ == '__main__':
    start_http_server(9750)
    REGISTRY.register(CustomCollector())
    while True:
        time.sleep(1)
