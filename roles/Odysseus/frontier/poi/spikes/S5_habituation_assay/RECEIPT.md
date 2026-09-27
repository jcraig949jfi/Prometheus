# Spike S5 -- a substrate-agnostic habituation assay with controls and a null

Currency: 2026-09-27. Odysseus spike worker, ubu001.
Origin: raw/E5_collective_morpho_unconventional.md PART 3 L1 (habituation floor:
LTI cannot habituate; two-timescale fading memory + static nonlinearity
suffices) and PART 2 item 2 (memory is generic in random dynamics; needs a
null of the same class).

## 1. Assay definition and thresholds (FROZEN BEFORE ANY RUN)

Written to this file before run_controls.py was executed. The same numbers
live in assay.py FROZEN; results.json records assay.py's sha256.

System interface: reset(); step(u) -> y  (u = tuple of n_inputs floats,
y = float or list of floats); get_state()/set_state(s) (or deepcopy-able).
Stimulus = pulse of amplitude AMP=1.0 for WIDTH=2 steps on one channel.

Evoked response (COUNTERFACTUAL metric): from a snapshot S at a stimulus
onset, run WINDOW=10 steps with the stimulus and, separately from the same
S, 10 steps without it. r = max_t |y_stim(t) - y_nostim(t)|. For any LTI
system this is exactly the impulse-response peak, independent of history,
so LTI can never show a decrement (a theorem, not a tuning).

Protocol (times in steps): warmup T0=200 with zero input -> snapshot S0.
 TRAIN: N=10 stimuli on channel A every ISI=10 steps -> r_1..r_N.
 SPEC:  at t_{N+1} (one ISI after stim N) probe channel B -> rB_after.
 REST:  from the post-train state, REST=300 zero steps, probe A -> r_rec.
 SHAM (same clock, no training, from S0): probe A at t_N -> r_sham_N;
        probe B at t_{N+1} -> rB_naive; probe A at t_rec -> r_sham_rec.
        (sham probes are on separate branches; each is from the
        undisturbed sham trajectory.)
 late = mean(r_{N-2}, r_{N-1}, r_N).

Gates (all thresholds fixed now):
 G0 valid: no NaN/inf, |y| < 1e6; responsive: r_1 >= 1e-6.
 H1 decrement: late / r_1 <= 0.70  AND  Kendall tau(k, r_k) <= -0.60.
 H2 stimulus-caused (anti-drift/anti-fatigue-over-time):
        r_sham_N / r_1 >= 0.80  AND  late / r_sham_N <= 0.70.
 H3 spontaneous recovery (time-matched):
        r_sham_rec > late  AND  (r_rec - late)/(r_sham_rec - late) >= 0.50.
 H4 stimulus specificity: rB_naive >= 0.10 * r_1  AND
        rB_after / rB_naive >= 0.80.
 PASS_CORE = G0 & H1 & H2 & H3   (usable on single-input engines)
 PASS_FULL = PASS_CORE & H4      (the headline verdict)

Controls and required outcomes:
 NEG   random stable LTI (orders 1-6, 2 inputs): PASS_FULL rate must be 0.
 POS   two-timescale fading memory per channel + ReLU: must PASS_FULL.
 CHEAT C1 output gain decays with time regardless of input: must fail (H2).
       C2 shared stimulus-driven fatigue (any channel depletes one output
          resource, recovers): must fail PASS_FULL (H4) -- core may pass.
       C3 irreversible per-channel depletion: must fail (H3).
       C4 downward baseline drift + LTI: must fail (H1).
 NULL  random nonlinear systems (leaky tanh nets n=2,3,4,6; leaky clipped-
       threshold nets n=2,3,4,6; random 2-variable quadratic maps). Primary
       statistic: PASS_FULL rate with readout 0 and channels (A,B)=(0,1),
       one pre-declared test per system, Wilson 95% CI. Secondary:
       best-of-k (any readout unit, either channel order) to show the
       multiple-comparisons inflation. Secondary sweep ISI in {5, 20}.
 Also reported: the naive "peak minus pre-stimulus value" metric on the
 same LTI systems, to show why the counterfactual metric is required.
