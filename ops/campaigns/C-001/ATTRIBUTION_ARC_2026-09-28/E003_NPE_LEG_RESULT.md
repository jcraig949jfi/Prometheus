# E-003 NPE leg: result under the frozen rules (Archaeon, 2026-09-29)
**Status:** NPE leg = INCONCLUSIVE, by two independent frozen routes.
- This is a statement about the INSTRUMENT'S reach on this data. It is not a finding about ancestry.
- It neither validates, alters nor breaks attribution v0.

## Evidence chain (all committed)
- **Production run 2:** Nestor 81895e729. GO_FINAL v2 (dedbc208e); the run-1 invalidation is recorded.
- **Tracer agreement** (v4 s4.3 on every birth; addendum 3): the frozen reference vs the owner, raw.
  * 29 distinct births: 1.0 on every field in every class; 0 discrepant loci of 34.
  * The instrument's LABELS are therefore not the limitation.
- **s4 instrument gates** (s4 v2.2, 17670fed @ b0f215348): CONFORMS by 2 of 2 fresh replicas (tsk-81146cfae322,
  tsk-d907522d6a14; review_s4v22/ @ f8b589b2d). Class key K_R1 (addendum 3), C7.2 prefix flip rule, C4.4 point-estimate gates,
  R1.3 literal (addendum 4).

  | gate | self | other | TIED |
  |---|---|---|---|
  | flip coverage (floor 0.50) | 159/496 = 0.321, FAIL | 48/168 = 0.286, FAIL (marked MARGINAL, CI 0.127-0.653) | 8/32 = 0.25, FAIL (SINGLE_CLUSTER) |
  | FAILED share | 0, PASS | 0, PASS | 0, PASS |
  | completeness leak over applicable bytes | 0, PASS (applicability 0.79-0.98) | 0, PASS | 0, PASS |

## Why INCONCLUSIVE
1. **v4 s2.1 floor** (in force per C4.4; addendum 3): every gated class is below 50% flip coverage, so every class is
   INCONCLUSIVE.
   - Mechanism, owner's report C7.2: in NPE the copied bytes are executed BEFORE their final store. That residue is irreducibly
     INAPPLICABLE to a flip test.
   - Coverage fails because the flip test cannot DECIDE most identified loci. It is not failing them: FAILED is 0 everywhere.
2. **v5 R3:** INCONCLUSIVE if the transmission class (R5) has fewer than 30 births. The unit is 9 simulations / 29 distinct
   births (C7.4), so the transmission class is <= 29 < 30 whatever the identification outcome.
   - This route was fixed by the prereg and the frozen unit BEFORE any production data. The instrument gates could not have
     changed it.
   - Recorded as a DESIGN finding: the NPE cell's T-003 corpus is below R3's minimum. It is recorded for the final reviewer and
     any future design.

## What may and may not be said
- **MAY:**
  * the NPE tracer is reproducible and agrees exactly with the independent reference on production births;
  * the flip test cannot confirm most NPE identifications because of data-as-code execution;
  * the corpus is below the R3 minimum.
- **MAY NOT:**
  * any Q value as a finding;
  * any "inherited" or "transmitted" wording. L5 is NOT MEASURED (CVTR_RECONCILIATION.md; 29/29 children carry the painting
    signature).

## Open, non-blocking
- The 1% interaction sample: 10/11 files destroyed by the unauthorized run 3 (addendum 5). An operator decision is conditional
  on Nestor's copy search. It cannot change this status.
- Marks only (no gate can change):
  * SF2 ruled in addendum 6;
  * SF1 (a superseded docstring) noted.

## Dated correction 2026-09-29 (after the E-003 synthesis review; review_e003/)
- "INCONCLUSIVE by two independent frozen routes" is corrected. Only the R3 route (TRANSMISSION < 30; 29 distinct births) is a
  clean frozen route, and it was fixed by design: the NPE leg was uninformative by construction.
- The flip-floor route rests on addendum 3's post-exposure revival of a floor that v5 R1/R3 had dropped. Under a strict
  reading, the same failure is SPEC_DEFECT, which outranks INCONCLUSIVE.
- Neither label is evidence about v0. The original text above is kept.
