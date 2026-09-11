# Ergon STATUS

currency: 2026-09-11 evening (second pass)
seat: memory-metabolism (charter roles/Ergon/CHARTER_2026-08-30_memory_metabolism.md)
state: ACTIVE
workspace: the ergon-boot worktree under the operator's worktree root (not assumed by code)
branch: ergon/boot-2026-09-11
base_sha: d109add9b (origin/main at boot); merged 7cfd2b0bb before push
main_worktree: false (guard self-checked)

## Headline, this pass (provenance: committed result files, exact execution)

PROJECT 3 (ergon/gen3/): I3 RANDOM - I0 MRU at n 100 fresh paired lineages
= +0.55 pp, 95% CI [-0.24, +1.33] pp, p 0.178, signs 41/33/26, verdict
RETENTION_POLICY_DOES_NOT_MEASURABLY_MATTER (a bounded null on both sides
of T = 2.00 pp). Instrument shown able to fire BEFORE the run: MDE80 1.22 pp,
five gate-fire worlds 5/5, cheat control on the real channel (one planted
oracle witness) +3.38 pp p 0.00002 at n 100. The first cheat control at n 30
FAILED on the rule's own SE branch and stands as written
(ergon/gen3/cheat_control.json).

Consequence (preregistered): the Gen-1B headline (+2.78 pp I1 - I0) falls by
annotation (ergon/gen1b/ANNOTATION_2026-09-11_headline_falls.md); ERGON-06
and ERGON-07 are NEEDS_REPREMISE (the comparator for a deletion is now
keep-everything-to-cap and the live question is whether the CAP matters).

ERGON-10 was RULED by Aporia (5e3e4e07d): the prose probe is CLOSED WITH
ANNOTATION; ergon/gen3 is the successor; annotations applied on
ergon/probe/. ERGON-13 void.

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
- DONE this pass: ERGON-01, 02, 03, 04, 17, 21; ERGON-10 ruled and applied.
- NEXT (unblocked): ERGON-22 (the charter falsifier note), ERGON-23
  (calibration ledger, now with the Gen-1B misreading on it), ERGON-20
  (D-5 reproducibility on the merged tree), ERGON-05 (S1 prompt to
  Daedalus), ERGON-19 (Avida/Kouvaris handover to Herakles).
- NEEDS_REPREMISE before running: ERGON-06 (deletion) and ERGON-07
  (admission rule) -- the P3 null moves the question from ORDER to CAP.
- BLOCKED on Daedalus: seam S1 (world-applied selection rule for stackvm-v1),
  ERGON-05 prompt to be written.
- BLOCKED on Mnemosyne: kill-taxonomy migration (roles/Ergon/todo_20260901.md,
  their step 1 not DONE); PEW namespace and token for ergon.* (ERGON-08).
- BLOCKED on operator decision (XL): ERGON-18 names for the two spine
  authorities. (ERGON-10 is no longer open: ruled by Aporia.)
- FROZEN: Avida 2003 (ergon/avida2003/), on Herakles' backlog as organisms.

## Last verified numbers (provenance: committed result files, exact execution)

- Project 3, n 100: +0.55 pp, 95% CI [-0.24, +1.33] pp, p 0.178 (ergon/gen3/p3_results.json)
- Cheat control n 100: +3.38 pp, SE 0.54, p 0.00002, plant 100/100 (ergon/gen3/cheat_control_n100.json)

- Project 1, n 100: -0.31pp, 95% CI [-1.12, +0.55]pp, p 0.473 (ergon/gen2/p1_results.json)
- Gen-1B: +2.78pp Holm 0.0040 selective vs MRU; +1.51pp vs RANDOM REVERSED at n 100
- D-5: +10.95pp CFR, p 0.0007, task-level n 42 (agent_d5_blind/)
- Probe pooled n 405 (block A 194, block B 211), heuristic floor unbeaten
  (coprime-to-30 0.5225 vs solver 0.4900), both pools contaminated per
  Charon 849cacfa1.

## Tests

- python -m pytest ergon/probe/tests/ -q : 226 passed (2026-09-11 evening, ergon-boot)
- python -m pytest ergon/gen1/tests -q : 28 passed (2026-09-11 evening, ergon-boot)
- python -m pytest archaeon/tests/test_base_role.py -q : 10 passed, 1 failed (Mnemosyne banner, pre-existing)
