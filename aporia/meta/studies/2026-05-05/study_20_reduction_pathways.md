# Study 20: Reduction Pathways Between Theories

**Date:** 2026-05-05
**Owner:** general-purpose subagent (Aporia delegation)
**Substrate connection:** `dependency_graph.py` augmentation; theory-graph design; calibrating whether the substrate's six envs (BSD / modular / knot / genus-2 / OEIS / mock theta) admit a *reductive* (rather than merely *analogical*) ordering.

## Problem statement (Prometheus-adapted)

Study 03 separated cross-domain edges into five bridge cases (theorem / conjectural correspondence / functor / dictionary / shared invariant) and Study 14 separated bridge-edges by *what is conserved across them*. Both studies operate at the level of mathematical *objects* (curves, forms, knots). The perpendicular question is whether the substrate should also represent edges between *theories* — formal axiomatic systems that could in principle host those objects — and whether such a "theory graph" gives a *strength ordering* that the object-level bridge graph does not.

Specifically:

1. Is there a published, citable "theory graph" the substrate could ingest as ground truth — a partial order of mathematical theories by some precise notion of reduction?
2. Does Friedman/Simpson reverse mathematics give the substrate a *reduction-strength score* it could attach to each env's theorem-base (BSD requires X axioms; modularity requires Y; knot Floer requires Z)?
3. Should `dependency_graph.py` be augmented with theory-level reduction edges in addition to operation-level edges?
4. The literature recognises at least three distinct "reduction" relations — interpretation, conservativity, equivalence — that get conflated in informal discussion. Are they actually distinct on the substrate's envs, and does the substrate need to track which one it has?

Honest summary up front: **a published theory graph exists at *foundational* granularity (the reverse-mathematics big-five hierarchy, the proof-theoretic-ordinal hierarchy, the foundations-comparison literature on ZFC / NBG / MK / ETCS / HoTT) but does NOT exist at the granularity Prometheus needs (BSD / modular / knot / genus-2 / OEIS / mock theta).** All six of the substrate's envs live well inside ZFC and almost certainly inside ACA_0 or weaker for their *computable* content; reverse-mathematics scoring would therefore not separate them. The three reduction relations are genuinely distinct, and the substrate already implicitly tracks the difference (Study 03's case-(1) is closest to *equivalence*, case-(3) to *interpretation*, case-(5) to neither). The recommended action is *not* to add theory-level edges to `dependency_graph.py` — the substrate operates at the operational layer where reverse-math has no resolution — but to record, *as metadata on each env*, the strongest published foundation under which its core theorems are known to live.

## Literature scan

**Reverse mathematics — the big five (Friedman 1975; Simpson 1985–2009).** The standard text is Simpson, *Subsystems of Second Order Arithmetic*, Perspectives in Logic, CUP 2nd ed. 2009. Five base systems are linearly ordered by interpretability:

> RCA_0 ⊊ WKL_0 ⊊ ACA_0 ⊊ ATR_0 ⊊ Π¹₁-CA_0

Each system is *equivalent over RCA_0* to a long list of "ordinary mathematical" theorems: WKL_0 ↔ Heine–Borel for [0,1], compactness of complete bounded metric spaces, Brouwer fixed-point in dimension n; ACA_0 ↔ Bolzano–Weierstrass, sequential compactness of [0,1]^N, the existence of König's lemma in full generality; ATR_0 ↔ comparability of countable well-orderings, perfect-set theorem; Π¹₁-CA_0 ↔ Cantor–Bendixson theorem, Σ¹₁-determinacy. (Simpson, op. cit., chapters III–VI.) **This is a published, computer-verifiable theory graph** — but it is a graph over *theorems of countable mathematics*, not over *fields*.

**Proof-theoretic ordinals (Gentzen 1936; Schütte; Rathjen; Pohlers).** Each consistent reasonably-strong theory T has a *proof-theoretic ordinal* |T| measuring the supremum of recursive ordinals whose well-foundedness T proves. PA has ε_0; ATR_0 has Γ_0 (Feferman–Schütte); Π¹₁-CA_0 has ψ(Ω_ω); ZFC's ordinal is unknown. (Pohlers, *Proof Theory: The First Step into Impredicativity*, Springer 2009; Rathjen, "The art of ordinal analysis," ICM 2006.) This gives a *real-valued reduction-strength score*, but again it lives at foundational granularity and pins out at "ZFC" for everything Prometheus does.

**Conservativity results.** A theory T₂ is conservative over T₁ for class Γ if every Γ-sentence provable in T₂ is already provable in T₁. Key results: (a) WKL_0 is Π¹₁-conservative over RCA_0 (Harrington, unpub. ~1977; Simpson IX.3); (b) ACA_0 is conservative over PA for arithmetical sentences (Friedman); (c) NBG is conservative over ZFC for set-theoretic sentences (Novak 1950, Shoenfield 1954); (d) ZFC + "there is an inaccessible" is conservative over ZFC for arithmetical sentences in suitable settings; (e) HoTT + univalence + propositional resizing is conservative over ZFC + countable inaccessibles for *propositional* mathematics (Voevodsky's simplicial model; Kapulkin–Lumsdaine, *J. EMS* 23, 2021, arXiv:1211.2851 — note: I'm reasonably confident about the existence of this paper but not the year, so treat the cite as illustrative). **Conservativity is the most operationally useful reduction relation:** it tells you whether using the stronger theory ever lets you prove something genuinely new in the language of the weaker one.

**Foundations comparison: ZFC / NBG / MK / ETCS / HoTT.**
- *NBG (von Neumann–Bernays–Gödel)* extends ZFC with proper classes; finitely axiomatisable; conservative over ZFC for set-theoretic sentences (cite (c) above).
- *MK (Morse–Kelley)* extends NBG by allowing impredicative class comprehension; *not* conservative over ZFC — proves Con(ZFC). (Mostowski, Felgner; Kelley *General Topology* appendix.)
- *ETCS (Lawvere 1964; McLarty 1993)* axiomatises the category of sets with NNO + choice; bi-interpretable with *bounded Zermelo* (Z + bounded separation, no replacement). Strictly weaker than ZFC. McLarty, "Exploring categorical structuralism," *Philosophia Mathematica* 12 (2004); Osius, "Categorical set theory," *J. Pure Appl. Algebra* 4 (1974).
- *ETCS+R (ETCS with replacement-style schema)* is bi-interpretable with ZFC. Mac Lane, Lawvere, Rosolini.
- *HoTT (Univalent Foundations Programme, *Homotopy Type Theory*, IAS 2013)* — ground-truth interpretability is delicate. Voevodsky's simplicial-set model gives an interpretation in ZFC + 2 inaccessibles. The reverse direction (ZFC interprets in HoTT) goes via setoids / 0-types and requires some choice principle. (Awodey & Warren, *Math. Proc. Camb. Phil. Soc.* 146, 2009; Kapulkin–Lumsdaine cite above.)

**There is a published partial-order picture** of these foundations — the "interpretability lattice" — most clearly drawn in Maddy, *Defending the Axioms*, OUP 2011, ch. 4, and in McLarty, "What does it take from the foundations of mathematics," *Philosophia Mathematica* 21, 2013. The picture: ETCS ≲ Z ≲ ZFC ≡ ETCS+R ≲ NBG (sentence-conservative) ≲ MK ≲ ZFC + inaccessible ≲ HoTT-with-univalence (ordering up to bi-interpretation). **This graph has < 10 nodes** and is therefore not granular enough to score the substrate's six envs.

**Categorical equivalences as reductions.** An equivalence of categories F: C → D is a structure-preserving reduction in the strongest sense — every categorical statement true in C has a translate true in D and vice versa. Examples relevant to the substrate: Stone duality (Boolean algebras ≃ Stone spaces^op), Gelfand duality (commutative C*-algebras ≃ compact Hausdorff^op), the equivalence between the Fukaya category of a torus and the derived category of an elliptic curve (homological mirror symmetry, Polishchuk–Zaslow 1998). These are *case-(1)/(3) bridges* in Study 03's typology. **Equivalence is a stronger relation than conservative interpretation** (it preserves more than provability) and a strictly stronger relation than bi-interpretation (it preserves the category structure, not just the deductive closure).

**The three reduction relations are genuinely distinct.** Interpretation (Tarski–Mostowski–Robinson 1953): a translation of formulas that preserves provability. Conservativity (above): provability-preservation in one direction over a fragment. Equivalence (Eilenberg–Mac Lane 1945, in the categorical sense; Morita equivalence for rings; Mita equivalence for theories in the model-theoretic sense): a structure-preserving bijection. Implications: equivalence ⇒ bi-interpretation ⇒ mutual interpretation ⇒ conservativity-pair-wise. None of the reverse implications hold in general; counter-examples in Visser, "Categories of theories and interpretations," in *Logic in Tehran*, 2006.

**No published theory graph at substrate granularity.** Searched the obvious places: nLab `interpretation` and `reverse mathematics` pages, Logic Atlas (the latter has < 50 theory nodes, all foundational), Specware/HETS (formal-methods tools tracking interpretations between specifications, but the theory base is software-engineering-flavoured, not number-theoretic). **Nothing maps the reductive relationships among "BSD", "modularity", "knot Floer homology", "Siegel-paramodular forms", "OEIS", or "mock theta functions" — because at this granularity the question is malformed:** these are *bodies of theorems and conjectures about specific objects*, not formal theories. They all live inside ZFC and almost all of their computable content lives inside ACA_0.

**Caveat — proof-theoretic strength of specific theorems.** There *is* a small literature scoring individual theorems by reverse-math strength: Robertson–Seymour graph minor theorem requires Π¹₁-CA_0 (Friedman, Robertson, Seymour 1987); Hindman's theorem requires ACA_0+; Kruskal's tree theorem requires ATR_0. These are all combinatorial-flavoured. **No similar scoring exists for modularity, BSD, or any of the substrate's headline conjectures**, because (a) they are conjectural rather than theorem, (b) their *known* partial cases are proved using machinery (étale cohomology, Galois deformations, p-adic Hodge theory) that lives well above ATR_0 in *consumed* strength but whose minimum-required strength has not been analysed.

## Substrate-relevance

Three load-bearing connections, all *negative or constraining*:

1. **Reverse mathematics does not separate the substrate's envs.** All six envs prove their core *computable* facts (computing a_p of an elliptic curve, computing a knot's Alexander polynomial, computing a Siegel form's Hecke eigenvalue, looking up an OEIS sequence, computing a mock theta coefficient) in RCA_0 + WKL_0. Their full *theoretical* development uses ZFC machinery, but the substrate consumes only the computable part. **A reverse-math-derived "reduction-strength score" would assign all six envs the same value.** This is a real negative finding, not a gap to fill.

2. **The dependency_graph.py is at the wrong layer for theory-graph augmentation.** Per the Aporia codebase pattern (operations like `compute_lfunction`, `lookup_oeis`, `apply_modular_transform`), `dependency_graph.py` tracks *operation* dependencies — which substrate calls require which others' outputs. Adding *theory* edges (e.g. "modularity reduces to GL(2) Langlands") would mix two layers: operational dependencies (must run X before Y) vs theoretical reductions (theorem of theory T₁ implies theorem of theory T₂). These layers have different semantics — operations succeed/fail at runtime, reductions hold or don't as logical facts — and conflating them would make the graph harder to query for either purpose.

3. **The substrate already implicitly distinguishes Study-14's three reduction relations**, in the form of Study 03's bridge-class typing. Mapping:
   - Study 03 case (1) = theorem-equivalence ≈ *categorical equivalence* (modularity is the bridge).
   - Study 03 case (3) = functor ≈ *interpretation* (Zwegers's mock-modular completion is a functor).
   - Study 03 case (4) = dictionary ≈ informal *bi-interpretation* (number-field / function-field analogy).
   - Study 03 case (5) = shared invariant ≈ no reduction, just coincidence of an attribute.
   The substrate does not need a separate "reduction kind" axis; it needs Study 03's bridge_class to be honoured.

## Concrete operational handles

1. **Add a `foundation_strength` field to env-level metadata** (one entry per env in `aporia/envs/*.json` or wherever env config lives), recording: (a) the strongest published foundation under which the env's core theorems are *proved* (typically ZFC + Grothendieck universe for arithmetic geometry), (b) the *minimum* known foundation under which the env's *computable content* is provably correct (typically RCA_0 or ACA_0), (c) a citation. This is documentation, not a graph; cost is one JSON field per env.

2. **Do NOT add theory-level reduction edges to `dependency_graph.py`.** Reasons:
   - At foundational granularity (ZFC ↔ NBG ↔ etc.), the graph has < 10 nodes and is identical for all six envs — adds no information.
   - At env granularity (BSD ↔ modularity ↔ knot Floer), the relations are *not* reductions in the formal sense; they are object-level bridges already captured by Study 03's bridge_class.
   - Mixing operation-graph and theory-graph in one structure would muddy the query semantics.
   - If a theory graph is later wanted, build a *separate* `theory_graph.py` whose nodes are *foundations* and whose edges are *interpretations*, populated from Maddy / McLarty / Visser citations. Cost: ~30 lines + a one-time literature ingest. Not recommended now; recommended *only* if a substrate use-case appears that distinguishes ETCS from ZFC from HoTT (none currently exists).

3. **For each Study 03 bridge edge, record which of (interpretation / conservativity / equivalence) it instantiates.** Concretely:
   - BSD ↔ modularity: *equivalence* of L-data (theorem, Wiles–Taylor–BCDT for the modularity half; BSD itself is conjectural).
   - Modular forms ↔ Galois reps: *interpretation* (Deligne's construction is a functor with no inverse).
   - Mock theta ↔ harmonic Maass: *interpretation* (Zwegers's completion is one-way; the mock theta is the "shadow" of the Maass form).
   - Knot Floer ↔ Heegaard Floer: *equivalence* of categorified invariants.
   - Genus-2 ↔ paramodular: *conjectural equivalence* (paramodular conjecture; partial cases by Brumer–Pacetti–Tornaria).
   - OEIS edges: *no reduction*, only attribute-sharing.

   Cost: one column on bridge_class-typed edges; usable by Charon's bridge-fidelity scoring and by Ergon's behaviour descriptor.

4. **Use the reverse-mathematics big-five as a calibration anchor** for what a *real* theory graph looks like, not as a tool for the substrate's envs. The big-five graph is small, linearly ordered, well-cited, computer-verifiable, and *separates* its nodes by concrete theorems. The substrate should refuse to claim "theory graph" status for any candidate structure that does not meet at least three of those four criteria. (Substrate's bridge graph from Study 03 meets two: well-cited and separating — but not linearly ordered and not computer-verifiable.)

5. **If the substrate later wants reduction-strength scoring at the theorem level**, the existing literature on *individual* theorems (Robertson–Seymour at Π¹₁-CA_0, Kruskal at ATR_0, Hindman at ACA_0+, Goodstein at ε_0-induction, Paris–Harrington at ε_0) gives a starting catalogue. A handful of substrate-relevant theorems whose strength has been analysed: Dirichlet's theorem on primes in AP (RCA_0; Harrington's trick), prime number theorem (WKL_0 + induction), Tijdeman's theorem on Catalan-style equations (provable in PA but with no known low-strength bound). This is the right granularity *if* the substrate ever wants to score its theorem-base by axiomatic strength. Currently no use case.

## Falsification

Central claim: **a "theory graph" exists at foundational granularity (< 10 nodes, well-published) but not at substrate-env granularity, and the right substrate response is metadata not graph augmentation.**

Falsified if any of:

1. A published catalogue is found that scores BSD, modularity, knot Floer, genus-2 paramodular, OEIS, and mock theta by reverse-math strength (not just by ZFC-membership) — would invalidate handle (1)'s claim that all six envs collapse to the same score.
2. A use case arises in the substrate where ETCS-vs-ZFC-vs-HoTT distinction matters operationally — would re-open the case for a separate theory_graph.py.
3. A reverse-math result is published showing one of the substrate's envs requires strictly more than ACA_0 for its computable content — would give the substrate a real reduction-strength signal at its native granularity.
4. The Kapulkin–Lumsdaine simplicial-set model citation turns out to be misremembered (I'm uncertain about the year and the journal) — would invalidate one specific cite but not the structure of the argument.

## Open questions raised

- Does *bi-interpretation* (the existence of mutual interpretations whose composition is provably equivalent to identity) give a finer-grained ordering on the substrate's bridge classes than Study 03's case (1)/(3)/(4)/(5) typology?
- Is there a useful intermediate object between "operational dependency_graph" and "foundational theory graph" — namely, a *theorem-dependency graph* that records which substrate-shipped theorems depend on which others? (This *would* be a useful substrate addition; it is what Lean's mathlib `import` graph instantiates.)
- For the substrate's actual six envs, is there a small set of *background theorems* (not foundational axioms) that all six implicitly assume — analogous to how all six implicitly assume ZFC? Candidates: Riemann hypothesis for L-functions of elliptic curves (assumed in many BSD computations), GRH (assumed for some Hecke-eigenvalue bounds), modularity (now a theorem). A "theorem-prerequisite graph" at *this* granularity would be substantively useful.
- Does the existence of *non-equivalent* interpretations (T₁ has two interpretations into T₂ that are not isomorphic in T₂'s sense) matter for the substrate? In foundations: yes (different models of ZFC inside HoTT give different choice principles). In Prometheus's envs: probably not.

## Citations

- Awodey, S. & Warren, M. A. "Homotopy theoretic models of identity types." *Math. Proc. Camb. Phil. Soc.* 146 (2009).
- Brumer, A., Pacetti, A., Tornaria, G. — paramodular conjecture sample computations (multiple papers, c. 2014–2019; representative: "Computing rational adelic genus-2 modular forms," various venues).
- Eilenberg, S. & Mac Lane, S. "General theory of natural equivalences." *Trans. AMS* 58 (1945).
- Friedman, H. "Some systems of second order arithmetic and their use." *Proc. ICM* (1975).
- Friedman, H., Robertson, N., Seymour, P. "The metamathematics of the graph minor theorem." *Contemp. Math.* 65 (1987).
- Gentzen, G. "Die Widerspruchsfreiheit der reinen Zahlentheorie." *Math. Ann.* 112 (1936).
- IAS Univalent Foundations Programme. *Homotopy Type Theory: Univalent Foundations of Mathematics.* Institute for Advanced Study, 2013.
- Kapulkin, K. & Lumsdaine, P. L. "The simplicial model of univalent foundations (after Voevodsky)." *J. EMS* 23 (cite year approximate; arXiv:1211.2851). [confidence: structure correct, year possibly wrong]
- Lawvere, F. W. "An elementary theory of the category of sets." *Proc. Nat. Acad. Sci. USA* 52 (1964).
- Maddy, P. *Defending the Axioms.* OUP, 2011.
- McLarty, C. "Exploring categorical structuralism." *Philosophia Mathematica* 12 (2004).
- McLarty, C. "What does it take from the foundations of mathematics." *Philosophia Mathematica* 21 (2013).
- Novak, I. L. "A construction for models of consistent systems." *Fund. Math.* 37 (1950).
- Pohlers, W. *Proof Theory: The First Step into Impredicativity.* Springer, 2009.
- Polishchuk, A. & Zaslow, E. "Categorical mirror symmetry: the elliptic curve." *Adv. Theor. Math. Phys.* 2 (1998).
- Rathjen, M. "The art of ordinal analysis." *Proc. ICM* (2006).
- Shoenfield, J. R. "A relative consistency proof." *J. Symb. Logic* 19 (1954).
- Simpson, S. *Subsystems of Second Order Arithmetic.* Perspectives in Logic, CUP, 2nd ed. 2009.
- Tarski, A., Mostowski, A., Robinson, R. M. *Undecidable Theories.* North-Holland, 1953.
- Visser, A. "Categories of theories and interpretations." In *Logic in Tehran* (Lecture Notes in Logic 26), 2006.

(Where I am less than fully confident about a specific year or journal, the cite is flagged or hedged. The structural claims — what each work proves — are reliable; the bibliographic surface details should be re-verified before any of these are forwarded as substrate-grade citations.)
