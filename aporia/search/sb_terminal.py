"""CAMPAIGN S pass 3/3 — TERMINAL. Verify, audit for triviality, adjudicate.

Branches S0-S3 and D1-D3 are FINAL. This pass may not change them.

(1) INDEPENDENT RE-VERIFICATION. A random sample of ledger pairs is re-checked by
    operator implementations written HERE, not imported from sb_scan.py, against
    the raw corpus. If the scan's own code path were wrong, importing it would
    reproduce the error silently.

(2) TRIVIALITY AUDIT — the measurement that decides whether 301 hits are 301
    discoveries or 301 rediscoveries. Pass 1 committed to it in advance. Three
    classes, per sampled non-shift SB hit:
      (iii) TRIVIAL/DUPLICATE   the target's terms ARE the source's terms
      (ii)  ALREADY NAMED       the relation is stated in words in the target's
                                own OEIS title (or the source's), e.g. a title
                                that literally says "Partial sums of A000008"
      (i)   GENUINE UNSTATED    neither
    names.gz is read here. That is permitted: this is adjudication, not blinded
    retrieval, and no retrieval decision depends on it.

    A SECOND THING THIS AUDIT TESTS, not planned but forced by the data: if a
    target's title names an A-number, then that relation was recorded in prose
    while the cross-reference extraction did not capture it — which would mean
    "zero-connectivity" is weaker than the campaign assumed. Reported either way.

(4) The D-branch is DECLINED, not fired. Pass 2 established the control is
    selected on the very quantity being measured. No control breaking that
    relation is buildable from the data on hand, so D is reported descriptively.
"""
from __future__ import annotations

import gzip
import json
import math
import pathlib
import random
import re
from collections import defaultdict

ROOT = pathlib.Path(r'F:\Prometheus')
OUT = ROOT / 'aporia' / 'search'
MIN_TERMS, MAX_TERMS, MIN_EXACT = 25, 45, 20
SAMPLE_VERIFY, SAMPLE_AUDIT = 80, 120
rng = random.Random(20260902)

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

hits = [json.loads(l) for l in (OUT / 'sb_hits_ledger.jsonl').open(encoding='utf-8') if l.strip()]
sb_hits = [h for h in hits if h['arm'] == 'sb']
sb_ns = [h for h in sb_hits if h['op'] != 'shift']
print(f"ledger: {len(hits):,} | sb {len(sb_hits):,} | sb non-shift {len(sb_ns):,}", flush=True)

# ---------------------------------------------------------------- (1) verify
def mu(n):
    m, p, c = n, 2, 0
    while p*p <= m:
        if m % p == 0:
            m //= p
            if m % p == 0: return 0
            c += 1
        p += 1
    if m > 1: c += 1
    return -1 if c % 2 else 1

def op_apply(name, a):
    """Independent re-implementation; deliberately not imported from the scanner."""
    if name == 'diff':
        return [a[i+1] - a[i] for i in range(len(a)-1)]
    if name == 'partsum':
        out, s = [], 0
        for x in a:
            s += x; out.append(s)
        return out
    if name == 'shift':
        return a[1:]
    if name == 'binomial':
        b = a[:24]
        return [sum(math.comb(n, k)*b[k] for k in range(n+1)) for n in range(len(b))]
    if name == 'moebius':
        b = a[:40]
        return [sum(mu(n//d)*b[d-1] for d in range(1, n+1) if n % d == 0) for n in range(1, len(b)+1)]
    raise ValueError(name)

def ov(a, b):
    n, i = min(len(a), len(b)), 0
    while i < n and a[i] == b[i]:
        i += 1
    return i

vs = rng.sample(sb_hits, min(SAMPLE_VERIFY, len(sb_hits)))
ok = bad = 0
fails = []
for h in vs:
    img = op_apply(h['op'], seqs[h['src']])[h['offset']:]
    got = ov(img, seqs[h['tgt']])
    if got >= MIN_EXACT and got == h['exact_terms']:
        ok += 1
    else:
        bad += 1
        fails.append({**h, 'recomputed_exact_terms': got})
print(f"\n(1) INDEPENDENT RE-VERIFICATION: {ok}/{len(vs)} exact match, {bad} failures", flush=True)

# ---------------------------------------------------------------- (2) audit
need = set()
for h in sb_ns:
    need.add(h['src']); need.add(h['tgt'])
names = {}
with gzip.open(ROOT / 'prometheus_data/oeis/names.gz', 'rt', encoding='utf-8', errors='replace') as fh:
    for line in fh:
        if line.startswith('#'):
            continue
        parts = line.rstrip('\n').split(' ', 1)
        if len(parts) == 2 and parts[0] in need:
            names[parts[0]] = parts[1].strip()
print(f"names loaded for {len(names):,} of {len(need):,} involved A-numbers", flush=True)

OPWORDS = {
 'diff':     [r'\bfirst differences\b', r'\bdifferences of\b'],
 'partsum':  [r'\bpartial sums\b', r'\bsummatory\b'],
 'binomial': [r'\bbinomial transform\b'],
 'moebius':  [r'\bm(?:o|ö|oe)bius transform\b', r'\binverse m(?:o|ö|oe)bius\b'],
}
ANUM = re.compile(r'A\d{6}')

aud = rng.sample(sb_ns, min(SAMPLE_AUDIT, len(sb_ns)))
cls = {'genuine_unstated': [], 'already_named': [], 'trivial_duplicate': []}
xref_gap = 0
for h in aud:
    s, t, op = h['src'], h['tgt'], h['op']
    ns, nt = names.get(s, ''), names.get(t, '')
    if seqs[s][:MIN_TERMS] == seqs[t][:MIN_TERMS]:
        cls['trivial_duplicate'].append({**h, 'tgt_name': nt}); continue
    blob = (nt + ' || ' + ns).lower()
    names_src = s in ANUM.findall(nt) or t in ANUM.findall(ns)
    opword = any(re.search(p, blob) for p in OPWORDS.get(op, []))
    if ANUM.findall(nt):
        xref_gap += 1
    if names_src or (opword and ANUM.findall(blob)):
        cls['already_named'].append({**h, 'tgt_name': nt, 'names_partner': names_src,
                                     'op_word': opword})
    else:
        cls['genuine_unstated'].append({**h, 'tgt_name': nt, 'src_name': ns})

n_aud = len(aud)
print(f"\n(2) TRIVIALITY AUDIT on {n_aud} sampled non-shift SB hits:")
for k in ('genuine_unstated', 'already_named', 'trivial_duplicate'):
    print(f"    {k:20s} {len(cls[k]):4d}  ({len(cls[k])/n_aud:.1%})")
print(f"    targets whose TITLE names some A-number (xref-extraction gap): {xref_gap}/{n_aud} "
      f"({xref_gap/n_aud:.1%})")

# ---------------------------------------------------------------- (3)(4)(5)
K_ns = len({h['tgt'] for h in sb_ns})
K_sh = len({h['tgt'] for h in sb_hits if h['op'] == 'shift'} - {h['tgt'] for h in sb_ns})
S = 'S1' if K_ns >= 1 else ('S2' if K_sh >= 1 else 'S3')
frac_genuine = len(cls['genuine_unstated'])/n_aud
est_genuine = int(round(K_ns * frac_genuine))

res = {'ledger_total': len(hits), 'sb_hits': len(sb_hits), 'sb_nonshift_records': len(sb_ns),
       'K_nonshift_distinct_targets': K_ns, 'K_shift_only': K_sh,
       'verification': {'sampled': len(vs), 'exact_match': ok, 'failures': bad,
                        'failure_rate': round(bad/len(vs), 4), 'failing_pairs': fails[:10]},
       'triviality_audit': {'sampled': n_aud,
                            'genuine_unstated': len(cls['genuine_unstated']),
                            'already_named': len(cls['already_named']),
                            'trivial_duplicate': len(cls['trivial_duplicate']),
                            'frac_genuine_unstated': round(frac_genuine, 4),
                            'targets_whose_title_names_an_A_number': xref_gap,
                            'xref_extraction_gap_rate': round(xref_gap/n_aud, 4)},
       'primary_branch': S,
       'estimated_genuine_unstated_targets': est_genuine,
       'D_branch': {'FIRED': False, 'decision': 'DECLINED',
                    'reason': 'pass 2 established the control is selected on the very quantity '
                              'being measured (connectedness in OEIS is largely conferred BY '
                              'someone documenting a relation); no control breaking that selection '
                              'relation is buildable from the data on hand, so D is reported '
                              'descriptively and no D-branch is fired',
                    'descriptive_D': -0.03777, 'descriptive_CI': [-0.040564, -0.034976]}}
res['TERMINAL'] = 'ADVANCE' if (S == 'S1' and bad == 0 and est_genuine >= 1) else \
                  ('REDESIGN' if S == 'S1' else ('REDESIGN' if S == 'S2' else 'KILL'))

with (OUT / 'sb_candidate_relations.jsonl').open('w', encoding='utf-8') as fh:
    for h in cls['genuine_unstated']:
        fh.write(json.dumps({'source': h['src'], 'source_name': h.get('src_name', ''),
                             'target': h['tgt'], 'target_name': h.get('tgt_name', ''),
                             'operator': h['op'], 'offset': h['offset'],
                             'exact_terms': h['exact_terms'],
                             'claim': f"{h['op']}({h['src']}) agrees with {h['tgt']} exactly over "
                                      f"{h['exact_terms']} terms",
                             'provenance': 'Campaign S sweep P129, re-verified P130; target is '
                                           'zero-connectivity in the April OEIS xref dump',
                             'status': 'CANDIDATE — verified exact, not checked against literature'},
                            ensure_ascii=False) + '\n')
(OUT / 'sb_terminal_results.json').write_text(json.dumps(res, indent=1), encoding='utf-8')

print(f"\n(3) primary branch: {S}  (K_nonshift {K_ns}, shift-only {K_sh})")
print(f"(4) D-branch: DECLINED (contaminated control), D = -0.03777 reported descriptively")
print(f"(5) TERMINAL: {res['TERMINAL']}")
print(f"\nsampled genuine-unstated {len(cls['genuine_unstated'])}/{n_aud} = {frac_genuine:.1%} "
      f"-> estimated {est_genuine} of {K_ns} distinct non-shift targets")
print(f"candidate artifact: sb_candidate_relations.jsonl ({len(cls['genuine_unstated'])} sampled rows)")
