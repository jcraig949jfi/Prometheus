"""Phase 2E: local mutational neighbourhoods around five genome categories, measured with the REPAIRED instruments.

For each tape X (with its representation), over the fixed single-substitution set (every position x 16 deltas =
L*16 mutants) and one seeded 8-input panel of INC (ATOMIC, ABR; one ruler for every category):
  bd            paired beneficial density (mutant panel score > X's)
  neutral       fraction of mutants with an identical panel score
  sr_base       X self-copies in isolation (adjudication.repro_descriptor)
  sr_lethal     among mutants of an SR tape: fraction that no longer self-copy
  sr_gain       among mutants of a non-SR tape: fraction that DO self-copy (basin-entry density one step away)
Categories (inputs file built from receipts; each tape carries its provenance):
  random, nonreplicator (top tapes of runs with no traced SELF_REPLICATION), first_gen (first self-replicating
  writer of each traced spontaneous run = an origin), evolved (dominant tape at the end of traced spontaneous runs
  when it self-copies), flagged_bd (top tapes of REPRODUCTIVE_MACHINERY_RAISED_BENEFICIAL_DENSITY runs).
    python neighbourhood.py --inputs <json> --workers 12      -> receipts/NEIGHBOURHOOD.json"""
from __future__ import annotations

import argparse
import collections
import json
import multiprocessing as mp
import os
import random
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(__file__))
import load as Ld  # noqa: E402

WORKTREE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
DELTAS = (1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 128, 144, 170, 200, 233, 255)


def _one(item):
    if WORKTREE not in sys.path:
        sys.path.insert(0, WORKTREE)
    from prometheus.z80atlas.world import Config
    from prometheus.z80atlas.tasks import Task
    from prometheus.z80atlas import geometry as Gm, adjudication as A
    cat, rep, tape_hex, prov = item
    cfg = Config(representation=rep, task="INC", scoring="ATOMIC")
    L = cfg.L
    X = bytes.fromhex(tape_hex)[:L]; X = X + bytes(L - len(X))
    task = Task("INC")
    pb = Gm.scan_paired(X, cfg, task, seed=20260923)
    sr0 = A.repro_descriptor(X, cfg, task)["self_copy"]
    flips = 0; n = 0
    for p in range(L):
        for d in DELTAS:
            t = bytearray(X); t[p] = (t[p] + d) & 0xFF; n += 1
            if A.repro_descriptor(bytes(t), cfg, task)["self_copy"] != sr0:
                flips += 1
    return {"cat": cat, "rep": rep, "prov": prov, "bd": pb["beneficial_density"], "neutral": pb["neutral_fraction"], "base": pb["base_score"],
            "sr_base": sr0, "sr_lethal": round(flips / n, 4) if sr0 else None, "sr_gain": round(flips / n, 4) if not sr0 else None}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    items = [tuple(x) for x in json.loads(open(a.inputs, encoding="utf-8").read())["items"]]
    with mp.Pool(a.workers) as pool:
        rows = pool.map(_one, items, chunksize=1)
    by = collections.defaultdict(list)
    for r in rows:
        by[r["cat"]].append(r)
    summ = {}
    for cat, rs in by.items():
        f = lambda k: [r[k] for r in rs if r[k] is not None]
        summ[cat] = {"n": len(rs), "sr_base_frac": round(sum(r["sr_base"] for r in rs) / len(rs), 3),
                     "bd_mean": round(st.mean(f("bd")), 4), "bd_median": st.median(f("bd")), "neutral_mean": round(st.mean(f("neutral")), 4),
                     "sr_lethal_mean": round(st.mean(f("sr_lethal")), 4) if f("sr_lethal") else None,
                     "sr_gain_mean": round(st.mean(f("sr_gain")), 5) if f("sr_gain") else None,
                     "sr_gain_any_frac": round(sum(1 for x in f("sr_gain") if x > 0) / len(f("sr_gain")), 3) if f("sr_gain") else None}
    p = Ld.write("NEIGHBOURHOOD.json", {"definition": __doc__, "summary": summ, "rows": rows})
    print(p); print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
