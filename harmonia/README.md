# Harmonia

**Tensor Train Exploration Engine for Cross-Domain Mathematical Structure Discovery**

Harmonia finds real structure across mathematical domains at tensor speed. It uses tensor train (TT) decomposition to explore combinatorial relationships between datasets — knots, curves, forms, fields, space groups, materials, L-functions — without materializing impossible full tensors. A falsification battery validates everything the tensor trains propose. A universal coordinate system (Mathematical Phonemes) provides the shared language.

Named for the Greek goddess of concordance between opposites. The engine finds where different mathematical worlds harmonize.

---

## Core Idea

Each mathematical domain is a **dimension** of a high-dimensional tensor. The full tensor is impossibly large (66K x 50K x 39K x 31K x 15K x ... = absurd), but tensor trains decompose it into a chain of small cores connected by bond dimensions.

**Bond dimension = strength of real cross-domain coupling.**

TT-Cross (adaptive cross approximation) builds the tensor train by sampling a black-box value function — never materializing the full tensor. The battery is the value function. Low rank survives. High rank gets killed. Fail early, fail fast, at tensor speeds.

---

## Architecture

```
Domain Indices          Phoneme Projector       TT-Cross Engine
+------------+         +-----------------+      +---+   +---+   +---+
| 14 domains |--feat-->| 5 universal     |---->| G |-r-| M |-r-| K |
| 287K objs  |         | phonemes:       |     |   | 01|   | 12|   |
+------------+         | complexity      |     +---+   +---+   +---+
                        | rank            |       |       |       |
  Battery (97 tests)    | symmetry        |     Bond dimensions ARE
  Dissection (34 strats)| arithmetic      |     the discovery.
                        | spectral        |
                        +-----------------+     Battery validates each
                              |                 component at tensor speed.
                              v                 Kills reduce bond dim.
                        Coupling Score          Truth = what survives.
```

---

## Mathematical Phonemes

Like the IPA (International Phonetic Alphabet) maps all speech sounds to articulatory features (place, manner, voicing), Harmonia maps all mathematical objects to 5 universal invariant coordinates:

| Phoneme | What it measures | Example mappings |
|---------|-----------------|------------------|
| **Complexity** | Size/conductor/discriminant | EC conductor, MF level, NF discriminant, lattice determinant |
| **Rank** | Dimension/richness | EC rank, NF degree, lattice dimension, polytope dimension |
| **Symmetry** | Automorphism/point group order | SG point group, lattice aut order, Maass symmetry type |
| **Arithmetic** | Torsion/class number/Selmer | EC torsion, NF class number, genus2 Selmer rank |
| **Spectral** | Eigenvalues/zeros/spectral data | Maass spectral parameter, material band gap, Dirichlet zeros |

### Phoneme Table

```
                COMPLEXITY  RANK  SYMMETRY  ARITHMETIC  SPECTRAL  TOTAL
elliptic_curves     1.0      1.8     -        1.0         -        3.8
modular_forms       1.0      0.8    1.2        -         0.9       3.9
dirichlet_zeros     1.0      1.9     -         -         1.6       4.5
number_fields       1.0      1.0     -        1.7        0.8       4.5
genus2              1.0      0.9    0.5       1.4         -        3.8
lattices            1.7      1.0    1.0       1.0         -        4.7
space_groups        0.5      0.6    1.0        -          -        2.1
polytopes           0.8      1.0    1.0        -          -        2.8
materials           1.3       -     0.8        -         1.0       3.1
knots               1.0       -      -        0.9        1.0       2.9
maass               1.0       -     0.8        -         1.7       3.5
battery             0.7       -      -         -         0.9       1.6
dissection          0.7      0.6     -         -          -        1.3
```

Cross-domain coupling appears when objects from different domains share phonemic profiles. The modularity theorem is literally: EC and MF share the **complexity** phoneme (conductor = level).

---

## Modules

### `src/domain_index.py` — Domain Loading

Maps 14 mathematical domains to integer indices with precomputed feature vectors.

| Domain | Objects | Features | Source |
|--------|---------|----------|--------|
| knots | 12,965 | 28 | KnotInfo (determinant, Alexander/Jones/Conway polynomials) |
| number_fields | 9,116 | 6 | LMFDB (degree, discriminant, class number, regulator) |
| space_groups | 230 | 5 | spglib+pymatgen (point group, crystal system, lattice type) |
| genus2 | 66,158 | 7 | LMFDB (conductor, Selmer rank, solvability, root number) |
| maass | 14,995 | 25 | LMFDB (level, weight, spectral parameter, 20 coefficients) |
| lattices | 39,293 | 6 | LMFDB (dimension, determinant, level, class number) |
| polytopes | 980 | 6 | Custom (dimension, vertices, edges, facets, f-vector) |
| materials | 10,000 | 6 | Materials Project (band gap, formation energy, density) |
| fungrim | 3,130 | 4 | Fungrim (type, symbols, module, formula length) |
| elliptic_curves | 31,073 | 4 | Charon DuckDB (conductor, rank, analytic rank, torsion) |
| modular_forms | 50,000 | 5 | Charon DuckDB (level, weight, dim, character order/parity) |
| dirichlet_zeros | 50,000 | 5 | Charon DuckDB (conductor, degree, rank, n_zeros, weight) |
| battery | 97 | 18 | Genocide rounds + battery logs (verdict, z-score, domain involvement) |
| dissection | 34 | 17 | Equation dissection strategies S1-S34 (priority, tractability, domain applicability) |

**Total: 287,940 objects across 14 domains.**

```python
from harmonia.src.domain_index import load_domains
domains = load_domains('knots', 'number_fields', 'space_groups')
```

### `src/coupling.py` — Coupling Scorers

Four coupling functions of increasing sophistication:

| Scorer | Method | Null-sensitive? | Best for |
|--------|--------|----------------|----------|
| `CouplingScorer` | Cosine similarity in random-projected shared space | No | Fast exploration |
| `DistributionalCoupling` | Cosine + M4/M2^2 kurtosis deviation | No | Distributional structure |
| `AlignmentCoupling` | Quantile-rank co-extremity with null-corrected interactions | Partial | Feature alignment |
| `PhonemeCoupling` | L2 distance in 5D universal phoneme space | Yes | Cross-domain inference |

### `src/phonemes.py` — Mathematical Phonemes

Universal coordinate system. Each domain maps to 5 phoneme axes via explicit, interpretable projections. No learned parameters.

```python
from harmonia.src.phonemes import phoneme_compatibility, print_phoneme_table

print_phoneme_table()
compat = phoneme_compatibility('modular_forms', 'elliptic_curves')
# -> 0.31 compatibility, shared: ['complexity', 'rank']
```

### `src/engine.py` — TT-Cross Engine

Core exploration engine. Runs tntorch's cross approximation over domain grids, extracts bond dimensions, reports structure.

```python
from harmonia.src.engine import HarmoniaEngine

engine = HarmoniaEngine(
    domains=['knots', 'number_fields', 'space_groups'],
    device='cpu',       # or 'cuda' for GPU
    max_rank=20,
    eps=1e-4,
    scorer='phoneme',   # or 'cosine', 'distributional', 'alignment'
    subsample=2000,     # None for full data
)

tt, report = engine.explore()
print(report.summary())
# Bond dimensions, singular values, wall time
```

### `src/validate.py` — Heuristic Validation

Extracts principal components from TT bonds and validates via energy thresholds and selectivity checks.

```python
from harmonia.src.validate import validate_bond
vr = validate_bond(tt, bond_idx=0, domains=engine._domain_list)
print(vr.summary())
# Raw rank -> Validated rank, per-component verdicts
```

### `src/tensor_falsify.py` — Tensor-Speed Falsification

Full battery tests implemented as TT operations. Each test is another TT-Cross call with modified data.

| Test | What it does | What kills it |
|------|-------------|--------------|
| **F1** Permutation null | Shuffle domain A's features, compare score variance + rank correlation | Score doesn't change under permutation |
| **F2** Subset stability | 3x 50% random splits, check rank consistency | CV > 0.5 across splits |
| **F3** Effect size | Cohen's d between top/bottom quartile objects | d < 0.5 avg or d < 0.2 on either side |
| **F8** Direction consistency | Deviation magnitude of top objects from population mean | Magnitude < 0.3 on either side |
| **F17** Confound residual | Remove top-variance feature, re-run TT-Cross | Rank drops to 0 |

Ensemble verdict: survive if F1 passes, OR (F2+F3 pass), OR 4+ tests pass.

```python
from harmonia.src.tensor_falsify import falsify_bond

report = falsify_bond('space_groups', 'elliptic_curves', subsample=2000)
print(report.summary())
# Per-test verdicts, surviving rank, wall time
```

### `src/sweep.py` — Parallel Sweep

Runs TT-Cross across all domain combinations in parallel via ThreadPoolExecutor.

```python
from harmonia.src.sweep import sweep_pairs
results = sweep_pairs(max_rank=15, subsample=2000, max_workers=8, device='cpu')
```

### `src/landscape.py` — MAP-Elites Explorer + Calibration

**Known-truth calibration:** Tests the tensor framework against 5 proven mathematical relationships and 3 known falsehoods. Measures sensitivity, specificity, accuracy.

**MAP-Elites landscape:** Randomly explores scorer x domain x resolution configurations. Builds a landscape of what structure exists where. Everything disposable.

```python
from harmonia.src.landscape import calibrate, run_landscape

metrics = calibrate(subsample=2000)
# Sensitivity: 100%, Specificity: 33%, Accuracy: 75%

summary = run_landscape(n_iterations=200, max_order=3)
# 127 unique cells, scorer comparison, domain heatmap
```

---

## Key Results

### Pairwise Bond Matrix (12 domains, 66 pairs, 8.7s)

```
              dirich ellipt fungri genus2 lattic materi modula number polyto space_
dirichlet_z     --     1      1      1     2      1      2      1      0     1
elliptic_c       1    --      1      1     1      2      1      1      1     2
genus2           1     1      1     --     0      0      0      1      0     1
lattices         2     1      1      0    --      1      1      1      1     1
materials        1     2      1      0     1     --      1      1      1     1
modular_f        2     1      1      0     1      1     --      1      1     2
number_f         1     1      1      1     1      1      1     --      1     1
polytopes        0     1      1      0     1      1      1      1     --     2
space_g          1     2      1      1     1      1      2      1      2    --
```

Knots and Maass decouple from everything (rank 0). Space groups is the hub.

### Deep Sweep (837 combos, layers 2-6, 8.2 min)

| Layer | Combos | Max Rank | Mean | All >= rank 3? |
|-------|--------|----------|------|----------------|
| 2 (pairs) | 45 | 2 | 1.0 | No (0/45) |
| 3 (triples) | 120 | 7 | 3.7 | 70% |
| 4 (quads) | 210 | 10 | 6.0 | **100%** |
| 5 (quintuples) | 252 | 10 | 7.2 | **100%** |
| 6 (sextuples) | 210 | 10 | 7.6 | **100%** |

Structure deepens monotonically with dimension. Every 4+ domain combination has rich structure.

### Meta-Tensor (battery + dissection as dimensions)

Adding the battery and dissection strategies as tensor dimensions reveals they are deeply entangled with the object domains:
- NF + genus2 + battery: rank 15
- genus2 + lattices + dissection: rank 14
- The analytical methods co-vary with the mathematical structure they measure

### Validated Cross-Domain Inferences

| Inference | Score | Verdict |
|-----------|-------|---------|
| SG <-> EC: high symmetry = high rank, high torsion | 5/5 | **Validated** |
| MF <-> Dirichlet: level = conductor (modularity theorem) | 4/5 | Probable |
| NF <-> Genus2: regulator predicts local solvability | 4/5 | Probable |
| Lattices <-> Dirichlet: level+class# = conductor | 3/5 | Possible |
| Materials <-> EC: band gap inversely tracks rank | 3/5 | Possible |

### Calibration (8 known truths/falsehoods, 8.0s)

| Metric | Value |
|--------|-------|
| **Sensitivity** | 100% (5/5 known truths detected) |
| **Specificity** | 33% (1/3 known falsehoods rejected) |
| **Accuracy** | 75% |

Remaining false positives share the "complexity" phoneme — objects that are complex in any domain look alike. Fixing this requires per-phoneme null models.

---

## Performance

| Operation | Scale | Time |
|-----------|-------|------|
| Load 14 domains (287K objects) | — | 3.5s |
| Pairwise sweep (66 pairs) | 10^10 grid points | 8.7s |
| Deep sweep (837 combos) | layers 2-6 | 8.2 min |
| Single falsification (5 tests) | per inference | 1.7s |
| MAP-Elites (200 explorations) | random configs | 134s |
| Full calibration (8 tests) | known truths/falsehoods | 8.0s |

All on CPU (ThreadPool parallelism). GPU available (RTX 5060 Ti 16GB) but CPU multiprocess is faster for this workload due to small TT-Cross batch sizes.

---

## Stack

- **tntorch** (v1.1.2): PyTorch tensor train library with TT-Cross support
- **PyTorch** (v2.11.0+cu128): GPU-ready, CUDA 12.8
- **Charon DuckDB**: 1.1GB database with EC, MF, Dirichlet zero data
- **Battery** (F1-F24b): Lives in `cartography/shared/scripts/battery_unified.py`

---

## Directory Structure

```
harmonia/
  README.md                     # This file
  configs/
    domains.yaml                # Domain definitions and exploration defaults
  src/
    __init__.py
    domain_index.py             # 14 domain loaders, 287K objects
    coupling.py                 # 4 coupling scorers (cosine, distributional, alignment, phoneme)
    phonemes.py                 # Mathematical Phonemes — universal 5D coordinate system
    engine.py                   # TT-Cross exploration engine
    validate.py                 # Heuristic bond validation
    tensor_falsify.py           # Tensor-speed battery (F1/F2/F3/F8/F17)
    sweep.py                    # Parallel sweep across domain combinations
    landscape.py                # MAP-Elites explorer + known-truth calibration
  data/                         # Precomputed feature caches (gitignored)
  results/                      # Exploration reports and sweep results
    calibration_phoneme.json    # Known-truth calibration metrics
    deep_sweep.json             # 837-combo deep sweep (layers 2-6)
    landscape.json              # MAP-Elites exploration landscape
    meta_sweep.json             # Battery + dissection as meta-dimensions
    sweep_12domains_pairs.json  # 66-pair pairwise sweep
    falsification_v2.json       # Tensor-speed falsification results
```

---

## Next Steps

1. **Per-phoneme null models** — Test each phoneme axis independently against permutation null. Kill couplings that only survive through the "complexity" phoneme (generic size correlation, not domain-specific structure).

2. **High-precision L-function zeros** — Load actual zero locations (120K objects, 79 zeros avg, 6-digit precision) as spectral features. This massively upgrades the "spectral" phoneme.

3. **Scorer ensemble** — Run all 4 scorers in parallel, require agreement. MAP-Elites showed alignment finds the most but cosine is most conservative. Their intersection is the truth.

4. **Landscape as training data** — 127 MAP-Elites cells with scorer x domain x rank outcomes. Train a meta-scorer that predicts which scorer works where.

5. **Random tensor exploration** — Generate thousands of random domain subsets, random feature projections, random phoneme weightings. Run TT-Cross + battery. Build a landscape of mathematical structure that's purely empirical, entirely disposable, and continuously self-calibrating.
