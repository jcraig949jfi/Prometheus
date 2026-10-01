## Verdict: CONFORMS

s4v2.py v2.2 repairs the blocking finding B1 and the should-fix items from the v2.1 review. I found nothing blocking. There are two SHOULD-FIX items, both documentation or annotation only; neither changes any gate outcome.

**How this was checked:** Python was denied, so every number was recomputed by hand from `rogit grep` dumps of the committed files. I did not recompute any sha256. I did not re-run the bootstrap; I only checked it is plausible. File identity comes from git history:
- s4v2.py is the same blob from b0f215348, whose commit message posts 17670fed, through HEAD.
- PRODUCTION_INDEX.json and S4_RESULTS.jsonl were each written only once, in 81895e729, the same commit as END_RECEIPT.json.

## Findings

**SHOULD-FIX**
- **SF1 — stale docstring rules.** The old R-e text (s4v2.py:44-46) still describes the CI-only verdict: PASS or FAIL from the CI, "else MARGINAL". The old R-f text (:47) still claims "identical selection hash and seeds as s4_run".
  - The code implements the new rules: V1 at :172-186 and :284-286, V4 at :115.
  - This matters because S4V2_SUMMARY.json sends readers to the docstring: `"repairs": "R-a..R-g, V1..V7 (docstring)"`.
- **SF2 — the bootstrap resamples only the simulations that contain the class, not all 9** (:157-162, called at :282).
  - K_R1 self resamples 8 simulations; other resamples 5.
  - R-e (:44) and C7.4 say "over the 9 distinct simulations".
  - The gates are unaffected, because they use the point estimate. The MARGINAL mark could change: K_R1 self's upper bound is 0.4884, just under the 0.50 floor.
  - Fix: resample all 9, or declare the conditional scheme.

**NOTE**
- **N1:** the new completeness measurement never checks that the replayed victim half equals the recorded one (:117). The frozen `analyse_birth` does check this.
- **N2:** INDEX_SHA is a hard-coded constant (:67) equal to END_RECEIPT's value; END_RECEIPT.json itself is not read.
- **N3:** a births record missing for a row raises KeyError (:208). That still fails closed, but without a REFUSED message. There is no assertion that the inputs give 29 births in 9 simulations.
- **N4:** tie-before-none (:89-91) and NO_MATERIAL counting kind "E" only (:80) are kept as declared. Neither case occurs in this data.
- **N5:** the leak denominator is applicable bytes, not all unnamed bytes as in the literal R5. This is the accepted F7 repair, and it can only raise the leak share.
- **N6:** the fz/fc flips are deterministic, so their K = 4 draws are identical. This matches `interventions.per_byte_arms`.
- **N7:** I could not re-run the engine, so I checked the completeness file only for internal consistency and its aggregation into the summary.

## Checklist
1. **identified:** OK. ENTITY MOVE, gating prefix flip not FAILED, and dependence changes == 0 (:237, :246).
2. **Flip-coverage denominator:** OK. It is the loci meeting R1 conditions 1 and 3. The V5 sensitivity (159/474 = 0.3354 for self) appears only under `reported` and is never gated.
3. **K_R1:** OK. It matches ruling 3; `store_side` is `"ab"[st.side]`, i.e. store_by (run_trace.py:88). NO_MATERIAL and TIED are handled.
4. **Q8c None:** OK, never counted as 0. There are 22 such loci, all INAPPLICABLE and all in self (S4_RESULTS lines 9, 10 and 25).
5. **Floors, CI and gate:** OK (V1, V6).
   - Floors are 0.50 / 0.01 / 0.05.
   - The gate is the point estimate against the floor. MARGINAL is a separate mark meaning the CI straddles the floor.
   - Cluster counts, SINGLE_CLUSTER and dropped resamples are all reported.
6. **Completeness (V2-V4):** OK.
   - fz/fc are in the universe, flipped exactly as in interventions.py (:121).
   - The unit is per byte: a byte leaks if any draw leaks, and is applicable if any draw is (:149-151).
   - The subset is s4_run's `per_byte_sampled` (S4_RESULTS lines 1, 3, 7, 16, 21, 24).
   - The new draw stream is declared honestly.
7. **Units and inputs (V7):** OK. 29 distinct births, 5 duplicates, 9 simulations by sim_id. A missing index entry, a hash mismatch or a written-set mismatch each give REFUSED (:193, :199, :210).
8. **Reproduce:** OK. Everything below matches S4V2_SUMMARY.json.
9. **Frozen files:** unmodified. Since freeze v4 (8153aaa8e), only s4v2.py and production_launch.py (binding constants) changed under tracer/. interventions.py, s4_run.py, run_production.py and z8shadow.py are unchanged.

## Recomputed K_R1

**Class membership:**
- **other (8 births, 5 sims):** s04/256, s04/258, s06A/256, s08A/256, s08B/256, s08B/262, s08B/263, s10/256.
- **TIED:** s04/257 (performers split 16/16).
- **NO_MATERIAL:** s09/256.
- **self:** the other 19 births, over 8 sims.

| class | MOVE loci | rule-identified | CONFIRMED | FAILED | coverage | gate | marks |
|---|---|---|---|---|---|---|---|
| self | 515 | 496 | 159 | 0 | 0.3206 | FAIL | – |
| other | 188 | 168 | 48 | 0 | 0.2857 | FAIL | MARGINAL (CI 0.127–0.653) |
| TIED | 32 | 32 | 8 | 0 | 0.2500 | FAIL | SINGLE_CLUSTER |
| NO_MATERIAL | 0 | 0 | – | – | – | not gated | – |

- Totals are 735 MOVE loci and 757 written loci, matching addendum 3.
- FAILED share is 0 in every class, so that gate passes everywhere.

**Per-byte completeness** (in every file row, draws = 4 × bytes):

| class | leaking / applicable bytes (all bytes) | leak share | gate |
|---|---|---|---|
| self | 0 / 3372 (3542) | 0 | PASS |
| other | 0 / 720 (910) | 0 | PASS, SINGLE_CLUSTER |
| TIED | 0 / 718 (732) | 0 | PASS |

The fz/fc addition adds +128, +124 and +128 bytes over v2.1. That is 4 items × 32, 31 and 32 written loci, which fits births with persisted registers on both sides.

Files are in /home/jcraig/fabric-work/worker.ubu001/attempts/att-de3a7cd6bba7/out/:
- REVIEW_s4v22_conformance.md — the full review.
- extract.py — an unused helper; it never ran because Python was denied.