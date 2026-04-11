"""
OEIS Sequence Growth Rate Taxonomy
===================================
Classify OEIS sequences by growth rate: constant, sub-linear, polynomial,
exponential, super-exponential, or factorial.

Cross-tabulate with BM recurrence order and keyword families.
"""

import json
import time
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats

DATA_DIR = Path(__file__).parent.parent / "oeis" / "data"
STRIPPED_FILE = DATA_DIR / "stripped_new.txt"
KEYWORDS_FILE = DATA_DIR / "oeis_keywords.json"
BM_RESULTS_FILE = Path(__file__).parent / "oeis_bm_order_results.json"
OUTPUT_FILE = Path(__file__).parent / "oeis_growth_taxonomy_results.json"

MIN_TERMS = 20
TARGET_SEQUENCES = 10000


def load_sequences(path, min_terms=MIN_TERMS, max_seqs=TARGET_SEQUENCES):
    """Load OEIS sequences from stripped format."""
    sequences = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Format: A000001 ,1,2,3,...,
            parts = line.split(" ", 1)
            if len(parts) != 2:
                continue
            seq_id = parts[0]
            terms_str = parts[1].strip().strip(",")
            if not terms_str:
                continue
            try:
                terms = [int(x) for x in terms_str.split(",") if x.strip()]
            except ValueError:
                continue
            if len(terms) >= min_terms:
                sequences[seq_id] = terms
            if len(sequences) >= max_seqs:
                break
    return sequences


def compute_aic(n, rss, k):
    """AIC for least-squares fit. k = number of parameters."""
    if rss <= 0 or n <= k + 1:
        return float("inf")
    return n * np.log(rss / n) + 2 * k


def classify_growth(terms):
    """
    Classify a sequence's growth rate.

    Returns dict with:
      - class: constant | sub_linear | polynomial | exponential | super_exponential | factorial
      - growth_exponent: for exponential, the base; for polynomial, the power
      - best_fit_r2: R^2 of best model
      - details: per-model fit info
    """
    vals = np.array(terms, dtype=float)
    n = np.arange(1, len(vals) + 1, dtype=float)

    # Check constant
    if np.all(vals == vals[0]):
        return {
            "class": "constant",
            "growth_exponent": 0.0,
            "best_fit_r2": 1.0,
            "details": {}
        }

    # Check near-constant (std/mean < 0.01 or range is tiny)
    val_range = np.max(np.abs(vals)) - np.min(np.abs(vals))
    if val_range == 0:
        return {
            "class": "constant",
            "growth_exponent": 0.0,
            "best_fit_r2": 1.0,
            "details": {}
        }

    # For fitting, we need |a_n| > 0. Use absolute values, skip zeros.
    abs_vals = np.abs(vals)
    mask = abs_vals > 0
    if np.sum(mask) < 10:
        # Too few positive terms to classify reliably
        return {
            "class": "unclassifiable",
            "growth_exponent": None,
            "best_fit_r2": None,
            "details": {"reason": "too_few_positive_terms"}
        }

    log_abs = np.log(abs_vals[mask])
    n_pos = n[mask]
    log_n = np.log(n_pos)
    n_pts = len(log_abs)

    results = {}

    # Model 1: Polynomial — log|a_n| = alpha * log(n) + beta
    try:
        slope, intercept, r, p, se = stats.linregress(log_n, log_abs)
        rss = np.sum((log_abs - (slope * log_n + intercept)) ** 2)
        aic = compute_aic(n_pts, rss, 2)
        results["polynomial"] = {
            "alpha": float(slope),
            "intercept": float(intercept),
            "r2": float(r ** 2),
            "aic": float(aic),
        }
    except Exception:
        results["polynomial"] = {"r2": 0, "aic": float("inf"), "alpha": 0}

    # Model 2: Exponential — log|a_n| = lambda * n + beta
    try:
        slope, intercept, r, p, se = stats.linregress(n_pos, log_abs)
        rss = np.sum((log_abs - (slope * n_pos + intercept)) ** 2)
        aic = compute_aic(n_pts, rss, 2)
        results["exponential"] = {
            "lambda": float(slope),
            "base": float(np.exp(slope)) if abs(slope) < 50 else None,
            "r2": float(r ** 2),
            "aic": float(aic),
        }
    except Exception:
        results["exponential"] = {"r2": 0, "aic": float("inf"), "lambda": 0}

    # Model 3: Factorial — log|a_n| = gamma * n*log(n) + beta
    try:
        n_log_n = n_pos * log_n
        slope, intercept, r, p, se = stats.linregress(n_log_n, log_abs)
        rss = np.sum((log_abs - (slope * n_log_n + intercept)) ** 2)
        aic = compute_aic(n_pts, rss, 2)
        results["factorial"] = {
            "gamma": float(slope),
            "r2": float(r ** 2),
            "aic": float(aic),
        }
    except Exception:
        results["factorial"] = {"r2": 0, "aic": float("inf"), "gamma": 0}

    # Model 4: Sub-linear — log|a_n| = alpha * log(n) + beta, with alpha < 1
    # (Same fit as polynomial, just classified differently)

    # Model 5: Super-exponential — log|a_n| = delta * n^2 + beta (quadratic in n)
    try:
        n_sq = n_pos ** 2
        slope, intercept, r, p, se = stats.linregress(n_sq, log_abs)
        rss = np.sum((log_abs - (slope * n_sq + intercept)) ** 2)
        aic = compute_aic(n_pts, rss, 2)
        results["super_exponential"] = {
            "delta": float(slope),
            "r2": float(r ** 2),
            "aic": float(aic),
        }
    except Exception:
        results["super_exponential"] = {"r2": 0, "aic": float("inf"), "delta": 0}

    # Decision logic: use AIC to pick best model, then refine class
    best_model = min(results, key=lambda k: results[k]["aic"])
    best_r2 = results[best_model]["r2"]

    # Determine class
    if best_model == "polynomial":
        alpha = results["polynomial"]["alpha"]
        if abs(alpha) < 0.05:
            cls = "constant"
            exponent = 0.0
        elif alpha < 1.0:
            cls = "sub_linear"
            exponent = float(alpha)
        else:
            cls = "polynomial"
            exponent = float(alpha)
    elif best_model == "exponential":
        lam = results["exponential"]["lambda"]
        if abs(lam) < 1e-4:
            # Nearly flat exponential = polynomial
            cls = "polynomial"
            exponent = results["polynomial"].get("alpha", 0)
        else:
            cls = "exponential"
            exponent = float(results["exponential"].get("base", np.exp(lam)))
    elif best_model == "factorial":
        cls = "factorial"
        exponent = float(results["factorial"]["gamma"])
    elif best_model == "super_exponential":
        cls = "super_exponential"
        exponent = float(results["super_exponential"]["delta"])
    else:
        cls = "unclassifiable"
        exponent = None

    # Sanity check: if the sequence is decreasing overall, still classify by magnitude growth
    # but note it
    is_decreasing = vals[-1] < vals[0] if len(vals) > 1 else False

    return {
        "class": cls,
        "growth_exponent": exponent,
        "best_fit_r2": float(best_r2),
        "best_model": best_model,
        "is_decreasing": bool(is_decreasing),
        "details": {k: {"r2": v["r2"], "aic": v["aic"]} for k, v in results.items()},
    }


def classify_keyword_family(keywords):
    """Map OEIS keywords to a mathematical family."""
    kw = set(keywords) if keywords else set()
    if "mult" in kw:
        return "multiplicative"
    if "base" in kw:
        return "base_dependent"
    if "walk" in kw or "tabf" in kw or "tabl" in kw:
        return "combinatorial"
    if any(k in kw for k in ["cofr", "cons", "frac"]):
        return "algebraic"
    if "eigen" in kw:
        return "algebraic"
    # Default heuristic from name would need names file; use "unclassified"
    return "unclassified"


def main():
    t0 = time.time()
    print("Loading OEIS sequences...")
    sequences = load_sequences(STRIPPED_FILE, MIN_TERMS, TARGET_SEQUENCES)
    print(f"  Loaded {len(sequences)} sequences with >= {MIN_TERMS} terms")

    # Load keywords
    print("Loading keywords...")
    with open(KEYWORDS_FILE) as f:
        all_keywords = json.load(f)

    # Load BM results (summary only — no per-sequence data)
    bm_order_dist = None
    bm_family = None
    if BM_RESULTS_FILE.exists():
        with open(BM_RESULTS_FILE) as f:
            bm_data = json.load(f)
        bm_order_dist = bm_data.get("order_distribution_verified", {})
        bm_family = bm_data.get("family_comparison", {})
        print(f"  Loaded BM results: {bm_data['statistics']['with_recurrence']} sequences with recurrence")

    # Classify each sequence
    print("Classifying growth rates...")
    classifications = {}
    class_counts = Counter()
    growth_exponents_by_class = defaultdict(list)
    family_class_matrix = defaultdict(lambda: Counter())

    for i, (seq_id, terms) in enumerate(sequences.items()):
        if (i + 1) % 2000 == 0:
            print(f"  {i+1}/{len(sequences)}...")

        result = classify_growth(terms)
        classifications[seq_id] = result
        cls = result["class"]
        class_counts[cls] += 1

        if result["growth_exponent"] is not None:
            growth_exponents_by_class[cls].append(result["growth_exponent"])

        # Cross-tabulate with keyword family
        kws = all_keywords.get(seq_id, [])
        family = classify_keyword_family(kws)
        family_class_matrix[family][cls] += 1

    total = len(classifications)
    elapsed = time.time() - t0

    # Build distribution
    ordered_classes = ["constant", "sub_linear", "polynomial", "exponential",
                       "super_exponential", "factorial", "unclassifiable"]
    distribution = {}
    for cls in ordered_classes:
        cnt = class_counts.get(cls, 0)
        distribution[cls] = {
            "count": cnt,
            "fraction": round(cnt / total, 4) if total > 0 else 0,
        }

    # Growth exponent statistics for exponential sequences
    exp_exponents = growth_exponents_by_class.get("exponential", [])
    exp_stats = {}
    if exp_exponents:
        arr = np.array(exp_exponents)
        arr_finite = arr[np.isfinite(arr)]
        if len(arr_finite) > 0:
            exp_stats = {
                "count": len(arr_finite),
                "mean_base": float(np.mean(arr_finite)),
                "median_base": float(np.median(arr_finite)),
                "std_base": float(np.std(arr_finite)),
                "min_base": float(np.min(arr_finite)),
                "max_base": float(np.max(arr_finite)),
                "percentiles": {
                    "p10": float(np.percentile(arr_finite, 10)),
                    "p25": float(np.percentile(arr_finite, 25)),
                    "p50": float(np.percentile(arr_finite, 50)),
                    "p75": float(np.percentile(arr_finite, 75)),
                    "p90": float(np.percentile(arr_finite, 90)),
                },
            }

    # Polynomial exponent stats
    poly_exponents = growth_exponents_by_class.get("polynomial", [])
    poly_stats = {}
    if poly_exponents:
        arr = np.array(poly_exponents)
        arr_finite = arr[np.isfinite(arr)]
        if len(arr_finite) > 0:
            poly_stats = {
                "count": len(arr_finite),
                "mean_power": float(np.mean(arr_finite)),
                "median_power": float(np.median(arr_finite)),
                "std_power": float(np.std(arr_finite)),
                "min_power": float(np.min(arr_finite)),
                "max_power": float(np.max(arr_finite)),
            }

    # Family cross-tabulation
    family_cross = {}
    for family, class_counter in sorted(family_class_matrix.items()):
        family_total = sum(class_counter.values())
        family_cross[family] = {
            "total": family_total,
            "breakdown": {cls: class_counter.get(cls, 0) for cls in ordered_classes},
            "dominant_class": class_counter.most_common(1)[0][0] if class_counter else None,
        }

    # BM recurrence cross-tabulation (qualitative, from BM summary data)
    bm_cross = None
    if bm_family:
        bm_cross = {
            "note": "From BM order results (summary level, not per-sequence join)",
            "growth_rate_correlation_with_bm": bm_data.get("growth_rate_correlation", {}),
            "family_recurrence_rates": {},
        }
        for fam, fdata in bm_family.items():
            bm_cross["family_recurrence_rates"][fam] = {
                "count": fdata["count"],
                "with_recurrence": fdata["with_recurrence"],
                "fraction_with_recurrence": fdata["fraction_with_recurrence"],
            }

    # R^2 quality check
    r2_values = [c["best_fit_r2"] for c in classifications.values()
                 if c["best_fit_r2"] is not None]
    r2_stats = {
        "mean": float(np.mean(r2_values)),
        "median": float(np.median(r2_values)),
        "fraction_above_0.9": float(np.mean(np.array(r2_values) > 0.9)),
        "fraction_above_0.95": float(np.mean(np.array(r2_values) > 0.95)),
    }

    # Assemble results
    results = {
        "experiment": "OEIS Sequence Growth Rate Taxonomy",
        "method": {
            "description": "Fit log|a_n| against 4 models (polynomial, exponential, factorial, super-exponential) using AIC model selection",
            "models": [
                "polynomial: log|a_n| ~ alpha * log(n)",
                "exponential: log|a_n| ~ lambda * n",
                "factorial: log|a_n| ~ gamma * n*log(n)",
                "super_exponential: log|a_n| ~ delta * n^2",
            ],
            "n_sequences": total,
            "min_terms": MIN_TERMS,
        },
        "distribution": distribution,
        "fit_quality": r2_stats,
        "exponential_growth_rates": exp_stats,
        "polynomial_growth_powers": poly_stats,
        "keyword_family_cross_tabulation": family_cross,
        "bm_recurrence_cross_tabulation": bm_cross,
        "elapsed_seconds": round(elapsed, 1),
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {OUTPUT_FILE}")
    print(f"Elapsed: {elapsed:.1f}s")
    print(f"\nGrowth Rate Distribution ({total} sequences):")
    print("-" * 50)
    for cls in ordered_classes:
        d = distribution[cls]
        bar = "#" * int(d["fraction"] * 100)
        print(f"  {cls:20s}: {d['count']:5d} ({d['fraction']*100:5.1f}%) {bar}")

    if exp_stats:
        print(f"\nExponential bases: median={exp_stats['median_base']:.3f}, "
              f"mean={exp_stats['mean_base']:.3f}")
    if poly_stats:
        print(f"Polynomial powers: median={poly_stats['median_power']:.3f}, "
              f"mean={poly_stats['mean_power']:.3f}")

    print(f"\nFit quality: {r2_stats['fraction_above_0.9']*100:.1f}% of fits have R^2 > 0.9")

    print("\nFamily cross-tabulation:")
    for fam, fd in sorted(family_cross.items()):
        print(f"  {fam}: {fd['total']} seqs, dominant={fd['dominant_class']}")


if __name__ == "__main__":
    main()
