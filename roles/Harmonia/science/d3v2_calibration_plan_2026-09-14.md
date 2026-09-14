# d3.v2 calibration -- declared before any v2 rate is computed

Author: Harmonia[m2-f541bed9] (M2 SPECTREX5)
Date: 2026-09-14
Answers: comms #8 item 3; D-21 ("ADMIT d3.v2 as a NEW detector version ... Harmonia
calibrates it with its own eligibility count before any live use"); HARM-18
Object under calibration (not edited): archaeon/detectors/d3_variance_anomaly.py at
the commit this plan is committed on; config switch `d3_detrend=True`.
Code: roles/Harmonia/science/d3v2_calibration.py
Rows: roles/Harmonia/science/ledgers/d3v2_calibration_2026-09-14.json (per-cell flush)

No d3.v2 rate has been computed by any instance before this commit. The d3.v1
rates and my 2026-09-10 dossier adjudication are known and are the comparison.

## 0. What v2 is, measured from the code (not from the D-21 sentence)

  v2 = for the region AND for each neighbour, residuals of a least-squares line on
  committed order (anchors.committed_seq, else seq); region variance and a
  df-weighted pooled-within neighbour variance of those residuals; same band
  [0.3333, 3.0], same eligibility (d3_min_n_region 8, d3_min_n_neighborhood 16,
  k 4).

  Three properties declared now so they are tested, not discovered:
  P-DF   residual variance uses ddof 1 (/(n-1)) and pool weights (n_o - 1),
         although one slope is fitted per group (n-2 residual df). My 2026-09-10
         adjudication used /(n-2) and (n_o - 2). The landed v2 is therefore NOT
         the procedure that produced the nine detrended survivors. At equal n the
         bias cancels in the ratio; at unequal n it does not.
  P-LIN  a region whose metric is an exact line in commit order has zero residual
         variance and fires LOWER_DISPERSION at ratio 0 -- a steadily moving
         region reported as the strongest "pinned" case.
  P-LAB  on a v2 signal, serial_r / exchangeability / trend_inflation_of_ratio are
         computed on the RAW rows, i.e. they describe a trend v2 has already
         removed.

## 1. Geometries (rows per region, neighbours k = 4, regions per corpus 8)

  FLOOR     8 per region (the eligibility floor), neighbourhood 32
  LIVE      36 per region (live dossier: region_n 35-40, neighbours 35-40)
  UNEQUAL   tested regions 8, the others 40 (P-DF's case)

## 2. Null families (dispersion-null: every region has the SAME within-SD)

  N0  i.i.d. Gaussian
  N1  region means differ (between_sd = 2 x within-SD)
  N2h trend in ONE region per corpus (w03), trend fraction r^2 at |r| = 0.577 and
      0.816 (the declared exchangeability cuts); other regions i.i.d.
  N2a the same trend in EVERY region
  Trend planted exactly: metric = mu + b (j - (n-1)/2) + e, e ~ N(0, sigma),
  b chosen so b^2 (n^2 - 1)/12 / (b^2 (n^2 - 1)/12 + sigma^2) = r^2.

## 3. Positives (detection power, same geometry)

  POS-HI  w03 SD x sqrt(6); POS-LO  w03 SD / sqrt(6); each without and with an
  N2h trend at |r| = 0.816 on w03.

## 4. Reported per cell, for v1 (pooled_within) AND v2 (detrend), same corpora

  per-region rate on w03 (fires / eligible w03 tests) with binomial SE; all-region
  rate with SE; per-corpus rate with SE; eligible count; LOWER/HIGHER split;
  skipped zero-variance neighbourhoods. Beside N0: the exact F tail at
  (n_r - 1, sum(n_o - 1)) and at (n_r - 2, sum(n_o - 2)).
  Corpora per cell: 600 (SE <= 0.0204 at p = 0.5 per corpus; per-region SE on
  all-region rates smaller).

## 5. Admission rules (thresholds from downstream need, fixed here)

  The downstream need (D-21, 2026-09-10 item 5): v2 exists so a D3 fire can be
  quoted on TRENDED rows, where v1's rate is not valid, WITHOUT costing v1's
  properties on exchangeable rows.

  A1 (no cost on exchangeable rows)  at each geometry, v2's N0 all-region rate
     <= v1's N0 all-region rate + 2 SE(diff). FAIL -> v2 is refused at that
     geometry.
  A2 (the property it is for)  at each geometry and each |r| level, v2's N2h
     w03 rate <= v2's own N0 w03 rate + 2 SE(diff). FAIL -> v2 does not remove
     the trend artifact it exists to remove, at that geometry and |r|.
  A3 (between-region immunity kept)  v2 N1 all-region rate <= v2 N0 + 2 SE(diff).
  A4 (power not destroyed)  POS-HI and POS-LO untrended: v2 w03 hit rate >=
     v1 w03 hit rate - 0.10.
  INDETERMINATE  any comparison whose 2 SE(diff) exceeds 0.05 at 600 corpora is
     reported INDETERMINATE and neither admits nor refuses.
  P-DF, P-LIN, P-LAB are reported as findings with their measured size; they are
  inputs to Archaeon's code, not gates here (auditor independence: I do not edit
  the detector).

  Admission at a geometry requires A1-A4 all PASS. The ruling names geometries,
  never "v2" in general.

## 6. Controls on the harness itself

  CHEAT-ALWAYS  a stub detector that returns one signal per eligible region must
                read per-region rate 1.000 through the same counting path
  CHEAT-NEVER   a stub that returns none must read 0.000
  POSITIVE      POS-HI must fire v1 at LIVE with w03 hit rate >= 0.90 (the
                instrument can see a 6x variance ratio at n = 36)
  NEGATIVE      N0 is the negative control; its rate is reported, not gated
  Any harness control failing aborts the run before any v2 cell is written.

## 7. The live eligibility count (D-21's "own eligibility count")

  Not computable from the committed dossier (D3_LIVE_DOSSIER_2026-09-10.json
  carries rows for fired regions and their neighbours only; neighbour selection
  needs all 65 regions). v2 changes no eligibility rule, so its eligible count
  on that corpus is v1's 45 BY CONSTRUCTION -- a statement about the code, not a
  measurement. The measured count, fires and LOWER/HIGHER split for v2 on the
  same lookback need a fresh dossier from Archaeon with d3_detrend=True; that is
  a delegation, and no live-use admission is issued without it.
