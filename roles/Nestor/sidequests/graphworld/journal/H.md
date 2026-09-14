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
