"""CAMPAIGN X-5 pass 1 — B-DIAG fix, refit on DEVELOPMENT ONLY, and G-pos re-verified.

frozen-B is not touched. No frozen quantity is computed in this file.

THE BUG, AND THE FIX. B-DIAG established that `binomial` is the only operator whose
operator images (23-24 terms, capped at 24) are shorter than the 25-term raw block,
so every binomial query was zero-padded in exactly the positions where pool
candidates hold real values — and because binomial images grow fastest, those are
the largest-magnitude components in the vector. Diagnostic evidence: 80 of 80
binomial pairs padded against 0 of 80 for every other operator, and a mean
projected query norm of 439.0 against 70-190 elsewhere.

FIX: the raw block is built from the first **20** terms rather than 25. The minimum
image length across all five operators is 23, so no operator is padded and the
comparison is length-symmetric for every one of them. This changes the feature
space for BOTH arms — the learned metric and the raw-term baseline — so the
baseline is refit on the same footing and X-3's 25-term figure is not comparable to
what follows. Stated rather than quietly carried.

CONSEQUENCE FOR POWER, AND WHY IT IS RECOMPUTED RATHER THAN INHERITED. The X-4 stub
fixed MDE = 0.0375 from a discordance rate of 0.2250 measured under the UNFIXED
metric. Inheriting that would be the wrong-population error firing a sixth time.
The discordance is re-measured here and the MDE restated from it.

G-POS re-verified with MULTIPLE derangements. P118 used a single permutation and
flagged that one draw has unestimated sampling error; 20 derangements are run here
and the permuted rate is reported with an interval.
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

RAW_K = 20                      # THE FIX: below the 23-term minimum image length
K, HASH_K, MIN_EXACT, MIN_TERMS, MAX_TERMS = 10, 12, 20, 25, 45
N_PERM = 20

pairs = json.loads((SEARCH / 'x4_pairs.json').read_text(encoding='utf-8'))
split = json.loads((SEARCH / 'x4_split.json').read_text(encoding='utf-8'))
terms = json.loads((SEARCH / 'x4_terms.json').read_text(encoding='utf-8'))
DEV = sorted(split['dev_indices'])
print(f"\n=== X-5 refit, DEVELOPMENT ONLY: {len(DEV)} pairs "
      f"(frozen-B {len(split['frozenB_indices'])} RESERVED, not opened) ===", flush=True)

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
print(f"pool: {len(pool):,}", flush=True)

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

def rawvec(v):
    a = v[:RAW_K] + [0]*max(0, RAW_K - len(v))
    return [math.copysign(math.log1p(abs(float(x))), x) for x in a]

def feat(v):
    return np.concatenate([np.array(rawvec(v), dtype=float), sig_v2(v)])

print(f"building feature matrix (raw block = {RAW_K} terms)...", flush=True)
F = np.nan_to_num(np.vstack([feat(pool[i]) for i in ids]), nan=0.0, posinf=0.0, neginf=0.0)
mu, sd = F.mean(0), F.std(0); sd[sd == 0] = 1.0
Zf = (F - mu)/sd
RAWZ = Zf[:, :RAW_K].copy()
print(f"features: {Zf.shape[1]} (raw {RAW_K} + V2 125)", flush=True)

POS = pairs['positives']
neg_by_src = defaultdict(list)
for n_ in pairs['negatives']:
    neg_by_src[(n_['op'], n_['src'])].append(n_['decoy'])

dpos, dneg = [], []
for i in DEV:
    p = POS[i]
    if p['src'] not in pool or p['tgt'] not in pool: continue
    dpos.append(Zf[idx_of[p['src']]] - Zf[idx_of[p['tgt']]])
    for d_ in neg_by_src.get((p['op'], p['src']), [])[:1]:
        if d_ in pool:
            dneg.append(Zf[idx_of[p['src']]] - Zf[idx_of[d_]])
dpos, dneg = np.vstack(dpos), np.vstack(dneg)
d = Zf.shape[1]
S_pos = np.cov(dpos, rowvar=False) + 1e-3*np.eye(d)
S_neg = np.cov(dneg, rowvar=False) + 1e-3*np.eye(d)
Li = np.linalg.inv(np.linalg.cholesky(S_pos))
M = Li @ S_neg @ Li.T; M = (M + M.T)/2
w, U = np.linalg.eigh(M); o = np.argsort(w)[::-1]; w, U = w[o], U[:, o]
V = Li.T @ U
KEEP = int((w > 1.0).sum())                     # same stated rule, unchanged
P = V[:, :KEEP] * np.sqrt(np.maximum(w[:KEEP] - 1.0, 0.0))
LEARN = Zf @ P
LEARN = LEARN/(np.linalg.norm(LEARN, axis=1, keepdims=True) + 1e-9)*np.sqrt(KEEP)
print(f"eigenvalues > 1.0: {KEEP} of {d} (rule unchanged); learned space {LEARN.shape[1]} dims", flush=True)

def hub(Z):
    Za = np.ascontiguousarray(Z, dtype=np.float32)
    sq = (Za**2).sum(1); n = Za.shape[0]
    r = np.empty(n, dtype=np.float32); occ = Counter()
    for s in range(0, n, 512):
        e = min(s+512, n)
        d2 = sq[s:e, None] + sq[None, :] - 2.0*(Za[s:e] @ Za.T)
        np.maximum(d2, 0, out=d2)
        for j in range(e-s): d2[j, s+j] = np.inf
        part = np.argpartition(d2, K, axis=1)[:, :K+1]
        for j in range(e-s):
            c = part[j]; c = c[np.argsort(d2[j, c])][:K]
            r[s+j] = np.sqrt(d2[j, c[-1]]); occ.update(c.tolist())
    oc = np.array([occ.get(i, 0) for i in range(n)], dtype=float)
    m_, s_ = oc.mean(), oc.std()
    return np.maximum(r, 1e-6), (float(((oc-m_)**3).mean()/(s_**3)) if s_ > 0 else 0.0)

RK_L, skL = hub(LEARN); RK_R, skR = hub(RAWZ)
UL, UR = skL > 1.0, skR > 1.0
print(f"hubness re-measured: learned skew {skL:.3f} ({'corrected' if UL else 'plain'}) | "
      f"raw skew {skR:.3f} ({'corrected' if UR else 'plain'})", flush=True)

asets = {}
for i in DEV:
    p = POS[i]
    if p['src'] in pool and p['tgt'] in pool:
        asets[i] = valid_partners(p['src'], p['op'])

def wilson(k_, n_, z=1.96):
    if n_ == 0: return (0.0, 0.0)
    pp = k_/n_; dd = 1 + z*z/n_
    c = (pp + z*z/(2*n_))/dd
    h = z*math.sqrt(pp*(1-pp)/n_ + z*z/(4*n_*n_))/dd
    return (round(c-h, 4), round(c+h, 4))

st = defaultdict(lambda: [0, 0]); av = defaultdict(lambda: [0, 0])
for i in DEV:
    if i not in asets: continue
    p = POS[i]; src, tgt, op = p['src'], p['tgt'], p['op']
    img = OPS[op](pool[src])[p['offset']:]
    q = np.nan_to_num(feat(img)); q = ((q - mu)/sd) @ P
    q = q/(np.linalg.norm(q) + 1e-9)*np.sqrt(KEEP)
    dd = np.linalg.norm(LEARN - q, axis=1)
    if UL:
        kq = np.sort(np.partition(dd, K)[:K+1])[K-1]
        dd = dd/np.sqrt(max(kq, 1e-6)*RK_L)
    dd[idx_of[src]] = np.inf
    top = ids[int(np.argmin(dd))]
    st[op][1] += 1; av[op][1] += 1
    if top == tgt: st[op][0] += 1
    if top in asets[i]: av[op][0] += 1
S = sum(v[0] for v in st.values()); A = sum(v[0] for v in av.values()); N = sum(v[1] for v in st.values())
lo, hi = wilson(A, N)
print(f"\nL1 dev strict    {S}/{N} = {S/N:.4f}  {dict((k_, f'{v[0]}/{v[1]}') for k_, v in st.items())}")
print(f"L1 dev any-valid {A}/{N} = {A/N:.4f}  {dict((k_, f'{v[0]}/{v[1]}') for k_, v in av.items())}")
print(f"  Wilson 95% CI ({lo}, {hi})")

def top10(Z, sid, rk, use):
    dd = np.linalg.norm(Z - Z[idx_of[sid]], axis=1)
    if use:
        kq = np.sort(np.partition(dd, K)[:K+1])[K-1]
        dd = dd/np.sqrt(max(kq, 1e-6)*rk)
    dd[idx_of[sid]] = np.inf
    return set(ids[j] for j in np.argsort(dd, kind='stable')[:10])

REAL = [i for i in DEV if i in asets and POS[i]['op'] != 'shift']
TL = {i: top10(LEARN, POS[i]['src'], RK_L, UL) for i in REAL}
TR = {i: top10(RAWZ, POS[i]['src'], RK_R, UR) for i in REAL}
hl = {i: bool(TL[i] & asets[i]) for i in REAL}
hr = {i: bool(TR[i] & asets[i]) for i in REAL}
kl, kr, n = sum(hl.values()), sum(hr.values()), len(REAL)
b = sum(1 for i in REAL if hl[i] and not hr[i]); c = sum(1 for i in REAL if hr[i] and not hl[i])
D = (b - c)/n
se = math.sqrt(max((b + c) - (b - c)**2/n, 0))/n
disc = (b + c)/n
MDE = 2*math.sqrt(disc/640) if disc > 0 else 0.0
print(f"\nL2 dev four real ops (n={n}): learned {kl}/{n} = {kl/n:.4f} | raw {kr}/{n} = {kr/n:.4f}")
print(f"D_dev = {D:+.4f} CI [{D-1.96*se:.4f}, {D+1.96*se:.4f}] (b={b}, c={c})")
print(f"discordance {disc:.4f} -> MDE at frozen-B n=640 is {MDE:.4f} "
      f"(X-4 stub had 0.0375 under the UNFIXED metric)")

prng = random.Random(20260827)
pl, pr = [], []
for _ in range(N_PERM):
    perm = REAL[:]
    prng.shuffle(perm)
    while any(x == y for x, y in zip(REAL, perm)):
        prng.shuffle(perm)
    pl.append(sum(bool(TL[i] & asets[j]) for i, j in zip(REAL, perm))/n)
    pr.append(sum(bool(TR[i] & asets[j]) for i, j in zip(REAL, perm))/n)
pl, pr = np.array(pl), np.array(pr)
print(f"\nG-pos permutation null over {N_PERM} derangements:")
print(f"  learned permuted {pl.mean():.5f} (min {pl.min():.5f} max {pl.max():.5f}) vs true {kl/n:.4f}")
print(f"  raw     permuted {pr.mean():.5f} (min {pr.min():.5f} max {pr.max():.5f}) vs true {kr/n:.4f}")

res = {'raw_block_terms': RAW_K, 'fix': 'raw block cut from 25 to 20 terms; minimum image length is 23 so no operator is padded',
       'features': int(d), 'k_rule_unchanged': 'lambda > 1.0', 'k_kept': KEEP,
       'hubness': {'learned_skew': round(skL, 3), 'learned_corrected': bool(UL),
                   'raw_skew': round(skR, 3), 'raw_corrected': bool(UR)},
       'L1_dev': {'strict': f"{S}/{N}", 'strict_rate': round(S/N, 4), 'any_valid': f"{A}/{N}",
                  'any_valid_rate': round(A/N, 4), 'wilson_95': [lo, hi],
                  'by_op_strict': {k_: f"{v[0]}/{v[1]}" for k_, v in st.items()},
                  'by_op_any_valid': {k_: f"{v[0]}/{v[1]}" for k_, v in av.items()}},
       'L2_dev': {'learned': f"{kl}/{n}", 'learned_rate': round(kl/n, 4),
                  'raw': f"{kr}/{n}", 'raw_rate': round(kr/n, 4),
                  'D': round(D, 4), 'b': b, 'c': c,
                  'ci95_paired': [round(D-1.96*se, 4), round(D+1.96*se, 4)],
                  'discordance': round(disc, 4)},
       'MDE_frozenB_n640': round(MDE, 4), 'MDE_x4_stub_superseded': 0.0375,
       'G_pos_permutation': {'n_derangements': N_PERM,
                             'learned_mean': round(float(pl.mean()), 5),
                             'learned_min': round(float(pl.min()), 5), 'learned_max': round(float(pl.max()), 5),
                             'raw_mean': round(float(pr.mean()), 5),
                             'raw_min': round(float(pr.min()), 5), 'raw_max': round(float(pr.max()), 5)},
       'frozen_quantities_computed': False}
(SEARCH / 'x5_refit_results.json').write_text(json.dumps(res, indent=1), encoding='utf-8')
print("\nNO frozen quantity computed. frozen-B untouched.")
