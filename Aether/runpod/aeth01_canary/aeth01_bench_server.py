"""Minimal bearer-authed static server for AETH-01 benchmark output.

Serves GET /bench.log only, on 0.0.0.0:8081, requiring
`Authorization: Bearer <AGE_ARTIFACT_TOKEN>` (mirrors pod_service.py's auth so
the same off-pod token retrieves both channels). The benchmark log is
non-secret (lattice sizes, tick times, GPU memory totals, digests). Stays alive
via serve_forever so the external controller can retrieve the log BEFORE
terminating the pod; this does NOT stop pod billing. No RunPod credentials are
ever read, and no request/error logs are emitted.
"""

import hmac
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

BENCH_PATH = "/app/bench.log"
LIMIT = 8 * 1024 * 1024


class BenchServer(HTTPServer):
    def __init__(self, address, token):
        self.authorization = ("Bearer " + token).encode("ascii")
        super().__init__(address, BenchHandler)

    def handle_error(self, request, client_address):
        pass  # Suppress tracebacks and access logs.


class BenchHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_error(self, code, message=None, explain=None):
        self._reply(code)

    def _reply(self, code, payload=b"", ctype="text/plain; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True
        if payload:
            self.wfile.write(payload)

    def do_GET(self):
        headers = self.headers.get_all("Authorization", [])
        supplied = headers[0].encode("latin-1") if len(headers) == 1 else b""
        if not hmac.compare_digest(supplied, self.server.authorization):
            self._reply(401)
            return
        target = self.requestline.split()[1]
        if target != "/bench.log":
            self._reply(404)
            return
        try:
            with open(BENCH_PATH, "rb") as f:
                data = f.read(LIMIT + 1)
        except OSError:
            self._reply(404)
            return
        if len(data) > LIMIT:
            data = data[:LIMIT]
        self._reply(200, data)


def main():
    token = os.environ.get("AGE_ARTIFACT_TOKEN", "")
    if not token or len(token) > 4096 or any(not 33 <= ord(c) <= 126 for c in token):
        print("missing/invalid AGE_ARTIFACT_TOKEN", file=sys.stderr)
        return 2
    with BenchServer(("0.0.0.0", 8081), token) as server:
        server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
