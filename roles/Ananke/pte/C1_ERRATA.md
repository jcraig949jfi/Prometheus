# PTE-C1 errata (C1 labels are NOT changed; these are reading notes)

Currency: 2026-09-26. Source: PTE-C1b (roles/Ananke/pte/c1b/, rows sha256
8019247c19cdf2f0) and the pre-run code inspection (comms #639/#640, #661,
#683).

E1 D-A PACKET-ABLATION WINDOW. C1's packet_ablation dropped arrivals over
   [t0, readout) and never at the readout tick. For the two M3 cells
   (0a23398f, f6b623cd; delay == delta == 4) this made the C1 null
   VACUOUS BY CONSTRUCTION: no arrival carrying the trial's cue could fall
   inside the window. C1b confirmed it on the specimens: C1 window
   0.697 / 0.686 (no effect), readout-tick-only 0.511 / 0.500, corrected
   window 0.501 / 0.500. The recheck of all 12 D-wave cells shows no other
   verdict affected (RELAY corrected 0.50 in 4/4; HOLD latches 1.00).
E2 FROZEN ROUTING VACUOUS under dest_mode "all" (both M3 cells). w is never
   read there, so "frozen routing: no effect" could not have been otherwise.
   The C1 reading "SETRULE carries it" rested partly on that null. C1b:
   SETRULE is required (freeze_rule -> 0.52), but the readout site's rule
   index carries no cue (constant 0).
E3 C1's MEMORY ABLATION reset only S. M2's "not in any site" was
   under-identified. C1b per-carrier resets: S, inbox no effect; w -0.066;
   the joint non-packet reset -0.062; flushing in flight -> 0.497.

## Errata from the inference-harvest code audit (2026-09-30, harvest/H-IMPL/REPORT.md)
- E-H1 (MAJOR, labels): on MAJ and XOR the twin assay negates EVERY sensor column but measures reach
  from sensor 0 only (assays.py twin_assay). A program that never emits scores beyond_hop 1.00 (MAJ
  reach 6, XOR reach 3). The stored REACH_BEYOND_HOP labels for MAJ (114/162, 59 with comm_delta < .02)
  and XOR (48/83, 46 with comm_delta < .02) are UNINTERPRETABLE. No C1_REPORT headline uses them.
  From 2026-09-30 twin_assay also reports reach_nearest / beyond_hop_nearest (distance to the nearest
  perturbed sensor); legacy keys are unchanged.
- E-H2 (label): on global topology every env distance is <= 1, so REACH_BEYOND_HOP can never fire
  (0/213 global evolve rows). "No distal reach" on global is structural, not measured.
- E-H5 (wording): wave E scales ONE RELAY law (bbef66a1). C1_REPORT s1's "frozen RELAY laws ...
  SIZE-FREE" rests on that single law, and bbef66a1 failed its fresh-seed reproduction (reps .572 /
  .506). The reproduced RELAY cells were never scaled.
- E-H2b (interpretation, principal-verified with H-SCI): zero_comm is exactly .500 in 213/213 RELAY,
  174/174 MAJ and 95/95 XOR rows. It is forced by construction: mirror pairs share all physics draws,
  and the actuator is never the sensor. COMM_DEPENDENT therefore equals SIGNAL in these families, and
  zero_comm cannot count as causal evidence there.
