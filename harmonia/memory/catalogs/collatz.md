---
catalog_name: Collatz conjecture (3n+1)
problem_id: collatz
version: 1
version_timestamp: 2026-04-21T00:55:00Z
status: alpha
surface_statement: Define T(n) = n/2 if n even, (3n+1)/2 if n odd. For every positive integer n, the orbit {T^k(n)} eventually reaches 1.
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
- **Description:** Recent work embeds Collatz-like dynamics in spin-
  chain transfer matrices; the conjecture becomes a uniqueness-of-
  ground-state question.
- **Status:** UNAPPLIED directly.
- **Expected yield:** Could provide physics-style mass-gap argument
  (parallel to Lehmer thread 5); introduces temperature parameter.

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
- **Description:** Train models to predict τ(n) or detect anomalous
  orbits.
- **Status:** UNAPPLIED.
- **Expected yield:** May surface heuristic patterns invisible to
  classical analysis.

### Lens 16 — Graph spectral analysis

- **Discipline:** Spectral graph theory
- **Description:** Eigenvalues of the (infinite) Collatz-graph
  adjacency matrix encode structural properties.
- **Status:** UNAPPLIED.
- **Expected yield:** Could formalize "is the Collatz graph a tree
  vs. has other components" as a spectral question.

### Lens 17 — Dynamical Manin-Mumford analogue

- **Discipline:** Arithmetic dynamics
- **Description:** Preperiodic-point rigidity analogues for Collatz-
  like maps.
- **Status:** UNAPPLIED.

### Lens 18 — Real-valued continuous extension

- **Discipline:** Real analysis / smooth dynamics
- **Description:** Extend T to a smooth map on R_>0 and analyze
  continuous dynamics; discretize back.
- **Status:** UNAPPLIED.
- **Expected yield:** Smooth-dynamics tools may apply.

## Cross-lens summary

- **Total lenses cataloged:** 18
- **APPLIED (Prometheus):** 5 (Lenses 1-5)
- **PUBLIC_KNOWN:** 4 (Lenses 6-10, approximately)
- **UNAPPLIED:** 9

**Current `SHADOWS_ON_WALL@v1` tier:** two-dimensional:

- **Truth axis:** `coordinate_invariant`. Five applied Prometheus
  lenses + four public-known lenses all agree on termination; three
  of them (Lenses 1, 2, 3) independently arrive at the SAME numerical
  constant τ(n)/log n ≈ 6.95 via different mechanisms.
- **Provability axis:** `map_of_disagreement`. Lens 5 (computability)
  says termination requires TI above ε₀; other lenses implicitly
  operate as if elementary descent suffices. This is the
  orthogonal-axis finding from the 2026-04-20 methodology run.

**Priority unapplied lenses:**

1. **Lens 11 — Physics spin-chain** (MEDIUM) — could provide mass-
   gap-style argument.
2. **Lens 18 — Real-valued continuous extension** (MEDIUM) — smooth-
   dynamics machinery is well-developed.
3. **Lens 16 — Graph spectral analysis** (LOW-MEDIUM) — formalizes
   connectedness as spectral question.

**Decidable measurements proposed:**

Three Prometheus-applied lenses agree on the concrete measurement:
measure τ(n)/log n for n ∈ [10^10, 10^12] on a representative sample;
predict mean ≈ 6.95 with sub-Gaussian fluctuations. Lens 4 proposes
a different measurement (in-degree-2 fraction at depth); both are
feasible on commodity hardware.

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
