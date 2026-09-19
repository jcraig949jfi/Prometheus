# Overnight TDD / playtest ledger -- 2026-09-19 (append-only)

Directive: prompts/2026-09-19_overnight_tdd/ (verbatim, MANIFEST). Window: 8 h from receipt.
RECEIPT: 2026-09-19T02:49:43Z (first command after the directive; `date -u`). END: 2026-09-19T10:49:43Z.
Starting commit: e17eb94c4 (== origin/main at receipt; tree clean). Branch: bellerophon/overnight-tdd-2026-09-19.
Host: M2 / SPECTREX5, python 3.14.4, no Redis reachable.

Format per cycle: C<n> | T+<elapsed> | pressure | RED (test, why it fails for the right reason) | change |
GREEN (targeted / suite / base-role) | playtest | defects & surprises | decision (alternatives, reopen condition) |
commit | next pressure. Failed approaches stay in the ledger.

----------------------------------------------------------------------------------------------------
C1 | T+0:05 | U3: per-episode series as durable receipt data (operator ruling s3)
  RED: tests/test_series.py (8 tests) -- collection error: prometheus.toolbox.series does not exist; then each
       test fails on the missing observer kind. Right reason: the capability does not exist.
  CHANGE: series.py (SeriesRecord: PRESENT/EMPTY/DISABLED/BOUND_EXCEEDED written; MISSING/MISSING_ARTIFACT/
       CORRUPT found by verify(); inline <= 512 records else content-addressed artifacts/series_<sha256>.json;
       declared bound keeps the first N deterministically and REPORTS n_records_dropped; recover() from the
       receipt alone). observer.series.v1 (per tick [tick, actions_sum, yield_cum, alive]; enabled=False ->
       DISABLED; optional StateDevice mirror as a cache). Executor collects series per episode into
       receipt["series"]. control.replay.v1 now also compares series hashes. IR: horizon >= 0 allowed (an
       EMPTY series needs a zero-tick run); budget.series_max_records. Observer contract: series flag +
       series_episode().
  GREEN: 8/8 series; suite 31 passed 1 skipped; base-role 11.
  PLAYTEST: series over 6 seeds x 3 episodes x 2 players, rows inspected via an invariant property test.
  DEFECTS/SURPRISES:
    (a) FALSE GREEN: perturbing the observer to never decrement alive PASSED the invariant test ("non-
        increasing" admits "constant"). Strengthened: the last record's alive must equal the world's own
        summary (independent source) and the fixture must show >= 1 absorption. Perturbation now FAILS.
    (b) REAL DEFECT exposed by (a): the terminal record disagreed with the world (1 vs 0 alive) because the
        executor delivered on_tick(t) BEFORE on_events(t): series rows were pre-consequence. Fixed: events
        of tick t are delivered before on_tick(t); the order is now written into the Observer contract.
    (c) yield-reset perturbation was caught by the monotone check (detection demonstrated).
  DECISION: series are receipt data with content-addressed artifacts beyond 512 records; alternatives were
    (i) always inline (receipts of MBs; rejected by the ruling's forensic clause? no -- by size discipline),
    (ii) device-only with a pointer (rejected by the ruling). Reopen if artifact directories become a
    provenance problem (an artifact shared by two receipts is fine: same content, same hash).
  NEXT: EXP-001 as a frozen semantic fixture.
C2 | T+0:06 | EXP-001 becomes a regression fixture (directive s2)
  RED: test_exp001_committed_receipts_are_a_semantic_fixture written; passed immediately on the unperturbed
       tree, so detection was PROVEN by perturbing the world's action multiplier (97 -> 98): FAILED; restored: passed.
  CHANGE: none to production. GREEN: suite 42 passed 1 skipped.
  NOTE: kernel_hash in the committed receipts is now stale relative to the tree (the fixture compares trace
       hashes and objective values, not kernel_hash); receipts are regenerated once at window end.
  NEXT: playtest A -- an experiment alien to EXP-001 (mixed representations, regime switch, stochastic kick,
       three players, permuted observations, world sweep) to find expressivity gaps.
