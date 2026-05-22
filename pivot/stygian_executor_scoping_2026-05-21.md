# Stygian Executor — Scoping Doc

**Date:** 2026-05-21
**Author:** Charon (session adopting role at 2026-05-20T20:28 EST)
**Status:** Scoping only. NOT shipped. Authored to unblock the next Charon session (or peer agent) who picks up the v10 battery executor integration.

---

## Why

Tonight's commits (`27b85bfd` cascade swap + `cd8bd187` Hecate→Stygian closed-loop) shipped two substrate-grade edges into the Charon swarm. But the swarm's verification valve is still closed:

- **Stygian writes attack PLANS** — markdown artifacts at `charon/agents/stygian/artifacts/attack_plan_*.md` describing what the v10 battery should do.
- **Nothing executes the battery.** The kill_ledger only grows from Theseus's generators.
- Therefore: the Hecate→Stygian queue carries demand but no current. Hecate analyzes Theseus's kill_patterns → Stygian wraps them as attack targets → no kill_ledger row emitted → Hecate re-analyzes the same Theseus data next tick. The "closed loop" is a closed pipe.

Per CHARTER §10 ("the substrate is the product; findings are byproducts"), an unverified plan is not substrate. Until Stygian emits actual kill_ledger rows from its own attacks, the v10 battery's frozen calibration is unused by the swarm and the closed-loop story has no causal arrow.

This doc scopes the integration. It is the work the next Charon session should ship.

---

## What the v10 battery actually wants

From `cartography/shared/scripts/battery_unified.py`:

The `UnifiedBattery` class exposes three callable modes:

1. **`test_distribution(finding_id, claim, values, predicted_value=None, domain_is_multiplicative=False, synthetic_generator=None, group_labels=None, confound_values=None, X_for_regression=None, Y_for_regression=None, notes="")`** — runs F15-F23 + F24 on a numeric distribution. Wants:
   - `values`: 1D numeric array (the distribution under test)
   - `predicted_value`: optional theoretical anchor (for F16 equivalence test)
   - Various conditional inputs depending on which sub-tests should fire

2. **`test_correlation(finding_id, claim, values_a, values_b, confounds=None, dose_levels=None, dose_labels=None, subgroups=None, n_hypotheses_tested=3, index_values=None, notes="")`** — runs F1-F14 (via `falsification_battery.py`) plus F21/F23. Wants two paired numeric arrays.

3. **`test_full(...)`** — runs both modes.

Each returns `{"tests": {...}, "overall": {"verdict": ..., "tier": ...}, "n_samples": N}` and logs to `BatteryLogger` (JSONL).

**The battery's API is clean.** Strings in, structured verdicts out. The integration challenge is not "how do I call this" — it's "where do the `values` arrays come from for each Stygian SEED_PROBLEM."

---

## The gap: attack_plan → battery inputs

Stygian's `SEED_PROBLEMS` (in `charon/agents/stygian/daemon.py`) are 10 high-level conjectures:

- `BL-C-001`: Lehmer's conjecture — wants Mahler measure values near M≈1.1762 on a polynomial family
- `BL-C-002`: BSD rank distribution at high conductor — wants rank-vs-conductor pairs
- `BL-C-003`: Mahler measure spectrum gaps — wants Mahler measures below threshold T
- `BL-C-004`: Schinzel-Zassenhaus follow-on — wants house values vs Dimitrov bound
- `BL-C-005`: abc conjecture — wants rad/q/log triples from real abc data
- `BL-C-006`: Beal's conjecture — wants small-exponent perfect-power candidates
- `BL-C-007`: Catalan-Mihailescu adjacent — wants perfect-power gap data
- `BL-C-008`: Vinogradov mean value — wants exact-constant test data
- `BL-C-009`: Goldbach exceptional set — wants theta-bound test data
- `BL-C-010`: Twin prime gaps — wants exact-H state data

Plus, post-Stand-#1, an open-ended stream of **HECATE-`<kill_pattern>`** problems whose "data" is a kill_pattern cluster from Theseus's ledger, not a mathematical object.

Each SEED_PROBLEM needs **a data loader** that produces battery-shaped arrays. Most of this data **already exists somewhere in the repo** — the historical kill_ledger (per README: 314K kills, 16 documented kills in EC zeros + RMT sign inversion) was produced by exactly these batteries running on exactly these problems. The question is whether the loaders were saved as reusable functions or were one-shot scripts.

---

## MVP scope (single problem, proof of life)

**Pick ONE SEED_PROBLEM and ship Stygian executing the battery against it end-to-end.** BL-C-001 (Lehmer) is the natural choice:

- Most canonical Prometheus problem
- Mahler measure data is well-instrumented (per discovery_pipeline_validated memory: "BSD rank cross-domain validates substrate at +1.37× p=0.00055")
- F15-F23 distribution mode applies cleanly — Mahler measures are multiplicative, have known theoretical anchors
- A bad executor on a known-test-case is recoverable; a bad executor on an open conjecture is mysterious

**Minimal flow:**

1. Stygian's `run_tick` picks BL-C-001 (or Hecate-fed equivalent).
2. Stygian writes `attack_plan` (already does this).
3. **NEW:** Stygian invokes `_execute_attack(problem)` → dispatcher.
4. Dispatcher looks up `BL-C-001` in a per-problem loader registry.
5. Loader produces `{values: <mahler_measures>, predicted_value: <smyth_lower_bound>, domain_is_multiplicative: True, ...}`.
6. Dispatcher calls `UnifiedBattery().test_distribution(**loader_output)`.
7. Battery returns verdict.
8. **NEW:** Stygian wraps verdict in a KillVector v2 record (per `agora.kill_ledger_entries` schema in `charon/agents/DESIGN_2026-05-19.md` §"Postgres pub/sub schema").
9. Writes the kill_ledger row — for MVP, to a local `charon/agents/stygian/state/kill_ledger.jsonl` (same shape as Theseus emits). Upgrade to `agora.kill_ledger_entries` Postgres table in v0.4.
10. Hecate's next tick sees the new row and includes it in its MI computation.

**Closed-loop edge actually carries current.**

Estimated LOC: ~150 dispatcher + ~80 loader for BL-C-001 + ~60 KillVector wrapper = ~290 LOC.

---

## Sub-MVPs (per-problem expansion)

After MVP1 (BL-C-001 working end-to-end), each subsequent SEED_PROBLEM needs its own loader. Estimated ~80-150 LOC per loader, depending on data source complexity:

- **BL-C-002 (BSD)**: Mnemosyne owns the EC data layer; loader queries her DuckDB or Postgres for rank/conductor pairs above 10^7 conductor. Distribution mode + `group_labels` for rank-0/rank-1 split.
- **BL-C-003 (Mahler spectrum gaps)**: Same data source as BL-C-001 but `test_distribution` with `synthetic_generator` for F19 generative replay.
- **BL-C-004 (Schinzel-Zassenhaus)**: `test_distribution` on house values vs Dimitrov's 1/(4*deg) bound.
- **BL-C-005..010**: each needs its own data source survey.

Suggested sub-MVP cadence: ship MVP1, watch the kill_ledger grow for a day, then add BL-C-002. Per-problem loader is the right unit of work.

---

## HECATE-* meta-test (DEFERRED to v0.4+)

Per Stand #1, the Hecate→Stygian queue surfaces `HECATE-<kill_pattern>` synthetic problems. These don't map cleanly onto the battery's (values, predicted_value) shape — a kill_pattern cluster is a *set of past kills sharing a pattern label*, not a numeric distribution.

Two candidate meta-test framings:

1. **Re-run F1-F14 on a held-out subset of the cluster's records.** Treat each kill_ledger entry as a (values_a, values_b) pair (the original test that produced the kill). Run battery; does the new subset reproduce the kill pattern?
2. **Permutation test on the cluster's signature.** Shuffle generator_id ↔ kill_pattern labels across the ledger; does the observed cluster size still appear? If yes → cluster is structural noise, not signal. If no → cluster is real.

#2 is cheaper and more honest given the measurement-circularity caveat (Hecate is partially measuring Theseus generator-design labels). Recommended for HECATE-* executor when it ships.

DEFER until single-problem MVP is solid. HECATE-* without a sensible meta-test would produce noise faster than substrate.

---

## Hard stops (respected, not negotiated)

Per `charon/RESPONSIBILITIES.md` standing pointer and `charon/BACKLOG.md`:

- **v10 battery FROZEN at 25 tests / 4 tiers.** The executor MUST NOT modify any battery source under `cartography/shared/scripts/`. Read-only consumer.
- **No v11 escalation.** If the executor surfaces a gap that calls for a new test, file a P2 ticket to Aporia. Do NOT add tests inline.
- **No `--writeable` upgrade.** The kernel contract holds.
- **No multiprocessing scaling.** Single-process executor; one attack per tick.
- **No LoRA work.** Out of scope.

The executor is a *thin* layer between Stygian's attack_plan and the existing frozen battery. If the integration starts looking like ~500 LOC of "let me also restructure the battery for usability," stop and back out.

---

## Telemetry + observability

The executor MUST emit:

1. **Per-tick stats additions** to Stygian's existing tick output:
   - `executor_invoked: bool`
   - `battery_mode: "distribution" | "correlation" | "full" | None`
   - `battery_verdict: "SURVIVED" | "KILLED" | "INCONCLUSIVE" | "SKIPPED" | "ERROR"`
   - `battery_elapsed_sec: float`
   - `kill_ledger_row_written: str | None` (id of the new row)
   - `executor_skip_reason: str | None` (e.g., "no_loader_for_problem")

2. **A kill_ledger row** (JSONL, shape per Theseus's existing emissions to maintain Hecate compatibility):
   - `kill_id` (content-addressed hash)
   - `claim_id` (from attack_plan)
   - `problem_id` (BL-C-* or HECATE-*)
   - `generator_id` (always "stygian" for executor emissions)
   - `kill_pattern` (e.g., "f3_effect_size_below_threshold" — derived from battery's specific failing test)
   - `verdict` (SURVIVED | KILLED | INCONCLUSIVE)
   - `tier` (battery's tier classification)
   - `battery_finding_id` (the finding_id passed to UnifiedBattery)
   - `attack_plan_path` (provenance back to artifact)
   - `hecate_queue_row_id` (if Hecate-fed; null otherwise)
   - `emitted_at`, `emitted_by` (always "stygian")
   - Full battery `tests` dict as nested JSON

3. **A `log_work` event** with `stage="stygian_battery_executed"` so Metis dashboards surface the activity.

---

## Risks / open questions

1. **Data loader maintenance burden.** 10 SEED_PROBLEMS × 80-150 LOC each = ~1000-1500 LOC just for loaders. Most of this is one-time work referencing existing data sources, but it's not negligible. Mitigation: ship MVP1 first, defer loaders 2-10 until MVP1 has proven the harness; let pain pick the second loader (which problem do we wish were attacked next?).

2. **Loader code quality drift.** Loaders are per-problem; easy to write them inconsistently. Mitigation: define a single `BatteryLoaderProtocol` (TypedDict) and a smoke-test fixture; every loader must pass the fixture before being registered.

3. **Battery runtime per attack.** F1-F14 with 10K permutations + F15-F23 distribution tests + F21-F23 correlation tests could take 30s-2min per attack on real data. Stygian's tick budget is currently ~5s (per rotation log). Need a per-tick timeout + ability to spread one attack across multiple ticks (state: "executing", "complete"). MVP can run sync at first, add async state machine in MVP2.

4. **kill_ledger row schema compatibility with Theseus.** Hecate consumes Theseus's JSONL shape. The executor's rows must use the same shape OR Hecate must learn to consume both. Mitigation: read Theseus's emit code, mirror exactly. Don't fork the schema for MVP.

5. **What does "KILLED" mean for an attack on a problem with no concrete claim?** BL-C-001 is "test Lehmer's conjecture" — but the battery tests *specific claims*, not conjectures wholesale. The loader must translate "attack Lehmer" into a specific testable claim like "Mahler measure series is bounded below by Smyth's bound." Each loader is, in part, a claim-formulator. Document the chosen claim in the loader's docstring; the attack_plan should already cite it.

6. **HECATE-* claim formulation is harder than BL-C-* claim formulation.** See "DEFERRED" section above. For MVP, the executor short-circuits HECATE-* problems with `executor_skip_reason="hecate_meta_test_not_yet_implemented"` and just writes the attack_plan. Falls back to current behavior; nothing breaks.

7. **Will the v10 battery actually produce a KILLED verdict on any of these?** Per README: "16 kills in 4-day sprint on EC zeros/spectral tail" — yes, the battery does kill. But it killed those specific claims; whether it kills the BL-C-* claims as currently formulated is empirical. MVP might produce 10 SURVIVED verdicts in a row, which is fine (also data). Per `feedback_residual_signal`: SURVIVED is not 100%; the per-test sub-verdicts and residuals are the substrate.

---

## Recommended next session's work

For the Charon agent picking this up (or me, next session):

1. **Read `cartography/shared/scripts/battery_unified.py:80-260` end-to-end.** The contract is clean; the LOC is small.
2. **Read `cartography/shared/scripts/falsification_battery.py:1-200` for F1-F14 specifics.** Understand what the correlation tests actually do.
3. **Locate the historical BL-C-001 (Lehmer) data source.** Likely under `charon/data/charon.duckdb` or `prometheus_math/databases/`. Grep for "mahler_measure" / "lehmer" near the existing test scripts.
4. **Build `charon/agents/stygian/loaders/lehmer.py`** as the single MVP loader. Returns a TypedDict matching `BatteryLoaderProtocol`.
5. **Build `charon/agents/stygian/executor.py`** with the dispatcher + KillVector wrapper. Wires into `Stygian.run_tick`.
6. **Smoke-test:** `python scripts/charon_loop.py --agent stygian` — should produce one attack_plan + one kill_ledger row.
7. **Watch Hecate's next tick:** does it see the new row? Does it update the MI signal?
8. **Commit** as "Charon swarm v0.4: v10 battery executor (Lehmer MVP)."

Estimated session length: 4-6 hours for MVP1 if data loader is straightforward; 8-10 hours if the loader needs significant data engineering.

---

## Closing posture

The Hecate→Stygian closed-loop edge I shipped tonight is, today, demand without supply. That's the substrate-passive-consumer failure mode (per `feedback_substrate_passive_consumer_warning`). Shipping the executor opens the supply side. Until then, the swarm is producing beautiful provenance documentation for attacks that never run.

Don't add more swarm agents, more queues, more producers until this gap is closed. **The executor is the load-bearing next ship.**

— Charon, 2026-05-21
