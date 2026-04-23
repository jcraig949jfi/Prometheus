---
catalog_name: Smooth knot concordance group — torsion classification
problem_id: knot_concordance
version: 1
version_timestamp: 2026-04-21T14:35:00Z
status: alpha
cnd_frame_status: cnd_frame
teeth_test_verdict: FAIL
teeth_test_sub_flavor: truth_axis_substrate_inaccessible
teeth_test_resolved: 2026-04-22
teeth_test_resolver: Harmonia_M2_sessionB
teeth_test_cross_resolver: Harmonia_M2_sessionC
teeth_test_doc: stoa/discussions/2026-04-22-teeth-test-on-existing-catalogs.md
surface_statement: Classify the torsion elements of the smooth knot concordance group C. Concretely: for which knots K is some finite connected-sum power K # K # ... # K smoothly slice (bounds a smoothly embedded disk in B^4), and are the only such knots the amphichiral order-2 ones, or is there hidden higher-order torsion?
anchors_stoa: stoa/predictions/open/2026-04-22-sessionD-teeth-test-stringency.md
---

## What the problem is really asking

Beneath the surface statement, at least six disciplines hear a different question:

1. **Is C a "clean" abelian group, or is its torsion subgroup an obstruction-theoretic swamp?**
   The topological concordance group C^top has a known 2-torsion piece (from amphichiral knots); Levine's algebraic concordance group has 2- and 4-torsion. The smooth C sits *between* these and is believed to be far wilder. Does smooth C have 2-torsion only, 2- and 4-torsion, or p-torsion for arbitrarily many primes p?

2. **Is smoothness-vs-topologicality a discrete invariant that lives on a single knot, or only a group-level phenomenon?** A knot being topologically slice but not smoothly slice (Casson-Gordon, Freedman-era phenomena) could be a lone anomaly or could generate an infinitely-branching torsion structure. The question is whether "smooth" is a coordinate or a derived property.

3. **Does every torsion class admit a finite 4-dimensional certificate?** If K has order n in C, is there a compact 4-manifold X with specific intersection form that exhibits the concordance to the unknot of nK? This asks whether torsion is *witnessable* — a proof-theoretic question dressed as topology.

4. **Is the concordance group torsion question a shadow of a gauge-theoretic rigidity phenomenon?** Donaldson's diagonalizability theorem, Furuta's 10/8-inequality, and Heegaard Floer d-invariants all produce concordance obstructions. The torsion question is whether the known obstructions are complete or whether undiscovered gauge-theoretic invariants detect new torsion.

5. **Is smooth C essentially infinite-rank-plus-Z/2, or does the smooth/topological discrepancy introduce densely many torsion classes?** A structural question: is the torsion subgroup T(C) countably-generated, finitely-presented, recursive, or not even recursively enumerable? Each answer has different foundational weight.

6. **Is ribbon-ness a decidable predicate?** If ribbon ⊊ smoothly slice strictly (the slice-ribbon conjecture fails), the torsion question inherits an undecidability flavor from the word problem in knot groups. Computer-checking "is K ribbon?" may itself be algorithmically unsolvable in general.

## Data provenance

**The problem.** The concordance group was defined by Fox-Milnor (1966); Levine's algebraic concordance group (1969) supplied the first structural handle. The smooth vs topological distinction became sharp in the early 1980s with Freedman's topological category theorems and Donaldson's diagonalizability. The torsion question in smooth C has been open the entire time: no element of smooth C is known to be of odd finite order, no element is known to have order strictly greater than 2 in a non-trivial way not covered by Levine's invariants, and structural results are sparse.

**What data exists.**

- `cartography/knots/data/knots.json` — 13K knots from KnotInfo; 2,977 entries have polynomial data (Alexander + Jones coefficients). This is the substrate for any Prometheus lens that wants to anchor in empirical concordance invariants.
- KnotInfo provides per-knot columns for: smooth and topological 4-genus, concordance genus, signature, Arf invariant, Rasmussen s-invariant, Ozsvath-Szabo tau, upsilon function, epsilon invariant, nu-plus, slice status (smooth and topological), ribbon status.
- Silent Islands Analysis (`aporia/mathematics/silent_islands_analysis.md` Island 1: KNOTS) enumerates the expected bridges: Alexander polynomial → number field, Jones at roots of unity → modular forms, Mahler measure of A-polynomial → L-values, 2-bridge → elliptic-curve correspondence, volume conjecture → hyperbolic geometry. All five bridges are relevant to concordance obstructions.
- `aporia/mathematics/lesser_known_open_problems.md` entry 19: states the problem; notes the Donaldson/Heegaard Floer partial obstructions. Entry 20 (slice-ribbon conjecture) is the nearest neighbor — same knot data, question about the slicing filtration.
- In LMFDB-adjacent territory: elliptic-curve L-values (Deninger-Boyd bridge), modular-form Hecke eigenvalues (quantum-invariant bridge), number-field discriminants (Alexander-polynomial-root bridge).

**The computational record.**

- Smooth torsion elements known: amphichiral knots of order 2 (many examples; e.g., the figure-eight generates an order-2 class). Arf invariant gives a surjection C → Z/2.
- Levine's algebraic concordance group has 2-torsion and 4-torsion detectable from Seifert-form signatures. Casson-Gordon invariants detect further topological torsion.
- No *odd-order* torsion is known. No smooth-torsion class of order ≥ 4 is known that is not already detected algebraically. The gap between "what we can detect" and "what might exist" is the problem.
- Hom's 2014 and subsequent results using upsilon and epsilon built infinite Z^infinity subgroups of smooth C, refining the rank picture, but they *killed* hypothesized torsion rather than finding it.

**Shape of the data.** Concordance invariants (tau, s, upsilon, nu-plus, epsilon) are integer- or piecewise-linear-function-valued; they form a commuting tower of surjective homomorphisms from C to Z, Z, PL, Z, and an ordered group respectively. Torsion maps to 0 under all Z-valued homomorphisms; so any torsion class is invisible to the "classical" concordance invariants and must be detected by fundamentally-different-type invariants (epsilon, or structure beyond).

## Motivations

- **Core low-dimensional topology.** C is a central object. Its structure theorem would resolve an enormous class of 4-manifold slicing questions.
- **Smooth-vs-topological gap.** C smooth vs C topological is the archetype of the gap between smooth and topological 4-manifolds; understanding torsion would refine that gap at the concordance level.
- **Gauge-theoretic invariants as a testbed.** Donaldson, Seiberg-Witten, Heegaard Floer, Khovanov homology — each new invariant produces a new concordance obstruction. The torsion question asks which obstructions are sharp and which are already subsumed.
- **Connections to algebraic number theory.** Mahler measures of Alexander polynomials (Boyd-Deninger) bridge to L-values; Alexander polynomial roots live in number fields. Torsion in C interacts with cyclotomic structure in the Alexander module.
- **Quantum topology.** Colored Jones polynomials and Kashaev invariants at roots of unity detect fine concordance structure. Root-of-unity values are conjecturally tied to hyperbolic volumes via the volume conjecture.
- **Prometheus-aligned.** KNOTS is a silent island in our tensor. Re-animating it via a lens catalog is itself a test of whether the `SHADOWS_ON_WALL@v1` frame can convert a silent domain into a coupled one.
- **Pedagogical / career.** Concordance is accessible enough to be an early-career problem but deep enough to be a Millennium-adjacent one.

## Lens catalog (23 entries — 18 adapted from Collatz + 3 NEW knot-specific + 2 BLENDED)

### Core discipline adaptations (lenses 1–18 from Collatz palette)

### Lens 1 — Ergodic / invariant-measure theory

- **Discipline:** Ergodic theory / mapping class group dynamics
- **Description:** Treat concordance as an equivalence relation on a (huge) space of knots; ask whether the mapping-class-group action on knot diagrams, or the SL(2,R)-action arising from hyperbolic knot monodromy, carries an invariant measure that separates torsion classes from the identity. Thurston's geometrization makes this partially concrete: for hyperbolic knots the Weil-Petersson measure on Teichmuller space of the complement supplies a candidate.
- **Status:** PROPOSED
- **Prior result / stance:** an ergodic theorist would predict that an invariant measure exists on the hyperbolic-knots stratum but sees the full knot-space as a stratified object where different strata carry different invariants; torsion classes should be detectable as *atoms* under a suitably chosen invariant measure. A concrete prediction: the support of such a measure under the cabling operation should have fractal dimension strictly below the ambient dimension on the torsion locus. Plausible but unverified.
- **Forbidden moves (under this prior):** must not invoke gauge theory / Floer homology / Khovanov homology; must not use the word "obstruction" in the algebraic-topology sense.
- **Data hooks:** hyperbolic volume column (where present), Alexander polynomial degree distribution in `cartography/knots/data/knots.json`; candidate ensembles built from cabling operations on the 2,977-knot polynomial subset.
- **Tier contribution:** Yes — ergodic theory is genuinely orthogonal to algebraic-topology priors.

### Lens 2 — Information-theoretic / Kolmogorov complexity

- **Discipline:** Algorithmic information theory
- **Description:** Treat each knot as a finite program producing its invariant tuple (Alexander coefficients, Jones coefficients, tau, s, upsilon, epsilon). Torsion classes in C are exactly those knots whose finite-power connected-sum program compresses to the unknot's program. Ask whether there is a Shannon-style capacity bound on how much torsion can be packed into a given crossing-number budget.
- **Status:** PROPOSED
- **Prior result / stance:** an information theorist would predict that torsion is *rare* by entropic arguments (slice knots have finite 4-genus, which is an MDL-style minimum description; generic knots have high 4-genus and are non-slice by counting). Plausible prediction: number of non-trivial torsion classes at crossing number n grows at most polynomially, much slower than the total count of knots (which grows exponentially). Plausible but unverified.
- **Forbidden moves:** must not name specific gauge-theoretic invariants (tau, s, upsilon) as primitives; must reformulate them in coding-length terms.
- **Data hooks:** crossing-number × slice-genus joint histogram on KnotInfo; Kolmogorov-proxy via minimal Gauss-code length on the 13K knots.
- **Tier contribution:** Yes.

### Lens 3 — Random walk / probabilistic heuristic

- **Discipline:** Probability theory
- **Description:** Model random knots via random diagrams, random braid words, or Petaluma-model random knots; compute induced distribution on concordance invariants and ask the probability that a random knot has finite order in C. If the distribution of, say, Rasmussen s concentrates on Z with Gaussian-like fluctuations as crossing number grows, torsion is asymptotically zero-density.
- **Status:** PROPOSED
- **Prior result / stance:** a probabilist would predict random-knot concordance invariants follow a CLT-regime with variance growing linearly in crossing number; probability that a random knot is of finite order in C goes to zero exponentially. Sharper: P(K is of order k ≥ 2 in C) ~ C_k · exp(-c · n) for n = crossing number. Plausible.
- **Forbidden moves:** must not invoke Heegaard Floer or Khovanov as primitives; must work only with invariant distributions and null-sampling.
- **Data hooks:** s, tau, upsilon, epsilon distributions vs crossing number in KnotInfo; Petaluma-random-knot simulations as a null.
- **Tier contribution:** Yes.

### Lens 4 — Graph-theoretic / functional graph

- **Discipline:** Combinatorics / graph theory
- **Description:** Build the "concordance graph" G_c: vertices = knots, edges = concordance-by-a-single-handle-attachment. Torsion in C is encoded in finite cycles passing through the unknot vertex. Ask about cycle structure, connectivity, and whether the unknot is a bottleneck with bounded-degree cycles.
- **Status:** PROPOSED
- **Prior result / stance:** a graph theorist would expect G_c to be highly connected in its bulk but with the unknot vertex having a structured neighborhood: torsion ↔ short cycles through the identity vertex. Predicts cycle girth through unknot ≥ 3 implies no odd torsion of corresponding order. Plausible but under-explored.
- **Forbidden moves:** must not use continuous invariants (upsilon) or smooth-topological distinction; stay in discrete combinatorial vocabulary.
- **Data hooks:** mutation and satellite operations on the 13K knot table induce edges; can we enumerate cycles under these operations?
- **Tier contribution:** Yes.

### Lens 5 — Computability / proof theory

- **Discipline:** Mathematical logic
- **Description:** Is "K is torsion in smooth C" decidable, semi-decidable, or independent of standard axioms? The question of "K smoothly slice" sits at Sigma^0_1 (searching for a disk); "K of order exactly k" is a Sigma^0_2-or-worse statement. Ask about proof-theoretic strength.
- **Status:** PROPOSED
- **Prior result / stance:** a proof theorist would predict: "K smoothly slice" is Sigma^0_1 (semi-decidable via search over PL disks in B^4 with bounded complexity); "K has order k in C" requires bounding the search; the universal statement "smooth C has no torsion of order > 2" could be Pi^0_2 and require transfinite induction (Goodstein-strength) to formalize a proof. Plausible but unverified; Goodstein-analogue is speculative.
- **Forbidden moves:** must not invoke any specific topological invariant; must reason purely syntactically about the logical form of the statements.
- **Data hooks:** meta-level; no direct tensor hook. Proof-assistant (Lean/Coq) experiments encoding concordance as a predicate.
- **Tier contribution:** Yes — orthogonal to all object-level lenses.

### Lens 6 — Density / almost-all arguments (Terras-style)

- **Discipline:** Analytic / density theory
- **Description:** Show that "almost all" knots (density 1 in some sensible enumeration) are *not* torsion in C. Terras-style: density of non-slice / non-torsion knots among all knots of crossing number ≤ N tends to 1 as N → ∞.
- **Status:** PROPOSED
- **Prior result / stance:** an analytic density theorist would expect this to be provable by counting: slice knots of crossing number ≤ N are far fewer than total knots. Torsion ⊆ slice-powers, so the same bound. Stance: density of torsion = 0 is plausibly elementary; the hard part is the remaining zero-density set.
- **Forbidden moves:** no smooth-topological distinction; work in whichever category permits counting arguments.
- **Data hooks:** KnotInfo slice-status counts vs crossing number curve.
- **Tier contribution:** Yes.

### Lens 7 — Cycle-counting combinatorial (Krasikov-Lagarias style)

- **Discipline:** Analytic number theory / combinatorial
- **Description:** Bound the number of torsion classes of order exactly k in C by combinatorial-height arguments. Krasikov-Lagarias achieve O(L^{1/3}) for Collatz cycles of length ≤ L; analogously, can we bound #(order-k classes represented by crossing-number ≤ n) by something like n^{c(k)}?
- **Status:** PROPOSED
- **Prior result / stance:** a combinatorial analyst would predict a polynomial-in-n bound on torsion classes of bounded order and bounded representative-complexity, with exponent depending on the order k. Speculative specific form: #(order-k, crossing ≤ n) ≤ C_k · n^{k/2}. Numbers invented; stance is plausible.
- **Forbidden moves:** no gauge theory; no continuous invariants.
- **Data hooks:** empirical: enumerate candidate order-k representatives among the 2,977 polynomial-data knots by looking for knots with specific Alexander-polynomial torsion structure.
- **Tier contribution:** Yes.

### Lens 8 — Logarithmic density / Tao-style near-solution

- **Discipline:** Analytic number theory / density
- **Description:** Prove that for almost all knots (in a log-density sense), connected-sum powers grow without bound under any finite set of homomorphisms C → Z. This is a "near-solution" analogue to Tao 2019 on Collatz: show that the obstruction is generic, without showing it is universal.
- **Status:** PROPOSED
- **Prior result / stance:** a Tao-style analyst would predict this is proveable with current tools — the log-density statement is strictly weaker than the full torsion classification. Expected stance: almost-all result attainable; full classification blocked by the same "specific family" issue that blocks Collatz.
- **Forbidden moves:** no appeal to specific invariant completeness.
- **Data hooks:** empirical log-density scatter of tau/s/upsilon growth under connected-sum powers.
- **Tier contribution:** Yes (distinct from pure density-1 Lens 6 by being a log-density refinement).

### Lens 9 — FRACTRAN / computational universality

- **Discipline:** Theoretical computer science
- **Description:** Concordance is decidable as a predicate only if the slice-disk search space is computably bounded. The word problem in knot groups is decidable, but the smooth-slice predicate embeds 4-dimensional smooth-category questions, which touch on undecidable territory (smooth 4-dim Poincare, smooth structures). Ask whether "K is smoothly slice" or "K is torsion" encodes a universal halting problem under some reduction.
- **Status:** PROPOSED
- **Prior result / stance:** a TCS theorist would predict: "K is topologically slice" is decidable given Freedman's classification for simply-connected 4-manifolds restricted to boundary; "K is smoothly slice" is *not known* to be decidable. Stance: plausible that smooth-slice is undecidable in general but no reduction from a universal problem is known. Compare to Markov's theorem on homeomorphism of 4-manifolds (undecidable).
- **Forbidden moves:** no specific topological-invariant names; stay in reduction/decidability vocabulary.
- **Data hooks:** meta-level; proof-assistant encoding of smooth-slice predicate.
- **Tier contribution:** Yes — orthogonal to Lens 5 (Lens 5 is syntactic form; Lens 9 is computational universality).

### Lens 10 — 2-adic / symbolic dynamics

- **Discipline:** p-adic analysis / symbolic dynamics
- **Description:** Extend concordance invariants to p-adic completions: Alexander polynomials have Z-coefficients, so they embed in Z_p[t] for any p; Mahler measure of the Alexander polynomial has a p-adic analogue (Mahler's p-adic function). Ask about p-adic ergodic properties of the shift action on Alexander-polynomial root profiles.
- **Status:** PROPOSED
- **Prior result / stance:** a p-adic analyst would predict that the torsion subgroup of C has a natural p-adic filtration coming from p-primary decomposition of the Alexander module. Stance: torsion at prime p in C is detected by p-adic valuation of the Alexander polynomial evaluated at -1 (the determinant). Speculative; no specific existing theorem asserted here.
- **Forbidden moves:** no smooth/topological distinction; no 4-dimensional reasoning.
- **Data hooks:** Alexander polynomial evaluations at -1 (determinant) for all 2,977 knots with polynomial data; p-adic valuations sorted.
- **Tier contribution:** Yes.

### Lens 11 — Physics / spin-chain / statistical mechanics

- **Discipline:** Mathematical physics
- **Description:** The Jones polynomial arises as a partition function of a 2D statistical mechanical model (Potts-model / Temperley-Lieb / Kauffman bracket). Concordance invariants can be phrased as phase-transition order parameters. Torsion in C would be a "symmetry-broken phase" where connected-sum powers of a knot return to a symmetric configuration.
- **Status:** PROPOSED
- **Prior result / stance:** a mathematical physicist would predict that torsion classes correspond to symmetry-enhanced phase points; they are measure-zero in coupling-constant space (the "cobordism phase diagram"). Analogy: torsion order k ↔ Z/k symmetry of a phase.
- **Forbidden moves:** cannot reference Heegaard Floer, Khovanov, or any homological invariant; must stay in partition-function language.
- **Data hooks:** Jones polynomial evaluations at roots of unity for 2,977 knots; look for phase-transition-like behavior in the evaluation distribution.
- **Tier contribution:** Yes.

### Lens 12 — Markov chain / coupling arguments

- **Discipline:** Probability theory
- **Description:** Construct a Markov chain on knot classes where transitions are crossing changes or band surgeries. Couple this chain with a "random-walk on C"; torsion classes are recurrent points of the chain under concordance equivalence.
- **Status:** PROPOSED
- **Prior result / stance:** a probabilist would predict that the chain mixes rapidly on the non-torsion bulk but has "trap" states at torsion classes. Expected measurement: mixing time on the non-torsion component ≪ mixing time when torsion traps are included. Plausible; unverified.
- **Forbidden moves:** no appeal to specific invariants; work only with Markov structure.
- **Data hooks:** crossing-change-distance tables in KnotInfo (unknotting number as a proxy).
- **Tier contribution:** Marginal (overlaps with Lens 3 random-walk; independent because of coupling primitive).

### Lens 13 — Algebraic / ring-theoretic

- **Discipline:** Algebra (commutative and non-commutative)
- **Description:** The smooth concordance group C is an abelian group. Structurally: is it the quotient of a free abelian group by relations coming from the slice-ribbon filtration? Torsion is then generated-and-related; ask about generators/relations explicitly.
- **Status:** PROPOSED
- **Prior result / stance:** an algebraist would predict C has the structure of a countable abelian group with a Z^∞ quotient (from concordance invariants mapping to Z) and a torsion subgroup T(C) that is the kernel of this quotient map. T(C) is non-trivial (Arf) and conjecturally has complicated p-primary structure. Stance: classify T(C) via its p-primary decomposition, expect 2-primary dominant.
- **Forbidden moves:** no smooth/topological-category arguments; treat C as an abstract abelian group given by generators and relations.
- **Data hooks:** Arf invariant column; signature mod 4; determinant mod various primes.
- **Tier contribution:** Yes.

### Lens 14 — Formal verification (Lean/Coq)

- **Discipline:** Formal methods
- **Description:** Machine-verify specific concordance claims (e.g., formal proofs that specific knots are not slice using tau, s, upsilon invariants). Build a formal library that encodes concordance predicates and verifies empirical torsion-free claims.
- **Status:** PROPOSED
- **Prior result / stance:** a formal-methods researcher would predict near-term feasibility of formalizing Rasmussen's theorem (genus bound via s-invariant) in Lean, and medium-term feasibility of formalizing upsilon-obstructions. Full torsion-freeness is *not* predicted formalizable in < 5 years. Plausible estimate.
- **Forbidden moves:** cannot appeal to heuristic arguments; every claim must be rendered as a formal proposition.
- **Data hooks:** meta-level; Lean mathlib for topology.
- **Tier contribution:** Partial (verification rather than discovery).

### Lens 15 — ML pattern-finding

- **Discipline:** Machine learning applied to math
- **Description:** Train models on (Alexander coeffs, Jones coeffs, known invariants) → predict concordance class / torsion order / slice genus. Identify knots whose predicted invariants disagree with measured — those are candidates for new torsion classes.
- **Status:** PROPOSED
- **Prior result / stance:** an ML-applied-to-math researcher would predict that gradient-boosted or transformer-based models can predict tau, s, upsilon from polynomial data with high accuracy on seen classes but will systematically fail at torsion classes precisely because torsion is the *low-data* regime. Useful as an outlier-detector, not a direct solver. Plausible; aligns with Davies-et-al 2021 pattern.
- **Forbidden moves:** must not claim ML discoveries as theorems; outputs are hypotheses to verify.
- **Data hooks:** all 2,977 polynomial-data knots as training set; held-out set of known-torsion (amphichiral) and known-non-torsion knots.
- **Tier contribution:** Yes (heuristic discovery lens, distinct from others).

### Lens 16 — Graph spectral analysis

- **Discipline:** Spectral graph theory
- **Description:** The concordance graph (Lens 4) or the knot graph (mutation adjacency) has an adjacency matrix whose spectrum encodes structural features. Torsion classes correspond to specific eigenvectors with finite-order rotational symmetry.
- **Status:** PROPOSED
- **Prior result / stance:** a spectral graph theorist would predict the concordance-graph Laplacian spectrum has a small set of eigenvectors supported near the unknot vertex corresponding to torsion classes; the spectral gap between the first "trivial" eigenvector and the torsion-supported ones is the quantitative torsion barrier. Speculative but analogous to well-trodden paths in finite-group spectral theory.
- **Forbidden moves:** no topological-invariant appeal; work with adjacency-matrix primitives.
- **Data hooks:** construct mutation-adjacency graph from KnotInfo; compute Laplacian spectrum on the 13K knots subgraph.
- **Tier contribution:** Yes.

### Lens 17 — Dynamical Manin-Mumford analogue

- **Discipline:** Arithmetic dynamics
- **Description:** Manin-Mumford: preperiodic points of an algebraic dynamical system are rigid. Analogue for concordance: connected-sum is a "dynamical operation" on the set of knots; torsion classes are preperiodic points under n-fold self-sum. Ask whether a rigidity theorem holds: the set of torsion classes has bounded height in any reasonable concordance-height function.
- **Status:** PROPOSED
- **Prior result / stance:** an arithmetic dynamicist would predict torsion classes have bounded concordance-height (bounded 4-genus, bounded crossing number representative, bounded Alexander-polynomial degree). Stance: T(C) has a "small height" representative theorem: every torsion class has a representative of crossing number ≤ f(order). f unknown; speculative.
- **Forbidden moves:** no smooth/topological 4-manifold constructions; stay in iteration-of-operation vocabulary.
- **Data hooks:** for each torsion candidate, minimum-crossing representative; test the bounded-height hypothesis.
- **Tier contribution:** Yes.

### Lens 18 — Real-valued continuous extension

- **Discipline:** Real analysis / smooth dynamics
- **Description:** Upsilon (Ozsvath-Stipsicz-Szabo) is already a concordance invariant taking values in piecewise-linear real-valued functions on [0,2]. This IS a continuous-extension lens in action. Push further: are there continuous families of concordance invariants (parametrized by, say, a real parameter t), and does the *derivative* with respect to t detect torsion?
- **Status:** PROPOSED (upsilon already exists and is partially applied at the community level)
- **Prior result / stance:** a real-analytic continuer would predict that a continuous family of concordance invariants defined on a connected parameter space detects torsion as zeros of all members of the family. Torsion classes are *common zeros* of an infinite continuous family; checking finitely many members gives a semi-decidable filter. Plausible; upsilon's zero set on torsion classes is partially verified.
- **Forbidden moves:** no discrete-invariant-only arguments; must treat the invariant as a function on a parameter space.
- **Data hooks:** upsilon function data in KnotInfo (where available); look for zero patterns on known amphichiral knots.
- **Tier contribution:** Yes.

### New knot-specific lenses (lenses 19–21)

### Lens 19 — Gauge theory / Donaldson-Floer invariants [NEW]

- **Discipline:** Gauge theory / 4-manifold topology
- **Description:** Donaldson's theorem (diagonalizability of definite 4-manifolds' intersection forms) produces concordance obstructions (Donaldson, Furuta, Fintushel-Stern). Heegaard Floer homology (Ozsvath-Szabo) gives the d-invariants and tau. Seiberg-Witten gives the 10/8-inequality. The full concordance-obstruction hierarchy comes from 4-dimensional gauge theory.
- **Status:** NEW
- **Prior result / stance:** a gauge theorist would predict that all currently-known concordance torsion is detected by some already-known gauge-theoretic invariant; the "open" torsion (knots for which all known invariants vanish but smooth-slice is still unknown) is the genuinely hard set. Stance: torsion in smooth C beyond Arf is detected by d-invariants of the double-branched cover; no torsion of odd prime order exists (2-adic dominance). Plausible given the pattern; specific predictions invented.
- **Forbidden moves:** cannot use purely algebraic (Levine-style) arguments; cannot use probabilistic arguments; no pure combinatorics.
- **Data hooks:** d-invariants of double branched covers (computable from determinant + signature); tau-invariant column in KnotInfo. Cross-reference with known 2-torsion (amphichiral) knots.
- **Tier contribution:** Yes — this is the established mainstream lens; we include it so the catalog isn't blind to orthodoxy.

### Lens 20 — Khovanov homology / categorification [NEW]

- **Discipline:** Categorified knot homology
- **Description:** Khovanov homology is a bigraded homology theory categorifying the Jones polynomial. Rasmussen's s-invariant gives a concordance obstruction. Ask whether the full Khovanov homology — not just its Euler-characteristic shadow Jones — detects torsion that the Jones polynomial alone misses.
- **Status:** NEW
- **Prior result / stance:** a Khovanov-homology theorist would predict there exists a knot whose Jones polynomial has no concordance signature but whose Khovanov homology does — suggesting torsion detectable only at the categorified level. Stance: Bar-Natan's "s-like" invariants beyond s detect further torsion. Speculative but aligned with ongoing research.
- **Forbidden moves:** no gauge-theoretic appeals; no Heegaard Floer; must work with Khovanov-chain-complex primitives.
- **Data hooks:** reduced Khovanov homology data for the 2,977 polynomial-data knots (available via KnotAtlas / knotinfo integration); torsion in Khovanov homology as a direct feature.
- **Tier contribution:** Yes — genuinely orthogonal to both gauge theory and Jones polynomial.

### Lens 21 — Hyperbolic geometry / volume conjecture [NEW]

- **Discipline:** Hyperbolic 3-manifold geometry
- **Description:** Every non-satellite-non-torus knot has a complete hyperbolic structure on its complement, with a well-defined volume. The volume conjecture (Kashaev-Murakami-Murakami) relates volume to the growth rate of the colored Jones polynomial at roots of unity. Torsion in C has no known direct volume signature, but amphichiral knots have symmetric hyperbolic structures.
- **Status:** NEW
- **Prior result / stance:** a hyperbolic geometer would predict that torsion classes in C correspond exactly to knots whose complement admits an orientation-reversing isometry (negative-amphichiral, for order 2) or other finite-order symmetry. Full torsion classification reduces to classification of finite-order symmetries of hyperbolic 3-manifolds with cusp. Stance: smooth C has only 2-torsion (from order-2 symmetry) and no higher torsion (no higher-order amphichirality that survives smooth category).
- **Forbidden moves:** no categorified homological invariants; no gauge-theoretic invariants; must work in Riemannian-geometry vocabulary.
- **Data hooks:** hyperbolic volume column for 2,977 polynomial-data knots; symmetry group column (from KnotInfo). Check: do all known torsion classes have non-trivial isometry group?
- **Tier contribution:** Yes — highly orthogonal.

### Blended lenses (lenses 22–23)

### Lens 22 — Information-theoretic × hyperbolic volume [BLEND of 2 + 21]

- **Discipline:** Algorithmic information theory blended with hyperbolic geometry
- **Description:** The Kashaev invariant is a sum of dilogarithms whose leading asymptotic is the hyperbolic volume. Treat volume as an information-theoretic quantity: the "description length" of the hyperbolic structure. Ask whether torsion classes are compressibility-minimizers under the volume-complexity measure. This fuses Lens 2 (Kolmogorov) and Lens 21 (hyperbolic).
- **Status:** BLEND
- **Prior result / stance:** a blended theorist would predict torsion classes have *anomalously low* hyperbolic-volume complexity per crossing number — a blended compressibility measure singles them out. Stance: define complexity ρ(K) = hyperbolic_volume(K) / crossing_number(K); torsion classes lie on a specific sub-quantile of ρ. This is a compression-candidate direction.
- **Forbidden moves:** cannot use either pure Kolmogorov arguments or pure hyperbolic arguments in isolation; the blend must commit to the joint measure.
- **Data hooks:** joint (hyperbolic_volume, crossing_number) histogram for the 2,977 polynomial-data knots; check whether known amphichiral (2-torsion) knots cluster in a specific ρ-quantile.
- **Tier contribution:** Yes — blended primitives count as one lens of their own for `SHADOWS_ON_WALL@v1` purposes when the primitive genuinely differs.

### Lens 23 — FRACTRAN × formal verification [BLEND of 9 + 14]

- **Discipline:** Computational universality blended with formal methods
- **Description:** Frame ribbon-ness (strictly-constructive slicing via ribbon disks) as a partial-recursive predicate and attempt to formally prove/disprove its decidability. If ribbon-ness embeds a universal halting problem (via the word problem in knot groups, which is decidable but for *smooth-ribbon* as a richer predicate), then the slice-ribbon conjecture is itself undecidable in certain axiomatic systems. This fuses Lens 9 (FRACTRAN) and Lens 14 (formal methods).
- **Status:** BLEND
- **Prior result / stance:** a blended theorist would predict: ribbon-ness is semi-decidable (search over finite presentations of a ribbon disk) but its non-provability for specific knots might require set-theoretic axioms stronger than ZFC. Stance: slice-ribbon conjecture's failure (if it fails) is undecidable in PA but decidable in ZFC plus a large-cardinal axiom. Speculative; offered as first-pass.
- **Forbidden moves:** cannot separate decidability from formal-verifiability; must treat them as a joint question.
- **Data hooks:** meta-level; Lean encoding of ribbon predicate + non-termination analysis.
- **Tier contribution:** Yes — as a distinct blended primitive.

## Cross-lens summary

- **Total lenses cataloged:** 23 (18 Collatz-palette adaptations + 3 NEW knot-specific + 2 BLEND)
- **PROPOSED:** 18 (Lenses 1–18)
- **NEW:** 3 (Lenses 19–21)
- **BLEND:** 2 (Lenses 22–23)
- **SKIP:** 0 — after evaluation, every Collatz-palette lens transported with at least a plausible analogue. A near-skip was Lens 18 (real-valued continuous extension), which is already realized by upsilon; we kept it as PROPOSED and noted community partial-application. Another near-skip was Lens 17 (dynamical Manin-Mumford), where the analogy is strained; we kept it because connected-sum plays the role of iteration and the rigidity question is natural.
- **APPLIED (by Prometheus):** 0 — this is first-pass catalog construction, not a multi-perspective attack run. No threads have been launched.

**Predicted cross-lens verdict type:** `mixed`.

Rationale: the truth axis (does smooth C have higher torsion?) is predicted to split the lenses. Lenses 13 (algebraic, via 2-primary decomposition), 19 (gauge theory, mainstream prior), and 21 (hyperbolic, symmetry-based argument) all predict torsion = Z/2 only, no higher. Lenses 20 (Khovanov, expects new categorified obstructions), 10 (2-adic, p-primary detection possible at any p), and 11 (physics / symmetry-broken phases, allows Z/k phases) allow hidden higher torsion. That is a direction-of-stance disagreement, not a magnitude one — so the shape is `map_of_disagreement` on the truth axis.

On the provability / decidability axis, Lens 5 (proof theory) and Lens 9 (FRACTRAN) predict the full classification requires strength beyond PA; Lenses 6, 7, 8 (density / counting / log-density) expect elementary-descent tools suffice for weaker versions. Similar `map_of_disagreement`.

On the data-access axis — what Prometheus can compute — most lenses converge on the same dataset hooks: the 2,977-knot polynomial-data subset, with specific columns (Alexander determinant, tau, s, upsilon, crossing number, hyperbolic volume). This is `convergent_triangulation` on the measurement proposal.

Hence `mixed`: divergent on stance, convergent on what to measure.

**Specific primitive that disagreement exposes.** The axis of genuine disagreement is whether "torsion order > 2 in smooth C" is detectable by *any* invariant computable from (Alexander polynomial, Jones polynomial, signature, standard Floer/Khovanov tuples). Pro-torsion-above-2 lenses (Lens 10, 20) say detection requires invariants not yet in common use (new p-adic valuations, uncaptured Khovanov torsion). Against-torsion-above-2 lenses (Lens 13, 19, 21) say current invariants are sufficient. The primitive exposed is: **is there an invariant beyond d, tau, s, upsilon, epsilon, Khovanov-H^* that is concordance-invariant and distinguishes hypothetical higher-order torsion classes?** This is an implicit "completeness of the invariant catalogue" question — and it's exactly the shape of `LENS_MISMATCH` at Level 3 (`lens_requires_new_primitive`).

**`LENS_MISMATCH` candidates in the current Prometheus knot row.** The knot domain is Silent Island 1 in the tensor (per `aporia/mathematics/silent_islands_analysis.md`). The current tensor features for knots are 28 raw polynomial coefficients (padded Alexander + Jones). Under this catalog:

- The current lens is *distributional over raw polynomial coefficients*. This is Level 1 or Level 2 lens mismatch (`lens_coarse` / `lens_wrong_category`). The mathematically-load-bearing primitives for concordance — Mahler measure, determinant mod n, tau, s, upsilon, hyperbolic volume — are *nonlinear* functions of the coefficients and are not in the feature set. The silent-island diagnosis in `silent_islands_analysis.md` P1.3 ("feature re-encoding") is the Prometheus-internal language for this same lens-mismatch.
- Prediction: if the knot row is re-encoded with the concordance-relevant 6 features (Mahler measure, determinant, signature, Alexander-polynomial degree, hyperbolic volume, tau), coupling to NF and EC rises from rank 0–1 to rank ≥ 3. This is a `LENS_COARSE` → `lens_adequate` demotion for the current knot-silence signal, and the transition predicts new F-ID candidates once the re-encoding lands.
- Candidate F-IDs this catalog could seed: **F_knot_concordance_torsion_detectability** (primary: are the standard invariants complete?) and **F_mahler_L_value_matches** (secondary: does P1.1 from silent_islands find ≥ 50 matches?).

**Priority lens follow-ups (from catalog to action).**

1. **Lens 19 (gauge theory) + Lens 20 (Khovanov)** — the pair that defines the current orthodoxy; any Prometheus attack must at minimum reproduce their predictions on the 2,977-knot dataset before claiming a new lens-mismatch.
2. **Lens 22 (information × hyperbolic blend)** — HIGH priority as a compression-candidate lens; computable on the existing data (hyperbolic volume + crossing number columns); directly testable.
3. **Lens 10 (2-adic)** — MEDIUM; gives a p-adic re-encoding of the Alexander polynomial that is one of the natural follow-ups to silent_islands P1.3.
4. **Lens 5 + Lens 9 (proof-theoretic pair)** — LOW priority for substrate but HIGH for methodology: this is the spot where running a multi-perspective attack may produce the same truth-vs-provability axis split that Collatz produced.

**First concrete data-hook proposed.** Compute the 6-feature re-encoding of the 2,977 polynomial-data knots per `silent_islands_analysis.md` P1.3, specifically: (Mahler measure of Alexander, determinant, signature, Alexander-polynomial degree, hyperbolic volume, Rasmussen s-invariant or Ozsvath-Szabo tau — whichever is populated). Cross-reference the resulting 2,977 × 6 tensor block against EC L-values and NF invariants. Expected first-pass yield: ≥ 3 novel couplings, seeding both F_knot_concordance_torsion_detectability and F_mahler_L_value_matches.

## Connections

**To other open problems.**
- Slice-ribbon conjecture (lesser-known #20) — parallel knot-theoretic rigidity; Lens 23 (FRACTRAN × formal) targets this directly.
- Jones polynomial detects the unknot (MATH-0332) — related detection-completeness question; shares Lenses 15, 20.
- Volume conjecture — Lens 21 primary lens; also feeds into Lens 22 blend.
- Lehmer's conjecture — connects via Lens 19 in Lehmer's catalog (Mahler measure of Alexander polynomial bounds hyperbolic volume per Silver-Williams). A positive Lehmer gap result would constrain Mahler measures of Alexander polynomials and thus this catalog's Lens 22.
- Langlands program via Deninger-Boyd bridge — Mahler measures of A-polynomials equaling L-values of EC (see Lehmer Lens 7) connects knot concordance to arithmetic geometry.

**To Prometheus symbols.**
- `SHADOWS_ON_WALL@v1` — this catalog is the operational implementation of the principle for the knot concordance problem. Predicted cross-lens verdict `mixed` (map of disagreement on stance, convergent on measurement).
- `MULTI_PERSPECTIVE_ATTACK@v1` — the catalog is the prior-work needed before running a 5-thread attack on this problem. Threads 1 (ergodic), 2 (information), 11 (physics), 19 (gauge theory), 5 (proof theory) would be the natural five-prior split.
- `LENS_MISMATCH` (Tier 3 candidate) — the knot row is a paradigm case: silent-island diagnosis + this catalog together constitute a Level-1/2 lens-mismatch claim that is actionable (re-encode features per P1.3). If the re-encoding produces coupling, that is a forward-path validation of `LENS_MISMATCH` — the first *prospective* use the symbol needs for Tier 3 promotion.
- `PROBLEM_LENS_CATALOG@v1` — this file is a catalog instance; it extends the existing roster (collatz, lehmer, p-vs-np) into low-dimensional topology for the first time.
- `PATTERN_30@v1` — any tensor signal claimed about knot concordance must be audited for algebraic coupling between its primitives; e.g., determinant vs Alexander-at-(-1) is identical, not correlated.
- Pattern 18 (uniform visibility = axis-class orphan) — the current knot silent-island state is Pattern 18 exemplar; this catalog names the missing axis class (concordance-specific invariants).

**To Prometheus tensor cells.**
- No current F-IDs touch knots; this catalog proposes F_knot_concordance_torsion_detectability as the first knot-substrate F-ID.
- Indirect: any future Mahler-measure-to-L-value finding (Lehmer catalog Lens 7 + this catalog Lens 22) would share a tensor cell.

## Version history

- **v1** 2026-04-21T14:35:00Z — first-pass catalog construction by Harmonia_M2_sessionA after James's prompt. 23 lenses (18 Collatz-palette PROPOSED + 3 NEW + 2 BLEND). No lenses SKIPPED. Predicted cross-lens verdict `mixed`. First concrete hook: 6-feature re-encoding of the 2,977-knot polynomial-data subset per `aporia/mathematics/silent_islands_analysis.md` P1.3. Several specific numerical predictions in individual lens entries are invented as first-pass stances and flagged "plausible but unverified"; refinement requires either community-literature triage or a multi-perspective attack run.
