#!/usr/bin/env python3
"""D001-09 analysis: does accumulated executable history (D8 M1F) add anything
beyond the diversity supplied by the same machinery filled with random programs
(D8 HRND)?

Inputs (read-only, repo commit 0424c372a6bba88f50d31f3abbd8b1204871bba6; files
unchanged since d332658cf):
  SerendipityFoundry/D8/agent_d8/ledgers/eval_<ARM>.jsonl   @0424c372a
  one JSON row per (arm, task): keys uid, arm, solved, family, solve_evals, ...

Usage:  python analysis.py <repo_root>
stdlib only. Not executed by the worker (no code execution available);
the paired counts quoted in REPORT.md were tallied by hand from the ledger rows
and this script is the mechanical check of that tally.

Decision rule (stated before running):
  * PRIMARY for this question: paired exact McNemar M1F vs HRND on the 60
    EV F1-F3 tasks. Content "adds something beyond diversity" iff
    b(M1F only) > c(HRND only) with two-sided p < 0.05.
    Hand tally expects b=7, c=6, p=1.0  -> NOT SHOWN.
  * Sanity: M1F vs M0b must reproduce the report's 11/5, p=0.210; HRND vs
    M0b hand tally 10/5 (p~0.30).
  * If the script gives different b/c than the hand tally, the hand tally
    (REPORT.md) is wrong and the script wins.
  * Power block: number of tasks needed to detect a content effect of
    size delta at the observed discordance rate (normal approximation).
"""
import json
import math
import os
import random
import sys
from math import comb

ARMS = ["M0a", "M0b", "M0c", "M1F", "M1L", "HBAG", "HSHUF", "HRND",
        "ABLMAC", "ABLRET", "ABLBIG"]
PRIMARY_FAMS = {"F1", "F2", "F3"}


def load(root, arm):
    p = os.path.join(root, "SerendipityFoundry", "D8", "agent_d8", "ledgers",
                     "eval_%s.jsonl" % arm)
    out = {}
    with open(p) as f:
        for line in f:
            r = json.loads(line)
            if r["family"] in PRIMARY_FAMS:
                out[r["uid"]] = bool(r["solved"])
    return out


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def paired(a, b):
    uids = sorted(set(a) & set(b))
    assert len(uids) == 60, len(uids)
    bb = sum(1 for u in uids if a[u] and not b[u])
    cc = sum(1 for u in uids if b[u] and not a[u])
    return uids, bb, cc


def boot_ci(a, b, uids, reps=2000, seed=0):
    rng = random.Random(seed)
    d = [int(a[u]) - int(b[u]) for u in uids]
    n = len(d)
    stats = sorted(sum(rng.choice(d) for _ in range(n)) / n for _ in range(reps))
    return stats[int(0.025 * reps)], stats[int(0.975 * reps) - 1]


def tasks_needed(delta, disc_rate, alpha_z=1.959964, power_z=0.841621):
    """Normal-approx McNemar sample size: tasks needed so that a true paired
    difference `delta` with discordance rate `disc_rate` is detected at
    two-sided alpha=0.05, power=0.80."""
    p = 0.5 + delta / (2 * disc_rate)
    if p >= 1:
        return float("nan")
    nd = (alpha_z * 0.5 + power_z * math.sqrt(p * (1 - p))) ** 2 / (p - 0.5) ** 2
    return nd / disc_rate


def main(root):
    L = {a: load(root, a) for a in ARMS}
    print("solve rates (EV F1-F3, n=60)")
    for a in ARMS:
        print("  %-7s %.3f" % (a, sum(L[a].values()) / 60))
    pairs = [("M1F", "M0b"), ("M1F", "HRND"), ("HRND", "M0b"),
             ("M1F", "HBAG"), ("M1F", "HSHUF"), ("M1L", "HRND"),
             ("M1L", "M0b"), ("HRND", "M0c"), ("M1F", "M0c")]
    print("\npaired exact McNemar (b = first-only, c = second-only)")
    res = {}
    for x, y in pairs:
        uids, b, c = paired(L[x], L[y])
        p = mcnemar_exact(b, c)
        lo, hi = boot_ci(L[x], L[y], uids)
        res[(x, y)] = (b, c, p)
        print("  %-5s vs %-5s  delta=%+.3f  b/c=%2d/%-2d  p=%.3f  boot95=[%+.3f,%+.3f]"
              % (x, y, (b - c) / 60, b, c, p, lo, hi))
        if (x, y) == ("M1F", "HRND"):
            print("      M1F-only:", [u for u in uids if L[x][u] and not L[y][u]])
            print("      HRND-only:", [u for u in uids if L[y][u] and not L[x][u]])

    b, c, p = res[("M1F", "HRND")]
    verdict = "CONTENT_BEYOND_DIVERSITY_SHOWN" if (b > c and p < 0.05) else "NOT_SHOWN"
    print("\nDECISION (M1F vs HRND):", verdict)

    disc = (b + c) / 60
    print("\npower: tasks needed (alpha .05 two-sided, power .80), disc rate %.3f" % disc)
    for d in (0.017, 0.05, 0.083, 0.10):
        print("  content delta %.3f -> ~%.0f tasks" % (d, tasks_needed(d, disc)))
    b0, c0, _ = res[("M1F", "M0b")]
    d0 = (b0 + c0) / 60
    print("  (check) M1F vs M0b delta 0.10 at disc %.3f -> ~%.0f tasks (report: 3-4x of 60)"
          % (d0, tasks_needed(0.10, d0)))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
