C-010-T032 INTEGRATION_READY (Cadmus[m1-a86ec5e4]). Re #1823.

Branch cadmus/c010-t032 at 836f96e18438b7256806b2b3035bfcaa9d94293a (merged with origin/main); claim 66eae1375. Receipt on main.
- R5: NULL = subject copy + reset_each_step + plasticity rates zeroed exactly as S-NOPL (AMENDMENT_v1.0.1). State
  test on the POS carrier: R = 0 equal to S-NOPL, runtime non-plastic, live W1 = genome W1 at every step. RED on
  the old NULL.
- E2: pin that building ANY arm leaves the shared subject unchanged (R, W1, W2, keep, alive, op, bias, cfg). RED:
  W1.E2 applied verbatim is killed. The code already copied; this was a test gap.
Witness suite 135 OK, binding 21 OK on the merged tree. Synthetic / hand-wired only; no registered statistic.
