"""X-ROOT-AUDIT (EXPLORE, MEASUREMENT / endpoint audit; child of X-SWAP-ORIGIN). Declared before running.

X-SWAP-ORIGIN: in 7ae3's own cell under ATOMIC write-back the world's max causal replication depth
far exceeds the implanted founder's own causal-lineage depth in 2 of 3 runaways (382 vs 71, 386 vs
27), and the foreign 9cba/e160 runaways are not founder-rooted at all. The runaway endpoint of
C-RUNAWAY, C-CRITICAL-MASS and C-ATOMIC is WORLD-level (any lineage), so those claims speak of the
cell containing the implant, not of the implant's lineage. Question: does C-ATOMIC C1 (46/80 vs
1/80) survive on a FOUNDER-ROOTED endpoint?

Sample: C-ATOMIC C1's recorded runs (7ae3, seeds 12_000_000 + s, s < 80, both arms), read-only from
c_atomic/results. founder_depth <= world depth by construction (the founder set is a subset of the
world's causal graph), so only runs with recorded world depth >= 20 can be founder-rooted runaways;
exactly those runs (46 ATOMIC, 1 BASE) are replayed here, in this directory, with the founder
causal-lineage tracker of X-SWAP-ORIGIN (ATOMIC runner = X-DONOR-SWAP's, the C-ATOMIC logic incl.
A1; BASE = world.Runner). All other runs count as not founder-rooted.
Endpoint: founder-rooted runaway = founder_depth >= 20.
INVALID if any replay's world depth differs from the recorded C-ATOMIC depth, or any founder_depth
exceeds its world depth.
Classification (C1's own thresholds on the new endpoint, 80 per arm): SIGNAL if share(ATOMIC) -
share(BASE) >= 0.25 AND one-sided Fisher p < 0.001; CLEAN_NULL if the share difference < 0.10;
WEAK_SIGNAL otherwise. Exploratory: this audits, it cannot re-adjudicate the frozen verdict.
"""
from __future__ import annotations

import json
import math
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
CAT = HERE.parent / "c_atomic" / "results"
sys.path.insert(0, str(HERE.parent / "x_swap_origin"))
sys.path.insert(0, str(HERE.parent / "x_donor_swap"))
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"
N = 80


def recorded():
    out = {}
    for s in range(N):
        for arm in ("ATOMIC", "BASE"):
            out[(12_000_000 + s, arm)] = json.loads((CAT / ("%s_%d_%s.json" % (SPEC[:16], 12_000_000 + s, arm))).read_text())["depth"]
    return out


def job(args):
    seed, armname = args
    import world
    import run_ds
    import run_so
    arm = run_ds.cells()[SPEC]
    base = run_ds.runner_cls(world) if armname == "ATOMIC" else world.Runner
    r = run_so.tracked(world, base)(dict(arm["cell"], atlas_axis="NONE"), seed, tier=arm["tier"],
                                    implant="ACTUAL_GENOME", implant_bytes=run_ds.donor_genome())
    out = r.run()
    rec = {"seed": seed, "arm": armname, "depth": out["max_causal_replication_depth"],
           "founder_depth": r.fdepth, "founder_causal_births": r.fbirths}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%d_%s.json" % (seed, armname))).write_text(json.dumps(rec))
    return rec


def fisher(a, b, n):
    k0 = a + b
    return (sum(math.comb(n, x) * math.comb(n, k0 - x) for x in range(a, min(n, k0) + 1))
            / math.comb(2 * n, k0)) if k0 else 1.0


def main():
    rec = recorded()
    todo = sorted(k for k, d in rec.items() if d >= 20)
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in todo if "%d_%s" % t not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    mism = [(r["seed"], r["arm"]) for r in res if r["depth"] != rec[(r["seed"], r["arm"])]]
    over = [(r["seed"], r["arm"]) for r in res if r["founder_depth"] > r["depth"]]
    fr = {a: sum(r["founder_depth"] >= 20 for r in res if r["arm"] == a) for a in ("ATOMIC", "BASE")}
    diff = (fr["ATOMIC"] - fr["BASE"]) / N
    p = fisher(fr["ATOMIC"], fr["BASE"], N)
    cls = ("INVALID" if mism or over or len(res) != len(todo) else
           "SIGNAL" if diff >= 0.25 and p < 0.001 else "CLEAN_NULL" if diff < 0.10 else "WEAK_SIGNAL")
    summ = {"classification": cls, "replayed": len(res), "replay_mismatches": mism, "founder_over_world": over,
            "world_runaways": {a: sum(d >= 20 for (s, x), d in rec.items() if x == a) for a in ("ATOMIC", "BASE")},
            "founder_rooted_runaways": fr, "n_per_arm": N, "share_diff": diff, "fisher_p": p,
            "runs": sorted(({k: r[k] for k in ("seed", "arm", "depth", "founder_depth", "founder_causal_births")} for r in res),
                           key=lambda x: (x["arm"], x["seed"]))}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps({k: v for k, v in summ.items() if k != "runs"}, indent=1))


if __name__ == "__main__":
    main()
