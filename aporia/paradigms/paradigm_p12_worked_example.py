"""PARADIGM-P12 worked example — Height and Diophantine Geometry, executed.

The paradigm's move: assign arithmetic SIZE (height) to points; finiteness and
structure follow from how height grows. Executable instance: the height
machine's signature on an elliptic curve — for a non-torsion rational point P,
the naive height of nP grows QUADRATICALLY (h(nP) ~ n^2 * hhat(P), the
canonical height). We compute nP in EXACT rational arithmetic on 37a1
(y^2 + y = x^3 - x, the smallest rank-1 conductor; generator P = (0,0)) and
measure h(nP) = log max(|num(x)|, |den(x)|).

Gates (each its own, P82 rule):
  - every computed point must satisfy the curve equation EXACTLY (Fractions)
    — the on-curve invariant is asserted at every step (P07's pattern).
  - the group law is exercised against a hand-checkable known first: 2P
    computed by the doubling formula must equal the value derived in-code
    from the tangent construction run symbolically on P=(0,0).

Pre-stated readings (BEFORE run):
  HEIGHT-QUADRATIC  h(nP)/n^2 converges (last three values within 2% of each
                    other) AND the log-log fitted exponent of h(nP) vs n is
                    within [1.9, 2.1]; all points on-curve exactly.
  HEIGHT-ANOMALY    otherwise — instrument-first: group-law sign conventions
                    (the a1,a3 terms of 37a1 are the classic trap), Fraction
                    overflow (impossible in python), height definition
                    (max of |num|,|den| of x).
"""
from __future__ import annotations
import json
import math
import pathlib
from fractions import Fraction

import numpy as np

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p12_results.json"

# 37a1: y^2 + a1 x y + a3 y = x^3 + a2 x^2 + a4 x + a6 with [0, 0, 1, -1, 0]
A1, A2, A3, A4, A6 = 0, 0, 1, -1, 0


def on_curve(P):
    if P is None:
        return True
    x, y = P
    return y * y + A1 * x * y + A3 * y == x ** 3 + A2 * x * x + A4 * x + A6


def add(P, Q):
    """Standard chord-tangent law for the general Weierstrass form (derived,
    with the a1/a3 terms carried — dropping them is the classic trap)."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2 + A1 * x2 + A3) == 0:
        return None                                  # P + (-P) = O
    if P == Q:
        lam = (3 * x1 * x1 + 2 * A2 * x1 + A4 - A1 * y1) / (2 * y1 + A1 * x1 + A3)
    else:
        lam = (y2 - y1) / (x2 - x1)
    nu = y1 - lam * x1
    x3 = lam * lam + A1 * lam - A2 - x1 - x2
    y3 = -(lam + A1) * x3 - nu - A3
    return (x3, y3)


P = (Fraction(0), Fraction(0))
assert on_curve(P), "generator not on curve — coefficient fault"

# gate: 2P by the implemented law vs the tangent construction done longhand
twoP = add(P, P)
# longhand at (0,0): lam = (0+0-1-0)/(0+0+1) = -1; nu = 0; x3 = 1-0-0 = 1;
# y3 = -(-1)*1 - 0 - 1 = 0  -> (1, 0)
assert twoP == (Fraction(1), Fraction(0)), f"group-law gate FAILS: 2P={twoP}"
assert on_curve(twoP)
print(f"group-law gate: 2P = {twoP} matches the longhand tangent construction — PASS", flush=True)

ns, hs = [], []
cur = None
NP = 24
pts = {}
for n in range(1, NP + 1):
    cur = add(cur, P)
    assert on_curve(cur), f"point {n}P off-curve — group-law fault"
    x = cur[0]
    h = math.log(max(abs(x.numerator), abs(x.denominator))) if n > 1 else 0.0
    ns.append(n)
    hs.append(h)
ratios = [hs[i] / ns[i] ** 2 for i in range(len(ns))]
print("n, h(nP), h/n^2 (last 8):", flush=True)
for i in range(len(ns) - 8, len(ns)):
    print(f"  n={ns[i]:2d}  h={hs[i]:10.4f}  h/n^2={ratios[i]:.6f}", flush=True)

last3 = ratios[-3:]
converged = (max(last3) - min(last3)) / max(last3) < 0.02
mask = np.array(ns) >= 5
slope = float(np.polyfit(np.log(np.array(ns)[mask]), np.log(np.array(hs)[mask]), 1)[0])
print(f"log-log fitted exponent (n>=5): {slope:.4f}; last-3 h/n^2 spread "
      f"{(max(last3)-min(last3))/max(last3):.4%}", flush=True)
verdict = ("HEIGHT-QUADRATIC" if (converged and 1.9 <= slope <= 2.1) else "HEIGHT-ANOMALY")
print(f"-> {verdict}  (canonical-height estimate hhat(P) ~ {ratios[-1]:.6f})", flush=True)

OUT.write_text(json.dumps({
    "protocol": "exact-rational multiples of the generator (0,0) on 37a1, full Weierstrass chord-tangent law with a1/a3 carried, on-curve invariant per step, naive height of x-coordinate",
    "curve": "37a1 [0,0,1,-1,0]", "n_max": NP,
    "heights": [round(h, 4) for h in hs],
    "h_over_n2_last3": [round(r, 6) for r in last3],
    "loglog_exponent": slope, "hhat_estimate": ratios[-1],
    "verdict": verdict}, indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
