"""
ADE Singularity Signature Extractor (S19) — Arnold's ADE classification of singular points.
============================================================================================
For polynomial formula trees with exactly 2 variables, find singular points
and classify them by ADE type using Milnor number and corank.

Usage:
    python ade_singularity_signatures.py                        # default (10K cap)
    python ade_singularity_signatures.py --max-formulas 50000   # cap input
    python ade_singularity_signatures.py --sample 5000          # random sample
"""

import argparse
import hashlib
import json
import random
import sys
import time
import concurrent.futures
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
TREES_FILE = ROOT / "cartography" / "convergence" / "data" / "formula_trees.jsonl"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_SIGS = OUT_DIR / "ade_singularity_signatures.jsonl"

TIMEOUT_SECONDS = 5
DEFAULT_MAX = 10000

try:
    import sympy
    from sympy import symbols, diff, solve, Matrix, Rational, Integer
    _HAS_SYMPY = True
except ImportError:
    _HAS_SYMPY = False


def _run_with_timeout(func, timeout):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            raise TimeoutError("Computation exceeded time limit")


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


def _is_bivariate_poly(node):
    """Check if tree is a polynomial with exactly 2 variables."""
    ops = set()
    _collect_ops(node, ops)
    if ops & TRANSCENDENTAL_OPS:
        return False, None
    if "div" in ops or "frac" in ops or "fraction" in ops:
        return False, None
    variables = _collect_variables(node)
    if len(variables) != 2:
        return False, None
    return True, sorted(variables)


def _tree_to_sympy(node, var_map):
    """Convert formula tree to sympy expression."""
    if not isinstance(node, dict):
        return None
    ntype = node.get("type", "")
    op = node.get("op", "")
    children = node.get("children", [])

    if ntype == "number":
        try:
            v = node.get("value", 0)
            fv = float(v)
            if fv == int(fv) and abs(fv) < 1e12:
                return Integer(int(fv))
            return Rational(fv).limit_denominator(10000)
        except (ValueError, TypeError):
            return None

    if ntype == "variable":
        name = node.get("name", "")
        if name in var_map:
            return var_map[name]
        return None

    if op == "eq":
        if len(children) >= 2:
            return _tree_to_sympy(children[-1], var_map)
        return None
    if op == "paren" and children:
        return _tree_to_sympy(children[0], var_map)
    if op == "neg" and children:
        v = _tree_to_sympy(children[0], var_map)
        return -v if v is not None else None
    if op == "add":
        vals = [_tree_to_sympy(c, var_map) for c in children]
        if any(v is None for v in vals):
            return None
        return sum(vals[1:], vals[0])
    if op == "sub":
        vals = [_tree_to_sympy(c, var_map) for c in children]
        if any(v is None for v in vals) or len(vals) < 2:
            return None
        result = vals[0]
        for v in vals[1:]:
            result = result - v
        return result
    if op == "multiply":
        vals = [_tree_to_sympy(c, var_map) for c in children]
        if any(v is None for v in vals):
            return None
        result = vals[0]
        for v in vals[1:]:
            result = result * v
        return result
    if op == "power":
        if len(children) < 2:
            return None
        base = _tree_to_sympy(children[0], var_map)
        exp = _tree_to_sympy(children[1], var_map)
        if base is None or exp is None:
            return None
        try:
            return base ** exp
        except Exception:
            return None
    return None


# ── ADE classification ──────────────────────────────────────────────

def classify_ade(milnor, corank):
    """Classify singularity by Milnor number and corank."""
    if corank == 1:
        # A_n: x^(n+1) + y^2, milnor = n
        if milnor >= 1:
            return f"A_{milnor}"
    elif corank == 2:
        if milnor == 1:
            return "A_1"
        # D_n: x^2*y + y^(n-1), milnor = n, n >= 4
        if milnor >= 4:
            # Could be D_n or E_6/7/8
            if milnor == 6:
                return "D_6_or_E_6"
            elif milnor == 7:
                return "D_7_or_E_7"
            elif milnor == 8:
                return "D_8_or_E_8"
            else:
                return f"D_{milnor}"
        elif milnor == 2:
            return "A_2"
        elif milnor == 3:
            return "A_3"
    return f"unknown_mu{milnor}_cr{corank}"


def compute_ade_signature(expr, sym_x, sym_y):
    """Compute ADE singularity signature for a bivariate polynomial."""
    def _compute():
        fx = diff(expr, sym_x)
        fy = diff(expr, sym_y)

        # Find singular points
        try:
            sing_pts = solve([fx, fy], [sym_x, sym_y], dict=True)
        except Exception:
            sing_pts = []

        if not sing_pts:
            return None

        # Filter to numeric solutions only
        numeric_pts = []
        for pt in sing_pts:
            try:
                xv = complex(pt.get(sym_x, 0))
                yv = complex(pt.get(sym_y, 0))
                if abs(xv.imag) < 1e-10 and abs(yv.imag) < 1e-10:
                    numeric_pts.append((float(xv.real), float(yv.real)))
            except (TypeError, ValueError):
                continue

        if not numeric_pts:
            return None

        results = []
        for (x0, y0) in numeric_pts:
            # Compute Hessian at singular point
            fxx = diff(fx, sym_x)
            fxy = diff(fx, sym_y)
            fyy = diff(fy, sym_y)

            try:
                h11 = float(fxx.subs([(sym_x, x0), (sym_y, y0)]))
                h12 = float(fxy.subs([(sym_x, x0), (sym_y, y0)]))
                h22 = float(fyy.subs([(sym_x, x0), (sym_y, y0)]))
            except (TypeError, ValueError):
                continue

            H = [[h11, h12], [h12, h22]]
            # Rank of Hessian
            rank = 0
            det_h = h11 * h22 - h12 * h12
            if abs(h11) > 1e-10 or abs(h12) > 1e-10 or abs(h22) > 1e-10:
                rank = 1
            if abs(det_h) > 1e-10:
                rank = 2
            corank = 2 - rank

            # Approximate Milnor number as number of solutions of fx=fy=0
            # (counting multiplicity is hard; use len as lower bound)
            milnor = len(numeric_pts)

            ade_type = classify_ade(milnor, corank)
            results.append({
                "point": [round(x0, 8), round(y0, 8)],
                "milnor_approx": milnor,
                "corank": corank,
                "hessian_det": round(det_h, 8),
                "ade_type": ade_type,
            })

        if not results:
            return None

        # Aggregate signature
        ade_types = [r["ade_type"] for r in results]
        type_counts = Counter(ade_types)
        primary_type = type_counts.most_common(1)[0][0]

        return {
            "n_singular_points": len(results),
            "ade_type": primary_type,
            "all_ade_types": dict(type_counts),
            "milnor_number": results[0]["milnor_approx"],
            "corank": results[0]["corank"],
            "singular_points": results[:5],  # cap at 5 for output
        }

    try:
        return _run_with_timeout(_compute, TIMEOUT_SECONDS)
    except (TimeoutError, Exception):
        return None


# ── JSON default ──────────────────────────────────────────────────────

def _json_default(obj):
    if hasattr(obj, 'item'):
        return obj.item()
    return str(obj)


# ── Main pipeline ────────────────────────────────────────────────────

def run(max_formulas=None, sample_n=None):
    t0 = time.time()
    print("=" * 70)
    print("  ADE Singularity Signatures (S19)")
    print("=" * 70)

    if not _HAS_SYMPY:
        print("  ERROR: sympy not available")
        return

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

    n_bivar = 0
    n_computed = 0
    n_no_sing = 0
    n_convert_fail = 0
    n_timeout = 0
    ade_counter = Counter()

    with open(OUT_SIGS, "w", encoding="utf-8") as out_f:
        for i, tree in enumerate(trees):
            if (i + 1) % 1000 == 0:
                print(f"  ... {i+1:,}/{len(trees):,} processed, "
                      f"{n_bivar} bivariate, {n_computed} classified")

            h = tree.get("hash", "")
            root = tree.get("root", {})

            is_poly, var_names = _is_bivariate_poly(root)
            if not is_poly:
                continue

            n_bivar += 1
            sym_x, sym_y = symbols(var_names)
            var_map = {var_names[0]: sym_x, var_names[1]: sym_y}

            expr = _tree_to_sympy(root, var_map)
            if expr is None:
                n_convert_fail += 1
                continue

            sig = compute_ade_signature(expr, sym_x, sym_y)
            if sig is None:
                n_no_sing += 1
                continue

            n_computed += 1
            ade_counter[sig["ade_type"]] += 1

            rec = {
                "hash": h,
                "variables": var_names,
                **sig,
            }
            out_f.write(json.dumps(rec, default=_json_default,
                                   separators=(",", ":")) + "\n")

    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"  ADE Singularity Signatures Complete")
    print(f"  {'=' * 38}")
    print(f"  Total trees:         {len(trees):>10,}")
    print(f"  Bivariate poly:      {n_bivar:>10,}")
    print(f"  Convert failures:    {n_convert_fail:>10,}")
    print(f"  No singularities:    {n_no_sing:>10,}")
    print(f"  Timeout/error:       {n_timeout:>10,}")
    print(f"  Classified:          {n_computed:>10,}")
    print(f"  Time:                {elapsed:>9.1f}s")
    print()
    print("  ADE type distribution:")
    for ade, cnt in ade_counter.most_common(20):
        print(f"    {ade:<25} {cnt:>8,}")
    print()
    print(f"  Output: {OUT_SIGS}")
    print("=" * 70)


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="S19: ADE singularity signatures for bivariate polynomial formula trees"
    )
    parser.add_argument("--max-formulas", type=int, default=None,
                        help="Cap on number of formula trees to load (default: 10000)")
    parser.add_argument("--sample", type=int, default=None,
                        help="Random sample size (after loading)")
    args = parser.parse_args()
    run(max_formulas=args.max_formulas, sample_n=args.sample)


if __name__ == "__main__":
    main()
