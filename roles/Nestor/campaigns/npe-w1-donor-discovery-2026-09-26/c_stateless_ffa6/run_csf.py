"""C-STATELESS-FFA6 (CONFIRM lane, fresh and frozen). Parent: C-STATELESS (CONFIRM, NOT_CONFIRMED) and
X-DD-STATELESS (EXPLORE, SIGNAL). Theory-aware by date.

NOTHING HERE MAY CHANGE AFTER COMMIT: cell, seeds, arms, endpoint, rule, allocation, controls.

C-STATELESS (frozen d4f7ba271 + A1) did NOT confirm: establishment DENSE 11/24 = 0.46 vs STATELESS 23/29 = 0.79
(diff 0.33 >= 0.25, but Fisher p = 0.012 > 0.001). The effect concentrated entirely in the ffa6 cell (8/16 ->
19/21) and was absent in 7ae3 (3/8 -> 4/8); in the exploratory X-DD-STATELESS both cells moved (7ae3 0.32 ->
0.74, ffa6 0.43 -> 0.98). The restriction to ffa6 is POST HOC, chosen from C-STATELESS's own data; it is
declared here and tested on fresh seeds.
Claim under test: in the ffa6 cell (Z8_SLOTTED, NICHES_HIGH_MIG; dense VM, ATOMIC, random populations) donor
establishment is limited by register-state persistence across executions.

Design: exactly C-STATELESS's jobs (run_sr.job DENSE arm, run_sl.job STATELESS arm) restricted to cell ffa6,
FRESH seeds 20_000_000 + s, s < 48, per arm; 96 runs. Endpoint, rule and controls exactly as C-STATELESS:
among L2 runs, ESTABLISHED = world causal depth >= 20; CONFIRMED iff each arm has >= 15 L2 runs AND
establishment difference >= 0.25 AND one-sided Fisher p < 0.001; INSUFFICIENT if < 15 L2 runs in an arm.
Results directories are created before the pool (C-STATELESS amendment A1 carried in).
Eligibility (before freezing): ffa6 L2 rate ~0.75 -> ~36 L2 runs per arm; at the C-STATELESS ffa6 rates
(0.50 vs 0.90) the expected counts (18 vs 32 of 36) give Fisher p = 3e-4.

    python run_csf.py -> VERDICT.json
"""
from __future__ import annotations

import json
import math
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
for p in (HERE.parent / "x_dd_stateless", HERE.parent / "x_dd_state_reset", HERE.parent / "x_dd_dense_copy",
          HERE.parent / "x_donor_discovery", HERE.parent.parent / "c9x-explore-2026-09-24" / "x_donor_swap",
          HERE.parent.parent / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))
N = 48
SEED0 = 20_000_000


def job(args):
    arm, cell, seed = args
    if arm == "STATELESS":
        import run_sl
        run_sl.HERE = HERE / "stateless"
        return run_sl.job((cell, seed))
    import run_sr
    run_sr.HERE = HERE / "dense"
    return run_sr.job(("DENSE", cell, seed))


def jobs():
    return [(arm, c, SEED0 + s) for s in range(N) for c in ("ffa6",) for arm in ("DENSE", "STATELESS")]


def fisher(a, b, n1, n2):
    k0 = a + b
    return (sum(math.comb(n1, x) * math.comb(n2, k0 - x) for x in range(a, min(n1, k0) + 1))
            / math.comb(n1 + n2, k0)) if k0 else 1.0


def main():
    import run_sl
    ok, st = run_sl.selftest()
    for sub in ("stateless", "dense"):            # AMENDMENT A1 (infrastructure): the job functions create
        (HERE / sub / "results").mkdir(parents=True, exist_ok=True)   # only the leaf directory
    done = set()
    for sub, arm in (("stateless", "STATELESS"), ("dense", "DENSE")):
        d = HERE / sub / "results"
        if d.exists():
            for p in d.glob("*.json"):
                r = json.loads(p.read_text())
                done.add((arm, r["cell"], r["seed"]))
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in jobs() if t not in done]))
    res = [json.loads(p.read_text()) for sub in ("stateless", "dense") for p in sorted((HERE / sub / "results").glob("*.json"))]
    assert len(res) == len(jobs()), len(res)
    arms_ok = all(r["arm"] in ("STATELESS", "DENSE") for r in res)
    by = {a: [r for r in res if r["arm"] == a] for a in ("DENSE", "STATELESS")}
    l2 = {a: [r for r in by[a] if any(c["L2"] > 0 for c in r["checkpoints"])] for a in by}
    est = {a: sum(r["depth"] >= 20 for r in l2[a]) for a in by}
    rate = {a: (est[a] / len(l2[a]) if l2[a] else None) for a in by}
    if not (ok and arms_ok):
        verdict = "INVALID"
    elif len(l2["DENSE"]) < 15 or len(l2["STATELESS"]) < 15:
        verdict = "INSUFFICIENT"
    else:
        p = fisher(est["STATELESS"], est["DENSE"], len(l2["STATELESS"]), len(l2["DENSE"]))
        verdict = "CONFIRMED" if rate["STATELESS"] - rate["DENSE"] >= 0.25 and p < 0.001 else "NOT_CONFIRMED"
    p = fisher(est["STATELESS"], est["DENSE"], len(l2["STATELESS"]), len(l2["DENSE"])) if all(l2.values()) else None
    v = {"verdict": verdict, "selftest": st, "L2_runs": {a: len(l2[a]) for a in by}, "established": est,
         "establishment_rate": {a: (round(x, 4) if x is not None else None) for a, x in rate.items()},
         "fisher_p": p, "secondary": {a: {"runaway_all_runs": sum(r["depth"] >= 20 for r in by[a]),
                                          "per_cell_L2_est": {c: [sum(1 for r in l2[a] if r["cell"] == c),
                                                                  sum(r["depth"] >= 20 for r in l2[a] if r["cell"] == c)]
                                                              for c in ("7ae3", "ffa6")}} for a in by}}
    (HERE / "VERDICT.json").write_text(json.dumps(v, indent=1))
    print(json.dumps(v, indent=1))


if __name__ == "__main__":
    main()
