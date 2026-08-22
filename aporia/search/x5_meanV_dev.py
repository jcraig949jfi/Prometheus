"""CAMPAIGN X-5 pass 1 — mean |V| on DEVELOPMENT, needed to state G-pos concretely.

G-pos is defined against the answer-set-adjusted chance 10*mean|V|/N, the same form
X-3 used for its kill threshold. Stating the gate requires the quantity, and the
quantity must come from the population it is applied to — so this computes it on
DEVELOPMENT, and pass 3 will recompute it on frozen-B rather than inherit it.

frozen-B is not touched. No frozen quantity is computed.
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
OPS = xg.OPS
HASH_K, MIN_EXACT, MIN_TERMS, MAX_TERMS = 12, 20, 25, 45

pairs = json.loads((SEARCH / 'x4_pairs.json').read_text(encoding='utf-8'))
split = json.loads((SEARCH / 'x4_split.json').read_text(encoding='utf-8'))
terms = json.loads((SEARCH / 'x4_terms.json').read_text(encoding='utf-8'))
DEV = sorted(split['dev_indices'])

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
N = len(pool)

index = defaultdict(list)
for k_, v in pool.items():
    if len(v) >= HASH_K:
        index[tuple(v[:HASH_K])].append(k_)

def overlap(a, b):
    n, i = min(len(a), len(b)), 0
    while i < n and a[i] == b[i]:
        i += 1
    return i

POS = pairs['positives']
sizes = []
for i in DEV:
    p = POS[i]
    if p['op'] == 'shift' or p['src'] not in pool or p['tgt'] not in pool:
        continue
    try:
        img0 = OPS[p['op']](pool[p['src']])
    except (ValueError, OverflowError):
        continue
    s = set()
    for drop in (0, 1):
        im = img0[drop:]
        if len(im) < HASH_K: continue
        for cid in index.get(tuple(im[:HASH_K]), ()):
            if cid != p['src'] and overlap(im, pool[cid]) >= MIN_EXACT:
                s.add(cid)
    sizes.append(len(s))

mV = float(np.mean(sizes))
adj = 10*mV/N
out = {'population': 'DEVELOPMENT four real operators', 'n_pairs': len(sizes),
       'pool_size': N, 'mean_V': round(mV, 4), 'median_V': float(np.median(sizes)),
       'max_V': int(np.max(sizes)),
       'chance_top10_unadjusted': round(10/N, 6),
       'chance_top10_answer_set_adjusted': round(adj, 6),
       'G_pos_threshold_3x': round(3*adj, 6),
       'note': 'pass 3 recomputes mean |V| on frozen-B; this value is NOT inherited',
       'frozen_quantities_computed': False}
(SEARCH / 'x5_meanV_dev.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print(json.dumps(out, indent=1))
