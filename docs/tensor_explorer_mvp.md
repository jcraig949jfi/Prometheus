# Tensor Explorer MVP — Poros

*Combinatorial concept exploration at computational speed, not language speed*

---

## The Problem

Nous explores 95^3 = 857,375 concept triples by sending each to a 397B model via API. At 30 seconds per call, the full space takes 285 days. We've covered ~3,500 in two weeks. That's 0.4% of the space.

The Lattice has 95 nodes. The dark edges number 4,465 pairwise + 857,375 triplewise. We're exploring by candlelight in a cathedral.

## The Insight

Concept combination isn't a language problem. It's a computational geometry problem. If we encode concepts as mathematical objects (tensors of structural properties), combination becomes a tensor operation that runs in microseconds, not seconds.

We don't need a 397B model to tell us that "Topology + Immune Systems has boundary-detection properties." We can compute that directly from the structural features of both concepts.

What we DO need the 397B model for: interpreting the high-scoring combinations in natural language, and generating implementation code. But the *search* — finding WHICH combinations are worth interpreting — should be computational.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  CONCEPT TENSOR LIBRARY                                  │
│                                                          │
│  Each concept encoded as a D-dimensional feature vector  │
│  (D = 30-50 structural properties)                       │
│                                                          │
│  Properties: dimensionality, linearity, determinism,     │
│  scale_invariance, compositionality, invertibility,      │
│  stability, entropy, boundary_sensitivity,               │
│  self_reference, temporal, conservation, ...             │
│                                                          │
│  Source: hand-seeded initially, then learned from         │
│  which combinations succeed in the forge                 │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│  TENSOR INTERACTION ENGINE                               │
│                                                          │
│  Pairwise: outer product → rank-2 interface tensor       │
│  Triplewise: einsum → rank-3 interaction tensor          │
│  N-wise: tensor network contraction                      │
│                                                          │
│  Novelty score: ||emergent|| / ||total||                 │
│  Complementarity: how different are the inputs?           │
│  Resonance: do the structural properties reinforce?      │
│                                                          │
│  Speed: ~1M combinations/second on CPU                   │
│  Full 95^3 space: < 1 second                             │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│  TENSOR TRAIN COMPRESSION (TensorLy / THOR)              │
│                                                          │
│  Compress the full interaction space:                     │
│    Raw: 95 × 95 × 95 × D = ~43M entries                 │
│    TT rank 10: ~285K entries (150x compression)          │
│                                                          │
│  Navigate compressed representation:                     │
│    - Find top-K novelty scores without decompressing     │
│    - Identify clusters of high-novelty regions           │
│    - Track which regions are explored vs unexplored      │
│    - Update incrementally when new concepts are added    │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│  SCORING & FILTERING                                     │
│                                                          │
│  From ~857K triples, score all computationally:          │
│                                                          │
│  Score 1: Novelty (emergent structure)                   │
│    = properties of combination that neither input has    │
│                                                          │
│  Score 2: Complementarity (structural diversity)         │
│    = how different are the input concept tensors?        │
│    (identical concepts score 0 — no new information)     │
│                                                          │
│  Score 3: Resonance (reinforcing properties)             │
│    = do the concepts share structural features that      │
│      amplify when combined? (both boundary-sensitive,    │
│      both scale-invariant → resonance)                   │
│                                                          │
│  Score 4: Exploration velocity feedback                  │
│    = did previous combinations with similar tensor       │
│      signatures lead to forge successes?                 │
│    (learned from Coeus causal data)                      │
│                                                          │
│  Combined: weighted sum, top 100 sent to LLM             │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│  LLM INTERPRETATION (only for top candidates)            │
│                                                          │
│  Send top 100 triples to 397B model:                     │
│    "Concepts A, B, C have these tensor properties:       │
│     [novelty=0.85, complementarity=0.92, resonance=0.71] │
│     The emergent structure has high boundary_sensitivity  │
│     + self_reference + nonlinearity.                     │
│     What interface exists? Name it. Can it be coded?"    │
│                                                          │
│  This is 100 API calls, not 857,000.                     │
│  ~50 minutes instead of 285 days.                        │
│                                                          │
│  High-scoring results → Hephaestus forge → Sphinx test   │
└──────────────────────────────────────────────────────────┘
```

---

## Concept Feature Encoding

### Initial Feature Set (30 dimensions)

Each concept gets a manually-seeded feature vector. This is the bootstrap — later, the system learns better features from forge success data.

```python
CONCEPT_FEATURES = {
    "topology": {
        "dimensionality": 0.9,      # operates in arbitrary dimensions
        "linearity": 0.3,           # mostly nonlinear (homeomorphisms)
        "determinism": 1.0,         # fully deterministic
        "scale_invariance": 0.8,    # topological properties are scale-free
        "compositionality": 0.7,    # spaces compose (product topology)
        "invertibility": 0.9,       # homeomorphisms are invertible
        "stability": 0.9,           # invariants are stable
        "information_content": 0.6, # moderate (qualitative, not quantitative)
        "boundary_sensitivity": 0.95,# extremely boundary-aware
        "self_reference": 0.4,      # fundamental group is self-referential
        "temporal": 0.1,            # mostly atemporal
        "conservation": 0.95,       # topological invariants are conserved
        "hierarchy": 0.7,           # homology groups form hierarchies
        "locality": 0.3,            # global properties from local data
        "symmetry": 0.8,            # symmetry groups central
        "discreteness": 0.3,        # mostly continuous
        "causality": 0.1,           # no inherent causality
        "adaptivity": 0.1,          # static structures
        "emergence": 0.6,           # global properties emerge from local
        "robustness": 0.95,         # invariant under deformation
        # ... 10 more dimensions
    },
    "immune_systems": {
        "dimensionality": 0.7,
        "linearity": 0.2,
        "determinism": 0.3,         # highly stochastic
        "scale_invariance": 0.5,
        "compositionality": 0.6,
        "invertibility": 0.2,       # mostly irreversible
        "stability": 0.4,           # dynamic equilibrium
        "information_content": 0.8, # high (diverse repertoire)
        "boundary_sensitivity": 0.95,# self/non-self IS boundary detection
        "self_reference": 0.7,      # self-recognition is core
        "temporal": 0.9,            # highly time-dependent
        "conservation": 0.3,        # population dynamics, not conservation
        "hierarchy": 0.8,           # innate → adaptive hierarchy
        "locality": 0.7,            # local detection, systemic response
        "symmetry": 0.2,            # asymmetric (self vs non-self)
        "discreteness": 0.6,        # discrete cells, continuous concentrations
        "causality": 0.8,           # causal chains (antigen → response)
        "adaptivity": 0.95,         # extreme adaptivity
        "emergence": 0.9,           # population-level behavior emerges
        "robustness": 0.7,          # robust to mutation, fragile to autoimmune
    },
}
```

### Computing the Interface

```python
import numpy as np

def concept_interface(a, b):
    """Compute the interface tensor between two concepts."""
    va = np.array(list(a.values()))
    vb = np.array(list(b.values()))

    # Outer product = full interface tensor
    interface = np.outer(va, vb)

    # Emergent properties: where both concepts score high
    # but in DIFFERENT dimensions (complementarity)
    resonance = va * vb  # element-wise: both high = reinforcing
    complementarity = np.abs(va - vb)  # high difference = complementary

    # Novelty: properties of the combination that neither has alone
    # The off-diagonal of the outer product captures cross-dimensional interactions
    diagonal = np.diag(interface)
    off_diagonal_energy = np.sum(interface**2) - np.sum(diagonal**2)
    total_energy = np.sum(interface**2)
    novelty = off_diagonal_energy / total_energy if total_energy > 0 else 0

    return {
        "resonance": float(np.mean(resonance)),
        "complementarity": float(np.mean(complementarity)),
        "novelty": float(novelty),
        "interface_rank": int(np.linalg.matrix_rank(interface, tol=0.1)),
        "dominant_dimensions": list(np.argsort(resonance)[-5:][::-1]),
    }
```

### Speed Benchmark

```python
# 95 concepts × 30 features each
# All pairwise interfaces: 95*94/2 = 4,465
# Time: ~2ms on one CPU core

# All triplewise interactions: 95*94*93/6 = 138,415
# Time: ~50ms on one CPU core

# Full 95^3 with replacement: 857,375
# Time: ~300ms on one CPU core

# With tensor train compression and top-K extraction:
# Time: ~500ms for the full scan + top 100 extraction
```

---

## Tensor Train Navigation

```python
import tensorly as tl
from tensorly.decomposition import tensor_train

# Build the full interaction tensor
# Shape: (95, 95, 95) where entry [i,j,k] = novelty_score(concept_i, concept_j, concept_k)
interaction = np.zeros((95, 95, 95))
for i in range(95):
    for j in range(i+1, 95):
        for k in range(j+1, 95):
            score = compute_triple_novelty(concepts[i], concepts[j], concepts[k])
            # Symmetric: fill all permutations
            interaction[i,j,k] = interaction[i,k,j] = interaction[j,i,k] = score
            interaction[j,k,i] = interaction[k,i,j] = interaction[k,j,i] = score

# Compress to tensor train (rank 10 = ~150x compression)
tt_cores = tensor_train(tl.tensor(interaction), rank=[1, 10, 10, 1])

# Navigate the compressed representation
# Find top-100 triples without decompressing the full tensor:
top_indices = tt_top_k(tt_cores, k=100)

# Incremental update when a new concept is added:
# Only recompute the new slices, not the full tensor
new_slices = compute_new_concept_interactions(new_concept, existing_concepts)
tt_cores = tt_update(tt_cores, new_slices)
```

---

## What Makes This Different from Nous

| | Nous (current) | Poros Tensor Explorer |
|---|---|---|
| **Speed** | 30s per triple (API) | ~1M triples/second (CPU) |
| **Coverage** | 3,500 of 857K (0.4%) | 857K of 857K (100%) |
| **Scoring** | LLM judgment (subjective) | Mathematical structure (objective) |
| **LLM usage** | Every triple | Top 100 only (after computational filter) |
| **API cost** | ~$0.01/triple | ~$0.01/100 triples (100x cheaper) |
| **Scalability** | Linear in API calls | Quadratic in concepts, but tensor-compressed |
| **Adding concepts** | Re-scan everything | Incremental TT update |
| **Exploration memory** | Flat JSONL | Compressed tensor (navigable) |

---

## The MVP Build

### What You Need

- `tensorly` (already listed in reference_toolkits.md)
- `numpy` (already installed)
- 30 minutes to hand-seed the first 20 concept feature vectors
- 2 hours to build the tensor interaction engine
- 1 hour to wire the top-K output into existing Nous/Hephaestus pipeline

### What You Get

- Complete scan of the 857K triple space in under 1 second
- Top 100 highest-novelty triples, ranked by emergent structure
- Those 100 go to the 397B model for interpretation (50 minutes of API time)
- Results feed Hephaestus forge as usual
- Exploration velocity metric: triples_scored / wall_clock_time

### What You Learn

Even if every triple scores 0 on the forge battery, you learn:
- Which structural properties predict forge success (feed back to feature encoding)
- Which regions of the tensor are uniformly low-novelty (mark infeasible, stop exploring)
- Which regions are high-novelty but untested (the frontier)
- Whether the tensor structure itself reveals clusters that text-based exploration missed

### Future Extensions

1. **Learned features**: Replace hand-seeded features with features learned from forge success data. Coeus already knows which concept properties predict forging — use those as tensor dimensions.

2. **Dynamic concepts**: When Eos finds a new technique, auto-encode it as a feature vector and incrementally update the tensor train. The exploration space grows without full recomputation.

3. **Higher-order**: Four-way and five-way concept intersections. Tensor networks (THOR) handle this without the exponential blowup that raw tensors suffer.

4. **Waste stream integration**: Arcanum specimens get encoded as feature vectors too. They enter the tensor space as nodes with unusual properties — high self_reference, low determinism, unknown dimensionality. The tensor explorer finds which known concepts interface with the unknown specimens.

5. **GPU acceleration**: The tensor operations parallelize perfectly. Move to GPU and the full scan drops from 300ms to 3ms. At that speed, you can re-scan after every forge result and track exploration velocity in real-time.

---

## Wacky Extensions (Why Not)

### B-Tree Concept Navigation
Organize the tensor space as a B-tree where each level splits on a different structural property. Navigate to "high boundary_sensitivity + high self_reference + low determinism" in O(log N) instead of scanning. Find the concept cluster that lives in that region. Ask: what's the emergent structure of that cluster?

### Random Projection Exploration
Instead of systematic search, randomly project the 30D concept space into 2D, 3D, 5D subspaces. In each projection, the "interesting" regions look different. Concepts that cluster together in one projection but separate in another have a complex, multi-faceted interface. That complexity IS the novelty signal.

### Concept Diffusion
Treat the tensor space as a diffusion medium. Drop a "heat source" on one concept and let it diffuse through the tensor connections. Where the heat accumulates = concepts that are structurally close through multiple pathways. Where heat doesn't reach = concepts that are genuinely isolated. The diffusion frontier IS the exploration frontier.

### Evolutionary Feature Discovery
Don't hand-seed the 30 feature dimensions. Evolve them. Start with random features. Score each feature set by how well it predicts forge success. CMA-ES optimizes the feature encoding. After 1000 generations, the features the system discovers might not be interpretable by humans — but they'll be the features that best predict which concept combinations produce reasoning tools.

This is the Arcanum of the feature space itself — structural dimensions that the system needs but humans can't name.
