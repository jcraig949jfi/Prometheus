# C0e -- second sealed universe E vs the already-frozen law -- PREREGISTRATION

Written 2026-09-23 ~13:05Z, before family E was executed on any sealed or fresh world.

## 0. What is being tested

The law frozen in C0b, unchanged:
  law f852d782cb (cmap v3), freeze hash 37c28c59ae919b08... (ledger in the C0b store):
  (C - (G + exp(-N))) <= -1.055  AND  ((C - log(Q)) * K) >= 0.1792
It was mined on regs/ring/ca, survived one adversary round, predicted sealed family D (BA .983)
and D interventions (G6b). D is now spent. E is a SECOND sealed universe, written and sealed AFTER
the law was frozen, so the law cannot have been shaped by E in any way; E's design, however, was
written by the same author who knows the law (declared conflict: E could have been written to be
easy or hard for it; I wrote it to be mechanically unlike every other family -- collective
memory with stochastic majority repair and a colony-wide agent budget -- and I declared its
hazard with a crude approximation I did not tune).

Family E: prometheus/cosmos/holdout/swarm.py (import refused outside the broker subprocess).
Seal: prometheus/cosmos/holdout/sealed_spec_E.json
  sha256 d17ace6e6f9171da49afab4a6c9626cfd1d998ae9e5c9cfdc14837dc319e7528 (240 worlds, CSPRNG nonce,
  swarm.py source hash recorded). Pre-seal selftest (fixed non-sealed control worlds, booleans
  only): replay identical, positive control, memoryless floor, sham quiet -- all true.
E's v3 coordinates: C = c_agent M H / R; N (v2) = H binom(M, m) u^m, m = (M+1)//2;
  K; G; Q = min(1, (A_max // M) / (K + 1)).

## 1. Gates
G5E  sealed-E balanced accuracy of the frozen law >= 0.80 AND >= (5-NN transfer from the C0b
     visible rows, v1 feature space) - 0.05. Majority baseline reported.
G6E  G6b protocol (c0b PREREG amendment B1) with salt "G6E" on fresh E worlds, cost axis c_agent.
     direction_ok >= 10/12 AND law mean |log2(f_obs_hi / f_hi)| <= 0.5 AND that error <= (best
     constant prescription's mean |log2 error| on the same ladders, constant chosen post hoc,
     i.e. generous to the baseline) - 0.3. (The chance floor B1 lacked.)

## 2. Precommitments written to be lost
E1  G5E passes.                                                                 conf 0.45
E2  If the law errs on E, the errors concentrate in M >= 3 with u > 0 (the crude declared
    hazard) rather than in the capacity-limited worlds (Q < 1).                  conf 0.6
E3  G6E passes.                                                                 conf 0.4

## RESULT (appended 2026-09-23T12:58Z; C0E.json, receipts_after_c0e.jsonl)
G5E PASS: sealed-E BA 0.972 (acc 0.967), 5-NN 0.769, majority 0.500; Brier 0.031 vs 0.174.
     (C0E.json field "base_rate_D" is E's base rate, 0.225 -- a label defect in broker.adjudicate.)
G6E PASS: 399 candidates, 124 eligible, 12 scored; direction 10/12 (at threshold); law mean
     |log2(f_obs_hi/f_hi)| 0.318 vs best constant (f=4) 1.250 -> clears the floor by 0.93.
E1 HELD. E3 HELD. E2 HELD (6 of 8 errors in M >= 3 with u > 0; 2/55 errors in Q < 1 worlds).
Error SHAPE shared with sealed D: false PAYS at the high-cost edge (7/8 on E, 7/7 on D), and both
G6E direction misses are bases just inside the law's cost ceiling (f_hi 1.06-1.08) observed QUIET.
INFERRED (not yet tested): the law's cost-ceiling atom sits ~0.045 in C above the physics form
G exp(-N) - C >= 0.10 at small N.
