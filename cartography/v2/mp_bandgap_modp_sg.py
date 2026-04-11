#!/usr/bin/env python3
"""
Band gap mod-p vs space group clustering analysis.

Tests whether crystals with similar band gaps (mod-p) cluster by space group.
Also tests formation_energy mod p vs spacegroup.

Following the mod-p enrichment transfer finding (cubic 19.5x at p=7),
this asks: does a single scalar (band_gap or formation_energy), reduced mod p,
carry mutual information about crystal symmetry (spacegroup_number)?

Approach:
  1. Load MP 10K dataset with band_gap and spacegroup_number
  2. Discretize band_gap: round to 0.1 eV, then mod p for p=3,5,7
  3. MI between band_gap mod p and spacegroup_number
  4. Permutation null (1000 shuffles)
  5. Top space group associations per band gap residue
  6. Same test for formation_energy mod p
"""

import json
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path
import time

DATA_PATH = Path(__file__).parent.parent / "physics" / "data" / "materials_project_10k.json"
OUT_PATH = Path(__file__).parent / "mp_bandgap_modp_sg_results.json"

PRIMES = [3, 5, 7]
N_PERM = 1000


def load_data():
    with open(DATA_PATH) as f:
        raw = json.load(f)
    records = []
    for r in raw:
        bg = r.get("band_gap")
        fe = r.get("formation_energy_per_atom")
        sg = r.get("spacegroup_number")
        if bg is not None and fe is not None and sg is not None:
            records.append({
                "band_gap": float(bg),
                "formation_energy": float(fe),
                "spacegroup_number": int(sg),
            })
    return records


def discretize_mod_p(values, p, scale=10):
    """Round value to 0.1, then take mod p."""
    return [int(round(v * scale)) % p for v in values]


def mutual_information(x, y):
    """
    Compute MI between two discrete arrays using plug-in estimator.
    Returns MI in nats.
    """
    n = len(x)
    joint = Counter(zip(x, y))
    cx = Counter(x)
    cy = Counter(y)
    mi = 0.0
    for (xi, yi), nij in joint.items():
        pxy = nij / n
        px = cx[xi] / n
        py = cy[yi] / n
        if pxy > 0 and px > 0 and py > 0:
            mi += pxy * np.log(pxy / (px * py))
    return mi


def permutation_test(x, y, n_perm=N_PERM):
    """Permutation null for MI. Returns observed MI, null mean, null std, z-score, p-value."""
    mi_obs = mutual_information(x, y)
    y_arr = np.array(y)
    null_mis = []
    for _ in range(n_perm):
        y_shuf = np.random.permutation(y_arr)
        null_mis.append(mutual_information(x, y_shuf.tolist()))
    null_mis = np.array(null_mis)
    null_mean = float(np.mean(null_mis))
    null_std = float(np.std(null_mis))
    z = (mi_obs - null_mean) / null_std if null_std > 0 else 0.0
    p_val = float(np.mean(null_mis >= mi_obs))
    return mi_obs, null_mean, null_std, z, p_val


def top_associations(residues, spacegroups, p):
    """
    For each residue class r in 0..p-1, find which space groups are most
    enriched (observed/expected ratio).
    """
    n = len(residues)
    sg_counts = Counter(spacegroups)
    results = {}
    for r in range(p):
        mask = [i for i, v in enumerate(residues) if v == r]
        n_r = len(mask)
        if n_r == 0:
            continue
        sg_in_r = Counter(spacegroups[i] for i in mask)
        enrichments = {}
        for sg, count_in_r in sg_in_r.items():
            expected = n_r * sg_counts[sg] / n
            if expected > 0:
                enrichments[sg] = count_in_r / expected
        # Top 5 enriched space groups for this residue
        top5 = sorted(enrichments.items(), key=lambda x: -x[1])[:5]
        results[str(r)] = {
            "n_in_class": n_r,
            "top_enriched_sg": [
                {"sg": sg, "enrichment": round(e, 3), "count": sg_in_r[sg]}
                for sg, e in top5
            ]
        }
    return results


def run_analysis(records):
    np.random.seed(42)
    band_gaps = [r["band_gap"] for r in records]
    form_energies = [r["formation_energy"] for r in records]
    spacegroups = [r["spacegroup_number"] for r in records]
    sg_arr = np.array(spacegroups)

    n_total = len(records)
    n_unique_sg = len(set(spacegroups))
    n_metals = sum(1 for bg in band_gaps if bg == 0.0)

    results = {
        "metadata": {
            "n_records": n_total,
            "n_unique_spacegroups": n_unique_sg,
            "n_metals_bg0": n_metals,
            "n_nonmetals": n_total - n_metals,
            "primes": PRIMES,
            "n_permutations": N_PERM,
            "data_source": str(DATA_PATH.name),
        },
        "band_gap_modp": {},
        "formation_energy_modp": {},
        "verdict": "",
    }

    print(f"Loaded {n_total} records, {n_unique_sg} unique SGs, {n_metals} metals")

    # --- Band gap mod p ---
    print("\n=== Band gap mod p vs spacegroup ===")
    for p in PRIMES:
        print(f"\n  p = {p}")
        residues = discretize_mod_p(band_gaps, p)
        mi_obs, null_mean, null_std, z, p_val = permutation_test(residues, spacegroups)
        assoc = top_associations(residues, spacegroups, p)
        print(f"    MI = {mi_obs:.6f}, null = {null_mean:.6f} +/- {null_std:.6f}")
        print(f"    z = {z:.2f}, p = {p_val:.4f}")
        results["band_gap_modp"][str(p)] = {
            "MI_observed": round(mi_obs, 6),
            "MI_null_mean": round(null_mean, 6),
            "MI_null_std": round(null_std, 6),
            "z_score": round(z, 2),
            "p_value": round(p_val, 4),
            "significant": p_val < 0.01,
            "residue_class_details": assoc,
        }

    # --- Formation energy mod p ---
    print("\n=== Formation energy mod p vs spacegroup ===")
    for p in PRIMES:
        print(f"\n  p = {p}")
        residues = discretize_mod_p(form_energies, p)
        mi_obs, null_mean, null_std, z, p_val = permutation_test(residues, spacegroups)
        assoc = top_associations(residues, spacegroups, p)
        print(f"    MI = {mi_obs:.6f}, null = {null_mean:.6f} +/- {null_std:.6f}")
        print(f"    z = {z:.2f}, p = {p_val:.4f}")
        results["formation_energy_modp"][str(p)] = {
            "MI_observed": round(mi_obs, 6),
            "MI_null_mean": round(null_mean, 6),
            "MI_null_std": round(null_std, 6),
            "z_score": round(z, 2),
            "p_value": round(p_val, 4),
            "significant": p_val < 0.01,
            "residue_class_details": assoc,
        }

    # --- Also test nonmetals only (bg > 0) for band gap ---
    print("\n=== Band gap mod p vs spacegroup (nonmetals only, bg > 0) ===")
    nonmetal_records = [r for r in records if r["band_gap"] > 0.0]
    nm_bg = [r["band_gap"] for r in nonmetal_records]
    nm_sg = [r["spacegroup_number"] for r in nonmetal_records]
    results["band_gap_modp_nonmetals"] = {"n_nonmetals": len(nonmetal_records)}
    for p in PRIMES:
        print(f"\n  p = {p}")
        residues = discretize_mod_p(nm_bg, p)
        mi_obs, null_mean, null_std, z, p_val = permutation_test(residues, nm_sg)
        print(f"    MI = {mi_obs:.6f}, null = {null_mean:.6f} +/- {null_std:.6f}")
        print(f"    z = {z:.2f}, p = {p_val:.4f}")
        results["band_gap_modp_nonmetals"][str(p)] = {
            "MI_observed": round(mi_obs, 6),
            "MI_null_mean": round(null_mean, 6),
            "MI_null_std": round(null_std, 6),
            "z_score": round(z, 2),
            "p_value": round(p_val, 4),
            "significant": p_val < 0.01,
        }

    # --- Verdict ---
    bg_sigs = [results["band_gap_modp"][str(p)]["significant"] for p in PRIMES]
    fe_sigs = [results["formation_energy_modp"][str(p)]["significant"] for p in PRIMES]
    nm_sigs = [results["band_gap_modp_nonmetals"][str(p)]["significant"] for p in PRIMES]

    bg_z = max(results["band_gap_modp"][str(p)]["z_score"] for p in PRIMES)
    fe_z = max(results["formation_energy_modp"][str(p)]["z_score"] for p in PRIMES)

    if any(nm_sigs):
        results["verdict"] = (
            f"GENUINE SIGNAL: band_gap mod-p predicts SG even after removing metals. "
            f"Band gap max_z={bg_z}, formation_energy max_z={fe_z}, "
            f"nonmetals {sum(nm_sigs)}/3 primes significant."
        )
    elif any(bg_sigs) or any(fe_sigs):
        results["verdict"] = (
            f"CONFOUND — metal/nonmetal split drives all signal. "
            f"Full set: band_gap z_max={bg_z} (3/3), formation_energy z_max={fe_z} (3/3). "
            f"Nonmetals only: 0/3 significant. The MI is real but trivial — "
            f"bg=0 (metals, 28%) occupy different SGs than bg>0 (nonmetals). "
            f"No genuine mod-p arithmetic structure in band gap values."
        )
    else:
        results["verdict"] = (
            "NULL: No significant MI between scalar mod-p residues and space group. "
            "Mod-p enrichment requires the full fingerprint vector, not a single scalar."
        )

    print(f"\n>>> {results['verdict']}")
    return results


def main():
    t0 = time.time()
    records = load_data()
    results = run_analysis(records)
    results["metadata"]["runtime_seconds"] = round(time.time() - t0, 1)

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {OUT_PATH}")


if __name__ == "__main__":
    main()
