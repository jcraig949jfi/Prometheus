"""
Symmetry Signature Detector (S9) — invariant transformations on formula trees.
===============================================================================
Detects which transformations leave a formula invariant. Two formulas with
isomorphic symmetry groups share structural DNA. Pure tree operations — no
evaluation, no numerical computation.

Symmetries detected:
  - Commutativity: fraction of binary nodes with order-invariant children
  - Variable symmetry: order of the permutation group leaving tree invariant
  - Self-similarity: repeated subtree ratio
  - Depth balance: min_depth / max_depth across binary nodes
  - Parity: even / odd / neither (negation symmetry on variables)

Usage:
    python symmetry_signatures.py                        # full run
    python symmetry_signatures.py --max-formulas 100000  # cap input
    python symmetry_signatures.py --sample 50000         # random sample
"""

import argparse
import hashlib
import json
import sys
import time
import random
from collections import defaultdict
from itertools import permutations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
TREES_FILE = ROOT / "cartography" / "convergence" / "data" / "formula_trees.jsonl"
FORMULAS_FILE = ROOT / "cartography" / "convergence" / "data" / "openwebmath_formulas.jsonl"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"

COMMUTATIVE_OPS = frozenset({"add", "multiply", "eq"})
MAX_VARS_FOR_PERM = 6  # factorial blowup guard


# ── Tree hashing (canonical string for subtree identity) ──────────────

def tree_canon(node):
    """Canonical string representation of a subtree."""
    if not isinstance(node, dict):
        return "?"
    ntype = node.get("type", "")
    if ntype == "variable":
        return f"V:{node.get('name', '')}"
    if ntype == "number":
        return f"N:{node.get('value', '')}"
    op = node.get("op", ntype) or "unk"
    children = node.get("children", [])
    if not children:
        return op
    child_strs = [tree_canon(c) for c in children]
    return f"{op}({','.join(child_strs)})"


def tree_canon_anon(node):
    """Canonical string with anonymised variables (all -> V)."""
    if not isinstance(node, dict):
        return "?"
    ntype = node.get("type", "")
    if ntype == "variable":
        return "V"
    if ntype == "number":
        return f"N:{node.get('value', '')}"
    op = node.get("op", ntype) or "unk"
    children = node.get("children", [])
    if not children:
        return op
    child_strs = [tree_canon_anon(c) for c in children]
    return f"{op}({','.join(child_strs)})"


def tree_canon_renamed(node, rename_map):
    """Canonical string with variables renamed according to rename_map."""
    if not isinstance(node, dict):
        return "?"
    ntype = node.get("type", "")
    if ntype == "variable":
        name = node.get("name", "")
        return f"V:{rename_map.get(name, name)}"
    if ntype == "number":
        return f"N:{node.get('value', '')}"
    op = node.get("op", ntype) or "unk"
    children = node.get("children", [])
    if not children:
        return op
    child_strs = [tree_canon_renamed(c, rename_map) for c in children]
    return f"{op}({','.join(child_strs)})"


def tree_canon_negated(node):
    """Canonical string with all variable leaves negated: wrap each in neg()."""
    if not isinstance(node, dict):
        return "?"
    ntype = node.get("type", "")
    if ntype == "variable":
        return f"neg(V:{node.get('name', '')})"
    if ntype == "number":
        return f"N:{node.get('value', '')}"
    op = node.get("op", ntype) or "unk"
    children = node.get("children", [])
    if not children:
        return op
    child_strs = [tree_canon_negated(c) for c in children]
    return f"{op}({','.join(child_strs)})"


def negate_whole(canon_str):
    """Wrap entire canonical string in neg()."""
    return f"neg({canon_str})"


# ── Commutativity ─────────────────────────────────────────────────────

def commutativity_score(node):
    """Fraction of binary commutative-op nodes whose children are order-invariant."""
    total_bin = 0
    commutative_count = 0
    stack = [node]
    while stack:
        n = stack.pop()
        if not isinstance(n, dict):
            continue
        children = n.get("children", [])
        op = n.get("op", "")
        if len(children) == 2 and op in COMMUTATIVE_OPS:
            total_bin += 1
            left_c = tree_canon_anon(children[0])
            right_c = tree_canon_anon(children[1])
            if left_c == right_c:
                commutative_count += 1
        for c in children:
            stack.append(c)
    if total_bin == 0:
        return 0.0, 0
    return commutative_count / total_bin, total_bin


# ── Variable symmetry ────────────────────────────────────────────────

def collect_variables(node):
    """Collect unique variable names from tree."""
    names = set()
    stack = [node]
    while stack:
        n = stack.pop()
        if not isinstance(n, dict):
            continue
        if n.get("type") == "variable":
            names.add(n.get("name", ""))
        for c in n.get("children", []):
            stack.append(c)
    return sorted(names)


def variable_symmetry_order(node, var_names):
    """Count how many variable permutations leave the tree invariant."""
    if len(var_names) <= 1:
        return 1
    if len(var_names) > MAX_VARS_FOR_PERM:
        # Too many variables — approximate: test only pairwise swaps
        return _pairwise_symmetry_order(node, var_names)
    base = tree_canon(node)
    count = 0
    for perm in permutations(var_names):
        rename = dict(zip(var_names, perm))
        if tree_canon_renamed(node, rename) == base:
            count += 1
    return count


def _pairwise_symmetry_order(node, var_names):
    """Approximate: count pairwise swaps that leave tree invariant. Return 1 + n_symmetric_pairs."""
    base = tree_canon(node)
    sym_pairs = 0
    n = len(var_names)
    for i in range(n):
        for j in range(i + 1, n):
            rename = {var_names[i]: var_names[j], var_names[j]: var_names[i]}
            if tree_canon_renamed(node, rename) == base:
                sym_pairs += 1
    return 1 + sym_pairs


# ── Self-similarity ──────────────────────────────────────────────────

def self_similarity(node):
    """Ratio of repeated subtree hashes to total subtrees."""
    hashes = []
    stack = [node]
    while stack:
        n = stack.pop()
        if not isinstance(n, dict):
            continue
        children = n.get("children", [])
        if children:
            hashes.append(tree_canon_anon(n))
            for c in children:
                stack.append(c)
    if not hashes:
        return 0.0, 0
    total = len(hashes)
    unique = len(set(hashes))
    repeated = total - unique
    return repeated / total, total


# ── Depth balance ────────────────────────────────────────────────────

def balance_score(node):
    """Average (min_child_depth / max_child_depth) across binary-op nodes. 1.0 = perfectly balanced."""
    total_ratio = 0.0
    n_bin = 0
    stack = [node]
    while stack:
        n = stack.pop()
        if not isinstance(n, dict):
            continue
        children = n.get("children", [])
        if len(children) >= 2:
            left_d = _subtree_depth(children[0])
            right_d = _subtree_depth(children[-1])
            hi = max(left_d, right_d)
            lo = min(left_d, right_d)
            total_ratio += (lo / hi) if hi > 0 else 1.0
            n_bin += 1
        for c in children:
            stack.append(c)
    if n_bin == 0:
        return 1.0
    return total_ratio / n_bin


def _subtree_depth(node, depth=0):
    if not isinstance(node, dict):
        return depth
    children = node.get("children", [])
    if not children:
        return depth
    return max(_subtree_depth(c, depth + 1) for c in children)


# ── Parity ───────────────────────────────────────────────────────────

def detect_parity(node):
    """Check negation symmetry: even (f(-x)=f(x)), odd (f(-x)=-f(x)), neither."""
    base = tree_canon(node)
    negated_vars = tree_canon_negated(node)
    if negated_vars == base:
        return "even"
    if negated_vars == negate_whole(base):
        return "odd"
    return "neither"


# ── Symmetry class hash ─────────────────────────────────────────────

def symmetry_class_hash(comm_bin, var_sym_order, parity):
    """Deterministic class hash from binned commutativity, var symmetry order, parity."""
    key = f"{comm_bin}|{var_sym_order}|{parity}"
    return hashlib.md5(key.encode()).hexdigest()[:12]


def bin_commutativity(score):
    """Bin commutativity to 0.1 resolution."""
    return round(score, 1)


# ── Domain lookup ────────────────────────────────────────────────────

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


# ── Main pipeline ────────────────────────────────────────────────────

def process_formulas(max_formulas=None, sample_size=None):
    print("=" * 70)
    print("  Symmetry Signature Detector (S9)")
    print("=" * 70)

    domain_map = load_domain_map(max_load=max_formulas)

    # Sampling
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

    sig_path = OUT_DIR / "symmetry_signatures.jsonl"
    clust_path = OUT_DIR / "symmetry_clusters.jsonl"

    # Cluster accumulators
    cluster_count = defaultdict(int)
    cluster_domains = defaultdict(set)
    cluster_examples = defaultdict(list)

    t0 = time.time()
    processed = 0
    skipped = 0

    # Parity / symmetry distribution counters
    parity_counts = defaultdict(int)
    var_sym_hist = defaultdict(int)

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

        # Commutativity
        comm, n_bin = commutativity_score(root)

        # Variable symmetry
        var_names = collect_variables(root)
        n_vars = len(var_names)
        vs_order = variable_symmetry_order(root, var_names) if n_vars >= 2 else 1

        # Self-similarity
        ss_ratio, n_subtrees = self_similarity(root)

        # Balance
        bal = balance_score(root)

        # Parity
        par = detect_parity(root) if n_vars > 0 else "unknown"

        # Symmetry class
        comm_bin = bin_commutativity(comm)
        sc = symmetry_class_hash(comm_bin, vs_order, par)

        sig_rec = {
            "hash": formula_hash,
            "commutativity": round(comm, 4),
            "var_symmetry_order": vs_order,
            "self_similarity": round(ss_ratio, 4),
            "balance": round(bal, 4),
            "parity": par,
            "n_variables": n_vars,
            "symmetry_class": sc,
            "domain": domain,
        }
        sig_out.write(json.dumps(sig_rec, separators=(",", ":")) + "\n")

        # Accumulate
        cluster_count[sc] += 1
        cluster_domains[sc].add(domain)
        if len(cluster_examples[sc]) < 3:
            cluster_examples[sc].append({"hash": formula_hash, "domain": domain})
        parity_counts[par] += 1
        var_sym_hist[vs_order] += 1
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

    # Write clusters
    n_cross = 0
    with open(clust_path, "w", encoding="utf-8") as cf:
        for sc in sorted(cluster_count, key=lambda h: -cluster_count[h]):
            domains = sorted(cluster_domains[sc])
            if len(domains) > 1:
                n_cross += 1
            rec = {
                "symmetry_class": sc,
                "n_formulas": cluster_count[sc],
                "n_domains": len(domains),
                "domains": domains,
                "examples": cluster_examples[sc],
            }
            cf.write(json.dumps(rec, separators=(",", ":")) + "\n")

    n_classes = len(cluster_count)

    # Summary
    print()
    print("=" * 70)
    print(f"  Symmetry Signature Detection Complete")
    print(f"  {'=' * 38}")
    print(f"  Formulas processed:    {processed:>12,}")
    print(f"  Skipped (parse err):   {skipped:>12,}")
    print(f"  Symmetry classes:      {n_classes:>12,}")
    print(f"  Cross-domain classes:  {n_cross:>12,}")
    print(f"  Time:                  {elapsed:>11.1f}s")
    if elapsed > 0:
        print(f"  Rate:                  {processed/elapsed:>11,.0f}/s")
    print()
    print("  Parity distribution:")
    for p in ("even", "odd", "neither", "unknown"):
        c = parity_counts.get(p, 0)
        pct = 100 * c / processed if processed else 0
        print(f"    {p:<10} {c:>10,}  ({pct:5.1f}%)")
    print()
    print("  Variable symmetry order distribution (top 10):")
    for i, (order, cnt) in enumerate(sorted(var_sym_hist.items(), key=lambda kv: -kv[1])[:10]):
        print(f"    order={order:<4}  n={cnt:>10,}")
    print()
    top = sorted(cluster_count.items(), key=lambda kv: -kv[1])[:15]
    print("  Top 15 symmetry classes:")
    for i, (sc, cnt) in enumerate(top, 1):
        doms = sorted(cluster_domains[sc])
        print(f"    {i:>2}. [{sc}] n={cnt:>8,}  domains={len(doms):>3}")
    print()
    print(f"  Output: {sig_path}")
    print(f"  Output: {clust_path}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Symmetry Signature Detector (S9)")
    parser.add_argument("--max-formulas", type=int, default=None,
                        help="Cap on total formulas to process")
    parser.add_argument("--sample", type=int, default=None,
                        help="Reservoir-sample N formulas instead of streaming all")
    args = parser.parse_args()
    process_formulas(max_formulas=args.max_formulas, sample_size=args.sample)


if __name__ == "__main__":
    main()
