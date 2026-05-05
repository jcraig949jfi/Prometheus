"""F011 conductor-mechanism test on BSD-1646 (parallel to Ergon's 200K run).

Hypothesis (Ergon/Aporia mechanism (a)): the gap-compression gradient is
conductor-dependent. Test on BSD-1646:
  1. Split rank-0 curves into conductor deciles.
  2. Per decile, compute gap1..gap4 variance (local-4-gap normalization).
  3. Compare to matched-GUE null (0.1472, 0.1741, 0.1725, 0.1468).
  4. Observe: does deficit DEEPEN or ATTENUATE with conductor?

Expected under (a): deficit grows with log(conductor) — L-function zero
statistics have stronger compression for "harder" arithmetic.
Kill: deficit flat across conductor deciles. Then conductor is NOT the mediator.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
import psycopg2

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')
MATCHED_NULL = [0.1472, 0.1741, 0.1725, 0.1468]  # from Ergon
SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'bsd_at_scale.json')
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'f011_conductor_gradient.json')
N_DECILES = 5  # use quintiles on n=782 rank-0 (~156 per bucket)


def parse_zeros(s):
    if not s: return None
    try:
        vals = json.loads(s.replace('{','[').replace('}',']'))
        return [float(z) for z in vals if float(z) > 0]
    except Exception:
        return None


def norm_gaps(zs):
    if zs is None or len(zs) < 5: return None
    z5 = sorted(zs)[:5]
    g = np.diff(z5)
    m = g.mean()
    if m <= 0: return None
    return g / m


def main():
    bsd = json.load(open(SRC))
    curves = bsd['results']
    iso_origins = {}
    for c in curves:
        parts = c['label'].split('.')
        cond, iso_letter = parts[0], parts[1].rstrip('0123456789')
        iso_origins[f'{cond}.{iso_letter}'] = f'EllipticCurve/Q/{cond}/{iso_letter}'

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("SELECT origin, positive_zeros FROM lfunc_lfunctions WHERE origin = ANY(%s) AND positive_zeros IS NOT NULL",
                (list(iso_origins.values()),))
    zeros_by_origin = {o: parse_zeros(z) for o, z in cur}

    rows = []  # (conductor, gaps, sha)
    for c in curves:
        if c['rank'] != 0: continue
        parts = c['label'].split('.')
        cond = int(c['conductor'])
        iso_letter = parts[1].rstrip('0123456789')
        origin = f'EllipticCurve/Q/{parts[0]}/{iso_letter}'
        zs = zeros_by_origin.get(origin)
        g = norm_gaps(zs)
        if g is None: continue
        rows.append({'cond': cond, 'gaps': g, 'sha': float(c['sha_an'])})

    print(f'rank-0 with zeros: n={len(rows)}')

    # Quintile by log(conductor)
    logs = np.array([np.log(r['cond']) for r in rows])
    order = np.argsort(logs)
    boundaries = np.linspace(0, len(rows), N_DECILES + 1).astype(int)
    decile_assignment = np.empty(len(rows), dtype=int)
    for k in range(N_DECILES):
        decile_assignment[order[boundaries[k]:boundaries[k+1]]] = k

    out = {
        'meta': {
            'protocol': 'F011 conductor-mechanism test on BSD-1646 rank-0',
            'n_deciles': N_DECILES,
            'matched_null': MATCHED_NULL,
            'n_rank0': len(rows),
        },
        'per_decile': [],
    }

    print(f'\n{"decile":>8}  {"n":>4}  {"min_log_N":>9}  {"max_log_N":>9}   {"d1%":>6}  {"d2%":>6}  {"d3%":>6}  {"d4%":>6}')
    for k in range(N_DECILES):
        idx = np.where(decile_assignment == k)[0]
        sub = [rows[i] for i in idx]
        if not sub: continue
        log_min = float(logs[idx].min())
        log_max = float(logs[idx].max())
        gaps = np.array([r['gaps'] for r in sub])  # (n, 4)
        deficits = []
        for gi in range(4):
            v = float(np.var(gaps[:, gi]))
            defi = (1 - v/MATCHED_NULL[gi]) * 100
            deficits.append(defi)
        print(f'{k+1:>8}  {len(sub):>4}  {log_min:>9.2f}  {log_max:>9.2f}   {deficits[0]:+6.1f}  {deficits[1]:+6.1f}  {deficits[2]:+6.1f}  {deficits[3]:+6.1f}')
        out['per_decile'].append({
            'decile': k + 1,
            'n': len(sub),
            'log_N_min': log_min,
            'log_N_max': log_max,
            'mean_log_N': float(logs[idx].mean()),
            'gap_deficits_pct': deficits,
            'gap_variances': [float(np.var(gaps[:, gi])) for gi in range(4)],
        })

    # Fit deficit vs log(N) linear slope per gap
    print(f'\nLinear slope of deficit vs mean log(N) per gap:')
    mean_logs = np.array([d['mean_log_N'] for d in out['per_decile']])
    for gi in range(4):
        defs = np.array([d['gap_deficits_pct'][gi] for d in out['per_decile']])
        A = np.vstack([mean_logs, np.ones_like(mean_logs)]).T
        slope, intercept = np.linalg.lstsq(A, defs, rcond=None)[0]
        # Correlation
        r = float(np.corrcoef(mean_logs, defs)[0, 1])
        print(f'  gap{gi+1}: slope = {slope:+.2f} %/log(N)  r = {r:+.3f}  (n={len(mean_logs)} deciles)')
        out['per_decile'][0].setdefault('fits', {})
        out.setdefault('fits_per_gap', {})[f'gap{gi+1}'] = {
            'slope_pct_per_log_N': float(slope), 'intercept': float(intercept), 'r': r
        }

    with open(OUT, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
