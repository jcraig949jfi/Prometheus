# E4 -- ENDPOINT-ALIGNED ACCEPTANCE CRITERION (DESIGN ONLY; NOT RUN)

Beta-02 (C-007). This is a new improver hypothesis, **not a repair of g11**. g11 remains the experimental positive
comparator. **Nothing here is used to interpret E1-E3.** Execution needs its own pre-registration on supply that
E1-E3 never used (LIN 72+), after Beta-02 closes.

## 1. Why
I_0 and g10 accept a candidate library by CHARGE SAVINGS on validation cells. The transfer endpoint demands something
else: REACH. That means producing a tribunal-qualified program within budget on a held-out family the reference
library cannot solve.

On natural (lineage) supply, a memorised library earns large charge savings on families that PRISTINE already
solves, because exact programs recur among lineage siblings. Yet it reaches no censored family. g11 removes the symptom
by deleting a candidate TYPE. E4 asks whether scoring the property itself does the same job, generally.

## 2. The four classes the rule must separate

| Class | Charge savings (I_0/g10) | Endpoint-aligned signature |
|---|---|---|
| High local fit, poor transfer | high on solvable families | reach on 0 censored validation families |
| Reusable abstraction | moderate | reach on >= 2 censored validation families, in BOTH folds |
| Memorisation | high (exact-program recurrence) | reach (if any) only via verbatim stored programs; large description length |
| False-positive shortcut | variable | reach fails tribunal qualification (T4 v1a), or is matched by the planted junk control |

## 3. Candidate rule g12 (hypothesis)
1. **Split VALIDATE** (12 families) into two seeded folds of 6.
2. **For each candidate library C,** walk each validation cell to a SELECTION cap (100k, below the 1M transfer cap,
   for cost). reach_f(C) = 1 if C reaches a T4-v1a-qualified program in >= 1 of the family's cells AND INHERITED is
   censored there.
3. **Score:** S(C) = min(reach_fold1, reach_fold2) - lambda * (description length of C's added entries, in entries).
   - The min-over-folds term requires the benefit to replicate across disjoint families. That is the anti-shortcut,
     anti-single-family term.
   - lambda = 0.25 entries^-1, fixed before any run. A 4-entry memorised library must reach one extra family per fold
     to break even with a 1-entry schema.
4. **Eligibility and choice:** a candidate is eligible iff S(C) > 0 AND every reached program passes the tribunal. The
   max S is chosen; ties are broken by charge saving, then sha.
5. **Content-freedom:** no family labels, no schema content, no candidate-type names (unlike g11, MEMORISE is NOT
   named).

## 4. Pre-registration sketch (for a later freeze)
- **Arms:**
  - g12 @ O10;
  - g11 @ O10 (positive comparator);
  - I_0 @ O4;
  - NULL12 (OFF planted, the gate);
  - **MEMO-PLANT12:** a planted memorised library of the observed programs, scored under g12. It must NOT be chosen.
    This is the direct test that g12 recognises memorisation without naming it.
- **Supply:** fresh LIN 72+ (W8 generator), at least 24 seeds.
- **Readouts:**
  - g12 vs I_0 (exact sign-flip);
  - g12 vs g11 (two-sided: does the general rule match the type rule?);
  - MEMO-PLANT12 rejection rate.
- **Cost:**
  - selection walks: about 8 candidates x 12 families x 2 cells to 100k, so about 3x a g11 donor;
  - about 15 core-h for 24 seeds plus the transfer walks.

## 5. Open risks
- **Selection cap:** reach at 100k may miss abstractions that pay only nearer 1M (the budget-relative capability seen
  in A23/W2). The cap is a parameter to fix before data.
- **Lambda:** a description-length weight is a prior. A lambda sweep would be exploratory only, never label-bearing.
- **Fold design:** with 6 families per fold, sparse natural benefit may leave min(fold) = 0 too often (the T08 lesson
  in another form). The fallback (min-over-folds >= 1 OR total >= 3) must be frozen in advance, not chosen after data.
