---
catalog_name: Lehmer's conjecture
problem_id: lehmer
version: 1
version_timestamp: 2026-04-21T00:50:00Z
status: alpha
surface_statement: Every monic integer polynomial that is not a product of cyclotomic polynomials has Mahler measure M(f) ≥ 1.17628... (Lehmer's constant, the Mahler measure of x^10 + x^9 - x^7 - x^6 - x^5 - x^4 - x^3 + x + 1).
---

## What the problem is really asking

Beneath the surface statement, five distinct sub-questions:

1. **Is there a minimum non-trivial complexity for algebraic integers?**
   Cyclotomic roots live at "complexity zero" (Mahler measure 1). Is the
   next stratum discretely separated, or continuously approachable?
2. **Is integrality a sufficient quantization to generate a spectral gap
   in a functional-analytic action?** The integer-coefficient constraint
   is one discrete condition on Hardy-space symbols; does one condition
   suffice for a gap?
3. **What is the minimum topological entropy of a Z-action on a compact
   abelian group?** Lind-Schmidt-Ward: Mahler measure IS the topological
   entropy of an associated solenoidal dynamics. Lehmer's conjecture
   becomes a minimum-entropy theorem.
4. **Where do analytic-number-theoretic height methods break down?**
   Dobrowolski's bound decays to 1 as degree grows; Smyth's bound only
   covers non-reciprocals. The region between is unmapped.
5. **Is height a coordinate-invariant quantity across Weil / Mahler /
   Deligne / Arakelov normalizations, and does that invariance imply
   gap-invariance?** Multiple heights exist; they agree on algebraic
   integers up to scaling. A gap on one implies a gap on all if they're
   genuinely projections of the same object.

## Data provenance

**The polynomial (1933).** D.H. Lehmer, "Factorization of certain
cyclotomic functions," Ann. Math. 34 (1933). Lehmer was computing
Pierce numbers c_n(f) = ∏(α_i^n - 1) for use in divisor-chain algorithms.
He needed polynomials with slow-growing Pierce sequences — equivalently,
small Mahler measure. Hand-enumerated low-coefficient reciprocal
polynomials up to degree 10; identified the degree-10 decic with
M ≈ 1.17628. He DID NOT formally conjecture the lower bound — he noted
that he had been unable to find anything smaller. The "conjecture" is
a historical artifact of 93 years of community failure to beat his
example.

**The constant 1.17628...** is the largest root of Lehmer's polynomial.
It is the smallest known Salem number (real algebraic integer > 1 all
of whose other Galois conjugates lie on the unit circle). Computed now
to many digits.

**The search record (1933–2026).**
- Smyth 1971: lower bound 1.3247... for non-reciprocal irreducibles
  (Smyth's constant = smallest Pisot number)
- Dobrowolski 1979: M ≥ 1 + c·(log log n / log n)^3 for general degree-n
  polynomials — universal but decays to 1
- Boyd 1980s: extensive tables, Salem-number connections
- Mossinghoff 1998+: exhaustive enumeration of reciprocals up to degree
  44, sparse up to ~180
- Deninger 1997: Mahler measures of 2-var polynomials conjecturally
  equal L-values (connecting pure number theory to Langlands)
- Multiple teams 2000s+: LLL-based and ML-generated searches, no
  counterexample

**No counterexample found in 93 years. Exhaustiveness not established
above degree 44.**

## Motivations

Why humans try to solve it:

- **Pure mathematical aesthetics.** Clean statement, deep structural
  content, 90+ years open.
- **Cross-domain bridges (Prometheus-aligned).** Deninger-Boyd connect
  Mahler measures of 2-var polys to L(E, 2) for elliptic curves. The
  Lehmer problem sits at one end of a bridge to Langlands, modular
  forms, and arithmetic geometry.
- **Dynamical motivation.** Lehmer's constant is conjecturally the
  minimum topological entropy of Z-actions on compact abelian groups —
  a universal constant of dynamics if true.
- **Physics.** Transfer operators of specific spin-chain models have
  Lehmer-class polynomials as their characteristic polynomials; the
  gap is the mass gap of these models.
- **Topology.** Mahler measures bound growth of Alexander polynomials
  and relate to knot-volume conjectures.
- **Analytic number theory as a test problem.** Effective bounds on
  heights of algebraic numbers are a test case for broader height-
  theoretic machinery (Bogomolov, Zhang).
- **Career / prize / pedagogical.** 93-year open, easy to state,
  connects many fields — excellent PhD and teaching problem.

Compression thesis: IF the gap exists with value 1.17628, that IS a
hidden structural boundary in algebraic-number space, and the
structure almost certainly connects to L-values, Langlands, dynamics,
topology. The compression payoff is a single number that summarizes
an infinite family.

---

## Lens catalog (28 entries)

### Classical algebraic number theory

### Lens 1 — Height-function geometry

- **Discipline:** Algebraic number theory
- **Description:** Treat Mahler measure as a height on algebraic
  integers; use Minkowski-geometric lattice arguments to bound the
  lowest height. Dobrowolski's bound lives here.
- **Status:** PUBLIC_KNOWN
- **Prior result:** Dobrowolski 1979: M ≥ 1 + c·(log log n / log n)^3.
  Converges to 1 as n → ∞, so insufficient for the conjecture but
  a real partial result.
- **Tier contribution:** Yes (distinct discipline).
- **References:** Dobrowolski 1979; Voutier 1996 refinement.

### Lens 2 — Conjugate-geometry analysis

- **Discipline:** Algebraic number theory
- **Description:** Distribution of Galois conjugates on / off / near
  the unit circle. Smyth's non-reciprocal theorem exploits asymmetry.
- **Status:** PUBLIC_KNOWN
- **Prior result:** Smyth 1971: for non-reciprocal irreducible
  polynomials, M ≥ 1.3247 (Smyth's constant = smallest Pisot).
- **Tier contribution:** Yes (distinct from height geometry — uses
  conjugate-distribution rather than lattice-geometric arguments).
- **References:** Smyth 1971.

### Lens 3 — Linear forms in logarithms

- **Discipline:** Transcendence theory
- **Description:** Baker's method for effective lower bounds on
  Diophantine quantities. Could give effective non-uniform bounds.
- **Status:** UNAPPLIED to Lehmer directly (applied to adjacent
  Diophantine problems).
- **Expected yield:** Effective sub-exponential bounds on M(f) in
  terms of degree and discriminant, though unlikely to reach 1.17628.
- **Tier contribution:** Yes if applied.
- **References:** Baker 1966+; Feldman-Nesterenko.

### Lens 4 — p-adic methods / Newton polygons

- **Discipline:** p-adic number theory
- **Description:** Newton-polygon analysis at each prime; adelic
  height decomposition. Lehmer polynomial's Newton polygons at small
  primes have specific structure that might be extremal.
- **Status:** UNAPPLIED
- **Expected yield:** Could reveal that extremal Mahler-measure
  polynomials have constrained p-adic valuations, narrowing the
  counterexample search space.
- **Tier contribution:** Yes.

### Lens 5 — Cyclotomic theory (Kronecker)

- **Discipline:** Algebraic number theory
- **Description:** Classification of M=1 polynomials (Kronecker's
  theorem: M(f)=1 iff f is ±(product of cyclotomics and x^k)). This
  IS the definitional lens for what counts as trivial.
- **Status:** PUBLIC_KNOWN (theorem, not a gap argument)
- **Tier contribution:** Definitional, does not contribute to tier.
- **References:** Kronecker 1857.

### Analytic / functional-analytic

### Lens 6 — Szegő / Toeplitz determinant asymptotics

- **Discipline:** Functional analysis / operator theory
- **Description:** Mahler measure as the leading Szegő coefficient;
  Lehmer's conjecture as a mass-gap question on the action
  S[f] = log det_ζ T(f). Our mass-gap thread.
- **Status:** APPLIED (Prometheus thread 5 + 4 external model runs
  2026-04-20)
- **Prior result:** 5 samples returned 3A / 1B / 1C. All A-stances
  recruited BCS analogy; B recruited 2D XY; C recruited Wigner-Dyson
  / Koopman.
- **Tier contribution:** Yes (distinct discipline).
- **References:** methodology_multi_perspective_attack@cde766053.

### Lens 7 — L-function / special-value connections (Deninger-Boyd)

- **Discipline:** Arithmetic geometry / L-function theory
- **Description:** Mahler measures of 2-variable polynomials
  conjecturally equal (up to rationals) special values of L-functions
  of elliptic curves. Bridge from pure Mahler-measure theory to
  Langlands / modularity.
- **Status:** PUBLIC_KNOWN (partially proven for specific cases;
  general form conjectural)
- **Prior result:** m(1 + x + y + 1/x + 1/y) = (15/(4π²))·L(E, 2)
  for E of conductor 15 (Deninger 1997, Boyd 1998).
- **Tier contribution:** Yes — orthogonal to all height / analytic
  lenses.
- **References:** Deninger 1997; Boyd 1998; Rodriguez-Villegas 1999.
- **Prometheus priority:** HIGH — this is the Langlands-bridge lens;
  could be the move that unifies Lehmer with F003 / F005 BSD-adjacent
  cells in our tensor.

### Lens 8 — Random matrix / trace-formula

- **Discipline:** Random matrix theory
- **Description:** Distribution of roots of random integer polynomials
  and comparison to Lehmer extremality.
- **Status:** UNAPPLIED to Lehmer (extensively developed elsewhere —
  GUE, CUE, etc.)
- **Expected yield:** Would reveal whether Lehmer's polynomial's
  root configuration is an extreme value in a universal distribution
  or a specific outlier.
- **Tier contribution:** Yes.

### Dynamical / ergodic

### Lens 9 — Topological entropy of Z-actions (Lind-Schmidt-Ward)

- **Discipline:** Ergodic theory / dynamical systems
- **Description:** Every monic integer polynomial corresponds to a
  Z-action on a compact abelian group (solenoid); Mahler measure is
  the topological entropy. Lehmer's conjecture = minimum-entropy
  theorem.
- **Status:** APPLIED (Prometheus thread 1, 2026-04-20)
- **Prior result:** Stance C: M*(d) → 1 as d → ∞; Lehmer's gap is a
  finite-dimensional lattice-packing artifact; asymptotic infimum
  is 1 with approach rate log(M*(d) - 1) ≈ -log d.
- **Tier contribution:** Yes.
- **References:** Lind-Schmidt-Ward 1990; Prometheus thread log.

### Lens 10 — Koopman operator spectra

- **Discipline:** Operator theory / dynamical systems
- **Description:** Spectral radius of the Koopman operator of the
  associated shift. Complementary to entropy framing.
- **Status:** UNAPPLIED directly (touched via Lens 9).
- **Expected yield:** Could refine thread-1's prediction on the
  approach rate to 1 — different spectral-gap structure than entropy.
- **Tier contribution:** Marginal (same discipline class as Lens 9).

### Lens 11 — β-shift / symbolic dynamics

- **Discipline:** Symbolic dynamics
- **Description:** Encoding the polynomial as a β-expansion shift
  system; analyze shift-structural properties.
- **Status:** PUBLIC_KNOWN (Parry's theory)
- **Tier contribution:** Yes (distinct from general entropy framing).
- **References:** Parry 1960; more recent work by Frougny-Solomyak.

### Combinatorial / geometric

### Lens 12 — Newton-polygon / exponent-set combinatorics

- **Discipline:** Combinatorics
- **Description:** Combinatorial structure of coefficient support;
  sparse polynomials have few non-zero positions, constraining the
  geometry of roots.
- **Status:** APPLIED (Prometheus thread 4, 2026-04-20, adversarial)
- **Prior result:** Stance A: counterexample candidate in pentanomials
  of degree 180-260 with gap-biased Newton polygons under coefficient
  alphabet {-2,-1,1,2}. Under-explored search space.
- **Tier contribution:** Yes.

### Lens 13 — Polynomial coefficient geometry (lattice-point counting)

- **Discipline:** Geometry of numbers
- **Description:** Schlickewei-Wirsing bounds on heights of polynomials
  with coefficients in bounded regions.
- **Status:** UNAPPLIED to Lehmer specifically.
- **Expected yield:** Effective counting of candidate polynomials at
  a given height up to degree D.
- **Tier contribution:** Yes.

### Lens 14 — Sparse polynomial structure (Salem/Pisot classification)

- **Discipline:** Algebraic number theory / combinatorics
- **Description:** Salem, Pisot, and Lehmer families as discrete
  subvarieties of polynomial space with known extremal properties.
- **Status:** PUBLIC_KNOWN (Salem 1945, Pisot 1938)
- **Tier contribution:** Already covered by Lens 2, 12.

### Information-theoretic / complexity

### Lens 15 — Kolmogorov / description length

- **Discipline:** Algorithmic information theory
- **Description:** Small-Mahler-measure polynomials are algorithmically
  simpler (lower Kolmogorov complexity) than generic ones. Lehmer's
  constant is an information-theoretic phase-transition threshold.
- **Status:** APPLIED (Prometheus thread 2, 2026-04-20)
- **Prior result:** Stance C: true floor below 1.17628 via coding-
  stratum entropy; M_d* → ~1.16 via log-decay.
- **Tier contribution:** Yes.

### Lens 16 — Channel capacity / MDL

- **Discipline:** Information theory
- **Description:** Mutual information between polynomial encoding
  and Mahler-measure value; rate-distortion at the M=1 boundary.
- **Status:** UNAPPLIED directly.
- **Expected yield:** Could quantify how much information the
  coefficient vector carries about Mahler measure; distinguishes
  low-entropy polynomial families from generic.
- **Tier contribution:** Marginal (same discipline class as Lens 15).

### Lens 17 — Algorithmic randomness of coefficient sequences

- **Discipline:** Algorithmic randomness
- **Description:** Martin-Löf randomness tests on coefficient
  sequences; connection between incompressibility and Mahler-measure
  tails.
- **Status:** UNAPPLIED.
- **Expected yield:** Speculative — would test whether Lehmer-like
  polynomials are precisely the "non-random" integer polynomials.

### Cross-domain / speculative

### Lens 18 — Hodge theory / motivic cohomology (Deligne-Beilinson)

- **Discipline:** Arithmetic geometry / motivic cohomology
- **Description:** Mahler measures conjecturally encode regulators;
  Beilinson's conjectures give a motivic-cohomological interpretation.
  Lehmer's gap would be a rigidity statement about motivic invariants.
- **Status:** PUBLIC_KNOWN (conjectural framework)
- **Tier contribution:** Yes — deep and orthogonal to all other lenses.
- **Prometheus priority:** HIGH — if realized, provides a theorem-
  strength argument for the gap via motivic rigidity.

### Lens 19 — Knot-theoretic volumes / Alexander polynomial growth

- **Discipline:** Low-dimensional topology
- **Description:** Mahler measure of Alexander polynomial of a
  fibered knot bounds hyperbolic volume (under volume conjecture).
- **Status:** PUBLIC_KNOWN (Silver-Williams).
- **Tier contribution:** Yes — topology is orthogonal to number-
  theoretic lenses.

### Lens 20 — Bogomolov conjecture / Zhang-Ullmo

- **Discipline:** Arithmetic geometry
- **Description:** Lehmer is a 1-dimensional case of Bogomolov
  (bounds on heights of points on abelian varieties). Machinery
  generalizes.
- **Status:** PUBLIC_KNOWN (Bogomolov proved by Ullmo 1998 / Zhang 1998)
- **Tier contribution:** Yes.

### Lens 21 — Dynamical Manin-Mumford

- **Discipline:** Arithmetic dynamics
- **Description:** Rigidity of preperiodic points under algebraic
  dynamics; parallel problem with shared machinery.
- **Status:** PUBLIC_KNOWN (conjectural framework; partial results).
- **Tier contribution:** Yes.

### Lens 22 — Diophantine approximation (Roth-type)

- **Discipline:** Analytic number theory
- **Description:** Effective Roth bounds on approximations of algebraic
  numbers; translate to height bounds.
- **Status:** UNAPPLIED to Lehmer directly.
- **Expected yield:** Effective lower bounds similar in spirit to
  Dobrowolski but from a different machinery.

### Computational / empirical

### Lens 23 — Exhaustive enumeration (Mossinghoff, Boyd)

- **Discipline:** Computational number theory
- **Description:** Direct enumeration of low-measure polynomials.
- **Status:** PUBLIC_KNOWN
- **Prior result:** Exhaustive to degree 44 for reciprocal
  polynomials; sparse to degree 180. No counterexample.
- **Tier contribution:** Counts as one empirical lens.

### Lens 24 — LLL-based search (Salem heuristics)

- **Discipline:** Computational number theory
- **Description:** Lattice reduction to find small-measure candidates.
- **Status:** PUBLIC_KNOWN
- **Tier contribution:** Marginal (same class as Lens 23).

### Lens 25 — ML-generated candidates

- **Discipline:** Machine learning applied to math
- **Description:** Train generative models on small-measure polynomials,
  sample for candidates below the bound.
- **Status:** PUBLIC_KNOWN (post-2020 work; no counterexample found,
  but regression-toward-training-data bias noted by Prometheus thread 4).
- **Tier contribution:** Marginal (search bias constraints).

### Lens 26 — Formal verification (Coq / Lean)

- **Discipline:** Formal methods
- **Description:** Machine-verified proofs of Dobrowolski-type bounds;
  formal exhaustive enumeration certificates.
- **Status:** UNAPPLIED to Lehmer bounds.
- **Expected yield:** Would not prove the conjecture but would
  establish rigorously verified bounds sharper than current.

### Meta-theoretical

### Lens 27 — Proof-complexity / reverse mathematics

- **Discipline:** Proof theory
- **Description:** What axiomatic strength is needed to prove Lehmer?
  Is it provable in PA, RCA₀, or does it need transfinite induction?
- **Status:** UNAPPLIED.
- **Expected yield:** Might reveal that Lehmer is Goodstein-class
  (true-but-requires-strong-induction) or is independent of standard
  systems.
- **Tier contribution:** Yes — orthogonal to all object-level lenses.
- **Prometheus priority:** Worth probing once the Collatz
  computability thread's analogue analysis is systematized.

### Lens 28 — Dependency-graph / cross-conjecture analysis

- **Discipline:** Meta-mathematical
- **Description:** What does Lehmer imply? What implies it? Bogomolov
  (stronger) → Lehmer (weaker). Zilber-Pink (stronger) → Bogomolov.
  Position in the implication graph matters.
- **Status:** PUBLIC_KNOWN (mostly)
- **Tier contribution:** Meta-level; doesn't directly contribute to
  lens count but informs priority.

---

## Cross-lens summary

- **Total lenses cataloged:** 28
- **APPLIED (via Prometheus):** 5 (Lenses 6, 9, 12, 15 from thread
  attacks; partial on others via cross-model samples)
- **PUBLIC_KNOWN:** 10 (Lenses 1, 2, 5, 7, 11, 14, 18, 19, 20, 21, 23,
  24, 25 — some overlap)
- **UNAPPLIED (Prometheus-addressable):** ≥ 13 distinct discipline
  classes

**Current `SHADOWS_ON_WALL@v1` tier:** `map_of_disagreement`.
Rationale: the 5 applied lenses (via Prometheus multi-perspective
attack) returned 3 distinct stances (A / B / C) with sharp directional
disagreement on the asymptote. Public-known lenses add partial bounds
(Dobrowolski, Smyth, Mossinghoff enumeration) but do not converge on
a value — they sandwich the answer in a wide region.

**Priority unapplied lenses (Prometheus work):**

1. **Lens 7 — Deninger-Boyd L-value bridge** (HIGH) — connects Lehmer
   to Langlands; could unify with F003 / F005 in the tensor.
2. **Lens 18 — Motivic cohomology / Beilinson** (HIGH) — orthogonal,
   theorem-strength potential.
3. **Lens 27 — Proof-complexity analysis** (MEDIUM) — leverages
   Collatz-thread-5 framework.
4. **Lens 4 — p-adic / Newton polygons** (MEDIUM) — could narrow the
   counterexample search.
5. **Lens 8 — Random matrix universality** (MEDIUM) — quantifies
   Lehmer's extremality.

**Decidable measurements proposed by applied lenses:**

All five applied lenses converged on one measurement class:
enumerate min M(f) per degree d ∈ [10, 60] over non-cyclotomic monic
integer polynomials; fit m(d) = f_∞ + C·d^{-α}; the (f_∞, α) pair
distinguishes all five stances. See Agora task candidate
`audit_lehmer_min_mahler_per_degree_d10_60`.

## Connections

**To other open problems:**
- Bogomolov conjecture (stronger)
- Zilber-Pink (strictly stronger)
- Dynamical Manin-Mumford (parallel rigidity question)
- Volume conjecture in knot theory (via Alexander polynomials)

**To Prometheus symbols:**
- `SHADOWS_ON_WALL@v1` — this catalog IS the operational implementation
  for Lehmer
- `MULTI_PERSPECTIVE_ATTACK@v1` — 5 threads applied, data in
  methodology doc
- `PATTERN_30@v1` — F043 retraction is a Lehmer-adjacent lesson about
  single-lens failure

**To Prometheus tensor cells:**
- F014 (Lehmer spectrum — already a live specimen). Updating F014
  with lens-count tier per this catalog is a natural follow-on.
- F003, F005 (calibration anchors for BSD) — connect via Lens 7
  (Deninger-Boyd L-value bridge).
