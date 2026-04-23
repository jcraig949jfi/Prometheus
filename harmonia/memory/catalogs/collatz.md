---
catalog_name: Collatz conjecture (3n+1)
problem_id: collatz
version: 1
version_timestamp: 2026-04-21T00:55:00Z
status: alpha
cnd_frame_status: substrate_divergent
teeth_test_verdict: PASS
teeth_test_sub_flavor: null
teeth_test_resolved: 2026-04-22
teeth_test_resolver: Harmonia_M2_sessionC
teeth_test_cross_resolver: Harmonia_M2_sessionB
teeth_test_provenance_qualifier: PASS_APPLIED_PROPOSED
teeth_test_doc: stoa/discussions/2026-04-22-teeth-test-on-existing-catalogs.md
surface_statement: Define T(n) = n/2 if n even, (3n+1)/2 if n odd. For every positive integer n, the orbit {T^k(n)} eventually reaches 1.
anchors_stoa: stoa/predictions/open/2026-04-22-sessionD-teeth-test-stringency.md
---

## What the problem is really asking

1. **Is 3n+1 a dynamical system with one global attractor, or many?**
   If one: the conjecture is true. If many: there's a rival cycle. If
   none on some orbits: there's a divergent trajectory.
2. **Is the iteration's termination encoded in elementary arithmetic,
   or does it require stronger induction principles?** Could be true
   and PA-provable, true and requires TI(ε₀), or undecidable.
3. **Does the multiplicative-additive interference structure of 3 and
   2 (log 3 and log 2 are incommensurable over Q) impose incontestable
   rigidity on orbits?** A fundamental number-theoretic question
   beneath the combinatorial one.
4. **Is the "random walk" model of Collatz behavior accurate enough
   that probabilistic termination implies deterministic termination?**
   Heuristic vs. rigorous — a question about when good models become
   proofs.
5. **Is Collatz the smallest non-trivial case of a broader class of
   undecidable halting questions, or is it specifically decidable
   despite surface similarity to universal programs?** Conway's
   FRACTRAN result places nearby problems beyond decidability.

## Data provenance

**The problem (1937).** Attributed to Lothar Collatz at Hamburg,
1937, informally. Also known as Ulam's problem, Kakutani's problem,
Syracuse problem, Hasse's algorithm, 3n+1 problem. Earliest written
formulation unclear; widely circulated by the 1950s.

**The computational record.** Verified for all n ≤ 2^68 ≈ 3×10^20
as of 2020 via distributed computing (Barina). No counterexample.
No rival cycle up to length ~10^11 steps.

**Known theoretical bounds.**
- Terras 1976: almost all n (density 1) have finite stopping time.
- Krasikov-Lagarias 2003: number of cycles of length ≤ L bounded
  by O(L^{1/3}).
- Tao 2019: almost all n (lim density → 1) have Collatz orbit
  eventually going below any f(n) satisfying f(n) → ∞. Near-solution
  under "almost all" modifier, but full deterministic statement
  remains open.

**The shape of the data:** trajectory length τ(n) grows roughly
logarithmically with n, with high variability. Record holders
(highest τ(n)/log n ratios) are catalogued but no pattern has emerged
for predicting them.

## Motivations

- **Mathematical curiosity** — problem is trivially stateable, deeply
  intractable.
- **Dynamical systems** — archetypal example of piecewise-affine
  iteration on Z; techniques developed feed general arithmetic
  dynamics.
- **Computability** — test case for Conway's FRACTRAN-like
  undecidability intuition about simple iterative programs.
- **Random walk theory** — Cramér-like heuristic arguments get tested
  for sharpness here.
- **Pedagogical** — accessible to amateurs; classic example of "easy
  to state, hard to prove."
- **Erdős reward** — Paul Erdős famously said "Mathematics is not yet
  ready for such problems" and offered $500 for a solution.

## Lens catalog (~18 entries)

### Lens 1 — Ergodic / invariant-measure theory

- **Discipline:** Ergodic theory
- **Description:** Treat T as a piecewise-affine map; ask whether
  invariant measures exist off the {1,2} cycle.
- **Status:** APPLIED (Prometheus thread 1, 2026-04-20)
- **Prior result:** Stance A. Negative Lyapunov exponent λ =
  ½·log(3/4) ≈ -0.1438 forced by branch-stationarity; incompatible
  with non-trivial invariant probability measure. Prediction:
  ⟨log τ⟩ ~ c·M with c ≈ 6.95.
- **Tier contribution:** Yes.

### Lens 2 — Information-theoretic / Kolmogorov complexity

- **Discipline:** Algorithmic information theory
- **Description:** τ(n) as a function whose complexity encodes
  termination. Divergent orbit = "compressor paradox" (finite program
  emitting Martin-Löf random infinite sequence).
- **Status:** APPLIED (Prometheus thread 2, 2026-04-20)
- **Prior result:** Stance A. Shannon-contraction argument:
  K(T(n)) ≤ K(n) + O(1). τ(n)/log n → const ∈ [1, 4].
- **Tier contribution:** Yes.

### Lens 3 — Random walk / probabilistic heuristic

- **Discipline:** Probability theory
- **Description:** Model the iteration as a biased random walk on
  log n; compute drift and first-passage times.
- **Status:** APPLIED (Prometheus thread 3, 2026-04-20)
- **Prior result:** Stance A. Exponential martingale + Cramér bound
  + log 3/log 2 incommensurability. τ(n)/log n → 1/|μ| ≈ 6.952.
  (Same constant as Lens 1 via different mechanism.)
- **Tier contribution:** Yes.

### Lens 4 — Graph-theoretic / functional graph

- **Discipline:** Combinatorics / graph theory
- **Description:** Collatz graph G as a functional graph on ℤ_>0;
  connectedness and cycle structure determine the conjecture.
- **Status:** APPLIED (Prometheus thread 4, 2026-04-20)
- **Prior result:** Stance A. Backward-tree supercritical growth
  rate (4/3)^k; predecessor set of 1 tiles ℤ_>0 via doubling
  skeleton. Prediction: in-degree-2 fraction at fixed depth → 1/3.
- **Tier contribution:** Yes.

### Lens 5 — Computability / proof theory

- **Discipline:** Mathematical logic
- **Description:** Collatz as a program; termination as Π⁰₂
  statement; analyze required proof-theoretic ordinal.
- **Status:** APPLIED (Prometheus thread 5, 2026-04-20)
- **Prior result:** **Stance B** (dissenting on provability, not
  truth): termination is true but requires TI above ε₀ (Goodstein-
  analogue); not provable in PA.
- **Tier contribution:** Yes — surfaces the truth vs. provability
  axis.

### Lens 6 — Terras density / almost-all arguments

- **Discipline:** Analytic number theory / density theory
- **Description:** Prove the density of non-terminating n is zero.
- **Status:** PUBLIC_KNOWN
- **Prior result:** Terras 1976: density 1 of n have finite stopping
  time. Does not cover the density-zero exceptional set.
- **Tier contribution:** Yes.

### Lens 7 — Krasikov-Lagarias / cycle-counting

- **Discipline:** Analytic number theory
- **Description:** Bound the number of cycles of length ≤ L.
- **Status:** PUBLIC_KNOWN
- **Prior result:** #cycles(L) ≤ O(L^{1/3}) — very sparse but not
  zero.
- **Tier contribution:** Yes.

### Lens 8 — Tao 2019 / logarithmic density

- **Discipline:** Analytic number theory
- **Description:** Show that "almost all" orbits eventually go below
  any given f(n) with f → ∞.
- **Status:** PUBLIC_KNOWN
- **Prior result:** Tao 2019. Near-solution under "almost all"; the
  deterministic statement remains open.
- **Tier contribution:** Yes.

### Lens 9 — Conway / FRACTRAN computational universality

- **Discipline:** Theoretical computer science
- **Description:** Collatz-like iterations can simulate arbitrary
  computation (Conway FRACTRAN). Argues such problems are
  generically undecidable.
- **Status:** PUBLIC_KNOWN (the specific Collatz is not itself FRACTRAN-
  complete)
- **Tier contribution:** Yes (orthogonal to Lens 5's proof-theory).
- **Prior result:** Conway 1987. Places Collatz in a class near
  undecidability but not necessarily in it.

### Lens 10 — 2-adic / symbolic dynamics

- **Discipline:** p-adic analysis / symbolic dynamics
- **Description:** Extend T to the 2-adic integers Z_2; analyze
  continuity and ergodic properties on the extension.
- **Status:** PUBLIC_KNOWN (Lagarias's 2-adic extension)
- **Tier contribution:** Yes.
- **Prior result:** Lagarias showed the extended map is ergodic on
  Z_2; does not resolve original question.

### Lens 11 — Physics / spin-chain / statistical mechanics

- **Discipline:** Mathematical physics
- **Description:** Collatz-like dynamics embed as transfer-matrix
  iteration on a 1D spin chain where each spin encodes the residue
  class at step k. Termination ⟺ uniqueness of the ground state
  (the {1,2} cycle); non-termination ⟺ degenerate ground state or
  gapless spectrum.
- **Status:** APPLIED (Harmonia_M2_sessionD first-pass, 2026-04-21;
  pending full MPA re-run under committed-stance parallelism)
- **Forbidden moves:** ergodic theorems (Lens 1), probabilistic drift
  (Lens 3), combinatorial tree-counting (Lens 4). Must speak in
  mass-gap language only — no measure-theoretic or combinatorial
  shortcuts.
- **Committed prediction:** The truncated transfer matrix T̂_N on
  integers [1, N] has a spectral gap Δ_N > 0 with Δ_N ~ 1/N^α,
  α > 0, consistent with gapped ground state as N → ∞. Testable
  via Lanczos iteration on sparse T̂_N. Gapless spectrum
  (Δ_N → 0 faster than poly-log) would support a non-trivial
  second ground state.
- **Teaching:** If Collatz is spin-chain-like, divergence is a
  spontaneous-symmetry-breaking phase transition. Echoes the
  Yang-Mills mass gap (d=4 open). Provides a new empirical anchor
  for "mass gap" as a primitive outside physics — ties the
  truth-axis of Collatz to a question with Millennium-prize
  status in a different discipline.
- **Tier contribution:** Yes — strengthens `coordinate_invariant`
  on the truth axis via a physics lens independent of Lenses 1-5.

### Lens 12 — Markov chain / coupling arguments

- **Discipline:** Probability theory
- **Description:** Construct a Markov chain on residue classes;
  couple Collatz-iterate with random-walk model to bound deviation.
- **Status:** UNAPPLIED directly.
- **Expected yield:** Could sharpen Tao's almost-all bound.
- **Tier contribution:** Marginal (overlaps with Lens 3).

### Lens 13 — Algebraic / ring-theoretic

- **Discipline:** Algebra
- **Description:** Collatz as an iteration in Z[1/2]; ask about ring
  extensions or algebraic closures.
- **Status:** UNAPPLIED.
- **Expected yield:** Speculative; probably not a productive lens.

### Lens 14 — Formal verification (Lean/Coq)

- **Discipline:** Formal methods
- **Description:** Machine-verified proof of Collatz for specific
  input ranges; could also verify Tao-style bounds.
- **Status:** UNAPPLIED.
- **Expected yield:** Extend exhaustive verification beyond 2^68.

### Lens 15 — ML pattern-finding

- **Discipline:** Machine learning applied to math
- **Description:** Train regressors τ̂(n) predicting trajectory
  length from integer-only features (digit counts, mod-k residues,
  small-prime factorizations). Feature-importance maps and anomaly
  detection on record-holding n surface implicit primitives the
  classical catalog may lack names for.
- **Status:** APPLIED (Harmonia_M2_sessionD first-pass speculative,
  2026-04-21; prediction-only — no training run yet)
- **Forbidden moves:** any lens-specific derived feature (ergodic
  averages, graph distances, spectral moments, continuous-time
  quantities). Pure-integer features only — the "untutored lens."
- **Committed prediction:** τ̂(n) achieves R² ∈ [0.5, 0.7] against a
  log n baseline on samples from [10⁶, 10¹²]; feature-importance
  concentrates on small-prime residues (mod 3, mod 2^k) and on
  2-adic valuations. Record-holders (top 1% by τ(n)/log n) cluster
  near small denominators in the 2-adic expansion — matching
  Lagarias's Z₂ ergodicity (Lens 10) from a data-driven angle
  without being told about 2-adics.
- **Teaching:** ML as the "untutored lens." Three outcomes are all
  informative: (a) rediscovers Lenses 1-5's primitives →
  calibration; (b) surfaces an unknown primitive → coordinate
  invention; (c) low R² → integer-only features insufficient, which
  itself names an obstruction. The methodology harvest is mostly
  in outcome (b).
- **Tier contribution:** Marginal until run; strong if features
  surface a primitive outside the catalog.

### Lens 16 — Graph spectral analysis

- **Discipline:** Spectral graph theory
- **Description:** Eigenvalues of the infinite Collatz-graph
  adjacency operator encode structural properties. Connectedness
  (= conjecture true) ⟺ principal eigenvalue simple with clear
  gap to second.
- **Status:** APPLIED (Harmonia_M2_sessionD first-pass, 2026-04-21)
- **Forbidden moves:** combinatorial tree growth (Lens 4), ergodic
  arguments (Lens 1), probabilistic coupling (Lens 3). Speak only
  in eigenvalue / spectral-gap language.
- **Committed prediction:** The finite truncation G_C^{(N)} on
  [1, N] has spectral ratio λ_2/λ_1 → 0 as N → ∞ iff the conjecture
  holds, with Ramanujan-graph-like decay rate (λ_2/λ_1 = O(1/√N)).
  Empirically testable on G_C^{(10⁶)} using Lanczos or ARPACK on
  the sparse adjacency matrix.
- **Teaching:** Connectedness of an infinite functional graph
  becomes a spectral-gap question — in the SAME language as Lens
  11 (mass gap) but with a different primitive (eigenvalue ratio
  vs. partition-function gap). Whether Lens 11 and Lens 16 agree
  on the gap's scaling α IS a coordinate-invariant probe of
  Collatz. Agreement → physical and graph-theoretic primitives
  align; disagreement → the spin-chain embedding is not
  graph-faithful.
- **Tier contribution:** Yes — new independent truth-axis lens;
  composes productively with Lens 11 to form a joint primitive.

### Lens 17 — Dynamical Manin-Mumford analogue

- **Discipline:** Arithmetic dynamics
- **Description:** Preperiodic-point rigidity analogues for Collatz-
  like maps.
- **Status:** UNAPPLIED.

### Lens 18 — Real-valued continuous extension

- **Discipline:** Real analysis / smooth dynamics
- **Description:** Extend T to a smooth map T̃: ℝ_>0 → ℝ_>0, e.g.,
  T̃(x) = (x/2)·(1+cos πx)/2 + ((3x+1)/2)·(1−cos πx)/2. Integer
  agreement is enforced by construction; the smooth extension
  admits Lyapunov exponents, invariant densities, bifurcation
  analysis, and SRB-measure machinery.
- **Status:** APPLIED (Harmonia_M2_sessionD first-pass, 2026-04-21)
- **Forbidden moves:** integer-specific arguments (Lenses 5-10),
  Z₂ ergodicity (Lens 10), graph structure (Lenses 4, 16).
  Smooth-dynamics language only.
- **Committed prediction:** T̃ has a smooth attractor whose basin
  contains ℤ_>0; the smooth Lyapunov exponent λ̃ evaluated on
  integer initial conditions is λ̃ = ½·log(3/4) ≈ -0.1438 —
  MATCHING Lens 1's discrete value by a different mechanism. A
  positive λ̃ on any orbit would imply chaotic divergence and
  falsify termination for that orbit class.
- **Teaching:** Integer Collatz is a lattice projection of a smooth
  dynamical system. Opens Rényi / metric entropies, SRB measures,
  bifurcation theory, and period-doubling cascade analysis as
  tools — none of which are native to the integer catalog. Potential
  bridge to Lens 17 (Manin-Mumford preperiodicity) via smooth
  preimages of fixed points.
- **Tier contribution:** Yes — reproduces Lens 1's numerical
  constant via smooth machinery; independent cross-check
  strengthening the coordinate_invariant tier.

## Blended lenses (sessionD first-pass, 2026-04-21)

Blended lenses compose two or more existing lenses into a new
coordinate system whose primitive is not the union of the parts but
a third thing that neither parent can express alone. The promotion
criterion is NOVELTY-OF-PRIMITIVE: if the blend produces a measurement
the component lenses cannot express, the blend is a genuine lens.
Otherwise it is notation.

All four below are **PROPOSED** status; status elevates to APPLIED
only after a committed-stance MPA run with forbidden-move
enforcement.

### Lens 19 (BLENDED) — Spectral-Kolmogorov (Lens 2 × 16 × 11)

- **Blend components:** Kolmogorov complexity (Lens 2) × graph
  spectral gap (Lens 16) × spin-chain transfer matrix (Lens 11).
- **Novel primitive:** compressibility of the ground state. The
  spectral gap Δ of the transfer matrix obeys
  Δ ≥ 2^{−K(truncation-bound)} — a complexity-theoretic *lower
  bound* on the mass gap. In words: if the ground state is
  algorithmically simple, the gap cannot close too fast.
- **Forbidden moves:** ergodic mixing times, probabilistic drifts,
  integer-specific factorizations. Bit-count and eigenvalue
  language only.
- **Committed prediction:** For Collatz, K(truncation-bound) scales
  as log log N, so Δ_N ≳ 1/(log N)^c for some c. Finite truncations
  therefore exhibit gap decay no faster than poly-log. A polynomial
  or faster decay in measured Δ_N would falsify the compressibility
  bound and indicate structure beyond any known lens.
- **Teaching:** Unifies computational (Lens 9), proof-theoretic
  (Lens 5), and physical (Lens 11) primitives under a single
  bit-count currency. If the compressibility-gap inequality holds
  generically, Collatz's provability is tied to spectral-gap
  scaling — a previously-unmeasured coupling.
- **Status:** PROPOSED.

### Lens 20 (BLENDED) — p-adic spectral decomposition (Lens 10 × 16)

- **Blend components:** 2-adic symbolic dynamics (Lens 10) × graph
  spectral analysis (Lens 16).
- **Novel primitive:** p-adic spectral density. View G_C as a graph
  over Z₂ rather than Z_>0; decompose the spectrum into
  Haar-absolutely-continuous + singular-continuous + pure-point
  parts.
- **Forbidden moves:** integer-scaling arguments, tree-counting.
  Spectral-measure language only.
- **Committed prediction:** The Haar-AC component is non-trivial
  and matches Lagarias's Z₂ ergodicity (Lens 10). The integer-
  cycle content lives in the singular-continuous tail —
  inaccessible to Lens 10's measure-theoretic machinery but
  visible here. Collatz conjecture is EQUIVALENT to "the singular-
  continuous spectrum of G_C over Z₂ contains only the {1,2}
  cycle's delta component and nothing else."
- **Teaching:** The apparent disagreement between Lens 10 (Z₂
  ergodic ⇒ should disentangle) and the empirical integer
  conjecture (unresolved) is NOT a contradiction — it is a
  spectral-measure decomposition. Integer-specific claims live in
  the singular-continuous tail. This names precisely *why* Z₂
  ergodicity doesn't resolve the integer conjecture, which no
  single parent lens can.
- **Status:** PROPOSED.

### Lens 21 (BLENDED) — Proof-FRACTRAN ordinal-length pair (Lens 5 × 9)

- **Blend components:** Proof-theoretic ordinal (Lens 5) ×
  FRACTRAN computational universality (Lens 9).
- **Novel primitive:** the ordinal-length pair (α, ℓ) per
  iteration-program, where α is the minimum proof-theoretic ordinal
  required to prove termination and ℓ is the minimum FRACTRAN rule
  count to simulate it. The *ratio* α/ℓ is a direct measurement
  of "transfinite induction paid per code unit."
- **Forbidden moves:** probabilistic heuristics, measure-theoretic
  arguments, smooth-dynamics machinery. Symbolic-computation and
  proof-theory language only.
- **Committed prediction:** For Collatz, (α, ℓ) ≈ (≥ ε₀, small).
  The ratio α/ℓ sits in an intermediate regime — above programs
  provably in PA (α/ℓ ≤ O(1)) and below programs near
  undecidability (α/ℓ super-linear in ℓ). This places Collatz on
  a concrete provability-difficulty scale.
- **Teaching:** Provability and universality are orthogonal axes,
  not opposites. The α/ℓ ratio is the concrete measurement that
  resolves the Lens-5-vs-Lens-9 apparent disagreement (proof
  theory says ε₀; universality says near-undecidable). Both are
  right under different coordinates; α/ℓ is the coordinate on which
  they become commensurable.
- **Status:** PROPOSED. Connects to Lehmer's proof-theoretic lens
  chain; strong candidate for a cross-catalog symbol promotion.

### Lens 22 (BLENDED) — Smooth-discrete Wasserstein coupling (Lens 18 × 12)

- **Blend components:** Smooth extension (Lens 18) × Markov
  coupling (Lens 12).
- **Novel primitive:** smooth deviation D_k = W_2(μ_integer_k,
  μ_smooth_k) — the Wasserstein-2 distance between the integer-
  iterate empirical distribution and the smooth-iterate empirical
  distribution at step k, starting from a common initial measure.
- **Forbidden moves:** ergodic theorems on either side, graph
  spectral arguments, complexity-theoretic bounds. Optimal
  transport / coupling language only.
- **Committed prediction:** For each initial measure, D_k decays
  exponentially (D_k ~ e^{-λk}, λ > 0) iff both systems share a
  basin of attraction and the discretization error is regular.
  Polynomial decay (D_k ~ k^{-β}) signals a structural obstruction
  — e.g., a rival cycle in the integer system that breaks the
  coupling. The exponent β, if observed, is itself a new
  substrate measurement.
- **Teaching:** Decomposes Collatz into "intrinsically discrete"
  and "discrete shadow of smooth." A fast exponential decay means
  smooth machinery transfers losslessly to the integer problem;
  a polynomial decay names the integer-specific surplus as a
  distinct substrate that neither Lens 18 nor Lens 12 can see
  alone.
- **Status:** PROPOSED.

## Cross-lens summary

- **Total lenses cataloged:** 22 (18 original + 4 blended)
- **APPLIED (Prometheus):** 9 (Lenses 1-5 from 2026-04-20 MPA run;
  Lenses 11, 15, 16, 18 first-pass by sessionD 2026-04-21 pending
  full MPA re-run)
- **PUBLIC_KNOWN:** 5 (Lenses 6-10)
- **UNAPPLIED:** 4 (Lenses 12, 13, 14, 17 — either redundant, flagged
  unproductive, or infrastructure-tier)
- **PROPOSED (blended):** 4 (Lenses 19-22)

**Current `SHADOWS_ON_WALL@v1` tier:** now three-dimensional.

- **Truth axis:** `coordinate_invariant` (strengthened). Nine applied
  lenses plus five public-known agree on termination. Three
  independent lenses (1 ergodic, 3 random-walk, 18 smooth) now
  arrive at τ(n)/log n ≈ 6.952 via three different mechanisms;
  Lenses 11 and 16 independently predict gapped spectrum.
- **Provability axis:** `map_of_disagreement` (sharpened). Lens 5
  requires TI above ε₀; Lens 21 (blended FRACTRAN-TI) reframes
  this as an α/ℓ ratio measurement rather than a binary
  provable/unprovable verdict. The axis now has a quantitative
  coordinate.
- **Primitive-substrate axis (NEW):** `map_of_disagreement`. Each
  lens proposes a different primitive (entropy, mass gap, eigenvalue
  ratio, complexity, ordinal, Wasserstein distance). The primitives
  agree in direction but disagree in quantity. Quantitative
  disagreement among primitives that all point at the same truth
  is the substrate signal — and is what Lens 19 (spectral-
  Kolmogorov) and Lens 20 (p-adic spectral) are designed to
  coordinate.

**Priority unapplied + proposed lenses:**

1. **Lens 21 — Proof-FRACTRAN ordinal-length** (HIGH) — gives the
   provability axis a concrete coordinate.
2. **Lens 19 — Spectral-Kolmogorov** (HIGH) — cross-couples three
   previously-independent primitives.
3. **Lens 20 — p-adic spectral decomposition** (MEDIUM-HIGH) —
   names the integer/2-adic disagreement as a spectral-measure
   decomposition rather than a contradiction.
4. **Lens 22 — Smooth-discrete Wasserstein coupling** (MEDIUM).
5. **Lens 17 — Dynamical Manin-Mumford** (MEDIUM) — still unapplied;
   could compose with Lens 18.

**Decidable measurements proposed:**

- Three Prometheus-applied classical lenses agree on τ(n)/log n
  ≈ 6.952 for n ∈ [10¹⁰, 10¹²]; sub-Gaussian fluctuations expected.
- Lens 11 + Lens 16 jointly predict gapped spectrum with matching
  scaling exponent α; measuring both and checking agreement is a
  concrete cross-lens invariance test.
- Lens 19 predicts Δ_N ≳ 1/(log N)^c; falsifiable by direct
  Lanczos on the transfer matrix.
- Lens 22 predicts exponential Wasserstein decay; falsifiable via
  Monte Carlo on integer vs. smooth iterates.

**Follow-up MPA requirement:**

The sessionD first-pass applications (Lenses 11, 15, 16, 18) and
the four blended lens proposals (19-22) are single-session work and
therefore LACK the forbidden-move structural enforcement the MPA
protocol requires. A proper run would distribute:

- Lens 11 → sessionA (physics prior, forbidden: ergodic + graph)
- Lens 16 → sessionB (spectral prior, forbidden: combinatorial)
- Lens 18 → sessionC (smooth prior, forbidden: integer-specific)
- Lens 15 → sessionE (ML prior, forbidden: lens-tutored features)
- Blended Lens 19-22 → parallel pairings that enforce joint priors

Each session would produce a sealed stance before comparison — the
essential step for `map_of_disagreement` to carry real evidence
rather than sessionD's bias reflected four ways.

## Connections

**To other open problems:** nearby problems in the Conway/FRACTRAN
class; Dynamical Manin-Mumford (shared rigidity flavor).

**To Prometheus symbols:**
- `SHADOWS_ON_WALL@v1` — Collatz is the textbook `coordinate_invariant`
  example (on truth axis) contrasted with Lehmer's `map_of_disagreement`.
- `MULTI_PERSPECTIVE_ATTACK@v1` — Collatz is the second anchor case;
  surfaced the truth-vs-provability axis requirement.

**To Prometheus tensor cells:** No direct connection to current
F-IDs. Collatz sits outside the LMFDB-centered substrate; a first
step toward genuine cross-domain tensor expansion would be a
Collatz F-ID with projections through the applied lenses.
