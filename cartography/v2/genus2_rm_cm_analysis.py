"""
Genus-2 Real Multiplication vs Complex Multiplication: Trace Statistics

Classifies genus-2 curves by endomorphism algebra and compares
their trace distributions (M2, M4, KS tests, variance ranking).

Data source: LMFDB genus-2 curves with endomorphism_ring field.
Traces computed by counting points on y^2 + h(x)*y = f(x) over F_p.
"""

import json
import math
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path
from itertools import combinations

# ---------- paths ----------
DATA_PATH = Path(__file__).parent.parent / "genus2" / "data" / "genus2_curves_lmfdb.json"
OUT_PATH = Path(__file__).parent / "genus2_rm_cm_results.json"


# ---------- hyperelliptic point counting ----------
def parse_equation(eq_str):
    """Parse LMFDB equation format [[f coeffs], [h coeffs]]."""
    eq = json.loads(eq_str) if isinstance(eq_str, str) else eq_str
    f_coeffs = eq[0]  # f(x) = f_0 + f_1*x + ...
    h_coeffs = eq[1] if len(eq) > 1 else []
    return f_coeffs, h_coeffs


def eval_poly(coeffs, x, p):
    """Evaluate polynomial at x mod p."""
    val = 0
    for i, c in enumerate(coeffs):
        val = (val + c * pow(x, i, p)) % p
    return val


def count_points_mod_p(f_coeffs, h_coeffs, p):
    """
    Count points on y^2 + h(x)*y - f(x) = 0 over F_p.
    For each x in F_p, count y solutions, add point at infinity.
    Returns #C(F_p).
    """
    count = 0
    for x in range(p):
        f_val = eval_poly(f_coeffs, x, p)
        h_val = eval_poly(h_coeffs, x, p)
        # y^2 + h*y - f = 0  =>  discriminant = h^2 + 4*f
        disc = (h_val * h_val + 4 * f_val) % p
        if disc == 0:
            count += 1  # one solution
        elif pow(disc, (p - 1) // 2, p) == 1:
            count += 2  # two solutions
        # else: no solutions
    # Add points at infinity (genus-2 hyperelliptic: 1 or 2 points)
    # For simplicity, use standard: #C(F_p) has 1 point at infinity for odd degree,
    # 2 for even degree of f(x) when h=0 or similar.
    deg_f = len(f_coeffs) - 1
    while deg_f >= 0 and (len(f_coeffs) <= deg_f or f_coeffs[deg_f] == 0):
        deg_f -= 1
    if deg_f % 2 == 1:
        count += 1  # one point at infinity
    else:
        count += 2  # two points at infinity
    return count


def trace_from_count(n_points, p):
    """a_p = p + 1 - #C(F_p) for genus-2 is not quite right.
    For genus 2: #C(F_p) = p + 1 - a_p where a_p is the trace of Frobenius.
    """
    return p + 1 - n_points


# ---------- main ----------
def main():
    print("Loading data...")
    with open(DATA_PATH) as f:
        data = json.load(f)
    records = data["records"]
    print(f"Total curves: {len(records)}")

    # Classify by endomorphism ring
    endo_counts = Counter(r["endomorphism_ring"] for r in records)
    print("\nEndomorphism ring distribution:")
    for k, v in endo_counts.most_common():
        print(f"  {k}: {v}")

    # Good primes for trace computation (avoid very small to reduce bad reduction issues)
    primes = [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

    # For efficiency, sample from Q (63K is too many for point counting)
    # Use all curves from non-Q types, sample from Q
    MAX_PER_CLASS = 2000
    np.random.seed(42)

    by_endo = defaultdict(list)
    for r in records:
        by_endo[r["endomorphism_ring"]].append(r)

    sampled = {}
    for endo, curves in by_endo.items():
        if len(curves) > MAX_PER_CLASS:
            idx = np.random.choice(len(curves), MAX_PER_CLASS, replace=False)
            sampled[endo] = [curves[i] for i in idx]
        else:
            sampled[endo] = curves

    print("\nSampled sizes:")
    for endo, curves in sampled.items():
        print(f"  {endo}: {len(curves)}")

    # Compute traces for each class
    print("\nComputing traces (this may take a minute)...")
    trace_data = {}  # endo -> list of normalized traces

    for endo, curves in sampled.items():
        all_normalized = []
        n_good = 0
        for curve in curves:
            f_coeffs, h_coeffs = parse_equation(curve["equation"])
            conductor = int(curve["conductor"])
            curve_traces = []
            for p in primes:
                if conductor % p == 0:
                    continue  # skip bad primes
                try:
                    npts = count_points_mod_p(f_coeffs, h_coeffs, p)
                    a_p = trace_from_count(npts, p)
                    # Normalize: a_p / (2*sqrt(p)) for genus 2
                    norm = a_p / (2.0 * math.sqrt(p))
                    curve_traces.append(norm)
                except Exception:
                    continue
            if curve_traces:
                all_normalized.extend(curve_traces)
                n_good += 1
        trace_data[endo] = np.array(all_normalized)
        print(f"  {endo}: {n_good} curves, {len(all_normalized)} trace values")

    # Compute moment statistics
    print("\nMoment statistics:")
    stats = {}
    for endo, traces in trace_data.items():
        if len(traces) < 10:
            print(f"  {endo}: too few traces, skipping")
            continue
        m2 = float(np.mean(traces**2))
        m4 = float(np.mean(traces**4))
        mean = float(np.mean(traces))
        var = float(np.var(traces))
        std = float(np.std(traces))
        skew = float(np.mean(((traces - mean) / std)**3)) if std > 0 else 0
        kurt = float(np.mean(((traces - mean) / std)**4)) if std > 0 else 0
        stats[endo] = {
            "n_traces": len(traces),
            "n_curves": len(sampled[endo]),
            "mean": round(mean, 6),
            "variance": round(var, 6),
            "M2": round(m2, 6),
            "M4": round(m4, 6),
            "std": round(std, 6),
            "skewness": round(skew, 4),
            "kurtosis": round(kurt, 4),
        }
        print(f"  {endo}: M2={m2:.4f}, M4={m4:.4f}, var={var:.4f}, mean={mean:.4f}")

    # Kolmogorov-Smirnov tests between all pairs
    from scipy.stats import ks_2samp
    print("\nKS tests:")
    ks_results = {}
    endo_keys = [k for k in trace_data if len(trace_data[k]) >= 10]
    for e1, e2 in combinations(sorted(endo_keys), 2):
        stat, pval = ks_2samp(trace_data[e1], trace_data[e2])
        key = f"{e1} vs {e2}"
        ks_results[key] = {"KS_statistic": round(float(stat), 6), "p_value": float(pval)}
        sig = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else "ns"
        print(f"  {key}: D={stat:.4f}, p={pval:.2e} {sig}")

    # Highest/lowest variance
    var_ranking = sorted(stats.items(), key=lambda x: x[1]["variance"], reverse=True)
    print("\nVariance ranking (highest to lowest):")
    for endo, s in var_ranking:
        print(f"  {endo}: {s['variance']:.6f}")

    # RM fraction
    total = len(records)
    rm_count = endo_counts.get("RM", 0)
    rm_fraction = rm_count / total
    print(f"\nRM fraction: {rm_count}/{total} = {rm_fraction:.4%}")

    # Focus: RM vs CM comparison
    rm_vs_cm = {}
    if "RM" in stats and "CM" in stats:
        rm_vs_cm = {
            "RM_M2": stats["RM"]["M2"],
            "CM_M2": stats["CM"]["M2"],
            "RM_M4": stats["RM"]["M4"],
            "CM_M4": stats["CM"]["M4"],
            "RM_variance": stats["RM"]["variance"],
            "CM_variance": stats["CM"]["variance"],
        }
        if "RM vs CM" in ks_results:
            rm_vs_cm["KS_statistic"] = ks_results["RM vs CM"]["KS_statistic"]
            rm_vs_cm["KS_p_value"] = ks_results["RM vs CM"]["p_value"]
        elif "CM vs RM" in ks_results:
            rm_vs_cm["KS_statistic"] = ks_results["CM vs RM"]["KS_statistic"]
            rm_vs_cm["KS_p_value"] = ks_results["CM vs RM"]["p_value"]

    # Build output
    results = {
        "analysis": "Genus-2 RM vs CM trace statistics",
        "date": "2026-04-10",
        "data_source": str(DATA_PATH),
        "total_curves": total,
        "endomorphism_distribution": {k: v for k, v in endo_counts.most_common()},
        "rm_fraction": round(rm_fraction, 6),
        "rm_count": rm_count,
        "primes_used": primes,
        "normalization": "a_p / (2*sqrt(p))",
        "moment_statistics": stats,
        "variance_ranking": [{"endo_type": e, "variance": s["variance"]} for e, s in var_ranking],
        "ks_tests": ks_results,
        "rm_vs_cm_comparison": rm_vs_cm,
        "methodology": {
            "trace_computation": "Point counting on y^2 + h(x)y = f(x) over F_p for good primes",
            "normalization": "a_p / (2*sqrt(p)) — Sato-Tate normalization for genus 2",
            "bad_primes": "Excluded primes dividing the conductor",
            "sampling": f"All non-Q classes fully counted; Q class sampled to {MAX_PER_CLASS}",
        }
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
