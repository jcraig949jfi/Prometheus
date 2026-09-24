# Nestor status

Currency: 2026-09-24. The operator's final Cycle-9 rulings have all been applied, and all
12 pre-freeze gates pass. **STOPPED BEFORE FREEZE** on a new scientific-validity defect
(C9-D14), as the ruling requires. Nothing is frozen, no final hash is written, no
production observatory exists, nothing is launched.

Read `campaigns/z80atlas-verify-2026-09-22/PREFREEZE_STOP_2026-09-24.md` first.
Rulings: `prompts/2026-09-24_cycle9_final_rulings/DIRECTIVE_VERBATIM.md`.
Branch `nestor/s1-forensics-2026-09-23` is pushed; main was last merged at d64e85e4e.

Open for operator:
1. C9-D14: choose an H3 certificate option, or withhold H3.
2. Authorize building the launch pipeline (runner, H1/H3 adjudicators, report and
   audit). It does not exist and must be built before freeze.
3. Confirm how same-stratum H2 candidates are labelled.
Manifest: 1,200 runs, 6.7 wall-hours at 6 workers.

---

## Previous state (2026-09-23, before S1-S4)


Currency: 2026-09-23, written at the close of the session that finished the Cycle-9
repair pass, immediately before an operator-requested context reset.

**seat state:** PRODUCTIVE. Not blocked. Holding at a deliberate stop before the
Cycle-9 freeze, awaiting operator review of the strategy.

**what it asserts:** PRESENT, ACTIVE, PRODUCTIVE (two campaigns closed or frozen, one
built and gated), VALID for the claims in `FINDINGS.md` and for nothing else.

**workspace:** worktree `nestor-sidequest-graphworld`, branch
`nestor/sidequest-graphworld-2026-09-14`. Merged to `main` on 2026-09-23.

---

## Read this first after a reset

`roles/Nestor/RESPONSIBILITIES.md` section 0 lists the bootstrap order. Short version:

1. `FINDINGS.md` -- what is known, what was withdrawn.
2. `prompts/2026-09-23_next_sequence/DIRECTIVE_VERBATIM.md` -- the operator's words.
3. `campaigns/z80atlas-verify-2026-09-22/STRATEGY_POST_RESET.md` -- the plan, **proposed
   not approved**.

## Where each campaign stands

| campaign | state |
|---|---|
| `cw01-2026-09-17` | cycles 1-8 closed. Cycle 8 measured accessibility: answer-before-read plateau, 4-edit valley, a single witness fixes in 10 of 12 runs, partial seeded gateway |
| `z80atlas-2026-09-19` | **FROZEN 2026-09-22.** 23,471 runs, 0 failed, 0 voided. Observatory is read-only forever. `REPORT.html` rev 2 passes its own audit, 40 checks, 0 failed |
| `z80atlas-verify-2026-09-22` | **BUILT, GATED, NOT FROZEN, NOT LAUNCHED.** Repairs P-1..P-10 in, five gates exit 0, calibration 10 of 10, manifest 252 bundles / 752 runs |

## The stop line

No grammar, manifest or protocol hash is written into the Cycle-9
`PREREGISTRATION.md`. No production observatory exists. Calibration output is named
`CALIBRATION_PREFREEZE.json` so it cannot be mistaken for the freeze gate having passed.

**Freeze and launch require an operator instruction and must never be inferred.**

## Next executable action

Begin **S1**, the bounded forensic mining pass, per section 2 of the strategy. Three
products, no general descriptive report:

- **A** the replication failure funnel for every non-`PAIR_EXECUTION` random-start run,
  which decides the shape of the exploratory campaign;
- **B** H4 extinction forensics on `64dea50f417efb02-s1203-tL-a0` and its control,
  which decides whether enlarging H4 is worth buying;
- **C** deeper mining of the 1,031, which calibrates P-11's threshold.

Known obstacle to name before starting A: two funnel steps -- "executed self-location"
and "attempted BIRTH" -- are **not separately counted** in the frozen record;
`world_op_calls` is a single total. Either re-run a sample with added counters into a
**new** directory, or report a partial funnel. Do not discover this mid-analysis.

## Open questions carried to the operator

1. The Cycle-9 manifest uses 11% of its envelope. The directive resolves this: enlarge
   H2, H3 and H4 unevenly, leave H1, target 5-8 wall hours.
2. C9-D01 scope: H2 is a pair-tape propagation test, because all 1,031 admissible
   spontaneous replicators are `PAIR_EXECUTION`. Confirmed as the operator's own reading
   in the 2026-09-23 directive.
3. H4's endogenous arm ran 4x faster than its control in smoke. Product B resolves it.

## Monitors owned or fed

None. No row in `roles/base-role/MONITORS.md`. No background process is running; the
72-hour campaign completed and its scheduled task is finished.
