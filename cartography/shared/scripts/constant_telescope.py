"""
Constant Telescope — Scan for universal constants in cross-domain ratios.
==========================================================================
Mathematical constants are fixed points of the landscape. If a ratio of
properties from two different datasets matches a known constant, that
constant is the bridge.

Three scans:
  1. CROSS-DATASET RATIOS: For each dataset pair with numerical data,
     compute ratios of statistical summaries (means, medians, std devs)
     and check against 83 known constants.

  2. CONVERGENCE RATES: For each OEIS sleeping beauty, compute the
     ratio of consecutive terms (a(n+1)/a(n)) and the nth-root limit.
     Match against constants. A sleeper whose growth rate IS a constant
     is a bridge to that constant's home domain.

  3. SHADOW TENSOR RESIDUALS: For each hot cell, take the near-miss
     test statistics (rho, d, p) and compute ratios between them.
     If residuals cluster around a constant, that constant is the
     normalizing factor the battery is missing.

Usage:
    python constant_telescope.py                   # full scan
    python constant_telescope.py --sleepers 1000   # scan 1000 sleepers
    python constant_telescope.py --pairs-only      # only cross-dataset ratios
"""

import json
import math
import sys
import time
import numpy as np
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from constant_matcher import identify_constant, LOCAL_CONSTANTS

ROOT = Path(__file__).resolve().parents[3]
CONVERGENCE = ROOT / "cartography" / "convergence"
SHADOW_FILE = CONVERGENCE / "data" / "shadow_tensor.json"
RESULTS_FILE = CONVERGENCE / "data" / "constant_telescope_results.json"


def scan_cross_dataset_ratios():
    """Scan ratios of numerical properties between dataset pairs."""
    print("\n  === SCAN 1: Cross-Dataset Ratios ===")

    from search_engine import (
        _load_genus2, _load_maass, _load_lattices, _load_knots, _load_nf,
        _load_materials, _load_oeis, _oeis_cache,
        _genus2_cache, _maass_cache, _lattices_cache, _knots_cache,
    )

    # Load datasets and extract key numerical arrays
    datasets = {}

    _load_genus2()
    if _genus2_cache:
        conds = [c["conductor"] for c in _genus2_cache if c.get("conductor")]
        datasets["Genus2_conductors"] = np.array(conds[:5000], dtype=float)

    _load_maass()
    if _maass_cache:
        spectral = [m["spectral_parameter"] for m in _maass_cache if m.get("spectral_parameter")]
        datasets["Maass_spectral"] = np.array(spectral, dtype=float)

    _load_lattices()
    if _lattices_cache:
        kissing = [l["kissing"] for l in _lattices_cache if l.get("kissing")]
        dims = [l["dim"] for l in _lattices_cache if l.get("dim")]
        dets = [l["det"] for l in _lattices_cache if l.get("det")]
        datasets["Lattices_kissing"] = np.array(kissing, dtype=float)
        datasets["Lattices_dim"] = np.array(dims, dtype=float)
        datasets["Lattices_det"] = np.array(dets, dtype=float)

    _load_knots()
    if _knots_cache:
        knot_list = _knots_cache.get("knots", _knots_cache) if isinstance(_knots_cache, dict) else _knots_cache
        knot_dets = [k["determinant"] for k in knot_list if isinstance(k, dict) and k.get("determinant") and k["determinant"] > 0]
        datasets["KnotInfo_determinants"] = np.array(knot_dets[:5000], dtype=float)

    _load_nf()
    from search_engine import _nf_cache
    if _nf_cache:
        class_nums = [f["class_number"] for f in _nf_cache if f.get("class_number")]
        disc_abs = [abs(int(f["disc_abs"])) for f in _nf_cache if f.get("disc_abs") and str(f["disc_abs"]).lstrip("-").isdigit()]
        datasets["NF_class_numbers"] = np.array(class_nums[:5000], dtype=float)
        datasets["NF_discriminants"] = np.array(disc_abs[:5000], dtype=float)

    print(f"    Loaded {len(datasets)} numerical arrays")

    # Compute ratios of summary statistics between all pairs
    hits = []
    ds_names = sorted(datasets.keys())

    for i, name_a in enumerate(ds_names):
        for name_b in ds_names[i+1:]:
            a = datasets[name_a]
            b = datasets[name_b]

            # Compute candidate ratios
            stats_a = {
                "mean": np.mean(a), "median": np.median(a),
                "std": np.std(a), "max": np.max(a), "min": np.min(a[a > 0]) if np.any(a > 0) else 1,
            }
            stats_b = {
                "mean": np.mean(b), "median": np.median(b),
                "std": np.std(b), "max": np.max(b), "min": np.min(b[b > 0]) if np.any(b > 0) else 1,
            }

            for sa_name, sa_val in stats_a.items():
                for sb_name, sb_val in stats_b.items():
                    if sb_val == 0 or sa_val == 0:
                        continue
                    ratio = sa_val / sb_val
                    if ratio <= 0 or not np.isfinite(ratio):
                        continue

                    # Check ratio and its log against constants
                    for val, label in [(ratio, "ratio"), (math.log(ratio), "log_ratio"),
                                       (math.sqrt(abs(ratio)), "sqrt_ratio")]:
                        if not np.isfinite(val) or abs(val) > 100:
                            continue
                        matches = identify_constant(val, tolerance=1e-4, use_ries=False)
                        for m in matches[:1]:  # best match only
                            if m.confidence > 0.99:
                                hits.append({
                                    "type": "cross_dataset_ratio",
                                    "dataset_a": name_a,
                                    "stat_a": sa_name,
                                    "val_a": round(sa_val, 6),
                                    "dataset_b": name_b,
                                    "stat_b": sb_name,
                                    "val_b": round(sb_val, 6),
                                    "transform": label,
                                    "value": round(val, 10),
                                    "constant": m.name,
                                    "residual": m.residual,
                                    "confidence": m.confidence,
                                })

    print(f"    Found {len(hits)} constant matches in cross-dataset ratios")
    return hits


def scan_sleeper_convergence(max_sleepers=5000):
    """Scan sleeping beauty sequences for convergence to known constants."""
    print(f"\n  === SCAN 2: Sleeper Convergence Rates (max {max_sleepers}) ===")

    from search_engine import _load_oeis, _oeis_cache

    _load_oeis()
    if not _oeis_cache:
        print("    OEIS not loaded")
        return []

    # Use the sleeping beauty search function to get high-entropy low-connectivity sequences
    # Fall back to random OEIS sequences if search unavailable
    try:
        from search_engine import oeis_sleeping_beauties
        beauties = oeis_sleeping_beauties(min_entropy=3.5, max_degree=3, max_results=max_sleepers)
        sleeper_ids = [b["id"] for b in beauties if "id" in b]
    except Exception:
        sleeper_ids = []

    if not sleeper_ids:
        # Sample from OEIS cache — prefer sequences with 15+ terms
        candidates = [(sid, terms) for sid, terms in _oeis_cache.items() if len(terms) >= 15]
        import random
        random.seed(42)
        random.shuffle(candidates)
        sleeper_ids = [sid for sid, _ in candidates[:max_sleepers]]

    print(f"    Scanning {len(sleeper_ids)} sleeper sequences")

    hits = []
    scanned = 0

    for seq_id in sleeper_ids:
        terms = _oeis_cache.get(seq_id)
        if not terms or len(terms) < 10:
            continue

        scanned += 1
        pos_terms = [t for t in terms if t > 0]

        if len(pos_terms) < 8:
            continue

        # Convergence rate: ratio of consecutive terms
        ratios = []
        for i in range(len(pos_terms) - 1):
            if pos_terms[i] > 0:
                ratios.append(pos_terms[i+1] / pos_terms[i])

        if not ratios:
            continue

        # Check various convergence indicators
        candidates = []

        # Limiting ratio (last 5 ratios averaged)
        if len(ratios) >= 5:
            tail_ratio = np.mean(ratios[-5:])
            if 0.1 < tail_ratio < 100 and np.isfinite(tail_ratio):
                candidates.append(("tail_ratio", tail_ratio))

        # Nth root limit: a(n)^(1/n)
        last = pos_terms[-1]
        n = len(pos_terms)
        if last > 0 and n > 5:
            nth_root = last ** (1.0 / n)
            if 0.1 < nth_root < 100 and np.isfinite(nth_root):
                candidates.append(("nth_root", nth_root))

        # Second differences ratio (for polynomial sequences)
        if len(pos_terms) >= 6:
            diffs1 = np.diff(pos_terms[:20])
            pos_diffs = [d for d in diffs1 if d > 0]
            if len(pos_diffs) >= 4:
                diff_ratios = [pos_diffs[i+1] / pos_diffs[i] for i in range(len(pos_diffs)-1) if pos_diffs[i] > 0]
                if diff_ratios:
                    tail_diff = np.mean(diff_ratios[-3:]) if len(diff_ratios) >= 3 else diff_ratios[-1]
                    if 0.1 < tail_diff < 100 and np.isfinite(tail_diff):
                        candidates.append(("diff_ratio", tail_diff))

        # Match each candidate against constants
        for ctype, cval in candidates:
            matches = identify_constant(cval, tolerance=1e-3, use_ries=False)
            for m in matches[:1]:
                if m.confidence > 0.95:
                    hits.append({
                        "type": "sleeper_convergence",
                        "seq_id": seq_id,
                        "convergence_type": ctype,
                        "value": round(cval, 10),
                        "constant": m.name,
                        "residual": m.residual,
                        "confidence": m.confidence,
                        "n_terms": len(pos_terms),
                    })

    print(f"    Scanned {scanned} sequences, found {len(hits)} constant matches")
    return hits


def scan_shadow_residuals():
    """Scan shadow tensor hot cells for constant signatures in test statistics."""
    print("\n  === SCAN 3: Shadow Tensor Residuals ===")

    if not SHADOW_FILE.exists():
        print("    Shadow tensor not found. Run shadow_tensor.py first.")
        return []

    shadow = json.loads(SHADOW_FILE.read_text(encoding="utf-8"))
    cells = shadow.get("cells", {})

    hits = []

    for pair, cell in cells.items():
        p_vals = cell.get("p_values", [])
        z_scores = cell.get("z_scores", [])

        if len(p_vals) < 5:
            continue

        p_arr = np.array([p for p in p_vals if 0 < p < 1])
        z_arr = np.array([z for z in z_scores if np.isfinite(z) and z != 0])

        if len(p_arr) < 3:
            continue

        # Compute candidate values from the cell's statistics
        candidates = []

        # Mean -log10(p): the "gravitational pull" of the cell
        mean_logp = np.mean(-np.log10(p_arr + 1e-15))
        if 0.1 < mean_logp < 50:
            candidates.append(("mean_neg_log10_p", mean_logp))

        # Ratio of best_z to median_z
        if len(z_arr) >= 3:
            median_z = np.median(np.abs(z_arr))
            best_z = np.max(np.abs(z_arr))
            if median_z > 0.1:
                candidates.append(("best_z_over_median_z", best_z / median_z))

        # Std of p-values (how variable is the signal?)
        if np.std(p_arr) > 0:
            candidates.append(("p_std_over_mean", np.std(p_arr) / np.mean(p_arr)))

        for ctype, cval in candidates:
            if not np.isfinite(cval) or abs(cval) > 100:
                continue
            matches = identify_constant(cval, tolerance=1e-3, use_ries=False)
            for m in matches[:1]:
                if m.confidence > 0.95:
                    hits.append({
                        "type": "shadow_residual",
                        "pair": pair,
                        "metric": ctype,
                        "value": round(cval, 10),
                        "constant": m.name,
                        "residual": m.residual,
                        "confidence": m.confidence,
                        "n_tests": cell.get("n_tested", 0),
                    })

    print(f"    Scanned {len(cells)} cells, found {len(hits)} constant matches")
    return hits


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Constant Telescope")
    parser.add_argument("--sleepers", type=int, default=5000, help="Max sleepers to scan")
    parser.add_argument("--pairs-only", action="store_true", help="Only cross-dataset ratios")
    parser.add_argument("--sleepers-only", action="store_true", help="Only sleeper convergence")
    parser.add_argument("--shadow-only", action="store_true", help="Only shadow residuals")
    args = parser.parse_args()

    print("=" * 70)
    print("  CONSTANT TELESCOPE")
    print("  Scanning for universal constants in cross-domain ratios")
    print("=" * 70)

    t0 = time.time()
    all_hits = []

    if not args.sleepers_only and not args.shadow_only:
        hits = scan_cross_dataset_ratios()
        all_hits.extend(hits)

    if not args.pairs_only and not args.shadow_only:
        hits = scan_sleeper_convergence(max_sleepers=args.sleepers)
        all_hits.extend(hits)

    if not args.pairs_only and not args.sleepers_only:
        hits = scan_shadow_residuals()
        all_hits.extend(hits)

    elapsed = time.time() - t0

    # Save results
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed_s": round(elapsed, 1),
            "total_hits": len(all_hits),
            "hits": all_hits,
        }, f, indent=2)

    # Summary
    print(f"\n{'=' * 70}")
    print(f"  CONSTANT TELESCOPE COMPLETE in {elapsed:.1f}s")
    print(f"  Total hits: {len(all_hits)}")

    if all_hits:
        # Group by constant
        by_constant = defaultdict(list)
        for h in all_hits:
            by_constant[h["constant"]].append(h)

        print(f"\n  Constants detected ({len(by_constant)} unique):")
        for const, hits in sorted(by_constant.items(), key=lambda x: -len(x[1])):
            types = set(h["type"] for h in hits)
            print(f"    {const:35s} {len(hits):3d} hits  ({', '.join(types)})")

        # Show most interesting hits (cross-dataset with high confidence)
        cross = [h for h in all_hits if h["type"] == "cross_dataset_ratio"]
        if cross:
            print(f"\n  Cross-dataset constant bridges:")
            for h in sorted(cross, key=lambda x: -x["confidence"])[:10]:
                print(f"    {h['constant']:30s} = {h['dataset_a']}.{h['stat_a']} / {h['dataset_b']}.{h['stat_b']}"
                      f"  (val={h['value']:.6f}, conf={h['confidence']:.4f})")

        sleepers = [h for h in all_hits if h["type"] == "sleeper_convergence"]
        if sleepers:
            print(f"\n  Sleeper sequences encoding constants:")
            by_const = defaultdict(list)
            for h in sleepers:
                by_const[h["constant"]].append(h)
            for const, hits in sorted(by_const.items(), key=lambda x: -len(x[1]))[:10]:
                seqs = [h["seq_id"] for h in hits[:5]]
                print(f"    {const:30s} {len(hits):4d} sleepers  (e.g. {', '.join(seqs)})")

    print(f"\n  Results saved to {RESULTS_FILE}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
