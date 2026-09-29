# W-K LOG

A0 2026-09-28. Read COMMON_RULES, COMMON_RULES_ARC3, W-K brief, W-D REPORT
   (allowed hypothesis source), engine/lens/plants/physics/rng/envs/assays/c1b
   source, tests/test_lens_instruments.py, pte/C1_ERRATA.md, instruments/*.md.
   No principal interpretation file (SYNTHESIS*, C1B_REVIEW*, ENGINE_CARD,
   ARC3_PRIORITIES) read. Timing smoke: echo_hold HOLD 64 worlds CPU 1.5 s.
A1 PLAN.md frozen (fixtures, checks K0..K9, scoring rule).
A2 wk.py written (plants flood_rwrite, flood_rdecor, latch_listen,
   rule_decor; harnesses Reference / Unwired / KeyedTarget / LabelSeed;
   CondFlush hook; 21 fixtures). Cleanup: removed a dead helper (mask_arm)
   before any run.
A3 accept.py run 1: crashed at MASK-B (self-hit count on a numpy mask).
   Bug in my harness's self-report; fixed (arrays count as 1 applied field).
A4 accept.py run 2: all 21 readings (acceptance criteria met); json write
   failed on a relative path (fixed; rerun to save).
   Readings: WIN-B NULL / WIN-V EFFECT; INERT-B NULL / INERT-V EFFECT;
   UNWIRED-B NULL / -V EFFECT; TARGET-B EFFECT (0.417, spurious) / -V NULL;
   DEAD-B NULL; SEED-B NULL; PROBE-B EFFECT (0.500, spurious); COND-V EFFECT;
   MASK-B AMBIG (0.938, pair 0 only) / MASK-V EFFECT; FORCED-B EFFECT
   (spurious) / FORCED-V EFFECT; SAT-B NULL / SAT-V EFFECT (0.589);
   V0-WIN NULL; V0-ROUTE NULL (0.974 vs 0.992, lo -0.065); V0-RULE NULL.
   All normals >= 0.99. No fixture repaired.
A5 checks.py smoke on UNWIRED-B, MASK-B, PROBE-B (partial matrix, not
   scored). Found my own bug: K5 recorded the DEFAULT variable (S) for the
   normal run and the declared variable (r) for the arm, so it compared
   different variables and "passed" on an unwired arm. A check aimed beside
   its claim. Fixed: both runs record the fixture arm's declared variable.
A6 checks.py full run: 21 fixtures x 16 checks, 0 ERROR, ~12 min CPU
   (2 threads). out/matrix.json, out/checks_run.log.
A7 score.py (frozen rule): out/scores.json, out/matrix.md. Best single
   check K2 (positive-control plant through the arm's own code): 7/10 caught,
   0/11 false alarms, J 0.70. Min zero-FA cover {K2, K4d, K7} (alternatives
   {K1g,K2,K7}, {K2,K7,K9}). Identical-arms alarms (K3, K3b, K3c) false-alarm
   on V0-WIN and V0-RULE (true nulls). K3b (end-state digest + trace) is
   weaker than K3 (trace): end states coincide for V0-RULE (r toggles back)
   and V0-WIN.
   Fixture caveat found in the data: WIN-B's C1 window dropped NOTHING
   (K4c applied 0; arm bit-identical), easier than the real C1 M3 case.
A8 POST-HOC exploratory (not scored, declared here after seeing A7):
   posthoc.py, WIN-B/-V at iti 2 (stale waves inside the C1 window).
   WIN-B-iti2: normal 0.961, arm 1.000 (NULL), applied 390 tick-worlds,
   arm not identical. Caught ONLY by K1 (actuator reach 0.0) and K2/K2iso;
   K1g (all-site twin reach), K3, K3c, K4c, K5 all PASS. WIN-V-iti2: all
   pass. out/posthoc_win_iti2.json.
