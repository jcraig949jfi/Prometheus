# C-012-T004 preregistration -- Fabric + PostgreSQL publication as the Moonshot work plane

Task C-012-T004. Owner: Themis. Authority: OP-NF2 s6 ("Once the two-node implementation passes its
fault-injection controls, preregister a bounded multi-node benchmark"); T003 closed at 974275bca. Written and
frozen BEFORE any benchmark data: the commit that adds this file with its MANIFEST is the freeze, and every run
receipt must come after it in git history. A change after any data exists is a NEW preregistration with its own
manifest, never an edit of this one.

Disclosure -- seen before freezing. Three harness smoke tests ran to validate tooling (labelled SMOKE, excluded,
files kept in evidence/T004/SMOKE/): N at D = 1 s, W = 2, 40 s: 43 published, M1 = 0.062 (RECONSIDER, B1); S at
K = 2, 20 s: 292 published, RECONSIDER on B1 and B3 (expected at D near 0); R at D = 5 s, W = 2: one kill, its task
recovered in 92.5 s. The author saw these lines before writing s7; P2, P5 and P6 may be informed by them.

## 1. Question

Is Fabric v0.2 with the Moonshot PostgreSQL publication path (C-012-T002/T003) an adequate work plane for R-EP
shard epochs on the fleet available without interfering with other experiments? Below what epoch duration does it
stop being adequate? Where is the first bottleneck? It is C-008's D4 question (never executed; SUPERSEDED by
OP-NF2) asked of the replacement, with D4's bounds -- which the operator retained in OP-LC1 -- so the answer is
comparable with what D4 would have asked of git compare-and-swap.

Correctness of the protocol is not in question here (T002 tests, T003 demonstration). T004 measures COST, and checks
that correctness survives load (the gate in s6).

## 2. Rig

- Nodes: ubu001 (192.168.1.218) and ubu002 (192.168.1.219): ThinkPad X1 Carbon 5th, i5-7300U 2C/4T, 8 GB, NVMe,
  Wi-Fi only; Ubuntu 26.04, Python 3.14.4, psycopg2 2.9.11. Frozen Fabric v0.2 runtime 9c022347e at
  ~/fabric-runtime-moonshot. Workers: `python3 -m fabric worker --agent worker.<host>.moonshot --caps
  moonshot.epoch.v1 --executors script --poll-s 1 --idle-exit-s 900`, FABRIC_SCHEMA set to the point's schema.
- Not used, so as not to interfere: ubu003, ubu005, ubu006 host active seats (Cosmos, Bellerophon, Ensorain;
  infra/FLEET_HOSTS.md); ubu004 is not reachable from M2. Adding them is a later amendment, not part of this freeze.
- Database: the canonical cluster (M1, PostgreSQL 17.9 on Windows, max_connections 100, 6 in use at freeze).
  Each point runs in THROWAWAY schemas (fabric_b_<tag>, moonshot_b_<tag>), dropped after its raw rows are written.
  The canonical Fabric queue is not used: no other seat's task can be claimed, no benchmark task enters it. The
  canonical lease rows ubu001:cpu4, ubu002:cpu4 and spectrex5:cpu12 are held for the run (MWO-0004 R2).
- Coordinator on M2 (SPECTREX5): dispatch and publication with ONE reused publisher connection (the coordinator's
  per-publication connections exist so that races meet in the database; that is not what is measured), the
  validation pass and the report.
- Executor: moonshot.epoch.fabric_exec at 55c74f7cb, the code qualified in T003, already staged on both nodes: no
  git remote is contacted. Every chain's approved_code_sha is 55c74f7cb.

## 3. Arms

- N (adequacy sweep): W = 8 (4 workers per node); D in {60, 30, 10, 3, 1} s. OPERATING POINT: D = 30 s.
- N-scaling: D = 30 s with W = 2 and W = 4 (1 and 2 workers per node); with N at D = 30, W = 8 it gives scaling.
- R (recovery under load): D = 30 s, W = 8, 600 s; three SIGKILLs of an ubu001 worker at 1/4, 2/4 and 3/4 of the
  wall. No replacement is started (W falls from 8 to 5): recovery must come from Fabric's reaper and the
  remaining workers.
- S (coordination ceiling; descriptive, no pass/fail): K in {4, 16} simulated workers in ONE process on M2, each
  doing exactly the store calls a Fabric worker does (claim, 8 artifacts, finish) around a 1-iteration
  in-process epoch; 120 s each. Reported: throughput, per-stage medians, the first saturating stage.

## 4. Workload (synthetic.v1; no organisms, no science)

- Epoch size: work_iterations = round(D x r), r = the median single-process synthetic.v1 rate (iterations/s) of
  the two nodes, measured by `bench.py calibrate` once at launch and recorded BEFORE the sweep; trace_every =
  max(1, work_iterations // 16); checkpoint_bytes = 4096. Four workers share two physical cores per node, so
  measured epoch durations exceed D; they are reported.
- Chains: 2W per point, epochs_target 100000 (never completes; time-bounded), namespace "bench".
- Each point: wall W_t = 360 s (R: 600 s, S: 120 s). At the deadline no new task is dispatched; in-flight attempts
  finish and are published (drain <= 3D + 180 s).
- Loop (M2), every 0.2 s: publish what Fabric completed; a PUBLISHED epoch's chain gets its next epoch dispatched;
  any other classification re-dispatches the same epoch (a retry tag).
- Validation after each point (M2): every published epoch byte-verified against its lineage input; every 10th
  publication (publication_id % 10 == 0) replay-verified.

## 5. Metrics (bench_metrics.py, frozen with this file)

All from database timestamps (one clock, M1). Per attempt: execute = first artifact - start; transfer = last
artifact - first artifact; finish = end - last artifact; queue = start - task created; publication latency =
Moonshot classified_at - end. Per worker instance: gap = start of its next attempt - end of this one (Fabric's
worker re-claims at once after an attempt: with work queued, the gap is reap + touch + claim transactions).
P = PUBLISHED classifications at the end of the point (drain included).

- M1 coordination wall fraction = (sum gap + sum(transfer + finish)) / (that + sum execute).
- M2 retries per published = (Fabric attempts - tasks, when positive, + DUPLICATE + STALE + HALTED) / P.
- M3 = p95(gap) / median(execute).
- M4 abandonment rate = (abandoned + failed attempts + STALE classifications) / executed attempts.
- M5 bytes moved per published = (artifact bytes + task params bytes) / P.
- M6 database bytes per published = pg_total_relation_size of the point's two schemas / P.
- M7 tripwire projection = M6 x (P / W_t) x 30 days.
- Descriptive: throughput P / W_t; medians and p95 (nearest rank) of execute, gap, transfer, finish, queue and
  publication latency; DISAGREEMENT count; byte failures and replay mismatches; client-visible database errors.

Limitations stated now: execute includes the worker's worktree lookup and the executor's process start-up
(charged to execution, which flatters M1 slightly at small D); transfer is 8 per-artifact commits over Wi-Fi;
publication latency includes the loop's 0.2 s period; Arm S runs K threads in one Python process (the GIL caps
its client side, so its ceiling is a lower bound on the database's).

## 6. Frozen bounds (D4's, retained by the operator in OP-LC1)

At each Arm N point:

| Bound | Metric | Threshold |
|---|---|---|
| B1 | M1 coordination wall fraction | <= 0.05 |
| B2 | M2 retries per published epoch | <= 0.05 |
| B3 | M3 p95 gap / median execute | <= 0.10 |
| B4 | M4 abandonment rate | <= 0.01 |
| B5 | client-visible database errors (worker store_error lines + coordinator exceptions) | = 0 |

D4's B5 was "rate-limit responses = 0" for a git remote; its counterpart here is client-visible database errors.
Tripwire T1 (operational): M7 <= 1 GB per 30 days at the operating point.
Correctness gate (every point, every arm): byte failures = replay mismatches = DISAGREEMENT = 0.
B7 (Arm R): every killed worker's abandoned attempt has its task PUBLISHED within TTL + 2D = 90 + 60 = 150 s of
the kill.

Verdict per Arm N point: ADEQUATE iff B1-B5 hold, else RECONSIDER naming the failed bounds. Envelope T* = the
smallest swept D that is ADEQUATE with every larger swept D ADEQUATE ("none" if D = 60 s fails).

THE RECONSIDER-COORDINATION THRESHOLD (OP-NF2 s6): Fabric + PostgreSQL is adequate for the Moonshot work plane on
this fleet iff the operating point (D = 30 s, W = 8) is ADEQUATE and the correctness gate passes. If not, the
precise bottleneck -- the stage and transaction, from the stage medians and Arm S -- is documented BEFORE any
additional component is proposed.

## 7. Predictions (precommitted; each can be lost)

- P1: ADEQUATE at the operating point (D = 30 s, W = 8).
- P2: T* = 3 s: ADEQUATE at D in {60, 30, 10, 3}, RECONSIDER at D = 1 s failing B1 (informed by the smoke).
- P3: at W = 8, M1 falls roughly as 1/D (coordination per epoch about constant across D).
- P4: the correctness gate passes at every point.
- P5: Arm S sustains >= 10 accepted epochs/s at K = 16, and the first saturating stage is publication
  (classification), not Fabric's claim (informed by the smoke: ~14/s at K = 2).
- P6: B7 holds for all three kills.
- P7: throughput at D = 30 s scales to >= 0.7 x linear from W = 2 to W = 8 (four workers on two physical cores
  per node makes this losable).

## 8. Budget and stop rules

- Local, unpaid. Nodes: 7 points x 6 min + R 10 min = 52 min wall at <= 8 workers (<= 7 CPU core-hours); M2: S 2 x
  2 min and validation replays (<= 30 min CPU). Total < 10 core-hours, under MWO-0004 R2 (<= 16 per item, <= 48 per
  seat per rolling 24 h).
- A point stops early, recorded as a DEVIATION and never as a result to tune: a node unreachable for more than
  60 s; free RAM under 10% on a node; an unrelated process using more than one core on a node (pre-point snapshot
  in each point record); the database refusing connections. A failed bound is a result. A rerun happens only for
  an execution failure (host died, harness crash), with the reason recorded; never because a number looked wrong.
- A correctness-gate failure stops the run; it is the result.
- The window is announced in comms before the run and closed after it.

## 9. Not baseline data

The SMOKE points (disclosure above) and any harness test are excluded. Calibration is setup, recorded in the run.

## 10. Analysis code and order (frozen)

At the freeze commit, sha256 over LF-normalised bytes (comms/manifest.py):
- ops/campaigns/C-012/evidence/T004/bench.py  b0a3deb6422b188af846666e4651a120b53119257888ded27ffa72f403b7e9c7
- ops/campaigns/C-012/evidence/T004/bench_metrics.py  ef349d706c0dc8c9df44bf5e75205fc2eb64067fa8cbc62d741f96c288032c4b
- ops/campaigns/C-012/evidence/T004/test_bench_metrics.py  5f876904b6e38942423b4a2e4a7a3f89b3de8f55a0a268322aacd948e0976641
Order: calibrate; N D60 W8, N D30 W8, N D10 W8, N D3 W8, N D1 W8; N D30 W2, N D30 W4; R D30 W8; S K4, S K16;
`bench.py report`. Output: ops/campaigns/C-012/evidence/T004/<run-id>/ (per point: point.json, rows.json;
REPORT.json; calibration.json).
