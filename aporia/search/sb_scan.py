"""CAMPAIGN S pass 2/3 — the exact sweep. S0 positive control first.

Branches S0-S3 and D1-D3 are FINAL in CAMPAIGN_S_PASS1 and are NOT adjudicated
here. This pass runs the scan and reports counts with the underlying pairs.

WHAT IS BEING ASKED: for each of the 31,189 zero-connectivity sequences B, does
there exist a corpus sequence A and one of five operators with op(A) = B exactly
over >= 20 overlapping terms? Same question, independently, for the 31,189
term-count-matched connected controls.

S0 POSITIVE CONTROL RUNS FIRST. The sweep code path is pointed at known verified
pairs from Campaign W's benchmark. If it cannot recover relations it is known to
contain, it cannot be trusted to report their absence, and the pass emits PARK
with NO counts.

FEASIBILITY, disclosed: a naive uncapped scan recomputes each full operator image
(binomial is O(24^2) big-integer work) for 230,694 sources x 5 operators. Instead
only the first 13 image terms are computed for the hash lookup, and the FULL image
is computed only on a hash hit for exact verification. That is an exact
optimisation — it changes cost, not results, because a pair can only verify if its
12-term prefix matches.

DEGENERACY FILTER, disclosed: the same filter every prior builder used is applied
to source and image (>= 8 distinct values in-window, not eventually constant).
BUILD-1 of Campaign X failed totally because a degenerate object is a simultaneous
fixed point of all five operators and saturates everything; the filter exists
because of that failure.

NO ADJUDICATION. NO TUNING.
"""
from __future__ import annotations

import gzip
import json
import math
import pathlib
import time
from collections import defaultdict

ROOT = pathlib.Path(r'F:\Prometheus')
OUT = ROOT / 'aporia' / 'search'
MIN_TERMS, MAX_TERMS, HASH_K, MIN_EXACT = 25, 45, 12, 20
PFX = HASH_K + 1                      # 13 terms covers offsets 0 and 1

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

tg = json.loads((OUT / 'sb_targets.json').read_text(encoding='utf-8'))
SB = set(tg['sb']); CTRL = set(tg['control'])
print(f"SB {len(SB):,} | control {len(CTRL):,}", flush=True)

def nondeg(v):
    w = v[:MIN_TERMS]
    return len(set(w)) >= 8 and not all(x == w[-1] for x in w[-6:])

# index only over the two target arms — the sweep asks about them alone
index = defaultdict(list)
for a in (SB | CTRL):
    v = seqs.get(a)
    if v and len(v) >= HASH_K:
        index[tuple(v[:HASH_K])].append(a)
print(f"target index keys: {len(index):,}", flush=True)

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
DIVS = [[] for _ in range(MAX_TERMS + 2)]
for d in range(1, MAX_TERMS + 2):
    for n in range(d, MAX_TERMS + 2, d):
        DIVS[n].append(d)
COMB = [[math.comb(n, k) for k in range(n + 1)] for n in range(MAX_TERMS + 2)]

def full_diff(a):    return [a[i+1]-a[i] for i in range(len(a)-1)]
def full_partsum(a):
    o, s = [], 0
    for x in a: s += x; o.append(s)
    return o
def full_binomial(a, cap=24):
    a = a[:cap]
    return [sum(COMB[n][k]*a[k] for k in range(n+1)) for n in range(len(a))]
def full_moebius(a, cap=40):
    a = a[:cap]
    return [sum(MU[n//d]*a[d-1] for d in DIVS[n] if d <= len(a)) for n in range(1, len(a)+1)]
def full_shift(a):   return a[1:]
FULL = {'diff': full_diff, 'partsum': full_partsum, 'binomial': full_binomial,
        'moebius': full_moebius, 'shift': full_shift}

def pfx_diff(a):     return [a[i+1]-a[i] for i in range(min(PFX, len(a)-1))]
def pfx_partsum(a):
    o, s = [], 0
    for x in a[:PFX]: s += x; o.append(s)
    return o
def pfx_binomial(a): return [sum(COMB[n][k]*a[k] for k in range(n+1)) for n in range(min(PFX, len(a)))]
def pfx_moebius(a):  return [sum(MU[n//d]*a[d-1] for d in DIVS[n]) for n in range(1, min(PFX, len(a))+1)]
def pfx_shift(a):    return a[1:1+PFX]
PFXF = {'diff': pfx_diff, 'partsum': pfx_partsum, 'binomial': pfx_binomial,
        'moebius': pfx_moebius, 'shift': pfx_shift}

def overlap(a, b):
    n, i = min(len(a), len(b)), 0
    while i < n and a[i] == b[i]:
        i += 1
    return i

def probe(aid, want=None):
    """Return verified hits for one source. want=None -> both arms."""
    out = []
    src = seqs[aid]
    if not nondeg(src):
        return out
    for op, pf in PFXF.items():
        try:
            pv = pf(src)
        except (ValueError, OverflowError):
            continue
        for drop in (0, 1):
            key = tuple(pv[drop:drop+HASH_K])
            if len(key) < HASH_K:
                continue
            cands = index.get(key)
            if not cands:
                continue
            try:
                img = FULL[op](src)[drop:]
            except (ValueError, OverflowError):
                continue
            if not nondeg(img):
                continue
            for bid in cands:
                if bid == aid:
                    continue
                ov = overlap(img, seqs[bid])
                if ov >= MIN_EXACT:
                    out.append({'src': aid, 'tgt': bid, 'op': op, 'offset': drop, 'exact_terms': ov})
    return out

# ---------------------------------------------------------------- S0
print("\n=== S0 POSITIVE CONTROL ===", flush=True)
wp = json.loads((OUT / 'w_pairs.json').read_text(encoding='utf-8'))
wm = json.loads((OUT / 'NOT_FOR_RETRIEVAL_w_blindmap.json').read_text(encoding='utf-8'))
sample = wp['positives'][:40]
found = 0; checked = 0
for p in sample:
    A, B = wm.get(p['src']), wm.get(p['tgt'])
    if A not in seqs or B not in seqs:
        continue
    checked += 1
    idx2 = defaultdict(list)
    v = seqs[B]
    idx2[tuple(v[:HASH_K])].append(B)
    saved = dict(index)
    index.clear(); index.update(idx2)
    hits = probe(A)
    index.clear(); index.update(saved)
    if any(h['tgt'] == B and h['op'] == p['op'] for h in hits):
        found += 1
S0 = (checked > 0 and found == checked)
print(f"known pairs checked {checked} | recovered by the sweep code path {found} -> "
      f"S0 {'PASS' if S0 else 'FAIL'}")

res = {'S0': {'checked': checked, 'recovered': found, 'PASS': bool(S0)}}
if not S0:
    res.update({'scan_run': False, 'TERMINAL_PROVISIONAL': 'PARK',
                'reason': 'S0 positive control failed; an instrument that cannot find relations it '
                          'is known to contain cannot report their absence'})
    (OUT / 'sb_scan_results.json').write_text(json.dumps(res, indent=1), encoding='utf-8')
    print("\nS0 FAILED. No counts reported. PARK.")
    raise SystemExit(0)

# ---------------------------------------------------------------- sweep
print("\n=== SWEEP (uncapped) ===", flush=True)
sources = [a for a in seqs if nondeg(seqs[a])]
print(f"non-degenerate sources: {len(sources):,}", flush=True)
hits_sb, hits_ct = [], []
t0 = time.time(); done = 0
for aid in sources:
    done += 1
    if done % 40000 == 0:
        print(f"  {done:,}/{len(sources):,} ({done/len(sources):.1%}) "
              f"| sb {len(hits_sb)} ctl {len(hits_ct)} | {time.time()-t0:.0f}s", flush=True)
    for h in probe(aid):
        (hits_sb if h['tgt'] in SB else hits_ct).append(h)
elapsed = time.time() - t0
print(f"sweep COMPLETE: {done:,}/{len(sources):,} sources in {elapsed:.0f}s", flush=True)

def summarize(hits, arm):
    tg_hit = {h['tgt'] for h in hits}
    ns = {h['tgt'] for h in hits if h['op'] != 'shift'}
    sh = {h['tgt'] for h in hits if h['op'] == 'shift'}
    per = defaultdict(set)
    for h in hits:
        per[h['op']].add(h['tgt'])
    return {'arm': arm, 'raw_hit_records': len(hits), 'distinct_targets_hit': len(tg_hit),
            'K_nonshift': len(ns), 'K_shift_only': len(sh - ns), 'K_shift_any': len(sh),
            'per_operator_distinct_targets': {k: len(v) for k, v in sorted(per.items())}}

res['sweep'] = {'sources_scanned': done, 'sources_total': len(sources),
                'fraction_complete': round(done/len(sources), 6), 'elapsed_s': round(elapsed, 1),
                'sb': summarize(hits_sb, 'sleeping_beauties'),
                'control': summarize(hits_ct, 'matched_control')}

n = len(SB)
k_sb = res['sweep']['sb']['distinct_targets_hit']
k_ct = res['sweep']['control']['distinct_targets_hit']
r_sb, r_ct = k_sb/n, k_ct/n
p = (k_sb + k_ct)/(2*n)
se = math.sqrt(2*p*(1-p)/n) if 0 < p < 1 else 0.0
D = r_sb - r_ct
res['D'] = {'R_sb': f"{k_sb}/{n}", 'R_sb_rate': round(r_sb, 6),
            'R_ctl': f"{k_ct}/{n}", 'R_ctl_rate': round(r_ct, 6),
            'D': round(D, 6), 'pooled_rate': round(p, 6), 'SE_diff': round(se, 6),
            'ci95': [round(D-1.96*se, 6), round(D+1.96*se, 6)],
            'MEASURED_MDE_2SE': round(2*se, 6),
            'preregistered_threshold_T': round(2*(2*se), 6),
            'note': 'T = 2 x measured MDE, computed here per the preregistration; not inherited'}

with (OUT / 'sb_hits_ledger.jsonl').open('w', encoding='utf-8') as fh:
    for h in hits_sb:
        fh.write(json.dumps({**h, 'arm': 'sb'}, ensure_ascii=False) + '\n')
    for h in hits_ct:
        fh.write(json.dumps({**h, 'arm': 'control'}, ensure_ascii=False) + '\n')
res['ledger'] = 'aporia/search/sb_hits_ledger.jsonl (every hit as a checkable pair)'
res['scan_run'] = True
res['adjudicated'] = False
(OUT / 'sb_scan_results.json').write_text(json.dumps(res, indent=1), encoding='utf-8')

print(f"\nSB      : {json.dumps(res['sweep']['sb'])}")
print(f"CONTROL : {json.dumps(res['sweep']['control'])}")
print(f"\nD = {D:+.6f}  CI {res['D']['ci95']}  SE {se:.6f}  measured MDE {2*se:.6f}  T {4*se:.6f}")
print(f"R_sb {k_sb}/{n} = {r_sb:.6f} | R_ctl {k_ct}/{n} = {r_ct:.6f}")
print("\nNOT adjudicated. Pass 3 verifies each pair and reads the branches.")
