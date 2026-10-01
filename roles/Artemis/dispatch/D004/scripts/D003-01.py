#!/usr/bin/env python3
"""D003-01 / FR-003 -- known-answer calibration of the Crius accessibility rulers on HIFF.

NOT RUN by the author of this file (the worker could not execute code). No output is claimed.

Purpose: the cheapest second-substrate measurement that the repository itself names
(roles/Artemis/challenge/PRIOR_ART_PRESSURE.md:754-771 @b960d1a42, "P16 HIFF -> KNOWN-ANSWER
WORLD"; roles/Artemis/backlog/prior_art/PA_accessibility_landscape.md:453 @b960d1a42).
HIFF (Watson, Hornby, Pollack 1998) is solvable by recombination and not by point-mutation
hill-climbing, so the right answer is known in advance.

Rulers, as defined in docs/essays/2026-09-24-accessibility-frontier.md:149-158 @391395aac:
  foothold density  = fraction of incomplete states on the best construction path whose paired
                      credit exceeds the neutral-edit background
  d_flat            = longest run of consecutive links with no positive credit on that path
  rho               = V / (V + d_flat * c)
HIFF fitness is deterministic, so "paired re-evaluation" is exact; the neutral-edit background
is the distribution of deltas of random edits that do not touch the path (reported, and used as
the threshold: a step counts as a foothold only if its delta > max(0, q95 of background)).

Operators (two arms, Crius defaults mu = 8, lambda = 24):
  PM : point mutation, 1/n per bit
  XO : two-point crossover between two parents, then point mutation
For the XO arm the "edit" used to build the path is a block transplant from a population member
(crossover's natural move); for PM it is a single bit flip.

DECISION RULE (from P16):
  A ruler PASSES iff
   (1) it ranks the arms correctly: foothold density(XO) > foothold density(PM),
       d_flat(XO) < d_flat(PM), rho(XO) > rho(PM), AND discovery rate(XO) > discovery rate(PM); and
   (2) per run, the ruler measured at generation G0 predicts time-to-optimum at least as well as
       current best fitness at G0 (Herakles K7 bar): |Spearman(ruler, T)| - |Spearman(fitness, T)|
       has a bootstrap 95% CI whose lower bound is >= 0 (strict version: > 0).
  Failing (1) disqualifies the ruler outright; passing (1) but failing (2) means "descriptive,
  not predictive" (the same status R-29 reports for a content-addressed arrival measure in Ares).
Stdlib only.
"""
import random
import statistics
import json
import sys

N_BITS = 32          # 2^5; also run 16 and 64 (P16 says k in {4,5,6})
MU, LAM = 8, 24
GENS = 3000
SEEDS = 30
G0 = 50              # generation at which rulers and fitness are read as predictors
BOOT = 2000


def hiff(bits):
    """Standard HIFF: recursive; a block scores len(block) if uniform, plus its children."""
    def rec(b):
        if len(b) == 1:
            return 1
        h = len(b) // 2
        s = rec(b[:h]) + rec(b[h:])
        if all(x == b[0] for x in b):
            s += len(b)
        return s
    return rec(tuple(bits))


def optimum_value(n):
    return hiff([1] * n)


def nearest_optimum(bits):
    z = sum(1 for x in bits if x == 0)
    return [0] * len(bits) if z * 2 > len(bits) else [1] * len(bits)


def path_pm(bits):
    """Best single-flip construction path to the nearest optimum: at each step flip the
    remaining mismatched bit that gives the largest delta (ties by index)."""
    target = nearest_optimum(bits)
    cur = list(bits)
    steps = []
    while cur != target:
        cands = [i for i in range(len(cur)) if cur[i] != target[i]]
        best = None
        for i in cands:
            nxt = cur[:]
            nxt[i] = target[i]
            d = hiff(nxt) - hiff(cur)
            if best is None or d > best[0]:
                best = (d, i, nxt)
        steps.append(best[0])
        cur = best[2]
    return steps


def path_xo(bits, pop):
    """Best block-transplant path: at each step copy the aligned block (any power-of-two size,
    any aligned position) from any population member (or the target, as the last resort that
    represents one full crossover with an optimal donor being absent -> counted as a mutation
    step of block length). Greedy on delta."""
    target = nearest_optimum(bits)
    cur = list(bits)
    steps = []
    n = len(cur)
    guard = 0
    while cur != target and guard < 4 * n:
        guard += 1
        best = None
        size = 1
        while size <= n:
            for start in range(0, n, size):
                for donor in pop:
                    blk = donor[start:start + size]
                    if blk != target[start:start + size]:
                        continue
                    nxt = cur[:start] + blk + cur[start + size:]
                    if nxt == cur:
                        continue
                    d = hiff(nxt) - hiff(cur)
                    if best is None or d > best[0]:
                        best = (d, nxt)
            size *= 2
        if best is None:  # no donor carries a useful block: fall back to single flips
            return steps + path_pm(cur)
        steps.append(best[0])
        cur = best[1]
    return steps


def background(bits, rng, k=64):
    """Neutral-edit background: deltas of random single flips (all positions)."""
    base = hiff(bits)
    out = []
    for _ in range(k):
        i = rng.randrange(len(bits))
        nxt = list(bits)
        nxt[i] ^= 1
        out.append(hiff(nxt) - base)
    return out


def rulers(steps, bg, v_gain, c):
    thr = max(0.0, sorted(bg)[int(0.95 * (len(bg) - 1))])
    inter = steps[:-1] if len(steps) > 1 else steps  # incomplete states only
    fd = (sum(1 for d in inter if d > thr) / len(inter)) if inter else 1.0
    run = best = 0
    for d in steps:
        run = run + 1 if d <= thr else 0
        best = max(best, run)
    rho = v_gain / (v_gain + best * c) if (v_gain + best * c) > 0 else float("nan")
    return {"foothold_density": fd, "d_flat": best, "rho": rho, "threshold": thr, "n_steps": len(steps)}


def evolve(arm, seed):
    rng = random.Random(seed)
    n = N_BITS
    pop = [[rng.randrange(2) for _ in range(n)] for _ in range(MU)]
    opt = optimum_value(n)
    snap = None
    t_hit = None
    for g in range(GENS):
        kids = []
        for _ in range(LAM):
            p = rng.choice(pop)[:]
            if arm == "XO":
                q = rng.choice(pop)
                a, b = sorted(rng.sample(range(n + 1), 2))
                p = p[:a] + q[a:b] + p[b:]
            for i in range(n):
                if rng.random() < 1.0 / n:
                    p[i] ^= 1
            kids.append(p)
        pool = pop + kids
        pool.sort(key=hiff, reverse=True)
        pop = [x[:] for x in pool[:MU]]
        if g == G0:
            snap = ([x[:] for x in pop], hiff(pop[0]))
        if t_hit is None and hiff(pop[0]) == opt:
            t_hit = g
            if snap is not None:
                break
    if snap is None:
        snap = ([x[:] for x in pop], hiff(pop[0]))
    return snap, t_hit


def spearman(x, y):
    def rank(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for k in range(i, j + 1):
                r[o[k]] = (i + j) / 2.0
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    if len(set(rx)) < 2 or len(set(ry)) < 2:
        return float("nan")
    return statistics.correlation(rx, ry)


def main():
    rng = random.Random(12345)
    n = N_BITS
    c = n / LAM  # generations to propose one specific flip at rate 1/n with lambda children (a choice; state it)
    out = {}
    for arm in ("PM", "XO"):
        rows = []
        for s in range(SEEDS):
            (pop, fit), t = evolve(arm, 1000 * s + (0 if arm == "PM" else 1))
            champ = pop[0]
            steps = path_pm(champ) if arm == "PM" else path_xo(champ, pop)
            v_gain = optimum_value(n) - fit
            r = rulers(steps, background(champ, rng), v_gain, c)
            rows.append({"seed": s, "fit_G0": fit, "t_hit": t, **r})
        T = [r["t_hit"] if r["t_hit"] is not None else GENS * 2 for r in rows]  # censored -> 2*GENS
        k7 = {}
        for key in ("foothold_density", "rho", "d_flat"):
            xs = [r[key] for r in rows]
            fs = [r["fit_G0"] for r in rows]
            diffs = []
            for _ in range(BOOT):
                idx = [rng.randrange(len(rows)) for _ in rows]
                a = spearman([xs[i] for i in idx], [T[i] for i in idx])
                b = spearman([fs[i] for i in idx], [T[i] for i in idx])
                if a == a and b == b:
                    diffs.append(abs(a) - abs(b))
            diffs.sort()
            k7[key] = {"rho_ruler_T": spearman(xs, T), "rho_fit_T": spearman(fs, T),
                       "boot_ci95_absdiff": [diffs[int(0.025 * len(diffs))], diffs[int(0.975 * len(diffs))]] if diffs else None}
        out[arm] = {"discovery_rate": sum(1 for r in rows if r["t_hit"] is not None) / SEEDS,
                    "mean_foothold_density": statistics.mean(r["foothold_density"] for r in rows),
                    "mean_d_flat": statistics.mean(r["d_flat"] for r in rows),
                    "mean_rho": statistics.mean(r["rho"] for r in rows),
                    "k7": k7, "rows": rows}
    ok1 = (out["XO"]["discovery_rate"] > out["PM"]["discovery_rate"] and
           out["XO"]["mean_foothold_density"] > out["PM"]["mean_foothold_density"] and
           out["XO"]["mean_d_flat"] < out["PM"]["mean_d_flat"] and
           out["XO"]["mean_rho"] > out["PM"]["mean_rho"])
    out["criterion1_arm_ranking_correct"] = ok1
    out["criterion2_note"] = "PASS per ruler iff boot_ci95_absdiff lower bound >= 0 in the arm(s) with variance in T"
    json.dump(out, sys.stdout, indent=1, default=str)


if __name__ == "__main__":
    main()
