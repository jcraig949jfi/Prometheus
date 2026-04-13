#!/usr/bin/env python3
"""Kill the last survivor: convergence rate signal. 3 lethal attacks."""
import sys, os, json, math
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy.stats import spearmanr, mannwhitneyu
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[3]
rng = np.random.default_rng(42)
import duckdb

primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]

con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
ec_data = con.execute("""SELECT aplist, conductor, rank, cm FROM elliptic_curves
    WHERE aplist IS NOT NULL AND rank IS NOT NULL AND conductor BETWEEN 100 AND 5000 LIMIT 10000""").fetchall()
con.close()

ec_all = []
for aplist_json, cond, rank, cm in ec_data:
    try:
        aplist = json.loads(aplist_json) if isinstance(aplist_json, str) else aplist_json
        if isinstance(aplist, list) and len(aplist) >= 15:
            ec_all.append({"ap": [int(a) for a in aplist[:min(25, len(aplist))]], "cond": cond, "rank": rank, "cm": cm or 0})
    except: pass
print(f"EC: {len(ec_all)} (conductor 100-5000)")

def convergence_rate(ap_list, prime_list, start=0, end=None):
    if end is None: end = len(prime_list)
    distances = []
    for n_p in [max(3, start+2), max(5, start+3), max(7, start+4), max(10, start+5), min(15, end)]:
        if n_p <= start: continue
        normalized = []
        for i in range(start, min(n_p, len(ap_list), len(prime_list))):
            val = ap_list[i] / math.sqrt(prime_list[i])
            if abs(val) <= 2.5: normalized.append(val)
        if len(normalized) < 3: continue
        sorted_v = sorted(normalized)
        n = len(sorted_v)
        ecdf = [(j+1)/n for j in range(n)]
        max_diff = 0
        for j, x in enumerate(sorted_v):
            xc = max(-1.999, min(1.999, x))
            tcdf = (1/math.pi) * (xc * math.sqrt(4 - xc*xc) / 4 + math.asin(xc/2) + math.pi/2)
            max_diff = max(max_diff, abs(ecdf[j] - tcdf))
        distances.append(max_diff)
    if len(distances) < 3: return float("nan")
    log_n = [math.log(i+3) for i in range(len(distances))]
    log_d = [math.log(max(d, 1e-10)) for d in distances]
    n = len(log_n)
    sx, sy = sum(log_n), sum(log_d)
    sxx = sum(x*x for x in log_n)
    sxy = sum(x*y for x, y in zip(log_n, log_d))
    denom = n * sxx - sx * sx
    return (n * sxy - sx * sy) / denom if denom != 0 else 0

def test_signal(ec_list, label, prime_list=None):
    if prime_list is None: prime_list = primes
    rates, ranks = [], []
    for ec in ec_list:
        a = convergence_rate(ec["ap"], prime_list)
        if not math.isnan(a):
            rates.append(a)
            ranks.append(ec["rank"])
    if len(rates) < 50: return None, None, None
    rates, ranks = np.array(rates), np.array(ranks)
    rho, p = spearmanr(rates, ranks)
    r0 = rates[ranks == 0]
    r1 = rates[ranks == 1]
    mw_p = mannwhitneyu(r0, r1).pvalue if len(r0) > 10 and len(r1) > 10 else 1.0
    print(f"  {label:40s}: rho={rho:+.4f} (p={p:.2e}), R0={np.mean(r0):.4f} R1={np.mean(r1):.4f}, MW p={mw_p:.2e}, n={len(rates)}")
    return rho, p, mw_p

# BASELINE
print("\n" + "=" * 80)
print("BASELINE: Real signal")
print("=" * 80)
test_signal(ec_all, "Real (all primes)")

# ATTACK 1: Prime reindexing
print("\n" + "=" * 80)
print("ATTACK 1: PRIME REINDEXING — keep values, shuffle prime assignment")
print("=" * 80)
for trial in range(3):
    shuffled_primes = list(primes[:15])
    rng.shuffle(shuffled_primes)
    test_signal(ec_all, f"Reindexed primes (trial {trial})", shuffled_primes)

# Also: assign to WRONG primes (shift by offset)
for offset in [1, 3, 5]:
    shifted = primes[offset:offset+15]
    test_signal(ec_all, f"Shifted primes (offset {offset})", shifted)

# ATTACK 2: Low-prime ablation
print("\n" + "=" * 80)
print("ATTACK 2: LOW-PRIME ABLATION — remove first k primes")
print("=" * 80)

for skip in [0, 2, 4, 6, 8]:
    # Use primes starting from index skip
    def rate_skip(ec):
        ap_sub = ec["ap"][skip:]
        p_sub = primes[skip:skip+len(ap_sub)]
        return convergence_rate(ap_sub, p_sub)

    rates, ranks = [], []
    for ec in ec_all:
        a = rate_skip(ec)
        if not math.isnan(a):
            rates.append(a); ranks.append(ec["rank"])
    if len(rates) >= 50:
        rates, ranks = np.array(rates), np.array(ranks)
        rho, p = spearmanr(rates, ranks)
        print(f"  Skip first {skip} primes (start at p={primes[skip]}): rho={rho:+.4f} (p={p:.2e}), n={len(rates)}")

# ATTACK 3: CM vs non-CM split
print("\n" + "=" * 80)
print("ATTACK 3: CM vs NON-CM — does signal exist in both?")
print("=" * 80)

cm_curves = [ec for ec in ec_all if ec["cm"] != 0]
non_cm = [ec for ec in ec_all if ec["cm"] == 0]
print(f"  CM curves: {len(cm_curves)}, non-CM: {len(non_cm)}")

test_signal(non_cm, "Non-CM only")
if len(cm_curves) >= 50:
    test_signal(cm_curves, "CM only")
else:
    print(f"  CM: too few ({len(cm_curves)}) for reliable test")

# ATTACK 4: Shuffled a_p control (within conductor bin)
print("\n" + "=" * 80)
print("ATTACK 4: SHUFFLED a_p — does order matter?")
print("=" * 80)

shuffled_ec = []
for ec in ec_all:
    ap_s = list(ec["ap"])
    rng.shuffle(ap_s)
    shuffled_ec.append({"ap": ap_s, "cond": ec["cond"], "rank": ec["rank"], "cm": ec["cm"]})
test_signal(shuffled_ec, "Shuffled a_p (full shuffle)")

# Block shuffle: preserve pairs but shuffle blocks
block_ec = []
for ec in ec_all:
    ap = list(ec["ap"])
    # Shuffle in blocks of 3
    blocks = [ap[i:i+3] for i in range(0, len(ap), 3)]
    rng.shuffle(blocks)
    block_ec.append({"ap": [a for b in blocks for a in b][:len(ap)], "cond": ec["cond"], "rank": ec["rank"], "cm": ec["cm"]})
test_signal(block_ec, "Block-shuffled (blocks of 3)")

# ATTACK 5: Conductor scaling
print("\n" + "=" * 80)
print("ATTACK 5: CONDUCTOR SCALING — how does signal decay?")
print("=" * 80)

bins = [(100, 300), (300, 700), (700, 1500), (1500, 3000), (3000, 5000)]
for lo, hi in bins:
    subset = [ec for ec in ec_all if lo <= ec["cond"] < hi]
    if len(subset) >= 100:
        test_signal(subset, f"Conductor [{lo}-{hi})")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
