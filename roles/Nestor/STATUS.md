# Nestor status

Currency: 2026-09-24. S1 through S4 of the operator directive of 2026-09-23 are COMPLETE.
**Stopped for operator review after S4, as directed.** Nothing is frozen, no final hash is
written, no production observatory exists, nothing is launched.

Directive: `prompts/2026-09-23_s1_s4_execution/DIRECTIVE_VERBATIM.md`.
Workspace: worktree `nestor-s1-forensics`, branch `nestor/s1-forensics-2026-09-23` (pushed,
NOT merged to main - the directive asks for review first).

Read in this order: `campaigns/z80atlas-verify-2026-09-22/S4_CANDIDATE.md` (the review
document), then `campaigns/z80atlas-forensics-2026-09-23/{S1A_FUNNEL,H4_AUTOPSY,S1C_P11_REASSAY}.md`,
then FINDINGS section E.

Headline: P-11 keeps 57 of the 1,031 (max causal depth 2); non-pair physics never
searched (zero births, so zero mutation); A-4 withdrawn; candidate manifest 1,352 runs,
7.6 wall-h (5.95 without H4).

Open operator decisions: H4-0 vs H4-R; H2 16-seed decision rule; H3 certificate edges
(C9-D11); P-11 authorship reading; then freeze (S5) and launch (S6).

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
