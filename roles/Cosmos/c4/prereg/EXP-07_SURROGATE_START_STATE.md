# EXP-07 -- INSTRUMENT: is the surrogate's underprediction the START STATE? (prereg 2026-10-11, before data)

Origin: EXP-06 (INSTRUMENT_DEFECT UNEXPLAINED; error grows with memory, survives noise-free composition).
Found by reading code after EXP-06, before any EXP-07 run: the task harness (c3/system.rollout, cert_b._run)
starts EVERY episode from system.init (zeros for the reservoirs); the frozen surrogate composes from STATIONARY
states. A start state with stationary variance decays as a^(k+2): negligible at a .5 (.06 at k 2), dominant at
a .95 (.81 at k 2), where it swamps the cue. This matches the EXP-06 failure shape.

H-START: composing from the task's own start state removes the underprediction.

Variants (the ONLY change is the start state; fit, features, noise, clip, decoder, seeds frozen):
  O0 frozen instrument (stationary starts) | O1 start = system.init(E) full state, whitened with the fit's whitener.
Grids: G1 = the 22 EXP-06 planted systems (diagnosis set); G2 = FRESH planted Reservoirs a {.5,.7,.85,.95} x
sigma {.1,.3} x wseed {3, 4} (16 systems, never run). k in {2, 4, 8}. Actual = Certificate B linear accuracy.

Decision (fixed now): H-START SUPPORTED iff on BOTH G1 and G2: O1 median abs error <= .5 x O0's AND
abs(O1 median signed error) <= .05. Otherwise H-START REJECTED and the defect stays unexplained.

Locality note: system.init is part of the TASK protocol, not a multi-step trajectory; reading it adds no controlled
step (G7 unaffected). If supported, surrogate v2 (init start) is a NEW instrument version: it must be requalified on
fresh DISCOVERY worlds of the families under its own prereg before use. EXP-04 is NOT rescored.
