#!/usr/bin/env python3
"""D10 (point release 2026-09): MEASURE the engine under the workload shape
Campaign 4+ intends -- more generations, more observations, more rows,
longer unattended operation -- and write numbers, not adjectives.

    python deploy/longrun_load.py --worlds 8 --gens 400 --port 8941 --out DIR

A scratch engine of THIS tree on loopback, disposable ledger on the same
volume class as production (D:). Per world: `gens` logical generations; each
generation = one experiment + commit + observation (logical_time = gen) and
every 10th generation a WORLD_EVENT; every 50th a checkpoint; every 100th an
artifact (8 KiB). Two producer threads write concurrently while one reader
thread walks cursors (the C9 shape: producer/reader contention on one
SQLite). Then a fork, a termination per world, and a full paginated walk of
every world's events at the end.

Measured (all recorded in the receipt JSON + a Markdown table):
  * per-route latency distribution (p50 / p95 / max) in successive
    row-count bands, so growth vs history is visible
  * events / observations / artifacts totals, DB + WAL bytes per 100K events
  * checkpoint latency, cursor page latency at the end (largest history)
  * restart: kill -9 at the end, relaunch, time to /v2/version, then
    verify-anchor on a sample and a full cursor walk
  * write_lock waits from /v2/health; any HTTP 5xx; any stall > 5 s
It never touches production. Retention: NOT changed here; the receipt is the
evidence for the retention DECISION in SFE_LONG_RUN_REPORT.md.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "SerendipityFoundryClient", "test_harness"))
from longrun_restart import Api, launch, port_free, wait_version  # noqa: E402

ENGINE = os.path.normpath(os.path.join(HERE, ".."))


class Lat:
    def __init__(self):
        self.lock = threading.Lock()
        self.samples = {}      # route -> list of (t, seconds)
        self.errors = []
        self.stalls = []

    def add(self, route, t, dt, status):
        with self.lock:
            self.samples.setdefault(route, []).append((t, dt))
            if status >= 500:
                self.errors.append((route, status, t))
            if dt > 5.0:
                self.stalls.append((route, round(dt, 2), t))

    def summary(self, bands):
        out = {}
        for route, xs in self.samples.items():
            out[route] = {"n": len(xs)}
            for lo, hi, label in bands:
                sel = [dt for (t, dt) in xs if lo <= t < hi]
                if sel:
                    sel.sort()
                    out[route][label] = {"n": len(sel),
                                         "p50_ms": round(1000 * statistics.median(sel), 1),
                                         "p95_ms": round(1000 * sel[min(len(sel) - 1, int(0.95 * len(sel)))], 1),
                                         "max_ms": round(1000 * sel[-1], 1)}
        return out


INFLIGHT = {}            # thread ident -> (route, start_time); read by the stall watchdog
INFLIGHT_LOCK = threading.Lock()


class TimedApi(Api):
    def __init__(self, base, lat, t_origin):
        super().__init__(base)
        self.lat = lat
        self.t_origin = t_origin

    def req(self, method, path, body=None, headers=None, timeout=60):
        route = method + " " + path.split("?")[0]
        for seg in path.split("/"):
            if seg.startswith(("wld_", "exp_", "obs_", "sha256:", "ckp_", "wrk_")):
                route = route.replace(seg, "{id}")
        t = time.time()
        me = threading.get_ident()
        with INFLIGHT_LOCK:
            INFLIGHT[me] = (route, t)
        try:
            st, out = super().req(method, path, body, headers, timeout)
        finally:
            with INFLIGHT_LOCK:
                INFLIGHT.pop(me, None)
        self.lat.add(route, t - self.t_origin, time.time() - t, st)
        return st, out


def serving_pid(port):
    """the pid that OWNS the listening socket (the venv python.exe is a launcher
    stub whose child serves; py-spy on the stub says 'Failed to find python
    version from target process')"""
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "(Get-NetTCPConnection -State Listen -LocalPort %d -ErrorAction SilentlyContinue | Select -First 1).OwningProcess" % port],
                             capture_output=True, text=True, timeout=15).stdout.strip()
        return int(out) if out else None
    except Exception:                                            # noqa: BLE001
        return None


def stall_watchdog(pid, stop, rec, threshold_s=4.0, max_dumps=6, port=None):
    """When any client request has been in flight longer than threshold_s,
    capture the ENGINE's thread stacks with py-spy (if installed) so a stall
    is diagnosed from the server side, not guessed from the client side."""
    import shutil as _sh
    spy = _sh.which("py-spy") or os.path.join(os.path.dirname(sys.executable), "py-spy.exe")
    dumps = []
    last = 0.0
    while not stop.is_set():
        now = time.time()
        with INFLIGHT_LOCK:
            slow = [(r, now - t0) for (r, t0) in INFLIGHT.values() if now - t0 > threshold_s]
        if slow and now - last > threshold_s and len(dumps) < max_dumps and os.path.exists(spy):
            last = now
            target = (serving_pid(port) if port else None) or pid
            try:
                pr = subprocess.run([spy, "dump", "--pid", str(target)], capture_output=True, text=True, timeout=20)
                out = pr.stdout + (("\nSTDERR: " + pr.stderr) if pr.stderr else "")
            except Exception as e:                                   # noqa: BLE001
                out = "py-spy failed: %r" % e
            # keep only the engine frames + thread headers
            keep = [ln for ln in out.splitlines() if ln.startswith("Thread") or "sfe" in ln or "sqlite" in ln.lower() or "store.py" in ln]
            dumps.append({"t": round(now, 1), "inflight": slow, "stack": keep[:60], "raw": out.splitlines()[:120]})
        stop.wait(0.5)
    rec["stall_dumps"] = dumps


def producer(api, sess_id, gens, tag, rec, lat, ck_every=50, ev_every=10, art_every=100, gen_pause=0.0):
    """one world, `gens` generations"""
    w = api.ok("POST", "/v2/worlds", {"session_id": sess_id, "name": "load-" + tag,
                                      "manifest": {"logical_time_unit": "generation", "load": tag},
                                      "manifest_schema": "fixture/1", "labels": {"load": tag}})
    wid = w["world_id"]
    api.ok("POST", "/v2/worlds/%s/start" % wid)
    cks = []
    for g in range(gens):
        e = api.ok("POST", "/v2/worlds/%s/experiments" % wid, {"spec": {"g": g, "tag": tag}},
                   headers={"Idempotency-Key": "idem:%s:exp:%d" % (tag, g)})["exp_id"]
        api.ok("POST", "/v2/worlds/%s/experiments/%s/commit" % (wid, e), {})
        api.ok("POST", "/v2/worlds/%s/observations" % wid,
               {"exp_id": e, "content": {"score": (g % 100) / 100.0, "vec": [g, g + 1, g + 2]},
                "outcome": "SURVIVED", "logical_time": g},
               headers={"Idempotency-Key": "idem:%s:obs:%d" % (tag, g)})
        if g % ev_every == 0:
            api.ok("POST", "/v2/worlds/%s/events" % wid,
                   {"kind": "pressure", "logical_time": g, "payload": {"rung": g // ev_every}})
        if g % ck_every == 0 and g:
            t = time.time()
            cks.append(api.ok("POST", "/v2/worlds/%s/checkpoint" % wid))
            rec["checkpoint_s"].append(round(time.time() - t, 4))
        if g % art_every == 0:
            api.ok("POST", "/v2/worlds/%s/artifacts" % wid,
                   {"kind": "trace", "data_b64": base64.b64encode(os.urandom(8192)).decode()},
                   headers={"Idempotency-Key": "idem:%s:art:%d" % (tag, g)})
        if gen_pause:
            time.sleep(gen_pause)
    if cks:
        api.ok("POST", "/v2/worlds/%s/fork" % wid, {"checkpoint_id": cks[-1]["checkpoint_id"],
                                                    "children": [{"name": "cf", "interventions": {"p": "Q"}}]})
    api.ok("POST", "/v2/worlds/%s/terminate" % wid,
           {"reason": "fixture:horizon", "logical_time": gens - 1, "horizon": gens})
    return wid


def reader(api, wids, stop, rec, pause=0.0):
    """walk cursors over whatever exists, continuously, until told to stop"""
    pages = 0
    while not stop.is_set():
        for wid in list(wids):
            after = 0
            while after is not None and not stop.is_set():
                st, p = api.req("GET", "/v2/worlds/%s/observations?after_seq=%d&limit=200" % (wid, after))
                if st != 200:
                    break
                pages += 1
                after = p["next_after_seq"]
                if pause:
                    time.sleep(pause)
        time.sleep(0.05)
    rec["reader_pages"] = pages


def wal_sampler(db, api, stop, rec):
    """every 5 s: WAL/DB bytes on disk and the engine's own checkpointer view"""
    samples = []
    while not stop.is_set():
        try:
            wal = os.path.getsize(db + "-wal") if os.path.exists(db + "-wal") else 0
            st, h = api.req("GET", "/v2/health")
            ck = h.get("checkpointer") if st == 200 else None
            try:
                av = subprocess.run(["powershell", "-NoProfile", "-Command",
                                     "(Get-Process MsMpEng -ErrorAction SilentlyContinue | Select -First 1).TotalProcessorTime.TotalSeconds"],
                                    capture_output=True, text=True, timeout=10).stdout.strip()
                av = float(av) if av else None
            except Exception:                                    # noqa: BLE001
                av = None
            samples.append({"t": round(time.time(), 1), "wal_bytes": wal, "db_bytes": os.path.getsize(db),
                            "msmpeng_cpu_s": av,
                            "ck_runs": ck and ck.get("runs"), "ck_alive": ck and ck.get("alive"),
                            "ck_truncates": ck and ck.get("truncates"), "ck_errors": ck and ck.get("errors")})
        except Exception as e:                                   # noqa: BLE001
            samples.append({"t": round(time.time(), 1), "error": repr(e)[:120]})
        stop.wait(5.0)
    rec["wal_samples"] = samples
    if samples:
        rec["wal_max_bytes"] = max(x.get("wal_bytes", 0) for x in samples)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=8)
    ap.add_argument("--gens", type=int, default=400)
    ap.add_argument("--producers", type=int, default=2)
    ap.add_argument("--port", type=int, default=8941)
    ap.add_argument("--out", default=os.path.join(HERE, "LONG_RUN_2026-09-17"))
    ap.add_argument("--db-dir", default=None, help="where the scratch ledger lives (default: a temp dir on this volume)")
    ap.add_argument("--no-reader", action="store_true", help="control: no concurrent cursor-reader thread")
    ap.add_argument("--reader-pause", type=float, default=0.0,
                    help="seconds between reader pages (a PACED reader, the PEW-ingestion shape); 0 = tight loop")
    ap.add_argument("--label", default=None, help="free text recorded in the receipt")
    ap.add_argument("--gen-pause", type=float, default=0.0,
                    help="seconds between generations per producer (a CAMPAIGN-RATE writer; Campaign 3 ran ~0.02 "
                         "observations/s per slot, i.e. pauses of tens of seconds -- 0.5 s here is still 25x faster)")
    a = ap.parse_args()
    if not port_free(a.port):
        print("REFUSING: port %d is held" % a.port); return 2
    os.makedirs(a.out, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="sfe_load_", dir=a.db_dir)
    db = os.path.join(tmp, "load.db")
    log = open(os.path.join(a.out, "engine.log"), "ab")
    rec = {"tool": "longrun_load", "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "config": vars(a), "db_dir": tmp, "checkpoint_s": [], "phases": {}}
    proc = launch(ENGINE, db, a.port, log)
    t_origin = time.time()
    lat = Lat()
    api0 = TimedApi("http://127.0.0.1:%d" % a.port, lat, t_origin)
    wait_version(api0)
    api0.token = api0.ok("POST", "/v2/clients", {"name": "load"})["token"]
    rec["engine"] = {k: v for k, v in api0.ok("GET", "/v2/version").items()
                     if k in ("engine_instance_id", "engine_source_hash", "schema_version")}
    sess = api0.ok("POST", "/v2/sessions", {"name": "load"})
    api0.session_key = sess["session_key"]

    wids = []
    lock = threading.Lock()
    stop = threading.Event()
    def prod_worker(k):
        api = TimedApi(api0.base, lat, t_origin); api.token = api0.token; api.session_key = api0.session_key
        for j in range(k, a.worlds, a.producers):
            wid = producer(api, sess["session_id"], a.gens, "w%02d" % j, rec, lat, gen_pause=a.gen_pause)
            with lock:
                wids.append(wid)
    rapi = TimedApi(api0.base, lat, t_origin); rapi.token = api0.token; rapi.session_key = api0.session_key
    rth = threading.Thread(target=reader, args=(rapi, wids, stop, rec, a.reader_pause), daemon=True)
    sapi = Api(api0.base)
    sstop = threading.Event()
    sth = threading.Thread(target=wal_sampler, args=(db, sapi, sstop, rec), daemon=True)
    sth.start()
    wth = threading.Thread(target=stall_watchdog, args=(proc.pid, sstop, rec), kwargs={"port": a.port}, daemon=True)
    wth.start()
    failures = []
    def _guard(fn):
        def run(*args):
            try:
                fn(*args)
            except Exception as e:                               # noqa: BLE001
                failures.append(repr(e)[:400]); stop.set()
        return run
    prod_worker = _guard(prod_worker)
    t0 = time.time()
    threads = [threading.Thread(target=prod_worker, args=(k,)) for k in range(a.producers)]
    if not a.no_reader:
        rth.start()
    [t.start() for t in threads]; [t.join() for t in threads]
    stop.set()
    if not a.no_reader:
        rth.join(timeout=30)
    rec["phases"]["write_s"] = round(time.time() - t0, 1)
    sstop.set(); sth.join(timeout=10)
    rec["producer_failures"] = failures
    rec["health_after_write"] = api0.ok("GET", "/v2/health")
    if failures:
        rec["ABORTED"] = True
        rec["latency_by_quarter"] = lat.summary([(0, 1e12, "all")])
        rec["http_5xx"] = lat.errors; rec["stalls_over_5s"] = lat.stalls
        json.dump(rec, open(os.path.join(a.out, "receipt.json"), "w", encoding="utf-8"), indent=1)
        open(os.path.join(a.out, "RECEIPT.md"), "w", encoding="utf-8").write(
            "# ABORTED: producer failure\n\n%s\n" % "\n".join(failures))
        proc.kill(); proc.wait(timeout=10); log.close()
        print("ABORTED:", failures[0][:200]); return 1

    # ---- totals + storage
    import sqlite3
    cx = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True)
    tot = {t: cx.execute("SELECT COUNT(*) FROM %s" % t).fetchone()[0]
           for t in ("events", "observations", "experiments", "artifacts", "checkpoints", "worlds")}
    cx.close()
    rec["totals"] = tot
    rec["storage_bytes"] = {"db": os.path.getsize(db),
                            "wal": os.path.getsize(db + "-wal") if os.path.exists(db + "-wal") else 0,
                            "blobs_dir": sum(os.path.getsize(os.path.join(dp, f)) for dp, _d, fs in os.walk(tmp) for f in fs)}
    rec["storage_bytes"]["db_per_100k_events"] = round(rec["storage_bytes"]["db"] / max(tot["events"], 1) * 100000)

    # ---- read latency at full history: cursor pages + default lists
    t0 = time.time(); n_pages = 0
    for wid in wids:
        after = 0
        while after is not None:
            p = api0.ok("GET", "/v2/worlds/%s/events?after_seq=%d&limit=500" % (wid, after))
            n_pages += 1; after = p["next_after_seq"]
    rec["phases"]["full_event_walk_s"] = round(time.time() - t0, 2)
    rec["phases"]["full_event_walk_pages"] = n_pages
    t0 = time.time()
    for wid in wids[:3]:
        api0.ok("GET", "/v2/worlds/%s/observations" % wid)      # default list (capped)
    rec["phases"]["default_obs_list_x3_s"] = round(time.time() - t0, 3)

    # ---- restart at full history
    t0 = time.time(); proc.kill(); proc.wait(timeout=30)
    while not port_free(a.port):
        time.sleep(0.1)
    rec["phases"]["kill_to_port_free_s"] = round(time.time() - t0, 2)
    t0 = time.time(); proc = launch(ENGINE, db, a.port, log); v = wait_version(api0)
    rec["phases"]["relaunch_to_version_s"] = round(time.time() - t0, 2)
    rec["identity_after_restart_same"] = (v["engine_instance_id"] == rec["engine"]["engine_instance_id"])
    t0 = time.time()
    ev = api0.ok("GET", "/v2/worlds/%s/events?after_seq=0&limit=1000" % wids[0])["events"]
    obs_ev = [e for e in ev if e["event_type"] == "OBSERVATION_RECORDED"][:50]
    n_ok = sum(1 for e in obs_ev if api0.ok("POST", "/v2/audit/verify-anchor",
                                            {"world_id": wids[0], "event_id": e["event_id"],
                                             "entry_hash": e["entry_hash"], "obs_id": e["refs"]["obs_id"]})["valid"])
    rec["anchor_sample_verified"] = "%d/%d" % (n_ok, len(obs_ev))
    rec["phases"]["anchor_sample_s"] = round(time.time() - t0, 2)
    rec["health_final"] = api0.ok("GET", "/v2/health")

    proc.kill(); proc.wait(timeout=10); log.close()
    total_s = rec["phases"]["write_s"]
    bands = [(0, total_s / 4, "q1"), (total_s / 4, total_s / 2, "q2"), (total_s / 2, 3 * total_s / 4, "q3"),
             (3 * total_s / 4, 1e12, "q4")]
    rec["latency_by_quarter"] = lat.summary(bands)
    rec["http_5xx"] = lat.errors
    rec["stalls_over_5s"] = lat.stalls
    if rec["checkpoint_s"]:
        cs = sorted(rec["checkpoint_s"])
        rec["checkpoint_latency"] = {"n": len(cs), "p50_s": cs[len(cs) // 2], "max_s": cs[-1]}
    rec["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    rec["checkpointer_final"] = rec["health_final"].get("checkpointer")
    json.dump(rec, open(os.path.join(a.out, "receipt.json"), "w", encoding="utf-8"), indent=1)
    # markdown table
    lines = ["# Long-run load receipt (%s)" % rec["finished_at"], "",
             "engine %s  schema %s  worlds %d x gens %d, producers %d + 1 reader" % (
                 rec["engine"]["engine_source_hash"][:20], rec["engine"]["schema_version"], a.worlds, a.gens, a.producers), "",
             "    totals   " + json.dumps(tot),
             "    storage  db %.1f MB, wal %.1f MB, %.0f bytes/event -> %.1f MB per 100K events" % (
                 rec["storage_bytes"]["db"] / 1048576, rec["storage_bytes"]["wal"] / 1048576,
                 rec["storage_bytes"]["db"] / max(tot["events"], 1),
                 rec["storage_bytes"]["db_per_100k_events"] / 1048576),
             "    phases   " + json.dumps(rec["phases"]),
             "    restart  identity_same=%s anchors %s" % (rec["identity_after_restart_same"], rec["anchor_sample_verified"]),
             "    5xx %d  stalls>5s %d  write_lock %s" % (len(lat.errors), len(lat.stalls),
                                                          json.dumps(rec["health_final"].get("write_lock"))),
             "    wal_max_bytes %s  checkpointer %s" % (rec.get("wal_max_bytes"),
                                                       json.dumps({k: (rec.get("checkpointer_final") or {}).get(k) for k in
                                                                   ("alive", "runs", "truncates", "errors", "max_wal_bytes_seen")})),
             "", "    route                                     q1 p50/p95/max ms        q4 p50/p95/max ms      n"]
    for route, d in sorted(rec["latency_by_quarter"].items()):
        q1, q4 = d.get("q1", {}), d.get("q4", {})
        f = lambda q: "%s/%s/%s" % (q.get("p50_ms", "-"), q.get("p95_ms", "-"), q.get("max_ms", "-"))
        lines.append("    %-40s %-24s %-22s %d" % (route[:40], f(q1), f(q4), d["n"]))
    open(os.path.join(a.out, "RECEIPT.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
