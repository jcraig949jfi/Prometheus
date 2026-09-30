# HT-a9e2ba7618 / W4 -- implementation notes (written before any run)

Prompt: hecate/programs/_prompts/probe_impl_v1.md (sha256 cf4bd374...bcea2).
Bound by roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.
Spec source: program.json experiment W4, mechanism M5, lens L5 (read only).

## Spec field -> code

- hypothesis: carrier-relative phase decoding is warp-invariant only when the
  carrier is co-warped with the message. Tested by comparing TREATMENT
  (co-warped carrier) with NULL_TWIN (unwarped carrier, warped message), both
  decoded by the same carrier-phase decoder.
- mechanism (M5): `world.py::make_transmission` builds a 6 Hz carrier (f0 = 6.0
  Hz, period T = 1/6 s). One slow cycle = one carrier cycle. Each cycle carries
  one symbol s in {0..4}, emitted as a single pulse at the centre of phase slot
  s, i.e. at carrier phase 2*pi*(s+0.5)/5. The transmission (carrier and pulse
  train) is sent through a random piecewise-linear monotone time warp g of
  strength w. `decode_carrier_phase` computes a complex Morlet CWT (w0 = 6) of
  the received carrier over 40 log-spaced frequencies 3-15 Hz, takes at every
  sample the scale of maximal |W| (adaptive-scale ridge), reads the ridge phase
  at each received pulse time, and assigns slot floor(5*phase/2pi).
- intervention: w in {0, 0.1, 0.2, 0.4}.
- control: `decode_clock` -- slot = min(4, floor(elapsed / (T/5))), where
  elapsed = received pulse time minus the received onset of that cycle. The
  onset is given to the decoder exactly (oracle, i.e. g(k*T)); see ambiguity A3.
- positive_control: separate seeds, w = 0 only; detected iff mean accuracy over
  seeds of BOTH decoders >= 0.98.
- null_twin: same message, same warp, same pulse times as the treatment, but the
  carrier is generated unwarped in received time: cos(2*pi*f0*t). Same carrier
  spectrum at w=0, same symbol counts; co-moving reference destroyed. Decoded by
  the same carrier-phase decoder.
- observable: symbol decoding accuracy = fraction of the 200 x 20 = 4000 symbols
  per (seed, w) whose decoded slot equals the transmitted slot.
- success_criterion (applied exactly, statistic = mean over the 10 seeds of
  per-seed accuracy):
  acc_T(0.4) >= 0.9 AND acc_T(0) - acc_T(0.4) <= 0.05 AND
  acc_C(0) - acc_C(0.4) >= 0.3 AND acc_N(0) - acc_N(0.4) >= 0.3.
- failure_criterion: acc_T(0) - acc_T(0.4) > 0.1, OR null twin shows the same
  invariance, read as acc_N(0.4) >= 0.9 AND acc_N(0) - acc_N(0.4) <= 0.05
  (the treatment's invariance clause applied to the null twin). This same
  predicate is `null_twin_meets_success` (PREREG CONFOUNDED).
- CHEAT arm: decoding is bypassed; the observable is written directly: carrier
  arm decoded = truth at every w; clock and null-twin decoded = truth at w=0 and
  uniform random symbols at w>0. Detected iff the evaluator's success predicate
  is True on the CHEAT values.

## Outcome logic (evaluate.py, in code, PREREG classes)
1. PC or CHEAT not detected -> INSTRUMENT_FAIL.
2. null_twin_meets_success -> CONFOUNDED.
3. success predicate True and failure predicate False -> SIGNAL.
4. otherwise -> NULL.

## Ambiguities and readings chosen
- A1 "5 symbols per slow cycle": read as a 5-letter alphabet coded by 5 phase
  slots, one symbol (pulse) per slow cycle. Reason: if five items filled five
  slots every cycle there would be no information to decode. Consequence: order
  within a cycle carries no information (relevant to stupid explanation 1).
- A2 "slow cycle" vs "6 Hz-like carrier": slow cycle = one carrier cycle.
- A3 clock decoder's "cycle onset": the true received onset of each cycle is
  given (oracle). This is the most generous reading; errors then come only from
  within-cycle tempo change, not from accumulated drift.
- A4 "random piecewise-linear monotone map of strength w": knots in source time
  at intervals drawn Uniform[0.5, 1.5]*T; slope on each segment = 1 + w*u,
  u ~ Uniform[-1, 1] (slopes in [0.6, 1.4] at w=0.4, always monotone, cannot
  fold cycles -- L5 failure mode excluded by construction). Received time
  t = g(tau). The same warp family is used in all arms.
- A5 edges: the carrier runs 2 cycles before and 2 after the 20 message cycles
  (source time [-2T, 22T]) so CWT edge effects do not fall on message cycles.
- A6 "10 seeds" x "200 sequences": 10 seeds per arm; each seed generates 200
  sequences of 20 cycles for each w. Rows: one per (arm, seed) holding the
  accuracy at each w.
- A7 "drop" = accuracy(w=0) - accuracy(w=0.4), same seed set, arm means.
- A8 statistic = mean over seeds (n=10 seeds, 4000 symbols each).

## Parameters (fixed from spec or convention, not from results)
- f0 = 6.0 Hz (spec), 5 slots (spec), 20 cycles, 200 sequences, 10 seeds, w
  levels (spec).
- fs = 200 Hz (>> 2 x 15 Hz; pulse slot width 33 ms = 6.7 samples).
- carrier amplitude 1, additive Gaussian noise sd 0.1 (spec silent; small noise
  so w=0 is not a noiseless tautology).
- Morlet w0 = 6 (standard), 40 log-spaced frequencies 3-15 Hz (covers local
  frequency 6/1.4..6/0.6 = 4.3..10 Hz with margin).
- Pulse at slot centre (no jitter; spec silent, least invented choice).

## Seeds
TREATMENT/CONTROL/NULL_TWIN share data: seed s in 0..9, rng =
default_rng([4, s, w_index]). POSITIVE_CONTROL: seeds 100..109. CHEAT: seeds
200..209 (random symbols only).

## Stupid explanations: planned handling
1. order decoder invariance: one symbol per cycle (A1), so order carries no
   slot information; null twin preserves pulse order and is decoded by the same
   decoder.
2. warps too weak: CONTROL's error rate directly measures how often a warp moves
   a pulse across a clock slot boundary; also logged as frac_boundary_crossed.
3. decoder overfits warp family: NOT addressed; only one warp family is run.

## Compute
Single-threaded numpy (thread env vars set to 1). CPU time measured with
time.process_time and written cumulatively into each row. Budget 10 core-min.
Attempts are counted in `ATTEMPT` inside world.py.

## Attempt log
(appended below after runs)

- Attempt 1 (2026-09-29): world.py ran to completion, no crash, no bug found;
  0.50 CPU core-minutes (process_time). evaluate.py -> NULL. PC and CHEAT
  detected. No parameter changed after the run; no rerun.
  Treatment acc 1.000/1.000/0.993/0.875 (w=0/0.1/0.2/0.4), drop 0.125 > 0.1
  (failure clause met). Clock 1.000/1.000/0.934/0.713, drop 0.287 (< 0.3).
  Null twin 1.000/0.412/0.242/0.205, drop 0.796.
