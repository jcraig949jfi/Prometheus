"""THESEUS-40: pool D-solver contrasts across master seeds (stratified 2x2 tables).

Prereg: roles/Theseus/prereg/2026-10-09_third_seed/PREREG.md.

  python -m theseus.synth.pooled --pair <evaldir>:<a>:<b> [--pair ...]

Per stratum (seed): a solvers / n, b solvers / n from J_<run>.jsonl (J >= .6).
  CMH       one-sided Cochran-Mantel-Haenszel test (no continuity correction) that a > b.
  RD_MH     Mantel-Haenszel common risk difference with the Greenland-Robins (1985)
            variance (Sato form), 95% CI.
  per seed  risk difference with Newcombe (Wilson score) 95% CI.
"""

import argparse
import json
import math

from scipy.stats import norm

SOLVER = 0.6


def solvers(path):
    v = [json.loads(l)["v"] for l in open(path, encoding="utf-8")]
    return sum(x >= SOLVER for x in v), len(v)


def wilson(x, n, z=1.959964):
    p = x / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def newcombe(x1, n1, x2, n2):
    p1, p2 = x1 / n1, x2 / n2
    l1, u1 = wilson(x1, n1)
    l2, u2 = wilson(x2, n2)
    d = p1 - p2
    return d, d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)


def cmh(tables):
    num, var = 0.0, 0.0
    for a, n1, c, n2 in tables:
        N = n1 + n2
        m1 = a + c
        m0 = N - m1
        num += a - n1 * m1 / N
        var += n1 * n2 * m1 * m0 / (N * N * (N - 1))
    z = num / math.sqrt(var)
    return z, float(norm.sf(z))


def rd_mh(tables):
    W = sum(n1 * n2 / (n1 + n2) for _, n1, _, n2 in tables)
    rd = sum((a * n2 - c * n1) / (n1 + n2) for a, n1, c, n2 in tables) / W
    # Sato (1989) variance estimator for the MH risk difference
    P = sum((n2 * n2 * a - n1 * n1 * c + n1 * n2 * (n1 - n2) / 2) / (n1 + n2) ** 2 for a, n1, c, n2 in tables)
    Q = sum((a * (n2 - c) + c * (n1 - a)) / (2 * (n1 + n2)) for a, n1, c, n2 in tables)
    se = math.sqrt(max(rd * P + Q, 0.0)) / W
    return rd, rd - 1.959964 * se, rd + 1.959964 * se


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair", action="append", required=True, help="evaldir:runA:runB")
    a = ap.parse_args(argv)
    tables, rows = [], []
    for p in a.pair:
        d, ra, rb = p.split(":")
        xa, na = solvers(f"{d}/J_{ra}.jsonl")
        xb, nb = solvers(f"{d}/J_{rb}.jsonl")
        tables.append((xa, na, xb, nb))
        rd, lo, hi = newcombe(xa, na, xb, nb)
        rows.append({"evaldir": d, "a": ra, "b": rb, "a_solvers": [xa, na], "b_solvers": [xb, nb],
                     "rd": rd, "rd_ci95": [lo, hi]})
    z, p = cmh(tables)
    rd, lo, hi = rd_mh(tables)
    print(json.dumps({"strata": rows, "CMH_z": z, "CMH_p_one_sided": p, "RD_MH": rd, "RD_MH_ci95": [lo, hi]}, indent=1))


if __name__ == "__main__":
    main()
