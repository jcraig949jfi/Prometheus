"""C-ABLATE (CONFIRM lane, fresh and frozen). Parent: X-DENSE-ABLATE (EXPLORE): under 1-byte
world-op encodings, removing self-location (27 -> 2 cells with replication) or in-place search
(27 -> 5) abolished spontaneous replication; removing energy inheritance did not (27 -> 26) but
halved child replication (depth >= 2: 11 -> 6).

NOTHING HERE MAY CHANGE AFTER COMMIT: cells, seeds, arms, endpoints, rules, allocation.

Fresh sample: tier-M FREE-physics BLOCK cells from the 1,255 predecessor random starts, never
used by any earlier experiment (X-NONPAIR-SEARCH, C-SELFLOC, C-ENERGY, C-DENSE), excluding the
localized structural failures; the first 40 by ascending sha256(run_id). Seeds 9_995_000 + k.
One job per worker process. Arms (shared seed): FULL, NO_LOC, NO_SEARCH, NO_ENERGY (dense
encodings in all; X-DENSE-ABLATE definitions).
Endpoints per run: R = replication_events > 0; D2 = max_causal_replication_depth >= 2.
Rules (each a separate verdict):
  LOC_NECESSARY     #R(FULL) - #R(NO_LOC) >= 8 and one-sided sign test on discordant cells p < 0.01
  SEARCH_NECESSARY  #R(FULL) - #R(NO_SEARCH) >= 8 and sign test p < 0.01
  ENERGY_FOR_DEPTH  |#R(FULL) - #R(NO_ENERGY)| <= 4 AND #D2(FULL) - #D2(NO_ENERGY) >= 3 with sign
                    test on D2-discordant cells p < 0.05

    python run_ca.py -> CELLS.json, RESULTS.json, VERDICT.json
"""
from __future__ import annotations

import hashlib
import json
import math
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
CAMP = ROOT.parent
FOR = CAMP / "z80atlas-forensics-2026-09-23"
sys.path.insert(0, str(CAMP / "z80atlas-verify-2026-09-22"))
sys.path.insert(0, str(ROOT / "x_dense_ablate"))
sys.path.insert(0, str(ROOT / "x_dense_ops"))
ARMS = ("FULL", "NO_LOC", "NO_SEARCH", "NO_ENERGY")


def cells():
    runs = [json.loads(l) for l in open(FOR / "FROZEN_FUNNEL_RUNS.jsonl")]
    used = set()
    for f in ("x_nonpair_search", "c_selfloc_confirm", "c_energy_confirm", "c_dense_confirm"):
        used |= {c["source_run"] for c in json.loads((ROOT / f / "CELLS.json").read_text())}
    sys.path.insert(0, str(FOR))
    import forensic
    cand = []
    for r in runs:
        if r["physics"] == "OVERWRITE" or r["tier"] != "M" or r["copy_primitive"] != "BLOCK" or r["run_id"] in used:
            continue
        cc = forensic.frozen_record(r["run_id"])[0]["job"]["cell"]
        if cc["pressure"] == "MINIMAL_CRITERION" or (cc["reproduction"] == "CONSTRUCTIVE" and cc["world"] == "GRAPH"):
            continue
        cand.append({"source_run": r["run_id"], "physics": r["physics"], "cell": cc})
    cand.sort(key=lambda c: hashlib.sha256(c["source_run"].encode()).hexdigest())
    return cand[:40]


def job(args):
    k, cell, arm = args
    import run_a
    r = run_a.job((k, cell, arm))                      # same world definitions as X-DENSE-ABLATE
    return {"k": k, "arm": arm, "R": r["replication_events"] > 0, "D2": r["max_causal_depth"] >= 2,
            "depth": r["max_causal_depth"]}


def sign_p(up, down):
    n = up + down
    return sum(math.comb(n, x) for x in range(up, n + 1)) / 2 ** n if n else 1.0


def main():
    cs = cells()
    (HERE / "CELLS.json").write_text(json.dumps(cs, indent=1))
    # run_a.job seeds from 9_960_000 + j; C-ABLATE must use fresh seeds, so pass j = k + 35_000
    todo = [(k + 35_000, c["cell"], arm) for k, c in enumerate(cs) for arm in ARMS]
    with mp.Pool(6, maxtasksperchild=1) as pool:
        res = pool.map(job, todo)
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    by = {}
    for r in res:
        by.setdefault(r["k"], {})[r["arm"]] = r

    def cnt(arm, key):
        return sum(1 for v in by.values() if v[arm][key])

    def disc(a, b, key):
        up = sum(1 for v in by.values() if v[a][key] and not v[b][key])
        down = sum(1 for v in by.values() if v[b][key] and not v[a][key])
        return up, down
    out = {"cells": len(cs), "seed_base": 9_960_000 + 35_000,
           "R": {a: cnt(a, "R") for a in ARMS}, "D2": {a: cnt(a, "D2") for a in ARMS}}
    for arm, name in (("NO_LOC", "LOC_NECESSARY"), ("NO_SEARCH", "SEARCH_NECESSARY")):
        up, down = disc("FULL", arm, "R")
        p = sign_p(up, down)
        out[name] = {"diff": out["R"]["FULL"] - out["R"][arm], "discordant": [up, down], "p": p,
                     "verdict": "CONFIRMED" if out["R"]["FULL"] - out["R"][arm] >= 8 and p < 0.01 else "NOT_CONFIRMED"}
    up, down = disc("FULL", "NO_ENERGY", "D2")
    p = sign_p(up, down)
    rdiff = abs(out["R"]["FULL"] - out["R"]["NO_ENERGY"])
    d2diff = out["D2"]["FULL"] - out["D2"]["NO_ENERGY"]
    out["ENERGY_FOR_DEPTH"] = {"R_absdiff": rdiff, "D2_diff": d2diff, "discordant": [up, down], "p": p,
                               "verdict": "CONFIRMED" if rdiff <= 4 and d2diff >= 3 and p < 0.05 else "NOT_CONFIRMED"}
    (HERE / "VERDICT.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
