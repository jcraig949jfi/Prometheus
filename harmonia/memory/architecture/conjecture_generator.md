# Conjecture Generator (Structure Hunter)

**Status:** v0.2 DRAFT — incubation, not yet candidate. Pre-spec.
**Proposed by:** Harmonia_M2_sessionC with James, 2026-04-23.
**Slot:** architectural primitive / candidate generator #12.
**Decision required before v1:** target class (§8), grammar atomic set +
lineage closure (§4), merger-or-sibling with `gen_11` (§13).

**Reframe (v0.2, per James 2026-04-23):** this is not a "conjecture
generator." It is a **coordinate-system discovery engine constrained
by algebraic-lineage pruning and MDL-with-encoding-robustness
calibration.** Framing A is a derived artifact, not a primary output.
Every candidate is a coordinate transformation with a declared
`preserves` / `destroys` audit; candidates that assert invariants are
type-rejected before scoring.

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

**Mandatory declaration per candidate:**
- `preserves`: list of algebraic properties, distributional moments, or
  relational structures that round-trip through the transformation.
  ("Rank is preserved." "Per-decile variance is preserved." "Isogeny
  equivalence is preserved.")
- `destroys`: list of properties lost — two objects distinct under the
  source coordinate that become indistinguishable under the
  transformation. ("Sign of `a_p` is destroyed." "Magnitude below
  `log N = 5` is quantized.")

**Candidates that cannot fill both fields are type-rejected pre-scoring.**
A projection without a `preserves` / `destroys` audit is an information-
lossy compression masquerading as a coordinate. The audit schema is
what separates a coordinate system from a claim.

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

**Needed upgrade: ideal-quotient check.** Given the known-identity basis
`{I_1, ..., I_k}` (BSD identity, Hasse bound, Mazur torsion classes,
Scholz reflection, modularity trace, Szpiro-Faltings definitional
coupling, etc.) **materialized as vectors on the calibration dataset**,
a candidate expression `E` is checked for membership in the linear
span these generate. Concretely, for v0:

1. Compute `E(x)` over the calibration dataset (vector of length `n_objects`).
2. Compute `I_j(x)` over the same dataset for each `j`.
3. Regress `E ~ α_0 + α_1 I_1 + ... + α_k I_k + ε`.
4. Classify by `R²`:
   - `R² ≥ 0.99`: `ALGEBRAICALLY_DEPENDENT_LEVEL_3` (hard reject; functionally a rearrangement)
   - `R² ∈ [0.90, 0.99)`: `ALGEBRAICALLY_DEPENDENT_LEVEL_2` (hard reject with audit-record)
   - `R² ∈ [0.60, 0.90)`: `NEAR_TAUTOLOGY_LEVEL_1` (advisory flag; scorer penalty γ'; still scoreable)
   - `R² < 0.60`: `CLEAN`

Thresholds pinned per-run in SIGNATURE. This is NOT a symbolic-algebra
check; it's a **functional-redundancy check** — orthogonal to the
atom-tag lineage gate and complementary to it. Expressions can pass the
atom gate (distinct atomic closure) and still fail the quotient check
(numerical span of identity basis).

**Honest caveats (logged in §9 failure-mode):**
- False positives: a genuinely new finding that happens to span the
  identity basis numerically on the calibration dataset but not
  structurally. Mitigation: re-test on independent dataset; surface
  for human adjudication.
- False negatives: a true rearrangement expressed in a non-linear
  form that the regression misses. Upgrade path: non-linear
  identity-span check (kernel regression; symbolic canonicalization);
  deferred to v1+.

**The grammar is not just typed variables with lineage. It is:**

> Typed variables + lineage tags + **forbidden subspaces** in the
> functional span of the known-identity basis.

That forbidden-subspace discipline is what prevents the F043 explosion
beyond what atom-level typing alone would catch.

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

---

## 6. Scoring — MDL with pinned tradeoff

`MDL_SCORER@v1` gives `L(model) + L(data|model)` in bits. We extend to
four-component scoring for the conjecture generator:

```
score(expr) = α · L(expr)                    [simplicity — shorter = better]
            + β · L(data | expr)              [explanatory — tighter fit = better]
            + γ · pattern_30_penalty(expr)    [≥ 2 = +∞; 1 = small penalty; 0 = 0]
            + δ · calibration_penalty(expr)   [fails to recover anchors = +∞]
```

**Tradeoff parameters (α, β, γ, δ) pinned per-run.** Default: α=β=1 (pure
MDL), γ=∞ (hard reject Level ≥ 2), δ=∞ (hard reject calibration
failures). A shelf candidate is an expression that passes calibration
AND has Level ≤ 1 AND achieves competitive MDL against known-anchor
baselines.

**Reproducibility note:** scorer parameters are declared in the run's
SIGNATURE; two runs with identical parameters on identical data must
produce byte-identical rankings (per `long_term_architecture.md §2.1`
idempotence discipline). Non-determinism in GP goes into an explicit
seed parameter.

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

## 9. Failure mode declaration (v0.2)

Per James's discipline: *if you can't state what the instrument fails
on, you don't understand the instrument yet.* This section is a
standing commitment, not a post-hoc audit.

### 9.1 Expected false positives

| Failure mode | Mechanism | Guard | Residual risk |
|---|---|---|---|
| **Numerically-spanning expressions** | Candidate `E` lies in the linear span of the identity basis on the calibration dataset without a true algebraic relation | §2.1 ideal-quotient check catches `R² ≥ 0.9` | A genuinely new quantity whose leading-order behavior happens to span the basis → surfaces for human adjudication, not auto-prune |
| **Grammar-advantaged functional forms** | MDL prefers whatever the grammar makes cheap; if `log` is cheap, log-laws win regardless of truth | §6.1 encoding-perturbation test; null-encoding baseline | Structural bias the perturbation set doesn't cover (e.g., we only vary operator costs, not atom-inclusion) |
| **Calibration-mimicking combinators** | Expression numerically matches F001–F009 on the dataset without being the same structure | §7 calibration battery; δ penalty for failed anchors | A false positive that coincidentally matches the anchor on `Q_EC_R0_D5@v1` but would diverge on a different subset — partial mitigation via cross-dataset check |
| **Reward-signal capture on declared niches** | MAP-Elites converges tightly on pre-declared cells; "full MAP" misread as success | §5.1 residual channel + out-of-MAP fraction threshold | If residual is empty AND full, ambiguous — defaults to warning, not failure |
| **Anchor-shaped artifacts** | Grammar's atom selection implicitly encodes the anchor; "discovering" the anchor is trivial given the atoms | §6.1.C null-encoding baseline + cross-grammar test (Tink 4) | A grammar whose atoms individually look generic but whose product happens to include anchor structure |

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

A promoted candidate from this generator carries, in its SIGNATURE:

- The grammar spec (atoms + operators + depth + lineage tags) active
  at generation time
- The identity basis used for §2.1 ideal-quotient check
- The calibration battery pass record (§7) and encoding-perturbation
  artifacts (§6.1.D)
- The `preserves` / `destroys` declaration (§1.1)
- The residual-channel state (§5.1) at the time the candidate was
  promoted

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
