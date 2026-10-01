"""P1 calibration slice: a search-power curve from planted targets (REQUIREMENTS.md SRCH-01 to SRCH-04).

    python reach.py            # writes RECEIPT_reach.json

Question. If d of the 8 instructions of the minimal builder are knocked out,
how often does blind search put them back, as a function of d, of the budget,
and of the acceptance rule?

This is the design's "descent" in miniature: scaffold level S5 is the designed
builder (d = 0), S4 is the builder with parts removed (d = 1, 2, 3), and d = 8
is the same search started from an empty program.

Search: one lineage is a chain. Each step proposes a single-point mutation of
the current parent (one instruction replaced by a random one) and scores it on
a FIXED block of training lives by the number of correct BUILD probes. Three
acceptance rules, held as a declared factor (SRCH-01):

  margin   accept only if the child gains at least a quarter of all probes
           (a jump no chance fluctuation can produce on this block)
  neutral  accept if the child is at least as good as the parent
  strict   accept only if the child is better than the parent

A lineage counts as RECOVERED only if it (1) reaches a perfect score on the
training block, (2) scores at least 0.9 on SELECTION lives it never saw, and
(3) passes the BUILD class-exclusion ruler on SEALED lives. Selection never
sees the lives on which the result is reported (SRCH-05).

Forecasts were written before the first run (PREREG.md) and are scored here.
"""
import hashlib
import json
import pathlib
import platform
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction

import numba
import numpy as np
from numba import njit, prange

import organisms as org
import rulers as ru
import wm_mini as wm

HERE = pathlib.Path(__file__).resolve().parent

BUDGET = 200_000          # proposals per lineage
LINEAGES = 24             # independent lineages per cell
DISTANCES = (0, 1, 2, 3, 8)
REGIMES = ("margin", "neutral", "strict")
N_TRAIN = 16              # training lives 0..15
N_SELECT = 64             # selection lives 1000..1063
N_SEALED = 64             # sealed lives
SEARCH_SEED = 777
P_KNOCK = 5_000_003
P_MUT = 7_000_003
P_RAND = 9_000_003
N_RANDOM = 2_000_000      # random programs for the random-hit rate

# Forecasts, written before the first run. Each is a statement and my probability that it is true.
FORECASTS = {
    "F1 margin rule, d=1: recovery rate >= 0.9": 0.85,
    "F2 margin rule, d=2: recovery rate <= 0.2": 0.80,
    "F3 every rule, d=8 (from an empty program): zero recoveries": 0.97,
    "F4 neutral and strict rules, d=1: recovery rate lower than the margin rule's": 0.75,
    "F5 margin rule: recovery rate does not rise as d goes 1, 2, 3, 8": 0.90,
    "F6 random programs: zero of 2,000,000 score >= 0.9 on the training block": 0.97,
}


@njit(cache=True)
def _u(h, shift, mod):
    return np.int64((h >> np.uint64(shift)) % np.uint64(mod))


@njit(cache=True)
def knock_out(target, n, d, seed, lineage):
    """Copy of the target with d distinct instructions replaced by NOP."""
    prog = target.copy()
    idx = np.arange(n)
    for j in range(d):                       # partial Fisher-Yates driven by the hash
        h = wm.khash(seed, lineage, P_KNOCK, j)
        r = j + np.int64(h % np.uint64(n - j))
        tmp = idx[j]
        idx[j] = idx[r]
        idx[r] = tmp
        for q in range(4):
            prog[idx[j], q] = 0
    return prog


@njit(cache=True)
def search_lineage(target, n, d, store0, seed, lineage, budget, regime,
                   K, R, E, T, F, cap, train0, ntrain, out_prog):
    """Returns (evaluations until a perfect training score, or -1; final training score)."""
    parent = knock_out(target, n, d, seed, lineage)
    fp, nfix = wm.probe_fitness(parent, n, store0, seed, train0, ntrain, K, R, E, T, F, cap)
    margin = (nfix + 3) // 4
    done = 0 if fp == nfix else -1
    child = parent.copy()
    i = 0
    while done < 0 and i < budget:
        h = wm.khash(SEARCH_SEED, lineage * 4 + regime, P_MUT + d, i)
        pos = _u(h, 0, n)
        old0, old1, old2, old3 = parent[pos, 0], parent[pos, 1], parent[pos, 2], parent[pos, 3]
        child[pos, 0] = _u(h, 8, wm.NOPS)
        child[pos, 1] = _u(h, 16, 8)
        child[pos, 2] = _u(h, 24, 64)
        child[pos, 3] = _u(h, 32, 16)
        fc, _ = wm.probe_fitness(child, n, store0, seed, train0, ntrain, K, R, E, T, F, cap)
        if regime == 0:
            accept = fc >= fp + margin
        elif regime == 1:
            accept = fc >= fp
        else:
            accept = fc > fp
        if accept:
            parent[pos, 0] = child[pos, 0]
            parent[pos, 1] = child[pos, 1]
            parent[pos, 2] = child[pos, 2]
            parent[pos, 3] = child[pos, 3]
            fp = fc
        else:
            child[pos, 0] = old0
            child[pos, 1] = old1
            child[pos, 2] = old2
            child[pos, 3] = old3
        i += 1
        if fp == nfix:
            done = i
    for a in range(n):
        for q in range(4):
            out_prog[a, q] = parent[a, q]
    return done, fp


@njit(parallel=True, cache=True)
def search_cell(target, n, d, store0, seed, lineages, budget, regime, K, R, E, T, F, cap, train0, ntrain):
    evals = np.zeros(lineages, dtype=np.int64)
    fit = np.zeros(lineages, dtype=np.int64)
    progs = np.zeros((lineages, n, 4), dtype=np.int64)
    for j in prange(lineages):
        e, f = search_lineage(target, n, d, store0, seed, j, budget, regime,
                              K, R, E, T, F, cap, train0, ntrain, progs[j])
        evals[j] = e
        fit[j] = f
    return evals, fit, progs


@njit(parallel=True, cache=True)
def random_hits(nprog, n, store0, seed, K, R, E, T, F, cap, train0, ntrain, thresh_num, thresh_den):
    """How many uniformly random programs of length n score >= thresh on the training block?"""
    hits = np.zeros(nprog, dtype=np.int64)
    best = np.zeros(nprog, dtype=np.int64)
    for j in prange(nprog):
        prog = np.zeros((n, 4), dtype=np.int64)
        for a in range(n):
            h = wm.khash(SEARCH_SEED, j, P_RAND, a)
            prog[a, 0] = _u(h, 8, wm.NOPS)
            prog[a, 1] = _u(h, 16, 8)
            prog[a, 2] = _u(h, 24, 64)
            prog[a, 3] = _u(h, 32, 16)
        f, nfix = wm.probe_fitness(prog, n, store0, seed, train0, ntrain, K, R, E, T, F, cap)
        best[j] = f
        if f * thresh_den >= thresh_num * nfix:
            hits[j] = 1
    return hits.sum(), best.max()


def confirm(prog, P):
    """Selection lives, then sealed lives. Returns (selected, sealed verdict, sealed accuracy)."""
    st = org.empty_store(P.S)
    c = ru.evaluate(prog, st, P, 1000, N_SELECT, sealed=False)["counts"]
    sel_ok = 10 * int(c[wm.T_PROBE, 1]) >= 9 * int(c[wm.T_PROBE, 0])
    if not sel_ok:
        return False, None, None
    c = ru.evaluate(prog, st, P, ru.SEALED_BASE + 60_000, N_SEALED)["counts"]
    v = ru.class_exclusion(int(c[wm.T_PROBE, 0]), int(c[wm.T_PROBE, 1]), P.R)
    return True, v["verdict"], int(c[wm.T_PROBE, 1]) / max(1, int(c[wm.T_PROBE, 0]))


def needle_bits():
    """Bits needed to specify builder_min exactly under the mutation operator's
    distribution (op uniform over 19, a over 8, b over 64, c over 16), counting
    only the fields each instruction actually uses. An upper bound on the
    needle: register renamings and other equivalent programs make it smaller."""
    from math import log2
    op = log2(19)
    spec = {
        "PH 6": op + 3, "SKZ 6": op + 3, "JMP +3": op + 4, "IN 0": op + 3,
        "STR 1,0": op + 3 + 3, "OUT 1": op + 3, "IN 3": op + 3, "STW 0,3": op + 3 + 3,
    }
    return spec, sum(spec.values())


def main():
    ru.require_unsealed(0, N_TRAIN)
    P = ru.Params()
    target = org.builder_min()
    n = target.shape[0]
    st = org.empty_store(P.S)
    args = (P.K, P.R, P.E, P.T, P.F, P.cap, 0, N_TRAIN)
    search_cell(target, n, 0, st, P.seed, 2, 10, 0, *args)                   # compile
    t0 = time.perf_counter()
    cells, total_evals = {}, 0
    for regime_id, regime in enumerate(REGIMES):
        for d in DISTANCES:
            t = time.perf_counter()
            evals, fit, progs = search_cell(target, n, d, st, P.seed, LINEAGES, BUDGET, regime_id, *args)
            recovered, when, overfit = 0, [], 0
            for j in range(LINEAGES):
                total_evals += int(evals[j]) if evals[j] >= 0 else BUDGET
                if evals[j] >= 0:
                    sel, verdict, acc = confirm(progs[j], P)
                    if sel and verdict == ru.PASS:
                        recovered += 1
                        when.append(int(evals[j]))
                    else:
                        overfit += 1
            by_budget = {str(b): sum(1 for w in when if w <= b) / LINEAGES for b in (2_000, 20_000, 200_000)}
            cells["%s d=%d" % (regime, d)] = {
                "regime": regime, "d": d, "lineages": LINEAGES, "recovered": recovered,
                "rate": recovered / LINEAGES, "perfect_on_training_but_not_confirmed": overfit,
                "rate_by_budget": by_budget,
                "median_evals_to_recover": int(np.median(when)) if when else None,
                "final_training_score_median": int(np.median(fit)),
                "seconds": round(time.perf_counter() - t, 1),
            }
            print("%-8s d=%d  recovered %2d/%d  by budget %s  median evals %s  (%.1f s)" % (
                regime, d, recovered, LINEAGES, by_budget,
                cells["%s d=%d" % (regime, d)]["median_evals_to_recover"], time.perf_counter() - t))

    # random-hit rate and needle size (SRCH-03)
    t = time.perf_counter()
    hits, best = random_hits(N_RANDOM, n, st, P.seed, P.K, P.R, P.E, P.T, P.F, P.cap, 0, N_TRAIN, 9, 10)
    _, nfix = wm.probe_fitness(target, n, st, P.seed, 0, N_TRAIN, P.K, P.R, P.E, P.T, P.F, P.cap)
    spec, bits = needle_bits()
    # exact one-sided 95% upper bound on the hit rate when 0 of N hit: 1 - 0.05^(1/N)
    upper = (1 - 0.05 ** (1.0 / N_RANDOM)) if hits == 0 else None
    rnd = {"programs": N_RANDOM, "hits_at_0.9": int(hits), "best_training_score": int(best),
           "training_probes": int(nfix), "upper_bound_95_on_hit_rate_if_zero": upper,
           "seconds": round(time.perf_counter() - t, 1),
           "needle_bits_exact_match_upper_bound": round(bits, 2), "needle_spec_bits": spec}
    print("random programs: %d of %d reach 0.9 on the training block; best score %d of %d (%.1f s)" % (
        hits, N_RANDOM, best, nfix, time.perf_counter() - t))
    print("needle: at most %.1f bits to specify builder_min exactly under the mutation distribution" % bits)

    def rate(regime, d):
        return cells["%s d=%d" % (regime, d)]["rate"]

    truth = {
        "F1 margin rule, d=1: recovery rate >= 0.9": rate("margin", 1) >= 0.9,
        "F2 margin rule, d=2: recovery rate <= 0.2": rate("margin", 2) <= 0.2,
        "F3 every rule, d=8 (from an empty program): zero recoveries": all(rate(r, 8) == 0 for r in REGIMES),
        "F4 neutral and strict rules, d=1: recovery rate lower than the margin rule's":
            rate("neutral", 1) < rate("margin", 1) and rate("strict", 1) < rate("margin", 1),
        "F5 margin rule: recovery rate does not rise as d goes 1, 2, 3, 8":
            rate("margin", 1) >= rate("margin", 2) >= rate("margin", 3) >= rate("margin", 8),
        "F6 random programs: zero of 2,000,000 score >= 0.9 on the training block": int(hits) == 0,
    }
    brier = sum((FORECASTS[k] - (1.0 if truth[k] else 0.0)) ** 2 for k in FORECASTS) / len(FORECASTS)
    brier_half = sum((0.5 - (1.0 if truth[k] else 0.0)) ** 2 for k in FORECASTS) / len(FORECASTS)
    print("forecasts:")
    for k in FORECASTS:
        print("   p=%.2f  %-5s  %s" % (FORECASTS[k], truth[k], k))
    print("Brier score %.4f (always-0.5 baseline %.4f)" % (brier, brier_half))
    d0_ok = all(cells["%s d=0" % r]["rate"] == 1.0 for r in REGIMES)
    print("positive control of the search harness (d=0 recovered by every rule): %s" % d0_ok)
    print("total proposals evaluated: %d in %.1f s" % (total_evals, time.perf_counter() - t0))

    src = {}
    for name in ("wm_mini.py", "organisms.py", "rulers.py", "reach.py"):
        src[name] = hashlib.sha256((HERE / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    receipt = {
        "what": "P1 calibration slice prototype: search-power curve from planted targets",
        "written_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "host": platform.node(), "python": platform.python_version(), "numba": numba.__version__,
        "threads": numba.get_num_threads(), "params": P.as_dict(),
        "budget_per_lineage": BUDGET, "lineages_per_cell": LINEAGES, "train_lives": N_TRAIN,
        "select_lives": N_SELECT, "sealed_lives": N_SEALED, "search_seed": SEARCH_SEED,
        "cells": cells, "random": rnd, "forecasts": FORECASTS,
        "forecast_truth": {k: bool(v) for k, v in truth.items()},
        "brier": brier, "brier_baseline_half": brier_half,
        "search_harness_positive_control_d0": bool(d0_ok),
        "total_proposals": total_evals, "seconds": round(time.perf_counter() - t0, 1),
        "source_sha256_lf": src,
    }
    (HERE / "RECEIPT_reach.json").write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n",
                                             encoding="utf-8", newline="\n")
    return 0 if d0_ok else 1


if __name__ == "__main__":
    sys.exit(main())
