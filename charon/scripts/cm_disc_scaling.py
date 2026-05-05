"""V-CM-scaling: compression depth vs |CM discriminant| on 2134 rank-0 CM EC.

Aporia proposal: test whether compression is a function of |D|. Heegner
discriminants (h(K)=1) suggest the deepest compression should correlate with
simplicity of the CM ring (smaller |D|, larger class number for bigger |D|).

Plan:
  1. Pull all 2134 rank-0 CM EC with stored zeros.
  2. Stratify by CM disc.
  3. Per disc (n >= 10), compute gap1..gap4 variance / matched-GUE deficit.
  4. Fit deficit_gap1 ~ f(|D|, h(K)) linear regression.
  5. Flag Heegner vs non-Heegner dichotomy.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
import psycopg2
from collections import defaultdict

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')
MATCHED_NULL = [0.1472, 0.1741, 0.1725, 0.1468]
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'cm_disc_scaling.json')

HEEGNER = {-3, -4, -7, -8, -11, -19, -43, -67, -163}  # class number 1 imaginary quad


def parse_zeros(s):
    if not s: return None
    try:
        vals = json.loads(s.replace('{','[').replace('}',']'))
        return [float(z) for z in vals if float(z) > 0]
    except Exception:
        return None


def norm_gaps(zs):
    if zs is None or len(zs) < 5: return None
    zs = sorted(zs)[:5]
    g = np.diff(zs)
    m = g.mean()
    if m <= 0: return None
    return g / m


def main():
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    print('Fetching CM rank-0 with zeros...', flush=True)
    cur.execute("""
        SELECT e.lmfdb_label, e.cm, e.conductor, l.positive_zeros
        FROM ec_curvedata e
        JOIN lfunc_lfunctions l
          ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso,'.',1)
                        || '/' || split_part(e.lmfdb_iso,'.',2)
        WHERE e.rank = '0' AND e.cm::int != 0
          AND l.positive_zeros IS NOT NULL
    """)
    rows = cur.fetchall()
    print(f'  got {len(rows)} CM rank-0 curves', flush=True)

    by_disc = defaultdict(list)
    conductors = defaultdict(list)
    for lab, cm, cond, z in rows:
        zs = parse_zeros(z)
        g = norm_gaps(zs)
        if g is None: continue
        by_disc[int(cm)].append(g)
        conductors[int(cm)].append(int(cond))

    # Report per-disc deficits (n >= 10)
    print(f'\n{"disc":>5}  {"heegner":>7}  {"n":>5}  {"mean_logN":>9}  {"gap1%":>7}  {"gap2%":>7}  {"gap3%":>7}  {"gap4%":>7}  {"grad":>6}')
    print('-' * 85)
    results = []
    for disc in sorted(by_disc.keys(), key=lambda d: abs(d)):
        arr = np.array(by_disc[disc])
        if len(arr) < 10: continue
        conds = np.array(conductors[disc])
        mean_log_n = float(np.log(conds.mean()))
        deficits = []
        for gi in range(4):
            v = float(np.var(arr[:, gi]))
            d = (1 - v/MATCHED_NULL[gi]) * 100
            deficits.append(d)
        grad = deficits[3] - deficits[0]
        is_heeg = 'YES' if disc in HEEGNER else ''
        print(f'{disc:>5}  {is_heeg:>7}  {len(arr):>5}  {mean_log_n:>9.2f}  {deficits[0]:+7.1f}  {deficits[1]:+7.1f}  {deficits[2]:+7.1f}  {deficits[3]:+7.1f}  {grad:+6.1f}')
        results.append({'disc': disc, 'heegner': disc in HEEGNER, 'n': len(arr),
                        'mean_log_N': mean_log_n, 'deficits': deficits, 'gradient': float(grad)})

    # Regression: deficit_gap1 ~ log|D| + log(mean conductor)
    print(f'\n=== Regression: gap1 deficit vs log|D| and log(mean conductor) ===')
    if len(results) >= 5:
        X = np.array([[np.log(abs(r['disc'])), r['mean_log_N'], 1.0] for r in results])
        y_g1 = np.array([r['deficits'][0] for r in results])
        y_g4 = np.array([r['deficits'][3] for r in results])
        for gi, y in [('gap1', y_g1), ('gap4', y_g4)]:
            coefs, *_ = np.linalg.lstsq(X, y, rcond=None)
            pred = X @ coefs
            resid = y - pred
            ss_res = float((resid**2).sum())
            ss_tot = float(((y - y.mean())**2).sum())
            r2 = 1 - ss_res/ss_tot if ss_tot > 0 else 0
            print(f'  {gi}: deficit = {coefs[0]:+.2f}*log|D| + {coefs[1]:+.2f}*log(N) + {coefs[2]:+.1f}  R^2={r2:.3f}')

        # Simple corr with |D|
        logD = np.array([np.log(abs(r['disc'])) for r in results])
        r_g1 = float(np.corrcoef(logD, y_g1)[0,1])
        r_g4 = float(np.corrcoef(logD, y_g4)[0,1])
        print(f'  Pearson(log|D|, gap1_deficit) = {r_g1:+.3f}')
        print(f'  Pearson(log|D|, gap4_deficit) = {r_g4:+.3f}')

    # Heegner vs non-Heegner summary
    heeg = [r for r in results if r['heegner']]
    nonh = [r for r in results if not r['heegner']]
    if heeg and nonh:
        hm = np.mean([r['deficits'][0] for r in heeg])
        nm = np.mean([r['deficits'][0] for r in nonh])
        print(f'\nHeegner mean gap1 deficit:     {hm:+.1f}%  (n disc groups = {len(heeg)})')
        print(f'non-Heegner mean gap1 deficit: {nm:+.1f}%  (n disc groups = {len(nonh)})')

    with open(OUT, 'w') as f:
        json.dump({'per_disc': results}, f, indent=2)
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
