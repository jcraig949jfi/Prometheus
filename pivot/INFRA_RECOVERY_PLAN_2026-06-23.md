# Prometheus Infrastructure Recovery Plan — 2026-06-23

**Author:** Aporia (Claude Opus 4.8) · **Trigger:** fleet 0/43 down (M4 monitor email)
+ James's directive "get the infrastructure back up."
**Status:** PLAN for review. Grounded in verified probes (E3) + the actual config/migration
code. Supersedes the Redis-assuming parts of `thesauros/MIGRATION_PLAN.md` and the
`.176`/`devmirror` defaults in `scripts/agora_persist.py` + `thesauros/prometheus_data/config.py`.

---

## VERIFIED 2026-06-24 (James: "Postgres live, Redis off for the foreseeable future")

Connected to the live local Postgres (`127.0.0.1:5432`, `postgres`/`prometheus`, pgpass present).
**The recovery is much further along than this plan assumed:**
- **4 DBs live:** `prometheus_fire`, `prometheus_sci`, `lmfdb`, `postgres`. The **DuckDB→PG migration is
  largely DONE** — `prometheus_fire` has `charon_duckdb`, `noesis`, `zeros`, `xref`, `kill`, `sigma`,
  `tensor`, `signals`, `analysis`, `results`, `meta` schemas. (Phase 2 mostly complete.)
- **The Redis-free message bus already exists on Postgres:** `agora.messages` (196 msgs, Redis-style
  `stream_id`, recent traffic) is the live bus. A `bus` schema scaffolds Redis data structures
  (`hashes/kv/lists/sets/zsets/stream_entries`) — currently empty, ready if hot-path state needs them.
  **So Phase 1's "one real rebuild" (the PG bus) is already built.**
- **agora schema populated:** agent_heartbeats 33, research_queue **425** (Pythia-ready), clio_papers
  596, clio_claim_extractions 1082, intelligence_outputs 10,946, machine_probes 35,947, sigma.claims 1079.
- **Two fan-out claims were STALE (captured during the outage):** a `sigma` schema *does* exist (1079
  claims, 7 caps, 0 promoted symbols); Clio *did* produce (596 papers in PG). **→ The deeper-dive must
  re-verify every "dead/vacuous" dossier verdict against live PG before any retire.**

**Remaining infra work is now small:** (a) point agent configs off the stale `.176` to `127.0.0.1`/`.202`
(`AGORA_POSTGRES_HOST`, `PROMETHEUS_*_HOST`, `~/.prometheus/db.toml`); (b) confirm daemons read/write
`agora.messages` (not Redis) on startup; (c) decide whether hot-path state (graph/landscape/hypothesis
queue) populates the `bus` schema or lives as relational tables. No bus to build; no Redis to restore.

### DONE 2026-06-24 — core config repointed + verified (Aporia)
Canonical address: **`192.168.1.202`** (PG verified listening on both `127.0.0.1` and `.202`; works fleet-wide).
- `~/.prometheus/db.toml` **created** → `fire`/`sci`/`lmfdb` → `192.168.1.202`, `postgres`/`prometheus`
  (overrides the stale `devmirror.lmfdb.xyz` defaults in `prometheus_data/config.py`).
- `scripts/agora_persist.py` default `AGORA_POSTGRES_HOST` `.176` → `.202`.
- `scripts/clio_submitter.py` `PROMETHEUS_FIRE_HOST` default `.176` → `.202`.
- **Verified:** `prometheus_data.get_pg_dsn('fire')` → `.202/prometheus_fire`, connects (research_queue 425);
  `agora_persist.read_all_agents()` → 33 rows. **Spine + Aporia keepers (Pythia, Clio) are PG-path, not
  Redis-path → unblocked by this repoint alone.**

### `.176` backlog (NOT swept — fix on-demand / separate task)
- **~80 ad-hoc analysis scripts** (`cartography/shared/scripts/*`, `harmonia/wsw_*`, `rank*`, `F0*`,
  `keating_*`, `explore_*`): hardcode `host='192.168.1.176'` AND usually `lmfdb/lmfdb` creds — **doubly
  stale** (host + creds). Not the coordination path; fix the specific script when it's next re-run, or
  refactor to import `prometheus_data.config`. Low priority.
- **Redis-host setters** (`scripts/post_*`, `charon_loop.py`, `harmonia_loop.py`, `session_telemetry.py`,
  `harmonia/agents/_base.py`, `_scorer.py`, `runners/gen_*`): set `AGORA_REDIS_HOST=.176` for the
  **retired** Redis. Dead config; the real fix is migrating those daemons (mostly swarm/retire-candidates)
  to the live `agora.messages` PG bus — a separate task, not a host swap.

---

## 0. Verified ground truth (probed 2026-06-23, E3)

- **M1 = SKULLPORT = `192.168.1.202`.** The old `.176` is unreachable from M1 (both ports time out).
- **Local Postgres is UP** on `127.0.0.1:5432`. **No local Redis** (refused; `redis-server` not installed).
- **Config drift is the root cause:** `agora_persist.py` defaults to `192.168.1.176`;
  `prometheus_data/config.py` defaults to `devmirror.lmfdb.xyz`. Neither points at `.202`.
  When M1's IP moved, everything kept dialing dead hosts.
- **DuckDB files present:** `charon/data/charon.duckdb` (1.2 GB), `noesis/v2/noesis_v2.duckdb` (20 MB).
- **M3 (Gandalf) is hardware-dead** — needs motherboard + CPU. This is the box the forge ran on.
- **43 components enumerated** in `docs/state.json`, all down; 0 discoveries, 0 deep-research reports.

## Locked decisions (from James, 2026-06-23)

1. **One backbone: Postgres on M1 (`.202:5432`).** No DuckDB. No Redis (done fighting WSL).
2. DuckDB data was always meant to land in Postgres → finish that migration, then archive.
3. Redis is **eliminated**, not restored → its two jobs (heartbeats, message bus) move to Postgres.

**Good news that shrinks the job:** Postgres is *already* the durable backbone. `agora_persist.py`
defines a rich idempotent schema — `agent_heartbeats`, `intelligence_outputs`, `machine_probes`,
`clio_papers`/`clio_claim_extractions`, **`research_queue`** (the Pythia/Deep-Research pipeline),
`gpu_reservations`. Heartbeats are *already dual-written* to PG and the dashboard already falls
back to it. So Redis removal is mostly "stop writing to Redis + rebuild the one message-bus piece,"
not a from-scratch rebuild.

---

## Phase 0 — Establish the backbone (M1, local, reversible) — *Aporia can do most*

1. **Locate the agent venv** (the system `python` on PATH lacks `psycopg2`/`redis`; the daemons
   use a venv). Establish which interpreter the fleet runs under.
2. **Verify local PG:** does `prometheus_fire` exist, with the `agora` schema + tables, and what
   credentials? (`agora_persist.py` assumes `postgres`/`prometheus`.) If the schema is missing,
   `python scripts/agora_persist.py init` builds it idempotently.
3. **Pick ONE canonical connection** and make it config-driven, not hardcoded (per `feedback_paths`):
   bind everything to `.202` via `~/.prometheus/db.toml` + a shared env file
   (`PROMETHEUS_*_HOST`, `AGORA_POSTGRES_HOST`). Other machines point their `db.toml` at `.202`.
4. **Kill the dead defaults in code:** `agora_persist.py` `.176`→`127.0.0.1`; `config.py`
   redis/pg defaults off `devmirror`. Small, reversible edits; env still overrides.

**Gate:** a heartbeat written from M1 appears in `agora.agent_heartbeats` over the local socket.

## Phase 1 — Sever Redis — *some Aporia, the bus needs design*

1. **Heartbeats:** stop the Redis dual-write; make PG the primary read/write path (it's already
   the fallback). Locate `AgoraClient` and flip the primary.
2. **The message bus is the one real rebuild.** The `agora:main / discoveries / challenges / tasks`
   Redis Streams are the inter-agent comms. Replace with a Postgres-backed bus:
   `agora.messages (id BIGSERIAL, stream TEXT, payload JSONB, ts TIMESTAMPTZ)` + per-consumer
   cursor on `id` (agents *already* track `last_read_ids` — see `roles/Aporia/loop_state.json`).
   Polling suffices at this cadence; `LISTEN/NOTIFY` optional for push later. Preserve the
   `AgoraClient` API so consumers don't change — swap only its internals. ~1 module.
3. **Make Redis optional in startup** so no agent hard-fails on its absence.

**Gate:** a test message round-trips through `agora.messages` between two processes.

## Phase 2 — Finish DuckDB → Postgres — *needs venv + care; greenlight before touching 1.2 GB*

- Follow `thesauros/MIGRATION_PLAN.md` **but redirect the four Redis-destined tables**
  (`graph_edges`, `known_bridges`, `landscape`, `hypothesis_queue`) **to Postgres** — that plan
  assumed Redis stays; that assumption is now reversed.
- Start from the existing `thesauros/migrate_noesis_v2.py` + `migrate_p3_duckdb.py`.
- Preserve object IDs (plan's Option A). Reconcile row counts. Archive DuckDB read-only — **never
  delete during migration.**

**Gate:** DuckDB row counts == Postgres counts; 100-object spot-check matches.

## Phase 3 — Bring up the live fleet — *per-machine; James/operators*

- **Live:** M1 (`.202`), M2 (spectrex5), M4 (aletheia). **Down:** M3 (gandalf) until hardware.
- **Order:** M1 backbone (PG + bus) → M1 operators (Aporia/Techne/Ergon + tools Clio/Pythia/
  Hypatia/Atalanta/Talos/Pheme) → M2 (Charon swarm, Apollo) → M4 (Pronoia monitor + Calliope).
- Point each machine's `db.toml` at `.202`.
- **Do not reflexively restart all 43** — bring up the spine + the components that earn it, defer
  the rest (the scoring effort, deferred to after infra; ties to Stand F retirement).

## The M3 / forge linkage — *surface loudly; this is the strategic part*

M3 hosted **Hephaestus, the forge.** The reset's agreed **decider is M1-metabolization
(forge → Learner)** — see `aporia/docs/M0_anti_calibration_design_aporia_2026-06-23.md` §10 +
`feedback_m1_metabolization_decides_not_m0_recognition`. **Therefore M3 being dead means the one
experiment that decides the 20-year bet is hardware-blocked.**

Options, in leverage order:
1. **Relocate the forge to a live GPU machine** (which of M1/M2/M4 has GPU headroom? the
   `gpu_reservations` system implies ≥1 does — needs confirming). Highest leverage: unblocks the
   decider, not just "lights back on."
2. Run the forge degraded on smaller local models on a live box.
3. Wait for the M3 mobo+CPU repair.

## What Aporia can start now vs what needs James

- **Aporia solo (local, reversible):** Phase 0 verification + config consolidation; draft the
  Postgres message-bus module (1.2); prep/redirect the migration scripts (Phase 2 prep, no data moved).
- **Needs James:** confirm `.202` + PG creds canonical; **which live machine has a GPU** (forge
  relocation); per-machine restarts (Phase 3); greenlight before moving the 1.2 GB data.

## Self-guard

Every phase has a verification gate above — nothing is "done" on assertion. And bring-up follows
the reset doctrine: restore the spine + what scores, not the whole monoculture.

---
*Recovery plan, Aporia 2026-06-23. The infra task and the North Star are the same task here:
the forge's homelessness (M3 dead) is what blocks the metabolization experiment, so forge
relocation is the highest-leverage item, not a footnote.*
