# prometheus.toolbox -- the Prometheus Worlds Kernel

Design of record: roles/Bellerophon/WORLDS_KERNEL_DESIGN_v0.4.md (v0.3 = first half of the overnight loop, v0.2 =
Phase 1/2 record; the overnight
ledger roles/Bellerophon/OVERNIGHT_LEDGER_2026-09-19.md records every cycle that changed this package).
Owner: Bellerophon (contracts, IR, capability model, device boundaries, adapters, reference implementations,
admission, lowering, conformance tests). Designers (Archaeon, Crius, Nestor, ...) own what to run; this
package makes it executable and never decides what is interesting.

    python -m pytest prometheus/toolbox/tests -q                  # conformance suite (pure stdlib)
    python -m prometheus.toolbox.tests.mutants                    # mutation ledger (every mutant must be CAUGHT)
    python -m prometheus.toolbox.examples.exp_001_delay_sweep     # the regression FIXTURE experiment
    python -m prometheus.toolbox.examples.exp_002_substrate_sweep # same players x six workspaces
    python -m prometheus.toolbox.playtests.pt_e_everything        # everything + interruption + forensic replay

A designer's text names components by registry KIND and parameters, never a library, host, queue or
transport:

    Experiment(family=..., world=ref("world.grid.v1", n_players=3, ...), substrate=ref("substrate.mailbox.v1"),
               players=[random_statemachine_v3(1), ...], interventions=[{"name": "tasks", "schedule": [...]}],
               objective=ref("objective.series_gain.v1"), observers=[ref("observer.series.v1", per_player=True)],
               controls=[ref("control.replay.v1"), ref("control.cheat.v1"), ref("control.ablation.v1")],
               sweep={"world": [A, B], "players": [popA, popB]}, seed_policy={"base": 1, "n_seeds": 3, "holdout_seeds": 2},
               budget={"episodes": 3, "horizon": 40, "world_state": "lifetime", "batch": 8})   # batch = execution policy, not science
    low = exp.compile("local")            # Lowering(status OK | BLOCKED_MISSING_CAPABILITY | TARGET_UNSUPPORTED, reasons)
    execute(low.job, "receipts.jsonl")    # one file = one execution; resume=True continues an interrupted job
    replay_file("receipts.jsonl", "replay.jsonl")   # re-executes the IR embedded in the summary on the SCALAR path; divergences are data

Objectives may be vectors (objective.multi.v1 = named components; objective.survival_per_player.v1 reads the
per-player series); a selector then takes rank="component" or is selector.pareto.v1 (by_cell=True for a front
per descriptor cell). Search above the kernel: evolve(template, selector, generations, workdir, seed,
compact=True) -- rows carry player_hash + the receipt they came from; player_of(row, workdir) fetches a
manifest. A world may return structured observations (nested JSON of ints) -- players flatten(); permute is
refused for them. Every instrument in this package has a test where it says NO:
roles/Bellerophon/science/POWER_REGISTER_2026-09-19.md.

Layout

    capabilities.py   5 immutable core ids + catalogued ext ids; negotiate() -> result, never an exception
    contracts.py      World / PlayerSpec / Substrate / PlayerInstance / Observer / Intervention / Objective /
                      Control / Transform / Selector; Event 5-tuples; observer delivery ORDER is a contract
    ir.py             Experiment IR: data (objects are converted to manifests), digest, validate, sweeps
                      (roots: world, substrate, interventions, budget, seed_policy, objective, players),
                      compile(target); no run()
    receipt.py        core.receipt.v1: disjoint ledgers, content-hashed id, per-file chain (prev_receipt_id),
                      strict read_all vs forensic scan (truncation / edit / duplicate / deletion named by line)
    series.py         per-episode observation SERIES as receipt data (inline <= 512 records else a
                      content-addressed artifact); self-describing columns; statuses; verify / recover
    registry.py       component rows; fork() for anything that registers its own components
    admission.py      machine predicate per slot -> ADMITTED | UNAVAILABLE (no approver)
    state.py          StateDevice protocol; InProcessStateDevice (reference, model-tested); RedisStateDevice
                      (exploratory; skipped where no server)
    search.py         ABOVE the kernel: selectors over archive ROWS (GEN_DONE / GEN_ABANDONED markers), resume
    backends/local.py lowering + the ONE episode loop + executor (resume, wall budget, checkpoints) + replay_file
    backends/sfe.py   lowering to archaeon.frontier specs (partial; mismatches classified)
    backends/sfe_executor.py  a kernel Executor for the SFE RUNTIME's worker loop (kind kernel.run_ir)
    backends/npe.py   BusJob against the pinned NPE envelope (UNAVAILABLE_INTERFACE until primordial/ lands)
    ref/              reference components (40, all admitted on M2): worlds integer / integer_alt / integer_batch
                      (numpy, ext.batch.v1) / grid (flat or structured observations) / pendulum (SEMANTIC) /
                      wforge (wrap) / c6 composed (wrap); representations statemachine v1/v2/v3, constant,
                      rewrite, proteus tape (wrap); substrates flat / kv / stream / mailbox / artifact;
                      observers trace / descriptor / series; objectives yield_net / survival v1,v2 / series_gain /
                      multi (named components); 8 controls (each with a test where it says NO -- see
                      roles/Bellerophon/science/POWER_REGISTER_2026-09-19.md); 4 transforms; 2 selectors (rank=)
    schemas/          JSON Schema for the IR, the receipt and the capability model (tied to the code by a test)
    examples/ playtests/   experiments with their committed receipts (replayable from the file alone)
    tests/            conformance, series, workspace, DOF, integrity, fuzz, state model, search, admission,
                      bridges, cross-platform, playtest findings (smallest reproducers, kept permanently)

Rules the code enforces: integer actions / events, observations as nested JSON of ints (opaque to the kernel;
players flatten(); permute only for flat ones); execution policy (budget.batch, wall_s, max_runs) outside the
scientific digest, batched receipts equal scalar receipts run for run; a missing capability or an unavailable
component blocks one experiment only; a failed run is a receipt; controls are objects with mechanical
expectations (INDETERMINATE when they could not act); Redis is never the sole copy of anything scientific;
one receipts file = one execution unless resume / append is explicit; SEMANTIC worlds declare their quantum
before any run and never widen it.
