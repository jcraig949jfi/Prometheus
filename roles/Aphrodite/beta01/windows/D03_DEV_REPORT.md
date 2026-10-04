# D03 -- DEV WINDOW 3 REPORT: repair/design packet

C-006 (C-P2B-APH-BETA-01), cycle 3, DEV. Threads TH-021 / TH-018. Evidence tier 2. Apparatus v2b-1 -> **v2b-2**.

## 1. Information bottleneck after TEST-2
T02 closed MEASUREMENT_FAILED because its PC_ONE control had a wrong known answer, as follows:
- In 2 replicates its two SAME families were extensional duplicates.
- In 2 others, START already solved SAME #2.
The earliest failed rung was the CONTROL specification, plus an unscreened property of the supply: transfer-family
distinctness.

## 2. Changes (v2b-2)

| Change | File | What it does |
|---|---|---|
| Extensional distinctness screen | engine/v2b/supply.py | `interchangeable(fa, fb)`: each witness body, placed in the other family's (init, final), is T4-v1a qualified in both directions. `distinct_classes(fams)` groups families into classes. From now on, reuse "across k families" means k CLASSES, and supply screens check distinctness before freeze |
| Repaired control logic | engine/v2b/t53_correction.py | PC_ONE is START-relative (no family-capability gain on SAME #2 beyond START) and is evaluated only on distinct pairs. CAP_D counts distinct classes |
| Graded + selection known-answer battery | engine/v2b/t1v2_graded_selection.py | described below |
| T52 runner | engine/v2b/t52_dose.py | the TEST-3 runner |

## 3. Qualification
**t1 v2 (beta01/runs/T03_T1V2/T1V2_RESULT.json): QUALIFIED.**

| Case | Expected | Got |
|---|---|---|
| GK_1 / GK_2 / GK_3 (entry holding k witness bodies) | exactly k families | exactly the first k families (graded sensitivity holds) |
| GK_LATE (motif entry after PRISTINE) | all solved, every charge > N_COV | 16/16 cells; every charge > N_COV = 151,920. The D endpoint records ordering cost |
| SK1 (selection with the planted motif shown) | M | M |
| SK2 (no candidate helps) | INHERITED | INHERITED (it does not select junk) |
| SK3 (M vs a re-expression M') | a member of the class, ruler EQUAL | M, ruler EQUAL |
| SK4 (one motif example + one unrelated; recorded, ungated) | -- | M. In the planted known-answer setting, one example suffices for the paired selector |

## 4. T53 correction analysis (CORRECTION class; post-exposure)
`beta01/runs/T02_T53/T53_CORRECTION.json`. These are T02's frozen walks re-read with the repaired logic. **The T02
readouts were seen before the repair, so this is a corrected analysis, not a frozen test.**
- Repaired PC_ONE: good on 8/8 evaluated distinct pairs. CON1 and CON8 are excluded as duplicate pairs. PC_MOTIF
  10/10; NC_OTHER 10/10. The disposition is MEASURED_CORRECTION.
- Distinct-class CAP_D_SAME: G1 5/10 (below k = 6); SHAM_0 8, SHAM_1 9, SHAM_2 10. G1_NC, SEL_P, SEL_OFF_0 and
  NC_OTHER are all 0.
- Reading (correction class): **A23-geometry capability is GENERIC to inheritance + composition + recurrence. Under
  distinct-class accounting it is not G1-specific, and G1 alone falls below A23's own threshold.** Capability
  arises only in donors that recovered the planted motif (T02 readout, consistent). The live controls (P, OFF_0,
  G1_NC) never reach it. This sharpens the operator's starting position ("the clean shams also succeeded"; "the
  donor frequently recovered the planted motif").

## 5. Next frozen experiment
TEST-3 = T52, the validation-dose response: `beta01/windows/T03_T52_SPEC.md`. It is a fresh, frozen,
single-factor experiment, and its continuity gate re-runs A23's own dose-2 G1 donors.

## 6. Queued
- A fresh-replicate confirmation of the CORRECTION reading (new A23-geometry replicates with the distinctness screen),
  if T52 does not make it moot.
- The no-donor-state receipt check (before the S4 replication).
- The Fabric output-retrieval gap is reported (#1404). T51 is planned on M4.
