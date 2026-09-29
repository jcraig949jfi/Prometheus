# Temporal intervention coverage: the C1 blind spot as a general problem

Currency: 2026-09-27. Specimen: C1's packet_ablation window [t0, readout),
which never dropped the readout tick's arrivals (D-A).

## What the measurement says (S-F, single-cue twins)

Share of cue-bearing deliveries to the actuator (cue onset -> readout)
that land AT the readout tick, i.e. OUTSIDE C1's window:

  cell            lag-0 share   C1 window coverage
  M3 0a23398f     1.00          0.00   <- window could not fire
  M3 f6b623cd     1.00          0.00   <- window could not fire
  RELAY x4        0.00-0.31     0.69-1.00
  MAJ D x2        0.07          0.93
  M2 (HOLD)       0.20          0.80  (arrivals only at lags -2..0)

So the blind spot was TOTAL for exactly the cells whose delay equals delta,
and partial (up to 31%) elsewhere. A window that is "mostly right" can
still misattribute when the champion's physics puts all its mass on one
tick.

## General lesson

An intervention is informative only where it can intersect the causal
event. That is the TEMPORAL form of the eligibility rule adopted for C1b
(A3: an absence reading counts only where a positive control fires). Three
recurring shapes, found in PTE and in other seats (CROSS_ENGINE_THREADS):
1. WINDOW MISS: the window excludes the event (C1 D-A).
2. CHANNEL INERT BY PHYSICS: the intervened channel cannot act (frozen
   routing under dest_mode "all"; Aether's forced full-ring ablation).
3. SWITCH NEVER REACHES THE MECHANISM: the gate is never wired to the
   measurement (Nestor C9-D16; Archaeon D-008's tabu with 0 hits).
All three are "an intervention that could not have fired". The remedy is
the same: before trusting a null, show the intervention's REACH.

## Proposed reusable instrument (not built yet; thread T-TA-1)

`lens.cue_arrival_profile(ph, genome, env)`: single-cue twins -> per
(tick, site) map of cue-bearing deliveries and state differences. It
costs seconds per cell (S-F: all 9 cells in under 1 min). Uses:
- REACH CHECK for any time-windowed ablation. Report the fraction of
  cue-bearing mass inside the window next to every such null. A null with
  reach < 0.5 is labelled WINDOW_UNREACHABLE, not NOT_SUPPORTED.
- EVENT-ALIGNED interventions: place ablations at the measured lags, not
  at nominal task times.
- A LATENCY SWEEP (+-k) as the standard timing positive control. It
  separates "deadline" (early ok, late fatal: M3) from "timing code"
  (both directions matter) from "tolerant" (M2 +1 ok).

## Where the lesson does NOT generalize

- Carrier SWAPS at a mid-interval tick are much less window-sensitive than
  ablations. Swapping the whole in-flight state carries every future
  arrival with it, and M2/M3 FLIP under it. For carrier identification,
  swaps are the preferred instrument precisely because they sidestep most
  window choices.
- Families whose readout integrates over many ticks (HOLD latches) are
  insensitive to single-tick misses (S3: HOLD D cells 1.00 under every
  window).
- Existing C1 verdicts: the S3 recheck showed D-A moved only the two M3
  cells. Rewriting other experiments is NOT warranted.
