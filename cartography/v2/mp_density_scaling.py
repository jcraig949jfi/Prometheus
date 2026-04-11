"""
Materials Project Density Scaling Laws
======================================
Loads MP 10K sample, computes:
1. Density distribution: mean, median, by crystal system
2. Density vs nsites: scaling law?
3. Density vs band_gap: correlation (metals vs insulators)?
4. Density vs formation_energy: do denser structures tend to be more stable?
5. Density vs volume/nsites (volume per atom): should be inverse by definition
6. Outliers: anomalously high/low density for crystal system
7. Element-density correlation: which elements produce densest structures
"""

import json
import re
import math
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path
from scipy import stats as sp_stats

DATA_PATH = Path(__file__).parent.parent / "physics" / "data" / "materials_project_10k.json"
OUT_PATH = Path(__file__).parent / "mp_density_scaling_results.json"


def parse_elements(formula: str) -> list:
    """Extract element symbols from a chemical formula."""
    return re.findall(r'[A-Z][a-z]?', formula)


def robust_stats(values):
    """Return mean, median, std, IQR, min, max for a list of values."""
    arr = np.array(values)
    q25, q75 = np.percentile(arr, [25, 75])
    return {
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "std": float(np.std(arr)),
        "iqr": float(q75 - q25),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "count": len(arr),
    }


def pearson_and_spearman(x, y, label=""):
    """Compute Pearson and Spearman correlations with p-values."""
    x, y = np.array(x), np.array(y)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if len(x) < 10:
        return {"label": label, "n": len(x), "note": "too few points"}
    pr, pp = sp_stats.pearsonr(x, y)
    sr, sp = sp_stats.spearmanr(x, y)
    return {
        "label": label,
        "n": int(len(x)),
        "pearson_r": float(pr),
        "pearson_p": float(pp),
        "spearman_rho": float(sr),
        "spearman_p": float(sp),
    }


def ols_log_log(x, y):
    """OLS fit in log-log space: log(y) = a + b*log(x). Returns slope, intercept, R^2."""
    x, y = np.array(x), np.array(y)
    mask = (x > 0) & (y > 0) & np.isfinite(x) & np.isfinite(y)
    lx, ly = np.log(x[mask]), np.log(y[mask])
    if len(lx) < 10:
        return {"n": len(lx), "note": "too few points"}
    slope, intercept, r, p, se = sp_stats.linregress(lx, ly)
    return {
        "n": int(len(lx)),
        "slope": float(slope),
        "intercept": float(intercept),
        "R2": float(r ** 2),
        "p_value": float(p),
        "slope_se": float(se),
    }


def main():
    with open(DATA_PATH) as f:
        data = json.load(f)

    print(f"Loaded {len(data)} materials")

    densities = [d["density"] for d in data]
    nsites = [d["nsites"] for d in data]
    band_gaps = [d["band_gap"] for d in data]
    fe = [d["formation_energy_per_atom"] for d in data]
    volumes = [d["volume"] for d in data]
    crystal_systems = [d["crystal_system"] for d in data]
    formulas = [d["formula"] for d in data]
    mat_ids = [d["material_id"] for d in data]

    results = {}

    # ─── 1. Density distribution ───
    results["density_global"] = robust_stats(densities)

    by_cs = defaultdict(list)
    for d, cs in zip(densities, crystal_systems):
        by_cs[cs].append(d)
    results["density_by_crystal_system"] = {
        cs: robust_stats(vals) for cs, vals in sorted(by_cs.items())
    }
    # Kruskal-Wallis across crystal systems
    groups = [np.array(by_cs[cs]) for cs in sorted(by_cs)]
    kw_stat, kw_p = sp_stats.kruskal(*groups)
    results["crystal_system_kruskal_wallis"] = {
        "H_statistic": float(kw_stat),
        "p_value": float(kw_p),
        "significant": bool(kw_p < 0.001),
    }

    # ─── 2. Density vs nsites ───
    results["density_vs_nsites"] = pearson_and_spearman(nsites, densities, "density_vs_nsites")
    results["density_vs_nsites_loglog"] = ols_log_log(nsites, densities)

    # ─── 3. Density vs band_gap ───
    results["density_vs_band_gap"] = pearson_and_spearman(band_gaps, densities, "density_vs_band_gap")

    # Metals (band_gap == 0) vs insulators (band_gap > 1 eV) vs semiconductors
    metals = [d for bg, d in zip(band_gaps, densities) if bg == 0.0]
    semiconductors = [d for bg, d in zip(band_gaps, densities) if 0 < bg <= 1.0]
    insulators = [d for bg, d in zip(band_gaps, densities) if bg > 1.0]
    results["density_by_electronic_class"] = {
        "metals": robust_stats(metals) if metals else None,
        "semiconductors": robust_stats(semiconductors) if semiconductors else None,
        "insulators": robust_stats(insulators) if insulators else None,
    }
    if metals and insulators:
        u_stat, u_p = sp_stats.mannwhitneyu(metals, insulators, alternative="two-sided")
        results["metal_vs_insulator_mannwhitney"] = {
            "U_statistic": float(u_stat),
            "p_value": float(u_p),
            "metal_median": float(np.median(metals)),
            "insulator_median": float(np.median(insulators)),
        }

    # ─── 4. Density vs formation_energy ───
    results["density_vs_formation_energy"] = pearson_and_spearman(
        fe, densities, "density_vs_formation_energy"
    )
    # Restrict to stable materials (fe <= 0)
    stable_d = [d for f, d in zip(fe, densities) if f <= 0]
    stable_fe = [f for f in fe if f <= 0]
    results["density_vs_formation_energy_stable_only"] = pearson_and_spearman(
        stable_fe, stable_d, "density_vs_fe_stable"
    )

    # ─── 5. Density vs volume per atom ───
    vol_per_atom = [v / n for v, n in zip(volumes, nsites)]
    results["density_vs_vol_per_atom"] = pearson_and_spearman(
        vol_per_atom, densities, "density_vs_vol_per_atom"
    )
    results["density_vs_vol_per_atom_loglog"] = ols_log_log(vol_per_atom, densities)

    # ─── 6. Outliers by crystal system ───
    outliers_high = []
    outliers_low = []
    for cs, vals in by_cs.items():
        arr = np.array(vals)
        q25, q75 = np.percentile(arr, [25, 75])
        iqr = q75 - q25
        low_fence = q25 - 3.0 * iqr
        high_fence = q75 + 3.0 * iqr
        for d_entry in data:
            if d_entry["crystal_system"] != cs:
                continue
            dens = d_entry["density"]
            if dens > high_fence:
                outliers_high.append({
                    "material_id": d_entry["material_id"],
                    "formula": d_entry["formula"],
                    "crystal_system": cs,
                    "density": float(dens),
                    "fence": float(high_fence),
                    "z_score": float((dens - np.mean(arr)) / np.std(arr)),
                })
            elif dens < low_fence:
                outliers_low.append({
                    "material_id": d_entry["material_id"],
                    "formula": d_entry["formula"],
                    "crystal_system": cs,
                    "density": float(dens),
                    "fence": float(low_fence),
                    "z_score": float((dens - np.mean(arr)) / np.std(arr)),
                })

    outliers_high.sort(key=lambda x: -x["density"])
    outliers_low.sort(key=lambda x: x["density"])
    results["outliers_high_density"] = {
        "count": len(outliers_high),
        "top_10": outliers_high[:10],
    }
    results["outliers_low_density"] = {
        "count": len(outliers_low),
        "top_10": outliers_low[:10],
    }

    # ─── 7. Element-density correlation ───
    element_densities = defaultdict(list)
    for formula, dens in zip(formulas, densities):
        for el in set(parse_elements(formula)):  # deduplicate per formula
            element_densities[el].append(dens)

    element_stats = {}
    for el, vals in element_densities.items():
        if len(vals) >= 5:
            element_stats[el] = {
                "mean_density": float(np.mean(vals)),
                "median_density": float(np.median(vals)),
                "count": len(vals),
            }

    # Sort by median density descending
    sorted_elements = sorted(element_stats.items(), key=lambda x: -x[1]["median_density"])
    results["element_density_ranking"] = {
        "densest_20": {el: st for el, st in sorted_elements[:20]},
        "lightest_20": {el: st for el, st in sorted_elements[-20:]},
        "total_elements": len(element_stats),
    }

    # ─── 8. Power-law test: density distribution ───
    # Fit density histogram to lognormal
    log_dens = np.log(np.array(densities))
    shapiro_stat, shapiro_p = sp_stats.shapiro(log_dens[:5000])  # shapiro max ~5000
    results["density_lognormal_test"] = {
        "shapiro_W": float(shapiro_stat),
        "shapiro_p": float(shapiro_p),
        "log_density_mean": float(np.mean(log_dens)),
        "log_density_std": float(np.std(log_dens)),
        "interpretation": "lognormal" if shapiro_p > 0.05 else "not_lognormal",
    }

    # ─── Summary ───
    results["summary"] = {
        "total_materials": len(data),
        "global_mean_density": results["density_global"]["mean"],
        "global_median_density": results["density_global"]["median"],
        "densest_crystal_system": max(
            results["density_by_crystal_system"].items(),
            key=lambda x: x[1]["median"]
        )[0],
        "lightest_crystal_system": min(
            results["density_by_crystal_system"].items(),
            key=lambda x: x[1]["median"]
        )[0],
        "density_nsites_correlation": results["density_vs_nsites"]["spearman_rho"],
        "density_bandgap_correlation": results["density_vs_band_gap"]["spearman_rho"],
        "density_fe_correlation": results["density_vs_formation_energy"]["spearman_rho"],
        "density_vol_per_atom_loglog_slope": results["density_vs_vol_per_atom_loglog"].get("slope"),
        "metals_denser_than_insulators": (
            results.get("metal_vs_insulator_mannwhitney", {}).get("metal_median", 0)
            > results.get("metal_vs_insulator_mannwhitney", {}).get("insulator_median", 0)
        ),
        "n_high_outliers": results["outliers_high_density"]["count"],
        "n_low_outliers": results["outliers_low_density"]["count"],
        "top_dense_element": sorted_elements[0][0] if sorted_elements else None,
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {OUT_PATH}")

    # Print key findings
    print(f"\n=== Key Findings ===")
    s = results["summary"]
    print(f"Global density: mean={s['global_mean_density']:.3f}, median={s['global_median_density']:.3f} g/cm^3")
    print(f"Densest crystal system: {s['densest_crystal_system']}")
    print(f"Lightest crystal system: {s['lightest_crystal_system']}")
    print(f"Density-nsites Spearman rho: {s['density_nsites_correlation']:.4f}")
    print(f"Density-bandgap Spearman rho: {s['density_bandgap_correlation']:.4f}")
    print(f"Density-formation_energy Spearman rho: {s['density_fe_correlation']:.4f}")
    print(f"Density vs vol/atom log-log slope: {s['density_vol_per_atom_loglog_slope']:.4f}")
    print(f"Metals denser than insulators: {s['metals_denser_than_insulators']}")
    print(f"High-density outliers: {s['n_high_outliers']}, Low-density outliers: {s['n_low_outliers']}")
    print(f"Densest element: {s['top_dense_element']}")

    mvi = results.get("metal_vs_insulator_mannwhitney", {})
    if mvi:
        print(f"Metal median density: {mvi['metal_median']:.3f}")
        print(f"Insulator median density: {mvi['insulator_median']:.3f}")
        print(f"Mann-Whitney p: {mvi['p_value']:.2e}")

    dln = results["density_lognormal_test"]
    print(f"Lognormal test: {dln['interpretation']} (Shapiro p={dln['shapiro_p']:.2e})")

    # Crystal system ranking
    print(f"\n=== Density by Crystal System (median) ===")
    cs_ranked = sorted(
        results["density_by_crystal_system"].items(),
        key=lambda x: -x[1]["median"]
    )
    for cs, st in cs_ranked:
        print(f"  {cs:15s}: median={st['median']:.3f}, mean={st['mean']:.3f}, n={st['count']}")

    # Top elements
    print(f"\n=== Top 10 Densest Elements ===")
    for el, st in sorted_elements[:10]:
        print(f"  {el:3s}: median={st['median_density']:.3f}, n={st['count']}")

    print(f"\n=== Top 10 Lightest Elements ===")
    for el, st in sorted_elements[-10:]:
        print(f"  {el:3s}: median={st['median_density']:.3f}, n={st['count']}")


if __name__ == "__main__":
    main()
