# Seat dossier: Atalanta

- Seat: Atalanta -- "E-track Primitive Hunter" (agent designed by Aporia 2026-05-23); reanimated as a base-role seat
  2026-09-11; RETIRED by the operator 2026-09-11 (RETIRE-AND-LIFT-ASSET).
- Crawler label: hist (Ixion sub-crawler)
- Date: 2026-10-01 (date -u 09:47Z)
- Base SHA read: bed05507a; history via `git log --all`.
- FULLY READ: agents/atalanta/CHARTER.md (157 lines incl. annotations); roles/Atalanta/RETIREMENT_2026-09-11.md;
  DEAD_GATING_SPECIMEN.md s0-2.2; CENSUS_LOOP_RISK s1-2; SALVAGE_ASSESSMENT top + asset 1; calibration L-09/L-10;
  base-role RESPONSIBILITIES rules 7-10; e6b3746f0 commit message; daemon.py lines 60-70, 218-228, 540-556.
- SAMPLED: ARCHAEOLOGY/PROPOSED_INVARIANT by headings; reference/ by line count; journals not read.
- LIVE READS: agora.intelligence_outputs atalanta_* and agora.agent_heartbeats (read-only).
- NOT READ: daemon.py in full (631 lines; sampled at cited lines); test_null_bound.py body; the three handover
  prompts; Hypatia/Pheme siblings beyond the commit message; the M1 gitignored artifacts directory (no longer cited
  as present).

## 1 Charter and role history

- [IMPL] Created 2026-05-23 04:43 -04 in e6b3746f0 "Aporia: three new agents for typed-DR substrate production"
  (Hypatia D-track, Atalanta E-track, Pheme demand voicer) "per pivot/persona_seed_prompts_2026-05-21.md".
- [INTENT] CHARTER: read Apollo organism logs, find high-reuse primitives and repeated unnamed length-2/3 composite
  chains, pick top-1 (anti-greedy rotation), fire a Type-E Deep Research query via agora.research_queue so Techne
  can register new primitives and Apollo's next run has a richer pool ("The feedback loop closes").
- [HIST] 2026-06-10 program audit: "Atalanta + Pheme (healthy but starved by dead upstreams -- shelve or rewire)"
  (aporia/docs/program_audit_2026-06-10.md:132-133).
- [HIST] 2026-08-20 Aporia P47 autopsy counted 354 UPSTREAM_NOT_FOUND artifacts on M1 (graded G3 by the seat).
- [IMPL] 2026-09-11: adoption b33712c94 -> self-test findings 96bf180e3 -> ATALANTA-04 specimen 827d021eb ->
  RETIRED 051304cd0. Operator epitaph (RETIREMENT_2026-09-11.md): "Atalanta was designed to detect reusable
  primitives. She detected none. Her reusable primitive was the failure mode of the detector itself."

## 2 Systems maintained

- [IMPL] AtalantaPrimitiveHunterLoop (agents/atalanta/daemon.py --loop --interval 1800), retired, code kept
  annotated. [IMPL] roles/Atalanta/reference/null_bound.py (126 lines) + test_null_bound.py (182) -- reference
  implementation of base rule 10. [IMPL] roles/Atalanta/ledgers/telemetry_census.py -- regenerable query.

## 3 Actual implementation paths

- agents/atalanta/{CHARTER.md, daemon.py 631, __init__.py, .gitignore}; scripts/atalanta_loop_launch.bat [HIST, not
  opened]; roles/Atalanta/* (11 md files + reference + ledgers).

## 4 Architecture

- [IMPL] Per-tick daemon (14-step contract): pid lock, session_telemetry heartbeat, state.json, scan
  APOLLO_RUN_ROOTS (daemon.py:63-67: apollo/runs, apollo/runs_v2, apollo/organism_runs -- three consumer-chosen
  literal paths), count primitives, enqueue DR, emit artifacts/events, anti-silence counter with alarm at 50.
- [IMPL] Liveness test = path existence (`find_active_apollo_root`, daemon.py:222-226).
- [IMPL] Alarm branch (daemon.py:547-552) emits `atalanta_self_audit_null` with no return and no state change, so
  it fires every tick after 50.
- [INTENT] Downstream: Pythia dispatches DR; ingestion to techne/registry/primitive_candidates/ "TBD; currently
  manual".

## 5 Data stores

- [IMPL] agora.intelligence_outputs (live read today): atalanta_upstream_not_found 354 rows (0 success),
  atalanta_self_audit_null 305 (0 success), atalanta_startup 3, atalanta_shutdown 1; first 2026-05-23 04:28 -04,
  last 2026-05-30 12:10:49 -04. These match the seat's numbers exactly.
- [IMPL] agora.agent_heartbeats row 'Atalanta' / SKULLPORT / status 'online' / last_heartbeat 2026-05-30 12:10 -04 --
  still reads 'online' four months after death (as does Hypatia).
- [HIST] Gitignored agents/atalanta/{state,artifacts,logs}/ on M1 -- ATALANTA-02 open, not reachable by the seat.

## 6 APIs/interfaces

- [IMPL] `python -m agents.atalanta.daemon --once | --loop --interval 1800 | status`; agora_persist.enqueue_research
  (target_substrate_type 'E', priority 4, queue_ref ATA-<date>-<NNN>) [INTENT, never exercised: 0 dispatches].

## 7 Scheduling model

- [HIST] Hand-launched detached via .bat from the canonical checkout; "no scheduled task has ever existed"
  (MONITORS.md:63). [REPORTED] 48.4 ticks/day vs 48.0 predicted (DEAD_GATING s1.4).

## 8 State machine

- [IMPL] tick outcomes: dispatch / dispatch_failed / NULL_TICK / UPSTREAM_NOT_FOUND / APOLLO_FORMAT_DRIFT (charter);
  anti_silence_counter resets only on productive tick. No park state -- the absence that rule 10 later supplies.

## 9 Communication channels

- [IMPL] heartbeat + log_work rows (read by nobody); [HIST] seat-era comms: #86/#97 (rule 10 proposal), handovers
  to Archaeon, Rhadamanthus, Daedalus (prompts/2026-09-11_closeout/). Bodies NOT_VERIFIED (comms DB not reached).

## 10 Failure recovery

- [IMPL] none effective: alarm writes a row; no route, no stop. [HIST] 2 of 3 sessions ended without a shutdown row
  ("killed, not stopped").

## 11 Persistence

- [IMPL] dual record (filesystem artifacts on M1 + agora rows), single mechanism; the seat states this is an
  independent RECORD, not an independent MEASUREMENT (DEAD_GATING s1.2) -- a provenance distinction worth keeping.

## 12 Provenance

- [IMPL] DEAD_GATING specimen grades every number G1-G4 (re-measured / canonical store / other seat not
  re-verifiable / derived) before use. Prediction-then-query: 305 alarm rows predicted from control flow, observed
  305 (verified by this crawl: 305).

## 13 Resource usage

- [INFER] CPU-only, trivial. 7 d 07:42 of operation [REPORTED, consistent with min/max finished_at read today].

## 14 Model/inference dependency

- [IMPL] Detection: INFERENCE_FREE (counters). [INTENT] Output: a Type-E Deep Research prompt (MODEL_MEDIATED, external
  DR via Pythia) -- the design pushed all inference to the downstream DR stage. Never reached.

## 15 Human dependency

- [INTENT] Ingestion of DR reports into Techne "manual for now"; promotion "Techne's call". Every useful output would
  have required a human or a model to read DR prose.

## 16 Major outputs

- [IMPL] Agent: zero domain outputs (0 Apollo runs scanned, 0 candidates, 0 DR dispatches) -- agora rows show no
  dispatch stage at all.
- [IMPL] Seat (one day): base rule 10 adopted as D-27 (7f68f5093, roles/base-role/RESPONSIBILITIES.md:135-157) with
  BOUND/ACCOUNTABLE SEAT registry columns and a downward-only ratchet test; DEAD_GATING_SPECIMEN; 30-loop census
  [REPORTED: UNROUTED 18/30, ROUTED_PASSIVE 9/30, ROUTED_ACTING 3/30]; D-28 producer-declaration invariant OPENED
  (still an unchecked item: roles/Archaeon/TODO.md:277 "F-35 (operator): rule on D-28").
- [IMPL] L-09 boot incident -> WORKING_CONTRACT.md s3 clause and roles/base-role/WAKE_DIRECTIVE.md rewording (cited
  "Archaeon, on Hypatia #90 and Atalanta L-09").
- [HIST] Found PrometheusMachineProbe M1/M2 failing; handed to Daedalus. [IMPL] still failing on M1 today (schtasks
  Last Result -2147024894, 2026-10-01).

## 17 Known failures

1. [IMPL] Consumer invented producer's interface (three literal paths Apollo never wrote) -- the operator's
   formulation: "A consumer was allowed to invent the producer's interface, and then mistake failure of that
   invented interface for failure of the producer."
2. [IMPL] Liveness test checks a path, not a producer.
3. [IMPL] Alarm without recipient or obligation; emitted 305 times.
4. [IMPL] Heartbeat row still 'online' 2026-05-30 (today).
5. [HIST] L-09: seat ran `git pull` in the canonical checkout at boot because the wake directive said "Pull the
   latest first"; no damage measured; became a contract clause.
6. [HIST] L-10: derived "~201 alarm firings" for Polyhymnia from prose; measured 23 (factor ~9).
7. [CORR] P47 autopsy's "consumer of a dead producer" back-projected Apollo's 2026-09-01 suspension onto May; Apollo
   committed 12 times during Atalanta's window (RETIREMENT item 5) [HIST, not recounted here].

## 18 Pivots

- 2026-05-23 built -> 05-30 last tick -> 06-10 "shelve or rewire" -> 06-24 dossier called two assets "salvage IP" ->
  09-11 adopted, specimen, salvage test (NOTHING unique), retired same day.

## 19 Journals/TODOs/backlogs

- roles/Atalanta/BACKLOG_H0H5.md, journal/2026-09-11.md + 2026-09-11b.md, calibration/LEDGER.md (13 rows),
  ARCHAEOLOGY (22 items, STILL_LIVE 0) [HIST].

## 20 Historical relevance to current Prometheus

- [IMPL] Atalanta's specimen is the direct source of base rule 10 and the open D-28 producer-declaration decision --
  both are about deterministic loop governance (bounded no-ops, typed park, named accountable recipient).
- [IMPL] The census predicate C1/C2/C3 (input bound by guess / unbounded no-ops / alarm without accountable
  recipient) is a deterministic, inspectable loop-risk classifier.

## 21 Inference-dependency classification

| function | class | evidence |
|---|---|---|
| primitive frequency / composite-chain counting | INFERENCE_FREE | daemon.py aggregate_primitive_signals; apollo/scripts/inspect_population.py:69-75 [HIST salvage] |
| candidate selection (anti-greedy rotation) | INFERENCE_FREE | CHARTER step 7 |
| turning a candidate into a named primitive with signature | MODEL_MEDIATED (Type-E DR) | CHARTER template |
| promotion into Techne registry | OCCASIONAL_JUDGMENT (human/Techne) | CHARTER downstream |
| null-tick bound + park (rule 10) | INFERENCE_FREE | reference/null_bound.py |
| loop-risk census C1-C3 | ASSISTED_PLAUSIBLY_DETERMINISTIC (C3 read from registry text) | CENSUS_LOOP_RISK s2 |

## 22 False-negative / false-positive watch

- FALSE NEGATIVE (strong): the scientific hypothesis -- recurring composite chains in evolved Apollo organisms
  signal missing primitives worth naming -- was NEVER TESTED. 0 runs were read. Death cause = IMPLEMENTATION/WORLD
  binding (guessed paths, assumed JSON container), not hypothesis. The retirement text itself says "the organism
  model was sound ... primitive_sequence ... is still live throughout apollo/src" and the composite-chain counter
  "rest[s] on a premise nothing ever tested" (RETIREMENT item 6; SALVAGE asset 2). Retirement was a UNIQUENESS test
  on code, not a test of the idea. Apollo itself was suspended 2026-09-01 [HIST], so the world is also absent now.
- FALSE NEGATIVE (minor): the "five mandated calibration patterns" in the DR template were never audited
  (SALVAGE asset 3) -- neither validated nor refuted.
- FALSE POSITIVE: the agent "scored" 354/354 productive under any emission-keyed metric (every tick wrote a
  well-formed artifact) -- the canonical example of emission != productivity.
