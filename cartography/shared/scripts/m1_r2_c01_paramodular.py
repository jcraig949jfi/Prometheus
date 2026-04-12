"""C01/R2: Paramodular conjecture probe.
The paramodular conjecture (Brumer-Kramer): weight-2 Siegel paramodular newform
at level N <--> abelian surface of conductor N.
We have 7 eigenvalue files at prime levels 277-587 and 66K genus-2 curves.
Check conductor matches and run F24 on eigenvalue properties.
Battery v2 (F24/F24b/F25/F27). Machine: M1 (Skullport), 2026-04-12
"""
import sys, json, re
import numpy as np
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from battery_v2 import BatteryV2

DATA = Path(__file__).resolve().parent.parent.parent
bv2 = BatteryV2()

# ============================================================
# Load genus-2 curves
# ============================================================
print("Loading genus-2 curves...")
with open(DATA / "genus2/data/genus2_curves_full.json", "r") as f:
    genus2_data = json.load(f)

# Build conductor -> list of curves mapping
conductor_to_curves = defaultdict(list)
for curve in genus2_data:
    cond = curve.get("conductor")
    if cond is not None:
        conductor_to_curves[int(cond)].append(curve)
print(f"Loaded {len(genus2_data)} genus-2 curves, {len(conductor_to_curves)} unique conductors")

# ============================================================
# Load Siegel eigenvalue files
# ============================================================
print("\nLoading Siegel paramodular eigenvalue files...")
eig_dir = DATA / "paramodular_wt2"
eig_files = sorted(eig_dir.glob("eig*.txt"))

def parse_eig_file(fpath):
    """Parse eigenvalue file. Format: header lines, then columns:
    Coeff  Det  Reduced_form  Unreduced_form
    Returns (level, list of coefficient values).
    """
    level = None
    coefficients = []
    with open(fpath, "r") as f:
        for line in f:
            line = line.strip()
            # Extract level from header
            m = re.search(r"LEVEL\s+(\d+)", line)
            if m:
                level = int(m.group(1))
                continue
            # Skip headers and separators
            if not line or line.startswith("=") or line.startswith("Coeff"):
                continue
            parts = line.split()
            if len(parts) >= 2:
                try:
                    coeff = int(parts[0])
                    coefficients.append(coeff)
                except ValueError:
                    continue
    return level, coefficients

eigenvalue_data = {}
for fp in eig_files:
    level, coeffs = parse_eig_file(fp)
    if level is not None:
        # Handle eig587minus/plus -> both are level 587
        if level in eigenvalue_data:
            eigenvalue_data[level]["coefficients"].extend(coeffs)
            eigenvalue_data[level]["files"].append(fp.name)
        else:
            eigenvalue_data[level] = {
                "level": level,
                "coefficients": coeffs,
                "files": [fp.name],
            }
    print(f"  {fp.name}: level={level}, {len(coeffs)} coefficients")

print(f"\nLoaded eigenvalues at {len(eigenvalue_data)} distinct levels: {sorted(eigenvalue_data.keys())}")

# ============================================================
# TEST 1: Conductor matching (paramodular conjecture check)
# ============================================================
print("\n" + "="*70)
print("TEST 1: Paramodular conjecture -- conductor matching")
print("="*70)

match_results = {}
all_coeffs_matched = []
all_coeffs_unmatched = []
matched_levels = []
unmatched_levels = []

for level, eig_info in sorted(eigenvalue_data.items()):
    curves_at_level = conductor_to_curves.get(level, [])
    has_match = len(curves_at_level) > 0
    coeffs = eig_info["coefficients"]

    match_results[level] = {
        "level": level,
        "n_eigenvalues": len(coeffs),
        "n_curves_at_conductor": len(curves_at_level),
        "has_match": has_match,
        "mean_coeff": float(np.mean(coeffs)) if coeffs else 0,
        "std_coeff": float(np.std(coeffs)) if coeffs else 0,
        "max_abs_coeff": int(max(abs(c) for c in coeffs)) if coeffs else 0,
    }

    if has_match:
        matched_levels.append(level)
        all_coeffs_matched.extend(coeffs)
        curve_info = curves_at_level[0]
        print(f"  Level {level}: MATCH -- {len(curves_at_level)} curve(s), "
              f"st_group={curve_info.get('st_group','?')}, "
              f"root_number={curve_info.get('root_number','?')}")
    else:
        unmatched_levels.append(level)
        all_coeffs_unmatched.extend(coeffs)
        print(f"  Level {level}: NO MATCH -- 0 genus-2 curves at this conductor")

n_matched = len(matched_levels)
n_unmatched = len(unmatched_levels)
n_total = n_matched + n_unmatched
print(f"\nSummary: {n_matched}/{n_total} levels have matching genus-2 curves")
print(f"  Matched levels:   {matched_levels}")
print(f"  Unmatched levels: {unmatched_levels}")

# ============================================================
# TEST 2: F24 -- eigenvalue properties by match status
# ============================================================
print("\n" + "="*70)
print("TEST 2: F24 -- eigenvalue coefficient magnitude by match status")
print("="*70)

# Group all coefficients by matched/unmatched
all_abs_coeffs = []
all_labels = []
for level, eig_info in eigenvalue_data.items():
    label = "matched" if level in matched_levels else "unmatched"
    for c in eig_info["coefficients"]:
        all_abs_coeffs.append(abs(c))
        all_labels.append(label)

if len(set(all_labels)) >= 2:
    v24, r24 = bv2.F24_variance_decomposition(
        np.array(all_abs_coeffs, dtype=float), all_labels
    )
    print(f"F24 verdict: {v24}")
    print(f"  eta^2 = {r24.get('eta_squared', 0):.4f}")
    print(f"  n_total = {r24.get('n_total', 0)}, n_groups = {r24.get('n_groups', 0)}")
    for gname, gstat in r24.get("group_stats", {}).items():
        print(f"  Group '{gname}': n={gstat['n']}, mean={gstat['mean']:.2f}, std={gstat['std']:.2f}")
else:
    v24, r24 = "INSUFFICIENT_DATA", {}
    print("Cannot run F24 -- need both matched and unmatched groups")

# ============================================================
# TEST 3: F24b -- metric consistency
# ============================================================
print("\n" + "="*70)
print("TEST 3: F24b -- metric consistency (tail localization)")
print("="*70)

if len(set(all_labels)) >= 2 and len(all_abs_coeffs) >= 40:
    v24b, r24b = bv2.F24b_metric_consistency(
        np.array(all_abs_coeffs, dtype=float), all_labels
    )
    print(f"F24b verdict: {v24b}")
    print(f"  M4/M2 ratio = {r24b.get('m4m2_ratio', 'N/A')}")
    print(f"  eta^2 = {r24b.get('eta_squared', 'N/A')}")
else:
    v24b, r24b = "INSUFFICIENT_DATA", {}
    print("Cannot run F24b -- insufficient data")

# ============================================================
# TEST 4: F25 -- transportability across levels
# ============================================================
print("\n" + "="*70)
print("TEST 4: F25 -- transportability across Siegel levels")
print("="*70)

# Primary label: matched/unmatched; secondary: level
primary_labels = []
secondary_labels = []
transport_values = []
for level, eig_info in eigenvalue_data.items():
    label = "matched" if level in matched_levels else "unmatched"
    for c in eig_info["coefficients"]:
        transport_values.append(abs(c))
        primary_labels.append(label)
        secondary_labels.append(str(level))

if len(set(secondary_labels)) >= 2:
    v25, r25 = bv2.F25_transportability(
        np.array(transport_values, dtype=float),
        primary_labels, secondary_labels
    )
    print(f"F25 verdict: {v25}")
    print(f"  Weighted OOS R^2 = {r25.get('weighted_oos_r2', 'N/A'):.4f}")
    print(f"  Mean OOS R^2 = {r25.get('mean_oos_r2', 'N/A'):.4f}")
else:
    v25, r25 = "INSUFFICIENT_DATA", {}
    print("Cannot run F25 -- need multiple secondary groups")

# ============================================================
# TEST 5: F27 -- consequence check
# ============================================================
print("\n" + "="*70)
print("TEST 5: F27 -- tautology check")
print("="*70)

v27, r27 = bv2.F27_consequence_check("paramodular_level", "genus2_conductor")
print(f"F27 verdict: {v27}")
if r27:
    print(f"  Details: {r27}")

# ============================================================
# TEST 6: Eigenvalue statistics per level
# ============================================================
print("\n" + "="*70)
print("TEST 6: Eigenvalue statistics per level")
print("="*70)

for level in sorted(eigenvalue_data.keys()):
    coeffs = np.array(eigenvalue_data[level]["coefficients"], dtype=float)
    if len(coeffs) < 5:
        continue
    normed = coeffs / np.std(coeffs) if np.std(coeffs) > 0 else coeffs
    m2 = np.mean(normed**2)
    m4 = np.mean(normed**4)
    m4m2 = m4 / m2**2 if m2 > 0 else 0
    status = "MATCHED" if level in matched_levels else "UNMATCHED"
    print(f"  Level {level} [{status}]: n={len(coeffs)}, mean={np.mean(coeffs):.2f}, "
          f"std={np.std(coeffs):.2f}, M4/M2^2={m4m2:.3f}")

# ============================================================
# CLASSIFICATION
# ============================================================
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)

print(f"Match rate: {n_matched}/{n_total} ({100*n_matched/max(n_total,1):.0f}%)")
print(f"F24 eta^2: {r24.get('eta_squared', 'N/A')}")
print(f"F24b consistency: {v24b}")
print(f"F25 transportability: {v25}")
print(f"F27 tautology: {v27}")

if n_matched == n_total:
    classification = "FULL_MATCH"
    print("\n--> All levels have genus-2 curve matches: paramodular conjecture consistent")
elif n_matched == 0:
    classification = "NO_MATCH"
    print("\n--> No levels have genus-2 curve matches: data gap or conjecture violation")
else:
    classification = "PARTIAL_MATCH"
    print(f"\n--> Partial match: {n_matched}/{n_total} levels support conjecture")
    print(f"    Missing conductors: {unmatched_levels}")

# ============================================================
# Save results
# ============================================================
final_results = {
    "test": "C01/R2",
    "claim": "Paramodular conjecture: weight-2 Siegel newform at level N <--> abelian surface of conductor N",
    "match_rate": n_matched / max(n_total, 1),
    "matched_levels": matched_levels,
    "unmatched_levels": unmatched_levels,
    "match_details": {str(k): v for k, v in match_results.items()},
    "f24": {"verdict": v24, "result": r24},
    "f24b": {"verdict": v24b, "result": r24b},
    "f25": {"verdict": v25, "result": r25},
    "f27": {"verdict": v27, "result": r27},
    "classification": classification,
}

out_path = Path(__file__).resolve().parent / "v2" / "c01_paramodular_results.json"
out_path.parent.mkdir(exist_ok=True)
with open(out_path, "w") as f:
    json.dump(final_results, f, indent=2, default=str)
print(f"\nResults saved to v2/c01_paramodular_results.json")
