# Tensor Train Architecture — Why This Makes UPK Discovery Tractable
## 2026-04-06

---

## The Problem with Flat Search

Anyone can dump data into a relational database and write search queries.
But cross-domain scientific discovery isn't a search problem — it's a
**manifold traversal problem**. The state space is exponential. If you have
8 datasets with thousands of objects each, the cross-product is 10^15+ cells.
Most are empty. The bridges are buried in that emptiness.

Standard approaches die here. Keyword search misses vocabulary gaps.
Citation networks miss uncited connections. Embedding similarity misses
structural isomorphisms across different mathematical languages.

## Why Tensor Trains

Tensor Train decomposition (TT-decomposition) breaks a massive high-order
tensor into a chain of low-rank cores. This isn't just compression — it's
a **structural revelation mechanism**.

### 1. Revealing Latent Bridges

In a full tensor, a connection between a 1950s physics paper and a 2026
number theory result is buried under 10^15 empty cells.

TT-decomposition finds the **rank of the interaction**. If the bond
dimension (the link between adjacent cores) stays low, it means there is
a strong, compressible structural relationship between those disparate
domains. Low bond dimension = the bridge has simple structure. High bond
dimension = the relationship is complex but still capturable.

This is a mathematical way to detect Swanson's ABC commutativity —
X→Y in domain A, Y→Z in domain C — without comparing every paper to
every other paper. The tensor train finds the shared low-rank structure
that IS the bridge.

### 2. Searching the Basin Geometry

Tensor trains don't just compress data; they **preserve global topology**.

Searching a tensor train isn't keyword lookup — it's an operation on the
entire manifold of knowledge. You can treat impossibility theorems as
singularities or high-tension regions in the tensor. The way the tensor
"curves" around those impossibilities reveals the steering vectors that
researchers have used to try to bypass them.

This connects directly to Charon's spectral analysis: the zero distributions
of L-functions ARE the geometry of the number-theoretic landscape. The
tensor train captures that geometry across all our datasets simultaneously.

### 3. Bridge Scoring as Tensor Contraction

The "bridge score" between two cross-domain objects becomes a tensor contraction:

```
score = contract(query_tensor, knowledge_tensor_train)
```

You take a "query tensor" (representing a specific concept, impossibility,
or hypothesis) and contract it against the full knowledge tensor train.
The resulting scalar is the bridge score.

Because TT-contraction is O(d * n * r^2), you can run evolutionary search
loops across millions of objects in seconds. This is what makes the closed
loop tractable — generate hypothesis, contract against tensor, score,
branch, repeat. The battery runs on the contraction results.

### 4. Detecting Causal Role Signatures

If you represent the "shape" of a mathematical structure as a tensor pattern,
TT-format is exceptionally good at finding **near-isomorphisms**.

It can find a paper that "looks" like a solution to your problem even if
the vocabulary is 100% different. It's like finding two puzzles with the
exact same edge shape — the labels on the pieces don't matter, only the
way they click together.

This is why knot determinants matching LMFDB conductors survived our battery:
the numerical structure (odd integers in specific ranges) is isomorphic
even though the mathematical contexts (knot theory vs algebraic number theory)
share zero vocabulary.

## Architecture: How TT Connects to What We Built Today

```
Current state (2026-04-06):
  8 datasets → concept extraction → 12K concepts → 165 bridges
  Per-dataset distance metrics (cosine, Euclidean, graph distance)
  Separate tensors per domain

Future state (TT integration):
  8+ datasets → concept extraction → concept-indexed tensor
  TT-decomposition of the full cross-domain tensor
  Bond dimensions reveal bridge strength
  Contraction replaces brute-force search
  Rank evolution at bridges highlights UPK clusters
```

### Phase 1 (done): Separate tensors per domain
Each dataset has its own natural distance metric. LMFDB uses L-function
coefficient cosine. KnotInfo uses polynomial coefficient Euclidean.
These are the diagonal blocks of the full tensor.

### Phase 2 (concept layer, started): Bridge points as off-diagonal elements
The concept index connects objects across datasets. Each shared concept
creates an off-diagonal element in the cross-domain tensor. The 165 bridges
we found today are the first non-zero off-diagonal entries.

### Phase 3 (next): TT-decomposition of the bridge tensor
Once we have enough off-diagonal elements, decompose the full tensor into
TT-format. The bond dimensions between dataset cores tell us:
- Low rank → simple, direct bridge (shared integer, same formula)
- Medium rank → structural bridge (isomorphic pattern, different language)
- High rank → complex bridge (multi-step Swanson chain)

### Phase 4 (future): Dynamic rank evolution
The critical question: **fixed rank or evolving rank?**

The answer should be **evolving**. As the Noesis loop discovers more complex
compositions, the rank at specific bridges should grow. Allowing rank to
increase specifically at bridges is a clean way to highlight where the most
intense undiscovered research is clustered.

Implementation: start with fixed low rank (r=5-10), monitor reconstruction
error per bridge. Where error is high, increase local rank. The rank growth
map IS the UPK heat map — regions where the tensor needs more capacity to
represent the cross-domain structure are exactly where Sleeping Beauties live.

## Technical Implementation Notes

### Libraries
- **TensorLy** — Python tensor decomposition library (already in reference_toolkits.md)
- **t3f** — TensorFlow tensor train library
- **ttpy** — Pure Python TT library by Oseledets (the inventor of TT-decomposition)

### Key Operations
```python
# Conceptual (not real code yet)

# 1. Build the knowledge tensor
# Dimensions: [dataset, object, concept, property_type, value_range]
# Most entries are zero — the tensor is extremely sparse

# 2. TT-decompose
# cores = tt_decompose(knowledge_tensor, max_rank=10)
# Each core: dataset_i × concept × bond_dimension

# 3. Query by contraction
# query = encode_hypothesis(hypothesis)
# score = tt_contract(query, cores)

# 4. Rank evolution
# For each bridge, monitor ||T - TT(T)||_F / ||T||_F
# Where error > threshold, increase local rank
# Rank growth map = UPK heat map
```

### Computational Budget
- TT-decomposition of a 500K-object tensor: minutes on CPU
- TT-contraction for one query: milliseconds
- Full hypothesis testing loop (100 contractions): seconds
- This is why the pipeline can run 5 iterations in 90 seconds

## The Insight

The reason this approach finds what others miss:

1. **Google Scholar** optimizes for citation count → popular papers win
2. **Keyword search** optimizes for vocabulary match → jargon silos win
3. **Embedding similarity** optimizes for local neighborhoods → nearby papers win
4. **Tensor train contraction** optimizes for **structural isomorphism** → the SHAPE of the relationship wins, regardless of vocabulary, popularity, or domain

The shape is the bridge. The bridge is the discovery. The tensor train
makes the shape searchable.

---

*"The bridge exists. The tensor train makes it visible."*

## References

- Oseledets, I. V. (2011). "Tensor-Train Decomposition." SIAM J. Sci. Comput.
- Khoromskij, B. N. (2018). "Tensor Numerical Methods in Scientific Computing."
- Swanson, D. R. (1986). "Undiscovered Public Knowledge." Library Quarterly.
- Chen et al. (2026). "A Modular Framework for Automated Hypothesis Validation."

*Captured from conversation with James, 2026-04-06*
