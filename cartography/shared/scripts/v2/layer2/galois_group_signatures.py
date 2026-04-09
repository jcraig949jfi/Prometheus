"""
Galois Group Signature Extractor (S10) — heuristic Galois group classification.
================================================================================
For polynomial formula trees of degree <= 7, estimate the Galois group using
discriminant-based heuristics and root analysis.

  - Degree 2: always Z/2Z
  - Degree 3: discriminant square test -> Z/3Z vs S_3
  - Degree 4: resolvent cubic discriminant -> V_4, D_4, A_4, S_4
  - Degree 5+: discriminant sign + real root count -> heuristic classification

Falls back to sympy.galois_group() if available (handles degree <= 5 exactly).

Usage:
    python galois_group_signatures.py                        # full run
    python galois_group_signatures.py --max-formulas 50000   # cap input
    python galois_group_signatures.py --sample 10000         # random sample
"""

import argparse
import hashlib
import json
import math
import random
import sys
import time
import warnings
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
TREES_FILE = ROOT / "cartography" / "convergence" / "data" / "formula_trees.jsonl"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_SIGS = OUT_DIR / "galois_group_signatures.jsonl"

MAX_DEGREE = 7

# Try to import sympy for exact Galois group computation
_HAS_SYMPY = False
try:
    from sympy import Poly, ZZ
    from sympy.abc import x as sym_x
    _HAS_SYMPY = True
except ImportError:
    pass


# ── Coefficient extraction (shared with discriminant_signatures.py) ────

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


def _ops_allowed(node, allowed):
    if not isinstance(node, dict):
        return True
    ntype = node.get("type", "")
    if ntype in ("operator", "equation", "group"):
        op = node.get("op", "")
        if op and op not in allowed:
            return False
    for c in node.get("children", []):
        if not _ops_allowed(c, allowed):
            return False
    return True


def _is_polynomial_tree(node):
    allowed_ops = {"add", "sub", "multiply", "neg", "power", "eq", "paren"}
    variables = _collect_variables(node)
    if len(variables) != 1:
        return False, None
    var = variables.pop()
    if not _ops_allowed(node, allowed_ops):
        return False, None
    return True, var


def _eval_tree(node, var_name, var_val):
    if not isinstance(node, dict):
        return None
    ntype = node.get("type", "")
    if ntype == "number":
        try:
            return float(node.get("value", 0))
        except (ValueError, TypeError):
            return None
    if ntype == "variable":
        name = node.get("name", "")
        if name == var_name:
            return var_val
        return None
    children = node.get("children", [])
    op = node.get("op", "")
    if op == "eq":
        if len(children) >= 2:
            return _eval_tree(children[1], var_name, var_val)
        return None
    if op == "paren":
        if children:
            return _eval_tree(children[0], var_name, var_val)
        return None
    if op == "neg":
        if children:
            v = _eval_tree(children[0], var_name, var_val)
            return -v if v is not None else None
        return None
    if op == "add":
        vals = [_eval_tree(c, var_name, var_val) for c in children]
        if any(v is None for v in vals):
            return None
        return sum(vals)
    if op == "sub":
        vals = [_eval_tree(c, var_name, var_val) for c in children]
        if any(v is None for v in vals) or len(vals) < 2:
            return None
        return vals[0] - sum(vals[1:])
    if op == "multiply":
        vals = [_eval_tree(c, var_name, var_val) for c in children]
        if any(v is None for v in vals):
            return None
        result = 1.0
        for v in vals:
            result *= v
        return result
    if op == "power":
        if len(children) < 2:
            return None
        base = _eval_tree(children[0], var_name, var_val)
        exp = _eval_tree(children[1], var_name, var_val)
        if base is None or exp is None:
            return None
        try:
            return base ** exp
        except (OverflowError, ValueError, ZeroDivisionError):
            return None
    return None


def extract_coefficients(node, var_name, max_degree=20):
    test_points = list(range(max_degree + 2))
    vals = []
    for p in test_points:
        v = _eval_tree(node, var_name, float(p))
        if v is None or not np.isfinite(v):
            return None
        if abs(v) > 1e15:
            return None
        vals.append(v)
    vals = np.array(vals, dtype=np.float64)
    diffs = vals.copy()
    degree = 0
    for d in range(max_degree + 1):
        if np.allclose(diffs, 0, atol=1e-8):
            break
        degree = d
        diffs = np.diff(diffs)
    else:
        degree = max_degree
    if degree == 0:
        return [float(vals[0])]
    x = np.array(test_points[:degree + 2], dtype=np.float64)
    y = vals[:degree + 2]
    try:
        coeffs = np.polyfit(x, y, degree)
        coeffs = coeffs[::-1].tolist()
        snapped = []
        for c in coeffs:
            r = round(c)
            if abs(c - r) < 1e-6:
                snapped.append(float(r))
            else:
                snapped.append(round(c, 10))
        return snapped
    except (np.linalg.LinAlgError, ValueError):
        return None


# ── Discriminant computation ────────────────────────────────────────────

def compute_discriminant(coeffs):
    """Compute discriminant of polynomial [a_0, ..., a_d]."""
    d = len(coeffs) - 1
    if d < 2:
        return None
    a_d = coeffs[d]
    if abs(a_d) < 1e-15:
        return None
    if d == 2:
        a, b, c = coeffs[2], coeffs[1], coeffs[0]
        return b * b - 4 * a * c
    if d == 3:
        a, b, c, dd = coeffs[3], coeffs[2], coeffs[1], coeffs[0]
        return (18*a*b*c*dd - 4*b**3*dd + b**2*c**2 - 4*a*c**3 - 27*a**2*dd**2)
    # General: Sylvester resultant
    f_prime = [coeffs[i] * i for i in range(1, len(coeffs))]
    if not f_prime:
        f_prime = [0.0]
    S = _sylvester_matrix(coeffs, f_prime)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res = np.linalg.det(S)
    except np.linalg.LinAlgError:
        return None
    sign_exp = (d * (d - 1)) // 2
    sign = (-1) ** sign_exp
    return sign * res / a_d


def _sylvester_matrix(p, q):
    p_hi = list(reversed(p))
    q_hi = list(reversed(q))
    m = len(q_hi) - 1
    n = len(p_hi) - 1
    size = m + n
    if size == 0:
        return np.array([[1.0]])
    S = np.zeros((size, size))
    for i in range(m):
        for j, c in enumerate(p_hi):
            if i + j < size:
                S[i, i + j] = c
    for i in range(n):
        for j, c in enumerate(q_hi):
            if m + i + j < size:
                S[m + i, i + j] = c
    return S


# ── Perfect square test ────────────────────────────────────────────────

def is_perfect_square(n):
    """Test whether n (float from discriminant) is a perfect square integer."""
    if n is None:
        return None
    try:
        n_int = int(round(n))
    except (OverflowError, ValueError):
        return None
    if n_int < 0:
        return False
    if n_int == 0:
        return True
    s = int(math.isqrt(abs(n_int)))
    return s * s == n_int


# ── Resolvent cubic for degree 4 ───────────────────────────────────────

def resolvent_cubic_coeffs(coeffs):
    """For a degree-4 polynomial a4*x^4 + a3*x^3 + a2*x^2 + a1*x + a0,
    compute the resolvent cubic y^3 - a2*y^2 + (a1*a3 - 4*a0)*y - (a1^2*a4 - 4*a0*a2 + a0*a3^2).
    Coefficients [c_0, c_1, c_2, c_3] (our convention: index = degree).

    Actually uses the depressed form. Input: [a0, a1, a2, a3, a4].
    Resolvent cubic: y^3 - a2*y^2 + (a1*a3 - 4*a0*a4)*y - (a0*a3^2 - 4*a0*a2*a4 + a1^2*a4)
    as coefficients [c0, c1, c2, c3=1].
    """
    if len(coeffs) != 5:
        return None
    a0, a1, a2, a3, a4 = coeffs
    # Resolvent cubic coefficients (standard form)
    c3 = 1.0
    c2 = -a2
    c1 = a1 * a3 - 4 * a0 * a4
    c0 = -(a0 * a3**2 - 4 * a0 * a2 * a4 + a1**2 * a4)
    return [c0, c1, c2, c3]


# ── Galois group classification ────────────────────────────────────────

def classify_galois_group(coeffs, disc):
    """Classify the Galois group heuristically based on degree, discriminant,
    and root analysis."""
    d = len(coeffs) - 1

    if d < 2:
        return None

    disc_is_square = is_perfect_square(disc) if disc is not None else None

    # Count real roots via numpy
    try:
        # numpy polyval uses highest-degree-first
        np_coeffs = list(reversed(coeffs))
        roots = np.roots(np_coeffs)
        n_real = sum(1 for r in roots if abs(r.imag) < 1e-8)
    except Exception:
        n_real = None

    if d == 2:
        return {
            "galois_group": "Z/2Z",
            "galois_order": 2,
            "is_solvable": True,
            "disc_is_square": disc_is_square,
            "n_real_roots": n_real,
            "method": "exact_d2",
        }

    if d == 3:
        if disc_is_square is True:
            group_name = "Z/3Z"
            group_order = 3
        else:
            group_name = "S_3"
            group_order = 6
        return {
            "galois_group": group_name,
            "galois_order": group_order,
            "is_solvable": True,
            "disc_is_square": disc_is_square,
            "n_real_roots": n_real,
            "method": "disc_square_d3",
        }

    if d == 4:
        # Use resolvent cubic to distinguish V_4, D_4, A_4, S_4
        res_coeffs = resolvent_cubic_coeffs(coeffs)
        res_disc = None
        res_disc_square = None
        if res_coeffs is not None:
            res_disc = compute_discriminant(res_coeffs)
            res_disc_square = is_perfect_square(res_disc) if res_disc is not None else None

        # Count rational roots of resolvent cubic (heuristic: integer roots near test points)
        n_rational_resolvent = 0
        if res_coeffs is not None:
            try:
                res_np = list(reversed(res_coeffs))
                res_roots = np.roots(res_np)
                for r in res_roots:
                    if abs(r.imag) < 1e-8:
                        r_real = r.real
                        if abs(r_real - round(r_real)) < 1e-6:
                            n_rational_resolvent += 1
            except Exception:
                pass

        if disc_is_square is True:
            if n_rational_resolvent == 3:
                group_name = "V_4"
                group_order = 4
            else:
                group_name = "A_4"
                group_order = 12
        else:
            if n_rational_resolvent >= 1:
                group_name = "D_4"
                group_order = 8
            else:
                group_name = "S_4"
                group_order = 24

        return {
            "galois_group": group_name,
            "galois_order": group_order,
            "is_solvable": True,
            "disc_is_square": disc_is_square,
            "n_real_roots": n_real,
            "method": "resolvent_d4",
        }

    if d == 5:
        # Try sympy first
        if _HAS_SYMPY:
            try:
                int_coeffs = [int(round(c)) for c in coeffs]
                poly = Poly(sum(int_coeffs[i] * sym_x**i for i in range(len(int_coeffs))),
                           sym_x, domain=ZZ)
                G, _ = poly.galois_group()
                group_name = str(G)
                group_order = G.order()
                is_solvable = G.is_solvable
                return {
                    "galois_group": group_name,
                    "galois_order": int(group_order),
                    "is_solvable": bool(is_solvable),
                    "disc_is_square": disc_is_square,
                    "n_real_roots": n_real,
                    "method": "sympy_d5",
                }
            except Exception:
                pass

        # Heuristic for degree 5
        # S_5 (order 120) is most common; A_5 if disc is square
        if disc_is_square is True:
            group_name = "A_5"
            group_order = 60
            is_solvable = False
        else:
            # Could be S_5, D_5, Z/5Z, F_20, etc. Default to S_5
            if n_real is not None:
                if n_real == 1:
                    group_name = "S_5"
                    group_order = 120
                    is_solvable = False
                elif n_real == 5:
                    group_name = "Z/5Z_or_D_5"
                    group_order = 10  # heuristic: could be 5 or 10
                    is_solvable = True
                else:
                    group_name = "S_5"
                    group_order = 120
                    is_solvable = False
            else:
                group_name = "S_5"
                group_order = 120
                is_solvable = False

        return {
            "galois_group": group_name,
            "galois_order": group_order,
            "is_solvable": is_solvable,
            "disc_is_square": disc_is_square,
            "n_real_roots": n_real,
            "method": "heuristic_d5",
        }

    # Degree 6-7: very rough heuristic
    if disc_is_square is True:
        group_name = f"A_{d}"
        group_order = math.factorial(d) // 2
        is_solvable = False  # A_n not solvable for n >= 5
    else:
        group_name = f"S_{d}"
        group_order = math.factorial(d)
        is_solvable = False

    return {
        "galois_group": group_name,
        "galois_order": group_order,
        "is_solvable": is_solvable,
        "disc_is_square": disc_is_square,
        "n_real_roots": n_real,
        "method": f"heuristic_d{d}",
    }


# ── Coefficient dedup ──────────────────────────────────────────────────

def _coeff_dedup_key(coeffs):
    rounded = tuple(round(c, 8) for c in coeffs)
    return hashlib.md5(str(rounded).encode()).hexdigest()


# ── JSON default ────────────────────────────────────────────────────────

def _json_default(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, complex):
        return {"re": obj.real, "im": obj.imag}
    return str(obj)


# ── Main pipeline ──────────────────────────────────────────────────────

def run(max_formulas=None, sample_n=None):
    t0 = time.time()
    print("=" * 70)
    print("Galois Group Signatures (S10)")
    print("=" * 70)

    if not TREES_FILE.exists():
        print(f"  ERROR: {TREES_FILE} not found")
        return

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

    print(f"  sympy available: {_HAS_SYMPY}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    n_poly = 0
    n_classified = 0
    n_deduped = 0
    n_skipped_degree = 0
    seen_coeff_keys = set()
    group_counter = Counter()

    with open(OUT_SIGS, "w", encoding="utf-8") as out_f:
        for i, tree in enumerate(trees):
            if (i + 1) % 50000 == 0:
                print(f"  ... {i+1:,}/{len(trees):,} processed, "
                      f"{n_poly} polynomials, {n_classified} classified")

            h = tree.get("hash", "")
            root = tree.get("root", {})

            is_poly, var = _is_polynomial_tree(root)
            if not is_poly:
                continue

            coeffs = extract_coefficients(root, var)
            if coeffs is None or len(coeffs) < 3:
                continue

            degree = len(coeffs) - 1
            if degree > MAX_DEGREE:
                n_skipped_degree += 1
                continue

            # Dedup
            ckey = _coeff_dedup_key(coeffs)
            if ckey in seen_coeff_keys:
                n_deduped += 1
                continue
            seen_coeff_keys.add(ckey)

            n_poly += 1

            # Compute discriminant
            disc = compute_discriminant(coeffs)

            # Classify Galois group
            galois_info = classify_galois_group(coeffs, disc)
            if galois_info is None:
                continue

            n_classified += 1
            group_counter[galois_info["galois_group"]] += 1

            rec = {
                "hash": h,
                "degree": degree,
                "coefficients": coeffs,
                "discriminant": float(disc) if disc is not None else None,
                **galois_info,
            }
            out_f.write(json.dumps(rec, default=_json_default,
                                   separators=(",", ":")) + "\n")

    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"  Galois Group Signatures Complete")
    print(f"  {'=' * 38}")
    print(f"  Total trees:         {len(trees):>10,}")
    print(f"  Polynomial:          {n_poly:>10,}")
    print(f"  Coeff-deduped:       {n_deduped:>10,}")
    print(f"  Skipped (deg>{MAX_DEGREE}):   {n_skipped_degree:>10,}")
    print(f"  Classified:          {n_classified:>10,}")
    print(f"  Time:                {elapsed:>9.1f}s")
    print()
    print("  Galois group distribution:")
    for group, cnt in group_counter.most_common(20):
        print(f"    {group:<20} {cnt:>8,}")
    print()
    print(f"  Output: {OUT_SIGS}")
    print("=" * 70)


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="S10: Galois group signatures from polynomial formula trees"
    )
    parser.add_argument("--max-formulas", type=int, default=None,
                        help="Cap on number of formula trees to load")
    parser.add_argument("--sample", type=int, default=None,
                        help="Random sample size (after loading)")
    args = parser.parse_args()
    run(max_formulas=args.max_formulas, sample_n=args.sample)


if __name__ == "__main__":
    main()
