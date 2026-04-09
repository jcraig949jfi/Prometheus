"""
Coefficient Field Signature Extractor (S32) — number field classification.
============================================================================
For polynomial formula trees, determines what number field the coefficients
live in: Q (rational), Q(sqrt(N)) (quadratic extension), transcendental
(pi, e), or complex (i).

Usage:
    python coefficient_field_signatures.py                          # full run
    python coefficient_field_signatures.py --max-formulas 100000    # cap
    python coefficient_field_signatures.py --sample 50000           # sample
"""

import argparse
import json
import math
import re
import sys
import time
import random
from collections import Counter
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
TREES_FILE = ROOT / "cartography" / "convergence" / "data" / "formula_trees.jsonl"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_FILE = OUT_DIR / "coefficient_field_signatures.jsonl"

# Known transcendental constants
TRANSCENDENTALS = {"pi", "e", "euler", "gamma", "zeta", "catalan", "apery"}
# Known algebraic irrationals (sqrt patterns)
SQRT_PATTERN = re.compile(r"sqrt\((\d+)\)", re.IGNORECASE)
# Complex unit
COMPLEX_MARKERS = {"i", "j", "imaginary"}


# ---------------------------------------------------------------------------
# Tree walking: extract numeric literals and special constants
# ---------------------------------------------------------------------------

def extract_numerics(node, numerics=None, constants=None, sqrt_args=None):
    """Walk tree, collect all numeric literals, named constants, and sqrt args."""
    if numerics is None:
        numerics = []
    if constants is None:
        constants = set()
    if sqrt_args is None:
        sqrt_args = set()

    if not isinstance(node, dict):
        return numerics, constants, sqrt_args

    ntype = node.get("type", "")
    op = (node.get("op", "") or "").lower().strip()
    value = node.get("value", "")
    name = (node.get("name", "") or "").lower().strip()
    children = node.get("children", [])

    # Number node
    if ntype == "number":
        try:
            val_str = str(value).strip()
            if val_str:
                # Try to parse as numeric
                if "/" in val_str:
                    # Fraction
                    try:
                        frac = Fraction(val_str)
                        numerics.append(("fraction", frac.numerator, frac.denominator))
                    except (ValueError, ZeroDivisionError):
                        numerics.append(("unknown", val_str, None))
                elif "." in val_str:
                    numerics.append(("float", float(val_str), None))
                else:
                    numerics.append(("integer", int(val_str), None))
        except (ValueError, TypeError):
            pass

    # Variable node that might be a constant
    if ntype == "variable" and name:
        if name in TRANSCENDENTALS:
            constants.add(name)
        if name in COMPLEX_MARKERS:
            constants.add("complex")

    # Sqrt operator: extract argument if numeric
    if op in ("sqrt", "\\sqrt"):
        if children:
            child = children[0]
            if isinstance(child, dict) and child.get("type") == "number":
                try:
                    n = int(child.get("value", 0))
                    # Check if it's a perfect square
                    rt = int(math.isqrt(abs(n)))
                    if rt * rt != abs(n) and n > 0:
                        sqrt_args.add(n)
                except (ValueError, TypeError):
                    pass

    # Recurse into children
    for c in children:
        extract_numerics(c, numerics, constants, sqrt_args)

    return numerics, constants, sqrt_args


# ---------------------------------------------------------------------------
# Field classification
# ---------------------------------------------------------------------------

def classify_field(numerics, constants, sqrt_args):
    """Classify the number field from extracted data."""
    has_complex = "complex" in constants or any(
        n in constants for n in ("i", "j"))
    has_transcendental = bool(constants & TRANSCENDENTALS)
    has_sqrt_irrational = bool(sqrt_args)
    has_fraction = any(t == "fraction" for t, _, _ in numerics)
    has_float = any(t == "float" for t, _, _ in numerics)

    # Determine field type (most complex wins)
    if has_complex:
        field_type = "C"
    elif has_transcendental:
        # Identify which transcendentals
        trans = sorted(constants & TRANSCENDENTALS)
        field_type = f"transcendental({','.join(trans)})"
    elif has_sqrt_irrational:
        # Quadratic extension
        if len(sqrt_args) == 1:
            d = list(sqrt_args)[0]
            field_type = f"Q(sqrt({d}))"
        else:
            ds = sorted(sqrt_args)[:3]  # Limit display
            field_type = f"Q(sqrt({','.join(str(d) for d in ds)}))"
    elif has_fraction or has_float:
        field_type = "Q"
    else:
        field_type = "Z"

    # Field discriminant for algebraic extensions
    discriminant = None
    if has_sqrt_irrational and len(sqrt_args) == 1:
        d = list(sqrt_args)[0]
        # Discriminant of Q(sqrt(d)): 4d if d ≡ 2,3 mod 4, else d
        discriminant = d if d % 4 == 1 else 4 * d

    # Max numerator/denominator
    max_num = 0
    max_den = 1
    for t, val, denom in numerics:
        if t == "integer":
            max_num = max(max_num, abs(val))
        elif t == "fraction":
            max_num = max(max_num, abs(val))
            if denom is not None:
                max_den = max(max_den, abs(denom))
        elif t == "float":
            max_num = max(max_num, abs(int(val)))

    return {
        "field_type": field_type,
        "field_discriminant": discriminant,
        "max_numerator": max_num,
        "max_denominator": max_den,
        "n_coefficients": len(numerics),
        "has_transcendental": has_transcendental,
        "has_complex": has_complex,
        "sqrt_extensions": sorted(sqrt_args) if sqrt_args else None,
    }


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run(max_formulas=100000, sample_size=None):
    print("=" * 70)
    print("  Coefficient Field Signature Extractor (S32)")
    print("=" * 70)

    if not TREES_FILE.exists():
        print(f"  ERROR: formula trees not found: {TREES_FILE}")
        return

    t0 = time.time()

    # Reservoir sampling if requested
    if sample_size:
        print(f"  Reservoir sampling {sample_size:,} formulas ...")
        reservoir = []
        scan_count = 0
        with open(TREES_FILE, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if max_formulas and scan_count >= max_formulas:
                    break
                scan_count += 1
                if len(reservoir) < sample_size:
                    reservoir.append(line)
                else:
                    j = random.randint(0, scan_count - 1)
                    if j < sample_size:
                        reservoir[j] = line
                if scan_count % 2_000_000 == 0:
                    print(f"    ... scanned {scan_count:,} lines")
        lines = reservoir
        print(f"  Sampled {len(lines):,} from {scan_count:,} total lines")
    else:
        lines = None

    field_counts = Counter()
    processed = 0
    skipped = 0

    def process_line(line):
        nonlocal processed, skipped
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            skipped += 1
            return None
        root = rec.get("root")
        if not root:
            skipped += 1
            return None
        formula_hash = rec.get("hash", "")
        numerics, constants, sqrt_args = extract_numerics(root)
        field_info = classify_field(numerics, constants, sqrt_args)
        field_info["hash"] = formula_hash
        field_counts[field_info["field_type"]] += 1
        processed += 1
        return field_info

    with open(OUT_FILE, "w", encoding="utf-8") as out:
        if lines is not None:
            for line in lines:
                sig = process_line(line)
                if sig:
                    out.write(json.dumps(sig, separators=(",", ":")) + "\n")
                if processed % 50_000 == 0 and processed > 0:
                    elapsed = time.time() - t0
                    print(f"    {processed:,} processed  ({processed / max(elapsed, 0.01):,.0f}/s)")
        else:
            with open(TREES_FILE, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if max_formulas and processed >= max_formulas:
                        break
                    sig = process_line(line)
                    if sig:
                        out.write(json.dumps(sig, separators=(",", ":")) + "\n")
                    if processed % 500_000 == 0 and processed > 0:
                        elapsed = time.time() - t0
                        print(f"    {processed:,} processed  ({processed / max(elapsed, 0.01):,.0f}/s)")

    elapsed = time.time() - t0

    print()
    print("=" * 70)
    print(f"  Coefficient Field Signatures Complete")
    print(f"  {'=' * 40}")
    print(f"  Formulas processed:    {processed:>12,}")
    print(f"  Skipped (parse err):   {skipped:>12,}")
    print(f"  Distinct field types:  {len(field_counts):>12,}")
    print(f"  Time:                  {elapsed:>11.1f}s")
    if elapsed > 0:
        print(f"  Rate:                  {processed / elapsed:>11,.0f}/s")
    print()
    print("  Field type distribution:")
    for ftype, cnt in field_counts.most_common(20):
        print(f"    {ftype:<30s}  {cnt:>8,}  ({100 * cnt / max(processed, 1):5.1f}%)")
    print()
    print(f"  Output: {OUT_FILE}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Coefficient Field Signature Extractor (S32)")
    parser.add_argument("--max-formulas", type=int, default=100_000,
                        help="Cap on formula trees to process (default: 100000)")
    parser.add_argument("--sample", type=int, default=None,
                        help="Reservoir-sample N formulas instead of streaming all")
    args = parser.parse_args()
    run(max_formulas=args.max_formulas, sample_size=args.sample)


if __name__ == "__main__":
    main()
