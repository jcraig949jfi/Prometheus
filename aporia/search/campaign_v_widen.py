"""CAMPAIGN V — one-pass campaign. Widen the operator family, at the same
evidential standard as the 203.

OPERATORS ADDED, chosen for EXACT VERIFIABILITY over interestingness — each either
holds over >= 20 terms or does not, with no tolerance:

    inverse_binomial  B_n = sum_k (-1)^(n-k) C(n,k) A_k
    second_diff       B_n = A_{n+2} - 2A_{n+1} + A_n
    stirling2         B_n = sum_k S2(n,k) A_k          (Stirling transform)
    bisect_even       B_n = A_{2n}
    bisect_odd        B_n = A_{2n+1}
    aerate            B = A_0, 0, A_1, 0, A_2, ...
    runmax            B_n = max(A_0..A_n)

REJECTED: partial products (values explode past any plausible OEIS match while
costing the most per source — high cost, near-zero expected yield); Dirichlet
inverse (needs a division that is not integral in general, so "holds exactly" is
not well defined without extra conditions).

S0 PER OPERATOR, RUN FIRST: each new operator must recover a pair it *should*
find — a synthetic target built as op(A) and temporarily indexed — through the
same probe path the sweep uses. **An operator that fails S0 does not enter the
sweep.** Campaign S's S0 tested one code path; this tests seven.

PRE-STATED BRANCHES, COMMITTED BEFORE ANY COMPUTATION
-----------------------------------------------------
N_new = distinct neglected targets contributed by the widened family that are NOT
already in the existing candidate set, AFTER the full audit chain (title check,
formula check, corrected all-source population).

    V1 KEEP      N_new >= 50   the widened family materially extends the set
    V2 MARGINAL  10 <= N_new < 50   some yield; keep the operators, note diminishing returns
    V3 WASH      N_new < 10    adds little; the line closes with the existing set

PARTITION over non-negative integers: exhaustive and mutually exclusive, verified
by enumeration. CENSUS, not a sample — no sampling error; the 10/50 cuts are
MATERIALITY judgements and are labelled as such. NULL CHECK: new operators finding
nothing gives N_new = 0 -> V3 WASH, which is the correct null output and distinct
from both other branches.

NEW HITS FACE THE SAME AUDIT CHAIN AS THE 203 — title, formula, all-source
population — so they arrive at the same evidential standard, not a lower one.
"""
from __future__ import annotations

import gzip
import json
import math
import pathlib
import re
from collections import defaultdict

ROOT = pathlib.Path(r'F:\Prometheus')
OUT = ROOT / 'aporia' / 'search'
CART = ROOT / 'cartography' / 'oeis' / 'data'
MIN_TERMS, MAX_TERMS, HASH_K, MIN_EXACT = 25, 45, 12, 20
PFX = HASH_K + 1
ANUM = re.compile(r'A\d{6}')

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

# corrected all-source neglected population, rebuilt exactly as Campaign U did
outbound, inbound = set(), set()
def absorb(sid, text):
    ms = ANUM.findall(text)
    others = [m for m in ms if m != sid]
    if others:
        outbound.add(sid); inbound.update(others)
xr = set()
with (CART / 'oeis_crossrefs.jsonl').open(encoding='utf-8', errors='replace') as fh:
    for line in fh:
        if not line.strip(): continue
        try: r = json.loads(line)
        except Exception: continue
        if r.get('source'): xr.add(r['source'])
        if r.get('target'): xr.add(r['target'])
with gzip.open(ROOT / 'prometheus_data/oeis/names.gz', 'rt', encoding='utf-8', errors='replace') as fh:
    for line in fh:
        if line.startswith('#'): continue
        pr = line.rstrip('\n').split(' ', 1)
        if len(pr) == 2: absorb(pr[0], pr[1])
for fn, key in (('oeis_formulas.jsonl', 'formula'), ('oeis_programs.jsonl', 'program')):
    with (CART / fn).open(encoding='utf-8', errors='replace') as fh:
        for line in fh:
            if not line.strip(): continue
            try: r = json.loads(line)
            except Exception: continue
            if r.get('seq_id'): absorb(r['seq_id'], r.get(key, '') or '')
NEG = set(seqs) - (xr | outbound | inbound)
print(f"corrected neglected population: {len(NEG):,}", flush=True)

def nondeg(v):
    w = v[:MIN_TERMS]
    return len(set(w)) >= 8 and not all(x == w[-1] for x in w[-6:])

COMB = [[math.comb(n, k) for k in range(n + 1)] for n in range(30)]
S2 = [[0]*30 for _ in range(30)]
S2[0][0] = 1
for n in range(1, 30):
    for k in range(1, n + 1):
        S2[n][k] = k*S2[n-1][k] + S2[n-1][k-1]

def f_invbin(a):
    b = a[:24]
    return [sum(((-1)**(n-k))*COMB[n][k]*b[k] for k in range(n+1)) for n in range(len(b))]
def f_sdiff(a):   return [a[i+2]-2*a[i+1]+a[i] for i in range(len(a)-2)]
def f_stir2(a):
    b = a[:22]
    return [sum(S2[n][k]*b[k] for k in range(n+1)) for n in range(len(b))]
def f_bise(a):    return a[0::2]
def f_biso(a):    return a[1::2]
def f_aer(a):
    o = []
    for x in a[:23]: o += [x, 0]
    return o[:-1]
def f_rmax(a):
    o, m = [], a[0]
    for x in a:
        m = max(m, x); o.append(m)
    return o
NEWOPS = {'inverse_binomial': f_invbin, 'second_diff': f_sdiff, 'stirling2': f_stir2,
          'bisect_even': f_bise, 'bisect_odd': f_biso, 'aerate': f_aer, 'runmax': f_rmax}

def overlap(a, b):
    n, i = min(len(a), len(b)), 0
    while i < n and a[i] == b[i]:
        i += 1
    return i

def probe(aid, idx, ops):
    out = []
    src = seqs[aid]
    if not nondeg(src): return out
    for op, fn in ops.items():
        try: img0 = fn(src)
        except (ValueError, OverflowError, IndexError): continue
        if len(img0) < MIN_EXACT: continue
        for drop in (0, 1):
            im = img0[drop:]
            if len(im) < HASH_K: continue
            for bid in idx.get(tuple(im[:HASH_K]), ()):
                if bid == aid or not nondeg(seqs[bid]): continue
                if not nondeg(im): continue
                ovl = overlap(im, seqs[bid])
                if ovl >= MIN_EXACT:
                    out.append({'src': aid, 'tgt': bid, 'op': op, 'offset': drop, 'exact_terms': ovl})
    return out

# ---------------------------------------------------------------- S0 per operator
print("\n=== S0 PER OPERATOR ===", flush=True)
probe_src = [a for a in list(seqs)[:4000] if nondeg(seqs[a])]
s0 = {}
for op, fn in NEWOPS.items():
    passed = tested = 0
    for aid in probe_src:
        if tested >= 5: break
        try: img = fn(seqs[aid])
        except Exception: continue
        if len(img) < MIN_EXACT + 2 or not nondeg(img): continue
        tested += 1
        fake = 'ZZ' + str(tested)
        seqs[fake] = img
        idx = {tuple(img[:HASH_K]): [fake]}
        hits = probe(aid, idx, {op: fn})
        if any(h['tgt'] == fake for h in hits): passed += 1
        del seqs[fake]
    s0[op] = {'tested': tested, 'passed': passed, 'PASS': tested > 0 and passed == tested}
    print(f"  {op:18s} {passed}/{tested} -> {'PASS' if s0[op]['PASS'] else 'FAIL'}", flush=True)
ACTIVE = {k: v for k, v in NEWOPS.items() if s0[k]['PASS']}
print(f"operators entering the sweep: {len(ACTIVE)} of {len(NEWOPS)}", flush=True)

# ---------------------------------------------------------------- sweep
index = defaultdict(list)
for a in NEG:
    v = seqs.get(a)
    if v and len(v) >= HASH_K: index[tuple(v[:HASH_K])].append(a)
sources = [a for a in seqs if nondeg(seqs[a])]
print(f"\n=== SWEEP: {len(sources):,} sources x {len(ACTIVE)} new operators ===", flush=True)
hits = []
for aid in sources:
    hits.extend(probe(aid, index, ACTIVE))
print(f"raw hits {len(hits):,} | distinct targets {len({h['tgt'] for h in hits}):,}", flush=True)

# ---------------------------------------------------------------- audit chain
need = set()
for h in hits: need.add(h['src']); need.add(h['tgt'])
names = {}
with gzip.open(ROOT / 'prometheus_data/oeis/names.gz', 'rt', encoding='utf-8', errors='replace') as fh:
    for line in fh:
        if line.startswith('#'): continue
        pr = line.rstrip('\n').split(' ', 1)
        if len(pr) == 2 and pr[0] in need: names[pr[0]] = pr[1].strip()
forms = defaultdict(list)
with (CART / 'oeis_formulas.jsonl').open(encoding='utf-8', errors='replace') as fh:
    for line in fh:
        if not line.strip(): continue
        try: r = json.loads(line)
        except Exception: continue
        if r.get('seq_id') in need: forms[r['seq_id']].append(r.get('formula', ''))

clean = []
for h in hits:
    s, t = h['src'], h['tgt']
    if seqs[s][:MIN_TERMS] == seqs[t][:MIN_TERMS]: continue           # trivial duplicate
    tn, sn = names.get(t, ''), names.get(s, '')
    if s in ANUM.findall(tn) or t in ANUM.findall(sn): continue        # stated in a title
    ftxt = ' '.join(forms.get(t, [])) + ' ' + ' '.join(forms.get(s, []))
    fh_ = set(ANUM.findall(ftxt))
    if s in fh_ or t in fh_: continue                                  # stated in a formula
    clean.append({**h, 'src_name': sn, 'tgt_name': tn})

existing = {json.loads(l)['target'] for l in
            (OUT / 'sb_candidates_corrected_population.jsonl').open(encoding='utf-8') if l.strip()}
new_tgt = {h['tgt'] for h in clean} - existing
N_new = len(new_tgt)

def fire(n):
    if n >= 50: return 'V1', 'KEEP'
    if n >= 10: return 'V2', 'MARGINAL'
    return 'V3', 'WASH'
cov = defaultdict(int)
for n in range(0, 200): cov[fire(n)[0]] += 1
br, term = fire(N_new)
print(f"\npartition over N_new 0..199: {sum(cov.values())} points, coverage {dict(cov)}")
print(f"  boundaries: 9->{fire(9)[0]} 10->{fire(10)[0]} 49->{fire(49)[0]} 50->{fire(50)[0]}")

per_op = defaultdict(set)
for h in clean:
    if h['tgt'] in new_tgt: per_op[h['op']].add(h['tgt'])
print(f"\nafter audit chain: {len(clean):,} clean records | NEW distinct neglected targets N_new = {N_new}")
print(f"  per operator: {dict(sorted((k, len(v)) for k, v in per_op.items()))}")
print(f"BRANCH {br} -> {term}")

# ---------------------------------------------------------------- consolidate
old = [json.loads(l) for l in (OUT / 'sb_candidates_corrected_population.jsonl').open(encoding='utf-8') if l.strip()]
cons = list(old)
for h in clean:
    if h['tgt'] in new_tgt:
        cons.append({'source': h['src'], 'source_name': h['src_name'], 'target': h['tgt'],
                     'target_name': h['tgt_name'], 'operator': h['op'], 'offset': h['offset'],
                     'exact_terms': h['exact_terms'],
                     'claim': f"{h['op']}({h['src']}) agrees with {h['tgt']} exactly over {h['exact_terms']} terms",
                     'provenance': 'Campaign V widened family, S0-gated per operator; same audit chain as the 203',
                     'status': 'CANDIDATE - verified exact; not in either title, formula or program text; '
                               'target neglected under the corrected all-source definition',
                     'population': 'corrected (crossrefs + titles + formulas + programs, inbound and outbound)'})
with (OUT / 'CANDIDATE_RELATIONS_CONSOLIDATED.jsonl').open('w', encoding='utf-8') as fh:
    for c in sorted(cons, key=lambda x: (-x['exact_terms'], x['target'])):
        fh.write(json.dumps(c, ensure_ascii=False) + '\n')
final_tgt = {c['target'] for c in cons}
print(f"\nCONSOLIDATED: {len(cons)} records over {len(final_tgt)} distinct targets")

res = {'new_operators': list(NEWOPS), 'S0': s0, 'operators_active': list(ACTIVE),
       'neglected_population': len(NEG), 'raw_hits': len(hits),
       'clean_after_audit': len(clean), 'N_new': N_new, 'per_operator_new': {k: len(v) for k, v in per_op.items()},
       'branch': br, 'TERMINAL': term,
       'partition': {'points': sum(cov.values()), 'coverage': dict(cov)},
       'census_not_sample': True, 'thresholds': 'materiality judgements; census has no sampling error',
       'consolidated_records': len(cons), 'consolidated_targets': len(final_tgt),
       'supersedes': ['sb_candidate_relations.jsonl', 'sb_candidates_formula_survivors.jsonl',
                      'sb_candidates_corrected_population.jsonl']}
(OUT / 'campaign_v_results.json').write_text(json.dumps(res, indent=1), encoding='utf-8')
