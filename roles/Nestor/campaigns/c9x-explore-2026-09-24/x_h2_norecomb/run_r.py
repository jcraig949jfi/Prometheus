"""X-H2-NORECOMB (EXPLORE, CAUSAL; child of X-H2-TERMINATION). Declared before running.

Observation: of 24 P-11-causal children of 7ae3's genome, 12 were OVERWRITTEN (identity to
their birth genome < 0.5) a median 3 epochs after birth, before they could donate. The cell's
point-mutation rate is LOW (0.002/byte), far too small; but it is on the RECOMBINATION atlas
axis, where `_mutate` splices the genome with a random living organism with probability 0.2
per call - and the pair tape calls `_mutate` on both halves every epoch. P(at least one splice
in 3 epochs) ~ 0.49, and a splice replaces about half the genome: the observed decay.

Single coordinate (CAUSAL): arm NO_RECOMB sets atlas_axis = NONE (no splice); everything else
is C9 arm B for 7ae3 (tier M, frozen donor genome, k = 1). Fresh seeds 9_980_000 + s, s < 16,
shared by both arms.
Readouts: max_causal_replication_depth; share depth >= 5; mean depth.
Classification: SIGNAL if NO_RECOMB's depth >= 5 share exceeds BASE by >= 0.25; CLEAN_NULL if
the difference < 0.10; WEAK_SIGNAL otherwise.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"


def job(args):
    s, arm_name = args
    import world
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    genome = bytes.fromhex(arm["kwargs"]["implant_hex"])
    cell = dict(arm["cell"], atlas_axis="NONE") if arm_name == "NO_RECOMB" else dict(arm["cell"])
    out = world.Runner(cell, 9_980_000 + s, tier=arm["tier"], implant="ACTUAL_GENOME",
                       implant_bytes=genome).run()
    return {"s": s, "arm": arm_name, "depth": out["max_causal_replication_depth"],
            "p11_events": out["p11_events"]}


def main():
    todo = [(s, a) for s in range(16) for a in ("BASE", "NO_RECOMB")]
    with mp.Pool(6, maxtasksperchild=2) as pool:
        res = pool.map(job, todo)
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    sh = {a: sum(r["depth"] >= 5 for r in res if r["arm"] == a) / 16 for a in ("BASE", "NO_RECOMB")}
    mean = {a: round(statistics.mean(r["depth"] for r in res if r["arm"] == a), 2) for a in ("BASE", "NO_RECOMB")}
    d = sh["NO_RECOMB"] - sh["BASE"]
    cls = "SIGNAL" if d >= 0.25 else ("CLEAN_NULL" if abs(d) < 0.10 else "WEAK_SIGNAL")
    out = {"classification": cls, "share_depth_ge5": sh, "mean_depth": mean,
           "max_depth": {a: max(r["depth"] for r in res if r["arm"] == a) for a in ("BASE", "NO_RECOMB")},
           "p11_events": {a: sum(r["p11_events"] for r in res if r["arm"] == a) for a in ("BASE", "NO_RECOMB")}}
    (HERE / "SUMMARY.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
