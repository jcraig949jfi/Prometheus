"""
NF16: Alexander-Salem Correlation
Compute roots of Alexander polynomials for all knots, measure unit-circle proximity.
Connections to Salem numbers and cyclotomic theory.
"""

import json
import re
import numpy as np
from collections import defaultdict
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "knots" / "data" / "knots.json"
OUT_PATH = Path(__file__).resolve().parent / "alexander_salem_results.json"

# Known torus knots in standard knot tables
TORUS_KNOTS = {
    "3_1",   # T(2,3) trefoil
    "5_1",   # T(2,5)
    "7_1",   # T(2,7)
    "9_1",   # T(2,9)
    "8_19",  # T(3,4)
    "10_124",# T(3,5)
}

UNIT_CIRCLE_TOL = 0.001


def parse_crossing_number(name: str) -> int:
    """Extract crossing number from knot name like '11*a_1' or '7_3'."""
    m = re.match(r"(\d+)", name)
    return int(m.group(1)) if m else -1


def classify_knot(name: str) -> str:
    """Classify as alternating, non-alternating, or unknown."""
    if "*n_" in name or "n_" in name and "*" in name:
        return "non-alternating"
    if "*a_" in name:
        return "alternating"
    # Lower crossing knots (e.g. '3_1', '8_19') — need heuristic
    # In standard tables, knots up to 10 crossings without 'a'/'n' prefix
    # are labeled by convention; alternating knots come first in numbering
    # For rigorous classification, we use the name pattern
    cn = parse_crossing_number(name)
    if cn <= 7:
        return "alternating"  # all knots up to 7 crossings are alternating
    # 8+ crossings: some are non-alternating
    # 8_19, 8_20, 8_21 are non-alternating; 10_124+ varies
    # We'll mark these as "low-crossing" to be conservative
    return "low-crossing"


def is_torus(name: str) -> bool:
    return name in TORUS_KNOTS


def build_polynomial_coeffs(alexander: dict) -> np.ndarray:
    """
    Build full polynomial coefficient array from Alexander data.
    The polynomial is sum(coeffs[i] * t^(min_power + i)).
    numpy.roots expects coefficients from highest to lowest power.
    """
    min_power = alexander["min_power"]
    coeffs = alexander["coefficients"]
    n = len(coeffs)
    max_power = min_power + n - 1

    if min_power < 0:
        # Factor out t^min_power: polynomial becomes
        # coeffs[0] + coeffs[1]*t + ... + coeffs[n-1]*t^(n-1)
        # after dividing by t^min_power (roots at 0 are from the factor)
        # The Alexander polynomial is a Laurent polynomial; to find roots
        # we treat t^(-min_power) * Delta(t) as an ordinary polynomial
        # This doesn't add spurious roots since t=0 is never a root of Delta(t)
        pass

    # Regardless, the roots of the Laurent polynomial (excluding t=0)
    # are roots of the ordinary polynomial with these coefficients
    # from power 0 to power (max_power - min_power)
    # numpy.roots expects highest power first
    poly_coeffs = np.array(coeffs[::-1], dtype=float)
    return poly_coeffs


def analyze():
    with open(DATA_PATH) as f:
        data = json.load(f)

    knots = data["knots"]
    has_alex = [k for k in knots if k.get("alexander") and k["alexander"].get("coefficients")]
    print(f"Knots with Alexander polynomial: {len(has_alex)}")

    # Accumulators
    all_roots = []
    all_moduli = []
    unit_circle_count = 0
    total_root_count = 0

    by_crossing = defaultdict(lambda: {"unit": 0, "total": 0, "knots": 0})
    by_type = defaultdict(lambda: {"unit": 0, "total": 0, "knots": 0})
    torus_stats = {"unit": 0, "total": 0, "knots": 0}
    non_torus_stats = {"unit": 0, "total": 0, "knots": 0}

    # Off-unit-circle root collection
    off_unit_roots = []

    knot_details = []

    for knot in has_alex:
        name = knot["name"]
        alex = knot["alexander"]
        coeffs = alex["coefficients"]

        if len(coeffs) < 2:
            # Constant polynomial — no roots
            continue

        poly_coeffs = build_polynomial_coeffs(alex)
        roots = np.roots(poly_coeffs)

        if len(roots) == 0:
            continue

        moduli = np.abs(roots)
        on_unit = np.sum(np.abs(moduli - 1.0) < UNIT_CIRCLE_TOL)
        n_roots = len(roots)

        unit_circle_count += on_unit
        total_root_count += n_roots

        cn = parse_crossing_number(name)
        ktype = classify_knot(name)
        is_tor = is_torus(name)

        by_crossing[cn]["unit"] += on_unit
        by_crossing[cn]["total"] += n_roots
        by_crossing[cn]["knots"] += 1

        by_type[ktype]["unit"] += on_unit
        by_type[ktype]["total"] += n_roots
        by_type[ktype]["knots"] += 1

        if is_tor:
            torus_stats["unit"] += on_unit
            torus_stats["total"] += n_roots
            torus_stats["knots"] += 1
        else:
            non_torus_stats["unit"] += on_unit
            non_torus_stats["total"] += n_roots
            non_torus_stats["knots"] += 1

        # Collect off-unit roots
        off_mask = np.abs(moduli - 1.0) >= UNIT_CIRCLE_TOL
        for r in roots[off_mask]:
            off_unit_roots.append(complex(r))

        all_moduli.extend(moduli.tolist())

        # Per-knot detail (for a sample)
        frac = float(on_unit) / n_roots if n_roots > 0 else 0.0
        knot_details.append({
            "name": name,
            "crossing_number": cn,
            "type": ktype,
            "is_torus": is_tor,
            "n_roots": int(n_roots),
            "n_unit_circle": int(on_unit),
            "unit_fraction": round(frac, 4),
        })

    # Overall
    overall_pct = 100.0 * unit_circle_count / total_root_count if total_root_count > 0 else 0.0
    print(f"\nOverall: {unit_circle_count}/{total_root_count} roots on unit circle = {overall_pct:.2f}%")

    # By crossing number
    print("\nBy crossing number:")
    cn_results = {}
    for cn in sorted(by_crossing.keys()):
        s = by_crossing[cn]
        pct = 100.0 * s["unit"] / s["total"] if s["total"] > 0 else 0.0
        print(f"  {cn}: {s['unit']}/{s['total']} = {pct:.2f}%  ({s['knots']} knots)")
        cn_results[str(cn)] = {
            "unit_circle_roots": int(s["unit"]),
            "total_roots": int(s["total"]),
            "percentage": round(pct, 4),
            "n_knots": int(s["knots"]),
        }

    # By alternating type
    print("\nBy knot type:")
    type_results = {}
    for ktype in sorted(by_type.keys()):
        s = by_type[ktype]
        pct = 100.0 * s["unit"] / s["total"] if s["total"] > 0 else 0.0
        print(f"  {ktype}: {s['unit']}/{s['total']} = {pct:.2f}%  ({s['knots']} knots)")
        type_results[ktype] = {
            "unit_circle_roots": int(s["unit"]),
            "total_roots": int(s["total"]),
            "percentage": round(pct, 4),
            "n_knots": int(s["knots"]),
        }

    # Torus vs non-torus
    print("\nTorus vs non-torus:")
    tor_pct = 100.0 * torus_stats["unit"] / torus_stats["total"] if torus_stats["total"] > 0 else 0.0
    ntor_pct = 100.0 * non_torus_stats["unit"] / non_torus_stats["total"] if non_torus_stats["total"] > 0 else 0.0
    print(f"  Torus:     {torus_stats['unit']}/{torus_stats['total']} = {tor_pct:.2f}%  ({torus_stats['knots']} knots)")
    print(f"  Non-torus: {non_torus_stats['unit']}/{non_torus_stats['total']} = {ntor_pct:.2f}%  ({non_torus_stats['knots']} knots)")

    # Off-unit-circle root distribution
    off_moduli = [abs(r) for r in off_unit_roots]
    off_real = [r.real for r in off_unit_roots]
    off_imag = [r.imag for r in off_unit_roots]

    moduli_arr = np.array(all_moduli)
    off_mod_arr = np.array(off_moduli) if off_moduli else np.array([])

    print(f"\nOff-unit-circle roots: {len(off_unit_roots)}")
    if len(off_mod_arr) > 0:
        print(f"  |z| range: [{off_mod_arr.min():.6f}, {off_mod_arr.max():.6f}]")
        print(f"  |z| mean: {off_mod_arr.mean():.6f}, median: {np.median(off_mod_arr):.6f}")
        # Histogram of moduli
        bins = [0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.999, 1.001, 1.1, 1.3, 1.5, 2.0, 3.0, 5.0, 10.0, 100.0]
        hist, _ = np.histogram(off_mod_arr, bins=bins)
        print("  Modulus distribution (off-unit):")
        for i in range(len(hist)):
            if hist[i] > 0:
                print(f"    [{bins[i]:.3f}, {bins[i+1]:.3f}): {hist[i]}")

        # Check reciprocal pairing (Salem number signature: roots come in (r, 1/r) pairs)
        n_reciprocal_pairs = 0
        used = set()
        sorted_off = sorted(off_unit_roots, key=lambda r: abs(r))
        for i, r in enumerate(sorted_off):
            if i in used:
                continue
            recip = 1.0 / r if abs(r) > 1e-10 else None
            if recip is not None:
                for j, s in enumerate(sorted_off):
                    if j in used or j == i:
                        continue
                    if abs(s - recip) < 0.001:
                        n_reciprocal_pairs += 1
                        used.add(i)
                        used.add(j)
                        break
        print(f"\n  Reciprocal pairs (r, 1/r) within tol=0.001: {n_reciprocal_pairs}")
        print(f"  Paired roots: {2 * n_reciprocal_pairs}/{len(off_unit_roots)}")

    # Salem number candidates: real roots > 1 with reciprocal on unit circle
    # A Salem number is an algebraic integer > 1 whose conjugates all have |z| <= 1,
    # with at least one conjugate on the unit circle
    salem_candidates = []
    for kd in knot_details:
        if kd["unit_fraction"] > 0 and kd["unit_fraction"] < 1.0:
            # Has both unit-circle and off-unit roots — potential Salem polynomial
            salem_candidates.append(kd["name"])

    print(f"\nKnots with mixed unit/off-unit roots (Salem-type): {len(salem_candidates)}/{len(knot_details)}")

    # Modulus histogram for ALL roots
    print("\nAll roots modulus histogram:")
    all_bins = [0, 0.5, 0.9, 0.999, 1.001, 1.1, 1.5, 2.0, 5.0, 100.0]
    hist_all, _ = np.histogram(moduli_arr, bins=all_bins)
    for i in range(len(hist_all)):
        print(f"  [{all_bins[i]:.3f}, {all_bins[i+1]:.3f}): {hist_all[i]}")

    # Build results
    results = {
        "problem": "NF16: Alexander-Salem Correlation",
        "description": "Root distribution of Alexander polynomials relative to the unit circle",
        "n_knots_analyzed": len(knot_details),
        "total_roots": int(total_root_count),
        "unit_circle_tolerance": UNIT_CIRCLE_TOL,
        "overall": {
            "unit_circle_roots": int(unit_circle_count),
            "total_roots": int(total_root_count),
            "percentage": round(overall_pct, 4),
        },
        "by_crossing_number": cn_results,
        "by_knot_type": type_results,
        "alternating_vs_nonalternating": {
            "alternating": type_results.get("alternating", {}),
            "non_alternating": type_results.get("non-alternating", {}),
            "note": "Low-crossing knots (<=10 crossings, no a/n prefix) reported separately",
        },
        "torus_vs_nontorus": {
            "torus": {
                "unit_circle_roots": int(torus_stats["unit"]),
                "total_roots": int(torus_stats["total"]),
                "percentage": round(tor_pct, 4),
                "n_knots": int(torus_stats["knots"]),
            },
            "non_torus": {
                "unit_circle_roots": int(non_torus_stats["unit"]),
                "total_roots": int(non_torus_stats["total"]),
                "percentage": round(ntor_pct, 4),
                "n_knots": int(non_torus_stats["knots"]),
            },
        },
        "off_unit_circle_distribution": {
            "count": len(off_unit_roots),
            "modulus_range": [round(float(off_mod_arr.min()), 6), round(float(off_mod_arr.max()), 6)] if len(off_mod_arr) > 0 else [],
            "modulus_mean": round(float(off_mod_arr.mean()), 6) if len(off_mod_arr) > 0 else None,
            "modulus_median": round(float(np.median(off_mod_arr)), 6) if len(off_mod_arr) > 0 else None,
            "reciprocal_pairs": int(n_reciprocal_pairs) if off_unit_roots else 0,
            "modulus_histogram": {
                f"[{all_bins[i]:.3f},{all_bins[i+1]:.3f})": int(hist_all[i])
                for i in range(len(hist_all))
            },
        },
        "salem_type_knots": {
            "count": len(salem_candidates),
            "fraction": round(len(salem_candidates) / len(knot_details), 4) if knot_details else 0,
            "description": "Knots whose Alexander polynomial has both unit-circle and off-unit roots",
        },
        "findings": [],
    }

    # Generate findings
    findings = []
    findings.append(f"Overall {overall_pct:.1f}% of Alexander polynomial roots lie on the unit circle (tol={UNIT_CIRCLE_TOL})")

    if "alternating" in type_results and "non-alternating" in type_results:
        a_pct = type_results["alternating"]["percentage"]
        n_pct = type_results["non-alternating"]["percentage"]
        diff = abs(a_pct - n_pct)
        if diff > 1.0:
            findings.append(f"Alternating ({a_pct:.1f}%) vs non-alternating ({n_pct:.1f}%): {diff:.1f}pp difference")
        else:
            findings.append(f"Alternating ({a_pct:.1f}%) and non-alternating ({n_pct:.1f}%) have similar unit-circle fractions ({diff:.1f}pp)")

    if torus_stats["total"] > 0:
        findings.append(f"Torus knots: {tor_pct:.1f}% unit-circle vs {ntor_pct:.1f}% for non-torus")

    if salem_candidates:
        findings.append(f"{len(salem_candidates)}/{len(knot_details)} knots ({100*len(salem_candidates)/len(knot_details):.1f}%) have Salem-type Alexander polynomials")

    if off_unit_roots and n_reciprocal_pairs > 0:
        findings.append(f"{2*n_reciprocal_pairs}/{len(off_unit_roots)} off-unit roots form reciprocal (r, 1/r) pairs — consistent with palindromic polynomial structure")

    results["findings"] = findings

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")

    return results


if __name__ == "__main__":
    analyze()
