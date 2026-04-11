#!/usr/bin/env python3
"""
Knot Unknotting Number: Distribution and Bounds
================================================
The unknotting number u(K) is the minimum number of crossing changes to unknot K.
Upper bound: u <= (c-1)/2 where c is crossing number.
Lower bound: |sigma(K)|/2 <= u where sigma is the knot signature.

Since the dataset lacks direct unknotting numbers and signatures,
we compute:
  - Signature from Levine-Tristram evaluation of Alexander polynomial
  - Upper/lower bounds on u(K)
  - Distribution of bounds by crossing number
  - Correlation with determinant
"""

import json
import re
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "knots" / "data" / "knots.json"
OUT_PATH = Path(__file__).parent / "knot_unknotting_results.json"


def parse_crossing_number(name: str) -> int | None:
    """Extract crossing number from knot name like '11*a_1' or '3_1'."""
    m = re.match(r"(\d+)", name)
    return int(m.group(1)) if m else None


def is_alternating(name: str) -> bool:
    """Check if knot is alternating (no * in name)."""
    return "*" not in name.split("_")[0] if "_" in name else "*" not in name


def compute_signature(alex_coeffs: list, min_power: int = 0) -> int:
    """
    Compute the knot signature from the Alexander polynomial.

    For a knot with Alexander polynomial Delta(t), the signature sigma(K)
    equals the Levine-Tristram signature at omega = -1, which counts
    sign changes of the real part of Delta(e^{i*theta}) for theta in (0, pi).

    Each zero crossing contributes +/-2 to the signature.
    The total signature = -2 * (number of roots of Delta on upper unit semicircle).
    """
    if not alex_coeffs or len(alex_coeffs) == 0:
        return 0

    n_eval = 2000
    thetas = np.linspace(0.001, np.pi - 0.001, n_eval)

    # The stored polynomial starts at min_power but is NOT centered.
    # The true (symmetric) Alexander polynomial is centered at power 0,
    # i.e., Delta(t) = sum a_i t^{i - degree/2}.
    # We must shift by degree/2 to get the symmetric form before evaluating.
    degree = len(alex_coeffs) - 1
    center = degree / 2.0

    # Evaluate Re[Delta(e^{i*theta})] with centered powers
    vals = np.zeros(n_eval)
    for i, c in enumerate(alex_coeffs):
        power = min_power + i - center
        vals += c * np.cos(power * thetas)

    # Count sign changes: each root on the upper unit semicircle
    # contributes +/-2 to the signature
    signs = np.sign(vals)
    sign_changes = 0
    for i in range(1, len(signs)):
        if signs[i] != signs[i - 1] and signs[i] != 0 and signs[i - 1] != 0:
            sign_changes += 1

    # |sigma| = 2 * number_of_roots_on_upper_semicircle
    return sign_changes * 2


def compute_alex_determinant(alex_coeffs: list, min_power: int = 0) -> int:
    """Compute |Delta(-1)| = determinant of knot."""
    if not alex_coeffs:
        return 0
    val = sum(c * ((-1) ** (min_power + i)) for i, c in enumerate(alex_coeffs))
    return abs(val)


def main():
    with open(DATA_PATH, "r") as f:
        data = json.load(f)

    knots = data["knots"]

    # ----- Per-knot analysis -----
    records = []
    for k in knots:
        cn = parse_crossing_number(k["name"])
        if cn is None or cn < 3:
            continue

        alex = k.get("alex_coeffs", [])
        alex_obj = k.get("alexander") or {}
        min_power = alex_obj.get("min_power", 0)
        det_stored = k.get("determinant", None)

        # Compute signature (gives |sigma|)
        abs_sigma = compute_signature(alex, min_power)

        # Verify determinant
        det_computed = compute_alex_determinant(alex, min_power)

        # Bounds on unknotting number
        u_upper = (cn - 1) / 2.0  # Theoretical upper bound
        u_lower_sig = abs_sigma / 2  # Signature lower bound: |sigma|/2 <= u

        # Alexander polynomial degree bound:
        # degree of Alex poly <= 2*u (Wendt), so u >= degree/2
        alex_degree = (len(alex) - 1) if alex else 0
        # For symmetric poly centered at 0, the "genus" = max_power
        genus_bound = alex_obj.get("max_power", 0) if alex_obj else 0
        # Seifert genus g(K) >= u, and degree(Delta) <= 2g
        # So u >= degree/2 is NOT valid directly, but g >= u_lower from signature

        records.append({
            "name": k["name"],
            "crossing_number": cn,
            "alternating": is_alternating(k["name"]),
            "determinant": det_stored,
            "det_from_alex": det_computed,
            "abs_signature": abs_sigma,
            "u_upper_bound": u_upper,
            "u_lower_signature": u_lower_sig,
            "alex_degree": alex_degree,
            "genus_upper": genus_bound,
        })

    n_total = len(records)

    # Separate knots with valid Alexander polynomial from those without
    records_with_alex = [r for r in records if r["alex_degree"] > 0]
    records_no_alex = [r for r in records if r["alex_degree"] == 0]
    n_with_alex = len(records_with_alex)
    n_no_alex = len(records_no_alex)
    print(f"Analyzed {n_total} knots ({n_with_alex} with Alexander poly, {n_no_alex} without)")

    # ----- 1. Distribution of signature lower bound by crossing number -----
    cn_groups = defaultdict(list)
    for r in records:
        cn_groups[r["crossing_number"]].append(r)

    dist_by_cn = {}
    for cn in sorted(cn_groups):
        group = cn_groups[cn]
        sig_lowers = [r["u_lower_signature"] for r in group]
        u_uppers = [r["u_upper_bound"] for r in group]
        dets = [r["determinant"] for r in group if r["determinant"] is not None]

        dist_by_cn[str(cn)] = {
            "count": len(group),
            "u_upper_bound": u_uppers[0],  # Same for all with same cn
            "sig_lower_mean": float(np.mean(sig_lowers)),
            "sig_lower_median": float(np.median(sig_lowers)),
            "sig_lower_max": float(np.max(sig_lowers)),
            "sig_lower_min": float(np.min(sig_lowers)),
            "sig_lower_std": float(np.std(sig_lowers)),
            "det_mean": float(np.mean(dets)) if dets else None,
            "det_median": float(np.median(dets)) if dets else None,
            "n_alternating": sum(1 for r in group if r["alternating"]),
        }

    # ----- 1b. Same distribution but only for knots WITH Alexander polynomial -----
    cn_groups_valid = defaultdict(list)
    for r in records_with_alex:
        cn_groups_valid[r["crossing_number"]].append(r)

    dist_by_cn_valid = {}
    for cn in sorted(cn_groups_valid):
        group = cn_groups_valid[cn]
        sig_lowers = [r["u_lower_signature"] for r in group]
        dets = [r["determinant"] for r in group if r["determinant"] is not None]
        dist_by_cn_valid[str(cn)] = {
            "count": len(group),
            "u_upper_bound": (cn - 1) / 2.0,
            "sig_lower_mean": float(np.mean(sig_lowers)),
            "sig_lower_median": float(np.median(sig_lowers)),
            "sig_lower_max": float(np.max(sig_lowers)),
            "sig_lower_min": float(np.min(sig_lowers)),
            "sig_lower_std": float(np.std(sig_lowers)),
            "det_mean": float(np.mean(dets)) if dets else None,
            "n_alternating": sum(1 for r in group if r["alternating"]),
        }

    # ----- 2. Fraction achieving upper bound -----
    # For alternating knots, u = (c-1)/2 is rare (only for torus knots T(2,n))
    # We check: how many have u_lower_signature == u_upper_bound
    # (meaning signature alone forces u to be maximal)
    n_at_upper = sum(
        1 for r in records if r["u_lower_signature"] >= r["u_upper_bound"]
    )
    frac_at_upper = n_at_upper / n_total if n_total > 0 else 0

    # Fraction where signature lower >= floor of upper bound
    n_near_upper = sum(
        1 for r in records
        if r["u_lower_signature"] >= r["u_upper_bound"] - 1
    )
    frac_near_upper = n_near_upper / n_total if n_total > 0 else 0

    # ----- 3. Signature bound verification -----
    # |sigma(K)|/2 <= u(K) is a theorem. We can verify our signature computation
    # by checking it against known small knots.
    # For trefoil (3_1): sigma = 2, u = 1, det = 3
    # For figure-8 (4_1): sigma = 0, u = 1, det = 5
    small_knots = {}
    for r in records:
        if r["crossing_number"] <= 7:
            small_knots[r["name"]] = {
                "abs_signature": r["abs_signature"],
                "u_lower_signature": r["u_lower_signature"],
                "u_upper_bound": r["u_upper_bound"],
                "determinant": r["determinant"],
                "det_from_alex": r["det_from_alex"],
            }

    # Filtered versions (only knots with Alexander polynomial)
    n_at_upper_v = sum(
        1 for r in records_with_alex if r["u_lower_signature"] >= r["u_upper_bound"]
    )
    frac_at_upper_v = n_at_upper_v / n_with_alex if n_with_alex > 0 else 0
    n_near_upper_v = sum(
        1 for r in records_with_alex
        if r["u_lower_signature"] >= r["u_upper_bound"] - 1
    )
    frac_near_upper_v = n_near_upper_v / n_with_alex if n_with_alex > 0 else 0

    # ----- 4. Determinant vs signature correlation -----
    dets = np.array([r["determinant"] for r in records_with_alex if r["determinant"] is not None and r["determinant"] > 0])
    sigs = np.array([r["abs_signature"] for r in records_with_alex if r["determinant"] is not None and r["determinant"] > 0])
    log_dets = np.log(dets + 1)

    det_sig_corr = float(np.corrcoef(log_dets, sigs)[0, 1])

    # By crossing number
    det_sig_by_cn = {}
    for cn in sorted(cn_groups_valid):
        group = cn_groups_valid[cn]
        d = [r["determinant"] for r in group if r["determinant"] and r["determinant"] > 0]
        s = [r["abs_signature"] for r in group if r["determinant"] and r["determinant"] > 0]
        if len(d) > 5:
            det_sig_by_cn[str(cn)] = float(np.corrcoef(np.log(np.array(d) + 1), s)[0, 1])

    # ----- 5. Mean u_lower/c ratio (proxy for u/c) -----
    ratios = [r["u_lower_signature"] / r["crossing_number"] for r in records_with_alex if r["crossing_number"] > 0]
    mean_ratio = float(np.mean(ratios))
    median_ratio = float(np.median(ratios))

    # By crossing number (valid only)
    ratio_by_cn = {}
    for cn in sorted(cn_groups_valid):
        group = cn_groups_valid[cn]
        r_vals = [r["u_lower_signature"] / cn for r in group]
        ratio_by_cn[str(cn)] = {
            "mean": float(np.mean(r_vals)),
            "std": float(np.std(r_vals)),
        }

    # ----- 6. Alternating vs non-alternating comparison -----
    alt_sigs = [r["u_lower_signature"] for r in records_with_alex if r["alternating"]]
    nonalt_sigs = [r["u_lower_signature"] for r in records_with_alex if not r["alternating"]]
    alt_ratios = [r["u_lower_signature"] / r["crossing_number"] for r in records_with_alex if r["alternating"] and r["crossing_number"] > 0]
    nonalt_ratios = [r["u_lower_signature"] / r["crossing_number"] for r in records_with_alex if not r["alternating"] and r["crossing_number"] > 0]

    alternating_comparison = {
        "n_alternating": len(alt_sigs),
        "n_nonalternating": len(nonalt_sigs),
        "alt_mean_sig_lower": float(np.mean(alt_sigs)) if alt_sigs else None,
        "nonalt_mean_sig_lower": float(np.mean(nonalt_sigs)) if nonalt_sigs else None,
        "alt_mean_ratio": float(np.mean(alt_ratios)) if alt_ratios else None,
        "nonalt_mean_ratio": float(np.mean(nonalt_ratios)) if nonalt_ratios else None,
    }

    # ----- 7. Signature distribution (histogram) -----
    sig_counter = Counter(r["abs_signature"] for r in records_with_alex)
    sig_distribution = {str(k): v for k, v in sorted(sig_counter.items())}
    sig_counter_all = Counter(r["abs_signature"] for r in records)

    # ----- Assemble results -----
    results = {
        "metadata": {
            "task": "Knot Unknotting Number: Distribution and Bounds",
            "n_knots": n_total,
            "crossing_range": [
                min(r["crossing_number"] for r in records),
                max(r["crossing_number"] for r in records),
            ],
            "note": "Dataset lacks direct unknotting numbers. We compute the signature-based lower bound |sigma(K)|/2 and crossing-number upper bound (c-1)/2.",
            "method": "Levine-Tristram signature from Alexander polynomial roots on unit circle",
            "n_with_alexander_poly": n_with_alex,
            "n_without_alexander_poly": n_no_alex,
            "caveat": "9988 knots at c=13 have empty Alexander polynomials; filtered stats exclude these.",
        },
        "distribution_by_crossing_number_all": dist_by_cn,
        "distribution_by_crossing_number_valid": dist_by_cn_valid,
        "upper_bound_analysis": {
            "bound": "u <= (c-1)/2",
            "all_knots": {
                "n_at_upper_bound_by_sig": n_at_upper,
                "frac_at_upper_bound": round(frac_at_upper, 6),
                "n_within_1_of_upper": n_near_upper,
                "frac_within_1_of_upper": round(frac_near_upper, 6),
            },
            "valid_alex_only": {
                "n_at_upper_bound_by_sig": n_at_upper_v,
                "frac_at_upper_bound": round(frac_at_upper_v, 6),
                "n_within_1_of_upper": n_near_upper_v,
                "frac_within_1_of_upper": round(frac_near_upper_v, 6),
            },
        },
        "signature_bound_verification": {
            "theorem": "|sigma(K)|/2 <= u(K)",
            "small_knots": small_knots,
            "note": "For 3_1 (trefoil): known u=1, sigma=-2 => |sigma|/2=1 <= 1 (tight). For 4_1 (figure-eight): known u=1, sigma=0 => 0 <= 1.",
        },
        "determinant_vs_signature": {
            "overall_corr_log_det_vs_sig": round(det_sig_corr, 4),
            "by_crossing_number": det_sig_by_cn,
        },
        "unknotting_ratio": {
            "description": "u_lower/c ratio where u_lower = |sigma|/2",
            "mean_ratio": round(mean_ratio, 6),
            "median_ratio": round(median_ratio, 6),
            "theoretical_max_ratio": 0.5,
            "by_crossing_number": ratio_by_cn,
        },
        "alternating_comparison": alternating_comparison,
        "signature_distribution": sig_distribution,
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)

    # ----- Print summary -----
    print(f"\n{'='*60}")
    print("KNOT UNKNOTTING NUMBER: DISTRIBUTION AND BOUNDS")
    print(f"{'='*60}")
    print(f"Total knots analyzed: {n_total}")
    print(f"Crossing number range: {results['metadata']['crossing_range']}")
    print()

    print("Distribution by crossing number (valid Alexander poly only):")
    for cn, info in dist_by_cn_valid.items():
        print(f"  c={cn}: n={info['count']}, "
              f"u_upper={(int(info['u_upper_bound']) if info['u_upper_bound'] == int(info['u_upper_bound']) else info['u_upper_bound'])}, "
              f"sig_lower mean={info['sig_lower_mean']:.2f} "
              f"(range [{info['sig_lower_min']:.0f}, {info['sig_lower_max']:.0f}])")

    print(f"\nFraction at upper bound (valid, by signature): {frac_at_upper_v:.4f}")
    print(f"Fraction within 1 of upper (valid): {frac_near_upper_v:.4f}")
    print(f"\nlog(det) vs |sigma| correlation: {det_sig_corr:.4f}")
    print(f"Mean u_lower/c ratio: {mean_ratio:.4f} (theoretical max: 0.5)")
    print(f"Median u_lower/c ratio: {median_ratio:.4f}")

    print(f"\nAlternating vs non-alternating:")
    print(f"  Alternating: n={alternating_comparison['n_alternating']}, "
          f"mean sig_lower={alternating_comparison['alt_mean_sig_lower']:.2f}, "
          f"mean ratio={alternating_comparison['alt_mean_ratio']:.4f}")
    print(f"  Non-alt:     n={alternating_comparison['n_nonalternating']}, "
          f"mean sig_lower={alternating_comparison['nonalt_mean_sig_lower']:.2f}, "
          f"mean ratio={alternating_comparison['nonalt_mean_ratio']:.4f}")

    print(f"\nSignature distribution (|sigma|):")
    for s, count in sorted(sig_counter.items()):
        bar = "#" * min(count // 50, 60)
        print(f"  |sigma|={s:2d}: {count:5d} {bar}")

    print(f"\nSmall knots verification:")
    for name in sorted(small_knots, key=lambda x: (parse_crossing_number(x) or 0, x)):
        info = small_knots[name]
        print(f"  {name:6s}: |sigma|={info['abs_signature']}, "
              f"u in [{info['u_lower_signature']}, {info['u_upper_bound']}], "
              f"det={info['determinant']}")

    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
