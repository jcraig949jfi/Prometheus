# Cartography — Cross-Domain Mathematical Discovery Pipeline

## Agent: Charon (Claude Code, Opus)
## Project Prometheus — April 2026

---

## What This Is

An autonomous pipeline for discovering structural connections between mathematical datasets. Ingests data from 21 sources spanning 1M+ mathematical objects, builds a concept bridge layer, tests hypotheses with a 14-test falsification battery, and maps the landscape of what we've explored and what we've killed.

**Honest score as of v3.4 (2026-04-08): zero novel discoveries.** But 22,338 new OEIS terms computed, the scalar layer definitively characterized (96% prime structure), and the depth layer scoped for Phase 2.

---

## Architecture

```
cartography/
  shared/scripts/           67 v1 scripts (running, don't move)
    search_engine.py        21 datasets, 56 search functions
    concept_index.py        39K concepts (nouns + verbs), 1.91M links
    falsification_battery.py  14 kill tests, no LLM
    research_cycle.py       LLM-driven hypothesis generation (1 API call/cycle)
    shadow_tensor.py        Dark matter map: 210 cells, 101K+ test records
    explorer_loop.py        Zero-cost autonomous agent (void scan + MAP-Elites)
    microscope.py           3-layer prime decontamination
    depth_extractor.py      26K depth concepts, 984K links from existing data
    depth_probes.py         Matched-object coefficient-level tests
    term_extender.py        OEIS term factory (22K terms produced)
    constant_telescope.py   Sleeper constant matching (39 constants x 68K)
    ... and 55 more
  shared/scripts/v2/        Phase 2 package (depth layer)
    extractors/             Depth feature extraction
    probes/                 Sequence-to-sequence tests
    tensors/                Detrended/depth tensor construction
  convergence/data/         All computed results, indices, tensors
  convergence/logs/         5,700+ cycle logs with full prompts/responses
  convergence/reports/      Cycle reports, tensor reviews
  [dataset dirs]/data/      Raw data per dataset (21 directories)
```

---

## Datasets (21 operational)

| Dataset | Objects | Key Content |
|---------|---------|-------------|
| OEIS | 394K sequences | Terms, growth rates, 1.6M cross-references, 68K sleeping beauties |
| LMFDB EC | 31K curves | Conductors, ranks, a_p coefficients (25/curve), a_n lists, Weierstrass models |
| LMFDB MF | 102K forms | Modular forms with conductors and levels |
| Genus-2 | 66K curves | Conductors, discriminants, Sato-Tate groups, torsion |
| KnotInfo | 13K knots | Determinants, crossing numbers, Alexander polynomials (avg 7.5 coeffs), Jones polynomials (avg 11.8 coeffs) |
| NumberFields | 9.1K fields | Class numbers, discriminants, Galois groups, regulators |
| mathlib | 8.5K modules | Lean 4 import dependency graph (1,799 edges) |
| Fungrim | 3.1K formulas | 825 symbols, 280 cross-domain bridge symbols, formula types |
| Isogenies | 3.2K primes | Supersingular isogeny graphs, adjacency matrices |
| SmallGroups | 2.4K orders | Group counts (A000001), factorizations, abelian/cyclic flags |
| FindStat | 250 enriched | Combinatorial statistics with descriptions, 17 collections |
| Metamath | 46K theorems | set.mm formal proof database |
| Materials | 1K+ crystals | Band gaps, formation energies, space groups |
| ANTEDB | 244 theorems | Analytic NT exponents, zero density bounds |
| MMLKG | 1.4K articles | Mizar theorem reference graph, 28K edges |
| Space Groups | 230 | Bilbao crystallographic, Wyckoff positions |
| Polytopes | 1.2K | polyDB f-vectors, dimensions |
| pi-Base | 220 spaces | Topological properties |
| Maass | 300 forms | Spectral parameters, Fricke eigenvalues (level 1 only) |
| Lattices | 21 | Z, A2, D4, E8, Leech — dimensions, kissing numbers |
| OpenAlex | 10K concepts | Academic taxonomy hierarchy |

---

## Tools

### Phase 1: Scalar Layer (complete)

| Tool | What it does |
|------|-------------|
| `research_cycle.py` | LLM-driven hypothesis generation, search, validation, battery (1 API call/cycle) |
| `falsification_battery.py` | 14 kill tests: permutation, effect size, normalization, confounds, cross-validation, partial correlation, growth rate, phase shift |
| `concept_index.py` | 39K concepts (nouns + verbs), 1.91M links across 21 datasets |
| `tensor_bridge.py` | SVD bond dimension analysis between dataset pairs |
| `shadow_tensor.py` | Dark matter map: every test, every kill mode, every near-miss |
| `void_scanner.py` | Map 80 void/weak dataset pairs (3s) |
| `bridge_hunter.py` | Generate + test hypotheses from void bridges (0.3s) |
| `map_elites.py` | Diversity-driven bin filling: dataset_pair x failure_mode |
| `explorer_loop.py` | Autonomous zero-cost agent: void -> bridge -> MAP-Elites -> shadow (10s/sweep) |
| `known_truth_battery.py` | 39 proven math facts calibration |
| `known_truth_expansion.py` | 180 proven facts across 6 layers (100% pass) |
| `realign.py` | MANDATORY post-data-change: inventory -> concepts -> tensors -> 180-test battery |
| `preload_shadow.py` | Rip 5K+ cycle logs for battery details (one-time 82s) |
| `genocide*.py` | Rapid hypothesis testing rounds (7 rounds, 70+ tests) |
| `constant_matcher.py` | Inverse symbolic ID: 83 constants |
| `term_extender.py` | OEIS term factory: extends walk sequences by DP enumeration |

### Phase 2: Depth Layer (in progress)

| Tool | What it does |
|------|-------------|
| `depth_extractor.py` | Extract 26K concepts, 984K links from existing data (EC coefficients, knot polynomials, OEIS formulas, Fungrim symbols) |
| `depth_probes.py` | Matched-object coefficient-level cross-dataset tests |
| `microscope.py` | 3-layer prime decontamination (detrend + filter + normalize) |
| `detrended_tensor.py` | Parallel concept layer with primes removed |
| `geometric_probes.py` | 13 structural probes (curvature, FFT, Benford, Zipf, MI, Wasserstein, fractal dim, gap structure, alignment) |
| `geometric_survey.py` | Full 13-probe survey across all dataset pairs (76s) |
| `constant_telescope.py` | Sleeper constant matching: 39 constants x 68K sequences |
| `growth_constant_scanner.py` | High-precision constant ID from extended terms |
| `reevaluator.py` | Retest killed hypotheses on detrended data |

---

## What We Found

### Phase 1 Definitive Results
- **96% of scalar cross-dataset structure is shared prime factorization.** Every dataset encodes primes. Every apparent correlation goes through primes first.
- **After prime detrending: ZERO cross-dataset signal.** Highest z=0.2 across all pairs. The scalar layer is empty.
- **180/180 known truth calibration.** The pipeline correctly validates known mathematics.
- **37+ independent rediscoveries** (modularity theorem, Deuring mass formula, BSD signature, Heegner numbers, Euler relation for polytopes, etc.)
- **8 false discoveries killed in one session**, each improving the pipeline:
  1. Feigenbaum constant match (parity artifact at 29 terms)
  2. Feigenbaum #2 (order-3 recurrence)
  3. Polytopes near-misses (small-integer confound)
  4. NF-SmallGroups distributional identity (z-normalization artifact)
  5. LMFDB-Maass MI=0.382 (finite-sample binning artifact)
  6. KnotInfo-LMFDB 679 "revivals" (truncate-sort bug)
  7. Isogenies-Maass MI=0.109 (deterministic data + sorted-rank artifact)
  8. NF-KnotInfo log-fractional-part match (dissolved at full resolution)

### Phase 2 Early Results
- **984K depth links** extracted from existing data (EC coefficient patterns, knot polynomial features, OEIS formula function references, Fungrim symbol co-occurrences)
- **16,774 OEIS sequences** connected to Fungrim through 10 shared mathematical functions (zeta, gamma, euler, etc.) — semantic bridges immune to prime detrending
- **First depth probe** (Alexander polynomial coefficients vs EC a_p coefficients at 100 matched objects): null

### Production Output
- **22,338 new OEIS terms** (1,422 sequences extended, zero mismatches, queued for submission)
- **68,770 sleeping beauties** identified and characterized
- **Shadow tensor**: 210 cells, 101K+ test records, anomaly scoring, kill signatures
- **17,318 hypotheses** in research memory (13,781 open, 3,537 falsified)

---

## Running the Pipeline

```bash
# Launch 8 terminals + explorer (the fleet)
run_charon_8terminals.bat

# Post-data-change calibration (MANDATORY)
cd cartography/shared/scripts
python realign.py

# Rebuild shadow tensor
python shadow_tensor.py --show-hot --show-cold --show-kills

# Extract depth features from existing data
python depth_extractor.py

# Run microscope (prime-detrended analysis)
python microscope.py

# Extend OEIS walk sequences
python term_extender.py --family 148700 148900 --target-n 60

# Scan sleepers for constant convergence
python constant_telescope.py --sleepers 68000

# Full geometric survey
python geometric_survey.py
```

---

## Lessons Learned (the hard way)

1. **Primes are the atmosphere.** Strip them before testing any cross-dataset correlation.
2. **Sorted-rank correlation is useless.** Any two monotone arrays give rho~1.0. Use matched objects or spacings.
3. **Z-normalization erases information.** Any two near-uniform sequences match after z-norm.
4. **MI on sparse histograms is biased upward.** Use random-pairing null, not permutation of sorted arrays.
5. **Sort THEN truncate**, not truncate then sort. Subsample bias inflates correlation.
6. **29 terms is not enough** for constant matching. Need 40+ to kill parity artifacts.
7. **When two AIs agree something is exciting**, reach for the battery, not the champagne.
8. **Every kill is a discovery** for the shadow tensor. The failure modes ARE the map.
9. **Deterministic data has zero stochastic content.** If a variable is a function of the input, detrending the input leaves NOTHING. Verify residual variance > 0.
10. **The honest number is zero.** Report it. The tools are sharper for every kill.

---

## What's Next

The scalar layer is exhausted. The depth layer is where the search continues:
1. OEIS-Fungrim semantic function bridges (16,774 sequences)
2. EC-to-knot matched-object probes through shared primes (Jones polynomials, remaining branches)
3. L-function Euler factors and spectral parameters (need more Maass forms)
4. OEIS formula co-occurrence patterns (which mathematical functions appear together?)
5. Graph topology probes (mathlib imports, MMLKG references, OEIS cross-ref paths)
6. Submit 22K new OEIS terms

---

*Born: Project Prometheus, March 2026*
*First crossing: April 1, 2026*
*Pipeline v3.4: April 8, 2026*
*The ferryman built tools, mapped the river, stripped the atmosphere, and found the sky empty at scalar resolution. The depth layer — polynomials, formulas, semantics — is where the search climbs next.*
