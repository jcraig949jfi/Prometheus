"""
CODATA Unitless Constant Galois Group Analysis
================================================
Extract dimensionless CODATA constants, compute continued fraction expansions,
test for periodicity via autocorrelation to infer algebraic degree.

CF of algebraic number of degree d is eventually periodic with period dividing d.
Periodic => algebraic of degree k (the period).
No periodicity => transcendental or high-degree algebraic.
"""

import json
import numpy as np
from pathlib import Path
from decimal import Decimal, getcontext

# High precision for CF computation
getcontext().prec = 50

DATA_DIR = Path(__file__).resolve().parent.parent / "physics" / "data" / "codata"
OUT_DIR = Path(__file__).resolve().parent


def load_dimensionless_constants():
    """Load constants with no unit field (dimensionless)."""
    with open(DATA_DIR / "constants.json") as f:
        data = json.load(f)
    return [c for c in data if "unit" not in c]


def continued_fraction(value, n_terms=30):
    """Compute first n_terms partial quotients of the CF expansion."""
    # Use the raw string value for maximum precision if available
    pqs = []
    x = Decimal(str(value))
    for _ in range(n_terms):
        a = int(x)
        pqs.append(a)
        frac = x - a
        if abs(frac) < Decimal("1e-30"):
            break
        x = Decimal(1) / frac
        if abs(x) > Decimal("1e30"):
            break
    return pqs


def detect_periodicity_autocorr(pqs, min_period=1, max_period=None):
    """
    Detect periodicity in partial quotient sequence using autocorrelation.

    Returns (period, confidence) where confidence is the peak autocorrelation
    at that lag, normalized. period=0 means no periodicity detected.
    """
    if len(pqs) < 6:
        return 0, 0.0

    # Skip the first PQ (integer part) - periodicity is in the fractional tail
    seq = np.array(pqs[1:], dtype=float)
    n = len(seq)
    if max_period is None:
        max_period = n // 2

    if max_period < min_period:
        return 0, 0.0

    # Normalize
    seq_centered = seq - np.mean(seq)
    var = np.var(seq_centered)
    if var < 1e-10:
        # Constant sequence => period 1
        return 1, 1.0

    # Compute autocorrelation at each lag
    autocorrs = []
    for lag in range(min_period, max_period + 1):
        if lag >= n:
            break
        c = np.mean(seq_centered[:n - lag] * seq_centered[lag:]) / var
        autocorrs.append((lag, c))

    if not autocorrs:
        return 0, 0.0

    # Find the lag with highest autocorrelation
    best_lag, best_corr = max(autocorrs, key=lambda x: x[1])

    # Threshold: require reasonably strong autocorrelation
    # For truly periodic sequences, autocorrelation at the period is ~1.0
    # We use 0.5 as threshold for "periodic"
    if best_corr > 0.5:
        return best_lag, float(best_corr)
    return 0, float(best_corr)


def detect_periodicity_exact(pqs):
    """
    Exact periodicity check: does the tail of the CF repeat exactly?
    More stringent than autocorrelation.
    """
    if len(pqs) < 4:
        return 0, False

    # Skip integer part
    tail = pqs[1:]
    n = len(tail)

    for period in range(1, n // 3 + 1):
        # Check if tail[i] == tail[i + period] for all valid i
        # Require at least 2 full repetitions
        matches = 0
        total = 0
        for i in range(n - period):
            total += 1
            if tail[i] == tail[i + period]:
                matches += 1
        if total > 0 and matches == total:
            return period, True

    return 0, False


def classify_constant(pqs, name):
    """Classify a constant based on its CF expansion."""
    # First check exact periodicity
    exact_period, exact_match = detect_periodicity_exact(pqs)

    # Then autocorrelation-based detection
    ac_period, ac_confidence = detect_periodicity_autocorr(pqs)

    # Check if CF terminates early (rational number)
    is_rational = len(pqs) < 30 and (len(pqs) < 3 or
                                       all(pq == 0 for pq in pqs[len(pqs)//2:]))

    if exact_match:
        if exact_period == 1:
            return {
                "classification": "quadratic_irrational",
                "degree": 2,
                "period": exact_period,
                "method": "exact",
                "confidence": 1.0
            }
        return {
            "classification": f"algebraic_degree_{exact_period}",
            "degree": exact_period,
            "period": exact_period,
            "method": "exact",
            "confidence": 1.0
        }

    if ac_period > 0 and ac_confidence > 0.5:
        return {
            "classification": f"possibly_algebraic_degree_{ac_period}",
            "degree": ac_period,
            "period": ac_period,
            "method": "autocorrelation",
            "confidence": round(ac_confidence, 4)
        }

    return {
        "classification": "transcendental_or_high_degree",
        "degree": None,
        "period": None,
        "method": "none",
        "confidence": 0.0
    }


def analyze_cf_statistics(pqs):
    """Compute statistics of the CF expansion."""
    if len(pqs) < 2:
        return {}
    tail = pqs[1:]
    arr = np.array(tail, dtype=float)
    return {
        "mean_pq": round(float(np.mean(arr)), 3),
        "median_pq": round(float(np.median(arr)), 3),
        "max_pq": int(np.max(arr)),
        "std_pq": round(float(np.std(arr)), 3),
        "n_terms": len(pqs),
        "khinchin_ratio": round(float(np.mean(np.log(arr[arr > 0]))) / np.log(2), 4) if np.any(arr > 0) else None
    }


def main():
    constants = load_dimensionless_constants()
    print(f"Loaded {len(constants)} dimensionless CODATA constants")

    results = []
    periodic_count = 0
    period_distribution = {}

    for c in constants:
        name = c["name"]
        value = c["value"]
        uncertainty = c.get("uncertainty", 0)

        pqs = continued_fraction(value, n_terms=30)
        classification = classify_constant(pqs, name)
        stats = analyze_cf_statistics(pqs)

        entry = {
            "name": name,
            "value": value,
            "uncertainty": uncertainty,
            "cf_partial_quotients": pqs,
            "cf_stats": stats,
            **classification
        }
        results.append(entry)

        if classification["period"] is not None:
            periodic_count += 1
            p = classification["period"]
            period_distribution[p] = period_distribution.get(p, 0) + 1

    # Summary statistics
    n_total = len(results)
    periodic_fraction = periodic_count / n_total if n_total > 0 else 0

    # Classify by type
    exact_periodic = [r for r in results if r["method"] == "exact"]
    ac_periodic = [r for r in results if r["method"] == "autocorrelation"]
    non_periodic = [r for r in results if r["method"] == "none"]

    summary = {
        "total_dimensionless": n_total,
        "periodic_count": periodic_count,
        "periodic_fraction": round(periodic_fraction, 4),
        "non_periodic_count": n_total - periodic_count,
        "exact_periodic_count": len(exact_periodic),
        "autocorrelation_periodic_count": len(ac_periodic),
        "period_distribution": {str(k): v for k, v in sorted(period_distribution.items())},
        "classification_breakdown": {
            "transcendental_or_high_degree": len(non_periodic),
            "exact_periodic": len(exact_periodic),
            "autocorrelation_periodic": len(ac_periodic)
        }
    }

    # Print report
    print(f"\n{'='*70}")
    print(f"CODATA Dimensionless Constants — CF Periodicity Analysis")
    print(f"{'='*70}")
    print(f"Total dimensionless constants: {n_total}")
    print(f"Periodic (any method):         {periodic_count} ({periodic_fraction*100:.1f}%)")
    print(f"  Exact periodicity:           {len(exact_periodic)}")
    print(f"  Autocorrelation periodic:    {len(ac_periodic)}")
    print(f"Non-periodic:                  {len(non_periodic)} ({(1-periodic_fraction)*100:.1f}%)")
    print(f"\nPeriod distribution:")
    for k, v in sorted(period_distribution.items()):
        print(f"  period {k}: {v} constants")

    if exact_periodic:
        print(f"\nExact periodic constants:")
        for r in exact_periodic:
            print(f"  {r['name']}: period={r['period']}, CF={r['cf_partial_quotients'][:15]}...")

    if ac_periodic:
        print(f"\nAutocorrelation-detected periodic constants:")
        for r in ac_periodic:
            print(f"  {r['name']}: period={r['period']}, conf={r['confidence']:.3f}")

    # Khinchin analysis: for transcendental numbers, the geometric mean of
    # PQs should approach Khinchin's constant K ≈ 2.6854...
    khinchin_target = 2.6854520010
    khinchin_ratios = []
    for r in non_periodic:
        s = r["cf_stats"]
        if s.get("khinchin_ratio") is not None:
            khinchin_ratios.append(s["khinchin_ratio"])

    if khinchin_ratios:
        mean_kr = np.mean(khinchin_ratios)
        print(f"\nKhinchin analysis (non-periodic constants):")
        print(f"  Mean log-mean/log2 of PQs: {mean_kr:.4f}")
        print(f"  Khinchin's constant (log K / log 2): {np.log(khinchin_target)/np.log(2):.4f}")
        summary["khinchin_analysis"] = {
            "mean_log_ratio": round(float(mean_kr), 4),
            "khinchin_target_log2": round(float(np.log(khinchin_target) / np.log(2)), 4)
        }

    output = {
        "summary": summary,
        "constants": results
    }

    out_path = OUT_DIR / "codata_galois_results.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {out_path}")

    return output


if __name__ == "__main__":
    main()
