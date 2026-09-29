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
