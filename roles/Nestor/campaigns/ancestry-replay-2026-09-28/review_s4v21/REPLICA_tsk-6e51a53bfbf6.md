# Conformance review of s4v2.py v2.1 (sha256 3d9eb155…, base 88b9d0a13)

## Verdict: DOES NOT CONFORM

There is one blocking defect: the floor verdict is decided from the confidence interval alone, not from the point estimate that C4.4 requires. Everything else checks out. The class key, denominators, units, duplicate handling and point estimates are all right, and the K_R1 numbers reproduce exactly. The fix is code-only and needs no re-run.

I couldn't run Python here: every script call was denied except `python3 --version`. So I recomputed everything by hand from greps of the committed files, and I did not re-run the bootstrap.

## Findings

### BLOCKING

**B1. The floor verdict ignores the point estimate** (s4v2.py:133-140 and :216; the docstring rule R-e at :22-24).
- **Spec:** v5 C4.4 and addendum 3 ruling 2 say a per-class gate is judged on the point estimate against the floor, with the 95% CI reported. A class whose CI straddles the floor is also marked MARGINAL.
- **Code:** `verdict()` never looks at the point estimate. It returns PASS if the whole CI is on the passing side, FAIL if the whole CI is on the failing side, and MARGINAL otherwise. MARGINAL replaces the gate decision instead of flagging it.
- **Effect on K_R1 "other":** flip coverage is 48/168 = 0.286, below the 0.50 floor, so the gate fails and the class is INCONCLUSIVE (v4 s2.1). Its CI [0.127, 0.653] straddles the floor, so it should also carry the MARGINAL mark. The summary reports only "MARGINAL", and so does the commit headline.
- **Correct K_R1 flip-coverage gates:**

  | class | gate | MARGINAL mark |
  |---|---|---|
  | self | FAIL (CI [0.139, 0.488]) | no |
  | other | FAIL | yes |
  | TIED | FAIL | no |

- The FAILED share and completeness gates pass under either rule.
- **Fix:** report the gate (point vs floor) and the MARGINAL mark (CI straddles) as separate fields.

### SHOULD-FIX

- **S1. The completeness test skips the flags** (s4v2.py:91-94 vs interventions.py:303-305).
  - The frozen s4_run test also randomises the two persisted flags, fz and fc, which the tracer labels `("P", ent, "fz"|"fc")` (z8shadow.py:586).
  - s4v2 randomises only tape bytes and registers 0..7, so a leak through a flag is never tested.
- **S2. The docstring's claim of "identical … seeds as s4_run" is false** (s4v2.py:25-26 vs :88).
  - The birth subset is the same 6 births: S4_RESULTS lines 1, 3, 7, 16, 21 and 24.
  - The random draws are not: s4v2 uses a new random stream (`S4V2CA|…`). This is a new, deterministic measurement and should be declared as one.
- **S3. The completeness unit is draws, not bytes** (s4v2.py:112-114 and :207-209).
  - R5 defines the leak share over bytes (each locus × unnamed byte), as s4_run counts it.
  - s4v2 divides leaking draws by applicable draws.
  - With 0 leaks this changes nothing here, but a real leak would be diluted by up to K = 4.
- **S4. Rule-identified loci include 22 loci with no usable dependence draws** (s4v2.py:183).
  - For these, every draw was suppressed, so `dep_changes` is 0 and `q8c` is None. The dependence condition is treated as met with no evidence.
  - All 22 are prefix-INAPPLICABLE and in K_R1 self (S4_RESULTS lines 9, 10 and 25).
  - Q8c None itself is never counted as 0; it goes to `q8c_no_usable_draws`.
  - Excluding the 22 gives self coverage 159/474 = 0.335, so the outcome doesn't change. It should be reported, or ruled on by Archaeon.
- **S5. Single-cluster CIs are graded PASS or FAIL without a flag.**
  - K_R1 TIED is one simulation.
  - K_R1 other's completeness rests on one sampled birth.
  - The number of clusters behind each statistic should be reported.

### NOTE

- **N1. Tie ordering:** a "none" performer majority combined with a store_by tie returns TIED rather than none (s4v2.py:62-65). No such case occurs in the data.
- **N2. Input hashes:** the births files, which supply store_by, and PRODUCTION_INDEX are not hash-checked; only S4_RESULTS is. The code also doesn't check that the written sets in S4_RESULTS and the births files match.
- **N3. Conditional bootstrap:** resamples with a zero denominator are dropped (s4v2.py:125-126).
- **N4. F7 is quantified, not removed:** the leak test still requires the full path to be unchanged, as R5 literally says. Applicability is now reported (0.75–0.98).
- **N5. `__ep` exclusion dropped:** s4_run skips `*__ep*` births files and s4v2 doesn't. There are none, so no effect.

## Checklist

1. **Identified:** conforms (s4v2.py:180-189). It requires written ENTITY MOVE, the gating prefix flip not FAILED, and `dep_changes == 0`. See S4.
2. **Flip-coverage denominator:** conforms. It is the loci meeting R1 conditions 1 and 3, and the numerator counts only those loci.
3. **Class key K_R1:** matches ruling 3.
   - NO_MATERIAL (10% or fewer written loci ENTITY-labelled) is tested first.
   - A tie in either majority gives TIED.
   - store_side and performer_ent use the same 'a'/'b' coding.
4. **Q8c None:** never counted as 0. See S4.
5. **Floors and CI:**
   - The thresholds are correct: 0.50, 0.01 and 0.05.
   - The bootstrap is over the 9 simulations with B = 2000.
   - The verdict rule is wrong (B1).
6. **Completeness applicability:**
   - It uses the same 20% birth subset.
   - The applicable and leak tallies match their definitions and add up from S4V2_COMPLETENESS.jsonl.
   - See S1-S3.
7. **Units:**
   - Duplicates are excluded (29 distinct births, 5 duplicates, 9 simulations).
   - A missing index entry stops the run with REFUSED (s4v2.py:155-156).
8. **Reproduce:**
   - The K_R1 classes, totals and point estimates reproduce exactly.
   - v2.1 changed only the K_R1 block of the summary.
   - The completeness file is byte-identical to the v2 commit's.
   - I did not re-run the bootstrap.
9. **Frozen files:** unchanged.
   - interventions.py (33c1e3a0), run_production.py (c00e827e) and z8shadow.py (d1d7cd74) match TRACER_FREEZE v4.
   - s4_run.py is the reviewed 68779d3e.
   - Nothing frozen changed between 81895e729 and 88b9d0a13.

## Recomputed K_R1 numbers

| class | births | sims | MOVE loci | rule-identified | covered (CONFIRMED + FAILED) | coverage |
|---|---|---|---|---|---|---|
| self | 19 | 8 | 515 | 496 | 159 + 0 | 0.3206 |
| other | 8 | 5 | 188 | 168 | 48 + 0 | 0.2857 |
| TIED | 1 (performer split 16 a / 16 b) | 1 | 32 | 32 | 8 + 0 | 0.25 |
| NO_MATERIAL | 1 (all 22 written loci COMPUTED) | 1 | 0 | 0 | – | – |

- **FAILED share:** 0 in every class.
- **"other" births:** S4_RESULTS lines 6, 8, 12, 18, 21, 27, 28 and 33.
- **Per simulation (covered / rule-identified):**
  - **self:**
    - s1 31/64, s2 62/96, s4 24/76, s6A 1/12;
    - s7 29/64, s8A 1/40, s8B 11/113, s10 0/31.
  - **other:** s4 5/43, s6A 3/12, s8A 3/19, s8B 8/62, s10 29/32.
- **Completeness:**

  | class | leaks / applicable draws | applicable / all draws |
  |---|---|---|
  | self | 0/12964 | 12964/13656 |
  | other | 0/2366 | 2366/3144 |
  | TIED | 0/2360 | 2360/2416 |

All of these match S4V2_SUMMARY.json.

Files are in /home/jcraig/fabric-work/worker.ubu001/attempts/att-02d192786679/out:
- REVIEW_S4V2_1.md
- inspect.py (never ran because Python was blocked; ignore it)