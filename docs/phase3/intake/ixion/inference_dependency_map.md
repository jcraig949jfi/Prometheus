# Inference-dependency map -- the current boundary (Ixion territory)

Currency: 2026-10-01T10:01Z (from date -u). Base read: origin/main bed05507a.
This maps where model inference sits TODAY in the institutional functions Ixion's 14 seats and the shared
infrastructure perform. It is a map of the present boundary, not a recommendation (charter: "Do not make
final Phase 3 recommendations. Just map the current boundary.").

Classes (charter wording):
- INFERENCE_FREE -- already inference-free: deterministic code does it now.
- ASSISTED_PLAUSIBLY_DETERMINISTIC -- inference-assisted but plausibly deterministic: a model does or triggers
  it, but the inputs are structured and the rule is statable.
- OCCASIONAL_JUDGMENT -- requires occasional model (or human) judgment.
- MODEL_MEDIATED -- fundamentally model-mediated as practiced now (not a claim that it must be).

Every row cites evidence; a class is what the evidence shows, not what is possible. "Run by hand" means
the code is deterministic but the TRIGGER is a model session or the operator -- a recurring pattern.

## 1. The charter's example functions

| function | where it happens now | class now | evidence | boundary note |
|---|---|---|---|---|
| experiment execution | Fabric script executor at pinned SHA (ubu001/ubu002 only); prometheus.toolbox compile/execute/replay; RowWriter campaigns; one-shot schtasks launchers on M1 | INFERENCE_FREE (execution); launch decision MODEL_MEDIATED | fabric.attempt 337 ubu001 + 36 ubu002 (Ixion SELECT); fabric/executors.py; ~93 disabled one-shot tasks pointing into session scratchpads | the run is code; choosing/launching it is a session act |
| result parsing | Atlas harvesters (git blobs, SQLite, Postgres -> facts with blob/line pointers); PEW campaign reader (32,938 rows, line provenance) | INFERENCE_FREE (run by hand) | atlas/harvest/*.py, common.py fact(); ew.campaign_observations; Atlas spot checks matched source in every sample | needs a hand-written adapter per engine; only 5 of 15 registered engines adapted |
| statistics | per-seat null/floor modules (42 *null* files in 15 top-level dirs); xpol floors.py; techne/lib rank_parity_null; prometheus_math | INFERENCE_FREE | build crawler file-name census; floors.json computed before any model call | duplicated per seat, not a shared library |
| scheduling | M1 schtasks (108 Prometheus-related, 104 disabled); M4 watchdog; ELSA census every 6 h; Fabric pull-queue (FIFO, no scheduler by FREEZE); fleet queue QUEUE.json hand-edited by Aporia; most seat work is session-driven | mixed: timers INFERENCE_FREE; what-runs-next MODEL_MEDIATED or OCCASIONAL_JUDGMENT | schtasks /query; QUEUE.json commits 6a7a84569, d4e47ebf5, 7d373ac02; CWO-C state machine | no code writes the queue of record |
| anomaly detection | Atlas comb (13 SQL rules, 192 signals); Achilles census flags; fleet_status.py; Alethelia 7 tri-state rules; PEW watchdog; productive_liveness | INFERENCE_FREE (detection) / MODEL_MEDIATED (response) | atlas.signal 192/192 OPEN (Ixion SELECT); comms #542 unanswered 8 days; Alethelia unhosted since 09-11 | detectors exist; nothing consumes their output without a model session |
| state updates | WORK_STATE.json (schema v1, written by sessions; 432 commits since 09-27, Ixion git count), STATUS.md, MONITORS.md, QUEUE.json/CENSUS.json | ASSISTED_PLAUSIBLY_DETERMINISTIC (written by model) | git log; Cyclops F3 future timestamps, F7 10/13 queue drift | most content derivable from git + comms + receipts |
| commit correlation | Atlas classify.py (regex over subjects/trailers; 31% of 7,419 commits unattributed); Achilles A1-A6 attribution (7% unattributed; path-majority misattribution) | INFERENCE_FREE (noisy) | classify.py:13-71 (atlas), classify.py:75-115 (achilles); 2c8c81bbb misattributed to Mnemosyne | rules are deterministic; defects are rule defects |
| provenance checks | prompt MANIFESTs (358, sha256 over LF); MWO publication blob check; Cosmos MANIFEST-gated import; PEW write-path gates; store identity guard; verify_deploy.py; D-23 workspace guard | INFERENCE_FREE | comms/manifest.py; PUBLICATIONS.md; atlas cosmos.py + tests; ew/store.py:34-83; ew/db.py:39-55 | strongest deterministic layer in the territory |
| baseline execution | xpol floors (chance, NCD, decoy, random p95) before any call; hephaestus gauntlet negative/positive/cheat controls; toolbox control.replay/cheat/ablation | INFERENCE_FREE | hephaestus/xpol_2026/floors.json; hephaestus/STATE.json ALL_PASS | per-seat; not automatic for every experiment |
| ruler execution | 1.0 trap battery (186 traps, seed 42); closure gauntlet; Achilles cheat-control tests | INFERENCE_FREE | trap_generator_extended; closure_test.py | the 1.0 comparator scores below a constant decoy (0.3925 vs 0.4032) -- execution is free, validity is not |
| search | PEW search (BM25 + local MiniLM + graph, no LLM; service down since 09-23); Atlas SQL; git grep; comms SELECTs | INFERENCE_FREE / ASSISTED (embedding) | ew/search.py:3,48; watchdog park #542 | the skill that fronts PEW still points at M1 localhost |
| hypothesis generation | Atlas proposals (XE, raids, RA-1..5, FR-1..12, none run); Aporia Deep Research queue (53/423 fired); Odysseus expeditions; Metis compose.py does NOT generate rivals | MODEL_MEDIATED | proposals/*; burn_research_tokens.py; SEASON1_RECEIPT "someone still has to name BASE_RATE_PRIORS" | the one function every crawler found irreducibly model/human today |
| experiment design | seat sessions + prereg; Metis compose.py picks the cheapest partitioning discriminator once rivals are named (5 retrospective episodes); atlas.policy fixed-weight scoring (0 outcomes ever) | OCCASIONAL_JUDGMENT (selection mechanisable, framing not) | roles/Metis/season1/specimen/compose.py + 13 tests; policy.py:23-114 | selection kernel exists and is unused |
| interpretation | seat sessions; Atlas inference harvest (7 readers + 3 synthesists + 2 verifiers + 2 external models over prose digests, 09-30); Fabric claude audit tasks (D2: 13 rounds) | MODEL_MEDIATED | roles/Atlas/inference_harvest_2026-09-30/; roles/Odysseus/fabric_pilot/d2_audit v1..v13 | harvest ran over prose because the index stopped at 09-22 |

## 2. Institutional functions specific to this territory (summary)

| function | class now | one-line evidence |
|---|---|---|
| inter-seat message transport/persistence | INFERENCE_FREE | comms 1,239 msgs, sha256 per message, receipts (Ixion SELECT) |
| message CONTENT (reports, heartbeats, orders) | MODEL_MEDIATED | 849 of 1,239 are kind=report; 124 heartbeat subjects, 14 hourly "no change" from one seat |
| liveness: presence | INFERENCE_FREE | comms.agents last_sync_at; productive_liveness.py ladder |
| liveness: heartbeat reports (CWO-B/C) | MODEL_MEDIATED | 86 heartbeat-subject msgs 09-30 04:18 .. 10-01 05:31 |
| fleet census | INFERENCE_FREE per run (registry model-built once) | achilles/census, runs 189e12502, db657a6df |
| operator brief narrative | INFERENCE_FREE by default since af9b4d9c9 (LLM only if METIS_LLM=1) | metis_portfolio.py:452-460; brief e9cf5ee16 says "no LLM in the loop" |
| email delivery + receipt | INFERENCE_FREE | send_brief_email.py; agora.intelligence_outputs email_dispatched rows |
| control-document authoring (MWO/CWO) | MODEL_MEDIATED (ChatGPT draft + operator) | MWO-0001:21; 7 orders, 16,858 words in ~40 h |
| control-document publication | ASSISTED_PLAUSIBLY_DETERMINISTIC | two-commit P/R protocol fully specified, executed by a session; CWOs skipped it |
| order adoption check | INFERENCE_FREE (check) / MODEL_MEDIATED (adoption) | fleet_status.py STALE_MWO; 22/22 WORK_STATE on MWO-0004 |
| evidence-memory claim extraction | MODEL_MEDIATED | ew.claims 143/147 MODEL_EXTRACTED |
| evidence-memory bulk ingestion | INFERENCE_FREE (run by hand) | ew.campaign_observations 32,938; fossil_encounters 12,935 |
| backup + restore verification | INFERENCE_FREE | ops/pew_backup.py, pew_restore_verify.py (M1 tasks disabled) |
| alarm RESPONSE | MODEL_MEDIATED and unscheduled | #542 (09-23) and #563 (09-24) unanswered; 14 unseen to Mnemosyne |
| index adapter authoring (new engine) | OCCASIONAL_JUDGMENT | the recurring cost behind Atlas coverage lag (8.6 days) |
| prior-art catalogue / ontology | MODEL_MEDIATED | atlas.ecosystem via surveyor subagents; 16 verification strings disagree with ref rows |
| tool/mechanism generation (forge) | MODEL_MEDIATED | 6,661 ledger rows, 2,861 api_call_failed |
| mechanism classification of generated code | INFERENCE_FREE | xpol shape.py, knockout_ablation.py |
| security audit of firewall code | MODEL_MEDIATED (self-tests deterministic) | D2 audit v1..v13 in ~2 days |
| privileged sandbox execution | INFERENCE_FREE design, NOT ENABLED | promexec, install operator-gated |
| hard gates / retirement decisions | human | MWO-0001 s7; Atalanta retirement; AGORA-01 unruled 17 days |
| operator <-> seat relay | human transport | base role s4 ASCII paste blocks; idle fleet days when operator absent (REPORTED) |

## 3. Tally over every row the six crawls classified (section 4 tables)

    crawler   INFERENCE_FR  ASSISTED_PLA  OCCASIONAL_J  MODEL_MEDIAT  other
    atlas     11            3             1             6             0
    fleet     17            3             1             5             0
    memory    14            1             4             6             0
    coord     7             5             4             6             1
    build     18            2             2             6             0
    hist      13            2             2             3             0
    TOTAL     80            16            14            32            1

    Rule: a row counts under the FIRST class named in its class cell; a cell naming none counts as other.

The tally counts rows, not cost: no mechanism in the territory records tokens, session minutes or dollars
per seat or per function (fleet crawler G; comms.agents holds only a self-declared model string). The
inference cost of each MODEL_MEDIATED row is UNKNOWN.

## 4. Full per-crawler tables (as written by the sub-crawlers; Ixion corrections marked)

Ixion correction applied: the memory crawler's row "Operator brief prose ... MODEL_MEDIATED" is wrong for the
default path; see section 2 (metis_portfolio.py:452-460; e9cf5ee16). The row is kept below with a [CORR] marker.

### atlas (21 rows)

| institutional function | current mechanism | class | evidence | notes |
|---|---|---|---|---|
| experiment/attempt record keeping | versioned Python harvesters over git blobs, SQLite (ro+immutable), Postgres SELECT | INFERENCE_FREE | atlas/harvest/*.py; harvest_run 136 rows | needs a hand-written adapter per engine (only 5 engines adapted) |
| result parsing (numbers) | flatten json receipts into facts with blob/line pointers | INFERENCE_FREE | common.py fact(); spot checks C.jsonl@24, P-I04 RESULT matched |  |
| disposition classification | regex ladder status_class/science_class | INFERENCE_FREE | classify.py:106-186 | semantically lossy: COMPLETE/PASS/completed -> POSITIVE; machine candidate preferred over author RECORD verdict |
| commit correlation (seat/lane/ids) | regex over subjects/trailers | INFERENCE_FREE | classify.py:13-71; git_commit 7,419 | 2,297 (31%) commits no seat |
| host / machine attribution | alias/IP/path/tag lookup in registry | INFERENCE_FREE | classify.py:80-101 | registry hand-curated |
| provenance checks | harvest_run per row; MANIFEST sha256 gate for exports | INFERENCE_FREE | db.py:107-146; cosmos.py | fail-closed on mismatch |
| identity collision detection | SQL over experiments/facts/field_conflict | INFERENCE_FREE | report.py:38-64 | field_conflict never fired (0 rows) |
| anomaly / weak-signal detection | 13 SQL comb rules | INFERENCE_FREE | comb.py:27-161 | 192 OPEN signals, none consumed; R03/R10 loose |
| index freshness / coverage lag | max(commit) - max(modelled activity) | INFERENCE_FREE | report.py:286-295; policy.py:146-158 | metric uses newest commit anywhere, not per area |
| loss tracking of host-local evidence | stat re-check, present=false + fact | INFERENCE_FREE | local_files.py:24-30 | M2 pass only once (09-19) |
| scheduling of index passes | operator instruction; session /loop (parked) | MODEL_MEDIATED | MONITORS.md:87-88; harvest_run dates | no schtasks/cron; trivially schedulable code |
| writing a new engine adapter | Atlas session writes harvester + migration + tests | OCCASIONAL_JUDGMENT | MODEL.md s7; cosmos.py written 09-26 | the recurring cost behind coverage lag |
| prior-art catalogue | six web-survey subagents -> JSONL -> loader | MODEL_MEDIATED | journal 2026-09-19; catalog/README.md | 16 verification strings disagree with ref rows; Artemis disputes 2 |
| ontology (propositions, confidence, blind spots) | Atlas session authors JSONL ledgers | MODEL_MEDIATED | theory/*.jsonl; journal 2026-09-24 | some bases cite the operator as source |
| primitive detection | model-written axis rules applied by code; experiment rows inherited per campaign | ASSISTED_PLAUSIBLY_DETERMINISTIC | theory.py:69-115 | 5 primitives UNMEASURED; null by construction for experiments |
| experiment prioritisation (scoring) | fixed weights over model-written proposal fields | ASSISTED_PLAUSIBLY_DETERMINISTIC | policy.py:23-114 | 0 outcomes ever; weights never refit |
| portfolio directives | SQL + constant-text directives | INFERENCE_FREE (content partly hard-coded) | policy.py:117-262 | ruled REPORTS ONLY 09-25 |
| hypothesis generation / proposals | Atlas session (XE, raid A-I, RA-1..5, FR-1..12) | MODEL_MEDIATED | proposals/*; ATLAS_OPERATOR_FRONTIER.md | none run |
| cross-engine interpretation / synthesis | Claude subagents over digests + 2 verifiers + NIM cross-family check | MODEL_MEDIATED | inference_harvest_2026-09-30/ | synthesis did not run over index rows |
| buried-signal extraction | subagent digests, ranked by Atlas | MODEL_MEDIATED | ATLAS_BURIED_SIGNALS_AND_RESIDUALS.md | comb R01/R06 are the deterministic analogue |
| M2-local evidence gather | Atlas-M2 session runs local_files/frontier_runs_m2 | ASSISTED_PLAUSIBLY_DETERMINISTIC | harvest_run seat=Atlas-M2 x8 | the code is deterministic; the trigger and de-dup decisions are not |

### fleet (26 rows)

| institutional function | current mechanism | class | evidence | notes |
|---|---|---|---|---|
| fleet roster discovery | Achilles: roles/ dirs on all origin refs + registry | INFERENCE_FREE | achilles/census/sources.py:22-45; build.py:440-466 | registry kinds/aliases were model-authored once |
| seat role description | Achilles registry declared_role/observed_role | MODEL_MEDIATED (one-time) then static | registry/SCHEMA.md; journal 2026-09-30:94-98 | drift check (ACHILLES-10) not built |
| seat activity / liveness | Achilles S0-S6 rules over commits, comms, ew | INFERENCE_FREE | classify.py:221-328 | misattribution and STATUS-line parse defects found (Mnemosyne, Atlas) |
| seat liveness (legacy) | portfolio_monitor EXPECTED_AGENTS + agora heartbeats | INFERENCE_FREE (wrong model) | scripts/portfolio_monitor.py:85; docs/state.json | reports 0/48 alive from May roster |
| presence | comms.agents/agent_instances sync timestamps | INFERENCE_FREE | comms/schema.sql:44-99; comms/api.py:404-441 | presence written by model sessions calling comms |
| commit attribution to seats | Achilles A1-A6 | INFERENCE_FREE | classify.py:75-115 | 7% unattributed [HIST] |
| experiment event detection | Achilles verdict-word regex | INFERENCE_FREE (noisy) | classify.py:122-153 | 62/24 h includes rulings, harvest deliverables |
| last task per seat | Achilles newest-of QUEUE/CENSUS/prompt/delegation | INFERENCE_FREE | build.py:261-291 | the source ledgers (QUEUE.json, CENSUS.json) are hand-written by Aporia |
| work dispatch / queue of record | ops/fleet/QUEUE.json edited by Aporia sessions | MODEL_MEDIATED | 6a7a84569, 7d373ac02 | no code writes QUEUE.json |
| stale-state detection | fleet_status.py; Achilles flags | INFERENCE_FREE | ops/fleet/fleet_status.py; classify.py:296-324 | fleet_status.py: no run evidence |
| conflict detection (declared states, hosts, ownership) | Achilles flags/anomalies | INFERENCE_FREE | classify.py:243-249; build.py:585-623 | resolution is not automated (freshest wins) |
| anomaly routing to owners | Achilles seat posts comms reports | OCCASIONAL_JUDGMENT | comms #1224-#1227; BACKLOG ACHILLES-06 | code only posts on census failure/park |
| heartbeats / status reports | seats post comms "heartbeat" reports per CWO-30C s13 | MODEL_MEDIATED | 124 heartbeat-subject messages total, 66 on 09-30 (query) | content mostly derivable from WORK_STATE + git |
| work-order publication | operator text; Aporia two-commit publish + broadcast; Cyclops register | MODEL_MEDIATED (publication steps ASSISTED_PLAUSIBLY_DETERMINISTIC) | ops/work_orders/PUBLICATIONS.md | sha256 verification is mechanical |
| order adoption by seats | each seat reads CURRENT.md and updates WORK_STATE mwo_id | MODEL_MEDIATED | fleet_status.py STALE_MWO flag exists to check it | adoption check is deterministic |
| standing-loop registry | MONITORS.md hand rows + self-test | ASSISTED_PLAUSIBLY_DETERMINISTIC | roles/base-role/MONITORS.md; archaeon/tests/test_base_role.py:140-222 | row states drift from DB facts (portfolio producer) |
| scheduled-task registration check | test_every_enabled_prometheus_scheduled_task... | INFERENCE_FREE | archaeon/tests/test_base_role.py:200-222 | name regex misses FoundryAPI, nestor_z80atlas |
| status email | send_brief_email.py (Gmail SMTP) | INFERENCE_FREE | scripts/send_brief_email.py:555-680; 485 email_dispatched rows | creds on M4 only |
| portfolio brief narrative | metis_portfolio deterministic default; LLM only if METIS_LLM=1 | INFERENCE_FREE (was MODEL_MEDIATED) | scripts/metis_portfolio.py:452-458; af9b4d9c9 | pivot after CoT leaks into email |
| fleet web page | Achilles render + pages.yml | INFERENCE_FREE | achilles/census/render.py; .github/workflows/pages.yml | client-side freshness |
| mailer delivery verification | census reads email_dispatched receipts | INFERENCE_FREE | sources.py:273-280; build.py:625-637 | closed loop verified 2026-10-01 |
| host resource telemetry | machine_probe -> agora.machine_probes | INFERENCE_FREE | scripts/machine_probe.py; DB | only M4 alive since 2026-05-30 |
| compute leases | ~/ananke_runs/leases/*.json + comms record; agora.gpu_reservations | ASSISTED_PLAUSIBLY_DETERMINISTIC | memory lease_convention; gpu_reservations 5 rows | convention, partly unrecorded |
| experiment launch | one-shot schtasks launchers | ASSISTED_PLAUSIBLY_DETERMINISTIC | primordial/ops/schtask_launch.py; M1 schtasks list | launcher cmd files live in session scratchpads |
| canonical-checkout protection | archaeon/workspace.py; achilles run.py:45-52 | INFERENCE_FREE | archaeon/workspace.py:35-103 |  |
| truthful status report | Alethelia v0.1 (value + query per field) | INFERENCE_FREE | agents/alethelia/alethelia.py; stations/REPORT_latest.md | no host since 09-11 |

### memory (25 rows)

| institutional function | current mechanism | class | evidence | notes |
|---|---|---|---|---|
| Evidence storage (claims/evidence/relations) | ew schema via REST + store.py gates | INFERENCE_FREE | evidence_wiki/ew/store.py:41-83 | storage is deterministic; what gets stored is not (next row) |
| Claim extraction from a source packet | model reads packet, writes canonical claim text | MODEL_MEDIATED | ew.claims creation_method MODEL_EXTRACTED 143/147 | 4 HUMAN rows; no deterministic extractor exists |
| Submitting results to the evidence memory | seat Claude session calls client (skill) | MODEL_MEDIATED (and largely not done) | 1 of 79 experiments submitted by a non-Mnemosyne seat | fleet does not submit; curated layer frozen at 09-03 |
| Ingesting campaign results | campaign reader 1.x over committed ledgers | INFERENCE_FREE (run by hand) | ew/campaign_ingest.py; 32,938 rows; 2nd pass 0 new [REPORTED] | trigger is a session; could be scheduled [INFER] |
| Result-row provenance (commit/path/line/blob sha) | columns filled by reader | INFERENCE_FREE | ew.campaign_observations columns | strong |
| Derived views / projections | projections.py rebuild with digest equality | INFERENCE_FREE | ew/projections.py; rebuild equal x3 [REPORTED] |  |
| Search / "has this been tested?" | BM25 + local MiniLM embeddings + graph | ASSISTED_PLAUSIBLY_DETERMINISTIC | ew/search.py:3,48 | no LLM; model load is the liveness weak point (#542) |
| Store identity / wrong-database prevention | system_identifier vs environments.json | INFERENCE_FREE | comms/identity.py; ew/db.py:39-55 | fail-closed; used by comms, atlas, fabric |
| Backup + restore qualification | pg_dump + scratch restore + per-table compare | INFERENCE_FREE | ops/pew_backup.py, pew_restore_verify.py | M1 tasks disabled; M2 unobservable from M1 |
| Liveness / productivity monitoring of PEW | watchdog property probe + rule-10 park + comms post | INFERENCE_FREE | scripts/ew_watchdog.ps1; comms #542 | detection deterministic |
| Responding to a monitor alarm | a Claude session of the owning seat must boot and read comms | MODEL_MEDIATED | #542 (09-23) unanswered to 10-01; 14 unseen messages for Mnemosyne | the escalation path terminates in inference that is not scheduled |
| Acceptance testing of the substrate | integration batteries + receipts | INFERENCE_FREE (run by hand) | integration/*.py, *_results.json | receipts rewritten by runs; self-authored |
| Migration authoring + schema contracts | Claude session writes SQL + docs | OCCASIONAL_JUDGMENT | migrations 011-015 commits |  |
| Ontology / vocabulary governance | mechanism registry + vocab refusal | OCCASIONAL_JUDGMENT | migrations 004; MNE-19 (code ontology 2 vs registry 7) |  |
| Credential issuance + tracking | sha256 in config, tracker doc | OCCASIONAL_JUDGMENT (human for rotation) | CREDENTIAL_ROTATION_TRACKER.md R-1..R-7 | R-1, R-3, R-6 OPEN on operator |
| Doctrine memory propagation | tracked doctrine file + base-role + M1-local auto-memory | MODEL_MEDIATED | critical_memories.md unchanged since 05-08; 156 local feedback files | lessons accrue in the non-portable tier |
| Status self-reporting (STATUS.md, MONITORS rows) | hand-written by sessions | MODEL_MEDIATED | Mnemosyne STATUS 09-18 stale; MONITORS rows 37-38 stale | no deterministic refresher |
| Fleet activity classification of these seats | Achilles census (deterministic rules) | INFERENCE_FREE | docs/fleet/fleet_state.json | misattributed 2c8c81bbb to Mnemosyne (path-majority) |
| State snapshot for the operator | portfolio_monitor.py | INFERENCE_FREE | scripts/intelligence_loop.py:443 |  |
| Operator brief prose | metis_portfolio.py LLM cascade (NVIDIA->Cerebras->Groq) every ~4 h | [CORR: INFERENCE_FREE by default; was MODEL_MEDIATED before af9b4d9c9] MODEL_MEDIATED (deterministic fallback exists) | scripts/metis_portfolio.py:6-7, 525-556, 777 | fallback added because the cascade leaked scratchpad (line 454) |
| Delivery to operator | SMTP + agora event row | INFERENCE_FREE | send_brief_email.py:643-676 | no payload hash / no-op detection |
| Staleness flag on delivered content | census block only | INFERENCE_FREE | send_brief_email.py:447-480 | brief itself has none |
| Duplicate-failure convergence | sha256 signature over at-failure observables; one incident file per signature | INFERENCE_FREE | roles/Hermes/science/convergence/; incidents/c84e26826cc12217.md | 2/5 historical cases converge [REPORTED] |
| Archaeology of retired seats/queues | session reads git + docs, classifies rows | OCCASIONAL_JUDGMENT | ARCHAEOLOGY_2026-09-11.md | contained a factual error caught by a peer |
| Memory-advantage evaluation | model arms + rubric scoring | MODEL_MEDIATED | evidence_wiki/v2, v3; read_log V2-T*-haiku | saturated instruments |

### coord (23 rows)

| institutional function | current mechanism | class | evidence | notes |
|---|---|---|---|---|
| inter-seat message transport + persistence | comms Postgres queue, sha256 per message, receipts | INFERENCE_FREE | comms/api.py; 1,239 rows | pull-only: a seat sees mail only when its session runs `comms sync` |
| liveness / presence | comms.agents last_sync_at -> `comms who`; agora.agent_heartbeats (M4 daemons) | INFERENCE_FREE | D-25 (8bb162a77); comms/__main__.py:89 | Cyclops F4: presence understates live seats; posting without syncing is invisible |
| liveness by heartbeat message (CWO-B/C) | model sessions post HEARTBEAT reports to Aporia | MODEL_MEDIATED | 86 heartbeat-subject msgs since 09-30 04:18; Bellerophon 14 "no change" | each beat is a model turn; content is often unchanged state |
| stale-state detection | ops/fleet/fleet_status.py | INFERENCE_FREE | fleet_status.py:59-72 + test | not scheduled; no FUTURE_UPDATE / undeclared-run checks |
| reported-vs-actual reconciliation | Cyclops audit, by hand | ASSISTED_PLAUSIBLY_DETERMINISTIC | audits/2026-09-30_observability.md F1-F5 | every finding is a join of git, comms, fabric lease, process table |
| control-document publication | two-commit P/R protocol executed by a session | ASSISTED_PLAUSIBLY_DETERMINISTIC | mwo0002_revision s2; PUBLICATIONS.md | fully specified; no script; CWO rows degraded |
| control-document authoring | ChatGPT draft + operator approval (+ seat candidate) | MODEL_MEDIATED | MWO-0001:21; mwo0003 verbatim :5 | 7 orders, 16,858 words, 09-28..09-30 |
| MWO discovery at boot | base-role boot step 1 reads CURRENT.md (since 17e25e67b) | INFERENCE_FREE (once read) | 17e25e67b; FP-001 | before 09-29 discovery depended on operator prompts / harness memory |
| adoption accounting | WORK_STATE.json mwo_id per seat | ASSISTED_PLAUSIBLY_DETERMINISTIC | 22 WORK_STATE files all MWO-0004 at bed05507a | no schema validator; free-text state values |
| work selection inside a seat | base-role 2a B ordering rules, then model | OCCASIONAL_JUDGMENT | RESPONSIBILITIES.md 2a B | rules 1-4 are partly mechanical (deterministic tie-break) |
| non-hard pending decisions | MWO-0004 R1 immediate default | OCCASIONAL_JUDGMENT | CURRENT.md R1 | "smallest reversible action" still requires judgment |
| hard gates | operator | MODEL_MEDIATED (human) | MWO-0001 s7 six gates | 6 of 22 WORK_STATEs list an operator decision at bed05507a |
| fleet queue CURRENT/NEXT/RESERVE | hand-edited QUEUE.json by Aporia | OCCASIONAL_JUDGMENT | QUEUE.json; Cyclops F7 (10/13 drift) | snapshot, not live |
| dispatch of bounded tasks | Aporia comms delegations | OCCASIONAL_JUDGMENT | comms #1136-#1150 | e.g. reviewer assignment C4 |
| blind-lane contamination guard | prepost_check.py + DO_NOT_BRIEF.txt | INFERENCE_FREE | probes/prepost_check.py, test | refuses broadcasts; bypassed for MWO broadcast |
| release-token / launch guard | exact-token check in C1b driver | INFERENCE_FREE | RULINGS.md 06:50Z | encoded a steward authority that was later retired |
| steward rulings on prereg details | Aporia/Cyclops sessions | MODEL_MEDIATED | 18 ruling-kind msgs from Aporia (4) + Cyclops (14) overall; RULINGS.md | retired 09-26 |
| liveness registry of standing loops | roles/base-role/MONITORS.md (hand-maintained) | ASSISTED_PLAUSIBLY_DETERMINISTIC | 75 commits | self-test checks schtasks rows per base role (not run by this crawler) |
| decisions register | archaeon/docs/expansion/DECISIONS.md | (stale) | last change 10b75cbb0 2026-09-11 | later rulings live in prompts/, RULINGS.md, MWO/CWO texts |
| literature acquisition | Gemini Deep Research scripts | MODEL_MEDIATED (external) | 53/423 fired | selection+firing scriptable; reading is model work |
| fleet census | Aporia CENSUS.json (by hand) -> Achilles census (every 6 h) | ASSISTED_PLAUSIBLY_DETERMINISTIC | 7cb91eaf9; 189e12502 | depth in Achilles crawler |
| ack / receipt of orders | MWO-0001 s2.7: no ACK messages; adoption via WORK_STATE | INFERENCE_FREE (by rule) | MWO-0001:56 | 79 ack-kind comms messages overall, 3 on 09-30 |
| operator <-> seat relay | operator pastes ASCII blocks by phone | MODEL_MEDIATED (human transport) | base role s4 | every cross-model review passes through the operator |

### build (28 rows)

| institutional function | current mechanism | class | evidence | notes |
|---|---|---|---|---|
| experiment execution (frozen scripts) | fabric script executor at pinned SHA, no shell | INFERENCE_FREE | fabric/executors.py; 123 script tasks in fabric.tasks | 28 failed, mostly worktree/infra errors |
| experiment execution (worlds/IR) | prometheus.toolbox compile/execute/replay | INFERENCE_FREE | prometheus/toolbox/README.md; 231 test fns | 21 external importing files |
| task queueing, claiming, leasing, requeue | fabric store (Postgres, SKIP LOCKED, fencing, TTL) | INFERENCE_FREE | fabric/store.py, worker.py; 4,196 heartbeat events | pull model, FIFO, no scheduler by FREEZE |
| resource leases (CPU/GPU) | fabric leases table + lease_compat frontends | INFERENCE_FREE | fabric/lease_compat.py 8370083ae; 40 leases | earlier: host files, comms LEASE records, Redis, agora.gpu_reservations |
| artifact capture + env receipt | fabric worker runtime upload | INFERENCE_FREE | fabric/README.md s4 | 1,697 artifact_added events |
| deployment verification | verify_deploy.py / preflight / qualify (SFE) | INFERENCE_FREE | deploy/verify_deploy.py docstring | written because the deployment tree is a shared checkout |
| ruler execution (reasoning battery) | trap_generator_extended seed=42, 186 traps | INFERENCE_FREE | hephaestus/xpol_2026/floors.json | ruler sits below a constant-index decoy |
| baselines/floors | floors.py (chance, NCD, decoy, random p95) | INFERENCE_FREE | floors.json computed 2026-09-19T12:01Z before any model call |  |
| mechanism classification of generated code | shape.py AST/regex fingerprint; knockout_ablation.py | INFERENCE_FREE | xpol_2026/shape.py; agents/hephaestus/src/knockout_ablation.py | replaces reading tools by hand |
| substrate-capability classification | closure gauntlet (A0/A1/A2/B) | INFERENCE_FREE | hephaestus/src/closure_test.py; controls ALL_PASS | specs per wall hand-written (OCCASIONAL_JUDGMENT) |
| work-item routing (packets) | refine.py rules on executed evidence | INFERENCE_FREE | hephaestus/src/refine.py; README rules | never exercised through a full cycle |
| freshness/liveness of a job | STATE.json last_input/last_success + NO-OP reason | INFERENCE_FREE | hephaestus/STATE.json | written per job run, not by a monitor |
| handoff/brief generation | handoff.py regenerates HEPHAESTUS_HANDOFF.txt | INFERENCE_FREE | hephaestus/src/handoff.py | contrasts with hand-written STATUS.md |
| seat durable state | WORK_STATE.json (prometheus.work_state.v1) | ASSISTED_PLAUSIBLY_DETERMINISTIC | roles/Odysseus/WORK_STATE.json | schema'd but authored by the model each commit |
| cross-host reproducibility check | TH-006 pack; brain `check` | INFERENCE_FREE | roles/Odysseus/th006; odysseus/brain |  |
| claim verification of other seats' reports | fabric claude Tasks (S2) | ASSISTED_PLAUSIBLY_DETERMINISTIC | S2 RESULT s3: claims were line/hash/count checks | C3-C6 reducible to grep/hash |
| leak/canary detection | canary scan over artifacts | INFERENCE_FREE | S3 CANARY_SCAN.json (0/80) |  |
| security/firewall code audit | claude audit Tasks, 13 rounds | MODEL_MEDIATED | roles/Odysseus/fabric_pilot/d2_audit (v1..v13) | self-tests are deterministic; verdict is model |
| blind quality scoring | 2 scorer Tasks per item, frozen rubric | MODEL_MEDIATED | S3 RESULT scoring section | rubric ceiling hit (Harmonia #1038) |
| privileged sandbox execution | promexec broker | INFERENCE_FREE | fabric/promexec/broker.py | NOT ENABLED; install operator-gated |
| model calls (all seats) | prometheus_llm complete/council | MODEL_MEDIATED | prometheus_llm/README.md | single choke point; 8 external importers |
| tool/mechanism generation | Nous + CODE_GEN (1.0); apprentice; Master Smith | MODEL_MEDIATED | ledger.jsonl; apprentice.py | apprentice refuses premium targets |
| novelty / "gravity" judgment | proposed second-model assay | MODEL_MEDIATED | HEPHAESTUS_2_0_GRAVITY_PILOT.md | proposal only |
| exploration (foreign mechanisms) | Odysseus expeditions, external raids | MODEL_MEDIATED | expedition/YIELD.md | yield ledger classifies fates deterministically after the fact |
| infrastructure defect triage | DEFECTS.md rows by the seat | OCCASIONAL_JUDGMENT | roles/Odysseus/fabric_pilot/DEFECTS.md (23 rows) | many detectable from fabric.events (requeued, worktree add failed) |
| component disposition | DISPOSITION_LEDGER with E-grades | OCCASIONAL_JUDGMENT | roles/Hephaestus/DISPOSITION_LEDGER.md |  |
| canonical-checkout guard | archaeon.workspace + 12 other workspace modules | INFERENCE_FREE | 13 modules (8 import archaeon.workspace) | duplicated implementations |
| row persistence during runs | primordial RowWriter commit-on-write | INFERENCE_FREE | primordial/fabric/rows.py | git races documented in memory feedback |

### hist (20 rows)

| institutional function | current mechanism | class | evidence | notes |
|---|---|---|---|---|
| Multi-stage pipeline orchestration (Era 1) | pronoia.py serial subprocess chain gated on date-named files | INFERENCE_FREE | `git show 3b3c74bc0^:pronoia.py` _run_cycle | Retired; coordination itself never needed a model |
| Literature/frontier triage | Eos+Aletheia+Skopos+Metis LLM cascade (Nemotron/Cerebras/Groq) | MODEL_MEDIATED | agents/metis/src/metis.py:171-212; agents/pronoia/README.md steps 1-4 | Retired with chain; never measured for value |
| Novelty/no-op detection downstream of an LLM | sha256 of normalised "Act" section (metis.py _detect_staleness) | INFERENCE_FREE but insufficient | metis.py:281-308; 6/8 briefs repeat 3 items byte-distinct | Hash checks are defeated by rewording; needs semantic or structural key |
| Pipeline health audit (Era 1) | regex over captured stdout | INFERENCE_FREE (invalid ruler) | pronoia.py run_audit; 0/37 HEALTHY | Graded self-reports, not properties |
| Fleet state snapshot | portfolio_monitor.py -> docs/state.json | INFERENCE_FREE | scripts/portfolio_monitor.py | Live on M4 |
| Fleet narrative brief | metis_portfolio.py deterministic template; LLM only if METIS_LLM=1 | ASSISTED_PLAUSIBLY_DETERMINISTIC (already realised deterministic) | scripts/metis_portfolio.py:449-458; af9b4d9c9 | Explicit migration after LLM confabulation and CoT leaks |
| LLM output sanitation | marker-count CoT leak detector + strip | INFERENCE_FREE | metis_portfolio.py:522-534, 782 | Guard around model output |
| Alive-vs-working liveness | productive_liveness.derive_health (pure, timestamps only) wired into heartbeat | INFERENCE_FREE | roles/Pronoia/science/productive_liveness.py; agora Pronoia health='productive' | Only 3/36 heartbeat rows carry work state |
| Truthful fleet report with anomaly rules | alethelia.py query-carrying fields + 7 tri-state rules | INFERENCE_FREE | agents/alethelia/alethelia.py:314-388 | No host; last run 2026-09-11 |
| Loop no-op bounding + park | rule 10 / null_bound.py | INFERENCE_FREE | roles/base-role/RESPONSIBILITIES.md:135-157 | Adoption status per loop UNDECLARED for many rows [HIST] |
| Loop-risk classification (C1 guessed input, C2 unbounded, C3 no recipient) | manual census over MONITORS rows | ASSISTED_PLAUSIBLY_DETERMINISTIC | roles/Atalanta/CENSUS_LOOP_RISK_2026-09-11.md | C3 parsed from registry free text |
| Producer discovery for a consumer | consumer-authored literal paths (Atalanta) | INFERENCE_FREE but unbound | agents/atalanta/daemon.py:63-67 | D-28 producer declaration unruled |
| Primitive/composite counting in evolved organisms | Counter over primitive_sequence | INFERENCE_FREE | apollo/scripts/inspect_population.py:69-75 [HIST via SALVAGE]; daemon.py | Never executed by Atalanta |
| Naming a candidate primitive (signature, composition rules) | Type-E Deep Research prompt | MODEL_MEDIATED | agents/atalanta/CHARTER.md template | Never dispatched |
| Experiment selection under correlated evidence | Metis compose.py: dependence grouping, vetoes, cheapest discriminator | INFERENCE_FREE | roles/Metis/season1/specimen/compose.py | Retrospective only (5 episodes) |
| Encoding historical evidence into bundles (rules_out, upstream tokens) | single author by hand | OCCASIONAL_JUDGMENT | roles/Metis/season1/FAILURE_LEDGER.md item 4 | Untested inter-encoder agreement (F4) |
| Naming rival explanations (e.g. base-rate priors) | human/model imagination | MODEL_MEDIATED | SEASON1_RECEIPT "Someone still has to name BASE_RATE_PRIORS" | The irreducible fork the specimen does not cover |
| Publication of reports | git add/commit/push from a loop | INFERENCE_FREE | pronoia.py publish_reports; intelligence_loop push_dashboard_to_main | Era-1 version swallowed git errors and pushed from canonical checkout |
| Retirement/seat-existence decisions | operator rulings on seat recommendations | OCCASIONAL_JUDGMENT | Atalanta RETIREMENT; Metis OPERATOR_RULING; PRON-01 | Census then maps lifecycle text to labels deterministically |
| Lifecycle labelling of seats | Achilles census rule mapping (e.g. CLOSED -> RETIRED) | INFERENCE_FREE | roles/Achilles/census/registry/seats_part3.json (Metis lifecycle_marker CLOSED) | Can over-claim retirement |
