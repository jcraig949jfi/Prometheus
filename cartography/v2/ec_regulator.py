"""EC Regulator Distribution by Rank — Prometheus cartography v2."""

import json
import numpy as np
from scipy import stats
import duckdb

DB = "charon/data/charon.duckdb"
OUT = "cartography/v2/ec_regulator_results.json"

con = duckdb.connect(DB, read_only=True)

# Load data
df = con.execute("""
    SELECT rank, regulator, conductor
    FROM elliptic_curves
    WHERE regulator IS NOT NULL AND rank IS NOT NULL
    ORDER BY rank, regulator
""").fetchdf()
con.close()

results = {"metadata": {"source": "charon.duckdb/elliptic_curves", "n_total": len(df)}}

# Per-rank statistics
for r in sorted(df["rank"].unique()):
    sub = df[df["rank"] == r]
    regs = sub["regulator"].values
    conds = sub["conductor"].values

    entry = {
        "n": int(len(regs)),
        "mean": float(np.mean(regs)),
        "median": float(np.median(regs)),
        "std": float(np.std(regs)),
        "min": float(np.min(regs)),
        "max": float(np.max(regs)),
        "q25": float(np.percentile(regs, 25)),
        "q75": float(np.percentile(regs, 75)),
    }

    if r == 0:
        entry["note"] = "R=1 by convention for rank 0"
    else:
        # Distribution of log(regulator) — test normality (log-normal hypothesis)
        pos = regs[regs > 0]
        log_regs = np.log(pos)
        entry["log_reg_mean"] = float(np.mean(log_regs))
        entry["log_reg_std"] = float(np.std(log_regs))

        # Shapiro-Wilk on log(reg) — sample if too large
        sample = log_regs if len(log_regs) <= 5000 else np.random.default_rng(42).choice(log_regs, 5000, replace=False)
        sw_stat, sw_p = stats.shapiro(sample)
        entry["shapiro_wilk_log_reg"] = {"statistic": float(sw_stat), "p_value": float(sw_p)}

        # KS test against log-normal
        ks_stat, ks_p = stats.kstest(pos, "lognorm", args=stats.lognorm.fit(pos))
        entry["ks_lognormal"] = {"statistic": float(ks_stat), "p_value": float(ks_p)}

        # Power-law: fit on complementary CDF (crude)
        sorted_reg = np.sort(pos)[::-1]
        log_x = np.log(sorted_reg)
        log_rank = np.log(np.arange(1, len(sorted_reg) + 1))
        slope, intercept, r_val, _, _ = stats.linregress(log_x, log_rank)
        entry["power_law_fit"] = {"slope": float(slope), "r_squared": float(r_val**2)}

        # Correlation: regulator vs conductor
        if len(pos) > 10:
            mask = regs > 0
            r_cond, p_cond = stats.spearmanr(regs[mask], conds[mask])
            entry["spearman_reg_vs_conductor"] = {"rho": float(r_cond), "p_value": float(p_cond)}

            # Log-log correlation
            r_ll, p_ll = stats.spearmanr(np.log(regs[mask]), np.log(conds[mask]))
            entry["spearman_log_reg_vs_log_cond"] = {"rho": float(r_ll), "p_value": float(p_ll)}

        # Percentile table
        entry["percentiles"] = {str(p): float(np.percentile(regs, p)) for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]}

    results[f"rank_{r}"] = entry

# Summary
print("=== EC Regulator Distribution by Rank ===")
for r in sorted(df["rank"].unique()):
    e = results[f"rank_{r}"]
    print(f"\nRank {r} (n={e['n']}):")
    print(f"  mean={e['mean']:.4f}  median={e['median']:.4f}  std={e['std']:.4f}")
    print(f"  range=[{e['min']:.6f}, {e['max']:.4f}]")
    if r > 0:
        sw = e["shapiro_wilk_log_reg"]
        ks = e["ks_lognormal"]
        pl = e["power_law_fit"]
        sc = e.get("spearman_reg_vs_conductor", {})
        print(f"  log-normal test: Shapiro p={sw['p_value']:.4g}, KS p={ks['p_value']:.4g}")
        print(f"  power-law slope={pl['slope']:.3f}, R²={pl['r_squared']:.3f}")
        if sc:
            print(f"  reg vs conductor: Spearman rho={sc['rho']:.4f}, p={sc['p_value']:.4g}")

with open(OUT, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {OUT}")
