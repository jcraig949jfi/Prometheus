"""
Formula Tree Survey — Structural census of the 27M parsed formula trees.
=========================================================================
Samples trees, computes structural statistics, looks for anomalous clusters
of formulas that share unusual operator patterns across mathematical domains.

Usage:
    python formula_survey.py                    # 100K sample
    python formula_survey.py --sample 500000    # bigger sample
"""

import argparse
import json
import sys
import time
import random
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
TREES_FILE = ROOT / "cartography" / "convergence" / "data" / "formula_trees.jsonl"
FORMULAS_FILE = ROOT / "cartography" / "convergence" / "data" / "openwebmath_formulas.jsonl"
OUT_FILE = ROOT / "cartography" / "convergence" / "data" / "formula_survey.json"


def _extract_operators(node, ops=None):
    """Recursively extract all operators from a tree."""
    if ops is None:
        ops = []
    if isinstance(node, dict):
        if node.get("type") in ("operator", "equation"):
            op = node.get("op", "")
            if op:
                ops.append(op)
        for child in node.get("children", []):
            _extract_operators(child, ops)
    return ops


def _tree_depth(node):
    if not isinstance(node, dict):
        return 0
    children = node.get("children", [])
    if not children:
        return 1
    return 1 + max(_tree_depth(c) for c in children)


def _tree_size(node):
    if not isinstance(node, dict):
        return 1
    return 1 + sum(_tree_size(c) for c in node.get("children", []))


def survey(sample_size=100000):
    print("=" * 70)
    print(f"  Formula Tree Survey — sampling {sample_size:,} trees")
    print("=" * 70)

    t0 = time.time()

    # Load domain info from formulas file (hash -> domain)
    print("  Loading domain mappings...")
    hash_to_domain = {}
    if FORMULAS_FILE.exists():
        with open(FORMULAS_FILE) as f:
            for i, line in enumerate(f):
                if i >= sample_size * 3:  # read enough to cover our sample
                    break
                try:
                    d = json.loads(line)
                    domains = d.get("domains", ["unknown"])
                    hash_to_domain[d["hash"]] = domains[0] if domains else "unknown"
                except Exception:
                    pass
    print(f"  {len(hash_to_domain):,} domain mappings loaded")

    # Sample trees using reservoir sampling
    print(f"  Sampling {sample_size:,} trees from {TREES_FILE.name}...")
    reservoir = []
    n_total = 0

    with open(TREES_FILE) as f:
        for line in f:
            n_total += 1
            if len(reservoir) < sample_size:
                reservoir.append(line)
            else:
                j = random.randint(0, n_total - 1)
                if j < sample_size:
                    reservoir[j] = line

            if n_total % 1000000 == 0:
                print(f"    scanned {n_total // 1000000}M...")

    print(f"  Sampled {len(reservoir):,} from {n_total:,} total")

    # Analyze
    print("  Analyzing trees...")
    op_counts = Counter()
    depth_hist = Counter()
    size_hist = Counter()
    domain_op_matrix = defaultdict(Counter)  # domain -> operator -> count
    op_pairs = Counter()  # co-occurring operator pairs
    rare_ops = Counter()
    deep_formulas = []
    large_formulas = []

    for line in reservoir:
        try:
            tree = json.loads(line)
        except Exception:
            continue

        root = tree.get("root", {})
        h = tree.get("hash", "")
        ops = _extract_operators(root)
        depth = tree.get("depth", _tree_depth(root))
        size = tree.get("n_nodes", _tree_size(root))

        # Operator counts
        for op in ops:
            op_counts[op] += 1

        # Depth/size histograms
        depth_hist[min(depth, 50)] += 1
        size_hist[min(size, 200)] += 1

        # Domain-operator matrix
        domain = hash_to_domain.get(h, "unknown")
        for op in set(ops):
            domain_op_matrix[domain][op] += 1

        # Co-occurring pairs
        unique_ops = sorted(set(ops))
        for i in range(len(unique_ops)):
            for j in range(i + 1, min(i + 5, len(unique_ops))):
                op_pairs[(unique_ops[i], unique_ops[j])] += 1

        # Track extreme formulas
        if depth >= 15:
            deep_formulas.append({"hash": h, "depth": depth, "ops": ops[:20], "domain": domain})
        if size >= 100:
            large_formulas.append({"hash": h, "size": size, "n_ops": len(ops), "domain": domain})

    elapsed = time.time() - t0

    # Compute cross-domain operator signatures
    # Which operators appear in unexpected domains?
    print("  Computing cross-domain signatures...")
    domain_totals = {d: sum(c.values()) for d, c in domain_op_matrix.items()}
    cross_domain_ops = []
    for op in op_counts.most_common(50):
        op_name = op[0]
        domains_with_op = {d for d, c in domain_op_matrix.items() if c[op_name] > 0}
        if len(domains_with_op) >= 3:
            domain_rates = {}
            for d in domains_with_op:
                rate = domain_op_matrix[d][op_name] / max(domain_totals[d], 1)
                domain_rates[d] = round(rate, 4)
            cross_domain_ops.append({
                "operator": op_name,
                "total_count": op[1],
                "n_domains": len(domains_with_op),
                "domain_rates": domain_rates,
            })

    # Find domain-specific operators (appear in only 1 domain)
    domain_specific = []
    for op, count in op_counts.most_common(200):
        domains_with = [d for d, c in domain_op_matrix.items() if c[op] > 5]
        if len(domains_with) == 1 and count > 50:
            domain_specific.append({
                "operator": op,
                "domain": domains_with[0],
                "count": count,
            })

    # Results
    results = {
        "sample_size": len(reservoir),
        "total_formulas": n_total,
        "elapsed_s": round(elapsed, 1),
        "top_operators": op_counts.most_common(30),
        "depth_distribution": {str(k): v for k, v in sorted(depth_hist.items())},
        "mean_depth": round(np.mean([k for k, v in depth_hist.items() for _ in range(v)]), 1),
        "mean_size": round(np.mean([k for k, v in size_hist.items() for _ in range(v)]), 1),
        "n_deep_formulas": len(deep_formulas),
        "n_large_formulas": len(large_formulas),
        "cross_domain_operators": cross_domain_ops[:20],
        "domain_specific_operators": domain_specific[:20],
        "top_operator_pairs": [{"pair": list(p), "count": c} for p, c in op_pairs.most_common(20)],
        "domain_formula_counts": {d: sum(c.values()) for d, c in sorted(domain_op_matrix.items())},
    }

    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    print(f"\n{'=' * 70}")
    print(f"  FORMULA TREE SURVEY COMPLETE")
    print(f"  Sample: {len(reservoir):,} / {n_total:,} total")
    print(f"  Time: {elapsed:.1f}s")
    print(f"\n  Mean depth: {results['mean_depth']}")
    print(f"  Mean size: {results['mean_size']} nodes")
    print(f"  Deep (>15): {len(deep_formulas)}")
    print(f"  Large (>100 nodes): {len(large_formulas)}")

    print(f"\n  Top 15 operators:")
    for op, count in op_counts.most_common(15):
        pct = count / len(reservoir) * 100
        print(f"    {op:20s} {count:>8,} ({pct:.1f}%)")

    print(f"\n  Domain distribution:")
    for d, count in sorted(results["domain_formula_counts"].items(), key=lambda x: -x[1])[:10]:
        print(f"    {d:20s} {count:>8,}")

    print(f"\n  Cross-domain operators (span 3+ domains):")
    for cdo in cross_domain_ops[:10]:
        doms = ", ".join(f"{d}:{r:.3f}" for d, r in sorted(cdo["domain_rates"].items(), key=lambda x: -x[1])[:4])
        print(f"    {cdo['operator']:20s} n={cdo['total_count']:>6,} [{cdo['n_domains']} domains] {doms}")

    if domain_specific:
        print(f"\n  Domain-specific operators (1 domain only):")
        for ds in domain_specific[:10]:
            print(f"    {ds['operator']:20s} {ds['domain']:15s} n={ds['count']}")

    print(f"\n  Output: {OUT_FILE}")
    print(f"{'=' * 70}")


def main():
    parser = argparse.ArgumentParser(description="Formula Tree Survey")
    parser.add_argument("--sample", type=int, default=100000, help="Sample size (default: 100K)")
    args = parser.parse_args()
    survey(sample_size=args.sample)


if __name__ == "__main__":
    main()
