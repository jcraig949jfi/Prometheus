"""Frontier intake (charter C5; PAN-09..11): adjacent research and locally runnable
models into schema pan, polite by construction.

Rate discipline is Eos's Dawn constitution adopted (roles/Eos/RESPONSIBILITIES.md):
never above 75 percent of a documented limit, limits known before the first call
(pan/frontier/seeds.json "limits", sourced from the research notes). Every call is
logged in pan.intake_call with status, bytes and timing, so the rate is auditable
after the fact rather than asserted.

Items are typed UNTYPED (Eos's vocabulary); nothing here judges relevance.
"""
import datetime as dt
import json
import time
from pathlib import Path

SEEDS = Path(__file__).resolve().parent / "seeds.json"
UA = "Prometheus-Pan/0.1 (research catalog; polite intake; one connection)"


def seeds():
    return json.loads(SEEDS.read_text(encoding="utf-8"))


class Client:
    """One session per source, a minimum interval between calls, a rolling-window cap,
    and a log row per call."""

    def __init__(self, source, run_id, min_interval_s, window_s=None, max_calls_per_window=None):
        import requests
        self.s = requests.Session()
        self.s.headers["User-Agent"] = UA
        self.source, self.run_id = source, run_id
        self.min_interval, self.window, self.cap = min_interval_s, window_s, max_calls_per_window
        self.last = 0.0
        self.calls = []
        self.log = []

    def get(self, url, params=None, timeout=60):
        wait = self.min_interval - (time.time() - self.last)
        if wait > 0:
            time.sleep(wait)
        if self.window and self.cap:
            now = time.time()
            self.calls = [t for t in self.calls if now - t < self.window]
            if len(self.calls) >= self.cap:
                time.sleep(self.window - (now - self.calls[0]) + 1)
        started = dt.datetime.now(dt.timezone.utc)
        t0 = time.time()
        status, n, err, r = None, None, None, None
        try:
            r = self.s.get(url, params=params, timeout=timeout)
            status, n = r.status_code, len(r.content)
            if status == 429 or status >= 500:
                err = "HTTP {}".format(status)
        except Exception as e:
            err = "{}: {}".format(type(e).__name__, e)
        self.last = time.time()
        self.calls.append(self.last)
        full = r.url if r is not None else url
        self.log.append((self.run_id, self.source, full[:2000], status, n, None, started,
                         int((time.time() - t0) * 1000), err))
        if status == 429:   # back off hard and say so; never retry in a tight loop
            time.sleep(max(60, self.min_interval * 10))
        return r if (r is not None and status == 200) else None

    def flush(self, cur):
        from psycopg2.extras import execute_values
        if self.log:
            execute_values(cur, """insert into pan.intake_call (run_id, source, url, status, n_bytes, n_items,
                                   started_at, elapsed_ms, error) values %s""", self.log)
            self.log = []


def new_run(kind, params=None):
    from .. import db, host
    run_id = "{}-{}-{}".format(kind, dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"), host().lower())
    with db.cursor() as cur:
        cur.execute("insert into pan.run (run_id, kind, host, params) values (%s,%s,%s,%s)",
                    (run_id, kind, host(), json.dumps(params or {})))
    return run_id


def finish_run(run_id, counts, status="OK"):
    from .. import db
    with db.cursor() as cur:
        cur.execute("update pan.run set finished_at=now(), status=%s, counts=%s where run_id=%s",
                    (status, json.dumps(counts, default=str), run_id))
