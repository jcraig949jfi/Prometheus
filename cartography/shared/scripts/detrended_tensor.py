"""
Detrended Tensor — The clean landscape after stripping prime atmosphere.
=========================================================================
For every object in every dataset, compute prime-detrended residual values
and store them as new concept features. Then rebuild the tensor bridge
on the residuals instead of raw values.

This creates a PARALLEL concept layer:
  - Original: "conductor_169" → integer concept (polluted by primes)
  - Detrended: "residual_0.0342" → position AFTER removing prime structure

The detrended values become new cells in the geometric space.
Tensor train searches on these values find bridges invisible under primes.
Gravitational wells in the detrended space are genuine structure.

Pipeline:
  1. For each dataset, extract numerical arrays
  2. Compute prime factorization features for each value
  3. Fit linear model: value ~ prime_features
  4. Store residuals per object
  5. Build detrended concept layer (binned residuals as concepts)
  6. Run tensor bridge on detrended concepts
  7. Compare: what bonds exist in detrended space that don't exist in raw space?

Usage:
    python detrended_tensor.py              # full rebuild
    python detrended_tensor.py --compare    # show raw vs detrended differences
"""

import json
import math
import sys
import time
import numpy as np
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from scipy import stats as sp_stats

sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path(__file__).resolve().parents[3]
CONVERGENCE = ROOT / "cartography" / "convergence"
DETRENDED_CONCEPTS = CONVERGENCE / "data" / "detrended_concepts.jsonl"
DETRENDED_LINKS = CONVERGENCE / "data" / "detrended_links.jsonl"
DETRENDED_TENSOR = CONVERGENCE / "data" / "detrended_tensor.json"


def prime_features(n):
    """Extract prime factorization features from an integer."""
    n = int(abs(n))
    if n < 2:
        return [0, 0, 0, 0, 0, 0]
    factors = {}
    d = 2
    temp = n
    while d * d <= temp and temp > 1:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1

    n_distinct = len(factors)
    total_exp = sum(factors.values())
    largest = max(factors.keys()) if factors else 0
    smallest = min(factors.keys()) if factors else 0
    is_prime = 1 if n_distinct == 1 and total_exp == 1 else 0
    smoothness = math.log(largest) / math.log(max(n, 2)) if largest > 0 else 0

    return [n_distinct, total_exp, math.log(max(largest, 2)),
            math.log(max(smallest, 2)), is_prime, smoothness]


def detrend_array(values, obj_ids):
    """Detrend an array of integers, returning residuals per object.

    Returns list of (obj_id, raw_value, residual, bin_label) tuples.
    """
    arr = np.array(values, dtype=float)
    valid_mask = arr > 1
    valid_vals = arr[valid_mask]
    valid_ids = [obj_ids[i] for i in range(len(obj_ids)) if valid_mask[i]]

    if len(valid_vals) < 20:
        return []

    # Build feature matrix
    features = np.array([prime_features(int(v)) for v in valid_vals])

    # Remove constant columns
    good_cols = [i for i in range(features.shape[1]) if np.std(features[:, i]) > 1e-10]
    if not good_cols:
        return []
    X = features[:, good_cols]
    X = np.column_stack([X, np.ones(len(X))])

    # Target: log of value
    target = np.log(valid_vals)

    try:
        coeffs, _, _, _ = np.linalg.lstsq(X, target, rcond=None)
        predicted = X @ coeffs
        residuals = target - predicted
    except Exception:
        return []

    # Bin residuals into quantile bins for concept layer
    n_bins = 20
    percentiles = np.percentile(residuals, np.linspace(0, 100, n_bins + 1))

    results = []
    for i in range(len(valid_vals)):
        resid = float(residuals[i])
        # Find bin
        bin_idx = np.searchsorted(percentiles[1:], resid, side='right')
        bin_idx = min(bin_idx, n_bins - 1)
        bin_label = f"resid_q{bin_idx:02d}"  # q00 to q19

        results.append({
            "obj_id": valid_ids[i],
            "raw_value": float(valid_vals[i]),
            "residual": round(resid, 6),
            "bin": bin_label,
        })

    return results


def extract_and_detrend():
    """Extract numerical arrays from all datasets and detrend."""
    print("  Extracting and detrending all datasets...")

    from search_engine import (
        _load_genus2, _genus2_cache,
        _load_nf, _nf_cache,
        _load_knots, _knots_cache,
        _load_smallgroups, _smallgroups_cache,
        _load_maass, _maass_cache,
        _load_lattices, _lattices_cache,
        _get_duck,
    )

    all_detrended = {}  # dataset -> list of detrended records

    # Genus-2 conductors
    _load_genus2()
    if _genus2_cache:
        vals = [c["conductor"] for c in _genus2_cache if c.get("conductor")]
        ids = [c["label"] for c in _genus2_cache if c.get("conductor")]
        all_detrended["Genus2"] = detrend_array(vals, ids)
        print(f"    Genus2: {len(all_detrended['Genus2'])} detrended values")

    # NF discriminants
    _load_nf()
    if _nf_cache:
        vals = [abs(int(f["disc_abs"])) for f in _nf_cache
                if f.get("disc_abs") and str(f["disc_abs"]).lstrip("-").isdigit()]
        ids = [f.get("label", f"nf_{i}") for i, f in enumerate(_nf_cache)
               if f.get("disc_abs") and str(f["disc_abs"]).lstrip("-").isdigit()]
        all_detrended["NumberFields"] = detrend_array(vals, ids)
        print(f"    NumberFields: {len(all_detrended['NumberFields'])} detrended values")

    # Knot determinants
    _load_knots()
    knot_list = _knots_cache.get("knots", []) if isinstance(_knots_cache, dict) else []
    if knot_list:
        vals = [k["determinant"] for k in knot_list
                if isinstance(k, dict) and isinstance(k.get("determinant"), (int, float)) and k["determinant"] > 0]
        ids = [f"knot_{i}" for i, k in enumerate(knot_list)
               if isinstance(k, dict) and isinstance(k.get("determinant"), (int, float)) and k.get("determinant", 0) > 0]
        all_detrended["KnotInfo"] = detrend_array(vals, ids)
        print(f"    KnotInfo: {len(all_detrended['KnotInfo'])} detrended values")

    # SmallGroups counts
    _load_smallgroups()
    if _smallgroups_cache:
        vals = [g["n_groups"] for g in _smallgroups_cache
                if isinstance(g.get("n_groups"), int) and 0 < g["n_groups"] < 1e9]
        ids = [f"order_{g['order']}" for g in _smallgroups_cache
               if isinstance(g.get("n_groups"), int) and 0 < g["n_groups"] < 1e9]
        all_detrended["SmallGroups"] = detrend_array(vals, ids)
        print(f"    SmallGroups: {len(all_detrended['SmallGroups'])} detrended values")

    # LMFDB conductors
    try:
        con = _get_duck()
        rows = con.execute(
            "SELECT conductor, label FROM objects WHERE object_type='elliptic_curve' AND conductor <= 50000"
        ).fetchall()
        con.close()
        vals = [r[0] for r in rows]
        ids = [r[1] for r in rows]
        all_detrended["LMFDB"] = detrend_array(vals, ids)
        print(f"    LMFDB: {len(all_detrended['LMFDB'])} detrended values")
    except Exception:
        pass

    # Isogenies node counts
    from search_engine import ISOGENY_GRAPHS
    if ISOGENY_GRAPHS.exists():
        vals, ids = [], []
        for pdir in sorted(ISOGENY_GRAPHS.iterdir()):
            if pdir.is_dir():
                try:
                    p = int(pdir.name)
                    # Node count ~ (p-1)/12 for supersingular
                    node_count = (p - 1) // 12 + 1
                    vals.append(node_count)
                    ids.append(f"isogeny_p{p}")
                except ValueError:
                    pass
        if vals:
            all_detrended["Isogenies"] = detrend_array(vals, ids)
            print(f"    Isogenies: {len(all_detrended.get('Isogenies', []))} detrended values")

    return all_detrended


def build_detrended_concepts(all_detrended):
    """Build concept layer from detrended residual bins."""
    concepts = set()
    links = []

    for dataset, records in all_detrended.items():
        for rec in records:
            bin_label = f"dt_{dataset}_{rec['bin']}"
            concepts.add(bin_label)
            links.append({
                "concept": bin_label,
                "dataset": dataset,
                "object_id": rec["obj_id"],
                "relationship": "has_detrended_residual",
                "residual": rec["residual"],
            })

            # Also add cross-dataset residual bins (coarser, for bridging)
            # Map to 5 universal bins: very_low, low, neutral, high, very_high
            r = rec["residual"]
            if r < -1.0:
                universal = "dt_universal_very_low"
            elif r < -0.3:
                universal = "dt_universal_low"
            elif r < 0.3:
                universal = "dt_universal_neutral"
            elif r < 1.0:
                universal = "dt_universal_high"
            else:
                universal = "dt_universal_very_high"

            concepts.add(universal)
            links.append({
                "concept": universal,
                "dataset": dataset,
                "object_id": rec["obj_id"],
                "relationship": "has_universal_residual",
            })

    return concepts, links


def build_detrended_svd(all_detrended):
    """Build SVD bond dimensions on detrended residual values."""
    print("\n  Computing detrended SVD bond dimensions...")

    datasets = sorted(all_detrended.keys())
    n_ds = len(datasets)

    # For each pair: compare residual distributions
    bonds = {}
    for d1, d2 in combinations(datasets, 2):
        r1 = np.array([rec["residual"] for rec in all_detrended[d1]])
        r2 = np.array([rec["residual"] for rec in all_detrended[d2]])

        if len(r1) < 20 or len(r2) < 20:
            continue

        # Build cross-histogram (2D joint distribution of residuals)
        n_bins = 20
        h1, edges1 = np.histogram(r1, bins=n_bins, density=True)
        h2, edges2 = np.histogram(r2, bins=n_bins, density=True)

        # Cross-product matrix
        cross = np.outer(h1, h2)

        # SVD
        U, S, Vt = np.linalg.svd(cross)
        # Bond dimension at 95% energy
        total_energy = np.sum(S**2)
        if total_energy == 0:
            bond_dim = 0
        else:
            cumulative = np.cumsum(S**2) / total_energy
            bond_dim = int(np.searchsorted(cumulative, 0.95) + 1)

        # KS test on residual distributions
        n = min(len(r1), len(r2))
        ks_stat, ks_p = sp_stats.ks_2samp(r1[:n], r2[:n])

        # Mutual information on residuals
        hist2d, _, _ = np.histogram2d(r1[:n], r2[:n], bins=15)
        pxy = hist2d / max(hist2d.sum(), 1)
        px = pxy.sum(axis=1)
        py = pxy.sum(axis=0)
        mi = 0.0
        for i in range(15):
            for j in range(15):
                if pxy[i, j] > 0 and px[i] > 0 and py[j] > 0:
                    mi += pxy[i, j] * np.log2(pxy[i, j] / (px[i] * py[j]))

        pair_key = f"{d1}--{d2}"
        bonds[pair_key] = {
            "bond_dim": bond_dim,
            "top_sv": round(float(S[0]), 4) if len(S) > 0 else 0,
            "ks_stat": round(float(ks_stat), 4),
            "ks_p": round(float(ks_p), 6),
            "residual_mi": round(float(mi), 6),
            "distributions_match": ks_p > 0.05,
            "n1": len(r1),
            "n2": len(r2),
        }

        marker = ""
        if ks_p > 0.05:
            marker = " <-- DETRENDED MATCH"
        if mi > 0.1:
            marker += " HIGH_MI"

        print(f"    {pair_key:35s} bd={bond_dim:2d} sv={S[0]:7.4f} "
              f"KS_p={ks_p:.4f} MI={mi:.4f}{marker}")

    return bonds


def run_detrended_tensor(compare=False):
    """Build the full detrended tensor."""
    print("=" * 70)
    print("  DETRENDED TENSOR — The clean landscape")
    print("  Primes stripped. Small integers filtered. Residuals only.")
    print("=" * 70)

    t0 = time.time()

    # Extract and detrend
    all_detrended = extract_and_detrend()

    # Build concept layer
    print(f"\n  Building detrended concept layer...")
    concepts, links = build_detrended_concepts(all_detrended)
    print(f"  {len(concepts)} detrended concepts, {len(links)} links")

    # Save concepts and links
    with open(DETRENDED_CONCEPTS, "w") as f:
        for c in sorted(concepts):
            f.write(json.dumps({"id": c, "type": "detrended_residual"}) + "\n")
    with open(DETRENDED_LINKS, "w") as f:
        for link in links:
            f.write(json.dumps(link) + "\n")

    # Build SVD tensor on residuals
    bonds = build_detrended_svd(all_detrended)

    elapsed = time.time() - t0

    # Save tensor
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_s": round(elapsed, 1),
        "n_datasets": len(all_detrended),
        "n_concepts": len(concepts),
        "n_links": len(links),
        "bonds": bonds,
        "datasets": {ds: len(recs) for ds, recs in all_detrended.items()},
    }

    def _default(obj):
        if isinstance(obj, (np.integer, np.bool_)):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        return str(obj)

    with open(DETRENDED_TENSOR, "w") as f:
        json.dump(output, f, indent=2, default=_default)

    # Summary
    print(f"\n{'=' * 70}")
    print(f"  DETRENDED TENSOR COMPLETE in {elapsed:.1f}s")
    print(f"  Datasets: {len(all_detrended)}")
    print(f"  Concepts: {len(concepts)}, Links: {len(links)}")

    # Highlight matches
    matches = {k: v for k, v in bonds.items() if v.get("distributions_match")}
    high_mi = {k: v for k, v in bonds.items() if v.get("residual_mi", 0) > 0.05}

    if matches:
        print(f"\n  DETRENDED DISTRIBUTION MATCHES (residuals look the same):")
        for k, v in sorted(matches.items(), key=lambda x: -x[1]["ks_p"]):
            print(f"    {k:35s} KS_p={v['ks_p']:.4f} MI={v['residual_mi']:.4f}")

    if high_mi:
        print(f"\n  HIGH MUTUAL INFORMATION (non-linear residual correlation):")
        for k, v in sorted(high_mi.items(), key=lambda x: -x[1]["residual_mi"]):
            print(f"    {k:35s} MI={v['residual_mi']:.4f} bits")

    # Compare with raw tensor if requested
    if compare:
        raw_tensor_file = CONVERGENCE / "data" / "tensor_bridges.json"
        if raw_tensor_file.exists():
            raw = json.loads(raw_tensor_file.read_text())
            raw_bonds = raw.get("svd_bond_dimensions", {})
            print(f"\n  RAW vs DETRENDED comparison:")
            print(f"  {'Pair':35s} {'Raw BD':>7s} {'Det BD':>7s} {'Raw SV':>8s} {'Det SV':>8s} {'Det MI':>7s}")
            for pair_key in sorted(bonds.keys()):
                raw_b = raw_bonds.get(pair_key, {})
                det_b = bonds[pair_key]
                raw_bd = raw_b.get("bond_dim", "?")
                raw_sv = raw_b.get("top_singular_values", [0])[0] if raw_b.get("top_singular_values") else 0
                print(f"  {pair_key:35s} {str(raw_bd):>7s} {det_b['bond_dim']:>7d} "
                      f"{float(raw_sv):>8.1f} {det_b['top_sv']:>8.4f} {det_b['residual_mi']:>7.4f}")

    print(f"\n  Saved to {DETRENDED_TENSOR}")
    print(f"{'=' * 70}")

    return output


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Detrended Tensor")
    parser.add_argument("--compare", action="store_true", help="Compare with raw tensor")
    args = parser.parse_args()

    run_detrended_tensor(compare=args.compare)
