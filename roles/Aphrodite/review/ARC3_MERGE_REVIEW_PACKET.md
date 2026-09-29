# ARC3 CLOSE -- MERGE / REVIEW PACKET (Aphrodite, MWO-0001)

Written 2026-09-29. Proposes merging aphrodite/arc3-2026-09-28 into main through normal review.
It proposes NO new wave: MWO-0001 says a future MWO reviews the close.

## 1. What is being merged
- Branch: aphrodite/arc3-2026-09-28.
  - ARC3 close content: 889bf8ddd.
  - It then merged origin/main 98ed64ca3 (db0bcad58, clean) and added the MWO-0001 adoption commits (WORK_STATE,
    NEXT_SESSION rewrite, this packet, ops/threads TH-018..021, ops/campaigns/C-003).
- The branch carries ALL unmerged Aphrodite work since main a71666665 (2026-09-26), four lines in one lineage:
  - A17 campaign (was aphrodite/a16-campaign-2026-09-26);
  - frontier program (aphrodite/frontier-2026-09-27);
  - compounding program (aphrodite/compounding-2026-09-27);
  - ARC3.
  Merging this branch makes those three older branches redundant.
- Scope of paths: roles/Aphrodite/** plus the new files ops/threads/TH-018..021.md and ops/campaigns/C-003/. No
  other seat's path is touched. The merge into main is clean (git merge-tree).
- Size: about 330 files, about 383k inserted lines, mostly JSON evidence rows. The largest is
  roles/Aphrodite/science/compounding/rb2/RB2_CENSUS_ROWS.json at 17.9 MB (under GitHub's 100 MB limit). The
  reviewer may ask for large row files to be trimmed or moved to LFS. None is required to reproduce a verdict except
  as listed in each amendment.

## 2. Claims of record (verdicts exactly as frozen; nothing retroactive)

| # | Claim | Evidence | Limits |
|---|---|---|---|
| 1 | Under the CONSTRUCTED recurrence test, G1 is a recurrent stepping stone. G1_RECURRENT_STEPPING_STONE = YES (n = 10 fillable of 12; k = 6). REUSED + CAPABILITY: G1 7, shams 8/9/10, controls 0/0/0. Sign test p = 0.0078 vs the no-composition, PRISTINE and OFF controls. | engine/AMENDMENT_23*, engine/A23_C3R2C/A23_C3R2C_RESULT_2026-09-28.json (includes the principal's attack) | Mechanism only. Capability is budget-relative (walk cliff). The donor mostly recovers the planted motif (7 of 8 G1 selections are literally the motif). |
| 2 | G1 is NOT established as privileged. GENERIC = 3/3: three clean shams pass at similar or higher rates. W8: under natural lineage, the frequency-matched sham ({H} + v) recurs 3x more than G1. | same; science/arc3/w8_lin_generator/REPORT.md s0 and A3 | none |
| 3 | LIN (lineage) task generation recurs repeatedly, about 14x i.i.d. (genuine P_reuse .135 vs .008-.010), but FAILS W1's "natural recurrence exists" criteria: dup .43 > .35; genuine X_G1 spread 3/24 seeds. | w8 REPORT s0, s2 | W1 and W8 differ on the edit law (root edits): P_reuse .45 vs .21 |
| 4 | Recurrence x visibility. Where recurrence arises naturally, it lands in families PRISTINE cannot reach (p0 .77 vs .61 at 250k). The 250k window holds about 2% of families in every generator. A natural-world null at 250k is predicted by the instrument, not by an absence of recurrence. | w8 REPORT s3; w2_learnability REPORT | Window model is equivalent-hit only; ignores Q2 |
| 5 | Predecessor assays: C3 (A20) UNTESTABLE; C3R (A21) INVALID_DESIGN_DEFECT; C3R2 (A22) UNTESTABLE. | engine/A20..A22 | The seat's own design/supply defects; the countermeasure is a pre-freeze supply screen |

Unchanged: all BOUNDED_RSI labels and the S4 ACCEPTED disposition. Campaign 1 is FROZEN and UNRUN. The DSL is not
extended.

## 3. What a reviewer should attack first
1. Motif recovery (claim 1). Does selection accuracy among about 60 compositions from 2 validation families count as
   more than recovering a planted motif? A cheap check is backlog T52, the validation-multiplicity dose response.
2. Budget-relativity. The capability ratios are walk-cliff quantities. T53 would re-score them D-stratified.
3. Instrument versions. E-011 ran on the frozen, unrepaired T4. W7 found a query-window mismatch for about 1.7% of
   families. T47 is the bridge.
4. Worker isolation is imperfect. Workers were fresh-context subagents sharing the filesystem. Six REPORTs were
   deposited verbatim by the principal (provenance in WORKER_MANIFEST.md).

## 4. Id mapping (MWO-0001 s4; aliases only, nothing renamed)
Threads:
- TH-018 (thr-4b608194554f): abstraction compounding
- TH-019 (thr-5fb60bba1e73): recurrence x visibility
- TH-020 (thr-71318d165e06): second-order / representation
- TH-021 (thr-1b0c5ac499ae): instrument validity (method)

Campaign: C-003 = ARC3 (CLOSED).

Experiments:
- E-008 = AMENDMENT 20 (C3)
- E-009 = AMENDMENT 21 (C3R)
- E-010 = AMENDMENT 22 (C3R2)
- E-011 = AMENDMENT 23 (C3R2-CONFIRM)

Tasks: W1-W8 (pre-Fabric; no tsk-* ids). Canonical ids are derived from genesis commit 32c3e52fe;
ops/tools/thread_check.py reports threads=21, failures=0.

## 5. Defects found at adoption (MWO-0001 s12) -- evidence, not fixed here
Exposed by Artemis #871 (R-08, R-11), a worker's claim that the principal verified 2026-09-29 at base 889bf8ddd.

| Location | Expected | Observed | Science blocked? |
|---|---|---|---|
| engine/run_s3s4.py L391 | S4 condition 4 ("hostile evaluation") computed from data | constant True, justified by a comment | S4 labels are historical and accepted by the operator. No re-label. Flag for review. |
| engine/run_s3s4.py L420 | S4 condition 8 ("no donor state") checked | constant True (membrane argument) | same |
| engine/run_s3s4.py L245, L317 | positive control independent of the treatment | the POSITIVE_CONTROL schema (acc + {H}) equals the derived schema; the code reports the equality | same; the positive control did not discriminate in S4 |
| engine/a16.py L490, and a17.py L581 (copied from a16) | donor adjudication validity computed | constant True | A16/A17 outcomes were UNTESTABLE or BRSI = NO; no positive rests on it |

None of these touches E-008..E-011: their verdicts come from a20_c3.stage_report. a18 imports a17 for engine utilities only, not for the flagged field. Any re-adjudication of S4 is an
operator-level question under MWO-0001 s7 (1); the seat is not doing it.

## 6. Operator decisions (non-blocking)
- DSL fork for TH-020: (A) a versioned promotion world W5P, or (B) parked until TH-019. Default (B).
- Whether a future MWO authorises the TH-019 donor stage: T51 per W8 s6, about 16 core-hours on M4 under a Fabric
  lease.

## 7. Requested action
Review and merge aphrodite/arc3-2026-09-28 into main (normal review; any reviewer). After the merge, delete the
three superseded Aphrodite branches listed in s1 (the reviewer's call).
