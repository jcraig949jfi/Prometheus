# RED-TEAM REVIEW: E1 + E2 FROZEN PRE-REGISTRATIONS (before any outcome)

Beta-03 (C-011). Reviewer: red-team subagent, 2026-10-08. Scope: E1 (beta03/windows/E1_PREREG.md, engine/v2b/b03.py,
FREEZE_E1.json) and E2 (beta03/windows/E2_PREREG.md, engine/v2b/b03_e2.py, engine/v2b/g12.py, FREEZE_E2.json).
Read-only. No frozen file was modified. The only computation was a dry-run of the frozen E1 report rules, copied
verbatim into a scratch script and applied to the FROZEN Beta-02 R8 files (beta02/runs/R8/*). This used no walks and
no donors, and took under 1 CPU-min.

State checked: beta03/runs/E1 does not exist and beta03/runs/E2 holds only E2_KNOWN.json. No E1 or E2 outcome exists,
so every "amend before data" item below is still permissible.

## Dry-run: frozen E1 rules applied to Beta-02 R8 data (diagnostic, not evidence)
My copy of the e1_report logic reproduces the W01 diagnostic exactly:
- 301 common slots;
- acquisition on the common residual: 30 / 32 / 37;
- interference contrast -7, with 1 better / 4 worse / 15 tied.

The frozen rules would then output:

| Machinery | share | PC | INTERFERENCE | SATURATION | REPRESENTATION_CEILING | disposition |
|---|---|---|---|---|---|---|
| g11@O10 (E1's machinery) | 0.928 | PASS (30 families, 7 pairs) | False | **True** | **True** | MEASURED |
| I_0@O4 (not in E1) | 0.717 | FAIL (8 families, 2 pairs) | False | **True** | False | INCONCLUSIVE_NO_POSITIVE_CONTROL |

So on the data that generated the hypotheses, the frozen E1 rules give SATURATION + REPRESENTATION_CEILING. Several
findings below show why the second label is close to automatic, and why the first is emitted even when the assay
cannot adjudicate.

---

## E1 findings

### E1-1 BLOCKER: the compositional-extension detector cannot see SCHEMA_ALL selections; a Beta-02 counter-example would be missed
- **Where:** b03.py:184-189 reads only `L_g11[0].get("schema")` and the recipient's `selected_schema`.
  - When the donor or the recipient selects SCHEMA_ALL, the entry has `schemas`, not `schema`, and `selected_schema`
    is None. The pair is then silently skipped.
  - composes_on (b03.py:135-141) also recognises only hole substitution, inherited[H := x]. It does not recognise the
    wrapping form op(inherited, atom), which is the form the engine's own composition move produces
    (a18.compositions).
- **Concrete Beta-02 case (pair 42 -> 66, g11 machinery):**
  - The inherited schema is `(acc + {H})`.
  - The L_g11 recipient selected SCHEMA_ALL, which contains `(acc + ({H} + v))` and `(acc + ({H} - v))`. Both are
    exact substitution-extensions of the inherited schema.
  - That recipient acquired **5 common-residual families**.
  - The frozen detector records nothing for this pair. REPRESENTATION_CEILING's fourth condition ("no extending
    recipient acquires anything") therefore stays True, and the label fires on the Beta-02 data.
- **Similar cases:** pair 29 -> 53 (the inherited library is SCHEMA_ALL) is skipped. Pair 33 -> 57,
  `(acc + {H})` -> `((acc + {H}) + v)`, is a wrapping extension that acquired 5 and is also not detected.
- **Action: amend before data.**
  - Iterate over every template in the inherited entry (`schema` or `schemas`) and every template in the selected
    entry.
  - Detect both substitution and wrapping (the a18.compositions form).
  - Extend K3 with the pair-66 and pair-57 rows as known positives. This is outcome-free.

### E1-2 BLOCKER: the positive control is measured on the treatment arm, so the strongest interference outcome becomes INCONCLUSIVE
- **Where:** b03.py:196-198 and :203. PC requires that the L_g11 recipients acquire >= 5 common families across
  >= 3 pairs, and INTERFERENCE_SUPPORTED requires PC.
- **Failure scenario:** strong interference.
  - Say L_g11 acquires 0-4 on the common set while L_P acquires about 37, as in Beta-02.
  - PC then fails, so the disposition becomes INCONCLUSIVE_NO_POSITIVE_CONTROL and INTERFERENCE cannot be emitted.
  - SATURATION is still emitted: in the dry-run with L_g11 forced to 0, the share is still about 0.7.
- The PC is supposed to show that the assay contains learnable mechanisms. That is a property of the opportunity set,
  not of the arm under test.
- **Action: amend before data.** Define PC on the max over arms, or on L_P (or on L_P or L_I0 if "after inheritance"
  is read literally). Report the L_g11-only count descriptively.

### E1-3 MAJOR: labels are emitted when the assay cannot adjudicate, and SATURATION has no floor guard
- **Labels are not gated on disposition** (b03.py:202-212). The labels dict is computed regardless of `disp`, so a
  result can read `disposition = INCONCLUSIVE_NO_POSITIVE_CONTROL` together with `SATURATION_SUPPORTED = True`. The
  I_0-machinery dry-run shows exactly this.
- **SATURATION does not require PC.** The share formula is `1 - I1/S1`, clamped to 1.0 when I1 >= 0 (b03.py:195).
  - The formula is well defined and sign-correct in every case. S1 >= 0 cannot label, because S1 < 0 is required,
    and |I1| > |S1| gives share < 0, which correctly fails.
  - However, share -> 1 whenever acquisition on the common residual is at the floor for both arms. That is H3's
    prediction, not H1's.
- **Action: amend before data.**
  - Emit the labels only when the disposition is MEASURED.
  - Require PC for SATURATION.
  - Add H1's positive prediction: end-state non-inferiority, D(L_g11) >= D(L_P) summed (W01: 366 vs 361). Without it,
    "deficit vanishes on equal opportunity" cannot be told apart from "nothing is learnable on equal opportunity".

### E1-4 MAJOR: REPRESENTATION_CEILING_SUPPORTED is close to automatic, partly calibrated on W01, and confounded with machinery
- **Close to automatic.** Its conditions are:
  1. PC (30 vs 5 needed in W01);
  2. enabling NOT significant (the absence of a low-powered effect is counted as support);
  3. best arm < 25% (W01: 12.3%);
  4. the vacuous-or-blind detector (E1-1).
- **Calibrated on W01.** The 25% and 5/3 thresholds were frozen 6 minutes after the W01 diagnostic (ledger 05:20Z ->
  05:25:48Z) with its numbers in hand.
- **Confounded with machinery.** Transplanted recipients have `held = []` (gtc.py:145-146). This disables
  a18.compositions of the inherited schema (gtc.py:176), the only designer route to second-order structure (see
  Hestia dossier s3c). So "the inherited abstraction is never extended" is partly a property of the transplant path,
  not of the grammar. The 25% threshold is also not separated from budget, escrow or observation limits.
- **Action:**
  - Amend before data: after the E1-1 fix, rename the label to REPRESENTATION_CEILING_CONSISTENT, or require
    condition 4 to be non-vacuous (>= 1 detected extension) and report "untested" otherwise.
  - Report-only caveat: composition-of-inherited is OFF for transplanted recipients (as in Beta-02 R8), so H3 is
    tested in E3/E5, not here.

### E1-5 MAJOR: INTERFERENCE may be unattainable at alpha 0.05, and the power statement is wrong
- **Where:** prereg s7 says "powered to detect LARGE interference only".
- The two-sided exact sign-flip minimum p is 2/2^k, where k is the number of nonzero pairs. With 5 nonzero pairs
  (W01: 1/4/15) the minimum is 0.0625, so p < 0.05 is impossible **regardless of effect size**. At least 6 nonzero
  pairs are needed.
- Recipients that learn the same schema produce exact ties (most of W01's ties). This structure is expected to recur.
- **Action:** report-only caveat, stated before data. Report k and the attainable minimum p next to I1. A null with
  k <= 5 is "unattainable", not "no large interference".

### E1-6 MAJOR: INTERFERENCE cannot separate search interference from selection-gate saturation
- g11 machinery accepts a candidate by its subset-benefit over the recipient's own INHERITED library on VALIDATE
  (gtc.py:110-133). If the L_g11 start already solves the validation families, an otherwise useful new schema can be
  ineligible.
- That is saturation acting at the selection stage, yet it would surface as C(L_g11) < C(L_P) and be labelled H2.
- The recipient rows do not persist the selection table or the derived schemas (b02._donor, b02.py:159-163 drops
  them), so this cannot be diagnosed afterwards.
- **Action: amend before data.** This is outcome-free instrumentation: persist `selection_table`, the derived schema
  list and the eligible count per recipient. Pre-register a descriptive decomposition of each L_g11 < L_P pair:
  (a) the L_P-learned schema was never derived by L_g11 (observation or search interference), or (b) it was derived
  but ineligible (selection-gate saturation).

### E1-7 MINOR: K2 does not test the new reducer
- **Where:** b03.py:253-255 only checks a constant in the diagnostic file. The docstring says it checks reproduction.
- My verbatim copy of the e1_report logic reproduces W01 exactly, which is reassuring, but the frozen code path
  itself is untested.
- **Action: amend before data.** Run e1_report's reducer on the Beta-02 R8 files as K2'. It is cheap and has no
  walks.

### E1-8 MINOR: hash integrity is self-referential
- E1_LIBRARIES.json and E1_COMMON_RESIDUAL.json store their own sha. `e1_recip` checks only that the residual file
  exists (b03.py:110), and `e1_report` never re-verifies the residual sha.
- **Action:** ledger both file shas before `e1 recip`, and verify them in the report.

### E1-9 MINOR: the headroom share mixes units
- Own-start gains are cell-level (`_gains`: the start is censored in *that* cell). The common residual is
  family-level (no start reaches in either cell). Families partially solved by a start count toward the own-start
  deficit but can never enter the common set, whichever arm owns them.
- **Action:** report-only. Decompose the own-start deficit into:
  (a) families the L_g11 start reaches;
  (b) partial-cell families;
  (c) the common residual.

### E1-10 MINOR: cross-block content overlap feeds inherited capability
- 427 identical (init, body, final) programs occur in both block A (donors) and block B (recipients), out of 5664
  distinct. Family names are unique (0 collisions), so there is no walk-key collision.
- L_I0 (g0_O4) often selects MEMORISE, so part of endpoint A is verbatim overlap rather than abstraction. This is
  content, not a membrane breach.
- **Action:** report-only caveat.

### Membrane (E1): no crossing found
- Recipients receive only `L["libraries"][d][lb]`, which is entries-only and sha-checked (b03.py:71-75, 113-114).
- Donors and recipients run in separate stages and processes.
- `_donor` args carry no donor state.
- The common residual is built from start walks only, and the runner refuses recipients until it exists.
- `_gains` keys (genome, seed, family, cell) do not collide: genomes `START|L_*` and `L_*|g11_O10` are distinct, and
  family names are globally unique. Walk dedupe by (lib, family, cell) is safe because walks are deterministic and
  names are unique.
- **Action:** none.

---

## E2 findings

### E2-1 MAJOR: the MEMO12 trap is arithmetically unfailable, and memorisation rejection is mostly a representation-keyed DL tax
- **MEMO12 cannot fail.** Each fold has 6 families, so reach_min <= 6 and S <= 6 - 0.25 x DL. Any DL >= 24 can
  therefore never be eligible. PLANT_MEMO costs 3 per program, giving DL 27-45 exposed, so the trap passes by
  construction.
- **Natural MEMORISE is close to unfailable too.** At DL 9-20 it needs a minimum fold reach of 3-6 out of 6.
- **The DL is effectively a type tax.** DL charges 1 per template whatever its complexity, but 1 per body for
  template-less entries (g12.py:82-87). The only template-less natural candidate is MEMORISE, so the penalty is
  functionally a type tax keyed on representation.
- MEMORISE is never named (verified: it appears only in the output flag g12.py:457 and the report count
  b03_e2.py:107). Even so, "rejects memorisation without a hard-coded exclusion" overstates what is shown.
- **Action: amend before data** (reporting-only).
  - Pre-register the λ = 0 rescore (g12.rescore, no new walks) per seed. Classify each natural-MEMORISE rejection as
    reach-driven or DL-driven.
  - Claim 2 counts only seeds where MEMORISE is I_0-eligible (attractive).
  - Report MEMO12 as a DL-only check.

### E2-2 MAJOR: "traps pass" does not require any trap to be attractive
- Claim 3 needs junk "that scores attractively on weak validation". NEAR was I_0-attractive on 0/4 exposed seeds.
  OFF is the unchanged Beta-02 junk. Yet YES (b03_e2.py:118-122) is granted with zero attractive traps.
- **Action: amend before data.** The claim-3 component counts (natural MEMORISE + plants) that are I_0-eligible AND
  rejected by g12, and needs >= 3 such seeds. Otherwise claim 3 is UNTESTED and G12_GENERAL_RULE is capped at
  INCONCLUSIVE.

### E2-3 MAJOR: NONINFERIOR is not a non-inferiority test
- **Where:** b03_e2.py:131-132. The rule is "neither one-sided test is significant, and the total ratio is >= 0.90".
  That is failure to reject plus a point estimate.
- With n of about 20 and many ties, g12 at 0.9 x g11 with p(g11 > g12) = 0.06 would be labelled NONINFERIOR.
- If tot g11 = 0, the condition is trivially true.
- **Action: amend before data.** Use a margin test: an exact sign-flip on d_i + δ_i, with δ_i = 0.10 x the seed's
  g11 gain (integer-scaled by 10), one-sided p < 0.05. Otherwise rename the label to NOT_SHOWN_DIFFERENT.

### E2-4 MINOR: Holm is anti-conservative on the g11 test
- **Where:** b03_e2.py:117 uses `min(p_g12>g11, p_g11>g12)` as a single p, which is half a two-sided p.
- **Action:** use `vs_g11["p_two_sided"]` in the Holm family. Labels are unaffected.

### E2-5 MINOR: no validity gate, and seeds can drop silently
- `report()` does not check E2_KNOWN or KNOWN pass and has no MEASUREMENT_FAILED.
- `_arm_libs` drops any seed that is missing a row (b03_e2.py:66-67). A g12 job that crashes or times out on a hard
  seed would leave the seed out of every arm.
- **Action: amend before data.** Record the dropped seeds, and set MEASUREMENT_FAILED if a usable seed is missing.
  Gate the labels on the known answers passing.

### E2-6 MINOR: the g11 comparator is coupled to E1 and carries a SCHEMA_ALL tax
- **Reusing E1's g11 rows is valid.** It is the identical b02._donor job, with the same seed filter, plan["O10"] and
  import order, and K1 shows determinism.
- **E2 now depends on E1_DONORS.jsonl being untouched.** Ledger that file's sha in the E2 report.
- **G12_VS_G11 partly measures the SCHEMA_ALL tax.** DL charges SCHEMA_ALL 3-7, and g11 does pick SCHEMA_ALL (seen in
  the R8 rows).
- **Action:** report-only. Ledger the sha, and split g12-vs-g11 by the type of g11's choice.

### E2-7 No action: INHERITED as gain 0, non-eliminating, fold and plant fairness
- When g12 selects INHERITED, the library is exactly pristine, so its gain is 0 by construction. This holds for every
  arm and introduces no bias.
- Non-eliminating (>= 50% of g11's non-INHERITED count) is not trivially satisfiable, because g11 selects on nearly
  every seed. Selections that do not transfer are caught by the vs-I_0 test.
- Joint-table arm picks are sound: PLANT_* keys never start with SCHEMA_, and the g12 arm excludes plants.
- No E2 outcome leaks into a construction. NEAR attractiveness reads only VALIDATE dev examples.

## Summary of recommended amendments (all outcome-free; E1/E2 data do not yet exist)
1. **E1-1:** fix the composition detector (SCHEMA_ALL plus the wrapping form); extend K3 with the Beta-02 pair 66/57
   rows.
2. **E1-2:** define PC on the opportunity set (max arm, or L_P), not on L_g11.
3. **E1-3:** gate the labels on disposition MEASURED; SATURATION requires PC plus end-state non-inferiority.
4. **E1-4:** make the ceiling label non-vacuous, or rename it to _CONSISTENT; state that composition-of-inherited is
   off under transplant.
5. **E1-6:** persist the selection tables and derived schemas for recipients.
6. **E2-1 / E2-2:** λ = 0 rescore as a descriptive receipt; claims 2 and 3 count only attractive-and-rejected cases.
7. **E2-3:** replace NONINFERIOR with a margin test.
8. **Report-only:** E1-5 (k nonzero and attainable p), E1-9, E1-10, E2-4, E2-6.
