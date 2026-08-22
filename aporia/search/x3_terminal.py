"""CAMPAIGN X-3 pass 3/3 — TERMINAL. Frozen split touched ONCE.

First pass in three campaigns permitted to measure L2, and only if K0 is earned
first. The L2 block sits inside an `if` on the gate result, so looking at the
sufficient condition without the necessary one is structurally impossible.

ORDER, WHICH IS THE EXPERIMENT:
  1  frozen answer sets, mean |V| computed ON FROZEN (never carried from dev —
     that error was caught in pass 2 and this is where it would have bitten)
  2  K0 interval gate: Wilson 95% CI lower bound on frozen L1 top-1 > 0.90
  3  K0 fails -> K4 PARK, no L2 computed
     K0 passes -> L2 on the 400 four-real-operator frozen pairs, V1 ALONGSIDE V2,
     three baselines, D with its interval, then K1-K4

PAIRED INFERENCE, DISCLOSED. The power calculation in P114 used the
independent-samples SE sqrt(2p(1-p)/n). But L2 and the raw-term baseline are
measured on THE SAME 400 pairs, so the comparison is paired and the correct
interval is McNemar's, which depends only on discordant pairs and is narrower.
Both are reported: the preregistered independent form (so the branch thresholds
are read on the basis they were set) and the correct paired form (because a
difference reported on the wrong variance model is how the X-2 gate died).
The preregistered thresholds are NOT changed — only better-characterised.
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

sig_v1, sig_v2, OPS = xg.sig_v1, xg.sig_v2, xg.OPS
MU1, SD1, W1 = xg.mu1, xg.sd1, xg.W1
MU2, SD2, W2 = xg.mu2, xg.sd2, xg.W2
K, HASH_K, MIN_EXACT, MIN_TERMS, MAX_TERMS = 10, 12, 20, 25, 45

pairs = json.loads((SEARCH / 'x3_pairs.json').read_text(encoding='utf-8'))
split = json.loads((SEARCH / 'x3_split.json').read_text(encoding='utf-8'))
terms = json.loads((SEARCH / 'x3_terms.json').read_text(encoding='utf-8'))
FRO = sorted(split['frozen_indices'])
print(f"\n=== X-3 FROZEN TOUCHED (once): {len(FRO)} positives ===", flush=True)

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
N_POOL = len(pool)
print(f"pool: {N_POOL:,}", flush=True)

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

def embed(fn, mu, sd, Wm):
    M = np.vstack([fn(pool[i]) for i in ids])
    M = np.nan_to_num(M, nan=0.0, posinf=0.0, neginf=0.0)
    return ((M - mu) / sd) @ Wm

def rk_of(Z):
    Zf = np.ascontiguousarray(Z, dtype=np.float32)
    sq = (Zf ** 2).sum(1); n = Zf.shape[0]
    r = np.empty(n, dtype=np.float32); occ = Counter()
    for s in range(0, n, 512):
        e = min(s + 512, n)
        d2 = sq[s:e, None] + sq[None, :] - 2.0 * (Zf[s:e] @ Zf.T)
        np.maximum(d2, 0, out=d2)
        for j in range(e - s):
            d2[j, s + j] = np.inf
        part = np.argpartition(d2, K, axis=1)[:, :K + 1]
        for j in range(e - s):
            c = part[j]; c = c[np.argsort(d2[j, c])][:K]
            r[s + j] = np.sqrt(d2[j, c[-1]]); occ.update(c.tolist())
    return np.maximum(r, 1e-6), occ

def wilson(k, nn, z=1.96):
    if nn == 0: return (0.0, 0.0)
    p = k/nn; d = 1 + z*z/nn
    c = (p + z*z/(2*nn))/d
    h = z*math.sqrt(p*(1-p)/nn + z*z/(4*nn*nn))/d
    return (round(c-h, 4), round(c+h, 4))

print("embedding V2...", flush=True)
Z2 = embed(sig_v2, MU2, SD2, W2); RK2, occ2 = rk_of(Z2)

# ---------------------------------------------- STEP 1: frozen answer sets
POS = pairs['positives']
asets, asize = {}, defaultdict(list)
for i in FRO:
    p = POS[i]
    if p['src'] in pool and p['tgt'] in pool:
        asets[i] = valid_partners(p['src'], p['op'])
        asize[p['op']].append(len(asets[i]))
missing = sum(1 for i in FRO if i in asets and POS[i]['tgt'] not in asets[i])
real_V = [len(asets[i]) for i in FRO if i in asets and POS[i]['op'] != 'shift']
MEAN_V = float(np.mean(real_V))
CHANCE_ADJ = 10 * MEAN_V / N_POOL
print(f"\nfrozen mean |V| on four real operators = {MEAN_V:.3f} (computed ON FROZEN)")
print(f"answer-set-adjusted chance top-10 = 10*{MEAN_V:.3f}/{N_POOL} = {CHANCE_ADJ:.6f} "
      f"(unadjusted {10/N_POOL:.6f}); 3x = {3*CHANCE_ADJ:.6f}")

# ---------------------------------------------- STEP 2: K0
def l1(Z, rk, fn, mu, sd, Wm):
    st = defaultdict(lambda: [0, 0]); av = defaultdict(lambda: [0, 0])
    for i in FRO:
        if i not in asets: continue
        p = POS[i]; src, tgt, op = p['src'], p['tgt'], p['op']
        img = OPS[op](pool[src])[p['offset']:]
        q = np.nan_to_num(fn(img)); q = ((q - mu)/sd) @ Wm
        d = np.linalg.norm(Z - q, axis=1)
        kq = np.sort(np.partition(d, K)[:K+1])[K-1]
        d = d/np.sqrt(max(kq, 1e-6)*rk)
        d[idx_of[src]] = np.inf
        top = ids[int(np.argmin(d))]
        st[op][1] += 1; av[op][1] += 1
        if top == tgt: st[op][0] += 1
        if top in asets[i]: av[op][0] += 1
    return st, av

st, av = l1(Z2, RK2, sig_v2, MU2, SD2, W2)
S = sum(v[0] for v in st.values()); A = sum(v[0] for v in av.values()); NL1 = sum(v[1] for v in st.values())
lo, hi = wilson(A, NL1)
K0 = lo > 0.90
res = {'frozen_positives': len(FRO), 'pool_size': N_POOL,
       'recorded_target_absent_from_answer_set': missing,
       'frozen_mean_V_four_real_ops': round(MEAN_V, 4),
       'chance_top10_unadjusted': round(10/N_POOL, 6),
       'chance_top10_answer_set_adjusted': round(CHANCE_ADJ, 6),
       'answer_set_size': {op: {'n': len(v), 'mean': round(float(np.mean(v)), 3),
                                'max': int(np.max(v)), 'frac_gt_1': round(float(np.mean([x > 1 for x in v])), 4)}
                           for op, v in asize.items()},
       'STEP2_K0': {'strict': f"{S}/{NL1}", 'strict_rate': round(S/NL1, 4),
                    'any_valid': f"{A}/{NL1}", 'any_valid_rate': round(A/NL1, 4),
                    'wilson_95': [lo, hi], 'threshold': 0.90, 'PASSED': bool(K0),
                    'by_op_strict': {k_: f"{v[0]}/{v[1]}" for k_, v in st.items()},
                    'by_op_any_valid': {k_: f"{v[0]}/{v[1]}" for k_, v in av.items()}}}
print(f"\nsanity: recorded target absent from own answer set = {missing}")
print(f"FROZEN L1 strict    {S}/{NL1} = {S/NL1:.4f}   {res['STEP2_K0']['by_op_strict']}")
print(f"FROZEN L1 any-valid {A}/{NL1} = {A/NL1:.4f}   {res['STEP2_K0']['by_op_any_valid']}")
print(f"Wilson 95% CI ({lo}, {hi})  vs K0 threshold 0.90")
print(f"\n*** K0 INTERVAL GATE: {'PASSED' if K0 else 'FAILED'} ***")

if not K0:
    res.update({'L2_measured': False, 'branch_fired': 'K4', 'TERMINAL': 'PARK',
                'reason': 'K0 interval gate failed on frozen; no L2 computed'})
    print("K4 fired. NO L2. TERMINAL: PARK")
else:
    print("\nK0 earned — measuring L2 (first time in three campaigns)...", flush=True)
    Z1 = embed(sig_v1, MU1, SD1, W1); RK1, _ = rk_of(Z1)
    RAWM = np.vstack([[math.copysign(math.log1p(abs(float(x))), x)
                       for x in (pool[i][:25] + [0]*max(0, 25-len(pool[i])))] for i in ids])
    RAWM = np.nan_to_num(RAWM); rm, rs = RAWM.mean(0), RAWM.std(0); rs[rs == 0] = 1.0
    RAWZ = (RAWM - rm)/rs
    GMZ = Z2[:, :6].copy()
    SHUF = Z2[np.random.default_rng(20260824).permutation(len(ids))]

    def l2_hits(Z, rk=None):
        """per-pair boolean: did a valid partner land in the top-10?"""
        out = {}
        for i in FRO:
            if i not in asets: continue
            src = POS[i]['src']
            d = np.linalg.norm(Z - Z[idx_of[src]], axis=1)
            if rk is not None:
                kq = np.sort(np.partition(d, K)[:K+1])[K-1]
                d = d/np.sqrt(max(kq, 1e-6)*rk)
            d[idx_of[src]] = np.inf
            top = set(ids[j] for j in np.argsort(d, kind='stable')[:10])
            out[i] = bool(top & asets[i])
        return out

    arms = {'V2': l2_hits(Z2, RK2), 'V1': l2_hits(Z1, RK1), 'B_raw': l2_hits(RAWZ),
            'B_shuffled': l2_hits(SHUF), 'B_growthmag': l2_hits(GMZ)}
    REAL = [i for i in FRO if i in asets and POS[i]['op'] != 'shift']
    SHIFT = [i for i in FRO if i in asets and POS[i]['op'] == 'shift']

    def summ(h, sub):
        k = sum(h[i] for i in sub); n = len(sub)
        return {'count': f"{k}/{n}", 'rate': round(k/n, 4), 'wilson_95': list(wilson(k, n))}
    L2 = {a: {'four_real_ops': summ(h, REAL), 'shift_control': summ(h, SHIFT),
              'by_op': {op: summ(h, [i for i in FRO if i in asets and POS[i]['op'] == op])
                        for op in ('diff', 'partsum', 'binomial', 'moebius')}}
          for a, h in arms.items()}
    res['STEP3_L2_top10_any_valid'] = L2
    res['L2_measured'] = True

    hv, hr = arms['V2'], arms['B_raw']
    b = sum(1 for i in REAL if hv[i] and not hr[i])
    c = sum(1 for i in REAL if hr[i] and not hv[i])
    n = len(REAL)
    D = (b - c)/n
    se_ind = math.sqrt(2*0.05*0.95/n)
    se_pair = math.sqrt(max((b + c) - (b - c)**2/n, 0))/n
    res['D'] = {'value': round(D, 4), 'b_V2_only': b, 'c_raw_only': c, 'n': n,
                'se_independent_preregistered': round(se_ind, 4),
                'ci95_independent': [round(D - 1.96*se_ind, 4), round(D + 1.96*se_ind, 4)],
                'se_paired_mcnemar': round(se_pair, 4),
                'ci95_paired': [round(D - 1.96*se_pair, 4), round(D + 1.96*se_pair, 4)],
                'disclosure': 'thresholds were set on the independent form; the paired form is '
                              'correct and narrower, and is reported but does NOT move the branches'}

    neg = defaultdict(list)
    for nn in pairs['negatives']:
        neg[(nn['op'], nn['src'])].append(nn['decoy'])
    fr = [0, 0]
    for i in FRO:
        if i not in asets: continue
        p = POS[i]
        dd = [x for x in neg.get((p['op'], p['src']), []) if x in pool]
        if not dd: continue
        q = Z2[idx_of[p['src']]]
        fr[1] += 1
        fr[0] += int(np.linalg.norm(Z2[idx_of[dd[0]]] - q) < np.linalg.norm(Z2[idx_of[p['tgt']]] - q))
    res['matched_negative_false_retrieval'] = {'count': f"{fr[0]}/{fr[1]}",
                                               'rate': round(fr[0]/max(fr[1], 1), 4), 'chance': 0.5}

    l2v2 = L2['V2']['four_real_ops']['rate']
    K1 = bool(D >= 0.05)
    K2 = bool(0.02 <= D < 0.05)
    K3 = bool(D < 0.02 and l2v2 <= 3*CHANCE_ADJ and K0)
    res['branches'] = {'K1_advance': K1, 'K2_redesign': K2, 'K3_kill': K3}
    res['TERMINAL'] = 'ADVANCE' if K1 else ('REDESIGN' if K2 else ('KILL' if K3 else 'REDESIGN'))
    res['branch_fired'] = 'K1' if K1 else ('K2' if K2 else ('K3' if K3 else 'K2-default'))

    print(f"\nL2 top-10 (any-valid), adjusted chance {CHANCE_ADJ:.6f}:")
    for a, v in L2.items():
        print(f"  {a:12s} four real {v['four_real_ops']['count']:>7s} = {v['four_real_ops']['rate']:.4f} "
              f"CI {v['four_real_ops']['wilson_95']} | shift {v['shift_control']['count']}")
    print(f"\n  V2 by op: {{op: v['by_op'][op]['count'] for op in v['by_op']}}".replace('v', 'L2[\"V2\"]'))
    for op in ('diff', 'partsum', 'binomial', 'moebius'):
        print(f"    {op:9s} V2 {L2['V2']['by_op'][op]['count']:>7s}  raw {L2['B_raw']['by_op'][op]['count']:>7s}")
    print(f"\nD = {D:+.4f}  (b={b} V2-only, c={c} raw-only, n={n})")
    print(f"  independent CI (preregistered basis) {res['D']['ci95_independent']}")
    print(f"  paired McNemar CI (correct)          {res['D']['ci95_paired']}")
    print(f"matched-negative FR {res['matched_negative_false_retrieval']['count']} = "
          f"{res['matched_negative_false_retrieval']['rate']} (chance 0.5)")
    print(f"branches: {res['branches']}")

(SEARCH / 'x3_terminal_results.json').write_text(json.dumps(res, indent=1), encoding='utf-8')
print(f"\n*** CAMPAIGN X-3 TERMINAL: {res['TERMINAL']} (branch {res['branch_fired']}) ***")
