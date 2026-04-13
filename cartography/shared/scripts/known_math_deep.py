#!/usr/bin/env python3
"""
Deep tests on 4 known mathematical theorems using data we already have.
These serve as calibration points for the precision-fixed TT-Cross metric.

1. Modularity: a_p(EC) = a_p(MF) coefficient-level agreement
2. Sato-Tate: a_p/sqrt(p) follows semicircle for non-CM EC
3. Montgomery-Odlyzko: EC zero spacing → GUE statistics
4. Analytic CNF: h*R/(w*sqrt(d)) convergence by degree (Brauer-Siegel)
"""
import sys, os, json
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy.stats import ks_2samp, spearmanr

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[3]
DATA = Path(__file__).resolve().parent.parent.parent
rng = np.random.default_rng(42)

import duckdb

print("=" * 100)
print("KNOWN MATHEMATICS DEEP CALIBRATION")
print("These are the ground truths for the precision-fixed metric.")
print("=" * 100)

# ============================================================
# 1. MODULARITY: a_p(EC) = a_p(MF) at matching conductor/level
# ============================================================
print("\n" + "=" * 100)
print("1. MODULARITY: Do a_p coefficients match between EC and MF?")
print("=" * 100)

con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)

# Get EC with a_p data
ec_ap = con.execute("""
    SELECT conductor, aplist, lmfdb_iso, cm
    FROM elliptic_curves
    WHERE aplist IS NOT NULL AND conductor > 0
    LIMIT 2000
""").fetchall()

# Get MF with a_p data
mf_ap = con.execute("""
    SELECT level, ap_coeffs, lmfdb_label, weight
    FROM modular_forms
    WHERE ap_coeffs IS NOT NULL AND weight = 2 AND level > 0
    LIMIT 5000
""").fetchall()

con.close()

print(f"  EC with a_p: {len(ec_ap)}")
print(f"  Weight-2 MF with a_p: {len(mf_ap)}")

# Build MF lookup by level
mf_by_level = defaultdict(list)
for level, ap_json, label, weight in mf_ap:
    try:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        if isinstance(ap, dict):
            mf_by_level[level].append({"label": label, "ap": ap})
    except:
        pass

# For each EC, find matching MF at same level and compare a_p
matched = 0
perfect = 0
distances = []
random_distances = []

primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]

for cond, aplist, iso, cm in ec_ap[:500]:
    if cond not in mf_by_level:
        continue

    # Parse EC a_p
    try:
        ec_coeffs = json.loads(aplist) if isinstance(aplist, str) else aplist
        if not isinstance(ec_coeffs, list) or len(ec_coeffs) < 5:
            continue
    except:
        continue

    # Compare to each MF at this level
    best_dist = float("inf")
    for mf in mf_by_level[cond]:
        mf_coeffs = mf["ap"]
        # Compute distance: sum of |a_p(EC) - a_p(MF)|^2 over shared primes
        dist = 0
        count = 0
        for i, p in enumerate(primes):
            ec_val = ec_coeffs[i] if i < len(ec_coeffs) else None
            mf_val = mf_coeffs.get(str(p), None)
            if ec_val is not None and mf_val is not None:
                dist += (ec_val - mf_val) ** 2
                count += 1
        if count >= 3:
            dist = np.sqrt(dist / count)
            best_dist = min(best_dist, dist)

    if best_dist < float("inf"):
        matched += 1
        distances.append(best_dist)
        if best_dist < 0.01:
            perfect += 1

        # Random baseline: distance to a random MF
        all_mf = list(mf_by_level.values())
        if all_mf:
            random_mf = rng.choice(all_mf[rng.integers(len(all_mf))])
            mf_coeffs = random_mf["ap"]
            dist_r = 0
            count_r = 0
            for i, p in enumerate(primes):
                ec_val = ec_coeffs[i] if i < len(ec_coeffs) else None
                mf_val = mf_coeffs.get(str(p), None)
                if ec_val is not None and mf_val is not None:
                    dist_r += (ec_val - mf_val) ** 2
                    count_r += 1
            if count_r >= 3:
                random_distances.append(np.sqrt(dist_r / count_r))

print(f"\n  Matched (EC has MF at same level): {matched}")
print(f"  Perfect match (dist < 0.01): {perfect} ({perfect/matched*100:.1f}%)" if matched > 0 else "")
print(f"  Mean matched distance: {np.mean(distances):.4f}" if distances else "")
print(f"  Mean random distance: {np.mean(random_distances):.4f}" if random_distances else "")
if distances and random_distances:
    print(f"  Separation ratio: {np.mean(random_distances)/np.mean(distances):.1f}x")


# ============================================================
# 2. SATO-TATE: a_p/sqrt(p) follows semicircle for non-CM
# ============================================================
print("\n" + "=" * 100)
print("2. SATO-TATE: a_p/sqrt(p) distribution for non-CM vs CM curves")
print("=" * 100)

con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
ec_st = con.execute("""
    SELECT aplist, cm FROM elliptic_curves
    WHERE aplist IS NOT NULL LIMIT 5000
""").fetchall()
con.close()

non_cm_normalized = []
cm_normalized = []

for aplist, cm_val in ec_st:
    try:
        coeffs = json.loads(aplist) if isinstance(aplist, str) else aplist
        if not isinstance(coeffs, list) or len(coeffs) < 5:
            continue
    except:
        continue

    # Normalize: a_p / sqrt(p) for small primes
    for i, p in enumerate(primes):
        if i < len(coeffs):
            normalized = coeffs[i] / np.sqrt(p)
            if abs(normalized) <= 2.5:  # filter outliers
                if cm_val == 0:
                    non_cm_normalized.append(normalized)
                else:
                    cm_normalized.append(normalized)

print(f"  Non-CM normalized a_p/sqrt(p): {len(non_cm_normalized)} values")
print(f"  CM normalized a_p/sqrt(p): {len(cm_normalized)} values")

# Sato-Tate semicircle CDF: F(x) = (1/pi) * (x*sqrt(4-x^2)/4 + arcsin(x/2) + pi/2)
def semicircle_cdf(x):
    x = np.clip(x, -2, 2)
    return (1/np.pi) * (x * np.sqrt(4 - x**2) / 4 + np.arcsin(x/2) + np.pi/2)

if non_cm_normalized:
    # KS test vs semicircle
    non_cm_arr = np.array(non_cm_normalized)
    ks_nonCM, p_nonCM = ks_2samp(non_cm_arr, rng.choice(np.linspace(-2, 2, 10000),
                                   size=len(non_cm_arr), p=np.diff(np.concatenate([[0], semicircle_cdf(np.linspace(-2, 2, 10000))]))))
    # Simpler: compare moments to semicircle theory
    # Semicircle: mean=0, var=1, skew=0, kurt=2 (excess kurt = -1)
    mean_nc = np.mean(non_cm_arr)
    var_nc = np.var(non_cm_arr)
    skew_nc = np.mean(((non_cm_arr - mean_nc) / np.std(non_cm_arr))**3)
    kurt_nc = np.mean(((non_cm_arr - mean_nc) / np.std(non_cm_arr))**4)

    print(f"\n  Non-CM moment analysis (Sato-Tate predicts: mean=0, var=1, skew=0, kurt=2):")
    print(f"    Mean: {mean_nc:.4f} (expect 0)")
    print(f"    Var:  {var_nc:.4f} (expect 1)")
    print(f"    Skew: {skew_nc:.4f} (expect 0)")
    print(f"    Kurt: {kurt_nc:.4f} (expect 2)")

if cm_normalized:
    cm_arr = np.array(cm_normalized)
    mean_cm = np.mean(cm_arr)
    var_cm = np.var(cm_arr)
    print(f"\n  CM moment analysis (should deviate from semicircle):")
    print(f"    Mean: {mean_cm:.4f}")
    print(f"    Var:  {var_cm:.4f}")
    print(f"    n: {len(cm_normalized)}")


# ============================================================
# 3. MONTGOMERY-ODLYZKO: EC zero spacing → GUE
# ============================================================
print("\n" + "=" * 100)
print("3. MONTGOMERY-ODLYZKO: L-function zero spacing statistics")
print("=" * 100)

con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
zeros_data = con.execute("""
    SELECT zeros_vector, n_zeros_stored FROM object_zeros
    WHERE n_zeros_stored >= 5 LIMIT 2000
""").fetchall()
con.close()

print(f"  Objects with ≥5 zeros: {len(zeros_data)}")

all_spacings = []
for zeros_json, n_zeros in zeros_data:
    try:
        zeros = json.loads(zeros_json) if isinstance(zeros_json, str) else zeros_json
        if isinstance(zeros, list) and len(zeros) >= 3:
            zeros = sorted([float(z) for z in zeros if z > 0])
            if len(zeros) >= 3:
                gaps = np.diff(zeros)
                mean_gap = np.mean(gaps)
                if mean_gap > 0:
                    normalized_gaps = gaps / mean_gap
                    all_spacings.extend(normalized_gaps.tolist())
    except:
        pass

print(f"  Total normalized spacings: {len(all_spacings)}")

if all_spacings:
    spacings = np.array(all_spacings)

    # GUE Wigner surmise: P(s) = (pi/2)*s*exp(-pi*s^2/4)
    # Moments: mean ≈ 0.886, var ≈ 0.178, skew ≈ 0.66, kurt ≈ 3.27
    # Poisson: P(s) = exp(-s), mean=1, var=1, skew=2, kurt=9

    mean_s = np.mean(spacings)
    var_s = np.var(spacings)
    skew_s = np.mean(((spacings - mean_s) / np.std(spacings))**3) if np.std(spacings) > 0 else 0
    kurt_s = np.mean(((spacings - mean_s) / np.std(spacings))**4) if np.std(spacings) > 0 else 0

    print(f"\n  Spacing statistics:")
    print(f"    Mean: {mean_s:.4f} (GUE≈0.89, Poisson=1.00)")
    print(f"    Var:  {var_s:.4f} (GUE≈0.18, Poisson=1.00)")
    print(f"    Skew: {skew_s:.4f} (GUE≈0.66, Poisson=2.00)")
    print(f"    Kurt: {kurt_s:.4f} (GUE≈3.27, Poisson=9.00)")

    # Which fits better?
    gue_dist = abs(var_s - 0.178) + abs(skew_s - 0.66)
    poi_dist = abs(var_s - 1.0) + abs(skew_s - 2.0)
    print(f"\n  Distance to GUE: {gue_dist:.3f}")
    print(f"  Distance to Poisson: {poi_dist:.3f}")
    print(f"  Better fit: {'GUE' if gue_dist < poi_dist else 'POISSON'}")

    # Level repulsion: P(s→0) → 0 for GUE, P(s→0) → 1 for Poisson
    frac_small = np.mean(spacings < 0.1)
    print(f"\n  Fraction s < 0.1: {frac_small:.4f} (GUE≈0.004, Poisson≈0.095)")
    print(f"  Level repulsion: {'STRONG (GUE)' if frac_small < 0.02 else 'WEAK (Poisson-like)'}")


# ============================================================
# 4. BRAUER-SIEGEL: log(h*R)/log(d) → 1/2 by degree
# ============================================================
print("\n" + "=" * 100)
print("4. BRAUER-SIEGEL: log(h*R) / log(d) convergence by degree")
print("=" * 100)

nf_raw = json.load(open(DATA / "number_fields/data/number_fields.json", encoding="utf-8"))
nf = []
for f in nf_raw:
    try:
        nf.append({
            "h": float(f.get("class_number", 0)),
            "R": float(f.get("regulator", 0)),
            "d": float(f.get("disc_abs", 0)),
            "deg": int(float(f.get("degree", 0))),
        })
    except: pass
nf = [f for f in nf if f["h"] > 0 and f["R"] > 0 and f["d"] > 1]

print(f"\n  {'Degree':>6s} | {'n':>5s} | {'mean log(hR)/log(d)':>20s} | {'std':>8s} | {'→ 0.5?'}")
print("  " + "-" * 55)

for deg in sorted(set(f["deg"] for f in nf)):
    subset = [f for f in nf if f["deg"] == deg]
    if len(subset) >= 10:
        ratios = [np.log(f["h"] * f["R"]) / np.log(f["d"]) for f in subset if f["d"] > 1]
        mean_r = np.mean(ratios)
        std_r = np.std(ratios)
        arrow = "↑" if mean_r < 0.5 else "↓" if mean_r > 0.5 else "="
        print(f"  {deg:6d} | {len(subset):5d} | {mean_r:20.4f} | {std_r:8.4f} | {arrow} (want 0.5)")


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 100)
print("KNOWN MATH CALIBRATION SUMMARY")
print("=" * 100)
print(f"""
  These are the ground truths for the precision-fixed TT-Cross metric.
  If the tensor detects these, it's calibrated. If it misses them, it's broken.

  1. Modularity: {'CONFIRMED' if perfect > matched * 0.3 else 'NEEDS MORE DATA'} — {perfect}/{matched} perfect a_p matches
  2. Sato-Tate: Non-CM moments {'MATCH semicircle' if abs(var_nc - 1) < 0.3 else 'DEVIATE'} (var={var_nc:.2f} vs 1.0)
  3. Montgomery-Odlyzko: Zero spacing {'GUE' if gue_dist < poi_dist else 'POISSON'}-like (var={var_s:.3f})
  4. Brauer-Siegel: See degree-by-degree table above
""")
