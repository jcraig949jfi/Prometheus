# W5 design notes (HT-55162c0ac0, P3v2)

Layer: implemented candidate (controls only). No treatment reading exists.

## What it tests

M10 via lens L5, and M10's own distinguishing observable: at a fixed item
count, do chaotic competitive draws lose more items than non-chaotic ones,
once interaction strength is held fixed? n = 4 competing species; draws
come from a +-10 % neighbourhood of the Vano et al. (2006) chaotic
matrix, so chaotic and non-chaotic draws sit side by side at nearly the
same strength. The contrast is the draw's own chaos label; nothing is
imposed on the dynamics.

It can fail cleanly: if chaotic draws keep as many species as their
non-chaotic neighbours (or more; the source matrix is known for chaotic
four-species coexistence), F1/F2 fire and M10's "chaos causes the loss"
reading is NULL for this substrate. The modulator half of M10 (shifting
the threshold) is deliberately not tested here: one claim per world.

## Why it avoids the earlier failures of this program

- Positive control reaches the spec's own thresholds on the control rows
  (S1 0.103 >= 0.08, S2 8e-6 < 0.01, S3 0.103 >= 0.06). The earlier
  failure mode was a positive control that the specified dynamics could
  not produce; here the positive control is a construction (absorbing
  boundary after the chaos label is fixed) whose effect does not depend on
  the hypothesis being true.
- Null twin cannot succeed by luck of a single seed: it is a label
  permutation of the same rows, pooled over 500 draws (S1 0.0016, p 0.36).
  The earlier failure mode was a twin whose per-seed successes (a lucky
  gain) broke a tight twin bound; no clause here is a per-seed max.
- Control and null twin are different constructions (symmetrised physical
  twin vs label permutation), not one construction named twice.
- Eligibility is counted before freezing: 98 chaotic / 402 non-chaotic in
  the control family (need >= 20 each). An ensemble of broad random
  matrices might contain almost no chaotic draws; the neighbourhood
  design removes that risk.
- The chaos estimator is itself checked: the unperturbed Vano matrix gives
  lambda 0.019 (literature value about 0.02), its symmetrisation -0.13.

## Ambiguities resolved

1. "Positive control (effect present by construction)": I read this as a
   world in which chaos causes loss by a rule I impose, measured through
   the identical label/recall/statistics path. Phase A (pure dynamics,
   label) is shared with the treatment's code path; only phase B differs.
2. "CHEAT detected": read as the evaluator registering success when
   success is injected into the observable (recall overwritten). This is
   what the earlier rounds used; it checks the instrument is not blind.
3. Threshold choice: the positive control's ceiling is about 0.1 because
   chaos-driven loss costs about one of four species and non-chaotic draws
   also lose species to exclusion. Thresholds were lowered from 0.15 to
   0.08 / 0.06 BEFORE any treatment exists (revision 1), and are about
   3.6 null standard errors above the permutation null.
4. Between F1 (< 0.03) and S1 (>= 0.08) the reading is INCONCLUSIVE.
5. Recall uses a 200-unit mean abundance, not an instantaneous value, so a
   chaotic dip at t = 3000 is not a loss.
6. Control seeds (0..4) and treatment seeds (100..104) differ, so the
   control run never evaluates the treatment's own draws.
