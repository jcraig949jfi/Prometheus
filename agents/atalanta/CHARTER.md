# Atalanta — E-track Primitive Hunter

> *Atalanta of Arcadia: huntress, first to wound the Calydonian Boar, faster than every suitor. The job is to react quickly to fresh game — primitive candidates emerging from Apollo's evolving organisms — before the trail goes cold.*

**Machine:** any (CPU-only)
**Operator:** Aporia
**Owns:** substrate type **E** (meta-reasoning circuit candidates — primitive proposals derived from Apollo organisms)
**Lives at:** `agents/atalanta/`
**Source of truth (code):** `agents/atalanta/daemon.py`

---

## Why Atalanta exists

Apollo evolves primitive routing DAGs (substrate E). The catch: Apollo's primitive pool is fixed at start of each run. When organisms repeatedly reach for primitives that don't exist (or use the same composite chain over and over), the pool itself is the bottleneck — but nobody is reading Apollo's runs to find that signal.

Atalanta's job is to read recent Apollo organism logs, identify primitives with **high reuse** (frequently appearing in successful organisms) or **high demand** (composite chains that look like an unnamed primitive), and fire Type-E DR queries that surface candidate primitives Techne should register.

Once Techne registers them, Apollo's next run has a richer pool. The feedback loop closes.

Atalanta is the E-track owner. She does not produce A / B / C / D. Direct substrate-E production stays with Apollo (organisms); Atalanta feeds Apollo's *input* (primitives) via DR-surfaced candidates.

---

## Per-tick contract

Default tick interval: **1800s (30 min)**. Reacts to new Apollo runs as they land.

Every tick:
1. Acquire single-instance lock (`agents/atalanta/atalanta.pid`); abort if another instance is live.
2. Register heartbeat (`session_telemetry.register_session`, `kind="tool"`, `operator="Aporia"`).
3. Read state from `agents/atalanta/state/state.json`: last-scanned Apollo run id, last-fired primitive candidate, anti-silence counter.
4. Scan the Apollo runs directory (configurable; default `apollo/runs/` if it exists, else `apollo/runs_v2/`). Identify runs completed since `last_scanned_run_id`.
5. For each new run, parse the organism log: count primitive usage frequencies, detect repeated composite chains (length-2 and length-3) that don't have a registered primitive name.
6. Aggregate across runs to find:
   - **High-reuse primitives:** appear in ≥ N organisms but have low Techne registry depth (signal: nearby variants would be high-leverage).
   - **Unnamed composites:** composite chains appearing ≥ M times across runs but with no registered single-primitive name (signal: a candidate primitive is being constantly re-derived).
7. Pick the top-1 candidate (anti-greedy: rotate across high-reuse vs unnamed-composite buckets to maintain variety).
8. Build the Type-E DR prompt (template at bottom of this charter).
9. Enqueue to `agora.research_queue` via `agora_persist.enqueue_research` with `target_substrate_type='E'`, `requested_by='Atalanta'`, `priority=4`, `queue_ref=ATA-<UTC-date>-<NNN>`, tags identifying the candidate kind.
10. Emit artifact at `agents/atalanta/artifacts/dispatch_<queue_ref>.md` + `log_work(stage='atalanta_dispatch', ...)`.
11. If no new Apollo runs since last scan → emit `NULL_TICK` sentinel with `{reason: 'no_new_apollo_runs', last_scanned: ...}`.
12. If Apollo runs dir does not exist → emit `UPSTREAM_NOT_FOUND` sentinel (clear human-actionable signal: Apollo's output path needs to be configured).
13. Anti-silence: increment counter on null/upstream-not-found ticks; alarm at threshold 50.
14. Persist state and release lock.

---

## Backlog source

The Apollo runs directory. If Apollo has multiple output locations (e.g., `apollo/runs/` for v1 and `apollo/runs_v2/` for v2), the daemon scans all configured roots. Per-run files are expected to be JSON or JSONL with at least: `run_id`, `completed_at`, `organisms`, each organism carrying its `primitive_sequence`.

`self_generate_backlog()` returns the current high-reuse + unnamed-composite buckets — exposed for orchestration view; not consumed directly by the tick.

If Apollo's output path changes or is unset, Atalanta refuses to silently no-op. The `UPSTREAM_NOT_FOUND` sentinel is the loud signal that wiring is missing.

---

## Downstream consumer

Pythia dispatches Atalanta's queries. Returned reports are tagged `target_substrate_type='E'`; ingestion to `techne/registry/primitive_candidates/` is downstream (TBD; currently manual). Once Techne reviews and promotes a candidate to a registered primitive, it becomes available in Apollo's next run.

The verdict-back protocol: when the Pythia report completes, the ingester (manual for now) reads the report's "primitive_name + signature + composition_rules" block and files a primitive proposal to Techne. Tracked via the `verdict_back_to` tag on the queue row.

---

## Type-E DR prompt template

```
Identify candidate atomic reasoning primitives that recur across the following Apollo organisms.

CONTEXT:
Apollo evolves primitive routing DAGs. The Prometheus substrate uses these to build reusable reasoning tools. We are looking for primitives that should be NAMED and REGISTERED in the substrate's primitive catalog, either because they are repeatedly re-derived from composites, or because they appear in many successful organisms but lack a canonical name.

OBSERVATION (from Atalanta's scan of recent Apollo runs):
{observation_summary}

THE CANDIDATE:
{candidate_description}

OUTPUT (strict JSONL block per primitive proposal):
{"primitive_name": "<CamelCase>", "signature": "<input_types> -> <output_type>", "when_applied": "<conditions of applicability>", "composition_rules": "<how it composes with existing primitives>", "evidence_organisms": [<organism ids>], "related_existing_primitives": [<existing primitive names if any>]}

Cite at least 2 of the 5 mandated calibration patterns where applicable: PATTERN_PRIME_GRAVITATIONAL_OVERFIT, PATTERN_CONDUCTOR_CONFOUND, PATTERN_BASE_RATE_NEGLECT, PATTERN_VRAM_TRUNCATION_ARTIFACT, PATTERN_RANK_PARITY_LEAK.

After the JSONL, give a one-paragraph rationale: why this primitive is likely to be load-bearing, and what current substrate gap it fills.
```

---

## Structured logging

Same three-stream pattern as Hypatia:

- **Text log** at `agents/atalanta/logs/atalanta.log`
- **Events JSONL** at `agents/atalanta/events.jsonl`
- **State file** at `agents/atalanta/state/state.json` — `{last_scanned_run_id, last_pick_at, anti_silence_counter, total_dispatched_lifetime, total_null_ticks_lifetime, recently_fired_candidate_hashes: {hash -> ts}}`
- **Heartbeat** via `session_telemetry.register_session` with rich `status_json`
- **Work events** via `session_telemetry.log_work`: `atalanta_dispatch`, `atalanta_null_tick`, `atalanta_upstream_not_found`, `atalanta_self_audit_null`, `atalanta_startup`, `atalanta_shutdown`
- **Per-dispatch artifact** + **per-null-tick artifact** in `agents/atalanta/artifacts/`

---

## Operational

**Single-instance lock:** `agents/atalanta/atalanta.pid`. Same shape as Hypatia.

**Detached launch:** `scripts/atalanta_loop_launch.bat` invoked via `Start-Process -WindowStyle Hidden`.

**CLI:**
- `python -m agents.atalanta.daemon --once`
- `python -m agents.atalanta.daemon --loop --interval 1800`
- `python -m agents.atalanta.daemon status`

**Hard stops:**
- Never write to `techne/registry/` directly (primitive promotion is Techne's call).
- Never read raw `*Key*` / `.env` files.
- Apollo's organism-log parser must tolerate format drift gracefully (Apollo's output schema evolves; parse-failure → emit `APOLLO_FORMAT_DRIFT` sentinel, do not silently drop).

**Anti-gravitational-well vigilance:** the conventional move is to query for "more interesting primitives in general." Atalanta must instead always anchor candidates to concrete Apollo-organism evidence. A primitive proposal without organism IDs in `evidence_organisms` is the failure mode — skip and re-orient.

— Aporia, 2026-05-23
