# W-A PLAN: what sets the useful delay of the M2 HOLD specimen?

Written before any engine run. Thresholds below are frozen. Model
predictions are frozen in out/predictions.json (sha256 recorded in s6
before the first engine run).

## 1 Question
The HOLD specimen 4ab2ba01 and 3 fresh champions (same physics) are
accurate at gap 6-8 and at chance for gap >= 12 (S-M2b, even gaps only).
What physically sets that interval, and can minimal alterations of physics,
program, or both move it as predicted?

## 2 Hypothesis H-ECHO (my reduction of the decompiled programs, decompile.py)
All four programs reduce to the same 3-line law plus an always-on EMIT:
  a (the only site with SENSE != 0) emits PAY_c := SENSE;
  every site emits PAY_c' := IN_c >> s  (the sum of comp c received since
  its last wake; s = 0 specimen, 4 fresh1 (c=1,c'=0), 2 fresh2, 0 fresh3);
  S0 := IN_c'  (OVERWRITTEN at every wake; no accumulation);
  c' is never relayed, so there is no recirculation: exactly two hops.
Specimen only: every wake RVAL = -1 at table index (-7168 mod R); for R=6
that is offset -1, so w[offset -1] decays 16 -> 0 over 16 wakes. This cuts
every hop-1 round trip (a -> a-1 has no weight; a+1 -> a has no weight).
fresh2/fresh3 also write routing (data-dependent, mirror-dependent); the
model treats their routing as uniform (a stated approximation).

Timing law (engine s6 order: delivery, sense, wake, run, emit):
- SENSE is seen only on a wake tick; the cue (2 ticks) is emitted once
  when update_period = 2.
- a copy at hop h arrives after d = clamp(lat_base + lat_hop*h + U{0..jitter}).
- arrivals are read at the first wake >= arrival; the relay emits then.
- the readout samples S0, i.e. the echoes that arrived in the LAST wake
  window before the readout tick.
So the round trip is RT = ceilP(d1) + ceilP(d2) (P = update_period), and
the useful interval is the SUPPORT of the echo kernel K(RT) (from routing,
hop distances, latency, jitter and P), shrunk by the distractor echoes
that share the readout window (SNR). The readout lag of the cue emission
is gap+2 or gap (alternating trial parity for even gaps, since the trial
period gap+5 is odd) and gap+1 for odd gaps.

Base-physics kernel (expected returning copies per unit payload, by RT):
  fresh1-3 (uniform): RT 4:0.72  6:1.44  8:4.32  10:1.44  12:0.72
  specimen:           RT 4:0     6:0     8:5.18  10:2.07  12:1.04
Qualitative predictions that follow before any simulation:
- P-a: nothing is held beyond RT_max = 12 ticks: accuracy at chance for
  readout lags > 12, whatever the SNR (amp_dist 0 included).
- P-b: sawtooth: odd gaps read lag gap+1 in every trial, so gap 7 (lag 8,
  the kernel peak) beats gap 8 (lags 8 and 10); gap 9 (lag 10) is below 8.
- P-c: the specimen, which lacks RT 4 and 6, is worse than fresh1-3 at
  short gaps (<= 5) and restoring uniform routing (plastic_route 0)
  lifts it there.
- P-d: +1 lat_base adds 1 per hop, which with P = 2 moves RT by 0 or +2 per
  hop; the interval moves later. lat_base 0 moves it earlier.
- P-e: a one-wake pipeline register at a (S0 := S1; S1 := echo; 2 field
  edits) shifts the whole curve by exactly +P = +2 gap units; combined
  with lat_base 0 the two shifts partly cancel.
- P-f: all four champions are one mechanism: the canonical 4-line echo
  genome (conditions.canon) reproduces the base curves (uniform ~ fresh3,
  specimen-route ~ specimen).

## 3 Reduced model (echo_model.py, no fitted parameters)
Particle Monte Carlo of the two-hop echo only (actuator -> neighbours ->
actuator) with the engine's delay, loss, fanout, routing, sync wake and
(primary) cap/saturate with Poisson background traffic from the physics.
Secondary: the same without saturation. 4000 simulated worlds per point.

## 4 Experiments (engine, CPU 2 threads, namespace 0x5E4, 64 worlds =
32 mirror pairs, 99% pair bootstrap; gaps 2..16, every integer)
Conditions x champions (conditions.py):
  base | lb0 lat_base 0 | lb2 lat_base 2 | lh2 lat_hop 2 | j0 jitter 0 |
  j2 jitter 2 | up1 update_period 1 | up3 update_period 3 | r2 radius 2 |
  pr0 plastic_route 0 | ad0 amp_dist 0 (env)   -- all 4 champions
  pipe, pipe_lb0 -- specimen and fresh3 (2 field edits)
  canon uniform / canon specimen -- minimal genomes
Every non-base physics is one the champions never saw.

## 5 Decision rules (frozen)
Per (condition, champion) curve, measured m(g) vs primary prediction p(g):
- FIT if MAE over g = 2..16 <= 0.07.
- INTERVAL = gaps with accuracy >= 0.65; INTERVAL-HOLDS if its min and max
  are each predicted within +-1 gap (both empty also holds).
- Gold standard: the reduced model PREDICTS if >= 75% of the non-base
  (condition, champion) curves are FIT and INTERVAL-HOLDS; PARTIAL if
  >= 50%; FAILS otherwise.
- A minimal alteration MOVES the interval if the measured INTERVAL's max
  (or min) shifts by >= 2 gaps vs base in the predicted direction and its
  endpoints match prediction +-1.
- P-a holds if every ad0 curve has lo99 <= 0.55 at every gap whose lags
  exceed RT_max = 12 (gaps >= 13: odd 13 reads lag 14, even 14 reads 14/16).
- P-b holds if acc(7) > acc(8) > acc(9) in >= 3/4 champions (base).
- P-c holds if specimen acc at gaps 2..5 is below every fresh champion's
  mean over the same gaps AND pr0 raises the specimen's mean there by >= 0.05.
- P-e holds if the pipe curve's argmax and interval endpoints are the base
  ones + 2 (+-1) for both genomes.
- P-f holds if canon curves are FIT against the measured base curve of
  fresh3 (uniform) and of the specimen (specimen-route).
If the evidence contradicts H-ECHO or the brief's framing, REPORT says so.

## 6 Frozen artefacts
(filled in just before the first engine run)
- out/predictions.json sha256 ccb51dc23248fbdb387ea055477d8b5782f5ea46e8c392d805c4b04929881079 (primary = "sat", secondary = "nosat";
  written 2026-09-27 before any engine run of this worker).
- echo_model.py / conditions.py sha256[:16]: 1000fbb7efb4451a 5f8b8ee3193b1e0e 
- Base-physics predictions are a calibration check only (S-M2b even-gap
  data were seen before the model was written; no parameter was fitted).

## 7 Addendum (written before running it): A5 engine-measured echo kernel
Single-cue twins (as spikes/s_f.py): the twin negates only trial 5's cue.
Record at the actuator the signed pair difference of component c' arriving
per tick, times the lead's cue sign, binned by read wake minus cue wake.
Prediction: normalized kernel matches echo_model.kernel (base physics):
specimen support {8,10,12} with zero mass at 4 and 6; fresh1 support
{4..12} with mode 8. HOLDS if support matches and total-variation
distance <= 0.15. fresh2/fresh3 are reported but expected contaminated
(their routing writes depend on SENSE sign, so twins also differ in routing).
