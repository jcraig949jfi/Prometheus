# Ergon Learner — Components Inventory

**Date:** 2026-05-03
**Source:** `ergon/learner/` directory after MVP scaffolding (commit 8010593f)

File-by-file map of the MVP code structure as it stands at design freeze. Each component is described by its responsibility, its acceptance test (where applicable), and its v8 reference.

## Top-level

### `README.md`
Entry point for any agent/human picking up the MVP cold. Names the canonical design docs (v7 final, v8 delta, v5 architectural canonical, v6 operational refinements) and the MVP structure. Should be read first.

### `MVP_PLAN.md`
Day-by-day execution plan for Days 1–30. Trials 1, 1.5, 2, 3 with acceptance criteria and failure paths. Logging targets and real-time alerts active from Day 1. Non-MVP scope (deferred to v0.5+) explicitly enumerated. **Bundle doc 03 is a copy of this.**

## Core modules

### `genome.py`
Genome dataclass. Represents a typed DAG over arsenal atoms (the 85-op metadata table from `prometheus_math.arsenal_meta`). Deterministic content hashing via sha256 over canonical DAG serialization. Type-checking against `arg_type` signatures.

**MVP day:** Day 8 (Trial 2). Acceptance: type discipline preserved across all mutation operators.

### `archive.py`
MAP-Elites archive. pyribs-based with pointer-storage discipline (heavy data in Postgres; pyribs holds pointers + descriptor coordinates only). 5-axis behavior descriptor → 5,000 cells.

**MVP day:** Day 11. Acceptance: archive supports add/replace/query at 1K-episode scale without IOPS contention.

### `descriptor.py`
Behavior descriptor: 5-axis projection from genome to archive cell. Hot-swappable per v5 §6.2 — per-axis fill-rate audit every 1K episodes; if any axis exceeds 70% concentration, swap with pre-specified replacement candidate from `descriptor_config.toml`.

**Axes:**
1. Canonicalizer subclass (group_quotient / partition_refinement / ideal_reduction / variety_fingerprint)
2. DAG entropy (structural complexity)
3. Output-type signature (terminal type)
4. Bounded magnitude bucket (5 bins)
5. Canonical-form distance (output vs canonical-form output)

**MVP day:** Day 11 alongside archive. Acceptance: tertiary acceptance from Trial 2 (no axis >70% concentration in single bin).

### `scheduler.py`
Operator-class scheduler. Cell-selection policy with coverage-pressure reweighting. Minimum-share enforcement: uniform ≥5%, anti_prior ≥5%, structured_null ≥5%; total non-prior ≥15%. The scheduler is the substrate's defense against operator-class collapse (e.g., structural mutation dominating because it's most rewarded).

**MVP day:** Day 14. Acceptance: minimum shares enforced over 1K-episode windows.

### `reward.py`
Agreement-weighted reward function. v8 form:
```
r = w_S * substrate_verdict     # PROMOTE/WARN/BLOCK from kernel
  + w_C * cross_model_agreement # 5-evaluator vote (v0.5+)
  + w_H * holdout_battery       # held-out subset of F1+F6+F9+F11 (v0.5+)
  + w_N * non_llm_evaluator     # numeric perturbation for Lehmer-Mahler (v0.5+)
  + w_R * residual_signal       # signal-class confidence from residual classifier
```

At MVP scope, only `substrate_verdict` and `residual_signal` are active. w_R activation is tier-conditioned on Trial 1 outcomes.

### `triviality.py`
F_TRIVIAL_BAND_REJECT signature library. 4 static + 2 temporal:

**Static signatures:**
1. Small-number coincidence (output happens to be a small integer; not structural)
2. Prime-density artifact (output reflects local prime density, not the claimed structure)
3. Scale rescaling (output is a scaled version of a known structure)
4. Cyclotomic root-of-unity coincidence (output near a cyclotomic but not actually one)

**Temporal signatures:**
5. Recurrence density (Jaccard ≥0.9 to ≥3 prior in same lineage / 1K window)
6. Novelty decay (avg distance decrease ≥30% / 1K window)

**MVP day:** Day 13. Acceptance: trigger rate within [5%, 30%] (real-time alert flags rates outside this band).

### `stability.py`
Magnitude perturbation-stability check. For magnitude buckets 4 and 5 ([10⁹, 10¹²) and [10¹², ∞)):

- Input jitter test: ε=0.001 across 100 trials, ≥95% same bucket
- Half-precision recompute test: same bucket

Failures route to `out_of_band` cell; trigger F_MAGNITUDE_STABILITY_REJECT kill-test.

**MVP day:** Day 12.

## Operators (`operators/`)

### `structural.py`
DAG topology mutation. Add/remove/swap nodes in the typed DAG, preserving type compatibility. Lineage-tagged.

### `symbolic.py`
Argument-value mutation. Change argument values within type bounds; structurally identical DAG, different leaf values. Lineage-tagged.

### `anti_prior.py`
Anti-correlated with corpus frequency stats. Builds `corpus_frequency_stats` database from Mathlib + Proof-Pile-2 frequency analysis (~5GB). Implements:
- KL divergence ≥1.0 nat per claim check
- Descriptor-displacement check (cell not occupied by `neural` operator outputs in any prior 10K window — at MVP, relax to "cell not occupied by any prior-shaped operator")

Failure flag: `anti_prior_failed_divergence`.

**MVP day:** Day 10. Critical for the bottled-serendipity thesis test — anti_prior is the operator that explores off-distribution territory.

### `uniform.py`
Strawman null. Uniform random sampling from typed action space; no selection pressure. Used as the comparison baseline in Trial 3.

### `structured_null.py`
Type-respecting null. Like uniform but respects the 5-axis descriptor — random but constrained to fall in some valid cell. Tighter null than uniform; tests whether the descriptor itself encodes useful structure.

## Trials (`trials/`)

### `trial_1_residual_benchmark.py`
Adversarial residual benchmark on 200 curated samples. Days 1–4. Outputs `trial_1_results.json` + `TRIAL_1_REPORT.md`.

### `trial_1_5_optimization_probe.py`
Adversarial optimization probe — closed-loop hill-climbing against frozen classifier. Days 5–7. Outputs `trial_1_5_results.json` + `TRIAL_1_5_REPORT.md`. **Gates Trial 2.**

### `trial_2_evolutionary_engine.py`
Bounded buckets + trivial detector + minimum-share enforcement at 1K episodes. Days 8–17 (interaction-effect debugging is the time sink). Outputs `trial_2_results.json` + `TRIAL_2_REPORT.md`.

### `trial_3_five_counts_diagnostic.py`
Multi-arm pilot at 9K episodes (3K × 3 arms). Days 18–22. Outputs `trial_3_results.json` + `TRIAL_3_REPORT.md`.

## Tests (`tests/`)

pytest suite per module:

- `test_genome.py` — type discipline, content hashing, DAG serialization round-trip
- `test_archive.py` — add/query/replace, pointer discipline, descriptor coordinate validity
- `test_descriptor.py` — per-axis bin edge cases, hot-swap protocol mechanics
- `test_scheduler.py` — minimum-share enforcement under skewed operator usage
- `test_reward.py` — weight tier conditioning per Trial 1 outcome bins
- `test_triviality.py` — each of the 6 signatures triggers on its target case and not on negatives
- `test_stability.py` — perturbation jitter + half-precision recompute correctness

## Open simulation requests

Per `pivot/simulation_request_round4_reviewer.md` and `pivot/simulation_request_round6b_reviewer.md` — two external-reviewer simulation offers were accepted for parallel-with-MVP execution. They provide a-priori expected-distribution baseline against which actual MVP results compare.

## Where to find more

- Canonical README: `ergon/learner/README.md`
- Canonical MVP plan: `ergon/learner/MVP_PLAN.md`
- v8 spec: `pivot/ergon_learner_proposal_v8.md`
