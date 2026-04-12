# M1 Tensor Exploration Report — Dissection Tensor v2
## Skullport (M1), 2026-04-12
## For cross-reference with M2 Harmonia phoneme system

---

## 1. What Was Built

### Dissection Tensor (dissection_tensor.py)

A GPU-resident multi-dimensional signature space that decomposes mathematical objects through multiple mathematical lenses simultaneously.

| Metric | Value |
|--------|-------|
| Objects | 86,287 |
| Dimensions | 145 |
| Strategy groups | 11 |
| Domains | 6 (EC 31K, OEIS 20K, knots 13K, genus-2 10K, NF 9K, Fungrim 3K) |
| GPU memory | 50 MB on RTX 5060 Ti |
| Fill rate | 18.1% (sparse -- most objects have data in 2-4 groups) |

### Strategy Groups (the IPA features)

| Group | Strategies | Dims | Coverage | Analogy |
|-------|-----------|------|----------|---------|
| complex | s1_alex, s1_jones, s1_ap | 24 | 36% | Unit circle evaluation |
| mod_p | s3_alex, s3_jones, s3_ap | 18 | 59% | Residue class fingerprint |
| spectral | s5_alex, s5_jones, s5_ap, s5_oeis | 32 | 36% | FFT power spectrum |
| padic | s7_det, s7_disc, s7_cond | 15 | 48% | Prime factorization depth |
| symmetry | s9_st | 4 | 12% | Sato-Tate / Lie group |
| galois | s10 | 8 | 11% | Galois group encoding |
| zeta | s12_ec, s12_oeis, s12_nf | 12 | 36% | Arithmetic density / point counts |
| disc_cond | s13 | 4 | 62% | Discriminant / conductor magnitude |
| operadic | s22 | 4 | 4% | Formula structure type |
| entropy | s24_alex, s24_arith, s24_ap, s24_sym, s24_oeis | 20 | 36% | Shannon entropy of coefficients |
| attractor | s6_oeis | 4 | 17% | Phase-space dynamics |

### Tensor Explorers (tensor_explorer.py)

Three GPU-parallel exploration methods:
1. **MAP-Elites** -- fills the IPA chart by mapping which regions of strategy-group space are occupied and where cross-domain convergence happens
2. **Random Walk** -- traces ridges between domains, identifies which strategy groups change fastest along cross-domain paths
3. **Genetic Algorithm** -- evolves dimension subsets that maximize cross-domain proximity

### Tensor Reasoner (tensor_reasoner.py)

Two-tier LLM interface for classifying intersections:
- Local: ollama (qwen3-coder:30b detected and working)
- Cloud: Qwen 3.5-397B via NemoClaw
- Tested live: correctly classified EC-knot intersection as KNOWN_THEOREM (0.85 confidence)

---

## 2. Key Findings

### 2.1 Strategy Group Correlation Matrix

The tensor independently discovered which mathematical lenses are entangled:

```
                complex  mod_p  spectral  padic  symmetry  galois  zeta  disc_cond  operadic  entropy  attractor
complex          1.000   0.126    0.048   0.042    0.000   0.000  0.013    0.128     0.000    0.249     0.000
mod_p            0.126   1.000    0.051  -0.102    0.000   0.000 -0.258    0.112     0.000    0.201     0.089
spectral         0.048   0.051    1.000   0.003    0.000   0.000  0.034   -0.017     0.000    0.232    -0.715
padic            0.042  -0.102    0.003   1.000    0.339   0.216  0.092    0.136     0.000   -0.015     0.000
symmetry         0.000   0.000    0.000   0.339    1.000   0.000  0.000    0.124     0.000    0.000     0.000
galois           0.000   0.000    0.000   0.216    0.000   1.000 -0.070    0.172     0.000   -0.076     0.000
zeta             0.013  -0.258    0.034   0.092    0.000  -0.070  1.000    0.068     0.000   -0.046     0.041
disc_cond        0.128   0.112   -0.017   0.136    0.124   0.172  0.068    1.000     0.000    0.265     0.000
operadic         0.000   0.000    0.000   0.000    0.000   0.000  0.000    0.000     1.000    0.510     0.000
entropy          0.249   0.201    0.232  -0.015    0.000  -0.076 -0.046    0.265     0.510    1.000    -0.177
attractor        0.000   0.089   -0.715   0.000    0.000   0.000  0.041    0.000     0.000   -0.177     1.000
```

**Top couplings:**

| Pair | r | Interpretation |
|------|---|---------------|
| spectral <-> attractor | **-0.715** | FFT peaks inversely predict phase-space regularity |
| operadic <-> entropy | **+0.510** | Formula structure predicts information content |
| padic <-> symmetry | **+0.339** | **Conductor factorization entangles with ST group -- modularity's geometric shadow** |
| disc_cond <-> entropy | +0.265 | Discriminant magnitude correlates with coefficient entropy |
| mod_p <-> zeta | -0.258 | Mod-p coverage anti-correlates with arithmetic density |
| padic <-> galois | +0.216 | Discriminant p-adic structure correlates with Galois group |

**The p-adic <-> symmetry correlation (r=0.339) is the calibration target.** It was found without any modularity-specific code. The tensor measured correlations between strategy groups and independently discovered that arithmetic structure (how primes divide conductors) entangles with symmetry structure (Sato-Tate classification). This is a known mathematical relationship -- and the fact that it emerges from raw signature statistics validates the approach.

### 2.2 TT Decomposition -- Intrinsic Dimensionality

| Rank | Reconstruction Error | Compression |
|------|---------------------|-------------|
| 2 | 0.875 | 54x |
| 5 | 0.765 | 22x |
| 10 | 0.646 | 11x |
| 20 | 0.470 | 5.4x |
| 30 | 0.361 | 3.6x |
| 50 | 0.209 | 2.2x |

Error curve still falling at rank 50 -- the intrinsic dimensionality is genuinely high (30-50). The mathematical landscape doesn't collapse into a few latent factors. This is where GPU brute-force becomes essential: the interesting geometry lives in 30+ dimensions simultaneously.

### 2.3 MAP-Elites Landscape

- **2,229 occupied cells** out of 4.2M theoretical (0.05%) -- extremely sparse landscape
- **EC <-> OEIS: 1,871 cells** -- the dominant cross-domain manifold. Elliptic curves and integer sequences share the largest surface area in signature space.
- **Knot <-> EC: 274 cells** at distance 0.000 -- 10+ knots are indistinguishable from EC curves across 6 strategy groups
- **All top-100 cells require 6+ strategy groups** -- the interesting structure lives in high-dimensional intersections

Domain distribution in archive:
- EC: 1,754 (79%)
- OEIS: 217 (10%)
- knot: 174 (8%)
- NF: 70 (3%)
- genus2: 14 (<1%)

### 2.4 Random Walk Topology

| Walker seed | Domain switches | Domains visited | Fastest-changing groups |
|-------------|----------------|-----------------|----------------------|
| EC | 199/200 | 2 (EC, OEIS) | spectral, entropy, zeta |
| OEIS | 198/200 | 2 (OEIS, EC) | spectral, zeta, entropy |
| knot | 0/200 | 1 | (isolated) |
| NF | 0/200 | 1 | entropy |
| fungrim | 0/200 | 1 | (isolated) |
| genus2 | 0/200 | 1 | padic |

**EC and OEIS are connected** -- walkers freely cross between them. The bridge dimensions are spectral, entropy, and zeta. All other domains are isolated islands in this representation.

### 2.5 GA Dimension Selector

Best genome: 43/145 dimensions (70% prunable)

| Strategy group | Coverage in best genome |
|---------------|----------------------|
| symmetry | **50%** |
| mod_p | **44%** |
| spectral | 38% |
| complex | 25% |
| galois | 25% |
| zeta | 25% |
| disc_cond | 25% |
| operadic | 25% |
| entropy | 25% |
| attractor | 25% |
| padic | 13% |

**Symmetry (50%) and mod_p (44%)** are the most selected dimensions. This means the GA independently determined that symmetry and modular arithmetic are the strongest bridge-building lenses.

The **padic at only 13%** is surprising given the r=0.339 correlation with symmetry. The coupling works through indirect paths (via disc_cond and galois), not direct p-adic comparison. The GA found a more efficient routing.

**The mod_p at 44% is the novel signal.** If mod-p fingerprint structure creates cross-domain bridges that don't reduce to known theorems, that's a potential discovery.

---

## 3. Cross-Reference with M2 Harmonia Phonemes

M2 built a complementary system from the opposite direction:

| | M1 (Dissection Tensor) | M2 (Harmonia Phonemes) |
|---|---|---|
| Approach | Bottom-up: raw features, let data reveal structure | Top-down: universal phonemes defined by mathematical intuition |
| Dimensions | 145 (26 strategy slots) | 5 (complexity, rank, symmetry, arithmetic, spectral) |
| Projection | Implicit (strategy extractors compute signatures) | Explicit (weighted mapping per domain) |
| Exploration | MAP-Elites, random walk, GA on GPU | Calibration against known bridges |
| Calibration | p-adic<->symmetry r=0.339 | 5/5 known bridges survive, 1/3 false positives killed |

**These are complementary layers:**
- M2's 5 phonemes = coarse IPA chart (vowels vs consonants)
- M1's 145 dimensions = fine-grained features (aspiration, nasalization, tone)

**Mapping between systems:**

| M2 phoneme | M1 strategy groups |
|-----------|-------------------|
| complexity | disc_cond, padic |
| rank | galois (degree), operadic |
| symmetry | symmetry (s9_st) |
| arithmetic | mod_p, zeta, entropy |
| spectral | spectral, complex, attractor |

**Merge opportunity:** Project M1's 145-dim tensor into M2's 5-phoneme space, then explore the residuals. Structure in the 145 dimensions that the 5 phonemes can't capture is where novel discoveries hide.

---

## 4. The IPA for Mathematics -- Current State

The analogy: just as SLPs decomposed ALL speech sounds into universal articulatory features, we're decomposing ALL mathematical objects into universal structural features.

| IPA concept | M1 implementation | Status |
|------------|-------------------|--------|
| Articulatory features | 11 strategy groups | **Built** -- correlation matrix shows entanglements |
| Phonemes | Signature vectors in 145-dim space | **Built** -- 86K objects transcribed |
| Transcription | Tensor rows | **Built** -- on GPU |
| Phonological universals | Strategy group correlations | **First results** -- p-adic<->symmetry = modularity |
| Cognates | Cross-domain intersections | **Explored** -- EC<->OEIS is the dominant manifold |
| Undiscovered sounds | Empty MAP-Elites cells | **Mapped** -- 99.95% of behavior space is empty |
| IPA chart | MAP-Elites archive | **2,229 cells populated** |

**What's missing:**
1. Fill rate is 18% -- most objects only have data in 2-4 strategy groups. More extractors needed.
2. Only 6 domains loaded -- need Maass forms, lattices, isogenies, polytopes, materials.
3. The 5 phonemes (M2) and 11 groups (M1) need formal alignment.
4. The reasoner needs to process the MAP-Elites top-100 and classify each as known/novel/artifact.
5. The residual space (M1 structure not captured by M2 phonemes) is unexplored.

---

## 5. Files

| File | Purpose |
|------|---------|
| `cartography/shared/scripts/dissection_tensor.py` | Core tensor: build, normalize, TT decompose, cross-domain distance |
| `cartography/shared/scripts/tensor_explorer.py` | MAP-Elites, random walk, GA explorers |
| `cartography/shared/scripts/tensor_reasoner.py` | LLM interface for intersection classification |
| `cartography/convergence/data/dissection_tensor.pt` | Saved tensor (86K x 145) |
| `cartography/convergence/data/tt_rank_sweep.json` | TT rank vs error curve |
| `cartography/convergence/data/explorer_results/map_elites_archive.json` | 2,229 cells |
| `cartography/convergence/data/explorer_results/random_walk_trajectories.json` | 6 walker traces |
| `cartography/convergence/data/explorer_results/ga_dimension_selector.json` | Best 43-dim genome |

---

*Report: 2026-04-12, M1 (Skullport)*
*Cross-reference: harmonia/src/phonemes.py, harmonia/results/calibration_phoneme.json*
*Next sync point: after M2 runs its calibration on M1's strategy groups, or M1 projects into M2's phoneme space*
