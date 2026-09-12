"""C9: drive a REAL engine process over REAL HTTP with the load shape that
stalled M1 three times on 2026-09-11 -- one client's burst of hundreds of
experiment creations interleaved with a serial consumer's 18-write rows and a
reader -- against a COPY of the live ledger, and measure what the log could
not: per-request latency on the ledger's clock, error class, and the size of
the -wal file through the burst and the quiet moment after it.

Two arms, so H1 can be killed:
  asdeployed  the engine exactly as it runs (one sqlite connection opened and
              closed per request; the last close checkpoints the WAL under an
              EXCLUSIVE lock and deletes it)
  pinned      identical, plus ONE read-only sqlite connection held open by
              this harness for the whole run. In WAL mode an open connection
              keeps a SHARED lock on the db file, so the engine's closing
              connection can never take EXCLUSIVE and the close-time
              checkpoint never runs. If the stall is H1, this arm has no stall.
              If the stall is elsewhere, both arms show it.

Nothing here touches the live service or the live ledger beyond one
`VACUUM INTO` read to make the copy. The engine under test is launched from
the PINNED worktree (the deployed code) on a loopback port with no TLS.

    python deploy/c9_burst_stall.py --ledger <live engine.db> --workdir <scratch>
        --engine-root <pinned SerendipityFoundryEngine dir> --arm asdeployed
        --burst 600 --serial-rows 12 --out <json>
"""
from __future__ import annotations

import argparse
import http.client
import json
import os
import socket
import sqlite3
import statistics
import subprocess
import sys
import threading
import time
import urllib.request

_HERE = os.path.dirname(os.path.abspath(__file__))
_CLIENT = os.path.join(os.path.dirname(os.path.dirname(_HERE)), "SerendipityFoundryClient")
if _CLIENT not in sys.path:
    sys.path.insert(0, _CLIENT)
from sfclient.client import EngineClient, EngineError  # noqa: E402


# --------------------------------------------------------------------------
# recording
# --------------------------------------------------------------------------
class Rec:
    def __init__(self):
        self.lock = threading.Lock()
        self.calls = []          # (t0, dt, who, op, phase, outcome)
        self.wal = []            # (t, bytes)
        self.phase = "setup"

    def call(self, who, op, fn):
        t0 = time.time()
        try:
            r = fn()
            outcome = "ok"
        except EngineError as e:
            r = None
            outcome = "http_%d" % e.status
        except (socket.timeout, TimeoutError):
            r = None
            outcome = "timeout"
        except (ConnectionError, http.client.HTTPException, OSError) as e:
            r = None
            outcome = "transport:" + type(e).__name__
        dt = time.time() - t0
        with self.lock:
            self.calls.append((t0, dt, who, op, self.phase, outcome))
        return r, outcome


def wal_sampler(rec: Rec, db: str, stop: threading.Event, every=0.5):
    while not stop.is_set():
        try:
            b = os.path.getsize(db + "-wal")
        except OSError:
            b = 0
        with rec.lock:
            rec.wal.append((time.time(), b))
        stop.wait(every)


# --------------------------------------------------------------------------
# the three loads
# --------------------------------------------------------------------------
def producer(rec: Rec, base: str, n: int, stop: threading.Event):
    """Vivarium's producer shape: one world, hundreds of committed+enqueued
    experiments, each followed by a family member add."""
    c = EngineClient(base)
    c.register("c9-producer")
    s = c.create_session("burst")
    w = c.create_world(s, "burst-w", seed_root=7)["world_id"]
    c.start(w)
    h = c.hypothesis(w, "burst")
    fam = c.family("campaign", {"planned_members": n}, name="c9-burst")["family_id"]
    for i in range(n):
        if stop.is_set():
            break
        r, oc = rec.call("producer", "experiment", lambda: c.experiment(
            w, {"rule": i, "arm": "map"}, hyp_id=h, commit=True, enqueue=True,
            kind="c9_noop"))
        if r:
            rec.call("producer", "family_member", lambda: c.family_member(
                fam, "experiment", r["exp_id"], role="planned", arm="map"))


def consumer_row(rec: Rec, c: EngineClient, s: str, i: int):
    """Vivarium's consumer shape, ~12 writes and reads per row."""
    r, oc = rec.call("consumer", "create_world", lambda: c.create_world(s, "row-%d" % i, seed_root=100 + i))
    if not r:
        return
    w = r["world_id"]
    rec.call("consumer", "start", lambda: c.start(w))
    h, _ = rec.call("consumer", "hypothesis", lambda: c.hypothesis(w, "row"))
    if not h:
        return
    p, _ = rec.call("consumer", "prediction", lambda: c.prediction(w, h, {"y": 1}))
    e, _ = rec.call("consumer", "experiment", lambda: c.experiment(
        w, {"rule": i}, hyp_id=h, pred_id=p, commit=True, enqueue=True, kind="c9_noop"))
    if not e:
        return
    rec.call("consumer", "audit_envelope", lambda: c.audit_envelope(w, e["exp_id"]))
    wk, _ = rec.call("consumer", "claim", lambda: c.claim("c9-worker", world_id=w))
    if not wk:
        return
    rec.call("consumer", "complete", lambda: c.complete(
        wk["work_id"], "c9-worker", wk["claim_id"], {"value": 1},
        attestation={"executed_config": {"rule": i}}))
    rec.call("consumer", "observation", lambda: c.observation(
        w, e["exp_id"], {"value": 1}, "SURVIVED", pred_id=p, work_id=wk["work_id"]))
    rec.call("consumer", "events", lambda: c.events(w, limit=500))
    rec.call("consumer", "audit_envelope2", lambda: c.audit_envelope(w, e["exp_id"]))


def consumer(rec: Rec, base: str, rows: int, stop: threading.Event, phase_hold: threading.Event):
    c = EngineClient(base)
    c.register("c9-consumer")
    s = c.create_session("serial")
    i = 0
    while not stop.is_set() and i < rows:
        consumer_row(rec, c, s, i)
        i += 1
    phase_hold.set()


def reader(rec: Rec, base: str, stop: threading.Event):
    c = EngineClient(base)
    c.register("c9-reader")
    s = c.create_session("reader")
    w = c.create_world(s, "reader-w", seed_root=3)["world_id"]
    c.start(w)
    h = c.hypothesis(w, "r")
    e = c.experiment(w, {"r": 0}, hyp_id=h, commit=True, kind="c9_noop")
    while not stop.is_set():
        rec.call("reader", "audit_envelope", lambda: c.audit_envelope(w, e["exp_id"]))
        rec.call("reader", "events", lambda: c.events(w, limit=500))
        stop.wait(0.5)


# --------------------------------------------------------------------------
# engine process
# --------------------------------------------------------------------------
def start_engine(python: str, engine_root: str, db: str, port: int, log: str):
    cmd = [python, os.path.join(engine_root, "serve.py"), "--db", db,
           "--host", "127.0.0.1", "--port", str(port), "--max-artifact-bytes", "33554432"]
    fh = open(log, "ab")
    p = subprocess.Popen(cmd, cwd=engine_root, stdout=fh, stderr=subprocess.STDOUT)
    base = "http://127.0.0.1:%d" % port
    for _ in range(120):
        try:
            with urllib.request.urlopen(base + "/v2/version", timeout=2) as r:
                if r.status == 200:
                    return p, base, json.loads(r.read())
        except Exception:
            time.sleep(0.5)
        if p.poll() is not None:
            break
    raise RuntimeError("engine did not come up; see " + log)


def summarize(rec: Rec):
    out = {}
    by = {}
    for t0, dt, who, op, phase, oc in rec.calls:
        by.setdefault((phase, who), []).append((dt, oc))
    for (phase, who), xs in sorted(by.items()):
        d = sorted(x[0] for x in xs)
        errs = {}
        for _, oc in xs:
            if oc != "ok":
                errs[oc] = errs.get(oc, 0) + 1
        out["%s/%s" % (phase, who)] = {
            "n": len(d), "p50_s": round(statistics.median(d), 3),
            "p95_s": round(d[int(0.95 * (len(d) - 1))], 3), "max_s": round(d[-1], 3),
            "over_10s": sum(1 for x in d if x > 10), "errors": errs}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ledger", required=True, help="live engine.db; read once by VACUUM INTO")
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--engine-root", required=True, help="the PINNED SerendipityFoundryEngine dir")
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--port", type=int, default=8902)
    ap.add_argument("--arm", choices=("asdeployed", "pinned"), required=True)
    ap.add_argument("--burst", type=int, default=600)
    ap.add_argument("--serial-rows", type=int, default=12)
    ap.add_argument("--quiet-rows", type=int, default=8, help="serial rows AFTER the burst ends")
    ap.add_argument("--reuse-copy", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    os.makedirs(a.workdir, exist_ok=True)
    copy = os.path.join(a.workdir, "c9_%s.db" % a.arm)
    if not (a.reuse_copy and os.path.exists(copy)):
        for suffix in ("", "-wal", "-shm"):
            try:
                os.remove(copy + suffix)
            except OSError:
                pass
        t = time.time()
        src = sqlite3.connect("file:%s?mode=ro" % a.ledger.replace("?", "%3f"), uri=True)
        src.execute("VACUUM INTO ?", (copy,))
        src.close()
        copy_s = round(time.time() - t, 1)
    else:
        copy_s = None

    pin = None
    if a.arm == "pinned":
        pin = sqlite3.connect("file:%s?mode=ro" % copy.replace("?", "%3f"), uri=True)
        pin.execute("PRAGMA journal_mode").fetchone()   # touch the header; stay open

    log = os.path.join(a.workdir, "c9_%s_engine.log" % a.arm)
    proc, base, version = start_engine(a.python, a.engine_root, copy, a.port, log)
    rec = Rec()
    stop = threading.Event()
    wal_stop = threading.Event()
    threads = [threading.Thread(target=wal_sampler, args=(rec, copy, wal_stop), daemon=True)]
    threads[0].start()
    t_start = time.time()
    try:
        # phase 1: burst + serial + reader together
        rec.phase = "burst"
        hold = threading.Event()
        tp = threading.Thread(target=producer, args=(rec, base, a.burst, stop), daemon=True)
        tc = threading.Thread(target=consumer, args=(rec, base, a.serial_rows, stop, hold), daemon=True)
        tr = threading.Thread(target=reader, args=(rec, base, stop), daemon=True)
        tp.start(); tc.start(); tr.start()
        tp.join()
        t_burst_end = time.time()
        # phase 2: quiet -- the burst is over; the serial consumer keeps going
        rec.phase = "quiet"
        tc.join()
        hold2 = threading.Event()
        tc2 = threading.Thread(target=consumer, args=(rec, base, a.quiet_rows, stop, hold2), daemon=True)
        tc2.start(); tc2.join()
        t_end = time.time()
        stop.set()
        tr.join(timeout=60)
    finally:
        wal_stop.set()
        proc.terminate()
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
        if pin is not None:
            pin.close()

    wal_max = max((b for _, b in rec.wal), default=0)
    wal_at_end = rec.wal[-1][1] if rec.wal else None
    result = {
        "schema": "c9_burst_stall.v1",
        "arm": a.arm, "engine": version, "copy_from": a.ledger,
        "copy_bytes": os.path.getsize(copy), "vacuum_into_s": copy_s,
        "burst": a.burst, "serial_rows": a.serial_rows, "quiet_rows": a.quiet_rows,
        "t_burst_s": round(t_burst_end - t_start, 1), "t_total_s": round(t_end - t_start, 1),
        "wal_max_bytes": wal_max, "wal_bytes_at_end": wal_at_end,
        "wal_samples": len(rec.wal),
        "summary": summarize(rec),
        "slow_calls": [
            {"at_s": round(t0 - t_start, 1), "dt_s": round(dt, 2), "who": who, "op": op,
             "phase": ph, "outcome": oc}
            for t0, dt, who, op, ph, oc in rec.calls if dt > 5 or oc != "ok"][:200],
        "wal_trace": [(round(t - t_start, 1), b) for t, b in rec.wal[::10]],
    }
    with open(a.out, "w", encoding="ascii") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in result.items() if k not in ("wal_trace", "slow_calls")}, indent=1))
    print("slow/err calls:", len(result["slow_calls"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
