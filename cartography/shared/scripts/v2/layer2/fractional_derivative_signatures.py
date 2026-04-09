"""
Fractional Derivative Signatures — Riemann-Liouville invariants from polynomial formulas.
===========================================================================================
Strategy S2: compute fractional derivatives D^alpha(f) using closed-form for monomials,
and fractional differences (Grunwald-Letnikov) for OEIS sequences.

For polynomial f(x) = sum(a_i * x^i):
    D^alpha(x^n) = Gamma(n+1)/Gamma(n+1-alpha) * x^(n-alpha)

For OEIS sequences: Grunwald-Letnikov fractional difference at alpha=0.5.

Usage:
    python fractional_derivative_signatures.py
    python fractional_derivative_signatures.py --max-formulas 50000
    python fractional_derivative_signatures.py --sample 10000
"""

import argparse
import gzip
import json
import random
import sys
import time
import warnings
import numpy as np
from math import gamma, pi, e, isfinite, lgamma, exp, log
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
TREES_FILE = ROOT / "cartography" / "convergence" / "data" / "formula_trees.jsonl"
OEIS_DATA = ROOT / "cartography" / "oeis" / "data"
STRIPPED_GZ = OEIS_DATA / "stripped_full.gz"
STRIPPED_FALLBACK = OEIS_DATA / "stripped.gz"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_SIGS = OUT_DIR / "fractional_derivative_signatures.jsonl"


# ── Coefficient extraction (shared with other extractors) ─────────────────

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
        if v is None or not isfinite(v):
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


# ── Fractional derivative (Riemann-Liouville for monomials) ───────────────

def _safe_gamma_ratio(n_plus_1, alpha):
    """Compute Gamma(n+1)/Gamma(n+1-alpha) safely using log-gamma."""
    a = n_plus_1
    b = n_plus_1 - alpha
    if b <= 0 and b == int(b):
        return None  # pole of gamma
    try:
        log_ratio = lgamma(a) - lgamma(b)
        if abs(log_ratio) > 700:
            return None
        return exp(log_ratio)
    except (ValueError, OverflowError):
        return None


def fractional_derivative_poly(coeffs, alpha, x):
    """Evaluate D^alpha(f)(x) for polynomial f with given coefficients.

    Uses: D^alpha(x^n) = Gamma(n+1)/Gamma(n+1-alpha) * x^(n-alpha)
    coeffs = [a_0, a_1, ..., a_d] (lowest degree first)
    """
    result = 0.0
    for n, a_n in enumerate(coeffs):
        if abs(a_n) < 1e-15:
            continue
        ratio = _safe_gamma_ratio(n + 1, alpha)
        if ratio is None:
            return None
        # x^(n-alpha): need x > 0 for non-integer exponent
        exponent = n - alpha
        if x <= 0 and exponent != int(exponent):
            return None
        try:
            term = a_n * ratio * (x ** exponent)
            if not isfinite(term):
                return None
            result += term
        except (OverflowError, ValueError, ZeroDivisionError):
            return None
    if not isfinite(result):
        return None
    return result


ALPHAS = [0.5, 1.5, 2 ** 0.5]
EVAL_POINTS = [1.0, e, pi]


def compute_frac_deriv_signature(coeffs):
    """Compute 9-value fractional derivative signature for a polynomial.
    3 alphas x 3 evaluation points.
    """
    sig = []
    for alpha in ALPHAS:
        for x in EVAL_POINTS:
            val = fractional_derivative_poly(coeffs, alpha, x)
            if val is None:
                return None
            sig.append(val)
    return sig


# ── Grunwald-Letnikov fractional difference for sequences ─────────────────

def grunwald_letnikov(seq, alpha=0.5, max_terms=20):
    """Compute fractional difference D^alpha[a](n) for first max_terms terms.

    D^alpha[a](n) = sum_{k=0}^{n} (-1)^k * C(alpha,k) * a(n-k)
    where C(alpha,k) = alpha*(alpha-1)*...*(alpha-k+1) / k!
    """
    n_out = min(max_terms, len(seq))
    result = []
    for n in range(n_out):
        total = 0.0
        binom_coeff = 1.0  # C(alpha, 0) = 1
        for k in range(n + 1):
            if k > 0:
                binom_coeff *= (alpha - k + 1) / k
            sign = (-1) ** k
            idx = n - k
            if idx < 0 or idx >= len(seq):
                break
            total += sign * binom_coeff * seq[idx]
        result.append(total)
    return result


# ── OEIS loader ───────────────────────────────────────────────────────────

def load_oeis_sequences(min_length=20, max_seqs=None):
    gz = STRIPPED_GZ if STRIPPED_GZ.exists() else STRIPPED_FALLBACK
    if not gz.exists():
        print(f"  ERROR: no stripped file at {STRIPPED_GZ} or {STRIPPED_FALLBACK}")
        return {}
    print(f"  Loading OEIS sequences from {gz.name} (min_length={min_length}) ...")
    seqs = {}
    with gzip.open(gz, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(" ", 1)
            if len(parts) < 2:
                continue
            sid = parts[0].strip()
            if not sid.startswith("A"):
                continue
            terms_str = parts[1].strip().strip(",")
            try:
                terms = [int(t) for t in terms_str.split(",") if t.strip()]
            except ValueError:
                continue
            if len(terms) >= min_length:
                seqs[sid] = terms
            if max_seqs and len(seqs) >= max_seqs:
                break
    print(f"  Loaded {len(seqs):,} sequences with >= {min_length} terms")
    return seqs


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
    print("Fractional Derivative Signatures (S2)")
    print("=" * 70)

    results = []

    # ── Part 1: Polynomial formulas ──
    print(f"\n  Loading formula trees from {TREES_FILE.name} ...")
    if TREES_FILE.exists():
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
            if coeffs is None or len(coeffs) < 2:
                continue

            ckey = tuple(round(c, 6) for c in coeffs)
            if ckey in seen:
                continue
            seen.add(ckey)

            n_poly += 1
            sig_vec = compute_frac_deriv_signature(coeffs)
            if sig_vec is None:
                continue
            n_sig += 1

            results.append({
                "id": h,
                "source": "formula",
                "type": "polynomial",
                "degree": len(coeffs) - 1,
                "coefficients": coeffs,
                "alphas": ALPHAS,
                "eval_points": EVAL_POINTS,
                "signature_vector": sig_vec,
            })

        print(f"  Formulas: {n_poly:,} polynomial, {n_sig:,} with signatures")
    else:
        print(f"  WARNING: {TREES_FILE} not found, skipping formula trees")

    # ── Part 2: OEIS sequences (Grunwald-Letnikov) ──
    print(f"\n  Processing OEIS sequences ...")
    seqs = load_oeis_sequences(min_length=20, max_seqs=max_formulas or 50000)
    n_oeis = 0
    for sid, terms in seqs.items():
        frac_diff = grunwald_letnikov(terms, alpha=0.5, max_terms=20)
        if not frac_diff or all(abs(v) < 1e-15 for v in frac_diff):
            continue
        # Check for non-finite values
        if any(not isfinite(v) for v in frac_diff):
            continue
        n_oeis += 1
        results.append({
            "id": sid,
            "source": "oeis",
            "type": "grunwald_letnikov",
            "alpha": 0.5,
            "n_terms": len(terms),
            "signature_vector": frac_diff,
        })
        if (n_oeis % 50000 == 0):
            print(f"    {n_oeis:,} OEIS signatures computed ...")

    print(f"  OEIS: {n_oeis:,} fractional difference signatures")

    # ── Write output ──
    write_jsonl(OUT_SIGS, results)

    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"  Total signatures: {len(results):,}")
    print(f"  Time: {elapsed:.1f}s")
    print(f"{'=' * 70}")


def main():
    parser = argparse.ArgumentParser(
        description="S2: Fractional derivative signatures from polynomial formulas and OEIS"
    )
    parser.add_argument("--max-formulas", type=int, default=None,
                        help="Cap on number of formulas/sequences to load")
    parser.add_argument("--sample", type=int, default=None,
                        help="Random sample size (after loading)")
    args = parser.parse_args()
    run(max_formulas=args.max_formulas, sample_n=args.sample)


if __name__ == "__main__":
    main()
