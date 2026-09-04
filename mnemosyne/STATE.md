# Mnemosyne State — 2026-09-01 (read-only world-state refresh)

## NOTE TO MNEMOSYNE
This file was fully rewritten 2026-09-01 after a four-month gap (previous body:
2026-04-16 + a 2026-04-29 sigma addendum; both preserved in git history and in
`roles/Mnemosyne/SESSION_JOURNAL_20260415.md` / `_20260429.md`). Everything
below was verified against the LIVE databases on 2026-09-01. This session was
survey-only: no ingestion, no schema changes, no writes to any database, per
James's explicit directive.

---

## Identity
- **Role:** DBA & Data Steward (roles/Mnemosyne/RESPONSIBILITIES.md — WARNING:
  its stack diagram is stale, see "Stale documentation" below)
- **This session ran on:** M1 (the machine hosting the local Postgres spine)

## Connections — THE BIG CHANGE since April

**The Postgres spine is LOCAL on M1 (`192.168.1.202` / localhost).**
`192.168.1.176` is a powered-off dead box; every doc that mentions it is stale.

| Service | Where | Status (verified 2026-09-01) |
|---------|-------|------------------------------|
| PostgreSQL 17.9 | localhost:5432 (M1) | LIVE — all three DBs served |
| lmfdb | 365 GB | READ-ONLY mirror, on `fast_space` tablespace (F:\pg_tablespace) |
| prometheus_sci | 320 MB | LIVE, unchanged since 04-16 |
| prometheus_fire | 2.76 GB | LIVE and ACTIVELY WRITTEN (agora schema, today) |
| Redis | — | **RETIRED 2026-06-24.** PgRedis (`thesauros/prometheus_data/pg_redis.py`) is the drop-in, backed by `prometheus_fire.bus`. `PROMETHEUS_USE_REDIS=1` reverts. |
| DuckDB | — | **RETIRED 2026-06-24.** Mirrored verbatim into `prometheus_fire.charon_duckdb.*` (14 tables). `.duckdb` files frozen as fallback. |

Credentials: read-only `lmfdb/lmfdb`; superuser `postgres/prometheus`; belong in
`%APPDATA%\postgresql\pgpass.conf`, never in tracked files. `psql.exe` at
`C:\Program Files\PostgreSQL\17\bin`.

---

## lmfdb (365 GB — verified reltuples + sizes)

| Table | Rows | Size | Notes |
|-------|------|------|-------|
| lfunc_lfunctions | 24,351,376 | 346 GB | all-TEXT columns; 6 indexes |
| nf_fields | 22,178,568 | 9.8 GB | **FULL** (the P6 partial-pull item is DONE) |
| ec_curvedata | 3,824,372 | 2.0 GB | |
| bsd_joined (matview) | 2,481,569 | 2.6 GB | EC ↔ L-function join, see thesauros/bsd_joined_view.md |
| mf_newforms | 1,141,510 | 3.9 GB | |
| artin_reps | 798,140 | 468 MB | |
| g2c_curves | 66,158 | 43 MB | |

## prometheus_sci (unchanged since 2026-04-16)
~1.16M rows across 14 tables (groups 545K, oeis 394K, qm9 134K, lattices 39K,
knots 13K, materials 10K, …). See `thesauros/data_dictionary.md`.

## prometheus_fire (2.76 GB) — what changed since April

Real `COUNT(*)` where noted; otherwise reltuples (spot-checks matched).

- **xref.object_registry: 2,118,642** (was 134K on 04-16). Grew ~15x via the
  object_id NULL repair / rekey — see `ergon/repair/README_rekey_2026-06-23.md`
  and commit 6f06e1b8a ("slow-roll repair for object_zeros NULL object_id").
- **zeros.object_zeros: 2,009,089** (was 121K) — same repair campaign.
- **zeros.dirichlet_zeros: 0** (was 184,830). The rows live in
  `charon_duckdb.dirichlet_zeros` (184,830). Emptying looks deliberate
  (dedup with the mirror) but I have not found the doc that says so —
  OPEN QUESTION below.
- **charon_duckdb.*: 14 tables, ~1.24M rows** — DuckDB retirement mirror
  (graph_edges 396K, dirichlet_zeros 185K, objects 130K, object_zeros 121K,
  landscape 119K, disagreement_atlas 119K, modular_forms 102K, …). See
  `roles/Ergon/DUCKDB_RETIREMENT_AUDIT_2026-06-24.md`.
- **agora schema is now the live operations center** (13 tables; grew from 3):
  - machine_probes: 112,307 rows, 2026-05-24 → **2026-09-01 (written today)**
  - intelligence_outputs: 13,357 rows, 2026-05-17 → **2026-09-01**
  - agent_heartbeats: 36 agents; online today: Pronoia (M4), Elenchus (M2),
    MachineProbe-M4
  - clio_papers 596 / clio_claim_extractions 1,082 / clio_quality_snapshots 238
  - research_queue 425, gpu_reservations 4, messages 196 (last message
    2026-04-29 — stream-style messaging effectively superseded by these tables)
- **sigma schema grew from 3 to 7 tables** and is in use: claims **1,079**,
  capabilities 7; symbols/residuals/evaluations/refinements/bindings 0.
  NOTE: `sigma.claims` columns (target_name, hypothesis, evidence, kill_path,
  target_tier, verdict_* …) differ from the 04-29 MVP shape — the kernel
  evolved after my last session (Substrate-Tester fire commits in git).
- signals.specimens: 72 (was 0). battery_results still 0.
- Still empty: results.*, tensor.*, kill.* schemas.
- **bus schema (PgRedis backend): provisioned, essentially unused** — all six
  tables empty, stream gid sequence at 8 (eight entries ever). The bus exists;
  traffic doesn't. Agora coordination happens via the agora.* tables instead.

---

## Standing traps (still true)
1. `pg_stat_user_tables.n_live_tup` reads 0 on populated 300GB+ tables (stats
   reset at the 04-16 migration, never re-ANALYZEd). Use `reltuples` or real
   `COUNT(*)`. This false-empty reading once got the spine called "dark."
2. lfunc_lfunctions is all-TEXT; cast-heavy queries are slow by construction —
   use bsd_joined or typed matviews.
3. Do not read from the frozen `.duckdb` files; the Postgres mirror is
   authoritative.

---

## Open queue (mnemosyne/queue/requests.jsonl)
- **REQ-001** (Aporia, 04-26, medium): Bloom Erdős catalog → questions.jsonl.
  Cloudflare 403 gating. **OPEN — HELD: James directed 2026-09-01 "don't
  ingest anything."**
- **REQ-002** (04-26, high): MathNet olympiad corpus (30,676 problems).
  License + download URL unverified. **OPEN — HELD, same directive.**

## Open questions / hygiene backlog (no action taken)
1. `zeros.dirichlet_zeros` emptied — confirm intentional and record where.
2. RESPONSIBILITIES.md stack diagram describes the dead .176/Redis world;
   rewrite when authorized.
3. Agent DB users (harmonia, ergon, charon, ingestor) still ride
   `postgres/prometheus`; per-agent creds never rotated in.
4. ANALYZE never rerun since the migration (reltuples close but stats stale).
5. `thesauros/data_dictionary.md` (authoritative data reference) predates the
   rekey, DuckDB retirement, agora expansion, and sigma v2 — needs a refresh
   pass.
6. sigma.claims schema drift vs the 04-29 MVP — read the Substrate-Tester
   fire history before touching sigma.

## Legacy non-Postgres stores — 2026-09-01 inventory (full report in journal)

Deletion of `charon/data/charon.duckdb` (1.18 GB) and `noesis/v2/noesis_v2.duckdb`
is gated on a todo-sweep: I placed `todo_20260901.md` in roles/{Charon,
CrossDomainCartographer, Harmonia, Koios, Ergon}; each seat flips its Status
to DONE when its legacy-store code is repointed/retired. **Sweep
`roles/*/todo_*.md` each session; delete only when all flipped, after a final
grep for `duckdb.connect` outside archive/.**

- charon/src: REPOINTED to Postgres via facade (commit fa8f625a1) — the
  06-24 audit's "still on duckdb.connect" is stale. Remaining: trivial
  version-banner import in charon/scripts/full_audit.py:162.
- Biggest blocker: ~180 read-only duckdb call sites in cartography/shared/
  scripts (~110), cartography/v2 (~50), harmonia/scripts (~20), koios (1).
- **MNEMOSYNE DEFECT — kill_taxonomy never migrated:** `mnemosyne/
  migrate_m2.py:231-248` reads DuckDB `hypothesis_queue` instead of
  `forge/v3/kill_taxonomy.db` (SQLite: 21 kills, 10 negative_dimensions)
  and returns 0 as success — that is why `kill.taxonomy` is empty. Ergon's
  live hypothesis gate (`ergon/tensor_executor.py:131`) consumes the SQLite
  file today. Fix loader + migrate (awaiting go-ahead), then Ergon repoints.
- `thesauros/prometheus_data/pool.py:191` `get_duckdb()` — deprecated, zero
  callers, still exported from `__init__.py:33,35`. Remove from the public
  API as part of the deletion checklist (my item).
- Deliberately SQLite, NOT debt: `theseus/orchestration/signature_index.sqlite`
  (live ledger, 3,311 sigs), `ludus/atlas_of_worlds/atlas.db`,
  `SerendipityFoundry/.../var/engine.db` (Gen-2 design choice, per its
  migration doc). Leave alone.
- Dormant never-migrated agent stores (aletheia KG / clymene vault / skopos
  scores, last touched Mar–Apr): RETIRE-after-HITL candidates per
  `pivot/COMPONENT_DOSSIERS_2026-06-24.md:627`; DB files kept, no todo issued
  (no role seats). Dead: archive seti mlflow.db, sigma_kernel demo dbs.
- sigma_kernel defaults to its SQLite backend (`sigma_kernel.py:449`); the
  Postgres `sigma` schema serves a newer 7-table shape with 1,079 claims.

## Documents of record for the April→September gap
- `roles/Ergon/DB_DIAGNOSIS_2026-06-23.md`
- `roles/Ergon/DUCKDB_RETIREMENT_AUDIT_2026-06-24.md`
- `roles/Ergon/REDIS_TO_POSTGRES_2026-06-24.md`
- `ergon/repair/README_rekey_2026-06-23.md`
- `roles/Mnemosyne/SESSION_JOURNAL_20260901.md` (this refresh)
