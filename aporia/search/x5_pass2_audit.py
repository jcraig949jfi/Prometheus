"""CAMPAIGN X-5 pass 2/3 — three audits of what pass 1 left exposed.

frozen-B is NOT touched and no frozen quantity is computed. N1-N6, G-pos and
G-null are FINAL and are not adjudicated here.

A1  RAW-BLOCK LENGTH SENSITIVITY. Pass 1 cut the raw block from 25 to 20 terms
    because the minimum image length is 23, choosing 20 for margin rather than by
    measurement. Lengths 20, 22 and 23 are compared. THIS IS NOT A TUNING SWEEP:
    20 stays regardless of which scores best, and the only question is whether the
    choice sits on a plateau (safe) or a cliff (a fragility to disclose before
    frozen-B is read).

A2  V2 LENGTH ARTIFACT. B-DIAG audited only the raw block, and pass 1 flagged that
    a second, smaller length sensitivity could remain in V2's 125 features. Direct
    test: for each operator compare ||sig_v2(image) - sig_v2(target)|| against the
    same distance with the TARGET TRUNCATED to the image's own length. If binomial's
    gap collapses under length-matching while other operators' do not, V2 carries a
    length artifact of its own.

A3  G-POS STABILITY. Pass 1 ran 20 derangements and found the learned arm clearing
    the threshold by 12% with individual draws over the line. 100 derangements here,
    with the full distribution and the fraction exceeding the threshold reported.

Efficiency note, stated because it is a deliberate simplification: the length sweep
compares representations WITHOUT local scaling, so the three arms are like-for-like
and the hubness computation is not repeated three times. That characterises the
representation's sensitivity, which is the question, not the final pipeline's score.
"""
from __future__ import annotations

import gzip
import importlib.util
import json
import math
import pathlib
import random
from collections import defaultdict

import numpy as np

ROOT = pathlib.Path(r'F:\Prometheus')
SEARCH = ROOT / 'aporia' / 'search'
spec = importlib.util.spec_from_file_location('xg', SEARCH / 'x2_entry_gate.py')
xg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xg)
sig_v2, OPS = xg.sig_v2, xg.OPS
K, HASH_K, MIN_EXACT, MIN_TERMS, MAX_TERMS = 10, 12, 20, 25, 45

pairs = json.loads((SEARCH / 'x4_pairs.json').read_text(encoding='utf-8'))
split = json.loads((SEARCH / 'x4_split.json').read_text(encoding='utf-8'))
terms = json.loads((SEARCH / 'x4_terms.json').read_text(encoding='utf-8'))
DEV = sorted(split['dev_indices'])
print(f"\n=== X-5 pass 2 audits, DEVELOPMENT ONLY: {len(DEV)} pairs "
      f"(frozen-B {len(split['frozenB_indices'])} untouched) ===", flush=True)

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
ids = list(pool); idx_of = {k_: i for i, k_ in enumerate(ids)}
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
        if len(im) < HASH_K: continue
        for cid in index.get(tuple(im[:HASH_K]), ()):
            if cid != src and overlap(im, pool[cid]) >= MIN_EXACT:
                out.add(cid)
    return out

print("computing V2 block over pool (once, reused by all three raw lengths)...", flush=True)
V2POOL = np.nan_to_num(np.vstack([sig_v2(pool[i]) for i in ids]), nan=0.0, posinf=0.0, neginf=0.0)

def rawblock(v, k):
    a = v[:k] + [0]*max(0, k - len(v))
    return [math.copysign(math.log1p(abs(float(x))), x) for x in a]

POS = pairs['positives']
neg_by_src = defaultdict(list)
for n_ in pairs['negatives']:
    neg_by_src[(n_['op'], n_['src'])].append(n_['decoy'])

asets = {}
for i in DEV:
    p = POS[i]
    if p['src'] in pool and p['tgt'] in pool:
        asets[i] = valid_partners(p['src'], p['op'])
REAL = [i for i in DEV if i in asets and POS[i]['op'] != 'shift']

def wilson(k_, n_, z=1.96):
    if n_ == 0: return (0.0, 0.0)
    pp = k_/n_; dd = 1 + z*z/n_
    c = (pp + z*z/(2*n_))/dd
    h = z*math.sqrt(pp*(1-pp)/n_ + z*z/(4*n_*n_))/dd
    return (round(c-h, 4), round(c+h, 4))

# ---------------------------------------------------------------- A1
print("\n--- A1: raw-block length sensitivity (20 / 22 / 23) ---", flush=True)
A1 = {}
store = {}
for RK in (20, 22, 23):
    RAWP = np.vstack([rawblock(pool[i], RK) for i in ids])
    F = np.nan_to_num(np.hstack([RAWP, V2POOL]), nan=0.0, posinf=0.0, neginf=0.0)
    mu, sd = F.mean(0), F.std(0); sd[sd == 0] = 1.0
    Z = (F - mu)/sd
    RAWZ = Z[:, :RK].copy()
    dpos, dneg = [], []
    for i in DEV:
        p = POS[i]
        if p['src'] not in pool or p['tgt'] not in pool: continue
        dpos.append(Z[idx_of[p['src']]] - Z[idx_of[p['tgt']]])
        for d_ in neg_by_src.get((p['op'], p['src']), [])[:1]:
            if d_ in pool: dneg.append(Z[idx_of[p['src']]] - Z[idx_of[d_]])
    dpos, dneg = np.vstack(dpos), np.vstack(dneg)
    d = Z.shape[1]
    Li = np.linalg.inv(np.linalg.cholesky(np.cov(dpos, rowvar=False) + 1e-3*np.eye(d)))
    M = Li @ (np.cov(dneg, rowvar=False) + 1e-3*np.eye(d)) @ Li.T; M = (M + M.T)/2
    w, U = np.linalg.eigh(M); o = np.argsort(w)[::-1]; w, U = w[o], U[:, o]
    V = Li.T @ U
    KEEP = int((w > 1.0).sum())
    P = V[:, :KEEP]*np.sqrt(np.maximum(w[:KEEP] - 1.0, 0.0))
    L = Z @ P
    L = L/(np.linalg.norm(L, axis=1, keepdims=True) + 1e-9)*np.sqrt(KEEP)
    av = defaultdict(lambda: [0, 0])
    for i in DEV:
        if i not in asets: continue
        p = POS[i]; src, op = p['src'], p['op']
        img = OPS[op](pool[src])[p['offset']:]
        q = np.nan_to_num(np.concatenate([np.array(rawblock(img, RK)), sig_v2(img)]))
        q = ((q - mu)/sd) @ P
        q = q/(np.linalg.norm(q) + 1e-9)*np.sqrt(KEEP)
        dd = np.linalg.norm(L - q, axis=1); dd[idx_of[src]] = np.inf
        av[op][1] += 1
        if ids[int(np.argmin(dd))] in asets[i]: av[op][0] += 1
    A = sum(v[0] for v in av.values()); NN = sum(v[1] for v in av.values())
    def t10(Zm, sid):
        dd = np.linalg.norm(Zm - Zm[idx_of[sid]], axis=1); dd[idx_of[sid]] = np.inf
        return set(ids[j] for j in np.argsort(dd, kind='stable')[:10])
    TL = {i: t10(L, POS[i]['src']) for i in REAL}
    TR = {i: t10(RAWZ, POS[i]['src']) for i in REAL}
    kl = sum(bool(TL[i] & asets[i]) for i in REAL); kr = sum(bool(TR[i] & asets[i]) for i in REAL)
    b = sum(1 for i in REAL if (TL[i] & asets[i]) and not (TR[i] & asets[i]))
    c = sum(1 for i in REAL if (TR[i] & asets[i]) and not (TL[i] & asets[i]))
    n = len(REAL); D = (b - c)/n
    A1[RK] = {'k_kept': KEEP, 'L1_any_valid': f"{A}/{NN}", 'L1_rate': round(A/NN, 4),
              'L1_wilson': list(wilson(A, NN)),
              'L1_by_op': {k_: f"{v[0]}/{v[1]}" for k_, v in av.items()},
              'L2_learned': f"{kl}/{n}", 'L2_learned_rate': round(kl/n, 4),
              'L2_raw': f"{kr}/{n}", 'L2_raw_rate': round(kr/n, 4),
              'D': round(D, 4), 'discordance': round((b+c)/n, 4)}
    print(f"  RAW_K={RK}: k={KEEP:3d} | L1 {A}/{NN} = {A/NN:.4f} CI {A1[RK]['L1_wilson']} | "
          f"L2 learned {kl}/{n} = {kl/n:.4f} raw {kr}/{n} = {kr/n:.4f} | D {D:+.4f}", flush=True)
    if RK == 20:
        store = {'L': L, 'TL': TL, 'TR': TR, 'kl': kl, 'kr': kr, 'n': n}

l1s = [A1[k]['L1_rate'] for k in (20, 22, 23)]
l2s = [A1[k]['L2_learned_rate'] for k in (20, 22, 23)]
A1_verdict = 'PLATEAU' if (max(l1s)-min(l1s) <= 0.05 and max(l2s)-min(l2s) <= 0.05) else 'CLIFF'
print(f"  L1 spread {max(l1s)-min(l1s):.4f}, L2 spread {max(l2s)-min(l2s):.4f} -> {A1_verdict}")

# ---------------------------------------------------------------- A2
print("\n--- A2: V2 block length artifact ---", flush=True)
A2 = {}
for op in ('diff', 'partsum', 'binomial', 'moebius', 'shift'):
    raw_gap, matched_gap = [], []
    for i in DEV:
        p = POS[i]
        if p['op'] != op or i not in asets: continue
        img = OPS[op](pool[p['src']])[p['offset']:]
        tgt = pool[p['tgt']]
        a = np.nan_to_num(sig_v2(img))
        raw_gap.append(float(np.linalg.norm(a - np.nan_to_num(sig_v2(tgt)))))
        matched_gap.append(float(np.linalg.norm(a - np.nan_to_num(sig_v2(tgt[:len(img)])))))
    r, m = float(np.mean(raw_gap)), float(np.mean(matched_gap))
    A2[op] = {'n': len(raw_gap), 'gap_full_target': round(r, 4),
              'gap_length_matched_target': round(m, 4),
              'reduction': round(r - m, 4), 'reduction_frac': round((r - m)/r, 4) if r else None}
    print(f"  {op:9s} full {r:8.4f} | length-matched {m:8.4f} | reduction {r-m:+8.4f} "
          f"({A2[op]['reduction_frac']:+.3f})")
others = [A2[o]['reduction_frac'] for o in A2 if o != 'binomial']
A2_verdict = 'SECOND ARTIFACT PRESENT' if A2['binomial']['reduction_frac'] > max(others) + 0.10 \
    else 'NO SECOND ARTIFACT'
print(f"  binomial reduction {A2['binomial']['reduction_frac']:+.3f} vs max other "
      f"{max(others):+.3f} -> {A2_verdict}")

# ---------------------------------------------------------------- A3
print("\n--- A3: G-pos stability over 100 derangements ---", flush=True)
mV = float(np.mean([len(asets[i]) for i in REAL]))
adj = 10*mV/N_POOL; thr = 3*adj
prng = random.Random(20260828)
pl, pr = [], []
for _ in range(100):
    perm = REAL[:]
    prng.shuffle(perm)
    while any(x == y for x, y in zip(REAL, perm)):
        prng.shuffle(perm)
    pl.append(sum(bool(store['TL'][i] & asets[j]) for i, j in zip(REAL, perm))/store['n'])
    pr.append(sum(bool(store['TR'][i] & asets[j]) for i, j in zip(REAL, perm))/store['n'])
pl, pr = np.array(pl), np.array(pr)
fl = float((pl > thr).mean()); fr = float((pr > thr).mean())
A3 = {'n_derangements': 100, 'mean_V': round(mV, 4), 'adjusted_chance': round(adj, 6),
      'threshold_3x': round(thr, 6),
      'learned': {'mean': round(float(pl.mean()), 5), 'min': round(float(pl.min()), 5),
                  'max': round(float(pl.max()), 5), 'p90': round(float(np.quantile(pl, 0.9)), 5),
                  'frac_over_threshold': round(fl, 3), 'true_rate': round(store['kl']/store['n'], 4)},
      'raw': {'mean': round(float(pr.mean()), 5), 'min': round(float(pr.min()), 5),
              'max': round(float(pr.max()), 5), 'p90': round(float(np.quantile(pr, 0.9)), 5),
              'frac_over_threshold': round(fr, 3), 'true_rate': round(store['kr']/store['n'], 4)}}
A3['verdict'] = 'G-POS UNRELIABLE' if max(fl, fr) > 0.10 else 'G-POS RELIABLE'
print(f"  mean|V| {mV:.4f} -> adjusted chance {adj:.6f}, threshold {thr:.6f}")
print(f"  learned permuted mean {pl.mean():.5f} min {pl.min():.5f} max {pl.max():.5f} "
      f"p90 {np.quantile(pl,0.9):.5f} | over threshold {fl:.1%} | true {store['kl']/store['n']:.4f}")
print(f"  raw     permuted mean {pr.mean():.5f} min {pr.min():.5f} max {pr.max():.5f} "
      f"p90 {np.quantile(pr,0.9):.5f} | over threshold {fr:.1%} | true {store['kr']/store['n']:.4f}")
print(f"  -> {A3['verdict']}")

out = {'A1_raw_block_length': A1, 'A1_verdict': A1_verdict,
       'A1_note': 'RAW_K stays 20 regardless of which length scored best; this characterises sensitivity',
       'A2_v2_length_artifact': A2, 'A2_verdict': A2_verdict,
       'A3_gpos_stability': A3, 'frozen_quantities_computed': False}
(SEARCH / 'x5_pass2_audit.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print("\nNO frozen quantity computed. frozen-B untouched.")
