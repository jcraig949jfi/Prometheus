"""
Maass Level-1 Deep Analysis
============================
Characterize the 2,202 level-1 Maass forms for SL(2,Z).

Data sources:
  - maass_rigor_full.json: 2202 level-1 forms with high-precision spectral parameters
  - maass_with_coefficients.json: 69 level-1 forms with Fourier coefficients

Analysis:
  1. Spectral parameter distribution vs Weyl law N(R) ~ R²/12
  2. Even/odd split and spacing statistics per symmetry
  3. M2, M4, M6 coefficient moments vs Catalan/SU(2) predictions
  4. Coefficient distribution: c_p/2 histograms for primes
  5. Serial autocorrelation at level 1
  6. Phase coherence at level 1
"""

import json
import numpy as np
from collections import Counter
from pathlib import Path
import sys

# ─── Load data ────────────────────────────────────────────────────────────────

BASE = Path(__file__).resolve().parent.parent
MAASS_DIR = BASE / "maass" / "data"

with open(MAASS_DIR / "maass_rigor_full.json") as f:
    rigor_data = json.load(f)

rigor_l1 = [r for r in rigor_data["records"] if r["level"] == 1]
print(f"Level-1 forms (rigor): {len(rigor_l1)}")

with open(MAASS_DIR / "maass_with_coefficients.json") as f:
    coeff_data = json.load(f)

coeff_l1 = [d for d in coeff_data if d["level"] == 1]
print(f"Level-1 forms with coefficients: {len(coeff_l1)}")

results = {"meta": {"level": 1, "total_forms_rigor": len(rigor_l1),
                     "total_forms_with_coefficients": len(coeff_l1)}}

# ─── 1. Spectral parameter distribution vs Weyl law ──────────────────────────

# For SL(2,Z), Weyl law: N(R) ~ R²/12 (number of forms with spectral param <= R)
# More precisely: N(R) ~ (1/12) R² - (2/pi) R log R + C*R + lower order

Rs_all = sorted([float(r["spectral_parameter"]) for r in rigor_l1])
Rs_all = np.array(Rs_all)

R_max = Rs_all[-1]
R_min = Rs_all[0]

# Cumulative count vs Weyl prediction
# N(R) counts ALL forms with spectral param <= R, including those below our minimum
# The Weyl law for SL(2,Z) (both even+odd): N(R) ~ R²/12
# We observe forms from R_min=9.53 onward, so compare N_observed(R) to R²/12 - R_min²/12

R_grid = np.linspace(R_min, R_max, 500)
N_actual = np.array([np.sum(Rs_all <= R) for R in R_grid])

# Total Weyl count N(R) ~ R²/12; our observed count starts at 1
# So N_obs(R) = N_total(R) - N_total(R_min) + 1
# Best approach: fit N_obs(R) = a*(R² - R_min²) + b*(R*log(R) - R_min*log(R_min)) + c*(R - R_min)
N_weyl_leading = (R_grid**2 - R_min**2) / 12

# Fit with offset basis
X = np.column_stack([
    R_grid**2 - R_min**2,
    R_grid * np.log(R_grid) - R_min * np.log(R_min),
    R_grid - R_min,
    np.ones_like(R_grid)
])
coeffs_fit, residuals, rank, sv = np.linalg.lstsq(X, N_actual, rcond=None)
a_fit, b_fit, c_fit, d_fit = coeffs_fit

# Compare a_fit to 1/12 = 0.08333...
weyl_ratio = a_fit / (1/12)

# Also check: predicted total at R_max from Weyl
weyl_predicted_total = R_max**2 / 12
# How many forms are we missing below R_min?
weyl_predicted_below_Rmin = R_min**2 / 12

# Residuals from leading Weyl term (offset)
weyl_residuals = N_actual - N_weyl_leading
mean_residual = np.mean(np.abs(weyl_residuals))
max_residual = np.max(np.abs(weyl_residuals))

print(f"\n=== Weyl Law Analysis ===")
print(f"R range: {R_min:.6f} to {R_max:.6f}")
print(f"Leading Weyl coefficient a = {a_fit:.8f} (expected 1/12 = {1/12:.8f})")
print(f"Ratio a/(1/12) = {weyl_ratio:.6f}")
print(f"Sub-leading: b*R*log(R) with b = {b_fit:.6f} (expected ~ -2/pi = {-2/np.pi:.6f})")
print(f"Linear term c = {c_fit:.4f}")
print(f"Mean |residual| from leading Weyl: {mean_residual:.2f}")

# Completeness check
completeness_ratios = {}
for R_check in [50, 100, 150, float(R_max)]:
    N_obs = int(np.sum(Rs_all <= R_check))
    N_weyl = R_check**2 / 12
    ratio = N_obs / N_weyl if N_weyl > 0 else 0
    completeness_ratios[f"R={R_check:.0f}"] = {"N_obs": N_obs, "N_weyl": round(N_weyl),
                                                  "completeness": round(ratio, 4)}
    print(f"  N({R_check:.0f}) = {N_obs} vs Weyl {N_weyl:.0f}, completeness = {ratio:.1%}")

overall_completeness = len(Rs_all) / (R_max**2 / 12)
print(f"Overall completeness: {overall_completeness:.1%} (dataset has gaps from LMFDB verification)")

results["weyl_law"] = {
    "R_min": float(R_min),
    "R_max": float(R_max),
    "leading_coefficient_a": float(a_fit),
    "expected_a": 1/12,
    "ratio_a_over_expected": float(weyl_ratio),
    "subleading_b": float(b_fit),
    "expected_b": -2/np.pi,
    "linear_c": float(c_fit),
    "constant_d": float(d_fit),
    "weyl_predicted_total": float(weyl_predicted_total),
    "weyl_predicted_below_Rmin": float(weyl_predicted_below_Rmin),
    "mean_abs_residual_from_leading": float(mean_residual),
    "max_abs_residual_from_leading": float(max_residual),
    "fit_quality": "excellent" if abs(weyl_ratio - 1.0) < 0.01 else
                   "good" if abs(weyl_ratio - 1.0) < 0.05 else "fair",
    "completeness": completeness_ratios,
    "overall_completeness": float(overall_completeness),
    "note": "Dataset ~77% complete vs Weyl prediction; LMFDB has verified subset"
}

# ─── 2. Even/odd split and spacing statistics ────────────────────────────────

# In rigor file: sym=1 -> even, sym=0 -> odd
even_Rs = sorted([float(r["spectral_parameter"]) for r in rigor_l1 if r["symmetry"] == 1])
odd_Rs = sorted([float(r["spectral_parameter"]) for r in rigor_l1 if r["symmetry"] == 0])

even_Rs = np.array(even_Rs)
odd_Rs = np.array(odd_Rs)

print(f"\n=== Even/Odd Split ===")
print(f"Even forms: {len(even_Rs)}")
print(f"Odd forms: {len(odd_Rs)}")
print(f"Even/Odd ratio: {len(even_Rs)/len(odd_Rs):.4f}")

# Nearest-neighbor spacings for each symmetry class
def spacing_stats(Rs, label):
    spacings = np.diff(Rs)
    # Normalize by mean spacing
    mean_sp = np.mean(spacings)
    normalized = spacings / mean_sp

    stats = {
        "count": len(Rs),
        "first_R": float(Rs[0]),
        "last_R": float(Rs[-1]),
        "mean_spacing": float(mean_sp),
        "std_spacing": float(np.std(spacings)),
        "min_spacing": float(np.min(spacings)),
        "max_spacing": float(np.max(spacings)),
    }

    # GUE/GOE comparison: compute spacing distribution moments
    # For GOE: <s> = 1, <s²> = 4/pi + 1 ≈ 2.273
    # For GUE: <s> = 1, <s²> ≈ 1.571 (= pi/2)
    # For Poisson: <s> = 1, <s²> = 2
    s2 = float(np.mean(normalized**2))
    s3 = float(np.mean(normalized**3))

    # Level repulsion: P(s→0) ~ s^β, β=1 for GOE, β=2 for GUE
    # Count fraction with s < 0.1
    small_frac = float(np.mean(normalized < 0.1))

    stats["normalized_s2"] = s2
    stats["normalized_s3"] = s3
    stats["small_spacing_fraction"] = small_frac

    # GOE reference: <s²> = 1 + 4/pi ≈ 2.273 -- WRONG
    # Actually for Wigner surmise (GOE): <s²> = 4 - 32/(3*pi) ≈ 0.607... no
    # Let me just compute and compare
    # Wigner surmise GOE: p(s) = (pi/2)*s*exp(-pi*s²/4), <s²> = (4-pi)/pi + 1 ...
    # Easier: just report the moments and ratio of variance
    stats["coefficient_of_variation"] = float(np.std(normalized) / np.mean(normalized))

    print(f"  {label}: n={len(Rs)}, mean_spacing={mean_sp:.6f}, <s²>={s2:.4f}, "
          f"small_frac={small_frac:.4f}, CV={stats['coefficient_of_variation']:.4f}")

    return stats

print()
even_stats = spacing_stats(even_Rs, "Even")
odd_stats = spacing_stats(odd_Rs, "Odd")
all_stats = spacing_stats(Rs_all, "All")

# Weyl law per symmetry: each class should have ~R²/24
even_weyl_ratio = len(even_Rs) / (R_max**2 / 24)
odd_weyl_ratio = len(odd_Rs) / (R_max**2 / 24)

# The ratio should approach 1 as R -> inf; for finite R we compare
# N_even(R) to (R² - R_min_even²)/24 since Weyl counts from 0
R_max_even = even_Rs[-1]
R_max_odd = odd_Rs[-1]
even_weyl_ratio_corrected = len(even_Rs) / ((R_max_even**2) / 24)
odd_weyl_ratio_corrected = len(odd_Rs) / ((R_max_odd**2) / 24)
print(f"\nEven: N_even/{R_max_even:.1f}^2/24 = {even_weyl_ratio_corrected:.4f}")
print(f"Odd:  N_odd/{R_max_odd:.1f}^2/24 = {odd_weyl_ratio_corrected:.4f}")

results["even_odd_split"] = {
    "even_count": len(even_Rs),
    "odd_count": len(odd_Rs),
    "ratio": float(len(even_Rs) / len(odd_Rs)),
    "even_weyl_ratio": float(even_weyl_ratio),
    "odd_weyl_ratio": float(odd_weyl_ratio),
    "even_spacing": even_stats,
    "odd_spacing": odd_stats,
    "all_spacing": all_stats
}

# ─── 3. M2, M4, M6 moments vs Catalan/SU(2) ─────────────────────────────────

# For SU(2) (Sato-Tate), coefficients a_p are distributed as semicircle on [-2,2]
# Moments of a_p/2 (= cos(θ)):
#   M2 = <(a_p/2)²> = 1/2 (Catalan: C1 = 1)...
# Actually: a_p ~ 2cos(θ), θ uniform on [0,π] weighted by sin²(θ)
# <a_p²> = <4cos²θ * (2/π)sin²θ dθ> ...
# For Sato-Tate: <a_p²> = 1, <a_p⁴> = 2, <a_p⁶> = 5
# These are Catalan numbers C_n: C1=1, C2=2, C3=5
# So M2k = <a_p^(2k)> should give Catalan numbers if SU(2)-distributed

# The coefficients in the file are a(n), normalized so a(1) = 1
# For Maass forms, a(p) for prime p should be in [-2, 2] if Ramanujan conjecture holds

print(f"\n=== Coefficient Moments (M2, M4, M6) ===")

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i*i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

# Collect prime coefficients from all level-1 forms with coefficients
all_prime_coeffs = []  # list of arrays, one per form
prime_indices = []  # which indices are prime

coeff_counts = sorted(set(d["n_coefficients"] for d in coeff_l1))
print(f"Coefficient counts: {coeff_counts}")

# Use forms with >= 100 coefficients for robust analysis; fall back to all if needed
coeff_l1_rich = [d for d in coeff_l1 if d["n_coefficients"] >= 100]
if len(coeff_l1_rich) < 10:
    coeff_l1_rich = coeff_l1  # fall back
    max_n = min(d["n_coefficients"] for d in coeff_l1_rich)
else:
    max_n = min(d["n_coefficients"] for d in coeff_l1_rich)
print(f"Forms with enough coefficients: {len(coeff_l1_rich)} (min n_coefficients = {max_n})")

# Find primes up to max_n (coefficients are indexed from 1)
for p in range(2, max_n + 1):
    if is_prime(p):
        prime_indices.append(p)

print(f"Primes up to {max_n}: {len(prime_indices)} (max prime = {prime_indices[-1]})")

# For each form, extract a(p) for prime p
# Note: coefficients[0] = a(1) = 1, coefficients[p-1] = a(p)
form_prime_coeffs = []
for d in coeff_l1_rich:
    coeffs = d["coefficients"]
    ap = np.array([coeffs[p-1] for p in prime_indices if p-1 < len(coeffs)])
    form_prime_coeffs.append(ap)

# Pool all prime coefficients across forms
pooled = np.concatenate(form_prime_coeffs)
print(f"Total prime coefficient values: {len(pooled)}")

# Check Ramanujan: what fraction of |a_p| > 2?
ramanujan_violations = np.mean(np.abs(pooled) > 2.0)
print(f"|a_p| > 2 fraction: {ramanujan_violations:.6f}")

# Moments
M2 = float(np.mean(pooled**2))
M4 = float(np.mean(pooled**4))
M6 = float(np.mean(pooled**6))

# Catalan predictions: C1=1, C2=2, C3=5
# These are for a_p distributed as Sato-Tate (semicircle on [-2,2])
print(f"M2 = {M2:.6f} (Catalan C1 = 1)")
print(f"M4 = {M4:.6f} (Catalan C2 = 2)")
print(f"M6 = {M6:.6f} (Catalan C3 = 5)")
print(f"M4/M2² = {M4/M2**2:.6f} (Catalan: 2/1 = 2.0)")
print(f"M6/M2³ = {M6/M2**3:.6f} (Catalan: 5/1 = 5.0)")

# Per-form moments
per_form_M2 = []
per_form_M4 = []
per_form_M6 = []
per_form_M4_M2sq = []

for ap in form_prime_coeffs:
    m2 = np.mean(ap**2)
    m4 = np.mean(ap**4)
    m6 = np.mean(ap**6)
    per_form_M2.append(m2)
    per_form_M4.append(m4)
    per_form_M6.append(m6)
    per_form_M4_M2sq.append(m4 / m2**2 if m2 > 0 else 0)

per_form_M2 = np.array(per_form_M2)
per_form_M4 = np.array(per_form_M4)
per_form_M6 = np.array(per_form_M6)
per_form_M4_M2sq = np.array(per_form_M4_M2sq)

print(f"\nPer-form M4/M2²: mean={np.mean(per_form_M4_M2sq):.4f}, "
      f"std={np.std(per_form_M4_M2sq):.4f}, "
      f"min={np.min(per_form_M4_M2sq):.4f}, max={np.max(per_form_M4_M2sq):.4f}")

# Split by symmetry
even_coeff = [d for d in coeff_l1_rich if d["symmetry"] == 1]
odd_coeff = [d for d in coeff_l1_rich if d["symmetry"] == -1]

def compute_moments(forms, label):
    all_ap = []
    for d in forms:
        coeffs = d["coefficients"]
        ap = [coeffs[p-1] for p in prime_indices if p-1 < len(coeffs)]
        all_ap.extend(ap)
    all_ap = np.array(all_ap)
    m2 = float(np.mean(all_ap**2))
    m4 = float(np.mean(all_ap**4))
    m6 = float(np.mean(all_ap**6))
    print(f"  {label} (n={len(forms)}): M2={m2:.4f}, M4={m4:.4f}, M6={m6:.4f}, "
          f"M4/M2²={m4/m2**2:.4f}")
    return {"n_forms": len(forms), "n_coeffs": len(all_ap),
            "M2": m2, "M4": m4, "M6": m6,
            "M4_over_M2sq": m4/m2**2, "M6_over_M2_cubed": m6/m2**3}

print(f"\nMoments by symmetry:")
even_moments = compute_moments(even_coeff, "Even")
odd_moments = compute_moments(odd_coeff, "Odd")

results["coefficient_moments"] = {
    "n_forms": len(coeff_l1_rich),
    "n_primes": len(prime_indices),
    "max_prime": prime_indices[-1],
    "total_prime_coefficients": len(pooled),
    "ramanujan_violation_fraction": float(ramanujan_violations),
    "pooled": {
        "M2": M2, "M4": M4, "M6": M6,
        "M4_over_M2sq": M4/M2**2,
        "M6_over_M2_cubed": M6/M2**3,
        "catalan_predictions": {"M2": 1, "M4": 2, "M6": 5}
    },
    "per_form_M4_M2sq": {
        "mean": float(np.mean(per_form_M4_M2sq)),
        "std": float(np.std(per_form_M4_M2sq)),
        "min": float(np.min(per_form_M4_M2sq)),
        "max": float(np.max(per_form_M4_M2sq)),
    },
    "by_symmetry": {"even": even_moments, "odd": odd_moments}
}

# ─── 4. Coefficient distribution: histogram of a_p/2 ─────────────────────────

print(f"\n=== Coefficient Distribution (a_p/2 histogram) ===")

half_coeffs = pooled / 2.0
bins = np.linspace(-1.1, 1.1, 51)
hist, bin_edges = np.histogram(half_coeffs, bins=bins, density=True)

# Sato-Tate density: (2/pi) * sqrt(1 - x²) for x in [-1, 1]
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
st_density = np.where(np.abs(bin_centers) <= 1,
                       (2/np.pi) * np.sqrt(np.maximum(1 - bin_centers**2, 0)), 0)

# KL divergence (discrete approximation)
# Normalize both
hist_norm = hist / np.sum(hist)
st_norm = st_density / np.sum(st_density)
# Avoid zeros
mask = (hist_norm > 0) & (st_norm > 0)
kl_div = float(np.sum(hist_norm[mask] * np.log(hist_norm[mask] / st_norm[mask])))

# Chi-squared style goodness of fit
chi2 = float(np.sum((hist_norm - st_norm)**2 / np.maximum(st_norm, 1e-10)))

print(f"KL divergence (empirical || Sato-Tate): {kl_div:.6f}")
print(f"Chi² statistic: {chi2:.6f}")
print(f"Mean of |a_p/2|: {np.mean(np.abs(half_coeffs)):.6f} (ST expected: 4/(3*pi) = {4/(3*np.pi):.6f})")

results["coefficient_distribution"] = {
    "histogram_bins": [float(x) for x in bin_centers],
    "histogram_density": [float(x) for x in hist],
    "sato_tate_density": [float(x) for x in st_density],
    "kl_divergence": kl_div,
    "chi2_statistic": chi2,
    "mean_abs_half_coeff": float(np.mean(np.abs(half_coeffs))),
    "expected_mean_abs_st": 4/(3*np.pi),
    "fraction_outside_unit": float(np.mean(np.abs(half_coeffs) > 1.0))
}

# ─── 5. Serial autocorrelation ───────────────────────────────────────────────

print(f"\n=== Serial Autocorrelation ===")

# For each form, compute autocorrelation of a(n) sequence at lags 1-10
autocorr_results = []
for d in coeff_l1_rich:
    coeffs = np.array(d["coefficients"][1:])  # skip a(1)=1
    if len(coeffs) < 20:
        continue
    coeffs_centered = coeffs - np.mean(coeffs)
    var = np.var(coeffs)
    if var < 1e-10:
        continue
    lags = []
    for lag in range(1, 11):
        ac = np.mean(coeffs_centered[:-lag] * coeffs_centered[lag:]) / var
        lags.append(float(ac))
    autocorr_results.append(lags)

autocorr_arr = np.array(autocorr_results)
mean_ac = np.mean(autocorr_arr, axis=0)
std_ac = np.std(autocorr_arr, axis=0)

# Expected for truly random: ~0 with std ~ 1/sqrt(N)
N_typical = min(d["n_coefficients"] for d in coeff_l1_rich) - 1
expected_std = 1.0 / np.sqrt(N_typical)

print(f"Forms used: {len(autocorr_results)}")
print(f"Expected noise level: +/-{expected_std:.6f}")
for lag in range(10):
    sig = abs(mean_ac[lag]) / expected_std
    print(f"  Lag {lag+1}: mean={mean_ac[lag]:.6f} +/- {std_ac[lag]:.6f} "
          f"({sig:.1f} sigma)")

results["serial_autocorrelation"] = {
    "n_forms": len(autocorr_results),
    "expected_noise_level": float(expected_std),
    "mean_autocorrelation": [float(x) for x in mean_ac],
    "std_autocorrelation": [float(x) for x in std_ac],
    "significance_sigma": [float(abs(mean_ac[i]) / expected_std) for i in range(10)]
}

# ─── 6. Phase coherence ──────────────────────────────────────────────────────

print(f"\n=== Phase Coherence ===")

# For Maass forms: a(p) = 2*cos(θ_p), so θ_p = arccos(a(p)/2)
# Phase coherence: how correlated are θ_p across different forms?

# Extract phases for each form
form_phases = []
for d in coeff_l1_rich:
    coeffs = d["coefficients"]
    # Get a(p)/2 for first 20 primes
    phases = []
    for p in prime_indices[:50]:  # first 50 primes
        if p-1 < len(coeffs):
            x = coeffs[p-1] / 2.0
            x = np.clip(x, -1, 1)
            phases.append(np.arccos(x))
    form_phases.append(np.array(phases))

# Phase coherence matrix: correlation between forms
n_forms = len(form_phases)
min_len = min(len(ph) for ph in form_phases)
phase_matrix = np.array([ph[:min_len] for ph in form_phases])

# Cross-form phase correlation
# For each pair of forms, compute correlation of their phase sequences
from itertools import combinations

cross_corrs = []
for i, j in combinations(range(n_forms), 2):
    cc = np.corrcoef(phase_matrix[i], phase_matrix[j])[0, 1]
    if np.isfinite(cc):
        cross_corrs.append(cc)

cross_corrs = np.array(cross_corrs)
print(f"Cross-form phase correlations (n_pairs={len(cross_corrs)}):")
print(f"  Mean: {np.mean(cross_corrs):.6f}")
print(f"  Std: {np.std(cross_corrs):.6f}")
print(f"  Min: {np.min(cross_corrs):.6f}")
print(f"  Max: {np.max(cross_corrs):.6f}")
print(f"  |corr| > 0.3 fraction: {np.mean(np.abs(cross_corrs) > 0.3):.4f}")

# Phase uniformity: for each prime, are the phases uniform on [0, π]?
# Kolmogorov-Smirnov test against uniform
from scipy import stats as sp_stats

phase_uniformity = []
for j, p in enumerate(prime_indices[:50]):
    phases_at_p = phase_matrix[:, j] if j < min_len else np.array([])
    if len(phases_at_p) < 5:
        continue
    # Normalize to [0,1]
    normed = phases_at_p / np.pi
    ks_stat, ks_pval = sp_stats.kstest(normed, 'uniform')
    phase_uniformity.append({
        "prime": p,
        "ks_stat": float(ks_stat),
        "ks_pval": float(ks_pval),
        "mean_phase": float(np.mean(phases_at_p)),
        "std_phase": float(np.std(phases_at_p))
    })

n_uniform = sum(1 for pu in phase_uniformity if pu["ks_pval"] > 0.05)
print(f"\nPhase uniformity (KS test at 50 primes):")
print(f"  Primes passing uniformity (p > 0.05): {n_uniform}/{len(phase_uniformity)}")

# Overall phase coherence metric
# Use circular variance: 1 - |mean(e^{2iθ})|
circ_vars = []
for j in range(min_len):
    z = np.exp(2j * phase_matrix[:, j])
    circ_var = 1 - np.abs(np.mean(z))
    circ_vars.append(float(circ_var))

mean_circ_var = np.mean(circ_vars)
print(f"  Mean circular variance: {mean_circ_var:.6f} (1.0 = perfectly uniform, 0.0 = perfectly coherent)")

results["phase_coherence"] = {
    "n_forms": n_forms,
    "n_primes_tested": len(phase_uniformity),
    "cross_form_correlation": {
        "n_pairs": len(cross_corrs),
        "mean": float(np.mean(cross_corrs)),
        "std": float(np.std(cross_corrs)),
        "min": float(np.min(cross_corrs)),
        "max": float(np.max(cross_corrs)),
        "large_corr_fraction": float(np.mean(np.abs(cross_corrs) > 0.3))
    },
    "phase_uniformity": {
        "n_passing": n_uniform,
        "n_tested": len(phase_uniformity),
        "fraction_uniform": n_uniform / len(phase_uniformity) if phase_uniformity else 0,
        "per_prime": phase_uniformity[:10]  # first 10 for brevity
    },
    "circular_variance": {
        "mean": float(mean_circ_var),
        "interpretation": "high" if mean_circ_var > 0.8 else "moderate" if mean_circ_var > 0.5 else "low"
    }
}

# ─── 7. Additional: nearest-neighbor spacing distribution (GOE test) ─────────

print(f"\n=== Nearest-Neighbor Spacing vs GOE/GUE ===")
print("NOTE: Dataset ~77% complete; missing forms create artificial large gaps.")
print("Testing both full range and low-R region (more complete).\n")

def wigner_cdf(s):
    return 1 - np.exp(-np.pi * s**2 / 4)

def poisson_cdf(s):
    return 1 - np.exp(-s)

spacing_goe_results = {}

# For each symmetry class, compare to Wigner surmise
for label, Rs in [("Even", even_Rs), ("Odd", odd_Rs)]:
    spacing_goe_results[label.lower()] = {}
    for sublabel, R_cut in [("full", None), ("R<50", 50), ("R<100", 100)]:
        if R_cut is not None:
            Rs_sub = Rs[Rs < R_cut]
        else:
            Rs_sub = Rs
        if len(Rs_sub) < 20:
            continue

        spacings = np.diff(Rs_sub)
        # Normalize by LOCAL mean spacing from Weyl: mean spacing ~ 6/R for each class
        # Or just normalize by empirical mean
        s = spacings / np.mean(spacings)

        ks_goe, pval_goe = sp_stats.kstest(s, wigner_cdf)
        ks_poi, pval_poi = sp_stats.kstest(s, poisson_cdf)

        verdict = "GOE" if pval_goe > pval_poi else "Poisson"
        print(f"  {label} {sublabel} (n={len(Rs_sub)}):")
        print(f"    GOE Wigner: KS={ks_goe:.6f}, p={pval_goe:.6f}")
        print(f"    Poisson:    KS={ks_poi:.6f}, p={pval_poi:.6f}")
        print(f"    Verdict: {verdict}-like")

        spacing_goe_results[label.lower()][sublabel] = {
            "n_forms": len(Rs_sub),
            "ks_goe": float(ks_goe), "pval_goe": float(pval_goe),
            "ks_poisson": float(ks_poi), "pval_poisson": float(pval_poi),
            "verdict": verdict
        }

results["spacing_goe_test"] = spacing_goe_results

# ─── Summary ──────────────────────────────────────────────────────────────────

print(f"\n{'='*60}")
print(f"SUMMARY: Level-1 Maass Form Characterization")
print(f"{'='*60}")
print(f"Total forms: {len(rigor_l1)} (2202 with spectral params, {len(coeff_l1)} with coefficients)")
print(f"Weyl law: a/(1/12) = {weyl_ratio:.4f} ({'consistent' if abs(weyl_ratio-1)<0.05 else 'deviation'})")
print(f"Even/Odd: {len(even_Rs)}/{len(odd_Rs)} = {len(even_Rs)/len(odd_Rs):.3f}")
print(f"M4/M2² = {M4/M2**2:.4f} (Catalan predicts 2.0)")
print(f"M6/M2³ = {M6/M2**3:.4f} (Catalan predicts 5.0)")
print(f"Ramanujan violations: {ramanujan_violations*100:.2f}%")
print(f"Phase coherence: circular variance = {mean_circ_var:.4f}")
print(f"KL divergence from Sato-Tate: {kl_div:.6f}")

results["summary"] = {
    "total_forms_spectral": len(rigor_l1),
    "total_forms_coefficients": len(coeff_l1_rich),
    "weyl_consistent": abs(weyl_ratio - 1) < 0.05,
    "weyl_ratio": float(weyl_ratio),
    "even_odd_ratio": float(len(even_Rs) / len(odd_Rs)),
    "M4_M2sq": float(M4/M2**2),
    "M6_M2_cubed": float(M6/M2**3),
    "catalan_M4_deviation_pct": float(abs(M4/M2**2 - 2) / 2 * 100),
    "catalan_M6_deviation_pct": float(abs(M6/M2**3 - 5) / 5 * 100),
    "ramanujan_violation_pct": float(ramanujan_violations * 100),
    "kl_from_sato_tate": float(kl_div),
    "phase_circular_variance": float(mean_circ_var),
    "phase_uniformity_fraction": float(n_uniform / len(phase_uniformity)) if phase_uniformity else 0
}

# ─── Save ─────────────────────────────────────────────────────────────────────

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

out_path = Path(__file__).resolve().parent / "maass_level1_deep_results.json"
with open(out_path, "w") as f:
    json.dump(results, f, indent=2, cls=NumpyEncoder)
print(f"\nResults saved to {out_path}")
