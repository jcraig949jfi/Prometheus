# ABI diff across the existing Prometheus runtimes (BELL-02)

Currency: 2026-09-18. Read-only; every row cites the file it was read from at origin/main 8c86cb1e4
(NPE rows from branch nestor/sidequest-graphworld-2026-09-14 @ b22a09b19, never imported).
"kernel" = prometheus/toolbox/contracts.py (core.*.v1). "adapter LOC" = lines of the wrapper that
exists today (prometheus/toolbox/ref/) or an estimate marked ~.

## 1. World seam

| method / property   | kernel World (core.world.v1)              | wforge Encounter (SerendipityFoundry/worldfoundry/wforge/world.py) | campaign6 ComposedWorld (archaeon/campaign6/worlds/runtime.py) | NPE contract.World (primordial/core/contract.py)        | adapter |
|---------------------|-------------------------------------------|--------------------------------------------------------------------|-----------------------------------------------------------------|---------------------------------------------------------|---------|
| construction        | factory(**params); unknown param refused  | Encounter(mech, world_id, episode_seed): mechanics from a genome   | ComposedWorld(params); world_id() = digest                      | class-specific; n_envs batched                          | wforge: 40 LOC (ref/worlds.py WforgeEncounterWorld); c6: ~60 LOC (state dict is explicit: st) |
| reset(seed)         | yes                                       | seed is a constructor arg (new Encounter per episode)              | reset(seed, ep, shared) -> st                                   | reset(seeds: u64[n_envs]) -> obs                        | wrap constructs per reset |
| observe(pid)        | list[int]                                 | observe(slot) -> list[int]                                         | observe(st) -> [[int]] per channel                              | obs returned by step; uint16[n_envs, n_slots, obs_dim]  | c6: flatten channels |
| legal_actions(pid)  | ActionSpace(width, range)                 | implicit: act_width, values mod 8                                  | implicit: K output channels, 32-bit words                       | act_dim, int32                                          | constant per world |
| step(actions)       | dict pid -> list[int]; returns done       | step(list per slot) -> done                                        | act(st, outputs) then done(st)                                  | step(int32[n_envs,n_slots,act_dim]) -> (obs, charge, done) | wforge: identical shape; NPE: batch axis is the one structural difference |
| trace_hash()        | sha256 hex                                | outcome()["trace_hash"] (sha256 over tick,regs,charge,alive)       | none (evaluate_world returns rows; no per-episode hash)        | trace_hashes() -> list[bytes] per env (THE oracle)      | c6 needs a hash added (~10 LOC, not in its lane) |
| events()            | ext.events.v1, 5-tuples                   | none (yield_events counters only)                                  | none                                                            | none (fabric events are job-level)                      | kernel-native; others emit [] |
| snapshot/restore    | ext.snapshot.v1                           | none (state is plain attributes; ~15 LOC)                          | st is a dict: trivially snapshotable                            | none                                                    | |
| batching            | one env per object; batch = job runs      | one                                                                | one                                                             | n_envs lock-step (numba/Warp)                           | MISMATCH: kernel is per-env; a batched World adapter must map n_envs -> n receipts (design s9) |
| determinism         | BIT (own xorshift streams)                | BIT (xorshift64 streams, no floats)                                | BIT (SplitMix64)                                                | BIT proven == wforge 320/320                            | |
| economy             | charge per player, yield window           | same shape (this is where the kernel world was modelled)           | reward per ask/episode (channel answers)                        | charge int32[n_envs,n_slots]                            | c6 "reward" is an Objective, not a World field |

## 2. Player / Substrate seam

| method             | kernel PlayerSpec + Substrate.instantiate         | Proteus v0 Player (proteus/foundry/vm.py)            | Proteus handover (proteus/graph/handover.py)        | NPE Brain/Genome                              | adapter |
|--------------------|---------------------------------------------------|------------------------------------------------------|-----------------------------------------------------|-----------------------------------------------|---------|
| spec               | PlayerSpec(representation, payload, initial_state, requires, meta) | manifest dict (schema proteus.player_manifest.v0) | manifest schema selects v0/graph                    | Genome.to_bytes(), descriptor()                | proteus: payload = {"manifest": ...} (ref/players.py ProteusTapeInstance, 30 LOC) |
| instantiate        | substrate.instantiate(spec, seed)                 | Player(manifest); fresh_state()                      | player_for(manifest)                                | class-specific                                | |
| act                | act(obs, legal) -> actions                        | run_tick(state, inputs, n_out, rng, meter) -> (outs, status) | same (A1 channel ABI on both substrates)     | act(obs, msg_in) -> (actions, msg_out)        | proteus: inputs=[obs], outs[0] -> actions |
| adapt              | adapt(signal)                                     | none (plasticity is on-tape)                         | none                                                | adapt(signal)                                 | no-op for Proteus |
| cost               | cost() -> raw counters                            | Meter.as_dict(manifest) (ops, categories, faults)    | meter_for(manifest)                                 | cost() -> {params, flops, state_bytes}        | |
| descent            | Transform slot (not on the instance)              | lineage.descend(parent, seed, mate)                  | descend_for(...)                                    | qd operators                                  | Transform wrapper ~20 LOC (Phase 1 not done) |
| fingerprint        | fingerprint() on the FRESH instance, fixed probe  | probes.run_ensemble -> transcript class              | fingerprint_for(...)                                | descriptor()                                  | kernel probe is a stand-in; Proteus's ensemble is richer and should become an Observer |
| substrate identity | Substrate.kind + capabilities + representations   | RUNTIME_HASH (sha256 of vm.py+affordances)          | PROFILES[sub]["runtime_hash"]                       | none explicit                                 | kernel should carry runtime_hash in the substrate manifest for wrapped runtimes (todo) |
| workspace          | ext.workspace.* (Phase 2, via StateDevice)        | tape IS the workspace (persist policy)               | same                                                | Redis-side channel (lingua)                   | the Substrate x workspace experiment of directive s12 |

## 3. Execution / evidence seam

| concept            | kernel                                         | SFE sfe/executors.py                              | archaeon/frontier specs.py + scheduler           | NPE fabric (envelope.py, rows.py)                       | mismatch |
|--------------------|------------------------------------------------|---------------------------------------------------|--------------------------------------------------|---------------------------------------------------------|----------|
| unit of work       | RunSpec (arm x sweep point x seed)             | WorkPackage(work_id, world_id, kind, payload, seed_root) | spec (family, world, organism, params, schedule, seed, budget, controls, capabilities) | job envelope (11 fields) + job_key + kwargs     | frontier spec = evolution SEGMENT, not an experiment on given players (backends/sfe.py names this) |
| result             | Receipt (core.receipt.v1)                      | ExecutorResult(status, result, artifacts, reproducibility) | segment_out.v1 rows + receipts                | rows with frozen status vocabulary + receipt validate()  | reproducibility class: SFE's 4 classes adopted verbatim |
| repro class        | BIT/SEMANTIC/PARTIAL/NONDET (+NOT_RUN)         | same four                                          | replay_required A                                 | oracle names in envelope                                | none |
| capabilities       | negotiate(required, provided) -> result        | none                                              | capabilities.present() probes, BLOCKED_MISSING_CAPABILITY | required_controls / required_oracles lists     | frontier's is the closest existing model; kernel generalises it to component-declared sets |
| controls           | Control objects with mechanical expectations   | none                                              | spec_delta descendants (seed, initialization, budget, replay_A/D) | required_controls names; cheat = row status  | only replay and initialization map to the frontier (backends/sfe.py CONTROL_MAP) |
| ledgers            | engineering / science disjoint                 | result dict                                        | rows                                              | engineering / science disjoint (validate_receipt)       | NPE rule adopted verbatim |
| archive            | Selector ingests receipts -> rows (not built)  | artifacts, lineage_edges in SQLite                | registry/queues JSON                              | Redis archive (qd/archive.py) + committed rows          | all externalised; kernel keeps the rule |

## 4. What the diff decided

1. The kernel World keeps wforge's per-env, integer, trace-hashed shape; batching is the backend's
   concern (NPE) and enters as a capability, not as the core ABI.
2. The Player/Substrate split maps cleanly onto Proteus's manifest/runtime split and onto NPE's
   Genome/Brain split; the flat substrate wraps Proteus v0 in 30 lines with no change to Proteus.
3. Frontier specs are not experiments in the kernel's sense; the SFE lowering therefore succeeds only for
   a frontier-shaped IR (selector = segment) and names every other mismatch (tests pass both ways).
4. NPE's receipt rule (disjoint ledgers) and envelope fields are pinned, not imported (D-BELL-2).

## 2026-09-19 overnight C97 (additive)
- Control.arm(experiment, rng_seed) may ALSO accept `registry=`; the kernel (lower, admission) passes its registry when
  the signature admits it (backends/local.py call_arm). Two-argument controls keep working. Reason: a transform
  control under a forked registry looked its transform up in the process-global one.
- receipts: science.player_fingerprints[pid] gains `spec_hash` (C96) beside `hash` (behavioural class) and `silent`;
  every receipt gains `execution` {batched, batch_size, reason, world?, requested_world?} (C92); engineering.batch on
  batched receipts; SUMMARY splits gain objective_shape / objective_shape_counts / objective_unsupported /
  objective_component_n (C94). budget.batch is execution policy outside the digest (C92).
- ext.batch.v1 catalogued (world face: reset_batch / observe_batch / step_batch / events_batch / trace_hashes /
  summaries / accounting_batch; actions None abandons an env).
- ComponentRecord.admission_params (C94); Registry.batch_implementation(kind, admit_on_demand=True) (C92).
- objective.multi.v1, objective.survival.v2, world.integer_batch.v1 registered; selectors take rank=; search rows
  carry player_hash; search.SelectorNeedsScalar.
