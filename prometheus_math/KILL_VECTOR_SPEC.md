# Kill Vector Spec — Day 3 of the 5-day plan

**Status:** Forged 2026-05-04. Backwards-compatible. 0 regressions on the
prometheus_math test stack.

## TL;DR

The discovery pipeline's outcome is now a *vector* per candidate, not a
single categorical kill_path. Each falsifier in the battery becomes one
coordinate of the vector, with both a `triggered: bool` and a continuous
`margin: float | None` (margin to failure). The vector is the substrate
for Day-4 (a learner that reads `E[k | operator]`) and Day-5 (greedy
navigation toward the zero vector).

## Why a vector?

Yesterday's empirical archaeology over the kernel ledger showed
**0.725 bits of MI** between operators and the *binary* categorical
kill_path. That's signal in the coarsest representation imaginable.

ChatGPT's reframe (and my agreement): the underlying outcome is
naturally multi-dimensional —

```
k = (k_F1, k_F6, k_F9, k_F11, k_recip, k_irreduce, k_catalog_*, k_band)
```

and each operator induces a directional derivative `∂k / ∂operator`
in this kill-space. Search target: the zero vector (no triggered
falsifiers). Multi-objective navigation, not scalar minimisation.

Collapsing to a categorical first-trigger throws away ≥ log₂(8) ≈ 3
bits per record. Even if the per-component margins are 50% noise,
recovering them is strictly better than not.

## The 8-12 components

Every `KillVector` is built in pipeline-call order. The first three are
deterministic; catalog adapters expand to one component each (5
catalogs in the default registry); the four F-checks are the tail.

| # | Falsifier | Triggered when | Margin | Unit | Computable cheaply? |
|---|-----------|----------------|--------|------|----------|
| 1 | `out_of_band` | `M ∉ (1.001, 1.18)` | `M - 1.18` (signed; negative when below 1.001) | `absolute` | yes |
| 2 | `reciprocity` | poly is not palindromic | `max\|c_i - c_{n-1-i}\|` | `absolute` | yes |
| 3 | `irreducibility` | `factor_list` returns >1 factor | `count_factors` | `absolute` | yes |
| 4..8 | `catalog:<name>` | adapter hits | `match_distance` if hit; `+inf` if no near match; `None` on adapter error | `hamming` | yes (when adapter live) |
| 9 | `F1_permutation_null` | observed M ≥ median permutation M | **deferred** (`1 - p_value` requires N≥1000 perms; today we run 30) | `p_value` | NO — deferred |
| 10 | `F6_base_rate` | trivial coefficient structure | `#distinct_nonzero - 2` (signed; negative = killed) | `z_score` | yes (parsed from rationale) |
| 11 | `F9_simpler_explanation` | cyclotomic explanation suspected | `M - 1.001` (cyclotomic gap) | `absolute` | yes |
| 12 | `F11_cross_validation` | cross-val mismatch | `\|M_a - M_b\|` (parsed from rationale; otherwise `None`) | `absolute` | yes |

### Cheap vs deferred

**Cheap** (computed at pipeline-time without any new code in the
falsifier internals):

- out_of_band, reciprocity, irreducibility — all derive from inputs we
  already have.
- catalog:* — `CatalogResult.match_distance` is already on the result;
  we just plumb it through.
- F6 — parsed out of the existing rationale string regex.
- F9 — `M - 1.001` is the cyclotomic gap; trivial.
- F11 — when there's a numeric mismatch the rationale carries it; we
  parse it.

**Deferred** (would require re-running the falsifier with extra
instrumentation):

- **F1's p-value.** Today's `_f1_permutation_null` runs 30 perms and
  reports `M < median(perm_Ms)`. The proper p-value would be the rank
  of observed M against the null distribution; getting a stable p-value
  needs ≥ 1000 perms. That's a 30× cost increase per F1 invocation —
  not worth it for the MVP. Day-4 learner will treat F1's component as
  triggered/not-triggered only; deferred margin = None.

The KillVector is honest about this: deferred margins are explicitly
`None`, never a fabricated value. The Day-4 learner downweights `None`
contributions in its directional-derivative estimator.

## Backwards compatibility

The legacy `DiscoveryRecord.kill_pattern: str | None` is preserved.
`DiscoveryRecord` gains a new field `kill_vector: KillVector | None`
(default None for legacy callers). Old code reading `record.kill_pattern`
continues to work.

For old data already in pilot JSON / kernel ledger:

- `kill_vector_from_legacy(record_dict)` reconstructs as much of a
  KillVector as possible from a legacy `DiscoveryRecord`-shaped dict.
- When `check_results` survived in the legacy record (most cases), the
  full margin-extraction path runs.
- When only `kill_pattern: str` survived, a minimal vector is
  synthesized — out_of_band component plus the single triggered
  component named by the legacy string. Margins are `None` where the
  data isn't recoverable. Don't fabricate.

The round-trip `kill_vector → to_legacy_kill_path() → str` matches the
original `kill_pattern` modulo trailing rationale truncation. Tested.

## Magnitude — the unit-combination question

This is the genuinely hard part: how do you combine a `p_value ∈ [0,1]`,
a signed `z_score ∈ R`, and a `hamming_distance ∈ N`?

### Option A: unit-aware squash (default; `magnitude(unit_aware=True)`)

Each `(margin, unit)` pair is mapped to `[0, 1]` saturated kill-strength
via a unit-specific squash:

| Unit | Squash |
|------|--------|
| `p_value` | `clip(margin, 0, 1)` (margin is `1 - p_value`) |
| `z_score` | `\|z\| / (\|z\| + 2)` (z=2 ≈ 0.5 saturated) |
| `hamming` | `1 - 1/(1 + d)` (d=0 → 0; d=1 → 0.5; d→∞ → 1) |
| `absolute` | `\|x\| / (\|x\| + 1)` |
| `log_distance` | `exp(-max(0, x))` |
| `boolean` | identity |

Then `magnitude = sqrt(sum_i squashed_i^2)` over triggered components.

**Pro:** Comparable across falsifiers; near-misses on F1 (p=0.04 →
margin 0.96) are commensurable with near-misses on catalog (Hamming 1).

**Con:** The squash characteristic constants (Z=2, +1) are arbitrary.
Different choices change the relative weight by ~2×. Documented; will
revisit when the Day-4 learner is sensitive to the specific scaling.

### Option B: raw L2 (`magnitude(unit_aware=False)`)

Just `sqrt(sum_i margin_i^2)` over triggered components with finite
numeric margins. **Use only when components share a unit** — i.e.
within-falsifier comparisons. Otherwise the raw norm is unitless
nonsense.

### Recommendation

Default to unit-aware. Day-4 learner will likely use the squashed
margins directly (one feature per component) rather than the scalar
magnitude — at which point the squash constants become tunable
hyperparameters, and the magnitude is just a debug projection.

### Alternatives considered

- **Per-unit norms summed multiplicatively.** `prod(norm_unit)` rather
  than `L2(squashed)`. Rejected: zero-margin components zero out the
  product (breaks backwards-compat with "any trigger → nonzero
  magnitude").
- **Mahalanobis distance over component covariance.** Requires
  estimating the covariance matrix from data. Premature for the MVP;
  re-evaluate after Day-4 has run.

The choice is documented; this paragraph is the call-to-revisit.

## Day 4-5 plan

### Day 4: simple learner

**Input:** corpus of `(operator, KillVector)` pairs from the kernel
ledger and pilot JSONs.

**Output:** for each operator class, the per-component empirical mean

```
E[k | operator] = (
    P(F1 triggered | op),
    P(F6 triggered | op),
    ...,
    E[F1 squashed | op],
    E[F6 squashed | op],
    ...
)
```

This is what `aggregate_by_operator(vectors)` returns today. The
learner can be as simple as a sklearn `LogisticRegression` per
component (predicts whether that component triggers given operator
features), or a multi-output gradient boosting tree.

The 0.725-bit MI baseline becomes the floor: any per-component model
that doesn't beat 0.725 bits across all components is worse than the
categorical baseline.

### Day 5: greedy navigation

**Goal:** at each step, pick the operator whose `E[k | op]` is closest
to the zero vector (in the squashed-L2 sense).

```python
def greedy_step(state, learner):
    candidates = state.legal_operators()
    scored = [(op, learner.predict_kill_vector(op, state).magnitude())
              for op in candidates]
    return min(scored, key=lambda x: x[1])[0]
```

The substrate gives us `learner.predict_kill_vector(op, state)`; the
search target is the zero vector. Greedy is a baseline; MAP-Elites or
NSGA-II would treat each component as a separate objective, but greedy
is a fair smoke test for whether the kill-vector representation buys
any signal at all.

## Open questions

1. **Squash constants.** Z_CHARACTERISTIC=2 and the `+1` Hamming
   stretch were picked by intuition. Day-4 will tell us how sensitive
   the learner is.

2. **Catalog component weighting.** Five catalog components, four
   F-component falsifiers, three structural checks. The catalog
   components dominate the squashed-L2 simply by count. Should we
   normalise? (One option: aggregate the five catalogs into a single
   `catalog:_aggregate` component for magnitude computation, but keep
   them split for the learner.)

3. **F1 p-value.** Worth the 30× cost? Probably yes for any candidate
   that survives to claim minting. We could add a `compute_f1_p_value`
   side-call that re-runs F1 with N=1000 only for survivors. Day-4 may
   surface a clear value-of-information argument.

4. **Stratified margins.** Some component margins (catalog Hamming, F11
   drift) are heavy-tailed; the squash compresses extreme values too
   aggressively. Open question whether log-scaling the margin first
   helps the learner.

5. **Margin combination across falsifiers.** A near-miss on F6 + a
   survival on everything else is structurally different from a clear
   F6 kill alone. Today's `magnitude` doesn't distinguish them. Day-5
   greedy navigation will surface whether this matters.

## Files

- `prometheus_math/kill_vector.py` — `KillComponent`, `KillVector`,
  margin-extraction helpers, legacy backfill, aggregation.
- `prometheus_math/discovery_pipeline.py` — `DiscoveryRecord` extended
  with optional `kill_vector` field; `process_candidate` emits a
  KillVector at every exit point.
- `prometheus_math/tests/test_kill_vector.py` — 17 tests
  (4 authority + 4 property + 5 edge + 4 composition).

## Provenance

- 2026-05-04 forged Day 3 of the 5-day plan; substrate-level change
  unblocks Day-4 learner and Day-5 greedy navigation.
