"""
EC Naive Height Distribution and Scaling
=========================================
Compute naive height h(E) = max(|a1|^6, |a2|^3, |a3|^2, |a4|^{3/2}, |a6|)
from Weierstrass a-invariants. Analyze scaling with conductor N and rank.
"""

import json
import numpy as np
import duckdb
from scipy import stats
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "charon" / "data" / "charon.duckdb"
OUT_PATH = Path(__file__).resolve().parent / "ec_height_scaling_results.json"


def compute_naive_height(ainvs):
    """h(E) = max(|a1|^6, |a2|^3, |a3|^2, |a4|^{3/2}, |a6|)"""
    a1, a2, a3, a4, a6 = ainvs
    terms = [
        abs(a1) ** 6,
        abs(a2) ** 3,
        abs(a3) ** 2,
        abs(a4) ** 1.5,
        abs(a6),
    ]
    return max(max(terms), 1.0)  # floor at 1 to avoid log(0)


def main():
    con = duckdb.connect(str(DB_PATH), read_only=True)
    rows = con.execute(
        "SELECT conductor, ainvs, rank, faltings_height FROM elliptic_curves"
    ).fetchall()
    con.close()

    conductors, heights, ranks, faltings = [], [], [], []
    for cond, ainv, rk, fh in rows:
        if ainv is None or cond is None or cond <= 0:
            continue
        h = compute_naive_height(ainv)
        conductors.append(cond)
        heights.append(h)
        ranks.append(rk if rk is not None else -1)
        faltings.append(fh)

    N = np.array(conductors, dtype=np.float64)
    H = np.array(heights, dtype=np.float64)
    R = np.array(ranks, dtype=int)
    F = np.array(faltings, dtype=np.float64)

    logN = np.log(N)
    logH = np.log(H)

    # --- 1. Overall scaling: log(h) vs log(N) ---
    slope, intercept, r_value, p_value, std_err = stats.linregress(logN, logH)

    # --- 2. Distribution of log(h) ---
    logh_mean = float(np.mean(logH))
    logh_median = float(np.median(logH))
    logh_std = float(np.std(logH))
    logh_p25 = float(np.percentile(logH, 25))
    logh_p75 = float(np.percentile(logH, 75))

    # --- 3. By rank ---
    rank_results = {}
    for rk in sorted(set(R)):
        mask = R == rk
        if mask.sum() < 10:
            continue
        sl, ic, rv, pv, se = stats.linregress(logN[mask], logH[mask])
        rank_results[int(rk)] = {
            "count": int(mask.sum()),
            "slope": round(sl, 6),
            "intercept": round(ic, 4),
            "r_squared": round(rv ** 2, 6),
            "mean_logH": round(float(np.mean(logH[mask])), 4),
            "median_logH": round(float(np.median(logH[mask])), 4),
        }

    # --- 4. Which a-invariant dominates the height? ---
    dominant_counts = {f"a{i}": 0 for i in [1, 2, 3, 4, 6]}
    for cond, ainv, rk, fh in rows:
        if ainv is None:
            continue
        a1, a2, a3, a4, a6 = ainv
        terms = {
            "a1": abs(a1) ** 6,
            "a2": abs(a2) ** 3,
            "a3": abs(a3) ** 2,
            "a4": abs(a4) ** 1.5,
            "a6": abs(a6),
        }
        winner = max(terms, key=terms.get)
        dominant_counts[winner] += 1

    # --- 5. Faltings height vs naive height correlation ---
    fmask = np.isfinite(F) & (F != 0)
    faltings_corr = float(np.corrcoef(logH[fmask], F[fmask])[0, 1]) if fmask.sum() > 10 else None

    # --- 6. Conductor bins: median height per decade ---
    log10N = np.log10(N)
    bin_edges = np.arange(0, np.ceil(log10N.max()) + 1, 1)
    binned = {}
    for i in range(len(bin_edges) - 1):
        lo, hi = bin_edges[i], bin_edges[i + 1]
        mask = (log10N >= lo) & (log10N < hi)
        if mask.sum() < 5:
            continue
        binned[f"[10^{int(lo)}, 10^{int(hi)})"] = {
            "count": int(mask.sum()),
            "median_logH": round(float(np.median(logH[mask])), 4),
            "mean_logH": round(float(np.mean(logH[mask])), 4),
        }

    results = {
        "description": "Naive height h(E)=max(|a1|^6,|a2|^3,|a3|^2,|a4|^{3/2},|a6|) scaling with conductor",
        "n_curves": len(N),
        "overall_fit": {
            "model": "log(h) = slope * log(N) + intercept",
            "slope": round(slope, 6),
            "intercept": round(intercept, 4),
            "r_squared": round(r_value ** 2, 6),
            "p_value": float(p_value),
            "std_err": round(std_err, 6),
        },
        "log_height_distribution": {
            "mean": round(logh_mean, 4),
            "median": round(logh_median, 4),
            "std": round(logh_std, 4),
            "p25": round(logh_p25, 4),
            "p75": round(logh_p75, 4),
        },
        "by_rank": rank_results,
        "dominant_invariant_counts": dominant_counts,
        "faltings_vs_naive_correlation": round(faltings_corr, 6) if faltings_corr else None,
        "conductor_bins": binned,
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    print(f"Curves analyzed: {len(N)}")
    print(f"\n=== Overall: log(h) vs log(N) ===")
    print(f"  slope = {slope:.4f}, R² = {r_value**2:.4f}")
    print(f"  => h ~ N^{slope:.3f}")
    print(f"\n=== log(h) distribution ===")
    print(f"  mean={logh_mean:.2f}, median={logh_median:.2f}, std={logh_std:.2f}")
    print(f"\n=== By rank ===")
    for rk, d in rank_results.items():
        print(f"  rank {rk}: n={d['count']}, slope={d['slope']:.4f}, R²={d['r_squared']:.4f}, median_logH={d['median_logH']:.2f}")
    print(f"\n=== Dominant invariant ===")
    for k, v in dominant_counts.items():
        print(f"  {k}: {v} ({100*v/len(N):.1f}%)")
    print(f"\n=== Faltings vs naive height correlation: {faltings_corr:.4f}" if faltings_corr else "")
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
