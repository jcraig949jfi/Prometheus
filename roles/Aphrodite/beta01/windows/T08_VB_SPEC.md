# T08 -- VALIDATION BREADTH ON THE ENDOGENOUS ROUTE (FROZEN SPEC)

C-006 (C-P2B-APH-BETA-01), cycle 8. Frozen in DEV-8, 2026-10-05. Rung R3 (SELECTABLE) on natural supply. Thread
TH-019. Evidence tier 2.

## 1. Question
T07's control-arm diagnostic: in 5 of 15 natural seeds (4, 9, 12, 13, 14) paired selection rejects even a planted
CORRECT base-class candidate, because the 4 VALIDATE families show no saving. The transfer families would still
benefit. **Does tripling the validation evidence (VALIDATE 4 -> 12) rescue those seeds without harming the others?**
The amount of evidence gathered before committing is an improver-level property.

## 2. Design
- **Seeds:** the 15 T51/T06 seeds, with the same OBSERVE 4 and TRANSFER 32.
- **Breadth 4:** T07's g0 run (identical roles; continuity-verified 15/15 against T51/T06).
- **Breadth 12:** the original 4 VALIDATE families + 8 extra families. The extras are drawn (seeded
  `APHRODITE/T08/VAL/<seed>`) from the seed's qualified head (p_PRISTINE <= .75) and never used in any role.
  **Supply check: 8/8 extras available in 15/15 seeds.**
- **Donor:** gtc.donor_g('g0') = I_0 (conformance-gated), kind P (PRISTINE start), escrow 30k, R_VAL as T51.
- **Endpoint (as T07):** gain = families of the 32 TRANSFER families where SEL reaches a T4-v1a-qualified program at
  <= 1M in >= 1 of 2 cells AND PRISTINE is censored. PRISTINE walks are reused from T07 (identical cells).
- **Runner:** `engine/v2b/t08_vbreadth.py`, sha256 22893f93....

## 3. Frozen readouts
- **VB_POSITIVE:** a one-sided paired sign test over seeds of gain(B12) vs gain(B4) gives p < 0.05, AND total
  gain(B12) > total gain(B4).
- **RESCUES_VALIDATION_LIMITED:** gain(B12) > 0 in >= 3 of the 5 validation-limited seeds (4, 9, 12, 13, 14).
- **Disposition:** MEASURED if >= 12 seeds are scored; otherwise SUPPLY_LIMITED.
- Also reported: per-seed gains, breadth-12 selections, and seeds harmed.

## 4. Interpretation (frozen)

| Result | Reading |
|---|---|
| RESCUES YES | the natural-supply R3 limit is the AMOUNT of validation evidence. A broader validation set lets the improver accept the correct abstraction |
| RESCUES NO | the 5 seeds' limit is not sample size at this scale: their supply's families do not reward the base class under paired selection even at 12 |
| VB_POSITIVE YES | breadth raises endogenous reuse overall |
| harm in success seeds | breadth dilutes the paired saving (selection becomes stricter or noisier) |

## 5. Compute
15 donors (selection cost about 3x at breadth 12; about 3 min each) plus new scoring walks only for new libraries.
About 1.5 core-h, which fits the seat's rolling 48 core-h (about 45.6 used at 00:40Z).
