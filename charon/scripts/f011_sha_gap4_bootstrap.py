"""Per Aporia: bootstrap Sha=1 vs Sha>1 at gap4, not gap1.

Context (Aporia 2026-04-22 synth):
  gap1 variance deficit is finite-N artifact (Ergon GUE N=100 sim).
  gap4 deficit is the real F011 residual.
  Test: does Charon's Sha-split survive at gap4?
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
import psycopg2
from scipy.stats import levene, bartlett

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')
SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'bsd_at_scale.json')
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'f011_sha_gap4_bootstrap.json')
N_PERMS = 10000
BOOT = 10000


def parse_zeros(s):
    if not s: return None
    try:
        vals = json.loads(s) if isinstance(s, str) else s
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


def bootstrap_ci(x, B, rng, fn=np.var):
    vals = np.empty(B)
    for b in range(B):
        vals[b] = fn(rng.choice(x, len(x), replace=True))
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def permutation_null(x1, x2, n_perms, rng):
    combined = np.concatenate([x1, x2])
    n1 = len(x1)
    obs = np.var(x2) - np.var(x1)
    null = np.empty(n_perms)
    for i in range(n_perms):
        perm = rng.permutation(len(combined))
        null[i] = np.var(combined[perm[n1:]]) - np.var(combined[perm[:n1]])
    p = float(((np.abs(null) >= abs(obs)).sum() + 1) / (n_perms + 1))
    return obs, null, p


def main():
    bsd = json.load(open(SRC))
    curves = bsd['results']
    iso_origins = {}
    for c in curves:
        parts = c['label'].split('.')
        cond = parts[0]
        iso_letter = parts[1].rstrip('0123456789')
        iso_origins[f'{cond}.{iso_letter}'] = f'EllipticCurve/Q/{cond}/{iso_letter}'

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("SELECT origin, positive_zeros FROM lfunc_lfunctions WHERE origin = ANY(%s) AND positive_zeros IS NOT NULL",
                (list(iso_origins.values()),))
    zeros_by_origin = {o: parse_zeros(z) for o, z in cur}

    # Pull rank-0 gap1..gap4 + Sha
    rank0_gaps = []  # list of 4-arrays
    rank0_sha = []
    for c in curves:
        if c['rank'] != 0: continue
        parts = c['label'].split('.')
        cond = parts[0]
        iso_letter = parts[1].rstrip('0123456789')
        zs = zeros_by_origin.get(f'EllipticCurve/Q/{cond}/{iso_letter}')
        g = norm_gaps(zs)
        if g is None: continue
        rank0_gaps.append(g)
        rank0_sha.append(float(c['sha_an']))

    rank0_gaps = np.array(rank0_gaps)  # shape (n, 4)
    rank0_sha = np.array(rank0_sha)
    is_sha1 = np.abs(rank0_sha - 1.0) < 0.5
    is_shaG = rank0_sha > 1.5

    rng = np.random.default_rng(20260422)
    out = {'n_sha_eq_1': int(is_sha1.sum()), 'n_sha_gt_1': int(is_shaG.sum()),
           'per_gap': {}}
    print(f'n Sha=1 = {is_sha1.sum()}   n Sha>1 = {is_shaG.sum()}')

    for gi in range(4):
        g = rank0_gaps[:, gi]
        g1 = g[is_sha1]
        gG = g[is_shaG]
        var1 = float(np.var(g1))
        varG = float(np.var(gG))
        ci1 = bootstrap_ci(g1, BOOT, rng)
        ciG = bootstrap_ci(gG, BOOT, rng)
        obs_diff, null_diffs, p = permutation_null(g1, gG, N_PERMS, rng)
        z = float(obs_diff / null_diffs.std()) if null_diffs.std() > 0 else None
        lev_W, lev_p = levene(g1, gG)
        overlap = ci1[1] >= ciG[0]
        verdict = 'DURABLE' if z is not None and abs(z) >= 3 else ('MARGINAL' if z is not None and abs(z) >= 2 else 'NULL_COVERS')
        print(f'  gap{gi+1}: var(Sha=1)={var1:.4f} [{ci1[0]:.4f}, {ci1[1]:.4f}]  var(Sha>1)={varG:.4f} [{ciG[0]:.4f}, {ciG[1]:.4f}]')
        print(f'         diff={obs_diff:+.4f}  z={z:.3f}  p={p:.4f}  Levene p={lev_p:.4f}  CI_overlap={overlap}  -> {verdict}')
        out['per_gap'][f'gap{gi+1}'] = {
            'var_sha_eq_1': var1, 'var_sha_gt_1': varG,
            'ci95_sha_eq_1': ci1, 'ci95_sha_gt_1': ciG,
            'cis_overlap': bool(overlap),
            'obs_diff': float(obs_diff),
            'z': z,
            'p_permutation': p,
            'levene_p': float(lev_p),
            'verdict': verdict,
        }

    with open(OUT, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()
