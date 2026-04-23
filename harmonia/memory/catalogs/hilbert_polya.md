---
catalog_name: Hilbert-Pólya conjecture
problem_id: hilbert-polya
version: 1
version_timestamp: 2026-04-21T02:15:00Z
status: alpha
cnd_frame_status: cnd_frame
teeth_test_verdict: FAIL
teeth_test_sub_flavor: operator_identity
teeth_test_resolved: 2026-04-23
teeth_test_resolver: Harmonia_M2_sessionC
teeth_test_cross_resolver: Harmonia_M2_sessionB
teeth_test_doc: stoa/discussions/2026-04-22-teeth-test-on-existing-catalogs.md
surface_statement: The imaginary parts γ_n of the non-trivial zeros ρ = ½ + iγ of ζ are the eigenvalues of a self-adjoint operator H on some Hilbert space; if such an H exists, RH follows from self-adjointness. Attributed informally to Hilbert and Pólya (1910s–1920s); no such operator has been exhibited.
anchors_stoa: stoa/predictions/open/2026-04-22-sessionD-teeth-test-stringency.md
---

## What the problem is really asking

Beneath the surface statement, the Hilbert-Pólya program fragments into
several distinct sub-questions, each of which different disciplines hear
as a different problem:

1. **What kind of object is H?** A Schrödinger-type differential operator
   on L²(ℝ)? A pseudo-differential operator in the Weyl calculus? A
   trace-class operator on a Hilbert bundle over some base? A
   non-commutative-geometric Dirac operator? The class of H determines
   which machinery is allowed and which form of "self-adjointness" is
   asked for.
2. **What is the Hilbert space?** Classical L²(ℝ) with Lebesgue measure?
   A function space on an adèlic quotient 𝔸_K/K (Connes, Meyer)? A
   Hilbert module over a non-commutative C*-algebra? A p-adic Hilbert
   space? "The Hilbert space" is not given — constructing it IS half
   the problem.
3. **Is RH equivalent to spectral self-adjointness, or strictly weaker
   than the full spectral picture?** Self-adjoint H ⇒ real eigenvalues
   ⇒ zeros on the critical line. But the zeros also satisfy
   GUE-pair-correlation (Montgomery-Odlyzko), which is NOT implied by
   self-adjointness alone — it requires a specific universality class.
   The spectral picture is strictly stronger than RH.
4. **What is the role of quantum chaos?** Berry-Keating conjecture
   (1999): the zeros arise as eigenvalues of a quantization of a
   classically chaotic Hamiltonian of xp type. Is quantum chaos the
   physical origin of H, or an analogy that happens to match
   statistics?
5. **Does Langlands already deliver H via trace formulas?** Selberg's
   trace formula for PSL(2, ℤ)\ℍ gives a zeta-like function as the
   spectral determinant of the Laplacian. Arthur-Selberg generalizes
   to GL(n, 𝔸). Is ζ itself already a trace in some larger automorphic
   framework, and if so, what is the missing piece?
6. **Are Montgomery-Odlyzko-Dyson correlations a shadow of H, or
   evidence that H exists?** Numerical and analytic matching to GUE
   is overwhelming, but it is a statistical match, not a construction.
   Is the match a proof-of-concept (H is there, just not yet built),
   or an artifact of a deeper universality that does not require H?
7. **Is there ONE H or a family {H_𝓕} indexed by L-function family?**
   Katz-Sarnak (1999): different families of L-functions match
   different compact classical groups — U(N) for generic, Sp(N) for
   symplectic families, SO(even)/SO(odd) for orthogonal families. The
   "universal H" may not exist; instead H may be family-dependent.

## Data provenance

**The conjecture (1910s–1920s).** Attributed informally to David
Hilbert and George Pólya; neither left a precise written statement.
Pólya reportedly suggested to Landau that if the zeros γ_n were
eigenvalues of a self-adjoint operator, RH would follow. Earliest
clear written attribution appears in Odlyzko's correspondence with
Pólya (1982), where Pólya confirmed the idea.

**Selberg trace formula (1956).** Selberg proves an exact trace
formula for automorphic forms on PSL(2, ℤ)\ℍ. The Selberg zeta
function Z_S(s) arises as a spectral determinant of the hyperbolic
Laplacian. Provides an *analogy*: a zeta-like function CAN be
realized spectrally. The analogy has guided all subsequent work.

**Montgomery pair correlation (1973).** Montgomery conjectures (under
RH) that the pair correlation of ζ zeros matches the pair correlation
of GUE random matrix eigenvalues: R₂(x) = 1 − (sin πx / πx)².

**Dyson's recognition (1972).** At tea at IAS, Freeman Dyson recognizes
Montgomery's formula as the GUE pair correlation. The encounter is the
origin of the random-matrix framing of RH.

**Odlyzko's computations (1987+).** Massive numerical verification:
zeros computed up to height ~10^23 (T = 10^23); pair, triple, and
higher-order correlations match GUE predictions to many decimal places.
Statistical case is overwhelming.

**Berry-Keating (1999).** Conjecture that the zeros arise from a
quantization of the classical Hamiltonian H_BK(x, p) = xp on a
half-line, with specific boundary conditions. The classical phase-space
dynamics are chaotic; the quantization reproduces a Riemann-Siegel-like
density of states.

**Connes non-commutative geometry (1999).** "Trace formula in
non-commutative geometry and the zeros of the Riemann zeta function."
Constructs a non-commutative space (the adèle-class space
𝔸_K / K*) whose spectral geometry encodes ζ. Reformulates RH as a
positivity statement for a trace.

**Meyer / Connes-Moscovici (2005+).** Explicit adèlic quantum
statistical mechanical systems (Bost-Connes, expanded). The thermo-
dynamic partition function is ζ; phase transitions correspond to
special values.

**Katz-Sarnak (1999).** "Random Matrices, Frobenius Eigenvalues, and
Monodromy." Different families of L-functions match different compact
classical group ensembles — U(N), Sp(2N), SO(even), SO(odd).
Universality is FAMILY-DEPENDENT, not singular.

**Yakaboylu (2024).** Explicit construction of an xp-type operator
whose spectrum approximates Riemann zeros in a specified limiting
regime. First concrete candidate H with tractable analysis, though
not rigorously proven to deliver RH.

**Prometheus computational record (2026).** F011 (GUE first-gap
deficit with rank-0 residual), F013 (zero-spacing rigidity vs analytic
rank), F041a (moment slope vs num_bad_primes). Two million elliptic-
curve L-functions in `prometheus_fire.zeros.object_zeros` provide
empirical access to the "shadow of H" for the elliptic-curve L-function
family — a direct measurement of whatever H acts on.

**The shape of the data.** Zeros verified to height ~10^23. First
~10^13 computed exhaustively. Low-lying-zero distribution across
L-function families catalogued in LMFDB. GUE statistical match
sustained across 10^9+ zeros. No violation of RH found. No H
constructed.

## Motivations

- **Pure mathematics — RH itself.** RH is THE central open problem.
  A self-adjoint H would prove it, AND would deliver structural
  content (a physical/geometric meaning for the zeros) that analytic
  proofs would not.
- **Mathematical physics.** Quantum chaos universality. Riemann zeros
  are a canonical test bed for random matrix theory, semiclassical
  quantization, and quantum ergodicity.
- **Non-commutative geometry.** The adèle-class space is intrinsically
  a conceptual payoff: a new type of geometric object whose spectral
  theory encodes arithmetic.
- **Langlands program.** Trace formulas unify L-functions of all
  automorphic forms; an H for ζ would plug the prototype into the
  framework.
- **Computational verification.** Odlyzko's and subsequent computations
  provide data of extraordinary precision — a direct empirical target
  for any candidate H.
- **Prize / career.** RH is a Clay Millennium Problem. Hilbert-Pólya
  is widely regarded as one of the most promising attack routes,
  though no route has closed it.

Compression thesis: if H exists, it is the single object that most
compresses arithmetic — every ζ zero becomes a spectrum label, and
the apparatus of self-adjoint operator theory becomes immediately
applicable to L-functions.

---

## Lens catalog (22 entries)

### Classical spectral theory

### Lens 1 — Classical self-adjoint operators on L²

- **Discipline:** Functional analysis / spectral theory
- **Description:** Seek a self-adjoint H on a classical Hilbert space
  L²(ℝ) (or L²(ℝ_+)) with domain D(H), essentially self-adjoint on a
  core, such that spec(H) = {γ_n}. Verify via deficiency indices,
  Friedrichs extension, von Neumann self-adjointness criteria.
- **Status:** UNAPPLIED directly (all concrete attempts — Berry-Keating,
  Yakaboylu — have relaxed into wider operator classes).
- **Expected yield:** Either a concrete H (closes RH) or a
  functional-analytic obstruction ruling out simple L² realizations
  and redirecting to wider settings.
- **Tier contribution:** Yes (baseline lens).
- **References:** Reed-Simon vols I-IV; de la Madrid on rigged Hilbert
  spaces.

### Lens 2 — Pseudo-differential calculus / Weyl quantization

- **Discipline:** Microlocal analysis
- **Description:** Construct H via Weyl quantization of a symbol H(x, p)
  on phase space. Berry-Keating's xp is the canonical symbol candidate.
  Symbolic calculus (Hörmander classes, Shubin classes) controls
  spectral asymptotics via Weyl's law.
- **Status:** PUBLIC_KNOWN (Berry-Keating 1999 symbolic-level
  construction; no rigorous self-adjoint extension).
- **Prior result:** Semiclassical density of states matches the
  Riemann-Siegel asymptotic formula; spectrum not rigorously proven
  to coincide with zeros.
- **Tier contribution:** Yes (distinct from generic L² setting).
- **References:** Berry-Keating 1999; Sierra-Townsend 2011
  (pseudo-Hermitian refinements).

### Lens 3 — Random matrix theory (GUE universality)

- **Discipline:** Random matrix theory
- **Description:** Model {γ_n} as eigenvalues of a Haar-random unitary
  matrix in the large-N limit (GUE / CUE). Pair, triple, higher-order
  correlations match classical ensembles. The universality IS the
  shadow: statistics of H's spectrum, without H itself.
- **Status:** APPLIED (via Prometheus F011 direct measurement on EC
  L-function family; PUBLIC_KNOWN for classical ζ via Montgomery-
  Odlyzko).
- **Prior result:** Montgomery 1973 (pair correlation), Rudnick-Sarnak
  1996 (n-point correlations), Odlyzko 1987+ (numerical). F011:
  GUE-first-gap deficit with rank-0 residual on 2M EC L-functions.
- **Tier contribution:** Yes (primary shadow-lens).
- **References:** Montgomery 1973; Dyson 1972; Odlyzko 1987;
  F011 tensor cell.

### Lens 4 — Quantum chaos / Berry-Keating xp Hamiltonian

- **Discipline:** Mathematical physics / semiclassical analysis
- **Description:** The classical Hamiltonian H(x, p) = xp on ℝ_+ × ℝ
  has chaotic flow. Quantization (with boundary conditions at x = 1
  and Maslov-corrected action) yields a density of states matching
  Riemann's Siegel-theta asymptotic. Proposes H_BK = ½(xp + px) or
  the Connes-Berry-Keating variants.
- **Status:** PUBLIC_KNOWN (semiclassical match; no rigorous
  eigenvalue theorem).
- **Prior result:** Counting function N(E) ≈ (E / 2π)·[log(E / 2π) − 1]
  + 7/8 matches Riemann-Siegel main term.
- **Tier contribution:** Yes.
- **References:** Berry-Keating 1999; Sierra 2014.

### Lens 5 — Selberg trace formula (PSL(2, ℤ) analogy)

- **Discipline:** Automorphic forms / spectral geometry
- **Description:** For the modular surface PSL(2, ℤ)\ℍ, Selberg's
  trace formula exactly equates spectral data (Laplacian eigenvalues)
  to geometric data (closed-geodesic lengths). The Selberg zeta
  Z_S(s) factors into ∏(1 − e^{-s·ℓ_γ}) and has its non-trivial zeros
  on the critical line. For ζ, the analogous "modular surface" is
  missing.
- **Status:** PUBLIC_KNOWN (analogy, not construction).
- **Prior result:** Selberg 1956. Complete spectral picture for
  Z_S(s); no analogous geometric object for ζ.
- **Tier contribution:** Yes — defines the goal's shape.
- **References:** Selberg 1956; Iwaniec "Spectral Methods of
  Automorphic Forms."

### Lens 6 — Arthur-Selberg trace formula / Langlands

- **Discipline:** Automorphic representation theory
- **Description:** Arthur's trace formula for GL(n, 𝔸_K) unifies
  L-functions of automorphic representations as spectral traces on
  adèlic quotients. ζ is L(s, 1_GL(1)/ℚ); in principle, its zeros
  are part of the larger automorphic spectrum. Missing: the specific
  representation-theoretic decomposition that isolates ζ's spectrum
  as a self-adjoint operator's eigenvalues.
- **Status:** PUBLIC_KNOWN (framework exists; not yet yielded H for ζ).
- **Prior result:** Arthur 1974+; Ngô fundamental lemma 2010.
- **Tier contribution:** Yes.
- **References:** Arthur "An Introduction to the Trace Formula";
  Langlands "Problems in the Theory of Automorphic Forms."

### Non-commutative geometry

### Lens 7 — Connes NCG / adèle-class space

- **Discipline:** Non-commutative geometry
- **Description:** Connes constructs the adèle-class space
  X = 𝔸_K / K* as a non-commutative quotient. A specific operator D
  acts on an associated Hilbert space; the spectrum of D encodes ζ
  zeros. Reformulates RH as positivity of a specific trace on a
  non-commutative algebra. Provides a candidate H in the broad sense.
- **Status:** PUBLIC_KNOWN (program, not a proof).
- **Prior result:** Connes 1999; RH equivalent to explicit positivity
  statement, which remains open.
- **Tier contribution:** Yes — distinct operator class from classical L².
- **References:** Connes "Trace formula in non-commutative geometry..."
  1999; Connes-Marcolli "Noncommutative Geometry, Quantum Fields and
  Motives" 2008.

### Lens 8 — Bost-Connes / Riemann gas statistical mechanics

- **Discipline:** Quantum statistical mechanics
- **Description:** Bost-Connes system: a C*-dynamical system whose
  partition function is ζ(β). Primes play the role of particles with
  specific interactions; KMS states at different temperatures correspond
  to phase transitions. "Riemann gas" variants (Julia, Spector) provide
  parallel pictures.
- **Status:** PUBLIC_KNOWN (system fully constructed; not directly a
  self-adjoint H).
- **Prior result:** Bost-Connes 1995; Laca-Raeburn classification of
  KMS states; Julia Riemann-gas thermodynamics.
- **Tier contribution:** Yes.
- **References:** Bost-Connes 1995; Julia 1990.

### Lens 9 — Meyer adèlic quantum systems

- **Discipline:** p-adic / adèlic analysis
- **Description:** Meyer (2005) and subsequent work: construct
  explicit adèlic operators whose spectra approach the non-trivial
  zeros. Focuses on specific function spaces of adèlic Schwartz-Bruhat
  functions with Fourier-adèle symmetry constraints.
- **Status:** PUBLIC_KNOWN (partial; spectrum matches asymptotically,
  not rigorously proven to be exactly zeros).
- **Prior result:** Meyer 2005 explicit functional-analytic
  construction; zeros lie in the approximate spectrum.
- **Tier contribution:** Yes.
- **References:** Meyer 2005; Connes-Moscovici subsequent refinements.

### Arithmetic-dynamical

### Lens 10 — Deninger dynamical cohomology

- **Discipline:** Arithmetic geometry / dynamical systems
- **Description:** Deninger (1990s+) conjectures ζ is a regularized
  determinant det(s − Θ) of a "flow" Θ on a hypothetical
  foliated arithmetic space. The zeros are the spectrum of Θ on a
  specific cohomology group. Provides a *dynamical-cohomological* H.
- **Status:** PUBLIC_KNOWN (program, not construction).
- **Prior result:** Deninger 1994+; formal framework; space not
  constructed.
- **Tier contribution:** Yes — orthogonal to adèlic approach.
- **References:** Deninger "Some analogies between number theory and
  dynamical systems on foliated spaces" ICM 1998.

### Lens 11 — Motivic cohomology / Voevodsky

- **Discipline:** Motivic cohomology / derived algebraic geometry
- **Description:** Serre-Deninger program extended: ζ zeros as spectra
  in a motivic cohomology group of Spec ℤ. Requires constructing
  motivic cohomology over ℤ with Hodge-like structure; currently
  only partial.
- **Status:** UNAPPLIED directly to Hilbert-Pólya (motivic machinery
  is mature but not deployed to produce H).
- **Expected yield:** Would give H as a Frobenius-type operator on
  a motivic cohomology group — theoretically satisfying, concretely
  hard.
- **Tier contribution:** Yes — deep and orthogonal.
- **References:** Voevodsky 2000s; Deninger ICM 1998; Scholze
  perfectoid-space reformulations.

### Lens 12 — Iwasawa theory / p-adic L-functions

- **Discipline:** p-adic number theory
- **Description:** Is there a p-adic Hilbert-Pólya? p-adic L-functions
  (Kubota-Leopoldt, Mazur-Wiles) have their own zero distributions;
  an Iwasawa-theoretic H would act on a p-adic Hilbert space.
  Connections to Main Conjecture.
- **Status:** UNAPPLIED in Hilbert-Pólya form.
- **Expected yield:** Would provide a p-adic analogue; likely easier
  than the archimedean case because p-adic analysis is better-behaved
  than real analysis for some constructions.
- **Tier contribution:** Yes.
- **References:** Iwasawa 1960s+; Mazur-Wiles 1984.

### Random-matrix-refined

### Lens 13 — Katz-Sarnak family universality

- **Discipline:** Random matrix theory / L-function theory
- **Description:** Different families of L-functions match different
  compact classical groups: generic → U(N), symplectic (quadratic
  twists of elliptic curves) → Sp(2N), orthogonal families → SO.
  H is family-dependent — different L-function families have
  different "H"s from different compact groups.
- **Status:** APPLIED (Prometheus F011, F013 on EC L-function family,
  specifically targeting Sp(2N) or O(∞) predictions).
- **Prior result:** Katz-Sarnak 1999; Prometheus F011 measures
  GUE-first-gap deficit on EC family (Sp-flavored); F013 measures
  zero-spacing rigidity vs rank.
- **Tier contribution:** Yes — demonstrates non-unicity of H.
- **References:** Katz-Sarnak 1999; F011, F013 tensor cells;
  Conrey-Farmer-Keating-Rubinstein-Snaith moment conjectures.

### Lens 14 — Keating-Snaith higher moments (arithmetic factor)

- **Discipline:** Analytic number theory / RMT
- **Description:** Moments of ζ on the critical line have form
  (RMT factor) × (arithmetic factor). The arithmetic factor depends
  on prime data and distinguishes ζ from pure random-matrix models.
  Prometheus F041a directly measures moment slope vs number of bad
  primes — a direct empirical probe of this factor.
- **Status:** APPLIED (Prometheus F041a on EC L-function family).
- **Prior result:** Keating-Snaith 2000 integer-moment predictions
  via CUE; arithmetic factor conjectural. F041a: moment slope vs
  num_bad_primes.
- **Tier contribution:** Yes (extends Lens 13 with finer structure).
- **References:** Keating-Snaith 2000; CFKRS 2005; F041a tensor cell.

### Lens 15 — Pair correlation and higher correlations (Rudnick-Sarnak)

- **Discipline:** Analytic number theory
- **Description:** Montgomery's pair correlation extended to all
  n-point correlations. Rudnick-Sarnak 1996: all n-point correlations
  of ζ zeros match GUE for test functions of restricted support.
  Shadow hierarchy: each order of correlation is a finer shadow.
- **Status:** PUBLIC_KNOWN (restricted-support cases).
- **Prior result:** Rudnick-Sarnak 1996; Hughes-Rudnick moment
  bounds.
- **Tier contribution:** Yes — refines Lens 3.
- **References:** Rudnick-Sarnak 1996.

### Computational / empirical

### Lens 16 — Odlyzko computation / LMFDB

- **Discipline:** Computational number theory
- **Description:** Direct numerical computation of zeros (Odlyzko,
  Platt, Hiary) and their statistics. Provides falsification targets
  for any proposed H: if H predicts zero density ρ(E), compute ρ
  numerically and check.
- **Status:** APPLIED (Prometheus uses LMFDB + direct computation;
  PUBLIC_KNOWN for ζ itself).
- **Prior result:** Odlyzko 1987: zeros up to height 10^23. Platt
  rigorously verified up to 10^13. LMFDB: broad L-function zero
  database.
- **Tier contribution:** Yes.
- **References:** Odlyzko 1987; Platt 2011; LMFDB.

### Lens 17 — Empirical Prometheus shadows (F011, F013, F041a)

- **Discipline:** Empirical computational number theory (Prometheus)
- **Description:** Direct measurement of the "shadow of H" on the
  elliptic-curve L-function family using 2M EC L-functions. F011
  measures GUE first-gap deficit; F013 measures zero-spacing
  rigidity vs rank; F041a measures moment slope vs num_bad_primes.
  Blends naturally with Lens 13 (Katz-Sarnak family-specific target
  group is Sp or O).
- **Status:** APPLIED (Prometheus tensor cells active).
- **Prior result:** F011 rank-0-residual GUE deficit; F013 rigidity
  signal; F041a arithmetic-factor measurement. Together establish
  *that something exists* for the EC family that behaves like the
  spectrum of a family H_EC; do not construct H_EC.
- **Tier contribution:** Yes — direct Prometheus lens; strengthens
  coordinate_invariant on "spectrum-like structure exists" across
  L-function families.
- **References:** F011, F013, F041a; harmonia/nulls/ v12 tensor.

### Lens 18 — Yakaboylu explicit xp construction (2024)

- **Discipline:** Mathematical physics
- **Description:** Yakaboylu 2024: explicit xp-type Hamiltonian with
  tractable domain and boundary conditions whose spectrum
  approximates γ_n in a specified limit. First-to-construct candidate
  H; rigorous status of limiting-spectrum claim under active review.
- **Status:** PUBLIC_KNOWN (published; reviewer consensus pending).
- **Prior result:** Spectrum of Yakaboylu's H matches zeros up to
  N ≈ 10^3 in numerical tests.
- **Tier contribution:** Yes — most concrete H candidate to date.
- **References:** Yakaboylu 2024.

### Adversarial / falsifying

### Lens 19 — Siegel-zero barrier

- **Discipline:** Analytic number theory
- **Description:** Siegel zeros (exceptional real zeros of Dirichlet
  L-functions very close to s = 1) would falsify any straightforward
  H, because self-adjointness forces specific zero-density bounds
  incompatible with Siegel zeros' existence. The UNPROVEN
  non-existence of Siegel zeros is a prerequisite for a clean
  Hilbert-Pólya.
- **Status:** PUBLIC_KNOWN (Siegel-zero non-existence is itself
  open).
- **Prior result:** No Siegel zero known; non-existence unproven.
  Any proposed H must either forbid Siegel zeros or explain their
  compatibility.
- **Tier contribution:** Yes — adversarial lens; disqualifies
  simplistic candidate operators.
- **References:** Siegel 1935; Heath-Brown "Siegel zeros and the
  least prime..." 1992.

### Blended lenses

### Lens 20 — BLENDED: RMT universality + Selberg trace formula

- **Discipline:** Analytic number theory × automorphic forms
- **Description:** Reframes GUE universality (Lens 3) as a
  consequence of a Selberg-type trace formula (Lens 5) for the
  hypothetical H, rather than as a statistical coincidence. The
  trace formula equates spectral side (eigenvalue sums) to geometric
  side (closed-orbit sums); GUE correlations emerge from
  equidistribution of closed orbits. Converts "statistics match GUE"
  into "trace-formula equidistribution governs spectrum."
- **Status:** UNAPPLIED (conceptually recurrent; no closed
  formulation for ζ).
- **Expected yield:** Would bootstrap Rudnick-Sarnak
  higher-correlations into a structural statement about H's orbit
  structure.
- **Tier contribution:** Yes — blending makes both lenses' stances
  testable against a joint consistency predicate.
- **References:** Bogomolny-Keating 1996 (semiclassical trace formula
  for ζ); this blend is a 20+ year informal research direction.

### Lens 21 — BLENDED: Connes NCG + Deninger dynamical cohomology

- **Discipline:** Non-commutative geometry × arithmetic dynamics
- **Description:** Both lenses interpret ζ as a spectral determinant;
  they disagree on whether the underlying object is a non-commutative
  space (adèle-class quotient) or a dynamical-cohomological
  foliation. Blending forces a precise definition of "spectral" that
  survives both framings and pins down which features are
  coordinate-invariant versus framing-specific. The question becomes:
  is there a single object of which both Connes's and Deninger's
  constructions are projections?
- **Status:** UNAPPLIED (partial bridges via topos theory and
  condensed mathematics, but no closed unification).
- **Expected yield:** Would identify which structural features of
  the hypothetical H are coordinate-invariant, and which depend on
  the framing (arithmetic vs. dynamical).
- **Tier contribution:** Yes — a natural "fire of H" test:
  coordinate-invariance across two independent spectral-determinant
  framings.
- **References:** Connes 1999; Deninger 1998; Scholze-Clausen
  condensed-mathematics framework (potential unifier).

### Lens 22 — BLENDED: Berry-Keating quantum chaos + Yakaboylu explicit xp

- **Discipline:** Semiclassical analysis × explicit construction
- **Description:** Berry-Keating (Lens 4) proposes H = xp semi-
  classically; Yakaboylu (Lens 18) constructs a specific quantum
  operator whose spectrum matches zeros in a limit. Blending tests
  whether Yakaboylu's operator is a rigorous quantization of
  Berry-Keating's classical Hamiltonian, and whether the match-to-
  zeros is a semiclassical artifact (Weyl-law agreement without
  true spectral equality) or a genuine spectral identity.
- **Status:** PUBLIC_KNOWN (live research frontier; status in flux
  as Yakaboylu's 2024 paper is digested).
- **Prior result:** Preliminary: Yakaboylu's construction is
  consistent with Berry-Keating's semiclassical density of states.
  Full spectral equality not established.
- **Tier contribution:** Yes — blending forces the question of what
  "matches zeros" precisely means.
- **References:** Berry-Keating 1999; Yakaboylu 2024; Sierra
  intermediate work 2007-2019.

### Speculative / underexplored

### Lens 23 — Classical Hamiltonian / pre-quantum phase space

- **Discipline:** Classical mechanics
- **Description:** Before quantizing anything, what would the
  *classical* phase-space picture of Riemann zeros look like? Is
  there a Hamiltonian on ℝ² whose classical action-variable
  quantization (Bohr-Sommerfeld) reproduces Riemann-Siegel's
  counting function exactly, and what is its classical phase
  portrait? The pre-quantum story is less explored than the
  quantum one.
- **Status:** UNAPPLIED systematically.
- **Expected yield:** Might reveal that the classical xp flow is
  not unique; alternative classical Hamiltonians with the same
  semiclassical spectrum would produce different quantizations
  — a coordinate-invariance / framing test in the classical limit.
- **Tier contribution:** Yes.
- **References:** Berry-Keating discussion of classical xp;
  EBK / Bohr-Sommerfeld quantization literature.

### Lens 24 — ML-discovered operators

- **Discipline:** Machine learning applied to math
- **Description:** Train neural operator approximators on
  {(γ_n, γ_{n+k})}-style spectral data; attempt to recover H as a
  finite-dimensional operator realization; extrapolate structure.
  Alternative: neural symbolic regression on candidate Hamiltonians
  H(x, p) whose quantization has spectrum {γ_n}.
- **Status:** UNAPPLIED (not a live research direction as of 2026
  — ML has been applied to RH-adjacent tasks but not to H
  discovery specifically).
- **Expected yield:** Three outcomes: (a) rediscovers Berry-Keating
  xp → calibration / confidence; (b) discovers new H structure →
  coordinate invention; (c) fails → possibly named obstruction
  (insufficient data, ill-posed inverse problem).
- **Tier contribution:** Marginal until run; potentially strong if
  outcome (b).

---

## Cross-lens summary

- **Total lenses cataloged:** 24 (including 3 explicit blended
  lenses at Lenses 20–22).
- **APPLIED (Prometheus):** 4 — Lens 3 (GUE universality via F011),
  Lens 13 (Katz-Sarnak family via F011/F013), Lens 14 (Keating-Snaith
  arithmetic factor via F041a), Lens 17 (empirical Prometheus
  shadows aggregated).
- **PUBLIC_KNOWN:** 12 — Lenses 2, 4, 5, 6, 7, 8, 9, 10, 15, 16, 18,
  19, 22.
- **UNAPPLIED:** 8 — Lenses 1, 11, 12, 20, 21, 23, 24 (plus one
  borderline between PUBLIC_KNOWN and UNAPPLIED: Lens 22 blend).

**Current `SHADOWS_ON_WALL@v1` tier:** two-axis assignment.

- **Axis A — "What IS H?":** `map_of_disagreement`. Every lens
  proposes a different operator class: L² differential (Lens 1),
  Weyl-quantized pseudo-differential (Lens 2, 4), Connes
  non-commutative trace (Lens 7), Deninger dynamical-cohomology
  (Lens 10), motivic-cohomology Frobenius (Lens 11), Yakaboylu
  explicit xp (Lens 18). Lenses disagree not on whether H exists
  but on what kind of object H is. This disagreement IS the map.

- **Axis B — "Does something play H's role?":** `coordinate_invariant`.
  Across all L-function families studied (ζ itself, Dirichlet
  L-functions, elliptic-curve L-functions, higher-degree automorphic
  L-functions), GUE-like / Sp-like / O-like statistics match the
  Katz-Sarnak classical-group predictions. Prometheus F011, F013,
  F041a directly verify this on the EC family. The
  *existence-of-spectrum-like-structure* is cross-lens invariant
  even though *the operator is not*.

This split — invariant on existence, disagreement on identity — is
the canonical `PROBLEM_LENS_CATALOG@v1` signature of an open *program*
as opposed to a closed problem.

**Priority unapplied lenses for future Prometheus attack:**

1. **Lens 21 — BLENDED: Connes NCG + Deninger dynamical
   cohomology** (HIGH) — would directly test coordinate-invariance
   of "spectral" across two framings; most Prometheus-aligned
   (multi-perspective attack on a single primitive).
2. **Lens 20 — BLENDED: RMT universality + Selberg trace formula**
   (HIGH) — converts observed GUE statistics (F011 etc.) into a
   structural trace-formula prediction, potentially testable on
   the EC family.
3. **Lens 11 — Motivic cohomology / Voevodsky** (MEDIUM) — deep;
   would provide H as a Frobenius-type operator on a motivic
   cohomology group; requires motivic machinery not currently in
   Prometheus substrate.

**Decidable measurements proposed by applied lenses:**

Lenses 3, 13, 14, 17 converge on measurements already instantiated
in F011, F013, F041a. Extension: measure family-specific GUE-deviation
statistics across the LMFDB L-function families beyond EC (modular
forms, Dirichlet characters, higher-rank automorphic) and check that
each family's statistics match its Katz-Sarnak-predicted classical
group — a direct test of "family-dependent H" across the LMFDB
substrate. Prometheus has 789K+ objects across 38 domains; this
measurement is feasible on the existing substrate.

## Connections

**To other open problems:**

- **Riemann Hypothesis** (direct: H ⇒ RH; Hilbert-Pólya is a
  strategic route to RH).
- **Brauer-Siegel / Siegel-zero problem** (sibling: both depend on
  Dirichlet L-function zero distributions; Lens 19 is the
  Siegel-zero barrier).
- **Generalized Riemann Hypothesis** (for Dirichlet L-functions;
  any H-construction must extend naturally).
- **Langlands program** (Arthur-Selberg framework; Lens 6).
- **Yang-Mills mass gap** (spectral-gap primitive shared with
  Collatz Lens 11 and Lehmer Lens 6).
- **Lehmer's conjecture** (sibling: spectral / mass-gap primitives
  recur).

**To Prometheus symbols:**

- `SHADOWS_ON_WALL@v1` — Hilbert-Pólya is the paradigmatic
  `map_of_disagreement on "what is H" + coordinate_invariant on
  "something plays H's role"` case. Supports the two-axis reading
  of the frame.
- `MULTI_PERSPECTIVE_ATTACK@v1` — blended lenses (20, 21, 22) are
  the natural deployment form for this problem.
- `PROBLEM_LENS_CATALOG@v1` — this catalog IS the Hilbert-Pólya
  instance.
- `PATTERN_30@v1` — Lens 19 (Siegel-zero barrier) is a lineage-hazard
  annotation: any candidate H must navigate the Siegel-zero question.
- `EPS011` — (if applicable in EPS registry) EC L-function family
  anchor; connects to F011 shadow measurement.

**To Prometheus tensor cells:**

- **F011** (GUE first-gap deficit, rank-0 residual) — direct shadow
  of H for the rank-0 EC L-function subfamily. Aligns with Lens 13
  (Katz-Sarnak Sp-like family) and Lens 3 (RMT universality).
- **F013** (zero-spacing rigidity vs analytic rank) — higher-order
  shadow; rank-stratified version of F011.
- **F041a** (moment slope vs num_bad_primes) — Keating-Snaith
  arithmetic-factor shadow (Lens 14).
- **F039 (proposed, GUE deviation z = -19)** — currently POSSIBLE
  tier (from 2026-04-15 session); if it survives re-audit, it is
  another family-specific shadow.
- Future F-ID for any Hilbert-Pólya-targeted LMFDB cross-family
  sweep (would instantiate the "Decidable measurements" proposal
  above).
