# T25: CSSR causal-state learner (dev, answer-keyed; thread thr-ens-sufficiency-ladder)

Code: `cssr.py`, a CSSR-style learner with no fixed state count, Lmax = 6, alpha = 1e-3, online refit every 500
symbols, KT readout.

Two determinization modes:
- "split" is standard CSSR.
- "vote" is a modal-successor variant added after debugging.

Evaluation: `cssr_eval.py`, eval seeds 1..16, T = 4000, metric = 2nd-half excess log-loss vs exact Bayes (bits/symbol).
Debugging used seeds 1001-1002 ONLY.

## Debug finding (seeds 1001-1002, before the precommitment)

- **split, Even process:** 7 states, excess .033-.039, i.e. no better than the k = 6 window floor (.0315).
  - The step-2 grouping finds the A-type (p ~ .5) and B-type (p = 1) histories correctly.
  - Determinization then splits the A/B loop into a 1-counter. The successor h[1:] + b drops the oldest symbol, so
    the history 011111 + 1 lands in the ambiguous state 111111, and that ambiguity propagates backwards through the
    chain.
  - The tracker therefore loses sync after 6 consecutive 1s. It becomes a window statistic again.
- **vote** gives each (state, symbol) its count-weighted modal successor instead of splitting.
  - Even: 3 states (A, B, a transient 1^6 state), excess .001.
  - W2 order 3: excess .16 and 1.34. The step-2 groups merge contexts with similar P(1) but different successors, so
    voting installs wrong transitions and the tracker locks into a wrong state.

## Precommitment (written BEFORE running cssr_eval.py on seeds 1..16)

Each line names its failure condition.
- P1 split/even: mean excess in [.025, .045] (the collapse to the window floor), AND states >= 5 in >= 14/16 seeds.
- P2 vote/even: mean excess < .005, AND states <= 3 in >= 14/16 seeds.
- P3 golden (both modes): mean excess < .003, AND states = 2 in >= 14/16 seeds.
- P4 split/w2_3: mean excess < .01.
- P5 vote/w2_3: excess > .05 in >= 9/16 seeds (the failure reproduces).
- P6 sns (both modes): mean excess < .01.

## Result (eval seeds 1..16; precommitment commit 482f74a9b; output results/cssr_eval.json)

| mode / world | mean 2nd-half excess | min / max | states per seed |
|---|---|---|---|
| split / even | .0341 | .0291 / .0375 | 7 in all 16 |
| vote / even | .0005 | .0000 / .0014 | 3 in all 16 |
| split / golden | .0004 | -.0006 / .0011 | 2 in all 16 |
| vote / golden | .0004 | -.0006 / .0011 | 2 in all 16 |
| split / w2_3 | .0026 | .0004 / .0053 | 6-20 (true contexts: 8) |
| vote / w2_3 | .3943 | .0053 / 1.2104 | 4-8; 14/16 seeds > .05 |
| split / sns | .0029 | -.0008 / .0060 | 3-7 |
| vote / sns | .0030 | -.0008 / .0063 | 3-5 |

Precommitment:
- P1 SURVIVES (.0341 in [.025, .045]; 16/16 at 7 states).
- P2 SURVIVES (.0005; 16/16 at 3 states).
- P3 SURVIVES.
- P4 SURVIVES (.0026).
- P5 SURVIVES (14/16 > .05).
- P6 SURVIVES (.0029 / .0030).

## Readings

1. **Standard CSSR at finite Lmax does NOT find the Even process's causal state.** It reproduces the window floor
   (.034 vs the exact k = 6 floor .0315).
   - The failure is in determinization, not in the statistics: step 2 grouped the histories correctly on every seed.
   - This is a failure SHAPE: the window's truncation re-enters through the successor map.
   - The 2-state EM-HMM (T25 pilot) reaches .000 on the same world, because its transitions are not built from
     truncated suffixes.
2. **Out-voting the truncated successors recovers the machine exactly** (A, B plus one transient state). But the same
   rule fails catastrophically on Markov order 3, where statistic-merged states are NOT closed under transitions.
   - Neither rule is right across worlds.
   - "Split" is safe but window-bounded. "Vote" is unbounded but unsafe.
3. **The discriminating quantity is the mass of the minority successor.**
   - On Even it is edge noise: only the 1^Lmax suffix, whose mass decays geometrically.
   - On W2 it is structural: a whole merged context.
   - NEXT (not run): a hybrid that splits only when the minority successor carries more than tau of the state's
     transition mass, with a precommitted tau. It should match "vote" on Even and "split" on W2.
4. **Relation to the sufficiency ladder:** "discovering what can be discarded" needs a transition model that is not
   itself a window. A finite-suffix construction (STAT, split-CSSR) pays the window floor on crypticity even when its
   grouping is exact.

## Tick 2026-09-29T04:40Z: "lookahead" successor repair (DEBUG seeds 1001-1002 only; NOT evaluated on eval seeds)

- Rule: keep split determinization, but if the (Lmax+1)-suffix counts reject the truncated successor's group (p <
  alpha_c = .01) while another group fits, redirect the successor to the best-fitting group.
- Debug results (2nd-half excess):

  | world | lookahead | split | vote |
  |---|---|---|---|
  | Even | .0033 / .0132, 12 states | ~.034 | ~.001 |
  | W2_3 | .0362 / .0106 | .0009 / .0033 | - |
  | golden, SNS | unchanged | | |

- Reading: this is the same safety/reach trade as split vs vote, only softened.
  - With about 128 (history, symbol) tests per fit, alpha_c yields about one false redirect per refit on Markov-3.
  - In a hard-tracking machine one wrong transition derails tracking, so its cost has no bound, while the gain from a
    repair is bounded.
  - Local successor repairs to CSSR therefore carry an asymmetric risk.
  - The EM-HMM's soft belief tracking does not have this failure mode.
- Status: kept as mode="lookahead" for the record. NOT promoted, no eval run, and no claim beyond the 2 debug seeds.
- NEXT, the textbook remedy: CSSR is consistent only as Lmax grows with N, and the Even floor decays geometrically in
  Lmax. Test split-CSSR at Lmax in {6, 8, 10} and T in {4000, 16000}, with the predictions precommitted.

## Precommitment: split-CSSR vs Lmax (written BEFORE running cssr_lmax.py)

Setup: eval seeds 1..16, split mode, alpha 1e-3, refit 1000, Lmax in {6, 8, 10}, T in {4000, 16000}, metric =
2nd-half excess. The exact Even window floors are .0315 (L6), .0157 (L8) and .0079 (L10).

- Q1: Even at T = 16000. The mean excess falls monotonically L6 > L8 > L10, and each lies in [floor, floor + .011]:
  L6 in [.031, .042], L8 in [.015, .027], L10 in [.007, .019].
- Q2: Even at T = 4000: L8 mean < L6 mean.
- Q3: Even at T = 16000: states = Lmax + 1 in >= 12/16 seeds for each Lmax (the 1-counter shape).
- Q4: safety. At T = 16000, W2_3 mean excess < .01 and golden mean excess < .003 at every Lmax.

## Result: split-CSSR vs Lmax (precommit commit 1a941aeb2; output results/cssr_lmax.json; 2 min on M2)

Mean 2nd-half excess (16 eval seeds):

| world | T | L6 | L8 | L10 |
|---|---|---|---|---|
| Even | 4000 | .0344 | .0192 | .0220 |
| Even | 16000 | .0316 | .0163 | .0086 |
| Golden | 16000 | .0001 | .0002 | .0002 |
| W2_3 | 4000 | .0027 | .0116 | .0294 |
| W2_3 | 16000 | .0003 | .0023 | .0073 |

- State counts:
  - Even at T = 16000: 7 / 9 / 11 states (= Lmax + 1) in 15 / 14 / 14 of 16 seeds.
  - W2_3 at T = 16000: median ~12 / 40 / 140 states, against 8 true contexts. Split over-fragments as Lmax grows.
- Q1 SURVIVES: monotone, and every value inside its band. Even at T = 16000 sits on the exact window floor
  (.0316 vs .0315, .0163 vs .0157, .0086 vs .0079).
- Q2 SURVIVES (.0192 < .0344).
- Q3 SURVIVES.
- Q4 SURVIVES (W2 .0073 max mean; golden <= .0002).

## Readings

1. **Split-CSSR is exactly a window learner on truncation** (it pays the H(X | last Lmax) floor to 3 decimals). But it
   is NOT one on estimation: its states pool the counts.
   - At T = 16000, CSSR L10 reaches .0086. The best window statistic reaches .0358 (STAT k8, optimum_vs_T.txt; a
     different generator, 16-seed means).
   - That is ~4x lower excess, with 11 states instead of 256 contexts.
   - So "discover the partition" buys the estimation half of the bias-variance trade, not the truncation half.
2. **The same data-dependent interior optimum reappears in Lmax.** At T = 4000, L10 is worse than L8 on Even (.0220 vs
   .0192), and on W2 the error grows with Lmax (.0027 -> .0294) through over-fragmentation. CSSR's consistency needs
   Lmax to grow slowly with N, which is the textbook condition, now measured.
3. **Where the truncation half goes:** only a transition model not built from suffixes pays neither half. The 2-state
   EM-HMM reaches .000 but needs S fixed in advance. "Vote" reaches .0005 but is unsafe on Markov-3.
   - Open design question: a learner with no fixed S that pays neither half on this ladder.
   - Candidates: soft belief-state tracking over CSSR-proposed states (EM refinement initialized from the split
     machine), or state merging by future-distribution equivalence (bisimulation-style) instead of suffix splitting.

## Tick 2026-09-29T05:15Z: EM refinement from the split-CSSR machine (cssr_em.py)

Debug, on seeds 1001-1002 only:
- **10 EM iterations:** Even .028 / .032 (barely off the window floor).
- **50 iterations:** Even .0011 / .0018.
  - At 200 iterations the final-fit log-loss is .6721 / .6656, vs Bayes .6726 / .6664.
  - So the stall was SLOW CONVERGENCE, not a local optimum. EM does leave the 1-counter basin.
- **50 iterations on W2_3:** .0102 / .0464 (split: .0009 / .0033). EM overfits the over-split machine: 12-17 soft
  states is several hundred free parameters on 4000 symbols. Golden and SNS are fine.
- **Remedy with a guarantee:** the prequential Bayes mixture of split and EM. Its total log-loss is <= the better
  learner's + 1 bit, by construction.

## Precommitment (written BEFORE running cssr_em_eval.py; eval seeds 1..16, T = 4000)

- E1: CSSR_EM on Even, mean 2nd-half excess < .005.
- E2 (failure reproduces): CSSR_EM on W2_3, mean excess > .01.
- E3: on every world, the MIX mean excess is <= min(split mean, EM mean) + .002.
- E4: MIX on Even < .006 AND MIX on W2_3 < .006 (one learner, with no fixed S, safe on both).
