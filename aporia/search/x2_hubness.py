"""CAMPAIGN X-2 pass 2 — OBLIGATION 2, and it is a METRIC pathology, not a feature gap.

THE MISS EVIDENCE THAT FORCED THIS: of the 7 residual genuine misses after the
ground-truth correction, the SAME distractor D017288 is rank-1 for two unrelated
partsum queries. A single pool object winning several unrelated queries is the
signature of HUBNESS — the concentration-of-distance pathology in which, as
dimension grows, a few points become nearest neighbours of disproportionately
many others. V2 is 125-dimensional, so it is squarely in the regime where this
appears.

WHY THIS IS NOT THE SAME AS PASS 1'S REFUTED METRIC ARGUMENT. Pass 1 tested ZCA
whitening, which fixes CORRELATION between feature blocks, and found it worth
-0.016. Hubness is a different pathology: it survives whitening untouched, because
decorrelating axes does nothing about a point sitting near the data mean and
therefore near everything. So this is a second, distinct metric hypothesis with
its own evidence, not a retry of the refuted one.

WHY IT IS NOT GATE-CHASING. The gate is 0.95 and the corrected score is 0.944 —
ONE PAIR apart at a granularity of 1/125 = 0.008. Feature engineering aimed at
that gap would be indefensible overfitting. What makes this admissible instead is
that hubness is (a) a standard, pre-existing phenomenon with a standard
correction, (b) predicted by an observation made BEFORE the fix — one distractor
winning two unrelated queries, and (c) MEASURABLE INDEPENDENTLY of the gate. So
the hubness statistic itself is reported first and stands whatever the gate does.
If the k-occurrence distribution is not skewed, the hypothesis is dead and no
correction is applied.

CORRECTION: local scaling. d'(q,x) = d(q,x) / sqrt(r_k(q) * r_k(x)), where r_k is
the distance to the k-th nearest neighbour. A hub sits close to everything, so its
own r_k is small, which inflates its corrected distance and demotes it.

NO L2 COMPUTATION APPEARS IN THIS FILE.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
from collections import Counter, defaultdict

import numpy as np

SEARCH = pathlib.Path(r'F:\Prometheus\aporia\search')
spec = importlib.util.spec_from_file_location('xg', SEARCH / 'x2_entry_gate.py')
xg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xg)
spec2 = importlib.util.spec_from_file_location('vp', SEARCH / 'x2_valid_partners.py')

pool, ids, idx_of = xg.pool, xg.ids, xg.idx_of
pairs, DEV, OPS = xg.pairs, xg.DEV, xg.OPS
Z, W, mu, sd, fn = xg.W2c, xg.W2, xg.mu2, xg.sd2, xg.sig_v2
K = 10

print("\n=== hubness: k-occurrence over the pool ===", flush=True)
Zf = np.ascontiguousarray(Z, dtype=np.float32)
sq = (Zf ** 2).sum(1)
n = Zf.shape[0]
rk = np.empty(n, dtype=np.float32)
knn_counts = Counter()
CH = 512
for s in range(0, n, CH):
    e = min(s + CH, n)
    d2 = sq[s:e, None] + sq[None, :] - 2.0 * (Zf[s:e] @ Zf.T)
    np.maximum(d2, 0, out=d2)
    for r in range(e - s):
        d2[r, s + r] = np.inf
    part = np.argpartition(d2, K, axis=1)[:, :K + 1]
    for r in range(e - s):
        cols = part[r]
        cols = cols[np.argsort(d2[r, cols])][:K]
        rk[s + r] = np.sqrt(d2[r, cols[-1]])
        knn_counts.update(cols.tolist())
rk = np.maximum(rk, 1e-6)

occ = np.array([knn_counts.get(i, 0) for i in range(n)], dtype=float)
m, sdv = occ.mean(), occ.std()
skew = float(((occ - m) ** 3).mean() / (sdv ** 3)) if sdv > 0 else 0.0
print(f"k-occurrence (k={K}): mean {m:.2f}  std {sdv:.2f}  max {int(occ.max())}  SKEWNESS {skew:.3f}")
print(f"points appearing in > 10x their fair share (> {10*K}): {int((occ > 10*K).sum())}")

HUBNESS_CONFIRMED = skew > 1.0

# ---------------------------------------------------------------- scoring
HASH_K, MIN_EXACT = 12, 20
index = defaultdict(list)
for k_, v in pool.items():
    if len(v) >= HASH_K:
        index[tuple(v[:HASH_K])].append(k_)

def overlap(a, b):
    nn, i = min(len(a), len(b)), 0
    while i < nn and a[i] == b[i]:
        i += 1
    return i

def valid_partners(src, op):
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
            if cid != src and overlap(im, pool[cid]) >= MIN_EXACT:
                out.add(cid)
    return out

def score(corrected: bool):
    st = defaultdict(lambda: [0, 0]); av = defaultdict(lambda: [0, 0]); miss = []
    for i in DEV:
        p = pairs['positives'][i]
        src, tgt, op = p['src'], p['tgt'], p['op']
        if src not in pool or tgt not in pool:
            continue
        V = valid_partners(src, op)
        img = OPS[op](pool[src])[p['offset']:]
        q = np.nan_to_num(fn(img)); q = ((q - mu) / sd) @ W
        d = np.linalg.norm(Z - q, axis=1)
        if corrected:
            kq = np.sort(np.partition(d, K)[:K + 1])[K - 1]      # the query's own r_k
            d = d / np.sqrt(max(kq, 1e-6) * rk)
        d[idx_of[src]] = np.inf
        top = ids[int(np.argmin(d))]
        st[op][1] += 1; av[op][1] += 1
        if top == tgt: st[op][0] += 1
        if top in V:   av[op][0] += 1
        else:          miss.append({'op': op, 'rank1': top, 'recorded': tgt, 'answer_set': len(V)})
    S = sum(v[0] for v in st.values()); A = sum(v[0] for v in av.values()); N = sum(v[1] for v in st.values())
    return {'strict': f"{S}/{N}", 'strict_rate': round(S / N, 4),
            'any_valid': f"{A}/{N}", 'any_valid_rate': round(A / N, 4),
            'by_op_any_valid': {k_: f"{v[0]}/{v[1]}" for k_, v in av.items()},
            'residual_misses': miss}

base = score(False)
print(f"\nUNCORRECTED  strict {base['strict']} = {base['strict_rate']}  |  any-valid {base['any_valid']} = {base['any_valid_rate']}")
res = {'k': K, 'k_occurrence': {'mean': round(m, 3), 'std': round(sdv, 3),
                                'max': int(occ.max()), 'skewness': round(skew, 3),
                                'n_over_10x_fair_share': int((occ > 10 * K).sum())},
       'hubness_confirmed': bool(HUBNESS_CONFIRMED),
       'uncorrected': base, 'GATE': 0.95}

if HUBNESS_CONFIRMED:
    corr = score(True)
    print(f"LOCAL-SCALED strict {corr['strict']} = {corr['strict_rate']}  |  any-valid {corr['any_valid']} = {corr['any_valid_rate']}")
    print(f"  by op (any-valid): {corr['by_op_any_valid']}")
    res['local_scaled'] = corr
    best = max(base['any_valid_rate'], corr['any_valid_rate'])
    res['best_any_valid'] = best
    res['best_variant'] = 'local_scaled' if corr['any_valid_rate'] >= base['any_valid_rate'] else 'uncorrected'
else:
    print("hubness NOT confirmed (skewness <= 1.0) — no correction applied, hypothesis dead")
    res['best_any_valid'] = base['any_valid_rate']
    res['best_variant'] = 'uncorrected'

res['GATE_PASSED'] = bool(res['best_any_valid'] >= 0.95)
res['L2_measured'] = False
(SEARCH / 'x2_hubness_results.json').write_text(json.dumps(res, indent=1), encoding='utf-8')
print(f"\n*** ENTRY GATE 0.95 on ANY-VALID: {'PASSED' if res['GATE_PASSED'] else 'FAILED'} "
      f"at {res['best_any_valid']:.4f} ({res['best_variant']}) — L2 NOT measured ***")
