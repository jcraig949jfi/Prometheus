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

## AMENDMENT A1 (pre-data; red-team beta03/reviews/REDTEAM_E5N_PREFREEZE.md; no E1/E5 outcome existed)
Supersedes s5/s6 where they conflict. Known answers K5a-K5d re-run: PASS.
1. **Attributed depth-2 (E5N-1 BLOCKER).** In the first promotion generation, P(x) can merely re-spell a plain
   extension.
   - **A pair counts as SECOND-LEVEL only if** arm D's SELECTED library has a non-trivial depth-2 schema AND >= 1
     acquired common-residual family's FIRST qualified program has a body that lies OUTSIDE G5 (a17.g5_bodies) and
     belongs to a promoted-form entry of the selected library. Such a body exists only through promotion.
   - Every arm's common acquisitions are split into **REORDER** (body in G5) and **EXTEND** (body outside G5), as
     W5P_DESIGN s6(b) requires.
2. **Sham (E5N-3).**
   - L_SHAM is the first panel sham, in a seeded order, whose schema is NOT among the pair's L_g11 / L_I0 templates.
     If there is none, the pair has no sham and is excluded from the SHAM test.
   - The SHAM test (D - F) is scored on the common residual MINUS the families the sham START reaches.
   - Arm F is excluded from the positive-control maximum.
3. **Confirmatory test and NO qualifiers (E5N-4).**
   - **P1 (D - C) is the SOLE confirmatory test.** P2 is descriptive, and the Holm family is removed.
   - Every NO carries qualifiers:
     - whether P1 is attainable at 0.05 (nonzero pairs);
     - **channel status:** CLOSED_CANDIDACY (no promoted schema derived in arm D), CLOSED_SELECTION (derived, never
       selected non-trivially), OPEN_NO_EXTEND_ACQUISITION, or OPEN.
   - **Caveat:** a natural-world NO does not by itself trigger retirement without the structured-world (E5-H)
     known-positive control.
4. **Receipts (E5N-5).** Rows now carry the selection_table (K5d). The negative-branch diagnosis can therefore
   compute SELECTION.
5. **KILL_CRITERION_HESTIA (E5N-6), mechanical.**
   - **FIRES** iff >= 20 pairs AND P1 is not positive AND the attributed depth-2 fraction (item 1) is < 10% of pairs.
   - **NOT_EVALUABLE_N_LT_20** if there are < 20 pairs.
   - **DOES_NOT_FIRE** otherwise.
   - The improvement measure is common-residual acquisition (the E1 primary).
6. **E6 attack, re-specified mechanically (E5N-2).** It applies only if the label is YES_PENDING_E6. For each
   SECOND-LEVEL pair:
   - **(a) PLAIN control:** arm D's selected library with every body outside G5 removed (entries left empty are
     dropped). The same transfer cells are re-walked.
   - **(b) SHAM swap:** in each depth-2 selected schema, the inherited primitive id(s) are replaced by the id of
     promote(pair's L_SHAM schema). The schema is re-instantiated (w5p.promote.instantiate) and re-walked.
   - **"Drop"** = strictly fewer acquired common-residual families than arm D.
   - **DEPENDENCY_CONFIRMED** iff the drop occurs under BOTH (a) and (b) in >= 2/3 of the SECOND-LEVEL pairs.
   - **(c) Label scramble:** entry `name` fields are renamed to seeded random strings on 2 pairs. Walk results must be
     identical (invariance).
   - **(d) Unseen lineages:**
     - Supply: W8 LIN 120-127 (generated by the unchanged w8_lin.py, the T51 foundry/roles/extras pipeline).
     - Pairing: block-A donor seeds 72..79 in order -> 120..127.
     - Arms C and D only. Common residual from the L_P / L_g11 starts.
     - **Pass rule:** sum(D - C) > 0 AND at most 1 pair worse.
   - **R8_UNDER_PROMOTION = YES** iff YES_PENDING_E6 AND DEPENDENCY_CONFIRMED AND (c) holds AND (d) passes.
     Otherwise NO_AFTER_ATTACK, with the failed component named.
7. **Billing (E5N-7, report-only):**
   - Every transfer candidate costs 1 charge and libraries hold expanded bodies, so promotion is never billed as one
     free operation.
   - The execution-size ledgers cover the donor phase only.
   - Larger depth-2 entries delay the fallback walk, which biases arm D toward NO.
8. **No-op gate (E5N-8): no change.** Caveat: P1 effectively compares promotable L_g11 with pristine-ordinary.

## AMENDMENT A2 (pre-data; receipts only; no E5 outcome exists)
- **b03_e5._w5p_run** also records the FULL derived-schema list (`derived_schemas`), using a per-job spy on
  w5p.promote.derive_schemas. The computation is unchanged. This makes E6's SELECTION diagnosis exact rather than
  bounded. Known answers K5a-K5e PASS.
- **The E6 runner is frozen** (engine/v2b/b03_e6.py, built by the representation lead @466b3457f and cherry-picked;
  its known answers K6a-K6j PASS, beta03/runs/E6/E6_KNOWN.json).
  - It implements s6 and A1 item 6 mechanically.
  - Pairs without a sham count as "no drop" under (b), which works against YES.
  - Re-walks are limited to common-residual families.
  - (d) LIN 120-127 is about 6-7 core-h (an extrapolated estimate). It runs only on YES_PENDING_E6, and only within
    the cap. If it cannot finish by the hard stop, CLOSE_RULE row 2 applies.

## AMENDMENT A3: TECHNICAL RERUN 1 of <= 3 (2026-10-09 07:20Z; after a TECHNICAL_FAILURE, no E5-N outcome inspected)
- **The failure.** `b03_e5.py recip` stopped at 73/88 jobs (07:09Z). In `donor_w5p`, the OUTPUT-promotion bookkeeping
  of a recipient's selected schema raised: `ValueError: promotion needs exactly one hole:
  '(acc - math.gcd(abs(math.gcd(abs({H}), abs({H}))), abs(v)))'`.
  - The schema's hole occurs twice, so it is not a unary-linear primitive under the W5P contract (call-by-value =
    textual expansion only when the argument occurs once).
  - No start-library template has a repeated hole (checked); the schema arises from the recipient's own LGG.
- **The repair** (scientifically neutral):
  - The `_w5p_run` wrapper patches, per job, `Promoted.from_schema` for `source_kind == "selected_entry"` ONLY. Such a
    schema gets an UNPROMOTABLE stand-in record: schema, deps, and depth = 1 + max dep depth, so depth attribution is
    preserved. It is listed in the row as `unpromotable_selected`.
  - Selection, selected entries and transfer are computed BEFORE this step, and are unaffected.
  - For every job without such a schema the wrapper behaves identically. That includes all 73 completed rows, which
    are kept.
  - Known answers K5a-K5e re-run: PASS.
- **Resume:** the remaining 15 jobs (resumable), then score / report / E6 diagnose.
- **Exposure disclosure:** while locating the traceback, one log line of the L_P (no-op) arm was seen (seed 116,
  selected `(acc + {H})`). That arm is constrained to equal E1's ordinary row. No other E5-N row was read.
