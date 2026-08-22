"""CAMPAIGN X pass 3 — MECHANISM DIAGNOSTIC, run AFTER the terminal state was
computed and written to retrieval_frozen_results.json.

This cannot change the verdict and is not permitted to: D1-D5 were adjudicated,
the confound rule applied, and REDESIGN recorded, all before this file ran. Its
only job is to name the deficit precisely enough for a successor campaign, which
is what a REDESIGN terminal state owes.

THE QUESTION: L1 top-1 on the trivial `shift` control is 1/10 on frozen, far
WORSE than the four real operators at 33/40. That is backwards if L1 misses were
simply a resolution limit — shift targets are nearly identical to their queries
and should be the easiest of all. The obvious competing explanation is that the
SOURCE SEQUENCE ITSELF is in the retrieval pool, and for shift the source is a
near-perfect match for the shifted image, so the source outranks the true target.
If so, a large share of "signature collisions" are a benchmark construction
artifact, not a representational deficit — and the two demand different fixes.

For each frozen L1 miss: what actually occupied rank 1, and where did the source
rank?
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
from collections import Counter

import numpy as np

SEARCH = pathlib.Path(r'F:\Prometheus\aporia\search')
spec = importlib.util.spec_from_file_location('rd', SEARCH / 'run_retrieval_dev.py')
rd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rd)

pairs, split = rd.pairs, rd.split
pool, idx_of, SIGZ, mu, sd = rd.pool, rd.idx_of, rd.SIGZ, rd.mu, rd.sd
ids = rd.ids
FROZEN = sorted(split['frozen_indices'])

rows = []
for i in FROZEN:
    p = pairs['positives'][i]
    src, tgt, op = p['src'], p['tgt'], p['op']
    if src not in pool or tgt not in pool:
        continue
    ti, si = idx_of[tgt], idx_of[src]
    img = rd.OPS[op](pool[src])[p['offset']:]
    q = np.nan_to_num(rd.signature(img)); q = (q - mu) / sd
    d = np.linalg.norm(SIGZ - q, axis=1)
    order = np.argsort(d, kind='stable')
    r_tgt = int(np.where(order == ti)[0][0]) + 1
    if r_tgt == 1:
        continue
    r_src = int(np.where(order == si)[0][0]) + 1
    top1_id = ids[order[0]]
    rows.append({'op': op, 'target_rank': r_tgt, 'source_rank': r_src,
                 'source_beat_target': r_src < r_tgt,
                 'rank1_is_source': top1_id == src,
                 'rank1_is_benchmark_seq': not top1_id.startswith('D'),
                 'rank1_is_distractor': top1_id.startswith('D')})

n = len(rows)
src_beat = sum(r['source_beat_target'] for r in rows)
r1_src = sum(r['rank1_is_source'] for r in rows)
r1_dis = sum(r['rank1_is_distractor'] for r in rows)
by_op = Counter(r['op'] for r in rows)
src_beat_by_op = Counter(r['op'] for r in rows if r['source_beat_target'])

out = {'frozen_L1_misses': n,
       'source_ranked_above_target': {'count': src_beat, 'rate': round(src_beat / max(n, 1), 4)},
       'rank1_was_the_source_itself': {'count': r1_src, 'rate': round(r1_src / max(n, 1), 4)},
       'rank1_was_an_unrelated_distractor': {'count': r1_dis, 'rate': round(r1_dis / max(n, 1), 4)},
       'misses_by_op': dict(by_op),
       'source_beat_target_by_op': dict(src_beat_by_op),
       'detail': rows,
       'interpretation_rule': (
           'misses where the SOURCE outranks the target are a benchmark-construction artifact '
           '(the query is derived from an object that is itself in the pool); misses where an '
           'UNRELATED DISTRACTOR takes rank 1 are genuine representational collisions. These '
           'require different fixes and must not be pooled.'),
       'note': 'Diagnostic only. Run AFTER the terminal state was computed and written. '
               'Changes no verdict.'}
(SEARCH / 'l1_miss_diagnosis.json').write_text(json.dumps(out, indent=1), encoding='utf-8')

print(f"frozen L1 misses: {n}")
print(f"  source outranked target      : {src_beat}/{n}")
print(f"  rank-1 WAS the source itself : {r1_src}/{n}")
print(f"  rank-1 was unrelated distractor: {r1_dis}/{n}   <-- genuine collisions")
print(f"  misses by op                 : {dict(by_op)}")
print(f"  source-beat-target by op     : {dict(src_beat_by_op)}")
