"""Bootstrap significance check on Charon's F011 Sha split finding.

Claim: rank-0, Sha=1 curves show gap1 variance 0.1002 (n=604) vs Sha>1 gap1 variance
0.1278 (n=178). Is the difference significant under:
  (a) Bootstrap per-group
  (b) Permutation null (shuffle Sha-label across rank-0 curves)
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
import psycopg2

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')
GAUDIN = 0.178
SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'bsd_at_scale.json')
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'f011_sha_bootstrap.json')
N_PERMS = 10000


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


def main():
    bsd = json.load(open(SRC))
    curves = bsd['results']

    # Map iso -> origin, get zeros
    iso_origins = {}
    for c in curves:
        parts = c['label'].split('.')
        cond = parts[0]
        iso_letter = parts[1].rstrip('0123456789')
        iso_origins[f'{cond}.{iso_letter}'] = f'EllipticCurve/Q/{cond}/{iso_letter}'

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT origin, positive_zeros FROM lfunc_lfunctions
        WHERE origin = ANY(%s) AND positive_zeros IS NOT NULL
    """, (list(iso_origins.values()),))
    zeros_by_origin = {o: parse_zeros(z) for o, z in cur}

    # Build per-curve gap1, tagged with Sha group
    rank0_gap1 = []
    rank0_sha = []
    for c in curves:
        if c['rank'] != 0: continue
        parts = c['label'].split('.')
        cond = parts[0]
        iso_letter = parts[1].rstrip('0123456789')
        origin = f'EllipticCurve/Q/{cond}/{iso_letter}'
        zs = zeros_by_origin.get(origin)
        g = norm_gaps(zs)
        if g is None: continue
        rank0_gap1.append(float(g[0]))
        rank0_sha.append(float(c['sha_an']))

    rank0_gap1 = np.array(rank0_gap1)
    rank0_sha = np.array(rank0_sha)
    print(f'n rank-0 with zeros = {len(rank0_gap1)}')

    is_sha1 = np.abs(rank0_sha - 1.0) < 0.5
    is_shaG = rank0_sha > 1.5
    print(f'n Sha=1: {is_sha1.sum()}   n Sha>1: {is_shaG.sum()}')

    gap1_sha1 = rank0_gap1[is_sha1]
    gap1_shaG = rank0_gap1[is_shaG]

    var_sha1 = float(np.var(gap1_sha1))
    var_shaG = float(np.var(gap1_shaG))
    obs_diff = var_shaG - var_sha1
    print(f'Observed var(Sha=1) = {var_sha1:.6f}   var(Sha>1) = {var_shaG:.6f}   diff = {obs_diff:+.6f}')

    # Bootstrap per-group
    rng = np.random.default_rng(20260422)
    B = 10000
    boot_var_sha1 = np.empty(B)
    boot_var_shaG = np.empty(B)
    for b in range(B):
        boot_var_sha1[b] = np.var(rng.choice(gap1_sha1, len(gap1_sha1), replace=True))
        boot_var_shaG[b] = np.var(rng.choice(gap1_shaG, len(gap1_shaG), replace=True))
    ci_sha1 = (float(np.percentile(boot_var_sha1, 2.5)), float(np.percentile(boot_var_sha1, 97.5)))
    ci_shaG = (float(np.percentile(boot_var_shaG, 2.5)), float(np.percentile(boot_var_shaG, 97.5)))
    print(f'Bootstrap 95% CI Sha=1 var: [{ci_sha1[0]:.4f}, {ci_sha1[1]:.4f}]')
    print(f'Bootstrap 95% CI Sha>1 var: [{ci_shaG[0]:.4f}, {ci_shaG[1]:.4f}]')
    overlap = ci_sha1[1] >= ci_shaG[0]
    print(f'95% CIs OVERLAP: {overlap}')

    # Permutation null: shuffle Sha labels across rank-0 curves
    combined = np.concatenate([gap1_sha1, gap1_shaG])
    n1 = len(gap1_sha1)
    null_diffs = np.empty(N_PERMS)
    for i in range(N_PERMS):
        perm = rng.permutation(len(combined))
        gh = combined[perm[:n1]]
        gG = combined[perm[n1:]]
        null_diffs[i] = np.var(gG) - np.var(gh)
    p_two_sided = float(((np.abs(null_diffs) >= abs(obs_diff)).sum() + 1) / (N_PERMS + 1))
    null_mean = float(null_diffs.mean())
    null_std = float(null_diffs.std())
    z = (obs_diff - null_mean) / null_std if null_std > 0 else None
    print(f'\nPermutation null ({N_PERMS} perms):')
    print(f'  null mean(diff) = {null_mean:+.6f}   null std = {null_std:.6f}')
    print(f'  observed diff = {obs_diff:+.6f}   z = {z:.3f}   p (two-sided) = {p_two_sided:.4f}')

    verdict = 'DURABLE' if abs(z) >= 3 else ('MARGINAL' if abs(z) >= 2 else 'NULL_COVERS')
    print(f'  verdict: {verdict}')

    # Also do Levene-style test: variance equality F-test on raw gap1 values
    # (not exact for non-normal data but a sanity check)
    from scipy.stats import levene, bartlett
    W, p_lev = levene(gap1_sha1, gap1_shaG)
    print(f'\nLevene test: W={W:.3f}  p={p_lev:.4f}')
    B_stat, p_bart = bartlett(gap1_sha1, gap1_shaG)
    print(f'Bartlett test: T={B_stat:.3f}  p={p_bart:.4f}')

    out = {
        'n_rank0_with_zeros': int(len(rank0_gap1)),
        'n_sha_eq_1': int(is_sha1.sum()),
        'n_sha_gt_1': int(is_shaG.sum()),
        'observed': {
            'var_gap1_sha_eq_1': var_sha1,
            'var_gap1_sha_gt_1': var_shaG,
            'diff_gt_minus_eq': obs_diff,
        },
        'bootstrap_95ci': {
            'var_gap1_sha_eq_1': ci_sha1,
            'var_gap1_sha_gt_1': ci_shaG,
            'cis_overlap': bool(overlap),
        },
        'permutation_null': {
            'n_perms': N_PERMS,
            'null_mean_diff': null_mean,
            'null_std_diff': null_std,
            'z': float(z) if z is not None else None,
            'p_two_sided': p_two_sided,
            'verdict': verdict,
        },
        'levene': {'W': float(W), 'p': float(p_lev)},
        'bartlett': {'T': float(B_stat), 'p': float(p_bart)},
    }
    with open(OUT, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
