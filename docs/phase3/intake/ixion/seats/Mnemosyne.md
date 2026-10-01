# Seat dossier: Mnemosyne

Crawler label: memory (Ixion sub-crawler)
Date: 2026-10-01 (date -u: Thu Oct 1 09:47 UTC 2026)
Base SHA read: bed05507a (origin/main, worktree F:\Prometheus-worktrees\ixion-phase3)
Host: M1 / SKULLPORT. Postgres reads were read-only sessions (default_transaction_read_only=on) against
localhost prometheus_fire, system_identifier 7628127204585430828 (the "canonical" store by the seat's own
identity definition).

Fully read: roles/Mnemosyne/RESPONSIBILITIES.md, STATUS.md, RESPONSIBILITIES_2026-04_historical.md (first 60
lines), mnemosyne/STATE.md, mnemosyne/README.md, evidence_wiki/README.md, evidence_wiki/FROZEN.md,
evidence_wiki/ew/db.py, .claude/skills/evidence-wiki/SKILL.md, aporia/doctrine/critical_memories.md (headings +
first 2 rules), roles/base-role/MONITORS.md rows 15-22, 37-38, 82, 85, V3/V1/V2 experiment closure docs (verdict
sections), CREDENTIAL_ROTATION_TRACKER.md (table rows only; no secret material read or copied).
Sampled: ew/service.py (route list, health, log_read), ew/store.py (write gates), ew/search.py (model), git log
of evidence_wiki (all 70 commits listed), roles/Mnemosyne (52 commits), session journals (headings + overviews),
BACKLOG_H0H5.md (row status grep), integration/*_results.json (summary keys only), comms rows addressed to/from
the seat, ew schema (all 44 tables counted with count(*)).
NOT read: ew/closure.py, refs.py, campaign_ingest.py, projections.py bodies; migrations bodies (only names);
v1b/, v2/, v3/ benchmark arm outputs; gold/ corpus; the 12 journal files' full bodies; config.json values
(deliberately: R-1 says it carries credentials); the M2 host (pinned worktree, derived/ logs, D:\PrometheusBackups)
-- unreachable from M1, so every M2-side fact below is [HIST].

## 1 Charter and role history

- 2026-04-15 seat created as "DBA & Data Steward" for the Agora team [HIST] (da460b7e1; roles/Mnemosyne/
  RESPONSIBILITIES_2026-04_historical.md:13-15 "I don't do science. I make science possible.").
- 2026-04-15 session 2 on M2: migrated 162,769 rows into Postgres via mnemosyne/migrate_m2.py [HIST]
  (831fa3295; SESSION_JOURNAL_20260415.md:10-17).
- 2026-04-29 a Claude session "covered" the seat ("Mnemosyne out sick today ... be her") and applied the sigma
  schema to prometheus_fire [HIST] (7a053e6b6; SESSION_JOURNAL_20260429.md:5-10). The seat identity is a
  role a session puts on, not a persistent process [INFER].
- 2026-04-29 -> 2026-09-01: no Mnemosyne commits (git log -- roles/Mnemosyne mnemosyne, 4-month gap) [IMPL].
- 2026-09-01 read-only world-state refresh, then charter expansion: owner of the Evidence Wiki ("PEW",
  Prometheus Evidence Wiki) [IMPL] (60721f003, c711c5bf6; prompts/CHARTER_EVIDENCE_WIKI_V0_2026-09-01.txt).
- 2026-09-02 V1, V2, V3 charters run and closed in one day; V3 closeout -> state PEW_FROZEN_WAITING_FOR_INCUBATOR
  [IMPL] (cb43847e9; evidence_wiki/FROZEN.md:1-3).
- 2026-09-03..05 reopened under FROZEN.md criterion 1 for consumers: first integration (Harmonia), world-
  provenance seam, closure v0, durability (backup + restore verify), session-affinity / execution lineage [IMPL]
  (1376df4fd, 4cb02c733, 81b7aa2d4, 5f8b70d7a).
- 2026-09-11 base-role adoption; operator ruling D-23 amendment 3 redefines the boundary: "Mnemosyne does not
  adjudicate domain hypotheses; it scientifically validates the memory and evidence substrate" [IMPL]
  (4616c9797; RESPONSIBILITIES.md:15-21). April file kept verbatim with a SUPERSEDED banner [IMPL].
- 2026-09-16..18 seat runs on M2 (instance m2-9c10ae00) after M1 was handed to Nestor (ccb26df01); PEW service
  restarted on M2 fronting the M1 store; point release (campaign ingestion) 09-17; Campaign 4/5 ingestion 09-18;
  Campaign 6 storage contract v0.1 "design only" 09-18 [IMPL] (e8683ea3f, f81ddddbe, 0d448387e).
- After 2026-09-18 14:58 local: no Mnemosyne-authored commit on origin/main (git log -- roles/Mnemosyne
  evidence_wiki; last 8915b660f) [IMPL]. comms.agents shows last_sync_at 2026-09-18 14:31 -04 and
  last_active_at 2026-09-23 08:35 -04 (the latter is the watchdog's automated park post, #542) [IMPL].

## 2 Systems maintained

1. PEW / Evidence Wiki: Postgres schema `ew` (44 tables on the canonical store, counted) + FastAPI REST service
   (port 8377; 56 decorated routes in ew/service.py, 9 in ew/campaign_routes.py, grep count) + human wiki UI
   (/wiki) + Python client (ew/client.py) + skill (.claude/skills/evidence-wiki/SKILL.md) [IMPL].
2. ew/db.py: the connection resolver + store-identity guard. De facto shared Postgres connector for comms
   (comms/api.py:80-82), atlas (atlas/db.py:28-29), fabric (fabric/store.py:93-95), ludus atlas_of_worlds
   (from_postgres.py:43-46), archaeon fossils (archaeon/fossils.py:432-433), arachne (landscapes/_pg.py:31)
   [IMPL]. This is the most load-bearing thing the seat owns [INFER].
3. Durability: pew_backup.py / pew_restore_verify.py + scheduled tasks (M1 PEWBackupDaily/PEWRestoreVerifyWeekly
   now Disabled; M2 *M2 variants per MONITORS rows 18-19) [IMPL for M1 schtasks state, HIST for M2].
4. Watchdog: scripts/ew_watchdog.ps1 (+ ew_watchdog_m2.ps1 wrapper), property probe = health + one authenticated
   hybrid search, rule-10 park after 12 non-productive ticks [IMPL code; HIST runtime].
5. Batteries: integration/pew_battery.py (E0-E14), seam, closure, lineage, h0h5_refs, campaign_release_check,
   s7_rehearsal_leg, ecology_selector_check, minted_player_check [IMPL].
6. Credential tracker docs/CREDENTIAL_ROTATION_TRACKER.md (R-1..R-7) and per-agent scoped tokens (sha256 in
   config.json agent_identities) [IMPL].
7. Historical (April): LMFDB / prometheus_sci / prometheus_fire DBA duties, sigma schema application, the
   mnemosyne/queue request queue (2 rows, both HELD) [HIST] (mnemosyne/STATE.md:120-126).

## 3 Actual implementation paths

- evidence_wiki/ew/: service.py (2003 lines), store.py (509), campaign_ingest.py (640), closure.py (418), wiki.py
  (368), campaign_routes.py (340), projections.py (313), search.py (252), refs.py (212), compiler.py (193),
  client.py (177), fossil.py (174), db.py (145), evidence_pack.py (118), workspace.py (99), coords.py (93),
  frozen_surface.py (86), ontology.py (62), ids.py (62) [IMPL] (wc -l).
- evidence_wiki/migrations/001..015 (.sql, 1,364 lines total) [IMPL].
- evidence_wiki/ops/: pew_backup.py, pew_restore_verify.py, apply_migration.py, index_candidate_sets.py,
  pew_serve_m2.py + .cmd wrappers [IMPL].
- evidence_wiki/integration/ (9 battery scripts + *_results.json receipts), tests/ (20 files) [IMPL].
- Research-era artifacts: benchmarks/ (24), gold/ (19), v1b/, v2/ (~120 files of blinded arm outputs and
  scores), v3/ [IMPL] (git ls-files evidence_wiki | dirname | uniq -c).
- mnemosyne/: April-era scripts (migrate_m2.py, ingest_priority1.py, extend_battery_sweep_20260429.py) and the
  09-01 data_existence_audit [IMPL].

## 4 Architecture

[INTENT] "One knowledge substrate (Postgres schema ew), many rebuildable projections (wiki, REST, BM25,
embeddings, graph, sparse coordinates, CP/Tucker/TT). Derived content can never become evidence."
(evidence_wiki/README.md:9-11).
[IMPL] Write path: client -> REST -> store.py; every write passes an idempotency gate (store.py:41-58,
ew.write_log ON CONFLICT DO NOTHING); packet URIs matching derived markers ("evidence_wiki/derived", "/wiki/",
"/api/v1/") are refused unless kind='derived_view' (store.py:63-83); unknown vocabulary terms are refused
(store.py:34-38). Reads are logged to ew.read_log (service.py:134-142).
[IMPL] Store identity: db.py:_require_environment compares pg_control_system().system_identifier with
comms/environments.json via comms.identity.require, at pool creation and on the direct fallback
(db.py:39-55, 136-138). attest_store() runs before the service binds (db.py:101-114).
[IMPL] Search: BM25 + all-MiniLM-L6-v2 embeddings + graph traversal (search.py:3, 48); embeddings are a local
sentence-transformers model, not an LLM call.
Layers added by consumer demand, in order (migration names): evidence terms, V1 governance, V3 fossil memory,
first integration, world-provenance seam, closure V0, sealed record, session affinity, typed refs +
publication outbox, corpus ref kinds, minted players, campaign ingestion, checkpoint duplicate seqs [IMPL]
(ls migrations/).

## 5 Data stores

ew schema on the canonical store, exact count(*) on 2026-10-01 [IMPL]:
- Curated knowledge layer: experiments 79, claims 147, evidence 133, relations 54, hypotheses 21 (all status
  HYPOTHESIZED), interpretations 2, source_packets 90, vocab 79, term_mappings 308, evidence_terms 282,
  mechanism_registry 26, ontology_versions 7, agents 18, constraints 40, constraint_events 60.
- Machine-ingested layer: campaign_observations 32,938; fossil_encounters 12,935; fossil_players 6,013;
  fossil_worlds 1,000; typed_refs 2,134; publication_outbox 2,147; ref_availability_events 2,147;
  ledger_observations 807; world_session_bindings 773; ingestion_checkpoints 442; producer_events 287;
  projection_rows 2,877; coordinates 232; derived_artifacts 82; sealed_records 40.
- Operational logs: write_log 6,077; read_log 4,981; schema_migrations 2 (only 014 and 015 recorded; the
  table was introduced by 014, so 001-013 have no applied_at row) [IMPL].
Who submits (measured, SQL group-by on submitted_by/agent_id):
- ew.experiments: 79 rows, ALL created 2026-09-01..09-03; 73 have submitted_by='Mnemosyne' (the seat curated
  the gold corpus on behalf of 18 attributed agents); exactly 1 experiment was submitted by another seat
  (Ergon, 2026-09-01) and 1 by a probe ('seam-pre-probe') [IMPL].
- ew.claims: 147 rows; newest 2026-09-17 09:51 (a battery). Non-Mnemosyne, non-battery submitters: Ergon 2,
  Ludus 1, harmonia 1. creation_method: MODEL_EXTRACTED 143, HUMAN 4 [IMPL].
- ew.evidence: 133 rows; non-Mnemosyne, non-battery submitters: Ergon 3, Elenchus 2, harmonia 1 [IMPL].
- ew.write_log by agent: vivarium 1,677 (fossil/outbox deliveries, 09-05..09-17), v3-ingest-M1..M4 2,032
  (V3 benchmark, 09-02..03), batteries/tests ~1,100, Mnemosyne 432, Theophrastus 134 (09-13..14), harmonia 54,
  Ergon 25, Ludus 16, Proteus 8, Elenchus 5, Pronoia 4, James 1 [IMPL].
- Last write of any kind: 2026-09-18 14:30 -04 (release-check). Last non-watchdog read: 2026-09-18 (release-
  check); Theophrastus last read 2026-09-14; vivarium 2026-09-14 [IMPL]. Last read_log row at all: M2 watchdog
  2026-09-23 07:32 -04 [IMPL].
Conclusion supported by the counts: the curated "canonical empirical memory" (experiments/claims/evidence) is a
one-time seeded corpus from 09-01..09-03 plus battery fixtures; the fleet does not submit to it. The volume is
machine-ingested campaign/fossil telemetry via Vivarium's outbox and Mnemosyne's own campaign reader [IMPL].
Other stores the seat inventories but does not own: lmfdb (365 GB RO mirror), prometheus_sci, prometheus_fire
schemas comms, viv, archaeon, agora, sigma (sigma.claims ~1,079 by pg_stat estimate), xref (~2.1 M), zeros
(~2.0 M), charon_duckdb [IMPL for schema list; counts here are pg_stat n_live_tup estimates].
The canonical store also holds 6 fabric_* and 6 viv_dev_*/viv_*_test schemas (test/dev copies) [IMPL] -- PEW's
backup dumps the whole database, so they are inside the backup of record [INFER].

## 6 APIs/interfaces

- REST /api/v1: claims, packets, evidence, relations, experiments, tensor/{compile,factor,contract,gaps,related},
  fossil/{encounters,encounters/batch,worlds,players,seal,contract,encounters?ecology=}, constraints (+events),
  refs (+availability), campaign/{observations,summary}, projections, ingestion/*, events (outbox inbox),
  release, health, version [IMPL] (service.py @app lines; STATUS.md "routes").
- Machine-readable contracts: GET /api/v1/fossil/contract (pew.fossil.v2), closure pew.closure.v0, inbox
  pew.events.v1, frozen surface digest (docs/point_release/CAMPAIGN4_FROZEN_SURFACE.json) [IMPL].
- Python client ew/client.py and the skill; the skill says "never query the database directly -- the API is the
  contract" (SKILL.md:9-11) [INTENT]. In practice atlas/harvest/pew.py reads ew.campaign_observations directly
  over SQL in READ ONLY transactions (atlas/harvest/pew.py:1-30) [IMPL] -- [CORR] with the skill's rule.
- ew.db.connect() as a library interface used by 6+ other subsystems (section 2) [IMPL].

## 7 Scheduling model

- M1 schtasks (queried 2026-10-01): MnemosyneEvidenceWikiWatchdog Disabled, last run 2026-09-15 17:11;
  PEWBackupDaily Disabled, last run 2026-09-15 03:30 result 0; PEWRestoreVerifyWeekly Disabled, last run
  2026-09-13 04:30, LAST RESULT 1 [IMPL]. [CORR] MONITORS.md row 17 records the 2026-09-13 run's receipt as
  "OBSERVED, chain reconstructed byte-identical"; Task Scheduler reports exit 1 for that run. Not reconciled.
- M2: MnemosyneEvidenceWikiWatchdogM2 (5 min), PEWBackupDailyM2 (03:30), PEWRestoreVerifyWeeklyM2 (Sun 04:30)
  [HIST] (MONITORS.md rows 18, 19, 22). Not observable from M1.
- Service: long-running FastAPI process from a pinned detached worktree, started by the watchdog's restart path
  [HIST] (STATUS.md "serving from"). Everything else (migrations, ingestion, batteries, releases) is run by a
  Claude session by hand [IMPL from commit messages].

## 8 State machine

- Seat posture states: FROZEN (PEW_FROZEN_WAITING_FOR_INCUBATOR) with explicit reopen criteria
  (FROZEN.md:74-79) [IMPL doc].
- Claim lifecycle values present in data: OBSERVED 64, SUPPORTED 33, REFUTED 18, NOT_ESTABLISHED 13, RETRACTED 13,
  ESTABLISHED 6; write_stage SUBMITTED -> SOURCE_BOUND [IMPL]. Statuses record what the SOURCE adjudicated, not a
  PEW judgment (SKILL.md:50-52) [INTENT].
- Typed refs: availability events and software_stage / connection_evidence / scientific_outcome /
  reproduction_state columns (typed_refs, evidence) [IMPL schema]; scientific_outcome is populated on 2 of 133
  evidence rows [IMPL].
- Watchdog: ok -> nonproductive tick count -> park at 12 (park file; cleared only by hand) [IMPL code per
  MONITORS row 22; the park happened 2026-09-23, comms #542].

## 9 Communication channels

- comms (Postgres schema comms): Mnemosyne sent 21 messages (#119..#542), received 66; 14 messages addressed to
  Mnemosyne have no Mnemosyne receipt (unseen), newest #1224 range includes #563 (2026-09-24) [IMPL].
- Bodies of posted messages are duplicated into git under roles/Mnemosyne/comms_out/ (22 files) [IMPL].
- Inbound file inboxes: roles/Mnemosyne/INBOX_*.md (5 files from Archaeon, Techne, Vivarium) [IMPL].
- Operator prompts recorded verbatim under prompts/ with MANIFEST/sha256 [IMPL].

## 10 Failure recovery

- Watchdog restarts a present-but-dead service after 3 ticks, parks after 12 non-productive ticks and posts one
  comms report [INTENT/IMPL code]. Observed: the park fired 2026-09-23 08:35 ("search model not ready after
  uptime 448.4s (loading=True)") and posted #542 [IMPL]. No human or seat acted on it: no Mnemosyne receipt of
  later messages, no commit, M2 8377 still not answering [IMPL: curl to 192.168.1.191:8377/api/v1/health and
  127.0.0.1:8377 returned no body, 2026-10-01 ~09:40Z].
- Vivarium #563 (2026-09-24): "8377 is HUNG ... Port listening ... pid 17192" with M2 at 98% memory commit
  [HIST] (comms #563, receipt roles/Vivarium/receipts/INCIDENT_2026-09-24_M2_HOST_EXHAUSTION.md).
- Backup/restore: verified restore into a scratch DB comparing every table's row count (pew_restore_verify.py)
  [IMPL code]; RESTORE_VERIFIED 164/164 and 171/171 reported [REPORTED] (STATUS.md).
- Earlier recoveries: M1 watchdog had "three restart FAILED lines, no ok line, no alarm" 2026-09-11..14 [HIST]
  (MONITORS row 22 HISTORY); M1 PEW silent 14h59m before being restored on M2 [HIST] (90dc7d888).

## 11 Persistence

- Canonical: ew schema (append-only by convention; corrections via CORRECTS/SUPERSEDES relations, 6 CORRECTS
  edges exist) [IMPL counts]. Content-addressed ids + idempotency keys [IMPL store.py].
- Backups: M2 D:\PrometheusBackups\pew, 14-dump retention, ~1.1 GB per dump [HIST] (MONITORS row 18).
- Receipts committed in git: integration/*_results.json, ops/restore_verification.json, docs/point_release/*
  [IMPL]. These receipts are mutated by running the tests: the canonical checkout F:\prometheus (branch vivarium/
  v0-2026-09-05) carries uncommitted, older (2026-09-10) versions of battery_results.json, h0h5_results.json and
  restore_verification.json plus uncommitted edits to ew/refs.py, ew/service.py and the credential tracker
  (git diff --stat, 9 files, +138/-74) [IMPL]. Techne reported the same mutation class 2026-09-12 [HIST]
  (INBOX_TECHNE_TEST_MUTATES_TRACKED_JSON_2026-09-12.md).

## 12 Provenance

Strengths [IMPL]: every claim/evidence row carries packet_id, source_span, source_quote, git_commit (experiments),
machine, submitted_by, creation_method, ontology_version, revision; campaign_observations carry source_commit,
source_path, source_line, source_blob_sha, reader_version, ingest_run_id, producer_row_digest
(information_schema). schema_migrations records applied_from worktree + SHA + dirty flag.
Weaknesses [IMPL]: migration 015 was applied from a dirty tree ("f46e821e0 dirty=True", ew.schema_migrations);
143 of 147 claims are MODEL_EXTRACTED (a model wrote the canonical claim text from source packets); claims are
attributed to seats (agent_id) that did not submit them (submitted_by='Mnemosyne'); ONTOLOGY_VERSION code
constant is 2 while the registry is at 7 (MNE-19 open) [IMPL/HIST].

## 13 Resource usage

- PEW service on M2: health ~31 ms, hybrid search ~83 ms per tick [REPORTED] (STATUS.md). Embedding model cold
  start ~80 s (search.py:25 comment) [IMPL comment]. The 09-23 park reason is the model still loading after 448 s
  [IMPL comms #542] -- consistent with host memory exhaustion reported in #563 [INFER].
- Backup ~1.1 GB dump in ~234 s; restore verify ~200 s [REPORTED] (MONITORS rows 18-19).
- V3 pooled ingest 48 ev/s single / 3,633 ev/s batch [REPORTED] (local memory project_pew_frozen...).

## 14 Model/inference dependency

- Runtime service: inference-free except a local sentence-transformer for embeddings [IMPL].
- Corpus construction: MODEL_EXTRACTED claims (143/147) [IMPL]; V1/V2 annotation and scoring used model arms
  (e.g. read_log agents 'V2-T08-B-haiku') [IMPL].
- Operation: migrations, ingestion releases, repairs, contracts, comms replies, review packets are written by
  Claude sessions (all commits "Mnemosyne[m2-...]") [IMPL]. A Claude session is the only actor that responds to
  a park/alarm; when no session runs, nothing responds (09-23 -> 10-01) [IMPL].

## 15 Human dependency

Operator rulings gate: store location (MNE-D1/D2), credential rotation (R-1, R-3, R-6 OPEN), ontology version
bump (MNE-19 XL), fork DB disposition [IMPL backlog/tracker]. The operator relays and seats the seat; Mnemosyne
"was out sick" and a session stood in (2026-04-29) [HIST].

## 16 Major outputs

- The ew schema with 15 migrations and a qualified write path (idempotency, derived-view quarantine) [IMPL].
- Store-identity guard adoption (with Hermes) closing the "wrong database by name" class for ew [IMPL db.py].
- Campaign ingestion: 32,938 campaign_observations across cmp1-5, ssf-c1..3, wse-survey-v01 [IMPL].
- Research verdicts on memory itself [REPORTED]: V0 G6 TENSOR_NOT_YET_JUSTIFIED (MRR curated 0.605 vs BM25 0.078 /
  embeddings 0.062 / CP 0.023); V1 ontology QUALIFIED, METABOLIZATION_NOT_DEMONSTRATED (instrument saturated);
  V2 RETRIEVAL_ADVANTAGE_WITHOUT_DESIGN_ADVANTAGE (MODEL_SPECIFIC); V3 MARGINAL +0.111, instrument SATURATED
  (evidence_wiki/README.md:37-49; docs/METABOLIZATION_EXPERIMENT_V1.md:23-30; MEMORY_ADVANTAGE_EXPERIMENT_V2.md:50-52;
  V3_EXPERIMENT_CLOSURE.md:5-9).
- 2026-09-01 data-existence audit and legacy-store inventory (mnemosyne/STATE.md) [IMPL doc].

## 17 Known failures

- PEW down since 2026-09-23 (park) / hung 09-24, unattended through 2026-10-01 [IMPL+HIST].
- M1 PEW dormant from 2026-09-15 17:11 (last M1 watchdog read) when M1 was handed to Nestor [IMPL read_log].
- mnemosyne/migrate_m2.py:231-248 read the wrong source for kill_taxonomy and returned 0 as success, leaving
  kill.taxonomy empty [HIST] (STATE.md:146-151; kill.taxonomy n_live_tup 0 today [IMPL estimate]).
- 439 post-split write_log rows reached the M2 fork silently before the identity guard [HIST] (db.py:42-45 docstring).
- V3 pool-race defect (500s under concurrency, no partial rows) [HIST] (FROZEN.md:39-49).
- Watchdog singleton guard kept a hung service 3 h; "localhost" costs ~2 s per call on M1 [HIST] (local memory
  project_mnemosyne_base_role_adopted).
- Closure verify timeout 6 s wrote UNVERIFIED silently (fixed to 30 s + retry) [HIST] (STATUS.md repairs).
- Committed credentials in evidence_wiki/config.json (R-1 OPEN) and plaintext DB credentials quoted in
  mnemosyne/STATE.md "Connections" section (tracked file; not copied here) [IMPL].
- ecology selector population empty: 0 of 12,858 encounters carry `ecology` [REPORTED] (STATUS.md last line).

## 18 Pivots

April DBA/steward (Redis+Postgres+DuckDB stack) -> 4-month dormancy -> 09-01 Evidence Wiki research program
(V0-V3 in 2 days, tensor rejected, memory-advantage null) -> 09-02 FROZEN -> 09-03..05 consumer-driven
integration layers (fossil contract, seam, closure, lineage) -> 09-11 boundary ruling "substrate science" ->
09-16 relocation to M2 as service fronting M1 store -> 09-17 point release (campaign telemetry warehouse) ->
09-18 Campaign 6 observatory-storage contract (design only) -> silence [IMPL/HIST, SHAs above].
The PEW's center of gravity moved from "curated claims memory for agents" to "provenance-bound warehouse for
Archaeon/Vivarium campaign telemetry" [INFER from row counts + migration order].

## 19 Journals/TODOs/backlogs

- BACKLOG_H0H5.md: 56 MNE rows; 13 begin "| DONE" in the status field (grep) [IMPL]; open XL operator items
  MNE-19, MNE-D1 residue, MNE-46 (O3 cutover checklist, 7 conditions), MNE-24 (one status file) [IMPL].
- todo_20260904.md (PEW closure lane), journal/ 4 files (09-11, 09-16..18), SESSION_JOURNAL_2026{0415,0429,0901}
  [IMPL].
- STATUS.md currency 2026-09-18 14:58; claims "What is running ... PEW service ... on M2" -- false since
  2026-09-23 and not updated [CORR: STATUS.md vs comms #542/#563 and curl today].

## 20 Historical relevance to current Prometheus

- ew/db.py identity guard is live infrastructure for comms/atlas/fabric even while the PEW service is down [IMPL].
- PEW holds the only normalized, source-line-addressed copy of campaign 1-5 observations (32,938 rows), which
  Atlas indexes by pointer (atlas/harvest/pew.py; 164 atlas.source rows with pg://...ew URIs) [IMPL].
- The memory-advantage experiments are the program's only controlled tests of "does memory help a model" and
  ended in saturated instruments, not negatives [REPORTED].

## 21 Inference-dependency classification

| function | class | evidence |
|---|---|---|
| Store identity attestation | INFERENCE_FREE | ew/db.py:39-55, comms/identity.py |
| Idempotent writes / derived-view refusal | INFERENCE_FREE | ew/store.py:41-83 |
| Campaign ingestion (reader 1.x) + projections rebuild | INFERENCE_FREE | ew/campaign_ingest.py, projections.py; rebuild equal x3 [REPORTED] |
| Backup + restore verification | INFERENCE_FREE | ops/pew_backup.py, pew_restore_verify.py |
| Watchdog property probe + park | INFERENCE_FREE | scripts/ew_watchdog.ps1; comms #542 |
| Batteries (E0-E14 etc.) | INFERENCE_FREE | integration/*.py |
| Hybrid search | ASSISTED_PLAUSIBLY_DETERMINISTIC | local MiniLM embeddings + BM25 (search.py) |
| Claim extraction from packets | MODEL_MEDIATED | 143/147 claims MODEL_EXTRACTED |
| Responding to a park / outage | MODEL_MEDIATED (in practice) | no non-session responder; 8 days unattended |
| Migration authoring, contracts, consumer negotiation | OCCASIONAL_JUDGMENT | commits 8216dd3de, 0d448387e |
| Deciding whether a stored claim is true | out of scope by ruling | RESPONSIBILITIES.md:15-27 |
| Ontology governance / mechanism registry | OCCASIONAL_JUDGMENT | migrations 004; MNE-19 |

## 22 False-negative / false-positive watch

False-negative candidates:
- "Memory does not improve design" (V1 METABOLIZATION_NOT_DEMONSTRATED; V2 no design advantage; V3 MARGINAL):
  all three are recorded as instrument saturation -- every arm scored 4/4 in V1, ceiling-compressed in V2/V3
  (METABOLIZATION_EXPERIMENT_V1.md:23-30). The repo is "dense with verdict documents" so controls found priors by
  plain grep. This is a ruler defect, not evidence the idea is bad [REPORTED + INFER]. The proposed fixes (tasks
  whose priors live only in ledgers, weaker/time-boxed agents, graded scoring, non-author scorer) were declared
  and never run (METABOLIZATION_EXPERIMENT_V1.md:33-40) [IMPL doc].
- Tensor views (G6 TENSOR_NOT_YET_JUSTIFIED) were judged at 81 findings / 99 coordinates; re-evaluation trigger
  ">= 1000 coordinates" never reached (coordinates 232 today) -- scale, not idea [IMPL counts + README:44-49].
- Ecology selector "empty" because producers never write the field (0/12,858), not because the selector fails.
False-positive candidates:
- Batteries "17/17 12/12 19/19 14/14+1" are self-authored, run against the seat's own deployment, and write the
  receipts they are judged by; the S2 cheat control exists, but no outside seat re-ran them [IMPL/INFER].
- Census (docs/fleet/fleet_state.json, 2026-10-01T04:35Z) labels Mnemosyne ACTIVE from commit 2c8c81bbb, which is
  an Aporia/Odysseus-lane keepalive fix to ew/db.py on unmerged branch origin/archaeon/comms-keepalive-2026-09-30,
  not a Mnemosyne act (git merge-base --is-ancestor 2c8c81bbb bed05507a -> NOT_ANCESTOR) [IMPL] [CORR].

## Memory architecture (assignment-specific section)

Every place Prometheus stores institutional memory, as found on 2026-10-01:

| # | store | where | writer(s) | reader(s) | currency evidence |
|---|---|---|---|---|---|
| 1 | Seat files: RESPONSIBILITIES, STATUS, BACKLOG, journal/, comms_out/, prompts/ (verbatim + MANIFEST) | git, roles/<Seat>/ | each seat's Claude session | the next session of that seat; census | per-seat; e.g. Mnemosyne STATUS 09-18 [IMPL] |
| 2 | Base-role constitution: NORTH_STAR, RESPONSIBILITIES, WORKING_CONTRACT, INHERITANCE, MONITORS | git, roles/base-role/ | Archaeon/operator, seats add rows | every booting seat | MONITORS currency 09-18 line 3, last commit a797beabd 09-30 [IMPL] |
| 3 | Tracked doctrine: aporia/doctrine/critical_memories.md (6 HARD rules) | git | 2 commits, 2026-05-06/08 | referenced by 118 files under roles/ops/scripts/comms/docs (git grep -c) | unchanged since 2026-05-08 [IMPL] |
| 4 | Per-session Claude auto-memory | C:\Users\jcrai\.claude\projects\f--Prometheus\memory (M1 only) | Claude sessions on M1 | Claude sessions on M1 | 349 files: 156 feedback_, 180 project_, 9 reference_, MEMORY.md index [IMPL ls]; M2/M4 have their own, unreadable from M1 [UNK] |
| 5 | Evidence Wiki ew schema | Postgres canonical store | Mnemosyne (seeded), Vivarium outbox, campaign reader, batteries | Atlas (pointers), Theophrastus, Harmonia, Kairos (token) | last write 09-18; service down since 09-23 [IMPL] |
| 6 | Atlas schema (35 tables; 2,053 experiments) | Postgres canonical store | Atlas harvesters from git + PEW | Phase 3 designers, Aporia | see Atlas dossier [IMPL count] |
| 7 | comms schema (1,239 messages) | Postgres canonical store, via ew/db.py | every seat + automated watchdogs | seats at sync; operator | max id 1239 [IMPL] |
| 8 | agora schema (13 tables; intelligence_outputs, agent_heartbeats) | Postgres | Pronoia/portfolio loop, M4 probes | send_brief_email.py, metis_portfolio.py | email_dispatched last 2026-10-01 08:15Z [IMPL] |
| 9 | bus schema (PgRedis) | Postgres | provisioned | none | "eight entries ever" [HIST] (STATE.md:101-104) |
| 10 | Portfolio brief + docs/state.json, docs/fleet/fleet_state.json | git main (auto-commits) + GitHub Pages + email | intelligence_loop (M4), Achilles census | operator by email/phone | auto-commit e9cf5ee16 2026-10-01 04:14 -04 [IMPL] |
| 11 | Work orders / fleet queue: ops/work_orders/CURRENT.md, ops/fleet/QUEUE.json, CENSUS.json | git | Aporia/operator | seats at boot | see Aporia dossier [UNK here] |
| 12 | Experiment ledgers (jsonl, receipts, *_results.json) | git, per project | engines and seats | Atlas harvesters, PEW campaign reader | e.g. ergon/probe/ledgers (dirty in canonical checkout) [IMPL git status] |
| 13 | Host-local derived state: watchdog logs, backup_state.json, lease files (~/ananke_runs/leases) | M1/M2 disks | scripts | the same host only | unreadable cross-host [HIST] (MONITORS rows 15-22) |
| 14 | Legacy data stores: lmfdb, prometheus_sci, sigma, xref, zeros, charon_duckdb, SQLite ledgers | Postgres / files | historical pipelines | analyses | STATE.md 2026-09-01 inventory [IMPL doc] |

How they relate / overlap [IMPL unless tagged]:
- comms bodies are stored twice: comms.messages.body and roles/<Seat>/comms_out/*.md. Neither is declared
  primary.
- Experiments are recorded in at least four places: git ledgers (source), PEW campaign_observations (normalized
  copy with source_line provenance), Atlas experiment rows (index; points at PEW and git), and ew.experiments
  (79 curated, frozen 09-03). Atlas holds 2,053 experiments vs PEW's 79 curated: the curated PEW layer stopped
  growing while Atlas became the experiment index [IMPL counts] [INFER].
- Doctrine exists in three tiers that do not sync: (3) tracked HARD rules frozen since 05-08; (2) base-role
  constitution with rules synthesized from 27 role docs (249bb0f98); (4) M1-local feedback memory with 156
  feedback files, dozens dated 09-14..10-01 (e.g. feedback_git_stash_is_repo_global, feedback_timestamps_from_
  clock_only). critical_memories.md:3 itself states local feedback files "exist only on M1 and are not portable",
  i.e. the newer lessons are exactly the non-portable ones [IMPL] [CORR].
- ew/db.py is simultaneously the PEW's connector and comms's connector, so the "memory substrate" seat owns the
  plumbing of the coordination channel (comms/api.py:3, 80) [IMPL].

Drift examples, each with both sides:
1. Service location. .claude/skills/evidence-wiki/SKILL.md:13 (unchanged since c711c5bf6, 09-01) tells every
   agent "Service: http://localhost:8377 on M1"; STATUS.md (09-18) says the service runs on M2 and M1 PEW is
   DORMANT since 09-15; today neither answers [IMPL] [CORR].
2. Pin. M1 auto-memory project_mnemosyne_base_role_adopted.md says "PEW serves from ... mnemosyne-pew at
   e301547dd"; repo STATUS.md says pin e8f90c04d on M2. No M1 memory file about PEW is newer than 09-11
   (4 PEW-related files; ls) [IMPL] [CORR].
3. Liveness. STATUS.md (09-18) "What is running ... PEW service"; comms #542 (09-23) park; #563 (09-24) hung;
   no STATUS update [IMPL] [CORR].
4. Census. docs/fleet/fleet_state.json Mnemosyne = ACTIVE (from another lane's unmerged commit); PEW has had no
   write since 09-18 and no seat session since 09-18 [IMPL] [CORR].
5. Receipts. origin/main integration/battery_results.json ran_at 2026-09-17T10:02; the canonical checkout
   F:\prometheus has an uncommitted 2026-09-10 version of the same file [IMPL] [CORR].
6. Restore verify. M1 Task Scheduler last result 1 for 2026-09-13; MONITORS row 17 cites that run as a good
   receipt [IMPL] [CORR].
7. Doctrine. critical_memories.md "Last updated: 2026-05-06"; base-role and local memory carry ~5 months of later
   rules; 118 files still point agents at the May file [IMPL].
8. Mailer record. MONITORS row 37 (Hermes, 09-11) says the mailer's only record is the email itself; agora.
   intelligence_outputs held 369 email_dispatched rows at that moment (see Hermes dossier) [IMPL] [CORR].
