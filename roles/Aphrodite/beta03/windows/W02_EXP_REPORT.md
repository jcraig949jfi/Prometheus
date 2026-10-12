# W02 (EXP) REPORT: E1/E2 EXECUTION UNDERWAY; INSTRUMENT QUALIFICATION FOR THE STRUCTURED WORLD

Beta-03 (C-011), 2026-10-08 09:05-13:05Z (closed 13:10Z).

## 1. Execution
- **Supply** (outcome-free): blocks A and B were foundried by 11:43Z.
  - Usable: **A 24/24, B 22/24.** Seeds 103 and 105 failed the extras rule.
  - **E1 therefore has 22 pairs**, >= 18 (E1), and >= 20 (the Hestia kill criterion).
- **E1/E2 chain** (started 11:43Z):
  - E1 donors: done.
  - E2 g12 / I_0 donor jobs: done.
  - E1 libraries frozen + hashed; E1 starts + common residual frozen (12:35-13:04Z).
  - E1 recipients were running at 13:04Z.
- **Compute-cap stop (13:10Z).** The rolling 24 h estimate was about 38.5 core-h at 13:07Z:
  - foundry 05:10-11:44, about 26.3 at 4 workers;
  - lead smokes, pilots and known answers, about 6.7;
  - chain, about 5.5.
  Finishing E1 (about 6) plus E2 scoring (about 4) would exceed 48. The chain was stopped with TaskStop (no python
  process survived), and relaunched for **E1 only** (recip resumes from completed rows -> score -> report).
  **E2 score/report is deferred** until the 05:10Z-onward foundry hours roll off (after about 05:15Z on 2026-10-09).
  This is a resource hold (R2), not a scientific gate, and no outcome was inspected.

## 2. Instrument qualification (exposed data only; W06/W08 work advanced)
- **W9-H discovery pilot** (ecology lead @64d51f5cb, exposed seeds 0-2, 1.30 core-h):
  - gen-1 donors derive 0 schemas at 30k and 300k;
  - the **known-positive oracle level-1 control never makes a true depth-2 composition a candidate.**
- **W5P re-certification of W9-H:** 31/47 agree. W5P certifies 28, covering all 8 compositions.
- **O1 observation repair** (representation lead @61d55a914; criterion frozen @78e6aad68 before runs; 1.12 core-h):
  **O1_FAILS 0/3.**
  - CANDIDACY breaks on 2 seeds.
  - SELECTION breaks on 1: the true composition (mean saving 5,524) loses to a bare re-expression P({H}) (7,862).
  - It is not a cheap repair.
- **Disposition: E5-H (structured-world R8) = INSTRUMENT_UNVALIDATED** (directive s7 / Outcome C). Not launched.
- O1 code stays off the coordinator branch (E5-N freezes W5P donor.py).

## 3. Frozen during W02 (before any E1/E2/E5 outcome)
- **E5-N** (natural-world R8 under promotion) + W5P decisions D1-D5 + the E6 attack. Red-teamed: 1 BLOCKER
  (renaming-copy attribution) + 5 MAJOR, **amended A1** pre-data. K5a-K5d PASS.
- **Close decision table** (beta03/MIGRATION_DESIGN_DRAFT.md s5; sha in STATE.close_decision_rule):
  CONTINUE / MIGRATE / REPAIR conditions, frozen before outcomes.
- **Migration design draft** (TFS-1 typed functional substrate; transplant known-answers; M0-M3).

## 4. Next (W03 DEV, 13:05-17:05Z)
1. E1 completes -> E1_REPORT.md.
2. E2 score/report and E5-N wait for the compute roll-off (about 05:15Z, 2026-10-09).
3. W03 DEV work: the E6 runner for both E5-N branches (mechanical, pre-registered); red-team of the migration draft;
   receipts and ledger.
