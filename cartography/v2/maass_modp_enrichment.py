"""
Maass Coefficient Mod-p Enrichment Analysis
============================================
Tests whether the ~8x mod-p fingerprint enrichment law (found for EC/genus-2)
holds for Maass forms.

Method:
- For each prime p in {3,5,7,11}, discretize coefficients into p bins via quantiles
  (coefficients are real-valued in ~[-3,3], so floor-mod-p collapses for large p;
  quantile binning ensures uniform marginals and makes enrichment meaningful)
- Fingerprint = tuple of binned (a_2, a_3, ..., a_k) for fingerprint lengths k=2,3,4
- Within each level, compute fraction of pairs sharing fingerprint
- Enrichment = observed_agreement / expected_if_independent (global null)
- Detrend by comparing to cross-level random pairing baseline

Key design choice: Maass coefficients are continuous reals, not integers.
Floor-mod-p gives only ~4 distinct values ({-2,-1,0,1} mod p), making fingerprints
degenerate for p>=5. Quantile binning is the correct analog of mod-p reduction
for continuous data: it partitions the value space into p equi-populated bins,
so the "mod-p" label refers to the resolution (p classes), not literal modular arithmetic.
"""

import json
import numpy as np
from collections import Counter, defaultdict
import time
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "maass", "data", "maass_with_coefficients.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "maass_modp_enrichment_results.json")

PRIMES_TO_TEST = [3, 5, 7, 11]
FINGERPRINT_LENGTHS = [2, 3, 4]  # number of coefficients in fingerprint
COEFF_INDICES = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # a_2 through a_10 (0-indexed)
MAX_FORMS = 2000
MAX_LEVELS = 50
MIN_FORMS_PER_LEVEL = 20  # need enough pairs for stable statistics


def build_quantile_bins(all_coeffs, p):
    """Compute quantile boundaries for each coefficient index, splitting into p bins."""
    # all_coeffs: dict of index -> list of values across all sampled forms
    boundaries = {}
    for idx, vals in all_coeffs.items():
        arr = np.array(vals)
        quantiles = np.linspace(0, 100, p + 1)[1:-1]  # p-1 internal boundaries
        boundaries[idx] = np.percentile(arr, quantiles)
    return boundaries


def quantile_bin(value, boundaries):
    """Assign a value to a quantile bin (0 to p-1)."""
    return int(np.searchsorted(boundaries, value))


def make_fingerprint(coeffs, indices, boundaries):
    """Compute quantile-binned fingerprint for given coefficient indices."""
    return tuple(quantile_bin(coeffs[i], boundaries[i]) for i in indices if i < len(coeffs))


def compute_pair_agreement(fingerprints):
    """Fraction of pairs with identical fingerprints."""
    n = len(fingerprints)
    if n < 2:
        return 0.0, 0
    counts = Counter(fingerprints)
    agreeing = sum(c * (c - 1) // 2 for c in counts.values())
    total_pairs = n * (n - 1) // 2
    return agreeing / total_pairs, total_pairs


def compute_global_expected(all_fps):
    """Expected agreement from global fingerprint distribution = sum(freq_i^2)."""
    counts = Counter(all_fps)
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return sum((c / total) ** 2 for c in counts.values())


def permutation_null(level_fps_dict, n_perms=200):
    """
    Permutation null: shuffle forms across levels, recompute within-level agreement.
    Returns distribution of mean enrichments under null.
    """
    all_fps = []
    level_sizes = []
    for lv in sorted(level_fps_dict.keys()):
        fps = level_fps_dict[lv]
        all_fps.extend(fps)
        level_sizes.append(len(fps))

    global_expected = compute_global_expected(all_fps)
    if global_expected == 0:
        return []

    null_enrichments = []
    rng = np.random.RandomState(42)
    for _ in range(n_perms):
        shuffled = list(all_fps)
        rng.shuffle(shuffled)
        idx = 0
        perm_enrichments = []
        for sz in level_sizes:
            chunk = shuffled[idx:idx+sz]
            idx += sz
            obs, n_pairs = compute_pair_agreement(chunk)
            if n_pairs > 0 and global_expected > 0:
                perm_enrichments.append(obs / global_expected)
        if perm_enrichments:
            null_enrichments.append(np.mean(perm_enrichments))

    return null_enrichments


def run_analysis():
    print("Loading data...")
    with open(DATA_PATH) as f:
        data = json.load(f)
    print(f"Loaded {len(data)} Maass forms")

    # Group by level
    by_level = defaultdict(list)
    for form in data:
        by_level[form["level"]].append(form)

    # Select levels with enough forms
    eligible_levels = {lv: forms for lv, forms in by_level.items() if len(forms) >= MIN_FORMS_PER_LEVEL}
    sorted_levels = sorted(eligible_levels.keys(), key=lambda lv: -len(eligible_levels[lv]))[:MAX_LEVELS]
    print(f"Selected {len(sorted_levels)} levels (min {MIN_FORMS_PER_LEVEL} forms each)")

    # Subsample proportionally, up to MAX_FORMS total
    total_available = sum(len(eligible_levels[lv]) for lv in sorted_levels)
    sampled = {}
    total_sampled = 0
    for lv in sorted_levels:
        forms = eligible_levels[lv]
        n_take = max(MIN_FORMS_PER_LEVEL, int(len(forms) / total_available * MAX_FORMS))
        n_take = min(n_take, len(forms))
        forms_sorted = sorted(forms, key=lambda f: float(f["spectral_parameter"]))
        if n_take < len(forms_sorted):
            indices = np.linspace(0, len(forms_sorted) - 1, n_take, dtype=int)
            sampled[lv] = [forms_sorted[i] for i in indices]
        else:
            sampled[lv] = forms_sorted
        total_sampled += len(sampled[lv])
    print(f"Sampled {total_sampled} forms across {len(sampled)} levels")

    results = {
        "metadata": {
            "n_forms_total": len(data),
            "n_levels_tested": len(sorted_levels),
            "n_forms_sampled": total_sampled,
            "primes_tested": PRIMES_TO_TEST,
            "fingerprint_lengths": FINGERPRINT_LENGTHS,
            "coeff_indices_pool": COEFF_INDICES,
            "discretization": "quantile binning (p equi-populated bins per coefficient)",
            "min_forms_per_level": MIN_FORMS_PER_LEVEL,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        },
        "by_prime": {},
        "by_fingerprint_length": {},
        "level_dependence": {},
        "spectral_proximity": {},
        "permutation_null": {},
    }

    # Collect all coefficient values for quantile computation
    all_coeff_values = defaultdict(list)
    for lv in sorted_levels:
        for form in sampled[lv]:
            for idx in COEFF_INDICES:
                if idx < len(form["coefficients"]):
                    all_coeff_values[idx].append(form["coefficients"][idx])

    # =====================================================================
    # Main analysis: prime x fingerprint_length grid
    # =====================================================================
    for p in PRIMES_TO_TEST:
        print(f"\n{'='*60}")
        print(f"=== Prime p={p} ===")

        # Build quantile bins
        boundaries = build_quantile_bins(all_coeff_values, p)

        prime_results = {}

        for k in FINGERPRINT_LENGTHS:
            fp_indices = COEFF_INDICES[:k]
            print(f"\n  --- Fingerprint length k={k} (indices {fp_indices}) ---")

            # Compute fingerprints per level
            level_fps = {}
            all_fps_global = []
            for lv in sorted_levels:
                fps = [make_fingerprint(f["coefficients"], fp_indices, boundaries) for f in sampled[lv]]
                level_fps[lv] = fps
                all_fps_global.extend(fps)

            # Global null
            global_expected = compute_global_expected(all_fps_global)
            uniform_expected = 1.0 / (p ** k)
            n_unique_fps = len(set(all_fps_global))

            print(f"    Unique fingerprints: {n_unique_fps} / {p**k} possible")
            print(f"    Global expected agreement: {global_expected:.6f}")
            print(f"    Uniform expected (1/{p}^{k}): {uniform_expected:.6f}")

            # Per-level enrichment
            level_details = []
            level_enrichments = []

            for lv in sorted_levels:
                fps = level_fps[lv]
                observed, n_pairs = compute_pair_agreement(fps)
                enrichment = observed / global_expected if global_expected > 0 else 0.0

                level_enrichments.append(enrichment)
                level_details.append({
                    "level": int(lv),
                    "n_forms": len(fps),
                    "n_pairs": n_pairs,
                    "observed_agreement": round(observed, 8),
                    "enrichment_vs_global": round(enrichment, 4),
                })

            enrichments = np.array(level_enrichments)
            # Include zeros — they represent levels with no collisions
            mean_e = float(np.mean(enrichments))
            median_e = float(np.median(enrichments))
            valid = enrichments[enrichments > 0]

            print(f"    Mean enrichment: {mean_e:.2f}x")
            print(f"    Median enrichment: {median_e:.2f}x")
            print(f"    Levels with >0 agreement: {len(valid)}/{len(enrichments)}")
            if len(valid) > 0:
                print(f"    Among non-zero: mean={np.mean(valid):.2f}x, median={np.median(valid):.2f}x")

            # Permutation null test
            null_means = permutation_null(level_fps, n_perms=200)
            null_mean = float(np.mean(null_means)) if null_means else 1.0
            null_std = float(np.std(null_means)) if null_means else 0.0
            z_score = (mean_e - null_mean) / null_std if null_std > 0 else 0.0

            print(f"    Permutation null: mean={null_mean:.2f}x, std={null_std:.3f}")
            print(f"    Z-score vs null: {z_score:.2f}")

            prime_results[str(k)] = {
                "fingerprint_length": k,
                "n_unique_fingerprints": n_unique_fps,
                "n_possible_fingerprints": p ** k,
                "global_expected_agreement": round(global_expected, 8),
                "uniform_expected_agreement": round(uniform_expected, 8),
                "mean_enrichment": round(mean_e, 4),
                "median_enrichment": round(median_e, 4),
                "std_enrichment": round(float(np.std(enrichments)), 4),
                "n_levels_nonzero": int(len(valid)),
                "mean_enrichment_nonzero": round(float(np.mean(valid)), 4) if len(valid) > 0 else 0,
                "median_enrichment_nonzero": round(float(np.median(valid)), 4) if len(valid) > 0 else 0,
                "n_levels_gt_2x": int(np.sum(enrichments > 2)),
                "n_levels_gt_5x": int(np.sum(enrichments > 5)),
                "n_levels_gt_8x": int(np.sum(enrichments > 8)),
                "permutation_null_mean": round(null_mean, 4),
                "permutation_null_std": round(null_std, 4),
                "z_score_vs_null": round(z_score, 2),
                "level_details": sorted(level_details, key=lambda x: -x["enrichment_vs_global"])[:20],
            }

        results["by_prime"][str(p)] = prime_results

    # =====================================================================
    # Level dependence: does enrichment correlate with level number?
    # =====================================================================
    print(f"\n{'='*60}")
    print("=== Level dependence ===")
    # Use p=3, k=3 as reference
    ref_p, ref_k = 3, 3
    if str(ref_p) in results["by_prime"] and str(ref_k) in results["by_prime"][str(ref_p)]:
        details = results["by_prime"][str(ref_p)][str(ref_k)]["level_details"]
        levels_arr = np.array([d["level"] for d in details])
        enrich_arr = np.array([d["enrichment_vs_global"] for d in details])
        nforms_arr = np.array([d["n_forms"] for d in details])

        corr_level = float(np.corrcoef(levels_arr, enrich_arr)[0, 1]) if len(levels_arr) > 2 else 0
        corr_size = float(np.corrcoef(nforms_arr, enrich_arr)[0, 1]) if len(nforms_arr) > 2 else 0

        results["level_dependence"] = {
            "reference": f"p={ref_p}, k={ref_k}",
            "corr_level_vs_enrichment": round(corr_level, 4),
            "corr_level_size_vs_enrichment": round(corr_size, 4),
        }
        print(f"  corr(level, enrichment) = {corr_level:.4f}")
        print(f"  corr(n_forms, enrichment) = {corr_size:.4f}")

    # =====================================================================
    # Spectral proximity: do spectrally-close forms share fingerprints more?
    # =====================================================================
    print("\n=== Spectral proximity ===")
    for p in PRIMES_TO_TEST:
        boundaries = build_quantile_bins(all_coeff_values, p)
        fp_indices = COEFF_INDICES[:3]  # k=3

        close_matches = []
        far_matches = []

        for lv in sorted_levels:
            forms = sampled[lv]
            if len(forms) < 6:
                continue
            spectral = np.array([float(f["spectral_parameter"]) for f in forms])
            fps = [make_fingerprint(f["coefficients"], fp_indices, boundaries) for f in forms]

            order = np.argsort(spectral)
            sorted_fps = [fps[i] for i in order]
            n = len(sorted_fps)

            # Close: adjacent pairs
            for i in range(n - 1):
                close_matches.append(1 if sorted_fps[i] == sorted_fps[i + 1] else 0)

            # Far: pairs at distance n//2
            half = max(n // 2, 3)
            for i in range(n - half):
                far_matches.append(1 if sorted_fps[i] == sorted_fps[i + half] else 0)

        close_rate = float(np.mean(close_matches)) if close_matches else 0
        far_rate = float(np.mean(far_matches)) if far_matches else 0
        ratio = close_rate / far_rate if far_rate > 0 else float("inf")

        results["spectral_proximity"][str(p)] = {
            "fingerprint_length": 3,
            "close_agreement_rate": round(close_rate, 6),
            "far_agreement_rate": round(far_rate, 6),
            "close_to_far_ratio": round(ratio, 4) if ratio != float("inf") else "inf",
            "n_close_pairs": len(close_matches),
            "n_far_pairs": len(far_matches),
        }
        print(f"  p={p}: close={close_rate:.4f}, far={far_rate:.4f}, ratio={ratio:.2f}")

    # =====================================================================
    # Also run with floor-mod-p (original method) for comparison at k=2,3
    # =====================================================================
    print(f"\n{'='*60}")
    print("=== Floor-mod-p comparison (literal mod arithmetic) ===")
    floor_results = {}
    for p in PRIMES_TO_TEST:
        for k in [2, 3]:
            fp_indices = COEFF_INDICES[:k]
            all_fps = []
            level_fps_floor = {}
            for lv in sorted_levels:
                fps = [tuple(int(np.floor(f["coefficients"][i])) % p for i in fp_indices)
                       for f in sampled[lv]]
                level_fps_floor[lv] = fps
                all_fps.extend(fps)

            global_exp = compute_global_expected(all_fps)
            enrichments_floor = []
            for lv in sorted_levels:
                obs, n_pairs = compute_pair_agreement(level_fps_floor[lv])
                enrichments_floor.append(obs / global_exp if global_exp > 0 else 0)

            arr = np.array(enrichments_floor)
            n_unique = len(set(all_fps))
            mean_e = float(np.mean(arr))
            key = f"p{p}_k{k}"
            floor_results[key] = {
                "prime": p, "fingerprint_length": k,
                "n_unique": n_unique,
                "global_expected": round(global_exp, 8),
                "mean_enrichment": round(mean_e, 4),
                "median_enrichment": round(float(np.median(arr)), 4),
            }
            print(f"  p={p}, k={k}: unique={n_unique}, mean={mean_e:.2f}x, median={np.median(arr):.2f}x")

    results["floor_modp_comparison"] = floor_results

    # =====================================================================
    # Summary
    # =====================================================================
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    # Use k=3 across all primes as the canonical comparison
    canonical_k = 3
    enrichments_by_prime = {}
    for p in PRIMES_TO_TEST:
        e = results["by_prime"][str(p)][str(canonical_k)]["mean_enrichment"]
        enrichments_by_prime[str(p)] = e

    overall = np.mean(list(enrichments_by_prime.values()))
    medians_by_prime = {}
    for p in PRIMES_TO_TEST:
        medians_by_prime[str(p)] = results["by_prime"][str(p)][str(canonical_k)]["median_enrichment"]
    overall_median = np.mean(list(medians_by_prime.values()))

    # Verdict based on quantile-binned k=3 results
    if 4 <= overall <= 16:
        verdict = "CONSISTENT with EC/genus-2 ~8x law"
    elif overall > 16:
        verdict = "STRONGER than EC/genus-2 ~8x law"
    elif overall > 1.5:
        verdict = "WEAKER but present — enrichment exists, below 8x"
    else:
        verdict = "NO enrichment detected"

    results["summary"] = {
        "canonical_fingerprint_length": canonical_k,
        "discretization": "quantile binning",
        "mean_enrichment_by_prime": enrichments_by_prime,
        "median_enrichment_by_prime": medians_by_prime,
        "overall_mean_enrichment": round(float(overall), 4),
        "overall_median_enrichment": round(float(overall_median), 4),
        "ec_genus2_reference": "~8x after detrending",
        "verdict": verdict,
        "spectral_proximity_finding": (
            "Close spectral pairs show higher/lower/similar agreement "
            "compared to far pairs — see spectral_proximity section"
        ),
    }

    for p in PRIMES_TO_TEST:
        e = enrichments_by_prime[str(p)]
        m = medians_by_prime[str(p)]
        z = results["by_prime"][str(p)][str(canonical_k)]["z_score_vs_null"]
        print(f"  p={p}: mean={e:.2f}x, median={m:.2f}x, z={z:.1f}")
    print(f"\n  Overall mean: {overall:.2f}x (reference: ~8x)")
    print(f"  Overall median: {overall_median:.2f}x")
    print(f"  VERDICT: {verdict}")

    # Save
    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")

    return results


if __name__ == "__main__":
    run_analysis()
