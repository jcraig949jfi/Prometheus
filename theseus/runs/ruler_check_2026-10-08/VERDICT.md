# THESEUS-23a verdict (prereg roles/Theseus/prereg/2026-10-08_ruler_check/)

Run: python -m theseus.synth.ruler_check --tag ruler_check_2026-10-08 --per_family 40 --workers 4
(branch theseus/loop48-2026-10-08, prereg 6d900baa3). 240 planted + 240 matched random.
Wall 330 s, CPU 1053 s. Viable: planted 204/240, random 149/240.

Viable-only scope (primary), frozen rule:
  R2 sparseness vs G0      AUC .324 [.265, .383]  WEAK (prefers random)
  R3 known-library dist    AUC .320 [.261, .376]  WEAK (prefers random)
  R4 jitter smoothness     AUC .464 [.400, .531]  NON-DISCRIMINATING
  R5 response mid-band     AUC .751 [.700, .807]  DISCRIMINATING (at the .75 edge)
  R6 replicate stability   AUC .424 [.364, .489]  WEAK (prefers random)

Predictions: Q1 WRONG (WEAK, not NON/ANTI), Q2 WRONG (same), Q3 WRONG, Q4 RIGHT, Q5 RIGHT.

Frozen consequence applied (POST-HOC, theseus/runs/posthoc_r5_2026-10-08/RESULT.json):
R5 on committed v0_1 arms, AUC vs random R: A .711, B .667, P .626, E .606, C .591,
D .567, G0 seeds .438. D vs one-shot (P+B+C): AUC .438 [.404, .472] -- deep
descendants show LESS graded causal structure than one-shot collisions.
Caveat: deliberately weird programs W score mean .742 on R5, above R (.705):
R5 is weak, not clean.
