# HT-a9e2ba7618 / W3 -- implementation notes (written before any code ran)

Prompt: hecate/programs/_prompts/probe_impl_v2.md (sha256 2021ed66...185e).
Bound by round-2 PREREG (control-first pilot) and round-1 PREREG.
Spec read: experiment W3, mechanisms M3, M12, lens L2 only.

## Spec field -> code (core.py holds shared primitives; no treatment arm in phase 1)

| spec field | code |
|---|---|
| 1D signal n=1024, 3 localized objects, different widths | `core.make_objects`: plateaus of amplitude 1.0 with 8-sample cosine tapers; widths drawn per seed from U[40,70], U[90,140], U[160,240] (non-dyadic ranges, order shuffled), random non-overlapping positions |
| 1/f noise | `core.pink_noise`: white FFT noise shaped to power ~ 1/f (f=0 removed), rescaled to std SIGMA_NOISE = 0.5 |
| 6 dyadic scales, scalogram (L2) | `core.scale_stack`: a trous (undecimated) B3-spline wavelet transform, smoothing planes c_j for j=1..6 (dyadic hole spacing 2^(j-1)), mirror boundaries |
| superlevel component per scale | `core.components`: contiguous runs of {c_j > TAU}, TAU = 0.5 (half the object amplitude) |
| 64 oscillators on a location grid | oscillator i at x_i = 8 + 16 i |
| edge if same superlevel component at >= k=3 of 6 scales | `core.cross_scale_graph` (K_SCALES = 3) |
| single-scale rule (twin / null twin) | `core.single_scale_graph`: edge iff same component at the finest scale j=1 |
| matched edge count | `core.match_edge_count`: random edges removed / random non-edges added until edge count equals the cross-scale graph on the SAME signal |
| Kuramoto 2000 steps | `core.kuramoto`: RK4, dt=0.1, 2000 steps, dtheta_i = w_i + (KC/deg_i) sum_j A_ij sin(theta_j-theta_i), KC=5.0, w_i ~ N(0,1), theta0 ~ U[0,2pi) |
| clusters by PLV > 0.9 | PLV over the last 1000 steps; clusters = connected components of the graph {PLV_ij > 0.9} |
| ARI vs ground truth | sklearn adjusted_rand_score |
| ARI of plain connected components of the coupling graph | same, labels = connected components of A |
| positive_control: noise-free, well-separated, ARI >= 0.95 | arm POSITIVE_CONTROL: noise-free signal, gaps between objects >= 128 and margins >= 64, cross-scale rule + oscillators |
| cheat control (round-1 PREREG) | arm CHEAT: cluster labels := ground-truth labels (success injected into the observable) |
| null_twin | arm NULL_TWIN: noisy signal (same generator as treatment), single-scale rule, edge count matched to the cross-scale graph on that signal, oscillators |
| intervention (phase 2) | TREATMENT: noisy signal, cross-scale rule; the "matched single-scale twin" of the success criterion is the NULL_TWIN arm on the same seed (paired) |
| control (phase 2) | CONTROL: phase-randomized surrogate of the noisy signal (FFT amplitudes kept, phases uniform, Hermitian), cross-scale rule, ground truth = original objects |

## Ambiguities and chosen readings

1. "Scalogram |W(s,t)|". A band-pass |W| of a plateau is high only near its
   edges at scales below the object width, so an object interior is one
   superlevel component only at scales >= its width. With widths 40-240 in
   1024 samples, no object could be one component at >= 3 dyadic scales
   before objects merge, so M3's own statement ("true objects persist across
   >= k scales", L2 predicted signal) would be false by construction. Chosen
   reading: the smoothing (scaling-coefficient) planes of the a trous wavelet
   transform, i.e. the low-pass part of the wavelet stack. Consequence: the
   spec's alternative explanation ("coarse scales simply smooth noise; any
   low-pass filter would do") is maximally live in this build and is NOT
   ruled out by it. Chosen by argument before running, not by trial.
2. Superlevel threshold is unspecified: TAU = 0.5 fixed (half the known
   object amplitude), same for all scales and arms.
3. Ground truth for locations outside every object: each such oscillator is
   its own singleton class (nothing should bind it). An oscillator is inside
   object m iff the object envelope at x_i > 0.5.
4. Null twin "degree-matched rewiring: same edge count and degree
   distribution". A single-scale graph cannot in general be given the
   cross-scale graph's exact degree sequence while remaining a single-scale
   graph; implemented: exact edge-count match by random removal/addition
   (the intervention's wording). Degree distribution is NOT matched; the
   degree histograms of both graphs are written to the rows so the gap is
   visible. The null twin and the "matched single-scale twin" are one arm.
5. The null twin needs the cross-scale graph's EDGE COUNT on the noisy
   signal. Only that integer is computed in phase 1; no treatment ARI,
   cluster or dynamics exists in phase 1.
6. "Positive control meets the spec's success criterion": the spec gives the
   positive control its own criterion, median ARI(oscillators) >= 0.95 over
   seeds (stricter than the absolute 0.7 part). The relative parts (gap to
   twin, oscillators vs components) are statements about the treatment and
   are not applied to controls.
7. "Null twin meets success": median ARI(oscillators) >= 0.7 (the absolute,
   single-arm part; the gap-to-twin part is vacuous for the twin itself).
   This is the conservative reading (easiest for the twin to count as
   confounding).
8. Cheat detected iff the evaluator reports median ARI(cheat) >= 0.7 and
   >= 0.95 (it sees success).
9. Success criterion (phase 2), all medians over the 50 seeds:
   median ARI_osc(T) >= 0.7 AND median paired diff ARI_osc(T)-ARI_osc(twin)
   >= 0.2 with one-sided paired Wilcoxon p < 0.01 AND
   median ARI_osc(T) > median ARI_comp(T) + 0.02.
   Failure criterion: median paired gap < 0.1 OR median ARI_osc(T) <=
   median ARI_comp(T) + 0.02. Outcome decided in evaluate.py by PREREG
   classes; a result meeting neither success nor failure is NULL (round-1:
   "treatment fails the criterion").
10. Coupling normalized by degree so that clique size does not set the
    locking condition; KC=5 chosen so KC > typical spread of N(0,1) natural
    frequencies in a clique; uncoupled pair spurious PLV>0.9 needs
    |dw| < ~0.016 over T=100 (about 0.9% of pairs) -- a known, untuned
    source of false merges, identical across arms.

## Parameters (from the spec or fixed a priori above; frozen)

N=1024, N_OSC=64, N_SCALES=6, K_SCALES=3, TAU=0.5, SIGMA_NOISE=0.5,
KC=5.0, DT=0.1, STEPS=2000, PLV_WINDOW=1000, PLV_THR=0.9, SEEDS=0..49 (50).

## Seeds

Per seed s: noisy-signal rng 1000+s, natural frequencies / initial phases
rng 2000+s (same for every arm on seed s), twin edge-matching rng 3000+s,
surrogate phases rng 4000+s, positive-control signal rng 5000+s.

## Pilot log

(appended below after running)

### Attempt 1 (FAILED)
positive median ARI_osc 0.904 (< 0.95; graph components ARI 1.0), cheat
1.0 detected, null twin 0.057 (does not meet). Diagnosis on the positive
control only (15 seeds): no object ever split; errors are all uncoupled
oscillators reading PLV > 0.9 by coincidence of natural frequencies
(~5 background pairs per seed, 1-2 background units joining an object).
With w ~ N(0,1) and T=100 the pairwise coincidence rate is ~0.9% of ~2000
pairs -- the readout, not the graph, fails. Files kept as
PILOT_attempt1.json, pilot_rows_attempt1.jsonl.

### Repair (the one allowed; controls/readout only, thresholds unchanged)
Applies identically to every arm (one readout code path). Chosen by the
analytic argument below, not by trial runs:
- natural frequencies: a seeded random permutation of linspace(-1,1,64)
  (min spacing 0.0317) instead of N(0,1) draws, so no two uncoupled units
  can be closer than the grid spacing;
- PLV window: last 1800 of the 2000 steps (was 1000);
- DT = 0.75, KC = 1.6: RK4 stability needs 2*KC*DT < 2.78 (2-cliques are
  the stiffest case, 2*1.6*0.75 = 2.4); KC = 1.6 > 1.27 (locking bound for
  uniform frequencies on [-1,1]) and >= 1 (2-clique bound).
Window T = 1350: two uncoupled grid neighbours have PLV ~ |sinc(21)| << 0.9;
a background unit still reads locked to an object cluster if its frequency
is within ~0.0012 of the cluster mean (~7% per object) -- this residual
false-binding rate is left as is.
PLV_THR 0.9, ARI 0.95 / 0.7 / 0.2 / 0.02, p < 0.01, k=3, TAU unchanged.

### Attempt 2 (PASSED)
positive median ARI_osc 1.0 (q10 0.93), cheat 1.0, null twin 0.167
(< 0.7). Parameters frozen from here; phase 2 begins (world.py).

## Phase 2 result (evaluate.py, no changes after running)
NULL. Treatment median ARI_osc 0.789 (>= 0.7), paired gap to twin 0.569
(Wilcoxon p 5.6e-10) -- but median ARI_osc - ARI_comp = 0.0 (graph
components 0.804): the failure criterion's second clause fires; the
oscillators add nothing over reading the coupling graph's components.
CONTROL (surrogate) 0.083. Total ~0.9 core-minutes.
