"""CAT-MATH-0057 attack — binary Goldbach, pure-compute (spec ELENCHUS-SOUND).

Part A: every even 4 <= n <= 1e8 decomposes as p+q (vectorized smallest-partner
        elimination; any survivor is an instrument bug before it is anything else).
Part B: representation counts r(n) (unordered, p <= n/2) for a stratified sample
        vs the Hardy-Littlewood prediction 2*C2*prod_{p|n,p>2}((p-1)/(p-2)) * S(n),
        under BOTH shape conventions (S = n/ln^2 n, and the HL integral
        J(n) = int_2^{n-2} dt/(ln t ln(n-t))) — convention-flip discipline.
C2 is COMPUTED from its Euler product prod_{2<p<=1e7}(1 - 1/(p-1)^2), not memory.
Calibration: r(n) for n in {10, 100, 1000} cross-checked by brute force sympy.
"""
from __future__ import annotations
import json
import math
import pathlib
import time

import numpy as np

N = 100_000_000
OUT = pathlib.Path(__file__).parent / "attack_0057_results.json"


def sieve_bool(n):
    s = np.ones(n + 1, dtype=bool)
    s[:2] = False
    for p in range(2, int(n ** 0.5) + 1):
        if s[p]:
            s[p * p:: p] = False
    return s


t0 = time.time()
S = sieve_bool(N)
primes = np.flatnonzero(S).astype(np.int64)
print(f"sieve to {N:.0e}: {len(primes)} primes in {time.time()-t0:.1f}s")

# ---- C2 from its Euler product (no memory numbers) ----
pp = primes[(primes > 2) & (primes <= 10_000_000)].astype(np.float64)
C2 = float(np.exp(np.sum(np.log1p(-1.0 / (pp - 1.0) ** 2))))
print(f"C2 computed = {C2:.10f}")

# ---- Part A: vectorized smallest-partner elimination ----
t0 = time.time()
evens = np.arange(4, N + 1, 2, dtype=np.int64)
found = np.zeros(len(evens), dtype=bool)
found[0] = bool(S[2])   # n=4 = 2+2: the even prime is not in the odd-partner loop
odd_primes = primes[primes % 2 == 1]
max_partner = 0
for p in odd_primes:
    rem = np.flatnonzero(~found)
    if len(rem) == 0:
        break
    e = evens[rem]
    ok = e - p >= 2
    hit = np.zeros(len(rem), dtype=bool)
    hit[ok] = S[e[ok] - p]
    found[rem[hit]] = True
    if hit.any():
        max_partner = int(p)
    if p > 20000 and len(rem) > 0:
        raise RuntimeError(f"partners beyond 20000 needed for {len(rem)} evens — audit")
n_fail = int((~found).sum())
print(f"Part A: {len(evens)} evens, undecomposed = {n_fail}, "
      f"max smallest odd partner = {max_partner}, {time.time()-t0:.1f}s")

# ---- Part B: stratified r(n) sample ----
rng = np.random.default_rng(20260820)
sample = []
for lo_exp in np.arange(3.0, 8.0, 0.5):
    lo, hi = int(10 ** lo_exp), min(int(10 ** (lo_exp + 0.5)), N)
    cand = rng.integers(lo // 2, hi // 2, size=120) * 2
    sample.extend(int(x) for x in cand)
sample = sorted(set(sample))

def r_count(n):
    ps = primes[primes <= n // 2]
    return int(np.count_nonzero(S[n - ps]))

def sing(n):
    prod = 1.0
    m = n
    while m % 2 == 0:
        m //= 2
    d = 3
    while d * d <= m:
        if m % d == 0:
            prod *= (d - 1) / (d - 2)
            while m % d == 0:
                m //= d
        d += 2
    if m > 1:
        prod *= (m - 1) / (m - 2)
    return prod

def hl_integral(n, steps=20000):
    # J(n) = int_2^{n-2} dt/(ln t ln(n-t)); symmetric: integrate 2..n/2, double.
    # u-substitution t = e^u (ELEN-P51 back-port of the P52 fix): the uniform-in-t
    # grid over-integrated J by +0.005%..+0.541% (1e3..1e8, reviewer-measured),
    # manufacturing the artifact's "flat 0.995" out of two cancelling errors.
    us = np.linspace(np.log(2.0), np.log(n / 2.0), steps)
    ts = np.exp(us)
    ys = ts / (np.log(ts) * np.log(n - ts))
    return 2.0 * float(np.trapezoid(ys, us))

t0 = time.time()
rows = []
for n in sample:
    obs = r_count(n)
    sg = sing(n)
    pred_shape = C2 * sg * n / math.log(n) ** 2      # unordered convention: C2 (not 2C2)
    rows.append({"n": n, "obs": obs, "sing": round(sg, 6),
                 "pred_shape": pred_shape, "J": hl_integral(n)})
print(f"Part B: {len(rows)} samples in {time.time()-t0:.1f}s")

# ratios under both conventions (factor ambiguity resolved empirically)
for row in rows:
    row["ratio_shape"] = row["obs"] / (row["pred_shape"]) if row["pred_shape"] else None
    # unordered HL prediction r(n) ~ C2*sg*J(n) (field matches its name now — the
    # old /2 made the stored value half the prediction; ELEN-P51 finding 4)
    row["pred_integral_unordered"] = C2 * row["sing"] * row["J"]
    row["ratio_integral"] = row["obs"] / row["pred_integral_unordered"]

# calibration cross-check with brute force
import sympy
def r_brute(n):
    return sum(1 for p in range(2, n // 2 + 1) if sympy.isprime(p) and sympy.isprime(n - p))
calib = {n: {"sieve": r_count(n), "brute": r_brute(n)} for n in (10, 100, 1000)}
print("calibration:", calib)

by_dec = {}
for row in rows:
    d = int(math.log10(row["n"]) * 2) / 2
    by_dec.setdefault(d, []).append(row)
summary = []
for d in sorted(by_dec):
    rs = by_dec[d]
    med_s = float(np.median([r["ratio_shape"] for r in rs]))
    med_i = float(np.median([r["ratio_integral"] for r in rs]))
    summary.append({"half_decade_log10": d, "n_samples": len(rs),
                    "median_ratio_shape": round(med_s, 4),
                    "median_ratio_integral": round(med_i, 4)})
    print(f"10^{d:>4}: shape {med_s:.4f}  integral {med_i:.4f}  (n={len(rs)})")

OUT.write_text(json.dumps({"C2_computed": C2, "part_a": {"n_evens": len(evens),
    "undecomposed": n_fail, "max_smallest_odd_partner": max_partner},
    "calibration": calib, "per_half_decade": summary,
    "sample_rows": rows[:40]}, indent=1), encoding="utf-8")
print(f"-> {OUT.name}")
