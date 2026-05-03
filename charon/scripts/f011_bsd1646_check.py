"""F011 multi-gap deficit check on Charon's 1646 BSD curves (Ergon request).

Reproduce Ergon's result:
  EC rank-0: gap1 deficit +33.9%, gap2 +16.9%, gap3 +24.7%, gap4 +44.4%
  MF rank-0: gap1 +1.4%, gap2 +0.9%, gap3 +14.2%, gap4 +33.8%

On our 1646 BSD-verified curves, split by Sha=1 vs Sha>1 (Ergon's secondary ask).
Mean-spacing unfolded; report variance / Gaudin_GUE = 4 - pi.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
import psycopg2

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')
GAUDIN_GUE = 0.178  # GUE NN spacing variance after mean-1 unfolding

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'bsd_at_scale.json')


def parse_zeros(z_str):
    if not z_str: return None
    try:
        if isinstance(z_str, str):
            z = [float(x) for x in z_str.strip('[]').split(',') if x.strip()]
        else:
            z = [float(x) for x in z_str]
        return np.array(sorted([x for x in z if x > 0]))
    except Exception:
        return None


def unfold_and_gaps(zs):
    """Per-Ergon: use first 5 zeros, mean over first 4 gaps for normalization."""
    if zs is None or len(zs) < 5: return None
    z5 = np.sort(zs)[:5]
    gaps = np.diff(z5)  # 4 gaps
    mean_gap = gaps.mean()
    if mean_gap <= 0: return None
    return gaps / mean_gap


def main():
    bsd = json.load(open(SRC))
    curves = bsd['results']
    print(f'Loaded {len(curves)} BSD curves')

    # Build iso class -> {sha, rank, label}
    iso_map = {}
    for c in curves:
        label = c['label']  # e.g. "8601.b2"
        iso = '.'.join(label.split('.')[:2]).rsplit('.', 1)  # "8601.b"
        # Actually label is "cond.iso_letter[number]". iso key is cond.iso_letter
        parts = label.split('.')
        cond = parts[0]
        iso_letter = parts[1].rstrip('0123456789')
        iso = f'{cond}.{iso_letter}'
        iso_map.setdefault(iso, []).append(c)

    print(f'Unique iso classes: {len(iso_map)}')

    # Build L-function origin keys
    origin_keys = [f'EllipticCurve/Q/{iso.split(".")[0]}/{iso.split(".")[1]}' for iso in iso_map]

    # Pull zeros
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT origin, positive_zeros
        FROM lfunc_lfunctions
        WHERE origin = ANY(%s)
          AND positive_zeros IS NOT NULL
    """, (origin_keys,))
    origin_zeros = {}
    for origin, z in cur:
        origin_zeros[origin] = parse_zeros(z)
    print(f'Pulled zeros for {len(origin_zeros)} iso classes')

    # Compute gaps per curve, group by Sha=1 vs Sha>1
    rows_all = []    # list of {sha, rank, conductor, gaps (4 floats)}
    for iso, curve_list in iso_map.items():
        cond, iso_letter = iso.split('.')
        origin = f'EllipticCurve/Q/{cond}/{iso_letter}'
        zs = origin_zeros.get(origin)
        gaps = unfold_and_gaps(zs)
        if gaps is None: continue
        for c in curve_list:
            rows_all.append({
                'label': c['label'],
                'rank': c['rank'],
                'conductor': c['conductor'],
                'sha': c['sha_an'],
                'gaps': gaps,
            })
    print(f'Curves with 5+ zeros: {len(rows_all)}')

    def variance_ratio(rows, gap_idx):
        vals = [r['gaps'][gap_idx] for r in rows]
        if len(vals) < 10: return None, None
        v = np.var(vals)  # ddof=0, matching Ergon
        return float(v), float(v / GAUDIN_GUE)

    # Split: all, rank=0, Sha=1, Sha>1
    def report(label, rows):
        if not rows:
            print(f'  {label}: no data')
            return None
        print(f'\n=== {label} (n={len(rows)}) ===')
        results = {'n': len(rows), 'gaps': {}}
        for i in range(4):
            v, ratio = variance_ratio(rows, i)
            if v is None:
                continue
            deficit = 1 - ratio
            print(f'  gap{i+1}: var={v:.4f}  ratio={ratio:.4f}  deficit=+{deficit*100:.1f}%')
            results['gaps'][f'gap{i+1}'] = {'var': v, 'ratio': ratio, 'deficit_pct': deficit * 100}
        return results

    rank0 = [r for r in rows_all if r['rank'] == 0]
    rank1 = [r for r in rows_all if r['rank'] == 1]
    rank_ge2 = [r for r in rows_all if r['rank'] >= 2]
    sha_eq_1_rank0 = [r for r in rank0 if abs(r['sha'] - 1.0) < 0.5]
    sha_gt_1_rank0 = [r for r in rank0 if r['sha'] > 1.5]

    out = {'context': 'F011 multi-gap check on Charon 1646 BSD curves vs Ergon report',
           'gaudin_GUE': GAUDIN_GUE,
           'total_with_zeros': len(rows_all)}
    out['all_ranks'] = report('ALL RANKS', rows_all)
    out['rank_0'] = report('RANK 0', rank0)
    out['rank_1'] = report('RANK 1', rank1)
    out['rank_ge2'] = report('RANK >= 2', rank_ge2)
    out['rank0_sha_eq_1'] = report('RANK 0, Sha = 1', sha_eq_1_rank0)
    out['rank0_sha_gt_1'] = report('RANK 0, Sha > 1', sha_gt_1_rank0)

    # Dominant-Sha view: Sha distribution
    shas = [r['sha'] for r in rank0]
    from collections import Counter
    sha_counts = Counter(int(round(s)) for s in shas)
    print(f'\nRank-0 Sha distribution: {dict(sha_counts.most_common(10))}')
    out['rank0_sha_distribution'] = dict(sha_counts.most_common(20))

    out_path = os.path.join(os.path.dirname(SRC), 'f011_bsd1646_check.json')
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'\n[saved] {out_path}')


if __name__ == '__main__':
    main()
