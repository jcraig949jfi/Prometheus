#!/usr/bin/env python3
"""
Oscillation Detector — Aporia Barrier 5 Test (Batch 01)

Tests whether computational evidence for conjectures OSCILLATES with parameter
rather than monotonically converging. Oscillation without convergence is a
potential signature of logical independence from ZFC.

Three tests on Batch 01 results:
  1. abc Szpiro: median Szpiro ratio vs log(conductor) bins
  2. BSD rank agreement: fraction rank==analytic_rank per conductor bin
  3. Chowla: autocorrelation |r(1,N)| decay across N = 10^4..10^8

References:
  - aporia/docs/five_barriers_report.md, Barrier 5
  - Friedman, Concrete Mathematical Incompleteness
  - Ben-David et al., ML learnability independent of ZFC, 2019
"""

import sys
import numpy as np

# ---------------------------------------------------------------------------
# Classification engine
# ---------------------------------------------------------------------------

def classify_sequence(values, labels=None):
    """
    Classify a numeric sequence as CONVERGENT, OSCILLATING, or FLAT.

    CONVERGENT: monotone (or nearly) toward a limit — at most 2 direction changes.
    OSCILLATING: 3+ direction changes.
    FLAT: range < 1% of mean (or all identical).

    Returns (classification, direction_changes, details_str).
    """
    vals = np.asarray(values, dtype=float)
    if len(vals) < 3:
        return "INSUFFICIENT_DATA", 0, "Need >= 3 data points"

    val_range = np.ptp(vals)
    val_mean = np.mean(np.abs(vals))
    if val_mean == 0 or val_range / max(val_mean, 1e-15) < 0.01:
        return "FLAT", 0, f"range/mean = {val_range/max(val_mean,1e-15):.4f} < 0.01"

    # Count direction changes in the sequence of differences
    diffs = np.diff(vals)
    # Remove near-zero diffs (noise floor: < 1% of range)
    noise_floor = 0.01 * val_range
    significant = diffs[np.abs(diffs) > noise_floor]
    if len(significant) < 2:
        return "FLAT", 0, "No significant differences after noise filtering"

    signs = np.sign(significant)
    direction_changes = int(np.sum(signs[1:] != signs[:-1]))

    if direction_changes >= 3:
        classification = "OSCILLATING"
    else:
        classification = "CONVERGENT"

    return classification, direction_changes, f"{direction_changes} direction change(s)"


def print_result(test_name, param_label, pairs, classification, direction_changes, details):
    """Pretty-print a single test result."""
    print(f"\n{'='*72}")
    print(f"  TEST: {test_name}")
    print(f"{'='*72}")
    print(f"\n  {'Parameter':>20s}  {'Statistic':>16s}")
    print(f"  {'-'*20}  {'-'*16}")
    for p, v in pairs:
        print(f"  {str(p):>20s}  {v:>16.6f}")
    print()
    print(f"  Classification : {classification}  ({details})")

    if classification == "OSCILLATING":
        verdict = (f"*** INDEPENDENCE SIGNAL: {direction_changes} oscillations "
                   f"detected — evidence does NOT converge monotonically.")
    elif classification == "CONVERGENT":
        verdict = "Evidence converges monotonically — no independence signature."
    elif classification == "FLAT":
        verdict = "Evidence is flat — trivially convergent, no independence signature."
    else:
        verdict = f"Insufficient data for classification."

    print(f"  Verdict        : {verdict}")
    print()


# ---------------------------------------------------------------------------
# Test 1: abc Szpiro ratio vs log(conductor)
# ---------------------------------------------------------------------------

def test_szpiro():
    """
    Bin elliptic curves by log(conductor), compute median Szpiro ratio per bin.
    If medians oscillate rather than converge, flag as independence signal.
    """
    import psycopg2

    conn = psycopg2.connect(
        host='localhost', port=5432,
        dbname='lmfdb', user='lmfdb', password='lmfdb'
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT szpiro_ratio::float, conductor::float
        FROM ec_curvedata
        WHERE szpiro_ratio IS NOT NULL
          AND szpiro_ratio != ''
          AND conductor IS NOT NULL
          AND conductor != ''
          AND conductor::float > 0
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        print("\n  [Szpiro] No data returned from ec_curvedata.")
        return

    szpiro = np.array([r[0] for r in rows], dtype=float)
    cond = np.array([r[1] for r in rows], dtype=float)
    log_cond = np.log10(cond)

    # 20 equal-width bins across log(conductor) range
    n_bins = 20
    bin_edges = np.linspace(log_cond.min(), log_cond.max(), n_bins + 1)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    medians = []
    pairs = []
    for i in range(n_bins):
        mask = (log_cond >= bin_edges[i]) & (log_cond < bin_edges[i + 1])
        if i == n_bins - 1:  # include right edge in last bin
            mask |= (log_cond == bin_edges[i + 1])
        subset = szpiro[mask]
        if len(subset) < 5:
            continue
        med = float(np.median(subset))
        medians.append(med)
        pairs.append((f"log10(N)={bin_centers[i]:.2f}", med))

    if len(medians) < 3:
        print("\n  [Szpiro] Too few populated bins for classification.")
        return

    cls, dc, det = classify_sequence(medians)
    print_result(
        "abc Szpiro Ratio vs log(conductor)",
        "log10(conductor) bin",
        pairs, cls, dc, det
    )


# ---------------------------------------------------------------------------
# Test 2: BSD rank agreement fraction per conductor bin
# ---------------------------------------------------------------------------

def test_bsd():
    """
    For each conductor bin, compute fraction where rank == analytic_rank.
    If always 1.0, classify as trivially convergent (FLAT).
    """
    import psycopg2

    conn = psycopg2.connect(
        host='localhost', port=5432,
        dbname='lmfdb', user='lmfdb', password='lmfdb'
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT rank::int, analytic_rank::int, conductor::float
        FROM ec_curvedata
        WHERE rank IS NOT NULL AND rank != ''
          AND analytic_rank IS NOT NULL AND analytic_rank != ''
          AND conductor IS NOT NULL AND conductor != ''
          AND conductor::float > 0
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        print("\n  [BSD] No data returned from ec_curvedata.")
        return

    rank = np.array([r[0] for r in rows], dtype=int)
    arank = np.array([r[1] for r in rows], dtype=int)
    cond = np.array([r[2] for r in rows], dtype=float)
    log_cond = np.log10(cond)

    agree = (rank == arank).astype(float)

    n_bins = 20
    bin_edges = np.linspace(log_cond.min(), log_cond.max(), n_bins + 1)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    fracs = []
    pairs = []
    for i in range(n_bins):
        mask = (log_cond >= bin_edges[i]) & (log_cond < bin_edges[i + 1])
        if i == n_bins - 1:
            mask |= (log_cond == bin_edges[i + 1])
        subset = agree[mask]
        if len(subset) < 5:
            continue
        frac = float(np.mean(subset))
        fracs.append(frac)
        pairs.append((f"log10(N)={bin_centers[i]:.2f}", frac))

    if len(fracs) < 3:
        print("\n  [BSD] Too few populated bins for classification.")
        return

    cls, dc, det = classify_sequence(fracs)
    print_result(
        "BSD Rank Agreement Fraction vs log(conductor)",
        "log10(conductor) bin",
        pairs, cls, dc, det
    )


# ---------------------------------------------------------------------------
# Test 3: Chowla autocorrelation decay
# ---------------------------------------------------------------------------

def mobius_sieve(n):
    """
    Compute Mobius function mu(k) for k = 1..n using a sieve.
    Returns array of length n+1 (index 0 unused).
    """
    mu = np.zeros(n + 1, dtype=np.int8)
    mu[1] = 1
    # Smallest prime factor sieve
    is_prime = np.ones(n + 1, dtype=bool)
    is_prime[0] = is_prime[1] = False

    for p in range(2, n + 1):
        if not is_prime[p]:
            continue
        # p is prime — mark composites
        for multiple in range(2 * p, n + 1, p):
            is_prime[multiple] = False

    # Sieve for mu: factorize via smallest prime factor
    # More efficient: direct multiplicative sieve
    mu = np.ones(n + 1, dtype=np.int8)
    mu[0] = 0
    # Track if any p^2 divides k
    square_free = np.ones(n + 1, dtype=bool)

    for p in range(2, int(n**0.5) + 1):
        if not is_prime[p]:
            continue
        p2 = p * p
        # Mark multiples of p^2 as not square-free
        for m in range(p2, n + 1, p2):
            square_free[m] = False

    # Now compute mu using a direct sieve approach
    # Reset and use a proper multiplicative sieve
    mu = np.zeros(n + 1, dtype=np.int8)
    mu[1] = 1
    # omega[k] = number of distinct prime factors
    omega = np.zeros(n + 1, dtype=np.int8)

    for p in range(2, n + 1):
        if not is_prime[p]:
            continue
        for m in range(p, n + 1, p):
            omega[m] += 1

    # mu(k) = (-1)^omega(k) if square-free, else 0
    for k in range(2, n + 1):
        if square_free[k]:
            mu[k] = (-1) ** omega[k]
        else:
            mu[k] = 0

    return mu


def chowla_autocorrelation(N, h=1):
    """
    Compute Chowla-type autocorrelation:
        r(h, N) = (1/N) * sum_{k=1}^{N} mu(k) * mu(k+h)

    Returns float.
    """
    mu = mobius_sieve(N + h)
    # Vectorized dot product
    r = np.sum(mu[1:N+1].astype(np.float64) * mu[1+h:N+1+h].astype(np.float64)) / N
    return r


def test_chowla():
    """
    Compute |r(1, N)| for N = 10^4, 10^5, 10^6, 10^7, 10^8.
    Check whether |r| decays monotonically or oscillates.
    """
    test_Ns = [10**4, 10**5, 10**6, 10**7]
    # 10^8 requires ~400MB for the sieve — attempt it but handle OOM
    try_large = True

    pairs = []
    abs_vals = []

    for N in test_Ns:
        print(f"  Computing Chowla r(1, N={N:.0e})...", flush=True)
        r = chowla_autocorrelation(N, h=1)
        abs_r = abs(r)
        pairs.append((f"N={N:.0e}", abs_r))
        abs_vals.append(abs_r)

    if try_large:
        N = 10**8
        try:
            print(f"  Computing Chowla r(1, N={N:.0e})... (large, may take a moment)", flush=True)
            r = chowla_autocorrelation(N, h=1)
            abs_r = abs(r)
            pairs.append((f"N={N:.0e}", abs_r))
            abs_vals.append(abs_r)
        except MemoryError:
            print(f"  Skipping N={N:.0e} — insufficient memory for sieve.", flush=True)

    if len(abs_vals) < 3:
        print("\n  [Chowla] Too few data points.")
        return

    cls, dc, det = classify_sequence(abs_vals)
    print_result(
        "Chowla Autocorrelation |r(1,N)| Decay",
        "N",
        pairs, cls, dc, det
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 72)
    print("  OSCILLATION DETECTOR — Aporia Barrier 5 (Independence Signatures)")
    print("  Batch 01 Results")
    print("=" * 72)

    # Test 1: Szpiro
    try:
        test_szpiro()
    except Exception as e:
        print(f"\n  [Szpiro] FAILED: {e}")

    # Test 2: BSD
    try:
        test_bsd()
    except Exception as e:
        print(f"\n  [BSD] FAILED: {e}")

    # Test 3: Chowla
    try:
        test_chowla()
    except Exception as e:
        print(f"\n  [Chowla] FAILED: {e}")

    print("\n" + "=" * 72)
    print("  SUMMARY")
    print("=" * 72)
    print("""
  Barrier 5 test complete. Interpretation guide:

    CONVERGENT  — Evidence converges monotonically. Standard behavior;
                  no independence signal.
    OSCILLATING — Evidence oscillates with parameter (3+ direction changes).
                  Potential independence signature. Warrants deeper
                  investigation with finer bins / larger ranges.
    FLAT        — No trend detected. Trivially convergent or degenerate
                  test configuration.

  If ANY test shows OSCILLATING, it does NOT prove independence from ZFC.
  It identifies conjectures where the finite evidence is structurally
  inconsistent with simple convergence — the empirical signature that
  Barrier 5 predicts for independent statements.
""")


if __name__ == "__main__":
    main()
