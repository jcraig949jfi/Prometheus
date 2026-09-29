# Adversarial review: E003_SYNTHESIS.md (at e6c8b5b2c)

**VERDICT: FOLLOWS WITH CORRECTIONS.**
- BEE "VALIDATED" can be recomputed from E003_RESULTS.json under v5 through C11.
- It is conditional on two amendments the synthesis does not disclose as verdict-bearing: C4.2, which removed an ALTERED route after a dry run on this same run had fired it, and C11, a self-arbitrated repair that averted INSTRUMENT_FAILED.
- NPE INCONCLUSIVE holds by one clean frozen route, not two.
- Section 3 overreaches in several places.

Paths: S = ops/campaigns/C-001/ATTRIBUTION_ARC_2026-09-28/E003_SYNTHESIS.md; V4/V5 = ANCESTRY_PREREG_v4/v5.md; J = f9a93eb6d:roles/Bellerophon/e003_2026-09-29/production/E003_RESULTS.json.

## 1. Recomputing the R3 route from J (check 1): the numbers match
Readings A and B are identical on every field below.

| R3 / gate input | J field | value | rule | result |
|---|---|---|---|---|
| identifiable share | `reading_A.identifiable_share_nonNM` | 0.968172 [0.966119, 0.969949], n = 32644 | >= 0.80 (V5:41) | pass |
| transmission count | `reading_A.transmission_births` | 31401 | >= 30 (V5:42) | pass |
| Q8c upper bound, transmission (P5) | `Q8c_transmission` | 0.00115 [0.000984, 0.001336] | upper < 0.05 (V5:48) | pass |
| Q8c upper bound, all loci | `Q8c_all` | 0.00582 [0.005381, 0.00626] | upper < 0.05 | pass |
| flip coverage, self | `flip_by_class.self.coverage` | 0.82217, CI [0.788, 0.853] | point >= 0.50 (C4.4, V5:137) | pass |
| flip coverage, other | `flip_by_class.other.coverage` | 0.543429 (1195/2199), CI [0.438785, 0.645698] | point >= 0.50 | pass, MARGINAL |
| flip coverage, none | `flip_by_class.none.coverage` | 0.719689, CI [0.637, 0.791] | point >= 0.50 | pass |
| FAILED share | `failed_rate` | 0 in every class | <= 1% | pass |
| completeness leak | `completeness_by_class.*.leak_rate` | 0 | <= 5% | pass |
| round-trip | `roundtrip` | `{status: PASS, records: 32827, check_failures: 0, mismatches: {}}` | must pass | pass |
| verdict | `verdict` | `{A: VALIDATED, B: VALIDATED, READING_DEPENDENT: false}` | | |

- The spot-checked numbers at S:23-25 match J.
- **1a. Expressibility is asserted, not evidenced.** R3's second VALIDATED clause (V5:48, V4:136) requires every by-design Q to be expressible in v0.
  - Nothing in J records per-Q expressibility.
  - `roundtrip` does not list which Qs were recomputed.
  - `Q5_drift_null` and `Q8r_pdom_scope` are `NOT_COMPUTED`.
  - C4.1 requires Q8c-whether to be exported as a v0 DEPENDENCE entry (V5:129-131). Nothing shows that the round-trip covered it.
  - The clause therefore rests on the owner's statement alone.
- **1b. The "other" class passes by 95 loci** (1195 confirmed against the 1100 needed). Its CI lower bound, 0.439, is below the floor.
  - The pass exists only because of C4.4's point-estimate rule.
  - C4 was written "after Archaeon's BEE dry run" (V5:127) on this same run r022153. That dry run had already shown this class at 0.537, MARGINAL (DRYRUN_BEE_r022153.md:88, 105).
  - v4 s2.1 (V4:91) never said point or CI. C4.4 is therefore a post-exposure choice on the one class that it decides.
  - S:78 lists the post-exposure rulings but omits C3 and C4.

## 2. Omitted: the P2 ALTERED route was removed after it fired on this run (checks 3 and 6)
- The frozen P2 consequence (V4:238) is "if it holds: ALTERED". The v5 dry run on r022153 applied it and returned **ALTERED** (DRYRUN:44, 57).
- C4.2 (V5:133-134), written after that dry run and after Review 7, reclassified P2 as an "engine-native finding, not a verdict route".
- In production P2 HOLDS: `P2_native_target_disagrees_identifiable` = 0.503797 [0.455696, 0.551899], n = 395; `predictions.P2_engine_native` = "HOLDS".
- Without C4.2 the verdict is ALTERED (a native-label correction field), not VALIDATED.
- A textual defence exists: R3 already says "All three name the v0 field required" (V5:47). But the owner's own dry run did not read it that way.
- S:8 ("NO ALTERED route fired"), S:84 and S:38-40 need to state that this holds only under C4.2, which was made after exposure to this run.

## 3. Omitted: C11 turned a literal INSTRUMENT_FAILED into VALIDATED (check 3)
- The production s4.3 agreement failed: written_other label 0.9740 < 0.995, owner against both other tracers (V5:506).
- V4:119 says INSTRUMENT_FAILED "unresolved at arbitration". V4:187 says arbitration is "by the independent reviewer".
- In C11, Archaeon arbitrated the disagreement itself and repaired its own two tracers after seeing the owner's reading (V5:524-528).
- **Mitigations, which I accept on substance:**
  - the reading adopted is the literal v4 text (V4:55) and matches the NPE precedent (V5:517);
  - the labels are non-ENTITY, so no Q changes;
  - fresh set 2 passed 3-way with 0 discrepancies (bee_fresh2_result/BEE_FRESH_AGREEMENT.txt);
  - the repaired shape does occur in the fresh-set-2 outputs (BEE_FRESH2_REFERENCE.jsonl and BEE_FRESH2_ARCHAEON.jsonl contain `["C", []]`/`["F", []]`).
- **Remaining issues:**
  - This review is the arbitration the prereg calls for. S:70 presents C11 as a label repair, not as the step that decided INSTRUMENT_FAILED vs VALIDATED.
  - The post-C11 production re-run still shows owner ~ reference 7238/7239 on the self label (bee_production_agreement_C11/NOTE.md:7).
  - The fresh-set comparator skips CONST kind whenever the reference is a party (BEE_FRESH_AGREEMENT.txt:1).

## 4. NPE: "INCONCLUSIVE by two routes" (check 2)
- **The R3 "<30" route is valid and was fixed before any data.**
  - The C7.4 unit is 29 distinct births (V5:272-274), and the TRANSMISSION class is a subset of births, so it has at most 29 < 30 (V5:42).
  - Counting the 34 births including duplicates would be the only escape, and C7.4 excluded that before production.
  - The route guarantees the NPE leg could never have returned VALIDATED or ALTERED. S:19 says "by design"; S:8-9 should say the leg was **uninformative by construction**.
- **The flip-floor route is not an R3 route.**
  - R3 replaced v4 s2.4 (V5:38-48) and dropped s2.4's "flip coverage floor fails -> INCONCLUSIVE" (V4:128).
  - The floor was revived per class by addendum 3 §2 after the v1 tallies had been seen (GO_FINAL_ADDENDUM_3.md:26-44).
  - Nothing in R3 turns a per-class INCONCLUSIVE into an engine verdict.
- **A competing reading ranks higher.**
  - R3 keeps SPEC_DEFECT "as in v4" (V5:39), and SPEC_DEFECT means "s4 thresholds fail ... not explained by a named channel absent from s1" (V4:121).
  - The coverage floor is an s4.1 threshold (V4:177).
  - SPEC_DEFECT outranks INCONCLUSIVE, and on this reading the correct NPE verdict is SPEC_DEFECT (stop; amend the prereg).
  - Addendum 3 did not address this. It is PLAUSIBLE rather than certain, because the C7.2 residue was anticipated as irreducible (V5:263-264).
- **Correction:** "INCONCLUSIVE by one frozen route (R3 <30); the flip-floor route rests on the addendum-3 ruling; SPEC_DEFECT not excluded."

## 5. Post-exposure rulings: effect on verdicts (check 3)

| item | changed a threshold or meaning? | could it change a verdict? |
|---|---|---|
| C3 (P2 evaluation set; post-dry-run) | changed P2's evaluation set | No: HOLDS either way (V5:124) |
| **C4.2** (post-dry-run) | removed P2 as a verdict route | **Yes: ALTERED -> VALIDATED (§2)** |
| **C4.4** (post-dry-run) | fixed a point-estimate reading of the floor | **Yes: BEE "other" class (§1b)** |
| C9 (NPE labels) | no threshold change; clarified label meanings | Only INSTRUMENT_FAILED vs INCONCLUSIVE for NPE. Production agreement was 1.0, so no. |
| C10 (NPE MUTATION; reference repaired against its own behaviour, V5:472-477) | changed the MUTATION addr meaning | Same as C9. Production compares before write-back (addendum 3:9), so MUTATION loci are not in the production gate. |
| **C11** (BEE) | no threshold change | **Yes: INSTRUMENT_FAILED -> VALIDATED (§3)** |
| Addendum 3 (flip floor + class key) | re-imposed a floor R3 had dropped; chose the denominator | NPE: no (<30 fires anyway). BEE: passes either way. |
| Addendum 4 (dep-vacuous loci kept) | none (literal text) | No. It can only lower coverage. NPE self gives 159/474 = 0.335 even with the 22 loci removed. BEE has `dep_vacuous_loci` 271 and passes as is. |
| Addendum 6 (SF2) | marks only | No. The NPE self point estimate is 0.321. |

S:77-78 ("None changed a threshold") is literally true. It omits that C4.2, C4.4 and C11 each sat on a verdict boundary.

## 6. Section 3 claims (check 4)
- **S:32-35 "depend on a non-donor for their EXISTENCE and not for their CONTENT": not measured.**
  - In the "other" class the non-donor is the occupant, and the occupant is the performer.
  - Q8c randomises only groups outside {donor, performer} (V5:31). Content dependence on the occupant is therefore excluded by construction, not measured as absent.
  - The 0.00115 quoted at S:33 is the TRANSMISSION class. The class the claim is about has `Q8c_by_class.other` = 0.011489, ten times higher.
- **S:31-32 figures are right; the contrast is expected.** `Q8c_whether_by_class.other.P.mean_suppression` = 0.926312 and `self.P` = 0.016401. But randomising the performer suppresses the performed copy almost by definition.
- **S:33 "only 0.00115" hides the high Q8c values.**
  - `Q8c_by_class.none` = 0.241941 [0.162042, 0.329772] (B: 0.245 [0.170, 0.325]);
  - `NO_MATERIAL` = 0.214;
  - `Q8c_nonmove` = 0.30851 [0.269, 0.349] (non-gating by R2).
  - Under a per-class reading of "the Q8c" in R3, the "none" lower bound is >= 5%, which is WEIGHTED ALTERED. The frozen text does not say per-class, so VALIDATED stands, but a reader needs these numbers.
- **S:28-29 and S:83: "strong sense", "each load-bearing", "confirmed as necessary".**
  - Field necessity was never a preregistered test. R3 VALIDATED tests sufficiency: no loss, expressible, round-trip.
  - Q1 = 0.141238 and Q4 = 0.169485 (n = 31401) show that the performer and capability fields are *non-redundant* on this run. That is descriptive, not a validation result.
  - The "v0 represents this" wording at S:34 rests on the untested round-trip coverage (1a).
- **S:37-40 P2 (0.504) is correct, but omits:**
  - the reading without the identifiability filter, `P2_native_target_disagrees_WPmajority` = 0.448, n = 553;
  - the Review 7 mechanism: 183/191 dry-run cases were frame-shifted copies, not IBS-as-IBD (DRYRUN:81).
  - "Founding premise, now measured" (S:40) comes from one run.

## 7. Wording and generalisation (check 5)
- No "inherited" or "heredity" claim is made; L3-L5 are disclaimed (S:51, S:61-62). OK.
- **Generalisation beyond the scope stated at S:10-11:**
  - S:28 says "on real data" and S:40 says "on production data". Both are one run.
  - S:63-64 says "resemblance **and value match** are not descent". E-003 tested only the native label (P2); no value-match test is cited.
  - S:64 says "agrees across three independent tracers". That is BEE only; NPE had two. Archaeon wrote or repaired two of the three tracers (C10, C11), so "independent" is overstated.
- **S:58-60 uses NPE ("the NPE painters") as positive evidence for thr-c64dca3118a1.** This contradicts S:8-9 ("NPE is evidence neither for nor against") and the NPE leg's "MAY NOT: any Q value as a finding" (E003_NPE_LEG_RESULT.md:39-40).

## 8. Other omissions a disbeliever needs (check 6)
- **The same run was seen before the rules were finalised.** The v5 dry run on r022153 (Archaeon's pipeline, full Qs and verdict) came before C3 and C4. BEE_PRODUCTION_GO_v2.md:32 says "Archaeon has still inspected no Q or verdict value", but that is true of production outputs only.
- **Flip coverage is thin in the gated class, and it matters.** The self class is at 0.321 in NPE. In BEE the "other" class, which carries the performer != donor finding, sits at 0.543 with its CI straddling the floor.
- **Unreported NO_MATERIAL flip coverage:** 0.333 on 3 loci. The effect is negligible.
- **Untested outputs:**
  - the persisted ORIGIN attributes (S:79 notes this);
  - Q8c-whether is engine-measured and never passed any agreement check (V5:355, for NPE);
  - Q5 is not reported, although BEE's by-design list includes it as descriptive (V4:143).
