"""
P1.1 Mahler Measure Bridge Test — Charon
========================================
Compute Mahler measures of Alexander polynomials for all 2,977 knots,
then match against L(E,2) values from 3.8M elliptic curves in Postgres.

Boyd's conjecture (proven in many cases by Rodriguez-Villegas):
  For certain knot polynomials, m(Delta) = r * L'(E, 0) / (2*pi)
  where m is the logarithmic Mahler measure.

We test the weaker version: do any knot Mahler measures match EC L-values
at high numerical precision?

Standing order: trust nothing. Battery overrides narrative.
"""
import json
import numpy as np
from pathlib import Path
import time

# ── Step 1: Compute Mahler measures of Alexander polynomials ──

def mahler_measure(coeffs):
    """
    Compute the (logarithmic) Mahler measure of a polynomial with given coefficients.

    m(P) = log|a_n| + sum_{|z_i|>1} log|z_i|

    where z_i are the roots and a_n is the leading coefficient.
    Equivalently: m(P) = integral_0^1 log|P(e^{2*pi*i*t})| dt

    For Alexander polynomials, we return both log Mahler measure and
    the exponential Mahler measure M(P) = exp(m(P)).
    """
    if not coeffs or all(c == 0 for c in coeffs):
        return None, None

    p = np.polynomial.polynomial.Polynomial(coeffs)
    roots = p.roots()

    # Mahler measure: |leading coeff| * product of max(1, |root|)
    leading = abs(coeffs[-1])
    if leading == 0:
        return None, None

    log_mahler = np.log(leading)
    for r in roots:
        abs_r = abs(r)
        if abs_r > 1:
            log_mahler += np.log(abs_r)

    return log_mahler, np.exp(log_mahler)


def mahler_measure_numerical(coeffs, n_points=10000):
    """
    Compute Mahler measure via numerical integration on unit circle.
    More robust for ill-conditioned polynomials.

    m(P) = integral_0^1 log|P(e^{2*pi*i*t})| dt
    """
    if not coeffs or all(c == 0 for c in coeffs):
        return None, None

    t = np.linspace(0, 1, n_points, endpoint=False)
    z = np.exp(2j * np.pi * t)

    # Evaluate polynomial at points on unit circle
    p_vals = np.zeros(n_points, dtype=complex)
    for i, c in enumerate(coeffs):
        p_vals += c * z**i

    abs_vals = np.abs(p_vals)
    # Avoid log(0)
    abs_vals = np.maximum(abs_vals, 1e-300)

    log_mahler = np.mean(np.log(abs_vals))
    return log_mahler, np.exp(log_mahler)


def compute_all_mahler_measures(knots_file):
    """Compute Mahler measures for all knots with Alexander data."""
    with open(knots_file) as f:
        data = json.load(f)

    knots = data['knots']
    results = []

    for k in knots:
        coeffs = k.get('alex_coeffs')
        if not coeffs:
            continue

        # Root-based computation
        log_m_root, M_root = mahler_measure(coeffs)
        # Numerical integration (for cross-validation)
        log_m_num, M_num = mahler_measure_numerical(coeffs)

        if log_m_root is not None and log_m_num is not None:
            results.append({
                'name': k['name'],
                'determinant': k.get('determinant'),
                'crossing_number': k.get('crossing_number'),
                'alex_coeffs': coeffs,
                'log_mahler_root': float(log_m_root),
                'mahler_root': float(M_root),
                'log_mahler_num': float(log_m_num),
                'mahler_num': float(M_num),
                'method_agreement': bool(abs(log_m_root - log_m_num) < 1e-4),
            })

    return results


# ── Step 2: Get EC L-values from Postgres ──

def get_ec_lvalues():
    """
    Query L-function special values for elliptic curves.
    We need L(E,s) values — specifically L(E,1) for rank-0 curves
    and L'(E,1) for rank-1 curves.

    Boyd's conjecture relates Mahler measures to L(E,2) = L'(E,0)/(2*pi),
    but we also check L(E,1) and derived quantities.
    """
    import psycopg2

    conn = psycopg2.connect(
        host='localhost', port=5432,
        dbname='lmfdb', user='lmfdb', password='lmfdb'
    )
    cur = conn.cursor()

    # Check what columns are available
    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'ec_curvedata'
        ORDER BY ordinal_position
    """)
    columns = [r[0] for r in cur.fetchall()]
    print(f"EC columns: {columns}")

    # Also check lfunc_lfunctions columns
    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'lfunc_lfunctions'
        ORDER BY ordinal_position
    """)
    lf_columns = [r[0] for r in cur.fetchall()]
    print(f"L-func columns: {lf_columns}")

    cur.close()
    conn.close()
    return columns, lf_columns


# ── Step 3: Precision matching ──

def match_mahler_to_lvalues(mahler_results, lvalues, tolerances=[1e-6, 1e-4, 1e-3]):
    """
    For each Mahler measure, check if it matches any EC L-value
    at various precision levels.

    We check:
    - Direct match: m(Delta) ~= L-value
    - Rational multiple: m(Delta) / L-value is close to a small rational
    - Pi-scaled: m(Delta) * (2*pi) ~= L-value (Boyd normalization)
    """
    matches = {tol: [] for tol in tolerances}

    mahler_values = np.array([r['mahler_root'] for r in mahler_results])
    log_mahler_values = np.array([r['log_mahler_root'] for r in mahler_results])

    for tol in tolerances:
        for lv_info in lvalues:
            lv = lv_info['value']
            if lv <= 0:
                continue

            # Direct match
            diffs = np.abs(mahler_values - lv)
            hits = np.where(diffs < tol)[0]
            for idx in hits:
                matches[tol].append({
                    'knot': mahler_results[idx]['name'],
                    'mahler': mahler_results[idx]['mahler_root'],
                    'lvalue': lv,
                    'ec': lv_info['label'],
                    'match_type': 'direct',
                    'diff': float(diffs[idx]),
                })

            # Log Mahler match (= L'/2pi for Boyd)
            log_diffs = np.abs(log_mahler_values - lv)
            hits = np.where(log_diffs < tol)[0]
            for idx in hits:
                matches[tol].append({
                    'knot': mahler_results[idx]['name'],
                    'log_mahler': mahler_results[idx]['log_mahler_root'],
                    'lvalue': lv,
                    'ec': lv_info['label'],
                    'match_type': 'log_mahler',
                    'diff': float(log_diffs[idx]),
                })

    return matches


# ── Main ──

if __name__ == '__main__':
    project_root = Path(__file__).parent.parent.parent
    knots_file = project_root / 'cartography' / 'knots' / 'data' / 'knots.json'

    print("=" * 60)
    print("P1.1 MAHLER MEASURE BRIDGE TEST")
    print("Charon — 2026-04-15")
    print("=" * 60)

    # Step 1: Compute Mahler measures
    print("\n[1/3] Computing Mahler measures for 2977 knots...")
    t0 = time.time()
    results = compute_all_mahler_measures(knots_file)
    t1 = time.time()
    print(f"  Computed: {len(results)} knots in {t1-t0:.1f}s")

    # Cross-validation
    agree = sum(1 for r in results if r['method_agreement'])
    print(f"  Method agreement (root vs numerical): {agree}/{len(results)} ({100*agree/len(results):.1f}%)")

    # Distribution
    mahler_vals = [r['mahler_root'] for r in results]
    log_mahler_vals = [r['log_mahler_root'] for r in results]
    print(f"  Mahler measure range: [{min(mahler_vals):.6f}, {max(mahler_vals):.6f}]")
    print(f"  Log Mahler range: [{min(log_mahler_vals):.6f}, {max(log_mahler_vals):.6f}]")
    print(f"  Mean Mahler: {np.mean(mahler_vals):.6f}")
    print(f"  Median Mahler: {np.median(mahler_vals):.6f}")

    # Save Mahler measures
    out_file = project_root / 'charon' / 'data' / 'mahler_measures.json'
    with open(out_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  Saved to {out_file}")

    # Step 2: Check EC data availability
    print("\n[2/3] Checking EC L-value data in Postgres...")
    try:
        ec_cols, lf_cols = get_ec_lvalues()
    except Exception as e:
        print(f"  Postgres error: {e}")
        print("  Will proceed with DuckDB fallback or report what we have.")
        ec_cols, lf_cols = [], []

    # Step 3: Summary statistics for the Mahler measures themselves
    print("\n[3/3] Mahler measure statistics...")

    # Known values to check against
    # Figure-8 knot (4_1): Alexander = 1 - t + t^2, Mahler = (3 + sqrt(5))/2 = golden ratio
    # Actually m(1-t+t^2) = 0 because all roots on unit circle
    for r in results:
        if r['name'] in ['4_1', '3_1']:
            print(f"  {r['name']}: M = {r['mahler_root']:.10f}, log(M) = {r['log_mahler_root']:.10f}")

    # Histogram of Mahler measures
    hist, edges = np.histogram(mahler_vals, bins=20)
    print(f"\n  Mahler measure distribution:")
    for i in range(len(hist)):
        bar = '#' * min(hist[i], 60)
        print(f"    [{edges[i]:.2f}, {edges[i+1]:.2f}): {hist[i]:4d} {bar}")

    # Count of M = 1 (all roots on unit circle — reciprocal polynomials)
    trivial = sum(1 for m in mahler_vals if abs(m - 1.0) < 1e-10)
    print(f"\n  Trivial (M=1, all roots on unit circle): {trivial}")
    print(f"  Non-trivial: {len(results) - trivial}")

    # Lehmer's constant check
    lehmer = 1.17628081825991
    near_lehmer = sum(1 for m in mahler_vals if 1.0 < m < lehmer + 0.01)
    below_lehmer = sum(1 for m in mahler_vals if 1.0 < m < lehmer)
    print(f"  Below Lehmer's constant ({lehmer:.6f}): {below_lehmer}")
    print(f"  Near Lehmer's constant (within 0.01): {near_lehmer}")

    print("\n" + "=" * 60)
    print("DONE. Next: match against EC L-values in Postgres.")
    print("=" * 60)
