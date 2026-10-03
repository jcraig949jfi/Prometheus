# Seat dossier: Odysseus (expeditionary research seat; builder of the Agent Fabric)

- Crawler label: build (Ixion sub-crawler; seats Hephaestus + Odysseus)
- Date: 2026-10-01 (date -u at write: Thu Oct 1 09:46 UTC 2026)
- Base SHA read: bed05507a (origin/main 2026-10-01). Seat commits run 2026-09-25 fe38c055d .. 2026-10-01 a336f6e73
  (git log over roles/Odysseus odysseus: 85 commits, 83 in 2026-09, 2 in 2026-10).
- FULLY READ: roles/Odysseus/{ABOUT.md, RESPONSIBILITIES.md (to s4b), WAKE.md, TODO.md, WORK_STATE.json};
  fabric/{README.md (to s5), FREEZE.md (to incident log)}; fabric/promexec/{STATUS_EXPERIMENTAL.md (to s round 1),
  broker.py docstring}; roles/Odysseus/fabric_pilot/{s2/RESULT.md s1-s3, s3/RESULT.md gate table}; DEFECTS.md row index;
  expedition/YIELD.md pass 1; odysseus/README.md head; full git log of the seat.
- SAMPLED: fabric/store.py connect(); fabric DB (read-only SELECTs, see s5); odysseus/brain line count + test count.
- NOT READ: fabric/{worker.py, executors.py, gateway.py, PROTOCOL.md} bodies; odysseus/DESIGN.md; roles/Odysseus/frontier/
  (77 files), expedition/ subdirs (153 files), d2_audit/ verdicts v1-v13 bodies, prompts/ (40 files), journals; the D2
  holdout protocol (prometheus/cosmos/c3_holdout_D2/ -- EXCLUDED by brief); comms bodies.

## 1 Charter and role history

- [HIST] 2026-09-25 fe38c055d created on ubu001 (ThinkPad X1 Carbon, Ubuntu 26.04.1), base role adopted, charter pending.
  Name self-chosen (ABOUT.md s1).
- [INTENT] 2026-09-26 bd76253c6 charter ADOPTED: distributed brain substrate (prompts/2026-09-26_charter/). e731ac509
  "brain v0 GREEN -- sharded UDP brain with record/play/pause/rewind/ff/fork".
- [HIST] 2026-09-27 626d8c396 operator FREEZE: brain lane parked "for more design". Same day: ABOUT.md, TH-006 slice
  (verification pack for Archaeon run r038751, 455e2e94c tests-first .. e40904023 report), physics-of-intelligence (POI)
  frontier program (ade0d6243 .. 8f47769b0).
- [INTENT] 2026-09-28 02800d2b5 durable role: "expeditionary research seat" (RESPONSIBILITIES s0): foreign idea -> stripped
  mechanism -> minimal world -> falsifier -> transplant candidate. Expedition 1 (d3941cb07, 610e0e296) then FROZEN (1abf82d0f).
- [HIST] 2026-09-28 1abf82d0f operator directive "Agent Fabric / A2A v0" (roles/Odysseus/prompts/2026-09-28_fabric/): the seat
  becomes the fabric builder. 9ff7dd967 fabric v0; ee2948cab v0.1; 3ba6fcc0c v0.2 (lease canonical); FREEZE (tag fabric-v0.2).
- [HIST] 2026-09-29..30: under MWO-0001..0004 and CWO-2026-09-30/B/C: adoption experiments S2/S3, auditor of record for the
  D2 holdout firewall (13 audit rounds v1..v13, 982819f8b .. 6f5ac3192), promexec broker rounds 1-2.
- [CORR] The seat's charter (expeditionary, external frontier) and its actual Sept 28-Oct 1 work (fabric infrastructure,
  firewall audits) diverge; RESPONSIBILITIES s4 lists brain and TH-006 as parked lanes but does not mention fabric as a lane;
  WORK_STATE.json is entirely fabric/promexec/D2.

## 2 Systems maintained

1. Agent Fabric v0.2 (fabric/): durable Task/Attempt/lease queue on M1 Postgres schema `fabric`, pull workers, claude/script/
   synthetic executors, A2A v1.0 JSON-RPC gateway, CLI. FROZEN 2026-09-28 except defect repairs.
2. promexec execution broker (fabric/promexec/, fabric/tools/promexec.py): root-owned sudo broker for model-proposed code;
   EXPERIMENTAL / NOT ENABLED.
3. Legacy-lease compatibility (fabric/lease_compat.py, 8370083ae): Ananke lease.py and nestor_lease.py frontends onto the
   fabric lease row.
4. odysseus/brain (parked): stdlib sharded spiking circuit over UDP with deterministic record/replay/fork.
5. TH-006 verification pack (roles/Odysseus/th006/): node-side recomputation of a run's hashes without bulk evidence.
6. Expedition machinery: expedition/YIELD.md (fate ledger), prior_work_search.sh, recert harness, sandbox, bacc assay
   (roles/Odysseus/expedition/*).
7. Node workers on ubu001 (worker.ubu001.a/.b/.sci) from ~/fabric-runtime.

## 3 Actual implementation paths

- [IMPL] fabric/ 55 tracked files, 3,878 Python lines (wc -l): store.py 586, promexec/acceptance.py 399, gateway.py 383,
  worker.py 296, promexec/broker.py 275, pilot/run_pilot.py 235, executors.py 204, __main__.py 189, tools/promexec.py 172,
  tools/rogit.py 140, lease_compat.py 91; schema.sql; tests 5 files (43 `def test_`).
- [IMPL] odysseus/: 23 files; brain/*.py 1,379 lines; tests 59 `def test_` (grep). [CORR] ABOUT.md says "73 tests";
  Cyclops Windows receipt 428d4b442 says "71 passed" (parametrization would explain the difference [INFER]).
- [IMPL] roles/Odysseus/: 475 files: fabric_pilot 175, expedition 153, frontier 77, prompts 40, th006 9.

## 4 Architecture (fabric)

- [IMPL per README s1-s4, store.py:87-108] Store-authoritative design: Postgres on M1 holds tasks, attempts, leases,
  artifacts+blobs (content-addressed, sha256 verified, 16 MB cap), append-only events, messages, agents/agent_instances.
  Invariants in the DB: one running attempt per task (partial unique index), one unreleased lease per resource,
  UNIQUE(principal, idempotency_key), DB clock for expiry. Fail closed: no store -> no claims (no file fallback).
- [IMPL] connect() goes through evidence_wiki.ew.db + comms.identity.require (wrong-cluster -> WrongEnvironment).
- Worker loop: reap -> touch -> claim with FOR UPDATE SKIP LOCKED filtered by required_caps <@ worker caps; leases taken in
  the claim transaction; detached worktree per base SHA; heartbeat at ttl/4 (fencing: ok=false kills executor); runtime
  uploads final_text.md, stdout, stderr, env_receipt.json, out/*, changes.patch.
- Claude executor: `claude -p` with empty CLAUDE_CONFIG_DIR/HOME, explicit --model, permission-mode dontAsk, Read/Grep/Glob
  scoped to worktree, Write only to out/, git via `rogit`, secret paths denied; token from ~/.config/prometheus/claude.env.
- Script executor: repo file/module at the pinned SHA, no shell, env allow-list. Synthetic executor: test load.
- promexec (round 2 source, not installed): broker takes only run id + two paths + integer limits on argv; runs
  /opt/promexec/py python -I in a transient systemd unit with DynamicUser, PrivateTmp, PrivateNetwork, ProtectSystem=strict,
  NoNewPrivileges etc. (broker.py docstring).

## 5 Data stores

- [IMPL, read-only SELECTs 2026-10-01 ~09:40Z on M1] fabric schema tables: agent_instances, agents, artifacts, attempts,
  blobs, events, leases, messages, tasks.
  - tasks 347: completed 302, failed 28, canceled 17; created 2026-09-28 (139), 09-29 (143), 09-30 (65); none after
    2026-09-30 11:32 -0400. By executor: claude 117 (105 completed, 12 canceled), script 123 (90 completed, 28 failed,
    5 canceled), synthetic 107 (all completed).
  - Principals: Odysseus 85, Artemis 61, Nestor 58, PilotHarness 54, Aether 45, Bellerophon 19, Archaeon 6, Ensorain 6,
    PilotPrincipal 5, Cosmos 4, Harmonia 2, Aporia 2 (12 principals).
  - attempts 373: succeeded 302, failed 61, canceled 7, abandoned 3. Hosts: ubu001 337, ubu002 36. No attempt on M1/M2/M3/M4.
    Attempt wall-hours (sum ended-started): script 15.4 h, claude 9.0 h, synthetic 0.1 h. Models on attempts:
    claude-opus-5-5 103, "claude-opus-4-8,claude-opus-5-5" 1, claude-sonnet-5 1, NULL 268 (non-claude).
  - Top failure errors: worktree add failures (unable to write file / invalid reference c49f2ebad0) ~37, "exit 1" 8,
    timeout 3 -- i.e. most failures are runtime/infra, not task content (matches DEF-ODY-009, -015).
  - leases 40, all released; resources skullport:cpu8 24, spectrex5:cpu12 7, pilot:cpu8 4, skullport:gpu 2,
    ubu001:fp001-probe 2, buckkeep:cpu8 1. First 2026-09-28, last 2026-09-30 20:22 -0400.
  - events: heartbeat 4,196; artifact_added 1,697; claimed 373; requeued 36; lease_expired 2; resource_busy 2.
  - agent_instances 53 rows (22 distinct agents on ubu001, 1 on ubu002); worker.ubu001.a/.b/.sci status online,
    last_seen 2026-10-01 09:40Z -> workers LIVE but IDLE (no tasks for ~18 h).
  - blobs table total relation size 2,888 kB [IMPL] (small artifacts or external storage; not resolved [UNK]).
- Repo stores: roles/Odysseus/fabric_pilot/{s2,s3,d2_audit}/, fabric/pilot/evidence/P1..P8 JSON, DEFECTS.md (23 rows
  DEF-ODY-001..023), WORK_STATE.json, expedition/YIELD.md.

## 6 APIs/interfaces

- [IMPL] CLI `python -m fabric init|submit|tasks|show|events|artifacts|get|cancel|lease acquire/renew/release/status|worker|
  gateway|agents|reap` (README s3).
- [IMPL] A2A v1.0 JSON-RPC at POST /a2a/jsonrpc (gateway.py); TCK results committed in fabric/validation/ (README/FREEZE:
  MUST 68/0, SHOULD 8/0/0; v0 commit message "MUST 65/65, SHOULD 5/5").
- [IMPL] lease_compat frontends (roles/Ananke/research/lease.py, roles/Nestor/tools/nestor_lease.py).
- [IMPL] `python -m odysseus.brain local|init|node|verify|check` (odysseus/README.md).

## 7 Scheduling model

- [IMPL] Fabric is pull-based: "No scheduler assigns work to a machine" (README s1); FIFO claims; FREEZE forbids scheduler/
  priority work. DEF-ODY-021 records short tasks starved behind long ones (no wall-aware ordering).
- [HIST] Workers run as long-lived processes on ubu001 from a detached worktree (FREEZE "Node runtime"); seat runtime is a
  tmux `claude --remote-control ubu001` session under a user service (ABOUT.md s1). Seat cadence: MWO seat loop
  (WAKE.md). No schtasks on M1 for fabric (filtered query empty).

## 8 State machine

- [IMPL] Task: submitted, working, input-required, completed, canceled, failed, rejected (terminal immutable). Attempt:
  running, succeeded, failed, abandoned, canceled. Lease: acquired -> renewed -> released | expired (token-fenced).
- [IMPL] promexec acceptance sequence (STATUS_EXPERIMENTAL.md): commit -> freeze tests -> run -> harden -> Aether review ->
  rerun -> wire -> end-to-end -> S3. Current: round-2 source done, install BLOCKED on operator (WORK_STATE.json).

## 9 Communication channels

- comms on M1 (EW_DB_HOST=192.168.1.202); WORK_STATE comms_cursor 1181. [UNK] `python -m comms who` shows Odysseus last
  2026-09-28 23:07 (instance ubu001-a96af0b0) while commits continue to 10-01; the column may be boot time, not activity.
- fabric thread labels (thr-d2-firewall-audit, thr-fabric-s2, thr-s3) -- "NOT in ops/threads" (WORK_STATE).
- GitHub push from ubu001 with a fine-grained token expiring 2026-10-25 (ABOUT.md s8).

## 10 Failure recovery

- [IMPL] Fabric: fencing tokens, TTL on DB clock, reap of expired attempts, requeue up to max_attempts (36 requeued events),
  late_finish_rejected events, idempotent submit. FP-001 recovery probe PASS (d60389c57: killed Attempt reaped, lease
  released, clean successor).
- [IMPL] DEF-ODY-019 (9c022347e) TCP keepalive + reconnect; DEF-ODY-015 (5266ccebe) bounded checkout cache after ubu001
  disk-full failed 20 Tasks; each repair has a regression test (FREEZE.md incident log).
- [CORR] DEF-ODY-023: the 019 socket hardening broke the Fabric CLI on Windows M1 (c97fe81a5 fix; Aporia #1181 smoke PASS).

## 11 Persistence

Postgres (fabric schema) for runtime state; git for protocols, results, defects, WORK_STATE. Artifacts in fabric blobs.

## 12 Provenance

- [IMPL] env_receipt.json per attempt; base_sha per task/attempt; artifact sha256; S2/S3 preregistered and frozen at commit
  before submission (59b94b4ed, 2a229c9a2); S3 scoring key committed by sha256 before scoring, revealed after (matches).
- [IMPL] REVIEWED_BROKER_SHA256 pins broker.py to 3cf32a64...0df3; `git show HEAD:fabric/promexec/broker.py | sha256sum`
  reproduces 3cf32a64. The Windows working-copy file (CRLF, core.autocrlf=true) hashes c3544f92 -- a Windows checkout
  would fail the pin [IMPL]; same CRLF hazard class as Hephaestus's "manifest-CRLF defect" (a3960783e).
- [HIST] TH-006: M2 attestation MATCH for r038751 (f525de9ef, #799).

## 13 Resource usage

- [IMPL per ABOUT.md, measured 2026-09-27] ubu001: i5-7300U 2C/4T, 7 GiB RAM, no GPU, 207 GB free, Wi-Fi only; safe envelope
  3 cores / 5 GiB. python 3.14 stdlib + psycopg2 + pytest; numpy absent system-wide (fabric/envs/ubu001-sci.pip-local.txt
  suggests a local sci env [INFER]).
- [IMPL] Fabric attempt time 24.5 h total (above). Claude attempts 103+ on opus-5-5.
- [HIST] Disk-full incident on ubu001 2026-09-29 (DEF-ODY-015).

## 14 Model/inference dependency

- The seat itself: claude-opus-5-5 heavy tier, operator-driven via phone remote control (ABOUT.md).
- Fabric runtime: INFERENCE_FREE (store, worker, leases, script executor). Claude executor: MODEL_MEDIATED by design.
- D2 audits, S2 verifications, S3 research packages, blind scoring: MODEL_MEDIATED (fabric claude Tasks).
- Brain substrate, TH-006 check, recert harness: INFERENCE_FREE.

## 15 Human dependency

- [IMPL] promexec round-2 install requires operator sudo (WORK_STATE blocked_on); ubu001->ubu002 ssh key paste awaits the
  operator; Claude login lapse stops the seat until someone logs in from M2 (ABOUT s8); token expiry 10-25.
- Lane assignments came by operator directive each day 09-26..09-28 (charter, freeze, expeditionary, fabric).

## 16 Major outputs

- [IMPL] Fabric v0.2 live: 347 tasks, 12 principals, 373 attempts in 3 days (DB).
- [REPORTED] S2: 18 verifier executions, principal coordination 5 actions (0.28/exec) vs control 126/36 (3.5/exec); 9 claims:
  6 CONFIRMED, 2 PARTIAL, 1 CANNOT-VERIFY, 0 REFUTED (7421fa500).
- [REPORTED] S3: 12/12 first-attempt; coordination 0.67/exec (corrected from 0.33 per Artemis #1019); blind quality 10.0 vs
  control 9.1 "at the rubric ceiling" (MAJOR ruler note per Harmonia #1038); 0 leaks; same-host separation NOT RUN.
- [REPORTED] D2 firewall audit: FAIL v1..v12, PASS v13 (6f5ac3192), anchored FIREWALL_AUDIT_1 (67e05df12, #1021).
- [REPORTED] brain v0: sharded run bit-identical to in-process reference under 40% datagram loss (ABOUT s4).
- [REPORTED] Expedition yield pass 1: 17 ideas; IH->SP 5/5 FALSIFIED-CLAIM (YIELD.md).

## 17 Known failures

- [IMPL] 23 DEF-ODY defects in 3 days (DEFECTS.md), incl. unbounded checkout cache (015), shared checkout race burning
  Attempts (011, 3 occurrences), busy worker shown offline (008), unresolvable base burning retries (009), git allow-rule
  brittle (D12), model pin not honored (003: modelUsage lists opus-4-8 and opus-5-5), FIFO starvation (021), argparse
  `--` args (022), Windows CLI break (023).
- [HIST] Day-one incident: canonical-checkout `git pull` (calibration/LEDGER.md per ABOUT s1).
- [HIST] Claim "the program has not X" wrong once (Cicala Z80 soup was KNOWN-INTERNALLY; YIELD Y09).

## 18 Pivots

brain substrate (09-26) -> frozen (09-27) -> TH-006 + POI frontier (09-27) -> expeditionary seat (09-28) -> expedition 1 frozen
-> fabric builder (09-28) -> fabric frozen for adoption experiments -> auditor/broker/defect-repairer under MWO/CWO (09-29..).
Four lane changes in four days, each operator-directed.

## 19 Journals/TODOs/backlogs

TODO.md (fabric active items; expedition frozen list), WORK_STATE.json (MWO-0004 + CWO-C), fabric/BACKLOG_AFTER_FREEZE.md,
BACKLOG_H0H5.md, expedition/FROZEN.md, frontier/poi/BACKLOG.md (~75 threads per d53c189eb), journal/ (4 files).

## 20 Historical relevance to current Prometheus

- [INFER] Fabric is the newest and most complete Task/Attempt/lease implementation, and the only one with measured
  coordination-cost data (S2/S3). It is the 6th+ queue/lease design (see build_findings D).
- [IMPL] The fabric lease table is declared THE lease authority (README s5, operator ruling 2026-09-28) and legacy helpers
  are cut over (8370083ae).

## 21 Inference-dependency classification

| function | class | evidence |
|---|---|---|
| task queue / claim / lease / reap / requeue | INFERENCE_FREE | fabric/store.py, worker.py; DB events |
| artifact capture + env receipt | INFERENCE_FREE | worker runtime uploads (README s4) |
| script execution of frozen analyses | INFERENCE_FREE | 123 script tasks; executors.py |
| capability probing / env pins | INFERENCE_FREE | fabric/envs/*.probe.json |
| cross-host replay verification (TH-006, brain check) | INFERENCE_FREE | roles/Odysseus/th006; odysseus/brain |
| claim verification of other seats' reports (S2) | ASSISTED_PLAUSIBLY_DETERMINISTIC | S2 claims were hash/line/count checks (C3-C6) done by claude Tasks |
| canary/leak scan | INFERENCE_FREE | S3 CANARY_SCAN.json |
| firewall code audit (D2 v1-v13) | MODEL_MEDIATED | 13 rounds of claude audit Tasks |
| blind quality scoring | MODEL_MEDIATED | S3 scoring Tasks (8) |
| defect triage / recording | OCCASIONAL_JUDGMENT | DEFECTS.md |
| expedition: foreign mechanism harvest, novelty audit | MODEL_MEDIATED | frontier/, YIELD.md |
| work-state updates / MWO adoption | ASSISTED_PLAUSIBLY_DETERMINISTIC | WORK_STATE.json is schema'd (prometheus.work_state.v1) but hand-written per commit |

## 22 False-negative / false-positive watch

- FN: [HIST] brain substrate frozen after 1 day with 59-73 passing tests and cross-OS receipts; parked "for more design", not
  for a failure.
- FN: [HIST] Expedition 1 frozen at 1 day (S7 d16 stopped "when the host reaper stopped it", a86e76b16) -- a resource
  limit, not a result.
- FN: [IMPL] fabric script failures 28/123 are dominated by worktree-add/infra errors; a reader counting failed Tasks would
  misattribute them to the analyses.
- FP: [REPORTED] S2/S3 coordination ratio uses a control coded from another seat's self-test ledger as a lower bound; S3
  quality at rubric ceiling cannot discriminate (Harmonia #1038); S2 control vs treatment differ in task type.
- FP: [REPORTED] D2 PASS at v13 follows 12 FAILs on the same auditor-of-record lineage; later Nestor findings (#1218, #1220)
  ruled NO_INFORMATION by the same seat (76059a9f0, a336f6e73).
