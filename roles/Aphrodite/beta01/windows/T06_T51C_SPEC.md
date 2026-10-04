# T06 -- T51-C: FROZEN CONFIRMATION OF ENDOGENOUS BASE-CLASS DERIVATION ON FRESH NATURAL SUPPLY

C-006 (C-P2B-APH-BETA-01), cycle 6. Frozen in DEV-6, 2026-10-04, before any T06 run. Thread TH-019 (and TH-018).
Rungs R1-R5 (derivable -> selected -> reused). Evidence tier 2.

## 1. Question
T51's exploratory diagnosis (post-hoc; seeds 0-7) found that a PRISTINE-start donor on natural lineage supply derives
the G1 base class endogenously, and reaches 57 of 256 held-out families beyond PRISTINE, against 70 for a donor that
inherits G1. Does that replicate on FRESH seeds under a frozen endpoint and frozen thresholds?

## 2. Supply and pipeline
- LIN seeds **8-15**. None of them was used by any Beta-01 run. **F1 passed 8/8** (byte-identical to W8_SUPPLIES.json
  with W8's init()).
- Pipeline: `t51_natural.py`, the identical code path, with:
  - arms P, G1, G1_NC, PA (V2B_T51_ARMS);
  - escrow 30k;
  - roles OBSERVE 4 / VALIDATE 4 / TRANSFER 32;
  - D endpoint at cap 1M, tribunal T4 v1a, 2 cells.
- Runner sha256 aced4a1a...; analysis `t06_confirm.py` sha256 85ade3cb...; plan `beta01/runs/T06_T51C/T51_PLAN.json`
  sha256 35dabe7f....
- The plan's X_S range is 0.000-0.306. The dose slope is not an endpoint here.

## 3. Frozen endpoint and rules (t06_confirm.py)
gain(lib, arm, seed) = number of the seed's 32 TRANSFER families where `lib` reaches a T4-v1a-qualified program at
<= 1M in >= 1 of 2 cells AND PRISTINE is censored in that cell.

| Rule | Definition |
|---|---|
| Gate | inherited benefit exists: gain(START, G1) > 0 in >= 6/8 seeds. Otherwise UNTESTABLE_NO_INHERITED_BENEFIT. Technical failure leads to up to 3 reruns |
| **H1 ENDOGENOUS_DERIVATION** | sum gain(SEL, P) >= 0.70 x sum gain(START, G1), AND gain(SEL, P) > 0 in >= 6/8 seeds |
| **H2 DERIVES_BASE_CLASS** | P's selected schema is EQUAL_ANY (ruler v2.1) to G1 or one of its re-expressions in >= 5/8 seeds |
| **H3 COMPOSITION_SMALL** (descriptive) | sum gain(SEL, G1) - sum gain(START, G1) <= 0.25 x sum gain(START, G1) |
| Reported, not gated | G1_NC SEL vs START; PA gains |

## 4. Interpretation (frozen)

| Result | Reading |
|---|---|
| H1 and H2 YES | CONFIRMED (tier 2): on natural lineage supply, an improver with no inherited abstraction derives the dominant recurring base class from 4 observed families, selects it, and recovers >= 70% of the transfer benefit of inheriting it. Natural recurrence is present and VISIBLE at the base-class level |
| H1 NO with H2 YES | derivation happens but pays less than inheritance on held-out families |
| H2 NO | T51's exploratory finding does not replicate |
| H3 YES | composition on an inherited stepping stone adds <= 25%. First-order compounding beyond the base class is small in natural supply |

## 5. Compute
Foundry about 1 h (4 workers); 32 donors about 0.4 h; transfer about 1 h. About 7 core-h, within R2 and the seat's
rolling 48 core-h (about 42 core-h used in the last 24 h, including this run).
