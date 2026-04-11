"""
Challenge: Maass "CM-Like" Forms — Characterize Low-Entropy Forms at Composite Levels
Finding #310 showed Maass entropy is NOT level-independent.
Small composite levels (36, 72, 100) host low-entropy forms (2.6-3.2 bits vs 5.2 bits at primes).

This script:
1. Computes Shannon entropy of coefficient distributions for all Maass forms
2. Identifies the bottom 5% by entropy
3. Characterizes: level clustering, coefficient distributions, phase coherence,
   spectral parameter distribution
4. Tests whether these are the Maass analogue of CM forms
"""

import json
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path
import math
from sympy import isprime, factorint

# ── Load data ──────────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent.parent / "maass" / "data" / "maass_with_coefficients.json"
OUTPUT_PATH = Path(__file__).parent / "maass_cm_like_results.json"

with open(DATA_PATH) as f:
    forms = json.load(f)

print(f"Loaded {len(forms)} Maass forms across {len(set(d['level'] for d in forms))} levels")

# ── 1. Compute entropy for each form ──────────────────────────────────────
def coefficient_entropy(coeffs, n_bins=50):
    """Shannon entropy of the coefficient distribution (histogram-based)."""
    arr = np.array(coeffs, dtype=float)
    if len(arr) < 10:
        return np.nan
    # Histogram with fixed bin count
    counts, _ = np.histogram(arr, bins=n_bins)
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs))

def phase_coherence(coeffs):
    """
    Phase coherence: treat coefficients as a signal, compute mean resultant length
    of the phases (angles of complex FFT). High coherence = peaked phase distribution.
    """
    arr = np.array(coeffs, dtype=float)
    if len(arr) < 10:
        return np.nan
    ft = np.fft.fft(arr)
    phases = np.angle(ft[1:len(ft)//2])  # skip DC
    # Mean resultant length (0 = uniform phases, 1 = all aligned)
    return float(np.abs(np.mean(np.exp(1j * phases))))

def coefficient_sparsity(coeffs):
    """Fraction of coefficients near zero (|c| < 0.01)."""
    arr = np.array(coeffs, dtype=float)
    return float(np.mean(np.abs(arr) < 0.01))

def coefficient_kurtosis(coeffs):
    """Excess kurtosis — high means peaked/heavy-tailed."""
    arr = np.array(coeffs, dtype=float)
    if len(arr) < 4 or np.std(arr) < 1e-12:
        return np.nan
    m = np.mean(arr)
    s = np.std(arr)
    return float(np.mean(((arr - m) / s) ** 4) - 3.0)

print("Computing entropy, phase coherence, sparsity, kurtosis for all forms...")

for form in forms:
    coeffs = form['coefficients']
    form['entropy'] = coefficient_entropy(coeffs)
    form['phase_coherence'] = phase_coherence(coeffs)
    form['sparsity'] = coefficient_sparsity(coeffs)
    form['kurtosis'] = coefficient_kurtosis(coeffs)
    form['R'] = float(form['spectral_parameter'])

# Filter out forms with NaN entropy
valid_forms = [f for f in forms if not np.isnan(f['entropy'])]
print(f"Valid forms (entropy computable): {len(valid_forms)}")

# ── 2. Identify bottom 5% by entropy ─────────────────────────────────────
entropies = np.array([f['entropy'] for f in valid_forms])
threshold = np.percentile(entropies, 5)
print(f"\nEntropy threshold (5th percentile): {threshold:.4f} bits")
print(f"Median entropy: {np.median(entropies):.4f} bits")
print(f"Mean entropy: {np.mean(entropies):.4f} bits")

low_entropy = [f for f in valid_forms if f['entropy'] <= threshold]
high_entropy = [f for f in valid_forms if f['entropy'] > np.percentile(entropies, 50)]
print(f"Low-entropy forms: {len(low_entropy)}")

# ── 3. Level clustering ──────────────────────────────────────────────────
le_levels = Counter(f['level'] for f in low_entropy)
all_levels = Counter(f['level'] for f in valid_forms)

print("\n── Level Clustering of Low-Entropy Forms ──")
print(f"{'Level':>6} {'Count':>6} {'Total':>6} {'Frac':>8} {'Prime?':>7} {'Factorization'}")
enrichment_data = []
for level, count in le_levels.most_common(30):
    total = all_levels[level]
    frac = count / total if total > 0 else 0
    is_prime = isprime(level)
    factors = factorint(level)
    factor_str = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(factors.items()))
    enrichment = (count / len(low_entropy)) / (total / len(valid_forms)) if total > 0 else 0
    enrichment_data.append({
        'level': int(level),
        'low_entropy_count': int(count),
        'total_count': int(total),
        'fraction_low_entropy': round(frac, 4),
        'enrichment': round(enrichment, 3),
        'is_prime': bool(is_prime),
        'factorization': factor_str
    })
    print(f"{level:>6} {count:>6} {total:>6} {frac:>8.3f} {'  Y' if is_prime else '  N':>7} {factor_str}")

# ── Prime vs Composite level analysis ────────────────────────────────────
prime_forms = [f for f in valid_forms if isprime(f['level'])]
composite_forms = [f for f in valid_forms if not isprime(f['level'])]

prime_entropies = [f['entropy'] for f in prime_forms]
composite_entropies = [f['entropy'] for f in composite_forms]

print(f"\n── Prime vs Composite Entropy ──")
print(f"Prime levels:     mean={np.mean(prime_entropies):.4f}, median={np.median(prime_entropies):.4f}, std={np.std(prime_entropies):.4f}")
print(f"Composite levels: mean={np.mean(composite_entropies):.4f}, median={np.median(composite_entropies):.4f}, std={np.std(composite_entropies):.4f}")

# What fraction of low-entropy forms are at composite levels?
le_composite = sum(1 for f in low_entropy if not isprime(f['level']))
le_prime = sum(1 for f in low_entropy if isprime(f['level']))
print(f"\nLow-entropy: {le_composite} composite ({100*le_composite/len(low_entropy):.1f}%), {le_prime} prime ({100*le_prime/len(low_entropy):.1f}%)")
print(f"All forms:   {len(composite_forms)} composite ({100*len(composite_forms)/len(valid_forms):.1f}%), {len(prime_forms)} prime ({100*len(prime_forms)/len(valid_forms):.1f}%)")

# ── 4. Coefficient distributions ─────────────────────────────────────────
print("\n── Coefficient Distributions ──")
le_sparsities = [f['sparsity'] for f in low_entropy]
he_sparsities = [f['sparsity'] for f in high_entropy]
le_kurtoses = [f['kurtosis'] for f in low_entropy if not np.isnan(f['kurtosis'])]
he_kurtoses = [f['kurtosis'] for f in high_entropy if not np.isnan(f['kurtosis'])]

print(f"Sparsity (frac near zero):  low-E={np.mean(le_sparsities):.4f}  high-E={np.mean(he_sparsities):.4f}")
print(f"Kurtosis (excess):          low-E={np.mean(le_kurtoses):.4f}  high-E={np.mean(he_kurtoses):.4f}")

# Coefficient magnitude stats
le_coeff_stds = [np.std(f['coefficients']) for f in low_entropy]
he_coeff_stds = [np.std(f['coefficients']) for f in high_entropy]
le_coeff_maxs = [np.max(np.abs(f['coefficients'])) for f in low_entropy]
he_coeff_maxs = [np.max(np.abs(f['coefficients'])) for f in high_entropy]

print(f"Coeff std:                  low-E={np.mean(le_coeff_stds):.4f}  high-E={np.mean(he_coeff_stds):.4f}")
print(f"Coeff max|c|:               low-E={np.mean(le_coeff_maxs):.4f}  high-E={np.mean(he_coeff_maxs):.4f}")

# ── 5. Phase coherence ──────────────────────────────────────────────────
print("\n── Phase Coherence ──")
le_coherence = [f['phase_coherence'] for f in low_entropy if not np.isnan(f['phase_coherence'])]
he_coherence = [f['phase_coherence'] for f in high_entropy if not np.isnan(f['phase_coherence'])]
all_coherence = [f['phase_coherence'] for f in valid_forms if not np.isnan(f['phase_coherence'])]

print(f"Phase coherence:  low-E={np.mean(le_coherence):.6f}  high-E={np.mean(he_coherence):.6f}  all={np.mean(all_coherence):.6f}")
print(f"Phase coherence std: low-E={np.std(le_coherence):.6f}  high-E={np.std(he_coherence):.6f}")

# ── 6. Spectral parameter (R) distribution ──────────────────────────────
print("\n── Spectral Parameter R Distribution ──")
le_R = [f['R'] for f in low_entropy]
he_R = [f['R'] for f in high_entropy]
all_R = [f['R'] for f in valid_forms]

print(f"R:  low-E mean={np.mean(le_R):.4f} median={np.median(le_R):.4f} std={np.std(le_R):.4f}")
print(f"R:  high-E mean={np.mean(he_R):.4f} median={np.median(he_R):.4f} std={np.std(he_R):.4f}")
print(f"R:  all    mean={np.mean(all_R):.4f} median={np.median(all_R):.4f} std={np.std(all_R):.4f}")

# Fraction with R < 5 (low spectral parameter)
le_low_R = sum(1 for r in le_R if r < 5) / len(le_R)
he_low_R = sum(1 for r in he_R if r < 5) / len(he_R)
print(f"Fraction with R < 5:  low-E={le_low_R:.4f}  high-E={he_low_R:.4f}")

le_low_R2 = sum(1 for r in le_R if r < 2) / len(le_R)
he_low_R2 = sum(1 for r in he_R if r < 2) / len(he_R)
print(f"Fraction with R < 2:  low-E={le_low_R2:.4f}  high-E={he_low_R2:.4f}")

# ── 7. CM-like test: coefficient periodicity at divisors ─────────────────
print("\n── CM-Like Periodicity Test ──")

def test_coefficient_periodicity(coeffs, level):
    """
    CM forms have coefficient patterns governed by the CM character.
    Test: are coefficients at indices coprime to level more structured
    than at indices sharing factors with level?
    Also test: does c(p) = 0 for primes p in a specific residue class mod level?
    """
    arr = np.array(coeffs, dtype=float)
    n = len(arr)
    factors = factorint(level)
    primes_dividing = list(factors.keys())

    # Split: indices sharing a factor with level vs coprime
    coprime_coeffs = []
    shared_coeffs = []
    for i in range(1, n):
        if any(i % p == 0 for p in primes_dividing):
            shared_coeffs.append(arr[i])
        else:
            coprime_coeffs.append(arr[i])

    if len(coprime_coeffs) < 5 or len(shared_coeffs) < 5:
        return None

    coprime_std = np.std(coprime_coeffs)
    shared_std = np.std(shared_coeffs)

    # Vanishing test: fraction of near-zero coefficients at multiples of primes dividing level
    shared_vanishing = np.mean(np.abs(np.array(shared_coeffs)) < 0.05)
    coprime_vanishing = np.mean(np.abs(np.array(coprime_coeffs)) < 0.05)

    return {
        'coprime_std': float(coprime_std),
        'shared_std': float(shared_std),
        'std_ratio': float(shared_std / coprime_std) if coprime_std > 1e-12 else None,
        'shared_vanishing_rate': float(shared_vanishing),
        'coprime_vanishing_rate': float(coprime_vanishing),
        'vanishing_enrichment': float(shared_vanishing / coprime_vanishing) if coprime_vanishing > 1e-6 else None
    }

# Run CM test on low-entropy composite forms
le_composite_forms = [f for f in low_entropy if not isprime(f['level']) and f['level'] > 1]
he_composite_forms = [f for f in high_entropy if not isprime(f['level']) and f['level'] > 1]

le_cm_results = []
for f in le_composite_forms:
    r = test_coefficient_periodicity(f['coefficients'], f['level'])
    if r:
        le_cm_results.append(r)

he_cm_results = []
for f in he_composite_forms[:500]:  # sample
    r = test_coefficient_periodicity(f['coefficients'], f['level'])
    if r:
        he_cm_results.append(r)

if le_cm_results:
    le_std_ratios = [r['std_ratio'] for r in le_cm_results if r['std_ratio'] is not None]
    he_std_ratios = [r['std_ratio'] for r in he_cm_results if r['std_ratio'] is not None]
    le_vanishing_enrich = [r['vanishing_enrichment'] for r in le_cm_results if r['vanishing_enrichment'] is not None]
    he_vanishing_enrich = [r['vanishing_enrichment'] for r in he_cm_results if r['vanishing_enrichment'] is not None]

    print(f"Std ratio (shared/coprime):     low-E={np.mean(le_std_ratios):.4f}  high-E={np.mean(he_std_ratios):.4f}")
    print(f"Vanishing enrichment at level:  low-E={np.mean(le_vanishing_enrich):.4f}  high-E={np.mean(he_vanishing_enrich):.4f}")
    print(f"  (>1 means coefficients at multiples of level-primes vanish more often)")

# ── 8. Symmetry distribution ────────────────────────────────────────────
print("\n── Symmetry Distribution ──")
le_sym = Counter(f['symmetry'] for f in low_entropy)
he_sym = Counter(f['symmetry'] for f in high_entropy)
print(f"Low-E symmetry: {dict(le_sym)} => even frac = {le_sym.get(1,0)/len(low_entropy):.3f}")
print(f"High-E symmetry: {dict(he_sym)} => even frac = {he_sym.get(1,0)/len(high_entropy):.3f}")

# ── 9. Coefficient count bias ───────────────────────────────────────────
print("\n── Coefficient Count Bias ──")
le_ncoeffs = [f['n_coefficients'] for f in low_entropy]
he_ncoeffs = [f['n_coefficients'] for f in high_entropy]
print(f"n_coefficients:  low-E mean={np.mean(le_ncoeffs):.0f} median={np.median(le_ncoeffs):.0f}")
print(f"n_coefficients:  high-E mean={np.mean(he_ncoeffs):.0f} median={np.median(he_ncoeffs):.0f}")
print(f"(If low-E forms have fewer coefficients, entropy difference may be a length artifact)")

# Check: does entropy correlate with n_coefficients?
from scipy import stats
r_corr, p_corr = stats.pearsonr(
    [f['n_coefficients'] for f in valid_forms],
    [f['entropy'] for f in valid_forms]
)
print(f"Entropy-vs-n_coefficients correlation: r={r_corr:.4f}, p={p_corr:.2e}")

# Control: recompute entropy using only first N coefficients for all forms
MIN_COEFFS = min(f['n_coefficients'] for f in valid_forms)
print(f"\nControlling for coefficient count: truncating all to {MIN_COEFFS} coefficients...")

for form in valid_forms:
    form['entropy_controlled'] = coefficient_entropy(form['coefficients'][:MIN_COEFFS])

entropies_ctrl = np.array([f['entropy_controlled'] for f in valid_forms])
threshold_ctrl = np.percentile(entropies_ctrl, 5)
low_entropy_ctrl = [f for f in valid_forms if f['entropy_controlled'] <= threshold_ctrl]
print(f"Controlled entropy threshold: {threshold_ctrl:.4f} bits")
print(f"Low-entropy (controlled) forms: {len(low_entropy_ctrl)}")

# Overlap with original low-entropy set
le_ids = set(f['maass_id'] for f in low_entropy)
le_ctrl_ids = set(f['maass_id'] for f in low_entropy_ctrl)
overlap = le_ids & le_ctrl_ids
print(f"Overlap with uncontrolled low-E: {len(overlap)}/{len(le_ids)} ({100*len(overlap)/len(le_ids):.1f}%)")

le_ctrl_levels = Counter(f['level'] for f in low_entropy_ctrl)
le_ctrl_composite = sum(1 for f in low_entropy_ctrl if not isprime(f['level']))
print(f"Controlled low-E: {le_ctrl_composite} composite ({100*le_ctrl_composite/len(low_entropy_ctrl):.1f}%)")
print(f"Top levels (controlled):", le_ctrl_levels.most_common(15))

# ── 10. Build per-level entropy profile ──────────────────────────────────
print("\n── Per-Level Entropy Profile ──")
level_entropies = defaultdict(list)
for f in valid_forms:
    level_entropies[f['level']].append(f['entropy_controlled'])

level_profiles = []
for level in sorted(level_entropies.keys()):
    ents = level_entropies[level]
    if len(ents) >= 3:
        profile = {
            'level': int(level),
            'count': len(ents),
            'mean_entropy': round(float(np.mean(ents)), 4),
            'median_entropy': round(float(np.median(ents)), 4),
            'std_entropy': round(float(np.std(ents)), 4),
            'min_entropy': round(float(np.min(ents)), 4),
            'is_prime': bool(isprime(level)),
            'factorization': " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(factorint(level).items()))
        }
        level_profiles.append(profile)

# Sort by mean entropy
level_profiles.sort(key=lambda x: x['mean_entropy'])
print(f"\n{'Level':>6} {'N':>5} {'Mean':>8} {'Med':>8} {'Min':>8} {'Prime?':>7} {'Factors'}")
for p in level_profiles[:20]:
    print(f"{p['level']:>6} {p['count']:>5} {p['mean_entropy']:>8.4f} {p['median_entropy']:>8.4f} {p['min_entropy']:>8.4f} {'  Y' if p['is_prime'] else '  N':>7} {p['factorization']}")

# ── 11. Highly composite level enrichment ────────────────────────────────
print("\n── Divisor Count vs Entropy ──")
from sympy import divisor_count
level_div_ent = []
for prof in level_profiles:
    dc = int(divisor_count(prof['level']))
    level_div_ent.append((dc, prof['mean_entropy'], prof['level']))

divs = [x[0] for x in level_div_ent]
ents_prof = [x[1] for x in level_div_ent]
r_div, p_div = stats.pearsonr(divs, ents_prof)
print(f"Divisor-count vs mean-entropy correlation: r={r_div:.4f}, p={p_div:.2e}")

# ── COMPILE RESULTS ──────────────────────────────────────────────────────
print("\n" + "="*70)
print("COMPILING RESULTS")
print("="*70)

# Determine verdict
composite_enrichment = (le_composite / len(low_entropy)) / (len(composite_forms) / len(valid_forms))
coeff_artifact = abs(r_corr) > 0.3
controlled_overlap_pct = 100 * len(overlap) / len(le_ids)

results = {
    "challenge": "Maass CM-Like Forms: Characterize Low-Entropy Forms at Composite Levels",
    "challenge_number": "Finding #310 follow-up",
    "n_forms": len(valid_forms),
    "n_levels": len(set(f['level'] for f in valid_forms)),
    "entropy_stats": {
        "threshold_5pct": round(float(threshold), 4),
        "threshold_5pct_controlled": round(float(threshold_ctrl), 4),
        "median": round(float(np.median(entropies)), 4),
        "mean": round(float(np.mean(entropies)), 4),
        "n_low_entropy": len(low_entropy),
        "n_low_entropy_controlled": len(low_entropy_ctrl),
        "controlled_overlap_pct": round(controlled_overlap_pct, 1),
    },
    "level_clustering": {
        "low_entropy_composite_fraction": round(le_composite / len(low_entropy), 4),
        "all_forms_composite_fraction": round(len(composite_forms) / len(valid_forms), 4),
        "composite_enrichment_in_low_entropy": round(composite_enrichment, 3),
        "controlled_composite_fraction": round(le_ctrl_composite / len(low_entropy_ctrl), 4),
        "top_enriched_levels": enrichment_data[:15],
        "level_profiles_lowest_20": level_profiles[:20],
    },
    "coefficient_distributions": {
        "sparsity_low_E": round(float(np.mean(le_sparsities)), 4),
        "sparsity_high_E": round(float(np.mean(he_sparsities)), 4),
        "kurtosis_low_E": round(float(np.mean(le_kurtoses)), 4),
        "kurtosis_high_E": round(float(np.mean(he_kurtoses)), 4),
        "coeff_std_low_E": round(float(np.mean(le_coeff_stds)), 4),
        "coeff_std_high_E": round(float(np.mean(he_coeff_stds)), 4),
    },
    "phase_coherence": {
        "low_E_mean": round(float(np.mean(le_coherence)), 6),
        "high_E_mean": round(float(np.mean(he_coherence)), 6),
        "all_mean": round(float(np.mean(all_coherence)), 6),
        "coherence_ratio": round(float(np.mean(le_coherence) / np.mean(he_coherence)), 4) if np.mean(he_coherence) > 0 else None,
    },
    "spectral_parameter": {
        "R_low_E_mean": round(float(np.mean(le_R)), 4),
        "R_high_E_mean": round(float(np.mean(he_R)), 4),
        "R_low_E_median": round(float(np.median(le_R)), 4),
        "R_high_E_median": round(float(np.median(he_R)), 4),
        "frac_R_lt_5_low_E": round(le_low_R, 4),
        "frac_R_lt_5_high_E": round(he_low_R, 4),
        "frac_R_lt_2_low_E": round(le_low_R2, 4),
        "frac_R_lt_2_high_E": round(he_low_R2, 4),
    },
    "cm_like_test": {
        "std_ratio_low_E": round(float(np.mean(le_std_ratios)), 4) if le_std_ratios else None,
        "std_ratio_high_E": round(float(np.mean(he_std_ratios)), 4) if he_std_ratios else None,
        "vanishing_enrichment_low_E": round(float(np.mean(le_vanishing_enrich)), 4) if le_vanishing_enrich else None,
        "vanishing_enrichment_high_E": round(float(np.mean(he_vanishing_enrich)), 4) if he_vanishing_enrich else None,
    },
    "symmetry": {
        "even_fraction_low_E": round(le_sym.get(1, 0) / len(low_entropy), 4),
        "even_fraction_high_E": round(he_sym.get(1, 0) / len(high_entropy), 4),
    },
    "artifact_controls": {
        "entropy_vs_ncoeff_correlation": round(float(r_corr), 4),
        "entropy_vs_ncoeff_pvalue": float(p_corr),
        "is_length_artifact": bool(coeff_artifact),
        "ncoeff_mean_low_E": round(float(np.mean(le_ncoeffs)), 0),
        "ncoeff_mean_high_E": round(float(np.mean(he_ncoeffs)), 0),
        "min_coefficients_used_in_control": int(MIN_COEFFS),
    },
    "divisor_count_correlation": {
        "r": round(float(r_div), 4),
        "p": float(p_div),
    },
}

# ── Verdict ──────────────────────────────────────────────────────────────
verdicts = []
if composite_enrichment > 1.3:
    verdicts.append(f"CONFIRMED: composite levels enriched {composite_enrichment:.2f}x in low-entropy tail")
else:
    verdicts.append(f"WEAK/ABSENT: composite enrichment only {composite_enrichment:.2f}x")

if coeff_artifact:
    verdicts.append(f"WARNING: entropy correlates with n_coefficients (r={r_corr:.3f}) — possible length artifact")
    if controlled_overlap_pct > 60:
        verdicts.append(f"BUT: {controlled_overlap_pct:.0f}% overlap survives length control — effect is real")
    else:
        verdicts.append(f"AND: only {controlled_overlap_pct:.0f}% overlap after control — likely artifact")

coherence_ratio = np.mean(le_coherence) / np.mean(he_coherence) if np.mean(he_coherence) > 0 else 1
if coherence_ratio > 1.5:
    verdicts.append(f"Phase coherence {coherence_ratio:.2f}x higher in low-E — supports CM-like interpretation")
elif coherence_ratio > 1.1:
    verdicts.append(f"Phase coherence mildly elevated ({coherence_ratio:.2f}x) in low-E")
else:
    verdicts.append(f"No phase coherence difference ({coherence_ratio:.2f}x)")

le_vanishing_mean = np.mean(le_vanishing_enrich) if le_vanishing_enrich else 1
if le_vanishing_mean > 2:
    verdicts.append(f"CM signature: coefficients at level-multiples vanish {le_vanishing_mean:.1f}x more in low-E composites")
elif le_vanishing_mean > 1.3:
    verdicts.append(f"Mild CM signature: vanishing enrichment {le_vanishing_mean:.2f}x at level-multiples")
else:
    verdicts.append(f"No CM vanishing signature (enrichment {le_vanishing_mean:.2f}x)")

results["verdicts"] = verdicts

for v in verdicts:
    print(f"  >> {v}")

# ── Save ──────────────────────────────────────────────────────────────────
with open(OUTPUT_PATH, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {OUTPUT_PATH}")
