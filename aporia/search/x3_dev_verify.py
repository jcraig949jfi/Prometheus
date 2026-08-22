"""CAMPAIGN X-3 pass 2/3 — instrument verification on DEVELOPMENT ONLY.

The 500 frozen indices in x3_split.json are loaded solely to be EXCLUDED. Only the
250 development pairs are scored. K0-K4 are not adjudicated here.

NO L2 COMPUTATION APPEARS IN THIS FILE. L2 is read once, on frozen, in pass 3, so
there is nothing in this pass that could be tuned toward it.

REPRESENTATION IMPORTED UNCHANGED from x2_entry_gate.py — sig_v2 and the
normalisation constants and whitening matrix fitted on the X-2-era pool, applied
here as-is. Nothing measured below is attributable to a representation change.

HUBNESS IS RE-MEASURED, NOT ASSUMED. X-2 pass 2 established that metric
pathologies are pool-specific: ZCA whitening estimated on one pool did not
transfer, and local scaling was justified only by a skewness of 3.783 measured on
THAT pool. The X-3 pool has different benchmark members, so the k-occurrence
distribution is recomputed here and the correction is applied only if skewness
> 1.0 — the same pre-committed condition, checked again on the new population.
This is the fourth application of the standing lesson that a statistic measured on
one population may not be quoted as a property of another.

CONFIDENCE INTERVAL METHOD, DISCLOSED: K0 is an interval gate but the
preregistration did not name a CI method, which is a small instance of the same
under-specification that twice forced thresholds to be invented at adjudication
time. This pass fixes it in the open: the WILSON score interval is used, because
it is well behaved for proportions near 1 where the Wald interval overshoots. Both
are printed so a reviewer can recompute either.
"""
from __future__ import annotations

import gzip
import importlib.util
import json
import math
import pathlib
import random
from collections import Counter, defaultdict

import numpy as np

ROOT = pathlib.Path(r'F:\Prometheus')
SEARCH = ROOT / 'aporia' / 'search'
spec = importlib.util.spec_from_file_location('xg', SEARCH / 'x2_entry_gate.py')
xg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xg)

sig_v2, OPS = xg.sig_v2, xg.OPS
MU2, SD2, W2 = xg.mu2, xg.sd2, xg.W2
K, HASH_K, MIN_EXACT, MIN_TERMS, MAX_TERMS = 10, 12, 20, 25, 45

pairs = json.loads((SEARCH / 'x3_pairs.json').read_text(encoding='utf-8'))
split = json.loads((SEARCH / 'x3_split.json').read_text(encoding='utf-8'))
terms = json.loads((SEARCH / 'x3_terms.json').read_text(encoding='utf-8'))
DEV = sorted(split['dev_indices'])
FROZEN_N = len(split['frozen_indices'])
print(f"\n=== X-3 DEVELOPMENT ONLY: {len(DEV)} pairs (frozen {FROZEN_N} excluded, not inspected) ===", flush=True)

def nondeg(v):
    w = v[:MIN_TERMS]
    return len(set(w)) >= 8 and not all(x == w[-1] for x in w[-6:])

rng = random.Random(20260823)
cands = []
with gzip.open(ROOT / 'prometheus_data/oeis/stripped.gz', 'rt', encoding='utf-8', errors='replace') as fh:
    for line in fh:
        if line.startswith('#'):
            continue
        p = line.strip().rstrip(',').split(',')
        if len(p) < MIN_TERMS + 1:
            continue
        try:
            t = [int(x) for x in p[1:MAX_TERMS + 1]]
        except ValueError:
            continue
        if len(t) >= MIN_TERMS and nondeg(t):
            cands.append(t)
rng.shuffle(cands)
pool = dict(terms)
for i, t in enumerate(cands[:20000]):
    pool[f"D{i:06d}"] = t
ids = list(pool); idx_of = {k: i for i, k in enumerate(ids)}
print(f"X-3 pool: {len(pool):,}", flush=True)

index = defaultdict(list)
for k_, v in pool.items():
    if len(v) >= HASH_K:
        index[tuple(v[:HASH_K])].append(k_)

def overlap(a, b):
    n, i = min(len(a), len(b)), 0
    while i < n and a[i] == b[i]:
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

print("embedding V2 (imported unchanged)...", flush=True)
M = np.vstack([sig_v2(pool[i]) for i in ids])
M = np.nan_to_num(M, nan=0.0, posinf=0.0, neginf=0.0)
Z = ((M - MU2) / SD2) @ W2

# ------------------------------------------------- hubness, RE-MEASURED on this pool
Zf = np.ascontiguousarray(Z, dtype=np.float32)
sq = (Zf ** 2).sum(1); n = Zf.shape[0]
rk = np.empty(n, dtype=np.float32); occ_c = Counter()
for s in range(0, n, 512):
    e = min(s + 512, n)
    d2 = sq[s:e, None] + sq[None, :] - 2.0 * (Zf[s:e] @ Zf.T)
    np.maximum(d2, 0, out=d2)
    for j in range(e - s):
        d2[j, s + j] = np.inf
    part = np.argpartition(d2, K, axis=1)[:, :K + 1]
    for j in range(e - s):
        c = part[j]; c = c[np.argsort(d2[j, c])][:K]
        rk[s + j] = np.sqrt(d2[j, c[-1]]); occ_c.update(c.tolist())
rk = np.maximum(rk, 1e-6)
occ = np.array([occ_c.get(i, 0) for i in range(n)], dtype=float)
mo, so = occ.mean(), occ.std()
skew = float(((occ - mo) ** 3).mean() / (so ** 3)) if so > 0 else 0.0
HUB = skew > 1.0
print(f"hubness on X-3 pool (k={K}): mean {mo:.2f} std {so:.2f} max {int(occ.max())} SKEWNESS {skew:.3f} -> "
      f"{'CONFIRMED, local scaling applies' if HUB else 'NOT confirmed, uncorrected reported'}", flush=True)

# ------------------------------------------------- answer sets + L1
POS = pairs['positives']
asets, asize = {}, defaultdict(list)
for i in DEV:
    p = POS[i]
    if p['src'] in pool and p['tgt'] in pool:
        asets[i] = valid_partners(p['src'], p['op'])
        asize[p['op']].append(len(asets[i]))
missing = sum(1 for i in DEV if i in asets and POS[i]['tgt'] not in asets[i])

def score(corrected):
    st = defaultdict(lambda: [0, 0]); av = defaultdict(lambda: [0, 0])
    for i in DEV:
        if i not in asets:
            continue
        p = POS[i]; src, tgt, op = p['src'], p['tgt'], p['op']
        img = OPS[op](pool[src])[p['offset']:]
        q = np.nan_to_num(sig_v2(img)); q = ((q - MU2) / SD2) @ W2
        d = np.linalg.norm(Z - q, axis=1)
        if corrected:
            kq = np.sort(np.partition(d, K)[:K + 1])[K - 1]
            d = d / np.sqrt(max(kq, 1e-6) * rk)
        d[idx_of[src]] = np.inf
        top = ids[int(np.argmin(d))]
        st[op][1] += 1; av[op][1] += 1
        if top == tgt: st[op][0] += 1
        if top in asets[i]: av[op][0] += 1
    S = sum(v[0] for v in st.values()); A = sum(v[0] for v in av.values()); N = sum(v[1] for v in st.values())
    return {'strict_count': f"{S}/{N}", 'strict': round(S/N, 4),
            'any_valid_count': f"{A}/{N}", 'any_valid': round(A/N, 4), 'n': N,
            'by_op_strict': {k_: f"{v[0]}/{v[1]}" for k_, v in st.items()},
            'by_op_any_valid': {k_: f"{v[0]}/{v[1]}" for k_, v in av.items()},
            'four_real_any_valid': f"{sum(v[0] for k_, v in av.items() if k_ != 'shift')}/"
                                   f"{sum(v[1] for k_, v in av.items() if k_ != 'shift')}",
            'shift_any_valid': f"{av['shift'][0]}/{av['shift'][1]}"}

def wilson(k, nn, z=1.96):
    if nn == 0: return (0.0, 0.0)
    p = k/nn; d = 1 + z*z/nn
    c = (p + z*z/(2*nn))/d
    h = z*math.sqrt(p*(1-p)/nn + z*z/(4*nn*nn))/d
    return (round(c-h, 4), round(c+h, 4))

def wald(k, nn, z=1.96):
    p = k/nn; s = math.sqrt(p*(1-p)/nn)
    return (round(p - z*s, 4), round(p + z*s, 4))

plain = score(False)
res = {'development_pairs': plain['n'], 'frozen_pairs_untouched': FROZEN_N,
       'pool_size': len(pool),
       'recorded_target_absent_from_answer_set': missing,
       'hubness': {'k': K, 'mean': round(mo, 3), 'std': round(so, 3),
                   'max': int(occ.max()), 'skewness': round(skew, 3), 'confirmed': bool(HUB)},
       'answer_set_size': {op: {'n': len(v), 'mean': round(float(np.mean(v)), 3),
                                'median': float(np.median(v)), 'max': int(np.max(v)),
                                'frac_gt_1': round(float(np.mean([x > 1 for x in v])), 4)}
                           for op, v in asize.items()},
       'uncorrected': plain, 'L2_measured': False}

use = plain
if HUB:
    corr = score(True)
    res['local_scaled'] = corr
    use = corr if corr['any_valid'] >= plain['any_valid'] else plain
    res['variant_used'] = 'local_scaled' if use is corr else 'uncorrected'
else:
    res['variant_used'] = 'uncorrected'

ka = round(use['any_valid'] * use['n'])
res['K0_preview'] = {'variant': res['variant_used'], 'any_valid': use['any_valid_count'],
                     'rate': use['any_valid'],
                     'wilson_95': wilson(ka, use['n']), 'wald_95': wald(ka, use['n']),
                     'K0_threshold': 0.90,
                     'ci_method_disclosure': 'Wilson used; the preregistration did not name a method'}

(SEARCH / 'x3_dev_results.json').write_text(json.dumps(res, indent=1), encoding='utf-8')

print(f"\nrecorded target absent from own answer set: {missing} (sanity, want 0)")
print("development answer-set size:")
for op, s in res['answer_set_size'].items():
    print(f"  {op:9s} mean {s['mean']:6.3f} median {s['median']:.0f} max {s['max']:3d} frac>1 {s['frac_gt_1']:.3f}")
print(f"\nUNCORRECTED   strict {plain['strict_count']} = {plain['strict']}   any-valid {plain['any_valid_count']} = {plain['any_valid']}")
if HUB:
    print(f"LOCAL-SCALED  strict {res['local_scaled']['strict_count']} = {res['local_scaled']['strict']}   "
          f"any-valid {res['local_scaled']['any_valid_count']} = {res['local_scaled']['any_valid']}")
print(f"\nvariant used: {res['variant_used']}")
print(f"  by op (any-valid): {use['by_op_any_valid']}")
print(f"  four real ops {use['four_real_any_valid']} | shift control {use['shift_any_valid']}")
print(f"\nK0 PREVIEW (development, NOT the gate): any-valid {use['any_valid_count']} = {use['any_valid']}")
print(f"  Wilson 95% CI {res['K0_preview']['wilson_95']}   Wald 95% CI {res['K0_preview']['wald_95']}   K0 needs LB > 0.90")
print("\nNO L2 MEASURED. Frozen split untouched. K0-K4 not adjudicated.")
