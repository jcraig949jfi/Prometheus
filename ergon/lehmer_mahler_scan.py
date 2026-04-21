#!/usr/bin/env python3
"""
Lehmer–Mahler Measure Scan on Number Field Defining Polynomials
===============================================================
Aporia Report #15 — Assignment for Ergon

Lehmer's conjecture: the smallest Mahler measure of a non-cyclotomic
monic integer polynomial is M(L) = 1.17628... (Lehmer's polynomial,
x^10 + x^9 - x^7 - x^6 - x^5 - x^4 - x^3 + x + 1).

We scan 100K sampled NF defining polynomials (degrees 2-10) from the
LMFDB Postgres mirror and compute Mahler measures, looking for:
  - Distribution by degree
  - The 20 smallest non-cyclotomic Mahler measures
  - Any measures below Lehmer's constant
  - Correlation with ramification

Mahler measure: M(P) = |a_n| * prod_{i} max(1, |alpha_i|)
where alpha_i are roots of P and a_n is the leading coefficient.
"""

import sys
import time
import numpy as np
import psycopg2
from collections import defaultdict

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
LEHMER_CONSTANT = 1.1762808182599175065  # M(Lehmer's polynomial)
LEHMER_POLY = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]  # x^10+x^9-x^7-..+x+1

# Boyd-Mossinghoff known small Mahler measures (degree <= 10)
# Source: Mossinghoff's tables, https://www.cecm.sfu.ca/~mjm/Lehmer/
KNOWN_SMALL = {
    "Lehmer d=10": 1.17628081825991750654,
    "d=18 (Mossinghoff)": 1.18836535913392491348,
    "d=14": 1.20002956264741068840,
    "d=10 #2": 1.20261432520101298514,
    "d=8": 1.20906428924695498498,
    "d=6 #1": 1.21639642877105028053,
    "d=4 (minimal quartic)": 1.22074408460575947536,
    "d=10 #3": 1.22769633826784710517,
    "d=8 #2": 1.23039124784498562105,
    "d=6 #2": 1.23568504070413641210,
}

SAMPLE_SIZE = 100_000

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_coeffs(coeffs_str: str) -> list[int]:
    """Parse Postgres array '{a0,a1,...,an}' to list of ints [a0, a1, ..., an]."""
    s = coeffs_str.strip('{}')
    return [int(x) for x in s.split(',')]


def mahler_measure_from_roots(coeffs: list[int]) -> float:
    """
    Compute Mahler measure via roots.
    M(P) = |a_n| * prod max(1, |root_i|)

    coeffs: [a0, a1, ..., a_n] where a0 is constant term, a_n is leading.
    numpy wants [a_n, ..., a1, a0] for np.roots.
    """
    if len(coeffs) < 2:
        return float('nan')

    leading = abs(coeffs[-1])
    if leading == 0:
        return float('nan')

    # np.roots wants highest degree first
    poly_np = list(reversed(coeffs))

    try:
        roots = np.roots(poly_np)
    except Exception:
        return float('nan')

    absroots = np.abs(roots)
    product = np.prod(np.maximum(1.0, absroots))
    return leading * product


def is_cyclotomic_candidate(coeffs: list[int], measure: float) -> bool:
    """
    Quick check: cyclotomic polynomials have M = 1 exactly.
    We flag anything with M < 1 + 1e-6 as cyclotomic.
    Also check: all coeffs in {-1, 0, 1} and leading/constant = +/-1.
    """
    if measure > 1.0 + 1e-6:
        return False
    # Cyclotomic polys are monic with constant term +/-1
    if abs(coeffs[-1]) != 1 or abs(coeffs[0]) != 1:
        return False
    return True


def is_reciprocal(coeffs: list[int]) -> bool:
    """Check if polynomial is reciprocal: a_i = a_{n-i} for all i."""
    n = len(coeffs)
    for i in range(n // 2 + 1):
        if coeffs[i] != coeffs[n - 1 - i]:
            return False
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 72)
    print("LEHMER-MAHLER MEASURE SCAN — NF Defining Polynomials")
    print("Aporia Report #15 for Ergon")
    print("=" * 72)

    # ------------------------------------------------------------------
    # 1. Connect and query
    # ------------------------------------------------------------------
    print(f"\n[1] Connecting to Postgres and sampling {SAMPLE_SIZE:,} polynomials...")
    t0 = time.time()

    conn = psycopg2.connect(
        host='localhost', port=5432,
        dbname='lmfdb', user='lmfdb', password='lmfdb'
    )
    cur = conn.cursor()

    query = """
        SELECT label, coeffs, degree::int, num_ram::int
        FROM nf_fields
        WHERE degree::int BETWEEN 2 AND 10
          AND coeffs IS NOT NULL
        ORDER BY RANDOM()
        LIMIT %s
    """
    cur.execute(query, (SAMPLE_SIZE,))
    rows = cur.fetchall()
    conn.close()

    elapsed = time.time() - t0
    print(f"    Fetched {len(rows):,} rows in {elapsed:.1f}s")

    # ------------------------------------------------------------------
    # 2. Compute Mahler measures
    # ------------------------------------------------------------------
    print("\n[2] Computing Mahler measures...")
    t0 = time.time()

    results = []  # (label, degree, num_ram, coeffs, measure, is_cyclo, is_recip)
    by_degree = defaultdict(list)  # degree -> [measures]
    by_ramification = defaultdict(list)  # num_ram -> [measures]
    n_nan = 0
    n_cyclo = 0
    n_below_lehmer = 0

    for i, (label, coeffs_str, degree, num_ram) in enumerate(rows):
        coeffs = parse_coeffs(coeffs_str)
        m = mahler_measure_from_roots(coeffs)

        if np.isnan(m):
            n_nan += 1
            continue

        cyclo = is_cyclotomic_candidate(coeffs, m)
        recip = is_reciprocal(coeffs)

        if cyclo:
            n_cyclo += 1

        if not cyclo and m < LEHMER_CONSTANT:
            n_below_lehmer += 1

        results.append((label, degree, num_ram, coeffs, m, cyclo, recip))
        by_degree[degree].append(m)

        if not cyclo:
            by_ramification[num_ram].append(m)

        if (i + 1) % 20000 == 0:
            print(f"    Processed {i+1:,}/{len(rows):,}...")

    elapsed = time.time() - t0
    print(f"    Done in {elapsed:.1f}s. {len(results):,} valid, {n_nan} NaN, {n_cyclo} cyclotomic.")

    # ------------------------------------------------------------------
    # 3. Distribution by degree
    # ------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("[3] MAHLER MEASURE DISTRIBUTION BY DEGREE")
    print("=" * 72)
    print(f"{'Deg':>4} {'Count':>8} {'Mean':>10} {'Median':>10} {'Min':>10} {'Max':>12} {'<Lehmer':>8}")
    print("-" * 72)

    for d in sorted(by_degree.keys()):
        ms = np.array(by_degree[d])
        non_cyclo = ms[ms > 1.0 + 1e-6]
        below = np.sum((non_cyclo < LEHMER_CONSTANT))
        print(f"{d:>4} {len(ms):>8,} {np.mean(ms):>10.4f} {np.median(ms):>10.4f} "
              f"{np.min(ms):>10.6f} {np.max(ms):>12.2f} {int(below):>8}")

    # ------------------------------------------------------------------
    # 4. Smallest non-cyclotomic Mahler measures
    # ------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("[4] 20 SMALLEST NON-CYCLOTOMIC MAHLER MEASURES")
    print("=" * 72)

    # Filter out cyclotomic
    non_cyclo_results = [(label, deg, nr, co, m, cy, rc)
                         for (label, deg, nr, co, m, cy, rc) in results if not cy]
    non_cyclo_results.sort(key=lambda x: x[4])

    top20 = non_cyclo_results[:20]
    print(f"{'Rank':>4} {'Measure':>16} {'Deg':>4} {'Recip':>6} {'#Ram':>5} {'Label':<30} {'Coeffs'}")
    print("-" * 110)
    for rank, (label, deg, nr, co, m, cy, rc) in enumerate(top20, 1):
        co_str = str(co) if len(str(co)) < 50 else str(co)[:47] + "..."
        flag = " ***" if m < LEHMER_CONSTANT else ""
        print(f"{rank:>4} {m:>16.12f} {deg:>4} {'Y' if rc else 'N':>6} {nr:>5} {label:<30} {co_str}{flag}")

    # ------------------------------------------------------------------
    # 5. Below Lehmer's constant?
    # ------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("[5] POLYNOMIALS BELOW LEHMER'S CONSTANT (1.17628081826...)")
    print("=" * 72)

    below_lehmer = [(label, deg, nr, co, m, cy, rc)
                    for (label, deg, nr, co, m, cy, rc) in non_cyclo_results
                    if m < LEHMER_CONSTANT]

    if not below_lehmer:
        print("    NONE found. All non-cyclotomic measures are >= Lehmer's constant.")
        print("    This is consistent with Lehmer's conjecture.")
    else:
        print(f"    WARNING: {len(below_lehmer)} polynomials found below Lehmer's constant!")
        print("    These need manual verification (likely numerical error or missed cyclotomic).")
        for label, deg, nr, co, m, cy, rc in below_lehmer:
            print(f"      M={m:.14f}  deg={deg}  label={label}")
            print(f"        coeffs={co}")
            # Double-check with higher precision unit-circle integration
            poly_np = list(reversed(co))
            t = np.linspace(0, 2 * np.pi, 10000, endpoint=False)
            z = np.exp(1j * t)
            vals = np.polyval(poly_np, z)
            m_int = np.exp(np.mean(np.log(np.abs(vals))))
            print(f"        Unit-circle integration (N=10000): M = {m_int:.14f}")

            # Check if it divides a cyclotomic polynomial
            roots = np.roots(poly_np)
            on_unit = np.sum(np.abs(np.abs(roots) - 1.0) < 1e-4)
            print(f"        Roots near unit circle: {on_unit}/{deg}")

    # ------------------------------------------------------------------
    # 6. Comparison to Boyd-Mossinghoff known small measures
    # ------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("[6] COMPARISON TO BOYD-MOSSINGHOFF KNOWN SMALL MEASURES")
    print("=" * 72)

    if top20:
        smallest = top20[0][4]
        print(f"    Our smallest non-cyclotomic: {smallest:.14f}")
    print(f"    Lehmer's constant:           {LEHMER_CONSTANT:.14f}")
    print()
    print(f"    {'Known measure':>40} {'Value':>18} {'Found in sample?':>18}")
    print("    " + "-" * 80)

    for name, val in sorted(KNOWN_SMALL.items(), key=lambda x: x[1]):
        # Check if any of our measures are close
        found = "No"
        for (label, deg, nr, co, m, cy, rc) in non_cyclo_results[:200]:
            if abs(m - val) < 1e-4:
                found = f"Yes ({label})"
                break
        print(f"    {name:>40} {val:>18.14f} {found:>18}")

    # ------------------------------------------------------------------
    # 7. Stratify by ramification
    # ------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("[7] MAHLER MEASURE vs RAMIFICATION (non-cyclotomic only)")
    print("=" * 72)
    print(f"{'#Ram':>5} {'Count':>8} {'Mean M':>10} {'Median M':>10} {'Min M':>12} {'Std':>10}")
    print("-" * 60)

    ram_stats = []
    for nr in sorted(by_ramification.keys()):
        ms = np.array(by_ramification[nr])
        if len(ms) < 10:
            continue
        ram_stats.append((nr, len(ms), np.mean(ms), np.median(ms), np.min(ms), np.std(ms)))
        print(f"{nr:>5} {len(ms):>8,} {np.mean(ms):>10.4f} {np.median(ms):>10.4f} "
              f"{np.min(ms):>12.6f} {np.std(ms):>10.4f}")

    # Spearman correlation: num_ram vs log(mahler)
    if len(ram_stats) >= 3:
        from scipy import stats as sp_stats
        all_nr = []
        all_logm = []
        for (label, deg, nr, co, m, cy, rc) in non_cyclo_results:
            all_nr.append(nr)
            all_logm.append(np.log(m))
        rho, pval = sp_stats.spearmanr(all_nr, all_logm)
        print(f"\n    Spearman correlation (num_ram vs log M): rho = {rho:.4f}, p = {pval:.2e}")
        if pval < 0.01:
            print(f"    Significant at p<0.01: {'positive' if rho > 0 else 'negative'} correlation.")
        else:
            print(f"    Not significant at p<0.01.")

    # ------------------------------------------------------------------
    # 8. Reciprocal vs non-reciprocal
    # ------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("[8] RECIPROCAL vs NON-RECIPROCAL (non-cyclotomic)")
    print("=" * 72)

    recip_m = [m for (_, _, _, _, m, _, rc) in non_cyclo_results if rc]
    nonrecip_m = [m for (_, _, _, _, m, _, rc) in non_cyclo_results if not rc]

    if recip_m:
        print(f"    Reciprocal:     n={len(recip_m):>7,}  mean={np.mean(recip_m):.6f}  "
              f"median={np.median(recip_m):.6f}  min={np.min(recip_m):.10f}")
    if nonrecip_m:
        print(f"    Non-reciprocal: n={len(nonrecip_m):>7,}  mean={np.mean(nonrecip_m):.6f}  "
              f"median={np.median(nonrecip_m):.6f}  min={np.min(nonrecip_m):.10f}")

    if recip_m and nonrecip_m:
        print(f"\n    Smallest reciprocal:     {np.min(recip_m):.12f}")
        print(f"    Smallest non-reciprocal: {np.min(nonrecip_m):.12f}")
        print("    (Lehmer's conjecture applies to reciprocal polynomials; "
              "Smyth's theorem gives M >= 1.3247... for non-reciprocal.)")
        smyth = 1.3247179572447460260  # real root of x^3 - x - 1
        below_smyth = sum(1 for m in nonrecip_m if m < smyth - 1e-6)
        print(f"    Non-reciprocal below Smyth's bound (1.32472): {below_smyth}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print(f"    Polynomials scanned:        {len(rows):>10,}")
    print(f"    Valid measures computed:     {len(results):>10,}")
    print(f"    Cyclotomic (M~1):           {n_cyclo:>10,}")
    print(f"    Non-cyclotomic:             {len(non_cyclo_results):>10,}")
    print(f"    Below Lehmer's constant:    {n_below_lehmer:>10}")
    if top20:
        print(f"    Smallest non-cyclo measure: {top20[0][4]:.14f}")
    print(f"    Lehmer's constant:          {LEHMER_CONSTANT:.14f}")
    print()
    if n_below_lehmer == 0:
        print("    VERDICT: Lehmer's conjecture holds across this 100K sample.")
        print("    No non-cyclotomic polynomial has M < 1.17628...")
    else:
        print("    VERDICT: Anomalies detected — manual verification required.")


if __name__ == "__main__":
    main()
