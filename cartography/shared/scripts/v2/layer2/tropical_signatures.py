"""
Tropical Signature Extractor (S18/S30) — tropical skeleton of polynomial formulas.
====================================================================================
Tropicalize polynomial formulas: replace + with min, * with +.
For univariate: tropical variety = Newton polygon slopes.
For bivariate: tropical curve as planar graph dual to Newton subdivision.

Usage:
    python tropical_signatures.py                        # default (10K cap)
    python tropical_signatures.py --max-formulas 50000   # cap input
    python tropical_signatures.py --sample 5000          # random sample
"""

import argparse
import hashlib
import json
import math
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
TREES_FILE = ROOT / "cartography" / "convergence" / "data" / "formula_trees.jsonl"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_SIGS = OUT_DIR / "tropical_signatures.jsonl"

DEFAULT_MAX = 10000

# ── Tree helpers ──────────────────────────────────────────────────────

TRANSCENDENTAL_OPS = {"sin", "cos", "tan", "arcsin", "arccos", "arctan",
                      "sinh", "cosh", "tanh", "exp", "log", "ln", "lg",
                      "sqrt", "cbrt", "abs", "floor", "ceil", "sgn",
                      "limit", "integral", "sum", "prod", "diff"}


def _collect_variables(node):
    if not isinstance(node, dict):
        return set()
    if node.get("type") == "variable":
        name = node.get("name", "")
        if len(name) == 1 and name.isalpha():
            return {name}
        return set()
    out = set()
    for c in node.get("children", []):
        out |= _collect_variables(c)
    return out


def _collect_ops(node, ops):
    if not isinstance(node, dict):
        return
    ntype = node.get("type", "")
    if ntype in ("operator", "equation", "group"):
        ops.add(node.get("op", ""))
    for c in node.get("children", []):
        _collect_ops(c, ops)


def _is_polynomial_tree(node):
    """Check if tree is a polynomial."""
    ops = set()
    _collect_ops(node, ops)
    if ops & TRANSCENDENTAL_OPS:
        return False, None
    if "div" in ops or "frac" in ops or "fraction" in ops:
        return False, None
    variables = _collect_variables(node)
    if len(variables) < 1 or len(variables) > 4:
        return False, None
    return True, sorted(variables)


# ── Monomial extraction (from newton_polytope.py pattern) ────────────

def extract_monomials(node):
    """Extract list of (coeff, exponent_dict) pairs from a formula tree."""
    if not isinstance(node, dict):
        return None, None
    if node.get("op") == "eq":
        children = node.get("children", [])
        if len(children) >= 2:
            monos, vrs = _extract_additive_terms(children[-1])
            if monos is None:
                monos, vrs = _extract_additive_terms(children[0])
            return monos, vrs
    return _extract_additive_terms(node)


def _extract_additive_terms(node):
    if not isinstance(node, dict):
        return None, None
    op = node.get("op", "")
    children = node.get("children", [])

    if op in ("add", "sub", "plus", "minus"):
        all_monos = []
        all_vars = set()
        for ci, c in enumerate(children):
            monos, vrs = _extract_additive_terms(c)
            if monos is None:
                return None, None
            # Negate terms after first for subtraction
            if op in ("sub", "minus") and ci > 0:
                monos = [(-coeff, exp) for coeff, exp in monos]
            all_monos.extend(monos)
            if vrs:
                all_vars.update(vrs)
        return all_monos, all_vars

    mono = _extract_single_monomial(node)
    if mono is None:
        return None, None
    coeff, exp_dict = mono
    variables = {k for k in exp_dict if exp_dict[k] != 0}
    return [(coeff, exp_dict)], variables


def _extract_single_monomial(node):
    """Extract (coefficient, exponent_dict) from a multiplicative expression."""
    if not isinstance(node, dict):
        return None
    ntype = node.get("type", "")
    op = node.get("op", "")
    children = node.get("children", [])

    if ntype == "number":
        try:
            return (float(node.get("value", 0)), {})
        except (ValueError, TypeError):
            return None

    if ntype == "variable":
        name = node.get("name", "")
        if len(name) == 1 and name not in ("|", ",", ".", ""):
            return (1.0, {name: 1})
        return (1.0, {})

    if op == "neg" and children:
        m = _extract_single_monomial(children[0])
        if m is None:
            return None
        return (-m[0], m[1])

    if op == "power" and len(children) >= 2:
        base_m = _extract_single_monomial(children[0])
        if base_m is None:
            return None
        exp_val = _extract_numeric(children[1])
        if exp_val is None or exp_val < 0:
            return None
        coeff = base_m[0] ** exp_val if base_m[0] != 1.0 else 1.0
        exp_dict = {v: d * exp_val for v, d in base_m[1].items()}
        return (coeff, exp_dict)

    if op == "multiply" and children:
        coeff = 1.0
        exp_dict = {}
        for c in children:
            cm = _extract_single_monomial(c)
            if cm is None:
                return None
            coeff *= cm[0]
            for v, d in cm[1].items():
                exp_dict[v] = exp_dict.get(v, 0) + d
        return (coeff, exp_dict)

    if op == "paren" and len(children) == 1:
        return _extract_single_monomial(children[0])

    if op in TRANSCENDENTAL_OPS or op in ("factorial", "binomial"):
        return None
    if op in ("add", "sub", "plus", "minus"):
        return None

    return None


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


# ── Tropical geometry ───────────────────────────────────────────────

def _tropical_valuation(coeff):
    """Tropical valuation: -log|coeff| (using natural log).
    For coefficient 0, return infinity (will be dominated)."""
    if coeff == 0 or not math.isfinite(coeff):
        return float('inf')
    return -math.log(abs(coeff)) if abs(coeff) > 1e-300 else float('inf')


def compute_newton_polygon_slopes(monomials, var_list):
    """For univariate: compute lower convex hull slopes (Newton polygon).
    monomials: list of (coeff, exp_dict)
    var_list: single-element list [var_name]
    Returns sorted slopes.
    """
    var = var_list[0]
    points = []  # (degree, valuation)
    for coeff, exp_dict in monomials:
        deg = exp_dict.get(var, 0)
        val = _tropical_valuation(coeff)
        if math.isfinite(val):
            points.append((deg, val))

    if len(points) < 2:
        return [], points

    # Sort by degree
    points.sort()

    # Lower convex hull (Newton polygon)
    hull = []
    for p in points:
        while len(hull) >= 2:
            # Check if last point is above line from second-to-last to current
            (x0, y0), (x1, y1), (x2, y2) = hull[-2], hull[-1], p
            dx1, dy1 = x1 - x0, y1 - y0
            dx2, dy2 = x2 - x0, y2 - y0
            # Cross product: if >= 0, point is not below the line -> remove
            if dx1 * dy2 - dy1 * dx2 >= 0:
                hull.pop()
            else:
                break
        hull.append(p)

    # Compute slopes between consecutive hull points
    slopes = []
    for i in range(len(hull) - 1):
        dx = hull[i+1][0] - hull[i][0]
        dy = hull[i+1][1] - hull[i][1]
        if dx != 0:
            slopes.append(dy / dx)

    return slopes, hull


def compute_tropical_curve_2d(monomials, var_list):
    """For bivariate: compute tropical curve properties.
    The tropical curve is dual to the Newton polygon subdivision.

    Returns (n_edges, n_vertices, tropical_genus, newton_vertices).
    """
    v1, v2 = var_list[0], var_list[1]

    # Collect exponent points with valuations
    points = {}  # (i, j) -> valuation
    for coeff, exp_dict in monomials:
        i = exp_dict.get(v1, 0)
        j = exp_dict.get(v2, 0)
        val = _tropical_valuation(coeff)
        key = (i, j)
        if key not in points or val < points[key]:
            points[key] = val  # keep minimum valuation

    if len(points) < 2:
        return None

    # Newton polygon: convex hull of exponent points
    pts = list(points.keys())

    if len(pts) < 3:
        # Degenerate: line segment
        return {
            "n_edges": 1 if len(pts) == 2 else 0,
            "n_vertices": len(pts),
            "tropical_genus": 0,
            "newton_polygon_n_vertices": len(pts),
            "newton_polygon_n_segments": max(0, len(pts) - 1),
            "max_slope": 0.0,
        }

    # Compute convex hull using gift wrapping (simple, no scipy needed)
    hull_pts = _convex_hull_2d(pts)
    n_hull = len(hull_pts)

    # Slopes of hull edges
    slopes = []
    for k in range(n_hull):
        p1 = hull_pts[k]
        p2 = hull_pts[(k + 1) % n_hull]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        if dx != 0:
            slopes.append(abs(dy / dx))
        else:
            slopes.append(float('inf'))

    max_slope = max((s for s in slopes if math.isfinite(s)), default=0.0)

    # Tropical curve properties:
    # Number of interior lattice points = genus (by Baker-Norine)
    # Pick's theorem: A = I + B/2 - 1, where I = interior pts, B = boundary pts
    area = _polygon_area(hull_pts)
    boundary = _count_boundary_lattice_points(hull_pts)
    interior = round(area - boundary / 2 + 1)
    if interior < 0:
        interior = 0

    # Tropical curve dual: edges = hull edges + interior edges from subdivision
    # For the basic Newton polygon (no subdivision), edges = hull edges
    # Vertices of tropical curve ~ n_hull + interior_lattice_points
    n_tropical_edges = n_hull + max(0, interior)
    n_tropical_vertices = n_hull + max(0, interior - 1) if interior > 0 else n_hull

    return {
        "n_edges": n_tropical_edges,
        "n_vertices": n_tropical_vertices,
        "tropical_genus": interior,
        "newton_polygon_n_vertices": n_hull,
        "newton_polygon_n_segments": n_hull,
        "newton_polygon_area": round(area, 4),
        "max_slope": round(max_slope, 6),
    }


def _convex_hull_2d(points):
    """Simple 2D convex hull (Andrew's monotone chain)."""
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    def cross(O, A, B):
        return (A[0] - O[0]) * (B[1] - O[1]) - (A[1] - O[1]) * (B[0] - O[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]


def _polygon_area(hull):
    """Shoelace formula for polygon area."""
    n = len(hull)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += hull[i][0] * hull[j][1]
        area -= hull[j][0] * hull[i][1]
    return abs(area) / 2.0


def _count_boundary_lattice_points(hull):
    """Count lattice points on boundary of polygon."""
    n = len(hull)
    count = 0
    for i in range(n):
        j = (i + 1) % n
        dx = abs(hull[j][0] - hull[i][0])
        dy = abs(hull[j][1] - hull[i][1])
        count += math.gcd(dx, dy)
    return count


def compute_tropical_signature(monomials, variables, var_list):
    """Compute full tropical signature."""
    n_vars = len(var_list)

    if n_vars == 1:
        slopes, hull = compute_newton_polygon_slopes(monomials, var_list)
        if not hull:
            return None
        max_slope = max((abs(s) for s in slopes), default=0.0) if slopes else 0.0
        return {
            "n_edges": len(slopes),
            "n_vertices": len(hull),
            "tropical_genus": 0,  # univariate curves have genus 0 tropically
            "newton_polygon_n_segments": len(slopes),
            "max_slope": round(max_slope, 6),
            "slopes": [round(s, 6) for s in slopes],
            "dimension": 1,
        }

    if n_vars == 2:
        result = compute_tropical_curve_2d(monomials, var_list)
        if result is None:
            return None
        result["dimension"] = 2
        return result

    # 3-4 variables: just compute Newton polytope vertex count + basic info
    # Full tropical variety in 3D+ is too expensive
    pts = set()
    for coeff, exp_dict in monomials:
        vec = tuple(exp_dict.get(v, 0) for v in var_list)
        pts.add(vec)
    total_degree = max(sum(p) for p in pts) if pts else 0
    return {
        "n_edges": 0,
        "n_vertices": len(pts),
        "tropical_genus": 0,
        "newton_polygon_n_segments": 0,
        "max_slope": 0.0,
        "dimension": n_vars,
        "n_monomials": len(pts),
        "total_degree": total_degree,
    }


# ── JSON default ──────────────────────────────────────────────────────

def _json_default(obj):
    if hasattr(obj, 'item'):
        return obj.item()
    return str(obj)


# ── Main pipeline ────────────────────────────────────────────────────

def run(max_formulas=None, sample_n=None):
    t0 = time.time()
    print("=" * 70)
    print("  Tropical Signatures (S18/S30)")
    print("=" * 70)

    if not TREES_FILE.exists():
        print(f"  ERROR: {TREES_FILE} not found")
        return

    if max_formulas is None:
        max_formulas = DEFAULT_MAX

    print(f"\n  Loading formula trees from {TREES_FILE.name} (cap={max_formulas:,}) ...")
    trees = []
    with open(TREES_FILE, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                trees.append(json.loads(line))
            except json.JSONDecodeError:
                continue
            if len(trees) >= max_formulas:
                break
    print(f"  Loaded {len(trees):,} formula trees")

    if sample_n and sample_n < len(trees):
        random.seed(42)
        trees = random.sample(trees, sample_n)
        print(f"  Sampled {len(trees):,} trees")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    n_poly = 0
    n_computed = 0
    n_extract_fail = 0
    dim_counter = Counter()
    genus_counter = Counter()

    with open(OUT_SIGS, "w", encoding="utf-8") as out_f:
        for i, tree in enumerate(trees):
            if (i + 1) % 2000 == 0:
                print(f"  ... {i+1:,}/{len(trees):,} processed, "
                      f"{n_poly} polynomial, {n_computed} tropicalized")

            h = tree.get("hash", "")
            root = tree.get("root", {})

            is_poly, var_names = _is_polynomial_tree(root)
            if not is_poly:
                continue

            n_poly += 1

            monos, variables = extract_monomials(root)
            if monos is None or not variables:
                n_extract_fail += 1
                continue

            sig = compute_tropical_signature(monos, variables, var_names)
            if sig is None:
                n_extract_fail += 1
                continue

            n_computed += 1
            dim_counter[sig["dimension"]] += 1
            genus_counter[sig.get("tropical_genus", 0)] += 1

            rec = {
                "hash": h,
                "variables": var_names,
                **sig,
            }
            out_f.write(json.dumps(rec, default=_json_default,
                                   separators=(",", ":")) + "\n")

    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"  Tropical Signatures Complete")
    print(f"  {'=' * 38}")
    print(f"  Total trees:         {len(trees):>10,}")
    print(f"  Polynomial:          {n_poly:>10,}")
    print(f"  Extract failures:    {n_extract_fail:>10,}")
    print(f"  Tropicalized:        {n_computed:>10,}")
    print(f"  Time:                {elapsed:>9.1f}s")
    print()
    print("  Dimension distribution:")
    for d, cnt in sorted(dim_counter.items()):
        print(f"    dim {d}: {cnt:>8,}")
    print()
    print("  Tropical genus distribution:")
    for g, cnt in sorted(genus_counter.items())[:15]:
        print(f"    genus {g}: {cnt:>8,}")
    print()
    print(f"  Output: {OUT_SIGS}")
    print("=" * 70)


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="S18/S30: Tropical signatures — tropical skeleton of polynomial formulas"
    )
    parser.add_argument("--max-formulas", type=int, default=None,
                        help="Cap on number of formula trees to load (default: 10000)")
    parser.add_argument("--sample", type=int, default=None,
                        help="Random sample size (after loading)")
    args = parser.parse_args()
    run(max_formulas=args.max_formulas, sample_n=args.sample)


if __name__ == "__main__":
    main()
