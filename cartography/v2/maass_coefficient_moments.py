#!/usr/bin/env python3
"""
Maass Form Spectral Parameter Analysis
=======================================

Fourier/Hecke coefficients are NOT available in our LMFDB Maass data
(35,416 forms from maass_rigor table). Available fields: label, level,
weight, character, spectral_parameter, symmetry, fricke.

Since we cannot compute M2/M4 of Fourier coefficients, we instead:
  1. Report data inventory (what IS available)
  2. Spectral parameter distribution statistics
  3. Level distribution
  4. Symmetry breakdown (even vs odd)
  5. Fricke eigenvalue distribution
  6. Spectral parameter spacing statistics (nearest-neighbor gaps)
  7. Compare spectral parameter statistics by symmetry class

Reference holomorphic results: M2=0.984, M4=1.957 (from moment_universality.py)
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter
from datetime import datetime


def load_maass_data():
    """Load the rigor dataset (35K forms, high-precision spectral parameters)."""
    path = Path(__file__).resolve().parent.parent / "maass" / "data" / "maass_rigor_full.json"
    with open(path) as f:
        data = json.load(f)
    return data["records"], data.get("total_records", len(data["records"]))


def spectral_parameter_stats(records):
    """Compute distribution statistics for spectral parameters."""
    params = np.array([float(r["spectral_parameter"]) for r in records])
    return {
        "count": len(params),
        "min": float(np.min(params)),
        "max": float(np.max(params)),
        "mean": float(np.mean(params)),
        "median": float(np.median(params)),
        "std": float(np.std(params)),
        "q25": float(np.percentile(params, 25)),
        "q75": float(np.percentile(params, 75)),
        "skewness": float(skewness(params)),
        "kurtosis_excess": float(kurtosis_excess(params)),
    }


def skewness(arr):
    m = np.mean(arr)
    s = np.std(arr)
    if s == 0:
        return 0.0
    return float(np.mean(((arr - m) / s) ** 3))


def kurtosis_excess(arr):
    m = np.mean(arr)
    s = np.std(arr)
    if s == 0:
        return 0.0
    return float(np.mean(((arr - m) / s) ** 4) - 3.0)


def level_distribution(records):
    """Level frequency distribution."""
    levels = [r["level"] for r in records]
    ctr = Counter(levels)
    # Top 20 most common
    top = ctr.most_common(20)
    return {
        "unique_levels": len(ctr),
        "top_20": [{"level": lv, "count": ct} for lv, ct in top],
        "level_range": [min(levels), max(levels)],
    }


def symmetry_breakdown(records):
    """Even (0) vs odd (1) symmetry."""
    ctr = Counter(r["symmetry"] for r in records)
    total = len(records)
    return {
        "even_count": ctr.get(0, 0),
        "odd_count": ctr.get(1, 0),
        "even_fraction": round(ctr.get(0, 0) / total, 4),
        "odd_fraction": round(ctr.get(1, 0) / total, 4),
    }


def fricke_distribution(records):
    """Fricke eigenvalue distribution."""
    ctr = Counter(r.get("fricke", r.get("fricke_eigenvalue")) for r in records)
    total = len(records)
    return {str(k): {"count": v, "fraction": round(v / total, 4)} for k, v in ctr.items()}


def spectral_spacing_analysis(records):
    """Nearest-neighbor spacing statistics for spectral parameters.

    For level-1 forms within a single symmetry class, the spectral
    parameters should follow GOE-like statistics (level repulsion).
    Mixing symmetry classes destroys repulsion and gives Poisson.
    We compute both mixed and per-symmetry spacing.
    """
    from collections import defaultdict

    # Group by (level, symmetry)
    by_key = defaultdict(list)
    by_level = defaultdict(list)
    for r in records:
        by_level[r["level"]].append(float(r["spectral_parameter"]))
        by_key[(r["level"], r["symmetry"])].append(float(r["spectral_parameter"]))

    results = {}

    def compute_gap_stats(params_sorted, label):
        if len(params_sorted) < 20:
            return None
        gaps = np.diff(params_sorted)
        mean_gap = np.mean(gaps)
        if mean_gap == 0:
            return None
        normalized_gaps = gaps / mean_gap
        obs_var = float(np.var(normalized_gaps))
        if obs_var < 0.3:
            interp = "GUE/GOE-like (level repulsion)"
        elif obs_var < 0.6:
            interp = "intermediate"
        else:
            interp = "Poisson-like (no repulsion)"
        return {
            "label": label,
            "num_forms": len(params_sorted),
            "num_gaps": len(gaps),
            "mean_gap": float(mean_gap),
            "normalized_gap_variance": obs_var,
            "normalized_gap_skewness": float(skewness(normalized_gaps)),
            "normalized_gap_kurtosis_excess": float(kurtosis_excess(normalized_gaps)),
            "goe_variance_reference": 0.286,
            "gue_variance_reference": 0.178,
            "poisson_variance_reference": 1.0,
            "interpretation": interp,
        }

    # Level 1, mixed symmetry (expect Poisson due to superposition)
    mixed = compute_gap_stats(sorted(by_level.get(1, [])), "level_1_mixed")
    if mixed:
        results["level_1_mixed"] = mixed

    # Level 1, even symmetry only (expect GOE)
    even = compute_gap_stats(sorted(by_key.get((1, 0), [])), "level_1_even")
    if even:
        results["level_1_even_symmetry"] = even

    # Level 1, odd symmetry only (expect GOE)
    odd = compute_gap_stats(sorted(by_key.get((1, 1), [])), "level_1_odd_symmetry")
    if odd:
        results["level_1_odd_symmetry"] = odd

    # Local unfolding: use k-NN local density to normalize gaps
    # This accounts for non-uniform spectral parameter density
    for sym_label, sym_val in [("even", 0), ("odd", 1)]:
        params = sorted(by_key.get((1, sym_val), []))
        if len(params) < 50:
            continue
        params = np.array(params)
        gaps = np.diff(params)
        # Local unfolding: normalize each gap by local mean of k neighbors
        k = 10
        local_gaps = []
        for i in range(len(gaps)):
            lo = max(0, i - k)
            hi = min(len(gaps), i + k + 1)
            local_mean = np.mean(gaps[lo:hi])
            if local_mean > 0:
                local_gaps.append(gaps[i] / local_mean)
        local_gaps = np.array(local_gaps)
        obs_var = float(np.var(local_gaps))
        if obs_var < 0.3:
            interp = "GUE/GOE-like (level repulsion)"
        elif obs_var < 0.6:
            interp = "intermediate"
        else:
            interp = "Poisson-like (no repulsion)"
        results[f"level_1_{sym_label}_locally_unfolded"] = {
            "label": f"level_1_{sym_label}_locally_unfolded (k={k})",
            "num_gaps": len(local_gaps),
            "normalized_gap_variance": obs_var,
            "normalized_gap_mean": float(np.mean(local_gaps)),
            "goe_variance_reference": 0.286,
            "gue_variance_reference": 0.178,
            "poisson_variance_reference": 1.0,
            "interpretation": interp,
        }

    return results


def spectral_stats_by_symmetry(records):
    """Compare spectral parameter distributions between even and odd forms."""
    even = [float(r["spectral_parameter"]) for r in records if r["symmetry"] == 0]
    odd = [float(r["spectral_parameter"]) for r in records if r["symmetry"] == 1]

    def stats(arr, label):
        a = np.array(arr)
        return {
            "label": label,
            "count": len(a),
            "mean": float(np.mean(a)),
            "std": float(np.std(a)),
            "median": float(np.median(a)),
            "min": float(np.min(a)),
            "max": float(np.max(a)),
        }

    return {
        "even": stats(even, "even (symmetry=0)"),
        "odd": stats(odd, "odd (symmetry=1)"),
    }


def main():
    records, total = load_maass_data()
    print(f"Loaded {len(records)} Maass forms (total_records={total})")

    # Check what fields are available
    sample = records[0]
    fields_available = list(sample.keys())
    has_coefficients = any(k in sample for k in
                          ["coefficients", "hecke_eigenvalues", "an", "ap",
                           "fourier_coefficients", "traces"])

    results = {
        "timestamp": datetime.now().isoformat(),
        "source": "LMFDB maass_rigor table (35,416 forms)",
        "data_inventory": {
            "total_forms": len(records),
            "fields_available": fields_available,
            "has_fourier_coefficients": has_coefficients,
            "note": "Fourier/Hecke coefficients NOT available in bulk LMFDB download. "
                    "Only spectral parameters and metadata. Individual form pages on "
                    "LMFDB do show coefficients, but the API/bulk export omits them.",
        },
        "coefficient_moment_comparison": {
            "holomorphic_reference": {
                "M2": 0.984,
                "M4": 1.957,
                "M4_over_M2_sq": round(1.957 / 0.984**2, 4),
                "note": "Weight-2 newforms, non-CM, from moment_universality.py",
            },
            "maass_prediction": {
                "M2_theory": 1.0,
                "M4_theory": 2.0,
                "M4_over_M2_sq_theory": 2.0,
                "note": "For generic (non-CM, non-dihedral) Maass forms with trivial "
                        "nebentypus, Hecke eigenvalues a(p)/sqrt(p) should follow "
                        "Sato-Tate (semicircle on [-2,2]). Same universality class "
                        "as holomorphic forms. Dihedral forms have different ST group.",
            },
            "status": "CANNOT_VERIFY — coefficients not in bulk data",
        },
        "spectral_parameter_statistics": {
            "all_forms": spectral_parameter_stats(records),
            "by_symmetry": spectral_stats_by_symmetry(records),
        },
        "level_distribution": level_distribution(records),
        "symmetry_breakdown": symmetry_breakdown(records),
        "fricke_eigenvalue_distribution": fricke_distribution(records),
        "spectral_spacing": spectral_spacing_analysis(records),
    }

    # Print summary
    print(f"\n=== Data Inventory ===")
    print(f"Fields: {fields_available}")
    print(f"Has Fourier coefficients: {has_coefficients}")

    print(f"\n=== Spectral Parameter Statistics ===")
    sp = results["spectral_parameter_statistics"]["all_forms"]
    for k, v in sp.items():
        print(f"  {k}: {v}")

    print(f"\n=== Symmetry Breakdown ===")
    sb = results["symmetry_breakdown"]
    print(f"  Even: {sb['even_count']} ({sb['even_fraction']:.1%})")
    print(f"  Odd:  {sb['odd_count']} ({sb['odd_fraction']:.1%})")

    print(f"\n=== Level Distribution ===")
    ld = results["level_distribution"]
    print(f"  Unique levels: {ld['unique_levels']}")
    print(f"  Range: {ld['level_range']}")
    print(f"  Top 5: {ld['top_20'][:5]}")

    print(f"\n=== Fricke Eigenvalue Distribution ===")
    for k, v in results["fricke_eigenvalue_distribution"].items():
        print(f"  fricke={k}: {v['count']} ({v['fraction']:.1%})")

    print(f"\n=== Spectral Spacing (Level 1) ===")
    for k, v in results["spectral_spacing"].items():
        print(f"  {k} ({v['label']}):")
        if "num_forms" in v:
            print(f"    Forms: {v['num_forms']}, Gaps: {v['num_gaps']}")
        else:
            print(f"    Gaps: {v['num_gaps']}")
        if "mean_gap" in v:
            print(f"    Mean gap: {v['mean_gap']:.6f}")
        print(f"    Normalized gap variance: {v['normalized_gap_variance']:.4f}")
        print(f"    GOE ref: {v['goe_variance_reference']}, GUE ref: {v['gue_variance_reference']}")
        print(f"    Interpretation: {v['interpretation']}")

    print(f"\n=== Coefficient Moment Comparison ===")
    print(f"  Holomorphic M2=0.984, M4=1.957 (measured)")
    print(f"  Maass predicted M2=1.0, M4=2.0 (Sato-Tate semicircle)")
    print(f"  Status: {results['coefficient_moment_comparison']['status']}")

    # Save
    outpath = Path(__file__).resolve().parent / "maass_coefficient_moments_results.json"
    with open(outpath, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {outpath}")


if __name__ == "__main__":
    main()
