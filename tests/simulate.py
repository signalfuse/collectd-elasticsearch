#! /usr/bin/python

import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT_NUMBER = 9200

if len(sys.argv) == 2:
    base_path = sys.argv[1]
    if os.path.isdir(base_path):
        print("simulating ES server from %s" % base_path)
    else:
        print("invalid or missing directory %s" % base_path)
        sys.exit(1)
else:
    print(
        "usage: ./simulate.py directory_path. Example ./simulate.py \
data/1.7.2"
    )
    sys.exit(1)


class EsSimulatorHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.serve_path(self.path)
        return

    def serve_path(self, path):
        file_path = os.path.join(base_path, path[1:])
        if os.path.isdir(file_path):
            file_path = os.path.join(file_path, "index.json")
        else:
            file_path = file_path + ".json"
        with open(file_path, "r") as f:
            self.wfile.write(f.read().encode("utf-8"))


try:
    server = HTTPServer(("", PORT_NUMBER), EsSimulatorHandler)
    print("Started ES simulator on port ", PORT_NUMBER)
    server.serve_forever()

except KeyboardInterrupt:
    print("ctrl-c received, shutting down")
    server.socket.close()
