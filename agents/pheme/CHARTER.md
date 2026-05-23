# Pheme — Substrate Demand Voicer

> *Pheme (φήμη): Greek personification of report and rumor, the voice that carries news between realms. Hesiod said she had her own altar at Athens because no warning that needed to be heard could afford to be silent.*

**Machine:** any (CPU-only, reads Ergon eval output)
**Operator:** Ergon
**Owns:** the demand signal — observed Learner training deficits → typed-DR-quota bias for upstream producers (Hypatia, Atalanta, Aporia, Lethe, Sophia)
**Lives at:** `agents/pheme/`
**Source of truth (code):** `agents/pheme/daemon.py`

---

## Why Pheme exists

The Learner gets trained on whatever substrate happens to land in `ergon/learner/corpus/`. Currently nothing tells the upstream producers what the *Learner is actually bad at*. Hypatia picks problems by round-robin. Atalanta picks primitives by recency. Aporia picks DR queries by judgment. None of them see Learner eval metrics.

Pheme reads the Learner's recent eval runs, identifies the worst-performing reasoning patterns (e.g., "R4 chains involving group-theoretic inference fail 65% of the time"), aggregates the signal into a **substrate-demand profile**, and publishes it where producers will read it. Hypatia's selector reads `agents/pheme/artifacts/demand_latest.json` and biases problem selection toward matching patterns. Atalanta does the same. Aporia incorporates the profile into the thesis-driven generator.

Pheme closes the demand–supply loop. Without her, the substrate pipeline is open-loop with respect to what the Learner needs.

---

## Per-tick contract

Default tick interval: **1800s (30 min)**.

Every tick:
1. Acquire single-instance lock (`agents/pheme/pheme.pid`); abort if another instance is live.
2. Register heartbeat (`session_telemetry.register_session`, `kind="tool"`, `operator="Ergon"` — note: Pheme is Ergon-operated, not Aporia-operated).
3. Read state from `agents/pheme/state/state.json`: last-scanned eval run, last-profile timestamp, anti-silence counter.
4. Scan the Ergon eval output roots (configurable). Identify eval runs completed since `last_scanned_eval_id`.
5. For each new eval run, parse the per-example results: extract failures, group by reasoning-pattern axes (`ladder_level`, `pattern_kind` from worked-solutions if available, problem subfield, paradigm tag).
6. Aggregate across new runs into a demand profile:
   - Per-pattern failure rate
   - Top-K worst-performing pattern combinations
   - Sample count + confidence interval per pattern
   - Trend vs prior profile (improving / stable / regressing)
7. Write `agents/pheme/artifacts/demand_<UTC-date>_<HHMMSS>.json` AND atomically replace `agents/pheme/artifacts/demand_latest.json` (the consumer-facing symlink-equivalent).
8. Fire `log_work(stage='ergon_substrate_demand', summary=..., output_path=...)` so Aletheia's dashboard + Hermes brief surface the signal.
9. If no new eval runs since last scan → emit `NULL_TICK` sentinel + `log_work(stage='pheme_null_tick', ...)`.
10. If Ergon eval root not found → emit `UPSTREAM_NOT_FOUND` sentinel (config wiring needed).
11. Persist state and release lock.

---

## Backlog source

Ergon's eval output directory. Pheme tries (in order): `ergon/learner/evals/`, `ergon/evals/`, `ergon/diagnostic_c/eval_runs/`. First existing root wins. Per-run files expected to be JSON or JSONL with per-example records carrying at least: `example_id`, `prediction`, `correct`, optionally `ladder_level`, `pattern_kind`, `paradigm`, `subfield`.

`self_generate_backlog()` returns the current top-K demand candidates — for orchestration visibility; not consumed by the tick.

If the eval root is missing or no eval has fired in 7+ days, Pheme emits `EVAL_DROUGHT` sentinel — visible warning that the demand signal is going stale, which means the producers are flying blind.

---

## Downstream consumers

- **Hypatia** reads `agents/pheme/artifacts/demand_latest.json` for `target_reasoning_patterns` and biases catalog selection.
- **Atalanta** reads the same file to bias primitive-candidate selection (high-failure patterns get priority for E-track DR).
- **Aporia** (the human or the session) reads the same file when authoring DR queues to bias the mix toward demand.

The demand profile shape is the contract:

```json
{
  "computed_at": "2026-05-23T14:00:00Z",
  "last_eval_run_id": "eval_2026-05-23_002",
  "eval_runs_aggregated": 3,
  "total_examples": 1200,
  "target_reasoning_patterns": [
    {"pattern_kind": "R4_group_theoretic", "failure_rate": 0.65, "n": 80,
     "trend": "stable", "priority": "P0"},
    {"pattern_kind": "R5_novel_framework", "failure_rate": 0.78, "n": 12,
     "trend": "regressing", "priority": "P0"},
    ...
  ],
  "low_priority_patterns": [
    {"pattern_kind": "R1_direct_lookup", "failure_rate": 0.03, "n": 240,
     "trend": "stable", "priority": "P3"}
  ],
  "substrate_type_bias": {
    "A": 0.30, "B": 0.10, "C": 0.10, "D": 0.40, "E": 0.10
  }
}
```

The `substrate_type_bias` is a quota override. The Aporia-set default is `A 0.35 / D 0.25 / B 0.15 / C 0.15 / E 0.10`. Pheme adjusts based on observed deficits: a Learner failing R4 chains needs more D substrate, so D goes up.

---

## Structured logging

Same three-stream pattern as Hypatia and Atalanta:

- **Text log** at `agents/pheme/logs/pheme.log`
- **Events JSONL** at `agents/pheme/events.jsonl`
- **State file** at `agents/pheme/state/state.json` — `{last_scanned_eval_id, last_profile_at, anti_silence_counter, total_profiles_lifetime, total_null_ticks_lifetime, prior_top_patterns: [...]}`
- **Heartbeat** via `session_telemetry.register_session` with `operator="Ergon"` and a status_json that includes the current top-K demand patterns (so anyone reading the heartbeat sees the live signal)
- **Work events** via `session_telemetry.log_work`: `ergon_substrate_demand`, `pheme_null_tick`, `pheme_upstream_not_found`, `pheme_eval_drought`, `pheme_self_audit_null`, `pheme_startup`, `pheme_shutdown`
- **Per-profile artifact** in `agents/pheme/artifacts/demand_<timestamp>.json` + atomic update of `demand_latest.json`
- **Per-null-tick artifact** in `agents/pheme/artifacts/null_<timestamp>.json`

---

## Operational

**Single-instance lock:** `agents/pheme/pheme.pid`.

**Detached launch:** `scripts/pheme_loop_launch.bat` invoked via `Start-Process -WindowStyle Hidden`.

**CLI:**
- `python -m agents.pheme.daemon --once`
- `python -m agents.pheme.daemon --loop --interval 1800`
- `python -m agents.pheme.daemon status`

**Hard stops:**
- Never write to `ergon/learner/corpus/` directly (corpus mutation is Ergon's call).
- Never override the producer's selection — only publish the demand signal.
- Never read raw `*Key*` files.

**Anti-gravitational-well vigilance:** the conventional move is to publish smoothed long-horizon trends. Pheme must instead surface the *current* signal honestly — a 30%-failing pattern that just spiked is more actionable than a 10%-failing pattern that's been there for months. Recency-weighting matters. A demand profile that just describes the long-term marginals is the failure mode — re-orient toward what changed since last profile.

— Aporia, 2026-05-23
