"""
Spectral Curve Signatures — eigenvalue distribution from polynomial companion matrices.
========================================================================================
Strategy S26: for each polynomial formula, build the companion matrix, compute
eigenvalues (= roots), and extract a spectral signature from the root distribution
in the complex plane.

Signature: n_real_roots, n_complex_roots, max_root_modulus, min_root_modulus,
spectral_radius, root_spread, root_centroid (real, imag).

Usage:
    python spectral_curve_signatures.py
    python spectral_curve_signatures.py --max-formulas 50000
    python spectral_curve_signatures.py --sample 10000
"""

import argparse
import json
import random
import sys
import time
import warnings
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
TREES_FILE = ROOT / "cartography" / "convergence" / "data" / "formula_trees.jsonl"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_SIGS = OUT_DIR / "spectral_curve_signatures.jsonl"


# ── Coefficient extraction (shared) ──────────────────────────────────────

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
        exp_v = _eval_tree(children[1], var_name, var_val)
        if base is None or exp_v is None:
            return None
        try:
            return base ** exp_v
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


# ── Companion matrix and spectral signature ───────────────────────────────

def build_companion_matrix(coeffs):
    """Build companion matrix for polynomial with coefficients [a_0, ..., a_d].
    The polynomial is a_0 + a_1*x + ... + a_d*x^d.
    Companion matrix eigenvalues = roots of the polynomial.
    """
    d = len(coeffs) - 1
    if d < 1:
        return None
    leading = coeffs[d]
    if abs(leading) < 1e-15:
        return None

    # numpy companion expects [c_d, c_{d-1}, ..., c_0] (highest first), monic
    # We use np.polynomial.polynomial.polycompanion which takes [a_0,...,a_d]
    try:
        # Normalize to monic: divide by leading coefficient
        monic = [c / leading for c in coeffs]
        # numpy's companion matrix for polynomial coefficients
        # Build manually: standard companion matrix
        C = np.zeros((d, d))
        for i in range(d - 1):
            C[i + 1, i] = 1.0
        for i in range(d):
            C[i, d - 1] = -monic[i]
        return C
    except Exception:
        return None


def compute_spectral_signature(coeffs):
    """Compute spectral signature from polynomial roots via companion matrix."""
    d = len(coeffs) - 1
    if d < 2:
        return None

    C = build_companion_matrix(coeffs)
    if C is None:
        return None

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            eigenvalues = np.linalg.eigvals(C)
    except np.linalg.LinAlgError:
        return None

    if len(eigenvalues) == 0:
        return None

    # Classify roots
    moduli = np.abs(eigenvalues)
    imag_parts = np.abs(eigenvalues.imag)
    real_mask = imag_parts < 1e-10

    n_real = int(np.sum(real_mask))
    n_complex = len(eigenvalues) - n_real
    max_modulus = float(np.max(moduli))
    nonzero_moduli = moduli[moduli > 1e-15]
    min_modulus = float(np.min(nonzero_moduli)) if len(nonzero_moduli) > 0 else 0.0
    spectral_radius = max_modulus
    root_spread = max_modulus - min_modulus

    # Centroid in complex plane
    centroid_real = float(np.mean(eigenvalues.real))
    centroid_imag = float(np.mean(eigenvalues.imag))

    # Check for non-finite
    vals = [n_real, n_complex, max_modulus, min_modulus,
            spectral_radius, root_spread, centroid_real, centroid_imag]
    if not all(np.isfinite(v) for v in vals[2:]):
        return None

    return {
        "n_real_roots": n_real,
        "n_complex_roots": n_complex,
        "max_root_modulus": max_modulus,
        "min_root_modulus": min_modulus,
        "spectral_radius": spectral_radius,
        "root_spread": root_spread,
        "root_centroid_real": centroid_real,
        "root_centroid_imag": centroid_imag,
        "signature_vector": [n_real, n_complex, max_modulus, min_modulus,
                             spectral_radius, root_spread,
                             centroid_real, centroid_imag],
    }


# ── JSON encoder ──────────────────────────────────────────────────────────

class _Enc(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def write_jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, cls=_Enc) + "\n")
    print(f"  Wrote {len(records):,} records -> {path}")


# ── Main ──────────────────────────────────────────────────────────────────

def run(max_formulas=None, sample_n=None):
    t0 = time.time()
    print("=" * 70)
    print("Spectral Curve Signatures (S26)")
    print("=" * 70)

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

    results = []
    n_poly = 0
    n_sig = 0
    seen = set()

    for i, tree in enumerate(trees):
        if (i + 1) % 50000 == 0:
            elapsed = time.time() - t0
            print(f"  ... {i+1:,}/{len(trees):,} processed, "
                  f"{n_poly} poly, {n_sig} sigs  ({elapsed:.1f}s)")

        h = tree.get("hash", "")
        root = tree.get("root", {})

        is_poly, var = _is_polynomial_tree(root)
        if not is_poly:
            continue

        coeffs = extract_coefficients(root, var)
        if coeffs is None or len(coeffs) < 3:  # need degree >= 2
            continue

        ckey = tuple(round(c, 6) for c in coeffs)
        if ckey in seen:
            continue
        seen.add(ckey)

        n_poly += 1
        sig = compute_spectral_signature(coeffs)
        if sig is None:
            continue

        n_sig += 1
        results.append({
            "id": h,
            "source": "formula",
            "degree": len(coeffs) - 1,
            "coefficients": coeffs,
            **sig,
        })

    write_jsonl(OUT_SIGS, results)

    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"  Total trees:   {len(trees):,}")
    print(f"  Polynomial:    {n_poly:,}")
    print(f"  Signatures:    {n_sig:,}")
    if results:
        n_real_arr = [r["n_real_roots"] for r in results]
        radii = [r["spectral_radius"] for r in results]
        print(f"  Real roots:    mean={np.mean(n_real_arr):.2f}  "
              f"max={max(n_real_arr)}")
        print(f"  Spectral rad:  mean={np.mean(radii):.3f}  "
              f"median={np.median(radii):.3f}")
    print(f"  Time: {elapsed:.1f}s")
    print(f"{'=' * 70}")


def main():
    parser = argparse.ArgumentParser(
        description="S26: Spectral curve signatures — companion matrix eigenvalues"
    )
    parser.add_argument("--max-formulas", type=int, default=None,
                        help="Cap on number of formula trees to load")
    parser.add_argument("--sample", type=int, default=None,
                        help="Random sample size (after loading)")
    args = parser.parse_args()
    run(max_formulas=args.max_formulas, sample_n=args.sample)


if __name__ == "__main__":
    main()
