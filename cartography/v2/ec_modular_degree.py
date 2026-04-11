"""
EC Modular Degree Distribution Analysis
========================================
Measures distribution of modular degree deg(φ) for weight-2 newforms.
The modular degree is the degree of the modular parametrization X_0(N) → E.

Key questions:
1. Distribution shape (log-normal vs power law)
2. Scaling with conductor: log(deg) ~ α·log(N)
3. Rank dependence
4. Comparison to theoretical deg ~ N^{1+ε}
"""
import json
import numpy as np
from scipy import stats
import duckdb

DB = "charon/data/charon.duckdb"
OUT = "cartography/v2/ec_modular_degree_results.json"

con = duckdb.connect(DB, read_only=True)

df = con.execute("""
    SELECT conductor, rank, degree, cm, semistable, torsion, class_size
    FROM elliptic_curves
    WHERE degree IS NOT NULL AND degree > 0 AND conductor > 0
""").fetchdf()

results = {"n_curves": len(df)}

# ─── 1. Distribution of log(degree) ───
log_deg = np.log(df["degree"].values.astype(float))

# Test log-normality (on degree itself → normality of log_deg)
shapiro_n = min(5000, len(log_deg))
rng = np.random.default_rng(42)
shapiro_sample = rng.choice(log_deg, shapiro_n, replace=False)
shapiro_stat, shapiro_p = stats.shapiro(shapiro_sample)

# Fit log-normal (= normal on log_deg)
ln_mu, ln_std = np.mean(log_deg), np.std(log_deg)

# Test power law: P(deg > x) ~ x^{-α}. Fit tail exponent via MLE on log_deg
# Power law on degree: log-log CDF. Use simple Hill estimator on top 10%
sorted_deg = np.sort(df["degree"].values.astype(float))
top10_idx = int(0.9 * len(sorted_deg))
x_min = sorted_deg[top10_idx]
tail = sorted_deg[top10_idx:]
hill_alpha = 1.0 / np.mean(np.log(tail / x_min))

# KS test: log-normal vs observed
ks_lognorm, ks_lognorm_p = stats.kstest(log_deg, "norm", args=(ln_mu, ln_std))

results["distribution"] = {
    "log_degree_mean": float(ln_mu),
    "log_degree_std": float(ln_std),
    "median_degree": float(np.median(df["degree"])),
    "shapiro_stat": float(shapiro_stat),
    "shapiro_p": float(shapiro_p),
    "ks_lognormal_stat": float(ks_lognorm),
    "ks_lognormal_p": float(ks_lognorm_p),
    "hill_tail_exponent": float(hill_alpha),
    "hill_x_min": float(x_min),
    "verdict": "log-normal" if ks_lognorm_p > 0.01 else "heavy-tailed (not log-normal)"
}

# ─── 2. Scaling: log(deg) ~ α·log(N) ───
log_N = np.log(df["conductor"].values.astype(float))
slope, intercept, r, p, se = stats.linregress(log_N, log_deg)

results["scaling"] = {
    "alpha": float(slope),
    "intercept": float(intercept),
    "r_squared": float(r**2),
    "p_value": float(p),
    "std_err": float(se),
    "theoretical_expectation": "deg ~ N^{1+epsilon}, so alpha ~ 1",
    "verdict": f"alpha={slope:.4f}, {'consistent' if 0.8 < slope < 1.5 else 'inconsistent'} with deg ~ N^{{1+eps}}"
}

# ─── 2b. Scaling in conductor bins ───
bins = np.percentile(df["conductor"], np.arange(0, 101, 10))
bins = np.unique(bins)
bin_labels = np.digitize(df["conductor"], bins)
bin_stats = []
for b in range(1, len(bins)):
    mask = bin_labels == b
    if mask.sum() < 10:
        continue
    ld = log_deg[mask]
    ln = log_N[mask]
    local_slope, _, local_r, _, _ = stats.linregress(ln, ld)
    bin_stats.append({
        "conductor_range": [float(bins[b-1]), float(bins[b]) if b < len(bins) else float(df["conductor"].max())],
        "n": int(mask.sum()),
        "mean_log_deg": float(np.mean(ld)),
        "local_slope": float(local_slope),
        "local_r_squared": float(local_r**2)
    })
results["scaling_by_bin"] = bin_stats

# ─── 3. Rank dependence ───
rank_stats = []
for r_val in sorted(df["rank"].dropna().unique()):
    mask = df["rank"] == r_val
    degs = df.loc[mask, "degree"].values.astype(float)
    conds = df.loc[mask, "conductor"].values.astype(float)
    if len(degs) < 5:
        continue
    # Fit scaling within rank
    sl, ic, rr, pp, _ = stats.linregress(np.log(conds), np.log(degs))
    rank_stats.append({
        "rank": int(r_val),
        "n": int(mask.sum()),
        "mean_degree": float(np.mean(degs)),
        "median_degree": float(np.median(degs)),
        "mean_log_degree": float(np.mean(np.log(degs))),
        "std_log_degree": float(np.std(np.log(degs))),
        "scaling_alpha": float(sl),
        "scaling_r2": float(rr**2),
    })

# Mann-Whitney: rank 0 vs rank 1 degree (controlling for conductor would be better, but start here)
r0 = df.loc[df["rank"] == 0, "degree"].values.astype(float)
r1 = df.loc[df["rank"] == 1, "degree"].values.astype(float)
mw_stat, mw_p = stats.mannwhitneyu(r0, r1, alternative="two-sided")

# Better test: compare residuals from scaling fit
residuals = log_deg - (slope * log_N + intercept)
r0_resid = residuals[df["rank"].values == 0]
r1_resid = residuals[df["rank"].values == 1]
mw_resid_stat, mw_resid_p = stats.mannwhitneyu(r0_resid, r1_resid, alternative="two-sided")

results["rank_dependence"] = {
    "by_rank": rank_stats,
    "rank0_vs_rank1_raw": {"U": float(mw_stat), "p": float(mw_p)},
    "rank0_vs_rank1_residual": {
        "U": float(mw_resid_stat), "p": float(mw_resid_p),
        "mean_resid_r0": float(np.mean(r0_resid)),
        "mean_resid_r1": float(np.mean(r1_resid)),
        "note": "residuals from log(deg) ~ alpha*log(N) fit, controlling for conductor"
    },
    "verdict": "rank 0 has larger modular degree at fixed conductor" if np.mean(r0_resid) > np.mean(r1_resid) else "rank 1 has larger modular degree at fixed conductor"
}

# ─── 4. CM vs non-CM ───
cm_mask = df["cm"] != 0
if cm_mask.sum() > 10:
    cm_degs = log_deg[cm_mask.values]
    ncm_degs = log_deg[~cm_mask.values]
    cm_resid = residuals[cm_mask.values]
    ncm_resid = residuals[~cm_mask.values]
    cm_mw, cm_p = stats.mannwhitneyu(cm_resid, ncm_resid, alternative="two-sided")
    results["cm_effect"] = {
        "n_cm": int(cm_mask.sum()),
        "n_non_cm": int((~cm_mask).sum()),
        "mean_log_deg_cm": float(np.mean(cm_degs)),
        "mean_log_deg_non_cm": float(np.mean(ncm_degs)),
        "residual_U": float(cm_mw),
        "residual_p": float(cm_p),
    }

# ─── 5. Semistable effect ───
ss_mask = df["semistable"] == True
if ss_mask.sum() > 10:
    ss_resid = residuals[ss_mask.values]
    nss_resid = residuals[~ss_mask.values]
    ss_mw, ss_p = stats.mannwhitneyu(ss_resid, nss_resid, alternative="two-sided")
    results["semistable_effect"] = {
        "n_semistable": int(ss_mask.sum()),
        "mean_resid_semistable": float(np.mean(ss_resid)),
        "mean_resid_non_semistable": float(np.mean(nss_resid)),
        "U": float(ss_mw),
        "p": float(ss_p),
    }

# ─── 6. Percentile table ───
pcts = [1, 5, 10, 25, 50, 75, 90, 95, 99]
results["percentiles"] = {f"p{p}": float(np.percentile(df["degree"], p)) for p in pcts}

# ─── 7. Degree / conductor ratio ───
ratio = df["degree"].values.astype(float) / df["conductor"].values.astype(float)
log_ratio = np.log(ratio)
results["degree_over_conductor"] = {
    "mean": float(np.mean(ratio)),
    "median": float(np.median(ratio)),
    "mean_log_ratio": float(np.mean(log_ratio)),
    "std_log_ratio": float(np.std(log_ratio)),
    "note": "if deg~N^alpha, log(deg/N) ~ (alpha-1)*log(N) + const"
}

# ─── Summary ───
results["summary"] = (
    f"31K curves. Modular degree spans 1 to ~15M. "
    f"Log-normal fit: mu={ln_mu:.2f}, sigma={ln_std:.2f}. "
    f"Scaling: log(deg) ~ {slope:.3f}*log(N), R²={r**2:.3f}. "
    f"Rank 0 curves have {'larger' if np.mean(r0_resid) > np.mean(r1_resid) else 'smaller'} "
    f"modular degree than rank 1 at fixed conductor (p={mw_resid_p:.2e})."
)

with open(OUT, "w") as f:
    json.dump(results, f, indent=2)

print(json.dumps(results, indent=2)[:3000])
con.close()
