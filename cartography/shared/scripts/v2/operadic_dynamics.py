"""
Operadic Skeleton Dynamics — Rewrite Distance Between Domains (C12)
====================================================================
Computes rewrite distances between Fungrim formula skeletons to find:
1. Within-module vs between-module distance ratios
2. Narrowest cross-domain bridges (minimum-edit formula pairs)
3. Conserved universal operator patterns across modules

Uses symbol multisets from Fungrim index as operadic fingerprints.
Distance metric: weighted Jaccard on symbol multisets, separating
structural operators from domain-specific functions.

Usage:
    python operadic_dynamics.py
"""

import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from itertools import combinations
import random

ROOT = Path(__file__).resolve().parents[4]
FUNGRIM_INDEX = ROOT / "cartography" / "fungrim" / "data" / "fungrim_index.json"
OUT_FILE = Path(__file__).resolve().parent / "operadic_dynamics_results.json"

# ── Operator classification ───────────────────────────────────────────

# Structural operators (the "verbs" of mathematics)
STRUCTURAL_OPS = {
    "Add", "Sub", "Mul", "Div", "Pow", "Neg", "Pos", "Abs",
    "Sum", "Product", "Integral", "ComplexDerivative", "Derivative",
    "Limit", "SequenceLimit", "RealLimit", "ComplexLimit",
    "Equal", "NotEqual", "Less", "LessEqual", "Greater", "GreaterEqual",
    "And", "Or", "Not", "Implies", "Equivalent",
    "For", "ForElement", "Def", "Where", "Cases",
    "Set", "SetMinus", "Union", "Intersection", "Element", "NotElement",
    "Tuple", "List", "Matrix", "Matrix2x2",
    "Floor", "Ceil", "Re", "Im", "Conjugate",
    "Min", "Max", "Mod", "GCD",
    "Sqrt", "Log", "Exp",
    "Sin", "Cos", "Tan", "Atan", "Asin", "Acos",
    "Factorial",
}

# Type/domain markers (not operators, just context)
DOMAIN_MARKERS = {
    "CC", "RR", "ZZ", "QQ", "HH", "ZZGreaterEqual", "ZZLessEqual",
    "PP", "NN",
    "OpenInterval", "ClosedInterval", "OpenClosedInterval", "ClosedOpenInterval",
    "Infinity", "UnsignedInfinity", "Undefined",
    "ConstI", "Pi", "ConstE", "ConstGamma",
    "True_", "False_",
    "This", "Arithmetic", "Illustrations", "References",
    "Image", "ImageSource", "Plot", "Represents",
    "Convergents", "Description",
}


def classify_symbols(symbols):
    """Split symbol list into structural ops, domain functions, and markers."""
    structural = []
    domain_fns = []
    markers = []
    for s in symbols:
        if s in STRUCTURAL_OPS:
            structural.append(s)
        elif s in DOMAIN_MARKERS:
            markers.append(s)
        else:
            domain_fns.append(s)
    return structural, domain_fns, markers


# ── Distance metrics ──────────────────────────────────────────────────

def jaccard_multiset(a, b):
    """Jaccard distance on multisets (1 - |intersection|/|union|)."""
    ca = Counter(a)
    cb = Counter(b)
    all_keys = set(ca) | set(cb)
    if not all_keys:
        return 0.0
    intersection = sum(min(ca[k], cb[k]) for k in all_keys)
    union = sum(max(ca[k], cb[k]) for k in all_keys)
    if union == 0:
        return 0.0
    return 1.0 - intersection / union


def rewrite_distance(f1_syms, f2_syms):
    """
    Weighted rewrite distance between two formulas.

    Structural operators get weight 1.0 (they define the skeleton).
    Domain-specific functions get weight 0.5 (they specialize the skeleton).
    Domain markers are ignored (they're just type annotations).
    """
    s1, d1, _ = classify_symbols(f1_syms)
    s2, d2, _ = classify_symbols(f2_syms)

    # If both have no meaningful content, distance is 0
    if not s1 and not d1 and not s2 and not d2:
        return 1.0  # maximally uninformative

    structural_dist = jaccard_multiset(s1, s2)
    domain_dist = jaccard_multiset(d1, d2)

    # Weight: structural skeleton matters more
    w_s = 0.7
    w_d = 0.3

    # Normalize by whether components exist
    if not s1 and not s2:
        return domain_dist
    if not d1 and not d2:
        return structural_dist

    return w_s * structural_dist + w_d * domain_dist


# ── Data loading ──────────────────────────────────────────────────────

def load_formulas():
    """Load Fungrim formula index."""
    print(f"Loading Fungrim index from {FUNGRIM_INDEX}")
    with open(FUNGRIM_INDEX) as f:
        data = json.load(f)

    formulas = data["formulas"]
    module_stats = data.get("module_stats", {})

    # Filter to formulas with meaningful symbols (>= 3 symbols, equation/definition type)
    meaningful_types = {"equation", "definition", "formula", "bound", "inequality"}
    filtered = [
        f for f in formulas
        if f["n_symbols"] >= 3
        and (f.get("type", "") in meaningful_types or f["n_symbols"] >= 5)
    ]

    print(f"  Total formulas: {len(formulas)}")
    print(f"  Filtered (meaningful): {len(filtered)}")
    print(f"  Modules: {len(module_stats)}")

    return filtered, module_stats


# ── Core computation ──────────────────────────────────────────────────

def compute_module_distances(formulas):
    """Compute within-module and between-module average rewrite distances."""

    # Group by module
    by_module = defaultdict(list)
    for f in formulas:
        by_module[f["module"]].append(f)

    modules = sorted(by_module.keys())
    print(f"\n  Computing distances across {len(modules)} modules...")

    # Within-module distances
    within_dists = {}
    for mod in modules:
        fms = by_module[mod]
        if len(fms) < 2:
            within_dists[mod] = None
            continue
        dists = []
        pairs = list(combinations(range(len(fms)), 2))
        # Sample if too many pairs
        if len(pairs) > 500:
            pairs = random.sample(pairs, 500)
        for i, j in pairs:
            d = rewrite_distance(fms[i]["symbols"], fms[j]["symbols"])
            dists.append(d)
        within_dists[mod] = sum(dists) / len(dists)

    # Between-module distances (sample for speed)
    between_dists = {}
    module_pairs = list(combinations(modules, 2))

    for m1, m2 in module_pairs:
        fms1 = by_module[m1]
        fms2 = by_module[m2]
        pairs = [(i, j) for i in range(len(fms1)) for j in range(len(fms2))]
        if len(pairs) > 200:
            pairs = random.sample(pairs, 200)
        dists = []
        for i, j in pairs:
            d = rewrite_distance(fms1[i]["symbols"], fms2[j]["symbols"])
            dists.append(d)
        between_dists[(m1, m2)] = sum(dists) / len(dists) if dists else None

    return within_dists, between_dists, by_module, modules


def find_cross_domain_bridges(by_module, modules, top_n=30):
    """Find minimum-distance cross-domain formula pairs."""
    print("  Finding narrowest cross-domain bridges...")

    bridges = []
    module_pairs = list(combinations(modules, 2))

    for m1, m2 in module_pairs:
        fms1 = by_module[m1]
        fms2 = by_module[m2]

        best_dist = 1.0
        best_pair = None

        for f1 in fms1:
            for f2 in fms2:
                d = rewrite_distance(f1["symbols"], f2["symbols"])
                if d < best_dist:
                    best_dist = d
                    best_pair = (f1, f2)

        if best_pair is not None:
            bridges.append({
                "module_a": m1,
                "module_b": m2,
                "formula_a": best_pair[0]["id"],
                "formula_b": best_pair[1]["id"],
                "symbols_a": best_pair[0]["symbols"],
                "symbols_b": best_pair[1]["symbols"],
                "distance": round(best_dist, 6),
                "shared_structural": sorted(
                    set(classify_symbols(best_pair[0]["symbols"])[0])
                    & set(classify_symbols(best_pair[1]["symbols"])[0])
                ),
                "shared_domain_fns": sorted(
                    set(classify_symbols(best_pair[0]["symbols"])[1])
                    & set(classify_symbols(best_pair[1]["symbols"])[1])
                ),
            })

    bridges.sort(key=lambda x: x["distance"])
    return bridges[:top_n]


def find_conserved_patterns(formulas, by_module, modules):
    """Find operator patterns that appear across many modules."""
    print("  Identifying conserved universal patterns...")

    # Which structural ops appear in each module?
    module_ops = {}
    for mod in modules:
        ops = set()
        for f in by_module[mod]:
            s, _, _ = classify_symbols(f["symbols"])
            ops.update(s)
        module_ops[mod] = ops

    # Count: how many modules use each structural op?
    op_module_count = Counter()
    for mod, ops in module_ops.items():
        for op in ops:
            op_module_count[op] += 1

    total_modules = len(modules)

    # Universal ops (appear in >80% of modules)
    universal_ops = {
        op: count for op, count in op_module_count.items()
        if count >= 0.8 * total_modules
    }

    # Domain-specific functions across modules
    fn_module_map = defaultdict(set)
    for mod in modules:
        for f in by_module[mod]:
            _, fns, _ = classify_symbols(f["symbols"])
            for fn in fns:
                fn_module_map[fn].add(mod)

    # Bridge functions: domain functions that appear in 3+ modules
    bridge_fns = {
        fn: sorted(mods)
        for fn, mods in fn_module_map.items()
        if len(mods) >= 3
    }

    # Operator bigrams: which structural ops co-occur in formulas?
    op_cooccurrence = Counter()
    for f in formulas:
        s, _, _ = classify_symbols(f["symbols"])
        s_unique = sorted(set(s))
        for i in range(len(s_unique)):
            for j in range(i + 1, len(s_unique)):
                op_cooccurrence[(s_unique[i], s_unique[j])] += 1

    top_cooccurrences = op_cooccurrence.most_common(30)

    return universal_ops, bridge_fns, top_cooccurrences, op_module_count


def build_distance_matrix(within_dists, between_dists, modules):
    """Build module x module distance matrix."""
    n = len(modules)
    mod_idx = {m: i for i, m in enumerate(modules)}
    matrix = [[0.0] * n for _ in range(n)]

    for (m1, m2), d in between_dists.items():
        if d is not None:
            i, j = mod_idx[m1], mod_idx[m2]
            matrix[i][j] = round(d, 4)
            matrix[j][i] = round(d, 4)

    return matrix


# ── Main ──────────────────────────────────────────────────────────────

def main():
    random.seed(42)
    t0 = time.time()

    formulas, module_stats = load_formulas()

    # Compute distances
    within_dists, between_dists, by_module, modules = compute_module_distances(formulas)

    # Summary statistics
    valid_within = [v for v in within_dists.values() if v is not None]
    valid_between = [v for v in between_dists.values() if v is not None]

    avg_within = sum(valid_within) / len(valid_within) if valid_within else 0
    avg_between = sum(valid_between) / len(valid_between) if valid_between else 0
    ratio = avg_within / avg_between if avg_between > 0 else float("inf")

    print(f"\n  === Distance Summary ===")
    print(f"  Average within-module distance:  {avg_within:.4f}")
    print(f"  Average between-module distance: {avg_between:.4f}")
    print(f"  Ratio (within/between):          {ratio:.4f}")
    if ratio < 1:
        print(f"  -> Formulas within a domain ARE more similar (expected)")
    else:
        print(f"  -> Domain boundaries do NOT strongly constrain skeleton structure")

    # Cross-domain bridges
    bridges = find_cross_domain_bridges(by_module, modules, top_n=30)
    print(f"\n  === Top 10 Narrowest Cross-Domain Bridges ===")
    for i, b in enumerate(bridges[:10]):
        print(f"  {i+1}. {b['module_a']} <-> {b['module_b']}: "
              f"d={b['distance']:.4f} "
              f"({b['formula_a']} <-> {b['formula_b']})")
        if b["shared_structural"]:
            print(f"     shared ops: {', '.join(b['shared_structural'])}")

    # Conserved patterns
    universal_ops, bridge_fns, top_cooccurrences, op_module_count = \
        find_conserved_patterns(formulas, by_module, modules)

    print(f"\n  === Universal Operators (>80% of modules) ===")
    for op, count in sorted(universal_ops.items(), key=lambda x: -x[1]):
        print(f"  {op}: {count}/{len(modules)} modules")

    print(f"\n  === Bridge Functions (domain fns in 3+ modules) ===")
    top_bridge = sorted(bridge_fns.items(), key=lambda x: -len(x[1]))[:15]
    for fn, mods in top_bridge:
        print(f"  {fn}: {len(mods)} modules — {', '.join(mods[:5])}{'...' if len(mods)>5 else ''}")

    print(f"\n  === Top Operator Co-occurrences ===")
    for (op1, op2), count in top_cooccurrences[:10]:
        print(f"  ({op1}, {op2}): {count} formulas")

    # Distance matrix
    dist_matrix = build_distance_matrix(within_dists, between_dists, modules)

    # Find module clusters (modules with lowest average distance to each other)
    module_avg_dist = {}
    for i, m in enumerate(modules):
        dists_to_others = [dist_matrix[i][j] for j in range(len(modules)) if i != j and dist_matrix[i][j] > 0]
        module_avg_dist[m] = sum(dists_to_others) / len(dists_to_others) if dists_to_others else 0

    # Most "central" modules (lowest avg distance = most universal skeleton)
    central = sorted(module_avg_dist.items(), key=lambda x: x[1])[:10]
    peripheral = sorted(module_avg_dist.items(), key=lambda x: -x[1])[:10]

    print(f"\n  === Most Central Modules (universal skeleton) ===")
    for m, d in central:
        print(f"  {m}: avg_dist={d:.4f} ({len(by_module[m])} formulas)")

    print(f"\n  === Most Peripheral Modules (unique skeleton) ===")
    for m, d in peripheral:
        print(f"  {m}: avg_dist={d:.4f} ({len(by_module[m])} formulas)")

    elapsed = time.time() - t0
    print(f"\n  Completed in {elapsed:.1f}s")

    # ── Save results ──────────────────────────────────────────────────
    results = {
        "meta": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "n_formulas_analyzed": len(formulas),
            "n_modules": len(modules),
            "elapsed_seconds": round(elapsed, 1),
        },
        "distance_summary": {
            "avg_within_module": round(avg_within, 6),
            "avg_between_module": round(avg_between, 6),
            "within_over_between_ratio": round(ratio, 6),
            "interpretation": (
                "within < between: domain boundaries constrain skeleton"
                if ratio < 1
                else "within ~ between: skeleton structure transcends domains"
            ),
        },
        "within_module_distances": {
            m: round(v, 6) if v is not None else None
            for m, v in sorted(within_dists.items())
        },
        "cross_domain_bridges": bridges,
        "conserved_patterns": {
            "universal_operators": {
                op: {"module_count": count, "fraction": round(count / len(modules), 3)}
                for op, count in sorted(universal_ops.items(), key=lambda x: -x[1])
            },
            "bridge_functions": {
                fn: {"module_count": len(mods), "modules": mods}
                for fn, mods in sorted(bridge_fns.items(), key=lambda x: -len(x[1]))[:30]
            },
            "top_operator_cooccurrences": [
                {"ops": [op1, op2], "count": count}
                for (op1, op2), count in top_cooccurrences[:30]
            ],
        },
        "module_centrality": {
            m: round(d, 6) for m, d in sorted(module_avg_dist.items(), key=lambda x: x[1])
        },
        "distance_matrix": {
            "modules": modules,
            "matrix": dist_matrix,
        },
    }

    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to {OUT_FILE}")


if __name__ == "__main__":
    main()
