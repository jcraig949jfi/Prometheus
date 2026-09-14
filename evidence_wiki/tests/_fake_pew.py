"""A stand-in PEW for the watchdog tests (tests/test_watchdog.py).

Modes, chosen on the command line so the watchdog's process match can find
this process by a unique --marker in its command line:

    healthy   /health 200 with search.ready true; /search 200 iff the bearer
              token equals --token (else 401)      -> the watchdog must log ok
    hung      accepts the TCP connection and never answers   -> positive
              control: the watchdog must count failures, then stop + start
    loading   /health 200 with search.loading true, uptime small
              -> the watchdog must log "warming up" and count nothing
    unready   /health 200 with search.ready false, loading false, uptime big
              -> a failure, not a warm-up

No dependency beyond the standard library, so it starts in well under a
second and the tests can judge the watchdog's timing rather than torch's.
"""
import argparse
import json
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--mode", required=True,
                    choices=["healthy", "hung", "loading", "unready"])
    ap.add_argument("--token", default="fake-token")
    ap.add_argument("--marker", default="fakepew")
    a = ap.parse_args()
    started = time.time()

    class H(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _json(self, code, obj):
            body = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if a.mode == "hung":
                threading.Event().wait()  # accept, never answer
                return
            path = self.path.split("?")[0]
            if path == "/api/v1/health":
                if a.mode == "healthy":
                    search = {"ready": True, "loading": False, "error": None}
                    uptime = round(time.time() - started, 1)
                elif a.mode == "loading":
                    search = {"ready": False, "loading": True, "error": None}
                    uptime = round(time.time() - started, 1)
                else:  # unready
                    search = {"ready": False, "loading": False, "error": None}
                    uptime = 99999.0
                return self._json(200, {"status": "ok", "uptime_s": uptime,
                                        "search": search, "marker": a.marker})
            if path == "/api/v1/search":
                tok = self.headers.get("Authorization", "").removeprefix("Bearer ").strip()
                if tok != a.token:
                    return self._json(401, {"detail": "bad or missing bearer token"})
                return self._json(200, {"results": [], "marker": a.marker})
            return self._json(404, {"detail": "not found"})

    # No SO_REUSEADDR: on Windows it lets two processes bind one port, and a
    # leftover fake would then answer for the one under test.
    ThreadingHTTPServer.allow_reuse_address = False
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), H)
    srv.daemon_threads = True
    sys.stdout.write(f"fake pew {a.mode} on {a.port} marker {a.marker}\n")
    sys.stdout.flush()
    srv.serve_forever()


if __name__ == "__main__":
    main()
