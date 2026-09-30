# HT-55162c0ac0 / W2 -- implementation notes (written before any run)

Prompt: hecate/programs/_prompts/probe_impl_v2.md (sha256 2021ed66...185e).
Bound by roles/Hecate/prereg/2026-09-30_probe_round2/PREREG.md and
2026-09-29_probe_round1/PREREG.md. Spec: program.json experiment W2
(mechanism M5, lens L6).

## Spec field -> code

| spec field | code |
|---|---|
| mechanism: x' = (3.9+u_t) x (1-x), abs(u_t) <= delta | core.fmap, core.R=3.9; u clipped to [-DELTA, DELTA] in core.simulate |
| controller u_t = sum_{k<C} w_k (x_{t-k} - x*_{phase,k}) | core.simulate: phase = index of nearest orbit point to x_t; reference for lag k is orbit point (phase-k) mod p; weights w[phase, k] |
| fitted by least squares on 20000 uncontrolled points | core.training_series (N=20000, open-loop exploratory kicks, see A1) + core.fit_controller (A2) |
| intervention: C in 1..8, p in 1..8, delta = 0.02 | core.CS, core.PS, core.DELTA |
| control: controller fitted on time-shuffled training series | core.fit_controller(shuffle=True): joint random permutation of the (x_t, u_t) pairs, then the identical fit |
| null_twin: time-shuffled training series | same construction as control (the spec defines them identically); see A8 |
| positive_control: C = 16 stabilises p = 1..4 with success fraction >= 0.8 | arm POSITIVE_CONTROL: unshuffled fit, C = 16, p = 1..4 |
| observable: success = abs(x_t - orbit) < 1e-3 for 200 consecutive steps within 5000 steps; fraction over 50 trials | core.simulate: run-length counter, TOL=1e-3, RUN=200, NSTEPS=5000, NTRIALS=50 |
| success_criterion | core.criterion (part A: p_max nondecreasing in C and p_max(8)-p_max(1) >= 3; part B: twin fraction <= 0.1 for all p >= 2, all C) |
| failure_criterion | core.criterion: p_max(8)-p_max(1) <= 1, or twin fraction >= 0.5 at some p >= 2 |
| CHEAT (round-1 PREREG) | arm CHEAT: for cells with p <= C the observable x_t is overwritten with the exact orbit point after step 100; cells p > C and the cheat twin are uncontrolled trajectories. By construction p_max(C) = C, so the evaluator must report success |

## Ambiguities and chosen readings (fixed before any run)

A1. "20000 uncontrolled points": uncontrolled data with u = 0 cannot
identify the kick sensitivity, so the training series is OPEN-LOOP: u_t
drawn i.i.d. uniform in [-delta, delta], no feedback. 100 burn-in steps
discarded. "Uncontrolled" is read as "no feedback controller".

A2. "fitted by least squares": for each orbit phase phi, take training
times t with abs(x_t - x*_phi) < EPS_FIT = 0.01 (nearest orbit point is phi),
t >= C-1. Regress, without intercept (the spec's controller form has
none), y = x_{t+1} - x*_{phi+1} on [x_{t-k} - x*_{phi-k}]_{k<C} and u_t.
Coefficients a (length C), b. Deadbeat weights w[phi,k] = -a_k / b
(the kick that makes the fitted next deviation zero). Fewer than C+6
rows for a phase -> that phase's weights are 0 (controller inert),
recorded in rows.

A3. Weights are per phase (w[phi, k]), since x*_{phase,k} is phase
dependent and one weight vector cannot serve different local slopes.

A4. u_t outside [-delta, delta] is CLIPPED (literal reading of
abs(u_t) <= delta), not gated off. Controller acts only once C past
states exist (pre-history of C-1 free steps before the 5000 are counted).

A5. Which UPO of period p: prime-period-p orbits of f (u=0) found by
sign changes of f^p(x) - x on a 2,000,001-point grid + bisection;
chosen orbit = the one with the smallest abs(multiplier) (least unstable),
ties by smallest point. Orbit residual abs(f^p(x) - x) recorded.

A6. "abs(x_t - orbit) < 1e-3" = distance from x_t to the nearest point of
the orbit set. Success once a run of 200 consecutive steps is reached.

A7. Aggregation: success fraction per (C, p) cell pooled over all seeds
(5 seeds x 50 trials = 250 trials); per-seed fractions also recorded.
p_max(C) = the LARGEST p in 1..8 with fraction >= 0.8 (literal), 0 if
none.

A8. Control arm and null twin are identical constructions in the spec.
Both are run; they differ only in the shuffle permutation stream.
Part B of the criterion is evaluated on the CONTROL arm; the
CONFOUNDED test uses the NULL_TWIN arm.

A9. Pilot decisions:
- positive_meets_success: pooled fraction >= 0.8 for every p in 1..4 at C=16.
- cheat_detected: core.criterion on the CHEAT grid (with the cheat twin)
  returns success.
- null_twin_meets_success: part A holds on the null-twin grid OR the
  null twin violates part B (fraction > 0.1 at some p >= 2, any C) --
  i.e. the shuffled fit either shows the memory law or stabilises
  long orbits on its own.
- pilot_pass = positive and cheat and not null.

## Parameters (from spec unless marked chosen)
R=3.9, DELTA=0.02, NTRAIN=20000, TOL=1e-3, RUN=200, NSTEPS=5000,
NTRIALS=50, C in 1..8, p in 1..8, positive C=16.
Chosen: EPS_FIT=0.01, BURN=100, CHEAT_START=100, min rows C+6,
UPO grid 2,000,001 points, initial conditions uniform(0.01, 0.99).
Seeds: 0,1,2,3,4 (pilot and phase 2). Per seed: np.random.default_rng
([seed, arm_code, stream]). Single-threaded BLAS for honest CPU accounting.

## Repairs

Pilot attempt 1 (kept as PILOT_attempt1.json + pilot_rows_attempt1.jsonl;
numbers kept here): positive_meets_success TRUE (C=16 pooled fraction
1.0 at p=1..4), cheat_detected TRUE, null_twin_meets_success TRUE ->
pilot FAIL. The null twin never showed the memory law (p_max = 0 at
every C), but it violated part B: pooled fraction up to 0.2 at p >= 2
(e.g. C=2 p=2/6/8, C=8 p=3). Mechanism: in single seeds a shuffled fit
stabilised 50/50 trials of a cell. The shuffled fit yields a random
proportional gain, and a 1-D map's UPO is stabilised by any gain in a
finite interval, so random gains sometimes land in it.

REPAIR (the one allowed, controls only, thresholds unchanged): reading
A2 fitted WITHOUT an intercept. On shuffled data the target
x_{t+1} - x*_{phi+1} has a large nonzero mean (E[x] - x*), which a
no-intercept fit loads onto the slope coefficients and so inflates the
spurious gains. Repair: fit y = a.dX + b u + c WITH an intercept c,
and DROP c from the controller (u = sum_k w_k dx_k, w = -a/b), which
keeps the spec's controller form exactly. Applies to all fits (shared
code; no treatment code or statistic exists). Everything else is
unchanged. If attempt 2 fails -> SPEC_UNATTAINABLE.
