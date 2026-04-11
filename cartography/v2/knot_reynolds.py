"""
DS6: Knot Polynomial Reynolds Number

Compute Re_knot = log(max|coeff|) * crossing_number / log(determinant + 1)
for ~13K knots. Test for phase transition by crossing number and compare
to mathematical Reynolds habitable zone [4.37, 13.68].
"""

import json
import re
import math
import numpy as np
from pathlib import Path
from collections import defaultdict

DATA_PATH = Path(__file__).parent.parent / "knots" / "data" / "knots.json"
OUT_PATH = Path(__file__).parent / "knot_reynolds_results.json"


def extract_crossing_number(name: str) -> int:
    """Extract crossing number from knot name like '11*a_1' -> 11."""
    m = re.match(r"(\d+)", name)
    if m:
        return int(m.group(1))
    return 0


def compute_re(knot: dict) -> dict | None:
    """Compute Reynolds number for a single knot."""
    cn = extract_crossing_number(knot["name"])
    if cn < 3:
        return None

    jones_coeffs = knot.get("jones_coeffs", [])
    if not jones_coeffs:
        return None

    det = knot.get("determinant", 0)
    if det is None or det <= 0:
        return None

    max_abs_coeff = max(abs(c) for c in jones_coeffs)
    coeff_var = float(np.var(jones_coeffs))

    # Re_knot = log(max|coeff|) * crossing_number / log(determinant + 1)
    log_max = math.log(max_abs_coeff + 1)  # +1 to avoid log(0) for trivial
    log_det = math.log(det + 1)

    if log_det == 0:
        return None

    re_knot = log_max * cn / log_det

    return {
        "name": knot["name"],
        "crossing_number": cn,
        "determinant": det,
        "max_abs_coeff": max_abs_coeff,
        "coeff_variance": round(coeff_var, 4),
        "n_jones_terms": len(jones_coeffs),
        "re_knot": round(re_knot, 6),
    }


def detect_phase_transition(binned: dict) -> dict:
    """Look for phase transitions in Re by crossing number."""
    cns = sorted(binned.keys())
    means = [binned[cn]["mean_re"] for cn in cns]
    stds = [binned[cn]["std_re"] for cn in cns]

    # Compute first and second derivatives of mean Re
    diffs = [means[i + 1] - means[i] for i in range(len(means) - 1)]
    second_diffs = [diffs[i + 1] - diffs[i] for i in range(len(diffs) - 1)]

    # Phase transition = largest absolute second derivative
    if second_diffs:
        max_idx = max(range(len(second_diffs)), key=lambda i: abs(second_diffs[i]))
        critical_cn = cns[max_idx + 1]  # offset by 1 due to double differencing
    else:
        critical_cn = None

    # Also check coefficient of variation by bin for regime change
    cvs = [binned[cn]["std_re"] / binned[cn]["mean_re"] if binned[cn]["mean_re"] > 0 else 0
           for cn in cns]

    return {
        "crossing_numbers": cns,
        "mean_re_by_cn": means,
        "std_re_by_cn": stds,
        "first_derivative": [round(d, 4) for d in diffs],
        "second_derivative": [round(d, 4) for d in second_diffs],
        "cv_by_cn": [round(c, 4) for c in cvs],
        "critical_cn": critical_cn,
        "critical_second_deriv": round(second_diffs[max_idx], 4) if second_diffs else None,
    }


def main():
    with open(DATA_PATH, "r") as f:
        data = json.load(f)

    knots = data["knots"]
    print(f"Loaded {len(knots)} knots")

    # Compute Re for all knots
    results = []
    for k in knots:
        r = compute_re(k)
        if r is not None:
            results.append(r)

    print(f"Computed Re for {len(results)} knots")

    re_values = [r["re_knot"] for r in results]
    print(f"Re range: [{min(re_values):.4f}, {max(re_values):.4f}]")
    print(f"Re mean: {np.mean(re_values):.4f}, median: {np.median(re_values):.4f}")

    # Bin by crossing number
    bins = defaultdict(list)
    for r in results:
        bins[r["crossing_number"]].append(r["re_knot"])

    binned = {}
    for cn in sorted(bins.keys()):
        vals = bins[cn]
        binned[cn] = {
            "n_knots": len(vals),
            "mean_re": round(float(np.mean(vals)), 6),
            "median_re": round(float(np.median(vals)), 6),
            "std_re": round(float(np.std(vals)), 6),
            "min_re": round(min(vals), 6),
            "max_re": round(max(vals), 6),
        }

    print("\n=== Mean Re by Crossing Number ===")
    for cn in sorted(binned.keys()):
        b = binned[cn]
        print(f"  cn={cn:2d}: n={b['n_knots']:5d}  mean_Re={b['mean_re']:.4f}  "
              f"std={b['std_re']:.4f}  range=[{b['min_re']:.4f}, {b['max_re']:.4f}]")

    # Detect phase transition
    transition = detect_phase_transition(binned)
    print(f"\n=== Phase Transition Analysis ===")
    print(f"Critical crossing number: {transition['critical_cn']}")
    print(f"Second derivative at critical: {transition['critical_second_deriv']}")
    print(f"First derivatives: {transition['first_derivative']}")
    print(f"Second derivatives: {transition['second_derivative']}")

    # Habitable zone comparison [4.37, 13.68]
    hab_lo, hab_hi = 4.37, 13.68
    in_zone = [r for r in results if hab_lo <= r["re_knot"] <= hab_hi]
    below = [r for r in results if r["re_knot"] < hab_lo]
    above = [r for r in results if r["re_knot"] > hab_hi]

    zone_stats = {
        "habitable_zone": [hab_lo, hab_hi],
        "n_in_zone": len(in_zone),
        "n_below": len(below),
        "n_above": len(above),
        "frac_in_zone": round(len(in_zone) / len(results), 4),
        "frac_below": round(len(below) / len(results), 4),
        "frac_above": round(len(above) / len(results), 4),
    }

    # Per-cn zone membership
    zone_by_cn = {}
    for cn in sorted(bins.keys()):
        vals = bins[cn]
        n_in = sum(1 for v in vals if hab_lo <= v <= hab_hi)
        zone_by_cn[cn] = round(n_in / len(vals), 4) if vals else 0.0

    print(f"\n=== Habitable Zone [4.37, 13.68] ===")
    print(f"In zone: {zone_stats['n_in_zone']} ({zone_stats['frac_in_zone']*100:.1f}%)")
    print(f"Below:   {zone_stats['n_below']} ({zone_stats['frac_below']*100:.1f}%)")
    print(f"Above:   {zone_stats['n_above']} ({zone_stats['frac_above']*100:.1f}%)")
    print(f"\nFraction in zone by cn:")
    for cn, frac in zone_by_cn.items():
        print(f"  cn={cn:2d}: {frac*100:.1f}%")

    # Assemble output
    output = {
        "challenge": "DS6",
        "title": "Knot Polynomial Reynolds Number",
        "formula": "Re_knot = log(max|coeff| + 1) * crossing_number / log(determinant + 1)",
        "n_knots_total": len(knots),
        "n_knots_computed": len(results),
        "global_stats": {
            "mean_re": round(float(np.mean(re_values)), 6),
            "median_re": round(float(np.median(re_values)), 6),
            "std_re": round(float(np.std(re_values)), 6),
            "min_re": round(min(re_values), 6),
            "max_re": round(max(re_values), 6),
        },
        "binned_by_crossing_number": {str(k): v for k, v in binned.items()},
        "phase_transition": {
            "critical_crossing_number": transition["critical_cn"],
            "second_derivative_at_critical": transition["critical_second_deriv"],
            "first_derivatives": transition["first_derivative"],
            "second_derivatives": transition["second_derivative"],
            "cv_by_cn": {str(cn): cv for cn, cv in
                         zip(transition["crossing_numbers"], transition["cv_by_cn"])},
        },
        "habitable_zone_comparison": zone_stats,
        "zone_fraction_by_cn": {str(k): v for k, v in zone_by_cn.items()},
    }

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
