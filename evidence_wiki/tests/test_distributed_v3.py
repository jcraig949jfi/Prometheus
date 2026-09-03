"""V3 distributed qualification (charter s17, gates G17-G22).

Four concurrent WORKER PROCESSES with distinct machine identities drive the
live service: sustained synthetic-namespace ingest with duplicate/retry
injection, a worker killed mid-run and replayed, concurrent reads during
writes, and duplicate-freedom verification. Cross-host caveat: workers run
on M1 (peers have not pulled the branch); this qualifies the SERVICE under
concurrency, not the LAN, and is reported as such.
"""
import json
import multiprocessing as mp
import random
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

WORKER_SRC = r'''
import hashlib, json, random, sys, time
sys.path.insert(0, r"{here}")
from ew.client import EvidenceWiki
machine, start, count, die_at = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
run_tag = sys.argv[5]
ew = EvidenceWiki(machine=machine, agent=f"v3-ingest-{{machine}}")
lat = []
# Deterministic across processes. The original seed was hash(machine), which
# Python randomizes per process (PYTHONHASHSEED): every rerun therefore sent
# DIFFERENT outcomes under the SAME encounter ids. The pre-006 service hid
# that behind ON CONFLICT DO NOTHING; it now returns 409, correctly.
rng = random.Random(int(hashlib.sha256(machine.encode()).hexdigest()[:8], 16))
for i in range(start, start + count):
    if die_at >= 0 and i - start == die_at:
        sys.exit(9)  # simulated crash mid-batch
    eid = f"SYN-{{i:06d}}"
    row = {{
        "encounter_id": eid,
        "run_id": run_tag,          # fresh execution identity per battery run
        "sfe_entry_hash": f"sha256:synthetic{{i:056d}}",
        "world_id": f"synw_{{i % 40:03d}}",
        "outcome": rng.choice(["committed", "low_score", "timeout", "crash"]),
        "failure_class": rng.choice([None, "low_score", "timeout"]),
        "namespace": "synthetic",
        "idempotency_key": f"syn-{{run_tag}}-{{eid}}"}}
    t0 = time.time()
    r = ew._post("fossil/encounters", row)
    lat.append(time.time() - t0)
    if rng.random() < 0.10:  # duplicate/retry injection: byte-identical replay
        ew._post("fossil/encounters", dict(row))
print(json.dumps({{"machine": machine, "n": count,
                  "p50_ms": sorted(lat)[len(lat)//2]*1000,
                  "p95_ms": sorted(lat)[int(len(lat)*0.95)]*1000}}))
'''


def main():
    from ew import db
    worker_py = HERE / "tests" / "_v3_worker.py"
    worker_py.write_text(WORKER_SRC.format(here=str(HERE)), encoding="utf-8")
    R = {}
    # Events per worker. Default 150; pass a smaller N when the host is under
    # heavy co-tenant load -- the STRUCTURE (4 identities, duplicate/retry
    # injection, crash + full replay, concurrent reads) is what qualifies the
    # write path, and the results file records the scale actually run.
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    run_tag = "reqal-" + time.strftime("%Y%m%dT%H%M%S")
    t0 = time.time()
    procs = []
    for i, m in enumerate(["M1", "M2", "M3", "M4"]):
        die = (2 * N) // 5 if m == "M3" else -1  # M3 crashes mid-batch
                                                 # (scales with N)
        p = subprocess.Popen([sys.executable, str(worker_py), m,
                              str(i * N), str(N), str(die), run_tag],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True)
        procs.append((m, p))
    # concurrent reads while writing (G17)
    import requests
    from ew.client import CFG
    hdrs = {"Authorization": f"Bearer {CFG['auth_token']}",
            "X-Prometheus-Machine": "M1", "X-Prometheus-Agent": "v3-reader"}
    read_lat, read_ok = [], 0
    for _ in range(30):
        r0 = time.time()
        r = requests.get(f"http://localhost:{CFG['port']}/api/v1/native/fossil/matrix",
                         headers=hdrs, timeout=30)
        read_lat.append(time.time() - r0)
        read_ok += r.status_code == 200
        time.sleep(0.2)
    outs = {}
    for m, p in procs:
        out, err = p.communicate(timeout=600)
        outs[m] = {"exit": p.returncode, "out": out.strip()[:200]}
    # replay the crashed worker's FULL batch (G19/G21: recovery + replay)
    i = 2
    p = subprocess.run([sys.executable, str(worker_py), "M3",
                        str(i * N), str(N), "-1", run_tag],
                       capture_output=True, text=True, timeout=600)
    outs["M3_replay"] = {"exit": p.returncode, "out": p.stdout.strip()[:200]}
    wall = time.time() - t0

    conn = db.connect()
    with db.dict_cur(conn) as cur:
        # Scored by the INVARIANT (stored == distinct, and this run's rows
        # all landed), not by an absolute count: the substrate is append-only
        # and accumulates legitimately across runs.
        cur.execute("SELECT COUNT(*) n, COUNT(DISTINCT encounter_id) d "
                    "FROM ew.fossil_encounters WHERE namespace='synthetic' "
                    "AND run_id=%s", (run_tag,))
        row = cur.fetchone()
        cur.execute("SELECT COUNT(*) n FROM ew.fossil_encounters "
                    "WHERE namespace='synthetic' AND (sfe_entry_hash IS NULL "
                    "OR sfe_entry_hash='') AND run_id=%s", (run_tag,))
        noprov = cur.fetchone()["n"]
        cur.execute("SELECT machine, COUNT(*) FROM ew.write_log WHERE "
                    "endpoint='fossil.encounter' AND idempotency_key LIKE %s "
                    "GROUP BY 1", (f"syn-{run_tag}-%",))
        by_machine = {r["machine"]: r["count"] for r in cur.fetchall()}
    conn.close()
    R = {
        "run_tag": run_tag,
        "workers": outs,
        "n_per_worker": N,
        "expected_unique": 4 * N,
        "stored_rows": row["n"], "stored_distinct": row["d"],
        "no_silent_duplicates_G21": row["n"] == row["d"] == 4 * N,
        "provenance_failures": noprov,
        "writes_logged_by_machine": by_machine,
        "reads_during_writes_G17": {"ok": read_ok, "of": 30,
            "p95_ms": round(sorted(read_lat)[28] * 1000, 1)},
        "crash_recovery_G19": outs["M3"]["exit"] == 9 and
                              outs["M3_replay"]["exit"] == 0,
        "wall_seconds": round(wall, 1),
        "service_path_events_per_sec": round((4 * N) / wall, 1),
        "cross_host_caveat": "4 concurrent processes with distinct machine identities on M1; LAN legs pending M2-M4 pulling the branch",
    }
    (HERE / "v3" / "distributed_qualification.json").write_text(
        json.dumps(R, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in R.items() if k != "workers"}, indent=1))


if __name__ == "__main__":
    main()
