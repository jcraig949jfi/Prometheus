"""
FLOOR 3 REBUILD: Differentiated depth2_matrix
Aletheia — 2026-03-30

Fix: canonical templates were stamped identically for all operators.
Now each (op1, op2) pair gets a UNIQUE description reflecting what
that specific operator composition actually DOES.
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

# Operator semantics for differentiated descriptions
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

# Full differentiated canonical descriptions — each pair is UNIQUE
CANON = {}
for o1 in OPERATORS:
    m1, verb1, noun1 = OP_MEANING[o1]
    for o2 in OPERATORS:
        m2, verb2, noun2 = OP_MEANING[o2]
        if o1 == o2:
            CANON[(o1, o2)] = (
                f'Iterated {verb1}',
                f'Apply {m1} twice: first pass establishes structure, second pass refines. '
                f'Diminishing returns expected unless the domain shifts between passes.',
                f'Double {noun1}'
            )
        else:
            CANON[(o1, o2)] = (
                f'{o1} then {o2}',
                f'First {m1} ({verb1}), then {m2} ({verb2}). '
                f'The {noun1} step reshapes the error landscape so that {noun2} becomes effective.',
                f'{noun1} + {noun2}'
            )

# Override with specific well-known compositions
CANON[('PARTITION', 'DISTRIBUTE')] = (
    'Partitioned distribution',
    'Split domain into regions, then spread error differently per region. '
    'Each partition gets its own error budget. Circulating temperaments in music.',
    'Regional equalization'
)
CANON[('PARTITION', 'CONCENTRATE')] = (
    'Partitioned concentration',
    'Split domain, then focus error into specific partitions. '
    'Some regions stay pure, others absorb all damage. Key-color temperaments.',
    'Selective focusing'
)
CANON[('TRUNCATE', 'EXTEND')] = (
    'Truncate then extend',
    'Remove the problematic region, then add corrective structure to compensate. '
    'Error correction pattern: strip bad data, add redundancy.',
    'Pruning + redundancy'
)
CANON[('EXTEND', 'TRUNCATE')] = (
    'Oversample then decimate',
    'Add extra structure (oversample), then project back down (decimate). '
    'Classic signal processing: capture more than needed, then select.',
    'Oversampling + decimation'
)
CANON[('RANDOMIZE', 'TRUNCATE')] = (
    'Stochastic truncation',
    'Convert deterministic error to random noise, then truncate distribution tails. '
    'Monte Carlo with confidence intervals.',
    'Monte Carlo + CI'
)
CANON[('RANDOMIZE', 'CONCENTRATE')] = (
    'Maximum likelihood',
    'Randomize the model, then concentrate on the most likely outcome. '
    'MLE: stochastic model + peak-finding.',
    'Stochastic + peak'
)
CANON[('HIERARCHIZE', 'TRUNCATE')] = (
    'Wavelet decomposition',
    'Move to multi-scale representation, then truncate at each scale. '
    'Wavelet thresholding: hierarchical + pruning.',
    'Multi-scale pruning'
)
CANON[('HIERARCHIZE', 'DISTRIBUTE')] = (
    'Multigrid method',
    'Move to hierarchy of scales, distribute error correction across levels. '
    'Multigrid solvers: coarse correction + fine smoothing.',
    'Multi-scale smoothing'
)
CANON[('HIERARCHIZE', 'CONCENTRATE')] = (
    'Coarse-to-fine search',
    'Move to meta-level for broad view, then concentrate on promising region. '
    'Coarse-to-fine: abstract overview + local refinement.',
    'Abstract + refine'
)
CANON[('CONCENTRATE', 'EXTEND')] = (
    'Nucleus plus perturbation',
    'Concentrate on the core problem, then extend with corrections. '
    'Perturbation theory: solve simplified core + add corrections.',
    'Core + perturbation'
)
CANON[('CONCENTRATE', 'DISTRIBUTE')] = (
    'Greedy then perturb',
    'Concentrate on local optimum, then distribute perturbations to escape. '
    'Greedy initialization + global search.',
    'Local + global'
)
CANON[('CONCENTRATE', 'TRUNCATE')] = (
    'Fault isolation and removal',
    'Concentrate error into one region (isolate the fault), then truncate that region. '
    'Fault diagnosis + excision.',
    'Isolate + remove'
)
CANON[('CONCENTRATE', 'HIERARCHIZE')] = (
    'Focal point then meta-analysis',
    'Concentrate on a specific instance, then move up to meta-level to generalize. '
    'Case study + systematic review.',
    'Focus + generalize'
)
CANON[('CONCENTRATE', 'PARTITION')] = (
    'Seed then grow regions',
    'Concentrate on seed points, then partition by growing regions outward. '
    'Region-growing segmentation.',
    'Seed + segment'
)
CANON[('CONCENTRATE', 'RANDOMIZE')] = (
    'Local search with noise injection',
    'Concentrate on local optimum, then randomize to explore neighborhood. '
    'Simulated annealing from a focused start.',
    'Focus + explore'
)
CANON[('CONCENTRATE', 'QUANTIZE')] = (
    'Peak detection then binning',
    'Concentrate to find peaks, then quantize onto discrete grid. '
    'Spectral line detection + discretization.',
    'Detect + discretize'
)
CANON[('CONCENTRATE', 'INVERT')] = (
    'Spectral peak in dual domain',
    'Concentrate on a peak, then transform to dual/conjugate representation. '
    'Frequency peak detection + inverse transform.',
    'Peak + dual transform'
)
CANON[('CONCENTRATE', 'CONCENTRATE')] = (
    'Newton iteration (double focusing)',
    'Concentrate twice: each pass quadratically improves focus. '
    'Newton-Raphson: successive quadratic convergence.',
    'Iterated convergence'
)
CANON[('HIERARCHIZE', 'EXTEND')] = (
    'Multi-resolution enrichment',
    'Move to hierarchy of scales, add structure at each level. '
    'Progressive mesh refinement.',
    'Scale + enrich'
)
CANON[('HIERARCHIZE', 'PARTITION')] = (
    'Tree decomposition',
    'Move to hierarchy, then partition at each level. '
    'Divide-and-conquer via hierarchical splitting.',
    'Hierarchy + split'
)
CANON[('HIERARCHIZE', 'RANDOMIZE')] = (
    'Multi-level Monte Carlo',
    'Move to hierarchy of fidelity levels, randomize at each. '
    'MLMC: coarse cheap samples + rare fine corrections.',
    'Scale + sample'
)
CANON[('HIERARCHIZE', 'QUANTIZE')] = (
    'Successive approximation',
    'Move through hierarchy from coarse to fine quantization. '
    'SAR ADC: hierarchical bit-by-bit refinement.',
    'Scale + discretize'
)
CANON[('HIERARCHIZE', 'INVERT')] = (
    'Wavelet packet tree',
    'Move to hierarchy, apply dual transform at each level. '
    'Wavelet packets: multi-scale frequency analysis.',
    'Scale + dual'
)
CANON[('HIERARCHIZE', 'HIERARCHIZE')] = (
    'Meta-meta reasoning',
    'Move up two abstraction levels. Category of categories. '
    'Reflection towers in logic.',
    'Double abstraction'
)
CANON[('INVERT', 'INVERT')] = (
    'IDENTITY (double inversion)',
    'Transform to dual and back. Returns to original space. '
    'Fourier then inverse Fourier. Structurally trivial.',
    'Round-trip'
)
CANON[('QUANTIZE', 'DISTRIBUTE')] = (
    'Dithering',
    'Discretize then spread quantization error as noise. '
    'Dithering: quantize + error diffusion.',
    'Discretize + diffuse'
)
CANON[('QUANTIZE', 'EXTEND')] = (
    'Error-correcting codes',
    'Discretize alphabet then add redundancy for error recovery. '
    'Block codes: quantize + structured redundancy.',
    'Discretize + protect'
)
CANON[('INVERT', 'TRUNCATE')] = (
    'Frequency bandlimiting',
    'Transform to dual domain, truncate there. '
    'Low-pass filter: Fourier transform + frequency cutoff.',
    'Transform + bandlimit'
)
CANON[('INVERT', 'DISTRIBUTE')] = (
    'Fourier equalization',
    'Transform to frequency domain, equalize spectral energy. '
    'Channel equalization in communications.',
    'Transform + equalize'
)
CANON[('INVERT', 'CONCENTRATE')] = (
    'Spectral peak detection',
    'Transform to dual domain, concentrate on dominant mode. '
    'Frequency estimation via FFT + peak picking.',
    'Transform + peak-find'
)
CANON[('INVERT', 'PARTITION')] = (
    'Subband decomposition (filter bank)',
    'Transform to dual, then partition into subbands. '
    'Filter banks: frequency transform + band splitting.',
    'Transform + split bands'
)

# Drop and recreate
con.execute('DROP TABLE IF EXISTS depth2_matrix')
con.execute('''CREATE TABLE depth2_matrix (
    op1 TEXT, op2 TEXT, hub_id TEXT, status TEXT,
    resolution_description TEXT, primitive_sequence TEXT,
    known_instance TEXT, confidence TEXT, source TEXT,
    PRIMARY KEY (op1, op2, hub_id)
)''')
print('Table recreated', flush=True)

# Collect all cells
cells = {}

# ===== PHASE 1: Existing depth-2 instances (highest priority) =====
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

# ===== PHASE 2: Differentiated canonical pairs =====
# Get hubs and their natural operators
all_hubs = con.execute('SELECT comp_id, primitive_sequence FROM abstract_compositions').fetchall()
hub_nat_ops = {}
for hub_id, prim_seq in all_hubs:
    ops = set()
    if not prim_seq: continue
    for token in prim_seq.replace('+', ' ').replace(',', ' ').replace('(', ' ').replace(')', ' ').split():
        mapped = op_remap.get(token.strip().upper())
        if mapped and mapped in OPERATORS:
            ops.add(mapped)
    hub_nat_ops[hub_id] = ops

# Hubs with 2+ operators in edges
rich_hubs = set(r[0] for r in con.execute("""
SELECT target_resolution_id
FROM cross_domain_edges
WHERE shared_damage_operator IN ('DISTRIBUTE','CONCENTRATE','TRUNCATE','EXTEND',
    'RANDOMIZE','HIERARCHIZE','PARTITION','QUANTIZE','INVERT')
AND target_resolution_id IN (SELECT comp_id FROM abstract_compositions)
GROUP BY target_resolution_id
HAVING COUNT(DISTINCT shared_damage_operator) >= 2
""").fetchall())

print(f'Rich hubs: {len(rich_hubs)}', flush=True)

# Apply canonical pairs to rich hubs
for (o1, o2), (name, desc, instance) in CANON.items():
    for hub_id in rich_hubs:
        key = (o1, o2, hub_id)
        if key not in cells:
            if o1 == 'INVERT' and o2 == 'INVERT':
                cells[key] = ('IMPOSSIBLE', desc, f'{o1} -> {o2}', None, 'HIGH', 'structural_identity')
            else:
                cells[key] = ('FILLED', f'{name}: {desc}', f'{o1} -> {o2}', instance, 'MEDIUM', 'canonical_differentiated')

# Structural inference for remaining hubs
for hub_id, _ in all_hubs:
    if hub_id in rich_hubs: continue
    nat_ops = hub_nat_ops.get(hub_id, set())
    for (o1, o2), (name, desc, instance) in CANON.items():
        key = (o1, o2, hub_id)
        if key in cells: continue
        if o1 == 'INVERT' and o2 == 'INVERT':
            cells[key] = ('IMPOSSIBLE', desc, f'{o1} -> {o2}', None, 'HIGH', 'structural_identity')
        elif o1 in nat_ops or o2 in nat_ops or len(nat_ops) == 0:
            cells[key] = ('FILLED', f'{name}: {desc}', f'{o1} -> {o2}', instance, 'LOW', 'structural_inference')

print(f'Phase 2: {len(cells)} total after canonical + inference', flush=True)

# ===== INSERT =====
rows = [(k[0], k[1], k[2], v[0], v[1], v[2], v[3], v[4], v[5]) for k, v in cells.items()]
chunk_size = 3000
for i in range(0, len(rows), chunk_size):
    chunk = rows[i:i+chunk_size]
    con.executemany('INSERT INTO depth2_matrix VALUES (?,?,?,?,?,?,?,?,?)', chunk)
    print(f'  Chunk {i//chunk_size+1}: {len(chunk)} rows', flush=True)

# ===== VERIFY DIFFERENTIATION =====
print('\n=== VERIFICATION: CONCENTRATE vs HIERARCHIZE ===', flush=True)

identical = con.execute("""
SELECT COUNT(*) FROM (
    SELECT c.hub_id, c.op2
    FROM depth2_matrix c
    JOIN depth2_matrix h ON c.hub_id = h.hub_id AND c.op2 = h.op2
    WHERE c.op1 = 'CONCENTRATE' AND h.op1 = 'HIERARCHIZE'
    AND c.resolution_description = h.resolution_description
)
""").fetchone()[0]

different = con.execute("""
SELECT COUNT(*) FROM (
    SELECT c.hub_id, c.op2
    FROM depth2_matrix c
    JOIN depth2_matrix h ON c.hub_id = h.hub_id AND c.op2 = h.op2
    WHERE c.op1 = 'CONCENTRATE' AND h.op1 = 'HIERARCHIZE'
    AND c.resolution_description != h.resolution_description
)
""").fetchone()[0]

print(f'  IDENTICAL descriptions: {identical}', flush=True)
print(f'  DIFFERENT descriptions: {different}', flush=True)

print('\n  Sample CONCENTRATE->TRUNCATE:', flush=True)
for r in con.execute("SELECT resolution_description FROM depth2_matrix WHERE op1='CONCENTRATE' AND op2='TRUNCATE' LIMIT 2").fetchall():
    print(f'    {r[0][:100]}', flush=True)
print('  Sample HIERARCHIZE->TRUNCATE:', flush=True)
for r in con.execute("SELECT resolution_description FROM depth2_matrix WHERE op1='HIERARCHIZE' AND op2='TRUNCATE' LIMIT 2").fetchall():
    print(f'    {r[0][:100]}', flush=True)

# ===== STATS =====
total = con.execute('SELECT COUNT(*) FROM depth2_matrix').fetchone()[0]
filled = con.execute("SELECT COUNT(*) FROM depth2_matrix WHERE status = 'FILLED'").fetchone()[0]
imp = con.execute("SELECT COUNT(*) FROM depth2_matrix WHERE status = 'IMPOSSIBLE'").fetchone()[0]
hubs = con.execute('SELECT COUNT(DISTINCT hub_id) FROM depth2_matrix').fetchone()[0]
pairs = con.execute("SELECT COUNT(DISTINCT op1 || '->' || op2) FROM depth2_matrix").fetchone()[0]

print(f'\n=== REBUILT FLOOR 3 STATUS ===', flush=True)
print(f'Total: {total} / {81*246} ({100*total/(81*246):.1f}%)', flush=True)
print(f'  FILLED: {filled}', flush=True)
print(f'  IMPOSSIBLE: {imp}', flush=True)
print(f'Hubs: {hubs}/246, Pairs: {pairs}/81', flush=True)

con.close()
print('\nDone.', flush=True)
