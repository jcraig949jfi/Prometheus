#!/usr/bin/env python3
"""
Asymptotic Regime Classification — Structure at Infinity
=========================================================
Challenge: ChatGPT Part 3 #7 / Grok Part 3 #4

Classifies OEIS sequences by growth regime, computes within-regime
mod-p enrichment, matches against EC and knot growth classes, and
analyzes F13 near-miss predictive value.
"""

import json
import math
import time
import warnings
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import stats as sp_stats
from scipy.optimize import curve_fit

warnings.filterwarnings("ignore", category=RuntimeWarning)

ROOT = Path(__file__).resolve().parents[4]  # F:/Prometheus
OEIS_FILE = ROOT / "cartography" / "oeis" / "data" / "stripped_new.txt"
KNOTS_FILE = ROOT / "cartography" / "knots" / "data" / "knots.json"
NEAR_MISS_FILE = ROOT / "cartography" / "shared" / "scripts" / "v2" / "near_miss_results.json"
FAILURE_FILE = ROOT / "cartography" / "shared" / "scripts" / "v2" / "failure_mode_results.json"
OUT_FILE = ROOT / "cartography" / "shared" / "scripts" / "v2" / "asymptotic_classifier_results.json"

# ── OEIS Parser ──────────────────────────────────────────────────────

def parse_oeis(path, min_terms=50, max_seqs=10000):
    """Parse stripped OEIS file, return dict {A-number: [int list]}."""
    seqs = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split(" ", 1)
            if len(parts) < 2:
                continue
            anum = parts[0]
            raw = parts[1].strip().strip(",")
            if not raw:
                continue
            try:
                vals = [int(x) for x in raw.split(",") if x.strip()]
            except ValueError:
                continue
            if len(vals) >= min_terms:
                seqs[anum] = vals
            if len(seqs) >= max_seqs:
                break
    return seqs


# ── Growth Regime Classifier ────────────────────────────────────────

REGIMES = [
    "constant", "sub_linear", "linear", "polynomial",
    "exponential", "super_exponential", "oscillatory"
]


def classify_sequence(vals, anum=""):
    """
    Classify a single sequence by its asymptotic growth regime.
    Returns dict with regime, parameters, and fit quality.
    """
    arr = np.array(vals, dtype=np.float64)
    n = len(arr)
    ns = np.arange(1, n + 1, dtype=np.float64)

    result = {
        "regime": "unknown",
        "alpha": None,
        "base_r": None,
        "fit_residual": float("inf"),
        "n_terms": n,
        "has_negative": bool(np.any(arr < 0)),
        "is_bounded": False,
        "sign_changes": 0,
    }

    # Count sign changes
    nonzero = arr[arr != 0]
    if len(nonzero) > 1:
        signs = np.sign(nonzero)
        result["sign_changes"] = int(np.sum(np.abs(np.diff(signs)) > 0))

    # Check oscillatory: many sign changes relative to length
    if result["sign_changes"] > n * 0.3 and result["has_negative"]:
        result["regime"] = "oscillatory"
        result["fit_residual"] = 0.0
        return result

    # Check constant
    if np.std(arr) < 1e-10:
        result["regime"] = "constant"
        result["fit_residual"] = 0.0
        return result

    # Check bounded (range doesn't grow with n)
    if n >= 50:
        first_half_range = np.ptp(arr[:n // 2])
        second_half_range = np.ptp(arr[n // 2:])
        if first_half_range > 0 and second_half_range / max(first_half_range, 1) < 2.0:
            if np.ptp(arr) < 1000:  # bounded in absolute terms too
                result["is_bounded"] = True

    # Work with absolute values for growth fitting
    abs_arr = np.abs(arr)
    pos_mask = abs_arr > 0
    if np.sum(pos_mask) < 10:
        result["regime"] = "constant"
        result["fit_residual"] = 0.0
        return result

    # Use tail for fitting (more representative of asymptotics)
    tail_start = max(0, n // 4)
    ns_tail = ns[tail_start:]
    abs_tail = abs_arr[tail_start:]
    pos_tail = abs_tail > 0

    if np.sum(pos_tail) < 5:
        result["regime"] = "constant"
        return result

    fits = {}

    # 1. Polynomial fit: log(a(n)) ~ alpha * log(n) + log(C)
    try:
        log_n = np.log(ns_tail[pos_tail])
        log_a = np.log(abs_tail[pos_tail])
        if len(log_n) >= 5 and np.std(log_n) > 0:
            slope, intercept, r_val, _, _ = sp_stats.linregress(log_n, log_a)
            residual = 1.0 - r_val ** 2
            fits["polynomial"] = {
                "residual": residual,
                "alpha": slope,
                "C": math.exp(intercept),
            }
    except Exception:
        pass

    # 2. Exponential fit: log(a(n)) ~ n * log(r) + log(C)
    try:
        log_a = np.log(abs_tail[pos_tail])
        n_vals = ns_tail[pos_tail]
        if len(n_vals) >= 5 and np.std(n_vals) > 0:
            slope, intercept, r_val, _, _ = sp_stats.linregress(n_vals, log_a)
            residual = 1.0 - r_val ** 2
            if slope > 0.01:  # must be growing
                fits["exponential"] = {
                    "residual": residual,
                    "base_r": math.exp(slope),
                    "C": math.exp(intercept),
                }
    except Exception:
        pass

    # 3. Super-exponential: log(log(a(n))) ~ log(n) (grows like n^n or n!)
    try:
        big_mask = abs_tail > math.e
        if np.sum(big_mask) >= 5:
            log_log_a = np.log(np.log(abs_tail[big_mask]))
            log_n_big = np.log(ns_tail[big_mask])
            finite = np.isfinite(log_log_a) & np.isfinite(log_n_big)
            if np.sum(finite) >= 5:
                slope, intercept, r_val, _, _ = sp_stats.linregress(
                    log_n_big[finite], log_log_a[finite]
                )
                residual = 1.0 - r_val ** 2
                if slope > 0.5:  # super-exponential signature
                    fits["super_exponential"] = {
                        "residual": residual,
                        "slope": slope,
                    }
    except Exception:
        pass

    # Select best fit
    if not fits:
        if result["is_bounded"]:
            result["regime"] = "oscillatory"
        else:
            result["regime"] = "unknown"
        return result

    best_name = min(fits, key=lambda k: fits[k]["residual"])
    best = fits[best_name]

    # Refinement for polynomial
    if best_name == "polynomial":
        alpha = best["alpha"]
        if alpha < 0.01:
            result["regime"] = "constant"
        elif alpha < 1.0:
            result["regime"] = "sub_linear"
            result["alpha"] = round(alpha, 4)
        elif abs(alpha - 1.0) < 0.15:
            result["regime"] = "linear"
            result["alpha"] = round(alpha, 4)
        else:
            result["regime"] = "polynomial"
            result["alpha"] = round(alpha, 4)
        result["fit_residual"] = best["residual"]

        # But check: if exponential fits MUCH better, override
        if "exponential" in fits and fits["exponential"]["residual"] < best["residual"] * 0.5:
            result["regime"] = "exponential"
            result["base_r"] = round(fits["exponential"]["base_r"], 6)
            result["fit_residual"] = fits["exponential"]["residual"]
            result["alpha"] = None

    elif best_name == "exponential":
        result["regime"] = "exponential"
        result["base_r"] = round(best["base_r"], 6)
        result["fit_residual"] = best["residual"]

        # Check super_exponential override
        if "super_exponential" in fits and fits["super_exponential"]["residual"] < best["residual"] * 0.7:
            result["regime"] = "super_exponential"
            result["fit_residual"] = fits["super_exponential"]["residual"]
            result["base_r"] = None

    elif best_name == "super_exponential":
        result["regime"] = "super_exponential"
        result["fit_residual"] = best["residual"]

    return result


# ── Mod-p Fingerprinting ────────────────────────────────────────────

def mod_p_fingerprint(vals, primes=(2, 3, 5, 7, 11, 13)):
    """Compute mod-p distribution vector for a sequence."""
    fp = {}
    for p in primes:
        residues = [v % p for v in vals]
        counts = Counter(residues)
        total = len(residues)
        dist = tuple(counts.get(r, 0) / total for r in range(p))
        fp[p] = dist
    return fp


def fingerprint_distance(fp1, fp2):
    """L2 distance between two mod-p fingerprints."""
    d = 0.0
    for p in fp1:
        if p in fp2:
            v1 = np.array(fp1[p])
            v2 = np.array(fp2[p])
            d += np.sum((v1 - v2) ** 2)
    return math.sqrt(d)


def compute_regime_enrichment(classified_seqs, oeis_data):
    """
    Within each regime, measure mod-p clustering.
    Compare within-regime distances to cross-regime distances.
    """
    # Build fingerprints
    fps = {}
    for anum, info in classified_seqs.items():
        if anum in oeis_data:
            fps[anum] = mod_p_fingerprint(oeis_data[anum])

    # Group by regime
    regime_groups = defaultdict(list)
    for anum, info in classified_seqs.items():
        regime_groups[info["regime"]].append(anum)

    results = {}
    all_within = []
    all_cross = []

    for regime, members in regime_groups.items():
        if len(members) < 10:
            continue

        # Sample within-regime distances
        within_dists = []
        sample = members[:min(200, len(members))]
        for i in range(min(500, len(sample) * (len(sample) - 1) // 2)):
            a, b = np.random.choice(len(sample), 2, replace=False)
            a_id, b_id = sample[a], sample[b]
            if a_id in fps and b_id in fps:
                within_dists.append(fingerprint_distance(fps[a_id], fps[b_id]))

        # Sample cross-regime distances
        other_members = [a for r, ms in regime_groups.items() if r != regime for a in ms]
        cross_dists = []
        if other_members:
            for i in range(min(500, len(sample) * len(other_members))):
                a = sample[np.random.randint(len(sample))]
                b = other_members[np.random.randint(len(other_members))]
                if a in fps and b in fps:
                    cross_dists.append(fingerprint_distance(fps[a], fps[b]))

        if within_dists and cross_dists:
            within_mean = np.mean(within_dists)
            cross_mean = np.mean(cross_dists)
            # Mann-Whitney test
            try:
                stat, pval = sp_stats.mannwhitneyu(within_dists, cross_dists, alternative="less")
            except Exception:
                pval = 1.0
            enrichment_ratio = cross_mean / within_mean if within_mean > 0 else 1.0

            results[regime] = {
                "n_members": len(members),
                "within_mean_dist": round(within_mean, 6),
                "cross_mean_dist": round(cross_mean, 6),
                "enrichment_ratio": round(enrichment_ratio, 4),
                "p_value": float(pval),
                "significant": pval < 0.01,
            }
            all_within.extend(within_dists)
            all_cross.extend(cross_dists)

    # Fine-grained: within polynomial, do same-alpha cluster better?
    poly_members = regime_groups.get("polynomial", [])
    fine_grained = {}
    if len(poly_members) >= 50:
        # Bin by alpha (rounded to nearest 0.5)
        alpha_bins = defaultdict(list)
        for anum in poly_members:
            a = classified_seqs[anum].get("alpha")
            if a is not None:
                bin_key = round(a * 2) / 2  # nearest 0.5
                alpha_bins[bin_key].append(anum)

        same_bin_dists = []
        diff_bin_dists = []
        for bin_key, members in alpha_bins.items():
            if len(members) < 5:
                continue
            sample = members[:100]
            for i in range(min(200, len(sample) * (len(sample) - 1) // 2)):
                a, b = np.random.choice(len(sample), 2, replace=False)
                if sample[a] in fps and sample[b] in fps:
                    same_bin_dists.append(fingerprint_distance(fps[sample[a]], fps[sample[b]]))

            # Cross-bin
            other = [x for k, ms in alpha_bins.items() if k != bin_key for x in ms]
            if other:
                for i in range(min(200, len(sample) * len(other))):
                    a = sample[np.random.randint(len(sample))]
                    b = other[np.random.randint(len(other))]
                    if a in fps and b in fps:
                        diff_bin_dists.append(fingerprint_distance(fps[a], fps[b]))

        if same_bin_dists and diff_bin_dists:
            try:
                stat, pval = sp_stats.mannwhitneyu(same_bin_dists, diff_bin_dists, alternative="less")
            except Exception:
                pval = 1.0
            fine_grained["polynomial_alpha_bins"] = {
                "n_bins": len([b for b in alpha_bins if len(alpha_bins[b]) >= 5]),
                "same_alpha_mean_dist": round(np.mean(same_bin_dists), 6),
                "diff_alpha_mean_dist": round(np.mean(diff_bin_dists), 6),
                "enrichment_ratio": round(np.mean(diff_bin_dists) / max(np.mean(same_bin_dists), 1e-10), 4),
                "p_value": float(pval),
                "significant": pval < 0.01,
            }

    # Same for exponential base_r
    exp_members = regime_groups.get("exponential", [])
    if len(exp_members) >= 30:
        r_bins = defaultdict(list)
        for anum in exp_members:
            r = classified_seqs[anum].get("base_r")
            if r is not None and r > 0:
                bin_key = round(math.log2(r) * 2) / 2  # bin by log2(r) to nearest 0.5
                r_bins[bin_key].append(anum)

        same_r_dists = []
        diff_r_dists = []
        for bin_key, members in r_bins.items():
            if len(members) < 3:
                continue
            sample = members[:100]
            for i in range(min(100, len(sample) * (len(sample) - 1) // 2)):
                a, b = np.random.choice(len(sample), 2, replace=False)
                if sample[a] in fps and sample[b] in fps:
                    same_r_dists.append(fingerprint_distance(fps[sample[a]], fps[sample[b]]))
            other = [x for k, ms in r_bins.items() if k != bin_key for x in ms]
            if other:
                for i in range(min(100, len(sample) * len(other))):
                    a = sample[np.random.randint(len(sample))]
                    b = other[np.random.randint(len(other))]
                    if a in fps and b in fps:
                        diff_r_dists.append(fingerprint_distance(fps[a], fps[b]))

        if same_r_dists and diff_r_dists:
            try:
                stat, pval = sp_stats.mannwhitneyu(same_r_dists, diff_r_dists, alternative="less")
            except Exception:
                pval = 1.0
            fine_grained["exponential_base_bins"] = {
                "n_bins": len([b for b in r_bins if len(r_bins[b]) >= 3]),
                "same_base_mean_dist": round(np.mean(same_r_dists), 6),
                "diff_base_mean_dist": round(np.mean(diff_r_dists), 6),
                "enrichment_ratio": round(np.mean(diff_r_dists) / max(np.mean(same_r_dists), 1e-10), 4),
                "p_value": float(pval),
                "significant": pval < 0.01,
            }

    return {
        "per_regime": results,
        "fine_grained": fine_grained,
        "global_within_mean": round(np.mean(all_within), 6) if all_within else None,
        "global_cross_mean": round(np.mean(all_cross), 6) if all_cross else None,
    }


# ── EC a_p Classification ───────────────────────────────────────────

def classify_ec_ap():
    """Classify EC a_p sequences — should be O(sqrt(p)) by Hasse bound."""
    try:
        import duckdb
        db = duckdb.connect(str(ROOT / "charon" / "data" / "charon.duckdb"), read_only=True)
        rows = db.execute(
            "SELECT lmfdb_label, aplist, conductor, rank, cm FROM elliptic_curves "
            "WHERE aplist IS NOT NULL LIMIT 2000"
        ).fetchall()
        db.close()
    except Exception as e:
        return {"error": str(e)}

    primes_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
                 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

    results = {"n_curves": len(rows), "regime_distribution": Counter(), "alpha_stats": []}
    alphas = []

    for label, aplist, conductor, rank, cm in rows:
        if not aplist or len(aplist) < 10:
            continue
        # a_p indexed by prime: aplist[i] = a_{p_i}
        n_primes = min(len(aplist), len(primes_25))
        ps = np.array(primes_25[:n_primes], dtype=np.float64)
        aps = np.array(aplist[:n_primes], dtype=np.float64)
        abs_aps = np.abs(aps)

        # Fit |a_p| ~ C * p^alpha
        pos = abs_aps > 0
        if np.sum(pos) < 5:
            continue
        try:
            log_p = np.log(ps[pos])
            log_ap = np.log(abs_aps[pos])
            slope, intercept, r_val, _, _ = sp_stats.linregress(log_p, log_ap)
            alphas.append(slope)
            if slope < 0.35:
                regime = "sub_sqrt"
            elif slope < 0.65:
                regime = "hasse_sqrt"  # expected ~0.5
            else:
                regime = "super_sqrt"
            results["regime_distribution"][regime] += 1
        except Exception:
            continue

    if alphas:
        alphas = np.array(alphas)
        results["alpha_stats"] = {
            "mean": round(float(np.mean(alphas)), 4),
            "median": round(float(np.median(alphas)), 4),
            "std": round(float(np.std(alphas)), 4),
            "min": round(float(np.min(alphas)), 4),
            "max": round(float(np.max(alphas)), 4),
            "expected": 0.5,
            "n_classified": len(alphas),
        }
    results["regime_distribution"] = dict(results["regime_distribution"])
    return results


# ── Knot Polynomial Classification ──────────────────────────────────

def classify_knot_growth():
    """Classify growth of knot polynomial coefficient sequences."""
    with open(KNOTS_FILE) as f:
        data = json.load(f)

    knots = data["knots"]
    results = {"n_knots": len(knots), "regime_distribution": Counter(), "details": []}

    for knot in knots:
        for poly_type in ["jones_coeffs", "alex_coeffs"]:
            coeffs = knot.get(poly_type)
            if not coeffs or not isinstance(coeffs, list):
                # Parse from polynomial dict
                poly = knot.get(poly_type.replace("_coeffs", ""))
                if poly and "coefficients" in poly:
                    coeffs = poly["coefficients"]

            if not coeffs or len(coeffs) < 4:
                continue

            abs_coeffs = [abs(c) for c in coeffs]
            max_coeff = max(abs_coeffs)

            # Knot poly coefficients are typically bounded and short
            # Classify by magnitude growth pattern
            if max_coeff <= 1:
                regime = "unit_bounded"
            elif max_coeff <= 10:
                regime = "small_bounded"
            elif max_coeff <= 100:
                regime = "moderate"
            else:
                regime = "large"

            results["regime_distribution"][f"{poly_type}_{regime}"] += 1

    results["regime_distribution"] = dict(results["regime_distribution"])
    return results


# ── Cross-Domain Matching ────────────────────────────────────────────

def cross_domain_match(oeis_classified, ec_results, knot_results):
    """Find OEIS sequences whose growth regime matches EC or knot classes."""
    matches = {"ec_matching_oeis": [], "knot_matching_oeis": []}

    # EC a_p growth is ~sqrt(p), so alpha ~0.5
    # Find OEIS sequences with alpha in [0.4, 0.6]
    ec_alpha_range = (0.35, 0.65)
    for anum, info in oeis_classified.items():
        if info["regime"] in ("sub_linear", "polynomial"):
            alpha = info.get("alpha")
            if alpha and ec_alpha_range[0] <= alpha <= ec_alpha_range[1]:
                matches["ec_matching_oeis"].append({
                    "anum": anum,
                    "alpha": alpha,
                    "regime": info["regime"],
                })

    # Knot coefficients are bounded+oscillatory — find OEIS sequences
    # that are oscillatory (sign-changing) specifically, not just constant/bounded
    for anum, info in oeis_classified.items():
        if info["regime"] == "oscillatory" and info.get("sign_changes", 0) > 5:
            matches["knot_matching_oeis"].append({
                "anum": anum,
                "regime": info["regime"],
                "sign_changes": info.get("sign_changes", 0),
            })

    matches["ec_matching_count"] = len(matches["ec_matching_oeis"])
    matches["knot_matching_count"] = len(matches["knot_matching_oeis"])
    # Truncate for output
    matches["ec_matching_oeis"] = matches["ec_matching_oeis"][:50]
    matches["knot_matching_oeis"] = matches["knot_matching_oeis"][:50]

    return matches


# ── F13 Near-Miss Analysis ──────────────────────────────────────────

def analyze_f13_near_misses(oeis_data):
    """
    Classify asymptotic regime of F13-killed near-misses.
    Compare resurrected vs truly-dead regime distributions.
    """
    with open(NEAR_MISS_FILE) as f:
        nm = json.load(f)

    f13 = nm["f13_resurrection"]
    resurrected = f13["records"]  # 34 records
    total_kills = f13["total_f13_kills"]  # 330
    truly_dead_count = f13["truly_dead"]  # 243
    borderline_count = f13["borderline"]  # 53

    # Extract OEIS A-numbers from resurrected claims
    resurrected_pairs = [(r["pair"], r.get("claim", "")) for r in resurrected]

    # Also check all_resurrected for kill_source = F13
    all_res = nm.get("all_resurrected", [])
    f13_res = [r for r in all_res if "F13" in str(r.get("kill_source", ""))]

    # Since we can't directly map near-misses to specific OEIS sequences
    # (they're cross-domain pairs), analyze the regime distribution of OEIS
    # sequences that appear in pairs
    oeis_in_pairs = set()
    for r in all_res:
        pair = r.get("pair", "")
        if "OEIS" in pair:
            oeis_in_pairs.add(pair)

    # Classify a sample of OEIS sequences and see if F13-killed ones differ
    # The key insight: F13 kills based on growth rate mismatch
    # We can test if sequences from different growth regimes are more/less
    # likely to be F13-killed

    results = {
        "total_f13_kills": total_kills,
        "resurrected": len(resurrected),
        "borderline": borderline_count,
        "truly_dead": truly_dead_count,
        "resurrection_rate": round(len(resurrected) / total_kills, 4) if total_kills > 0 else 0,
        "resurrected_pair_types": Counter([r["pair"] for r in resurrected]),
        "resurrected_confidence_stats": {},
        "f13_in_all_resurrected": len(f13_res),
        "regime_prediction_analysis": {},
    }

    # Confidence distribution for resurrected
    confidences_raw = [r.get("confidence", r.get("resurrection_confidence", 0)) for r in resurrected]
    confidences = []
    for c in confidences_raw:
        try:
            confidences.append(float(c))
        except (ValueError, TypeError):
            pass
    if confidences:
        results["resurrected_confidence_stats"] = {
            "mean": round(np.mean(confidences), 4),
            "median": round(float(np.median(confidences)), 4),
            "std": round(float(np.std(confidences)), 4),
        }

    # Analyze resurrection reasons
    reason_counts = Counter()
    for r in resurrected:
        for reason in r.get("resurrection_reasons", []):
            reason_counts[reason] += 1
    results["resurrection_reason_distribution"] = dict(reason_counts)

    # Key analysis: margin distribution (how close to threshold)
    margins = [r.get("margin", 0) for r in resurrected]
    if margins:
        results["margin_stats"] = {
            "mean": round(np.mean(margins), 4),
            "median": round(float(np.median(margins)), 4),
            "min": round(float(np.min(margins)), 4),
            "max": round(float(np.max(margins)), 4),
        }

    # Worst baseline type distribution — tells us WHICH growth comparison killed them
    worst_baselines = Counter([r.get("worst_baseline_type", "unknown") for r in resurrected])
    results["worst_baseline_distribution"] = dict(worst_baselines)

    results["resurrected_pair_types"] = dict(results["resurrected_pair_types"])

    return results


# ── Main ─────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    np.random.seed(42)

    print("[1/6] Parsing OEIS sequences (min 50 terms, max 10K)...")
    oeis_data = parse_oeis(OEIS_FILE, min_terms=50, max_seqs=10000)
    print(f"  Loaded {len(oeis_data)} sequences")

    print("[2/6] Classifying growth regimes...")
    classified = {}
    for anum, vals in oeis_data.items():
        classified[anum] = classify_sequence(vals, anum)

    regime_dist = Counter(info["regime"] for info in classified.values())
    print(f"  Regime distribution: {dict(regime_dist)}")

    # Alpha distribution for polynomial
    poly_alphas = [info["alpha"] for info in classified.values()
                   if info["regime"] == "polynomial" and info["alpha"] is not None]
    sublin_alphas = [info["alpha"] for info in classified.values()
                     if info["regime"] == "sub_linear" and info["alpha"] is not None]
    linear_alphas = [info["alpha"] for info in classified.values()
                     if info["regime"] == "linear" and info["alpha"] is not None]

    # Exponential base distribution
    exp_bases = [info["base_r"] for info in classified.values()
                 if info["regime"] == "exponential" and info["base_r"] is not None]

    print("[3/6] Computing mod-p fingerprint enrichment...")
    enrichment = compute_regime_enrichment(classified, oeis_data)
    print(f"  Regimes with significant enrichment: "
          f"{sum(1 for v in enrichment['per_regime'].values() if v.get('significant'))}"
          f"/{len(enrichment['per_regime'])}")

    print("[4/6] Classifying EC a_p growth...")
    ec_results = classify_ec_ap()
    print(f"  EC alpha stats: {ec_results.get('alpha_stats', {})}")

    print("[5/6] Classifying knot polynomial growth...")
    knot_results = classify_knot_growth()
    print(f"  Knot regime distribution: {knot_results['regime_distribution']}")

    print("[6/6] Cross-domain matching & F13 analysis...")
    cross_domain = cross_domain_match(classified, ec_results, knot_results)
    f13_analysis = analyze_f13_near_misses(oeis_data)

    elapsed = time.time() - t0

    # Build output
    output = {
        "meta": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed_seconds": round(elapsed, 1),
            "n_sequences_classified": len(classified),
            "challenge": "Asymptotic Regime Classification — Structure at Infinity",
        },
        "regime_distribution": {
            "counts": dict(regime_dist),
            "percentages": {k: round(v / len(classified) * 100, 1)
                           for k, v in regime_dist.items()},
        },
        "alpha_distribution": {
            "polynomial": {
                "count": len(poly_alphas),
                "mean": round(np.mean(poly_alphas), 3) if poly_alphas else None,
                "median": round(float(np.median(poly_alphas)), 3) if poly_alphas else None,
                "std": round(float(np.std(poly_alphas)), 3) if poly_alphas else None,
                "histogram_bins": {},
            },
            "sub_linear": {
                "count": len(sublin_alphas),
                "mean": round(np.mean(sublin_alphas), 3) if sublin_alphas else None,
            },
            "linear": {
                "count": len(linear_alphas),
                "mean": round(np.mean(linear_alphas), 3) if linear_alphas else None,
            },
        },
        "exponential_base_distribution": {
            "count": len(exp_bases),
            "mean": round(np.mean(exp_bases), 3) if exp_bases else None,
            "median": round(float(np.median(exp_bases)), 3) if exp_bases else None,
            "common_bases": {},
        },
        "mod_p_enrichment": enrichment,
        "ec_growth_classification": ec_results,
        "knot_growth_classification": knot_results,
        "cross_domain_matches": cross_domain,
        "f13_near_miss_analysis": f13_analysis,
        "conclusions": {},
    }

    # Alpha histogram
    if poly_alphas:
        hist, edges = np.histogram(poly_alphas, bins=[0, 1, 1.5, 2, 2.5, 3, 4, 5, 10, 50])
        output["alpha_distribution"]["polynomial"]["histogram_bins"] = {
            f"{edges[i]:.1f}-{edges[i+1]:.1f}": int(hist[i]) for i in range(len(hist))
        }

    # Exponential base histogram
    if exp_bases:
        bases_arr = np.array(exp_bases)
        common = Counter(round(b, 1) for b in exp_bases)
        output["exponential_base_distribution"]["common_bases"] = dict(common.most_common(20))

    # Conclusions
    output["conclusions"] = {
        "regime_landscape": (
            f"Of {len(classified)} OEIS sequences with 50+ terms: "
            f"{regime_dist.get('polynomial', 0)} polynomial, "
            f"{regime_dist.get('exponential', 0)} exponential, "
            f"{regime_dist.get('super_exponential', 0)} super-exponential, "
            f"{regime_dist.get('oscillatory', 0)} oscillatory, "
            f"{regime_dist.get('sub_linear', 0)} sub-linear, "
            f"{regime_dist.get('linear', 0)} linear, "
            f"{regime_dist.get('constant', 0)} constant."
        ),
        "enrichment_finding": (
            f"Within-regime mod-p enrichment: "
            f"{sum(1 for v in enrichment['per_regime'].values() if v.get('significant'))}"
            f" of {len(enrichment['per_regime'])} regimes show significant clustering "
            f"(p < 0.01). Global within-regime mean distance = "
            f"{enrichment.get('global_within_mean', 'N/A')}, "
            f"cross-regime = {enrichment.get('global_cross_mean', 'N/A')}."
        ),
        "fine_grained_finding": (
            "Fine-grained alpha/base clustering: "
            + (" | ".join(
                f"{k}: enrichment={v['enrichment_ratio']}, p={v['p_value']:.2e}, sig={v['significant']}"
                for k, v in enrichment.get("fine_grained", {}).items()
            ) if enrichment.get("fine_grained") else "insufficient data for fine-grained test")
        ),
        "ec_finding": (
            f"EC a_p sequences: mean alpha = "
            f"{ec_results.get('alpha_stats', {}).get('mean', 'N/A')} "
            f"(expected 0.5 from Hasse). Distribution: {ec_results.get('regime_distribution', {})}."
        ),
        "cross_domain_finding": (
            f"Cross-domain: {cross_domain['ec_matching_count']} OEIS sequences in EC growth class "
            f"(alpha~0.5), {cross_domain['knot_matching_count']} in knot bounded class."
        ),
        "f13_finding": (
            f"F13 kills: {f13_analysis['total_f13_kills']} total, "
            f"{f13_analysis['resurrected']} resurrected ({f13_analysis['resurrection_rate']*100:.1f}%). "
            f"Worst baseline types: {f13_analysis.get('worst_baseline_distribution', {})}. "
            f"Resurrection reasons: {f13_analysis.get('resurrection_reason_distribution', {})}."
        ),
    }

    # Write results
    with open(OUT_FILE, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to {OUT_FILE}")
    print(f"Elapsed: {elapsed:.1f}s")

    # Print summary
    print("\n" + "=" * 70)
    print("ASYMPTOTIC REGIME CLASSIFICATION — SUMMARY")
    print("=" * 70)
    for k, v in output["conclusions"].items():
        print(f"\n{k}:")
        print(f"  {v}")


if __name__ == "__main__":
    main()
