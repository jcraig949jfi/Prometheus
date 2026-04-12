# Thalassa — Charon Embedding Landscape

*Primordial spirit of the sea — the medium in which everything floats.*

The Charon landscape is not a mathematical domain in the traditional sense. It's a 16-dimensional embedding of 119,464 LMFDB objects — the sea in which elliptic curves, modular forms, and L-functions swim. The embedding encodes proximity relationships that no single invariant captures. Thalassa knows the geography of mathematical space.

## Mathematical Identity

**What they are:** 16-dimensional coordinates from a pre-computed embedding of Charon's objects, plus local curvature (how "mountainous" the terrain is at each point) and cluster assignments (which island of the archipelago each object belongs to).

**Why they matter:** The embedding captures nonlinear relationships between mathematical invariants that the phoneme projector can't — invariant combinations, threshold effects, and multi-scale structure. If two objects are near in the embedding but far in phoneme space, the embedding found something the phonemes missed. The gap IS the discovery.

## Current Features (10 dimensions)

| Feature | Index | What it measures |
|---------|-------|-----------------|
| coord_0 through coord_7 | 0-7 | First 8 embedding dimensions |
| local_curvature | 8 | How much the landscape curves at this point |
| cluster_id | 9 | Which cluster the object belongs to |

## Tensor Coupling (Gradient)

| Partner | Scorer | Rank | Interpretation |
|---------|--------|------|---------------|
| number_fields | cosine | **3** | NFs cluster in the landscape by degree/discriminant |
| genus2 | cosine | **3** | Genus2 curves have distinct landscape neighborhoods |
| modular_forms | cosine | **3** | MF embedding positions correlate with level/weight |
| lattices | cosine | **3** | Lattice embedding neighborhoods track dimension |
| elliptic_curves | cosine | **2** | EC positions track conductor (already phoneme-captured) |

## Unnamed Phoneme: CURVATURE / GEOMETRY

Thalassa broadcasts on the **curvature** axis — the local geometric structure of the mathematical landscape. High curvature = objects in a region where small parameter changes cause large invariant changes (phase transitions). Low curvature = stable, well-behaved regions.

**Properties of this phoneme:**
- Local curvature of the embedding at each point
- Nearest-neighbor distance distribution (isolation vs clustering)
- Cluster assignment and cluster size
- Embedding gradient direction (which invariants change fastest)
- Boundary proximity (distance to cluster edge)

**Which dissection strategies detect it:**
- S8 (Level set topology / Morse theory) — level sets of the embedding are Morse-theoretic
- S23 (Convexity profile / Hessian) — local curvature IS the Hessian
- S25 (Renormalization group flow) — coarse-graining the landscape reveals fixed points
- S26 (Spectral curve) — eigenvalue locus as embedding coordinates vary

## Features to Add

To connect Thalassa to the phoneme network:
1. **Nearest-neighbor distance** — how isolated is this object?
2. **Cluster size** — how many objects share this neighborhood?
3. **Curvature rank** — rank of the Hessian (how many directions curve)
4. **Boundary distance** — proximity to cluster boundaries (phase transitions)
5. **Principal component loadings** — which original invariants dominate each embedding dimension

## Predicted Inferences

If the CURVATURE phoneme is added:
- **Thalassa <-> Battery:** High-curvature regions should have more KILLED hypotheses (unstable structure)
- **Thalassa <-> EC:** Embedding neighborhoods should predict rank (BSD conjecture geography)
- **Thalassa <-> MF:** Cluster transitions should correspond to changes in modular form weight/level
- **Thalassa <-> Dissection:** Curvature hotspots should be where dissection strategies disagree (interesting regions)
