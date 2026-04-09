"""
AST Bridge — Cross-module formula similarity via symbol overlap.
================================================================
Computes pairwise Jaccard similarity between Fungrim formulas from
different modules, finds clusters of structurally similar formulas
across mathematical domains.

Usage:
    python ast_bridge.py                    # full scan
    python ast_bridge.py --top 200          # top N bridges
    python ast_bridge.py --min-jaccard 0.8  # stricter threshold
"""

import argparse
import json
import sys
import time
import numpy as np
from collections import defaultdict
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
FUNGRIM_JSON = ROOT / "cartography" / "fungrim" / "data" / "fungrim_index.json"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_BRIDGES = OUT_DIR / "ast_bridges.jsonl"
OUT_MODULE_PAIRS = OUT_DIR / "ast_module_pairs.json"


def load_formulas():
    """Load Fungrim formula index."""
    print(f"Loading {FUNGRIM_JSON} ...")
    with open(FUNGRIM_JSON) as f:
        data = json.load(f)
    formulas = data["formulas"]
    print(f"  {len(formulas)} formulas, {data.get('n_modules', '?')} modules")
    return formulas


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def build_module_index(formulas):
    """Group formulas by module."""
    by_module = defaultdict(list)
    for f in formulas:
        by_module[f["module"]].append(f)
    return dict(by_module)


def find_cross_module_bridges(formulas, min_jaccard=0.7, top_n=500):
    """Find formula pairs from different modules with high symbol overlap."""
    t0 = time.time()

    # Index by module
    by_module = build_module_index(formulas)
    modules = sorted(by_module.keys())
    print(f"  {len(modules)} modules")

    # Precompute symbol sets
    sym_sets = {}
    for f in formulas:
        sym_sets[f["id"]] = set(f["symbols"])

    # Cross-module pairs: only compare across different modules
    bridges = []
    n_compared = 0
    module_pairs = list(combinations(modules, 2))
    print(f"  {len(module_pairs)} module pairs to scan")

    for i, (m1, m2) in enumerate(module_pairs):
        if i % 500 == 0 and i > 0:
            print(f"    pair {i}/{len(module_pairs)}, {len(bridges)} bridges so far")

        fs1 = by_module[m1]
        fs2 = by_module[m2]

        for f1 in fs1:
            s1 = sym_sets[f1["id"]]
            if len(s1) < 2:
                continue
            for f2 in fs2:
                s2 = sym_sets[f2["id"]]
                if len(s2) < 2:
                    continue
                n_compared += 1
                j = jaccard(s1, s2)
                if j >= min_jaccard:
                    # Bridge score: jaccard * module_distance_weight
                    # Different modules -> distance >= 2
                    bridge_score = j * 0.5  # 1/module_distance, distance=2 for different modules
                    bridges.append({
                        "id_a": f1["id"],
                        "id_b": f2["id"],
                        "module_a": m1,
                        "module_b": m2,
                        "type_a": f1["type"],
                        "type_b": f2["type"],
                        "symbols_a": f1["symbols"],
                        "symbols_b": f2["symbols"],
                        "shared_symbols": sorted(s1 & s2),
                        "jaccard": round(j, 4),
                        "bridge_score": round(bridge_score, 4),
                    })

    bridges.sort(key=lambda x: x["bridge_score"], reverse=True)
    bridges = bridges[:top_n]

    elapsed = time.time() - t0
    print(f"  {n_compared:,} pairs compared in {elapsed:.1f}s")
    print(f"  {len(bridges)} bridges found (jaccard >= {min_jaccard})")
    return bridges


def compute_module_pair_stats(formulas):
    """Average Jaccard between all module pairs."""
    t0 = time.time()
    by_module = build_module_index(formulas)
    modules = sorted(by_module.keys())

    # Precompute symbol sets
    sym_sets = {}
    for f in formulas:
        sym_sets[f["id"]] = set(f["symbols"])

    pair_stats = []
    for m1, m2 in combinations(modules, 2):
        fs1 = by_module[m1]
        fs2 = by_module[m2]

        jaccards = []
        for f1 in fs1:
            s1 = sym_sets[f1["id"]]
            if len(s1) < 2:
                continue
            for f2 in fs2:
                s2 = sym_sets[f2["id"]]
                if len(s2) < 2:
                    continue
                jaccards.append(jaccard(s1, s2))

        if not jaccards:
            continue

        avg_j = float(np.mean(jaccards))
        max_j = float(np.max(jaccards))
        n_high = sum(1 for j in jaccards if j >= 0.5)

        pair_stats.append({
            "module_a": m1,
            "module_b": m2,
            "n_pairs": len(jaccards),
            "avg_jaccard": round(avg_j, 4),
            "max_jaccard": round(max_j, 4),
            "n_above_50pct": n_high,
        })

    # Sort by avg jaccard descending
    pair_stats.sort(key=lambda x: x["avg_jaccard"], reverse=True)
    elapsed = time.time() - t0
    print(f"  Module-pair stats: {len(pair_stats)} pairs in {elapsed:.1f}s")
    return pair_stats


def save_bridges(bridges, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for b in bridges:
            f.write(json.dumps(b) + "\n")
    print(f"  Wrote {len(bridges)} bridges to {path}")


def save_module_pairs(pair_stats, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Flag unexpected overlaps: pairs with avg_jaccard > global mean + 2*std
    jaccards = [p["avg_jaccard"] for p in pair_stats]
    if jaccards:
        mean_j = float(np.mean(jaccards))
        std_j = float(np.std(jaccards))
        threshold = mean_j + 2 * std_j
        for p in pair_stats:
            p["unexpected"] = p["avg_jaccard"] > threshold
        n_unexpected = sum(1 for p in pair_stats if p["unexpected"])
    else:
        threshold = 0.0
        n_unexpected = 0

    out = {
        "n_pairs": len(pair_stats),
        "mean_jaccard": round(float(np.mean(jaccards)) if jaccards else 0, 4),
        "std_jaccard": round(float(np.std(jaccards)) if jaccards else 0, 4),
        "unexpected_threshold": round(threshold, 4),
        "n_unexpected": n_unexpected,
        "pairs": pair_stats,
    }
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"  Wrote module-pair stats to {path}")
    return n_unexpected


def main():
    parser = argparse.ArgumentParser(description="AST Bridge — cross-module formula similarity")
    parser.add_argument("--min-jaccard", type=float, default=0.7,
                        help="Minimum Jaccard for a bridge (default: 0.7)")
    parser.add_argument("--top", type=int, default=500,
                        help="Keep top N bridges (default: 500)")
    args = parser.parse_args()

    t_start = time.time()

    formulas = load_formulas()

    print("\n--- Cross-module bridge scan ---")
    bridges = find_cross_module_bridges(formulas, min_jaccard=args.min_jaccard, top_n=args.top)
    save_bridges(bridges, OUT_BRIDGES)

    print("\n--- Module-pair statistics ---")
    pair_stats = compute_module_pair_stats(formulas)
    n_unexpected = save_module_pairs(pair_stats, OUT_MODULE_PAIRS)

    # Summary
    elapsed = time.time() - t_start
    print(f"\n{'='*60}")
    print(f"AST Bridge Summary")
    print(f"  Formulas analyzed: {len(formulas)}")
    print(f"  Bridges found (jaccard >= {args.min_jaccard}): {len(bridges)}")
    if bridges:
        print(f"  Top bridge: {bridges[0]['module_a']} <-> {bridges[0]['module_b']} "
              f"(jaccard={bridges[0]['jaccard']})")
    print(f"  Module pairs with unexpected overlap: {n_unexpected}")
    print(f"  Total time: {elapsed:.1f}s")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
