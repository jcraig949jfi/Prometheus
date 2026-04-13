#!/usr/bin/env python3
"""
Three genuinely novel explorations — none need unfolded zeros.

1. a_p compression: LZ complexity of coefficient sequences
2. Congruence graph: a_p mod ell structure (Ricci curvature)
3. Convergence rate: Sato-Tate approach rate as invariant
"""
import sys, os, json
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy.stats import spearmanr

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[3]
rng = np.random.default_rng(42)

import duckdb

print("=" * 100)
print("THREE NOVEL EXPLORATIONS")
print("=" * 100)

# Load EC data
con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
ec_data = con.execute("""
    SELECT aplist, conductor, rank, torsion, analytic_rank
    FROM elliptic_curves
    WHERE aplist IS NOT NULL AND rank IS NOT NULL AND conductor > 0
    LIMIT 10000
""").fetchall()
con.close()

primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

ec_parsed = []
for aplist_json, cond, rank, tors, ar in ec_data:
    try:
        aplist = json.loads(aplist_json) if isinstance(aplist_json, str) else aplist_json
        if isinstance(aplist, list) and len(aplist) >= 15:
            ec_parsed.append({
                "ap": [int(a) for a in aplist[:25]],
                "cond": cond, "rank": rank, "tors": tors, "ar": ar
            })
    except:
        pass

print(f"  EC with 25+ a_p: {len(ec_parsed)}\n")


# ============================================================
# 1. a_p COMPRESSION: Kolmogorov complexity proxy
# ============================================================
print("=" * 100)
print("1. a_p COMPRESSION — does information content predict rank?")
print("=" * 100)

import zlib

def lz_complexity(sequence):
    """LZ compression ratio as Kolmogorov complexity proxy."""
    s = ",".join(str(x) for x in sequence)
    compressed = zlib.compress(s.encode())
    return len(compressed) / len(s.encode())

# Compute compression ratio for each EC
compressions = []
for ec in ec_parsed:
    cr = lz_complexity(ec["ap"])
    compressions.append({
        "cr": cr, "rank": ec["rank"], "cond": ec["cond"],
        "tors": ec["tors"], "ar": ec["ar"]
    })

cr_arr = np.array([c["cr"] for c in compressions])
rank_arr = np.array([c["rank"] for c in compressions])
cond_arr = np.array([c["cond"] for c in compressions], dtype=float)
tors_arr = np.array([c["tors"] for c in compressions], dtype=float)

print(f"\n  Compression ratio stats: mean={np.mean(cr_arr):.4f}, std={np.std(cr_arr):.4f}")

# Does compression predict rank?
rho_cr_rank, p_cr = spearmanr(cr_arr, rank_arr)
print(f"  rho(compression, rank) = {rho_cr_rank:.4f} (p={p_cr:.4e})")

# Does compression predict rank BEYOND conductor?
log_cond = np.log(cond_arr)
X = np.column_stack([np.ones(len(log_cond)), log_cond])
beta_cr = np.linalg.lstsq(X, cr_arr, rcond=None)[0]
beta_rk = np.linalg.lstsq(X, rank_arr.astype(float), rcond=None)[0]
resid_cr = cr_arr - X @ beta_cr
resid_rk = rank_arr - X @ beta_rk
rho_partial, p_partial = spearmanr(resid_cr, resid_rk)
print(f"  Partial rho(compression, rank | log_cond) = {rho_partial:.4f} (p={p_partial:.4e})")

# By rank
print(f"\n  Compression by rank:")
for r in sorted(set(rank_arr)):
    mask = rank_arr == r
    if np.sum(mask) >= 10:
        print(f"    Rank {int(r)}: mean CR={np.mean(cr_arr[mask]):.4f}, n={np.sum(mask)}")

# Does compression predict torsion?
rho_cr_tors, p_tors = spearmanr(cr_arr, tors_arr)
print(f"\n  rho(compression, torsion) = {rho_cr_tors:.4f} (p={p_tors:.4e})")

if abs(rho_partial) > 0.05 and p_partial < 0.001:
    print(f"\n  SIGNAL: Compression predicts rank beyond conductor!")
    print(f"  More compressible a_p → {'lower' if rho_partial < 0 else 'higher'} rank.")
else:
    print(f"\n  No significant partial signal. Compression ≈ conductor proxy.")


# ============================================================
# 2. CONGRUENCE GRAPH: a_p mod ell structure
# ============================================================
print("\n" + "=" * 100)
print("2. CONGRUENCE GRAPH — a_p mod ell topology")
print("=" * 100)

# For ell=2: build graph where EC are connected if a_p(E1) ≡ a_p(E2) mod 2
# for ALL primes p in our list

def congruence_fingerprint(ap_list, ell):
    """Mod-ell fingerprint of a_p sequence."""
    return tuple(a % ell for a in ap_list)

for ell in [2, 3, 5]:
    fps = defaultdict(list)
    for i, ec in enumerate(ec_parsed[:5000]):
        fp = congruence_fingerprint(ec["ap"][:10], ell)  # first 10 primes
        fps[fp].append(i)

    # Graph statistics
    n_classes = len(fps)
    class_sizes = [len(v) for v in fps.values()]
    max_class = max(class_sizes)
    n_isolated = sum(1 for s in class_sizes if s == 1)

    print(f"\n  mod-{ell} congruence classes (10 primes):")
    print(f"    Classes: {n_classes}")
    print(f"    Max class size: {max_class}")
    print(f"    Isolated (singletons): {n_isolated} ({n_isolated/n_classes*100:.0f}%)")
    print(f"    Mean class size: {np.mean(class_sizes):.1f}")

    # Do congruence classes predict rank?
    class_labels = [""] * len(ec_parsed[:5000])
    for fp, indices in fps.items():
        for idx in indices:
            class_labels[idx] = str(fp)

    from battery_v2 import BatteryV2
    bv2 = BatteryV2()
    # Quick eta² check
    ranks_sub = [ec_parsed[i]["rank"] for i in range(min(5000, len(ec_parsed)))]

    groups = defaultdict(list)
    for i, cl in enumerate(class_labels):
        if cl and i < len(ranks_sub):
            groups[cl].append(ranks_sub[i])
    valid = {k: np.array(v) for k, v in groups.items() if len(v) >= 5}
    if len(valid) >= 2:
        all_v = np.concatenate(list(valid.values()))
        gm = np.mean(all_v)
        ss_t = np.sum((all_v - gm)**2)
        ss_b = sum(len(v) * (np.mean(v) - gm)**2 for v in valid.values())
        eta = ss_b / ss_t if ss_t > 0 else 0
        print(f"    eta²(mod-{ell} class → rank) = {eta:.4f}")

    # Top congruence classes by rank composition
    print(f"    Top 3 classes by size:")
    top_classes = sorted(fps.items(), key=lambda x: -len(x[1]))[:3]
    for fp, indices in top_classes:
        ranks = [ec_parsed[i]["rank"] for i in indices]
        rank_dist = Counter(ranks)
        print(f"      {fp[:5]}...: n={len(indices)}, ranks={dict(rank_dist)}")


# ============================================================
# 3. CONVERGENCE RATE: Sato-Tate approach rate
# ============================================================
print("\n" + "=" * 100)
print("3. CONVERGENCE RATE — how fast does a_p/sqrt(p) approach Sato-Tate?")
print("=" * 100)

def sato_tate_distance(ap_list, n_primes_used):
    """KS distance between empirical a_p/sqrt(p) and semicircle, using first n primes."""
    from scipy.stats import kstest
    normalized = []
    for i in range(min(n_primes_used, len(ap_list))):
        if i >= len(primes):
            break
        val = ap_list[i] / np.sqrt(primes[i])
        if abs(val) <= 2.5:
            normalized.append(val)
    if len(normalized) < 5:
        return float("nan")

    # Semicircle CDF: F(x) = (1/pi)(x*sqrt(4-x^2)/4 + arcsin(x/2) + pi/2) for x in [-2,2]
    def semicircle_cdf(x):
        x = np.clip(x, -2 + 1e-10, 2 - 1e-10)
        return (1/np.pi) * (x * np.sqrt(4 - x**2) / 4 + np.arcsin(x/2) + np.pi/2)

    norm_arr = np.array(normalized)
    # Manual KS against semicircle
    sorted_vals = np.sort(norm_arr)
    n = len(sorted_vals)
    ecdf = np.arange(1, n+1) / n
    theoretical = np.array([semicircle_cdf(x) for x in sorted_vals])
    ks = np.max(np.abs(ecdf - theoretical))
    return ks

# Compute convergence curve for each EC
print(f"\n  Computing ST convergence curves for {len(ec_parsed)} EC...")

rates = []
for ec in ec_parsed[:3000]:
    # Distance at 5, 10, 15, 20, 25 primes
    distances = []
    for n_p in [5, 10, 15, 20, 25]:
        d = sato_tate_distance(ec["ap"], n_p)
        distances.append(d)

    if all(not np.isnan(d) for d in distances):
        # Convergence rate: slope of log(distance) vs log(n_primes)
        log_n = np.log([5, 10, 15, 20, 25])
        log_d = np.log([max(d, 1e-10) for d in distances])
        # Linear fit: log(d) = alpha * log(n) + beta → d ~ n^alpha
        try:
            alpha = np.polyfit(log_n, log_d, 1)[0]
            rates.append({
                "alpha": alpha,
                "d_at_25": distances[-1],
                "rank": ec["rank"],
                "cond": ec["cond"],
                "tors": ec["tors"],
            })
        except:
            pass

print(f"  EC with convergence rates: {len(rates)}")

if rates:
    alpha_arr = np.array([r["alpha"] for r in rates])
    rank_arr = np.array([r["rank"] for r in rates])
    cond_arr = np.array([r["cond"] for r in rates], dtype=float)
    d25_arr = np.array([r["d_at_25"] for r in rates])

    print(f"  Convergence exponent alpha: mean={np.mean(alpha_arr):.4f}, std={np.std(alpha_arr):.4f}")
    print(f"  (Negative alpha = converging to ST. More negative = faster convergence.)")

    # Does convergence rate predict rank?
    rho_alpha_rank, p_alpha = spearmanr(alpha_arr, rank_arr)
    print(f"\n  rho(convergence_rate, rank) = {rho_alpha_rank:.4f} (p={p_alpha:.4e})")

    # Partial after conductor
    log_c = np.log(cond_arr)
    X = np.column_stack([np.ones(len(log_c)), log_c])
    b_a = np.linalg.lstsq(X, alpha_arr, rcond=None)[0]
    b_r = np.linalg.lstsq(X, rank_arr.astype(float), rcond=None)[0]
    r_a = alpha_arr - X @ b_a
    r_r = rank_arr - X @ b_r
    rho_partial_alpha, p_partial_alpha = spearmanr(r_a, r_r)
    print(f"  Partial rho(rate, rank | log_cond) = {rho_partial_alpha:.4f} (p={p_partial_alpha:.4e})")

    # By rank
    print(f"\n  Convergence rate by rank:")
    for r in sorted(set(rank_arr)):
        mask = rank_arr == r
        if np.sum(mask) >= 10:
            print(f"    Rank {int(r)}: mean alpha={np.mean(alpha_arr[mask]):.4f}, mean d_25={np.mean(d25_arr[mask]):.4f}, n={np.sum(mask)}")

    # The council's prediction: high-rank curves converge SLOWER
    if len(set(rank_arr)) >= 2:
        r0 = alpha_arr[rank_arr == 0]
        r1 = alpha_arr[rank_arr == 1]
        if len(r0) >= 10 and len(r1) >= 10:
            from scipy.stats import mannwhitneyu
            stat, p_mw = mannwhitneyu(r0, r1)
            print(f"\n  Rank 0 vs Rank 1 convergence:")
            print(f"    Rank 0 mean alpha: {np.mean(r0):.4f}")
            print(f"    Rank 1 mean alpha: {np.mean(r1):.4f}")
            print(f"    Mann-Whitney p: {p_mw:.4e}")
            if np.mean(r1) > np.mean(r0):
                print(f"    CONFIRMED: Higher rank → slower convergence (less negative alpha)")
            else:
                print(f"    CONTRADICTED: Higher rank → faster convergence")


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 100)
print("NOVEL EXPLORATIONS SUMMARY")
print("=" * 100)
