"""C41/S1: Knot polynomial unit circle profiles — F18 stability.
Prior: Rich 13-point profile distinguishes knot types. Need stability test.
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

with open(DATA / "knots/data/knots.json") as f:
    data = json.load(f)
knots = data["knots"]
print(f"Loaded {len(knots)} knots")

# Evaluate Jones polynomial on unit circle at 13 points
angles = np.linspace(0, 2*np.pi, 13, endpoint=False)
unit_circle_points = np.exp(1j * angles)

def eval_poly(coeffs, min_power, t):
    """Evaluate Laurent polynomial sum(c_k * t^(min_power+k))"""
    if not coeffs:
        return 0.0
    return sum(c * t**(min_power + k) for k, c in enumerate(coeffs))

# Build profiles
profiles = []
names = []
for k in knots:
    jones = k.get("jones")
    if not jones or not isinstance(jones, dict):
        continue
    coeffs = jones.get("coefficients", [])
    min_pow = jones.get("min_power", 0)
    if not coeffs:
        continue
    profile = np.array([abs(eval_poly(coeffs, min_pow, t)) for t in unit_circle_points])
    if np.any(np.isnan(profile)) or np.any(np.isinf(profile)):
        continue
    profiles.append(profile)
    names.append(k["name"])

profiles = np.array(profiles)
print(f"Knots with valid Jones profiles: {len(profiles)}")
print(f"Profile shape: {profiles.shape}")

# --- Test 1: Profile statistics ---
print("\n" + "="*70)
print("TEST 1: Unit circle profile statistics")
print("="*70)
mean_profile = np.mean(profiles, axis=0)
std_profile = np.std(profiles, axis=0)
print("Mean profile:", np.round(mean_profile, 4))
print("Std profile:", np.round(std_profile, 4))
print(f"CV across angles: {np.mean(std_profile / (mean_profile + 1e-10)):.4f}")

# --- Test 2: F18 stability — subsample consistency ---
print("\n" + "="*70)
print("TEST 2: F18 stability (subsample consistency)")
print("="*70)
rng = np.random.RandomState(42)
n_subsamples = 20
subsample_size = len(profiles) // 2
mean_profiles_sub = []
for i in range(n_subsamples):
    idx = rng.choice(len(profiles), size=subsample_size, replace=False)
    sub_mean = np.mean(profiles[idx], axis=0)
    mean_profiles_sub.append(sub_mean)

mean_profiles_sub = np.array(mean_profiles_sub)
cv_per_angle = np.std(mean_profiles_sub, axis=0) / (np.mean(mean_profiles_sub, axis=0) + 1e-10)
print(f"Mean CV across subsamples: {np.mean(cv_per_angle):.6f}")
print(f"Max CV: {np.max(cv_per_angle):.6f}")
if np.mean(cv_per_angle) < 0.01:
    print("-> STABLE (CV < 1%)")
elif np.mean(cv_per_angle) < 0.05:
    print("-> MODERATELY STABLE (CV < 5%)")
else:
    print("-> UNSTABLE (CV >= 5%)")

# --- Test 3: Profile distinguishes Alexander vs Jones ---
print("\n" + "="*70)
print("TEST 3: Alexander vs Jones profile comparison")
print("="*70)
alex_profiles = []
for k in knots:
    alex = k.get("alexander")
    if not alex or not isinstance(alex, dict):
        continue
    coeffs = alex.get("coefficients", [])
    min_pow = alex.get("min_power", 0)
    if not coeffs:
        continue
    profile = np.array([abs(eval_poly(coeffs, min_pow, t)) for t in unit_circle_points])
    if np.any(np.isnan(profile)) or np.any(np.isinf(profile)):
        continue
    alex_profiles.append(profile)

alex_profiles = np.array(alex_profiles)
print(f"Alexander profiles: {len(alex_profiles)}")

if len(alex_profiles) > 0:
    jones_mean = np.mean(profiles, axis=0)
    alex_mean = np.mean(alex_profiles, axis=0)
    from scipy import stats as sp_stats
    rho, p = sp_stats.spearmanr(jones_mean, alex_mean)
    print(f"Jones vs Alexander mean profile correlation: rho = {rho:.4f}, p = {p:.4f}")
    cosine_sim = np.dot(jones_mean, alex_mean) / (np.linalg.norm(jones_mean) * np.linalg.norm(alex_mean))
    print(f"Cosine similarity: {cosine_sim:.4f}")

# --- Test 4: F24 — profile variance by crossing number ---
print("\n" + "="*70)
print("TEST 4: Profile norm by crossing number (F24)")
print("="*70)
import re
profile_norms = np.linalg.norm(profiles, axis=1)
crossing_from_name = []
for n in names:
    m = re.match(r'(\d+)', n)
    crossing_from_name.append(str(m.group(1)) if m else "0")
crossing_from_name = np.array(crossing_from_name)

v4, r4 = bv2.F24_variance_decomposition(profile_norms, crossing_from_name)
print(f"Verdict: {v4}, eta2 = {r4.get('eta_squared', 0):.4f}")

# Per crossing number
for cn in sorted(set(crossing_from_name)):
    mask = crossing_from_name == cn
    if sum(mask) < 10:
        continue
    print(f"  Crossing {cn}: n={sum(mask)}, mean norm={np.mean(profile_norms[mask]):.4f}, std={np.std(profile_norms[mask]):.4f}")

# --- Classification ---
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)
cv_stability = np.mean(cv_per_angle)
crossing_eta2 = r4.get("eta_squared", 0)
print(f"Profile stability (CV): {cv_stability:.6f}")
print(f"Crossing->profile_norm eta2: {crossing_eta2:.4f}")
print(f"Jones-Alexander profile correlation: {rho:.4f}" if len(alex_profiles) > 0 else "No Alexander data")

if cv_stability < 0.01 and crossing_eta2 >= 0.14:
    classification = "STABLE_LAW"
elif cv_stability < 0.01:
    classification = "STABLE_TENDENCY"
else:
    classification = "UNSTABLE"
print(f"\n-> CLASSIFICATION: {classification}")

results = {
    "test": "C41/S1",
    "claim": "Knot polynomial unit circle profiles distinguish knot types",
    "n_jones_profiles": len(profiles),
    "n_alex_profiles": len(alex_profiles),
    "stability_cv": float(cv_stability),
    "crossing_eta2": crossing_eta2,
    "jones_alex_corr": float(rho) if len(alex_profiles) > 0 else None,
    "classification": classification,
}
with open(DATA / "shared/scripts/v2/c41_knot_unit_circle_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to v2/c41_knot_unit_circle_results.json")
