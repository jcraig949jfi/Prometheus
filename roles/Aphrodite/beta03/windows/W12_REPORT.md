# W12 REPORT: SELECTION-OVERRIDE ORACLE BOUND (attack on the E5-N negative)

Beta-03 (C-011).
- **Pre-registration:** beta03/windows/W12_SELECTION_ORACLE_PREREG.md. The libraries (W12_LIBRARIES.json, sha
  d33c6031...) were hashed before any walk.
- **Run:** 07:37-08:18Z, 4 workers, 4,432 walks; clean. About 2.7 core-h.
- **Receipts:** beta03/runs/W12/{W12_RESULT.json, W12_INDEX.json, W12_WALKS.jsonl}.
- **A qualifier only:** E5-N's NO is unchanged.

## Result
**ORACLE_SELECTION_ENABLES = NO.**
- 165 non-trivial promoted-dependent schemas were derived by arm D across 22 pairs (0-47 per pair). Each was built as
  its own library with the inherited L_g11 start, and walked on the pair's common residual.
- Taking the per-pair BEST of them (post-hoc, an upper bound on selection):

  | Library | Common-residual families |
  |---|---|
  | **Oracle-best promoted-dependent** | **9** |
  | Pristine promotable recipient (C) | 35 |
  | Arm D's actual g11 selection | 29 |

  | Contrast | Better / worse / tied | Two-sided p |
  |---|---|---|
  | Oracle vs C | 3 / 11 / 8 | 0.020 |
  | Oracle vs D | 3 / 9 / 10 | 0.036 |

## Reading (frozen asymmetric rule)
- Even PERFECT selection among the promoted-dependent schemas the next generation derives does not enable learning
  beyond a pristine recipient. Those schemas are WORSE transfer libraries than the plain ones g11 picks, and worse than
  pristine search.
- **The binding limit is upstream of selection**, in CANDIDACY / REPRESENTATION:
  - the one-hole LGG over observed W5 bodies proposes promoted-dependent schemas that are deeper re-fillings of what
    the plain path already derives (review finding: 23/23 eligible ones duplicate plain-derived schemas);
  - their instantiations push the useful plain bodies later in the walk.
- This sharpens the E6 diagnosis. Selection was not the real blocker.
- **The E2 lesson** (an endpoint-aligned acceptance rule) cannot rescue this. There is nothing better to select.
