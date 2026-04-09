"""
Newton Polytope Signature Extractor (S14) — convex hull of exponent vectors.
=============================================================================
The Newton polytope of a polynomial is the convex hull of its exponent vectors.
Two formulas with the same Newton polytope share the same algebraic complexity
class regardless of coefficients.

    x^2*y + 3*x*y^2 + x^3  ->  exponent vectors (2,1), (1,2), (3,0)
                              ->  polytope = triangle with those vertices

Only applies to polynomial/rational formulas — transcendentals are skipped.

Usage:
    python newton_polytope.py                          # full run
    python newton_polytope.py --max-formulas 100000    # cap input
    python newton_polytope.py --sample 50000           # random sample
"""

import argparse
import hashlib
import json
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
TREES_FILE = ROOT / "cartography" / "convergence" / "data" / "formula_trees.jsonl"
FORMULAS_FILE = ROOT / "cartography" / "convergence" / "data" / "openwebmath_formulas.jsonl"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"

TRANSCENDENTAL_OPS = {"sin", "cos", "tan", "arcsin", "arccos", "arctan",
                      "sinh", "cosh", "tanh", "exp", "log", "ln", "lg",
                      "sqrt", "cbrt", "abs", "floor", "ceil", "sgn",
                      "limit", "integral", "sum", "prod", "diff"}


# ── Formula classification ───────────────────────────────────────────

def classify_formula(node, _cache=None):
    """Classify tree as polynomial, rational, transcendental, or mixed."""
    ops = set()
    _collect_ops(node, ops)
    has_transcendental = bool(ops & TRANSCENDENTAL_OPS)
    has_division = "div" in ops or "frac" in ops or "fraction" in ops
    has_neg_power = _has_neg_power(node)
    if has_transcendental:
        return "transcendental"
    if has_division or has_neg_power:
        return "rational"
    return "polynomial"


def _collect_ops(node, ops):
    if not isinstance(node, dict):
        return
    ntype = node.get("type", "")
    if ntype in ("operator", "equation", "group"):
        ops.add(node.get("op", ""))
    for c in node.get("children", []):
        _collect_ops(c, ops)


def _has_neg_power(node):
    """Check if any power node has a negative exponent."""
    if not isinstance(node, dict):
        return False
    if node.get("op") == "power":
        children = node.get("children", [])
        if len(children) >= 2:
            exp = children[1]
            if exp.get("op") == "neg":
                return True
            if exp.get("type") == "number":
                try:
                    if float(exp.get("value", 0)) < 0:
                        return True
                except (ValueError, TypeError):
                    pass
    for c in node.get("children", []):
        if _has_neg_power(c):
            return True
    return False


# ── Monomial extraction ──────────────────────────────────────────────

def extract_monomials(node):
    """Extract list of exponent-vector dicts from a formula tree.

    Each monomial is a dict: {var_name: exponent, ...}.
    Returns (monomials, variables) or (None, None) if not extractable.
    """
    # Unwrap equation nodes — get the RHS or the whole thing
    if not isinstance(node, dict):
        return None, None
    if node.get("op") == "eq":
        children = node.get("children", [])
        if len(children) >= 2:
            # Try RHS first, then LHS
            monos, vrs = _extract_additive_terms(children[-1])
            if monos is None:
                monos, vrs = _extract_additive_terms(children[0])
            return monos, vrs
    return _extract_additive_terms(node)


def _extract_additive_terms(node):
    """Split a node into additive terms and extract monomials from each."""
    if not isinstance(node, dict):
        return None, None
    op = node.get("op", "")
    children = node.get("children", [])

    # Addition/subtraction: collect terms
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

    # Single multiplicative term
    mono = _extract_single_monomial(node)
    if mono is None:
        return None, None
    variables = {k for k in mono if mono[k] != 0}
    return [mono], variables


def _extract_single_monomial(node):
    """Extract a single monomial (exponent dict) from a multiplicative expression.

    Returns dict {var: exponent} or None if not a monomial.
    """
    if not isinstance(node, dict):
        return None
    ntype = node.get("type", "")
    op = node.get("op", "")
    children = node.get("children", [])

    # Leaf: variable
    if ntype == "variable":
        name = node.get("name", "")
        if len(name) == 1 and name not in ("|", ",", ".", ""):
            return {name: 1}
        return {}  # skip non-single-char vars as constants

    # Leaf: number
    if ntype == "number":
        return {}  # coefficient, no variable contribution

    # Negation: pass through
    if op == "neg" and children:
        return _extract_single_monomial(children[0])

    # Power: var^n
    if op == "power" and len(children) >= 2:
        base_mono = _extract_single_monomial(children[0])
        if base_mono is None:
            return None
        exp_val = _extract_numeric(children[1])
        if exp_val is None:
            return None
        if exp_val < 0:
            return None  # rational, skip
        result = {}
        for var, deg in base_mono.items():
            result[var] = deg * exp_val
        return result

    # Multiply: product of monomials
    if op == "multiply" and children:
        result = {}
        for c in children:
            cmono = _extract_single_monomial(c)
            if cmono is None:
                return None
            for var, deg in cmono.items():
                result[var] = result.get(var, 0) + deg
        return result

    # Subscript: treat as single variable (e.g. a_n)
    if op == "subscript":
        return {}

    # Group (parenthesized): unwrap
    if op == "paren" and len(children) == 1:
        return _extract_single_monomial(children[0])

    # Factorial, function calls: not polynomial
    if op in TRANSCENDENTAL_OPS or op in ("factorial", "binomial"):
        return None

    # Addition inside a product: can't merge
    if op in ("add", "sub", "plus", "minus"):
        return None

    # Unknown: skip gracefully
    return None


def _extract_numeric(node):
    """Try to extract a non-negative integer from a node."""
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
    # Negation
    if node.get("op") == "neg":
        children = node.get("children", [])
        if children:
            v = _extract_numeric(children[0])
            if v is not None:
                return -v
        return None
    return None


# ── Newton polytope computation ──────────────────────────────────────

def compute_polytope(monomials, variables):
    """Compute Newton polytope from monomials.

    Returns dict with: dimension, vertices, n_vertices, volume, degree,
    n_monomials, vertex_hash.  Returns None if trivial.
    """
    if not monomials:
        return None

    # Build sorted variable list for consistent ordering
    var_list = sorted(variables) if variables else []
    dim = len(var_list)

    if dim == 0:
        # Pure constant
        return None

    # Convert monomials to exponent vectors
    points = []
    seen = set()
    for mono in monomials:
        vec = tuple(mono.get(v, 0) for v in var_list)
        if vec not in seen:
            points.append(vec)
            seen.add(vec)

    n_monomials = len(monomials)
    n_unique = len(points)
    degree = max(sum(p) for p in points) if points else 0

    if dim == 1:
        # 1D: polytope is interval [min_deg, max_deg]
        degs = [p[0] for p in points]
        mn, mx = min(degs), max(degs)
        verts = [(mn,), (mx,)] if mn != mx else [(mn,)]
        vol = float(mx - mn)
        vhash = _vertex_hash(verts)
        return {
            "dimension": 1,
            "vertices": [list(v) for v in verts],
            "n_vertices": len(verts),
            "volume": vol,
            "degree": degree,
            "n_monomials": n_monomials,
            "vertex_hash": vhash,
        }

    if n_unique < dim + 1:
        # Not enough points for a full-dimensional polytope
        verts = sorted(points)
        vhash = _vertex_hash(verts)
        return {
            "dimension": dim,
            "vertices": [list(v) for v in verts],
            "n_vertices": len(verts),
            "volume": 0.0,
            "degree": degree,
            "n_monomials": n_monomials,
            "vertex_hash": vhash,
        }

    # 2D+ convex hull
    try:
        import numpy as np
        from scipy.spatial import ConvexHull

        pts = np.array(points, dtype=np.float64)

        # Check if points are coplanar/collinear
        if dim == 2 and n_unique >= 3:
            try:
                hull = ConvexHull(pts)
                verts = sorted(tuple(int(x) for x in pts[i]) for i in hull.vertices)
                vol = float(hull.volume)  # area in 2D
            except Exception:
                verts = sorted(points)
                vol = 0.0
        elif dim >= 3 and n_unique >= dim + 1:
            try:
                hull = ConvexHull(pts)
                verts = sorted(tuple(int(x) for x in pts[i]) for i in hull.vertices)
                vol = float(hull.volume)
            except Exception:
                verts = sorted(points)
                vol = 0.0
        else:
            verts = sorted(points)
            vol = 0.0

        vhash = _vertex_hash(verts)
        return {
            "dimension": dim,
            "vertices": [list(v) for v in verts],
            "n_vertices": len(verts),
            "volume": vol,
            "degree": degree,
            "n_monomials": n_monomials,
            "vertex_hash": vhash,
        }
    except ImportError:
        # Fallback without scipy: just report vertices as all unique points
        verts = sorted(points)
        vhash = _vertex_hash(verts)
        return {
            "dimension": dim,
            "vertices": [list(v) for v in verts],
            "n_vertices": len(verts),
            "volume": 0.0,
            "degree": degree,
            "n_monomials": n_monomials,
            "vertex_hash": vhash,
        }


def _vertex_hash(vertices):
    """Hash sorted vertex coordinates to 16 hex chars."""
    s = str(vertices)
    return hashlib.md5(s.encode()).hexdigest()[:16]


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
    print("  Newton Polytope Extractor (S14)")
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

    poly_path = OUT_DIR / "newton_polytopes.jsonl"
    clust_path = OUT_DIR / "newton_clusters.jsonl"

    # Counters
    n_polynomial = 0
    n_rational = 0
    n_transcendental = 0
    n_mixed = 0
    n_extracted = 0
    n_skipped = 0
    processed = 0

    # Cluster accumulators
    cluster_formulas = defaultdict(list)
    cluster_domains = defaultdict(set)
    cluster_count = defaultdict(int)
    cluster_dims = defaultdict(set)

    t0 = time.time()

    def process_line(line, out_f):
        nonlocal processed, n_polynomial, n_rational, n_transcendental
        nonlocal n_mixed, n_extracted, n_skipped
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            n_skipped += 1
            return
        root = rec.get("root")
        if not root:
            n_skipped += 1
            return

        formula_hash = rec.get("hash", "")
        domain = domain_map.get(formula_hash, "unclassified")
        processed += 1

        # Classify
        poly_type = classify_formula(root)
        if poly_type == "transcendental":
            n_transcendental += 1
            return
        elif poly_type == "rational":
            n_rational += 1
        else:
            n_polynomial += 1

        # Extract monomials
        monomials, variables = extract_monomials(root)
        if not monomials or not variables:
            n_mixed += 1
            return

        # Compute polytope
        polytope = compute_polytope(monomials, variables)
        if polytope is None:
            n_mixed += 1
            return

        n_extracted += 1
        vhash = polytope["vertex_hash"]

        out_rec = {
            "hash": formula_hash,
            "poly_type": poly_type,
            "dimension": polytope["dimension"],
            "degree": polytope["degree"],
            "n_monomials": polytope["n_monomials"],
            "n_vertices": polytope["n_vertices"],
            "volume": round(polytope["volume"], 6),
            "vertex_hash": vhash,
            "vertices": polytope["vertices"],
        }
        out_f.write(json.dumps(out_rec, separators=(",", ":")) + "\n")

        # Accumulate clusters keyed on (dim, n_vertices, vertex_hash)
        ckey = vhash
        cluster_count[ckey] += 1
        cluster_domains[ckey].add(domain)
        cluster_dims[ckey].add(polytope["dimension"])
        if len(cluster_formulas[ckey]) < 5:
            cluster_formulas[ckey].append({
                "hash": formula_hash,
                "domain": domain,
                "poly_type": poly_type,
                "degree": polytope["degree"],
            })

    with open(poly_path, "w", encoding="utf-8") as out_f:
        if lines is not None:
            for line in lines:
                process_line(line, out_f)
                if processed % 500_000 == 0 and processed > 0:
                    elapsed = time.time() - t0
                    print(f"    {processed:,} processed  ({processed/elapsed:,.0f}/s)")
        else:
            with open(TREES_FILE, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if max_formulas and processed >= max_formulas:
                        break
                    process_line(line, out_f)
                    if processed % 500_000 == 0 and processed > 0:
                        elapsed = time.time() - t0
                        print(f"    {processed:,} processed  ({processed/elapsed:,.0f}/s)")

    elapsed = time.time() - t0

    # Write cluster file
    n_cross_domain = 0
    with open(clust_path, "w", encoding="utf-8") as cf:
        for vhash in sorted(cluster_count, key=lambda h: -cluster_count[h]):
            domains = sorted(cluster_domains[vhash])
            is_cross = len(domains) > 1 and not (len(domains) == 1 and domains[0] == "unclassified")
            if is_cross:
                n_cross_domain += 1
            rec = {
                "vertex_hash": vhash,
                "n_formulas": cluster_count[vhash],
                "dimensions": sorted(cluster_dims[vhash]),
                "domains": domains,
                "examples": cluster_formulas[vhash],
            }
            cf.write(json.dumps(rec, separators=(",", ":")) + "\n")

    n_unique = len(cluster_count)

    print()
    print("=" * 70)
    print("  Newton Polytope Extraction Complete")
    print(f"  {'=' * 38}")
    print(f"  Formulas processed:    {processed:>12,}")
    print(f"  Skipped (parse err):   {n_skipped:>12,}")
    print(f"  Polynomial:            {n_polynomial:>12,}")
    print(f"  Rational:              {n_rational:>12,}")
    print(f"  Transcendental:        {n_transcendental:>12,}")
    print(f"  Failed extraction:     {n_mixed:>12,}")
    print(f"  Polytopes extracted:   {n_extracted:>12,}")
    print(f"  Unique polytopes:      {n_unique:>12,}")
    print(f"  Cross-domain clusters: {n_cross_domain:>12,}")
    print(f"  Time:                  {elapsed:>11.1f}s")
    if elapsed > 0:
        print(f"  Rate:                  {processed/elapsed:>11,.0f}/s")
    print()

    top = sorted(cluster_count.items(), key=lambda kv: -kv[1])[:15]
    print("  Top 15 Newton polytope types:")
    for i, (vhash, cnt) in enumerate(top, 1):
        dims = sorted(cluster_dims[vhash])
        doms = sorted(cluster_domains[vhash])
        print(f"    {i:>2}. [{vhash}] n={cnt:>8,}  dim={dims}  domains={len(doms)}")
    print()
    print(f"  Output: {poly_path}")
    print(f"  Output: {clust_path}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Newton Polytope Extractor (S14)")
    parser.add_argument("--max-formulas", type=int, default=None,
                        help="Cap on total formulas to process")
    parser.add_argument("--sample", type=int, default=None,
                        help="Reservoir-sample N formulas instead of streaming all")
    args = parser.parse_args()
    process_formulas(max_formulas=args.max_formulas, sample_size=args.sample)


if __name__ == "__main__":
    main()
