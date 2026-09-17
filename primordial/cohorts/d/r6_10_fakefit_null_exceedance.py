"""D-R6-10 (ANOM-1789415790379-0): E2b's FAKEFIT cheat (real descent, fitness shuffled within each batch) beat the max
of 20 null worlds in 1 of 3 reps (6.5% vs 4.7%). A cheat with no fitness signal should never beat the null. How often
does it?

The anomaly's discriminator: 100 null worlds and 10 FAKEFIT reps, the exceedance rate with a CI. E2b's own functions
(primordial.qd.e2_run: evolve, read_events, branch_points with z_mode "cell", perturbed_world), E2b's parameters
(300 gens x batch 1024, k 50, z >= 2, hamming <= 8, held25 = perturbed_world(0.25, 11)). Null worlds
perturbed_world(1.0, 100 + i) for i in 0..99 (E2b's 20 are i 0..19). evolve's lineage archive is UNSEEDED (E2b's
harness), so reps are statistical draws, not replays. Fresh evolve seeds: FAKEFIT 4000..4009, honest 4100..4102,
filler 4200. Redis 6393 (lane D).

Rule (fixed before reading):
  per FAKEFIT rep: exceed100 = transfer_rate_held25 > max over the 100 nulls (a rep with no surviving founder has no
  rate and does not exceed); e = # of 10 reps exceeding.
  NULL_HOLDS   e == 0
  RARE         1 <= e <= 2
  CHEAT_LEAKS  e >= 3
  I1  honest reps: rate > max(100 nulls) in >= 2 of 3 (the null can be beaten by real selection); filler rep:
      founders_eligible == 0 (false parents fail the descent check); >= 8 of 10 FAKEFIT reps have a defined rate
      -- else INDETERMINATE.
Reported, not judged: Clopper-Pearson 95% CI of e / 10; the E2b-style count against the first 20 nulls only; each rep's
percentile of its held25 rate among its 100 null rates; per-rep evolve and branch-point CPU / wall.
"""
from __future__ import annotations

import math
import time

import numpy as np

from primordial.qd import e2_run as E

EXP = "D-R6-10-fakefit-null-exceedance"
PREDICATE_ID = EXP
ANOMALY = "1789415790379-0"
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
ARCHIVE_URL = "redis://127.0.0.1:6393/0"
GENS, BATCH, N_NULL = 300, 1024, 100
FAKE_SEEDS = tuple(range(4000, 4010))
HONEST_SEEDS = (4100, 4101, 4102)
FILLER_SEED = 4200


def worlds() -> dict:
    w = {"held25": E.perturbed_world(0.25, 11)}
    w.update({f"null{i}": E.perturbed_world(1.0, 100 + i) for i in range(N_NULL)})
    return w


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Exact binomial CI by bisection on the binomial tail (no scipy)."""
    def cdf(x, p):
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(x + 1))

    def solve(f):
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if f(mid):
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    lower = 0.0 if k == 0 else solve(lambda p: 1 - cdf(k - 1, p) < alpha / 2)
    upper = 1.0 if k == n else solve(lambda p: cdf(k, p) > alpha / 2)
    return lower, upper


def rep(r, mode: str, seed: int, ws: dict) -> dict:
    run = f"d-r6-10-{mode}-{seed}"
    t0, c0 = time.perf_counter(), time.process_time()
    ev = E.evolve(r, run, mode, GENS, BATCH, seed)
    recs = E.read_events(r, ev["arch"].skey)
    t1, c1 = time.perf_counter(), time.process_time()
    bp = E.branch_points(recs, GENS, E.K_PRIMARY, E.Z_PRIMARY, ws, z_mode="cell")
    ev["arch"].clear()
    nulls = [bp[f"transfer_rate_null{i}"] for i in range(N_NULL)]
    rate = bp["transfer_rate_held25"]
    defined = rate is not None
    return {"mode": mode, "seed": seed, "events": bp["events"], "real_edges": bp["real_edges"],
            "founders_eligible": bp["founders_eligible"], "founders_surviving": bp["founders_surviving"],
            "transfer_rate_held25": rate, "rate_defined": defined,
            "null_rates": nulls, "null_max_100": max(nulls) if defined else None, "null_max_20": max(nulls[:20]) if defined else None,
            "exceed100": bool(defined and rate > max(nulls)), "exceed20": bool(defined and rate > max(nulls[:20])),
            "percentile_in_nulls": float(np.mean([x < rate for x in nulls])) if defined else None,
            "evolve_wall_s": round(t1 - t0, 2), "evolve_cpu_s": round(c1 - c0, 2),
            "bp_wall_s": round(time.perf_counter() - t1, 2), "bp_cpu_s": round(time.process_time() - c1, 2)}


def decide(i1: bool, e: int) -> str:
    if not i1:
        return "INDETERMINATE"
    if e == 0:
        return "NULL_HOLDS"
    if e <= 2:
        return "RARE"
    return "CHEAT_LEAKS"


def job(ctx, status="record"):
    import redis
    t0 = time.perf_counter()
    r = redis.Redis.from_url(ARCHIVE_URL)
    ws = worlds()
    out = {"fakefit": [], "honest": [], "filler": []}
    plan = [("honest", s) for s in HONEST_SEEDS] + [("filler", FILLER_SEED)] + [("fakefit", s) for s in FAKE_SEEDS]
    for mode, seed in plan:
        x = rep(r, mode, seed, ws)
        out[mode].append(x)
        ctx.emit({"kind": "rep", "exp": EXP, "status": "control" if mode != "fakefit" else status,
                  "ts": round(time.time(), 3), **x})
    honest_ok = sum(x["exceed100"] for x in out["honest"]) >= 2
    filler_ok = all(x["founders_eligible"] == 0 for x in out["filler"])
    defined_ok = sum(x["rate_defined"] for x in out["fakefit"]) >= 8
    i1 = {"honest_beats_100_nulls_2of3": bool(honest_ok), "filler_founders_eligible_0": bool(filler_ok),
          "fakefit_rates_defined_8of10": bool(defined_ok)}
    e = sum(x["exceed100"] for x in out["fakefit"])
    e20 = sum(x["exceed20"] for x in out["fakefit"])
    lo, hi = clopper_pearson(e, len(out["fakefit"]))
    ctx.emit({"kind": "summary", "exp": EXP, "predicate_id": PREDICATE_ID, "anomaly": ANOMALY, "status": status,
              "ts": round(time.time(), 3), "gens": GENS, "batch": BATCH, "n_null": N_NULL, "k": E.K_PRIMARY,
              "z_min": E.Z_PRIMARY, "h_max": E.H_MAX, "z_mode": "cell",
              "checks": {"I1": i1}, "controls": {"honest": [{k: x[k] for k in ("seed", "transfer_rate_held25", "null_max_100", "exceed100")} for x in out["honest"]],
                                                 "filler": [{k: x[k] for k in ("seed", "founders_eligible")} for x in out["filler"]]},
              "fakefit_exceed100": e, "fakefit_reps": len(out["fakefit"]), "exceed_rate_ci95": [lo, hi],
              "reported_not_judged": {"e2b_style_exceed20": e20,
                                      "fakefit_percentiles": [x["percentile_in_nulls"] for x in out["fakefit"]],
                                      "fakefit_rates": [x["transfer_rate_held25"] for x in out["fakefit"]],
                                      "null_max_100_by_rep": [x["null_max_100"] for x in out["fakefit"]]},
              "decision": decide(all(i1.values()), e), "wall_s": round(time.perf_counter() - t0, 3)})
