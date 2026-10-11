# C-016-T042 -- Q3 re-check of the repaired Ensorain assay (FREEZE_ENSORAIN v1.1.0): REPORT

Reviewer: Pallas[harry1-7368c61b], claude-fable-5-1 (Q3; runtime verified at comms boot, tier heavy), headless on
harry1 (M4), 2026-10-11. Surface: FREEZE.md v1.1.0, FROZEN.json fcfe67ce (34 files; LF sha256 recomputed here),
code 6fff93af9, amendment 030f1746f, re-freeze ebe4860c1; base 28b5c5e1c. `freeze check` OK before the claim, after
every mutant restore (12/12) and after the runs. No confirmatory lifetime exists (seeds 16_330_xxx untouched; `assay
confirm` never called); no searched subject's lifetime was run (FS reads structure). Caveats: cell member; writes no
production code; an informed re-check (code, tests, DEV_CHECK.json and red_rows.jsonl read first), not first-sight;
a different model family from the repairer (Argus on claude-opus-5-5) but the same vendor. Scope: TASK.json
`problem` -- confirm the repair closes REPORT s4 without opening a new hole; no second challenge, no repair round
after this (PREREGISTRATION s11.12): a survivor here is a recorded limitation the result must carry, stated in s4.

## 1. Ordering evidence (git, UTC; one headless session; <= 2 computing processes at any moment)

    82f3342aa  main    CLAIMED (LEASE.json)                                                  13:05Z
    f5523168c  main    IMPLEMENTING                                                          13:08Z
    ec70e1596  branch  the SET: CHALLENGE_SET_R2.md with predictions, expected_r2.json,
                       subjects_r2.py, cases_r2.py, witnesses_r2.py, run_edits_r2.py          13:29:48Z
    cases      S1 S2 S3 FS GR5 B3 B1 S5 P3 B2 REF WK RT TN5 TN4 (one process)                 13:30Z-13:33Z
    edits      baseline, E1 E2 E3 E4 E6 (suite phase; the runner's child overlapped the
               case process: two computing processes)                                        13:32:43Z-13:33:45Z
    patch      run_edits_r2.py: E5's T040 find string no longer occurs in v1.1.0 (assay.py:146
               changed the arm tuple); an E5 control with the v1.1.0 line was added (s6.1)   13:34Z
    edits      E5' R1 R2 R3 R4 R5 R6 (suite), W1-W5 (witness phase)                           13:34:29Z-13:36:30Z
    cases      S4 (the 26,400-row reproduction, 242 s; overlapped the edits' child only)     13:36Z-13:40Z
    (next)     results_r2.jsonl, red_rows_r2.jsonl, this report, receipt -- one commit; GREEN /
               INTEGRATION_READY on main

The set's files are byte-identical to ec70e1596 except run_edits_r2.py, which differs by the three-line E5' entry (s6.1);
no prediction, seed or case logic changed. R2 seeds 16_360_001..16_369_999 (subjects_r2.conflicts() == [] checked
before every case run; disjoint from s6, from WTP-05's registered ranges and from the T040 challenge range).

## 2. Score (16 cases; 12 mutants; 5 witnesses)

    sound     S1 S2 S3 S4 GR5                          5/5 AS_EXPECTED
    re-runs   B1 S5 P3 B2 B3                           5/5 AS_EXPECTED (REPORT s4's cases, repaired rule)
    broken    WK walker SURVIVOR, FS family S SURVIVOR 2/2 as predicted
    semantic  TN5 ref_tiny 1e-5 SURVIVOR               as predicted
    probes    RT ratchet RECORDED (prediction held); TN4 ref_tiny 1e-4 RECORDED (sub-prediction MISSED, s6.2)
    comparator REF RECORDED (REVISION_HISTORY_DEPENDENT)
    edits     baseline GREEN 33/33; E1 E2 E3 E4 E6 R1 R2 R3 R4 R5 R6 each RED on its named test (11/11; the suite
              fails on each); E5 verbatim NOT APPLICABLE (find count 0 in v1.1.0), E5' KILLED by the two predicted
              tests (test_assay Endpoint.test_frozen_reference_scores_zero_late_and_full_pre,
              DeclaredMemory.test_frozen_life_may_not_change_any_parameter) plus Registered.test_qd_jitter_and_qe_learns_pre_on_dev;
              hash guard fired on 12/12 mutants; every restore verified (sha256 + git diff --quiet), freeze check OK
              after each; W1-W5 differ between original and mutant 5/5 (red_rows_r2.jsonl)
    predictions  15 of 16 case predictions held in full (TN4's "noise arm revised in > 0 lives" missed); edits 12/12;
              witnesses 5/5

## 3. CLOSED / NOT CLOSED per surface

    INFERENCE        REPORT s4.1 CLOSED: the four reference-graph learners (theta0 +.2, 0, +1, -.1) now read one
                     verdict, REVISION_HISTORY_DEPENDENT, with the same full-arm count (121 of 200 revised; dev 255 of
                     400), and jitter is REVISION_NOT_SHOWN because its noise arm is itself (K1n exactly 0:0:200; K1f
                     alone 9:0, p .002). The Holm step, the G_PRE arm, the window, the control assignment, the gate
                     threshold, the intersection-union, the competence bound, the whole-life endpoint and the noise
                     arm's eta are each pinned by a test that turns RED on its mutant (11/11, re-run here with -B).
                     NOT CLOSED on one bounded point the repair opened: the whole-life endpoint with the
                     intersection-union K1 is passed by LAW-BLIND DRIFT (WK: K1 vs frozen 48:0, vs noise 48:0, K2
                     36:31 p .31, noswitch 142 of 200, theta moves 1.24 on average in a life with no switch) and reads
                     REVISION_WITHOUT_RETAINED_COMPETENCE; the same construction with role 5 correct (RT) reads
                     REVISION_NOT_HISTORY_DEPENDENT and is switch-triggered (noswitch 200/200, theta never moves
                     without a switch). The two K1-only labels therefore do not license "revises": they cover drift
                     and halt-on-success search alike, and only K2 and the noswitch column separate them. Bearing:
                     NARROWING of two s5 rows (s4 L1), a limitation the result must carry; the family-P reading is
                     unaffected (K2 96:15, noswitch 200/200). Nothing blocking.
    INSTRUMENT       CLOSED. S4 reproduces the 26,400 development rows bitwise (sha b54c751b..., 242 s); the noise
                     arm shares the full arm's world episodes block for block and moves theta <= 4.2e-9 in a life
                     (S3); memory_ok / recompute_ok hold on every one of the 10,400 R2 rows (every subject, every
                     arm) incl. the walker, the ratchet and the amplified ref_tiny genomes; the registered controls
                     now contain a stochastic non-learner (Q-d) and a positive the old rule got wrong (Q-e); P1 is
                     fixed and pinned (R3 RED). Two limitations recorded, neither needing a change before the run:
                     (L3) ETA_NOISE is an absolute floor in a physics whose update is in absolute units, so the
                     comparator is not scale-invariant (TN5: the reference rescaled by 1e-5 is its own noise arm,
                     K1n 0:0:200 with full and noise rows byte-identical, REVISION_NOT_SHOWN; TN4 at 1e-4 reads
                     REVISION_NOT_HISTORY_DEPENDENT) -- a false negative only, and family S's smallest eta is .059;
                     (L5) no registered qualification control is a drift subject, so Q-a..Q-e cannot refuse a rule
                     that passes drift (the walker row is the evidence that it does).
    INTERPRETATION   NOT CLOSED on two points, neither blocking. (a) Family S "from genome structure" (assay.py:192-195)
                     reads a non-empty declared plastic key set and not LIVENESS: searched_16310007's plastic LIN
                     (node 12) is an input of no node and searched_16310008's plastic BILIN (node 3) reaches neither
                     ACT nor WRITE (FS, tape._live, the compiler's own liveness); both are parameter-free in effect,
                     and an unconnected plastic CONST is admitted (searched_dead). Family S has ONE subject whose
                     plastic parameter can touch its scored action (searched_16310006). Bearing: the result must
                     report search accessibility as 1 testable and 7 not (5 parameter-free, 2 dead-plastic), and note
                     that 006 is tested at Holm's alpha/6 worst case for a family of one (s4 L2). (b) The s5 readings
                     for REVISION_NOT_HISTORY_DEPENDENT and REVISION_WITHOUT_RETAINED_COMPETENCE need "or law-blind
                     drift" (s4 L1); 006's structure (eta/sigma = 50, sigma .02) is the walker's regime (|theta| >>
                     sigma), so if it reads a K1-only label, drift is the first thing its noswitch count and K2 must
                     exclude. Also recorded, bearing NONE: G_R5's meaning (L4), the bound dependence of the reference's
                     own revisability (O1), the manifest's blindness to added files (O2).

Nothing found is BLOCKING; nothing in s2-s4, s6-s7 or s10 needs to change; the confirmatory run can execute on the
frozen v1.1.0 code and its rows will be valid evidence. The verdict labels it prints must be read with s4.

## 4. What the result must state (no further repair round; PREREGISTRATION s11.12)

L1 DRIFT. "REVISION_NOT_HISTORY_DEPENDENT" and "REVISION_WITHOUT_RETAINED_COMPETENCE" mean: the subject's revised
   lives exceed those of its frozen AND its noise-matched configuration (both sign tests at Holm alpha), and its
   revised lives do NOT exceed those of a history-shuffled configuration (or the competence is not shown kept). A
   plastic parameter whose ES update is reward-uncorrelated noise -- a genome whose decision the perturbation never
   flips, with permanent reward spread in the block -- produces exactly this pattern (walker: 48 of 200 lives revised
   in the full arm, 0 in frozen and noise, 43 in shuffle; noswitch 142/200). So do a halt-on-success search (ratchet:
   53/0/0/52; noswitch 200/200) and a genuine learner whose K2 is underpowered. Neither label licenses "revises" or
   "responds to the switch" on its own. The noswitch count must be printed beside either label; a count well below
   the subject's N says the parameter moves without a switch. Only REVISION_HISTORY_DEPENDENT (K2) excludes drift.
   For the reference, K2 holds (96:15 here; 204:28 on development) and noswitch is 200/200: unaffected.
L2 FAMILY S. Of the three searched subjects declared to family S by structure, only searched_16310006's plastic
   parameter is live (reaches ACT); searched_16310007 and searched_16310008 carry dead plastic code and are
   parameter-free in effect. Search accessibility is reported as 1 testable subject and 7 not (5 with no plastic key,
   2 with a dead one). Holm runs over the 6 registered tests of family S; 006's K1 and K2 are read at the alpha/6
   worst case (power at p_full .60 vs p_ctrl .45: .964 instead of .987; DEV_CHECK sensitivity rows). 007/008's
   labels will be REVISION_NOT_SHOWN by construction and are not evidence about search.
L3 NOISE FLOOR. ETA_NOISE = 1e-9 is absolute (assay.py:33, :97-103; tape.py:349 updates in absolute units). A genome
   with its own eta <= 1e-9 is its own noise arm and cannot pass K1 (s11.4); a genome with eta within a few decades
   of the floor has a noise arm that learns (TN4). The reference rescaled by 1e-5 with an amplified readout is such a
   genome and reads REVISION_NOT_SHOWN (TN5). A false negative only. No registered subject is near the floor (family
   S's smallest eta .059, the controls' 1e-9 is jitter by design).
L4 G_R5 means: significantly more than 9 lives in 10 (>= 371 of 400) keep >= 90% of their post-switch role-5 gates.
   A subject at 89% in every life fails it; one at 0% in 29 of 400 lives and 100% in the rest passes it (GR5).
L5 QUALIFICATION. Q-a..Q-e cannot detect that the rule passes drift: no drift control is registered (one would FAIL
   under v1.1.0, which is why it cannot be added now). The walker row (results_r2.jsonl WK_WALKER) is the recorded
   evidence that it does; it is read with L1, not as a qualification failure.
O1 (observation, interpretation of s1 "bounded persistent learner"). The reference's revisability depends on the
   PLASTIC_BOUND clip: the same decision statistics with an unbounded parameter (ref_tiny, whose theta can grow
   without limit) revise in 8 of 200 lives, late accuracy .066, against the reference's 121 and .604 on the same
   seeds. Once |theta| >> sigma the perturbation no longer flips decisions and the ES signal vanishes; the clip keeps
   the reference at theta = 1 where 2.3% of its decisions still flip and the post-switch gradient can act. "Bounded"
   is part of the mechanism, not a safety margin.
O2 (observation, freeze). `freeze check` verifies pinned files only; files added under rso/ensorain/ are invisible to
   it (S1 lists the 7 R2 files a re-cut would pin). Harmless for this run (the assay imports only pinned modules);
   whoever re-cuts the manifest should EXCLUDE challenge/R2/ as challenge/ is, or accept that the re-check's own
   files become frozen bytes.

## 5. Cases in detail

### 5.1 Sound

S1: 34/34 pins equal (git blob and disk, LF); FROZEN.json LF sha256 fcfe67ce98d0ac59ed01cc807af6ecf8c5395bd6055ae4b02a04f4375048c7ab;
freeze.mismatches() and env_mismatches() empty; 030f1746f is an ancestor of ebe4860c1 (08:43:14 vs 08:45:30 -0400);
ebe4860c1 is an ancestor of HEAD. S2: k_pos(400, .05, 1/2) = 217, k_pos(400, .05, 9/10) = 371 (P(X >= 371) = .0357,
P(X >= 370) = .0524), k_pos(200, .05, 1/2) = 113, k_pos(200, .05, 9/10) = 188, from math.comb / Fractions; ruler.thresholds,
analysis._gate (217 True, 216 False) and _competence (371 True, 370 False) agree; power_revised at the development
rates reproduces DEV_CHECK `power` (1.000 x 3). S3: the reference on 5 seeds, full vs noise: episodes identical in
12/12 blocks on 5/5 seeds, sw equal, noise-arm theta move 1.7e-9..4.2e-9, full-arm .79..1.2. S4: 26,400 rows,
rows_sha256 b54c751b0796bc58d6dd04f4ddd69deaba879e5f4925757ecf8aab3e85e0f830 = DEV_CHECK.json, 242 s. GR5: as
predicted (s4 L4).

### 5.2 Re-runs (N = 200 R2 seeds; arms full / frozen / noise / shuffle / newlife / noswitch)

    subject      theta0  verdict                        pre  K1f (W:L:T)  K1n (W:L:T)  K2 (W:L:T)   revised f/fz/n/sh/nl  noswitch
    reference    +.2     REVISION_HISTORY_DEPENDENT     200  121:0:79     120:0:80     96:15:89     121/0/1/40/29         200
    innate_zero   0      REVISION_HISTORY_DEPENDENT     200   89:17:94     94:21:85   105:11:84     121/49/48/27/29       200
    innate_max   +1      REVISION_HISTORY_DEPENDENT     200  121:0:79     121:0:79    105:8:87      121/0/0/24/29         200
    learns_pre   -.1     REVISION_HISTORY_DEPENDENT     200  121:0:79     120:0:80    109:5:86      121/0/1/17/29         200
    jitter       +.1*    REVISION_NOT_SHOWN             200    9:0:191      0:0:200     8:5:187       9/0/9/6/9           185
    * eta 1e-9

B1's endpoint sub-prediction held: all 9 of jitter's revised full-arm lives have sw >= 7 (3 at sw 7 of 40, 6 at sw 8
of 32; 0 at sw 4-6 of 128), i.e. one or two late blocks read on 32-64 gates; the frozen arm has none; the noise arm
has the same 9 (ties). The whole-life endpoint admits a fixed-sign policy by variance only where the late half is
short, and the intersection-union removes it. B3 under the repaired rule: 180 of 400 lives at zero post role-5 ->
220 retained < 371 -> REVISION_WITHOUT_RETAINED_COMPETENCE (closed).

### 5.3 The new parts, one attack each

    case  part attacked                 result
    WK    intersection-union K1,        law-blind random walk (type-1 s*theta, |theta| >> sigma; type-2 constant):
          whole-life endpoint           G_PRE 175/200, G_R5 0/200, K1f 48:0:152, K1n 48:0:152, K2 36:31:133 (p .31,
                                        Holm .31), REVISION_WITHOUT_RETAINED_COMPETENCE; revised by sw 9/35, 6/38,
                                        10/55, 12/40, 11/32 (no sw dependence: drift, not variance); noswitch 142/200;
                                        in 40 no-switch lives theta moved 1.24 on average (max 1.5); memory_ok and
                                        recompute_ok on 1,400/1,400 rows. SURVIVOR; prediction held in every clause.
    RT    (probe) the same label class  halt-on-success search: G_PRE 200, G_R5 200, K1f 53:0, K1n 53:0, K2 42:41
                                        (p .5), REVISION_NOT_HISTORY_DEPENDENT; noswitch 200/200; theta never moved
                                        without a switch (40 lives, max 0.0). Prediction held.
    TN5   noise arm (eta -> 1e-9)       the reference at scale 1e-5: full and noise rows identical on 200/200 seeds;
                                        K1n 0:0:200; K1f 8:0 (p .004); REVISION_NOT_SHOWN. SURVIVOR (s4 L3). Its full
                                        arm revises 8/200, late .066 (O1: the unbounded parameter runs away).
    TN4   noise arm, graded             scale 1e-4 (eta 1e-8): noise arm revised 0/200 (predicted > 0: MISSED, the
                                        runaway dominates both arms), full 8/200, K1 8:0 (Holm .0078), K2 6:36 (the
                                        shuffle walk from a 2e-5 start crosses zero in 38 lives) ->
                                        REVISION_NOT_HISTORY_DEPENDENT. Recorded; the same limitation.
    FS    family S from structure       family_s(SUBJECTS) = [006, 007, 008]; plastic node live from ACT: 006 True
                                        (node 1 -> 3 -> 5 -> 6 -> 7 -> 9 -> 10), 007 False (node 12 feeds nothing),
                                        008 False (node 3 feeds 4, 5, 11, 12, 15, 17; ACT 8 <- 7 <- 1, 0; WRITE 16 <- 7);
                                        searched_dead admitted. SURVIVOR (s4 L2). eta/sigma: 006 50.4, 007 2.4, 008 .46.
    GR5   371/400 bound                 as s4 L4; no gap beyond the bound's stated meaning.

### 5.4 Edits (red_rows_r2.jsonl; every subprocess -B after a cache purge; hash guard on 12/12 mutants)

    E1 Holm bypass           RED  Inference.test_holm_decides_not_the_raw_p         W1 NOT_SHOWN -> NOT_HISTORY_DEPENDENT (raw .040, Holm .081)
    E2 G_PRE frozen arm      RED  Gates.test_gpre_counts_the_full_arm (+2)          W2 learns_pre 12 seeds: G_PRE True -> False, REFUSED
    E3 late window sw+2      RED  Instrument.test_late_window_starts_three_blocks_after_the_switch
                                                                                     W3 (c_early,n_early,c_late,n_late) 4/102/53/101 -> 1/63/56/140
    E4 K1<->K2 controls      RED  Inference.test_k1_is_against_frozen_and_k2_against_shuffle (+1)
                                                                                     W4 NOT_SHOWN (K1 vs frozen ties) -> NOT_HISTORY_DEPENDENT (40:0)
    E5 frozen arm plastic    n/a  find count 0 in v1.1.0 (assay.py:146 arm tuple); E5' with the v1.1.0 line: KILLED by
                                  the two predicted test_assay tests + Registered.test_qd_jitter_and_qe_learns_pre_on_dev
    E6 majority gate         RED  Gates.test_gpre_threshold_is_the_exact_binomial_not_a_majority
                                                                                     W5 REFUSED (205 < 217) -> REVISION_HISTORY_DEPENDENT
    R1 K1 without noise arm  RED  Inference.test_k1_needs_the_noise_matched_arm_too
    R2 G_R5 at chance 1/2    RED  Gates.test_gr5_has_a_competence_bound
    R3 no np.isfinite        RED  Instrument.test_nan_plastic_value_is_flagged
    R4 late-only endpoint    RED  Inference.test_endpoint_is_the_whole_life (+1)
    R5 family S = searched   RED  Registered.test_family_s_is_declared_from_genome_structure
    R6 noise arm keeps eta   RED  Instrument.test_noise_arm_shares_the_full_arms_draws (+1)

Every kill is behavioural (neither test module hashes the tree). W2's original verdict at N = 12 is
REVISION_WITHOUT_RETAINED_COMPETENCE because G_R5 cannot pass below N = 29 (s11.8), which is the registered behaviour
and does not touch the witness (G_PRE True -> False).

## 6. Escapes, misses and tooling

6.1 E5 verbatim is not applicable to v1.1.0: the repair changed the arm tuple at assay.py:146, so the T040 find string
occurs 0 times (the runner refused, as designed). I added E5' (the same fault with the v1.1.0 line) to run_edits_r2.py
after the set commit: three lines, disclosed; `git diff ec70e1596 -- rso/ensorain/challenge/R2/` shows exactly that
hunk. Argus's red_rows.jsonl did not include E5 either (RED_EDITS.json lists E1 E2 E3 E4 E6; E5 was the control).
6.2 Miss: TN4's sub-prediction (noise arm revised in > 0 lives) failed: both arms of the rescaled reference revise
rarely because the unbounded parameter runs away (O1), and the noise arm (1/10 rate) revised none. The verdict
(REVISION_*) part held. Recorded, unscored.
6.3 Processes: the case process and the mutation runner's child overlapped for ~1 min, and S4 overlapped the runner's
child for ~2 min: two computing processes at most, never three (the runner's parent only waits). CPU: cases ~2.5 min,
S4 242 s, 12 mutants x ~10 s suite + witnesses ~1 min. No paid compute, nothing on ubu006, no WTP-05 seed.
6.4 Bytecode hygiene: every subprocess with -B after purging rso/ensorain's __pycache__; restores verified by sha256 and
`git diff --quiet`; `freeze check` OK after each (red_rows_r2.jsonl, 12/12).
6.5 Not done: no G_R5-keeping pure walker (impossible with eta and sigma shared by every parameter: CHALLENGE_SET_R2.md
s5), no timer (T040 P2 and s5 of the set: none exists in this physics), no searched-subject lifetime. Q3 reviewer time:
about 40 min wall from boot to this report (ONBOARDING s8).

## 7. Files

    rso/ensorain/challenge/R2/CHALLENGE_SET_R2.md   the set and its predictions (ec70e1596)
    rso/ensorain/challenge/R2/expected_r2.json      the answer key
    rso/ensorain/challenge/R2/subjects_r2.py        walker, ratchet, ref_tiny, searched_dead; R2 seeds; conflicts()
    rso/ensorain/challenge/R2/cases_r2.py           S1 S2 S3 S4 FS GR5 B3 B1 S5 P3 B2 REF WK RT TN5 TN4
    rso/ensorain/challenge/R2/witnesses_r2.py       W1-W5 (six-arm schema)
    rso/ensorain/challenge/R2/run_edits_r2.py       the mutation re-run (E5' added after the set, s6.1)
    rso/ensorain/challenge/R2/results_r2.jsonl      one row per case (16)
    rso/ensorain/challenge/R2/red_rows_r2.jsonl     baseline, 12 suite rows, 5 witness rows
    rso/ensorain/challenge/R2/REPORT.md             this file
