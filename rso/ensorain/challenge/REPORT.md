# C-016-T040 -- Q3 challenge of the frozen Ensorain assay (FREEZE_ENSORAIN v1.0.0): REPORT

Reviewer: Pallas[harry1-855aa018], claude-fable-5-1 (Q3; runtime verified at comms boot, tier heavy), headless on
harry1 (M4), 2026-10-11. Surface: FREEZE.md, code commit 93623a03a, FROZEN.json b198ab8f; 26/26 pinned hashes
verified by `freeze check` before the claim and recomputed independently (S1) before the set was written; `freeze
check` OK after every edit was restored. No confirmatory lifetime exists (seeds 16_330_xxx untouched; `assay confirm`
never called; no searched-subject endpoint computed; EXPOSURE.md). Caveats printed with every record: cell member;
writes no production code; an INFORMED coverage review (the frozen test bodies were read), not first-sight; a
different model family from the builder (T030 author Argus on claude-opus-5-5) but the same vendor. One exposure
disclosed in EXPOSURE.md (the integrator's killed G_PRE-removal mutant; not scored here).

## 1. Ordering evidence (git, UTC)

    7c95657ab  main    CLAIMED (LEASE.json)                                                       11:38Z
    3a622d053  main    IMPLEMENTING                                                               11:46Z
    22bf4ce85  branch  the SET: EXPOSURE, CHALLENGE_SET with predictions, expected.json,
                       subjects_c.py, cases.py, witnesses.py, edits.json, run_edits.py          11:51:26Z
    cases      S1 S2 (then S3 crashed on a name collision in MY harness, s6.1)                     11:51:49Z
    edits      baseline 19/19 GREEN; E1-E6 suite; W1-W5 witnesses                                 11:52:09Z-11:52:47Z
    cases      S3 B1 REF B2 S5 B3 P1 P2 S4 under the two-line harness fix                         11:53:15Z-11:55:27Z
    96e995a9c  branch  post-hoc probe P3 (innate_zero) with its prediction, BEFORE it ran          11:56:40Z
    posthoc    P3 run; P4 (theta after block 0) written and run after the cases                    11:57Z-12:02Z
    (next)     results.jsonl, mutation_rows.jsonl, this report, receipt -- one commit; GREEN /
               INTEGRATION_READY on main

The set's data files (expected.json, edits.json, subjects_c.py, witnesses.py, run_edits.py, CHALLENGE_SET.md,
EXPOSURE.md) are byte-identical to 22bf4ce85. cases.py differs from 22bf4ce85 by exactly two lines (s6.1): the
imported channel constant P1 was shadowed by the probe function P1; the fix renames the import. No prediction and no
case logic changed.

## 2. Score (the packet's denominators: >= 1 sound, 2 broken, 2 semantic edits, adversarial genomes)

    sound    5 scored: S1 S2 S3 S4 AS_EXPECTED; S5 NOT_AS_PREDICTED (an honest miss that is the report's
             sharpest finding, s4.1). S6 (the pairing null, inside B1) AS_EXPECTED.
    broken   3 scored, 3 SURVIVOR: B1 jitter (REVISION_NOT_HISTORY_DEPENDENT for a non-learner), B2 innate_max
             (REVISION_HISTORY_DEPENDENT with nothing learnable before the switch), B3 G_R5 semantics.
    probes   P1 and P2 RECORDED, both predictions held; post-hoc P3 and P4 RECORDED (labelled, unscored).
    edits    6 proposed, 6 applied (find count 1 each), 6 restored and verified, freeze check OK after each.
             E1 E2 E3 E4 E6 SURVIVE the frozen suite (19/19 pass on each mutant); every witness differs as
             predicted. E5 (control) KILLED by exactly the two predicted tests. The hash guard fired on every
             mutant (recorded with the mutant in place): it protects the run; it pins no behaviour.
    predictions (expected.json): cases 8 of 10 scored predictions held (S5 missed its verdict; B2 held its verdict
             but missed the K2-direction sub-prediction, s4.3); P1/P2 held; edits 6 of 6, witnesses 5 of 5;
             post-hoc P3's own prediction missed on K2 (s4.1).

Every suite kill here is behavioural: the frozen unittest suite contains no test that hashes the tree
(test_confirm_refuses_on_changed_bytes mocks file_sha). This differs from C-013-T011, where a manifest test
hash-killed four edits; here the hash guard lives only in `freeze check` / `assay confirm`.

## 3. CLOSED / NOT CLOSED per surface

    INFERENCE        NOT CLOSED -- the sign test, its seed pairing, the thresholds and the power table are SOUND
                     (S2, S6; s5.1). What is not closed: (a) K1 and K2 are contrasts against the subject's OWN
                     frozen and shuffled configurations, so the verdict is a function of the innate value of the
                     plastic parameter: one learning rule, four innate starts, identical late-window behaviour,
                     three different verdicts (s4.1: B1, P3, REF, S5). K1 is passed by perturbation noise alone
                     when the innate value is on the pre-switch side (B1) and cannot be passed when it is on the
                     post-switch side (S5: the frozen arm IS the Smuggler). (b) The Holm step, the endpoint window,
                     the control assignment and the gate threshold are pinned by hash only (E1, E3, E4, E6).
                     Bearing on the run as frozen: NONE (the rows carry what the narrowing needs). Bearing on the
                     registered verdicts: NARROWING of the s5 "licensed reading" column before any result is
                     read, and an AMENDMENT candidate (s5) for the repair round. Nothing BLOCKING.
    INSTRUMENT       NOT CLOSED on the control set; the code is correct on every input tried -- memory_check and
                     recompute_check hold on 9,600 reproduced development rows (S4, bitwise) and 7,400 challenge
                     rows; the NaN hole fails closed (P1); the four-policy argument is a theorem of the world (S3)
                     and extends to plastic timers (P2: analytic, and the best timer TAPE allows is a reviser whose
                     no-switch behaviour matches the predicted equilibrium to two decimals). Not closed: the
                     registered qualification controls (s5 Q-b, Q-c) are all deterministic, so the noise class
                     (B1) and the innate-position dependence (S5/P3) pass qualification unseen; no no-switch arm
                     exists; which arm G_PRE reads is unpinned (E2). Bearing: AMENDMENT candidate for the repair
                     round (two control subjects, one descriptive arm, five tests). Nothing BLOCKING.
    INTERPRETATION   NOT CLOSED -- four readings cannot be supported as written: s1 "revise a lifetime-LEARNED
                     parameter" (B2, S5, P4), the s5 row "K1 only -> revises" (B1, P3), "depends on its own reward
                     history" as a property of the learner rather than of the pair (learner, innate start)
                     (P3 vs REF), and "keeps the unrelated competence" (B3). "Search accessibility" over 8 subjects
                     of which 5 cannot be revisers by construction needs the same narrowing (s4.4). Bearing:
                     NARROWING required BEFORE any result is read; a wording-only versioned amendment of s1 and
                     the s5 table is the cheapest form. Not blocking the run.

Nothing found is BLOCKING; nothing found requires a change to the arms, seeds, endpoint, N, alpha or the
confirmatory command (s2-s4, s6-s7, s10). The confirmatory run can execute on the frozen code and its rows will be
valid evidence; the VERDICT LABELS it prints must be read with s4's narrowing, and the repair round should land the
s5 wording and the two missing controls (s5 below) before T050 reads a label as a scientific statement.

## 4. Survivors and their bearing on the registered verdicts

### 4.1 Inference: the contrasts are self-relative, so the verdict depends on the innate value

All five subjects below carry the reference graph (planted.py:115-116) and the reference's eta = 1, sigma = 0.5;
only the plastic CONST's initial value theta0 differs. At the 200 challenge seeds their FULL arms have the same
late-window counts (late accuracy .6336, K1 ties 8, newlife pre .526 for every one of them): the ES update takes
theta to the clip within the first blocks from every start (P4: after one update theta >= .21 from -0.1, >= .41 from
0, >= .65 from +0.2; at 1.0 it stays), long before the late window opens at sw + 3 >= 7, and from there the
trajectories coincide because the rng streams coincide. What differs is the CONTROL arms:

    theta0   subject       frozen arm is       frozen late  shuffle late  K1 (W:L:T, p)          K2 (W:L:T, p)          verdict
    +0.1*    jitter        +s (no noise)       .000         .422          200:0:0   6e-61        101:97:2  .42         REVISION_NOT_HISTORY_DEPENDENT
     0.0     innate_zero   +1 (chance)         .507         .554          121:78:1  .0014        101:98:1  .44         REVISION_NOT_HISTORY_DEPENDENT
    +0.2     reference     +s                  .000         .444          192:0:8   2e-58        121:77:2  .0011       REVISION_HISTORY_DEPENDENT
    +1.0     innate_max    +s                  .000         .188          192:0:8   2e-58        155:44:1  5e-16       REVISION_HISTORY_DEPENDENT
    -0.1     learns_pre    -s (the Smuggler)   1.000        .587          0:197:3   1            93:106:1  .84         REVISION_NOT_SHOWN
    * jitter has eta = 1e-9: perturbation on, learning off (theta moved 1.5e-9 over a life); its full-arm late
      accuracy is .423, the noise floor, not .6336.

Readings the frozen rule licenses (s5 table) against what happened:

- "REVISION_NOT_HISTORY_DEPENDENT: revises; dependence on own history not shown" -- held by jitter, which revises
  nothing (B1, SURVIVOR), and by innate_zero, which learns and revises exactly as the reference does (P3,
  post-hoc). K1 is "the plastic configuration beats its own frozen configuration on the late window": when the
  innate value is on the pre-switch side the frozen arm scores 0 and any noise wins (s11.4 says "nearly automatic";
  it is automatic, and needs no learning); when the innate value is at zero the frozen arm is chance and K1 is a
  real contrast; when it is on the post-switch side the frozen arm is perfect and K1 cannot be won. It is not a
  world-demand contrast; it is a statement about the innate value. The four-policy argument (s3) is correct for
  deterministic policies and does not reach the noise class because the frozen arm removes the perturbation
  together with the learning.
- "REVISION_HISTORY_DEPENDENT: revises, and the revision depends on its own reward history" -- held by the
  reference and innate_max; NOT held by innate_zero, whose learning is the same computation from block 1 on. K2
  compares the learner to the clipped random walk that starts at the same innate value: from +0.2 or +1.0 that walk
  sits on the wrong side of the late window often (.444, .188) and the contrast is strong; from 0 it is chance
  (.554) against the learner's .634 and 200 lives do not separate them (101:98). K2's sensitivity is a property of
  the (learner, innate start) pair. For the REFERENCE the reading is valid: its innate start is known and K2 is
  genuinely the evidence (K1 carries none). For a SEARCHED subject the label alone is uninterpretable without its
  frozen-arm and shuffle-arm late accuracies, which the rows carry (analysis `late` / `late_n`).
- "REVISION_NOT_SHOWN: no revision shown; not a demonstrated absence" -- held by learns_pre, the one subject that
  LEARNS the pre-switch law in-life (block-0 type-1 accuracy .413, then the law, then the revision; pre-competent
  200/200). Its frozen arm acts -s, the post-switch law, so it is late-perfect and K1 is lost on every pair. A
  genuine lifetime learner that happens to be innately on the post-switch side is read as "no revision shown".
  (The verdict's own caveat, "not a demonstrated absence", is doing the right work; the problem is the K1 row above
  it.) S5 was predicted REVISION_HISTORY_DEPENDENT: my miss, and the finding.

NARROWING (before any label is read): K1 holds => "the plastic configuration's late accuracy exceeds its frozen
configuration's; for an innate value on the pre-switch side this is satisfied by perturbation noise". K2 holds =>
"the plastic configuration's late accuracy exceeds that of a history-shuffled configuration started at the same
innate value". Neither is "revises" on its own; the pair (K2 with the subject's frozen-arm late accuracy near 0 and
its full-arm late accuracy well above the shuffle arm's) is the revision evidence, and that is what the reference
shows. AMENDMENT candidate (repair round): a noise-matched control arm (plasticity on, eta -> 0: the perturbation
without the update) as the K1 comparator, or K1 against both; and the per-subject frozen/shuffle late accuracies
printed beside every verdict.

Sound in this surface: S2 reproduces k_pos = 217 (P(X >= 217) = .0494), the Holm worst case 221, q = .5701 / .6240
from the 400 development lives by an independent pair loop, power .7777 / .9985 (P) and .5235 / .9882 (S at
alpha/16) -- all equal to s7 within .002. Family S at alpha/6 (if its family were the 3 subjects that carry a
plastic parameter) would have .641 / .995; the 10 forced p = 1 tests cost power, not validity. S6: jitter's K2 is
101:97 (p .42), the empirical null of the s11.2 pairing with diverged rng streams: exchangeable, valid, as the
preregistration argues.

### 4.2 Instrument

- memory_check / recompute_check: sound on every input tried. S4 reproduces the 9,600 development rows bitwise
  (rows_sha256 1d5ccf28..., 84 s), a third reproduction from a different worktree. All 7,400 challenge rows hold
  both flags except P1's frozen arm, where NaN is flagged. P1: the bound `np.abs(ya) > PLASTIC_BOUND` is False for
  NaN, so memory_check(g, g, plastic=True) == (True, 8) for a NaN plastic value; the non-plastic comparison
  np.array_equal(NaN, NaN) is False, so the frozen arm flags it and the verdict is INSTRUMENT_FAULT. Fails closed by
  the accident of the second comparison. Bearing NONE; `np.isfinite` is a one-line repair.
- G_PRE and the four-policy argument (S3): over 12,800 gates the scored step shows exactly 2 distinct type-1
  observation vectors (s = +1 / -1) and 2 type-2; the corridor step is never scored; the type-1 target is s * law.
  With z = 0 at step 0 a deterministic genome's scored action is a function of s alone: {+s, -s, +1, -1} is the
  whole deterministic memoryless class, as s3 says. The N1-N4 collapse is a property of the world.
- Timers (P2). The wake note asked whether a Smuggler could learn the first sign and flip on a block counter. The
  analytic argument in CHALLENGE_SET.md P2 says no: the only cross-block channel is the ES update of a plastic
  parameter; whatever parameter the type-1 action reads receives a law-dependent gradient of the same scale as any
  law-independent (type-2) drive, with the pull maximal at the flip point, so in expectation the parameter stalls
  below its flip point before the switch and crosses after it; the discrete regime is bounded by the ES signal-to-
  noise (<= ~3.7 per block at K = 64). The probe confirms the mechanism: clock_hybrid (phi driven by type-2, read by
  type-1, predicted equilibrium (d - c)/2 = -0.625 with type-1 accuracy Phi(.75) = .773) never flips without a
  switch (100/100 no-switch lives above 1/2 in blocks 7-11; mean late accuracy .770) and, with a switch, is the
  strongest reviser in the set (late .987, K1 200:0, K2 200:0, G_R5 195/200, REVISION_HISTORY_DEPENDENT). The
  reference, innate_max and jitter also never flip without a switch (100/100 each). A no-switch arm is the control
  that makes this empirical for any searched subject; it costs one lifetime per seed and is descriptive, like
  newlife. AMENDMENT candidate for the repair round.
- The control set (s5 Q-b, Q-c) consists of deterministic policies and the planted reference. It cannot see the
  noise class (B1) or the innate-position dependence (S5, P3), because every registered control's frozen arm is
  itself. Q-c ("memoryless_plus is not REVISION_*") passes while memoryless_plus's noisy twin (jitter) is
  REVISION_*. AMENDMENT candidate: register jitter (Q-d: not REVISION_*) and learns_pre (Q-e: a REVISION_* verdict,
  the lifetime-learned positive) as instrument controls. Under the frozen rule Q-d FAILS and Q-e FAILS; that is the
  point: they cannot be added without the K1 narrowing or the noise-matched comparator.
- E2 (G_PRE reads the frozen arm) survives the suite; witness W2: learns_pre admitted by the original (G_PRE
  200/200) and refused by the mutant (frozen-arm pre-competent lives 0). The suite's smuggler and reference cases
  cannot distinguish the arms because both have frozen pre = full pre. One test for the repair round.

### 4.3 Interpretation

- s1 "revise a lifetime-learned parameter": for the reference the law SIGN is innate (theta0 = +0.2) and the
  first update moves theta to >= .65 (P4), to the clip soon after; innate_max, which cannot learn anything before
  the switch, is behaviourally identical in the late window and gets the same verdict with a STRONGER K2 (155:44 vs
  121:77; my sub-prediction said weaker, because I expected the clipped random walk to leave the boundary faster
  than it does). The one subject whose pre-switch value IS lifetime-learned (learns_pre) is read REVISION_NOT_SHOWN.
  NARROWING: "revise a genome-initialised plastic parameter whose innate value sits on the pre-switch side of the
  law". B2 SURVIVOR; S5 miss.
- s5 "keeps the unrelated competence" (B3, SURVIVOR): synthetic N = 400 with 180 lives at ZERO post-switch role-5
  accuracy passes G_R5 (220 >= 217) and reads REVISION_HISTORY_DEPENDENT; at 184 it does not. The threshold is
  k_pos of a chance-1/2 binomial, which has no meaning for a competence-retention statement. NARROWING: "in
  significantly more than half of the lives". Not blocking: the reference keeps it in 400/400 (development) and
  200/200 here; clock_hybrid in 195/200.
- "Search accessibility: the number of searched subjects per verdict" (s5): 5 of the 8 subjects carry no plastic
  key; for them tape.lifetime draws nothing from the rng (tape.py:305, :313-324, :344), the three arms are the same
  computation, every pair ties, and the verdict is REVISION_NOT_SHOWN or REFUSED_FIXED_PRIOR by construction. The
  count must be reported over the 3 subjects that carry a plastic parameter, and each of those three labels needs
  its frozen-arm and shuffle-arm late accuracies beside it (s4.1). Also worth saying before the run: clock_hybrid
  shows the world rewards a learner poised near its flip point (late .987) far more than the planted reference
  (.634); a searched elite that out-revises the reference is not evidence of anything beyond that.
- "Capacity" and "world demand" (directive s4): capacity holds for the reference (K2). World demand, as the
  preregistration itself says in s11.4, is carried by the four-policy argument plus G_PRE, not by K1; with B1 the
  honest statement is "no deterministic memoryless policy and no law-blind timer can pass G_PRE and the late
  window; a fixed pre-switch prior with perturbation noise passes K1 but not K2".

### 4.4 Edits: what the frozen suite does not pin (behavioural outcomes; hash guard fired on all six)

    E1  Holm bypass (raw p decides)            SURVIVES 19/19   W1: 26:14 of 40, raw .0403, Holm .0807 ->
                                                                NOT_SHOWN (orig) vs NOT_HISTORY_DEPENDENT (mutant)
    E2  G_PRE counts the frozen arm            SURVIVES 19/19   W2: learns_pre G_PRE True -> False, REFUSED
    E3  late window from sw + 2                SURVIVES 19/19   W3: reference life sw 5: c_late 127/128 ->
                                                                163/165, c_early 51/109 -> 15/72
    E4  K1 <-> K2 controls swapped             SURVIVES 19/19   W4: jitter NOT_HISTORY_DEPENDENT (K1 40:0) ->
                                                                NOT_SHOWN (K1 21:19)
    E5  frozen arm plastic (control)           KILLED           test_frozen_reference_scores_zero_late_and_full_pre,
                                                                test_frozen_life_may_not_change_any_parameter
    E6  gates on a simple majority             SURVIVES 19/19   W5: 205/400 REFUSED (orig) -> HISTORY_DEPENDENT

The instrument half of the suite (DeclaredMemory, Endpoint, Subjects) pins what it says it pins (E5 dies on two
tests). The decision rule is exercised only through the development verdicts of the smuggler and the reference,
which are insensitive to all five surviving edits. Five tests for the repair round, each with its witness input
above. Bearing on the run: NONE (freeze check / assay confirm refuse any changed byte).

## 5. Recommendations for the one bounded repair round (owner's, not mine)

1. Wording (s1, s5 table): the narrowings of s4.1-4.3, as a versioned amendment (v1.0.1) before T050 reads a label.
2. Comparator: a noise-matched arm (plasticity on, eta -> 0) beside frozen, or K1 against both; print each
   subject's frozen-arm and shuffle-arm late accuracy with its verdict (the rows already hold them).
3. Controls: register jitter (must not be REVISION_*) and learns_pre (must be REVISION_*) under s5's qualification;
   both fail under the frozen rule, which is why they belong there. Optionally a no-switch descriptive arm (P2).
4. Tests: Holm (E1), G_PRE arm (E2), window (E3), control assignment (E4), threshold (E6); np.isfinite (P1).
5. Family S: declare the family as the subjects with a non-empty plastic key set (3), from genome structure, before
   the run; the five parameter-free subjects are reported, not tested (S2 note).
Then re-freeze, re-check (a small Q3 packet: the five witnesses and B1/S5 re-run against the repaired rule), run.

## 6. Escapes, misses and tooling

6.1 cases.py name collision. The S3 case indexed the observation with `P1`, which the probe function `def P1()` had
rebound. The run stopped after S1 and S2 had written their rows; I renamed the two imports (`P0 as CH_P0, P1 as
CH_P1`) and re-ran S3 onward. Two lines; no prediction, no seed, no case logic touched; `git diff 22bf4ce85 --
cases.py` shows exactly the hunk. S1 and S2 were not re-run (their rows stand).
6.2 Misses: S5's verdict (predicted REVISION_HISTORY_DEPENDENT, observed REVISION_NOT_SHOWN: I did not notice that
the frozen arm of a post-side innate value is the Smuggler); B2's K2-direction sub-prediction (stronger, not weaker);
post-hoc P3's own prediction (K2 101:98, not significant). Each is reported above as what it taught.
6.3 Post-hoc, labelled, unscored: P3 (innate_zero; prediction committed at 96e995a9c before it ran) and P4 (theta
after one update; written and run after the cases; its results.jsonl note says the clip is reached "in one update",
which P4's own numbers show is true only from theta0 = 1.0 -- the correct statement is s4.1's).
6.4 Bytecode hygiene: every subprocess ran with -B after a purge of rso/ensorain's __pycache__; the restored files
were verified by sha256 and `git diff --quiet`, and `freeze check` printed OK after each edit (mutation_rows.jsonl).
6.5 Processes: the case runner (1) and the mutation runner's child (1) overlapped for ~40 s; the runner's parent
only waits. Case CPU about 3 min (S4 84 s); suite 3 s per mutant. No paid compute, nothing on ubu006, no WTP-05
seed.
6.6 Not done: no cascade timer was built (P2 argues it cannot work; the hybrid probe tests the mechanism, not every
construction); the searched subjects were not run in any form; E5's witness not needed. Q3 reviewer time: about 60
min wall from boot to this report (ONBOARDING s8 "Q3 reviewer time").

## 7. Files

    rso/ensorain/challenge/CHALLENGE_SET.md   the set and its predictions (22bf4ce85)
    rso/ensorain/challenge/EXPOSURE.md        what was seen before the set
    rso/ensorain/challenge/expected.json      the answer key
    rso/ensorain/challenge/subjects_c.py      jitter, innate_max, learns_pre, nan_plastic, clock_hybrid, ref_like
    rso/ensorain/challenge/cases.py           S1-S5, B1-B3, P1-P2, REF (two-line fix after the set, s6.1)
    rso/ensorain/challenge/posthoc_p3.py      post-hoc P3 with its prediction (96e995a9c)
    rso/ensorain/challenge/witnesses.py       W1-W5
    rso/ensorain/challenge/edits.json         E1-E6
    rso/ensorain/challenge/run_edits.py       the mutation runner (apply, suite / witness, hash guard, restore)
    rso/ensorain/challenge/results.jsonl      one row per case, plus P3 and P4
    rso/ensorain/challenge/mutation_rows.jsonl baseline, six suite rows, five witness rows
    rso/ensorain/challenge/REPORT.md          this file
