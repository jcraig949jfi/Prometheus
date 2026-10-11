# INCIDENT 2026-10-08 -- 48H campaign lost ~45 of 48 hours to a silent stall (Cosmos, ubu003-623ec771)

Severity: CAMPAIGN-LOSS (no data corrupted; no holdout touched; $0). Detected 2026-10-10T18:37Z by the operator's
"Status & ETA?" -- NOT by Cosmos. Recorded 2026-10-11.

## Timeline (UTC)
- 10-08 05:26  campaign start (lease acquired, ttl 7200 s).
- 10-08 08:10  hour-3 status (the last one).
- 10-08 08:19  EXP-04 launched as `nohup python - <<EOF ... EOF &` with a spawn Pool (and commit 859e18741).
- 10-08 08:19  waiter started: `while kill -0 132777; do sleep 15; done` (watches the PID only). Cosmos ended its
               turn waiting for that waiter's completion notification.
- 10-08 10:03  lease expired (never renewed).
- 10-10 05:26  campaign hard stop passed. No final handoff.
- 10-10 18:37  operator asks for status; Cosmos finds 0 rows, kills PID 132777 and its workers.

## Mechanism
1. Spawned workers re-import __main__ from its file. __main__ was `<stdin>` ->
   `FileNotFoundError: .../cosmos-c4/<stdin>` in every worker.
2. multiprocessing.Pool replaces dead workers silently. The parent waited forever on imap_unordered; workers
   crashed and were respawned 4,683,366 times (run.log 5,175,119,707 bytes, sha256 f90bdaee...8685f; head and
   receipt kept in COSMOS_HOME/incidents/2026-10-08_exp04_stdin_spawn/). Load ~3 for 58 h.
3. The waiter judged LIVENESS (PID alive), not PROGRESS (rows written). It could never fire.
4. Process hole (the real cause of the loss): Cosmos had no independent periodic check. The hourly status,
   lease renewal and no-idle policy all depended on Cosmos being woken, and the only wake signal was the waiter.
   A live process producing zero science looked identical to a slow experiment.

Prior art ignored: EXP-03 (10 minutes earlier) had been launched correctly from a script file.

## Repair (cosmos/c4-v03; tested)
- prometheus/cosmos/supervise.py (c7e784d3f, 6a4431724, 402c5a938):
  - run_jobs refuses a stdin / -c main before any worker exists (SpawnUnsafe);
  - ProcessPoolExecutor (spawn): a dead worker ends the run FAILED instead of a silent respawn loop;
  - PROGRESS.json separates last_result_utc (science) from heartbeat_utc (liveness);
  - launch: own process group; STALLED = no new result within the stall limit even if alive; kill the group,
    record, resume from checkpoint up to max_restarts, else terminal FAILED; exit code 0 only on DONE.
- prometheus/cosmos/tests/test_supervise.py: 11 failure-injection tests, including a REPLAY of this incident
  (stdin spawn Pool under the watchdog -> STALLED and the session emptied in < 60 s) and hung / dying / raising
  jobs.

## Second stall, caught (2026-10-11)
The EXP-04 relaunch under the new runner stopped at 60 = 3 workers x 20 rows with a live parent and no workers:
CPython's ProcessPoolExecutor replaces a worker retired by max_tasks_per_child only on a later submit(), and every
job had been submitted up front. Diagnosed live from the process tree within ~1 minute; reproduced in isolation
(2 workers x 2 tasks: 4/10 done, 6 hung); fixed by incremental submission (402c5a938) with a regression test. The
watchdog was left to act on the live run: see EVENTS.jsonl in COSMOS_HOME/c4_exp04 (outcome recorded below).

Outcome: the watchdog declared STALLED at 05:55:05Z (612 s after the last result, n_done 60/300), killed the
process group, and restarted; the restart loaded the fixed code (402c5a938, committed 05:48Z) and resumed at 60;
DONE 300/300, 0 job failures, at 05:58:50Z (final verdict DONE, restarts 1). No human or agent action between
the stall and the recovery.

## Rules adopted
- Never launch a multiprocessing job from stdin or -c. Use a module (`python -m`) under `supervise launch`.
- Every long job runs under `supervise launch --stall S`; any waiter waits on the LAUNCHER (which exits on DONE /
  FAILED / STALLED), never on a PID.
- While a job runs, an independent monitor reports progress (rows and time since last result), so a stall surfaces
  within the stall limit even if the launcher itself misbehaves.
- An autonomous window is only claimed after a reliability test shows unattended progress (operator, 2026-10-11).
