"""
Jones Polynomial Zero Density (List2 #14)

Extract complex roots of Jones polynomials, measure radial density
at the unit circle boundary |z| = 1.

Compare to Alexander polynomial result (41.19% on unit circle from NF16).
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict

# --- Config ---
KNOTS_PATH = Path(__file__).parent.parent / "knots" / "data" / "knots.json"
OUTPUT_PATH = Path(__file__).parent / "jones_zero_density_results.json"
TOLERANCE = 0.01       # |root| within 0.01 of 1.0
TIGHT_TOL = 0.001      # tighter tolerance for comparison with Alexander result


def build_polynomial(jones_data):
    """
    Build polynomial coefficient array from Jones data.

    jones_data has min_power, max_power, coefficients.
    E.g. min_power=-3, coefficients=[1,-3,7,...] means
    1*t^(-3) + (-3)*t^(-2) + 7*t^(-1) + ...

    Multiply through by t^(-min_power) to get a standard polynomial.
    Then find roots of that polynomial.

    Note: multiplying by t^k just adds k roots at z=0, which we ignore.
    """
    min_pow = jones_data["min_power"]
    coeffs = jones_data["coefficients"]
    # The polynomial in t is: sum_i coeffs[i] * t^(min_pow + i)
    # Multiply by t^(-min_pow) to clear negative powers:
    # becomes sum_i coeffs[i] * t^i  (if min_pow <= 0)
    # or sum_i coeffs[i] * t^(min_pow + i - min_pow_overall) in general

    # Degree after clearing: max_pow - min_pow = len(coeffs) - 1
    # The polynomial p(t) = coeffs[0] + coeffs[1]*t + ... + coeffs[n]*t^n
    # numpy.roots expects highest degree first

    if len(coeffs) < 2:
        return None  # constant or empty, no roots

    # Reverse for numpy (highest degree first)
    poly_coeffs = list(reversed(coeffs))
    return poly_coeffs


def analyze():
    print("Loading knots data...")
    with open(KNOTS_PATH) as f:
        data = json.load(f)

    knots = data["knots"]

    # Filter to knots with Jones polynomial data
    jones_knots = [k for k in knots if k.get("jones") and k["jones"].get("coefficients")]
    print(f"Total knots: {len(knots)}, with Jones polynomial: {len(jones_knots)}")

    # Collect all roots
    all_radii = []
    all_roots = []
    knot_stats = []
    by_crossing = defaultdict(lambda: {"unit_circle_roots": 0, "total_roots": 0, "n_knots": 0})
    by_crossing_tight = defaultdict(lambda: {"unit_circle_roots": 0, "total_roots": 0, "n_knots": 0})

    n_analyzed = 0
    total_roots = 0
    unit_circle_count = 0
    unit_circle_count_tight = 0

    # Radial histogram bins
    radial_bins = np.linspace(0, 3, 301)
    radial_hist = np.zeros(len(radial_bins) - 1)

    for knot in jones_knots:
        jones = knot["jones"]
        poly_coeffs = build_polynomial(jones)
        if poly_coeffs is None:
            continue

        try:
            roots = np.roots(poly_coeffs)
        except Exception:
            continue

        # Filter out near-zero roots (artifacts of clearing negative powers)
        roots = roots[np.abs(roots) > 1e-8]

        if len(roots) == 0:
            continue

        radii = np.abs(roots)
        n_analyzed += 1
        total_roots += len(radii)

        on_circle = np.sum(np.abs(radii - 1.0) < TOLERANCE)
        on_circle_tight = np.sum(np.abs(radii - 1.0) < TIGHT_TOL)
        unit_circle_count += on_circle
        unit_circle_count_tight += on_circle_tight

        all_radii.extend(radii.tolist())

        # Per-crossing stats
        cn = knot.get("crossing_number", 0)
        # Many knots have crossing_number=0 in the data; use name to infer
        name = knot.get("name", "")
        if cn == 0 and name:
            # Try to extract from name like "11*a_1" -> 11, or "3_1" -> 3
            parts = name.replace("*", "").split("_")
            try:
                cn = int(''.join(c for c in parts[0] if c.isdigit()))
            except (ValueError, IndexError):
                cn = 0

        by_crossing[cn]["unit_circle_roots"] += int(on_circle)
        by_crossing[cn]["total_roots"] += len(radii)
        by_crossing[cn]["n_knots"] += 1

        by_crossing_tight[cn]["unit_circle_roots"] += int(on_circle_tight)
        by_crossing_tight[cn]["total_roots"] += len(radii)
        by_crossing_tight[cn]["n_knots"] += 1

        # Histogram
        h, _ = np.histogram(radii, bins=radial_bins)
        radial_hist += h

        knot_stats.append({
            "name": name,
            "crossing_number": cn,
            "n_roots": len(radii),
            "on_unit_circle": int(on_circle),
            "fraction_on_circle": float(on_circle / len(radii)),
            "mean_radius": float(np.mean(radii)),
            "median_radius": float(np.median(radii)),
            "min_radius": float(np.min(radii)),
            "max_radius": float(np.max(radii)),
        })

    # Summary
    all_radii = np.array(all_radii)
    fraction_on_circle = unit_circle_count / total_roots if total_roots > 0 else 0
    fraction_on_circle_tight = unit_circle_count_tight / total_roots if total_roots > 0 else 0

    print(f"\n=== Jones Polynomial Zero Density ===")
    print(f"Knots analyzed: {n_analyzed}")
    print(f"Total roots: {total_roots}")
    print(f"Roots on unit circle (tol={TOLERANCE}): {unit_circle_count} ({100*fraction_on_circle:.2f}%)")
    print(f"Roots on unit circle (tol={TIGHT_TOL}): {unit_circle_count_tight} ({100*fraction_on_circle_tight:.2f}%)")
    print(f"Mean |root|: {np.mean(all_radii):.4f}")
    print(f"Median |root|: {np.median(all_radii):.4f}")
    print(f"Std |root|: {np.std(all_radii):.4f}")

    # Radial distribution percentiles
    percentiles = [5, 10, 25, 50, 75, 90, 95]
    pct_values = np.percentile(all_radii, percentiles)
    print(f"\nRadial distribution percentiles:")
    for p, v in zip(percentiles, pct_values):
        print(f"  {p}th: {v:.4f}")

    # By crossing number
    print(f"\nBy crossing number (tol={TOLERANCE}):")
    for cn in sorted(by_crossing.keys()):
        s = by_crossing[cn]
        pct = 100 * s["unit_circle_roots"] / s["total_roots"] if s["total_roots"] > 0 else 0
        print(f"  {cn}: {s['unit_circle_roots']}/{s['total_roots']} = {pct:.1f}% ({s['n_knots']} knots)")

    # Comparison with Alexander
    print(f"\n=== Comparison with Alexander Polynomial (NF16) ===")
    print(f"Alexander unit-circle density (tol=0.001): 41.19%")
    print(f"Jones unit-circle density (tol={TOLERANCE}): {100*fraction_on_circle:.2f}%")
    print(f"Jones unit-circle density (tol={TIGHT_TOL}): {100*fraction_on_circle_tight:.2f}%")
    print(f"Expected: ~61.8%")

    delta = fraction_on_circle - 0.4119
    if delta > 0:
        print(f"Jones roots are MORE concentrated on unit circle than Alexander roots (+{100*delta:.2f}pp)")
    else:
        print(f"Jones roots are LESS concentrated on unit circle than Alexander roots ({100*delta:.2f}pp)")

    # Build results
    # Coarsen radial histogram for JSON
    coarse_bins = np.linspace(0, 3, 61)
    coarse_hist, _ = np.histogram(all_radii, bins=coarse_bins)

    results = {
        "problem": "List2 #14: Jones Polynomial Zero Density",
        "description": "Radial density of complex roots of Jones polynomials at the unit circle |z|=1",
        "n_knots_analyzed": n_analyzed,
        "total_roots": int(total_roots),
        "tolerances": {
            "standard": TOLERANCE,
            "tight": TIGHT_TOL,
        },
        "overall": {
            "unit_circle_roots_tol_0.01": int(unit_circle_count),
            "unit_circle_roots_tol_0.001": int(unit_circle_count_tight),
            "total_roots": int(total_roots),
            "percentage_tol_0.01": round(100 * fraction_on_circle, 4),
            "percentage_tol_0.001": round(100 * fraction_on_circle_tight, 4),
        },
        "radial_statistics": {
            "mean": round(float(np.mean(all_radii)), 6),
            "median": round(float(np.median(all_radii)), 6),
            "std": round(float(np.std(all_radii)), 6),
            "min": round(float(np.min(all_radii)), 6),
            "max": round(float(np.max(all_radii)), 6),
            "percentiles": {str(p): round(float(v), 6) for p, v in zip(percentiles, pct_values)},
        },
        "by_crossing_number_tol_0.01": {
            str(cn): {
                "unit_circle_roots": s["unit_circle_roots"],
                "total_roots": s["total_roots"],
                "percentage": round(100 * s["unit_circle_roots"] / s["total_roots"], 4) if s["total_roots"] > 0 else 0,
                "n_knots": s["n_knots"],
            }
            for cn, s in sorted(by_crossing.items())
        },
        "by_crossing_number_tol_0.001": {
            str(cn): {
                "unit_circle_roots": s["unit_circle_roots"],
                "total_roots": s["total_roots"],
                "percentage": round(100 * s["unit_circle_roots"] / s["total_roots"], 4) if s["total_roots"] > 0 else 0,
                "n_knots": s["n_knots"],
            }
            for cn, s in sorted(by_crossing_tight.items())
        },
        "radial_histogram": {
            "bin_edges": [round(float(b), 4) for b in coarse_bins.tolist()],
            "counts": coarse_hist.tolist(),
        },
        "comparison_with_alexander": {
            "alexander_unit_circle_pct_tol_0.001": 41.19,
            "jones_unit_circle_pct_tol_0.01": round(100 * fraction_on_circle, 4),
            "jones_unit_circle_pct_tol_0.001": round(100 * fraction_on_circle_tight, 4),
            "jones_more_concentrated": bool(fraction_on_circle > 0.4119),
            "expected_density": 0.618,
            "observed_density_tol_0.01": round(fraction_on_circle, 6),
            "observed_density_tol_0.001": round(fraction_on_circle_tight, 6),
        },
        "interpretation": "",  # filled below
    }

    # Interpretation
    if abs(fraction_on_circle - 0.618) < 0.05:
        results["interpretation"] = (
            f"Jones unit-circle density ({100*fraction_on_circle:.1f}%) is near the expected ~61.8%, "
            f"consistent with golden-ratio concentration. "
            f"Significantly higher than Alexander's 41.2%."
        )
    elif fraction_on_circle > 0.4119:
        results["interpretation"] = (
            f"Jones unit-circle density ({100*fraction_on_circle:.1f}%) exceeds Alexander's 41.2% "
            f"but {'falls short of' if fraction_on_circle < 0.618 else 'exceeds'} the expected ~61.8%. "
            f"Jones roots are more concentrated on the unit circle than Alexander roots."
        )
    else:
        results["interpretation"] = (
            f"Jones unit-circle density ({100*fraction_on_circle:.1f}%) is below Alexander's 41.2%. "
            f"Jones roots are less concentrated on the unit circle than Alexander roots, "
            f"contradicting the ~61.8% expectation."
        )

    # Save
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUTPUT_PATH}")

    return results


if __name__ == "__main__":
    analyze()
