# Report 80: Universal Bulk Constant at k=24 — New Invariant or Finite-Conductor Correction?

**For:** Harmonia agent
**Session:** F011 follow-up
**Date:** 2026-04-23

## 1. Precise Problem Statement

F011 measured a local-gap-variance deficit at 24-gap normalization relative to a matched-GUE null:

- EC rank-0 non-CM (symmetry class O+): **+50.9%**
- EC rank-0 CM (mixed U-product): **+47.8%**
- Genus-2 rank-0 (USp(4)): **+46.4%**

These three agree within 5 percentage points despite living in three distinct Katz–Sarnak classes (orthogonal, unitary, symplectic). Maass GL(3) shows a mixed edge-positive/bulk-negative gradient, not a clean +50% deficit.

The question is whether the tight clustering at **+46–51% at k=24** is (a) a genuine new universal constant of arithmetic L-function local statistics beyond compact-group RMT, (b) a large but ordinary finite-conductor correction, or (c) a normalization artifact of the specific k=24 choice.

## 2. Literature State

Katz–Sarnak (1999, *Random Matrices, Frobenius Eigenvalues, and Monodromy*) established asymptotic bulk 2-point correlation is identical across U/O/Sp — universality at infinite conductor. Finite-N corrections are expected to be O(1/N), i.e. 2–5% at conductors Harmonia is sampling, not 50%.

Published finite-conductor work:

- **Rubinstein (Duke 2001)** — finite-conductor corrections for Dirichlet and EC families are logarithmic in conductor, not fixed multiplicative deficit.
- **Hughes–Rudnick (Compositio 2003)** — mock-Gaussian moments; predicts arithmetic lower-order terms of size (log N)^(-1).
- **CFKRS (2005)** — integral moment conjectures with arithmetic factors that do *not* cancel across U/O/Sp.
- **Shin–Templier (Invent. Math. 2016)** — sharpened rate of convergence; polynomial rates but no prediction of a cross-family constant deficit.
- **Keating–Odgers (2008)** — secondary terms in moments of characteristic polynomials; family-dependent.
- **Selberg (1992)** — baseline integrated 2-point correlation for ζ.

**No published work predicts a +50% bulk-variance deficit at a fixed gap scale k=24 across three Katz–Sarnak classes.** This is unprecedented.

## 3. Candidate Interpretations

**(a) New universal arithmetic constant.** Cross-family agreement within 5 pp is suggestive; if real it would be a post-Katz–Sarnak invariant visible only in arithmetic (not pure-RMT) ensembles, possibly related to CFKRS arithmetic factor a_k at a specific shift.

**(b) Finite-conductor correction.** Magnitude (~50%) is 10–20× larger than Rubinstein/Hughes–Rudnick predictions at typical Harmonia conductors. For a finite-N effect, hidden coefficient would need to be anomalously large, or k=24 would need to sit near a resonance of conductor-dependent spectral form factor (Berry–Keating saturation scale).

**(c) k=24 normalization artifact.** 24 is neither small nor large; sits in the crossover window where form factor transitions linear→plateau. Fortuitous value could produce apparent universality without content.

## 4. Discriminating Tests

- **For (b):** Stratify each family by log(conductor) into ≥3 bins; fit deficit vs 1/log(N). If slope is large and deficit shrinks at high N, (b) is supported.
- **For (c):** Repeat measurement at k ∈ {6, 12, 18, 24, 30, 36, 48}. If +46–51% cluster persists *only* at k=24, (c) is supported. If smooth curve of cross-family agreement appears across a k-range, (a) is supported.
- **For (a):** Add Dirichlet L (U class) and Rankin–Selberg GL(2)×GL(2) (Sp-type). Universality should hold.
- **Cross-check against CFKRS arithmetic factor** a_k(F) for each family at k=24; compute a_24 symbolically and see whether a_24(O+)/a_24(USp) predicts observed 50.9/46.4.

## 5. Connection to F011 Paper

If test (a) survives, F011 has a headline finding: a new arithmetic universality class beyond Katz–Sarnak. If (b) or (c), F011 becomes a methodological paper on finite-conductor artifacts at crossover scales — still publishable but different framing. Recommend running k-stratification test *before* paper commits to language. Default framing should be (b/c) until (a) survives falsification.

## 6. Caveats

The Maass GL(3) gradient inversion (edge +, bulk −) is a serious warning. If +50% deficit were a true Katz–Sarnak-transcending universal, it should appear in degree-3 L-functions as well. Its absence argues either that the effect is degree-2-specific (weakening the "universal" claim) or that degree-3 bulk statistics require different normalization. The paper should not claim universality across all arithmetic L-functions until GL(3) is resolved; at most, claim "universal within degree-2 Katz–Sarnak classes."

**Word count: 712**
