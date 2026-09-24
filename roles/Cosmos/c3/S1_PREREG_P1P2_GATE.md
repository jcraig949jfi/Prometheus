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
