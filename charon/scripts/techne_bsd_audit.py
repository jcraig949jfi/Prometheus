"""Techne BSD consistency audit (Techne's ask, 1776892951935-0).

For rank-0 Sha>1 curves from LMFDB:
  1. Compute |Sha_an| via Techne TOOL_ANALYTIC_SHA (BSD formula)
  2. Compute dim Sel_2 via Techne TOOL_SELMER_RANK (2-descent)
  3. Verify |Sha_an| (rounded) matches LMFDB stored sha
  4. Verify dim Sel_2 == rank + dim Sha[2] + dim E(Q)[2]

Flags:
  - |Sha_an| - nearest_int > 0.1 : numerical-precision or BSD-inconsistency
  - LMFDB sha != rounded(|Sha_an|) : BSD inconsistency
  - dim Sel_2 != rank + dim Sha[2] + dim E[2] : Selmer structural violation
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
import psycopg2
from techne.lib.analytic_sha import analytic_sha
from techne.lib.selmer_rank import selmer_2_data

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')
N_SAMPLE = 5000
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'techne_bsd_audit.json')


def parse_ainvs(s):
    return [int(float(x.strip())) for x in s.strip('[]{}').split(',')]


def dim_F2_sha(sha_int):
    """log_2 of 2-part of Sha. For Sha = 2^a * odd, dim_F2 Sha[2] = a."""
    if sha_int <= 0: return 0
    a = 0
    while sha_int % 2 == 0:
        sha_int //= 2
        a += 1
    return a


def main():
    t0 = time.time()
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    print(f'Sampling {N_SAMPLE} rank-0 Sha>1 curves...', flush=True)
    cur.execute("""
        SELECT lmfdb_label, ainvs, sha, torsion, conductor
        FROM ec_curvedata
        WHERE rank = '0'
          AND sha::int > 1
          AND ainvs IS NOT NULL
        ORDER BY random()
        LIMIT %s
    """, (N_SAMPLE,))
    rows = cur.fetchall()
    print(f'  got {len(rows)} curves', flush=True)

    results = []
    ok_sha = 0
    mismatch_sha = 0
    large_dev = 0
    ok_selmer = 0
    mismatch_selmer = 0
    failures = 0

    tc = time.time()
    for i, (label, ainvs_s, sha_lmfdb, tors_lmfdb, cond) in enumerate(rows):
        try:
            ainvs = parse_ainvs(ainvs_s)
            sha_lmfdb = int(float(sha_lmfdb))
            asha = analytic_sha(ainvs)
            sha_an = asha['value']
            sha_rounded = asha['rounded']
            deviation = abs(sha_an - sha_rounded)

            sel_data = selmer_2_data(ainvs, effort=1)
            dim_sel2 = sel_data['dim_sel_2']
            dim_E2 = sel_data['dim_E2']
            rank_proved = sel_data['rank_proved']
            r_lo = sel_data['rank_lo']
            # expected dim Sel_2 = rank (0) + dim Sha[2] + dim E[2]
            expected_sel2 = r_lo + dim_F2_sha(sha_lmfdb) + dim_E2

            sha_match = (sha_rounded == sha_lmfdb)
            sel_match = (dim_sel2 == expected_sel2) and rank_proved

            if sha_match: ok_sha += 1
            else: mismatch_sha += 1
            if deviation > 0.1: large_dev += 1
            if sel_match: ok_selmer += 1
            elif rank_proved: mismatch_selmer += 1

            results.append({
                'label': label,
                'sha_lmfdb': sha_lmfdb,
                'sha_an_value': sha_an,
                'sha_an_rounded': sha_rounded,
                'sha_deviation': deviation,
                'sha_match': sha_match,
                'dim_sel2': dim_sel2,
                'dim_E2': dim_E2,
                'rank_pari_lo': r_lo,
                'rank_proved_by_pari': rank_proved,
                'expected_dim_sel2': expected_sel2,
                'sel2_match': sel_match,
            })
        except Exception as e:
            failures += 1
            if failures < 5:
                print(f'  fail {label}: {e}', flush=True)

        if (i + 1) % 500 == 0:
            dt = time.time() - tc
            rate = (i + 1) / dt
            eta = (len(rows) - i - 1) / rate
            print(f'  {i+1}/{len(rows)}  rate {rate:.1f}/s  eta {eta:.0f}s  sha_ok={ok_sha} sha_mis={mismatch_sha} large_dev={large_dev}', flush=True)

    n = len(results)
    print(f'\nDone: {n} / {len(rows)} (failures={failures}) in {time.time()-tc:.1f}s')
    print(f'Sha_an matches LMFDB sha: {ok_sha}/{n} ({100*ok_sha/max(n,1):.2f}%)')
    print(f'Large deviation (|dev|>0.1): {large_dev}/{n}')
    print(f'Sel_2 match expected (rank + sha[2] + E[2]): {ok_selmer}/{n} ({100*ok_selmer/max(n,1):.2f}%)')
    print(f'Selmer mismatches (rank proved): {mismatch_selmer}')

    # Deviation distribution
    devs = np.array([r['sha_deviation'] for r in results])
    print(f'\nSha_an deviation from integer — percentiles:')
    for p in [50, 90, 99, 99.9]:
        print(f'  p{p}: {np.percentile(devs, p):.3e}')
    print(f'  max: {devs.max():.3e}')

    # Mismatch details
    mismatches = [r for r in results if not r['sha_match']][:20]
    if mismatches:
        print(f'\nSample Sha mismatches (showing up to 20):')
        for m in mismatches:
            print(f'  {m["label"]}: LMFDB sha={m["sha_lmfdb"]}  analytic={m["sha_an_rounded"]} (value={m["sha_an_value"]:.4f})')

    out = {
        'meta': {
            'protocol': 'BSD consistency audit (Sha_an vs LMFDB + Sel_2 vs predicted)',
            'n_sampled': len(rows),
            'n_computed': n,
            'n_failures': failures,
            'elapsed_sec': time.time() - t0,
        },
        'summary': {
            'sha_match_count': ok_sha,
            'sha_mismatch_count': mismatch_sha,
            'large_dev_count': large_dev,
            'sel2_match_count': ok_selmer,
            'sel2_mismatch_count': mismatch_selmer,
        },
        'deviation_percentiles': {
            f'p{p}': float(np.percentile(devs, p)) for p in [50, 90, 99, 99.9]
        },
        'deviation_max': float(devs.max()),
        'sample_mismatches': mismatches[:20],
        'per_curve': results[:2000],  # truncate for size
    }
    with open(OUT, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
