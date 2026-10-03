# Seat dossier: Pronoia

- Seat: Pronoia (Era 1 "Forethought Orchestrator" 2026-03-23..2026-04-01; Era 2 "intelligence_loop" fleet-reporting
  daemon 2026-05-15..present; seat file created 2026-09-11)
- Crawler label: hist (Ixion sub-crawler)
- Date: 2026-10-01 (date -u at start 09:36:30Z, at write 09:47Z)
- Base SHA read: bed05507a (worktree F:/Prometheus-worktrees/ixion-phase3); history read with `git log --all`.
- FULLY READ: deleted pronoia.py (via `git show 3b3c74bc0^:pronoia.py`, 872 lines); agents/pronoia/README.md;
  roles/Pronoia/RESPONSIBILITIES.md; PRON02_GHOST_DISPOSITION sections 1-3; scripts/check_intelligence_pipeline.py
  lines 85-260; scripts/intelligence_loop.py lines 1-140; productive_liveness.py header; all 37 audit + 5 health
  report status lines (grep-tallied); pivot/COMPONENT_DOSSIERS_2026-06-24.md Pronoia entry.
- SAMPLED: 3 of 42 log files read in full (audit_2026-03-23_134526, audit_2026-04-01_032612,
  health_intelligence_enhanced_2026-03-31_191441); QUEUE_ARCHAEOLOGY first 40 lines; test files by function list.
- LIVE READS (read-only, set_session(readonly=True)) against canonical Postgres prometheus_fire on M1:
  agora.agent_heartbeats, agora.intelligence_outputs. schtasks /query on M1.
- NOT READ: intelligence_loop.py lines 140-626 in full (sampled by grep); send_brief_email.py, portfolio_monitor.py
  beyond grep (Hermes/coord crawlers own them); roles/Pronoia/journal in full; the M2/M4 hosts (unreachable from here).
  comms DB not reachable with the agora credentials (no comms schema in prometheus_fire) -> comms history NOT_VERIFIED.

## 1 Charter and role history

- [IMPL] Era 1 created 2026-03-23 in eb17886fa ("agents: add Aletheia, Clymene, Hermes, Pronoia + wire full
  pipeline"); entry point was ROOT-level pronoia.py (523 lines at creation, 872 at deletion; numstat over
  eb17886fa, 7e9719cb0 +369/-37, 8af6ba9e5 +17, 9e189d683 +5/-5).
- [IMPL] pronoia.py deleted 2026-04-23 in 3b3c74bc0 "Clean up repo for external visibility" (message lists
  pronoia.py among "internal scratch") and gitignored (`.gitignore:206:/pronoia.py`, checked with
  `git check-ignore -v`; the seat file cites line 174 at an older base -- line drift, not a contradiction).
- [INTENT] README: "single entry point for the entire Prometheus agent pipeline ... so you can read it on your
  phone" (agents/pronoia/README.md). "Pronoia serves the coffee. You drink it." Gating table: scanning, dedup,
  extraction, brief generation, publishing autonomous; experiment choice and interpretation human.
- [HIST] 2026-06-10 program audit archived the whole serial chain "+Pronoia orchestrator"
  (aporia/docs/program_audit_2026-06-10.md:135-136); 2026-06-15 reset repeats ARCHIVE
  (aporia/docs/STATUS_2026-06-15_reset.md:105). No per-agent adjudication.
- [IMPL] Era 2: scripts/intelligence_loop.py docstring line 3 "Intelligence Loop -- Pronoia-orchestrator for the
  multi-machine reporting pipeline"; first commits b0787cfc4/56d128abc 2026-05-15; PG dual-write heartbeat
  373d81469 2026-05-23.
- [HIST] Seat adopted base role 2026-09-11 (18fee46d0) under operator directive "do nothing else except report what
  the agent did" (roles/Pronoia/prompts/2026-09-11_adoption/OPERATOR_DIRECTIVE.md). Same day a "first active
  mission" (8b0cecadc): ghost pronoia.py on M2 neutralised, heartbeat made work-aware (PRON-03), 36-row liveness
  survey. Seat then returned to BLOCKED on PRON-01 ("does this seat exist, and does it own fleet liveness").
- [IMPL] MONITORS.md assigns Pronoia the PrometheusMachineProbeM1/M2/M4 rows "BY RULING 2026-09-11 evening"
  (roles/base-role/MONITORS.md:21,24,25).
- [CORR] Achilles census (docs/fleet/FLEET_CENSUS.md:60) lists Pronoia "DORMANT (Uncertain)", last activity
  2026-09-18. The Era 2 loop it claims is, by live DB read today, PRODUCTIVE (section 16). The census measures the
  seat's git activity, not its daemon.

## 2 Systems maintained

| System | Era | Status today | Evidence |
|---|---|---|---|
| pronoia.py serial pipeline (scan/eos/metis/status/review) | 1 | retired, deleted, gitignored | 3b3c74bc0 |
| run_audit() in-process health audit (step 7) | 1 | retired | pronoia.py run_audit |
| publish_reports() git add/commit/push to main | 1 | retired; M2 disk copy deleted under PRON-02 | PRON02_GHOST_DISPOSITION |
| scripts/check_intelligence_pipeline.py (health_intelligence reports) | 1 (04-01) | dormant (no caller found) | 9e189d683 |
| scripts/intelligence_loop.py (hourly portfolio refresh + Metis brief, 4-hourly push, daily email, heartbeat) | 2 | LIVE on M4 | agora rows 2026-10-01 |
| PrometheusIntelligenceWatchdog (30-min restarter) | 2 | registered on M4, OWNER UNCLAIMED | MONITORS.md:28 |
| roles/Pronoia/science/productive_liveness.py + liveness_survey.py | seat | on-demand; derive_health imported by the live loop | intelligence_loop.py:63-70 |
| PrometheusMachineProbe M1/M2/M4 (by ruling) | seat | M1 task failing (see 17) | schtasks |

## 3 Actual implementation paths

- Era 1: `git show 3b3c74bc0^:pronoia.py` (blob 96f674b29be55c816a923613fe5798dd48304a0a per PRON02 s2 [HIST]);
  agents/pronoia/README.md; agents/pronoia/logs/ (42 files: 37 audit_*.md, 5 health_intelligence*.md, counted with ls).
- Era 1 called: agents/eos/src/eos_daemon.py, agents/aletheia/src/aletheia.py, agents/skopos/src/skopos.py,
  agents/metis/src/metis.py, agents/clymene/src/clymene.py, agents/hermes/src/hermes.py, ignis/src/review_watchman.py
  (constants at pronoia.py top).
- Era 2: scripts/intelligence_loop.py (626 lines), scripts/portfolio_monitor.py (945), scripts/metis_portfolio.py
  (928), scripts/send_brief_email.py (682), scripts/orchestration_logging.py, scripts/agora_persist.py,
  scripts/intelligence_watchdog.ps1 (66), scripts/register_intelligence_watchdog.ps1 (47),
  scripts/start_intelligence_loop.{bat,sh}. Line counts by wc -l at bed05507a.
- Seat code: roles/Pronoia/science/{productive_liveness.py 227, liveness_survey.py 147,
  test_productive_liveness.py 380, test_heartbeat_wiring.py 224}.

## 4 Architecture

- [IMPL] Era 1 is a SERIAL SUBPROCESS CHAIN in one Python process: `_run_cycle()` runs Eos; only if a digest file
  for today exists does it run Aletheia -> Skopos(ASSESS) -> Metis; then Clymene (72 h cooldown gate read from
  agents/clymene/data/last_run.txt), Hermes, run_audit(logs), a "constitutional pulse" (ingest.get_substrate_health:
  alert if <5 additions in 24h -- PRINT ONLY), Skopos GENERATE if any `skopos_scores.score >= 4` (sqlite), then
  optional publish_reports(). `cmd_scan(every=N)` loops with time.sleep(N*3600). Coordination primitive = file
  existence by date-stamped filename (digest_path, brief_path). Each stage's stdout/stderr captured into a dict.
- [IMPL] No state machine, no queue, no lease; dependency gating is "does today's file exist".
- [IMPL] Era 2 is a long-running daemon with three cadences (hourly / daily / heartbeat tick, default 60 s, M4 run
  at --tick-sec 1800 since 6be994430) and a heartbeat thread mirroring Redis/Agora to Postgres
  (agora.agent_heartbeats). Work-state fields last_work_attempt_at / last_work_success_at are set only at cycle
  boundaries; success requires exit 0 AND a dashboard file mtime >= cycle start (`_cycle_left_evidence`,
  intelligence_loop.py ~line 117-140) -- PRON-03.

## 5 Data stores

- Era 1 [IMPL]: date-named markdown files per agent; agents/aletheia/data/knowledge_graph.db (sqlite; tables papers,
  techniques, reasoning_motifs, tools, terms, claims read by `_query_entity_counts`); agents/skopos/data/scores.db
  (sqlite, table skopos_scores); agents/eos/data/paper_index.json; Clymene last_run.txt; git history (auto-publish).
- Era 2 [IMPL]: agora.agent_heartbeats (36 rows today), agora.intelligence_outputs (pronoia_* stages: 2049 rows
  2026-05-23..2026-10-01, counted by SELECT), docs/state.json, docs/portfolio_brief.md, docs/briefs/,
  docs/manual_status.json, docs/intelligence_loop.log (gitignored).

## 6 APIs/interfaces

- [IMPL] Era 1 CLI: `pronoia.py {scan,eos,metis,status,review} [--every HOURS] [--publish]`; `--every -1` prints an
  easter egg. Interfaces to agents are argv `--once` and date-named output files.
- [IMPL] Era 2 CLI flags: --hourly-min, --daily-hour, --daily-minute, --no-email, --no-metis, --tick-sec
  (intelligence_loop.py docstring; 6be994430). Kill switch file scripts/.intelligence_loop.disabled
  (MONITORS.md:28 [HIST]).
- [IMPL] External APIs reached by Era 1 children (README table): arXiv, OpenAlex, Semantic Scholar, GitHub, Tavily,
  NVIDIA NIM, Cerebras, Groq; Gmail SMTP via Hermes. Keys from agents/eos/.env (README; not opened).

## 7 Scheduling model

- [IMPL] Era 1: hand-started in-process loop (`--every`), no scheduled task in code. [INFER] auto-publish commit
  spacing on 2026-03-23 (13:45, 14:23, 15:00, 15:36, ...) is ~33-38 min, consistent with `--every 0.5` plus run time.
  [HIST] MONITORS.md:46 "no scheduled task ever existed; the orchestrator was hand-run".
- [IMPL] Era 2: daemon + Windows scheduled watchdog (PrometheusIntelligenceWatchdog, every 30 min, restarts the loop;
  register_intelligence_watchdog.ps1). Not on M1 (schtasks /query on M1 shows no such task; only
  PrometheusMachineProbeM1 matched).

## 8 State machine

- [IMPL] Era 1 audit: tri-state HEALTHY/DEGRADED/UNHEALTHY; any HIGH (regex `429|rate.?limit|too many
  requests|backoff`) -> UNHEALTHY; any MEDIUM -> DEGRADED.
- [IMPL] check_intelligence_pipeline.py per-agent: CRITICAL if `[ERROR]|[CRITICAL]` lines; DEGRADED if >5
  `[WARN]|[WARNING]`; HEALTHY if recent_logs>0 OR has_output OR running; else IDLE **with healthy=True**
  (lines 241-253).
- [IMPL] Era 2 PRON-03 derive_health(): levels L0-L4 (process, eligibility, attempt, success, artifact), L5
  (consumption) explicitly not inferable (productive_liveness.py docstring); health values include productive /
  stalled / failing / booting (tests T1-T4). Live value today: 'productive'.

## 9 Communication channels

- [IMPL] Era 1: stdout capture, files, GitHub push (read on phone), Hermes email. Era 2: Agora heartbeat (Redis, later
  PgRedis), Postgres dual-write, docs/* pushed to main for GitHub Pages, daily Gmail digest via send_brief_email.py.
- [HIST] Seat: comms notices 2026-09-11 (590c3431b liveness findings to Archaeon/Mnemosyne/Daedalus/Hermes;
  77c8c7116 reply NONE to TALOS-10). Bodies NOT_VERIFIED in comms DB.

## 10 Failure recovery

- [IMPL] Era 1: none beyond per-stage warnings; publish_reports swallows all git errors (capture_output=True, prints
  only stderr of push). No retry, no lock, no idempotency key besides file existence.
- [IMPL] Era 2: watchdog restart every 30 min; fail-soft optional imports (orchestration_logging, agora_persist,
  productive_liveness: a missing module degrades health to None, intelligence_loop.py:63-70).
- [IMPL] 2026-09-11..09-17: 37 consecutive `pronoia_dashboard_pushed` rows success=false with EMPTY `error` text
  (SELECT grouped by stage/success/error over 2026-09-11..18); recovered 2026-09-18 (6/6 cycle_complete success per
  day from 09-18). [HIST] the fix is 6be994430 (2026-09-17) per its message; causation [UNK].

## 11 Persistence

- [IMPL] Era 1 outputs persisted ONLY because they were auto-committed; Metis briefs were overwritten per date
  (58 distinct brief blobs over 8 filenames in history; see Metis dossier). Audit logs timestamped, never overwritten.
- [IMPL] Era 2 durable rows in agora.intelligence_outputs since 2026-05-23; docs/* commits every 4 h.

## 12 Provenance

- [IMPL] Era 1 audit reports carry a UTC "Generated" line consistent with local filename time +4h.
  check_intelligence_pipeline.py:259 labels LOCAL time as UTC (`datetime.now().strftime("... UTC")`), so the 5
  health reports' "19:14:41 UTC" is local EDT [INFER from filename 191441 and 19:09 local commit].
- [IMPL] Era 2 cycle rows carry cycle_id/run_id; error column empty on 37 failures (weak provenance).
- [IMPL] Every auto-commit authored "James Craig" with machine-generated message; no host field in commits.
- [UNK] Era 1 host: MONITORS.md:46 says M1; roles/Metis/STATUS.md says the March run "was the Pronoia serial
  pipeline on M4"; README paths are F:\Prometheus (M1 convention); audit VRAM total 16311 MiB (a 16 GB card).
  Unresolved.

## 13 Resource usage

- [IMPL] Era 1: GPU readings in 27/37 audits >1 GB (max observed 8909 MiB of 16311) -- attributed by the seat to
  co-resident Ignis training [HIST]; the pipeline itself is HTTP-only [INFER from code: no torch import in pronoia.py].
- [REPORTED] README durations: Eos 2-5 min, Aletheia 1-3, Skopos 1-2, Metis 1-2, Clymene 2-5, Hermes 5 s.
- [IMPL] Era 2 metis_portfolio step 0.3-0.5 s per cycle (output_summary of last two pronoia_brief_generated rows),
  i.e. deterministic mode is cheap.

## 14 Model/inference dependency

- [IMPL] Era 1 orchestrator itself: none. Children: Eos (Nemotron 120B analysis), Aletheia (LLM extraction cascade),
  Skopos (LLM scoring), Metis (LLM brief), Skopos GENERATE (LLM prompt synthesis for "Titan Council"). So ~5 of 9
  stages MODEL_MEDIATED via free-tier external APIs.
- [IMPL] Era 2: metis_portfolio is deterministic unless METIS_LLM=1 (since af9b4d9c9, 2026-08-18); loop otherwise
  inference-free.

## 15 Human dependency

- [INTENT] Era 1 explicitly "human decides" what results mean; pipeline consumer = James's phone.
- [HIST] Era 2: M4 is unreachable to seats; "James has no M4 access to set env vars, so the code default rules"
  (af9b4d9c9 message); M4 diagnosed and healed through the repo only (71d809b49 "W-005 CLOSED").

## 16 Major outputs (with receipts)

- [IMPL] Era 1: 37 audit reports 2026-03-23..2026-04-01; status tally by grep: 27 UNHEALTHY, 10 DEGRADED, 0 HEALTHY.
  Detector firing (grep, files): rate-limit 27, API-error 28 files/31 lines, zero_output 0, VRAM>1GB 27.
  ~40 "pronoia: auto-publish" commits (39 touch agents/pronoia per git log count).
- [IMPL] Aletheia KG growth visible in audits: claims 46->76, papers 82->163, terms 141->224, tools 18->41
  (first vs last audit).
- [IMPL] Era 2 lifetime (agora.intelligence_outputs, all time): pronoia_brief_generated 345 (345 success),
  pronoia_email_dispatched 336 (335), pronoia_dashboard_pushed 335 (298), metis_brief_generated 498 (495);
  2026-05-23..2026-10-01.
- [IMPL] Heartbeat today: agent_heartbeats Pronoia/M4 status online, last_work_attempt_at 2026-10-01 04:14:35-04,
  last_work_success_at 04:15:07-04, health 'productive'. 3 of 36 rows have non-NULL last_work_success_at
  (HealthCheck-M4, MachineProbe-M4, Pronoia) -- the PRON-03 signal the seat said should "climb"; it is 3 vs 2 on
  09-11 [HIST].
- [IMPL] Seat outputs: PRODUCTIVE_LIVENESS_SURVEY, liveness_survey_2026-09-11.json (keys generated_utc,
  assumed_cadence_sec, totals, rows), PRON02 disposition, QUEUE_ARCHAEOLOGY (1 STILL_LIVE, 3 NEEDS_REPREMISE,
  1 PARKED, 3 SUPERSEDED, 3 RETIRED [HIST]).

## 17 Known failures

1. [IMPL] Era 1 audit status near-constant: 0/37 HEALTHY (computed). A single substring "429"/"backoff" in any
   child's log forces UNHEALTHY (pronoia.py run_audit).
2. [IMPL] zero_output (`len(agent_log.strip()) < 20`) fired 0/37 (grep). The captured log is the CHILD's
   stdout+stderr (run_agent_captured), and agents not run are recorded SKIPPED before the check. [HIST] the seat
   says every child that ran printed well over 20 chars, so eligibility was ~0; [UNK] not independently re-measured
   here (child logs are not committed).
3. [IMPL] knowledge_growth has no predicate: counts printed, compared to nothing.
4. [IMPL] VRAM detector measures the whole GPU, not the pipeline; fired 27/37.
5. [IMPL] check_intelligence_pipeline.py: (a) IDLE => healthy=True; (b) warning regex requires bracketed
   `[WARNING]` but Aletheia logs "[ALETHEIA] WARNING" unbracketed, so the 03-31 report shows Groq 403 failures and
   "techniques=0 ... claims=0" under "[HEALTHY] 7/7 agents healthy" and PRONOIA "Recent Log Lines: 0 ... HEALTHY";
   (c) get_latest_report() (line 115) checks a filename containing today's date and never opens it, so a brief whose
   body is the LLM-failure string counts as output.
6. [IMPL] Era 2: heartbeat 'online' while all pronoia_* cycles failed or were absent (09-09..09-17); the seat's
   09-11 measurement of "0 rows since 09-09" is confirmed for 09-09/09-10 and refined: 09-12..09-17 cycles RAN
   6/day but cycle_complete success=0 (dashboard push failing, error text empty).
7. [IMPL] 2026-10-01 brief (docs/portfolio_brief.md, produced by this loop) lists "Pronoia @ M4 ... DEAD, daemon
   stopped -- No heartbeat for 23min" -- the loop reports itself dead because M4 heartbeats were slowed to 30 min
   (6be994430) while portfolio_monitor's DEAD threshold is HEARTBEAT_TIMEOUT_SEC (fleet default). [HIST] 6be994430:
   "Accepted by James: M4 agents will read stale/offline between 30-min beats." An accepted, standing false alarm
   at the top of the operator's brief.
8. [IMPL] PrometheusMachineProbeM1 (owner Pronoia by ruling): schtasks Last Result -2147024894 at 2026-10-01 05:44
   local, still every 5 min. [INFER] 0x80070002 file-not-found (task runs bare `pythonw.exe`). Known since 09-11
   (Atalanta handover to Daedalus) [HIST]; unresolved 20 days later.
9. [HIST] Era 2 state.json frozen 2026-06-24..2026-08-18 because PgRedis lacked exists/hlen/zcard; brief re-narrated
   a June snapshot 6x/day for 8 weeks (af9b4d9c9 message).

## 18 Pivots

- 2026-03-23 Era 1 created -> 2026-04-01 last audit -> 2026-04-23 deleted (3b3c74bc0) [IMPL].
- 2026-05-15 Era 2 born as "Metis portfolio mode: LLM brief over Agora state" (56d128abc) + loop (b0787cfc4) [IMPL].
- 2026-05-19 chain-of-thought strip (52b844afa); 2026-05-23 deterministic fallback (65b6e0140); 2026-08-18
  deterministic-FIRST, LLM opt-in (af9b4d9c9) [IMPL]. This is the clearest documented LLM -> deterministic
  migration in this crawl's territory.
- 2026-09-11 heartbeat made work-aware (PRON-03, 8b0cecadc); live on M4 by 2026-10-01 [IMPL DB].

## 19 Journals/TODOs/backlogs

- roles/Pronoia/BACKLOG_H0H5.md (PRON-01 charter decision XL, PRON-02 ghost, PRON-03 heartbeat, PRON-05 name a
  consumer) [HIST]; journal/2026-09-11.md; calibration/LEDGER.md opens with three rows against the seat itself.
- [HIST] pivot/COMPONENT_DOSSIERS_2026-06-24.md:608-615 "AI suggestion (advisory, NOT approved): REFACTOR"; HITL
  field BLANK.

## 20 Historical relevance to current Prometheus

- Era 1 is the Era-1 BASELINE for coordination: a serial, file-gated, single-process chain with LLM stages, git-push
  as the publication bus, and an audit that graded stdout. Later coordination layers (Agora heartbeats -> comms
  receipts -> MWO/CWO) re-encounter the same question Era 1 failed: "is the stage producing, not just running"
  (base rules 7, 8, 10 cite Pronoia/Atalanta specimens) [HIST].
- Era 2 is today's only automated fleet-wide email/Pages surface and is LIVE [IMPL]; its deterministic brief is a
  working precedent for inference-free reporting.
- [CORR] The 06-24 dossier recommended lifting check_intelligence_pipeline.py's detectors as "directly portable"
  salvage (COMPONENT_DOSSIERS:610); the 09-11 seat audit showed three of those detectors could not fire or measured
  the wrong process. AI-generated salvage advice recommended preserving defective instruments.

## 21 Inference-dependency classification

| function | class | evidence |
|---|---|---|
| Era 1 stage chaining / cooldown gating | INFERENCE_FREE | pronoia.py _run_cycle, clymene_is_due |
| Era 1 health audit (regex over stdout) | INFERENCE_FREE (but invalid) | run_audit |
| Era 1 literature triage (Eos/Aletheia/Skopos/Metis) | MODEL_MEDIATED | README steps 1-4, metis.py call_llm |
| Era 1 "Titan Council" prompt generation | MODEL_MEDIATED | run_skopos_generate |
| Era 1/2 publish to GitHub | INFERENCE_FREE | publish_reports; push_dashboard_to_main |
| Era 2 fleet state snapshot | INFERENCE_FREE | portfolio_monitor.py |
| Era 2 brief narrative | ASSISTED_PLAUSIBLY_DETERMINISTIC (already moved to deterministic default) | metis_portfolio.py:449-458 |
| Era 2 productive-liveness health | INFERENCE_FREE | productive_liveness.derive_health (pure, tested) |
| Deciding whether a stalled loop is a real failure (INDETERMINATE branch) | OCCASIONAL_JUDGMENT | RESPONSIBILITIES 0.3 |
| Seat charter question (does this seat exist) | OCCASIONAL_JUDGMENT (operator) | PRON-01 |

## 22 False-negative / false-positive watch

- FALSE NEGATIVE candidates:
  - [INFER] Era 1's literature-intake idea was not killed by evidence of uselessness; it was archived as a unit
    (program_audit_2026-06-10) without per-agent adjudication. The pipeline's measured defects are implementation
    (free-tier rate limits, an audit that graded stdout, LLM briefs repeating three internal items). Bad RULER and
    bad IMPLEMENTATION, not a tested bad hypothesis. Whether automated literature triage is valuable was never
    measured (no consumption metric existed).
  - [IMPL] The Aletheia KG was growing (papers 82->163 over 9 days); "knowledge_growth" had no predicate, so the one
    positive signal in the pipeline was never evaluated.
- FALSE POSITIVE candidates:
  - [IMPL] Era 2 heartbeat 'online' (pre-PRON-03) and the check_intelligence_pipeline "HEALTHY" reports.
  - [IMPL] Today's census "DORMANT (Uncertain)" vs DB 'productive' -- a false NEGATIVE about liveness by the
    census, and today's brief's "Pronoia DEAD" is a known false alarm (17.7).
