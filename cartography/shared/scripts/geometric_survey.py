"""
Geometric Survey — Run all geometric probes across all dataset pairs.
======================================================================
Extracts numerical arrays from every dataset, runs 13 probes (9 single,
4 pair), and builds a geometric fingerprint for the entire landscape.

Feeds the shadow tensor with structural signatures beyond correlation.

Usage:
    python geometric_survey.py                    # full survey
    python geometric_survey.py --focus Genus2     # one dataset
"""

import json
import sys
import time
import numpy as np
from collections import defaultdict
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from geometric_probes import run_single_probes, run_pair_probes

ROOT = Path(__file__).resolve().parents[3]
RESULTS_FILE = ROOT / "cartography" / "convergence" / "data" / "geometric_survey.json"


def extract_arrays():
    """Extract numerical arrays from all datasets."""
    arrays = {}

    # LMFDB conductors
    try:
        from search_engine import _get_duck
        con = _get_duck()
        rows = con.execute(
            "SELECT conductor FROM objects WHERE object_type='elliptic_curve' AND conductor <= 50000"
        ).fetchall()
        con.close()
        arrays["LMFDB_conductors"] = np.array([r[0] for r in rows], dtype=float)
    except Exception:
        pass

    # Genus-2
    try:
        from search_engine import _load_genus2, _genus2_cache
        _load_genus2()
        arrays["Genus2_conductors"] = np.array(
            [c["conductor"] for c in _genus2_cache[:5000] if c.get("conductor")], dtype=float)
    except Exception:
        pass

    # Maass
    try:
        from search_engine import _load_maass, _maass_cache
        _load_maass()
        arrays["Maass_spectral"] = np.array(
            [m["spectral_parameter"] for m in _maass_cache if m.get("spectral_parameter")], dtype=float)
    except Exception:
        pass

    # Lattices
    try:
        from search_engine import _load_lattices, _lattices_cache
        _load_lattices()
        arrays["Lattices_kissing"] = np.array(
            [l["kissing"] for l in _lattices_cache if l.get("kissing")], dtype=float)
        arrays["Lattices_dim"] = np.array(
            [l["dim"] for l in _lattices_cache if l.get("dim")], dtype=float)
    except Exception:
        pass

    # KnotInfo
    try:
        from search_engine import _load_knots, _knots_cache
        _load_knots()
        knot_list = _knots_cache.get("knots", [])
        arrays["KnotInfo_determinants"] = np.array(
            [k["determinant"] for k in knot_list
             if isinstance(k, dict) and k.get("determinant") and k["determinant"] > 0][:5000], dtype=float)
        arrays["KnotInfo_crossings"] = np.array(
            [k["crossing_number"] for k in knot_list
             if isinstance(k, dict) and k.get("crossing_number", 0) > 0][:5000], dtype=float)
    except Exception:
        pass

    # Number Fields
    try:
        from search_engine import _load_nf, _nf_cache
        _load_nf()
        arrays["NF_class_numbers"] = np.array(
            [int(f["class_number"]) for f in _nf_cache if f.get("class_number") and str(f["class_number"]).isdigit()][:5000], dtype=float)
        arrays["NF_discriminants"] = np.array(
            [abs(int(f["disc_abs"])) for f in _nf_cache
             if f.get("disc_abs") and str(f["disc_abs"]).lstrip("-").isdigit()][:5000], dtype=float)
    except Exception:
        pass

    # SmallGroups
    try:
        from search_engine import _load_smallgroups, _smallgroups_cache
        _load_smallgroups()
        arrays["SmallGroups_counts"] = np.array(
            [g["n_groups"] for g in _smallgroups_cache
             if g.get("n_groups") and isinstance(g["n_groups"], int) and g["n_groups"] < 1e9][:2000], dtype=float)
        arrays["SmallGroups_orders"] = np.array(
            [g["order"] for g in _smallgroups_cache if g.get("order")][:2000], dtype=float)
    except Exception:
        pass

    # Isogenies
    try:
        from search_engine import isogeny_stats
        istats = isogeny_stats()
        if istats and "data" in istats[0]:
            node_data = istats[0]["data"].get("node_counts_sample", [])
            if node_data:
                arrays["Isogenies_nodes"] = np.array(node_data, dtype=float)
    except Exception:
        pass

    # SpaceGroups
    try:
        from search_engine import _load_spacegroups, _sg_data
        _load_spacegroups()
        if _sg_data:
            orders = [sg.get("point_group_order", 0) for sg in _sg_data.values() if sg.get("point_group_order")]
            if orders:
                arrays["SpaceGroups_orders"] = np.array(orders, dtype=float)
    except Exception:
        pass

    # MMLKG reference degrees
    try:
        from search_engine import mmlkg_stats
        ms = mmlkg_stats()
        if ms and "data" in ms[0]:
            hubs = ms[0]["data"].get("top_articles", [])
            if hubs:
                arrays["MMLKG_degrees"] = np.array([h.get("degree", 0) for h in hubs], dtype=float)
    except Exception:
        pass

    # Materials
    try:
        from search_engine import _load_materials, _materials_cache
        _load_materials()
        if _materials_cache:
            bgs = [m.get("band_gap", 0) for m in _materials_cache if m.get("band_gap") is not None]
            if bgs:
                arrays["Materials_bandgaps"] = np.array(bgs, dtype=float)
    except Exception:
        pass

    return arrays


def run_survey(focus_dataset=None):
    """Run the full geometric survey."""
    print("=" * 70)
    print("  GEOMETRIC SURVEY")
    print("  13 probes x all dataset pairs")
    print("=" * 70)

    t0 = time.time()

    print("\n  Extracting numerical arrays...")
    arrays = extract_arrays()
    print(f"  Extracted {len(arrays)} arrays:")
    for name, arr in sorted(arrays.items()):
        print(f"    {name:30s}: {len(arr):6d} values, range [{arr.min():.1f}, {arr.max():.1f}]")

    if focus_dataset:
        array_names = [k for k in arrays if focus_dataset in k]
    else:
        array_names = list(arrays.keys())

    # Single-array probes
    print(f"\n  Running single-array probes on {len(array_names)} arrays...")
    single_results = {}
    for name in array_names:
        single_results[name] = run_single_probes(arrays[name], name)

    # Pair probes
    pairs = list(combinations(array_names, 2))
    print(f"  Running pair probes on {len(pairs)} pairs...")

    pair_results = {}
    for name_a, name_b in pairs:
        key = f"{name_a}--{name_b}"
        pair_results[key] = run_pair_probes(arrays[name_a], arrays[name_b], name_a, name_b)

    elapsed = time.time() - t0

    # Compile results
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_s": round(elapsed, 1),
        "n_arrays": len(arrays),
        "n_pairs": len(pairs),
        "single_probes": single_results,
        "pair_probes": pair_results,
    }

    # JSON serialization helper
    def _default(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return str(obj)

    with open(RESULTS_FILE, "w") as f:
        json.dump(output, f, indent=2, default=_default)

    # Summary
    print(f"\n{'=' * 70}")
    print(f"  GEOMETRIC SURVEY COMPLETE in {elapsed:.1f}s")
    print(f"  Arrays: {len(arrays)}, Pairs: {len(pairs)}")

    # Highlight interesting findings
    print(f"\n  === INTERESTING SINGLE-ARRAY SIGNATURES ===")
    for name, probes in single_results.items():
        benford = probes.get("benford", {})
        if benford and benford.get("follows_benford"):
            print(f"    {name:30s} FOLLOWS Benford's law (p={benford['p_value']:.3f})")
        growth = probes.get("growth_shape", {})
        if growth:
            print(f"    {name:30s} best fit: {growth['best_fit']} "
                  f"(poly_degree={growth.get('poly_degree','?')}, r2={growth.get('r2_polynomial','?')})")

    print(f"\n  === INTERESTING PAIR SIGNATURES ===")
    # Sort pairs by mutual information
    mi_pairs = []
    for key, probes in pair_results.items():
        mi = probes.get("mutual_info", {})
        if mi:
            mi_pairs.append((key, mi.get("normalized_mi", 0), mi.get("mi_bits", 0)))

    mi_pairs.sort(key=lambda x: -x[1])
    print(f"  Top 10 by mutual information:")
    for key, nmi, mi in mi_pairs[:10]:
        print(f"    {key:50s} NMI={nmi:.4f} MI={mi:.4f} bits")

    # Wasserstein similarities
    w_pairs = []
    for key, probes in pair_results.items():
        w = probes.get("wasserstein", {})
        if w:
            w_pairs.append((key, w.get("w1_distance", 99), w.get("distributions_same", False)))

    w_pairs.sort(key=lambda x: x[1])
    print(f"\n  Most similar distributions (Wasserstein):")
    for key, w1, same in w_pairs[:10]:
        print(f"    {key:50s} W1={w1:.4f} {'SAME' if same else ''}")

    # Spectral coherence
    sc_pairs = []
    for key, probes in pair_results.items():
        sc = probes.get("spectral_cross", {})
        if sc:
            sc_pairs.append((key, sc.get("mean_coherence", 0), sc.get("max_coherence", 0)))

    sc_pairs.sort(key=lambda x: -x[1])
    print(f"\n  Top spectral coherence:")
    for key, mean_c, max_c in sc_pairs[:10]:
        print(f"    {key:50s} mean={mean_c:.4f} max={max_c:.4f}")

    print(f"\n  Results saved to {RESULTS_FILE}")
    print(f"{'=' * 70}")

    return output


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Geometric Survey")
    parser.add_argument("--focus", type=str, default=None, help="Focus on one dataset")
    args = parser.parse_args()

    run_survey(focus_dataset=args.focus)
