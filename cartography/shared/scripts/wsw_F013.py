"""
Weak Signal Walk — F013 (Zero spacing rigidity vs rank)

Task: wsw_F013 (claimed by Harmonia_M2_sessionD, 2026-04-17)

Baseline from pattern library: slope = -0.0019, R^2 = 0.399 (pooled, unspecified
preprocessing). Task asks: does the rank-coupling survive conductor conditioning,
and does the representation-permutation null (P042) kill it?

Projections tested this walk:
  P020 — conductor conditioning
  P021 — bad-prime count stratification
  P024 — torsion stratification
  P025 — CM vs non-CM
  P042 — feature permutation (shuffle zero sequences across curves, keep rank)
  P051 — N(T) unfolding (density normalization)

Balanced sample by rank to avoid Pattern 4 (rank 0 dominates pooled data).

Author: Harmonia_M2_sessionD, 2026-04-17
"""
import json
import os
import sys
import numpy as np
import psycopg2
from pathlib import Path


PG = dict(host='192.168.1.176', port=5432, dbname='lmfdb',
          user='postgres', password='prometheus')


def fetch_sample(n_per_rank=1000, max_rank=3):
    """Pull n_per_rank curves per rank bin (balanced). Returns list of dicts."""
    conn = psycopg2.connect(**PG)
    cur = conn.cursor()
    rows = []
    for r in range(max_rank + 1):
        cur.execute(
            """
            SELECT ec_label, rank, conductor, num_bad_primes, torsion, cm,
                   analytic_conductor, positive_zeros
            FROM bsd_joined
            WHERE rank = %s
              AND positive_zeros IS NOT NULL
              AND analytic_conductor IS NOT NULL
            ORDER BY random()
            LIMIT %s
            """, (r, n_per_rank))
        rows.extend(cur.fetchall())
    cur.close(); conn.close()
    colnames = ['ec_label', 'rank', 'conductor', 'num_bad_primes', 'torsion',
                'cm', 'analytic_conductor', 'positive_zeros']
    result = []
    for row in rows:
        d = dict(zip(colnames, row))
        # Parse positive_zeros (TEXT holding list literal)
        zs = d['positive_zeros']
        if isinstance(zs, str):
            zs = json.loads(zs)
        d['zeros'] = np.asarray(zs, dtype=float)
        result.append(d)
    return result


def spacing_variance(zeros, n_max=10):
    """Variance of first n_max gaps, avoiding the corrupted pos 21-24 zone."""
    zs = zeros[:n_max + 1]
    if len(zs) < 3:
        return np.nan
    gaps = np.diff(zs)
    return float(np.var(gaps))


def unfold_zeros(zeros, analytic_conductor):
    """N(T) unfolding for degree-2 L-functions: gamma_j -> (gamma_j / (2*pi)) * log(N * gamma_j^2 / (4 pi^2))
    Here N is the analytic_conductor. Simpler mean-density normalization."""
    N = float(analytic_conductor)
    if N <= 0:
        return None
    arr = np.asarray(zeros, dtype=float)
    arr = arr[arr > 0]
    if len(arr) < 3:
        return None
    # Density formula for deg 2: rho(t) ~ (1/(2pi)) * log(N * t^2 / (4 pi^2))
    # Cumulative density: integrated rho over 0..gamma_j gives unfolded index.
    # Use approximate local rescale: gamma'_j = gamma_j * (1/(2pi)) * log(N*gamma_j^2 / (4 pi^2))
    logterm = np.log(N * arr * arr / (4 * np.pi * np.pi))
    # Clamp any weird values
    logterm = np.clip(logterm, 0.01, None)
    unfolded = arr * logterm / (2 * np.pi)
    return unfolded


def fit_slope(xs, ys):
    xs = np.asarray(xs, dtype=float); ys = np.asarray(ys, dtype=float)
    mask = np.isfinite(xs) & np.isfinite(ys)
    xs = xs[mask]; ys = ys[mask]
    if len(xs) < 3:
        return dict(slope=float('nan'), intercept=float('nan'), r2=float('nan'), n=int(len(xs)))
    slope, intercept = np.polyfit(xs, ys, 1)
    yhat = slope * xs + intercept
    ss_res = np.sum((ys - yhat) ** 2)
    ss_tot = np.sum((ys - ys.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float('nan')
    return dict(slope=float(slope), intercept=float(intercept), r2=float(r2), n=int(len(xs)))


def within_strata_fit(rows, strat_fn, axis_name):
    """Bin by strat_fn; fit slope within each bin. Returns per-bin and pooled."""
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
        ranks = [r['rank'] for r in rs]
        svars = [r['spacing_var'] for r in rs]
        per_bin[str(k)] = {'n': len(rs), **fit_slope(ranks, svars)}
    return {'axis': axis_name, 'per_bin': per_bin}


def feature_permutation_null(rows, n_shuffles=1000, rng=None):
    """P042 — shuffle zero-sequences across curves (keep ranks). Re-fit slope.
    Return (real_slope, null_slopes, p_value_lower_tail, p_value_abs)."""
    rng = rng or np.random.default_rng(42)
    ranks = np.array([r['rank'] for r in rows])
    svars = np.array([r['spacing_var'] for r in rows])
    mask = np.isfinite(svars)
    ranks = ranks[mask]; svars = svars[mask]

    real = fit_slope(ranks, svars)['slope']
    null_slopes = np.empty(n_shuffles)
    for i in range(n_shuffles):
        shuffled_sv = rng.permutation(svars)
        null_slopes[i] = fit_slope(ranks, shuffled_sv)['slope']
    null_mean = float(null_slopes.mean())
    null_std = float(null_slopes.std())
    if null_std > 0:
        z = (real - null_mean) / null_std
    else:
        z = float('nan')
    # Two-sided p-value: fraction of |null| >= |real|
    p_two_sided = float((np.abs(null_slopes) >= abs(real)).mean())
    return {
        'real_slope': float(real),
        'null_mean': null_mean,
        'null_std': null_std,
        'z': float(z),
        'p_two_sided': p_two_sided,
        'n_shuffles': int(n_shuffles),
    }


def main():
    print('[F013] Fetching balanced rank sample...')
    rows = fetch_sample(n_per_rank=1000, max_rank=3)
    print(f'[F013] Got {len(rows)} rows.')

    # Compute spacing_var per curve (raw zeros)
    for r in rows:
        r['spacing_var'] = spacing_variance(r['zeros'], n_max=10)

    # Pooled fit (calibration)
    ranks = [r['rank'] for r in rows]
    svars = [r['spacing_var'] for r in rows]
    pooled = fit_slope(ranks, svars)
    pooled['label'] = 'pooled_raw_zeros (calibration vs baseline slope=-0.0019 R2=0.399)'

    # Per-rank stats
    per_rank = {}
    for r in range(4):
        rs = [x for x in rows if x['rank'] == r]
        vs = [x['spacing_var'] for x in rs if np.isfinite(x['spacing_var'])]
        per_rank[str(r)] = dict(n=len(rs), n_valid=len(vs),
                                spacing_var_mean=float(np.mean(vs)) if vs else None,
                                spacing_var_std=float(np.std(vs)) if vs else None)

    # P020 conductor conditioning — log10 bins
    def cond_bin(row):
        N = float(row['conductor'])
        if N <= 0: return None
        lgN = np.log10(N)
        # 4 bins: [0,3), [3,4), [4,5), [5,inf)
        if lgN < 3: return 'log10N<3'
        if lgN < 4: return '3<=log10N<4'
        if lgN < 5: return '4<=log10N<5'
        return 'log10N>=5'

    p020 = within_strata_fit(rows, cond_bin, 'P020_conductor')

    # P021 bad-prime count
    def bp_bin(row):
        k = row['num_bad_primes']
        if k is None: return None
        return str(min(int(k), 6))  # cap tail at 6+
    p021 = within_strata_fit(rows, bp_bin, 'P021_num_bad_primes')

    # P024 torsion stratification
    def tors_bin(row):
        t = row['torsion']
        if t is None: return None
        return str(int(t))
    p024 = within_strata_fit(rows, tors_bin, 'P024_torsion')

    # P025 CM binary
    def cm_bin(row):
        return 'cm' if int(row['cm'] or 0) != 0 else 'non_cm'
    p025 = within_strata_fit(rows, cm_bin, 'P025_cm_vs_noncm')

    # P042 feature permutation null
    print('[F013] Running P042 feature permutation null (1000 shuffles)...')
    p042 = feature_permutation_null(rows, n_shuffles=1000)
    p042['label'] = 'P042_feature_permutation (shuffle spacings across curves, keep ranks)'

    # P051 unfolded zeros
    print('[F013] Computing unfolded zeros and re-fitting slope...')
    for r in rows:
        uz = unfold_zeros(r['zeros'], r['analytic_conductor'])
        if uz is None:
            r['spacing_var_unfolded'] = float('nan')
        else:
            gaps = np.diff(uz[:11])
            r['spacing_var_unfolded'] = float(np.var(gaps)) if len(gaps) >= 2 else float('nan')
    unfolded_ranks = [r['rank'] for r in rows]
    unfolded_svars = [r['spacing_var_unfolded'] for r in rows]
    p051 = fit_slope(unfolded_ranks, unfolded_svars)
    p051['label'] = 'P051_unfolded_pooled (unfolded zeros, pooled slope)'

    # Construct verdict based on shape across projections
    baseline = {'slope': -0.0019, 'r2': 0.399, 'source': 'pattern_library.md Pattern?/F013'}

    result = {
        'specimen_id': 'F013',
        'specimen_label': 'Zero spacing rigidity vs rank',
        'drafted_by': 'Harmonia_M2_sessionD',
        'task_id': 'wsw_F013',
        'baseline': baseline,
        'sample': {
            'n_total': len(rows),
            'n_per_rank': per_rank,
            'balanced_by_rank': True,
            'max_rank': 3,
            'sampling_note': 'ORDER BY random() per rank to avoid Pattern 4 (rank 0 dominance)',
        },
        'pooled_raw': pooled,
        'projections': {
            'P020_conductor_conditioning': p020,
            'P021_bad_prime_count': p021,
            'P024_torsion': p024,
            'P025_cm_vs_noncm': p025,
            'P042_feature_permutation_null': p042,
            'P051_unfolded_pooled': p051,
        },
    }

    outpath = Path('cartography/docs/wsw_F013_results.json')
    outpath.parent.mkdir(parents=True, exist_ok=True)
    with open(outpath, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f'[F013] Wrote {outpath}')
    # Short console verdict for logs
    print()
    print('== POOLED RAW (calibration) ==')
    print(f'  slope={pooled["slope"]:.6f}  r2={pooled["r2"]:.4f}  n={pooled["n"]}')
    print(f'  baseline: slope=-0.0019  r2=0.399')
    print()
    print('== P042 feature permutation null ==')
    print(f'  real_slope={p042["real_slope"]:.6f}  null_mean={p042["null_mean"]:.6f}  null_std={p042["null_std"]:.6f}')
    print(f'  z={p042["z"]:.3f}  p_two_sided={p042["p_two_sided"]:.4f}')
    print()
    print('== P051 unfolded pooled ==')
    print(f'  slope={p051["slope"]:.6f}  r2={p051["r2"]:.4f}  n={p051["n"]}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
