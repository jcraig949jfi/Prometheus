# Seat dossier: Bellerophon

- Crawler: Sisyphus (forensic crawl worker), crawl date 2026-10-01
- Base SHA of worktree: 19299e06b (F:/Prometheus-worktrees/sisyphus-base-role, = origin/main at crawl time)
- Epistemic tags used inline: [IMPL] implementation fact; [INTENT] design intent; [HIST] historical claim;
  [RESULT-UNVERIFIED] reported result not re-established here; [CORRECTION] later correction/contradiction;
  [CODE-INFERRED] capability inferred from code; [UNKNOWN] unknown/ambiguous.
- Nothing was re-run. All numbers are recorded numbers unless tagged [IMPL].

## Coverage statement

Read (directly, or by a read-only helper pass whose notes I spot-checked against source and git):
- roles/Bellerophon/: RESPONSIBILITIES.md, STATUS.md, STATUS_REPORT_2026-10-01.md, WORK_STATE.json, BACKLOG_H0H5.md,
  calibration/LEDGER.md, prompts/ (charter 09-18, WORLDS KERNEL 09-18, overnight TDD 09-19, atlas-bee pilot 09-19,
  Z80 x Atlas 09-19, post-campaign forensics 09-23), TOOLBOX_RESEARCH/DESIGN, WORLDS_KERNEL_DESIGN v0.2/v0.3/v0.4,
  ABI_DIFF, OVERNIGHT_REPORT and OVERNIGHT_LEDGER (1,081 lines), atlas_bee/ preregs/results/review packet,
  forensics_2026-09-23/ (POST_CAMPAIGN_FORENSICS, ISSUE_AND_REPAIR_LEDGER, GROUNDING_PREREG/REPORT,
  ERRATA_2026-09-29), coupling_2026-09-24/ (PREREG, REPORT, FAILURE_LEDGER, IMPLEMENTATION_AUDIT), multiday_2026-09-26/,
  e003_2026-09-29/ (result + errata), repl_2026-09-30/ (PREREG, RESULT, ERRATA_REPL01, RESULT_02), science/.
- prometheus/toolbox/ (112 files, ~11k Python lines): capabilities.py, ir.py, registry.py, admission.py, receipt.py,
  series.py, state.py, search.py, backends/{local,sfe,sfe_executor,npe}.py, ref/ (worlds, players, substrates,
  controls, objectives), tests and playtests listing. prometheus/atlas_bee/.
- prometheus/z80atlas/ (vm.py read directly; world.py, grammar.py, tasks.py, coupling.py, controls.py, adjudication.py,
  multiday*, tests/golden_v1.json via helper).
- git history of roles/Bellerophon, prometheus/toolbox, prometheus/z80atlas; origin/bellerophon/* branches (0 unmerged
  commits except c4-rmech 164df3cdd).
- Cross-seat: roles/Harmonia/audits EVIDENCE_AUDIT_2026-09-30_SAMPLE2/3/4 and STANDING_RULES F7/F8; Atlas digests
  (ensorain_bellerophon.md), ATLAS_CONTRADICTIONS, atlas/registry.json; Achilles census rows; Cosmos PROVENANCE.md.

NOT read, and why:
- Host-local evidence on M2 (C:/Users/James/z80atlas_campaign_2026-09-19/ CAMPAIGN_PACKET.md, coupling/multiday
  results.jsonl 129 MB, atlas-bee run workroot receipts): not in git; recorded only by sha256.
- The c4-rmech interim review in detail (it reviews a Cosmos holdout-adjacent design; read only via status report).
- Any holdout or nestor_secrets path (hard rule). The 09-26 rulings item #550 (a Cosmos C3 item) was not opened.

---

## 1. Identity and purpose

- Canonical name: Bellerophon. Created 2026-09-18 21:18 EDT (commit 44dc09559), base role adopted, charter PENDING
  [HIST]. Row in roles/base-role/INHERITANCE.md:13.
- Host: M2 / SPECTREX5 (Windows, CPython 3.14.4; WSL Linux py3.12 used for cross-platform replay checks). Runtime
  evidence lives under C:/Users/James/... on M2; Achilles' census flags this user path as possibly a different machine
  account from other M2 seats, unverified [HIST: roles/Achilles/census/registry/seats_part1.json].
- Instances: Bellerophon[m2-c95cc146] (09-18/19), Bellerophon[m2-9e74888e] (09-23 forensics); later sessions
  claude-opus-5-5.
- Alias "BEE" changes referent [IMPL/HIST]: on 09-19 (Atlas->BEE pilot) BEE = the toolbox ("Bellerophon Emergence
  Engine"); from ~09-25 (E-003, REPL-01, the "BEE register-world axis" commit 35b2fde55) BEE = the prometheus/z80atlas
  Z80 soup. Atlas uses BEE in the second sense ("Z80 triplet: NPE, BEE, Archaeon z80atlas").
- Original charter [INTENT: prompts/2026-09-18_charter/]: set up the seat, research tools, "build out toolboxes" for
  SFE and NPE. The same night the WORLDS KERNEL directive (prompts/2026-09-18_worlds_kernel/
  00_OPERATOR_DIRECTIVE_verbatim.md) reframed it: "This is no longer merely a toolbox"; build a backend-neutral WORLDS
  KERNEL with first-class World, Player, Substrate, Intervention, Objective, Observer, Transform, Selector, Control,
  Experiment, Sweep, Receipt, Capability; a tiny immutable core of 5 ids plus versioned ext.* capabilities; the IR
  has no run() and lowers to local|sfe|npe; phases 1 core+local, 2 StateDevice (InProcess + Redis), 3 ComputeDevice
  (NumPy, then CuPy/GraphBLAS), 4 Box2D. Ownership: contracts/IR/devices/adapters/admission/lowering/conformance,
  explicitly NOT "which hypotheses ... which worlds are interesting". Closing line: "BUILD THE BORING KERNEL THAT
  LETS THE STRANGE THINGS EXIST."
- Charter changes / pivots (section 11): 09-19 overnight TDD loop; 09-19 Atlas->BEE pilot; 09-19 operator forwarded
  Nestor's Z80 x Atlas directive ("I asked this of Nestor. Try doing the same thing.") -> Bellerophon becomes a
  substrate scientist; 09-23 forensics directive addresses the seat as "responsible for the Z80 x Atlas emergence
  substrate and campaign harness"; 09-25 RESPONSIBILITIES s7 addendum (5711b7b49) formally overrides s4 ("never runs
  experiments for a scientific claim of its own") for z80atlas science; 09-28 fleet MWO model; 09-30 replication
  attempt of Nestor's C-A3; 09-30/10-01 reviewer of Cosmos C4 (R-MECH).
- Current/terminal role: "WORKING, gated" on the C4 R-MECH review final; no workers, no leases, $0 spend [HIST:
  STATUS_REPORT_2026-10-01.md]. RESPONSIBILITIES.md currency still reads 09-18 and STATUS.md 09-29; WORK_STATE.json
  (10-01 09:25Z) is the live record [IMPL].
- Relationships: built the BEE engine in parallel with Nestor's Z8 engine (NPE) and Archaeon's z80atlas, all from one
  directive; independent replicator of Nestor (REPL-01/02); instrument provider for Archaeon's C-001 ancestry campaign
  (E-003 BEE leg); audited by Harmonia (SAMPLE2/3/4, rules F7, F8), challenged by Artemis (R-26 #877, S3 #1005) and
  Odysseus (#748/#804); reviewer for Cosmos (C4).

## 2. Engine / system inventory

### 2.1 Worlds Kernel ("toolbox"), prometheus/toolbox/ -- built 09-18 .. 09-19, dormant since
- 112 tracked files, ~11,070 Python lines, stdlib-only except optional numpy and redis [IMPL]. First commit 4c0435544
  (09-18, "Phase 1 built and running ... Phase 2 StateDevice reference"); ~100 commits through the overnight loop;
  last commit on 2026-09-19 (atlas-bee scaffolding) [IMPL: git log; 102 commits touch the package].
- Purpose [INTENT]: declare an experiment once as data, lower it to any backend, execute with receipts, controls and
  replay.
- Entry points [IMPL]: prometheus.toolbox.ir.Experiment (+ ref(kind, **params)), Experiment.compile(target),
  backends/local.execute()/replay_file(), search.evolve(), admission.admit_*(), registry.Registry (fork()).
- Modules: capabilities.py (5 CORE ids + ~26 ext.* catalogue; negotiate() never raises), ir.py, backends/local.py
  (lowering to RunSpecs; the one episode loop), receipt.py (content-hashed chained receipts; forensic scan),
  series.py (observation series as receipt data/artifacts), registry.py + admission.py (ADMITTED/UNAVAILABLE with
  determinism, probe power and reference-agreement checks), state.py (InProcessStateDevice reference;
  RedisStateDevice exploratory), search.py (Truncation/MapElites/Pareto selectors over JSONL archive rows; evolve()
  with GEN_DONE/GEN_ABANDONED markers and resume), backends/sfe.py (partial lowering to archaeon.frontier
  experiment_spec.v1), backends/sfe_executor.py (kernel.run_ir executor for SFE runtime), backends/npe.py
  (UNAVAILABLE_INTERFACE; envelope pinned from nestor/sidequest-graphworld @ b22a09b19, nothing imported).
- Persistence: JSONL receipts files ("one file = one execution"), archive rows, content-addressed series artifacts.
- Execution model: synchronous lock-step episodes, one world per experiment, actions are int lists; optional batched
  path (ext.batch.v1) [IMPL; self-declared in WORLDS_KERNEL_DESIGN_v0.4 s4].

### 2.2 prometheus/atlas_bee/ -- 09-19
- Shim that re-instantiated six Atlas-indexed experiments (a1-a6) inside the toolbox; the only package that imports
  prometheus.toolbox [IMPL: git grep].

### 2.3 Z80 soup engine "BEE", prometheus/z80atlas/ -- 09-19 .. 09-30
- Built 98b2149a7 (2026-09-19 10:39 EDT; 2,496 lines, 16 tests); now ~4,364 lines across vm.py, world.py, grammar.py,
  tasks.py, runner.py, campaign.py, scheduler.py, controls.py, adjudication.py, observatory.py, geometry.py,
  grounding.py, robustness.py, coupling.py, coupling_campaign.py, coupling_supervisor.py, multiday_campaign.py,
  multiday_supervisor.py, tests/ [IMPL]. It imports nothing from prometheus.toolbox [IMPL per helper grep].
- Versions: physics v1 (72 h campaign, kept byte-replayable via tests/golden_v1.json built at 9bd0c39fb from the
  unmodified harness); v2 forensic repairs (f8ed38944, b2ee19847; gated by Config.physics); v3 coupling copy-resource
  ledger (c9bed96de); measurement-only 2.8x speedup with byte-identical output (515a675ae); register-world axis
  reg_world ZERO/CARRIED/RANDOM and reg_zero_p (35b2fde55, 60a926eee, 8a2390d82, 09-30) [IMPL].
- Consumers outside the seat [IMPL per helper grep]: archaeon/causal_lens/bee_tape_replay.py, archaeon tools_bee/,
  Artemis dispatch D004 script, ops/campaigns/C-001 (E-003). This, not the toolbox, is the engine other seats used.
- Scale: 72 h campaign 63,247 runs / 49,412 families / 592 CPU-h; grounding 12,130 runs; coupling 11,657 runs;
  multiday 4,160 runs at 20k ticks, 47.1 h active; superlinear cost (500/2000/5000 ticks = 59/641/3049 s,
  43/268/597 MB; 41f73bc0e) [HIST].

### 2.4 Analysis/forensic tooling
- forensics_2026-09-23 blind auditor (20 repro scripts), SPECIMEN_LEDGER.jsonl (2,188 rows); coupling_2026-09-24/tools
  (coupling_analysis.py, ops_accounting.py); e003 bee_tracer (823cbef1, frozen cfb57f67a; 32,827 births replayed
  bit-for-bit) [HIST/IMPL].

## 3. Architecture

### 3.1 Toolbox (code level)
- What an experiment is [IMPL: ir.py]: a dataclass with family, world, substrate, players, interventions, objective,
  observers, controls, transforms, selector, sweep (dotted path -> cartesian values), seed_policy, budget,
  required_capabilities, provenance, id. Components named by registry kind + params. compile(target) returns a
  Lowering (OK / TARGET_UNSUPPORTED / BLOCKED_MISSING_CAPABILITY / UNAVAILABLE_INTERFACE); digest() gives content
  identity (budget policy excluded).
- What a world is [IMPL: ref/]: a registered kind with reset(seed)/observe/step/events and declared replay class
  (BIT or SEMANTIC with quantum). See section 4 for the list.
- What a player is [IMPL]: a registered representation instance with act(obs) and adapt() (adapt returns None in
  every reference instance -- no lifetime learning). Representations: statemachine.v1 (Mealy table 4 states x 8
  observation buckets; bucket = fold(obs) % 8), statemachine.v2 (+1 workspace memory slot), statemachine.v3
  (+ executable-artifact ops), rewrite.v1 (6 rules, alphabet 8, tape 12), sequence.v1 (open-loop 16 actions),
  constant.v1 (negative control), proteus.tape.v0 (wrap of proteus.foundry.vm; "49/60 random Proteus players are
  silent").
- Substrate ("Player separate from Substrate") [IMPL]: flat.v1 (no workspace), kv.v1, kv_weather.v1 (seeded erase or
  sham), stream.v1, mailbox.v1 (shared stream; communication as a substrate door), artifact.v1 (shared executable
  shelf). Each workspace backed by one InProcessStateDevice (TTL, scopes, capacity, snapshot; model-based property
  tested).
- Episode loop [IMPL: backends/local.py]: reset(seed) -> [observe all -> act all -> step -> drain events -> observers]
  x horizon. Kernel wrappers: ObservationWrapper (delay, permute), ScheduleWrapper (mid-episode parameter changes).
- Search/mutation [IMPL]: evolve() above the kernel; TruncationSelector (e.g. keep=3, n=6), MapElitesSelector,
  ParetoSelector; transform.point_mutation.v1 changes one table cell or one action; fallback to shuffle then fresh
  random player if a transform does not accept the representation. Other transforms: shuffle, fresh, relabel.
- Selection/admission: admission is a component-level gate (contract, determinism, probe power, reference
  agreement), not organism selection [IMPL].
- Controls [IMPL: ref/controls.py]: replay, cheat, negative, positive, sham, scratch, permutation, ablation; each can
  return MET / NOT_MET / INDETERMINATE; docstring: expectations concern the INSTRUMENT, "never about the science".
- Observers/objectives [IMPL]: trace, descriptor, series (per-player); yield_net.v1, survival.v1 (step function),
  survival.v2, survival_per_player.v1, charge.v1, series_gain.v1, multi.v1 (selectors must rank by a component or
  refuse).
- Reproduction: none inside any toolbox world; populations change only through evolve() between episodes [IMPL;
  CODE-INFERRED as the decisive limit -- the 72 h endogenous-reproduction directive could not be expressed in the
  toolbox, which is why z80atlas was written as a separate package].
- Lineage/provenance: archive rows carry player manifests and spec hashes; receipts carry host and build hashes and a
  prev_receipt_id chain; behavioural fingerprint over 16 probes (can collapse distinct genomes: "11 distinct players
  behind one fingerprint", v0.4 s1) [IMPL/HIST].
- Design vs code disagreements [IMPL/CODE-INFERRED]: phases 3-4 never built (no ComputeDevice, no Box2D;
  ext.workspace.graph/tensor, ext.physics2d, ext.message_bus are catalogue strings only); IR CONTROL_KINDS lists
  compute_matched, storage_matched, transplant with no implementation; directive transforms (graft, sham graft,
  corrupt, edge edits, swap substrate, topology change) not built; directive selectors novelty/tournament/threshold
  not built; Redis "hot world state" acceptance never reached (M1 Redis needs auth, M2 has none; C123); NPE lowering
  unavailable, SFE lowering partial (M1 mismatch: frontier spec has no fixed-player mode). So the directive's
  falsifier F1 ("one nontrivial Experiment compiles to both SFE and NPE") was never met. Minor: README says 40 admitted
  components, STATUS 42/42; RESPONSIBILITIES still names design v0.2, README v0.4.

### 3.2 BEE / prometheus/z80atlas (code level)
- VM [IMPL, read directly: vm.py header]: "A small Z80-LIKE substrate. Not the Z80 ISA." One 256-byte address space
  per execution (every address mod 256): own tape [0, L), neighbour window [L, 2L) (the partner's tape; writes there
  are reproduction attempts), task input at 0xE0 (16 bytes, read-only; a write is the recorded
  "corrupt validation state" exploit), output at 0xF0. Registers A B C D (data), S T (pointers), Z/C flags. ~45
  defined single-byte opcodes with 0-1 operand bytes: loads, LD (S)/(T) indirect, LDI, LDIR (real Z80 semantics),
  COPYALL (only in the VM_COPY representation), ADD/SUB/XOR/AND/OR/INC/DEC/SHL/SHR/CP, JP/JZ/JNZ/JC absolute, JR and
  DJNZ relative, IN/OUT, register moves, SWAP, HALT 0xFF. No MUL. Undefined opcodes execute as NOP (~80% of byte
  values). A run is a pure function of (memory, entry, budget, inputs) and returns memory, outputs and a trace
  (writes, copy events, reads, halts). Step budget 256; LDIR 1 step per byte and with C = 0 sweeps 256 bytes (defect
  M2). Registers started at zero on every execution until the 09-30 reg_world axis.
- World [IMPL per helper read of world.py]: Config with cells (144 default; 256 in the 72 h campaign and grounding),
  ticks (200 default; 500 in campaign/grounding; 20k multiday), L = 64 (Z80_64, VM_COPY) or 32 (BYTECODE32).
  Topologies SOUP, GRID (torus, von Neumann), GRAPH (degree ~4), NICHES (four 2x2 blocks; RESERVOIR forces niche 0 to
  ECHO). Per tick: environment steps; each organism in seeded random order picks a partner and runs own tape +
  partner window + inputs; it is scored and pays energy; the reproduction physics interprets the window writes.
- Reproduction physics [IMPL]: EXTERNAL (manager breeds max(1, n/8) per tick with 4x mutation -- defect M3);
  ENDOGENOUS_COPY (all L window bytes written); ENDOGENOUS_PARTIAL (>= 1 byte, chimeras); OVERWRITE (target occupied,
  >= L/2 written); CONSTRUCTIVE (target empty, >= L/2 written); PAIR_EXECUTION (both tapes as one 2L program, then
  split; refused under v3 coupling).
- Energy/death [IMPL]: INIT 12; inflow 1 + 0.5 x score (pressure-dependent); cost 0.9 + 0.001 x steps; METABOLIC tape
  cost; death at energy <= 0 or age > 40. v3 adds a ledger-held COPY RESOURCE R invisible to the VM: base income per
  interaction, bonus when the first output is correct (ON) with control arms OFF / SHUFFLED / RANDOM_REWARD / YOKED /
  IRRELEVANT / DELAYED; a birth costs copy_cost x n_written; R clamped at 256; newborn R = 0; ledger balance asserted.
- Mutation [IMPL]: OPERAND (+/-1), OPCODE or BYTE (uniform), STRUCTURAL (insert/delete/dup) at LOW 0.002 / MED 0.008 /
  HIGH 0.03 per byte per tick on every living tape; one-point CROSSOVER under EXTERNAL only.
- Seeding [IMPL]: 1/8 minority of a half-filled grid. SEEDED_REPLICATOR = 8 bytes (LD S,0; LD T,L; LD C,L; LDIR;
  HALT); SEEDED_WITNESS (task witness); SEEDED_HYBRID (replicator + witness); init_tapes (transplanted minority).
- Tasks [IMPL: tasks.py]: CONST k, ECHO, INC, COND_ONE, COND_MULTI, SUM2 (one input byte except SUM2); scoring ATOMIC /
  INCREMENTAL (byte distance) / NEUTRAL; read gate ABR or FORCED; environment FIXED / SHIFT (every 60 ticks) / DRIFT /
  COEVOLVE / PER_NICHE / ENV_REPRO. verify_tape: the tape alone (empty window) must answer a fixed 16-input panel
  exactly.
- Grammar [IMPL]: 14 axes hashed (factors + constraints + violations source); UNAVAILABLE levels NESTOR_TAPE (M1-local)
  and PREDATOR_PREY_EXPLICIT; collision templates; one-axis CRITICAL_CONTROLS; 3-stage producer/consumer scheduler
  with promotion.
- Lineage/provenance [IMPL]: v2 adds window-write provenance (source, pc, opcode), SELF_REPLICATION predicate, sr_depth
  chains, first_self_replication with a seeded flag, glineage vs causal lineage, world_copies_under_endogenous.
  [CORRECTION, DEF-BEL-008] glineage is assigned by resemblance (label-as-content, world.py:562-569).
- Controls [IMPL: controls.py]: positive controls vm_executes, known_replicator_replicates, known_witness_solves,
  external_reproduction_evolves, endogenous_invades_when_seeded.
- Design vs code: the 72 h v1 observatory and the documented intent disagreed in at least 34 ways catalogued after the
  fact (section 7); v1 kept byte-replayable on purpose.

## 4. World capability audit

| world | state | spatial | observability | stochastic | agents | horizon | toy limit |
|---|---|---|---|---|---|---|---|
| toolbox world.integer.v1 (+ alt, batch) | 6 registers mod 2^16, per-player charge, pending-action queue | none | partial (folded obs) | seeded linear transitions, stochastic kick, regime flip | 1 default | 64 ticks default | tiny economy; "integer ladder has a delay-invariant optimum" (atlas-bee a5 self-note) |
| toolbox world.grid.v1 | ring of 8 nodes; pools (max 3), cells, owners | 1-D ring | partial | seeded | 2 | short | Ludus-shaped toy; tools, contested pools, stigmergic READ/WRITE cells |
| toolbox world.pendulum.v1 | 1-DOF damped driven pendulum per player | none | full | deterministic float | n | short | SEMANTIC replay at 1e-6 |
| wrapped wforge encounter / c6 composed | other seats' worlds | -- | -- | -- | 2 / 1 | -- | wforge "charge landscape is a sparse plateau" (a1 self-note); c6 single organism |
| BEE z80atlas | 144-256 tapes x 32-64 B; 256 B per execution | SOUP / GRID torus / GRAPH / NICHES | organism reads partner bytes and 16 input bytes; no sensing of energy or R | seeded mutation, inputs, partner choice | 144-256 organisms, pairwise interaction, overwrite competition | 200-20,000 ticks | fixed L, 256 B address space, six one-byte tasks; open-endedness bounded; superlinear cost with horizon |

Explicit statements:
- Every toolbox home-written world is a small toy: no 2-D space, no physics engine, no open-ended state growth, no
  in-world reproduction, no death-birth demography, no heritable variation inside the world. The toolbox is a
  well-instrumented executor/receipt system for toy worlds, not an emergence substrate [CODE-INFERRED].
- Task diversity in BEE is six one-byte transforms; environment change is scripted (shift/drift/coevolving constant);
  ecology is niches and migration; the world has no environment generation. The multiday campaign found the
  task ladder stalls at COND_ONE (0/960) [RESULT-UNVERIFIED].
- "World generation capability" (crawl brief): what exists is (a) a registry of hand-written world kinds with
  admission checks and sweepable params, (b) BEE's grammar over physics/topology/task/seeding levels, (c) mid-episode
  scheduled parameter changes. There is no procedural world generator beyond parameter sweeps [IMPL/CODE-INFERRED].

## 5. Organism capability audit

- Toolbox players: 4x8 Mealy tables (with one memory slot in v2/v3), a 6-rule rewrite system, a 16-step open-loop
  sequence, or wrapped Proteus tapes (mostly silent when random). No lifetime learning (adapt() returns None), no
  reproduction, no self-modification; communication only through mailbox/kv substrates; tool use only as the
  artifact shelf (create/invoke). Search is point mutation with tiny populations. A successful toolbox player could
  at best be a small reactive finite-state controller with one register of memory. Realistic chance at a nontrivial
  reasoning primitive: very low as built; the kernel was intended to host richer players, which were never added.
- BEE organisms: 32-64 byte self-modifiable programs in a 256-byte space, 6 registers, branching, block copy, reading
  a partner's bytes and 16 input bytes, writing the partner's tape (reproduction), registers zero-initialized per
  execution (until 09-30). No lifetime memory across executions in the default world (registers reset), so the only
  persistent state is the tape itself. Reproduction is cheap by construction: SR access depends on LDIR with C = 0
  sweeping 256 bytes plus an ~80% NOP slide; a random tape is a replicator with p about 3e-5 (grounding P8 ablation:
  LDIR off / cost x4 / undefined->HALT abolishes SR, 8/300 -> 0/300) [RESULT-UNVERIFIED]. Task competence and copying
  were decoupled until v3; under v3 the payment maintains SEEDED task code but de novo acquisition reaches only ECHO
  and INC, never COND_ONE, never from random soup (0/3,200) [RESULT-UNVERIFIED]. Fighting chance: real for copying
  (engineered basin), weak for task computation coupled to reproduction within the explored horizons.

## 6. Search and pressure mechanism

- Toolbox: external selection (truncation, MAP-Elites, Pareto) on point-mutated tables over seeds; tiny populations;
  descriptor saturation collapsed a MAP-Elites archive to 4 cells until a calibratable descriptor v2 (C27) [HIST].
- BEE: per-tick background mutation on every tape; reproduction through window writes (endogenous) or manager breeding
  (external); energy economy; v3 copy-resource payment for correct output; niches, migration, reservoir, coevolving
  constant. Collapse modes recorded: POLLINATION/RESERVOIR migration spawning hidden world copies under endogenous
  physics (median 888 per run; defect P1); seeded-hybrid takeover (579/600 ARCH flags); payment of half-correct tapes
  (non-competent-earner share 1.0) as the candidate reason for the COND_ONE null [HIST/RESULT-UNVERIFIED].

## 7. Measurement / ruler stack

### Toolbox
- Trace-hash replay (BIT / SEMANTIC with quantum), behavioural 16-probe fingerprint + spec hash, control expectations
  (instrument-level only), admission probe power (C70: a wrong twin had passed on an action-blind probe; repaired),
  POWER_REGISTER_2026-09-19.md, mutation ledger (20 -> 37 -> 62 -> 85/85 -> 93 mutants caught).
- [CORRECTION, self, v0.4 s2-3] "37/37 caught" was true but 18 mutants could not have been reported otherwise (an
  anchor-drift test failed for every applied mutant); honest "since C95"; a stale-.pyc false RED of 47 tests (C122).
- [CORRECTION, self] the batched-execution throughput premise was falsified: 6.0 us/env-tick scalar vs 8.6 us batched
  (0.70x); end to end 0.93-0.95x (science/BATCH_THROUGHPUT_2026-09-19.json).
- Blind spots: no compute- or storage-matched or transplant controls; ablation is workspace-only (cannot ablate hidden
  player state; atlas-bee a6 UNREPRESENTABLE); all evidence within toy worlds.

### BEE v1 (72 h) rulers -- retired for adjudication after 09-23
- Mechanical triggers with frozen thresholds (replication_rate 0.05, hifi 0.90, solvers = score_ema >= 0.85,
  compression 0.70) and five "high-value" flag classes (ENDO_NOT_EXT, BENEFICIAL_DENSITY, REPRODUCTIVE_ARCHITECTURE,
  INCR_NOT_ATOMIC, RESERVOIR_CROSSED_MOAT).
- 34-row ISSUE_AND_REPAIR_LEDGER [CORRECTION]: C1 tail metrics read pre-extinction windows (616 extinct runs fire
  task_score); C2 solver = score_ema >= 0.85 (INCREMENTAL accepts answers ~19 off); C3 INCR vs ATOMIC compares unlike
  rulers; C4 RESERVOIR easy ECHO niche plus a mis-seeded witness (6/7 moat flags); C5 moat trigger fires in 48% of
  runs; C6 beneficial density unpaired (the identity "mutant" scores better 60% of the time); C7 ARCH flag = seeded
  hybrid takeover + max-PC span artifact; C8 1-byte capture births counted as hifi replication; C9 interventions
  counted as spontaneous (42); M1 fidelity measured post-execution (self-smear 1.0); M2 bare LDIR with C=0 sweeps 256
  bytes and counts as a full copy; M3 EXTERNAL offspring get 4x mutation; M4 any() over unequal run sets; M5 family
  id ignores init_tapes; M6 late matched controls mis-seeded (5,156/6,859); M7 gated skippers never age; M8 promotion
  near-universal; M9 geometry on end-of-run niche-0 task; P1 hidden world copies; H1 un-relocated seeded hybrid (its
  absolute jumps were not relocated; it answered 8/16 of the panel); m1-m6 minor.

### BEE v2/v3 rulers
- SELF_REPLICATION predicate: >= 0.9L window bytes written by LDI/LDIR/COPYALL from own-tape sources, >= 90% executed
  from own code, writer material, fidelity >= 0.9 to pre- and post-execution tape [IMPL].
- Blind spots [CORRECTION / UNKNOWN]: "own code" is LOCATION-defined (pc < L), not material-defined; Atlas's digest
  records r038751 with 27,083 of 28,163 location-foreign births that are own material (Archaeon #741); no SR recount
  by material found in git. Competent-SR endpoint sr_depth > 0 is a birth event, not an isolated capability
  (DEF-BEL-003; Odysseus #748/#804) -- inflates control arms. Heritability (r_cc - r_nc) measures copy fidelity
  (F6); retention r_cc at ceiling (F7); enrichment ratio saturates (F8). Transplant slots take 0 world-RNG draws, so
  transplant-vs-control same-seed runs are not CRN-paired (DEF-BEL-009). geometry zero padding inflates `replicates`
  (DEF-BEL-010). Grounding seed formula has no cell term (pseudo-replication, DEF-BEL-005). md_analysis "holds" not
  conditioned on instrument_ok (DEF-BEL-002). Founder-snapshot FM ruler cannot separate descent-with-turnover from
  de novo origin (Harmonia F8). Reachability: REPL-01 K3 and REPL-02 dominance readouts never shown able to return the
  non-null outcome (REPL-02 positive control 0/50).
- Reproducibility: coupling/multiday results.jsonl, the 72 h workdir, grounding results and atlas-bee receipts are
  host-local on M2, recorded by sha256 only; re-deriving MD_RESULTS ~561 CPU-h [HIST].

## 8. Experiment inventory (campaigns)

### 8.1 TK-NIGHT: Worlds Kernel build + overnight TDD/playtest loop (C1-C150)
- 09-18 night .. 09-19 ~09:49Z. Paths: prometheus/toolbox/, roles/Bellerophon/OVERNIGHT_LEDGER_2026-09-19.md,
  OVERNIGHT_REPORT_2026-09-19.txt, WORLDS_KERNEL_DESIGN_v0.3/v0.4.md; commits 4c0435544 .. cfc4542f3.
- Question: does the kernel work as an instrument (receipts, replay, controls, resume, fuzz, mutants)?
- Reference experiments EXP-001 (frozen semantic fixture), EXP-002 (432 runs, 6 substrates x 2 regimes; controls 5/5
  MET 72/72), playtests A-H (pt_b and pt_f have no committed file).
- Reported: suite 1,421 passed / 6 skipped (Redis); mutation ledger 85/85 caught; 42/42 components admitted; 300-seed
  fuzz 0 crashes; cross-platform replay 87/87 trace hashes identical (Windows py3.14 vs WSL py3.12).
- RESPONSIBILITIES s4: "EXP-00n reference experiments prove the kernel and claim nothing about worlds" [INTENT].
- Label: REPORTED POSITIVE (engineering), with self-corrections (powerless mutants; batching falsified).

### 8.2 AB: Atlas->BEE pilot a1-a6 (toolbox)
- 09-19 ~12:35Z .. 13:42Z (~1 h for six adaptations). Paths: roles/Bellerophon/atlas_bee/ (PREREG_a1..a6,
  RESULT_a1..a6, SELECTION_FROZEN, REVIEW_PACKET_2026-09-19.md 933ee9f02), prometheus/atlas_bee/.
- Question: do Atlas-indexed results survive re-instantiation in a different ecology?
- Reported: a1 E10 closed-vs-open INVERTED (closed organism overfit: train 318.6 -> held-out -0.4); a2 e05 CHANGED
  (subadditive); a3 e01 CHANGED (recurrence control inverts); a4 C3-SFE-10 ABSENT (offspring cap unrepresentable);
  a5 C2-SFE-06 ABSENT (delay-invariant optimum); a6 e07 PRESERVED (P1 refuses). Recommendation "ADMIT BEE as a third
  ecosystem".
- Reinterpretation: none found by any other seat; the packet itself concedes a1 and a5 failed because of the toy
  world; run counts are not in the RESULT files and receipts stayed in the run workroot [UNKNOWN].
- Label: UNKNOWN (unreviewed).

### 8.3 BEE-72H: Bellerophon's Z80 x Atlas 72 h campaign
- 09-19 14:39Z .. 09-22 14:38Z. Code 98b2149a7, 16fc6c2a2; workdir C:/Users/James/z80atlas_campaign_2026-09-19 (not
  in git).
- Question: which reproduction-physics x topology x pressure combinations open paths to computations inaccessible
  under external reproduction?
- Scale: 63,247 runs, 49,412 families, 592 CPU-h, 0 failures; 1,629 high-value flags.
- Reported: only operational counts committed; live transcript snapshots (446 flags at 44.6 h; "spontaneous
  replication fires 276") were never committed [HIST].
- Reinterpretation (09-23 forensics): ENDO_NOT_EXT FALSIFIED (reverse holds 1,554 vs 443 exposure-matched); beneficial
  density INSTRUMENT FAILURE; architecture CONFOUNDED (seeded hybrid); INCR_NOT_ATOMIC DETECTOR_ONLY; RESERVOIR
  FALSIFIED (ECHO solvers in easy niche 0); the "276" was a trigger count; POLLINATION topology effect = P1.
- Label: LATER OVERTURNED (flags); INSTRUMENT FAILURE (v1 rulers).

### 8.4 FOR: Post-campaign forensics (09-23)
- Path: roles/Bellerophon/forensics_2026-09-23/POST_CAMPAIGN_FORENSICS.md, ISSUE_AND_REPAIR_LEDGER.md,
  SPECIMEN_LEDGER.jsonl; branch merged.
- Reported: five flag classes collapse; spontaneous own-code SR survives: ~1,076 origins (7.2%, CI 4.8-9.6%) through
  ~3 routes (LDIR from S=0 57%, COPYALL 13%, LDI); replicator lineages carry no task computation (beneficial density
  0.0001); "SUSTAINED 89.6%" of trigger-selected origins.
- Reinterpretation: exploratory by its own statement; sustained share later shown selection-biased (grounding 39.4%
  unselected, later 25-29%).
- Label: MIXED (mostly REPORTED NEGATIVE for prior claims).

### 8.5 GRD: Grounding round under physics v2 (09-23)
- Prereg frozen a1b066309; 12,130/12,130 runs; controls 8/8; replay 606/606. Paths: GROUNDING_PREREG.md,
  GROUNDING_REPORT.md, ERRATA_2026-09-29.md (2159c2e06, 280f468b0).
- Reported: SR CONFIRMED_CAUSAL (needs LDIR and the NOP slide); EXTERNAL beats ENDOGENOUS causally on task pairs (178
  vs 2); P1 causes the POLLINATION effect (extinction 0/150 v1 vs 148/150 v2); task causally inert under IMPLICIT;
  verdict "instrument ready, physics not ready": no pathway by which computation affects reproduction.
- [CORRECTION] ERRATA 09-29: "160/160 first SR BUILT_BY_COPY" -> 103/160 (DEF-BEL-001; Artemis R-26 #877); origins
  pseudo-replicated (160 origins / 83 seeds / 45 exact duplicates); sustained 39.4% -> 28.7% (unique events) / 25.3%
  (per seed); "no task dependence" -> NOT_ADJUDICABLE (Artemis S3 #1005). No gate flips.
- Label: REPORTED POSITIVE (SR access) + REPORTED NEGATIVE (coupling), partially CORRECTED.

### 8.6 CPL: Coupling campaign, physics v3 (09-24 .. 09-25)
- Prereg c9bed96de; Amendment 1 6607b3cb5 (operational, after an OOM reaper killed the driver, F4); merged cc63d7e8a.
  Paths: coupling_2026-09-24/.
- Question: does correct computation, paid as a non-heritable copy resource, raise reproduction and select for task
  code?
- Arms: ON, OFF, SHUFFLED, RANDOM_REWARD, YOKED, IRRELEVANT, DELAYED, NOCOMP, NOCOPY, RANDOUT; K16 and K40. Scale
  11,657 runs, 500 ticks; replay 341/341.
- Reported: READY_FOR_MULTIDAY; P1 40/40; P2 149 vs 0; P3 0.9987; P4 67 vs 1 hold; P5 fails at ceiling; P6 4/60 vs
  0/60 ns; acquisition only ECHO K40 29/150 vs 6/150; random worlds 0/3,200.
- Reinterpretation (self, report s5): the core effect is MAINTENANCE of seeded code; P3 is copy fidelity (F6); P5
  ceiling (F7); DEF-BEL-003 SR label = birth event inflates control counts.
- Label: MIXED (REPORTED POSITIVE for maintenance).

### 8.7 MD: Multi-day campaign E-BEL-MD (09-26 16:40Z .. 09-28 15:48Z)
- Freeze 12ce26e23, code a3086cece; merged e51c8dec6 after two Fabric reviews (MERGE_WITH_FIXES); fixes 1c6bca786.
  Paths: multiday_2026-09-26/ (MULTIDAY_PREREG.md, MULTIDAY_CAMPAIGN_REPORT.md, receipts/MD_RESULTS.json).
- Lanes LADDER1 (1,280), COPIER (960), REPAIR (960), LADDER2 (960); 4,160 runs at 20k ticks, 47.1 h active; replay
  114/114.
- Reported: Q1_LADDER1 HOLDS 58/320 vs 0-1; Q1_COPIER HOLDS 36/240 vs 2-4; Q1_LADDER2 FAILS 0/960; Q2 HOLDS small
  (+0.0115); Q3 FAILS the baseline clause (4.7% < 6.7%).
- Reinterpretation: post-hoc label audit -- ON 108/109 real self-copiers, 6/9 control acquisitions are non-copying
  label carriers; Q2 compares possibly different lineages, so "protection" is suggested not established; label-audit
  counts not recomputable from git.
- Label: MIXED.

### 8.8 E003: E-003 BEE leg for Archaeon's C-001 ancestry campaign (09-29)
- Tracer 823cbef1 frozen cfb57f67a; production 72ed6e160; merged 0629fd4f0 as "VALIDATED (A and B)". 32,827 births
  replayed bit-for-bit; 123,210 interactions; fixtures 28/28.
- [CORRECTION] Harmonia SAMPLE2 item H: NOT_SUPPORTED as labelled -- amendment C4.2 removed the P2 -> ALTERED route 17
  minutes after the owner's dry run on the same deterministic data, undisclosed; merge-review prompts told reviewers
  to accept it. ERRATA_2026-09-30: confirmatory = ALTERED; verdict of record OPEN with the operator. Harmonia
  STANDING_RULES F7 was set on this case.
- Label: LATER OVERTURNED (label); outcome UNKNOWN pending operator.

### 8.9 REPL-01 / REPL-02: independent BEE rebuild of Nestor's C-A3-INTERNALIZE (09-30)
- REPL-01 freeze 74f72e805, seal 3b2e11a3e, result 279927367; ERRATA_REPL01 6879b2236; merged c776cea6a. Arms ZERO /
  P90 / P75 register worlds, 100 runs each (plain CARRIED killed founders: 0/24 persist vs ZERO 10/24 in pilot).
  Reported: DISAPPEARS (K3); K1 93/200 vs 18/100 (p 6.6e-7). Commit subject: "scaffold-dependent emergence of
  state-freedom in BEE is real". [CORRECTION] errata after two adversarial reviews: K3 had no route to SURVIVES (FM ~0.01
  by tick 500 in all arms); "kill is real", "chance-level", "BEE-specific" withdrawn; blinding honour-system (the X-MAT
  verdict merged into the branch 67 min before the freeze); descent UNRESOLVED; Harmonia SAMPLE4 J -> SUPPORTED_WITH_
  DEFECTS; rule F8. The engine change 35b2fde55 reached main without pre-merge review (self-disclosed 91e88e8df,
  confirmed by Harmonia SAMPLE3).
- REPL-02 freeze 4d1a7c885, result 64d8d2d3f: RESIDUE_NOT_REPLICATED (ABSENT): BASE 1/50 vs 0/50; positive control
  RANDOM 0/50 -- readout reachability undemonstrated; post hoc REPL-01 K1 mostly transient (state-free at tick 2000:
  P90 8/100, P75 17/100, ZERO 4/100).
- Label: INCONCLUSIVE (REPL-01 descent); REPORTED NEGATIVE/NULL with power caveat (REPL-02).

### 8.10 R-MECH: review of Cosmos C4 DESIGN v0.2 (09-30 .. gated)
- Interim 164df3cdd on origin/bellerophon/c4-rmech-2026-09-30 (the only unmerged Bellerophon commit). Findings F1/F2
  BLOCKING (a zero-parameter law reading a guard-compliant coordinate restates Certificate A; Certificate B
  reconstructs A's contrast 47/48), F3-F5 REPAIR, F6 NOTE. Final gated on Cosmos.
- Label: INCONCLUSIVE (interim).

### 8.11 FP-001: Fabric reproducibility probe (09-29, MWO-0003)
- probes/FP-001_RESULT.json (756bd0366): frozen multiday plan sha 1ab324d5 rebuilt on 2 replicas. Label: REPORTED
  POSITIVE (ops).

## 9. False-positive / false-negative archaeology

### 9.1 72 h flags -> forensics
- Claim: 09-19..22 live status: 1,629 high-value flags; "spontaneous replication fires 276"; POLLINATION topology
  concentration; REPRODUCTIVE_ARCHITECTURE_RESPONDED_TO_TASK (600), BENEFICIAL_DENSITY (493).
- Evidence: v1 triggers.
- Challenge: 09-23 forensics directive; blind auditor; traced replay with byte provenance.
- Correction: 34-row ledger (section 7); H1 un-relocated hybrid carried 303/493 BD flags; C6 unpaired identity null
  scored "better" 60%; P1 hidden world copies explain POLLINATION; late "fresh seed verification" would have confirmed
  an instrument failure (the BD flag reproduced 58% under fresh seeds because the instrument is biased).
- Status: LATER OVERTURNED; own-code SR survives on traced provenance.

### 9.2 Grounding numbers -> errata
- 160/160 BUILT_BY_COPY -> 103/160; sustained 39.4% -> 28.7% / 25.3%; "no task dependence" -> NOT_ADJUDICABLE.
  Sources: Artemis R-26 #877, S3 #1005; ERRATA_2026-09-29.md. Status: CORRECTED, no gate flips.

### 9.3 E-003 "VALIDATED"
- 09-29 merged as VALIDATED; 09-30 Harmonia found a post-exposure amendment removed the ALTERED route; errata relabel
  ALTERED; OPEN for operator. Lesson recorded in calibration LEDGER: "Exposure is a property of the DATA. Any seat's
  dry run on the same deterministic data counts as exposure."

### 9.4 REPL-01 "real" -> UNRESOLVED
- 09-30 commit subject asserted reality of scaffold-dependent emergence; same day errata withdrew it; K3 could not
  return SURVIVES; blinding was honour-system. Lesson: "Every kill test needs a real-data planted positive that shows
  it can return SURVIVES."

### 9.5 Toolbox self-corrections
- Mutant ledger powerless for 18 mutants until C95; "batched = NPE-class throughput" falsified (0.70x); STATUS once
  called archaeon/z80atlas "Nestor's own build", corrected to Archaeon's (c7610ea19).

### 9.6 False negatives / capability nulls
- REPL-01 K3 DISAPPEARS: ruler could not return SURVIVES -> descent UNRESOLVED, not absent.
- REPL-02 ABSENT: positive control failed.
- Coupling P5 FAIL: ceiling; P6 underpowered (60 seeds for an effect ~7%).
- Multiday LADDER2 0/960: payoff likely rewards half-correct tapes; edit distance to COND_ONE never measured.
- Grounding REPRODUCTIVE_ARCHITECTURE FALSIFIED "at this scale" (0/100, bound 3.7%) -- scale-limited.
- Atlas-bee a4/a5 ABSENT: unrepresentable mechanism or degenerate toy optimum -- not evidence against the sources.
- Cross-engine (Atlas A1): "random Z80 tapes do not copy" (Archaeon census, no copy op) vs "unmodified random tapes
  replicate" (BEE, LDIR + NOP slide) -- an ISA difference, not a contradiction [HIST: ATLAS_CONTRADICTIONS A1].

## 10. Research outputs

- TOOLBOX_RESEARCH_2026-09-18.md (prior-art tool survey); TOOLBOX_DESIGN_v0.1.md; WORLDS_KERNEL_DESIGN_v0.2/v0.3/v0.4.md
  (v0.4 = design of record: what runs, what failed, assumptions); ABI_DIFF.md.
- OVERNIGHT_REPORT_2026-09-19.txt and OVERNIGHT_LEDGER_2026-09-19.md (150-cycle TDD record).
- science/POWER_REGISTER_2026-09-19.md, MUTATION_LEDGER_2026-09-19.json, BATCH_THROUGHPUT_2026-09-19.json.
- atlas_bee/REVIEW_PACKET_2026-09-19.md, ATLAS_EXTENSION_PROPOSAL.md, PHASE1_CORRESPONDENCE.md.
- forensics_2026-09-23/POST_CAMPAIGN_FORENSICS.md, ISSUE_AND_REPAIR_LEDGER.md, GROUNDING_PREREG.md, GROUNDING_REPORT.md,
  ERRATA_2026-09-29.md.
- coupling_2026-09-24/COUPLING_CAMPAIGN_PREREG.md, COUPLING_CAMPAIGN_REPORT.md, COUPLING_FAILURE_LEDGER.md (F1-F11),
  COUPLING_IMPLEMENTATION_AUDIT.md, REVIEW_PACKET_COUPLING_2026-09-25.md, NEXT_MULTIDAY_CAMPAIGN.md,
  RESUME_AFTER_RESET.md.
- multiday_2026-09-26/MULTIDAY_PREREG.md, MULTIDAY_CAMPAIGN_REPORT.md.
- e003_2026-09-29/E003_BEE_RESULT.md, ERRATA_2026-09-30.md.
- repl_2026-09-30/PREREG.md, RESULT.md, ERRATA_REPL01_2026-09-30.md, RESULT_02.md.
- STATUS_REPORT_2026-10-01.md; R-MECH interim (unmerged branch).

## 11. Journals, TODOs, pivots, abandoned branches

- Journal: roles/Bellerophon/journal/ (dated entries 09-18 ..); calibration/LEDGER.md records self-identified wrong
  calls (09-18 .. 09-30), including the exposure, blind-lane, planted-positive and state-file lessons [IMPL listing;
  contents via helper].
- BACKLOG_H0H5.md: open kernel items BELL-24 (graft via Proteus lineage), BELL-26 (Redis acceptance), BELL-30..33
  (compute devices, Box2D) [HIST].
- Pivots and why:
  1. 09-18 toolbox -> Worlds Kernel (operator directive: backend-neutral kernel).
  2. 09-19 kernel -> Z8 substrate science: operator forwarded Nestor's 72 h directive; the toolbox could not express
     endogenous reproduction, so z80atlas was written from scratch; the toolbox received no further commits.
  3. 09-23 forensics directive: the 72 h flags had to be adjudicated; v2 physics added behind a gate.
  4. 09-24/25 grounding verdict "physics not ready" (no computation -> reproduction pathway) -> v3 coupling; s7
     addendum lets the seat run its own science.
  5. 09-26 multiday by operator ruling; 09-28 MWO fleet model; 09-29 instrument work for Archaeon (E-003); 09-30
     replication of Nestor; 09-30/10-01 Cosmos review.
- Abandoned: kernel phases 3-4 (compute devices, Box2D), Redis hot state, NPE lowering, SFE bridge packet to Daedalus
  (drafts not posted), E-BEL-BUILD-01 (generalise BEE controls into a builder experiment; not started under CWO
  no-scope-growth).
- Branches: origin/bellerophon/{coupling-campaign, e003-bee-ancestry, multiday-campaign, mwo-0001,
  post-campaign-forensics, repl-internalize} all merged (0 unmerged commits); c4-rmech has 1 unmerged commit held by
  operator ruling.
- Open defects: DEF-BEL-008 (glineage resemblance label), DEF-BEL-009 (non-CRN transplant pairing), DEF-BEL-010
  (geometry zero padding); open operator decision E003-BEE-LABEL.

## 12. Lens inventory

### Lens B-1: Worlds Kernel as an experiment-declaration and receipt instrument
- Substrate observed: any registered world x player x substrate combination expressed as an IR.
- Organisms: small finite-state, rewrite, sequence players; wrapped Proteus tapes.
- Worlds: integer, grid ring, pendulum; wraps of wforge and campaign-6.
- Pressures: external selection between episodes (truncation, MAP-Elites, Pareto); interventions and schedules.
- Phenomenon family: memory/substrate use, communication via substrates, transfer via world sweeps, control-arm
  causal attribution.
- Resolving mechanism: chained receipts, BIT/SEMANTIC replay, instrument-level controls with power register,
  admission with reference agreement, mutation ledger.
- Resolution ceiling: set by the toy worlds and fixed tiny players; no in-world reproduction; lock-step only.
- Noise sources: fingerprint collapse of distinct genomes; descriptor saturation; Python-only throughput.
- Reusable: the IR/lowering/receipt/replay/admission/mutation-ledger machinery and the discipline that a control
  expectation is about the instrument; cross-platform replay evidence.
- Toy-grade: every home-written world and player.
- Unknown: whether the IR can express a world with endogenous reproduction without core changes (not attempted; the
  72 h work bypassed it).

### Lens B-2: BEE Z80 soup (prometheus/z80atlas)
- Substrate: 32-64 byte self-modifiable tapes in a 256-byte address space with LDIR/LDI/COPYALL and a partner window.
- Worlds: 144-256 cells, SOUP/GRID/GRAPH/NICHES, reproduction physics grammar, energy, v3 copy resource, reg_world axis.
- Pressures: energy economy, payment for correct output (v3), niches/migration.
- Phenomenon family: spontaneous self-replication; coupling of computation to reproduction; maintenance vs acquisition
  of task code; scaffold dependence of initialization.
- Resolving mechanism: SELF_REPLICATION provenance predicate, verify_tape exact panel, v3 arm battery (ON vs YOKED /
  SHUFFLED / RANDOM_REWARD ...), golden replay, label audits, external tracer (E-003).
- Ceiling: replication is an engineered basin (LDIR C=0 sweep + NOP slide); six one-byte tasks; COND_ONE never
  acquired; location-defined "own code"; birth-event competence label; host-local raw data.
- Noise sources: hidden world copies (P1, repaired in v2), seeded takeovers, pseudo-replicated seeds, non-CRN
  transplant pairing, resemblance lineage labels.
- Reusable: v1-golden + gated physics versions discipline; v3 copy-resource ledger with a rich negative-arm battery;
  register-world axis shared conceptually with NPE.
- Toy-grade: task set and world size.
- Unknown: material-defined SR recount; whether the multiday acquisition holds with label-carrier correction
  re-derived from durable data.

### Lens B-3: Cross-engine replication harness (REPL-01/02, E-003)
- Substrate: BEE used as an independent second engine to test claims from NPE (Nestor) and Archaeon.
- Phenomenon: portability of mechanism claims across ISAs.
- Ceiling: kill tests without demonstrated reachability; blinding by honour system; exposure via shared deterministic
  data.
- Reusable: the pattern itself and the recorded lessons (planted positive must be able to return SURVIVES).

## Open questions / unknowns

- Contents of the 72 h CAMPAIGN_PACKET.md and the live flag splits (host-local, transcript only).
- Atlas-BEE a1-a6 run counts and whether workroot receipts still exist.
- Whether any SR recount by MATERIAL (rather than pc < L location) was ever done.
- Multiday label-audit counts depend on host-local results.jsonl (129 MB); no durable archive.
- E-003 verdict of record (ALTERED vs VALIDATED-as-amended), pending operator.
- Quantitative impact of DEF-BEL-009 on historical transplant-vs-control contrasts (grounding HIST lane, coupling
  Lane J).
- C4 R-MECH final verdict (gated on Cosmos).
- Toolbox backend neutrality untested beyond local + partial SFE (Redis and NPE never exercised).
- Atlas disagreements recorded: atlas/registry.json lists "bellerophon.toolbox" as LIVE (home_host null) though it is
  dormant since 09-19 with no external consumers, and has no row for prometheus/z80atlas, the engine actually used;
  Atlas's classifier treats "Bellerophon overnight C<n>" kernel TDD commits as indexable runs; the cross-engine
  synthesis line "contingent earning selects FOR task code (Bellerophon, strongest surviving mechanism)" drops
  Bellerophon's own qualifier (maintenance of SEEDED code; acquisition only ECHO/INC; COND_ONE 0/960), which the
  digest retains; "CONFIRMED_CAUSAL" SR is quoted without the location-vs-material ruler caveat.
- The C:/Users/James host-account question raised by Achilles is unverified.
- Selective-irreversibility blind lane: programs/selective_irreversibility/probes/blind_probe_v1.py (Cyclops, 3de747dd8,
  09-25) registers Bellerophon's paths (roles/Bellerophon, prometheus/z80atlas, prometheus/toolbox, prometheus/atlas_bee
  and the frozen coupling workdir) as a BLIND lane, and its commit records an INCIDENT ("Cyclops #585 exposed the
  Bellerophon seat (rows + frozen analysis stay blind)"). This is a path registry, not a code consumer. How far that
  exposure bears on later Bellerophon blinding (REPL-01 was honour-system blind) was not traced [UNKNOWN].
