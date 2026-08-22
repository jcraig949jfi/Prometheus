"""CAMPAIGN X-4 pass 2/3 — fit the learned metric on DEVELOPMENT ONLY.

NEITHER frozen split is touched. frozenA is pass 3's decision split; frozenB is
RESERVED for a successor campaign and is not opened by X-4 at all. Both index
lists are loaded solely to be excluded. M0-M5 are not adjudicated.

WHAT IS BEING LEARNED. Feature space = the raw-25 sign-log vector concatenated
with V2's 125 features, z-scored over the pool (150 dims). Closed-form metric
learning: with S_pos the covariance of (z_src - z_tgt) over development POSITIVES
and S_neg the covariance of (z_src - z_decoy) over development NEGATIVES, solve
the generalised eigenproblem S_neg v = lambda S_pos v. Directions with large
lambda are those along which unrelated pairs vary MORE than related pairs — i.e.
exactly the directions that separate structure from coincidence.

CHOOSING k WITHOUT A DISGUISED HYPERPARAMETER SEARCH. k is fixed by a rule
computed from the eigenspectrum alone: KEEP EVERY DIRECTION WITH lambda > 1.0.
That threshold is not a tuning knob — lambda > 1 is precisely the statement "along
this direction, decoy pairs are more spread out than true pairs", so it is the
natural boundary between informative and anti-informative directions and it is
readable off the spectrum before any retrieval is run. No values of k were tried
and compared; trying them and keeping the best would be a hyperparameter search
wearing a disguise, and on 400 development pairs with no reviewer it would not be
caught.

DEVELOPMENT D IS NOT AN UNBIASED ESTIMATE, AND THIS IS THE POINT. The metric is
fitted to pull sources and targets together on these very pairs, so development L2
IS the training objective. A strong development D therefore means very little.
A WEAK one would be damning — it would say the method cannot even fit the data it
was given. That asymmetry is why this pass reports development D at all, and why
the decision waits for frozen-A.

NO FROZEN QUANTITY IS COMPUTED IN THIS FILE.
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
K, HASH_K, MIN_EXACT, MIN_TERMS, MAX_TERMS = 10, 12, 20, 25, 45

pairs = json.loads((SEARCH / 'x4_pairs.json').read_text(encoding='utf-8'))
split = json.loads((SEARCH / 'x4_split.json').read_text(encoding='utf-8'))
terms = json.loads((SEARCH / 'x4_terms.json').read_text(encoding='utf-8'))
DEV = sorted(split['dev_indices'])
print(f"\n=== X-4 DEVELOPMENT ONLY: {len(DEV)} pairs "
      f"(frozenA {len(split['frozenA_indices'])} and frozenB {len(split['frozenB_indices'])} excluded) ===", flush=True)

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
print(f"X-4 pool: {N_POOL:,}", flush=True)

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
    a = v[:25] + [0]*max(0, 25 - len(v))
    return [math.copysign(math.log1p(abs(float(x))), x) for x in a]

def feat(v):
    return np.concatenate([np.array(rawvec(v), dtype=float), sig_v2(v)])

print("building 150-dim feature matrix...", flush=True)
F = np.vstack([feat(pool[i]) for i in ids])
F = np.nan_to_num(F, nan=0.0, posinf=0.0, neginf=0.0)
mu, sd = F.mean(0), F.std(0); sd[sd == 0] = 1.0
Zf = (F - mu)/sd
RAWZ = Zf[:, :25].copy()                       # the baseline arm: raw terms only
print(f"features: {Zf.shape[1]} (raw 25 + V2 125)", flush=True)

# ------------------------------------------------- fit on DEVELOPMENT ONLY
POS = pairs['positives']
neg_by_src = defaultdict(list)
for n_ in pairs['negatives']:
    neg_by_src[(n_['op'], n_['src'])].append(n_['decoy'])

dpos, dneg = [], []
for i in DEV:
    p = POS[i]
    if p['src'] not in pool or p['tgt'] not in pool:
        continue
    dpos.append(Zf[idx_of[p['src']]] - Zf[idx_of[p['tgt']]])
    for d_ in neg_by_src.get((p['op'], p['src']), [])[:1]:
        if d_ in pool:
            dneg.append(Zf[idx_of[p['src']]] - Zf[idx_of[d_]])
dpos = np.vstack(dpos); dneg = np.vstack(dneg)
print(f"fitting on {len(dpos)} positive differences and {len(dneg)} negative differences (DEV only)", flush=True)

d = Zf.shape[1]
S_pos = np.cov(dpos, rowvar=False) + 1e-3*np.eye(d)
S_neg = np.cov(dneg, rowvar=False) + 1e-3*np.eye(d)
Lc = np.linalg.cholesky(S_pos)
Li = np.linalg.inv(Lc)
Msym = Li @ S_neg @ Li.T
Msym = (Msym + Msym.T)/2
w, U = np.linalg.eigh(Msym)
order = np.argsort(w)[::-1]
w, U = w[order], U[:, order]
V = Li.T @ U                                    # generalised eigenvectors
KEEP = int((w > 1.0).sum())                     # THE STATED RULE, no search
print(f"eigenvalues > 1.0: {KEEP} of {d}   (top five {np.round(w[:5],3).tolist()}, "
      f"median {np.median(w):.3f}, min {w[-1]:.3f})", flush=True)
P = V[:, :KEEP] * np.sqrt(np.maximum(w[:KEEP] - 1.0, 0.0))    # weight by informativeness
LEARN = Zf @ P
LEARN = LEARN / (np.linalg.norm(LEARN, axis=1, keepdims=True) + 1e-9) * np.sqrt(KEEP)
print(f"learned space: {LEARN.shape[1]} dims", flush=True)

def hub(Z):
    Za = np.ascontiguousarray(Z, dtype=np.float32)
    sq = (Za**2).sum(1); n = Za.shape[0]
    r = np.empty(n, dtype=np.float32); occ = Counter()
    for s in range(0, n, 512):
        e = min(s+512, n)
        d2 = sq[s:e, None] + sq[None, :] - 2.0*(Za[s:e] @ Za.T)
        np.maximum(d2, 0, out=d2)
        for j in range(e-s):
            d2[j, s+j] = np.inf
        part = np.argpartition(d2, K, axis=1)[:, :K+1]
        for j in range(e-s):
            c = part[j]; c = c[np.argsort(d2[j, c])][:K]
            r[s+j] = np.sqrt(d2[j, c[-1]]); occ.update(c.tolist())
    o = np.array([occ.get(i, 0) for i in range(n)], dtype=float)
    m, s_ = o.mean(), o.std()
    sk = float(((o-m)**3).mean()/(s_**3)) if s_ > 0 else 0.0
    return np.maximum(r, 1e-6), m, s_, float(o.max()), sk

RK_L, mL, sL, mxL, skL = hub(LEARN)
RK_R, mR, sR, mxR, skR = hub(RAWZ)
print(f"hubness RE-MEASURED  learned: skew {skL:.3f} max {int(mxL)} | raw: skew {skR:.3f} max {int(mxR)}", flush=True)
USE_L, USE_R = skL > 1.0, skR > 1.0

asets = {}
for i in DEV:
    p = POS[i]
    if p['src'] in pool and p['tgt'] in pool:
        asets[i] = valid_partners(p['src'], p['op'])
missing = sum(1 for i in DEV if i in asets and POS[i]['tgt'] not in asets[i])

def l1(Z, rk, use):
    st = defaultdict(lambda: [0, 0]); av = defaultdict(lambda: [0, 0])
    for i in DEV:
        if i not in asets: continue
        p = POS[i]; src, tgt, op = p['src'], p['tgt'], p['op']
        img = OPS[op](pool[src])[p['offset']:]
        q = np.nan_to_num(feat(img)); q = (q - mu)/sd
        q = q @ P
        q = q/(np.linalg.norm(q) + 1e-9)*np.sqrt(KEEP)
        dd = np.linalg.norm(Z - q, axis=1)
        if use:
            kq = np.sort(np.partition(dd, K)[:K+1])[K-1]
            dd = dd/np.sqrt(max(kq, 1e-6)*rk)
        dd[idx_of[src]] = np.inf
        top = ids[int(np.argmin(dd))]
        st[op][1] += 1; av[op][1] += 1
        if top == tgt: st[op][0] += 1
        if top in asets[i]: av[op][0] += 1
    return st, av

def l2_hits(Z, rk, use):
    out = {}
    for i in DEV:
        if i not in asets: continue
        src = POS[i]['src']
        dd = np.linalg.norm(Z - Z[idx_of[src]], axis=1)
        if use:
            kq = np.sort(np.partition(dd, K)[:K+1])[K-1]
            dd = dd/np.sqrt(max(kq, 1e-6)*rk)
        dd[idx_of[src]] = np.inf
        top = set(ids[j] for j in np.argsort(dd, kind='stable')[:10])
        out[i] = bool(top & asets[i])
    return out

def wilson(k_, n_, z=1.96):
    if n_ == 0: return (0.0, 0.0)
    p = k_/n_; dd = 1 + z*z/n_
    c = (p + z*z/(2*n_))/dd
    h = z*math.sqrt(p*(1-p)/n_ + z*z/(4*n_*n_))/dd
    return (round(c-h, 4), round(c+h, 4))

st, av = l1(LEARN, RK_L, USE_L)
S = sum(v[0] for v in st.values()); A = sum(v[0] for v in av.values()); NL = sum(v[1] for v in st.values())
lo, hi = wilson(A, NL)

hl, hr = l2_hits(LEARN, RK_L, USE_L), l2_hits(RAWZ, RK_R, USE_R)
REAL = [i for i in DEV if i in asets and POS[i]['op'] != 'shift']
SH = [i for i in DEV if i in asets and POS[i]['op'] == 'shift']
kl = sum(hl[i] for i in REAL); kr = sum(hr[i] for i in REAL); n = len(REAL)
b = sum(1 for i in REAL if hl[i] and not hr[i]); c = sum(1 for i in REAL if hr[i] and not hl[i])
D = (b - c)/n
se_pair = math.sqrt(max((b + c) - (b - c)**2/n, 0))/n
disc = (b + c)/n
mde_640 = 2*math.sqrt(disc/640) if disc > 0 else 0.0

res = {'development_pairs': NL, 'pool_size': N_POOL,
       'frozenA_untouched': len(split['frozenA_indices']), 'frozenB_reserved': len(split['frozenB_indices']),
       'features': int(d), 'k_rule': 'keep every generalised eigenvalue > 1.0; no k values were tried',
       'k_kept': KEEP, 'eig_top5': [round(float(x), 4) for x in w[:5]],
       'eig_median': round(float(np.median(w)), 4), 'eig_min': round(float(w[-1]), 4),
       'hubness': {'learned_skew': round(skL, 3), 'learned_max': int(mxL), 'learned_corrected': bool(USE_L),
                   'raw_skew': round(skR, 3), 'raw_max': int(mxR), 'raw_corrected': bool(USE_R)},
       'recorded_target_absent_from_answer_set': missing,
       'L1_dev': {'strict': f"{S}/{NL}", 'strict_rate': round(S/NL, 4),
                  'any_valid': f"{A}/{NL}", 'any_valid_rate': round(A/NL, 4),
                  'wilson_95': [lo, hi], 'K0_threshold_for_pass3': 0.90,
                  'by_op_strict': {k_: f"{v[0]}/{v[1]}" for k_, v in st.items()},
                  'by_op_any_valid': {k_: f"{v[0]}/{v[1]}" for k_, v in av.items()}},
       'L2_dev_four_real_ops': {'learned': f"{kl}/{n}", 'learned_rate': round(kl/n, 4),
                                'learned_wilson': list(wilson(kl, n)),
                                'raw': f"{kr}/{n}", 'raw_rate': round(kr/n, 4),
                                'raw_wilson': list(wilson(kr, n)),
                                'shift_control_learned': f"{sum(hl[i] for i in SH)}/{len(SH)}",
                                'shift_control_raw': f"{sum(hr[i] for i in SH)}/{len(SH)}"},
       'D_dev': {'value': round(D, 4), 'b_learned_only': b, 'c_raw_only': c, 'n': n,
                 'se_paired': round(se_pair, 5),
                 'ci95_paired': [round(D - 1.96*se_pair, 4), round(D + 1.96*se_pair, 4)],
                 'discordance_rate': round(disc, 4),
                 'BIAS_WARNING': 'development D is the training objective, not an estimate; '
                                 'a strong value means little, a weak one would be damning'},
       'MDE_implication': {'preregistered_mde_at_640': 0.0265,
                           'preregistered_assumed_discordance': 0.1125,
                           'observed_dev_discordance': round(disc, 4),
                           'implied_mde_at_640': round(mde_640, 4)},
       'frozen_quantities_computed': False}
(SEARCH / 'x4_dev_results.json').write_text(json.dumps(res, indent=1), encoding='utf-8')

print(f"\nsanity: recorded target absent from own answer set = {missing}")
print(f"L1 dev strict    {S}/{NL} = {S/NL:.4f}   {res['L1_dev']['by_op_strict']}")
print(f"L1 dev any-valid {A}/{NL} = {A/NL:.4f}   {res['L1_dev']['by_op_any_valid']}")
print(f"  Wilson 95% CI ({lo}, {hi})   K0 in pass 3 needs LB > 0.90")
print(f"\nL2 dev (four real ops, n={n}):  learned {kl}/{n} = {kl/n:.4f} CI {res['L2_dev_four_real_ops']['learned_wilson']}")
print(f"                                raw     {kr}/{n} = {kr/n:.4f} CI {res['L2_dev_four_real_ops']['raw_wilson']}")
print(f"  shift control: learned {res['L2_dev_four_real_ops']['shift_control_learned']} "
      f"raw {res['L2_dev_four_real_ops']['shift_control_raw']}")
print(f"\nD_dev = {D:+.4f}  (b={b} learned-only, c={c} raw-only, n={n})  paired CI "
      f"{res['D_dev']['ci95_paired']}")
print(f"discordance {disc:.4f} vs preregistered assumption 0.1125 -> implied MDE at n=640 is "
      f"{mde_640:.4f} (preregistered 0.0265)")
print("\nNO frozen quantity computed. frozenA and frozenB untouched. M0-M5 not adjudicated.")
