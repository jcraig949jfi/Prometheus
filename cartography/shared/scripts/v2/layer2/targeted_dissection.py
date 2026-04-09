"""
Targeted Dissection — run ALL extractors on highest-priority formulas.
=====================================================================
Selects ultra-targeted set from formula_triage.jsonl:
  1. All D_erdos formulas (105)
  2. All 4+-set formulas (multi-set, highest priority)
  3. Cap at 500 total (D_erdos first, then multi-set by n_sets desc)

Loads trees via grep (35GB file), runs operadic/convexity/symmetry/polytope
extractors inline, writes combined signatures.

Usage:
    python targeted_dissection.py
    python targeted_dissection.py --cap 200
"""

import argparse
import hashlib
import json
import sys
import time
from collections import Counter, defaultdict
from itertools import permutations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
TRIAGE = ROOT / "cartography" / "convergence" / "data" / "formula_triage.jsonl"
TREES  = ROOT / "cartography" / "convergence" / "data" / "formula_trees.jsonl"
OUT    = ROOT / "cartography" / "convergence" / "data" / "targeted_dissection.jsonl"


# ── Operadic skeleton ────────────────────────────────────────────────

def skeleton(node):
    if not isinstance(node, dict):
        return "?"
    ntype = node.get("type", "")
    if ntype == "variable":
        return "V"
    if ntype == "number":
        return "N"
    op = node.get("op", ntype) or "unk"
    children = node.get("children", [])
    if not children:
        return op
    return f"{op}({','.join(skeleton(c) for c in children)})"


# ── Convexity ────────────────────────────────────────────────────────

CURV_NAMES = ("convex", "concave", "saddle", "linear", "oscillating")
CURV_IDX = {n: i for i, n in enumerate(CURV_NAMES)}

_OP_CURVATURE = {
    "add": "linear", "sub": "linear", "neg": "linear",
    "sum": "linear", "pm": "linear",
    "multiply": "saddle", "mul": "saddle", "cdot": "saddle",
    "times": "saddle", "cross": "saddle", "dot": "saddle",
    "frac": "saddle", "div": "saddle", "over": "saddle",
    "exp": "convex", "cosh": "convex", "abs": "convex",
    "norm": "convex", "max": "convex",
    "log": "concave", "ln": "concave", "sqrt": "concave",
    "cbrt": "concave", "min": "concave",
    "sin": "oscillating", "cos": "oscillating", "tan": "oscillating",
    "sec": "oscillating", "csc": "oscillating", "cot": "oscillating",
    "arcsin": "oscillating", "arccos": "oscillating", "arctan": "concave",
    "asin": "oscillating", "acos": "oscillating", "atan": "concave",
    "sinh": "convex", "tanh": "concave",
    "int": "linear", "integral": "linear", "diff": "linear",
    "partial": "linear", "nabla": "linear", "grad": "linear",
    "lim": "linear", "limit": "linear",
}


def _classify_power(node):
    children = node.get("children", [])
    if len(children) < 2:
        return "convex"
    exp_node = children[1]
    if isinstance(exp_node, dict) and exp_node.get("type") == "number":
        try:
            n = float(exp_node.get("value", 2))
        except (ValueError, TypeError):
            return "convex"
        if n in (0, 1):
            return "linear"
        if 0 < n < 1:
            return "concave"
        if n < 0:
            return "convex"
        if n == int(n) and int(n) % 2 == 0:
            return "convex"
        return "saddle"
    return "convex"


def node_curvature(node):
    if not isinstance(node, dict):
        return "linear"
    ntype = node.get("type", "")
    if ntype in ("variable", "number"):
        return "linear"
    op = (node.get("op") or ntype or "").lower().strip()
    if op in ("pow", "power", "superscript", "^"):
        return _classify_power(node)
    return _OP_CURVATURE.get(op, "linear")


def curvature_walk(node):
    vec = [0, 0, 0, 0, 0]
    stack = [node]
    total = 0
    while stack:
        n = stack.pop()
        if not isinstance(n, dict):
            continue
        ntype = n.get("type", "")
        children = n.get("children", [])
        if ntype not in ("variable", "number") and (children or ntype not in ("variable", "number", "")):
            curv = node_curvature(n)
            vec[CURV_IDX.get(curv, 3)] += 1
            total += 1
        for c in children:
            stack.append(c)
    dominant = CURV_NAMES[vec.index(max(vec))] if total > 0 else "linear"
    return tuple(vec), dominant, total


# ── Symmetry ─────────────────────────────────────────────────────────

COMMUTATIVE_OPS = frozenset({"add", "multiply", "eq"})
MAX_VARS_FOR_PERM = 6


def tree_canon(node):
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
    return f"{op}({','.join(tree_canon(c) for c in children)})"


def tree_canon_anon(node):
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
    return f"{op}({','.join(tree_canon_anon(c) for c in children)})"


def tree_canon_renamed(node, rename_map):
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
    return f"{op}({','.join(tree_canon_renamed(c, rename_map) for c in children)})"


def tree_canon_negated(node):
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
    return f"{op}({','.join(tree_canon_negated(c) for c in children)})"


def commutativity_score(node):
    total_bin = 0
    comm = 0
    stack = [node]
    while stack:
        n = stack.pop()
        if not isinstance(n, dict):
            continue
        children = n.get("children", [])
        op = n.get("op", "")
        if len(children) == 2 and op in COMMUTATIVE_OPS:
            total_bin += 1
            if tree_canon_anon(children[0]) == tree_canon_anon(children[1]):
                comm += 1
        for c in children:
            stack.append(c)
    return (comm / total_bin if total_bin else 0.0), total_bin


def collect_variables(node):
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
    if len(var_names) <= 1:
        return 1
    if len(var_names) > MAX_VARS_FOR_PERM:
        base = tree_canon(node)
        sym_pairs = 0
        n = len(var_names)
        for i in range(n):
            for j in range(i + 1, n):
                rename = {var_names[i]: var_names[j], var_names[j]: var_names[i]}
                if tree_canon_renamed(node, rename) == base:
                    sym_pairs += 1
        return 1 + sym_pairs
    base = tree_canon(node)
    count = 0
    for perm in permutations(var_names):
        rename = dict(zip(var_names, perm))
        if tree_canon_renamed(node, rename) == base:
            count += 1
    return count


def detect_parity(node):
    base = tree_canon(node)
    negated = tree_canon_negated(node)
    if negated == base:
        return "even"
    if negated == f"neg({base})":
        return "odd"
    return "neither"


# ── Newton polytope ──────────────────────────────────────────────────

TRANSCENDENTAL_OPS = {"sin", "cos", "tan", "arcsin", "arccos", "arctan",
                      "sinh", "cosh", "tanh", "exp", "log", "ln", "lg",
                      "sqrt", "cbrt", "abs", "floor", "ceil", "sgn",
                      "limit", "integral", "sum", "prod", "diff"}


def _extract_numeric(node):
    if not isinstance(node, dict):
        return None
    if node.get("type") == "number":
        try:
            v = float(node.get("value", ""))
            if v == int(v) and v >= 0:
                return int(v)
        except (ValueError, TypeError):
            pass
        return None
    if node.get("op") == "neg":
        children = node.get("children", [])
        if children:
            v = _extract_numeric(children[0])
            if v is not None:
                return -v
    return None


def _extract_single_monomial(node):
    if not isinstance(node, dict):
        return None
    ntype = node.get("type", "")
    op = node.get("op", "")
    children = node.get("children", [])
    if ntype == "variable":
        name = node.get("name", "")
        if len(name) == 1 and name not in ("|", ",", ".", ""):
            return {name: 1}
        return {}
    if ntype == "number":
        return {}
    if op == "neg" and children:
        return _extract_single_monomial(children[0])
    if op == "power" and len(children) >= 2:
        base_mono = _extract_single_monomial(children[0])
        if base_mono is None:
            return None
        exp_val = _extract_numeric(children[1])
        if exp_val is None or exp_val < 0:
            return None
        return {var: deg * exp_val for var, deg in base_mono.items()}
    if op == "multiply" and children:
        result = {}
        for c in children:
            cmono = _extract_single_monomial(c)
            if cmono is None:
                return None
            for var, deg in cmono.items():
                result[var] = result.get(var, 0) + deg
        return result
    if op == "paren" and len(children) == 1:
        return _extract_single_monomial(children[0])
    if op in TRANSCENDENTAL_OPS or op in ("factorial", "binomial"):
        return None
    if op in ("add", "sub", "plus", "minus"):
        return None
    if op == "subscript":
        return {}
    return None


def _extract_additive_terms(node):
    if not isinstance(node, dict):
        return None, None
    op = node.get("op", "")
    children = node.get("children", [])
    if op in ("add", "sub", "plus", "minus"):
        all_monos = []
        all_vars = set()
        for c in children:
            monos, vrs = _extract_additive_terms(c)
            if monos is None:
                return None, None
            all_monos.extend(monos)
            if vrs:
                all_vars.update(vrs)
        return all_monos, all_vars
    mono = _extract_single_monomial(node)
    if mono is None:
        return None, None
    variables = {k for k in mono if mono[k] != 0}
    return [mono], variables


def extract_newton_polytope(node):
    """Returns (n_vertices, max_degree, n_monomials) or None."""
    if not isinstance(node, dict):
        return None
    # Unwrap equation
    if node.get("op") == "eq":
        children = node.get("children", [])
        if len(children) >= 2:
            result = _try_polytope(children[-1])
            if result is None:
                result = _try_polytope(children[0])
            return result
    return _try_polytope(node)


def _try_polytope(node):
    monos, vrs = _extract_additive_terms(node)
    if monos is None or not monos:
        return None
    if not vrs:
        return (0, 0, len(monos))
    var_list = sorted(vrs)
    # Build exponent vectors
    vectors = set()
    max_deg = 0
    for m in monos:
        vec = tuple(m.get(v, 0) for v in var_list)
        vectors.add(vec)
        deg = sum(vec)
        if deg > max_deg:
            max_deg = deg
    # Convex hull vertex count: for 1D it's min/max, else approximate
    n_verts = len(vectors)  # upper bound (exact hull needs scipy)
    if len(var_list) == 1:
        vals = [v[0] for v in vectors]
        n_verts = len({min(vals), max(vals)})
    return (n_verts, max_deg, len(monos))


# ── Tree stats ───────────────────────────────────────────────────────

def tree_depth(node, d=0):
    if not isinstance(node, dict):
        return d
    children = node.get("children", [])
    if not children:
        return d
    return max(tree_depth(c, d + 1) for c in children)


def count_nodes(node):
    if not isinstance(node, dict):
        return 0
    return 1 + sum(count_nodes(c) for c in node.get("children", []))


# ── Target selection ─────────────────────────────────────────────────

def select_targets(cap=500):
    """Load triage, select D_erdos + 4+-set formulas, cap total."""
    erdos = []
    multi4 = []
    t0 = time.time()
    with open(TRIAGE, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            sets = rec.get("sets", [])
            ns = rec.get("n_sets", 0)
            is_erdos = "D_erdos" in sets
            if is_erdos:
                erdos.append(rec)
            if ns >= 4 and not is_erdos:
                multi4.append(rec)
    print(f"  triage scan: {time.time()-t0:.1f}s, D_erdos={len(erdos)}, 4+sets={len(multi4)}")

    # Sort multi4 by n_sets descending
    multi4.sort(key=lambda r: -r.get("n_sets", 0))
    remaining = cap - len(erdos)
    if remaining < 0:
        erdos = erdos[:cap]
        remaining = 0
    targets = erdos + multi4[:remaining]
    print(f"  selected {len(targets)} targets (cap={cap})")
    return targets


# ── Tree loading via grep ────────────────────────────────────────────

def load_trees_for_hashes(hashes):
    """Stream formula_trees.jsonl, extracting only target hashes. Returns {hash: root}."""
    if not hashes:
        return {}

    trees = {}
    remaining = set(hashes)
    t0 = time.time()
    scanned = 0

    with open(TREES, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            scanned += 1
            if scanned % 2_000_000 == 0:
                print(f"    scanned {scanned/1e6:.0f}M lines, found {len(trees)}/{len(hashes)}...")
            # Fast pre-check: hash is always near start of line
            # Format: {"hash":"XXXXXXXXXXXX","root":...}
            # Hash starts at position 9, 12 chars
            if len(line) < 24:
                continue
            h_candidate = line[9:21]  # extract hash without JSON parse
            if h_candidate not in remaining:
                continue
            try:
                rec = json.loads(line)
                h = rec.get("hash", "")
                if h in remaining:
                    trees[h] = rec.get("root", {})
                    remaining.discard(h)
                    if not remaining:
                        break
            except json.JSONDecodeError:
                continue

    print(f"  loaded {len(trees)}/{len(hashes)} trees in {time.time()-t0:.1f}s ({scanned/1e6:.1f}M lines scanned)")
    return trees


# ── Combined extraction ──────────────────────────────────────────────

def extract_all(tree, triage_rec):
    """Run all extractors on a single formula tree. Returns signature dict."""
    h = triage_rec["hash"]
    root = tree

    # Operadic skeleton
    skel = skeleton(root)

    # Curvature
    curv_vec, curv_dom, curv_total = curvature_walk(root)

    # Symmetry
    comm_score, comm_bins = commutativity_score(root)
    var_names = collect_variables(root)
    var_sym = variable_symmetry_order(root, var_names)
    parity = detect_parity(root)

    # Newton polytope
    polytope = extract_newton_polytope(root)
    poly_verts = polytope[0] if polytope else None
    poly_deg = polytope[1] if polytope else None
    poly_monos = polytope[2] if polytope else None

    # Tree stats
    n_nodes = count_nodes(root)
    depth = tree_depth(root)

    return {
        "hash": h,
        "triage_sets": triage_rec.get("sets", []),
        "n_triage_sets": triage_rec.get("n_sets", 0),
        "operadic_skeleton": skel[:500],  # truncate huge skeletons
        "skeleton_hash": hashlib.md5(skel.encode("utf-8", errors="replace")).hexdigest()[:16],
        "curvature_vector": list(curv_vec),
        "curvature_dominant": curv_dom,
        "curvature_nodes": curv_total,
        "commutativity": round(comm_score, 3),
        "comm_binary_nodes": comm_bins,
        "symmetry_parity": parity,
        "var_symmetry_order": var_sym,
        "n_variables": len(var_names),
        "polytope_vertices": poly_verts,
        "polytope_degree": poly_deg,
        "polytope_monomials": poly_monos,
        "n_nodes": n_nodes,
        "depth": depth,
    }


# ── Summary ──────────────────────────────────────────────────────────

def print_summary(results):
    n = len(results)
    print(f"\n{'='*60}")
    print(f"TARGETED DISSECTION SUMMARY: {n} formulas processed")
    print(f"{'='*60}")
    if n == 0:
        print("  No results to summarize.")
        return

    # Set membership
    set_counts = Counter()
    for r in results:
        for s in r["triage_sets"]:
            set_counts[s] += 1
    print(f"\nSet membership:")
    for s, c in set_counts.most_common():
        print(f"  {s}: {c}")

    # Curvature distribution
    curv_dist = Counter(r["curvature_dominant"] for r in results)
    print(f"\nDominant curvature:")
    for c, cnt in curv_dist.most_common():
        print(f"  {c}: {cnt} ({100*cnt/n:.1f}%)")

    # Parity distribution
    par_dist = Counter(r["symmetry_parity"] for r in results)
    print(f"\nParity:")
    for p, cnt in par_dist.most_common():
        print(f"  {p}: {cnt} ({100*cnt/n:.1f}%)")

    # Variable symmetry
    sym_dist = Counter(r["var_symmetry_order"] for r in results)
    print(f"\nVariable symmetry order:")
    for s, cnt in sym_dist.most_common(10):
        print(f"  order {s}: {cnt}")

    # Polytope coverage
    has_poly = sum(1 for r in results if r["polytope_vertices"] is not None)
    print(f"\nNewton polytope extractable: {has_poly}/{n} ({100*has_poly/n:.1f}%)")
    if has_poly > 0:
        deg_dist = Counter(r["polytope_degree"] for r in results if r["polytope_degree"] is not None)
        print(f"  Degree distribution (top 10):")
        for d, cnt in deg_dist.most_common(10):
            print(f"    deg {d}: {cnt}")

    # Skeleton clusters
    skel_hash_counts = Counter(r["skeleton_hash"] for r in results)
    n_unique = len(skel_hash_counts)
    n_clustered = sum(1 for v in skel_hash_counts.values() if v > 1)
    print(f"\nOperadic skeletons: {n_unique} unique, {n_clustered} shared")
    if n_clustered > 0:
        print(f"  Largest clusters:")
        for sh, cnt in skel_hash_counts.most_common(10):
            if cnt < 2:
                break
            # Find an example hash
            ex = next(r["hash"] for r in results if r["skeleton_hash"] == sh)
            print(f"    {sh}: {cnt} formulas (e.g. {ex})")

    # Depth/size stats
    depths = [r["depth"] for r in results]
    nodes = [r["n_nodes"] for r in results]
    print(f"\nTree size: depth {min(depths)}-{max(depths)} (median {sorted(depths)[n//2]}), "
          f"nodes {min(nodes)}-{max(nodes)} (median {sorted(nodes)[n//2]})")

    # Cross-formula skeleton matches between D_erdos and multi-set
    erdos_skels = {r["skeleton_hash"] for r in results if "D_erdos" in r["triage_sets"]}
    multi_skels = {r["skeleton_hash"] for r in results if "D_erdos" not in r["triage_sets"]}
    cross = erdos_skels & multi_skels
    print(f"\nCross-set skeleton matches (D_erdos vs multi-set): {len(cross)}")
    if cross:
        for sh in list(cross)[:5]:
            e_count = sum(1 for r in results if r["skeleton_hash"] == sh and "D_erdos" in r["triage_sets"])
            m_count = sum(1 for r in results if r["skeleton_hash"] == sh and "D_erdos" not in r["triage_sets"])
            print(f"    {sh}: {e_count} erdos + {m_count} multi-set")


# ── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Targeted formula dissection")
    parser.add_argument("--cap", type=int, default=500, help="Max formulas (default 500)")
    args = parser.parse_args()

    t0 = time.time()
    print("[1/4] Selecting targets from triage...")
    targets = select_targets(cap=args.cap)

    # Build lookup
    triage_by_hash = {t["hash"]: t for t in targets}
    target_hashes = set(triage_by_hash.keys())

    print(f"[2/4] Loading trees for {len(target_hashes)} hashes...")
    trees = load_trees_for_hashes(target_hashes)

    missing = target_hashes - set(trees.keys())
    if missing:
        print(f"  WARN: {len(missing)} hashes not found in trees file")

    print(f"[3/4] Running extractors on {len(trees)} formulas...")
    results = []
    for i, (h, root) in enumerate(trees.items()):
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{len(trees)}...")
        try:
            sig = extract_all(root, triage_by_hash[h])
            results.append(sig)
        except Exception as e:
            print(f"  ERR {h}: {e}")
            continue

    print(f"[4/4] Writing {len(results)} signatures to {OUT.name}...")
    with open(OUT, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s")
    print_summary(results)


if __name__ == "__main__":
    main()
