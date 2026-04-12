"""
FLOOR 3: Depth-2 Composition Matrix Builder
Aletheia — 2026-03-30
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

# Drop and recreate
con.execute('DROP TABLE IF EXISTS depth2_matrix')
con.execute('''CREATE TABLE depth2_matrix (
    op1 TEXT, op2 TEXT, hub_id TEXT, status TEXT,
    resolution_description TEXT, primitive_sequence TEXT,
    known_instance TEXT, confidence TEXT, source TEXT,
    PRIMARY KEY (op1, op2, hub_id)
)''')
print('Table created', flush=True)

# Collect all rows keyed by (op1,op2,hub) — first write wins
cells = {}

# ===== PHASE 1: Existing depth-2 compositions (highest priority) =====
depth2 = con.execute("""
SELECT comp_id, notes FROM composition_instances WHERE tradition = 'depth-2 composition'
""").fetchall()

op_pat = re.compile(r'COMPOSITION:\s*(\w+)\s*(?:->|→)\s*(\w+)')
for hub_id, notes in depth2:
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

print(f'Phase 1: {len(cells)} from existing depth-2 data', flush=True)

# ===== PHASE 2: Canonical pairs x ALL hubs with any Floor 1 data =====
# Lower threshold: any hub with at least 2 distinct operators in edges
hub_ops = con.execute("""
SELECT target_resolution_id, COUNT(DISTINCT shared_damage_operator) as cnt
FROM cross_domain_edges
WHERE shared_damage_operator IN ('DISTRIBUTE','CONCENTRATE','TRUNCATE','EXTEND',
    'RANDOMIZE','HIERARCHIZE','PARTITION','QUANTIZE','INVERT')
AND target_resolution_id IN (SELECT comp_id FROM abstract_compositions)
GROUP BY target_resolution_id HAVING cnt >= 2
""").fetchall()
rich_hubs = [r[0] for r in hub_ops]
print(f'Hubs with 2+ Floor 1 operators: {len(rich_hubs)}', flush=True)

# All canonical pair descriptions
CANON = {
    ('PARTITION','DISTRIBUTE'): 'Partitioned distribution: split domain, spread error per part',
    ('PARTITION','CONCENTRATE'): 'Partitioned concentration: split domain, focus error per part',
    ('PARTITION','TRUNCATE'): 'Partitioned truncation: split domain, trim within each',
    ('PARTITION','RANDOMIZE'): 'Stratified sampling: partition then randomize within',
    ('PARTITION','EXTEND'): 'Domain decomposition with padding',
    ('PARTITION','HIERARCHIZE'): 'Nested decomposition',
    ('PARTITION','QUANTIZE'): 'Adaptive quantization per region',
    ('PARTITION','INVERT'): 'Local dual transform per region',
    ('PARTITION','PARTITION'): 'Recursive partitioning (quadtree)',
    ('TRUNCATE','EXTEND'): 'Error correction: remove bad, add redundancy',
    ('TRUNCATE','DISTRIBUTE'): 'Window then uniform weight',
    ('TRUNCATE','CONCENTRATE'): 'Trim extremes, focus core',
    ('TRUNCATE','TRUNCATE'): 'Iterative pruning',
    ('TRUNCATE','RANDOMIZE'): 'Restricted Monte Carlo',
    ('TRUNCATE','PARTITION'): 'Reduce domain then decompose',
    ('TRUNCATE','HIERARCHIZE'): 'Simplify then level-shift',
    ('TRUNCATE','QUANTIZE'): 'Clip then discretize',
    ('TRUNCATE','INVERT'): 'Windowed Fourier transform',
    ('EXTEND','TRUNCATE'): 'Oversample then decimate',
    ('EXTEND','DISTRIBUTE'): 'Add redundancy + load balance',
    ('EXTEND','CONCENTRATE'): 'Embed + convex optimize',
    ('EXTEND','PARTITION'): 'Augmented space decomposition',
    ('EXTEND','EXTEND'): 'Multi-round error correction',
    ('EXTEND','RANDOMIZE'): 'Expanded space Monte Carlo',
    ('EXTEND','HIERARCHIZE'): 'Progressive multi-scale',
    ('EXTEND','QUANTIZE'): 'Oversampled quantization',
    ('EXTEND','INVERT'): 'Augmented Fourier analysis',
    ('DISTRIBUTE','CONCENTRATE'): 'Simulated annealing: explore then converge',
    ('DISTRIBUTE','TRUNCATE'): 'Regularize then sparsify',
    ('DISTRIBUTE','PARTITION'): 'Uniform init then cluster',
    ('DISTRIBUTE','EXTEND'): 'Smooth then refine',
    ('DISTRIBUTE','RANDOMIZE'): 'Entropy maximization',
    ('DISTRIBUTE','HIERARCHIZE'): 'Multi-scale smoothing',
    ('DISTRIBUTE','QUANTIZE'): 'Dithered quantization',
    ('DISTRIBUTE','INVERT'): 'Equalized dual domain',
    ('DISTRIBUTE','DISTRIBUTE'): 'Iterated Laplacian smoothing',
    ('CONCENTRATE','DISTRIBUTE'): 'Greedy init then perturb',
    ('CONCENTRATE','TRUNCATE'): 'Fault isolation + removal',
    ('CONCENTRATE','EXTEND'): 'Nucleus + perturbation theory',
    ('CONCENTRATE','PARTITION'): 'Seed + region growing',
    ('CONCENTRATE','RANDOMIZE'): 'Local search + noise injection',
    ('CONCENTRATE','HIERARCHIZE'): 'Focal point + meta-analysis',
    ('CONCENTRATE','QUANTIZE'): 'Peak detection + binning',
    ('CONCENTRATE','INVERT'): 'Spectral peak in dual domain',
    ('CONCENTRATE','CONCENTRATE'): 'Newton iteration (double focus)',
    ('RANDOMIZE','TRUNCATE'): 'Monte Carlo + confidence intervals',
    ('RANDOMIZE','CONCENTRATE'): 'Maximum likelihood estimation',
    ('RANDOMIZE','DISTRIBUTE'): 'Noise injection + averaging',
    ('RANDOMIZE','PARTITION'): 'Random hashing / stochastic load balance',
    ('RANDOMIZE','EXTEND'): 'Random feature expansion',
    ('RANDOMIZE','HIERARCHIZE'): 'Multi-level Monte Carlo',
    ('RANDOMIZE','QUANTIZE'): 'Stochastic rounding',
    ('RANDOMIZE','INVERT'): 'Random projection',
    ('RANDOMIZE','RANDOMIZE'): 'Re-randomization (CLT convergence)',
    ('HIERARCHIZE','TRUNCATE'): 'Wavelet: level-shift then truncate',
    ('HIERARCHIZE','DISTRIBUTE'): 'Multigrid: level-shift then spread',
    ('HIERARCHIZE','CONCENTRATE'): 'Coarse-to-fine search',
    ('HIERARCHIZE','PARTITION'): 'Tree decomposition',
    ('HIERARCHIZE','EXTEND'): 'Multi-resolution enrichment',
    ('HIERARCHIZE','RANDOMIZE'): 'Multi-level Monte Carlo',
    ('HIERARCHIZE','QUANTIZE'): 'Successive approximation ADC',
    ('HIERARCHIZE','INVERT'): 'Multi-scale Fourier / wavelet packet',
    ('HIERARCHIZE','HIERARCHIZE'): 'Meta-meta: category of categories',
    ('QUANTIZE','DISTRIBUTE'): 'Dithering: discretize + spread error',
    ('QUANTIZE','CONCENTRATE'): 'Lattice nearest-neighbor decode',
    ('QUANTIZE','TRUNCATE'): 'Bit-depth reduction',
    ('QUANTIZE','EXTEND'): 'Error-correcting codes on discrete alphabet',
    ('QUANTIZE','PARTITION'): 'Block coding',
    ('QUANTIZE','RANDOMIZE'): 'Randomized rounding',
    ('QUANTIZE','HIERARCHIZE'): 'Successive approximation',
    ('QUANTIZE','INVERT'): 'DFT on discrete lattice',
    ('QUANTIZE','QUANTIZE'): 'Re-quantization / resampling',
    ('INVERT','DISTRIBUTE'): 'Fourier equalization',
    ('INVERT','CONCENTRATE'): 'Spectral peak detection',
    ('INVERT','TRUNCATE'): 'Frequency bandlimiting',
    ('INVERT','EXTEND'): 'Fourier zero-padding',
    ('INVERT','PARTITION'): 'Subband decomposition (filter bank)',
    ('INVERT','RANDOMIZE'): 'Random spectral sampling',
    ('INVERT','HIERARCHIZE'): 'Wavelet packet tree',
    ('INVERT','QUANTIZE'): 'Spectral quantization',
    ('INVERT','INVERT'): 'IDENTITY: double inversion returns to start',
}
assert len(CANON) == 81

before = len(cells)
for (o1, o2), desc in CANON.items():
    for hub in rich_hubs:
        key = (o1, o2, hub)
        if key not in cells:
            cells[key] = ('FILLED', desc, f'{o1} -> {o2}',
                         desc.split(':')[0] if ':' in desc else None,
                         'MEDIUM', 'canonical_pair')
# Also for ALL hubs, mark INVERT->INVERT as IMPOSSIBLE
all_hubs = [r[0] for r in con.execute('SELECT comp_id FROM abstract_compositions').fetchall()]
for hub in all_hubs:
    key = ('INVERT', 'INVERT', hub)
    cells[key] = ('IMPOSSIBLE', 'Double inversion = identity', 'INVERT -> INVERT',
                  None, 'HIGH', 'structural_identity')

print(f'Phase 2: +{len(cells)-before} from canonical pairs x {len(rich_hubs)} hubs', flush=True)

# ===== PHASE 3: Expand to ALL hubs using structural inference =====
# For each hub, determine which operators it naturally supports from its primitive_sequence
hub_natural_ops = {}
for hub_id, prim_seq, _ in con.execute('SELECT comp_id, primitive_sequence, description FROM abstract_compositions').fetchall():
    ops = set()
    if not prim_seq: continue
    for token in prim_seq.replace('+', ' ').replace(',', ' ').replace('(', ' ').replace(')', ' ').split():
        token = token.strip().upper()
        mapped = op_remap.get(token)
        if mapped and mapped in OPERATORS:
            ops.add(mapped)
    hub_natural_ops[hub_id] = ops

# For hubs not yet covered by rich_hubs, generate pairs from their natural operators
extra = 0
for hub in all_hubs:
    if hub in rich_hubs: continue  # already covered
    nat_ops = hub_natural_ops.get(hub, set())
    if len(nat_ops) < 1: continue
    # Generate pairs where at least one operator is natural to this hub
    for (o1, o2), desc in CANON.items():
        if o1 in nat_ops or o2 in nat_ops:
            key = (o1, o2, hub)
            if key not in cells:
                cells[key] = ('FILLED', desc, f'{o1} -> {o2}', None, 'LOW', 'structural_inference')
                extra += 1

print(f'Phase 3: +{extra} from structural inference on remaining hubs', flush=True)

# ===== INSERT ALL =====
rows = [(k[0], k[1], k[2], v[0], v[1], v[2], v[3], v[4], v[5]) for k, v in cells.items()]
print(f'Total cells to insert: {len(rows)}', flush=True)

# Insert in chunks to avoid memory issues
chunk_size = 5000
for i in range(0, len(rows), chunk_size):
    chunk = rows[i:i+chunk_size]
    con.executemany('INSERT INTO depth2_matrix VALUES (?,?,?,?,?,?,?,?,?)', chunk)
    print(f'  Inserted chunk {i//chunk_size + 1}: {len(chunk)} rows', flush=True)

# ===== STATS =====
total = con.execute('SELECT COUNT(*) FROM depth2_matrix').fetchone()[0]
filled = con.execute("SELECT COUNT(*) FROM depth2_matrix WHERE status = 'FILLED'").fetchone()[0]
imp = con.execute("SELECT COUNT(*) FROM depth2_matrix WHERE status = 'IMPOSSIBLE'").fetchone()[0]

total_possible = 81 * 246
print(f'\n=== FLOOR 3 STATUS ===', flush=True)
print(f'Total cells: {total} / {total_possible} ({100*total/total_possible:.1f}%)', flush=True)
print(f'  FILLED: {filled}', flush=True)
print(f'  IMPOSSIBLE: {imp}', flush=True)
print(f'  EMPTY: {total_possible - total}', flush=True)

hubs_covered = con.execute('SELECT COUNT(DISTINCT hub_id) FROM depth2_matrix').fetchone()[0]
pairs_covered = con.execute("SELECT COUNT(DISTINCT op1 || '->' || op2) FROM depth2_matrix").fetchone()[0]
print(f'Hubs with data: {hubs_covered}/246', flush=True)
print(f'Op pairs with data: {pairs_covered}/81', flush=True)

print(f'\n=== TOP 15 HUBS ===', flush=True)
for r in con.execute("""
SELECT hub_id, SUM(CASE WHEN status='FILLED' THEN 1 ELSE 0 END) as f, COUNT(*) as t
FROM depth2_matrix GROUP BY hub_id ORDER BY f DESC LIMIT 15
""").fetchall():
    print(f'  {r[0]}: {r[1]}F / {r[2]}T of 81', flush=True)

print(f'\n=== OPERATOR PAIR FILL (top 20) ===', flush=True)
for r in con.execute("""
SELECT op1 || '->' || op2 as pair,
    SUM(CASE WHEN status='FILLED' THEN 1 ELSE 0 END) as f, COUNT(*) as t
FROM depth2_matrix GROUP BY pair ORDER BY f DESC LIMIT 20
""").fetchall():
    print(f'  {r[0]}: {r[1]}F / {r[2]}T of 246', flush=True)

con.close()
print('\nDone.', flush=True)
