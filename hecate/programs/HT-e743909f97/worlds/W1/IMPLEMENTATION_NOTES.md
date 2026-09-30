# HT-e743909f97 / W1 -- implementation notes (written before any run)

Prompt: hecate/programs/_prompts/probe_impl_v1.md (sha256 cf4bd374...ea2).
Rules: roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.
Sources read: W1, mechanisms M3 and M16, lens L2 in program.json.

Before writing this file I ran only the linear predictor (the Nyquist
routine and a companion-matrix eigenvalue check). No simulation of any
arm had been run.

## Model (mechanism, M3 + M16)

Discrete-time stochastic population loop, integer counts, t = 0..4999:

    p[t+1] = p[t] + Poisson(r p[t]) - Binomial(p[t], min(1, k C[t]))
    C[t+1] = C[t] + Poisson(a[t] p[t-tau]) - Binomial(C[t], c)

- "p grows at rate r": per-capita birth rate r (Poisson births).
- "killed at rate k*p*C": total kill k p C, drawn as Binomial(p, kC).
- "C decays at rate c": per-capita death c (Binomial).
- "C grows at rate a*p(t-tau)": AMBIGUITY. Read as additive recruitment
  a*p(t-tau) (Poisson), not per-capita a*p(t-tau)*C. Reasons: M3 says the
  clone "grows in proportion to delayed error" (the error is p), and
  L2 needs a stable equilibrium at small delay so that a critical delay
  exists. The per-capita reading is a delayed Lotka-Volterra system whose
  discrete-time equilibrium is not stable at tau = 0, so tau* would not
  exist and the hypothesis could not be tested.
- Equilibrium: C* = r/k, p* = c r / (a k).
- Exhaustion (M16) "reduces a when p has not fallen for T steps":
  AMBIGUITY. Read literally: a counter n counts consecutive steps with
  p[t] >= p[t-1]; it resets to 0 on any fall. Exhaustion is on when
  n >= T, and then a[t] = a0 * (1 - eta), else a[t] = a0. The spec gives
  neither T nor the size of the reduction. Chosen a priori:
  T = round(tau_pred) = 22 (the response has had one loop delay to bring
  p down and has not), eta = 0.5 (halve the gain). These are inventions
  of detail; the mechanism (gain drop on persistent non-falling error) is
  the spec's.

## Parameters (fixed before any run; all written to every row)

r = 0.05, c = 0.05, k = 1e-6, a0 = 0.025  ->  C* = 50,000, p* = 100,000.
- Counts ~1e5 so the linearisation is valid (L2 failure mode "small clone
  counts invalidate linearisation").
- r = c = 0.05 places the predicted critical delay (22.07) in the middle
  of a 40-value integer sweep tau = 0..39, giving grid resolution
  1/22 = 4.5%, finer than the 15% tolerance. (The linear loop gain is
  a k p* = c r, independent of a and k.)
- 5000 steps, window = last 2000 steps (spec). CV threshold 0.2 (spec).
- 20 seeds per condition (spec "over 20 seeds"), all arms.
- Initial condition: history p = p* for t < 0, C0 = C*, p0 = 1.1 p*
  (10% kick), identical in treatment, control, null twin and positive
  control, so that an unstable mode has a finite start amplitude.

## Prediction (L2): tau_pred

Linearise at (p*, C*): x = dp, y = dC:
    x[t+1] = x[t] - k p* y[t];  y[t+1] = (1-c) y[t] + a x[t-tau]
Characteristic: (z-1)(z-1+c) + g z^-tau = 0, g = a k p* = c r.
Nyquist: find w with |D(e^iw)| = g, D(z) = (z-1)(z-1+c); then
tau_pred = (pi - arg D(e^iw)) / w (mod the period). Result:
tau_pred = 22.071, w = 0.0396 (period 159 steps). Eigenvalue check: the
largest root modulus is 0.99996 at tau = 22 and 1.0005 at tau = 23, so
the integer onset is 23 (4.2% above tau_pred, inside 15%).
tau_pred is computed from the no-exhaustion loop only (exhaustion is a
nonlinearity with no linearisation given by the spec).

## Arms

- TREATMENT: the model above, exhaustion off and on, tau = 0..39, 20
  seeds each.
- CONTROL: AMBIGUITY. Spec: "fixed-gain controller with gain equal to the
  time-averaged k*C of the adaptive run (with and without exhaustion)".
  A literal fixed kill rate G = mean(kC) removes the loop and the delay,
  so it has no tau-dependence, tau_obs is undefined, and success clause 3
  ("exceeds the matched fixed-gain control's ratio by >= 0.1") cannot be
  evaluated. The hypothesis states the comparison as "an equal mean-gain
  reduction", and the stupid explanation as "exhaustion only reduces mean
  gain". Reading chosen: the control is the same delayed clone loop with
  exhaustion off and the clonal gain FIXED at the time average of a[t]
  from the matched adaptive run (same tau, same seed index): a_fix =
  mean(a[t]) of the exhaustion-on run for the "with exhaustion" member,
  and a_fix = a0 (the mean of the exhaustion-off run) for the "without"
  member. mean(kC) of every run is also written to the rows. Independent
  RNG stream.
- NULL_TWIN: C(t) replaced by a phase-randomised surrogate of the matched
  adaptive run's full C series (FFT, uniform random phases on all bins
  except DC and Nyquist, inverse FFT: same mean, spectrum and variance),
  negative values clipped to 0 (clipped fraction recorded); p then runs
  the same birth/kill law with the surrogate C, decoupled from p. Done
  for the exhaustion-off and -on source runs.
- POSITIVE_CONTROL: linear delayed proportional loop
  p[t+1] = p[t] - K (p[t-tau] - p*) + N(0, (0.001 p*)^2), no clipping,
  K = 2 sin(pi/104) = 0.06041. Analytic critical delay (x[n+1] = x[n] -
  K x[n-tau] stable iff K < 2 sin(pi/(2(2 tau+1)))): tau_c = 25.5. The
  Nyquist routine gives 25.500 for it. Detection: the pipeline's tau_obs
  (same CV indicator, same 50%-of-seeds rule, same grid) within 5% of
  25.5. Noise sd 0.001 p* keeps stable-side quasi-cycles well under CV 0.2.
- CHEAT: no simulation; the observable is written directly: treatment-off
  cv = 1 for tau >= ceil(tau_pred) = 23 else 0; treatment-on onset
  ceil(1.5 * 23) = 35; cheat-control on and off onset 23 (ratio 1.0).
  Detected iff the evaluator's success function returns True on it.

## Observable (spec)

cv = std(p[3000:5000]) / mean(p[3000:5000]) (population std).
indicator = cv > 0.2.
- If p is extinct over the whole window (mean 0), cv is undefined and the
  indicator is False (the literal test "CV > 0.2" is not true). Extinction
  is recorded per row (stupid explanation 2).
- If p exceeds 1e13 (null twin / positive control divergence) the run is
  stopped and marked diverged; the indicator is True (the uncapped
  trajectory grows without bound, so its CV over the window exceeds 0.2);
  cv is recorded as null.
tau_obs = smallest tau in 0..39 with indicator True in >= 50% of the 20
seeds; per arm and exhaustion setting.

## Criteria as applied (evaluate.py)

For an arm A (TREATMENT, NULL_TWIN or CHEAT) with its control:
- relerr = |tau_obs(A, off) - tau_pred| / tau_pred.
- ratio(A) = tau_obs(A, on) / tau_obs(A, off);
  ratio(control) = tau_obs(CONTROL, on) / tau_obs(CONTROL, off)
  (CHEAT uses its own injected control).
- If tau_obs(on) is undefined (no onset in the grid), it is censored at 40
  (one past the grid) as a lower bound and flagged; if tau_obs(off) is
  undefined or 0, relerr/ratio are undefined and the criterion is not met.
- success(A) = relerr <= 0.15 AND ratio(A) >= 1.3 AND
  ratio(A) - ratio(control) >= 0.1.
- failure = relerr > 0.15 OR ratio < 1.1 OR |ratio - ratio(control)| < 0.1
  OR positive control misses by > 5%. Reported; the PREREG maps any
  non-success of the treatment to NULL.
- The positive-control clause of the failure criterion is also the
  PREREG positive-control detection.

## Outcome (code, PREREG classes)

- positive control or cheat not detected -> INSTRUMENT_FAIL
- else null twin meets success -> CONFOUNDED (checked whether or not the
  treatment succeeds, since a null twin passing the criterion is a finding
  about the spec either way; it counts as NULL for the world)
- else treatment meets success -> SIGNAL
- else NULL

## Seeds

Per (arm, exhaustion, seed index s in 0..19): numpy PCG64 seeded with
SeedSequence([20260929, arm_code, exh, s]); arm codes TREATMENT=1,
CONTROL=2, NULL_TWIN=3, POSITIVE_CONTROL=4. Each seed runs all 40 taus
vectorised with one generator. Rows are written one per
(arm, exhaustion, tau, seed) -- a finer grain than (arm, seed).

## Compute

Single process, BLAS threads pinned to 1; CPU time measured with
time.process_time in both scripts and written to OUTCOME.json.

## Attempt log

(appended after runs)
- Attempt 1 (world.py, 26.2 CPU s): completed; no rerun of world.py.
- evaluate.py first invocation crashed before writing OUTCOME.json on a
  string-format bug ("50%" inside a %-formatted string); fixed to "50%%"
  and re-run on the same rows. After the result, anomaly REPORTING lines
  were added to evaluate.py (exhaustion sign, exhaustion duty cycle,
  control ratio exactly 1.0); no threshold, parameter or criterion was
  changed and world.py was not re-run.
- Observation (not a repair): under the literal exhaustion reading,
  exhaustion is on 51% of steps on average; halving a lets p rise, which
  keeps the "not fallen" counter running, so exhaustion can self-sustain.
  The onset delay fell from 23 to 8. Recorded as found.
