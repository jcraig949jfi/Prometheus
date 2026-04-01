"""Fill remaining Floor 3 cells that were lost in partial insert"""
import duckdb, sys, json
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

CANON = {
    ('PARTITION','DISTRIBUTE'): 'Partitioned distribution',
    ('PARTITION','CONCENTRATE'): 'Partitioned concentration',
    ('PARTITION','TRUNCATE'): 'Partitioned truncation',
    ('PARTITION','RANDOMIZE'): 'Stratified sampling',
    ('PARTITION','EXTEND'): 'Domain decomposition with padding',
    ('PARTITION','HIERARCHIZE'): 'Nested decomposition',
    ('PARTITION','QUANTIZE'): 'Adaptive quantization',
    ('PARTITION','INVERT'): 'Local dual transform',
    ('PARTITION','PARTITION'): 'Recursive partitioning',
    ('TRUNCATE','EXTEND'): 'Error correction after pruning',
    ('TRUNCATE','DISTRIBUTE'): 'Window + uniform weight',
    ('TRUNCATE','CONCENTRATE'): 'Trim extremes focus core',
    ('TRUNCATE','TRUNCATE'): 'Iterative pruning',
    ('TRUNCATE','RANDOMIZE'): 'Restricted Monte Carlo',
    ('TRUNCATE','PARTITION'): 'Reduced domain decomposition',
    ('TRUNCATE','HIERARCHIZE'): 'Simplify then level-shift',
    ('TRUNCATE','QUANTIZE'): 'Clip then discretize',
    ('TRUNCATE','INVERT'): 'Windowed Fourier',
    ('EXTEND','TRUNCATE'): 'Oversample then decimate',
    ('EXTEND','DISTRIBUTE'): 'Redundancy + load balance',
    ('EXTEND','CONCENTRATE'): 'Embed + convex optimize',
    ('EXTEND','PARTITION'): 'Augmented space decomposition',
    ('EXTEND','EXTEND'): 'Multi-round error correction',
    ('EXTEND','RANDOMIZE'): 'Expanded space Monte Carlo',
    ('EXTEND','HIERARCHIZE'): 'Progressive multi-scale',
    ('EXTEND','QUANTIZE'): 'Oversampled quantization',
    ('EXTEND','INVERT'): 'Augmented Fourier',
    ('DISTRIBUTE','CONCENTRATE'): 'Simulated annealing',
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
    ('CONCENTRATE','EXTEND'): 'Nucleus + perturbation',
    ('CONCENTRATE','PARTITION'): 'Seed + region growing',
    ('CONCENTRATE','RANDOMIZE'): 'Local search + noise',
    ('CONCENTRATE','HIERARCHIZE'): 'Focal point + meta-analysis',
    ('CONCENTRATE','QUANTIZE'): 'Peak detection + binning',
    ('CONCENTRATE','INVERT'): 'Spectral peak dual',
    ('CONCENTRATE','CONCENTRATE'): 'Newton iteration',
    ('RANDOMIZE','TRUNCATE'): 'Monte Carlo + CI',
    ('RANDOMIZE','CONCENTRATE'): 'Maximum likelihood',
    ('RANDOMIZE','DISTRIBUTE'): 'Noise inject + average',
    ('RANDOMIZE','PARTITION'): 'Random hashing',
    ('RANDOMIZE','EXTEND'): 'Random feature expansion',
    ('RANDOMIZE','HIERARCHIZE'): 'Multi-level Monte Carlo',
    ('RANDOMIZE','QUANTIZE'): 'Stochastic rounding',
    ('RANDOMIZE','INVERT'): 'Random projection',
    ('RANDOMIZE','RANDOMIZE'): 'Re-randomization',
    ('HIERARCHIZE','TRUNCATE'): 'Wavelet decomposition',
    ('HIERARCHIZE','DISTRIBUTE'): 'Multigrid',
    ('HIERARCHIZE','CONCENTRATE'): 'Coarse-to-fine search',
    ('HIERARCHIZE','PARTITION'): 'Tree decomposition',
    ('HIERARCHIZE','EXTEND'): 'Multi-resolution enrichment',
    ('HIERARCHIZE','RANDOMIZE'): 'Multi-level Monte Carlo',
    ('HIERARCHIZE','QUANTIZE'): 'Successive approximation',
    ('HIERARCHIZE','INVERT'): 'Wavelet packet tree',
    ('HIERARCHIZE','HIERARCHIZE'): 'Meta-meta reasoning',
    ('QUANTIZE','DISTRIBUTE'): 'Dithering',
    ('QUANTIZE','CONCENTRATE'): 'Lattice decode',
    ('QUANTIZE','TRUNCATE'): 'Bit-depth reduction',
    ('QUANTIZE','EXTEND'): 'Error-correcting codes',
    ('QUANTIZE','PARTITION'): 'Block coding',
    ('QUANTIZE','RANDOMIZE'): 'Randomized rounding',
    ('QUANTIZE','HIERARCHIZE'): 'Successive approx',
    ('QUANTIZE','INVERT'): 'DFT on lattice',
    ('QUANTIZE','QUANTIZE'): 'Resampling',
    ('INVERT','DISTRIBUTE'): 'Fourier equalization',
    ('INVERT','CONCENTRATE'): 'Spectral peak detect',
    ('INVERT','TRUNCATE'): 'Frequency bandlimit',
    ('INVERT','EXTEND'): 'Fourier zero-padding',
    ('INVERT','PARTITION'): 'Subband decomposition',
    ('INVERT','RANDOMIZE'): 'Random spectral sampling',
    ('INVERT','HIERARCHIZE'): 'Wavelet packet',
    ('INVERT','QUANTIZE'): 'Spectral quantization',
    ('INVERT','INVERT'): 'IDENTITY',
}

# Get existing cells to avoid conflicts
existing = set()
for r in con.execute('SELECT op1, op2, hub_id FROM depth2_matrix').fetchall():
    existing.add((r[0], r[1], r[2]))
print(f'Existing cells: {len(existing)}', flush=True)

# Get hub natural operators from primitive sequences
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

# Generate missing cells
new_rows = []
for hub_id, _ in all_hubs:
    nat_ops = hub_nat_ops.get(hub_id, set())
    for (o1, o2), desc in CANON.items():
        if (o1, o2, hub_id) in existing:
            continue
        if o1 == 'INVERT' and o2 == 'INVERT':
            continue  # already marked impossible
        # Include if at least one op is natural, or if hub has no ops (include anyway at LOW conf)
        if o1 in nat_ops or o2 in nat_ops or len(nat_ops) == 0:
            new_rows.append((o1, o2, hub_id, 'FILLED', desc,
                           f'{o1} -> {o2}', None, 'LOW', 'structural_fill'))

print(f'New cells to insert: {len(new_rows)}', flush=True)

# Insert in chunks
chunk_size = 2000
for i in range(0, len(new_rows), chunk_size):
    chunk = new_rows[i:i+chunk_size]
    con.executemany('INSERT OR IGNORE INTO depth2_matrix VALUES (?,?,?,?,?,?,?,?,?)', chunk)
    print(f'  Chunk {i//chunk_size+1}: {len(chunk)} rows', flush=True)

# Stats
total = con.execute('SELECT COUNT(*) FROM depth2_matrix').fetchone()[0]
filled = con.execute("SELECT COUNT(*) FROM depth2_matrix WHERE status = 'FILLED'").fetchone()[0]
imp = con.execute("SELECT COUNT(*) FROM depth2_matrix WHERE status = 'IMPOSSIBLE'").fetchone()[0]
hubs = con.execute('SELECT COUNT(DISTINCT hub_id) FROM depth2_matrix').fetchone()[0]
pairs = con.execute("SELECT COUNT(DISTINCT op1 || '->' || op2) FROM depth2_matrix").fetchone()[0]

print(f'\n=== FLOOR 3 FINAL STATUS ===', flush=True)
print(f'Total: {total} / {81*246} ({100*total/(81*246):.1f}%)', flush=True)
print(f'  FILLED: {filled}', flush=True)
print(f'  IMPOSSIBLE: {imp}', flush=True)
print(f'  EMPTY: {81*246 - total}', flush=True)
print(f'Hubs: {hubs}/246, Pairs: {pairs}/81', flush=True)

con.close()
print('Done.', flush=True)
