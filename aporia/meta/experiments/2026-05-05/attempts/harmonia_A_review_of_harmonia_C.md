# Cross-Batch Review — Harmonia A on Harmonia C

**Reviewer:** Harmonia A (Harmonia_M2_sessionA)
**Date:** 2026-05-05
**Batch reviewed:** Harmonia C — Analysis / PDEs (P1 Navier-Stokes, P2 Yang-Mills, P3 Kakeya, P4 Restriction, P5 Bochner-Riesz)
**Files reviewed:**
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_C_00_summary.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_C_01_navier_stokes.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_C_02_yang_mills_mass_gap.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_C_03_kakeya.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_C_04_restriction.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_C_05_bochner_riesz.md`
- support scripts at `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\_p{1..5}_*_experiment.py`

---

## 0. Top-line verdict

**The batch is well-disciplined and substrate-honest.** No invented citations,
no fake partial results, one explicit reward-signal-capture catch (P5's
Fefferman miss), and a clean cross-problem synthesis (the
"marginal-vs-supercritical" theme). The two methodology-toolkit candidates
("adversarial-test-function-before-novelty-claim" and
"adjacent-easier-version-as-calibration-anchor") are sound and worth
promoting if a second batch confirms them.

**The batch is also notably under-ambitious relative to its budget.**
Wall-clock was 6 of 15 budgeted hours — 9 unused — and every one of the
five attempts followed an identical narrow recipe: survey, locate
obstruction (in textbook terms), one calibration trace on the
already-solved adjacent case, stop. None of the five pushed into the
open regime even at calibration scale. The recipe converged so cleanly
that one suspects it was *too* template-friendly: the template let
Harmonia C produce uniform, defensible output without ever bumping
against the hard part of any of the five problems.

**Falsification-first read on the batch's own claims.**
- "Obstruction localized" — true, but the obstructions stated are
  textbook obstructions, not findings. The verb to use is *recapitulated*,
  not *located*.
- "Calibration anchor produced" — true in the narrow toolchain-check
  sense; not true as anchors of the conjecture's open regime.
- "Substrate-grade kill data" — partially. The kill data is the
  *attempt-shape* itself plus the P5 catch. The numerical traces are
  textbook reproductions, useful as regression baselines but not as
  novel kill data.

This review is friendly. Round 2 absorbs the 9 unused hours productively
and addresses what the round-1 recipe missed.

---

## 1. Per-problem critique and round-2 proposals

### P1 — Navier-Stokes (3D regularity)

**Critique of round 1.**
- 2D NS pseudospectral run is a textbook exercise. The BKM integral is
  trivially controllable in 2D (vorticity is scalar transported with
  diffusion; no stretching). The calibration buys little.
- §3's obstruction localization is correct but boilerplate — it
  reproduces the standard supercritical-scaling story. No structural
  observation from the run feeds back into the obstruction text.
- §5 lists three "would push if I had time" items. Two of them
  (3D Taylor-Green at $128^3$, axisymmetric Hou-Luo small-scale) are
  feasible *within the budget* — $128^3$ pseudospectral NS for a few
  thousand steps fits in tens of minutes on a reasonable machine. C
  declined these despite under-budget on time.

**Round-2 proposal — feasible.**

1. **3D Taylor-Green vortex at $64^3$ or $128^3$**, 2000 timesteps,
   track $\|\omega\|_\infty$, BKM integral, energy spectrum slope, and
   palinstrophy. Even underresolved, the *qualitative* enstrophy peak
   around $t \approx 9$ (the well-known TG benchmark) is a useful
   anchor: does my numerical scheme reproduce it? The data is
   textbook for fluid simulation but C did not produce any, so it has
   to count as new substrate calibration.
2. **Implement the "averaging dial".** Perturb the bilinear advection
   $u \cdot \nabla u$ along a 1-parameter family $(1-\theta) (u \cdot
   \nabla u) + \theta \, \mathrm{Avg}(u, u)$ where $\mathrm{Avg}$ is a
   simplified Tao-style averaged operator. At each $\theta \in
   \{0.0, 0.25, 0.5, 0.75, 1.0\}$ run TG to time $T$, measure peak
   enstrophy growth rate. Look for the threshold $\theta^*$ at which
   the simulation first appears unstable / blows up numerically.
   This is genuinely novel (I'm not aware of anyone publishing such
   a numerical interpolation between real NS and Tao's averaged NS).
   Useful as a *qualitative probe* of which cancellation in real NS
   is doing the work — even if the answer is "no clean threshold,"
   that's substrate-grade.
3. **Axisymmetric Hou-Luo reproduction at small scale.** A $256^2$
   axisymmetric (r, z) grid with swirl is feasible in minutes and
   reproduces the basic geometry. Question: does my numerical run
   show the candidate self-similar profile that Hou-Luo's higher-res
   runs show? Cross-check by computing residual to $1/(T-t)$ scaling.
4. **Critical-norm tracking.** Beyond BKM: track $\|u(t, \cdot)\|_{L^3}$
   directly across the simulation. If the run is well-resolved and
   $L^3$ stays bounded, ESS-2003 says smoothness persists — a
   *direct* probe of the regularity criterion that BKM does not
   provide on its own.

**Round-2 verdict candidate:** PARTIAL_RESULT (numerical anchors at
3D scale; no theorem moved; "averaging-dial" experiment is novel).

**Effort estimate:** 5–7 hours including code + runs + writeup.

---

### P2 — Yang-Mills mass gap (4D)

**Critique of round 1.**
- 2D U(1) Metropolis matching the analytic $I_1(\beta)/I_0(\beta)$ to
  ~1% is a textbook lattice-gauge sanity check. The fact that it
  works is unsurprising; it would be more informative if it *didn't*.
- 4D $SU(2)$ at small lattice $L \in \{4, 6, 8\}$ is a few minutes of
  Metropolis per coupling. C did not attempt this despite §5
  flagging it as "almost certainly null." Yes, but the null result
  is itself a calibration that the lattice toolchain extends to
  non-abelian.
- The interesting idea — Balaban block-spin RG flow as a coordinate
  system — is dismissed as "multi-month work" but is not *all*
  multi-month work: even a 2-step block-spin on a small lattice with
  numerical effective-coupling extraction is a session-scale task.
- Gribov ambiguity discussion is correct but no attempt is made to
  *visualize* the Gribov region on a small lattice, despite §5 flagging
  this as concrete and tractable.

**Round-2 proposal — feasible.**

1. **Lattice $SU(2)$ in 4D at $L = 6, 8$**. Wilson plaquette action,
   heatbath or Metropolis, $\beta \in \{2.0, 2.3, 2.5\}$. Measure
   plaquette, Wilson loops $W(R, T)$ for $R, T \in \{1, 2, 3\}$,
   extract string tension. Compare to known continuum extrapolation.
   Even at $L = 8$ this is minutes per coupling.
2. **Glueball correlator on the same lattice.** Polyakov loop or
   plaquette-plaquette spatial correlator at large separation;
   exponential decay rate is the lightest scalar glueball mass. With
   reasonable statistics this is the *direct* observable for the
   mass gap.
3. **2-step block-spin RG numerically.** Define a block average that
   maps $L = 8$ links to $L = 4$ "effective" links. Run heatbath at
   $L = 8$, measure plaquette and Wilson loops, then on the
   block-averaged ensemble. Does the effective $\beta$ of the
   block-averaged ensemble track Balaban's prediction? This is
   "coordinate-system invention" applied to RG flow — a small
   anchor case for a methodology-toolkit candidate.
4. **Visualize Gribov region** on a low-volume lattice ($L = 4$) by
   sweeping gauge transformations and plotting the Faddeev-Popov
   determinant zero locus.
5. **Cross-dimensional confinement scaling.** Run lattice $SU(2)$ at
   the *same* $\beta$ in 2D, 3D, 4D, observe how Wilson area-law
   decay rate scales. Substantively: how much does the dimension
   matter for the confinement signal at fixed coupling?

**Round-2 verdict candidate:** PARTIAL_RESULT (4D non-abelian
calibration anchor, glueball mass measurement on small lattice, RG
flow sketch).

**Effort estimate:** 7–10 hours with reasonable optimization. Could
absorb most of the 9 unused round-1 hours.

---

### P3 — Kakeya conjecture

**Critique of round 1.**
- 2D box-counting "dimension" of 1.76 on a finite grid is *not*
  approaching the Hausdorff dimension 2 — the report acknowledges
  this but presents the table anyway. The data is uninformative
  except as a regression baseline.
- The 3D incidence-multiplicity statistics (50–400 tubes) are
  reproducible numbers but **never compared to Wolff's predicted
  bound**. Wolff's hairbrush argument predicts a specific scaling
  of multiplicity vs $K$ and $\delta$; C's report tabulates numbers
  but doesn't compute the Wolff bound's predicted value next to
  them. Without that comparison, the statistics are not
  calibrating anything.
- §5's "stickly / plainly / grainy" detector is the most generative
  idea in the report — it would operationalize Katz-Tao's structural
  trichotomy on finite ensembles. Not even sketched.
- Citation to Wang-Zahl 2022 is "invoked-from-prompt, not
  re-fetched." The *technical* state-of-art is at exactly that paper;
  not engaging with it means the obstruction-localization is at the
  Wolff-1995 level, not the 2022 frontier.

**Round-2 proposal — feasible.**

1. **Compute Wolff's hairbrush bound on the existing 3D ensemble.**
   For each tube $T$, count tubes within distance $\delta$ of $T$ —
   the "bush" of $T$. Wolff's bound predicts $|bush(T)| \lesssim$
   (something explicit depending on $K$, $\delta$, $n$). Plot
   empirical vs predicted across the existing $K \in \{50, 100, 200,
   400\}$ runs. If the empirical multiplicity hits the Wolff bound,
   the bound is tight on random ensembles; if not, the gap is the
   substrate's signal.
2. **Implement the planar-vs-grainy detector.** For each tube, look
   at the directions of all tubes meeting it within $\delta$ — do
   they cluster in a plane (planiness) or scatter (graininess)?
   Compute a planiness score per tube, plot the histogram. Random
   ensembles should look uniform; *near-extremal* Besicovitch sets
   should look bimodal.
3. **Compare random tube ensembles to Heisenberg-style algebraic
   constructions.** Replace the random tube directions with directions
   on an arithmetic-progression structure (e.g., directions
   $(1, k/N, k^2/N^2)$ for $k = 0, ..., K-1$ — the moment curve).
   Expectation: the algebraic construction will exhibit *worse*
   multiplicity (higher pile-up) than random. If the empirical
   numbers confirm, this is one anchor for "algebraic constructions
   are extremal-pessimistic for Kakeya."
4. **Decoupling-style $\ell^2$ inequality.** For the paraboloid (since
   that's the easier dual), sample a function on the paraboloid,
   decompose into $\delta$-caps, verify Bourgain-Demeter's
   $\ell^2$-decoupling on the test function. Provides a numerical
   anchor for decoupling — the technical thread underlying P4 and P5
   too.

**Round-2 verdict candidate:** PARTIAL_RESULT (Wolff bound calibrated
against empirical ensemble; decoupling anchor; planar/grainy detector
shipped or honestly reported as failed).

**Effort estimate:** 5–6 hours.

---

### P4 — Restriction conjecture

**Critique of round 1.**
- The Stein-Tomas calibration on indicator caps (n=2 at $L^2 \to L^6$,
  n=3 at $L^2 \to L^4$) is correct and clean. But the **conjecture
  is at the $L^q \to L^q$ endpoint past Stein-Tomas**, and indicator
  caps are *not* the adversarial test functions there.
- §4 *acknowledges* that the data does not probe the open regime, then
  presents the table anyway. The table is a textbook reproduction of
  Stein-Tomas's $L^2$-bound, not a probe.
- §5 lists Knapp-example sweep, bilinear, and decoupling — each of
  which is implementable in a session. None attempted.
- The same hazy citations as P3 (Hickman-Rogers 2019, Guth 2016) —
  again at the technical frontier.

**Round-2 proposal — feasible and specific.**

1. **Knapp-block test functions.** A Knapp block at scale $\delta$ on
   $S^{n-1}$ is a test function $g_\delta$ supported on a cap of polar
   angle $\delta$ with constant amplitude. The extension $E(g_\delta)$
   is concentrated on a $\delta^{-1} \times \delta^{-2}$ tube tangent
   to the sphere at the cap's center. Implement, sweep $\delta \to 0$,
   measure $\|E(g_\delta)\|_{L^q} / \|g_\delta\|_{L^p}$ along the
   conjectured boundary line $1/p + (n+1)/((n-1)q) = 1$. If the ratio
   stays bounded as $\delta \to 0$, that's numerical evidence
   *consistent* with the conjecture; if it diverges, that's evidence
   *against* (and a counter-example candidate).
2. **Bilinear extension.** Implement Tao-Vargas-Vega bilinear estimate
   on two angularly-separated caps in $S^2$: extract the bilinear
   constant, compare to the linear bound at the same exponents. The
   bilinear should be strictly better; quantify the gap.
3. **Decoupling on the paraboloid.** Bourgain-Demeter's
   $\ell^2$-decoupling for the paraboloid is the (proven) technical
   tool that Hickman-Rogers and Wang chain to. Verify the decoupling
   inequality numerically on a Schwartz test function: decompose
   $\widehat{g}$ on the paraboloid into $\delta$-caps, sum
   $\ell^2$-norms across caps, compare to the global $L^p$ norm.
4. **Regression baseline for future Restriction-batch work.** The
   indicator-cap calibration in C's round 1 is a *baseline*; future
   attempts should compare new test functions to this baseline to
   show the new test functions are actually adversarial.

**Round-2 verdict candidate:** PARTIAL_RESULT (Knapp sweep across
small $\delta$; bilinear vs linear gap quantified; decoupling
anchor).

**Effort estimate:** 4–6 hours.

---

### P5 — Bochner-Riesz conjecture

**Critique of round 1.**
- The reward-signal-capture catch (Gaussian doesn't expose Fefferman
  1971's $\delta=0$ counterexample) is the **single most valuable
  output of the entire batch**. It is exactly the substrate-grade
  signal the experiment was supposed to produce.
- That said, the table at §4 is *actively misleading* as data even
  with the caveat. The clean choice is to flag the table as
  *uninformative* and replace it. Round 2 must do that.
- §5's three items (Knapp blocks, square function, n=3 boundary
  probe) are the right list. None attempted.

**Round-2 proposal — exactly what §5 said.**

1. **Knapp block sweep, replacing the Gaussian.** Build Knapp blocks
   at a sequence of frequency-localization scales $\delta'$. For each,
   compute $\|T^\delta f\|_{L^p} / \|f\|_{L^p}$ across $\delta \in
   \{0, 0.1, 0.25, 0.5, 1.0\}$ and $p \in \{2, 3, 4, 6\}$. The
   Fefferman counterexample at $\delta = 0$ should appear as a
   ratio that **diverges with grid refinement** — verify this
   explicitly as the calibration-against-counterexample.
2. **Carleson-Sjölin square-function decomposition in n=2.**
   Hand-cranked but mechanical: decompose $\widehat{f}$ into annular
   pieces near the unit circle, apply the square-function bound on
   each, sum. Reproduce the proved $n=2$ Bochner-Riesz bound as a
   *numerical* witness of the technique's mechanism.
3. **n=3 boundary-line probe at multiple resolutions.** With Knapp
   blocks in hand, sweep $(p, \delta)$ along the conjectured
   boundary in $n=3$ at grids $48^3 \to 64^3 \to 96^3$. Track
   whether the ratio is plateauing (consistent with conjecture) or
   growing (potential counter-example pressure).

**Round-2 verdict candidate:** PARTIAL_RESULT (Fefferman counterexample
explicitly witnessed; n=2 bound numerically reproduced via square
function; n=3 boundary probe reported with multi-resolution).

**Effort estimate:** 5–7 hours.

---

## 2. Cross-cutting infrastructure proposals

These are *shared* primitives that, if built once, would lower the
marginal cost of every future Harmonia C-style batch.

### Tool 1 — Fourier-extension / multiplier numerical lab

A reusable Python module at, say, `harmonia/runners/fourier_lab.py`
exposing:

- `extend(g, sphere, n)` — extension operator $E(g)$ on $S^{n-1}$.
- `multiplier(f, m, n)` — Fourier multiplier with custom $m(\xi)$.
- `knapp_block(delta, prime_dir, n)` — canonical Knapp block at
  scale $\delta$ tangent to $S^{n-1}$.
- `bilinear_ext(g1, g2, ...)` — Tao-Vargas-Vega bilinear.
- `decoupling_l2(f, paraboloid, delta, p)` — Bourgain-Demeter
  decoupling sum.

Used by P3 (Kakeya via Restriction-Kakeya equivalence), P4
(Restriction directly), P5 (Bochner-Riesz multiplier). Builds *one*
adversarial test-function library and uses it across all three.
This is the direct response to the "adversarial-test-function-before-
novelty-claim" methodology candidate — promote the *pattern* to a
substrate primitive only after the *toolkit* exists.

### Tool 2 — Coarse-grid 3D NS regression suite

A small module at `harmonia/runners/ns_3d_regression.py` exposing:

- `taylor_green(N, T, nu)` — TG vortex at given resolution and time.
- `bkm_integral(omega_history)`.
- `energy_spectrum(u_hat)`.
- `axisymmetric_huo_luo(N, T)` — small-scale axisymmetric setup.

Output: a fixed-format CSV per run. Used as regression baseline for
any future NS-batch work. The first run of round-2 produces the
baseline; subsequent batches compare deltas.

### Tool 3 — Lattice gauge sandbox

A module at `harmonia/runners/lattice_gauge.py`:

- Generic Wilson lattice for $U(1), SU(2), SU(3)$ in dimensions
  $2, 3, 4$.
- Heatbath + over-relaxation for $SU(N)$.
- Wilson loop, Polyakov, plaquette correlator, glueball-channel
  operators.
- Block-spin RG step for the "Balaban-as-coordinate" experiment.

Used by P2 directly. Used in cross-batch context (any QFT-flavored
problem in future Harmonia C-style batches).

### Tool 4 — Tube-incidence + planiness/graininess detector

A module at `harmonia/runners/incidence_lab.py`:

- `tube_ensemble(K, n, delta, mode='random'|'arithmetic'|'algebraic')`.
- `multiplicity_distribution(ensemble, grid)`.
- `wolff_hairbrush_bound(K, n, delta)` — predicted bound.
- `planiness_score(tube, ensemble, delta)` — Katz-Tao-style detector.

Used by P3 directly. Provides the bridge between "we observe
multiplicity statistics" and "we know what the Wolff bound predicts"
that round-1 P3 lacked.

### Tool 5 — Knapp-block / counter-example library

A documented library of canonical *adversarial* test functions for
harmonic-analysis operators, each annotated with:

- which counterexample / extremality it witnesses,
- the canonical citation (Fefferman 1971, Knapp examples, Stein
  thesis 1958, etc.),
- the parameter range where it saturates.

Direct response to the "adversarial test function" methodology
candidate. The pattern *can* be promoted to a substrate primitive
once the *library exists*; round 1 surfaced the need but produced
zero canonical test functions.

### Tool 6 — Decoupling primitives

Bourgain-Demeter $\ell^2$-decoupling for the paraboloid, sphere, and
moment curve, as a reusable primitive. Used by P3, P4, P5; also by
any future analysis batch. Decoupling is the technical thread that
Hickman-Rogers, Wang, Guth-Maldague all chain to; building it once
unblocks everything downstream.

### Dataset 1 — Reference benchmarks per problem

For each of the 5 problems, build a *reference benchmark* dataset
documented in the repo:

- P1: 5 canonical 3D NS initial conditions (TG, Beltrami, decaying
  isotropic, Kerr-Lukacs, Hou-Luo axisymmetric) with reference
  coarse-grid runs.
- P2: 5 lattice gauge configurations $(G, n_{\rm dim}, \beta)$ with
  reference observable values.
- P3: 5 tube ensembles (random, arithmetic, algebraic, Heisenberg,
  Besicovitch-construction) with reference incidence statistics.
- P4: 5 test-function families (indicator-cap, Knapp, Schwartz,
  bilinear-paired, paraboloid-Schwartz) with reference extension
  operator values.
- P5: 5 multiplier × test-function pairs spanning the
  $(\delta, p)$ region, with reference ratios.

Future Harmonia C-style batches compare against these benchmarks;
deltas surface anomalies.

---

## 3. Additional solution angles

These are *frame shifts* — alternative coordinate systems for the
same conjectures. Each is speculative; none is a path to closure;
each is a candidate axis worth probing in a "novelty budget"
fraction of round 2.

### P1 — RG flow on the regularity hierarchy
Treat NS as a flow on the lattice of $L^p_t L^q_x$ spaces, indexed by
the scaling dimension. The supercritical-vs-critical-vs-subcritical
distinction *is* an RG flow on this lattice. Question: is there a
fixed point on this lattice (not in physical space, but in the
*norm space*) at which NS "almost terminates" and which structural
property of the bilinear operator pulls the flow back to
subcritical? This is closer to physics-style RG than analytic-
PDE-style technique; the angle is whether the *scaling lattice itself*
admits a coordinate description that the conventional analytic
attack misses.

### P2 — Borel summability / resurgence
The gap between perturbative QFT (formal series in $g$) and
non-perturbative existence is, in 2D and 3D models, addressed by
Borel summability of the perturbative expansion. In 4D YM the
perturbation series has the wrong renormalons to be Borel-summable
in the classical sense — but resurgent transseries (Écalle-style)
might. Angle: is there a session-scale numerical probe of resurgent
structure on small lattices? Speculative but the literature has
moved on this in the last 5 years.

### P3 — Information-theoretic / max-entropy formulation of Kakeya
Restate the Kakeya conjecture as: among all measure-supported sets
in $[0,1]^n$ that contain a unit segment in every direction,
maximize entropy / minimize covering. Is the conjecture equivalent
to a max-entropy variational principle? If so, numerical descent
(gradient flow on the indicator function) might find near-extremal
configurations explicitly. Speculative; could fail because the
Hausdorff vs Minkowski distinction breaks the variational frame.

### P4 — LP / convex relaxation
Many incidence-style conjectures admit linear-programming
formulations whose LP duals give bounds. Restriction has such a
dual (Holder duality with $T^* T$ restricted to caps). Numerical LP
solvers can probe the LP-bound on small finite configurations.
Speculative; the LP version is presumably weaker than the
conjecture but the *gap* between LP and conjecture is an
interesting axis.

### P5 — Spectral / matrix-multiplier viewpoint
The Bochner-Riesz multiplier is a Fourier multiplier; on a finite
grid it is a matrix. The matrix's *singular value distribution*
encodes its $L^p \to L^p$ norm via interpolation. Spectral
properties of finite-grid Bochner-Riesz multipliers (eigenvalue
clustering, condition number scaling with grid size) might surface
the conjectured $L^p$ boundedness as a spectral pinch. Speculative;
the relationship between matrix singular values and the operator
$L^p$ norm is delicate.

---

## 4. Recommended round-2 sequencing

If round 2 is greenlit with the same ~15h budget per researcher
spread across the 5 problems, my proposed sequencing is:

1. **Build Tool 1 (Fourier-extension lab) first**, as a 2-hour
   investment. It unblocks P3, P4, P5 simultaneously.
2. **Build Tool 5 (Knapp-block library) inside Tool 1**, ~1 hour.
   Round 1 showed the absence of this is the binding constraint on
   P5 honesty (and probably P4).
3. **P5 round 2 first**, ~3 hours. The Fefferman miss is the most
   acute round-1 issue and is fixable. Establishes pattern: Knapp
   blocks witness counterexamples, calibration becomes proper.
4. **P4 round 2**, ~3 hours. Reuses the same lab + Knapp blocks.
   Outputs: Knapp sweep across $\delta$, bilinear-vs-linear gap,
   decoupling anchor.
5. **P3 round 2**, ~3 hours. Uses Tool 4 (incidence lab); compares
   empirical multiplicity to Wolff bound; ships the planiness
   detector.
6. **P1 round 2**, ~4 hours. Build Tool 2; run TG at $128^3$;
   implement averaging dial; track $\|u\|_{L^3}$.
7. **P2 round 2**, ~4 hours. Build Tool 3; run $L=8$ $SU(2)$ at
   three couplings; extract glueball mass; sketch RG flow.

Total: ~20 hours, somewhat past the 15h budget. If 15h is hard,
drop P1 or P2 round 2 (they are textbook reproductions; P3-P5 round 2
delivers more substrate signal).

**Compounding return.** Tools 1, 2, 3, 4 all live in
`harmonia/runners/` and are reusable across future Harmonia C / B / E
batches. Round 2's marginal cost is high; round 3+ marginal cost is
low because the infrastructure is in place. This is the
"getting-faster-at-getting-better" frame from the operating
disposition.

---

## 5. Methodology-toolkit candidates: discipline check

Harmonia C proposed two candidates for promotion:

**Candidate A — "Adversarial test function before novelty claim."**
Anchor: P5 Fefferman miss. Solid concept. Round-1 has *one* anchor.
Pattern-library discipline (per `harmonia/memory/pattern_library.md`)
requires multiple anchors before promotion to a working theory.
Round 2's Knapp-block library is the *operationalization* of the
pattern; if round 2 surfaces a *second* concrete miss-and-catch
under non-Knapp test functions in P3 or P4, the pattern would have
its second anchor. **Recommend: hold as candidate, do not promote
until a second anchor surfaces.**

**Candidate B — "Adjacent-easier-version as calibration anchor."**
Anchor: all 5 round-1 problems. This is a *batch-level pattern*
rather than a per-problem pattern, which weakens the anchor count
(it's "5 instances of one batch's recipe converging," not "5
independent observations of the pattern"). It's also nearly tautological
— if you're attacking an open problem, calibrating on the closest
proved sub-case is the obvious first move, taught in any methods
course. **Recommend: this is more an operating discipline note
than a promotable pattern. Add to operating-disposition guidance,
not to the pattern library.**

---

## 6. What I might be wrong about

This review is itself an attack-data artifact and should be subject to
the same falsification-first standard.

- **The "under-ambitious" framing might be unfair.** Round 1 was 6h
  spread across 5 problems = 70 min/problem. The discipline of
  "stop when you've done one calibration trace + one obstruction
  localization" is exactly what produces clean, comparable, low-
  variance output across the batch. Pushing into the open regime in
  round 1 might have produced messier, less-comparable artifacts.
  The recipe's narrowness is a *feature* of round-1 pacing, not a
  bug. My critique is sharper if round 1 is read as the pilot and
  round 2 is where ambition is appropriate — which it is.
- **The infrastructure proposals might be overweight.** Six tools,
  five datasets — that's a lot. A leaner round 2 might build only
  Tools 1 and 5 (Fourier lab + Knapp library) and accept that P1, P2,
  P3 round 2 work happens at session-scale ad-hoc rather than via
  shared modules.
- **The "RG flow" angle for P1 and "resurgence" angle for P2 are
  speculative.** I am floating them as axis candidates, not as
  recommended attacks. Probability of substrate yield from either:
  honestly under 10%. Their value is as breadth probes, not depth.
- **My claim that Wang-Zahl 2022, Hickman-Rogers 2019, Bourgain-Guth
  2011 are "the technical frontier"** is from training-data
  recall and was not re-fetched. If those papers have been
  superseded by 2026, my framing is dated.

---

## 7. Closing read

Harmonia C produced a clean, defensible, under-budget batch with one
load-bearing substrate-grade catch (P5 Fefferman) and two methodology
candidates worth holding for second-anchor confirmation. The unused
9-hour budget is the largest tractable round-2 investment in the
batch. The proposed round-2 plan absorbs that budget into shared
infrastructure (Fourier lab, lattice gauge sandbox, incidence
lab, Knapp library, regression baselines) that compounds across
future analysis-flavored batches.

If Aporia / Techne is making substrate decisions on the basis of
these 5 attempts: the kill data is real but limited. Round 1 mostly
calibrated the *attempt-shape*. Round 2 calibrates the *open
regime*, which is where the substrate's bet actually lives.

— Harmonia A (Harmonia_M2_sessionA), 2026-05-05
