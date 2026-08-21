"""CAT-MATH-0065 attack — maximal prime gaps vs ln^2 p (spec ELENCHUS-CORRECTED).

Binding corrections: p >= 100 cutoff (p=2 gives a spurious 2.08); direction fixed
(ratios approaching/exceeding 2e^-gamma ~ 1.1229 would SUPPORT the Granville frame;
an asymptotic limsup is not falsifiable in range — output is the descriptive trend).
Reproduction target: reviewer-executed in-range max ratio 0.7395 with the cutoff.
Convention flip: g/ln^2 p at the LEFT endpoint and g/ln^2 q at the RIGHT endpoint.
"""
from __future__ import annotations
import json
import math
import pathlib
import time

import numpy as np

N = 100_000_000
OUT = pathlib.Path(__file__).parent / "attack_0065_results.json"

t0 = time.time()
S = np.ones(N + 1, dtype=bool)
S[:2] = False
for p in range(2, int(N ** 0.5) + 1):
    if S[p]:
        S[p * p:: p] = False
primes = np.flatnonzero(S).astype(np.int64)
print(f"sieve: {len(primes)} primes in {time.time()-t0:.1f}s")

gaps = np.diff(primes)
left = primes[:-1].astype(np.float64)
right = primes[1:].astype(np.float64)

mask = left >= 100
g = gaps[mask].astype(np.float64)
ratio_left = g / np.log(left[mask]) ** 2
ratio_right = g / np.log(right[mask]) ** 2
i_max_l = int(np.argmax(ratio_left))
i_max_r = int(np.argmax(ratio_right))
pl = int(left[mask][i_max_l]); gl = int(g[i_max_l])
pr = int(left[mask][i_max_r]); gr = int(g[i_max_r])
print(f"max ratio LEFT  = {ratio_left[i_max_l]:.4f} at p={pl}, gap={gl}")
print(f"max ratio RIGHT = {ratio_right[i_max_r]:.4f} at p={pr}, gap={gr}")

# record gaps (maximal gaps): gap larger than all before it
rec = []
best = 0
for i in range(len(gaps)):
    if gaps[i] > best:
        best = int(gaps[i])
        p = int(primes[i])
        rec.append({"p": p, "gap": best,
                    "ratio_left": round(best / math.log(p) ** 2, 4) if p >= 3 else None})
print(f"record gaps: {len(rec)}; last: {rec[-1]}")

# descriptive trend: per-decade max ratio (left endpoint, cutoff applied)
trend = []
for k in range(2, 8):
    lo, hi = 10 ** k, 10 ** (k + 1)
    m = (left >= max(lo, 100)) & (left < hi)
    if m.any():
        rr = gaps[m] / np.log(left[m]) ** 2
        j = int(np.argmax(rr))
        trend.append({"decade": f"1e{k}-1e{k+1}", "max_ratio": round(float(rr[j]), 4),
                      "at_p": int(left[m][j]), "gap": int(gaps[m][j])})
        print(trend[-1])

TWO_E_NEG_GAMMA = 2 * math.exp(-np.euler_gamma)
OUT.write_text(json.dumps({"cutoff": 100,
    "max_ratio_left": round(float(ratio_left[i_max_l]), 6), "at_p_left": pl, "gap_left": gl,
    "max_ratio_right": round(float(ratio_right[i_max_r]), 6), "at_p_right": pr, "gap_right": gr,
    "granville_2e_neg_gamma": round(TWO_E_NEG_GAMMA, 6),
    "record_gaps": rec, "per_decade_max": trend}, indent=1), encoding="utf-8")
print(f"2e^-gamma = {TWO_E_NEG_GAMMA:.6f} -> {OUT.name}")
