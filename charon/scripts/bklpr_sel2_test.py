"""BKLPR Sel_2 distribution test on 10K random rank-0 EC (Aporia ask).

BKLPR / Poonen-Rains predicts the distribution of dim_F2 Sel_2 for "random" EC
(ordered by conductor). For rank-0 curves specifically:
    Sel_2 = dim_F2 Sha[2] + dim_F2 E(Q)[2]

Reference predicted probabilities (Poonen-Rains, all ranks pooled at p=2):
    P(Sel_2 = 0) = prod_{k>=1}(1+2^{-k})^{-1}               approx 0.2097
    P(Sel_2 = 1) = 2 * prod_{k>=1}(1+2^{-k})^{-1} * 2^{-1}  approx 0.5244
    P(Sel_2 = 2) = (8/3) * prod ... * 2^{-3}                approx 0.2424
    P(Sel_2 = 3)                                              approx 0.0231
    P(Sel_2 = 4+)                                            very rare

For rank-0 curves (our filter), empirical distribution should be compared to the
Poonen-Rains prediction conditioned on rank 0. At rank 0, Sel_2 >= dim E(Q)[2].
We report both the raw Sel_2 and Sel_2 - dim_E_tors_2 = dim_F2 Sha[2].

Method:
  1. Pull 10K random rank-0 curves from lmfdb.ec_curvedata (ainvs, label, torsion_order).
  2. Compute Sel_2 via Techne.
  3. Report distribution, chi-square against Poonen-Rains prediction.
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
import psycopg2
from collections import Counter
from techne.lib.selmer_rank import selmer_2_rank, selmer_2_data

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')
N_SAMPLE = 10000
SEED = 20260422

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'data', 'bklpr_sel2_test.json')

# Poonen-Rains prediction (all ranks, p=2) — from Poonen-Rains 2012.
# For the unconditional Sel_2 distribution:
PR_PROB = {
    0: 0.209719,
    1: 0.524298,
    2: 0.242430,
    3: 0.023088,
    4: 0.000463,
    5: 0.000003,
}


def main():
    t0 = time.time()
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    print(f'[{time.strftime("%H:%M:%S")}] Sampling {N_SAMPLE} rank-0 EC...')
    cur.execute("""
        SELECT lmfdb_label, ainvs, torsion, conductor, sha
        FROM ec_curvedata
        WHERE rank = '0'
          AND ainvs IS NOT NULL
        ORDER BY random()
        LIMIT %s
    """, (N_SAMPLE,))
    rows = cur.fetchall()
    print(f'  got {len(rows)} curves')

    results = []
    sel2_counts = Counter()
    sha2_counts = Counter()  # Sel_2 - dim_E_tors_2
    failures = 0
    t_compute = time.time()
    for i, (label, ainvs_str, tors, cond, sha_an) in enumerate(rows):
        try:
            ainvs = [int(float(x.strip())) for x in ainvs_str.strip('[]{}').split(',')]
            if len(ainvs) != 5:
                failures += 1
                continue
            data = selmer_2_data(ainvs, effort=1)
            if not data.get('rank_proved'):
                continue  # skip unproved; rank=0 from LMFDB but PARI may differ
            sel2 = data['dim_sel_2']
            dim_e2 = data['dim_E2']
            sha2 = sel2 - dim_e2  # rank is 0 so this is dim_F2 Sha[2]
            if sha2 < 0:
                sha2 = 0
            sel2_counts[sel2] += 1
            sha2_counts[sha2] += 1
            results.append({
                'label': label,
                'ainvs': ainvs,
                'dim_sel_2': sel2,
                'dim_E2_tors': dim_e2,
                'dim_sha_2': sha2,
                'sha_an': float(sha_an) if sha_an is not None else None,
            })
        except Exception as e:
            failures += 1
            if failures < 5:
                print(f'  fail on {label}: {e}')
        if (i + 1) % 1000 == 0:
            elapsed = time.time() - t_compute
            rate = (i + 1) / elapsed
            eta = (len(rows) - i - 1) / rate
            print(f'  {i+1}/{len(rows)}  rate {rate:.1f}/s  eta {eta:.0f}s')

    n = len(results)
    print(f'\nComputed Sel_2 for {n} / {len(rows)} (failures={failures}) in {time.time()-t_compute:.1f}s')

    # Observed vs PR
    print(f'\n{"Sel_2":>8} {"observed":>12} {"obs_frac":>10} {"PR_pred":>10} {"diff":>10}')
    chi2 = 0.0
    total_expected = 0.0
    for k in sorted(set(list(sel2_counts.keys()) + list(PR_PROB.keys()))):
        obs = sel2_counts.get(k, 0)
        frac = obs / n
        pr = PR_PROB.get(k, 0.0)
        expected = pr * n
        if expected >= 5:
            chi2 += (obs - expected) ** 2 / expected
            total_expected += expected
        print(f'{k:>8} {obs:>12} {frac:>10.4f} {pr:>10.4f} {frac-pr:>+10.4f}')

    # Chi-square dof = bins - 1 (with expected >= 5 filter)
    from scipy.stats import chi2 as chi2_dist
    dof = max(1, len([k for k in PR_PROB if PR_PROB[k] * n >= 5]) - 1)
    p_value = 1.0 - chi2_dist.cdf(chi2, df=dof)
    print(f'\nChi-square = {chi2:.3f}  dof = {dof}  p = {p_value:.4f}')

    # Sha2 distribution (rank-0 conditional)
    print(f'\nSha[2] dim distribution (rank-0, n={n}):')
    for k in sorted(sha2_counts.keys()):
        c = sha2_counts[k]
        print(f'  dim Sha[2] = {k}: {c} ({c/n:.4f})')

    # Summary stats
    mean_sel2 = sum(k * v for k, v in sel2_counts.items()) / n
    mean_sha2 = sum(k * v for k, v in sha2_counts.items()) / n
    print(f'\nMean Sel_2   = {mean_sel2:.4f}  (PR prediction ~1.0 for p=2 all-rank)')
    print(f'Mean Sha[2]  = {mean_sha2:.4f}')

    out = {
        'meta': {
            'protocol': 'BKLPR Sel_2 test on 10K rank-0 EC',
            'n_sampled': len(rows),
            'n_computed': n,
            'n_failures': failures,
            'rank_filter': '0 (from LMFDB ec_curvedata)',
            'seed': SEED,
            'elapsed_sec': time.time() - t0,
        },
        'poonen_rains_reference': PR_PROB,
        'observed_sel2': dict(sel2_counts),
        'observed_sel2_fraction': {k: v / n for k, v in sel2_counts.items()},
        'observed_sha2': dict(sha2_counts),
        'chi_square': float(chi2),
        'chi_square_dof': int(dof),
        'chi_square_p': float(p_value),
        'mean_sel2': mean_sel2,
        'mean_sha2': mean_sha2,
    }
    with open(OUT, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
