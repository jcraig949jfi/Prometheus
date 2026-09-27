# Joint carrier 4781b0a1: PLAN (committed before any run)

Thread: T-DM-2 / T-JC-1. Specimen: C1 D-wave MAJ cell 4781b0a1 (ring
N=144 r3, sync period 2, lat 1+1*hop+jit 1, loss .1, cap 2 saturate,
fanout 8 sample, P=2, state_dim 2, WIMM on, plastic_route on; env MAJ
d 3, delta 16, 5 sensors flip_p .3). Prior observation (S-CT and addendum
3): a joint channel+site swap FLIPs at t0+1/+8/+15; channel alone 0.70 /
0.52 / 0.63; site alone 0.30 / 0.48 / 0.38.

CAUTION FIXED UP FRONT: a joint swap of all channel + all site state
exchanges essentially the whole world state, so it flips ANY mechanism. It
is a sanity check, not evidence of distribution. The evidence is in the
single-carrier results and in erasures.

Hypotheses and what each predicts at mid-interval (t0+8):
  H-RED  redundancy: the bit is copied in both. A single ERASE is harmless;
         a double erase kills; a single SWAP gives conflict ~0.5.
  H-SYN  synergy (XOR-like): each part is useless alone. A single erase
         kills; the single-part decoders are at chance.
  H-HAND sequential handoff: at any tick one carrier dominates. Erasing
         the dominant carrier kills, the other is harmless, and the
         dominance shifts over ticks.
  H-ADD  additive integration in progress: the answer is a sum of partial
         contributions, some already at sites and some still in flight.
         Each single erase HALF-hurts (intermediate). The single-part
         decoders are above chance but below the joint one. The joint
         linear decoder ~ normal.
  H-ART  swap artefact: a joint swap before the cue exists (end of the
         previous ITI, tick t0-1) also FLIPs the upcoming trial.
Ananke's prior (stated before running): H-ADD, because MAJ integrates 5
sensors whose packets arrive at different times. Site state may include
Kp via WIMM.

Probes (all between ticks; 64 worlds, ns 0x5E7; CPU, 2 threads; per-trial
accuracy over 12 trials; 99% pair bootstrap):
  J1 single-carrier SWAPS at t0+1, t0+8, t0+15: S, Kp, inbox (Acc), w,
     channel pay0, channel pay1, channel counts.
  J2 ERASURES at the same ticks: reset S; reset Kp; reset inbox; reset w
     (to 16); flush the channel; and the double erasures S+flush and
     Kp+flush.
  J3 decoders at t0+8 (fit on half the pairs, score on the other half):
     sign of actuator S0, actuator S1, sum of actuator Kp, in-flight pay0,
     in-flight pay1, pay1 addressed to the actuator, and the joint linear
     sign(a*x + b*y) of the best site and the best channel feature
     (a, b fitted on the fit half).
  J4 artefact control: joint swap at t0-1 (before the trial's cue).
Decision rules (at t0+8, "erase hurts" = drop >= 0.10 with lo99(diff) <
-0.05; "harmless" = lo99(diff) >= -0.10):
  H-RED if both single erasures are harmless and the double erasure hurts;
  H-SYN if both single erasures drop to hi99 <= 0.60 and the single
     decoders are at chance (lo99 <= 0.5);
  H-HAND if exactly one single erasure hurts at each probe tick and the
     hurting carrier changes between t0+1 and t0+15;
  H-ADD if both single erasures hurt but stay above 0.60 (partial) and
     the joint decoder beats both single decoders;
  H-ART if the J4 swap at t0-1 FLIPs.
  Otherwise: UNRESOLVED, with the pattern reported.
Budget: 30 min CPU. Every Attempt is logged in LOG.md.
