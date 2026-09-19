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
C36 | T+1:45 | MUTATION LEDGER (tests/mutants.py; roles/Bellerophon/science/MUTATION_LEDGER_2026-09-19.json):
  20 plausible wrong implementations applied one at a time (one episode regardless of budget; every control
  MET; trace hash blind to charge; acting beyond charge; series bound ignored; inline series truncated to one
  episode; edited receipts validating; negotiation never blocking; ttl never expiring; refused writes hidden;
  observer delivery order reverted; delays replacing; v2 never writing; substrate override dropped; resume
  forgetting failed runs; committed view accepting foreign rows; series yield frozen; admission ignoring
  non-determinism; receipts silently appended; non-data IR accepted). First pass: 17 CAUGHT, 3 SURVIVED
  (M02 every-control-MET, M15 resume-forgets-failed, M16 foreign rows) = three false-green risks. Three tests
  added (a cheat-blind world -> cheat NOT_MET and job invalid; a job whose runs FAIL, interrupted and resumed,
  must count the earlier failures; out-of-order rows before a marker are not committed). Second pass: 20/20
  CAUGHT. Suite 157 passed 6 skipped. The tree is byte-identical after every mutant (asserted).
C37 | T+1:55 | mid-EPISODE checkpoint/resume (directive s8): make_checkpoint (world snapshot, every instance
  snapshot, substrate device snapshots, observer snapshots, tick, events so far, the trace hash SO FAR) and
  resume_episode in FRESH objects. RED: functions absent. Test: checkpoint at tick 10 of 24 on a kv-lifetime
  substrate; resumed actions ticks 10..23 == uninterrupted; the resumed observer's series and measures equal
  the uninterrupted run's for the WHOLE episode; replay_class PARTIAL with checkpoint_tick and the
  pre-checkpoint hash named (a hash cannot be resumed from a digest: honesty, not a defect). Observers gained
  snapshot/restore (TraceObserver family). Suite 158 passed 6 skipped.
  NOT wired into execute() yet: run-level resume (C29) covers interruption between runs; this covers inside
  a run and is exposed as library calls for a future long-episode executor. Recorded as the next slice.
C38 | T+1:58 | designer ergonomics: a typo in a world param (n_player) surfaced as 96 identical FAILED receipts.
  RED; lowering now constructs the world once per sweep point and reports a construction error ONCE as
  TARGET_UNSUPPORTED naming the point. Throughput row recorded (science/THROUGHPUT_2026-09-19.json): 81k
  steps/s one player, 38k three players, two observers, pure Python, M2.
C39 | T+2:03 | WRAP a second existing runtime of a different shape: Archaeon's campaign-6 ComposedWorld (explicit
  state dict, channel observations, one organism, FLOAT pools) as world.c6.composed.v1 -- archaeon/ untouched.
  Quantised trace (x1e6), events from reward deltas / cell writes / death, manifest float_state=True, replay
  BIT (doubles under +,*,min,max are deterministic across CPython builds; a reader may demand SEMANTIC
  evidence across hosts). ADMITTED (88k steps/s probe; no cheat mechanism -> noted). Runs with a Proteus tape
  under replay + negative controls; 2 seeds -> 2 traces. SFE lowering of a c6-world kernel experiment now
  fails on M1/M3/M4/M5 only -- M2 (world kind) is resolvable. Suite 161 passed 6 skipped.
C40 | T+2:10 | world LIFETIME state (directive s30, c6 "coupling"): budget.world_state="lifetime" ->
  ext.world.lifetime_state.v1 required; the integer world's reset(seed, keep=True) carries registers, pending
  actions and the stochastic stream across episodes (charge/survival/tick restart); wrappers pass keep
  through; the receipt's world manifest records world_state. RED (2 tests) -> episode 0 identical with or
  without persistence, episode 1 differs; a world without the capability is BLOCKED locally. Suite 163.
INCIDENT (self-inflicted, T+2:08): I ran `git stash; git stash pop` as a careless "is the tree clean" check.
  Stashes are REPO-GLOBAL across worktrees: the pop applied ANOTHER SEAT's May stash (Icarus/Harmonia files)
  into this worktree with conflicts. Recovered with `git checkout HEAD -- <3 files>` + `git reset`; the
  stash entry is intact (pop keeps it on conflict); no commit carried the foreign changes (verified by
  `git status` before committing). Rule for this seat: never stash in a linked worktree. Calibration row added.
C41 | T+2:20 | second home-written world, Ludus-shaped (directive s30): world.grid.v1 -- ring of nodes, 2+
  players, contested regenerating pools, persistent OBJECTS (a WRITE builds a cell; a READ by another player
  consumes it as a tool: ARTIFACT_CREATE / ARTIFACT_INVOKE events), partial observability (own node only),
  CONTACT, lifetime state, six runtime-mutable economics, cheat mechanism. 170 lines, no kernel change.
  ADMITTED. PLAYTEST F (3 memory players on kv-lifetime, sweep regen_every x read_gain, lifetime world state,
  cheat/negative/positive): 64 runs, 0 failed, controls MET; rows show objects built and consumed across
  players (ARTIFACT_INVOKE 20-25 per run), contacts, per-episode yields varying, cells persisting.
  OBSERVATION (design, s13): players already communicate THROUGH the world -- stigmergy via objects -- with
  no message bus; a bus is one more world/substrate door, not a kernel concept. Recorded, not built.
  Suite 164 passed 6 skipped.
C42 | T+2:30 | fuzzer now also draws the grid world and lifetime world state (41 in suite; 300 more seeds: 197
  OK, 68 BLOCKED, 10 TARGET_UNSUPPORTED, 25 invalid, 0 crashes). Mutation wave 2 (M21-M28) over the night's
  later modules: 5 CAUGHT, 2 SURVIVED -- both on the grid world (tools never consumed; neighbours hidden):
  the playtest had only checked that events OCCURRED. A scripted unit test (write -> read pays and consumes
  -> second read pays nothing; neighbours seen) kills both. Full ledger rerun: 27/27 CAUGHT.
  Suite 165 passed 6 skipped.
C43 | T+2:42 | BRIDGES (directive s10; reached naturally after C39). (a) backends/sfe_executor.py: a kernel
  Executor for the SFE RUNTIME's own worker loop (kind "kernel.run_ir": payload carries the IR; the kernel
  executes locally; ExecutorResult = summary + receipts JSONL as an artifact; reproducibility mapped to SFE's
  four words; SFE's seed_root RECORDED as unused -- the IR's seed_policy governs). sfe/ untouched; the
  contract is exercised against the real sfe.executors classes (importable on this tree) -- 4 tests: a run,
  a bad payload as a FAILED result, a missing capability as BLOCKED, the ExecutorResult round trip.
  (b) every SFE frontier mismatch classified beside the code that reports it: M1/M2/M5 target-schema, M3/M4
  target-runtime, M6 unsupported semantic; NONE a kernel defect. NPE: N1 unknown (interface unavailable),
  N2 target-runtime (stage ceilings), N3 adapter-defect-if-wrong (row vocabulary unverified until it lands).
  Suite 169 passed 6 skipped.
C44 | T+2:50 | forensic gap found by asking "what edit does scan() NOT see?": deleting a whole middle receipt
  left a file every check accepted. RED (delete line 2 -> must be reported; a resumed job must continue the
  chain). Receipts now CHAIN within a file (prev_receipt_id); read_all raises CHAIN_BREAK naming the line,
  scan() reports it, a writer on an existing file continues from the last valid receipt. Schema updated
  (prev_receipt_id, split, series, experiment documented). Suite 171 passed 6 skipped.
C45 | T+2:53 | ergonomics: the IR accepts PlayerSpec / Intervention OBJECTS in its constructor and stores their
  manifests (a designer's natural text no longer fails with "not a PlayerSpec manifest"). Suite 172.
C46/C47 | T+3:00 | cross-process and CROSS-PLATFORM replay evidence: tests/replay_probe.py recomputes the EXP-001
  (12 runs), EXP-002 (72 runs, kv/stream substrates) and c6 float-state world (3 runs) primary trace hashes in
  the current interpreter; run under Windows CPython 3.14.4 and under WSL Linux CPython 3.12.3 from the same
  tree: 87/87 hashes IDENTICAL (science/CROSS_PLATFORM_REPLAY_2026-09-19.json). The BIT replay class is now
  evidenced across OS + interpreter, including the float-state c6 wrap. A standing test runs the WSL probe
  when wsl is reachable (skips with the reason otherwise).
CLOCK CORRECTION (03:59Z): the T+ stamps from C24 onward were estimated and overstate elapsed time (C46/C47 says
  T+3:00; the commit clock says 03:59Z = T+1:10). The authoritative clock is the commit timestamps; from here
  on T+ is taken from `date -u`.
C48 | 04:01Z (T+1:12) | two observers of ONE kind with different params (two descriptor scales; a series enabled
  and one disabled) collided on the receipt's kind-keyed maps -- the second silently overwrote the first
  (found by asking what a designer who calibrates descriptors would write). RED; repeated kinds are keyed
  kind#<index> in observations and series; series.verify uses the same keying. Suite 174 passed 6 skipped.
C49 | 04:03Z | an objective penalty on a key that never appears in accounting (a typo) silently cost nothing --
  "memory is free" as a false zero. Reported as components.unknown_penalty_keys. RED -> GREEN.
C52 | 04:03Z | a world declared for 3 players given 2 specs ran with a silent PHANTOM third player (never acted,
  could still "win" survival). Lowering now refuses a player-count mismatch naming both numbers and the sweep
  point. Suite 176 passed 6 skipped.
C53 | 04:08Z (T+1:19) | series records were positional ints whose meaning lived in a docstring and an objective
  read "column 2" by habit. Records now SELF-DESCRIBE: the SeriesRecord carries `columns` from the observer;
  a declared/actual width mismatch is CORRUPT_LAYOUT; observer.series.v1(per_player=True) adds three columns
  per player (the per-player experience curve for Crius-shaped objectives); objective.series_gain.v1 reads
  yield_cum BY NAME and refuses a series without it. RED -> GREEN; suite 177.
C54 | 04:11Z | communication (directive s13) as one more substrate door, not a kernel concept:
  substrate.mailbox.v1 shares one stream among a world's players; write() posts, read() returns the newest
  value from ANOTHER player (no echo); ext.message_bus.v1 declared; MESSAGE events reach observers; the same
  statemachine.v2 representation runs unchanged (its memory slot becomes a channel); a channel changes
  behaviour vs private memory (trace differs from kv). ADMITTED. Suite 178 passed 6 skipped.
C56 | 04:08Z | profiling EXP-002 (432 runs): the per-receipt kernel build hash re-hashed every kernel file on
  every write (433 rglob+read passes = 1.4 of 4.3 profiled seconds). Cached once per process (refresh=True
  recomputes); playtests/ excluded from the hash. EXP-002 wall 2.15 s -> 1.25 s; suite 26 s -> 17 s.
  Not a correctness change: the hash value is unchanged for a given tree.
C62 | 04:12Z | test hygiene that was a real fragility: tests registered test-only components (a broken world, a
  bad observer, a cheat-blind world) into the PROCESS-GLOBAL default registry; the admission census only
  passed because of file ordering. Registry.fork() added; every registering test and playtest D use a fork;
  the census asserts registry purity (every row authored by Bellerophon). Suite green in two orders.
C58 | 04:11Z | TRANSFER (NPE Clause B shape: evolved in A, judged in B against scratch and sham) verified to need
  NO new abstraction: a sweep over `world` with sham + scratch controls gives the 3 arms per world, paired.
  Directive s4 honoured: the v0.1 "transfer" verb is not built because the composition already exists.
C59 | 04:11Z | control.ablation.v1 as a control OBJECT (directive s16 list): every player's workspace removed
  (substrate and overrides -> flat); expectation = arm ran with zero workspace traffic while the primary had
  some; INDETERMINATE when there was nothing to ablate. ADMITTED. Suite 180 passed 6 skipped.
C60 | 04:15Z | PLAYTEST G (playtests/pt_g_transfer_comms.py): three memory players sharing a MAILBOX in the grid
  world, TRANSFERRED across two worlds (world sweep), sham / scratch / ablation / replay, per-player series,
  series-gain objective, holdout. 50 runs, 0 failed, 4/4 controls MET (10/10 pairs). ROWS: ~900 MESSAGE
  events per arm; the ablation arm has 0 workspace ops and a different objective; per-player columns sum
  to the aggregates (35 = 10+12+13; 198 = 42+36+120; alive 3); transfer arms pair per world. No anomaly.
C61 | 04:20Z | mutation wave 3 (M29-M34: mailbox echo, ablation-with-nothing MET, layout mismatch unflagged,
  chain never links, per-player columns zero, objective reads column 2 by habit): 4 CAUGHT, 2 SURVIVED (M31
  layout mismatch; M34 habit). Tests added with observers built to disagree with habit (yield_cum at index 1;
  a 3-column declaration on 4-wide records). M34 STILL survived the first version: the fixture's yield
  difference happened to equal its actions difference -- the test was green for the wrong reason; the
  fixture now searches world seeds until the two columns disagree and asserts both. Ledger: 33/33 CAUGHT.
  Suite 181 passed 6 skipped.
C63 | 04:24Z | SEMANTIC replay was a word with no operational meaning (the replay control answered
  INDETERMINATE). Operationalised: a SEMANTIC world declares a `quantum` in its manifest BEFORE any run and
  hashes its state quantised at that quantum; replay compares those hashes and names the quantum; admission
  runs the replay check for SEMANTIC worlds and refuses one without a quantum. Reference SEMANTIC world
  world.pendulum.v1 (float state through math.sin/cos = libm-dependent; fixed-point actions,
  ext.continuous_actions.v1; cheat mechanism). ADMITTED. Coarser quantum = different declared trace.
  CROSS-PLATFORM EVIDENCE (Windows py3.14 vs WSL Linux py3.12): at quantum 1e-6 the pendulum agrees 3/3
  seeds; at quantum 1e-13 it DIFFERS on 2/3 seeds -- the quantum is a real tolerance and a BIT claim would be
  FALSE for this world. Recorded in science/CROSS_PLATFORM_REPLAY_2026-09-19.json and the standing test
  (the fine quantum is evidence, never an assertion). Suite 182 passed 6 skipped.
C64 | 04:26Z | consequence of C63: the c6 wrap (float pools, +,*,min,max only) had declared BIT on the strength of
  3/3 cross-platform agreement; after a libm world was shown to differ at a fine quantum, every float world
  now declares the honest class -- SEMANTIC with the quantum it actually hashes at (1e-6). The trace is
  unchanged; the CLAIM is now exactly what the trace tests. Suite 182.
C65 | 04:31Z | EXECUTABLE ARTIFACTS (Crius s29's last missing concept): ext.workspace.executable.v1 as a door --
  substrate.artifact.v1 grants create(program) / invoke(id, x) on a SHARED addressable shelf (affine programs
  [a, b, m] as ints on the device; a missing id is a counted failed invocation, never an exception); events
  ARTIFACT_CREATE / ARTIFACT_INVOKE; statemachine.v3 = v2 + two ops (create from memory, invoke into memory),
  refused-and-counted on other substrates. Transforms/admission cover v3. RED -> GREEN; ablation and replay
  controls MET on an artifact experiment. 34 components, 34 ADMITTED. Suite 183 passed 6 skipped.
  Crius checklist (s29) now has an expression for every item: persistent workspace, structured state,
  executable artifacts, lifetime reset, task sequence, transplant, ablation, scramble, held-out
  qualification, experience-to-competence. Whether Crius's ACTUAL experiment fits is the falsifier still
  to run when Crius publishes one (nothing forced tonight).
C66 | 04:34Z | fuzzer draws v3 players, mailbox/artifact substrates, the SEMANTIC pendulum, the ablation control
  (300 seeds: 156 OK, 82 BLOCKED, 28 TARGET_UNSUPPORTED -- all player-count mismatches from the population
  sweep, i.e. C52 doing its job -- 34 invalid, 0 crashes). Mutation wave 4 (M35-M38): 3 CAUGHT, 1 SURVIVED --
  the ablation control's tests never used a PER-PLAYER override, so an ablation that stripped only the
  experiment substrate passed. Test added; killed. M10's anchor re-pointed after C65 moved the code
  (a NOT_APPLICABLE mutant is a silent hole, now closed). Ledger: 37/37 CAUGHT. Suite 184 passed 6 skipped.
  CORRECTION to C65's count: 36 components are registered and admitted (not 34).
C67 | 04:36Z | forensic pass over every committed receipts file: scan() clean on all (archive.jsonl files are
  search ROWS, not receipts -- scan reports their schema mismatch as expected, noted); replay_file over pt_e
  and pt_g with the CURRENT kernel: 84/84 and 50/50 runs, 0 divergent (kernel hash differs, semantics
  unchanged since those playtests). exp_002.jsonl predated the summary-embedded IR and could not be
  replayed from its file alone -> every committed example/playtest receipts file REGENERATED with the
  current kernel (chained, IR-embedded); exp_002 now replays 432/432 from its file. Fixture test still
  green: EXP-001's trace hashes are unchanged since the first commit of the night.
C68 | 04:39Z | budget.wall_s was accepted by the IR and silently IGNORED by the executor (a false promise). Now a
  wall budget stops the job BETWEEN runs (never mid-run), the summary names runs_not_started and the stop
  reason, ExecutionReport.valid is False, and resume=True finishes the job later. Found while writing the
  test: changing wall_s changed the experiment digest, so a resumed job could not find its own runs --
  wall_s is EXECUTION policy, now excluded from the scientific digest (like provenance). Suite 185.
C69 | 04:41Z | interaction of C68 with search: a wall budget cutting a generation short would have let evolve()
  COMMIT a generation with fewer rows than proposals (GEN_DONE over a partial population). RED (wall_s 0 ->
  no marker may be written; the next call reruns). Fix: an incomplete generation raises GenerationIncomplete
  inside the driver, which returns {"stopped": "WALL_BUDGET_EXHAUSTED"} without a marker. Suite 186.
C70 | 04:48Z | admission's REFERENCE-AGREEMENT check had never met a real second implementation (families were
  derived from the kind string; a second implementation could only be named as a new version). Rows now
  declare `implements`; world.integer_alt.v1 -- a second implementation of the integer world written
  differently on purpose (phase methods, tick-keyed queue, tuple tables; 172k steps/s vs 155k) -- is
  ADMITTED against world.integer.v1. A deliberately WRONG twin (action multiplier 98 for 97) was ALSO
  admitted at first: on the default probe (world_seed 0) the reference's linear ops overwrite every action
  target within the tick, so actions are invisible in the trace and agreement proved nothing (a probe
  without POWER). Fix: the reference check runs over several world seeds (asked of the world, not guessed)
  and asserts that the reference is action-sensitive on the probe; agreement without power is a failed
  check. The wrong twin is now UNAVAILABLE on "reference"; 37/37 components admitted. Suite 187.
  DESIGN NOTE: world.integer.v1 with world_seed 0 is an action-blind world (targets overwritten) -- a
  property of that seed's structure, recorded, not "fixed": a world may be action-blind; the instrument
  must know when it is.
C71 | 04:47Z | wrapped engines (wforge, c6) had no cheat mechanism, so control.cheat.v1 could only be
  INDETERMINATE on them. The WRAPPER now implements the kernel cheat at its own level (the engine is never
  stepped; only the clock moves): both wraps pass admission's controls check with trace_changed=True and the
  cheat control applies to wforge with MET. The old test that documented wforge's lack of a cheat is
  replaced by a fork-registered refusing world (same property, honest fixture). In writing the test C52
  refused my 1-player IR against a 2-slot wforge world -- the guard working as designed.
C72 | 04:47Z | "execution is synchronous": TURN-TAKING is expressible inside the one loop -- a world hands a
  player an ActionSpace of width 0 on ticks it may not act; every reference representation and observer
  survives width-0 spaces (test: round-robin over three representations incl. per-player series). Not an
  assumption removal (the loop is still lock-step), a demonstrated expression. Suite 189 passed 6 skipped.
C73 | 04:49Z | playtest D had to SUBCLASS the selector to evolve statemachine.v2 (gen-0 hard-wired to v1).
  Selectors take `representation`; generation 0 comes from that representation's REGISTERED generator; a
  representation the mutation operator cannot touch gets the structure-preserving shuffle as fallback.
  Tested for v2, v3 and the rewrite system; playtest D's subclass deleted (same results). Suite 190.
C75 | 04:46Z | component CENSUS as data: `python -m prometheus.toolbox.registry` -> every row with its admission
  state on this host (science/COMPONENT_CENSUS_2026-09-19.json): 37 components, 37 ADMITTED; 6 worlds, 5
  substrates, 6 representations, 3 observers, 3 objectives, 8 controls, 4 transforms, 2 selectors.
C76 | 04:46Z | ONE designer text over EVERY registered world (integer, integer_alt, grid, pendulum, c6 wrap,
  wforge wrap): same memory players on kv-lifetime, per-player series, series-gain objective, replay /
  cheat / sham controls -- 6/6 lower, run, replay MET, cheat MET, sham MET. Worlds vary independently of
  players, demonstrated across every world the kernel has. Suite 196 passed 6 skipped.
C77 | 04:50Z | sweeps explode silently. The ELIGIBILITY COUNT (points x arms x seeds) is now part of every
  Lowering's job description, and a declared budget.max_runs refuses the job BEFORE any run, naming the
  arithmetic (300 runs = 50 points x 2 arms x 3 seeds > 100). max_runs, like wall_s, is execution policy
  and outside the scientific digest. Suite 197 passed 6 skipped.
REPORT | 04:54Z (T+2:04) | OVERNIGHT_REPORT_2026-09-19.txt written after the strongest regression (208 passed
  6 skipped; 37/37 mutants; 300-seed fuzz 0 crashes) and pushed (c57a31188). The loop continues below; the
  report's numbers are as of that commit.
C78 | 04:56Z | replay_file over a file whose embedded IR names a component that is now UNAVAILABLE: a DATA
  outcome (status TARGET_UNSUPPORTED, reasons), never an exception. Test added (already the behaviour).
C79 | 04:56Z | resume=True against a receipts file of a DIFFERENT experiment silently interleaved two
  experiments into one chained file. RED; a resume must name the same experiment or is refused with both
  ids (append=True remains the explicit way to add another execution). Suite 199.
C84 | 04:59Z | ZERO-PLAYER experiments: the IR refused players=[] ("nothing would run"); a world observed with
  no player (a pure dynamical system) is a legitimate experiment. players may be empty; the world must
  declare n_players=0 (C52 refuses the mismatch); the integer world runs to its horizon with no player;
  observers, series, replay and cheat apply. The strongest negation of "a player is a conventional agent".
  One old assertion (validate() >= 3 defects on a broken IR) adjusted. Suite 200 passed 6 skipped.
C85 | 05:00Z | the zero-player defect class in every home-written world: `not any(alive)` on an empty list
  ended the episode at tick 1 (integer_alt, grid, pendulum all did it; C84 had fixed only the reference).
  Parametrised RED over the four worlds accepting n_players=0; all fixed; all still ADMITTED (the alt still
  agrees with the reference: the same fix on both sides). Suite 204 passed 6 skipped.
C87 | 05:01Z | the mutation ledger can rot silently (an anchor drifts -> NOT_APPLICABLE -> a hole). A standing
  test asserts every mutant's anchor exists in the current tree. Suite 205.
C89/C90 | 05:03Z | series.schema.json (statuses, encoding, columns, inline-or-artifact) tied to the code by a
  test; a designer-facing package surface (`from prometheus.toolbox import Experiment, ref, execute,
  replay_file, scan, read_all, evolve, admit, census`); importing runs nothing. Suite 206 passed 6 skipped.
