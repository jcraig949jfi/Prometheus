# Study 07: Invariants as Discovery Anchors

**Date:** 2026-05-05
**Owner:** general-purpose subagent (Aporia delegation)
**Substrate connection:** The 4 canonicalizer subclasses {group_quotient, partition_refinement, ideal_reduction, variety_fingerprint} are the load-bearing typology for Ergon's behavior descriptor and for residual classification; this study tests whether they cover the documented "kinds of invariants" and whether invariant-discovery itself is a substrate primitive worth encoding.

## Problem statement (Prometheus-adapted)

Prometheus uses invariants in two distinct ways:

1. **As axes of the MAP-Elites archive.** `evaluate_canonicalizer_subclass` projects every candidate into one of 4 buckets so that the archive maintains diversity over invariant *kind*, not just over invariant *value*.
2. **As a residual classifier.** A residual is "signal-class" iff its surviving sub-population has a non-trivial classification under the same 4-subclass taxonomy (per Techne's 2026-05-02 spec). This is the mechanical signal-vs-noise gate.

Both uses assume the 4-subclass taxonomy is a defensible covering of "the kinds of invariants mathematicians actually use." If the taxonomy is short by a major class, the descriptor degenerates and the residual classifier produces false negatives.

The honest summary up front: (1) the 4-subclass taxonomy maps cleanly onto the *computed* invariants of the equivalence-class-of-objects literature (group actions, equivalence relations, quotient rings, scheme-theoretic invariants) but is short by at least two documented classes — *cohomological* (functorial, derived, characteristic-class-style) and *spectral / dynamical* (eigenvalue / zeta-function / dimensional). (2) Automatic discovery of *new* invariants is largely unsolved; Khovanov-style categorification, Donaldson-style gauge theory, and Vassiliev-style singularity perturbation are all manual. The closest algorithmic analog is *learned equivariant features* (Cohen et al., GDL), which are not the same thing. (3) A weak heuristic exists: invariants that survive a known *coincidence* (Casson handles, exotic R⁴, Mostow rigidity threshold) are the productive ones. (4) The substrate-relevant difference between *computing a known invariant* and *discovering a new one* is the difference between a registry lookup and an open-ended search; the substrate currently does only the former.

## Literature scan

**The invariant-as-anchor pattern, documented explicitly.** Atiyah's "How Research is Carried Out" (1974, reprinted in *Collected Works* vol. 1) and Thurston's "On Proof and Progress in Mathematics" (*BAMS* 30, 1994, arXiv:math/9404236) both name invariants as the discovery substrate of geometry / topology. Thurston explicitly: "the most useful invariants are those that distinguish examples we already care about distinguishing." The substrate-relevant version is calibration-by-known-distinction.

**Cohomology as the canonical functorial invariant.** Eilenberg-Steenrod axioms (*Foundations of Algebraic Topology*, 1952) characterize ordinary (co)homology by 4 axioms (homotopy, exactness, excision, dimension). Generalized cohomology theories drop the dimension axiom and gain K-theory, cobordism, etc. (Adams, *Stable Homotopy and Generalised Homology*, 1974). Characteristic classes (Stiefel-Whitney, Chern, Pontryagin, Euler) live in cohomology and are the canonical "obstruction-theoretic" invariants of bundles (Milnor & Stasheff, *Characteristic Classes*, 1974). **None of these collapses cleanly into Prometheus's 4 subclasses.** They are *functors*, not partitions or quotients; the relevant operation is "pull back along a map," not "reduce modulo an ideal."

**Tor / Ext and derived invariants.** Cartan-Eilenberg (*Homological Algebra*, 1956) — Tor and Ext are bifunctors measuring failure of tensor / Hom to preserve exactness; they detect non-flatness, non-projectivity, extension classes, etc. Verdier's derived categories (*Astérisque* 239, 1996) take this further: invariants live not on objects but on chain complexes up to quasi-isomorphism. **This is the cleanest example of an invariant class Prometheus's taxonomy does not name.** `ideal_reduction` is the closest Prometheus subclass but conflates "reduce mod I" with "compute Tor over R."

**Galois / arithmetic invariants.** Galois groups, conductors, regulators, Tate-Shafarevich, Selmer ranks, p-adic L-functions (Mazur-Wiles 1984; Kato 2004; Skinner-Urban 2014). These show up across Charon's existing work (`charon/scripts/f011_*`, BSD audit, etc.). They are *spectra-of-an-action* invariants: eigenvalues of Frobenius, dimensions of cohomology groups attached to motives. The Prometheus taxonomy nominally accommodates these under `group_quotient` (the Galois group is a quotient) but loses the *spectral* dimension that does the actual discovery work.

**Knot polynomials and categorification.** Alexander (1928), Jones (1985, *BAMS* 12), HOMFLY-PT (1985), Kauffman bracket (1987). Khovanov homology (Khovanov, *Duke Math J.* 101, 2000, arXiv:math/9908171) categorifies the Jones polynomial: replaces a polynomial invariant with a graded chain complex whose Euler characteristic recovers the polynomial. Categorification is *the* documented procedure for inventing a new invariant from an old one — but it is manual and creative, not algorithmic. Bar-Natan's local Khovanov homology (Bar-Natan, *Geom. Topol.* 9, 2005, arXiv:math/0410495) and Lee homology (Lee, *Adv. Math.* 197, 2005, arXiv:math/0210213) extend the construction; Rasmussen's s-invariant gives slice-genus bounds (Rasmussen, *Invent. Math.* 182, 2010, arXiv:math/0402131). This is a *family* of new invariants generated by a single procedural insight.

**Donaldson, Seiberg-Witten, gauge-theoretic invariants.** Donaldson's polynomial invariants (Donaldson, *Topology* 29, 1990) come from instanton moduli spaces; Seiberg-Witten invariants (Witten, *Math. Res. Lett.* 1, 1994, arXiv:hep-th/9411102) replaced them with a vastly simpler equation. **Falsification example:** Donaldson invariants were initially read as the "right" 4-manifold invariants until Seiberg-Witten showed the same distinctions came from a 1-line equation. The lesson: invariants that are computationally heavy may be reframings of lighter ones not yet found.

**Vassiliev / finite-type invariants.** Vassiliev (*Adv. Sov. Math.* 1, 1990) produced a filtration of the space of knot invariants by singularity-theoretic perturbation. Kontsevich's integral (*Adv. Sov. Math.* 16, 1993) gives a universal Vassiliev invariant via formal iterated integrals. This is a rare case where a *systematic procedure* generates an entire infinite family of invariants — not a single new one.

**The "false invariant" / falsification literature.** Casson handles (Freedman, *J. Diff. Geom.* 17, 1982): smooth-vs-topological 4-manifold distinctions vanish at the topological level. Exotic R⁴ (Donaldson + Freedman, 1982): infinitely many smooth structures on R⁴, none distinguishable by classical invariants. Mostow rigidity (Mostow, *Publ. IHES* 34, 1968): hyperbolic structure on closed 3-manifolds of dimension ≥3 is determined by fundamental group; in dimension 2 it is not. Margulis arithmeticity (Margulis, *Discrete Subgroups of Semisimple Lie Groups*, 1991): all higher-rank lattices are arithmetic; rank-1 lattices need not be. **The pattern: invariants tied to dimension thresholds. The interesting math lives at the threshold.**

**Algorithmic invariant discovery, what exists.** Geometric Deep Learning (Bronstein et al., 2021, arXiv:2104.13478) provides a *framework* for learning equivariant features under specified group actions, but the group is given; the features are not a new invariant of the *problem* but a new representation of a *known* symmetry. Davies et al. ("Advancing mathematics by guiding human intuition with AI," *Nature* 600, 2021) uses saliency over learned features to *suggest* invariants for human verification (knot signature ≈ promotional Cromwell move count, permutation symmetric-group invariants). This is not autonomous invariant discovery; it is hypothesis suggestion with a human in the loop. AlphaFold's pair representation (Jumper et al., *Nature* 596, 2021) is sometimes called an "implicit" learned invariant, but only in the structural-biology sense. **No system in the published literature autonomously proposes, tests, and promotes a new mathematical invariant.** The closest existence proof is Davies et al., which still requires Marc Lackenby to recognize that the suggested feature is a known invariant.

**Equivariant / group-theoretic invariant theory (classical).** Hilbert's Basis Theorem and his Finiteness Theorem (1890) bound invariants of reductive group actions; Mumford's GIT (*Geometric Invariant Theory*, 1965) gives the modern moduli-space framework. Computer-algebra packages (Singular, Magma, Macaulay2) compute invariant rings *given the group*. This is the registry-lookup case: known group, known machinery, mechanical computation.

## Substrate-relevance

Three load-bearing connections:

1. **The 4-subclass taxonomy maps the equivalence-class-of-objects axis cleanly but misses the functorial axis.** `group_quotient` (orbit space), `partition_refinement` (equivalence classes finer than a known one), `ideal_reduction` (mod-I quotients), `variety_fingerprint` (scheme-theoretic invariants of a variety) are all *single-object-with-action* invariants. Cohomology, Tor/Ext, characteristic classes, and Galois cohomology are *functorial* invariants — they live on a category, not on an object. The taxonomy as currently implemented will route Ext groups, Stiefel-Whitney classes, and Selmer ranks into the wrong cell or into none at all.

2. **The residual classifier currently uses the taxonomy as a 4-way mechanical discriminator** (`techne/TECHNE_SESSION_2026-05-02.md` lines 285-290). If the taxonomy is short by a major class, surviving sub-populations of *cohomological* type will be misclassified as residual-noise rather than residual-signal, and Ergon will drop genuinely interesting candidates. This is a falsifiable failure mode the substrate can test for.

3. **The substrate does not currently distinguish "computing a known invariant on a new object" from "discovering a new invariant on known objects."** The arsenal_meta table at `prometheus_math.arsenal_meta` lists 85 typed callables; `equivalence_class` tags route each to one of the 4 subclasses. This is registry lookup. Open-ended invariant *discovery* — the Khovanov / Donaldson / Vassiliev pattern — has no representation. Whether the substrate should add it is an architectural decision, not a typology question.

## Concrete operational handles

1. **Add a fifth subclass: `cohomological_functor`.** Covers cohomology (ordinary and generalized), Tor/Ext, characteristic classes, Galois cohomology, derived-category invariants. The diagnostic: the invariant takes an object *and a coefficient system* (or a category morphism) as input. Implementation: extend `evaluate_canonicalizer_subclass` to recognize the functorial signature; add a corresponding `equivalence_class` value in arsenal_meta. Cost: one descriptor-axis bin and a registry update.

2. **Consider a sixth: `spectral_dynamical`.** Covers eigenvalues of Frobenius, zeta-function zeros, Lyapunov exponents, dimension-theoretic invariants (Hausdorff, box-counting, Minkowski). These are spectra-of-an-action-or-flow invariants. They are currently absorbed (incorrectly) under `variety_fingerprint`. Whether to split is a calibration question — count how many existing arsenal_meta entries currently mis-route into `variety_fingerprint` and decide based on the empirical frequency, not on principle.

3. **Add a hot-swap candidate for canonicalizer_subclass to `descriptor_config.toml`.** Per Ergon's hot-swap protocol (v5 §6.2), if any axis exceeds 70% concentration the axis must swap. Inspection of seed=42 / 1K eps already shows `variety_fingerprint` taking 24/46 cells (52%, per `roles/Ergon/SESSION_JOURNAL_20260504.md` line 481). Pre-specify `cohomological_functor` (or an entropy-binned axis) as the swap candidate so the protocol fires deterministically when the threshold is crossed.

4. **Encode the dimension-threshold heuristic as a CLAIM-suggesting prior, not as substrate machinery.** Mostow / Margulis / Casson all point to *threshold dimensions* as productive territory. This is a search-space prior, not a kernel primitive — surface it as a sampling weight in Aporia's open-question selection, not as a Sigma opcode.

5. **Do not yet build "invariant discovery" as a substrate primitive.** The literature offers no algorithmic precedent that has worked autonomously. Davies et al. with Lackenby is the existence proof, and it required a human topologist. Until Prometheus has either (a) a domain expert in residence or (b) a calibrated benchmark of "invariants to be discovered," this is an investment that almost certainly fails to recoup its cost. Track instead "did the substrate independently rediscover a known invariant?" as a calibration anchor.

## Falsification

The central claim of this study is *the 4-subclass taxonomy is short by at least one major class (cohomological/functorial) and possibly two (spectral/dynamical), and adding them is a low-cost upgrade that improves both archive diversity and residual classification accuracy*.

This claim is refuted if any of the following is true:

- A complete enumeration of the arsenal_meta table shows >95% of entries route cleanly into one of the existing 4 subclasses with no functorial misclassifications.
- Empirical archive coverage stays balanced under the 4-subclass descriptor across ≥10 production runs with diverse seeds (no axis exceeds 60% in any cell), indicating the existing taxonomy already separates production candidates without the proposed additions.
- An A/B test comparing 4-subclass vs 5-subclass descriptor on the same kill-battery shows no improvement in `n_substrate_passed` or in archive entropy.
- The cohomological-functor diagnostic (object + coefficient system as joint input) collapses in practice to one of the 4 existing diagnostics — i.e., the proposed extra axis turns out to be definitionally redundant with `group_quotient` (Galois cohomology = invariants of a Galois-group quotient action).

## Open questions raised

1. Where is the precise boundary between `group_quotient` and `cohomological_functor`? Galois cohomology is both a quotient and a derived functor; the substrate needs a tie-breaking rule.
2. Is "spectral / dynamical" actually a clean class, or is it three classes (analytic spectra, zeta zeros, dimension-theoretic) that should be separated?
3. Does Davies et al.'s saliency-suggestion approach generalize to a substrate where the human is replaced by a battery of falsification tests? Specifically: can Aporia's literature scan + Charon's null-protocol + Ergon's MAP-Elites jointly act as the "Lackenby" in the loop, or does autonomous invariant discovery require a class of capability the current substrate lacks?
4. The 4 subclasses are listed in `canonicalizer.md` (referenced in the glossary at `aporia/notebooklm_bundles/ergon_learner/09_glossary.md`); this study did not locate the spec file directly. Does the canonicalizer.md spec already address the cohomological / spectral gaps and reject them on principle? If so, the principle should be made explicit and falsifiable.
5. Is "invariant discovery" actually one task or two? Categorification (Khovanov) lifts an existing invariant to a higher structure; gauge theory (Donaldson) builds a new invariant from physics. The two procedures share almost no machinery.

## Citations

- Eilenberg, S., & Steenrod, N. (1952). *Foundations of Algebraic Topology*. Princeton.
- Adams, J. F. (1974). *Stable Homotopy and Generalised Homology*. Chicago Lectures.
- Milnor, J., & Stasheff, J. (1974). *Characteristic Classes*. Annals of Math Studies 76.
- Cartan, H., & Eilenberg, S. (1956). *Homological Algebra*. Princeton.
- Verdier, J.-L. (1996). *Des catégories dérivées des catégories abéliennes*. Astérisque 239.
- Atiyah, M. (1974). "How Research is Carried Out." Reprinted in *Collected Works*, vol. 1.
- Thurston, W. P. (1994). "On Proof and Progress in Mathematics." *BAMS* 30(2):161-177. arXiv:math/9404236.
- Khovanov, M. (2000). "A categorification of the Jones polynomial." *Duke Math J.* 101(3):359-426. arXiv:math/9908171.
- Bar-Natan, D. (2005). "Khovanov's homology for tangles and cobordisms." *Geom. Topol.* 9:1443-1499. arXiv:math/0410495.
- Lee, E. S. (2005). "An endomorphism of the Khovanov invariant." *Adv. Math.* 197(2):554-586. arXiv:math/0210213.
- Rasmussen, J. (2010). "Khovanov homology and the slice genus." *Invent. Math.* 182(2):419-447. arXiv:math/0402131.
- Donaldson, S. K. (1990). "Polynomial invariants for smooth four-manifolds." *Topology* 29(3):257-315.
- Witten, E. (1994). "Monopoles and four-manifolds." *Math. Res. Lett.* 1(6):769-796. arXiv:hep-th/9411102.
- Vassiliev, V. A. (1990). "Cohomology of knot spaces." *Adv. Soviet Math.* 1.
- Kontsevich, M. (1993). "Vassiliev's knot invariants." *Adv. Soviet Math.* 16:137-150.
- Freedman, M. (1982). "The topology of four-dimensional manifolds." *J. Diff. Geom.* 17(3):357-453.
- Mostow, G. D. (1968). "Quasi-conformal mappings in n-space and the rigidity of hyperbolic space forms." *Publ. IHES* 34:53-104.
- Margulis, G. A. (1991). *Discrete Subgroups of Semisimple Lie Groups*. Springer.
- Mumford, D. (1965). *Geometric Invariant Theory*. Springer.
- Bronstein, M. M., Bruna, J., Cohen, T., & Veličković, P. (2021). "Geometric Deep Learning: Grids, Groups, Graphs, Geodesics, and Gauges." arXiv:2104.13478.
- Davies, A., Veličković, P., Buesing, L., et al. (2021). "Advancing mathematics by guiding human intuition with AI." *Nature* 600:70-74.
- Mazur, B., & Wiles, A. (1984). "Class fields of abelian extensions of Q." *Invent. Math.* 76(2):179-330.
- Internal: `aporia/notebooklm_bundles/ergon_learner/09_glossary.md`; `techne/TECHNE_SESSION_2026-05-02.md` lines 213-291; `roles/Ergon/SESSION_JOURNAL_20260504.md` lines 168-171, 477-481.
