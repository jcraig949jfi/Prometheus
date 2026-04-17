"""Exploration 4: Lehmer scan on the 2.4M nf_fields now in local Postgres."""
import sys, io, time
import numpy as np
import psycopg2
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("EXPLORATION 4: LEHMER SCAN — 2.4M local nf_fields")
print("=" * 70)

LEHMER_BOUND = 1.17628081825991

def mahler_measure(coeffs):
    if len(coeffs) < 2:
        return None
    poly = [float(c) for c in reversed(coeffs)]
    if abs(poly[0]) < 1e-15:
        return None
    try:
        roots = np.roots(poly)
        leading = abs(poly[0])
        product = float(np.prod([max(1.0, abs(r)) for r in roots]))
        return leading * product
    except:
        return None

# Check where nf_fields lives locally
for dbname in ['prometheus_fire', 'prometheus_sci', 'lmfdb']:
    try:
        conn = psycopg2.connect(host='192.168.1.176', port=5432, dbname=dbname,
                                user='postgres', password='prometheus')
        cur = conn.cursor()
        cur.execute("""
        SELECT table_schema, table_name FROM information_schema.tables
        WHERE table_name LIKE '%nf_field%' OR table_name LIKE '%number_field%'
        """)
        for s, t in cur.fetchall():
            print(f"  Found {dbname}.{s}.{t}")
        cur.close(); conn.close()
    except Exception as e:
        print(f"  {dbname}: {e}")

# Try the migration target
try:
    conn = psycopg2.connect(host='192.168.1.176', port=5432, dbname='lmfdb',
                            user='postgres', password='prometheus')
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM nf_fields")
    cnt = cur.fetchone()[0]
    print(f"\nlocal lmfdb.nf_fields: {cnt:,} rows")

    # Min Mahler per degree
    best_per_degree = {}

    for degree in range(2, 25):
        t0 = time.time()
        cur.execute("""
        SELECT label, coeffs, disc_abs::numeric
        FROM nf_fields
        WHERE degree = %s AND coeffs IS NOT NULL
        ORDER BY disc_abs::numeric ASC
        LIMIT 5000
        """, (str(degree),))
        rows = cur.fetchall()
        elapsed = time.time() - t0

        if not rows:
            continue

        measures = []
        for label, coeffs_raw, disc in rows:
            try:
                coeffs = [float(c) for c in coeffs_raw] if isinstance(coeffs_raw, list) else \
                         [float(c) for c in str(coeffs_raw).strip('{}').split(',')]
            except:
                continue
            mm = mahler_measure(coeffs)
            if mm is not None and mm > 1.0001:
                measures.append((mm, label, disc))

        if measures:
            measures.sort()
            m, lbl, d = measures[0]
            marker = ""
            if m < LEHMER_BOUND:
                marker = " *** BELOW LEHMER ***"
            elif m < LEHMER_BOUND * 1.01:
                marker = " << VERY CLOSE"
            print(f"  deg {degree:>2}: {len(measures):>4} non-trivial, min M={m:.8f} [{lbl}]{marker}  [{elapsed:.1f}s]")
            best_per_degree[degree] = (m, lbl, d)

    # Global summary vs yesterday's 90K scan
    print("\n=== VS YESTERDAY (90K sample via devmirror) ===")
    print(f"Yesterday min (degree 12): M=1.22778556")
    print(f"Yesterday Lehmer-poly rediscovery (degree 20): M=1.17628082")

    all_below_yesterday = [(m, l, d, deg) for deg, (m, l, d) in best_per_degree.items()
                           if m < 1.2278]
    if all_below_yesterday:
        all_below_yesterday.sort()
        print(f"\nNEW polynomials below yesterday's best (M<1.228):")
        for m, l, d, deg in all_below_yesterday[:10]:
            print(f"  deg={deg} {l}: M={m:.10f}")
    else:
        print("\nNo improvements below yesterday's minimum.")

    cur.close(); conn.close()
except Exception as e:
    print(f"Error: {e}")
    print("Trying devmirror instead...")
    conn = psycopg2.connect(host='devmirror.lmfdb.xyz', port=5432, dbname='lmfdb',
                            user='lmfdb', password='lmfdb')
    cur = conn.cursor()
    # Same scan but remote
    for degree in range(2, 25):
        t0 = time.time()
        cur.execute("""
        SELECT label, coeffs FROM nf_fields
        WHERE degree = %s ORDER BY disc_abs::numeric ASC LIMIT 5000
        """, (degree,))
        rows = cur.fetchall()
        measures = []
        for label, coeffs_raw in rows:
            try:
                coeffs = [float(c) for c in coeffs_raw]
            except:
                continue
            mm = mahler_measure(coeffs)
            if mm is not None and mm > 1.0001:
                measures.append((mm, label))
        if measures:
            measures.sort()
            m, lbl = measures[0]
            marker = ""
            if m < LEHMER_BOUND:
                marker = " *** BELOW ***"
            elif m < LEHMER_BOUND * 1.01:
                marker = " << VERY CLOSE"
            print(f"  deg {degree:>2}: min M={m:.8f} [{lbl}]{marker}  [{time.time()-t0:.1f}s]")
    cur.close(); conn.close()

print("\nEXPLORATION 4 COMPLETE")
