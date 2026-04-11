"""
Materials Project Formation Energy Landscape & Phase Stability
==============================================================
210K structures from Materials Project.
Analyses: formation energy distribution, 2D landscape (formation energy vs band gap),
approximate convex hull analysis per element combination, crystal system vs stability,
stability gap for off-hull structures, nsites vs stability correlation.
"""

import json
import re
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path
from scipy import stats

DATA_PATH = Path(__file__).parent.parent / "physics" / "data" / "materials_project_full.json"
OUT_PATH = Path(__file__).parent / "mp_formation_energy_results.json"


def load_data():
    print(f"Loading {DATA_PATH} ...")
    with open(DATA_PATH) as f:
        raw = json.load(f)
    print(f"  {len(raw):,} records loaded (raw).")
    clean = [r for r in raw if r.get("band_gap") is not None
             and r.get("formation_energy_per_atom") is not None
             and r.get("crystal_system") is not None
             and r.get("nsites") is not None]
    dropped = len(raw) - len(clean)
    if dropped:
        print(f"  Dropped {dropped:,} records with null fields.")
    print(f"  {len(clean):,} records usable.")
    return clean


def extract_elements(formula):
    """Extract sorted tuple of element symbols from a formula string."""
    return tuple(sorted(set(re.findall(r'[A-Z][a-z]?', formula))))


# ── Section 1: Formation energy distribution ──────────────────────────

def formation_energy_distribution(data):
    fe = np.array([r["formation_energy_per_atom"] for r in data])
    stable = float(np.mean(fe < 0))
    metastable = float(np.mean(fe >= 0))

    result = {
        "count": len(fe),
        "mean": round(float(np.mean(fe)), 6),
        "median": round(float(np.median(fe)), 6),
        "std": round(float(np.std(fe)), 6),
        "min": round(float(np.min(fe)), 6),
        "max": round(float(np.max(fe)), 6),
        "fraction_stable_negative": round(stable, 6),
        "fraction_metastable_positive": round(metastable, 6),
        "percentiles": {
            str(p): round(float(np.percentile(fe, p)), 6)
            for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]
        },
    }
    print(f"\n=== Formation Energy Distribution ===")
    print(f"  Mean: {result['mean']:.4f} eV/atom")
    print(f"  Stable (<0): {stable:.1%}, Metastable (>=0): {metastable:.1%}")
    print(f"  Range: [{result['min']:.4f}, {result['max']:.4f}]")
    return result


# ── Section 2: 2D landscape — formation energy vs band gap ───────────

def fe_vs_bandgap_landscape(data):
    fe = np.array([r["formation_energy_per_atom"] for r in data])
    bg = np.array([r["band_gap"] for r in data])

    # Correlation
    r_pearson, p_pearson = stats.pearsonr(fe, bg)
    r_spearman, p_spearman = stats.spearmanr(fe, bg)

    # 2D binned density (formation energy bins x band gap bins)
    fe_edges = np.linspace(float(np.percentile(fe, 1)), float(np.percentile(fe, 99)), 51)
    bg_edges = np.linspace(0, float(np.percentile(bg, 99)), 51)
    hist2d, _, _ = np.histogram2d(fe, bg, bins=[fe_edges, bg_edges])

    # Find density peaks (top 5 bins)
    flat_idx = np.argsort(hist2d.ravel())[::-1][:5]
    peaks = []
    for idx in flat_idx:
        i, j = divmod(int(idx), hist2d.shape[1])
        peaks.append({
            "fe_center": round(float((fe_edges[i] + fe_edges[i+1]) / 2), 4),
            "bg_center": round(float((bg_edges[j] + bg_edges[j+1]) / 2), 4),
            "count": int(hist2d[i, j]),
        })

    # Quadrant analysis
    metallic_stable = int(np.sum((bg == 0) & (fe < 0)))
    metallic_metastable = int(np.sum((bg == 0) & (fe >= 0)))
    gapped_stable = int(np.sum((bg > 0) & (fe < 0)))
    gapped_metastable = int(np.sum((bg > 0) & (fe >= 0)))

    result = {
        "pearson_r": round(float(r_pearson), 6),
        "pearson_p": float(p_pearson),
        "spearman_r": round(float(r_spearman), 6),
        "spearman_p": float(p_spearman),
        "density_peaks": peaks,
        "quadrants": {
            "metallic_stable": metallic_stable,
            "metallic_metastable": metallic_metastable,
            "gapped_stable": gapped_stable,
            "gapped_metastable": gapped_metastable,
        },
    }
    print(f"\n=== Formation Energy vs Band Gap ===")
    print(f"  Pearson r={r_pearson:.4f} (p={p_pearson:.2e})")
    print(f"  Spearman r={r_spearman:.4f}")
    print(f"  Metallic+stable: {metallic_stable:,}  Gapped+stable: {gapped_stable:,}")
    print(f"  Metallic+meta:   {metallic_metastable:,}  Gapped+meta:   {gapped_metastable:,}")
    return result


# ── Section 3: Approximate convex hull per element combination ───────

def convex_hull_analysis(data):
    """
    For each unique element combination, find the structure with lowest
    formation energy (hull point). Compute energy above hull for others.
    This is an approximate 0D hull — real hull needs composition axis,
    but for same-elements grouping this gives the stability floor.
    """
    groups = defaultdict(list)
    for r in data:
        elems = extract_elements(r.get("formula", ""))
        if elems:
            groups[elems].append(r)

    hull_count = 0
    off_hull_gaps = []
    group_sizes = []
    n_polymorphs_with_competition = 0  # groups with >1 structure

    for elems, members in groups.items():
        if len(members) == 1:
            hull_count += 1
            group_sizes.append(1)
            continue

        n_polymorphs_with_competition += 1
        group_sizes.append(len(members))
        fes = [r["formation_energy_per_atom"] for r in members]
        hull_energy = min(fes)
        hull_count += 1  # one hull structure per group

        for fe_val in fes:
            gap = fe_val - hull_energy
            if gap > 1e-9:
                off_hull_gaps.append(gap)

    off_hull_arr = np.array(off_hull_gaps) if off_hull_gaps else np.array([0.0])

    result = {
        "n_element_groups": len(groups),
        "n_groups_with_polymorphs": n_polymorphs_with_competition,
        "n_hull_structures": hull_count,
        "n_off_hull_structures": len(off_hull_gaps),
        "group_size_stats": {
            "mean": round(float(np.mean(group_sizes)), 2),
            "median": float(np.median(group_sizes)),
            "max": int(np.max(group_sizes)),
            "percentile_95": round(float(np.percentile(group_sizes, 95)), 1),
        },
        "stability_gap_eV": {
            "mean": round(float(np.mean(off_hull_arr)), 6),
            "median": round(float(np.median(off_hull_arr)), 6),
            "std": round(float(np.std(off_hull_arr)), 6),
            "max": round(float(np.max(off_hull_arr)), 6),
            "percentiles": {
                str(p): round(float(np.percentile(off_hull_arr, p)), 6)
                for p in [10, 25, 50, 75, 90, 95, 99]
            },
        },
    }
    print(f"\n=== Convex Hull Analysis (approximate, per element combo) ===")
    print(f"  {len(groups):,} unique element combinations")
    print(f"  {n_polymorphs_with_competition:,} groups with >1 polymorph")
    print(f"  {len(off_hull_gaps):,} off-hull structures")
    print(f"  Mean stability gap: {result['stability_gap_eV']['mean']:.4f} eV/atom")
    print(f"  Median stability gap: {result['stability_gap_eV']['median']:.4f} eV/atom")
    return result


# ── Section 4: Crystal system vs formation energy ────────────────────

def crystal_system_stability(data):
    buckets = defaultdict(list)
    for r in data:
        cs = r.get("crystal_system")
        if cs:
            buckets[cs].append(r["formation_energy_per_atom"])

    result = {}
    print(f"\n=== Crystal System vs Formation Energy ===")
    for cs in sorted(buckets, key=lambda k: np.mean(buckets[k])):
        arr = np.array(buckets[cs])
        frac_stable = float(np.mean(arr < 0))
        entry = {
            "count": len(arr),
            "mean_fe": round(float(np.mean(arr)), 6),
            "median_fe": round(float(np.median(arr)), 6),
            "std_fe": round(float(np.std(arr)), 6),
            "fraction_stable": round(frac_stable, 6),
        }
        result[cs] = entry
        print(f"  {cs:14s}: mean={entry['mean_fe']:+.4f}, stable={frac_stable:.1%}, n={len(arr):,}")

    # ANOVA: do crystal systems differ in formation energy?
    groups_for_anova = [np.array(buckets[cs]) for cs in buckets if len(buckets[cs]) >= 30]
    if len(groups_for_anova) >= 2:
        f_stat, p_val = stats.f_oneway(*groups_for_anova)
        result["anova_F"] = round(float(f_stat), 4)
        result["anova_p"] = float(p_val)
        print(f"  ANOVA F={f_stat:.2f}, p={p_val:.2e}")

    return result


# ── Section 5: Stability gap distribution (energy above hull) ────────

def stability_gap_analysis(data):
    """
    Deeper look at stability gaps: how they distribute, and whether
    formation energy alone predicts hull membership.
    """
    groups = defaultdict(list)
    for r in data:
        elems = extract_elements(r.get("formula", ""))
        if elems:
            groups[elems].append(r)

    on_hull_fes = []
    off_hull_fes = []
    gaps_by_crystal = defaultdict(list)

    for elems, members in groups.items():
        if len(members) < 2:
            continue
        fes = [(r["formation_energy_per_atom"], r["crystal_system"]) for r in members]
        hull_energy = min(fe for fe, cs in fes)

        for fe_val, cs in fes:
            gap = fe_val - hull_energy
            if gap < 1e-9:
                on_hull_fes.append(fe_val)
            else:
                off_hull_fes.append(fe_val)
                gaps_by_crystal[cs].append(gap)

    # Gap distribution by crystal system
    gap_by_cs = {}
    for cs in sorted(gaps_by_crystal, key=lambda k: np.mean(gaps_by_crystal[k])):
        arr = np.array(gaps_by_crystal[cs])
        gap_by_cs[cs] = {
            "count": len(arr),
            "mean_gap": round(float(np.mean(arr)), 6),
            "median_gap": round(float(np.median(arr)), 6),
        }

    # Separation between hull and off-hull formation energies
    on_arr = np.array(on_hull_fes) if on_hull_fes else np.array([0.0])
    off_arr = np.array(off_hull_fes) if off_hull_fes else np.array([0.0])

    result = {
        "n_on_hull": len(on_hull_fes),
        "n_off_hull": len(off_hull_fes),
        "on_hull_mean_fe": round(float(np.mean(on_arr)), 6),
        "off_hull_mean_fe": round(float(np.mean(off_arr)), 6),
        "fe_separation": round(float(np.mean(off_arr) - np.mean(on_arr)), 6),
        "gap_by_crystal_system": gap_by_cs,
    }
    print(f"\n=== Stability Gap Deep Dive ===")
    print(f"  On-hull: {len(on_hull_fes):,} (mean fe={np.mean(on_arr):.4f})")
    print(f"  Off-hull: {len(off_hull_fes):,} (mean fe={np.mean(off_arr):.4f})")
    print(f"  FE separation: {result['fe_separation']:.4f} eV/atom")
    return result


# ── Section 6: nsites vs stability ───────────────────────────────────

def nsites_stability(data):
    fe = np.array([r["formation_energy_per_atom"] for r in data])
    ns = np.array([r["nsites"] for r in data])

    r_pearson, p_pearson = stats.pearsonr(ns, fe)
    r_spearman, p_spearman = stats.spearmanr(ns, fe)

    # Bin nsites and compute mean formation energy
    bins = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    binned = {}
    for i in range(len(bins) - 1):
        lo, hi = bins[i], bins[i+1]
        mask = (ns >= lo) & (ns < hi)
        n_in_bin = int(np.sum(mask))
        if n_in_bin > 0:
            label = f"{lo}-{hi-1}"
            binned[label] = {
                "count": n_in_bin,
                "mean_fe": round(float(np.mean(fe[mask])), 6),
                "fraction_stable": round(float(np.mean(fe[mask] < 0)), 6),
            }

    # Large structures (nsites >= 64)
    large_mask = ns >= 64
    small_mask = ns < 64
    large_stable = float(np.mean(fe[large_mask] < 0)) if np.sum(large_mask) > 0 else 0
    small_stable = float(np.mean(fe[small_mask] < 0)) if np.sum(small_mask) > 0 else 0

    result = {
        "pearson_r": round(float(r_pearson), 6),
        "pearson_p": float(p_pearson),
        "spearman_r": round(float(r_spearman), 6),
        "spearman_p": float(p_spearman),
        "nsites_bins": binned,
        "large_vs_small": {
            "large_ge64_count": int(np.sum(large_mask)),
            "large_ge64_fraction_stable": round(large_stable, 6),
            "small_lt64_count": int(np.sum(small_mask)),
            "small_lt64_fraction_stable": round(small_stable, 6),
        },
    }
    print(f"\n=== nsites vs Stability ===")
    print(f"  Pearson r={r_pearson:.4f} (p={p_pearson:.2e})")
    print(f"  Spearman r={r_spearman:.4f}")
    print(f"  Large (>=64 sites): {np.sum(large_mask):,} structures, {large_stable:.1%} stable")
    print(f"  Small (<64 sites):  {np.sum(small_mask):,} structures, {small_stable:.1%} stable")
    return result


# ── Section 7: Density and volume vs formation energy ────────────────

def density_volume_stability(data):
    """Bonus: does density or volume per atom correlate with stability?"""
    fe = np.array([r["formation_energy_per_atom"] for r in data])
    density = np.array([r.get("density", 0) for r in data])
    volume = np.array([r.get("volume", 0) for r in data])
    nsites = np.array([r["nsites"] for r in data])

    # Volume per atom
    vol_per_atom = volume / np.maximum(nsites, 1)

    # Filter valid
    valid = (density > 0) & (volume > 0)
    if np.sum(valid) < 100:
        return {"skipped": True, "reason": "too few valid density/volume records"}

    r_dens, p_dens = stats.pearsonr(density[valid], fe[valid])
    r_vol, p_vol = stats.pearsonr(vol_per_atom[valid], fe[valid])

    result = {
        "density_vs_fe_pearson_r": round(float(r_dens), 6),
        "density_vs_fe_p": float(p_dens),
        "vol_per_atom_vs_fe_pearson_r": round(float(r_vol), 6),
        "vol_per_atom_vs_fe_p": float(p_vol),
        "n_valid": int(np.sum(valid)),
    }
    print(f"\n=== Density/Volume vs Formation Energy ===")
    print(f"  Density-FE Pearson r={r_dens:.4f}")
    print(f"  Vol/atom-FE Pearson r={r_vol:.4f}")
    return result


# ── Main ─────────────────────────────────────────────────────────────

def main():
    data = load_data()

    results = {
        "metadata": {
            "source": "materials_project_full.json",
            "n_records": len(data),
            "analysis": "formation_energy_landscape_phase_stability",
        },
        "formation_energy_distribution": formation_energy_distribution(data),
        "fe_vs_bandgap_landscape": fe_vs_bandgap_landscape(data),
        "convex_hull_approximate": convex_hull_analysis(data),
        "crystal_system_stability": crystal_system_stability(data),
        "stability_gap_analysis": stability_gap_analysis(data),
        "nsites_stability": nsites_stability(data),
        "density_volume_stability": density_volume_stability(data),
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
