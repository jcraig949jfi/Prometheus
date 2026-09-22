# Phase 1 -- Atlas <-> BEE capability correspondence (read-only pass, 2026-09-19 12:40-13:05Z)

Sources read: atlas/README.md, roles/Atlas/{MODEL,STATUS,SOURCES}.md, atlas/sql/001-003 + views.sql, atlas/db.py;
schema atlas on M1 (read-only SELECTs); archaeon/campaign{1..5} reports, PREREG/RECEIPT/rows of the SFE candidates;
Atlas facts/conclusions/sources of the NPE candidates (their campaign directories are on Nestor's M1-local branch and
are NOT readable from M2 -- every NPE statement below is what Atlas indexed). BEE = prometheus/toolbox at 087666a6f+
(WORLDS_KERNEL_DESIGN_v0.4.md). Nothing in either system was modified in this phase.

## 1. Atlas's model in one paragraph

Three layers in separate tables: WHAT RAN (attempt, segment; facts layer RAN), WHAT WAS SEEN (fact layer OBSERVED,
every fact -> fact_evidence -> source), WHAT WAS SAID (conclusion, verbatim/by pointer, never overwritten), and WHAT
ATLAS SAYS (atlas_class/_confidence/_method, ATLAS_DERIVED facts/edges/signals). Identity: engine -> campaign ->
experiment -> attempt -> segment, keys built from NATIVE ids only ('<program>/<native>:<native>#<native>@<native>').
Lineage is one typed edge table (EXECUTION / SCIENTIFIC / ORGANISM / PROVENANCE) with relations incl. RERUN_OF,
DESCENDANT_OF, DEFORMATION_OF, REPLICATION_OF, TRANSPLANT_OF ("the parent's question moved to another
world/substrate/engine") and reason CROSS_SUBSTRATE_TRANSPLANT -- the vocabulary for Phase 7 already exists.
Sources are first-class pointers with visibility (GIT_REMOTE | GIT_LOCAL:<host> | FS:<host> | PG:<host> |
EXPECTED:<host>); a rerun never overwrites its parent; validity states include INSTRUMENT_FAILURE and
PARTIAL_EVIDENCE; signals (weak-signal layer) are never directives.

## 2. Correspondence table

| Atlas concept (schema / SFE / NPE usage) | BEE-native concept | relation | note |
|---|---|---|---|
| engine (sfe, npe, vivarium) | a Lowering target: local / sfe / npe; BEE itself = a new engine row 'bee' | ANALOGOUS | BEE executes locally (compile("local")); receipts name build.kernel_hash + host |
| engine_instance (eng_906356...) | receipt.build {kernel_hash, n_files} + receipt.host | ANALOGOUS | BEE mints no instance id; Atlas rule: synthetic 'bee@<host>:<kernel_hash12>' |
| campaign | an Experiment.family + a workdir of receipts files (a search = gen_NNN_aK.jsonl + archive.jsonl) | ANALOGOUS | no campaign object in BEE; the adaptation packet plays that role |
| experiment (native id, question, world/organism/pressure/search families, seeds, budget) | Experiment IR: family, world ref, players, substrate, interventions, objective, observers, controls, sweep, seed_policy, budget; experiment_id = family/digest | ANALOGOUS | BEE's digest excludes execution policy (wall_s, max_runs, batch); Atlas prereg_digest/design_digest map to the frozen preregistration hash |
| attempt (of_record, rerun_of, resumed_from, host, commit, code_digest) | one receipts file = one execution; resume=True continues the SAME job (C29/C79); append=True = a second execution; RunSpec(arm, sweep_point, seed, split) | ANALOGOUS | BEE keys resumes by (arm, sweep point, seed), not by attempt number; a rerun is a new file |
| segment (chunk/step/epoch/cell) | one receipt (a run = episodes x horizon ticks); generation files for search | ANALOGOUS | |
| fact layer RAN (budgets, timings, seeds, host, code) | receipt.engineering {wall_s, cpu_s, ticks, steps_per_s, batch}, accounting, started/finished_utc, host, build | IDENTICAL in kind | BEE separates the ENGINEERING and SCIENCE ledgers by construction |
| fact layer OBSERVED (measurements, controls, detector firings, descriptors) | receipt.science {observations by observer kind, world_summary, player_fingerprints, objective}, series (U3), SUMMARY.science.controls/splits | IDENTICAL in kind | observer.trace/descriptor/series; objective value may be a vector (named components) |
| fact layer CONCLUDED (dispositions) | none -- BEE judges nothing scientific | OMITTED by design | the shim's comparison packet is the conclusion layer, authored by Bellerophon |
| SFE world = WSE cell (W0, W1_d4, W2_K2 ...: ask/answer streams, delay, K streams) | world.integer.v1 (registers, hidden yield window, action_delay, regime_period, stoch), grid, pendulum, wforge Encounter (wrap), c6 composed (wrap) | ANALOGOUS / UNREPRESENTABLE | delay and regime map to integer/wforge params; ask/answer streams and per-ask credit have no BEE world |
| NPE world = Encounter genomes w1..w5 (lane B NpEncounter), NK stubs, signal worlds, cw01 economics worlds (necessity / composition / weather) | world.wforge.encounter.v0(genome_seed=k) IS the wforge de_novo world family; economics worlds are not BEE worlds | IDENTICAL (Encounter) / ANALOGOUS (economics via substrate doors) | cw01's "affordances" (A1 write, A4 re-enter) correspond to substrate DOORS (kv/stream/mailbox/artifact) |
| organism / representation (Proteus player-VM programs; TT/linear brains; policy vectors; inclusion vectors) | Player representations: statemachine v1/v2/v3, constant, rewrite, proteus.tape.v0 (wrap of the SAME Proteus VM) | IDENTICAL (Proteus) / ANALOGOUS | open-loop action TENSORS (E4b/E10) have no BEE representation yet -> sequence.v1 (Phase 3 scaffolding) |
| pressure / selection (tournament, elitism, ancestor-relative info per resource) | Objective (yield_net with penalties, survival v1/v2/per-player, series_gain, multi) + Selector (truncation, map_elites, pareto[/by_cell]) | ANALOGOUS | BEE objectives charge memory ops by NAME; "ancestor-relative" = objective minus generation-0 mean (shim computes) |
| search (N, G, E; QD archives in Redis; foundry gen 0) | search.evolve over archive ROWS (GEN_DONE/ABANDONED markers, resume, compact rows, player_hash identity) | ANALOGOUS | BEE evaluates a player on n_seeds x episodes; SFE's E = episodes per generation |
| ruler / held-out evaluation (top-16 on 64 held-out seeds; competence_heldout) | seed_policy holdout_seeds + SUMMARY.splits; replay_file for re-evaluation; the shim evaluates elites on a held-out seed range | ANALOGOUS | |
| controls (positive/negative/cheat/permuted/CRN/sham/cost-matched sham) | control.replay/cheat/negative/positive/sham(shuffle)/scratch(fresh)/permutation/ablation with POWER (each has a test where it says NO) | IDENTICAL in kind | CRN: BEE keys every seed's world init on (world_seed, seed) -- arms share generation 0 and seeds by construction |
| interventions (world params, schedules, weather/damage, doses, caps) | interventions.world_params / wrappers (delay, permute) / schedule (set_params at ticks); injection into gen 0 = Phase 3 scaffolding; offspring cap = none | ANALOGOUS / UNREPRESENTABLE (cap; in-life organism-state damage) | |
| retention / workspace / backend swap (mem vs redis) | Substrate doors + StateDevice (in-process reference; Redis device behind PK_REDIS_URL, unreachable: authenticated) | IDENTICAL in kind | "physics survives a backend swap" = BEE's device-model equivalence test (25-seed model, streams model) |
| telemetry / per-organism counters | accounting (ws_reads/writes/appends/refused/expired/discarded, ops, params, state_bytes), series columns per player | IDENTICAL in kind | |
| replay / determinism ("a01 reproduced ... exactly from attempt_id alone") | replay_file (scalar path, divergences are data), control.replay, BIT/SEMANTIC classes with declared quantum, cross-platform probe | IDENTICAL in kind | BEE replays ALL 38 committed receipts files 0/1296 divergent on Linux 3.12 |
| provenance (harvest_run, commit sha, worktree, dirty) | receipt.build.kernel_hash, host, provenance dict (designer-supplied), Experiment.provenance | ANALOGOUS | |
| lineage edges (RERUN_OF, DESCENDANT_OF, TRANSPLANT_OF, ORGANISM ancestry) | Experiment.provenance.parent + sweep_point; archive rows: player_hash, source {file, receipt_id}, meta.parent/transform (organism ancestry through meta inheritance) | ANALOGOUS | Atlas's TRANSPLANT_OF / CROSS_SUBSTRATE_TRANSPLANT is the edge an adaptation should carry |
| defects (friction ledger; CW01-Dnnn) | overnight ledger cycles; failure_signature entries; receipt.error on FAILED runs | ANALOGOUS | |
| validity_state (VALID / INSTRUMENT_FAILURE / PARTIAL_EVIDENCE / SUPERSEDED) | ExecutionReport.valid (0 failed, 0 unstarted, every control MET); scan() forensic codes; runs_not_started/stopped_reason | ANALOGOUS | INDETERMINATE controls count AGAINST valid in BEE |
| signal (weak-signal layer) | none | OMITTED | not a kernel concern |

## 3. What BEE has that the Atlas model has no column for (candidate Phase 7 vocabulary)

- execution POLICY vs science: budget.batch / wall_s / max_runs are outside the digest; batched receipts equal scalar receipts run for run.
- objective SHAPE (scalar / vector / none / UNSUPPORTED / MIXED) as a first-class summary field.
- instrument POWER as a maintained property (POWER_REGISTER): every control/admission check has a test where it says NO.
- behavioural class vs spec identity of an organism (probe fingerprint vs manifest hash).
- series as receipt data (U3): per-tick, per-player trajectories with verify/recover states.

## 4. Consequences for the adaptation layer

- The five BEE core ids are not touched. The shim lives beside the kernel (prometheus/atlas_bee/) and emits BEE IRs + search runs; BEE keeps its receipts, replay, admission, failure semantics.
- Scaffolding that is BEE-native and reusable goes INTO BEE with tests (Phase 3 lists it: sequence.v1 open-loop players; evaluation battery over world variants; seed players injected at generation 0 with origin tracking; recurring episode seeds; a workspace-weather substrate door).
- Anything a BEE object cannot state -- SFE ask/answer streams, per-ask credit, the offspring cap, in-life damage to an organism's HIDDEN state -- is classified UNREPRESENTABLE/OMITTED in the translation manifest, never approximated silently.
