"""CAMPAIGN X-2 pass 1 — build a NEW frozen split, disjoint from the burned one.

PRECONDITION HANDLED FIRST. Campaign X's frozen split has been read. Testing a
redesigned representation against those same 50 pairs is adaptive and would void
the experiment, so they cannot be reused. This script rescans with the SAME
preregistered thresholds and constants as build_blinded_benchmark.py, collects
every verified pair, EXCLUDES every pair used in Campaign X, and draws a new
frozen split from the remainder. Campaign X's 125 pairs are demoted to
development.

ON READING THE BLIND MAP: this is a BUILDER, not a retrieval path. The blinding
rule is that RETRIEVAL code may never see A-numbers; the builder necessarily
works in A-numbers because it is the thing that assigns blind ids. Establishing
disjointness from Campaign X's pairs requires knowing which A-numbers those were,
so the old blind map is read HERE and nowhere downstream. No retrieval script in
this campaign reads it, and the new map is written to its own not-for-retrieval
file exactly as before.

UNCHANGED, so the new split is comparable to the old: MIN_EXACT=20, MIN_TERMS=25,
HASH_K=12, MAX_TERMS=45, the five operators, the degeneracy filters, and the
per-source/per-target caps. CHANGED and disclosed: the RNG seed, because drawing
a new sample with the old seed would reproduce the old selection.
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

MIN_EXACT, TARGET_PER_OP, MIN_TERMS = 20, 25, 25      # preregistered, unchanged
HASH_K, MAX_TERMS = 12, 45                            # unchanged
MIN_DISTINCT, MAX_PAIRS_PER_SRC, MAX_PAIRS_PER_TGT = 8, 2, 2   # unchanged
rng = random.Random(20260823)                         # CHANGED — disclosed above

def nondegenerate(v):
    w = v[:MIN_TERMS]
    return len(set(w)) >= MIN_DISTINCT and not all(x == w[-1] for x in w[-6:])

seqs = {}
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
        if len(t) >= MIN_TERMS:
            seqs[parts[0].strip()] = t
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

def op_diff(a): return [a[i+1]-a[i] for i in range(len(a)-1)]
def op_partsum(a):
    o, s = [], 0
    for x in a: s += x; o.append(s)
    return o
def op_binomial(a, cap=24):
    a = a[:cap]
    return [sum(math.comb(n, k)*a[k] for k in range(n+1)) for n in range(len(a))]
def op_moebius(a, cap=40):
    a = a[:cap]
    return [sum(MU[n//d]*a[d-1] for d in range(1, n+1) if n % d == 0) for n in range(1, len(a)+1)]
def op_shift(a): return a[1:]
OPS = {'diff': op_diff, 'partsum': op_partsum, 'binomial': op_binomial,
       'moebius': op_moebius, 'shift': op_shift}

# --- Campaign X's pairs, recovered in A-numbers, to be EXCLUDED --------------
old_map = json.loads((OUT / 'NOT_FOR_RETRIEVAL_blindmap.json').read_text(encoding='utf-8'))
old_bench = json.loads((OUT / 'benchmark_pairs.json').read_text(encoding='utf-8'))
OLD_PAIRS = {(old_map[p['src']], old_map[p['tgt']], p['op']) for p in old_bench['positives']}
print(f"Campaign X pairs to exclude: {len(OLD_PAIRS)}", flush=True)

def overlap(img, tgt):
    n, i = min(len(img), len(tgt)), 0
    while i < n and img[i] == tgt[i]:
        i += 1
    return i

pool_src = [a for a in seqs if nondegenerate(seqs[a])]
rng.shuffle(pool_src)
print(f"non-degenerate sources: {len(pool_src):,}", flush=True)

found = {}
for opname, fn in OPS.items():
    hits, per_s, per_t, seen = [], defaultdict(int), defaultdict(int), set()
    for aid in pool_src:
        if len(hits) >= TARGET_PER_OP * 6:
            break
        try:
            img = fn(seqs[aid])
        except (ValueError, OverflowError):
            continue
        if len(img) < MIN_EXACT or not nondegenerate(img):
            continue
        for drop in (0, 1):
            im = img[drop:]
            if len(im) < HASH_K:
                continue
            for bid in index.get(tuple(im[:HASH_K]), ()):
                if bid == aid or not nondegenerate(seqs[bid]):
                    continue
                if (aid, bid, opname) in OLD_PAIRS:       # <-- disjointness
                    continue
                if per_s[aid] >= MAX_PAIRS_PER_SRC or per_t[bid] >= MAX_PAIRS_PER_TGT:
                    continue
                ov = overlap(im, seqs[bid])
                if ov >= MIN_EXACT and (aid, bid) not in seen:
                    seen.add((aid, bid)); per_s[aid] += 1; per_t[bid] += 1
                    hits.append({'src': aid, 'tgt': bid, 'offset': drop, 'exact_terms': ov})
    found[opname] = hits
    print(f"{opname}: {len(hits)} NEW verified pairs (disjoint from Campaign X)", flush=True)

short = [op for op, v in found.items() if len(v) < TARGET_PER_OP]
if short:
    print(f"WARNING underpowered on {short}", flush=True)

blind, gcache = {}, {}
def bid_(a):
    if a not in blind:
        blind[a] = f"T{len(blind):06d}"
    return blind[a]
def gcl(a):
    if a not in gcache:
        gcache[a] = growth_class(seqs[a])[0]
    return gcache[a]

new = {'positives': [], 'negatives': [], 'meta': {}}
all_ids = list(seqs)
for opname, hits in found.items():
    rng.shuffle(hits)
    for p in hits[:TARGET_PER_OP]:
        s, t = p['src'], p['tgt']
        new['positives'].append({'op': opname, 'src': bid_(s), 'tgt': bid_(t),
                                 'exact_terms': p['exact_terms'], 'offset': p['offset'],
                                 'tgt_growth': gcl(t)})
        want_g, want_len = gcl(t), len(seqs[t])
        want_mag = int(math.log10(max(abs(seqs[t][-1]), 1)) + 1)
        for _ in range(400):
            c = rng.choice(all_ids)
            if c in (t, s):
                continue
            if abs(int(math.log10(max(abs(seqs[c][-1]), 1)) + 1) - want_mag) > 1: continue
            if abs(len(seqs[c]) - want_len) > 8: continue
            if gcl(c) != want_g: continue
            new['negatives'].append({'op': opname, 'src': bid_(s), 'decoy': bid_(c), 'growth': want_g})
            break

new['meta'] = {'seed': 20260823, 'disjoint_from_campaign_x': True,
               'pairs_found': {k: len(v) for k, v in found.items()},
               'positives': len(new['positives']), 'negatives': len(new['negatives']),
               'underpowered_ops': short,
               'role': 'THIS IS THE NEW FROZEN SET — not to be touched until Campaign X-2 pass 3',
               'campaign_x_pairs_demoted_to': 'development'}

(OUT / 'x2_frozen_pairs.json').write_text(json.dumps(new, indent=1), encoding='utf-8')
(OUT / 'x2_frozen_terms.json').write_text(json.dumps(
    {b: seqs[a] for a, b in blind.items()}, indent=1), encoding='utf-8')
(OUT / 'NOT_FOR_RETRIEVAL_x2_blindmap.json').write_text(json.dumps(
    {v: k for k, v in blind.items()}, indent=1), encoding='utf-8')
print(json.dumps(new['meta'], indent=1), flush=True)
