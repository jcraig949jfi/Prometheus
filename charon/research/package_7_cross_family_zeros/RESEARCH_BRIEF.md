# Research Package 7: Cross-Family Zero Comparison
## Priority: HIGH — validates our cross-type search approach

---

## Research Question

Has anyone compared L-function zero distributions ACROSS different families of arithmetic objects (not within a single family)? For example: comparing elliptic curve zeros to modular form zeros, or to number field zeros, or to Artin representation zeros — as a geometric or metric comparison?

## Context

Our system builds a single k-NN search space where elliptic curves, modular forms, and genus-2 curves coexist, with distances computed from their zero vectors. The council raised a valid concern: different object types have different Katz-Sarnak symmetry types (orthogonal, symplectic, unitary), so cross-type Euclidean distances are mixing objects from different random matrix ensembles.

## Specific Questions

1. Has anyone formally defined a distance metric between L-functions from different families that accounts for different symmetry types? Something like a "symmetry-normalized distance"?

2. The Selberg class provides a unified framework for L-functions. Has anyone used the Selberg class axioms to define a metric space on L-functions that respects the degree and conductor normalization?

3. Cross-family zero comparison: are there papers that explicitly plot or compare the zero distributions of (say) an elliptic curve L-function against a Dedekind zeta function, or against a symmetric-square L-function? Not statistical ensemble comparisons — individual object-to-object comparisons?

4. The "arithmetic equivalence" problem: number fields with the same Dedekind zeta function but different arithmetic. Has anyone studied this via zero-vector similarity as opposed to coefficient comparison?

5. Is there a concept of "zero-space embedding" in the analytic number theory literature — any formalization of treating zeros as coordinates for a geometric space?

## Key Starting Papers
- Selberg — axioms for the Selberg class
- Conrey, Farmer — "Mean values of L-functions and symmetry" (2000)
- Booker — "Numerical tests of modularity" (2006)
- Farmer, Koutsoliotas, Lemurell — "Varieties via their L-functions" (2019)
- Any work connecting L-function zeros across degree boundaries
