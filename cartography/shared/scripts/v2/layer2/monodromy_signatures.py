"""
Monodromy Signature Extractor (S11) — singularity detection and classification.
================================================================================
For polynomial and rational formula trees, detect singularities (poles, branch
points, removable) and classify their monodromy type.

Usage:
    python monodromy_signatures.py                        # default (10K cap)
    python monodromy_signatures.py --max-formulas 50000   # cap input
    python monodromy_signatures.py --sample 5000          # random sample
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
OUT_SIGS = OUT_DIR / "monodromy_signatures.jsonl"

TIMEOUT_SECONDS = 5
DEFAULT_MAX = 10000

try:
    import sympy
    from sympy import (symbols, solve, limit, oo, Poly, cancel, fraction,
                       series, sqrt as sym_sqrt, Integer, Rational, denom, numer)
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

BRANCH_OPS = {"sqrt", "cbrt", "log", "ln"}
POLE_OPS = {"div", "frac", "fraction"}


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


def _has_neg_power(node):
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


def _classify_tree(node):
    """Classify tree and check suitability for monodromy analysis."""
    ops = set()
    _collect_ops(node, ops)
    variables = _collect_variables(node)
    if len(variables) != 1:
        return None, None, None

    var = sorted(variables)[0]
    has_branch = bool(ops & BRANCH_OPS)
    has_pole = bool(ops & POLE_OPS) or _has_neg_power(node)
    # Skip deeply transcendental (trig, Bessel, etc.) but allow sqrt/log
    disallowed = TRANSCENDENTAL_OPS - BRANCH_OPS
    if ops & disallowed:
        return None, None, None

    kind = "polynomial"
    if has_pole:
        kind = "rational"
    if has_branch:
        kind = "algebraic"  # has branch points

    return var, kind, has_branch


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
    if op in ("div", "frac", "fraction"):
        if len(children) < 2:
            return None
        num = _tree_to_sympy(children[0], var_map)
        den = _tree_to_sympy(children[1], var_map)
        if num is None or den is None:
            return None
        try:
            return num / den
        except Exception:
            return None
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
    if op == "sqrt" and children:
        v = _tree_to_sympy(children[0], var_map)
        return sym_sqrt(v) if v is not None else None
    if op == "cbrt" and children:
        v = _tree_to_sympy(children[0], var_map)
        return v ** Rational(1, 3) if v is not None else None
    if op in ("log", "ln") and children:
        v = _tree_to_sympy(children[0], var_map)
        return sympy.log(v) if v is not None else None

    return None


# ── Singularity analysis ────────────────────────────────────────────

def analyze_singularities(expr, sym_var, kind, has_branch):
    """Analyze singularities of expression."""
    def _compute():
        singularities = []

        # Find poles (zeros of denominator for rational functions)
        try:
            n, d = fraction(cancel(expr))
        except Exception:
            n, d = expr, Integer(1)

        poles = []
        if d != Integer(1) and d != 1:
            try:
                pole_candidates = solve(d, sym_var)
                for p in pole_candidates:
                    try:
                        pv = complex(p)
                        if abs(pv.imag) > 1e-8:
                            continue  # skip complex poles
                        pv = float(pv.real)
                    except (TypeError, ValueError):
                        continue

                    # Determine pole order
                    order = 1
                    try:
                        d_poly = Poly(d, sym_var)
                        # Count multiplicity
                        remainder = d_poly
                        factor = Poly(sym_var - p, sym_var)
                        for k in range(1, 10):
                            q, r = divmod(remainder, factor)
                            if r.is_zero:
                                order = k + 1
                                remainder = q
                            else:
                                order = k
                                break
                    except Exception:
                        pass

                    singularities.append({
                        "location": round(pv, 8),
                        "type": "pole",
                        "order": order,
                    })
                    poles.append(pv)
            except Exception:
                pass

        # Find branch points (for sqrt, log expressions)
        branch_points = []
        if has_branch:
            # Branch points of sqrt(g(x)): where g(x) = 0
            try:
                # Extract argument of sqrt/log from the expression
                for atom in expr.atoms(sympy.Pow):
                    exp_val = atom.args[1] if len(atom.args) > 1 else None
                    if exp_val is not None and exp_val == Rational(1, 2):
                        inner = atom.args[0]
                        bp_candidates = solve(inner, sym_var)
                        for bp in bp_candidates:
                            try:
                                bpv = complex(bp)
                                if abs(bpv.imag) > 1e-8:
                                    continue
                                bpv = float(bpv.real)
                                if bpv not in poles:
                                    singularities.append({
                                        "location": round(bpv, 8),
                                        "type": "branch_point",
                                        "order": 2,  # square root branch
                                    })
                                    branch_points.append(bpv)
                            except (TypeError, ValueError):
                                continue

                for atom in expr.atoms(sympy.log):
                    inner = atom.args[0] if atom.args else None
                    if inner is not None:
                        bp_candidates = solve(inner, sym_var)
                        for bp in bp_candidates:
                            try:
                                bpv = complex(bp)
                                if abs(bpv.imag) > 1e-8:
                                    continue
                                bpv = float(bpv.real)
                                singularities.append({
                                    "location": round(bpv, 8),
                                    "type": "branch_point",
                                    "order": 0,  # logarithmic branch
                                })
                                branch_points.append(bpv)
                            except (TypeError, ValueError):
                                continue
            except Exception:
                pass

        # Check for removable singularities among pole candidates
        removable = []
        final_sings = []
        for s in singularities:
            if s["type"] == "pole":
                try:
                    lim_val = limit(expr, sym_var, s["location"])
                    if lim_val.is_finite:
                        s["type"] = "removable"
                        removable.append(s)
                    else:
                        final_sings.append(s)
                except Exception:
                    final_sings.append(s)
            else:
                final_sings.append(s)

        all_sings = final_sings + removable

        if not all_sings:
            return None

        n_poles = sum(1 for s in all_sings if s["type"] == "pole")
        n_branch = sum(1 for s in all_sings if s["type"] == "branch_point")
        n_removable = sum(1 for s in all_sings if s["type"] == "removable")
        max_pole_order = max((s["order"] for s in all_sings if s["type"] == "pole"), default=0)

        loc_hash = hashlib.md5(
            str(sorted(s["location"] for s in all_sings)).encode()
        ).hexdigest()[:16]

        return {
            "n_singularities": len(all_sings),
            "n_poles": n_poles,
            "n_branch_points": n_branch,
            "n_removable": n_removable,
            "max_pole_order": max_pole_order,
            "singularity_locations_hash": loc_hash,
            "singularities": all_sings[:8],  # cap detail
            "formula_kind": kind,
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
    print("  Monodromy Signatures (S11)")
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

    n_eligible = 0
    n_computed = 0
    n_no_sing = 0
    n_convert_fail = 0
    type_counter = Counter()
    kind_counter = Counter()

    with open(OUT_SIGS, "w", encoding="utf-8") as out_f:
        for i, tree in enumerate(trees):
            if (i + 1) % 1000 == 0:
                print(f"  ... {i+1:,}/{len(trees):,} processed, "
                      f"{n_eligible} eligible, {n_computed} analyzed")

            h = tree.get("hash", "")
            root = tree.get("root", {})

            var_name, kind, has_branch = _classify_tree(root)
            if var_name is None:
                continue

            # Pure polynomials in one variable have no singularities
            if kind == "polynomial" and not has_branch:
                continue

            n_eligible += 1
            sym_var = symbols(var_name)
            var_map = {var_name: sym_var}

            expr = _tree_to_sympy(root, var_map)
            if expr is None:
                n_convert_fail += 1
                continue

            sig = analyze_singularities(expr, sym_var, kind, has_branch)
            if sig is None:
                n_no_sing += 1
                continue

            n_computed += 1
            kind_counter[kind] += 1
            for s in sig.get("singularities", []):
                type_counter[s["type"]] += 1

            rec = {
                "hash": h,
                "variable": var_name,
                **sig,
            }
            out_f.write(json.dumps(rec, default=_json_default,
                                   separators=(",", ":")) + "\n")

    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"  Monodromy Signatures Complete")
    print(f"  {'=' * 38}")
    print(f"  Total trees:         {len(trees):>10,}")
    print(f"  Eligible (rat/alg):  {n_eligible:>10,}")
    print(f"  Convert failures:    {n_convert_fail:>10,}")
    print(f"  No singularities:    {n_no_sing:>10,}")
    print(f"  Analyzed:            {n_computed:>10,}")
    print(f"  Time:                {elapsed:>9.1f}s")
    print()
    print("  Formula kind distribution:")
    for k, cnt in kind_counter.most_common():
        print(f"    {k:<20} {cnt:>8,}")
    print()
    print("  Singularity type distribution:")
    for t, cnt in type_counter.most_common():
        print(f"    {t:<20} {cnt:>8,}")
    print()
    print(f"  Output: {OUT_SIGS}")
    print("=" * 70)


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="S11: Monodromy signatures — singularity detection and classification"
    )
    parser.add_argument("--max-formulas", type=int, default=None,
                        help="Cap on number of formula trees to load (default: 10000)")
    parser.add_argument("--sample", type=int, default=None,
                        help="Random sample size (after loading)")
    args = parser.parse_args()
    run(max_formulas=args.max_formulas, sample_n=args.sample)


if __name__ == "__main__":
    main()
