

Subject: Automated falsification pipeline finds unexplained Frobenius phase–rank correlation (p = 3.5 × 10⁻¹⁰)

  Professor Sarnak,

  I am an independent researcher. I built an automated instrument that tests structural hypotheses across mathematical
  databases using a 14-test falsification battery with a 63.9% kill rate. It is designed to destroy false positives, not
   accumulate them. I am writing because it found results in your territory that survived.

  The instrument rediscovered known structure without being told what to look for:

  The pipeline detected modularity at 31,073/31,073 elliptic curve–modular form pairs in 0.4 seconds, purely from
  L-function coefficient matching. It confirmed Poisson level spacing across all 120 (level, symmetry) pairs in the
  LMFDB's 35,416 rigorously computed Maass forms (KS distance to Poisson: 0.034; to GUE: 0.17). It recovered CM from a
  single behavioral statistic — the zero-frequency of Fourier coefficients — with F1 = 1.00 and a 29-percentage-point
  separation gap, using no algebraic metadata. These serve as calibration: the instrument measures known structure
  correctly before claiming anything new.

  The result I cannot explain:

  For 66,158 genus-2 curves over Q, I computed the Frobenius eigenvalue phases at good primes p ≤ 97 and measured their
  mean resultant length R (a coherence statistic: R = 1 is perfect alignment, R = 0 is uniform). Phase coherence R
  correlates with analytic rank:

  - Rank 0: mean R = 0.046
  - Rank 1: mean R = 0.067
  - Rank 2: mean R = 0.085
  - Rank 3: mean R = 0.108

  Spearman ρ = 0.197, p = 3.5 × 10⁻¹⁰, surviving control for conductor (partial ρ = 0.172, p = 4.75 × 10⁻⁸). Higher-rank
   curves have systematically negative mean trace, shifting the Frobenius constellation toward phase clustering. This is
   a local measurement (eigenvalue geometry at finitely many primes) seeing a global invariant (order of vanishing of
  the L-function at s = 1).

  I do not know why this is true. The correlation is modest but highly significant across the full LMFDB genus-2 corpus.
   It is not explained by conductor, Sato-Tate group, or endomorphism type — it was tested against all of these.

  Additional structural measurements from the pipeline:

  - Three primes (mod 3, 5, 7) suffice to uniquely identify every weight-2 newform in the 17,314-form LMFDB database
  (catastrophic 788× collapse at depth 2, complete singleton rigidity at depth 3)
  - The mod-2 congruence graph for genus-2 curves decomposes into complete cliques following a power law with exponent α
   = 3.19 (R² = 0.97), with a discrete phase transition to perfect matching at mod 3
  - The curvature flow on the mod-5 Hecke congruence graph converges to κ* = 0.73 at iteration 44, perfectly separating
  accidental pairwise congruences (destroyed) from structural triangles (all 27 preserved)

  The full pipeline, data, and 136 investigation scripts are at:
  https://github.com/jcraig949jfi/Prometheus

  I am seeking an arxiv endorsement in math.NT to post these findings. If you or a colleague would be willing, I would
  be grateful.

  James Craig