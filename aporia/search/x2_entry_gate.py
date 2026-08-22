"""CAMPAIGN X-2 pass 1 — instrument rebuild and ENTRY GATE.

Runs on Campaign X's 125 pairs, now DEMOTED TO DEVELOPMENT. The new frozen set
(x2_frozen_pairs.json) is NOT opened by this script at all.

DEFICIT 1 — the query's own source is a pool member. Campaign X's diagnosis:
10 of 16 L1 misses had the source outranking the target and 7 had the source at
rank 1, concentrated entirely in the near-identity `shift` operator. This is a
benchmark bug, not a representational finding. FIX: the query's source index is
removed from the candidate ranking. Verified below by re-measuring V1 unchanged
with and without the exclusion — the delta isolates the bug's contribution.

DEFICIT 2 — resolution. 8 of 50 frozen queries had an UNRELATED DISTRACTOR beat a
sequence they were exactly equal to over >= 20 terms. Reading what those 33
features actually are: quantiles, entropies, histograms and moments — every one
an AGGREGATE. Aggregates are near-permutation-invariant; they record which
behaviours occur, not in what order. Only sign-alternation rate and the difference
moments retain any ordering at all. So the named deficit is ORDER-BLINDNESS, and
the fix must add features that are order-sensitive while staying scale-free.

V2 adds, each aimed at that evidence and nothing else:
  detrended log-magnitude profile   growth SHAPE after removing the linear trend,
                                    sampled at 12 fixed relative positions
  residue vectors mod 2 and mod 3   per-term arithmetic fingerprint in ORDER,
                                    not collapsed to a density and an entropy
  normalised rank profile           the order permutation itself, magnitude-free
  sign sequence, first 16 terms     ordering of sign, not just its rate
  local-extremum profile            where the sequence turns, magnitude-free

SEPARATING 'WRONG FEATURES' FROM 'WRONG METRIC' — Campaign X could not do this and
said so. A 2x2 does: {V1, V2} x {z-scored Euclidean, ZCA-whitened}. Euclidean on
z-scored features weights all dimensions equally even when blocks are internally
redundant (V1's 9 leading-digit bins sum to 1, so they carry 8 degrees of freedom
while consuming 9; the 4 growth one-hots carry 3 while consuming 4). Whitening
decorrelates, so if the metric is the problem the whitened column improves and if
the features are the problem the V2 row improves. Both improving means both.

ENTRY GATE, preregistered here and enforced in-script: L1 top-1 >= 0.95 on
development. A representation that cannot identify a sequence it has been handed
may not be tested on the sufficient condition. NO L2 MEASUREMENT IS TAKEN IN THIS
SCRIPT AT ALL — not gated, not computed — so there is nothing to tune toward.
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

MIN_TERMS, MAX_TERMS, N_DISTRACT = 25, 45, 20000
GATE = 0.95
rng = random.Random(20260823)

pairs = json.loads((SEARCH / 'benchmark_pairs.json').read_text(encoding='utf-8'))
terms = json.loads((SEARCH / 'benchmark_terms.json').read_text(encoding='utf-8'))
DEV = list(range(len(pairs['positives'])))          # ALL of Campaign X = development now
print(f"development pairs (Campaign X, demoted): {len(DEV)}", flush=True)

def nondeg(v):
    w = v[:MIN_TERMS]
    return len(set(w)) >= 8 and not all(x == w[-1] for x in w[-6:])

pool = dict(terms)
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
for i, t in enumerate(cands[:N_DISTRACT]):
    pool[f"D{i:06d}"] = t
ids = list(pool)
idx_of = {k: i for i, k in enumerate(ids)}
print(f"pool: {len(pool):,}", flush=True)

# ------------------------------------------------------------------ V1 (unchanged)
def sig_v1(v):
    a = [int(x) for x in v[:MAX_TERMS]]; n = len(a); f = []
    gc, dg = growth_class(a)
    f += [1.0 if gc == c else 0.0 for c in ('POLY', 'EXP', 'SUPEREXP', 'ABSTAIN')]
    f += [float(dg.get('poly_slope', 0.0)), float(dg.get('exp_slope', 0.0))]
    lr = [math.log(abs(a[i+1])/abs(a[i])) for i in range(n-1) if a[i] and a[i+1]] or [0.0]
    f += [float(np.quantile(lr, q)) for q in (0.1, 0.25, 0.5, 0.75, 0.9)]
    sg = [1 if x > 0 else (-1 if x < 0 else 0) for x in a]
    f.append(sum(1 for s in sg if s > 0)/n)
    f.append(sum(1 for i in range(n-1) if sg[i]*sg[i+1] < 0)/max(n-1, 1))
    for p in (2, 3, 5, 7):
        r = [x % p for x in a]
        c = np.array([r.count(k) for k in range(p)], dtype=float)/n
        f.append(float(c[0])); nz = c[c > 0]
        f.append(float(-(nz*np.log(nz)).sum()) if len(nz) else 0.0)
    d = np.clip(np.array([(a[i+1]-a[i])/(abs(a[i]) or 1) for i in range(n-1)] or [0.0], dtype=float), -1e6, 1e6)
    f += [float(d.mean()), float(d.std()), float(np.median(d))]
    ld = [int(str(abs(x))[0]) for x in a if x != 0] or [1]
    f += [float(ld.count(k))/len(ld) for k in range(1, 10)]
    return np.array(f, dtype=float)

# ------------------------------------------------------------------ V2 = V1 + order-sensitive
def sig_v2(v):
    a = [int(x) for x in v[:MAX_TERMS]]; n = len(a)
    f = list(sig_v1(v))
    # detrended log-magnitude profile at 12 fixed relative positions (scale-free SHAPE)
    lm = np.array([math.log1p(abs(float(x))) for x in a], dtype=float)
    t = np.arange(n, dtype=float)
    if n >= 3:
        sl, ic = np.polyfit(t, lm, 1)
        r = lm - (sl*t + ic)
        s = r.std() or 1.0
        r = r/s
    else:
        r = np.zeros(n)
    pos = np.linspace(0, n-1, 12)
    f += [float(np.interp(p, t, r)) for p in pos]
    # per-term residues mod 2 and mod 3, IN ORDER (first 16 terms)
    w = (a + [0]*16)[:16]
    f += [float(x % 2) for x in w]
    f += [float(x % 3)/2.0 for x in w]
    # normalised rank profile of the first 16 terms — the order permutation itself
    ww = np.array(w, dtype=float)
    order = np.argsort(np.argsort(ww))
    f += [float(o)/15.0 for o in order]
    # sign sequence, first 16
    f += [1.0 if x > 0 else (0.0 if x == 0 else -1.0) for x in w]
    # local-extremum profile (where it turns), magnitude-free
    f += [1.0 if (0 < i < 15 and ((w[i] > w[i-1] and w[i] > w[i+1]) or
                                  (w[i] < w[i-1] and w[i] < w[i+1]))) else 0.0
          for i in range(16)]
    return np.array(f, dtype=float)

def build(fn, label):
    M = np.vstack([fn(pool[i]) for i in ids])
    M = np.nan_to_num(M, nan=0.0, posinf=0.0, neginf=0.0)
    mu, sd = M.mean(0), M.std(0); sd[sd == 0] = 1.0
    Z = (M - mu)/sd
    print(f"{label}: dim {M.shape[1]}", flush=True)
    return Z, mu, sd

def whiten(Z):
    """ZCA: decorrelate so internally redundant blocks stop double-counting."""
    C = np.cov(Z, rowvar=False) + 1e-6*np.eye(Z.shape[1])
    w, V = np.linalg.eigh(C)
    W = V @ np.diag(1.0/np.sqrt(np.maximum(w, 1e-12))) @ V.T
    return Z @ W, W

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
OPS = {'diff': lambda a: [a[i+1]-a[i] for i in range(len(a)-1)],
       'partsum': lambda a: [sum(a[:i+1]) for i in range(len(a))],
       'binomial': lambda a: [sum(math.comb(n, k)*a[:24][k] for k in range(n+1)) for n in range(len(a[:24]))],
       'moebius': lambda a: [sum(MU[n//d]*a[:40][d-1] for d in range(1, n+1) if n % d == 0) for n in range(1, len(a[:40])+1)],
       'shift': lambda a: a[1:]}

Z1, mu1, sd1 = build(sig_v1, 'V1')
Z2, mu2, sd2 = build(sig_v2, 'V2')
W1c, W1 = whiten(Z1)
W2c, W2 = whiten(Z2)

def l1_top1(Z, mu, sd, fn, Wm=None, exclude_source=True):
    """L1: signature the computed image, retrieve the target. Returns (top1, by_op, misses)."""
    hits, by_op, misses = 0, {}, []
    for i in DEV:
        p = pairs['positives'][i]
        src, tgt, op = p['src'], p['tgt'], p['op']
        if src not in pool or tgt not in pool:
            continue
        img = OPS[op](pool[src])[p['offset']:]
        q = np.nan_to_num(fn(img)); q = (q - mu)/sd
        if Wm is not None:
            q = q @ Wm
        dist = np.linalg.norm(Z - q, axis=1)
        if exclude_source:
            dist[idx_of[src]] = np.inf
        r = int(np.where(np.argsort(dist, kind='stable') == idx_of[tgt])[0][0]) + 1
        by_op.setdefault(op, []).append(r)
        if r == 1:
            hits += 1
        else:
            misses.append({'op': op, 'rank': r})
    n = sum(len(v) for v in by_op.values())
    return hits/n, n, {k: (sum(1 for r in v if r == 1), len(v)) for k, v in by_op.items()}, misses

res = {'development_pairs': len(DEV), 'pool_size': len(pool), 'gate': GATE,
       'v1_dim': int(Z1.shape[1]), 'v2_dim': int(Z2.shape[1])}

# deficit-1 verification: V1 unchanged, with and without source exclusion
a_incl, n_, _, _ = l1_top1(Z1, mu1, sd1, sig_v1, None, exclude_source=False)
a_excl, _, byop_excl, _ = l1_top1(Z1, mu1, sd1, sig_v1, None, exclude_source=True)
res['deficit1_source_exclusion'] = {
    'V1_L1_top1_source_in_pool': round(a_incl, 4),
    'V1_L1_top1_source_excluded': round(a_excl, 4),
    'delta': round(a_excl - a_incl, 4), 'n': n_,
    'meaning': 'the delta is the benchmark bug\'s contribution, isolated with the representation held fixed'}
print(f"\nDEFICIT 1 — source exclusion (V1 held fixed): {a_incl:.4f} -> {a_excl:.4f}  (delta {a_excl-a_incl:+.4f})")

# the 2x2
cells = {}
for fname, (Z, mu, sd, fn, Wm) in {
        'V1_euclid':   (Z1, mu1, sd1, sig_v1, None),
        'V1_whitened': (W1c, mu1, sd1, sig_v1, W1),
        'V2_euclid':   (Z2, mu2, sd2, sig_v2, None),
        'V2_whitened': (W2c, mu2, sd2, sig_v2, W2)}.items():
    t1, n, byop, misses = l1_top1(Z, mu, sd, fn, Wm, exclude_source=True)
    cells[fname] = {'L1_top1': round(t1, 4), 'top1_count': int(round(t1*n)), 'n': n,
                    'by_op': {k: f"{a}/{b}" for k, (a, b) in byop.items()},
                    'misses_by_op': {}}
    for m in misses:
        cells[fname]['misses_by_op'][m['op']] = cells[fname]['misses_by_op'].get(m['op'], 0) + 1
    print(f"{fname:12s} L1 top-1 = {int(round(t1*n))}/{n} = {t1:.4f}   by_op {cells[fname]['by_op']}")
res['grid_2x2'] = cells

feat_gain = cells['V2_euclid']['L1_top1'] - cells['V1_euclid']['L1_top1']
metr_gain = cells['V1_whitened']['L1_top1'] - cells['V1_euclid']['L1_top1']
res['attribution'] = {'feature_gain_V1_to_V2_euclid': round(feat_gain, 4),
                      'metric_gain_euclid_to_whitened_V1': round(metr_gain, 4),
                      'combined': round(cells['V2_whitened']['L1_top1'] - cells['V1_euclid']['L1_top1'], 4)}

best = max(cells, key=lambda k: cells[k]['L1_top1'])
res['best_cell'] = best
res['best_L1_top1'] = cells[best]['L1_top1']
res['GATE_PASSED'] = bool(cells[best]['L1_top1'] >= GATE)
res['L2_measured'] = False
res['note'] = ('No L2 measurement is computed anywhere in this script, gate passed or not, '
               'so nothing could have been tuned toward it.')

(SEARCH / 'x2_entry_gate_results.json').write_text(json.dumps(res, indent=1), encoding='utf-8')
print(f"\nattribution: features {feat_gain:+.4f} | metric {metr_gain:+.4f} | combined {res['attribution']['combined']:+.4f}")
print(f"best cell: {best} at {cells[best]['L1_top1']:.4f}")
print(f"\n*** ENTRY GATE ({GATE}): {'PASSED' if res['GATE_PASSED'] else 'FAILED'} — L2 NOT measured ***")
