# ENSORAIN E1 -- preregistration, part 2 (constants frozen; no gate moved)

Currency: 2026-09-23. Committed after dev engineering (seeds 0-999) and
BEFORE any tuning run (seeds 1000-1999) or confirmatory run (instances
20000-20039). Part 1 (acf899366) is unchanged.

## 1. Dev findings (dev rows only; ensorain/runs/e1_dev_*.jsonl)

- d1 (default constants, C=192, 6 instances): TT_LATENT held-out R^2
  -0.18; TT_INJECT only 0.55-0.63 lock success because the code let it
  consolidate -- a BUG against part 1 s3 ("no learning"), fixed (sweeps
  0). NOMEM passes 25% of locks at absolute tau .15: the TT field is
  heavy-tailed around 0.
- Learner round 1 (proximal lam x sweeps): lam 10 / 5 sweeps -> R^2_ho
  0.60. Round 2: lam 30 / 20 sweeps -> R^2_ho 0.83, R^2_seen 0.96, L2
  success 0.56. Diagnosis: 128-sample scratch batches are highly
  correlated (16 fibers); weak proximal terms forget. Round 3 NOT used.
  These knobs are genes for EVERY fitting arm with the same ranges (s3),
  so the finding does not favour the TT.

## 2. Frozen constants

Tolerance: part 1 form kept literally, |answer - truth| < tau * sd(type),
  tau = 0.15. Criterion check on dev worlds (Gaussian errors): R^2 .99 ->
  ~87% pass, R^2 .5 -> ~17%, NOMEM 25% (heavy tails). The chance floor is
  removed by EFF (minus U_NOMEM) and the negative control is relative to
  NOMEM, so no change of form is needed. (A relative-tolerance form was
  evaluated on dev and REJECTED: it would have changed part 1's rule.)
Economy: energy0 400, metabolism 0.5/event, reward 10 per solved lock.
Compute: kappa 5e-6 energy/unit; matched per-life ceiling 3e7 units
  (fits the round-2 TT config, ~2.2e7); scratch S = 128 samples.
Secondary sensitivity (reported only): kappa x0 and x4.

## 3. Tuning (equal budget; part 1 s3)

Per cap in {96, 128, 192, 384}, per tunable arm (CP, LOWRANK, MLP,
TT_OBS, TT_TUNED): 24 random configurations (seeded 31337 + cap), each
on 4 training worlds (instances 1000 + 4*cap_index .. +3, class 0,
organism seed 0). NOMEM is run on the same worlds for U_NOMEM. Objective:
mean EFF. Champion per (arm, cap) is frozen in
ensorain/runs/e1_champions.json before confirmatory runs.
Shared genes (every fitting arm): lam log-uniform [0.3, 100];
  sweeps/epochs in {2, 5, 10, 20}; init_scale in {0.3, 0.5, 1.0}.
Arm genes: TT_OBS ranks profile (each 1..6, shrunk to cap), observed
  order fixed; TT_TUNED + order (uniform over 24); CP rank 1..cap/32;
  LOWRANK partition in {0,1,2}, rank 1..cap/128 (NA below 128);
  MLP width 1..(cap-1)/34, lr log-uniform [0.01, 0.3], weight-decay-to-old
  lam log-uniform [1e-4, 1e-1], epochs in {5, 10, 20, 40}.
TT_LATENT (positive control) = TT_TUNED champion's lam, sweeps,
  init_scale at the same cap, latent order, ranks (3,3,3) shrunk to cap.

## 4. Confirmatory matrix

C1: lam in {0, 1}; caps {96, 128, 192, 384}; arms NOMEM, LRU, KNN, CP,
    LOWRANK, MLP, TT_OBS, TT_TUNED, TT_LATENT, TT_INJECT, ORACLE;
    instances 20000-20039, organism seeds 0-1.
C2: transplant (part 1 s6) at C=192, lam 0, all learning arms.
C3: SMUGGLER at C=192 on instance 20000 (must be refused).
C4 (secondary): C1 at caps {128, 192}, lam 0, kappa x0 and x4.
Scorer ensorain/e1/score.py committed before C1 runs.
