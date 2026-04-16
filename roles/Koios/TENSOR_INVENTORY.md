# Tensor Inventory
## Maintained by Koios. Last updated: 2026-04-15.

---

## 1. Ergon Tensor (The Workhorse)

**Type**: Illuminated (active, hypothesis-testing substrate)
**File**: `ergon/tensor.npz`
**Shape**: `(58111, 28)` float32
**Size**: 312 KB
**Built by**: `ergon/tensor_builder.py` (370 lines)
**Consumed by**: `ergon/tensor_executor.py` (HypothesisExecutor class)

**Domain coverage** (7 domains, row ranges):
| Domain | Rows | Count |
|--------|------|-------|
| elliptic_curves | 0-10000 | 10,000 |
| modular_forms | 10000-20000 | 10,000 |
| number_fields | 20000-29116 | 9,116 |
| genus2_curves | 29116-39116 | 10,000 |
| maass_forms | 39116-44116 | 5,000 |
| knots | 44116-54116 | 10,000 |
| superconductors | 54116-58111 | 3,995 |

**Features** (28 columns): conductor, log_conductor, rank, torsion, n_bad_primes, ap_kurtosis, ap_compression_lz (EC); level, weight, dim (MF); discriminant, log_discriminant, class_number, regulator, degree (NF); conductor, discriminant, torsion, st_group, root_number (G2); level, spectral_parameter, coefficient_entropy (Maass); crossing_number, determinant, jones_degree, alex_degree (Knots); tc (SC)

**Data sources**: Charon DuckDB (EC, MF), cartography JSON files (NF, G2, Maass, Knots, SC)

**Status**: ACTIVE. Primary tensor for Ergon's exploration engine. Processes 100+ hypotheses/sec.

---

## 2. Shadow Tensor (The Dark Matter Map)

**Type**: Shadow (negative space — tracks where we looked and how things died)
**File**: `cartography/convergence/data/shadow_tensor.json`
**Shape**: Cell grid indexed by dataset pairs. Currently 2 populated cells.
**Size**: 3.1 MB
**Built by**: `cartography/shared/scripts/shadow_tensor.py`
**Sources**: research_memory.jsonl, bridge_hunter_results, void_scanner_results, genocide results (r1-r7), tensor_bridges.json

**Cell structure** (per dataset pair):
- n_tested, n_passed, n_killed
- kill_profile: `{F1: count, ..., F14: count}`
- p_distribution, z_distribution, effect_sizes
- best_p, best_z (closest misses)
- bond_dim, top_sv (from SVD)
- exploration_depth, hypothesis_types

**Purpose**: Maps the failure landscape. A ring of cells that barely fail (p~0.06) indicates gravitational signatures — something pulling the statistics that can't be seen directly. Kill-mode clusters reveal structural insights.

**Status**: ACTIVE but sparse. Only 2 cells populated in the main file. The real shadow data is distributed across preload and Ergon snapshots.

---

## 3. Shadow Preload

**Type**: Shadow (bulk failure data for shadow tensor reconstruction)
**File**: `cartography/convergence/data/shadow_preload.jsonl`
**Shape**: 6,240 lines
**Size**: 20.4 MB
**Built by**: `cartography/shared/scripts/preload_shadow.py`

**Status**: Input data for shadow tensor rebuilds. Large.

---

## 4. Ergon Shadow Archive (Generational Snapshots)

**Type**: Shadow (evolutionary exploration snapshots)
**Directory**: `ergon/results/shadow_*.json`
**Files** (13 snapshots):

| File | Size | Notes |
|------|------|-------|
| shadow_ergon_20260413_204649_gen15.json | 73 KB | Early generation |
| shadow_ergon_20260413_215133_gen1000.json | 992 KB | |
| shadow_ergon_20260413_215133_gen2000.json | 1.2 MB | |
| shadow_ergon_20260413_215133_gen3000.json | 1.3 MB | |
| shadow_ergon_20260413_215133_gen4000.json | 1.4 MB | Converging |
| shadow_ergon_20260413_215133_gen5000.json | 1.4 MB | |
| shadow_ergon_20260413_215133_gen6000.json | 1.4 MB | |
| shadow_ergon_20260413_215133_gen7000.json | 1.4 MB | |
| shadow_ergon_20260413_215133_gen8000.json | 1.5 MB | |
| shadow_ergon_20260413_215133_gen9000.json | 1.5 MB | Near-final |
| shadow_20260413_204752.json | 119 KB | Standalone snapshot |
| shadow_20260414_045031.json | 1.5 MB | Latest |

**Built by**: `ergon/shadow_archive.py` (ShadowArchive class)
**Indexed by**: `(domain_a, domain_b, feature_a, feature_b, coupling) -> FailureProfile`
**Consumed by**: Ergon's exploration engine (steers away from dead zones, toward gradient zones)

**Status**: ACTIVE. Shows convergence — files plateau at ~1.5 MB by gen 6000+.

---

## 5. Dissection Tensor (GPU-Accelerated Signature Space)

**Type**: Illuminated (multi-strategy mathematical fingerprints)
**File**: `cartography/convergence/data/dissection_tensor.pt` — **NOT CURRENTLY BUILT**
**Built by**: `cartography/shared/scripts/dissection_tensor.py` (4000+ lines)
**Consumed by**: `tensor_battery.py`, `kill_with_fire.py`, `kill_ec_maass.py`

**Design** (when built):
- Each mathematical object encoded as point in N-dimensional signature space
- 24 strategies (S1-S24): complex plane eval, mod-p fingerprints, spectral/FFT, p-adic valuation, symmetry groups, Galois groups, zeta-like density, etc.
- Battery dimensions: F_eta2, F_p, F_z, F_verdict
- TT-decomposition via TensorLy for compression
- GPU-native (CUDA, RTX 5060 Ti)

**Output format**: PyTorch `.pt` with `tensor [N, D]`, `mask [N, D]`, labels, domains, strategy_slices

**Status**: DORMANT. Script exists, `.pt` file not present. Was used for Megethos investigation (now killed).

---

## 6. Detrended Tensor (Prime-Stripped Landscape)

**Type**: Derived (raw values with prime structure removed)
**File**: `cartography/convergence/data/detrended_tensor.json`
**Size**: 2.6 KB (metadata only)
**Built by**: `cartography/shared/scripts/detrended_tensor.py`

**Contents**: Bond dimensions and SVD statistics for 10 dataset pairs after prime detrending:
- 5 datasets, 94 concepts, 166,102 links
- All bonds have bond_dim=1 (no multi-dimensional entanglement detected post-detrending)
- Companion files: `detrended_concepts.jsonl`, `detrended_links.jsonl`

**Purpose**: Creates a parallel concept layer where prime-driven structure is regressed out. Bridges in detrended space are invisible under raw primes.

**Status**: BUILT. Small metadata file; the real data is in the companion JSONL files.

---

## 7. V2 Domain-Specific Tensors

**Type**: Illuminated (specialized per-domain investigations)
**Directory**: `cartography/v2/`

| Script | Results | Size | Domain Focus |
|--------|---------|------|-------------|
| genus2_interference_tensor.py | 10.6 KB | 12.1 KB | Genus-2 curve interference patterns |
| prime_correlation_tensor.py | 17.9 KB | 15.2 KB | Prime correlation structure |
| sha_fricke_tensor.py | 3.9 KB | 11.4 KB | SHA/Fricke involution tensor |
| weil_phase_tensor.py | 5.4 KB | 9.9 KB | Weil pairing phase structure |

**Also**: `cartography/shared/scripts/v2/m43_tensor_rank_moonshine.py` (results: 0.9 KB)

**Status**: RESULTS EXIST. These were investigative tensors from the v2 exploration phase. Status of findings vs. forensic timeline unknown — need cross-reference.

---

## 8. Tensor Bridge Data

**Type**: Derived (cross-domain connection map)
**File**: `cartography/convergence/data/tensor_bridges.json`
**Size**: 147 KB
**Built by**: `cartography/shared/scripts/tensor_bridge.py`
**Consumed by**: `steering_vectors.py` (`load_tensor_bridges()`), shadow tensor builder

**Contents**: 2.7M links, 17 datasets, 279K objects, 39K concepts. Each bridge: dataset1/object1 -> dataset2/object2 with shared concepts, specificity, uniqueness scores.

**Status**: BUILT. Input to shadow tensor and exploration steering.

---

## 9. Tensor Validation Sweep

**Type**: Diagnostic
**File**: `cartography/convergence/data/tensor_validation_sweep.json`
**Size**: 19 KB
**Built by**: `cartography/shared/scripts/tensor_validation_sweep.py`

**Status**: BUILT. Validation results for tensor structure.

---

## 10. Auxiliary .npy Files

| File | Purpose |
|------|---------|
| `cartography/convergence/data/concept_vectors.npy` | Concept embedding vectors |
| `noesis/v2/damage_hub_matrix.npy` | Hub damage analysis (Noesis v2) |
| `noesis/v2/hub_alignment.npy` | Hub alignment matrix (Noesis v2) |
| `noesis/v2/prime_cone_coords.npz` | Prime cone coordinates (Noesis v2) |
| `cartography/metabolism/data/iML1515_eigenvalues.npy` | Metabolic network eigenvalues |
| `cartography/metabolism/data/iMM904_eigenvalues.npy` | Metabolic network eigenvalues |

**Status**: HISTORICAL. Noesis v2 and metabolism files from earlier exploration phases.

---

## 11. MPA Tensor Schema (The Admission Registry)

**Type**: Schema (not a data tensor — the rules for building the MPA)
**File**: `koios/data/mpa_tensor_schema.json`
**Maintained by**: Koios

**Current state**:
- **Admitted coordinates** (1): `m4_m2_squared` (spectral class, 5/5 gates, domains: EC/MF/Maass)
- **Rejected coordinates** (2): `modp_fingerprint` (failed Gate 5), `aut_size_ratio` (failed Gate 1)
- **Pending coordinates** (0)

**Status**: ACTIVE. This is the ground truth for what belongs in the MPA.

---

## 12. Audit Tensor Predictions

**Type**: Diagnostic
**Directory**: `audit/data/`

| File | Purpose |
|------|---------|
| tensor_239hub_predictions.json | 239-hub tensor predictions |
| tensor_9op_predictions.json | 9-operator tensor predictions |

**Status**: HISTORICAL. From audit phase.

---

## 13. Mock / Oscillation Shadow Data

**Type**: Shadow (experimental/mock)
**Directory**: `cartography/shared/scripts/v2/`

| File | Size | Purpose |
|------|------|---------|
| mock_shadow_mapping.py | 24.2 KB | Mock shadow tensor for testing |
| mock_shadow_results.json | 185.5 KB | Mock results |
| s6_oscillation_shadow_results.json | 0.2 KB | S6 oscillation shadow |

**Also**: `charon/v2/oscillation_shadow.py` + results, `cartography/v2/twist_shadow_commutator.py` + results

**Status**: EXPERIMENTAL. V2-era investigations.

---

## 14. External Tensor Libraries (Vault)

**Directory**: `vault/repos/`
- TensorLy (`tensorly/`) — used by dissection_tensor.py for TT-decomposition
- TensorLy-Torch (`tensorly-torch/`) — PyTorch backend
- TensorNetwork (`tensornetwork/`) — Google's tensor network library

**Status**: REFERENCE. Cloned for local use.

---

## Taxonomy Summary

| Category | Count | Total Size | Active? |
|----------|-------|-----------|---------|
| Illuminated (Ergon) | 1 | 312 KB | Yes |
| Illuminated (Dissection) | 0 (script only) | — | Dormant |
| Illuminated (V2 domain) | 4 | ~38 KB results | Check against forensic timeline |
| Shadow (main) | 1 | 3.1 MB | Yes (sparse) |
| Shadow (preload) | 1 | 20.4 MB | Yes |
| Shadow (Ergon archive) | 13 | ~15 MB total | Yes |
| Shadow (experimental) | 5 | ~190 KB | Historical |
| Derived (detrended) | 1 | 2.6 KB + JSONL | Built |
| Derived (bridges) | 1 | 147 KB | Built |
| Schema (MPA) | 1 | — | Active |
| Diagnostic | 3 | ~19 KB | Historical |
| Auxiliary .npy | 6 | varies | Historical |
