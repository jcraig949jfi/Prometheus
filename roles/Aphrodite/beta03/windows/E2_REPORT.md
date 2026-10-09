# E2 REPORT: g12 ENDPOINT-ALIGNED SELECTOR (fresh-seed confirmation)

Beta-03 (C-011). Pre-registration: beta03/windows/E2_PREREG.md, frozen before data, with AMENDMENT A1 (red team,
pre-data). Evidence tier 2.
- **Receipts:** beta03/runs/E2/{E2_RESULT.json, E2_DONORS.jsonl, E2_INDEX.json, E2_WALKS.jsonl, E2_KNOWN.json}.
- **Reused:** E1's g11 rows, with their sha recorded in the result.
- **Log:** beta03/runs/E12_chain.log (donors, 2026-10-08 12:02-12:35Z) and beta03/runs/D2_chain.log (scoring,
  2026-10-09 05:15-05:48Z, after the compute roll-off).

## 1. Dispositions
- **Technical: CLEAN.** 24/24 seeds (block A, LIN 72-95); no dropped seeds; K4 known answer PASS.
- **Scientific: MEASURED.**

## 2. Frozen readouts

| Readout | Result |
|---|---|
| **G12_GENERAL_RULE** | **INCONCLUSIVE** |
| **G12_VS_G11** | **INFERIOR** (frozen one-sided rule) |

**Transfer**

| Measure | Value |
|---|---|
| Totals (24 x 32 held-out families beyond PRISTINE) | I_0 94; g11 179; **g12 142** |
| g12 vs I_0 @ O10 | +48; 13 better / 6 worse / 5 tied; **one-sided p = 0.053** (misses 0.05) |
| g12 vs g11 @ O10 | -37; 3 better / 11 worse / 10 tied; g11 > g12 one-sided p = **0.048** |
| Holm (two-sided, over both) | neither rejected (p2 = 0.106 and 0.096) |
| Non-inferiority to g11 (margin 10% of g11 mean) | NOT shown (p = 0.83) |

**Claims**

| Claim | Status | Detail |
|---|---|---|
| 2: rejects memorisation without a ban | **PASS** | MEMORISE was attractive under I_0 in 18 seeds; g12 rejected it in **18/18**. **The lambda = 0 rescore also selects MEMORISE in 0 seeds**, so the rejection comes from the fold-minimum REACH requirement, not from the description-length penalty |
| 3: rejects attractive junk | **UNTESTED** | The near-miss and OFF plants were attractive under I_0 in 0 seeds. The amendment then caps the label at INCONCLUSIVE |
| Traps | pass | NULL12 / MEMO12 / NEAR12 plants selected in 0/24 each; natural MEMORISE selected by g12 in 0/24 |
| Non-eliminating | pass | g12 selects a non-INHERITED library in 20 seeds, against g11's 24 |

## 3. Reading
1. **The memorisation lesson generalises.**
   - An acceptance rule that scores REACH on unsolved validation families, requires it in both folds, and never names
     memorisation, rejects the memorised library in every seed where it tempted I_0.
   - It does so even with the size penalty switched off.
   - The hand-coded ban (g11) can be replaced by an endpoint-aligned criterion as far as **rejecting memorisation** is
     concerned.
2. **But g12 is a worse SELECTOR of transferable abstractions than g11** on this supply.
   - g12 142 vs g11 179. It keeps the inherited library in 4 seeds, where g11 always selects.
   - Where the two differ, g12 usually picks a schema that transfers less.
   - The fold-minimum reach criterion with 6 families per fold is sparse: it under-rewards abstractions whose benefit
     shows as charge savings rather than new reach at the 100k selection cap.
3. **Against I_0, g12 improves transfer** (+48, 13/6/5). It misses the frozen threshold narrowly (p = 0.053). Under
   the rules that is not a YES.

**Answer to the directive's Q2:** partly.
- **YES**, g12 learns to reject memorisation without a hand-coded ban (18/18, independent of the penalty).
- **NOT ESTABLISHED** that it prefers transferable abstractions as well as g11 does. It is INFERIOR on the frozen
  one-sided rule, though not Holm-significant.
- **g11 remains the established positive control** (directive s5).

## 4. Caveats
- Claim 3 could not be tested: no junk was attractive. The red team (E2-2) predicted this, and it is why the label caps
  at INCONCLUSIVE.
- The MEMO12 plant is rejected by the penalty almost automatically (DL 27-45). The informative memorisation test is the
  natural MEMORISE count (claim 2).
- **Selection cap 100k vs transfer cap 1M:** reach at 100k can miss abstractions that pay off nearer 1M. This is an
  open design risk recorded in E4_DESIGN s5. It is plausibly part of the gap to g11, but not tested here.
- Per CLOSE_RULE, E2 sets qualifiers only: the TFS-1 M2 g12 arm stays descriptive, because G12_GENERAL_RULE is not
  YES.

## 5. CORRECTIONS from the independent adversarial review (labels unchanged)
- g12 is a DESIGNED rule. "Learns to reject memorisation" overclaims. The correct statement: **an endpoint-aligned
  acceptance rule rejects memorisation without naming it** (18/18 attractive seeds; also at lambda 0).
- INFERIOR is effectively a two-sided test at alpha 0.10 (one-sided p 0.048 in the opposite direction). It is not
  Holm-significant.
