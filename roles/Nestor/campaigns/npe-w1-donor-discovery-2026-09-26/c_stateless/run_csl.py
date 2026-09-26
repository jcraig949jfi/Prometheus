"""C-STATELESS (CONFIRM lane, fresh and frozen). Parent: X-DD-STATELESS (EXPLORE, SIGNAL).

NOTHING HERE MAY CHANGE AFTER COMMIT: cells, seeds, arms, endpoint, rule, allocation, controls.

Exploratory result (X-DD-STATELESS vs X-DD-STATE-RESET's DENSE arm, same seeds): in random populations with
one-byte block-copy encodings (dense VM) and ATOMIC write-back, starting every execution from the fresh
register state raised donor ESTABLISHMENT (runaway given a fresh-start-competent donor) from 23/60 = 0.38 to
56/62 = 0.90, with acquisition unchanged (60 vs 62 donor runs). Localization chain: X-DD-ESTABLISH (80% of
stalled donors never copy in-world) -> X-DD-NOCOPY-CONTEXT -> X-DD-STATE-RESET (reset on genome change:
CLEAN_NULL) -> X-DD-SELFSTATE (18/18 stalled donors copy at 0.0 from the state their own execution leaves).
Claim under test: donor establishment in this cell class is limited by register-state persistence across
executions (self-poisoning carried state); removing persistence makes establishment the common outcome.

Design: exactly the parent runners -- DENSE = X-DD-STATE-RESET's DENSE arm (run_sr.job), STATELESS =
X-DD-STATELESS (run_sl.job) -- with FRESH seeds 19_000_000 + s, s < 24, per cell (7ae3, ffa6) per arm;
96 runs. One job per process; the VM is set explicitly per job.
Endpoint: among runs with L2 (a COMPETENT genome at some 100-epoch checkpoint), ESTABLISHED = world causal
depth >= 20.
CONFIRMED iff each arm has >= 15 L2 runs AND establishment(STATELESS) - establishment(DENSE) >= 0.25 AND
one-sided Fisher exact p < 0.001 on (established, not established) x arm among L2 runs.
INSUFFICIENT if either arm has < 15 L2 runs. NOT_CONFIRMED otherwise.
Frozen controls (INVALID if any fails): X-DD-STATELESS's self-test (a non-fresh organism enters its
interaction fresh under STATELESS, not under the plain runner); X-DD-STATE-RESET's self-test is not needed
(no reset arm); every job records its arm.
Eligibility (before freezing): expected L2 runs per arm at the exploratory rate (~0.64) ~31 of 48;
P(L2 < 15) negligible. At the exploratory establishment rates (0.90 vs 0.38) with 31 L2 runs per arm the
Fisher p at the expected counts (28 vs 12) is 2e-5; simulated power of the full rule (2,000 draws) 0.89.
Secondary, never decisive: runaway per run, per cell.

    python run_csl.py -> VERDICT.json
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
N = 24
SEED0 = 19_000_000


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
    return [(arm, c, SEED0 + s) for s in range(N) for c in ("7ae3", "ffa6") for arm in ("DENSE", "STATELESS")]


def fisher(a, b, n1, n2):
    k0 = a + b
    return (sum(math.comb(n1, x) * math.comb(n2, k0 - x) for x in range(a, min(n1, k0) + 1))
            / math.comb(n1 + n2, k0)) if k0 else 1.0


def main():
    import run_sl
    ok, st = run_sl.selftest()
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
