# E5-N REPORT: R8 UNDER REPRESENTATION PROMOTION, NATURAL WORLD (+ E6 attack, negative branch)

Beta-03 (C-011).
- **Pre-registration:** beta03/windows/E5N_PREREG.md.
  - Frozen before any E1 or E5 outcome.
  - Amendments A1 (red team, pre-data), A2 (receipts, pre-data) and A3 (technical rerun 1/3, neutral bookkeeping
    repair).
- **E6 runner:** frozen (engine/v2b/b03_e6.py).
- **Evidence tier 2,** local CPU engine.
- **Receipts:**
  - beta03/runs/E5N/{E5N_RESULT.json, E5N_RECIP.jsonl, E5N_SHAM_LIBRARIES.json, E5N_SHAM_START_*, E5N_RECIP_INDEX.json,
    E5N_RECIP_WALKS.jsonl, E5N_KNOWN.json};
  - beta03/runs/E6/E6_NEGATIVE_DIAGNOSIS.json;
  - log beta03/runs/D2_chain.log.

## 1. Dispositions
- **Technical:**
  - TECHNICAL_FAILURE at 73/88 jobs (07:09Z): a repeated-hole selected schema in the output-promotion bookkeeping.
  - Repaired by **A3**: neutral; selection and transfer unaffected; K5a-K5e PASS.
  - Resumed, and the stages ran to completion by 07:34Z (**technical rerun 1 of 3**).
- **Gates:**
  - **No-op continuity:** the promotable pristine arm equals E1's ordinary pristine arm in **22/22** pairs.
  - **Positive control:** PASS (best arm L_P: 35 common-residual families).
  - **Sham pairs:** 22/22 (a redrawn panel sham where needed).
- **Scientific: MEASURED. R8_UNDER_PROMOTION (natural) = NO.**

## 2. Frozen readouts (unit = pair; common residual from E1, 329 slots over 22 pairs)

| Arm (machinery g11 @ O10) | Common-residual acquisition | Own-start improvement |
|---|---|---|
| A: L_P, ordinary (E1) | 35 | 137 |
| B: L_g11, ordinary (E1) | 28 | 33 |
| C: L_P, promotable | 35 (= A, the no-op gate) | 137 |
| **D: L_g11, promotable** | **29** | 34 |
| E: L_I0, promotable | 24 | 88 |
| F: L_SHAM, promotable | 11 | 8 |

| Test | Result |
|---|---|
| **P1, enabling D - C (sole confirmatory)** | **-6; 3 better / 4 worse / 15 tied; p one-sided = 0.82.** ATTAINABLE (k = 7, minimum p 0.008). **NOT positive** |
| P2, promotion effect D - B (descriptive) | +1 (one pair) |
| SHAM D - F (residual minus sham-start reach) | +25; 9/0/13; p = 0.002 |
| SECOND-LEVEL (attributed depth-2 with acquisition in >= 3 pairs) | **1 pair** (pair 99) |
| Non-trivial depth-2 SELECTED (arm D) | 4 pairs (99, 102, 111, 117) |
| Pairs deriving promoted-constituent schemas (arm D) | 19 / 22 |
| REORDER / EXTEND split of arm D's common acquisitions | 28 / **1** |
| Channel status | **OPEN** (derived, selected and acquired, at least once) |
| **KILL_CRITERION_HESTIA (proxy)** | **FIRES** (22 pairs >= 20; P1 not positive; attributed depth-2 fraction 0.045 < 0.10) |
| Max dependency depth observed | **2** (selected: 4 pairs; attributed with acquisition: 1 pair) |

**On the sham result:** it shows the g11 library is a better inheritance than a frequency-matched sham library. It does
NOT show enabling, because P1 (vs pristine) is negative. YES would have required all of P1, SECOND-LEVEL and SHAM.

## 3. E6 attack: negative branch (frozen, mechanical; beta03/runs/E6/E6_NEGATIVE_DIAGNOSIS.json)
- **Global first broken link:** **STATISTICAL: P1_ENABLING + SECOND_LEVEL_COUNT.**
  - Every mechanical link (no-op, supply, candidacy, selection, transfer) was traversed by at least one pair. The chain
    is open, but too rarely and too weakly to change acquisition.
- **Per-pair broken link** (22 pairs):

  | Link | Pairs |
  |---|---|
  | **SELECTION** | **15** |
  | CANDIDACY | 3 |
  | TRANSFER | 3 |
  | NONE (pair 99, complete) | 1 |

  - **SELECTION (15):** promoted-constituent schemas are derived, and often ELIGIBLE, but g11 selects a plain schema.
  - **CANDIDACY (3):** nothing promoted-dependent is derived.
  - **TRANSFER (3):** a depth-2 schema is selected, but it has no EXTEND acquisition.
- **Example (pair 96):** derived `P(({H} - v))` and `P(gcd(|{H}|, |v|))`. Both were eligible; g11 selected
  `(acc + {H})`.
- **The single complete chain** (pair 99): the inherited P = `(acc - {H})` became a constituent of the selected
  `P(({H} - v))`, expanding to `(acc - ({H} - v))`. That library reached 1 common-residual family whose first
  qualified program needs a body outside G5.

## 4. Cost (both ledgers; donor phase)
- Arm D used **3.5x** the search charges of the pristine promotable arm: 614M vs 175M.
- Its expanded execution units were 6.52e9, against 5.42e9 promoted units. The promotion overhead ratio is about 1.20.
- Promotion is never billed as free on the transfer endpoint: every candidate costs 1 and libraries hold expanded
  bodies.
- **Economic break-even is not reached:** +1 attributed family for about 4.4e8 extra search charges vs the
  promotable pristine arm.

## 5. Reading (answers to the directive)
- **Q3 (can an endogenous abstraction become a composable primitive with exact semantics?): YES.**
  - Exact semantics: 15,360 cases, 0 mismatches.
  - Hashed, serialisable, transplantable.
  - In 19/22 natural pairs the next generation DERIVES schemas built on the inherited primitive.
- **Q4 (does promotion expose genuinely new attainable second-order structure?): MARGINALLY.**
  - In 1/22 pairs, an attributed depth-2 schema reached 1 family that only a promotion-built body solves.
  - The structured-world test (E5-H) is INSTRUMENT_UNVALIDATED.
- **Q5 (does inherited knowledge make new learning better under promotion?): NOT ESTABLISHED in this engine.**
  - P1 = -6, n.s., and attainable.
  - The dominant obstacle is SELECTION: the acceptance rule prefers plain schemas over eligible promoted-dependent
    ones.
- **Q6 (maximum clean dependency depth): 2,** in a single pair. That is below the pre-registered multiple-lineage bar
  (>= 3).

Per CLOSE_RULE (row 4): **MIGRATE_SUBSTRATE**, with:
- BASIS = OUTCOME_C_APPARATUS_LIMIT;
- S10_KILL_CRITERION = NOT_MET (the structured-world known-positive control failed);
- KILL_CRITERION_HESTIA_PROXY = FIRES.

Wording that recursion is refuted is not used.

## 6. CORRECTIONS from the independent adversarial review (beta03/reviews/INDEPENDENT_ADVERSARIAL_REVIEW.md)
The labels are unchanged; all were re-derived and confirmed. Wording and interpretation are corrected:
1. **Q6, corrected.**
   - "2, in a single pair" violates CLOSE_RULE's wording requirement. **Q6 = NOT ESTABLISHED in this engine.**
   - The pair-99 depth-2 acquisition was never attacked: the E6 dependency ablation runs only on the positive branch.
   - Context: the ordinary arm in pair 99 selected the same schema in plain form. It instantiates 6 bodies vs 167 and
     did not reach the family.
2. **Q4, corrected.**
   - "A family that only a promotion-built body solves" is wrong. W8 families have base-grammar witnesses. The correct
     statement is that the FIRST qualified program found lay outside G5.
   - **New finding:** all 23 eligible promoted candidates (8 pairs) expand to schemas the SAME recipient also derived in
     plain form. Promotion adds deeper hole fills, not new candidate schemas.
   - **The limit is upstream of selection** (candidacy / representation).
3. **"SELECTION 15/22", corrected.**
   - The frozen E6 runner counts every pair that derived but did not select. By the prereg's own definition ("eligible
     and rejected by g11") the split is:
     - **6 pairs** rejected an eligible promoted candidate;
     - **8 pairs** had none eligible;
     - **1 pair** had bare re-expressions only.
   - Pair 116 is a tie-break between two spellings with identical savings.
   - **The s3 pair-96 example is wrong:** the gcd candidate was INELIGIBLE.
4. **The sham control is degenerate.**
   - The sham recipient observes 0 programs in 19/22 pairs. On the sham residual it acquires 1 family vs 33 for the
     pristine promotable arm.
   - The significant SHAM test shows only that the g11 recipient learns at all.
   - It also shows that **a non-solving inherited library interferes strongly**.
   - Hypothesis (untested): the inherited prefix (>= 57,960 candidates in 21/22 g11 and all sham libraries) exceeds the
     30k observation escrow.
