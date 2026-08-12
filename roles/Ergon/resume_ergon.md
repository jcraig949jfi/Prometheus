# Ergon — resume point (pick up here after a restart)

**Last worked:** 2026-06-23 → 08-12 session. **Role:** Ergon (the engine / the Learner
march). This is the single "start here" doc. Everything below is committed + on disk.

---

## 0. TL;DR — where to pick up

The session was mostly an **infra rescue** (all done + landed by the team) plus a
**research re-orientation** back to the Learner. The live decision when we stopped:
which Ergon research thread to drive. James pivoted the last turn to reviewing
**Leanstral 1.5** (Mistral's Apache-2.0 Lean-4 proof agent) and how Prometheus uses it.

**Recommended pickup:** prototype the **Leanstral → M0 Set-C probe** (see §5.A). It's
the highest-value, doctrine-safe next step and connects to the reassessment keystone.

---

## 1. Environment / access (verified this session)

- **Postgres is LOCAL and healthy** on this host (skullport = `192.168.1.202`). The old
  `192.168.1.176` is a dead/stale address — do not chase it. See
  `DB_DIAGNOSIS_2026-06-23.md`.
  - `psql`: `C:/Program Files/PostgreSQL/17/bin/psql.exe`
  - Creds: **`postgres` / `prometheus`** (superuser) and **`lmfdb` / `lmfdb`** (read +
    write on the `bus` schema). Stored in `%APPDATA%/postgresql/pgpass.conf` — never in
    tracked files.
  - DBs: `lmfdb` (363 GB, ~52M rows), `prometheus_fire` (results/kills/bus/charon_duckdb),
    `prometheus_sci`. Note: use `reltuples`/`COUNT(*)`, NOT `n_live_tup` (stats were stale
    → false-empty; ANALYZE was run this session).
- **Torch/CUDA Python** (for LoRA/model work): `C:/Users/jcrai/AppData/Local/Programs/Python/Python311/python.exe`
  (torch 2.11+cu128, CUDA true). Base `python` is 3.12, no torch — but this session I
  installed **`duckdb` and `psycopg2`** into it for the migrations.
- Local model: Qwen2.5-Math-1.5B-Instruct under `E:/hf_cache/hub`. RTX 5060 Ti; LoRA
  rank-16 ≈ 10 min. **VRAM ceiling ~3–4B** (119B Leanstral will NOT run locally).
- Redis is retired (see §3); the message bus is now Postgres-backed.

---

## 2. What we accomplished — INFRA (all landed across the team)

The reassessment (`pivot/REASSESSMENT_2026-06-22_*`) flagged the "data spine dark" and
prescribed a DuckDB fallback. **That premise was wrong on this host** — I diagnosed it,
fixed the real root causes, and the corrections were folded into doctrine.

- **DB diagnosis** (`270e4c4d`, `14dba21b`): Postgres isn't dark, `.176` is a stale
  address. Reassessment CC-3 corrected from "DuckDB fallback" → "fix Postgres root cause."
  The `.176`→`.202` config repoint later landed (`983fd077`).
- **object_id repair** (`6f06e1b8`): `zeros.object_zeros` had `object_id` NULL on
  **1,984,167 / 2,009,089 rows (98.8%)** — root cause a **desynced sequence**
  (`last_value=1` vs `max=134475`). Built a slow-roll (Windows Scheduled Task
  `PrometheusRekeyObjectZeros`) that minted registry ids + backfilled; completed in
  ~8h15m to **0 NULL, all object_ids unique**. Reversible via `object_id > 134475`.
  Tooling + reverse SQL: `ergon/repair/` (`README_rekey_2026-06-23.md`).
- **Corrupt-table drop + more sequence fixes** (`59d0ac66`): dropped 3
  `*_corrupt_20260416` tables (~1.28 GB); fixed 2 more desynced sequences
  (`xref.bridges`, `meta.ingestion_log`) — same April-migration failure class.
- **DuckDB → Postgres migration** (`90ff4f2d`): all 14 `charon.duckdb` tables mirrored
  verbatim into `prometheus_fire.charon_duckdb.*` (**1,242,918 rows, counts verified**);
  `noesis_v2.duckdb` already in `noesis.*`. **Postgres now holds ALL duckdb data.**
  `charon.duckdb` kept frozen as fallback (do NOT delete). Charon then repointed its
  `charon/src` read path off `duckdb.connect()` from my handoff prompt (`fa8f625a`).
  Doc: `DUCKDB_RETIREMENT_AUDIT_2026-06-24.md`.
- **Redis → Postgres bus** (`c0419972`, `3e276531`): built **PgRedis**
  (`thesauros/prometheus_data/pg_redis.py`), a drop-in for the redis-py subset actually
  used (streams / hashes / zsets / sets / lists / kv+ttl), backed by `prometheus_fire`
  schema `bus`. `get_redis()` returns it by default (`PROMETHEUS_USE_REDIS=1` reverts);
  `get_bus(decode_responses=)` for direct-connect callers. Harmonia repointed her 33
  files (`e7b41f14`) + added cross-machine host detection; I did `cartography/viewer/server.py`
  + list ops. **All active callers now on the PG bus.** Doc: `REDIS_TO_POSTGRES_2026-06-24.md`.

Net: Postgres healthy & local; DuckDB data fully migrated (code repoint done by Charon);
Redis retired onto Postgres. The three data stores are consolidated on local Postgres.

---

## 3. Subsystem state (quick reference)

- **Postgres** — healthy, local (`.202`), all 3 DBs populated. `charon_duckdb` schema =
  faithful DuckDB archive. `bus` schema = the message bus.
- **DuckDB** — frozen fallback only (`charon.duckdb` Apr 3, `noesis_v2.duckdb` Mar 30).
  Data all in Postgres. Keep until Charon's repoint is fully validated; then dossier +
  HITL before any RETIRE (no delete — `feedback_retirement_needs_thoughtwork_dossier_hitl`).
- **Bus** — Postgres-backed (`bus.*`). Redis off; flip back only via `PROMETHEUS_USE_REDIS=1`.

---

## 4. What we accomplished — RESEARCH (re-orientation, no new experiment run yet)

Re-read the Learner thread. Key standing results (unchanged, re-confirmed):
- **Routing eval** (`ROUTING_EVAL_2026-06-09.md`): mined-failure residue is navigable
  **behaviorally** (warm-start co-solve clustering, +0.075, robust in the tail) but **not
  semantically** (cold-start concept-label routing NULL — real fields ≈ shuffled). The
  Learner's true objective (route a *new problem* → tool) is **untestable** on the current
  artifact: it's top-10 truncated and lacks probe features, and the **failure-mining
  producer is NOT in-repo** (confirmed — hephaestus only has `benchmark_models.py`,
  `test_v2_tools.py`).
- **Compute-traces** (`COMPUTE_TRACE_RESULT_2026-06-08.md`, `ergon/learner/greedy/`):
  per-op worked traces teach in-op computation (in-op +0.16). Cross-op "transfer" (+0.36
  vs base) is **format acquisition, not computation** — `trace ≈ verdict` on held-out
  ops; `ood_summation` barely moved. Isolation metric = `acc(trace) − acc(verdict)` on
  held-out ops (~0 at 8 ops).

The open research fork (past-Ergon deferred to James; still open):
- **(1) coverage→transfer experiment** — extend `compute_traces.py` with more ops; train
  trace vs verdict at narrow vs broad coverage; test whether breadth grows `(trace−verdict)`
  on held-out ops or confirms the 1.5B capacity ceiling. Self-contained, falsifiable.
- **(2) router-grade artifact** — reconstruct the missing failure-mining producer to emit
  full solve sets + probe features, then test cold-start routing. North-star-aligned but
  bigger/riskier (probe alignment is unverifiable — risks the exact doctrine failure mode).

---

## 5. Next moves (ranked)

### A. RECOMMENDED — Leanstral 1.5 → M0 Set-C probe
Leanstral 1.5 (Apache-2.0, 119B/6.5B-active MoE, Lean-4 proof agent, PutnamBench 587/672;
HF `mistralai/Leanstral-1.5-119B-A6B`, blog `mistral.ai/news/leanstral-1-5`). **Why it's
usable despite the "frontier models aren't allies" doctrine:** its output is **checked by
the Lean kernel, not another model** — a wrong proof doesn't compile, so no AI-to-AI
inflation and we needn't trust its benchmark numbers. It's a *cheap generator feeding a
ground-truth verifier*, an arbiter — NOT an explorer (keep it downstream of generation, or
it drags us into the ITP gravity well).

**Probe:** wire Leanstral (free Mistral API — 119B won't run on the local 5060 Ti) behind
the EXISTING Lean harness (`agents/_shared/proof_search/`, the `lake`/Lean-REPL env under
`agents/_shared/external_tools/`, `rhea/src/lean_verifier.py`) and use it to generate +
Lean-check ~10 **M0 Set-C** candidate claims. This is the reassessment's keystone:
v2 defined M0 Set C as "synthetic true claims from formal systems where truth is externally
checkable" — Leanstral+Lean IS that oracle. **Coordinate with Harmonia** (`harmonia/experiments/m0_anticalibration*.py`
is live) so output drops into their set format. Validates integration + advances the keystone
+ stays in the "arbiter not explorer" lane.

Other Leanstral fits (later): formal falsification tier for the battery; autoformalization
as a representation *discriminator* (what the substrate finds that Lean CAN'T express is
where the non-traditional bet lives); the 85 unsolved PutnamBench problems as hard-reasoning
calibration anchors; verify `prometheus_math` ops (the Learner's gold).

### B. If not Leanstral — run the coverage→transfer experiment (fork option 1). Falsifiable,
self-contained, closes the compute-trace thread. Preregistered kill: `Δ_broad ≤ Δ_narrow`
⇒ coverage does not induce transferable computation (capacity ceiling).

### C. Watch item — the seam. The allowlist rebuild (`6439311a`) fixed the Theseus→Ergon
handoff, but the freshest anchors in `theseus/handoff/ergon_outbox/` are quarantined
(06-07, pre-fix). Confirm the seam re-runs clean before relying on its failure-data.

---

## 6. Doctrine touchpoints (this session)

- Reassessment live thesis: Prometheus = the **TDD layer / progress meter**; keystone = **M0**
  (can the selector recognize novelty outside its calibration manifold);
  `feedback_m1_metabolization_decides_not_m0_recognition` says the *decider* is
  **M1-metabolization** (model consumes kill-geometry, behavior changes, survives ablation).
  Techne's latest pickup (`5b8a80c2`) is also M1-metabolization — align there.
- `project_db_spine_is_local` (memory) updated with the Postgres/DuckDB/bus facts.
- Guardrails in play: `feedback_frontier_models_window`, `feedback_llm_convergence_is_gravity_amplifier`,
  `feedback_ai_to_ai_inflation` (all reasons Leanstral must stay an *arbiter*),
  `feedback_anti_gravitational_well`, `feedback_vram_ceiling`, `feedback_take_a_stand`.

— Ergon
