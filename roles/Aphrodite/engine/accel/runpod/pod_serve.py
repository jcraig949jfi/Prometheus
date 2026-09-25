"""On-pod, bearer-authed, read-only server for the canary outputs.

Serves GET /status.json, /ACCEL_EQUIVALENCE.json, /canary.log from
$ACCEL_OUT_DIR (default /app/out) on 0.0.0.0:8080. Requires
`Authorization: Bearer <ACCEL_ARTIFACT_TOKEN>` (a per-run random token minted
by the controller -- NOT the RunPod key). Refuses to start if any RunPod
credential is present in its environment (the boot script unsets the key that
RunPod injects into every pod -- see AETH-01 RUNPOD_SMOKE_RECEIPT_2026-09-22).
Emits no access logs. Serving does NOT stop billing; only the controller or
the reaper terminating the pod does.
"""
import hmac
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

NAMES = {"/status.json": "application/json", "/ACCEL_EQUIVALENCE.json": "application/json",
         "/canary.log": "text/plain; charset=utf-8"}
LIMIT = 8 * 1024 * 1024


class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_error(self, code, message=None, explain=None):
        self._reply(code)

    def _reply(self, code, data=b"", ctype="text/plain"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True
        if data:
            self.wfile.write(data)

    def do_GET(self):
        got = self.headers.get_all("Authorization", [])
        supplied = got[0].encode("latin-1") if len(got) == 1 else b""
        if not hmac.compare_digest(supplied, self.server.auth):
            return self._reply(401)
        path = self.path.split("?", 1)[0]
        if path not in NAMES:
            return self._reply(404)
        try:
            with open(os.path.join(self.server.out_dir, path.lstrip("/")), "rb") as f:
                data = f.read(LIMIT)
        except OSError:
            return self._reply(404)
        self._reply(200, data, NAMES[path])


def main():
    for k in ("RUNPOD_API_KEY", "RUNPOD_API_TOKEN", "RUNPOD_TOKEN"):
        if os.environ.get(k):
            print("pod_serve: RunPod credential present in env -- refusing", file=sys.stderr)
            return 2
    token = os.environ.get("ACCEL_ARTIFACT_TOKEN", "")
    if len(token) < 24:
        print("pod_serve: ACCEL_ARTIFACT_TOKEN missing", file=sys.stderr)
        return 2
    srv = HTTPServer(("0.0.0.0", 8080), H)
    srv.auth = ("Bearer " + token).encode("ascii")
    srv.out_dir = os.environ.get("ACCEL_OUT_DIR", "/app/out")
    srv.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
