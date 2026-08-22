"""CAMPAIGN X pass 3/3 — THE TERMINAL PASS. The frozen split is touched ONCE.

The signature is NOT redefined here. This script IMPORTS run_retrieval_dev.py and
calls its `signature`, its pool construction, its normalisation constants and its
`rank_of` — so the representation and metric are byte-identical to pass 2 by
construction, not by my assertion. Nothing in this file changes a feature, a
weight, a distance, or a pool member.

What is computed on the 50 FROZEN positives:
  L0  operator-aware exact          (circular ceiling / sanity)
  L1  operator-aware signature      (NECESSARY condition; collision rate)
  L2  operator-agnostic signature   (THE SUBSTRATE CLAIM)
  baselines: raw-term NN, shuffled signature, growth/magnitude-only
  per-operator decomposition with the trivial `shift` control SEPARATED
  matched-negative false-retrieval rate

Then D1-D5 are adjudicated exactly as preregistered in
BENCHMARK_blinded_relations.md, read FIRST and unmodified; and only after that
the supplementary confound rule pre-committed in RETRIEVAL_dev_2026-08-22.md
(written before frozen was ever touched) is applied.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib

import numpy as np

SEARCH = pathlib.Path(r'F:\Prometheus\aporia\search')
spec = importlib.util.spec_from_file_location('rd', SEARCH / 'run_retrieval_dev.py')
rd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rd)          # identical pool, identical signatures, identical seeds

pairs, split = rd.pairs, rd.split
pool, idx_of, SIGZ, RAWZ, GM, SHUF = rd.pool, rd.idx_of, rd.SIGZ, rd.RAWZ, rd.GM, rd.SHUF
mu, sd = rd.mu, rd.sd
FROZEN = sorted(split['frozen_indices'])
print(f"\n=== FROZEN SPLIT TOUCHED (once): {len(FROZEN)} positives, pool {len(pool):,} ===", flush=True)

neg_by_src = {}
for n in pairs['negatives']:
    neg_by_src.setdefault((n['op'], n['src']), []).append(n['decoy'])

lvls = {k: [] for k in ('L1_sig', 'L2_agnostic', 'B_raw', 'B_shuf', 'B_growthmag')}
by_op = {k: {} for k in lvls}
l0_hits = 0
l1_misses = []
fr = {'sig_n': 0, 'sig_bad': 0, 'raw_n': 0, 'raw_bad': 0}

for i in FROZEN:
    p = pairs['positives'][i]
    src, tgt, op = p['src'], p['tgt'], p['op']
    if src not in pool or tgt not in pool:
        continue
    ti, si = idx_of[tgt], idx_of[src]
    img = rd.OPS[op](pool[src])[p['offset']:]
    l0_hits += int(len(img) >= 12 and pool[tgt][:12] == img[:12])

    q1 = np.nan_to_num(rd.signature(img)); q1 = (q1 - mu) / sd
    r1 = rd.rank_of(q1, SIGZ, ti)
    if r1 > 1:
        l1_misses.append({'op': op, 'rank': r1})
    ranks = {'L1_sig': r1,
             'L2_agnostic': rd.rank_of(SIGZ[si], SIGZ, ti),
             'B_raw': rd.rank_of(RAWZ[si], RAWZ, ti),
             'B_shuf': rd.rank_of(SHUF[si], SHUF, ti),
             'B_growthmag': rd.rank_of(GM[si], GM, ti)}
    for k, r in ranks.items():
        lvls[k].append(r)
        by_op[k].setdefault(op, []).append(r)

    decoys = [d for d in neg_by_src.get((op, src), []) if d in pool]
    if decoys:
        d0 = idx_of[decoys[0]]
        fr['sig_n'] += 1
        fr['sig_bad'] += int(np.linalg.norm(SIGZ[d0] - SIGZ[si]) < np.linalg.norm(SIGZ[ti] - SIGZ[si]))
        fr['raw_n'] += 1
        fr['raw_bad'] += int(np.linalg.norm(RAWZ[d0] - RAWZ[si]) < np.linalg.norm(RAWZ[ti] - RAWZ[si]))

def summ(rs):
    a = np.array(rs, dtype=float)
    return {'n': int(len(a)), 'top1_count': int((a == 1).sum()), 'top1': round(float((a == 1).mean()), 4),
            'top10_count': int((a <= 10).sum()), 'top10': round(float((a <= 10).mean()), 4),
            'top100': round(float((a <= 100).mean()), 4), 'mrr': round(float((1 / a).mean()), 4),
            'median_rank': float(np.median(a))}

N = len(lvls['L1_sig'])
res = {'frozen_pairs_scored': N, 'pool_size': len(pool),
       'chance_top10': round(10 / len(pool), 6),
       'L0_exact_ceiling': {'hits': l0_hits, 'n': N},
       'levels': {k: summ(v) for k, v in lvls.items()},
       'per_operator': {k: {op: summ(r) for op, r in v.items()} for k, v in by_op.items()}}

nontrivial = [r for op, v in by_op['L2_agnostic'].items() if op != 'shift' for r in v]
shiftr = by_op['L2_agnostic'].get('shift', [])
res['L2_nontrivial_only'] = summ(nontrivial)
res['L2_shift_control'] = summ(shiftr) if shiftr else {}
l1_nontrivial = [r for op, v in by_op['L1_sig'].items() if op != 'shift' for r in v]
res['L1_nontrivial_only'] = summ(l1_nontrivial)
res['matched_negative_false_retrieval'] = {
    'signature': {'n': fr['sig_n'], 'decoy_above_target': fr['sig_bad'],
                  'rate': round(fr['sig_bad'] / max(fr['sig_n'], 1), 4)},
    'raw_terms': {'n': fr['raw_n'], 'decoy_above_target': fr['raw_bad'],
                  'rate': round(fr['raw_bad'] / max(fr['raw_n'], 1), 4)},
    'chance': 0.5}
res['L1_collisions'] = {'misses': len(l1_misses), 'n': N,
                        'rate': round(len(l1_misses) / max(N, 1), 4), 'detail': l1_misses}

# ---------------------------------------------------------- ADJUDICATION
# D1-D5 read FIRST, exactly as preregistered, before any supplementary rule.
L1, L2 = res['levels']['L1_sig'], res['levels']['L2_agnostic']
L2nt, L2sh = res['L2_nontrivial_only'], res['L2_shift_control']
RAW, SH = res['levels']['B_raw'], res['levels']['B_shuf']
dev = json.loads((SEARCH / 'retrieval_dev_results.json').read_text(encoding='utf-8'))
dev_l2 = dev['levels']['L2_agnostic']['top10']

D = {}
D['D1_signature_beats_both_baselines'] = bool(
    L2['top10'] > RAW['top10'] and L2['top10'] > SH['top10'] and L2nt['top10'] > 0.3)
D['D2_raw_terms_equal'] = bool(abs(L2['top10'] - RAW['top10']) <= 0.05)
D['D3_dev_works_frozen_fails'] = bool(dev_l2 >= 0.30 and L2['top10'] < 0.15)
D['D4_only_shift_retrieves'] = bool(
    (L2sh.get('top10', 0) >= 0.5) and L2nt['top10'] < 0.20)
D['D5_nothing_retrieves'] = bool(L2['top10'] <= res['chance_top10'] * 20)
res['D_branches'] = D
fired = [k for k, v in D.items() if v]
res['D_branches_fired'] = fired

# ---------------------------------------------------------- SUPPLEMENT (pre-committed)
l1_top1 = L1['top1']
if l1_top1 >= 0.95:
    res['confound_rule'] = {'branch': 'CLEAN', 'frozen_L1_top1': l1_top1,
        'meaning': 'the instrument resolves its own targets; the L2 read is a clean verdict on the substrate claim'}
else:
    res['confound_rule'] = {'branch': 'CONFOUNDED', 'frozen_L1_top1': l1_top1,
        'meaning': 'the instrument cannot reliably retrieve targets it is exactly equal to; any D4/D5 verdict is '
                   'confounded by instrument resolution and may not be issued as a KILL'}

if res['confound_rule']['branch'] == 'CONFOUNDED' and (D['D4_only_shift_retrieves'] or D['D5_nothing_retrieves']):
    res['TERMINAL'] = 'REDESIGN'
elif D['D1_signature_beats_both_baselines']:
    res['TERMINAL'] = 'ADVANCE'
elif D['D3_dev_works_frozen_fails']:
    res['TERMINAL'] = 'REDESIGN'
elif D['D5_nothing_retrieves']:
    res['TERMINAL'] = 'KILL'
else:
    res['TERMINAL'] = 'REDESIGN'

(SEARCH / 'retrieval_frozen_results.json').write_text(json.dumps(res, indent=1), encoding='utf-8')

print(f"\nL0 exact ceiling: {l0_hits}/{N} (circular)")
for k in ('L1_sig', 'L2_agnostic', 'B_raw', 'B_shuf', 'B_growthmag'):
    s = res['levels'][k]
    print(f"{k:14s} top1={s['top1_count']}/{s['n']}={s['top1']:.3f}  top10={s['top10_count']}/{s['n']}={s['top10']:.3f}  "
          f"MRR={s['mrr']:.4f}  median={s['median_rank']:.0f}")
print(f"\nL2 shift control  : top10 {L2sh.get('top10_count','-')}/{L2sh.get('n','-')} = {L2sh.get('top10','-')}  median {L2sh.get('median_rank','-')}")
print(f"L2 four real ops  : top10 {L2nt['top10_count']}/{L2nt['n']} = {L2nt['top10']}  median {L2nt['median_rank']}")
print(f"L1 four real ops  : top1  {res['L1_nontrivial_only']['top1_count']}/{res['L1_nontrivial_only']['n']} = {res['L1_nontrivial_only']['top1']}")
print("\nper-operator L2 top10:", {op: f"{summ(r)['top10_count']}/{summ(r)['n']}" for op, r in by_op['L2_agnostic'].items()})
print("per-operator L1 top1 :", {op: f"{summ(r)['top1_count']}/{summ(r)['n']}" for op, r in by_op['L1_sig'].items()})
print(f"\nmatched-negative FR: signature {fr['sig_bad']}/{fr['sig_n']} = {res['matched_negative_false_retrieval']['signature']['rate']}, "
      f"raw {fr['raw_bad']}/{fr['raw_n']} = {res['matched_negative_false_retrieval']['raw_terms']['rate']}, chance 0.5")
print(f"L1 collisions: {len(l1_misses)}/{N} = {res['L1_collisions']['rate']}")
print(f"\nD-branches fired: {fired}")
print(f"confound rule  : {res['confound_rule']['branch']} (frozen L1 top-1 = {l1_top1})")
print(f"\n*** CAMPAIGN X TERMINAL: {res['TERMINAL']} ***")
