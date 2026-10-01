# Seat dossier: Alethelia

- Seat: Alethelia -- "truthful reporter", "the sensory cortex that is not allowed to imagine". Chartered 2026-08-17,
  built 2026-08-20 inside the Aporia loop (P29), base-role adoption 2026-09-11 as an on-demand instrument (no host).
- Crawler label: hist (Ixion sub-crawler)
- Date: 2026-10-01 (date -u 09:47Z)
- Base SHA read: bed05507a; history via `git log --all`.
- FULLY READ: roles/Alethelia/{RESPONSIBILITIES.md, STATUS.md, CALIBRATION.md, BACKLOG_H0H5.md,
  notes/BOOTSTRAP_M1_2026-08-27.md (first 40 lines), notes/NAME_COLLISION_2026-08-27.md (first 60)};
  agents/alethelia/alethelia.py lines 1-60 + function index; test_alethelia.py function index;
  aporia/docs/germline_infrastructure_2026-08-17.md s6; 756b7cf16 message; stations/REPORT_latest.md (worktree, and
  the canonical checkout copy, head only).
- NOT READ: BASE_ROLE_ADOPTION_2026-09-11.txt, journal in full, alethelia.py bodies of q_* functions,
  engine/decoys/DECOY_SET.jsonl beyond one grep line. Tests NOT run (prohibited mutation risk: the reporter writes
  stations/REPORT_latest.*).

## 1 Charter and role history

- [HIST] Charter RATIFIED by James 2026-08-17 (aporia/docs/germline_infrastructure_2026-08-17.md s6): monitors and
  reports only; "every field in every report must be traceable to a query ... any field it cannot compute is
  rendered UNKNOWN(n), never narrated"; decoy law; two-control rule (positive: real anomaly gets through; cheat:
  fabricated calm does not pass). Planned products: weekly HITL page, PushNotification on kill-conditions only,
  station health.
- [HIST] Motivation stated in the charter: "the old M4 reporter's documented failure mode was confabulation ('14
  agents pending' fabricated from 43 UNKNOWNs, mailed to James 6x/day for seven weeks)". [INFER] that reporter is
  Pronoia Era 2's metis_portfolio LLM path (see Metis/Pronoia dossiers); Alethelia's NAME_COLLISION note calls the
  predecessor "Aletheia_M4 ... the old M4 reporter".
- [IMPL] v0 built 2026-08-20 in 756b7cf16 "Aporia P29: Alethelia v0 -- the reporter that cannot fabricate calm";
  P30 decoy law (e773576c8), P31 DR event trail (b781e06af) touched it the same day.
- [HIST] 2026-08-27 manual M1 run ("usually run on M3" per James) -- output not committed for 15 days (CALIBRATION 2).
- [IMPL] 2026-09-11 base-role adoption d2c54fa2b: v0.1 anomaly rules, comms-receipt liveness, canonical-checkout
  refusal, 7 controls; journal close d27c208a6 ("comms message 17 to Archaeon").
- [IMPL] Census: DORMANT, last activity 2026-09-11 (FLEET_CENSUS.md:77). Name chosen to break a three/four-way
  "Aletheia" collision (KG component agents/aletheia/, the M4 reporter seat, the M4 hostname alias, Alethelia).

## 2 Systems maintained

- [IMPL] AletheliaReport (agents/alethelia/alethelia.py v0.1, 444 lines; test_alethelia.py 185 lines). Registered
  DORMANT in MONITORS.md:50.

## 3 Actual implementation paths

- agents/alethelia/alethelia.py, agents/alethelia/test_alethelia.py; outputs stations/REPORT_latest.{md,json};
  inputs agora.agent_heartbeats, comms.receipts/messages, git, engine/queues/BACKLOG.jsonl + GATE_ELI5.jsonl,
  engine/ledger/DR_EVENTS.jsonl, engine/shadow/WORKLOG.jsonl + REVIEWS.jsonl (MONITORS.md:50).

## 4 Architecture

- [IMPL] Source families -> fields, each `{"value":..., "query": "<how computed>"}` or `{"unknown": reason, "query"}`
  (`field()`, alethelia.py:60). Sections: postgres (q_postgres:65), comms (q_comms:92), git (q_git:153), queues
  (q_queues:179), shadow (q_shadow:234), workspace (q_workspace:262).
- [IMPL] 7 deterministic anomaly rules (evaluate_rules:314-348): stale_heartbeats, zombie_running, no_unblocked_work,
  shadow_input_dormant, unanswered_reviews, unreviewed_passes, dormant_on_comms. Each returns FIRED / CLEAR /
  INDETERMINATE(reason); a rule over an UNKNOWN field is INDETERMINATE.
- [IMPL] Banner (banner_text:375-388): calm ONLY if zero UNKNOWN fields, zero FIRED and zero INDETERMINATE; text
  "calm is not implied by silence" on degraded.
- [IMPL] Thresholds are constants traced to the registry: SHADOW_DORMANT_H 48, COMMS_DORMANT_H 24,
  HEARTBEAT_STALE_H 6 (alethelia.py:55-57).
- [IMPL] Dependency injection: build_report(pg=q_postgres, git=..., ...) (line 351) -- fixtures replace sources in
  tests (clean_*, fake_pg, dead_pg, dead_queues, stale_shadow, stale_pg, empty_queues in test_alethelia.py).

## 5 Data stores

- [IMPL] Reads only; writes stations/REPORT_latest.md/.json (overwritten; no dated copies -- ALET-16 proposes them).

## 6 APIs/interfaces

- [IMPL] `python agents/alethelia/alethelia.py`; `python agents/alethelia/test_alethelia.py` (exit 0 required).
  Entry point refuses the canonical checkout (D-23 s1) [HIST STATUS; guard code not read line-by-line].

## 7 Scheduling model

- [IMPL] none. "Host: NONE ... on-demand instrument until the deployment decision (ALET-04) is taken" (STATUS.md).
  Runs recorded: 2026-08-20 (committed), 2026-08-27 (uncommitted), 2026-09-11 (committed). No M1 scheduled task
  (schtasks query found none).

## 8 State machine

- [IMPL] Report-level: CALM / ANOMALIES / DEGRADED by banner_text; rule-level FIRED/CLEAR/INDETERMINATE.

## 9 Communication channels

- [IMPL] files committed with the pass; [HIST] comms message 17 to Archaeon (d27c208a6), not verified in comms DB.
  [INTENT] PushNotification / weekly HITL page never built (ALET-17/18).

## 10 Failure recovery

- [IMPL] source failure -> UNKNOWN + DEGRADED banner (design core). No retries, no scheduling, so no recovery loop.

## 11 Persistence

- [IMPL] git history of stations/REPORT_latest.* (4 commits: 756b7cf16, e773576c8, b781e06af, d2c54fa2b).

## 12 Provenance

- [IMPL] Every value carries its query string; every report carries workspace base_sha/branch/worktree/dirty
  (v0.1). Strongest per-field provenance discipline seen in this crawl's four seats.
- [IMPL] Defect left in place: the canonical checkout F:/prometheus/stations/REPORT_latest.md (mtime 2026-09-20 local,
  head read today) carries the OLD v0 banner "all 15 fields computed from live queries" dated 2026-09-11T11:42:40 --
  the wrong-directory run recorded in CALIBRATION item 4; the operator declined the repair (STATUS "Open"). The
  canonical file currently shows as modified in git status. A reader of the canonical checkout sees the calm-style
  v0 banner, not the v0.1 anomaly report.

## 13 Resource usage

- [INFER] a handful of SQL queries and file reads per run; negligible.

## 14 Model/inference dependency

- [IMPL] none. Pure queries + rules. The seat was built as the explicit inference-free replacement for an LLM reporter.

## 15 Human dependency

- [HIST] Host decision ALET-04 (operator, XL) open since 2026-09-11; M4 seat needs James at the box; consumer of the
  report is the operator.

## 16 Major outputs

- [REPORTED] 2026-08-20 first clean report: 31/34 agora heartbeat rows ~90 days stale with status 'online' (756b7cf16).
- [REPORTED] 2026-08-27: 33/35 stale-online; BACKLOG 644 PARKED / 138 DONE / 0 QUEUED; DR_EVENTS.jsonl 0 bytes
  despite "DR event trail live" claim in P31; 81 of 644 PARKED gates without ELI5 (DEC-005).
- [IMPL] 2026-09-11 committed report: 19 fields, 0 UNKNOWN, 5/7 rules FIRED (stations/REPORT_latest.md at bed05507a).
- [IMPL] Re-measured today: 32 of 36 agora.agent_heartbeats rows are status 'online' with last_heartbeat older than
  7 days (SELECT count). The label/property gap Alethelia reported on 08-20 persists 6 weeks later.

## 17 Known failures

- [HIST] CALIBRATION 1: v0 banner measured source REACHABILITY and read as HEALTH while 31/34 rows stale (15 days
  uncorrected). 2: uncommitted run = "chat claim". 3: dormant_on_comms over-fired on 20 never-booted seats (caught
  pre-commit). 4: ran old code from canonical checkout to "prove the guard" (D-23 s1 violation).
- [IMPL] No host: the instrument has not run since 2026-09-11 (20 days) by commit evidence.

## 18 Pivots

- 08-17 charter (M4 seat) -> 08-20 v0 inside Aporia loop on M1 -> 08-27 M1 manual -> 09-11 v0.1, registered DORMANT,
  "M4 seat" heading annotated STALE.

## 19 Journals/TODOs/backlogs

- BACKLOG_H0H5.md ALET-01..24, notably ALET-06 (read every MONITORS row's freshness source), ALET-07 (diff
  scheduled tasks vs registry), ALET-18 (deterministic PushNotification predicates, "no model in the path"),
  ALET-22 (label/property disagreement rule).

## 20 Historical relevance to current Prometheus

- [IMPL] The clearest existing pattern for inference-free reporting: query-carrying fields, UNKNOWN-not-narrated,
  rule tri-state, calm-requires-zero, fixture-injected controls including cheat controls.
- [IMPL] Its backlog is effectively a spec for a deterministic registry auditor (ALET-06/07/10/22) that Achilles'
  census (2026-09-30) partially overlaps [INFER; coord crawler owns Achilles].

## 21 Inference-dependency classification

| function | class | evidence |
|---|---|---|
| field collection (pg/git/queues/shadow/comms) | INFERENCE_FREE | q_* functions |
| anomaly rules + banner | INFERENCE_FREE | evaluate_rules, banner_text |
| choosing thresholds / which rules exist | OCCASIONAL_JUDGMENT | constants traced to MONITORS rows |
| deciding the host / paging predicates | OCCASIONAL_JUDGMENT (operator) | ALET-04, ALET-18 |
| narrative interpretation of anomalies | not performed by design | charter s6 |

## 22 False-negative / false-positive watch

- FALSE NEGATIVE: the instrument is VALID (7/7 controls, per STATUS) but unscheduled; its "dormancy" is a deployment
  decision gap, not an instrument failure. A future reader seeing DORMANT should not infer the design failed.
- FALSE POSITIVE: v0 calm-style banner (still present in the canonical checkout copy).
- [UNK] The 7/7 control pass is reported, not re-run here.
