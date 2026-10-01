# Seat dossier: Achilles (fleet census) -- plus shared fleet infrastructure pointers

Seat: Achilles
Crawler label: fleet (Ixion sub-crawler)
Date: 2026-10-01T09:46Z (from `date -u`)
Base SHA read: bed05507a (origin/main as seen by the ixion-phase3 worktree). Census snapshot audited:
docs/fleet/fleet_state.json generated 2026-10-01T04:35:00Z from origin/main 38d317a83 (commit db657a6df).

FULLY READ: achilles/census/{sources,classify,build,run,util}.py; achilles/deploy/*; achilles/README.md;
roles/Achilles/{RESPONSIBILITIES,STATUS,TODO,BACKLOG_H0H5,RECONSTRUCTION_2026-09-30}.md;
roles/Achilles/journal/2026-09-30.md (lines 1-160); roles/Achilles/census/registry/SCHEMA.md;
roles/Achilles/census/runs/2026-10.jsonl; docs/fleet/run_status.json; scripts/send_brief_email.py:445-483.
SAMPLED: achilles/census/render.py (grep of functions, staleness JS 136-143); achilles/census/tests/test_census.py
(test names); registry seats_part1.json (first record); docs/fleet/fleet_state.json (programmatic extraction of
all 88 rows: state, rule, flags, last_active, last_commit basis, task source, host); CLASSIFICATION_RULES.md
(headings only); comms DB (read-only queries, see s5/s9).
NOT READ: registry seats_part2-4.json and engines.json record-by-record (3,436 + 3,521 lines); index.html body;
email_census.json body; roles/Achilles/prompts/* verbatim charters (only filenames + journal summary);
the ELSA host itself (task state, census.log, state.json, PARKED.json) -- this crawl ran on M1 and cannot see ELSA.

Tag key: [IMPL] [INTENT] [HIST] [REPORTED] [CORR] [INFER] [UNK] per CRAWL_BRIEF.

---------------------------------------------------------------------------------------------------------------

## 1 Charter and role history

- [HIST] Created 2026-09-30 on host ELSA (192.168.1.163, Windows 10 Home) as a base-role seat, charter PENDING:
  d56ac4937 (creation pass), pushed 090317f9f, heartbeat to Aporia comms #1197 (d6f36008b).
- [IMPL] Operator charter "ACHILLES -- PROMETHEUS FLEET CENSUS AND STATUS SYSTEM" committed verbatim at
  roles/Achilles/prompts/2026-09-30_charter/ and adopted in a797beabd (2026-09-30 21:44 -0400), which in one commit
  landed the census engine, classification rules, registry, mailer section, and MONITORS.md row.
- [IMPL] Pre-charter role body preserved in roles/Achilles/superseded/ (RESPONSIBILITIES_pre_charter_2026-09-30.md,
  BACKLOG_H0H5_pre_charter_2026-09-30.md).
- [INTENT] One-sentence contract (roles/Achilles/RESPONSIBILITIES.md s0): "one authoritative, evidence-backed map
  of the entire Prometheus fleet ... each value citing its source -- rebuilt every six hours on the observability
  and reporting machinery Prometheus already has." Explicit non-powers (s3): never assigns work, never rules on
  science, never writes the DB, never edits other seats' files.
- [IMPL] Total seat lifetime at crawl time: ~14 h; 7 commits touch achilles/ or roles/Achilles/ (git log).

## 2 Systems maintained

- [IMPL] achilles/census/ (Python package, 1,804 lines incl. tests): sources -> classify -> build -> render -> run.
- [IMPL] Outputs: docs/fleet/fleet_state.json (schema prometheus.fleet_census.v2, 1.28 MB), docs/fleet/index.html
  (0.69 MB), docs/fleet/email_census.json (44 KB), docs/fleet/FLEET_CENSUS.md, docs/fleet/run_status.json,
  roles/Achilles/census/runs/<YYYY-MM>.jsonl (run.py:36-81).
- [IMPL] Seat/engine registry roles/Achilles/census/registry/ (seats_part1-4.json, engines.json) -- 88 entities,
  133 engines per journal [HIST]; built_at 2026-10-01T01:22:42Z from 9e4d75e62 (seats_part1.json header).
- [IMPL] Scheduled task PrometheusFleetCensus on ELSA (achilles/deploy/register_fleet_census.ps1) and its
  MONITORS.md row "PrometheusFleetCensus / AchillesFleetCensus" (bound 4, accountable Achilles).
- [IMPL] An additive section in a mailer it does not own: scripts/send_brief_email.py:445-482 build_fleet_census.

## 3 Actual implementation paths

achilles/census/sources.py (280) evidence collectors; classify.py (328) deterministic rules; build.py (717) snapshot,
aggregates, delta, anomalies; render.py (345) HTML/email/markdown; run.py (233) one cycle incl. git push; util.py (132)
time/git/read-only DB/provenance field; tests/test_census.py (217, 26 tests per journal); deploy/run_census.cmd (9),
deploy/register_fleet_census.ps1 (52). [IMPL] (wc -l at bed05507a)

## 4 Architecture

[IMPL] Pipeline per run (run.py:130-201):
1. refuse canonical checkout (run.py:45-52, git-dir == common-dir test, same idea as archaeon/workspace.py);
2. `git fetch --prune`, hard `checkout -f --detach origin/main`, `clean` of its own output dirs (run.py:55-59);
3. open a read-only DB session via comms.api.connect + `SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY`
   verified by `SHOW default_transaction_read_only` (util.py:390-412);
4. build snapshot (build.py:437-677) from git (all origin refs), roles/ files, ops/fleet ledgers, MONITORS.md,
   comms.agents/agent_instances/messages, ew.experiments, agora.agent_heartbeats, agora.intelligence_outputs;
5. write 5 outputs + append a receipt line (run.py:62-81); commit only those paths as author "Achilles";
   push HEAD:refs/heads/main with up to 4 attempts, re-sync + rewrite on rejection, verify ancestry (run.py:84-107);
6. update local state.json (failure_streak, consecutive_nonproductive) and maybe park (run.py:193-200).
Code runs from a pinned sparse worktree (achilles-census-pinned, detached 885f41df1, 18 files) and writes into a
separate sparse publish worktree (2,248 files) [HIST journal 2026-09-30 "Launch"].

## 5 Data stores

- [IMPL] Git (origin/main) is the canonical store of the snapshot; history of fleet_state.json is the time series
  (ACHILLES-17 defers a separate history dir).
- [IMPL] Local state on ELSA: <state-dir>/state.json, last_failure.txt, PARKED.json, census.log (run.py:139-144,
  196, 214; run_census.cmd:9). Not in git. [UNK] contents not inspected (ELSA not reachable from this crawl).
- [IMPL] Read-only DB sources (M1 prometheus_fire): comms.*, ew.experiments, agora.agent_heartbeats,
  agora.intelligence_outputs (sources.py:240-280).

## 6 APIs/interfaces

- [IMPL] CLI: `python -m achilles.census.run --publish-root <wt> [--state-dir] [--no-push] [--no-sync] [--deep]`
  (run.py:131-137). Exit 0 OK, 1 FAILED, 3 PARKED.
- [IMPL] Consumer contracts: email_census.json {schema prometheus.fleet_census_email.v1, generated_at_utc,
  markdown, html, rows} read by send_brief_email.build_fleet_census; run_status.json
  {schema prometheus.fleet_census_run.v1} fetched by the page's JS (render.py:143).
- [IMPL] Public page https://jcraig949jfi.github.io/Prometheus/fleet/ via .github/workflows/pages.yml (deploys docs/).

## 7 Scheduling model

- [IMPL] Windows Task Scheduler on ELSA: daily 00:30 local with PT6H repetition for P1D, StartWhenAvailable,
  IgnoreNew, 1 h limit, LogonType Interactive (needs the operator's logged-on credential store for git push)
  (register_fleet_census.ps1:40-51).
- [IMPL] Evidence of firing: receipts at 2026-10-01T03:46:12Z (manual Start-ScheduledTask, deep) and 04:35:00Z
  (incremental) in roles/Achilles/census/runs/2026-10.jsonl; commits 189e12502, db657a6df. The 04:35Z start
  vs the 04:30Z slot is unexplained [UNK]. The 10:30Z slot had not occurred at crawl time.
- [UNK] Task state on ELSA not verified by this crawl (not M1). M1 `schtasks /query` shows no Achilles task (expected).

## 8 State machine

[IMPL] Run-level: SUCCESS / FAILED / PARKED (run.py:142-144, 199-201, 227-228); failure_streak and
consecutive_nonproductive counters in state.json. Seat-level classification is the S0-S6 rule cascade
(classify.py:221-328) -- see Deep reconstruction "activity inference".

## 9 Communication channels

- [IMPL] comms posts (subprocess `python -m comms post ... --kind report`) only at failure-streak start and on park
  (run.py:110-127, 226). Best-effort, exceptions swallowed (run.py:118-119).
- [IMPL] comms DB, 2026-10-01 query: Achilles sent 7 messages (#1197, #1209, #1224-#1228), all kind=report; 3 are
  heartbeats to Aporia; 4 are launch notices/defect reports (Hermes+Pronoia, Aporia, Atlas, Archaeon). Achilles
  received 0 messages addressed to it (query on recipients).
- [IMPL] Page + email are the "loud" channel (run.py:11-14 docstring).

## 10 Failure recovery

- [IMPL] On exception: snapshot/page NOT replaced; only run_status.json + receipt committed (run.py:216-224); browser
  computes staleness from run_status (render.py:136-143, STALE_AFTER_H=7.0 render.py:16); mailer prints STALE /
  UNAVAILABLE (send_brief_email.py:463-480).
- [IMPL] Push rejection: sleep 5+10i s, re-sync, rewrite outputs, retry up to 4 (run.py:84-107).
- [IMPL] Park: after BOUND=4 consecutive non-productive runs, write PARKED.json, `schtasks /Change /DISABLE`, one
  comms report (run.py:122-127). Resume = delete park record + re-enable (manual).
- [INFER] The park bound cannot fire on the success path: `productive` is true whenever origin/main's SHA or the
  comms max id changed since the previous snapshot (run.py:171-172). The census's own push moves origin/main after
  every successful run, and the M4 loop pushes "auto: portfolio update" every 4 h (12 such commits since
  2026-09-29 by `git log --grep`), so consecutive_nonproductive resets every successful run. It can still fire via
  repeated FAILURES (run.py:212). (Same class as memory rule "guard that cannot fire".)

## 11 Persistence

[IMPL] Every run commits ~2 MB of regenerated JSON/HTML to main (fleet_state.json 1,281,076 B + index.html
691,531 B + email 44,383 B at 05:28 local mtime). At 4 runs/day this is ~8 MB/day of raw blob churn before
compression [INFER, arithmetic from file sizes]. Aggregates are carried in the snapshot itself ("aggregates",
"engine_aggregates", "cursors": build.py:671-674), so the snapshot is also the incremental crawler's state.

## 12 Provenance

- [IMPL] Every important per-seat field is util.field(value, source, source_time, observed_at, confidence)
  (util.py:346-353); evidence list strongest-first (build.py:366-379); state_detail carries rule id, "why" strings,
  every declared state with source+age (build.py:409-411).
- [IMPL] Receipt per run: run_id, host, code_root, code_sha, publish_root, base_sha, status, mode, commits_scanned,
  counts, anomalies, sources status, productive, publish_sha (run.py:150-152, 178-181, 192).
- [IMPL] Commit message names base SHA, host, code SHA (run.py:187-191).
- [IMPL] Email addresses redacted from all published artifacts (sources.py:220-225; run.py:67).
- [INFER] Weakness: the registry (declared_role, observed_role, lifecycle_marker, documented_host, engines) is the
  output of model-authored "registry passes" (journal 2026-09-30 lines 94-98) with path:line sources, but is
  thereafter treated as input facts; drift checking of declared vs observed role is backlog ACHILLES-10, not code.

## 13 Resource usage

[IMPL] Receipts: deep run 40 s over 10,679 commits; incremental run 27 s over 4 commits (runs/2026-10.jsonl).
[HIST] journal: dry-run deep build 16 s over 10,607 commits; first attempt at two full 66k-file checkouts was
killed under host memory pressure, rebuilt as sparse worktrees. No model inference per run [IMPL: no LLM import in
achilles/census/*.py; classify.py:1-6 states "No model sits in this path"].

## 14 Model/inference dependency

- [IMPL] Per-run census: INFERENCE_FREE (regexes, timestamps, git, SQL).
- [HIST/INFER] One-time: the registry (88 seat records, 133 engines, role prose, lifecycle markers, aliases,
  documented hosts) and RECONSTRUCTION_2026-09-30.md were produced in a model session (Claude, instance
  elsa-c0ac1245). Anomalies are routed to owners by the seat (model) per ACHILLES-06, not by code.

## 15 Human dependency

- [IMPL] Interactive logon of the operator's account on ELSA required for push (register_fleet_census.ps1:17-18,47).
- [IMPL] Un-parking is manual (run.py:124). [HIST] gh credential set up by the operator 2026-09-30 (RESPONSIBILITIES s5).

## 16 Major outputs

[IMPL] 189e12502 (first census, deep, 59 seats / 88 entities, 28 anomalies), db657a6df (incremental, 27 anomalies);
RECONSTRUCTION_2026-09-30.md (forensic map of the reporting stack); 4 defect reports (#1224-#1227).

## 17 Known failures

[HIST] Dry-run defects fixed before launch (journal): MONITORS parser read 0 rows; 27% unattributed commits before
the engine registry (7% after); mailer receipt leaked recipient email address; mixed timezones; "review packet" and
"FREEZE.md" read as experiments; 2 MB snapshot / 87 KB email. Post-launch failures found by THIS crawl: see
"Census output checked against reality" below (path-majority misattribution; STATUS.md line misparse; experiment
over-count; self-activity; park guard).

## 18 Pivots

[IMPL] Pre-charter generic base-role seat -> chartered census seat within ~2.5 h (d56ac4937 -> a797beabd);
[HIST] decision to extend Aporia's v1 CENSUS.json rather than invent a schema, and to reuse the existing mailer,
Pages and Task Scheduler rather than Fabric or a Claude /loop (RECONSTRUCTION s4).

## 19 Journals/TODOs/backlogs

[IMPL] TODO.md (ACHILLES-01..04 still open at 01:45Z though journal says 01-04 done by 03:55Z -- [CORR] TODO lags
journal); BACKLOG_H0H5.md ACHILLES-01..20 (attribution <5%, RESULT.md/REVIEW_PACKET experiment sources, Fabric
evidence, calibration vs Aporia's hand census over 7 days, second census host). calibration/LEDGER.md empty.

## 20 Historical relevance to current Prometheus

[INFER] Achilles is the first fleet-wide, scheduled, inference-free status producer that reads all four evidence
planes (git, seat files, comms, ew/agora) and publishes with provenance. It supersedes as a *source* (not by
deletion) the M4 portfolio_monitor roster view (hard-coded EXPECTED_AGENTS, scripts/portfolio_monitor.py:85),
agora.agent_heartbeats liveness, stations/*_STATUS, and complements Aporia's hand-kept ops/fleet/CENSUS.json v1.

## 21 Inference-dependency classification

| function | class | evidence |
|---|---|---|
| roster discovery (roles/ on all origin refs) | INFERENCE_FREE | sources.py:22-45, build.py:440-456 |
| commit attribution | INFERENCE_FREE | classify.py:75-115 |
| experiment detection | INFERENCE_FREE (regex; noisy) | classify.py:122-153 |
| state classification | INFERENCE_FREE | classify.py:221-328 |
| HTML/email rendering | INFERENCE_FREE | render.py |
| scheduling, push, park | INFERENCE_FREE | run.py, register_fleet_census.ps1 |
| seat/engine registry (roles, markers, aliases, hosts) | MODEL_MEDIATED (one-time), then static input | journal 2026-09-30:94-98; SCHEMA.md |
| anomaly routing to owners | OCCASIONAL_JUDGMENT (seat session) | BACKLOG ACHILLES-05/06; comms #1224-1227 |
| registry drift re-verification | ASSISTED_PLAUSIBLY_DETERMINISTIC (not implemented) | ACHILLES-10 |

## 22 False-negative / false-positive watch

- False positive (activity): Mnemosyne shown ACTIVE (S4-activity) from 2c8c81bbb, an Archaeon-executed commit
  (Archaeon WORK_STATE "#1148 complete (2c8c81bbb") attributed by path-majority to evidence_wiki's primary seat.
- False positive (activity): Achilles's own census commits count as its substantive "work" every run [INFER from
  classify.py:136-153 -- subject has no status/experiment token and files are not STATUS_PATHS].
- False negative (state): Atlas shown PARKED because the parser takes the first "seat state:" line
  (classify.py:198, 205) which refers to the index LOOP; the seat's fresh line "state: READY" in the same STATUS.md
  is ignored.
- False positive (experiments): experiments_24h=62 counts verdict-vocabulary commits, incl. inference-harvest
  deliverables, audit rulings and a "method frozen" commit whose subject contains "IQ-NULL".
- False-negative risk for Phase 3: seats with no commits/messages but real out-of-git compute (ELSA, ubu00x,
  Fabric workers) would read DORMANT; Fabric is not a source (ACHILLES-09 blocked on #1135).

---------------------------------------------------------------------------------------------------------------

## ACHILLES DEEP RECONSTRUCTION

All line refs at bed05507a. "Ran" evidence: R1 = receipts roles/Achilles/census/runs/2026-10.jsonl (2 rows);
R2 = commits 189e12502 (deep) + db657a6df (incremental); R3 = mailer receipt agora.intelligence_outputs
stage=email_dispatched 2026-10-01T04:15Z output_summary "... census=2026-10-01T03:46:12Z rows=59 age_h=0.5"
(queried read-only by this crawl); R4 = snapshot fields in docs/fleet/fleet_state.json @ db657a6df.

### Roster discovery
- Code: sources.py:22-28 (ref_tips: every refs/remotes/origin/*), 31-33 (ls-tree roles/ on a ref, minus base-role),
  36-45 (branch_only_roles); build.py:34-50 (registry load + hash), 440-466 (entity universe + Roster).
- Algorithm: entities = roles/<X> dirs on origin/main (kind from registry, default SEAT) U roles/<X> found only on
  other origin branches (BRANCH_ONLY_SEAT) U registry rows of kind AGENT_TOOL. Roster = canonical names + single-token
  registry aliases of relation lane/instance; resolve() is case-insensitive and strips "-X" lane suffixes
  (classify.py:52-72). roster_hash over sorted names triggers deep mode on change.
- Deterministic. Inputs: git refs, registry JSON.
- Ran: yes (R1 seats=59, entities=88; R4 includes Chiron as BRANCH_ONLY_SEAT).

### Role discovery
- Code: registry declared_role/observed_role consumed at build.py:356-364, 402-404; entry file + "Currency:" line
  sources.py:91-113; operator prompt dir sources.py:147-176.
- Algorithm: role text is copied from the registry (declared_role.text, with source + currency); observed_role shown
  only when registry says differs; flags MISSING_ROLE_DESCRIPTION / NO_ROLE_DOCUMENT. Entry file chosen by fixed
  precedence BOOTSTRAP > STARTUP > RESPONSIBILITIES > ROLE > CHARTER.
- Deterministic at run time; the role TEXT itself is MODEL-AUTHORED once (registry passes) and not re-derived.
- Ran: yes (R4 role_description fields).

### Activity inference
- Code: build.py:191-228 (candidates), classify.py:136-153 (commit category), 166-177 (message level),
  221-328 (S0-S6 + active word), constants FRESH_H=24, RECENT_H=72, IDLE_LIMIT_H=168, DECLARED_FRESH_H=72
  (classify.py:215-218).
- Algorithm: substantive = newest of (non-status attributed commit, level-3 comms message, ew.experiments row);
  status = newest of (status-only commit, heartbeat message, WORK_STATE updated_at); presence = newest of
  comms.agents last_sync/last_active and agora heartbeat. "active" Yes if substantive <=24 h; Uncertain if <=72 h
  or status/presence <=24 h. Presence never makes a seat ACTIVE (cheat controls).
- Deterministic. Ran: yes (R4 active_6h/24h/72h = 11/21/21).

### Engine mapping
- Code: registry engines.json; build.py:468-492 (engine_of / path_owner by longest path prefix), 81-84 (per-engine
  last/recent commits), 569-596 (engine rows, OWNERSHIP_DRIFT, ENGINE_NO_OWNER).
- Algorithm: each touched file maps to the longest registry engine path; engine last_change = newest touching commit
  (deep: `git log -1 -- paths`); contributors = attributed seats of last 12 commits; drift flagged when >=5
  attributed commits and a non-listed seat holds a strict majority.
- Deterministic; engine catalogue model-authored once. Ran: yes (R4 "engines" block).

### Last-task mapping
- Code: build.py:261-291; helpers _ws_task 145-155, _status_next_action 168-173.
- Algorithm: candidates = QUEUE.json seats.X.current (rank 1), CENSUS.json v1 forward.current_objective (rank 1),
  newest operator prompt dir (rank 2), newest comms prompt/delegation addressed to the seat (rank 3); NEWEST BY TIME
  wins regardless of rank. Fallbacks: WORK_STATE current_objective/next_actions (rank 4), STATUS.md "next executable
  action" (rank 6). All candidates kept in task.candidates.
- Deterministic. Ran: yes. Observed weakness: Hermes's "task" is comms #73, a 2026-09-11 delegation; Mnemosyne's is
  comms #461 (a Campaign-6 delegation) -- the newest-wins rule surfaces stale delegations when nothing newer exists.

### Experiment mapping
- Code: classify.py:122-158 (RESULT_RE, START_RE, NOT_EXPERIMENT_RE, STATUS_PATHS_RE); build.py:105-110, 293-310;
  ew source sources.py:257-262; window count build.py:509-513.
- Algorithm: commit subject regex over capitalised verdict words -> experiment_result; PREREG/FROZEN/LAUNCH ->
  experiment_start; negatives for heartbeat/pytest/dashboard etc.; ew.experiments newest row per agent_id competes
  by time; infrastructure/reporting/coordination/audit domains get "N/A".
- Deterministic. Ran: yes (R4 experiments_24h=62). This crawl reproduced 382 commits / 62 results in the same 24 h
  window with the same classifier on local refs; the 62 include harvest deliverables ("RESULT: wave-2 ..."),
  Harmonia rulings/audits, an "Ananke tools: freeze_check" commit (PASS), and "U-02 method frozen" (NULL via
  "IQ-NULL"). [INFER] it is a verdict-word counter, not an experiment ledger. ew.experiments is stale: 79 rows,
  newest 2026-09-03 (query).

### Git mapping
- Code: sources.py:48-68 (one `git log --no-merges --name-only` over all origin tips, trailers unfolded),
  classify.py:75-115 (A1-A6 attribution), build.py:75-110 (aggregates), 312-316 (last commit field).
- Algorithm: precedence: "auto:" -> SYSTEM; "Seat[instance]:" prefix; "Seat <topic>:" word prefix; "<Seat>-Instance:"
  trailer; strict path majority over roles/<Seat>/ and engine primary seats; author name; else unattributed (counted,
  sampled, never guessed). Instance tag -> host via HOST_PREFIX map (classify.py:14-40).
- Deterministic. Ran: yes (R1 commits_scanned 10,679 deep). [HIST] 7% unattributed (779/10,607) per
  RECONSTRUCTION s5.11.

### Canonical state
- Code: build.py:654-677 (snapshot dict), run.py:62-81 (write), util.py:382-387 (atomic write via tmp+replace).
- Algorithm: one JSON object = summary + mailer health + seats + engines + anomalies + stats + cursors +
  aggregates + delta; HTML/email/markdown rendered only from it (README).
- Deterministic. Ran: yes (R2). Note: extends but does not replace ops/fleet/CENSUS.json v1, which remains Aporia's
  hand-maintained file (16 seats, as_of 2026-09-30T18:05Z) and is read as one declared-state source.

### HTML generation
- Code: render.py:29-62 (table rows), 147-280 (render_html), 136-143 (client-side freshness).
- Algorithm: static page with embedded JSON rows + JS filter/sort; freshness banner computed in the viewer's browser
  from run_status.json fetched at view time, red if >7 h old or last_status != SUCCESS.
- Deterministic. Ran: yes (docs/fleet/index.html committed; [HIST] Pages run 36812088571, HTTP 200 per journal --
  not re-checked by this crawl).

### Email integration
- Code: render.py:289-340 (email_block: md + inline-styled html); scripts/send_brief_email.py:445-482
  (build_fleet_census), 617-622 (inserted into body), 653-655 (receipt tag in emit_event summary);
  build.py:625-637 + sources.py:273-280 (census reads the mailer's own receipts, sets census_included_last,
  raises EMAIL_NOT_SENT_72H).
- Algorithm: closed loop -- census writes block; M4 mailer (every 4 h, run by scripts/intelligence_loop.py) embeds it
  or prints STALE/UNAVAILABLE; mailer writes census=<ts> into agora.intelligence_outputs; next census verifies.
- Deterministic. Ran: YES -- R3 (04:15Z email carried census 03:46:12Z) and R4 mailer.census_included_last=true,
  failures_72h=0. email_dispatched has 3-6 successful rows per day back to at least 2026-09-12 (query).

### Scheduling
- Code: achilles/deploy/register_fleet_census.ps1:40-51; run_census.cmd:1-9; run.py TASK_NAME 38.
- Algorithm: user-level Windows task, 6-hourly, IgnoreNew overlap policy, 1 h execution cap; env EW_DB_HOST=M1.
- Deterministic. Ran: R1/R2 two runs. [UNK] ELSA task state not inspected.

### Incremental crawl
- Code: build.py:494-507 (deep vs incremental decision + `git log ... --not <previous tips>`), 519-526 (comms
  cursor id > previous max), 671-674 (cursors persisted in snapshot); DEEP_EVERY_H=168 (build.py:27).
- Algorithm: carry previous aggregates; scan only commits unreachable from previous ref tips (tips verified to still
  exist via cat-file) and messages above comms_max_id; deep rebuild on first run, roster/registry hash change, or 7 days.
- Deterministic. Ran: yes (R1 second row mode=incremental, commits_scanned=4, 27 s).
- [INFER] Edge: force-pushed/rebased branches whose old tips vanish drop out of the exclude list and are re-scanned
  (safe, idempotent via _newer); deleted branches' seats can only disappear at the next deep pass.

### Provenance
- Code: util.py:346-353 (field), build.py:366-379 (evidence list), 409-411 (state_detail), run.py:150-152,
  178-181 (receipt), 187-191 (commit message).
- Deterministic. Ran: yes (R4 fields carry source/source_time/observed_at/confidence).

### Conflict detection
- Code: classify.py:243-249 (CONFLICTING_STATES among fresh declarations; confidence capped MEDIUM), 271-275
  (ACTIVITY_AFTER_RETIREMENT), 280-284 (PARKED_BUT_ACTIVE); build.py:328-333 (documented vs observed host kept
  side by side), 585-594 (OWNERSHIP_DRIFT / ENGINE_NO_OWNER), 598-623 (UNKNOWN_COMMS_SENDER/AGENT,
  UNFAMILIAR_SEAT_IN_WORK_ORDER, BRANCH_ONLY_SEAT, UNATTRIBUTED_COMMITS, SEAT_DISAPPEARED, NEW_SEAT).
- Deterministic. Ran: yes (R1: 28 then 27 anomalies; R4 flags CONFLICTING_STATES on Aphrodite, Artemis, Odysseus,
  Techne, Theseus).
- Note: conflict is FLAGGED, not resolved; resolution = freshest declaration (declared.sort by age, build.py:250),
  which lets a third party's v1 census line (Aporia, 11 h) outrank the seat's own WORK_STATE (14 h) for Theseus.

### Stale-task detection
- Code: classify.py:296-300 (VISIBILITY_STALE, ACTIVE_NO_WORK_48H), 320-324 (STALE_TASK: declared BLOCKED/HOLD with
  no substantive work in 7 d); build.py:288-291 (ASSIGNMENT_NO_PROGRESS: task >24 h old and no substantive work since).
- Deterministic. Ran: yes (R4 STALE_TASK on Agora, Hypatia, Icarus, Nous).

### Failure reporting
- Code: run.py:202-229 (failure record pushed; comms report on streak start), 110-119 (_post_comms best-effort),
  122-127 (_park), 199-200 (non-productive park); render.py:136-143; send_brief_email.py:463-480.
- Deterministic. Ran: [UNK] no failure has occurred (both receipts SUCCESS). The STALE/UNAVAILABLE email paths are
  covered by tests test_mailer_says_stale_loudly / _missing_loudly (test_census.py:201-214) [IMPL test exists;
  not executed by this crawl]. Park guard see s10 [INFER cannot fire on success path].

### Census output checked against reality (12 seats; snapshot 04:35Z vs `git log 38d317a832 -- roles/<Seat>` and
### `git log --all -i --grep "^<Seat>[[ :]"` before 04:35Z)

| seat | census state / last commit (basis) | git reality | verdict |
|---|---|---|---|
| Achilles | READY; 49aac03d0 (prefix) | roles-dir last 49aac03d0 | MATCH |
| Aporia | WORKING; 737d9209b (prefix) | roles-dir last 737d9209b | MATCH |
| Atlas | PARKED (S2-parked-active); d95cffcc8 "state READY" | STATUS.md line 5 "state: READY", line 24 "seat state: PARKED ... for the index LOOP" | MISMATCH: parser takes line 24 (classify.py:198-205) |
| Atlas-M2 | IDLE; 53e071604 | roles-dir last 53e071604 (09-25) | MATCH |
| Mnemosyne | ACTIVE (S4-activity); 2c8c81bbb (path-majority) | roles-dir last 8915b660f 2026-09-18; 2c8c81bbb body cites "Aporia #1148"; Archaeon WORK_STATE claims it | MISMATCH: misattribution -> false ACTIVE |
| Hephaestus | IDLE; d22beca12 (09-25) | roles-dir last d22beca12 | MATCH |
| Odysseus | BLOCKED; a336f6e73 (path-majority) | roles-dir last a336f6e73 (a D2 ruling addendum in roles/Odysseus) | MATCH (basis weak) |
| Agora | BLOCKED + STALE_TASK; 8dc34fe32 (09-14) | roles-dir last 8dc34fe32 | MATCH |
| Pronoia | DORMANT; 6be994430 "M4: stop console-window popups" (path-majority, 09-18) | roles-dir last 77c8c7116 (09-11); 6be994430 touches scripts/* owned by Pronoia in registry | PLAUSIBLE; attribution by engine ownership, not authorship |
| Alethelia | DORMANT; d27c208a6 (09-11) | roles-dir last d27c208a6 | MATCH |
| Hermes | DORMANT; 283687393 (prefix, 09-11) | roles-dir last 44d3dd7ff is a Ludus commit touching roles/Hermes | MATCH (census correctly ignores the foreign commit) |
| Cyclops | PARKED + PARKED_BUT_ACTIVE; 9ec36b2bf "parked" | roles-dir last 9ec36b2bf | state MATCH; flag is a false alarm (the "parking" commit itself is the substantive activity) |
| Metis | RETIRED + ACTIVITY_AFTER_RETIREMENT; f9f90c0f7 | roles-dir last f9f90c0f7 (Season 1 CLOSED 09-13) | MATCH (flag plausible) |
| Koios | DORMANT; d13f20df34 (path-majority, 04-23) | roles-dir last 249bb0f98 is a base-role commit (09-11); last prefix commit 2026-04-18 | MATCH |

Result: 10 of 14 checked rows match git; 2 substantive mismatches (Mnemosyne false ACTIVE, Atlas false PARKED);
2 weak/false-alarm flags (Cyclops PARKED_BUT_ACTIVE, Pronoia ownership-based attribution). [IMPL; computed by this
crawl with the two git log forms above and a programmatic dump of fleet_state.json]
Additional: comms check -- census "last activity" for Achilles = comms 03:47:33Z = message #1227 (MATCH).

### Mechanisms that could support Phase 3 resource/scientific accounting (observational)

| existing mechanism | accounting signal it already produces | gaps (observed) |
|---|---|---|
| Commit attribution (classify.py:75-115) + aggregates (build.py:75-110) | per-seat commit counts, last work, recent commits, host via instance tag; per-engine last change + contributors | 7% unattributed; path-majority credits engine owners for others' work (Mnemosyne case); no commit size/effort; no cost |
| Commit vocabulary experiment detector (classify.py:122-153) | experiment start/result events with verdict token, per seat, per 24 h | counts verdict words, not experiments; no link to prereg/result files; ACHILLES-08 (RESULT.md, REVIEW_PACKET) unbuilt |
| comms messages (sources.py:252-254, build.py:113-140) | per-seat message counts by level (substantive/heartbeat/ack), assignments (prompt/delegation) | no body-size/token accounting used; kinds self-declared by sender |
| comms.agents / agent_instances (sources.py:240-249) | per-seat model id, machine, last sync/active, instance count | model is self-declared at boot; no session duration, tokens or $ |
| ew.experiments (sources.py:257-262) | experiment rows with git_commit | stale since 2026-09-03 (79 rows) |
| Mailer receipts agora.intelligence_outputs (sources.py:273-280) | delivery success/failure, census inclusion | only for one mailer |
| MONITORS.md parse (sources.py:199-217, build.py:565-567) | per-seat standing loops with host, bound, accountable seat | registry hand-maintained; contradicted by DB for the portfolio producer (see fleet_findings) |
| Run receipts (run.py:150-181) | census duration, commits scanned, source health per run | census-only |
| Delta (build.py:682-717) | state changes, new assignments, experiments completed, blockers added/cleared | per-run only; no trend store (ACHILLES-13 unbuilt) |
| Missing entirely | -- | CPU/GPU-hours, wall-clock per task, inference tokens/cost per seat, Fabric task/attempt rows (ACHILLES-09), lease usage (~/ananke_runs/leases, agora.gpu_reservations 5 rows) |
