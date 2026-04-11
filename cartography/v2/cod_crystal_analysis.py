"""
COD Crystal Structure Analysis — Volume, Symmetry, Cross-Reference
Analyzes 9,800 COD structures: cell volumes, parameter ratios, angles,
element frequencies, and cross-references with Materials Project.
"""

import json
import numpy as np
from collections import Counter
from pathlib import Path
from scipy import stats

# ── Load data ───────────────────────────────────────────────────────
COD_PATH = Path(__file__).parent.parent / "physics" / "data" / "cod" / "cod_structures.json"
MP_PATH = Path(__file__).parent.parent / "physics" / "data" / "materials_project_10k.json"
OUT_PATH = Path(__file__).parent / "cod_crystal_analysis_results.json"

with open(COD_PATH) as f:
    cod = json.load(f)
print(f"Loaded {len(cod)} COD structures")

with open(MP_PATH) as f:
    mp = json.load(f)
print(f"Loaded {len(mp)} MP structures")

results = {}

# ── 1. Cell volume distribution ─────────────────────────────────────
volumes = np.array([s["cell_volume"] for s in cod if s.get("cell_volume") is not None])
print(f"\n=== Cell Volume Distribution (n={len(volumes)}) ===")

vol_stats = {
    "count": int(len(volumes)),
    "mean": float(np.mean(volumes)),
    "median": float(np.median(volumes)),
    "std": float(np.std(volumes)),
    "min": float(np.min(volumes)),
    "max": float(np.max(volumes)),
    "q25": float(np.percentile(volumes, 25)),
    "q75": float(np.percentile(volumes, 75)),
}

# Log-normal test: take log, test normality via Shapiro on subsample
log_vols = np.log(volumes[volumes > 0])
# Shapiro-Wilk max 5000 samples
rng = np.random.default_rng(42)
sub = rng.choice(log_vols, size=min(5000, len(log_vols)), replace=False)
shapiro_stat, shapiro_p = stats.shapiro(sub)
# Also D'Agostino-Pearson on full set
dagostino_stat, dagostino_p = stats.normaltest(log_vols)

vol_stats["log_normal_test"] = {
    "shapiro_wilk_stat": float(shapiro_stat),
    "shapiro_wilk_p": float(shapiro_p),
    "dagostino_k2_stat": float(dagostino_stat),
    "dagostino_k2_p": float(dagostino_p),
    "log_mean": float(np.mean(log_vols)),
    "log_std": float(np.std(log_vols)),
    "interpretation": "log-normal" if shapiro_p > 0.05 else "not log-normal (heavy tails likely)"
}

print(f"  Mean: {vol_stats['mean']:.2f}, Median: {vol_stats['median']:.2f}")
print(f"  Range: [{vol_stats['min']:.2f}, {vol_stats['max']:.2f}]")
print(f"  Shapiro on log(vol): W={shapiro_stat:.4f}, p={shapiro_p:.2e}")
print(f"  D'Agostino on log(vol): k2={dagostino_stat:.2f}, p={dagostino_p:.2e}")

results["cell_volume_distribution"] = vol_stats

# ── 2. Volume by nelements ──────────────────────────────────────────
print("\n=== Volume by nelements ===")
nel_groups = {}
for s in cod:
    nel = s.get("nelements")
    vol = s.get("cell_volume")
    if nel is not None and vol is not None:
        nel_groups.setdefault(nel, []).append(vol)

nel_stats = {}
for nel in sorted(nel_groups.keys()):
    vols = np.array(nel_groups[nel])
    entry = {
        "count": int(len(vols)),
        "mean": float(np.mean(vols)),
        "median": float(np.median(vols)),
        "std": float(np.std(vols)),
        "min": float(np.min(vols)),
        "max": float(np.max(vols)),
    }
    nel_stats[str(nel)] = entry
    print(f"  nelements={nel}: n={entry['count']}, mean={entry['mean']:.1f}, median={entry['median']:.1f}")

# Correlation: nelements vs volume
nels_arr = []
vols_arr = []
for s in cod:
    if s.get("nelements") is not None and s.get("cell_volume") is not None:
        nels_arr.append(s["nelements"])
        vols_arr.append(s["cell_volume"])
nels_arr = np.array(nels_arr)
vols_arr = np.array(vols_arr)
corr_pearson, corr_p_pearson = stats.pearsonr(nels_arr, vols_arr)
corr_spearman, corr_p_spearman = stats.spearmanr(nels_arr, vols_arr)

nel_volume_correlation = {
    "pearson_r": float(corr_pearson),
    "pearson_p": float(corr_p_pearson),
    "spearman_rho": float(corr_spearman),
    "spearman_p": float(corr_p_spearman),
}
print(f"  Pearson r={corr_pearson:.4f} (p={corr_p_pearson:.2e})")
print(f"  Spearman rho={corr_spearman:.4f} (p={corr_p_spearman:.2e})")

results["volume_by_nelements"] = nel_stats
results["nelements_volume_correlation"] = nel_volume_correlation

# ── 3. Cell parameter ratios ────────────────────────────────────────
print("\n=== Cell Parameter Ratios ===")
ratios_ab, ratios_bc, ratios_ac = [], [], []
for s in cod:
    a, b, c = s.get("cell_a"), s.get("cell_b"), s.get("cell_c")
    if a and b and c and a > 0 and b > 0 and c > 0:
        ratios_ab.append(a / b)
        ratios_bc.append(b / c)
        ratios_ac.append(a / c)

def ratio_stats(arr, name):
    arr = np.array(arr)
    cubic_frac = float(np.mean(np.abs(arr - 1.0) < 0.01))  # within 1% of 1.0
    near_one_frac = float(np.mean(np.abs(arr - 1.0) < 0.05))  # within 5%
    return {
        "count": int(len(arr)),
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "std": float(np.std(arr)),
        "fraction_within_1pct_of_1": cubic_frac,
        "fraction_within_5pct_of_1": near_one_frac,
    }

ratio_results = {
    "a_over_b": ratio_stats(ratios_ab, "a/b"),
    "b_over_c": ratio_stats(ratios_bc, "b/c"),
    "a_over_c": ratio_stats(ratios_ac, "a/c"),
}

# Fraction that are cubic (all three ratios ~1)
cubic_count = 0
total_ratio = 0
for s in cod:
    a, b, c = s.get("cell_a"), s.get("cell_b"), s.get("cell_c")
    if a and b and c and a > 0 and b > 0 and c > 0:
        total_ratio += 1
        if abs(a/b - 1) < 0.01 and abs(b/c - 1) < 0.01 and abs(a/c - 1) < 0.01:
            cubic_count += 1

ratio_results["cubic_fraction"] = float(cubic_count / total_ratio) if total_ratio > 0 else 0
ratio_results["cubic_count"] = cubic_count
ratio_results["total_with_params"] = total_ratio

for key in ["a_over_b", "b_over_c", "a_over_c"]:
    r = ratio_results[key]
    print(f"  {key}: mean={r['mean']:.3f}, median={r['median']:.3f}, "
          f"within 1% of 1.0: {r['fraction_within_1pct_of_1']:.1%}")
print(f"  Cubic (all ratios ~1): {cubic_count}/{total_ratio} ({ratio_results['cubic_fraction']:.1%})")

results["cell_parameter_ratios"] = ratio_results

# ── 4. Angle distribution ───────────────────────────────────────────
print("\n=== Angle Distribution ===")
alphas, betas, gammas = [], [], []
for s in cod:
    al, be, ga = s.get("cell_alpha"), s.get("cell_beta"), s.get("cell_gamma")
    if al is not None:
        alphas.append(al)
    if be is not None:
        betas.append(be)
    if ga is not None:
        gammas.append(ga)

def angle_stats(arr, name):
    arr = np.array(arr)
    exact_90 = float(np.mean(arr == 90.0))
    near_90 = float(np.mean(np.abs(arr - 90.0) < 0.1))
    return {
        "count": int(len(arr)),
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "fraction_exactly_90": exact_90,
        "fraction_within_0.1_of_90": near_90,
        "unique_values_sample": sorted(list(set(np.round(arr, 2))))[:20],
    }

angle_results = {
    "alpha": angle_stats(alphas, "alpha"),
    "beta": angle_stats(betas, "beta"),
    "gamma": angle_stats(gammas, "gamma"),
}

# Orthorhombic+: all three angles exactly 90
ortho_count = 0
total_angle = 0
for s in cod:
    al, be, ga = s.get("cell_alpha"), s.get("cell_beta"), s.get("cell_gamma")
    if al is not None and be is not None and ga is not None:
        total_angle += 1
        if al == 90.0 and be == 90.0 and ga == 90.0:
            ortho_count += 1

angle_results["all_90_fraction"] = float(ortho_count / total_angle) if total_angle else 0
angle_results["all_90_count"] = ortho_count
angle_results["total_with_angles"] = total_angle

# Monoclinic: alpha=gamma=90, beta!=90
mono_count = sum(1 for s in cod
    if s.get("cell_alpha") == 90.0 and s.get("cell_gamma") == 90.0
    and s.get("cell_beta") is not None and s["cell_beta"] != 90.0)
angle_results["monoclinic_count"] = mono_count
angle_results["monoclinic_fraction"] = float(mono_count / total_angle) if total_angle else 0

# Triclinic: none are 90
tri_count = sum(1 for s in cod
    if s.get("cell_alpha") is not None and s["cell_alpha"] != 90.0
    and s.get("cell_beta") is not None and s["cell_beta"] != 90.0
    and s.get("cell_gamma") is not None and s["cell_gamma"] != 90.0)
angle_results["triclinic_count"] = tri_count
angle_results["triclinic_fraction"] = float(tri_count / total_angle) if total_angle else 0

for a in ["alpha", "beta", "gamma"]:
    r = angle_results[a]
    print(f"  {a}: mean={r['mean']:.2f}, exactly 90: {r['fraction_exactly_90']:.1%}")
print(f"  All angles = 90 (orthorhombic+): {ortho_count}/{total_angle} ({angle_results['all_90_fraction']:.1%})")
print(f"  Monoclinic pattern: {mono_count} ({angle_results['monoclinic_fraction']:.1%})")
print(f"  Triclinic pattern: {tri_count} ({angle_results['triclinic_fraction']:.1%})")

results["angle_distribution"] = angle_results

# ── 5. Formula / Element analysis ───────────────────────────────────
print("\n=== Element Frequency ===")
element_counter = Counter()
for s in cod:
    if s.get("elements"):
        for el in s["elements"]:
            element_counter[el] += 1

top_30 = element_counter.most_common(30)
element_freq = {el: cnt for el, cnt in top_30}
total_structs_with_elements = sum(1 for s in cod if s.get("elements"))

element_results = {
    "total_structures_with_elements": total_structs_with_elements,
    "unique_elements": len(element_counter),
    "top_30_elements": {el: {"count": cnt, "fraction": round(cnt / total_structs_with_elements, 4)}
                        for el, cnt in top_30},
}

for el, cnt in top_30[:15]:
    print(f"  {el}: {cnt} ({cnt/total_structs_with_elements:.1%})")

# nelements distribution
nel_counter = Counter(s.get("nelements") for s in cod if s.get("nelements") is not None)
element_results["nelements_distribution"] = {str(k): v for k, v in sorted(nel_counter.items())}
print(f"\n  nelements distribution:")
for k, v in sorted(nel_counter.items()):
    print(f"    {k}: {v}")

# Most common formulas
formula_counter = Counter(s.get("chemical_formula_reduced") for s in cod
                          if s.get("chemical_formula_reduced"))
top_formulas = formula_counter.most_common(20)
element_results["top_20_formulas"] = {f: c for f, c in top_formulas}
print(f"\n  Top 10 formulas:")
for f, c in top_formulas[:10]:
    print(f"    {f}: {c}")

results["element_analysis"] = element_results

# ── 6. Cross-reference with Materials Project ───────────────────────
print("\n=== Cross-Reference: COD vs MP ===")

# Build formula -> volumes maps
cod_formula_vols = {}
for s in cod:
    f = s.get("chemical_formula_reduced")
    v = s.get("cell_volume")
    if f and v is not None:
        cod_formula_vols.setdefault(f, []).append(v)

mp_formula_vols = {}
for s in mp:
    f = s.get("formula")
    v = s.get("volume")
    if f and v is not None:
        mp_formula_vols.setdefault(f, []).append(v)

# Find shared formulas
shared = set(cod_formula_vols.keys()) & set(mp_formula_vols.keys())
print(f"  COD formulas: {len(cod_formula_vols)}")
print(f"  MP formulas: {len(mp_formula_vols)}")
print(f"  Shared formulas: {len(shared)}")

cross_ref = {
    "cod_unique_formulas": len(cod_formula_vols),
    "mp_unique_formulas": len(mp_formula_vols),
    "shared_formulas": len(shared),
    "comparisons": [],
}

# For shared formulas, compare mean volumes
vol_diffs = []
for f in sorted(shared):
    cod_mean = float(np.mean(cod_formula_vols[f]))
    mp_mean = float(np.mean(mp_formula_vols[f]))
    ratio = cod_mean / mp_mean if mp_mean > 0 else None
    diff_pct = ((cod_mean - mp_mean) / mp_mean * 100) if mp_mean > 0 else None
    entry = {
        "formula": f,
        "cod_mean_volume": round(cod_mean, 2),
        "mp_mean_volume": round(mp_mean, 2),
        "cod_count": len(cod_formula_vols[f]),
        "mp_count": len(mp_formula_vols[f]),
        "ratio_cod_mp": round(ratio, 4) if ratio else None,
        "diff_pct": round(diff_pct, 2) if diff_pct else None,
    }
    cross_ref["comparisons"].append(entry)
    if ratio is not None:
        vol_diffs.append(diff_pct)

if vol_diffs:
    vol_diffs = np.array(vol_diffs)
    cross_ref["volume_difference_stats"] = {
        "mean_diff_pct": float(np.mean(vol_diffs)),
        "median_diff_pct": float(np.median(vol_diffs)),
        "std_diff_pct": float(np.std(vol_diffs)),
        "within_5pct": float(np.mean(np.abs(vol_diffs) < 5)),
        "within_10pct": float(np.mean(np.abs(vol_diffs) < 10)),
        "within_20pct": float(np.mean(np.abs(vol_diffs) < 20)),
    }
    print(f"  Mean volume diff: {np.mean(vol_diffs):.1f}%")
    print(f"  Median volume diff: {np.median(vol_diffs):.1f}%")
    print(f"  Within 5%: {np.mean(np.abs(vol_diffs) < 5):.1%}")
    print(f"  Within 10%: {np.mean(np.abs(vol_diffs) < 10):.1%}")

    # Show biggest outliers
    cross_ref["comparisons"].sort(key=lambda x: abs(x["diff_pct"]) if x["diff_pct"] else 0, reverse=True)
    print(f"\n  Top outliers (biggest volume mismatch):")
    for c in cross_ref["comparisons"][:5]:
        print(f"    {c['formula']}: COD={c['cod_mean_volume']}, MP={c['mp_mean_volume']}, diff={c['diff_pct']}%")

results["cross_reference_cod_mp"] = cross_ref

# ── 7. Summary ──────────────────────────────────────────────────────
summary = {
    "dataset": "COD (Crystallography Open Database) via OPTIMADE",
    "n_structures": len(cod),
    "n_with_volume": int(len(volumes)),
    "volume_median": float(np.median(volumes)),
    "volume_spans_orders_of_magnitude": float(np.log10(np.max(volumes)) - np.log10(np.min(volumes[volumes > 0]))),
    "dominant_symmetry": "orthorhombic+" if angle_results["all_90_fraction"] > 0.5 else "mixed",
    "orthorhombic_plus_fraction": angle_results["all_90_fraction"],
    "monoclinic_fraction": angle_results["monoclinic_fraction"],
    "cubic_fraction": ratio_results["cubic_fraction"],
    "most_common_element": top_30[0][0] if top_30 else None,
    "most_common_formula": top_formulas[0][0] if top_formulas else None,
    "nelements_volume_correlation_spearman": float(corr_spearman),
    "mp_shared_formulas": len(shared),
    "mp_median_volume_diff_pct": float(np.median(vol_diffs)) if len(vol_diffs) > 0 else None,
}
results["summary"] = summary

print(f"\n=== Summary ===")
for k, v in summary.items():
    print(f"  {k}: {v}")

# ── Save ────────────────────────────────────────────────────────────
with open(OUT_PATH, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {OUT_PATH}")
