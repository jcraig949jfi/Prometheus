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
