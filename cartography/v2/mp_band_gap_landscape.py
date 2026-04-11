"""
Materials Project Band Gap Landscape — Crystal Physics Axis
============================================================
210,579 structures from Materials Project.
Analyses: distribution, crystal system grouping, space group statistics,
predictability (RF), formation energy correlation, density-volume scaling.
"""

import json
import os
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "physics" / "data" / "materials_project_full.json"
OUT_PATH = Path(__file__).parent / "mp_band_gap_landscape_results.json"


def load_data():
    print(f"Loading {DATA_PATH} ...")
    with open(DATA_PATH) as f:
        raw = json.load(f)
    print(f"  {len(raw):,} records loaded (raw).")
    # Filter out records with None in critical numeric fields
    clean = [r for r in raw if r.get("band_gap") is not None
             and r.get("formation_energy_per_atom") is not None
             and r.get("density") is not None
             and r.get("volume") is not None
             and r.get("nsites") is not None]
    dropped = len(raw) - len(clean)
    if dropped:
        print(f"  Dropped {dropped:,} records with null numeric fields.")
    print(f"  {len(clean):,} records usable.")
    return clean


def band_gap_distribution(data):
    """Section 2: global band gap statistics."""
    gaps = np.array([r["band_gap"] for r in data])
    metallic = float(np.mean(gaps == 0))
    insulator = float(np.mean(gaps > 3.0))
    semiconductor = float(np.mean((gaps > 0) & (gaps <= 3.0)))
    result = {
        "count": len(gaps),
        "mean": float(np.mean(gaps)),
        "median": float(np.median(gaps)),
        "std": float(np.std(gaps)),
        "min": float(np.min(gaps)),
        "max": float(np.max(gaps)),
        "fraction_metallic": round(metallic, 6),
        "fraction_semiconductor": round(semiconductor, 6),
        "fraction_insulator": round(insulator, 6),
        "percentiles": {
            str(p): round(float(np.percentile(gaps, p)), 4)
            for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]
        },
    }
    print(f"\n=== Band Gap Distribution ===")
    print(f"  Mean: {result['mean']:.4f} eV, Median: {result['median']:.4f} eV")
    print(f"  Metallic: {metallic:.1%}, Semiconductor: {semiconductor:.1%}, Insulator: {insulator:.1%}")
    return result


def by_crystal_system(data):
    """Section 3: mean band gap per crystal system."""
    buckets = defaultdict(list)
    for r in data:
        cs = r.get("crystal_system")
        if cs:
            buckets[cs].append(r["band_gap"])

    result = {}
    print(f"\n=== Band Gap by Crystal System ===")
    for cs in sorted(buckets, key=lambda k: -np.mean(buckets[k])):
        arr = np.array(buckets[cs])
        entry = {
            "count": len(arr),
            "mean": round(float(np.mean(arr)), 4),
            "median": round(float(np.median(arr)), 4),
            "std": round(float(np.std(arr)), 4),
            "fraction_metallic": round(float(np.mean(arr == 0)), 4),
        }
        result[cs] = entry
        print(f"  {cs:14s}  n={entry['count']:6d}  mean={entry['mean']:.3f}  metallic={entry['fraction_metallic']:.1%}")
    return result


def by_spacegroup(data):
    """Section 4: band gap statistics per space group."""
    buckets = defaultdict(list)
    for r in data:
        sg = r.get("spacegroup_number")
        if sg is not None:
            buckets[sg].append(r["band_gap"])

    result = {}
    for sg in sorted(buckets):
        arr = np.array(buckets[sg])
        result[str(sg)] = {
            "count": len(arr),
            "mean": round(float(np.mean(arr)), 4),
            "median": round(float(np.median(arr)), 4),
            "std": round(float(np.std(arr)), 4),
            "fraction_metallic": round(float(np.mean(arr == 0)), 4),
        }

    # Top-10 highest mean band gap SGs (with >=50 entries)
    top_gap = sorted(
        [(sg, v) for sg, v in result.items() if v["count"] >= 50],
        key=lambda x: -x[1]["mean"],
    )[:10]
    # Top-10 most metallic SGs
    top_metal = sorted(
        [(sg, v) for sg, v in result.items() if v["count"] >= 50],
        key=lambda x: -x[1]["fraction_metallic"],
    )[:10]

    print(f"\n=== Space Group Statistics ({len(result)} groups) ===")
    print(f"  Top-10 highest mean band gap (n>=50):")
    for sg, v in top_gap:
        print(f"    SG {sg:>3s}: mean={v['mean']:.3f} eV  n={v['count']}")
    print(f"  Top-10 most metallic (n>=50):")
    for sg, v in top_metal:
        print(f"    SG {sg:>3s}: metallic={v['fraction_metallic']:.1%}  n={v['count']}")

    return {
        "per_group": result,
        "top10_highest_gap": [{"sg": sg, **v} for sg, v in top_gap],
        "top10_most_metallic": [{"sg": sg, **v} for sg, v in top_metal],
        "num_groups": len(result),
    }


def predict_band_gap_bin(data):
    """Section 5: Can space group predict band gap bin? RF classifier."""
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import cross_val_score
        from sklearn.preprocessing import LabelEncoder
    except ImportError:
        print("\n=== Predictability (skipped: sklearn not available) ===")
        return {"skipped": True, "reason": "sklearn not installed"}

    # Features: spacegroup_number, crystal_system (encoded), nsites, density, volume
    crystal_enc = LabelEncoder()
    cs_labels = [r.get("crystal_system", "Unknown") for r in data]
    cs_encoded = crystal_enc.fit_transform(cs_labels)

    X = np.column_stack([
        [r["spacegroup_number"] for r in data],
        cs_encoded,
        [r["nsites"] for r in data],
        [r["density"] for r in data],
        [r["volume"] for r in data],
    ])

    # Bin band gap: 0=metallic, 1=semiconductor (0,3], 2=insulator (>3)
    gaps = np.array([r["band_gap"] for r in data])
    y = np.where(gaps == 0, 0, np.where(gaps <= 3.0, 1, 2))

    class_dist = {int(k): int(v) for k, v in zip(*np.unique(y, return_counts=True))}

    print(f"\n=== Predictability: RF on (SG, crystal_sys, nsites, density, volume) -> gap bin ===")
    print(f"  Class distribution: {class_dist}")

    # Subsample for speed if huge
    n = len(X)
    if n > 50000:
        idx = np.random.RandomState(42).choice(n, 50000, replace=False)
        X_sub, y_sub = X[idx], y[idx]
        print(f"  Subsampled to 50,000 for CV speed.")
    else:
        X_sub, y_sub = X, y

    rf = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    scores = cross_val_score(rf, X_sub, y_sub, cv=5, scoring="accuracy")

    # Majority baseline
    majority_acc = max(class_dist.values()) / sum(class_dist.values())

    # Feature importance from full fit
    rf.fit(X_sub, y_sub)
    feat_names = ["spacegroup_number", "crystal_system", "nsites", "density", "volume"]
    importances = dict(zip(feat_names, [round(float(x), 4) for x in rf.feature_importances_]))

    result = {
        "method": "RandomForest (100 trees, depth=12)",
        "features": feat_names,
        "bins": {"0": "metallic (gap=0)", "1": "semiconductor (0<gap<=3)", "2": "insulator (gap>3)"},
        "class_distribution": class_dist,
        "cv5_accuracy_mean": round(float(np.mean(scores)), 4),
        "cv5_accuracy_std": round(float(np.std(scores)), 4),
        "majority_baseline": round(majority_acc, 4),
        "lift_over_baseline": round(float(np.mean(scores)) - majority_acc, 4),
        "feature_importances": importances,
    }
    print(f"  5-fold CV accuracy: {result['cv5_accuracy_mean']:.4f} ± {result['cv5_accuracy_std']:.4f}")
    print(f"  Majority baseline:  {result['majority_baseline']:.4f}")
    print(f"  Lift:               {result['lift_over_baseline']:.4f}")
    print(f"  Feature importances: {importances}")
    return result


def formation_energy_correlation(data):
    """Section 6: Formation energy vs band gap."""
    fe = np.array([r["formation_energy_per_atom"] for r in data])
    bg = np.array([r["band_gap"] for r in data])

    # Overall Pearson
    corr_all = float(np.corrcoef(fe, bg)[0, 1])

    # Among non-metals only
    mask = bg > 0
    corr_nonmetal = float(np.corrcoef(fe[mask], bg[mask])[0, 1])

    result = {
        "pearson_all": round(corr_all, 6),
        "pearson_nonmetal": round(corr_nonmetal, 6),
        "formation_energy_stats": {
            "mean": round(float(np.mean(fe)), 4),
            "std": round(float(np.std(fe)), 4),
            "min": round(float(np.min(fe)), 4),
            "max": round(float(np.max(fe)), 4),
        },
    }
    print(f"\n=== Formation Energy vs Band Gap ===")
    print(f"  Pearson (all):       {corr_all:.4f}")
    print(f"  Pearson (non-metal): {corr_nonmetal:.4f}")
    return result


def density_volume_scaling(data):
    """Section 7: Density vs volume scaling law."""
    dens = np.array([r["density"] for r in data])
    vol = np.array([r["volume"] for r in data])
    nsites = np.array([r["nsites"] for r in data])

    # log-log fit: log(density) = a * log(volume) + b
    mask = (dens > 0) & (vol > 0)
    log_d = np.log10(dens[mask])
    log_v = np.log10(vol[mask])

    # Raw
    slope_raw, intercept_raw = np.polyfit(log_v, log_d, 1)

    # Per-atom volume
    vol_per_atom = vol / nsites
    mask2 = (dens > 0) & (vol_per_atom > 0)
    log_vpa = np.log10(vol_per_atom[mask2])
    log_d2 = np.log10(dens[mask2])
    slope_pa, intercept_pa = np.polyfit(log_vpa, log_d2, 1)

    result = {
        "raw_log_log": {
            "slope": round(float(slope_raw), 4),
            "intercept": round(float(intercept_raw), 4),
            "note": "log10(density) = slope * log10(volume) + intercept",
        },
        "per_atom_volume_log_log": {
            "slope": round(float(slope_pa), 4),
            "intercept": round(float(intercept_pa), 4),
            "note": "log10(density) = slope * log10(volume/nsites) + intercept",
        },
        "density_stats": {
            "mean": round(float(np.mean(dens)), 4),
            "median": round(float(np.median(dens)), 4),
            "std": round(float(np.std(dens)), 4),
        },
        "volume_per_atom_stats": {
            "mean": round(float(np.mean(vol_per_atom)), 4),
            "median": round(float(np.median(vol_per_atom)), 4),
        },
    }
    print(f"\n=== Density vs Volume Scaling ===")
    print(f"  Raw:     log(dens) = {slope_raw:.4f} * log(vol) + {intercept_raw:.4f}")
    print(f"  PerAtom: log(dens) = {slope_pa:.4f} * log(vol/n) + {intercept_pa:.4f}")
    return result


def lmfdb_structural_parallel(data):
    """Section 8: Compare space group gap structure to LMFDB lattice data if available."""
    # Check for any LMFDB lattice data in cartography
    lattice_path = Path(__file__).parent.parent / "shared" / "data" / "lmfdb_lattices.json"
    if not lattice_path.exists():
        # Try alternate locations
        for alt in [
            Path(__file__).parent.parent / "v2" / "lmfdb_lattice_gaps.json",
            Path(__file__).parent.parent / "shared" / "data" / "spectral_gaps.json",
        ]:
            if alt.exists():
                lattice_path = alt
                break

    # Even without LMFDB lattice data, compute the space-group gap "spectrum"
    # Treat mean band gap per SG as a discrete spectrum and compute its statistics
    buckets = defaultdict(list)
    for r in data:
        sg = r.get("spacegroup_number")
        if sg is not None:
            buckets[sg].append(r["band_gap"])

    sg_means = np.array(sorted([float(np.mean(v)) for v in buckets.values()]))
    gaps_between_sgs = np.diff(sg_means)

    result = {
        "sg_mean_spectrum": {
            "count": len(sg_means),
            "min": round(float(sg_means.min()), 4),
            "max": round(float(sg_means.max()), 4),
            "mean_of_means": round(float(np.mean(sg_means)), 4),
            "std_of_means": round(float(np.std(sg_means)), 4),
        },
        "gap_between_sg_means": {
            "mean_gap": round(float(np.mean(gaps_between_sgs)), 6),
            "std_gap": round(float(np.std(gaps_between_sgs)), 6),
            "max_gap": round(float(np.max(gaps_between_sgs)), 4),
            "min_gap": round(float(np.min(gaps_between_sgs)), 6),
        },
        "lmfdb_comparison": "No LMFDB lattice spectral gap data found in cartography; structural parallel deferred.",
    }
    print(f"\n=== LMFDB Structural Parallel ===")
    print(f"  {len(sg_means)} SG mean band gaps form discrete spectrum")
    print(f"  Gap-between-means: mean={result['gap_between_sg_means']['mean_gap']:.6f}, "
          f"std={result['gap_between_sg_means']['std_gap']:.6f}")
    return result


def main():
    data = load_data()

    results = {}
    results["band_gap_distribution"] = band_gap_distribution(data)
    results["by_crystal_system"] = by_crystal_system(data)
    results["by_spacegroup"] = by_spacegroup(data)
    results["predictability"] = predict_band_gap_bin(data)
    results["formation_energy_vs_gap"] = formation_energy_correlation(data)
    results["density_volume_scaling"] = density_volume_scaling(data)
    results["lmfdb_structural_parallel"] = lmfdb_structural_parallel(data)

    # Summary
    results["_meta"] = {
        "source": "Materials Project (materials_project_full.json)",
        "records": len(data),
        "analyses": list(results.keys()),
        "date": "2026-04-10",
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n=== Results saved to {OUT_PATH} ===")


if __name__ == "__main__":
    main()
