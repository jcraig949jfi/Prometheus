"""
Recursion Operator Signature Extractor (S33) — linear recurrence detection.
=============================================================================
For OEIS sequences, applies the Berlekamp-Massey algorithm to detect linear
recurrences, then extracts the characteristic polynomial and its roots.

Usage:
    python recursion_operator_signatures.py                      # full run
    python recursion_operator_signatures.py --max-formulas 50000 # cap seqs
    python recursion_operator_signatures.py --sample 20000       # sample
"""

import argparse
import gzip
import json
import math
import sys
import time
import random
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
OEIS_DATA = ROOT / "cartography" / "oeis" / "data"
STRIPPED_GZ = OEIS_DATA / "stripped_full.gz"
STRIPPED_FALLBACK = OEIS_DATA / "stripped.gz"
STRIPPED_TXT = OEIS_DATA / "stripped_new.txt"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_FILE = OUT_DIR / "recursion_operator_signatures.jsonl"


# ---------------------------------------------------------------------------
# OEIS loader
# ---------------------------------------------------------------------------

def load_oeis_sequences(min_length=20, max_seqs=None):
    """Parse OEIS stripped format, keep sequences with >= min_length terms."""
    if STRIPPED_GZ.exists():
        src, opener = STRIPPED_GZ, lambda p: gzip.open(p, "rt", encoding="utf-8", errors="ignore")
    elif STRIPPED_FALLBACK.exists():
        src, opener = STRIPPED_FALLBACK, lambda p: gzip.open(p, "rt", encoding="utf-8", errors="ignore")
    elif STRIPPED_TXT.exists():
        src, opener = STRIPPED_TXT, lambda p: open(p, "r", encoding="utf-8", errors="ignore")
    else:
        print(f"  ERROR: no OEIS stripped file found")
        return {}

    print(f"  Loading OEIS sequences from {src.name} (min_length={min_length}) ...")
    seqs = {}
    with opener(src) as f:
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


# ---------------------------------------------------------------------------
# Berlekamp-Massey algorithm (over rationals)
# ---------------------------------------------------------------------------

def berlekamp_massey(sequence):
    """Find minimal linear recurrence relation using Berlekamp-Massey.

    Returns (coefficients, degree) where:
      a(n) = -c[0]*a(n-1) - c[1]*a(n-2) - ... - c[deg-1]*a(n-deg)

    Uses floating-point for speed; exact integer arithmetic would be better
    for very long sequences but this suffices for signature extraction.
    """
    n = len(sequence)
    if n == 0:
        return [], 0

    # Work with floats for numerical stability
    s = [float(x) for x in sequence]

    b = [1.0]
    c = [1.0]
    l_deg = 0
    m = 1
    d = 1.0

    for i in range(n):
        # Compute discrepancy
        disc = s[i]
        for j in range(1, l_deg + 1):
            if j < len(c):
                disc += c[j] * s[i - j]

        if abs(disc) < 1e-10:
            m += 1
        elif 2 * l_deg <= i:
            t = list(c)
            coef = -disc / d
            while len(c) < len(b) + m:
                c.append(0.0)
            for j in range(len(b)):
                c[j + m] += coef * b[j]
            l_deg = i + 1 - l_deg
            b = t
            d = disc
            m = 1
        else:
            coef = -disc / d
            while len(c) < len(b) + m:
                c.append(0.0)
            for j in range(len(b)):
                c[j + m] += coef * b[j]
            m += 1

    # Extract recurrence coefficients (skip c[0] = 1)
    coeffs = c[1:l_deg + 1]
    return coeffs, l_deg


def verify_recurrence(sequence, coeffs, degree):
    """Check if the recurrence actually reproduces the sequence."""
    if degree == 0 or not coeffs:
        return False
    n = len(sequence)
    if degree >= n:
        return False

    # Verify on the portion of the sequence not used to fit
    errors = 0
    check_start = degree
    check_end = min(n, degree + max(20, n // 2))

    for i in range(check_start, check_end):
        predicted = 0.0
        for j in range(degree):
            if j < len(coeffs):
                predicted -= coeffs[j] * sequence[i - j - 1]
        # Allow small floating-point error relative to magnitude
        actual = float(sequence[i])
        tol = max(1.0, abs(actual) * 1e-6)
        if abs(predicted - actual) > tol:
            errors += 1

    max_errors = max(1, (check_end - check_start) // 10)
    return errors <= max_errors


def compute_roots(coeffs):
    """Compute roots of characteristic polynomial x^d + c[0]*x^(d-1) + ...
    Returns list of (real, imag) tuples."""
    try:
        import numpy as np
        # Characteristic polynomial: x^d + c[0]*x^(d-1) + c[1]*x^(d-2) + ...
        # In numpy.roots format: [1, c[0], c[1], ..., c[d-1]]
        poly = [1.0] + [float(c) for c in coeffs]
        roots = np.roots(poly)
        result = []
        for r in roots:
            result.append((round(float(r.real), 8), round(float(r.imag), 8)))
        return result
    except (ImportError, Exception):
        return None


def dominant_root(roots):
    """Find the root with largest absolute value."""
    if not roots:
        return None
    best = max(roots, key=lambda r: math.sqrt(r[0] ** 2 + r[1] ** 2))
    return {
        "real": best[0],
        "imag": best[1],
        "modulus": round(math.sqrt(best[0] ** 2 + best[1] ** 2), 8),
    }


# ---------------------------------------------------------------------------
# Signature extraction
# ---------------------------------------------------------------------------

def sequence_recurrence(seq_id, terms):
    """Extract recurrence operator signature for a sequence."""
    n = len(terms)
    coeffs, degree = berlekamp_massey(terms)

    # Validate: degree should be < len/3 for a meaningful recurrence
    is_linear = False
    verified = False
    char_coeffs = None
    roots = None
    dom_root = None

    if degree > 0 and degree < n // 3:
        verified = verify_recurrence(terms, coeffs, degree)
        if verified:
            is_linear = True
            # Round coefficients for cleaner output
            char_coeffs = [round(c, 8) for c in coeffs]
            roots = compute_roots(coeffs)
            if roots:
                dom_root = dominant_root(roots)

    result = {
        "seq_id": seq_id,
        "is_linear_recurrence": is_linear,
        "recurrence_degree": degree if is_linear else None,
        "characteristic_coeffs": char_coeffs,
        "dominant_root": dom_root,
        "n_roots": len(roots) if roots else 0,
        "n_terms": n,
    }

    # Add root summary if available
    if roots and is_linear:
        real_roots = sum(1 for r, i in roots if abs(i) < 1e-8)
        complex_roots = len(roots) - real_roots
        result["real_roots"] = real_roots
        result["complex_roots"] = complex_roots

    return result


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run(max_seqs=50000, sample_size=None):
    print("=" * 70)
    print("  Recursion Operator Signature Extractor (S33)")
    print("=" * 70)

    t0 = time.time()
    seqs = load_oeis_sequences(min_length=20, max_seqs=max_seqs)

    if sample_size and sample_size < len(seqs):
        keys = random.sample(list(seqs.keys()), sample_size)
        seqs = {k: seqs[k] for k in keys}
        print(f"  Sampled {len(seqs):,} sequences")

    type_counts = Counter()
    degree_counts = Counter()
    written = 0

    with open(OUT_FILE, "w", encoding="utf-8") as out:
        for i, (sid, terms) in enumerate(seqs.items()):
            sig = sequence_recurrence(sid, terms)
            out.write(json.dumps(sig, separators=(",", ":")) + "\n")

            if sig["is_linear_recurrence"]:
                type_counts["linear_recurrence"] += 1
                deg = sig["recurrence_degree"]
                if deg is not None:
                    degree_counts[deg] += 1
            else:
                type_counts["non_linear"] += 1

            written += 1
            if (i + 1) % 10_000 == 0:
                elapsed = time.time() - t0
                n_lin = type_counts["linear_recurrence"]
                print(f"    {i + 1:,} processed  (linear: {n_lin:,})  "
                      f"({(i + 1) / max(elapsed, 0.01):,.0f}/s)")

    elapsed = time.time() - t0
    n_lin = type_counts["linear_recurrence"]
    n_nonlin = type_counts["non_linear"]

    print()
    print("=" * 70)
    print(f"  Recursion Operator Signatures Complete")
    print(f"  {'=' * 40}")
    print(f"  Sequences processed:       {written:>12,}")
    print(f"  Linear recurrences found:  {n_lin:>12,}  ({100 * n_lin / max(written, 1):.1f}%)")
    print(f"  Non-linear / high-order:   {n_nonlin:>12,}  ({100 * n_nonlin / max(written, 1):.1f}%)")
    print(f"  Time:                      {elapsed:>11.1f}s")
    if elapsed > 0:
        print(f"  Rate:                      {written / elapsed:>11,.0f}/s")
    print()
    if degree_counts:
        print("  Recurrence degree distribution (top 15):")
        for deg, cnt in degree_counts.most_common(15):
            print(f"    degree {deg:>3d}:  {cnt:>8,}  ({100 * cnt / max(n_lin, 1):5.1f}%)")
    print()
    print(f"  Output: {OUT_FILE}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Recursion Operator Signature Extractor (S33)")
    parser.add_argument("--max-formulas", type=int, default=50_000,
                        help="Cap on OEIS sequences to process (default: 50000)")
    parser.add_argument("--sample", type=int, default=None,
                        help="Random-sample N sequences")
    args = parser.parse_args()
    run(max_seqs=args.max_formulas, sample_size=args.sample)


if __name__ == "__main__":
    main()
