# Ergon STATUS

currency: 2026-09-11T10:40Z
seat: memory-metabolism (charter roles/Ergon/CHARTER_2026-08-30_memory_metabolism.md)
workspace: F:\Prometheus-worktrees\ergon-base-role (the operator's host convention; not assumed by code)
branch: ergon/base-role-adoption-2026-09-11
base_sha: f727dfb1f3928c0269510d508dc732a992e7fb50
main_worktree: false (guard self-checked)

## Long-running processes owned by this seat

| task | state | since | last tick | what every tick in the uncommitted ledger region (09-05..09-11) did |
|---|---|---|---|---|
| PrometheusCampaign | DISABLED 2026-09-11T10:21:57Z | 2026-08-21 | 2026-09-11T10:14Z | adopt pooled population, raise NoResidueError, exit 0; 0 rows (199 ticks) |
| PrometheusColdbandDrip | DISABLED 2026-09-11T10:21:58Z | 2026-08-22 | 2026-09-11T08:38Z | "complete" per block, 0 rows (96 ticks) |
| PrometheusColdbandM30 | DISABLED 2026-09-11T10:21:59Z | 2026-08-22 | 2026-09-11T09:52Z | "collected +0/0, coverage 400/400", 0 rows (289 ticks) |

None of the three runs. All three ran from the canonical checkout (D-23 s6
violation) and exited 0 without work (base rule 7 violation: dormancy was
not visible). Evidence: roles/Ergon/ops/SCHEDULED_TASKS_DISABLED_2026-09-11.txt
and the ledgers committed on this pass. Re-arming is ERGON-13 and waits on
ERGON-10 (the probe's disposition, not this seat's call).

## Open items, by state

- RUNNING: nothing.
- NEXT (unblocked): ERGON-02/03/04/17 -- preregister and run I0 MRU vs I3
  RANDOM at n 100 with MDE, gate-fire and cheat control first. Local exact
  execution, no spend, ~27 s per lineage.
- BLOCKED on Daedalus: seam S1 (world-applied selection rule for stackvm-v1),
  ERGON-05 prompt to be written.
- BLOCKED on Mnemosyne: kill-taxonomy migration (roles/Ergon/todo_20260901.md,
  their step 1 not DONE); PEW namespace and token for ergon.* (ERGON-08).
- BLOCKED on operator decision (XL): ERGON-10 probe disposition; ERGON-18
  names for the two spine authorities.
- FROZEN: Avida 2003 (ergon/avida2003/), on Herakles' backlog as organisms.

## Last verified numbers (provenance: committed result files, exact execution)

- Project 1, n 100: -0.31pp, 95% CI [-1.12, +0.55]pp, p 0.473 (ergon/gen2/p1_results.json)
- Gen-1B: +2.78pp Holm 0.0040 selective vs MRU; +1.51pp vs RANDOM REVERSED at n 100
- D-5: +10.95pp CFR, p 0.0007, task-level n 42 (agent_d5_blind/)
- Probe pooled n 405 (block A 194, block B 211), heuristic floor unbeaten
  (coprime-to-30 0.5225 vs solver 0.4900), both pools contaminated per
  Charon 849cacfa1.

## Tests

- python -m pytest ergon/probe/tests/ -q : 226 passed (2026-09-11, this worktree)
- python -m pytest ergon/gen1/tests -q : 28 passed (2026-09-11, this worktree)
