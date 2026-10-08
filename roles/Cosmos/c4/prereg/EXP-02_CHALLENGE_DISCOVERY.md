# EXP-02 -- challenge-proposal DISCOVERY batch 1 + the egocentric re-encoding test (EXPLORATORY; prereg 2026-10-08
# before any EXP-02 world was run)

Why: EXP-01's foreign family was uninformative (30/30 FUNCTIONAL under P) and stig failed for the LOCAL laws
(moving-sensor reachability; frame-dependent linearization). EXP-02 asks whether C4-L-0003 TRANSFERS, unrefit,
to a challenge region where every family, including the foreign one, can fail.

## Worlds
DISCOVERY split, batch 1; proposal Q (exp01.Q, written from the declared knob meanings: noise, instability,
transport, export). 30 worlds per family (rnn, graph, stig, sediment). Caveat (R-STAT A8): Q is not author-blind;
the author has seen EXP-01.

## Frozen predictor (no refit)
C4-L-0003 with theta = -4.3144 (results/theta_L0003.json: pooled max-BA on EXP-01 determinate rows, A labels).
Also reported: LOFO-refit L-0003, L-0001, T2a, T3-DOWN.

## Decisions fixed now
- L-0003 is KILLED as a cross-family candidate if, with the FROZEN theta, (i) its mean within-family BA uplift
  over T3-DOWN on the T3-REGISTERED rows (the S0-A analogue) is < 0, OR (ii) it is below T2a in >= 2 informative
  families (both classes >= 3 rows).
- FOREIGN-FAMILY test: if sediment is informative, frozen-theta L-0003 BA on sediment < .60 => FAILED on the foreign
  family (recorded as the authorship-independence verdict). If sediment is still uninformative => NOT_REACHED
  again, and Q itself is recorded as a failed design for that family.
- T-C1 frame test (no labels needed): for every stig world, L-0003's predicted class on Stig vs EgoStig (exact
  relabelling, readout identical). FRAME-DEPENDENT if they differ on > 10% of stig worlds. Also reported: which
  frame's prediction agrees with Certificate A.
