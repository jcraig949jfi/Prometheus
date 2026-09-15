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

## 2026-09-15 R16 iteration 1: H-R16-1 BASELINE_N in F12 and the replay

- Trigger: Nestor-A cross-session order.
  - Operator ruling 16 (SWARM_R4 s9): 32 run seeds x 4 RNG families (4200/2101/3303/5501), 8 per
    family, mandatory for every baseline and every stochastic floor part.
  - Bus: 1789455185855-0 (ruling), 1789455359216-0 (G's v2 names win: baseline.{n_runs,
    families, n_per_family, readout}; run rows carry rng_family), 1789455401413-0 (G phase 1
    cleared), 1789455552584-0 (per-family minimum; 29+1+1+1 must be refused).
  - E's judge at 3dd777386 enforces n_runs < 32 and < 4 families; E is adding the per-family
    condition.
- Code:
  - clause_a_r4.baseline_n(baseline) returns None, or INELIGIBLE(BASELINE_N) when n_runs < 32,
    len(set(families)) < 4, n_per_family absent or empty, or any value < 8. Payload:
    baseline_n_runs, baseline_families, baseline_n_per_family, need_runs 32, need_families 4,
    need_per_family 8.
  - s4_verdict applies it right after the screen check, in check_r4's order (guard ->
    BASELINE_N -> oracles/cheats/runs).
  - For BASELINE_N, _agrees also requires the judge's why to match. The compression tally reads
    INELIGIBLE(BASELINE_N), and a judge without the rule reads MISMATCH (scores 0).
  - screen_replay:
    - Runs are pooled by (rng_family, run_seed), since v2 reuses seeds 0-7 per family.
    - Baseline families and n_per_family come from the rows.
    - Each cell gets clause_a_baseline_n OK|BASELINE_N from the same baseline_n.
    - families and n_per_family are compared when the file carries them (v2).
    - The summary lists clause_a_eligible vs clause_a_refused_baseline_n.
- Committed v1 file: replay still PASS, 0 mismatches, 0 row defects. The one survivor, w13
  train128, is refused BASELINE_N (8 seeds, no families); clause_a_eligible is empty.
- Tests:
  - test_score_clause_a_r4.py gains the 8x4 fixture, and these cases with the payload checked:
    29+1+1+1 / v1 / no n_per_family / 3 families / 31 with a 7 all give BASELINE_N.
  - 8x4 passes through to progress 0.95 PASS. BASELINE_N precedes the oracle and run-count gates.
  - The compression tally, and MISMATCH against a judge without the rule.
  - The real judge agrees on all 6. The 3 per-family cases skip until
    qd_ledger.BASELINE_MIN_PER_FAMILY exists.
  - test_score_screen_replay.py: v1 rows refuse clause A on every survivor; pooled 8x4 is OK
    (n_runs 32 despite repeated seeds) and 29+1+1+1 is refused. The committed v1 survivors are
    all refused.
- Suite before the merge of G 205dedfed / E de91fbd52: 237 passed, 4 skipped, pytest rc 0.
- Pooling order:
  - Reading G 205dedfed (metric/baseline.pooled_stats): G pools in FAMILIES order
    (4200, 2101, 3303, 5501), then run seed.
  - median_ci resamples by index, so order changes the CI. My first draft sorted families
    numerically, which would have reported false CI mismatches on every v2 cell.
  - The replay now pools in SWARM_R4 s9's listed order (4200, 2101, 3303, 5501), written in
    the replay itself rather than imported from G. v1 rows come first; unlisted families
    follow by id.
  - Test: rows written 3303-first give exactly median_ci over the s9 order.
- Push:
  - The first ops.push was refused (exit 4) on a rebase conflict in test_score_clause_a_r4.py.
    E's per-family commit c0a1404b4 had added the same n_per_family 8x4 fixture line.
  - Rebased by hand, taking my commit's version, and verified both of E's lines are kept (no
    conflict markers).
  - With qd_ledger.BASELINE_MIN_PER_FAMILY present, the 3 per-family cross-checks run instead
    of skipping: the real judge agrees on all 6 BASELINE_N cases.
  - Suite on the rebased tip: 245 passed, 1 skipped, pytest rc 0. Committed v1 replay still
    PASS, 0 mismatches.
  - Pushed e26668c8b as a fast-forward (no rebase during the push).

# Round 5 P-BUILD (SWARM_R5 s3 H-R5-1..4; overrides O5, O8; SMOKE stage, hard cap 2 h)

## 2026-09-15 06:13 start, item 1: H-R5-1 automatic receipt guard

- Trigger: Nestor-A cross-session order. ff-merged to 130848210 and read prompts_bld_r5/H.md,
  SWARM_R5.md, and prompt 19 s2/s3/s4.4/s8/s11/s12. Cap 08:13; "H BUILD STATUS" due 07:58.
- Coordination (before coding), H ask 1789467218102-0:
  - A 1789467242979-0: names match; campaign_stage has 4 values, SMOKE|PILOT|PRODUCTION|REPLICATION.
  - F 1789467306628-0: envelope is the JSON field `envelope` on the job spec in pm:jobs:<L>;
    admit() reason codes; pm:events; pm:resumable.
  - G: CANDIDATE_N payload and order; it also refuses any n_per_family < 8.
  - A 1789467299042-0: invariants rng_family_count == len(families) and runs_total ==
    sum(n_per_family); no rng_families key.
- Code: primordial/score/receipt_guard.py.
  - guard(rec, envelope) runs every check and reports every refusal as {check, reason, detail}.
  - The nine 19 s4.4 checks, with campaign_stage and the sample rule:
      rows_exist               ROWS_MISSING
      rows_committed           ROWS_UNCOMMITTED   (absent at the sha, or dirty)
      sha_on_integration       SHA_INVALID | SHA_NOT_ON_INTEGRATION
      identity_tag             IDENTITY_TAG_MISSING
      campaign_stage           CAMPAIGN_STAGE_INVALID | _NO_ENVELOPE | _MISMATCH
      predicate_predates_run   PREDICATE_MISSING | RUN_START_UNKNOWN | PREDICATE_AFTER_RUN
                               (bus 'PREDICATE <id>' with an exact-id match, vs the earliest
                               committed row ts)
      required_controls        CONTROLS_MISSING
      oracle_result            ORACLE_MISSING
      sample_rule              SAMPLE_INVARIANT (3 invariants) | SAMPLE_FIELDS_MISSING |
                               CANDIDATE_N | BASELINE_N
  - Thresholds are imported from qd_ledger. A PILOT under-sample that claims no scientific
    verdict is not refused; that label is H-R5-4's.
  - file() posts RECEIPT_REFUSED to <lane>,A and raises, or files through bus.receipt.
    envelope_of_job reads F's job spec.
- Wiring: bus.receipt runs the H guard on every receipt carrying campaign_stage. The envelope
  comes from rec.envelope or the job spec. A refusal posts RECEIPT_REFUSED and raises
  ReceiptError. Older receipts keep only guard_git.
- Tests: test_score_receipt_guard.py, 35 cases.
  - A clean receipt is accepted in all 4 stages.
  - Each reason code is refused, with the check marked REFUSED.
  - Uncommitted both ways (dirty file, and absent at the sha).
  - All failures are reported together.
  - A PILOT under-sample with no verdict is accepted.
  - Thresholds come from the judge.
  - file() refusal post, and the clean path.
  - Exact predicate-id match.
  - Family invariants and 29+1+1+1.
  - Envelope from the job spec.
- Suite 278 passed, 1 skipped, pytest rc 0 at 06:20.
- For after R5: G's CANDIDATE_N replaces the judge's 'runs < 8' refusal, so F12's
  clause_a_r4.s4_verdict mirror must follow when G lands it, or F12 reads MISMATCH.
- Pushed 50707b07b (ops.push rebased onto other lanes' commits; suite re-run on the tip below).

## 2026-09-15 06:22, item 2: H-R5-2 sealed anti-prior ledger (O5)

- Code: primordial/score/anti_prior.py. Keys pm:prior:sealed, pm:prior:commit, pm:prior:assign.
  - seal(): predictor-only.
    - WRITE_DENIED when the writer role is not predictor, or the predictor_id is an experimenter.
    - FIELD_MISSING for the five 19 s11 fields plus prediction_id and cell.
    - P_OUT_OF_RANGE outside [0, 1] (bools and strings too).
    - ALREADY_SEALED on a second write (hsetnx).
    - A sha256 commitment of the canonical record is stored, and verify() detects a changed
      prior.
  - assign(exp_id, seed, now, k):
    - A seeded PCG64 draw in prediction_id order among prior_p_pass <= 0.2 with
      prediction_ts < now, unassigned and verified.
    - Returns {exp_id, cell} only. ALREADY_ASSIGNED on a repeat.
    - eligible_at refuses a prediction at or after assignment (PREDICTION_NOT_BEFORE_ASSIGNMENT).
  - read():
    - The experimenter gets EXPERIMENTER_READ_DENIED until receipt_filed is true for every
      assignment holding the prediction; an unassigned prior is denied too.
    - Predictor and conductor may read; any other role gets READ_DENIED.
  - calibration(outcomes): per bucket (0/.1/.2/.4/.6/.8/1) n, mean prior, pass rate, Brier.
    Marked descriptive_only.
- Limitation (PRODUCTION_CANDIDATE note): sealing is enforced by this API plus the commitment. It
  is not cryptographic against a session reading the Redis hash directly.
- Tests: test_score_anti_prior.py, 12.
  - Write denials, and write-once.
  - 6 bad-record refusals.
  - The commitment detects a tamper, and a tampered prior is never drawn.
  - The draw takes p <= 0.2 only, is reproducible by seed, gives cells only, and refuses a
    repeat assignment.
  - A late prediction is never drawn, and a tie is refused.
  - Experimenter read denied then allowed after the receipt; conductor read; unknown role.
  - The calibration table.
- Pushed 3b94d3fbd. Suite on the tip with H-R5-2 included: 303 passed, 1 skipped, pytest rc 0
  (06:24).

## 2026-09-15 06:26, item 3 + integration asks: H-R5-4 classifier, G's CANDIDATE_N tests, A's guard bypass

- H-R5-4: primordial/score/expected_refusal.py.
  - Deliberate under-sample = stage SMOKE|PILOT|REPLICATION AND the job sample below the judge's
    own minimum (imported from qd_ledger). No agent declares the expectation.
  - classify() reads only the judge's output. Labels:
    - EXPECTED_REFUSAL_OBSERVED: INELIGIBLE with CANDIDATE_N | BASELINE_N | FAMILY_COVERAGE.
    - UNEXPECTED_REFUSAL_REASON.
    - EXPECTED_REFUSAL_MISSING: the judge gave a verdict to a deliberate under-sample (a defect).
    - NOT_APPLICABLE.
  - emit() writes pm:events and never emits NOT_APPLICABLE.
  - Tests, 12: every label; a deep copy shows the judge result untouched; the real qd_ledger.check
    output is byte-identical across the 4 stages, and its BASELINE_N on an 8-run baseline labels
    OBSERVED (PRODUCTION reads NOT_APPLICABLE); emit.
- G 1789467746914-0 / A 1789467765694-0 (integration stays green): G's CANDIDATE_N would turn 5
  of my real-judge tests red, since they pass runs only.
  - The tests pass runs_total / rng_family_count / runs_per_family when check()'s signature
    accepts them, so they hold on today's judge and G's.
  - Added a PILOT-sized agreement test (16/2/8 -> CANDIDATE_N on both sides), skipped until G's
    judge lands.
  - F12 mirror: clause_a_r4.candidate_n uses G's payload names in the order screen -> BASELINE_N
    -> CANDIDATE_N -> oracles, when a candidate sample is supplied. Otherwise the old runs < 8
    check stays until G lands.
  - compression_r4 passes the row's sample fields to s4 and to check (when accepted). _agrees
    requires the why to match for both sample refusals.
- A 1789467821844-0 (defect): the 50707b07b guard was bypassable by OMISSION, since it only ran
  when the receipt carried campaign_stage.
  - receipt_guard.should_guard = campaign_stage present OR active_round(r). active_round reads
    pm:round:current -> pm:round:<r> start_ts/end_ts, with a 1800 s close-out grace; an absent or
    malformed clock returns None.
  - bus.receipt uses should_guard.
  - guard() refuses a missing stage with CAMPAIGN_STAGE_MISSING.
  - Tests: A's 4 clock cases (active + omitted is guarded; outside a round is the old path; active
    + valid PILOT is guarded; clock absent is no active round), plus the grace edges and MISSING.
- Suite 322 passed, 2 skipped, pytest rc 0. Pushed e3412c04b and told G to push CANDIDATE_N
  (bus 1789468367121-0).

## 2026-09-15 06:32, item 4: H-R5-3 F12 progress axes by rule (O8)

- Code: primordial/score/axes_r5.py, axes(receipts).
  - Computed from receipt type and lineage only. A receipt's own points are never read, and
    neither is prose.
  - error_metabolism:
    - +1 per distinct other-lane exp_id named in `refutes` (F12's identifier matcher) by a
      board-eligible PASS/KILL receipt.
    - Credited to the FILING lane, earliest filer first, never the originator (O8).
    - Own-lane refutations score 0 and are listed under own_refutations_unscored.
  - instrument_gain: +1 per PASS receipt with experiment_class instrument|tooling (envelope or top
    level) whose regression_test names an existing primordial/ test file (FIXED_WITH_REGRESSION).
  - boundary_resolution: +1 per FAIL/KILL receipt with committed rows and science.boundary
    {parameter, below{value, verdict}, above{value, verdict}}, with below.value < above.value and
    differing verdicts.
- Tests: test_score_axes_r5.py, 11.
  - Credit goes to the refuter, not the originator. A second refutation of the same claim gets 0.
    Own lane gets 0 and is listed. A non-board-eligible receipt gets 0, and so does a FAIL
    "refutation".
  - Instrument gain needs a tooling/instrument class, an existing test, and PASS.
  - 8 boundary cases.
  - Self-reported points are ignored.
- Suite on the pushed tip e3412c04b plus axes_r5: 336 passed, 2 skipped, pytest rc 0 (06:35).

## 2026-09-15 06:35 R5 BUILD close-out (all four H items green, 22 min of the 2 h cap)

- H-R5-1 receipt guard: 50707b07b, plus the clock trigger in e3412c04b. H-R5-2 sealed ledger:
  3b94d3fbd. H-R5-4 classifier: e3412c04b. H-R5-3 axes: this push.
- Gate items from H: 4 (EXPECTED_REFUSAL_OBSERVED), 9 (the guard refuses each failure case), 14
  (sealed prior read-denied to the experimenter), and 15 (suite rc 0 on the tip).
- PRODUCTION_CANDIDATE notes (not done in this SMOKE build, not extended):
  1. The sealed ledger is enforced by its API plus a sha256 commitment. It is not cryptographic
     against a session reading pm:prior:* directly; a production fix is encryption, or a separate
     Redis ACL user for the predictor.
  2. axes_r5 is a library, not yet wired into progress.vector / the `progress` CLI as a round 5
     output row.
  3. F12's s4 mirror keeps the old `runs < 8` check for a candidate row without the three sample
     fields, until G's CANDIDATE_N is on integration; then that fallback should be removed.
  4. The receipt guard reads oracle results from rec['oracles']; cohort receipt writers must fill
     it. Currently a convention, posted to A/F/G.
- The H-R5-3 push (5a0a3488e) rebased onto E's round 5 items and F-R5-4/5/6. The suite on that
  tip: 365 passed, 2 skipped, pytest rc 0 (06:38). G's CANDIDATE_N is still not on integration.
- One clock reader:
  - F 999083dee added primordial.ops.round_clock.active(r, now, grace_s=1800), the same window
    rule as receipt_guard.active_round. A's launch-gate item 16 asserts that clock at T+0.
  - receipt_guard.active_round now delegates to round_clock.active (returns round_id), so the
    guard and the gate cannot disagree.
  - F's read() raises on a malformed hash; the guard turns that into "no active round" rather
    than crashing bus.receipt (tested).
  - The test Clock fake is built from round_clock.plan (end = start + 7200).
  - Suite 365 passed, 2 skipped, pytest rc 0 (06:41).
- H-R16-2 (replay of worlds_r4/v2 with pooled-32 CIs and the top1_train reader) waits for
  "G R16 DONE".
