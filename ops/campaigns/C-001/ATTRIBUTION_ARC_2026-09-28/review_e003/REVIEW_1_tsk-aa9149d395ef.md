# Adversarial review of E003_SYNTHESIS.md (at e6c8b5b2c)

**VERDICT: FOLLOWS WITH CORRECTIONS.**
- The narrow claim follows arithmetically: BEE r022153 is R3-VALIDATED under v4 + v5 as amended through C11, and NPE is not
  evidence either way.
- Three things do NOT follow:
  * s3's "validated in the strong sense ... each load-bearing" and s7's "plural field structure confirmed as necessary";
  * the unqualified "No ALTERED route fired";
  * "three independent tracers".
- The synthesis also omits that every BEE amendment made "before production" was made after a dry run on the SAME run and the
  SAME 32,827 births.

Abbreviations: S = E003_SYNTHESIS.md; P5 = ANCESTRY_PREREG_v5.md; P4 = ANCESTRY_PREREG_v4.md;
J = f9a93eb6d:roles/Bellerophon/e003_2026-09-29/production/E003_RESULTS.json (reading_A; reading_B is identical on every
field below unless stated).

## 1. R3 route recomputed from J: VALIDATED holds as written
| R3 condition (P5:38-49) | J field | value | result |
|---|---|---|---|
| identifiable >= 80% of non-NO_MATERIAL | `identifiable_share_nonNM` | 0.968172 [0.966119, 0.969949], n = 32644 (= 32827 - 183) | pass |
| TRANSMISSION >= 30 | `transmission_births` | 31401 | pass |
| Q8c upper bound < 5% | `Q8c_transmission` | 0.00115 [0.000984, 0.001336] | pass |
| (same, if R2's pooled estimand over all loci is meant) | `Q8c_all` | 0.00582 [0.005381, 0.00626] | pass |
| flip floor 0.50, point estimate (C4.4) | `flip_by_class.*.coverage` | self 0.82217 (4517/5494); other 0.543429 (1195/2199; CI [0.438785, 0.645698]); none 0.719689 (1389/1930) | pass, "other" MARGINAL |
| FAILED <= 1% | `failed` | 0 in every class | pass |
| completeness leak <= 5% | `completeness_by_class.*.leak_rate` | 0.0 | pass |
| round-trip | `roundtrip` | records 32827, check_failures 0, mismatches {}, PASS | pass |
| ALTERED lower bound >= 5% | as above | no pooled lower bound reaches 5% | none fires |
| predictions | `predictions` | P1 HOLDS (0.962031 >= 0.90); P5 HOLDS | no ALTERED consequence |

- `verdict`: A = B = VALIDATED; `READING_DEPENDENT`: false.
- S's spot-checks (S:23-25) match J exactly. On the frozen-as-amended text, the VALIDATED computation is correct.

## 2. "No ALTERED route fired" depends on C4.2, which was written after P2's outcome on this run was known
- In P4:238, P2 has the consequence "if it holds: ALTERED".
- The dry run (DRYRUN_BEE_r022153.md:44, :57) found P2 HOLDS -> ALTERED on r022153. Review 7 was then adjudicated
  (REVIEW_7_ADJUDICATION.md:18).
- After that, C4.2 (P5:132-134) demoted P2 to an "engine-native finding". Production P2 still HOLDS: 0.503797 [0.455696, 0.551899],
  n = 395 (`P2_native_target_disagrees_identifiable`).
- Without C4.2, the verdict is ALTERED, unless R3's clause "All three name the v0 field required" (P5:47) is read as already
  excluding P2.
- That reading is defensible, since an IBD correction to a native label is not a v0 field. But it is an interpretation adopted
  after exposure.
- C4 is labelled "BEFORE any production data" (P5:127). Production replayed the identical births (dry run 32,827/32,827,
  DRYRUN:17), so that label gives little protection.
- **Correction:** state that "no ALTERED route" rests on C4.2, which was adopted after the P2 outcome on this run was seen.
  Record that the pre-C4 text gives ALTERED.

## 3. C4.4 (point-estimate gating) was also set after the near-floor "other" class was seen on the same run
- Review 7 recorded "other" flip coverage of 0.537, CI [0.497, 0.651] (REVIEW_7_ADJUDICATION.md:20). C4.4 then chose point
  estimates (P5:137).
- In production, "other" is 0.543 with CI [0.439, 0.646]. A lower-bound gate would FAIL that class.
- Under addendum 3's reading, that makes the class INCONCLUSIVE. P5 does not say how a class-level INCONCLUSIVE maps to the
  engine verdict.
- C4.4 could have changed the BEE verdict. S s6 (S:77-78) lists only addenda 3/4/6 as post-exposure rulings. It omits C3 and C4.

## 4. Post-exposure rulings and repairs: did any change a threshold or endpoint, and could it change a verdict?
- **C9 (NPE labels; after G2):** no threshold changed. It moved NPE away from a possible INSTRUMENT_FAILED
  (P4:119-120, s4.3 arbitration).
  * It cannot change NPE's INCONCLUSIVE, because the <30 route is tracer-independent.
  * S:71 says "Every repair was followed by a fresh independent agreement set that passed". That is false for C9: the first
    fresh set after it FAILED on set M (P5:445-455). Only after C10 did fresh set 2 PASS (fresh2_result/FRESH_AGREEMENT.txt:27).
- **C10 (NPE MUTATION draw index and addr; reference repaired after seeing the owner):** it affects only MUTATION loci, which are
  non-MOVE and compared pre-mutation (P5:270). It cannot change any Q or the NPE verdict.
- **C11 (BEE, all-CONSTANT computations; both Archaeon-side tracers repaired after seeing the owner):**
  * Without it, production s4.3 is 0.9740 < 0.995 in written_other (P5:506). Under P4:119-120 that is INSTRUMENT_FAILED,
    "unresolved at arbitration".
  * So C11 changed the verdict route from INSTRUMENT_FAILED to VALIDATED. The ruling is textually sound: P4:55 says "CONSTANT bases
    dropped", with the NPE C6 B4 precedent (P5:207).
  * P4:187 assigns arbitration to the INDEPENDENT reviewer, so C11 is valid only if this review accepts it. I accept the reading.
  * **But the "independent" test of the repair is almost empty.** The repaired shape occurs on 1 locus of fresh set 2 (one `["F", []]`,
    BEE_FRESH2_ARCHAEON.jsonl line 408). It occurs on 0 loci of the `["C", []]` kind.
  * The production failure had 68 loci, 3 of them `C` (bee_production_agreement/BEE_FRESH_DISCREPANCIES.jsonl: 6 of 136 records).
  * The only substantive test is the post-exposure production re-run (bee_production_agreement_C11/NOTE.md:8, "NOT independent").
  * Also, the owner's result lists C11 among "readings made and ruled before production" (E003_BEE_RESULT.md, Declared limits).
    It was ruled after the production outputs were compared.
- **Addendum 3 (flip floor revived; post-exposure to the NPE v1 tallies):**
  * P5:11 says R1 "replaces v4 s2.1", and the P4:275 dated note says the same. R3's INCONCLUSIVE list (P5:41-42) dropped
    "flip coverage floor fails" (compare P4:128).
  * Reviving the floor is therefore a post-exposure reading, not the literal text. For BEE it is only stricter, and BEE passes it.
    For NPE see finding 5.
- **Addendum 4 (dep-vacuous loci stay in the denominator):** BEE has `dep_vacuous_loci` 271, class split not given. The worst
  case is all 271 in "other" and all covered: (1195-271)/(2199-271) = 0.479, which FAILS.
  * That case is implausible. In "other" the only groups outside {X, performer} are INPUT, whose suppression is 0.000377
    (`Q8c_whether_by_class.other.INPUT`). Vacuity should fall in "none", where even the worst case is 1118/1659 = 0.674.
  * For BEE this was a pre-output ruling (BEE_AGREEMENT_DECLARATION.md:19). It is very unlikely to change a verdict. Still, report
    the per-class split.
- **Addendum 6:** it affects marks only. Gates use point estimates. It cannot change a verdict.

## 5. NPE "INCONCLUSIVE by two routes": one route is solid; the other is a post-exposure reading, and SPEC_DEFECT is an alternative
- **The R3 route is solid.** "The transmission class (R5) has fewer than 30 births" (P5:42) is implied by C7.4's 29 distinct births
  (P5:272-274), which were fixed before production. The class is a subset of the births, so it has <= 29 < 30 births.
  * This rests on C7.4's de-duplication. With the 34 raw births the route would not be automatic.
  * The route decided NPE before any data. E-003's NPE leg could never have returned VALIDATED or ALTERED.
- **The flip-floor route rests on addendum 3's revival** of a clause that v5 said it replaced (finding 4).
- **Precedence problem.** P4:177 makes the coverage floor an s4 threshold ("coverage floor per s2.1"). SPEC_DEFECT ("s4 thresholds
  fail ... not explained by a named channel absent from s1", P4:121-122; kept "as in v4", P5:39) outranks INCONCLUSIVE.
  * Once the floor is revived, the frozen text arguably returns SPEC_DEFECT for NPE, not INCONCLUSIVE. The data-as-code residue
    is an applicability limit, not a named channel.
- **Correction:** "INCONCLUSIVE (R3 <30, fixed by design); the flip floor also fails, which under a strict reading is
  SPEC_DEFECT". Neither label is evidence about v0.
- **Correction:** S:7 says "NOT BROKEN anywhere". For NPE no BROKEN channel search is recorded. Say "no BROKEN route fired".

## 6. Section 3 overreaches
- **S:28-29 and S:83** ("validated in the strong sense"; "a single 'parent' field would lose each of these"; "confirmed as
  necessary"): R3 VALIDATED tests sufficiency (Q8c, expressibility, round-trip). No preregistered test compares v0 with a
  single-parent schema.
  * The one verdict-bearing number points the other way: a singular-donor value record misstates only 0.00115 of transmission
    loci.
  * These are unpreregistered descriptive claims presented as validation.
- **Item 1** (Q1 0.141238, n = 32654): supported as descriptive.
- **Item 2:** the numbers are right (`Q8c_whether_by_class.other.P` 0.926312; `self.P` 0.016401). But the non-donor that other-class
  births depend on IS the performer, so this is item 1 again, not an independent field.
  * Randomising the donor/writer suppresses births in 0.734197 (`Q8c_whether.W`), so existence dependence is the norm.
  * C4.1 defined Q8c-whether as a v0 dependence entry, so "v0 represents this" holds by construction.
- **Item 3:** 0.169485 (`Q4_material_without_capability_transmission`) is right. But production does NOT support "capability-WITH-
  CONDITIONS is needed".
  * Host-assisted capable 0.816767 vs isolated 0.810095. Incapable-in-isolation-but-host-capable is 0.007311 of births, about 240.
  * The dry run on the same births found the "other" class 0.8077 [0.6538, 0.9615] host-assisted capable (dry51_r022153.json:93-96,
    DRYRUN:104). If that held, the figure would be about 0.14 x 0.81 = 0.11 of births, not 0.007.
  * This unexplained ~15x discrepancy undercuts "relational capability" (REVIEW_7_ADJUDICATION.md s1), which S s5 (S:58-60) leans
    on for thr-c64dca3118a1. S does not mention it.
- **Item 4:** the numbers are right. But:
  * P2's evaluation set was changed after the data (C3), and its verdict role was removed (C4.2).
  * Review 7 found 183/191 of the disagreements are frame-shifted copies, i.e. positional shift-blindness (REVIEW_7_ADJUDICATION.md:16).
  * "Now measured on production data" re-measures the dry run's births; it is not a fresh test.
  * "BEE's ... label is not a descent label" (S:38-39) should be scoped to "in r022153" (the owner scopes it that way).

## 7. Wording and generalisation (L1-L2 scope)
- There is no explicit inherit/heredity wording about BEE. It is good that S:51 and S:61 restrict to L1-L2.
- **S:60** "which entity is the replicator is a per-lineage empirical question": lineage is L3+ and is not measured by E-003.
- **S:63-64** "resemblance and value match are not descent. Byte-level causal ancestry is measurable and agrees across three
  independent tracers" is unscoped and overstated:
  * NPE production agreement was two-way (reference vs owner; GO_FINAL_ADDENDUM_3.md:8);
  * the reference was repaired by Archaeon after exposure (C10, C11);
  * Archaeon's tracer is written by the spec author and was also repaired (C11);
  * "value match" was not measured as a separate endpoint.
- **S:10** "one cell (VM_COPY, SHARED, OPCODE mutation, task INC)" names 4 of about 14 config axes (r022153.config.json: NICHES,
  NOVELTY, MED rate, ENDOGENOUS_COPY, ...). The v5 population cell is VM_COPY + SHARED + ENDOGENOUS_COPY. Say "one run".

## 8. Omissions a reader needs in order to disbelieve the synthesis
1. **Same-run dry run.** C3, C4.2, C4.4 and the NO_MATERIAL class-gate change (BEE_AGREEMENT_DECLARATION.md:33-35) were all set after
   r022153's data were seen (findings 2 and 3).
2. **Per-class and non-MOVE Q8c.**
   - `Q8c_by_class.none` = 0.241941 [0.162042, 0.329772]. Its lower bound exceeds 5%. Gated per class, this is ALTERED-WEIGHTED
     (62 births).
   - `Q8c_by_class.NO_MATERIAL` = 0.214; `Q8c_nonmove` = 0.30851.
   - R3 is pooled, so the verdict stands. The numbers are still verdict-relevant and absent from S.
3. **Dependence-set precision** is 0.134-0.226 by class (`completeness_by_class.*.precision`): other 0.136, none 0.165, NO_MATERIAL
   0.134. Under the original R5 gate (P5:62-64) that is OVER-TAINT -> INSTRUMENT_FAILED. C1 (pre-draw) made it non-gating.
4. **Instrument drift on identical births** between the dry run and production:
   - Q8c on transmission: 0.0003 [0.0002, 0.0004] vs 0.00115 [0.00098, 0.00134], non-overlapping;
   - Q8c over all loci: 0.027 vs 0.0058;
   - transmission class: 30,945 vs 31,401;
   - Q4 host-assisted: see finding 6.
   All are far from 5%, but the drift is unexplained.
5. **Arbitration.** VALIDATED depends on this reviewer accepting C11 as the P4:187 arbitration (finding 4). The persisted ORIGIN
   attributes are untested (S:79 records this).
6. **NPE could not have decided at all.** The leg was INCONCLUSIVE by design before any data (finding 5), so "BEE and NPE" in the
   title is effectively one BEE run.
7. **Omitted by-design Q.** Q5 (by-design, descriptive, P4:143) is not reported (`Q5_drift_null` NOT_COMPUTED). The round-trip
   covers only reported Qs.

## Required corrections (minimum)
1. Qualify "No ALTERED route fired" with C4.2 and the pre-C4 ALTERED outcome.
2. Add C3 and C4 (same-run, post-dry-run) to s6.
3. Delete or relabel as descriptive "validated in the strong sense", "a single parent field would lose each", and "confirmed as
   necessary".
4. Drop "capability-with-conditions is needed", or explain the Q4 host-assisted discrepancy.
5. NPE: "INCONCLUSIVE (R3 <30, by design); flip-floor route is a post-exposure reading; strict reading SPEC_DEFECT". Replace
   "NOT BROKEN" with "no BROKEN route fired".
6. Replace "three independent tracers".
7. Fix S:71 (C9's first fresh set failed). Report the C11 fresh-set exposure (1 locus).
8. Report `Q8c_by_class.none`, `Q8c_nonmove`, `Q8c_all` and precision.
