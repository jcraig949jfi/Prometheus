# PREREG WTP-05 -- DESERT CROSSING: stateful developmental tensor worlds

Seat: Ensorain[ubu006-4b001784]. Date: 2026-10-10. Host: ubu006 (4 cores, 15 GB).

Authority:
- Operator directive 2026-10-10 (roles/Ensorain/prompts/2026-10-10_wtp05_directive/, verbatim + MANIFEST).
- Phase 2-B campaign C-014 (ops/campaigns/C-014/), packet C-014-E1; sub-assay C-014-E2 under its own
  prereg (ensorain/wtp5/PREREG_E2_REVIVAL.md @232dbe90f).

This document, the engine ensorain/wtp5/, its tests, the PROBE rows and the admission table are committed
BEFORE any SCREEN row. WTP-04 is preserved exactly as recorded (ISLANDS_MAPPED) and is not reinterpreted.

## 0. Questions (kept separate; never collapsed into one fitness number)

- Q1 Can a bounded organism with working state, lifetime plasticity, reusable modules and a search archive
  cross a reachability desert that the existing Ensorain regressors cannot cross?
- Q2 If it does, which mechanism made the crossing possible?
- Q3 Does longer search cross only rarity, or does new machinery cross composition?

## 1. Engine (new; ensorain/wtp5/)

| file | contents |
|---|---|
| tape.py | the TAPE organism and its interpreter |
| worlds.py | families A, B, C, N |
| planted.py | constructed solutions (never imported by the search; a test asserts it) |
| nulls.py | null ladder |
| certify.py | independent rung certifier |
| mutate.py | variation operators |
| search.py | arms |
| campaign5.py | finish-in-place runner |
| ablate.py | controls, RG, accounting |
| assays.py | reachability diagnostics |
| admit.py | world admission |
| revival.py | E2 |

Runtime: Python 3.14.4, numpy 2.3.5 (ensorain/requirements.txt). Rows are ubu006-bound.

## 2. Worlds (worlds.py docstring is normative)

Observations are LOCAL: 8 channels = 4 payload, event flag, tag, gate flag, bias.
- Corridor steps carry random +-1 payload on every channel.
- The gate observation is identical whatever the hidden context (tested).
- Actions are +-1; only gate steps are scored; chance is .5.

### 2.1 A -- delayed-context maze

- A cue cA (and for R1/R3 a second cue cB) is shown, then disappears.
- Three tag-0 distractor events give structured ambiguity.
- After a 15-step horizon, a locally identical junction requires:
  - R0: cA;
  - R1: cA or cB (asked by tag);
  - R2: cA * b, with b a local bit (FLIP / XOR);
  - R3: cA * cB * b (parity-3).

### 2.2 B -- rank-1 tensor lock

- Factors a, b (and c) in R^2 are shown at separated times.
- The lock requires sign(u.a) sign(v.b) [sign(w.c)], with fixed unit vectors u, v, w. This is contract(A,B):
  neither factor alone carries information (P = .5 given one factor).
- Factors are continuous, so literal lookup is useless.

### 2.3 N -- NON-TENSOR-NATIVE hidden finite-state process

- R2: the parity of a variable-length bit stream, interleaved with corridor noise.
- R3: a mode event selects which of two interleaved streams' parity is asked ("context(A) selects
  operation(B)").
- The answer is a finite-state machine, not a TT/CP/low-rank target.

### 2.4 C -- law switch (lifetime-plasticity world)

- 12 blocks. A type-1 law (s -> s) flips sign at an unannounced block in [4, 8]. A type-2 law (q -> q) never
  changes: this is the unrelated competence that must not be destroyed.
- The working state resets every episode, so only lifetime plasticity can track the switch.
- C conditions:
  - DESERT: one switch.
  - STEPPING: an early practice reversal at block 2 that reverts. This adapts directive s15: the sub-skill is
    "track a reversal".
  - YOKED: block 2's type-1 trials are replaced, at the same count, timing and weight, by an unrelated
    reactive type-3 behaviour.

### 2.5 Conditions for A / B / N (directive s15)

- DESERT: only the final gate is scored.
- STEPPING: two extra scored gates that are legitimate sub-skills.
  - A: a final-format gate with b = +1 (the context alone), and a gate right after the cues are re-shown
    (a short history suffices).
  - B: the primitives sign(u.a) and sign(v.b).
  - N: a final-format gate mid-stream (a shorter parity).
- YOKED: the same number, timing and weight of extra gates, scored on an unrelated reactive behaviour (the sign
  of a random payload channel at that gate).
- No stepping stone encodes the final program.

### 2.6 Composition ladder

R0-R3 per family as certified (s6).
- R4 (reuse) and R5 (promotion) require the optional nested family D (directive s6). D is not built in this
  prereg. R4/R5 are reported NOT_TESTED, and module reuse is reported descriptively (CALL counts and the
  module-removal controls).

## 3. Organism and search

### 3.1 TAPE (tape.py)

WORKING STATE:
- S <= 8 slots x 8 floats (<= 64), reset every episode.
- Persistent across steps unless overwritten by WRITE (clipped to [-1e3, 1e3]).

LONG-TERM MEMORY:
- CONST / LIN / BILIN parameter tensors; BILIN is dense or rank-1.

PROGRAM GRAPH:
- Typed DAG, <= 32 nodes.
- Primitives: OBS READ CONST CH ADD MUL SIGN SEL LIN DOT BILIN PERM WRITE ACT CALL.
- Library: <= 4 pure modules of <= 10 nodes, invoked by CALL.

### 3.2 Timescales

- FAST = within-episode working state.
- MEDIUM = lifetime plasticity between blocks of K = 32 episodes.
  - Antithetic finite-difference (ES) updates of the parameters flagged plastic.
  - Rule: theta = clip(theta + eta * sum z(r_k) eps_k / (K sigma), -1, 1). Plastic parameters are bounded;
    without the bound the update stalls, as found in dev (s10).
  - No update inside an episode.
- SLOW = evolutionary search over genomes.

### 3.3 Operators (mutate.py)

- Baseline, every arm: add, delete, rewire, perturb, change op, change S.
- L arm adds: plastic flag toggle; eta / sigma.
- P arm adds:
  - DUP: duplicate a cone and reconnect one typed port;
  - PROMOTE: reify a cone with <= 2 external inputs into a module, replaced by CALL;
  - CALL insert;
  - FREEZE;
  - module perturb.

### 3.4 Arms (search.py)

- base: (mu+lambda), mu = lambda = 32, tournament 3. The top 8 survivors are re-evaluated every generation
  (running-mean fitness).
- R: Go-Explore archive keyed by stepping-stone DESCRIPTORS:
  - per-role accuracy bins;
  - latents retained in working state (certificate-style, never the construction);
  - slots in use; module count; plastic flag.
  - Half of the parents come from the archive, weighted 1/sqrt(1 + selections).
- Rr (random-checkpoint archive control): the R machinery keyed by a genome hash mod 64, with P and L on
  (matched to RPL).
- Combinations: P, L, RP, PL, RPL. RL is dropped (fractional design, directive s13).
- Final evaluation is ARCHIVE OFF: the elite runs alone, on held-out seeds.

### 3.5 Fitness

fitness = share of lifetime reward - complexity, where complexity is:
- .001 per main node;
- .01 per module + .001 per module node (frozen modules at half);
- .001 per executed module node per CALL.

Promotion therefore costs fitness and is never automatic. The rung is NEVER fitness.

## 4. Planted solutions (planted.py)

| world | planted nodes | rung certified |
|---|---|---|
| A-R0 | 20 | latch |
| A-R1 | 23 | R1 |
| A-R2 | 22 | R2 |
| A-R3 | 25 | R3 |
| B-R2 | 27 (29 stepping) | R2 |
| B-R3 | 32 | R3 |
| N-R2 | 26 | R2 |
| N-R3 | 36 | R3 |
| C | 8 (plastic) | -- |

- Every planted A/B/N solver scores 1.000 on its world's scored gates and certifies its rung.
- The C solver tracks the switch: block accuracy recovers within ~3 blocks. Its late type-1 accuracy (.80 in
  dev) is below the .85 certificate. The C certificate is therefore calibrated to .75 (s6), still far above a
  static mapping's 0.
- Planted solvers are used only for expressibility, solvability, minimum-mechanism size, calibration and the
  s9 diagnostics.

## 5. Null ladder and admission (nulls.py, admit.py)

Cheap competitors first. Every null is fitted in hindsight (favourable to the null) and scored on held-out
gates:
- N0 constant;
- N1 reactive;
- N2 short history k <= 4;
- N3 bounded-memory register (current obs + the last event's payload and tag);
- N4 the existing Ensorain menu (WTP-03 table / additive / lowrank / cp / tt / dct on a window tensor index);
- N5 short planner = N1 (actions never change observations here);
- N6 unbounded full-history quadratic ridge: a reference, not used for admission.

Admission:
- H_null = (best of N0-N4 - .5) / .5.
- GOLDILOCKS .2-.8; TRIVIAL > .8; DESERT_CONTROL < .2 with a small certified planted solver; INACCESSIBLE
  otherwise.
- The table is ensorain/runs/wtp05/admission.json, committed with this prereg.
- Desert variants are DESERT_CONTROLs by construction (no cheap null clears them). Stepping variants carry the
  Goldilocks mix. This is the directive's "deliberately harsh desert controls, distinguished".

Admission result (ensorain/runs/wtp05/admission.json, seed 6_100_000):

| variant | label | H_null |
|---|---|---|
| A-R0 / R1 / R2 / R3 desert | DESERT_CONTROL | .09 / .01 / .10 / .03 |
| A-R2 / R3 stepping | GOLDILOCKS | .52 / .34 |
| A / B / N yoked | GOLDILOCKS | .68-.70 |
| B-R2 / R3 desert | DESERT_CONTROL | .05 / .05 |
| B-R2 stepping | GOLDILOCKS | .49 |
| N-R2 / R3 desert | DESERT_CONTROL | .03 / .07 |
| N-R2 / R3 stepping | DESERT_CONTROL | .07 / .17 (the mid-stream parity gates defeat the nulls too) |
| C desert / stepping / yoked | GOLDILOCKS | .54 / .57 / .57 |

- Every planted A/B/N solver certifies its rung.
- N6, the unbounded full-history quadratic reference, solves A-R0/R1/R2 (.98-1.0). It fails A-R3, B and N
  (<= .57; .82 on B-R2-stepping), as their targets are cubic or non-polynomial in the raw history.
- Caveat: C's plastic planted solver beats the best static null on total reward by only .00-.03 (ES
  exploration noise costs reward in stable phases). Its advantage is concentrated after the switch, which is
  what the C certificate measures.

## 6. Certifier (certify.py; never fitness)

Probes:
- Held-out seeds.
- A normal lifetime first, then 4 probe blocks of K = 64 with plasticity frozen at the learned parameters.

Tests:
- Behavioural pass: final-gate Wilson 95% lower bound >= .85.
- RETAINED latent: some single working-state channel agrees in sign with it on >= 90% of probe episodes
  (either polarity, each tested as a true sign match).
- Necessity for R2+: the accuracy with the working state reset every step must be <= .60.

Rungs:
- A: R0 cA retained | R1 cA and cB retained | R2 pass A-R2 | R3 pass A-R3.
- B: R0 one factor sign retained | R1 both | R2 / R3 pass.
- N: R0 mode retained | R1 both parities retained (N-R3 probe) | R2 / R3 pass.
- C: SWITCH_TRACKED if late type-1 accuracy (blocks >= switch+3) >= .75 and type-2 >= .90.

Score = the highest certified rung (-1 = none).

## 7. Stages and sizing (measured throughput, PROBE s10)

Throughput:
- Measured during PROBE with the machine fully loaded: 38-75 evaluations/s per run-core on A/B/N, 120-140 on C.
- Sizing assumes 50 (A/B/N) and 130 (C).

### 7.1 SCREEN

- 8 seeds per cell, 16,000 evaluations per run, logs every 2,000.
- Seeds 51_000_001 .. 51_000_008, never used before.
- 3 workers, nice 10, wall cap 12 h. Unfinished runs carry over (finish-in place) and are scored at the
  evaluations they reached.
- Cells (40 cells, 320 runs, estimated ~9.5 h):
  - G1 factorial, deserts: A-R2-desert and N-R2-desert x {base, R, P, L, RP, PL, RPL, Rr} (16 cells).
  - G2 conditions: {A-R2, N-R2} x {stepping, yoked} and B-R2 x {desert, stepping, yoked}, each x {base, RPL}
    (14 cells).
  - G3 plasticity: C x {desert, stepping, yoked} x {base, L} (6 cells).
  - G4 harsh R3: {A-R3-desert, N-R3-desert} x {base, RPL} (4 cells).

### 7.2 Kill rule after SCREEN

- Metric m = best certified rung per seed (C: 1 if SWITCH_TRACKED else -1).
- A non-base cell SURVIVES if either:
  - the one-sided 90% bootstrap upper bound of mean(m_arm) is above mean(m_base) of the same world and
    condition, and the point estimate is >= mean(m_base); or
  - any of its seeds reached a rung that no base seed reached.
- Base cells continue whenever any cell of the same world and condition survives (matched-compute
  reference).
- At most 12 cells go to DEEP, ranked by the mean rung gain over base, then by the share of seeds at the
  cell's maximum rung.

### 7.3 DEEP

- Surviving cells continue from their SCREEN checkpoints (finish in place).
- Per-run budget B_deep = min(400,000, floor(36 h x 3 workers x 3600 x thr / n_runs)), where thr = the mean
  SCREEN throughput.
- Wall cap 48 h.
- FLAT STOP: a run stops early when, over its last max(50,000, 40% of its evaluations), there was no new best
  rung, archive growth < 5% and best-fitness gain < .01.

### 7.4 EXTENDED

- At most one arm (8 seeds). It is the DEEP cell with the largest rung gain over base that passes the s8
  controls; failing that, the cell whose best rung was still rising at DEEP end.
- It continues to a 72 h total for that arm, under the same flat-stop rule.
- Nothing continues if the frontier is flat.

## 8. Controls, reachability gain, accounting (ablate.py; directive s20, s23, s24)

Run on every certified R2+ elite, and on the best elite of every DEEP cell:
- working-state reset;
- plasticity frozen;
- shuffled lifetime history;
- module removed;
- random module of matched size;
- the Rr arm (random archive checkpoints) as the archive control.

Reachability gain, measured causally at the same subsequent budget (one lifetime):
- RG_state, RG_plastic, RG_shuffled_history, RG_module, RG_random_module = accuracy - accuracy with the
  artifact ablated.

Cognitive accounting:
- environment (best cheap null);
- inherited structure (birth block);
- lifetime learning (end - birth);
- working state;
- promoted modules;
- search / archive (lineage: whether any archive branching is in the elite's ancestry);
- certifier gap.

Transfer, for R2+ elites (directive s22):
- new seeds;
- longer horizon (T = 24);
- reskinned statistics (A: 6 distractors; N: bit rate .7; B: factor tags swapped);
- novel combination: NOT_TESTED (no D).

Non-tensor-native readout:
- the elites' tensor ops (LIN / BILIN / DOT) are counted and ablated one at a time.
- "Selected a tensor substrate" = a tensor op is causally necessary (ablation drop >= .1) in an N elite at R2+.

## 9. Reachability assays (assays.py; diagnostic arms, not the main result)

For every composed world whose desert has no R2 at DEEP end:
- one-edit break + repair (8 breaks, 1,500-evaluation repairs);
- partial-mechanism seed (planted minus its final composition; 4 x 3,000 evaluations);
- the stepping vs yoked contrast.

Each failed rung is assigned named bottlenecks (EXPRESSIBILITY / REACHABILITY / REWARD / CREDIT / DETECTION /
OPTIMIZATION / RESOURCE) by the rules in assays.py's docstring. "Didn't learn" is never written.

## 10. Dev and PROBE disclosures (all before this commit)

Instrument fixes made during dev:
- Flag decoders in the planted solvers: a tag-0 event was passing a tag-+1 gate.
- C stimulus moved onto the gate step: it had accidentally been a memory task.
- Plastic parameters bounded: ES on a sign output stalls once |theta| >> sigma.
- Family A gained distractors: N3 "remember the last event" solved A-R0 and A-R2 perfectly without them.
- Certifier polarity bug: an all-zero channel counted as retained.
- Interpreter and world generation vectorised; no semantic change; planted results identical.

PROBE (ensorain/runs/wtp05/probe/, seed 9_500_001, 6,000 evaluations per run, 1 worker):
- The only certified rung was R0, in A-R2-stepping with RPL. A-R0/R1/R2 deserts (base), A-R2-desert RPL,
  N-R2-desert RPL and B-R2-stepping RPL reached nothing certified.
- C: base and L reached no SWITCH_TRACKED certificate. Their best fitness (.84) is selection on lucky
  late-switch lives, which the certifier correctly refused.
- The directive s18 gates for long runs: planted solvers pass; nulls behave (admission table); a stateful arm
  cleared R0 (PROBE); throughput measured.

Correction (not an edit to WTP-04): RESULTS_WTP04_MAP.md s5's "~29 s per unit-core" should read "~29 s wall
per unit at 3 workers (~86 core-s per unit)".

## 11. Primary result (directive s28), mechanical, in precedence order

- INSTRUMENT_FAILURE: any planted A/B/N solver fails its certificate on the eval seeds; or the ws_reset
  control fails to collapse a planted R2 solver; or admission finds no DESERT_CONTROL / GOLDILOCKS world.
- DESERT_CROSSED:
  - some non-base arm certifies R2+ in a composed DESERT world in >= 4/8 seeds while base is <= 1/8 at
    matched evaluations;
  - every crossing elite passes ws_reset necessity;
  - at least one machinery is credited:
    - P, when module removal and the random module each drop accuracy by >= .2;
    - L, when frozen plasticity and shuffled history each drop it by >= .1;
    - R, when the Rr cell reaches the rung in <= 1/8 seeds.
  - If the crossing is unattributed it is reported, and the primary result falls through to the next class.
- STEPPING_STONES_REQUIRED: in some composed world, R2+ in the STEPPING condition in >= 3/8 seeds (any arm),
  while that world's DESERT cells are 0/8 in every arm and its YOKED cells are <= 1/8.
- RARITY_ONLY: from SCREEN to DEEP end, no cell's maximum rung rises, while the share of seeds at an
  already-reached rung rises in >= 1 cell.
- COMPOSITION_WALL_CONFIRMED: instruments pass and no composed-world desert cell certifies R2 in any seed at
  DEEP end.

All five conditions are also reported as booleans. The report answers the four directive s32 questions
explicitly.

## 12. Predictions (made after PROBE and before any SCREEN row)

| id | prediction | p |
|---|---|---|
| P1 | No arm certifies R2 in A-R2-desert or N-R2-desert during SCREEN | .8 |
| P2 | A-R2-stepping RPL certifies R2 in >= 3/8 seeds by DEEP end | .4 |
| P3 | C: L certifies SWITCH_TRACKED in >= 4/8 seeds in at least one C condition; base 0/8 | .6 |
| P4 | R3 deserts: 0/8 everywhere | .9 |
| P5 | B-R2-stepping: R2 in >= 1 seed by DEEP end (the primitives give a real gradient) | .5 |
| P6 | R beats base on mean best rung in >= 1 desert; Rr does not | .4 |
| P7 | Primary: COMPOSITION_WALL_CONFIRMED .35, RARITY_ONLY .25, STEPPING_STONES_REQUIRED .25, DESERT_CROSSED .10, INSTRUMENT_FAILURE .05 | -- |

## 13. Limitations, stated in advance

- One organism family (TAPE).
- Fixed laws: u, v, w are the same in every lifetime of B, so evolution can learn them as inherited structure.
  A modes-reordered transfer test exposes this.
- R4/R5 untested without D.
- Budgets are ubu006-bound. A crossing that needs 10x the evaluations would read here as a wall, so the
  RESOURCE bottleneck is reported where the frontier is still rising.
- A non-Claude adversarial review is requested (C-014 F-COI).

## Amendment 2026-10-10 ~13:40Z: DEEP mechanics implemented (during SCREEN, before analysis, before any DEEP row)
s7.3 already specified the DEEP rules, but they had no code. This adds the code and changes no rule:
- `Run.frontier_flat` / `--flat-stop`: the s7.3 FLAT STOP, word for word.
  - Window = max(50,000, 40% of evals). It never fires before the window has fully elapsed.
  - The best-fitness gain is the window's maximum minus the maximum before the window.
  - A flat-stopped run counts as finished and is flagged `stopped_flat`.
- `campaign5 --from-stage screen`: a DEEP run copies its SCREEN checkpoint and continues it to B_deep. The
  SCREEN checkpoint is left untouched.
- Wall cap: DEEP runs with `--max-wall-h 48`.
- `_job` still accepts the 7-field jobs of the SCREEN runners that were already running, so the running shards
  are unaffected. Their logs show no error.
- Test: tests/test_wtp5.py::test_flat_stop_rule. A scratch continuation run (600 -> 1,200 evals) was checked
  for telemetry continuity.

## Amendment 2026-10-10 ~14:30Z: s8/s9 drivers written (during SCREEN, before analysis)
- ensorain/wtp5/post5.py runs ablate.controls, accounting, transfer and the s8 tensor-op readout on every
  R2+ run plus the best run of every cell. It also runs the s9 assays with mechanical bottleneck labels.
- The ablated genome is each run's exact final elite, loaded from its checkpoint. The JSON copy (4 dp) is only
  a fallback, and every record names its source. The final elite can certify lower than the run's best rung;
  both are reported.
- Repair counts only the edits that actually broke the planted solver: `n_broken` and `repaired_of_broken`
  (an additive field in assays.py).
  - OPTIMIZATION = fewer than half of the broken solvers are repaired.
  - If no edit breaks the solver, OPTIMIZATION is not assigned.
- DETECTION is approximated by the best-fitness (training-distribution) value being >= .9 in the failing
  cell. This is disclosed, because a held-out training accuracy is not separately computed.
- RESOURCE = some run's current best rung was first reached in the last 40% of its evaluations.
- The certifier gap is reported as None (not computed).
