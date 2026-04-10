"""
Scaling Law Peak Prime — Map the Full Enrichment Curve to p=31
================================================================
R3-3: Extend the enrichment curve from p=23 to p=31 and fit models.

Tests:
1. Raw enrichment at each prime (mod-p fingerprint exact match rate)
2. Detrended enrichment (strip small prime factors first)
3. Model fits: power law, logistic, Gaussian peak (AIC/BIC)
4. Family-specific enrichment curves for top 5 families

Uses C11 clusters (2,246 families) as primary, C08 (173) as fallback.

Usage:
    python scaling_law_peak.py
"""

import gzip
import json
import math
import os
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import curve_fit

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[4]
V2_DIR = Path(__file__).resolve().parent
C11_RESULTS = V2_DIR / "algebraic_dna_fungrim_results.json"
C08_RESULTS = V2_DIR / "recurrence_euler_factor_results.json"
OEIS_STRIPPED_GZ = ROOT / "cartography" / "oeis" / "data" / "stripped_full.gz"
OEIS_STRIPPED_TXT = ROOT / "cartography" / "oeis" / "data" / "stripped_new.txt"
OUT_FILE = V2_DIR / "scaling_law_peak_results.json"

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
FP_LEN = 20  # fingerprint window length
N_RANDOM_PAIRS = 50000

random.seed(42)
np.random.seed(42)


# ---------------------------------------------------------------------------
# Load OEIS
# ---------------------------------------------------------------------------
def load_oeis():
    """Load OEIS sequences into {id: terms_list}."""
    cache = {}
    src = OEIS_STRIPPED_TXT if OEIS_STRIPPED_TXT.exists() else OEIS_STRIPPED_GZ
    if not src.exists():
        print(f"  WARNING: {src} not found")
        return cache
    opener = gzip.open if str(src).endswith('.gz') else open
    mode = "rt" if str(src).endswith('.gz') else "r"
    print(f"  Loading OEIS from {src.name}...")
    with opener(src, mode, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) < 3:
                continue
            sid = parts[0].strip()
            terms = []
            for t in parts[1:]:
                t = t.strip()
                if t:
                    try:
                        terms.append(int(t))
                    except ValueError:
                        pass
            if terms:
                cache[sid] = terms
    print(f"  Loaded {len(cache):,} sequences")
    return cache


# ---------------------------------------------------------------------------
# Load families from C11 (primary) or C08 (fallback)
# ---------------------------------------------------------------------------
def load_families_c11(oeis_data):
    """Load C11 all_cluster_results as families."""
    if not C11_RESULTS.exists():
        return {}
    with open(C11_RESULTS, "r") as f:
        c11 = json.load(f)
    clusters = c11.get("all_cluster_results", [])
    families = {}
    for cluster in clusters:
        if not isinstance(cluster, dict):
            continue
        poly_str = cluster.get("char_poly_str", "")
        seq_ids = cluster.get("fungrim_direct_refs", [])
        seq_ids = [s for s in seq_ids if isinstance(s, str) and s in oeis_data
                   and len(oeis_data[s]) >= FP_LEN]
        if len(seq_ids) >= 2:
            families[poly_str] = seq_ids
    return families


def load_families_c08(oeis_data):
    """Load C08 polynomial_clusters as families."""
    if not C08_RESULTS.exists():
        return {}
    with open(C08_RESULTS, "r") as f:
        c08 = json.load(f)
    top_clusters = c08.get("polynomial_clusters", {}).get("top_clusters", [])
    families = {}
    for cluster in top_clusters:
        if not isinstance(cluster, dict):
            continue
        coeffs = cluster.get("char_poly_coeffs", [])
        seq_ids = cluster.get("sequences", [])
        poly_str = str(coeffs)
        seq_ids = [s for s in seq_ids if isinstance(s, str) and s in oeis_data
                   and len(oeis_data[s]) >= FP_LEN]
        if len(seq_ids) >= 2:
            families[poly_str] = seq_ids
    return families


def load_families(oeis_data):
    """Load families: try C11 first (2,246 clusters), fall back to C08 (173)."""
    families = load_families_c11(oeis_data)
    source = "C11"
    if not families:
        families = load_families_c08(oeis_data)
        source = "C08"
    if not families:
        print("  WARNING: No families loaded from either C11 or C08")
        return {}, "none"
    n_seqs = sum(len(v) for v in families.values())
    print(f"  Loaded {len(families)} families ({n_seqs} sequences) from {source}")
    return families, source


# ---------------------------------------------------------------------------
# Fingerprint computation
# ---------------------------------------------------------------------------
def fingerprint(terms, p, start=0):
    """Compute mod-p fingerprint of terms[start:start+FP_LEN]."""
    window = terms[start:start + FP_LEN]
    if len(window) < FP_LEN:
        return None
    return tuple(t % p for t in window)


def compute_exact_match_rate(families, oeis_data, p):
    """Compute fraction of within-family pairs sharing exact mod-p fingerprint."""
    matches = 0
    total = 0
    for poly, seq_ids in families.items():
        fps = {}
        for sid in seq_ids:
            fp = fingerprint(oeis_data[sid], p)
            if fp is not None:
                fps[sid] = fp
        sids = list(fps.keys())
        for i in range(len(sids)):
            for j in range(i + 1, len(sids)):
                total += 1
                if fps[sids[i]] == fps[sids[j]]:
                    matches += 1
    return matches / total if total > 0 else 0, total


def compute_random_match_rate(oeis_data, p, n_pairs=N_RANDOM_PAIRS):
    """Compute exact match rate for random pairs."""
    all_ids = [s for s in oeis_data if len(oeis_data[s]) >= FP_LEN]
    matches = 0
    tested = 0
    for _ in range(n_pairs):
        a, b = random.sample(all_ids, 2)
        fp_a = fingerprint(oeis_data[a], p)
        fp_b = fingerprint(oeis_data[b], p)
        if fp_a is not None and fp_b is not None:
            tested += 1
            if fp_a == fp_b:
                matches += 1
    return matches / tested if tested > 0 else 0, tested


def enrichment_ratio(family_rate, random_rate):
    """Compute enrichment, avoiding division by zero."""
    if random_rate == 0:
        return float('inf') if family_rate > 0 else 1.0
    return family_rate / random_rate


def smoothed_enrichment(family_rate, random_rate, n_random_pairs):
    """Laplace-smoothed enrichment: adds 1 pseudo-match to random baseline.
    This avoids infinity and gives a conservative lower bound."""
    smoothed_rate = (random_rate * n_random_pairs + 1) / (n_random_pairs + 1)
    if smoothed_rate == 0:
        return float('inf') if family_rate > 0 else 1.0
    return family_rate / smoothed_rate


def detrend_primes(terms):
    """Remove factors of 2,3,5,7,11,13 from each term."""
    out = []
    for t in terms:
        if t == 0:
            out.append(0)
            continue
        v = abs(t)
        for p in [2, 3, 5, 7, 11, 13]:
            while v % p == 0 and v > 0:
                v //= p
        out.append(v * (1 if t > 0 else -1))
    return out


# ---------------------------------------------------------------------------
# Model fitting
# ---------------------------------------------------------------------------
def power_law(p, A, alpha):
    return A * np.power(p, alpha)


def logistic(p, E_max, k, p_half):
    return E_max / (1.0 + np.exp(-k * (p - p_half)))


def gaussian_peak(p, A, B, p_peak):
    return A * np.exp(-B * (p - p_peak) ** 2)


def compute_aic_bic(n, k_params, rss):
    """AIC and BIC from residual sum of squares."""
    if rss <= 0 or n <= k_params:
        return float('inf'), float('inf')
    log_lik = -n / 2 * (np.log(2 * np.pi * rss / n) + 1)
    aic = 2 * k_params - 2 * log_lik
    bic = k_params * np.log(n) - 2 * log_lik
    return float(aic), float(bic)


def fit_models(primes_arr, enrichments_arr):
    """Fit power law, logistic, and Gaussian peak models. Return dict of results."""
    results = {}
    n = len(primes_arr)
    p = primes_arr.astype(float)
    e = enrichments_arr.astype(float)

    # Filter out infinities
    mask = np.isfinite(e)
    if mask.sum() < 3:
        return {"note": "insufficient finite data points"}
    p_fin = p[mask]
    e_fin = e[mask]
    n_fin = len(p_fin)

    # 1) Power law: E(p) = A * p^alpha
    try:
        popt, _ = curve_fit(power_law, p_fin, e_fin, p0=[1.0, 1.0], maxfev=10000)
        pred = power_law(p_fin, *popt)
        rss = float(np.sum((e_fin - pred) ** 2))
        r2 = 1.0 - rss / np.sum((e_fin - np.mean(e_fin)) ** 2)
        aic, bic = compute_aic_bic(n_fin, 2, rss)
        results["power_law"] = {
            "A": float(popt[0]), "alpha": float(popt[1]),
            "r_squared": float(r2), "rss": rss,
            "aic": aic, "bic": bic,
            "predicted": [float(x) for x in power_law(p, *popt)]
        }
    except Exception as ex:
        results["power_law"] = {"error": str(ex)}

    # 2) Logistic: E(p) = E_max / (1 + exp(-k*(p - p_half)))
    try:
        popt, _ = curve_fit(logistic, p_fin, e_fin,
                            p0=[max(e_fin) * 2, 0.3, 15.0],
                            maxfev=10000, bounds=([0, 0, 0], [1e6, 10, 50]))
        pred = logistic(p_fin, *popt)
        rss = float(np.sum((e_fin - pred) ** 2))
        r2 = 1.0 - rss / np.sum((e_fin - np.mean(e_fin)) ** 2)
        aic, bic = compute_aic_bic(n_fin, 3, rss)
        results["logistic"] = {
            "E_max": float(popt[0]), "k": float(popt[1]), "p_half": float(popt[2]),
            "r_squared": float(r2), "rss": rss,
            "aic": aic, "bic": bic,
            "predicted": [float(x) for x in logistic(p, *popt)]
        }
    except Exception as ex:
        results["logistic"] = {"error": str(ex)}

    # 3) Gaussian peak: E(p) = A * exp(-B * (p - p_peak)^2)
    try:
        idx_max = np.argmax(e_fin)
        popt, _ = curve_fit(gaussian_peak, p_fin, e_fin,
                            p0=[max(e_fin), 0.01, p_fin[idx_max]],
                            maxfev=10000, bounds=([0, 0, 0], [1e6, 1, 50]))
        pred = gaussian_peak(p_fin, *popt)
        rss = float(np.sum((e_fin - pred) ** 2))
        r2 = 1.0 - rss / np.sum((e_fin - np.mean(e_fin)) ** 2)
        aic, bic = compute_aic_bic(n_fin, 3, rss)
        results["gaussian_peak"] = {
            "A": float(popt[0]), "B": float(popt[1]), "p_peak": float(popt[2]),
            "r_squared": float(r2), "rss": rss,
            "aic": aic, "bic": bic,
            "predicted": [float(x) for x in gaussian_peak(p, *popt)]
        }
    except Exception as ex:
        results["gaussian_peak"] = {"error": str(ex)}

    # Best model by AIC
    valid = {k: v for k, v in results.items() if "aic" in v}
    if valid:
        best = min(valid, key=lambda k: valid[k]["aic"])
        results["best_model"] = best
        results["best_aic"] = valid[best]["aic"]
    return results


# ---------------------------------------------------------------------------
# Main computation
# ---------------------------------------------------------------------------
def run_peak_analysis(families, oeis_data, family_source):
    results = {
        "challenge": "R3-3",
        "title": "Scaling Law Peak Prime — Enrichment Curve to p=31",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "family_source": family_source,
        "n_families": len(families),
        "n_sequences": sum(len(v) for v in families.values()),
        "primes_tested": PRIMES,
        "fp_length": FP_LEN,
        "random_pairs": N_RANDOM_PAIRS,
    }

    # ===================================================================
    # 1. RAW ENRICHMENT CURVE
    # ===================================================================
    print("\n=== RAW ENRICHMENT CURVE ===")
    raw_curve = {}
    for p in PRIMES:
        fam_rate, fam_n = compute_exact_match_rate(families, oeis_data, p)
        rand_rate, rand_n = compute_random_match_rate(oeis_data, p)
        ratio = enrichment_ratio(fam_rate, rand_rate)
        smooth_ratio = smoothed_enrichment(fam_rate, rand_rate, rand_n)
        raw_curve[str(p)] = {
            "family_rate": fam_rate, "random_rate": rand_rate,
            "enrichment": ratio, "smoothed_enrichment": smooth_ratio,
            "family_pairs": fam_n, "random_pairs": rand_n
        }
        sym = "inf" if ratio == float('inf') else f"{ratio:.1f}x"
        smooth_sym = f"{smooth_ratio:.1f}x"
        print(f"  mod {p:2d}: family={fam_rate:.6f} random={rand_rate:.6f} "
              f"enrichment={sym} (smoothed={smooth_sym})")
    results["raw_curve"] = raw_curve

    # ===================================================================
    # 2. DETRENDED ENRICHMENT CURVE
    # ===================================================================
    print("\n=== DETRENDED ENRICHMENT CURVE ===")
    detrended = {sid: detrend_primes(terms) for sid, terms in oeis_data.items()}
    detrended_curve = {}
    for p in PRIMES:
        fam_rate, fam_n = compute_exact_match_rate(families, detrended, p)
        rand_rate, rand_n = compute_random_match_rate(detrended, p)
        ratio = enrichment_ratio(fam_rate, rand_rate)
        detrended_curve[str(p)] = {
            "family_rate": fam_rate, "random_rate": rand_rate,
            "enrichment": ratio, "family_pairs": fam_n, "random_pairs": rand_n
        }
        sym = "inf" if ratio == float('inf') else f"{ratio:.1f}x"
        print(f"  mod {p:2d}: family={fam_rate:.6f} random={rand_rate:.6f} enrichment={sym}")
    results["detrended_curve"] = detrended_curve
    del detrended

    # ===================================================================
    # 3. MODEL FITTING — RAW CURVE
    # ===================================================================
    print("\n=== MODEL FITTING (RAW — smoothed enrichment) ===")
    primes_arr = np.array(PRIMES)
    raw_enrichments_smooth = np.array([raw_curve[str(p)]["smoothed_enrichment"] for p in PRIMES])
    raw_models = fit_models(primes_arr, raw_enrichments_smooth)
    for name in ["power_law", "logistic", "gaussian_peak"]:
        if name in raw_models and "r_squared" in raw_models[name]:
            m = raw_models[name]
            print(f"  {name}: R²={m['r_squared']:.4f}  AIC={m['aic']:.1f}  BIC={m['bic']:.1f}")
            if name == "power_law":
                print(f"    E(p) = {m['A']:.3f} * p^{m['alpha']:.3f}")
            elif name == "logistic":
                print(f"    E_max={m['E_max']:.1f}  k={m['k']:.4f}  p_half={m['p_half']:.1f}")
            elif name == "gaussian_peak":
                print(f"    A={m['A']:.1f}  B={m['B']:.6f}  p_peak={m['p_peak']:.1f}")
        elif name in raw_models:
            print(f"  {name}: {raw_models[name]}")
    if "best_model" in raw_models:
        print(f"  Best model: {raw_models['best_model']} (AIC={raw_models['best_aic']:.1f})")
    results["raw_model_fits"] = raw_models

    # ===================================================================
    # 4. MODEL FITTING — DETRENDED CURVE
    # ===================================================================
    print("\n=== MODEL FITTING (DETRENDED) ===")
    det_enrichments = np.array([detrended_curve[str(p)]["enrichment"] for p in PRIMES])
    det_models = fit_models(primes_arr, det_enrichments)
    for name in ["power_law", "logistic", "gaussian_peak"]:
        if name in det_models and "r_squared" in det_models[name]:
            m = det_models[name]
            print(f"  {name}: R²={m['r_squared']:.4f}  AIC={m['aic']:.1f}  BIC={m['bic']:.1f}")
        elif name in det_models:
            print(f"  {name}: {det_models[name]}")
    if "best_model" in det_models:
        print(f"  Best model: {det_models['best_model']} (AIC={det_models['best_aic']:.1f})")
    results["detrended_model_fits"] = det_models

    # Detrended slope analysis
    det_finite = [(p, detrended_curve[str(p)]["enrichment"]) for p in PRIMES
                  if np.isfinite(detrended_curve[str(p)]["enrichment"])]
    if len(det_finite) >= 3:
        det_p = np.array([x[0] for x in det_finite])
        det_e = np.array([x[1] for x in det_finite])
        slope, intercept = np.polyfit(det_p, det_e, 1)
        r2_linear = 1.0 - np.sum((det_e - (slope * det_p + intercept)) ** 2) / np.sum(
            (det_e - np.mean(det_e)) ** 2)
        peak_p_det = int(det_p[np.argmax(det_e)])
        results["detrended_slope_analysis"] = {
            "linear_slope": float(slope),
            "linear_intercept": float(intercept),
            "linear_r_squared": float(r2_linear),
            "is_flat": abs(slope) < 0.5,  # enrichment change < 0.5x per prime unit
            "peak_prime": peak_p_det,
            "min_enrichment": float(np.min(det_e)),
            "max_enrichment": float(np.max(det_e)),
            "mean_enrichment": float(np.mean(det_e)),
            "std_enrichment": float(np.std(det_e)),
        }
        print(f"\n  Detrended slope: {slope:.4f} per prime unit "
              f"({'FLAT' if abs(slope) < 0.5 else 'SLOPED'})")
        print(f"  Peak prime (detrended): p={peak_p_det}")
        print(f"  Range: {np.min(det_e):.1f}x — {np.max(det_e):.1f}x "
              f"(mean={np.mean(det_e):.1f}x, std={np.std(det_e):.1f})")

    # ===================================================================
    # 5. FAMILY-SPECIFIC CURVES (top 5 largest families)
    # ===================================================================
    print("\n=== FAMILY-SPECIFIC ENRICHMENT CURVES ===")
    sorted_families = sorted(families.items(), key=lambda x: len(x[1]), reverse=True)
    top5 = sorted_families[:5]

    family_curves = {}
    for poly_str, seq_ids in top5:
        single_fam = {poly_str: seq_ids}
        fam_curve = {}
        print(f"\n  Family: {poly_str[:60]}... ({len(seq_ids)} seqs)")
        for p in PRIMES:
            fam_rate, fam_n = compute_exact_match_rate(single_fam, oeis_data, p)
            rand_rate = raw_curve[str(p)]["random_rate"]  # reuse global baseline
            ratio = enrichment_ratio(fam_rate, rand_rate)
            fam_curve[str(p)] = {
                "family_rate": fam_rate, "enrichment": ratio, "pairs": fam_n
            }
            sym = "inf" if ratio == float('inf') else f"{ratio:.1f}x"
            print(f"    mod {p:2d}: rate={fam_rate:.6f} enrichment={sym}")

        # Find peak prime for this family
        finite_entries = [(int(k), v["enrichment"]) for k, v in fam_curve.items()
                         if np.isfinite(v["enrichment"])]
        if finite_entries:
            peak_p = max(finite_entries, key=lambda x: x[1])[0]
        else:
            peak_p = None

        family_curves[poly_str] = {
            "n_sequences": len(seq_ids),
            "curve": fam_curve,
            "peak_prime": peak_p,
            "sample_seqs": seq_ids[:5],
        }
        print(f"    Peak prime: p={peak_p}")

    results["family_specific_curves"] = family_curves

    # ===================================================================
    # 6. OVERALL PEAK ANALYSIS
    # ===================================================================
    print("\n" + "=" * 60)
    print("  PEAK PRIME ANALYSIS SUMMARY")
    print("=" * 60)

    # Raw curve peak (use smoothed to avoid inf)
    raw_finite = [(p, raw_curve[str(p)]["smoothed_enrichment"]) for p in PRIMES
                  if np.isfinite(raw_curve[str(p)]["smoothed_enrichment"])]
    if raw_finite:
        raw_peak = max(raw_finite, key=lambda x: x[1])
        # Check if still monotonically increasing (infinite at larger primes)
        raw_all_e = [raw_curve[str(p)]["smoothed_enrichment"] for p in PRIMES]
        # Check monotonicity on smoothed values
        monotone_finite = all(raw_all_e[i] <= raw_all_e[i + 1]
                             for i in range(len(raw_all_e) - 1)
                             if np.isfinite(raw_all_e[i]) and np.isfinite(raw_all_e[i + 1]))
        # Check if family rates are still declining (signal fading)
        fam_rates = [raw_curve[str(p)]["family_rate"] for p in PRIMES]
        family_rate_declining = all(fam_rates[i] >= fam_rates[i + 1]
                                    for i in range(len(fam_rates) - 1))
        any_inf_after = any(not np.isfinite(raw_curve[str(p)]["enrichment"]) for p in PRIMES)
    else:
        raw_peak = (None, None)
        any_inf_after = True
        monotone_finite = True

    results["peak_analysis"] = {
        "raw_peak_prime_smoothed": raw_peak[0],
        "raw_peak_enrichment_smoothed": raw_peak[1],
        "raw_smoothed_monotone": monotone_finite,
        "family_rate_monotone_declining": family_rate_declining,
        "family_peak_primes": {poly: info["peak_prime"]
                               for poly, info in family_curves.items()},
        "families_agree_on_peak": len(set(
            info["peak_prime"] for info in family_curves.values()
            if info["peak_prime"] is not None)) == 1,
    }

    print(f"  Raw curve (smoothed): peak enrichment at p={raw_peak[0]} ({raw_peak[1]:.1f}x)"
          if raw_peak[1] else "  Raw curve: all infinite")
    print(f"  Raw smoothed monotone increasing: {monotone_finite}")
    print(f"  Family rate monotone declining: {family_rate_declining}")
    print(f"  Family peak primes: {results['peak_analysis']['family_peak_primes']}")
    if not results['peak_analysis']['families_agree_on_peak']:
        print("  ** Different families peak at DIFFERENT primes — "
              "peak prime is a family invariant! **")
    else:
        print("  All families share the same peak prime.")

    # Interpretation
    interp = []
    if monotone_finite:
        interp.append("Smoothed raw enrichment is monotonically increasing to p=31; "
                      "no peak detected in raw curve.")
        interp.append("Family match rate declines with p (sparser fingerprints), "
                      "but random baseline declines faster — signal persists.")
    else:
        # Find peak in smoothed
        smooth_vals = [(p, raw_curve[str(p)]["smoothed_enrichment"]) for p in PRIMES]
        peak_raw_p = max(smooth_vals, key=lambda x: x[1])[0]
        interp.append(f"Smoothed raw enrichment peaks at p={peak_raw_p}, "
                      f"then declines — there IS a peak prime in the raw curve.")
    if "detrended_slope_analysis" in results:
        dsa = results["detrended_slope_analysis"]
        if dsa["is_flat"]:
            interp.append(f"Detrended curve is FLAT (slope={dsa['linear_slope']:.4f}): "
                         f"after removing shared prime factors, the residual enrichment "
                         f"is a constant ~{dsa['mean_enrichment']:.1f}x across all primes.")
            interp.append("The raw scaling law is ENTIRELY driven by prime factor sharing; "
                         "the algebraic signal itself has no prime-dependent structure.")
        else:
            interp.append(f"Detrended curve has slope={dsa['linear_slope']:.4f}: "
                         f"there IS prime-dependent structure beyond shared factors.")
            interp.append(f"Detrended peak at p={dsa['peak_prime']}.")
    if not results["peak_analysis"]["families_agree_on_peak"]:
        interp.append("Different families peak at different primes — the peak prime "
                      "is a new algebraic invariant, likely related to Galois image size "
                      "or the largest prime dividing the discriminant/conductor.")
    results["interpretation"] = interp
    for line in interp:
        print(f"  {line}")

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    t0 = time.time()
    print("Scaling Law Peak Prime — R3-3")
    print("=" * 60)

    oeis_data = load_oeis()
    families, source = load_families(oeis_data)

    if not families:
        print("FATAL: No families loaded. Exiting.")
        sys.exit(1)

    results = run_peak_analysis(families, oeis_data, source)

    # Serialize, handling inf/nan
    def json_safe(obj):
        if isinstance(obj, float):
            if math.isinf(obj):
                return "Infinity" if obj > 0 else "-Infinity"
            if math.isnan(obj):
                return "NaN"
        return obj

    class SafeEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, (np.integer,)):
                return int(o)
            if isinstance(o, (np.floating,)):
                v = float(o)
                if math.isinf(v) or math.isnan(v):
                    return str(v)
                return v
            if isinstance(o, np.ndarray):
                return o.tolist()
            return super().default(o)

    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2, cls=SafeEncoder, default=str)
    print(f"\nResults saved to {OUT_FILE}")
    print(f"Total time: {time.time() - t0:.1f}s")
