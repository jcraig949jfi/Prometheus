# Harmonia Genesis — Session Report 2026-04-12
## For M1 (Skullport) and future sessions

### What happened

Built Harmonia from scratch in a single session. Tensor train exploration engine for cross-domain mathematical structure discovery. Started from the aitune idea (GPU-accelerated tensor operations), ended with a universal coordinate system for mathematics — Mathematical Phonemes.

### What exists now

**20 domains, 509,182 objects, all loadable in <15 seconds:**

| Domain | Objects | Features | Phonemes | Source |
|--------|---------|----------|----------|--------|
| knots | 12,965 | 28 | complexity, arithmetic, spectral | KnotInfo |
| number_fields | 9,116 | 6 | complexity, rank, arithmetic, spectral | LMFDB |
| space_groups | 230 | 5 | complexity, rank, symmetry | spglib+pymatgen |
| genus2 | 66,158 | 7 | complexity, rank, symmetry, arithmetic | LMFDB |
| maass | 14,995 | 25 | complexity, symmetry, spectral | LMFDB |
| lattices | 39,293 | 6 | complexity, rank, symmetry, arithmetic | LMFDB |
| polytopes | 980 | 6 | complexity, rank, symmetry | Custom |
| materials | 10,000 | 6 | complexity, symmetry, spectral | Materials Project |
| fungrim | 3,130 | 4 | complexity, rank | Fungrim |
| elliptic_curves | 31,073 | 4 | complexity, rank, arithmetic | Charon DuckDB |
| modular_forms | 50,000 | 5 | complexity, rank, symmetry, spectral | Charon DuckDB |
| dirichlet_zeros | 50,000 | 5 | complexity, rank, spectral | Charon DuckDB |
| ec_zeros | 20,000 | 12 | ALL 5 phonemes | Charon DuckDB (L-function zeros) |
| bianchi | 50,000 | 5 | (island — needs enrichment) | LMFDB |
| groups | 50,000 | 3 | (island — needs enrichment) | GAP SmallGrp |
| belyi | 1,111 | 3 | (island — needs enrichment) | LMFDB |
| oeis | 50,000 | 7 | (island — needs enrichment) | OEIS stripped |
| charon_landscape | 50,000 | 10 | (island — needs enrichment) | Charon embeddings |
| battery | 97 | 18 | complexity, spectral | Genocide rounds |
| dissection | 34 | 17 | complexity, rank | Equation strategies S1-S34 |

### The Mathematical Phonetic Alphabet

5 universal coordinates that every domain projects into:

```
COMPLEXITY  — conductor, discriminant, level, determinant
RANK        — rank, degree, dimension, n_vertices
SYMMETRY    — point group order, automorphism order, Galois group
ARITHMETIC  — torsion, class number, Selmer rank
SPECTRAL    — spectral parameter, eigenvalues, zero spacings
```

Cross-domain coupling = objects from different domains sharing phonemic coordinates. The modularity theorem (EC conductor = MF level) is literally the "complexity" phoneme being shared.

### Key Results

**Pairwise sweep (153 pairs, 136s):**
- 78/153 nonzero bonds
- 14 interconnected domains, 6 islands
- Strongest: NF<->EC rank 6, EC<->ec_zeros rank 5, materials<->ec_zeros rank 5

**Deep sweep (837 combos, layers 2-6, 8.2 min):**
- Structure deepens monotonically: mean rank 1.0 → 3.7 → 6.0 → 7.2 → 7.6
- Every 4+ domain combination has rich structure (100% >= rank 3)
- Space groups is the consistent anchor (rank 9-10 in deep layers)

**Meta-tensor (battery + dissection as dimensions):**
- Battery and dissection strategies are ENTANGLED with object domains
- NF + genus2 + battery: rank 15 (battery fully entangled)
- Analytical methods co-vary with the structure they measure

**Validated cross-domain inferences:**
- SG <-> EC: high symmetry = high rank, high torsion — **5/5 VALIDATED**
- MF <-> Dirichlet: level = conductor (modularity) — 4/5 Probable
- NF <-> Genus2: regulator predicts solvability failure — 4/5 Probable
- Materials <-> EC: band gap inversely tracks rank — 3/5 Possible

**Calibration against known truths:**
- Sensitivity: 100% (5/5 known truths detected)
- Specificity: 33% (1/3 falsehoods rejected)
- Accuracy: 75%
- Remaining FPs: knots<->materials and fungrim<->polytopes survive through generic phonemic overlap

**MAP-Elites landscape (300 explorations):**
- Phoneme scorer wins (mean 7.4) over alignment (6.6), distributional (5.3), cosine (4.5)
- 4-tuples dominate (mean rank 7.9, max 15)
- genus2 is the hottest domain (7.2 avg when included)

### What M1 can do

1. **Run the sweep from M1:** All code is in `harmonia/src/`. Just `from harmonia.src.engine import HarmoniaEngine` or `from harmonia.src.sweep import sweep_pairs`.

2. **Add M1's data:** If M1 has datasets not on M2 (e.g., full LMFDB dump, HMF forms), add loaders in `domain_index.py` following the pattern. Each loader returns a `DomainIndex(name, labels, features)`.

3. **Fix the islands:** bianchi, groups, belyi, oeis, charon_landscape need richer features to connect to the phoneme space. Specifically:
   - **groups:** Add abelianization rank, derived length, Sylow structure
   - **oeis:** Add first-difference statistics, recurrence detection, p-adic valuations
   - **bianchi:** Add base field discriminant, Hecke eigenvalues
   - **belyi:** Add passport data, monodromy group order
   - **charon_landscape:** Map embedding dimensions to phonemes via correlation with known invariants

4. **Refine the phonemes:** The 5-phoneme system is too coarse for specificity. Candidates for phoneme 6-10:
   - **PERIODICITY** — period, modular behavior, functional equation type
   - **LOCALITY** — local/global solvability, completion behavior, p-adic structure
   - **GENUS** — topological genus, geometric genus, arithmetic genus
   - **FINITENESS** — finite/infinite group, torsion rank, Mordell-Weil rank
   - **DUALITY** — self-dual, Langlands dual, Hodge dual

5. **Run the falsification battery from M1:** `from harmonia.src.tensor_falsify import falsify_bond`. Each call takes ~2s and runs F1/F1b/F2/F3/F8/F17.

### Performance on M2

- RTX 5060 Ti 16GB (available but CPU multiprocess faster for current workload)
- 153 pairs: 136s (CPU, 8 threads)
- 837 deep combos: 8.2 min
- Single falsification: ~2s
- Full calibration: ~9s

### Architecture

```
harmonia/
  src/
    domain_index.py     — 20 domain loaders
    coupling.py         — 4 scorers (cosine, distributional, alignment, phoneme)
    phonemes.py         — Mathematical Phonemes (5 universal coordinates)
    engine.py           — TT-Cross exploration engine
    validate.py         — Heuristic bond validation
    tensor_falsify.py   — 6-test battery at tensor speed
    sweep.py            — Parallel sweep across combinations
    landscape.py        — MAP-Elites explorer + known-truth calibration
  configs/
    domains.yaml        — All domain specs + phoneme mappings
  results/
    sweep_20domains.json      — Full 20-domain pairwise sweep
    deep_sweep.json           — 837-combo layer 2-6 sweep
    meta_sweep.json           — Battery+dissection as meta-dimensions
    landscape_v2.json         — MAP-Elites 300 explorations
    calibration_phoneme.json  — Known-truth calibration metrics
    falsification_v2.json     — Cross-domain inference validation
```

### The convergence

The battery (F1-F24b from cartography) and the tensor framework (Harmonia) are not separate systems. The battery test outcomes are entangled with the mathematical domains (rank 15 when added as a dimension). The dissection strategies (S1-S34) are entangled too. The analytical methods and the objects they analyze share the same underlying structure.

This means: refining the battery refines the tensor. Refining the tensor refines the battery. They converge on the same truth from different directions. The Mathematical Phonemes are the coordinate system where they meet.

### What's NOT done

- Per-phoneme null models (F1b needs work — current version too permissive)
- GPU acceleration (CUDA works but CPU multiprocess is faster at current scale)
- aitune integration (deferred — needs larger batch sizes to benefit)
- Scorer ensemble (run all 4, require agreement)
- High-precision zero features for Dirichlet L-functions (only EC zeros loaded so far)
- Integration with the full battery (battery_unified.py) — currently using tensor-speed approximation
