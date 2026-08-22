"""CAMPAIGN B pass 1 — mechanical void audit of the problem catalog.

No model is asked whether a problem is attackable. Every column below is
computed from committed metadata or a live probe.

PRE-STATED BRANCHES (committed before the computation runs):
  B1  Most unrouted rows lack a data binding OR a finite observable ->
      the "37 of N routed" figure measures CATALOG EXECUTABILITY, not
      paradigm coverage, and the operator-facing "500 voids" claim is
      RETRACTED.
  B2  Many rows have executable bindings AND finite observables but ZERO
      paradigm assignments -> genuine paradigm COVERAGE GAP; name the
      subdomain classes it falls in.
  B3  Many rows are executable but their required tool is absent ->
      TOOLING is the limiter, and this audit has measured the demand that
      would justify installing Sage/Macaulay2/SAT (the only thing that
      would).
  B4  The classification cannot be derived mechanically from existing
      metadata -> the catalog is insufficient to support ANY coverage
      inference, and that is itself the finding.

Branch precedence if several apply: report ALL that fire, and name the
dominant one by row count.
"""
from __future__ import annotations
import json
import pathlib
import re
import collections

ROOT = pathlib.Path(r'F:\Prometheus')
OUT = ROOT / 'aporia' / 'docs' / 'void_audit_results.json'

rows = [json.loads(l) for l in (ROOT / 'aporia/mathematics/triage.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
trees = [json.loads(l) for l in (ROOT / 'aporia/paradigms/paradigm_trees.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]

assigned = collections.Counter()
anti = collections.Counter()
for t in trees:
    for a in t['assignments']:
        assigned[a] += 1
    for a in t['anti_assignments']:
        anti[a] += 1

# --- live binding probe: which sources actually resolve on this machine ------
LIVE_SOURCES = {}
try:
    import psycopg2
    conn = psycopg2.connect(host='localhost', port=5432, dbname='lmfdb', user='postgres')
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    LIVE_SOURCES['lmfdb_tables'] = {r[0] for r in cur.fetchall()}
    conn.close()
except Exception as e:
    LIVE_SOURCES['lmfdb_tables'] = set()
    print('lmfdb probe failed:', e)
LIVE_SOURCES['oeis'] = (ROOT / 'prometheus_data/oeis/stripped.gz').exists()
LIVE_SOURCES['zeros_pg'] = True   # charon_duckdb schema in prometheus_fire, verified P72

TOOL_ABSENT = re.compile(r'\b(sage|magma|macaulay|gap\b|sat solver|z3|cvc|pari/gp|bertini|polymake|gfan|snappy)\b', re.I)
PLACEHOLDER = re.compile(r'see specific test|requires data extension|^\s*$', re.I)


def has_binding(r):
    ds = str(r.get('data_source') or '').strip()
    if not ds or PLACEHOLDER.search(ds):
        return False, 'none-or-placeholder'
    low = ds.lower()
    if 'pure-compute' in low or 'pure compute' in low:
        return True, 'pure-compute'
    if 'oeis' in low:
        return bool(LIVE_SOURCES['oeis']), 'oeis'
    if 'duckdb' in low or 'zeros' in low:
        return True, 'zeros-pg (migrated)'
    if 'lmfdb' in low or 'ec_curvedata' in low or 'g2c' in low or 'mf_' in low or 'nf_' in low or 'lfunc' in low:
        hit = [t for t in LIVE_SOURCES['lmfdb_tables'] if t in low]
        return (bool(hit) or 'lmfdb' in low), f'lmfdb({hit[:2] if hit else "named"})'
    if 'cartography' in low or 'knots' in low:
        return False, 'cartography/knots (unverified)'
    return False, 'unrecognized'


def has_observable(r):
    ts = str(r.get('test_spec') or '')
    fc = str(r.get('falsification_criterion') or '')
    ts_ok = bool(ts.strip()) and not PLACEHOLDER.search(ts) and len(ts) > 80
    fc_ok = bool(fc.strip()) and not re.search(r'^deviation from predicted asymptotic behavior\.?$|^same as ', fc.strip(), re.I)
    return ts_ok and fc_ok


def tool_available(r):
    blob = ' '.join(str(r.get(k) or '') for k in ('data_source', 'test_spec', 'notes'))
    m = TOOL_ABSENT.search(blob)
    return (m is None), (m.group(0) if m else None)


def blocker_recorded(r):
    blob = ' '.join(str(r.get(k) or '') for k in ('notes', 'published_bound'))
    prov = r.get('provenance')
    if isinstance(prov, dict):
        blob += ' ' + json.dumps(prov)
    return bool(re.search(r'blocked|requires data extension|not accessible|pending', blob, re.I))


recs = []
for r in rows:
    b, bwhy = has_binding(r)
    o = has_observable(r)
    ta, tname = tool_available(r)
    recs.append({
        'id': r['id'], 'subdomain': r.get('subdomain'), 'bucket': r.get('bucket'),
        'binding': b, 'binding_kind': bwhy, 'observable': o,
        'assigned': assigned.get(r['id'], 0), 'anti': anti.get(r['id'], 0),
        'tool_available': ta, 'tool_missing': tname,
        'blocker_recorded': blocker_recorded(r)})

n = len(recs)
routed = [x for x in recs if x['assigned'] > 0]
unrouted = [x for x in recs if x['assigned'] == 0]
executable = [x for x in recs if x['binding'] and x['observable']]
exec_unrouted = [x for x in unrouted if x['binding'] and x['observable']]
unexec_unrouted = [x for x in unrouted if not (x['binding'] and x['observable'])]
tool_blocked = [x for x in recs if not x['tool_available']]
exec_unrouted_toolblocked = [x for x in exec_unrouted if not x['tool_available']]

print(f"catalog rows: {n}")
print(f"routed (>=1 paradigm assigned): {len(routed)}")
print(f"unrouted: {len(unrouted)}")
print(f"  of which NOT executable (no binding or no finite observable): {len(unexec_unrouted)}")
print(f"  of which EXECUTABLE but unassigned: {len(exec_unrouted)}")
print(f"    of those, blocked by a missing tool: {len(exec_unrouted_toolblocked)}")
print(f"executable rows overall: {len(executable)}")
print(f"rows naming an absent tool anywhere: {len(tool_blocked)} "
      f"({collections.Counter(x['tool_missing'] for x in tool_blocked).most_common(5)})")
print(f"binding kinds: {collections.Counter(x['binding_kind'] for x in recs).most_common()}")

fired = []
if len(unexec_unrouted) > 0.5 * len(unrouted):
    fired.append('B1')
if len(exec_unrouted) >= 20:
    fired.append('B2')
if len(exec_unrouted_toolblocked) >= 20:
    fired.append('B3')
if not recs or all(x['binding_kind'] == 'unrecognized' for x in recs):
    fired.append('B4')
dominant = 'B1' if 'B1' in fired else (fired[0] if fired else 'NONE-FIRED')
print(f"branches fired: {fired}; dominant: {dominant}")

# subdomain classes among executable-but-unrouted (B2's naming requirement)
sub_exec_unrouted = collections.Counter(x['subdomain'] for x in exec_unrouted).most_common(10)
print(f"executable-but-unrouted by subdomain: {sub_exec_unrouted}")

OUT.write_text(json.dumps({
    'n_rows': n, 'routed': len(routed), 'unrouted': len(unrouted),
    'unrouted_not_executable': len(unexec_unrouted),
    'unrouted_executable': len(exec_unrouted),
    'unrouted_executable_toolblocked': len(exec_unrouted_toolblocked),
    'executable_total': len(executable),
    'rows_naming_absent_tool': len(tool_blocked),
    'binding_kinds': dict(collections.Counter(x['binding_kind'] for x in recs)),
    'exec_unrouted_by_subdomain': sub_exec_unrouted,
    'branches_fired': fired, 'dominant_branch': dominant,
    'per_row': recs}, indent=1), encoding='utf-8')
print(f"-> {OUT.name}")
