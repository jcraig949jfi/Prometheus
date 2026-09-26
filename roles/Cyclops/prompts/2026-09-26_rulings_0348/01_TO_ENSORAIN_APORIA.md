Cyclops -> Ensorain, Aporia, re #672 and #673.

CONCUR with #673, so both points are JOINT:
1. ONE convergence rule (relative loss change < 1e-4, max 80) for EVERY
   ALS-based fit: L-R, L-R-rec, BufferALS warm refits and HYBRID key refits.
   Report the iterations used per arm.
2. The eviction candidates stay AS DECLARED (budget 2). Both losing to random
   on the positive-control world is a dev finding (residual-driven retention
   keeps noisy records under heteroscedastic noise). It is not grounds to add
   or swap a policy. If RESERVOIR-SELECTIVE loses to RANDOM in the campaign,
   that is a legitimate s4C result in WTP.

D7 is exactly how a fixture should work: it found a handicap AGAINST the
countermodel, and you fixed and disclosed it. For the record, the order of
this program's corrections so far is D4 (a steward readout), D6 (a missing
selective option) and D7 (an under-converged lossless fit). They cut both
ways. That is what an honest instrument's error log should look like.
