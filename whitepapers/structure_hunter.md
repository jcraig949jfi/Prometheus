# Structure Hunter
## A Whitepaper on Automated Discovery of Coordinate Transformations in Empirical Mathematics
### v2 — 2026-04-24 — Harmonia_M2_sessionC with James Craig, Project Prometheus

---

## READ THIS FIRST

This document is **incubation-stage**, not a shipped system. No code has
been written against this design. No outputs have been measured.

The target audience is external reviewers — frontier models tasked with
critique, mathematicians assessing whether the discipline is
load-bearing, or engineers deciding whether to build the reference
implementation. The document is self-contained: you should not need to
read the Prometheus substrate to evaluate the position. Where substrate
primitives are referenced, this paper gives enough context to evaluate
the reference; it points to internal artifacts for full detail.

**The paper describes an instrument, not findings.** The instrument is
designed to produce candidate coordinate transformations on empirical
mathematical data. The primary claim is *architectural*: that certain
constraints must be enforced at the language-design level for the
instrument to produce substrate-legible output rather than F043-class
noise. Whether the instrument, once built, produces anything novel is
an empirical question the paper does not answer.

**v2 note.** This revision absorbs a five-fragility critique of v1 from
James Craig (2026-04-24) whose core observation was: v1's binary-gate
discipline was over-brittle, and continuous measurement of structural
independence and usefulness is the right abstraction. v2 restructures
§4 around seven scoring axes with Pareto-front promotion and two
categorical gates, replacing v1's four binary-gate principles. The
bones are the same; the discipline inside the pipeline is continuous
rather than binary. Section 4 headings and the scoring function are
the most-changed material; §1–3 (the problem framing) are largely
unchanged.

Please cite specific passages when offering critique. Memory-augmented
inference without citation is how prior Prometheus reviews drifted into
wrong framing.

---

## Abstract

The standard framing for "automated conjecture generation" is symbol
regression: run genetic programming or reinforcement learning over a
space of parameterized expressions, score candidates by fit, return
the best. The literature is extensive (AI-Feynman, PySR, Deep Symbolic
Regression, DreamCoder, equation-learning variants) and the outputs
are reliably plentiful. They are also reliably noisy: most discovered
"laws" are algebraic rearrangements of input variables, functional
redundancies in the chosen grammar, or overfits to the encoding scheme
that made certain forms cheap. The problem is not that the search is
weak; the problem is that *evidence of structure* has been conflated
with *low description length against a fit target*. Those are not the
same thing.

This paper proposes a reframe. Instead of "generate conjectures," the
instrument generates **coordinate transformations** — typed functions
from objects to features that declare what information they preserve,
what they destroy, and what claim-relevant detectability gains they
afford. Two categorical gates protect type-integrity and scorer
sanity; everything else is continuous. Specifically:

- **Two hard gates.** A type-level rule (no output that asserts
  invariants; transformations must declare `preserves`, `destroys`,
  and `affordances`) and a calibration sanity gate (the instrument
  must rediscover known anchors before its verdict on novel
  candidates is trusted).
- **Seven continuous scoring axes.** Simplicity, fit, basis-projection
  (continuous measurement of functional-span overlap with known
  identities via linear, kernel, and mutual-information estimators),
  calibration alignment, residual structure (non-random leftover
  pattern after transformation), affordance gain (downstream
  detectability), reconstructability (inverse-model accuracy on
  declared preserves), and AST-diversity (search-bias control).
- **Pareto-front promotion on a substrate-value triple** —
  `(novelty, usefulness, faithfulness)` = `(1 − basis_projection,
  affordance_gain, reconstructability)` — replaces pure scalar
  minimization. This surfaces candidates that win on a specific
  substrate-value axis even if their aggregate compression score is
  middling.
- **Cross-dataset consistency as a first-class audit artifact.**
  Every run executes on ≥ 2 datasets; per-axis consistency metrics
  are reported alongside candidates; transformations that work on
  only one slice are flagged, not auto-rejected.
- **Encoding-perturbation robustness** — ordering invariance, margin
  stability, and null-encoding baseline — distinguishes structural
  signal from syntax preference in the MDL objective.
- **A failure-mode declaration** — what the instrument WILL produce
  false positives on, and what kinds of structure it is
  constitutionally unable to see — commits to the bound before
  operating inside it.

The instrument's reach is bounded. Declaring the bound up front, and
reporting continuous metrics rather than binary verdicts, is the
discipline. The paper closes with a reference implementation sketch,
an open-question list, and a roadmap with a cheap-path starting
experiment designed to be empirically informative in ~1.5 ticks of
compute.

---

## 1. The conjecture problem in empirical mathematics

A working mathematician observing computational data over a class of
objects — elliptic curves, number fields, modular forms, graphs,
integer sequences — looks for relations. A dense table of object
features invites the question: which of these columns predict which
others? Which combinations are invariant across a family? Which
inequalities tighten at a family boundary?

The operational form of this question is *conjecture*. The
Hardy–Littlewood circle method, the Birch–Swinnerton–Dyer conjecture,
the Lehmer gap problem, the abc conjecture — each begins as a
statement of the form "in the class of objects X, the quantity Y
stands in relation R to quantity Z, empirically." The conjecture is
verified or falsified on a scale the author can hand-compute, then
promoted or retracted over decades of subsequent work.

Automating the hand-computing step is tempting. If we can enumerate
relations faster than a human, we might surface structure a human
attention span misses. Symbol-regression tools do exactly this: they
mutate and cross-over candidate expressions, score them against data,
keep the best. The AI-Feynman pipeline recovers many of the
classical physics equations from their numerical instantiations;
PySR has been used to find effective theories in cosmology and
chemistry; DreamCoder evolves programmatic regularities in abstract
sequences. The tooling works.

### 1.1 What the tooling is actually doing

The tooling returns the expression `e*` minimizing some variant of
`description_length(e) + description_length(data | e)`. It is a
principled scoring function (Rissanen's MDL). But "the expression
that best compresses the data in a given grammar" and "evidence that
the relation named by the expression is structural" are not the same
proposition.

Specifically, the tooling cannot distinguish:

- **structural laws** — relations that hold by virtue of the
  mathematical objects' intrinsic nature (e.g., the Hasse bound
  `|a_p| ≤ 2√p` on elliptic curves);
- **definitional rearrangements** — relations that hold because the
  expression is an algebraic restatement of how the variables were
  defined (e.g., any correlation between `log|Sha|` and
  `log(Ω·∏c_p)` on elliptic curves is forced by the BSD identity);
- **near-tautologies** — relations that are not exact rearrangements
  but lie in the functional span of the known identity basis
  (Szpiro ratio and Faltings height both contain `log|Δ|` at
  leading order and "correlate" by near-identity rather than by
  structure);
- **grammar-advantaged forms** — relations that win because the
  grammar makes them cheap to express;
- **sparse-structure phenomena** — phase transitions, threshold
  effects, and rare-but-real structure that MDL's compression
  objective cannot naturally express.

The five are numerically indistinguishable in a single MDL score.
They are distinguishable only by *multiple complementary measurements*
— structural independence tests, encoding-perturbation audits, and
downstream-usefulness probes — and by *making each measurement
continuous rather than binary* so that boundary cases surface for
review rather than collapse into a yes/no verdict.

### 1.2 The empirical cost of the conflation

Project Prometheus, the substrate hosting this work, experienced the
conflation at scale. In April 2026 a correlation between analytic
Sha and a Tamagawa-Ω product on rank-0 elliptic curves was reported
with `corr = −0.4343` at `z_block = −348` under a block-shuffle-
within-conductor-decile null. The result passed its own null because
the block-shuffle preserved the definitional dependence: the BSD
identity expresses `log A` as a linear combination of terms that
include `−log|Sha|`, so the correlation is a restatement of the
identity in rearranged variables. The finding was retracted as F043
on 2026-04-19. It is now the anchor case for a graded severity scale
("Pattern 30") applied to all correlation-based work on the
substrate.

F043 is one instance of a structural pattern. A brute search over
BSD-ingredient variables with a symbol-regression tool would produce
many such instances. The surface form of the output — low MDL, high
block-shuffle z, survives naive nulls — matches the surface form of
a genuine finding. An instrument that returns both without
discriminating between them accumulates work that will be retracted
in bulk when the structural check is eventually performed.

Prometheus's position is that the structural check cannot be bolted
on after generation, AND that the check should not be a single binary
gate. The discipline must live continuously across multiple
measurements in the generator's type system. This paper describes
how.

---

## 2. Substrate context (brief, for external readers)

Prometheus is a version-controlled empirical audit substrate for
computational mathematics. It has been operational since early 2026
and its charter (`docs/landscape_charter.md`,
`docs/long_term_architecture.md`) is explicit: the instrument records
and audits measurements, it does not prove theorems or publish
discoveries. Findings are instrumented byproducts of exercising the
tool; the tool is the deliverable.

The substrate's primitives, minimally:

- **F-IDs** — identifiers for empirical claims about mathematical
  objects (e.g., F003 is BSD parity on elliptic curves; F011 is a
  first-gap variance deficit in rank-0 L-functions).
- **P-IDs** — identifiers for projections or coordinate systems
  through which claims are measured (e.g., P020 is
  conductor-decile conditioning; P028 is Katz–Sarnak symmetry-type
  stratification).
- **The tensor** — a 2-D matrix `T[F, P] ∈ {−2, −1, 0, +1, +2}`
  recording the per-cell verdict of an F-ID measured through a P-ID.
- **Pattern library** — ~30 recognized failure modes (e.g., Pattern
  30: algebraic-identity coupling detection, five severity levels).
- **Null protocol** — five claim classes, each mapped to an
  appropriate null model. Construction-biased samples (Class 4)
  cannot be validated by permutation; algebraic-identity claims
  (Class 5) cannot be validated by any null — they require Pattern
  30 diagnosis instead.
- **Symbol registry** — versioned, immutable primitives for operators
  (null models), datasets (SQL-pinned), shapes (structural pattern
  descriptors), constants (with CI), signatures (tuple schemas),
  and patterns (methodology recognition rules). Twenty-four
  promoted symbols as of 2026-04-23.
- **Retractions** — first-class events, preserved historically.

The substrate is deliberately bottom-up. It is not derived from a
philosophy of mathematics; it is derived from cataloguing what
happens when specific tests are run against specific data, with
enough provenance that future readers can reproduce or refute every
claim.

The Structure Hunter proposal — automating the generation of P-IDs —
sits in a space the substrate has anticipated (the `gen_11` slot of
the generator pipeline is "coordinate-system invention") but not yet
populated. This whitepaper proposes how to populate it.

---

## 3. Why naive symbol regression fails: the F043 anchor, generalized

Consider a genetic-programming pipeline over a grammar whose atomic
variables include the full BSD-ingredient family:

```
atoms = {L(E, 1), Ω(E), Reg(E), ∏_p c_p(E), |Sha(E)|, |E(Q)_tors|,
         rank(E), ...}
operators = {+, −, ×, ÷, log, exp, ^, =, ≤, ~, corr}
```

The BSD identity, at rank 0, is:

$$ L(E, 1) = \frac{\Omega_E \cdot \prod_p c_p(E) \cdot |\text{Sha}(E)|}{|E(\mathbb{Q})_{\text{tors}}|^2} $$

Taking logs:

$$ \log L = \log \Omega + \log \prod c_p + \log |\text{Sha}| - 2 \log |\text{Tor}| $$

The identity implies that any expression over these atoms whose
leading-order behavior is a linear combination of `{log Ω, log ∏c_p,
log|Sha|, log|Tor|}` will be numerically dependent on the other
terms in the identity, on the rank-0 cohort, **by construction**.

A naive GP pipeline evolving expressions in this grammar will
produce:

- `corr(log|Sha|, log(Ω·∏c_p))` — exact rearrangement, the F043 shape
- `corr(log|Sha| + 2 log|Tor|, log L − log(Ω·∏c_p))` — longer rearrangement
- `corr(log|Sha|/log|Tor|², (Ω·∏c_p)/L)` — ratio rearrangement
- `corr((Ω·∏c_p·|Sha|) − |Tor|², log L)` — inequality-shaped rearrangement
- `corr(log Ω + log ∏c_p, log L − log|Sha| + 2 log|Tor|)` — another
  identity restatement
- (many more)

Every one passes a block-shuffle null within conductor decile.
Every one has a large `|z|` statistic. Every one scores well under
MDL because the relation is exact on the dataset — `L(data | expr)`
is near zero. In fact, because the identity holds exactly, these
candidates *outscore* genuine findings like F011 (a statistical
deficit with non-zero residual variance), because F011 has non-zero
`L(data | expr)` while F043-shaped candidates do not.

### 3.1 Why a single post-hoc filter is not the fix

The naive fix is "filter the output with Pattern 30 before
promotion." This catches exact rearrangements. It does not catch:

- Log-transformed near-tautologies where the atoms are not shared
  but their log transforms span the same numerical subspace.
- Partial-product couplings (Szpiro × Faltings both contain
  `log|Δ|`).
- Mixed-scale expressions whose dominant behavior is identity-forced
  even when the expression is not a rearrangement.
- Functional redundancies — two expressions that span the same
  equivalence class under the grammar's operator closure.

The post-generation filter also comes too late computationally. If
90% of candidates are rearrangements, the filter throws away 90% of
the compute budget. Worse, the remaining 10% that pass the filter
are not independent draws from the "real structure" distribution;
they are whatever the grammar happens to express that does not share
variables with the identity basis. The sample is biased by the
filter in ways the downstream consumer has no visibility into.

### 3.2 Why a single binary gate is also not the fix

A first-draft alternative (v1 of this paper) proposed a hard
*grammar-time* gate: candidates with `R² ≥ 0.9` against the known
identity basis, via linear regression, are pruned before scoring.
This is better than post-hoc filtering but still brittle in two ways:

1. **Linear R² misses non-linear couplings.** Multiplicative,
   compositional, and monotone identity dependencies lie in the
   functional span of the basis but not in the linear span. A
   linear-only gate gives false negatives precisely where
   intuition-driven novelty is most plausible.
2. **Binary gates obscure boundary cases.** A candidate at
   `R² = 0.85` is closer to the identity basis than one at
   `R² = 0.05` and deserves heavier scrutiny — but a binary gate at
   `0.9` treats both as "pass." The instrument loses the continuous
   information that would help distinguish "genuinely novel" from
   "just under the threshold."

### 3.3 The actual fix: continuous, multi-measurement discipline

The claim of this paper is that the discipline must live in the
grammar *and* must be continuous. Specifically:

1. Every atomic variable carries an **algebraic-closure tag** listing
   the identities it participates in.
2. Operators carry **lineage propagation rules** defining how closure
   tags combine.
3. Candidates compute their Pattern 30 severity level at
   tree-construction time, from atom-tag intersection. Severity
   enters scoring as a continuous penalty, not a pre-scoring gate.
4. An **ideal-quotient check** runs against the known-identity basis
   materialized on the calibration dataset, using three complementary
   measures (linear R², kernel R², mutual information) with `max`
   aggregation. Continuous score; continuous penalty.
5. Candidates are scored on **seven axes**, not one (§4.4). The
   MDL-compression objective is one axis among several, balancing
   fit against basis-projection novelty, residual structure,
   affordance gain, reconstructability, and AST-diversity.
6. **Pareto-front promotion** replaces scalar minimization (§4.4).
   A candidate dominated on all three substrate-value axes (novelty,
   usefulness, faithfulness) is filtered; one non-dominated on ≥ 1
   is retained.
7. **Two categorical gates** (§4.5) remain hard rejections: the
   type-level Framing B rule and calibration battery total failure.
   These are what-the-instrument-IS and is-the-scorer-working; they
   are categorical, not continuous.

Under this discipline, F043-shape candidates pay heavy penalties
along the basis-projection axis but are not pre-pruned; they surface
in SIGNATURE with their continuous dependence scores; the auditor
can see *how close* a candidate is to the identity basis rather than
only whether it crossed a line. The compute budget still goes mostly
to independent candidates, because the soft penalty pushes F043-shaped
outputs low on the Pareto front. The difference from v1 is that
boundary cases and incomplete-basis artifacts are visible rather
than silently filtered.

---

## 4. The design

### 4.1 Overview: two categorical gates + continuous multi-axis discipline

The instrument has exactly two categorical rejection gates. Everything
else is continuous measurement:

- **Categorical Gate 1 — Framing B type rule.** Candidates that
  assert invariants as their output (equalities, inequalities,
  correlations) are rejected. Candidates without declared
  `preserves` / `destroys` / `affordances` metadata are rejected.
  §4.2 details.
- **Categorical Gate 2 — Calibration sanity.** If the instrument's
  scorer fails to recover any known anchor from a grammar that
  demonstrably contains it (`frac_anchors_recovered = 0`), all
  non-anchor outputs are untrustworthy by construction. §4.6 details.

These two gates are principled retentions, not leftover brittleness
from v1. They protect two distinct categorical properties:

- Gate 1 protects **what the instrument IS** (a transformation
  producer, not a claim producer). Soft pressure on "how claim-shaped
  is your output" would be category confusion.
- Gate 2 protects **whether the instrument is working** (can it
  find known structure). Soft pressure on "how well-calibrated is
  your scorer" just promotes less-bad garbage when the scorer is
  broken.

All other discipline — algebraic-lineage scoring, MAP-Elites niche
pressure, encoding-perturbation calibration, cross-dataset
consistency, MDL scoring — is continuous. The instrument's output
carries per-axis scores, not pass/fail verdicts.

### 4.2 Framing B — transformations with affordances, not claims

A "conjecture" is a claim about the data. A "coordinate
transformation" is a function of the data. The distinction is
load-bearing.

The type-level rule, enforced at Gate 1:

> A candidate may **transform** observables but may **not** assert
> invariants.

Allowed output shapes: feature maps (`f: objects → features`),
stratifications (`s: objects → strata`), coordinate changes
(`c: features → features`), scorers (`σ: objects → ℝ`, with
declared range and invariance).

Forbidden output shapes: equalities (`X = Y`), inequalities
(`X ≤ Y`), proportionalities (`X ~ f(Y)`), or any expression whose
natural reading is a claim about the data.

**But the type-level rule is not enough.** A purely-transformational
instrument that never engages with relational structure produces
awkward outputs: a useful transformation is often useful *because*
it linearizes something, tightens a conditional distribution, or
makes a latent structure detectable by a downstream model. Forbidding
the *expression* of relations and also forbidding the *measurement*
of relational affordances over-constrains the system.

**The resolution: affordance measurements are allowed; affordance
claims are not.** Every candidate ships with three mandatory
metadata slots:

1. **`preserves`** — a list of algebraic properties, distributional
   moments, or relational structures that round-trip through the
   transformation.
2. **`destroys`** — a list of properties lost under the
   transformation (objects distinct under the source coordinate
   that become indistinguishable after).
3. **`affordances`** — measurements of claim-relevant detectability
   gain, from a standard list (v0.3.1 lists seven types):

| Affordance | Operational form | Applies |
|---|---|---|
| `linear_probe_gain` | `acc(linear(σ(x)) → Y) − acc(linear(x) → Y)` | all candidates |
| `nonlinear_probe_gain` | same with random-forest probe (100 trees, depth ≤ 6) | all candidates |
| `variance_reduction` | `Var(Y|σ(x)) / Var(Y|x)` | numerical targets |
| `mutual_information_gain` | `I(σ(x); Y) − I(x; Y)` (KSG k=5) | any target |
| `clustering_separability` | silhouette on k-means of σ(x) vs x | all candidates |
| `rank_correlation_gain` | `|spearman(σ(x), Y)| − |spearman(x, Y)|` | ordinal targets |
| `autocorrelation_exposure` | lag-1 autocorrelation exposure | sequence-valued atoms only |

Each affordance carries a declared null baseline (same metric on
shuffled features). The instrument reports
`affordance_gain = affordance_score − null_baseline` to prevent
metrics with a non-zero floor from generating spurious
"usefulness."

**Framing-A activation path.** A candidate whose affordance score
crosses a declared threshold becomes *eligible* for Framing-A
arbitration through the substrate's existing null-protocol. The
affordance IS NOT the claim; the affordance is a screening signal
that surfaces claim candidates for independent audit. The
substrate's retraction-enabled infrastructure remains the arbiter
of truth. The Structure Hunter instrument does not assert; it
suggests, with measurements, where assertion-testing might be
informative.

### 4.3 Continuous basis-projection scoring

As described in §3.2–3.3, Pattern 30 discipline is a grammar-time
input to scoring, not a pre-scoring binary gate. Two complementary
layers:

**Layer A — atom-tag lineage.** Each atomic variable is annotated
with the identities it participates in. For LMFDB elliptic curves,
the annotation is seeded from the BSD identity, Hasse bound, Mazur
torsion classification, Scholz reflection, modularity trace, and
Szpiro-Faltings coupling. Operators carry propagation rules.
Candidate expressions inherit a severity label by atom-tag
intersection at tree-construction time.

**Layer B — continuous basis-projection score.** For a candidate
expression `E`:

```
R²_lin  = linear regression of E against {I_1, ..., I_k} materialized on data
R²_kern = kernel-ridge regression (RBF, γ = 1/n_features, ridge λ = 1e-3)
MI_norm = mutual-information estimate between E and (I_1, ..., I_k),
          normalized by H(E) (KSG estimator, k = 5)

basis_projection_score = max(R²_lin, R²_kern, MI_norm)   ∈ [0, 1]
```

Higher = closer to the identity span = less novel. Lower = farther
from the span = more novel. No binary threshold: the score enters
the seven-axis scorer (§4.4) with coefficient γ. Default γ is
large enough that candidates near `basis_projection_score = 1`
are effectively de-prioritized without being pre-pruned — which
preserves auditability of boundary cases.

**Per-measure reporting.** The three component scores are emitted
separately in SIGNATURE so downstream readers can see which kind of
dependence fired. A candidate with `R²_lin = 0.1` but
`R²_kern = 0.9` is a non-linear near-tautology that linear-only
checks would miss — the separation is diagnostic.

**Why `max`, not average.** Any one of the three measures crossing
high is evidence of dependence; averaging dilutes signal. The
stricter measure wins by construction.

**The grammar, stated precisely:**

> Typed variables + lineage tags + a continuous distance-from-
> identity-basis signal in the functional span of the known
> identities.

Distance-from-basis replaces "forbidden subspaces" as the v1 mental
model. The discipline is the same (prevent F043-shaped output); the
mechanism is continuous, which makes the instrument's epistemology
debuggable.

### 4.4 Seven-axis scoring with Pareto-front promotion

v1 of this paper used a four-component scorer. v2 expands to seven
axes, all continuous:

```
score(expr, data, grammar, basis, anchors, explored) =
    α · L(expr)                                   [simplicity]
  + β · L(data | expr)                            [fit]
  + γ · basis_projection_score                    [algebraic novelty — §4.3]
  + δ · (1 − calibration_alignment)               [anchor-battery alignment]
  + ε · (1 − residual_structure_score)            [non-random leftover — below]
  + ζ · (1 − affordance_gain_normalized)          [downstream usefulness — §4.2]
  + η · (1 − reconstructability)                  [inverse pressure — below]
  + θ · ast_diversity_penalty                     [search-bias control — below]
```

The three additions beyond v1 — **residual structure** (ε),
**reconstructability** (η), and **AST-diversity** (θ) — address
failure modes v1 could not see.

**Residual structure (ε).** A transformation that produces i.i.d.
residuals has compressed all legible structure into the model. A
transformation that produces non-random residuals has exposed
structure the forward-pass scorer does not capture. The residual-
structure score measures non-random pattern in `data − model(σ(x))`
via autocorrelation (Ljung–Box Q), compression ratio vs. shuffled
baseline, and MI between residuals and object identity. Higher =
more residual structure = more revealed signal. This catches
threshold and phase-transition phenomena that MDL alone misses.

**Reconstructability (η).** A transformation that destroys too much
(e.g., the pathological `σ(x) = 0`) scores well on simplicity and
even on narrow affordances while being useless as a coordinate.
Reconstructability is the accuracy of a simple inverse model
`invM: σ(x) → preserves(x)` — gradient-boosted regression with
bounded complexity so it cannot memorize. Candidates must
reconstruct *all* declared preserves to score well; the score is
`min(accuracy_per_preserved)`. This imposes an inverse-pressure
floor: degenerate projections fail here even if they pass
elsewhere.

**AST-diversity (θ).** GP populations collapse to local structural
optima if unconstrained. MAP-Elites enforces output diversity
(different behavior cells); the θ penalty enforces input diversity
(different tree shapes) via a replay buffer of canonicalized AST
hashes. Both are needed; either alone leaves a failure mode.

**Scale normalization.** Before coefficients make sense, axis
scales must be commensurate:

| Axis | Raw scale | Normalized form | Typical range |
|---|---|---|---|
| Simplicity | AST bits | `L(expr) / n_nodes` (per-node) | `[0, 10]` |
| Fit | data bits | `L(data|expr) / n_samples` | `[0, 20]` |
| Basis projection | `[0, 1]` max-of-three | unchanged | `[0, 1]` |
| Calibration alignment | `[0, 1]` frac | `1 − frac` | `[0, 1]` |
| Residual structure | `[0, 1]` max-of-three | `1 − score` | `[0, 1]` |
| Affordance gain | `[0, ∞)` max-of-seven | `1 − min(1, max)` | `[0, 1]` |
| Reconstructability | `[0, 1]` min accuracy | `1 − acc` | `[0, 1]` |
| AST diversity | `[0, 1]` similarity | unchanged | `[0, 1]` |

**Default coefficients (v0.3.1 PROVISIONAL, subject to empirical
calibration):**

```
α = 0.1     # per-node simplicity; light because trees are small
β = 1.0     # per-sample fit; the anchor scale
γ = 5.0     # basis projection — load-bearing
δ = +∞      # calibration — HARD REJECTION on total failure (§4.6)
            # otherwise 2.0 × (1 − calibration_alignment)
ε = 1.0     # residual structure
ζ = 1.0     # affordance gain
η = 0.5     # reconstructability — moderate inverse pressure
θ = 0.3     # AST diversity — light shape pressure
```

These are guesses. The first cheap-path run (Tink 1, §10) is the
coefficient-calibration pass; values will be tuned empirically.
The **coefficient-sensitivity audit** (§7.1) is the honesty
mechanism for the fact that starting values are not principled.

**Pareto-front promotion.** The top-K promoted set is the
non-dominated frontier on a pinned **substrate-value triple**:

```
  (1 − basis_projection_score)   [novelty]
  affordance_gain_normalized      [usefulness]
  reconstructability              [faithfulness]
```

Fit and simplicity are in the aggregate scalar (via α, β); including
them in the Pareto-front would correlate it with the scalar ranking
and defeat the purpose. The Pareto-front is **orthogonal** to the
scalar's fit-and-simplicity emphasis: it surfaces candidates that
might lose on overall compression but win on a specific
substrate-value axis. A candidate dominated on all three of
`(novelty, usefulness, faithfulness)` is not substrate-interesting
regardless of MDL; a candidate non-dominated on ≥ 1 is retained for
audit. This is the structural answer to "F011-shaped findings that
don't compress well but reveal real structure" that a pure-MDL
approach would lose.

Alternative triples are declarable per-run (e.g.,
`(novelty, residual_structure, reconstructability)` for
phase-transition-style discovery). The choice is a SIGNATURE field.

### 4.5 AXIS_CLASS niches + residual channel + auto-descriptor proposal

MAP-Elites — the quality-diversity evolutionary algorithm —
maintains an archive of candidates indexed by behavioral
descriptors, returning the fittest candidate per descriptor cell.
The descriptor choice is non-trivial. A naive descriptor set
imposes a prior about what kinds of transformations exist.

The discipline: the niche taxonomy is drawn from the substrate's
existing controlled vocabulary. Prometheus maintains `AXIS_CLASS@v1`,
a ten-value taxonomy of coordinate types (`family_level`,
`magnitude`, `ordinal`, `categorical`, `stratification`,
`preprocessing`, `null_model`, `scorer`, `joint`, `transformation`).
The MAP-Elites archive indexes on these values. If a niche
dimension the generator needs is not covered by `AXIS_CLASS`, the
substrate's taxonomy is extended — the generator does not maintain
a parallel taxonomy.

**Residual channel.** Candidates that don't embed cleanly in any
declared cell are not discarded or force-fit. They enter a residual
channel, clustered by (tree edit distance) × (MDL similarity) ×
(atom-usage Jaccard). Clusters above a size threshold are
**auto-proposed as descriptors** with a quantitative stability test:

1. For each cluster of size ≥ 5, fit a simple classifier
   distinguishing cluster members from declared-cell members.
2. If classifier separation accuracy ≥ 0.8, the decision boundary
   defines a candidate descriptor `d_new`.
3. Re-run MAP-Elites with `map_axes = existing ∪ {d_new}`. If the
   new axis produces a cell with stable occupancy (≥ 3 candidates
   across independent seeds), existing cells stay stable, and
   anchor rediscovery is not degraded, the descriptor is a
   validated `AXIS_CLASS` extension candidate.
4. Human review still gates actual `AXIS_CLASS@v2` promotion; the
   instrument surfaces a quantitative proposal with a stability
   record.

This is the v2 upgrade on v1's residual channel. v1 stopped at
"cluster and surface for human review"; v2 machine-proposes
descriptors with evidence, letting the substrate's taxonomy evolve
at the speed of generator work rather than at the speed of human
review cycles.

**Out-of-MAP mass as first-class signal.** The per-run report
includes:
- `out_of_map_fraction` — density of the residual channel
- `out_of_map_clusters` — top-K residual clusters with exemplars
- `proposed_descriptors` — auto-proposed descriptors with stability
  test records

An empty residual with a dense MAP is a warning (tight
reward-signal capture on declared niches), not a pass.

### 4.6 Calibration — encoding-perturbation + cross-dataset

The MDL objective optimizes whatever the grammar makes cheap. A
scorer whose top-K candidates change under encoding perturbation
is measuring syntax, not structure. A scorer whose candidates work
on one dataset but not another is measuring cohort artifact, not
substrate-legible structure. Two complementary calibration
protocols, both required for shelf promotion:

**Encoding-perturbation protocol** (retained from v1):

- **Ordering invariance.** Under `±20%` perturbation to each
  operator cost in isolation, the top-10 candidate ordering by
  Kendall's τ against the base encoding must have
  `τ ≥ 0.8` for at least `(k − 1)/k` of operator perturbations.
- **Margin stability.** For each anchor in the top-N, the ratio
  `margin_perturbed / margin_base` lies in `[0.5, 2.0]` under
  perturbation. Collapse indicates the anchor won by rounding
  error.
- **Null-encoding baseline.** A random grammar with shuffled atom
  names and operator symbols should place zero anchors at top-K.
  If it places any, the statistic is a property of the data shape,
  not the grammar's calibration.

**Cross-dataset protocol** (new in v2, per James 3.3 critique):

Every production run executes on **≥ 2 datasets**:
- Primary: `Q_EC_R0_D5@v1` (LMFDB rank-0 EC, conductor `[10⁵, 10⁶)`,
  n = 559,386).
- Secondary (at least one): `Q_EC_R0_D4@v0` (smaller conductor
  range, tests conductor-scaling robustness) or `Q_EC_R0_D6@v0`
  (larger range) or `Q_EC_R2_D5@v0` (rank 2 at same range, tests
  rank-class-specificity).

Per-candidate consistency metric:

```
consistency_score = 1 − |agg_primary − agg_secondary| / max(agg_primary, agg_secondary)
```

Thresholds: `≥ 0.9` robust; `[0.7, 0.9)` partial flag; `< 0.7`
dataset-specific (penalize or retain only conditionally).
Per-axis decomposition is reported separately — a candidate with
consistent `basis_projection_score` but varying `affordance_gain`
is informative, not disqualifying.

**Calibration battery.** Before any candidate without a theorem
tag is considered, the instrument must rediscover a battery of
known-true structure:

| Anchor | Target expression | Severity | Expected niche |
|---|---|---|---|
| F003 | `(−1)^rank = root_number` (BSD parity) | Level 4 identity | `categorical × categorical` |
| F004 | `|a_p| ≤ 2√p` (Hasse) | Level 4 identity | `ordinal × magnitude` |
| F002 | Mazur torsion classification | Level 4 identity | `categorical` |
| F008 | Scholz reflection ratio ≈ 3 | Level 4 identity | `magnitude × categorical` |

Pass criterion: every in-grammar anchor lands in its expected niche
at top-N% MDL within the first K candidates (proposal: K = 1000,
N = top 5%).

**Calibration Gate 2 (hard rejection):** if
`frac_anchors_recovered = 0` for in-grammar anchors, all non-anchor
outputs are untrustworthy. This is the one case where continuous
pressure cannot fix the problem: a broken scorer's "less-bad"
candidates are still broken. Partial recovery (e.g., 3/4 anchors)
is a δ-penalty, not a rejection — the instrument can still be
informative, with its partial calibration declared.

A fifth calibration test lives in the red-team regime. With
`lineage_tags = disabled`, the instrument should reproduce F043 in
top-20 MDL on rank-0 data. This is not a bug to fix; it is a
demonstration that the gate works when enabled, and that the known
failure mode is within the grammar's reach.

---

## 5. Reference instrument — scorer signature and artifacts

The instrument's external contract:

```
input:
  dataset_primary:      pinned dataset symbol (e.g., Q_EC_R0_D5@v1)
  dataset_secondary:    pinned dataset symbol for cross-dataset check
  grammar:              (atoms, operators, max_depth, lineage_tags,
                        identity_basis)
  mdl_coefficients:     (α, β, γ, δ, ε, ζ, η, θ)  — eight axes
  pareto_triple:        axis names for Pareto-front promotion
                        default: (basis_projection, affordance_gain,
                                  reconstructability)
  map_axes:             subset of AXIS_CLASS values defining niches
  affordance_types:     list of ≤ 7 affordance measurements
  probe_set:            pinned downstream models for affordance gain
  iteration_budget:     int  — GP generations × population
  seed:                 int  — GP RNG seed

output (per candidate past gates, per dataset):
  (expression_ast,
   aggregate_score,
   per_axis_scores:           dict of eight axis values
   pareto_non_dominated_on:   list of axis names
   preserves_declared:        list[property]
   destroys_declared:         list[property]
   affordances_measured:      dict of affordance type → (score, null_baseline)
   map_cell_or_residual:      AXIS_CLASS cell or "residual"
   signature)                 full SIGNATURE JSON

per-run audit artifacts (required for shelf promotion):
  encoding_perturbation_matrix   Kendall's τ per operator
  margin_stability_matrix        margin ratios per anchor × perturbation
  null_encoding_top_K            random-grammar baseline
  coefficient_sensitivity_matrix Pareto-front composition under ±20%
                                 perturbation on each of α...θ
  out_of_map_fraction            residual-channel density
  out_of_map_clusters            top-N residual clusters + exemplars
  proposed_descriptors           auto-proposed AXIS_CLASS candidates
                                 with stability test records
  cross_dataset_consistency      per-candidate × per-axis
                                 consistency_score
```

Reproducibility: all scoring parameters (eight coefficients,
sub-thresholds, kernel bandwidths, probe set, inverse-model choice,
replay-buffer seed, Pareto-triple axes, affordance-type list) are
declared in SIGNATURE; two runs with identical parameters on
identical data produce byte-identical rankings. Non-determinism
lives in an explicit seed. This aligns with the substrate's
idempotence mandate (`long_term_architecture.md §2.1`).

---

## 6. Calibration-first runs — the go/no-go gate before novelty

Before any candidate without a theorem tag enters the promoted set,
the instrument runs its calibration battery (§4.6). The calibration
is not a one-time qualifier; it is executed at the start of every
production run and its pass record is a SIGNATURE field.

Expected behavior on Tink 1 (F003 rediscovery with minimal grammar):

- Grammar: `atoms = {rank, root_number}`, operators =
  `{=, ·, ^, (−1)}`, depth ≤ 4.
- Dataset (primary + secondary): `Q_EC_R0_D5@v1` and
  `Q_EC_R0_D4@v0`.
- Expected output: `(−1)^rank = root_number` lands top-10 on
  aggregate score within 1000 candidates on both datasets.
- Cross-dataset consistency should be `≥ 0.95` on all axes (an
  identity is dataset-independent by construction).
- Calibration Gate 2 PASSes; all other calibration artifacts
  present.

Failure diagnostics:

- Anchor reaches MAP but at low aggregate rank → coefficient weights
  wrong; adjust and re-run.
- Anchor not in any niche → taxonomy gap; surface as auto-descriptor
  proposal.
- Anchor discovered in wrong algebraic form → grammar lineage tag
  incomplete; audit Layer A.
- Anchor in-grammar but not found within K → search operators too
  weak, or the anchor does not live where expected; document as
  terrain data.
- Calibration Gate 2 FAILs → scorer is miscalibrated; all
  non-anchor candidates from this run are discarded; investigate
  before proceeding.

---

## 7. Failure mode declaration (v2)

The instrument's reach is bounded. Declaring the bound up front is
the discipline.

### 7.1 Expected false positives (continuous-metric analogs)

| Failure mode | Mechanism | Guard | Residual risk |
|---|---|---|---|
| Non-linear identity couplings | Candidate lies in the non-linear span of the identity basis (multiplicative, compositional, monotone) | §4.3 multi-kernel `basis_projection_score = max(R²_lin, R²_kern, MI_norm)` | A true rearrangement in a form none of the three measures captures; v3 upgrade = symbolic canonicalization |
| Incomplete identity basis | A candidate "passes" because the relevant identity was never encoded | Per-run distribution of `basis_projection_score`; histogram bimodal-at-zero signals thin basis | Silent false negatives when entire identity families are missing; mitigation = cross-dataset consistency (§4.6) |
| Grammar-advantaged forms | MDL prefers whatever the grammar makes cheap | Encoding-perturbation protocol (§4.6) | Structural bias the perturbation set doesn't cover (atom-inclusion bias, depth-limit bias); partial mitigation = cross-grammar test |
| Calibration-mimicking combinators | Expression numerically matches anchors on one dataset without being the same structure | Cross-dataset consistency metric; flag `consistency_score < 0.7` | Two-dataset coincidence; mitigation = third dataset or null-protocol audit |
| Reward-signal capture on declared niches | MAP-Elites converges tightly on `AXIS_CLASS` cells; "full MAP" misread as success | Residual channel + auto-descriptor stability test | Dense MAP with empty residual is ambiguous — treated as warning, not pass |
| Anchor-shaped artifacts | Grammar's atoms implicitly encode the anchor | Null-encoding baseline (§4.6) | Grammar whose atoms individually look generic but whose product includes anchor structure; mitigation = v3 cross-grammar convergence |
| Degenerate projections via simplicity pressure | High-simplicity transformations destroying everything (`σ(x) = 0`) score well on α + β | Reconstructability axis η imposes inverse-model floor | Transformations with high affordance for narrow task but low reconstructability are surfaced as task-specific, not rejected |
| GP search collapse to local shape optima | Tree-shape bias; diversity in output but not in input | AST-diversity penalty θ + replay buffer | Replay buffer is per-run; cross-run structural bias accumulates and is not caught at per-run level |
| Dataset-specific affordance inflation | `affordance_gain` high on one dataset but not others, masking scorer bias | Cross-dataset decomposes affordances; minimum used in aggregate | Cohort artifact persisting across both calibration datasets but failing on a third; mitigation = ≥ 3 datasets for v1 shelf |
| Pareto-front dominance bias | The "non-dominated" set depends on which axes are in the triple; coefficient choice biases which structure survives | Coefficient-sensitivity audit — run at 3 coefficient settings; report Pareto-front stability | Underlying coefficient choice is itself a coordinate decision (meta-Pattern 6); surfaces as recurring failure at the scoring-hyperparameter layer |

### 7.2 Structural blind spots

These are not tuning issues. No amount of calibration eliminates
them; they define the instrument's horizon.

- **Structure requiring atoms outside the grammar.** Any invariant
  expressible only via atoms not included is invisible. A null
  result from the instrument is not evidence of structural absence
  — only that the grammar-covered form is absent.
- **Higher-level / analytic / categorical structure.** Automorphic
  lifts, Galois representations as functors, L-function analytic
  continuation — relations between object classes rather than
  expressions over atomic invariants of one object. F001
  modularity (elliptic curve ↔ modular form) is probably in this
  class.
- **Conditional / existential / quantified claims.** MDL does not
  naturally encode quantifiers. Candidates of this shape are
  silently unrepresented. No coverage is claimed.
- **Non-arithmetic structure native to the object class but not
  expressible in the atom set.** Analytic, topological,
  measure-theoretic. F011's zero-spacing variance deficit lives in
  spectral statistics; this generator will not touch it without a
  separate spectral-atom grammar.
- **Unbounded depth.** The grammar pins `max_depth`. Expressions
  deeper than the limit are invisible.
- **Cross-object structure.** The grammar operates per-object.
  Claims of the form "property of X is controlled by property of
  Y" for distinct objects are out of scope.
- **Structure requiring non-linear basis extensions the v2
  instrument can't detect.** Even with kernel R² and MI, some
  functional-span relations escape. Symbolic canonicalization is
  a v3 upgrade path.

### 7.3 What the SIGNATURE guarantees

A candidate coming out of the instrument carries:

- The grammar spec (atoms + operators + depth + lineage tags)
  active at generation time.
- The identity basis used for the basis-projection check.
- The calibration-battery pass record.
- The encoding-perturbation artifacts.
- The `preserves` / `destroys` / `affordances` declaration.
- The residual-channel state and auto-descriptor proposals.
- **Seven-axis score breakdown.**
- **Cross-dataset consistency metrics** per-axis.
- **Pareto-front position** (which axes the candidate is
  non-dominated on).
- **Coefficient-sensitivity record** (how the candidate's rank
  changes under ±20% perturbation of each scorer coefficient).

The SIGNATURE does not carry "this is the deepest structure in the
data." It carries "this is a coordinate transformation that
passed a specific set of gates, scored continuously on seven
axes, and held position on the Pareto-front of substrate-value
for grammar G, data Q, coefficients C." A future reader decides
whether those gates and coefficients were appropriate for their
question, and can re-run the same discipline to verify.

---

## 8. Relationship to prior work

### 8.1 Symbol regression and equation discovery

AI-Feynman (Udrescu & Tegmark, 2020), PySR (Cranmer, 2023), Deep
Symbolic Regression (Petersen et al., 2021), SINDy (Brunton et al.,
2016), DreamCoder (Ellis et al., 2021).

All score candidates by fit-to-data under some complexity penalty,
and all inherit the conflations in §1.1. None enforces a grammar-
time lineage gate; none requires a declared
`preserves`/`destroys`/`affordances` schema; none has a calibration
protocol controlling for encoding bias. Structure Hunter's
contribution is not the core loop (standard GP + MAP-Elites + MDL)
but the discipline layers wrapped around it and the continuous
multi-axis scoring that replaces the usual scalar fit-plus-simplicity
objective.

The honest comparison: those tools work for classical physics data
where the ground-truth equation space is known and the grammar is
well-matched. For open empirical domains — number theory,
combinatorics, graph theory — where the identity basis is richer
and less well-bounded, the continuous lineage and multi-axis
calibration gates described here are a necessary addition.

### 8.2 MDL, Kolmogorov complexity, and the description-length tradition

Rissanen (1978, 1983), Solomonoff (1964), Hutter (2005), Grünwald
(2007). Structure Hunter uses MDL as *one* scoring axis among seven
(not the sole objective) and inherits its pathologies
(encoding-dependence, Turing-uncomputability, universal-distribution
choice). The encoding-perturbation calibration (§4.6) is a
practical response to encoding-dependence. The seven-axis
Pareto-front (§4.4) is the structural response to the subtler
critique (from Grünwald and from James's fragility 2E) that MDL
as sole proxy misses sparse / threshold / phase-transition
structure.

### 8.3 Quality-diversity and MAP-Elites

MAP-Elites (Mouret & Clune, 2015) and descendants (CVT-MAP-Elites,
SAIL, QDax). Structure Hunter's contribution is not the algorithm
but: (a) the behavioral grid draws from an external controlled
vocabulary (`AXIS_CLASS@v1`); (b) a residual channel for
out-of-grid mass; (c) **auto-descriptor proposal** from residual
clusters — v2's closing of the ontology-lock-in failure mode James
identified. Without (a)–(c) MAP-Elites converges on the grid it
was given and mistakes grid-saturation for success.

### 8.4 Automated conjecturing in mathematics

Fajtlowicz's Graffiti (1986) for graph-theoretic conjectures;
Larson's GraphTheory package; Schmidhuber's OOPS; the Ramanujan
Machine (Raayoni et al., 2021) for candidate integer-relation
formulae for mathematical constants.

These systems share Structure Hunter's commitment to discipline
(Graffiti's conjectures were designed to be falsifiable by the
same pipeline that produced them; the Ramanujan Machine publishes
candidates, not theorems). They differ in addressing the
claim-output problem directly (ship claim-shaped candidates, let
proof infrastructure arbitrate) rather than redefining the output
as coordinate transformations with affordance measurements.
Structure Hunter's Framing B + affordances is the key
distinguishing move.

### 8.5 Within Prometheus

Within the substrate, Structure Hunter is a sibling of:

- **`gen_11`** — coordinate-system invention as an axis-space
  producer reading tensor demand signals (VACUUM / EXHAUSTION).
  Structure Hunter operates over a grammar on pinned data. The
  output overlaps (candidate P-IDs); the input differs. Merger
  vs. sibling status is an explicit v3 question.
- **`TT_APPROX_MAP@v0`** (auditor, 2026-04-24) — MAP-Elites
  archive over tensor-train approximations with its own
  calibration anchors and a decomposition-lineage analog of
  Pattern 30. Structure Hunter is the arithmetic-grammar cousin;
  a cross-substrate comparison of the two archives is a gen_09
  candidate.
- **Definition DAG** — substrate primitive recording mathematical
  concepts + algebraic dependence. Phase 0 is the hard
  prerequisite for Structure Hunter's full-path grammar
  specification.
- **Pattern 30 / null_protocol_v1.1** — graded severity for
  algebraic-identity coupling, and the five-class null-protocol
  taxonomy. Structure Hunter reuses these wholesale; the novelty
  is making Pattern 30 application a continuous grammar-time
  scoring input, not a post-evaluation filter or a binary gate.

---

## 9. Open questions

The following are deferred for external review, internal decision,
or empirical measurement. None is a blocker for the cheap-path
starting experiment (§11).

1. **Merger with `gen_11`.** Shared output shape (candidate P-IDs);
   different input (grammar + data vs. tensor demand signals).
   The cheap-path tinkering in §11 should inform this before
   commitment.
2. **Target class.** LMFDB rank-0 elliptic curves
   (`Q_EC_R0_D5@v1`) is the recommended starting target. Alternative
   targets (integer sequences for OEIS-style calibration; number
   fields; graph invariants) were considered and scored lower on
   substrate-alignment or calibration-anchor availability.
3. **Grammar atom set + identity basis.** The LMFDB-EC atom set in
   Appendix A is illustrative. Production use requires a Definition
   DAG Phase-0 extended seed (~60–80 nodes) and a materialized
   identity basis covering BSD identity, Hasse bound, Mazur
   torsion, Scholz reflection, modularity trace, Szpiro–Faltings
   definitional coupling, and Euler-product identities.
4. **Playground-tier home.** Early tinkering can live in a
   `zoo/`-tier parallel substrate with no tensor migration (the
   `TT_APPROX_MAP` precedent), or in mainline under full discipline
   from day 1. The cheap-path assumes `zoo/`.
5. **Non-linear basis-extension methods.** `basis_projection_score`
   combines linear R², kernel R², and KSG mutual information. A
   true rearrangement expressed in a form none of the three
   captures will be missed. Upgrade paths: symbolic
   canonicalization via CAS; kernel tuning per domain. Not
   obviously favorable at v0.
6. **Cross-object structure.** The grammar operates per-object.
   Multi-object grammars (e.g., expressing "property of Y-curve
   is controlled by property of X-curve") require semantic
   extensions scoped for v3+.
7. **Quantifier-class claims.** Existential and universal claims
   are not representable in MDL framework. A v3 extension would
   require a separate scoring pathway for bounded-existence
   claims on curated datasets, interacting with null-protocol
   Class 4 in ways not yet scoped.
8. **Pareto-front axes.** Default triple is
   `(1 − basis_projection, affordance_gain, reconstructability)`.
   Alternatives are declarable per-run. The triple choice is
   load-bearing — it determines which substrate-value axes drive
   promotion. The default prioritizes "novel, useful, faithful";
   phase-transition-hunting runs would select a different triple.

---

## 10. What a successful first run looks like

The cheapest useful experiment — "Tink 2" in the architecture doc
— is to **deliberately reproduce F043 under a disabled lineage
gate** (with both Layer A atom-tags AND Layer B basis-projection
turned off). The value of this experiment is not a discovery; it
is a concrete demonstration that the instrument's gate mechanism
is doing real work.

Setup: minimal grammar with BSD-ingredient atoms (`log Sha`,
`log Ω`, `log ∏c_p`, `log|Tor|`, `log L`), operators (`+`, `−`,
`corr`, `log`), depth ≤ 3, lineage tags disabled, basis-projection
coefficient `γ = 0`. Datasets: `Q_EC_R0_D5@v1` + `Q_EC_R0_D4@v0`.
Iteration budget: 1000 candidates.

Expected output:

- `corr(log|Sha|, log(Ω·∏c_p))` appears in the top-10 aggregate
  score on both datasets, with a large `|z|` statistic and a
  block-shuffle-passing null.
- Cross-dataset consistency for this candidate is `≥ 0.95` (the
  identity holds identically on both cohorts).
- Several rearranged forms of the same identity appear alongside
  it in the top-20.
- `basis_projection_score` for these candidates, if computed even
  with `γ = 0` (i.e., measured but not penalized), is `≥ 0.95` —
  the measurement fires even when the scoring doesn't.
- Pareto-front on `(1 − basis_projection, affordance_gain,
  reconstructability)` places these candidates near the origin
  on the novelty axis (low novelty, near the basis) — **they do
  not appear on the Pareto front**, even though they dominate
  the aggregate scalar.

**This is the payoff.** The aggregate scalar (fit-dominated)
rewards F043-shape candidates; the Pareto-front (novelty-aware)
rejects them. The two disagree, and the disagreement is the
evidence that the seven-axis discipline does something a single
scalar cannot.

Re-run with `γ = 5.0` (full lineage coefficient): the top-20
aggregate is cleared of identity restatements. The Pareto-front
looks roughly the same (it was already clearing them). The
contrast between the two runs is the second piece of evidence:
γ materially changes the aggregate but only marginally affects
Pareto-promotion. The seven-axis + Pareto architecture is more
robust to coefficient choice than the aggregate alone.

A successful full-path run of "Tink 3" (empty-niche scan on a
full BSD-lineage-tagged grammar) would surface:

- Candidate P-IDs per `AXIS_CLASS` niche, ranked by Pareto
  position, each with declared `preserves` / `destroys` /
  `affordances`.
- A list of niches with density zero (VACUUM signals: coordinate
  gaps the substrate's P-ID catalog does not currently fill).
- A list of residual-channel clusters with auto-proposed
  descriptors and stability test records.
- Cross-dataset consistency scores per candidate per axis.
- Coefficient-sensitivity matrix showing which candidates are
  stable under `±20%` scorer-coefficient perturbation.

None of this is a finding. All are candidates for human or
`gen_11`-style review. The substrate's existing promotion
infrastructure arbitrates.

---

## 11. Roadmap

### 11.1 Cheap-path (recommended start, ~1.5–2 ticks)

- **Location:** `zoo/conjecture_gp/` (playground-tier; verdicts
  do not migrate to the landscape tensor).
- **Grammar:** hand-built BSD-ingredient atom set + minimal
  operator suite. ~50 LOC.
- **Search:** naive GP loop (tournament selection, subtree
  crossover, point mutation). ~100 LOC.
- **Scoring:** seven-axis scorer with provisional default
  coefficients (§4.4). Layer A lineage enabled; Layer B
  basis-projection via `max(R²_lin, R²_kern, MI_norm)` using
  scikit-learn kernel ridge + KSG MI. ~200 LOC.
- **Affordances:** `linear_probe_gain`, `variance_reduction`,
  and `rank_correlation_gain` only (three of seven). ~50 LOC.
- **Calibration:** encoding-perturbation ordering test + one
  null-encoding baseline run + one secondary dataset. No full
  matrices at this tier.
- **Output:** two run reports (Tink 1 PASS/FAIL anchor
  rediscovery; Tink 2 F043 reproduction or not), posted to
  decisions queue for review.

**Budget:** ~1.5 ticks implementation (up from ~1 tick for v1 due
to expanded scorer), ~0.5 tick run time. Total ~2 ticks.

### 11.2 Full-path (gated on cheap-path informative results)

- **Definition DAG Phase 0 extended seed** (~60–80 nodes; 3–5
  ticks).
- **Grammar-time Pattern 30 + multi-kernel basis-projection in
  `harmonia/sweeps/pattern_30.py`** (2 ticks — upgraded from
  v1's linear-only estimate because kernel + MI implementations
  add work).
- **GP + MAP-Elites + full seven-axis scoring + encoding-
  perturbation + cross-dataset + auto-descriptor proposal in
  `harmonia/runners/conjecture_gp.py`** (3–4 ticks, up from
  v1's 2–3 because residual-structure, reconstructability,
  AST-diversity, cross-dataset, and auto-descriptor are new).
- **Full calibration battery with required audit artifacts
  (including coefficient-sensitivity matrix)** (1–2 ticks).
- **`gen_12` Agora prompt at
  `docs/prompts/gen_12_conjecture_generator.md`** (½ tick).
- **Graduation** to shelf entry `CONJECTURE_GENERATOR@v1` in
  `methodology_toolkit.md`.

**Budget:** ~10–13 ticks total (up from v1's 7–11), gated on
cheap-path producing evidence that the seven-axis discipline
does what it claims.

### 11.3 Deferred / v3 roadmap

A detailed v3 roadmap (2026-04-24, absorbing James's third-round
critique) is specified at
`harmonia/memory/architecture/conjecture_generator_v3_roadmap.md`.
Summary of the five v3 priorities:

1. **Typed Relational Grammar** — closes the cross-object blind spot
   (§7.2). Atoms extend to arity > 1; new affordance
   `cross_domain_projection_gain`. Makes F001 modularity + F009
   Serre-Mazur reachable as calibration anchors. Budget: 7–11 ticks.
2. **CAS symbolic canonicalization** — adds Layer C (SymPy) before
   the empirical Layer B multi-kernel check. Exact-rearrangement
   detection back to the logical layer; kernel + MI reserved for
   genuinely muddy functional overlaps. Budget: 2–3 ticks.
3. **Ensemble Pareto Promotion** — 3 parallel MAP-Elites
   populations with perturbed coefficients (novelty-biased,
   faithfulness-biased, fit-biased). Shelf promotion requires
   non-domination on ≥ 2 of 3 ensemble Pareto-fronts. Converts
   coefficient-sensitivity from audit artifact to selection
   pressure. Budget: 1–2 ticks.
4. **`gen_11` merger via demand-driven input** — Structure Hunter
   absorbs `gen_11` by ingesting `VACUUM` / `EXHAUSTION` demand
   signals from the tensor. Atom priors + MAP-cell seed priors +
   δ boost for vacuum-filling candidates. Standalone `gen_11`
   deprecated on merger. Budget: 2–3 ticks.
5. **Latent-trace reconstructability** — η becomes a composite
   `η_composite = 0.7·η_inverse + 0.3·η_trace` where η_trace is
   derived from AST execution-graph information density and
   reversibility. Composes with the Sovereign Harvest engine's
   reasoning-trace taxonomy. Budget: 1–2 ticks.

**Total v3 budget: 13–21 ticks additional to v2's 10–13 ticks
full-path.** The v3 roadmap doc details dependency tiers (pre-Tink
spec, post-Tink 2, post-Tink 3) and explicit conflicts between
items (ensemble compute cost, demand-seed-bias vs. novelty-seeking,
TRG grammar blowup).

**v3 commitment is gated on v2 empirical validation.** If Tink 2
does not produce the predicted aggregate-scalar / Pareto-front
disagreement on F043, v2 architecture is wrong and v3 does not
proceed; reset to v2 critique.

Additional items deferred beyond v3:
- Quantifier-class claim extension (§9.7).
- Port to number-field target class (Scholz reflection +
  Serre–Mazur lineage) — candidate for v3 TRG's second
  calibration cohort.
- Auto-descriptor promotion pathway into `AXIS_CLASS@v2`.
- Unbounded AST depth; non-arithmetic atom grammars (spectral,
  topological).

---

## 12. Scope disclaimer

This document describes an instrument. It does not describe a set
of findings obtained via the instrument, because the instrument
has not been run.

Under the Prometheus charter, the instrument described here is
*not* a conjecture generator in the sense of producing paper-ready
mathematical claims. It is a producer of candidate coordinate
transformations whose shelf-promotion requires passing a declared
battery of continuous scoring axes and two categorical gates. Any
future claim-shaped output (a "conjecture") would arise as a
derived artifact when a candidate's declared affordances cross a
threshold and the implied hypothesis passes the substrate's
null-protocol arbitration — not as a primary output the
instrument unilaterally emits.

The authors of this paper commit, as a standing discipline, to
**not** publishing outputs of this instrument as novel
mathematical findings outside the substrate's retraction-enabled
channels. The substrate's one prior retraction (F043, 2026-04-19)
is the anchor case for why this commitment exists.

---

## Appendix A — Illustrative grammar (LMFDB rank-0 EC)

The atom set below is first-pass. Production use requires the
Definition DAG Phase-0 extended seed for complete lineage
closure.

| Atom | Type | Algebraic closure | `AXIS_CLASS` |
|---|---|---|---|
| `N` (conductor) | magnitude | denominator in Szpiro; co-factor of Δ | magnitude |
| `a_p` (Frobenius trace at prime p) | ordinal | Hasse bound `|a_p| ≤ 2√p` | ordinal |
| `rank` | categorical | BSD parity identity | categorical |
| `root_number` (±1) | categorical | BSD parity identity | categorical |
| `|Δ|` (discriminant abs value) | magnitude | linked to N via bad-prime structure | magnitude |
| `Ω` (real period) | magnitude | BSD-ingredient (primary) | magnitude |
| `|Sha|` (analytic Sha, rank-0) | ordinal | BSD-ingredient (primary) | ordinal |
| `∏ c_p` (Tamagawa product) | magnitude | BSD-ingredient (primary) | magnitude |
| `|Tor|` | categorical | BSD-ingredient + Mazur classification | categorical |
| `j` (j-invariant) | magnitude | CM classification | magnitude |
| `L(E, 1)` | magnitude | BSD-ingredient (primary) | magnitude |

Operators and their lineage propagation:

| Operator | Input types | Output type | Closure propagation |
|---|---|---|---|
| `+`, `−` | (magnitude, magnitude) | magnitude | union of closures |
| `×`, `÷` | (any, any) | magnitude | union of closures |
| `log`, `exp` | (magnitude) | magnitude | preserves closure |
| `^` | (any, integer literal) | magnitude | preserves closure |
| `=`, `≤` as output | (any, any) | **FORBIDDEN** | Gate 1 (§4.1) |
| `corr` as output | (magnitude-vector, magnitude-vector) | scalar | **FORBIDDEN** (Gate 1) |
| `[·]` (Iverson bracket) as object-level feature | (boolean expression) | `{0, 1}` | allowed (transformation, not claim) |
| `stratify_by(V)` | (object-feature, V) | stratification | promotes to null-protocol Class 2 |
| `per_rank(f)` | (scorer) | scorer | conditional on rank |

Identity basis to be materialized over `Q_EC_R0_D5@v1`:

1. `log L = log Ω + log ∏c_p + log|Sha| − 2 log|Tor|` (BSD at
   rank 0, since `Reg = 1`)
2. `|a_p| ≤ 2√p` (Hasse)
3. `|Tor| ∈ {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12} ∪ {2k : k ∈ 1..4}`
   (Mazur)
4. `log|Δ| ~ log N + C` (bad-prime bounded contribution, weak
   linear coupling — produces `R²_lin < R²_kern` patterns)
5. `a_p(E) = a_p(f_E)` for the modular form `f_E` (modularity;
   cross-object, partially out of grammar)

## Appendix B — Reference compositions with substrate primitives

| Substrate primitive | How Structure Hunter uses it |
|---|---|
| `AXIS_CLASS@v1` | MAP-Elites niche taxonomy (§4.5) |
| `PATTERN_30@v1` | Atom-tag lineage layer A (§4.3) |
| `null_protocol_v1.1` | Framing-A derived artifact arbitration (§4.2) |
| `SHADOWS_ON_WALL@v1` | Per-candidate lens count in SIGNATURE |
| `VACUUM@v1` | Residual-channel diagnostic + MAP-level vacuum signal (§4.5) |
| `MULTI_PERSPECTIVE_ATTACK@v1` | Cross-grammar convergence test (deferred to v3) |
| `SIGNATURE@v2` | Candidate output schema, extended to carry preserves/destroys/affordances + seven-axis breakdown + Pareto-front position + coefficient-sensitivity matrix |
| `MDL_SCORER@v1` | Scoring axis β backbone (§4.4) |
| `Q_EC_R0_D5@v1` | Primary calibration dataset |
| `Q_EC_R0_D4@v0` / `Q_EC_R0_D6@v0` / `Q_EC_R2_D5@v0` | Secondary cross-dataset checks (§4.6) |
| `TT_APPROX_MAP@v0` | Methodological cousin; cross-substrate MAP comparison is a gen_09 target |
| Definition DAG | Grammar spec source (prerequisite for full-path §11.2) |

## Appendix C — v1 → v2 delta summary

For readers familiar with v1 of this paper, the substantive
changes in v2:

| v1 position | v2 position | Reason |
|---|---|---|
| Four discipline "principles," each a binary gate | Two categorical gates + seven continuous scoring axes | James 2A/2C: binary gates lose continuous information; moves the discipline into the score rather than out of it |
| `preserves` / `destroys` required; affordances forbidden | `preserves` / `destroys` / `affordances` required (affordances are measurements, not claims) | James 2A: no-claims rule over-constrains; affordances bridge transformation-level output to claim-relevant utility without smuggling |
| `basis_projection` via linear R², binary threshold `R² ≥ 0.9` | `basis_projection_score = max(R²_lin, R²_kern, MI_norm)`, continuous, penalty via γ | James 2B: linear R² misses non-linear couplings; continuous score surfaces boundary cases |
| MAP-Elites residual channel, human-only descriptor promotion | Residual channel + auto-descriptor proposal with quantitative stability test | James 2D: ontology lock-in on `AXIS_CLASS`; let the system propose axes, gate human review |
| MDL scoring (α·L(expr) + β·L(data|expr)) with γ, δ hard gates | Seven-axis scoring with Pareto-front on `(1 − basis_projection, affordance_gain, reconstructability)` | James 2E: MDL misses sparse / threshold / phase-transition structure; multi-axis captures those explicitly |
| Cross-dataset validation mentioned but not first-class | Cross-dataset consistency required per-run, per-axis | James 3.3: make it the discipline, not the aspiration |
| No inverse-pressure axis | Reconstructability axis η | James 3.4: prevents degenerate projections that destroy too much |
| No search-bias axis | AST-diversity penalty θ + per-run replay buffer | James 3.5: input diversity complements MAP output diversity |
| Cheap-path ~1 tick; full path ~7–11 ticks | Cheap-path ~1.5–2 ticks; full path ~10–13 ticks | Expanded scorer adds work at both tiers |
| "Conjecture generator under algebraic-lineage + MDL constraints" | "Coordinate-system discovery engine defined by continuous measurement of structural independence and usefulness" | Bottom-line reframe from James: hard exclusion → continuous measurement |

---

## Provenance

- **Authors:** Harmonia_M2_sessionC (drafts + integration), James
  Craig (founding proposal + four-tension critique + five-fragility
  critique that produced v2), Harmonia_M2_sessionA (substrate-
  primitive context via `orbit_canonicalization` precedent),
  Harmonia_M2_auditor (methodological cousin `TT_APPROX_MAP@v0`).
- **Architecture source:** `harmonia/memory/architecture/conjecture_generator.md`
  v0.3.1 (2026-04-24), this whitepaper's internal companion.
- **Prior conversation:** Harmonia_M2_sessionC ↔ James, 2026-04-23
  / 2026-04-24, two rounds of substantial critique absorbed.
- **Anchor retraction:** F043 (analytic Sha × Tamagawa-Ω product
  correlation on rank-0 EC), retracted 2026-04-19 by external
  review. See `harmonia/memory/decisions_for_james.md` post-review
  entry.
- **Cross-substrate cousin:**
  `whitepaper_orbit_canonicalization.md` (Harmonia_M2_sessionA,
  2026-04-23) — adjacent substrate-primitive proposal for
  equivalence-class canonicalization in search.

## Status

**Incubation-stage, pre-implementation.** No code has been written
against this design. No outputs have been measured. The cheap-path
starting experiment (§11.1) is the proposed next move.

Critique welcome. The paper is designed to be falsifiable on
architecture grounds (seven continuous axes load-bearing? two
categorical gates principled?) before empirical grounds (does the
instrument produce anything?). Falsification at the architecture
layer is cheaper than building the instrument and measuring.

---

## Version history

- **v2** — 2026-04-24 — five-fragility critique from James
  absorbed; full propagation from architecture doc v0.3.1.
  Substantive changes detailed in Appendix C. Abstract rewritten.
  §4 restructured from four principles to one overview +
  five-subsection design. §5 scorer signature expanded to
  eight-axis + cross-dataset + coefficient-sensitivity artifacts.
  §6 + §7 updated for continuous-metric discipline. Roadmap
  budgets updated. Appendix C (v1 → v2 delta) added.
- **v1** — 2026-04-23 — initial whitepaper after the four-tension
  critique produced v0.2 of the architecture doc. Frames the
  problem, four design principles, calibration battery, failure-
  mode declaration, prior-art comparison, open questions, roadmap,
  scope disclaimer, illustrative grammar, substrate-primitive
  composition table.
