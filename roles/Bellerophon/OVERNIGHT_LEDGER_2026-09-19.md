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
C6 | T+0:12 | workspace substrates (directive s12 hypothesis, tested before building)
  RED: tests/test_workspace.py (9 tests) -- collection error (random_statemachine_v2 absent); the contract was
    written in the test module docstring first: ext.workspace.kv.v1 / .stream.v1 / ext.substrate.lifecycle.v1.
  CHANGE: statemachine.v2 (one memory slot living in the substrate's workspace; PREFERS memory, requires
    nothing, runs memoryless on flat with refused writes COUNTED); Workspace doors (NoWorkspace, KVWorkspace,
    StreamWorkspace) -- the only path from a player to a StateDevice; substrate.kv.v1 (scope, ttl, max_keys)
    and substrate.stream.v1 (scope, lag, maxlen); executor lifecycle hooks episode_begin/tick; substrate
    events merged into the observer stream; science["substrate"] block (carry_over).
  GREEN: 8/9 then 9/9 after the test itself taught me something: with default params kv == stream(lag 1)
    EXACTLY (read = last write). Encoded as a metamorphic identity; lag 3 differs. Suite 60 (49 kernel +
    11 base-role).
  DECISION: the StateDevice contract did NOT need to change (directive s4 said change it if so); what was
    missing was the DOOR (Workspace) and the lifecycle hooks. Alternative rejected: giving players the
    device (violates s6 "do not expose Redis as the programming model").
C7 | T+0:13 | transforms did not accept statemachine.v2 -> sham/scratch would be INDETERMINATE for all of EXP-002.
  RED: relabel/shuffle/fresh on v2; relabel must preserve the fingerprint (metamorphic). Fixed; 50 passed.
C8 | T+0:14 | EXP-002 (examples/exp_002_substrate_sweep.py) first run CRASHED the executor: sweeping over whole
  component refs (dict values) made the run key unhashable -> TypeError, a process halt from a legitimate
  designer sweep (anti-bureaucracy rule s32 violated by the kernel itself). RED reproducer; fix: JSON key.
  EXP-002: 432 runs (6 substrates x 2 regimes x 2 charges x 6 arms x 3 seeds), 0 failed, 5/5 controls MET
  (72/72 pairs each). ROWS: all six substrates give DISTINCT traces at every one of the 12 (seed, regime,
  charge) points; flat refused 818 writes (visible); kv lifetime carry_over True; kv ttl=4 expired 116
  keys; memory charged at 0.05/op lowers the objective below flat for these random players (mechanics
  visible; no scientific claim). Series PRESENT 72/72, inline (<= 512 records).
C9 | T+0:15 | EXP-002 rows: stream substrates at lifetime scope said carry_over=False (the log DOES survive):
  StreamWorkspace.read bypassed the substrate's read hook -- the science block lied by omission. RED
  (lifetime True / episode False), fixed. EXP-002 regenerated: stream lifetime carry_over now True.
  COMMIT below. NEXT: corrupted/truncated receipt files; fuzzed IR compositions; sweep over players
  (missing DOF found in C3: "players" is not a sweepable root).
C10 | T+0:17 | receipt FILE integrity (forensics, not just per-record)
  RED: tests/test_integrity.py (4): truncated last line, edited middle record, duplicated record, clean scan.
  CHANGE: receipt.read_all is STRICT (raises naming the line); receipt.scan() is FORENSIC (never raises;
    counts valid; names every defect by line: TRUNCATED_OR_MALFORMED_JSON, RECEIPT_ID_MISMATCH = edited
    after writing, SCHEMA:*, DUPLICATE_RECEIPT_ID). Decision: a duplicate is a defect and NOT a valid run
    (a copy is not a second execution). GREEN 56.
C11 | T+0:19 | fuzzed compositions (tests/test_fuzz.py): seeded random Experiments from the registry (1-3
  players of mixed representations, random world params incl. zero ops / zero yield / huge charge, random
  substrate configs incl. max_keys=0, random interventions incl. delay 40 > horizon, random controls /
  observers / sweeps incl. horizon 0, series bounds 0). 40 seeds in the suite; 300 run once out of suite:
  189 OK (0 FAILED receipts), 64 BLOCKED_MISSING_CAPABILITY (adversarial knobs: a required capability
  nobody grants; an unknown wrapper), 47 invalid IR refused as data (negative horizon; sweep root
  "players"), 0 crashes. Every refusal carries a reason (asserted).
  FINDING (not a defect, a DOF): "players" is not a sweepable root -- a population variation must be a
  separate experiment today. Recorded; next cycle decides.
C17 | T+0:19 | unexpected events: a world emitting an uncatalogued event kind CRASHED TraceObserver
  (IndexError on EVENT_KINDS[kind]) -- events would have been normalised away by a crash. RED with a world
  that emits kind 99; fix: observers retain UNKNOWN_<id>. GREEN 97 passed 1 skipped (fuzz adds 41).
C12 | T+0:22 | population as a sweep axis (the DOF C3/C11 found missing)
  RED: sweep={"players": [A, B, C]} refused by validate. CHANGE: "players" is a sweepable root; "players.1"
  and "players.0.initial_state.state" already worked through the dotted setter (test kept). Controls pair per
  population (3 pairs). GREEN.
C13 | T+0:23 | an objective that READS THE SERIES: objective.series_gain.v1 = last-episode yield - first-episode
  yield (the experience-to-competence shape). None with reason SERIES_MISSING / SERIES_DISABLED / SERIES_EMPTY,
  never a fabricated 0. The recovered episodes reach the objective on a transient key that never hits the
  written receipt. FALSE-GREEN GUARD: a version reading only the inline series returns SERIES_EMPTY on an
  artifact-backed run; a test pins the artifact case and the perturbation was shown to fail it.
C14 | T+0:24 | held-out split as receipt data: seed_policy.holdout_seeds -> contiguous seeds tagged
  split="holdout"; SUMMARY carries per-split n / objective_n / objective_mean; controls pair within split.
  Decision: the kernel TAGS and AGGREGATES; whether a holdout result "qualifies" is the designer's reading
  (kernel never adjudicates). Suite 102 passed 1 skipped.
C19 | T+0:27 | non-stationary worlds: Intervention.schedule (list of {tick, world_params}) applied by a kernel
  ScheduleWrapper at tick boundaries through world.set_params (ext.world.mutable_params.v1; integer world
  exposes six runtime-mutable params, emits one TASK_CHANGE per changed param, refuses others as a FAILED run).
  RED 3 tests (schedule changes the trace + is recorded; a world without mutable params -> BLOCKED locally;
  a non-mutable param -> FAILED receipt not a halt). Refactor while GREEN: the wrapper counted ticks itself
  instead of reading the world's private state. Suite 105.
C20 | T+0:29 | PLAYTEST C (playtests/pt_c_changing_tasks.py): 2 memory players on kv lifetime ttl=6, two task
  schedules, two populations, 2 train + 2 holdout seeds, series-gain objective. 80 runs, 0 failed, 4/4
  controls MET. ROWS: per-episode yields read [84, 84, 84] and [0, 0, 0] for every run; objective 0.0
  everywhere; holdout mean 0.0 -- a FALSE ZERO.
C21 | T+0:30 | cause: the series' yield column was cumulative over the RUN (SeriesObserver inherited
  TraceObserver's run-total counters), so every episode ended at the same number and series_gain = 0
  identically. The C1 invariant test (monotone within episode) could not see it. RED: per-episode final
  yields must sum to the run total and an episode must start near zero. Fix: SeriesObserver keeps its own
  per-episode yield counter. Playtest C re-run: per-episode yields now vary (see rows). Suite 106.
  LESSON (ledger): an invariant that holds for both the right and the wrong implementation is not a test of
  the difference; the playtest row that looked "too regular" was the signal.
