# Nestor-H journal: MEASUREMENT builder (round 3)

Lane H, package F10, F12, F13, S1, S2, S3 (ROUND3_BACKLOG s3, DELEGATION_BRIEFS_R3_R6 sH).
Worktree nestor-bld-h, branch nestor/bld-h-2026-09-14. Threads: OMP = NUMBA = 2 (conductor
budget 1789425755152-0).

## 2026-09-14 epoch 1, iteration 1: F10 predicate hypotheses + round 2 prior-vs-reality

- Boot: Nestor[m1-4024f4bd] (claude-opus-5), bus hello 1789425880417-0, claim H-F10-predicate-resolver.
  Inbox: A's core + GPU budget (H = 2 threads). No GPU needed for this package.
- Code: primordial/score/predicates.py (schema, JSON row expressions, gate, evaluator,
  calibration) and primordial/score/round2.py (bus predicate posts -> receipts -> canonical
  predicates -> resolved on rows). Tests: primordial/tests/test_score_predicates.py.
- Rule kept: no verdict reads a prose field. Linking reads identifiers only: exp == exp_id
  for C/E; the B-R2-<n> token at the start of a B claim or the prefix of its exp_id. B
  per-cell prior keys (w3_128, int2_w4_128, a2_w4_8) are parsed against each QD row's cell;
  exactly one key must match. B verdicts are recomputed with qd_ledger.check over
  baseline rows (oracle_clean = QD status != cheat); C and E use the row expressions in
  C_TRANSLATION / E_TRANSLATION.
- Disclosed translation: 3 C predicates posted their threshold as a rule string (C-R2-02,
  05, 09). The table spells each rule over summary-row fields. Numeric thresholds come from
  the posts. E predicates (E-T1, E-T1b, E-T2) were translated per prior key from the posted
  comparator text.
- Result (37 round 2 receipts): 37 have a prior and 37 resolve by code into 43 units, 41 of
  them decided. Indeterminate: B-R2-4 int2 (clause A INELIGIBLE under skip-odd, later
  re-judged by B-R2-8 under its own predicate) and C-R2-08 (oracle gate failed).
  Recomputed B clause A == the verdict recorded on every decided B QD row. E-T1b rerun
  identity 120/120 was recomputed from rows.
- Calibration (decided only):
    all  n=41 prior .522 hit .756 brier .157 (under-confident by .23)
    B    n=28 prior .496 hit .821 brier .195; w3/w4 hit 1.00 at prior ~.55, w1 hit .44 at .38
    C    n=6  prior .317 hit .333 brier .067 (anti-prior cohort is calibrated)
    E    n=7  prior .800 hit .857 brier .082
  Reading: B underrated its own exploitation on w3/w4 and was about right on w1.
- Pushed 2ca077799 (integration + nestor/bld-h). Inbox after the push: A confirmed G-M1. The
  abstain-only floor beats every clause A baseline (w4 107.75, w3 122.62, w1 88.28), so the
  scorer must report BELOW_FLOOR and score nothing below the floor. The F10 B priors are
  therefore calibration on sub-floor baselines, not evidence of compression (acked to A and G).

## 2026-09-14 epoch 1, iteration 2: F12 scorer as a program

- Code: primordial/score/progress.py computes a per-cohort vector, never one score. Axes:
  compression (raw clause A PASS AND G's floor verdict PASS; BELOW_FLOOR, NO_HEADROOM and
  NO_FLOOR score 0; superseded rows dropped), landscape (distinct QD cells), failure_landscape
  (dev/aborted/timeout/cheat rows), anomalies_filed, anomalies_resolved (events backed by a
  committed rows file), refutations (board-eligible, refutes names ANOTHER lane's exp_id by
  identifier), kills_own (reported, unscored), corrections (superseding rows + receipts
  refuting own lane), instruments (PASS receipts whose rows hold cheat and control rows),
  transfer (NOT_OPEN until S1).
- G's floor lives on nestor/bld-g (f939148be), not yet on integration. progress.py reads
  check()['floor'] when present and treats its absence as NO_FLOOR, so it scores 0 either way.
- Round 2 replay vector:
    B  compression 0 (raw_pass 23, NO_FLOOR 28) landscape 28 failure 3 anomalies_filed 3 corrections 3
    C  landscape 13 failure 14 anomalies_filed 2
    D  failure 341 anomalies_filed 3 anomalies_resolved 4
    E  failure 145 instruments 1
  Round 2 had no refutations and no own-KILLs.
- Push held: the integration tip 660ab7f38 failed collection (test_fabric_hygiene.py:59, A's
  file). Asked A (1789427057457-0); A had already fixed it at fb15cc3a2. Rebased, suite 105
  passed, pushed b15d3aece via primordial.ops.push. The backup push to nestor/bld-h was
  rejected non-ff after the rebase (not forced).
- With G's floor rows live on integration, all 28 B clause A cells read BELOW_FLOOR, so
  compression stays 0 for cause.

## 2026-09-14 epoch 1, iteration 3: F13 budget enforcement

- Code: primordial/score/budget.py. The live source is F7's worker ledger (pm:jobs:<L>:done
  cpu_s, joined to pm:jobs:<L> specs for exp_id), windowed by stream-id time. Verdict per
  cohort vs 40/25/20/15: OVER / WITHIN / INDETERMINATE. INDETERMINATE applies when total
  < 60 CPU-s or any cohort is unmetered. Died jobs count with unknown CPU; nothing is guessed.
  `warn` posts one BUDGET WARNING per OVER cohort per epoch to <L>,A (SET NX dedupe).
- F12 now passes held=held64_by_run_seed to check (M3 band). F10 keeps the posted IQR rule.
- Round 2 replay from rows: INDETERMINATE. Only C recorded CPU (348 CPU-s); B, D and E rows
  carry wall time only. Wall time is not CPU, so the budget split was unmeasurable in round 2.
- Live epoch 1 report: 0 cohort jobs on the worker streams (INDETERMINATE). Cohorts must
  submit through the worker in round 4 for F13 to measure anything.
- Pushed 0ef4d600c. Posted EPOCH 1 (1789427422565-0). Its "tests=18" is wrong: H tests were 20
  (11 + 5 + 4).

## 2026-09-14 epoch 2, iteration 4: S1 clause B check-b

- Told G on the bus before touching qd_ledger.py (1789427441027-0). The change is a
  `check-b` subparser plus a dispatch branch only; check/floor_of/_check_raw are untouched.
- Code: primordial/score/transfer_b.py. Per (exp_id, family, donor, recipient) and per run
  seed: d = held_auc(graft) - held_auc(cheat) for rand_graft and shuffle_graft. p is the
  one-sided exact sign-flip (E's computation, reimplemented to avoid importing the harness);
  p_max over both cheats; Holm across world pairs WITHIN one experiment. Gates, any of which
  makes the pair INDETERMINATE (never FAIL): all conditions paired on every run seed; graft
  bytes unmodified and fused == numpy; oracle row clean (world 0 failing, skip_lin >= 14;
  brain 0 mismatched, cheat >= 14); planted positive self_graft p_max < alpha.
- E-T1b re-derived from rows, exact vs the harness summary on all 3 pairs:
    w2->w4   p_max 0.000275  Holm 0.000824  PASS
    w17->w3  p_max 0.3466    Holm 0.6933    FAIL
    w25->w1  p_max 0.7046    Holm 0.7046    FAIL
  self_graft p_max 1.5e-05 in every pair, and every gate is clean. The same code on E-T1
  (8 seeds) gives w2->w4 PASS (0.0039, Holm 0.0117) and w17->w3 / w25->w1 FAIL, matching E's
  report-only post-hoc graft-minus-cheat numbers.
- Reading for round 5: one displacement survives (the w2 linear genome grafted into w4).
  That result has not been re-run on new seeds, so it is not yet a primitive.
- Pushed c8a96d0cd; G confirmed no pending qd_ledger edits (1789427554676-0).

## 2026-09-14 epoch 2, iteration 5: S2 anomaly triage + S3 prior-vs-reality board

- S2 code: primordial/score/anomaly_triage.py. Epochs are 30 min from the first cohort hello
  (B 1789417224) to the last cohort message. Per epoch end: open = filed before the end, with
  the latest event not RESOLVED/REFUTED (INDETERMINATE stays open); resolved = closing events
  in the window; RAISE_D when open > 2x resolved. Triage order: children (ANOM-<id> in
  `source` only; prose is never read), then age, then id. A firing rule yields a
  proposal moving 0.05 of the split from B to D; the operator owns the split.
- Round 2 replay: epoch 1 open 14 resolved 3; epoch 2 open 14 resolved 1; epoch 3 open 14
  resolved 0. RAISE_D in all 3 epochs; proposal B .35 C .25 D .25 E .15. The backlog is
  mostly A's 10 seeded round 1 anomalies, which nobody resolved, so they lead on age.
- S3 code: round2.publish_board publishes F10 calibration to pm:board:prior_vs_reality
  (zset members <cohort>|<domain>|<metric>, replaced atomically), readable via
  `bus board prior_vs_reality` and exported by ops/bus_export. It is display only.
  CLI: python -m primordial.score.round2 --board.

# Round 4 phase P0 (SWARM_R4 s2 H-R4-1..3)

## 2026-09-14 P0 iteration 1: H-R4-1 round-versioned budget shares

- Boot: Nestor[m1-ff4b74b8] (claude-opus-5), ff-merged to 86a3825ae, bus hello 1789433610923-0,
  claim H-R4-1-budget-shares. PM_LANE=H, OMP = NUMBA = 2.
- Code: budget.py now has SHARES_R2 (40/25/20/15) and SHARES_R4 (35/25/25/15), SHARES_BY_ROUND,
  DEFAULT_ROUND = r4. `report` takes --round (default r4) and writes round + shares on its row.
  `replay-round2` is always judged against SHARES_R2. Its output is unchanged: INDETERMINATE,
  unmetered B/D/E, C 348.176 CPU-s, shares printed 0.40/0.25/0.20/0.15.
- Tests: the old report test pinned round 2 arithmetic, so it now passes SHARES_R2 explicitly.
  Two tests were added: r4 is the default (B 38% is OVER in r4 and WITHIN in r2, D 22% the
  reverse), and replay-round2 calls report with SHARES_R2. Suite 160 passed, 1 skipped, pytest rc 0.
- Not changed: anomaly_triage.SHARES is the round 2 split used by S2's replayed proposal, and
  S2 already proposed the 35/25/25/15 move.
- H-R4-2 schema: proposed worlds_r4.json to G and A (1789433688592-0). A accepted it with an
  amendment (1789433714703-0): per-cell `verdicts` for the four Q1 x Q2 variants
  (four_policy|gate_in x CULL|HOLD, where gate_in floor = max(floor, gate_held64) and HOLD
  replaces CULLED with HELD when gate_held64 > floor), NOT_REACHED recorded per variant, and
  NOT_REACHED cells included. check() reads the active pair only. Waiting for G's agreement
  before writing the reader.

## 2026-09-14 P0 iteration 2: H-R4-2 F12 scorer on worlds_r4.json

- Inbox: G accepted the schema plus bound fields (1789433928197-0): floor_is_bound, bound_parts,
  learner block, and the bootstrap = primordial.metric.ci.median_ci with PCG64 20260914. Operator
  message 13 made the active variant gate_in|HOLD (A 1789434918331-0); HELD is INELIGIBLE(HELD).
  G's HELD rule (1789435058202-0): HELD iff gate_held64 > four-policy floor AND ci95[0] <= the
  variant floor. cull_reason is BASELINE iff gate > four-policy floor, else WEAK_WORLD, else
  NOT_REACHED. H-R4-3 replays that rule. ff-merged to 076194e92.
- Code: primordial/score/clause_a_r4.py.
  - screen_of reads verdicts[<q1>|<q2>] from the file only. NOT_REACHED comes from cull_reason.
    A world that is absent, or missing the file, is UNSCREENED.
  - s4_verdict is SWARM_R4 s4 computed from the file's numbers. The floor is
    verdicts[variant].floor, never derived. The progress CI is median_ci mapped through the formula.
  - compression_r4 consults the judge (qd_ledger check) only on SURVIVED cells, and scores a PASS
    only if check's `clause_a_r4` block agrees (same verdict, |progress diff| <= 1e-9).
    Disagreement is MISMATCH and a missing block is NO_JUDGE; neither scores.
  - progress.py: vector(worlds=...), with CLI --round r2|r4, --since and --worlds. r4 writes
    F12-progress-vector-r4.jsonl. r2 output is unchanged (B raw_pass 25, BELOW_FLOOR 28).
- Asked G (1789435262391-0) for the G-R4-5 names: check() returns res['clause_a_r4'] = {verdict,
  why, progress, progress_ci, floor, baseline_median, baseline_bytes, variant, screen}, and
  worlds_r4.json writes verdicts[v].floor. Reader adapts if G picks other names.
- Tests (test_score_clause_a_r4.py, 11): active variant only (a four_policy SURVIVED under an
  active CULLED reads CULLED); planted progress 0.94 FAIL / 0.95 PASS / -0.01 BELOW_FLOOR; bytes
  tie FAIL; not on the list UNSCREENED; HELD/CULLED/NOT_REACHED INELIGIBLE; < 8 runs; oracle and
  cheat gates; progress CI mapping; judge never called off the survivor list; NO_JUDGE; MISMATCH;
  no file. Suite 176 passed, 1 skipped, pytest rc 0.
- Live smoke, no worlds_r4.json yet: --round r4 gives B INELIGIBLE(UNSCREENED) 28, C 4, scored 0.

## 2026-09-14 P0 iteration 3: PENDING, and a cross-judge check against G-R4-5

- Inbox:
  - G confirmed the H-R4-2 names as asked (1789435384732-0): check() returns clause_a_r4, and
    every verdicts[v] carries its floor. G-R4-4/5 landed (765e2ff9b, 685940e27).
  - G stage 1 (e365d4fa3): 74/74 cells, abstain is the floor everywhere, gate > floor in 10.
    Stage 2 is running.
  - A (1789440120713-0): non-survivable cells whose HELD vs CULLED needs the train128 learner
    (w7, w26, w34, w10 train128) are PENDING. F12 and the replay treat PENDING as
    INELIGIBLE(PENDING). The replay must recompute from rows that non-survivability is exact:
    ci95[0] <= the pressure's own bound.
  - G (1789440338587-0): HOLD variants write PENDING; CULL variants write CULLED with
    cull_reason PENDING.
  - ff-merged to 036a80333.
- Code:
  - clause_a_r4.SCREEN gains PENDING, and PENDING_LEARNER (integration's worlds.PENDING before
    G's rename) reads as PENDING.
  - compression_r4 now passes doc= to check, so the judge and F12 read the same file.
- Cross-judge, aimed at the claim: the real qd_ledger.check(doc=) vs s4_verdict on 10 planted
  cells (0.94/0.95/-0.01, bytes tie, HELD, CULLED, NOT_REACHED, PENDING, UNSCREENED,
  active-variant-only). Verdict and progress agree 10/10; now a permanent parametrized test.
- Defects reported to G (1789441091802-0). Neither affects scoring, because F12 never consults
  the judge off its survivor list:
  1. clause_a_r4_block returns screen='SURVIVED' for a PENDING cell.
  2. worlds.PENDING is still 'PENDING_LEARNER' on integration.
- r2 progress output unchanged after G's check change (B raw_pass 25, BELOW_FLOOR 28).
- Tests: test_score_clause_a_r4.py 22. Suite 198 passed, 1 skipped, pytest rc 0.
- H-R4-3 still waits for "G P0 DONE".

## 2026-09-15 P0 iteration 4: H-R4-3 independent screen replay (0 mismatches)

- Trigger: conductor Nestor-A cross-session order to start H-R4-3 now. worlds_r4.json committed at
  ee86620f4 (file commit da8c5312a); G PASS receipts G-R4-3/4/5 mirrored at 45c46442f. ff-merged to
  45c46442f; claim H-R4-3-screen-replay.
- G fixed my two H-R4-2 defects before the file (1789442491847-0): PENDING screen label, and
  worlds.PENDING = 'PENDING'.
- Code: primordial/score/screen_replay.py.
  - Imports nothing from G's metric screen/worlds/suite/baseline/invariant/screen_run.
  - Numbers come from the lowest committed rows, never from the file or G's aggregates:
    - suite_cheap floors: abstain, best_fixed, and the median of the 8 random policy seeds;
      gate.gate_held64.
    - Learner: run rows without `family`, grouped by the cell's own (gen_seed, pressure), median
      over >= 8 run seeds.
    - Baseline: family=linear run rows, median, and median_ci in run-seed order (PCG64
      20260914), bytes.
  - Rules re-implemented from SWARM_R4 s2/s3/s7, operator message 13 and A's rulings: variant
    floors, HELD, cull_reason, bound exactness (re-judged at a larger floor), PENDING survivable
    vs non-survivable, and the 8-survivor stop in gate-headroom order.
  - The comparison covers every field of every cell under all four variants, plus the active
    pair and max_survivors.
- Result on the committed rows vs the committed file: PASS, 0 mismatches, 0 row defects, 74 cells
  (all stage 2).
  - gate_in|HOLD: SURVIVED 1 (w13 train128), HELD 5 (w7 t8, w1 t8, w1 t128, w34 t8, w13 t8),
    PENDING 4, CULLED 64. NOT_REACHED 0 in every variant.
  - PENDING non-survivability is exact from rows (ci95[0] <= the pressure's own bound):
      w7 t128   161.45 <= 189.19   w26 t128  188.51 <= 227.39
      w34 t128  155.26 <= 273.33   w10 t128   11.57 <=  22.30
  - Row written: primordial/ledger/rows/H/H-R4-3-screen-replay.jsonl.
- Tests (test_score_screen_replay.py, 11):
  - Rules on 6 planted cells.
  - G's own assembler (screen_run.assemble + worlds.build) on the same synthetic rows gives 0
    mismatches at max_survivors 8 and 1.
  - The stop marks later survivors NOT_REACHED.
  - Four tampered fields are each caught by name.
  - Row defects: a duplicate run seed with two values, and 7 run seeds.
  - A written survivable PENDING cell is a mismatch.
  - The committed screen replays with 0 mismatches.
- Suite 209 passed, 1 skipped, pytest rc 0.
- F12 on the real file (H-R4-2 end to end):
  - `progress --round r4 --since <round 4 plan ts>`: no cohort cells yet, scored 0.
  - All-time window: round 2 B cells read INELIGIBLE(CULLED) 19 and INELIGIBLE(HELD) 9. C reads
    INELIGIBLE(UNSCREENED) 4 (non-graphworld domains). 0 mismatches, 0 scored.
- H P0 DONE: H-R4-1 (490601595), H-R4-2 (a97934437, 519103e45), H-R4-3 (this push).
