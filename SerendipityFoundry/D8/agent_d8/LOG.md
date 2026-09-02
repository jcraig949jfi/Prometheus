# D-8 engineering log (pre-freeze calibration and validation)

All timestamps local (2026-08-28). CAL/VAL seed blocks only until freeze.

- Built SVM-8 substrate, task families, M0 suite, M1 machinery, controls,
  orchestrator. Smoke test: task generation + M0c run OK (unsolved task,
  best 2/6 — no conclusion drawn; that is what calibration is for).
- Declared informativeness band BEFORE calibration: primary M0 solve rate
  on CAL F1–F3 in [0.15, 0.60] (recorded in PREREG.md §14).
- CAL1 launched: M0a/M0b/M0c on CAL battery (F1 x10, F2 x10, F3 x10,
  F4 x8, F5 x4), budget 3000.
- CAL1 RESULT (ledgers/cal_1.jsonl): F1-F3 solve rates M0a 0.67, M0b 0.67,
  M0c 0.73 — ABOVE the declared band [0.15, 0.60] (battery too easy;
  bimodal: trivia solved by everything, rest by nothing). F4 = 0.00 for all
  arms (held-out family vacuously unfindable). F5 = 0.00 as expected.
- PRE-FREEZE TUNING (logged, CAL seeds only): (1) F1/F3 generator lengths
  5-10 -> 7-12; (2) added oracle-side triviality screen: generator is
  resampled if a fixed 250-candidate uniform random probe (uid-seeded,
  independent of learner streams) reproduces all 6 revealed outputs;
  (3) F4 templates reduced to 1-2 constants, 5 templates, lengths 5-8, so
  the held-out family has nonzero findability. tasks.py updated.
- CAL2 launched with the tuned generators.
- CAL2 RESULT: F1-F3 rates M0a 0.20 / M0b 0.37 / M0c 0.33 — in band.
  F4 still 0.00 for all arms.
- PRE-FREEZE TUNING: added an easier commutative F4 template
  (x_{p0}+a+x_{p1}) so the held-out family is not vacuously unfindable
  (CAL3: F4 still 0.00 for M0 on n=8).
- F4 probe (CALF4X mini battery, 15 tasks): M0b/M0c solve 0/15, best
  byte-matches 1-2 — byte-exact match-count fitness gives search almost no
  gradient; M0 weaker than the charter demands.
- PRE-FREEZE INSTRUMENT CHANGES (all arms identically, learner-side,
  family-agnostic, declared before any binding evidence): (1) search
  fitness = bit-level agreement over the 6 revealed pairs (0..48); the
  SOLVE predicate is unchanged (6/6 byte matches + 24 hidden byte matches);
  (2) literal tokens get a local +-1..8 wraparound perturbation on half of
  point mutations. Rationale: independently justified partial-credit
  signal, declared pre-freeze per charter section 7.
- CAL4 (B=3000, bit fitness): M0b 0.33 / M0c 0.20; F4 mini battery still
  0/15. Budget-sensitivity test: at B=20000 M0c solves 1/6 F4 (and hits
  5/6 on another) -> F4 findable in principle, budget-limited.
- PRE-FREEZE TUNING: global BUDGET 3000 -> 10000 for every arm.
- CAL5 (frozen config): M0a 0.23 / M0b 0.50 / M0c 0.33 (band OK).
  F4 0.00 on n=8 (accepted: stretch family; weak-baseline caveat will be
  attached to transfer analysis). CAL6 replicate: M0a 0.17 / M0b 0.30 /
  M0c 0.27.
- COMPARATOR SELECTION (frozen rule, pooled CAL5+CAL6, n=60 F1-F3 tasks):
  M0a 0.20, M0b 0.40, M0c 0.30 -> PRIMARY M0 = M0b (restart hill-climber).
  Note the confound this avoids: M1 is GA-based; measuring its advantage
  against the STRONGEST history-free comparator (M0b) is conservative.
  M1F vs M0c (same base) will be reported as decomposition evidence.
- Instrument validation suite V1-V8 launched.
- VALIDATION GEN 1 (ledgers/validation_1787897167.json, budget 2000):
  7/8 passed; V8 sensitivity FAILED (gain 0.08 < 0.15). Preserved.
- FIX: validation must run at the binding budget (10000).
- VALIDATION GEN 2 (ledgers/validation_1787897224.json, budget 10000):
  6/8. V3 "failed" at abs(d)=0.150000000000002 with NEGATIVE d (random
  history hurting is not the guarded failure mode) -> checks V2/V3 made
  one-sided (d <= 0.151). V8 FAILED HARDER (gain 0.00): the planted
  battery hit a ceiling (M0c solved 0.92 of it) and the hand-picked motif
  was mostly dead code (suffix LD0 made tasks near-identity). Preserved.
- FIX (V8 redesign, oracle-side validation tooling only): planted tasks
  now require the triviality screen, the degeneracy filter, AND a
  load-bearing check (deleting the motif changes >= 12/24 hidden
  outputs); motif chosen as the first pool-A motif whose battery has
  M0c <= 0.25 at the binding budget (selection log preserved in the
  validation JSON). Sensitivity controls are allowed to be placed in the
  detectable regime; this is instrument engineering, not evidence.
- VALIDATION GEN 3 (ledgers/validation_1787897332.json): 8/8 PASSED.
  V8: planted-motif battery M0c 0.00, macro-armed arm 1.00, ablation loss
  1.00 — the admission pipeline can detect a true object and its ablation.
- PRE-FREEZE DESIGN CHANGE (symbolic-hoard richness): mini-dev showed the
  hoard admission bar (>=5/6 byte matches) starves history (4 records
  after 6 tasks). Widened: also admit bit-fitness >= 40/48 at weight 1
  (solutions w=6, near-solutions w=5). Probe-behavior dedup keeps the
  hoard compact; history-construction cost is metered (hist_evals).
  Mini-dev recheck: 39 records after 6 tasks.
- VALIDATION GEN 4 launched under the final freeze-candidate code (gen 3
  ran before the hoard-admission edit; discipline requires validation to
  pass under the exact frozen code).
- VALIDATION GEN 4 (ledgers/validation_1787897401.json): 8/8 PASSED under
  the final code. FREEZE follows immediately; no further code, config,
  threshold, or task-generator changes after this point. Binding order:
  dev -> hrnd -> eval arms -> ablz -> stats. No binding output may be used
  to modify anything.
- FROZEN (frozen/MANIFEST.json), m0_primary=M0b.
- BINDING: dev 27/60 solved, hoard 1034, 8 macros promoted. hrnd built
  (298 records after dedup — count mismatch vs M1 hoard noted as a
  weakness, NOT repaired post-freeze). All 20 eval arms run. Stats run
  once, untouched.
- VERDICT: S0 (primary delta +0.100, CI [-0.033,+0.233], McNemar p=0.21).
  0/8 z admitted. No budget violations. See REPORT.md — packet complete.
- Post-hoc only after verdict: z3 = NOT(x>>1) via NEG(128)=128 overflow
  fixed point (inert fossil, preserved); z2 reused in 8 novel solutions
  with zero ablation consequence (correctly refused).
