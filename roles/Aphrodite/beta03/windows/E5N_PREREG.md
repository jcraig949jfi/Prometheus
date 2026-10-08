# E5-N PRE-REGISTRATION: R8 UNDER REPRESENTATION PROMOTION, NATURAL WORLD (+ W5P freeze decisions, + E6 attack)

Beta-03 (C-011). This is W05/W09 DEV work, advanced into W02. It is frozen before ANY E1 or E5 outcome exists. The E1
chain had not started: it is waiting for supply B.
Directive sections 6 (E3 W5P), 8 (E5) and 9 (E6). Evidence tier 2.
- **W5P implementation:** branch aphrodite/b03-w5p @1e169a577, merged; engine/w5p/W5P_DESIGN.md; 11/11 tests PASS.
- **Runner:** engine/v2b/b03_e5.py. Hashes are in beta03/FREEZE_E5N.json.

## 1. Question
When a learned abstraction can become a composable primitive, does an inherited g11-produced library ENABLE the next
generation to acquire more NEW, tribunal-qualified, transferable structure than a pristine recipient? And does any
such acquisition depend computationally on the inherited abstraction (depth >= 2)?

## 2. W5P decisions, frozen here (the representation lead's D1-D5)
- **D1. Observation is unchanged.** It does not walk promoted applications, so it is identical for every arm and
  comparable with E1 and Beta-02. Promoted forms enter only through derivation and candidacy. (Limitation: a
  first-generation depth-2 schema needs the pattern to be recognisable in observed bodies.)
- **D2. Bare re-expressions P({H}) of an inherited primitive stay as candidates** (the same for every arm). They
  NEVER count as a depth-2 mechanism.
- **D3. Scope.** All promotion comparisons are made WITHIN W5P machinery (arms C-F). The ordinary arms A and B come
  from E1 with identical g11 machinery, used only for the "promotion effect" contrast P2. Both cost ledgers are
  reported: search charges, plus expanded and promoted execution units.
- **D4. A depth-2 claim needs a SELECTED schema** with dependency depth >= 2 that is not a bare P({H}). A schema that
  is merely derived does not count.
- **D5. The composition move on promoted primitives is OFF.** Transplanted recipients have held = [], as in
  Beta-02/E1. No designer composition move is added.

## 3. Supply, arms, membrane
- **Recipients:** E1's block-B pairs (LIN 96-119; pair d <-> d + 24) and **E1's FROZEN common-residual set**. That
  set is built from start walks only and hashed before any recipient runs.
- **Donor libraries:**
  - E1's frozen, hashed L_g11 / L_I0 / L_P;
  - **L_SHAM:** the start library of a W8 panel sham (PA..PD, frequency-matched to G1 on the U supply), drawn per pair
    by a seeded rule `APHRODITE/B03/E5N/SHAM/<d>`. No outcome is read. It is hashed in E5N_SHAM_LIBRARIES.json.
- **Machinery:** the W5P donor with rule g11 @ O10 and promotion ON. Inherited schemas are promoted to
  P(x) := S[H := x] and can be constituents of newly derived schemas. Budgets, escrow (30k), cap (1M), tribunal (T4
  v1a), cell seeds and evaluator access are identical across arms. Only entry lists cross the membrane.
- **Arms:**

  | Arm | Source | Content |
  |---|---|---|
  | A | E1 | L_P, ordinary |
  | B | E1 | L_g11, ordinary |
  | C | new | L_P, promotable |
  | **D** | new | **L_g11, promotable** |
  | E | new | L_I0, promotable |
  | F | new | L_SHAM, promotable |

## 4. Measures
1. Inherited competence: the start libraries vs PRISTINE (from E1, plus the L_SHAM start walks).
2. **New acquisition on the common residual (PRIMARY):** the number of common-residual families the selected library
   reaches in >= 1 cell.
3. The own-start-censored improvement (Beta-02 measure, secondary).
4. Final competence.
5. Newly learned abstractions (derived-with-promoted counts).
6. **The abstraction-dependency DAG depth:** selected, and maximum.
7. Search charges.
8. Promotion overhead: expanded vs promoted execution units.
9. Economic break-even: acquisition per expanded unit (descriptive).

## 5. Frozen decision rules (unit = pair; exact sign-flip tests)
- **Measurement gate (NO-OP continuity):** arm C must equal arm A EXACTLY in every pair (selected schema, entries,
  n_observed, n_derived, classes). W5P with a pristine start promotes nothing. Otherwise **MEASUREMENT_FAILED**.
- **Positive control:** the best arm acquires >= 5 common-residual families across >= 3 pairs. Otherwise
  **INSTRUMENT_UNVALIDATED** (the assay cannot adjudicate).
- **P1, enabling:** D - C on common-residual acquisition, one-sided.
- **P2, promotion effect on the inherited library:** D - B, one-sided.
- **Holm at 0.05 over {P1, P2}.**
- **SHAM:** D - F, one-sided p < 0.05 and sum > 0.
- **SECOND-LEVEL:** >= 3 pairs in which arm D's SELECTED library has a non-trivial depth-2 promoted schema (D4) AND
  that pair acquires >= 1 common-residual family.
- **R8_UNDER_PROMOTION (natural):**
  - **YES_PENDING_E6** iff the gate and PC pass, AND P1 is Holm-significant with sum > 0, AND SECOND-LEVEL holds, AND
    SHAM holds. It becomes **YES** only if the E6 dependency ablation below confirms;
  - **NO** otherwise (gate and PC passing).
- **Not macro-renaming or cheaper billing:**
  - Transfer reach is measured by the unchanged walker, with every candidate charged 1 and libraries holding EXPANDED
    bodies. A promoted macro is never one free operation on the endpoint.
  - The expanded/promoted execution ledgers are reported.
- **If NO: the negative is preserved.** The grammar is not widened to rescue it (directive).

## 6. E6 attack, chosen mechanically now
- **If YES_PENDING_E6:**
  - For every SECOND-LEVEL pair, replace the inherited primitive inside arm D's selected depth-2 schema with arm F's
    (sham) primitive. Keep the base-grammar expressivity, re-instantiate, and re-walk the same transfer cells.
  - **DEPENDENCY_CONFIRMED** iff common-residual acquisition drops in >= 2/3 of those pairs.
  - Also re-run arm D on 8 further unseen LIN seeds (W8 regeneration 120+), recipients only, with the same libraries.
- **If NO:** a negative-branch diagnosis on the recorded rows, classifying the FIRST broken link:
  1. Were depth-2 schemas ever DERIVED in arm D (n_derived_with_promoted > 0)? If not: **CANDIDACY** (D1
     observation) or **REPRESENTATION**.
  2. If derived, were they eligible and rejected by g11? **SELECTION.**
  3. If selected but with no acquisition: **TRANSFER** or **SEARCH_BUDGET** (charges vs cap).
  4. Was the positive control met? **SUPPLY.**
  5. Did the no-op gate hold? **MEASUREMENT.**
- The structured-world test (E5-H, the W9-H ecology with a known-positive depth-two control) is pre-registered
  separately (W07/W09). It is a different claim from natural-world R8.

## 7. Known answers (outcome-free, EXPOSED Beta-02 data; beta03/runs/E5N/E5N_KNOWN.json): PASS
- **K5a:** W5P with promotion ON and a PRISTINE start reproduces Beta-02 E12 seed 25 g11_O10 exactly (the basis of
  the no-op gate).
- **K5b:** W5P with promotion OFF and the inherited Beta-02 R8 L_g11 (pair 25 -> 49) reproduces the Beta-02 R8
  recipient row for seed 49 exactly (transplant continuity).
- **K5c:** with promotion ON, the block is well formed.
  - Exposed illustration (not evidence): 2 schemas derived with promoted constituents; the selected schema was
    depth 1.

## 8. Power and expectations (stated before data)
- From W01: on the common residual, Beta-02's L_g11 vs L_P contrast was -7 (1/4/15). An ENABLING effect would have to
  reverse that.
- The exposed K5c run derived promoted-constituent schemas but did not select them.
- **The most likely outcome is NO, with the first broken link at SELECTION or CANDIDACY.** That is stated in advance.

## 9. Compute
- Sham start walks: about 1.5k.
- 96 W5P recipient donors at about 3-5 CPU-min each.
- Walks for about 3 new libraries per pair.
- **About 9-10 core-h.** It runs after the E1/E2 chain, with a rolling-cap check first.
