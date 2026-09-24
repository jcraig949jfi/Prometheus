# C3 Session 1 -- results (running record; PROVISIONAL throughout)

## P1/P2 certificate (S1_PREREG_P1P2_GATE.md)
v1 smoke: NZ INCOHERENT (floor mismatch) -> A1. Gate v2 FAIL (NZ seed 3 INCOHERENT; MC passed on a tie).
v3 (A2: readout probe + max-stat null + p-value, ties against): gate PASS on fresh seeds 6-10;
non-gated seeds 1-5: one MC INDETERMINATE (the band's ~8% false-flag rate).

## Maps (runs/maps_s1; 2026-09-24T07:38Z; code 01b6b49b1 maps, certificate v3)
120 worlds (40 per family, k in {2,4,8}) + 12 hybrid substitution worlds.
  rnn   FUNCTIONAL 34, NONE 4, INDETERMINATE 2
  graph NONE 16, PASSIVE 8, FUNCTIONAL 11, INDETERMINATE 4, INCOHERENT 1
  stig  FUNCTIONAL 31, PASSIVE 9
  hybrid (internal, external) x k: FUNCTIONAL whenever either channel is present (9/9); NONE when both
         are removed (3/3). History moves to the remaining channel; the function is unchanged.
INCOHERENT graph K=3 b=-.5 p=.01 k=8: P2 effect .028 (z 7.7) while both P1 probes are negative
(D_generic -0.051: the generic probe overfits a 96-dim noisy binary state). Certificate power limit;
recorded, not fixed in Session 1. Several noisy graph worlds show strongly negative D_generic.

## Law search (runs/maps_s1/LAW.json; analysis committed before the data were read)
CANDIDATE: exp(-sR) <= 0.97, i.e. FUNCTIONAL iff sR > ~0.030 (sR = readout-view history-signal share).
LOLO BA graph 0.960, rnn 1.000, stig 0.968; null p = 0.05 (19-permutation floor).
Baselines (LOLO BA graph/rnn/stig): sF-only .602/.882/.530; kNN5 .820/.912/.785.
Gates L1 PASS, L2 PASS, L3 PASS (per family), L4 PASS (hybrid substitution, no refit).
PASSIVE worlds (17): sR = 0.000 in all, sF 0.078-1.000 -> PASSIVE <=> history in the state, none in the
readout's view. Misfits: 2 of 113 (graph K3 b.5 p.1 k2 NONE at sR .101; stig delta .02 v1 j.3 k2 FUNCTIONAL
at sR .009, effect .010 -- both weak/noisy).
Precommitments: Q1 HELD (sR threshold), Q2 HELD, Q3 LOST (worst fold is graph .960, not stig .968 --
close), Q4 HELD (hybrid 12/12), Q5 HELD (sF-only fails on graph and stig).

INFERRED (not concluded): the law is close to a restatement of "a trained readout can use history
only if history reaches the readout's inputs". Its non-definitional content: one unit-free, decoder-
free geometric quantity with ONE threshold separates FUNCTIONAL across three unrelated mechanisms,
succeeds where the persistence coordinate fails, and transfers without refit when the substitution
attack moves history from internal state to the world. What governs functional memory here is causal
ACCESSIBILITY to the actor, not the locus of persistence. Whether that survives a substrate Cosmos did
not write is D's question.
