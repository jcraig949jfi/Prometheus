#!/usr/bin/env python3
"""Profile the SFE write path, and answer: client, engine, or host?

    python deploy/write_path_profile.py [--json]

Two rows died on "The read operation timed out" on 2026-09-10 AFTER their
experiment had been committed, while the engine was writing ~3768
experiments/hour. The operator's instruction was: no tuning without the
measurement. This is the measurement.

EVERYTHING HERE RUNS ON A THROWAWAY ENGINE. The live ledger is read only for
its shape (row counts, chain length), never written.

WHAT IT MEASURES
  1. per-operation latency on an empty ledger
  2. how that latency SCALES as the hash chain grows
  3. writer serialisation: N concurrent writers through Store.write()
  4. THE TWO DEADLINES -- the client's socket timeout against the engine's
     effective SQLite lock wait
"""
from __future__ import annotations

import argparse
import inspect
import json
import os
import socket
import statistics
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.dirname(HERE)
SF = os.path.dirname(ENG)
for p in (ENG, os.path.join(SF, "SerendipityFoundryClient")):
    if p not in sys.path:
        sys.path.insert(0, p)

from sfe.runtime import Foundry                                   # noqa: E402
from sfe.store import Store                                       # noqa: E402
import sfclient                                                   # noqa: E402

LIVE_DB = r"F:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine\var\engine.db"


def ms(seconds):
    return round(seconds * 1000.0, 3)


def percentiles(xs):
    xs = sorted(xs)
    if not xs:
        return {}
    def p(q):
        return xs[min(len(xs) - 1, int(q * len(xs)))]
    return {"p50": ms(p(0.50)), "p90": ms(p(0.90)), "p99": ms(p(0.99)),
            "max": ms(xs[-1]), "n": len(xs)}


def bench_operations(tmp, n=60):
    """One experiment's worth of writes, repeatedly, on a fresh ledger."""
    f = Foundry(os.path.join(tmp, "ops.db"))
    c = f.create_client("prof")
    s = f.create_session(c, "prof")
    w = f.create_world(s, "prof")["world_id"]
    f.start_world(w, c)
    timings = {"create_artifact": [], "hypothesis": [], "experiment": [],
               "observation": [], "commit_experiment": []}
    for i in range(n):
        t = time.perf_counter()
        f.create_artifact(w, "blob", b"x" * 256, client_id=c)
        timings["create_artifact"].append(time.perf_counter() - t)

        t = time.perf_counter()
        h = f.propose_hypothesis(w, "h%d" % i, client_id=c)
        timings["hypothesis"].append(time.perf_counter() - t)

        t = time.perf_counter()
        e = f.create_experiment(w, {"spec_version": 1, "i": i},
                                hyp_id=h, client_id=c)
        e = e["exp_id"] if isinstance(e, dict) else e
        timings["experiment"].append(time.perf_counter() - t)

        t = time.perf_counter()
        f.record_observation(w, e, {"v": i}, "SURVIVED", client_id=c)
        timings["observation"].append(time.perf_counter() - t)

        t = time.perf_counter()
        f.commit_experiment(w, e, client_id=c)
        timings["commit_experiment"].append(time.perf_counter() - t)
    f.close()
    return {k: percentiles(v) for k, v in timings.items()}


def bench_chain_growth(tmp, steps=(0, 2000, 8000, 20000)):
    """Does a write get slower as the hash chain gets longer?

    THE QUESTION BEHIND THE QUESTION. events is append-only and each entry
    hashes the previous one, so if the append re-read or re-scanned the chain,
    latency would climb with ledger size -- and the engine has 63k events.
    """
    f = Foundry(os.path.join(tmp, "chain.db"))
    c = f.create_client("prof")
    s = f.create_session(c, "prof")
    w = f.create_world(s, "prof")["world_id"]
    f.start_world(w, c)
    out, written = [], 0
    for target in steps:
        while written < target:
            f.create_artifact(w, "blob", b"y" * 64, client_id=c)
            written += 1
        samples = []
        for _ in range(40):
            t = time.perf_counter()
            f.create_artifact(w, "blob", os.urandom(64), client_id=c)
            samples.append(time.perf_counter() - t)
            written += 1
        out.append({"events_before": target, **percentiles(samples)})
    f.close()
    return out


def bench_concurrency(tmp, workers=(1, 2, 4, 8), per_worker=25):
    """Store.write() takes BEGIN IMMEDIATE, so writers serialise. How badly?"""
    results = []
    for n in workers:
        f = Foundry(os.path.join(tmp, "conc%d.db" % n))
        c = f.create_client("prof")
        s = f.create_session(c, "prof")
        w = f.create_world(s, "prof")["world_id"]
        f.start_world(w, c)
        lat, errs = [], []
        lock = threading.Lock()

        def work():
            for _ in range(per_worker):
                t = time.perf_counter()
                try:
                    f.create_artifact(w, "blob", os.urandom(48), client_id=c)
                    d = time.perf_counter() - t
                    with lock:
                        lat.append(d)
                except Exception as e:                       # noqa: BLE001
                    with lock:
                        errs.append(type(e).__name__)

        t0 = time.perf_counter()
        ts = [threading.Thread(target=work) for _ in range(n)]
        for x in ts:
            x.start()
        for x in ts:
            x.join()
        wall = time.perf_counter() - t0
        f.close()
        results.append({"writers": n, "writes": n * per_worker,
                        "wall_s": round(wall, 3),
                        "throughput_per_s": round((n * per_worker) / wall, 1),
                        "errors": errs[:5], "latency": percentiles(lat)})
    return results


def bench_deadlines(tmp):
    """THE HEADLINE. The client's socket timeout vs the engine's real lock wait.

    They are both configured as 30 s and they are NOT the same deadline:
    SQLite's busy handler accumulates SLEEP time, not wall-clock, so it
    overshoots. Whichever expires first decides what the caller sees.
    """
    db = os.path.join(tmp, "dead.db")
    st = Store(db)
    st.initialize()
    configured = st._conn.execute("PRAGMA busy_timeout").fetchone()[0]

    started = threading.Event()

    def holder():
        h = Store(db)
        h.initialize()
        with h.write() as cx:
            cx.execute("SELECT 1")
            started.set()
            time.sleep(50)

    threading.Thread(target=holder, daemon=True).start()
    started.wait(10)
    time.sleep(0.5)
    t0 = time.perf_counter()
    engine_err = None
    try:
        w = Store(db)
        w.initialize()
        with w.write() as cx:
            cx.execute("SELECT 1")
        engine_wait = time.perf_counter() - t0
    except Exception as e:                                   # noqa: BLE001
        engine_wait = time.perf_counter() - t0
        engine_err = type(e).__name__

    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    port = srv.getsockname()[1]

    def blackhole():
        try:
            conn, _ = srv.accept()
            time.sleep(120)
            conn.close()
        except OSError:
            pass

    threading.Thread(target=blackhole, daemon=True).start()
    cl = sfclient.EngineClient("http://127.0.0.1:%d" % port, token="x")
    t0 = time.perf_counter()
    client_err = None
    try:
        cl.version()
        client_wait = time.perf_counter() - t0
    except Exception as e:                                   # noqa: BLE001
        client_wait = time.perf_counter() - t0
        client_err = "%s: %s" % (type(e).__name__, str(e)[:40])
    srv.close()

    client_default = inspect.signature(
        sfclient.EngineClient.__init__).parameters["timeout"].default
    return {
        "client_configured_s": client_default,
        "engine_configured_busy_timeout_ms": configured,
        "client_gave_up_after_s": round(client_wait, 2),
        "client_error": client_err,
        "engine_lock_wait_s": round(engine_wait, 2),
        "engine_error": engine_err,
        "client_gives_up_first_by_s": round(engine_wait - client_wait, 2),
    }


def live_shape():
    import sqlite3
    if not os.path.exists(LIVE_DB):
        return {"unavailable": LIVE_DB}
    cx = sqlite3.connect("file:%s?mode=ro" % LIVE_DB.replace("\\", "/"),
                         uri=True, timeout=20)
    try:
        out = {"db_bytes": os.path.getsize(LIVE_DB)}
        for t in ("events", "experiments", "observations", "artifacts",
                  "work_items"):
            try:
                out[t] = cx.execute("SELECT COUNT(*) FROM %s" % t).fetchone()[0]
            except sqlite3.Error:
                out[t] = None
        busiest = cx.execute(
            "SELECT strftime('%Y-%m-%dT%HZ', ts, 'unixepoch') h, COUNT(*) n "
            "FROM events GROUP BY h ORDER BY n DESC LIMIT 3").fetchall()
        out["busiest_hours"] = [{"hour": h, "events": n} for h, n in busiest]
        if busiest:
            top = busiest[0][0]
            gaps = []
            rows = cx.execute(
                "SELECT ts FROM events WHERE strftime('%Y-%m-%dT%HZ', ts, "
                "'unixepoch')=? ORDER BY ts", (top,)).fetchall()
            for i in range(1, len(rows)):
                gaps.append(rows[i][0] - rows[i - 1][0])
            out["inter_event_gap_ms_in_busiest_hour"] = percentiles(gaps)
        return out
    finally:
        cx.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", default=os.path.join(
        HERE, "WRITE_PATH_PROFILE_2026-09-10.json"))
    a = ap.parse_args()

    tmp = tempfile.mkdtemp(prefix="sfe-profile-")
    print("SFE WRITE-PATH PROFILE -- throwaway engine at %s" % tmp)
    print("=" * 74)

    R = {"_what_this_is":
         "Measured on a throwaway engine. The live ledger was read only for "
         "its shape. No tuning is proposed here that is not supported by a "
         "number in this file.",
         "live_shape": live_shape()}
    print("\n-- live ledger shape --")
    print("  " + json.dumps(R["live_shape"])[:300])

    print("\n-- per-operation latency, empty ledger (ms) --")
    R["operations_ms"] = bench_operations(tmp)
    for k, v in R["operations_ms"].items():
        print("  %-20s p50=%-8s p90=%-8s p99=%-8s max=%s"
              % (k, v["p50"], v["p90"], v["p99"], v["max"]))

    print("\n-- does latency grow with the hash chain? (ms) --")
    R["chain_growth_ms"] = bench_chain_growth(tmp)
    for row in R["chain_growth_ms"]:
        print("  after %-7d events   p50=%-8s p99=%-8s max=%s"
              % (row["events_before"], row["p50"], row["p99"], row["max"]))

    print("\n-- concurrent writers through Store.write() --")
    R["concurrency"] = bench_concurrency(tmp)
    for row in R["concurrency"]:
        print("  %d writer(s): %5.1f writes/s   p50=%-8s p99=%-8s errors=%s"
              % (row["writers"], row["throughput_per_s"],
                 row["latency"]["p50"], row["latency"]["p99"],
                 row["errors"] or "none"))

    print("\n-- THE TWO DEADLINES --")
    R["deadlines"] = bench_deadlines(tmp)
    d = R["deadlines"]
    print("  client configured        : %s s" % d["client_configured_s"])
    print("  engine busy_timeout      : %s ms" %
          d["engine_configured_busy_timeout_ms"])
    print("  client actually gave up  : %s s  (%s)"
          % (d["client_gave_up_after_s"], d["client_error"]))
    print("  engine lock wait actually: %s s  (%s)"
          % (d["engine_lock_wait_s"], d["engine_error"]))
    print("  CLIENT GIVES UP FIRST BY : %s s" % d["client_gives_up_first_by_s"])

    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(R, indent=2) + "\n")
    print("\n  written: %s" % a.out)
    if a.json:
        print(json.dumps(R, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
