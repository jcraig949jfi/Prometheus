# EXP-04 -- LOCAL SUFFICIENCY: does nonlinear one-step physics, composed, predict usability? (EXPLORATORY; prereg
# 2026-10-08 after G-0007/G-0008, before any surrogate was run on any world)

Question: G-0007 failed on stig (reachability) and cosmos_phase (phase coding). Is the failure the LINEAR composition,
or LOCALITY itself (stationary one-step physics does not determine k-step usability)?

Instrument (sysid_surrogate.py): from at most one controlled step per stationary state (G7, via LocalProbe):
  - a nonlinear one-step model: whitened next full state ~ random ReLU features (width 512, frozen seed) of
    (whitened full state, onehot input symbol), ridge; residual covariance Gaussian;
  - a readout map: whitened readout ~ random features of whitened full state (zero steps);
then COMPOSE by simulation: E = 2000 surrogate episodes of the task (cue, k distractors, query) starting from
stationary states, train a ridge linear decoder of the cue on half, test on the other half -> predicted accuracy.
Prediction with ZERO fitted parameters: USABLE iff predicted excess (acc - 1/V)/(1 - 1/V) >= .10.

Data: every discovery world so far (EXP-01 120, EXP-02 120, EXP-03 60; 5 families), B-accuracy labels (USABLE-B).
These labels were already seen, but the predictor has no label-fitted parameter.

Decisions fixed now (per family; A14 rule: informative = >= 10 per class):
- LOCAL SUFFICIENCY HOLDS for a family if Spearman(predicted, actual B excess) >= .70 and USABLE BA >= .75.
- If it holds on phase and/or stig (where linear composition failed) => the G-0007 failure was LINEARIZATION.
- If it fails on stig AND phase while holding elsewhere => LOCALITY is insufficient there (history-conditioned
  structure), recorded as a property of those mechanisms, not repaired.
- If it fails on rnn/graph/sediment too => INSTRUMENT_DEFECT of the surrogate (it cannot even match linear
  composition), and no physics conclusion is drawn.
