#!/usr/bin/env python3
"""
F011 Residual Thread: Higher-Gap Analysis & Cross-Family Comparison

Test 1: Is the F011 deficit concentrated in gap1 only (excised ensemble / central zero repulsion)
        or uniform across gap1-gap4 (deeper compression phenomenon)?

Test 2: Does the same deficit appear in modular form L-functions (generic unfolding issue)
        or only in EC L-functions (arithmetic structure)?

Gaudin variance reference: 0.178
"""

import numpy as np
import psycopg2
import json
import sys
from collections import defaultdict

GAUDIN_VAR = 0.178

def parse_zeros(raw):
    """Parse positive_zeros from postgres (stored as text array or JSON-like)."""
    if raw is None:
        return None
    if isinstance(raw, (list, tuple)):
        return [float(z) for z in raw]
    s = str(raw).strip()
    if s in ('', '[]', '{}', 'None'):
        return None
    # Handle postgres array format {a,b,c} or JSON [a,b,c]
    s = s.replace('{', '[').replace('}', ']')
    try:
        vals = json.loads(s)
        return [float(z) for z in vals]
    except:
        return None


def compute_normalized_gaps(zeros, max_gap=4):
    """Compute gap1..gap_max normalized by per-curve mean gap."""
    if zeros is None or len(zeros) < max_gap + 1:
        return None
    zeros = sorted(zeros)[:max_gap + 1]
    gaps = [zeros[i+1] - zeros[i] for i in range(max_gap)]
    mean_gap = np.mean(gaps)
    if mean_gap <= 0:
        return None
    return [g / mean_gap for g in gaps]


def analyze_gaps(rows, label, need_conductor=True):
    """Analyze gap variances for a set of (zeros, conductor, ...) rows."""
    gap_data = defaultdict(list)  # gap_index -> list of normalized gaps
    n_used = 0
    n_skipped = 0

    for row in rows:
        zeros = parse_zeros(row[0])
        if zeros is None or len(zeros) < 5:
            n_skipped += 1
            continue
        ngaps = compute_normalized_gaps(zeros, max_gap=4)
        if ngaps is None:
            n_skipped += 1
            continue
        for i, g in enumerate(ngaps):
            gap_data[i].append(g)
        n_used += 1

    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(f"  Curves used: {n_used:,}  |  Skipped (too few zeros): {n_skipped:,}")
    print()
    print(f"  {'Gap':<8} {'N':>8} {'Mean':>8} {'Var':>8} {'Var/Gaudin':>12} {'Deficit%':>10}")
    print(f"  {'-'*56}")

    results = {}
    for i in range(4):
        arr = np.array(gap_data[i])
        if len(arr) == 0:
            print(f"  gap{i+1:<4}  {'(no data)':>8}")
            continue
        mean = np.mean(arr)
        var = np.var(arr)
        ratio = var / GAUDIN_VAR
        deficit_pct = (1.0 - ratio) * 100
        print(f"  gap{i+1:<4} {len(arr):>8,} {mean:>8.4f} {var:>8.5f} {ratio:>12.4f} {deficit_pct:>9.1f}%")
        results[f'gap{i+1}'] = {'var': var, 'ratio': ratio, 'deficit': deficit_pct, 'n': len(arr)}

    return results


def main():
    print("Connecting to LMFDB Postgres...")
    conn = psycopg2.connect(
        host='localhost', port=5432,
        dbname='lmfdb', user='lmfdb', password='lmfdb'
    )
    cur = conn.cursor()

    # ── Test 1: EC L-functions, gaps 1-4 ──
    print("\nFetching EC L-function zeros (rank=0)...")
    cur.execute("""
        SELECT l.positive_zeros, e.conductor::float, e.rank::int
        FROM ec_curvedata e
        JOIN lfunc_lfunctions l
          ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso, '.', 1)
                        || '/' || split_part(e.lmfdb_iso, '.', 2)
        WHERE e.rank::int = 0
          AND l.positive_zeros IS NOT NULL
          AND l.positive_zeros != '[]'
        LIMIT 200000
    """)
    ec_rows = cur.fetchall()
    print(f"  Fetched {len(ec_rows):,} EC rows")

    ec_results = analyze_gaps(ec_rows, "TEST 1: EC L-functions — Higher-Gap Analysis")

    # ── Test 2: Modular Form L-functions, gap1 only ──
    print("\nFetching Modular Form L-function zeros...")
    cur.execute("""
        SELECT positive_zeros, conductor::float
        FROM lfunc_lfunctions
        WHERE origin LIKE 'ModularForm/GL2/Q/holomorphic/%%'
          AND positive_zeros IS NOT NULL
          AND positive_zeros != '[]'
        LIMIT 100000
    """)
    mf_rows = cur.fetchall()
    print(f"  Fetched {len(mf_rows):,} MF rows")

    mf_results = analyze_gaps(mf_rows, "TEST 2: Modular Form L-functions — Cross-Family Comparison")

    # ── Summary ──
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  Gaudin reference variance: {GAUDIN_VAR}")
    print()

    # Test 1 verdict
    if ec_results:
        gap1_def = ec_results.get('gap1', {}).get('deficit', 0)
        other_defs = [ec_results.get(f'gap{i}', {}).get('deficit', 0) for i in range(2, 5)]
        avg_other = np.mean(other_defs) if other_defs else 0

        print(f"  TEST 1 — Gap-specificity:")
        print(f"    gap1 deficit:       {gap1_def:+.1f}%")
        print(f"    gap2-4 avg deficit: {avg_other:+.1f}%")
        if abs(gap1_def) > 2 * abs(avg_other) and abs(gap1_def) > 5:
            print(f"    VERDICT: Deficit CONCENTRATED in gap1 → excised ensemble / central zero repulsion")
        elif abs(gap1_def - avg_other) < 3:
            print(f"    VERDICT: Deficit UNIFORM across all gaps → deeper compression phenomenon")
        else:
            print(f"    VERDICT: Mixed pattern — requires further analysis")

    # Test 2 verdict
    if ec_results and mf_results:
        ec_gap1 = ec_results.get('gap1', {}).get('ratio', 1.0)
        mf_gap1 = mf_results.get('gap1', {}).get('ratio', 1.0)
        print(f"\n  TEST 2 — Cross-family:")
        print(f"    EC  gap1 var/Gaudin: {ec_gap1:.4f}")
        print(f"    MF  gap1 var/Gaudin: {mf_gap1:.4f}")
        diff = abs(ec_gap1 - mf_gap1)
        if diff < 0.05:
            print(f"    VERDICT: SAME deficit in both families → generic unfolding / normalization issue")
        else:
            print(f"    VERDICT: DIFFERENT deficit (delta={diff:.4f}) → family-specific arithmetic structure")

    print()
    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
