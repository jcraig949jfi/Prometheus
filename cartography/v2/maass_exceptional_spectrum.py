"""
Maass Exceptional Spectrum — Hunt for Forms with Anomalous Moment Ratios

The population mean M4/M2^2 = 2.018 (GOE prediction ~2.0).
Question: Are there individual forms that deviate significantly?
What characterizes them?

Approach:
  1. Load all forms with >100 prime coefficients
  2. For each: compute M4/M2^2 with bootstrap 95% CI
  3. Identify forms where CI excludes 2.0
  4. Characterize anomalous forms by level, spectral parameter, symmetry, entropy
  5. Top 20 most anomalous
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter
import time

# --- Paths ---
DATA_PATH = Path(__file__).resolve().parent.parent / "maass" / "data" / "maass_with_coefficients.json"
OUT_JSON = Path(__file__).resolve().parent / "maass_exceptional_spectrum_results.json"

# --- Primes sieve ---
def primes_up_to(n):
    sieve = np.ones(n + 1, dtype=bool)
    sieve[:2] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = False
    return np.where(sieve)[0]

PRIMES = primes_up_to(3000)  # enough for coefficient arrays up to ~3000

# --- Core computation ---
def moment_ratio_bootstrap(coeffs_at_primes, n_boot=2000, ci=0.95):
    """Compute M4/M2^2 and bootstrap CI for a single form's prime coefficients."""
    x = np.array(coeffs_at_primes, dtype=np.float64)
    n = len(x)
    if n < 30:
        return None, None, None, None

    m2 = np.mean(x**2)
    m4 = np.mean(x**4)
    ratio = m4 / (m2**2) if m2 > 0 else np.nan

    # Bootstrap
    rng = np.random.default_rng(42)
    boot_ratios = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        xb = x[idx]
        m2b = np.mean(xb**2)
        m4b = np.mean(xb**4)
        boot_ratios[b] = m4b / (m2b**2) if m2b > 0 else np.nan

    alpha = (1 - ci) / 2
    lo = np.nanpercentile(boot_ratios, 100 * alpha)
    hi = np.nanpercentile(boot_ratios, 100 * (1 - alpha))
    return ratio, lo, hi, n


def shannon_entropy(coeffs):
    """Normalized Shannon entropy of |coefficients| histogram."""
    x = np.abs(np.array(coeffs))
    if len(x) < 10:
        return np.nan
    hist, _ = np.histogram(x, bins=30, density=True)
    hist = hist[hist > 0]
    h = -np.sum(hist * np.log(hist + 1e-15)) * (x.max() - x.min()) / 30
    return h / np.log(30)  # normalize to [0,1]


def main():
    print("Loading data...")
    with open(DATA_PATH) as f:
        data = json.load(f)
    print(f"  {len(data)} forms loaded")

    MIN_PRIME_COEFFS = 100
    results = []
    skipped = 0
    t0 = time.time()

    for i, form in enumerate(data):
        coeffs = form.get("coefficients", [])
        n_coeffs = len(coeffs)

        # Extract prime-indexed coefficients (1-indexed: coeffs[0]=a(1), coeffs[p-1]=a(p))
        prime_coeffs = []
        for p in PRIMES:
            idx = p - 1  # coefficients are 1-indexed
            if idx < n_coeffs:
                prime_coeffs.append(coeffs[idx])
            else:
                break

        if len(prime_coeffs) < MIN_PRIME_COEFFS:
            skipped += 1
            continue

        ratio, lo, hi, n_primes = moment_ratio_bootstrap(prime_coeffs)
        if ratio is None:
            skipped += 1
            continue

        # Is CI excluding 2.0?
        anomalous = (lo > 2.0) or (hi < 2.0)
        deviation = ratio - 2.0
        # Distance of nearest CI bound from 2.0 (signed)
        if lo > 2.0:
            ci_gap = lo - 2.0  # positive = above
        elif hi < 2.0:
            ci_gap = hi - 2.0  # negative = below
        else:
            ci_gap = 0.0

        ent = shannon_entropy(prime_coeffs)

        rec = {
            "maass_id": form["maass_id"],
            "level": form.get("level"),
            "spectral_parameter": form.get("spectral_parameter"),
            "symmetry": form.get("symmetry"),
            "weight": form.get("weight"),
            "conrey_index": form.get("conrey_index"),
            "fricke_eigenvalue": form.get("fricke_eigenvalue"),
            "n_prime_coeffs": n_primes,
            "M4_M2sq": round(ratio, 6),
            "ci_lo": round(lo, 6),
            "ci_hi": round(hi, 6),
            "anomalous": anomalous,
            "deviation": round(deviation, 6),
            "ci_gap": round(ci_gap, 6),
            "entropy": round(ent, 6),
        }
        results.append(rec)

        if (i + 1) % 3000 == 0:
            elapsed = time.time() - t0
            print(f"  processed {i+1}/{len(data)} ({elapsed:.1f}s)")

    elapsed = time.time() - t0
    print(f"  Done: {len(results)} forms analyzed, {skipped} skipped, {elapsed:.1f}s")

    # --- Analysis ---
    ratios = np.array([r["M4_M2sq"] for r in results])
    anomalous_forms = [r for r in results if r["anomalous"]]
    anomalous_above = [r for r in anomalous_forms if r["ci_gap"] > 0]
    anomalous_below = [r for r in anomalous_forms if r["ci_gap"] < 0]

    print(f"\n=== RESULTS ===")
    print(f"Total forms analyzed: {len(results)}")
    print(f"Population M4/M2^2: mean={np.mean(ratios):.4f}, median={np.median(ratios):.4f}, std={np.std(ratios):.4f}")
    print(f"Anomalous (CI excludes 2.0): {len(anomalous_forms)} ({100*len(anomalous_forms)/len(results):.1f}%)")
    print(f"  Above 2.0: {len(anomalous_above)}")
    print(f"  Below 2.0: {len(anomalous_below)}")

    # Characterize anomalous vs normal
    normal_forms = [r for r in results if not r["anomalous"]]

    def stats_of(subset, key):
        vals = []
        for r in subset:
            v = r[key]
            if v is not None:
                try:
                    vals.append(float(v))
                except (ValueError, TypeError):
                    pass
        if not vals:
            return {"mean": None, "median": None, "std": None}
        return {"mean": round(np.mean(vals), 4), "median": round(np.median(vals), 4), "std": round(np.std(vals), 4)}

    print(f"\n--- Characterization ---")
    for key in ["level", "spectral_parameter", "entropy"]:
        a_stats = stats_of(anomalous_forms, key)
        n_stats = stats_of(normal_forms, key)
        print(f"  {key}:")
        print(f"    anomalous: mean={a_stats['mean']}, median={a_stats['median']}, std={a_stats['std']}")
        print(f"    normal:    mean={n_stats['mean']}, median={n_stats['median']}, std={n_stats['std']}")

    # Symmetry breakdown
    anom_sym = Counter(r["symmetry"] for r in anomalous_forms)
    norm_sym = Counter(r["symmetry"] for r in normal_forms)
    print(f"\n  Symmetry distribution:")
    print(f"    anomalous: {dict(anom_sym)}")
    print(f"    normal:    {dict(norm_sym)}")

    # Level distribution for anomalous
    anom_levels = Counter(r["level"] for r in anomalous_forms)
    print(f"\n  Top 10 levels among anomalous: {anom_levels.most_common(10)}")

    # Top 20 most anomalous (by |ci_gap|)
    top20 = sorted(anomalous_forms, key=lambda r: abs(r["ci_gap"]), reverse=True)[:20]
    print(f"\n--- Top 20 Most Anomalous ---")
    for i, r in enumerate(top20):
        direction = "ABOVE" if r["ci_gap"] > 0 else "BELOW"
        print(f"  {i+1}. {r['maass_id']} level={r['level']} R={float(r['spectral_parameter']):.6f} "
              f"sym={r['symmetry']} ratio={r['M4_M2sq']:.4f} CI=[{r['ci_lo']:.4f},{r['ci_hi']:.4f}] "
              f"gap={r['ci_gap']:.4f} {direction} ent={r['entropy']:.4f}")

    # Oldform-like check: forms with high ratio AND low entropy might be CM-like
    high_ratio_low_ent = [r for r in anomalous_above if r["entropy"] < stats_of(results, "entropy")["median"]]
    print(f"\n  Anomalous-above with below-median entropy (CM-like candidates): {len(high_ratio_low_ent)}")

    # --- Save ---
    summary = {
        "metadata": {
            "description": "Maass Exceptional Spectrum: individual forms with anomalous M4/M2^2",
            "date": "2026-04-11",
            "n_forms_analyzed": len(results),
            "n_skipped": skipped,
            "min_prime_coeffs": MIN_PRIME_COEFFS,
            "n_bootstrap": 2000,
            "ci_level": 0.95,
            "population_mean_ratio": round(float(np.mean(ratios)), 6),
            "population_median_ratio": round(float(np.median(ratios)), 6),
            "population_std_ratio": round(float(np.std(ratios)), 6),
        },
        "anomalous_summary": {
            "n_anomalous": len(anomalous_forms),
            "fraction": round(len(anomalous_forms) / len(results), 4),
            "n_above_2": len(anomalous_above),
            "n_below_2": len(anomalous_below),
            "anomalous_vs_normal_level": {
                "anomalous": stats_of(anomalous_forms, "level"),
                "normal": stats_of(normal_forms, "level"),
            },
            "anomalous_vs_normal_spectral": {
                "anomalous": stats_of(anomalous_forms, "spectral_parameter"),
                "normal": stats_of(normal_forms, "spectral_parameter"),
            },
            "anomalous_vs_normal_entropy": {
                "anomalous": stats_of(anomalous_forms, "entropy"),
                "normal": stats_of(normal_forms, "entropy"),
            },
            "symmetry_distribution": {
                "anomalous": dict(anom_sym),
                "normal": dict(norm_sym),
            },
            "top_levels_anomalous": anom_levels.most_common(20),
            "cm_like_candidates": len(high_ratio_low_ent),
        },
        "top_20_anomalous": top20,
        "all_anomalous": anomalous_forms,
    }

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.bool_,)):
                return bool(obj)
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    with open(OUT_JSON, "w") as f:
        json.dump(summary, f, indent=2, cls=NumpyEncoder)
    print(f"\nSaved to {OUT_JSON}")


if __name__ == "__main__":
    main()
