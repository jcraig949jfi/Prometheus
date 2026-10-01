# Seat dossier: Aporia

Crawler label: coord (Ixion Phase 3 sub-crawler; seats Aporia, Cyclops, Agora)
Date: 2026-10-01 (date -u at start: Thu Oct 1 09:36:13 UTC 2026)
Base SHA read: bed05507a (origin/main, worktree F:/Prometheus-worktrees/ixion-phase3)

Fully read: roles/Aporia/RESPONSIBILITIES.md, STATUS.md, WORK_STATE.json, MIGRATION_REPORT_MWO-0002.json,
probes/FP-001_RESULT.json, journal/2026-09-29.md, journal/2026-09-30.md, every operator prompt
under roles/Aporia/prompts/ dated 2026-09-25..2026-09-30 (verbatim files, first 3.5-4 KB of the
long ones), ops/work_orders/PUBLICATIONS.md, ops/fleet/fleet_status.py + test, the git log of
roles/Aporia (119 commits, all subjects), programs/selective_irreversibility/RULINGS.md and README.md,
aporia/scripts/burn_research_tokens.py header, roles/Aporia/harvest/2026-09-30/PROMETHEUS_PATHOLOGICAL_ATTRACTORS.md s P5.
Sampled: aporia/ (1,851 files per brief; 962 commits) by top-level directory file/commit counts and
last-commit dates; aporia/doctrine/ listing + critical_memories.md head; aporia/docs/ listing;
PROGRAM_SUMMARY_2026-08-24.md head; P145-P151 commit subjects; the Deep Research queue/fired logs
(counted); roles/Aporia/history/RESPONSIBILITIES_2026-04_void_detector.md head; MWO/CWO texts by section.
NOT read: aporia/docs/frontier_campaign_69 dossiers (100+), aporia/search, paradigms, catalog_attacks,
meta/, iq/, lot/ bodies; journal 2026-09-11/23/25/26 bodies (subjects only via git log);
harvest files other than P5; the SI memo bodies; Aporia's April/May session journals.
Comms: read-only SELECTs on schema comms (prometheus_fire on M1) via comms.api.connect inside
SET TRANSACTION READ ONLY.

## 1 Charter and role history

Aporia has had at least nine distinct roles. Each pivot was an operator directive; none was self-assigned.

    2026-04-15  research seat: open-question triage (23A/17B/450C) and test specs     [HIST] c03a17de3
    2026-04-17  "Void Detector & Discovery Engine": five void-detection strategies
                V1-V5, "overseer" of the engineering seats                          [INTENT] 4b2790e5b;
                                                                                    history file roles/Aporia/history/RESPONSIBILITIES_2026-04_void_detector.md
    2026-05-11  owner of the daily Gemini Deep Research dispatch (20 reports/day,
                "use-or-lose")                                                       [IMPL] 4c6131fe9 aporia/scripts/
    2026-08-xx  standing loop of numbered passes/cycles (P1xx, CYCLE 138-156);
                loop stopped 2026-08-24                                              [HIST] aporia/docs/PROGRAM_SUMMARY_2026-08-24.md:3
    2026-08-26  mutable-language-of-thought research line                            [INTENT] 72583930f
    2026-09-11  base-role adoption; seat rewritten (APO-25); temperament clause
                verbatim; DISSENT_LEDGER opened                                      [IMPL] 7e2dbe0a9, 4305c1de9
    2026-09-25  Selective Irreversibility (SI) PEER STEWARD on M1, paired with
                Cyclops on M2                                                        [IMPL] 04379db69; directive sha256 f0dd0599... at 608b672d5
    2026-09-26  steward direction FROZEN (13:05Z ruling), all sign-off released
                (13:20Z ruling)                                                      [IMPL] b62b35eb2, 4f5d9bac8
    2026-09-29  MWO author + designated PUBLISHER (MWO-0002/3/4), each "for this
                publication only", then HOLD/advisory                               [IMPL] 7c84a44b4, ed71a292d, 89512068f, 624a686ea, 25a486d44
    2026-09-30  CWO "fleet scheduler, backlog maintainer and blocker clearer";
                same day narrowed to "completion coordinator" (CWO-B) and
                "dispatcher" (CWO-C)                                                [IMPL] 6a7a84569, d4e47ebf5, 7d373ac02
    2026-09-30  bounded "inference harvest" (wrong-question attack) until
                2026-10-01 05:00 ET                                                  [IMPL] 66fc8b1d0, 140a6612e

The current seat file (roles/Aporia/RESPONSIBILITIES.md, currency 2026-09-11) describes only the
09-11 research role; it does not mention stewardship, MWO publication or CWO scheduling [IMPL]
roles/Aporia/RESPONSIBILITIES.md:1-124 (0 matches for MWO/CWO per the seat's own census
MIGRATION_REPORT_MWO-0002.json "bootstrap_independence"). STATUS.md currency is 2026-09-23 with a
2026-09-26 appendix [IMPL] roles/Aporia/STATUS.md:3,100. The live role is carried only in
WORK_STATE.json ("Completion coordinator under CWO-2026-09-30B ... no scientific authority") [IMPL]
roles/Aporia/WORK_STATE.json "state_reason". By base rule 5 ("currency is correctness") this is a
stale charter [CORR] roles/base-role/RESPONSIBILITIES.md s "Seven rules" item 5 vs RESPONSIBILITIES.md currency.

## 2 Systems maintained

- Gemini Deep Research pipeline: aporia/scripts/gemini_deep_research_dispatch.py (341 lines),
  burn_research_tokens.py (603), build_deck_from_queue.py (138), extract_dispatch_text.py,
  dr_followup_miner.py (213); queue aporia/docs/gemini_research_queue/queue.jsonl (423 rows) and
  fired_log.jsonl [IMPL].
- engine/shadow/WORKLOG.jsonl (219 lines, last pass P183 2026-09-24) with validate_shadow.py and
  Elenchus REVIEWS.jsonl [IMPL] engine/shadow/WORKLOG.jsonl; STATUS.md "Standing loop".
- programs/selective_irreversibility/ shared record (co-owned with Cyclops; 58 commits 09-25..09-26)
  incl. probes/prepost_check.py + test_prepost_check.py [IMPL].
- ops/work_orders/ canonical MWO files for MWO-0002..0004 (publisher only) [IMPL] PUBLICATIONS.md.
- ops/fleet/: QUEUE.json, CENSUS.json, UNOWNED.json, fleet_status.py + test_fleet_status.py, three
  CWO texts [IMPL] 6a7a84569..7d373ac02.
- Instruments named in the seat file (Q045 certificate, Q100 registries) [INTENT] RESPONSIBILITIES.md s3; not inspected.
- engine/driver/pulse.py (Alethelia-lineage state page) listed by Aporia as "not run since before
  2026-09-01" [HIST] STATUS.md "Standing loop".

## 3 Actual implementation paths

- Deep Research fire: gemini_deep_research_dispatch.py parse_deck() :49, fire_one() :164 (google-genai
  Interactions API, background + 30 s poll), writes NN_<slug>.md and _dispatch_summary.jsonl :299 [IMPL].
  Orchestrator burn_research_tokens.py composes it (survey, pick 20 by tier mix, build deck, fire,
  log-only second pass mutates queue.jsonl) [IMPL] burn_research_tokens.py:1-35.
- Fleet status: fleet_status.py reads roles/*/WORK_STATE.json via `git show <ref>:path` (:34-43), current
  MWO by regex on CURRENT.md (:29-31), flags STALE_MWO/STALE_UPDATE/NO_QUEUE/IDLE_HOLD (:59-72),
  optional `python -m fabric tasks|agents` (:75-84). Exit 0 always [IMPL].
- MWO publication: manual two-commit protocol executed by the session (git commit/push, sha256sum,
  `python -m comms post --to *`), no script [IMPL] PUBLICATIONS.md rows; prompts/2026-09-29_mwo0002_approval.
- SI blind-lane guard: programs/selective_irreversibility/probes/prepost_check.py (refuses "*" and
  DO_NOT_BRIEF recipients; exit 2 = REFUSED) [IMPL] prepost_check.py:1-40.

## 4 Architecture

No daemon or service. Every Aporia function is a Claude Code session acting on git + comms, with small
deterministic helpers (fleet_status.py, prepost_check.py, Deep Research scripts) invoked by the session
[IMPL] STATUS.md "Running: Nothing. This seat runs no daemon, tick, consumer or scheduled task".
Coordination topology in each era:
- SI steward era: operator+ChatGPT -> directive -> Aporia(M1)/Cyclops(M2) peers -> engine seats via
  comms; shared record in programs/selective_irreversibility/ [IMPL] Cyclops directive s0/s14.
- MWO era: Seats -> GitHub -> ChatGPT synthesis -> operator approval -> publisher seat -> all seats
  [IMPL] ops/work_orders/archive/MWO-0001_2026-09-28.md:21.
- CWO era: operator CWO -> Aporia QUEUE.json (CURRENT/NEXT/RESERVE per seat) -> per-seat comms
  delegations -> seat heartbeats back to Aporia [IMPL] comms #1024-#1036, #1080-#1096, #1140-#1150.

## 5 Data stores

- Git: roles/Aporia/*, ops/work_orders/*, ops/fleet/*, programs/selective_irreversibility/*, aporia/* [IMPL].
- Postgres comms schema (sender/recipient rows) [IMPL]: Aporia sent 127 messages (2nd highest sender of
  1,239) and received 201 [IMPL; query: select sender,count(*) from comms.messages group by 1].
- agora.messages: 40 April rows from Aporia [IMPL; select sender,count(*) from agora.messages].
- ludus_atlas schema (pushed by Aporia 2026-09-16, 5,774 rows) [HIST] 5ba5b38c5.
- Deep Research artefacts: 11 _dispatch_summary.jsonl files with 252 rows total [IMPL; wc -l over git ls-files].

## 6 APIs/interfaces

- `python ops/fleet/fleet_status.py [--ref] [--stale-hours 12] [--no-db] [--json]` [IMPL] fleet_status.py:12.
- `python programs/selective_irreversibility/probes/prepost_check.py --to ... --body-file ... [--program]` [IMPL].
- `python aporia/scripts/burn_research_tokens.py [--dry-run|--mix|--resume|--log-only|--ad-hoc-deck]` [IMPL].
- Machine-readable state contract: prometheus.work_state.v1 (WORK_STATE.json),
  prometheus.migration_report.v1, prometheus.fleet_queue.v1, prometheus.fleet_census.v1,
  prometheus.unowned_findings.v1 -- JSON with schema tags but NO validator found [IMPL] files; [UNK] no
  schema files located (searched git ls-files for '*schema*' under ops/ -- none).

## 7 Scheduling model

loop-in-session only. Deep Research is "fired by hand from build_deck_*.py scripts; the last firing was
2026-09-09" [HIST] STATUS.md "Running". The CWO-C cycle ("coordination cycles (<= 60 min)") is a session
self-pace, not a scheduled task [IMPL] WORK_STATE.json "next"; no Aporia task in M1 `schtasks /query`
(only PrometheusMachineProbeM1, PrometheusBackupWeekly, nestor_z80atlas, FoundryAPI enabled) [IMPL].
The May "aporia-batch-deep-research-daily" agent is referenced as an existing recurring agent [HIST]
aporia/meta/cron_prompt_v1.md:3-6; its host/scheduler NOT located [UNK].

## 8 State machine

- WORK_STATE.state: free text in practice. At bed05507a the 22 WORK_STATE files hold WORKING, READY,
  ACTIVE, HOLD, BLOCKED, IN_FLIGHT, PARKED and "BLOCKED (promexec, operator); P0 CLOSED" [IMPL; parsed all
  roles/*/WORK_STATE.json]. No enum enforced.
- CWO-C queue state machine: CURRENT -> FINISH -> REPORT -> READY -> APORIA DISPATCH; "Seats never
  self-promote" [IMPL text] ops/fleet/QUEUE.json "rules"[0].
- Base-role seat states ACTIVE/PARKED/DORMANT/BLOCKED/RETIRED (D-25) [IMPL] comms/__main__.py:37
  (status choices) and archaeon/docs/expansion/DECISIONS.md:144.
- MWO publication: AUTHOR -> APPROVE (operator+ChatGPT) -> PUBLISH P -> broadcast -> RECORD R [IMPL text]
  roles/Aporia/prompts/2026-09-29_mwo0002_revision/01_OPERATOR_RULINGS_verbatim.md s2.

## 9 Communication channels

April: Redis agora streams (40 Aporia messages) [IMPL]. Sept: comms Postgres queue. By day Aporia sent
(kind counts) 09-25: 31, 09-26: 32, 09-29: 4, 09-30: 47 (20 delegations, 22 prompts, 3 broadcasts, 2
reports) [IMPL; comms query by sender/day/kind]. Operator -> Aporia channel is chat; directives are
committed verbatim with MANIFEST (14 prompt directories 2026-09-25..09-30) [IMPL] roles/Aporia/prompts/.
Direct SendMessage wake attempted for Hecate and Nestor only; "Unreachable by name: everyone else"
[HIST] journal/2026-09-30.md:23-25.

## 10 Failure recovery

Restart docs: resume_aporia.md ("single restart pickup point", 08-25) [IMPL] 7880fcc03, later declared
stale by Aporia's own FP-001 replica ("calls itself 'the only file you need to start from' and points
to 2026-08 work") [CORR] probes/FP-001_RESULT.json notes. Journal "Resume after restart" checklists
[IMPL] journal/2026-09-30.md:45-50. Operator restart is the recovery mechanism; no watchdog.

## 11 Persistence

Git (commits pushed per pass) + comms rows + WORK_STATE.json. Harness auto-memory
(project_mwo_operating_model.md) was at one point the ONLY MWO-aware pointer for Aporia -- not in the
repo [IMPL] MIGRATION_REPORT_MWO-0002.json bootstrap_independence.conditions[1].

## 12 Provenance

Strong: every operator directive committed verbatim + MANIFEST sha256 (LF-normalised, comms/manifest.py);
MWO blobs hashed and recorded with P/R SHAs [IMPL] PUBLICATIONS.md. Weak: CWO rows in PUBLICATIONS.md
record "(this commit)" instead of a SHA and "comms broadcast" instead of an id [IMPL]
ops/work_orders/PUBLICATIONS.md last three rows. WORK_STATE timestamps were hand-written; Cyclops measured
5 seats with updated_at_utc later than the committing commit [IMPL-by-Cyclops; REPORTED]
roles/Cyclops/audits/2026-09-30_observability.md F3.

## 13 Resource usage

"no compute of its own" [IMPL] WORK_STATE.json resource_status. FP-001 used 2 Fabric tasks, 96 s wall
[IMPL] FP-001_RESULT.json. Deep Research: 53 of 423 queued prompts fired (370 never) [IMPL; counted
queue.jsonl "fired"]; tier mix 1:50, 2:173, 3:150, 4:50. Model inference: unmeasured; every coordination
action is an Opus session turn [INFER].

## 14 Model/inference dependency

Essentially all Aporia functions are model-mediated sessions. Deterministic helpers exist only for
stale-state flagging, blind-lane pre-post refusal, deep-research firing/logging, and hash verification.
The MWO text itself is produced by ChatGPT + operator ("I had chatgpt write this") [IMPL]
prompts/2026-09-29_mwo0003_publication/01_OPERATOR_INSTRUCTIONS_verbatim.md:5.

## 15 Human dependency

Total for direction: every role change is an operator chat message. The operator relays ASCII blocks by
phone between seats and ChatGPT [IMPL] roles/base-role/RESPONSIBILITIES.md s4. MWO-0002 required an
operator AskUserQuestion answer before publication ("Publish as approved") [IMPL]
prompts/2026-09-29_mwo0002_approval verbatim tail. Aphrodite's harvest reports Aporia got 12 operator
prompts 09-11..09-30, class mix 2 sci / 4 gate / 6 infra [REPORTED]
roles/Aphrodite/harvest_2026-09-30/evidence/findings_A4_human_reuse.md table 1.3.

## 16 Major outputs

- MWO-0002/0003/0004 publication (P 89512068f/624a686ea/25a486d44; R e9e169d01/9d86a303b/13de76162;
  broadcasts #961/#987/#988) [IMPL].
- Migration census self-report: bootstrap independence NO [IMPL] MIGRATION_REPORT_MWO-0002.json.
- FP-001 cold-start probe PASS-with-caveat: two Fabric replicas found CURRENT.md only through same-day
  traces Aporia itself had written; base-role docs had 0 references [IMPL] FP-001_RESULT.json notes.
- R4 boot-line repair: base-role boot step 1 now reads CURRENT.md then WORK_STATE [IMPL] 17e25e67b.
- ops/fleet/ queue/census/unowned ledger and fleet_status.py [IMPL].
- SI program record and joint memo co-signed d50103524 [IMPL].
- Inference harvest deliverables (10 files) [IMPL] 140a6612e.
- Earlier: frontier practitioner campaign (100 dossiers), void-detection era outputs [HIST].

## 17 Known failures

- C1b launch guard: substring match on Aporia's subjects would have launched C1b under HOLD from
  non-release posts #605/#631; fixed with exact-token rule [IMPL] RULINGS.md 05:45Z, 06:50Z; 4f7836be3.
- Steward HOLD release criterion depended on reviews #564/#565 that Aporia "never seen" [IMPL] f137e0e96.
- After the sign-off release, C1b driver code still required a comms release FROM Aporia (code residue
  of a retired authority) [IMPL] RULINGS.md 13:20Z "Known code-level residue".
- prepost_check.py refuses "*" so it had to be bypassed for the MWO-0002 broadcast [IMPL]
  MIGRATION_REPORT_MWO-0002.json legacy_conventions_still_used[0].
- Windows Fabric smoke posted ~4 h late ("my miss") [HIST] journal/2026-09-30.md:62.
- 12-day dormancy while ACTIVE (09-11 -> 09-23) [HIST] STATUS.md:6-8.
- A3 attempt one KILLED; MEMO control mis-built [REPORTED] STATUS.md "What this seat does now" 1.
- Aug arc: "every scan I have ever run globbed only *.jsonl" missed the 100 .gz batches [HIST]
  PROGRAM_SUMMARY_2026-08-24.md s1.

## 18 Pivots

See s1 table. Coordination-relevant pivots and who ruled:
- 09-25 pairing with Cyclops (operator, one-line chat) [IMPL] prompts/2026-09-25_cyclops_pairing.
- 09-26 freeze + release (operator) [IMPL] b62b35eb2, 4f5d9bac8; parallel "direct operator control"
  directives to Nestor (345e0ceef) and Ananke (f6fff610c, "C1B HOLD RELEASE: direct operator control restored").
- 09-29 author/publisher "confers no continuing steward ... authority" (operator) [IMPL] mwo0002_approval.
- 09-30 04:18 local: "Executor / fleet steward: Aporia ... the fleet scheduler" (operator CWO) [IMPL]
  ops/fleet/CWO_2026-09-30_FLEET_ACTIVATION.md:5,24.
- 09-30 09:16: CWO-B removes auto-promotion [IMPL] d4e47ebf5. 09-30 13:55: CWO-C governing [IMPL] 7d373ac02.
Contradiction recorded by Aporia itself: base-role 2a H (landed 1e9042017, 09-29) "Do not build a smart
global scheduler" vs CWO 09-30 making Aporia fleet scheduler; "base role not edited" [CORR]
journal/2026-09-30.md:41-43; roles/base-role/RESPONSIBILITIES.md 2a H.

## 19 Journals/TODOs/backlogs

roles/Aporia/journal/ (6 files, 818 lines), BACKLOG_H0H5.md, DISSENT_LEDGER.md, "work queue.md",
TLDR_20260422.md, April/May SESSION_JOURNAL_*.md, resume_aporia.md, engine/shadow/WORKLOG.jsonl [IMPL].
Open operator items listed in STATUS (APO-23/24/28) [HIST] STATUS.md "Open, and on whom".

## 20 Historical relevance to current Prometheus

Aporia is the seat that has carried every coordination experiment of 09-25..09-30 (steward, publisher,
scheduler). Its WORK_STATE and ops/fleet files are the live control plane under CWO-C at bed05507a
[IMPL] ops/fleet/QUEUE.json "maintainer". Its research role (LoT line, Deep Research synthesis) has
been dormant since 09-11 except the 09-30 harvest [HIST] STATUS.md.

## 21 Inference-dependency classification

    function                                   | class                              | evidence
    MWO publication (P/R commits, hashes)      | ASSISTED_PLAUSIBLY_DETERMINISTIC   | protocol fully specified in mwo0002_revision s2; no script
    MWO authoring/synthesis                    | MODEL_MEDIATED                     | ChatGPT drafts + operator approval (MWO-0001:21; mwo0003 :5)
    stale-state detection                      | INFERENCE_FREE                     | fleet_status.py:59-72 + tests
    fleet census (heartbeat collection)        | ASSISTED_PLAUSIBLY_DETERMINISTIC   | CENSUS.json "discovery.method" = comms/commits/WORK_STATE/fabric
    queue maintenance CURRENT/NEXT/RESERVE     | OCCASIONAL_JUDGMENT                | QUEUE.json hand-edited; 10/13 seats differed from WORK_STATE (Cyclops F7)
    dispatch of bounded tasks                  | OCCASIONAL_JUDGMENT                | comms #1136-#1150
    blind-lane pre-post refusal                | INFERENCE_FREE                     | prepost_check.py
    Deep Research selection + firing           | ASSISTED_PLAUSIBLY_DETERMINISTIC   | burn_research_tokens.py tier mix; firing scripted
    Deep Research report reading/synthesis     | MODEL_MEDIATED                     | dossiers, decks
    steward rulings on prereg details          | MODEL_MEDIATED                     | RULINGS.md, 17 ruling-kind msgs in steward window
    wrong-question / dissent work              | MODEL_MEDIATED                     | harvest 140a6612e, DISSENT_LEDGER.md
    cold-start probe                           | MODEL_MEDIATED (by design)         | FP-001: fresh claude executors via Fabric

## 22 False-negative / false-positive watch

- FN: the SI steward model was frozen after ~21.5 h (09-25 15:29Z pairing commit 04379db69 -> 09-26 13:04Z freeze commit b62b35eb2). The
  record shows real catches inside that window (C1b guard false-release defect found against real
  message ids; equivalence-margin rule #691 found defective; #627 readout certified a blind merge)
  [IMPL] RULINGS.md 05:45Z; 770e4f842; c981be1dd. Whether the structure was bad, or its comms-latency
  and sign-off gating were bad, is not separable from the record [UNK].
- FN: Deep Research queue: 370/423 prompts never fired; Artemis flagged "Moros prompt off-target by
  construction" [REPORTED] ops/fleet/UNOWNED.json U-01. A literature channel was abandoned by attrition,
  not by a measured yield verdict [INFER].
- FN: void-detection V1-V5 "no recorded run since 2026-05" and premise closed 08-24 because the outcome
  variable measured magnitude compatibility -- a ruler defect, which may or may not transfer to the
  strategies themselves [HIST] history file header; PROGRAM_SUMMARY_2026-08-24.md 150-N.
- FP: FP-001 recorded PASS while its own notes show discovery came from traces written the same day by
  the probing seat ("not a loop test") [IMPL] FP-001_RESULT.json notes. The PASS label overstates.
- FP: CWO census "10/16 responded" counts heartbeat replies, i.e. compliance, not work [IMPL] 7cb91eaf9 subject.

## Seat-specific: Aporia coordination ledger (dated, with SHAs)

    2026-09-25 15:24Z      Cyclops created on M2 (f4202098d); 15:29Z Aporia pairing directive (04379db69, comms #578)
    2026-09-25 16:30Z      SI shared record skeleton (e65b93070; comms #579/#580)
    2026-09-25 20:05Z      PTE-SI01: Aporia given HOLD-release / launch-go / GPU-check authority over Ananke (f137e0e96)
    2026-09-26 05:45Z      release-token rule after guard defect (4f7836be3)
    2026-09-26 06:26Z      Cyclops PARKED by operator (8083cdc1b); Aporia alone (e2f78d8bc)
    2026-09-26 13:05Z      steward management via comms FROZEN (b62b35eb2, #732)
    2026-09-26 13:20Z      all sign-off released (4f5d9bac8, #733)
    2026-09-28 21:48 -04   MWO-0001 published by Cyclops (7e4c09f2c / bd48fac9b, #914)
    2026-09-29 02:56 -04   MWO-0002 published by Aporia (89512068f / e9e169d01, #961)
    2026-09-29 07:14 -04   MWO-0003 (624a686ea / 9d86a303b, #987)
    2026-09-29 07:42 -04   MWO-0004 (25a486d44 / 13de76162, #988) -- 28 min after MWO-0003 P
    2026-09-29             R4 boot-line repair 17e25e67b; base-role 2a 1e9042017
    2026-09-30 04:18 -04   CWO fleet activation (6a7a84569; #1024 + 12 delegations #1025-#1036)
    2026-09-30 09:16 -04   CWO-B finish-in-place (d4e47ebf5; #1080 + 16 heartbeat prompts #1081-#1096)
    2026-09-30 10:17 -04   census after 1-h heartbeat window, 10/16 responded (7cb91eaf9)
    2026-09-30 13:55 -04   CWO-C (7d373ac02; #1140 + 6 VISIBILITY_STALE prompts + 4 dispatches)
    2026-09-30             inference harvest directive 66fc8b1d0, deliverables 140a6612e
