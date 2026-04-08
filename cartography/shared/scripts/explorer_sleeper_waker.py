"""
Explorer: Sleeper Waker — Fingerprint ALL sleeping beauties with F13 growth filter.
====================================================================================
For each OEIS sleeping beauty (high entropy, low connectivity), apply transforms
(first_differences, partial_sums, ratios) and test partial correlation against
baseline sequences (primes, squares, Fibonacci, triangular). A sleeper SURVIVES
the F13 filter only if it correlates with primes (r_partial > 0.3, p < 0.01)
but does NOT correlate equally with squares.

This finds genuine bridges — sleepers connected to the primes through hidden
transformations, not mere growth-rate artifacts.

Usage:
    python explorer_sleeper_waker.py
"""

import json
import math
import random
import sys
import time
from collections import Counter
from pathlib import Path

# --- Imports from search_engine ---
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from search_engine import (
    _load_oeis, _oeis_cache,
    _load_oeis_crossrefs, _oeis_xref_cache, _oeis_xref_reverse,
    _load_oeis_names, _oeis_names_cache,
)

REPO = Path(__file__).resolve().parents[3]
OUTPUT_DIR = REPO / "cartography" / "convergence" / "data"
OUTPUT_FILE = OUTPUT_DIR / "sleeper_wakeup_candidates.json"

# Parameters
ENTROPY_THRESHOLD = 3.91       # Shannon entropy of first diffs
MAX_DEGREE = 2                 # Total cross-ref degree (in + out)
MIN_TERMS = 20                 # Minimum terms for correlation
MAX_SLEEPERS = 20_000          # Cap for initial run
CORR_THRESHOLD = 0.3           # Partial correlation with primes
P_VALUE_THRESHOLD = 0.01       # Significance threshold
PREFIX_LEN = 8                 # For lookup dict


# ---------------------------------------------------------------------------
# Baseline gauntlet sequences (generated, not loaded from OEIS)
# ---------------------------------------------------------------------------

def gen_primes(n: int) -> list[int]:
    """Generate first n primes."""
    primes = []
    candidate = 2
    while len(primes) < n:
        is_prime = True
        for p in primes:
            if p * p > candidate:
                break
            if candidate % p == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(candidate)
        candidate += 1
    return primes


def gen_squares(n: int) -> list[int]:
    return [(i + 1) ** 2 for i in range(n)]


def gen_fibonacci(n: int) -> list[int]:
    fibs = [1, 1]
    while len(fibs) < n:
        fibs.append(fibs[-1] + fibs[-2])
    return fibs[:n]


def gen_triangular(n: int) -> list[int]:
    return [(i + 1) * (i + 2) // 2 for i in range(n)]


# Pre-generate baselines (enough terms for any sequence we'll test)
BASELINE_LEN = 200
PRIMES = gen_primes(BASELINE_LEN)
SQUARES = gen_squares(BASELINE_LEN)
FIBONACCI = gen_fibonacci(BASELINE_LEN)
TRIANGULAR = gen_triangular(BASELINE_LEN)


# ---------------------------------------------------------------------------
# Transform functions
# ---------------------------------------------------------------------------

def first_differences(terms: list[int]) -> list[int] | None:
    if len(terms) < 2:
        return None
    return [terms[i + 1] - terms[i] for i in range(len(terms) - 1)]


def partial_sums(terms: list[int]) -> list[int] | None:
    if len(terms) < 2:
        return None
    s, acc = [], 0
    for t in terms:
        acc += t
        s.append(acc)
    return s


def ratios_float(terms: list[int]) -> list[float] | None:
    """Consecutive ratios (float). Only for positive sequences."""
    if len(terms) < 2 or any(t <= 0 for t in terms):
        return None
    return [terms[i + 1] / terms[i] for i in range(len(terms) - 1)]


TRANSFORMS = {
    "first_differences": first_differences,
    "partial_sums": partial_sums,
    "ratios": ratios_float,
}


# ---------------------------------------------------------------------------
# Correlation with t-test (no scipy dependency)
# ---------------------------------------------------------------------------

def pearson_r(x: list[float], y: list[float]) -> float | None:
    """Pearson correlation coefficient. Returns None if degenerate."""
    n = len(x)
    if n < 3:
        return None
    mx = sum(x) / n
    my = sum(y) / n
    sxx = sum((xi - mx) ** 2 for xi in x)
    syy = sum((yi - my) ** 2 for yi in y)
    sxy = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    if sxx == 0 or syy == 0:
        return None
    return sxy / math.sqrt(sxx * syy)


def p_value_from_r(r: float, n: int) -> float:
    """Approximate two-sided p-value for Pearson r using t-distribution.

    Uses the approximation: t = r * sqrt((n-2)/(1-r^2)), df = n-2.
    Then approximate p from the t statistic using a normal approximation
    (valid for df > 20).
    """
    if n <= 2 or abs(r) >= 1.0:
        return 0.0 if abs(r) >= 1.0 else 1.0
    df = n - 2
    t_stat = r * math.sqrt(df / (1.0 - r * r))
    # Normal CDF approximation for |t| (valid for large df)
    z = abs(t_stat)
    # Abramowitz and Stegun approximation
    p_one_tail = 0.5 * math.erfc(z / math.sqrt(2))
    return 2.0 * p_one_tail


def partial_correlation(x: list[float], y: list[float],
                        z: list[float]) -> tuple[float | None, float]:
    """Partial correlation of x and y, controlling for z.

    Returns (r_partial, p_value).
    """
    n = min(len(x), len(y), len(z))
    if n < MIN_TERMS:
        return None, 1.0
    x, y, z = x[:n], y[:n], z[:n]

    rxy = pearson_r(x, y)
    rxz = pearson_r(x, z)
    ryz = pearson_r(y, z)

    if rxy is None or rxz is None or ryz is None:
        return None, 1.0

    denom = math.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))
    if denom < 1e-15:
        return None, 1.0

    r_partial = (rxy - rxz * ryz) / denom
    r_partial = max(-1.0, min(1.0, r_partial))
    p = p_value_from_r(r_partial, n - 1)  # df adjustment for partial
    return r_partial, p


# ---------------------------------------------------------------------------
# Identify sleeping beauties (ALL, then sample)
# ---------------------------------------------------------------------------

def find_all_sleepers() -> list[tuple[str, list[int]]]:
    """Return ALL (seq_id, terms) pairs meeting sleeper criteria."""
    _load_oeis()
    _load_oeis_crossrefs()

    sleepers = []
    for seq_id, terms in _oeis_cache.items():
        if len(terms) < MIN_TERMS:
            continue

        # Connectivity check: total degree <= MAX_DEGREE
        out_deg = len(_oeis_xref_cache.get(seq_id, set()))
        in_deg = len(_oeis_xref_reverse.get(seq_id, set()))
        if out_deg + in_deg > MAX_DEGREE:
            continue

        # Shannon entropy of first differences
        diffs = [terms[i + 1] - terms[i] for i in range(min(len(terms) - 1, 30))]
        if not diffs:
            continue
        counts = Counter(diffs)
        total = len(diffs)
        entropy = -sum(
            (c / total) * math.log2(c / total)
            for c in counts.values() if c > 0
        )
        if entropy < ENTROPY_THRESHOLD:
            continue

        sleepers.append((seq_id, terms))

    return sleepers


# ---------------------------------------------------------------------------
# Build 8-term prefix lookup dict (for downstream use / verification)
# ---------------------------------------------------------------------------

def build_prefix_lookup(cache: dict, n: int = PREFIX_LEN) -> dict[tuple, list[str]]:
    """Map tuple(first n terms) -> [seq_ids] for O(1) matching."""
    lookup: dict[tuple, list[str]] = {}
    for seq_id, terms in cache.items():
        if len(terms) < n:
            continue
        key = tuple(terms[:n])
        lookup.setdefault(key, []).append(seq_id)
    return lookup


# ---------------------------------------------------------------------------
# F13 growth-rate filter
# ---------------------------------------------------------------------------

def apply_f13(seq_id: str, terms: list[int],
              transform_name: str, transformed: list) -> dict | None:
    """Apply the F13 filter to a transformed sequence.

    Survives only if:
      - partial_corr(transformed, primes | controlling squares) > CORR_THRESHOLD
      - p < P_VALUE_THRESHOLD
      - raw corr with squares < raw corr with primes (growth filter)

    Returns a result dict if it survives, else None.
    """
    n = min(len(transformed), BASELINE_LEN)
    if n < MIN_TERMS:
        return None

    # Convert to float for correlation
    x = [float(v) for v in transformed[:n]]
    primes_slice = [float(v) for v in PRIMES[:n]]
    squares_slice = [float(v) for v in SQUARES[:n]]
    fib_slice = [float(v) for v in FIBONACCI[:n]]
    tri_slice = [float(v) for v in TRIANGULAR[:n]]

    # Raw correlation with primes and squares
    r_primes = pearson_r(x, primes_slice)
    r_squares = pearson_r(x, squares_slice)
    if r_primes is None or r_squares is None:
        return None

    # F13 growth filter: must correlate MORE with primes than squares
    if abs(r_primes) <= abs(r_squares):
        return None

    # Partial correlation: primes controlling for squares
    r_partial, p_val = partial_correlation(x, primes_slice, squares_slice)
    if r_partial is None:
        return None
    if abs(r_partial) < CORR_THRESHOLD or p_val >= P_VALUE_THRESHOLD:
        return None

    # Also compute correlations with Fibonacci and triangular for context
    r_fib = pearson_r(x, fib_slice)
    r_tri = pearson_r(x, tri_slice)

    return {
        "seq_id": seq_id,
        "seq_name": _oeis_names_cache.get(seq_id, ""),
        "transform": transform_name,
        "n_terms": n,
        "r_primes": round(r_primes, 4),
        "r_squares": round(r_squares, 4),
        "r_partial_primes_ctrl_squares": round(r_partial, 4),
        "p_value": round(p_val, 6),
        "r_fibonacci": round(r_fib, 4) if r_fib is not None else None,
        "r_triangular": round(r_tri, 4) if r_tri is not None else None,
        "first_10_original": terms[:10],
        "first_10_transformed": [round(v, 4) if isinstance(v, float) else v
                                 for v in transformed[:10]],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run():
    t0 = time.time()
    print("=" * 70)
    print("Explorer: Sleeper Waker — F13 Growth-Rate Filter")
    print("=" * 70)

    # 1. Load data
    print("\n[1] Loading OEIS data...")
    _load_oeis()
    _load_oeis_names()
    _load_oeis_crossrefs()

    # 2. Build prefix lookup
    print(f"\n[2] Building {PREFIX_LEN}-term prefix lookup...")
    lookup = build_prefix_lookup(_oeis_cache, PREFIX_LEN)
    print(f"    Lookup: {len(lookup):,} unique prefixes from {len(_oeis_cache):,} sequences")

    # 3. Find all sleepers
    print("\n[3] Identifying ALL sleeping beauties "
          f"(entropy >= {ENTROPY_THRESHOLD}, degree <= {MAX_DEGREE})...")
    all_sleepers = find_all_sleepers()
    print(f"    Found {len(all_sleepers):,} total sleepers")

    # 4. Sample if needed
    if len(all_sleepers) > MAX_SLEEPERS:
        random.seed(42)
        sleepers = random.sample(all_sleepers, MAX_SLEEPERS)
        print(f"    Sampled {MAX_SLEEPERS:,} for this run")
    else:
        sleepers = all_sleepers

    # 5. Apply transforms + F13 filter
    print(f"\n[4] Applying transforms + F13 filter to {len(sleepers):,} sleepers...")
    survivors = []
    transform_tested = {name: 0 for name in TRANSFORMS}
    transform_survived = {name: 0 for name in TRANSFORMS}

    for idx, (seq_id, terms) in enumerate(sleepers):
        if (idx + 1) % 2000 == 0:
            elapsed = time.time() - t0
            print(f"    Progress: {idx + 1:,}/{len(sleepers):,} "
                  f"({elapsed:.0f}s, {len(survivors)} survivors so far)")

        for tname, tfunc in TRANSFORMS.items():
            transformed = tfunc(terms)
            if transformed is None or len(transformed) < MIN_TERMS:
                continue
            transform_tested[tname] += 1

            result = apply_f13(seq_id, terms, tname, transformed)
            if result is not None:
                survivors.append(result)
                transform_survived[tname] += 1

    elapsed = time.time() - t0

    # 6. Sort survivors by partial correlation strength
    survivors.sort(key=lambda s: -abs(s["r_partial_primes_ctrl_squares"]))

    # 7. Report
    print(f"\n{'=' * 70}")
    print("RESULTS")
    print(f"{'=' * 70}")
    print(f"  Total sleepers in OEIS:     {len(all_sleepers):,}")
    print(f"  Sleepers tested this run:   {len(sleepers):,}")
    print(f"  Survivors (F13 passed):     {len(survivors):,}")
    print(f"  Survival rate:              "
          f"{100 * len(survivors) / max(len(sleepers), 1):.2f}%")
    print(f"  Elapsed time:               {elapsed:.1f}s")

    print(f"\nTransform breakdown:")
    print(f"  {'Transform':<25s} {'Tested':>10s} {'Survived':>10s} {'Rate':>8s}")
    print(f"  {'-'*25} {'-'*10} {'-'*10} {'-'*8}")
    for tname in TRANSFORMS:
        tested = transform_tested[tname]
        survived = transform_survived[tname]
        rate = 100 * survived / max(tested, 1)
        print(f"  {tname:<25s} {tested:>10,} {survived:>10,} {rate:>7.2f}%")

    print(f"\nTop 30 survivors (by partial correlation):")
    for i, s in enumerate(survivors[:30]):
        print(f"  [{i+1:2d}] {s['seq_id']} ({s['seq_name'][:50]})")
        print(f"       transform={s['transform']}, r_partial={s['r_partial_primes_ctrl_squares']:.4f}, "
              f"p={s['p_value']:.6f}")
        print(f"       r_primes={s['r_primes']:.4f}, r_squares={s['r_squares']:.4f}, "
              f"r_fib={s['r_fibonacci']}, r_tri={s['r_triangular']}")

    # 8. Save results
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "parameters": {
            "entropy_threshold": ENTROPY_THRESHOLD,
            "max_degree": MAX_DEGREE,
            "min_terms": MIN_TERMS,
            "corr_threshold": CORR_THRESHOLD,
            "p_value_threshold": P_VALUE_THRESHOLD,
            "max_sleepers_sampled": MAX_SLEEPERS,
        },
        "total_sleepers_in_oeis": len(all_sleepers),
        "sleepers_tested": len(sleepers),
        "survivors_count": len(survivors),
        "survival_rate_pct": round(100 * len(survivors) / max(len(sleepers), 1), 2),
        "elapsed_seconds": round(elapsed, 1),
        "transform_tested": transform_tested,
        "transform_survived": transform_survived,
        "survivors": survivors,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    run()
