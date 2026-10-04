# T02 -- T53 D-STRATIFIED v1a RE-SCORE OF A23 CAPABILITY: REPORT + EXTERNAL-REVIEW PACKET

C-006 (C-P2B-APH-BETA-01), cycle 2, TEST window 2. Threads TH-018 / TH-021. Evidence tier 2.

## 1. Disposition
- **Technical: CLEAN.** 2,912 / 2,912 exact walks; 0 evaluator disagreements; about 2h 42m on 4 M4 workers.
- **Scientific: MEASUREMENT_FAILED** under the frozen gate (spec s4). The in-run control PC_ONE was good in 6 / 10
  replicates; the gate required >= 8. PC_MOTIF was 10/10 and NC_OTHER 10/10.

**Per the frozen rule, no T53 readout is a result.** The readouts are listed in s5 only because the runner printed
them, and so that the exposure is disclosed.

## 2. Why the control failed (the earliest failed rung: the CONTROL'S OWN known answer was mis-specified)
PC_ONE's expectation was: "solves SAME #1 (its own body), and does NOT solve SAME #2". It was wrong by
construction in 4 replicates, for two distinct reasons:

| Replicate | Cause | Evidence |
|---|---|---|
| 1, 8 | **SAME #2 is an extensional DUPLICATE of SAME #1.** The motif's filler atoms evaluate identically, so the single body solves both families (correctly) | rep 1: (v // (acc + pow(1, first))) vs (v // (acc + math.gcd(abs(last), abs(1)))). Both fillers are the constant 1. rep 8: (last % (acc + gcd(abs(v), abs(0)))) vs (last % (acc + gcd(abs(v), abs(v)))). Both are abs(v) |
| 7, 11 | **START already solves SAME #2** (the inherited G1 library covers it), so "not solved" was unattainable | START non-censored 4/4 on SAME #2 in both |

The control code was wrong, not the apparatus. The PC_ONE gate should have been START-relative and restricted to
extensionally DISTINCT pairs. The spec text anticipated the duplicate case ("unless extensionally reachable:
recorded as a reason"), but the gate did not exempt it.

## 3. NEW FINDING: extensionally duplicate transfer families in A23 (correction-only; A23 label unchanged)
Audit: engine/v2b/receipts/A23_SAME_PAIR_DUPLICATES.json. Body interchangeability was tested by tribunal (T4 v1a
direct_score, both directions). **2 of A23's 40 SAME pairs are interchangeable duplicates, and both are G1 pairs
(CON1, CON8).** Both of those replicates count toward A23's G1 REUSED_SAME = 7 (threshold k = 6).

Under accounting that requires >= 2 extensionally DISTINCT SAME families, **A23's G1 REUSED_SAME is 5/10 < 6. The
G1-specific verdict (G1_RECURRENT_STEPPING_STONE = YES) would not hold.** The shams' 30 pairs contain no
duplicates, so GENERIC 3/3 is unaffected.

A23's recorded label is NOT changed (it is historical and was accepted under MWO-0004 G5). This is recorded as a
correction-class finding for TH-018 / TH-021. The planned instrument repair is a distinctness screen on
transfer-family supply.

## 4. Apparatus facts established by this run (independent of the failed control)
- **Continuity:** 400 / 400 comparable A23 transfer cells reproduce A23's recorded SELECTED charge exactly (the same
  cells, seeds, libraries and walk). The re-score is measuring A23's own cells.
- **Bridge (A23 CAPABILITY_SAME vs the new CAP_D_SAME, per replicate):** G1 9 agree / 1 historical-only;
  G1_NC 10/10; SHAM_0, SHAM_1 and SHAM_2 10/10 each. 49 / 50 agree.
- **Live controls became live and ran:** SEL_P and SEL_OFF_0 libraries on G1 and sham SAME families.

## 5. Readouts (NOT RESULTS: MEASUREMENT_FAILED; disclosed because they were seen)
- G1 CAP_D_SAME 6/10; G1_NC 0; SEL_P 0; SEL_OFF_0 0.
- SHAM_0 8, SHAM_1 9, SHAM_2 10. Generic-cliff excess G1 - max(shams) = -4.
- Motif-recovery split: CAP_D_SAME 33/35 among donors whose selection EQUALS the planted motif; 0/5 otherwise.
- The runner's readout flags: R_SURVIVES YES, R_G1_SPECIFIC NO, R_LIVE_CONTROLS_BEATEN True, R_RECOVERY_ONLY True.

Because these were seen, any repaired re-analysis of THIS walk set is a **post-exposure corrected analysis**
(CORRECTION class, weaker than a frozen test). A fresh confirmation needs new replicates.

## 6. Next (DEV-3)
1. Repair the control logic: PC_ONE becomes START-relative and is evaluated only on extensionally distinct pairs.
2. Add a new supply instrument: an extensional-distinctness screen for transfer families (tribunal
   interchangeability), made mandatory pre-freeze.
3. Run the t1 v2 graded and selection known-answer battery.
4. Freeze T03, deciding between (a) a post-exposure corrected re-analysis of these walks (labelled CORRECTION), and
   (b) a fresh-replicate confirmation.

## 7. External-review attack questions
1. Is a START-relative PC_ONE still a test that can fail, or does it become vacuous when START covers the family?
2. Should A23-style reuse be counted per extensional class rather than per family everywhere? (That would also
   change G1_NC and the shams if their pairs ever collide.)
3. The motif-recovery split (33/35 vs 0/5) is the most decision-relevant readout and it is not readable here. What
   is the minimal fresh design that measures it under a frozen gate?
4. Was 6/10 for PC_ONE predictable from the supply? (Yes, in hindsight: the duplicate fillers. That argues the
   distinctness screen belongs in every pre-freeze supply check.)

## 8. Replay
`python t53_rescore.py report` regenerates T53_RESULT.json from the committed plan and walks. The walk file is
deterministic and reproducible from `run`.
