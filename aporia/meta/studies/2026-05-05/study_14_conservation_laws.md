# Study 14: Cross-Domain Conservation Laws

**Date:** 2026-05-05
**Owner:** general-purpose subagent (Aporia delegation)
**Substrate connection:** Bridge gradient design (Study 03); behavior descriptor axis selection (Ergon v8 5-axis archive); bridge-quality scoring; calibrating "what's conserved" as an operational handle distinct from "what shape it has."

## Problem statement (Prometheus-adapted)

Prometheus's bridge gradient framing claims that real cross-domain transport requires a *structural* bridge — a functor, an equivalence, or a correspondence theorem — not a shared symbol. Study 03 separated the substrate's six envs into ~3 case-(1)–(3) bridge edges and ~12 case-(5) "shared invariant" edges and recommended refusing transfer claims on edges weaker than `dictionary`. This study asks the perpendicular question:

**Are there *conservation principles* (in the physics sense — a quantity invariant under a class of transformations) that genuinely span unrelated mathematical fields, and if so, do they give Prometheus an operational handle distinct from "shared invariant"?**

Specifically:

1. Should the Ergon v8 5-axis behavior descriptor (currently `canonicalizer_subclass / dag_entropy / output_type / magnitude / canonical_form_distance`) include a "what is conserved by this transformation" axis?
2. Are there documented "conserved quantities" that survive across the substrate's six envs (BSD / modular / knot / genus-2 / OEIS / mock theta) under a *known* transformation?
3. What's the falsification test that distinguishes a real conservation principle from a coincidence of notation?
4. Should bridge-quality scoring (Study 03's recommendation #2: L-function coefficient agreement) be generalised to "preserved quantity under the bridge"?

Honest summary up front: **conservation principles do cross fields, but in a more constrained way than the question suggests.** The cleanest cross-field conservation pattern is the Atiyah–Singer / Riemann–Roch / Gauss–Bonnet family — *equality of two functorially-defined integers, one analytic and one topological*. This is structurally different from physics-style Noether conservation (continuous symmetry → conserved current); the substrate should not conflate them. For the substrate's existing envs, three cross-env conserved quantities are documented (L-function, conductor, motivic weight), and they live on case-(1)–(3) bridges only. Adding a "what's conserved" axis is defensible *only if* it is operationalised as "the invariant the bridge preserves" — not as a free-floating descriptor.

## Literature scan

**Noether's theorem (1918).** The original statement: every continuous symmetry of an action functional yields a conserved current. The mathematical content is a bijection between Lie-algebra elements of the symmetry group and divergence-free vector fields on the solution space. (Olver, *Applications of Lie Groups to Differential Equations*, GTM 107, 1986; Noether, *Nachr. König. Gesell. Wiss. Göttingen*, 1918, English trans. Tavel arXiv:physics/0503066.) **This is a theorem, not a metaphor.** It applies wherever the input is an action functional with a Lie group of symmetries; it does not apply to discrete combinatorial structures, number-theoretic objects without a continuous symmetry, or knot diagrams. The "Noether-style" pattern in pure math (Hamiltonian → moment map, GIT quotient) is a literal application of the same theorem in a different category.

**Topological invariants as conserved quantities.** Euler characteristic χ, Betti numbers b_i, genus g, signature σ, and characteristic numbers (Stiefel–Whitney, Chern, Pontryagin) are all *conserved under continuous deformation* — i.e., they are homotopy or cobordism invariants. (Milnor & Stasheff, *Characteristic Classes*, 1974; Hatcher, *Algebraic Topology*, 2002.) The "conservation law" framing is faithful: deformation = transformation, invariance = conservation. This is the most direct mathematical analog of physical conservation, and it has the same logical structure (group of transformations / quotient invariant).

**Index theorems as cross-field conservation.** The Atiyah–Singer Index Theorem (1963, *Ann. Math.* 87, 1968) equates an *analytic* index (dimension of kernel minus dimension of cokernel of an elliptic operator) with a *topological* index (a characteristic-class integral). Both sides are integers; both are functorial; the equality is the bridge. Specialisations recover Riemann–Roch (analytic Euler char of a sheaf = topological Euler char), Gauss–Bonnet (curvature integral = 2πχ), Hirzebruch signature theorem (signature = L-genus), and the Chern–Gauss–Bonnet theorem. **This family is the cleanest documented case where "conservation in field A turns out to be the same conservation in field B."** (Atiyah & Singer, *Ann. Math.* 87, 484–530 (1968) and successors I–V; Berline, Getzler & Vergne, *Heat Kernels and Dirac Operators*, 1992.)

**Conservation of L-functions across the Langlands bridge.** Modularity Theorem (Wiles–Taylor–BCDT, 2001): for every elliptic curve E/Q there is a weight-2 newform f with L(E,s) = L(f,s). The L-function is conserved under the bridge; this is structurally identical to "energy conserved under time translation," with the symmetry being the equivalence of the two categories (elliptic curves ~ rational-Hecke newforms). Conductor and Tate–Shafarevich rank are also conserved (the latter conjecturally, via BSD). (Bump, *Automorphic Forms and Representations*, CUP 1997; Diamond & Shurman, *A First Course in Modular Forms*, GTM 228, 2005.)

**Cobordism as a conservation framework.** Thom's cobordism theory (*Comm. Math. Helv.* 28, 1954) classifies manifolds by what is *invariant* under cobordism — i.e., what survives the equivalence relation "M ~ M' iff their disjoint union bounds a manifold one dimension up." Stiefel–Whitney and Pontryagin numbers are cobordism invariants; they are *the* invariants in the unoriented and oriented cases respectively. (Milnor, "On the cobordism ring Ω* and a complex analogue," *Amer. J. Math.* 82, 1960.) The conservation framing is again literal: the equivalence relation defines the symmetry, the invariant is the conserved quantity.

**Information-theoretic conservation (negative result).** Shannon entropy is *not* conserved under arbitrary transformations; it is conserved only under bijections of finite sets and monotone under deterministic measurable maps. Kolmogorov–Sinai entropy is conserved under measure-preserving conjugacy of dynamical systems (Sinai, *Doklady* 124, 1959). The pattern: the "conservation" requires a precisely-specified equivalence relation; the looser the relation, the weaker the conservation. **No "universal" conservation law spans information theory, topology, and number theory.**

**Categorical formulation.** Universal property of a Kan extension, equivariant K-theory's Mayer–Vietoris, monoidal-category trace: each is a "conservation law" in the category-theoretic sense (an invariant of a functor / of a 2-morphism). Ben-Zvi, Francis & Nadler ("Integral transforms and Drinfeld centers in derived algebraic geometry," *J. AMS* 23, 2010, arXiv:0805.0157) treats these uniformly as traces. The general principle: *every adjunction induces a conserved quantity (the trace of the unit)*. Not yet shown to give the substrate a useful new operational handle.

**Failure mode: "conservation" of the wrong thing.** Bell's theorem and the violation of local realism is the canonical physics example of a "conservation law" (local hidden-variable correlations) that turns out not to hold. Pure-math analog: pre-Donaldson smooth-vs-topological invariants of 4-manifolds were assumed to coincide; they do not (Donaldson 1982). The lesson for Prometheus: a *postulated* cross-domain conservation is not a real one until tested, and dimension thresholds (Mostow rigidity threshold, Donaldson dimension 4) are where false conservation laws die.

**No canonical catalogue.** This author finds **no published "graph of cross-domain conservation laws"**. nLab maintains scattered entries on `conserved current`, `Noether's theorem`, `cobordism hypothesis`, `index theorem`, but no unified taxonomy. Frenkel's *Love and Math* (Basic Books, 2013) gestures at a "grand unified theory of mathematics" via Langlands but is popular, not catalogued. The closest existing object is the index-theorem family tree (Berline–Getzler–Vergne, ch. 1).

## Substrate-relevance

Three load-bearing connections:

1. **The 5-axis behavior descriptor does not currently encode "what is conserved."** Per `ergon/learner/descriptor.py` line 385, the axes are `canonicalizer_subclass / dag_entropy_bucket / output_type_signature / magnitude_bucket / canonical_form_distance_bucket`. The first axis is the *kind* of canonicalisation (group quotient, partition refinement, ideal reduction, variety fingerprint) — i.e., the *transformation type*. There is no axis for *what survives* the transformation. This is a real gap, but the right fix is *not* a free-floating "conserved quantity" axis (which would degenerate into output_type_signature or magnitude_bucket). The right fix is to *type the canonicalizer subclass with its preserved quantity*: every group_quotient preserves the conjugacy-class function on the group, every ideal_reduction preserves the image in R/I, etc. This is metadata on the existing axis, not a new axis.

2. **Of the substrate's six envs, three pairs share documented conserved quantities under known bridges.** Per Study 03's edge classification:
   - **BSD ↔ modular**: L-function (full Dirichlet series), conductor, root number, Hecke eigenvalues a_p — all conserved under modularity. *Already exploited by Charon's f011_* scripts.*
   - **Modular forms ↔ Galois representations**: trace of Frobenius (= a_p), determinant (= chi(p) p^(k-1) for weight k), conductor — all conserved under Deligne's construction.
   - **Mock theta ↔ harmonic Maass forms**: shadow operator, mock-modular completion — Zwegers's correspondence preserves these (a case-(3) bridge per Study 03).

   The other three env-pairs (knot ↔ NF, genus-2 ↔ paramodular, OEIS ↔ anything) carry only case-(5) shared-invariant or weaker. **Conservation-preservation is therefore not a substrate-wide universal; it is a per-edge property that the bridge-class typing already captures.** Adding it as a separate axis would double-count.

3. **Bridge-quality scoring (Study 03 handle #2) can be sharpened by conservation tests.** Study 03 proposed L-function coefficient agreement as the bridge fidelity score on the BSD–modular edge. The general form: for each documented bridge, list the quantities the bridge claims to preserve, and score the bridge by computing both sides and comparing. This is exactly how mathematicians verify a conjectural bridge (e.g., paramodular conjecture sample computations by Brumer–Pacetti–Tornaria). The substrate can adopt this directly.

## Concrete operational handles

1. **Annotate canonicalizer_subclass with preserved-quantity metadata** in `ergon/learner/descriptor.py`. Each of the four subclasses has a known conserved quantity:
   - `group_quotient` → conjugacy-class function (or, more generally, the invariant ring under the group action)
   - `partition_refinement` → orbit count and orbit-type signature
   - `ideal_reduction` → image in R/I (reduction-mod-I)
   - `variety_fingerprint` → scheme-theoretic invariants (Hilbert polynomial, étale cohomology, point counts over finite fields)
   This is metadata, not a new axis; cost is one column in arsenal_meta and one helper in descriptor.py.

2. **Do NOT add a free-floating "what's conserved" descriptor axis.** The literature does not support a universal cross-domain conservation taxonomy that would justify it. Such an axis would either collapse into `output_type_signature` (for value-level conservation) or into `canonicalizer_subclass` (for structure-level conservation). Hot-swap candidates per Ergon v8 §6.2 should remain `cohomological_functor` and `spectral_dynamical` (Study 07), not "conserved quantity."

3. **Generalise the bridge-fidelity score (Study 03 handle #2) to a conservation-test battery.** For each declared case-(1)–(3) bridge, list the quantities the bridge claims to preserve; for each pair of objects on the two sides claimed to correspond, compute both sides and score the discrepancy. Concretely for Charon:
   - BSD–modular: a_p for p ≤ N (already done); add conductor, root number, weight.
   - Mock theta–harmonic Maass: shadow operator output (currently unexploited per Study 03).
   - Genus-2–paramodular: L-function coefficients (this is a *test* of the paramodular conjecture, not a verified bridge).

4. **Use the index-theorem family as a calibration anchor for "real cross-domain conservation."** Atiyah–Singer is the textbook case: two integers, two categories, one equality. Any candidate cross-domain conservation principle the substrate detects should be pattern-matched against this template before being elevated to a substrate-grade finding. Specifically: (a) two functorially-defined quantities on two different categories, (b) a precise equality (not a correlation), (c) at least one specialisation that recovers a known classical theorem.

5. **Treat physics-style Noether conservation as one specific instance, not a template.** Noether's theorem requires an action functional with a continuous Lie symmetry. Most of the substrate's envs (BSD, modular, knot, OEIS) lack this structure. Importing Noether-language ("the substrate's symmetry of X conserves Y") without that structure is a category mistake the substrate should refuse.

## Falsification

Central claim: **"what is conserved" is per-bridge metadata, not a substrate-wide axis; the only universal cross-domain conservation patterns documented in the literature are (a) the index-theorem family and (b) Langlands-style L-function preservation, both of which the substrate already has hooks for via canonicalizer_subclass + bridge_class typing.**

Refuted if any of the following holds:

- A systematic catalogue is found that documents ≥1 cross-domain conservation principle the substrate cannot encode as (canonicalizer_subclass × bridge_class) metadata. Candidate examples to look for: motivic weight (currently unhandled), Tate twists, weight-monodromy.
- An A/B test with a "preserved_quantity" axis added to the descriptor shows >5% improvement in either archive coverage or `n_substrate_passed` over the v8 5-axis configuration on the same kill-battery.
- A genuine Noether-style conservation (continuous symmetry → conserved current) is identified in a substrate env that lacks an action functional. (This would force a re-examination of the categorical scope of Noether.)
- Charon's bridge-fidelity test on the BSD–modular edge produces non-zero discrepancy at the L-function-coefficient level for a sample where modularity is known to hold. (This would refute the "L-function is preserved" claim and force a re-look at the bridge.)

Refutation by literature alone is unlikely; refutation by substrate experiment via the proposed conservation-test battery is feasible within Charon's existing tooling.

## Open questions raised

1. Is motivic weight a substrate-relevant conserved quantity not yet captured? It is preserved by Tate twists and by L-function functional equations, and it crosses the modular / Galois / motive boundary cleanly. The substrate has not surfaced it.
2. Does the index-theorem template (analytic = topological) suggest a generic test pattern: for any pair of substrate envs, compute a "pseudo-analytic" and a "pseudo-topological" invariant on both sides and check equality? This is speculative; the index theorem is much more constrained than that.
3. Should the substrate distinguish *conservation under a transformation* from *invariance under an equivalence relation*? Mathematically these are nearly the same, but the operational tests differ (transformations have generators; equivalence relations have representatives).
4. Is there a substrate-detectable signature of a *failed* cross-domain conservation, distinct from a successful one? Donaldson's smooth-vs-topological 4-manifold distinction is the model; the substrate would need to detect that an assumed-invariant quantity actually depends on a structure being quotiented.
5. Would a conservation-test battery on case-(5) "shared invariant" edges (the 12 the substrate currently treats as null) discover new bridges? Study 03 noted that such bridges would have to be tested on an "invariant transport" metric; this study's conservation framing suggests how to score them.

## Citations

- Noether, E. *Invariante Variationsprobleme*. Nachr. König. Gesell. Wiss. Göttingen, Math.-Phys. Kl. (1918), 235–257. English trans. M. A. Tavel, arXiv:physics/0503066.
- Olver, P. J. *Applications of Lie Groups to Differential Equations*. GTM 107, Springer, 1986.
- Atiyah, M. F.; Singer, I. M. *The index of elliptic operators I*, Ann. Math. 87 (1968), 484–530. (Plus II–V in successive volumes.)
- Berline, N.; Getzler, E.; Vergne, M. *Heat Kernels and Dirac Operators*. Springer, 1992.
- Milnor, J.; Stasheff, J. *Characteristic Classes*. Annals of Math. Studies 76, Princeton, 1974.
- Hatcher, A. *Algebraic Topology*. CUP, 2002.
- Thom, R. *Quelques propriétés globales des variétés différentiables*, Comm. Math. Helv. 28 (1954), 17–86.
- Milnor, J. *On the cobordism ring Ω* and a complex analogue*, Amer. J. Math. 82 (1960), 505–521.
- Sinai, Ya. G. *On the concept of entropy of a dynamical system*, Doklady Akad. Nauk SSSR 124 (1959), 768–771.
- Wiles, A. *Modular elliptic curves and Fermat's Last Theorem*, Ann. Math. 141 (1995), 443–551. (Plus Taylor–Wiles, BCDT 2001.)
- Bump, D. *Automorphic Forms and Representations*. CUP, 1997.
- Diamond, F.; Shurman, J. *A First Course in Modular Forms*. GTM 228, Springer, 2005.
- Zwegers, S. *Mock Theta Functions*. PhD thesis, Utrecht University, 2002.
- Brumer, A.; Kramer, K. *Paramodular abelian varieties of odd conductor*, Trans. AMS 366 (2014), 2463–2516.
- Donaldson, S. K. *Self-dual connections and the topology of smooth 4-manifolds*, BAMS 8 (1983), 81–83.
- Mostow, G. D. *Strong Rigidity of Locally Symmetric Spaces*. Annals of Math. Studies 78, Princeton, 1973.
- Ben-Zvi, D.; Francis, J.; Nadler, D. *Integral transforms and Drinfeld centers in derived algebraic geometry*, J. AMS 23 (2010), 909–966. arXiv:0805.0157.
- nLab community wiki, entries `conserved current`, `Noether's theorem`, `cobordism hypothesis`, `index theorem`, `Langlands correspondence`. (Not primary; most extensive informal cross-reference extant.)

No canonical catalogue of cross-domain conservation laws was located. The Atiyah–Singer family tree (Berline–Getzler–Vergne ch. 1) is the closest published unified treatment, and it is restricted to index-theoretic conservation — i.e., the analytic-equals-topological pattern.
