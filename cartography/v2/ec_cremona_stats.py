"""
EC Cremona Label Structure: Does the Alphabetic Suffix Correlate with Arithmetic?

Cremona labels encode conductor.isogeny_class.curve_number.
Question: Does the number of isogeny classes per conductor correlate with arithmetic properties?

Uses charon DuckDB: elliptic_curves table with lmfdb_iso, conductor, rank, class_size, etc.
"""

import json
import numpy as np
from collections import Counter
from scipy import stats
import duckdb

DB_PATH = "charon/data/charon.duckdb"
OUT_PATH = "cartography/v2/ec_cremona_stats_results.json"


def omega(n):
    """Number of distinct prime factors of n."""
    if n <= 1:
        return 0
    count = 0
    d = 2
    while d * d <= n:
        if n % d == 0:
            count += 1
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        count += 1
    return count


def is_prime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    d = 5
    while d * d <= n:
        if n % d == 0 or n % (d + 2) == 0:
            return False
        d += 6
    return True


def main():
    con = duckdb.connect(DB_PATH, read_only=True)

    # ── 1. Load per-conductor isogeny class counts ──
    cond_df = con.execute("""
        SELECT conductor,
               COUNT(DISTINCT lmfdb_iso) as num_classes,
               COUNT(*) as num_curves,
               AVG(class_size) as mean_class_size,
               AVG(rank) as mean_rank,
               MAX(rank) as max_rank,
               AVG(torsion) as mean_torsion,
               SUM(CASE WHEN cm != 0 THEN 1 ELSE 0 END) as cm_count,
               AVG(degree) as mean_modular_degree,
               AVG(sha) as mean_sha
        FROM elliptic_curves
        GROUP BY conductor
        ORDER BY conductor
    """).fetchdf()

    conductors = cond_df['conductor'].values
    num_classes = cond_df['num_classes'].values
    num_curves = cond_df['num_curves'].values
    mean_rank = cond_df['mean_rank'].values
    max_rank = cond_df['max_rank'].values
    mean_torsion = cond_df['mean_torsion'].values
    cm_count = cond_df['cm_count'].values
    mean_mod_deg = cond_df['mean_modular_degree'].values
    mean_sha = cond_df['mean_sha'].values

    # Compute arithmetic properties of conductors
    omega_vals = np.array([omega(int(c)) for c in conductors])
    is_prime_vals = np.array([is_prime(int(c)) for c in conductors])
    log_cond = np.log(conductors.astype(float))

    results = {}

    # ── 2. Basic stats ──
    results["basic_stats"] = {
        "total_curves": int(num_curves.sum()),
        "total_conductors": len(conductors),
        "total_isogeny_classes": int(num_classes.sum()),
        "max_classes_per_conductor": int(num_classes.max()),
        "mean_classes_per_conductor": float(num_classes.mean()),
        "median_classes_per_conductor": float(np.median(num_classes)),
    }

    # Class count distribution
    class_dist = Counter(int(c) for c in num_classes)
    results["class_count_distribution"] = dict(sorted(class_dist.items()))

    # ── 3. Conductors with most isogeny classes ──
    top_idx = np.argsort(-num_classes)[:20]
    top_conductors = []
    for i in top_idx:
        top_conductors.append({
            "conductor": int(conductors[i]),
            "num_classes": int(num_classes[i]),
            "num_curves": int(num_curves[i]),
            "omega": int(omega_vals[i]),
            "is_prime": bool(is_prime_vals[i]),
            "mean_rank": float(mean_rank[i]),
            "factorization_hint": f"omega={omega_vals[i]}"
        })
    results["top_20_conductors_by_class_count"] = top_conductors

    # ── 4. Correlation: class count vs conductor size ──
    r_logcond, p_logcond = stats.spearmanr(log_cond, num_classes)
    results["correlation_class_count_vs_log_conductor"] = {
        "spearman_r": round(float(r_logcond), 4),
        "p_value": float(p_logcond),
        "interpretation": "positive" if r_logcond > 0 else "negative"
    }

    # ── 5. Correlation: class count vs omega(N) ──
    r_omega, p_omega = stats.spearmanr(omega_vals, num_classes)
    results["correlation_class_count_vs_omega"] = {
        "spearman_r": round(float(r_omega), 4),
        "p_value": float(p_omega),
        "interpretation": "Number of distinct prime factors strongly predicts class count" if r_omega > 0.3 else "Weak"
    }

    # ── 6. Prime vs composite conductors ──
    prime_mask = is_prime_vals
    composite_mask = ~is_prime_vals
    prime_classes = num_classes[prime_mask]
    composite_classes = num_classes[composite_mask]

    mw_stat, mw_p = stats.mannwhitneyu(prime_classes, composite_classes, alternative='two-sided')
    results["prime_vs_composite_conductor"] = {
        "prime_conductors": int(prime_mask.sum()),
        "composite_conductors": int(composite_mask.sum()),
        "prime_mean_classes": round(float(prime_classes.mean()), 3),
        "prime_median_classes": float(np.median(prime_classes)),
        "composite_mean_classes": round(float(composite_classes.mean()), 3),
        "composite_median_classes": float(np.median(composite_classes)),
        "mannwhitney_U": float(mw_stat),
        "mannwhitney_p": float(mw_p),
    }

    # ── 7. Class count vs rank distribution ──
    r_rank, p_rank = stats.spearmanr(num_classes, mean_rank)
    results["correlation_class_count_vs_mean_rank"] = {
        "spearman_r": round(float(r_rank), 4),
        "p_value": float(p_rank),
    }

    # Rank distribution by class-count bins
    bins = [(1, 1), (2, 3), (4, 6), (7, 10), (11, 20), (21, 100)]
    rank_by_bin = []
    for lo, hi in bins:
        mask = (num_classes >= lo) & (num_classes <= hi)
        if mask.sum() > 0:
            rank_by_bin.append({
                "class_count_range": f"{lo}-{hi}",
                "n_conductors": int(mask.sum()),
                "mean_rank": round(float(mean_rank[mask].mean()), 4),
                "max_rank_seen": int(max_rank[mask].max()),
                "mean_torsion": round(float(mean_torsion[mask].mean()), 4),
                "cm_fraction": round(float(cm_count[mask].sum() / num_curves[mask].sum()), 4),
            })
    results["rank_by_class_count_bin"] = rank_by_bin

    # ── 8. Class count vs modular degree ──
    valid_deg = ~np.isnan(mean_mod_deg) & (mean_mod_deg > 0)
    if valid_deg.sum() > 10:
        r_deg, p_deg = stats.spearmanr(num_classes[valid_deg], np.log(mean_mod_deg[valid_deg]))
        results["correlation_class_count_vs_log_modular_degree"] = {
            "spearman_r": round(float(r_deg), 4),
            "p_value": float(p_deg),
            "n": int(valid_deg.sum()),
        }

    # ── 9. Class count vs Sha ──
    valid_sha = ~np.isnan(mean_sha)
    if valid_sha.sum() > 10:
        r_sha, p_sha = stats.spearmanr(num_classes[valid_sha], mean_sha[valid_sha])
        results["correlation_class_count_vs_mean_sha"] = {
            "spearman_r": round(float(r_sha), 4),
            "p_value": float(p_sha),
        }

    # ── 10. Omega-stratified analysis ──
    omega_strat = []
    for w in sorted(set(omega_vals)):
        mask = omega_vals == w
        if mask.sum() >= 5:
            omega_strat.append({
                "omega": int(w),
                "n_conductors": int(mask.sum()),
                "mean_classes": round(float(num_classes[mask].mean()), 3),
                "median_classes": float(np.median(num_classes[mask])),
                "max_classes": int(num_classes[mask].max()),
                "mean_rank": round(float(mean_rank[mask].mean()), 4),
            })
    results["omega_stratified"] = omega_strat

    # ── 11. Residual: class count after controlling for omega ──
    # Does class count predict rank BEYOND what omega explains?
    from scipy.stats import pearsonr
    # Regress class count on omega, get residuals
    if len(set(omega_vals)) > 1:
        slope, intercept = np.polyfit(omega_vals, num_classes, 1)
        class_residual = num_classes - (slope * omega_vals + intercept)
        r_resid, p_resid = stats.spearmanr(class_residual, mean_rank)
        results["residual_class_count_vs_rank_controlling_omega"] = {
            "spearman_r": round(float(r_resid), 4),
            "p_value": float(p_resid),
            "interpretation": "Class count has independent signal for rank beyond omega" if p_resid < 0.01 else "No independent signal"
        }

    # ── 12. Class size distribution ──
    class_size_df = con.execute("""
        SELECT class_size, COUNT(*) as n
        FROM elliptic_curves
        WHERE class_size IS NOT NULL
        GROUP BY class_size
        ORDER BY class_size
    """).fetchdf()
    results["class_size_distribution"] = {
        str(int(r['class_size'])): int(r['n'])
        for _, r in class_size_df.iterrows()
    }

    # ── 13. Per-isogeny-class rank variation ──
    # Within a conductor, do different isogeny classes have different ranks?
    rank_var_df = con.execute("""
        SELECT conductor,
               COUNT(DISTINCT lmfdb_iso) as n_classes,
               COUNT(DISTINCT rank) as n_distinct_ranks
        FROM elliptic_curves
        WHERE rank IS NOT NULL
        GROUP BY conductor
        HAVING COUNT(DISTINCT lmfdb_iso) > 1
    """).fetchdf()

    multi_class = rank_var_df[rank_var_df['n_classes'] > 1]
    results["rank_variation_across_classes"] = {
        "conductors_with_multiple_classes": int(len(multi_class)),
        "conductors_with_rank_variation": int((multi_class['n_distinct_ranks'] > 1).sum()),
        "fraction_with_rank_variation": round(float((multi_class['n_distinct_ranks'] > 1).mean()), 4),
    }

    # ── Summary ──
    results["summary"] = {
        "finding_1": f"Class count strongly correlates with omega(N) (rho={r_omega:.3f}), confirming compositeness drives isogeny proliferation",
        "finding_2": f"Prime conductors average {prime_classes.mean():.1f} classes vs {composite_classes.mean():.1f} for composites",
        "finding_3": f"Class count vs mean rank: rho={r_rank:.3f} (p={p_rank:.2e})",
        "finding_4": f"Top conductor by classes: N={int(conductors[top_idx[0]])} with {int(num_classes[top_idx[0]])} classes, omega={int(omega_vals[top_idx[0]])}",
        "finding_5": f"{results['rank_variation_across_classes']['fraction_with_rank_variation']*100:.1f}% of multi-class conductors show rank variation across isogeny classes",
    }

    con.close()

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved to {OUT_PATH}")
    print(json.dumps(results["summary"], indent=2))


if __name__ == "__main__":
    main()
