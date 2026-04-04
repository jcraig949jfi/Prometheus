# Research Package 24: Graph Neural Networks on Arithmetic Structures
## For: Google AI Deep Research  
## Priority: MEDIUM — novelty claim for architecture paper

---

## Context

Package 6 (ML on LMFDB survey) confirmed that NOBODY has applied Graph Neural Networks
to the mathematical graph structures in the LMFDB — isogeny graphs, modularity maps,
twist relationships, or Hecke operator graphs. All existing ML on LMFDB uses sequence-
based inputs (1D CNNs on Dirichlet coefficients, PCA on Fourier coefficients, etc.).

Our architecture uses k-NN on zero vectors, which implicitly creates a graph structure.
If we upgrade to GNN-based representation learning on the actual LMFDB graph topology,
that's a confirmed novel contribution. This package maps the landscape.

## Specific Questions

1. **What graph structures exist natively in LMFDB?** List all relationship types:
   isogeny graphs, Hecke correspondences, Galois orbits, twist families, congruence
   relations between modular forms, etc. What are their sizes and densities?

2. **GNNs on mathematical graphs — any work at all?** Not just LMFDB. Has anyone
   used GNNs on Cayley graphs, Bruhat-Tits trees, modular curves, Hecke eigenvalue
   graphs, or any algebraic/arithmetic graph structure?

3. **Node2Vec / GraphSAGE on number-theoretic data?** Any graph embedding approach
   applied to mathematical databases.

4. **What would a GNN learn from isogeny graphs?** Isogeny classes encode deep
   arithmetic equivalences. If we treat each EC as a node, isogenies as edges,
   and zero vectors as node features, what could message-passing learn that
   sequence models can't?

5. **Scalability.** LMFDB has ~3M elliptic curves. How many isogeny edges?
   What graph learning architectures scale to millions of nodes?

6. **The LMFDB "knowledge graph."** Has anyone proposed or built a knowledge
   graph over LMFDB? E.g., linking curves to their modular forms, to their
   Galois representations, to their L-functions as a heterogeneous graph?

## Key Papers
- Kipf, Welling — Graph Convolutional Networks (2017)
- Hamilton, Ying, Leskovec — GraphSAGE (2017)
- Any intersection of GNNs with pure mathematics
- Sutherland — computational isogeny class work
- He et al. — "Machine Learning meets Number Theory" ecosystem
