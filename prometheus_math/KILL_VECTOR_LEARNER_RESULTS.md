# Kill Vector Learner — Day 4 Results

Day 4 of the 5-day kill-space pivot. Asks the empirical question: **is
the gradient field even learnable from the existing ledger?**

ChatGPT's framing: input = `(region_meta, operator)`; output = predicted
`kill_vector`. Plain regression — no RL, no neural net. If MAE on
held-out is meaningfully better than predicting the global mean, the
substrate has a learnable gradient field. If the learner doesn't beat
the per-(region, operator) cell-mean baseline, then "learning" reduces
to "look up the table."

Generated 2026-05-04.

## Setup

### The question

Does the existing 314,971-record kill ledger contain learnable
structure that maps `(state, operator) -> predicted kill_vector`, or
is the ledger a flat lookup with no generalisation?

### Data

Source: 16 pilot JSONs across the Lehmer-family arsenal
(`_catalog_seeded_pilot.json`, the four-count files, the degree
sweep, the v2/v3 cells). Each pilot persists kills as
**aggregated per-(region, operator) counts**, not per-candidate
records — the crucial sparseness finding from Day 2.

Each aggregated row gives `(region, operator, kill_pattern, count)`.
We expand each row into ``count`` individual `LearnerRecord`s with
``triggered=True`` for the matching kill-vector component and
``triggered=False`` for the other 11. The "False for others" is a
**conservative conditional** rather than a measured outcome — the
legacy ledger only logs the first-failing component, so we can't
say from this data whether component 7 would have fired had
component 4 not. The Day-3 KillVector representation captures both
in a single row going forward, but that backfill is unavailable for
the 315k-record legacy corpus.

To prevent runtime blowup on the largest cell (`upstream:cyclotomic_or_large`,
~130k kills), we cap expansion at **5,000 rows per cell** and carry
the original count as a `weight` on each row. sklearn handles
``sample_weight`` natively for both LogisticRegression and
LinearRegression.

### Architecture

For each of the 12 canonical kill_vector components:

  * **triggered** : sklearn `LogisticRegression(solver="liblinear",
    max_iter=2000, random_state=42)` on (region one-hot, operator
    one-hot, degree, alphabet_width, reward_shape one-hot).
  * **margin** : sklearn `LinearRegression()` on the same features —
    only fitted when ≥5 records have a recoverable margin. The
    legacy ledger has none, so margin models are empty for this
    pass; they will populate when the Day-3 KillVector is wired into
    `discovery_pipeline.process_candidate` going forward.

12 components × 2 sub-models = 24 small sklearn-style models.

**Why not a neural net?**
  - The cell count is tiny (6 regions × 7 operators = 42 cells, only
    15 non-empty). A NN would memorize the table.
  - Linear models degrade gracefully on sparse cells.
  - Logistic-regression coefficients are interpretable: each (region,
    operator) feature's coefficient says how it shifts the kill
    probability of each component.

### Baselines

  1. **Global mean** : predict the global mean kill_vector for every
     test row.
  2. **Region mean** : predict the per-region mean (region context
     only, no operator).
  3. **Operator mean** : predict the per-operator mean (operator
     only, no region).
  4. **Region × operator cell mean** : predict the per-(region,
     operator) training-cell mean. **Upper bound for "no learning,
     just look up the table."**

A learner that beats baseline 4 has captured generalisation. A
learner that matches it has learned the table — fine for a static
lookup, useless for navigating to unseen (region, operator) cells.

### Split

Stratified by region with random seed 42. 70/10/20 train/val/test.
Regions with <4 records go entirely into train (no validation
possible); regions with <10 use a 0% val split.

## Dataset stats

  * Total expanded records: **142,773**
  * Components: **12**
  * Regions: **6** — `discovery_pipeline|deg14|w5|step`,
    `four_counts|deg{10,12,14}|w5|step`, `four_counts|deg10|w5|shaped`,
    `four_counts|deg10|w7|step`.
  * Operators: **7** — `random_null`, `random_uniform`,
    `random_seeded`, `reinforce_uniform`, `reinforce_seeded`,
    `reinforce_frozen_bias`, `reinforce_agent`.
  * Coverage matrix: **6 × 7 = 42** cells, **15 non-empty**
    (sparseness 64.3%). The empty cells reflect Stream 2's finding:
    every region's 13 arms only sample a handful of operators, and
    new pilots reuse a small core operator set across regions.
  * Train: 99,941 / Val: 14,278 / Test: 28,554

### Per-region records

| Region | n |
|---|---|
| `discovery_pipeline|deg14|w5|step` | 38,594 |
| `four_counts|deg10|w5|step` | 38,248 |
| `four_counts|deg14|w5|step` | 24,327 |
| `four_counts|deg12|w5|step` | 17,630 |
| `four_counts|deg10|w5|shaped` | 13,327 |
| `four_counts|deg10|w7|step` | 10,647 |

### Per-operator records

| Operator | n |
|---|---|
| `random_null` | 53,881 |
| `reinforce_agent` | 50,298 |
| `random_seeded` | 11,544 |
| `reinforce_frozen_bias` | 9,974 |
| `random_uniform` | 6,932 |
| `reinforce_seeded` | 5,096 |
| `reinforce_uniform` | 5,048 |

The two large-N operators are the workhorses of the four_counts
runs; the smaller operators are catalog-seeded probes.

## Held-out kill_vector MAE (lower is better)

| Model | Test KV MAE | vs. learner |
|---|---|---|
| **Learner** | **0.0002402** | — |
| Baseline (global) | 0.0002711 | learner +11% better |
| Baseline (region) | 0.0002302 | learner -4% worse |
| Baseline (operator) | 0.0002695 | learner +11% better |
| Baseline (region × operator cell) | 0.0002396 | learner ≈ baseline |

The numbers are tiny because the dataset is dominated by
`out_of_band` kills (99.9% of records — every `upstream:*` legacy
pattern routes there since those candidates were rejected by the
env's Phase-0 band check before reaching F1/F6/F9/F11). With 12
components and only 1 firing per record, naive prediction of "all
zeros" is already 11/12 = 91.7% per-row L1 error budget, so a
constant baseline does well in absolute terms. **The relative
ordering is what matters**: learner ≈ region × operator cell-mean,
both of which slightly beat the global mean.

## Per-component metrics (test set)

| Component | Learner Acc | Learner AUC | Cell Acc | Region Acc | n_pos / n_total |
|---|---|---|---|---|---|
| `out_of_band` | 0.999 | 0.971 | 0.999 | 0.999 | 28521/28554 |
| `reciprocity` | 1.000 | n/a | 1.000 | 1.000 | 0/28554 |
| `irreducibility` | 1.000 | n/a | 1.000 | 1.000 | 0/28554 |
| `catalog:Mossinghoff` | 1.000 | n/a | 1.000 | 1.000 | 0/28554 |
| `catalog:lehmer_literature` | 1.000 | n/a | 1.000 | 1.000 | 0/28554 |
| `catalog:LMFDB` | 1.000 | n/a | 1.000 | 1.000 | 0/28554 |
| `catalog:OEIS` | 1.000 | n/a | 1.000 | 1.000 | 0/28554 |
| `catalog:arXiv` | 1.000 | n/a | 1.000 | 1.000 | 0/28554 |
| `F1_permutation_null` | 1.000 | n/a | 1.000 | 1.000 | 0/28554 |
| `F6_base_rate` | 1.000 | n/a | 1.000 | 1.000 | 0/28554 |
| `F9_simpler_explanation` | 0.999 | 0.971 | 0.999 | 0.999 | 33/28554 |
| `F11_cross_validation` | 1.000 | n/a | 1.000 | 1.000 | 0/28554 |

AUC is undefined where there are zero positives in the test set
(catalog/F1/F6/F11 — these components essentially never fired in the
expanded legacy ledger, because the env labels rejection
upstream-of-pipeline). Two components with non-trivial positive rates
(`out_of_band` ~99.9% and `F9_simpler_explanation` ~0.1%) hit AUC
0.971 — a meaningful operating point but matched 1:1 by the
cell-mean baseline.

## Per-region performance

| Region | n | KV MAE | Macro Acc |
|---|---|---|---|
| `discovery_pipeline|deg14|w5|step` | 7,719 | 0.0000 | 1.000 |
| `four_counts|deg10|w5|step` | 7,650 | 0.0000 | 1.000 |
| `four_counts|deg14|w5|step` | 4,865 | 0.0000 | 1.000 |
| `four_counts|deg12|w5|step` | 3,526 | 0.0000 | 1.000 |
| `four_counts|deg10|w5|shaped` | 2,665 | 0.0026 | 0.998 |
| `four_counts|deg10|w7|step` | 2,129 | 0.0000 | 1.000 |

The `four_counts|deg10|w5|shaped` region is the only one with
non-zero MAE — that's where the F9 cyclotomic kills concentrate
(33 of the 33 positives in the test set). Width 5 with shaped
reward sees more cyclotomic-style routes, which the model
distinguishes (correctly) from the straight Phase-0 band kill that
dominates the other regions.

## Operator coordinate chart recovery

Per ChatGPT: for each operator, does the model reproduce the
empirical `E[k|operator]` over held-out data? L1 distance is the
sum-of-absolute differences between the model's mean predicted
kill-vector and the empirical mean.

| Operator | n | L1 (empirical, model) |
|---|---|---|
| `random_null` | 10,914 | 0.0045 |
| `reinforce_agent` | 9,921 | 0.0000 |
| `random_seeded` | 2,278 | 0.0000 |
| `reinforce_frozen_bias` | 2,013 | 0.0000 |
| `random_uniform` | 1,416 | 0.0000 |
| `reinforce_seeded` | 1,020 | 0.0000 |
| `reinforce_uniform` | 992 | 0.0000 |

**The most-sampled operator (`random_null`, 10,914 test rows)
matches the empirical chart to L1 = 0.0045 over a 12-dim vector
where each coordinate is in [0, 1]**. The other six operators
reproduce empirical means exactly (L1 = 0.0000 to 4 decimal
places). The model has captured the operator coordinate chart
structure as far as the training data supports.

This is a **substrate-positive** result: the ledger's per-operator
kill geometry is consistent and recoverable. But "consistent and
recoverable" is what the cell-mean baseline already delivers — the
model isn't extracting structure beyond what direct table lookup
gives.

## Verdict

# **B: Learner matches but does not beat cell-mean.**

  * Learner test KV MAE = **0.0002402**
  * Cell-mean baseline KV MAE = **0.0002396**
  * Difference: **+0.000006** (well within the 0.005 epsilon
    threshold)

No generalisation beyond memorisation. Day 5 navigation founded on
this learner is **just lookup** — for any (region, operator) cell
the model has seen, it returns the cell mean; for unseen cells, it
falls back through region or operator means.

This is **not** a representation bug (verdict C) — the learner runs
clean, predictions are well-formed, AUC is 0.971 on the
non-degenerate components. The dataset itself is the bottleneck:
once `upstream:*` patterns are mapped to the canonical
`out_of_band` component, the per-(region, operator) kill
distribution collapses to a near-trivial "one component fires,
others don't" structure that the cell-mean baseline already captures.

### Why this happened (honest reading of the data)

  1. **315k aggregated kills, 12 components, but only ~3 effectively
     used.** `out_of_band` carries 99.9% of legacy mass because
     every `upstream:*` env-rejection routes there. `F9_cyclotomic`
     carries 0.1%. The other 10 components are essentially empty in
     this corpus — their counts come from kill_vector_from_legacy
     mapping but the underlying ledger doesn't tag them.
  2. **No per-record kill vectors yet.** Pilots aggregate by
     `(arm, kill_pattern)`; we never persisted a 12-tuple per
     candidate. The Day-3 KillVector representation (just shipped)
     emits these going forward, but the legacy 315k can't be
     retroactively tagged.
  3. **Sparse coverage.** 15/42 cells = 64% sparseness. The
     workhorse cells (`reinforce_agent` × `four_counts|*`) are
     dense, but the long tail is empty. Generalisation is
     impossible across cells the model has never seen, and within
     dense cells the cell mean is already optimal.

### Implication for Day 5

Greedy navigation built on this learner reduces to: "for each
(region, operator) pair, look up the cell mean and pick the
operator that minimises predicted ‖k‖." That's a valid Day-5 step,
but the "learner" piece is doing no work — a pure cell-mean lookup
table would behave identically.

To find a *learnable* gradient field beyond table lookup we need:

  * **More operator diversity per region** : the long-tail empty
    cells are where generalisation could be tested.
  * **Per-record kill_vector persistence going forward** : Day-3's
    KillVector is the substrate for this. Once
    `discovery_pipeline.process_candidate` emits one per
    candidate, **every** F-check fires against every candidate,
    not just the first-failing — so triggered=False becomes a
    measured outcome, not a conditional.
  * **Margin recovery on fresh runs** : the margin layer of the
    learner is fully wired but empty on the legacy 315k. Once
    pipelines emit margins for F1 (p-value), F6 (distinct count),
    F9 (M − 1.001), and the catalog distance, the margin
    sub-models will see real signal.

## Honest framing

This is a small learner on noisy categorical data. A positive
result would be a **substrate signal** (the ledger has learnable
(region, operator) → kill structure), not mathematical capability.
The Lehmer brute-force PROMOTE rate remains 0; every kill in this
dataset is a near-miss in the kill-space geometry, not a
ground-truth target.

The negative-but-not-broken verdict here is the most useful
outcome: it falsifies the optimistic reading of Day 1-3 ("the
substrate has a learnable gradient field") and pinpoints the
intervention ("we need per-candidate kill_vector persistence to
make the gradient field denser than a table"). Day 5 ships a
greedy navigator that runs on the cell-mean baseline directly —
no learner — with a clear note that this is the lookup-table
fallback, not a learnt gradient. When the new pipeline accumulates
per-record kill_vectors over the next few weeks, we re-run this
learner and re-test the verdict.

## Reproducing

```bash
cd F:/Prometheus
python -c "from prometheus_math.kill_vector_learner import run_learner, write_report; \
  res = run_learner(); \
  write_report(res, json_path='prometheus_math/_kill_vector_learner_results.json', \
                    md_path='prometheus_math/KILL_VECTOR_LEARNER_RESULTS.md')"
```

Tests: `python -m pytest prometheus_math/tests/test_kill_vector_learner.py`
(17 tests; covers authority/property/edge/composition rubric).

## Files

  * `prometheus_math/kill_vector_learner.py` — the learner module
    (~750 LOC).
  * `prometheus_math/tests/test_kill_vector_learner.py` — 17 tests
    across the four math-tdd categories.
  * `prometheus_math/_kill_vector_learner_results.json` — full
    structured results (per-component metrics, per-region
    breakdown, operator chart recovery, baselines, verdict).
  * `prometheus_math/KILL_VECTOR_LEARNER_RESULTS.md` — this file.
