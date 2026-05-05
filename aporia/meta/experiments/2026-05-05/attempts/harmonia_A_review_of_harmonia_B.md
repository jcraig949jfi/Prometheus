# Cross-Batch Review — Harmonia A on Harmonia B

**Reviewer:** Harmonia A (Harmonia_M2_sessionA)
**Date:** 2026-05-05
**Batch reviewed:** Harmonia B — Dynamical Systems (P1 Furstenberg ×2 ×3, P2 Sarnak Möbius, P3 Palis, P4 Painlevé n-body, P5 KAM Hénon-Heiles)
**Files reviewed:**
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_B_summary.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_B_01_furstenberg_x2x3.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_B_02_sarnak_mobius.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_B_03_palis.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_B_04_painleve_n_body.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_B_05_kam_stability.md`
- support scripts at `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\_scratch_B\`

---

## 0. Top-line verdict

**Harmonia B's batch is the strongest of the three I have now reviewed
(my own A, plus C, plus B).** It produced four genuinely substrate-grade
observations — finite-N Möbius indistinguishability (P2), float64
underflow as a substantive computational obstruction (P1), the
Lyapunov-spectrum-blind-to-tangency observation (P3), and the
multiplicative-subgroup-index-matches-finite-orbit-fraction observation
(P1) — and produced the cleanest cross-problem synthesis of the
batches I have seen (the two-class A/B obstruction taxonomy).

**It also has the same structural issue as C's batch: under-budget,
recipe-driven, and the most interesting attacks are the ones explicitly
marked "sketched, NOT executed."** B used 7.5 of 15 budgeted hours.
The unrun attacks include exactly the experiments that would
calibrate the substrate-grade claims B did make. Round 2 absorbs the
remaining 7.5 hours by executing the sketched attacks.

**Falsification-first read on B's own claims.**
- The four substrate-grade observations are real and well-anchored;
  this is the strongest output across the batches.
- The "two-class taxonomy" (Class A: missing rigidity functional in
  zero-entropy / sub-uniform regime; Class B: missing sharp
  finite-dimensional bound) is a real pattern — but Class A applied
  to *three* problems and Class B to *two* in a 5-problem batch,
  which is a thin anchor count. The taxonomy is a candidate
  observation, not a settled pattern.
- The "Class B problems closed within ~10 years by computational
  advances" prediction (in `harmonia_B_summary.md`) is
  reward-signal-capture-flavored. Painlevé n=4 has resisted 30+
  years; KAM explicit bounds 50+. "10 years by computational
  advances" lacks the rigor of the rest of the batch.
- The float64-underflow finding in P1 is honest but **the workaround
  is 5 lines of code** (Python's `Fraction` or `decimal` with high
  precision). B reported the obstruction without applying the
  obvious fix and re-running. That is *not* "the computational
  instrument was not strong enough"; it is "the chosen instrument
  configuration was wrong."

This review is direct. The batch is good; round 2 is where the
substrate signal compounds.

---

## 1. Per-problem critique and round-2 proposals

### P1 — Furstenberg ×2 ×3

**Critique of round 1.**
- Attack 1 (float64 underflow) is presented as "the computational
  instrument was not even strong enough to attempt the conjecture
  without exact arithmetic." This is true *for the attempted
  configuration* but the fix is trivial: `from fractions import
  Fraction` and represent x as `Fraction(p, q)` with q a power of
  6. With `Fraction`, ×2 and ×3 are exact; orbit walks are bounded
  in numerator size only by the number of iterations. **Why this
  was not done in round 1 is the load-bearing question.** It looks
  like the catch was reported as the substrate-signal *because* it
  was a clean halt, rather than as a workaround prompt.
- Attack 3 (Z/q finite analog) is the cleanest result: visited
  fraction `~ 0.46` for `q ∈ {23, 47}` matching `<2,3> ≤ (Z/q)^×`
  index exactly. Solid.
- Attack 4 (Hochman-style, sketched not run) underspecifies the
  candidate measure. The argument "any candidate must have both
  `h_{T_2} = 0` and `h_{T_3} = 0`, hence simultaneous base-2 and
  base-3 determinism, hence Borel-normality-is-open" hand-waves
  past Hochman 2010+ work on overlapping self-similar measures,
  which is precisely the modern setting where this question has
  structure beyond "Borel normality."
- Attack 5 (Fourier reformulation) correctly identifies that
  joint multiplicativity reduces to the coprime-to-6 sub-lattice
  but doesn't push further. A *numerical* probe of Fourier
  coefficients on that sub-lattice for candidate self-similar
  measures was the obvious next move and was not made.

**Round-2 proposal.**

1. **Re-run Attack 1 with exact arithmetic.** Replace `float` with
   `Fraction(num, 6**k)` for `k = 0..N`; orbit is exact through
   any finite iteration count. Compute the empirical histogram of
   orbits seeded at small dyadic-rational-coprime-to-3 starts. The
   histogram on rationals is finite-supported (rationals are
   eventually periodic) — observe the *distribution of period
   lengths* and tail behavior. Substrate-grade because it is the
   correct probe of the topological-rigidity-vs-measure-rigidity
   gap on rationals.
2. **Profinite probe on `Z_q`.** For `q ∈ {5, 7, 11, 13, 17, 19,
   23, 29}`, simulate ×2 and ×3 on `Z/q^k` for `k = 1..6`. Track
   the joint-orbit fraction across `k`. Does it stabilise toward
   Haar (= 1) or toward a non-trivial limit measure? Specifically
   for `q = 23, 47` where `<2,3>` is index-2 — does the index-2
   subgroup persist into `Z_q^k` for higher `k`? This addresses
   the "profinite limit may give different question than `Z/q`"
   point B raised but didn't probe.
3. **Hochman-style entropy-of-projections.** Pick a specific
   self-similar measure `μ` invariant under `T_2` (e.g., the
   natural Bernoulli measure on a 1-step subshift of finite type
   over `{0, 1}`). Compute `μ̂(3^j n)` for `j = 0, 1, 2, ...,
   small n`, check whether the joint multiplicativity is
   compatible with `T_3`-invariance. This is the *concrete*
   self-similar-measure attack.
4. **Numerical Fourier coefficient probe on the coprime-to-6
   sub-lattice.** Build candidate non-Lebesgue measures from
   1-step Bernoulli over `{0, 1, 2}` (base-3 self-similar) and
   compute their Fourier coefficients at `n` coprime to 6.
   Plot `|μ̂(n)|` vs `n`; non-Lebesgue measures should give
   non-zero coefficients on this sub-lattice; match against the
   `T_2`-invariance condition `μ̂(2k) = μ̂(k)`.

**Round-2 verdict candidate:** PARTIAL_RESULT (exact arithmetic
fixes the obstruction; profinite probe gives a finite-arithmetic
finer picture than `Z/q`; Fourier sub-lattice probe surfaces
candidate non-Lebesgue structure or its absence).

**Effort estimate:** ~3-4 hours total.

---

### P2 — Sarnak Möbius disjointness

**Critique of round 1.**
- The substrate-grade observation in Attack 4 — at `N = 10^6`,
  Sturmian `|S(N)|/N = 6.2e-5` is *smaller* than random
  positive-entropy `7.7e-5`, both at `N^{-1/2}` rate — is the
  highest-quality observation in the batch. It forecloses naive
  numerical falsification of Sarnak. **This deserves promotion to
  the methodology toolkit as a Pattern 21-flavored stratification
  caveat: "finite-N decay rates do not separate proven cases from
  positive-entropy controls."**
- Attack 5 (BSZ correlation criterion on IET) is the highest-
  leverage *unrun* experiment in the batch. B says it would be
  "informative" and lists IETs as "open-territory" zero-entropy
  systems, then doesn't execute. This is exactly the experiment
  that round 2 should run.
- Citations are uniformly `[paraphrase]`-flagged. The Bourgain-
  Sarnak-Ziegler arXiv ID `1110.0992` and the Tao 2017 *Forum of
  Math Pi* citation are real (I am near-certain on both from
  prior recall) but B did not verify either — and it costs ~30
  seconds to verify the arXiv ID.

**Round-2 proposal.**

1. **Execute Attack 5: BSZ correlation criterion on an IET.**
   Implement a simple 3-interval IET on `[0, 1]` with rotation
   angle `α = √2`. Compute the BSZ correlation `(1/N) Σ_{n≤N}
   f(T^{pn} x) f̄(T^{qn} x)` for `(p, q) = (2, 3), (3, 5), (5, 7)`
   at `N = 10^4, 10^5, 10^6`. Plot decay vs `N`. If it decays at
   `N^{-1/2}` (consistent with Sarnak), that's numerical evidence
   the conjecture holds for IETs in this regime; if it stays
   bounded away from 0, that's a candidate falsifier (extremely
   unlikely but the experiment should run).
2. **Logarithmic Chowla numerical check.** Tao 2017 proved the
   logarithmic Chowla (`(1/log N) Σ_{n≤N} μ(n)/n → 0`). Compute
   `(1/log N) Σ μ(n)/n` for `N = 10^k, k = 3..7` and verify the
   decay rate. Calibration anchor for the technical thread Tao
   used.
3. **Cross-correlation between two zero-entropy systems.**
   Compute `(1/N) Σ μ(n) f_1(T_1^n x_1) f_2(T_2^n x_2)` for
   `f_1` = Sturmian, `f_2` = polynomial phase, `f_1, f_2`
   substitution-system. If the cross-correlations decay strictly
   faster than each individual sum, that's evidence of joint
   independence; if not, it surfaces a structural correlation
   the conjecture predicts shouldn't exist.
4. **Verify all citations.** A 30-second arXiv lookup for
   `1110.0992` and a Google Scholar lookup for "Tao 2017 Forum
   Math Pi logarithmic Chowla" replace half the `[paraphrase]`
   flags with hard citations.

**Round-2 verdict candidate:** PARTIAL_RESULT (BSZ on IET; log-Chowla
calibration; cross-correlation probe; tighter citations).

**Effort estimate:** ~4 hours.

---

### P3 — Palis density of hyperbolicity

**Critique of round 1.**
- Attack 1 (Lyapunov spectrum on 3D skew product) gives a
  beautiful negative result: spectrum `(0.352, 0.336, 0.000)`
  flat across α ∈ [0, 0.6]. Attack 2 (min stable/unstable angle)
  shows monotone collapse from 87° to 5° on the *same* sweep.
  Together these are the cleanest substrate-grade observation in
  B's batch: **Lyapunov methods are blind to tangency-class
  non-hyperbolicity; geometric methods (min-angle profiles) see
  it.** Worth promoting.
- B correctly notes that the skew-product toy *cannot* model the
  heterodimensional-cycle obstruction (skew products preserve
  index of periodic orbits). So the min-angle observation is on
  the *tangency* side of the conjecture, not the *heterodim*
  side. The presentation in §7 (Honest read) does flag this
  but the abstract / verdict could conflate.
- Attack 3 (heterodim cycle search in 3D Hénon-like) marked as
  3-6 hours, not run. This is the *correct* experiment for the
  heterodim side of Palis. B has 7.5 hours of budget remaining;
  this should have been done.
- Attack 4 (periodic-orbit count) marked intractable. Fair —
  but tractable on small period: count periodic orbits of period
  ≤ 10 numerically via Newton iteration on initial conditions.
  Even period 10 with refinement gives 50–200 orbits in standard
  3D Hénon-like maps.

**Round-2 proposal.**

1. **Execute Attack 3: 3D Hénon-like heterodim cycle search.**
   `f_{α, β}(x, y, z) = (1 - α y² + z, x + β y, β z)`. Find two
   saddle fixed points; compute their stable/unstable manifolds
   numerically via parameterization-method finite-Fourier (Cabré-
   Fontich-de la Llave style); look for non-transverse
   intersections in a 2-parameter sweep. Even a low-resolution
   search produces calibration data on what a heterodim crossing
   "looks like" geometrically.
2. **Generic 3D perturbation off skew-product.** Replace the
   skew-product toy with `f(x, y, z) = (3.7 x(1-x), y + α
   sin(2πx) + γ sin(2πz), z + δ x²)`. The `δ x²` term breaks
   skew-product structure; track *both* Lyapunov spectrum and
   min-angle profile. Does the spectrum now move with the
   parameters, contradicting the Attack-1 observation? If yes,
   the Attack-1 finding is skew-product-specific. If no, the
   "Lyapunov blind to tangency" pattern survives non-skew-product
   perturbation, strengthening the substrate observation.
3. **Cone-field / dominated-splitting numerical detector.** At
   each phase-space point, find the cone field `C(x) ⊂ T_x M`
   that is forward-invariant under `Df`. Track the expansion rate
   inside the cone vs contraction rate outside. A *dominated
   splitting* exists iff the ratio is bounded away from 1 across
   the orbit. Implement on the toy + the perturbed version;
   compare to Lyapunov + min-angle. Three-detector cross-check
   on the same orbits.
4. **Periodic orbit count on small period.** Newton iteration to
   find period-`k` orbits for `k = 1..10`. Count growth rate vs
   `k`. Substrate-relevant because positive topological entropy
   `↔` exponential periodic orbit growth.

**Round-2 verdict candidate:** PARTIAL_RESULT (heterodim crossing
calibration; generic-perturbation Lyapunov-vs-angle confirmation
or refutation; cone-field detector shipped).

**Effort estimate:** ~5 hours.

---

### P4 — Painlevé n-body (n = 4)

**Critique of round 1.**
- The single highest-leverage missing action: **B has a
  low-confidence recollection of "Fleischer 2024 (or recent)"
  preprint claiming to settle the planar 4-body case** and writes
  "I cannot verify this and flag it as uncertain." This is not a
  flag-and-move-on situation. **If a 2024 preprint really
  settled Painlevé n=4, the entire P4 attempt is operating on
  obsolete information.** A 30-second arXiv search for
  "Painlevé 4-body" with `submittedDate:[2024 TO 2026]` filter
  resolves this. B did not run that search. *That is the round-1
  failure mode to fix first.*
- Attacks 1 and 2 (naive 2+2 and 1+3 configurations) cleanly show
  linear escape — substrate-grade negative on symmetric ansätze.
  Energy drift `< 10^{-9}` confirms it's not numerical artifact.
  Solid.
- Attack 3 (Xia n=5 reproduction) marked as 3-4 hours, not run.
  This is the *calibration anchor* the negative results lack:
  show the integrator handles a known-singular configuration
  before claiming naive symmetric configurations don't produce
  singularities. Without this anchor the linear-escape results
  are slightly empty — the integrator might be missing the
  effect for numerical reasons.
- Attack 4 (Gerver's 4-body model problem, sketched) and Attack
  5 (Mather symbolic dynamics, sketched) correctly identify the
  technical bottlenecks but don't push.

**Round-2 proposal.**

1. **VERIFY THE FLEISCHER 2024 CLAIM FIRST.** WebSearch arXiv:
   `Painlevé four body` with date filter. Resolves the
   open-vs-closed status before any other work. ~5 minutes.
2. **Execute Attack 3: Xia n=5 reproduction.** Set up the planar
   binary-binary + oscillator configuration with Xia's published
   parameters. Use `mpmath` or interval arithmetic for
   integration. Verify the binary-tightening + oscillator-energy-
   gain qualitatively. Calibration anchor for "what a real
   non-collision singularity looks like in the simulator."
3. **Scattering cross-section probe for 4-body close encounters.**
   Set up: binary `(m_1, m_2)` at separation `r` with given
   internal velocity, third body `m_3` arriving on a hyperbolic
   trajectory. Sweep impact parameter and incoming velocity;
   track binary's post-encounter eccentricity and CM velocity
   change. The empirical (incoming, outgoing) scattering map is
   the computational form of Gerver's missing `η_crit` estimate.
4. **Asymmetric IC search.** Symmetric ansätze ruled out. Try
   `m_1 = 1, m_2 = 1, m_3 = 1, m_4 = 0.1` with the small body
   shuttling between a tight binary and a separated third body.
   Newton-iterate over IC space looking for bound oscillator
   trajectories (the precondition for energy transfer).
5. **CAPD-style interval arithmetic for short-time evolution.**
   Even at small T, interval-arithmetic integration certifies
   that a candidate orbit does not collide and does not blow up
   to roundoff. Doable in Python with `mpmath` + careful interval
   bracketing.

**Round-2 verdict candidate:** depends entirely on Fleischer 2024
verification. If confirmed open: PARTIAL_RESULT (Xia calibration +
asymmetric IC search + scattering map). If Fleischer 2024 actually
settled it: NEGATIVE_RESULT_ON_SUB_CASE (entire P4 framing was
obsolete; substrate-grade kill data on lit-scan failure mode).

**Effort estimate:** ~5 hours, plus the 5-minute critical lit-check.

---

### P5 — KAM Hénon-Heiles

**Critique of round 1.**
- Attack 1 (chaos-score sweep) gives `E_* ≈ 0.115-0.125`, matching
  Hénon-Heiles 1964 + modern SALI refinements. Clean.
- Attack 2 (orbit-by-orbit at `E = 0.10`) shows 5x score variance,
  consistent with KAM-coexistence picture. Solid.
- Attack 3 (rigorous-vs-empirical gap analysis) is the *key
  observation* — 30-100x gap between rigorous KAM lower bound
  (~10⁻³) and empirical chaos onset (~0.12) for Hénon-Heiles.
  But B says "I cannot recall a published explicit rigorous lower
  bound `ε_*` specifically for Hénon-Heiles" — this is a
  literature gap that should have been searched. Celletti-
  Chierchia 2007 *Memoirs AMS* would be the place to look.
- Attack 4 (SALI/GALI) marked as ~1 hour, not run. This is the
  obvious next step for orbit-level chaos certification — a
  sharper instrument than the variance-of-section-points score.
  Skipping a 1-hour high-leverage task with 7.5 hours of budget
  remaining is the central round-1 failure.
- Attack 5 (Fourier-Newton KAM torus parameterization) marked as
  3-4 hours, not run. Computational-KAM is the technical thread
  that closes the gap to within ~2x of empirical; even
  non-rigorous Fourier-Newton at finite truncation gives
  qualitative `ε_*` estimates.

**Round-2 proposal.**

1. **Execute Attack 4: SALI / GALI on the existing 72-orbit grid.**
   ~1 hour. Replaces variance-of-section-points with a clean
   per-orbit chaos certificate. Re-run the sweep with SALI;
   compare.
2. **Execute Attack 5: Fourier-Newton KAM torus solver.** At
   `E = 0.05, 0.08, 0.10, 0.12`, attempt to parameterize an
   invariant torus by its Fourier expansion `K(θ) = Σ K_n e^{inθ}`
   truncated at `|n| ≤ 32`. Newton-iterate the cohomological
   equation. Convergence at `E` vs divergence is a *numerical*
   estimate of `ε_*_computational`. Compare to empirical
   `E_* ≈ 0.118`.
3. **Compare to standard map.** The standard map `K_*` ≈ 0.971635
   (Greene 1979) is the classical KAM test bed; replicate the
   chaos-score + SALI sweep there and verify cross-system
   consistency of the methodology.
4. **Basin-of-stability scan.** Lai-Tél style basin-entropy on a
   fine grid in `(x, p_x)` at fixed `E`. Bridges the
   "regular orbit" / "chaotic orbit" classification at the
   geometric level.
5. **Search Celletti-Chierchia 2007 for explicit Hénon-Heiles
   rigorous bound.** Lit-scan gap to fill.

**Round-2 verdict candidate:** PARTIAL_RESULT (SALI sharpens chaos
onset; Fourier-Newton gives `ε_*_computational`; cross-system
calibration).

**Effort estimate:** ~3-4 hours.

---

## 2. Cross-cutting infrastructure proposals

### Tool 1 — Exact-arithmetic dynamics primitive
`harmonia/runners/exact_dyadic.py`. Wraps `Fraction` for ×2, ×3
and similar maps. Provides histogram-on-rationals tooling.
**Direct response to the P1 float64 catch.** ~2 hours to build;
unblocks any future Furstenberg-flavored work.

### Tool 2 — Möbius / multiplicative-functions sieve cache
`harmonia/runners/multiplicative_cache.py`. Sieves μ(n), λ(n),
Λ(n) for n ≤ 10⁸ once, caches to disk, exposes a fast lookup
API. Currently every Sarnak-flavored script re-sieves μ on each
run. Sieve once; share across sessions. ~1 hour to build.

### Tool 3 — Hamiltonian-orbit toolkit
`harmonia/runners/hamiltonian_orbits.py`. Includes:
- SALI / GALI computation
- Poincaré-section event detection
- Fourier-Newton KAM torus solver
- Basin-of-stability scanner
- Interval-arithmetic integration via `mpmath`

P5 needed all of these and most weren't built. ~6-8 hours to
build properly; amortizes across all future Hamiltonian-dynamics
batches.

### Tool 4 — n-body integrator with variable precision + close-encounter regularization
`harmonia/runners/n_body_orbits.py`. Standard scipy is insufficient
for singular-orbit work; CAPD-equivalent in Python is the
substrate-grade move. Includes Brouwer-Brent variable precision,
KS-regularization for binary collisions, and a Newton-iteration IC
finder for bound oscillator trajectories. ~4-6 hours.

### Tool 5 — Geometric-dynamics indicators
`harmonia/runners/geometric_dynamics.py`. Cone fields, dominated
splittings, finite-time minimum-angle profiles. P3 established
that these are the right Palis-relevant detectors; build the
library. ~3 hours.

### Tool 6 — arXiv API verifier
`harmonia/runners/citation_verify.py`. Given a "hazy citation"
string, queries arXiv (and possibly INSPIRE / MathSciNet if
credentials available) and returns a verified bibrec or
"not found." Direct response to the [paraphrase]-flag fragility
across both B and C batches. **The Fleischer 2024 incident in
P4 is the load-bearing case: a 5-minute lit verification
distinguishes "the problem is open" from "the entire attempt is
based on obsolete information."** ~2 hours to build.

### Tool 7 — Symbolic-dynamics encoder
`harmonia/runners/symbolic_dynamics.py`. IET, Sturmian,
substitution-system codings as a reusable primitive. Used in P2
and conceptually in P1. "Give me a deterministic sequence of
complexity X" inputs become a single-line call. ~2 hours.

### Dataset 1 — Reference orbital library
For n-body work: 5 known IC families with reference high-precision
trajectories: Lagrange equilateral, figure-8 choreography, Xia 5-body,
Gerver 4-body candidate, Schubart binary collision. Used by P4
round 2 and any future n-body batch. ~2 hours to assemble.

### Dataset 2 — KAM-system benchmark library
Hénon-Heiles, standard map, perturbed pendulum, Sun-Jupiter
restricted, spin-orbit. Each with documented `ε_*_empirical` and
`ε_*_rigorous` (where published). Future KAM probes compare
against these. ~3 hours.

### Dataset 3 — Möbius / Chowla finite-N table
At N ∈ {10⁴, 10⁵, 10⁶, 10⁷} for: Sturmian, polynomial-phase,
IET, nilsystem, plus matched random-CLT controls. Anchor for
the P2 finite-N indistinguishability observation. ~2 hours
(once Tool 2 is built).

---

## 3. Additional solution angles

### P1 — Furstenberg ×2 ×3
- **Adelic / S-arithmetic perspective.** The natural infinite-dim
  analog of Z/q is the adelic ring `A_Q`. Joint ×2, ×3 invariance
  on `A_Q / Q` reduces to a question about `Z_p` for `p ∈ {2, 3}`
  and `R/Z` jointly. Speculative — closing this would not solve
  the original conjecture but might surface a different rigidity
  functional.
- **Connection to the Baker-Erdős conjecture on normal numbers
  in different bases simultaneously.** B touched this in Attack
  4. The connection is real; what's not done is a numerical
  probe of base-2-base-3 simultaneous determinism candidates
  (e.g., Liouville-type numbers).

### P2 — Sarnak Möbius
- **Quantum-walk-on-graph zero-entropy systems.** Quantum random
  walks on Cayley graphs of nilpotent groups are zero-entropy
  classical systems with positive complexity. The BSZ machinery
  works for nilsystems; do quantum walks reduce to nilsystem
  factors, or do they sit in the open territory? Speculative;
  literature exists (Frantzikinakis circle).
- **Random matrix theory analogy.** Σ μ(n) f(T^n x) at finite N
  has a fluctuation distribution. RMT predicts specific
  distributions for analogous quantities in random sequences.
  Compare empirical Möbius-weighted-sum distributions against
  GOE/GUE/CLT. Substrate-grade because it operationalizes the
  finite-N indistinguishability observation as a *distribution*
  rather than a magnitude.

### P3 — Palis
- **Persistent homology of stable/unstable manifolds.** As a
  parameter is varied through a tangency, the topological
  structure of the stable/unstable intersection changes; persistent
  homology detects this with quantified persistence. Speculative
  but concrete: build a Vietoris-Rips filtration on the manifold
  intersection point cloud.
- **Machine-learning detector trained on tangency vs heterodim.**
  Given a labeled training set of "this orbit segment is in a
  tangency neighborhood" vs "this is a heterodim cycle approach,"
  train a small NN to classify. Substrate-grade if the trained
  detector generalizes to systems outside the training
  distribution.

### P4 — Painlevé n=4
- **Hamilton-Jacobi PDE on configuration space.** The n-body
  problem reduces to an HJ PDE. Singular orbits correspond to
  singularities of the PDE solution. Numerical PDE methods
  (level-set, fast-marching) might surface the singularity
  manifold. Speculative; high computational cost.
- **Symplectic-integrator + rigorous-error-bound combination.**
  Recent work by Nakhleh / others on KS-regularized symplectic
  integrators for n-body close encounters. Build the integrator;
  apply to candidate Painlevé orbits; verify post-singularity
  trajectories.

### P5 — KAM
- **Renormalization-group fixed point of the small-divisor
  iteration.** MacKay's RG approach to KAM (1980s) treats
  KAM → near-critical → chaotic as an RG flow. Compute the RG
  flow numerically on Hénon-Heiles; identify the fixed point;
  compare to empirical `E_*`.
- **Optimal control / variational formulation.** Find the orbit
  that minimizes a "stability functional" on the phase space.
  Below `ε_*` the minimizer is a KAM torus; above, it's a
  chaotic orbit. Variational viewpoint may give numerically-
  tractable bounds.

---

## 4. Recommended round-2 sequencing

If round 2 is greenlit at the same ~15h budget:

1. **Build Tool 6 (arXiv verifier) first.** ~2 hours. This is the
   load-bearing primitive — the Fleischer 2024 incident shows
   that a single unverified citation can invalidate an entire
   attempt's framing.
2. **Verify Fleischer 2024 Painlevé claim.** ~5 minutes.
   Determines whether P4 is open or closed; may reframe the
   entire batch.
3. **Build Tool 1 (exact dyadic), Tool 2 (multiplicative cache),
   Tool 5 (geometric dynamics indicators).** ~6 hours total.
   Unblocks P1, P2, P3 round-2.
4. **P5 round 2** (~3 hours): SALI on existing grid, Fourier-Newton
   torus solver. Highest ROI per hour because Tool 3 is partially
   built (B has DOP853 + section detection already in place).
5. **P3 round 2** (~5 hours): heterodim cycle search; generic
   perturbation off skew-product; cone-field detector.
6. **P2 round 2** (~4 hours): BSZ on IET; log-Chowla; cross-correlation.
7. **P1 round 2** (~3 hours): exact-arithmetic re-run; profinite
   probe; Hochman-style measure.
8. **P4 round 2** (~5 hours, or more if Fleischer 2024 reframes):
   Xia reproduction; scattering cross-section; asymmetric IC search.

Total ~28 hours, well past 15. If 15 is hard, drop P1 or P3 round 2
(P5 + P2 + P4 cover the highest-leverage observations).

**Compounding return.** Tools 1-7 live in `harmonia/runners/` and
amortize across every future dynamical-systems batch. The
arXiv verifier in particular amortizes across *every* batch in the
substrate, not just dynamical systems.

---

## 5. Methodology-toolkit candidates: discipline check

Harmonia B's batch produces several candidates. Anchor-count
discipline says hold each until a second anchor surfaces.

**Candidate A — "Finite-N decay rate does not separate proven cases
from positive-entropy controls."** Anchor: P2 Attack 4 at `N = 10⁶`.
Strong concept; clean numerical anchor; relates to Pattern 21
(stratification) discipline. **Recommend: hold as candidate; promote
when a second batch confirms (e.g., applying the same logic to
Chowla, prime gaps, or any other random-vs-deterministic finite-N
study).**

**Candidate B — "Lyapunov spectrum is blind to tangency-class
non-hyperbolicity; geometric (cone field / min-angle) methods see
it."** Anchor: P3 Attacks 1-2 on the 3D skew-product toy. Strong
single anchor. **Recommend: hold as candidate; second anchor would be
applying the same Lyapunov-vs-geometric comparison on a *non-skew-
product* generic 3D perturbation in round 2.**

**Candidate C — "Float64 dyadic-action numerics fails at depth ≈ 53;
exact arithmetic required."** Anchor: P1 Attack 1. Substrate-level
operational reminder. **Recommend: this is more an operating-discipline
note than a promotable pattern. Add to `harmonia/memory/abandon_log.md`
or operating-disposition guidance, not pattern library.**

**Candidate D — Two-class A/B obstruction taxonomy.** Anchor: this
batch's 5 problems split 3-2. Thin anchor. **Recommend: hold as
candidate; second anchor would be applying the same A/B classification
to other batches (my A combinatorics batch fits Class B for Hadamard
and arguably Class A for the entropy-bounded conjectures Frankl /
Sunflower; C's analysis batch fits Class A for the conjecture triangle
and Class B for NS, YM). If three batches' problems all fit cleanly,
the taxonomy is promotable.**

**Candidate E — Z/q multiplicative-subgroup-index matches finite-orbit
fraction.** Anchor: P1 Attack 3. This is a clean piece of finite-
arithmetic-rigidity data, but it's narrowly about ×2, ×3 specifically
on `Z/q^×`. Generalises only to other multiplicatively-independent
integer pairs. **Recommend: log to methodology toolkit as a
finite-arithmetic anchor; do not promote to a substrate primitive.**

---

## 6. What I might be wrong about

This review's claims should be subject to the same falsification-first
discipline.

- **The "10 years to close Class B" critique might be too
  harsh.** B framed it as informal analysis hand-off to Aporia;
  reading it as a confident prediction is an ungenerous read.
  If B intended the 10-year window as *suggestive* not
  *predictive*, my critique overstates.
- **The Fleischer 2024 lit-check is not certain to surface a
  real paper.** If "Fleischer 2024" is a misremembering (e.g.,
  Fleisher / Fleisser / a different name; or a different
  problem), the verification returns "not found" and the
  framing reverts to "open as previously believed." But the
  asymmetry favors checking: 5 minutes either way.
- **My "exact arithmetic is a 5-line fix" claim** for P1 is
  technically correct but practically more involved than
  one-line: histogram-on-rationals is finite-supported, so the
  natural follow-up question changes shape (you're now studying
  period distributions, not orbit equidistribution). My critique
  may overstate how much the fix advances the conjecture.
- **The infrastructure-tools wishlist is ambitious.** Seven
  tools + three datasets is ~25 hours of build time. A leaner
  round 2 might build only Tools 1, 2, 6 (the minimum viable
  set: exact arithmetic, Möbius cache, citation verifier) and
  do everything else session-scale.

---

## 7. Closing read

Harmonia B's batch is the strongest of the three batches I have
reviewed. Four genuinely substrate-grade observations, a clean
two-class taxonomy candidate, and reproducible numerical artifacts
across all 5 problems. Of the three batches, this one's round-1
output most closely resembles "kill data with rich morphology"
that the batch prompt asked for.

The same structural issue recurs across all three batches reviewed:
each used roughly 50% of budget, each produced 3-5 sketched-but-not-
executed attacks per problem, and the most interesting next moves
are precisely those unrun attacks. For all three, round 2 is where
the substrate signal compounds — and B's batch in particular has
the most unrun-attack richness to harvest.

The single load-bearing item to fix in B's round 2 is the Fleischer
2024 lit-check on P4. Everything else — exact arithmetic, BSZ on
IET, heterodim search, SALI sweep — is incremental sharpening on a
solid base. Fleischer 2024 verification is the difference between
"open problem" framing and "entire attempt was based on obsolete
information" framing.

The four substrate-grade observations from round 1 — finite-N
indistinguishability (P2), Lyapunov blind to tangency (P3),
multiplicative-subgroup-index in Z/q (P1), float64 underflow as
substantive obstruction (P1) — are worth promoting at the
toolkit-candidate level today, with anchor-count discipline gating
full pattern-library promotion until a second anchor surfaces.

— Harmonia A (Harmonia_M2_sessionA), 2026-05-05
