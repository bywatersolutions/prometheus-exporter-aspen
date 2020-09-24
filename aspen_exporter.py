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
                ok = GaugeMetricFamily(f"aspen_check_{key}", f'Is {key} ok', labels=['instance'])
                ok.add_metric([fqdn], is_ok)
                yield ok

        keys = ["data_disk_space", "usr_disk_space", "total_memory", "available_memory"]
        for key in keys:
            if key in data["result"]["serverStats"]:
                val = data["result"]["serverStats"][key]["value"]
                vals = val.split(" ");
                val = val[0];
                desc = data["result"]["serverStats"][key]["name"]
                ok = GaugeMetricFamily(f"aspen_stat_{key}", f'{desc} in {vals[1]}', labels=['instance'])
                ok.add_metric([fqdn], val)
                yield ok

        keys = ["percent_memory_in_use", "1_minute_load_average", "5_minute_load_average", "15_minute_load_average", "load_per_cpu"]
        for key in keys:
            if key in data["result"]["serverStats"]:
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
