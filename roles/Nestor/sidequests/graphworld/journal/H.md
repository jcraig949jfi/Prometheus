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
