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
