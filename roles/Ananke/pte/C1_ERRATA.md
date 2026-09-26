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
