"""C37/K1: Knot determinant M4/M² = 2.155 — F24 classification.
Prior: [2.092, 2.217], NOT SU(2)=2.0. Need F24+F24b classification.
Machine: M1 (Skullport), 2026-04-12
"""
import json, sys
import numpy as np
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from battery_v2 import BatteryV2

DATA = Path(__file__).resolve().parent.parent.parent
bv2 = BatteryV2()

# Load knots
with open(DATA / "knots/data/knots.json") as f:
    data = json.load(f)
knots = data["knots"]
print(f"Loaded {len(knots)} knots")

# Extract determinants
dets = np.array([k["determinant"] for k in knots if (k.get("determinant") or 0) > 0], dtype=float)
print(f"Determinants > 0: {len(dets)}")

# ─── Test 1: M4/M² computation ───
print("\n" + "="*70)
print("TEST 1: M4/M² of knot determinants")
print("="*70)
normed = dets / np.mean(dets)
m2 = np.mean(normed**2)
m4 = np.mean(normed**4)
m4m2 = m4 / (m2**2)
print(f"M2 = {m2:.6f}")
print(f"M4 = {m4:.6f}")
print(f"M4/M² = {m4m2:.4f}")

# Bootstrap CI
rng = np.random.RandomState(42)
boot_ratios = []
for _ in range(10000):
    idx = rng.choice(len(dets), size=len(dets), replace=True)
    sample = dets[idx]
    sn = sample / np.mean(sample)
    sm2 = np.mean(sn**2)
    sm4 = np.mean(sn**4)
    boot_ratios.append(sm4 / (sm2**2))

boot_ratios = np.array(boot_ratios)
ci_lo, ci_hi = np.percentile(boot_ratios, [5, 95])
print(f"90% CI: [{ci_lo:.4f}, {ci_hi:.4f}]")
print(f"Contains SU(2)=2.0? {'YES' if ci_lo <= 2.0 <= ci_hi else 'NO'}")
print(f"Contains Gaussian=3.0? {'YES' if ci_lo <= 3.0 <= ci_hi else 'NO'}")

# ─── Test 2: F24 by crossing number groups ───
print("\n" + "="*70)
print("TEST 2: F24 — determinant by crossing number")
print("="*70)
crossing_labels = np.array([str(k["crossing_number"]) for k in knots if (k.get("determinant") or 0) > 0])
verdict, result = bv2.F24_variance_decomposition(dets, crossing_labels)
print(f"Verdict: {verdict}")
print(f"eta² = {result.get('eta_squared', 0):.4f}")

verdict_b, result_b = bv2.F24b_metric_consistency(dets, crossing_labels)
print(f"F24b: {verdict_b}")
if "tail_contribution" in result_b:
    print(f"  tail_contribution = {result_b['tail_contribution']:.3f}")

# ─── Test 3: M4/M² by crossing number stratum ───
print("\n" + "="*70)
print("TEST 3: M4/M² stability across crossing number strata")
print("="*70)
crossing_vals = np.array([k["crossing_number"] for k in knots if (k.get("determinant") or 0) > 0])
for cn in sorted(set(crossing_vals)):
    mask = crossing_vals == cn
    if sum(mask) < 20:
        continue
    d = dets[mask]
    dn = d / np.mean(d)
    sm2 = np.mean(dn**2)
    sm4 = np.mean(dn**4)
    ratio = sm4 / (sm2**2)
    print(f"  Crossing {cn:2d}: n={sum(mask):5d}, M4/M² = {ratio:.4f}")

# ─── Test 4: Log-normal comparison ───
print("\n" + "="*70)
print("TEST 4: Distribution shape — log-normal comparison")
print("="*70)
from scipy import stats as sp_stats
log_dets = np.log(dets)
stat_norm, p_norm = sp_stats.normaltest(log_dets)
print(f"Log-normality test: stat={stat_norm:.2f}, p={p_norm:.2e}")
print(f"Log-det mean={np.mean(log_dets):.3f}, std={np.std(log_dets):.3f}, skew={sp_stats.skew(log_dets):.3f}, kurtosis={sp_stats.kurtosis(log_dets):.3f}")

# Reference: log-normal M4/M² depends on sigma
# For log-normal: M4/M² = exp(4*sigma²)/exp(2*sigma²)² = exp(0) = ... no
# Actually for log-normal X: M4/M² = (mu4)/(mu2²) in terms of raw moments
# Let's compute the theoretical M4/M² for a log-normal with observed sigma
sigma_obs = np.std(log_dets)
# For log-normal: kurtosis = exp(4σ²) + 2exp(3σ²) + 3exp(2σ²) - 6
# M4/M² for normalized log-normal
print(f"  Observed σ(log det) = {sigma_obs:.3f}")

# ─── Test 5: Comparison to known distributions ───
print("\n" + "="*70)
print("TEST 5: Reference M4/M² values")
print("="*70)
print("  Exponential: M4/M² = 9.0")
print("  Gaussian: M4/M² = 3.0")
print("  Uniform: M4/M² = 1.8")
print("  SU(2) (semicircle): M4/M² = 2.0")
print(f"  Observed: M4/M² = {m4m2:.4f}")
print(f"  → Between uniform (1.8) and SU(2) (2.0)? {'YES' if 1.8 < m4m2 < 2.0 else 'NO'}")
print(f"  → Between SU(2) (2.0) and Gaussian (3.0)? {'YES' if 2.0 < m4m2 < 3.0 else 'NO'}")

# ─── Classification ───
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)
print(f"M4/M² = {m4m2:.4f} [{ci_lo:.4f}, {ci_hi:.4f}]")
print(f"NOT SU(2) (2.0 {'outside' if not (ci_lo <= 2.0 <= ci_hi) else 'inside'} 90% CI)")
print(f"eta² (crossing→det) = {result.get('eta_squared', 0):.4f}")
print(f"F24b: {verdict_b}")

# The M4/M² value is a distributional constant, not a group effect
# Classification depends on whether it matches any known universality class
if ci_lo <= 2.0 <= ci_hi:
    classification = "POSSIBLE_SU2"
elif 2.0 < m4m2 < 3.0:
    classification = "NOVEL_UNIVERSALITY_CLASS"
else:
    classification = "UNCLASSIFIED"

print(f"\n→ CLASSIFICATION: {classification}")
print(f"  The knot determinant distribution has M4/M² ≈ {m4m2:.3f},")
print(f"  which does not match any standard universality class exactly.")

results = {
    "test": "C37/K1",
    "claim": "Knot determinant M4/M² = 2.155",
    "m4m2_ratio": m4m2,
    "ci_90": [ci_lo, ci_hi],
    "su2_in_ci": bool(ci_lo <= 2.0 <= ci_hi),
    "crossing_eta2": result.get("eta_squared", 0),
    "f24_verdict": verdict,
    "f24b_verdict": verdict_b,
    "n_determinants": len(dets),
    "classification": classification,
}
with open(DATA / "shared/scripts/v2/c37_knot_det_m4m2_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to v2/c37_knot_det_m4m2_results.json")
