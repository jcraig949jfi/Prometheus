# C-012-T004 run R1 -- Fabric + PostgreSQL as the Moonshot work plane (preregistered benchmark)

Preregistration: ../../../prereg/T004_PREREG.md, FROZEN at 2f4b38ef0 (sha256 fa2569699470...) before any data; analysis
code ../bench_metrics.py and driver ../bench.py at their frozen hashes (unmodified; diag_storage.py and R1/run_r1.py
only wrap or sequence them). Window 2026-10-10T09:37Z-11:13Z on ubu001 + ubu002 (comms #2020, #2029, #2039, #2040).

Files: calibration.json (1.70M synthetic.v1 iterations/s per node, single process); RUN_LOG.jsonl (point order, M2 load
before/after each point, the Arm S deviation); <point>/point.json + rows.json (every Fabric attempt with its timestamps,
artifact bytes and Moonshot classification); REPORT.json (`bench.py report`); DIAG_STORAGE/ (diagnostic, below).

## Results against the frozen bounds (Arm N; B1 <= 0.05, B2 <= 0.05, B3 <= 0.10, B4 <= 0.01, B5 = 0)

| Point | Published | Epochs/s | M1 coord. fraction | M2 | M3 p95 gap/med exec | M4 | Verdict |
|---|---|---|---|---|---|---|---|
| D60 W8 | 32 | 0.089 | 0.00065 | 0 | 0.00017 | 0 | ADEQUATE |
| D30 W8 (operating point) | 48 | 0.133 | 0.00154 | 0 | 0.00038 | 0 | ADEQUATE |
| D10 W8 | 116 | 0.322 | 0.00423 | 0 | 0.00135 | 0 | ADEQUATE |
| D3 W8 | 338 | 0.938 | 0.01486 | 0 | 0.00500 | 0 | ADEQUATE |
| D1 W8 | 838 | 2.327 | 0.05588 | 0 | 0.30632 | 0 | RECONSIDER (B1, B3) |
| D30 W2 | 25 | 0.069 | 0.00506 | 0 | 0.00150 | 0 | ADEQUATE |
| D30 W4 | 42 | 0.117 | 0.00361 | 0 | 0.00126 | 0 | ADEQUATE |
| R D30 W8 (3 kills) | 65 | 0.108 | 0.00208 | 0.046 | 0.00072 | 0.044 | (B4 by design: induced kills) |

B5 (client-visible database errors) = 0 at every point. Correctness gate: PASS -- 1,504 published epochs, all
byte-verified, 146 replayed on M2, 0 replay mismatches, 0 DISAGREEMENT.

- THE RECONSIDER-COORDINATION THRESHOLD: the operating point (D = 30 s, W = 8) is ADEQUATE and the gate passes ->
  Fabric + PostgreSQL is adequate for the Moonshot work plane on this fleet.
- Envelope T* = 3 s.
- Stage medians (D = 1 s, W = 8): claim gap 0.027 s (p95 1.04 s), artifact transfer 0.084 s (8 commits over Wi-Fi),
  finish 0.016 s, publication latency 0.142 s (p95 0.245 s), execution 3.39 s for a nominal 1 s epoch (4 workers on 2
  physical cores). The D = 1 s failure is the worker's 1 s idle-poll QUANTUM: a worker that finds the queue
  momentarily empty sleeps a full poll interval, and the queue empties because each chain's next epoch is dispatched
  only after its previous one is published (one epoch in flight per chain; ~0.14 s publication + the 0.2 s loop).
  Not PostgreSQL transaction cost. Levers, not built: more chains per worker, a shorter poll, event-driven claims.
- Bytes moved per epoch (M5) 11.8-14.3 KB (artifacts + task params).

## Predictions (precommitted in s7)

- P1 operating point ADEQUATE: HELD.
- P2 T* = 3 s, RECONSIDER at D = 1 s failing B1: HELD (it also failed B3).
- P3 M1 about proportional to 1/D (coordination per epoch about constant): HELD. Per-epoch coordination, the
  median claim gap + transfer + finish, is 0.105 / 0.098 / 0.104 / 0.100 / 0.127 s at D = 60 / 30 / 10 / 3 / 1;
  M1 x D = 0.039 / 0.046 / 0.042 / 0.045 / 0.056 is roughly constant too, but it is NOT seconds of coordination
  per epoch, because execution runs longer than D on shared cores (a 30 s epoch takes ~80 s at W = 8).
- P4 correctness gate everywhere: HELD.
- P5 Arm S >= 10 epochs/s at K = 16, publication the first saturating stage: NOT TESTED (Arm S deferred, below).
- P6 B7 for all three kills (recovered within TTL + 2D = 150 s): LOST -- recovered after 189.6, 131.7 and 124.6 s.
  Recovery is three serial delays: Fabric's 90 s heartbeat TTL before the dead attempt is reaped (95-100 s
  observed), waiting for a free worker (all busy; the requeued task is first in line), and a full re-execution (80 s
  for a 30 s epoch at W = 8 on shared cores). B7 assumed a re-execution of about D and no wait.
- P7 throughput scales >= 0.7 x linear from W = 2 to W = 8: LOST -- 0.069 / 0.117 / 0.133 epochs/s at W = 2 / 4 / 8
  (ratio 0.48). CPU-bound, not coordination: two physical cores per node; M1 <= 0.005 at every W.

## Tripwire T1 (operational): FAILED, and why it cannot pass at that rate

M7 at the operating point = 2.6e10 bytes per 30 days (bound 1 GB). R1 measured database bytes only as a point total
(schemas are dropped), so a DIAGNOSTIC point (DIAG_STORAGE/STORAGE.json; not preregistered; 45 epochs through the
frozen harness, per-relation sizes measured before the drop) attributes them: 65 KB per epoch at that size including
fixed per-table overhead; the marginal cost from R1 (D = 1 vs D = 30) is about 42 KB. Fabric's per-attempt record is
about two thirds: blobs 13.1 KB, tasks 11.7 KB (the input checkpoint travels inline as base64 in the task params),
events 7.6 KB (13 events per attempt, 8 of them artifact_added), artifacts 4.0 KB, attempts 3.5 KB. Moonshot's is
about a sixth: content-addressed objects 10.7 KB (the 4 KB checkpoint), attempts 2.5 KB, publications 2.2 KB,
results 2.0 KB. The 4 KB checkpoint is stored three times. At the operating rate (0.133 epochs/s, ~345,000 epochs in
30 days) 1 GB allows under 3 KB per epoch -- less than one copy of the checkpoint, so T1 (inherited from D4, where it
bounded git repository growth) is unattainable at that rate on any transport that keeps the checkpoint. What the
program would need to decide: retention (prune Fabric's artifact copies after Moonshot classifies them -- Fabric's
owner), checkpoints by reference (contract item N1), and whether the fleet runs at the operating point 24/7.

## Deviations (recorded, not results)

- Arm S (the M2 coordination ceiling) NOT RUN: the operator started experiments on M2 at ~09:30Z (Pan's record
  140d95927); M2's CPU was 19-46% before the points (RUN_LOG.jsonl). It runs later under this preregistration if M2
  is idle; P5 stays open until then. spectrex5:cpu12 was not held during the node arms (M2 footprint: the coordinator
  loop and replays, about one core).
- The prereg's stop rule for a correctness failure is enforced by checking each point's gate as it ended (the runner
  only stops on a harness failure); no point failed it.
- Each point took longer than estimated (drain + replay validation): window extended to ~11:30Z (#2029), closed 11:13Z.

N4 for the Observatory (descriptive, post-freeze): wasted execution under induced worker loss = 72.8, 1.2 and 1.2 s
for the three kills (two landed just after their attempt started) = 1.6% of all execution in Arm R.
