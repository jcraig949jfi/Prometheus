"""CAMPAIGN S pass 1 — INSTRUMENT ONLY. Freeze the Sleeping Beauty target set.

CORRECTION OF RECORD: aporia/docs/HANDBACK_2026-08-22.md claimed OEIS
cross-reference data was not on disk and parked the Sleeping Beauty sweep on
that basis. It was wrong. `cartography/oeis/data/oeis_crossrefs.jsonl` holds
1,588,669 edges. The previous allocation pass flagged "I ruled the set
unobtainable without exhaustively searching the repository" as a stated
weakness and named exactly this as a falsifier; the falsifier fired.

WHAT THIS BUILDS: the zero-connectivity set — corpus sequences with at least 25
terms that appear as neither source nor target of any cross-reference edge. These
are the sequences nothing in OEIS points at and which point at nothing: the
"sleeping beauties".

    corpus with >= 25 terms                       266,122
    distinct A-numbers touched by any edge         347,655
    ZERO-CONNECTIVITY with >= 25 terms              31,189

The 68,770 recorded in memory is a different population — that figure predates the
>= 25-term filter this line uses. Recorded rather than reconciled silently.

MATCHED CONTROL, built here so it cannot be chosen later: an equal-sized sample of
CONNECTED sequences matched on term count, drawn with a fixed seed. Without it a
hit rate among sleeping beauties has nothing to be a hit rate *against*.

NO SCAN IS RUN IN THIS FILE. The primary experiment belongs to pass 2.
"""
from __future__ import annotations

import gzip
import json
import pathlib
import random
from collections import defaultdict

ROOT = pathlib.Path(r'F:\Prometheus')
OUT = ROOT / 'aporia' / 'search'
MIN_TERMS, MAX_TERMS = 25, 45
rng = random.Random(20260901)

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
print(f"corpus with >= {MIN_TERMS} terms: {len(seqs):,}", flush=True)

connected = set()
edges = 0
with open(ROOT / 'cartography/oeis/data/oeis_crossrefs.jsonl', 'r', encoding='utf-8', errors='replace') as fh:
    for line in fh:
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        edges += 1
        if r.get('source'): connected.add(r['source'])
        if r.get('target'): connected.add(r['target'])
print(f"crossref edges: {edges:,} | distinct A-numbers touched: {len(connected):,}", flush=True)

SB = sorted(a for a in seqs if a not in connected)
CONN = [a for a in seqs if a in connected]
print(f"zero-connectivity (SB) with >= {MIN_TERMS} terms: {len(SB):,}", flush=True)
print(f"connected pool available for the control: {len(CONN):,}", flush=True)

# ---- matched control: same size, matched on term count, fixed seed
by_len = defaultdict(list)
for a in CONN:
    by_len[len(seqs[a])].append(a)
for k in by_len:
    rng.shuffle(by_len[k])
ptr = defaultdict(int)
CTRL, unmatched = [], 0
for a in SB:
    L = len(seqs[a])
    lst = by_len.get(L, [])
    if ptr[L] < len(lst):
        CTRL.append(lst[ptr[L]]); ptr[L] += 1
    else:
        unmatched += 1
print(f"matched control drawn: {len(CTRL):,} (unmatched on exact term count: {unmatched:,})", flush=True)

sb_lens = [len(seqs[a]) for a in SB]
ct_lens = [len(seqs[a]) for a in CTRL]
meta = {'corpus_min_terms': MIN_TERMS, 'corpus_size': len(seqs),
        'crossref_edges': edges, 'a_numbers_touched': len(connected),
        'sb_count': len(SB), 'control_count': len(CTRL),
        'control_unmatched_on_term_count': unmatched,
        'sb_mean_terms': round(sum(sb_lens)/len(sb_lens), 2),
        'control_mean_terms': round(sum(ct_lens)/len(ct_lens), 2),
        'seed': 20260901,
        'memory_figure_68770': 'a different population; predates the >=25-term filter used here',
        'correction': 'HANDBACK_2026-08-22.md claimed this data was absent; it is present at '
                      'cartography/oeis/data/oeis_crossrefs.jsonl',
        'scan_run': False}
(OUT / 'sb_targets.json').write_text(json.dumps(
    {'meta': meta, 'sb': SB, 'control': CTRL}, indent=1), encoding='utf-8')
print(json.dumps(meta, indent=1))
print("\nNO SCAN RUN. Primary experiment belongs to pass 2.")
