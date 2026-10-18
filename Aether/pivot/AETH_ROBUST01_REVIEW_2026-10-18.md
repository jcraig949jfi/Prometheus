+==============================================================================+
| REVIEW PACKET -- AETH-V2B-ROBUST01: does folding every contender (XOR of all |
| valid writes) instead of one hash-chosen winner make composition robust,     |
| discoverable and reusable?                                                   |
| Author: Aether (role seat), host SPECTREX5 / M2, RTX 5060 Ti 16 GB           |
| Date: 2026-10-18                                                             |
| For: HITL operator + external reviewers                                      |
| Status: COMPLETE (all 4 stages). Freeze c989c09a1, closed 22 h after freeze  |
|         (hard stop was 48 h).                                                |
| Self-contained: every load-bearing number is inline.                         |
+==============================================================================+

-----
0. SUMMARY FOR THE HURRIED REVIEWER
-----
REACH01 ended at one binding constraint: under the frozen contest law
(aeth01.op_xor, where a hash picks ONE winner among simultaneous writers),
compositions are position-fragile. ROBUST01 changes exactly that rule.
Template fields now store the XOR-fold of EVERY valid write
(aeth01.op_xor_fold); the energy field is unchanged. ROBUST01 then reran
REACH01's own frozen search, certifier and reducers.

Stage dispositions (all frozen code, all gates passed):
 - S0 reproduction gate: PASSED. Run through the ROBUST01 harness, the
   contest law gives back REACH01 exactly (certificates, a byte-identical
   transplant table, 7/7 discoveries).
 - S0 planted combiner under fold: PLANTED_COMPOSE_AUTONOMOUS.
   - Computes a ^ b at 256/256 positions (contest: 66/256), under both
     alternative seeds.
   - Certificate 18/19/1, as derived in advance.
 - S1 discovery (G1, 40 seeds): ROBUST_COMPOSITION_DISCOVERABLE /
   HELDOUT_NOT_GENERAL.
   - Autonomous composition in 4/40 arm-C seeds, against 0/40 under contest.
   - Held-out generality in 1/40.
 - S2a assisted reuse (planted component): CUMULATIVE_ACQUISITION_ADVANTAGE
   + ROBUST_REUSE.
   - P 8/8, necessity 1.0, median position fraction 1.0 (contest 0.016).
 - S2b genuine reuse (S1's own composition): REUSE_NOT_SUPPORTED. P 1/8.

What survived:
 - Contest arbitration was the source of position fragility for designed,
   discovered AND search-built structure.
 - It was not what limited discovery rate or reusability.

What died:
 - "The fold law makes raw material compose." Arm A, which evaluates
   exactly the same 20,480 patches per seed under both laws, combines in
   0/40 seeds under either.
 - "Discovered compositions are reusable building blocks." S2b got P 1/8.

Biggest caveat (Sec 7.1): for a mechanism with no energy-field contest,
position independence follows from the law by theorem. Most of the
robustness is guaranteed by construction. The empirical content lies
elsewhere:
 - 61 of the 90 S1 candidates do have energy contests, and all stayed
   robust;
 - the discovery and acquisition rates;
 - necessity;
 - held-out generality.

Predictions: 10 registered clauses (P-S1 counted by its 5 parts); 7 held,
3 failed (Sec 5.5).

-----
1. PROVENANCE AND INSTRUMENT (verified, not trusted)
-----
 - Branch aether/robust01-2026-10-17. Freeze c989c09a1
   (2026-10-17T03:50:42Z): PREREGISTRATION.md, RULES.json, FREEZE.sha256.
 - Law: fold_physics.py, sha256 50aeee337e8c... It is a wrapper; the frozen
   kernel is untouched. install() remaps op "XOR" inside the process, so
   REACH01's search, certifier and reducers run byte-identical. Any other
   op raises.
 - Fixtures: test_fold_physics.py, 15/15 passing, including CPU == GPU bit
   identity under fold.
 - Every unit output carries a robust01 stamp: semantics_id, fold sha, and
   fold_ticks_executed > 0 for the process that wrote it. Checked on all
   80 S1, 32 S2a and 32 S2b units.
 - Runner: r01_run.py. It refuses express01.py, which, run as a script,
   would bypass the patch; a smoke test caught this before the freeze.
 - Reproduction (the instrument check that matters): the contest law
   through the ROBUST01 harness reproduces REACH01 S0 exactly. The S1
   reducer's own counts on REACH01 data are 7/3/0/1 (arm C) and 0/0/0/0
   (arm A), equal to the published numbers.

-----
2. PREREGISTRATION CHAIN
-----
 - One freeze, c989c09a1, and no amendments. Predictions were written
   before any fold-law run of the planted combiner or of any discovered
   mechanism.
 - Post-hoc additions are labelled as such:
   - r01_s1_describe.py (separability and a ^ b dependence of the
     discovered functions; Fisher exact tests);
   - the S1 determinism recheck.
 - ROBUST_REUSE was applied by its registered rule (RULES.json stage2:
   P success >= 6/8 AND median P position fraction >= 0.9) to r4_reduce's
   own summary fields. No frozen script computes it; the rule is two
   comparisons.

-----
3. DESIGN AS EXECUTED
-----
 - S0 (2 units):
   - contest law, then fold law;
   - R3 planted combiner: certificate, tables, invariance check;
   - R4 task-1 transplant over 6 offsets x 256 positions;
   - REACH01's 7 G1 discoveries, certified again.
 - S1 (80 + 80 units):
   - G1 geometry, arms C (certificate-guided) and A (ordinary), seeds
     0-39, 20 x 1024 evaluations;
   - up to 10 COMBINE candidates certified per unit;
   - reduced by r01_reduce_s1.py, gated in order: INCOMPLETE ->
     REDUCER_DEFECT -> INSTRUMENT_DEFECT -> k.
 - S2a (32 + 1 units):
   - REACH01 R4 exactly (planted component, arms N S U P, seeds 0-7);
   - frozen r4_reduce with S0's fold transplant table.
 - S2b (32 + 1 units):
   - component chosen by the frozen r01_stage2b.py rule from S1:
     G1_C_s13 88052bc1, the only COMPOSE candidate with no energy contest;
   - R4c's task (input C at (12, 1)), in2 (0x55, 0xAA);
   - frozen r4_reduce.
 - Compute: spectrex5:gpu0 leased, --jobs 2. The GPU was shared with the
   operator's skullport-gfx (Sec 7.6).

-----
4. CENSUS
-----
 - 232 GPU units ran in total. Every rc was 0 and none is missing.
   - S0: 2.
   - S1: 80 search and 80 certify.
   - S2a: 32 + 1. S2b: 32 + 1.
   - Recheck: 4.
   - 25 S1 search units also ran a second time (incident, Sec 7.5).
 - Wall clock:
   - S0 49 min;
   - S1 search 13:57Z-20:10Z with yields; certify 77 min;
   - S2a 72 + 36 min; S2b 80 + 6 min.

-----
5. RESULTS
-----
5.1 S0 (contest -> fold), planted R3 combiner:
     position-0 table          a ^ b   -> a ^ b (7 distinct outputs)
     COMBINE positions          66/256  -> 256/256
     alternative seeds          F, F    -> T, T
     a_only / b_only / shared   13/10/0 -> 18/19/1   (predicted 18/19/1)
     held-out alphabet          COMBINE -> COMBINE
     transplant (R4 task 1)     fails   -> fails: 1.0 at (0,0), 0.0 at 5 offsets
   REACH01's contest-era compositions (s2, s22, s27) do not survive the
   change: 0.0 positions under fold. Only s7, the value detector, is
   unchanged (autonomous).

5.2 S1, G1, 40 seeds per cell (Wilson 95%):
                    fold C        fold A   contest C     contest A
     COMBINE        9 (.12-.38)   0        7 (.09-.32)   0
     COMPOSE        4 (.04-.23)   0        3 (.03-.20)   0
     AUTO_COMPOSE   4 (.04-.23)   0        0 (0-.09)     0
     AUTO_ANY       9 (.12-.38)   0        1 (.00-.13)   0
     GEN_COMPOSE    1 (.00-.13)   0        -             -
   - Gates: 80/80 units and certificates; reproduction exact; 0 instrument
     violations; all stamped.
   - All 90 certified candidates are AUTONOMOUS, at position fraction 1.0
     with seed-identical tables, including the 61 with energy contests
     (29 have none).
   - COMPOSE seeds: 6, 13, 16, 37. GEN_COMPOSE: seed 13 only.
   - Fisher exact, one-sided, fold C vs contest C (post hoc):
     AUTO_COMPOSE p = 0.058; AUTO_ANY p = 0.0072; COMBINE p = 0.39.

5.3 S2a, R4 with the planted component (8 seeds; budget 20,480):
     arm   success   median cost   necessity   position (median)
     N     0/8       >budget       -           -
     S     1/8       >budget       0.0 (copy-free)  1.0
     U     0/8       >budget       -           -
     P     8/8       2090.5        1.0 (40/40) 1.0
     REACH01 R4, contest law: P 8/8, 6559.5, 1.0, 0.016.

5.4 S2b, R4c's task with S1's s13 composition:
     arm   success   necessity   position
     N     0/8       -           -
     S     1/8       0.0 (copy-free)  1.0
     U     0/8       -           -
     P     1/8       1.0 (5/5)   1.0
   - Median max rung: P 2, U 2, S 2, N 0.5.
   - REACH01 R4c, contest law, with a different discovered component (the
     s7 value detector): P 7/8, necessity 0.66, position 0.109;
     REUSE_NOT_SUPPORTED.

5.5 Prediction scorecard (10 clauses: 7 held, 3 failed):
     HELD    P-S0-1   planted table exactly a ^ b; held-out rung 2
     HELD    P-S0-1b  COMPOSE 18/19/1, AUTONOMOUS
     HELD    P-S0-2   transplant 1.0 at (0,0), 0 elsewhere
     HELD    P-S1a    fold C COMBINE > 7/40 (9/40, narrowly)
     FAILED  P-S1b    fold A COMBINE > 0/40 (0/40)
     HELD    P-S1c    ROBUST_COMPOSITION_DISCOVERABLE (k = 4)
     HELD    P-S1d    instrument gate, 0 violations
     FAILED  P-S1e    not every candidate autonomous (90/90 are)
     HELD    P-S2a    CUMULATIVE_ACQUISITION_ADVANTAGE + ROBUST_REUSE
     FAILED  P-S2b    COMPOSITION_REUSE_SUPPORTED or better (REUSE_NOT_SUPPORTED)

-----
6. INHERITED LESSONS AND HOW EACH WAS HANDLED
-----
 - "Old code needs its world": the frozen REACH01 code runs unmodified;
   the law is swapped by an in-process wrapper, and the change is stamped
   into every output.
 - "Certificates must fingerprint inputs": every output carries the fold
   sha. The evidence holds sha256 manifests of all unit data
   (S1_DATA_SHA256.txt, S2A_..., S2B_...).
 - "Write precommitments you can lose": 3 of 10 clauses were lost. The
   invariance theorem was written into the prereg, so the position
   fraction was known in advance not to be a free test (Sec 7.1).
 - "Subtracted-channel novelty": applied post hoc to S1, where it bit
   (Sec 7.2). It should have been registered.
 - "Same-seed premise must be tested": tested after an incident (Sec 7.5).
   4/4 double-run units were byte-identical apart from wall-clock fields.

-----
7. HOSTILE REVIEW AND SELF-ATTACKS
-----
7.1 Robustness is largely built into the law.
   - The prereg's invariance theorem: with no energy-field contest, a tile
     behaves identically at every position and under every seed. So
     position fraction 1.0 for such mechanisms (all of S1's 29 contest-free
     candidates, and probably most S2a/S2b solutions, which r4_reduce does
     not count) is a consequence of the definition, not a discovery.
   - What could have failed and did not:
     a. the 61 S1 candidates WITH energy contests: all 61 stayed
        seed-identical at 1.0. P-S1e predicted some would break.
     b. rates (discovery 4/40; acquisition 8/8 vs 1/8) and necessity;
     c. held-out generality (1/40).
   - Status: CONCEDED. Read "robust" as "the law makes it so, and the
     remaining energy contests turned out not to matter". It is not an
     independent robustness finding.
7.2 Half of the counted compositions are joins made by the law itself.
   - s16 and s37 are separable, f = h1(a) ^ h2(b): two single-input
     detectors whose writes meet on the output cell. The certificate
     correctly says COMPOSE, but the XOR is the law's.
   - Non-separable compositions: s6 and s13, 2/40. That still meets the
     DISCOVERABLE bar (>= 2), but the count is post hoc.
   - Status: CONCEDED. Future fold-law discovery preregistrations must
     register separability.
7.3 4/40 vs 0/40 is not decisive: one-sided Fisher p = 0.058.
   - Arm C is not paired either; its search path follows the law's own
     certificates.
   - The firm statistical contrast is AUTO_ANY, 9 vs 1 (p = 0.0072).
   - Status: OPEN. A 4x replication needs its own preregistration.
7.4 The S2b comparison with R4c is not like-for-like: different component
   (s13 composition vs s7 value detector).
   - The S2a vs S2b contrast (planted a ^ b with 7 values: 8/8, vs s13
     with 2 values: 1/8) holds law and task family fixed, but the tasks
     differ (R4 task vs R4c task, different input-C cell).
   - "Coarse components reuse poorly" is a hypothesis, not a finding.
   - Status: OPEN; the controlled test is in Sec 11b.
7.5 Process incident: duplicate flight driver.
   - TaskStop left a supervisor script running. It started extra drivers
     on the S1 search plan (16:57Z, 18:13Z). Up to 4 GPU processes ran,
     against the lease's <= 2, and 25 units ran twice into the same paths.
   - Mitigation: the duplicates were killed. 4 double-run COMBINE units
     were rerun into a separate directory: every JSON field except wall
     clock, and every npz array, is identical. The search is seeded
     (default_rng(0xA5C0 + 1000*seed + arm)) and CPU == GPU bit-identical,
     so the remaining 21 double-run units are covered by the same
     argument, though not checked one by one.
   - Status: RESOLVED for outputs; recorded as a process defect.
7.6 Operator GPU sharing.
   - The run shared the card with the operator's skullport-gfx (ComfyUI,
     gfx_batch), under a supervisor that stops the flight on ComfyUI or
     on skullport GPU > 20% for 30 s.
   - The rule was agreed with the skullport session in mid-run: gfx_batch
     bakes run at ~0% GPU on M2 and may share the card.
   - Stops and restarts change wall clock only, because units are written
     atomically.
7.7 The S1 launch at 08:48Z crashed on a missing directory before any unit
   ran. The directory was created; no code changed.
7.8 Not examined: the 5 arm-C seeds whose candidates are AUTONOMOUS and
   COMBINE but not COMPOSE (s24, s26, s29, s33, s39). What makes them
   non-compositional (shared pathways?) is undescribed.

-----
8. WHAT THIS LEARNED (shapes, not verdict lines)
-----
 1. Contest arbitration was the whole of the position and seed fragility.
    Under fold, the designed combiner (S0), every discovered candidate
    (S1) and every search-built reuse solution (S2a) are position- and
    seed-robust, including where energy contests remain.
 2. The interface binding is a second, independent limit that the law
    does not touch. Every component transplants at 1.0 at (0, 0) and at 0
    at shifted frames, planted and discovered alike: inputs write into
    fixed cells.
 3. The law changes what a found structure is like, not how often raw
    material combines. Arm A: 0/40 under both laws on identical patches.
    Guided COMBINE: 7 -> 9. Autonomous: 1 -> 9.
 4. Under an XOR-fold law, "composition" includes the law's own join.
    Separability is the triviality attack, and it removed 2 of 4.
 5. The bottleneck moved from robustness to expressiveness.
    - Discovered compositions are coarse (2-4 distinct outputs, against 7
      for a ^ b), mostly not general (1/4 held-out), and reuse poorly
      (S2b P 1/8).
    - The planted, information-rich component reuses at 8/8.
 6. The fold law opens copy-free solutions to the 3-input task: arm S found
    one in 1/8 seeds in both S2a and S2b, against 0/8 in REACH01's R4 and
    R4c.

-----
9. FINAL VERDICT
-----
ROBUST01 removes the binding constraint REACH01 identified: position
fragility was a property of hash arbitration. That removal is mostly by
construction (Sec 7.1). The question it leaves is no longer robustness. It
is whether discovery can find compositions rich enough to build on. Under
this law it finds few (2/40 non-separable) and coarse ones, and the one
offered for reuse did not reuse (1/8).

-----
10. CLAIM CEILING
-----
 - One op (XOR, folded), the execution-only regime (write cost 1,
   maintenance 0, mutation 0, no rain).
 - Geometries G1 (S1, S2b) and R3/R4 (S0, S2a).
 - 40 seeds (S1) and 8 seeds per arm (S2), at 20 x 1024 evaluations per
   unit.
 - Only the template fields are folded; the energy field keeps hash
   arbitration.
 - Not tested under fold: ADD and ROTX, other geometries, larger budgets.
 - The non-separability and generality counts are post hoc.

-----
11. SUCCESSOR PRESCRIPTION (proposals; the HITL's call)
-----
 a. DISC-EXPR: a discovery run under fold that preregisters separability
    and output information (distinct outputs, held-out rung) as criteria.
    The frontier descriptor would add distinct-output count. The question
    is whether guided search can find non-separable, information-rich
    compositions at G1. Cost is about S1's: ~3 h of GPU.
 b. COARSE-CONTROL: test the hypothesis from Sec 7.4 cheaply. Run R4c's
    task with a planted component reduced to 2 output values, e.g. a
    planted 0x64 * g(a ^ b), against the planted a ^ b. 32 + 32 units,
    ~3 h. If the coarse planted component also fails (P <= 2/8), output
    information, not discovered-vs-planted, explains S2b.
 c. RELADDR: the interface limit (lesson 2). A law or tile variant where
    inputs are addressed relative to the component, not by fixed cells,
    so that transplant can work. Needs design.
 d. Not recommended yet: a 4x S1 replication for power. (a) asks the
    sharper question.

-----
12. PRIMARY ARTIFACT INDEX (branch aether/robust01-2026-10-17)
-----
 c989c09a1  freeze: PREREGISTRATION.md, RULES.json, FREEZE.sha256, code
 3cd288b92  S0_RESULT.md + evidence/S0/        (28e39c815 wording fix)
 19b3bbc09  S1_RESULT.md + evidence/S1/ (REDUCTION_S1.json, 80 certs,
            S1_DESCRIBE.json, recheck/, S1_DATA_SHA256.txt),
            r01_s1_describe.py
 b847117da  S2A_RESULT.md + evidence/S2A/
 3b27b5bac  S2B_RESULT.md + evidence/S2B/
 f55a54b0b, 4ba81866b  journal: GPU-sharing gate, duplicate-driver incident
 Data: C:/Prometheus-data/aether_robust01/{S0,S1,S1_recheck,S2A,S2B}/ on M2
