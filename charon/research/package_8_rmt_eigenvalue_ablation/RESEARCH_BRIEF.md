# Research Package 8: Random Matrix Theory — Eigenvalue Ablation
## Priority: MEDIUM-HIGH — theoretical grounding for our core finding

---

## Research Question

In random matrix theory (RMT), if you sample eigenvalues from GOE, GUE, and GSE ensembles and try to classify which ensemble a sample came from, does REMOVING the smallest eigenvalue improve classification accuracy? Is there an RMT analogue to our finding that removing the first L-function zero improves rank clustering?

## Context

We found that L-function zero vectors with the first zero removed cluster better by rank (ARI=0.5486) than with all zeros included (ARI=0.5456). Using only zeros 5-19 gives the best result (ARI=0.5548). The first zero, which is the most "structured" (it encodes rank via order of vanishing), actually HURTS the geometric clustering.

In RMT, the smallest eigenvalue has special statistics (Tracy-Widom distribution) that differ from the bulk. If removing it also improves ensemble classification in RMT, our finding has a clean theoretical explanation: the smallest eigenvalue/zero introduces classification noise because its distribution is dominated by the specific symmetry constraint (vanishing order) rather than the global ensemble structure.

## Specific Questions

1. For finite-N random matrices from GOE vs GUE vs GSE: if you build feature vectors from the N smallest eigenvalues and classify by ensemble, does removing the smallest eigenvalue improve accuracy?

2. The Tracy-Widom distribution governs the largest eigenvalue statistics. Is there analogous work on the SMALLEST eigenvalue and its role in ensemble discrimination?

3. "Level repulsion" differs between GOE, GUE, GSE in systematic ways. Does this repulsion signature concentrate in the bulk of the spectrum or at the edges? If bulk: our finding that higher zeros (which sample the bulk) classify better is explained.

4. In the Katz-Sarnak random matrix model for L-function zeros, the first zero is the most conductor-dependent (scaling as ~1/log(N)). Are the higher zeros less conductor-dependent and therefore more "universal" within a family? Would this predict that higher zeros are better family classifiers?

5. Any work on "optimal subset selection" of eigenvalues/zeros for ensemble classification — choosing which eigenvalues carry the most discriminative information?

## Key Starting Papers
- Tracy, Widom — distributions for largest eigenvalue (1994, 1996)
- Katz, Sarnak — "Random Matrices, Frobenius Eigenvalues, and Monodromy" (1999)
- Forrester — "Log-Gases and Random Matrices" (2010) — comprehensive reference
- Mezzadri, Snaith — "Recent Perspectives in Random Matrix Theory and Number Theory" (2005)
