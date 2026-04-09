"""
Gröbner Basis Signature Extractor (S15) — Gröbner basis invariants for multivariate polynomials.
=================================================================================================
For polynomial formula trees with 2-4 variables and degree <= 6, compute
the Gröbner basis and extract structural invariants.

Usage:
    python groebner_signatures.py                        # default (10K cap)
    python groebner_signatures.py --max-formulas 50000   # cap input
    python groebner_signatures.py --sample 5000          # random sample
"""

import argparse
import hashlib
import json
import random
import signal
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
TREES_FILE = ROOT / "cartography" / "convergence" / "data" / "formula_trees.jsonl"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_SIGS = OUT_DIR / "groebner_signatures.jsonl"

MAX_DEGREE = 6
MIN_VARS = 2
MAX_VARS = 4
TIMEOUT_SECONDS = 5
DEFAULT_MAX = 10000

# ── sympy imports ─────────────────────────────────────────────────────

try:
    import sympy
    from sympy import symbols, groebner as sympy_groebner, Poly, degree as sympy_degree
    _HAS_SYMPY = True
except ImportError:
    _HAS_SYMPY = False

# ── Timeout via threading (Windows-compatible) ────────────────────────

import threading
import concurrent.futures

def _run_with_timeout(func, timeout):
    """Run func() with a timeout. Returns result or raises TimeoutError."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            raise TimeoutError("Computation exceeded time limit")


# ── Tree helpers (shared pattern) ────────────────────────────────────

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


TRANSCENDENTAL_OPS = {"sin", "cos", "tan", "arcsin", "arccos", "arctan",
                      "sinh", "cosh", "tanh", "exp", "log", "ln", "lg",
                      "sqrt", "cbrt", "abs", "floor", "ceil", "sgn",
                      "limit", "integral", "sum", "prod", "diff"}


def _collect_ops(node, ops):
    if not isinstance(node, dict):
        return
    ntype = node.get("type", "")
    if ntype in ("operator", "equation", "group"):
        ops.add(node.get("op", ""))
    for c in node.get("children", []):
        _collect_ops(c, ops)


def _is_polynomial_tree(node):
    """Check if tree is a polynomial with 2-4 variables."""
    ops = set()
    _collect_ops(node, ops)
    if ops & TRANSCENDENTAL_OPS:
        return False, None
    if "div" in ops or "frac" in ops or "fraction" in ops:
        return False, None
    variables = _collect_variables(node)
    if len(variables) < MIN_VARS or len(variables) > MAX_VARS:
        return False, None
    return True, sorted(variables)


# ── Tree to sympy expression ────────────────────────────────────────

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
                return sympy.Integer(int(fv))
            return sympy.Rational(fv).limit_denominator(10000)
        except (ValueError, TypeError):
            return None

    if ntype == "variable":
        name = node.get("name", "")
        if name in var_map:
            return var_map[name]
        return None

    if op == "eq":
        # Take RHS
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
        if any(v is None or isinstance(v, (list, tuple)) for v in vals):
            return None
        try:
            result = vals[0]
            for v in vals[1:]:
                result = result + v
            return result
        except (TypeError, AttributeError):
            return None

    if op == "sub":
        vals = [_tree_to_sympy(c, var_map) for c in children]
        if any(v is None or isinstance(v, (list, tuple)) for v in vals) or len(vals) < 2:
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


# ── Gröbner basis computation ───────────────────────────────────────

def compute_groebner_signature(expr, sym_vars):
    """Compute Gröbner basis signature for a sympy polynomial expression."""
    try:
        poly = Poly(expr, *sym_vars)
    except Exception:
        return None

    total_deg = poly.total_degree()
    if total_deg > MAX_DEGREE or total_deg < 1:
        return None

    def _compute():
        gb = sympy_groebner([poly], *sym_vars, order='grevlex')
        return list(gb)

    try:
        gb_polys = _run_with_timeout(_compute, TIMEOUT_SECONDS)
    except (TimeoutError, Exception):
        return None

    if not gb_polys:
        return None

    n_basis = len(gb_polys)
    max_deg = 0
    total_terms = 0
    leading_terms = []

    for bp in gb_polys:
        try:
            p = Poly(bp, *sym_vars)
            d = p.total_degree()
            if d > max_deg:
                max_deg = d
            total_terms += len(p.as_dict())
            lt = p.LT()
            leading_terms.append(str(lt))
        except Exception:
            total_terms += 1
            leading_terms.append("?")

    lt_hash = hashlib.md5(str(sorted(leading_terms)).encode()).hexdigest()[:16]

    return {
        "n_basis_polys": n_basis,
        "max_degree_in_basis": max_deg,
        "total_terms_in_basis": total_terms,
        "leading_terms_hash": lt_hash,
        "input_degree": total_deg,
        "n_variables": len(sym_vars),
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
    print("  Gröbner Basis Signatures (S15)")
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

    n_multivar = 0
    n_computed = 0
    n_timeout = 0
    n_skip_degree = 0
    n_convert_fail = 0
    degree_dist = Counter()

    with open(OUT_SIGS, "w", encoding="utf-8") as out_f:
        for i, tree in enumerate(trees):
            if (i + 1) % 1000 == 0:
                print(f"  ... {i+1:,}/{len(trees):,} processed, "
                      f"{n_multivar} multivar, {n_computed} signatures")

            h = tree.get("hash", "")
            root = tree.get("root", {})

            is_poly, var_names = _is_polynomial_tree(root)
            if not is_poly:
                continue

            n_multivar += 1

            # Create sympy symbols
            sym_vars = symbols(var_names)
            if not isinstance(sym_vars, tuple):
                sym_vars = (sym_vars,)
            var_map = {name: sv for name, sv in zip(var_names, sym_vars)}

            # Convert tree to sympy
            try:
                expr = _tree_to_sympy(root, var_map)
            except Exception:
                expr = None
            if expr is None or isinstance(expr, (list, tuple)):
                n_convert_fail += 1
                continue

            # Compute signature
            sig = compute_groebner_signature(expr, sym_vars)
            if sig is None:
                n_timeout += 1
                continue

            n_computed += 1
            degree_dist[sig["input_degree"]] += 1

            rec = {
                "hash": h,
                "variables": var_names,
                **sig,
            }
            out_f.write(json.dumps(rec, default=_json_default,
                                   separators=(",", ":")) + "\n")

    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"  Gröbner Basis Signatures Complete")
    print(f"  {'=' * 38}")
    print(f"  Total trees:         {len(trees):>10,}")
    print(f"  Multivariate poly:   {n_multivar:>10,}")
    print(f"  Convert failures:    {n_convert_fail:>10,}")
    print(f"  Timeout/skip:        {n_timeout:>10,}")
    print(f"  Signatures:          {n_computed:>10,}")
    print(f"  Time:                {elapsed:>9.1f}s")
    print()
    print("  Degree distribution:")
    for deg, cnt in sorted(degree_dist.items()):
        print(f"    degree {deg}: {cnt:>8,}")
    print()
    print(f"  Output: {OUT_SIGS}")
    print("=" * 70)


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="S15: Gröbner basis signatures for multivariate polynomial formula trees"
    )
    parser.add_argument("--max-formulas", type=int, default=None,
                        help="Cap on number of formula trees to load (default: 10000)")
    parser.add_argument("--sample", type=int, default=None,
                        help="Random sample size (after loading)")
    args = parser.parse_args()
    run(max_formulas=args.max_formulas, sample_n=args.sample)


if __name__ == "__main__":
    main()
