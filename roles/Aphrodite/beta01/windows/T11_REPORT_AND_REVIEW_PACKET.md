# T11 -- ABSTRACTION-ONLY CANDIDACY UNDER g10: REPORT + EXTERNAL-REVIEW PACKET

C-006 (C-P2B-APH-BETA-01), cycle 11, TEST window 11. Rung R3 via an improver-rule change. Evidence tier 2,
EXPOSED seeds.

| Item | Value |
|---|---|
| Spec | beta01/windows/T11_ABS_SPEC.md (t11_absonly.py f2b8442e..., frozen at 76b8c0190 before transfer data) |
| Receipts | beta01/runs/T11_ABS/{T11_RESULT.json, T11_DONORS.jsonl, T11_INDEX.json, T11_WALKS.jsonl, T11_KNOWN.json} |

## 1. Dispositions
- **Technical: CLEAN.**
  - Attempt 1; 45 donors; 256 new walks.
  - Ran 13:48-14:07Z with 4 workers, threads = 1, exit 0. About 1.3 core-h.
- **Scientific: MEASURED.** The gate passed:
  - K1 and K2 passed;
  - NULL11 selected OFF in 0/15 seeds; NULL11 total 123 <= 123 + 2;
  - MEMORISE selected in 0 seeds in every g11 arm (the mechanical check).

## 2. Frozen readouts

| Readout | Comparison | Totals | Better / worse / tied | Sign p | Frozen result |
|---|---|---|---|---|---|
| **ABSTRACTION_ONLY_POSITIVE** (primary) | g11 O10 vs g10 O10 | **123 vs 99** | **4 / 0 / 11** | **0.0625** | **NO** (p >= 0.05) |
| Secondary | g11 O4 vs g10 O4 | 101 vs 98 | 1 / 0 / 14 | 0.5 | NO |
| **IMPROVER_CUMULATIVE_POSITIVE** | g11 O10 vs g0 O4 | **123 vs 93** | 6 / 2 / 7 | 0.1445 | **NO** |

**The frozen labels are NO.** They are not upgraded on effect size or direction.

## 3. Per seed (gain of 32)

| Seed | g0 O4 | g10 O4 | g10 O10 | g11 O4 | g11 O10 | g11 O10 selection |
|---|---|---|---|---|---|---|
| 6 | 8 | 8 | 0 | 8 | **7** | (acc - {H}) (MEMORISE removed) |
| 12 | 0 | 0 | 0 | 0 | **4** | ({H} + v) |
| 13 | 7 | 7 | 0 | 7 | **7** | (v - {H}) (= K2) |
| 14 | 0 | 0 | 0 | 0 | **6** | SCHEMA_ALL |
| 9 | 0 | 0 | 5 | **3** | 5 | (acc + {H}) |
| 0 | 0 | 0 | 11 | 0 | 11 | (acc + {H}) |
| 7 | 0 | 0 | 3 | 0 | 3 | ({H} + v) |
| 4 | 0 | 5 | 7 | 5 | 7 | ({H} + v) |
| 1 | 10 | 10 | 5 | 10 | 5 | (acc + {H}) (validation-to-transfer mismatch, unaddressed) |
| 2, 3, 5, 8, 10, 15 | = | = | = | = | = | unchanged |

## 4. Reading
1. **Mechanism confirmed, at the selection level.**
   - Every seed where MEMORISE had won (T10: 6, 12, 13, 14) now selects an abstraction.
   - All four gain transfer: +24 in total.
   - **No seed is harmed (0 worse).**
   - With memorisation removed, observation breadth (T10) converts into reuse: g11 O10 vs g11 O4 = 123 vs 101.
2. **The frozen test is UNDERPOWERED by design, and that defect is Aphrodite's.**
   - g11 can only change seeds where MEMORISE wins, which is 4 seeds at O10.
   - A one-sided sign test over 4 non-tied seeds cannot go below p = 1/16 = 0.0625.
   - So the primary readout could NOT have been positive. The pre-registration should have either:
     - computed the attainable minimum p;
     - pre-registered a family-level paired test (128 family-cells per arm);
     - or required fresh seeds.
   - This is recorded as an INVALID_DESIGN component of the readout (power). The label stays NO; it is not collapsed
     into "no effect", and it is not upgraded.
3. **Cumulative (g11 O10 vs I_0): +30 transfer families (93 -> 123, +32%), 6 better / 2 worse.**
   - Better: seeds 0, 4, 7, 9, 12 and 14.
   - Worse:
     - seed 1 (10 -> 5): the validation-to-transfer mismatch between real abstractions;
     - seed 6 (8 -> 7).
   - p = 0.14: not positive.
4. **What can be said at tier 2 (exposed seeds):**
   - the direction is uniform in the treated seeds;
   - the size is large (+24 against g10 O10; +30 against I_0);
   - the mechanism is verified by the selection-level known answer (K2);
   - the frozen statistical claim is NOT met.
   - **No R7-positive label is issued.**

## 5. First broken rung now
- **Evidential:** the R3 repair needs an adequately powered, UNEXPOSED replication (fresh seeds), not another rule
  change.
- **Mechanistic residual:**
  - seed 1, the validation-to-transfer mismatch between two real abstractions;
  - seed 0 at O4, starvation that only observation breadth fixes.

## 6. Candidate T12 (for DEV-12)
A fresh-seed replication of the cumulative improver (g11 O10) against I_0 (g0 O4) and g10 O10:
- **Seeds:** new W8 LIN seeds (16+), with the T51 role rules.
- **Power:** pre-registered for power, with the attainable minimum p computed before freeze, and a family-level paired
  endpoint as co-primary.
- **Feasibility:** subject to supply (the T51 foundry per seed) and the 48 core-h cap. If it does not fit one window,
  T12 is a powered re-analysis design plus a SUPPLY_LIMITED disposition, not a forced run.

## 7. Attack questions
1. Is removing MEMORISE equivalent to a hidden content prior (abstractions are favoured by construction)? Counter: the
   rule names a candidate TYPE produced by every donor. It encodes no family or schema content; NULL11's planted OFF
   schema is still rejected 15/15.
2. Seed 14 selects SCHEMA_ALL (the union of all derived schemas). Is its gain of 6 due to one member? An ablation would
   answer this.
3. Would MEMORISE stop winning if validation were scored on the PRISTINE-censored endpoint instead of charge savings?
   That is the endpoint-aligned selection alternative. It is not tested here.
