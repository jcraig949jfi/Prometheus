# Learned crypticity estimate (LM02 open question; thread thr-ens-sufficiency-ladder; dev, answer-keyed)

- Question: LM02 worlds have no answer key. Can a learned model estimate how much a bounded window of retained records
  leaves unresolved (T25's moderator)?
- Measure D6: the model's own log-loss cost of predicting from the last 6 symbols instead of the full past. It is
  invariant to redundant or split states, unlike raw state entropy.
- Learned model: the CSSR_EM fit on the whole T = 4000 stream. True model: the generating machine.
- Worlds: the 24 held-out unifilar worlds. Script: crypt_learned.py.

## Precommitment (written BEFORE running crypt_learned.py)

- C1: Spearman(learned D6, true D6) > .8 across the 24 worlds.
- C2: learned D6 < .005 on both window-sufficient worlds (U3_s7, U4_s7; H6 ~ 0).
- C3 (sanity check that the two exact crypticity measures agree): Spearman(true D6, H6) > .8.

## Result (precommit commit e0a67493c; output results/crypt_learned.json; 37 s on M2)

- C1 SURVIVES: Spearman(learned D6, true D6) = .946.
  - The largest misses are where the learner failed to learn the structure at T = 4000: U5_s3 (true .0531, learned
    .0253) and U3_s6 (.0075 vs .0021).
  - A wrong model UNDER-estimates crypticity.
- C2 SURVIVES: learned D6 is .0000 (U3_s7) and .0001 (U4_s7).
- C3 REFUTED: Spearman(true D6, H6) = .721 < .8.
  - Shape: H6 (state entropy) over-counts ambiguity between states that predict almost alike. U5_s5 has H6 = .96 bits
    but true D6 = .0045, with a state gap of .0007.
  - That is exactly the unexplained G4 exception at T = 16000 (T25).

## Exploratory (NOT precommitted): which measure predicts the gain from discovered compression?

Spearman with (STAT6 - MIX3_FS) at T = 16000, over 24 worlds:

| true D6 | learned D6 | H6 |
|---|---|---|
| .922 | .910 | .606 |

Reading:
- The PREDICTIVE window cost D6 is the right moderator, not the state entropy H6.
- The learned estimate, which needs no answer key, is almost as good as the true one.
- This carries into LM02 as a PREDICTION to be precommitted before any LM02 run: the gain of discovered over retained
  compression rank-correlates with learned D6.
- Caveat: the learned D6 comes from the same CSSR_EM family whose gain it predicts. A learned-D6 measure from a
  different model family is needed to rule out circularity.
