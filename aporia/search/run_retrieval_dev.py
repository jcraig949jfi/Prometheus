"""CAMPAIGN X pass 2 — signature design + DEVELOPMENT-ONLY retrieval.

THE FROZEN SPLIT IS NOT TOUCHED. Frozen indices are loaded only to EXCLUDE
those positives. No D1-D5 branch is adjudicated here; those are read once,
against frozen, in pass 3.

------------------------------------------------------------------------
THE CRITICAL DESIGN POINT, resolved explicitly
------------------------------------------------------------------------
The task is "given A, retrieve B = op(A)". There are three distinct framings
and they test completely different claims. This pass runs all three, because
conflating them is how a retrieval result gets over-read.

  L0  OPERATOR-AWARE EXACT (ceiling, CIRCULAR — reported, never used as
      evidence): compute op(A) exactly, hash-match it in the pool. This is
      ~100% by construction, because the benchmark pairs were FOUND by exact
      hash matching. It measures nothing about signatures; it is included
      only to show the ceiling and to prove the pool contains the targets.

  L1  OPERATOR-AWARE SIGNATURE (necessary condition): compute op(A), take
      its SIGNATURE, retrieve by signature distance. This asks: is the
      signature discriminative enough to identify a sequence you have
      literally already computed, among tens of thousands of distractors?
      If L1 fails, the signature is not a usable retrieval key at all and L2
      cannot possibly succeed.

  L2  OPERATOR-AGNOSTIC (THE SUBSTRATE CLAIM): signature A directly and
      retrieve B without knowing or computing any operator. This is the
      actual "signature-keyed structural map" claim — that behavioral
      representation places related objects near each other regardless of
      the transformation relating them. This is the hard one and the one
      that matters for the Sleeping Beauties, where no operator is known.

Note honestly: for a KNOWN finite operator set, L0 is the right production
algorithm and needs no signature. Signatures only earn their keep where the
operator is unknown (L2) or exact matching fails (offsets, truncation).

------------------------------------------------------------------------
SIGNATURE FEATURES (each justified; all computed from terms alone)
------------------------------------------------------------------------
  growth class + fitted slopes   coarse scale behaviour (P21's battery)
  log-ratio quantiles            scale-free growth SHAPE, not magnitude
  sign statistics                alternation structure survives many ops
  mod-p residue fingerprints     arithmetic structure invariant to scale
                                 (the C11 mod-p fingerprint idea)
  normalised difference moments  local shape independent of units
  leading-digit distribution     scale-free distributional fingerprint

Only the scale-free families (sign, mod-p, leading digit) have any prospect
of surviving a transformation like differencing or partial summation, which
is stated BEFORE the numbers exist.

Retrieval pool: the 358 benchmark sequences PLUS 20,000 blinded distractors
drawn from the corpus, so retrieval is not trivially easy. Distractors are
blinded with their own id space and never mapped back in this script.
"""
from __future__ import annotations

import gzip
import json
import math
import pathlib
import random
import sys

import numpy as np

ROOT = pathlib.Path(r'F:\Prometheus')
SEARCH = ROOT / 'aporia' / 'search'
sys.path.insert(0, str(SEARCH))
from growth_battery import growth_class

rng = random.Random(20260823)
N_DISTRACT = 20000
MIN_TERMS = 25
MAX_TERMS = 45

pairs = json.loads((SEARCH / 'benchmark_pairs.json').read_text(encoding='utf-8'))
split = json.loads((SEARCH / 'benchmark_frozen_split.json').read_text(encoding='utf-8'))
terms = json.loads((SEARCH / 'benchmark_terms.json').read_text(encoding='utf-8'))
FROZEN = set(split['frozen_indices'])
DEV = [i for i in split['dev_indices']]
print(f"development positives: {len(DEV)} (frozen {len(FROZEN)} NOT touched)", flush=True)

# ---------------------------------------------------------------- pool
pool = {k: v for k, v in terms.items()}
def nondegenerate(v):
    w = v[:MIN_TERMS]
    return len(set(w)) >= 8 and not all(x == w[-1] for x in w[-6:])

cands = []
with gzip.open(ROOT / 'prometheus_data/oeis/stripped.gz', 'rt', encoding='utf-8', errors='replace') as fh:
    for line in fh:
        if line.startswith('#'):
            continue
        parts = line.strip().rstrip(',').split(',')
        if len(parts) < MIN_TERMS + 1:
            continue
        try:
            t = [int(x) for x in parts[1:MAX_TERMS + 1]]
        except ValueError:
            continue
        if len(t) >= MIN_TERMS and nondegenerate(t):
            cands.append(t)
rng.shuffle(cands)
for i, t in enumerate(cands[:N_DISTRACT]):
    pool[f"D{i:06d}"] = t
print(f"retrieval pool: {len(pool):,} sequences ({len(terms)} benchmark + {N_DISTRACT:,} distractors)", flush=True)

# ---------------------------------------------------------------- signature
def signature(v):
    a = [int(x) for x in v[:MAX_TERMS]]
    n = len(a)
    f = []
    # growth class one-hot + slopes
    gc, diag = growth_class(a)
    f += [1.0 if gc == c else 0.0 for c in ('POLY', 'EXP', 'SUPEREXP', 'ABSTAIN')]
    f += [float(diag.get('poly_slope', 0.0)), float(diag.get('exp_slope', 0.0))]
    # log-ratio quantiles (scale-free growth shape)
    lr = []
    for i in range(n - 1):
        if a[i] != 0 and a[i + 1] != 0:
            lr.append(math.log(abs(a[i + 1]) / abs(a[i])))
    lr = lr or [0.0]
    f += [float(np.quantile(lr, q)) for q in (0.1, 0.25, 0.5, 0.75, 0.9)]
    # sign structure
    signs = [1 if x > 0 else (-1 if x < 0 else 0) for x in a]
    f.append(sum(1 for s in signs if s > 0) / n)
    f.append(sum(1 for i in range(n - 1) if signs[i] * signs[i + 1] < 0) / max(n - 1, 1))
    # mod-p fingerprints (arithmetic structure, scale-invariant)
    for p in (2, 3, 5, 7):
        res = [x % p for x in a]
        counts = np.array([res.count(r) for r in range(p)], dtype=float) / n
        f.append(float(counts[0]))                                  # density of 0 mod p
        nz = counts[counts > 0]
        f.append(float(-(nz * np.log(nz)).sum()) if len(nz) else 0.0)   # residue entropy
    # normalised difference moments
    d = []
    for i in range(n - 1):
        base = abs(a[i]) if a[i] != 0 else 1
        d.append((a[i + 1] - a[i]) / base)
    d = np.array(d or [0.0], dtype=float)
    d = np.clip(d, -1e6, 1e6)
    f += [float(d.mean()), float(d.std()), float(np.median(d))]
    # leading-digit distribution
    ld = [int(str(abs(x))[0]) for x in a if x != 0] or [1]
    hist = np.array([ld.count(k) for k in range(1, 10)], dtype=float) / len(ld)
    f += [float(x) for x in hist]
    return np.array(f, dtype=float)

ids = list(pool)
print("computing signatures...", flush=True)
SIG = np.vstack([signature(pool[i]) for i in ids])
SIG = np.nan_to_num(SIG, nan=0.0, posinf=0.0, neginf=0.0)
mu, sd = SIG.mean(0), SIG.std(0)
sd[sd == 0] = 1.0
SIGZ = (SIG - mu) / sd
idx_of = {k: i for i, k in enumerate(ids)}
print(f"signature dim: {SIG.shape[1]}", flush=True)

# raw-term baseline vector: first 25 terms, sign-log compressed (scale handled)
def rawvec(v):
    a = v[:25] + [0] * max(0, 25 - len(v))
    return np.array([math.copysign(math.log1p(abs(float(x))), x) for x in a], dtype=float)
RAW = np.vstack([rawvec(pool[i]) for i in ids])
RAW = np.nan_to_num(RAW)
rmu, rsd = RAW.mean(0), RAW.std(0); rsd[rsd == 0] = 1.0
RAWZ = (RAW - rmu) / rsd
# growth/magnitude-only baseline
GM = SIGZ[:, :6].copy()
# shuffled-signature baseline: permute the feature-to-object assignment
perm = np.random.default_rng(20260823).permutation(len(ids))
SHUF = SIGZ[perm]

# ---------------------------------------------------------------- operators
def op_diff(a): return [a[i+1]-a[i] for i in range(len(a)-1)]
def op_partsum(a):
    out, s = [], 0
    for x in a: s += x; out.append(s)
    return out
def op_binomial(a, cap=24):
    a = a[:cap]
    return [sum(math.comb(n, k)*a[k] for k in range(n+1)) for n in range(len(a))]
def mobius(n):
    m, p, c = n, 2, 0
    while p*p <= m:
        if m % p == 0:
            m //= p
            if m % p == 0: return 0
            c += 1
        p += 1
    if m > 1: c += 1
    return -1 if c % 2 else 1
MU = [0]+[mobius(i) for i in range(1, MAX_TERMS+2)]
def op_moebius(a, cap=40):
    a = a[:cap]
    return [sum(MU[n//d]*a[d-1] for d in range(1, n+1) if n % d == 0) for n in range(1, len(a)+1)]
def op_shift(a): return a[1:]
OPS = {'diff': op_diff, 'partsum': op_partsum, 'binomial': op_binomial,
       'moebius': op_moebius, 'shift': op_shift}

def rank_of(qvec, matrix, target_i):
    d = np.linalg.norm(matrix - qvec, axis=1)
    order = np.argsort(d, kind='stable')
    return int(np.where(order == target_i)[0][0]) + 1

# ---------------------------------------------------------------- run DEV
results = {lvl: {'ranks': [], 'by_op': {}} for lvl in
           ('L0_exact', 'L1_sig', 'L2_agnostic', 'B_raw', 'B_shuf', 'B_growthmag')}
exact_hits = 0
for i in DEV:
    p = pairs['positives'][i]
    src, tgt, opname = p['src'], p['tgt'], p['op']
    if src not in pool or tgt not in pool:
        continue
    ti = idx_of[tgt]
    a = pool[src]
    img = OPS[opname](a)[p['offset']:]
    # L0 ceiling: exact prefix match in pool
    hit = any(pool[k][:12] == img[:12] for k in (tgt,)) if len(img) >= 12 else False
    exact_hits += int(hit)
    # L1: signature of the computed image
    q1 = np.nan_to_num(signature(img)); q1 = (q1 - mu) / sd
    r1 = rank_of(q1, SIGZ, ti)
    # L2: signature of the SOURCE, operator unknown
    r2 = rank_of(SIGZ[idx_of[src]], SIGZ, ti)
    rb = rank_of(RAWZ[idx_of[src]], RAWZ, ti)
    rs = rank_of(SHUF[idx_of[src]], SHUF, ti)
    rg = rank_of(GM[idx_of[src]], GM, ti)
    for lvl, r in (('L1_sig', r1), ('L2_agnostic', r2), ('B_raw', rb),
                   ('B_shuf', rs), ('B_growthmag', rg)):
        results[lvl]['ranks'].append(r)
        results[lvl]['by_op'].setdefault(opname, []).append(r)

def summarise(rs):
    if not rs: return {}
    rs = np.array(rs)
    return {'n': int(len(rs)), 'top1': float((rs == 1).mean()), 'top10': float((rs <= 10).mean()),
            'top100': float((rs <= 100).mean()), 'mrr': float((1.0 / rs).mean()),
            'median_rank': float(np.median(rs))}

out = {'pool_size': len(pool), 'dev_pairs_scored': len(results['L1_sig']['ranks']),
       'L0_exact_ceiling_hits': exact_hits,
       'levels': {lvl: summarise(v['ranks']) for lvl, v in results.items() if v['ranks']},
       'per_operator': {lvl: {op: summarise(r) for op, r in v['by_op'].items()}
                        for lvl, v in results.items() if v['by_op']},
       'note': 'DEVELOPMENT ONLY. No D-branch adjudicated. Frozen split untouched.'}
(SEARCH / 'retrieval_dev_results.json').write_text(json.dumps(out, indent=1), encoding='utf-8')

print(f"\nL0 exact-match ceiling (circular by construction): {exact_hits}/{out['dev_pairs_scored']}")
for lvl in ('L1_sig', 'L2_agnostic', 'B_raw', 'B_shuf', 'B_growthmag'):
    s = out['levels'].get(lvl, {})
    if s:
        print(f"{lvl:14s} top1={s['top1']:.3f} top10={s['top10']:.3f} top100={s['top100']:.3f} "
              f"MRR={s['mrr']:.4f} median_rank={s['median_rank']:.0f}")
print("\nper-operator top10:")
for lvl in ('L1_sig', 'L2_agnostic'):
    row = {op: round(summarise(r)['top10'], 2) for op, r in results[lvl]['by_op'].items()}
    print(f"  {lvl}: {row}")
print("-> retrieval_dev_results.json")
