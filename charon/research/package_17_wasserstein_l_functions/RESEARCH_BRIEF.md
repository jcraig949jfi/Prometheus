# Research Package 17: Wasserstein Distance on L-Function Zeros
## For: Google AI Deep Research
## Priority: HIGH — potential publishable architecture contribution

---

## Context

We built a cross-family k-NN search space using L-function zeros as coordinates. Our
zero-vector distance metric is currently naive Euclidean distance between Katz-Sarnak
normalized zero sequences. Four independent research reviews identified this as a
fundamental vulnerability: raw Euclidean distance mixes symmetry-type effects with
genuine arithmetic structure.

Gemini's Package 7 research identified Wasserstein distance (Earth Mover's Distance)
as the theoretically correct metric for cross-family zero comparison. The idea:
measure each object's empirical zero distribution against its expected RMT baseline,
then compare the RESIDUALS. This strips symmetry-type contamination.

Package 6 confirmed that NO formal L-function distance metric exists in the literature
beyond naive coefficient comparison. If Wasserstein-on-zeros is genuinely novel, it's
a publishable contribution to computational number theory.

## Specific Questions

1. **Has anyone applied Wasserstein distance (or any optimal transport metric) to
   compare L-function zero distributions?** Between individual L-functions, not
   between families. Any application of Earth Mover's Distance to number-theoretic
   spectral data.

2. **Wasserstein distance in Random Matrix Theory.** Has optimal transport been used
   to compare eigenvalue distributions of different matrix ensembles? E.g., measuring
   the distance between a GOE sample and a GUE sample using Wasserstein rather than
   KL divergence or KS statistic?

3. **Symmetry-normalized residuals.** Our proposed approach:
   - Compute empirical measure mu_F from the first N zeros of L-function F
   - Compute theoretical baseline nu_G from the RMT 1-level density for symmetry type G
   - The "residual" is W_1(mu_F, nu_G) — the Wasserstein distance from theory
   - Cross-family distance between objects A and B is the distance between their residuals
   Has anything like this been proposed or implemented?

4. **Alternative distance metrics on spectral data.** Beyond Wasserstein, what metrics
   are used in spectral theory for comparing eigenvalue distributions?
   - Kolmogorov-Smirnov distance on CDFs of spacings?
   - Levy-Prokhorov metric?
   - Fisher-Rao metric on the statistical manifold of spacing distributions?
   - Hausdorff distance on zero sets?
   Which is most appropriate for the finite-sample, cross-family case?

5. **Computational tractability.** For 134,000+ objects with 20 zeros each, can W_1
   be computed efficiently? What's the complexity? Are there approximations (e.g.,
   sliced Wasserstein) that scale better?

6. **The Selberg class as a metric space.** Has anyone formally treated the Selberg
   class as a metric space with a topology derived from zero distributions? Steuding
   studied value distribution using uniform convergence metrics. Is there work on
   metrics derived specifically from the zeros (not the values) of Selberg class functions?

## Key Papers to Start From

- Villani — "Optimal Transport: Old and New" (2009) (foundations)
- Peyre — "Computational Optimal Transport" (2019) (algorithms)
- Any application of Wasserstein distance to eigenvalue distributions
- Steuding — "Value-distribution of L-functions" (Selberg class topology)
- Conrey, Farmer — "Mean values of L-functions and symmetry" (2000)
- Package 7 results (cross-family zero distributions report)

## What Outcome Helps Us

- If nobody has used Wasserstein on L-function zeros: strong novelty claim for our
  architecture. We implement it and publish.
- If someone has used it: we cite them and extend to the cross-family case with
  symmetry normalization.
- If a better metric exists (e.g., Fisher-Rao on spacing distributions): we adopt
  that instead and cite the theoretical justification.
