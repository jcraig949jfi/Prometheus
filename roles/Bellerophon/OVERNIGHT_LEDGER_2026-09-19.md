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
C3 | T+0:07 | PLAYTEST A (playtests/pt_a_alien_mix.py): 3 players of 3 representations (state machine, constant,
  Proteus tape) in a non-stationary integer world (regime switch, stochastic kick), delay + permute
  interventions, sweep over world_seed x regime_period, 7 controls, 3 observers, survival objective.
  96 runs, 0 failed, every control "MET". Rows inspected -> three surprises:
    S1 the permutation CONTROL's wrapper REPLACED the designer's own permutation (dict keyed by name; last
       writer wins) -- a semantic leak between a control and the conditions it was supposed to leave alone.
    S2 sham/scratch acted only on statemachine.v1; on the constant and Proteus players they did nothing and
       reported MET (cost-matched trivially). A control that cannot act must not claim it did.
    S3 the Proteus player never acted (actions 0) and "won" survival; its fingerprint equalled the constant-
       zero player's. Not a wrapper bug: 11/60 random Proteus genomes emit anything in 32 ticks (measured).
  DECISION: S1 -> C4; S2 -> C5 (Transform slot); S3 -> silence made visible (C5b).
C4 | T+0:08 | wrappers compose (S1)
  RED: tests/test_playtest_findings.py two tests: manifest wrappers int not list; arm lost the 4242 permute.
  CHANGE: ObservationWrapper takes a LIST of permute seeds applied in intervention order; delays add; the
    manifest records every seed. GREEN: 34 passed. Metamorphic check inside the test: a double permutation
    is a permutation of the same multiset and differs from each single one.
C5 | T+0:09 | Transform slot + control coverage (S2), silent players (S3), probe disturbance (found while fixing)
  RED: 4 tests: sham/scratch on constant -> expected INDETERMINATE (got MET); coverage list; Proteus sham;
    registry rows for transforms.
  CHANGE: ref/transforms.py: transform.shuffle.v1 (sham; statemachine table cells / Proteus genome words,
    cost preserved), transform.fresh.v1 (scratch), transform.relabel.v1 (behaviour-preserving relabel, for
    metamorphic tests), each with `accepts`; controls sham/scratch now apply the registered transform to every
    accepted player and record provenance.transformed_players; no player transformed -> INDETERMINATE.
  FOUND WHILE FIXING (C5b): every silent player shares one fingerprint, and 49/60 random Proteus players are
    silent on the probe. player_fingerprints is now {"hash", "silent"}; a test pins that silent players are
    flagged. The sham test uses a non-silent Proteus seed (17) found by probing seeds 1..200.
  FOUND WHILE FIXING (C5c): the Proteus instance's snapshot() omitted the rng stream and the meter, so the
    fingerprint probe ADVANCED the player's random stream and inflated its cost -- "the probe never disturbs
    the run" was false. RED test (probe twice; cost and later actions must equal an unprobed twin), fix:
    snapshot/restore cover rng + meter. GREEN: 40 passed 1 skipped.
  PLAYTEST A re-run after C4/C5: 96 runs, 0 failed; sham now INDETERMINATE? see line below.
  PLAYTEST A after C4/C5: 96 runs, 0 failed; sham transformed players [0, 2] (state machine + Proteus; the
    constant player correctly untouched) -> MET with coverage recorded; player 2 flagged silent=True.
  COMMIT: (this entry's commit hash below).
  NEXT: playtest B -- state at scopes / substrate variation pressure (does EXP-002 need substrate.kv.v1 or can
    the StateDevice be reached through the existing contracts?).
