# DESIGN_C0 -- Ares cycle-0 sweep, preregistered

Currency: 2026-09-19. Ares. This file is committed BEFORE the first
sweep result (the git history is the order). Anything changed after a
result is seen goes in a dated ADDENDUM at the bottom, never in the
body. Post-hoc variants are separate configs labelled EXPLORATORY.

## 1. What is being tested

The charter's hypothesis, in operational form: an ABSTRACT PRESSURE in
the world -- and nothing in the objective or the substrate -- changes
the KIND of machinery a dumb search finds. Fitness is world reward
only. For each world the three modes present / absent / shuffled are
run with identical substrate, search and seeds; the comparison is
between modes, never against a target architecture.

## 2. Fixed apparatus (hashes in every run receipt)

- Substrate: ares/substrate.py. Default Config: 8 hidden slots, 2 ticks
  per world step, topology mutation on, keep on, plasticity on (rate 0
  until mutated). Ops: ADD MUL MAX MIN THRESH GATE TANH DIFF CONST.
  Inputs 6 (ch4 = clock, ch5 = 1), outputs 3, action = argmax.
- Search: ares/search.py `run`: P=128, G=120, 4 training episodes per
  generation with fresh seeds, elites 16, tournament 3 among the top
  half, 1+Poisson(1) mutations per child. Held-out evaluation: 32
  episodes with seeds balanced on the first binary draw (search.py
  `_balanced_eval_seeds`).
- Seeds: 1, 2, 3 per cell. Eligible count per world-mode cell = 3.
- Worlds: ares/worlds.py W1 W2 W3 W4 W5 W7 W11 W12 (+ W6 = W3 under
  scarce/abundant configs; W9 two-sided coevolution; W10 developmental
  encoding on W4 and W3; W8 transplant protocol).
- Baselines: ares/runs/baselines.json (fixed policies, random policy,
  gen-0 population), computed 2026-09-19 before this file.

## 3. Floors and thresholds (from baselines.json, 32 balanced held-out eps)

    world  mode      best_fixed  attainable(pre-estimate)  threshold
    W1     present     0.00        ~27                       5.4
    W1     absent      0.00        ~27                       5.4
    W1     shuffled    0.00        ~27                       5.4
    W2     present    60.00        ~195                     87.0
    W2     absent     60.00         60 (nothing above safe)  60.0 (cannot exceed)
    W2     shuffled   60.00         60                       60.0 (cannot exceed)
    W3     present     1.50        ~58                      12.8
    W3     absent      2.69        ~60                      14.2
    W3     shuffled    1.50         ~2 (unlearnable)         1.5 (cannot exceed)
    W4     present     0.00        ~40                       8.0
    W4     absent      0.00        ~40                       8.0
    W4     shuffled    0.00          0                       0.0 (cannot exceed)
    W5     present     0.00        ~50                      10.0
    W5     absent      0.00        ~50                      10.0
    W5     shuffled    0.00          0                       0.0 (cannot exceed)
    W7     present    49.50        ~90                      57.6
    W7     absent     40.50        ~60                      44.4
    W7     shuffled   48.38        ~55                      49.7
    W11    present     0.00        ~50                      10.0
    W11    absent      0.00        ~56                      11.2
    W11    shuffled    0.00          0                       0.0 (cannot exceed)
    W12    present    19.00        ~80 (lifetime cap)       31.2
    W12    absent     80.00         80 (cap)                80.0 (at cap)
    W12    shuffled   19.00        ~25 (no state visible)   20.2

threshold = best_fixed + 0.2 * (attainable - best_fixed). "attainable"
is an analytic PRE-ESTIMATE, not a measurement; where the mode cannot
exceed its floor by construction the threshold is the floor and the
cell is INDETERMINATE for the fitness question (it still supplies a
structural control). The first baselines run (16 seeds, 2026-09-19
12:xx UTC) gave a fixed policy 10.0 on W4 by regime imbalance; the
held-out set was rebuilt balanced (32 seeds) BEFORE this file was
committed and before any sweep cell ran; the numbers above are from the
balanced set. Gen-0 random organisms already reach 140 on W2 present
(and 60 on W2 shuffled): conditional risk on W2 is one edge away from
random, which prediction P-W2 accounts for.

## 4. Preregistered outcome rule per world (applied at summary)

A pressure is scored MATERIAL for a world only if ALL of:
  (i)   present-mode champion held-out >= threshold in >= 2 of 3 seeds;
  (ii)  the world's conditional-behaviour statistic (below) differs
        between present and shuffled champions in the preregistered
        direction in >= 2 of 3 seeds;
  (iii) the present champion has at least one LOAD-BEARING hidden node
        (ablation delta <= -25% of (base - floor)) in >= 2 of 3 seeds,
        i.e. the behaviour is localisable, not a direct input-output
        reflex.
DID NOTHING: (i) fails (search finds nothing above threshold) with the
  absent-mode champion above its own threshold (the task is learnable,
  the pressure was not answered).
MERELY HARDER: (i) fails AND absent is also below threshold, OR (i)
  holds but (iii) fails and the structural profile of present champions
  matches absent/shuffled champions (same op histogram class, same
  n_keep/n_cyclic bands).
INDETERMINATE: 1 of 3 seeds, or thresholds not computable.

Conditional statistics (ares/sweep.py behaviour_probe) and directions:
  W1  p_act_danger < p_act_nodanger by >= 0.2 (present); no such gap in
      shuffled (cue uninformative there).
  W2  p_risky_window - p_risky_nowindow >= 0.4 (present); shuffled ~0.
  W3  acc_post (after flip+5) >= 0.6 while acc_pre >= 0.6 (present);
      shuffled cannot; absent has no post period (N/A).
  W4  acc_late >= 0.65 (present); shuffled ~0.5; also acc_late_r0 and
      acc_late_r1 BOTH >= 0.55 (not a fixed policy).
  W5  dec_acc >= 0.7 with dec_acc_pos and dec_acc_neg both >= 0.55.
  W7  score_A >= 1.0 AND score_B >= 0.8 (both regimes handled); the
      ablation profile has at least one node whose removal cuts score_A
      by >= 0.3 while score_B stays within 0.2, or vice versa
      (separable). No MoE-ness measure exists or will be added.
  W11 mean_commit_step >= 2 AND commit_acc >= 0.7 (present); absent has
      no commit (N/A); shuffled commit_acc ~0.5.
  W12 p_risky_by_energy is strictly higher in the lowest non-empty bin
      than in the highest non-empty bin by >= 0.3 (present); absent and
      shuffled flat (difference < 0.15).

## 5. Secondary, descriptive, NOT claims

Structure (n_hidden, n_edges, n_keep, n_cyclic, n_gate_like,
n_plastic, op_hist), diversity (struct_div, behav_div), mutation
survival, adaptation speed (first logged generation at or above the
threshold), transfer matrix, W8 retention, W9 cycle autocorrelation,
W10 generations-to-threshold vs direct. With 3 seeds per cell NO
structural difference between modes is claimed as a finding this
cycle; it is reported as "observed in k of 3" with the direction, and
the winners are rerun at 10 seeds in cycle 1 before any such claim.

## 6. Predictions (each can lose)

  P-W1  MATERIAL in >= 2/3 (a gate on ch1 will be load-bearing).
  P-W2  MATERIAL in 3/3; the ablation will localise to one THRESH/GATE/
        MUL node reading ch1. RISK: a gen-0 organism already scored 114,
        so (iii) may fail (the reflex is a direct edge, not a node) --
        that is a legitimate "no hidden machinery needed" outcome.
  P-W3  MERELY HARDER or INDETERMINATE: a reflex on last reward (ch2)
        and last action (ch3) can recover in one step with no hidden
        node; acc_post will be reached without a load-bearing node.
  P-W4  MATERIAL in >= 1/3, INDETERMINATE overall: a self-loop or high-
        keep node is needed and search at G=120 may not find it.
  P-W5  DID NOTHING (dec_acc at chance in 3/3): 26-step delay through
        distractor is beyond this substrate at this budget.
  P-W6  scarce champions reach a LOWER held-out than abundant in 3/3;
        scarce champions have >= 1 load-bearing node in >= 2/3 (no room
        for redundancy); no motif claim.
  P-W7  score_B is solved (option 0) in 3/3; score_A stays near the
        fixed floor (0.67) in >= 2/3; separability fails: MERELY HARDER.
  P-W8  evolved-subgraph retention does NOT exceed random-subgraph
        retention (difference < 0.1) in every pair (null expected).
  P-W9  choice autocorrelation lag1 > 0.5 in present (cycling); present
        champions' n_cyclic not larger than absent's: Red Queen null.
  P-W10 developmental encoding reaches threshold no faster than direct
        on either world (null expected).
  P-W11 mean_commit_step < 2 in 3/3 (immediate commitment): DID NOTHING
        or MERELY HARDER.
  P-W12 MATERIAL in >= 2/3: the energy channel is visible and a
        threshold on it is one node.
  P-ARM the nostate arm loses on W4 (held-out lower than default in
        3/3) and is indistinguishable on W2, W3, W12.
Overall prior: 3-4 of 12 MATERIAL, most of the rest DID NOTHING or
MERELY HARDER; 0 mechanisms that fail to map onto a threshold, a gate
or a carrier. The interesting outcome is anything outside that.

## 7. What would make me stop

If no world scores MATERIAL with a load-bearing node, the substrate
cannot host the question at this budget and cycle 1 is a substrate
question, not a pressure question. If every MATERIAL world's mechanism
is a single threshold node on the cue channel, pressure engineering
has (so far) only produced reflexes and the report says so.

## ADDENDA (dated, appended only)

ADDENDUM 1 (2026-09-19 12:50 UTC, written after the first 18 cells
had run, before any dissection). The W2 shuffled floor "60.0 (cannot
exceed)" in s3 is WRONG: W2 windows persist ~2 steps (p_off 0.5) and
the last-reward channel (ch2) shows +60 on the step after a paying
risky action, so the policy "risky iff last reward was +60" exploits
window persistence with no cue. Observed: shuffled champions 75.34 and
80.34 (seeds 1, 3), 60.00 (seed 2). Consequences: (a) the W2 present-vs-
shuffled comparison in rule (ii) is still valid (p_risky_window -
p_risky_nowindow is computed against the TRUE window, and the shuffled
reflex can only fire on the second step of a window), but the shuffled
cell is no longer a "no structure" control; it is a "structure only
via reward feedback" control. (b) The same leak exists in principle in
W1 (danger persists ~3 steps; a catastrophe shows on ch2 as a large
negative) and is weaker there because catastrophes are rare and
abstaining after one is cheap. Recorded in roles/Ares/calibration/
LEDGER.md. No threshold is moved; the report labels the W2 shuffled
cell accordingly.
