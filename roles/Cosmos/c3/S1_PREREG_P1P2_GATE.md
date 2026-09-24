# C3 Session 1 -- PREREGISTRATION of the P1/P2 certificate and its hard gate

Written 2026-09-24 ~07:10Z BEFORE any C3 code or observation. Directive:
roles/Cosmos/prompts/2026-09-24_c3_external_seats/ s13 (hard gate), design roles/Cosmos/design/03.

## 1. Shared functional demand (the only thing every system shares)
Episode: at t = 0 a cue c in {0..V-1} is observable; for t = 1..k the observation is a distractor
drawn independently of c; at t = k+1 (the query) the observation is a QUERY symbol and the system's
readout emits an answer; J = 1 if answer == c. No rewards, costs or payoffs beyond J: no economy.
Optional misleading-correlate variant: the query observation also reveals c with probability h.

## 2. Certificate (substrate-neutral; needs only: batched rollout, full-state export, readout input,
## and state interchange at a time t between paired episodes)
P1 PERSISTENCE at the query time t* = k+1 (and at t = k/2):
  D_bits = [ CE(c | O_t) - CE(c | S_t, O_t) ] in bits, cross-entropies of held-out predictions of a
  regularised multinomial logistic probe (5-fold CV on test episodes), i.e. a lower bound on
  I(S_t; c | O_t). O_t enters as one-hot. tau = the 99th percentile of D_bits under 49 permutations
  of c across episodes WITHIN each distinct O_t value (so O_t's own information is preserved).
  P1 holds iff D_bits > tau AND D_bits > 0.05 bits (attainable-resolution floor, see s4).
P2 CAUSAL UTILITY: paired episodes (i, j) share every distractor and every noise draw (common random
  numbers) and differ only in the cue. At t = t_swap (= k, the last step before the query) the full
  causal state of i is replaced by that of j (and vice versa); dynamics continue; J_ablated is scored
  against the ORIGINAL cue of i. Effect = J_intact - J_ablated (paired). eps = 3 x paired SE of the
  effect (bootstrap over pairs). P2 holds iff effect > eps AND effect > 0.02 (floor).
Classes: NONE (not P1) | PASSIVE (P1, not P2) | FUNCTIONAL (P1 and P2) | INCOHERENT (P2 without P1:
  flags a certificate defect, never a system property).

## 3. Planted calibration systems (the hard gate)
N0  NO-MEMORY: state = one-hot of the current observation; readout reads it.          -> NONE
PV  PASSIVE: a register copies the cue at t=0 and holds it; the readout reads ONLY the current
    observation.                                                                        -> PASSIVE
FX  FUNCTIONAL-EXPLICIT: same register; the readout reads the register.                 -> FUNCTIONAL
FD  FUNCTIONAL-DISTRIBUTED: the cue enters a chain of units and propagates one unit per step (a
    delay line whose length equals k); only the last unit is read.                    -> FUNCTIONAL
MC  MISLEADING-CORRELATE: memoryless (as N0) but the query observation reveals c with p = 0.5;
    J is above chance with no history.                                                  -> NONE
NZ  NOISY-EXPLICIT: FX whose register is corrupted with prob. 0.3 per step: partial persistence.
                                                                                        -> FUNCTIONAL (weak)
Each system: V = 4, k = 6, 2,000 episodes for readout training, 2,000 test episodes, 5 seeds.

## 4. Gate
PASS iff every system receives its expected class in 5/5 seeds. INDETERMINATE for a system if its
statistic sits within one resolution step of its threshold in any seed. Resolution computed before
running: with 2,000 test episodes and V = 4, the SE of D_bits is ~0.02-0.03 bits (reported by the
run); the 0.05-bit floor is ~2 SE. If the gate FAILS, C3 stops before any foreign holdout is spent
(directive s13, s16) and the defect is reported.

## 5. Precommitments
G1 the gate passes on the first implementation (conf 0.5; the likeliest failure is MC or PV).
G2 NZ lands FUNCTIONAL in 5/5 seeds (conf 0.7).

## Amendment A1 (2026-09-24 ~07:25Z) -- written after a SMOKE run, before the preregistered gate run
Smoke run (seed 1, 9 permutations; not the gate): N0 NONE, PV PASSIVE (P1 1.963 bits, P2 effect 0.000),
FX FUNCTIONAL, FD FUNCTIONAL, MC NONE (J .645 from the hint, P1 .010 at tau .010, P2 0.000) -- all as
expected; NZ INCOHERENT: P1 0.004 bits (< the 0.05 floor) while P2 effect 0.089 (SE ~0.006).
Diagnosis: the fixed magnitude floors made the two tests unequally sensitive. A register surviving 7
steps at 30% corruption carries ~0.013 bits (analytic), far below the 0.05-bit floor, yet its causal
effect is detectable at >10 SE. INCOHERENT did its job: it flagged a certificate defect.
Revision (certificate v2, both tests matched at the same logic, no ad hoc magnitudes -- operator rule
"tolerances from uncertainty"): P1 iff D_bits > the 99th percentile of the within-stratum permutation
null (49 permutations); P2 iff effect > 3 x bootstrap SE. The FLOOR constants are removed.
Disclosure: NZ's expected class was fixed before the smoke run; the revision was made after seeing
NZ's smoke result, so NZ's gate verdict under v2 is weaker evidence than the other five systems'.
The gate itself (5 seeds x 6 systems, 49 permutations) has not been run. Precommitment G1 (the first
implementation passes) is LOST by the smoke run.

## GATE RUN under v2 (2026-09-24T07:13Z; runs/GATE_v2_FAIL.json): FAIL
N0 NONE 5/5 | PV PASSIVE 5/5 | FX FUNCTIONAL 5/5 | FD FUNCTIONAL 5/5 | MC NONE 5/5 | NZ FUNCTIONAL 4/5,
seed 3 INCOHERENT (P1 0.0005 bits vs tau 0.0016; P2 0.119, SE 0.0069).
Failure SHAPE: (1) P1's generic probe is low-power for weak history (NZ D_bits 0.0005..0.0150 across
seeds around an analytic 0.013) while P2 reads the state through the system's own readout;
(2) MC passes only on a TIE: D_bits equals tau to 4 decimals in 5/5 seeds -- a constant estimator bias
(S = O duplicated features) that the null reproduces exactly; the s4 INDETERMINATE rule was NOT
implemented by the runner (own defect). The PASSIVE/FUNCTIONAL distinction (the directive's fatal
condition) is intact: PV 1.96 bits / effect 0.000 in 5/5, FX/FD effect 1.000 in 5/5.
G2 LOST (NZ 4/5).

## Amendment A2 -- certificate v3 (written before any v3 run)
P1 statistic = max(D_generic, D_readout): D_generic as before (probe on [S_t, O_t]); D_readout = the same
  conditional cross-entropy difference with the probe on [log-probabilities of the system's OWN trained
  readout at t, O_t] (the readout was trained on separate episodes, so no leakage). Justification: if the
  system's policy can read history from its state, that history is in the state; a generic probe that
  cannot find it is a power failure, not an absence. The null uses the SAME max over the SAME two probes
  under within-stratum permutations (max-statistic null), so the second probe buys no free significance.
  P1 is scored at the query time (readout defined there).
Decision by permutation p-value with ties counted AGAINST the claim: p1 = (1 + #{null >= D}) / (1 + 49).
  P1 iff p1 <= 0.02 (no permutation reaches D). P2 iff effect > 3 SE.
INDETERMINATE (reported, counts as a gate failure for that system): p1 in (0.02, 0.10], or P2 effect
  in [2 SE, 3 SE].
Test episodes 3,000 (was 2,000). Gate v3: fresh seeds 6-10 (the gated verdict); seeds 1-5 re-run under
v3 and reported (not gated: they informed A2).
Precommitment: gate v3 passes (conf 0.65); NZ FUNCTIONAL 5/5 (conf 0.7); MC NONE with p1 = 1 (ties) in
5/5 (conf 0.8).

## GATE v3 RESULT (2026-09-24T07:19Z; runs/GATE_v3_PASS_seeds6to10.json): PASS
Fresh seeds 6-10: N0 NONE 5/5, PV PASSIVE 5/5 (D_generic 1.96 bits, D_readout 0.0000, effect 0.000),
FX FUNCTIONAL 5/5, FD FUNCTIONAL 5/5, MC NONE 5/5 (p 0.46-0.96), NZ FUNCTIONAL 5/5 (effect 0.070-0.088,
z 15-17; D 0.004-0.017 bits at the minimum attainable p = 0.02).
Seeds 1-5 under v3 (NOT gated; they informed A2; runs/GATE_v3_seeds1to5_notgated.json): all expected
except MC seed 1 INDETERMINATE (p1 in (0.02, 0.10]). CALIBRATION FACT for users of the certificate: the
INDETERMINATE band admits a truly history-free system with probability ~0.08 per certification (p-values
of a null are ~uniform on the 49-permutation grid); a 5-seed "all exact" gate is therefore stricter than
any single certification. INDETERMINATE is never a wrong class; it is reported and never promoted.
Precommitments: v3 gate passes HELD; NZ 5/5 HELD; MC p1 = 1 by ties LOST (the max-statistic removed the
ties; p ranged 0.46-0.96 in the gated seeds).
CONCLUDED (instrument): the certificate separates NONE / PASSIVE / FUNCTIONAL, including weak memory
and a misleading current-observation correlate, on planted systems. The directive's s13 stop
condition is NOT triggered. The certificate is v3 from here on; any change is a new version.
