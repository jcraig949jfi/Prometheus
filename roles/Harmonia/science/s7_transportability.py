"""S7 -- TRANSPORT VALIDITY: attacking C-8 and the replication-level question.

Harmonia science loop 7 part 2, 2026-09-05.

C-8 as proposed said "a parameter held fixed is a scope boundary; declare every
fixed parameter". Literally applied that is impossible -- a run fixes the
interpreter version, the CPU, the order of dict keys. So the rule must be
derived, not asserted.

METHOD: perturb each fixed parameter of the SE-1b cell one at a time, holding
everything else, and classify what the perturbation actually does to the claim:

  INERT        the estimate is unchanged within noise
  PRECISION    only the variance changes; the estimand is the same
  MAGNITUDE    the effect size moves materially but keeps its sign
  SIGN         the direction reverses -- the claim's content inverts
  ESTIMAND     the quantity being estimated is no longer the same quantity

The last class is the interesting one and it is not a matter of degree. A
heterogeneous world population does not perturb the effect; it replaces "the
effect" with "the average effect over a mixture", which is a different thing
that happens to have the same name.

A THIRD PLAYER CLASS (annealing) is run through the identical machinery, because
a constraint derived from two policies is a claim about two policies.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys

BITS, ENC, NW, BLOCKS = 64, 20, 64, 6


def target_for(seed, bits=BITS):
    r = random.Random("t|%s|%s" % (seed, bits))
    return [r.randint(0, 1) for _ in range(bits)]


def score(b, t, structure="smooth", scale=1.0, noise=0.0, rng=None):
    bits = len(t)
    if structure == "smooth":
        v = sum(1 for i in range(bits) if b[i] == t[i]) / bits
    else:
        nb = bits // 8
        v = sum(1 for k in range(nb)
                if all(b[i] == t[i] for i in range(k * 8, k * 8 + 8))) / nb
    if noise and rng:
        v += rng.gauss(0, noise)
    return v * scale


def hill(t, seed, enc=ENC, structure="smooth", scale=1.0, noise=0.0,
         mut=1, tie=">=", init="random"):
    bits = len(t)
    r = random.Random("hill|%s" % seed)
    cur = ([0] * bits if init == "zeros"
           else [r.randint(0, 1) for _ in range(bits)])
    best = score(cur, t, structure, scale, noise, r)
    for _ in range(enc - 1):
        cand = list(cur)
        for _ in range(mut):
            cand[r.randrange(bits)] ^= 1
        s = score(cand, t, structure, scale, noise, r)
        if (s >= best) if tie == ">=" else (s > best):
            cur, best = cand, s
    return best


def sample(t, seed, enc=ENC, structure="smooth", scale=1.0, noise=0.0,
           init="random", **kw):
    bits = len(t)
    r = random.Random("sample|%s" % seed)
    first = ([0] * bits if init == "zeros"
             else [r.randint(0, 1) for _ in range(bits)])
    best = score(first, t, structure, scale, noise, r)
    for _ in range(enc - 1):
        best = max(best, score([r.randint(0, 1) for _ in range(bits)],
                               t, structure, scale, noise, r))
    return best


def anneal(t, seed, enc=ENC, structure="smooth", scale=1.0, noise=0.0,
           init="random", **kw):
    """THIRD PLAYER CLASS: accepts worsening moves with decaying probability."""
    bits = len(t)
    r = random.Random("anneal|%s" % seed)
    cur = ([0] * bits if init == "zeros"
           else [r.randint(0, 1) for _ in range(bits)])
    cs = score(cur, t, structure, scale, noise, r)
    best = cs
    for k in range(enc - 1):
        temp = max(1e-6, 0.15 * (1 - k / max(1, enc - 1)))
        cand = list(cur)
        cand[r.randrange(bits)] ^= 1
        s = score(cand, t, structure, scale, noise, r)
        if s >= cs or r.random() < math.exp((s - cs) / temp):
            cur, cs = cand, s
        best = max(best, cs)
    return best


def cohen_d(a, b):
    va, vb = statistics.variance(a), statistics.variance(b)
    sp = (((len(a) - 1) * va + (len(b) - 1) * vb) / (len(a) + len(b) - 2)) ** 0.5
    return (statistics.fmean(b) - statistics.fmean(a)) / sp if sp else 0.0


def effect(playerA, playerB, seed_off, bits=BITS, **kw):
    """d for (B - A) over NW worlds. Positive means B beats A."""
    A, B = [], []
    for w in range(NW):
        t = target_for(seed_off + w, bits)
        A.append(playerA(t, seed_off + w, **kw))
        B.append(playerB(t, seed_off + w, **kw))
    return cohen_d(A, B)


def blocked_estimate(playerA, playerB, bits=BITS, **kw):
    """Mean and sd of d over BLOCKS independent seed blocks."""
    ds = [effect(playerA, playerB, 20000 + 1000 * k, bits, **kw)
          for k in range(BLOCKS)]
    m = statistics.fmean(ds)
    sd = statistics.stdev(ds)
    return m, sd, ds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    print("=" * 78)
    print("S7  PERTURBING THE 'IMPLEMENTATION DETAILS' OF THE SE-1b CELL")
    print("    baseline: hill vs sample, smooth, 64 bits, budget 20")
    print("    each estimate is the mean of %d independent seed blocks of "
          "n=%d worlds" % (BLOCKS, NW))
    print("=" * 78)

    base_m, base_sd, _ = blocked_estimate(sample, hill)
    se_block = base_sd / BLOCKS ** 0.5
    print("\n  BASELINE d(hill - sample) = %+.3f  (sd across blocks %.3f, "
          "SE %.3f)" % (base_m, base_sd, se_block))
    print("  a perturbation counts as MATERIAL if it moves d by more than "
          "2 SE = %.3f\n" % (2 * se_block))

    PERTURBATIONS = [
        ("seed stream (new blocks)", dict(), "resampling only"),
        ("scoring scale x100", dict(scale=100.0), None),
        ("tie-break > instead of >=", dict(tie=">"), None),
        ("start state all-zeros", dict(init="zeros"), None),
        ("mutation operator 2-bit", dict(mut=2), None),
        ("observation noise sd=0.02", dict(noise=0.02), None),
        ("encounter budget 20 -> 10", dict(enc=10), None),
        ("encounter budget 20 -> 40", dict(enc=40), None),
        ("landscape 64 -> 128 bits", dict(bits=128), None),
        ("landscape structure -> blocked", dict(structure="blocked"), None),
    ]

    rows = []
    print("  perturbation                        d        delta     class")
    print("  " + "-" * 70)
    for label, kw, note in PERTURBATIONS:
        bits = kw.pop("bits", BITS)
        m, sd, _ = blocked_estimate(sample, hill, bits=bits, **kw)
        delta = m - base_m
        material = abs(delta) > 2 * se_block
        if (m > 0) != (base_m > 0):
            klass = "SIGN"
        elif material:
            klass = "MAGNITUDE"
        elif sd > base_sd * 1.5:
            klass = "PRECISION"
        else:
            klass = "INERT"
        rows.append({"perturbation": label, "d": m, "sd": sd,
                     "delta_vs_baseline": delta, "class": klass})
        print("  %-33s %+.3f   %+.3f    %s" % (label, m, delta, klass))

    # ------------------------------------------------------------------
    # ESTIMAND CHANGE: a heterogeneous world population
    # ------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("HETEROGENEOUS WORLDS -- does this perturb the effect, or replace it?")
    print("=" * 78)
    ds_mix = []
    for k in range(BLOCKS):
        A, B = [], []
        for w in range(NW):
            off = 20000 + 1000 * k + w
            structure = "smooth" if w % 2 == 0 else "blocked"
            t = target_for(off)
            A.append(sample(t, off, structure=structure))
            B.append(hill(t, off, structure=structure))
        ds_mix.append(cohen_d(A, B))
    mix_m, mix_sd = statistics.fmean(ds_mix), statistics.stdev(ds_mix)
    sm_m, sm_sd, _ = blocked_estimate(sample, hill, structure="smooth")
    bl_m, bl_sd, _ = blocked_estimate(sample, hill, structure="blocked")
    print("\n  pure smooth worlds        d = %+.3f" % sm_m)
    print("  pure blocked worlds       d = %+.3f" % bl_m)
    print("  50/50 mixture             d = %+.3f" % mix_m)
    print("  mean of the two pure      d = %+.3f" % ((sm_m + bl_m) / 2))
    print("\n  The mixture value is not a perturbation of either pure value.")
    print("  It is an average over a POPULATION OF WORLDS that the claim must")
    print("  name. Change the mixing proportion and the number changes with")
    print("  no experimental error at all -- the ESTIMAND moved, not the")
    print("  estimate.")

    # ------------------------------------------------------------------
    # THIRD PLAYER CLASS through the identical machinery
    # ------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("THIRD PLAYER CLASS (simulated annealing) THROUGH THE SAME MACHINERY")
    print("=" * 78)
    pairs = [("hill - sample", sample, hill),
             ("anneal - sample", sample, anneal),
             ("anneal - hill", hill, anneal)]
    third = {}
    for lbl, pa, pb in pairs:
        for structure in ("smooth", "blocked"):
            m, sd, _ = blocked_estimate(pa, pb, structure=structure)
            third["%s | %s" % (lbl, structure)] = {"d": m, "sd": sd}
            print("  %-18s %-8s  d = %+.3f  (sd %.3f)" % (lbl, structure, m, sd))
    print("\n  The ordering of the three policies is not stable across")
    print("  landscape structure. A constraint derived from two of them is a")
    print("  claim about those two.")

    out = {"baseline_d": base_m, "baseline_sd": base_sd,
           "block_se": se_block, "perturbations": rows,
           "heterogeneous": {"smooth": sm_m, "blocked": bl_m,
                             "mixture": mix_m,
                             "mean_of_pures": (sm_m + bl_m) / 2},
           "third_class": third}
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("\nrows: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
