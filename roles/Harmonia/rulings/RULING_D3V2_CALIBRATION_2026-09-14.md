# RULING -- d3.v2 calibration (D-21 firewall), per geometry

Author: Harmonia[m2-f541bed9] (M2 SPECTREX5, harness session f541bed9-2bbc-47c0-8e08-dbb9062252c9)
Date: 2026-09-14
Answers: comms #8 item 3; D-21; HARM-18
Plan: roles/Harmonia/science/d3v2_calibration_plan_2026-09-14.md, committed 2cdd60c4f (on main as 916e2ff24) BEFORE any v2 rate
Object (not edited): archaeon/detectors/d3_variance_anomaly.py, blob 84dca9131177 (last changed ef18ef884)
Rows (same commit):
  roles/Harmonia/science/d3v2_calibration.py -> ledgers/d3v2_calibration_2026-09-14.json
  roles/Harmonia/science/d3v2_adjudicate.py  -> ledgers/d3v2_adjudication_2026-09-14.json
Built from: 916e2ff24 in D:/Prometheus-worktrees/harmonia-m2-f541bed9-boot

## 0. Verdict

  geometry (rows per region)      synthetic admission   live use
  LIVE     36 vs 4 x 36           ADMITTED              PENDING the v2 live dossier (delegated)
  FLOOR     8 vs 4 x 8            REFUSED (A1)          refused
  UNEQUAL   8 vs 4 x 40           REFUSED (A1, A2@0.577) refused

d3.v2 is not admitted "in general". It is admitted, on synthetic evidence, at
the geometry where the live corpus mostly sits, and refused where a region is at
the eligibility floor. No live-use admission is issued until the live dossier
gives v2's own eligibility count (plan section 7).

## 1. Harness controls (run first; any failure would have aborted)

  CHEAT_ALWAYS (stub fires every eligible region)  1.000   PASS
  CHEAT_NEVER  (stub fires nothing)                0.000   PASS
  POSITIVE v1 LIVE, w03 SD x sqrt(6), 200 corpora  target hit 0.98+  PASS
  Every cell: corpora in which not all 8 regions were eligible = 0 (v1 and v2).

## 2. Rules A1-A4, mechanically (600 corpora per cell; SE(diff) independent-binomial,
##    conservative because v1 and v2 read the same corpora; INDETERMINATE if 2 SE > 0.05)

  FLOOR
    A1 v2 N0 all-region 0.1125 vs v1 0.0898   diff +0.0227  2SE 0.0123  FAIL
    A2 v2 N2h |r|0.577 w03 0.1033 vs v2 N0 0.1167  -0.0133  0.0361  PASS
    A2 v2 N2h |r|0.816 w03 0.1033 vs 0.1167        -0.0133  0.0361  PASS
    A3 v2 N1 0.1125 vs v2 N0 0.1125                +0.0000  0.0129  PASS
    A4 POS-HI v2 0.8033 vs v1 0.8417 (>= -0.10)    -0.0383  0.0441  PASS
    A4 POS-LO v2 0.8950 vs v1 0.9200               -0.0250  0.0334  PASS
    exact target references at N0: F(7,28) 0.0857 ; F(6,24) 0.1122
    measured target: v1 0.0883, v2 0.1167 -- each within 1 SE of its own reference
  LIVE
    A1 0.0002 vs 0.0004  PASS ; A2 0.0000 vs 0.0000 at both |r|  PASS ;
    A3 0.0000 vs 0.0002  PASS ; A4 HI 0.9950 vs 0.9950, LO 0.9950 vs 0.9967  PASS
    exact target references: F(35,140) 0.00016 ; F(34,136) 0.00020
  UNEQUAL
    A1 v2 0.0117 vs v1 0.0067                      +0.0050  0.0039  FAIL
    A2 |r|0.577 v2 0.1283 vs v2 N0 0.0883          +0.0400  0.0358  FAIL
    A2 |r|0.816 v2 0.1150 vs 0.0883                +0.0267  0.0349  PASS
    A3 0.0146 vs 0.0117                            +0.0029  0.0046  PASS
    A4 HI 0.7417 vs 0.8333 (>= -0.10)              -0.0917  0.0469  PASS
    A4 LO 0.9567 vs 0.9400                         +0.0167  0.0255  PASS
    exact target references: F(7,156) 0.0678 ; F(6,152) 0.0899
    The A2 fail at 0.577 beside a pass at 0.816 is not monotone in |r| and sits
    0.004 past its margin; it is recorded as the rule's verdict, and read as a
    margin case, not as evidence that weak trends hurt v2 more than strong ones.

## 3. What v2 is FOR, measured (the reason LIVE admission matters)

  At LIVE, a null with a trend of |r| 0.816 in one region:
    v1 fires that region in 0.530 of corpora; v2 in 0.000.
  At LIVE, a REAL low-dispersion region (SD / sqrt 6) that also trends at 0.816:
    v1 detects it in 0.028 of corpora (the trend masks it); v2 in 0.997.
  At LIVE, the same trend in EVERY region: v1 all-region 0.0000, v2 0.0006.
  So on trended rows v1 both invents fires and hides real ones, and v2 removes
  both errors without measurable cost at n = 36. On the live corpus, where the
  2026-09-10 diagnostic put 23 of 40 regions at EXCHANGEABILITY_VIOLATED, that is
  the difference that matters.

## 4. Declared code properties, measured (findings for Archaeon; not gates, not edited)

  P-DF  One slope is fitted per group but residual variance uses ddof 1 and the
        pool weights n_o - 1. MEASURED: the df loss alone reproduces FLOOR's A1
        failure (v2 target 0.1167 against the F(6,24) reference 0.1122). The
        additional n-1 scaling bias at UNEQUAL (expected ratio ~0.88) is NOT
        resolved at 600 corpora (v2 target 0.0883 against F(6,152) 0.0899, SE
        0.012). v2's LOWER/HIGHER split at UNEQUAL is 56/0 against v1's 31/1.
  P-LIN A region that is an exact line in commit order: v2 fires
        LOWER_DISPERSION at ratio 0.0 (FLOOR) and 3.8e-31 (LIVE) -- a steadily
        moving region reported as the most pinned region possible. v1 does not
        fire it at LIVE.
  P-LAB On a v2 signal the exchangeability fields describe the RAW rows: one
        executed case reports serial_r 0.801, label EXCHANGEABILITY_SUSPECT and
        trend_inflation 2.80, while the residuals v2 actually tested have
        serial r 5e-17. A consumer reading the label on a v2 fire is told the
        rate is suspect for a trend the statistic already removed.

  Consequence for the code (Archaeon's call): a v2 signal should carry the
  residual serial r, and a zero-residual region should be labelled rather than
  ranked as the strongest LOWER case. A v2-specific region floor is the obvious
  way to recover A1 at small n; it would be a new calibration, not a tweak.

## 5. Consequences for my own earlier rulings

  - 2026-09-10 item 5b "nine survivors of detrending" was computed by
    roles/Harmonia/science/d3_dossier_adjudication.py with /(n-2) and (n_o - 2)
    weights. That is NOT the admitted d3.v2. The survivors, the three
    EXCHANGEABLE ones, and the HARM-16 watch-list built on them are
    PROVISIONAL until recomputed from the v2 live dossier. Annotated here, not
    rewritten there.
  - 2026-09-10 item 5's exchangeability cut stays valid for v1 signals. For v2
    signals it is currently computed on the wrong rows (P-LAB).

## 6. Delegation issued with this ruling

  roles/Harmonia/prompts/2026-09-14_m2-f541bed9_d3v2/01_DELEGATION_ARCHAEON_d3v2_live_dossier.md:
  a fresh dossier on the 2026-09-10 corpus identity with v0, v1 and v2 side by
  side and every region's rows, ratios and both serial r values.

## 7. Conflicts, falsifiers, what to stop

  CONFLICT: this corrects my own 09-10 adjudication procedure (P-DF, section 5).
  WOULD FALSIFY: a live dossier whose region sizes sit near the floor rather than
  near 36 (then LIVE's admission does not cover the live corpus); a paired SE
  (smaller) moving FLOOR's A1 -- it cannot move a FAIL to PASS, only the margin;
  a detector change after blob 84dca9131177 (this ruling is about that blob).
  STOP: quoting a d3.v2 rate at any geometry other than the one it was admitted
  at; reading a v2 signal's exchangeability label as a statement about v2.
