# Reasoning-Quality Emit primitive — implementation note

**Module:** `prometheus_math/reasoning_quality_emit.py`
**Tests:** `prometheus_math/tests/test_reasoning_quality_emit.py` (16 tests, all green)
**Forged:** 2026-06-09 (Techne)
**Implements:** `aporia/docs/reasoning_quality_emit_spec_v0.1.md` (Aporia, 2026-06-08)
**Parents (doctrine):** `feedback_no_naive_score_combination` (the failure this fixes),
`feedback_anticorrelation_is_not_noncyclicity` (the contested-sampling rationale),
`feedback_substrate_passive_consumer_warning` (every doc → a behavior delta).

---

## What it is

The canonical emitter for the **per-evaluator score vector**. Root cause it fixes
(spec §0): the substrate computes per-head reasoning scores, **combines them into one
scalar/verdict, and persists only the combined value** — discarding the vector that the
*validated* relational H-R1 instrument and the curl diagnostic are the only consumers of.
Five times in the 2026-06 reasoning-steering arc a finding-in-memory had no on-disk
multi-evaluator data behind it for exactly this reason.

The one-sentence change (spec §1): **wherever ≥2 heads / judges / scorers evaluate the
same reasoning candidate, persist the per-evaluator score VECTOR — before any combination —
alongside whatever combined value is produced.** The combine step stays; we stop throwing
the vector away. It is no-inference to SPECIFY and to LOG — the heads already run.

## API (the contract)

- `candidate_id_for(text) -> sha1` — stable content-address for a reasoning state.
- `make_record(candidate_id, task_id, evaluator_scores, *, combined, outcome, contested,
  scorer_versions, born_at) -> EvalRecord` — validated builder. `evaluator_scores` IS the
  vector (spec §2). `born_at` is **injected, not auto-stamped**, so records are
  reproducible and tests deterministic; production callers pass an ISO-8601 string.
- `EvalRecord.to_json_line()` / `EvalRecord.from_json()` — append-only JSONL round-trip.
- `append_records(path, records)` / `load_records(path)` — append-only writer/loader.
- `is_task_contested(candidates)` / `top_candidate_per_evaluator(candidates)` /
  `mark_contested(records)` — the contested-sampling lever (spec §4): curl concentrates on
  candidates where evaluators split; a task is contested iff its evaluators disagree on the
  top candidate. Ties break on sorted candidate_id (deterministic, order-independent).
- `to_relational_records(records, *, contested_only=False)` — **the load-bearing adapter**:
  surfaces the vector as `record["margins"]`, the exact key the UNCHANGED validated
  `stage0b.runner.run_h_r1` reads. `contested_only` keeps only contested-task candidates
  (importance-sampling toward disagreement).

## Why these design choices (the stands taken)

- **`born_at` injected, not `datetime.now()` inside.** Keeps the emitter a pure function:
  same inputs → same record. Hidden wall-clock would make the corpus non-reproducible and
  the tests flaky. Production callers stamp; the primitive does not.
- **≥2-evaluator validation raises, it does not warn.** A lone score is not a vector
  (spec §1); silently accepting it would reproduce the discard-the-vector failure one layer
  up. The family-holdout null also needs ≥2 stable evaluator names to mean anything.
- **Non-string / empty evaluator ids raise.** The emitter-family-holdout null and the
  per-evaluator screen key on STABLE names (spec §2); integer/None keys silently break them.
- **`contested` is a task-level property of the candidate set**, computed by
  `mark_contested` over records grouped by `task_id` — not a per-record guess. This matches
  the curl object: non-transitivity only exists across a *set* of compared candidates.
- **Adapter emits to the existing `margins` key rather than a new schema.** The runner is
  validated (47+50 tests, Efron-dice positive control 0.99 curl). The cheapest correct move
  is to feed it its native format, not to touch it. Interface-is-contract.

## Verification

- `test_pipeline_feeds_validated_runner` is the decisive composition test: 10 emitted
  candidates → `append_records` → `load_records` → `to_relational_records` →
  `stage0b.runner.run_h_r1` returns a structured verdict in `{BEATS_NULL, NULL}` (NOT
  INVALID, `n_states == 10`). The vector survives to disk and the instrument reads it.
  We do **not** assert BEATS_NULL/NULL — that is the empirical reasoning question this
  unblocks, not a property of the plumbing.
- Authority = the spec §2 schema + the runner's `margins` contract (no math table applies
  to a logging primitive; these two contracts are the authority).
- 16/16 emit tests green on Python311; the dependency instrument (`stage0b/tests/`) green.
- Purely additive: two new files, **zero edits to existing code** → no regression surface.

## What it unblocks (the behavior delta)

This is the precondition for H-R1 arms A (independent judges) and D (the actual heads) on
**real** reasoning data — the only place the non-conservativity thesis can still live after
two math-object NULLs (Mahler, genus-2 are scalar-reducible). The next move is a
**one-line integration**: at any site that already scores a candidate with ≥2 heads
(the Walk-Z/PRM reward path is the named one — spec §3), call `make_record(...)` +
`append_records(...)` just before the existing combine step. Then run
`prescreen.signal_screen` → on PASS, `run_h_r1` on the emitted vectors. The verdict changes
how the substrate rewards reasoning: NULL → a single best-aligned head suffices; BEATS_NULL
→ scalar/linear reward combination is provably lossy and a vector-valued reward is required
(path-B `reward_curl_demo`, now on real data).

— Techne, 2026-06-09
