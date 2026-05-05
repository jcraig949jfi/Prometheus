"""CM vs non-CM large-sample F011 test (follow-up to BSD-1646 n=18 finding).

Pull all 2134 rank-0 CM EC with zeros + ~5000 matched non-CM rank-0 EC with zeros.
Compute gap1-4 variance (local-4-gap normalization) and compare to matched-GUE null.

Strengthens the CM-deficit finding with proper n.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
import psycopg2

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')
MATCHED_NULL = [0.1472, 0.1741, 0.1725, 0.1468]
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'f011_cm_large_sample.json')


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
    cm_rows = cur.fetchall()
    print(f'  CM: {len(cm_rows)}', flush=True)

    print('Fetching 5000 random non-CM rank-0 with zeros (conductor-matched strategy: full random)...', flush=True)
    cur.execute("""
        SELECT e.lmfdb_label, e.cm, e.conductor, l.positive_zeros
        FROM ec_curvedata e
        JOIN lfunc_lfunctions l
          ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso,'.',1)
                        || '/' || split_part(e.lmfdb_iso,'.',2)
        WHERE e.rank = '0' AND e.cm::int = 0
          AND l.positive_zeros IS NOT NULL
        ORDER BY random()
        LIMIT 5000
    """)
    noncm_rows = cur.fetchall()
    print(f'  nonCM: {len(noncm_rows)}', flush=True)

    # Compute gaps
    cm_gaps = []
    cm_cond = []
    cm_cm_disc = []
    for lab, cm, cond, z in cm_rows:
        zs = parse_zeros(z)
        g = norm_gaps(zs)
        if g is None: continue
        cm_gaps.append(g)
        cm_cond.append(int(cond))
        cm_cm_disc.append(int(cm))

    noncm_gaps = []
    noncm_cond = []
    for lab, cm, cond, z in noncm_rows:
        zs = parse_zeros(z)
        g = norm_gaps(zs)
        if g is None: continue
        noncm_gaps.append(g)
        noncm_cond.append(int(cond))

    cm_gaps = np.array(cm_gaps)
    noncm_gaps = np.array(noncm_gaps)
    print(f'\nCM n with gaps: {len(cm_gaps)},  nonCM n with gaps: {len(noncm_gaps)}')

    # Variance + bootstrap CI + deficits
    rng = np.random.default_rng(20260422)
    B = 5000

    def report(arr, tag):
        if len(arr) < 3:
            print(f'  {tag}: no data')
            return None
        print(f'\n=== {tag} (n={len(arr)}) ===')
        defs = []
        cis = []
        for gi in range(4):
            v = float(np.var(arr[:, gi]))
            d = (1 - v/MATCHED_NULL[gi]) * 100
            defs.append(d)
            boot_defs = np.empty(B)
            for b in range(B):
                s = rng.choice(len(arr), len(arr), replace=True)
                boot_defs[b] = (1 - np.var(arr[s, gi])/MATCHED_NULL[gi]) * 100
            ci = (float(np.percentile(boot_defs, 2.5)), float(np.percentile(boot_defs, 97.5)))
            cis.append(ci)
            print(f'  gap{gi+1}: var={v:.4f}  deficit=+{d:.1f}%  CI95=[{ci[0]:+.1f}, {ci[1]:+.1f}]')
        grad = defs[3] - defs[0]
        boots_grad = np.empty(B)
        for b in range(B):
            s = rng.choice(len(arr), len(arr), replace=True)
            g1_v = np.var(arr[s,0]); g4_v = np.var(arr[s,3])
            boots_grad[b] = (1 - g4_v/MATCHED_NULL[3]) * 100 - (1 - g1_v/MATCHED_NULL[0]) * 100
        grad_ci = (float(np.percentile(boots_grad, 2.5)), float(np.percentile(boots_grad, 97.5)))
        print(f'  gradient (gap4 - gap1): {grad:+.1f}  CI95=[{grad_ci[0]:+.1f}, {grad_ci[1]:+.1f}]')
        return {'defs': defs, 'cis': cis, 'grad': float(grad), 'grad_ci': grad_ci, 'n': len(arr)}

    cm_res = report(cm_gaps, 'CM rank-0')
    nc_res = report(noncm_gaps, 'non-CM rank-0')

    # Permutation: pool all, split randomly
    combined = np.concatenate([cm_gaps, noncm_gaps])
    n_cm = len(cm_gaps)
    obs_diffs = [cm_res['defs'][i] - nc_res['defs'][i] for i in range(4)]
    null_diffs = np.empty((5000, 4))
    for i in range(5000):
        perm = rng.permutation(len(combined))
        a = combined[perm[:n_cm]]; b = combined[perm[n_cm:]]
        for gi in range(4):
            null_diffs[i, gi] = (1 - np.var(a[:,gi])/MATCHED_NULL[gi])*100 - (1 - np.var(b[:,gi])/MATCHED_NULL[gi])*100
    print(f'\nPermutation null (5K perms): CM vs nonCM deficit DIFFERENCE per gap:')
    for gi in range(4):
        obs = obs_diffs[gi]
        p = ((np.abs(null_diffs[:,gi]) >= abs(obs)).sum() + 1) / 5001
        z = obs / null_diffs[:,gi].std() if null_diffs[:,gi].std() > 0 else None
        print(f'  gap{gi+1}: obs diff = {obs:+.1f}  z={z:.2f}  p={p:.4f}')

    # CM sub-split by CM discriminant
    print(f'\nCM curve breakdown by CM disc:')
    from collections import Counter
    cmdisc_counts = Counter(cm_cm_disc)
    for disc, cnt in cmdisc_counts.most_common(6):
        mask = np.array(cm_cm_disc) == disc
        if mask.sum() < 20: continue
        arr = cm_gaps[mask]
        g1_def = (1 - np.var(arr[:,0])/MATCHED_NULL[0]) * 100
        g4_def = (1 - np.var(arr[:,3])/MATCHED_NULL[3]) * 100
        print(f'  CM disc = {disc}:  n={mask.sum()}  gap1={g1_def:+.1f}%  gap4={g4_def:+.1f}%')

    out = {
        'n_cm': int(len(cm_gaps)),
        'n_noncm': int(len(noncm_gaps)),
        'cm': cm_res,
        'noncm': nc_res,
        'obs_diffs': [float(x) for x in obs_diffs],
    }
    with open(OUT, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
