"""
Maass Spectral Gap vs Number Field Regulator Scaling
=====================================================
Tests whether Maass form spectral parameters R correlate with
regulators of totally real quadratic number fields, matched via
|discriminant| = level.

Theory: For totally real fields of degree d, there should be Maass forms
on GL(d) with spectral parameters related to the regulator. For d=2,
the fundamental unit log(epsilon) equals the regulator, and Maass forms
at level N = |disc| should encode this.

Approach:
1. Load 14,995 Maass newforms (LMFDB dump) with spectral_parameter R, level N
2. Load 3,043 totally real degree-2 NF with regulator and |disc|
3. Match: Maass forms at level N <-> degree-2 NF with |disc| = N
4. Correlate: R vs log(regulator) for matched pairs
5. Also: within fixed level, test R distribution vs regulator
6. Extended matching: |disc| within tolerance of N (approximate)
7. Null: 1000 random pairings to establish baseline

Data:
  - cartography/lmfdb_dump/maass_newforms.json (14,995 records)
  - cartography/number_fields/data/number_fields.json (9,116 fields)
"""

import json
import numpy as np
from scipy import stats
from collections import defaultdict
from pathlib import Path

# ── Load data ──────────────────────────────────────────────────────────
MAASS_PATH = Path(__file__).parent.parent / "lmfdb_dump" / "maass_newforms.json"
NF_PATH = Path(__file__).parent.parent / "number_fields" / "data" / "number_fields.json"
OUT_PATH = Path(__file__).parent / "maass_nf_regulator_results.json"

print("Loading Maass newforms...")
with open(MAASS_PATH) as f:
    maass_raw = json.load(f)
maass_records = maass_raw["records"]
print(f"  Loaded {len(maass_records)} Maass newform records")

print("Loading number fields...")
with open(NF_PATH) as f:
    nf_all = json.load(f)
print(f"  Loaded {len(nf_all)} number fields")

# ── Parse Maass forms ────────────────────────────────────────────────
maass_forms = []
for r in maass_records:
    try:
        sp = float(r["spectral_parameter"])
    except (ValueError, TypeError):
        continue
    maass_forms.append({
        "spectral_parameter": sp,
        "level": int(r["level"]),
        "symmetry": int(r["symmetry"]),
    })
print(f"  Parsed {len(maass_forms)} Maass forms with valid spectral parameters")

# Group Maass forms by level
maass_by_level = defaultdict(list)
for f in maass_forms:
    maass_by_level[f["level"]].append(f["spectral_parameter"])

maass_levels = set(maass_by_level.keys())
print(f"  Unique Maass levels: {len(maass_levels)} (range {min(maass_levels)}-{max(maass_levels)})")

# ── Parse totally real degree-2 NF ───────────────────────────────────
nf_deg2_tr = []
for nf in nf_all:
    if nf["degree"] == 2 and nf["disc_sign"] == 1:
        reg = float(nf["regulator"])
        disc = int(nf["disc_abs"])
        nf_deg2_tr.append({
            "label": nf["label"],
            "disc": disc,
            "regulator": reg,
            "log_regulator": float(np.log(reg)) if reg > 0 else None,
            "class_number": int(nf["class_number"]),
        })

# Also index by disc for matching
nf_by_disc = {}
for nf in nf_deg2_tr:
    nf_by_disc[nf["disc"]] = nf

print(f"  Totally real degree-2 NF: {len(nf_deg2_tr)} (disc range {min(n['disc'] for n in nf_deg2_tr)}-{max(n['disc'] for n in nf_deg2_tr)})")

# ── Exact matching: level = |disc| ───────────────────────────────────
print("\n== Exact matching: Maass level = NF |disc| ==")

exact_matches = []
matched_levels = sorted(maass_levels & set(nf_by_disc.keys()))
print(f"  Levels with exact disc match: {len(matched_levels)}")

for level in matched_levels:
    nf = nf_by_disc[level]
    sps = maass_by_level[level]
    for sp in sps:
        exact_matches.append({
            "level": level,
            "spectral_parameter": sp,
            "regulator": nf["regulator"],
            "log_regulator": nf["log_regulator"],
            "class_number": nf["class_number"],
        })

print(f"  Total matched (Maass form, NF) pairs: {len(exact_matches)}")

# ── Correlation: R vs log(regulator) ─────────────────────────────────
if len(exact_matches) > 10:
    R_vals = np.array([m["spectral_parameter"] for m in exact_matches])
    log_reg_vals = np.array([m["log_regulator"] for m in exact_matches])

    # Filter out any None/nan
    valid = np.isfinite(R_vals) & np.isfinite(log_reg_vals)
    R_vals = R_vals[valid]
    log_reg_vals = log_reg_vals[valid]

    # Pearson and Spearman
    r_pearson, p_pearson = stats.pearsonr(R_vals, log_reg_vals)
    r_spearman, p_spearman = stats.spearmanr(R_vals, log_reg_vals)

    # Also: R vs regulator (not log)
    reg_vals = np.array([m["regulator"] for m in exact_matches])[valid]
    r_pear_raw, p_pear_raw = stats.pearsonr(R_vals, reg_vals)
    r_spear_raw, p_spear_raw = stats.spearmanr(R_vals, reg_vals)

    print(f"\n  R vs log(regulator):")
    print(f"    Pearson  r = {r_pearson:.6f}, p = {p_pearson:.6e}")
    print(f"    Spearman r = {r_spearman:.6f}, p = {p_spearman:.6e}")
    print(f"  R vs regulator (raw):")
    print(f"    Pearson  r = {r_pear_raw:.6f}, p = {p_pear_raw:.6e}")
    print(f"    Spearman r = {r_spear_raw:.6f}, p = {p_spear_raw:.6e}")

    exact_correlation = {
        "n_pairs": int(len(R_vals)),
        "n_unique_levels": len(matched_levels),
        "R_vs_log_reg": {
            "pearson_r": float(r_pearson),
            "pearson_p": float(p_pearson),
            "spearman_r": float(r_spearman),
            "spearman_p": float(p_spearman),
        },
        "R_vs_reg_raw": {
            "pearson_r": float(r_pear_raw),
            "pearson_p": float(p_pear_raw),
            "spearman_r": float(r_spear_raw),
            "spearman_p": float(p_spear_raw),
        },
        "R_stats": {
            "mean": float(np.mean(R_vals)),
            "std": float(np.std(R_vals)),
            "min": float(np.min(R_vals)),
            "max": float(np.max(R_vals)),
        },
        "log_reg_stats": {
            "mean": float(np.mean(log_reg_vals)),
            "std": float(np.std(log_reg_vals)),
            "min": float(np.min(log_reg_vals)),
            "max": float(np.max(log_reg_vals)),
        },
    }
else:
    exact_correlation = {"n_pairs": len(exact_matches), "error": "too_few_matches"}

# ── Level-aggregated: median R vs regulator per level ────────────────
print("\n== Level-aggregated: median(R) per level vs regulator ==")

level_agg_pairs = []
for level in matched_levels:
    nf = nf_by_disc[level]
    sps = maass_by_level[level]
    level_agg_pairs.append({
        "level": level,
        "median_R": float(np.median(sps)),
        "mean_R": float(np.mean(sps)),
        "min_R": float(np.min(sps)),
        "n_forms": len(sps),
        "regulator": nf["regulator"],
        "log_regulator": nf["log_regulator"],
    })

if len(level_agg_pairs) > 5:
    med_R = np.array([p["median_R"] for p in level_agg_pairs])
    mean_R = np.array([p["mean_R"] for p in level_agg_pairs])
    min_R = np.array([p["min_R"] for p in level_agg_pairs])
    log_regs = np.array([p["log_regulator"] for p in level_agg_pairs])

    valid = np.isfinite(log_regs)
    results_agg = {}
    for name, arr in [("median_R", med_R), ("mean_R", mean_R), ("min_R", min_R)]:
        rp, pp = stats.pearsonr(arr[valid], log_regs[valid])
        rs, ps = stats.spearmanr(arr[valid], log_regs[valid])
        results_agg[name] = {
            "pearson_r": float(rp), "pearson_p": float(pp),
            "spearman_r": float(rs), "spearman_p": float(ps),
        }
        print(f"  {name} vs log(reg): Pearson r={rp:.4f} (p={pp:.4e}), Spearman r={rs:.4f} (p={ps:.4e})")

    level_aggregated = {
        "n_levels": len(level_agg_pairs),
        "correlations": results_agg,
        "pairs": level_agg_pairs,
    }
else:
    level_aggregated = {"n_levels": len(level_agg_pairs), "error": "too_few"}

# ── Extended matching: |disc - level| <= tolerance ───────────────────
print("\n== Extended matching: |disc - level| within tolerance ==")

extended_results = {}
for tol_frac in [0.0, 0.05, 0.10, 0.20]:
    pairs = []
    for nf in nf_deg2_tr:
        disc = nf["disc"]
        for level in maass_levels:
            if tol_frac == 0.0:
                match = (disc == level)
            else:
                match = abs(disc - level) <= tol_frac * disc
            if match:
                for sp in maass_by_level[level]:
                    pairs.append((sp, nf["log_regulator"]))

    if len(pairs) > 10:
        arr = np.array(pairs)
        valid = np.isfinite(arr[:, 1])
        arr = arr[valid]
        rp, pp = stats.pearsonr(arr[:, 0], arr[:, 1])
        rs, ps = stats.spearmanr(arr[:, 0], arr[:, 1])
        extended_results[f"tol_{tol_frac:.2f}"] = {
            "n_pairs": len(arr),
            "pearson_r": float(rp), "pearson_p": float(pp),
            "spearman_r": float(rs), "spearman_p": float(ps),
        }
        print(f"  Tol {tol_frac:.0%}: {len(arr)} pairs, Pearson r={rp:.4f} (p={pp:.4e}), Spearman r={rs:.4f} (p={ps:.4e})")
    else:
        extended_results[f"tol_{tol_frac:.2f}"] = {"n_pairs": len(pairs), "error": "too_few"}
        print(f"  Tol {tol_frac:.0%}: {len(pairs)} pairs (too few)")

# ── First eigenvalue (smallest R per level) vs regulator ─────────────
print("\n== First eigenvalue (min R per level) vs regulator ==")

first_eigen_pairs = []
for level in matched_levels:
    nf = nf_by_disc[level]
    sps = maass_by_level[level]
    first_eigen_pairs.append({
        "level": level,
        "first_R": float(min(sps)),
        "regulator": nf["regulator"],
        "log_regulator": nf["log_regulator"],
    })

if len(first_eigen_pairs) > 5:
    first_R = np.array([p["first_R"] for p in first_eigen_pairs])
    log_regs = np.array([p["log_regulator"] for p in first_eigen_pairs])
    valid = np.isfinite(log_regs)

    rp, pp = stats.pearsonr(first_R[valid], log_regs[valid])
    rs, ps = stats.spearmanr(first_R[valid], log_regs[valid])
    print(f"  first_R vs log(reg): Pearson r={rp:.4f} (p={pp:.4e}), Spearman r={rs:.4f} (p={ps:.4e})")

    # Also: first_R * sqrt(level) vs regulator (normalized spectral gap)
    levels_arr = np.array([p["level"] for p in first_eigen_pairs], dtype=float)
    norm_R = first_R / np.sqrt(levels_arr)
    rp_n, pp_n = stats.pearsonr(norm_R[valid], log_regs[valid])
    rs_n, ps_n = stats.spearmanr(norm_R[valid], log_regs[valid])
    print(f"  first_R/sqrt(N) vs log(reg): Pearson r={rp_n:.4f} (p={pp_n:.4e}), Spearman r={rs_n:.4f} (p={ps_n:.4e})")

    first_eigenvalue_corr = {
        "n_levels": int(np.sum(valid)),
        "first_R_vs_log_reg": {
            "pearson_r": float(rp), "pearson_p": float(pp),
            "spearman_r": float(rs), "spearman_p": float(ps),
        },
        "normalized_R_vs_log_reg": {
            "pearson_r": float(rp_n), "pearson_p": float(pp_n),
            "spearman_r": float(rs_n), "spearman_p": float(ps_n),
        },
    }
else:
    first_eigenvalue_corr = {"n_levels": len(first_eigen_pairs), "error": "too_few"}

# ── CONFOUND CONTROL: partial correlation controlling for level ──────
print("\n== Confound control: partial correlation (controlling for level) ==")

if len(level_agg_pairs) > 10:
    lev_arr = np.array([p["level"] for p in level_agg_pairs], dtype=float)
    med_R_arr = np.array([p["median_R"] for p in level_agg_pairs])
    min_R_arr = np.array([p["min_R"] for p in level_agg_pairs])
    lr_arr = np.array([p["log_regulator"] for p in level_agg_pairs])
    log_lev = np.log(lev_arr)
    valid_pc = np.isfinite(lr_arr)

    # Show the confound: level vs log(reg), level vs R
    r_conf_lr, p_conf_lr = stats.pearsonr(log_lev[valid_pc], lr_arr[valid_pc])
    r_conf_R, p_conf_R = stats.pearsonr(log_lev[valid_pc], min_R_arr[valid_pc])
    print(f"  Confound: log(level) vs log(reg): r={r_conf_lr:.4f} (p={p_conf_lr:.4e})")
    print(f"  Confound: log(level) vs min(R):   r={r_conf_R:.4f} (p={p_conf_R:.4e})")

    # Residualize both on log(level)
    partial_corr = {}
    for name, R_data in [("min_R", min_R_arr), ("median_R", med_R_arr)]:
        slope_r, intercept_r, _, _, _ = stats.linregress(log_lev[valid_pc], R_data[valid_pc])
        resid_R_data = R_data[valid_pc] - (slope_r * log_lev[valid_pc] + intercept_r)

        slope_lr, intercept_lr, _, _, _ = stats.linregress(log_lev[valid_pc], lr_arr[valid_pc])
        resid_lr = lr_arr[valid_pc] - (slope_lr * log_lev[valid_pc] + intercept_lr)

        rp_part, pp_part = stats.pearsonr(resid_R_data, resid_lr)
        rs_part, ps_part = stats.spearmanr(resid_R_data, resid_lr)
        partial_corr[name] = {
            "pearson_r": float(rp_part), "pearson_p": float(pp_part),
            "spearman_r": float(rs_part), "spearman_p": float(ps_part),
        }
        print(f"  Partial ({name} vs log_reg | log_level): Pearson r={rp_part:.4f} (p={pp_part:.4e}), Spearman r={rs_part:.4f} (p={ps_part:.4e})")

    confound_analysis = {
        "confound_log_level_vs_log_reg": {"pearson_r": float(r_conf_lr), "pearson_p": float(p_conf_lr)},
        "confound_log_level_vs_min_R": {"pearson_r": float(r_conf_R), "pearson_p": float(p_conf_R)},
        "partial_correlations_controlling_log_level": partial_corr,
        "verdict": "Raw correlations are almost entirely driven by the shared dependence on level/discriminant. "
                   "After residualizing on log(level), the signal drops to marginal (r ~ -0.18, p ~ 0.07) "
                   "for spectral gap and vanishes for median R.",
    }
else:
    confound_analysis = {"error": "too_few_levels"}

# ── Null distribution: random pairing ────────────────────────────────
print("\n== Null distribution (1000 random pairings) ==")

N_NULL = 1000
rng = np.random.default_rng(42)

if len(exact_matches) > 10:
    null_pearsons = []
    null_spearmans = []

    R_vals_full = np.array([m["spectral_parameter"] for m in exact_matches])
    log_reg_full = np.array([m["log_regulator"] for m in exact_matches])
    valid_full = np.isfinite(R_vals_full) & np.isfinite(log_reg_full)
    R_v = R_vals_full[valid_full]
    lr_v = log_reg_full[valid_full]

    for _ in range(N_NULL):
        shuffled_lr = rng.permutation(lr_v)
        rp_null, _ = stats.pearsonr(R_v, shuffled_lr)
        rs_null, _ = stats.spearmanr(R_v, shuffled_lr)
        null_pearsons.append(float(rp_null))
        null_spearmans.append(float(rs_null))

    null_pearsons = np.array(null_pearsons)
    null_spearmans = np.array(null_spearmans)

    # Observed vs null
    obs_pearson = exact_correlation["R_vs_log_reg"]["pearson_r"]
    obs_spearman = exact_correlation["R_vs_log_reg"]["spearman_r"]

    # Empirical p-value: fraction of null >= |observed|
    p_emp_pearson = float(np.mean(np.abs(null_pearsons) >= abs(obs_pearson)))
    p_emp_spearman = float(np.mean(np.abs(null_spearmans) >= abs(obs_spearman)))

    # Z-score vs null
    z_pearson = float((obs_pearson - np.mean(null_pearsons)) / np.std(null_pearsons)) if np.std(null_pearsons) > 0 else 0.0
    z_spearman = float((obs_spearman - np.mean(null_spearmans)) / np.std(null_spearmans)) if np.std(null_spearmans) > 0 else 0.0

    print(f"  Observed Pearson r = {obs_pearson:.6f}")
    print(f"  Null Pearson: mean={np.mean(null_pearsons):.6f}, std={np.std(null_pearsons):.6f}")
    print(f"  Z-score (Pearson): {z_pearson:.2f}, empirical p = {p_emp_pearson:.4f}")
    print(f"  Observed Spearman r = {obs_spearman:.6f}")
    print(f"  Null Spearman: mean={np.mean(null_spearmans):.6f}, std={np.std(null_spearmans):.6f}")
    print(f"  Z-score (Spearman): {z_spearman:.2f}, empirical p = {p_emp_spearman:.4f}")

    null_results = {
        "n_permutations": N_NULL,
        "pearson": {
            "observed": float(obs_pearson),
            "null_mean": float(np.mean(null_pearsons)),
            "null_std": float(np.std(null_pearsons)),
            "z_score": z_pearson,
            "empirical_p": p_emp_pearson,
        },
        "spearman": {
            "observed": float(obs_spearman),
            "null_mean": float(np.mean(null_spearmans)),
            "null_std": float(np.std(null_spearmans)),
            "z_score": z_spearman,
            "empirical_p": p_emp_spearman,
        },
    }
else:
    null_results = {"error": "too_few_matches_for_null"}

# ── Regulator binned analysis ────────────────────────────────────────
print("\n== Regulator-binned spectral parameter statistics ==")

if len(exact_matches) > 20:
    # Bin by log(regulator)
    lr_all = np.array([m["log_regulator"] for m in exact_matches])
    R_all = np.array([m["spectral_parameter"] for m in exact_matches])
    valid = np.isfinite(lr_all)
    lr_all = lr_all[valid]
    R_all = R_all[valid]

    bin_edges = np.percentile(lr_all, [0, 25, 50, 75, 100])
    bin_labels = ["Q1", "Q2", "Q3", "Q4"]
    binned_stats = []

    for i in range(4):
        mask = (lr_all >= bin_edges[i]) & (lr_all < bin_edges[i+1] + (1e-10 if i == 3 else 0))
        if np.sum(mask) < 3:
            continue
        R_bin = R_all[mask]
        binned_stats.append({
            "quartile": bin_labels[i],
            "log_reg_range": [float(bin_edges[i]), float(bin_edges[i+1])],
            "n": int(np.sum(mask)),
            "R_mean": float(np.mean(R_bin)),
            "R_median": float(np.median(R_bin)),
            "R_std": float(np.std(R_bin)),
        })
        print(f"  {bin_labels[i]} (log_reg {bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}): n={np.sum(mask)}, mean R={np.mean(R_bin):.3f}, median R={np.median(R_bin):.3f}")

    # KW test: do quartiles have different R distributions?
    groups_for_kw = []
    for i in range(4):
        mask = (lr_all >= bin_edges[i]) & (lr_all < bin_edges[i+1] + (1e-10 if i == 3 else 0))
        if np.sum(mask) >= 3:
            groups_for_kw.append(R_all[mask])

    if len(groups_for_kw) >= 2:
        kw_stat, kw_p = stats.kruskal(*groups_for_kw)
        print(f"  Kruskal-Wallis: H={kw_stat:.4f}, p={kw_p:.4e}")
        binned_analysis = {
            "quartile_stats": binned_stats,
            "kruskal_wallis_H": float(kw_stat),
            "kruskal_wallis_p": float(kw_p),
        }
    else:
        binned_analysis = {"quartile_stats": binned_stats, "error": "insufficient_groups"}
else:
    binned_analysis = {"error": "too_few_matches"}

# ── Higher degree check (degree 3, 4) ───────────────────────────────
print("\n== Higher degree fields (check for broader pattern) ==")

higher_degree_results = {}
for deg in [3, 4]:
    nf_deg = [nf for nf in nf_all if nf["degree"] == deg and nf["disc_sign"] == 1]
    if not nf_deg:
        nf_deg = [nf for nf in nf_all if nf["degree"] == deg]
    nf_deg_by_disc = {}
    for nf in nf_deg:
        d = int(nf["disc_abs"])
        nf_deg_by_disc[d] = nf

    overlap = maass_levels & set(nf_deg_by_disc.keys())
    pairs = []
    for level in overlap:
        nf = nf_deg_by_disc[level]
        reg = float(nf["regulator"])
        if reg <= 0:
            continue
        for sp in maass_by_level[level]:
            pairs.append((sp, np.log(reg)))

    if len(pairs) > 10:
        arr = np.array(pairs)
        rp, pp = stats.pearsonr(arr[:, 0], arr[:, 1])
        rs, ps = stats.spearmanr(arr[:, 0], arr[:, 1])
        higher_degree_results[f"degree_{deg}"] = {
            "n_fields": len(nf_deg),
            "n_overlap_levels": len(overlap),
            "n_pairs": len(pairs),
            "pearson_r": float(rp), "pearson_p": float(pp),
            "spearman_r": float(rs), "spearman_p": float(ps),
        }
        print(f"  Degree {deg}: {len(pairs)} pairs, Pearson r={rp:.4f} (p={pp:.4e}), Spearman r={rs:.4f} (p={ps:.4e})")
    else:
        higher_degree_results[f"degree_{deg}"] = {
            "n_fields": len(nf_deg),
            "n_overlap_levels": len(overlap),
            "n_pairs": len(pairs),
            "note": "too_few_pairs",
        }
        print(f"  Degree {deg}: {len(nf_deg)} NF, {len(overlap)} overlap, {len(pairs)} pairs (too few)")

# ── Assemble results ─────────────────────────────────────────────────
# Determine signal strength
if isinstance(exact_correlation, dict) and "R_vs_log_reg" in exact_correlation:
    obs_r = abs(exact_correlation["R_vs_log_reg"]["spearman_r"])
    obs_p = exact_correlation["R_vs_log_reg"]["spearman_p"]
    if obs_r > 0.10 and obs_p < 0.01:
        signal_strength = "moderate"
    elif obs_r > 0.05 and obs_p < 0.05:
        signal_strength = "weak"
    elif obs_p < 0.05:
        signal_strength = "marginal"
    else:
        signal_strength = "null"
else:
    signal_strength = "insufficient_data"
    obs_r = None
    obs_p = None

results = {
    "metadata": {
        "question": "ChatGPT New#4: Maass Spectral Gap vs Number Field Regulator Scaling",
        "theory": "For totally real fields of degree d, Maass forms on GL(d) at level=|disc| should have spectral parameters related to the regulator",
        "n_maass_forms": len(maass_forms),
        "n_maass_levels": len(maass_levels),
        "n_nf_degree2_totally_real": len(nf_deg2_tr),
        "n_exact_disc_level_matches": len(matched_levels),
        "n_matched_pairs": len(exact_matches),
        "expected_r_range": "0.05-0.12",
    },
    "exact_match_correlation": exact_correlation,
    "level_aggregated_correlation": level_aggregated,
    "first_eigenvalue_correlation": first_eigenvalue_corr,
    "extended_matching": extended_results,
    "null_distribution": null_results,
    "regulator_binned_analysis": binned_analysis,
    "higher_degree_fields": higher_degree_results,
    "confound_analysis": confound_analysis,
    "interpretation": {
        "signal_strength_raw": signal_strength,
        "signal_strength_after_confound_control": (
            "marginal" if isinstance(confound_analysis, dict)
            and "partial_correlations_controlling_log_level" in confound_analysis
            and abs(confound_analysis["partial_correlations_controlling_log_level"]
                    .get("min_R", {}).get("pearson_r", 0)) > 0.15
            else "null"
        ),
        "observed_spearman_r_raw": float(obs_r) if obs_r is not None else None,
        "observed_spearman_p_raw": float(obs_p) if obs_p is not None else None,
        "partial_r_after_level_control": (
            confound_analysis.get("partial_correlations_controlling_log_level", {})
            .get("min_R", {}).get("pearson_r")
            if isinstance(confound_analysis, dict) else None
        ),
        "null_z_score": null_results.get("spearman", {}).get("z_score"),
        "null_empirical_p": null_results.get("spearman", {}).get("empirical_p"),
        "verdict": (
            "The raw R-vs-log(regulator) correlation is very strong (r ~ -0.75 to -0.85) "
            "but is almost entirely a confound: both spectral parameters and regulators "
            "scale with level/discriminant. After residualizing on log(level), the partial "
            "correlation for the spectral gap drops to r ~ -0.18 (p ~ 0.07), marginal at best. "
            "For median R it vanishes entirely. The theoretical connection may exist but is "
            "not detectable above the level-scaling confound in this data."
        ),
        "notes": [
            "CRITICAL: Raw correlations are confounded by shared level/disc dependence",
            "Partial correlation controlling for log(level) is the honest test",
            "Matching is disc=level (exact), theoretically motivated",
            "Each level maps to one NF but many Maass forms, inflating pair count",
            "Level-aggregated (one point per level) is the cleaner test",
            "First eigenvalue (spectral gap) shows marginal partial signal (p~0.07)",
            "Random pairing null controls for marginal distribution artifacts",
        ],
    },
}

# ── Save ──────────────────────────────────────────────────────────────
with open(OUT_PATH, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {OUT_PATH}")

# ── Final summary ─────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SUMMARY: Maass Spectral Gap vs NF Regulator")
print("=" * 60)
print(f"Exact matches (disc=level): {len(matched_levels)} levels, {len(exact_matches)} pairs")
print(f"Signal strength: {signal_strength}")
if isinstance(exact_correlation, dict) and "R_vs_log_reg" in exact_correlation:
    ec = exact_correlation["R_vs_log_reg"]
    print(f"R vs log(reg) Pearson:  r={ec['pearson_r']:.4f}, p={ec['pearson_p']:.4e}")
    print(f"R vs log(reg) Spearman: r={ec['spearman_r']:.4f}, p={ec['spearman_p']:.4e}")
if isinstance(null_results, dict) and "spearman" in null_results:
    ns = null_results["spearman"]
    print(f"Null z-score (Spearman): {ns['z_score']:.2f}, empirical p={ns['empirical_p']:.4f}")
if isinstance(first_eigenvalue_corr, dict) and "first_R_vs_log_reg" in first_eigenvalue_corr:
    fe = first_eigenvalue_corr["first_R_vs_log_reg"]
    print(f"First eigenvalue vs log(reg): Pearson r={fe['pearson_r']:.4f}, Spearman r={fe['spearman_r']:.4f}")
