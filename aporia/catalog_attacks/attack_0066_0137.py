"""CAT-MATH-0066 (prime-pair counts vs HL singular series) + CAT-MATH-0137
(Agoh-Giuga full conjunction) — the authored pipeline's final two attacks.

0066: N_2k(1e8) = #{p : p, p+2k both prime}, k = 1..50, ratios N_2k/N_2 vs the
      singular series prod_{odd q | k} (q-1)/(q-2); tolerance at Poisson scale
      z = (ratio/pred - 1) / (sqrt(1/N_2k + 1/N_2)) per the reviewer's standing
      note. Targets: N_2 = 440312, max |z| = 0.84, zero rows beyond 2 sigma.
0137: composites n <= 1e7 satisfying the FULL conjunction (squarefree AND for
      every p|n: p | n/p - 1 AND p-1 | n/p - 1). Targets: zero hits; the four
      Giuga-half false alarms {30, 858, 1722, 66198} excluded, each cross-checked
      against the raw statistic sum k^(n-1) mod n.
"""
from __future__ import annotations
import json
import math
import pathlib
import time

import numpy as np

OUT = pathlib.Path(__file__).parent / "attack_0066_0137_results.json"
res = {}

# ================= 0066 =================
N = 100_000_000
t0 = time.time()
S = np.ones(N + 101, dtype=bool)
S[:2] = False
for p in range(2, int((N + 100) ** 0.5) + 1):
    if S[p]:
        S[p * p:: p] = False
primes = np.flatnonzero(S[: N + 1]).astype(np.int64)
print(f"sieve: {time.time()-t0:.1f}s")

def sing_ratio(k):
    # MISMATCH-first catch (this pass): the first draft did not strip the factor
    # 2 before the odd-prime loop, so even k with odd factors (k=6 -> should be
    # 2, gave 1) exploded z to 541 — the sing_prod landmine class ELEN deleted
    # from the old template, re-created here and caught by the reviewer target.
    prod = 1.0
    m = k
    while m % 2 == 0:
        m //= 2
    q = 3
    while q * q <= m:
        if m % q == 0:
            prod *= (q - 1) / (q - 2)
            while m % q == 0:
                m //= q
        q += 2
    if m > 1:
        prod *= (m - 1) / (m - 2)
    return prod

rows = []
N2 = None
for k in range(1, 51):
    cnt = int(np.count_nonzero(S[primes + 2 * k]))
    if k == 1:
        N2 = cnt
    rows.append({"k": k, "N_2k": cnt})
for r in rows:
    pred = sing_ratio(r["k"])
    ratio = r["N_2k"] / N2
    tol = math.sqrt(1.0 / r["N_2k"] + 1.0 / N2)
    r.update({"pred_sing": round(pred, 6), "ratio": round(ratio, 6),
              "z": round((ratio / pred - 1.0) / tol, 3)})
zs = [abs(r["z"]) for r in rows]
print(f"0066: N_2={N2}, max|z|={max(zs):.2f}, rows>2sigma={sum(1 for z in zs if z>2)}")
res["polignac_pairs"] = {"N_2": N2, "max_abs_z": max(zs),
                         "rows_beyond_2sigma": sum(1 for z in zs if z > 2),
                         "reviewer_targets": {"N_2": 440312, "max_z": 0.84, "beyond2": 0},
                         "rows": rows}

# ================= 0137 =================
t0 = time.time()
M = 10_000_000
spf = np.zeros(M + 1, dtype=np.int32)
for i in range(2, int(M ** 0.5) + 1):
    if spf[i] == 0:
        spf[i * i:: i][spf[i * i:: i] == 0] = i
hits = []
excluded_check = {}
for n in range(4, M + 1):
    if spf[n] == 0:
        continue                       # prime
    m = n
    fs = []
    sq_free = True
    while m > 1:
        p = int(spf[m]) or m
        e = 0
        while m % p == 0:
            m //= p
            e += 1
        if e > 1:
            sq_free = False
            break
        fs.append(p)
    if not sq_free:
        continue
    ok = all((n // p - 1) % p == 0 and (n // p - 1) % (p - 1) == 0 for p in fs)
    if ok:
        hits.append(n)
print(f"0137: full-conjunction hits <=1e7: {hits}  ({time.time()-t0:.0f}s)")

# false-alarm exclusion cross-check against the raw statistic
def raw_stat(n):
    return sum(pow(k, n - 1, n) for k in range(1, n)) % n
for n in (30, 858, 1722, 66198):
    m = n
    fs = []
    while m > 1:
        p = int(spf[m]) or m
        fs.append(p)
        while m % p == 0:
            m //= p
    giuga_half = all((n // p - 1) % p == 0 for p in set(fs))
    full = giuga_half and all((n // p - 1) % (p - 1) == 0 for p in set(fs))
    rs = raw_stat(n) if n <= 70000 else None
    excluded_check[n] = {"giuga_half_fires": giuga_half, "full_conjunction_fires": full,
                        "raw_stat_mod_n": rs, "required_for_counterexample": n - 1}
print("0137 false-alarm checks:", excluded_check)
res["agoh_giuga"] = {"range": "1e7", "hits": hits,
                     "false_alarm_exclusions": excluded_check,
                     "reviewer_targets": {"hits": [], "alarms_excluded": True}}

OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
print(f"-> {OUT.name}")
