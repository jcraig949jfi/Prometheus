# HT-e743909f97 / W3 -- implementation notes (written before any code ran)

Bound by roles/Hecate/prereg/2026-09-30_probe_round2/PREREG.md (control-first
pilot) and 2026-09-29_probe_round1/PREREG.md. Prompt: probe_impl_v2.md,
sha256 2021ed66...8185e (verified).

## Spec field -> code

| spec field | code |
|---|---|
| 1D linear-Gaussian system, drift parameter | `core.observe`: x_{t+1} = x_t + theta_t + w_t, w ~ N(0, 1/2); only increments d_t = theta_t + w_t are used (sufficient) |
| 256 clones over drift parameter | `core.run_replicator`: vector theta (256,), init U[-2,2] |
| replicate prop. to exp(-squared prediction error) | fitness exp(-(d_t - theta_i)^2); multinomial resampling each step |
| mutation sd prop. to each clone's recent error | (phase 2, world.py) sd_i = K * sqrt(ema_i), ema_i = EMA of e_i^2, alpha = 0.1, inherited on resampling |
| switch true parameter at step 1000 | theta_t = theta0 for t < 1000, theta1 for t >= 1000 |
| control: bootstrap PF, constant jitter of same time-averaged size | (phase 2) same loop, sd = mean of all sds the error-scaled run applied for that seed |
| positive control: exact grid posterior alongside; replicator, zero mutation, exact weights, KL < 0.02 | `core.run_positive`: 256 clones = 4 per grid centre, frequencies updated by the deterministic replicator equation x_i <- x_i f_i / mean f (exact weights, no sampling), no mutation |
| cheat | `core.run_cheat`: observable injected: q := exact posterior, clone mean := true theta |
| null twin: mutation sd from same empirical distribution, permuted across clones and time | `core.null_twin_sd`: the arm computes the error-scaled sd for every clone every step (same K, alpha), adds them to a pool, and each clone's applied sd is a uniform draw from the pool of all sds so far (all clones, all steps) |
| observable: KL(clone histogram || grid posterior), 64-bin grid | `core.kl`: q = clone counts binned to nearest of 64 centres on [-2,2] (width 1/16); p = exact grid posterior; KL = sum_{q>0} q (log q - log p), log domain |
| re-tracking time | first s >= 0 such that at step 1000+s, abs(clone mean - theta1) <= max(clone sd, 1/32); censored at 1000 if never |
| stationary KL | mean KL over steps 750..999 (pre-switch, after burn-in), per seed; median over seeds |
| 30 seeds | seeds 0..29 for every arm |

## Exact grid posterior

Generative class: theta lives on the 64 grid centres; prior uniform; each
step theta stays with prob 1-h or jumps to a uniformly random centre, h =
1/2000 (one switch in 2000 steps, the spec's size). Forward HMM filter in
log domain: pred = log((1-h) p + h/64), post = pred - (d - c)^2, normalise.
exp(-e^2) is the exact Gaussian likelihood because sigma^2 = 1/2 (chosen so
the spec's fitness is the exact likelihood). Truths are grid centres:
theta0 uniform over centres in [-1,1]; theta1 a centre with 0.75 <=
abs(theta1-theta0) <= 1.25 and abs(theta1) <= 1.5 (seeded).

Measurement order per step: observe d_t, compute errors, update EMA,
reweight/resample, MEASURE (histogram, mean, sd; exact posterior after the
same datum), then mutate (prediction step to t+1). Clones clipped to [-2,2].

## Ambiguities and chosen readings

A1 "exact weights" + zero mutation: read as the replicator equation on
   frequencies (infinite-population limit, no resampling noise). With
   multinomial resampling and zero mutation the population fixes by drift
   and no construction could meet KL < 0.02. Clones are placed on the grid
   centres (4 each) so the positive control has the effect by design.
A2 "1 sd": the approximating posterior's own sd (clone population sd),
   floored at half a bin width (1/32) so a collapsed population is not
   unreachable. Cheat and positive control use their own q's sd, same floor.
A3 Stationary = pre-switch window 750..999.
A4 "median re-tracking time <= 0.7 x both": ratio of medians over 30 seeds.
A5 Null twin in the PILOT: it cannot exist without the error-scaled sd
   rule (it matches that rule's statistics), so the rule sd = K*sqrt(ema)
   lives in core.py as part of the null twin. No treatment arm (no
   error-coupled mutation applied to clones) exists in phase 1. "Permuted
   across clones and time" is implemented causally (draw from the pool so
   far) because the pilot has no completed treatment run to permute.
A6 null_twin_meets_success. PILOT: the criterion's ratio clause needs the
   control arm (phase 2); read literally with the null twin in the
   treatment role its ratio against itself is 1 > 0.7, so it is
   structurally False in the pilot. This makes the pilot's null-twin check
   non-informative -- recorded as an anomaly, not hidden. PHASE 2 (decides
   CONFOUNDED): KL_null < 0.1 AND median rt_null <= 0.7 x median rt_control
   (the self-comparison is dropped).
A7 cheat_detected: cheat meets the success criterion against the
   comparators that exist (pilot: null twin; phase 2: null twin and control).
A8 positive_meets_success: median stationary KL < 0.02 (the spec's own
   positive-control threshold, which implies < 0.1). Its re-tracking is
   not part of its job (zero mutation).
A9 Outcome (phase 2), in order: pos or cheat not detected ->
   INSTRUMENT_FAIL; null twin meets success -> CONFOUNDED; treatment
   meets success -> SIGNAL; otherwise NULL (includes the 0.7-0.9 gap,
   which meets neither criterion; flagged in notes if it happens).

## Parameters (fixed now, before any run)

N = 256, T = 2000, SWITCH = 1000, SIGMA2 = 0.5, H = 1/2000, GRID = 64 on
[-2, 2], K = 0.01 (stationary sd ~ 0.007 ~ 0.11 bin: a round value chosen
so stationary jitter is small against the grid, not from any result),
ALPHA = 0.1, window 750..999, rt floor 1/32, rt censor 1000, seeds 0..29.
Single-threaded numpy (OMP/MKL threads = 1). CPU time via time.process_time.

## Repairs

(none yet)

## Run log

- Pilot attempt 1: PASS (PILOT.json). No repair used.
- Phase 2 attempt 1 (world.py, evaluate.py): outcome NULL (OUTCOME.json).
  Pilot arms rerun in phase 2 reproduced the pilot rows exactly (same seeds,
  same code path). No parameter changed after any treatment statistic.
- Caveat for readers: K = 0.01 was an implementer choice (the spec gives no
  mutation scale). All three bootstrap arms sit at stationary KL ~1.6, so the
  KL clause fails for every jittered arm at this K; whether any K meets both
  clauses was not searched (would be tuning after seeing treatment numbers).
