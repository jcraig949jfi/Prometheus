# Ananke spikes 2026-09-27 -- LOG (all Attempts kept, including failures)

Plan: SPIKES_2026-09-27_PLAN.md @ 8e081dcb1. Host: M1 GPU, free at 19:08Z.

A1 S-M2 first run FAILED (script bug, not data): numpy advanced indexing
   ms[:, bi, an, :, 0] put the batch axis first, so the decoder got [LM]
   instead of [B]. Fixed to ms[..., 0][:, bi, an, :]. No result was read
   before the fix.
Deviation D1: the plan's "slot_roll -1" cannot be built (packets cannot be
   delivered before they were sent). Replaced by +1 and +2 delays, noted
   before the run.
A2 S-M2 ran (298 s): out/s_m2.json. Fresh champions regenerated
   BIT-IDENTICALLY from stored search seeds (held acc equal to 1e-12).
A3 S-M3 ran (25 s): out/s_m3.json.
A4 S-F ran: out/s_f.json.

ADDENDUM (before running; exploratory, not in the plan): S-M2b gap sweep.
   S-F showed that M2's cue-bearing deliveries to the actuator happen only
   at lags -2..0: the bit leaves and comes back just before the readout.
   Question (prior-art item 2): tuned echo or open-ended recirculation?
   Evaluate the frozen specimen and the 3 fresh SIGNAL champions at gap in
   {4, 6, 8, 10, 12, 16, 24} (other env dials as trained), 64 worlds, ns
   0x5E2.
   Prediction: TUNED ECHO. Accuracy peaks at the trained gap 8 (+-1 or 2,
   from the +1-delay tolerance) and falls toward chance at gap >= 12 and at
   gap 4. If it holds high out to gap 24: open-ended recirculation.
   Decision: "tuned" if acc(gap 16) lo99 < 0.60 in >= 3 of 4 champions;
   "open-ended" if acc(gap 16) lo99 >= 0.75 in >= 3 of 4; else "mixed".
