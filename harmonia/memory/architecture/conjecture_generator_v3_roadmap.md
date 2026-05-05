# Conjecture Generator — v3 Roadmap

**Status:** pre-implementation planning document. Companion to
`conjecture_generator.md` v0.3.1.
**Created:** 2026-04-24 — Harmonia_M2_sessionC, absorbing James's
third-round critique.
**Purpose:** enumerate five architectural extensions identified for v3
with specifications, dependency graph, and budgets; gate implementation
on v2 empirical validation.

---

## 0. Empirical gate — read this first

This roadmap assumes **Tink 2 (F043 reproduction under disabled
lineage) validates v2's core claim:** the aggregate scalar promotes
F043-shaped candidates while the Pareto-front on
`(1 − basis_projection, affordance_gain, reconstructability)` rejects
them. The disagreement between the two rankings is the load-bearing
evidence that v2's seven-axis + Pareto discipline does something a
single-scalar scorer cannot.

**If Tink 2 fails to produce this disagreement, this roadmap resets
rather than progresses.** The five v3 items below all assume v2's
discipline is empirically functional. A v2 that can't distinguish
F043 from genuine structure via its own Pareto-front is wrong at
the architecture level, and v3's extensions would compound the
wrongness rather than correct it.

Spec-writing can proceed ahead of Tink 2; implementation cannot.
This document is the spec.

---

## 1. Typed Relational Grammar — closing the cross-object blind spot

**Source:** James critique item 1 (2026-04-24) — "chasing the Langlands gap."

### 1.1 Problem

v2's grammar operates per-object by construction. Candidate
transformations take `f: Object → features`. Cross-object structure
— F001 modularity (elliptic curve `E` ↔ modular form `f_E`), the
Scholz–Davenport–Heilbronn reflection between number fields and
their mirror, the Langlands functoriality between Galois
representations and automorphic forms — is flagged in §7.2 as a
structural blind spot.

This scope limit is deliberate but increasingly costly. The
substrate's calibration anchors F001 (modularity) and F008 (Scholz)
and F009 (Serre+Mazur lineage) all live in the cross-object class;
an instrument that categorically cannot reach them leaves
foundational invariants outside its calibration battery.

### 1.2 Proposed extension

**Typed Relational Grammar (TRG).** Extend the grammar's type
system with object-class arguments so transformations can carry
arity > 1:

```
atoms:
  single-object atoms      f: Object_A → feature           (v2, unchanged)
  cross-object atoms       g: (Object_A, Object_B) → feature
  lift atoms               h: Object_A → Object_B          (maps one object class to another)

operators:
  unary                    arity 1 (v2, unchanged)
  binary                   arity 2, typed over object classes
  relational               binary that outputs a scalar (used in preserves/destroys/affordances,
                           forbidden as top-level output per Framing B Gate 1)
```

Expression trees gain a type-checking pass: an expression's root
output type must match the declared projection target
(`f: Object_A → features` or `f: (Object_A, Object_B) → features`),
and subtrees must match their operator's expected types. Mismatches
are Gate-1 type violations.

### 1.3 New affordance type

Add **`cross_domain_projection_gain`** to the affordance list (making
it 8 types):

```
cross_domain_projection_gain(σ_A: Object_A → features) :=
  L(Object_B | identity_basis_B) − L(Object_B | identity_basis_B ∪ σ_A(Object_A))
```

Operationally: does the transformation `σ_A` of class-`A` objects
reduce the description length of class-`B`'s established invariant
basis? If yes, `σ_A` carries cross-class information — it is the
functorial image of something.

This affordance is specifically designed to surface modularity-shape
candidates: a transform `σ(E)` of elliptic curves that reduces the
description length of modular-form Fourier coefficients is a
candidate for an `a_p`-level modularity observation.

### 1.4 Calibration anchors now reachable

With TRG + `cross_domain_projection_gain`, the calibration battery
extends:

| Anchor | v2 status | v3 status |
|---|---|---|
| F003 parity | reachable | reachable (unchanged) |
| F004 Hasse | reachable | reachable (unchanged) |
| F002 Mazur | reachable | reachable (unchanged) |
| F008 Scholz | reachable (single-object: NF ↔ dual NF, same class) | reachable + tighter (can now test reflection as a class-to-class lift) |
| **F001 modularity** | **out of grammar** | **reachable** as (EC, MF) → a_p match |
| **F009 Serre+Mazur** | **out of grammar** | **reachable** as (EC, Galois-rep) → image-pattern match |

Calibration battery expands from 4 in-grammar anchors to 6. F001
and F009 become go/no-go additions to the pass criterion.

### 1.5 Cost and risk

**Grammar size scales worse than linearly.** If the v2 grammar has
`k` single-object atoms, v3 TRG at arity ≤ 2 has roughly `k + k²`
atom candidates. Depth-bounded search over the expanded space may
need new diversity pressure to avoid search-time blowup.

**Dataset joinery.** Cross-object transformations require a joined
dataset: `EC × MF` at matching conductor. LMFDB has the join via
`lfunc_lfunctions`, but the grammar needs a pinned dataset symbol
for each cross-object pair of interest. Proposed new symbols:
`Q_EC_MF_R0@v0`, `Q_NF_dualNF_deg3@v0`, `Q_EC_GalRep@v0`.

**Over-reach hazard.** TRG opens the door to multi-object
expressions that look "discovery-shaped" but are really just
identity statements on the joined data. The basis-projection check
(§4.3) must be extended: the identity basis now includes the
joining relation itself (modularity theorem, Langlands
correspondence) as a materialized identity. Without this, TRG will
reinvent the modularity theorem as a "novel finding" on its first
run.

### 1.6 Budget

~7–11 ticks. Breakdown:
- 2–3 ticks: type-system extension in the grammar + type-checker
- 1 tick: new atom / operator declarations for BSD-ingredient + MF
  + Galois-rep atoms
- 2 ticks: `cross_domain_projection_gain` affordance scorer
- 1 tick: F001 + F009 calibration-anchor encodings
- 2 ticks: joined-dataset symbol pinning (`Q_EC_MF_R0@v0`,
  `Q_NF_dualNF@v0`)
- 1–2 ticks: integration testing with Tink 3 empty-niche scan on
  TRG grammar

### 1.7 v3 open questions on TRG

- Should arity be capped at 2, or allow 3+ for n-ary Langlands-shape
  observations? Start at 2; raise only if Tink-3 TRG shows arity-2
  saturating the signal space.
- Does Framing B Gate 1 extend correctly to relational output? A
  relational atom `corr(σ_A, σ_B)` as top-level output is a claim
  (forbidden); as a sub-expression inside a transformation is fine.
  The semantic rule "top-level output whose natural reading is an
  assertion of truth across the dataset" is still the correct
  boundary; TRG doesn't change the boundary, only the sub-expression
  space it protects.

---

## 2. CAS-Driven Symbolic Canonicalization — Layer C in basis-projection

**Source:** James critique item 2 (2026-04-24).

### 2.1 Problem

v2's `basis_projection_score = max(R²_lin, R²_kern, MI_norm)` is an
empirical stopgap for an algebraic truth. It catches:
- linear span (linear R²)
- non-linear regression-recoverable span (kernel R²)
- distributional-form couplings (MI)

It misses:
- exact rearrangements disguised by deep composition (e.g., a
  candidate `log(L·Tor²·Sha/∏c_p) − log Ω` is algebraically 0 by
  BSD but may evade kernel regression at finite sample size if
  numerical noise breaks rank)
- identities whose manifestation requires operator inversion
  (e.g., `exp(log X) = X` — empirically caught but symbolically
  obvious)
- multi-step algebraic simplifications the empirical estimators
  cannot perform in principle

These are rare but high-cost false negatives: a candidate that
looks novel empirically, passes basis-projection, passes
cross-dataset, AND is algebraically trivial.

### 2.2 Proposed extension

**Add Layer C — symbolic canonicalization — before Layer B.**

Pipeline (v3):

```
Candidate expression E
  ↓
Layer A: atom-tag lineage intersection (v2, unchanged)
  ↓
Layer C: CAS symbolic canonicalization (NEW in v3)
  ↓ if CAS can reduce (E − I_j) to exactly 0 for some I_j ∈ basis:
  ↓   basis_projection_score = 1.0 (hard-pinned); bypass Layer B
  ↓ else:
Layer B: continuous basis-projection max(R²_lin, R²_kern, MI_norm) (v2, unchanged)
  ↓
basis_projection_score reported in SIGNATURE
```

**CAS tooling choice:**
- **SymPy** for v3 initial implementation. Pure Python, embeds cleanly
  in the runner, handles the canonical forms we need (algebraic
  simplification, polynomial reduction, log/exp normalization).
- **Upgrade to SageMath or FLINT** is a v4 question. Benefits:
  richer simplification, Gröbner basis computation for multivariate
  polynomial ideals. Costs: heavier integration, Python-C bridge.
- **Not pursuing full proof assistants** (Lean, Coq) — out of scope.

### 2.3 Composition with v2 Layer A and Layer B

Layer A (atom-tag lineage) remains the cheapest filter and runs
first. Layer C runs only on candidates that survive Layer A.
Layer B runs on candidates that survive Layers A + C. The three
layers form a pipeline of increasing computational cost and
increasing semantic precision:

| Layer | Cost | Precision | What it catches |
|---|---|---|---|
| A (atom-tag) | near-zero | syntactic | Expression uses atoms that share a known identity closure |
| C (CAS) | moderate | exact-symbolic | Expression can be algebraically reduced to an identity basis element |
| B (empirical) | high | approximate-numerical | Expression is numerically in the functional span of the identity basis on the calibration dataset |

Layer C at 100% precision is a reduction of false-negative risk
from Layer B's approximation. Layer B at arbitrary functional
complexity is a reduction of false-negative risk from Layer C's
symbolic reach limit. Neither subsumes the other; both are needed.

### 2.4 Grammar-compatibility constraint

Not all grammar operators map to CAS canonical forms. Stratifications
(`stratify_by(V)`), probe-based operators (`per_rank`), and the
Iverson bracket `[·]` are out of CAS scope — CAS handles the
pure-algebraic sub-expressions only. The runner checks: "is this
sub-AST pure-algebraic (atom set ⊂ CAS-representable, operator set
⊂ CAS-supported)?" If yes, Layer C runs on it; if no, skip to
Layer B.

This gives CAS the speed advantage on the common case (pure
algebraic expressions) without forcing it on expressions CAS can't
represent.

### 2.5 Budget

~2–3 ticks. Breakdown:
- 1 tick: SymPy integration + pure-algebraic sub-AST detector
- 1 tick: CAS-canonical-form matcher against identity basis with
  reduce-to-zero detection
- 0.5–1 tick: integration with existing Layer B scorer and SIGNATURE
  reporting (new field: `cas_reduced_to`)

### 2.6 v3 open questions on CAS

- Does the identity basis for CAS match the numerical basis Layer B
  uses, or does CAS need its own symbolic identity basis (since
  not all numerical identities have CAS-canonicalizable forms)?
  Proposal: dual basis — CAS-basis is a strict subset of numerical-
  basis, symbols-only; numerical-basis additionally includes
  empirical approximations (e.g., `log|Δ| ~ log N + C` — the ~
  makes this numerical, not CAS).
- What's the timeout for a single CAS canonicalization? SymPy can
  loop on certain inputs. Proposal: 500ms per candidate; timeout
  = "CAS could not canonicalize" = fall through to Layer B.

---

## 3. Ensemble Pareto Promotion — from diagnostic to selection pressure

**Source:** James critique item 3 (2026-04-24).

### 3.1 Problem

v2 emits a `coefficient_sensitivity_matrix` as an audit artifact
showing how the Pareto-front composition changes under ±20%
perturbation of each scorer coefficient. This is diagnostic but
passive: a candidate that's non-dominated only at the specific
coefficient values pinned for the run might still be promoted,
with the sensitivity reported alongside.

James's observation: this lets coefficient bias influence promotion.
A candidate whose survival depends on `γ = 5.0` exactly is not
robust; it shouldn't be on the shelf.

### 3.2 Proposed extension

**Ensemble Pareto Promotion.** Instead of one run, execute 3
parallel MAP-Elites populations with deliberately perturbed
coefficient matrices. A candidate is promoted to the shelf only if
it is **non-dominated on the Pareto-triple in at least 2 of 3
ensemble runs**.

**Three canonical ensemble configurations (v3 default):**

| Run | Purpose | Coefficient perturbation from v2 defaults |
|---|---|---|
| **Novelty-biased** | Prioritize candidates far from the identity basis | `γ = 8.0` (from 5.0); `ζ, η = 0.7` (from 1.0, 0.5); others unchanged |
| **Faithfulness-biased** | Prioritize candidates with strong inverse-reconstruction | `η = 1.5` (from 0.5); `γ = 3.0` (from 5.0); others unchanged |
| **Fit-biased** | Prioritize candidates with strong data explanation | `β = 2.0` (from 1.0); `γ = 3.0`; others unchanged |

Each run uses the same grammar, same data, same seed (or three
distinct seeds with cross-seed check). A candidate present on the
Pareto-front of ≥ 2 runs is **ensemble-invariant**. Ensemble-
invariant candidates are shelf-eligible; single-run candidates are
reported but not shelf-eligible.

### 3.3 Calibration step — ensemble breadth

If perturbations are too aggressive, the intersection of Pareto-fronts
can be empty (no candidate survives 2/3 runs). If perturbations
are too light, the ensemble is redundant with the single-run
audit.

**Pre-promotion calibration:** apply the ensemble to the calibration
battery (F002, F003, F004, F008). Each anchor should appear on
the Pareto-front of ≥ 2 ensemble runs. If an anchor is ensemble-
invariant for all three ensemble configurations, the ensemble is
over-broad. If an anchor is ensemble-invariant for only one run,
the ensemble is over-narrow. Adjust the perturbation magnitudes
until at least two-thirds of anchors appear on exactly 2/3 ensemble
Pareto-fronts; this defines "just-broad-enough" for the candidate
population.

### 3.4 Cost

Ensemble Pareto is **3× compute** at minimum. This is the most
expensive of the five v3 extensions per unit of output. The
benefit: candidates surviving ensemble promotion are genuinely
coefficient-invariant, which is the honesty mechanism v2 claimed
to want but only delivered diagnostically.

### 3.5 Interaction with cross-dataset consistency (§6.2)

Cross-dataset consistency (v2) checks a candidate on ≥ 2 datasets
at fixed coefficients. Ensemble Pareto checks a candidate across
≥ 2 coefficient configurations at fixed data. The two are
orthogonal audits — a v3-full candidate survives both. Expected
cost: `3 × 2 = 6`× compute vs. v2 single-run single-dataset.
Runtime is unpalatable for cheap-path tinkering, acceptable for
v1-shelf promotion.

### 3.6 Budget

~1–2 ticks implementation (wrapping existing runs, adding
intersection check).

---

## 4. gen_11 Merger via Demand-Driven Input

**Source:** James critique item 4 (2026-04-24); resolves v2 open
question 1.

### 4.1 Problem

v2 Structure Hunter runs on pinned static datasets: grammar +
`Q_EC_R0_D5@v1` + iterate. This is "map the territory"
exploration. Meanwhile, `gen_11` in the substrate generator pipeline
reads tensor demand signals (VACUUM rows where a feature has
uniform +1 across projections → resolving axis missing;
EXHAUSTION rows where an axis class is exhausted by kills → redirect
needed) and proposes P-IDs in response.

Two producers doing similar work on different inputs is duplication.
v2 open Q1 left the merger question unresolved.

### 4.2 Proposed extension — merger via demand-signal input port

Structure Hunter absorbs `gen_11`'s role by ingesting demand
signals as an additional input:

```
input (v3):
  dataset_primary         (unchanged)
  dataset_secondary       (unchanged)
  grammar                 (unchanged)
  mdl_coefficients        (unchanged)
  pareto_triple           (unchanged)
  map_axes                (unchanged)
  affordance_types        (unchanged; now 8 with cross-domain)
  iteration_budget        (unchanged)
  seed                    (unchanged)
  demand_signal          NEW: {vacuum_f_ids, exhaustion_axes, priority_weights}
```

**`demand_signal` schema:**

```python
{
  "vacuum_f_ids": [
    {"f_id": "F011",
     "vacuum_axes": ["family_level", "magnitude", "ordinal"],
     "priority": 0.9}
  ],
  "exhaustion_axes": [
    {"axis_class": "family_level",
     "killed_f_ids": ["F010", "F020", ..., "F028"],
     "priority": 0.7}
  ],
  "priority_weights": {
    "coverage_vacuum": 1.5,       # weight toward filling vacuum cells
    "axis_class_gap": 1.2,        # weight toward non-exhausted axis classes
    "default_exploration": 0.5,   # baseline undirected exploration
  }
}
```

**Seed-bias mechanism:**

Given a demand signal, Structure Hunter modifies its GP initialization:
- **Atom-usage prior.** Atoms that the vacuum F-IDs' descriptions
  cite (e.g., F011's description references `a_p` zero spacings) get
  higher initial sampling probability.
- **MAP-cell seed prior.** Cells in `AXIS_CLASS` values that
  correspond to vacuum-axes or non-exhausted classes get higher
  candidate-density at population initialization.
- **Scorer boost.** δ penalty scales higher for candidates that place
  in a vacuum cell — candidates that fill a gap are preferred to
  candidates that duplicate a well-populated cell.

Under `demand_signal = None`, Structure Hunter reverts to v2
undirected-exploration behavior. Under demand signal present, the
instrument is topographically oriented.

### 4.3 `gen_11` deprecation

Once Structure Hunter v3 accepts `demand_signal`, `gen_11` as a
standalone generator is deprecated. The generator-pipeline doc
(`generator_pipeline.md`) gets an entry: `gen_11` → merged into
`gen_12` (`CONJECTURE_GENERATOR`). No work lost — gen_11's
architectural intent is fully served by the merged producer.

### 4.4 Substrate-integration requirements

- Redis stream for live demand signals: `agora:structure_hunter:demand`.
  Writes from tensor-push events (VACUUM detection, EXHAUSTION
  counter update). Reads from the Structure Hunter runner at
  initialization time.
- `AXIS_CLASS@v1` stays the niche taxonomy (unchanged); the demand
  signal just changes which cells get prioritized, not the cell
  definitions.
- Tensor integration: `VACUUM@v1` and `EXHAUSTION@v1` shape symbols
  are the substrate primitives that define what a demand signal IS.
  No new symbol promotions required for v3.

### 4.5 Budget

~2–3 ticks. Breakdown:
- 1 tick: demand-signal ingestion + Redis stream reader
- 1 tick: seed-bias mechanism (atom prior + MAP-cell prior + scorer
  boost)
- 0.5–1 tick: `gen_11` deprecation + `generator_pipeline.md` update

### 4.6 Risk

**Reward-hacking the demand signal.** A candidate that lands in a
vacuum cell for shallow reasons (e.g., a trivial stratification
that matches the axis taxonomy but doesn't resolve F011) still gets
the δ boost under the new scorer. The cross-dataset check and
reconstructability η should catch this — a trivial stratification
fails reconstructability because it destroys too much. But the risk
is real: demand-signal ingestion makes the instrument goal-directed,
and goal-directed search has its own failure modes.

**Mitigation:** the demand signal enters at *initialization*
(seed-bias) and *scoring* (δ boost), not at *gate rejection*. A
candidate scoring poorly on basis-projection or reconstructability
still fails regardless of demand-signal alignment. Demand is a
direction, not a license.

---

## 5. Latent-Trace Reconstructability — η via AST execution graphs

**Source:** James critique item 5 (2026-04-24); composes with the
Sovereign Harvest engine.

### 5.1 Problem

v2's reconstructability η is measured via an external inverse
model: fit a gradient-boosted regressor from `σ(x) → preserves(x)`,
measure test accuracy. This is sound but treats the transformation
as a black box. It doesn't use information the AST evaluation
already produces.

### 5.2 Proposed extension — η as composite of external + internal

Augment η with a second signal derived from the AST evaluation
trace itself:

```
η_composite = w_external · η_inverse_model + w_internal · η_trace
```

**η_trace definition:**

Instrument the AST evaluator to emit, for each candidate `σ`:
- **Information density per node.** For each intermediate node `n`
  in the AST, measure `H(output_n | inputs_n)` — conditional entropy
  of the node's output given its inputs, estimated empirically on
  the calibration dataset.
- **Reversibility per step.** For each operator step `n_parent →
  n_child`, measure the bit-accuracy with which a simple inverse
  `n_child → n_parent` can be reconstructed.
- **Trace density.** Total information preserved through the full
  AST evaluation, normalized by the object's native information
  content.

`η_trace = trace_density / max_possible_trace_density`, in `[0, 1]`.
Higher = more information preserved through evaluation = more
"reversible" the transformation is at the execution-step level.

### 5.3 Composition with Sovereign Harvest engine

The Sovereign Harvest engine (the broader Prometheus project
— evolved prompt strategies + reasoning-trace harvest from frontier
models on coding tasks) has an established reasoning-trace
taxonomy. AETHON's 10-module vocabulary (chain_of_thought,
socratic_questioning, metacognitive_reflection, etc., per
`aethon/living_ideas.md` §Integration 1) tags reasoning-trace
structure at the prompt-output level.

A natural composition: **AST execution traces are reasoning traces
at a different scale.** Each AST node's operation is a
"reasoning step" in the same sense a model's chain-of-thought
step is. The Sovereign Harvest taxonomy can classify AST steps by
analogous categories:
- `composition` — operator applied to sub-expressions
- `reduction` — arity-reducing operation (e.g., sum, max)
- `lift` — type-changing operation (scalar → stratification)
- `transformation` — arithmetic/functional step
- `branch` — conditional or stratification split

With AST steps tagged by this taxonomy, η_trace becomes a
structured signal: reconstructability partitioned by reasoning-step
type, revealing which computational stages lose information.

### 5.4 Budget

~1–2 ticks. Breakdown:
- 0.5 tick: AST evaluator instrumentation (emit per-node conditional
  entropy + per-step reversibility)
- 0.5 tick: η_trace scorer aggregation + composition with η_inverse
- 0.5–1 tick: integration with Sovereign Harvest taxonomy (if
  Integration 1 from `aethon/living_ideas.md` has landed — otherwise
  defer the taxonomy overlay)

### 5.5 v3 open questions on η_trace

- **Weighting `w_external` vs `w_internal`.** Default proposal:
  `w_external = 0.7, w_internal = 0.3` — external inverse model is
  the established discipline, latent trace is the augmenting signal.
  Calibration via anchor-battery will tune these.
- **When do the two signals disagree?** If they diverge strongly
  (e.g., high η_inverse but low η_trace), that's diagnostic —
  the transformation reconstructs well in aggregate but destroys
  information at a specific step. Surface for audit; don't auto-
  resolve.

---

## 6. Dependency graph and sequencing

### 6.1 Tiers by empirical readiness

**Tier A — pre-Tink, spec-only:** items that can be specified ahead
of v2 empirical validation without committing implementation budget.

- #1 Typed Relational Grammar (design)
- #3 Ensemble Pareto Promotion (design)

**Tier B — post-Tink 2:** items that depend on v2's seven-axis
scorer existing and being empirically validated.

- #5 Latent-Trace Reconstructability (extends existing η)
- #2 CAS Symbolic Canonicalization (inserted as Layer C in
  basis-projection)

**Tier C — post-Tink 3:** items that depend on substrate integration
signals only available after a full-grammar scan has run.

- #4 gen_11 Merger (needs VACUUM / EXHAUSTION signals from a
  populated tensor + demonstrated `gen_11`-style use cases)
- #1 Typed Relational Grammar (implementation)

### 6.2 Total v3 budget

~13–21 ticks additional to v2's ~10–13 ticks full-path. Grand total
for v3 shipped: ~23–34 ticks.

This is substantial. The honest sequencing: don't commit Tier B or
Tier C implementation until Tier A spec is reviewed AND v2 Tink 2
has produced the predicted disagreement.

### 6.3 If cheap-path fails to validate v2

If Tink 2 does NOT show aggregate-scalar / Pareto-front disagreement
on F043, v2 architecture is wrong. Response: reset to critique,
not proceed to v3. Possible resets:

- Pareto-front triple is wrong (try alternatives)
- Coefficient scales are wrong (re-normalize)
- Basis-projection Layer B estimator is wrong (try different kernels)
- Categorical gates are wrong (add/remove)
- The whole seven-axis scoring is over-engineered; fall back to 4-axis

This roadmap assumes v2 is right, empirically. If not, start over at
v2 critique, not here.

---

## 7. v3 item interactions — where items reinforce or conflict

### 7.1 Reinforcements

- **#1 TRG + #2 CAS.** Cross-object expressions are exactly where
  CAS canonicalization pays off most — modularity identity
  `a_p(E) = a_p(f_E)` is a CAS-canonicalizable identity that would
  be missed by empirical Layer B on a finite-prime sample. TRG and
  CAS are mutually reinforcing.
- **#3 Ensemble Pareto + #4 Demand-driven merger.** A candidate
  promoted under a demand signal AND surviving ensemble Pareto is
  doubly-vetted: it aligns with substrate need AND is coefficient-
  invariant. The combination is stricter than either alone.
- **#5 Latent trace + #2 CAS.** AST execution traces and CAS
  canonical forms are two views of the same computation. A
  candidate whose CAS canonical form is simple but whose AST
  execution trace is information-dense is a candidate whose
  compression lives in the logical structure, not the computational
  structure. The two perspectives together give richer η.

### 7.2 Conflicts

- **#3 Ensemble Pareto × compute cost.** 3× compute at base;
  composed with cross-dataset (2×) = 6× compute vs. v2 minimum.
  On the cheap path (zoo/), this is unpalatable. Ensemble is a
  shelf-promotion gate, not a tinkering gate.
- **#4 Demand-driven seed-bias × novelty-seeking.** A strongly
  goal-directed search may under-explore unexpected regions. The
  demand-signal `priority_weights.default_exploration` parameter
  is the hedge; at high demand strength, exploration drops.
  Discipline: never set `default_exploration < 0.3` without explicit
  reason.
- **#1 TRG × grammar search blowup.** `k²` atom candidates at
  arity ≤ 2 may require new search-bias controls beyond
  AST-diversity (θ). Potential resolution: hierarchical grammar
  where relational atoms are opt-in via flag, not default.

---

## 8. Items explicitly NOT in v3

For clarity about the scope boundary:

- **Quantifier-class claims** (v2 open Q7) — existential / universal
  MDL extension. Deferred to v4+.
- **Unbounded AST depth.** v3 retains `max_depth` pinning.
- **Non-arithmetic atom grammars** (spectral statistics, topological
  features). Distinct instruments, deferred indefinitely.
- **Paper-shaped output.** v3 still commits to Framing B discipline;
  outputs are coordinate transformations with measurements, not
  findings. (Scope disclaimer unchanged.)

---

## Version history

- **v3-roadmap-v1** — 2026-04-24 — initial roadmap following James's
  third-round critique. Five extensions specified at architecture
  level; dependency graph and budgets pinned; empirical gate
  (Tink 2 validation) named as precondition for implementation
  commitment.
