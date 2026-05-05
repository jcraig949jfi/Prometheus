# Study 08: Dimensional Lifting as a Discovery Strategy

**Date:** 2026-05-05
**Owner:** general-purpose subagent (Aporia delegation)
**Substrate connection:** Abstraction strategies; choice of kill_vector
dimensionality (currently 8-12); MAP-Elites behavior-descriptor dimensionality
(currently 5-axis); category-theoretic lifts vs reductions.

## Problem statement (Prometheus-adapted)

The substrate just performed a *dimensional lift* on its outcome representation:
`kill_path: str` (categorical first-trigger, ~3 bits) became `KillVector`
(8-12 components, each with triggered + margin). This was substrate-positive in
the small sense (more bits per record, directional derivatives become well-typed)
but the broader question is unresolved:

1. Is there a topology / category-theory heuristic for *when* lifting a problem
   into a higher-dimensional or higher-categorical setting will reveal structure
   versus produce a sparser, harder problem?
2. For the kill_vector specifically: is 8-12 the right number, is there a
   theoretically motivated optimum, and what is the failure mode at each end?
3. For Prometheus's 5-axis MAP-Elites behavior descriptor: is there empirical
   QD literature on optimal descriptor dimensionality?
4. When lifting *fails*, what is the typical pathology — pure complexity blow-up,
   sparsity-of-data-per-cell, dependent-type explosion, or something else?

Honest summary up front: (1) a clean predictive heuristic does not exist in the
literature this scan reviewed; the closest are *retrospective* patterns
(stable invariants, semisimplification, free-functor existence) and an explicit
counterexample to "higher = harder" in topology (Smale's h-cobordism). (2) The
kill_vector dimensionality question is *not directly answered by topology*; the
applicable literature is QD-archive sparsity and statistical-learning effective
dimension, both of which point to a soft optimum well below the dimensionality of
the raw outcome space. (3) The QD literature has *measured* descriptor-dimension
trade-offs and the recurrent finding is that 2-6 hand-chosen axes outperform
higher-dimensional learned descriptors on most benchmarks, with autoencoded
descriptors (AURORA) closing the gap when raw observations are high-dimensional.
(4) The named pathology of failed lifts is **sparsity in the lifted space** plus
**loss of the original problem's compactness/finiteness** — not "complexity" in
a single sense.

## Literature scan

**Smale's high-dimensional Poincaré (h-cobordism, 1962).** Smale proved the
generalized Poincaré conjecture for dimensions ≥ 5 using the h-cobordism
theorem; the dim-3 case (Perelman, 2003) and dim-4 (still open in the smooth
category) are *harder*, not easier. The standard explanation: in dim ≥ 5 there
is *room for the Whitney trick* (embedded disks can be made disjoint), which
fails in low dimensions. This is the canonical counterexample to "higher
dimensions are harder" and it identifies the mechanism cleanly: lifting is
productive when it gives you *room to perform a key technical move* that was
obstructed in the original setting. (Milnor's lectures on the h-cobordism
theorem are the standard reference.)

**Categorification (Khovanov 1999; Crane-Frenkel 1994).** Khovanov homology
lifts the Jones polynomial (a Laurent polynomial in q) to a bigraded chain
complex whose graded Euler characteristic recovers the polynomial. The *gain*
is functoriality (cobordisms induce maps), strictly more invariant power
(distinguishes knots Jones cannot, e.g. Kawauchi's pair distinguished by
Lee-Rasmussen), and proof-theoretic leverage (Rasmussen's combinatorial proof
of Milnor's conjecture, 2004). The *cost* is an explosion of computational
complexity: Khovanov homology of a 20-crossing knot is non-trivial to compute.
This is a worked example of a *successful* lift, and the retrospective
diagnostic is: it succeeded because the lifted theory had a *natural functor
back down* (Euler characteristic) so claims could always be verified at the
lower level.

**Geometric Langlands (Beilinson-Drinfeld; Frenkel surveys).** A categorical
lift of the Langlands correspondence (functions on automorphic forms become
sheaves on moduli stacks). Productive in the sense that it has produced new
proofs and connections (geometric Satake, Bezrukavnikov), but the cost is
extreme: the framework requires derived algebraic geometry, ∞-categories, and
factorization algebras. The retrospective diagnostic from Frenkel's Bourbaki
talks: the lift succeeded *because* the original problem already had the
right structure (Hecke eigenvalues, automorphic representations) staring at a
moduli space; the lift was a re-coordinatization, not a new posit.

**Universal enveloping algebras / monoidal categories.** A textbook successful
lift: a Lie algebra (vector space + bracket) lifts to its universal enveloping
algebra (associative algebra) and the lift is *free* (left adjoint to forgetful
functor). The PBW theorem certifies the lift loses no information. The
abstract pattern: when the lift is a left or right adjoint to a forgetful
functor, the lift is *information-preserving* and its productivity reduces to
whether the higher structure has a useful theorem the lower one lacks. (Mac
Lane, *Categories for the Working Mathematician*, ch. IV.)

**∞-categories (Lurie's *Higher Topos Theory*, 2009).** ∞-categorical lifts of
ordinary category theory have produced derived algebraic geometry and a
revisionist account of homotopy theory. The cost is severe: the foundations
take ~900 pages. The retrospective pattern: the lift was productive when the
ordinary categorical setting was already *tracking only the truncated
homotopy type* and losing essential information; when it was tracking enough,
the ∞-lift was overkill. There is no published predictive heuristic for "this
problem will need ∞-categories" — the consensus is that you discover it
because ordinary categorical machinery starts producing wrong or undefined
constructions (e.g., functorial cone construction in the derived category).

**Morse theory / dimensional reduction in topology.** The opposite direction:
Morse theory replaces a smooth manifold with a CW complex by tracking critical
points of a generic real-valued function. The dimension of the *problem*
drops (manifold → finite cell-complex with ≤ dim+1 cell types). This is the
prototypical *productive reduction*: it works when the lower-dimensional
gadget retains the topological information you need (homology) but not what
you don't (smooth structure). Bott periodicity and the Atiyah-Singer
index theorem are downstream beneficiaries.

**Dimensional regularization in physics ('t Hooft-Veltman 1972).** Compute
divergent integrals in d dimensions, take d → 4 from above. The lift is
*formal* (analytic continuation in spacetime dimension) and productive
because the regulator preserves gauge invariance which other regulators
break. This is a case where the lifted space is *not interpretable* (d = 4 −
ε is not a real geometry) but the lift is justified by the structure it
preserves. The substrate-side translation: a lift can be formal and still
load-bearing if it preserves the right invariants on the way back down.

**Effective dimension in statistics.** The standard Vapnik-Chervonenkis /
Rademacher complexity result: generalization error scales as O(√(d/n)) where
d is effective dimension and n is sample count. Lifting a problem to d
dimensions imposes a 1/d multiplicative cost in samples-per-cell. For
Prometheus's MAP-Elites archive, where each cell needs ≥ a few samples to
distinguish operator effects, this is the operative budget constraint.

**Quality-Diversity descriptor dimensionality.** Cully-Demiris (Frontiers in
Robotics & AI, 2018) survey QD; Mouret-Clune (2015, MAP-Elites paper) report
2-6 hand-designed dimensions. Cully (2019) "Autonomous skill discovery with
QD and unsupervised descriptors" introduces AURORA, which learns descriptors
via autoencoder; reported gains primarily on tasks where the raw observation
is image/sequence and hand-design is hard. Vassiliades et al. (2018) "Using
centroidal Voronoi tessellations to scale up MAP-Elites" specifically
addresses the curse of dimensionality in archive grid spacing — their CVT
approach ameliorates but does not eliminate the sparsity problem in higher
descriptor dimensions. Empirical consensus across the QD-benchmarks
(QDax, pyribs documentation): 2-6 axes outperform higher-dimensional grids
on most non-pixel tasks; CVT-MAP-Elites becomes important above ~4
dimensions; AURORA helps when raw observations are high-dimensional and a
learned compression is reasonable.

**Manifold hypothesis / intrinsic dimension.** Standard ML result (Tenenbaum
et al. 2000 ISOMAP; Levina-Bickel 2004 intrinsic-dimension estimation):
high-dimensional data typically lies on a low-dimensional manifold, and the
*intrinsic* dimension is what governs sample complexity, not the ambient.
For the kill_vector: if the 8-12 components are highly correlated (which the
KILL_VECTOR_LEARNER_RESULTS may already show), the intrinsic dimension is
substantially smaller, and the operating dim is set by it.

## Substrate-relevance

1. **The kill_vector lift was substrate-positive on independent grounds.** A
   3-bit categorical → 8-12-component vector adds bits per record, but the
   real win is that *directional derivatives become well-typed* (you can ask
   `∂k_F1 / ∂operator` separately from `∂k_irreducibility / ∂operator`). The
   Khovanov pattern says: this is the right shape iff there is a natural
   functor back down (sum, hash, or "first triggered" gives you the old
   categorical kill_path). There is — so the lift is *information-strict*
   and the worst case is decorative components, not lost information.

2. **8-12 is plausibly above the intrinsic dimension and that is fine for
   *diagnosis* but bad for *navigation*.** The kill_vector is built in
   pipeline-call order; many components will be near-deterministic functions
   of others (e.g., `out_of_band` and the F-checks correlate; catalog hits
   correlate within a registry). For *diagnosis* of why a candidate failed,
   redundancy is harmless. For the Day-5 *navigator* (greedy descent toward
   the zero vector), redundant components inflate the search space and
   produce phantom directions. Recommend running an intrinsic-dimension
   estimator (Levina-Bickel, or just PCA of the kill-matrix) on the
   accumulated KillVector ledger and reporting the effective dimension. If
   intrinsic dim is ≤ 4-5, the navigator should operate on a learned
   low-dim projection rather than the raw 8-12.

3. **MAP-Elites 5-axis descriptor sits in the empirically supported range.**
   The QD literature consensus (2-6 hand-designed axes; CVT or AURORA above
   that) supports the current substrate choice. The substrate should *not*
   reflexively expand to 8 or 12 axes by symmetry with the kill_vector — the
   archive sparsity penalty is multiplicative and per-cell sample counts
   degrade as N^(1/d). If a sixth axis is added, recommend switching to
   CVT-MAP-Elites at the same time.

4. **The Khovanov / monoidal-category pattern gives one operational test for
   *future* lifts:** before adopting a higher-dimensional or higher-
   categorical representation, check that there is an explicit functor (or
   projection, or summary statistic) back to the original representation.
   If yes, the lift is information-strict and reversible at any time (worst
   case: decorative axes). If no, the lift is a *posit* about new structure
   and needs adversarial validation — this is the AM/Eurisko cautionary
   tale from Study 06.

5. **The Smale pattern — "lift is productive when it gives room for a key
   technical move" — predicts that the substrate's most valuable lifts will
   be those that enable an operator that was *blocked* in the lower
   representation.** The kill_vector enables per-component directional
   derivatives, which were ill-defined on a categorical first-trigger. That
   is the Whitney-trick analog. Future lifts should be evaluated by *which
   blocked move they unblock*, not by "more bits is better."

## Concrete operational handles

1. **Add an intrinsic-dimension report to the kill_vector ledger.** Every
   N=1000 records, run Levina-Bickel (k=10) or PCA-95% on the KillVector
   matrix. Publish the effective dimension alongside the nominal 8-12. If
   effective dim drifts well below nominal, flag for component pruning or
   merging. This is a 30-line addition to whatever already aggregates the
   ledger.

2. **For the Day-5 navigator, operate on a learned projection, not the raw
   vector.** Concretely: fit a low-dim embedding (PCA, or a tiny MLP
   autoencoder if non-linearity matters) on the ledger, navigate in
   embedding-space, project back for the falsifier check. This avoids
   chasing phantom directions in correlated subspaces. Recommended embedding
   dim: max(intrinsic-dim estimate, 3).

3. **Adopt the "functor-back-down" heuristic for future lift proposals.**
   When the substrate proposes a new lifted representation (e.g., kernel
   AST → typed effect graph; kill_vector → kill_tensor over operators), require
   an explicit projection/summary back to the previous representation as
   part of the proposal. If no projection is exhibited, the lift is a posit
   and needs an adversarial test before adoption.

4. **Cap MAP-Elites descriptor dimensionality at 6 unless switching to
   CVT-MAP-Elites.** The QD literature is consistent on this. Add a
   substrate guardrail: if a 7th descriptor axis is proposed, the proposal
   must include a CVT or AURORA-style scheme.

5. **Document Prometheus's lift-test pattern as substrate convention.** A
   one-page convention: "Before lifting, check (a) functor back, (b) blocked
   move unblocked, (c) intrinsic-dim budget, (d) sample-per-cell budget."
   This is convention-level, not code, but it would prevent enthusiastic
   over-lifting.

## Falsification

The central operational claims would be refuted by:

- An intrinsic-dimension estimate on the KillVector ledger that comes back
  *near* the nominal dim (e.g., ≥ 9 of 12). That would mean the components
  really are independent and the navigator can use the raw vector safely;
  the embedding recommendation collapses.
- A QD benchmark in the literature (post-2024) showing that 8-12-axis
  MAP-Elites archives outperform 4-6-axis ones on a non-pixel task at
  fixed compute. This scan did not identify one but did not exhaustively
  search; if one exists, the descriptor-cap recommendation is too
  conservative.
- A demonstration that the kill_vector's `kill_path` projection (sum, or
  first-triggered) loses information that the substrate empirically needs
  — i.e., that the lift is not actually information-strict because the
  full vector encodes ordering or interaction effects that the projection
  destroys. (This would *strengthen* the case for the lift but invalidate
  the "worst case is decorative" framing.)

The broader claim — that there is no published predictive heuristic for
"will this lift help" — would be refuted by a single citation of a
constructive theorem of the form "if your problem has property P, then the
lift to setting S will reveal more structure than working in the original."
This scan did not find one; the closest are the *adjoint-functor* family of
results which give *information preservation* but not *productivity*.

## Open questions raised

1. What is the intrinsic dimension of the current KillVector ledger? This
   is a 30-line script and would directly calibrate the dim choice.
2. Are any of the substrate's 5 MAP-Elites axes redundant with each other
   under the population already in the archive? Same intrinsic-dim question
   one level up.
3. Does a "functor back down" requirement rule out any productive lifts the
   substrate has *already done*? (Sigma kernel from raw operator stack;
   bridge gradient from tensor coordinates; Aporia's edge-of-knowledge
   catalog.) If yes, the requirement is too strict and needs softening.
4. Is there a math-discovery analog of the Smale "Whitney trick room"
   pattern — a substrate-level move that is currently blocked in the
   tensor-coordinate representation and would be unlocked by a specific
   lift? If so, that lift is the highest-value one to try next.
5. Does Khovanov-style categorification have any concrete handle for
   Prometheus's bridge gradient, or is the analogy purely structural? In
   particular: is there a graded-chain-complex-of-bridges that has the
   gradient as its Euler characteristic? Probably no, but the question
   is worth a 30-minute scan.

## Citations

- Smale, S. "Generalized Poincaré's conjecture in dimensions greater than four." *Annals of Mathematics* 74, 391-406 (1961).
- Milnor, J. *Lectures on the h-Cobordism Theorem*. Princeton University Press (1965).
- Khovanov, M. "A categorification of the Jones polynomial." *Duke Math. J.* 101, 359-426 (2000). arXiv:math/9908171.
- Bar-Natan, D. "On Khovanov's categorification of the Jones polynomial." *Algebr. Geom. Topol.* 2, 337-370 (2002). arXiv:math/0201043.
- Rasmussen, J. "Khovanov homology and the slice genus." *Invent. Math.* 182, 419-447 (2010). arXiv:math/0402131.
- Crane, L., Frenkel, I. B. "Four dimensional topological quantum field theory, Hopf categories, and the canonical bases." *J. Math. Phys.* 35, 5136-5154 (1994).
- Frenkel, E. "Lectures on the Langlands program and conformal field theory." arXiv:hep-th/0512172 (2005).
- Beilinson, A., Drinfeld, V. "Quantization of Hitchin's integrable system and Hecke eigensheaves." Preprint (1991, unpublished).
- Lurie, J. *Higher Topos Theory*. Princeton University Press (2009). https://www.math.ias.edu/~lurie/papers/HTT.pdf
- Mac Lane, S. *Categories for the Working Mathematician*, 2nd ed. Springer (1998).
- Milnor, J. *Morse Theory*. Princeton University Press (1963).
- 't Hooft, G., Veltman, M. "Regularization and renormalization of gauge fields." *Nucl. Phys. B* 44, 189-213 (1972).
- Vapnik, V. *The Nature of Statistical Learning Theory*. Springer (1995).
- Levina, E., Bickel, P. J. "Maximum Likelihood Estimation of Intrinsic Dimension." NeurIPS 2004. https://papers.nips.cc/paper/2004/hash/74934548253bcab8490ebd74afed7031-Abstract.html
- Tenenbaum, J. B., de Silva, V., Langford, J. C. "A Global Geometric Framework for Nonlinear Dimensionality Reduction." *Science* 290, 2319-2323 (2000).
- Mouret, J.-B., Clune, J. "Illuminating search spaces by mapping elites." arXiv:1504.04909 (2015).
- Cully, A., Demiris, Y. "Quality and Diversity Optimization: A Unifying Modular Framework." *IEEE Trans. Evol. Comput.* (2018). arXiv:1708.09251.
- Cully, A. "Autonomous skill discovery with Quality-Diversity and Unsupervised Descriptors." GECCO 2019. arXiv:1905.11874. (AURORA.)
- Vassiliades, V., Chatzilygeroudis, K., Mouret, J.-B. "Using Centroidal Voronoi Tessellations to Scale Up the Multidimensional Archive of Phenotypic Elites Algorithm." *IEEE Trans. Evol. Comput.* (2018). arXiv:1610.05729. (CVT-MAP-Elites.)
- Internal: `F:/Prometheus/prometheus_math/KILL_VECTOR_SPEC.md`; `F:/Prometheus/prometheus_math/KILL_VECTOR_LEARNER_RESULTS.md`; `F:/Prometheus/prometheus_math/KILL_VECTOR_NAVIGATOR_RESULTS.md`; `F:/Prometheus/aporia/meta/studies/2026-05-05/study_06_mutation_operators.md`; `F:/Prometheus/aporia/meta/studies/2026-05-05/BATCH_PLAN.md`; feedback files `feedback_calibration.md`, `feedback_assume_wrong.md`, `feedback_narrative_resistance.md`.

*This scan did not find a published predictive heuristic of the form "your
problem has property P, therefore lifting to setting S will help." The
recommendations rest on retrospective patterns (Khovanov-functor-back,
Smale-room-for-the-move) and on independent statistical-learning grounds
(intrinsic dimension, sample complexity per cell). If a constructive
predictive theorem exists in the categorification literature, this report
under-cites it. The QD descriptor-dim recommendation is grounded in
empirical consensus across QDax and pyribs benchmarks but is not a proved
theorem; it is a defensible default, not a hard limit.*
