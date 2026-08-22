"""CAMPAIGN X-2 pass 2 — OBLIGATION 1: is the benchmark's ground truth unique?

Run BEFORE any attempt to buy more resolution, because more features cannot fix a
benchmark whose correct answer is not unique.

THE HYPOTHESIS (from pass 1): for a near-identity operator like `shift`, op(A) is
A with one term dropped, and OEIS holds many sequences that are near-shifts or
variants of one another. If several pool objects satisfy the SAME relation to the
same source, then a retrieval that returns one of them is CORRECT, and scoring it
against the single recorded target counts a right answer as a collision.

MEASURED DIRECTLY, not inferred from rank-1 alone: for every development pair,
enumerate ALL pool objects that agree with op(src) over >= 20 overlapping terms at
either offset — the same exactness rule the builder used to certify the recorded
pair in the first place. That set is the query's true answer set. Anything in it
is as valid as the recorded target, by the benchmark's own definition.

Then L1 is scored two ways, side by side and auditable:
    STRICT     rank-1 is the RECORDED target        (the pass-1 rule)
    ANY-VALID  rank-1 is ANY member of the answer set

The representation is imported from x2_entry_gate.py unchanged — same features,
same whitening, same pool, same seeds — so nothing here can be attributed to a
representation change.

NO L2 COMPUTATION APPEARS IN THIS FILE.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
from collections import defaultdict

import numpy as np

SEARCH = pathlib.Path(r'F:\Prometheus\aporia\search')
spec = importlib.util.spec_from_file_location('xg', SEARCH / 'x2_entry_gate.py')
xg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xg)

pool, ids, idx_of = xg.pool, xg.ids, xg.idx_of
pairs, DEV, OPS = xg.pairs, xg.DEV, xg.OPS
HASH_K, MIN_EXACT = 12, 20

# candidate index over the retrieval pool, same key length the builder used
index = defaultdict(list)
for k, v in pool.items():
    if len(v) >= HASH_K:
        index[tuple(v[:HASH_K])].append(k)

def overlap(a, b):
    n, i = min(len(a), len(b)), 0
    while i < n and a[i] == b[i]:
        i += 1
    return i

def valid_partners(src, op):
    """Every pool object satisfying op(src) exactly over >= MIN_EXACT terms."""
    try:
        img0 = OPS[op](pool[src])
    except (ValueError, OverflowError):
        return set()
    out = set()
    for drop in (0, 1):
        im = img0[drop:]
        if len(im) < HASH_K:
            continue
        for cid in index.get(tuple(im[:HASH_K]), ()):
            if cid == src:
                continue
            if overlap(im, pool[cid]) >= MIN_EXACT:
                out.add(cid)
    return out

print("\n=== OBLIGATION 1: enumerating answer sets ===", flush=True)
Zbest, Wbest = xg.W2c, xg.W2          # V2 whitened — pass 1's best cell
mu, sd, fn = xg.mu2, xg.sd2, xg.sig_v2

rows, sizes = [], defaultdict(list)
strict = defaultdict(lambda: [0, 0])
anyval = defaultdict(lambda: [0, 0])
recorded_missing = 0

for i in DEV:
    p = pairs['positives'][i]
    src, tgt, op = p['src'], p['tgt'], p['op']
    if src not in pool or tgt not in pool:
        continue
    V = valid_partners(src, op)
    sizes[op].append(len(V))
    if tgt not in V:
        recorded_missing += 1      # sanity: the recorded target must be in its own answer set

    img = OPS[op](pool[src])[p['offset']:]
    q = np.nan_to_num(fn(img)); q = (q - mu) / sd
    q = q @ Wbest
    d = np.linalg.norm(Zbest - q, axis=1)
    d[idx_of[src]] = np.inf
    top = ids[int(np.argmin(d))]

    strict[op][1] += 1; anyval[op][1] += 1
    if top == tgt:
        strict[op][0] += 1
    if top in V:
        anyval[op][0] += 1
    if top != tgt:
        rows.append({'op': op, 'rank1_id': top, 'recorded_tgt': tgt,
                     'rank1_is_valid_partner': top in V, 'answer_set_size': len(V)})

S = sum(v[0] for v in strict.values()); N = sum(v[1] for v in strict.values())
A = sum(v[0] for v in anyval.values())
misses = len(rows)
rescued = sum(1 for r in rows if r['rank1_is_valid_partner'])

out = {
 'development_pairs': N, 'pool_size': len(pool),
 'recorded_target_absent_from_own_answer_set': recorded_missing,
 'answer_set_size': {op: {'n': len(v), 'mean': round(float(np.mean(v)), 3),
                          'median': float(np.median(v)), 'max': int(np.max(v)),
                          'frac_gt_1': round(float(np.mean([x > 1 for x in v])), 4)}
                     for op, v in sizes.items()},
 'L1_top1_STRICT':    {'overall': f"{S}/{N}", 'rate': round(S / N, 4),
                       'by_op': {k: f"{v[0]}/{v[1]}" for k, v in strict.items()}},
 'L1_top1_ANY_VALID': {'overall': f"{A}/{N}", 'rate': round(A / N, 4),
                       'by_op': {k: f"{v[0]}/{v[1]}" for k, v in anyval.items()}},
 'misses_strict': misses, 'misses_that_were_valid_alternatives': rescued,
 'rescue_rate': round(rescued / max(misses, 1), 4),
 'miss_detail': rows,
 'note': 'No L2 quantity is computed in this file.'}
(SEARCH / 'x2_valid_partners.json').write_text(json.dumps(out, indent=1), encoding='utf-8')

print(f"\nrecorded target absent from its own answer set: {recorded_missing}/{N} (sanity, want 0)")
print("\nanswer-set size (how many pool objects satisfy the SAME relation):")
for op, s in out['answer_set_size'].items():
    print(f"  {op:9s} mean {s['mean']:6.3f}  median {s['median']:.0f}  max {s['max']:3d}  frac>1 {s['frac_gt_1']:.3f}")
print(f"\nL1 top-1 STRICT    : {S}/{N} = {S/N:.4f}   {out['L1_top1_STRICT']['by_op']}")
print(f"L1 top-1 ANY-VALID : {A}/{N} = {A/N:.4f}   {out['L1_top1_ANY_VALID']['by_op']}")
print(f"\nstrict misses: {misses}; of those, rank-1 was a VALID alternative in {rescued} ({out['rescue_rate']:.3f})")
