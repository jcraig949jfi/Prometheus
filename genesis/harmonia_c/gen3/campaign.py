"""Gen-3 campaign runner: E1 (arena admissibility) and E2 (six-arm head-to-head).

Results land in results/*.json.  Nothing here may alter the arena -- it is locked.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import time

import numpy as np

import arena
import arms as A
from arena import OUT_LO, World, fmt, run

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(RESULTS, exist_ok=True)

SEEDS = [20260901 + i for i in range(12)]        # frozen: 12 seeds, no optional stopping
WORLD_NAMES = ["W1_PIPELINE", "W2_DECEPTIVE", "W3_INTERFERENCE"]


# ------------------------------------------------------------------------ statistics

def clopper_pearson(k, n, alpha=0.05):
    """Exact binomial 95% CI.  No naked point estimates anywhere in this campaign."""
    if n == 0:
        return (0.0, 1.0)
    lo = 0.0 if k == 0 else _beta_ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else _beta_ppf(1 - alpha / 2, k + 1, n - k)
    return (lo, hi)


def _betainc(a, b, x):
    """Regularised incomplete beta I_x(a,b) via Lentz's continued fraction.

    Replaces a direct binomial-tail sum, which overflowed to OverflowError once n ran
    into the thousands (retention edges).  Stable in log space for every n used here.
    """
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(a * math.log(x) + b * math.log(1 - x) - lbeta) / a
    if x > (a + 1.0) / (a + b + 2.0):
        return 1.0 - _betainc(b, a, 1.0 - x)
    f, c, d = 1.0, 1.0, 0.0
    for i in range(0, 300):
        m = i // 2
        if i == 0:
            num = 1.0
        elif i % 2 == 0:
            num = (m * (b - m) * x) / ((a + 2.0 * m - 1.0) * (a + 2.0 * m))
        else:
            num = -((a + m) * (a + b + m) * x) / ((a + 2.0 * m) * (a + 2.0 * m + 1.0))
        d = 1.0 + num * d
        if abs(d) < 1e-30:
            d = 1e-30
        d = 1.0 / d
        c = 1.0 + num / c
        if abs(c) < 1e-30:
            c = 1e-30
        f *= c * d
        if abs(1.0 - c * d) < 1e-12:
            break
    return front * (f - 1.0)


def _beta_ppf(p, a, b, iters=200):
    lo, hi = 0.0, 1.0
    for _ in range(iters):
        mid = (lo + hi) / 2
        if _betainc(a, b, mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def fisher_exact(a, b, c, d):
    """Two-sided Fisher exact p for the 2x2 table [[a,b],[c,d]]."""
    n = a + b + c + d

    def p_tab(a_):
        b_, c_, d_ = (a + b) - a_, (a + c) - a_, n - (a + b) - (a + c) + a_
        if min(b_, c_, d_) < 0:
            return 0.0
        return (math.comb(a + b, a_) * math.comb(c + d, c_)) / math.comb(n, a + c)

    p_obs = p_tab(a)
    lo = max(0, (a + c) - (c + d))
    hi = min(a + b, a + c)
    return min(1.0, sum(p_tab(x) for x in range(lo, hi + 1) if p_tab(x) <= p_obs + 1e-12))


# ------------------------------------------------------------------------------- E1

def e1():
    """Arena admissibility, leakage controls, chance floors.  Gates K1 and K2."""
    out = {"experiment": "E1", "kills": {}, "worlds": {}, "controls": {}}

    # --- chance floors, measured not assumed -------------------------------------
    for wn in WORLD_NAMES:
        w = World(wn)
        T = w.targets(w.heldout)
        floors = []
        for k in range(w.n_slots):
            counts = np.bincount(T[k], minlength=256)
            floors.append(float(counts.max()) / T.shape[1])
        # probability that a RANDOM program holds each capability
        rng = random.Random(4242)
        hits = [0] * w.n_slots
        N_RAND = 20000
        for _ in range(N_RAND):
            p = A.rand_prog(rng)
            for k in w.capset(p, "heldout"):
                hits[k] += 1
        out["worlds"][wn] = dict(
            note=w.note, goal=sorted(w.goal), boot_slots=list(w.boot_slots),
            majority_class_rate=[round(f, 4) for f in floors],
            random_program_capability_rate=[h / N_RAND for h in hits],
            n_random_programs=N_RAND,
        )

    # --- K2: leakage controls ----------------------------------------------------
    leaks = []
    for wn in WORLD_NAMES:
        w = World(wn)
        # (a) constant-output programs
        for c in range(16):
            prog = [(10, OUT_LO + k, c) for k in range(w.n_slots)]
            if w.capset(prog, "heldout"):
                leaks.append(dict(world=wn, kind="constant", const=(c * 17) & 0xFF))
        # (b) input-ignoring programs (scratch only, never reads R0/R1)
        rng = random.Random(99)
        for _ in range(4000):
            prog = [(rng.randrange(arena.N_OPS), rng.randrange(2, 8), rng.randrange(2, 8))
                    for _ in range(rng.randint(4, 16))]
            if w.capset(prog, "heldout"):
                leaks.append(dict(world=wn, kind="input_ignoring", prog=fmt(prog)))
                break
        # (c) empty program
        if w.capset([], "heldout"):
            leaks.append(dict(world=wn, kind="empty"))
    out["controls"]["leakage_violations"] = leaks
    out["kills"]["K2_leakage"] = "PASS" if not leaks else "FIRED"

    # --- K1: is the arena too easy for random search? ----------------------------
    w1_random_goal = 0
    for s in SEEDS:
        su = A.Run("F_RANDOM", "W1_PIPELINE", s).go().summary()
        w1_random_goal += su["goal_met_arm_phase"]
    rate = w1_random_goal / len(SEEDS)
    out["controls"]["F_RANDOM_W1_goal_rate"] = rate
    out["kills"]["K1_arena_too_easy"] = "FIRED" if rate >= 0.20 else "PASS"

    # --- A5 blind-spot re-check: ungated HELDOUT on every run's best program ------
    mismatches = 0
    checked = 0
    for wn in WORLD_NAMES:
        for arm in A.ARMS:
            r = A.Run(arm, wn, SEEDS[0]).go()
            best = r.best[2]
            if best is None:
                continue
            expressed, _ = A.expand(best, [v[1] for v in r.archive.values()])
            ungated = r.world.capset(expressed, "heldout")
            gated = r.world.eval_train(expressed)[2]
            checked += 1
            if ungated and not gated:
                mismatches += 1
    out["controls"]["A5_ungated_recheck"] = dict(checked=checked, mismatches=mismatches)

    # --- determinism / replay ----------------------------------------------------
    a = A.Run("E_COMP_REF", "W2_DECEPTIVE", SEEDS[0]).go().summary()
    b = A.Run("E_COMP_REF", "W2_DECEPTIVE", SEEDS[0]).go().summary()
    out["controls"]["replay_identical"] = (a == b)

    # --- bootstrap parity across arms -------------------------------------------
    parity = {}
    for wn in WORLD_NAMES:
        sigs = set()
        for arm in A.ARMS:
            r = A.Run(arm, wn, SEEDS[0], evals=A.BOOTSTRAP).go()
            sigs.add(json.dumps(sorted(sorted(k) for k in r.archive.keys())))
        parity[wn] = (len(sigs) == 1)
    out["controls"]["bootstrap_identical_across_arms"] = parity

    with open(os.path.join(RESULTS, "e1.json"), "w") as f:
        json.dump(out, f, indent=1)
    return out


# ------------------------------------------------------------------------------- E2

def e2():
    """Six-arm head-to-head.  Primary: P(goal acquisition in the ARM PHASE | budget)."""
    rows = []
    t0 = time.time()
    for wn in WORLD_NAMES:
        for arm in A.ARMS:
            for s in SEEDS:
                r = A.Run(arm, wn, s).go()
                su = r.summary()
                su["distinct_signatures_crossing"] = len(
                    {r.world.signature(A.expand(r.genomes[c[0]],
                                                [v[1] for v in r.archive.values()])[0])
                     for c in r.crossings if c[0] in r.genomes})
                rows.append(su)
            print("  %-16s %-11s done (%.0fs)" % (wn, arm, time.time() - t0), flush=True)

    agg = {}
    for wn in WORLD_NAMES:
        agg[wn] = {}
        for arm in A.ARMS:
            rs = [r for r in rows if r["world"] == wn and r["arm"] == arm]
            k = sum(r["goal_met_arm_phase"] for r in rs)
            n = len(rs)
            lo, hi = clopper_pearson(k, n)
            firsts = [r["first_cross_eval"].get(str(sorted(World(wn).goal)[-1]))
                      for r in rs]
            firsts = [f for f in firsts if f]
            agg[wn][arm] = dict(
                k=k, n=n, rate=k / n, ci95=[round(lo, 4), round(hi, 4)],
                mean_radius=round(float(np.mean([r["mean_radius"] for r in rs])), 3),
                mean_vm_instructions=int(np.mean([r["vm_instructions"] for r in rs])),
                mean_archive=round(float(np.mean([r["archive_size"] for r in rs])), 2),
                fallback_rate=round(float(np.mean([r["fallbacks"] for r in rs])) / 20000, 4),
                truncations=int(np.mean([r["truncations"] for r in rs])),
                median_evals_to_goal=(int(np.median(firsts)) if firsts else None),
                bootstrap_contaminated=sum(r["goal_met_at_bootstrap"] for r in rs),
            )

    # every arm vs A_LOCAL, and vs the random control
    tests = {}
    for wn in WORLD_NAMES:
        tests[wn] = {}
        for arm in A.ARMS:
            for ref in ("A_LOCAL", "F_RANDOM"):
                if arm == ref:
                    continue
                a_ = agg[wn][arm]["k"]; b_ = agg[wn][arm]["n"] - a_
                c_ = agg[wn][ref]["k"]; d_ = agg[wn][ref]["n"] - c_
                tests[wn]["%s_vs_%s" % (arm, ref)] = round(fisher_exact(a_, b_, c_, d_), 5)

    out = dict(experiment="E2", seeds=SEEDS, rows=rows, aggregate=agg, fisher=tests,
               kills=dict(K3_no_acquisition="FIRED" if all(
                   agg[w][a]["k"] == 0 for w in WORLD_NAMES for a in A.ARMS) else "PASS"))
    with open(os.path.join(RESULTS, "e2.json"), "w") as f:
        json.dump(out, f, indent=1)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("which", choices=["e1", "e2"])
    a = ap.parse_args()
    t = time.time()
    res = {"e1": e1, "e2": e2}[a.which]()
    print(json.dumps(res.get("kills", {}), indent=1))
    print("%s done in %.0fs" % (a.which, time.time() - t))
