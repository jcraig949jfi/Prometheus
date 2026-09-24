"""X-CRITICAL-MASS (EXPLORE, DOSE; child of X-SUFFICIENCY). Declared before running.

Runaways (C-RUNAWAY: 7/150 with the splice off) are not separated from stalls by copier
quality (X-SUFFICIENCY: genome-sufficient copies in both), but by early copy SCALE (thousands
of P-11 copies by epoch 200 vs <= 31). Hypothesis: runaway is a critical-mass phenomenon - it
needs enough copiers copying early before overwriting erodes them.

Single coordinate (DOSE): founders k in {1, 4} (implanted 7ae3 donor genome, splice OFF, C9
arm-B physics, tier M). 64 fresh seeds 9_993_000 + s, shared across k. One job per process.
Endpoint: runaway = P-11 depth >= 20.
Prediction (declared): if critical mass, runaway rate at k=4 >= 3x the k=1 rate (and >= 15%).
Classification: SIGNAL if runaways(k=4) >= 3 * runaways(k=1) and >= 10/64; CLEAN_NULL if
|difference| <= 2; WEAK_SIGNAL otherwise.
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

    class K(world.Runner):
        _extra = k - 1

        def _seed_genome(self):
            if self._extra > 0:
                self._extra -= 1
                return self._pad(genome)
            return super()._seed_genome()

    out = K(dict(arm["cell"], atlas_axis="NONE"), 9_993_000 + s, tier=arm["tier"],
            implant="ACTUAL_GENOME", implant_bytes=genome).run()
    rec = {"s": s, "k": k, "depth": out["max_causal_replication_depth"], "p11_events": out["p11_events"]}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%03d_k%d.json" % (s, k))).write_text(json.dumps(rec))
    return rec


def main():
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    todo = [(s, k) for s in range(64) for k in (1, 4) if "%03d_k%d" % (s, k) not in done]
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, todo))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    ra = {k: sum(r["depth"] >= 20 for r in res if r["k"] == k) for k in (1, 4)}
    cls = ("SIGNAL" if ra[4] >= 3 * max(1, ra[1]) and ra[4] >= 10 else
           "CLEAN_NULL" if abs(ra[4] - ra[1]) <= 2 else "WEAK_SIGNAL")
    out = {"classification": cls, "runaways": ra, "n_per_k": 64,
           "depth_ge5": {k: sum(r["depth"] >= 5 for r in res if r["k"] == k) for k in (1, 4)},
           "max_depth": {k: max(r["depth"] for r in res if r["k"] == k) for k in (1, 4)}}
    (HERE / "SUMMARY.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
