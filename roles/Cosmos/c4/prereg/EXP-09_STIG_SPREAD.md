# EXP-09 -- stig H-SPREAD on FRESH worlds (EXPLORATORY; DISCOVERY batch 4; prereg 2026-10-11, before data)

Origin: EXP-05 (INCONCLUSIVE; post hoc: the noise-free ring-return predictor works only at low diffusion).
H-SPREAD: stig usability is the reachability of a decaying, DIFFUSING cue trace by a moving, jittering sensor.
Predictor (zero parameters, mechanistic, from the declared knobs; exp09.spread_score): expected cue-trace mass in
the sensor's +-1 window at query time (unit deposit at cell 0 at t 0; per step decay, diffusion D; sensor shift v
plus jitter j). Checked BEFORE this prereg on synthetic knobs only: reduces to the return predictor R when
delta = D = j = 0 (test_c4_exp09). This is an EXPLANATION of one family, not a cross-family LOCAL law.

Data: 60 NEW stig worlds, natural proposal (split_seed DISCOVERY 4, 800000 + i), L 16, k 1..40, Certificate B linear.
Per moving world (v >= 1): s_spread = Spearman over k (score, B excess); s_return = Spearman(R, B excess).

Decision (fixed now): H-SPREAD SUPPORTED iff, both over all moving worlds AND over those with D >= .1:
median s_spread >= .50 AND median s_spread - median s_return >= .10. Otherwise REJECTED.
