"""X-H2-7AE3 (EXPLORE, DOSE; child of C9 H2 WEAK_SIGNAL). Declared before running.

Observation: in C9, specimen 7ae3f9c1437c8000's implanted donor genome (arm B) reached causal
depth 6, 0, 1, 1, 12, 3, 15, 2, 0, 1, 2, 7, 1, 0, 0, 0 over 16 seeds (>= 5 in 4/16); random
bytes 0/16. Heavy-tailed: deep when it goes, absent otherwise - the signature of an
ESTABLISHMENT LOTTERY (the founder's first copies survive or not), not of a weak copier.

Prediction: if success is establishment-limited with per-founder probability p (~0.25),
k founders succeed with probability ~ 1 - (1 - p)^k (k = 4 -> ~0.68).
Single coordinate (DOSE): number of implanted founders k in {1, 4}; everything else is C9's
arm B (the specimen's cell, tier M, the frozen donor genome from the H2 panel). Fresh seeds
9_970_000 + s, s < 16, shared across k.
Readouts: max_causal_replication_depth (P-11); share of seeds with depth >= 5.
Classification: SIGNAL (establishment-limited) if the k = 4 share >= 0.5 and exceeds k = 1 by
>= 0.25; CLEAN_NULL if the difference < 0.10; WEAK_SIGNAL otherwise.
Also recorded (C9-D17 check): nothing - the A/C identity is documented in the addendum.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"


def job(args):
    s, k = args
    import world
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    genome = bytes.fromhex(arm["kwargs"]["implant_hex"])

    class KFounders(world.Runner):
        _extra = k - 1

        def _seed_genome(self):
            if self._extra > 0:
                self._extra -= 1
                return self._pad(genome)
            return super()._seed_genome()

    r = KFounders(arm["cell"], 9_970_000 + s, tier=arm["tier"], implant="ACTUAL_GENOME", implant_bytes=genome)
    out = r.run()
    return {"s": s, "k": k, "depth": out["max_causal_replication_depth"], "p11_events": out["p11_events"]}


def main():
    todo = [(s, k) for s in range(16) for k in (1, 4)]
    with mp.Pool(6, maxtasksperchild=2) as pool:
        res = pool.map(job, todo)
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    sh = {k: sum(r["depth"] >= 5 for r in res if r["k"] == k) / 16 for k in (1, 4)}
    d = sh[4] - sh[1]
    cls = "SIGNAL" if sh[4] >= 0.5 and d >= 0.25 else ("CLEAN_NULL" if abs(d) < 0.10 else "WEAK_SIGNAL")
    out = {"classification": cls, "share_depth_ge5": sh,
           "depths": {k: [r["depth"] for r in sorted(res, key=lambda r: r["s"]) if r["k"] == k] for k in (1, 4)}}
    (HERE / "SUMMARY.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
