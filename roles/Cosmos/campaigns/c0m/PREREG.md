# C0m -- mechanism-level attack on the frozen law -- PREREGISTRATION

Written 2026-09-23 ~13:05Z before any repetition-coded world was run.

Question (charter s VI, adversary): "Search for alternative mechanisms that accomplish the same
function and expose whether the supposed law was phrased at the wrong level."

Frozen law under test (unchanged): f852d782cb, cmap v3,
  (C - (G + exp(-N))) <= -1.055 AND ((C - log(Q)) * K) >= 0.1792

Alternative mechanism: regs with `code = 3` -- every stored bit is written as 3 physical bits
and read by majority at the ask; no repair during the horizon; 3x the bit maintenance cost.
The same function (hold the cue, emit it at the ask); a different mechanism.
Declared coordinates for code = 3 (from the spec, computed BEFORE running):
  C = bitcost * 3b * H / R
  N v1 = q * 3b * H (raw flips)
  N v2 = -b ln(1 - P_maj), P_maj = 3 pi^2 - 2 pi^3, pi = (1 - (1 - 2q)^H) / 2
  (for code = 1 the declared N is unchanged: q b H)
  Q = 1 (registers unbounded)

Design: 300 regs worlds with code = 3 drawn from the regs lattice (seed 20260925), plus the SAME
300 worlds with code = 1 as the matched reference (MECHANISM_OF pairs in the graph as
COORD_PRESERVING? no -- they differ in coordinates; recorded as DEFORMATION_OF knob=code).

Gates (thresholds set now):
M1  frozen-law BA on code = 3 worlds >= 0.90
M2  BA(code = 3) >= BA(code = 1) - 0.05   (the law is not specific to the reference mechanism)
M3  reported, not gated: BA of the law if the code = 3 worlds are (wrongly) given code = 1
    coordinates -- how much the mechanism-level coordinates matter.
Precommitments: M1 holds (conf 0.6); M2 holds (conf 0.6); M3 BA drops by >= 0.1 (conf 0.5).
