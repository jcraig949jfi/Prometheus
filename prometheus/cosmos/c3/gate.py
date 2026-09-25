"""The P1/P2 hard gate (roles/Cosmos/c3/S1_PREREG_P1P2_GATE.md s3-s4, amendment A1).

  python -m prometheus.cosmos.c3.gate <out_dir>
PASS iff every planted system gets its expected class in 5/5 seeds.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from prometheus.cosmos.c3.calib import planted
from prometheus.cosmos.c3.certify import certify
from prometheus.cosmos.c3.task import Task
from prometheus.cosmos.hashing import code_identity

SEEDS = (6, 7, 8, 9, 10)          # v3 gate: fresh seeds (A2); seeds 1-5 informed A2


def run(out: Path, seeds=SEEDS) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    t, tmc = Task(4, 6), Task(4, 6, h=0.5)
    rows, summary = [], {}
    for sysm, tk, expected in planted(tmc, t):
        got = []
        for s in seeds:
            t0 = time.time()
            r = certify(sysm, tk, seed=s)
            r["expected"], r["s"] = expected, round(time.time() - t0, 2)
            rows.append(r)
            got.append(r["class"])
        summary[sysm.name] = {"expected": expected, "got": got, "pass": all(g == expected for g in got)}
    res = {"identity": code_identity(), "summary": summary, "gate": "PASS" if all(v["pass"] for v in summary.values()) else "FAIL",
           "rows": rows}
    (out / "GATE.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    return res


if __name__ == "__main__":
    seeds = tuple(int(x) for x in sys.argv[2].split(",")) if len(sys.argv) > 2 else SEEDS
    r = run(Path(sys.argv[1]), seeds)
    for k, v in r["summary"].items():
        print("%-3s expected %-10s got %s" % (k, v["expected"], v["got"]))
    print("GATE", r["gate"])
