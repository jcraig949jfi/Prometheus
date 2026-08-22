"""CAMPAIGN X pass 2, supplement — the two preregistered metrics the first
run did not produce, plus the control-removal read.

  (a) MATCHED-NEGATIVE FALSE-RETRIEVAL RATE: for each development positive that
      has a matched decoy (same growth class, within one order of magnitude and
      8 terms of length), does the signature rank the DECOY above the TRUE
      TARGET? This was preregistered and is the metric that cannot be gamed by
      pool size — it is a head-to-head between two objects chosen to look alike.

  (b) L2 WITH THE TRIVIAL CONTROL REMOVED: `shift` was built in deliberately as
      a control, because B = A shifted by one is nearly the same object. Any
      aggregate L2 number that includes shift is inflated by construction. The
      honest L2 read is the four non-trivial operators.

  (c) L1 MISS ANATOMY: L1 signatures a sequence that is exactly equal to the
      target over >= 20 terms and asks it to find that target. Every L1 miss is
      therefore a signature COLLISION — a case where the representation cannot
      distinguish the right answer from a distractor even when handed it. That
      is a direct measurement of representational resolution, and it is more
      informative than the recall number itself.

FROZEN SPLIT UNTOUCHED. No D-branch adjudicated.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

SEARCH = pathlib.Path(r'F:\Prometheus\aporia\search')
sys.path.insert(0, str(SEARCH))

# reuse the pass-2 machinery verbatim by importing it as a module
import importlib.util
spec = importlib.util.spec_from_file_location('rd', SEARCH / 'run_retrieval_dev.py')
rd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rd)          # recomputes pool + signatures (deterministic seeds)

pairs, split = rd.pairs, rd.split
DEV, pool, idx_of, SIGZ, RAWZ = rd.DEV, rd.pool, rd.idx_of, rd.SIGZ, rd.RAWZ
mu, sd = rd.mu, rd.sd

# ------------------------------------------------- (a) matched negatives
# negatives are keyed by (op, src); attach each to its positive
neg_by_src = {}
for n in pairs['negatives']:
    neg_by_src.setdefault((n['op'], n['src']), []).append(n['decoy'])

def d(v, i):
    return float(np.linalg.norm(SIGZ[i] - v))

fr_sig = {'n': 0, 'decoy_beats_target': 0}
fr_raw = {'n': 0, 'decoy_beats_target': 0}
l1_miss_ops = {}
l2_by_op = {}
for i in DEV:
    p = pairs['positives'][i]
    src, tgt, op = p['src'], p['tgt'], p['op']
    if src not in pool or tgt not in pool:
        continue
    decoys = [x for x in neg_by_src.get((op, src), []) if x in pool]
    if decoys:
        dec = decoys[0]
        q = SIGZ[idx_of[src]]
        fr_sig['n'] += 1
        fr_sig['decoy_beats_target'] += int(d(q, idx_of[dec]) < d(q, idx_of[tgt]))
        qr = RAWZ[idx_of[src]]
        dr = lambda j: float(np.linalg.norm(RAWZ[j] - qr))
        fr_raw['n'] += 1
        fr_raw['decoy_beats_target'] += int(dr(idx_of[dec]) < dr(idx_of[tgt]))
    # L2 rank by operator
    r2 = rd.rank_of(SIGZ[idx_of[src]], SIGZ, idx_of[tgt])
    l2_by_op.setdefault(op, []).append(r2)
    # L1 miss anatomy
    img = rd.OPS[op](pool[src])[p['offset']:]
    q1 = np.nan_to_num(rd.signature(img)); q1 = (q1 - mu) / sd
    r1 = rd.rank_of(q1, SIGZ, idx_of[tgt])
    if r1 > 1:
        l1_miss_ops.setdefault(op, []).append(r1)

nontrivial = {op: v for op, v in l2_by_op.items() if op != 'shift'}
flat = np.array([r for v in nontrivial.values() for r in v])
shift = np.array(l2_by_op.get('shift', [1e9]))

out = {
 'matched_negative_false_retrieval': {
   'signature': {'n': fr_sig['n'], 'decoy_ranked_above_target': fr_sig['decoy_beats_target'],
                 'rate': round(fr_sig['decoy_beats_target'] / max(fr_sig['n'], 1), 4)},
   'raw_terms': {'n': fr_raw['n'], 'decoy_ranked_above_target': fr_raw['decoy_beats_target'],
                 'rate': round(fr_raw['decoy_beats_target'] / max(fr_raw['n'], 1), 4)},
   'chance': 0.5},
 'L2_nontrivial_only': {'n': int(len(flat)), 'top1': round(float((flat == 1).mean()), 4),
                        'top10': round(float((flat <= 10).mean()), 4),
                        'top100': round(float((flat <= 100).mean()), 4),
                        'mrr': round(float((1 / flat).mean()), 4),
                        'median_rank': float(np.median(flat)),
                        'chance_top10_in_pool': round(10 / len(pool), 6)},
 'L2_shift_control': {'n': int(len(shift)), 'top10': round(float((shift <= 10).mean()), 4),
                      'median_rank': float(np.median(shift))},
 'L1_miss_anatomy': {'total_misses': int(sum(len(v) for v in l1_miss_ops.values())),
                     'by_op': {k: {'n': len(v), 'median_rank_when_missed': float(np.median(v))}
                               for k, v in l1_miss_ops.items()},
                     'meaning': 'every L1 miss is a signature COLLISION: the query is exactly '
                                'equal to the target over >=20 terms and a distractor still ranks closer'},
 'note': 'DEVELOPMENT ONLY. Frozen split untouched. No D-branch adjudicated.'}

(SEARCH / 'retrieval_dev_supplement.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print(json.dumps(out, indent=1))
