# s4v2.py v2.2 conformance review: CONFORMS

There are no BLOCKING or SHOULD-FIX findings. v2.2 repairs B1 and the v2.1 should-fix items (S1, S2, plus notes N1, N2, N6); I checked each one myself.

**How this was checked:** Python and shell pipelines were denied, so I recomputed everything by hand. I hashed files with sha256sum and tallied from search extracts of the committed files. I did **not** re-run the bootstrap confidence intervals (CIs). They only set the MARGINAL mark, never a gate. They are consistent with the per-simulation values I recomputed.

## Checklist
1. **identified:** it requires an ENTITY MOVE (a `flip_prefix` is present), a C7.2 prefix flip that is not FAILED, and `dep_changes == 0` (`s4v2.py:234-246`). **OK.**
2. **Flip-coverage denominator:** it is the rule-identified loci, i.e. R1 conditions 1 and 3 (`:237-242`, `:258-260`). The V5 sensitivity appears only under "reported" (`:270-273`, `:291`). It is not in FLOORS (`:65`), so it is never gated. **OK.**
3. **K_R1:** `:82-93` matches ruling 3. NO_MATERIAL is checked first (`:80`), a tie in either majority gives TIED, and a non-ENTITY majority performer gives "none". **OK.**
4. **Q8c None:** it is only counted (`:239-245`) and never used as a value. **OK.**
5. **Floors, CI and gate:**
   - Floors are 0.50 (at least), 0.01 and 0.05 (at most) (`:65`).
   - **The gate is the point estimate against the floor** (`:172-177`, `:284`). MARGINAL is a separate mark, set when the CI straddles the floor (`:180-186`, `:285`). This repairs B1 (V1).
   - The bootstrap is clustered on the simulation ID, with B = 2000 and seed 20260929.
   - Cluster counts, dropped resamples and SINGLE_CLUSTER are all reported (`:283-293`), per V6. **OK.**
6. **Completeness (V2, V3, V4):**
   - The universe includes the fz/fc flags, flipped with the same logic as `interventions.py:302-328` (`s4v2.py:118-142`).
   - The unit is the byte: a byte leaks if any of its K draws leaks, and is applicable if any draw is applicable (`:132-153`).
   - The birth subset is the committed `per_byte_sampled` rows of the distinct births (`:217`).
   - The new draw stream `S4V2CA` is declared in docstring V4 and in the summary's `completeness_draws` field.
   - **OK.**
7. **Units and inputs (V7):** duplicates are excluded, leaving 29 births in 9 simulations with 5 duplicates. Each of these exits with REFUSED:
   - an S4_RESULTS hash mismatch (`:191`);
   - an index hash mismatch (`:193`);
   - a births file missing from the index, or with the wrong hash (`:199`);
   - an S4 row missing from the index (`:206`);
   - a written-set mismatch (`:210`).

   I checked the inputs:
   - PRODUCTION_INDEX is `f478ce0d…`, which equals END_RECEIPT's recorded value.
   - All 11 births files match their `births_sha256`.
   - S4_RESULTS is `e232fd04…`.

   **OK.**
8. **Reproduce:** every number I recomputed matches exactly (below).
9. **Frozen files:** `interventions.py`, `run_production.py` and `z8shadow.py` match TRACER_FREEZE v4, and `s4_run.py` is still 68779d3e. None has been committed to since freeze v4. `s4v2.py` last changed in b0f215348, before the run; its results were committed in 10d9ad23f. **OK.**

## NOTES (none changes an outcome)
- **N1 (`:44-50`):** the history docstring is stale. R-e still describes the CI-only verdict rule, and R-f still claims "identical … seeds as s4_run". V1 and V4 supersede and retract these lines, but the text remains.
- **N2:** the gated leak share divides by applicable bytes (the F7 repair). R5's literal wording and the frozen `s4_run` divide by all unnamed bytes. v2.2's choice is the conservative one, and with 0 leaks the two agree.
- **N3:** K_R1 checks ties before "none", and treats a store_by tie as TIED; ruling 3 says nothing about ties. Neither case occurs in the data.
- **N4:** each class's bootstrap resamples only the simulations that have births in that class, not all 9. Zero-denominator resamples are dropped and counted.
- **N5:** a SINGLE_CLUSTER class still gets a PASS/FAIL gate. For example, K_R1 "other" completeness rests on s08B/256 alone. The spec sets no minimum cluster count.
- **N6 (`:109-117`):** the completeness step does not re-assert that the re-run reproduces the recorded victim half, as the frozen `analyse_birth` does. The risk is low because the births are hash-pinned and the engine is frozen.
- **N7:** `INDEX_SHA` is a hard-coded constant, not read from END_RECEIPT (I checked they are equal). An S4 row with no births record raises KeyError rather than REFUSED, but still stops the run.
- **N8:** INCIDENT_RUN3 records that run 3 rewrote births files in Nestor's old worktree, which were then restored. The V7 births-hash guard is what protects v2.2 from that incident.

## Recomputed K_R1 numbers
**Class membership** (majority performer vs majority store_by, per birth):
- **self** (19 births / 8 simulations): s01/256-257, s02/256-258, s04/259-261, s06A/257, s07/256-257, s08A/257-258, s08B/257-261, s10/257.
- **other** (8 / 5): s04/256, s04/258, s06A/256, s08A/256, s08B/256, s08B/262, s08B/263, s10/256.
- **TIED** (1): s04/257, performers split 16/16.
- **NO_MATERIAL** (1): s09/256, no ENTITY-labelled written loci.

| class | MOVE loci | rule-identified | CONFIRMED | FAILED | coverage | gate |
|---|---|---|---|---|---|---|
| self | 515 | 496 | 159 | 0 | 0.3206 | FAIL (CI 0.139–0.488, not MARGINAL) |
| other | 188 | 168 | 48 | 0 | 0.2857 | FAIL, marked MARGINAL (CI 0.127–0.653) |
| TIED | 32 | 32 | 8 | 0 | 0.2500 | FAIL, SINGLE_CLUSTER |
| NO_MATERIAL | 0 | – | – | – | – | NO_DATA |

- **FAILED share** is 0 in every class, so it PASSES.
- **V5 sensitivity:** all 22 loci with no usable dependence draws are in "self" and all are INAPPLICABLE, giving 159/474 = 0.3354.
- **Per-simulation coverage, self:** s01 31/64, s02 62/96, s04 24/76, s06 1/12, s07 29/64, s08A 1/40, s08B 11/113, s10 0/31.
- **Per-simulation coverage, other:** s04 5/43, s06 3/12, s08A 3/19, s08B 8/62, s10 29/32.

**Per-byte completeness:**

| class | births | bytes | applicable bytes | leaking |
|---|---|---|---|---|
| self | s01/256, s02/256, s07/256, s08B/259 | 3542 | 3372 | 0 |
| other | s08B/256 | 910 | 720 | 0 |
| TIED | s04/257 | 732 | 718 | 0 |

- Every class PASSES, with a leak share of 0.0.
- Draw totals are 14168/13476, 3640/2862 and 2928/2872 (all draws / applicable draws), with 0 leaks.
- **Independent check of the universe:** the frozen `s4_run`'s per-locus `unnamed_tested` counts sum per birth to 960, 1126, 732, 768, 910 and 688. These equal v2.2's per-birth byte counts exactly, so the fz/fc universe and the named-byte mapping match the frozen engine.

Under this reading, flip coverage fails in every gated K_R1 class, so the replay stays INCONCLUSIVE and no claim is broadened.

The full review, with file:line evidence, is in `/home/jcraig/fabric-work/worker.ubu001/attempts/att-6f3c91994ea2/out/REVIEW_s4v22_conformance.md`.