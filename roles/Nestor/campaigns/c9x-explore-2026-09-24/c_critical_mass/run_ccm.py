"""C-CRITICAL-MASS (CONFIRM lane, fresh and frozen). Parent: X-CRITICAL-MASS (EXPLORE:
with the recombination splice off, 4 founders vs 1 gave depth >= 5 in 32/64 vs 8/64 and
runaways (depth >= 20) in 9/64 vs 0/64).

NOTHING HERE MAY CHANGE AFTER COMMIT: specimen, seeds, arms, endpoints, rule, allocation.

Claim under test: in 7ae3's cell with the splice off, pair-tape causal heredity is
establishment-limited - more founders establish deep causal lineages more often.
Sample: C9 arm-B physics for specimen 7ae3 (its cell with atlas_axis NONE, tier M, frozen donor
genome); founders k in {1, 4}; 80 fresh seeds 9_996_000 + s, shared across k. One job per process.
Primary endpoint: max_causal_replication_depth >= 5. Secondary: runaway (>= 20).
Rule: CONFIRMED iff share(k=4) - share(k=1) >= 0.20 on the primary AND one-sided Fisher p < 0.001.
Secondary runaway counts and Fisher p are reported, never decisive.

    python run_ccm.py -> RESULTS.json, VERDICT.json
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
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"
N = 80


def job(args):
    s, k = args
    import world
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    genome = bytes.fromhex(arm["kwargs"]["implant_hex"])

    class K(world.Runner):
        _extra = k - 1

        def _seed_genome(self):
            if self._extra > 0:
                self._extra -= 1
                return self._pad(genome)
            return super()._seed_genome()

    out = K(dict(arm["cell"], atlas_axis="NONE"), 9_996_000 + s, tier=arm["tier"],
            implant="ACTUAL_GENOME", implant_bytes=genome).run()
    r = {"s": s, "k": k, "depth": out["max_causal_replication_depth"]}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%03d_k%d.json" % (s, k))).write_text(json.dumps(r))
    return r


def fisher(a, b, n):
    k0 = a + b
    return (sum(math.comb(n, x) * math.comb(n, k0 - x) for x in range(a, min(n, k0) + 1))
            / math.comb(2 * n, k0)) if k0 else 1.0


def main():
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    todo = [(s, k) for s in range(N) for k in (1, 4) if "%03d_k%d" % (s, k) not in done]
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, todo))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    d5 = {k: sum(r["depth"] >= 5 for r in res if r["k"] == k) for k in (1, 4)}
    rw = {k: sum(r["depth"] >= 20 for r in res if r["k"] == k) for k in (1, 4)}
    p = fisher(d5[4], d5[1], N)
    v = {"verdict": "CONFIRMED" if (d5[4] - d5[1]) / N >= 0.20 and p < 0.001 else "NOT_CONFIRMED",
         "n_per_k": N, "depth_ge5": d5, "share_diff": round((d5[4] - d5[1]) / N, 4), "fisher_p": p,
         "secondary_runaways": rw, "secondary_runaway_fisher_p": fisher(rw[4], rw[1], N),
         "max_depth": {k: max(r["depth"] for r in res if r["k"] == k) for k in (1, 4)}, "n_results": len(res)}
    (HERE / "VERDICT.json").write_text(json.dumps(v, indent=1))
    print(json.dumps(v, indent=1))


if __name__ == "__main__":
    main()
