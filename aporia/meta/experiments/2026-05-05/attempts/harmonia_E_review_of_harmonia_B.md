# Review and Critique — Harmonia B's Dynamical Systems Batch

**Reviewer:** Harmonia E (Harmonia_M2_sessionE)
**Reviewed batch:** Harmonia B — Dynamical Systems
  (`harmonia_B_{01..05}_*.md` + `harmonia_B_summary.md` in this directory)
**Date:** 2026-05-05
**Verdict:** The strongest *computational* batch I've reviewed; the
only batch with a self-summary; produced the cleanest substrate-grade
calibration data of any of the four batches. Bottleneck is **time
compression (1.5h × 5 vs 3h × 5 target)** plus **lack of
exact-arithmetic / interval-arithmetic / rigorous-numerics tooling**.
Round-2 ROI is high and concrete — most "Attack 3+, NOT executed"
sketches are 1-3 hours apiece with the right libraries.

---

## 0. Scope of this review

James asked the same four questions as for A and D:

1. What additional research could further each of the 5 solutions?
2. Could a round 2 be done for any of them?
3. Are there additional solution angles available?
4. Are there additional datasets or compute tools we could build?

This is review, not re-attempt. I'm a complexity-batch peer reviewer
and have no claim to dynamical-systems expertise — where my critique
flags a "missing angle," it may reflect a real gap or my unfamiliarity
with what's standard in the discipline.

Note: B is also the sessionB instance that shipped Pivot Move 1
(`descriptor-collapse audit substrate primitive`, commit `8b15cbab`)
earlier the same day. The closing note in `harmonia_B_summary.md`
acknowledges this. B turned around two productive directions
(infrastructure + dynamics batch) in one session — operationally
strong dual-track work.

---

## 1. Executive summary

**What Harmonia B did well:**

- **Real computational engagement on 4 of 5 problems.** Five Python
  scripts at `_scratch_B/` produced JSON result files. This is a
  sharper computational reach than A (no SAT solver), D (zero
  experiments), or my own batch (one experiment for det-vs-perm).
  When the brief said "small computational verification where
  applicable," B took it seriously.

- **Self-summary file (`harmonia_B_summary.md`) is unique to this
  batch.** B is the only researcher who synthesized cross-problem
  patterns into a separate document. The two-class obstruction
  taxonomy (Class A: missing rigidity functional; Class B: missing
  sharp finite-dim bound) is the kind of cross-problem residue
  Aporia's synthesis pass needs and is parallel to my own
  three-batch failure-mode signatures (combinatorics: saturation;
  complexity: meta-barrier; foundations: parallel-network). B
  demonstrates that **a fourth pattern — "two-class within one
  domain" — exists**, where the same domain has internally distinct
  failure morphologies.

- **Substrate-grade computational discoveries.** Several findings
  that go beyond bookkeeping:

  | finding | location | substrate value |
  |---|---|---|
  | float64 underflow on T_2/T_3 orbits within ~50 iterations | P1 Attack 1 | methodology caveat — dyadic-action numerics on R/Z requires exact arithmetic |
  | (Z/q)^× joint-orbit fraction matches multiplicative-subgroup index for q=23,47 | P1 Attack 3 | clean finite-arithmetic-rigidity calibration |
  | finite-N (10^6) indistinguishability between proven-orthogonal and positive-entropy null | P2 Attack 4 | forecloses naive simulation-based falsification of Sarnak |
  | Lyapunov spectrum constant while min stable/unstable angle drops 87°→5° | P3 Attack 2 | Lyapunov is wrong instrument for tangency-class non-hyperbolicity |
  | Hénon-Heiles E_* ≈ 0.115-0.125 reproduced via std-of-section heuristic | P5 Attack 1 | matches Hénon-Heiles 1964 + modern SALI refinements |
  | symmetric 2+2 and 1+3 four-body configs show linear escape, not finite-time singularity | P4 Attacks 1-2 | "symmetric ansatz is wrong attack space" calibration |

  The Sarnak finite-N indistinguishability finding is particularly
  load-bearing: it says **simulation-based falsification of Sarnak is
  structurally unfeasible** at any reachable N, because the CLT
  signal `~ N^{-1/2}` from the random null and the conjecture-relevant
  signal from a true counterexample would be indistinguishable at
  finite N.

- **Calibration discipline excellent.** Multiple proven cases used as
  anchors before attacking the open versions: Davenport for Sarnak,
  Sturmian sequences for Sarnak, topological rigidity for Furstenberg,
  Hénon-Heiles 1964 for KAM. Calibration-before-novelty is the
  right discipline and B held it.

- **Honest time-compression notes.** Per-problem 1.5h vs 3h target
  acknowledged explicitly in every file's header. Not buried.

**What's weakest:**

- **Time compression hit Attack 3+ depth across the board.** Every
  problem has 2-3 attacks "(sketched, NOT executed)" that are
  exactly the most informative attacks: reproducing Xia's n=5 for
  Painlevé, BSZ correlation criterion on IETs for Sarnak, SALI/GALI
  for KAM, generic 3D Hénon for Palis. Each is 1-3 hours of work
  with the right libraries.

- **No exact / interval / rigorous arithmetic libraries used.** Float64
  was the only numerical tool. B identified its inadequacy for
  Furstenberg explicitly but didn't pivot to mpmath, gmpy2, or
  symbolic representations. CAPD-style interval arithmetic (the
  standard for rigorous-numerics dynamics) wasn't tried.

- **No specialized dynamical-systems packages.** No AUTO-07p
  (continuation), no MatCont, no SageMath dynamical systems library,
  no pde-cont. SciPy IVP only.

- **Painlevé experiments were exploratory rather than reproductive.**
  B simulated naive 2+2 and 1+3 configurations and confirmed they
  don't work. The most informative single computation — reproduce
  Xia's published n=5 ICs as a calibration anchor, then perturb
  toward n=4 — was sketched as "infeasible at this scale" and not
  executed. The known-true Xia configuration is in the literature
  with explicit parameters; reproducing it is mostly engineering.

- **The unique self-summary is unique to this batch.** Other batches
  (mine included) didn't write one. The summary's two-class taxonomy
  is substrate-grade; not having it from the others is a gap.
  *Suggestion:* require a `<batch>_summary.md` from every researcher
  in future rounds.

**Headline recommendation:** A round-2 batch focused on **executing
the existing Attack 3+ sketches** with **mpmath / CAPD-style /
SALI-GALI / IET-simulator tooling**. B already designed the
experiments; round-2 needs to run them. Expected output: substrate-
grade calibration anchors that turn the existing literature-recall
analysis into reproducible computational artifacts.

---

## 2. Per-problem critique

### 2.1 Problem 1 — Furstenberg ×2 ×3 (`harmonia_B_01`)

**Verdict given:** NO_PROGRESS_DOCUMENTED_OBSTACLES.

**My read of the work:**

✓ **The Z/q joint-orbit-fraction discovery (Attack 3) is the cleanest
substrate finding in B's batch.** Empirical fraction visited at q=23
is 0.46, q=47 is 0.48 — exactly matching the predicted index of
`<2,3>` as a proper subgroup of `(Z/q)^×`. Clean, reproducible,
arithmetically grounded.

✓ **Float64 underflow obstruction (Attack 1)** is a methodology-level
finding worth promoting. T_2(0)=T_3(0)=0; double-precision orbits
collapse to fixed point within 50 steps. This is the kind of
low-level obstruction the "test data is what we're after" framing
should capture, and B captures it.

✓ **Topological-rigidity calibration (Attack 2)** confirms the
simulator on the proven case before attempting the open one.
Discipline.

✗ **Did not pivot to exact arithmetic after detecting the float64
collapse.** The fix is well-known: represent x as (a, b) with
`x = a · 2^{-b}` and track b as integer, OR use mpmath, OR use
gmpy2 with rational arithmetic, OR use Sage. B noted this in prose
("would require exact arithmetic") but didn't implement.

✗ **No profinite Z_p analogue.** B's Attack 3 finite analogue
(Z/q for prime q) was good; the natural lift is to Z_p (p-adic
integers, profinite limit). Bernoulli measures on the digit
expansion of p-adic integers give natural candidate non-Lebesgue
measures — testable computationally.

✗ **Hochman self-similar machinery not engaged even at sketch
level beyond Attack 4.** Hochman 2014's inverse theorem connects
entropy to dimension for self-similar measures on R/Z; testing
specific candidate measures (Bernoulli convolutions, IFS-attractor
measures) computationally is feasible.

✗ **Bourgain-Lindenstrauss-Michel-Venkatesh sumset method** mentioned
in literature scan but not pursued.

**Round 2 plan (~3hr):**
- Replace float64 with `mpmath.mpf` at 200-bit precision for orbit
  simulation (~30 min). Re-run the empirical-orbit measure-estimation
  with x_0 a transcendental Diophantine number; observe whether the
  histogram converges to Lebesgue.
- Implement profinite Z_p analogue with Bernoulli digit measures
  (~1hr). Test ×2-Bernoulli for ×3-invariance; should fail in a
  computable way.
- Implement Hochman-style self-similar candidate measures
  (Bernoulli convolutions on a contraction ratio) and test
  for ×2 ×3 joint invariance (~1.5hr).
- Calibrate against Rudolph 1990 positive-entropy edge case.

**Additional solution angles I'd add:**
- **Profinite / p-adic analogues.** Concrete computational handle
  on the otherwise-purely-asymptotic structure.
- **Hochman self-similar measure framework.** Hochman 2014 inverse
  theorem; entropy-dimension correspondence for self-similar.
- **Multi-scale entropy comparison.** h(T_2|μ) vs h(T_3|μ) under
  candidate measures. Rudolph's theorem says positive entropy on
  one ⇒ Lebesgue. Zero entropy on both is the open frontier.
- **Bourgain-Lindenstrauss-Michel-Venkatesh sumset method.** Sieve-
  style attack on equidistribution.
- **Connection to Littlewood's conjecture** via Einsiedler-Katok-
  Lindenstrauss: parallel rigidity result on homogeneous spaces.
- **Connection to normality questions.** Borel-normality of typical
  irrationals in base 2 AND base 3 simultaneously — open in many
  formulations.

**Datasets/tools to build:**
- **Exact-arithmetic dynamical-systems library.** mpmath / gmpy2 /
  Sage wrapper for orbit simulation under expanding maps. Should
  default to symbolic (a, b) representation where applicable.
- **Self-similar measure simulator.** IFS attractors with computable
  dimension/entropy; testbed for Hochman-style theorems.
- **Z/q / Z_p arithmetic-dynamics library.** Multiplicative
  subgroup `<2, 3>` membership; Bernoulli-digit measure generators.
- **Catalog of candidate "wild zero-entropy" systems.** None known
  but if they were constructed, they'd want to be in a registry.

---

### 2.2 Problem 2 — Sarnak Möbius (`harmonia_B_02`)

**Verdict given:** PARTIAL_RESULT (calibration + finite-N
indistinguishability).

**My read of the work:**

✓ **The finite-N indistinguishability finding (Attack 4) is the
single most substrate-grade observation in B's batch.** At N=10^6,
proven-Sturmian (6.2e-5), random null seed 42 (7.7e-5), random null
seed 123 (9.2e-5) are all within the same factor-1.5 band. Both
decay as N^{-1/2}. **Numerical falsification of Sarnak by simulation
is structurally infeasible** at finite N. This is a kill-data
observation that generalizes far beyond Sarnak — it forecloses naive
"compute and compare" battery patterns for any conjecture whose
signal is at the CLT-noise scale.

✓ **Davenport calibration (Attack 1)** and **Sturmian calibration
(Attack 3)** are correctly used as anchors. Decay rates match the
literature.

✓ **Quadratic-phase (Attack 2)** behaves as Vinogradov-Hua predicts,
with the noted "burn-in" before asymptotic kicks in.

✗ **Attack 5 (BSZ correlation criterion on IETs) not executed.** B
correctly identifies IETs as the canonical "open-territory" zero-
entropy systems — polynomial complexity, not nilsystem-modeled. The
sketch suggests "3-6 hours" to do honestly. This is the highest-
ROI single experiment in the entire dynamics batch — IETs are
precisely where the conjecture's resistance might live, and the BSZ
criterion test is mechanically well-defined.

✗ **Substitution dynamical systems not surveyed.** Thue-Morse,
Rudin-Shapiro, Fibonacci — all zero-entropy, all famous, several
have proven Sarnak-orthogonality results, all amenable to direct
simulation. Could give multiple calibration anchors.

✗ **Logarithmic Chowla not tested computationally.** Tao 2017 gives
`Σ μ(n)μ(n+h)/n` decay; computing this empirically is feasible
and gives an orthogonal observation.

✗ **No engagement with Frantzikinakis-Host complexity hypothesis.**
F-H's polynomial-complexity systems are the cleanest "open-but-might-
be-tractable" class; mentioned in lit scan but not probed.

**Round 2 plan (~3hr):**
- Implement IET simulator (~1.5hr; permutation + irrational rotation
  parameter, well-documented). Run BSZ correlation criterion at
  primes (p, q) = (2, 3), (3, 5), (5, 7); check whether
  `(1/N) Σ f(T^{pn} x) f̄(T^{qn} x) → 0` at N=10^5.
- Implement Thue-Morse and Rudin-Shapiro substitution sequences
  (~30 min). Compute Σ μ(n) f(T^n x) decay.
- Implement logarithmic Chowla `Σ μ(n)μ(n+h)/n` for h=1..10 (~30 min).
- Spend 30 min on F-H polynomial-complexity systems.

**Additional solution angles I'd add:**
- **Interval-exchange transformations (IETs).** Most-cited "open
  territory" zero-entropy systems.
- **Substitution dynamical systems.** Thue-Morse, Rudin-Shapiro,
  Fibonacci.
- **Logarithmic Chowla / Sarnak equivalence.** Tao 2017.
- **Skew-product extensions.** Zero-entropy extensions of irrational
  rotations; recent papers extend BSZ here.
- **Furstenberg systems / disjointness lattice.** Sarnak's framing
  itself; the disjointness from Möbius is one node in a larger
  lattice of mutual-disjointness questions.
- **Logarithmic averaging.** Sarnak in logarithmic vs Cesàro
  averages; some open in one, proven in the other.

**Datasets/tools to build:**
- **IET simulator with built-in BSZ-criterion test.** Standard
  formulation; reusable across other open-territory systems.
- **Substitution-system library.** Thue-Morse, Rudin-Shapiro,
  Chacon, Fibonacci as canonical instances; all with documented
  spectral / complexity properties.
- **Möbius-correlation runner.** Given a sequence (f(T^n x))_n,
  compute and plot Σ μ(n) f(T^n x), Σ μ(n)μ(n+h), logarithmic
  variants. Comparable across systems.
- **"Finite-N indistinguishability" general lemma.** B's Sarnak
  observation generalizes: any conjecture whose signal is at the
  N^{-1/2} CLT-noise scale cannot be falsified at finite N. Worth
  a short writeup in `methodology_toolkit.md`.

---

### 2.3 Problem 3 — Palis Conjecture (`harmonia_B_03`)

**Verdict given:** NO_PROGRESS_DOCUMENTED_OBSTACLES (with
quasi-tangency observation).

**My read of the work:**

✓ **The "Lyapunov is wrong instrument" finding (Attack 2)** is
substrate-grade. Lyapunov spectrum is constant `(0.352, 0.336,
0.000)` while minimum stable/unstable angle drops monotonically
from 87° to 5° as α grows. **Quasi-tangency without Lyapunov
collapse** — a clean computational demonstration of why the Newhouse
phenomenon resists Lyapunov methods. This is the kind of negative
methodology data that should feed into Prometheus's
methodology_toolkit.

✓ **Toy is correctly identified as too-rigid skew product.** B
notes the skew-product structure preserves the splitting and so
cannot model heterodimensional cycles. Self-aware about toy
limitations.

✓ **Bonatti-Diaz blender framing in Attack 5** correctly identifies
that no rigid C^1 blender is known — informative evidence *for*
the conjecture's truth in C^1.

✗ **Attack 3 (3D Hénon heterodim cycle search) not executed.** This
is the calibration anchor B's own analysis identified as needed.
3D Hénon-like maps with explicit parameters that exhibit
heterodimensional cycles are documented in Bonatti-Diaz-Viana 2005
and follow-up papers. Reproducing one and varying parameters would
have given a non-skew-product toy.

✗ **No SALI/GALI on the existing data.** B's data already has
72 orbits across the parameter sweep; adding SALI on top is ~50
lines of Python. Could have given a finer-grained chaos detector
than std-of-section.

✗ **No cone-field visualization.** B's analysis indicates cone
fields are the right instrument; building a cone-field visualizer
on the 3D toy data is ~1 hour and would directly demonstrate
B's structural claim.

✗ **Topological-entropy via periodic-orbit count (Attack 4) not
executed.** Standard technique; would have given an independent
chaos certificate.

**Round 2 plan (~3hr):**
- Replace skew-product toy with generic 3D Hénon-like map
  (~1hr). Use Bonatti-Diaz parameters from the published
  blender constructions.
- Add SALI/GALI orbit-level chaos detector to the existing
  Lyapunov code (~30 min).
- Add cone-field visualizer (~1hr).
- Periodic-orbit count for topological entropy (~30 min).

**Additional solution angles I'd add:**
- **Generic 3D Hénon / Lozi / standard-map-3D.** Real heterodim
  test beds.
- **Cone-field / dominated-splitting visualizers.** B's analysis
  identifies these as the right instrument; build them.
- **SALI/GALI/MEGNO chaos detectors.** Sharper than Lyapunov for
  individual orbits.
- **Topological entropy via periodic-orbit count.** Independent
  certificate.
- **Crovisier's connecting-lemma machinery in concrete examples.**
  Crovisier 2010 essentially reaches Palis under homoclinic-class
  hypothesis; testing the lemma's hypothesis numerically on
  candidate diffeomorphisms would surface where it bites.
- **C^r vs C^1 distinction tests.** Newhouse phenomenon in C^2 vs
  C^1; test whether B's toy exhibits Newhouse-style persistent
  tangencies in C^2 vs not in C^1.

**Datasets/tools to build:**
- **Heterodimensional-cycle test-bed library.** 3D maps with
  documented parameters known to exhibit heterodim cycles. Bonatti-
  Diaz-Viana 2005 has explicit examples.
- **Cone-field visualizer.** Given a smooth map and a region, plot
  the invariant cone field and check dominated-splitting condition
  numerically.
- **Generic-perturbation generator.** Given a base diffeomorphism,
  produce a sample of C^1-small perturbations; check how many are
  hyperbolic vs have tangency vs have heterodim cycle. This is a
  direct numerical test of Palis's density claim.
- **Newhouse-domain detector.** Identify whether a given system is
  in the Newhouse domain (persistent tangencies in C^2) numerically.

---

### 2.4 Problem 4 — Painlevé n-body (`harmonia_B_04`)

**Verdict given:** NO_PROGRESS_DOCUMENTED_OBSTACLES (with
calibrated negatives on naive 4-body configs).

**My read of the work:**

✓ **Naive 2+2 and 1+3 configurations confirmed not to produce
finite-time singularities.** Linear escape `r_max ~ v_sep · t`
across 9 runs; energy drift `< 1.5e-8`. The negative result is
clean and the framing — "symmetric ansatz is wrong attack space" —
is the right substrate-grade observation.

✓ **Energy conservation calibration is robust.** DOP853 at
rtol=1e-11 gives `~10^{-9}` energy drift. The integrator is good
enough to detect a real singularity if one occurred.

✓ **Linear-escape calibration template.** `r_max ≈ v_sep · t + O(R)`
distinguishes ballistic from singular orbits; useful as a negative
test for any future candidate.

✗ **Attack 3 (reproduce Xia n=5) was NOT executed.** This is the
single-highest-leverage missing experiment in the entire dynamics
batch. Xia 1992's construction has explicit ICs documented; the
binary-binary + oscillator structure is mechanically reproducible.
Reproducing Xia would:
  (a) calibrate the integrator on a known-true case,
  (b) demonstrate the binary-tightening + oscillator-acceleration
      mechanism numerically, and
  (c) provide the launching point for perturbing toward n=4.

  B sketched it as "3-4 hours infeasible at this scale" — but at 1.5h
  per problem and Attack 3 sketched at 4h, this represents the bulk
  of the time-compression cost.

✗ **Gerver's planar 4-body model with published ICs not run.**
Gerver 1991 has the heuristic construction; specific ICs documented
in the literature. Even if rigorous estimates fail, simulating
Gerver's proposed orbit with high-precision integration would test
whether the energy-transfer mechanism produces the predicted
acceleration over short times.

✗ **No interval-arithmetic / CAPD attempt.** CAPD (Computer-Assisted
Proofs in Dynamics) is the standard framework for rigorous numerics
in n-body problems. Even setting it up on a small test case would
have been substrate-grade.

✗ **No Levi-Civita / Kustaanheimo-Stiefel regularization.** Close
encounters in n-body destroy double-precision numerics; standard
regularizations (Levi-Civita for 2D, KS for 3D) handle this. Not
even sketched.

**Round 2 plan (~3hr):**
- Reproduce Xia's n=5 configuration with documented ICs (~2hr).
  Use double precision with KS regularization for close encounters,
  or mpmath at 100-bit precision. Verify binary-tightening +
  oscillator-acceleration over a moderate time horizon.
- Run Gerver's planar 4-body proposal with published ICs (~1hr).
  Even short-time verification of the mechanism would be
  informative.

**Additional solution angles I'd add:**
- **CAPD interval-arithmetic n-body.** Standard rigorous-numerics
  package; produces validated existence theorems.
- **Levi-Civita / KS regularization.** Standard for close encounters.
- **Symbolic dynamics on the candidate orbit.** Mather-style
  shadowing.
- **Spatial 3D vs planar 2D variants.** Xia's n=5 is 3D; Gerver's
  n=5 is planar. The dimensional distinction is load-bearing.
- **Reverse-time integration from the would-be singularity.**
  Backwards from `t = T - ε` with `ε → 0` gives a different
  perspective.
- **Recent post-2020 preprints.** B noted "Fleischer 2024" as a
  low-confidence recollection. WebSearch would resolve this in 5
  minutes; B explicitly flagged the uncertainty rather than
  fabricating.

**Datasets/tools to build:**
- **n-body simulator with KS regularization.** Standard but
  not in scipy by default; ~200 LOC.
- **CAPD wrapper for Python.** Interval-arithmetic ODE; rigorous-
  numerics frontier tool.
- **Catalog of singular n-body ICs.** Xia 1992 (n=5), Gerver
  1991/2003 (n=5), Mather-McGehee collinear, candidate n=4 ICs.
  Each with documented parameters.
- **Singular-orbit signature library.** `r_max ~ (T - t)^{-α}` for
  various α corresponds to different singularity types; provide
  a classifier given an orbit's late-time behavior.

---

### 2.5 Problem 5 — KAM Stability for Hénon-Heiles (`harmonia_B_05`)

**Verdict given:** PARTIAL_RESULT (empirical E_* ≈ 0.12 confirmed).

**My read of the work:**

✓ **Empirical E_* ≈ 0.115-0.125 reproduced.** Matches Hénon-Heiles
1964 and modern SALI refinements (E_* ≈ 0.118). 72-orbit sweep
across 12 energies with monotonically increasing chaos score.
Steepest growth between E=0.10 and E=0.13. Clean.

✓ **Coexistence at E=0.10 (Attack 2)** demonstrates the KAM picture
of mixed phase space: chaos scores at one energy span 0.020 to
0.112, factor-5 spread within a single energy.

✓ **Gap to rigorous KAM correctly identified at 30-100×.**
Locatelli-Giorgilli computational KAM gets within ~2× of empirical;
rigorous KAM at 30-100× below.

✗ **Attack 4 (SALI/GALI) not executed.** ~50 lines of Python on top
of B's existing code. Would have given orbit-level chaos certificates.

✗ **Attack 5 (Fourier-Newton parameterization) not executed.** This
is the computational-KAM technique; with sympy it's ~2-3 hours of
work and gives provable existence of KAM tori at specific energies
modulo Newton-iteration certification.

✗ **No multi-system comparison.** Hénon-Heiles is one of several
canonical KAM testbeds; standard map and restricted 3-body would
give a multi-system view of the rigorous-vs-empirical gap.

✗ **No CAPD or interval-arithmetic Newton iteration.** The path to
*proof* of KAM tori at specific energies goes through interval-
arithmetic Newton; not even set up.

**Round 2 plan (~3hr):**
- Implement SALI/GALI orbit-level chaos detector (~1hr). Re-run
  the 72-orbit sweep.
- Implement basic Fourier-Newton iteration for a specific KAM
  torus at sub-critical E (~1.5hr). Verify Newton convergence at
  E=0.05; check failure at E=0.13.
- Multi-system comparison: standard map at K_c=0.971... (Greene
  threshold), restricted 3-body Sun-Jupiter at Celletti's ε_*
  (~30 min).

**Additional solution angles I'd add:**
- **SALI/GALI/MEGNO/REM orbit-level chaos indicators.** Sharper
  than std-of-section.
- **Greene's residue method.** For symplectic maps, the breakup of
  KAM tori at specific frequencies is detectable via fixed-point
  residues of high-period orbits. Standard and computable.
- **Frequency analysis (Laskar's method).** Compute orbit
  frequencies via FFT; KAM tori have stable frequencies, chaotic
  orbits don't.
- **Computer-assisted-proof framework.** CAPD interval-arithmetic
  Newton on Fourier coefficients.
- **Locatelli-Giorgilli computational KAM in full.** 1990s technique
  has ~30 years of refinements; concrete published code in
  Mathematica that could be ported.
- **Multi-system comparison.** Standard map (Greene threshold),
  restricted 3-body (Celletti), Hénon-Heiles in one framework.

**Datasets/tools to build:**
- **SALI/GALI library.** ~50-100 LOC Python; not in widespread
  Python packages.
- **Fourier-Newton KAM solver.** ~500-1000 LOC; reusable across
  systems.
- **CAPD / interval-arithmetic Newton interface.**
- **Calibration registry for KAM systems.** Hénon-Heiles E_* ≈ 0.118,
  standard map K_c ≈ 0.971, Sun-Jupiter ε_* (Celletti's bounds),
  spin-orbit etc. — known empirical and rigorous values tabulated.
- **Cross-system frequency-analysis runner.** Given a Hamiltonian
  + parameter, output stability map across initial conditions.

---

## 3. Cross-cutting observations

### 3.1 B's two-class taxonomy is substrate-grade

The `harmonia_B_summary.md` taxonomy:

- **Class A (missing rigidity functional):** Furstenberg, Sarnak,
  Palis. Each has a proven case via positive-entropy / nilpotent /
  uniform / structurally-clean instrument; the open case fails because
  the instrument is silent in the relevant regime. **Resolution
  requires identifying a new rigidity functional.**

- **Class B (missing sharp finite-dim bound):** Painlevé n=4, KAM
  explicit bounds. Each has a heuristic mechanism known to work in
  a calibration case. **Resolution requires a single sharp
  quantitative estimate** — computer-assisted-proof in principle,
  not yet within standard CAS technology.

This is parallel to but distinct from the failure-mode signatures
I've identified across other batches:

| batch | dominant signature | resolution |
|---|---|---|
| Combinatorics (A) | `SHARP_INEQUALITY_AT_WRONG_CONSTANT` | new structural input |
| Foundations (D) | `REQUIRES_PARALLEL_OPEN_PROBLEM` | unlock single hub-problem |
| Complexity (E, mine) | `META_OBSTRUCTION_RULES_OUT_TECHNIQUE_CLASS` | techniques outside known classes |
| **Dynamics (B)** | **`TWO_CLASSES_WITHIN_DOMAIN`** | **depends on class** |

**B's signature is unique** — within a single domain, two
qualitatively different failure morphologies coexist. Class A is
"pure-math structural" (we don't know what to look for). Class B is
"computational-frontier" (we know what to compute but can't yet).
This **internal heterogeneity within domain** is itself a
substrate-grade observation that deserves promotion to a substrate
primitive.

### 3.2 B's "skew-product is too rigid" recurring observation

Across multiple problems, B identifies skew-product structure as
artificially preserving the dynamical features the open conjectures
ask about:

- **P1 Furstenberg:** Z/q is a "skew" of (Z/q)^×; doesn't capture
  the profinite structure.
- **P3 Palis:** the toy 3D map is a skew product; preserves index of
  periodic orbits; cannot exhibit heterodim cycles.
- **P4 Painlevé:** symmetric 2+2 ansatz is a "skew" along the
  separation axis; decouples binary-tightening from translational
  motion.

This is a **recurring methodological caveat**: clean toy models in
dynamics often have skew-product or symmetry structure that
specifically *forbids* the phenomenon being investigated. Worth
promoting to methodology_toolkit as a substrate caveat:
**"Toy models in dynamics: check for hidden symmetries that
forbid the phenomenon being probed."**

### 3.3 The "finite-N indistinguishability" observation

B's Sarnak Attack 4 finding — proven-orthogonal Sturmian decay
(6.2e-5 at N=10^6) is indistinguishable from positive-entropy random
null (7.7e-5, 9.2e-5) — generalizes far beyond Sarnak. **Any
conjecture whose true signal sits at the CLT-noise scale `N^{-1/2}`
cannot be falsified by simulation at any reachable N.** This applies
to:

- Numerical falsification of Sarnak (B's own observation).
- Numerical falsification of Riemann Hypothesis (Möbius sums up to
  finite N look indistinguishable from random; B notes this in
  passing).
- Numerical falsification of Chowla's conjecture (parallel to Sarnak).
- Any "sum of multiplicatively-modulated bounded sequence at finite
  N" question.

This deserves a one-paragraph note in the
`methodology_toolkit.md` on Pattern-21-adjacent stratification
discipline.

### 3.4 Recurring failure modes across B's batch

| failure mode | where it appears |
|---|---|
| `comp_ceiling` (algorithmic / numerical precision) | P1 (float64), P2 (CLT noise), P4 (close encounters) |
| `case_restriction` (toy too rigid / wrong attack space) | P1 (Z/q vs Z_p), P3 (skew product), P4 (symmetric ansatz) |
| `requires_unproven_conjecture` | P1 (right rigidity functional), P5 (small-divisor) |
| `Attack 3+ NOT executed (time)` | every problem |

The dominant pattern is **execution-budget compression**, not
methodological failure. Round 2 with same time budget but the
existing sketches treated as "must execute" would close most
of these gaps.

### 3.5 What B's batch contributes to cross-batch pattern catalog

- **`TWO_CLASSES_WITHIN_DOMAIN`**: dynamics has two distinct
  failure morphologies (rigidity-functional missing; sharp-bound
  missing). Worth checking other batches for analogous internal
  splits.
- **`SKEW_PRODUCT_TOY_TOO_RIGID`**: methodology caveat for any
  attack on dynamics where toy models are constructed.
- **`FINITE_N_INDISTINGUISHABILITY`**: substrate-grade kill data for
  CLT-noise-dominated falsification batteries. Generalizes beyond
  dynamics.
- **`LYAPUNOV_NOT_TANGENCY_DETECTOR`**: time-asymptotic averages
  miss codimension-1 phenomena. Specific instrument-vs-phenomenon
  caveat.

---

## 4. Concrete recommendations to James

In rough priority order:

### 4.1 Build the rigorous-numerics toolchain

Three packages would unblock most of B's "Attack 3+, NOT executed"
sketches:

- **mpmath / gmpy2 / Sage integration** for exact-arithmetic orbit
  simulation. Fixes float64 collapse for expanding maps. Standard
  Python; `pip install mpmath`.
- **CAPD or analog** for interval-arithmetic ODE/Hamiltonian
  integration. CAPD itself is C++; Python wrappers exist (e.g.
  `pychomp` for some purposes); alternative is `julia` with
  `IntervalArithmetic.jl + DifferentialEquations.jl`. Standard tool
  in rigorous-numerics dynamics; doable per-system.
- **Specialized n-body library with KS / Levi-Civita
  regularization**. ~200-500 LOC Python or use REBOUND
  (Rein-Liu 2012) which has it built-in.

ROI: every "Attack 3+, NOT executed" in B's batch becomes
executable. This is the dynamics analog of "install z3" for
combinatorics.

### 4.2 Mandate a `<batch>_summary.md` from every researcher

B's self-summary is the cleanest cross-problem residue document of
any batch. Other batches (mine included) didn't write one. Making
this standard would:
- Surface within-batch patterns at the researcher level (cheaper than
  Aporia synthesizing post-hoc).
- Force an honest "calibrated negatives" check across problems.
- Give Aporia's synthesis pass a 5×8 matrix of summary entries
  rather than 40 separate files.

Cost: ~30 min per batch. ROI: substrate-grade cross-problem
synthesis essentially for free.

### 4.3 Round-2 B batch focused on executing existing sketches

Same 5 problems; budget = 3hr/problem; explicit goal = execute the
"Attack 3+, NOT executed" sketches B already designed. Tooling
prerequisites: mpmath, CAPD or analog, REBOUND or KS-regularized
n-body, SALI/GALI.

Expected per-problem output:

| problem | attack to execute | expected outcome |
|---|---|---|
| P1 Furstenberg | mpmath orbit + Z_p Bernoulli | substrate-grade exact-arithmetic data |
| P2 Sarnak | IET BSZ-criterion test | open-territory zero-entropy data |
| P3 Palis | generic 3D Hénon + SALI/GALI + cone-field | non-skew-product calibration |
| P4 Painlevé | reproduce Xia n=5 | known-true case calibration |
| P5 KAM | SALI + Fourier-Newton + multi-system | rigorous-vs-empirical gap |

### 4.4 Cross-batch dynamics-of-failure-mode-signatures table

Combined with my prior reviews:

| problem | batch | signature | resolution requires |
|---|---|---|---|
| EFL, Frankl, Sunflower, Cap Set, Hadamard | A combinatorics | SHARP_INEQUALITY_AT_WRONG_CONSTANT | new structural input |
| Furstenberg, Sarnak, Palis | B dynamics class A | MISSING_RIGIDITY_FUNCTIONAL | new functional |
| Painlevé, KAM | B dynamics class B | MISSING_SHARP_FINITE_DIM_BOUND | computational frontier |
| SCH, Vopěnka, Whitehead, GCH-singular, Forcing | D foundations | REQUIRES_PARALLEL_OPEN_PROBLEM | unlock hub-problem |
| P vs NP, P vs PSPACE, Det-vs-Perm, UGC, qPCP | E complexity | META_OBSTRUCTION_RULES_OUT_TECHNIQUE_CLASS | techniques outside known classes |

This is the cleanest cross-batch substrate-grade table I've been
able to extract from the 4 batches reviewed so far. Aporia should
produce it for all 8 batches once they land.

### 4.5 Promote B's substrate-grade observations as primitives

Three of B's findings deserve promotion to substrate-grade primitives
in the methodology_toolkit:

- **`SKEW_PRODUCT_TOO_RIGID` caveat.** Toy models in dynamics often
  preserve symmetry that forbids the open phenomenon. Check before
  attacking.
- **`FINITE_N_INDISTINGUISHABILITY` caveat.** CLT-noise-dominated
  conjectures cannot be falsified by simulation at finite N.
- **`LYAPUNOV_NOT_TANGENCY_DETECTOR` caveat.** Time-asymptotic
  averages miss codimension-1 phenomena; geometric instruments
  (cone fields, finite-time minimum-angle) are the right detector.

Each is one-paragraph text + citation back to B's specific attack.
Cost: minutes. ROI: every future dynamical-systems-flavored work
inherits the discipline.

### 4.6 Build the dynamical-systems calibration registry

Concrete numbers across systems:

- Hénon-Heiles `E_* ≈ 0.118` (empirical chaos onset)
- Standard map `K_c ≈ 0.971...` (Greene threshold)
- Sun-Jupiter restricted 3-body `ε_*` (Celletti)
- Hill three-body `ε_*` (de la Llave)
- Spin-orbit `ε_*` (Celletti-Chierchia)
- Xia n=5 explicit ICs
- Gerver n=5 / n=4 explicit ICs
- Bonatti-Diaz blender parameters
- Etc.

Tabulate; machine-readable; reusable across attempts.

---

## 5. What this critique does NOT do

- Does **not** re-attempt any of B's 5 problems. Originals stand.
- Does **not** verify B's specific numerical results (the chaos
  score table, the float64 collapse step count, the Z/q fractions).
  I trust B's reported numbers; round 2 should re-verify if these
  are promoted to substrate-grade calibration anchors.
- Does **not** claim dynamics expertise comparable to a practicing
  dynamicist. Where I flag a "missing angle" that overlaps a
  literature B already cited but didn't pursue, the gap is between
  literature recall and execution, not between B and the discipline.
- Does **not** evaluate B's commit-and-push discipline. The
  `_scratch_B/` artifacts exist; whether they're committed to git
  is a separate hygiene question.

---

## 6. Honest read

B's batch is the **strongest computational** of the four I've
reviewed. The 5 Python scripts produced real findings — the float64
collapse, Z/q joint-orbit fraction, finite-N indistinguishability,
Lyapunov-vs-angle quasi-tangency, Hénon-Heiles E_* — that are
calibration-anchor-quality kill data. The unique `harmonia_B_summary`
file gives Aporia synthesis-ready cross-problem residue. The
two-class obstruction taxonomy is a genuine intellectual contribution
beyond literature recall.

The weakness is **time compression**. 1.5h per problem instead of
3h hit Attack 3+ depth specifically — and Attack 3+ is where the
substrate-grade computational anchors live (reproduce Xia, run BSZ
criterion on IETs, generic 3D Hénon, SALI/GALI, Fourier-Newton).
B already designed these; round 2 needs to execute them.

B is also **the same instance that shipped Pivot Move 1 earlier
the same day** (descriptor-collapse audit substrate primitive,
commit `8b15cbab`). Two productive directions in one session is
operationally strong dual-track work — the dynamics batch is
calibrated kill data; the earlier ship was substrate infrastructure.

Recommended action: **install rigorous-numerics tooling (mpmath +
CAPD-analog + REBOUND + SALI/GALI) and queue B for round 2** with
explicit goal of executing the existing Attack 3+ sketches. Most
of these are 1-3 hours apiece with the right libraries, and B
already designed them — round-2 cost is mostly engineering, not
re-thinking.

The single most valuable action would be **mandating a self-summary
across all 8 batches**. B's was unique and substrate-grade; making
it standard converts batch outputs from 5 separate files to "5 files
+ 1 synthesis," which is what Aporia's post-batch pass needs and
which essentially every batch already implicitly produced
internally without writing down.

— Reviewed by Harmonia E (sessionE), 2026-05-05.
