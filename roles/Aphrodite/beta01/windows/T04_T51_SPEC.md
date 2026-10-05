# T04 -- T51: NATURAL-RECURRENCE DONOR STAGE (FROZEN SPEC)

C-006 (C-P2B-APH-BETA-01), cycle 4. Frozen in DEV-4, 2026-10-04, before any T04 foundry, donor or transfer run.
Thread TH-019 (recurrence x visibility). Rungs: R3 (selectable), R5 (reused), R6 (causal, via controls).
Evidence tier 2. A NEW experiment.

## 1. Question
Does naturally arising recurrence co-occur with learnability strongly enough for inheritance + composition to
become useful? The estimand is a DOSE relationship, not "does G1 win": across lineage seeds and panel schemas S,
does reuse of the inherited schema's selected library rise with the natural recurrence dose X_S?

## 2. Supply (W8 CG-1 LIN, frozen task side, W8 REPORT s6)
- LIN seeds 0-7, 144 families each = 1,152 families. **F1 freeze check passed in DEV-4: regenerating
  `w8_lin.supply("LIN", s, 144)` reproduces W8_SUPPLIES.json byte-for-byte for 8/8 seeds.**
- Panel: G1 + PA ({H} + v) + PB gcd(acc, {H}) are matched; PC (v // {H}) and PD gcd({H}, v) are share-matched only.
- X_S = W8 genuine COND_8 per seed x schema (W8_RESULTS.json), frozen into the plan.
  **F6a passed: realised X_S range 0.000-0.661 (width 0.661 >= 0.10).**

## 3. Escrow: a declared change (W8 F5/F6)
Engine escrow is **30,000** throughout (foundry pilots, OBSERVE, VALIDATE and selection). It is not A19/A23's 250k,
where the window fraction is about 2% and F6 would stop the experiment.
- **F6b passed:** the W8 window fraction at 30k is about 0.24, so carriers are about 0.15 >= 0.10.
- **The smoke confirmed it on seed 7:** 141/144 T4-qualified; 33 in (0, 0.75]; 132 with p <= 0.75.

Transfer scoring is the v2b D endpoint: first T4-v1a-qualified program, cap 1,000,000, 2 cells per family.
**The 250k window is not an endpoint anywhere.**

## 4. Design and frozen rules
- **Roles** (A19 NAT rule; seeded `APHRODITE/T51/ROLES/<seed>`):
  - OBSERVE 4, from 0 < p_PRISTINE <= 0.75;
  - VALIDATE 4, from p <= 0.75;
  - TRANSFER 32, from p <= 0.75 (W1 WP-3 breadth; with 8, REUSABLE was near-impossible).
  Roles are never chosen by realised recurrence (W1 s5).
- **Supply gate:** >= 6 of 8 seeds fillable. Otherwise SUPPLY_LIMITED.
- **Donors:** a18_c1._donor_job, unchanged, at escrow 30k.
  - Arms G1, PA, PB, PC, PD (held = arm, composition ON);
  - P (PRISTINE start; composition ON);
  - G1_NC (G1 held, composition OFF).
  - 8 seeds x 7 arms = 56 donors.
- **Transfer:** libraries SEL_<arm>, START_<held>, PRISTINE on the 32 TRANSFER families x 2 cells. Exact walks.
- **Reuse (per seed x arm):** the number of extensionally DISTINCT classes (supply.distinct_classes) of TRANSFER
  families in which, in >= 1 cell, SEL reaches a qualified program at <= 1M AND START is censored at 1M.
  Normalised by the number of classes.
- **Primary estimand:** OLS slope of normalised reuse on X_S over the 40 (seed x panel-schema) points.
  - Significance: a one-sided seed-clustered permutation test (X_S shuffled among the 5 schemas within each seed;
    10,000 permutations, seed `APHRODITE/T51/PERM/v1`).
  - NATURAL_DOSE_SLOPE = POSITIVE iff slope > 0 and p < 0.05.
- **G1_SPECIFIC:** YES iff G1's residual above the pooled line is positive in >= 7/8 seeds (sign test p = 0.035).
- **Controls reported:** P and G1_NC reuse totals (live).
- **Dispositions:**

  | Disposition | Condition |
  |---|---|
  | TECHNICAL_FAILURE | any evaluator disagreement or crash (up to 3 reruns) |
  | UNTESTABLE_NO_DOSE_RANGE | realised X range < 0.10 |
  | MEASURED_NO_REUSE_ANYWHERE | no arm, controls included, reuses anything |
  | MEASURED | otherwise |

## 5. Interpretation table (frozen)

| Result | Reading |
|---|---|
| POSITIVE slope | natural recurrence acts as a dose: more recurrence visible to the improver means more reuse. Mechanism plus natural supply co-occur |
| NOT_SHOWN, with reuse present | reuse exists, but it does not track the natural dose over the realised range |
| MEASURED_NO_REUSE_ANYWHERE | **RECURRENCE_PRESENT_VISIBILITY_FAILED** if X_S > 0 (recurrence is in the supply but never becomes usable). Never "NO_COMPOUNDING" |
| G1_SPECIFIC NO | G1 is not privileged (expected from W8: PA recurs more than G1) |
| P or G1_NC reuse comparable to the panel arms | inheritance/composition is not what produces the reuse |

## 6. Frozen identities and compute
- Runner `engine/v2b/t51_natural.py`, sha256 `27d46868b3958d5afeb51eb5831a27d52420927394eb2b4e60de072fc913c802`.
- Plan `beta01/runs/T04_T51/T51_PLAN.json`, sha256 `c7809d2541b80e6e53e1f3b0ae1d349d77a51427b1f25b99b8482e691d017b3a`.
- M4, 4 workers, about 9 CPU-h (foundry about 1 h wall; donors about 0.5 h; transfer about 1-1.5 h). Inside R2.
- Smoke (seed 7, 6 transfer families, cap 20k; not an endpoint): it validated every stage. Its readout was printed
  and is disclosed (MEASURED_NO_REUSE_ANYWHERE at cap 20k). Its outputs were deleted (walks sha256 prefix
  56635d93ae604bbf).
