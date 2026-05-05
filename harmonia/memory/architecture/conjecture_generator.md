# Conjecture Generator (Structure Hunter)

**Status:** v0.3.1 DRAFT — incubation, not yet candidate. Pre-spec.
**Proposed by:** Harmonia_M2_sessionC with James, 2026-04-23.
**Slot:** architectural primitive / candidate generator #12.
**Decision required before v1:** target class (§8), grammar atomic set +
lineage closure (§4), merger-or-sibling with `gen_11` (§13).

**Reframe (v0.3, per James 2026-04-24 five-fragility critique):**
the earlier reframe stands, but the discipline shape changes. v0.2 was
"coordinate-system discovery engine constrained by algebraic-lineage
pruning and MDL-with-encoding-robustness calibration." v0.3 is:

> **Coordinate-system discovery engine defined by continuous
> measurement of structural independence and usefulness.**

Hard exclusion was over-brittle. A binary R² gate gives false negatives
(non-linear couplings look novel) and under-uses continuous information
(a candidate with `R² = 0.85` is genuinely closer to the identity basis
than one with `R² = 0.05` but was getting equal treatment). v0.3
replaces the binary gates with continuous metrics along seven axes
(§6), with Pareto-front promotion rather than pure scalar minimization.
Framing B stays as the type-level rule on output shape (no equalities,
inequalities, or correlations), but candidates now carry a third
metadata slot alongside `preserves`/`destroys`: **`affordances`** —
empirical measurements of claim-relevant detectability gains under the
transformation. Affordances are measurements, not claims; but a
candidate whose affordances cross a declared threshold becomes eligible
for Framing-A arbitration via `null_protocol_v1.1`.

---

## 0. Why this doc exists

James proposed an Automated Conjecture Generator: GP/GA over parameterized
expressions, MAP-Elites for niche diversity, scored on simplicity-vs-
explanatory-power. This doc incubates the idea — surfaces the structural
tensions, maps it against the existing substrate, and defines what has
to be true before any code is written. Tinkering is invited *after* this
draft is confirmed; this doc's job is to make the tinkering load-bearing
rather than reward-signal-driven.

**Prior-art note.** The idea is closest-in-substrate to `gen_11`
(coordinate-invention, axis-space producer) and to the Definition DAG
(atomic-variable grammar). It is a cousin of `CRITICAL_EXPONENT@v1` +
`MDL_SCORER@v1` from `methodology_toolkit.md` (the scoring function).
Nothing here is conceptually new at the substrate level; the contribution
is putting the pieces together under a discipline that doesn't produce
F043-class garbage at scale.

---

## 1. Substrate alignment check (charter compliance)

`docs/landscape_charter.md` and `long_term_architecture.md` are explicit:
Prometheus does not prove theorems, does not aim to generate publishable
mathematics. An "automated conjecture generator" is linguistically in
tension with that.

**Resolution:** frame outputs as candidate *substrate artifacts*, not as
findings. Three framings, one ruled out:

| Framing | Artifact | Charter status |
|---|---|---|
| **A — claim generator** | Candidate F-IDs seeded into `register_specimen`; each carries claim-class under `null_protocol_v1`; each passes `gen_06` Pattern 30/20/19 sweep before tensor entry. | ALIGNED. Outputs are measurement proposals, not claims. |
| **B — coordinate generator** | Candidate P-IDs (new scorers, stratifications, transformations) that make existing data more legible. Pattern 15 literal ("machinery is the product"). | **ALIGNED AND HIGHER-LEVERAGE.** Direct substrate growth. |
| **C — publishable-conjecture generator** | Outputs framed as "things we found." | CHARTER VIOLATION / reward-signal capture. |

**Recommended framing: B primary, A secondary.**
- B is what `gen_11` is architecturally trying to be. A conjecture generator
  operating on axis-space is a concrete gen_11 implementation strategy.
- A is a natural by-product: when a candidate coordinate has a pinned
  functional form whose pattern-of-outputs is a claim (e.g., "this scorer
  stratifies F011 uniformly"), the candidate F-ID writes itself.
- C is forbidden. No paper-shaped output framing. Every artifact is a
  substrate commit.

### 1.1 Hard rule — B cannot silently collapse into C (v0.2)

Framing B without enforcement collapses into C. A projection that
systematically highlights a relation is already halfway to a claim:
*"this projection reveals a linear relation between X and Y"* is
structurally identical to *"X and Y are linearly related"* with a
softer interface.

The hard rule, enforced at the **type level**:

> A P-ID produced by this generator may **transform** observables but
> may **NOT** assert invariants.

| Allowed output shape | Schema |
|---|---|
| Feature map | `f: objects → features` (unary transformation) |
| Stratification | `s: objects → strata` (partition function) |
| Coordinate change | `c: feature_space → feature_space` (bijection or injection) |
| Scorer (object→scalar) | `σ: objects → ℝ` (with declared range + invariance) |

| Forbidden output shape | Why |
|---|---|
| "`X = Y`," "`X ≤ Y`," "`X ~ f(Y)`" | Assertion, not transformation |
| Any expression whose natural reading is a claim about the data | Claim in disguise |
| A projection whose only purpose is to "reveal" a relation | Framing-C smuggling |

**Mandatory declaration per candidate (three fields, v0.3):**
- `preserves`: list of algebraic properties, distributional moments, or
  relational structures that round-trip through the transformation.
  ("Rank is preserved." "Per-decile variance is preserved." "Isogeny
  equivalence is preserved.")
- `destroys`: list of properties lost — two objects distinct under the
  source coordinate that become indistinguishable under the
  transformation. ("Sign of `a_p` is destroyed." "Magnitude below
  `log N = 5` is quantized.")
- **`affordances`** (v0.3, per James fragility critique 2A + 3.1):
  empirical measurements of **claim-relevant detectability** under the
  transformation. Not claims; measurements.

**Candidates that cannot fill all three fields are type-rejected
pre-scoring.** A projection without a `preserves` / `destroys` /
`affordances` audit is an information-lossy compression masquerading
as a coordinate.

### 1.2 Affordances — bridging transformation and claim without smuggling (v0.3)

The v0.2 hard rule forbade equalities, inequalities, and correlations
as output. James's 2A critique: this over-constrains. Many useful
transformations are useful *because* they linearize or expose a
relation — a transform that makes `rank` detectable from transformed
features is implicitly carrying structure. v0.2 forced the system to
discover structure but never express it directly, producing awkward
encodings or scoring loss.

**Resolution: affordance measurements are allowed; affordance claims
are not.** Concretely, a candidate may declare and report (v0.3.1 list,
7 types):

| Affordance type | Operational form | Measures | Applies |
|---|---|---|---|
| `linear_probe_gain` | Accuracy of `linear_model(transformed) → target` vs `linear_model(raw) → target` | How much easier a downstream linear task becomes | all candidates |
| `nonlinear_probe_gain` | Accuracy of `RF(transformed) → target` vs `RF(raw) → target` (random forest with bounded depth, e.g., 100 trees depth 6) | Catches transformations useful to non-linear models but not linear ones | all candidates |
| `variance_reduction` | `Var(Y | transformed) / Var(Y | raw)` for declared target `Y` | Tightens conditional distribution of `Y` | numerical targets |
| `mutual_information_gain` | `I(transformed; Y) − I(raw; Y)` via KSG estimator, k=5 | Information about `Y` recovered/lost | any target |
| `clustering_separability` | Silhouette score on k-means of transformed vs raw, `k` pinned | Cluster structure revealed | all candidates |
| `rank_correlation_gain` | `|spearman(transformed, Y)| − |spearman(raw, Y)|` | Ordinal-relation exposure (useful for rank, torsion order, CM-type) | ordinal targets |
| `autocorrelation_exposure` | Lag-1 autocorrelation of transformed sequence vs raw | Serial structure exposure | **sequence-valued atoms only** (e.g., `a_p` sequences) |

**Null baseline discipline.** Every affordance score carries a
declared null baseline — same metric computed on shuffled features
(or equivalent randomization). Reported as a pair
`(affordance_score, null_baseline)` in the SIGNATURE. The scorer uses
`affordance_gain = affordance_score − null_baseline`, so candidates
that score well only because the metric has a non-zero floor are not
rewarded.

**Affordance aggregation into score axis ζ.**

```
affordance_max = max over applicable types of (affordance_gain_normalized)
axis_ζ_contribution = ζ · (1 − affordance_max)
```

`max` is used (not mean) because: a transformation that helps one
downstream task strongly and others not at all is still valuable for
that task; averaging dilutes the signal. Per-type affordances are
reported individually in SIGNATURE for diagnostic use.

**Extensibility.** The affordance list is versioned (current version
7 types); an 8th type can be added via substrate amendment. A
candidate's SIGNATURE records which affordance-list version it was
scored against.

**Framing-A activation path (v0.3, refined).** A candidate's affordance
crossing a declared threshold makes it eligible for Framing-A
arbitration — i.e., eligible to seed a candidate F-ID. The F-ID is NOT
the affordance measurement itself; it is the hypothesis the affordance
suggests, audited by `null_protocol_v1.1` with a full claim-class
assignment. Example:

- Candidate transform `σ(E) = (log|Disc|/log N, ∏c_p, rank)` declares
  affordance `linear_probe_gain(rank) = +0.23` (accuracy gain on
  rank prediction).
- Affordance crosses threshold. Candidate F-ID proposed:
  "rank is linearly predictable from `σ(E)` on rank-0 cohort."
- Candidate F-ID enters `register_specimen`, gets Class 2 or Class 3
  null protocol assignment, passes or fails Pattern 30 lineage check,
  is audited.

The affordance is NOT treated as evidence for any claim; it is a
screening device that surfaces claim candidates for independent
arbitration. The substrate's retraction-enabled infrastructure remains
the arbiter of truth.

---

## 2. The F043-factory problem is structural, not a tuning issue

Pattern 30 anchor: `corr(log Sha, log A = Ω·∏c_p) = −0.4343` at `z_block = −348`
survived a conductor-decile block-shuffle because the null preserved the
definitional BSD rearrangement. **Any GP evolving formulas over
BSD-ingredient atomic variables will evolve every algebraic rearrangement
of the identity as "conjectures," and every one passes its own null.**
This is not a rate-limiting problem — it is a total-output problem.

**Consequence:** Pattern 30 cannot be a post-evaluation filter here. It
must live in the **grammar**.

Concretely: every atomic variable in the grammar carries an
`algebraic_closure` tag listing the identities it participates in.
`PATTERN_BSD_TAUTOLOGY` (`null_protocol_v1.1` amendment, 2026-04-22)
already enumerates the BSD-ingredient family and its closures. The
grammar inherits this as a pre-declared type system. Candidate expressions
compute their Pattern 30 severity level at *generation time* from the
atom tags, not from their evaluated correlations. Level ≥ 2 candidates
never reach the MAP-Elites archive — they are pruned at birth.

**This promotes the Definition DAG from "nice to have" to
hard prerequisite.** Phase 0 (manual seed of ~20 nodes) is already the
next implementation step; the conjecture generator extends the seed
requirement to ~60–80 nodes covering LMFDB-scope arithmetic invariants.
Without the DAG, the grammar has no type system and every output is
a potential F043.

### 2.1 Pattern 30 level-check is necessary but NOT sufficient (v0.2)

Pruning Level ≥ 2 catches *exact algebraic rearrangement*. It does NOT
catch:

- **Log-transformed near-tautologies** — `corr(log|Δ|, log N)` is strong
  because `N | Δ` (bad primes divide the discriminant) even though
  neither is a term of the other's definition
- **Partial-product coupling** — Szpiro ratio `log|Δ|/log N` and Faltings
  height `h_F ≈ (1/12)·log|Ω|⁻¹ + const` both carry `log|Δ|` at
  leading order; they "correlate" by near-identity without being
  exact rearrangements
- **Mixed-scale expressions** — quantities whose dominant behavior is
  identity-forced even when the expression itself is not a rearrangement
- **Functional redundancy** — two expressions that span the same
  equivalence class under the grammar's operator closure (e.g., `log X`
  and `log X + c` for grammar-definable `c` are the same "discovery")

**Needed upgrade (v0.3: continuous multi-kernel basis-projection
score).** Given the known-identity basis `{I_1, ..., I_k}` materialized
as vectors on the calibration dataset, a candidate expression `E` is
checked for functional redundancy against the basis using three
complementary span-detection measures. Unlike v0.2's binary threshold,
v0.3 returns a continuous score that enters scoring as a soft penalty
(§6 axis γ), not as a hard prune.

**Three measures, taken jointly:**

1. **Linear span strength** `R²_lin`: regress
   `E ~ α_0 + α_1 I_1 + ... + α_k I_k + ε` via OLS; record `R²`.
2. **Non-linear span strength** `R²_kern`: kernel ridge regression of
   `E` against the basis with an RBF kernel (`γ = 1/n_features`, ridge
   `λ = 1e-3` pinned default). Catches multiplicative couplings,
   compositional dependencies, and monotone transforms that linear
   regression misses.
3. **Information span** `MI_norm`: mutual information estimate between
   `E` and the basis vector `(I_1, ..., I_k)` via Kraskov-Stögbauer-
   Grassberger (KSG) `k=5`. Normalized to `[0, 1]` by division by
   `H(E)` (entropy of candidate). Catches couplings in distributional
   form that neither regression picks up.

**Continuous basis-projection score:**

```
basis_projection_score = max(R²_lin, R²_kern, MI_norm)
```

Reported per-candidate in `[0, 1]`. Higher = closer to the identity
span = less novel. Lower = farther from the span = more novel. No
hard threshold; the score enters the seven-axis scorer (§6) with
coefficient `γ`. Default `γ` is large enough that candidates with
`basis_projection_score > 0.95` are effectively de-prioritized without
being pre-pruned, which preserves auditability of boundary cases.

**Per-measure reporting.** The three component scores are emitted
separately in SIGNATURE so downstream readers can inspect which kind
of dependence is firing. A candidate with `R²_lin = 0.1` but
`R²_kern = 0.9` is a non-linear near-tautology that linear-only
checks would miss — the separation is diagnostic.

**Why max, not average.** Any one of the three measures crossing high
is evidence of dependence; averaging dilutes signal. The stricter
measure wins by construction. If users want a softer scoring, they
can adjust `γ` downward, not the aggregation rule.

**Rank-and-audit alternative to pure scoring.** Candidates are not only
scored by aggregate MDL + penalties; they are also ranked on a
Pareto front where one axis is `1 − basis_projection_score` ("novelty")
and another is aggregate MDL-goodness. A candidate dominated on both
is filtered; a candidate on the frontier is retained for review even
at high `basis_projection_score`. This surfaces boundary cases the
scalar score would hide (per James 2C critique: "novelty is defined
relative to what you encoded — make it continuous, not binary").

**Upgrade path to v1+:**
- Symbolic canonicalization via CAS (SymPy) to catch rearrangements the
  three numerical measures miss structurally but pick up numerically
  by accident.
- Per-kernel tuning to domain (RBF is default; polynomial kernel for
  near-polynomial couplings; string-kernel for atom-sequence checks).
- Basis-extension auto-suggestion: when a candidate's
  `basis_projection_score` is high BUT no single known identity
  explains it, the residual regression vector is a candidate
  identity-basis addition.

**The grammar is not just typed variables with lineage. It is:**

> Typed variables + lineage tags + a **continuous distance-from-
> identity-basis signal** in the functional span of the known
> identities.

Distance-from-basis replaces "forbidden subspaces" as the v0.2 mental
model. The discipline is the same (prevent F043-shaped output); the
mechanism is continuous, which makes the instrument's epistemology
debuggable.

---

## 3. Architecture sketch (Framing B primary)

### 3.1 Search loop

```
┌─────────────────┐     ┌────────────────┐     ┌────────────────┐
│  GRAMMAR        │────►│  GP / GA       │────►│  PATTERN 30    │
│  (atomic vars,  │     │  mutate /      │     │  GRAMMAR GATE  │
│   operators,    │     │  crossover /   │     │  (level ≥ 2?)  │
│   lineage tags) │     │  prune         │     │   reject/emit  │
└─────────────────┘     └────────────────┘     └────────┬───────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌────────────────┐     ┌────────────────┐
│  FEEDBACK:      │◄────│  MAP-ELITES    │◄────│  MDL SCORER    │
│  niche gaps →   │     │  niches =      │     │  L(expr) +     │
│  mutation       │     │  AXIS_CLASS    │     │  L(data|expr)  │
│  priors         │     │  cells         │     │                │
└─────────────────┘     └────────────────┘     └────────────────┘
```

### 3.2 Five components (each mapped to substrate)

| Component | Substrate primitive | Notes |
|---|---|---|
| **Grammar** | Definition DAG nodes + edges w/ Pattern 30 severity; `AXIS_CLASS@v1` tags on each atomic variable | Phase-0-extended DAG is the grammar's spec |
| **Search** | GP / GA — no substrate primitive yet | New. Tinkering ground. |
| **Grammar gate** | `harmonia/sweeps/pattern_30.py` extended to operate on expression-trees at generation time | Re-use, extend |
| **Scorer** | `MDL_SCORER@v1` from `methodology_toolkit.md` entry #4 | Paste-ready per shelf |
| **Diversity archive** | MAP-Elites over cells indexed by `AXIS_CLASS@v1` values | Re-use taxonomy |

### 3.3 What's already ready vs what's new

**Ready (re-use as-is):**
- `PATTERN_30@v1` + `LINEAGE_REGISTRY` + `PATTERN_BSD_TAUTOLOGY`
- `null_protocol_v1.1` (claim-class assignment)
- `AXIS_CLASS@v1` (10-value niche taxonomy)
- `MDL_SCORER@v1` (shelf entry #4, paste-ready)
- `MULTI_PERSPECTIVE_ATTACK@v1` (adversarial-grammar discipline, §5)
- `SHADOWS_ON_WALL@v1` (lens-count per candidate)

**Needs new infrastructure:**
- Definition DAG Phase 0 extended seed (~60–80 nodes)
- Expression-tree representation (AST + atom-tag propagation)
- GP operators that respect lineage tags (crossover can't merge
  incompatible algebraic-closures without re-running Pattern 30)
- MAP-Elites archive with `AXIS_CLASS`-indexed cells

---

## 4. Atomic-variable grammar (worked example)

First target class is **LMFDB elliptic curves at rank 0**, where
calibration anchors live and Pattern 30 atoms are already enumerated.

**Atomic variables (illustrative subset, not exhaustive):**

| Atom | Type | Algebraic closure | AXIS_CLASS |
|---|---|---|---|
| `N` (conductor) | magnitude | BSD-ingredient (weak — denominator) | magnitude |
| `a_p` (Frobenius trace at p) | ordinal | Hasse-bound `\|a_p\| ≤ 2√p` (identity at p) | ordinal |
| `rank` | categorical | BSD parity identity | categorical |
| `disc` (discriminant) | magnitude | N | disc via bad-prime structure | magnitude |
| `Ω` (real period) | magnitude | **BSD-ingredient (primary)** | magnitude |
| `|Sha|` | ordinal | **BSD-ingredient (primary)** | ordinal |
| `∏c_p` (Tamagawa product) | magnitude | **BSD-ingredient (primary)** | magnitude |
| `|Tor|` | categorical | BSD-ingredient (Mazur) | categorical |
| `root_number` | categorical (±1) | BSD parity identity | categorical |
| `j_invariant` | magnitude | CM classification | magnitude |

**Operators:** `+`, `−`, `×`, `÷`, `log`, `exp`, `^`, `mean_p`, `sum_p`,
`stratify_by`, `cond_decile`, `per_rank`. Each has its own lineage rule
(e.g., `log` preserves BSD-membership; `÷` between two BSD-primaries
produces a BSD-derived quantity; `stratify_by(rank)` produces a
conditional claim of Class 2 under `null_protocol_v1`).

**Candidate expression → (severity, claim_class, axis_class) at
generation time:**

```
expr = (log |Sha| − mean_p(a_p²/p)) / log N
                                           
atoms_used       = {|Sha|, a_p, p, N}
bsd_primaries    = {|Sha|}        # count = 1
bsd_derived      = {mean_p(a_p²/p)}  # Hasse-related, weak
pattern_30_level = 1 (WEAK_ALGEBRAIC — log N denominator)
null_protocol    = Class 2 (rank-stratified if `per_rank` later applied)
axis_class       = magnitude (principal) × ordinal (secondary)
```

This metadata accompanies the expression through scoring. The generator
does not lie to itself about what it just proposed.

---

## 5. The MAP-Elites niche design is a coordinate choice (meta-Pattern 6)

MAP axes listed by James ("linear vs nonlinear, local vs global") are
themselves coordinate-system choices. Every declared niche is a claim
about what kinds of conjectures exist. Two consequences:

1. **Niche taxonomy reuses `AXIS_CLASS@v1`.** 10-value controlled
   vocabulary: `family_level`, `magnitude`, `ordinal`, `categorical`,
   `stratification`, `preprocessing`, `null_model`, `scorer`, `joint`,
   `transformation`. No parallel taxonomy. If the conjecture generator
   needs a niche dimension `AXIS_CLASS` doesn't cover, that's a
   `AXIS_CLASS` extension, not a generator-local invention.

2. **Conjectures that don't fit any declared niche are structurally
   invisible.** This is `VACUUM@v1` applied recursively: a uniform
   high-density region across declared niches means the resolving axis
   isn't in our MAP. Treating "MAP is full" as success is backwards.
   Pattern 18 says the interesting candidates may be the ones the MAP
   can't place.

**Discipline:** every MAP-Elites run reports (a) per-cell best candidate,
(b) per-cell density, (c) **unplaceable candidate count and sample**.
The last is the load-bearing audit — if 80% of high-MDL candidates don't
fit any declared niche, the niche taxonomy is the problem, not the
candidates.

### 5.1 Residual channel — out-of-MAP mass as first-class signal (v0.2)

Unplaceable candidates are NOT discarded or force-fit into the nearest
declared cell. They enter a **residual channel** processed as follows:

1. **Retention.** Every candidate passing the grammar gate (§2) but
   not fitting any declared `AXIS_CLASS` cell is retained with full
   metadata: expression tree, MDL score, atom usage, `preserves` /
   `destroys` declaration.

2. **Clustering.** Unplaceable candidates are clustered by nearest-
   neighbor in (expression-tree edit distance) × (MDL-score similarity)
   × (atom-usage Jaccard). Cluster size threshold proposed at `≥ 5`
   for "cluster worth reporting."

3. **Post-hoc axis discovery.** Clusters exceeding threshold are
   inspected for a shared structural property the current
   `AXIS_CLASS@v1` taxonomy does not name. If found, the cluster is
   promoted as an `AXIS_CLASS` extension candidate and surfaced via
   `decisions_for_james.md`. The generator proposes taxonomy updates;
   it does not perform them unilaterally.

4. **Per-run reporting schema:**
   ```
   out_of_map_fraction = |unplaceable| / |all_candidates_past_gate|
   out_of_map_top_clusters = [(cluster_size, exemplar_expression, shared_properties_guessed)]
   ```

**Operationalization of Pattern 18 at the MAP level:**

| MAP-cell density | Out-of-MAP fraction | Diagnostic |
|---|---|---|
| Uniform, high | Low (< 5%) | Calibration passing; search healthy |
| Clustered around anchors | Low (< 5%) | Either well-calibrated OR tight reward-signal capture on declared niches |
| Uniform, high | High (> 30%) | **VACUUM signal — resolving axis is outside both the anchor catalog AND the MAP's prior taxonomy.** Substrate-growth opportunity. |
| Sparse / empty | Any | Grammar too restrictive, search operators too weak, or target class has less structure than assumed |

A dense MAP with empty residual cannot distinguish "calibrated success"
from "tight reward-signal capture" — the residual channel is what
resolves that ambiguity. **An empty residual is a warning, not a
success metric.**

**This is a meta-move.** The MAP itself becomes a coordinate choice
subject to Pattern 18 / `VACUUM@v1` discipline. Geometry 3 (projection-
discipline is recursive) applied one layer above the candidate. The
residual channel is where that recursion becomes operational.

### 5.2 Auto-descriptor proposal from residual clusters (v0.3)

Per James 2D critique: the v0.2 residual channel stopped at
"cluster + surface to humans." Ontology lock-in persists because
taxonomy updates only happen when a human reviews and decides. v0.3
extends the residual channel to **machine-proposed descriptors** with
a quantitative stability test.

**Procedure:**

1. **Cluster** unplaceable candidates as in §5.1 (tree-edit + MDL +
   atom-Jaccard).
2. **For each cluster of size ≥ threshold**, fit a simple classifier
   that distinguishes cluster members from the union of declared-cell
   members. The classifier's features are: atom-usage vector,
   tree-depth, operator-histogram, preserves/destroys declarations,
   affordance vector.
3. **If the classifier achieves separation accuracy ≥ 0.8**, the
   decision boundary defines a *candidate descriptor function*
   `d_new: candidate → ℝ`. The descriptor is the function that, when
   added as a MAP axis, would move this cluster into its own cell.
4. **Stability test:** re-run MAP-Elites with `map_axes = existing ∪
   {d_new}` on a fresh search budget. If:
   - The new axis produces a cell with stable occupancy (≥ 3
     candidates across independent seeds),
   - The existing cells remain stable (out-of-MAP fraction does not
     spike),
   - Anchor rediscovery (§6 calibration battery) is not degraded,
   then the descriptor is a **validated `AXIS_CLASS` extension
   candidate**.
5. **Human review** still gates actual `AXIS_CLASS@v2` promotion; the
   instrument surfaces a quantitative proposal with a stability
   record, not a unilateral taxonomy edit. The decision record lives
   in `decisions_for_james.md`.

**Example hypothetical workflow:**

- v0.3 Tink 3 run produces 27 candidates in the residual channel.
- Clustering yields three clusters of size 9, 8, 6.
- Cluster-1 classifier separates members from the `magnitude` cell
  at 0.91 accuracy; the decision boundary uses atom `j_invariant`
  predominantly.
- Descriptor `d_new = uses_j_invariant(candidate)` proposed.
- Re-run with the new axis: new cell (`magnitude × j_invariant_user`)
  populated with 5 candidates across 3 seeds; existing MAP stable;
  anchor battery unchanged.
- Entry surfaces in `decisions_for_james.md`: "candidate `AXIS_CLASS`
  extension `j_invariant_user` proposed, validated by 2-seed
  stability test. Recommended for `AXIS_CLASS@v2` if approved."

**Safeguards:**

- The auto-proposer does NOT modify the live `AXIS_CLASS@v1`
  registry. It writes to a separate `AXIS_CLASS_CANDIDATES`
  namespace.
- A proposed descriptor that fails stability (anchor degradation,
  unstable occupancy) is logged and discarded, not promoted.
- The classifier's features are restricted to syntactic and
  declared-metadata signals — it does not use MDL scores or
  affordance values, so proposed descriptors cannot be gamed by
  scoring-artifact clusters.

**Composition with other discipline:** auto-descriptor proposals feed
`gen_11` (coordinate-invention). If Structure Hunter and `gen_11`
eventually merge (§13 open question), the auto-descriptor pathway is
the natural interface.

---

## 6. Scoring — seven axes with Pareto-front promotion (v0.3)

v0.2 used a four-component scorer (α·simplicity + β·fit + γ·Pattern-30
hard gate + δ·calibration hard gate). James's critique (2E + 3.1 +
3.4 + 3.5) expanded the scope: MDL as sole proxy for structure misses
sparse / threshold / phase-transition phenomena; hard gates obscure
boundary cases; degenerate projections that destroy too much escape a
fit-only objective; GP search dynamics bias tree shape.

v0.3 generalizes to **seven axes**, all continuous, all pinned per-run,
with Pareto-front promotion replacing pure scalar minimization.

```
score(expr, data, grammar, basis, anchors, explored) =
    α · L(expr)                                         [simplicity]
  + β · L(data | expr)                                  [fit]
  + γ · basis_projection_score(expr, basis)             [algebraic novelty — §2.1]
  + δ · calibration_alignment(expr, anchors)            [anchor-battery recovery]
  + ε · residual_structure_score(expr, data)            [non-random leftover — §6.3 below]
  + ζ · affordance_gain(expr, data, probes)             [downstream usefulness — §1.2]
  + η · reconstructability(expr, data, preserves)       [inverse-model accuracy — §6.4]
  + θ · ast_diversity_penalty(expr, explored)           [search-bias control — §6.5]
```

All coefficients `(α, β, γ, δ, ε, ζ, η, θ)` pinned per-run in the
SIGNATURE.

### 6.0.1 Scale normalization (v0.3.1)

Before coefficients make sense, axis scales must be commensurate.
Naive bits-of-expression (tens to hundreds) and bits-of-data
(hundreds of thousands for a 500K-row dataset) are orders of
magnitude apart, and the six other axes live in `[0, 1]`. Default
normalization:

| Axis | Raw scale | Normalized form | Typical range |
|---|---|---|---|
| Simplicity | AST bits | per-node bits = `L(expr) / n_nodes` | `[0, 10]` |
| Fit | data bits | per-sample bits = `L(data|expr) / n_samples` | `[0, 20]` |
| Basis projection | `[0, 1]` max-of-three | unchanged | `[0, 1]` |
| Calibration alignment | `[0, 1]` frac recovered | `1 − frac_recovered` | `[0, 1]` |
| Residual structure | `[0, 1]` max-of-three | `1 − residual_score` | `[0, 1]` |
| Affordance gain | `[0, ∞)` max-of-seven | `1 − min(1, affordance_max)` | `[0, 1]` |
| Reconstructability | `[0, 1]` min accuracy | `1 − reconstructability` | `[0, 1]` |
| AST diversity | `[0, 1]` similarity | unchanged | `[0, 1]` |

### 6.0.2 Coefficient defaults (v0.3.1, PROVISIONAL)

```
α = 0.1     # simplicity — per-node bits; light because trees are small
β = 1.0     # fit — per-sample bits; the anchor scale
γ = 5.0     # basis projection — load-bearing, heavy penalty on dependence
δ = +∞      # calibration — HARD REJECTION on total failure (§9.1 gate)
            # otherwise 2.0 × (1 − calibration_alignment)
ε = 1.0     # residual structure — substantial but not dominant
ζ = 1.0     # affordance gain — substantial but not dominant
η = 0.5     # reconstructability — moderate inverse pressure
θ = 0.3     # AST diversity — light shape-diversity pressure
```

**These values are guesses.** The first cheap-path run (Tink 1
anchor-rediscovery on F003) is the coefficient-calibration pass.
Expected outcome:

- F003 lands top-10 on aggregate score → current coefficients
  approximately correct; minor tuning on run-2
- F003 lands top-100 but not top-10 → raise `γ` and/or lower `α, β`;
  the scorer under-weights novelty relative to fit
- F003 not in top-100 → scorer is miscalibrated at the scale level,
  not the coefficient level; investigate normalization before
  tuning further

The **coefficient-sensitivity audit** (§9.1 new failure-mode row
"Pareto-front dominance bias") is the honesty mechanism for
acknowledging that starting values are guesses. Every shelf-promoted
candidate must survive coefficient perturbation at ±20% on each
weight, with Pareto-front composition stable on at least one of the
three triple axes. Candidates whose promotion depends on a specific
coefficient value are not shelf-worthy.

**Axis definitions (with operational forms):**

| Axis | Symbol | Range | Measures | Operational form |
|---|---|---|---|---|
| Simplicity | `α · L(expr)` | `[0, ∞)` | Description length of the expression tree | Huffman-coded AST bits + symbol-table bits |
| Fit | `β · L(data|expr)` | `[0, ∞)` | Description length of data given the transformation | Gaussian residual code on reconstructed features |
| Basis projection | `γ · basis_projection_score` | `[0, 1]` | Functional-span overlap with known identities | `max(R²_lin, R²_kern, MI_norm)` per §2.1 |
| Calibration alignment | `δ · (1 − frac_anchors_recovered)` | `[0, 1]` | Fraction of battery anchors the scorer places top-N | Per §7 battery |
| Residual structure | `ε · (1 − randomness(residuals))` | `[0, 1]` | Non-random pattern remaining after transformation | Autocorrelation + Ljung-Box statistic + compression ratio of residuals |
| Affordance gain | `ζ · (1 − max(affordance_scores))` | `[0, 1]` | How much downstream detectability improves | Per §1.2 probe set |
| Reconstructability | `η · (1 − inverse_model_accuracy)` | `[0, 1]` | Whether declared preserves can be recovered from transformed features | Per §6.4 |
| AST diversity penalty | `θ · similarity(expr, explored)` | `[0, 1]` | Penalty for redundancy with previously-explored tree shapes | Per §6.5 replay-buffer |

**Aggregate scalar** used for initial ranking = sum of weighted axes.
**Pareto-front promotion** replaces pure scalar minimization: the
top-K promoted set is the non-dominated frontier on a pinned **three-
axis substrate-value triple**:

```
Pareto-front axes (v0.3.1 default):
  (1 − basis_projection_score)   [novelty — orthogonal to identity basis]
  affordance_gain_normalized      [downstream usefulness]
  reconstructability              [faithfulness — inverse-model accuracy]
```

**Why this triple, and why not include `fit`.** The aggregate scalar
already handles fit and simplicity via `β·L(data|expr) + α·L(expr)`.
Including fit in the Pareto-front makes the front highly correlated
with the scalar ranking — the front becomes redundant with the
ranking. The right move is a Pareto-front **orthogonal** to the
aggregate scalar's emphasis: surfacing candidates that might lose on
overall compression/fit but win on a specific substrate-value axis
that a compression-first scorer underweights.

The triple `(novelty, usefulness, faithfulness)` captures three
independent ways a transformation can be substrate-valuable:
- **Novelty** — it's not a rearrangement of what we already encoded
- **Usefulness** — it makes a downstream measurement easier
- **Faithfulness** — its declared `preserves` actually round-trip

A candidate dominated on all three is not substrate-interesting
regardless of MDL; a candidate non-dominated on ≥ 1 is retained for
audit even if its aggregate scalar is middling. This is what surfaces
the F011-shaped "statistical deficit that doesn't compress well but
reveals structure on residuals" class of finding that naive MDL would
lose.

**Alternative triples** (declared per-run): some research questions
may warrant different axes. Valid alternatives include
`(novelty, residual_structure, reconstructability)` for
phase-transition-style discovery, or
`(novelty, affordance_gain, calibration_alignment)` for anchor-adjacent
terrain. The triple choice is a SIGNATURE field; default is the one
above.

**Hard rejection remains for exactly two cases (v0.3.1 principled
retention):**

1. **Type-level Framing B violation.** `preserves`/`destroys`/`affordances`
   not declared, or expression has forbidden output shape (§1.1).
2. **Calibration battery total failure.** `frac_anchors_recovered = 0`
   for in-grammar anchors.

**Why these two, and no others.** The v0.3.1 reframe commits to
continuous discipline "inside the pipeline." But these two rejections
are not about candidate quality along an axis — they are about two
distinct categories of failure that continuous pressure cannot
address:

- **Framing B enforces what the instrument IS.** A candidate that
  outputs `X = Y` is categorically a different kind of thing from a
  transformation. Making this continuous ("90% transformation, 10%
  claim") would be category confusion, not epistemic humility. The
  rule is semantic: an expression whose *natural reading is an
  assertion of truth across the dataset* is forbidden. An expression
  that *uses comparison operators as part of an object-level
  transformation* (e.g., a Boolean feature `σ(x) = [j(x) > 1728]`) is
  fine — it's a transformation whose image is `{0, 1}`, not a claim.

- **Calibration total failure means the scorer itself is
  uncalibrated.** If the instrument cannot recover any known anchor
  from a grammar that demonstrably contains them, the scorer's
  verdict on non-anchor candidates is not "worse-ranked"; it is
  structurally untrustworthy. Soft pressure (δ-penalty scaling) on a
  broken scorer just means we promote less-bad garbage. The gate
  exists to prevent broken-scorer outputs from entering review at
  all.

Both rejections have the property: continuous pressure is
*categorically inappropriate*, not just weaker. Every other
discipline layer addresses "how good is this candidate on an axis"
— the right move there is continuous. These two address "is this
output the kind of thing the instrument produces" and "is the
instrument working" — categorical, not continuous.

**All other discipline is continuous.** Pattern-30 / lineage tagging
(§2) still sets atom-level closure tags, but the `basis_projection_score`
uses those tags as *input*, not as a gate. A candidate with strong
atom-level closure AND high `R²_kern` is penalized heavily via `γ`
but still appears on the Pareto front, still has a SIGNATURE, still
is auditable. The discipline is encoded in the score, not in the
gate.

**Why this is better than binary:**

- **Boundary cases surface.** A candidate at `basis_projection_score
  = 0.85` and `affordance_gain = 0.6` is on the "borderline tautology
  that also usefully reduces downstream variance" boundary — this is
  exactly the kind of case where the identity basis might be
  incomplete (real novelty) OR the affordance might be spurious
  (false positive). Binary reject gives us no visibility into this
  class; Pareto-front surfaces it for audit.
- **Coefficient-sensitivity debuggable.** Running the same candidate
  set at multiple `γ` values shows how sensitive the promoted set is
  to basis-projection weight. A promoted set that changes drastically
  at `γ ∈ [1, 3]` is less trustworthy than one stable across that
  range. This is the coefficient-space analog of §6.1 encoding-
  perturbation.
- **Multi-objective accommodates structure plurality.** Per James 2E:
  structure is not always compressive. Residual structure, affordance
  gain, and reconstructability each capture a different kind of
  "is this meaningful" signal. MDL as sole proxy misses threshold
  and sparse phenomena; the seven-axis scorer gives them explicit
  weight.

**Reproducibility note:** scorer parameters (all eight coefficients +
per-axis sub-thresholds + kernel bandwidths + probe-set + inverse-model
choice + replay-buffer seed) are declared in the SIGNATURE; two runs
with identical parameters on identical data produce byte-identical
rankings (per `long_term_architecture.md §2.1` idempotence). Non-
determinism lives in an explicit seed.

### 6.1 Encoding-perturbation robustness (v0.2)

**The load-bearing observation:** MDL will optimize whatever the grammar
makes cheap. If logs are cheap, the winner will be a log law. If
polynomials are cheap, the winner will be a polynomial law. This is not
a bias — it *is* the objective. A scorer that only answers "did the
anchor rank top?" cannot distinguish structure from syntax preference.

**Required tightening of the calibration gate:**

#### A. Ordering invariance

- Run the scorer under two encoding schemes `E_base` and `E_perturbed`,
  where `E_perturbed` differs by `±20%` on the cost of each operator in
  isolation (one operator at a time; one full run per perturbed operator).
- For each perturbation, compute Kendall's τ between the top-10 anchor
  orderings under `E_base` vs `E_perturbed`.
- **Pass criterion:** `τ ≥ 0.8` for at least `(k-1)/k` of operator
  perturbations where `k` is the operator-arity count. Scorers with
  encoding-unstable top-10 are measuring syntax, not structure.

#### B. Margin test

- For each anchor in the top-N, record
  `margin(anchor) = MDL(anchor) - MDL(next_non_anchor_competitor)`.
- Under `±20%` perturbation on any operator, a robust anchor retains
  `margin_perturbed / margin_base ∈ [0.5, 2.0]`.
- **Fail:** margin collapses below `0.5×` under perturbation →
  the anchor "won" by rounding error; its verdict is unreliable.
- **Caution:** margin exceeding `2.0×` under perturbation means the
  anchor is *over*-favored by the base encoding; audit the encoding
  for implicit atom-preference before trusting the result.

#### C. Null-encoding baseline

- Build a "random grammar" with the same atom count, operator count,
  and expression-tree depth limit, but **atom names and operator
  symbols shuffled** so lineage tags no longer match real identities.
- Run the full calibration battery on this random grammar against the
  same dataset.
- **Pass criterion:** the random grammar places **zero** anchors at
  top-`K` (K pinned; default K=100).
- **Fail:** if the random grammar also "finds" F003 parity or F004
  Hasse, the anchor is "findable by any scorer on this data" — the
  statistic is a property of the data shape, not of the grammar's
  calibration. Documented in §9 failure-mode; upgrade path is richer
  anchor set or stricter null.

#### D. Per-run artifacts

Every calibration run emits:
- `encoding_perturbation_matrix`: τ per operator
- `margin_stability_matrix`: margin ratios per anchor × per perturbation
- `null_encoding_top_K`: list of expressions the random grammar ranked
  top-K and their MDL scores (for the audit trail)

A scorer without these artifacts has not been calibrated — it has only
been *tested*. The shelf-promotion gate requires all three to be
present and passing.

### 6.2 Cross-dataset consistency as a first-class artifact (v0.3)

Per James 3.3 critique: cross-dataset validation was mentioned in v0.2
but not first-class. v0.3 elevates it to a required per-run artifact.

**Protocol:** every production run is executed against **≥ 2
datasets**:

- **Primary calibration dataset.** `Q_EC_R0_D5@v1` (LMFDB rank-0 EC,
  conductor `[10⁵, 10⁶)`, `n = 559,386`).
- **Secondary cross-check dataset (at least one of):**
  - `Q_EC_R0_D4@v0` (proposed) — rank 0, conductor `[10⁴, 10⁵)`,
    smaller cohort but same claim-class, tests conductor-range
    robustness.
  - `Q_EC_R0_D6@v0` (proposed) — rank 0, conductor `[10⁶, 10⁷)`,
    larger cohort, tests scaling robustness.
  - `Q_EC_R2_D5@v0` (proposed) — rank 2 at same conductor range,
    tests whether candidates are rank-class-specific.

**Per-candidate consistency metrics (required artifact):**

```
consistency_score(candidate) = 1 - |aggregate_score_primary - aggregate_score_secondary|
                                    / max(aggregate_score_primary, aggregate_score_secondary)
```

- `consistency_score ≥ 0.9`: candidate's aggregate score survives
  dataset swap; robust.
- `consistency_score ∈ [0.7, 0.9)`: partial consistency; flag for
  audit.
- `consistency_score < 0.7`: candidate is dataset-specific; penalize
  heavily or retain only as a conditional candidate ("works on
  `Q_EC_R0_D5@v1` only").

**Per-axis consistency decomposition.** The aggregate score's axis
components are reported separately across datasets; a candidate whose
`basis_projection_score` is consistent but whose `affordance_gain`
varies by `2×` is diagnostic — the algebraic structure is stable but
the downstream utility is dataset-specific, which is informative
rather than disqualifying.

**Pareto-front promotion now requires** passing `consistency_score ≥
0.7` on at least one axis-component decomposition. Pure MDL-optimal
candidates that collapse under dataset swap do not promote.

**Composition with §4.1 affordances:** affordance measurements are
run independently on each dataset; the affordance_gain axis in the
scorer uses the *minimum* across datasets (worst-case). Candidates
that afford linear-probe gain on one dataset but not another are
surfaced as dataset-specific, not dataset-general.

### 6.3 Residual structure — non-random leftover pattern detection (v0.3)

Per James 2E critique: MDL assumes structure = compression, but some
real structure (sparse phenomena, phase transitions, threshold
effects) is not compressive in the given representation. v0.3 adds a
`residual_structure_score` axis (ε).

**Measurement:**

For a candidate transformation `σ: objects → features`:

1. Compute transformed feature vector `σ(x)` over the dataset.
2. Compute residuals `r = data - model(σ(x))` where `model` is a
   pinned simple regressor (e.g., linear regression of raw target
   against transformed features).
3. Test residuals `r` for non-random structure using three measures:
   - **Autocorrelation** of residuals ordered by conductor: lag-1
     coefficient + Ljung-Box Q statistic p-value.
   - **Compression ratio** of residual sequence under `zstd` vs under
     shuffle (deterministic patterns compress below shuffle baseline).
   - **Mutual information** between residuals and object identity
     (non-random residuals carry identity information that target-
     regression missed).
4. Aggregate: `residual_structure_score = max(1 - p_LjungBox,
   1 - compress_ratio/compress_ratio_shuffle, MI_normalized)`.
   Higher = more residual structure = transformation exposes
   something the simple regression doesn't capture.

**Why this matters:** a transformation that creates a two-hump
distribution in residuals (phase-transition signature) is exposing
structure invisible to MDL-on-forward-pass. A transformation that
produces i.i.d. residuals has compressed all legible structure into
the model; residual structure is near zero. Both are valid; they
carry different information. The scorer weights both.

**Pattern 30 interaction:** residual structure with `autocorrelation`
coefficient ≥ 0.9 AND dataset-wide is candidate for a Pattern 30
flag — residuals that dense correlate might reflect the transformation
leaving a definitional term untouched. Cross-check by computing the
autocorrelation under shuffled dataset order; persistent structure
under shuffle indicates true residual structure, not ordering artifact.

### 6.4 Reconstructability — inverse pressure against degenerate projections (v0.3)

Per James 3.4 critique: transformations that destroy too much (e.g.,
a transform that maps all objects to `0`) can score well on simplicity
and even on some "novelty" axes while being useless. v0.3 adds a
reconstructability axis (η) as a soft floor.

**Measurement:**

For a candidate with declared `preserves = {P_1, P_2, ...}`:

1. Fit a simple inverse model `invM: σ(x) → preserves(x)` on a
   train/test split. Default inverse model: gradient-boosted
   regression (XGBoost with ≤ 100 trees, depth ≤ 4) — bounded-
   complexity so it cannot memorize the training set.
2. Measure inverse-model accuracy on test set per preserved property.
   For numerical properties: `1 − NRMSE`. For categorical: classification accuracy.
3. Aggregate: `reconstructability = min(accuracy_per_preserved)`.
   A transformation must reconstruct *all* declared preserves to
   score well; partial preservation is penalized on the weakest link.

**What this catches:**

- Degenerate projections: `σ(x) = 0` for all `x` can't reconstruct
  anything → reconstructability = 0 → heavy scorer penalty even if
  simplicity is maximal.
- Over-optimistic `preserves` declarations: a candidate that claims
  to preserve `rank` but whose transformed features don't predict
  rank → declaration is falsified → reconstructability low.
- Information-lossy transformations masquerading as useful: a
  transformation whose affordance gain is high (downstream probes
  work better) but whose reconstructability is low is genuinely
  useful only for specific downstream tasks; not a general-purpose
  coordinate.

**Composition with §1.2 affordances:** reconstructability and
affordance gain are different axes. A transformation can have high
affordance for task `T` (downstream probes detect `T`) AND low
reconstructability for property `P` — the transformation is useful
for `T` but lossy for `P`. Both are measured; the scorer weights
them. A candidate with high affordance AND high reconstructability
is a general-purpose coordinate; a candidate with high affordance
AND low reconstructability is a task-specific projection (valid but
narrower).

### 6.5 AST-structure diversity — search-bias control (v0.3)

Per James 3.5 critique: GP search dynamics have structural biases
(e.g., bloating, symmetry-breaking, operator-frequency skew). v0.3
adds an `ast_diversity_penalty` axis (θ).

**Mechanism:**

1. Maintain a **replay buffer** of explored expression tree shapes.
   The buffer stores canonicalized AST hashes (sub-tree ordering
   normalized, variable-name-substituted) with occurrence counts.
2. For each new candidate, compute `similarity(expr, buffer)` =
   weighted mean of (1 − Hamming distance between canonical hashes)
   over top-K nearest buffer entries.
3. Penalty: `ast_diversity_penalty = similarity(expr, buffer)` ∈
   `[0, 1]`. Higher = candidate is redundant with previously-explored
   shapes.

**Scorer integration:** `θ · ast_diversity_penalty` enters the scalar
aggregate with default `θ = 0.2`. A candidate repeating a
previously-explored shape pays a small cost; a candidate with a novel
tree shape is rewarded.

**Buffer-management discipline:**

- Buffer is per-run, seeded empty; does NOT persist across runs
  (persistence would bias results by replay history).
- Canonical-hash computation is pinned in SIGNATURE.
- Buffer max size = max(1000, 10% of iteration_budget); eviction by
  FIFO on hash-age (not by score).

**Why this matters:** GP populations collapse to local structural
optima if unconstrained. Diversity pressure on tree shape
complements MAP-Elites behavioral diversity — MAP enforces output
diversity (different cells), θ enforces input diversity (different
tree shapes). Both are needed; either alone leaves a failure mode.

---

## 7. Calibration-first — no novel output until anchors pass

Before the MAP-Elites archive is treated as a source of candidates, the
generator must rediscover known-true structure. The **calibration
battery** is the go/no-go gate:

| Anchor | Target expression | Pattern 30 level | Expected MAP placement |
|---|---|---|---|
| F003 | `(−1)^rank = root_number` | Level 4 IDENTITY | top of `categorical × categorical` niche |
| F004 | `\|a_p\| ≤ 2√p` (inequality form) | Level 4 IDENTITY | top of `ordinal × magnitude` niche |
| F001 | `a_p(E) = a_p(f)` (EC ↔ modular form) | Level 4 IDENTITY | *may not be in grammar's reach; documented if so* |
| F002 | Mazur torsion ⊂ 15 classes | Level 4 IDENTITY | top of `categorical` niche |
| F008 | Scholz reflection ratio ≈ 3 | Level 4 IDENTITY | top of `categorical × magnitude` niche |

**Pass criterion:** all in-grammar anchors land in their expected niches
at top-N% MDL *within the first K candidates* (K, N pinned per run;
proposal: K=1000, N=top 5%). If not, the generator is miscalibrated —
its verdict on novel candidates is untrustworthy. **No promotion of
non-anchor candidates before calibration passes.** This is
`feedback_phoneme_killed.md` generalized.

**Calibration failure modes to watch for:**
- Anchor reaches MAP but at low MDL rank → scorer weights wrong
- Anchor not in any niche → taxonomy gap (see §5 discipline)
- Anchor discovered with wrong algebraic form → grammar lineage tag
  incomplete; definitional coupling wasn't caught
- Anchors in-grammar but not discovered within K → search operators
  too weak; grammar too large; or the anchor doesn't actually live
  where we think (*this itself is terrain data — document in
  `abandon_log.md`*)

---

## 8. Target class — where to start

James's original listed targets: integer sequences, graphs,
combinatorial identities, recurrence relations.

| Target | Fit | Notes |
|---|---|---|
| Integer sequences (OEIS-style) | LOW for substrate growth | Heavy prior art; calibration via OEIS is external. Useful as a sanity check but not substrate-aligned. |
| Graph invariants | LOW–MEDIUM | Well-mapped combinatorics; weak intersection with existing Prometheus F-IDs. |
| Combinatorial identities | LOW | Gosper/Zeilberger already proof-produce these; downstream of mature tooling. |
| Recurrence relations | MEDIUM | Sloane territory; candidate if framed as `a_p`-recurrences on EC. |
| **LMFDB rank-0 EC invariants** | **HIGH** | Calibration anchors F001–F009 live here; substrate knows the space; grammar atomic-set already partly specified via BSD lineage. **Preferred starting target.** |
| LMFDB number fields | HIGH | Scholz reflection (F008), Serre-Mazur (F009) live here; second target. |
| Zero-spacing statistics | MEDIUM-HIGH | F011/F013 live here; statistical rather than algebraic grammar needed — different generator shape; defer to v2. |

**Recommended first target: LMFDB rank-0 EC at `Q_EC_R0_D5@v1`** (the
dataset symbol is already pinned, n=559,386). Grammar seed in §4 is
first-pass. Calibration anchors F001–F005 + F008 are all evaluable on
this data or on trivial extensions.

---

## 9. Failure mode declaration (v0.3)

Per James's discipline: *if you can't state what the instrument fails
on, you don't understand the instrument yet.* This section is a
standing commitment, not a post-hoc audit. v0.3 updates for continuous
metrics — failure modes are no longer about binary-gate bypass but
about multi-axis signal corruption.

### 9.1 Expected false positives (v0.3, continuous-metric analogs)

| Failure mode | Mechanism | Guard | Residual risk |
|---|---|---|---|
| **Non-linear identity couplings** | Candidate `E` lies in the non-linear span of the identity basis (multiplicative, compositional, monotone) | §2.1 multi-kernel `basis_projection_score = max(R²_lin, R²_kern, MI_norm)` | A true rearrangement expressed in a form none of the three measures captures; v1+ upgrade = symbolic canonicalization |
| **Incomplete identity basis** | A candidate "passes" the basis-projection check because the relevant identity was never encoded in the basis | Per-run report surfaces `basis_projection_score` distribution across candidates; histograms with bimodal-at-zero signal thin basis | Silent false negatives when entire identity families are missing from the basis; mitigation = cross-dataset consistency (§6.2) |
| **Grammar-advantaged functional forms** | MDL prefers whatever the grammar makes cheap; if `log` is cheap, log-laws win regardless of truth | §6.1 encoding-perturbation test (ordering τ + margin stability + null-encoding baseline) | Structural bias the perturbation set doesn't cover (atom-inclusion bias, depth-limit bias); partial mitigation = cross-grammar test in Tink 4 |
| **Calibration-mimicking combinators** | Expression numerically matches anchors on one dataset without being the same structure | §6.2 cross-dataset consistency metric; flag candidates with `consistency_score < 0.7` | A combinator that coincidentally matches on both `Q_EC_R0_D5@v1` AND `Q_EC_R0_D4@v0` by two-dataset accident; mitigation = third dataset or claim-class-appropriate null |
| **Reward-signal capture on declared niches** | MAP-Elites converges tightly on `AXIS_CLASS` cells; "full MAP" misread as success | §5.1 residual channel + §5.2 auto-descriptor stability test + out-of-MAP fraction threshold | Dense MAP with empty residual is ambiguous — treated as warning, not pass; human review gate is the tiebreaker |
| **Anchor-shaped artifacts** | Grammar's atoms implicitly encode the anchor; "discovering" it is trivial given the atoms | §6.1.C null-encoding baseline + Tink 4 cross-grammar convergence | A grammar whose atoms individually look generic but whose product includes anchor structure; mitigation = v1 cross-grammar attack discipline |
| **Degenerate projections via simplicity pressure** | High-simplicity transformations that destroy everything (e.g., `σ(x) = 0`) score well on `α·L(expr)` + `β·L(data|expr)` in a pathological way | §6.4 reconstructability axis η imposes inverse-model floor | Transformations with high affordance for narrow task BUT low reconstructability are task-specific, surfaced explicitly rather than rejected |
| **GP search collapse to local shape optima** | Tree-shape bias causes the archive to re-explore structural local optima; diversity is in output (MAP) but not in input (tree shape) | §6.5 AST-diversity penalty θ + replay buffer | Replay buffer is per-run; cross-run structural bias accumulates in the broader grammar-usage patterns and is not caught at the per-run level |
| **Dataset-specific affordance inflation** | `affordance_gain` high on one dataset but not others, masking scorer bias | §6.2 cross-dataset decomposes affordances per-dataset; minimum used in aggregate | A cohort artifact that persists across both calibration datasets but would fail on a third; mitigation = ≥ 3 datasets for shelf-promotion at v1 |
| **Pareto-front dominance bias** | The "non-dominated" set can be dominated by whichever axes are heavily weighted; coefficient choice biases which structure survives | Coefficient-sensitivity audit — run the same candidate set at 3 coefficient settings; report stability of Pareto front | Underlying coefficient choice is itself a coordinate decision (meta-Pattern 6); surfaces as recurring failure at the scoring-hyperparameter layer |

### 9.2 Structure this instrument CANNOT see

These are *structural* blind spots, not tuning issues. No amount of
calibration eliminates them; they define the instrument's horizon.

- **Structure requiring atomic variables outside the grammar.** Any
  invariant expressible only via atoms we haven't included is
  invisible. Running the generator is NOT evidence such structure is
  absent — only that the grammar-covered form is absent. **Null
  results from this instrument are conditional on grammar scope,
  always.**
- **Higher-level / analytic / categorical structure.** Automorphic
  lifts, Galois representations as functors, L-function analytic
  continuation — anything living as a relation between object classes
  rather than as an expression over atomic invariants of one object.
  F001 modularity is probably in this class: we can match `a_p`
  numerically but cannot derive the modular-form side from EC atoms.
- **Conditional / existential / quantified claims.** "There exist
  infinitely many X with Y" or "For all X satisfying C, P(X) holds."
  MDL does not naturally encode quantifiers. Candidates of this shape
  are silently unrepresented. We explicitly DO NOT claim coverage of
  this class.
- **Non-arithmetic structure.** Analytic, topological, measure-
  theoretic, or categorical structure native to the object class but
  not expressible in the atom set. Example: F013's zero-spacing
  rigidity lives in spectral statistics, not algebraic invariants;
  this generator won't touch it without a separate grammar for
  spectral-statistics atoms.
- **Structure requiring un-bounded expression depth.** The grammar
  pins `max_depth`; deeper-than-max expressions are invisible. Raising
  the bound is a grammar-choice, not a discovery.
- **Cross-object structure.** Any claim of the form "property P of
  object X is controlled by property Q of object Y" for distinct X,
  Y — the grammar operates per-object by construction.

### 9.3 What the failure-mode declaration guarantees

A promoted candidate from this generator carries, in its SIGNATURE
(v0.3-extended):

- The grammar spec (atoms + operators + depth + lineage tags) active
  at generation time
- The identity basis used for §2.1 basis-projection check
- The calibration battery pass record (§7) and encoding-perturbation
  artifacts (§6.1.D)
- The `preserves` / `destroys` / **`affordances`** declaration (§1.1)
- The residual-channel state (§5.1) and any auto-descriptor proposals
  from the run (§5.2)
- **Seven-axis score breakdown** (§6): individual component values for
  (simplicity, fit, basis_projection, calibration_alignment,
  residual_structure, affordance_gain, reconstructability,
  ast_diversity_penalty)
- **Cross-dataset consistency metrics** (§6.2): per-axis component
  variance across the ≥ 2 datasets used in the run
- **Pareto-front position:** which axes the candidate is non-dominated
  on, and against which dominating candidates it was measured
- **Coefficient-sensitivity record** (optional but recommended for
  v1 shelf): how the candidate's rank changes under ±20% perturbation
  of each scorer coefficient

**That SIGNATURE does NOT carry a claim of "this is the deepest
structure in the data."** It carries a claim of "this is a coordinate
transformation that passed a specific set of gates operational on
date D, grammar G, data Q." A future Harmonia reading the SIGNATURE
can decide whether those gates were appropriate for their question —
and can re-run the same gates against the same data to verify.

The instrument's reach is bounded. Declaring the bound up front is
the discipline.

---

## 10. First tinkering experiments (what James wants to do)

Per James 2026-04-23: "tinkering is what might reveal something." The
draft's job is to make tinkering load-bearing rather than vibes-driven.
Three concrete tinkering experiments, in order:

### Tink 1 — "Can GP find F003 BSD parity in 1000 candidates?" (calibration anchor)

- Smallest grammar: atoms = {`rank`, `root_number`}, operators =
  {`=`, `·`, `^`, `(−1)`}, depth ≤ 4
- Objective: MDL minimization on the 559,386-row dataset
- **Expected:** `(−1)^rank = root_number` found within 100 candidates
- **Failure = instrument error**, not a negative finding

### Tink 2 — "Does the grammar produce F043 if we let it?" (red-team)

- Grammar: atoms = BSD-ingredient family with lineage tags *disabled*
- Let GP run without Pattern 30 grammar gate
- **Expected:** `corr(log Sha, log A)` appears within top-20 MDL
  candidates, reproducing F043
- **Purpose:** concrete demonstration that the Pattern 30 gate is
  necessary, not cosmetic. Also validates that the scorer behaves
  correctly on a known retraction.

### Tink 3 — "Empty niche scan" (first novelty probe, gated)

- Gated on Tink 1 PASS and Tink 2 DEMO.
- Grammar: full BSD-lineage-tagged atoms
- Run MAP-Elites for K candidates
- Report: (a) per-niche top candidate + MDL, (b) niches with density=0
  (VACUUM signals — coordinate gaps our catalog doesn't fill), (c)
  unplaceable-candidate sample (taxonomy-stress signal per §5)
- **This is the first substrate-growth output.** No promotion; surfaces
  candidate P-IDs for `gen_11`-style review.

### Tink 4+ (deferred)

- Cross-grammar comparison (two different atom sets, same data — do the
  top candidates converge? `MULTI_PERSPECTIVE_ATTACK` applied at the
  grammar level)
- Framing A activation (claim-form candidates from MAP-Elites archive
  seeded as candidate F-IDs through `register_specimen`)

---

## 11. Graduation criteria — when does v0 become v1?

| Gate | Criterion |
|---|---|
| Charter alignment | Framing decision (A/B/both) committed in writing |
| Grammar | Definition DAG Phase-0 extended seed landed (≥60 nodes) |
| Scorer | MDL_SCORER@v1 + four-component extension paste-ready |
| Pattern 30 | Grammar-time pruning shipped in `harmonia/sweeps/pattern_30.py` |
| Calibration | Tink 1 PASSes on at least 2 anchors; Tink 2 demo reproduces F043 |
| Paste-ready | `docs/prompts/gen_12_conjecture_generator.md` spec shipped |

Only then does `CONJECTURE_GENERATOR@v1` land in `methodology_toolkit.md`
as shelf entry #9, and `gen_12` opens claimable on Agora.

---

## 12. Risks / kill conditions

| Risk | Kill condition | Mitigation |
|---|---|---|
| Reward-signal capture (novelty without calibration) | Any novel-candidate promotion before §7 gate passes | Hard block in promotion pipeline; tight `feedback_autonomous_when_idle.md` reference |
| F043 factory at scale | Any single run produces >10% Pattern 30 Level ≥ 2 candidates past the grammar gate | Gate audit + grammar rebuild; abandon if root-cause unfixable |
| Grammar overfitting to known anchors | Calibration passes but novel candidates don't ensemble-replicate across 2+ grammars | MPA-at-grammar-level (Tink 4) is the check |
| MAP-Elites taxonomy bias | Unplaceable-candidate rate >50% for 3 runs | Taxonomy extension proposed as `AXIS_CLASS@v2`; do not proceed on novel output |
| Definition DAG never stabilizes | Phase 0 drifts past ~4 weeks | Scope down to BSD-ingredient-only subgrammar; accept narrower first target |
| Scope creep (target class expands pre-v1) | Second target claimed before first target passes calibration | Re-read this section |

---

## 13. Open questions for James

1. **Framing A + B vs B-only.** B is higher-leverage but A is a natural
   by-product. Does §3 recommendation land, or do you want a B-only
   v0?
2. **Target class.** §8 recommends rank-0 EC (LMFDB, `Q_EC_R0_D5@v1`)
   as first target. Is there a reason to start elsewhere (graph
   invariants, OEIS-style, NF) that the substrate alignment misses?
3. **Tinkering scope.** §10 proposes 3 experiments (calibration,
   red-team, empty-niche). Is that the right ordering, or do you want
   to jump to Tink 3 faster?
4. **Grammar atomic set.** §4 is illustrative — which atoms would you
   want added / removed / re-tagged for lineage? The choice is
   load-bearing (Pattern 30 gate depends on it).
5. **How much to build before tinkering.** Definition DAG Phase-0
   extension + GP scaffolding + MAP-Elites archive is ~3–5 ticks
   before Tink 1 is runnable. Is that the right upfront investment, or
   should we start with a minimal hand-built grammar and GP loop
   (~1 tick) and defer the DAG extension?

---

## Version history

- **v0.3.1** — 2026-04-24 — self-check resolutions after James
  green-lighted propagation. Four focused refinements: (a) **Pareto-
  front triple** set to `(1 − basis_projection_score, affordance_gain,
  reconstructability)` — "novelty, usefulness, faithfulness" — with
  explicit rationale for excluding fit (already in aggregate scalar);
  §6 alternative-triples-per-run noted. (b) **Scale normalization**
  §6.0.1 formalized: per-node bits for `L(expr)`, per-sample bits for
  `L(data|expr)`, all other axes `[0, 1]`. Coefficient defaults §6.0.2
  explicitly labeled PROVISIONAL pending Tink 1 calibration pass;
  coefficient-sensitivity audit named as the honesty mechanism. (c)
  **Hard-rejection retention justified** §6: two gates are categorical
  not continuous — Framing B defines what the instrument IS, and
  calibration failure means the scorer itself is untrustworthy. All
  other discipline remains continuous. (d) **Affordance list expanded
  5 → 7**: added `nonlinear_probe_gain` (random forest) and
  `rank_correlation_gain` (Spearman); flagged `autocorrelation_exposure`
  as sequence-specific; null-baseline discipline formalized; max-
  aggregation explained. No structural re-architecture; all four are
  sharpenings of v0.3 decisions.
- **v0.3** — 2026-04-24 — James's five-fragility critique absorbed
  (no-claims rule over-strict, linear R² too weak, identity-basis
  moving-target, AXIS_CLASS lock-in, MDL-as-sole-proxy misses sparse/
  threshold/phase-transition structure). Bottom-line reframe:
  *shift from hard exclusion of "bad structure" to continuous
  measurement of structural independence and usefulness.* Six
  substantive changes: (a) §1.2 **affordances** as a third metadata
  slot — bridges transformation and claim without smuggling;
  Framing-A activation path refined; (b) §2.1 replaced binary R²
  gate with continuous `basis_projection_score = max(R²_lin,
  R²_kern, MI_norm)` — enters scoring as soft penalty γ, not hard
  prune; (c) §5.2 **auto-descriptor proposal** — residual clusters
  generate quantitative AXIS_CLASS extension candidates with
  stability tests; (d) §6 **seven-axis scoring** with Pareto-front
  promotion replacing scalar minimization — adds residual-structure
  (ε), affordance-gain (ζ), reconstructability (η), AST-diversity
  (θ); (e) §6.2 **cross-dataset consistency** as first-class
  artifact, not aspirational; (f) §9 failure-mode table updated to
  continuous-metric analogs, SIGNATURE contents expanded to seven-
  axis breakdown + coefficient-sensitivity record. Framing B's
  output-shape rule remains type-enforced (unchanged); the
  discipline inside the pipeline is now continuous.
- **v0.2** — 2026-04-23 — James's four-tension pushback absorbed.
  Five substantive additions: (a) §1.1 Framing B hard rule +
  `preserves`/`destroys` schema — type-enforced prevention of B→C
  collapse; (b) §2.1 algebraic dependence detection via ideal-quotient
  check — catches near-tautologies beyond exact rearrangement; (c)
  §5.1 residual channel as first-class metric with Pattern-18-at-MAP
  diagnostic table; (d) §6.1 encoding-perturbation robustness —
  ordering invariance + margin test + null-encoding baseline
  distinguishes structure from syntax preference; (e) §9 failure-mode
  declaration — expected false positives + structural blind spots +
  SIGNATURE guarantees. Reframe at top of doc acknowledges this is a
  coordinate-system discovery engine under algebraic-lineage + MDL-
  calibration constraints, not a conjecture generator. Section
  numbering shifted: old §9→10 (tinkering), §10→11 (graduation),
  §11→12 (risks), §12→13 (open questions). Decision-pending on target
  class, grammar atomic set, and merger-with-gen_11.
- **v0.1** — 2026-04-23 — incubation draft by Harmonia_M2_sessionC after
  James's proposal. Covers framing fork, F043 structural risk,
  architecture sketch, grammar worked example, MAP-Elites niche
  discipline, MDL scoring, calibration battery, first target, tinkering
  experiments, graduation criteria, risks. Decision-pending on 5
  open questions.
