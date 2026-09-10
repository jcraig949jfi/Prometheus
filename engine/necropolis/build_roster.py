#!/usr/bin/env python3
"""
Necropolis roster builder — DERIVES ROSTER.jsonl from repository evidence, not memory.

Sources (all read-only):
  docs/state.json                                 -> canonical agent registry (48)
  engine/ledger/AGENT_AUTOPSIES.jsonl             -> which agents are autopsied (21) + failure_class
  pivot/PROCESS_TABLE_2026-06-24.md               -> 2026-06 advisory disposition (43-subset)
  pivot/COMPONENT_DOSSIERS_2026-06-24.md          -> which have a full thoughtwork dossier
  agents/<name_lower>/                             -> source-location presence

Run from the repo root:  python engine/necropolis/build_roster.py
Emits engine/necropolis/ROSTER.jsonl (one intake row per canonical agent).
The roster is INTAKE ONLY: no resurrection decisions are made here (Necropolis LAW N3).
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def p(*a): return os.path.join(ROOT, *a)

# --- canonical registry -----------------------------------------------------
state = json.load(open(p('docs','state.json'), encoding='utf-8'))
agents = state['agents']

# --- autopsy layer ----------------------------------------------------------
autopsy = {}
for line in open(p('engine','ledger','AGENT_AUTOPSIES.jsonl'), encoding='utf-8'):
    line = line.strip()
    if not line: continue
    r = json.loads(line)
    autopsy[r['agent_id']] = r.get('failure_class','')

# --- 2026-06 advisory disposition (43-subset) -------------------------------
disp = {}
pt = open(p('pivot','PROCESS_TABLE_2026-06-24.md'), encoding='utf-8').read()
for m in re.finditer(r'^\|\s*([A-Za-z0-9_\-]+)\s*\|.*\|\s*(?:_suggest:_\s*)?([A-Za-z0-9\-]+(?:-after-HITL)?)\s*\|\s*y\s*\|', pt, re.M):
    name, d = m.group(1), m.group(2)
    if name != 'Component':
        disp[name] = d

# --- full thoughtwork dossier presence --------------------------------------
dtext = open(p('pivot','COMPONENT_DOSSIERS_2026-06-24.md'), encoding='utf-8').read()

def has_dossier(name):
    # a dedicated section header naming the component
    pats = [rf'^#+\s*.*\b{re.escape(name)}\b.*dossier', rf'^#+\s*Dossier\s+\d+\s*[—-]\s*{re.escape(name)}\b',
            rf'^#+\s*{re.escape(name)}\b']
    return any(re.search(pt, dtext, re.M|re.I) for pt in pats)

# --- family inference -------------------------------------------------------
CLUSTER = {  # autopsy taxonomy cluster membership (AUTOPSY_TAXONOMY.md)
 'Atalanta':'DEAD-GATING','Moros':'DEAD-GATING','Nephele':'DEAD-GATING(latent)','Nemesis':'BOUNDED-MENU-SATURATION/DEAD-GATING',
 'Acheron':'LOW-BITS-EMISSION','Pollux':'LOW-BITS-EMISSION','Hecate':'LOW-BITS-EMISSION','Polyhymnia':'LOW-BITS-EMISSION/STUB-ADAPTATION','Hypatia':'LOW-BITS-EMISSION',
 'Sophia':'BOUNDED-MENU-SATURATION','Charon_Loop':'SELECTION-DECOUPLED','Telos':'SELECTION-DECOUPLED','Harmonia_Loop':'SELECTION-DECOUPLED',
 'Argos':'SEAM-BROKEN','Erebos':'SEAM-BROKEN','Lethe':'SEMANTIC-TASK-SYNTACTIC-TOOL',
 'Aletheia':'CLEAN-NULL(corrected)','Coeus':'CLEAN-NULL','Eos':'CLEAN-NULL','Hermes':'CLEAN-NULL','Iris':'CLEAN-NULL',
}
def family(name, kind, operator):
    if name in CLUSTER: return 'autopsy:'+CLUSTER[name]
    if kind in ('healthcheck',): return 'infra:healthcheck'
    if name.startswith('MachineProbe'): return 'infra:machineprobe'
    if kind == 'operator': return 'operator'
    if kind == 'pipeline-stage': return 'pipeline-stage'
    if operator: return 'tool:'+operator
    return kind or 'unknown'

def source_locations(name):
    locs=[]
    d = p('agents', name.lower())
    if os.path.isdir(d): locs.append('agents/%s/'%name.lower())
    return locs

def intake_status(name):
    # already rigorously autopsied / partial / dossier-only / untouched / infra
    a = name in autopsy
    dd = has_dossier(name)
    if name.startswith('MachineProbe') or 'healthcheck' in (family(name,'','')):
        return 'infra_process_not_reasoning_agent'
    if a and dd: return 'autopsied_and_dossiered'
    if a: return 'autopsied'
    if dd: return 'dossier_only'
    return 'untouched'

rows=[]
for a in agents:
    name = a['name']; kind = a.get('kind'); op = a.get('operator')
    fam = family(name, kind, op)
    row = {
      'agent_id': name,
      'aliases': [],
      'source_locations': source_locations(name),
      'machine': a.get('machine'),
      'kind': kind,
      'operator': op,
      'role': a.get('role'),
      'historical_status': a.get('lifecycle') or a.get('status'),
      'autopsy_exists': name in autopsy,
      'autopsy_failure_class': autopsy.get(name),
      'dossier_exists': has_dossier(name),
      'disposition_2026_06_advisory': disp.get(name),  # None => NOT covered by the 43-subset
      'apparent_family': fam,
      'proposed_investigation_status': 'UNQUEUED',
      'notes': ''
    }
    rows.append(row)

# annotate the identity discrepancy: in registry but absent from the 43 disposition pass
for r in rows:
    if r['disposition_2026_06_advisory'] is None and not r['agent_id'].startswith('MachineProbe'):
        r['notes'] = 'in canonical registry (state.json) but ABSENT from the 2026-06 43-process disposition pass'
    if r['agent_id'].startswith('MachineProbe'):
        r['notes'] = 'infra probe; absent from the 2026-06 43-process disposition pass'

out = p('engine','necropolis','ROSTER.jsonl')
with open(out,'w',encoding='utf-8') as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False)+'\n')

# summary to stderr
autopsied = sum(1 for r in rows if r['autopsy_exists'])
dossiered = sum(1 for r in rows if r['dossier_exists'])
covered   = sum(1 for r in rows if r['disposition_2026_06_advisory'])
sys.stderr.write(f"ROSTER: {len(rows)} canonical agents | {autopsied} autopsied | {dossiered} dossiered | {covered} disposition-covered\n")
sys.stderr.write("Absent from 43-pass: " + ", ".join(r['agent_id'] for r in rows if not r['disposition_2026_06_advisory']) + "\n")
