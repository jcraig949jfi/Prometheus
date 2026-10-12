# E2 PRE-REGISTRATION: g12 ENDPOINT-ALIGNED SELECTOR (fresh-seed confirmation)

Beta-03 (C-011), prepared early in W01 (W03's DEV work, advanced because the selector lead delivered early). It runs in
W04 / EXP, or as soon as the block-A supply and E1 donors exist. Frozen before any E2 outcome.
Directive s5. Starting hypothesis: beta02/E4_DESIGN.md.
- **Implementation:** branch aphrodite/b03-g12 @ 6c03a218f (selector lead), merged.
  - engine/v2b/g12.py;
  - tests 16/16 PASS (engine/v2b/G12_IMPLEMENTATION.md).
- **Runner:** engine/v2b/b03_e2.py. Hashes are in beta03/FREEZE_E2.json.

## 1. Question
g11 excludes MEMORISE BY NAME (a hand-coded candidate-type ban). **Does a selector that scores candidate libraries by
endpoint-aligned REACH, with a description-length penalty and never naming MEMORISE, retain transferable
abstractions, reject memorisation and attractive junk, and transfer to fresh families?**

## 2. g12 (frozen parameters = g12.params())
- **Folds:** VALIDATE (12 families) is split into 2 seeded folds of 6 (`APHRODITE/B03/G12/FOLDS/<seed>`).
- **Walks:** each candidate library is walked on all VALIDATE cells (a17.R_VAL per family) to a **selection cap of
  100k**, tribunal T4 v1a (BOTH), max spurious 10k. The exact prefix-decomposition shortcut is used (verified 0/480
  differences against full walks).
- **Reached family:** the candidate qualifies in a cell where INHERITED is censored.
- **Score:** S = min over folds (families reached) - **0.25 x DL**.
  - DL counts what an entry states: 1 per schema template, 1 per explicitly listed body, and non-default
    inits/finals.
  - MEMORISE is never named. A renaming test passes.
- **Eligibility:** S > 0, and every reached program is tribunal-qualified.
- **Choice:** max S; ties broken by qualified-walk charge saving vs INHERITED (censored = cap), then min sha256.
- **E4 fallback is OFF** (decision D1). When nothing is eligible, g12 selects INHERITED. That counts as gain 0, and it
  is counted against "non-eliminating" below.
- **The tie-break is confirmed as implemented** (decision D4).
- Width O10, VALIDATE 12, PRISTINE start. Instruments are identical to Beta-02/E1.

## 3. Supply and arms
- **Seeds:** block A, W8 LIN 72-95. They are never used in Beta-01/02, and E1 uses them only as DONORS (E1's outcome
  is measured on block B).
- **A seed is usable** iff the role and extras rules pass. **>= 18 usable seeds are required,** otherwise
  SUPPLY_LIMITED.
- **Arms** (paired on the same seeds and roles):

  | Arm | Content |
  |---|---|
  | I_0 @ O10 | original acceptance; new rows |
  | g11 @ O10 | **reused from E1's block-A donors** (an identical job; the K1 path) |
  | **g12 @ O10** | the treatment |
  | NULL12 | the OFF junk plant under g12 |
  | MEMO12 | memorised plant under g12 (the observed programs verbatim) |
  | NEAR12 | near-miss plant under g12: the best-supported derived schema with its root operator swapped; a mechanical generator, no outcome read |

  All four g12 arms are picks over ONE g12 table per seed. Each candidate's score is independent of the other
  candidates, verified on 300 tables.

## 4. Endpoint
Beta-02 E1 endpoint: held-out TRANSFER families (32 per seed) reached at <= 1M in >= 1 of 2 cells, with PRISTINE
censored.

## 5. Frozen decision rules (unit = seed; exact sign-flip tests)
- **Traps pass:** all of the following.
  - NULL12, MEMO12 and NEAR12 each select their plant in <= 2 seeds.
  - The natural MEMORISE candidate is selected by g12 in <= 2 seeds.
  - The near-miss trap's ATTRACTIVENESS (eligible under the recorded I_0 diagnostic table) is reported descriptively
    (decision D2). Its rejection carries information only where it is attractive.
- **Non-eliminating:** g12 selects a non-INHERITED library in >= 50% as many seeds as g11 does.
- **G12_GENERAL_RULE:**
  - **YES** iff g12 vs I_0 @ O10 has one-sided p < 0.05 with sum > 0, AND traps pass, AND non-eliminating;
  - **NO** iff sum <= 0, OR traps fail, OR eliminating;
  - **INCONCLUSIVE** otherwise.
- **G12_VS_G11:**
  - **SUPERIOR:** g12 > g11, one-sided p < 0.05;
  - **INFERIOR:** g11 > g12, one-sided p < 0.05;
  - **NONINFERIOR:** neither of the above, AND total g12 >= 0.90 x total g11;
  - **INCONCLUSIVE:** otherwise.
- **Holm at 0.05 over the two primary tests** is reported alongside.
- **If g12 fails, g11 remains the established positive control.** The g12 outcome does not determine which
  representation experiment runs (directive).

## 6. Known answers (outcome-free): PASS
- **K4** (beta03/runs/E2/E2_KNOWN.json): via this runner's import path, a g12 job on EXPOSED Beta-02 seed 26
  reproduces the lead's smoke receipt exactly (arm choices + S/eligible table).
- **Lead tests 16/16:**
  - per-job reset;
  - reproduction of Beta-02 rows for g10 / g0 / g11 in the same worker as g12;
  - prefix shortcut 0/480;
  - independence of arms across 300 tables.
- **Import-order guard:** `a18.TAG == 'T51'` is asserted in every g12 job (a defect class found by both leads; it
  affects no historical run, because all historical runners imported b02/r7e first).

## 7. Power and honesty notes (stated before data)
- **Proxy:** if g12 behaved like g11, power vs I_0 @ O10 at N = 20-24 is about 0.99 (Beta-02 g11 - I_0 @ O10
  per-seed diffs).
- **Exposed smoke (4 biased seeds, development only):** g12 25 vs g11 29 vs I_0 8. **A G12_VS_G11 = INFERIOR outcome
  is plausible** and will be reported as such.
- **The MEMO12 plant is rejected almost automatically by DL** (27-45 entries). It mainly tests the penalty. The
  natural MEMORISE count is the more informative memorisation test.

## 8. Compute
- About 13-19 core-h for 24 seeds: g12 jobs about 5 CPU-min each, I_0 rows, plus about 7 new libraries per seed walked
  on 64 transfer cells.
- Rolling-cap check before launch.

## AMENDMENT A1 (pre-data; red-team; no E2 outcome existed)
Supersedes s5 where it conflicts.
1. **Claim 2, rejects memorisation without a ban (E2-1).**
   - It is tested only on seeds where MEMORISE is ATTRACTIVE, meaning eligible under the recorded I_0 diagnostic
     table.
   - **PASS** iff >= 3 attractive seeds AND g12 rejects MEMORISE in >= 80% of them. **UNTESTED** if < 3 attractive.
     **FAIL** otherwise.
   - A pre-registered **lambda = 0 rescore** (g12.rescore, no new walks) is reported. It shows whether rejection comes
     from the fold-minimum or from the DL penalty.
   - The MEMO12 plant remains a DL check only.
2. **Claim 3, rejects attractive junk (E2-2).** It is tested only on seeds where PLANT_NEAR or PLANT_OFF is eligible
   under I_0. The same PASS / UNTESTED / FAIL rule applies.
3. **G12_GENERAL_RULE:**
   - **NO** iff (sum vs I_0 <= 0) OR traps fail OR eliminating OR claim 2 FAIL OR claim 3 FAIL;
   - **YES** iff the transfer test vs I_0 is positive AND claims 2 and 3 PASS (plus the trap and non-eliminating
     rules);
   - otherwise **INCONCLUSIVE**. That includes a positive transfer test with an UNTESTED claim.
4. **NONINFERIOR (E2-3)** is now a real margin test:
   - delta = 10% of g11's mean per-seed gain;
   - exact one-sided sign-flip on 10*d + round(10*delta) > 0;
   - it also requires g11's total > 0.
   - SUPERIOR and INFERIOR are unchanged.
5. **Holm (E2-4)** uses two-sided p values.
6. **Gate and receipts (E2-5, E2-6):**
   - MEASUREMENT_FAILED if E2_KNOWN does not pass;
   - dropped seeds are listed;
   - the sha256 of E1_DONORS.jsonl (the reused g11 rows) is recorded.
   - Note that DL also taxes SCHEMA_ALL (report-only).
