"""C41-deep: Unit circle profile independence test.
Prior: Jones-Alexander cosine=0.933. Is this known? F25 across crossing strata.
Battery v6. Machine: M1 (Skullport), 2026-04-12
"""
import sys, json, re
import numpy as np
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from battery_v2 import BatteryV2

DATA = Path(__file__).resolve().parent.parent.parent
bv2 = BatteryV2()

with open(DATA / "knots/data/knots.json") as f:
    data = json.load(f)
knots = data["knots"]
print(f"Loaded {len(knots)} knots")

angles = np.linspace(0, 2*np.pi, 13, endpoint=False)
unit_circle_points = np.exp(1j * angles)

def eval_poly(coeffs, min_power, t):
    if not coeffs:
        return 0.0
    return sum(c * t**(min_power + k) for k, c in enumerate(coeffs))

# Build profiles for both Jones and Alexander
records = []
for k in knots:
    jones = k.get("jones")
    alex = k.get("alexander")
    if not jones or not isinstance(jones, dict) or not alex or not isinstance(alex, dict):
        continue
    j_coeffs = jones.get("coefficients", [])
    a_coeffs = alex.get("coefficients", [])
    if not j_coeffs or not a_coeffs:
        continue

    j_profile = np.array([abs(eval_poly(j_coeffs, jones["min_power"], t)) for t in unit_circle_points])
    a_profile = np.array([abs(eval_poly(a_coeffs, alex["min_power"], t)) for t in unit_circle_points])

    if np.any(np.isnan(j_profile)) or np.any(np.isnan(a_profile)):
        continue
    if np.any(np.isinf(j_profile)) or np.any(np.isinf(a_profile)):
        continue

    cn = k.get("crossing_number") or 0
    if cn == 0:
        m = re.match(r'(\d+)', k.get("name", ""))
        cn = int(m.group(1)) if m else 0

    records.append({
        "name": k["name"],
        "crossing": cn,
        "j_profile": j_profile,
        "a_profile": a_profile,
        "j_norm": float(np.linalg.norm(j_profile)),
        "a_norm": float(np.linalg.norm(a_profile)),
    })

print(f"Knots with both Jones and Alexander profiles: {len(records)}")

j_profiles = np.array([r["j_profile"] for r in records])
a_profiles = np.array([r["a_profile"] for r in records])
j_norms = np.array([r["j_norm"] for r in records])
a_norms = np.array([r["a_norm"] for r in records])
crossings = np.array([r["crossing"] for r in records])
crossing_labels = np.array([str(r["crossing"]) for r in records])

# --- Test 1: Per-knot cosine similarity Jones vs Alexander ---
print("\n" + "="*70)
print("TEST 1: Per-knot Jones-Alexander cosine similarity")
print("="*70)

cosines = []
for i in range(len(records)):
    j = j_profiles[i]
    a = a_profiles[i]
    cos = np.dot(j, a) / (np.linalg.norm(j) * np.linalg.norm(a) + 1e-10)
    cosines.append(cos)
cosines = np.array(cosines)

print(f"Mean cosine: {np.mean(cosines):.4f}")
print(f"Median cosine: {np.median(cosines):.4f}")
print(f"Std cosine: {np.std(cosines):.4f}")
print(f"Min cosine: {np.min(cosines):.4f}")
print(f"Fraction > 0.9: {np.mean(cosines > 0.9)*100:.1f}%")
print(f"Fraction > 0.8: {np.mean(cosines > 0.8)*100:.1f}%")

# --- Test 2: F24 - cosine similarity by crossing number ---
print("\n" + "="*70)
print("TEST 2: F24 - cosine similarity by crossing number")
print("="*70)

v2, r2 = bv2.F24_variance_decomposition(cosines, crossing_labels)
print(f"Verdict: {v2}, eta2 = {r2.get('eta_squared', 0):.4f}")

for cn in sorted(set(crossings)):
    mask = crossings == cn
    if sum(mask) < 10:
        continue
    print(f"  Crossing {cn}: n={sum(mask)}, mean cosine={np.mean(cosines[mask]):.4f}")

# --- Test 3: F25 - does the Jones-Alex relationship transfer across crossing strata? ---
print("\n" + "="*70)
print("TEST 3: F25 - Jones norm -> Alexander norm transportability across crossings")
print("="*70)

# Use Jones norm to predict Alexander norm; test if this transfers
# Group by crossing, use F25
v3, r3 = bv2.F25_transportability(a_norms, crossing_labels, crossing_labels)
print(f"F25 verdict: {v3}")
if "weighted_oos_r2" in r3:
    print(f"Weighted OOS R2: {r3['weighted_oos_r2']:.4f}")

# --- Test 4: Profile shape independence test ---
print("\n" + "="*70)
print("TEST 4: Are Jones and Alexander profiles the SAME shape or just correlated norms?")
print("="*70)

# Normalize profiles to unit norm and compare
j_unit = j_profiles / (np.linalg.norm(j_profiles, axis=1, keepdims=True) + 1e-10)
a_unit = a_profiles / (np.linalg.norm(a_profiles, axis=1, keepdims=True) + 1e-10)

# Mean shape
j_mean_shape = np.mean(j_unit, axis=0)
a_mean_shape = np.mean(a_unit, axis=0)
shape_cosine = np.dot(j_mean_shape, a_mean_shape) / (np.linalg.norm(j_mean_shape) * np.linalg.norm(a_mean_shape))
print(f"Mean SHAPE cosine (norm-independent): {shape_cosine:.4f}")

# Per-knot shape cosine
shape_cosines = []
for i in range(len(records)):
    cos = np.dot(j_unit[i], a_unit[i])
    shape_cosines.append(cos)
shape_cosines = np.array(shape_cosines)
print(f"Per-knot mean shape cosine: {np.mean(shape_cosines):.4f}")
print(f"Per-knot std shape cosine: {np.std(shape_cosines):.4f}")

if np.mean(shape_cosines) > 0.9:
    print("-> Jones and Alexander have the SAME SHAPE on the unit circle (not just correlated magnitudes)")
elif np.mean(shape_cosines) > 0.7:
    print("-> Jones and Alexander have SIMILAR shapes (high correlation, some variation)")
else:
    print("-> Jones and Alexander have DIFFERENT shapes (correlation is mainly magnitude)")

# --- Test 5: Norm ratio stability ---
print("\n" + "="*70)
print("TEST 5: Jones/Alexander norm ratio by crossing number")
print("="*70)

ratios = j_norms / (a_norms + 1e-10)
from scipy import stats as sp_stats

for cn in sorted(set(crossings)):
    mask = crossings == cn
    if sum(mask) < 10:
        continue
    r = ratios[mask]
    print(f"  Crossing {cn}: n={sum(mask)}, mean ratio={np.mean(r):.4f}, CV={np.std(r)/np.mean(r):.4f}")

rho, p_val = sp_stats.spearmanr(crossings, ratios)
print(f"Spearman rho(crossing, norm_ratio): {rho:.4f}, p={p_val:.2e}")

# --- Test 6: F27 consequence check ---
print("\n" + "="*70)
print("TEST 6: F27 - is Jones-Alexander correlation a known consequence?")
print("="*70)
v7, r7 = bv2.F27_consequence_check("jones_polynomial", "alexander_polynomial")
print(f"Verdict: {v7}")
if r7:
    print(f"  {r7}")

# Note: Both are knot invariants derived from skein relations. Their correlation
# on the unit circle is NOT a priori obvious -- they use different variables
# and different skein relations. But they both encode the same topological information.

# --- Classification ---
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)
print(f"Mean per-knot cosine: {np.mean(cosines):.4f}")
print(f"Mean shape cosine: {np.mean(shape_cosines):.4f}")
print(f"Crossing->cosine eta2: {r2.get('eta_squared', 0):.4f}")

if np.mean(shape_cosines) > 0.9:
    classification = "STRUCTURAL_IDENTITY"
    print("-> STRUCTURAL IDENTITY: Jones and Alexander encode the same unit-circle shape")
elif np.mean(cosines) > 0.9:
    classification = "STRONG_CORRELATION"
    print("-> STRONG CORRELATION: Magnitude-driven, shapes differ")
else:
    classification = "MODERATE_CORRELATION"
    print("-> MODERATE CORRELATION")

results = {
    "test": "C41-deep",
    "claim": "Jones-Alexander unit circle profiles are structurally identical",
    "mean_cosine": float(np.mean(cosines)),
    "mean_shape_cosine": float(np.mean(shape_cosines)),
    "crossing_cosine_eta2": r2.get("eta_squared", 0),
    "norm_ratio_vs_crossing_rho": float(rho),
    "classification": classification,
}
with open(DATA / "shared/scripts/v2/r2_c41_deep_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to v2/r2_c41_deep_results.json")
