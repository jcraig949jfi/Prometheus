"""
Functional Equation Signature Detector (S31) — structural symmetry patterns.
=============================================================================
Walk formula trees looking for structural patterns that indicate functional
equations: reflection f(1-x), shift f(x+n), scaling f(cx), multiplicative
f(x)*f(y)=f(xy), and duplication f(2x)=...f(x).

This is tree pattern matching: for each formula tree, check if any subtree
matches known functional equation skeletons.

Usage:
    python functional_equation_signatures.py                        # full run
    python functional_equation_signatures.py --max-formulas 50000   # cap input
    python functional_equation_signatures.py --sample 10000         # random sample
"""

import argparse
import json
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
TREES_FILE = ROOT / "cartography" / "convergence" / "data" / "formula_trees.jsonl"
FORMULAS_FILE = ROOT / "cartography" / "convergence" / "data" / "openwebmath_formulas.jsonl"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_SIGS = OUT_DIR / "functional_equation_signatures.jsonl"


# ── Tree walking utilities ──────────────────────────────────────────────

def _collect_variables(node):
    """Return set of single-letter variable names in the tree."""
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


def _is_variable(node):
    """Check if node is a variable leaf."""
    return isinstance(node, dict) and node.get("type") == "variable"


def _is_number(node):
    """Check if node is a number leaf."""
    return isinstance(node, dict) and node.get("type") == "number"


def _get_number(node):
    """Extract numeric value from a number node, or None."""
    if not _is_number(node):
        return None
    try:
        return float(node.get("value", 0))
    except (ValueError, TypeError):
        return None


def _has_variable(node):
    """Check if subtree contains any variable."""
    if not isinstance(node, dict):
        return False
    if node.get("type") == "variable":
        return True
    return any(_has_variable(c) for c in node.get("children", []))


def _is_pure_number(node):
    """Check if subtree contains only numbers (no variables)."""
    if not isinstance(node, dict):
        return False
    if node.get("type") == "variable":
        return False
    if node.get("type") == "number":
        return True
    return all(_is_pure_number(c) for c in node.get("children", []))


# ── Functional equation detectors ──────────────────────────────────────

# Each detector walks the tree and returns True if the pattern is found.
# We look for compositions like op(const, variable) fed into a function.

def _contains_function_call(node):
    """Check if tree contains any function-like operator (sin, cos, f, etc.)."""
    if not isinstance(node, dict):
        return False
    ntype = node.get("type", "")
    op = node.get("op", "")
    # Known function operators
    func_ops = {"sin", "cos", "tan", "arcsin", "arccos", "arctan",
                "sinh", "cosh", "tanh", "exp", "log", "ln",
                "sqrt", "Gamma", "zeta", "function"}
    if op in func_ops or ntype == "function":
        return True
    return any(_contains_function_call(c) for c in node.get("children", []))


def detect_reflection(node):
    """Detect reflection symmetry: f(1-x), f(-x), f(N-x) patterns.

    Look for sub(N, V) where N is a constant and V contains a variable,
    appearing as argument to a function or operator.
    """
    found = []
    stack = [node]
    while stack:
        n = stack.pop()
        if not isinstance(n, dict):
            continue
        op = n.get("op", "")
        children = n.get("children", [])

        # Pattern: sub(constant, variable_expr) or sub(number, variable)
        if op == "sub" and len(children) >= 2:
            left, right = children[0], children[1]
            if _is_pure_number(left) and _has_variable(right):
                const_val = _get_number(left)
                found.append({
                    "type": "reflection",
                    "constant": const_val,
                    "pattern": f"({const_val}-x)",
                })

        # Pattern: neg(variable) → f(-x)
        if op == "neg" and len(children) >= 1:
            if _has_variable(children[0]):
                # Check if this neg is an argument to a function
                found.append({
                    "type": "negation_reflection",
                    "pattern": "(-x)",
                })

        for c in children:
            stack.append(c)

    return found


def detect_shift(node):
    """Detect shift symmetry: f(x+1), f(x+n) patterns.

    Look for add(V, N) or sub(V, N) where V contains a variable and
    N is a constant.
    """
    found = []
    stack = [node]
    while stack:
        n = stack.pop()
        if not isinstance(n, dict):
            continue
        op = n.get("op", "")
        children = n.get("children", [])

        if op in ("add", "sub") and len(children) >= 2:
            for i, c in enumerate(children):
                others = [children[j] for j in range(len(children)) if j != i]
                if _has_variable(c):
                    for o in others:
                        if _is_pure_number(o):
                            const_val = _get_number(o)
                            sign = "+" if op == "add" else "-"
                            found.append({
                                "type": "shift",
                                "shift_value": const_val,
                                "pattern": f"(x{sign}{const_val})",
                            })

        for c in children:
            stack.append(c)

    return found


def detect_scaling(node):
    """Detect scaling symmetry: f(cx) or f(x/c) patterns.

    Look for multiply(N, V) or div/frac(V, N) where N is constant
    and V contains a variable.
    """
    found = []
    stack = [node]
    while stack:
        n = stack.pop()
        if not isinstance(n, dict):
            continue
        op = n.get("op", "")
        children = n.get("children", [])

        if op == "multiply" and len(children) >= 2:
            has_var_child = False
            const_children = []
            for c in children:
                if _has_variable(c):
                    has_var_child = True
                elif _is_pure_number(c):
                    const_children.append(c)
            if has_var_child and const_children:
                for cc in const_children:
                    const_val = _get_number(cc)
                    if const_val is not None and const_val != 1.0:
                        found.append({
                            "type": "scaling",
                            "scale_factor": const_val,
                            "pattern": f"({const_val}*x)",
                        })

        if op in ("frac", "div", "fraction") and len(children) >= 2:
            if _has_variable(children[0]) and _is_pure_number(children[1]):
                const_val = _get_number(children[1])
                if const_val is not None and const_val != 0:
                    found.append({
                        "type": "scaling",
                        "scale_factor": 1.0 / const_val,
                        "pattern": f"(x/{const_val})",
                    })

        for c in children:
            stack.append(c)

    return found


def detect_multiplicative(node):
    """Detect multiplicative structure: f(x)*f(y) patterns.

    Look for multiply nodes where two or more children are function
    applications on different variables.
    """
    found = []
    stack = [node]
    while stack:
        n = stack.pop()
        if not isinstance(n, dict):
            continue
        op = n.get("op", "")
        children = n.get("children", [])

        if op == "multiply" and len(children) >= 2:
            func_children = []
            for c in children:
                if _contains_function_call(c) and _has_variable(c):
                    func_children.append(c)
            if len(func_children) >= 2:
                # Check if different variables
                var_sets = [_collect_variables(fc) for fc in func_children]
                all_vars = set()
                for vs in var_sets:
                    all_vars |= vs
                if len(all_vars) >= 2 or len(func_children) >= 2:
                    found.append({
                        "type": "multiplicative",
                        "n_function_factors": len(func_children),
                        "pattern": "f(x)*f(y)",
                    })

        for c in children:
            stack.append(c)

    return found


def detect_duplication(node):
    """Detect duplication formulas: f(2x) = ...f(x)... patterns.

    Look for a tree that contains both multiply(2, V) and the same
    function applied to V alone.
    """
    found = []

    # Collect all "multiply(2, V)" subtrees and all function applications
    scaling_by_2 = []
    func_apps = []

    stack = [node]
    while stack:
        n = stack.pop()
        if not isinstance(n, dict):
            continue
        op = n.get("op", "")
        children = n.get("children", [])

        if op == "multiply" and len(children) >= 2:
            for i, c in enumerate(children):
                val = _get_number(c)
                if val is not None and abs(val - 2.0) < 1e-10:
                    others = [children[j] for j in range(len(children)) if j != i]
                    for o in others:
                        if _has_variable(o):
                            scaling_by_2.append(_collect_variables(o))

        # Track function applications
        func_ops = {"sin", "cos", "tan", "exp", "log", "ln", "sqrt",
                    "Gamma", "zeta", "function"}
        if op in func_ops and children:
            for c in children:
                if _has_variable(c):
                    func_apps.append(_collect_variables(c))

        for c in children:
            stack.append(c)

    # If we have scaling by 2 AND function applications on overlapping variables
    if scaling_by_2 and func_apps:
        for s_vars in scaling_by_2:
            for f_vars in func_apps:
                if s_vars & f_vars:
                    found.append({
                        "type": "duplication",
                        "pattern": "f(2x)=...f(x)...",
                    })
                    break
            if found:
                break

    return found


def detect_equation_structure(node):
    """Detect if the tree is an equation (has = sign) and analyze both sides."""
    if not isinstance(node, dict):
        return None
    op = node.get("op", "")
    children = node.get("children", [])

    if op == "eq" and len(children) >= 2:
        lhs = children[0]
        rhs = children[1]
        lhs_vars = _collect_variables(lhs)
        rhs_vars = _collect_variables(rhs)
        lhs_has_func = _contains_function_call(lhs)
        rhs_has_func = _contains_function_call(rhs)
        return {
            "is_equation": True,
            "lhs_vars": sorted(lhs_vars),
            "rhs_vars": sorted(rhs_vars),
            "lhs_has_function": lhs_has_func,
            "rhs_has_function": rhs_has_func,
            "shared_vars": sorted(lhs_vars & rhs_vars),
        }
    return None


# ── Classify functional equation type ──────────────────────────────────

def classify_functional_equation(reflections, shifts, scalings,
                                  multiplicatives, duplications, eq_info):
    """Assign a functional equation type label based on detected patterns."""
    types = []

    if reflections:
        # Check for specific reflection values
        for r in reflections:
            if r.get("constant") == 1.0:
                types.append("reflection_1-x")
            elif r.get("type") == "negation_reflection":
                types.append("reflection_-x")
            else:
                types.append("reflection_N-x")

    if shifts:
        shift_vals = [s.get("shift_value") for s in shifts if s.get("shift_value") is not None]
        if any(abs(v - 1.0) < 1e-10 for v in shift_vals if v is not None):
            types.append("shift_1")
        elif shift_vals:
            types.append("shift_N")

    if scalings:
        types.append("scaling")

    if multiplicatives:
        types.append("multiplicative")

    if duplications:
        types.append("duplication")

    if not types:
        return "none"

    return "+".join(sorted(set(types)))


# ── Domain lookup ──────────────────────────────────────────────────────

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


# ── Main pipeline ──────────────────────────────────────────────────────

def run(max_formulas=None, sample_n=None):
    t0 = time.time()
    print("=" * 70)
    print("Functional Equation Signatures (S31)")
    print("=" * 70)

    if not TREES_FILE.exists():
        print(f"  ERROR: {TREES_FILE} not found")
        return

    domain_map = load_domain_map(max_load=max_formulas)

    # Load formula trees
    print(f"\n  Loading formula trees from {TREES_FILE.name} ...")
    trees = []
    with open(TREES_FILE, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                trees.append(json.loads(line))
            except json.JSONDecodeError:
                continue
            if max_formulas and len(trees) >= max_formulas:
                break
    print(f"  Loaded {len(trees):,} formula trees")

    if sample_n and sample_n < len(trees):
        random.seed(42)
        trees = random.sample(trees, sample_n)
        print(f"  Sampled {len(trees):,} trees")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    n_processed = 0
    n_with_pattern = 0
    n_skipped = 0
    type_counter = Counter()
    pattern_counter = Counter()
    domain_pattern_counter = defaultdict(Counter)

    with open(OUT_SIGS, "w", encoding="utf-8") as out_f:
        for i, tree in enumerate(trees):
            if (i + 1) % 50000 == 0:
                elapsed = time.time() - t0
                rate = (i + 1) / elapsed if elapsed > 0 else 0
                print(f"  ... {i+1:,}/{len(trees):,} processed, "
                      f"{n_with_pattern} with patterns ({rate:,.0f}/s)")

            h = tree.get("hash", "")
            root = tree.get("root", {})
            domain = domain_map.get(h, "unclassified")

            if not isinstance(root, dict):
                n_skipped += 1
                continue

            n_processed += 1

            # Detect all pattern types
            reflections = detect_reflection(root)
            shifts = detect_shift(root)
            scalings = detect_scaling(root)
            multiplicatives = detect_multiplicative(root)
            duplications = detect_duplication(root)
            eq_info = detect_equation_structure(root)

            has_reflection = len(reflections) > 0
            has_shift = len(shifts) > 0
            has_scaling = len(scalings) > 0
            has_multiplicative = len(multiplicatives) > 0
            has_duplication = len(duplications) > 0

            fe_type = classify_functional_equation(
                reflections, shifts, scalings,
                multiplicatives, duplications, eq_info
            )

            has_any = (has_reflection or has_shift or has_scaling
                       or has_multiplicative or has_duplication)
            if has_any:
                n_with_pattern += 1

            type_counter[fe_type] += 1
            if has_reflection:
                pattern_counter["reflection"] += 1
            if has_shift:
                pattern_counter["shift"] += 1
            if has_scaling:
                pattern_counter["scaling"] += 1
            if has_multiplicative:
                pattern_counter["multiplicative"] += 1
            if has_duplication:
                pattern_counter["duplication"] += 1
            if has_any:
                domain_pattern_counter[domain][fe_type] += 1

            rec = {
                "hash": h,
                "domain": domain,
                "has_reflection": has_reflection,
                "has_shift": has_shift,
                "has_scaling": has_scaling,
                "has_multiplicative": has_multiplicative,
                "has_duplication": has_duplication,
                "functional_eq_type": fe_type,
                "n_reflections": len(reflections),
                "n_shifts": len(shifts),
                "n_scalings": len(scalings),
                "is_equation": eq_info["is_equation"] if eq_info else False,
            }

            # Add detail for formulas with patterns
            if has_any:
                details = {}
                if reflections:
                    details["reflections"] = reflections[:3]
                if shifts:
                    details["shifts"] = shifts[:3]
                if scalings:
                    details["scalings"] = scalings[:3]
                if multiplicatives:
                    details["multiplicatives"] = multiplicatives[:3]
                if duplications:
                    details["duplications"] = duplications[:1]
                rec["details"] = details

            out_f.write(json.dumps(rec, separators=(",", ":")) + "\n")

    elapsed = time.time() - t0

    # Summary
    print(f"\n{'=' * 70}")
    print(f"  Functional Equation Signatures Complete")
    print(f"  {'=' * 42}")
    print(f"  Formulas processed:   {n_processed:>10,}")
    print(f"  Skipped (parse err):  {n_skipped:>10,}")
    print(f"  With any pattern:     {n_with_pattern:>10,}"
          f"  ({100*n_with_pattern/n_processed:.1f}%)" if n_processed else "")
    print(f"  Time:                 {elapsed:>9.1f}s")
    if elapsed > 0:
        print(f"  Rate:                 {n_processed/elapsed:>9,.0f}/s")
    print()
    print("  Pattern counts:")
    for pat in ("reflection", "shift", "scaling", "multiplicative", "duplication"):
        c = pattern_counter.get(pat, 0)
        pct = 100 * c / n_processed if n_processed else 0
        print(f"    {pat:<20} {c:>8,}  ({pct:5.1f}%)")
    print()
    print("  Top 20 functional equation types:")
    for fe_type, cnt in type_counter.most_common(20):
        pct = 100 * cnt / n_processed if n_processed else 0
        print(f"    {fe_type:<40} {cnt:>8,}  ({pct:5.1f}%)")
    print()
    print("  Top domains with patterns:")
    domain_totals = {d: sum(tc.values()) for d, tc in domain_pattern_counter.items()}
    for d, total in sorted(domain_totals.items(), key=lambda kv: -kv[1])[:15]:
        print(f"    {d:<30} {total:>8,}")
    print()
    print(f"  Output: {OUT_SIGS}")
    print("=" * 70)


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="S31: Functional equation symmetry signatures from formula trees"
    )
    parser.add_argument("--max-formulas", type=int, default=None,
                        help="Cap on number of formula trees to load")
    parser.add_argument("--sample", type=int, default=None,
                        help="Random sample size (after loading)")
    args = parser.parse_args()
    run(max_formulas=args.max_formulas, sample_n=args.sample)


if __name__ == "__main__":
    main()
