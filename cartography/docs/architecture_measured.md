# Multi-Metric Tensor Architecture
## Measured properties of each domain tensor

### Domain Tensors (with native metrics)

| Domain | Objects | Metric | Silhouette | Survives Normalization? |
|--------|---------|--------|-----------|------------------------|
| L-functions (LMFDB) | 336K | Coefficient cosine | 0.55 (ARI) | NO (all scale) |
| OEIS sequences | 392K | Log-term cosine | 0.37 (K=10) | NO (growth IS structure) |
| mathlib theorems | 216K | Namespace Jaccard | N/A (graph) | N/A |
| Crystals (COD) | 500 | Cell ratio | 0.52 (K=3) | YES (crystal system is real) |
| Materials (MP) | 1000 | Property vector | 0.54 (K=5) | YES (metal/semi/insul real) |
| H spectrum (NIST) | 1,150 | Energy gaps | N/A (Rydberg exact) | N/A |
| Finite groups (GAP) | 97MB raw | TBD (char table) | TBD | TBD |
| FindStat | ~1000 stats | TBD (map structure) | TBD | TBD |

### Cross-Tensor Bridge Layer

| Bridge | Type | Strength | p-value |
|--------|------|----------|---------|
| OEIS -> mathlib (sequences predict imports) | Topological | 5.1x enrichment | N/A |
| OEIS terms <-> properties | Geometric | r=0.56 | 0.0001 |
| Operations -> imports | Predictive | r=0.27 | <0.0001 |
| LMFDB -> OEIS (coefficients) | Exact match | 72 ECs | N/A |
| OEIS <-> mathlib (RSA) | Geometric | r=-0.13 | 0.41 (NONE) |

### Key Architectural Decisions (Data-Driven)

1. PHYSICS tensors have real categorical structure that survives normalization.
   MATH tensors (OEIS, L-functions) collapse to scale under normalization.
   This means: physics landscapes can use direct distance metrics.
   Math landscapes need operation-based or topological metrics instead.

2. Operations predict proof dependencies (r=0.27) better than content (r=0.17).
   The bridge layer should match on OPERATIONS (functorial structure)
   not on CONTENT (shared objects). Category theory was right.

3. Symmetry predicts analogy density (R2=0.914).
   Datasets with high internal symmetry (groups, crystals, codes)
   will produce more bridges per object. Prioritize symmetric datasets.

4. The exploration is autocatalytic (1.9 findings/hr, accelerating).
   Each finding opens more threads than it closes.
   The self-directing loop works: bridges steer ingestion priority.
