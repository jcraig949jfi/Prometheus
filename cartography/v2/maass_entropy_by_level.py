#!/usr/bin/env python3
"""
Maass Coefficient Entropy by Level — Does Level Affect Randomness?

For each Maass form, compute Shannon entropy of the binned coefficient
distribution (50 bins on [-2, 2]).  Group by level and symmetry; test
whether entropy is level-independent and correlate with spectral parameter R.
"""

import json, pathlib, sys
import numpy as np
from collections import defaultdict
from scipy import stats as sp_stats

# ── paths ───────────────────────────────────────────────────────────────
DATA   = pathlib.Path("F:/Prometheus/cartography/maass/data/maass_with_coefficients.json")
OUT    = pathlib.Path("F:/Prometheus/cartography/v2/maass_entropy_by_level_results.json")

# ── helpers ─────────────────────────────────────────────────────────────
NBINS = 50
BIN_RANGE = (-2.0, 2.0)

def shannon_entropy(coefficients):
    """Shannon entropy (bits) of coefficient histogram, 50 bins on [-2,2]."""
    arr = np.asarray(coefficients, dtype=np.float64)
    # clip to range so outliers land in edge bins
    arr = np.clip(arr, BIN_RANGE[0], BIN_RANGE[1])
    counts, _ = np.histogram(arr, bins=NBINS, range=BIN_RANGE)
    # normalise
    p = counts / counts.sum()
    p = p[p > 0]
    return -np.sum(p * np.log2(p))


# ── load data ───────────────────────────────────────────────────────────
print(f"Loading {DATA} ...")
with open(DATA) as f:
    forms = json.load(f)
print(f"  {len(forms)} Maass forms loaded.")

# ── per-form entropy ────────────────────────────────────────────────────
records = []
for fm in forms:
    coeffs = fm["coefficients"]
    if len(coeffs) < 20:
        continue
    h = shannon_entropy(coeffs)
    records.append({
        "maass_id":   fm["maass_id"],
        "level":      fm["level"],
        "symmetry":   fm["symmetry"],       # +1 even, -1 odd
        "R":          fm["spectral_parameter"],
        "n_coeffs":   len(coeffs),
        "entropy":    round(h, 6),
    })

print(f"  {len(records)} forms with valid entropy.")

# numpy arrays for vectorised work
levels    = np.array([r["level"]    for r in records])
symmetry  = np.array([r["symmetry"] for r in records])
R_vals    = np.array([r["R"]        for r in records], dtype=float)
entropies = np.array([r["entropy"]  for r in records])

# ── 1. Global statistics ────────────────────────────────────────────────
global_mean = float(np.mean(entropies))
global_std  = float(np.std(entropies))
global_med  = float(np.median(entropies))
print(f"\nGlobal entropy: mean={global_mean:.4f} ± {global_std:.4f}  median={global_med:.4f} bits")

# ── 2. Group by level ──────────────────────────────────────────────────
by_level = defaultdict(list)
for r in records:
    by_level[r["level"]].append(r["entropy"])

level_stats = {}
for lv in sorted(by_level):
    vals = np.array(by_level[lv])
    level_stats[int(lv)] = {
        "count":   len(vals),
        "mean":    round(float(np.mean(vals)), 6),
        "std":     round(float(np.std(vals)), 6),
        "min":     round(float(np.min(vals)), 6),
        "max":     round(float(np.max(vals)), 6),
    }

unique_levels = sorted(level_stats.keys())
print(f"  {len(unique_levels)} distinct levels (range {unique_levels[0]}–{unique_levels[-1]})")

# level-independence test: one-way ANOVA across levels with >= 5 forms
groups_for_anova = [np.array(by_level[lv]) for lv in unique_levels if len(by_level[lv]) >= 5]
if len(groups_for_anova) >= 2:
    F_stat, anova_p = sp_stats.f_oneway(*groups_for_anova)
else:
    F_stat, anova_p = float("nan"), float("nan")
print(f"  ANOVA (levels with n>=5): F={F_stat:.4f}, p={anova_p:.4e}")

# also Kruskal-Wallis (non-parametric)
if len(groups_for_anova) >= 2:
    kw_stat, kw_p = sp_stats.kruskal(*groups_for_anova)
else:
    kw_stat, kw_p = float("nan"), float("nan")
print(f"  Kruskal-Wallis: H={kw_stat:.4f}, p={kw_p:.4e}")

# ── 3. Entropy vs spectral parameter R ─────────────────────────────────
r_corr, r_pval = sp_stats.pearsonr(R_vals, entropies)
rho_corr, rho_pval = sp_stats.spearmanr(R_vals, entropies)
print(f"\nEntropy vs R:  Pearson r={r_corr:.4f} (p={r_pval:.4e}), Spearman rho={rho_corr:.4f} (p={rho_pval:.4e})")

# ── 4. Even vs odd symmetry ────────────────────────────────────────────
even_ent = entropies[symmetry ==  1]
odd_ent  = entropies[symmetry == -1]
if len(even_ent) > 0 and len(odd_ent) > 0:
    sym_t, sym_p = sp_stats.ttest_ind(even_ent, odd_ent)
    mw_stat, mw_p = sp_stats.mannwhitneyu(even_ent, odd_ent, alternative="two-sided")
else:
    sym_t = sym_p = mw_stat = mw_p = float("nan")

print(f"\nEven symmetry: n={len(even_ent)}, mean={np.mean(even_ent):.4f} ± {np.std(even_ent):.4f}")
print(f"Odd  symmetry: n={len(odd_ent)},  mean={np.mean(odd_ent):.4f} ± {np.std(odd_ent):.4f}")
print(f"  t-test: t={sym_t:.4f}, p={sym_p:.4e}")
print(f"  Mann-Whitney: U={mw_stat:.1f}, p={mw_p:.4e}")

# ── 5. Comparison to EC Hecke entropy ──────────────────────────────────
ec_nonCM = 3.84
ec_CM    = 2.45
ec_hecke = 3.27  # approximate universal from prior work
print(f"\nComparison to EC Hecke entropy:")
print(f"  Maass global mean  = {global_mean:.4f} bits")
print(f"  EC non-CM          = {ec_nonCM} bits")
print(f"  EC CM              = {ec_CM} bits")
print(f"  EC Hecke universal = {ec_hecke} bits")

# ── 6. Entropy vs level correlation ────────────────────────────────────
level_corr_r, level_corr_p = sp_stats.pearsonr(levels.astype(float), entropies)
level_corr_rho, level_corr_rho_p = sp_stats.spearmanr(levels.astype(float), entropies)
print(f"\nEntropy vs level: Pearson r={level_corr_r:.4f} (p={level_corr_p:.4e}), Spearman rho={level_corr_rho:.4f} (p={level_corr_rho_p:.4e})")

# ── 7. Top/bottom levels by mean entropy ───────────────────────────────
levels_with_enough = {lv: s for lv, s in level_stats.items() if s["count"] >= 5}
sorted_by_mean = sorted(levels_with_enough.items(), key=lambda x: x[1]["mean"])
top5 = sorted_by_mean[-5:][::-1]
bot5 = sorted_by_mean[:5]
print(f"\nTop 5 levels by mean entropy (n>=5):")
for lv, s in top5:
    print(f"  level={lv}: mean={s['mean']:.4f}, n={s['count']}")
print(f"Bottom 5 levels by mean entropy (n>=5):")
for lv, s in bot5:
    print(f"  level={lv}: mean={s['mean']:.4f}, n={s['count']}")

# ── 8. Entropy distribution by R bands ──────────────────────────────────
R_bands = [(0, 5), (5, 10), (10, 20), (20, 40), (40, 100)]
print(f"\nEntropy by spectral parameter R bands:")
r_band_stats = {}
for lo, hi in R_bands:
    mask = (R_vals >= lo) & (R_vals < hi)
    band_ent = entropies[mask]
    if len(band_ent) > 0:
        label = f"R in [{lo},{hi})"
        r_band_stats[label] = {
            "count": int(len(band_ent)),
            "mean":  round(float(np.mean(band_ent)), 6),
            "std":   round(float(np.std(band_ent)), 6),
        }
        print(f"  {label}: n={len(band_ent)}, mean={np.mean(band_ent):.4f} ± {np.std(band_ent):.4f}")

# ── build results ───────────────────────────────────────────────────────
results = {
    "description": "Maass coefficient entropy by level — does level affect randomness?",
    "n_forms": len(records),
    "n_bins": NBINS,
    "bin_range": list(BIN_RANGE),
    "global_entropy": {
        "mean": round(global_mean, 6),
        "std":  round(global_std, 6),
        "median": round(global_med, 6),
    },
    "level_independence": {
        "n_levels_total": len(unique_levels),
        "n_levels_anova": len(groups_for_anova),
        "anova_F":  round(float(F_stat), 6) if not np.isnan(F_stat) else None,
        "anova_p":  float(anova_p) if not np.isnan(anova_p) else None,
        "kruskal_H": round(float(kw_stat), 6) if not np.isnan(kw_stat) else None,
        "kruskal_p": float(kw_p) if not np.isnan(kw_p) else None,
        "entropy_vs_level_pearson_r": round(float(level_corr_r), 6),
        "entropy_vs_level_pearson_p": float(level_corr_p),
        "entropy_vs_level_spearman_rho": round(float(level_corr_rho), 6),
        "entropy_vs_level_spearman_p": float(level_corr_rho_p),
    },
    "entropy_vs_R": {
        "pearson_r":    round(float(r_corr), 6),
        "pearson_p":    float(r_pval),
        "spearman_rho": round(float(rho_corr), 6),
        "spearman_p":   float(rho_pval),
    },
    "symmetry_comparison": {
        "even_n":    int(len(even_ent)),
        "even_mean": round(float(np.mean(even_ent)), 6) if len(even_ent) > 0 else None,
        "even_std":  round(float(np.std(even_ent)), 6)  if len(even_ent) > 0 else None,
        "odd_n":     int(len(odd_ent)),
        "odd_mean":  round(float(np.mean(odd_ent)), 6)  if len(odd_ent) > 0 else None,
        "odd_std":   round(float(np.std(odd_ent)), 6)   if len(odd_ent) > 0 else None,
        "ttest_t":   round(float(sym_t), 6) if not np.isnan(sym_t) else None,
        "ttest_p":   float(sym_p) if not np.isnan(sym_p) else None,
        "mannwhitney_U": round(float(mw_stat), 2) if not np.isnan(mw_stat) else None,
        "mannwhitney_p": float(mw_p) if not np.isnan(mw_p) else None,
    },
    "ec_comparison": {
        "maass_mean": round(global_mean, 4),
        "ec_nonCM":   ec_nonCM,
        "ec_CM":      ec_CM,
        "ec_hecke":   ec_hecke,
    },
    "r_band_stats": r_band_stats,
    "top5_levels_by_entropy": [{"level": lv, **s} for lv, s in top5],
    "bottom5_levels_by_entropy": [{"level": lv, **s} for lv, s in bot5],
    "level_stats": level_stats,
    "per_form_sample": records[:20],
}

# ── save ────────────────────────────────────────────────────────────────
with open(OUT, "w") as f:
    json.dump(results, f, indent=1)
print(f"\nResults saved to {OUT}")
print("Done.")
