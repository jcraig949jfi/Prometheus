"""
Report 18i — LMFDB enumeration-cutoff audit across (degree, galois_label) strata.

Parent: R18h discovered that LMFDB S3 cubic enumeration is complete through
|disc| ≤ 10^7 (bucket 6), with buckets ≥ 7 showing a 50× drop-then-recover
pattern indicative of selective augmentation. Pattern 21 candidate:
"LMFDB Enumeration Cutoff" — every (degree, galois_label) stratum has a
natural disc-bucket cutoff; any statistical claim must respect it.

This script produces a reference table of cutoffs for every (degree,
galois_label) stratum in nf_fields with enough fields to matter.

Method: pull per-bucket row count per (degree, gal) stratum. Define the
"enumeration cutoff" as the last bucket B such that n(B+1) / n(B) ≤ 1/5
(sharp drop of 5× or more to the next bucket) AND n(B) ≥ 1000.

Output: cartography/docs/report18i_lmfdb_cutoff_audit_results.json.

Author: Harmonia_M2_sessionD, 2026-04-18.
"""
import json
import sys
import io
from pathlib import Path
import psycopg2

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PG = dict(host='192.168.1.176', port=5432, dbname='lmfdb',
          user='lmfdb', password='lmfdb')
OUTPUT = Path('cartography/docs/report18i_lmfdb_cutoff_audit_results.json')


def find_cutoff(buckets_dict):
    """Given {bucket: count}, identify the enumeration cutoff.

    Returns the last bucket B such that count(B) >= 1000 AND the next
    bucket's count is < 20% of B's count (sharp 5× drop). Returns None
    if no such cutoff detected (smooth distribution).
    """
    sorted_buckets = sorted(buckets_dict.items())
    if len(sorted_buckets) < 2:
        return None
    for i, (b, n) in enumerate(sorted_buckets[:-1]):
        if n < 1000:
            continue
        next_n = sorted_buckets[i + 1][1]
        if next_n < 0.2 * n:
            return {
                'cutoff_bucket': int(b),
                'cutoff_disc_abs_bound': f'10^{b+1}',
                'n_at_cutoff': int(n),
                'n_next_bucket': int(next_n),
                'drop_ratio': float(next_n) / float(n),
            }
    return None


def main():
    conn = psycopg2.connect(**PG, connect_timeout=10,
                            options='-c statement_timeout=300000')
    cur = conn.cursor()

    # Top-N (degree, galois_label) strata by count
    cur.execute("""
        SELECT degree, galois_label, count(*) AS n
        FROM nf_fields
        WHERE class_number IS NOT NULL AND disc_abs IS NOT NULL
        GROUP BY degree, galois_label
        HAVING count(*) >= 1000
        ORDER BY count(*) DESC
        LIMIT 30
    """)
    strata = [(row[0], row[1], row[2]) for row in cur.fetchall()]
    print(f'[R18i] found {len(strata)} strata with n >= 1000')

    results = []
    for degree, gal, total_n in strata:
        cur.execute("""
            SELECT floor(log(greatest(disc_abs::numeric, 1)) / log(10))::int AS bucket,
                   count(*) AS n
            FROM nf_fields
            WHERE degree = %s AND galois_label = %s
              AND class_number IS NOT NULL AND disc_abs IS NOT NULL
            GROUP BY bucket
            ORDER BY bucket
        """, (degree, gal))
        buckets = {int(r[0]): int(r[1]) for r in cur.fetchall()}
        cutoff = find_cutoff(buckets)
        results.append({
            'degree': degree,
            'galois_label': gal,
            'total_n_with_class_number': int(total_n),
            'buckets': buckets,
            'cutoff_detected': cutoff,
        })

    cur.close(); conn.close()

    # Sort results for output
    results.sort(key=lambda r: (int(r['degree']), r['galois_label']))

    report = {
        'task': 'report18i_lmfdb_cutoff_audit',
        'parent': 'report18h_s3_cubic_bst',
        'drafted_by': 'Harmonia_M2_sessionD',
        'date': '2026-04-18',
        'purpose': (
            'Enumerate LMFDB nf_fields completeness cutoff per (degree, galois_label) '
            'stratum. Pattern 21 candidate.'
        ),
        'method': (
            'Per stratum, pull per-bucket row count. Cutoff = last bucket B with n >= 1000 '
            'and n(B+1)/n(B) < 0.2 (sharp 5× drop to next bucket).'
        ),
        'strata': results,
        'cutoff_table': [
            {
                'degree': r['degree'],
                'galois_label': r['galois_label'],
                'total_n': r['total_n_with_class_number'],
                'cutoff_bucket': r['cutoff_detected']['cutoff_bucket'] if r['cutoff_detected'] else None,
                'cutoff_disc_bound': r['cutoff_detected']['cutoff_disc_abs_bound'] if r['cutoff_detected'] else None,
                'drop_ratio': r['cutoff_detected']['drop_ratio'] if r['cutoff_detected'] else None,
                'has_sharp_cutoff': r['cutoff_detected'] is not None,
            }
            for r in results
        ],
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f'[R18i] wrote {OUTPUT}')
    print()

    print('== LMFDB ENUMERATION CUTOFF REFERENCE TABLE ==')
    print(f'{"degree":>6} {"galois":>8} {"total_n":>12} {"cutoff_bucket":>14} '
          f'{"disc_bound":>12} {"drop_ratio":>12}')
    for row in report['cutoff_table']:
        cb = row['cutoff_bucket']
        if cb is not None:
            db = row['cutoff_disc_bound']; dr = row['drop_ratio']
            print(f"{row['degree']:>6} {row['galois_label']:>8} {row['total_n']:>12,} "
                  f"{cb:>14} {db:>12} {dr:>+12.4f}")
        else:
            print(f"{row['degree']:>6} {row['galois_label']:>8} {row['total_n']:>12,} "
                  f"{'smooth':>14} {'—':>12} {'—':>12}")
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
