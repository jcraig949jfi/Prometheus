"""
p-adic Signature Extractor (S7) — p-adic valuations and Newton polygons.
=========================================================================
For polynomial formula trees: compute p-adic valuations of coefficients,
build Newton polygons (lower convex hull of (i, v_p(a_i))), extract
segment counts and slopes.

For OEIS sequences with integer terms: compute v_p(a(n)) profiles and
extract (mean_valuation, max_valuation, valuation_entropy) per prime.

Usage:
    python padic_signatures.py                          # full run
    python padic_signatures.py --max-formulas 50000     # cap input
    python padic_signatures.py --sample 10000           # random sample
"""

import argparse
import gzip
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
OEIS_DATA = ROOT / "cartography" / "oeis" / "data"
STRIPPED_GZ = OEIS_DATA / "stripped_full.gz"
STRIPPED_FALLBACK = OEIS_DATA / "stripped.gz"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_SIGS = OUT_DIR / "padic_signatures.jsonl"

PRIMES = [2, 3, 5, 7, 11]


# ── Coefficient extraction (shared with discriminant_signatures.py) ────

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


def _eval_tree(node, var_name, var_val):
    """Evaluate a formula tree numerically with var_name=var_val."""
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
    """Extract polynomial coefficients [a_0, a_1, ..., a_d] by evaluating
    at enough points and solving the Vandermonde system."""
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


# ── p-adic valuation ────────────────────────────────────────────────────

def padic_valuation(n, p):
    """Compute v_p(n) = max power of p dividing n. Returns 0 for n=0."""
    if n == 0:
        return float("inf")
    n = abs(int(n))
    if n == 0:
        return float("inf")
    v = 0
    while n > 0 and n % p == 0:
        v += 1
        n //= p
    return v


# ── Newton polygon (lower convex hull) ─────────────────────────────────

def newton_polygon(coeffs, p):
    """Build Newton polygon for polynomial with coefficients [a_0,...,a_d] w.r.t. prime p.

    Returns (segments, slopes) where segments = list of ((i1,v1),(i2,v2))
    and slopes = list of floats.
    """
    # Build points (i, v_p(a_i)) for nonzero coefficients
    points = []
    for i, c in enumerate(coeffs):
        if c != 0:
            v = padic_valuation(c, p)
            if v == float("inf"):
                continue
            points.append((i, v))

    if len(points) < 2:
        return [], []

    # Lower convex hull using Andrew's monotone chain (lower half)
    points.sort()
    lower = []
    for pt in points:
        while len(lower) >= 2:
            # Cross product to check left turn
            o, a, b = lower[-2], lower[-1], pt
            cross = (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
            if cross <= 0:
                lower.pop()
            else:
                break
        lower.append(pt)

    # Extract segments and slopes
    segments = []
    slopes = []
    for i in range(len(lower) - 1):
        p1, p2 = lower[i], lower[i + 1]
        segments.append((p1, p2))
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        slope = dy / dx if dx != 0 else float("inf")
        slopes.append(slope)

    return segments, slopes


# ── OEIS loader ─────────────────────────────────────────────────────────

def load_oeis_sequences(min_length=16, max_seqs=None):
    """Parse OEIS stripped format, keep sequences with >= min_length integer terms."""
    gz = STRIPPED_GZ if STRIPPED_GZ.exists() else STRIPPED_FALLBACK
    if not gz.exists():
        print(f"  WARNING: no OEIS stripped file at {STRIPPED_GZ} or {STRIPPED_FALLBACK}")
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


# ── Valuation entropy ──────────────────────────────────────────────────

def valuation_entropy(vals):
    """Shannon entropy of a sequence of valuation values."""
    if not vals:
        return 0.0
    counts = Counter(vals)
    total = len(vals)
    ent = 0.0
    for c in counts.values():
        p = c / total
        if p > 0:
            ent -= p * math.log2(p)
    return ent


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
    if obj == float("inf"):
        return "inf"
    return str(obj)


# ── Main pipeline ──────────────────────────────────────────────────────

def run(max_formulas=None, sample_n=None):
    t0 = time.time()
    print("=" * 70)
    print("p-adic Signatures (S7)")
    print("=" * 70)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    n_poly = 0
    n_sigs = 0
    n_oeis = 0
    n_deduped = 0
    seen_coeff_keys = set()

    with open(OUT_SIGS, "w", encoding="utf-8") as out_f:

        # ── Part 1: Polynomial formula trees ────────────────────────
        print(f"\n  [Part 1] Loading formula trees from {TREES_FILE.name} ...")
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

            for i, tree in enumerate(trees):
                if (i + 1) % 50000 == 0:
                    print(f"  ... {i+1:,}/{len(trees):,} processed, "
                          f"{n_poly} polynomials, {n_sigs} signatures")

                h = tree.get("hash", "")
                root = tree.get("root", {})

                is_poly, var = _is_polynomial_tree(root)
                if not is_poly:
                    continue

                coeffs = extract_coefficients(root, var)
                if coeffs is None or len(coeffs) < 2:
                    continue

                # Dedup
                ckey = _coeff_dedup_key(coeffs)
                if ckey in seen_coeff_keys:
                    n_deduped += 1
                    continue
                seen_coeff_keys.add(ckey)

                n_poly += 1

                # Compute p-adic signatures for each prime
                padic_sigs = {}
                for p in PRIMES:
                    segs, slopes = newton_polygon(coeffs, p)
                    valuations = []
                    for c in coeffs:
                        if c != 0:
                            valuations.append(padic_valuation(c, p))

                    finite_vals = [v for v in valuations if v != float("inf")]
                    padic_sigs[str(p)] = {
                        "n_segments": len(segs),
                        "slopes": [round(s, 6) if s != float("inf") else "inf"
                                   for s in slopes],
                        "min_valuation": min(finite_vals) if finite_vals else None,
                        "max_valuation": max(finite_vals) if finite_vals else None,
                        "total_width": (segs[-1][1][0] - segs[0][0][0])
                                       if segs else 0,
                    }

                rec = {
                    "source": "formula",
                    "id": h,
                    "degree": len(coeffs) - 1,
                    "coefficients": coeffs,
                    "padic": padic_sigs,
                }
                out_f.write(json.dumps(rec, default=_json_default,
                                       separators=(",", ":")) + "\n")
                n_sigs += 1
        else:
            print(f"  WARNING: {TREES_FILE} not found, skipping formula trees")

        # ── Part 2: OEIS sequences ──────────────────────────────────
        print(f"\n  [Part 2] Loading OEIS sequences ...")
        oeis_seqs = load_oeis_sequences(min_length=16,
                                        max_seqs=max_formulas or 50000)

        oeis_items = list(oeis_seqs.items())
        if sample_n and sample_n < len(oeis_items):
            random.seed(42)
            oeis_items = random.sample(oeis_items, sample_n)
            print(f"  Sampled {len(oeis_items):,} OEIS sequences")

        for idx, (sid, terms) in enumerate(oeis_items):
            if (idx + 1) % 10000 == 0:
                print(f"  ... {idx+1:,}/{len(oeis_items):,} OEIS sequences processed")

            # Only use nonzero integer terms
            int_terms = [t for t in terms[:200] if isinstance(t, int)]
            if len(int_terms) < 8:
                continue

            padic_sigs = {}
            for p in PRIMES:
                vals = []
                for t in int_terms:
                    if t == 0:
                        vals.append(0)  # convention: v_p(0) = 0 for profile
                    else:
                        vals.append(padic_valuation(t, p))

                finite_vals = [v for v in vals if v != float("inf")]
                if not finite_vals:
                    padic_sigs[str(p)] = {
                        "mean_valuation": None,
                        "max_valuation": None,
                        "valuation_entropy": 0.0,
                    }
                    continue

                padic_sigs[str(p)] = {
                    "mean_valuation": round(sum(finite_vals) / len(finite_vals), 6),
                    "max_valuation": max(finite_vals),
                    "valuation_entropy": round(valuation_entropy(finite_vals), 6),
                }

            rec = {
                "source": "oeis",
                "id": sid,
                "n_terms": len(int_terms),
                "padic": padic_sigs,
            }
            out_f.write(json.dumps(rec, default=_json_default,
                                   separators=(",", ":")) + "\n")
            n_oeis += 1

    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"  p-adic Signatures Complete")
    print(f"  {'=' * 38}")
    print(f"  Formula polynomials: {n_poly:>10,}")
    print(f"  Coeff-deduped:       {n_deduped:>10,}")
    print(f"  Formula signatures:  {n_sigs:>10,}")
    print(f"  OEIS signatures:     {n_oeis:>10,}")
    print(f"  Total written:       {n_sigs + n_oeis:>10,}")
    print(f"  Time:                {elapsed:>9.1f}s")
    print(f"  Output: {OUT_SIGS}")
    print("=" * 70)


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="S7: p-adic valuation signatures and Newton polygons"
    )
    parser.add_argument("--max-formulas", type=int, default=None,
                        help="Cap on number of formula trees / OEIS seqs to load")
    parser.add_argument("--sample", type=int, default=None,
                        help="Random sample size (after loading)")
    args = parser.parse_args()
    run(max_formulas=args.max_formulas, sample_n=args.sample)


if __name__ == "__main__":
    main()
