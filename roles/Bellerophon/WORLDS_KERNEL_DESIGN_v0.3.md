# Prometheus Worlds Kernel -- design v0.3 (overnight TDD/playtest snapshot)

Currency: 2026-09-19 04:05Z (mid-window snapshot of the overnight loop; final numbers in the end-of-window
report). Supersedes v0.2 where they differ; v0.2 stays as the Phase 1/2 record. Ledger of every cycle:
roles/Bellerophon/OVERNIGHT_LEDGER_2026-09-19.md (append-only, failed approaches kept).

Authority tonight: THINGS WE TRIED AND OBSERVED WORKING, not what a document says should work. Every line
in section 1 has a test or a committed playtest receipt behind it.

--------------------------------------------------------------------------
1. WHAT RUNS (observed)
--------------------------------------------------------------------------

  python -m pytest prometheus/toolbox/tests -q            176 passed, 6 skipped (Redis unreachable; wsl probe
                                                           runs when wsl is present), ~27 s on M2
  python -m prometheus.toolbox.tests.mutants               27 plausible wrong implementations, 27 CAUGHT
  python -m prometheus.toolbox.examples.exp_001_delay_sweep  96 runs / 7 controls MET (regression FIXTURE)
  python -m prometheus.toolbox.examples.exp_002_substrate_sweep  432 runs, 6 substrates DISTINCT at every point
  playtests/pt_a..pt_e                                     alien mix; changing tasks; MAP-Elites over the kernel;
                                                           everything-at-once + interruption + forensic replay
  registry: 31 components in 8 slots, all 31 ADMITTED by machine predicate on M2
  cross-platform: 87/87 primary trace hashes identical, Windows CPython 3.14.4 vs WSL Linux CPython 3.12.3,
                  including the float-state c6 world (science/CROSS_PLATFORM_REPLAY_2026-09-19.json)
  throughput: 81k steps/s (1 player) / 38k (3 players) with two observers, pure Python, M2

--------------------------------------------------------------------------
2. WHAT CHANGED SINCE v0.2 (by pressure, not by roadmap)
--------------------------------------------------------------------------

Contracts (core ids untouched; extensions added, all provisional and versioned):
  Observer          series flag + series_episode(); DELIVERY ORDER is a contract: events of tick t before
                    on_tick(t) (C1 found the terminal absorption missing from the last record)
  World             reset(seed, keep=True) -> ext.world.lifetime_state.v1 (C40); set_params() at tick
                    boundaries -> ext.world.mutable_params.v1 with TASK_CHANGE (C19); snapshot-based
                    mid-episode checkpoint/resume (C37)
  Substrate         Workspace DOOR (NoWorkspace / KVWorkspace / StreamWorkspace) is the only path from a
                    player to a StateDevice; lifecycle hooks episode_begin/tick -> ext.substrate.lifecycle.v1;
                    per-player substrate overrides in one world (C34); science block carry_over / "no reads"
  Intervention      schedule: [{tick, world_params}] (C19); same-kind wrappers COMPOSE in order (C4)
  Transform         a real slot: shuffle / fresh / relabel / point_mutation with declared `accepts`; controls
                    apply them and record coverage; nothing transformed -> INDETERMINATE (C5); extra player
                    keys (substrate) travel with the player (C35)
  Events            UNKNOWN_<id> retained (C17); STATE_EXPIRE / STATE_DISCARD split from TASK_CHANGE (C23)
  IR                sweep roots + "players"; per-player `substrate`; seed_policy.holdout_seeds -> split;
                    budget.series_max_records / world_state; objects accepted and stored as manifests (C45);
                    non-data values refused (C30)
  Receipt           series (U3, inline <= 512 records else content-addressed artifact, statuses PRESENT /
                    EMPTY / DISABLED / BOUND_EXCEEDED + MISSING / MISSING_ARTIFACT / CORRUPT on verify);
                    prev_receipt_id chain per file (C44); split; SUMMARY embeds the IR (replay_file, C32)
                    and per-split objective aggregates; one job = one experiment_id on every receipt (C29);
                    player_fingerprints {hash, silent} (C5b); repeated observer kinds keyed kind#i (C48)
  Executor          execute(): refuses accidental appends (C22), resume=True continues an interrupted job
                    from valid lines (C29), construction errors and player-count mismatches reported ONCE
                    at lowering (C38, C52); replay_file() re-executes a receipts file alone (C32)
  Search            above the kernel: archive as JSONL rows with GEN_DONE / GEN_ABANDONED markers; resume
                    from rows identical to uninterrupted; rows aggregate per player over seeds (C26/C27)
  Bridges           SFE RUNTIME executor for kind kernel.run_ir tested against sfe.executors (C43); every
                    frontier/NPE mismatch classified (none a kernel defect)

Reference components added: statemachine.v2 (memory slot in the workspace), rewrite.v1 (a rewrite system
as a player), substrate.kv.v1 / substrate.stream.v1, world.grid.v1 (Ludus-shaped), world.c6.composed.v1
(wrap of Archaeon's ComposedWorld, float state quantised), observer.series.v1, objective.series_gain.v1,
four transforms, two selectors.

--------------------------------------------------------------------------
3. DEFECTS THE ROWS FOUND (the night's real product)
--------------------------------------------------------------------------

  C1   terminal absorption missing from the last series record (delivery order)         fixed + contract
  C3   a control silently replaced the designer's permutation (dict keyed by name)        fixed (compose)
  C3   sham/scratch "MET" on players they never touched                                   fixed (coverage)
  C5b  every silent player shares one fingerprint; 49/60 random Proteus genomes silent    flagged in receipts
  C5c  fingerprint probe advanced the Proteus rng + meter (incomplete snapshot)            fixed + test
  C8   dict-valued sweep crashed the executor (unhashable key) = a process halt            fixed
  C9   stream substrate said carry_over=False while the log persisted (hook bypassed)      fixed
  C17  an uncatalogued event kind crashed the trace observer                               fixed (retain)
  C21  series yield column was cumulative over the RUN -> objective identically 0          fixed (false zero)
  C22  a second execution APPENDED to a receipts file; stale rows analysed as fresh         fixed (refuse)
  C23  StateDevice reused TASK_CHANGE for expiry/discard -> task counts inflated            fixed (new kinds)
  C24b undrained device event buffer grew without bound                                    fixed (bounded)
  C26b one archive row per receipt made one player look like two elites                    fixed (aggregate)
  C27  row descriptor from the first seed contradicted the mean objective; buckets saturate fixed (aggregate,
                                                                                            calibratable)
  C29  primary receipts at a sweep point carried a different experiment_id than the arms    fixed (job id)
  C35  transforms dropped per-player substrate overrides: sham ran on other machines         fixed
  C44  deleting a middle receipt was invisible to every check                               fixed (chain)
  C48  two observers of one kind overwrote each other                                       fixed (kind#i)
  C49  a typo'd penalty key cost nothing -- "memory is free"                                reported
  C52  a phantom third player never acted and could win survival                            refused
  FALSE GREENS (tests that passed the wrong code): C1 alive column; C36 three mutants (every control MET;
  resume forgets failed runs; foreign rows committed); C42 two grid mutants (tools never consumed; neighbours
  hidden). Each got a test that the perturbation now fails.
  INCIDENT: an accidental repo-global `git stash pop` (recovered; rule recorded; calibration row).

--------------------------------------------------------------------------
4. ASSUMPTIONS STILL PRESENT (directive s8, honest list)
--------------------------------------------------------------------------

  execution is synchronous: one lock-step loop (observe all -> act all -> step); asynchronous or event-driven
    worlds would need a different loop contract (ext.async.v1, not designed)
  one world per experiment; players share it (heterogeneous machines yes; heterogeneous worlds no)
  communication is stigmergic (through world objects); no message door yet (a substrate door, when needed)
  observations are int lists; continuous actions are not exercised (Physics2D not started)
  series records are per-tick aggregates over players; per-player series is a parameter not yet built
  one objective per experiment (components carry more; a list of objectives is not modelled)
  batched (n_envs) worlds are not modelled (U1); throughput is per-process pure Python

--------------------------------------------------------------------------
5. STATUS OF THE NAMED ITEMS
--------------------------------------------------------------------------

  U3 series            RESOLVED per the ruling (C1); artifact route, bounds, verify/recover, replay, objective
  EXP-002              DONE as a real playtest (432 runs; six substrates distinct at every point; memory charged)
  substrate.kv/stream  DONE; the StateDevice contract did NOT need changing (the door + hooks were missing)
  statemachine.v2      DONE (prefers memory, requires nothing)
  Transform slot       DONE (4 transforms); controls use it
  admission            DONE for every slot; 31/31 admitted
  Redis                UNAVAILABLE on M2 (Windows, WSL, docker): 6 tests skip with the reason; the in-process
                       device passes a 25-seed model-based property test with two proven perturbations
  bridges              SFE runtime executor built and tested against the real sfe.executors; frontier lowering
                       classified (schema/runtime limitations); NPE unknown (interface not on main)
  Box2D / compute      NOT started (phase order; no pressure from any playtest tonight)
