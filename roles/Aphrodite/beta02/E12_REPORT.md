# BETA-02 E1 + E2 REPORT: IMPROVER REPLICATION AND MECHANISM SPLIT

C-007 (C-P2B-APH-BETA-02). Pre-registration beta02/BETA02_PREREG.md, frozen at 122b0c8cb (2026-10-06 01:02Z), before
any outcome. Evidence tier 2: local CPU engine, W5. First-order only.

| Item | Value |
|---|---|
| Receipts | beta02/runs/E12/{E12_RESULT.json, E12_DONORS.jsonl, E12_INDEX.json, E12_WALKS.jsonl, E12_SEEDS.json}; beta02/runs/SUPPLY/{FOUNDRY.jsonl, PLAN_E.json}; beta02/runs/KNOWN.json |

## 1. Dispositions
- **Technical: CLEAN.** Attempt 1, 01:02-05:15Z, 4 workers, threads = 1, exit 0.
  - Foundry: 3,456 families.
  - Donors: 220.
  - Walks: 4,608.
- **Supply: OK.**
  - Roles filled 24/24.
  - **Usable seeds: 22.** LIN 24 and 27 failed the pre-registered extras-fill rule (fewer than 8 VALIDATE + 6 OBSERVE
    extras). That rule was applied by code before any donor ran.
  - 22 >= the pre-registered minimum of 20.
- **Scientific: MEASURED.** Known answers K0-K5 pass. Junk gates pass:

  | NULL arm | Planted OFF selected | NULL total vs treatment |
  |---|---|---|
  | NULL11 @ O10 | 0/22 | 162 = 162 |
  | NULL0x @ O10 | 0/22 | 133 = 133 |

- **REPLICATION_GATE = PASS**, so E3 (R8) was launched as pre-registered.

## 2. E1: replication of T12 (g11 @ O10 vs I_0 @ O4)

| Measure | Value |
|---|---|
| Totals (held-out families reached beyond PRISTINE, 22 seeds x 32) | **g11 @ O10: 162 (23.0%)** vs **I_0 @ O4: 63 (8.9%)**, a ratio of 2.57 |
| Per-seed difference d | sum **+99**, mean **+4.5**, median **+5.5** |
| Better / worse / tied | **16 / 0 / 6** |
| Exact one-sided sign-flip p | **1.5e-5** (= the attainable minimum for 16 nonzero seeds) |
| **E1_POSITIVE** | **YES** |

Per-seed d (seeds 25-47, excluding 27): 0, 8, 0, 6, 8, 12, 1, 6, 0, 5, 10, 0, 6, 6, 1, 3, 6, 0, 0, 9, 8, 4. **No
seed is worse.**

T12 (8 seeds, p = 0.031 at its floor) is replicated with a large margin on 22 unexposed seeds.

## 3. E2: factorial mechanism split

**Totals over 22 seeds** (rule x width):

| Rule | O4 | O10 |
|---|---|---|
| I_0 (g0) | 63 | 95 |
| I_0 minus MEMORISE (g0x) | 98 | 133 |
| g10 (subset criterion) | 72 | 101 |
| **g11 (g10 minus MEMORISE)** | **122** | **162** |

**Named effects** (per-seed contrasts in families per seed; exact two-sided sign-flip; Holm at 0.05 across the three):

| Effect | Definition | Mean per seed | Better / worse / tied | p (two-sided) | Holm |
|---|---|---|---|---|---|
| **MEMORISE_EXCLUSION_EFFECT** | mean over widths of (g11 - g10) | **+2.52** | 12 / 0 / 10 | **0.00049** | **REJECT** |
| OBSERVATION_WIDTH_EFFECT | mean over {g11, g10} of (O10 - O4) | +1.57 | 8 / 4 / 10 | 0.043 | not rejected |
| INTERACTION | (g11 - g10)@O10 - (g11 - g10)@O4 | +0.50 | 3 / 4 / 15 | 0.52 | not rejected |

On widths: the OBSERVATION_WIDTH_EFFECT p of 0.043 needs <= 0.025 at the second Holm step. The per-rule cells are
below.

**Cells:**

| Cell | Sum | Better / worse / tied | p (one-sided) |
|---|---|---|---|
| EXCL @ O10 (g11 vs g10) | +61 | 10 / 0 / 12 | 0.00098 |
| **EXCL @ O4 (g11 vs g10)** | **+50** | **9 / 0 / 13** | **0.0020** |
| EXCL under I_0 @ O4 (g0x vs g0) | +35 | 5 / 0 / 17 | 0.031 |
| EXCL under I_0 @ O10 (g0x vs g0) | +38 | 5 / 0 / 17 | 0.031 |
| CRITERION @ O4 (g10 vs g0) | +9 | 2 / 0 / 20 | 0.25 |
| CRITERION @ O10 (g10 vs g0) | +6 | 1 / 0 / 21 | 0.50 |
| WIDTH under g11 | +40 | 8 / 2 / 12 | 0.0068 |
| WIDTH under g10 | +29 | 7 / 3 / 12 | 0.084 |
| g11 @ O4 vs I_0 @ O4 | +59 | 11 / 0 / 11 | 0.00049 |

**G11_ONLY_WORKS_AT_O10 = NO.** g11 beats g10 at O4 (9/0/13, p = 0.002) as well as at O10. The interaction is null.

**Memorisation selected** (seeds of 22):

| Arm | g0 O4 | g0 O10 | g10 O4 | g10 O10 | g0x / g11 / NULL arms |
|---|---|---|---|---|---|
| MEMORISE selected | 11 | 11 | 11 | 10 | 0 (mechanical) |

## 4. Reading (answers to the directive)
1. **The T12 effect is caused by the selection-rule change, specifically by excluding memorisation from candidacy.**
   - It holds at both observation widths and under both acceptance criteria. It is weaker under I_0's lower95
     criterion (5 seeds) than under g10's (9-10 seeds).
   - **The g10 subset criterion by itself does nothing** (CRITERION: 1-2 seeds, p >= 0.25). It adds only once
     memorisation is gone: g11 122 vs g0x 98 at O4 (descriptive).
2. **Wider observation helps additively, but less, and it is not established after Holm.**
   - Under g11 it is significant as a cell (8/2/12, p = 0.007).
   - It is not required for the exclusion effect. There is no interaction.
   - Under I_0, wider observation alone raises 63 -> 95 (descriptive). It also feeds MEMORISE in some seeds (seed 25:
     I_0 6 -> 0).
3. **The original improver chooses memorisation in HALF of fresh natural seeds** (11/22 at either width).
   - In every same-width exclusion contrast (g11 vs g10 and g0x vs g0, at O4 and at O10), each seed where the
     excluding arm gains had a baseline that chose MEMORISE or INHERITED. There were no exceptions (verified on the
     donor rows).
   - In the cross-width E1 contrast, seeds 29 and 40 gain over an I_0 @ O4 baseline that had chosen a real schema.
     Those gains come from width, not exclusion.
4. **Correction of a Beta-01 impression:** T11's g11 @ O4 (101 vs 98, exposed seeds) suggested that exclusion
   needed width. On fresh supply it does not (122 vs 72 at O4). The T11 figure was an exposed-seed, small-sample
   reading. Its label is unchanged.

**Status:** IMPROVER_CHANGE_REPLICATED_LOCAL = YES (now at N = 22 unexposed, p = 1.5e-5); EVIDENCE_TIER = 2;
FIRST_ORDER_ONLY = YES. **R8: running (gated PASS).**

## 5. Per seed (gain of 32)

| Seed | g0 O4 | g0 O10 | g0x O4 | g0x O10 | g10 O4 | g10 O10 | g11 O4 | g11 O10 |
|---|---|---|---|---|---|---|---|---|
| 25 | 6 | 0 | 6 | 6 | 6 | 0 | 6 | 6 |
| 26 | 0 | 8 | 0 | 8 | 0 | 8 | 2 | 8 |
| 28 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 7 |
| 29 | 10 | 16 | 10 | 16 | 10 | 16 | 10 | 16 |
| 30 | 0 | 8 | 0 | 8 | 0 | 8 | 0 | 8 |
| 31 | 0 | 0 | 12 | 12 | 0 | 0 | 12 | 12 |
| 32 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 1 |
| 33 | 0 | 0 | 6 | 6 | 0 | 0 | 6 | 6 |
| 34 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 7 |
| 35 | 0 | 0 | 0 | 0 | 5 | 0 | 5 | 5 |
| 36 | 0 | 0 | 0 | 0 | 4 | 0 | 4 | 10 |
| 37 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 |
| 38 | 0 | 6 | 0 | 6 | 0 | 6 | 0 | 6 |
| 39 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 6 |
| 40 | 11 | 12 | 11 | 12 | 11 | 12 | 11 | 12 |
| 41 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 3 |
| 42 | 0 | 0 | 6 | 6 | 0 | 0 | 6 | 6 |
| 43 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 |
| 44 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| 45 | 0 | 9 | 3 | 9 | 0 | 9 | 3 | 9 |
| 46 | 0 | 0 | 8 | 8 | 0 | 0 | 8 | 8 |
| 47 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 4 |

## 6. Attack questions
1. The named-effect tests treat seeds as the unit, but the cells share supply. That is correct for paired inference,
   and family-level dependence is absorbed by the seed-level contrast.
2. Seeds 32 and 41 show g11 @ O10 < g11 @ O4 (1 vs 2; 3 vs 7). Width can change which abstraction wins even without
   memorisation (cf. T11 seed 1, the validation-to-transfer mismatch).
3. The NULL arms equal their treatments exactly in every seed. The planted OFF schema is never competitive, so the gate
   is passed easily. A stronger junk control (a planted near-miss schema) would be more demanding. Recorded for E4.
