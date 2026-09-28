# W-H LOG

## Attempt 0 (setup) 2026-09-28
- Read COMMON_RULES.md, COMMON_RULES_ARC3.md, W-H brief.
- Read engine/lens/plants/envs/search/assays.evaluate; W-B scripts and W-B
  out/*.json (raw numbers only). No context contamination: did NOT read W-B
  REPORT/PLAN/LOG or any principal interpretation file before PLAN.
- Static disasm of b59e6c3a, 311c465f, 95649e2c, faafa5b0 (W-B disasm.py).
- timing.py: CPU 2 threads, 96x8 worlds one generation = 19.1 s.
- PLAN.md frozen.

## Attempt 1 (Part 0 observation) - BUG
- obs.py recorded w.S.cpu().numpy() on CPU tensors = views of live state,
  so every recorded tick aliased the final state (S0 constant). Caught by
  checking recorded S0 against the engine trace (1.2% agreement). Fixed by
  .copy(); rerun. Normal accuracies (unaffected): b59e6c3a .741 [.707,.772],
  311c465f .755 [.715,.797], 95649e2c .665 [.648,.680].

## Attempt 2 (Part 0 observation, fixed) -> mechanisms in PLAN ADDENDUM A
- S1 readout-site transition table (awake ticks): r_pre=0 & CNT0=0 -> 0
  (11110/11110); CNT0=1 -> 1 (198/198); CNT0=2 -> 2 (12/12). Rule 1 sets
  S0=776, ramp -60 per awake tick in rule 0 (trace world 0 trials 3-5).
- S2 world 0: rule-1 tick = the awake cue tick in trials 3 and 5 (S0 := 399
  after decay of 256^200); in trial 4 rule 1 ran at phase 2 on a distractor
  (-64) and was right by luck of sign. S2 parity changes via decay (94->83).
- S3 world 0: -110 payload arrivals -> rule 2 next tick -> readout emits
  (forwarder) and holds S0; S0 = CNT0 in rule 0.
- Search arms running on GPU (lease token 2ce85284abe2).

## Attempt 3 (Part 1 counterfactuals, cf.py -> out/cf.json)
- S1 b59e: CF1 forbid readout rule switch -> .500 exactly (d -.241
  [-.272,-.207]) NECESSARY; CF1c same pin on a random other site -> d 0
  (control clean); CF2 force rule 1 at t0+5 in y=-1 trials -> .022
  [0,.088] on those trials (normal .947) SUFFICIENT-FLIP.
- S2 311c: CF1 forbid rule 1 on cue phases -> .495 (d -.254) NECESSARY;
  CF2 force rule 1 in the gap -> .528 [.449,.599] SUFFICIENT-CHANCE;
  DIAG force rule 1 at both cue phases -> .764 (= normal; the clock's own
  timing is already near its ceiling).
- S3 9564: CF1 forbid rule 2 at all sites (t>=2Pd-1) -> .600 (d -.070
  [-.087,-.055]) NECESSARY but partial; CF1r readout only d -.021
  NECESSARY (small); CF2 force rule 2 everywhere at t0+3 in y=-1 trials ->
  .495 vs normal .491 on those trials: NO-EFFECT. Note y=-1 trials score
  ~.49 in NORMAL runs (S0 = CNT0 >= 0 -> ties): all S3 competence is on
  +cue trials.

## Attempt 4 (Part 2 H arm, hand.py -> out/hand.json) - first try
- H1 (7 instr, rules=1) on S1 physics: .764 [.736,.793] >= A* .707.
- H2 (4 instr latch) on S2 physics: .999 [.995,1.0] >= A* .715 (champion .755).
- H3 (role-faithful forwarder, 9 instr) on S3: .511 FAIL.
- H3alt = H1 on S3 physics: .792 [.762,.824] >= A* .648.
## Attempt 5 (H3 debug, 3 iterations used, hand_h3dbg.py)
- iter1 no refractory: .512 (pos .887, neg .127: reverberation never dies).
- iter2 payload TTL (sum of arrivals defeats TTL): identical .512.
- iter3 halving TTL: .536 (pos .747, neg .304). H3 faithful design closed
  as FAILED (tuning a reverberation lifetime by hand); H3alt stands.

## Attempt 6 (S4 faafa5b0, ADDENDUM B; hand_s4.py -> out/hand_s4.json)
- champion on analysis worlds .590 [.560,.622] (A* .560).
- H4a plain S0 latch: exactly .750 (pos 1.0, neg .5) as predicted from the
  S - (S>>1) positive floor at 1.
- H4b Kp latch via WIMM (rules=1, 6 live instr): 1.000 on all 64 worlds.
## Attempt 7 (S5 ed884172, ADDENDUM C; out/hand_s5.json)
- champion .654 [.592,.717]; H4a latch .735 [.724,.744] (pos .984, neg .488).
