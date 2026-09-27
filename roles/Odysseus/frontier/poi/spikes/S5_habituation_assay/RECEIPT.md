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

## 2. Run

Command: `python3 roles/Odysseus/frontier/poi/spikes/S5_habituation_assay/run_controls.py results.json`
(run from inside the spike dir; 141 s, stdlib, Python 3.14.4, ubu001).
Seeds: LTI 20260927, positive family 7, cheats 99, null 314159, ISI sweep 271828.
Rows: results.json beside this file (includes assay.py sha256 and FROZEN).
No threshold was changed after the run.

## 3. Control outcomes (all required outcomes met)

NEGATIVE, random stable LTI (1000; half dense, half diagonal with
separated timescales 1 to ~300 steps):
 - counterfactual metric: PASS_FULL 0/1000, PASS_CORE 0/1000, H1 0/1000
   (Wilson 95% upper bound 0.38%). Max |late/r_1 - 1| = 6.7e-15, i.e. the
   theorem holds numerically: evoked response is history-independent.
 - naive prestim metric on the SAME systems: PASS_FULL 37/1000 = 3.7%
   [2.7%, 5.1%]. The naive "peak minus pre-stimulus value" readout lets
   the decaying tail of earlier responses masquerade as habituation. The
   counterfactual (snapshot) metric is therefore mandatory, not cosmetic.

POSITIVE, two-timescale fading memory + ReLU (tau_f=5, tau_s=100,
gf=0.15, gs=0.04): PASS_FULL. late/r_1=0.53, Kendall tau=-1.0, sham
ratio 1.0, recovery fraction 0.95, specificity 1.00.
 - Randomized family (200; tau_f 2-8, tau_s 50-200, gf 0.05-0.3,
   gs 0.02-0.08): 181/200 = 90.5% [85.6%, 93.8%] pass. All 19 misses are
   weak-slow-gain members (gs ~0.02-0.03) with late/r_1 = 0.71-0.76, just
   above the 0.70 cut: the assay is conservative, not wrong.
 - Ablations: slow-only memory + ReLU also PASSES (late/r_1 0.37);
   fast-only memory (tau_f=5 < ISI) FAILS H1 (0.90). So the gated hallmarks
   (decrement, recovery, specificity) need ONE memory slower than the ISI
   plus a nonlinearity; they do NOT certify two timescales. The secondary
   rate-sensitivity diagnostic (not a gate) separates them only weakly:
   canonical recovers faster after short-ISI training (0.69 vs 0.61),
   slow-only does not (0.56 vs 0.60).

CHEATS (all fail PASS_FULL):
 - C1 gain decays with time (50 instances): H1 passes 50/50 (the decrement
   is real) but H2 fails 50/50 (sham shows the same decline). 0 pass.
 - C2 shared stimulus-driven fatigue: passes CORE (H1,H2,H3) but fails H4
   (spec_ratio 0.49 < 0.80). This is the designed behaviour: without a
   second channel, fatigue and habituation are indistinguishable.
 - C3 irreversible per-channel depletion: fails H3 (recovery fraction -0.11).
 - C4 input-blind baseline drift + LTI (50): fails H1 50/50 (the
   counterfactual cancels drift).

## 4. NULL -- base rate of random nonlinear systems passing

Classes: leaky tanh nets and leaky clipped-threshold nets, n = 2,3,4,6,
500 each (leak rates log-uniform [0.005, 1], gain 0.5-3, random input and
bias); random 2-variable quadratic maps, 1000 (262 diverged, excluded).
Valid 4738; responsive (r_1 >= 1e-6) 3871.

 PRIMARY (one pre-declared test per system, readout 0, A=0, B=1):
   PASS_FULL 12/4738 = 0.25%  Wilson 95% CI [0.15%, 0.44%]
   (among responsive: 0.31% [0.18%, 0.54%])
 PASS_CORE (no specificity gate): 44/4738 = 0.93% [0.69%, 1.24%]
 BEST-OF-k (any unit as readout, either channel order; k = 2n, up to 12):
   105/4738 = 2.2% [1.8%, 2.7%]; worst class thresh_n6 37/500 = 7.4%.
 Per class primary: tanh 0/1/0/3, thresh 1/3/2/2 (n=2/3/4/6, of 500),
   quadmap 0/738.
 By net timescale spread (max/min leak): <10: 0.22%, 10-100: 0.40%,
   >=100: 0/344 (upper bound 1.1%).
 ISI sweep (1200 nets each): ISI=5 0.75% [0.40%, 1.4%]; ISI=20 0.33%.
 Most random passers are marginal (late/r_1 0.60-0.70).

Reading: with a single pre-declared stimulus/readout pair, random small
nonlinear systems pass about 1 in 400. Searching over readouts or channel
pairs inflates this roughly linearly in the number of tests (x9 here), so
the E5 warning about "memory is generic" is real but only bites under
search. Dropping specificity (single-input engines) raises the rate ~4x.

## 5. What an engine must expose to be assayed

 1. A scalar (or vector) response readout per step, chosen BEFORE testing.
 2. At least one stimulus channel it can inject a fixed pulse into; TWO
    distinct channels for the full verdict (H4). One channel -> CORE only,
    which cannot distinguish habituation from shared fatigue.
 3. Deterministic snapshot/restore of the full world state (including RNG
    state), so the counterfactual no-stimulus branch can be run. Without
    it the fallback is a sham run per probe, and the naive prestim metric
    must not be used (3.7% false-positive rate on pure LTI).
 4. A notion of "rest" (zero/neutral input) and a clock of at least
    T0 + N*ISI + REST + WINDOW = 610 steps at the default protocol; ISI
    and REST must be rescaled to the engine's own relaxation times and the
    rescaling declared before testing.
 5. A reporting rule: state the number of readout/channel pairs searched;
    compare the pass count to k x base rate (0.25% FULL, 0.93% CORE per
    test for the null classes here), or better, run the same assay on
    random systems of the engine's own class (shuffled rules/weights).

## 6. Limits

 - Null classes are small (<= 6 units) synthetic nets and maps; the base
   rate for a Prometheus world class must be re-measured on randomized
   instances of that class. 0.25% is a reference, not a universal null.
 - Deterministic systems only; noisy engines need repeated trials and a
   variance-aware version of the ratios (not built).
 - Gates certify decrement + stimulus-caused + recovery + specificity
   (Thompson-Spencer 1, 2, 7-ish specificity). Not tested: dishabituation
   by a novel strong stimulus, habituation-of-dishabituation, below-zero
   habituation, intensity dependence. Rate sensitivity is only a
   diagnostic and the gates do not certify two timescales (slow-only
   ablation passes).
 - Thresholds (0.70/0.80/0.50) are conventional; ~10% of genuine weak
   habituators sit just above the decrement cut, and most random passers
   sit just below it. An effect-size margin would trade sensitivity for
   specificity.
 - Protocol timescales (ISI 10, REST 300) are fixed in steps; a system
   whose memory is much slower than REST fails H3 by design.
 - Divergent systems (26% of quadratic maps) were excluded from the
   denominator.

## 7. Verdict

Fit to hand to engine owners as v0, with requirement 3 (snapshot/restore)
and requirement 5 (declared search size vs base rate) as non-negotiable.
