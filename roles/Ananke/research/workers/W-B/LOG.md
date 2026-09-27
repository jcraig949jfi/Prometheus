# W-B LOG

A0 2026-09-27: read brief, COMMON_RULES, engine.py, lens.py, s_m3.py/json.
  Static disasm of both M3 genomes (disasm.py). Found: every rule variant
  has a SETRULE reading a register that is zero at tick 0 -> rule 0
  default; explains s_m3's 5442/6400 = 0.8 awake + 0.05. PLAN.md written.
A1 GPU lease acquired (token 949b0f52f816, ttl 90 min, fallback lease file).
A2 m3.py (X1-X8) on both M3 specimens, GPU, 62 s each. out/m3.json.
  First draft had a broadcasting bug in the X4_by_readout_r0 line; fixed
  before the first run (no results produced by the buggy version).
  Every bootstrap-only prediction held (details in REPORT.md).
  Surprise: X5d gave identical numbers for junk rules 1, 2, 3, and X5c
  frac0.25 = X5d. Not in PLAN: added X5e (junk_check.py) to test whether
  junk rules are simply silent. Result: uniform-k frozen for k=1..3 emits
  0 packets per world in both specimens; X5d traces bit-identical across
  junk rules. Junk rule = dead site.
A3 Census clarification written BEFORE running census.py: FA (freeze
  after settling) is scored on trials 2..end (the only trials it can
  affect), as s_m3 E2; all other arms on all trials. Duplicate genomes in
  the 42 rows are reported, not removed.
A4 census.py started (GPU, background). First 18 rows ~10 min; row 19
  (RELAY delta 16) slower. Partial view showed ONGOING/CUE_CARRYING rows;
  PLAN Addendum A (Part 3) written before any Part-3 run.
A5 deepdive.py on 6 non-bootstrap cells seen so far (0017d8cc c939c3c7
  faafa5b0 311c465f cc18858f dd6fdf49), run concurrently with the census.
  Static disasm of faafa5b0 (HOLD, sync): rule 0 never writes S0; rule 1
  writes S0 (from SENSE and inbox) and always returns to rule 0 next tick;
  rule 0 enters rule 1 when (CNT0 - ENERGY) is odd. A count-parity gate on
  when the hold register is written: a candidate genuine ongoing role.
A6 deepdive part 1 done (out/deepdive.json, 6 cells). r swap NO-EFFECT in
  all 6 (r never the bit carrier); pin readout r after settling HURTS in
  4 (0017d8cc, c939c3c7, faafa5b0, 311c465f; up to -0.28), pin all other
  sites EXACTLY 0 change in all 6. Added Addendum B (Y6/Y7, descriptive).
A7 phase.py (Y6/Y7) on 5 cells -> out/phase.json. 311c465f and faafa5b0:
  S0 written only by rule 1; readout enters rule 1 around cue onset.
  311c465f profile identical for y=+1/-1 (timing gate); faafa5b0 and
  c939c3c7 profiles sign-dependent (excursions mostly when y=-1), yet r
  at the readout tick does not predict y (Y3 ~0.51) and r swap NO-EFFECT.
A8 gate.py (Addendum C) -> out/gate.json. Z1 HURTS, Z3 HURTS as predicted;
  Z2 PREDICTION FAILED: pinned to rule 1 with no distractors is also
  chance (0.50). Hypothesis G as frozen (gate needed only against
  distractors) is refuted. Reading: rule 1 overwrites S0 from the current
  SENSE every tick, so a rule-1-only readout cannot hold at all; the
  rule-0 phase is the hold, not merely a distractor filter. Surprise:
  311c465f's own normal accuracy drops 0.76 -> 0.55 without distractors
  (the champion depends on distractor input; not followed up).
A9 census done: 42/42 rows, no errors, no duplicate genomes (out/census.json).
  Lease renewed: released 949b0f52f816, acquired f3b256647b52 (75 min).
A10 deepdive part 2 + phase on the remaining non-bootstrap cells:
  b059e735 95649e2c e2334ea7 369f5a5b 63d17a90 1d88af70 b59e6c3a 42716814
  (ONGOING), 8e1caf6b (UNRESOLVED), c7d7d2a4 88f94654 (PATTERN_BOOT).
  deepdive.py rewrites deepdive.json with only its argv cells, so part 1
  was copied to out/deepdive_part1.json first.
A11 deepdive part 2 + phase part 2 done; merged into out/deepdive_all.json
  and out/phase_all.json (18 cells). GPU lease f3b256647b52 released.
  r swap at mid: NO-EFFECT 17/18, CHANCE 1 (b059e735), FLIP 0.
  Pin readout r after settling: HURTS 12/18; pin all other sites: exactly
  0.000 change in 13/18, HURTS in 3 (95649e2c, 369f5a5b, 42716814).
  Six RELAY cells show a readout-site excursion to a non-zero rule in
  mid-interval in worlds of ONE cue sign only, back to rule 0 before the
  readout tick (Y3 = 0.50).
A12 Non-independence check: no identical genomes, but 5 of the 12 ONGOING
  cells share C1 lineage c939c3c7 (itself + 4 wave-B children with
  parent c939c3c7271e65d2). Effective n for "ONGOING" is smaller than 12.
A13 Scorecard vs PLAN: Part 1 all predictions held. Census: UNIFORM_BOOT
  25/42 = 59.5% (prediction >= 60%: MISSED narrowly); ONGOING 12/42 = 29%
  (prediction <= 20%: FAILED); CUE_CARRYING tag 12 (prediction <= 3:
  FAILED, but the tag = any partner r difference; Y1 shows r is not a
  carrier in any). Addendum C Z2: FAILED.
