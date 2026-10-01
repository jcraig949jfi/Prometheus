# H-PLANT PLAN ADDENDUM (deviations from plans/H-PLANT_PLAN.md; each written BEFORE the affected run)

A1 (before any P-XOR run) P-XOR is not "one-hop". envs.build places the XOR actuator uniformly
   among sites at distance >= max(1, d//2) from both sensors, so no in-range physics makes both
   sensors direct neighbours of the actuator in every world. P-XOR instead floods the per-trial
   set of cue signs (flags P/Q) and reads y = -1 iff both flags; "co-arrival" is provided by a
   global tick clock (S3 = t, reset at trial onset) instead of same-window arrival. Chosen
   physics: torus 64 r3, dest all, lossless, lat 1, jitter 0, sync period 1 (all in C1 ranges).

A2 (before any P-XOR run) "C1-sampled physics point" for XOR: d9cc is the plan-named point but
   the clock plant needs update_period 1 (d9cc: 2). Added: (a) an analytic light-cone bound at
   d9cc XOR; (b) a pre-declared screen over all clock-compatible C1 XOR rows (sync, period 1,
   decay 0, mut 0, c_op 0) at 32 DEV worlds, top-1 then scored on 256 fresh worlds. At a C1
   point the plant sets only the genome-space fields (c1b.at_specimen / PLANT_STRUCT, the C1b
   A2.2 convention; C1's own plant_viability likewise reset prog_len); all communication physics
   (topology, loss, latency, cap, decay, update, economy, mut) is the row's.

A3 (before any P-XOR must-fail run) MF-XOR (gated) = sensor s2's cue zeroed in the schedule
   ("readout ignoring one sensor"): the plant merges cues by sign class, so no single plant
   operand corresponds to one sensor. Q-operand-zeroed readout run as a diagnostic only.

A4 (before any P-MULTIHOP run) env d: the parent plan says d = 2*radius (= 6 at d9cc's radius 3),
   which is outside C1's env levels {1,2,3,5}. Primary multi-hop env = d=5 (C1-sampled: cell
   fac4aaa23a0bdcb2, ring distance 5 > radius 3 => >= 2 hops forced). d=6 run as an extra.
   P-MULTIHOP program = plants.relay_flood unchanged (every site that changes relays; this is the
   minimal hand-written relay, rather than a designated single relay site, which a homogeneous
   program cannot designate).

A5 (before the gate) gate values: relay_flood recorded accuracies = C1 plant_viability row
   29b7e63a5fa4a78b (.9609375) and C1b F_DA normal (1.0); echo_hold = C1b F_echo normal (1.0).

A6 (after the XOR screen and the top-1 score; BEFORE this run) Strictness of "a point C1 actually
   sampled": the top screen cell 4eeca9f10c514f08 needed genome-space overrides (prog_len 8->16,
   state_dim 1->4, ...), so it is a C1 COMMUNICATION-physics point, not a full C1 dial vector.
   Added (pre-declared now): score P-XOR on the 256 fresh worlds at the best screen cell whose
   FULL C1 dial vector accepts the plant with NO override (prog_len 16, state_dim >= 4,
   payload_width >= 2): aa2b8d6805a15ec6 (screen .719; the only such cell above .55 besides the
   torus cells at .57). The XOR reading will be stated for both the strict and the at_specimen
   sense.

A7 (after all three plants were scored; BEFORE this run; extra analysis, no reading depends on
   it) Light-cone census: run lightcone.bound on every C1 EVOLVE-wave row (A, B, B2, C, D, E) of
   XOR, FLIP and RELAY, and report the fraction of rows whose analytic upper bound is < .60
   (= rows whose NULL no program could lift to lo99 > .60 at that physics+env). Optimistic for
   async rows (a site may wake any tick).
