"""C-NORECOMB (CONFIRM lane, fresh and frozen). Parent: X-H2-NORECOMB (EXPLORE WEAK_SIGNAL:
with the RECOMBINATION splice off, 7ae3's implanted genome reached depth >= 5 in 3/16 seeds vs
0/16 (mean depth 13.1 vs 0.9; one seed depth 179 with 163,612 P-11 events)).

NOTHING HERE MAY CHANGE AFTER COMMIT: specimens, seeds, arms, endpoint, rule, allocation.

Claim under test: in pair-tape RECOMBINATION cells, the world's recombination splice is a
causal limit on P-11 heredity depth - turning it off (atlas_axis NONE, everything else fixed)
raises the share of implants whose causal lineage reaches depth >= 5.
Sample: the two RECOMBINATION-axis H2 specimens that ever reached causal depth >= 3 in C9:
7ae3f9c1437c8000-s54765-tL-a0 and c2a87e5970ad345d-s80949-tL-a0; C9 arm-B physics (their cell,
tier M, the frozen donor genome, one founder). Fresh seeds 9_985_000 + s, s < 24, per specimen,
shared by both arms. One job per worker process.
Arms: BASE (the cell as frozen) and NO_RECOMB (atlas_axis NONE).
Endpoint: max_causal_replication_depth >= 5 (P-11).
Rule: CONFIRMED iff pooled over the 48 seed-pairs, share(NO_RECOMB) - share(BASE) >= 0.15 AND
the one-sided Fisher exact test gives p < 0.01. Per-specimen shares reported as secondary.

    python run_cr.py -> RESULTS.json, VERDICT.json
"""
from __future__ import annotations

import json
import math
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
SPECS = ("7ae3f9c1437c8000-s54765-tL-a0", "c2a87e5970ad345d-s80949-tL-a0")


def job(args):
    spec, s, arm_name = args
    import world
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == spec)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    genome = bytes.fromhex(arm["kwargs"]["implant_hex"])
    cell = dict(arm["cell"], atlas_axis="NONE") if arm_name == "NO_RECOMB" else dict(arm["cell"])
    out = world.Runner(cell, 9_985_000 + s, tier=arm["tier"], implant="ACTUAL_GENOME",
                       implant_bytes=genome).run()
    return {"spec": spec, "s": s, "arm": arm_name, "depth": out["max_causal_replication_depth"]}


def main():
    todo = [(sp, s, a) for sp in SPECS for s in range(24) for a in ("BASE", "NO_RECOMB")]
    with mp.Pool(6, maxtasksperchild=1) as pool:
        res = pool.map(job, todo)
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    n = 48
    hit = {a: sum(r["depth"] >= 5 for r in res if r["arm"] == a) for a in ("BASE", "NO_RECOMB")}
    k0 = hit["BASE"] + hit["NO_RECOMB"]
    p = (sum(math.comb(n, x) * math.comb(n, k0 - x) for x in range(hit["NO_RECOMB"], min(n, k0) + 1))
         / math.comb(2 * n, k0)) if k0 else 1.0
    diff = (hit["NO_RECOMB"] - hit["BASE"]) / n
    per = {sp: {a: sum(r["depth"] >= 5 for r in res if r["arm"] == a and r["spec"] == sp) for a in ("BASE", "NO_RECOMB")}
           for sp in SPECS}
    v = {"verdict": "CONFIRMED" if diff >= 0.15 and p < 0.01 else "NOT_CONFIRMED",
         "depth_ge5": hit, "share_diff": round(diff, 4), "fisher_p": p, "per_specimen": per,
         "max_depth": {a: max(r["depth"] for r in res if r["arm"] == a) for a in ("BASE", "NO_RECOMB")}}
    (HERE / "VERDICT.json").write_text(json.dumps(v, indent=1))
    print(json.dumps(v, indent=1))


if __name__ == "__main__":
    main()
