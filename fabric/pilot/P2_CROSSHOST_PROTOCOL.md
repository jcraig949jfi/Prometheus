# P2 cross-host claim race: frozen protocol (committed before the run)

- **Frozen:** 2026-09-28, before execution.
- **Runner:** `fabric/pilot/run_p2_crosshost.py`.
- **Evidence:** `fabric/pilot/evidence/P2-crosshost.json`.

## Participants

- **ubu002:** `worker.ubu002`, the disposable fabric worker already online (started per #854; capacity 1).
- **ubu001:** `worker.ubu001`, one fabric worker process started by the runner with the same poll interval (5 s).
- Both run the same `fabric.store.claim` against the canonical store on M1.
- The tasks are synthetic (0.5 s sleep, tiny output) and require only `compute.cpu.light` plus the `synthetic`
  executor. Both workers advertise these, and this respects ubu002's "light tasks only" note (#857).
- No task names a host or target.

## Rounds

- **R1, single-task rounds (N = 20).** Each round starts when both workers are idle and the queue is empty:
  1. Submit exactly one task.
  2. Wait until it is terminal.
  3. Wait a random 0-6 s (random.Random(2026), so both pollers land at uniformly random phases).

  Because only one task exists at a time, every round is a race between the two hosts for that same durable
  Task.
- **R2, batch round.** Submit 30 tasks in one transaction burst, then wait until all are terminal.

## Pass criteria (all must hold)

1. Every task (R1 and R2) has exactly one Attempt, and that Attempt succeeded. No task has two Attempts, and none
   was lost or left non-terminal after a 300 s timeout.
2. There are no duplicate `claimed` events for any task.
3. In R1, each host wins at least 1 round. This shows both hosts were contending for the same single Task. A host
   that never wins means it never really raced, so the test is inconclusive rather than a pass.
4. In R2, each host completes at least 1 task.

## Reported (not gated)

- Wins per host.
- Claim latency (submit to `attempt_started`) per host.
- Nothing else: no throughput or fairness numbers are claimed.

## Out of scope

Throughput, fairness, and anything needing heavy compute on ubu002.
