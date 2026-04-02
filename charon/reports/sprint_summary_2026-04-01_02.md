# Charon Sprint Summary: April 1-2, 2026
## Two Days, Three Kills, One Foundation

### What was built
- 133K objects ingested across three types (EC, MF, genus-2)
- Two representations tested: Dirichlet (killed), zeros (validated)
- One graph built (396K edges), proven orthogonal to zeros (rho=0.04)
- One disagreement atlas (119K objects classified into 4 types)
- Full audit trail with pre-registered thresholds and methodology document

### What was killed
1. **Dirichlet coefficients** — binary hash, no geometry. ARI=0.008. Dead in 30 minutes.
2. **The grand correspondence claim** — zeros encode rank, not correspondence. Useful search tool, not discovery engine.
3. **The paramodular interpretation of the 163** — genus-2 curves are NOT zero-proximate to these forms. Character/weight artifact, not functorial descent.

### What survived
- **Zero coordinate system** — continuous rank-aware geometry. ARI=0.55, survives conductor regression. 100% bridge recovery via raw k-NN.
- **Three-layer architecture** — zeros/graph/Dirichlet, each with distinct purpose.
- **The pipeline itself** — genus-2 curves entered through the same door with zero schema changes.
- **Murmurations** — independently reproduced in our data (r = -0.64 to -0.84).

### What was learned
- Dim-2 is special (10.7% EC-proximate vs 0.8% for dim-3, 0% for dim-5+)
- Non-trivial character amplifies EC-proximity 3.3x
- 62K connected components is the structure of the Langlands program at this scale, not a data gap
- Zeros and graph are orthogonal — genuinely independent axes of arithmetic structure
- No embedding adds value over raw vector search on zeros

### The honest framing
Charon is a rank-aware arithmetic search system, not a correspondence discovery engine.
The zeros see rank. The graph sees relationships. Neither sees the other's structure.
The architecture generalizes to new object types without redesign.
The finding machine works, tells the truth, and documents every receipt.

### Sprint statistics
- Objects ingested: 134,475 (31K EC + 102K MF + 1.3K genus-2)
- Tests run: 16 (5 zero battery + 4 Dirichlet battery + 2 kill tests + 3 investigations + 1 genus-2 + 1 audit)
- Bugs found and fixed: 10
- LMFDB queries: ~250K
- Total compute time: ~12 hours (dominated by ingestion)
- False claims published: 0
