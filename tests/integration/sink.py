import json
import signal
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from time import time

# This module collects metrics from collectd and can echo them back out for
# making assertions on the collected metrics.


# Fake the /v1/collectd endpoint and just stick all of the metrics in a
# list
def run_fake_ingest(metric_data):
    class FakeCollectdIngest(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get("Content-Length")))

            metric_data.extend(json.loads(body))

            self.send_response(200)
            self.send_header("Content-Type", "text/ascii")
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write("OK".encode("utf-8"))

    print("Starting ingest server on port 80")
    httpd = HTTPServer(("", 80), FakeCollectdIngest)
    httpd.serve_forever()
    print("Ingest server shutting down")


# Dumps all of the collected metrics back out as JSON upon request
def serve_metric_data(metric_data):
    class MetricDataSpewer(BaseHTTPRequestHandler):
        def do_GET(self):
            data = json.dumps(metric_data)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            print(data)
            self.wfile.write(data.encode("utf-8"))

    print("Starting metric spewer on port 8080")
    httpd = HTTPServer(("", 8080), MetricDataSpewer)
    httpd.serve_forever()
    print("Metric spewer shutting down")


if __name__ == "__main__":
    # Lists are thread-safe due to the GIL
    metric_data = []
    t1 = threading.Thread(target=run_fake_ingest, args=(metric_data,))
    t2 = threading.Thread(target=serve_metric_data, args=(metric_data,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()
