"""
Weak Signal Walk — F015 (Szpiro monotone decrease at fixed bad-prime count)

Task: wsw_F015 (claimed by Harmonia_M2_sessionD, 2026-04-17)

Ergon (2026-04-16) reported: szpiro_ratio decreases monotonically with conductor
when stratified by num_bad_primes. Reproduce and apply 5 projections.

Projections tested:
  P021 — bad-prime count stratification (the axis that resolves the signal)
  P020 — conductor conditioning
  P042 — feature permutation null (shuffle szpiro within strata; does the
         within-stratum slope survive?)
  P051 — N(T) unfolding equivalent (ambiguous for abc-like data; report
         what we can)
  P052 — prime decontamination (residualize szpiro on num_bad_primes
         before testing)

Data source: lmfdb.ec_curvedata (has szpiro_ratio, conductor, num_bad_primes
directly — no need for bsd_joined).

Pattern 1 warning: szpiro_ratio = log|disc|/log(N); both encode bad-prime
content. Apply formula-lineage check to every z-score.

Balanced sampling per num_bad_primes to avoid Pattern 4.

Author: Harmonia_M2_sessionD, 2026-04-17
"""
import json
import sys
import io
import numpy as np
import psycopg2
from pathlib import Path

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


PG = dict(host='192.168.1.176', port=5432, dbname='lmfdb',
          user='postgres', password='prometheus')


def fetch_sample(n_per_stratum=5000, k_bins=(1, 2, 3, 4, 5, 6)):
    """Balanced sample by num_bad_primes. Returns list of dicts."""
    conn = psycopg2.connect(**PG)
    cur = conn.cursor()
    rows = []
    for k in k_bins:
        cur.execute(
            """
            SELECT lmfdb_label, conductor, num_bad_primes,
                   szpiro_ratio, faltings_height, rank, cm, semistable
            FROM ec_curvedata
            WHERE num_bad_primes::int = %s
              AND szpiro_ratio IS NOT NULL
              AND conductor IS NOT NULL
              AND conductor::bigint > 0
            ORDER BY random()
            LIMIT %s
            """, (k, n_per_stratum))
        rows.extend(cur.fetchall())
    cur.close(); conn.close()
    colnames = ['lmfdb_label', 'conductor', 'num_bad_primes',
                'szpiro_ratio', 'faltings_height', 'rank', 'cm', 'semistable']
    result = []
    for row in rows:
        d = dict(zip(colnames, row))
        d['log10_conductor'] = float(np.log10(float(d['conductor'])))
        d['szpiro'] = float(d['szpiro_ratio'])
        d['k'] = int(d['num_bad_primes'])
        result.append(d)
    return result


def fit_slope(xs, ys):
    xs = np.asarray(xs, dtype=float); ys = np.asarray(ys, dtype=float)
    mask = np.isfinite(xs) & np.isfinite(ys)
    xs = xs[mask]; ys = ys[mask]
    if len(xs) < 3:
        return dict(slope=float('nan'), intercept=float('nan'),
                    r2=float('nan'), n=int(len(xs)))
    slope, intercept = np.polyfit(xs, ys, 1)
    yhat = slope * xs + intercept
    ss_res = np.sum((ys - yhat) ** 2)
    ss_tot = np.sum((ys - ys.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float('nan')
    return dict(slope=float(slope), intercept=float(intercept),
                r2=float(r2), n=int(len(xs)))


def within_strata_fit(rows, strat_fn, axis_name, y='szpiro', x='log10_conductor'):
    buckets = {}
    for row in rows:
        try:
            k = strat_fn(row)
        except Exception:
            continue
        if k is None:
            continue
        buckets.setdefault(k, []).append(row)
    per_bin = {}
    for k, rs in buckets.items():
        if len(rs) < 30:
            per_bin[str(k)] = {'n': len(rs), 'skipped': 'n<30'}
            continue
        xs = [r[x] for r in rs]
        ys = [r[y] for r in rs]
        per_bin[str(k)] = {'n': len(rs), **fit_slope(xs, ys)}
    return {'axis': axis_name, 'per_bin': per_bin}


def permutation_null_within_strata(rows, strat_fn, n_shuffles=500, rng=None):
    """Within each stratum, shuffle the y variable (szpiro) and re-fit slope.
    Returns per-stratum null statistics and p-values."""
    rng = rng or np.random.default_rng(42)
    buckets = {}
    for row in rows:
        k = strat_fn(row)
        if k is None: continue
        buckets.setdefault(k, []).append(row)
    per_stratum = {}
    for k, rs in buckets.items():
        if len(rs) < 30:
            per_stratum[str(k)] = {'n': len(rs), 'skipped': 'n<30'}
            continue
        xs = np.array([r['log10_conductor'] for r in rs])
        ys = np.array([r['szpiro'] for r in rs])
        real = fit_slope(xs, ys)
        null_slopes = np.empty(n_shuffles)
        for i in range(n_shuffles):
            ys_shuf = rng.permutation(ys)
            null_slopes[i] = fit_slope(xs, ys_shuf)['slope']
        null_mean = float(null_slopes.mean())
        null_std = float(null_slopes.std())
        z = (real['slope'] - null_mean) / null_std if null_std > 0 else float('nan')
        p_two = float((np.abs(null_slopes) >= abs(real['slope'])).mean())
        per_stratum[str(k)] = {
            'n': len(rs),
            'real_slope': real['slope'],
            'real_r2': real['r2'],
            'null_mean': null_mean, 'null_std': null_std,
            'z': float(z), 'p_two_sided': p_two, 'n_shuffles': int(n_shuffles),
        }
    return per_stratum


def decontaminate_and_refit(rows):
    """P052-like: residualize szpiro against num_bad_primes (the axis known to
    confound), then fit slope of residuals against log_conductor.
    If the monotone trend is bad-prime-mediated, residualization should kill
    the slope inside each stratum (which would be a tautology flag).
    """
    ks = np.array([r['k'] for r in rows])
    szs = np.array([r['szpiro'] for r in rows])
    logN = np.array([r['log10_conductor'] for r in rows])
    # Residualize szpiro on k
    mean_by_k = {int(k): float(np.mean(szs[ks == k])) for k in set(ks.tolist())}
    sz_resid = np.array([szs[i] - mean_by_k[int(ks[i])] for i in range(len(rows))])
    # Pooled slope of residuals vs logN
    pooled = fit_slope(logN, sz_resid)
    # Per-stratum slope of residuals (should be same as raw per-stratum since
    # residualization is a constant shift within each k — confirms the maths).
    buckets = {}
    for i, r in enumerate(rows):
        buckets.setdefault(r['k'], []).append((logN[i], sz_resid[i]))
    per_bin = {}
    for k, pts in buckets.items():
        if len(pts) < 30:
            per_bin[str(k)] = {'n': len(pts), 'skipped': 'n<30'}; continue
        x = [p[0] for p in pts]; y = [p[1] for p in pts]
        per_bin[str(k)] = {'n': len(pts), **fit_slope(x, y)}
    return {
        'residualization_on': 'num_bad_primes (k)',
        'pooled_residual_slope_vs_logN': pooled,
        'per_bin': per_bin,
        'interpretation': (
            'Residualizing szpiro on k is a constant shift within each k, so '
            'within-k slopes are identical to the raw P021 slopes. The interesting '
            'number is the POOLED residual slope: if it remains strongly negative, '
            'there is residual conductor-dependence after removing the stratum effect. '
            'If it collapses to ~0, the pooled monotone signal was entirely k-mediated '
            '(and the within-k residual slope is the real effect).'
        ),
    }


def main():
    print('[F015] Fetching balanced sample by num_bad_primes...')
    rows = fetch_sample(n_per_stratum=5000, k_bins=(1, 2, 3, 4, 5, 6))
    print(f'[F015] Got {len(rows)} rows.')
    if len(rows) == 0:
        print('NO DATA', file=sys.stderr); sys.exit(1)

    # Per-stratum summary
    per_stratum_counts = {}
    for r in rows:
        per_stratum_counts.setdefault(r['k'], 0)
        per_stratum_counts[r['k']] += 1
    print('[F015] Per-stratum counts:', per_stratum_counts)

    # POOLED pooled (no stratification) — shows confound
    pooled_logN = [r['log10_conductor'] for r in rows]
    pooled_sz = [r['szpiro'] for r in rows]
    pooled = fit_slope(pooled_logN, pooled_sz)
    pooled['label'] = 'pooled (no stratification)'

    # P021 stratification by k = num_bad_primes
    p021 = within_strata_fit(rows, lambda r: r['k'], 'P021_num_bad_primes')

    # Ergon's claim: monotone decrease. Check sign and ordering of per-k slopes.
    slopes_by_k = {int(k): v['slope'] for k, v in p021['per_bin'].items()
                   if 'slope' in v and np.isfinite(v['slope'])}
    slopes_ordered = [(k, slopes_by_k[k]) for k in sorted(slopes_by_k)]
    monotone_check = {
        'slopes_in_k_order': [{'k': k, 'slope': s} for k, s in slopes_ordered],
        'all_negative': all(s < 0 for _, s in slopes_ordered),
        'monotone_decreasing_in_k': (
            all(slopes_ordered[i][1] <= slopes_ordered[i-1][1]
                for i in range(1, len(slopes_ordered)))
            if len(slopes_ordered) >= 2 else None
        ),
        'note': ('"Monotone decreasing in k" means the within-k slope gets MORE '
                 'negative as bad-prime count grows — i.e., the szpiro-vs-logN '
                 'trend is steepest for many-bad-prime curves.'),
    }

    # P020 conductor conditioning — within-conductor-bin, does k explain slope?
    def cond_bin(r):
        lg = r['log10_conductor']
        if lg < 3: return 'log10N<3'
        if lg < 4: return '3<=log10N<4'
        if lg < 5: return '4<=log10N<5'
        return 'log10N>=5'
    # Within each conductor bin, fit szpiro vs k (is k still a predictor?)
    cond_buckets = {}
    for r in rows:
        cond_buckets.setdefault(cond_bin(r), []).append(r)
    p020 = {'axis': 'P020_conductor_within_bin_szpiro_vs_k', 'per_bin': {}}
    for cb, rs in cond_buckets.items():
        if len(rs) < 30:
            p020['per_bin'][cb] = {'n': len(rs), 'skipped': 'n<30'}; continue
        ks = [r['k'] for r in rs]; szs = [r['szpiro'] for r in rs]
        p020['per_bin'][cb] = {'n': len(rs), **fit_slope(ks, szs)}

    # P042 permutation null within strata
    print('[F015] Running P042 permutation null within strata (500 shuffles per stratum)...')
    p042 = permutation_null_within_strata(rows, lambda r: r['k'], n_shuffles=500)

    # P052 decontamination
    print('[F015] Running P052 decontamination...')
    p052 = decontaminate_and_refit(rows)

    # Tautology note per Pattern 1
    tautology_note = (
        'Pattern 1 lineage check: szpiro_ratio = log|disc| / log(N). Both numerator '
        'and denominator encode the same primes (bad primes dominate log|disc|, and '
        'conductor is the product of bad-prime powers). Stratifying by num_bad_primes '
        'is the NATURAL tautology control: at fixed k, the discriminant\'s bad-prime '
        'structure is held roughly constant, leaving the residual szpiro-vs-logN '
        'relationship to reflect (a) conductor spread within the bad-prime set and '
        '(b) the specific primes chosen. Effect survives P021 by construction if it '
        'is not purely confound-driven; this is what Ergon observed.'
    )

    # Shape summary
    shape = {
        'verdict_shape': 'REPRODUCE / PARTIAL / KILLED pending results',
        'invariance_profile_preview': {
            'P021': 'see slopes_in_k_order and p042 z-scores',
            'P020': 'see p020 per-bin slopes of szpiro vs k within conductor bins',
            'P042': 'see p042 per-stratum z and p_two_sided',
            'P051': 'NOT_APPLICABLE (zero-unfolding concept; no natural analog for scalar szpiro). Flagging as 0 in invariance profile.',
            'P052': 'see p052 pooled_residual_slope_vs_logN — if near 0, pooled monotone was k-mediated',
        },
    }

    result = {
        'specimen_id': 'F015',
        'specimen_label': 'abc/Szpiro monotone decrease at fixed bad-prime count (Ergon 2026-04-16)',
        'drafted_by': 'Harmonia_M2_sessionD',
        'task_id': 'wsw_F015',
        'sample': {
            'n_total': len(rows),
            'n_per_stratum': per_stratum_counts,
            'balanced_by': 'num_bad_primes',
            'k_bins': [1, 2, 3, 4, 5, 6],
        },
        'tautology_warning': tautology_note,
        'pooled': pooled,
        'projections': {
            'P021_num_bad_primes_stratified_slope_szpiro_vs_logN': p021,
            'P020_conductor_binned_slope_szpiro_vs_k': p020,
            'P042_within_stratum_permutation_null': p042,
            'P051_unfolding': {
                'skipped': 'NOT_APPLICABLE',
                'reason': 'P051 N(T) unfolding is a zero-spacing concept. No natural analog for scalar szpiro_ratio. Flagging as 0 (untested) in invariance profile rather than forcing a mismatched test.',
            },
            'P052_decontamination': p052,
        },
        'monotone_check': monotone_check,
        'shape_summary': shape,
    }

    outpath = Path('cartography/docs/wsw_F015_results.json')
    outpath.parent.mkdir(parents=True, exist_ok=True)
    with open(outpath, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f'[F015] Wrote {outpath}')

    print()
    print('== POOLED (pre-stratification) ==')
    print(f'  slope={pooled["slope"]:+.6f}  r2={pooled["r2"]:+.4f}  n={pooled["n"]}')
    print()
    print('== P021 within-k slopes (szpiro vs log N) ==')
    for row_ in monotone_check['slopes_in_k_order']:
        print(f'  k={row_["k"]}  slope={row_["slope"]:+.6f}')
    print(f'  all_negative: {monotone_check["all_negative"]}')
    print(f'  monotone_decreasing_in_k: {monotone_check["monotone_decreasing_in_k"]}')
    print()
    print('== P042 within-stratum permutation null ==')
    for k in sorted(p042, key=lambda s: int(s) if s.isdigit() else 999):
        v = p042[k]
        if 'skipped' in v: continue
        print(f'  k={k}  n={v["n"]}  real_slope={v["real_slope"]:+.6f}  z={v["z"]:+.3f}  p={v["p_two_sided"]:.4f}')
    print()
    print('== P052 decontamination pooled residual slope ==')
    pr = p052['pooled_residual_slope_vs_logN']
    print(f'  pooled residual slope={pr["slope"]:+.6f}  r2={pr["r2"]:+.4f}  n={pr["n"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
