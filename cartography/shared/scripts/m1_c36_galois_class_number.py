"""C36: Galois group → class number — interaction analysis with degree as confound.
Prior: eta²=0.138, KILLED by F17 (degree confound). Rerun with interaction decomposition.
Machine: M1 (Skullport), 2026-04-12
"""
import json, sys, os
import numpy as np
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from battery_v2 import BatteryV2

DATA = Path(__file__).resolve().parent.parent.parent
bv2 = BatteryV2()

# Load number fields
with open(DATA / "number_fields/data/number_fields.json") as f:
    fields = json.load(f)

print(f"Loaded {len(fields)} number fields")

# Parse class numbers (stored as strings)
records = []
for nf in fields:
    cn = int(nf["class_number"])
    deg = nf["degree"]
    gal = nf["galois_label"]
    disc = abs(int(nf["disc_abs"]))
    reg = float(nf["regulator"]) if nf["regulator"] not in ("", "0") else 0.0
    if cn > 0 and deg >= 2:  # skip trivial Q
        records.append({"cn": cn, "degree": deg, "galois": gal, "disc": disc, "reg": reg})

print(f"Records with CN > 0, degree >= 2: {len(records)}")

cn_vals = np.array([r["cn"] for r in records], dtype=float)
gal_labels = np.array([r["galois"] for r in records])
deg_labels = np.array([r["degree"] for r in records])

# ─── Test 1: Global F24 — Galois → class number ───
print("\n" + "="*70)
print("TEST 1: Global Galois → class number (F24)")
print("="*70)
verdict, result = bv2.F24_variance_decomposition(cn_vals, gal_labels)
print(f"Verdict: {verdict}")
print(f"eta² = {result.get('eta_squared', 0):.4f}")
print(f"F = {result.get('f_statistic', 0):.2f}")
print(f"n_groups = {result.get('n_groups', 0)}, n_total = {result.get('n_total', 0)}")

verdict_b, result_b = bv2.F24b_metric_consistency(cn_vals, gal_labels)
print(f"F24b: {verdict_b}")
if "tail_contribution" in result_b:
    print(f"  tail_contribution = {result_b['tail_contribution']:.3f}")

# ─── Test 2: Global F24 — Degree → class number ───
print("\n" + "="*70)
print("TEST 2: Degree → class number (F24)")
print("="*70)
verdict2, result2 = bv2.F24_variance_decomposition(cn_vals, deg_labels)
print(f"Verdict: {verdict2}")
print(f"eta² = {result2.get('eta_squared', 0):.4f}")
print(f"F = {result2.get('f_statistic', 0):.2f}")

# ─── Test 3: Within-degree Galois → class number ───
print("\n" + "="*70)
print("TEST 3: Within-degree Galois → class number (interaction decomposition)")
print("="*70)

for deg in sorted(set(deg_labels)):
    mask = deg_labels == deg
    cn_deg = cn_vals[mask]
    gal_deg = gal_labels[mask]

    # Need at least 2 Galois groups with >= 5 members
    gc = Counter(gal_deg)
    valid_gals = [g for g, c in gc.items() if c >= 5]
    if len(valid_gals) < 2:
        print(f"  Degree {deg}: {sum(mask)} fields, {len(gc)} Galois groups — SKIP (< 2 valid groups)")
        continue

    v, r = bv2.F24_variance_decomposition(cn_deg, gal_deg)
    print(f"  Degree {deg}: {sum(mask)} fields, {len(valid_gals)} groups → eta² = {r.get('eta_squared', 0):.4f} ({v})")

# ─── Test 4: Incremental — Galois after controlling degree ───
print("\n" + "="*70)
print("TEST 4: Incremental eta² (Galois after degree residualization)")
print("="*70)

# Residualize CN by degree means
deg_means = {}
for d in set(deg_labels):
    deg_means[d] = np.mean(cn_vals[deg_labels == d])

cn_resid = np.array([cn_vals[i] - deg_means[deg_labels[i]] for i in range(len(cn_vals))])
v_resid, r_resid = bv2.F24_variance_decomposition(cn_resid, gal_labels)
print(f"Verdict: {v_resid}")
print(f"Incremental eta² (Galois | degree) = {r_resid.get('eta_squared', 0):.4f}")

# ─── Test 5: Rank correlation of Galois effects across degrees ───
print("\n" + "="*70)
print("TEST 5: Rank correlation — are Galois effects consistent across degrees?")
print("="*70)

from scipy import stats as sp_stats

# Get mean CN per Galois group within each degree
degree_galois_means = {}
for deg in sorted(set(deg_labels)):
    mask = deg_labels == deg
    gal_deg = gal_labels[mask]
    cn_deg = cn_vals[mask]
    gc = Counter(gal_deg)
    valid = {g: np.mean(cn_deg[gal_deg == g]) for g, c in gc.items() if c >= 5}
    if len(valid) >= 3:
        degree_galois_means[deg] = valid

if len(degree_galois_means) >= 2:
    degs_with_data = sorted(degree_galois_means.keys())
    for i in range(len(degs_with_data)):
        for j in range(i+1, len(degs_with_data)):
            d1, d2 = degs_with_data[i], degs_with_data[j]
            shared = set(degree_galois_means[d1]) & set(degree_galois_means[d2])
            if len(shared) >= 3:
                vals1 = [degree_galois_means[d1][g] for g in shared]
                vals2 = [degree_galois_means[d2][g] for g in shared]
                rho, p = sp_stats.spearmanr(vals1, vals2)
                print(f"  Degree {d1} vs {d2}: {len(shared)} shared groups, rho = {rho:.3f}, p = {p:.4f}")
    print("  (If rho ≈ 0 or negative: Galois effects are degree-specific = INTERACTION)")
else:
    print("  Not enough degrees with 3+ valid Galois groups for rank comparison")

# ─── Classification ───
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)
global_eta2 = result.get("eta_squared", 0)
incr_eta2 = r_resid.get("eta_squared", 0)
print(f"Global Galois→CN eta² = {global_eta2:.4f}")
print(f"Degree→CN eta² = {result2.get('eta_squared', 0):.4f}")
print(f"Incremental Galois|degree eta² = {incr_eta2:.4f}")
print(f"Ratio (incremental/global) = {incr_eta2/global_eta2:.3f}" if global_eta2 > 0 else "")

if incr_eta2 < 0.01:
    print("\n→ VERDICT: NEGLIGIBLE after degree control. Galois→CN is a DEGREE CONFOUND (confirms F17 kill).")
elif incr_eta2 < 0.06:
    print("\n→ VERDICT: SMALL incremental effect. Galois adds a real but minor signal beyond degree.")
else:
    print("\n→ VERDICT: MODERATE+ incremental effect. Galois has genuine predictive power beyond degree.")

# Save results
results = {
    "test": "C36",
    "claim": "Galois group predicts class number",
    "global_galois_eta2": global_eta2,
    "global_galois_verdict": verdict,
    "degree_eta2": result2.get("eta_squared", 0),
    "incremental_galois_eta2": incr_eta2,
    "incremental_verdict": v_resid,
    "f24b_verdict": verdict_b,
    "classification": "DEGREE_CONFOUND" if incr_eta2 < 0.01 else "SMALL_EFFECT" if incr_eta2 < 0.06 else "MODERATE+",
}
with open(DATA / "shared/scripts/v2/c36_galois_cn_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to v2/c36_galois_cn_results.json")
