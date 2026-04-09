"""
Automorphic Signatures (Strategy S21) — L-function coefficients & Sato-Tate.
==============================================================================
For polynomial formula trees, compute L-function-like coefficient sequences
a_p for small primes, classify by Sato-Tate distribution type, and compute
partial Euler products.

Usage:
    python automorphic_signatures.py
    python automorphic_signatures.py --max-formulas 50000
    python automorphic_signatures.py --sample 10000
"""

import argparse
import json
import math
import sys
import time
import random
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
TREES_FILE = ROOT / "cartography" / "convergence" / "data" / "formula_trees.jsonl"
FORMULAS_FILE = ROOT / "cartography" / "convergence" / "data" / "openwebmath_formulas.jsonl"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_FILE = OUT_DIR / "automorphic_signatures.jsonl"

# Small primes for L-function coefficient computation
SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23]

# Operators that keep us in polynomial world
POLY_OPS = {"add", "sub", "multiply", "power", "neg"}
RATIONAL_OPS = POLY_OPS | {"frac", "dfrac"}
TRANSCENDENTAL_OPS = {"sin", "cos", "log", "exp", "sqrt", "int", "sum"}
TRANSPARENT_OPS = {"eq", "paren"}

_JUNK_VARS = frozenset(",|.;:!?'\"()[]{}/ \\")


# ---------------------------------------------------------------------------
# Tree classification and evaluation (mirrors mod_p_signatures.py)
# ---------------------------------------------------------------------------

def _classify_tree(root):
    """Classify tree as polynomial, rational, transcendental, or opaque."""
    ops = set()
    has_subscript = False
    n_vars = set()

    def walk(node):
        nonlocal has_subscript
        if not isinstance(node, dict):
            return
        t = node.get("type", "")
        if t in ("operator", "equation", "relation"):
            op = node.get("op", "")
            if op == "subscript":
                has_subscript = True
            elif op not in TRANSPARENT_OPS and op:
                ops.add(op)
        elif t == "variable":
            name = node.get("name", "")
            if name and name not in _JUNK_VARS:
                n_vars.add(name)
        for c in node.get("children", []):
            walk(c)

    walk(root)

    single_chars = {v for v in n_vars if len(v) == 1}
    if len(single_chars) > 8:
        return "text_artifact", ops, n_vars

    if ops & TRANSCENDENTAL_OPS:
        return "transcendental", ops, n_vars
    if has_subscript:
        return "indexed", ops, n_vars
    if ops <= RATIONAL_OPS:
        if ops & {"frac", "dfrac"}:
            return "rational", ops, n_vars
        return "polynomial", ops, n_vars
    return "opaque", ops, n_vars


def _eval_tree_mod_p(node, var_val, p):
    """Evaluate a tree node mod p given variable assignments.

    Returns (value_mod_p, ok).
    """
    if not isinstance(node, dict):
        return (0, False)

    t = node.get("type", "")

    if t == "number":
        try:
            v = int(node["value"])
            return (v % p, True)
        except (ValueError, KeyError):
            try:
                v = float(node["value"])
                if v == int(v):
                    return (int(v) % p, True)
            except (ValueError, KeyError):
                pass
            return (0, False)

    if t == "variable":
        name = node.get("name", "")
        if not name or name in _JUNK_VARS:
            return (0, False)
        if name in var_val:
            return (var_val[name] % p, True)
        return (0, False)

    children = node.get("children", [])
    op = node.get("op", "")

    if t == "group" or op in TRANSPARENT_OPS:
        real_children = []
        for c in children:
            if isinstance(c, dict):
                if c.get("type") == "variable" and (
                        not c.get("name") or c.get("name") in _JUNK_VARS):
                    continue
                real_children.append(c)
        if not real_children:
            return (0, False)
        if len(real_children) == 1:
            return _eval_tree_mod_p(real_children[0], var_val, p)
        if op == "eq":
            return _eval_tree_mod_p(real_children[-1], var_val, p)
        result = 1
        for c in real_children:
            v, ok = _eval_tree_mod_p(c, var_val, p)
            if not ok:
                return (0, False)
            result = (result * v) % p
        return (result, True)

    if op == "add":
        total = 0
        for c in children:
            v, ok = _eval_tree_mod_p(c, var_val, p)
            if not ok:
                return (0, False)
            total = (total + v) % p
        return (total, True)

    if op == "sub":
        if len(children) < 2:
            return (0, False)
        left, ok1 = _eval_tree_mod_p(children[0], var_val, p)
        right, ok2 = _eval_tree_mod_p(children[1], var_val, p)
        if not (ok1 and ok2):
            return (0, False)
        return ((left - right) % p, True)

    if op == "neg":
        if not children:
            return (0, False)
        v, ok = _eval_tree_mod_p(children[0], var_val, p)
        if not ok:
            return (0, False)
        return ((-v) % p, True)

    if op == "multiply":
        result = 1
        for c in children:
            if isinstance(c, dict) and c.get("type") == "variable" and (
                    not c.get("name") or c.get("name") in _JUNK_VARS):
                continue
            v, ok = _eval_tree_mod_p(c, var_val, p)
            if not ok:
                return (0, False)
            result = (result * v) % p
        return (result, True)

    if op == "power":
        if len(children) < 2:
            return (0, False)
        base, ok1 = _eval_tree_mod_p(children[0], var_val, p)
        exp_val, ok2 = _eval_tree_mod_p(children[1], var_val, p)
        if not (ok1 and ok2):
            return (0, False)
        if exp_val < 0:
            if base % p == 0:
                return (0, False)
            inv = pow(base, p - 2, p)
            return (pow(inv, (-exp_val) % (p - 1), p), True)
        return (pow(base, exp_val, p), True)

    if op in ("frac", "dfrac"):
        if len(children) < 2:
            return (0, False)
        num, ok1 = _eval_tree_mod_p(children[0], var_val, p)
        den, ok2 = _eval_tree_mod_p(children[1], var_val, p)
        if not (ok1 and ok2):
            return (0, False)
        if den % p == 0:
            return (0, False)
        inv = pow(den, p - 2, p)
        return ((num * inv) % p, True)

    return (0, False)


# ---------------------------------------------------------------------------
# Automorphic signature computation
# ---------------------------------------------------------------------------

def count_roots_mod_p(root, p, variables):
    """Count N_p = #{x in Z/pZ : f(x) = 0 (mod p)}.

    For single-variable polynomials, evaluates f(x) for x = 0..p-1.
    For multi-variable, fixes all but one to sweep values.
    """
    if not variables:
        # Constant — check if it's zero
        val, ok = _eval_tree_mod_p(root, {}, p)
        if ok and val == 0:
            return p  # "all" points are roots of 0
        return 0

    # Pick evaluation variable
    sorted_vars = sorted(variables)
    eval_var = sorted_vars[0]
    other_vars = {v: 1 for v in sorted_vars[1:]}

    count = 0
    for x in range(p):
        var_val = dict(other_vars)
        var_val[eval_var] = x
        val, ok = _eval_tree_mod_p(root, var_val, p)
        if not ok:
            return None  # evaluation failed
        if val == 0:
            count += 1
    return count


def compute_a_p_vector(root, variables, primes=None):
    """Compute a_p = p - N_p for each small prime.

    Returns list of a_p values, or None if evaluation fails.
    """
    if primes is None:
        primes = SMALL_PRIMES

    a_p = []
    for p in primes:
        n_p = count_roots_mod_p(root, p, variables)
        if n_p is None:
            return None
        a_p.append(p - n_p)
    return a_p


def compute_sato_tate_angles(a_p, primes=None):
    """Compute Sato-Tate angles: theta_p = arccos(a_p / (2*sqrt(p))).

    Returns list of angles in [0, pi], or None if computation fails.
    Angles outside [-1, 1] for arccos argument are clamped.
    """
    if primes is None:
        primes = SMALL_PRIMES

    angles = []
    for ap_val, p in zip(a_p, primes):
        bound = 2 * math.sqrt(p)
        if bound < 1e-15:
            angles.append(math.pi / 2)  # degenerate
            continue
        arg = ap_val / bound
        # Clamp to [-1, 1] for arccos
        arg = max(-1.0, min(1.0, arg))
        theta = math.acos(arg)
        angles.append(theta)
    return angles


def classify_sato_tate(angles):
    """Classify the Sato-Tate distribution type from a set of angles.

    Returns (type, confidence) where type is one of:
    - "SU2" (semicircular — generic, non-CM)
    - "trivial" (uniform distribution — trivial character)
    - "CM" (concentrated — complex multiplication)
    - "unknown"
    """
    if not angles or len(angles) < 3:
        return "unknown", 0.0

    n = len(angles)
    mean_angle = sum(angles) / n
    var_angle = sum((a - mean_angle) ** 2 for a in angles) / n
    std_angle = math.sqrt(var_angle) if var_angle > 0 else 0

    # Expected stats for SU(2) Sato-Tate: mean ~ pi/2, std ~ pi/(2*sqrt(2))
    # ~0.785 and ~0.555
    su2_mean = math.pi / 2
    su2_std = math.pi / (2 * math.sqrt(2))  # ~ 1.11 / 2 ~ 0.555

    # Uniform on [0, pi]: mean ~ pi/2, std ~ pi/sqrt(12) ~ 0.907
    uniform_std = math.pi / math.sqrt(12)

    # CM: concentrated near specific angles, low variance
    # std << su2_std

    # Classify by comparing std
    if std_angle < 0.2:
        return "CM", min(1.0, (0.2 - std_angle) / 0.2)

    mean_err = abs(mean_angle - su2_mean)
    if mean_err < 0.3:
        # Mean is near pi/2; distinguish SU(2) vs uniform by std
        std_ratio_su2 = abs(std_angle - su2_std) / su2_std
        std_ratio_unif = abs(std_angle - uniform_std) / uniform_std

        if std_ratio_su2 < std_ratio_unif:
            conf = max(0, 1.0 - std_ratio_su2)
            return "SU2", round(conf, 4)
        else:
            conf = max(0, 1.0 - std_ratio_unif)
            return "trivial", round(conf, 4)

    return "unknown", 0.0


def compute_euler_product(a_p, primes=None, s=2.0):
    """Compute partial Euler product: prod(1 - a_p*p^(-s) + p^(1-2s)).

    This is the standard degree-2 L-function Euler product.
    """
    if primes is None:
        primes = SMALL_PRIMES

    product = 1.0
    for ap_val, p in zip(a_p, primes):
        term = 1.0 - ap_val * (p ** (-s)) + p ** (1 - 2 * s)
        if abs(term) < 1e-30:
            # Zero in Euler product — special
            return 0.0
        product *= term
    return product


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Automorphic signature extractor (S21)")
    ap.add_argument("--max-formulas", type=int, default=0,
                    help="Max formulas to process (0 = all)")
    ap.add_argument("--sample", type=int, default=0,
                    help="Reservoir sample size (0 = sequential)")
    ap.add_argument("--primes", type=str,
                    default=",".join(str(p) for p in SMALL_PRIMES),
                    help=f"Primes to use (default: {SMALL_PRIMES})")
    ap.add_argument("--skip-domains", action="store_true",
                    help="Skip domain lookup")
    args = ap.parse_args()

    primes = [int(x) for x in args.primes.split(",")]

    print("=" * 70)
    print("  Automorphic Signature Extractor (S21)")
    print(f"  Primes: {primes}")
    print("=" * 70)
    t0 = time.time()

    trees_path = TREES_FILE
    if not trees_path.exists():
        print(f"  ERROR: {trees_path} not found")
        sys.exit(1)

    limit = args.max_formulas if args.max_formulas else float("inf")
    sample_k = args.sample if args.sample else 0

    rng = random.Random(42)

    print(f"  Streaming {trees_path.name}...")
    if sample_k:
        print(f"  Reservoir sampling {sample_k:,} formulas")

    records = []
    reservoir = []
    stats = Counter()
    n_read = 0
    n_evaluable = 0

    with open(trees_path) as f:
        for i, line in enumerate(f):
            if i >= limit:
                break
            n_read = i + 1

            if i % 100000 == 0 and i > 0:
                elapsed = time.time() - t0
                rate = i / elapsed
                n_out = len(reservoir) if sample_k else len(records)
                print(f"    {i:,} read ({rate:.0f}/s) — "
                      f"{n_out:,} evaluable, skips: {dict(stats)}")

            try:
                d = json.loads(line)
            except Exception:
                stats["parse_error"] += 1
                continue

            h = d.get("hash", f"tree_{i}")
            root = d.get("root", {})

            # Classify tree
            kind, ops, variables = _classify_tree(root)
            if kind not in ("polynomial", "rational"):
                stats[f"skip_{kind}"] += 1
                continue

            # Compute a_p vector
            a_p = compute_a_p_vector(root, variables, primes)
            if a_p is None:
                stats["skip_eval_fail"] += 1
                continue

            # Sato-Tate angles
            angles = compute_sato_tate_angles(a_p, primes)
            st_type, st_conf = classify_sato_tate(angles)

            # Euler product at s=2
            euler = compute_euler_product(a_p, primes, s=2.0)

            # Basic stats
            mean_ap = sum(a_p) / len(a_p) if a_p else 0
            std_ap = (sum((v - mean_ap) ** 2 for v in a_p) / len(a_p)) ** 0.5 if len(a_p) > 1 else 0

            rec = {
                "hash": h,
                "a_p_vector": a_p,
                "sato_tate_type": st_type,
                "sato_tate_confidence": st_conf,
                "sato_tate_angles": [round(a, 6) for a in angles],
                "euler_product_at_2": round(euler, 8) if math.isfinite(euler) else None,
                "mean_a_p": round(mean_ap, 6),
                "std_a_p": round(std_ap, 6),
                "kind": kind,
                "n_vars": len(variables),
                "primes_used": primes,
            }

            if sample_k:
                n_evaluable += 1
                if len(reservoir) < sample_k:
                    reservoir.append(rec)
                else:
                    j = rng.randint(0, n_evaluable - 1)
                    if j < sample_k:
                        reservoir[j] = rec
            else:
                records.append(rec)

    if sample_k:
        records = reservoir

    elapsed = time.time() - t0

    # Write output
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    print(f"\n  Wrote {len(records):,} signatures to {OUT_FILE}")

    # Summary
    print()
    print("=" * 70)
    print("  SUMMARY")
    print(f"  Total formulas read:    {n_read:,}")
    print(f"  Evaluable:              {len(records):,}")
    print(f"  Skip breakdown:         {dict(stats)}")

    # Sato-Tate distribution
    st_counts = Counter(r["sato_tate_type"] for r in records)
    print(f"\n  Sato-Tate classification:")
    for st, cnt in st_counts.most_common():
        pct = 100 * cnt / max(len(records), 1)
        print(f"    {st:15s} {cnt:>7,}  ({pct:.1f}%)")

    # a_p statistics
    if records:
        all_mean_ap = [r["mean_a_p"] for r in records]
        all_std_ap = [r["std_a_p"] for r in records]
        print(f"\n  a_p statistics across formulas:")
        print(f"    mean(mean_a_p): {sum(all_mean_ap)/len(all_mean_ap):.4f}")
        print(f"    mean(std_a_p):  {sum(all_std_ap)/len(all_std_ap):.4f}")

    # Euler product distribution
    euler_vals = [r["euler_product_at_2"] for r in records
                  if r["euler_product_at_2"] is not None]
    if euler_vals:
        euler_sorted = sorted(euler_vals)
        print(f"\n  Euler product at s=2 (n={len(euler_vals):,}):")
        print(f"    min:    {euler_sorted[0]:.6f}")
        print(f"    median: {euler_sorted[len(euler_sorted)//2]:.6f}")
        print(f"    max:    {euler_sorted[-1]:.6f}")

    # Interesting: formulas near zero Euler product
    near_zero = [r for r in records
                 if r["euler_product_at_2"] is not None
                 and abs(r["euler_product_at_2"]) < 0.01]
    if near_zero:
        print(f"\n  Near-zero Euler products: {len(near_zero):,}")
        for r in near_zero[:5]:
            print(f"    {r['hash']}: euler={r['euler_product_at_2']:.8f}, "
                  f"ST={r['sato_tate_type']}")

    print(f"\n  Time:                   {elapsed:.1f}s")
    print("=" * 70)


if __name__ == "__main__":
    main()
