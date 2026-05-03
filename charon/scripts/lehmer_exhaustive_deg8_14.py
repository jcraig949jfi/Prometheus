"""Exhaustive Lehmer scan on LMFDB NF deg 8..14 (Aporia's ask).

My prior 10K-per-degree subsample missed Lehmer's own NF (10.2.1332031009.1 M=1.17628).
The true min-M on LMFDB NF corpus is Lehmer's bound at degree 10. This scan:
  1. Iterates ALL LMFDB NFs at deg in {8, 9, 10, 11, 12, 13, 14}
  2. Computes M(f) for each via techne.lib.mahler_measure
  3. Reports per-degree true min-M and bottom-20 specimens
  4. Flags any M < 1.17628 (Lehmer counterexamples — none expected)

Scale: deg 8 = 3.21M, deg 9 = 0.38M, deg 10 = 2.83M, deg 11 = 1.6K, deg 12 = 0.3M,
       deg 13 = 0.31K, deg 14 = 2.84K.
Total ~6.7M polys at ~0.1-0.2 ms/poly for degrees 8-14. Est ~20-30 min.
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
import psycopg2
from techne.lib.mahler_measure import mahler_measure

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')
DEGREES = [8, 9, 10, 11, 12, 13, 14]
LEHMER_BOUND = 1.17628081825991750654407033847403505069341580657
FETCH_BATCH = 50000
KEEP_BOTTOM = 50

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'lehmer_exhaustive_deg8_14.json')


def parse_coeffs(s):
    s = s.strip('{}[]')
    if not s: return None
    try:
        asc = [int(x.strip()) for x in s.split(',') if x.strip()]
        if len(asc) < 2: return None
        return asc[::-1]  # descending for numpy
    except ValueError:
        return None


def scan_degree(cur, deg):
    """Streaming M(f) scan — keep only bottom KEEP_BOTTOM specimens."""
    from heapq import heappush, heappushpop
    # min-heap keyed by (-M, ...) so we keep smallest M
    top = []  # list of (M, label, disc)

    t_fetch = time.time()
    cur.execute("""
        SELECT label, disc_abs, coeffs FROM nf_fields WHERE degree = %s AND coeffs IS NOT NULL
    """, (str(deg),))
    print(f'  [deg={deg}] streaming fetch...', flush=True)

    n = 0
    n_bad_parse = 0
    m_below_lehmer = 0
    t_start = time.time()
    while True:
        batch = cur.fetchmany(FETCH_BATCH)
        if not batch: break
        for label, disc_s, coeffs_s in batch:
            c = parse_coeffs(coeffs_s)
            if c is None or len(c) != deg + 1:
                n_bad_parse += 1
                continue
            try:
                m = mahler_measure(c)
                if not np.isfinite(m) or m < 0.0:
                    continue
                m = max(m, 1.0)
            except Exception:
                continue
            disc = float(disc_s) if disc_s else 0.0
            n += 1
            if m < LEHMER_BOUND:
                m_below_lehmer += 1
            if len(top) < KEEP_BOTTOM:
                top.append((m, label, disc))
            else:
                # Keep bottom KEEP_BOTTOM: if new m < current max in top, replace
                if m < max(x[0] for x in top):
                    top.append((m, label, disc))
                    top.sort()
                    top = top[:KEEP_BOTTOM]
        if n and n % 500000 == 0:
            dt = time.time() - t_start
            print(f'    [deg={deg}] {n:,} computed ({n/dt:.0f}/s, min M so far = {min(x[0] for x in top):.6f})', flush=True)

    top.sort()
    return {
        'degree': deg,
        'n_computed': n,
        'n_bad_parse': n_bad_parse,
        'n_below_lehmer_bound': m_below_lehmer,
        'min_M_all': float(top[0][0]) if top else None,
        'min_M_non_cyclotomic': next((float(m) for m, _, _ in top if m > 1.001), None),
        'bottom_50': [
            {'M': float(m), 'label': lab, 'disc_abs': d}
            for m, lab, d in top
        ],
        'elapsed_sec': time.time() - t_start,
    }


def main():
    t0 = time.time()
    conn = psycopg2.connect(**DB)
    cur = conn.cursor('lehmer_stream')  # server-side cursor for streaming
    out = {'meta': {'started': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                    'degrees': DEGREES, 'keep_bottom': KEEP_BOTTOM,
                    'lehmer_bound': LEHMER_BOUND},
           'per_degree': {}}
    for d in DEGREES:
        cur2 = conn.cursor(f'lehmer_d{d}')
        print(f'\n[deg={d}]', flush=True)
        r = scan_degree(cur2, d)
        out['per_degree'][str(d)] = r
        cur2.close()
        print(f'  done: n={r["n_computed"]:,}  min={r["min_M_all"]:.6f}  '
              f'min_non_cyc={r["min_M_non_cyclotomic"] if r["min_M_non_cyclotomic"] else "N/A"}  '
              f'below_lehmer={r["n_below_lehmer_bound"]}  elapsed={r["elapsed_sec"]:.0f}s', flush=True)

    out['meta']['elapsed_sec'] = time.time() - t0
    out['meta']['finished'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'\n[saved] {OUT}')
    print(f'Total elapsed: {out["meta"]["elapsed_sec"]:.0f}s')


if __name__ == '__main__':
    main()
