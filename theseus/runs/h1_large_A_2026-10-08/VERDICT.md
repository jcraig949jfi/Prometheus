# THESEUS-24 verdict (prereg roles/Theseus/prereg/2026-10-08_h1_large_A/, 7cf5ac9c6)

Run: python -m theseus.synth.h1_rescore --tag h1_large_A_2026-10-08 --workers 2
(branch theseus/loop48-2026-10-08; v1 genomes committed b857ec80c before evaluation).
A v1: 250 valid, 0 rejected, 194 viable (0.776). Arms viable: D 338, A 245, B 223, C 219, R 175.

H1 at equal n = 175 (frozen rule, analysis.hard_test unchanged): FAIL
  grid pca  EX(D) 29 vs null median 30 (p .607); EX each D29 A24 B30 C37 R38
  grid desc EX(D) 35 vs 35 (p .526);              D35 A27 B36 C43 R39
  grid resp EX(D)  3 vs  6 (p .965);              D3 A3 B10 C8 R13
  O(D)-O(R): euclid_z -0.06 [-0.34, 0.24]; cosine -0.003 [-0.038, 0.012];
             quantile_l1 -0.004 [-0.010, 0.003]
H1 without A (D vs B, C, R; n 175): FAIL (EX(D) 35/42/7 vs null 36/42/10).
v0-sized A re-draw (n 51): INDETERMINATE -- the v0/v0_1 flip was a small-n artefact.

Predictions N1 FAIL RIGHT; N2 not PASS RIGHT; N3 RIGHT; N4 viable >= .75 RIGHT (.776).

Reading: at 3x the n, deep descendants occupy no more exclusive behavioural niches than
chance assigns them; complexity-matched random programs hold the most exclusive cells.
