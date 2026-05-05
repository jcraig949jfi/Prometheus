# Study 03: Analogy Graphs Between Mathematical Fields

**Date:** 2026-05-05
**Owner:** general-purpose subagent (Aporia delegation)
**Substrate connection:** Bridge gradient design, cross-domain transport claims (currently weak per Case A finding); informs whether the substrate's six envs (BSD, modular, knot, genus-2, OEIS, mock theta) should be treated as edges of a typed bridge graph or as independent islands.

## Problem statement (Prometheus-adapted)

Prometheus has six cross-domain environments and is empirically watching its
RL agents *fail to transfer* across them in any way that survives a
modal-class null. The substrate-side question is not "are there analogies
between mathematical fields" (yes), but: **what kind of object is a real
bridge, and does anything Prometheus is currently doing produce or detect
one?**

A bridge in mathematics is sometimes:

1. A **theorem** asserting an isomorphism / equivalence of categories (e.g.
   modularity theorem: every elliptic curve over Q corresponds to a weight-2
   newform).
2. A **conjectural correspondence** with partial cases proved (Langlands).
3. A **functor** between categories (Fukaya category ↔ derived category of
   coherent sheaves under mirror symmetry).
4. A **dictionary** of computable invariants (number-field ↔ function-field
   analogy).
5. A **shared invariant** (Euler characteristic, characteristic classes).

Most "bridges" appearing in popular math writing are case (5) or weaker —
they share a *symbol* but not a structure-preserving map. Case A's negative
finding is consistent with the substrate detecting only this weakest sense.

## Literature scan

**Langlands program.** The *formal* statement is a conjectural
correspondence between (a) automorphic representations of a reductive group
G over a global field, and (b) Galois representations into the L-group of G.
For G = GL(2)/Q, restricting to weight-2 holomorphic newforms with rational
Hecke eigenvalues, this specialises to the Modularity Theorem
(Wiles–Taylor–Breuil–Conrad–Diamond, 2001). The bridge is a *bijection*
preserving L-functions: L(E,s) = L(f,s). This is the strongest possible
sense of "structure-preserving" — every analytic and arithmetic invariant
on one side has a named partner on the other. (Cf. Bump, *Automorphic
Forms and Representations*, CUP 1997; Gelbart, BAMS 1984 survey.)

**Geometric Langlands.** Beilinson–Drinfeld reformulated Langlands as an
equivalence of derived categories: D-modules on Bun_G(X) ↔ quasi-coherent
sheaves on the moduli of L^G-local systems. This is genuinely a functor
(in fact, a conjectural equivalence of (∞,1)-categories), proved in the
de Rham setting for GL_n by Gaitsgory et al. (announced 2024, see Arinkin–
Gaitsgory and successor papers). The functoriality is *the* content.

**Atiyah–Singer Index Theorem.** Equates the analytic index of an elliptic
operator with a topological index built from characteristic classes. This
is a *theorem* (1963), not a conjecture, and the equality is a numerical
identity between two functorially-defined integers. The bridge is
structure-preserving in a precise sense: K-theory provides a category
where both sides live as morphisms.

**Mirror symmetry.** Originally a string-theory observation (Candelas et
al. 1991), upgraded by Kontsevich (1994) to **Homological Mirror Symmetry**:
a conjectured equivalence D^b(Coh(X)) ≃ D^πFuk(X^∨) of triangulated
categories. Proved in special cases (elliptic curves, K3 surfaces, toric
varieties — Polishchuk–Zaslow, Seidel, Abouzaid). Strongest case (5)/case
(3) hybrid: numerical mirror symmetry shares Hodge numbers; HMS shares
A_∞-categorical structure.

**Function-field / number-field analogy.** Weil's "Rosetta stone" between
Z, F_q[t], and meromorphic functions on a Riemann surface. Concretely:
zeta(s) ↔ Hasse–Weil zeta of a curve over F_q ↔ Selberg zeta. RH was
proved in the function-field case (Weil 1948, Deligne 1974). Transfer of
the **proof technique** to the number-field case: zero in 75 years,
despite enormous effort. This is the cleanest documented case where an
analogy is *deep at the statement level* but does **not** transfer
proofs. Important calibration anchor.

**Tao's writing on analogy.** Terence Tao has written informally (blog,
"What is good mathematics?", Bull. AMS 2007) about heuristic transfer but
has not, to this author's knowledge, produced a systematic catalogue. No
canonical source identified for a "graph of mathematical analogies."

**Category-theoretic frameworks.** Lawvere's functorial semantics, Lurie's
∞-category program, and the Univalent Foundations program all provide
*languages* in which "structure-preserving map" has a precise meaning
(functor, equivalence, weak equivalence). The nLab wiki maintains an
informal but extensive cross-referencing of "duality" pairs (Stone, Pontryagin,
Gelfand, Tannaka, Koszul, Langlands…); this is the closest extant object to
the graph requested by the study question.

**Failure pattern of superficial analogies.** Three common modes:

1. *Shared invariant, different category.* "Both have a Z/2 grading" is not
   a bridge — Z/2-graded things abound. (cf. critiques of early
   "supermathematics" hype.)
2. *Numerology.* Coincident numerical values without functorial origin
   (monstrous moonshine *looked* like this until Borcherds 1992 produced
   the vertex-algebra functor — so "looks superficial" is not always a
   kill).
3. *Translation that doesn't extend.* The analogy works for objects but
   not morphisms. Symptomatic in physics-to-math transfers.

## Substrate-relevance

Prometheus's six envs map onto known bridges as follows:

- **BSD ↔ modular forms**: bridged by the Modularity Theorem
  (case 1 above). Structure-preserving at L-function level. Substrate
  exploits this in Charon (e.g., `f011_*` scripts test BSD via modular data).
- **Modular forms ↔ Galois representations**: Langlands for GL(2)/Q. Case 1
  for the rational Hecke locus, case 2 generally.
- **Knot trace fields ↔ number fields**: shared object (a number field
  with a chosen Galois action), not a bridge in case (1)–(3) sense. This is
  case (5) — shared-invariant only. Cross-transfer of theorems is not
  documented at the level the substrate would need.
- **Genus-2 curves ↔ paramodular forms**: paramodular conjecture (Brumer–
  Kramer 2014). Case 2 — conjectural correspondence with partial cases.
  This is the substrate's *only* genuinely-bridgeable env-pair beyond the
  BSD/modular axis, and the bridge is unproved.
- **OEIS Sleeping Beauty ↔ anything**: OEIS is a *registry*, not a domain.
  The relevant object is "what mathematical structure does each sequence
  index?" Bridges live at the per-sequence level, not at the OEIS level.
- **Mock theta ↔ modular forms**: Zwegers (2002) made mock theta functions
  the holomorphic parts of harmonic Maass forms — a genuine functorial
  embedding (case 3). Substrate has not exploited this.

So of 15 unordered env-pairs, ~3 (BSD–modular, modular–Galois implicit,
genus-2–paramodular) carry case-(1)–(3) bridges; the rest are case (5) or
weaker. **The substrate's expectation of 15 bridges where ~3 exist is
itself a finding.** Case A's failure to detect cross-domain transport may
be re-explained as: agents transferred between env-pairs that aren't
actually bridged in any structure-preserving sense.

## Concrete operational handles

1. **Type the bridge graph.** Annotate each env-pair edge with:
   `bridge_class ∈ {none, shared_invariant, dictionary, conjectural,
   theorem_functor}`. Refuse to make "transfer" claims on edges with
   class < `dictionary`.

2. **Operationalise structure-preservation as L-function preservation.**
   For the substrate's existing envs, the cheapest measurable invariant
   is the L-function (Dirichlet coefficients up to a cutoff). A genuine
   bridge predicts coefficient-level equality (or known transformation).
   Charon already computes a_p sequences for both EC and modular form
   sides; turn this into a *bridge fidelity score*.

3. **Negative envs.** Add an env-pair with **known absence of bridge**
   (e.g., random EC over Q vs random number-field of unrelated
   conductor). Use as a null-bridge calibration — any transfer signal
   here is methodological artifact.

4. **Replace "cross-domain RL transfer" metric with "invariant transport"
   metric.** Instead of asking "does policy from env A help in env B?",
   ask "does the substrate compute the *same* L-function value on both
   sides of a known bridge?" This is what mathematicians do when
   verifying a bridge; it's also computationally cheap.

5. **Refuse to add a new env without a declared bridge class to at least
   one existing env.** This prevents the env catalogue from drifting into
   a bag of unrelated puzzles.

## Falsification

Central claim of this study: **most claimed mathematical analogies do
not transfer theorems; the ones that do are nameable, sparse, and
typically have an underlying functor or correspondence-theorem.**

Refuted if:

- A systematic catalogue of mathematical analogies is found in which
  >50% transfer theorems by some defensible measure (no such catalogue
  is known to this author).
- The substrate demonstrates non-trivial cross-env transfer on an
  edge currently classed `shared_invariant` or `none`, robust to a
  null-bridge calibration. This would force re-classification (good
  outcome).
- A constructive method is found for upgrading case (5) analogies to
  case (3) routinely. (Mock theta → harmonic Maass forms is the
  proof-of-concept; its rarity is the evidence.)

Refutation by literature is unlikely; refutation by substrate experiment
on the proposed "invariant transport" metric is feasible within Charon's
existing tooling.

## Open questions raised

- Is there a category in which Prometheus's six envs are objects and
  bridges are morphisms? (Probably not as stated, but a sub-collection
  may form one.)
- Can the substrate **discover** a new bridge, or only verify known
  ones? Discovery would require finding two envs whose computed
  invariants agree under a non-obvious transformation. The substrate's
  current tooling could in principle do this; it has not been pointed
  at the question.
- What's the right granularity for "env"? Genus-2 paramodular is a
  single env in Prometheus; in the literature it's a thicket of
  sub-cases (split / non-split, prime / composite paramodular level).
  Coarser env definitions hide where bridges actually live.
- Does the function-field/number-field analogy's failure-to-transfer-
  proofs predict a similar failure between, e.g., the substrate's
  knot env and number-field env, even if a case-(3) bridge were
  conjectured? Probably yes.
- Is "bridge depth" measurable? Candidate metric: the smallest cut in
  the dependency graph of theorems on each side that, when matched,
  determines all others. No such metric is in the literature to this
  author's knowledge.

## Citations

- Gelbart, S. *An elementary introduction to the Langlands program*,
  BAMS 10 (1984), 177–219.
- Bump, D. *Automorphic Forms and Representations*. CUP, 1997.
- Wiles, A. *Modular elliptic curves and Fermat's Last Theorem*,
  Ann. Math. 141 (1995), 443–551. (Plus Taylor–Wiles and BCDT 2001
  for the full modularity theorem.)
- Atiyah, M.; Singer, I. *The index of elliptic operators I–V*,
  Ann. Math. 87 (1968) and successors.
- Kontsevich, M. *Homological algebra of mirror symmetry*, Proc. ICM
  Zurich 1994, 120–139. arXiv:alg-geom/9411018.
- Polishchuk, A.; Zaslow, E. *Categorical mirror symmetry: the
  elliptic curve*, Adv. Theor. Math. Phys. 2 (1998), 443–470.
  arXiv:math/9801119.
- Beilinson, A.; Drinfeld, V. *Quantization of Hitchin's integrable
  system and Hecke eigensheaves*. Preprint (no canonical published
  version; widely circulated).
- Arinkin, D.; Gaitsgory, D., et al. *Proof of the geometric Langlands
  conjecture* (2024 series). arXiv:2405.03599 and successors.
- Weil, A. *Sur les courbes algébriques et les variétés qui s'en
  déduisent*, Hermann, 1948.
- Deligne, P. *La conjecture de Weil I*, Pub. IHÉS 43 (1974), 273–307.
- Brumer, A.; Kramer, K. *Paramodular abelian varieties of odd
  conductor*, Trans. AMS 366 (2014), 2463–2516.
- Zwegers, S. *Mock Theta Functions*. PhD thesis, Utrecht, 2002.
- Borcherds, R. *Monstrous moonshine and monstrous Lie superalgebras*,
  Invent. Math. 109 (1992), 405–444.
- Tao, T. *What is good mathematics?*, BAMS 44 (2007), 623–634.
- nLab community wiki, especially entries on `duality`, `Langlands
  correspondence`, `mirror symmetry`. (Not a primary source but the
  most extensive informal catalogue extant.)

No canonical source identified for "graph of mathematical analogies"
as a single object. The closest are the nLab duality pages and Frenkel's
*Love and Math* (popular, not a catalogue).
