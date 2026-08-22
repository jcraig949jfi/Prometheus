"""CAMPAIGN X-3 pass 1 — INSTRUMENT ONLY. Build a benchmark large enough to
resolve the decision, chosen by power calculation rather than by convenience.

WHY X-3 EXISTS AND WHY IT IS NOT A THIRD TRY AT THE SAME THING. Campaigns X and
X-2 both terminated without ever measuring the operator-agnostic claim: X because
its instrument failed the necessary condition, X-2 because its gate sat 0.006 from
the measured value against a standard error of 0.0195 and was never resolvable.
The binding constraint is sample size, and this pass fixes exactly that.

THE POWER CALCULATION, DONE BEFORE ANY THRESHOLD IS CHOSEN (new doctrine, P113):

  L1 gate.  Measured true L1 is ~0.944. A gate at 0.95 is unresolvable at ANY
  practical n -- 0.29 SE at n=125, 0.58 at n=500, and still only 1.85 SE at
  n=5000. Adding power does not fix it, which means the VALUE was wrong and not
  merely underpowered. So X-3 does not use a point-estimate gate at all: it uses
  an INTERVAL gate -- the lower bound of the 95% CI on L1 top-1 must exceed 0.90.
  That is resolvable (at n=500, p=0.944 gives LB 0.924) and it tests what the gate
  was always for: that the index reliably finds what it is handed, KNOWN to a
  stated precision rather than asserted at a point.

  L2 decision.  The quantity that matters is L2 minus the raw-term baseline on the
  four real operators. SE_diff = sqrt(2p(1-p)/n) at p~0.05:
      n = 160 real-op pairs -> SE 0.0244 : a 0.05 gap is 2.05 SE
      n = 400 real-op pairs -> SE 0.0154 : a 0.05 gap is 3.24 SE
      n = 800 real-op pairs -> SE 0.0109 : a 0.05 gap is 4.59 SE
  So 400 real-operator pairs in the FROZEN split is the target, which makes a 0.05
  effect a >3 SE decision and lets a null RULE OUT effects of that size -- which is
  what a kill branch actually requires.

TARGET: 150 positives per operator = 750 total. Split 250 development / 500 FROZEN,
with the LARGER half frozen because that is where the decision is made. Frozen
carries 400 real-operator pairs by construction.

Disjoint from BOTH Campaign X's 125 pairs and Campaign X-2's 125 pairs. Every
preregistered constant from the original builder is unchanged; only the seed and
the per-operator target differ, and both are disclosed.

NO RETRIEVAL AND NO SIGNATURE IS RUN IN THIS FILE. Instrument only.
"""
from __future__ import annotations

import gzip
import json
import math
import pathlib
import random
import sys
from collections import defaultdict

ROOT = pathlib.Path(r'F:\Prometheus')
OUT = ROOT / 'aporia' / 'search'
sys.path.insert(0, str(OUT))
from growth_battery import growth_class

MIN_EXACT, MIN_TERMS, HASH_K, MAX_TERMS = 20, 25, 12, 45          # unchanged
MIN_DISTINCT, MAX_PAIRS_PER_SRC, MAX_PAIRS_PER_TGT = 8, 2, 2      # unchanged
TARGET_PER_OP = 150                                               # CHANGED, power-derived
SCAN_CAP = TARGET_PER_OP * 3
rng = random.Random(20260824)                                     # CHANGED, disclosed

def nondeg(v):
    w = v[:MIN_TERMS]
    return len(set(w)) >= MIN_DISTINCT and not all(x == w[-1] for x in w[-6:])

seqs = {}
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
        if len(t) >= MIN_TERMS:
            seqs[p[0].strip()] = t
print(f"corpus: {len(seqs):,}", flush=True)

index = defaultdict(list)
for aid, t in seqs.items():
    index[tuple(t[:HASH_K])].append(aid)

def mobius(n):
    m, p, c = n, 2, 0
    while p * p <= m:
        if m % p == 0:
            m //= p
            if m % p == 0: return 0
            c += 1
        p += 1
    if m > 1: c += 1
    return -1 if c % 2 else 1
MU = [0] + [mobius(i) for i in range(1, MAX_TERMS + 2)]

OPS = {
 'diff':     lambda a: [a[i+1]-a[i] for i in range(len(a)-1)],
 'partsum':  lambda a: [sum(a[:i+1]) for i in range(len(a))],
 'binomial': lambda a: [sum(math.comb(n, k)*a[:24][k] for k in range(n+1)) for n in range(len(a[:24]))],
 'moebius':  lambda a: [sum(MU[n//d]*a[:40][d-1] for d in range(1, n+1) if n % d == 0) for n in range(1, len(a[:40])+1)],
 'shift':    lambda a: a[1:]}

# ---- exclude every pair used by Campaign X and Campaign X-2 (builder-side only)
EXCL = set()
for pairs_f, map_f in (('benchmark_pairs.json', 'NOT_FOR_RETRIEVAL_blindmap.json'),
                       ('x2_frozen_pairs.json', 'NOT_FOR_RETRIEVAL_x2_blindmap.json')):
    bm = json.loads((OUT / map_f).read_text(encoding='utf-8'))
    bp = json.loads((OUT / pairs_f).read_text(encoding='utf-8'))
    for p in bp['positives']:
        EXCL.add((bm[p['src']], bm[p['tgt']], p['op']))
print(f"pairs excluded (X + X-2): {len(EXCL)}", flush=True)

def overlap(a, b):
    n, i = min(len(a), len(b)), 0
    while i < n and a[i] == b[i]:
        i += 1
    return i

pool_src = [a for a in seqs if nondeg(seqs[a])]
rng.shuffle(pool_src)
print(f"non-degenerate sources: {len(pool_src):,}", flush=True)

found = {}
for opname, fn in OPS.items():
    hits, per_s, per_t, seen = [], defaultdict(int), defaultdict(int), set()
    for aid in pool_src:
        if len(hits) >= SCAN_CAP:
            break
        try:
            img = fn(seqs[aid])
        except (ValueError, OverflowError):
            continue
        if len(img) < MIN_EXACT or not nondeg(img):
            continue
        for drop in (0, 1):
            im = img[drop:]
            if len(im) < HASH_K:
                continue
            for bid in index.get(tuple(im[:HASH_K]), ()):
                if bid == aid or not nondeg(seqs[bid]) or (aid, bid, opname) in EXCL:
                    continue
                if per_s[aid] >= MAX_PAIRS_PER_SRC or per_t[bid] >= MAX_PAIRS_PER_TGT:
                    continue
                ov = overlap(im, seqs[bid])
                if ov >= MIN_EXACT and (aid, bid) not in seen:
                    seen.add((aid, bid)); per_s[aid] += 1; per_t[bid] += 1
                    hits.append({'src': aid, 'tgt': bid, 'offset': drop, 'exact_terms': ov})
    found[opname] = hits
    print(f"{opname}: {len(hits)} verified pairs (cap {SCAN_CAP})", flush=True)

short = {op: len(v) for op, v in found.items() if len(v) < TARGET_PER_OP}
if short:
    print(f"UNDERPOWERED: {short} — fewer than {TARGET_PER_OP} available", flush=True)

blind, gcache = {}, {}
def bid_(a):
    if a not in blind: blind[a] = f"X{len(blind):06d}"
    return blind[a]
def gcl(a):
    if a not in gcache: gcache[a] = growth_class(seqs[a])[0]
    return gcache[a]

bench = {'positives': [], 'negatives': [], 'meta': {}}
all_ids = list(seqs)
for opname, hits in found.items():
    rng.shuffle(hits)
    for p in hits[:TARGET_PER_OP]:
        s, t = p['src'], p['tgt']
        bench['positives'].append({'op': opname, 'src': bid_(s), 'tgt': bid_(t),
                                   'exact_terms': p['exact_terms'], 'offset': p['offset'],
                                   'tgt_growth': gcl(t)})
        wg, wl = gcl(t), len(seqs[t])
        wm = int(math.log10(max(abs(seqs[t][-1]), 1)) + 1)
        for _ in range(400):
            c = rng.choice(all_ids)
            if c in (t, s): continue
            if abs(int(math.log10(max(abs(seqs[c][-1]), 1)) + 1) - wm) > 1: continue
            if abs(len(seqs[c]) - wl) > 8: continue
            if gcl(c) != wg: continue
            bench['negatives'].append({'op': opname, 'src': bid_(s), 'decoy': bid_(c), 'growth': wg})
            break

# split: the LARGER half is FROZEN, because that is where the decision is made
by_op = defaultdict(list)
for i, p in enumerate(bench['positives']):
    by_op[p['op']].append(i)
dev_idx, fro_idx = [], []
for op, idxs in by_op.items():
    rng.shuffle(idxs)
    cut = int(round(len(idxs) / 3))          # 1/3 development, 2/3 FROZEN
    dev_idx += idxs[:cut]; fro_idx += idxs[cut:]

nt_frozen = sum(1 for i in fro_idx if bench['positives'][i]['op'] != 'shift')
bench['meta'] = {'seed': 20260824, 'target_per_op': TARGET_PER_OP, 'scan_cap': SCAN_CAP,
                 'pairs_found': {k: len(v) for k, v in found.items()},
                 'positives': len(bench['positives']), 'negatives': len(bench['negatives']),
                 'dev_count': len(dev_idx), 'frozen_count': len(fro_idx),
                 'frozen_four_real_operator_pairs': nt_frozen,
                 'underpowered_ops': short,
                 'disjoint_from': ['campaign_X', 'campaign_X2'],
                 'power_note': 'frozen four-real-op n drives SE_diff = sqrt(2*0.05*0.95/n)'}

(OUT / 'x3_pairs.json').write_text(json.dumps(bench, indent=1), encoding='utf-8')
(OUT / 'x3_split.json').write_text(json.dumps(
    {'dev_indices': sorted(dev_idx), 'frozen_indices': sorted(fro_idx),
     'note': 'FROZEN BEFORE ANY SIGNATURE OR THRESHOLD TOUCHES IT'}, indent=1), encoding='utf-8')
(OUT / 'x3_terms.json').write_text(json.dumps(
    {b: seqs[a] for a, b in blind.items()}, indent=1), encoding='utf-8')
(OUT / 'NOT_FOR_RETRIEVAL_x3_blindmap.json').write_text(json.dumps(
    {v: k for k, v in blind.items()}, indent=1), encoding='utf-8')

se = math.sqrt(2 * 0.05 * 0.95 / max(nt_frozen, 1))
print(json.dumps(bench['meta'], indent=1), flush=True)
print(f"\nfrozen four-real-op pairs = {nt_frozen} -> SE_diff = {se:.4f}; "
      f"a 0.05 effect is {0.05/se:.2f} SE, a 0.03 effect is {0.03/se:.2f} SE", flush=True)
