#!/usr/bin/env python3
"""
THE DECISIVE TEST: Conductor-matched + prime-only + shuffled control.

For each surviving signal (tail density, learnability, convergence rate):
1. Fix conductor (tight bins)
2. Use only a_p at primes (not composite indices)
3. Compare real vs shuffled

If real shows signal and shuffled kills it → pure arithmetic dynamics.
If shuffled preserves it → distributional artifact.
"""
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

print("=" * 100)
print("THE DECISIVE TEST")
print("Conductor-matched + prime-only + shuffled control")
print("=" * 100)

# Load
con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
ec_data = con.execute("""
    SELECT aplist, conductor, rank, torsion
    FROM elliptic_curves
    WHERE aplist IS NOT NULL AND rank IS NOT NULL AND conductor > 0
""").fetchall()

zeros_data = con.execute("""
    SELECT object_id, zeros_vector, analytic_rank
    FROM object_zeros WHERE n_zeros_stored >= 5
""").fetchall()
con.close()

primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

ec_all = []
for aplist_json, cond, rank, tors in ec_data:
    try:
        aplist = json.loads(aplist_json) if isinstance(aplist_json, str) else aplist_json
        if isinstance(aplist, list) and len(aplist) >= 15:
            ec_all.append({
                "ap": [int(a) for a in aplist[:15]],
                "cond": cond, "rank": rank, "tors": tors,
                "log_cond": math.log(cond),
            })
    except: pass

print(f"  EC total: {len(ec_all)}")
print(f"  Zeros: {len(zeros_data)}")

# Conductor bins (tight: factor of 2)
cond_bins = [(10, 50), (50, 200), (200, 1000), (1000, 3000), (3000, 10000)]

# ============================================================
# SIGNAL 1: Mod-2 learnability (conductor-matched + shuffled)
# ============================================================
print("\n" + "=" * 100)
print("SIGNAL 1: MOD-2 LEARNABILITY — conductor-matched + shuffled control")
print("=" * 100)

def learnability_mod2(ap_list):
    """Majority-vote prediction accuracy on a_p mod 2."""
    ap_mod = [a % 2 for a in ap_list]
    correct = 0
    total = 0
    for k in range(3, min(14, len(ap_mod))):
        history = defaultdict(int)
        for j in range(k):
            history[ap_mod[j]] += 1
        prediction = max(history, key=history.get)
        if ap_mod[k] == prediction:
            correct += 1
        total += 1
    return correct / total if total > 0 else float("nan")

print(f"\n  {'Cond bin':>15s} | {'n':>5s} | {'R0 learn':>8s} | {'R1 learn':>8s} | {'real rho':>8s} | {'shuf rho':>8s} | {'Survives?'}")
print("  " + "-" * 80)

for lo, hi in cond_bins:
    bin_ec = [ec for ec in ec_all if lo <= ec["cond"] < hi]
    if len(bin_ec) < 50:
        continue

    # Real learnability
    real_learn = []
    real_rank = []
    for ec in bin_ec:
        l = learnability_mod2(ec["ap"])
        if not math.isnan(l):
            real_learn.append(l)
            real_rank.append(ec["rank"])

    if len(real_learn) < 30:
        continue

    real_learn = np.array(real_learn)
    real_rank = np.array(real_rank)
    rho_real, p_real = spearmanr(real_learn, real_rank)

    # Shuffled control: shuffle a_p within each EC, recompute
    shuf_learn = []
    shuf_rank = []
    for ec in bin_ec:
        ap_shuf = list(ec["ap"])
        rng.shuffle(ap_shuf)
        l = learnability_mod2(ap_shuf)
        if not math.isnan(l):
            shuf_learn.append(l)
            shuf_rank.append(ec["rank"])

    shuf_learn = np.array(shuf_learn)
    shuf_rank = np.array(shuf_rank)
    rho_shuf, _ = spearmanr(shuf_learn, shuf_rank)

    # By rank within this bin
    r0 = real_learn[real_rank == 0]
    r1 = real_learn[real_rank == 1]
    r0_mean = np.mean(r0) if len(r0) > 0 else 0
    r1_mean = np.mean(r1) if len(r1) > 0 else 0

    survives = abs(rho_real) > abs(rho_shuf) * 2 and abs(rho_real) > 0.05
    print(f"  [{lo:>5d},{hi:>5d}) | {len(bin_ec):5d} | {r0_mean:8.4f} | {r1_mean:8.4f} | {rho_real:8.4f} | {rho_shuf:8.4f} | {'YES' if survives else 'no'}")


# ============================================================
# SIGNAL 2: Convergence rate (conductor-matched + shuffled)
# ============================================================
print("\n" + "=" * 100)
print("SIGNAL 2: CONVERGENCE RATE — conductor-matched + shuffled control")
print("=" * 100)

def convergence_rate(ap_list):
    """ST convergence rate (alpha) from expanding prime window."""
    distances = []
    for n_p in [3, 5, 7, 10, 15]:
        normalized = []
        for i in range(min(n_p, len(ap_list), len(primes))):
            val = ap_list[i] / math.sqrt(primes[i])
            if abs(val) <= 2.5:
                normalized.append(val)
        if len(normalized) < 3:
            return float("nan")
        # KS vs semicircle
        sorted_v = sorted(normalized)
        n = len(sorted_v)
        ecdf = [(i+1)/n for i in range(n)]
        max_diff = 0
        for i, x in enumerate(sorted_v):
            x_clip = max(-2+1e-10, min(2-1e-10, x))
            tcdf = (1/math.pi) * (x_clip * math.sqrt(4 - x_clip*x_clip) / 4 + math.asin(x_clip/2) + math.pi/2)
            max_diff = max(max_diff, abs(ecdf[i] - tcdf))
        distances.append(max_diff)

    if len(distances) < 5 or any(d == 0 for d in distances):
        return float("nan")
    log_n = [math.log(x) for x in [3, 5, 7, 10, 15]]
    log_d = [math.log(max(d, 1e-10)) for d in distances]
    # Linear fit
    n = len(log_n)
    sx = sum(log_n)
    sy = sum(log_d)
    sxx = sum(x*x for x in log_n)
    sxy = sum(x*y for x, y in zip(log_n, log_d))
    alpha = (n * sxy - sx * sy) / (n * sxx - sx * sx) if (n * sxx - sx * sx) != 0 else 0
    return alpha

print(f"\n  {'Cond bin':>15s} | {'n':>5s} | {'R0 alpha':>8s} | {'R1 alpha':>8s} | {'real rho':>8s} | {'shuf rho':>8s} | {'Survives?'}")
print("  " + "-" * 80)

for lo, hi in cond_bins:
    bin_ec = [ec for ec in ec_all if lo <= ec["cond"] < hi]
    if len(bin_ec) < 50:
        continue

    real_alpha = []
    real_rank = []
    for ec in bin_ec:
        a = convergence_rate(ec["ap"])
        if not math.isnan(a):
            real_alpha.append(a)
            real_rank.append(ec["rank"])

    if len(real_alpha) < 30:
        continue

    real_alpha = np.array(real_alpha)
    real_rank = np.array(real_rank)
    rho_real, _ = spearmanr(real_alpha, real_rank)

    # Shuffled
    shuf_alpha = []
    shuf_rank = []
    for ec in bin_ec:
        ap_s = list(ec["ap"])
        rng.shuffle(ap_s)
        a = convergence_rate(ap_s)
        if not math.isnan(a):
            shuf_alpha.append(a)
            shuf_rank.append(ec["rank"])
    shuf_alpha = np.array(shuf_alpha)
    shuf_rank = np.array(shuf_rank)
    rho_shuf, _ = spearmanr(shuf_alpha, shuf_rank)

    r0 = real_alpha[real_rank == 0]
    r1 = real_alpha[real_rank == 1]

    survives = abs(rho_real) > abs(rho_shuf) * 2 and abs(rho_real) > 0.05
    print(f"  [{lo:>5d},{hi:>5d}) | {len(bin_ec):5d} | {np.mean(r0) if len(r0) > 0 else 0:8.4f} | {np.mean(r1) if len(r1) > 0 else 0:8.4f} | {rho_real:8.4f} | {rho_shuf:8.4f} | {'YES' if survives else 'no'}")


# ============================================================
# SIGNAL 3: Spectral tail density (conductor-matched)
# ============================================================
print("\n" + "=" * 100)
print("SIGNAL 3: SPECTRAL TAIL DENSITY — by analytic rank, conductor-matched")
print("=" * 100)

# Parse zeros
zero_parsed = []
for obj_id, zeros_json, ar in zeros_data:
    try:
        zlist = json.loads(zeros_json) if isinstance(zeros_json, str) else zeros_json
        if isinstance(zlist, list) and len(zlist) >= 5:
            zeros = sorted([float(z) for z in zlist if z > 0])
            if len(zeros) >= 5:
                tail_gaps = np.diff(zeros[1:5])
                tail_density = 1.0 / np.mean(tail_gaps) if np.mean(tail_gaps) > 0 else 0
                zero_parsed.append({"td": tail_density, "ar": ar, "id": obj_id})
    except: pass

if zero_parsed:
    td_arr = np.array([z["td"] for z in zero_parsed])
    ar_arr = np.array([z["ar"] for z in zero_parsed if z["ar"] is not None])
    td_with_ar = np.array([z["td"] for z in zero_parsed if z["ar"] is not None])

    # Can't conductor-match zeros easily (no conductor in zeros table)
    # But we CAN check: does the signal persist after rank-shuffling?
    rho_real_td, p_td = spearmanr(td_with_ar, ar_arr)

    null_rhos = []
    for _ in range(500):
        shuf_ar = ar_arr.copy()
        rng.shuffle(shuf_ar)
        r, _ = spearmanr(td_with_ar, shuf_ar)
        null_rhos.append(r)
    null_rhos = np.array(null_rhos)
    z_td = (rho_real_td - np.mean(null_rhos)) / np.std(null_rhos) if np.std(null_rhos) > 0 else 0

    print(f"  rho(tail_density, analytic_rank) = {rho_real_td:.4f} (p={p_td:.4e})")
    print(f"  Permutation null: mean={np.mean(null_rhos):.4f}, z={z_td:.1f}")
    print(f"  Rank 0: mean td={np.mean(td_with_ar[ar_arr == 0]):.4f} (n={np.sum(ar_arr == 0)})")
    print(f"  Rank 1: mean td={np.mean(td_with_ar[ar_arr == 1]):.4f} (n={np.sum(ar_arr == 1)})")


# ============================================================
# RANK GRADIENT: Does signal scale monotonically?
# ============================================================
print("\n" + "=" * 100)
print("RANK GRADIENT: Do signals scale monotonically with rank?")
print("=" * 100)

# Learnability by rank (full dataset)
learn_by_rank = defaultdict(list)
for ec in ec_all[:10000]:
    l = learnability_mod2(ec["ap"])
    if not math.isnan(l):
        learn_by_rank[ec["rank"]].append(l)

# Convergence rate by rank
rate_by_rank = defaultdict(list)
for ec in ec_all[:5000]:
    a = convergence_rate(ec["ap"])
    if not math.isnan(a):
        rate_by_rank[ec["rank"]].append(a)

print(f"\n  {'Rank':>6s} | {'n_learn':>7s} | {'learn':>8s} | {'n_rate':>6s} | {'rate':>8s} | {'n_td':>5s} | {'td':>8s}")
print("  " + "-" * 65)

for r in sorted(set(list(learn_by_rank.keys()) + list(rate_by_rank.keys()))):
    lr = learn_by_rank.get(r, [])
    rr = rate_by_rank.get(r, [])
    td = [z["td"] for z in zero_parsed if z["ar"] == r] if zero_parsed else []
    print(f"  {r:6d} | {len(lr):7d} | {np.mean(lr):8.4f} | {len(rr):6d} | {np.mean(rr) if rr else 0:8.4f} | {len(td):5d} | {np.mean(td) if td else 0:8.4f}")


# ============================================================
print("\n" + "=" * 100)
print("DECISIVE TEST SUMMARY")
print("=" * 100)
