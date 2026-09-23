"""A3 kill matrix: hard-kill producers, the writer and Redis mid-stream, then
count lost / duplicate / phantom events exactly and re-verify every chain.

Runs against the PRIVATE fabric substrate (gw-fabric, 127.0.0.1:6395), never
the shared bus. Rows: primordial/ledger/rows/A/A3_killmatrix_<stamp>.jsonl.

  python -m primordial.fabric.killmatrix [--quick] [--hdd-dir F:/lab/pm-data-A]

Expectations written before the run (the claim):
  correct writer : lost == 0 and verify ok in EVERY fault scenario
  cheat writer   : (--ack-before-commit, killed mid-batch) lost > 0, or the
                   instrument cannot see loss and every correct PASS is void
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time

import redis

from primordial.fabric import ledger as L

ROOT = pathlib.Path(__file__).resolve().parents[2]
URL = "redis://127.0.0.1:6395/0"
CONTAINER = "gw-fabric"
PY = sys.executable
DATA = pathlib.Path(os.environ.get("PM_DATA_A", "C:/Users/jcrai/lab/pm-data/A")) / "a3"


def spawn(*args: str) -> subprocess.Popen:
    env = dict(os.environ, PYTHONPATH=str(ROOT))
    return subprocess.Popen([PY, "-m", "primordial.fabric.ledger", *args], cwd=str(ROOT),
                            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def acked_count(path: pathlib.Path) -> int:
    try:
        with open(path, "rb") as fh:
            return fh.read().count(b"\n")
    except FileNotFoundError:
        return 0


def wait_ping(r: redis.Redis, timeout=60) -> float:
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            if r.ping():
                return time.time() - t0
        except (redis.ConnectionError, redis.TimeoutError):
            pass
        time.sleep(0.1)
    raise RuntimeError("fabric redis did not come back")


def kill_redis(r: redis.Redis) -> float:
    subprocess.run(["wsl.exe", "-e", "docker", "kill", CONTAINER], capture_output=True, timeout=60)
    time.sleep(1.0)
    subprocess.run(["wsl.exe", "-e", "docker", "start", CONTAINER], capture_output=True, timeout=60)
    return wait_ping(r)


def drained(r: redis.Redis, stream: str) -> bool:
    try:
        for g in r.xinfo_groups(stream):
            name = g["name"].decode() if isinstance(g["name"], bytes) else g["name"]
            if name == "writer":
                return g["pending"] == 0 and (g.get("lag") in (0, None)) and \
                    g.get("entries-read") is not None and g["entries-read"] >= r.xlen(stream)
    except (redis.ConnectionError, redis.TimeoutError, redis.ResponseError):
        return False
    return False


def scenario(name, n, producers, fault="none", writer_flags=(), db_dir=DATA, pipe=50):
    r = redis.Redis.from_url(URL, socket_timeout=5)
    wait_ping(r)
    stream = f"a3:{name}:{int(time.time()*1000)}"
    work = pathlib.Path(db_dir) / stream.replace(":", "_")
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    db, stats = str(work / "ledger.db"), str(work / "stats.txt")
    acked = [work / f"acked_p{i}.txt" for i in range(producers)]
    wargs = ["writer", "--url", URL, "--stream", stream, "--db", db, "--stats", stats, *writer_flags]
    pargs = lambda i: ["producer", "--url", URL, "--stream", stream, "--producer", f"p{i}",
                       "--n", str(n), "--acked", str(acked[i]), "--pipe", str(min(pipe, n))]
    events = []
    t0 = time.time()
    w = spawn(*wargs)
    ps = [spawn(*pargs(i)) for i in range(producers)]
    total = n * producers
    fired = fault == "none"
    deadline = t0 + 900
    restart_wargs = [x for x in wargs]
    if "--crash-after-commit" in restart_wargs:
        i = restart_wargs.index("--crash-after-commit")
        del restart_wargs[i:i + 2]
    while time.time() < deadline:
        if w.poll() == 3:                    # crashed between COMMIT and XACK by design
            events.append(("writer_crashed_after_commit", round(time.time() - t0, 3)))
            w = spawn(*restart_wargs)
        done = sum(acked_count(a) for a in acked)
        if not fired and done >= 0.4 * total:
            if fault == "kill_writer":
                w.kill(); w.wait()
                events.append(("writer_killed", round(time.time() - t0, 3), done))
                time.sleep(0.5)
                w = spawn(*wargs)
            elif fault == "kill_producer":
                ps[0].kill(); ps[0].wait()
                events.append(("producer_killed", round(time.time() - t0, 3), done))
                ps[0] = spawn(*pargs(0))
            elif fault == "kill_redis":
                back = kill_redis(r)
                events.append(("redis_killed", round(time.time() - t0, 3), done, round(back, 3)))
            elif fault == "cheat_kill_writer":
                # writer acks first then sleeps --slow-ms before commit: kill inside that window
                time.sleep(0.15)
                w.kill(); w.wait()
                events.append(("cheat_writer_killed", round(time.time() - t0, 3), done))
                time.sleep(0.5)
                w = spawn(*wargs)
            fired = True
        if all(p.poll() is not None for p in ps):
            break
        time.sleep(0.02)
    t_prod = time.time() - t0
    prod_rc = [p.returncode for p in ps]
    while time.time() < deadline and not drained(r, stream):
        if w.poll() == 3:
            events.append(("writer_crashed_after_commit", round(time.time() - t0, 3)))
            w = spawn(*restart_wargs)
        time.sleep(0.05)
    t_drain = time.time() - t0
    time.sleep(0.3)
    w.kill(); w.wait()

    attempted = {(f"p{i}", q) for i in range(producers) for q in range(n)}
    acked_set = set()
    for i, a in enumerate(acked):
        with open(a, "rb") as fh:
            acked_set |= {(f"p{i}", int(x)) for x in fh.read().split()}
    cx = L.open_db(db)
    in_db = {(p, q) for p, q in cx.execute("SELECT producer, pseq FROM events")}
    dup = 0
    if os.path.exists(stats):
        with open(stats) as fh:
            dup = sum(int(line.split()[2]) for line in fh if line.strip())
    v = L.verify(cx)
    cx.close()
    row = dict(scenario=name, fault=fault, n_per_producer=n, producers=producers,
               writer_flags=list(writer_flags), db_dir=str(db_dir), stream=stream,
               acked=len(acked_set), rows=len(in_db),
               lost=len(acked_set - in_db), phantom=len(in_db - attempted),
               unacked_but_written=len(in_db - acked_set),
               duplicates_deduped=dup, stream_len=r.xlen(stream),
               verify=v, events=events, producer_rc=prod_rc,
               t_produce_s=round(t_prod, 3), t_drain_s=round(t_drain, 3),
               events_per_s_end_to_end=round(len(in_db) / t_drain, 1) if t_drain else None)
    r.delete(stream)
    return row


def direct_baseline(n, db_dir):
    work = pathlib.Path(db_dir) / f"direct_{int(time.time()*1000)}"
    work.mkdir(parents=True)
    t0 = time.time()
    L.run_direct(str(work / "ledger.db"), n)
    dt = time.time() - t0
    cx = L.open_db(str(work / "ledger.db"))
    v = L.verify(cx)
    cx.close()
    return dict(scenario=f"direct_1txn_per_event", n_per_producer=n, producers=1, db_dir=str(db_dir),
                rows=v["rows"], verify=v, t_drain_s=round(dt, 3),
                events_per_s_end_to_end=round(n / dt, 1))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--hdd-dir", default=None)
    a = ap.parse_args(argv)
    big = 2000 if a.quick else 10000
    plan = [
        ("none_n1", 1, 1, "none", ()),
        ("none_n100", 100, 1, "none", ()),
        ("none_big_1p", big, 1, "none", ()),
        ("none_big_4p", big, 4, "none", ()),
        ("kill_writer_4p", big, 4, "kill_writer", ()),
        ("kill_producer_4p", big, 4, "kill_producer", ()),
        ("kill_redis_4p", big, 4, "kill_redis", ()),
        ("slow_writer_4p", big, 4, "none", ("--slow-ms", "50", "--batch", "100")),
        ("crash_after_commit_4p", big, 4, "none", ("--crash-after-commit", "3", "--batch", "200")),
        ("CHEAT_ack_before_commit", big, 4, "cheat_kill_writer",
         ("--ack-before-commit", "--slow-ms", "400", "--batch", "200")),
    ]
    stamp = time.strftime("%Y%m%dT%H%M%S")
    out = ROOT / "primordial" / "ledger" / "rows" / "A" / f"A3_killmatrix_{stamp}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    with open(out, "a", encoding="utf-8", newline="\n") as fh:
        def emit(row):
            rows.append(row)
            fh.write(json.dumps(row, sort_keys=True) + "\n")
            fh.flush()
            print(f"{row['scenario']:28s} rows={row['rows']:>6} lost={row.get('lost','-')!s:>5} "
                  f"dup={row.get('duplicates_deduped','-')!s:>5} verify={row['verify']['ok']} "
                  f"ev/s={row['events_per_s_end_to_end']} drain={row['t_drain_s']}s", flush=True)
        for name, n, p, fault, flags in plan:
            emit(scenario(name, n, p, fault, flags))
        emit(direct_baseline(big, DATA))
        if a.hdd_dir:
            emit(scenario("none_big_4p_HDD", big, 4, "none", (), db_dir=a.hdd_dir))
            emit(direct_baseline(min(big, 1000), a.hdd_dir))
    print("rows ->", out.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
