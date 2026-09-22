# Prometheus Worlds Kernel -- design v0.2

Currency: 2026-09-18. Author: Bellerophon[m2-c95cc146]. Supersedes TOOLBOX_DESIGN_v0.1.md (kept; its
Pressure slot is split here into Intervention + Objective, and Substrate is made first-class, per the
operator's WORLDS KERNEL directive, verbatim in prompts/2026-09-18_worlds_kernel/). Status: Phase 1
BUILT AND RUNNING; Phase 2 StateDevice reference BUILT; Redis adapter exploratory; Phases 3-4 designed.

Package: prometheus/toolbox/ (D-BELL-1; the name stays -- the kernel is what the toolbox became, and a
rename would be churn). Tests: prometheus/toolbox/tests/test_kernel.py (22 passed, 1 skipped on M2).

--------------------------------------------------------------------------
0. WHAT RUNS (lead with it)
--------------------------------------------------------------------------

    python -m prometheus.toolbox.examples.exp_001_delay_sweep
      -> 96 runs (4 sweep points x 8 arms x 3 seeds), 97 receipts, 0 failed,
         controls replay/cheat/negative/positive/sham/scratch/permutation all MET
      receipts: prometheus/toolbox/examples/receipts/exp_001.jsonl (committed)

    python -m pytest prometheus/toolbox/tests -q
      -> 22 passed, 1 skipped (Redis: no server reachable on this host)

EXP-001 is a designer's text with no library, host, queue or transport in it:

    Experiment(family="exp001_delay_sweep",
               world=ref("world.integer.v1", n_players=2, world_seed=11, ...),
               substrate=ref("substrate.flat.v1"),
               players=[random_statemachine(101).manifest(), random_statemachine(202).manifest()],
               interventions=[{"name": "conditions", "world_params": {"action_delay": 0},
                               "wrappers": {"observation_delay": 0}}],
               objective=ref("objective.yield_net.v1", penalties={"ops": 0.01}),
               observers=[ref("observer.trace.v1"), ref("observer.descriptor.v1")],
               controls=[ref("control.replay.v1"), ref("control.cheat.v1"), ...],
               sweep={"interventions.0.wrappers.observation_delay": [0, 4],
                      "interventions.0.world_params.action_delay": [0, 2]},
               seed_policy={"base": 1000, "n_seeds": 3}, budget={"episodes": 2, "horizon": 64})
    exp.compile("local") -> LocalJob;  execute(job, path) -> receipts

The same IR compiles to "sfe" (TARGET_UNSUPPORTED with five named mismatches) and to "npe"
(UNAVAILABLE_INTERFACE with a structurally valid BusJob). Section 6 has the F1 verdict.

--------------------------------------------------------------------------
1. ARCHITECTURE (directive s1)
--------------------------------------------------------------------------

    designer text  ->  Experiment IR (ir.py)  ->  compile(target)
                                                   |-- local  -> LocalJob   -> backends/local.execute -> receipts
                                                   |-- sfe    -> FrontierSpec (archaeon.frontier.experiment_spec.v1)
                                                   `-- npe    -> BusJob (envelope + kwargs), pinned interface
    registry (registry.py) holds component rows; admission (admission.py) flips a row ADMITTED/UNAVAILABLE
    capabilities (capabilities.py): components declare, experiments require, negotiate() returns a result
    contracts (contracts.py): World, PlayerSpec, Substrate, PlayerInstance, Observer, Intervention, Objective,
                              Control, Transform, Selector; Event = (tick, kind, player, key, value)
    receipt (receipt.py): core.receipt.v1, disjoint ledgers, content-hashed id, JSONL flushed per record
    state (state.py): StateDevice protocol, InProcessStateDevice (reference), RedisStateDevice (exploratory)

Nothing in the runtime path consults a model, a chat, or a ruling. A missing capability, an unavailable
component, a failed run and a NOT_MET control are each a RESULT for one experiment (s32); the only halt
is a ReceiptWriter integrity error.

--------------------------------------------------------------------------
2. FIRST-CLASS CONCEPTS (s2) -- what each is, in one line, and where
--------------------------------------------------------------------------

  World         an environment object: reset/observe/legal_actions/step/trace_hash (+events, snapshot)   contracts.World
  Player        PlayerSpec DATA: representation id + payload + initial_state + requires + meta          contracts.PlayerSpec
  Substrate     the machine: instantiate(spec, seed) -> PlayerInstance; declares representations it runs
                and the capabilities (workspace.*, tensor.*) it grants; accounts cost                   contracts.Substrate
  Intervention  DATA that changes conditions: world_params overrides + kernel wrappers                    contracts.Intervention
  Objective     evaluate(receipt) -> value + components; declares penalties; reads only                   contracts.Objective
  Observer      begin/on_tick/on_events/measure/describe; kind + version in every receipt                 contracts.Observer
  Transform     apply(obj, seed) over declared object kinds (design only in Phase 1; slot registered)     contracts.Transform
  Selector      propose(archive_rows) / ingest(receipts) -> rows; archive is rows (design only)          contracts.Selector
  Control       arm(exp) -> variant exp; expectation(primary, arm) -> MET/NOT_MET/INDETERMINATE            contracts.Control
  Experiment    the IR (s4)                                                                                ir.Experiment
  Sweep         dotted-path axes -> cartesian points; eligibility count = len(points) x arms x seeds       ir.Experiment.sweep
  Receipt       s4                                                                                         receipt.py
  Capability    versioned id; core (5, immutable) vs ext (open)                                            capabilities.py

Player vs Substrate (s12), as built: statemachine.v1 / constant.v1 / proteus.tape.v0 are REPRESENTATIONS;
substrate.flat.v1 instantiates all three. The Proteus VM is a representation+runtime pair wrapped in 30
lines without touching proteus/. A future substrate.kv.v1 instantiates the SAME representations with a
StateDevice-backed workspace granted as ext.workspace.kv.v1 -- the s12 experiment "same player x flat x
kv x stream x graph x tensor workspace" needs no change to the World.

Pressure -> Intervention + Objective (s2), as built: EXP-001's observation delay and action delay are
Interventions (one kernel wrapper, one world parameter); "yield minus 0.01 x ops" is an Objective
computed from the receipt after the run. The v0.1 idea that pressures carry their own cheat control
survives as control.cheat.v1 (a world-side mechanism the control arms).

--------------------------------------------------------------------------
3. SMALL IMMUTABLE CORE, EXTENSIBLE CAPABILITIES (s3)
--------------------------------------------------------------------------

CORE (5, frozen within v1): core.world.v1, core.player.v1, core.substrate.v1, core.experiment.v1,
core.receipt.v1. EXTENSIONS catalogued in capabilities.EXTENSIONS (21 today); uncatalogued ids are
allowed and reported. Negotiation: exp.derived_requirements() (declared + implied by content: wrappers,
world_params, multiplayer, player.requires) against the union of the world row, the substrate row, the
substrate object and the kernel's own wrapper capabilities. Outcome is a Negotiation value object.
BLOCKED_MISSING_CAPABILITY is a Lowering status for THAT experiment (tests: the next experiment compiles).

--------------------------------------------------------------------------
4. EXPERIMENT IR AND RECEIPT (s4)
--------------------------------------------------------------------------

Schemas: prometheus/toolbox/schemas/{experiment,receipt,capability}.schema.json (JSON Schema 2020-12;
a test asserts they agree with the code's REQUIRED sets and enums; no jsonschema dependency).

IR fields: family, world, substrate, players, interventions, objective, observers, controls, transforms,
selector, sweep, seed_policy, budget, required_capabilities, provenance, id. Identity = sha256 over the
content minus id/provenance. There is no run(). validate() returns defects as data; compile() raises only
on an invalid IR (a designer error, not a runtime state).

Receipt fields: experiment_id/digest, arm, sweep_point, seed, status, components (kinds + manifest hashes
+ the world manifest), capabilities (required/world/substrate), replay_class, trace_hashes (per episode),
events_total, engineering, science (observations by observer kind, world_summary, player_fingerprints,
objective), accounting (raw counters: world_steps, transitions, ops, reads, writes, params, state_bytes,
wall_s, cpu_s), provenance, host, build (kernel_hash over the kernel's own files), timestamps.
receipt_id = sha256(body): an edited receipt fails validate().

--------------------------------------------------------------------------
5. LOCAL EXECUTION PATH (s5, s25)
--------------------------------------------------------------------------

lower(): resolve component rows -> negotiate -> expand arms (primary + one per control) x sweep points x
seeds into RunSpecs. execute(): per RunSpec build world (+ObservationWrapper for kernel interventions),
substrate, instances (fingerprint taken on the FRESH instance = spec identity), observers; run
budget.episodes episodes of the ONE episode loop:

    reset(seed) -> [observe all -> act all -> step -> drain events -> observers] x (horizon or done)

then objective over the receipt; write receipt; after all runs, each control's expectation over
(primary, arm) pairs keyed by (sweep_point, seed); a SUMMARY receipt carries control outcomes and the
registry rows used. ExecutionReport.valid = no failed run and every control MET.

--------------------------------------------------------------------------
6. BACKEND LOWERING STATUS AND THE F1 FALSIFIER (s5)
--------------------------------------------------------------------------

  target  status for EXP-001        status for a frontier-shaped IR             file
  local   OK, executed              OK                                          backends/local.py
  sfe     TARGET_UNSUPPORTED (5)    OK: validated archaeon.frontier spec        backends/sfe.py
  npe     UNAVAILABLE_INTERFACE     UNAVAILABLE_INTERFACE (BusJob valid)        backends/npe.py

F1 ("one nontrivial Experiment compiles to both SFE and NPE without rewriting its scientific
definition"): NOT YET DECIDABLE for NPE (interface not on main: D-BELL-2) and FALSE for SFE as the
frontier stands, with the exact mismatches, all semantic, none transport:

  M1  a frontier spec is an EVOLUTION SEGMENT (foundry/c4 population x generations x descent grammar),
      the IR is an experiment on given players; only IR with selector=selector.frontier.segment.v1 and
      players=[] lowers
  M2  frontier WORLD_KINDS are wse.WorldSpec | c6.composed.v1 | c6.composed.sample; a kernel world enters
      SFE only as one of those or through a new Executor kind that Vivarium claims
  M3  the segment evaluator's reward is fixed (per_ask | episode): IR objectives do not lower
  M4  frontier observation = the frozen detector set: IR observers do not lower
  M5  frontier controls are spec deltas (seed, initialization, budget, replay_A/D): of the kernel's seven,
      replay and scratch lower; cheat, negative, positive, sham, permutation have no expression
  M6  kernel interventions with wrappers (observation delay/permute) have no frontier expression;
      world_params do, for c6 worlds

The honest reading: SFE-the-runtime (sfe/executors.py) can run a kernel job as a new Executor kind in a
few dozen lines on Daedalus's side (WorkPackage.payload = the IR, ExecutorResult.result = receipts); it is
the FRONTIER SCHEDULER's spec that cannot express the IR. That is the seam to open, not the IR.

NPE: a BusJob is built against the pinned envelope (11 fields, b22a09b19) and validated structurally.
Semantic mapping: job_key "kernel.run_ir" -> the local executor; receipts re-emitted as fabric rows
(status "record", evidence_class "OBSERVATION"). No IR field is lost; the fabric's stage-admission
ceilings are execution policy in the envelope, not science in the IR. Becomes OK when a one-file worker
lands on main with primordial/.

--------------------------------------------------------------------------
7. PHASE 2 -- STATE DEVICE (s6, s7, s8, s23, s26) -- BUILT (reference) + EXPLORATORY (Redis)
--------------------------------------------------------------------------

Protocol state.StateDevice: advance(tick), end_scope(scope), put/get/delete, hset/hget, append/read
(streams with maxlen), zadd/zrange, events(), accounting(), snapshot()/restore().
Lifetimes: scope in ephemeral | episode | lifetime | persistent; ttl in LOGICAL TICKS (the device never
reads a wall clock; Redis EXPIRE is deliberately not used so replay is clock-free). Bounded: max_keys and
per-stream maxlen refuse with a RESOURCE_CHANGE event, never an exception. Every op is counted so a
Substrate can charge a Player for remembering. Events are kernel Event tuples (STATE_READ, STATE_WRITE,
MESSAGE, TASK_CHANGE for expiry/discard) so a stream transport carries them unchanged.
Reference InProcessStateDevice: 22 tests' script covers ttl expiry, scope ends, persistent survival,
streams since-id, ranked range, snapshot/restore boundary. RedisStateDevice: same script, same expected
values, SKIPPED on M2 (no server on the Windows side or in WSL; M1 has one on 6390 -- the first run there
is the acceptance test). Namespaced keys; snapshot = SCAN of the namespace to JSON, so a crashed run is
reconstructable from the last snapshot + receipts and Redis is never the sole copy (s23).

Redis boundary, specifically: the device owns key lifetimes (a meta table in the device, not Redis
TTLs); Players never see Redis; a Substrate exposes at most {workspace.read, workspace.write,
workspace.append, workspace.link, workspace.rank, workspace.ttl} as ext.workspace.* capabilities backed
by whichever device the experiment names. Experiment definitions, receipts, provenance and archives are
never written to a StateDevice.

Not yet built: substrate.kv.v1 (a Substrate that grants ext.workspace.kv.v1 through a StateDevice to
the existing representations). That is the next slice (s12 experiment).

--------------------------------------------------------------------------
8. PHASE 3 -- COMPUTE DEVICE BOUNDARY (s9, s24) -- DESIGNED
--------------------------------------------------------------------------

ComputeDevice protocol (to be added as compute.py): kind, capabilities {tensor.dense.v1,
tensor.sparse.v1, tensor.matmul.v1, tensor.contract.v1, tensor.reduce.v1, tensor.gather.v1,
tensor.scatter.v1, tensor.nearest.v1}; ops take and return device handles; to_host(handle) -> bytes
(canonical interchange: int32/uint16 arrays, fixed-point for floats with the scale in the manifest);
accounting() counts ops and bytes moved. NumPyDevice first; CuPy/torch (present on M2: torch cu128) and
GraphBLAS (NPE B2 proved the semantics) only when an experiment requires them. A World or Substrate
declares requires={"tensor.dense.v1", ...}; negotiation binds a device or blocks that experiment. Rule
kept from NPE R7: a device that changes trace hashes on an integer world is not admitted for it (the
oracle wins over the speedup). Player-visible tensor ops are Substrate grants and are cost-accounted.

--------------------------------------------------------------------------
9. PHASE 4 -- BOX2D (s11, s28) -- DESIGNED, NOT STARTED
--------------------------------------------------------------------------

world.physics2d.v1 over Box2D v3's C API (ctypes; built in WSL on M2 per D-BELL-3 with compiler,
version, flags and dependency hashes recorded). Capabilities: ext.physics2d.v1, ext.continuous_actions.v1
(actions as fixed-point int32 with a declared scale), ext.events.v1 (CONTACT from contact events),
ext.replay.semantic.v1 with a tolerance DECLARED IN THE MANIFEST before any run; trace_hash over the
quantised body state per tick. One conformance world: a box on a slope with one actuated joint; no
rendering. Admission adds: cross-host semantic replay rows, headless batching throughput vs n_worlds.
Blocked on: nothing but ordering (s11: after the minimal kernel works -- it now does) and the Techne
acquisition of the Box2D v3 source (held under D-BELL-4 until this phase is opened).

--------------------------------------------------------------------------
10. CRIUS AND LUDUS AS FALSIFIERS (s29, s30)
--------------------------------------------------------------------------

The IR can already state: multiple players (ext.multiplayer.v1), lifetime reset (seed_policy + episodes),
task sequence (sweep over interventions), ablation/transplant/scramble (Control kinds are reserved:
ablation, transplant; sham/permutation exist), held-out qualification (a sweep point the objective
excludes -- NOT yet a first-class concept), experience-to-competence (an Objective over a receipt that
carries per-episode measures -- the receipt carries per-episode trace hashes but observers report totals:
a per-episode observation series is a missing concept, recorded here). Persistent workspace and
executable artifacts are Phase 2 (substrate.kv.v1) and ext.workspace.executable.v1 (not designed beyond
the id). These are the four concepts to watch when a Crius experiment is expressed: held-out split,
per-episode series, executable artifacts, workspace-carrying substrate.

--------------------------------------------------------------------------
11. ADMISSION (s19) -- BUILT for worlds
--------------------------------------------------------------------------

admission.admit_world(kind, registry): registry row, provenance (author, license, route), well-formed
capabilities, conformance (Protocol + one episode), demonstrable extensions (events()/snapshot() if
declared), replay (BIT: equal traces over 3 seeds), reference agreement (family reference if one exists),
controls (the cheat mechanism changes the trace; a world without it is noted, not failed), performance
receipt (steps/s, dated, python version). Result: ADMITTED or UNAVAILABLE, in-process and as data.
On M2: world.integer.v1 ADMITTED (155k steps/s in the admission probe); world.wforge.encounter.v0
ADMITTED (64k steps/s; no cheat mechanism -> noted); a deliberately non-replayable world -> UNAVAILABLE
on "replay" and an experiment naming it -> TARGET_UNSUPPORTED while the next experiment runs (test).
Substrate/observer/control admission predicates: same shape, next slice.

--------------------------------------------------------------------------
12. WRITE / WRAP / BIND / CHOP (s21) -- the registry route column
--------------------------------------------------------------------------

  write  world.integer.v1, statemachine.v1, constant.v1, substrate.flat.v1, observers, objectives,
         7 controls, state.inprocess.v1
  wrap   world.wforge.encounter.v0 (Ludus), proteus.tape.v0 (Proteus), state.redis.v1 (exploratory)
  bind   world.physics2d.v1 (Phase 4), compute devices (Phase 3)
  chop   selector.poet_admission / observer.pata_ec / selector.go_explore (Nyx, held under D-BELL-4)

--------------------------------------------------------------------------
13. FALSIFIERS AND UNRESOLVED MISMATCHES
--------------------------------------------------------------------------

  F1   SFE: FALSE today for a general IR (M1-M6 above); TRUE for frontier-shaped IR. NPE: undecidable
       until primordial/ lands. The kernel side of the bridge (Executor kind for SFE, job_key worker for
       NPE) is one file each on the owners' sides; the frontier SPEC cannot express the IR and should not
       be bent to.
  F2   (v0.1) pressure-as-transformer: dissolved by the Intervention/Objective split; kernel wrappers are
       the only transformers and they are two (delay, permute); a wrapper that does not bind to a world is
       a capability negotiation failure, not a silent no-op.
  F3   admission cost vs write cost for Box2D: open until Phase 4.
  F4   whether any admitted world changes what an R16-style screen finds: not the kernel's claim to make;
       the kernel's job is to make the screen expressible (a Selector + sweep) -- Selector is not built.
  U1   batched worlds (NPE n_envs) vs the per-env kernel World: the adapter is n_envs -> n RunSpecs in one
       process, which loses NPE's lock-step throughput unless the batch is inside the world; an
       ext.batch.v1 capability is the likely answer and is not designed.
  U2   substrate runtime identity for wrapped runtimes (Proteus RUNTIME_HASH) is not yet in the substrate
       manifest; receipts carry it only through PlayerSpec.meta.
  U3   per-episode observation series (needed for experience-to-competence) is not in the receipt.
  U4   Redis adapter untested on this host.

--------------------------------------------------------------------------
14. NEXT IMPLEMENTATION SLICE
--------------------------------------------------------------------------

  1  substrate.kv.v1: the flat substrate + a StateDevice workspace granted as ext.workspace.kv.v1 to a
     representation that can use it (statemachine.v2 with read/write ops), and EXP-002 = same players x
     {flat, kv, stream} substrates (directive s12) -- the first experiment only the kernel can express.
  2  per-episode observation series in the receipt (U3) and an Objective that reads it.
  3  Transform slot: relabel / permute / graft / sham-graft over statemachine.v1 and proteus.tape.v0
     (via lineage.descend), so scratch/sham controls stop special-casing representations.
  4  admission predicates for substrate, observer, control.
  5  Redis acceptance on M1 (one run of the state script against 127.0.0.1:6390), then the SFE Executor
     kind packet to Daedalus and the NPE worker packet to Nestor (one file each; drafted, not posted).
  6  Phase 3 NumPyDevice + ext.batch.v1 design (U1).
