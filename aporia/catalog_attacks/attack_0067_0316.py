"""CAT-MATH-0067 (Artin primitive-root density, base 2) + CAT-MATH-0316 (amicable pairs).

0067: fraction of primes p <= 1e8 with 2 a primitive root, per decade, vs the Artin
      constant A = prod_p (1 - 1/(p(p-1))) COMPUTED from its product (no memory).
      ord test via smallest-prime-factor sieve on p-1 + modpow per prime factor.
      Reviewer target: density 0.373908 at 1e7.
0316: amicable pairs under BOTH conventions with smaller member a <= 1e7:
      standard (count by smaller member; reviewer: ~108) and both-bounded
      (a<b<=1e7; reviewer: 100; delta = exactly 8 boundary pairs). Partner range
      headroom MEASURED: max s(a) for a<=1e7 must sit inside the 1e8 sieve.
"""
from __future__ import annotations
import json
import pathlib
import time

import numpy as np

OUT = pathlib.Path(__file__).parent / "attack_0067_0316_results.json"
res = {}
N = 100_000_000

# ---- shared: smallest-prime-factor sieve to 1e8 ----
t0 = time.time()
spf = np.zeros(N + 1, dtype=np.int32)
for i in range(2, int(N ** 0.5) + 1):
    if spf[i] == 0:
        spf[i * i:: i][spf[i * i:: i] == 0] = i
print(f"spf sieve: {time.time()-t0:.0f}s")

def factors(m):
    fs = set()
    while m > 1:
        p = int(spf[m]) or m
        fs.add(p)
        while m % p == 0:
            m //= p
    return fs

# ---- 0067 ----
t0 = time.time()
primes_mask = spf[: N + 1] == 0
primes_mask[:2] = False
primes = np.flatnonzero(primes_mask).astype(np.int64)
print(f"primes: {len(primes)}")

# Artin constant from its product over primes to 1e7
pp = primes[primes <= 10_000_000].astype(np.float64)
A = float(np.exp(np.sum(np.log1p(-1.0 / (pp * (pp - 1.0))))))
print(f"Artin constant computed = {A:.10f}")

decades = {k: [0, 0] for k in range(1, 9)}   # decade -> [prim_root_count, prime_count]
t1 = time.time()
for p in primes[1:]:                          # skip p=2
    p = int(p)
    m = p - 1
    ok = True
    for q in factors(m):
        if pow(2, m // q, p) == 1:
            ok = False
            break
    d = min(max(len(str(p)), 1), 8)   # digit count: 7-digit primes -> upto-1e7 bucket
                                      # (first run had len-1, shifting every label a decade)
    decades[d][1] += 1
    if ok:
        decades[d][0] += 1
print(f"ord sweep: {time.time()-t1:.0f}s")

cum_pr = cum_pp = 0
per_dec = []
for k in range(1, 9):
    cum_pr += decades[k][0]; cum_pp += decades[k][1]
    if cum_pp:
        per_dec.append({"upto": 10 ** k, "density": round(cum_pr / cum_pp, 6),
                        "ratio_to_A": round(cum_pr / cum_pp / A, 5)})
print("0067 per-decade cumulative:", per_dec[-4:])
res["artin"] = {"A_computed": A, "per_decade_cumulative": per_dec,
                "reviewer_target_1e7": 0.373908}

# ---- 0316 ----
t0 = time.time()
sig = np.zeros(N + 1, dtype=np.int32)
for d in range(1, N // 2 + 1):
    sig[2 * d:: d] += d
X = 10_000_000
max_partner = int(sig[2: X + 1].max())
print(f"sigma sieve: {time.time()-t0:.0f}s; max s(a) for a<=1e7 = {max_partner} "
      f"({'INSIDE' if max_partner <= N else 'OUTSIDE'} the 1e8 sieve — headroom measured)")

pairs = []
for a in range(2, X + 1):
    b = int(sig[a])
    if b > a and b <= N and int(sig[b]) == a:
        pairs.append((a, b))
std_count = len(pairs)                              # smaller member <= 1e7
both_bounded = sum(1 for a, b in pairs if b <= X)   # both members <= 1e7
boundary = [(a, b) for a, b in pairs if b > X]
print(f"0316: standard (smaller<=1e7) = {std_count}; both-bounded = {both_bounded}; "
      f"boundary pairs = {len(boundary)}")
res["amicable"] = {"X": X, "standard_count": std_count, "both_bounded_count": both_bounded,
                   "boundary_pairs": boundary, "max_partner": max_partner,
                   "reviewer": {"standard": "~108", "both_bounded": 100, "boundary": 8}}

OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
print(f"-> {OUT.name}")
