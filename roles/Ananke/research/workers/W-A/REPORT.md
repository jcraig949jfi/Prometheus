# W-A REPORT: what sets the useful delay of the M2 HOLD specimen

(Saved by Ananke from W-A's final message; the harness refused the
worker's write (LOG A9). CPU only, 2 threads; a cpu8 lease held ~5 min and
released; no GPU; no evolution. Files in this directory: PLAN.md (frozen
rules; predictions sha256 ccb51dc2... in s6), LOG.md (A0-A9), decompile.py,
echo_model.py, conditions.py, predict_all.py, run_engine.py,
kernel_engine.py, evaluate.py, null_check.py (post hoc),
out/{predictions,engine,kernel_engine,evaluation}.json.)

## 1 Mechanism (decompiled, then tested)
All four champions reduce to the same three-line law, with EMIT always on:
- the actuator a sends PAY_c := SENSE;
- every site relays PAY_c' := IN_c >> s (s = 0 specimen, 4 fresh1 [c=1,
  c'=0], 2 fresh2, 0 fresh3);
- S0 := IN_c', overwritten at every wake.
Component c' is never relayed, so the bit makes EXACTLY TWO HOPS (a ->
neighbour -> a). There is no recirculation and no accumulation; the readout
SAMPLES the echo that arrived in the last wake window.
The specimen's ROUTING WRITE cuts short round trips: every wake it writes
RVAL=-1 at table index (-7168 mod 6)=2 (offset -1). That neighbour's
weight goes 16 -> 0 within 16 wakes, which deletes every hop-1 round trip.
The engine-measured kernel confirms zero echo mass at RT 4 and 6 for the
specimen.
Interval law: RT = ceil_P(d1) + ceil_P(d2), where d = lat_base +
lat_hop*h + U{0..jitter} and P = update_period. h ranges over the hop
distances routing allows. SENSE is seen only on wake ticks. The readout
reads cue lag gap or gap+2 alternating for even gaps, and gap+1 for odd
gaps. The useful interval is the support of the echo kernel K(RT): at base
physics RT 4-12 (fresh1-3) and 8-12 (specimen). Distractors lower the
accuracy level but do not set the edges.
Checks:
- canonical genome: 4 lines + the specimen's 2 routing lines reproduce
  base:4ab2ba01 exactly at all 15 gaps. Without the routing lines it equals
  the specimen and fresh3 exactly under plastic_route 0; fresh1/2 differ
  by <= 0.004 MAE.
- engine-measured kernel (single-cue twins) vs the model kernel: TV 0.05
  (specimen) and 0.07 (fresh1).
- fresh2 and fresh3 have extra mass at RT 10-12 (TV 0.27 / 0.20): their
  routing writes depend on the sense sign and bias traffic toward long
  hops. Same mechanism, different kernel weights.

## 2 Gold standard (predictions frozen before any engine run)
The reduced model is a particle Monte Carlo of the two-hop echo only,
with the engine's latency, loss, fanout, routing, sync wake and
cap/saturate, and ZERO fitted parameters. It was tested on 46 curves
(gaps 2..16) under conditions the champions never saw:
- 9 physics changes: lat_base 0/2, lat_hop 2, jitter 0/2, update_period
  1/3, radius 2, plastic_route 0;
- amp_dist 0 (no distractors);
- 2 program edits and 2 canonical genomes.
Engine runs: 64 worlds, ns 0x5E4, 99% pair bootstrap.
RESULT: 46/46 curves FIT (MAE <= 0.07) and INTERVAL-HOLDS (endpoints of
the >= .65 interval within +-1). The verdict is PREDICTS, with or without
saturation in the model. Median MAE ~0.02, max 0.058. The post-hoc null
(each champion's base curve as the prediction) passes only 12/44.
  alteration                 specimen (base 6-11)   fresh1 (base 4-10)    predicted
  lat_base 0                 3-8                    2-8                   3-8 / 2-8
  lat_hop 2                  10-16 comb (9,13 dead) 6-15 comb             10-16 / 6-16
  jitter 0                   6-8                    3-8                   same
  update_period 1            4-9                    2-8                   4-9 / 3-8
  update_period 3            4-12 peak 10           4-12                  same
  radius 2                   2-8                    3-8                   same
  plastic_route 0            4-10                   4-10 (no change)      same
  program: pipeline register (S0:=S1, echo->S1; 2 fields)
                             8-12 (peak 7->9)       fresh3 4-11 -> 6-13   +2
  pipeline + lat_base 0      5-10                   fresh3 5-10           the shifts cancel
  amp_dist 0                 6-11 (no change)       3-11                  edges unchanged

## 3 Held, failed, surprised
Held: all six pre-stated predictions (P-a..P-f), 46/46 curves, and the
kernel check for the specimen and fresh1.
Nothing failed the frozen rules. The uniform-routing assumption is
visibly imperfect for fresh2/3 (curves ~1 gap late; peak position on
two-peak curves); not corrected, because correcting after the data would
be post hoc. evaluate.py had a key collision (fixed, no rule change). The
model ran 26 min against a ~2 min estimate.
Surprises / corrections to prior text:
(a) The trained gap is NOT the best gap: gap 7 beats gap 8 in 4/4
    champions (0.97 vs 0.87 specimen), because of readout-parity
    alternation. S-M2b's "peak 6-8" reading came from sweeping even gaps
    only.
(b) SYNTHESIS s1's "routing: disruption, not storage" is too weak: the
    specimen's routing write SHAPES the kernel (it deletes short round
    trips and sets the lower edge).
(c) The edge is set by KERNEL SUPPORT, not by signal-to-noise: with no
    distractors the upper edge stays at 11.
(d) SYNTHESIS s2's two-stage echo is confirmed, but "lands 0-2 ticks
    before readout" is the arrival-side view. The interval = round-trip
    support x per-wake-window sampling.
(e) The interval can be a quantized SET, not a band (a lat_hop 2 comb to
    gap 16; two peaks at update_period 3).
(f) C1b's shuffle_time fits: U[1,7] has support and mean close to the
    native delays.

## 4 Proposed threads
T-WA-1 A routing-aware model with the measured per-site weights for
       fresh2/3 (prediction: residual MAE < .02; also tests whether routing
       carries the cue sign).
T-WA-2 Design, not evolve: use echo_model to choose physics and pipeline
       depth to cover a target gap set, then verify in the engine. A cheaper
       alternative to T-M2-2 step 3; may hold two lags via S1.
T-WA-3 M2 retention is bounded by physics (2*ceil_P(lat_base +
       lat_hop*r + jitter)). Any SI01 or C2 design on PTE needs a
       RECIRCULATING control genome (e.g. PAY_c := SENSE + IN_c').
T-WA-4 Always sweep odd gaps; even-only sweeps hide the parity sawtooth.
