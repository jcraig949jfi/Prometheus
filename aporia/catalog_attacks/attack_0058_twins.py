"""CAT-MATH-0058 attack — twin primes vs 2*C2*li_2 (spec ELENCHUS-CORRECTED).

The correction is binding: predictor is 2*C2*li_2(x), li_2(x) = int_2^x dt/ln^2 t
(the reviewer demonstrated x/ln^2 x gives an unresolvable 1.49 while li_2 gives
0.9999 at 1e8 — that value is this run's reproduction target).
C2 computed from its Euler product. Convention flip: pairs counted by p<=x AND by
p+2<=x (both reported; the difference is edge-only but recorded, per P51 residue).
"""
from __future__ import annotations
import json
import math
import pathlib
import time

import numpy as np

N = 100_000_000
OUT = pathlib.Path(__file__).parent / "attack_0058_results.json"

t0 = time.time()
S = np.ones(N + 3, dtype=bool)
S[:2] = False
for p in range(2, int((N + 2) ** 0.5) + 1):
    if S[p]:
        S[p * p:: p] = False
primes = np.flatnonzero(S[: N + 1]).astype(np.int64)
print(f"sieve: {len(primes)} primes to {N:.0e} in {time.time()-t0:.1f}s")

pp = primes[(primes > 2) & (primes <= 10_000_000)].astype(np.float64)
C2 = float(np.exp(np.sum(np.log1p(-1.0 / (pp - 1.0) ** 2))))
print(f"C2 computed = {C2:.10f}")

# twin lower members p with p and p+2 prime, p+2 <= N+2 handled by sieve padding
twin_p = primes[S[primes + 2]]
print(f"twin pairs with lower member <= {N:.0e}: {len(twin_p)}")

def li2(x, steps=200_000):
    # u-substitution t = e^u: int_2^x dt/ln^2 t = int_{ln2}^{ln x} e^u/u^2 du.
    # The integrand is smooth in u, so a uniform-in-u trapezoid converges fast;
    # a uniform-in-t grid (first draft) under-resolves near t=2 and biased the
    # predictor ~0.15% high — caught by the REVIEWER-MISMATCH pre-stated reading.
    us = np.linspace(math.log(2.0), math.log(float(x)), steps)
    return float(np.trapezoid(np.exp(us) / us ** 2, us))

rows = []
for k in range(3, 9):
    x = 10 ** k
    obs_lower = int(np.count_nonzero(twin_p <= x))          # p <= x
    obs_upper = int(np.count_nonzero(twin_p <= x - 2))      # p+2 <= x
    pred = 2.0 * C2 * li2(x)
    rows.append({"x": x, "obs_p_le_x": obs_lower, "obs_pair_le_x": obs_upper,
                 "pred_2C2_li2": round(pred, 2),
                 "ratio_lower": round(obs_lower / pred, 6),
                 "ratio_upper": round(obs_upper / pred, 6)})
    print(f"1e{k}: obs {obs_lower:>8} pred {pred:>12.1f} ratio {obs_lower/pred:.6f}")

OUT.write_text(json.dumps({"C2_computed": C2, "n_twins_1e8": len(twin_p),
                           "per_decade": rows}, indent=1), encoding="utf-8")
print(f"-> {OUT.name}")
