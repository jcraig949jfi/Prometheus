+==============================================================================================================+
| REVIEW PACKET: T25 -- DOES A LEARNER WITH NO FIXED STATE COUNT DISCOVER WHAT CAN BE DISCARDED?               |
| Author: Ensorain (M2, seat m2-32b65655)   Date: 2026-09-29                                                   |
| For: HITL operator + external reviewers   Status: DEV, answer-keyed, per-tick precommitments (not a prereg)   |
| Self-contained: every load-bearing number is inline. No repo access is needed.                              |
+==============================================================================================================+

-----
0. SUMMARY AND VERDICT
-----
Question (ARC3 thread "sufficiency ladder"): the right compression of a sequence is its causal state, the minimal
sufficient statistic of the past for the future. Can a learner that is NOT told the number of states find it? And
does finding it beat keeping a fixed window of raw history?

Verdict, in three parts:
(a) A three-stage learner does it on a 4-world answer-keyed ladder, 14/14 precommitted predictions surviving:
    - a statistical partition proposal (CSSR);
    - likelihood refinement (EM);
    - a prequential arbiter (a mixture).
(b) On 24 HELD-OUT random 3-5 state machines, precommitted:
    - the RANKING generalizes (learner < window statistics);
    - the ABSOLUTE LEVEL at T = 4000 does NOT: 2 of 6 predictions were refuted.
    The shortfall is data-limited: the 4 worst worlds fall more than 2x by T = 16000, while the window statistic is flat.
(c) Claim ceiling: the learner is a better "hypothesis-locus" compressor than window statistics, and its excess over
    the causal-state oracle falls with data. It is NOT shown to be a general causal-state discoverer at small T.
    Where it needs more data is predicted by window crypticity (rho = .58).

-----
1. WHAT WAS BUILT (all pure Python + numpy, M2, seconds to minutes per run)
-----
- Worlds, each with an EXACT Bayes predictor as the answer key:
  - Even process (2 causal states, infinite Markov order);
  - golden mean (order-1 control);
  - order-3 Markov with random Beta(.5, .5) rows (W2_3);
  - simple nonunifilar source (SNS, infinitely many causal states);
  - a held-out sampler of random binary unifilar machines (S = 3, 4, 5; resampled until strongly connected).
- Learners:
  - STAT(k): order-k context counts, KT readout; the window baseline.
  - CSSR "split": standard Shalizi-Klinkner CSSR, Lmax = 6, alpha = 1e-3, online refit.
  - CSSR "vote" and "lookahead": two successor-repair variants, both recorded as negatives.
  - CSSR_EM: Baum-Welch initialized from the split-CSSR machine, eps = .01 smoothing, 50 iterations.
  - MIX: two-expert Bayes mixture of split and EM. MIX_FS: fixed-share, rate 1e-3.
- Metric: 2nd-half excess log-loss vs the exact Bayes predictor, in bits/symbol. 16 eval seeds per ladder world.
- Protocol: debug on seeds 1001-1002 only. The predictions (with failure conditions) were committed to git BEFORE
  each eval run.

-----
2. RESULTS ON THE 4-WORLD LADDER (eval seeds 1..16, T = 4000)
-----
                      Even     golden    W2_3     SNS
  split-CSSR          .0344    .0005     .0027    .0038     (Even: 7 states in 16/16 seeds)
  vote                .0005    .0004     .3943    .0030     (W2_3: 14/16 seeds > .05)
  CSSR_EM (50 it)     .0011    .0003     .0160    .0029
  MIX (split, EM)     .0024    .0004     .0029    .0030
  window reference: exact H(X | last 6) - 2/3 on Even = .0315; best STAT on Even at T = 16000 is .0358 (k = 8)

Failure shapes:
- split on Even: the grouping step is CORRECT on every seed. Determinization then rebuilds the window, because the
  successor suffix drops its oldest symbol. The tracker desynchronizes after 6 consecutive 1s and pays exactly the
  window floor.
- vote on W2_3: statistic-merged states are not closed under transitions. Voted transitions lock the tracker into a
  wrong state.
- lookahead (debug only): ~1 false redirect per refit on W2_3. One wrong transition derails hard tracking, so its
  cost has no bound, while the gain from a repair is bounded.
- EM (10 iterations): stalled at .028-.032. Diagnosis: slow convergence, not a local optimum. At 200 iterations the
  fit log-loss is .6721 vs Bayes .6726.
- EM on W2_3: overfit. The 12-20 over-split states give it hundreds of free parameters on 4000 symbols.

Lmax sweep (split, eval seeds, 4/4 precommitted predictions survived):
  Even, T = 16000:  L6 .0316  L8 .0163  L10 .0086   vs exact window floors .0315 / .0157 / .0079
  Even, T = 4000:   L6 .0344  L8 .0192  L10 .0220   (an interior optimum again)
  W2_3, T = 16000:  L6 .0003  L8 .0023  L10 .0073   (states: 12 / 40 / 140 against 8 true contexts)
Reading: split-CSSR pays EXACTLY the window's truncation floor, but pools estimation. At L10 it reaches .0086 against
the best window statistic's .0358, with 11 states instead of 256 contexts.

-----
3. HELD-OUT FAMILY (24 random unifilar worlds, T = 4000; H1-H6 precommitted)
-----
  family means:  STAT3 .0674  STAT6 .0372  split .0399  EM .0219  MIX .0231  MIX_FS .0171
  H1 REFUTED  MIX <= min(split, EM) + .002 held in only 18/24 worlds (<= 2 misses allowed; 6 misses).
              Shape: Bayes-mixture LOCK-IN on the early leader. E.g. U4_s6: MIX = split = .0772, EM = .0256.
  H2 REFUTED  MIX mean .0231 vs predicted < .015. That is 5-7x the ~.003 parametric cost of an exact-structure learner.
  H3 survives MIX < best STAT (.0231 < .0372).   H4 survives EM < split.
  H5 survives MIX_FS on Even: mean .0018, max .0040 (plain MIX: max .0327).   H6 survives MIX_FS <= MIX + .001.

Diagnosis (D1, D2 precommitted; both survived):
  D1  Spearman(H6, MIX_FS excess) = .583 (p = .003). H6 = causal-state entropy given the last 6 symbols.
      Competitors: gap between states .35, rarest-state probability .40, state count .17.
  D2  the 4 worst worlds at T = 16000:
        U4_s3 .0612 -> .0047    U5_s3 .0525 -> .0110    U5_s1 .0271 -> .0060    U5_s2 .0248 -> .0033
      STAT6 at T = 16000 stays at .021-.073.

-----
4. INDEPENDENT REPLICATION OF THE PARENT PILOT (Fabric tsk-ba120344aa29)
-----
A Fabric worker (ubu002, fresh context, spec only) reimplemented the sufficiency-ladder claims C1-C4 in pure stdlib.
All were CONFIRMED:
- STAT(3) = Bayes on order-3 Markov;
- over-order costs .0044 / .0187 / .0435;
- Even interior optimum at k = 6;
- Even Bayes loss -> 2/3.
Caveat: the worker's executor cannot run code, so its unmodified script was executed on M2. The implementation is
independent; the execution is not. It also supplied the exact Even truncation floor used above; verified by
enumeration.

-----
5. WHAT THIS DOES AND DOES NOT ESTABLISH
-----
DOES:
- On answer-keyed worlds, "discovering what can be discarded" (a learned state partition) beats "keeping a window"
  in excess vs the oracle. It decomposes cleanly: truncation floor + estimation cost. Window statistics pay both.
  Split-CSSR pays only the floor. EM plus mixing pays neither on the ladder.
- The learner's residual gap on random machines shrinks with data (4/4 worst worlds). The window's gap does not.
- The failure shapes of each single stage are reproducible and mechanistic (Section 2).
DOES NOT:
- Any claim at T = 4000 about random machines at the parametric floor (H2 refuted).
- Any statement about the 20 non-worst held-out worlds at T = 16000 (not run).
- Anything beyond binary alphabets, one alpha, and one eps; or anything preregistered. These are per-tick
  precommitments by the same author who built the learners.
- Anything about WTP-LM01 (frozen, not launched, untouched by this work).

-----
6. INCIDENTS AND PROCESS HOLES
-----
- The Fabric task was mis-specified by the author: a code-execution replica was sent to the claude executor, which has
  no python by design. It was recorded in the migration report; the next such task uses the script executor.
- heldout_eval.py lacked a __main__ guard, so importing it re-ran the family evaluation. The rerun was deterministic and
  identical. Fixed.
- The two mixture implementations differ: the first used clipped cumulative loss, the second the exact sequential
  posterior. That explains MIX on Even .0024 / .0215 vs .0031 / .0327. Both are disclosed.
- Debug-seed discipline held throughout. But the design iterations (vote, lookahead, EM iteration count) were chosen
  after seeing debug-seed behaviour on the SAME world types used for eval. Only the random family is truly held-out.

-----
7. DECISION / RECOMMENDATION (HITL's call)
-----
Ensorain's lean: continue T25 at low cost, as dev work, then fold it into the LM02 design as the "hypothesis-locus"
arm.
Next steps, none needing a campaign or lease:
- run the 24-world family at T = 16000 as a Fabric script-executor Task, with a precommitted prediction that the family
  mean falls below .008;
- precommit MIX_FS as the default arbiter.
"Stop" is a legitimate answer: the causal-state literature (Shalizi-Klinkner; Still-Crutchfield) already predicts
most of Section 2. What is new here is the measured two-halves decomposition and the failure shapes, not a new
algorithm.

-----
8. QUESTIONS FOR THE REVIEWER (written to resist agreement)
-----
Q1  The oracle for the random family KNOWS the parameters, while W2's oracle is a posterior. Is comparing excess
    across the two families meaningful, or should every family use a Bayesian-mixture oracle?
Q2  Is "EM initialized from CSSR" just a good HMM initialization, making the CSSR stage incidental? The test would be
    EM from random restarts with S = CSSR's count. It was NOT run.
Q3  H6 is computed at Lmax = 6, the learner's own window. Does rho = .58 just restate that the learner is
    window-bounded, rather than explain anything?
Q4  Is fixed-share's win (.0171 < per-world best .0189) evidence of mid-stream switching, or of variance reduction
    by averaging two models? The two are not separated here.
Q5  Would a reviewer accept "ranking generalizes, level does not" as a positive result, or is it a negative dressed
    as one?

-----
9. ARTIFACTS (branch ensorain/base-role-adopt-2026-09-23 on origin)
-----
- ensorain/arc3/suff/CSSR_T25.md: the full log, including every precommitment and its commit.
- Precommitment commits: 482f74a9b (split/vote), 1a941aeb2 (Lmax), d0d52f531 (EM + mixture), f57504071 (held-out
  family), 5d5678427 (diagnosis). Results commits: 0d2abaf63, de8ab41e1, 03bb7f32f, 91152a674, 36b8d0756.
- Code: ensorain/arc3/suff/cssr.py, cssr_em.py, worlds_unifilar.py, cssr_eval.py, cssr_lmax.py, cssr_em_eval.py,
  heldout_eval.py, heldout_diag.py.
- Results: ensorain/arc3/suff/results/cssr_eval.json, cssr_lmax.json, cssr_em_eval.json, heldout_eval.json,
  heldout_diag.json.
- Replication: ensorain/arc3/suff/replication/README.md (Fabric tsk-ba120344aa29, att-32409eb521dc).

+==============================================================================================================+
| END. "Not worth continuing" is a first-class answer: say so if Sections 5 and 7 do not justify another tick.  |
+==============================================================================================================+

ADDENDUM 2026-09-29T10:20Z (process hole, Section 6):
- The results/*.json files listed in Section 9 were gitignored (`**/results/`) and were NOT on origin when this packet
  was pushed. They are force-added in the commit that adds this addendum.
- The quoted numbers are unchanged (the runs are deterministic and were cross-reproduced).
