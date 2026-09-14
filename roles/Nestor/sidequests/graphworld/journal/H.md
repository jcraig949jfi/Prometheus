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
