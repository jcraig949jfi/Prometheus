# raid_B toy -- multiple transient memories -- RESULT

Status: EXPLORATORY. Preregistration: PREREG.md (frozen before the first
run, not edited since). Code: mtm.py (preregistered run), posthoc.py
(POST-HOC, labelled). Data: pilot.json, results.json, posthoc.json,
posthoc_log.txt. Stdlib Python, 4 processes, shared host at load ~39.

Commands (from this directory):
  python3 mtm.py pilot                      (seed 999; ~10.5 min wall under load)
  python3 mtm.py main 1024 64 1.0 2.0 3 6   (~1.8 min)
  python3 posthoc.py                        (POST-HOC)

## 1. Pilot (rule applied as written)

- W1 (particles) at g1 = 1.0, g2 = 2.0: SINGLE(g2) absorbed (C(g2) = 0) at
  1024 cycles -> t_long = 1024, t_mid = 64. No scaling needed.
- Lattice at g2 = 10 and at 0.75x (g2 = 8): never absorbed within 8192
  cycles (C(g2) stayed 0.65 / 0.35). At 0.5625x (g1 = 3, g2 = 6): absorbed at
  64 -> t_long = 64, t_mid = 4.
- DEVIATION (recorded): scaled lattice amplitudes were ROUNDED to integers
  (round(5*0.75)=4, round(10*0.75)=8, round(5*0.5625)=3, round(10*0.5625)=6);
  the prereg did not say how to round an integer lattice amplitude.
- CONSEQUENCE NOT FORESEEN: with g1 = 3, g2 = 6 and band width w = 3, W4's
  two bands [0,3) and [3,6) tile [0,6), so W4-alt collapses to the nested
  case at long times. W4 is therefore uninformative for H_nest in the
  preregistered run.

## 2. Preregistered outcome

| world | P1 mid both | P2 long forget g1 | P3 noise both | P4 single no g1 | P5 rand none | MTM |
|-------|-------------|-------------------|---------------|-----------------|--------------|-----|
| W1 particles | FAIL | pass | FAIL | pass | pass | NO |
| W2 lattice nested | FAIL | pass | FAIL | pass | pass | NO |
| W3 lattice spread | FAIL | pass (weak, K=0.033) | FAIL | pass | pass | NO |
| W4 lattice band | FAIL | pass | FAIL | pass | pass | NO |

Decision rule K1 fires: the toy did NOT replicate the source (no memory of
the smaller amplitude g1 is ever written, in any world, noise or not).
By the preregistered rules no inference about Prometheus lattices follows.
g2 memory (the largest amplitude) is written everywhere (a clean onset/kink
at g2), P2/P4/P5 pass everywhere -- but P2 passes trivially because g1 was
never stored, so "forgetting" was not observed either.

Diagnostic facts from results.json (seed-averaged C(a)):
- W1 alt at t_mid: slope of C below g1 (0.026 per unit) equals slope in
  (g1, g2) (0.029); the alternating run's curve is indistinguishable from
  the SINGLE(g2) curve. g1 cycles do nothing that g2 cycles do not already
  do: with a nested rule and a randomising kick, the g1 training is
  REDUNDANT.
- W3 (activity spreads to quiet neighbours with p = 0.25) never absorbs at
  g2 = 6 (C(6) = 0.38 at t_long vs 0.001 in W2): leaking activity lowers the
  critical amplitude; the g2 memory is weak (kink 0.03 vs 0.13 in W2).
- W4 SINGLE(g2) shows a flat plateau of C over [3, 6] (the cleared band):
  a non-nested rule writes an interval, not a threshold.

## 3. Diagnosis (source re-read AFTER the run)

Paulsen, Keim & Nagel (PRE 88, 032306; arXiv html 1307.1184) use the same
readout (f_mov = fraction that collides in a trial deformation; memory = a
peak in f_mov'') and state the mechanism: training "depletes f_mov' just
below the training value and enhances it above". Their kick is eps = 0.005
particle diameters (prereg used 0.5, 100x larger) and they train ~1e4
cycles. A small kick leaves a disturbed particle near the MARGIN of the
amplitude that disturbed it; a large kick re-randomises it and erases the
margin structure. The preregistered toy therefore tested (a)-(c) of the
mechanism without (d).

## 4. POST-HOC test of the small-kick hypothesis (NOT preregistered)

Hypothesis H_margin: small kicks are what write the smaller memory.
Only the kick changed (W1s: eps = 0.05; lattice W2s/W3s/W4s: a kicked site
moves s -> s + u, u in {-2..2}\{0}); same readout and detector; more
checkpoints (W1s to 4096 cycles, lattice to 4096). W2big = prereg W2 rerun
as reference. 5 seeds each. Summary (posthoc_log.txt, posthoc.json):

- g1 (smaller amplitude) memory: NOT detected in any world, any condition,
  any checkpoint (max K at g1 = 0.070 in W1s alt_noise t64, below its 3-SD
  gate; every lattice K(g1) <= 0.001).
- g2 (largest) memory: detected everywhere after the first checkpoint.
  Small kicks roughly DOUBLE its sharpness on the lattice (K(g2) = 0.29 in
  W2s vs 0.14 in W2big): pile-up just above the trained amplitude is real --
  the margin effect exists, but only at the amplitude that bounds the quiet
  set.
- Noise: with small kicks the g2 memory decays under noise (W2s K 0.27 ->
  0.17 from t256 to t4096) -- noise here erodes, it does not re-open
  plasticity for g1.
- W4s SINGLE(g2) writes a plateau (non-nested rule stores an interval);
  alternating g1, g2 again tiles [0, 6) (w = 3) so W4 stays uninformative.
- W1s is UNDERPOWERED: after 256 cycles 117 of 300 particles still overlap
  at rest (kick 0.05 vs overlap depth up to 1), so C(a) is dominated by
  static overlaps (C(0.1) = 0.13 even at 4096 cycles). The source needed
  ~1e4 cycles with eps = 0.005; this toy could not afford that in budget.
  No wall artefact (0 particles pinned at the y walls; checked).

## 5. Verdict

1. PREREGISTERED: MTM NOT REPRODUCED (K1: instrument failure). Only the
   largest-amplitude memory forms. No inference about Prometheus lattices
   from the prereg rules.
2. POST-HOC (EXPLORATORY): small kicks sharpen the largest memory but do not
   write the smaller one on a discrete lattice (Q = 64, amplitudes 3 and 6)
   within 4096 cycles; the particle version did not converge in budget.
3. What the toy DID establish, robustly across 4 rules x 2 kick sizes x 5
   seeds: a nested, threshold-activated, dissipative rule writes the
   MAXIMUM drive amplitude as a sharp, label-free, history-specific feature
   of C(a) (P4, P5 pass everywhere: absent in random state; present only
   at the trained amplitude). In coarse discrete substrates this is a
   Mullins-type max-register, not multiple memory.
4. Mechanistic reading (hypothesis, not tested): the smaller memory is a
   second-order RATE-ASYMMETRY imprint (units below g1 are disturbed twice
   as often as units in (g1, g2), giving a jump in the margin density at
   g1). It needs continuous (fine-grained) margins and a long sub-critical
   transient; a coarse integer margin and fast absorption erase it. This is
   the Prometheus-relevant prediction: in discrete lattice worlds with coarse
   margins, expect max-register memory, not MTM, unless margins are
   fine-grained.
5. Next test (not run): W1 with eps = 0.005, 2e4 cycles, compiled or
   vectorised; lattice with Q = 1024 and amplitudes ~ 50/100 (fine margins);
   add a slope-jump detector (C'' peak) as in the source.

Wall time used: pilot 10.5 min + main 1.8 min + post-hoc ~20 min on a host
at load ~39 (the 30-min budget was exceeded by the post-hoc; recorded).
