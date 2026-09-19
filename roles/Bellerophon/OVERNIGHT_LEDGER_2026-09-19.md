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
C22 | T+0:33 | while re-checking C21 the rows STILL read [84, 84, 84]: I was reading a receipts file that
  execute() had APPENDED a second run to -- two executions interleaved as one file, stale rows analysed as
  fresh. RED: executing twice to one path must raise unless append=True. Fix in execute(). Suite 107.
C23 | T+0:35 | fresh playtest C rows: TASK_CHANGE counts (13, 10, 9, 7) exceeded what the schedule could
  produce (6, 6, 6, 3): the StateDevice reused TASK_CHANGE for key expiry and scope discards -- one event id,
  two meanings. RED (TASK_CHANGE == 3 params x 2 episodes; STATE_EXPIRE == ws_expired; STATE_DISCARD >= 1);
  fix: STATE_EXPIRE / STATE_DISCARD appended to EVENT_KINDS (ids stable). Suite 108. Playtest C re-run: per
  seed TASK_CHANGE now matches the schedule and expiries are their own kind (rows below in the receipt file).
C24 | T+0:40 | model-based property test of the StateDevice contract (tests/test_state_model.py): a 20-line
  reference model driven by 400 random ops x 25 seeds (put with every scope and ttl in {None,0,1,2,5}, get,
  advance by 0/1/3, end_scope of every scope, snapshot/restore) must agree with the device on every key after
  every op and on expired/refused counts. Passed first time -- so DETECTION WAS PROVEN by two perturbations:
  ttl off-by-one (< for <=): 25/25 fail; capacity off-by-one (<= for <): 17/25 fail. TTL boundary pinned:
  ttl k put at T is gone from advance(T+k); ttl 0 is gone at the next advance even to the same tick.
  Redis arm: 5 seeds, SKIPPED here (no server).
C24b | T+0:42 | the model test's runtime exposed an unbounded device EVENT buffer when nobody drains it.
  RED: 250 puts with max_events=100 -> 100 kept (newest), events_dropped == 150 in accounting. Fixed for the
  in-process device (every emit routed through a bounded _emit). Suite 135 passed 6 skipped.
C26 | T+0:50 | search ABOVE the kernel (directive s18): prometheus/toolbox/search.py -- Selector proposes from
  archive ROWS (JSONL: elite rows + GEN_DONE markers), the kernel runs each generation as an ordinary
  Experiment with `players` swept (one player per point), receipts ingested into rows. selector.truncation.v1,
  selector.map_elites.v1 (one elite per descriptor cell), transform.point_mutation.v1 (exactly one cell).
  RED: module absent. Tests: 4-gen uninterrupted == 2-gen + resume (row keys identical); a crash landing
  AFTER a generation's rows but BEFORE its marker -> rows marked GEN_ABANDONED at resume, generation rerun,
  committed view == clean run; MAP-Elites keeps one elite per cell.
  DETECTION PROVEN: (a) process-local state in the selector (id(self) as the stream seed) -> resume test
  fails; (b) trusting uncommitted rows at resume -> abandoned test fails (only after the test was
  strengthened to crash AFTER rows were appended; the first version crashed before any row and could not
  see the perturbation -- recorded as a weak test that was fixed).
  FOUND (C26b): one row per RECEIPT made a player with two seeds look like two elites; rows now aggregate per
  player (objective = mean over seeds, receipt ids listed). Suite 139 passed 6 skipped.
  DECISION: the kernel knows nothing about search; nothing in the IR/executor/receipts changed. Reopen if a
  selector needs per-receipt access beyond receipt ids (then rows carry a receipts path, not receipt copies).
C27 | T+0:55 | PLAYTEST D (playtests/pt_d_search_memory.py): MAP-Elites above the kernel, 6 gens x 8 x 2 seeds,
  flat vs kv-lifetime, statemachine.v2, regime-switching world. First run: archive collapsed to 4-5 cells;
  the best cell (0,7,0) carried objective 160 while its yield bucket said 0.
  TWO FINDINGS: (a) a row's descriptor came from the FIRST seed while its objective was the mean over seeds
  -- a cell key contradicting its own objective. RED (fake receipts: [0,7,0]+[0,7,7] must give [0,7,4] and
  keep both); rows now aggregate descriptors element-wise and keep every seed's. (b) descriptor buckets
  saturated at 7 (magnitude, yield) on this world: observer.descriptor.v1 -> version 2 with action_scale /
  yield_scale params (a designer calibrates; the kernel cannot know a world's ranges). With scales (2, 40):
  flat 12 cells, kv 16 cells, best 160 / 159.3. No claim about memory; the composition works.
  Suite 140 passed 6 skipped.
C29 | T+1:00 | interrupted jobs resume from the receipts file (directive s8: one experiment != one uninterrupted
  computation). RED: execute(..., resume=True) absent. CHANGE: runs already on disk for this job (keyed by
  arm, sweep point, seed; valid lines only -- a truncated tail is redone) are kept and skipped; the summary
  and control expectations cover old + new; ExecutionReport.resumed_runs. Test: interrupt after 6 of 18 runs,
  resume, record == uninterrupted (trace hashes, objectives, control outcomes).
  FOUND BY THE TEST: primary receipts at a sweep point carried the POINT experiment's id while control-arm
  receipts carried the parent's -- one job, two ids. Every receipt of a job now carries the job's id
  (experiment_digest keeps the point). Suite 141 passed 6 skipped.
C28 | T+1:05 | admission for EVERY slot (directive s19): admit(kind) dispatches by slot -- observer (protocol,
  serialisable measure/describe/manifest, DETERMINISM over two identical synthetic runs, series shape),
  substrate (protocol, every DECLARED representation demonstrably instantiates/acts/snapshots, refuses unmet
  requires, integer accounting), control (arm() yields a VALID Experiment; expectation() returns a typed
  outcome on synthetic receipts), representation / objective / transform / selector smoke; admit_all().
  RED: module functions absent. Tests: every reference row ADMITTED on M2; a set-valued observer refused on
  "serialisable"; an os.urandom observer on "determinism"; a substrate claiming a representation nobody can
  make on "representations"; a control emitting an invalid IR on "arm"; an unknown kind on "registry" (no
  exception). Suite 147 passed 6 skipped.
C30 | T+1:12 | an IR is pure data: validate() refuses callables, sets, NaN ("not serialisable as JSON") instead of
  letting a receipt writer crash later. RED then GREEN.
C32 | T+1:13 | REPLAY FROM THE RECEIPTS FILE ALONE: the SUMMARY receipt now embeds the job's full IR;
  backends.local.replay_file(receipts, out) re-executes it and compares every run's trace hashes, series
  hashes and objective with the record -- divergences are DATA per run, the kernel-hash difference is
  information beside them. Test: a clean file replays with 0 divergent; the IR tampered inside the summary
  (world_seed 99) replays with 2/2 divergent on trace_hashes, no exception. Suite 149 passed 6 skipped.
  NOTE: receipt_id covers the embedded IR, so tampering with it is also visible to scan() unless the id is
  recomputed (as the test deliberately did) -- a forger must rewrite the id, which the forensic scan of an
  UNMODIFIED copy would expose by comparison. Two copies is the defence; recorded, not built.
C33 | T+1:18 | "a player is a conventional agent" not assumed: rewrite.v1 -- a token rewrite system as a player
  (rules over an integer alphabet applied to its own tape each tick, observations injected at the head, the
  tape a shift register, actions read from the tail). RED (representation absent) -> instantiates on every
  substrate, ADMITTED, sham/scratch transforms accept it, runs beside a state machine in one world with
  replay MET. First cut produced constant actions (tail never reached by the injected tokens): the shift
  register fixed it; the test's "actions vary" assertion caught it. Suite 150.
C34 | T+1:22 | one machine per experiment not assumed: a player entry may carry its own substrate ref (the
  experiment's substrate is the default). Executor instantiates per player, drives every substrate's
  lifecycle hooks, merges events, records components.player_substrates and accounting.by_substrate.
  Negotiation checks a player's requires against ITS machine. RED (2 tests) -> the same table on kv vs flat
  diverges inside one world; an override that cannot run the player is refused at lowering. Suite 152.
C35 | T+1:33 | fuzzer extended with tonight's features (rewrite players, per-player substrates, schedules incl.
  a non-mutable param, holdout seeds, players/substrate sweeps, series objective): 41 in suite; 400 seeds out
  of suite: 259 OK, 95 BLOCKED, 9 TARGET_UNSUPPORTED, 37 invalid, 0 crashes, 0 unexplained FAILED.
  PLAYTEST E (playtests/pt_e_everything.py): three machines in one world (kv-lifetime state machine, stream
  rewrite system, flat Proteus tape), delay + schedule, population sweep, holdout, series-gain objective, six
  controls, INTERRUPTED after 20 runs, RESUMED (64 more), then replay_file over the resumed file: 84/84
  compared, 0 divergent, kernel hash equal. ROWS: the sham arm's player_substrates read [flat, flat, flat]
  while the primary's were [kv, stream, flat] -- transforms rebuilt manifests from PlayerSpec and DROPPED the
  per-player substrate override: the "cost-matched" sham ran on different machines. RED; fixed (keys the
  PlayerSpec does not model travel with the player). Also: a stream substrate whose player never reads
  reported carry_over=False; now None with reason "no workspace reads". Suite 154 passed 6 skipped.
