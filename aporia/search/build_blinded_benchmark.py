"""CAMPAIGN X pass 1 — build the blinded relation-recovery benchmark.

This pass BUILDS ONLY. No retrieval is run and no signature is designed here;
that separation is the point, because the frozen split must exist before any
representation choice can see it.

THE EXPERIMENT (why it exists): the loop has a competent adjudicator and an
untested search policy. Before pointing anything at the 68,770 unreferenced
"Sleeping Beauty" sequences, we test whether behavioral signatures can recover
relationships that are ALREADY KNOWN and have been deliberately hidden from the
retrieval path. If it cannot rediscover concealed known structure, there is no
basis for believing it will find unknown structure.

PREREGISTERED OPERATORS (five, exact and machine-verifiable from terms alone):
  diff     B_n = A_{n+1} - A_n
  partsum  B_n = sum_{k<=n} A_k
  binomial B_n = sum_k C(n,k) A_k
  moebius  B_n = sum_{d|n} mu(n/d) A_d     (1-indexed)
  shift    B_n = A_{n+1}                    (DELIBERATELY TRIVIAL control)

PREREGISTERED THRESHOLDS (committed before the scan runs):
  - a pair counts only if the operator holds EXACTLY on >= 20 overlapping terms
  - target 25 positive pairs per operator
  - source pool restricted to sequences with >= 25 terms
  - split 60% development / 40% FROZEN, written to disk in this pass

PREREGISTERED PASS-2 BRANCHES (retrieval is judged against these, not against
whatever looks interesting later):
  D1  signature retrieval materially beats BOTH the raw-term baseline and the
      shuffled-signature baseline on FROZEN positives
      -> the behavioral representation has demonstrated retrieval value
  D2  raw terms do equally well -> the signature adds nothing demonstrable
  D3  development works, frozen fails -> overfitting
  D4  only shift/subsequence retrieves -> the map detects superficial
      equivalence, not structural relation
  D5  nothing retrieves -> KILL the Sleeping Beauties search outright

INSTANT-KILL / REDESIGN CHECK (this pass): if fewer than 10 positive pairs are
found for 3 or more operators, the benchmark is underpowered — say so and
REDESIGN rather than proceeding.

BLINDING DESIGN: the retrieval path will receive term vectors keyed by an
opaque blind_id only. A-numbers and names live in a separate mapping file
marked not-for-retrieval. names.gz is never opened by this script.
"""
from __future__ import annotations

import gzip
import json
import math
import pathlib
import random
from collections import defaultdict

ROOT = pathlib.Path(r'F:\Prometheus')
OUTDIR = ROOT / 'aporia' / 'search'
import sys
sys.path.insert(0, str(OUTDIR))
from growth_battery import growth_class

MIN_EXACT = 20          # preregistered
TARGET_PER_OP = 25      # preregistered
MIN_TERMS = 25          # preregistered
HASH_K = 12             # index key length
MAX_TERMS = 45
rng = random.Random(20260822)

# --- DEGENERACY FILTERS (added in-pass after the first build; see below) -----
# BUILD-1 FAILED TOTALLY and was caught before any retrieval ran: all 125
# positives were ONE source sequence (the all-zeros sequence) mapping to
# all-zero targets, and the five operators returned near-identical pair counts
# (323/323/322/321/323) because a degenerate object satisfies EVERY operator
# simultaneously and therefore saturates every quota first. New class for the
# catch ledger: DEGENERACY-SATURATED-BENCHMARK.
# Filters, preregistered here before the rebuild:
MIN_DISTINCT = 8        # a sequence must take >= 8 distinct values in its window
MAX_PAIRS_PER_SRC = 2   # no single source may dominate an operator's quota
MAX_PAIRS_PER_TGT = 2


def nondegenerate(v):
    w = v[:MIN_TERMS]
    if len(set(w)) < MIN_DISTINCT:
        return False
    if all(x == w[-1] for x in w[-6:]):        # eventually constant in-window
        return False
    return True

# ---------------------------------------------------------------- corpus
seqs = {}
with gzip.open(ROOT / 'prometheus_data/oeis/stripped.gz', 'rt', encoding='utf-8', errors='replace') as fh:
    for line in fh:
        if line.startswith('#'):
            continue
        parts = line.strip().rstrip(',').split(',')
        if len(parts) < MIN_TERMS + 1:
            continue
        aid = parts[0].strip()
        try:
            terms = [int(t) for t in parts[1:MAX_TERMS + 1]]
        except ValueError:
            continue
        if len(terms) >= MIN_TERMS:
            seqs[aid] = terms
print(f"corpus: {len(seqs):,} sequences with >= {MIN_TERMS} terms", flush=True)

index = defaultdict(list)
for aid, t in seqs.items():
    index[tuple(t[:HASH_K])].append(aid)

# ---------------------------------------------------------------- operators
def mobius(n):
    m, p, cnt = n, 2, 0
    while p * p <= m:
        if m % p == 0:
            m //= p
            if m % p == 0:
                return 0
            cnt += 1
        p += 1
    if m > 1:
        cnt += 1
    return -1 if cnt % 2 else 1

MU = [0] + [mobius(i) for i in range(1, MAX_TERMS + 2)]

def op_diff(a):
    return [a[i + 1] - a[i] for i in range(len(a) - 1)]

def op_partsum(a):
    out, s = [], 0
    for x in a:
        s += x
        out.append(s)
    return out

def op_binomial(a, cap=24):
    a = a[:cap]
    out = []
    for n in range(len(a)):
        s = 0
        for k in range(n + 1):
            s += math.comb(n, k) * a[k]
        out.append(s)
    return out

def op_moebius(a, cap=40):
    a = a[:cap]
    out = []
    for n in range(1, len(a) + 1):
        s = 0
        for d in range(1, n + 1):
            if n % d == 0:
                s += MU[n // d] * a[d - 1]
        out.append(s)
    return out

def op_shift(a):
    return a[1:]

OPS = {'diff': op_diff, 'partsum': op_partsum, 'binomial': op_binomial,
       'moebius': op_moebius, 'shift': op_shift}

# ------------------------------------------------- scan for real pairs
def exact_overlap(img, tgt):
    """longest common exact prefix length between operator image and target"""
    n = min(len(img), len(tgt))
    i = 0
    while i < n and img[i] == tgt[i]:
        i += 1
    return i

source_pool = [a for a in seqs if nondegenerate(seqs[a])]
rng.shuffle(source_pool)                        # no dict-order dominance
print(f"non-degenerate source pool: {len(source_pool):,} of {len(seqs):,}", flush=True)

found = {op: [] for op in OPS}
for oi, (opname, fn) in enumerate(OPS.items()):
    seen_pairs = set()
    per_src = defaultdict(int)
    per_tgt = defaultdict(int)
    for aid in source_pool:
        if len(found[opname]) >= TARGET_PER_OP * 4:
            break
        terms = seqs[aid]
        try:
            img = fn(terms)
        except (ValueError, OverflowError):
            continue
        if len(img) < MIN_EXACT or not nondegenerate(img):
            continue
        for drop in (0, 1):                      # tolerate one offset convention
            im = img[drop:]
            if len(im) < HASH_K:
                continue
            for bid in index.get(tuple(im[:HASH_K]), ()):
                if bid == aid or not nondegenerate(seqs[bid]):
                    continue
                if per_src[aid] >= MAX_PAIRS_PER_SRC or per_tgt[bid] >= MAX_PAIRS_PER_TGT:
                    continue
                ov = exact_overlap(im, seqs[bid])
                if ov >= MIN_EXACT and (aid, bid) not in seen_pairs:
                    seen_pairs.add((aid, bid))
                    per_src[aid] += 1
                    per_tgt[bid] += 1
                    found[opname].append({'src': aid, 'tgt': bid, 'offset': drop,
                                          'exact_terms': ov})
    print(f"{opname}: {len(found[opname])} verified pairs "
          f"(>= {MIN_EXACT} exact terms)", flush=True)

underpowered = [op for op, v in found.items() if len(v) < 10]
if len(underpowered) >= 3:
    print(f"REDESIGN: underpowered on {underpowered} — fewer than 10 pairs on 3+ operators", flush=True)

# ------------------------------------------------- build the benchmark
bench = {'positives': [], 'negatives': [], 'meta': {}}
blind = {}
def blind_id(aid):
    if aid not in blind:
        blind[aid] = f"S{len(blind):06d}"
    return blind[aid]

growth_cache = {}
def gclass(aid):
    if aid not in growth_cache:
        growth_cache[aid] = growth_class(seqs[aid])[0]
    return growth_cache[aid]

all_ids = list(seqs)
for opname, pairs in found.items():
    rng.shuffle(pairs)
    chosen = pairs[:TARGET_PER_OP]
    for p in chosen:
        s, t = p['src'], p['tgt']
        bench['positives'].append({
            'op': opname, 'src': blind_id(s), 'tgt': blind_id(t),
            'exact_terms': p['exact_terms'], 'offset': p['offset'],
            'tgt_growth': gclass(t), 'tgt_len': len(seqs[t]),
            'tgt_mag': int(math.log10(max(abs(seqs[t][-1]), 1)) + 1)})
    # matched negatives: same growth class, similar length and magnitude, NOT the true target
    for p in chosen:
        t = p['tgt']
        want_g, want_len = gclass(t), len(seqs[t])
        want_mag = int(math.log10(max(abs(seqs[t][-1]), 1)) + 1)
        tries = 0
        while tries < 400:
            tries += 1
            cand = rng.choice(all_ids)
            if cand == t or cand == p['src']:
                continue
            cm = int(math.log10(max(abs(seqs[cand][-1]), 1)) + 1)
            if abs(cm - want_mag) > 1 or abs(len(seqs[cand]) - want_len) > 8:
                continue
            if gclass(cand) != want_g:
                continue
            bench['negatives'].append({'op': opname, 'src': blind_id(p['src']),
                                       'decoy': blind_id(cand), 'growth': want_g})
            break

# ------------------------------------------------- freeze the split FIRST
by_op = defaultdict(list)
for i, p in enumerate(bench['positives']):
    by_op[p['op']].append(i)
frozen_idx, dev_idx = [], []
for op, idxs in by_op.items():
    rng.shuffle(idxs)
    cut = int(0.6 * len(idxs))
    dev_idx += idxs[:cut]
    frozen_idx += idxs[cut:]

bench['meta'] = {
    'corpus_size': len(seqs), 'min_exact_terms': MIN_EXACT,
    'target_per_op': TARGET_PER_OP, 'min_terms': MIN_TERMS,
    'pairs_found': {k: len(v) for k, v in found.items()},
    'positives': len(bench['positives']), 'negatives': len(bench['negatives']),
    'dev_count': len(dev_idx), 'frozen_count': len(frozen_idx),
    'underpowered_ops': underpowered,
    'verdict': 'REDESIGN' if len(underpowered) >= 3 else 'BENCHMARK-BUILT',
    'seed': 20260822}

(OUTDIR / 'benchmark_pairs.json').write_text(json.dumps(bench, indent=1), encoding='utf-8')
(OUTDIR / 'benchmark_frozen_split.json').write_text(json.dumps(
    {'frozen_indices': sorted(frozen_idx), 'dev_indices': sorted(dev_idx),
     'note': 'FROZEN BEFORE ANY SIGNATURE DESIGN — reshaping this file invalidates the experiment'},
    indent=1), encoding='utf-8')
# blinding map is deliberately separate and must never be read by retrieval code
(OUTDIR / 'NOT_FOR_RETRIEVAL_blindmap.json').write_text(json.dumps(
    {v: k for k, v in blind.items()}, indent=1), encoding='utf-8')
# term vectors keyed ONLY by blind id — this is what retrieval may read
(OUTDIR / 'benchmark_terms.json').write_text(json.dumps(
    {b: seqs[a] for a, b in blind.items()}, indent=1), encoding='utf-8')

print(json.dumps(bench['meta'], indent=1), flush=True)
print(f"-> benchmark_pairs.json / benchmark_frozen_split.json / benchmark_terms.json "
      f"/ NOT_FOR_RETRIEVAL_blindmap.json", flush=True)
