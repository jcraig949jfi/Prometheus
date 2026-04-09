"""
Differential Galois Signature Extractor (S20/S29) — classify differential Galois groups.
=========================================================================================
For formula trees that represent differential equations, classify the differential
Galois group based on solution type from sympy.dsolve.

Most formulas are NOT ODEs, so this has a low hit rate by design.
The few that match are high-value bridges.

Usage:
    python diff_galois_signatures.py                        # default (10K cap)
    python diff_galois_signatures.py --max-formulas 50000   # cap input
    python diff_galois_signatures.py --sample 5000          # random sample
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
OUT_SIGS = OUT_DIR / "diff_galois_signatures.jsonl"

TIMEOUT_SECONDS = 5
DEFAULT_MAX = 10000

try:
    import sympy
    from sympy import (symbols, Function, Eq, dsolve, classify_ode,
                       Derivative, Integer, Rational, exp as sym_exp,
                       sin, cos, log as sym_log, sqrt as sym_sqrt,
                       besselj, bessely, airyai, airybi)
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

DIFF_OPS = {"diff", "partial", "derivative", "d/dx", "nabla", "prime"}


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


def _has_diff_op(node):
    """Check if tree contains differential operators."""
    ops = set()
    _collect_ops(node, ops)
    if ops & DIFF_OPS:
        return True
    # Also check for prime notation (y', y'')
    return _has_prime_notation(node)


def _has_prime_notation(node):
    """Check for prime (') notation in variable names."""
    if not isinstance(node, dict):
        return False
    if node.get("type") == "variable":
        name = node.get("name", "")
        if "'" in name or "prime" in name.lower():
            return True
    if node.get("op") == "prime":
        return True
    for c in node.get("children", []):
        if _has_prime_notation(c):
            return True
    return False


def _is_ode_tree(node):
    """Check if tree looks like an ODE."""
    if not _has_diff_op(node):
        return False, None, None

    variables = _collect_variables(node)
    # ODE needs exactly 1 independent variable, possibly function name(s)
    # Common: x is independent, y is dependent
    single_char_vars = {v for v in variables if len(v) == 1}

    # Heuristic: most ODEs use x as independent and y as dependent
    # or t as independent and y/x as dependent
    indep = None
    dep = None
    if 'x' in single_char_vars and 'y' in single_char_vars:
        indep, dep = 'x', 'y'
    elif 't' in single_char_vars and 'y' in single_char_vars:
        indep, dep = 't', 'y'
    elif 't' in single_char_vars and 'x' in single_char_vars:
        indep, dep = 't', 'x'
    elif len(single_char_vars) == 2:
        sv = sorted(single_char_vars)
        indep, dep = sv[0], sv[1]
    else:
        return False, None, None

    return True, indep, dep


def _detect_ode_order(node, dep_name):
    """Detect the order of the ODE from the tree."""
    max_order = 0

    if not isinstance(node, dict):
        return 0

    op = node.get("op", "")
    children = node.get("children", [])

    # Check for diff operator
    if op in ("diff", "partial", "derivative"):
        # Order = number of differentiation variables or exponent
        order = max(1, len(children) - 1)
        if order > max_order:
            max_order = order

    # Check for prime notation
    if node.get("type") == "variable":
        name = node.get("name", "")
        if name.startswith(dep_name):
            primes = name.count("'")
            if primes > max_order:
                max_order = primes
    if op == "prime":
        max_order = max(max_order, 1)
        # Check for double prime
        for c in children:
            if isinstance(c, dict) and c.get("op") == "prime":
                max_order = max(max_order, 2)

    for c in children:
        child_order = _detect_ode_order(c, dep_name)
        if child_order > max_order:
            max_order = child_order

    return max_order


# ── ODE solving and classification ──────────────────────────────────

def _tree_to_ode_expr(node, var_map, func_sym, indep_sym):
    """Convert formula tree to sympy expression suitable for ODE.
    Replaces dependent variable with Function, derivatives with Derivative.
    """
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
        # Handle prime notation
        if name and name[0] in var_map:
            primes = name.count("'")
            if primes > 0 and name[0] == str(func_sym).replace("(" + str(indep_sym) + ")", "")[0:1]:
                return Derivative(func_sym, (indep_sym, primes))
        return None

    if op == "eq":
        if len(children) >= 2:
            lhs = _tree_to_ode_expr(children[0], var_map, func_sym, indep_sym)
            rhs = _tree_to_ode_expr(children[-1], var_map, func_sym, indep_sym)
            if lhs is not None and rhs is not None:
                return Eq(lhs, rhs)
            if rhs is not None:
                return rhs
        return None

    if op == "paren" and children:
        return _tree_to_ode_expr(children[0], var_map, func_sym, indep_sym)

    if op == "neg" and children:
        v = _tree_to_ode_expr(children[0], var_map, func_sym, indep_sym)
        return -v if v is not None else None

    if op in ("diff", "partial", "derivative"):
        # First child is the function being differentiated
        if children:
            inner = _tree_to_ode_expr(children[0], var_map, func_sym, indep_sym)
            if inner is not None:
                order = max(1, len(children) - 1)
                return Derivative(func_sym, (indep_sym, order))
        return Derivative(func_sym, indep_sym)

    if op == "prime":
        if children:
            return Derivative(func_sym, indep_sym)
        return Derivative(func_sym, indep_sym)

    if op == "add":
        vals = [_tree_to_ode_expr(c, var_map, func_sym, indep_sym) for c in children]
        if any(v is None for v in vals):
            return None
        return sum(vals[1:], vals[0])

    if op == "sub":
        vals = [_tree_to_ode_expr(c, var_map, func_sym, indep_sym) for c in children]
        if any(v is None for v in vals) or len(vals) < 2:
            return None
        result = vals[0]
        for v in vals[1:]:
            result = result - v
        return result

    if op == "multiply":
        vals = [_tree_to_ode_expr(c, var_map, func_sym, indep_sym) for c in children]
        if any(v is None for v in vals):
            return None
        result = vals[0]
        for v in vals[1:]:
            result = result * v
        return result

    if op in ("div", "frac", "fraction"):
        if len(children) < 2:
            return None
        num = _tree_to_ode_expr(children[0], var_map, func_sym, indep_sym)
        den = _tree_to_ode_expr(children[1], var_map, func_sym, indep_sym)
        if num is None or den is None:
            return None
        try:
            return num / den
        except Exception:
            return None

    if op == "power":
        if len(children) < 2:
            return None
        base = _tree_to_ode_expr(children[0], var_map, func_sym, indep_sym)
        exp_v = _tree_to_ode_expr(children[1], var_map, func_sym, indep_sym)
        if base is None or exp_v is None:
            return None
        try:
            return base ** exp_v
        except Exception:
            return None

    if op == "sqrt" and children:
        v = _tree_to_ode_expr(children[0], var_map, func_sym, indep_sym)
        return sym_sqrt(v) if v is not None else None

    if op == "exp" and children:
        v = _tree_to_ode_expr(children[0], var_map, func_sym, indep_sym)
        return sym_exp(v) if v is not None else None

    if op == "sin" and children:
        v = _tree_to_ode_expr(children[0], var_map, func_sym, indep_sym)
        return sin(v) if v is not None else None

    if op == "cos" and children:
        v = _tree_to_ode_expr(children[0], var_map, func_sym, indep_sym)
        return cos(v) if v is not None else None

    if op in ("log", "ln") and children:
        v = _tree_to_ode_expr(children[0], var_map, func_sym, indep_sym)
        return sym_log(v) if v is not None else None

    return None


def classify_solution_type(sol_expr):
    """Classify the solution expression to determine differential Galois group."""
    s = str(sol_expr)
    atoms_types = set()

    # Check what functions appear in solution
    for atom in sol_expr.atoms():
        t = type(atom).__name__
        atoms_types.add(t)

    # Check for specific function types
    has_exp = bool(sol_expr.atoms(sympy.exp))
    has_trig = bool(sol_expr.atoms(sin, cos))
    has_log = bool(sol_expr.atoms(sympy.log))
    has_bessel = bool(sol_expr.atoms(besselj, bessely))
    has_airy = bool(sol_expr.atoms(airyai, airybi))
    has_poly_only = not (has_exp or has_trig or has_log or has_bessel or has_airy)

    # Classify differential Galois group
    if has_bessel or has_airy:
        return {
            "solution_type": "special_function",
            "diff_galois_class": "SL2",
            "is_liouvillian": False,
            "solution_functions": sorted(atoms_types & {"besselj", "bessely", "airyai", "airybi"}),
        }
    elif has_poly_only:
        return {
            "solution_type": "polynomial",
            "diff_galois_class": "trivial",
            "is_liouvillian": True,
            "solution_functions": [],
        }
    elif has_exp and not has_trig and not has_log:
        return {
            "solution_type": "exponential",
            "diff_galois_class": "Ga",  # additive group
            "is_liouvillian": True,
            "solution_functions": ["exp"],
        }
    elif has_trig and not has_exp:
        return {
            "solution_type": "trigonometric",
            "diff_galois_class": "Gm",  # multiplicative group
            "is_liouvillian": True,
            "solution_functions": sorted({"sin", "cos"} & {type(a).__name__ for a in sol_expr.atoms()}),
        }
    elif has_log and not has_exp and not has_trig:
        return {
            "solution_type": "logarithmic",
            "diff_galois_class": "Gm",
            "is_liouvillian": True,
            "solution_functions": ["log"],
        }
    elif has_exp and has_trig:
        return {
            "solution_type": "exp_trig",
            "diff_galois_class": "Gm_ext",  # extension of multiplicative
            "is_liouvillian": True,
            "solution_functions": sorted({"exp", "sin", "cos"} & atoms_types),
        }
    else:
        return {
            "solution_type": "mixed",
            "diff_galois_class": "unknown",
            "is_liouvillian": None,
            "solution_functions": [],
        }


def compute_diff_galois_signature(ode_expr, func_sym, indep_sym, dep_name, order):
    """Attempt to solve ODE and classify differential Galois group."""
    def _compute():
        # Try to classify the ODE first
        try:
            ode_class = classify_ode(ode_expr, func_sym)
        except Exception:
            ode_class = ()

        # Try to solve
        try:
            sol = dsolve(ode_expr, func_sym)
        except Exception:
            # Can't solve - still report what we can
            if ode_class:
                return {
                    "equation_order": order,
                    "solution_type": "unsolvable_by_CAS",
                    "diff_galois_class": "unknown",
                    "is_liouvillian": None,
                    "ode_classification": list(ode_class)[:5] if ode_class else [],
                }
            return None

        # Classify the solution
        if isinstance(sol, list):
            sol_expr = sol[0].rhs if hasattr(sol[0], 'rhs') else sol[0]
        elif hasattr(sol, 'rhs'):
            sol_expr = sol.rhs
        else:
            sol_expr = sol

        galois_info = classify_solution_type(sol_expr)

        return {
            "equation_order": order,
            **galois_info,
            "ode_classification": list(ode_class)[:5] if ode_class else [],
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
    print("  Differential Galois Signatures (S20/S29)")
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

    n_ode = 0
    n_computed = 0
    n_convert_fail = 0
    n_timeout = 0
    galois_counter = Counter()
    order_counter = Counter()
    sol_type_counter = Counter()

    with open(OUT_SIGS, "w", encoding="utf-8") as out_f:
        for i, tree in enumerate(trees):
            if (i + 1) % 1000 == 0:
                print(f"  ... {i+1:,}/{len(trees):,} processed, "
                      f"{n_ode} ODEs found, {n_computed} classified")

            h = tree.get("hash", "")
            root = tree.get("root", {})

            is_ode, indep_name, dep_name = _is_ode_tree(root)
            if not is_ode:
                continue

            n_ode += 1
            order = _detect_ode_order(root, dep_name)
            if order < 1:
                continue

            # Set up sympy symbols
            indep_sym = symbols(indep_name)
            dep_func = Function(dep_name)
            func_sym = dep_func(indep_sym)

            var_map = {
                indep_name: indep_sym,
                dep_name: func_sym,
            }

            # Convert tree to ODE expression
            ode_expr = _tree_to_ode_expr(root, var_map, func_sym, indep_sym)
            if ode_expr is None:
                n_convert_fail += 1
                continue

            # If it's an Eq, use directly; otherwise assume = 0
            if not isinstance(ode_expr, Eq):
                ode_expr = Eq(ode_expr, 0)

            sig = compute_diff_galois_signature(ode_expr, func_sym, indep_sym, dep_name, order)
            if sig is None:
                n_timeout += 1
                continue

            n_computed += 1
            galois_counter[sig["diff_galois_class"]] += 1
            order_counter[sig["equation_order"]] += 1
            sol_type_counter[sig["solution_type"]] += 1

            rec = {
                "hash": h,
                "independent_var": indep_name,
                "dependent_var": dep_name,
                **sig,
            }
            out_f.write(json.dumps(rec, default=_json_default,
                                   separators=(",", ":")) + "\n")

    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"  Differential Galois Signatures Complete")
    print(f"  {'=' * 38}")
    print(f"  Total trees:         {len(trees):>10,}")
    print(f"  ODE candidates:      {n_ode:>10,}")
    print(f"  Convert failures:    {n_convert_fail:>10,}")
    print(f"  Timeout/error:       {n_timeout:>10,}")
    print(f"  Classified:          {n_computed:>10,}")
    print(f"  Time:                {elapsed:>9.1f}s")
    print()
    print("  Differential Galois group distribution:")
    for g, cnt in galois_counter.most_common():
        print(f"    {g:<20} {cnt:>8,}")
    print()
    print("  ODE order distribution:")
    for o, cnt in sorted(order_counter.items()):
        print(f"    order {o}: {cnt:>8,}")
    print()
    print("  Solution type distribution:")
    for t, cnt in sol_type_counter.most_common():
        print(f"    {t:<25} {cnt:>8,}")
    print()
    print(f"  Output: {OUT_SIGS}")
    print("=" * 70)


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="S20/S29: Differential Galois signatures for ODE formula trees"
    )
    parser.add_argument("--max-formulas", type=int, default=None,
                        help="Cap on number of formula trees to load (default: 10000)")
    parser.add_argument("--sample", type=int, default=None,
                        help="Random sample size (after loading)")
    args = parser.parse_args()
    run(max_formulas=args.max_formulas, sample_n=args.sample)


if __name__ == "__main__":
    main()
