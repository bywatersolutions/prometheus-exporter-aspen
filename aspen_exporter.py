#!/usr/bin/env python3

"""
A server for exporting Aspen stats for Prometheus
Usage::
    ./aspen_exporter.py [<port>]
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from prometheus_client import CONTENT_TYPE_LATEST
from socketserver import ForkingMixIn
from urllib.parse import urlparse
import logging
import os
import urllib

from collector import collect_aspen


class ForkingHTTPServer(ForkingMixIn, HTTPServer):
    pass


class AspenExporterHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/metrics":
            params = urllib.parse.parse_qs(url.query)
            if "address" not in params:
                self.send_response(400)
                self.end_headers()
                self.wfile.write("Parameter 'address' is required".encode("utf-8"))
                return

            self.send_response(200)
            self.send_header("Content-Type", CONTENT_TYPE_LATEST)
            self.end_headers()

            address = params["address"][0]
            output = collect_aspen(address)

            self.wfile.write(output)
        elif url.path == "/":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(
                """<html>
          <head><title>Aspen Exporter for Prometheus</title></head>
          <body>
          <h1>Aspen Exporter for Prometheus</h1>
          <p>Visit <code>/metrics?address=my.aspen.example.com</code> to use.</p>
          </body>
          </html>""".encode(
                    "utf-8"
                )
            )
        else:
            self.send_response(404)
            self.end_headers()


def run(server_class=HTTPServer, handler_class=AspenExporterHandler, cli_port=""):
    port = cli_port or os.environ.get("ASPEN_EXPORTER_PORT") or 9750
    port = int(port)

    logging.basicConfig(level=logging.INFO)
    logging.info(f"Starting httpd on port {port}...\n")

    server_address = ("", port)
    httpd = server_class(server_address, handler_class)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info("Stopping httpd...\n")


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
