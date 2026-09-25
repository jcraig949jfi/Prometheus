"""C-RUNAWAY (CONFIRM lane, fresh and frozen). Parents: X-H2-NORECOMB, C-NORECOMB, X-RUNAWAY.

Exploratory evidence (post-hoc endpoint, hence this fresh test): with the RECOMBINATION splice
off, 3 of 64 seeds of specimen 7ae3's implanted genome produced RUNAWAY causal heredity (P-11
depth 179, 126, 18; X-RUNAWAY: takeoff by epoch 20, 70-97% of the population descended through
P-11 copies, ~75 causal copies per epoch sustained for 1,800+ epochs); with the splice on, 0 of
64 (max depth 8).

NOTHING HERE MAY CHANGE AFTER COMMIT: specimen, seeds, arms, endpoint, rule, allocation.

Claim under test: in this pair-tape cell the world's recombination splice prevents runaway
causal heredity: turning it off (atlas_axis NONE, all else fixed) makes runaways occur, and
with it on they do not.
Sample: specimen 7ae3f9c1437c8000-s54765-tL-a0, C9 arm-B physics (its cell, tier M, frozen donor
genome, ONE founder). Fresh seeds 9_990_500 + s, s < 150, shared by both arms. One job per
worker process.
Arms: BASE (splice on, as frozen) and NO_RECOMB (atlas_axis NONE).
Endpoint: RUNAWAY = max_causal_replication_depth >= 20.
Rule: CONFIRMED iff #RUNAWAY(NO_RECOMB) >= 4 AND #RUNAWAY(BASE) == 0 AND one-sided Fisher exact
p < 0.01. Secondary: depth >= 5 counts, max depths.

    python run_crw.py [workers] -> RESULTS.json, VERDICT.json
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
N = 150


def job(args):
    s, arm_name = args
    import world
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    genome = bytes.fromhex(arm["kwargs"]["implant_hex"])
    cell = dict(arm["cell"], atlas_axis="NONE") if arm_name == "NO_RECOMB" else dict(arm["cell"])
    out = world.Runner(cell, 9_990_500 + s, tier=arm["tier"], implant="ACTUAL_GENOME",
                       implant_bytes=genome).run()
    rec = {"s": s, "arm": arm_name, "depth": out["max_causal_replication_depth"],
           "p11_events": out["p11_events"]}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%03d_%s.json" % (s, arm_name))).write_text(json.dumps(rec))
    return rec


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    todo = [(s, a) for s in range(N) for a in ("BASE", "NO_RECOMB") if "%03d_%s" % (s, a) not in done]
    with mp.Pool(workers, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, todo))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    run = {a: sum(r["depth"] >= 20 for r in res if r["arm"] == a) for a in ("BASE", "NO_RECOMB")}
    k0 = run["BASE"] + run["NO_RECOMB"]
    p = (sum(math.comb(N, x) * math.comb(N, k0 - x) for x in range(run["NO_RECOMB"], min(N, k0) + 1))
         / math.comb(2 * N, k0)) if k0 else 1.0
    v = {"verdict": "CONFIRMED" if run["NO_RECOMB"] >= 4 and run["BASE"] == 0 and p < 0.01 else "NOT_CONFIRMED",
         "n_per_arm": N, "runaways_depth_ge20": run, "fisher_p": p,
         "depth_ge5": {a: sum(r["depth"] >= 5 for r in res if r["arm"] == a) for a in ("BASE", "NO_RECOMB")},
         "max_depth": {a: max(r["depth"] for r in res if r["arm"] == a) for a in ("BASE", "NO_RECOMB")},
         "n_results": len(res)}
    (HERE / "VERDICT.json").write_text(json.dumps(v, indent=1))
    print(json.dumps(v, indent=1))


if __name__ == "__main__":
    main()
