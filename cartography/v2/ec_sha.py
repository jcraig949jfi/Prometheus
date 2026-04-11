"""EC Analytic Sha Distribution by Rank — Prometheus cartography v2."""
import json
import numpy as np
import duckdb

DB = "charon/data/charon.duckdb"
OUT = "cartography/v2/ec_sha_results.json"

con = duckdb.connect(DB, read_only=True)

results = {"title": "EC Analytic Sha Distribution by Rank", "n_curves": 0}

# --- 1. Basic counts ---
n = con.execute("SELECT COUNT(*) FROM elliptic_curves WHERE sha IS NOT NULL").fetchone()[0]
results["n_curves"] = int(n)

# --- 2. Sha distribution by rank ---
rows = con.execute("""
    SELECT rank, sha, COUNT(*) as c
    FROM elliptic_curves WHERE sha IS NOT NULL
    GROUP BY rank, sha ORDER BY rank, sha
""").fetchall()

sha_by_rank = {}
for rank, sha, c in rows:
    sha_by_rank.setdefault(int(rank), {})[int(sha)] = int(c)
results["sha_by_rank"] = sha_by_rank

# --- 3. Fraction with sha > 1, > 4, > 9 ---
for threshold in [1, 4, 9]:
    row = con.execute(f"""
        SELECT COUNT(*) FILTER (WHERE sha > {threshold}),
               COUNT(*),
               COUNT(*) FILTER (WHERE sha > {threshold}) * 1.0 / COUNT(*)
        FROM elliptic_curves WHERE sha IS NOT NULL
    """).fetchone()
    results[f"frac_sha_gt_{threshold}"] = {
        "count": int(row[0]), "total": int(row[1]),
        "fraction": round(float(row[2]), 6)
    }

# By rank
for threshold in [1, 4, 9]:
    rows = con.execute(f"""
        SELECT rank,
               COUNT(*) FILTER (WHERE sha > {threshold}),
               COUNT(*),
               COUNT(*) FILTER (WHERE sha > {threshold}) * 1.0 / COUNT(*)
        FROM elliptic_curves WHERE sha IS NOT NULL
        GROUP BY rank ORDER BY rank
    """).fetchall()
    results[f"frac_sha_gt_{threshold}_by_rank"] = {
        int(r[0]): {"count": int(r[1]), "total": int(r[2]), "fraction": round(float(r[3]), 6)}
        for r in rows
    }

# --- 4. Sha across conductor ranges ---
rows = con.execute("""
    SELECT
        CASE
            WHEN conductor < 1000 THEN '<1K'
            WHEN conductor < 10000 THEN '1K-10K'
            WHEN conductor < 100000 THEN '10K-100K'
            ELSE '100K+'
        END as cond_bin,
        AVG(sha) as mean_sha,
        MEDIAN(sha) as median_sha,
        MAX(sha) as max_sha,
        COUNT(*) as n,
        COUNT(*) FILTER (WHERE sha > 1) as n_nontrivial,
        COUNT(*) FILTER (WHERE sha > 1) * 1.0 / COUNT(*) as frac_nontrivial
    FROM elliptic_curves WHERE sha IS NOT NULL
    GROUP BY cond_bin
    ORDER BY MIN(conductor)
""").fetchall()

results["sha_by_conductor_bin"] = {
    r[0]: {
        "mean_sha": round(float(r[1]), 4),
        "median_sha": float(r[2]),
        "max_sha": int(r[3]),
        "n_curves": int(r[4]),
        "n_nontrivial": int(r[5]),
        "frac_nontrivial": round(float(r[6]), 6)
    } for r in rows
}

# --- 5. Correlations: sha vs conductor, regulator, Tamagawa ---
# Sha vs conductor (Spearman)
df = con.execute("""
    SELECT sha, conductor, regulator FROM elliptic_curves
    WHERE sha IS NOT NULL AND regulator IS NOT NULL
""").fetchnumpy()

from scipy import stats

sha_arr = df['sha'].astype(float)
cond_arr = df['conductor'].astype(float)
reg_arr = df['regulator'].astype(float)

rho_cond, p_cond = stats.spearmanr(sha_arr, cond_arr)
rho_reg, p_reg = stats.spearmanr(sha_arr, reg_arr)

results["correlations"] = {
    "sha_vs_conductor": {"spearman_rho": round(float(rho_cond), 6), "p_value": float(p_cond)},
    "sha_vs_regulator": {"spearman_rho": round(float(rho_reg), 6), "p_value": float(p_reg)},
}

# Sha vs Tamagawa: need to compute from bad_primes or check if stored
# The DB doesn't have tamagawa directly; check if we can compute from isogeny info
# Try: product of local Tamagawa numbers. Not in this table, but degree may proxy.
# Skip if not available.

# --- 6. Sha by rank: mean and std ---
rows = con.execute("""
    SELECT rank, AVG(sha), STDDEV_SAMP(sha), MIN(sha), MAX(sha), COUNT(*)
    FROM elliptic_curves WHERE sha IS NOT NULL
    GROUP BY rank ORDER BY rank
""").fetchall()

results["sha_stats_by_rank"] = {
    int(r[0]): {
        "mean": round(float(r[1]), 4),
        "std": round(float(r[2]), 4) if r[2] is not None else None,
        "min": int(r[3]),
        "max": int(r[4]),
        "n": int(r[5])
    } for r in rows
}

# --- 7. Perfect square verification ---
sha_vals = con.execute("SELECT DISTINCT sha FROM elliptic_curves WHERE sha IS NOT NULL ORDER BY sha").fetchall()
all_perfect_squares = all(int(s[0]**0.5 + 0.5)**2 == s[0] for s in sha_vals)
results["all_sha_perfect_squares"] = all_perfect_squares
results["distinct_sha_values"] = sorted([int(s[0]) for s in sha_vals])

# --- 8. Sha distribution conditioned on rank 0 vs rank >= 1 ---
for rk_label, rk_cond in [("rank_0", "rank = 0"), ("rank_ge1", "rank >= 1")]:
    rows = con.execute(f"""
        SELECT sha, COUNT(*) as c FROM elliptic_curves
        WHERE sha IS NOT NULL AND {rk_cond}
        GROUP BY sha ORDER BY sha
    """).fetchall()
    total = sum(r[1] for r in rows)
    results[f"sha_dist_{rk_label}"] = {
        int(r[0]): {"count": int(r[1]), "fraction": round(r[1]/total, 6)}
        for r in rows
    }

# --- Summary ---
print(f"Total curves: {results['n_curves']}")
print(f"Distinct sha values: {results['distinct_sha_values']}")
print(f"All perfect squares: {results['all_sha_perfect_squares']}")
print(f"\nFraction sha > 1: {results['frac_sha_gt_1']['fraction']:.4f} ({results['frac_sha_gt_1']['count']}/{results['frac_sha_gt_1']['total']})")
print(f"Fraction sha > 4: {results['frac_sha_gt_4']['fraction']:.4f} ({results['frac_sha_gt_4']['count']}/{results['frac_sha_gt_4']['total']})")
print(f"Fraction sha > 9: {results['frac_sha_gt_9']['fraction']:.4f} ({results['frac_sha_gt_9']['count']}/{results['frac_sha_gt_9']['total']})")
print(f"\nSha stats by rank:")
for rk, s in results["sha_stats_by_rank"].items():
    print(f"  rank {rk}: mean={s['mean']:.3f}, std={s['std']:.3f}, max={s['max']}, n={s['n']}")
print(f"\nCorrelations:")
print(f"  sha vs conductor: rho={rho_cond:.4f}, p={p_cond:.2e}")
print(f"  sha vs regulator: rho={rho_reg:.4f}, p={p_reg:.2e}")
print(f"\nSha by conductor bin:")
for b, v in results["sha_by_conductor_bin"].items():
    print(f"  {b}: mean={v['mean_sha']:.3f}, frac_nontrivial={v['frac_nontrivial']:.4f}, n={v['n_curves']}")

con.close()

with open(OUT, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {OUT}")
