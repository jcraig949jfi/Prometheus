"""CAMPAIGN F — one-pass campaign. Do the candidate relations FACTOR?

THE QUESTION THIS ANSWERS, AND THE ONE IT DOES NOT
---------------------------------------------------
The decisive check on the candidate set — is any relation actually unknown to
mathematics — cannot be run by this loop. This is the closest machine-executable
proxy: does a candidate relation `op(A) = B` factor through a third corpus
sequence, i.e. does there exist C and operators op1, op2 in the family with
`op1(A) = C` and `op2(C) = B`, both exact over >= 20 terms?

**A factoring relation is IMPLIED by two simpler ones.** It is not atomic, and it
is correspondingly less likely to be an interesting fact in its own right.

**This is a FACTORISATION test, not a novelty test.** A composition can still be
unnoticed. What it gives is a triage signal — atomic relations first — not a
verdict on novelty. Scoped here before any number exists.

PRE-STATED BRANCHES, COMMITTED BEFORE COMPUTATION
--------------------------------------------------
P = fraction of non-trivial-operator candidate targets whose relation factors.

    F1 MOSTLY-COMPOSITE   P >= 0.60   most candidates are compositions; novelty value
                                      is low and triage starts with the minority that
                                      does not factor
    F2 MIXED              0.20 <= P < 0.60   substantial factoring; the non-factoring
                                      subset is the priority
    F3 MOSTLY-ATOMIC      P < 0.20    most candidates do not factor; they are atomic
                                      relations and the set retains its value

PARTITION over [0,1]: exhaustive and mutually exclusive, verified by enumeration.
CENSUS of all non-trivial candidates — no sampling error; the 0.20/0.60 cuts are
MATERIALITY judgements, labelled as such.
NULL CHECK: nothing factors -> P = 0 -> F3; everything factors -> P = 1 -> F1.
Extremes map to distinct branches, so the rule discriminates.

TRIVIAL-CLASS OPERATORS ARE EXCLUDED from the denominator, per Campaign V: shift,
runmax, aerate and the two bisections are the trivial control class and their
candidates are not part of the honest core.
"""
from __future__ import annotations

import gzip
import json
import math
import pathlib
from collections import defaultdict

ROOT = pathlib.Path(r'F:\Prometheus')
OUT = ROOT / 'aporia' / 'search'
MIN_TERMS, MAX_TERMS, HASH_K, MIN_EXACT = 25, 45, 12, 20
TRIVIAL = {'shift', 'runmax', 'aerate', 'bisect_even', 'bisect_odd'}

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

COMB = [[math.comb(n, k) for k in range(n + 1)] for n in range(30)]
S2 = [[0]*30 for _ in range(30)]; S2[0][0] = 1
for n in range(1, 30):
    for k in range(1, n + 1):
        S2[n][k] = k*S2[n-1][k] + S2[n-1][k-1]
def mob(n):
    m, p, c = n, 2, 0
    while p*p <= m:
        if m % p == 0:
            m //= p
            if m % p == 0: return 0
            c += 1
        p += 1
    if m > 1: c += 1
    return -1 if c % 2 else 1
MU = [0] + [mob(i) for i in range(1, MAX_TERMS + 2)]
DIV = [[] for _ in range(MAX_TERMS + 2)]
for d in range(1, MAX_TERMS + 2):
    for n in range(d, MAX_TERMS + 2, d): DIV[n].append(d)

OPS = {
 'diff':     lambda a: [a[i+1]-a[i] for i in range(len(a)-1)],
 'partsum':  lambda a: [sum(a[:i+1]) for i in range(len(a))],
 'binomial': lambda a: [sum(COMB[n][k]*a[:24][k] for k in range(n+1)) for n in range(len(a[:24]))],
 'moebius':  lambda a: [sum(MU[n//d]*a[:40][d-1] for d in DIV[n] if d <= len(a[:40])) for n in range(1, len(a[:40])+1)],
 'shift':    lambda a: a[1:],
 'inverse_binomial': lambda a: [sum(((-1)**(n-k))*COMB[n][k]*a[:24][k] for k in range(n+1)) for n in range(len(a[:24]))],
 'second_diff': lambda a: [a[i+2]-2*a[i+1]+a[i] for i in range(len(a)-2)],
 'stirling2': lambda a: [sum(S2[n][k]*a[:22][k] for k in range(n+1)) for n in range(len(a[:22]))],
 'bisect_even': lambda a: a[0::2],
 'bisect_odd':  lambda a: a[1::2],
 'aerate':   lambda a: [x for p in ((v, 0) for v in a[:23]) for x in p][:-1],
 'runmax':   lambda a: [max(a[:i+1]) for i in range(len(a))],
}

index = defaultdict(list)
for a, v in seqs.items():
    if len(v) >= HASH_K: index[tuple(v[:HASH_K])].append(a)
print(f"full-corpus index keys: {len(index):,}", flush=True)

def ov(a, b):
    n, i = min(len(a), len(b)), 0
    while i < n and a[i] == b[i]:
        i += 1
    return i

def images(aid):
    """All exact op-images of aid landing on a corpus sequence."""
    out = []
    src = seqs[aid]
    for op, fn in OPS.items():
        try: img0 = fn(src)
        except Exception: continue
        if len(img0) < MIN_EXACT: continue
        for drop in (0, 1):
            im = img0[drop:]
            if len(im) < HASH_K: continue
            for cid in index.get(tuple(im[:HASH_K]), ()):
                if cid != aid and ov(im, seqs[cid]) >= MIN_EXACT:
                    out.append((op, cid))
    return out

def hits_target(cid, bid):
    """Operators taking cid exactly to bid."""
    out = []
    src = seqs[cid]
    for op, fn in OPS.items():
        try: img0 = fn(src)
        except Exception: continue
        if len(img0) < MIN_EXACT: continue
        for drop in (0, 1):
            im = img0[drop:]
            if ov(im, seqs[bid]) >= MIN_EXACT:
                out.append(op); break
    return out

cands = [json.loads(l) for l in (OUT / 'CANDIDATE_RELATIONS_CONSOLIDATED.jsonl').open(encoding='utf-8') if l.strip()]
core = [c for c in cands if c['operator'] not in TRIVIAL]
core_tgt = {c['target'] for c in core}
print(f"consolidated {len(cands)} records | non-trivial core {len(core)} records over {len(core_tgt)} targets", flush=True)

fact_tgt, atomic = set(), []
chains = []
for c in core:
    A, B = c['source'], c['target']
    if A not in seqs or B not in seqs: continue
    found = None
    for op1, C in images(A):
        if C == B: continue
        ops2 = hits_target(C, B)
        if ops2:
            found = (op1, C, ops2[0]); break
    if found:
        fact_tgt.add(B)
        chains.append({**c, 'factors_via': {'op1': found[0], 'intermediate': found[1], 'op2': found[2]}})
    else:
        atomic.append(c)

P = len(fact_tgt)/len(core_tgt) if core_tgt else 0.0
def fire(p):
    if p >= 0.60: return 'F1', 'MOSTLY-COMPOSITE'
    if p >= 0.20: return 'F2', 'MIXED'
    return 'F3', 'MOSTLY-ATOMIC'
grid = [round(x/1000, 3) for x in range(1001)]
cov = defaultdict(int)
for g in grid: cov[fire(g)[0]] += 1
br, term = fire(P)
print(f"\npartition: {len(grid)} points, coverage {dict(cov)}")
print(f"  boundaries: 0.199->{fire(0.199)[0]} 0.200->{fire(0.200)[0]} 0.599->{fire(0.599)[0]} 0.600->{fire(0.600)[0]}")
print(f"\nfactoring targets {len(fact_tgt)}/{len(core_tgt)} = P = {P:.4f}  ->  {br} {term}")

atomic_tgt = core_tgt - fact_tgt
with (OUT / 'CANDIDATES_ATOMIC.jsonl').open('w', encoding='utf-8') as fh:
    for c in sorted(atomic, key=lambda x: (-x['exact_terms'], x['target'])):
        if c['target'] in atomic_tgt:
            fh.write(json.dumps({**c, 'factorisation': 'ATOMIC - no two-step chain through any corpus '
                                 'sequence under the 12-operator family'}, ensure_ascii=False) + '\n')
res = {'consolidated_records': len(cands), 'core_records': len(core), 'core_targets': len(core_tgt),
       'factoring_targets': len(fact_tgt), 'atomic_targets': len(atomic_tgt), 'P': round(P, 4),
       'branch': br, 'TERMINAL': term, 'partition': {'points': len(grid), 'coverage': dict(cov)},
       'census_not_sample': True,
       'scope': 'FACTORISATION test, not a novelty test — a composition can still be unnoticed',
       'trivial_operators_excluded': sorted(TRIVIAL),
       'example_chains': chains[:5]}
(OUT / 'campaign_f_results.json').write_text(json.dumps(res, indent=1), encoding='utf-8')
print(f"atomic artifact: CANDIDATES_ATOMIC.jsonl ({len(atomic_tgt)} targets)")
