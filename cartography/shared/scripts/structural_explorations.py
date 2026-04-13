#!/usr/bin/env python3
"""
Structural explorations 4-6 + improved compression (ST-weighted).

4. Spectral tail density vs isogeny class size
5. Learnability as invariant (sample efficiency of a_p mod ell prediction)
6. Cross-form sequence resonance (EC a_p vs Maass coefficients)
Plus: ST-weighted compression replacing naive LZ
"""
import sys, os, json, math
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy.stats import spearmanr

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[3]
DATA = Path(__file__).resolve().parent.parent.parent
rng = np.random.default_rng(42)

import duckdb

print("=" * 100)
print("STRUCTURAL EXPLORATIONS 4-6 + ST-WEIGHTED COMPRESSION")
print("=" * 100)

# Load EC data
con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
ec_data = con.execute("""
    SELECT aplist, conductor, rank, torsion, lmfdb_iso
    FROM elliptic_curves
    WHERE aplist IS NOT NULL AND rank IS NOT NULL AND conductor > 0
    LIMIT 10000
""").fetchall()

# Load zero data
zeros_data = con.execute("""
    SELECT object_id, zeros_vector, n_zeros_stored, analytic_rank
    FROM object_zeros WHERE n_zeros_stored >= 5
    LIMIT 5000
""").fetchall()
con.close()

primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

ec_parsed = []
for aplist_json, cond, rank, tors, iso in ec_data:
    try:
        aplist = json.loads(aplist_json) if isinstance(aplist_json, str) else aplist_json
        if isinstance(aplist, list) and len(aplist) >= 15:
            ec_parsed.append({
                "ap": [int(a) for a in aplist[:15]],
                "cond": cond, "rank": rank, "tors": tors, "iso": iso
            })
    except: pass

print(f"  EC: {len(ec_parsed)}, Zeros: {len(zeros_data)}\n")


# ============================================================
# IMPROVED: ST-weighted compression
# ============================================================
print("=" * 100)
print("IMPROVED COMPRESSION: Sato-Tate weighted information content")
print("=" * 100)

def st_surprise(ap_list, primes_list):
    """Compute total surprise (negative log-likelihood) under Sato-Tate.

    Sato-Tate density: f(x) = (2/pi) * sqrt(1 - x^2/4) for x in [-2, 2]
    where x = a_p / sqrt(p).

    Surprise = -sum(log f(a_p/sqrt(p))) over primes.
    Lower surprise = more predictable = more structured.
    """
    total_surprise = 0
    count = 0
    for i in range(min(len(ap_list), len(primes_list))):
        p = primes_list[i]
        x = ap_list[i] / math.sqrt(p)
        if abs(x) >= 2:
            total_surprise += 10  # extreme penalty for Hasse violations (shouldn't happen)
            count += 1
            continue
        # ST density
        density = (2 / math.pi) * math.sqrt(1 - x*x/4)
        if density > 0:
            total_surprise += -math.log(density)
        else:
            total_surprise += 10
        count += 1
    return total_surprise / count if count > 0 else float("nan")

surprises = []
for ec in ec_parsed:
    s = st_surprise(ec["ap"], primes)
    if not math.isnan(s):
        surprises.append({"surprise": s, "rank": ec["rank"], "cond": ec["cond"], "tors": ec["tors"]})

if surprises:
    s_arr = np.array([s["surprise"] for s in surprises])
    rank_arr = np.array([s["rank"] for s in surprises])
    cond_arr = np.array([s["cond"] for s in surprises], dtype=float)

    print(f"\n  ST-surprise: mean={np.mean(s_arr):.4f}, std={np.std(s_arr):.4f}")

    rho_s_rank, p_sr = spearmanr(s_arr, rank_arr)
    print(f"  rho(ST_surprise, rank) = {rho_s_rank:.4f} (p={p_sr:.4e})")

    # Partial after conductor
    log_c = np.log(cond_arr)
    X = np.column_stack([np.ones(len(log_c)), log_c])
    b_s = np.linalg.lstsq(X, s_arr, rcond=None)[0]
    b_r = np.linalg.lstsq(X, rank_arr.astype(float), rcond=None)[0]
    rho_partial_s, p_partial_s = spearmanr(s_arr - X @ b_s, rank_arr - X @ b_r)
    print(f"  Partial rho(surprise, rank | log_cond) = {rho_partial_s:.4f} (p={p_partial_s:.4e})")

    # By rank
    for r in sorted(set(rank_arr)):
        mask = rank_arr == r
        if np.sum(mask) >= 10:
            print(f"    Rank {int(r)}: mean surprise={np.mean(s_arr[mask]):.4f}, n={np.sum(mask)}")

    # Compare to naive LZ compression
    import zlib
    lz_arr = np.array([len(zlib.compress(",".join(str(a) for a in ec["ap"]).encode())) / len(",".join(str(a) for a in ec["ap"]).encode())
                        for ec in ec_parsed[:len(surprises)]])
    rho_lz_st, _ = spearmanr(lz_arr, s_arr)
    print(f"\n  Correlation LZ vs ST-surprise: rho={rho_lz_st:.4f}")
    print(f"  LZ captures {'most' if abs(rho_lz_st) > 0.5 else 'some' if abs(rho_lz_st) > 0.2 else 'little'} of the ST-weighted signal")


# ============================================================
# 4. SPECTRAL TAIL DENSITY vs ISOGENY CLASS SIZE
# ============================================================
print("\n" + "=" * 100)
print("4. SPECTRAL TAIL vs ISOGENY CLASS — do zeros encode algebraic network size?")
print("=" * 100)

# Count isogeny class sizes
iso_class_sizes = Counter()
for ec in ec_parsed:
    iso = ec.get("iso", "")
    if iso:
        # Extract class from label like "11.a1" -> "11.a"
        parts = iso.rsplit(".", 1)[0] if "." in iso else iso
        # Actually the iso field IS the class
        iso_class_sizes[iso] += 1

# For EC with zeros, compute first-zero height and match to isogeny class
ec_with_zeros = {}
for obj_id, zeros_json, n_zeros, ar in zeros_data:
    try:
        zlist = json.loads(zeros_json) if isinstance(zeros_json, str) else zeros_json
        if isinstance(zlist, list) and len(zlist) >= 3:
            zeros = sorted([float(z) for z in zlist if z > 0])
            if len(zeros) >= 3:
                # Spectral tail: density of zeros 2-5
                tail_gaps = np.diff(zeros[1:5]) if len(zeros) >= 5 else np.diff(zeros[1:])
                if len(tail_gaps) > 0:
                    tail_density = 1.0 / np.mean(tail_gaps)
                    ec_with_zeros[obj_id] = {
                        "z1": zeros[0], "tail_density": tail_density,
                        "n_zeros": n_zeros, "ar": ar,
                    }
    except: pass

print(f"  EC with spectral tail data: {len(ec_with_zeros)}")
print(f"  Isogeny classes: {len(iso_class_sizes)}")

# Find EC that appear in both datasets
# The object_id in zeros might not match lmfdb_iso directly
# But we can correlate by position in the sorted conductor list
# For now, just check if tail density correlates with analytic rank

if ec_with_zeros:
    td_arr = np.array([v["tail_density"] for v in ec_with_zeros.values()])
    ar_arr = np.array([v["ar"] for v in ec_with_zeros.values() if v["ar"] is not None])
    td_with_ar = np.array([v["tail_density"] for v in ec_with_zeros.values() if v["ar"] is not None])

    if len(ar_arr) >= 50:
        rho_td_ar, p_td = spearmanr(td_with_ar, ar_arr)
        print(f"  rho(tail_density, analytic_rank) = {rho_td_ar:.4f} (p={p_td:.4e})")

        for r in sorted(set(ar_arr.astype(int))):
            mask = ar_arr == r
            if np.sum(mask) >= 10:
                print(f"    Rank {r}: mean tail_density={np.mean(td_with_ar[mask]):.4f}, n={np.sum(mask)}")


# ============================================================
# 5. LEARNABILITY: Sample efficiency of a_p mod ell prediction
# ============================================================
print("\n" + "=" * 100)
print("5. LEARNABILITY — how quickly can you learn a_p mod ell from partial data?")
print("=" * 100)

# Instead of training a neural network (too heavy), use a simpler proxy:
# Given first k primes' a_p mod ell, how well does majority-class predict the (k+1)th?
# The "sample efficiency" = how quickly prediction improves with k.

for ell in [2, 3]:
    print(f"\n  mod-{ell} learnability:")

    # For each EC, compute prediction accuracy using expanding window
    accuracies_by_rank = defaultdict(list)

    for ec in ec_parsed[:3000]:
        ap_mod = [a % ell for a in ec["ap"]]
        rank = ec["rank"]

        # For each position k (5 to 14), predict a_{p_{k+1}} mod ell
        # from the frequency distribution of a_{p_1}...a_{p_k} mod ell
        correct = 0
        total = 0
        for k in range(5, min(14, len(ap_mod))):
            # Majority vote from history
            history = Counter(ap_mod[:k])
            prediction = history.most_common(1)[0][0]
            if ap_mod[k] == prediction:
                correct += 1
            total += 1

        if total > 0:
            accuracy = correct / total
            accuracies_by_rank[rank].append(accuracy)

    # Results
    print(f"    {'Rank':>6s} | {'n':>5s} | {'mean accuracy':>14s} | {'std':>8s}")
    print("    " + "-" * 40)
    all_acc = []
    all_rank = []
    for r in sorted(accuracies_by_rank.keys()):
        accs = accuracies_by_rank[r]
        if len(accs) >= 10:
            print(f"    {r:6d} | {len(accs):5d} | {np.mean(accs):14.4f} | {np.std(accs):8.4f}")
            all_acc.extend(accs)
            all_rank.extend([r] * len(accs))

    if all_acc:
        rho_learn, p_learn = spearmanr(all_acc, all_rank)
        print(f"    rho(learnability, rank) = {rho_learn:.4f} (p={p_learn:.4e})")

        if abs(rho_learn) > 0.05 and p_learn < 0.001:
            print(f"    SIGNAL: {'Higher' if rho_learn > 0 else 'Lower'} rank = {'more' if rho_learn > 0 else 'less'} predictable mod-{ell}")
        else:
            print(f"    No significant learnability-rank relationship")


# ============================================================
# 6. CROSS-FORM RESONANCE: EC a_p vs Maass coefficients
# ============================================================
print("\n" + "=" * 100)
print("6. CROSS-FORM RESONANCE — EC a_p vs Maass coefficients")
print("=" * 100)

# Load Maass coefficients
maass = json.load(open(DATA / "maass/data/maass_with_coefficients.json", encoding="utf-8"))
maass_parsed = []
for m in maass[:3000]:
    coeffs = m.get("coefficients", [])
    if len(coeffs) >= 15:
        maass_parsed.append({
            "coeffs": [float(c) for c in coeffs[:15]],
            "level": m.get("level", 0),
            "spectral": m.get("spectral_parameter", 0),
        })

print(f"  EC: {len(ec_parsed)}, Maass: {len(maass_parsed)}")

if maass_parsed:
    # Normalized cross-correlation between EC a_p and Maass coefficients
    # For each (EC, Maass) pair, compute correlation of their coefficient sequences

    # Sample 1000 random pairs
    n_pairs = 1000
    real_corrs = []
    for _ in range(n_pairs):
        i = rng.integers(len(ec_parsed))
        j = rng.integers(len(maass_parsed))
        ec_seq = np.array(ec_parsed[i]["ap"][:15], dtype=float)
        ma_seq = np.array(maass_parsed[j]["coeffs"][:15], dtype=float)
        # Normalize
        ec_norm = (ec_seq - np.mean(ec_seq)) / (np.std(ec_seq) + 1e-10)
        ma_norm = (ma_seq - np.mean(ma_seq)) / (np.std(ma_seq) + 1e-10)
        corr = np.mean(ec_norm * ma_norm)
        real_corrs.append(corr)

    real_corrs = np.array(real_corrs)

    # Null: shuffle within each sequence
    null_corrs = []
    for _ in range(n_pairs):
        i = rng.integers(len(ec_parsed))
        j = rng.integers(len(maass_parsed))
        ec_seq = np.array(ec_parsed[i]["ap"][:15], dtype=float)
        ma_seq = np.array(maass_parsed[j]["coeffs"][:15], dtype=float)
        rng.shuffle(ec_seq)
        rng.shuffle(ma_seq)
        ec_norm = (ec_seq - np.mean(ec_seq)) / (np.std(ec_seq) + 1e-10)
        ma_norm = (ma_seq - np.mean(ma_seq)) / (np.std(ma_seq) + 1e-10)
        null_corrs.append(np.mean(ec_norm * ma_norm))

    null_corrs = np.array(null_corrs)

    print(f"\n  Random EC-Maass coefficient correlations (1000 pairs):")
    print(f"    Real:   mean={np.mean(real_corrs):.4f}, std={np.std(real_corrs):.4f}")
    print(f"    Null:   mean={np.mean(null_corrs):.4f}, std={np.std(null_corrs):.4f}")
    z_res = (np.mean(real_corrs) - np.mean(null_corrs)) / np.std(null_corrs) if np.std(null_corrs) > 0 else 0
    print(f"    z-score: {z_res:.1f}")

    # Tail analysis: are there anomalous high-correlation pairs?
    high_corr = np.sum(np.abs(real_corrs) > 0.5)
    high_null = np.sum(np.abs(null_corrs) > 0.5)
    print(f"\n    |corr| > 0.5: real={high_corr}, null={high_null}")
    print(f"    |corr| > 0.7: real={np.sum(np.abs(real_corrs) > 0.7)}, null={np.sum(np.abs(null_corrs) > 0.7)}")

    if z_res > 3:
        print(f"\n    SIGNAL: EC-Maass coefficient sequences show above-null resonance")
    elif high_corr > high_null * 2:
        print(f"\n    TAIL SIGNAL: Excess high-correlation pairs (not bulk mean)")
    else:
        print(f"\n    No resonance detected. Coefficient sequences are independent.")


# ============================================================
print("\n" + "=" * 100)
print("STRUCTURAL EXPLORATIONS SUMMARY")
print("=" * 100)
