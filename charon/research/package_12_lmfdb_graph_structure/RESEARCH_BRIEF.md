# Research Package 12: LMFDB Relationship Graph Structure
## Priority: MEDIUM — validates our graph layer and sparsity finding

---

## Research Question

Has anyone studied the connectivity structure of the LMFDB known-relationship network? We found 62,234 connected components for 133,223 nodes. Is this known? Is it studied? Does the graph structure have a name or a theory?

## Context

Our relationship graph has three edge types: isogeny (EC↔EC), modularity (EC↔MF), and twist (MF↔MF). The graph is extremely sparse — 156K edges, 62K components, largest component 192 nodes. The council raised the valid concern that our "orthogonality" finding (zeros vs graph, rho=0.04) might be an artifact of this sparsity.

## Specific Questions

1. Has anyone computed the connected components of the LMFDB relationship graph? Is the 62K number (for conductor ≤ 5000) consistent with what's expected?

2. As conductor increases, does the graph get denser? Is there a scaling law for the number of connected components as a function of conductor range?

3. The "isogeny graph" of elliptic curves — has anyone studied its spectral properties? Eigenvalues of the adjacency matrix? Expander properties?

4. The "twist graph" of modular forms — is it studied as a graph-theoretic object? Does it have known structural properties?

5. Ramanujan graphs arise naturally in number theory. Is the LMFDB relationship graph related to any Ramanujan graph construction?

6. Has anyone proposed using graph-theoretic properties (centrality, clustering coefficient, community structure) of the LMFDB graph to discover arithmetic structure?

7. The "graph of correspondences" — in the Langlands program literature, is there a formal graph-theoretic framework for the known correspondences? Or is it always treated as isolated theorems rather than a network?

## Key Starting Points
- LMFDB infrastructure papers
- Cremona — elliptic curve database methodology
- Any papers on "isogeny graphs" or "isogeny volcanoes"
- Sutherland — computational aspects of isogeny graphs
- Any graph-theoretic number theory papers
