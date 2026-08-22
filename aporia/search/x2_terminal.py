"""CAMPAIGN X-2 pass 3/3 — THE TERMINAL PASS. The new frozen split is touched ONCE.

STRICT ORDER, AND THE ORDER IS THE EXPERIMENT:
  step 1  re-verify the ENTRY GATE on FROZEN (L1 top-1, any-valid, local-scaled)
  step 2  if frozen L1 < 0.95 -> E4 PARK and NO L2 QUANTITY IS COMPUTED AT ALL
  step 3  only if frozen L1 >= 0.95 -> measure L2, adjudicate E1/E2/E3

The L2 block is inside an `if` on the gate result. That is deliberate: it makes it
structurally impossible for this pass to look at the sufficient condition unless
the necessary one was earned first, rather than merely promising not to.

REPRESENTATION IMPORTED UNCHANGED from x2_entry_gate.py — sig_v1, sig_v2, and the
normalisation constants mu/sd and whitening matrices W, all FITTED ON THE
DEVELOPMENT-ERA POOL and applied here as-is. They are not refitted on the frozen
pool; refitting would adapt the representation to the split it is being judged on.

POOL: the frozen term vectors plus the SAME 20,000 blinded distractors (identical
seed and filter as pass 2), so pool composition is matched and only the benchmark
portion differs.

V1 IS RUN ALONGSIDE V2 at L2. Pass 1 flagged a structural tension — order-sensitive
features are the ones least likely to survive an operator, so the features that
passed the gate may be the ones that fail the real task. Running both answers that
question instead of restating it.
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
GATE, K, HASH_K, MIN_EXACT = 0.95, 10, 12, 20
MIN_TERMS, MAX_TERMS = 25, 45

fro = json.loads((SEARCH / 'x2_frozen_pairs.json').read_text(encoding='utf-8'))
fterms = json.loads((SEARCH / 'x2_frozen_terms.json').read_text(encoding='utf-8'))
print(f"\n=== FROZEN SPLIT TOUCHED (once): {len(fro['positives'])} positives ===", flush=True)

def nondeg(v):
    w = v[:MIN_TERMS]
    return len(set(w)) >= 8 and not all(x == w[-1] for x in w[-6:])

rng = random.Random(20260823)                      # same seed as pass 2 -> same distractors
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
pool = dict(fterms)
for i, t in enumerate(cands[:20000]):
    pool[f"D{i:06d}"] = t
ids = list(pool); idx_of = {k: i for i, k in enumerate(ids)}
print(f"pool: {len(pool):,}  (chance top-10 = {10/len(pool):.6f})", flush=True)

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
    r = np.empty(n, dtype=np.float32)
    for s in range(0, n, 512):
        e = min(s + 512, n)
        d2 = sq[s:e, None] + sq[None, :] - 2.0 * (Zf[s:e] @ Zf.T)
        np.maximum(d2, 0, out=d2)
        for j in range(e - s):
            d2[j, s + j] = np.inf
        part = np.argpartition(d2, K, axis=1)[:, :K + 1]
        for j in range(e - s):
            c = part[j]; c = c[np.argsort(d2[j, c])][:K]
            r[s + j] = np.sqrt(d2[j, c[-1]])
    return np.maximum(r, 1e-6)

print("embedding V2...", flush=True)
Z2 = embed(sig_v2, MU2, SD2, W2)
RK2 = rk_of(Z2)

POS = fro['positives']
answer_sets, asize = {}, defaultdict(list)
for i, p in enumerate(POS):
    if p['src'] in pool and p['tgt'] in pool:
        V = valid_partners(p['src'], p['op'])
        answer_sets[i] = V
        asize[p['op']].append(len(V))
missing = sum(1 for i, p in enumerate(POS) if i in answer_sets and p['tgt'] not in answer_sets[i])

# ------------------------------------------------------- STEP 1: GATE ON FROZEN
def l1_scores(Z, rk, fn, mu, sd, Wm):
    st = defaultdict(lambda: [0, 0]); av = defaultdict(lambda: [0, 0])
    for i, p in enumerate(POS):
        if i not in answer_sets:
            continue
        src, tgt, op = p['src'], p['tgt'], p['op']
        img = OPS[op](pool[src])[p['offset']:]
        q = np.nan_to_num(fn(img)); q = ((q - mu) / sd) @ Wm
        d = np.linalg.norm(Z - q, axis=1)
        kq = np.sort(np.partition(d, K)[:K + 1])[K - 1]
        d = d / np.sqrt(max(kq, 1e-6) * rk)          # local scaling, as pass 2
        d[idx_of[src]] = np.inf
        top = ids[int(np.argmin(d))]
        st[op][1] += 1; av[op][1] += 1
        if top == tgt: st[op][0] += 1
        if top in answer_sets[i]: av[op][0] += 1
    S = sum(v[0] for v in st.values()); A = sum(v[0] for v in av.values()); N = sum(v[1] for v in st.values())
    return {'strict': f"{S}/{N}", 'strict_rate': round(S/N, 4), 'any_valid': f"{A}/{N}",
            'any_valid_rate': round(A/N, 4),
            'by_op_strict': {k_: f"{v[0]}/{v[1]}" for k_, v in st.items()},
            'by_op_any_valid': {k_: f"{v[0]}/{v[1]}" for k_, v in av.items()}}, A/N

gate_detail, gate_val = l1_scores(Z2, RK2, sig_v2, MU2, SD2, W2)
GATE_PASSED = gate_val >= GATE

res = {'frozen_positives': len(POS), 'pool_size': len(pool),
       'chance_top10': round(10/len(pool), 6),
       'recorded_target_absent_from_answer_set': missing,
       'answer_set_size': {op: {'n': len(v), 'mean': round(float(np.mean(v)), 3),
                                'median': float(np.median(v)), 'max': int(np.max(v)),
                                'frac_gt_1': round(float(np.mean([x > 1 for x in v])), 4)}
                           for op, v in asize.items()},
       'STEP1_frozen_gate': gate_detail, 'GATE': GATE, 'GATE_PASSED': bool(GATE_PASSED)}

print(f"\nrecorded target absent from own answer set: {missing} (sanity, want 0)")
print("frozen answer-set size:")
for op, s in res['answer_set_size'].items():
    print(f"  {op:9s} mean {s['mean']:6.3f} median {s['median']:.0f} max {s['max']:3d} frac>1 {s['frac_gt_1']:.3f}")
print(f"\nFROZEN L1 strict    {gate_detail['strict']} = {gate_detail['strict_rate']}   {gate_detail['by_op_strict']}")
print(f"FROZEN L1 any-valid {gate_detail['any_valid']} = {gate_detail['any_valid_rate']}   {gate_detail['by_op_any_valid']}")
print(f"\n*** STEP 1 — ENTRY GATE ON FROZEN ({GATE}): {'PASSED' if GATE_PASSED else 'FAILED'} at {gate_val:.4f} ***")

if not GATE_PASSED:
    # ------------------------------------------------- STEP 2: E4 PARK, NO L2
    res['L2_measured'] = False
    res['branch_fired'] = 'E4'
    res['TERMINAL'] = 'PARK'
    res['reason'] = ('the one-pair development margin did not generalise to the frozen split; '
                     'no L2 quantity was computed anywhere in this pass, and a third rebuild is '
                     'not being spent')
    print("\nE4 fired. NO L2 measured. TERMINAL: PARK")
else:
    # ------------------------------------------------- STEP 3: L2, only now earned
    print("\ngate earned — embedding V1 and baselines for L2...", flush=True)
    Z1 = embed(sig_v1, MU1, SD1, W1); RK1 = rk_of(Z1)
    RAWM = np.vstack([[math.copysign(math.log1p(abs(float(x))), x)
                       for x in (pool[i][:25] + [0]*max(0, 25-len(pool[i])))] for i in ids])
    RAWM = np.nan_to_num(RAWM)
    rm, rs = RAWM.mean(0), RAWM.std(0); rs[rs == 0] = 1.0
    RAWZ = (RAWM - rm)/rs
    GMZ = Z2[:, :6].copy()
    SHUF = Z2[np.random.default_rng(20260823).permutation(len(ids))]

    def l2_run(Z, rk=None):
        by_op = defaultdict(lambda: [0, 0])
        for i, p in enumerate(POS):
            if i not in answer_sets:
                continue
            src, op = p['src'], p['op']
            d = np.linalg.norm(Z - Z[idx_of[src]], axis=1)
            if rk is not None:
                kq = np.sort(np.partition(d, K)[:K + 1])[K - 1]
                d = d / np.sqrt(max(kq, 1e-6) * rk)
            d[idx_of[src]] = np.inf
            top10 = set(ids[j] for j in np.argsort(d, kind='stable')[:10])
            by_op[op][1] += 1
            if top10 & answer_sets[i]:
                by_op[op][0] += 1
        tot = [sum(v[0] for v in by_op.values()), sum(v[1] for v in by_op.values())]
        nt = [sum(v[0] for k_, v in by_op.items() if k_ != 'shift'),
              sum(v[1] for k_, v in by_op.items() if k_ != 'shift')]
        return {'overall': f"{tot[0]}/{tot[1]}", 'overall_rate': round(tot[0]/tot[1], 4),
                'four_real_ops': f"{nt[0]}/{nt[1]}", 'four_real_rate': round(nt[0]/max(nt[1], 1), 4),
                'shift_control': f"{by_op['shift'][0]}/{by_op['shift'][1]}",
                'by_op': {k_: f"{v[0]}/{v[1]}" for k_, v in by_op.items()}}

    L2 = {'V2_localscaled': l2_run(Z2, RK2), 'V2_plain': l2_run(Z2),
          'V1_localscaled': l2_run(Z1, RK1), 'V1_plain': l2_run(Z1),
          'B_raw': l2_run(RAWZ), 'B_shuffled': l2_run(SHUF), 'B_growthmag': l2_run(GMZ)}
    res['STEP3_L2_top10_any_valid'] = L2
    res['L2_measured'] = True

    neg_by_src = defaultdict(list)
    for n in fro['negatives']:
        neg_by_src[(n['op'], n['src'])].append(n['decoy'])
    fr = [0, 0]
    for i, p in enumerate(POS):
        if i not in answer_sets:
            continue
        dec = [d for d in neg_by_src.get((p['op'], p['src']), []) if d in pool]
        if not dec:
            continue
        q = Z2[idx_of[p['src']]]
        fr[1] += 1
        fr[0] += int(np.linalg.norm(Z2[idx_of[dec[0]]] - q) < np.linalg.norm(Z2[idx_of[p['tgt']]] - q))
    res['matched_negative_false_retrieval'] = {'count': f"{fr[0]}/{fr[1]}",
                                               'rate': round(fr[0]/max(fr[1], 1), 4), 'chance': 0.5}

    # ---- adjudication. Thresholds for E1/E2 supplied here and DISCLOSED as such.
    v2 = L2['V2_localscaled']['four_real_rate']; raw = L2['B_raw']['four_real_rate']
    ch = res['chance_top10']
    E1 = bool(v2 >= 2*raw and (v2 - raw) >= 0.10)
    E2 = bool(abs(v2 - raw) < 0.10)
    E3 = bool(GATE_PASSED and v2 <= 3*ch and raw <= 3*ch)
    res['branches'] = {'E1_advance': E1, 'E2_redesign': E2, 'E3_kill': E3}
    res['threshold_disclosure'] = ('E3 carried a preregistered numeric (<= 3x chance). E1 and E2 did '
                                   'not, and their cuts (2x ratio with >= 0.10 absolute gap) were '
                                   'supplied at adjudication time. With 40 four-real-operator frozen '
                                   'pairs the granularity is 1/40 = 0.025, so a 0.10 gap is 4 pairs.')
    res['TERMINAL'] = 'KILL' if E3 else ('ADVANCE' if E1 else 'REDESIGN')
    res['branch_fired'] = 'E3' if E3 else ('E1' if E1 else 'E2')

    print(f"\nL2 top-10 (any-valid), chance = {ch:.6f}:")
    for k_, v in L2.items():
        print(f"  {k_:16s} overall {v['overall']:>7s} = {v['overall_rate']:.4f} | four real ops "
              f"{v['four_real_ops']:>6s} = {v['four_real_rate']:.4f} | shift {v['shift_control']:>6s}")
    print(f"\nmatched-negative FR: {res['matched_negative_false_retrieval']['count']} = "
          f"{res['matched_negative_false_retrieval']['rate']} (chance 0.5)")
    print(f"branches: {res['branches']}")

(SEARCH / 'x2_terminal_results.json').write_text(json.dumps(res, indent=1), encoding='utf-8')
print(f"\n*** CAMPAIGN X-2 TERMINAL: {res['TERMINAL']} (branch {res['branch_fired']}) ***")
