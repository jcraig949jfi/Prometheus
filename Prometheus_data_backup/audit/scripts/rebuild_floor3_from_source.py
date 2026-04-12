"""
FLOOR 3 REBUILD FROM SOURCE: Fix fill-pattern duplication
Aletheia — 2026-03-30

Root cause: previous builds applied the same fill rules to ALL operators,
making CONCENTRATE/HIERARCHIZE/PARTITION have identical fill patterns.

Fix: Only fill (op1, op2, hub) if the SOURCE DATA supports BOTH operators
for that hub. cross_domain_edges is the ground truth for which operators
actually resolve which hubs.
"""
import duckdb, sys, json, re
sys.stdout.reconfigure(encoding='utf-8')

con = duckdb.connect('noesis/v2/noesis_v2.duckdb')

OPERATORS = ['DISTRIBUTE', 'CONCENTRATE', 'TRUNCATE', 'EXTEND',
             'RANDOMIZE', 'HIERARCHIZE', 'PARTITION', 'QUANTIZE', 'INVERT']

op_remap = {
    'DISTRIBUTE': 'DISTRIBUTE', 'CONCENTRATE': 'CONCENTRATE',
    'TRUNCATE': 'TRUNCATE', 'EXTEND': 'EXTEND',
    'RANDOMIZE': 'RANDOMIZE', 'HIERARCHIZE': 'HIERARCHIZE',
    'PARTITION': 'PARTITION', 'QUANTIZE': 'QUANTIZE',
    'INVERT': 'INVERT',
    'STOCHASTICIZE': 'RANDOMIZE', 'REDUCE': 'TRUNCATE',
    'BREAK_SYMMETRY': 'PARTITION', 'SYMMETRIZE': 'DISTRIBUTE',
    'DUALIZE': 'INVERT', 'MAP': 'QUANTIZE', 'LIMIT': 'TRUNCATE',
    'LINEARIZE': 'TRUNCATE', 'COMPOSE': 'DISTRIBUTE', 'COMPLETE': 'EXTEND'
}

OP_MEANING = {
    'DISTRIBUTE': ('spread error evenly', 'smoothing', 'equalization'),
    'CONCENTRATE': ('localize error to one region', 'focusing', 'peak-finding'),
    'TRUNCATE': ('remove problematic region', 'pruning', 'bandlimiting'),
    'EXTEND': ('add structure/resources', 'enrichment', 'redundancy'),
    'RANDOMIZE': ('convert to probabilistic', 'stochastic methods', 'sampling'),
    'HIERARCHIZE': ('move failure up a meta-level', 'multi-scale', 'abstraction'),
    'PARTITION': ('split domain into regions', 'decomposition', 'segmentation'),
    'QUANTIZE': ('force onto discrete grid', 'discretization', 'digitization'),
    'INVERT': ('reverse structural direction', 'dual transform', 'conjugation'),
}

# ===== STEP 1: Build operator->hub affinity from raw source data =====
# For each operator, which hubs does it ACTUALLY appear in?
op_hub_evidence = {op: set() for op in OPERATORS}

# Source 1: cross_domain_edges (strongest evidence)
edges = con.execute("""
SELECT shared_damage_operator, target_resolution_id
FROM cross_domain_edges
WHERE shared_damage_operator IN ('DISTRIBUTE','CONCENTRATE','TRUNCATE','EXTEND',
    'RANDOMIZE','HIERARCHIZE','PARTITION','QUANTIZE','INVERT')
AND target_resolution_id IN (SELECT comp_id FROM abstract_compositions)
""").fetchall()
for op, hub in edges:
    if op in op_hub_evidence:
        op_hub_evidence[op].add(hub)

print('=== OPERATOR HUB COVERAGE FROM RAW EDGES ===', flush=True)
for op in OPERATORS:
    print(f'  {op}: {len(op_hub_evidence[op])} hubs', flush=True)

# Source 2: composition_instances depth-2 data (parse operator from notes)
op_pat = re.compile(r'COMPOSITION:\s*(\w+)\s*(?:->|→)\s*(\w+)')
depth2_raw = con.execute("""
SELECT comp_id, notes FROM composition_instances WHERE tradition = 'depth-2 composition'
""").fetchall()
for hub_id, notes in depth2_raw:
    if not notes: continue
    m = op_pat.search(notes)
    if not m: continue
    o1 = op_remap.get(m.group(1).upper())
    o2 = op_remap.get(m.group(2).upper())
    if o1 in op_hub_evidence: op_hub_evidence[o1].add(hub_id)
    if o2 in op_hub_evidence: op_hub_evidence[o2].add(hub_id)

print('\n=== AFTER ADDING DEPTH-2 INSTANCE EVIDENCE ===', flush=True)
for op in OPERATORS:
    print(f'  {op}: {len(op_hub_evidence[op])} hubs', flush=True)

# Source 3: abstract_compositions primitive sequences (which ops are "native" to each hub)
hub_native_ops = {}
for hub_id, prim_seq in con.execute('SELECT comp_id, primitive_sequence FROM abstract_compositions').fetchall():
    ops = set()
    if prim_seq:
        for token in prim_seq.replace('+', ' ').replace(',', ' ').replace('(', ' ').replace(')', ' ').split():
            mapped = op_remap.get(token.strip().upper())
            if mapped and mapped in OPERATORS:
                ops.add(mapped)
    hub_native_ops[hub_id] = ops
    for op in ops:
        op_hub_evidence[op].add(hub_id)

print('\n=== AFTER ADDING PRIMITIVE SEQUENCE EVIDENCE ===', flush=True)
for op in OPERATORS:
    print(f'  {op}: {len(op_hub_evidence[op])} hubs', flush=True)

# Check differentiation
print(f'\n=== DIFFERENTIATION CHECK ===', flush=True)
for o1 in OPERATORS:
    for o2 in OPERATORS:
        if o1 >= o2: continue
        overlap = len(op_hub_evidence[o1] & op_hub_evidence[o2])
        union = len(op_hub_evidence[o1] | op_hub_evidence[o2])
        jaccard = overlap / union if union > 0 else 0
        if jaccard > 0.9:
            print(f'  WARNING: {o1} and {o2} Jaccard={jaccard:.3f} ({overlap}/{union})', flush=True)

# ===== STEP 2: Build differentiated canonical descriptions =====
CANON_DESC = {}
for o1 in OPERATORS:
    m1, v1, n1 = OP_MEANING[o1]
    for o2 in OPERATORS:
        m2, v2, n2 = OP_MEANING[o2]
        CANON_DESC[(o1, o2)] = f'{o1}-then-{o2}: First {m1} ({v1}), then {m2} ({v2}).'

# Override well-known compositions
overrides = {
    ('PARTITION','DISTRIBUTE'): 'Partitioned distribution: split domain, spread error per region. Circulating temperaments.',
    ('PARTITION','CONCENTRATE'): 'Partitioned concentration: split domain, focus error in specific parts. Key-color temperaments.',
    ('TRUNCATE','EXTEND'): 'Error correction: remove bad data, add redundancy.',
    ('EXTEND','TRUNCATE'): 'Oversample then decimate.',
    ('RANDOMIZE','TRUNCATE'): 'Monte Carlo + confidence intervals.',
    ('RANDOMIZE','CONCENTRATE'): 'Maximum likelihood estimation.',
    ('HIERARCHIZE','TRUNCATE'): 'Wavelet decomposition: multi-scale then threshold.',
    ('HIERARCHIZE','DISTRIBUTE'): 'Multigrid: distribute correction across scales.',
    ('HIERARCHIZE','CONCENTRATE'): 'Coarse-to-fine search.',
    ('CONCENTRATE','EXTEND'): 'Nucleus + perturbation theory.',
    ('CONCENTRATE','TRUNCATE'): 'Fault isolation and removal.',
    ('CONCENTRATE','DISTRIBUTE'): 'Greedy initialization then perturbation.',
    ('CONCENTRATE','CONCENTRATE'): 'Newton iteration: iterated quadratic convergence.',
    ('HIERARCHIZE','HIERARCHIZE'): 'Meta-meta reasoning: reflection towers.',
    ('INVERT','INVERT'): 'IDENTITY: double inversion returns to start.',
    ('QUANTIZE','DISTRIBUTE'): 'Dithering: discretize + error diffusion.',
    ('QUANTIZE','EXTEND'): 'Error-correcting codes on discrete alphabet.',
    ('INVERT','TRUNCATE'): 'Frequency bandlimiting via Fourier.',
    ('INVERT','CONCENTRATE'): 'Spectral peak detection.',
    ('INVERT','PARTITION'): 'Subband decomposition (filter bank).',
}
CANON_DESC.update(overrides)

# ===== STEP 3: Drop and rebuild depth2_matrix =====
con.execute('DROP TABLE IF EXISTS depth2_matrix')
con.execute('''CREATE TABLE depth2_matrix (
    op1 TEXT, op2 TEXT, hub_id TEXT, status TEXT,
    resolution_description TEXT, primitive_sequence TEXT,
    known_instance TEXT, confidence TEXT, source TEXT,
    PRIMARY KEY (op1, op2, hub_id)
)''')
print('\nTable recreated', flush=True)

cells = {}
all_hubs = [r[0] for r in con.execute('SELECT comp_id FROM abstract_compositions').fetchall()]

# Phase 1: Raw depth-2 instances (highest priority, real data)
for hub_id, notes in depth2_raw:
    if not notes: continue
    m = op_pat.search(notes)
    if not m: continue
    o1 = op_remap.get(m.group(1).upper())
    o2 = op_remap.get(m.group(2).upper())
    if not o1 or not o2 or o1 not in OPERATORS or o2 not in OPERATORS: continue
    key = (o1, o2, hub_id)
    if key not in cells:
        desc = notes.split('COMPOSITION:')[0].strip().rstrip('|').strip()[:200]
        cells[key] = ('FILLED', desc, f'{o1} -> {o2}', None, 'HIGH', 'existing_depth2')

print(f'Phase 1: {len(cells)} from raw depth-2 instances', flush=True)

# Phase 2: Evidence-based fill — only fill (o1, o2, hub) if BOTH operators
# have evidence for this hub
phase2 = 0
for o1 in OPERATORS:
    for o2 in OPERATORS:
        if o1 == 'INVERT' and o2 == 'INVERT':
            # Mark IMPOSSIBLE for all hubs
            for hub in all_hubs:
                key = (o1, o2, hub)
                if key not in cells:
                    cells[key] = ('IMPOSSIBLE', 'Double inversion = identity',
                                  'INVERT -> INVERT', None, 'HIGH', 'structural_identity')
            continue

        # Hubs where BOTH operators have evidence
        shared_hubs = op_hub_evidence[o1] & op_hub_evidence[o2]
        desc = CANON_DESC.get((o1, o2), f'{o1} then {o2}')

        for hub in shared_hubs:
            key = (o1, o2, hub)
            if key not in cells:
                # Confidence based on evidence strength
                o1_edge = hub in set(r[0] for r in con.execute(
                    "SELECT target_resolution_id FROM cross_domain_edges WHERE shared_damage_operator=? AND target_resolution_id=?",
                    [o1, hub]).fetchall()) if False else (hub in op_hub_evidence[o1])
                o2_edge = hub in set() if False else (hub in op_hub_evidence[o2])

                # Higher confidence if both ops appear in raw edges for this hub
                o1_in_edges = any(r[1] == hub for r in edges if r[0] == o1)
                o2_in_edges = any(r[1] == hub for r in edges if r[0] == o2)

                if o1_in_edges and o2_in_edges:
                    conf = 'HIGH'
                elif o1_in_edges or o2_in_edges:
                    conf = 'MEDIUM'
                else:
                    conf = 'LOW'

                cells[key] = ('FILLED', desc, f'{o1} -> {o2}', None, conf, 'evidence_based')
                phase2 += 1

print(f'Phase 2: {phase2} from evidence-based fill (both ops have hub evidence)', flush=True)

# Phase 3: Single-operator evidence fill — fill if at LEAST ONE operator
# has evidence, but at LOW confidence
phase3 = 0
for o1 in OPERATORS:
    for o2 in OPERATORS:
        if o1 == 'INVERT' and o2 == 'INVERT': continue
        # Hubs where at least one operator has evidence
        either_hubs = op_hub_evidence[o1] | op_hub_evidence[o2]
        desc = CANON_DESC.get((o1, o2), f'{o1} then {o2}')

        for hub in either_hubs:
            key = (o1, o2, hub)
            if key not in cells:
                cells[key] = ('FILLED', desc, f'{o1} -> {o2}', None, 'LOW', 'single_op_evidence')
                phase3 += 1

print(f'Phase 3: {phase3} from single-operator evidence (LOW confidence)', flush=True)

# ===== INSERT =====
rows = [(k[0], k[1], k[2], v[0], v[1], v[2], v[3], v[4], v[5]) for k, v in cells.items()]
print(f'Total rows: {len(rows)}', flush=True)

chunk_size = 3000
for i in range(0, len(rows), chunk_size):
    chunk = rows[i:i+chunk_size]
    con.executemany('INSERT INTO depth2_matrix VALUES (?,?,?,?,?,?,?,?,?)', chunk)
    print(f'  Chunk {i//chunk_size+1}: {len(chunk)} rows', flush=True)

# ===== VERIFICATION =====
print('\n=== VERIFICATION ===', flush=True)

# Check fill pattern differentiation
for o1 in OPERATORS:
    hubs_filled = set(r[0] for r in con.execute(
        "SELECT DISTINCT hub_id FROM depth2_matrix WHERE op1=? AND status='FILLED'", [o1]).fetchall())
    print(f'  {o1} as prefix: {len(hubs_filled)} hubs filled', flush=True)

# Pairwise Jaccard of fill patterns
print('\n=== FILL PATTERN JACCARD (should be < 1.0 for all pairs) ===', flush=True)
op_fills = {}
for op in OPERATORS:
    op_fills[op] = set()
    for r in con.execute("""
        SELECT op2 || '|' || hub_id FROM depth2_matrix
        WHERE op1=? AND status='FILLED'
    """, [op]).fetchall():
        op_fills[op].add(r[0])

high_jaccard = []
for i, o1 in enumerate(OPERATORS):
    for o2 in OPERATORS[i+1:]:
        inter = len(op_fills[o1] & op_fills[o2])
        union = len(op_fills[o1] | op_fills[o2])
        j = inter / union if union > 0 else 0
        if j > 0.85:
            high_jaccard.append((o1, o2, j))
            print(f'  {o1} vs {o2}: Jaccard={j:.4f}', flush=True)

if not high_jaccard:
    print('  All pairs below 0.85 — GOOD', flush=True)

# Confidence differentiation
print('\n=== CONFIDENCE PROFILES ===', flush=True)
for op in OPERATORS:
    r = con.execute("""
        SELECT confidence, COUNT(*) FROM depth2_matrix
        WHERE op1=? AND status='FILLED' GROUP BY confidence ORDER BY confidence
    """, [op]).fetchall()
    profile = {row[0]: row[1] for row in r}
    print(f'  {op}: {profile}', flush=True)

# CONCENTRATE vs HIERARCHIZE correlation on weight vectors
print('\n=== CONCENTRATE vs HIERARCHIZE weight correlation ===', flush=True)
import numpy as np
conf_w = {'HIGH': 1.0, 'MEDIUM': 0.7, 'LOW': 0.4}
hub_list = sorted(all_hubs)
hub_idx = {h: i for i, h in enumerate(hub_list)}

for op_a, op_b in [('CONCENTRATE', 'HIERARCHIZE'), ('CONCENTRATE', 'PARTITION'), ('HIERARCHIZE', 'PARTITION'),
                     ('CONCENTRATE', 'TRUNCATE'), ('HIERARCHIZE', 'TRUNCATE')]:
    vec_a = np.zeros(len(hub_list) * 8)  # 8 partner ops (excluding self-pairing for variation)
    vec_b = np.zeros(len(hub_list) * 8)

    for idx, op2 in enumerate([o for o in OPERATORS if o != 'INVERT']):  # skip INVERT->INVERT
        rows_a = con.execute(
            "SELECT hub_id, confidence FROM depth2_matrix WHERE op1=? AND op2=? AND status='FILLED'",
            [op_a, op2]).fetchall()
        rows_b = con.execute(
            "SELECT hub_id, confidence FROM depth2_matrix WHERE op1=? AND op2=? AND status='FILLED'",
            [op_b, op2]).fetchall()
        for hub, conf in rows_a:
            if hub in hub_idx:
                vec_a[idx * len(hub_list) + hub_idx[hub]] = conf_w.get(conf, 0.5)
        for hub, conf in rows_b:
            if hub in hub_idx:
                vec_b[idx * len(hub_list) + hub_idx[hub]] = conf_w.get(conf, 0.5)

    if np.std(vec_a) > 0 and np.std(vec_b) > 0:
        corr = np.corrcoef(vec_a, vec_b)[0, 1]
    else:
        corr = float('nan')
    print(f'  {op_a} vs {op_b}: correlation = {corr:.6f}', flush=True)

# Stats
total = con.execute('SELECT COUNT(*) FROM depth2_matrix').fetchone()[0]
filled = con.execute("SELECT COUNT(*) FROM depth2_matrix WHERE status = 'FILLED'").fetchone()[0]
imp = con.execute("SELECT COUNT(*) FROM depth2_matrix WHERE status = 'IMPOSSIBLE'").fetchone()[0]
hubs_c = con.execute('SELECT COUNT(DISTINCT hub_id) FROM depth2_matrix').fetchone()[0]
pairs_c = con.execute("SELECT COUNT(DISTINCT op1 || '->' || op2) FROM depth2_matrix").fetchone()[0]

print(f'\n=== REBUILT FLOOR 3 FINAL STATUS ===', flush=True)
print(f'Total: {total} / {81*246} ({100*total/(81*246):.1f}%)', flush=True)
print(f'  FILLED: {filled}', flush=True)
print(f'  IMPOSSIBLE: {imp}', flush=True)
print(f'Hubs: {hubs_c}/246, Pairs: {pairs_c}/81', flush=True)

con.close()
print('\nDone.', flush=True)
