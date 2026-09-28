"""P2 cross-host claim race (protocol: fabric/pilot/P2_CROSSHOST_PROTOCOL.md, frozen before the run).

    EW_DB_HOST=192.168.1.202 python3 fabric/pilot/run_p2_crosshost.py
"""
from __future__ import annotations

import json
import random
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from fabric import store as S  # noqa: E402

EV = Path(__file__).parent / "evidence"; EV.mkdir(exist_ok=True)
RUN = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
CAPS = ["compute.cpu.light"]
PARAMS = {"seconds": 0.5, "text": "p2 crosshost"}


def wait_terminal(conn, tids, timeout=300):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if all(S.get_task(conn, t)["state"] in S.TERMINAL for t in tids):
            return True
        time.sleep(0.5)
    return False


def remote_live(conn):
    return [a for a in S.agents(conn) if a["agent"] == "worker.ubu002" and a["live"]]


def main():
    conn = S.connect()
    if not remote_live(conn):
        print(json.dumps({"test": "P2-crosshost", "pass": None, "error": "worker.ubu002 not live; nothing run"}))
        return 2
    w = subprocess.Popen([sys.executable, "-m", "fabric", "worker", "--agent", "worker.ubu001", "--caps", *CAPS,
                          "--executors", "synthetic", "--poll-s", "5", "--idle-exit-s", "900"], cwd=str(REPO),
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(8)
    rng = random.Random(2026)
    r1, r2 = [], []
    try:
        for i in range(20):
            tid = S.submit(conn, "Odysseus", "P2 cross-host single-task round %d" % i, "synthetic", required_caps=CAPS,
                           params=PARAMS, max_attempts=1, idempotency_key="p2x-%s-r1-%02d" % (RUN, i),
                           title="P2x R1 round %d" % i, thread_id="thr-fabric-p2x")["task_id"]
            r1.append(tid)
            wait_terminal(conn, [tid], timeout=120)
            time.sleep(rng.uniform(0, 6))
        for i in range(30):
            r2.append(S.submit(conn, "Odysseus", "P2 cross-host batch task %d" % i, "synthetic", required_caps=CAPS,
                               params=PARAMS, max_attempts=1, idempotency_key="p2x-%s-r2-%02d" % (RUN, i),
                               title="P2x R2 batch %d" % i, thread_id="thr-fabric-p2x")["task_id"])
        wait_terminal(conn, r2, timeout=300)
    finally:
        w.terminate(); w.wait(timeout=30)

    def row(tid):
        t = S.get_task(conn, tid)
        ev = S.events(conn, tid)
        sub = next(e["at"] for e in ev if e["kind"] == "submitted")
        st = [e["at"] for e in ev if e["kind"] == "attempt_started"]
        return {"task": tid, "state": t["state"], "attempts": [(a["attempt_id"], a["host"], a["status"]) for a in t["attempts"]],
                "claimed_events": sum(1 for e in ev if e["kind"] == "claimed"),
                "claim_latency_s": round((st[0] - sub).total_seconds(), 2) if st else None}
    rows1, rows2 = [row(t) for t in r1], [row(t) for t in r2]
    allrows = rows1 + rows2
    c1 = [r for r in allrows if not (len(r["attempts"]) == 1 and r["attempts"][0][2] == "succeeded" and r["state"] == "completed")]
    c2 = [r for r in allrows if r["claimed_events"] != 1]
    wins1 = Counter(r["attempts"][0][1] for r in rows1 if r["attempts"])
    wins2 = Counter(r["attempts"][0][1] for r in rows2 if r["attempts"])
    lat = {}
    for r in allrows:
        if r["attempts"] and r["claim_latency_s"] is not None:
            lat.setdefault(r["attempts"][0][1], []).append(r["claim_latency_s"])
    res = {"test": "P2-crosshost", "run": RUN,
           "pass": not c1 and not c2 and wins1.get("ubu001", 0) >= 1 and wins1.get("ubu002", 0) >= 1
                   and wins2.get("ubu001", 0) >= 1 and wins2.get("ubu002", 0) >= 1,
           "criterion_1_exactly_one_successful_attempt_violations": c1, "criterion_2_duplicate_claim_events": c2,
           "r1_single_task_wins": dict(wins1), "r2_batch_wins": dict(wins2),
           "claim_latency_s_median": {h: sorted(v)[len(v) // 2] for h, v in lat.items()},
           "tasks_total": len(allrows), "r1": rows1, "r2": rows2,
           "finished": time.strftime("%FT%TZ", time.gmtime())}
    (EV / "P2-crosshost.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: res[k] for k in ("test", "pass", "r1_single_task_wins", "r2_batch_wins", "claim_latency_s_median",
                                          "tasks_total")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
