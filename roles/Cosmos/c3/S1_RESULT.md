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

## L5 adversary (runs/maps_s1/ATTACK.json; 2026-09-24T07:47Z): SURVIVED
720 fresh candidates (30% off-lattice sizes: rnn n 16/96, graph N 48/192, stig L 8/32); 90 certified
(15 band + 15 confident per family). Confirmed confident misses 2/44 = 4.5% (kill > 10%); per family
rnn 0/15, graph 2/14 (14%, kill > 20%), stig 0/15. Band calibration: mean law P 0.46 vs observed
FUNCTIONAL rate 0.55 (n 40).
FAILURE REGION (shape): both confirmed misses -- and the one graph map misfit -- are noisy excitable
graph worlds (b = +0.5, flip p 0.03-0.1) predicted FUNCTIONAL, certified NONE, with sR 0.06-0.31 AND a
readout-view signal that GROWS from t = 1 to the query (rR 1.5, rF 1.35). INFERRED: sR measures
SENSITIVITY to history; in chaotic noisy dynamics any perturbation is amplified but not in a cue-
consistent way, so sensitivity is not reliable accessibility. Recorded as a known failure region
(on the D/E withholding list); the law is NOT patched in Session 1.

## Uncertainty and family dependence (post-hoc, on the map data)
Pooled threshold sR* = 0.0304; bootstrap 95% CI [0.0064, 0.0425] (wide below: stig has few worlds near
its boundary). Family-specific thresholds: graph 0.040, rnn 0.032, stig 0.004; gain over the pooled
threshold in per-family BA: graph 0.000, rnn 0.000, stig 0.016 -> no family-specific correction term is
needed (directive s16 stop condition NOT triggered), but stig's own boundary sits lower than the pooled
one: an offset the coordinate audit should look at.

## Preliminary candidate law (Session 1 endpoint; NOT frozen)
  FUNCTIONAL  iff  sR > sR*,  sR* = 0.030 [0.006, 0.043]
  PASSIVE     iff  sR ~ 0 and sF > 0    (history persists, none in the actor's view)
  NONE        iff  sF ~ 0
where sR / sF are the generic decoder-free history-signal shares of the readout view / full causal
state (geometry.py). Known failure region: chaotic noisy dynamics (sensitivity without information).
