# HT-faa9277e02 / W2 -- implementation notes (written before any run)

Prompt: hecate/programs/_prompts/probe_impl_v1.md (sha256 cf4bd374...133bcea2).
Bound by roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.
Spec read: experiment W2, mechanisms M3, M15, lens L2 only.

## World (spec "mechanism")

- 100 cells, integer position x in {0..99}, drawn uniformly (prior p(x)=1/100).
- Noiseless gradients c1 = exp(-x/20), c2 = exp(-(100-x)/20).
- Multiplicative noise sigma=0.3. READING: lognormal, one sample is
  c * exp(0.3*xi), xi ~ N(0,1), independent per gradient and per sample
  (keeps concentrations positive, so log-concentration is defined).
- Integration time T: the readout sees the arithmetic mean of T independent
  noisy samples of each gradient, c_bar. Input vector to every readout is
  u = (log c1_bar, log c2_bar) (log-concentration space, which the spec's
  control uses).
- T in {1,2,4,8,16,32}. Each (seed, T) has its own 20000-sample training set
  and 50000-sample test set; the SAME test set (common random numbers) is used
  for every arm at that (seed, T).

## Arms

- TREATMENT (spec "intervention", M3/M15): K=8 readout units with prototype
  weight vectors w_k in the 2-D input space. READING of "winner-take-most":
  soft competition y_k = softmax_k(-|u-w_k|^2 / (2*s^2)) with s = 0.3 (the
  spec's noise sigma; fixed, not tuned). READING of "Hebbian with Oja decay":
  literal Oja form applied per unit, dw_k = eta * y_k * (u - y_k * w_k).
  Online, one pass over the 20000 training samples in order.
  eta decays geometrically from 0.05 to 0.001 over the pass (standard online
  schedule, chosen a priori). Init: w_k = 8 distinct random training inputs.
  Test readout r = argmin_k |u - w_k| (the winner), r in {0..7}.
  Trained separately at each T on T-averaged inputs.
- CONTROL (spec "control"): uniform fixed quantizer, 8 bins evenly spaced in
  log-concentration space. READING: the 1-D log-ratio coordinate
  z = log c2_bar - log c1_bar (noiseless range z(0)=-5 to z(99)=+4.9);
  8 equal-width bins over [z(0), z(99)], values outside clipped to end bins.
- NULL_TWIN (spec "null_twin"): same nearest-prototype readout, K=8, but the
  8 centres are drawn at random from the input range instead of learned.
  READING of "input range": centre = noiseless input u(x*) at x* ~ U[0,99]
  (continuous), i.e. uniform along the input manifold. "Same widths": same
  nearest-centre (s=0.3 competition) readout rule. No learning.
- POSITIVE_CONTROL (spec "positive_control"): Bayesian decoder with the known
  noise model, restricted to K=8 outputs. READING: posterior p(x|u) over the
  100 cells from the known model; output = argmax of posterior mass over the
  8 position classes floor(8x/100). Noise model for the T-average: exact
  lognormal at T=1; for T>1 the Fenton-Wilkinson lognormal approximation of a
  mean of T iid lognormals (sigma_T^2 = ln(1+(e^{0.09}-1)/T), mean preserved).
  This is the "optimal-decoder bits (restricted to K=8 outputs)" reference
  used in the ratio. It is a strong reference, not a proven upper bound on
  8-output MI.
- CHEAT: bypasses the mechanism and writes the observable directly:
  bits(T) = 0.9 * PC_bits(seed, T=1) + 0.5*log2(T). It exists only to show
  the evaluator registers success. It can exceed log2(8)=3 bits, which no
  real 8-output readout can; the evaluator flags that as an anomaly.

## Observable (spec "observable", lens L2)

I(x; r) in bits from the 100 x 8 joint count table over 50000 test samples:
plug-in entropies with Miller-Madow correction, H_MM = H_plugin + (m-1)/(2N ln2)
bits (m = occupied cells), I = H_MM(x) + H_MM(r) - H_MM(x,r). Plug-in value and
occupied-bin counts are also recorded (stupid explanation 1).

## Criteria (thresholds as written, readings recorded)

Statistic per seed: bits at each T; slope = OLS slope of bits vs log2 T over
T in {1,2,4,8}.

SUCCESS (spec): READING: "for 10 seeds" = each clause must hold in every one of
the 10 seeds:
  (a) Hebb bits(T=1) >= 0.8 * PC bits(T=1)   [same seed]
  (b) Hebb bits(T=1) - NULL_TWIN bits(T=1) >= 0.5
  (c) 0.3 <= Hebb slope <= 0.7
FAILURE (spec): READING: on seed means,
  mean Hebb bits(T=1) <= mean CONTROL bits(T=1) + 0.1, OR
  mean Hebb slope outside [0.15, 0.85].
Treatment is NULL if success is not met or failure is met.

null_twin_meets_success: clauses (a) and (c) applied to NULL_TWIN in every
seed (clause (b) is self-referential for the twin and is omitted).
positive_control_detected: PC bits(T=1) - NULL_TWIN bits(T=1) >= 0.5 in every
seed (the instrument can resolve a margin of the size clause (b) demands;
clause (a) is identically 1.0 for the PC; the slope clause is not a claim the
bound makes).
cheat_detected: CHEAT row values pass (a), (b), (c) in every seed.

Outcome, in code, per PREREG: INSTRUMENT_FAIL if PC or CHEAT not detected;
else CONFOUNDED if null_twin_meets_success; else SIGNAL if treatment success
and not failure; else NULL.

Also reported (not deciding): CONTROL slope (stupid explanation 3: the log law
from averaging without Hebb), ceiling check (bits at T=16,32), attainability
of (a)+(c) jointly under the 3-bit cap.

## Seeds, sizes, compute

Seeds 0..9 (spec: 10 seeds). RNG: numpy default_rng(SeedSequence([20260929,
seed, T, stream])) with stream 0=train data, 1=test data, 2=init, 3=null centres.
Sizes: 20000 train / 50000 test / 6 T values / 10 seeds, as spec. Estimated
well under 10 core-minutes; measured with time.process_time and recorded.
No parameter above depends on any result.

## Attempt log (appended after attempt 1)

Attempt 1 (0.54 core-min): evaluator returned INSTRUMENT_FAIL. PC not
detected (PC - NULL_TWIN at T=1 = 0.23 bits < 0.5 in every seed) and CHEAT not
detected. Attempt-1 files kept as attempt1_rows.jsonl / attempt1_OUTCOME.json /
attempt1_run_meta.json.

ONE INSTRUMENT REPAIR (per the prompt's rule), CHEAT only: the attempt-1 injection
bits(T) = 0.9*PC(T=1) + 0.5*log2 T ignored clause (b), so it sat ~0.005 bits
above the null twin and could not register success. This was a construction bug
in the cheat, independent of the treatment. Repaired injection:
bits(T) = max(0.9*PC(T=1), NULL_TWIN(T=1)+0.6) + 0.5*log2 T, which satisfies
(a), (b), (c) by construction. No threshold, parameter, arm definition, reading,
or the PC-detection rule was changed. The PC non-detection is left as is: it
follows from the spec (random centres along the manifold already reach ~90% of
the 8-class Bayes bits, so no readout can beat the twin by 0.5 bits), and is not
an instrument bug I can repair without redefining the spec's null twin.
Attempt 2 reruns everything once.
