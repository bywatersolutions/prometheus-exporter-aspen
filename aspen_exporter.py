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

        keys = ["solr", "backup", "memory_usage", "load_average", "nightly_index", "koha", "side_loads", "overdrive", "hoopla", "open_archives", "cloud_library", "cron", "sitemap", "offline_holds"]
        for key in keys:
            if key in data["result"]["checks"]:
                is_ok = 1 if data["result"]["checks"][key]["status"] == "okay" else 0
                ok = GaugeMetricFamily(f"aspen_{key}_guage", f'Is {key} ok', labels=['instance'])
                ok.add_metric([fqdn], 1)
                yield ok

if __name__ == '__main__':
    start_http_server(9750)
    REGISTRY.register(CustomCollector())
    while True:
        time.sleep(1)
