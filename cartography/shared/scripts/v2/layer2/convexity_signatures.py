"""
Convexity Signature Extractor (S23) — curvature landscape from formula trees.
==============================================================================
Walks each formula tree and classifies every operator node by its second-order
curvature structure (convex, concave, saddle, linear, oscillating). The
resulting curvature vector is a geometric fingerprint: formulas that bend space
the same way cluster together regardless of mathematical domain.

    exp(x + y)  -> curvature_vector=(1,0,0,1,0)  dominant=convex
    log(x * y)  -> curvature_vector=(0,1,1,0,0)  dominant=concave

Usage:
    python convexity_signatures.py                          # full run
    python convexity_signatures.py --max-formulas 100000    # cap input
    python convexity_signatures.py --sample 50000           # random sample
"""

import argparse
import hashlib
import json
import math
import sys
import time
import random
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
TREES_FILE = ROOT / "cartography" / "convergence" / "data" / "formula_trees.jsonl"
FORMULAS_FILE = ROOT / "cartography" / "convergence" / "data" / "openwebmath_formulas.jsonl"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"


# ── Curvature classification ─────────────────────────────────────────

# Indices: convex=0, concave=1, saddle=2, linear=3, oscillating=4
CURV_NAMES = ("convex", "concave", "saddle", "linear", "oscillating")
CURV_IDX = {n: i for i, n in enumerate(CURV_NAMES)}

# Operator -> curvature type
_OP_CURVATURE = {
    # Linear (curvature 0)
    "add": "linear", "sub": "linear", "neg": "linear",
    "sum": "linear", "pm": "linear",
    # Bilinear -> saddle
    "multiply": "saddle", "mul": "saddle", "cdot": "saddle",
    "times": "saddle", "cross": "saddle", "dot": "saddle",
    # Division: curvature depends on structure, default saddle
    "frac": "saddle", "div": "saddle", "over": "saddle",
    # Convex
    "exp": "convex", "cosh": "convex", "abs": "convex",
    "norm": "convex", "max": "convex",
    # Concave
    "log": "concave", "ln": "concave", "sqrt": "concave",
    "cbrt": "concave", "min": "concave",
    # Oscillating
    "sin": "oscillating", "cos": "oscillating", "tan": "oscillating",
    "sec": "oscillating", "csc": "oscillating", "cot": "oscillating",
    # Inverse trig: concave/convex piecewise, treat as oscillating
    "arcsin": "oscillating", "arccos": "oscillating", "arctan": "concave",
    "asin": "oscillating", "acos": "oscillating", "atan": "concave",
    # Hyperbolic (convex family)
    "sinh": "convex", "tanh": "concave",
    # Integrals/derivatives: linear operators
    "int": "linear", "integral": "linear", "diff": "linear",
    "partial": "linear", "nabla": "linear", "grad": "linear",
    "lim": "linear", "limit": "linear",
}


def classify_power(node):
    """Classify power(x, n) curvature based on exponent."""
    children = node.get("children", [])
    if len(children) < 2:
        return "convex"
    exp_node = children[1]
    if isinstance(exp_node, dict) and exp_node.get("type") == "number":
        try:
            n = float(exp_node.get("value", 2))
        except (ValueError, TypeError):
            return "convex"
        if n == 1:
            return "linear"
        if n == 0:
            return "linear"
        if 0 < n < 1:
            return "concave"  # e.g. sqrt
        if n < 0:
            return "convex"   # convex for x > 0
        if n > 1:
            # Even integer exponents: convex. Odd: mixed (saddle).
            if n == int(n) and int(n) % 2 == 0:
                return "convex"
            return "saddle"
    return "convex"  # default for symbolic exponent


def node_curvature(node):
    """Return curvature type string for a single operator node."""
    if not isinstance(node, dict):
        return "linear"
    ntype = node.get("type", "")
    if ntype in ("variable", "number"):
        return "linear"
    op = (node.get("op") or ntype or "").lower().strip()
    if op in ("pow", "power", "superscript", "^"):
        return classify_power(node)
    return _OP_CURVATURE.get(op, "linear")


# ── Tree walk ─────────────────────────────────────────────────────────

def curvature_walk(node, depth=0):
    """Walk tree, return (curvature_vector, depth_first_nonlinear, total_nodes)."""
    vec = [0, 0, 0, 0, 0]
    first_nl = None
    total = 0

    def _walk(n, d):
        nonlocal first_nl, total
        if not isinstance(n, dict):
            return
        ntype = n.get("type", "")
        children = n.get("children", [])
        # Only count operator/group nodes, not leaves
        if ntype not in ("variable", "number") and (children or ntype not in ("variable", "number", "")):
            curv = node_curvature(n)
            idx = CURV_IDX.get(curv, 3)
            vec[idx] += 1
            total += 1
            if curv != "linear" and first_nl is None:
                first_nl = d
        for c in children:
            _walk(c, d + 1)

    _walk(node, 0)
    return tuple(vec), first_nl, total


def curvature_entropy(vec):
    """Shannon entropy of curvature distribution."""
    total = sum(vec)
    if total == 0:
        return 0.0
    ent = 0.0
    for v in vec:
        if v > 0:
            p = v / total
            ent -= p * math.log2(p)
    return round(ent, 4)


def dominant_curvature(vec):
    """Return the most common curvature type."""
    if sum(vec) == 0:
        return "linear"
    idx = max(range(5), key=lambda i: vec[i])
    return CURV_NAMES[idx]


def curvature_class(dominant, entropy, nl_ratio):
    """Hash-based class from (dominant, entropy_bin, nl_ratio_bin)."""
    ent_bin = int(entropy * 4)  # 0..9-ish
    nl_bin = int(nl_ratio * 10)  # 0..10
    key = f"{dominant}:{ent_bin}:{nl_bin}"
    return hashlib.md5(key.encode()).hexdigest()[:12]


# ── Domain lookup ─────────────────────────────────────────────────────

def load_domain_map(max_load=None):
    """Load hash -> domain from openwebmath_formulas.jsonl."""
    dmap = {}
    if not FORMULAS_FILE.exists():
        print(f"  [warn] domain file not found: {FORMULAS_FILE}")
        return dmap
    print(f"  Loading domain map from {FORMULAS_FILE.name} ...")
    t0 = time.time()
    count = 0
    with open(FORMULAS_FILE, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if max_load and count >= max_load:
                break
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            h = rec.get("hash", "")
            domains = rec.get("domains", ["unclassified"])
            if h:
                dmap[h] = domains[0] if domains else "unclassified"
            count += 1
            if count % 2_000_000 == 0:
                print(f"    ... {count:,} domain entries loaded")
    print(f"  Domain map: {len(dmap):,} entries in {time.time()-t0:.1f}s")
    return dmap


# ── Main pipeline ─────────────────────────────────────────────────────

def process_formulas(max_formulas=None, sample_size=None):
    print("=" * 70)
    print("  Convexity Signature Extractor (S23)")
    print("=" * 70)

    domain_map = load_domain_map(max_load=max_formulas)

    # Reservoir sampling if requested
    if sample_size:
        print(f"  Sampling {sample_size:,} formulas (reservoir sampling) ...")
        reservoir = []
        count = 0
        with open(TREES_FILE, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if max_formulas and count >= max_formulas:
                    break
                count += 1
                if len(reservoir) < sample_size:
                    reservoir.append(line)
                else:
                    j = random.randint(0, count - 1)
                    if j < sample_size:
                        reservoir[j] = line
                if count % 2_000_000 == 0:
                    print(f"    ... scanned {count:,} lines")
        lines = reservoir
        print(f"  Sampled {len(lines):,} from {count:,} total lines")
    else:
        lines = None

    sig_path = OUT_DIR / "convexity_signatures.jsonl"
    clust_path = OUT_DIR / "convexity_clusters.jsonl"

    # Cluster accumulators
    class_formulas = defaultdict(list)
    class_domains = defaultdict(set)
    class_count = defaultdict(int)
    class_label = {}  # cclass -> dominant curvature

    t0 = time.time()
    processed = 0
    skipped = 0

    def process_line(line, sig_out):
        nonlocal processed, skipped
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            skipped += 1
            return
        root = rec.get("root")
        if not root:
            skipped += 1
            return
        formula_hash = rec.get("hash", "")
        domain = domain_map.get(formula_hash, "unclassified")

        vec, depth_nl, total = curvature_walk(root)
        dom = dominant_curvature(vec)
        ent = curvature_entropy(vec)
        nl_count = vec[0] + vec[1] + vec[2] + vec[4]  # non-linear = everything except linear
        nl_ratio = round(nl_count / total, 4) if total > 0 else 0.0
        depth_nl = depth_nl if depth_nl is not None else -1
        cclass = curvature_class(dom, ent, nl_ratio)

        sig_rec = {
            "hash": formula_hash,
            "curvature_vector": list(vec),
            "dominant": dom,
            "entropy": ent,
            "depth_first_nonlinear": depth_nl,
            "nonlinearity_ratio": nl_ratio,
            "curvature_class": cclass,
            "domain": domain,
        }
        sig_out.write(json.dumps(sig_rec, separators=(",", ":")) + "\n")

        class_count[cclass] += 1
        class_domains[cclass].add(domain)
        class_label[cclass] = dom
        if len(class_formulas[cclass]) < 3:
            class_formulas[cclass].append({
                "hash": formula_hash,
                "domain": domain,
                "curvature_vector": list(vec),
            })
        processed += 1

    with open(sig_path, "w", encoding="utf-8") as sig_out:
        if lines is not None:
            for line in lines:
                process_line(line, sig_out)
                if processed % 500_000 == 0 and processed > 0:
                    elapsed = time.time() - t0
                    print(f"    {processed:,} processed  ({processed/elapsed:,.0f}/s)")
        else:
            with open(TREES_FILE, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if max_formulas and processed >= max_formulas:
                        break
                    process_line(line, sig_out)
                    if processed % 500_000 == 0 and processed > 0:
                        elapsed = time.time() - t0
                        print(f"    {processed:,} processed  ({processed/elapsed:,.0f}/s)")

    elapsed = time.time() - t0

    # Write cluster file
    n_cross = 0
    with open(clust_path, "w", encoding="utf-8") as cf:
        for cclass in sorted(class_count, key=lambda k: -class_count[k]):
            domains = sorted(class_domains[cclass])
            is_cross = len(domains) > 1 and not (len(domains) == 1 and domains[0] == "unclassified")
            if is_cross:
                n_cross += 1
            rec = {
                "curvature_class": cclass,
                "dominant": class_label.get(cclass, "linear"),
                "n_formulas": class_count[cclass],
                "n_domains": len(domains),
                "domains": domains,
                "examples": class_formulas[cclass],
            }
            cf.write(json.dumps(rec, separators=(",", ":")) + "\n")

    n_classes = len(class_count)
    top = sorted(class_count.items(), key=lambda kv: -kv[1])[:15]

    print()
    print("=" * 70)
    print(f"  Convexity Signature Extraction Complete")
    print(f"  {'=' * 40}")
    print(f"  Formulas processed:    {processed:>12,}")
    print(f"  Skipped (parse err):   {skipped:>12,}")
    print(f"  Curvature classes:     {n_classes:>12,}")
    print(f"  Cross-domain classes:  {n_cross:>12,}")
    print(f"  Time:                  {elapsed:>11.1f}s")
    if elapsed > 0:
        print(f"  Rate:                  {processed/elapsed:>11,.0f}/s")
    print()
    print("  Top 15 curvature classes:")
    for i, (cclass, cnt) in enumerate(top, 1):
        dom = class_label.get(cclass, "?")
        doms = sorted(class_domains[cclass])
        print(f"    {i:>2}. [{cclass}] n={cnt:>8,}  dominant={dom:<12s}  domains={len(doms):>3}")
    print()
    print(f"  Output: {sig_path}")
    print(f"  Output: {clust_path}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Convexity Signature Extractor (S23)")
    parser.add_argument("--max-formulas", type=int, default=None,
                        help="Cap on total formulas to process")
    parser.add_argument("--sample", type=int, default=None,
                        help="Reservoir-sample N formulas instead of streaming all")
    args = parser.parse_args()
    process_formulas(max_formulas=args.max_formulas, sample_size=args.sample)


if __name__ == "__main__":
    main()
