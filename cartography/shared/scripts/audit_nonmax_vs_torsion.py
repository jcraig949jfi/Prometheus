"""
Audit: torsion primes ⊆ nonmax_primes for every non-CM EC.

Claim to test (candidate calibration anchor F009): for every EC over Q with
`cm = 0`, the set of primes dividing `torsion` (rational torsion order) is a
subset of `nonmax_primes` (primes where mod-ℓ Galois image is non-surjective).

This is a theorem fragment: rational ℓ-torsion stabilizes a line in E[ℓ],
so the mod-ℓ image is contained in the Borel and hence non-surjective onto
GL_2(F_ℓ). LMFDB's `nonmax_primes` records this; the check is data-quality.

Task: audit_nonmax_vs_torsion (claimed by Harmonia_M2_sessionD, 2026-04-17).
Output: cartography/docs/audit_nonmax_vs_torsion_results.json.
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


def prime_factors(n):
    """Trial-divide the torsion order. Torsion orders ≤ 16 by Mazur, so this is fast."""
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors


def parse_list(s):
    """Parse a Postgres-text list like '[2, 3, 5]' into a Python set of ints."""
    if s is None:
        return set()
    s = s.strip()
    if s in ('', '[]', 'None', 'NULL'):
        return set()
    # Strip brackets and split
    inner = s.strip('[]').strip()
    if not inner:
        return set()
    try:
        return {int(x.strip()) for x in inner.split(',') if x.strip()}
    except ValueError:
        return set()


def main():
    conn = psycopg2.connect(**PG, connect_timeout=10,
                            options='-c statement_timeout=120000')
    cur = conn.cursor()

    # Fetch only rows that can actually have a claim to test: cm=0 and torsion > 1.
    # Rows with torsion = 1 have no primes to check and trivially pass.
    # Rows with cm != 0 use the different "max" convention and are not in scope.
    print('[audit] fetching non-CM curves with torsion > 1...')
    cur.execute("""
        SELECT lmfdb_label, torsion::int AS tor, nonmax_primes, torsion_structure,
               cm::int AS cmflag
        FROM ec_curvedata
        WHERE cm = '0' AND torsion::int > 1
    """)
    rows = cur.fetchall()
    print(f'[audit] fetched {len(rows):,} rows')
    cur.close(); conn.close()

    n_rows = len(rows)
    n_trivial_pass = 0  # torsion=1 — skipped in SQL, count separately later
    n_pass = 0
    n_violate = 0
    violations = []  # (lmfdb_label, torsion, primes_of_torsion, nonmax_primes_set)
    per_torsion = {}  # torsion_order -> (pass, violate)

    for lbl, tor, nonmax_text, tor_struct, cmflag in rows:
        tor_primes = prime_factors(tor)
        nonmax_set = parse_list(nonmax_text)
        passed = tor_primes.issubset(nonmax_set)
        per_torsion.setdefault(tor, [0, 0])
        if passed:
            n_pass += 1
            per_torsion[tor][0] += 1
        else:
            n_violate += 1
            per_torsion[tor][1] += 1
            if len(violations) < 30:
                violations.append({
                    'lmfdb_label': lbl,
                    'torsion': tor,
                    'torsion_primes': sorted(tor_primes),
                    'nonmax_primes': sorted(nonmax_set),
                    'missing_primes': sorted(tor_primes - nonmax_set),
                    'torsion_structure': tor_struct,
                })

    # Also count torsion=1 non-CM rows (trivially pass)
    conn = psycopg2.connect(**PG, connect_timeout=10,
                            options='-c statement_timeout=30000')
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM ec_curvedata WHERE cm='0' AND torsion::int = 1")
    n_trivial_pass = cur.fetchone()[0]
    # And CM rows (out of scope) for completeness
    cur.execute("SELECT count(*) FROM ec_curvedata WHERE cm != '0'")
    n_cm_out_of_scope = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM ec_curvedata")
    n_total = cur.fetchone()[0]
    cur.close(); conn.close()

    total_non_cm_tor_gt_1 = n_pass + n_violate
    pass_rate = n_pass / total_non_cm_tor_gt_1 if total_non_cm_tor_gt_1 else 1.0
    overall_rate = (n_pass + n_trivial_pass) / (n_pass + n_violate + n_trivial_pass) if (n_pass + n_violate + n_trivial_pass) else 1.0

    result = {
        'task_id': 'audit_nonmax_vs_torsion',
        'drafted_by': 'Harmonia_M2_sessionD',
        'claim_under_test': 'For every non-CM EC, primes(torsion) ⊆ nonmax_primes.',
        'scope': {
            'total_ec_rows': int(n_total),
            'cm_zero_and_torsion_gt_1_tested': total_non_cm_tor_gt_1,
            'cm_zero_and_torsion_eq_1_trivial_pass': int(n_trivial_pass),
            'cm_nonzero_out_of_scope': int(n_cm_out_of_scope),
        },
        'results': {
            'n_pass': n_pass,
            'n_violate': n_violate,
            'pass_rate_on_tested': pass_rate,
            'pass_rate_overall_non_cm': overall_rate,
        },
        'per_torsion_breakdown': {
            str(k): {'pass': v[0], 'violate': v[1]}
            for k, v in sorted(per_torsion.items())
        },
        'first_30_violations': violations,
        'verdict': ('F009_ANCHOR_CONFIRMED' if n_violate == 0
                    else ('F009_ANCHOR_NEAR_EXACT_MINOR_VIOLATIONS' if n_violate < 100
                          else 'F009_ANCHOR_NEEDS_INVESTIGATION')),
        'interpretation': (
            'The inclusion primes(torsion) ⊆ nonmax_primes is a theorem, not a '
            'conjecture: rational ℓ-torsion stabilizes a line in E[ℓ], forcing the '
            'mod-ℓ Galois image into the Borel subgroup — therefore non-maximal. '
            'Any row violating this is a data-quality violation in LMFDB, not a '
            'counterexample to math. A 100% pass rate confirms F009 as a clean '
            'calibration anchor.'
        ),
    }

    outpath = Path('cartography/docs/audit_nonmax_vs_torsion_results.json')
    outpath.parent.mkdir(parents=True, exist_ok=True)
    with open(outpath, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f'[audit] wrote {outpath}')

    print()
    print('== RESULTS ==')
    print(f'  scope: non-CM with torsion>1 tested: {total_non_cm_tor_gt_1:,}')
    print(f'  pass: {n_pass:,} ({pass_rate*100:.4f}%)')
    print(f'  violate: {n_violate:,}')
    print(f'  verdict: {result["verdict"]}')
    print()
    print('== PER TORSION ORDER ==')
    for tor in sorted(per_torsion):
        p, v = per_torsion[tor]
        pct = (p / (p + v) * 100) if (p + v) else 0
        print(f'  torsion={tor:>3}  pass={p:>9,}  violate={v:>6,}  ({pct:.4f}%)')
    if violations:
        print()
        print('== FIRST FEW VIOLATIONS ==')
        for v in violations[:5]:
            print(f'  {v["lmfdb_label"]:>20}  tor={v["torsion"]}  '
                  f'tor_primes={v["torsion_primes"]}  '
                  f'nonmax={v["nonmax_primes"]}  missing={v["missing_primes"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
