# C3 Session 1 -- PREREGISTRATION of the visible-family law search

Written 2026-09-24 ~07:30Z, after the P1/P2 gate (v3 PASS) and the substrate smoke run, BEFORE any
map data. Certificate v3 (S1_PREREG_P1P2_GATE.md A2) is the phenomenon instrument throughout.

## 1. Target phenomenon
Per world (family, native parameters, delay k): the certificate class NONE / PASSIVE / FUNCTIONAL
(INDETERMINATE worlds are reported and excluded from fitting, never relabelled). Primary binary target:
FUNCTIONAL vs not. Secondary: PASSIVE vs NONE among non-FUNCTIONAL worlds. P3 (advantage) is NOT
studied (directive s13; design 03 s2).

## 2. Candidate coordinates (constructed by Cosmos; firewall: no substrate declares any)
One GENERIC protocol, identical for every family, using only the interface (rollout, full_state,
readout_features, paired CRN episodes). No decoder, no task labels beyond "the first observation
differs":
  d_sig(t)   mean distance between two trajectories that share every noise draw and every later
             observation but differ in the first observation (the cue)
  d_noise(t) mean distance between two trajectories with the same first observation and independent noise
  measured in two VIEWS: F = full causal state, R = the readout's input (readout_features);
  distances: Euclidean on each view's vector, each view standardised by its per-component SD over all
  recorded states (unit-free; binary and continuous states comparable).
Coordinates at the query time q = k+1 (dimensionless):
  sR = d_sig^R(q) / (d_noise^R(q) + d_sig^R(q))   in [0,1]: history signal share in the readout view
  sF = the same in the full view
  rR = d_sig^R(q) / d_sig^R(1)                     retention of the readout-view signal since t = 1
  rF = the same in the full view
  kq = k + 1 (the delay; a task parameter, not a substrate declaration)
The coordinates exist for any substrate that implements the interface (D/E authors included) without
the author saying what they mean.

## 3. Data
Worlds per family drawn uniformly from native lattices (seed 20260924):
  rnn   rho {0, .3, .6, .8, .9, .95, 1.0, 1.1}, a {.2, .5, 1}, sigma {.01, .1, .3, 1}
  graph K {1, 2, 3, 4, 6}, b {-1, -.5, 0, .5}, p {0, .01, .03, .1}
  stig  delta {.02, .1, .3, .6}, D {0, .1, .3}, v {0, 1, 2}, j {0, .1, .3}
  delay k in {2, 4, 8} for every family.
40 worlds per family (120), certificate v3 (3,000 test episodes, 49 permutations), coordinates from
400 paired episodes. Plus the hybrid H at its 4 switch settings x 3 delays (substitution map; not used
for fitting).

## 4. Mining and gates
Miner: the C0 grammar and LOLO machinery over terminals {sR, sF, rR, rF, kq} (families = lineages;
AST lineage audit: A/B/C independent), 19-permutation whole-search null, one or two atoms.
L1 (law exists): CANDIDATE with worst-family LOLO BA >= 0.80 and null p <= 0.05.
L2 (beats simple baselines): LOLO BA >= that of (a) a single-coordinate threshold on sF alone,
    (b) the native-parameter-free constant, (c) a 5-NN on the coordinates -- 0.03 margin over (a).
L3 (family residual, per family, NOT pooled): per-family BA >= 0.75 for every family.
L4 (substitution): the law, fitted on A/B/C, classifies the hybrid's 12 worlds with >= 10/12 correct.
L5 (adversarial): >= 30 fresh worlds per family chosen near the law's boundary and at lattice extremes;
    kill if confirmed misclassifications (confirmed = replicate certificate agrees) exceed 10% of the
    law's confident predictions (confidence >= 0.9), or if any single family exceeds 20%.
Session 1 ends with a PRELIMINARY candidate law (or NONE), not a frozen one; freezing for D happens
after the Harmonia coordinate audit (directive s10) in a later step.

## 5. Precommitments written to be lost
Q1 A law exists and its core is a readout-view signal share: FUNCTIONAL iff sR above a threshold. 0.5
Q2 PASSIVE worlds are exactly those with high sF and low sR (a two-coordinate PASSIVE rule).        0.5
Q3 The stig family is the hardest (its signal lives in a sparse field channel that Euclidean distance
   may dilute) -- worst LOLO fold is stig.                                                        0.4
Q4 L4 holds: the law transfers to the hybrid's substitution settings without refit.               0.6
Q5 sF alone (a plain "is the history anywhere in the state" coordinate) fails L1 because it
   cannot see PASSIVE.                                                                            0.7
