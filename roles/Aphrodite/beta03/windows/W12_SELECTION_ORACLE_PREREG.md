# W12 PRE-REGISTRATION: SELECTION-OVERRIDE ORACLE BOUND (attack on the E5-N negative)

Beta-03 (C-011). It is pre-registered after the E5-N outcome (NO) and the E6 negative diagnosis (SELECTION 15/22). It is
the directive's s9 negative-branch attack: "check whether selection rejects legitimate improvements".
- It is an ATTACK on a frozen negative. It **cannot relabel E5-N** (R8_UNDER_PROMOTION natural = NO stands).
- Frozen before any W12 walk.
- Runner: engine/v2b/b03_w12.py; hashes in beta03/FREEZE_W12.json.

## Question
If selection were PERFECT among the promoted-dependent schemas that arm D actually derived, would the inherited g11
library ENABLE common-residual acquisition beyond the pristine promotable recipient (arm C)?

## Construction (no new donors)
- **Candidates:** for each of E5-N's 22 pairs, every distinct non-trivial derived schema of arm D that contains a
  promoted primitive. Bare `P_x({H})` re-expressions are excluded. The full derived list comes from the A2 receipt.
- **Library per candidate:** `[w5p schema_entry(S, reg)] + inherited L_g11 start`, with reg = promote_start(L_g11).
  These libraries are hashed (W12_LIBRARIES.json) before any walk.
- **Walks:** the pair's **E1 common-residual families** only (both cells, cap 1M, T4 v1a, the same walker and
  cells).
- **Oracle bound:** per pair, the BEST candidate's common acquisition (a post-hoc max over candidates).
- Pairs with no candidate score 0.

## Frozen decision rule
- **ORACLE_SELECTION_ENABLES = YES** iff an exact one-sided sign-flip over pairs on (oracle best - arm C) gives
  p < 0.05 and a sum > 0.
- **Asymmetric interpretation (frozen):**
  - **YES** shows only that enabling is POSSIBLE under perfect selection. It is an upper bound inflated by
    best-of-k, NOT a demonstration. Selection would then be a binding, potentially repairable limit on this
    substrate.
  - **NO** is strong. Even oracle selection among the derived promoted-dependent schemas does not enable learning
    beyond pristine, so the binding limit is UPSTREAM of selection (candidacy / representation).
- Also reported: oracle vs arm D's actual selection; candidates per pair.
- **Per CLOSE_RULE, W12 is a qualifier only.**

## Compute
About 170 candidate libraries x about 15 common families x 2 cells, minus reused walks. About 2-3 core-h at 4 workers,
within the rolling cap after the roll-off.
