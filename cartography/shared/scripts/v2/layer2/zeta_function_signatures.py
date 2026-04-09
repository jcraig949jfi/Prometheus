"""
Zeta Function Signatures — local factor approximation from polynomial formulas.
================================================================================
Strategy S12: for polynomial formulas over finite fields, count solutions mod p.

For each prime p in [2,3,5,7,11,13,17,19,23], count N_p = number of x in
{0,...,p-1} where f(x) = 0 (mod p). The sequence (N_2,...,N_23) approximates
local factors of the Hasse-Weil zeta function.

Cross-reference: LMFDB elliptic curves have a_p = p - N_p. If a formula's
N_p sequence matches an EC's a_p, that's a structural bridge.

Usage:
    python zeta_function_signatures.py
    python zeta_function_signatures.py --max-formulas 50000
    python zeta_function_signatures.py --sample 10000
"""

import argparse
import json
import random
import sys
import time
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
TREES_FILE = ROOT / "cartography" / "convergence" / "data" / "formula_trees.jsonl"
EC_FILE = ROOT / "cartography" / "convergence" / "data" / "elliptic_curves.json"
EC_FILE_ALT = ROOT / "cartography" / "lmfdb" / "data" / "elliptic_curves.json"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_SIGS = OUT_DIR / "zeta_function_signatures.jsonl"

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23]


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


# ── Solution counting mod p ──────────────────────────────────────────────

def eval_poly_mod_p(coeffs, x, p):
    """Evaluate polynomial with integer coefficients at x mod p.
    coeffs = [a_0, a_1, ..., a_d] (lowest degree first).
    """
    result = 0
    x_pow = 1
    for c in coeffs:
        c_int = int(round(c))
        result = (result + c_int * x_pow) % p
        x_pow = (x_pow * x) % p
    return result


def count_solutions_mod_p(coeffs, p):
    """Count N_p = number of x in {0,...,p-1} where f(x) = 0 (mod p)."""
    count = 0
    for x in range(p):
        if eval_poly_mod_p(coeffs, x, p) == 0:
            count += 1
    return count


def compute_zeta_signature(coeffs):
    """Compute the N_p vector and normalized N_p/p for all primes."""
    # Check coefficients are near-integer (needed for mod arithmetic)
    for c in coeffs:
        if abs(c - round(c)) > 0.01:
            return None

    n_p = []
    n_p_normalized = []
    for p in PRIMES:
        np_val = count_solutions_mod_p(coeffs, p)
        n_p.append(np_val)
        n_p_normalized.append(np_val / p)

    # Compute a_p = p - N_p (for EC cross-reference)
    a_p = [p - n for p, n in zip(PRIMES, n_p)]

    return {
        "n_p": n_p,
        "n_p_normalized": n_p_normalized,
        "a_p": a_p,
    }


# ── Load known elliptic curves for cross-referencing ──────────────────────

def load_ec_ap():
    """Load elliptic curve a_p data if available. Returns dict of label -> a_p list."""
    for path in [EC_FILE, EC_FILE_ALT]:
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                ec_map = {}
                if isinstance(data, list):
                    for entry in data:
                        label = entry.get("label", entry.get("lmfdb_label", ""))
                        ap = entry.get("a_p", entry.get("ap", []))
                        if label and ap:
                            ec_map[label] = ap
                elif isinstance(data, dict):
                    for label, entry in data.items():
                        ap = entry.get("a_p", entry.get("ap", []))
                        if ap:
                            ec_map[label] = ap
                print(f"  Loaded {len(ec_map):,} elliptic curves from {path.name}")
                return ec_map
            except Exception as e:
                print(f"  WARNING: failed to load {path}: {e}")
    return {}


def match_ec(a_p_formula, ec_map, primes=None):
    """Check if formula's a_p matches any EC's a_p (first len(primes) values)."""
    if primes is None:
        primes = PRIMES
    matches = []
    n = min(len(a_p_formula), len(primes))
    for label, ec_ap in ec_map.items():
        if len(ec_ap) < n:
            continue
        # EC a_p is typically indexed by prime position, match first n
        if ec_ap[:n] == a_p_formula[:n]:
            matches.append(label)
    return matches


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
    print("Zeta Function Signatures (S12)")
    print("=" * 70)

    # Load EC data for cross-referencing
    ec_map = load_ec_ap()

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
    n_ec_match = 0
    seen = set()

    for i, tree in enumerate(trees):
        if (i + 1) % 50000 == 0:
            elapsed = time.time() - t0
            print(f"  ... {i+1:,}/{len(trees):,} processed, "
                  f"{n_poly} poly, {n_sig} sigs, {n_ec_match} EC matches  ({elapsed:.1f}s)")

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
        zeta_sig = compute_zeta_signature(coeffs)
        if zeta_sig is None:
            continue

        n_sig += 1
        rec = {
            "id": h,
            "source": "formula",
            "degree": len(coeffs) - 1,
            "coefficients": coeffs,
            "primes": PRIMES,
            **zeta_sig,
        }

        # Cross-reference with EC
        if ec_map:
            ec_matches = match_ec(zeta_sig["a_p"], ec_map)
            if ec_matches:
                n_ec_match += 1
                rec["ec_matches"] = ec_matches[:10]

        results.append(rec)

    write_jsonl(OUT_SIGS, results)

    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"  Total trees:   {len(trees):,}")
    print(f"  Polynomial:    {n_poly:,}")
    print(f"  Signatures:    {n_sig:,}")
    print(f"  EC matches:    {n_ec_match:,}")
    print(f"  Time: {elapsed:.1f}s")
    print(f"{'=' * 70}")


def main():
    parser = argparse.ArgumentParser(
        description="S12: Zeta function signatures — solution counting mod p"
    )
    parser.add_argument("--max-formulas", type=int, default=None,
                        help="Cap on number of formula trees to load")
    parser.add_argument("--sample", type=int, default=None,
                        help="Random sample size (after loading)")
    args = parser.parse_args()
    run(max_formulas=args.max_formulas, sample_n=args.sample)


if __name__ == "__main__":
    main()
