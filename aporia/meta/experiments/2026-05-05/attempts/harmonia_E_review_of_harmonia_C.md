# Review and Critique — Harmonia C's Analysis / PDEs Batch

**Reviewer:** Harmonia E (Harmonia_M2_sessionE)
**Reviewed batch:** Harmonia C — Analysis / PDEs
  (`harmonia_C_{00..05}_*.md` in this directory)
**Date:** 2026-05-05
**Verdict:** The cleanest methodological batch I've reviewed.
Numbered `_00_summary.md` (more disciplined than B's separate
`_summary.md`), 5 Python experiments, **and** the canonical
substrate-grade reward-signal-capture catch (P5 Bochner-Riesz
Gaussian-vs-Fefferman-counterexample) of the entire 8-batch round.
Round-2 ROI is concrete and high — Knapp-block test functions are
universally missing across P4 and P5; coordinate-system invention
across the P3–P5 implication triangle was explicitly not attempted.

---

## 0. Scope of this review

James asked the same four questions as for A, D, B:

1. What additional research could further each of the 5 solutions?
2. Could a round 2 be done for any of them?
3. Are there additional solution angles available?
4. Are there additional datasets or compute tools we could build?

This is review, not re-attempt. I'm a complexity-batch peer reviewer
and have no claim to harmonic-analysis / PDE expertise — where I
flag a "missing angle," it may reflect a genuine gap or my
unfamiliarity with what's discipline-standard. C engaged with
harmonic-analysis literature substantively; I'm reading at the
peer-review level, not the expert-review level.

---

## 1. Executive summary

**What Harmonia C did well:**

- **Numbered summary file (`harmonia_C_00_summary.md`).** C is the
  only researcher who put the summary at index 00 — explicitly the
  synthesis-index position. B's was a separate suffixed file; mine
  and A's and D's didn't exist. C's index-00 placement signals
  "read this first" and is materially better organization for
  Aporia's downstream synthesis pass.

- **The canonical reward-signal-capture catch.** P5 (Bochner-Riesz)
  Gaussian sweep produced `‖T^0 f‖/‖f‖ = 1.0000` exactly across all
  `p` in `n = 2, 3`. A naïve read says "BR is bounded for all δ ≥ 0
  and all p," which **contradicts Fefferman 1971 (the ball
  multiplier is unbounded for δ = 0, p ≠ 2)**. C caught this
  mid-execution, diagnosed it correctly (Gaussian's frequency
  support doesn't intersect the multiplier's transition region),
  flagged the metadata field `reward_signal_capture_check: partial
  pass`, and identified Knapp blocks as the required adversarial
  test class. **This is the discipline working as designed.** It
  is the cleanest single example of substrate-grade self-correction
  in the entire 8-batch round; for a "test data is what we're
  after" framing, this is the platonic ideal.

- **Two methodology-toolkit primitives proposed explicitly.** C's
  summary §5 surfaces two substrate-grade candidates:
  1. **`ADVERSARIAL_TEST_FUNCTION_BEFORE_NOVELTY_CLAIM`** —
     generalizes the P5 catch. Before claiming a numerical bound is
     consistent with a theorem, verify the test function actually
     exercises the regime where the theorem could fail. Smooth
     Schwartz functions miss known counterexamples on Knapp slabs,
     thin caps, sharp cutoffs.
  2. **`ADJACENT_EASIER_VERSION_AS_CALIBRATION_ANCHOR`** — for any
     open conjecture, the lower-dim / abelian / Euclidean / smooth
     analog where the result IS known is the calibration target.
     Run the tool on the analog, verify the known answer, document
     the gap.
  Both are concretely anchored across the 5 attempts. **Both should
  be promoted to `harmonia/memory/methodology_toolkit.md`.**

- **Strong implication-triangle framing for P3–P5.** C identifies
  `Kakeya ⇒ Restriction ⇒ Bochner-Riesz` as the structural backbone
  and shows how all three reduce to "incidence geometry of tubes /
  caps / multipliers near a (n-1)-dimensional manifold (sphere or
  cone) in `R^n`." This framing is correct, well-known in
  harmonic analysis, and **exactly the right cross-problem
  observation for Aporia's synthesis**.

- **Quantitative substrate-grade calibration anchors across all 5.**

  | problem | calibration anchor produced |
  |---|---|
  | P1 NS | 2D BKM-integral trace clean (energy 0.114%, enstrophy 0.475% drift, BKM ~ 0.97/sec) |
  | P2 YM | 2D U(1) Wilson lattice matches I_1/I_0 to ~1% on 16² @ β=2 |
  | P3 Kakeya | 2D box-counting + 3D incidence-multiplicity stats reproducible |
  | P4 Restriction | Tomas-Stein ratio bounded `< 5` in n=3 across cap-size factor 16 |
  | P5 BR | T^δ ratio sweep reproducible to 4 digits across (δ, p) |

  Every problem produced a reproducible calibration trace. Every
  one was clean in the expected regime.

- **Operating-disposition vocabulary used correctly.** C uses
  "reward-signal-capture check," "novelty-budget work," and
  "candidate primitive for methodology toolkit" — these are
  Prometheus-internal terms from `restore_protocol.md` and
  `MEMORY.md`. Either C had the substrate disposition fully
  internalized at session-open, or C is more rigorous about citing
  internal terminology than other instances. Either way, the
  signal is good.

- **Honest under-budget time discipline.** ~70 min/problem (not
  1.5h like B; 70 min is shorter), totaling ~6 hours wall-clock
  on a 15-hour budget. Acknowledged in summary §4. Time was used
  on calibration + obstruction localization + reward-signal-capture
  check; deeper attacks were sketched but not run.

**What's weakest:**

- **Knapp blocks are universally missing across P4 and P5.** C
  explicitly identifies this in P5 as the required adversarial test
  class and in P4 as the path past Stein-Tomas. Knapp construction
  is mechanically known (~1-2 hours of careful coding). **The
  single highest-ROI follow-up is "implement Knapp blocks once,
  reuse across P4 and P5."**

- **Coordinate-system invention across P3–P5 not attempted.** C
  explicitly says in §6: *"Did not attempt cross-problem
  coordinate-system invention."* But the implication triangle
  `Kakeya ⇒ Restriction ⇒ Bochner-Riesz` is exactly the kind of
  scaffold where a single coordinate system (tubes / caps /
  multipliers near a sphere in R^n) could unify the three calibration
  spaces. C identified this as out-of-scope; **it's the
  highest-leverage missing experiment** in the entire batch
  (and aligned with Prometheus's coordinate-systems-of-legibility
  charter, see `user_prometheus_north_star.md`).

- **NS at N=64² and 2D only.** Hou-Luo work runs at ~10^9 mesh
  points; C's calibration is at 4096 grid cells. Even 3D
  pseudospectral at N=128³ Taylor-Green vortex on a workstation
  is feasible in hours and would have given a substrate-grade
  3D-NS calibration anchor.

- **Yang-Mills is 2D U(1) only.** Honest calibration but 4D
  non-abelian is a different beast. Even small SU(2) at L=8 in 3D
  would have been informative — C sketched the higher-dim sweep
  as Attack 1 of "where I would push" but didn't run.

- **Decoupling not simulated.** Bourgain-Demeter 2015 `ℓ²`-decoupling
  is the modern unifying tool for P3–P5; C mentions it in
  literature scans but doesn't run any decoupling-style numerical
  experiment.

- **No bilinear / multilinear extension experiment for P4.** The
  Tao-Vargas-Vega bilinear estimate is the canonical path past
  Stein-Tomas; C sketched as "where I would push" but didn't run.

**Headline recommendation:** A round-2 batch with **Knapp blocks
implemented once, then reused across P4 and P5**, plus **3D NS at
N=128³** and **2D non-abelian SU(2) + 3D U(1) lattice**, plus
**a unifying coordinate system attempt across P3–P5**. C's existing
calibration anchors mean round-2 cost is mostly engineering, not
re-thinking. Both methodology-toolkit primitives C proposed should
be promoted immediately as substrate primitives — they're already
anchored across 5 attempts.

---

## 2. Per-problem critique

### 2.1 Problem 1 — Navier-Stokes 3D Regularity (`harmonia_C_01`)

**Verdict given:** OPEN (no progress; obstruction localized;
2D calibration clean).

**My read of the work:**

✓ **Operational form clean.** Statement, scaling analysis
(supercritical L², critical L³), and Tao-2016-averaged-vs-real-NS
distinction (vortex stretching cancellation) are correct and
substrate-grade.

✓ **2D BKM integral as calibration anchor.** Correct choice — 2D
NS has no vortex stretching and is the regime where BKM is
trivial. Energy decay 2.5%, enstrophy 4.7%, BKM integral grows
linearly at ~0.97/sec. Calibration confirms the criterion is
quantitatively computable.

✓ **Localization of obstruction at "supercritical-energy + no
stretching bound."** Exactly right. The supercriticality of `L²`
control vs the criticality of `L³` is the textbook gap.

✗ **3D not attempted.** C is honest about compute budget. But
N=128³ Taylor-Green vortex is feasible in 1-3 hours on a
workstation — **the highest-leverage single experiment** for any
NS attack. It's the canonical computational anchor for what
3D NS does.

✗ **Hou-Luo geometry not reproduced even at small scale.**
Axisymmetric Euler with boundary on a small cylinder + adaptive
refinement is feasible at scale-down. C lists this as Attack #2
of "where I would push" but didn't run.

✗ **Tao's averaged-NS not simulated.** The construction has
explicit form; reproducing Tao's blowup mechanism on the averaged
equation in 1D would be a clean substrate trace.

✗ **No Constantin-Iyer / vortex stretching diagnostic.** Lagrangian
markers for vortex stretching tracking; standard PDE diagnostic.

**Round 2 plan (~3hr):**
- 3D pseudospectral NS at N=128³, Taylor-Green vortex,
  ν=10⁻³, t∈[0, 10] (~2hr). Track ‖ω‖_∞, BKM integral,
  enstrophy. Compare to Brachet-Meiron-Orszag literature values.
- Tao-averaged-NS in 1D reproduction (~30 min). Verify the
  cascade of "logic gate" components.
- Hou-Luo axisymmetric Euler at small scale (~30 min sketch;
  full reproduction is multi-day).

**Additional solution angles I'd add:**
- **3D Taylor-Green vortex.** Canonical 3D NS test bed.
- **Hou-Luo axisymmetric Euler near-blowup.** Active 2014-2025
  research target.
- **Constantin-Iyer Lagrangian formula.** Vortex stretching
  diagnostic.
- **Self-similar profile fitting.** If a candidate near-blowup
  configuration is detected, fit `1/(T-t)^α` profile.
- **Euler vs NS comparison.** Euler is conjecturally where blowup
  lives; NS dissipation may regularize. Direct comparison is
  informative.
- **CAPD-style validated PDE numerics.** Interval-arithmetic for
  rigorous bounds on intermediate quantities.

**Datasets/tools to build:**
- **Pseudospectral 3D NS solver** at workstation scale
  (N up to 256³). REBOUND-style, but for incompressible NS.
- **BKM-integral diagnostic library.** Reusable across any 3D
  flow simulation.
- **Hou-Luo geometry simulator** for axisymmetric Euler.
- **Self-similar fitting library** for candidate near-blowup data.

---

### 2.2 Problem 2 — Yang-Mills Mass Gap (`harmonia_C_02`)

**Verdict given:** OPEN.

**My read of the work:**

✓ **2D U(1) Metropolis matches I_1/I_0 to 1%.** Clean calibration
of the lattice toolchain. ⟨cos θ_p⟩ = 0.69991 vs exact 0.69777
at β=2.0 is excellent. Wilson loops W(1,1), W(2,2), W(1,3) all
within 1-3 sigma of analytic predictions.

✓ **Obstruction correctly localized at "marginal renormalizability
+ Gribov + reflection-positivity-of-continuum-limit."** This is
the standard list from Glimm-Jaffe; C identifies it precisely.

✓ **2D abelian / 4D non-abelian distinction articulated.** "In 2D,
plaquettes factor through Haar measure on U(1), partition function
is product of single-plaquette integrals. In 4D non-abelian,
plaquettes are coupled, partition function is multi-dimensional,
RG is marginal." Correct and clear.

✗ **Did not run 2D non-abelian (SU(2)).** This is the cheapest
non-trivial extension — same Metropolis structure, different
group (Haar measure on SU(2) instead of U(1)). Would have given
a non-abelian 2D anchor where existence is rigorously known.

✗ **Did not run 3D abelian or 3D non-abelian.** 3D YM is
super-renormalizable; existence is more secure than 4D. Sweeping
2D → 3D → 4D in U(1), then 2D → 3D in SU(2), would have given a
"how does the gap measurement scale with dimension" trajectory.

✗ **Glueball mass not measured.** Even on a small lattice,
Polyakov loop correlators give a glueball mass estimate. C didn't
attempt — but this is the canonical "is there a gap" diagnostic.

✗ **No deconfinement transition probe.** As β varies, the lattice
exhibits a phase transition; locating it is a substrate-grade
calibration of the toolchain.

✗ **Balaban block-spin RG not visualized.** C lists this in
"where I would push" as the most novel direction; not attempted.

**Round 2 plan (~3hr):**
- Implement 2D SU(2) Metropolis (~1hr; Haar measure swap).
  Verify confinement / area law.
- 3D U(1) and 3D SU(2) sweeps (~1hr). Document dimension scaling.
- Glueball mass via Polyakov loop correlator (~30 min on existing
  data).
- Sketch Balaban RG visualization (~30 min).

**Additional solution angles I'd add:**
- **2D / 3D non-abelian lattice.** Cheapest non-abelian extension.
- **Polyakov loop deconfinement transition.** Critical β location.
- **Glueball mass via correlator.** Direct gap diagnostic.
- **Symanzik improvement.** Reduce lattice artifacts.
- **Stochastic quantization / Langevin lattice.** Alternative
  sampling.
- **Balaban block-spin RG flow.** As coordinate system across
  scales — Prometheus-aligned (coordinate-systems-of-legibility).
- **Migdal-Kadanoff approximate RG.** Closed-form-ish RG flow for
  2D / 3D, useful for cross-dim comparison.

**Datasets/tools to build:**
- **Lattice gauge theory toolkit** with U(1), SU(2), SU(3); 2D /
  3D / 4D; Wilson + Symanzik improved actions; Polyakov / Wilson
  loop estimators.
- **Glueball-mass extraction library.**
- **RG flow visualizer.**

---

### 2.3 Problem 3 — Kakeya Conjecture (`harmonia_C_03`)

**Verdict given:** OPEN (incidence-multiplicity scaling localized).

**My read of the work:**

✓ **Implication-triangle framing for P3–P5 is correct.** Kakeya ⇒
Restriction ⇒ Bochner-Riesz at the bound-transfer level. C is
explicit that this is why P3–P5 are bundled.

✓ **2D box-counting calibration trace.** N=256² grid, K up to 256
directions. Dimension grows from 1.194 to 1.756 monotonically;
asymptotes below 2 because grid is finite. C explicitly flags
this as artifact, not progress. **Reward-signal-capture check
passes.**

✓ **3D tube incidence stats are substrate-grade.** N=64³, K from
50 to 400 random tubes. Avg overlap grows 5× → 21× as K
quadruples. Max multiplicity grows 30 → 115. **This is the
"tubes pile up at points" structure that Wolff's argument
quantifies, made numerically visible.** Reproducible in ~2 minutes
of CPU.

✗ **Wolff hairbrush bound numerical reproduction sketched, not
run.** Hairbrush = bush of tubes through a fixed tube. Counting
hairbrushes in C's 3D tube ensemble and verifying Wolff's
inequality numerically would be a substrate-grade
"calibrate-the-tool-against-itself" check. Listed as "where I
would push" Attack 2.

✗ **Stickly / plainly / grainy Katz-Tao trichotomy not detected.**
C lists as Attack 3 of "where I would push." This is the kind of
classification that a coordinate-system attempt would naturally
produce.

✗ **No 4D / 5D extension of incidence stats.** The same `N^d` grid
+ K random tubes computation runs in 4D / 5D; would have shown
how multiplicity scales with dimension.

✗ **Finite-field Kakeya (Dvir 2008) not invoked.** Dvir's
polynomial-method proof of finite-field Kakeya is the cleanest
calibration anchor for the polynomial method itself; not
mentioned.

✗ **No bushification / decoupling experiment.** Bourgain-Demeter
ℓ²-decoupling on the moment curve / paraboloid is the modern
unification tool; C didn't simulate.

**Round 2 plan (~3hr):**
- Wolff hairbrush numerical reproduction (~1hr). Count hairbrushes
  in existing 3D ensemble; verify Wolff's inequality.
- 4D and 5D extension of 3D incidence stats (~30 min reusing
  existing code).
- Finite-field Kakeya simulation (~30 min). F_p^n with K random
  affine lines; Dvir's polynomial-method bound is computable on
  small p, n.
- Stickly / plainly / grainy detector on small ensembles (~1hr).

**Additional solution angles I'd add:**
- **Finite-field Kakeya via polynomial method.** Dvir 2008.
- **Wolff hairbrush + Katz-Tao trichotomy detection.**
- **Bourgain-Demeter decoupling on paraboloid.**
- **Connection to projection theorems** (Marstrand, Mattila).
- **Maximal function estimates.** Kakeya maximal function as
  intermediate diagnostic.
- **4D / 5D dimension scaling.** Quantitative gap to conjectured
  vs Wolff bound.

**Datasets/tools to build:**
- **Tube-incidence registry** for Kakeya extremal candidates;
  reproducible numerical fingerprints.
- **Polynomial method calculator.** Given a forbidden pattern,
  output the slice-rank-style bound; reusable across cap-set,
  Kakeya, sunflower (cross-batch tool — also B's batch could use).
- **Hairbrush + bush counting library.**

---

### 2.4 Problem 4 — Restriction Conjecture (`harmonia_C_04`)

**Verdict given:** OPEN (Stein-Tomas calibrated; gap to full
restriction localized).

**My read of the work:**

✓ **Stein-Tomas endpoints for n=2,3,4,5 tabulated correctly.**
n=2: (2,6); n=3: (2,4); n=4: (2, 10/3); n=5: (2, 3). The shrinking
gap to conjectured `2n/(n-1)` is well-articulated.

✓ **Indicator-of-arc / cap calibration in n=2 and n=3.** Stein-Tomas
ratio at q=6 (n=2) stays under ~2.4 across cap-size factor-16
sweep; ratio at q=4 (n=3) stays under 5. **Decreases with cap size
δ.** Calibration confirms boundedness in proven regimes.

✓ **Gap-localization clean.** "L² orthogonality reaches q =
2(n+1)/(n-1) but cannot push to conjectured q > 2n/(n-1).
Bilinear / multilinear / polynomial / decoupling each closes
part of the gap." Correct articulation.

✗ **Knapp examples not implemented.** C explicitly notes this is
the required test class for probing the open part of the
conjecture (saturation from below). **This is the universal
missing piece across P4 and P5.**

✗ **Bilinear extension (Tao-Vargas-Vega) not simulated.** Two
angularly-separated caps in S²; bilinear estimate is strictly
better than linear. Standard machinery; ~1-2 hours of code.
Listed as "where I would push" Attack 2.

✗ **Decoupling on paraboloid not run.** Bourgain-Demeter
ℓ²-decoupling sample on `{(x, |x|²): x ∈ R^{n-1}}`. Listed as
Attack 3.

✗ **No comparison sphere vs paraboloid.** Two natural restriction
geometries; comparing extension constants on each is informative.

**Round 2 plan (~3hr):**
- Implement Knapp examples (~1.5hr). Sweep restriction estimate
  on Knapp blocks at conjectured boundary in n=3.
- Bilinear extension (Tao-Vargas-Vega) numerical (~1hr).
- Decoupling on paraboloid (~30 min).

**Additional solution angles I'd add:**
- **Knapp blocks (universal missing piece for P4 + P5).**
- **Bilinear / multilinear restriction (Tao-Vargas-Vega,
  Bennett-Carbery-Tao 2006).**
- **Decoupling on paraboloid (Bourgain-Demeter).**
- **Sphere vs paraboloid comparison.**
- **Maximal restriction estimates.**
- **Stein-Tomas / Strichartz duality.** Restriction is dual to
  L^p → L^q estimates for Schrödinger / wave; computable in PDE
  setting too.

**Datasets/tools to build:**
- **Knapp-block test function library** (universal missing piece
  for P4 and P5; reusable across batches).
- **Bilinear extension calculator.**
- **Decoupling-bound runner.**

---

### 2.5 Problem 5 — Bochner-Riesz Conjecture (`harmonia_C_05`)

**Verdict given:** OPEN (calibration *partial* due to
Gaussian non-adversarial test function; Fefferman 1971 not
exposed by smooth test).

**My read of the work:**

✓ **The reward-signal-capture catch is the cleanest substrate-grade
discipline event in any batch.** Gaussian sweep gave `T^0 f / f
= 1.0000` exactly across all p in n=2,3 — which would imply BR is
bounded at δ=0, contradicting Fefferman 1971. C caught this,
diagnosed it (Gaussian's frequency support doesn't reach the
multiplier transition region), flagged metadata as `partial pass`,
and identified Knapp blocks as the required adversarial class.
**Promoting this catch as the canonical example of
reward-signal-capture-prevention is high-ROI for the substrate.**

✓ **Boundary-line of conjectured region articulated.**
`|1/p - 1/2| ≤ (δ + 1/2)/n`. C tabulates conjectured (p_lo, p_hi)
for various δ in n=2,3.

✓ **n=2 vs n≥3 distinction at curvature level.** "Unit circle is
1-manifold with constant curvature; Carleson-Sjölin local
orthogonality exploits this. In n≥3, sphere has higher-dim
curvature variation that the local-orthogonality argument
doesn't directly control." Correct articulation.

✗ **Knapp blocks not implemented.** Same as P4. The Knapp-block
implementation, once done, exposes Fefferman's counterexample at
δ=0 as a *divergent* ratio with grid refinement. Until then,
calibration is incomplete.

✗ **Square function approach not implemented.** C lists as Attack
2 of "where I would push." Carleson-Sjölin / Cordoba decomposition
numerically in 2D would reproduce the proved n=2 bound. Hand-cranked
but mechanical.

✗ **n=3 boundary probe not run.** Sweep `(p, δ)` along conjectured
boundary line in n=3 at multiple grid resolutions, see whether
ratio appears bounded as grid refines. Numerical evidence (with
caveats) for conjecture in open regime.

✗ **No FFT-based fast multiplier.** C uses grid-based multiplier;
FFT-based is the standard fast technique.

**Round 2 plan (~3hr):**
- Implement Knapp blocks (~1hr; reusable from P4 round-2).
  Run BR ratio sweep on Knapp blocks; verify Fefferman
  counterexample appears as divergent ratio at δ=0.
- Square function decomposition in 2D (~1hr).
- n=3 boundary probe at multiple grid resolutions (~1hr).

**Additional solution angles I'd add:**
- **Knapp blocks (same as P4).**
- **Square function decomposition.**
- **FFT-based fast multiplier.**
- **Christ-Kiselev maximal function.**
- **Restricted projection lemma.**
- **Tao multilinear adjoint Kakeya.**

**Datasets/tools to build:**
- **Knapp-block library (cross-P4-P5 tool).**
- **FFT-based BR multiplier library.**
- **Boundary-line probe runner** for any multiplier-style operator.

---

## 3. Cross-cutting observations

### 3.1 C's "marginal-vs-supercritical" cross-batch signature

C's summary §2 articulates: *"all 5 share a 'marginal-vs-
supercritical' theme: the controlled quantity (energy in P1,
lattice approximation in P2, L² orthogonality in P3-P5) sits one
degree below what the open problem requires."*

This is C's substrate-grade dominant signature:
**`MARGINAL_VS_SUPERCRITICAL_GAP`** — the proven instrument
controls a quantity one degree below what's needed. Resolution
requires either bridging the marginal gap or finding a categorically
different controlled quantity.

### 3.2 Updated cross-batch failure-mode-signature table

Five batches reviewed end-to-end (mine, A, B, C, D). Each has a
distinct dominant signature:

| batch | dominant signature | resolution requires |
|---|---|---|
| Combinatorics (A) | `SHARP_INEQUALITY_AT_WRONG_CONSTANT` | new structural input |
| Dynamics (B) | `TWO_CLASSES_WITHIN_DOMAIN` | depends on class |
| **Analysis/PDE (C)** | **`MARGINAL_VS_SUPERCRITICAL_GAP`** | **bridge the marginal gap or find different controlled quantity** |
| Foundations (D) | `REQUIRES_PARALLEL_OPEN_PROBLEM` | unlock single hub-problem |
| Complexity (E, mine) | `META_OBSTRUCTION_RULES_OUT_TECHNIQUE_CLASS` | techniques outside known classes |

**Five batches, five distinct dominant signatures.** This is
substrate-grade — each domain has its own *shape of failure*.
Aporia's cross-batch synthesis should formalize this 5-class
taxonomy and use it as anchor data for the remaining 3 batches
(charon 1, 2, 3).

### 3.3 The reward-signal-capture catch in P5 as substrate primitive

C's P5 catch is the platonic ideal of the discipline working. The
sequence:
1. Run experiment.
2. Get clean numerical result (`T^0 f / f = 1.0000`).
3. Recognize result would imply known-false statement.
4. Diagnose mechanism (test function too smooth).
5. Flag in metadata as partial pass.
6. Identify required adversarial test class.
7. Leave in record explicitly with the contradiction visible.

This deserves to be promoted as the **canonical anchor case** for
the reward-signal-capture pattern in `feedback_signal_capture`-
style memory entries. Concretely: a paragraph in
`harmonia/memory/methodology_toolkit.md` referencing this attempt
file as the anchor.

### 3.4 The "implication triangle" as cross-batch primitive

C identifies `Kakeya ⇒ Restriction ⇒ Bochner-Riesz` as a
quantitative-bound-transfer structure. This is **a different kind
of cross-problem connection** than the failure-mode signatures
(which are about *shapes of failure*). The implication-triangle
structure is about *forward propagation of progress* — a
breakthrough on one node lifts the others.

For Aporia synthesis: every batch should be checked for similar
implication structures. **Do A's combinatorics problems have
implication triangles?** (Sunflower → Cap Set via polynomial
method — yes, partial.) **D's foundations?** (SCH ⟂ GCH-singular
via SH — yes.) **Mine?** (None — meta-obstructions are
domain-specific.) Substrate-grade observation: implication
triangles are present in some batches and absent in others; the
presence is itself signal.

### 3.5 Recurring failure modes within C's batch

| failure mode | where |
|---|---|
| Knapp blocks missing | P4, P5 |
| Coordinate-system invention not attempted | P3-P5 cross-cutting |
| 3D / higher-dim sweep at scale | P1 (3D NS), P2 (3D YM), P3 (4D Kakeya) |
| Bilinear / multilinear / decoupling not run | P3, P4 |
| `MARGINAL_VS_SUPERCRITICAL_GAP` | all 5 |

Time-compression hit specifically at the "implementations that
would actually probe the open regime." C's calibration anchors
are clean; the gap is to the open territory.

### 3.6 What C's batch contributes to cross-batch pattern catalog

- **`MARGINAL_VS_SUPERCRITICAL_GAP`** — analysis/PDE-domain
  signature.
- **`ADVERSARIAL_TEST_FUNCTION_BEFORE_NOVELTY_CLAIM`** — methodology
  primitive.
- **`ADJACENT_EASIER_VERSION_AS_CALIBRATION_ANCHOR`** — methodology
  primitive.
- **`IMPLICATION_TRIANGLE` (Kakeya⇒Restriction⇒BR)** — cross-problem
  forward-propagation structure.
- **`NUMBERED_SUMMARY_FILE_AS_INDEX`** — operational pattern; better
  than separate suffixed file.
- **`P5_REWARD_SIGNAL_CAPTURE_CATCH`** — canonical anchor case for
  the reward-signal-capture pattern.

---

## 4. Concrete recommendations to James

In rough priority order:

### 4.1 Promote C's two methodology-toolkit primitives immediately

C explicitly proposes both candidates anchored across 5 attempts:
- `ADVERSARIAL_TEST_FUNCTION_BEFORE_NOVELTY_CLAIM`
- `ADJACENT_EASIER_VERSION_AS_CALIBRATION_ANCHOR`

Both are concretely grounded; no second-batch confirmation needed
since the anchors live in C's 5 attempts. Add to
`harmonia/memory/methodology_toolkit.md` with citations to
`harmonia_C_05_bochner_riesz.md` (P5 reward-signal-capture catch)
as the anchor case for primitive 1, and to all 5 C attempts as
anchors for primitive 2.

### 4.2 Promote the P5 reward-signal-capture catch as canonical anchor

The Bochner-Riesz Gaussian-vs-Fefferman catch is the cleanest
single example of substrate-grade self-correction in the entire
8-batch round. Promote as canonical anchor case in
`feedback_signal_capture`-adjacent memory entries. Concretely:
~1 paragraph in `methodology_toolkit.md` + cross-link to
`harmonia_C_05_bochner_riesz.md`.

### 4.3 Build Knapp-block test function library

Single highest-ROI cross-problem tool for analysis/PDE batch.
~1-2 hours of code; covers P4 (restriction), P5 (Bochner-Riesz),
and any future harmonic-analysis batch attempt. Universal missing
piece in C's batch.

### 4.4 Round-2 C batch focused on executing existing sketches +
implication-triangle coordinate system

Same 5 problems, 3hr/problem budget. Concretely:

| problem | execute |
|---|---|
| P1 NS | 3D pseudospectral N=128³ Taylor-Green vortex |
| P2 YM | 2D SU(2) + 3D U(1) + 3D SU(2) lattice sweep + glueball mass |
| P3 Kakeya | Wolff hairbrush bound + 4D/5D incidence + finite-field Kakeya |
| P4 Restriction | Knapp examples + bilinear (Tao-Vargas-Vega) + decoupling |
| P5 BR | Knapp blocks + square function + n=3 boundary probe |

**Bonus task:** Attempt a unifying coordinate system across P3-P5
(tube-incidence / cap-extension / multiplier-near-sphere). C
explicitly listed this as out-of-scope; it's the highest-leverage
charter-aligned experiment (coordinate-systems-of-legibility).

### 4.5 Adopt the numbered-summary-file convention across all batches

C's `_00_summary.md` placement is materially better than B's
suffix-only `_summary.md` — index-00 signals "read this first"
to any future tooling that walks the directory. Mandate
`<batch>_00_summary.md` as the index file for any future round.

### 4.6 Cross-batch dynamics-of-failure-mode-signatures (5-batch
update)

Five batches reviewed, five distinct dominant signatures. The
table now reads:

| problem | batch | signature |
|---|---|---|
| EFL, Frankl, Sunflower, Cap Set, Hadamard | A combinatorics | SHARP_INEQUALITY_AT_WRONG_CONSTANT |
| Furstenberg, Sarnak, Palis | B dynamics class A | MISSING_RIGIDITY_FUNCTIONAL |
| Painlevé, KAM | B dynamics class B | MISSING_SHARP_FINITE_DIM_BOUND |
| **NS, YM, Kakeya, Restriction, BR** | **C analysis/PDE** | **MARGINAL_VS_SUPERCRITICAL_GAP** |
| SCH, Vopěnka, Whitehead, GCH-singular, Forcing | D foundations | REQUIRES_PARALLEL_OPEN_PROBLEM |
| P vs NP, P vs PSPACE, Det-vs-Perm, UGC, qPCP | E complexity | META_OBSTRUCTION_RULES_OUT_TECHNIQUE_CLASS |

This is the cleanest cross-batch substrate-grade table I've been
able to extract. Aporia should produce this for all 8 batches once
the remaining charon 1/2/3 land.

### 4.7 Build the analysis/PDE calibration registry

Concrete numbers across systems:

- 2D NS BKM integral growth at ν=10⁻³: ~0.97/sec
- 2D U(1) ⟨cos θ_p⟩ at β=2: 0.69777
- 2D U(1) string tension at β=2: 0.35986
- 3D Kakeya tube incidence at K=400, N=64³: avg overlap 21×, max
  multiplicity 115
- n=3 Stein-Tomas ratio on indicator-of-cap: bounded `< 5`
- BR ratio at δ=0 on Gaussian: 1.0000 *(known artifact, not bound)*

Tabulate; machine-readable; reusable across attempts.

---

## 5. What this critique does NOT do

- Does **not** re-attempt any of C's 5 problems. Originals stand.
- Does **not** verify C's specific numerical results. I trust C's
  reported numbers; round 2 should re-verify if these are promoted
  to substrate-grade calibration anchors.
- Does **not** claim harmonic-analysis / PDE expertise comparable
  to a practicing analyst. Where I flag a "missing angle" that
  overlaps a literature C already cited but didn't pursue, the gap
  is between literature recall and execution, not between C and the
  discipline.
- Does **not** evaluate the methodological-toolkit primitive
  proposals' specific formulations beyond "they're well-anchored."
  Final phrasing is for the methodology toolkit's curator.

---

## 6. Honest read

C's batch is the **cleanest methodologically** of the five batches
reviewed. The numbered `_00_summary.md` is the right index pattern.
The P5 reward-signal-capture catch is the platonic ideal of the
discipline working. The two methodology-toolkit primitives are
explicitly ready for promotion. The implication-triangle framing
for P3-P5 is correct and is exactly the substrate-grade cross-problem
observation Aporia synthesis needs.

Where C falls short is **execution depth at the open frontier**.
Time compression hit Attack 3+ across all 5 problems; Knapp blocks
are the universal missing piece for P4 and P5; coordinate-system
invention across P3-P5 is the highest-leverage out-of-scope
experiment.

C's substrate-vocabulary use ("reward-signal-capture check,"
"novelty-budget work," "methodology toolkit candidate") suggests
either deep substrate disposition internalization at session-open
or rigorous internal-terminology citation. Either way, the signal
is good — C is methodology-aligned with the substrate at a level
no other batch I've reviewed demonstrates.

Recommended action sequence:

1. **Promote C's two methodology-toolkit primitives** to
   `harmonia/memory/methodology_toolkit.md` immediately. Anchored
   across 5 attempts; ready.

2. **Promote the P5 reward-signal-capture catch** as the canonical
   anchor case for that pattern. ~1 paragraph + cross-link.

3. **Build Knapp-block test function library** (~1-2 hours; covers
   P4 + P5 + any future harmonic-analysis batch).

4. **Adopt the numbered-summary-file convention** (`<batch>_00_summary.md`)
   across all future rounds.

5. **Round-2 C batch** with explicit goals: execute the
   "where I would push" Attack-2/3 sketches across all 5 problems,
   plus a unifying coordinate system attempt across P3-P5.

The single most valuable single action: **promote both
methodology-toolkit primitives now**. They're anchored, they're
ready, and they generalize beyond C's batch — every future
analysis-flavored work and every future numerical-experiment-based
work inherits the discipline.

— Reviewed by Harmonia E (sessionE), 2026-05-05.
