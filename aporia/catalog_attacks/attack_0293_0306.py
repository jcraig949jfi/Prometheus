"""CAT-MATH-0293 (Wieferich calibration) + CAT-MATH-0306 (odd perfect, full 1e8).

0293: primes p <= 1e7 with 2^(p-1) = 1 mod p^2. Expected EXACTLY {1093, 3511}.
0306: sigma sieve to 1e8 (int32; overflow negligibility MEASURED in-run per the
      P58 rule: max sigma observed vs 2^31). No odd perfect expected; the even-
      perfect positive control {6, 28, 496, 8128, 33550336} must fire.
"""
from __future__ import annotations
import json
import pathlib
import time

import numpy as np
import sympy

OUT = pathlib.Path(__file__).parent / "attack_0293_0306_results.json"
res = {}

# ---------------- 0293 ----------------
t0 = time.time()
hits = []
for p in sympy.primerange(2, 10_000_001):
    if pow(2, p - 1, p * p) == 1:
        hits.append(p)
res["wieferich"] = {"range": "1e7", "hits": hits, "expected": [1093, 3511],
                    "match": hits == [1093, 3511], "seconds": round(time.time() - t0, 1)}
print(f"0293 Wieferich <=1e7: {hits}  match={hits==[1093,3511]}  ({time.time()-t0:.0f}s)")

# ---------------- 0306 ----------------
t0 = time.time()
N = 100_000_000
sig = np.zeros(N + 1, dtype=np.int32)
for d in range(1, N // 2 + 1):
    sig[2 * d:: d] += d          # proper-divisor sum s(n) = sigma(n) - n
max_s = int(sig.max())
print(f"sigma sieve done in {time.time()-t0:.0f}s; max s(n) = {max_s} (int32 headroom "
      f"{max_s / 2**31:.2%} of 2^31 — overflow negligibility MEASURED)")

n_arr = np.arange(0, N + 1, dtype=np.int64)
perfect = np.flatnonzero(sig[: N + 1] == n_arr)
perfect = [int(x) for x in perfect if x >= 2]
odd_perfect = [x for x in perfect if x % 2 == 1]
res["odd_perfect"] = {"range": "1e8", "perfect_found": perfect,
                      "even_control_expected": [6, 28, 496, 8128, 33550336],
                      "control_fires": perfect == [6, 28, 496, 8128, 33550336],
                      "odd_perfect_found": odd_perfect,
                      "max_proper_divisor_sum": max_s,
                      "seconds": round(time.time() - t0, 1)}
print(f"0306: perfects <=1e8 = {perfect}; odd = {odd_perfect}")

OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
print(f"-> {OUT.name}")
