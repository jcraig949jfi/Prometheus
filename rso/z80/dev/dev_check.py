"""C-017-T030 development check (dev partition 17_030_xxx only; PREREGISTRATION.md s7). Two parts, rows gzipped beside this file:
    python -m rso.z80.assay dev rso/z80/dev/DEV_ROWS 8 0/2    (and 1/2 in a second process)   every arm at n = 8, plus forgeries
    python -m rso.z80.dev.dev_check power 0/2                    (and 1/2) RECON_ENDO_IMPL and NH_ENDO_SHORT at their confirmatory n = 48
    python -m rso.z80.dev.dev_check summary                      DEV_CHECK.json: the frozen rule applied to the dev rows
The summary scores every arm from DEV_ROWS except the two powered arms, which come from DEV_POWER (their first 8 seeds are in both).
"""
import json
import os
import sys

from rso.slice001.receipt import sha256_hex
from rso.z80 import analysis, assay

HERE = os.path.dirname(os.path.abspath(__file__))
POWERED = ("RECON_ENDO_IMPL", "NH_ENDO_SHORT")


def power(shard):
    import gzip
    rows = assay.run("dev", lambda a: assay.CONFIRM_N[a] if a in POWERED else 0, shard)
    with gzip.open(os.path.join(HERE, "DEV_POWER.%d-%d.jsonl.gz" % shard), "wt", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    print("rows", len(rows), "sha256", sha256_hex(rows))


def summary():
    base = analysis.load([os.path.join(HERE, "DEV_ROWS.%d-2.jsonl.gz" % i) for i in (0, 1)])
    pw = analysis.load([os.path.join(HERE, "DEV_POWER.%d-2.jsonl.gz" % i) for i in (0, 1)])
    rows = [r for r in base if r["arm"] not in POWERED] + pw
    rows.sort(key=lambda r: (r["arm"], r["seed"], r["forgery"]))
    v = analysis.verdict(rows)
    out = {"schema": "rso.z80.dev_check.v1", "partition": "dev 17_030_xxx", "n_rows": len(rows), "rows_sha256": sha256_hex(rows),
           "verdict_on_dev": v["verdict"], "failed": v["failed"], "unpowered": v["unpowered"], "baselines_passing_q1": v["baselines_passing_q1"],
           "q1": v["q1"], "q2": v["q2"], "q3": v["q3"], "q4": v["q4"], "confusion": v["confusion"],
           "purity": {a: [sum(r["n_" + r["cls"]] for r in rows if r["arm"] == a and not r["forgery"] and r["cls"] in assay.LABELS),
                          sum(r["n_func"] for r in rows if r["arm"] == a and not r["forgery"] and r["cls"] in assay.LABELS)]
                      for a in sorted({r["arm"] for r in rows})}}
    with open(os.path.join(HERE, "DEV_CHECK.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    print(out["verdict_on_dev"], out["failed"], out["unpowered"], out["rows_sha256"])


if __name__ == "__main__":
    if sys.argv[1] == "power":
        power(tuple(int(x) for x in sys.argv[2].split("/")))
    else:
        summary()
