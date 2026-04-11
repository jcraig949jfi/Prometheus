#!/usr/bin/env python3
"""
Class Number One Distribution and Properties

Analyzes h=1 fraction by degree, signature type, and discriminant range.
Tests Cohen-Lenstra predictions and class number distribution shape.

Data sources:
  - Local: cartography/number_fields/data/number_fields.json (degree <= 6, |disc| <= 10000)
  - LMFDB stats: cartography/lmfdb_dump/nf_fields_counts.json (22M+ fields, aggregated)
  - LMFDB stats: cartography/lmfdb_dump/nf_fields_stats.json

Output: cartography/v2/nf_class_number_stats_results.json
"""

import json
import os
import math
import numpy as np
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LOCAL_NF = ROOT / "cartography" / "number_fields" / "data" / "number_fields.json"
LMFDB_COUNTS = ROOT / "cartography" / "lmfdb_dump" / "nf_fields_counts.json"
LMFDB_STATS = ROOT / "cartography" / "lmfdb_dump" / "nf_fields_stats.json"
OUTPUT = Path(__file__).resolve().parent / "nf_class_number_stats_results.json"


def load_local_nf():
    """Load local number fields JSON."""
    with open(LOCAL_NF) as f:
        data = json.load(f)
    # Parse signature from label: degree.r2.disc_abs.index
    for d in data:
        parts = d["label"].split(".")
        d["r2"] = int(parts[1])
        d["r1"] = d["degree"] - 2 * d["r2"]
        d["disc_abs_int"] = int(d["disc_abs"])
        d["class_number_int"] = int(d["class_number"])
    return data


def load_lmfdb_counts():
    """Load LMFDB aggregated counts."""
    with open(LMFDB_COUNTS) as f:
        return json.load(f)


def load_lmfdb_stats():
    """Load LMFDB stats."""
    with open(LMFDB_STATS) as f:
        return json.load(f)


def signature_type(r1, r2):
    """Classify signature into type."""
    if r2 == 0:
        return "totally_real"
    elif r1 == 0:
        return "totally_complex"
    else:
        return "mixed"


# =====================================================================
# Part 1: LMFDB-scale analysis (22M fields, aggregated counts)
# =====================================================================

def analyze_lmfdb_h1_by_degree(counts_data):
    """h=1 fraction by degree from LMFDB counts (deduplicated)."""
    records = counts_data["records"]

    # h=1 by degree (exact class_number = 1)
    h1_deg = {}
    for r in records:
        if tuple(r["cols"]) == ("class_number", "degree") and r["values"][0] == 1:
            deg = r["values"][1]
            if deg not in h1_deg:
                h1_deg[deg] = r["count"]

    # Total by degree (all fields)
    total_deg = {}
    for r in records:
        if tuple(r["cols"]) == ("degree",):
            v = r["values"][0]
            if isinstance(v, int):
                if v not in total_deg:
                    total_deg[v] = r["count"]

    # h=1 fraction
    result = {}
    for deg in sorted(h1_deg.keys()):
        if deg in total_deg and total_deg[deg] > 0:
            frac = h1_deg[deg] / total_deg[deg]
            result[deg] = {
                "h1_count": h1_deg[deg],
                "total_count": total_deg[deg],
                "h1_fraction": round(frac, 6),
            }
    return result


def analyze_lmfdb_h1_by_degree_r2(counts_data):
    """h=1 fraction by (degree, r2) from LMFDB counts."""
    records = counts_data["records"]

    # h=1 by (degree, r2)
    h1_dr2 = {}
    for r in records:
        if tuple(r["cols"]) == ("class_number", "degree", "r2") and r["values"][0] == 1:
            key = (r["values"][1], r["values"][2])
            if key not in h1_dr2:
                h1_dr2[key] = r["count"]

    # Total by (degree, r2)
    total_dr2 = {}
    for r in records:
        if tuple(r["cols"]) == ("degree", "r2"):
            v0, v1 = r["values"]
            if isinstance(v0, int) and isinstance(v1, int):
                key = (v0, v1)
                if key not in total_dr2:
                    total_dr2[key] = r["count"]

    result = {}
    for (deg, r2) in sorted(h1_dr2.keys()):
        key = f"{deg}_{r2}"
        r1 = deg - 2 * r2
        stype = signature_type(r1, r2)
        total = total_dr2.get((deg, r2), 0)
        if total > 0:
            frac = h1_dr2[(deg, r2)] / total
            result[key] = {
                "degree": deg,
                "r1": r1,
                "r2": r2,
                "signature_type": stype,
                "h1_count": h1_dr2[(deg, r2)],
                "total_count": total,
                "h1_fraction": round(frac, 6),
            }
    return result


def analyze_lmfdb_h1_by_signature_type(dr2_data):
    """Aggregate h=1 fraction by signature type across all degrees."""
    agg = defaultdict(lambda: {"h1": 0, "total": 0})
    for key, val in dr2_data.items():
        stype = val["signature_type"]
        agg[stype]["h1"] += val["h1_count"]
        agg[stype]["total"] += val["total_count"]

    result = {}
    for stype in ["totally_real", "mixed", "totally_complex"]:
        if stype in agg and agg[stype]["total"] > 0:
            result[stype] = {
                "h1_count": agg[stype]["h1"],
                "total_count": agg[stype]["total"],
                "h1_fraction": round(agg[stype]["h1"] / agg[stype]["total"], 6),
            }
    return result


def analyze_lmfdb_class_number_distribution(counts_data):
    """Class number distribution from LMFDB counts."""
    records = counts_data["records"]

    # Exact class numbers by degree
    cn_dist = defaultdict(lambda: defaultdict(int))
    for r in records:
        if tuple(r["cols"]) == ("class_number", "degree"):
            cn = r["values"][0]
            deg = r["values"][1]
            if isinstance(cn, int) and isinstance(deg, int):
                cn_dist[deg][cn] = max(cn_dist[deg][cn], r["count"])

    # Binned class numbers (for large values)
    cn_bins = defaultdict(int)
    total_all = 0
    for r in records:
        if tuple(r["cols"]) == ("class_number",):
            cn = r["values"][0]
            if isinstance(cn, dict):
                # Range bin like {$gt: 1, $lt: 11}
                label = str(cn)
                cn_bins[label] = max(cn_bins[label], r["count"])
            elif isinstance(cn, int):
                cn_bins[f"exact_{cn}"] = max(cn_bins[f"exact_{cn}"], r["count"])

    # For exact values, compute distribution statistics
    all_exact = defaultdict(int)
    for deg, dist in cn_dist.items():
        for cn, count in dist.items():
            all_exact[cn] += count

    return {
        "by_degree": {str(deg): dict(dist) for deg, dist in sorted(cn_dist.items()) if deg <= 10},
        "global_exact": dict(sorted(all_exact.items())),
    }


# =====================================================================
# Part 2: Local analysis (9K fields with individual records)
# =====================================================================

def analyze_local_h1_by_disc_range(data):
    """h=1 fraction by discriminant range within fixed degree."""
    disc_bins = [0, 100, 500, 1000, 2000, 5000, 10000, 50000]

    result = {}
    for deg in [2, 3, 4, 5]:
        subset = [d for d in data if d["degree"] == deg]
        if len(subset) < 10:
            continue

        bins_data = []
        for i in range(len(disc_bins) - 1):
            lo, hi = disc_bins[i], disc_bins[i + 1]
            in_bin = [d for d in subset if lo <= d["disc_abs_int"] < hi]
            if len(in_bin) < 5:
                continue
            h1_count = sum(1 for d in in_bin if d["class_number_int"] == 1)
            mean_cn = np.mean([d["class_number_int"] for d in in_bin])
            bins_data.append({
                "disc_range": f"[{lo},{hi})",
                "count": len(in_bin),
                "h1_count": h1_count,
                "h1_fraction": round(h1_count / len(in_bin), 4),
                "mean_class_number": round(float(mean_cn), 4),
            })

        # Test monotonic decrease of h=1 fraction
        fracs = [b["h1_fraction"] for b in bins_data]
        monotonic_decreasing = all(fracs[i] >= fracs[i + 1] for i in range(len(fracs) - 1))
        # Weaker test: overall trend
        if len(fracs) >= 3:
            from scipy import stats as sp_stats
            slope, _, _, p_value, _ = sp_stats.linregress(range(len(fracs)), fracs)
            trend = {"slope": round(slope, 6), "p_value": round(p_value, 6)}
        else:
            trend = None

        result[str(deg)] = {
            "bins": bins_data,
            "monotonic_decreasing": monotonic_decreasing,
            "trend": trend,
        }

    return result


def analyze_local_h1_by_signature(data):
    """h=1 fraction by signature type within each degree (local data)."""
    result = {}
    for deg in sorted(set(d["degree"] for d in data)):
        subset = [d for d in data if d["degree"] == deg]
        if len(subset) < 5:
            continue
        by_type = defaultdict(list)
        for d in subset:
            stype = signature_type(d["r1"], d["r2"])
            by_type[stype].append(d)

        deg_result = {}
        for stype, fields in by_type.items():
            h1 = sum(1 for f in fields if f["class_number_int"] == 1)
            deg_result[stype] = {
                "count": len(fields),
                "h1_count": h1,
                "h1_fraction": round(h1 / len(fields), 4) if fields else 0,
                "mean_class_number": round(float(np.mean([f["class_number_int"] for f in fields])), 4),
                "median_class_number": float(np.median([f["class_number_int"] for f in fields])),
            }
        result[str(deg)] = deg_result

    return result


def analyze_class_number_distribution_shape(data):
    """Test whether class number distribution is geometric, power law, etc."""
    results = {}
    from scipy import stats as sp_stats

    for deg in [2, 3, 4]:
        subset = [d for d in data if d["degree"] == deg]
        if len(subset) < 50:
            continue

        cn_values = [d["class_number_int"] for d in subset]
        cn_array = np.array(cn_values, dtype=float)

        # Basic stats
        stats = {
            "count": len(cn_values),
            "mean": round(float(np.mean(cn_array)), 4),
            "median": float(np.median(cn_array)),
            "std": round(float(np.std(cn_array)), 4),
            "max": int(np.max(cn_array)),
            "min": int(np.min(cn_array)),
        }

        # Distribution of values
        unique, counts = np.unique(cn_array, return_counts=True)
        freq = dict(zip(unique.astype(int).tolist(), counts.tolist()))

        # Test geometric (exponential) fit: P(h=k) ~ p*(1-p)^(k-1)
        # MLE for geometric: p_hat = 1/mean
        p_hat = 1.0 / np.mean(cn_array)
        # Compute KS test against geometric
        from scipy.stats import kstest
        geo_ks = kstest(cn_array, lambda x: 1 - (1 - p_hat) ** x)

        # Test power law: P(h >= k) ~ k^(-alpha)
        # For cn >= 1, use MLE: alpha = 1 + n / sum(ln(cn/cn_min))
        cn_pos = cn_array[cn_array >= 1]
        if len(cn_pos) > 10:
            alpha_mle = 1 + len(cn_pos) / np.sum(np.log(cn_pos / 1.0 + 0.5))
        else:
            alpha_mle = None

        # Log-log regression for power law
        if len(unique) > 5:
            log_k = np.log(unique[unique > 0])
            log_c = np.log(counts[unique > 0].astype(float))
            if len(log_k) > 2:
                slope, intercept, r_value, p_value, _ = sp_stats.linregress(log_k, log_c)
                power_law_fit = {
                    "slope": round(slope, 4),
                    "r_squared": round(r_value ** 2, 4),
                    "p_value": round(p_value, 6),
                }
            else:
                power_law_fit = None
        else:
            power_law_fit = None

        # By signature type
        by_sig = defaultdict(list)
        for d in subset:
            stype = signature_type(d["r1"], d["r2"])
            by_sig[stype].append(d["class_number_int"])

        sig_stats = {}
        for stype, vals in by_sig.items():
            sig_stats[stype] = {
                "count": len(vals),
                "mean": round(float(np.mean(vals)), 4),
                "median": float(np.median(vals)),
            }

        results[str(deg)] = {
            "stats": stats,
            "frequency_top20": {int(k): int(v) for k, v in
                                sorted(freq.items(), key=lambda x: -x[1])[:20]},
            "geometric_fit": {
                "p_hat": round(p_hat, 6),
                "ks_statistic": round(geo_ks.statistic, 4),
                "ks_pvalue": round(geo_ks.pvalue, 6),
            },
            "power_law_fit": power_law_fit,
            "alpha_mle": round(alpha_mle, 4) if alpha_mle else None,
            "by_signature_type": sig_stats,
        }

    return results


def analyze_real_quadratic_gauss(data):
    """For real quadratic fields (degree 2, disc > 0): Cohen-Lenstra analysis.

    Cohen-Lenstra predicts that for real quadratic fields:
    - Prob(p | h) ~ 1 - prod_{k>=1}(1 - p^(-k)) for odd prime p
    - Specifically, Prob(3 | h) ~ 1/3 ≈ 0.333...
    - h=1 fraction should be about 75.446% (Cohen-Lenstra constant)
    """
    real_quad = [d for d in data if d["degree"] == 2 and d["disc_sign"] == 1]

    if len(real_quad) < 10:
        return {"error": "insufficient real quadratic fields", "count": len(real_quad)}

    cn_values = [d["class_number_int"] for d in real_quad]
    h1_count = sum(1 for c in cn_values if c == 1)
    h1_frac = h1_count / len(real_quad)

    # Divisibility by small primes
    div_by = {}
    for p in [2, 3, 5, 7, 11, 13]:
        div_count = sum(1 for c in cn_values if c % p == 0)
        div_by[str(p)] = {
            "count": div_count,
            "fraction": round(div_count / len(real_quad), 6),
        }

    # Cohen-Lenstra predictions for Prob(p | h) for real quadratic fields
    # For real quadratic: Prob(p | h) ≈ 1 - prod_{k=2}^{inf} (1 - p^{-k})
    # (the product starts at k=2 for real quadratic)
    cl_predictions = {}
    for p in [3, 5, 7, 11, 13]:
        prod = 1.0
        for k in range(2, 100):
            prod *= (1 - p ** (-k))
        cl_prob = 1 - prod
        observed = div_by[str(p)]["fraction"]
        cl_predictions[str(p)] = {
            "cohen_lenstra_predicted": round(cl_prob, 6),
            "observed": observed,
            "ratio": round(observed / cl_prob, 4) if cl_prob > 0 else None,
        }

    # h=1 Cohen-Lenstra prediction for real quadratic
    # Approximately 0.75446 (the Cohen-Lenstra constant)
    # Computed as product over odd primes p of (1 - Prob_real(p | h))
    # This is approximate since we'd need all primes
    cl_h1_approx = 1.0
    for p in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        prod = 1.0
        for k in range(2, 100):
            prod *= (1 - p ** (-k))
        cl_h1_approx *= prod

    # Include p=2 contribution (genus theory: always divides if disc has >= 3 prime factors)
    # For simplicity, use empirical h=1 fraction

    return {
        "count": len(real_quad),
        "h1_count": h1_count,
        "h1_fraction": round(h1_frac, 6),
        "cohen_lenstra_h1_prediction_approx": round(cl_h1_approx, 6),
        "note": "CL prediction excludes p=2; observed h1 includes 2-part",
        "divisibility_by_prime": div_by,
        "cohen_lenstra_comparison": cl_predictions,
        "mean_class_number": round(float(np.mean(cn_values)), 4),
        "median_class_number": float(np.median(cn_values)),
    }


def analyze_imaginary_quadratic(data):
    """Imaginary quadratic fields (degree 2, disc < 0): verify the 9 known h=1."""
    imag_quad = [d for d in data if d["degree"] == 2 and d["disc_sign"] == -1]

    cn_values = [d["class_number_int"] for d in imag_quad]
    h1_fields = [d for d in imag_quad if d["class_number_int"] == 1]
    h1_discs = sorted([d["disc_abs_int"] for d in h1_fields])

    # Known: -3, -4, -7, -8, -11, -19, -43, -67, -163
    known_h1_discs = [3, 4, 7, 8, 11, 19, 43, 67, 163]
    found_all = set(h1_discs) == set(known_h1_discs) if len(h1_discs) <= 9 else False

    # Cohen-Lenstra for imaginary quadratic: Prob(p | h) ≈ 1 - prod_{k=1}^{inf}(1 - p^{-k})
    cl_predictions_imag = {}
    div_by = {}
    for p in [2, 3, 5, 7, 11, 13]:
        div_count = sum(1 for c in cn_values if c % p == 0)
        div_by[str(p)] = round(div_count / len(imag_quad), 6) if imag_quad else 0

    for p in [3, 5, 7, 11, 13]:
        prod = 1.0
        for k in range(1, 100):
            prod *= (1 - p ** (-k))
        cl_prob = 1 - prod
        cl_predictions_imag[str(p)] = {
            "cohen_lenstra_predicted": round(cl_prob, 6),
            "observed": div_by[str(p)],
            "ratio": round(div_by[str(p)] / cl_prob, 4) if cl_prob > 0 else None,
        }

    return {
        "count": len(imag_quad),
        "h1_count": len(h1_fields),
        "h1_discs_found": h1_discs,
        "known_h1_discs": known_h1_discs,
        "all_9_found": found_all,
        "note": "Baker-Heegner-Stark: exactly 9 imaginary quadratic fields with h=1",
        "h1_fraction": round(len(h1_fields) / len(imag_quad), 6) if imag_quad else 0,
        "divisibility_fractions": div_by,
        "cohen_lenstra_comparison": cl_predictions_imag,
        "mean_class_number": round(float(np.mean(cn_values)), 4) if cn_values else 0,
    }


def main():
    print("=" * 70)
    print("Class Number One Distribution and Properties")
    print("=" * 70)

    # Load data
    print("\n[1] Loading data...")
    local_data = load_local_nf()
    counts_data = load_lmfdb_counts()
    print(f"    Local NF records: {len(local_data)}")
    print(f"    LMFDB count records: {counts_data['total_records']}")

    results = {
        "metadata": {
            "challenge": "Class Number One Distribution and Properties",
            "local_fields": len(local_data),
            "lmfdb_total_fields": 22178569,
            "lmfdb_with_class_number": 21954110,
            "lmfdb_h1_count": 10295486,
            "lmfdb_h1_fraction_global": round(10295486 / 21954110, 6),
        }
    }

    # Part 1: LMFDB-scale h=1 by degree
    print("\n[2] h=1 fraction by degree (LMFDB, 22M fields)...")
    h1_by_degree = analyze_lmfdb_h1_by_degree(counts_data)
    results["h1_by_degree_lmfdb"] = h1_by_degree
    for deg in sorted(h1_by_degree.keys(), key=int)[:15]:
        d = h1_by_degree[deg]
        print(f"    deg={deg:>2}: h1={d['h1_count']:>10,} / {d['total_count']:>10,}  "
              f"({d['h1_fraction']:.4f})")

    # Part 2: h=1 by (degree, r2) = signature
    print("\n[3] h=1 fraction by signature (LMFDB)...")
    h1_by_dr2 = analyze_lmfdb_h1_by_degree_r2(counts_data)
    results["h1_by_degree_r2_lmfdb"] = h1_by_dr2

    # Part 3: h=1 by signature type (aggregated)
    print("\n[4] h=1 by signature type (aggregated)...")
    h1_by_sigtype = analyze_lmfdb_h1_by_signature_type(h1_by_dr2)
    results["h1_by_signature_type"] = h1_by_sigtype
    for stype, d in h1_by_sigtype.items():
        print(f"    {stype:>20}: h1={d['h1_count']:>10,} / {d['total_count']:>10,}  "
              f"({d['h1_fraction']:.4f})")

    # Part 4: h=1 by discriminant range (local data)
    print("\n[5] h=1 fraction by |disc| range (local, deg<=6, |disc|<=10000)...")
    h1_by_disc = analyze_local_h1_by_disc_range(local_data)
    results["h1_by_disc_range_local"] = h1_by_disc
    for deg, info in sorted(h1_by_disc.items()):
        fracs = [b["h1_fraction"] for b in info["bins"]]
        mono = info["monotonic_decreasing"]
        trend = info.get("trend")
        slope_str = f"slope={trend['slope']:.4f}, p={trend['p_value']:.4f}" if trend else "N/A"
        print(f"    deg={deg}: h1_fracs={[f'{f:.2f}' for f in fracs]}  "
              f"monotonic={mono}  {slope_str}")

    # Part 5: Class number distribution shape
    print("\n[6] Class number distribution shape (local)...")
    cn_dist = analyze_class_number_distribution_shape(local_data)
    results["class_number_distribution"] = cn_dist
    for deg, info in sorted(cn_dist.items()):
        s = info["stats"]
        g = info["geometric_fit"]
        pl = info.get("power_law_fit")
        print(f"    deg={deg}: mean={s['mean']:.2f}, median={s['median']:.0f}, "
              f"max={s['max']}")
        print(f"           geometric KS={g['ks_statistic']:.4f} (p={g['ks_pvalue']:.4f})")
        if pl:
            print(f"           power-law slope={pl['slope']:.4f}, R²={pl['r_squared']:.4f}")

    # Part 6: Imaginary quadratic (verify 9 known h=1)
    print("\n[7] Imaginary quadratic fields (verify h=1 problem)...")
    imag_quad = analyze_imaginary_quadratic(local_data)
    results["imaginary_quadratic"] = imag_quad
    print(f"    Fields: {imag_quad['count']}, h=1: {imag_quad['h1_count']}")
    print(f"    h=1 discriminants: {imag_quad['h1_discs_found']}")
    print(f"    All 9 found: {imag_quad['all_9_found']}")
    print(f"    Cohen-Lenstra comparison:")
    for p, cl in imag_quad["cohen_lenstra_comparison"].items():
        print(f"      p={p}: predicted={cl['cohen_lenstra_predicted']:.4f}, "
              f"observed={cl['observed']:.4f}, ratio={cl['ratio']:.4f}")

    # Part 7: Real quadratic (Cohen-Lenstra / Gauss)
    print("\n[8] Real quadratic fields (Gauss / Cohen-Lenstra)...")
    real_quad = analyze_real_quadratic_gauss(local_data)
    results["real_quadratic"] = real_quad
    print(f"    Fields: {real_quad['count']}, h=1: {real_quad['h1_count']} "
          f"({real_quad['h1_fraction']:.4f})")
    print(f"    CL h=1 prediction (approx): {real_quad['cohen_lenstra_h1_prediction_approx']:.4f}")
    print(f"    Cohen-Lenstra comparison:")
    for p, cl in real_quad["cohen_lenstra_comparison"].items():
        print(f"      p={p}: predicted={cl['cohen_lenstra_predicted']:.4f}, "
              f"observed={cl['observed']:.4f}, ratio={cl['ratio']:.4f}")

    # Part 8: LMFDB class number distribution (aggregated bins)
    print("\n[9] Class number distribution (LMFDB aggregated)...")
    lmfdb_cn_dist = analyze_lmfdb_class_number_distribution(counts_data)
    results["class_number_distribution_lmfdb"] = lmfdb_cn_dist

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nGlobal h=1 fraction (LMFDB): {results['metadata']['lmfdb_h1_fraction_global']:.4f} "
          f"({results['metadata']['lmfdb_h1_count']:,} / {results['metadata']['lmfdb_with_class_number']:,})")

    print(f"\nKey findings:")
    # Check if h=1 fraction varies by signature type
    if h1_by_sigtype:
        fracs = {k: v["h1_fraction"] for k, v in h1_by_sigtype.items()}
        print(f"  - Signature type h=1 fractions: {fracs}")
        if "totally_real" in fracs and "totally_complex" in fracs:
            if fracs["totally_real"] > fracs["totally_complex"]:
                print(f"  - Totally real fields have HIGHER h=1 fraction than totally complex")
            else:
                print(f"  - Totally complex fields have HIGHER h=1 fraction than totally real")

    # Cohen-Lenstra check
    if "cohen_lenstra_comparison" in real_quad:
        for p in ["3", "5"]:
            if p in real_quad["cohen_lenstra_comparison"]:
                cl = real_quad["cohen_lenstra_comparison"][p]
                print(f"  - Real quadratic p={p} divisibility: CL predicts {cl['cohen_lenstra_predicted']:.4f}, "
                      f"observed {cl['observed']:.4f}")

    # Monotonicity check
    for deg, info in h1_by_disc.items():
        if info.get("trend"):
            slope = info["trend"]["slope"]
            p_val = info["trend"]["p_value"]
            if p_val < 0.05:
                direction = "decreasing" if slope < 0 else "increasing"
                print(f"  - Degree {deg}: h=1 fraction {direction} with |disc| (slope={slope:.4f}, p={p_val:.4f})")

    # Save
    with open(OUTPUT, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {OUTPUT}")


if __name__ == "__main__":
    main()
