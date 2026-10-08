# EXP-03 -- out-of-family transfer to a family the law has never seen (EXPLORATORY; prereg 2026-10-08 before any
# cosmos_phase world was labelled for C4 -- 8 sanity worlds were certified to check the family is non-degenerate)

Family: cosmos_phase (authored after L-0003; never used to fit any threshold or form). DISCOVERY split, batch 2,
natural proposal, 60 worlds, k uniform {2, 4, 8}. Labels: A, B-linear, T3-DOWN (exp01.run_world).

Frozen predictors (no refit on phase):
- C4-L-0003, theta -4.3144 (A labels; results/theta_L0003.json)
- C4-L-0004, theta -1.9992 on the USABLE-under-B target (B excess >= .10; results/theta_L0004.json)

Decisions fixed now:
- L-0004 FAILS OUT-OF-FAMILY if its BA on phase (USABLE-B target) is < .70, or if phase is informative (>= 10 per
  class) and L-0004 does not beat both T2a (k) and T3-DOWN on phase.
- L-0003 FAILS OUT-OF-FAMILY if its BA on phase (A FUNCTIONAL target, determinate rows) is < .70.
- BOUNDARY prediction (the substance of L-0004's "common boundary" claim): the phase family's own max-BA boundary in
  log d2 for the USABLE-B target lies within +-1.0 of -2.0. Outside => the common-boundary claim FAILS on phase.
- If phase is NOT informative (< 10 per class) the transfer test is NOT_REACHED and is recorded as such.
