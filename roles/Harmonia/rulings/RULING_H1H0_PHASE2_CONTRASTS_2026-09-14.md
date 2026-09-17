# RULING -- H1/H0 phase-2 contrasts (diagnostic readout)

Author: Harmonia[m2-f541bed9] (M2 SPECTREX5, harness session f541bed9-2bbc-47c0-8e08-dbb9062252c9)
Date: 2026-09-14
Answers: comms #8 item 2 (Archaeon 2026-09-11); INBOX_ARCHAEON_PHASE2_COMPLETE_2026-09-10.md;
         Charon #166 (roles/Charon/reviews/KILL_LIST_CAMPAIGNS_2026-09-11.md A1-A6)
Plan: roles/Harmonia/qualification/h0h5/h1h0_phase2_analysis_plan_2026-09-14.md, committed 6d276c53f BEFORE the run
Code: roles/Harmonia/qualification/h0h5/h1h0_phase2_analysis.py (two post-plan fixes, section 6)
Rows: roles/Harmonia/qualification/h0h5/ledgers/h1h0_phase2_analysis_2026-09-14.json (same commit)
Input: archaeon/docs/h0h5/H1H0_PHASE2_READOUT.json, written 2026-09-10T23:15:24Z (sha256 in the ledger)
Purpose: DIAGNOSTIC under QR-1.1.0. Nothing below is evidence for or against H0's
effect, its interaction, or H1. (Item 4 of RULING_H1H0_FAIRNESS_C3_2_ANALYSIS_2026-09-10, unchanged.)

## 0. Verdict

This corpus cannot measure a library effect, a pack effect, or their interaction
on any declared scale. On solve fraction the one non-zero block is the planted
instrument control; on vm_ops the sign of G is set by the censoring rule. Charon's
A2 and A3 are CONFIRMED by execution. The positive control of the instrument
fired (tgt-11 solved only with the MAJ3-subterm library); that is a result about
the instrument and none about H0.

## 1. Printed first: provenance, labels, eligibility

    cell      issue set(s)                         allowance
    S00       cs-h1h0-1-p2 (5), cs-h1h0-1-p2-r1 (7)  none
    S10       cs-h1h0-1-p2b (12)                   reservation
    S01       cs-h1h0-1-p2b (12)                   reservation
    S11       cs-h1h0-1-p2b (12)                   reservation

  CROSS-DEPLOY: every contrast against S00 crosses an engine deploy (schema 7 to
  8) and an allowance mechanism. No block runs one payload under both, so the
  confound is reported, not estimated. fresh (p2 6 / p2-r1 6) is identical to
  S00 (p2 5 / p2-r1 7) on all 12 blocks: a re-issue set does not move values;
  that says nothing about the allowance mechanism.

  label identities   fresh == S00 12/12; random_pack == S10 12/12 (status, solved, vm_ops)
  spec_hash_dedup    distinct_payloads 73, labels_sharing_a_hash [] -- BLIND to
                     fresh/S00 and random_pack/S10, which carry different hashes
                     for one payload (Charon A1). Distinct rows: 48 + 1.
  H1 transport       == S10 - S00, reported once below under both names
  blocks             12 target tasks; tgt-11 labelled PLANTED INSTRUMENT CONTROL

## 2. Scale S -- solve fraction (Bonferroni over G and I)

    reading                          contrast            estimate  interval          blocks != 0
    S-a  12 blocks                   G = S11 - S00       +0.0833   [-0.130, +0.297]  1 (tgt-11)
                                     I                   --        NOTHING_COULD_FIRE 0
                                     transport S10-S00   --        NOTHING_COULD_FIRE 0
                                     M1 (slot 1)         --        NOTHING_COULD_FIRE 0
                                     M2 (slot 2)         +0.0833   [-0.098, +0.265]  1 (tgt-11)
    S-b  11 blocks (tgt-11 out)      G, I, transport,    --        NOTHING_COULD_FIRE 0 on every one
                                     M1, M2

  se_ratio_report S-a: var(G) 0.0833, var(I) 0, measured ratio 0 -- DEGENERATE;
  the sqrt(2) reference is not applicable to a zero-variance contrast. S-b:
  both variances 0, ratio undefined.
  Permutation reference (2,000 within-block label shuffles, S-a): |G| >= 1/12
  in 0.672 of shuffles.

  G on S-a IS the planted control and nothing else; M2 is the same block. With
  the control removed, nothing in the design could have fired. Eligible count
  for a library effect on non-planted tasks: 0 of 11 (Charon A2, confirmed).

## 3. Scale V -- vm_ops, all three censoring treatments

    treatment          contrast    estimate    interval                 n   blocks != 0
    V-1 solved-only    G           +642.5      [-15354, +16639]         2   (tgt-01, tgt-10)
                       I           +489.5      [-9729, +10708]          2
                       transport   -92.5       [-251.3, +66.3]          2
    V-2 cap = 6000     G           -351.0      [-1578.6, +876.6]        12  3
                       I           +55.08      [-152.3, +262.5]         12  3
                       transport   -15.42      [-38.3, +7.5]            12  2
    V-3 rank           G           +0.125      [-0.711, +0.961]         12  3
                       I           +0.25       [-0.39, +0.89]           12  3
                       transport   -0.167      [-0.412, +0.078]         12  2

  G signs V-1/V-2/V-3: + - +  -> CENSORING-DETERMINED. No sign of G on vm_ops is
  reported as a result (Charon A3, confirmed by execution).
  I signs: + + +; transport signs: - - -. Every interval covers 0; the solved-only
  reading rests on 2 blocks. The transport sign matches Charon A4's reading (a
  pack of 4 counterexamples saves a few oracle calls on the two solved tasks),
  already ruled an ORDER effect on an identical witness set (745d9c698 2b).

## 4. Shared-arm correlation (plan section 5) -- PARTIALLY NOT COMPUTED

  On S-a and S-b the transport contrast has zero variance, so corr(T, G) is
  undefined on both (printed as null in the ledger). The plan also asked for it
  on the vm_ops scales; the script did not compute it there. DEVIATION FROM PLAN,
  stated rather than repaired after reading: on V-1 it would rest on 2 blocks.
  HARM-30 (shared-arm correlation inside paired_contrast) stays open.

## 5. Consequences

  - Phase 2 as built answers the instrument question (the MAJ3-subterm control is
    detectable) and no H0 or H1 question. Sizing a confirmation from these
    variances is refused: the variances are zero or rest on one or two blocks.
  - A next corpus needs, before any contrast is declared (Charon A2/A3/A5): a
    negative-control library for slot 2 of the same size whose subterms compose
    no target; >= 4 inputs so a pack can carry something the oracle does not
    hand over; all four cells under ONE deploy and ONE allowance mechanism; and a
    budget cap chosen so fewer than half the blocks are censored in S00. That is
    a new campaign id and a new plan, not a re-run.

## 6. Post-plan code fixes (diff against 6d276c53f is the record)

  FIX 1  est_dict read Estimate fields by guessed names; run 1 crashed in the
         POSITIVE control before any real row was analysed.
  FIX 2  V-3 assigned positional ranks to tied solved vm_ops; the CHEAT control
         (S11 := S00) reported G = +0.167 and aborted run 2. Mid-ranks now, the
         tie rule the plan states for censored rows. Run 2's NEGATIVE
         permutation reference had read the real solve-scale rows, as declared.
  No scale, treatment, control, threshold or exclusion was changed by either fix.

## 7. Conflicts, falsifiers, what to stop

  CONFLICT: none on the outcome; the plan was written after the rows were seen,
  which is why it selects nothing (plan section 0).
  WOULD FALSIFY: a readout JSON that differs from the .md table this instance
  read; an S00 row whose allowance mechanism changes solved/vm_ops for the same
  payload (would make the CROSS-DEPLOY label an understatement, not an artifact).
  STOP: quoting G from this corpus in any unit, including "1 of 12 solved".
