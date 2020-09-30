from prometheus_client import CollectorRegistry, generate_latest
from prometheus_client.core import GaugeMetricFamily
import requests
import logging

def collect_aspen(address):
    registry = CollectorRegistry()
    registry.register(CustomCollector(address))
    return generate_latest(registry)

class CustomCollector(object):
    def __init__(self, address):
        self.address = address

    def collect(self):
        logging.basicConfig(level=logging.INFO)

        metrics = {}

        aspen_fqdn = self.address

        url = f"https://{aspen_fqdn}/API/SearchAPI?method=getIndexStatus"
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

        metric_name = "aspen_check_health_status".replace(".", "_")
        metric_name.replace(".", "_")
        ok = GaugeMetricFamily(metric_name, f'Is aspen ok', labels=['instance'])
        ok.add_metric([aspen_fqdn], is_ok)

        metrics[metric_name] = ok

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

            metric_name = f"aspen_check_{key}".replace(".", "_")
            ok = GaugeMetricFamily(metric_name, f'Is {key} ok', labels=['instance','aspen_health_check_type'])
            ok.add_metric([aspen_fqdn,key], is_ok)

            metrics[metric_name] = ok

        # Aspen server metrics
        for key in data["result"]["serverStats"].keys():
            val = str(data["result"]["serverStats"][key]["value"])
            vals = val.split(" ");
            metric_name = f"aspen_check_{key}".replace(".", "_")
            metric_name.replace(".", "_")
            if len(vals) > 1: # Value contains a number and a metric, i.e. "41.49 GB"
                val = vals[0]
                metric = vals[1]
                desc = data["result"]["serverStats"][key]["name"]
                ok = GaugeMetricFamily(metric_name, f'{desc} in {metric}', labels=['instance'])
                ok.add_metric([aspen_fqdn], val)
                metrics[metric_name] = ok
            else: # Value is just a simple number, i.e. "0.31" # Value is just a simple number, i.e. "0.31"
                val = data["result"]["serverStats"][key]["value"]
                desc = data["result"]["serverStats"][key]["name"]
                ok = GaugeMetricFamily(f"aspen_stat_{key}", desc, labels=['instance'])
                ok.add_metric([aspen_fqdn], val)
                metrics[metric_name] = ok
        return metrics.values()
