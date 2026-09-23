# c2x -- complete the 2x2 and replicate C2 -- PREREGISTRATION (2026-09-23 ~15:52Z, before running)

Arms (both new configs in campaign0.py; no sealed universe is used -- none remains):
  c2none  seed 20260929 (the C2/c2abl seed), NO cost lines, NO location-aware selection (LOLO pick as
          in C0b/C1), location gate ON. Completes the lines x selection 2x2 on one seed.
  c2rep   C2 exactly, fresh seed 20260931. Replication: positive results are provisional.
Predictions: c2none -> no law survives the location gate (conf 0.6). c2rep -> a law survives with
worst per-family offset <= 0.10 log2 and a G exp(-N)-product ceiling (conf 0.5).
Scope: one seed per cell; the 2x2 is descriptive, not a significance test.

## c2none RESULT (2026-09-23T16:04Z)
NO lines, NO location-aware selection, location gate ON, seed 20260929: round 0 law FAILED by the
location gate (ring +.134, ca +.063); revised law ce54e6dd6f (v4)
  (exp(-N) - C/G) >= 0.1454  AND  ((C - log Q) K) >= 0.16
SURVIVED round 1 (1/111; offsets ca .000 regs -.033 ring +.055). Prediction LOST.
On seed 20260929 all three arms run (both / selection only / neither) produced a surviving, well-
located law; C1 (lines, no selection) failed on seed 20260928. The lines x selection attribution is
confounded with seed. Added arm (written before it runs):
  c1s29   C1 exactly (lines, no selection, location gate) on seed 20260929 -- completes the 2x2 on one
          seed. Prediction (conf 0.5): it produces a survivor too (i.e. C1's failure was the seed).
