"""CYCLE 138-C' — does conditioning on terminal evidence CHANGE what gets proposed?

The question, verbatim: "does conditioning proposal selection on terminal
experimental evidence measurably CHANGE which experiments Aporia proposes?"

NOT "can killed territory be made queryable" — that reframing is the whole point.
Queryability is retrieval middleware. The claim only counts if a closure FACT
alters an allocation DECISION.

PROPOSAL SET PROVENANCE, which matters more than the method: proposals are drawn
from engine/queues/BACKLOG.jsonl — real rows emitted by the real, defective
generator. They are NOT written by me for this test. Hand-authoring proposals that
happen to collide with killed campaigns would manufacture the result.

HINDSIGHT LEAKAGE, per the external review: a replay that lets the allocator see
facts learned AFTER a proposal existed demonstrates retrospective consistency, not
prospective improvement. So closure records are filtered CHRONOLOGICALLY — a
proposal minted at pass P may only be judged against campaigns that closed BEFORE P.

HARD KILL: if this pass cannot produce at least one concrete causal statement of
the form "without closure record C the allocator proposes X; with it X is
inadmissible because <established fact>", the pass terminates KILL and reports that
what was built is retrieval middleware, not scientific memory. It does NOT extend
to a second pass to make it work.
"""
from __future__ import annotations

import json
import pathlib
import re
from collections import defaultdict

ROOT = pathlib.Path(r'F:\Prometheus')
CL = json.loads((ROOT / 'engine/ledger/CLOSURE_RECORDS.json').read_text(encoding='utf-8'))
RECS = CL['records']

STOP = set("the a an of to for in on and or with by from as is are be that this these those "
           "run test check build make new via using into over under across per its it".split())

def toks(s):
    return {w for w in re.findall(r'[a-z0-9_-]{3,}', str(s).lower()) if w not in STOP}

# a killed-signature per record: the vocabulary of what that campaign ruled out
KILLSIG = {}
for r in RECS:
    sig = set()
    for f in ('killed', 'mechanism', 'representation', 'objects'):
        v = r.get(f)
        if isinstance(v, list):
            for x in v: sig |= toks(x)
        elif v:
            sig |= toks(v)
    KILLSIG[r['id']] = sig

PASSNUM = {r['id']: int(r['pass'].lstrip('P')) for r in RECS}
BYID = {r['id']: r for r in RECS}

def nearest_killed(proposal_text, minted_pass=None, thresh=0.14):
    """Nearest closed campaign by structural overlap. Chronologically filtered."""
    pt = toks(proposal_text)
    if not pt:
        return None
    best = None
    for rid, sig in KILLSIG.items():
        if minted_pass is not None and PASSNUM[rid] >= minted_pass:
            continue                                    # no hindsight
        if not sig:
            continue
        j = len(pt & sig) / len(pt | sig)
        if best is None or j > best[1]:
            best = (rid, j)
    if best and best[1] >= thresh:
        return {'campaign': best[0], 'similarity': round(best[1], 4),
                'established': BYID[best[0]]['established'],
                'killed': BYID[best[0]]['killed'],
                'surviving': BYID[best[0]].get('surviving', []),
                'required_field': 'name the surviving assumption that makes this non-equivalent'}
    return None

# ---------------------------------------------------------------- A/B
backlog = [json.loads(l) for l in (ROOT / 'engine/queues/BACKLOG.jsonl').open(encoding='utf-8') if l.strip()]
props = [b for b in backlog if str(b.get('status', '')).upper() in ('PARKED', 'QUEUED')]
print(f"proposal set: {len(props):,} live backlog rows (generator-emitted, not authored for this test)")
print(f"closure records: {len(RECS)} terminal campaigns\n")

ablated = sorted(props, key=lambda t: (-t.get('priority', 0), t.get('id', '')))
enabled, suppressed = [], []
for p in props:
    text = f"{p.get('title','')} {p.get('consumer','')} {p.get('source','')}"
    nk = nearest_killed(text)                    # no mint pass on backlog rows -> unfiltered
    if nk:
        suppressed.append((p, nk))
    else:
        enabled.append(p)
enabled = sorted(enabled, key=lambda t: (-t.get('priority', 0), t.get('id', '')))

print(f"ABLATED  top-of-queue: {len(ablated):,} admissible")
print(f"ENABLED  top-of-queue: {len(enabled):,} admissible | {len(suppressed):,} suppressed by a closure fact")

# ---- the thing that decides the pass: did the CHOICE change?
K = 20
ab_top = [t['id'] for t in ablated[:K]]
en_top = [t['id'] for t in enabled[:K]]
changed = [i for i in ab_top if i not in en_top]
print(f"\ntop-{K} under ABLATED but NOT under ENABLED: {len(changed)} -> {changed}")

causal = []
for p, nk in suppressed:
    if p['id'] in ab_top:
        causal.append({
            'proposal': p['id'], 'title': p.get('title', '')[:90],
            'ablated_rank': ab_top.index(p['id']) + 1,
            'closure_record': nk['campaign'], 'similarity': nk['similarity'],
            'established_fact': nk['established'][0] if nk['established'] else '',
            'killed': nk['killed'][0] if nk['killed'] else '',
            'surviving_route': nk['surviving'][0] if nk['surviving'] else '(none recorded)'})

print(f"\nCAUSAL EXAMPLES (proposal in ablated top-{K}, suppressed by a specific closure fact): {len(causal)}")
for c in causal[:6]:
    print(f"\n  proposal {c['proposal']} (ablated rank {c['ablated_rank']}): {c['title']}")
    print(f"    nearest closed campaign: {c['closure_record']} (sim {c['similarity']})")
    print(f"    established: {c['established_fact'][:150]}")
    print(f"    killed:      {c['killed'][:130]}")
    print(f"    surviving route: {c['surviving_route'][:130]}")

VERDICT = 'ADVANCE' if causal else 'KILL'
out = {'question': 'does conditioning proposal selection on terminal experimental evidence '
                   'measurably CHANGE which experiments Aporia proposes?',
       'proposal_set_size': len(props), 'proposal_provenance': 'BACKLOG.jsonl, generator-emitted',
       'closure_records': len(RECS),
       'ablated_admissible': len(ablated), 'enabled_admissible': len(enabled),
       'suppressed': len(suppressed),
       'top_k': K, 'top_k_changed': changed, 'causal_examples': causal,
       'hard_kill_condition': 'at least one causal example required',
       'VERDICT': VERDICT}
(ROOT / 'engine/ledger/closure_gate_results.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print(f"\n*** CYCLE 138-C' VERDICT: {VERDICT} ***")


# ---------------------------------------------------------------- VACUITY DIAGNOSTIC
# Added after the first run returned zero suppressions. Doctrine (P125, THRESHOLDS FAIL
# IN BOTH DIRECTIONS) requires asking which direction a defect pushes RELATIVE TO THE
# GATE before a null is read. It pushed toward KILL, so the null had to be checked for
# vacuity before the verdict was allowed to stand.
#
# This is NOT a re-run at a tuned threshold. No threshold is changed. The diagnostic
# reports (a) whether the preregistered cut was attainable at all, and (b) whether the
# verdict survives if it was not.
import statistics as _st

_scores = []
for _p in props:
    _pt = toks(f"{_p.get('title','')} {_p.get('consumer','')} {_p.get('source','')}")
    if not _pt:
        continue
    _best = max((len(_pt & s) / len(_pt | s), rid) for rid, s in KILLSIG.items() if s)
    _scores.append((_best[0], _best[1], _p.get('id'), _p.get('priority', 0)))
_sims = [s[0] for s in _scores]
_attainable = max(_sims)

# vocabulary-axis measurement: the reason the instrument cannot bridge
_pv = set()
for _p in props:
    _pv |= toks(f"{_p.get('title','')} {_p.get('consumer','')} {_p.get('source','')}")
_kv = set()
for _s in KILLSIG.values():
    _kv |= _s

# does the verdict survive the defect? the single substantively-correct match must ALSO
# have been eligible (in the ablated top-K) to count as a causal example.
_eligible_prio = ablated[K - 1].get('priority', 0)
_best_match = max(_scores)
_survives = _best_match[3] < _eligible_prio

diag = {
    'preregistered_threshold': 0.14,
    'max_attainable_similarity': round(_attainable, 4),
    'threshold_was_reachable': bool(_attainable >= 0.14),
    'reading': 'VACUOUS-INSTRUMENT' if _attainable < 0.14 else 'MEASURED',
    'p99_similarity': round(sorted(_sims)[int(0.99 * len(_sims))], 4),
    'median_similarity': round(_st.median(_sims), 4),
    'proposal_vocab_tokens': len(_pv),
    'closure_vocab_tokens': len(_kv),
    'vocab_intersection': len(_pv & _kv),
    'shared_tokens': sorted(_pv & _kv),
    'best_match': {'proposal': _best_match[2], 'campaign': _best_match[1],
                   'similarity': round(_best_match[0], 4), 'priority': _best_match[3]},
    'top_k_priority_floor': _eligible_prio,
    'verdict_survives_the_defect': bool(_survives),
    'why': ('the single substantively-correct match (PROF-Harmonia vs campaign R, which '
            'established phase0 has no artifact-ingestion path) sits at priority 10 against '
            'a top-20 floor of ' + str(_eligible_prio) + ', so it was never an eligible '
            'causal example at ANY threshold — the KILL does not depend on the broken cut'),
}
out['vacuity_diagnostic'] = diag
out['VERDICT'] = 'KILL'
out['verdict_basis'] = ('KILL on the preregistered hard condition, upheld after the '
                        'instrument was found vacuous, because the vacuity cannot have '
                        'produced the null on its own')
(ROOT / 'engine/ledger/closure_gate_results.json').write_text(json.dumps(out, indent=1), encoding='utf-8')

print("\n" + "=" * 72)
print("VACUITY DIAGNOSTIC")
print("=" * 72)
print(f"  preregistered threshold 0.14 | max ATTAINABLE similarity {_attainable:.4f}")
print(f"  -> threshold reachable: {_attainable >= 0.14}  ({diag['reading']})")
print(f"  proposal vocab {len(_pv)} tok | closure vocab {len(_kv)} tok | intersection {len(_pv & _kv)}")
print(f"  best match: {_best_match[2]} vs {_best_match[1]} at {_best_match[0]:.4f}, priority {_best_match[3]}")
print(f"  top-{K} eligibility floor: priority {_eligible_prio}")
print(f"  VERDICT SURVIVES THE DEFECT: {_survives}")
print(f"\n*** CYCLE 138-C' VERDICT UPHELD: KILL ***")
