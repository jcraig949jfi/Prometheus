# SFE-05 -- H4 ADAPTIVE CHALLENGES x TRANSFER (record; directive IV shape)

## A. STARTUP

- experiment ID: SFE-05
- question: do adaptive challenge generation and transfer reinforce each
  other (interaction > 0 on an INDEPENDENTLY defined evaluation), rather
  than merely making the environment harder?
- starting commit: af666a099 (SFE-04 close); harness sfe05.py; the v01
  solver elites as the transfer set (archaeon/campaign1/ssf_seeds.py ->
  archaeon.wse.ssf._v01_solver_pop; committed rows of wse-survey-v01).
  No H4 kind exists anywhere in the repo (survey 2026-09-17): this is the
  first H4 alpha, built on the WSE grammar (D-011).
- services: engine v2 (one ISOLATED world; transfer set as an artifact;
  per-run adaptive schedule as an artifact; experiment + observation per
  cell x seed).
- world/spec: challenge = W1 cell (K=1, D=1, 4-bit) whose DELAY is the
  difficulty knob. FIXED: delay 4 every generation. ADAPTIVE: a sealed
  internal policy over the ladder {1,2,4,8,16}: start at 1; step up when
  the population's mean training reward >= 0.40; step down when < 0.10;
  the schedule is recorded per generation. TRANSFER OFF: random
  generation 0. ON: the v01 solver elites padded with randoms.
- evaluation (independent, fixed, identical for every cell): held-out
  family "eval", delays {1, 4, 16}, 24 episodes each; primary = mean of
  the three per-delay competences; per-delay values reported.
- seeds 1,2,3; N=200; G=80 generations, one generation per run_cell call
  (the loop is generation-atomic) with a per-generation branch label
  shared across cells (common random numbers per generation index) and a
  campaign-local child-generation rule identical to the loop's (elitism 4,
  tournament 4, one grammar operator per child).
- frozen assumptions: the WSE grammar and loop; the transfer set is the
  same organisms SSF cycles 1-3 transferred.
- controls: the 2x2 itself (fixed/off = baseline); the eval battery
  contains delay 16, which no arm trains on except adaptive runs that
  climb there; max_delay_reached per run is recorded so "harder" and
  "better" can be told apart.
- assay capability: fixed/off on delay 4 is expected at the floor (W1_d4
  unreachable de novo, L-017); the eval mean will then be driven by delay
  1 (reachable from the transfer set and, in some seeds, de novo: v01
  W1_d1 2/3 at 8-bit). If every cell's eval mean is at the floor the
  outcome is INCONCLUSIVE; if only transfer cells move, transfer_main is
  measurable and the interaction is the question.
- time: 12 runs x 80 generations x (200 x 16 x ~10 ticks x <=64 ops) ~
  2-4 min each on 12 procs; engine seconds.

- AMENDMENT before any engine run (D-012): the dry run showed the transfer
  set at eval 1.000 on W1 for every delay (a last-value register solves
  K=1 D=1 at any delay), so delay cannot separate the cells once transfer
  is on. The difficulty knob is now the DISTRACTOR count Kd of the stream
  cell (K=1, D=1, delay 4): ladder {0,1,2,4,8}, fixed Kd=4, eval battery
  Kd {0,4,8}. The transfer set scores ~1.0 / ~0.2 / ~0.1 there (SSF
  cycles): a real gradient. Everything else unchanged.

## B. EXECUTION

- one engine attempt (RECEIPT.json, rows.json; 86.3 s: startup 1.19,
  cells 79.9 on 12 procs, records 4.97, teardown 0.23; 0 errors) after two
  dry runs (the first exposed D-012). Design as amended: knob = Kd; ladder
  {0,1,2,4,8}; fixed Kd 4; eval Kd {0,4,8} x 24 episodes; N=200, G=80,
  E=16; generation-atomic loop with a shared per-generation RNG label;
  transfer set = 7 v01 solver rows' top-4 manifests (28 organisms) padded
  with randoms.
- engine: 1 session, 1 world, 1 hypothesis, 13 artifacts (transfer set +
  12 adaptive/fixed schedules), 12 experiments + 12 observations.
- decisions: D-011 (H4 alpha on the WSE grammar), D-012 (Kd knob).
  Failures: none. Restart: not needed. Repeated work: none.

## C. SCIENCE

- primary outcome (independent eval battery, mean over Kd {0,4,8}):
    cell            s1     s2     s3     mean
    fixed/off       0.069  0.042  0.042  0.051
    fixed/on        0.153  0.097  0.181  0.144
    adaptive/off    0.014  0.069  0.472  0.185
    adaptive/on     0.222  0.292  0.444  0.319
  adaptive_main = +0.155; transfer_main = +0.113; interaction = +0.042.
  per-Kd means (Kd 0 / 4 / 8): fixed/off 0.08/0.03/0.04; fixed/on
  0.01/0.22/0.19; adaptive/off 0.36/0.14/0.06; adaptive/on 0.63/0.25/0.08.
  max Kd reached by the adaptive policy: off [0,0,1], on [4,4,1].
- the landscape that matters: fixed/on LOST Kd=0 competence (0.00-0.04)
  while gaining at Kd 4/8 (0.22/0.19) -- the transferred last-value
  solvers, trained only at Kd 4 for 80 generations, evolved away from the
  easy case (a forgetting shelf); adaptive/on kept Kd=0 (0.38/0.50/1.00)
  and climbed to Kd 4 in 2/3 seeds; adaptive/off found Kd=0 de novo in 1/3
  seeds (1.000) but never climbed (mean reward stayed below the 0.40 step
  rule).
- controls: fixed/off baseline (floor); the eval battery includes Kd 8,
  which no arm trains on; max-Kd-reached separates "harder" from "better".
- assay capability: YES (fixed/off at the floor; three other cells move).
- evidence: adaptive challenges POSITIVE (weak, n=3; driven by retained
  Kd-0 competence and one climb); transfer POSITIVE (weak, n=3);
  interaction NOT ESTIMABLE (+0.04 at n=3; adaptive/on is the best cell
  in every seed but by margins inside seed variance).
- confounders: the adaptive policy's thresholds (0.40/0.10) were chosen
  without tuning and gate the climb -- adaptive/off climbed to Kd 1 only
  once; the transfer set is register solvers with no distractor handling,
  so "transfer" = a foothold at Kd 0; n=3.
- must NOT be claimed: reinforcement (interaction) between adaptive
  challenges and transfer; that adaptive challenges make organisms
  "better" rather than preventing the loss of easy competence (the per-Kd
  rows say the second).

## D. TEARDOWN

- 1 world TERMINATED (0.23 s); no orphans (4 python processes); logs
  under D:/Prometheus-data/archaeon/cmp1-sfe05.log. Clean for SFE-06: yes.

## E. BENCH IMPROVEMENT

BUGS: none. FRICTION: the loop is generation-atomic only by calling
run_cell with G=1 and rebuilding children outside it (a second copy of
the selection rule, L-021); no per-generation RNG label exists (L-008
recurrence: solved by a label per generation index).
MISSING TELEMETRY: the schedule artifact per run is the right object; a
per-generation held-out probe at EVERY ladder rung (not only the final
elite) would show forgetting as it happens (L-022).
AUTOMATION: adaptive policy + eval battery + artifacts + records ran in
86 s with zero manual steps.
TO MACHINERY: a generation-step API on the loop (L-021) so curricula,
ramps and schedules do not re-implement selection.
KEEP POLICY: the ladder, the step thresholds, the eval battery.
MISSING FAILURE STATE: "policy never fires" (adaptive/off stayed at rung
0 in 2/3 seeds: the up-rule was never met) -- record as
CURRICULUM_STALLED with the rung and generations.
MISSING RECOVERY: none. PORTABILITY: none. OBSERVABILITY: L-022.

## F. LANDSCAPE / GRADIENT NOTES

- The 2x2 means hide the forgetting shelf: eval at Kd 0 per cell (0.08 /
  0.01 / 0.36 / 0.63) is the strongest signal in the experiment and is
  invisible in the primary. A per-rung x per-generation competence matrix
  (from the schedule artifacts + a probe) is the landscape to keep.
- The adaptive schedules themselves (kd-paths: 0000..., 00111244444...,
  002222...4, 0111...) are strategy-switch traces; the rung at which the
  climb stalls (1 or 2 for transfer-off, 4 for transfer-on) is a cheap
  "reachable difficulty" measure per lineage.
- Dead region: the down-rule (< 0.10) never fired; the ladder only went
  up; a policy landscape (up/down thresholds) is untested.

DISPOSITION: COMPLETE. Science: adaptive main +0.155 and transfer main
+0.113 (both weak positive, n=3), interaction not estimable; a forgetting
shelf under fixed hard challenges with transfer. Instrument: 0 errors.
