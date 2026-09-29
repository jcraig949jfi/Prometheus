+==========================================================================================================================+
| E-003 SYNTHESIS (REVIEWED): does byte-level ancestry in BEE and NPE validate, alter or break attribution v0?                |
| Author: Archaeon (M2 SPECTREX5)    Date: 2026-09-29    For: operator / central coordination + independent reviewers       |
| Status: REVIEWED. 2 fresh Fabric replicas (review_e003/): both FOLLOWS WITH CORRECTIONS; every correction applied here.    |
| Draft superseded: e6c8b5b2c. Self-contained: every number is inline; paths are for checking, not for reading.             |
+==========================================================================================================================+
Identifiers:
- Thread thr-a7fcb43e8092 (TH-015); also thr-c64dca3118a1 and thr-5085da70a143.
- Campaign C-001; Experiment E-003.
- Spec: ANCESTRY_PREREG v4 + v5 through C11.

-----
0. ANSWER
-----
**BEE (one run, r022153): VALIDATED under the prereg AS AMENDED. It is a CONDITIONAL verdict.**
- It depends on three amendments. Each sits on a verdict boundary, and each was made after exposure to this same run: the dry
  run on r022153 came before C3/C4, and the production agreement before C11.

  | amendment | what it did | if absent or read otherwise |
  |---|---|---|
  | C4.2 | removed P2 as a verdict route | P2 HOLDS (0.504), so the pre-C4 text returns ALTERED, as the dry run did |
  | C4.4 | fixed point-estimate gating | "other" flip coverage 0.543, CI [0.439, 0.646]; a lower-bound gate fails that class |
  | C11 | constant-only COMPUTED label; repaired the two ARCHAEON-side tracers after seeing the owner's reading | production agreement was 0.974 < 0.995, i.e. INSTRUMENT_FAILED |

- **C11 arbitration.** v4 s4.3 assigns arbitration to the independent reviewer. Review 1 ACCEPTS C11 explicitly as that
  arbitration; Review 2 accepts it on substance. So C11 now stands as independently arbitrated.
- **The robust, amendment-independent finding:** in the TRANSMISSION class, value dependence outside {donor, performer} is
  negligible. Q8c = 0.00115 [0.00098, 0.00134] in production; 0.0003 in the dry run. On this run a singular-donor
  value-descent record loses almost nothing.

**NPE: uninformative BY CONSTRUCTION.**
- v5 R3 makes the leg INCONCLUSIVE whenever the transmission class has < 30 births. The frozen unit (C7.4) has 29 distinct
  births in total, so the NPE leg could never have returned VALIDATED or ALTERED.
- The flip-floor route (coverage 0.321 / 0.286 / 0.25) rests on Archaeon's post-exposure addendum-3 reading.
- Under a strict reading, that same failure is SPEC_DEFECT (v4: s4 thresholds fail, not explained by a named channel), which
  outranks INCONCLUSIVE. Neither label is evidence about v0.

**Not claimed:**
- "v0 confirmed necessary". Field necessity was never a preregistered test; R3 tests sufficiency.
- Anything beyond L1-L2.
- Anything beyond one run.
- "BROKEN" was not searched for in NPE. The correct statement is "no BROKEN route fired".

-----
1. EVIDENCE CHAIN (owners executed; Archaeon owned the questions, fixtures, agreement and rulings)
-----
**BEE (Bellerophon; E003_BEE_RESULT.md @ f9a93eb6d; production/E003_RESULTS.json, lf sha 3a4c97b2):**
- **Agreement:**
  * fresh set 1: owner ~ Archaeon exact;
  * production s4 sample: FAIL -> C11 -> post-exposure re-run PASS;
  * fresh set 2: 3-way exact, 0 discrepancies. Weak as a test of the repair: the repaired shape occurs on very few loci there
    (Review 1 counts one ["F", []], zero ["C", []]).
- **R3 route, recomputed by both reviewers from the JSON:**
  * identifiable 0.968 (n = 32,644); TRANSMISSION 31,401;
  * Q8c upper 0.00134;
  * flip self 0.822, other 0.543 (MARGINAL), none 0.720;
  * FAILED 0; leak 0; round-trip PASS on 32,827.
- **Expressibility** (R3's second VALIDATED clause) is ASSERTED by the owner, not evidenced: the JSON does not record per-Q
  expressibility or round-trip Q coverage.

**NPE (Nestor):**
- production births: the frozen reference vs the owner agree 1.0 on every field, 29 distinct births. TWO tracers, not three.
- s4 v2.2 conforms (2 replicas); flip coverage FAILS in every class.
- The CVT-R reconciliation marks L5 NOT MEASURED; the children carry the painting signature.

-----
2. NUMBERS A DISBELIEVER NEEDS (all from the sealed JSON unless marked)
-----
- **Per-class Q8c:** self 0.0044, other 0.0115, none 0.242 [0.162, 0.330] (62 births), NO_MATERIAL 0.214. Q8c over all loci
  is 0.0058; Q8c-nonmove is 0.309 [0.269, 0.349].
  * R3 is pooled, so the verdict stands.
  * Read per class, the "none" class's lower bound exceeds 5%, which would be WEIGHTED ALTERED.
- **Dependence-set precision:** 0.13-0.23 by class. Under the original R5 gate that is OVER-TAINT, i.e. INSTRUMENT_FAILED;
  C1 (pre-draw) made it non-gating.
- **dep-vacuous loci:** 271. The class split is not reported. A worst-case allocation to "other" would fail its floor;
  Review 1 judges that implausible.
- **Dry run vs production on the IDENTICAL 32,827 births** (UNEXPLAINED drift):

  | quantity | dry run | production |
  |---|---|---|
  | Q8c transmission | 0.0003 [0.0002, 0.0004] | 0.00115 (non-overlapping) |
  | Q8c all loci | 0.027 | 0.0058 |
  | transmission class | 30,945 | 31,401 |

- **Q4:**
  * production: isolated-capable 0.810; host-assisted 0.817; incapable-alone-but-host-capable 0.007 of births;
  * the dry run found the "other" class 0.81 host-assisted capable with 0/120 isolated. That implies about 0.11 of births,
    about 15x the production figure;
  * this is UNEXPLAINED. Until it is resolved, no "relational capability" claim is made.
- **P2** (engine-native): 0.504 [0.456, 0.552] (n = 395), or 0.448 without the identifiability filter.
  * Review 7's mechanism: 183/191 of the dry-run cases were frame-shifted copies, i.e. positional shift-blindness, not IBS
    read as IBD.

-----
3. WHAT THE BEE DATA SHOW ABOUT v0 FIELDS (DESCRIPTIVE ONLY, not validation results)
-----
On r022153 these v0 fields are NON-REDUNDANT:
- performer != copy-descent donor in 0.141 of births (Q1);
- 0.169 of TRANSMISSION-class children carry writer material without isolated capability (Q4).

Two withdrawn claims:
- "existence without content dependence": content dependence on the PERFORMER is excluded from Q8c by construction, so it
  was not measured;
- "capability-with-conditions is needed": the Q4 discrepancy above.

The reproduction predicates stay PLURAL, per the arc directive. Nothing here justifies collapsing them. Nothing here proves
each is necessary.

-----
4. THREADS
-----
- **thr-c64dca3118a1 (replicator identity):** E-003 measures L1-L2 only; lineage questions are L3+. No update from E-003
  beyond the non-redundancy of material and capability on one BEE run. The NPE painters are NOT cited as evidence.
- **thr-5085da70a143 (cargo vs heredity):** OPEN; untested beyond one engine; E-003 does not reach L3-L5.
- **Founding premise (native labels are not descent):** supported on ONE BEE run by P2, with the shift-blindness mechanism.
  "Value match" was not tested as a separate endpoint.

-----
5. PROCESS RECORD (kept visible)
-----
- **Same-run exposure:** C3, C4.2, C4.4 and the NO_MATERIAL class-gate change were all made after r022153's data had been
  seen (the dry run). "Archaeon inspected no Q" is true of PRODUCTION outputs only.
- **Post-agreement-test repairs:**
  * C9 (NPE labels): the FIRST fresh set after it FAILED on set M;
  * C10 (NPE MUTATION; the reference repaired after seeing the owner); fresh set 2 then passed;
  * C11 (BEE; both Archaeon-side tracers repaired after seeing the owner); fresh set 2 passed (thin).
- **Post-exposure rulings:**
  * addendum 3 revived the flip floor that v5 R1/R3 had dropped;
  * addendum 4 (dep-vacuous);
  * addendum 6 (marks only).
- **Withdrawn:** the C8 A1/A2 canonical clearance.
- **Incidents:** NPE run 1 invalidated (bookkeeping); an unauthorized NPE run 3 destroyed 10/11 of the 1% sample files. The
  1% check is still open; tsk-c4317a3656d0 is unclaimable (no skullport worker). It cannot change either leg.
- **Untested by any agreement check:** the persisted ORIGIN attributes (both engines); Q8c-whether (engine-measured).
- **Not reported:** Q5, which has no null.

-----
6. WHAT THIS DOES AND DOES NOT ESTABLISH
-----
- **ESTABLISHES** (one BEE run):
  * byte-level causal ancestry can be traced reproducibly and cross-checked;
  * singular-donor value descent loses almost nothing in the transmission class;
  * the native resemblance label is not a descent label;
  * performer and capability are non-redundant with donor.
- **DOES NOT ESTABLISH:**
  * that v0 is validated independently of post-exposure amendments;
  * anything about NPE;
  * necessity of v0's fields;
  * heredity (L3-L5);
  * generality beyond one run.

-----
7. DECISION / RECOMMENDATION (operator's call)
-----
- E-003 is complete for its question, with a conditional answer.
- **To make the BEE verdict amendment-independent:** a NEW preregistered BEE run drawn fresh, under the v5-through-C11 text
  frozen BEFORE any exposure.
- **To make NPE informative:** a corpus of >= 30 transmission births, plus an identification test that does not require
  store-before-execute.
- **Neither is proposed here.** MWO-0002 authorizes no new campaign. They are recorded for a future MWO.
- **Open, non-blocking:**
  * the dry-vs-production drift (Q8c; Q4 host-assisted) should be explained before any later citation of those quantities;
  * the NPE 1% sample check.

-----
8. QUESTIONS FOR THE REVIEWER (written to resist agreement)
-----
1. Given C4.2/C4.4/C11, is "VALIDATED" the right headline at all, or should the headline be the robust Q8c finding alone?
2. Should the "none" class per-class Q8c (0.242, lower bound > 5%) be read as a WEIGHTED ALTERED signal the pooled R3 hides?
3. Is the dry-vs-production drift an instrument problem that should suspend the BEE Q4 and Q8c numbers entirely?
+==========================================================================================================================+
| END. "Not worth continuing" and "the conclusion does not follow" remain first-class answers.                                |
+==========================================================================================================================+

-----
ADDENDUM 2026-09-29 (after the owner's reply, comms #983; the BEE leg merged to main at 0629fd4f0)
-----
**A. Q4 discrepancy: EXPLAINED as an owner instrument defect (DEF-BEL-004).**
- The frozen host arm kept the isolated test's "own stores" condition, so a host-performed copy fails it by construction.
- **POST-HOC diagnostic** (labelled; same draws; success = the child's exact tape in the window):
  * "other" class: isolated 0.0002, frozen host arm 0.0075, relational 0.733, with the occupant performing 97.4% of the
    successful copies;
  * all births: 0.124 relationally capable but not isolated-capable.
- This matches the dry run's ~0.81 host-capable / 0/120 isolated.
- **Consequence:**
  * the frozen Q4 host-assisted figure (0.007) is WITHDRAWN as a relational measure;
  * the relational capability of the "other" (parasite) class is supported, but only by a POST-HOC measurement;
  * it may be cited only with that label.

**B. The "drift" is CROSS-PIPELINE, not within one pipeline.**
- The owner's dry run and production agree exactly (TRANSMISSION 31,401; Q8c 0.00115).
- The contrast in s2 (0.0003; 30,945) is Archaeon's pre-C4 dry pipeline, with its own tracer (9cd6bb4ed, pre-C2/C11) and
  rules, against the owner's frozen pipeline.
- The cause on Archaeon's side is NOT traced. Record it as a pipeline difference; the Q8c conclusion (< 5% in both) is
  unaffected.

**C. Further conditionality, disclosed by the owner** (flagged for the final reviewer):
- "NO_MATERIAL not gated" is a FOURTH rule adopted after r022153 was seen (NO_MATERIAL flip coverage 0.333 on 3 loci). Either
  it or C4.4 alone would give INCONCLUSIVE.
- The s0 table therefore gains a row: NO_MATERIAL class gating, post-dry, which would make the verdict INCONCLUSIVE.

**D. Expressibility is weaker than stated.**
- The v0 round-trip recomputed only 4 quantities. The remaining by-design Qs' expressibility is asserted.
- Empty performers were encoded as org:W in the round-trip records.
- Both weaken R3's VALIDATED clause 2. Neither is resolved here.

**Revised headline, unchanged in kind:** BEE VALIDATED is CONDITIONAL. It is now conditional on four post-exposure rules
(C4.2, C4.4, NO_MATERIAL-not-gated, C11) and a partly-asserted expressibility clause. The robust finding remains Q8c
(< 5%, both pipelines).

**E. Cross-pipeline Q8c difference: partly localised (Archaeon, 2026-09-29; bounded check, nothing re-run).**
- Per-birth join of Archaeon's dry51_r022153.births.json.gz (q8c_mean) with the owner's production/arms.jsonl.gz
  (q8c_changes / q8c_draws per locus).
- **Same births:** all 30,945 of the dry pipeline's TRANSMISSION births are present in both. The class definition is NOT the
  cause of the mean difference.
- **Per-birth means:** 0.00030 (Archaeon dry) vs 0.00103 (owner), unweighted.
- **Disagreements run in both directions:**
  * 629 self births are 0 in the dry pipeline but > 0 in the owner's;
  * 273 self + 111 other births are lower in the owner's;
  * 231 + 83 other births are higher in the owner's.
- **Reading:** stochastic K = 8 draw noise, plus a SYSTEMATIC component (the 629 zero-vs-positive self births).
- **Hypothesis (UNTESTED):** the owner's arm randomises a source group or byte range that the dry pipeline did not (e.g. the
  input region beyond the supplied input).
- **Status:** OPEN, non-blocking. Q8c < 5% in both pipelines. Resolving it needs a comparison of the arm group definitions.

**F. Cross-pipeline Q8c difference: CAUSES IDENTIFIED (Archaeon, 2026-09-29; MWO-0004 R1 bounded item; code comparison only,
nothing re-run).**
- The source groups are IDENTICAL in both pipelines: W, P (when occupied) and the supplied INPUT bytes (owner
  s4_tests.group_addrs; Archaeon bee_dryrun_v5.analyse_birth).
- **The ESTIMAND differs.** Archaeon's pre-C4 dry pipeline did NOT compute R2 as written:
  * per locus it took the MAX over outside groups of changes / K, where the owner pools changes / draws over (group, draw);
  * its denominator K counted every draw, including draws in which the write is suppressed. R2, and the owner, count only
    draws in which the write occurs.
- **Draw streams are independent** (different RNG seeding). With K = 8, rare changes appear in one pipeline and not the other.
  That fits the two-directional per-birth discordance in item E.
- **Consequence:**
  * the dry-run Q8c value (0.0003) is NOT an R2 value and must not be cited as one;
  * the owner's 0.00115 is the R2 estimand;
  * the effect of each difference on the mean is not apportioned (that would need a re-run).
- **Item CLOSED** as explained qualitatively. The VALIDATED computation is unaffected.

**G. The NPE 1% production agreement sample: VERIFIED and PASS** (MWO-0004 G2; native on SKULLPORT under R3; Nestor #990, #1023).
- **Stage 1** (verifier v2, addendum-5 content identity): run-1 copy candidate 1 VERIFIED. 11/11 files, 28,055 interactions.
- **Stage 2** (frozen reference 15737444 vs owner; raw per class; npe_sample_task @ 8631128c3; one rerun after the declared
  schema): AGREEMENT PASS.

  | class | addr / ctrl / exec / written | label |
  |---|---|---|
  | unwritten (1,693,918) | 1.0 | 0.99842 |
  | written_other (43,251) | 1.0 | 0.99864 |
  | written_self (56,293) | 1.0 | 0.99867 |
  | written_perf_none (2,058) | 1.0 | 1.0 |

  * AGREEMENT.txt sha256 0aa5d2d30431748b7e39ccf95c224341b571656a466e7aa031dd9d9a1b521645.
  * Outputs: Nestor g2_sample_check/rerun_8631128c3/ @ 168c8b81d on main.
- **The residue (2,818 label-only loci) is UNDIAGNOSED but mutation-shaped:**
  * about 1 locus per interaction, in 2,704 of 28,055 interactions (9.6%);
  * 95% on unwritten loci; both halves equally.
  * That fits the two sides placing post-write-back MUTATION labels differently: RNG-state alignment at write-back, or the
    MUTATION encoding. It exceeds the ~6% expected for one set of mutations.
  * The cell rate (LOW, 0.002) matches the reference default, so the rate is excluded.
  * It cannot be classified further: npe_sample_task's discrepancy records omit the label values, a design gap in
    Archaeon's module.
  * Every pre-write-back field (addr, ctrl, exec, written) agrees 100%.
- **Consequence for E-003:** none. The NPE leg stays uninformative by construction (R3 < 30). This check confirms the NPE
  tracer's production labels at production scale, with the stated mutation-label residue.
