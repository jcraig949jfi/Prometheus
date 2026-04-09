"""
Discriminant Signatures — algebraic invariants from polynomial formula trees.
=============================================================================
Strategy S13: for polynomial-like formulas, compute discriminant (root collision
invariant) and resultant-derived signatures. Cross-reference against known
discriminants from LMFDB (genus-2 curves, number fields) to find structural
bridges between formula space and algebraic geometry.

Usage:
    python discriminant_signatures.py                        # full run
    python discriminant_signatures.py --max-formulas 50000   # cap input
    python discriminant_signatures.py --sample 10000         # random sample
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
GENUS2_FILE = ROOT / "cartography" / "genus2" / "data" / "genus2_curves_full.json"
NF_FILE = ROOT / "cartography" / "number_fields" / "data" / "number_fields.json"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_SIGS = OUT_DIR / "discriminant_signatures.jsonl"
OUT_MATCHES = OUT_DIR / "discriminant_matches.jsonl"


# ── Coefficient extraction from formula trees ────────────────────────────

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


def _is_polynomial_tree(node):
    """Heuristic: tree is polynomial-like if it uses only add/sub/multiply/power
    with integer exponents and a single variable."""
    allowed_ops = {"add", "sub", "multiply", "neg", "power", "eq", "paren"}
    variables = _collect_variables(node)
    if len(variables) != 1:
        return False, None
    var = variables.pop()
    if not _ops_allowed(node, allowed_ops):
        return False, None
    return True, var


def _ops_allowed(node, allowed):
    """Check all operator ops are in the allowed set."""
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


def _eval_tree(node, var_name, var_val):
    """Evaluate a formula tree numerically with var_name=var_val.
    Returns float or None on failure."""
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
        return None  # unknown variable

    children = node.get("children", [])
    op = node.get("op", "")

    if op == "eq":
        # For an equation, try the RHS (second child) as the polynomial expression
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
    """Extract polynomial coefficients [a_0, a_1, ..., a_d] by evaluating
    at enough points and solving the Vandermonde system."""
    # Try evaluating at integer points to determine degree
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

    # Determine degree by successive finite differences
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

    # Fit polynomial of determined degree
    x = np.array(test_points[:degree + 2], dtype=np.float64)
    y = vals[:degree + 2]
    try:
        coeffs = np.polyfit(x, y, degree)
        # polyfit returns highest-degree first; reverse for [a_0, ..., a_d]
        coeffs = coeffs[::-1].tolist()
        # Snap near-integers (most mathematical polynomials have integer coeffs)
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


# ── Discriminant computation ──────────────────────────────────────────────

def sylvester_matrix(p, q):
    """Build Sylvester matrix for polynomials p, q (coefficients [a_0,...,a_d],
    i.e. lowest degree first). Returns numpy array."""
    # Convert to highest-degree-first for consistency with standard Sylvester
    p_hi = list(reversed(p))
    q_hi = list(reversed(q))
    m = len(q_hi) - 1  # degree of q
    n = len(p_hi) - 1  # degree of p
    size = m + n
    if size == 0:
        return np.array([[1.0]])
    S = np.zeros((size, size))
    # m rows from p
    for i in range(m):
        for j, c in enumerate(p_hi):
            S[i, i + j] = c
    # n rows from q
    for i in range(n):
        for j, c in enumerate(q_hi):
            S[m + i, i + j] = c
    return S


def poly_derivative(coeffs):
    """Derivative of polynomial with coefficients [a_0, a_1, ..., a_d].
    Returns [a_1, 2*a_2, ..., d*a_d]."""
    if len(coeffs) <= 1:
        return [0.0]
    return [coeffs[i] * i for i in range(1, len(coeffs))]


def compute_discriminant(coeffs):
    """Compute the discriminant of a polynomial given coefficients [a_0,...,a_d].
    Returns (discriminant_value, method_used) or (None, 'failed')."""
    d = len(coeffs) - 1  # degree
    if d < 2:
        return (None, "degree<2")

    a_d = coeffs[d]  # leading coefficient
    if abs(a_d) < 1e-15:
        return (None, "zero_leading")

    # Degree 2: b^2 - 4ac  (coeffs = [c, b, a])
    if d == 2:
        a, b, c = coeffs[2], coeffs[1], coeffs[0]
        disc = b * b - 4 * a * c
        return (disc, "quadratic")

    # Degree 3: 18abcd - 4b^3d + b^2c^2 - 4ac^3 - 27a^2d^2
    # With coeffs [d_val, c_val, b_val, a_val] (our convention: index=degree)
    if d == 3:
        a = coeffs[3]
        b = coeffs[2]
        c = coeffs[1]
        dd = coeffs[0]
        disc = (18 * a * b * c * dd
                - 4 * b**3 * dd
                + b**2 * c**2
                - 4 * a * c**3
                - 27 * a**2 * dd**2)
        return (disc, "cubic")

    # General: Sylvester matrix of f and f'
    # disc = (-1)^(d(d-1)/2) * Res(f, f') / a_d
    f_prime = poly_derivative(coeffs)
    S = sylvester_matrix(coeffs, f_prime)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res = np.linalg.det(S)
    except np.linalg.LinAlgError:
        return (None, "det_failed")

    sign_exp = (d * (d - 1)) // 2
    sign = (-1) ** sign_exp
    disc = sign * res / a_d
    return (disc, f"sylvester_d{d}")


# ── Invariant signature ──────────────────────────────────────────────────

def sign_changes(coeffs):
    """Count sign changes in non-zero coefficients (Descartes bound)."""
    nonzero = [c for c in coeffs if abs(c) > 1e-15]
    changes = 0
    for i in range(1, len(nonzero)):
        if nonzero[i] * nonzero[i - 1] < 0:
            changes += 1
    return changes


def coeff_hash(coeffs):
    """Hash of sorted normalized absolute coefficients."""
    if not coeffs:
        return "empty"
    mx = max(abs(c) for c in coeffs) or 1.0
    normed = sorted(abs(c) / mx for c in coeffs)
    # Quantize to 4 decimal places
    key = ",".join(f"{v:.4f}" for v in normed)
    return hashlib.md5(key.encode()).hexdigest()[:12]


def compute_signature(coeffs, disc_val):
    """Build the full signature vector."""
    d = len(coeffs) - 1
    f_at_1 = sum(coeffs)
    f_at_neg1 = sum(c * ((-1) ** i) for i, c in enumerate(coeffs))
    n_sign = sign_changes(coeffs)
    c_hash = coeff_hash(coeffs)

    disc_sign = 0
    log_abs_disc = None
    if disc_val is not None:
        disc_sign = 1 if disc_val > 0 else (-1 if disc_val < 0 else 0)
        abs_disc = abs(disc_val)
        log_abs_disc = math.log10(abs_disc) if abs_disc > 1e-300 else -300.0

    return {
        "degree": d,
        "discriminant": float(disc_val) if disc_val is not None else None,
        "disc_sign": disc_sign,
        "log_abs_disc": round(log_abs_disc, 6) if log_abs_disc is not None else None,
        "n_sign_changes": n_sign,
        "f_at_1": round(f_at_1, 10),
        "f_at_neg1": round(f_at_neg1, 10),
        "leading_coeff": coeffs[-1],
        "constant_term": coeffs[0],
        "coeff_hash": c_hash,
    }


# ── Known discriminant loader ────────────────────────────────────────────

def load_known_discriminants():
    """Load discriminants from genus-2 curves and number fields."""
    known = {}  # abs_disc -> list of (source, label)

    # Genus-2 curves
    if GENUS2_FILE.exists():
        print(f"  Loading genus-2 discriminants from {GENUS2_FILE.name} ...")
        try:
            with open(GENUS2_FILE) as f:
                data = json.load(f)
            curves = data if isinstance(data, list) else data.get("curves", [])
            for c in curves:
                d = c.get("discriminant")
                if d is not None:
                    d_abs = abs(int(d))
                    known.setdefault(d_abs, []).append(("genus2", c.get("label", "?")))
            print(f"    {len(known)} unique |disc| values from genus-2")
        except Exception as e:
            print(f"    WARNING: genus-2 load failed: {e}")

    # Number fields
    n_nf = 0
    if NF_FILE.exists():
        print(f"  Loading number field discriminants from {NF_FILE.name} ...")
        try:
            with open(NF_FILE) as f:
                data = json.load(f)
            for nf in data:
                d_abs = nf.get("disc_abs")
                if d_abs is not None:
                    try:
                        d_abs = abs(int(d_abs))
                    except (ValueError, TypeError):
                        continue
                    known.setdefault(d_abs, []).append(("nf", nf.get("label", "?")))
                    n_nf += 1
            print(f"    {n_nf} number field entries loaded")
        except Exception as e:
            print(f"    WARNING: number field load failed: {e}")

    print(f"  Known discriminants: {len(known)} unique |disc| values total")
    return known


# ── Main pipeline ─────────────────────────────────────────────────────────

def run(max_formulas=None, sample_n=None):
    t0 = time.time()
    print("=" * 70)
    print("Discriminant Signatures (S13)")
    print("=" * 70)

    # Load known discriminants for cross-referencing
    known_disc = load_known_discriminants()

    # Load formula trees
    print(f"\n  Loading formula trees from {TREES_FILE.name} ...")
    if not TREES_FILE.exists():
        print(f"  ERROR: {TREES_FILE} not found")
        return

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

    # Process
    n_poly = 0
    n_disc = 0
    n_matched = 0
    sigs = []
    matches = []
    disc_counter = Counter()

    for i, tree in enumerate(trees):
        if (i + 1) % 50000 == 0:
            print(f"  ... {i+1:,}/{len(trees):,} processed, {n_poly} polynomials, {n_disc} discriminants")

        h = tree.get("hash", "")
        root = tree.get("root", {})

        is_poly, var = _is_polynomial_tree(root)
        if not is_poly:
            continue

        coeffs = extract_coefficients(root, var)
        if coeffs is None or len(coeffs) < 3:
            continue

        n_poly += 1
        disc_val, method = compute_discriminant(coeffs)
        sig = compute_signature(coeffs, disc_val)
        sig["hash"] = h
        sig["method"] = method
        sig["coefficients"] = coeffs
        sigs.append(sig)

        if disc_val is not None:
            n_disc += 1
            disc_counter[method] += 1

            # Cross-reference with known discriminants
            abs_disc_int = None
            try:
                abs_disc_int = abs(int(round(disc_val)))
            except (OverflowError, ValueError):
                pass

            if abs_disc_int is not None and abs_disc_int in known_disc:
                n_matched += 1
                for source, label in known_disc[abs_disc_int]:
                    matches.append({
                        "formula_hash": h,
                        "discriminant": float(disc_val),
                        "abs_disc": abs_disc_int,
                        "match_source": source,
                        "match_label": label,
                        "degree": sig["degree"],
                        "coefficients": coeffs,
                    })

    # Write outputs
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUT_SIGS, "w") as f:
        for s in sigs:
            f.write(json.dumps(s, default=_json_default) + "\n")
    print(f"\n  Wrote {len(sigs):,} signatures to {OUT_SIGS.name}")

    with open(OUT_MATCHES, "w") as f:
        for m in matches:
            f.write(json.dumps(m, default=_json_default) + "\n")
    print(f"  Wrote {len(matches):,} matches to {OUT_MATCHES.name}")

    # Summary
    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"  Total trees:       {len(trees):,}")
    print(f"  Polynomial:        {n_poly:,}")
    print(f"  With discriminant: {n_disc:,}")
    print(f"  Cross-matches:     {n_matched:,}")
    print(f"  Methods:           {dict(disc_counter)}")
    print(f"  Time:              {elapsed:.1f}s")
    print("=" * 70)


def _json_default(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return str(obj)


# ── CLI ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="S13: Discriminant & resultant signatures from polynomial formula trees"
    )
    parser.add_argument("--max-formulas", type=int, default=None,
                        help="Cap on number of formula trees to load")
    parser.add_argument("--sample", type=int, default=None,
                        help="Random sample size (after loading)")
    args = parser.parse_args()
    run(max_formulas=args.max_formulas, sample_n=args.sample)


if __name__ == "__main__":
    main()
