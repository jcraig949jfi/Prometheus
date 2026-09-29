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

## Circularity check: cross-family estimators (crypt_crossfamily.py)

Estimators:
- (a) D6 from a fixed-S = 8 HMM, EM from random restarts. It uses no CSSR proposal.
- (b) A model-free D_seq: STAT6 minus the best of STAT8/10/12 on the 2nd half.

### Precommitment (written BEFORE running crypt_crossfamily.py)

- X1: Spearman(HMM8 D6, true D6) > .8.
- X2: Spearman(D_seq, STAT6 - MIX3_FS at T = 16000) > .5. Weaker, because estimation cost confounds D_seq.
- X3: Spearman(HMM8 D6, STAT6 - MIX3_FS at T = 16000) > .7.
- If X1 and X3 hold, the moderator result is not an artefact of scoring the learner with its own model family.

### Result (precommit commit f5eb1437a; output results/crypt_crossfamily.json; 97 s on M2)

- X1 REFUTED: Spearman(HMM8 D6, true D6) = .695 < .8.
- X2 REFUTED: Spearman(D_seq, gap16) = .419 < .5.
- X3 SURVIVES, barely: Spearman(HMM8 D6, gap16) = .709 > .7.

Failure shape (this is the finding):
- The random-restart HMM8 reports D6 ~ 0 where the true D6 is ~.05: U4_s1 .0036 vs .052; U4_s2 .0025 vs .082; U4_s8
  .0002 vs .046; U5_s2 .0001 vs .055.
- These are EXACTLY the four worlds where random-init EM failed catastrophically in the Q2 ablation (T25). A model
  that did not learn the hidden structure cannot see the crypticity it failed to learn.
- So a learned D_k is FAILURE-SILENT, and it errs toward "the window is sufficient". That is the dangerous direction:
  it would steer LM02 toward retention exactly where discovery was needed but failed.
- D_seq is mostly NEGATIVE at T = 4000: longer windows' estimation cost dominates their truncation gain. It is not a
  usable crypticity proxy at this sample size.
- CSSR_EM's learned D6 (rho .946 in C1) was good because CSSR_EM rarely fails catastrophically (the Q2 insurance
  result). Its apparent reliability is inherited from the learner, not intrinsic to D6.

Consequence for LM02 (design rule, to be precommitted):
- A learned D_k is admissible only behind a MODEL-QUALITY GATE: the model's held-out log-loss must beat STAT_k's.
  Otherwise D_k is reported as UNKNOWN, never as 0.
- Whether such a gate catches these four failures has not been tested. It is the next check.

## Model-quality gate test (crypt_gate.py)

- Fit on the first half, evaluate on the second. The gate passes iff the model's 2nd-half log-loss < STAT6's.
- Silent failure := true D6 > .02 and learned D6 < true D6 / 3, recomputed on this run with first-half fits.
- The precommitted subject is HMM8. CSSR_EM is shown for comparison only.

### Precommitment (written BEFORE running crypt_gate.py)

- K1: the gate rejects >= 80% of HMM8's silent failures. If there are none, K1 is vacuous and reported as such.
- K2: among HMM8 gate-passing worlds, Spearman(D6, true D6) > .8.
- K3: the gate passes >= 12/24 worlds for HMM8, i.e. it is not rejecting everything.

### Result (precommit commit 6c3723bcc; output results/crypt_gate.json; 69 s on M2)

HMM8 (precommitted subject):
- silent failures: U3_s4, U4_s1, U4_s2, U4_s8, U5_s1, U5_s2, U5_s3 (7);
- caught by the gate: 5/7;
- gate-passing worlds: 12/24;
- gated Spearman(D6, true D6) = .900.

| prediction | result |
|---|---|
| K1: gate catches >= 80% of silent failures | REFUTED (5/7 = 71%) |
| K2: gated Spearman > .8 | SURVIVES (.900) |
| K3: gate passes >= 12/24 | SURVIVES, exactly at the threshold (12/24) |

CSSR_EM (comparison only, no prediction): 2 silent failures (U5_s1, U5_s3), 1 caught; 16/24 pass; gated Spearman .898.

Failure shape of K1:
- The gate catches CATASTROPHIC failures: a model worse than the window, e.g. U4_s1 .931 vs STAT6 .866.
- It misses PARTIAL failures, where the model beats the window but has learned only part of the hidden structure:
  - U3_s4: HMM8 .3849 < STAT6 .3896, D6 .0019 vs true .0272;
  - U5_s3: .5344 < .5429, D6 .0112 vs true .0531.
- The gate also rejects the window-sufficient worlds, where the model ties or loses slightly to STAT6 (U3_s7, U4_s7,
  U5_s5). So it discards exactly the "window sufficient" evidence, and those worlds come out UNKNOWN.

Consequence for LM02 (revises the design rule):
- A gated learned D_k is a LOWER BOUND on crypticity. A pass means "at least this cryptic", never "no more".
- A learned D_k can therefore support "discovery should win here" (large gated D_k). It can never support "the window
  suffices here" (small D_k), because a small value is indistinguishable from partial learning.
- A "window sufficient" claim needs a different kind of evidence: e.g. a longer-window model that fails to beat STAT_k
  despite ample data (a power argument), not a small learned D_k.
