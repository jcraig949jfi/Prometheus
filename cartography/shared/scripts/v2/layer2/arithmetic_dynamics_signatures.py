"""
Arithmetic Dynamics Signature Extractor (S27) — orbit structure from sequences.
================================================================================
Treats OEIS sequences as iterated maps and extracts dynamical invariants:
Lyapunov exponents, orbit types, periodicity, and return map statistics.

Usage:
    python arithmetic_dynamics_signatures.py                      # full run
    python arithmetic_dynamics_signatures.py --max-formulas 50000 # cap seqs
    python arithmetic_dynamics_signatures.py --sample 20000       # sample
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
OUT_FILE = OUT_DIR / "arithmetic_dynamics_signatures.jsonl"


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
# Dynamical signature extraction
# ---------------------------------------------------------------------------

def detect_returns(terms):
    """Count how many times a value recurs (periodic orbit detection)."""
    seen = {}
    n_returns = 0
    for i, t in enumerate(terms):
        if t in seen:
            n_returns += 1
        seen.setdefault(t, i)
    return n_returns


def detect_period(terms):
    """Find smallest period k where a(n+k) == a(n) for all n beyond some offset.
    Returns (period, offset) or (None, None) if not periodic."""
    n = len(terms)
    for k in range(1, n // 3 + 1):
        # Check if tail is periodic with period k
        match = True
        start = n - n // 2  # check second half
        for i in range(start, n - k):
            if terms[i] != terms[i + k]:
                match = False
                break
        if match:
            return k, start
    return None, None


def lyapunov_exponent(terms):
    """Estimate Lyapunov exponent from consecutive ratio of differences.
    lambda = mean(log|a(n+1) - a(n)| / |a(n) - a(n-1)|) for valid terms."""
    if len(terms) < 3:
        return None
    ratios = []
    for i in range(1, len(terms) - 1):
        d_prev = abs(terms[i] - terms[i - 1])
        d_next = abs(terms[i + 1] - terms[i])
        if d_prev > 0 and d_next > 0:
            ratios.append(math.log(d_next / d_prev))
    if not ratios:
        return None
    return round(sum(ratios) / len(ratios), 6)


def classify_orbit(lyap, period, n_returns, n_terms):
    """Classify orbit type from Lyapunov exponent and periodicity."""
    if period is not None and period == 1:
        return "fixed_point"
    if period is not None:
        return "periodic"
    if lyap is None:
        return "undetermined"
    if abs(lyap) < 0.01:
        # Near-zero Lyapunov: quasiperiodic if many returns
        if n_returns > n_terms * 0.3:
            return "quasiperiodic"
        return "quasiperiodic"
    if lyap > 0.1:
        return "chaotic"
    if lyap < -0.1:
        return "contracting"
    return "quasiperiodic"


def phase_portrait_stats(terms):
    """Statistics of the (a(n), a(n+1)) phase portrait."""
    if len(terms) < 2:
        return {}
    pairs_x = terms[:-1]
    pairs_y = terms[1:]

    # Basic stats
    n = len(pairs_x)
    mean_x = sum(pairs_x) / n
    mean_y = sum(pairs_y) / n

    # Correlation coefficient
    var_x = sum((x - mean_x) ** 2 for x in pairs_x)
    var_y = sum((y - mean_y) ** 2 for y in pairs_y)
    cov_xy = sum((pairs_x[i] - mean_x) * (pairs_y[i] - mean_y) for i in range(n))

    denom = math.sqrt(var_x * var_y) if var_x > 0 and var_y > 0 else 0
    correlation = round(cov_xy / denom, 6) if denom > 0 else 0.0

    # How many points on the diagonal (a(n) == a(n+1))?
    n_diagonal = sum(1 for i in range(n) if pairs_x[i] == pairs_y[i])

    # Unique points in phase space
    unique_pairs = len(set(zip(pairs_x, pairs_y)))

    return {
        "correlation": correlation,
        "n_diagonal": n_diagonal,
        "unique_pairs": unique_pairs,
        "phase_density": round(unique_pairs / max(n, 1), 6),
    }


def sequence_dynamics(seq_id, terms):
    """Compute full dynamics signature for a sequence."""
    n_returns = detect_returns(terms)
    period, period_offset = detect_period(terms)
    lyap = lyapunov_exponent(terms)
    orbit = classify_orbit(lyap, period, n_returns, len(terms))
    phase = phase_portrait_stats(terms)

    return {
        "seq_id": seq_id,
        "lyapunov": lyap,
        "orbit_type": orbit,
        "period": period,
        "n_returns": n_returns,
        "n_terms": len(terms),
        "phase_portrait_stats": phase,
    }


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run(max_seqs=50000, sample_size=None):
    print("=" * 70)
    print("  Arithmetic Dynamics Signature Extractor (S27)")
    print("=" * 70)

    t0 = time.time()
    seqs = load_oeis_sequences(min_length=20, max_seqs=max_seqs)

    if sample_size and sample_size < len(seqs):
        keys = random.sample(list(seqs.keys()), sample_size)
        seqs = {k: seqs[k] for k in keys}
        print(f"  Sampled {len(seqs):,} sequences")

    orbit_counts = Counter()
    written = 0

    with open(OUT_FILE, "w", encoding="utf-8") as out:
        for i, (sid, terms) in enumerate(seqs.items()):
            sig = sequence_dynamics(sid, terms)
            out.write(json.dumps(sig, separators=(",", ":")) + "\n")
            orbit_counts[sig["orbit_type"]] += 1
            written += 1

            if (i + 1) % 10_000 == 0:
                elapsed = time.time() - t0
                print(f"    {i + 1:,} processed  ({(i + 1) / max(elapsed, 0.01):,.0f}/s)")

    elapsed = time.time() - t0

    print()
    print("=" * 70)
    print(f"  Arithmetic Dynamics Signatures Complete")
    print(f"  {'=' * 40}")
    print(f"  Sequences processed:   {written:>12,}")
    print(f"  Time:                  {elapsed:>11.1f}s")
    if elapsed > 0:
        print(f"  Rate:                  {written / elapsed:>11,.0f}/s")
    print()
    print("  Orbit type distribution:")
    for otype, cnt in orbit_counts.most_common():
        print(f"    {otype:<20s}  {cnt:>8,}  ({100 * cnt / max(written, 1):5.1f}%)")
    print()
    print(f"  Output: {OUT_FILE}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Arithmetic Dynamics Signature Extractor (S27)")
    parser.add_argument("--max-formulas", type=int, default=50_000,
                        help="Cap on OEIS sequences to process (default: 50000)")
    parser.add_argument("--sample", type=int, default=None,
                        help="Random-sample N sequences")
    args = parser.parse_args()
    run(max_seqs=args.max_formulas, sample_size=args.sample)


if __name__ == "__main__":
    main()
