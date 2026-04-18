"""
Report 18 — Cohen-Lenstra Prob(p | h) by (degree, galois_label, signature).

Task: Aporia Report 18 — Cohen-Lenstra. Assigned to sessionD per sessionA.
Question: does empirical Prob(p | h_K) match Cohen-Lenstra-Martinet-Bartel
predictions across number-field strata? If |z| < 3 at every adequate
stratum, F-anchor candidate.

Strata (21.8 M total NF rows):
  - (deg=2, gal=2T1, r2=1)  ≈ imaginary quadratic  → classical Cohen-Lenstra
  - (deg=2, gal=2T1, r2=0)  ≈ real      quadratic → classical Cohen-Lenstra
  - (deg=3, gal=3T1 C3)      ≈ cyclic cubic        → special (|G|=3 is good)
  - (deg=3, gal=3T2 S3, r2=?)  → Cohen-Martinet / Bhargava-Varma
  - (deg=4, gal=4T1 C4)      ≈ cyclic quartic
  - (deg=4, gal=4T2 V4)      ≈ biquadratic
  - (deg=4, gal=4T3 D4)       → Bartel-Lenstra
  - (deg=4, gal=4T4 A4)
  - (deg=4, gal=4T5 S4)       → Cohen-Martinet / Bhargava-Shankar
  - (deg=5, 5T1..5T5)

Primes tested: p ∈ {3, 5, 7, 11, 13} (p = 2 handled separately because
Cohen-Lenstra conjectures restrict to odd p in most formulations).

Theoretical reference:
  For imaginary quadratic: Prob(p | h) = 1 - ∏_{k=1}^∞ (1 - p^-k).
  For real      quadratic: Prob(p | h) = 1 - ∏_{k=2}^∞ (1 - p^-k).
  For Galois groups where p ∤ |G|, the Cohen-Martinet heuristic generalizes
  these. For p | |G|, the prediction is different (Cohen-Lenstra modification
  or no clean prediction).

  We encode the two classical predictions with high confidence and report
  EMPIRICAL values for the remaining strata so sessionA / Harmonia can
  compare against the specific Bartel-Lenstra / Bhargava-Varma formulas.

Output: cartography/docs/report18_cohen_lenstra_results.json.

Author: Harmonia_M2_sessionD, 2026-04-18.
"""
import json
import sys
import io
from math import sqrt, prod
from pathlib import Path
import psycopg2

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


PG = dict(host='192.168.1.176', port=5432, dbname='lmfdb',
          user='lmfdb', password='lmfdb')

PRIMES = [3, 5, 7, 11, 13]


def cl_prob_imaginary_quadratic(p, terms=200):
    """Prob(p | h) ~ 1 - ∏_{k=1}^∞ (1 - p^-k).  For imaginary quadratic
    fields (Cohen-Lenstra 1984). High convergence after k≈50."""
    eta = 1.0
    for k in range(1, terms + 1):
        eta *= (1 - p ** -k)
    return 1.0 - eta


def cl_prob_real_quadratic(p, terms=200):
    """Prob(p | h) ~ 1 - ∏_{k=2}^∞ (1 - p^-k).  For real quadratic fields."""
    eta = 1.0
    for k in range(2, terms + 1):
        eta *= (1 - p ** -k)
    return 1.0 - eta


# Reference predictions per (degree, galois_label, signature_bucket, prime).
# signature_bucket: 'complex' means r2 >= 1 (has complex places), 'real' means r2 == 0.
# Only well-established Cohen-Lenstra predictions are encoded here with
# confidence; others are None and reported as empirical-only.
def theoretical_prob(degree, galois_label, signature_bucket, p):
    """Return (theoretical_probability, confidence) or (None, 'not_encoded')."""
    # Imaginary quadratic (degree 2, r2=1 — one pair of complex embeddings)
    if degree == 2 and galois_label == '2T1' and signature_bucket == 'complex':
        return cl_prob_imaginary_quadratic(p), 'cohen_lenstra_1984'
    # Real quadratic (degree 2, r2=0)
    if degree == 2 and galois_label == '2T1' and signature_bucket == 'real':
        return cl_prob_real_quadratic(p), 'cohen_lenstra_1984'
    return None, 'not_encoded'


def parse_int(s):
    if s is None:
        return None
    try:
        return int(s)
    except (ValueError, TypeError):
        return None


def main():
    conn = psycopg2.connect(**PG, connect_timeout=10,
                            options='-c statement_timeout=300000')
    cur = conn.cursor()

    # Define strata. Each stratum is (degree, galois_label).
    # We compute signature-split counts separately.
    strata = [
        (1, '1T1'),
        (2, '2T1'),
        (3, '3T1'), (3, '3T2'),
        (4, '4T1'), (4, '4T2'), (4, '4T3'), (4, '4T4'), (4, '4T5'),
        (5, '5T1'), (5, '5T2'), (5, '5T3'), (5, '5T4'), (5, '5T5'),
    ]

    per_stratum = []
    for (deg, gal) in strata:
        print(f'[R18] computing stratum deg={deg} galois_label={gal}...')
        # One query per stratum, grouped by signature bucket (r2=0 real vs r2>=1 complex)
        # and per prime, counting how many rows have p | class_number.
        cur.execute("""
            SELECT
              CASE WHEN r2::int = 0 THEN 'real' ELSE 'complex' END AS sig_bucket,
              count(*) AS n,
              count(*) FILTER (WHERE (class_number::bigint) %% 3  = 0) AS div_3,
              count(*) FILTER (WHERE (class_number::bigint) %% 5  = 0) AS div_5,
              count(*) FILTER (WHERE (class_number::bigint) %% 7  = 0) AS div_7,
              count(*) FILTER (WHERE (class_number::bigint) %% 11 = 0) AS div_11,
              count(*) FILTER (WHERE (class_number::bigint) %% 13 = 0) AS div_13
            FROM nf_fields
            WHERE degree::int = %s
              AND galois_label = %s
              AND class_number IS NOT NULL
            GROUP BY sig_bucket
            ORDER BY sig_bucket
        """, (deg, gal))
        rows = cur.fetchall()
        for sig_bucket, n, d3, d5, d7, d11, d13 in rows:
            divs = {3: d3, 5: d5, 7: d7, 11: d11, 13: d13}
            stratum = {
                'degree': deg,
                'galois_label': gal,
                'signature_bucket': sig_bucket,
                'n_total': int(n),
                'per_prime': {},
            }
            for p in PRIMES:
                k = int(divs[p])
                emp = k / n if n > 0 else None
                theo, conf = theoretical_prob(deg, gal, sig_bucket, p)
                entry = {
                    'n_divisible': k,
                    'empirical_prob': emp,
                }
                if theo is not None:
                    se = sqrt(theo * (1 - theo) / n) if n > 0 else None
                    z = (emp - theo) / se if (emp is not None and se and se > 0) else None
                    entry.update({
                        'theoretical_prob': theo,
                        'theoretical_source': conf,
                        'se_under_null': se,
                        'z': z,
                        'matches_theory': (abs(z) < 3.0) if z is not None else None,
                    })
                stratum['per_prime'][str(p)] = entry
            per_stratum.append(stratum)

    cur.close(); conn.close()

    # Roll-up: aggregate verdict over all encoded-theory strata.
    anchor_checks = []
    for s in per_stratum:
        for p, entry in s['per_prime'].items():
            if 'theoretical_prob' in entry:
                anchor_checks.append({
                    'degree': s['degree'],
                    'galois_label': s['galois_label'],
                    'signature_bucket': s['signature_bucket'],
                    'p': int(p),
                    'n': s['n_total'],
                    'empirical': entry['empirical_prob'],
                    'theoretical': entry['theoretical_prob'],
                    'z': entry['z'],
                    'matches': entry['matches_theory'],
                })

    all_match = all(c['matches'] for c in anchor_checks if c['matches'] is not None)
    result = {
        'task': 'report18_cohen_lenstra',
        'drafted_by': 'Harmonia_M2_sessionD',
        'date': '2026-04-18',
        'claim_under_test': (
            'Empirical Prob(p | h_K) matches Cohen-Lenstra classical '
            'predictions for quadratic strata; empirical values for '
            'S3/D4/S4/etc. are reported for sessionA/Harmonia to compare '
            'against Bartel-Lenstra / Cohen-Martinet / Bhargava formulas.'
        ),
        'primes_tested': PRIMES,
        'n_strata': len(per_stratum),
        'per_stratum': per_stratum,
        'anchor_candidates': anchor_checks,
        'all_encoded_theory_match': all_match,
        'verdict': (
            'F_ANCHOR_CANDIDATE_CONFIRMED' if all_match
            else 'NEEDS_INVESTIGATION'
        ),
        'notes': [
            'Theoretical predictions encoded: imaginary quadratic + real quadratic '
            '(Cohen-Lenstra 1984). These are the highest-confidence closed-form '
            'cases; all others report empirical only.',
            'S3 (3T2), D4 (4T3), S4 (4T5) empirical values are the Bartel-Lenstra '
            '/ Cohen-Martinet / Bhargava test cases per Aporia Report 18. '
            'sessionA / Harmonia should compare against the specific formulas.',
            'p | |G| cases (p=3 for S3, p=2 for C2/V4/D4, p=2 for S4) may require '
            'the Cohen-Lenstra modification because the heuristic assumes p ∤ |G|.',
            'Signature bucketing: r2=0 → real (totally real field); r2>=1 → complex. '
            'For quadratic this gives real / imaginary as expected.',
        ],
    }

    outpath = Path('cartography/docs/report18_cohen_lenstra_results.json')
    outpath.parent.mkdir(parents=True, exist_ok=True)
    with open(outpath, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f'[R18] wrote {outpath}')

    # Console summary
    print()
    print('== ANCHOR CANDIDATES (classical Cohen-Lenstra encoded) ==')
    print(f'{"deg":>4} {"gal":>5} {"sig":>8} {"p":>4} {"n":>10} '
          f'{"emp":>8} {"theo":>8} {"z":>8} {"match":>6}')
    for c in anchor_checks:
        z_str = f'{c["z"]:>+8.2f}' if c['z'] is not None else '    —   '
        match = 'YES' if c['matches'] else 'NO' if c['matches'] is not None else '-'
        print(f'{c["degree"]:>4} {c["galois_label"]:>5} {c["signature_bucket"]:>8} '
              f'{c["p"]:>4} {c["n"]:>10,} {c["empirical"]:>8.4f} '
              f'{c["theoretical"]:>8.4f} {z_str} {match:>6}')
    print()
    print(f'Verdict: {result["verdict"]}')

    print()
    print('== EMPIRICAL VALUES (all strata) ==')
    print(f'{"deg":>4} {"gal":>5} {"sig":>8} {"n":>10} {"p=3":>7} {"p=5":>7} {"p=7":>7} {"p=11":>7} {"p=13":>7}')
    for s in per_stratum:
        row = f'{s["degree"]:>4} {s["galois_label"]:>5} {s["signature_bucket"]:>8} {s["n_total"]:>10,}'
        for p in PRIMES:
            emp = s['per_prime'][str(p)]['empirical_prob']
            row += f'  {emp:.4f}' if emp is not None else '       —'
        print(row)

    return 0


if __name__ == '__main__':
    sys.exit(main())
