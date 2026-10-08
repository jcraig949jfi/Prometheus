# E1 REPORT: R8 SATURATION vs INTERFERENCE vs REPRESENTATION CEILING (fresh supply)

Beta-03 (C-011). Pre-registration: beta03/windows/E1_PREREG.md, frozen before data, with AMENDMENT A1 (red team, also
pre-data). Evidence tier 2, local CPU engine.
- **Receipts:** beta03/runs/E1/{E1_RESULT.json, E1_DONORS.jsonl, E1_LIBRARIES.json, E1_COMMON_RESIDUAL.json,
  E1_START_*, E1_RECIP*.jsonl, E1_RECIP_INDEX.json}.
- **Log:** beta03/runs/E12_chain.log.

## 1. Dispositions
- **Technical: CLEAN.**
  - Donors 11:43Z; libraries and common residual frozen 12:35-13:04Z.
  - Recipients from 13:08Z. The chain was stopped once for the compute cap, and the run resumed from completed rows.
  - Scoring finished 14:18Z.
  - The library and common-residual hashes were ledgered before the recipients ran.
- **Supply:**
  - 22 usable pairs (A 24, B 22; seeds 103 and 105 failed the extras rule). That meets the >= 18 requirement.
  - **Common residual: 329 of 704 slots.**
- **Known answers:** K1, K1b, K2 (the reducer reproduces W01), and K3 (+ Beta-02 pairs 66/57) all PASS.
- **Positive control (opportunity set):** PASS. The best arm (L_P) acquires 35 common-residual families across 12
  pairs.
- **Disposition: MEASURED.**

## 2. Frozen labels

| Label | Result | Basis |
|---|---|---|
| **SATURATION_SUPPORTED** | **YES** | Own-start deficit L_g11 - L_P = **-104** (1 better / 20 worse / 1 tied, p one-sided = 2e-6; Holm-rejected). **Headroom share 0.933.** End-state non-inferiority holds: L_P is NOT better at end state (L_g11 388 vs L_P 363; 3 better / 8 worse / 11 tied for L_P; p = 0.97) |
| INTERFERENCE_SUPPORTED | **NO** | Common-residual contrast L_g11 - L_P = **-7** (2 / 4 / 16; two-sided p = 0.44). The test was ATTAINABLE: k = 6 nonzero pairs, minimum two-sided p 0.031 |
| REPRESENTATION_CEILING_CONSISTENT | **NO** (condition 4 failed) | 7 pairs had a recipient extending its inherited schema. 2 of them (pairs 87->111 and 93->117) acquired 2 common families each. See s4 for why this is weak evidence either way |

**Answer to the directive's Q1:** yes. On fresh, unexposed supply, **R8's failure is caused mostly by unequal
residual learning headroom.**
- 93% of the inherited library's own-start deficit disappears when every arm is scored on the same opportunity set.
- The inherited library ENDS at the highest competence: 388 vs 363 reachable families.
- A small residual deficit on identical opportunities (-7) is not significant. Interference is not supported.

## 3. Measures

| Measure | L_g11 | L_I0 | L_P |
|---|---|---|---|
| A. Inherited capability (start vs PRISTINE) | **143** | 44 | 0 |
| C. New acquisition on the common residual | 28 (10 pairs) | 24 (8) | 35 (12) |
| Own-start improvement (Beta-02 measure, secondary) | 33 | 88 | 137 |
| D. End-state reach | **388** | 355 | 363 |
| Failed opportunities (of 329) | 301 | 305 | 294 |
| Derived schemas / behaviour classes (median) | 5 / 5 | 4 / 7.5 | 3.5 / 7.5 |

- The best arm acquires **10.6%** of the common residual. **89% of opportunities unsolved by every start library stay
  unsolved by every recipient.**
- **Candidate ordering:** on the 339 families reached by both the L_g11 and L_P recipients, the median charge ratio
  is 1.00. There is no ordering penalty where both succeed.
- **Donors:** g11 @ O10 selected MEMORISE in 0/24 seeds; I_0 @ O4 in 11/24. This replicates Beta-02 (11/22).
- **Inherited capability on unseen lineages replicates Beta-02:**

  | Library | Beta-03 (22 pairs x 32) | Beta-02 (20 pairs) |
  |---|---|---|
  | L_g11 | 143 | 104 |
  | L_I0 | 44 | 32 |

## 4. Caveats (frozen in A1, plus what the data show)
1. **Composition of the inherited schema is OFF for transplanted recipients** (held = []). H3 is tested in E3/E5, not
   E1. That is why the ceiling label is a weak instrument here.
2. **The extending recipients' acquisitions are NOT attributed** (E1 has no extension attribution; E5-N does).
   - On the two extending pairs (111, 117), the pristine recipient acquired 2 and 1 common families, against the
     extending recipients' 2 and 2.
   - Failing condition 4 means "not consistent with a ceiling at this resolution". It is **not evidence of enabling**:
     the enabling test is -7, n.s.
3. **The 25% and 5/3 thresholds were set after the W01 diagnostic.**
4. **The share compares a cell-level own-start measure with a family-level common measure.**
5. **427 identical programs occur in both seed blocks.** Part of inherited capability may be memorised overlap,
   although g11 libraries are abstraction-only (MEMORISE 0/24).

## 5. Implications (qualifiers only; per CLOSE_RULE these do not change the recommendation)
- Any R8 assay, on any substrate, must score next-generation learning on a **common, pre-recipient residual
  opportunity set**. The own-start-censored endpoint mainly measures how much the inheritance already solved.
- The natural-world question that remains is whether promotion lets inheritance ENABLE learning on the 89% of residual
  opportunities that no arm reaches. That is E5-N's P1, run after the compute roll-off.
