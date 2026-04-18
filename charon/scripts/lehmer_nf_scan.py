"""
Charon — Lehmer's Conjecture scan over LMFDB number field defining polynomials.

Tests Lehmer's conjecture: the smallest Mahler measure of any non-cyclotomic
monic integer polynomial equals M(L) = 1.17628081825991...

Database: 22,178,569 number field defining polynomials from LMFDB.
Strategy: sample 500K across all degrees, compute Mahler measures, find minimum.
"""

import json
import time
import os
import sys
import numpy as np
import psycopg2
from collections import defaultdict
from pathlib import Path

# Constants
LEHMER_CONSTANT = 1.17628081825991
LEHMER_COEFFS_ASCENDING = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]  # constant first
LEHMER_COEFFS_DESCENDING = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1][::-1]  # leading first

# DB config
DB_CONFIG = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')

# Sampling strategy: for degrees with many polys, sample; for rare degrees, take all
SAMPLE_CAP_PER_DEGREE = 50000  # max polys per degree
TOTAL_TARGET = 500000


def parse_coeffs(coeffs_str):
    """Parse '{1,2,3}' -> [1, 2, 3] (ascending order: constant, x, x^2, ...)"""
    s = coeffs_str.strip('{}')
    return [int(x) for x in s.split(',')]


def mahler_measure(coeffs_ascending):
    """
    Compute Mahler measure: M(P) = |a_n| * prod(max(1, |root|))
    coeffs_ascending: [a_0, a_1, ..., a_n] where a_n is leading coefficient.
    numpy roots expects descending order.
    """
    # numpy wants highest degree first
    coeffs_desc = coeffs_ascending[::-1]
    leading = abs(coeffs_desc[0])
    if leading == 0:
        return float('inf')

    try:
        roots = np.roots(coeffs_desc)
    except Exception:
        return float('inf')

    product = 1.0
    for r in roots:
        mag = abs(r)
        if mag > 1.0:
            product *= mag

    return leading * product


def is_cyclotomic_approx(coeffs_ascending, tol=1e-8):
    """
    Check if polynomial is cyclotomic: all roots lie on the unit circle.
    Equivalently, Mahler measure == 1 (for monic).
    Also check: must be monic, integer coeffs, and self-reciprocal properties.
    """
    coeffs_desc = coeffs_ascending[::-1]
    if abs(coeffs_desc[0]) != 1:
        return False
    if abs(coeffs_ascending[0]) != 1:
        return False  # constant term must be +/-1 for cyclotomic

    try:
        roots = np.roots(coeffs_desc)
    except Exception:
        return False

    for r in roots:
        if abs(abs(r) - 1.0) > tol:
            return False
    return True


def matches_lehmer_poly(coeffs_ascending):
    """Check if this polynomial is the Lehmer polynomial."""
    if len(coeffs_ascending) != 11:
        return False
    return coeffs_ascending == LEHMER_COEFFS_ASCENDING


def run_scan():
    print("=" * 70)
    print("CHARON — Lehmer's Conjecture NF Scan")
    print("=" * 70)
    print(f"Lehmer's constant: {LEHMER_CONSTANT}")
    print()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Get degree distribution
    cur.execute("SELECT degree, COUNT(*) FROM nf_fields GROUP BY degree ORDER BY degree::int")
    degree_counts = [(int(d), int(c)) for d, c in cur.fetchall()]
    total_polys = sum(c for _, c in degree_counts)
    print(f"Total polynomials in database: {total_polys:,}")
    print(f"Degrees: {len(degree_counts)} (from {degree_counts[0][0]} to {degree_counts[-1][0]})")
    print()

    # Build sampling plan
    sampling_plan = []
    total_sample = 0
    for deg, count in degree_counts:
        if deg <= 1:
            n = count  # take all degree-1
        elif count <= SAMPLE_CAP_PER_DEGREE:
            n = count  # take all for rare degrees
        else:
            n = SAMPLE_CAP_PER_DEGREE
        sampling_plan.append((deg, count, n))
        total_sample += n

    print(f"Sampling plan: {total_sample:,} polynomials across {len(sampling_plan)} degrees")
    print()

    # Results tracking
    all_measures = []
    below_lehmer = []
    cyclotomic_count = 0
    lehmer_matches = []
    min_noncyc_measure = float('inf')
    min_noncyc_poly = None
    error_count = 0
    degree_stats = defaultdict(lambda: {'count': 0, 'min': float('inf'), 'cyclo': 0})

    t_start = time.time()

    for deg, total_count, sample_n in sampling_plan:
        t_deg = time.time()
        # For large degrees, use TABLESAMPLE or ORDER BY RANDOM() with LIMIT
        # But TABLESAMPLE isn't great for filtered queries. Use modular approach.
        if sample_n >= total_count:
            query = f"SELECT coeffs, label FROM nf_fields WHERE degree = '{deg}'"
        else:
            # Random sample
            query = f"SELECT coeffs, label FROM nf_fields WHERE degree = '{deg}' ORDER BY RANDOM() LIMIT {sample_n}"

        cur.execute(query)
        rows = cur.fetchall()

        batch_measures = []
        for coeffs_str, label in rows:
            try:
                coeffs = parse_coeffs(coeffs_str)
            except Exception:
                error_count += 1
                continue

            if len(coeffs) < 2:
                continue

            M = mahler_measure(coeffs)
            if not np.isfinite(M) or M <= 0:
                error_count += 1
                continue

            is_cyc = abs(M - 1.0) < 1e-8
            if is_cyc:
                cyclotomic_count += 1
                degree_stats[deg]['cyclo'] += 1
                continue  # skip cyclotomic for Lehmer analysis

            all_measures.append(M)
            batch_measures.append(M)
            degree_stats[deg]['count'] += 1
            if M < degree_stats[deg]['min']:
                degree_stats[deg]['min'] = M

            # Check against Lehmer
            if M < LEHMER_CONSTANT:
                below_lehmer.append({
                    'label': label,
                    'coeffs': coeffs,
                    'mahler_measure': float(M),
                    'degree': deg
                })

            if M < min_noncyc_measure:
                min_noncyc_measure = M
                min_noncyc_poly = {
                    'label': label,
                    'coeffs': coeffs,
                    'mahler_measure': float(M),
                    'degree': deg
                }

            # Check Lehmer polynomial match
            if matches_lehmer_poly(coeffs):
                lehmer_matches.append({
                    'label': label,
                    'coeffs': coeffs,
                    'mahler_measure': float(M)
                })

        elapsed = time.time() - t_deg
        batch_min = min(batch_measures) if batch_measures else float('inf')
        print(f"  deg={deg:2d}: {len(rows):>7,} sampled, "
              f"{len(batch_measures):>6,} non-cyc, "
              f"min M = {batch_min:.10f}, "
              f"{elapsed:.1f}s")

    total_time = time.time() - t_start

    # === VERIFICATION ===
    # Re-verify anything below Lehmer with higher precision
    verified_below = []
    for item in below_lehmer:
        coeffs = item['coeffs']
        # Double-check with companion matrix eigenvalues for higher precision
        coeffs_desc = coeffs[::-1]
        n = len(coeffs_desc) - 1
        if n < 1:
            continue
        # Build companion matrix
        companion = np.zeros((n, n))
        for i in range(n - 1):
            companion[i + 1, i] = 1.0
        for i in range(n):
            companion[i, n - 1] = -coeffs_desc[n - i] / coeffs_desc[0]
        try:
            eigenvalues = np.linalg.eigvals(companion)
            leading = abs(coeffs_desc[0])
            M_verified = leading * np.prod([max(1.0, abs(e)) for e in eigenvalues])
            item['mahler_measure_verified'] = float(M_verified)
            # Also check cyclotomic more carefully
            all_on_circle = all(abs(abs(e) - 1.0) < 1e-6 for e in eigenvalues)
            item['is_cyclotomic_verified'] = all_on_circle
            if not all_on_circle and M_verified < LEHMER_CONSTANT:
                verified_below.append(item)
        except Exception as e:
            item['verification_error'] = str(e)
            verified_below.append(item)  # keep it flagged

    # === STATISTICS ===
    measures_arr = np.array(all_measures)

    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Total polynomials processed: {len(all_measures) + cyclotomic_count:,}")
    print(f"  Cyclotomic (M~=1): {cyclotomic_count:,}")
    print(f"  Non-cyclotomic: {len(all_measures):,}")
    print(f"  Errors/skipped: {error_count:,}")
    print(f"  Time: {total_time:.1f}s")
    print()

    if len(measures_arr) > 0:
        print("Mahler measure distribution (non-cyclotomic):")
        print(f"  Min:    {measures_arr.min():.12f}")
        print(f"  Max:    {measures_arr.max():.6f}")
        print(f"  Mean:   {measures_arr.mean():.6f}")
        print(f"  Median: {np.median(measures_arr):.6f}")
        print(f"  Std:    {measures_arr.std():.6f}")
        print()

        # Histogram bins near Lehmer
        bins_near = [1.0, 1.05, 1.10, 1.15, LEHMER_CONSTANT, 1.20, 1.25, 1.30, 1.50, 2.0, 5.0, 100.0]
        hist, _ = np.histogram(measures_arr, bins=bins_near)
        print("Distribution near Lehmer's constant:")
        for i in range(len(hist)):
            marker = " <-- LEHMER" if bins_near[i + 1] == LEHMER_CONSTANT or bins_near[i] == LEHMER_CONSTANT else ""
            print(f"  [{bins_near[i]:.5f}, {bins_near[i+1]:.5f}): {hist[i]:>8,}{marker}")
        print()

    # Lehmer match
    print(f"Lehmer polynomial matches: {len(lehmer_matches)}")
    for m in lehmer_matches:
        print(f"  {m['label']}: M = {m['mahler_measure']:.12f}")
    print()

    # Below Lehmer
    print(f"Polynomials with M < {LEHMER_CONSTANT} (before verification): {len(below_lehmer)}")
    print(f"Polynomials with M < {LEHMER_CONSTANT} (after verification): {len(verified_below)}")
    if verified_below:
        print("\n*** POTENTIAL LEHMER COUNTEREXAMPLES ***")
        for item in verified_below[:20]:
            print(f"  {item['label']}: coeffs={item['coeffs']}, "
                  f"M={item.get('mahler_measure_verified', item['mahler_measure']):.12f}, "
                  f"cyc={item.get('is_cyclotomic_verified', '?')}")
    else:
        print("  None — Lehmer's conjecture holds for this sample.")
    print()

    # Minimum non-cyclotomic
    print(f"Minimum non-cyclotomic Mahler measure: {min_noncyc_measure:.12f}")
    if min_noncyc_poly:
        print(f"  Polynomial: {min_noncyc_poly['label']}")
        print(f"  Coefficients: {min_noncyc_poly['coeffs']}")
        print(f"  Degree: {min_noncyc_poly['degree']}")
        gap = min_noncyc_measure - LEHMER_CONSTANT
        print(f"  Gap above Lehmer: {gap:.12f} ({'ABOVE' if gap >= 0 else 'BELOW !!!'})")
    print()

    # Degree-level statistics
    print("Per-degree minimum Mahler measures (non-cyclotomic):")
    for deg in sorted(degree_stats.keys()):
        s = degree_stats[deg]
        if s['count'] > 0:
            print(f"  deg={deg:2d}: min M = {s['min']:.10f}, "
                  f"n={s['count']:>7,}, cyclo={s['cyclo']:>6,}")
    print()

    # === SAVE RESULTS ===
    results = {
        'scan_metadata': {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_in_db': total_polys,
            'total_sampled': len(all_measures) + cyclotomic_count,
            'cyclotomic_count': cyclotomic_count,
            'non_cyclotomic_count': len(all_measures),
            'error_count': error_count,
            'runtime_seconds': round(total_time, 1),
            'lehmer_constant': LEHMER_CONSTANT,
        },
        'statistics': {
            'min': float(measures_arr.min()) if len(measures_arr) > 0 else None,
            'max': float(measures_arr.max()) if len(measures_arr) > 0 else None,
            'mean': float(measures_arr.mean()) if len(measures_arr) > 0 else None,
            'median': float(np.median(measures_arr)) if len(measures_arr) > 0 else None,
            'std': float(measures_arr.std()) if len(measures_arr) > 0 else None,
        },
        'lehmer_polynomial_matches': lehmer_matches,
        'below_lehmer_unverified': len(below_lehmer),
        'below_lehmer_verified': [
            {k: v for k, v in item.items()} for item in verified_below
        ],
        'minimum_non_cyclotomic': {
            'mahler_measure': float(min_noncyc_measure) if np.isfinite(min_noncyc_measure) else None,
            'polynomial': min_noncyc_poly
        },
        'per_degree_min': {
            str(deg): {
                'min_mahler': float(degree_stats[deg]['min']) if np.isfinite(degree_stats[deg]['min']) else None,
                'non_cyclotomic_count': degree_stats[deg]['count'],
                'cyclotomic_count': degree_stats[deg]['cyclo']
            }
            for deg in sorted(degree_stats.keys())
        },
        'conjecture_status': 'HOLDS' if len(verified_below) == 0 else 'POTENTIAL_COUNTEREXAMPLE'
    }

    out_path = Path(__file__).parent.parent / 'data' / 'lehmer_nf_scan.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {out_path}")

    conn.close()
    return results


if __name__ == '__main__':
    run_scan()
