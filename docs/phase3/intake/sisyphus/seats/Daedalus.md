# Daedalus -- forensic dossier (Sisyphus crawl)

- Seat: Daedalus ("Maintainer of the Serendipity Foundry Engine")
- Crawl date: 2026-10-01
- Base SHA of worktree: 19299e06b (F:/Prometheus-worktrees/sisyphus-base-role, origin/main)
- Crawler: Sisyphus worker (seats Daedalus + Apollo)

## Coverage statement

READ (code): SerendipityFoundry/SerendipityFoundryEngine/sfe/ in full for
executors.py and canary.py; runtime.py method index plus the observation /
evidence-class / sharing-policy / family sections; serve.py flags; store.py
schema version; deploy/ inventory and the M2 launcher;
SerendipityFoundry/worldfoundry/wforge/{world,genome,probes}.py (heads and the
expansion function). Off-repo, read-only: F:/SerendipityD (the D-9/D-13
Foundry, the lineage ancestor) -- README, SEARCH_PHYSICS.md,
ECOLOGY_REPAIR_VERDICT.md, foundry/search/{objective,map_elites}.py,
foundry/engines/gp/stackvm/vm.py header, d9/ directory listing, git log.

READ (prose/history): roles/Daedalus/ (CHARTER, GENESIS, RESPONSIBILITIES,
STATUS, SESSION_STATE genesis, TODO D6 section and headings, BACKLOG_H0H5
head, INBOX_HERAKLES_BITSTRING_EXECUTOR, journals 09-11/12/16/17 heads);
SerendipityFoundryEngine/docs/{SERENDIPITY_FOUNDRY_GEN2_ARCHITECTURE,
SERENDIPITY_FOUNDRY_GEN2_CANARY}.md, campaign_6/SFE_C6_OBSERVATORY_REVIEW;
SerendipityFoundry/forensics/SFE_WOW0_FORENSIC_SURVEY.md (s1-s7);
wow/WOW_ARCHAEOLOGY_REVIEW_PACKET.txt (s0-s1, A6-A8); commit bodies of
17f2b8d3a, 1ac333f43, 6efa4f88d, 5ceeb5b9b, 85c74304c, a6f86c3d3, 5821ee076,
0496968b1, ef504133f; D6/VERDICT.json, D6A/REPORT_D6A.md head, D7/README.md
head, D8/SESSION.md head, D10/D10_INDEX.md, D10phase2/PHASE2_REPORT.md head;
full git log of SerendipityFoundry/ and roles/Daedalus/ (98 engine commits,
18 client commits); comms subject lines naming Daedalus (#414-#563);
roles/Artemis/threads/sfe_retrospective/REPORT.md (used as a locator and
cross-checked); Atlas grep (catalog/ECOSYSTEMS.jsonl, SOURCES.md, STATUS.md,
inference_harvest_2026-09-30/*); roles/Harmonia/contracts/conformance_check.py
header.

NOT READ, and why: the SFE ledgers themselves (M1 eng_8a37a5d3 and M2
eng_906356f7 live off-repo on host disks; opening SQLite is out of scope and
they are not on this host's worktree); the bulk of deploy/ receipts (154
files; sampled by name and by commit message only); MHC prodledger code,
stackvm_admission and selection_boundary code (read through their commit
bodies and packets only); D7/D8/D10 code; the 702-line TODO.md beyond the D6
section; the full point-release receipt set; the Vivarium / Archaeon /
Harmonia side of the H0-H5 and Campaign 1-6 science (those are other seats'
dossiers). Comms bodies for #881 (Artemis -> Daedalus) did not render through
`comms show`; only its subject is known.

-----------------------------------------------------------------------

## 1. Identity and purpose

- Canonical name: Daedalus. Seat created 2026-09-01 by commit d332658cf
  ("Daedalus: Serendipity Foundry Engine + Client, role, and multi-
  experimenter isolation"). [HIST]
- Historical aliases: "Serendipity D" / "D-9 Serendipity Foundry" session;
  the WOW-0 forensic survey header identifies the investigator as "Daedalus
  SFE (M1 maintainer session; originated as Serendipity D)"
  (SerendipityFoundry/forensics/SFE_WOW0_FORENSIC_SURVEY.md s0, s2). The
  pre-split engine package was `gen2` inside F:/SerendipityD (commit dd006cb
  there), renamed `sfe` on relocation. [HIST]
- Original charter (roles/Daedalus/CHARTER.md, 2026-09-01): "the craftsman
  who maintains the machine, not the one who flies with it". Standing order
  1: "The instrument serves the experiment; it never shapes it ... never let
  the Engine become the fitness landscape." Two myths as orders: isolation
  that holds (Labyrinth) and never shipping an unverified guarantee (Icarus).
  [INTENT]
- Later charter changes: base-role inheritance banner added 2026-09-11
  (D-23); no rewrite of mission. A de facto pivot happened 2026-09-02/03, when
  the same seat produced science-design and statistics packets (Incubator
  World-0, World Foundry v0 + wforge, Microstructure Hadron Collider, WOW
  archaeology, stackvm admission language, selection boundary) that go well
  beyond "maintainer" scope. These are authored "Daedalus" in the packets
  (e.g. wow/WOW_ARCHAEOLOGY_REVIEW_PACKET.txt header "Author : Daedalus,
  maintainer of the Serendipity Foundry Engine"). From 2026-09-04 onward the
  seat returned to pure service engineering. [HIST]
- Role pivots: (a) 08-27..08-30 (pre-seat) experiment-runner lineage D-6A,
  D-7, D-8, D-10, D-9/D-12/D-13 Foundry; (b) 09-01 engine maintainer; (c)
  09-02..09-03 incubator/statistics designer; (d) 09-04..09-15 service owner
  for Harmonia, Vivarium, Archaeon, Mnemosyne/PEW on M1; (e) 09-16..09-18
  M2 production owner, point release 9.0/9.0.1, Campaign 4 readiness,
  Campaign 6 observatory review. [HIST]
- Current / terminal role: ORPHANED/SILENT. Last comms post #460 at
  2026-09-18 16:07 (C6 interface delta); last commit 9cfcd3779 (09-18). Did
  not answer Vivarium #563 (09-24, "SFE 8811 and PEW 8377 hold their port"
  during the M2 98% commit incident). STATUS.md still reads "SFE 9.0.1 IS
  PRODUCTION" at currency 2026-09-18 03:45Z. Artemis
  (sfe_retrospective/REPORT.md s0 item 7) calls SFE "orphaned, not decided";
  the operator's 09-18 ruling to move the ledger from SQLite to Postgres
  (comms #448) was never executed. [HIST]
- Relationships: first user Harmonia (M2); consumers Vivarium (queue +
  executor), Archaeon (producer/tick, Campaigns 1-6), Mnemosyne/PEW (fossil
  consumer, SFE owns phenotype emission semantics -- roles/Daedalus/
  todo_20260902.md), Proteus (organisms for C4-C6), Herakles (bitstring
  defect F-1), Kairos (claim census), Apollo (Apollo's Gen-2 adapter targeted
  the older /v0 Foundry, not SFE; Apollo measured on 09-11 that SFE /v2
  exposes no search/evaluate routes -- roles/Apollo/STATUS.txt).
- Hosts: M1 / SKULLPORT 192.168.1.202:8811 (09-01..09-15; ledger
  eng_8a37a5d3, moved F: -> D: 09-12); M2 / SPECTREX5 192.168.1.191:8811
  (09-16 onward; ledger eng_906356f7, D: SMR HDD then C:\Prometheus-data\sfe
  NVMe 09-17). The ancestor D-13 Foundry runs on M1 192.168.1.202:8799 from
  F:/SerendipityD (PID 23276 since 2026-08-30 per the 09-02 survey). [HIST]

## 2. Engine / system inventory

### 2.1 Serendipity Foundry Engine (SFE), "Gen-2", /v2
- Paths: SerendipityFoundry/SerendipityFoundryEngine/{sfe/, serve.py,
  workspace.py, manage_client.py, tests/, deploy/, docs/}.
- Purpose [INTENT]: "durable multi-world research runtime" -- per-world
  hash-chained event ledger, atomic leased work queue, fork-by-reference,
  prediction ordering, first-class failures, sharing topology, budgets,
  claims, families, attestation (GENESIS.md, docs/..._ARCHITECTURE.md).
- Size [IMPL]: sfe/ 9,783 lines (runtime.py 5,125; api.py 1,599; store.py
  1,190; executors.py 492; attestation.py 281; canary.py 241; events.py 211);
  tests/ 33 files, 436 `def test_` functions at HEAD (STATUS.md cites "Tests
  512", presumably parametrized). Schema version 9 (sfe/store.py:35).
- Major versions [HIST]: schema 1 (09-01) -> GEN-2.1 crossing hardening
  (09-02, f5866b130) -> v5 session affinity (09-05) -> v6 scientific
  provenance (869df1fa1, 09-05) -> v7 measurement meaning / read scopes
  (2fa52de86, 642736763, 09-06) -> v8 artifact resolution + cost events
  (ef05397f2, 09-09) -> v8 + A6 attestation journal (8c53d04e6, 09-12) ->
  v9 world facts: logical_time, typed termination, sealed WORLD_EVENTs,
  manifest envelope (084e8c18e, 09-17) -> 9.0.1 WAL/checkpointer repair
  (build 699ca0f9, deployed 2983bd548, 09-17).
- Entrypoints: `serve.py` (FastAPI/uvicorn; flags --science-profile
  off|warn|strict default warn, --session-enforcement advisory|strict default
  advisory, --max-artifact-bytes); `python -m sfe.canary`; client
  `SerendipityFoundryClient/sfclient/client.py` (stdlib EngineClient /
  RemoteWorker).
- Important classes [IMPL]: `Foundry` (runtime.py:712, the only writer);
  `Store` (SQLite WAL, FK on, BEGIN IMMEDIATE, content-addressed blobs);
  `events.append/verify_world` (per-world hash chain); `Executor`,
  `WorkPackage`, `ExecutorResult`, `WorkerLoop` (executors.py); `Journal`
  (attestation.py, A6 intent-before-write journal).
- Data flow: client token -> client_id -> runtime method -> one write
  transaction mutating a table and appending the matching event -> commit.
  Work: enqueue_work -> claim_work (lease, fencing claim_id) -> start ->
  executor.execute -> complete_work/fail_work (idempotent, exactly-once).
- State representation: ~29 SQLite tables (store.py) -- clients, sessions,
  worlds, events, work_items, hypotheses, predictions, experiments,
  observations, failures, artifacts, lineage_edges, budgets, reservations,
  checkpoints, families, claims, measurements, read_scopes/grants, cost
  events, etc.
- Persistence: one SQLite file per engine instance plus a blob dir. Ledger
  rate ceiling measured ~400-900 events/s single process; ~1.07 KB/event
  (docs/campaign_6/SFE_C6_OBSERVATORY_REVIEW_2026-09-18.md s1). [RESULT-UNVERIFIED]
- Execution model: single-process service; workers are external processes
  (Vivarium's executor) or in-process WorkerLoop (canary/tests).
- Scale [HIST]: M1 ledger 89,939 experiments (86,296 from Vivarium), M2
  production 2,070 experiments (Artemis REPORT s0 item 7, s1.3). Not
  re-counted here.

### 2.2 Reference executors (the only "physics" SFE ships)
- `BitStringExecutor` (kind evaluate_bitstring): hidden target =
  sha256("target:{seed_root}:{length}") bits; score = fraction of matching
  positions; solved iff score >= 1.0 (executors.py:47-117). A onemax-like
  landscape. [IMPL]
- `NKLandscapeExecutor` (kind nk_landscape_v0, 09-10, b91880a2d): NK
  landscape with integer tables hashed on demand, N in 8..20, k in 0..N-1,
  optimum CERTIFIED by enumeration (2^N), joint locus permutation for an
  exchangeability null, no defaults, exact param set (executors.py:122-406).
  Also `nk_coordinate_scan`, the specified strict-increase climber. [IMPL]
- `NondeterministicExecutor` (os.urandom; replay-honesty test). [IMPL]

### 2.3 Gen-2 canary driver
- sfe/canary.py: five worlds forked from one checkpoint, one per sharing
  policy, bounded (mu+lambda) over 24-bit strings. Documented in
  docs/SERENDIPITY_FOUNDRY_GEN2_CANARY.md. [IMPL]

### 2.4 SFE client and harnesses
- SerendipityFoundryClient/: sfclient (stdlib), config (profile + public
  certs m1.crt/m2.crt), examples (run_sample, run_worker), test_harness
  (12/12 capability harness, 7/7 two-experimenter isolation). [IMPL/HIST]

### 2.5 deploy/ tooling (operations, not science)
- 154 tracked files: verify_deploy, make_pin, preflight_deploy,
  prepare_deployment, qualify_v9, release_v9, longrun_load, write_path_profile,
  c9_burst_stall, rehearsal_restart_m2, adopt_m1_ledger, move_ledger_to_*,
  relocate_m2, claim_census, fossil_ancestry, reconcile_attestations,
  reconcile_costs, read_scope_grant/verify_read_grant, orphaned_commits,
  watchdog scripts; dated receipt directories (LONG_RUN_2026-09-17,
  RELEASE_9_0_1_2026-09-17, REHEARSAL_RESTART_2026-09, C9_BURST_STALL, etc.).

### 2.6 World Foundry v0 / wforge (09-02)
- SerendipityFoundry/worldfoundry/{wforge/, schemas/,
  WORLD_FOUNDRY_V0_EXTERNAL_REVIEW_PACKET.txt}; 593 lines of Python.
- WorldGenome (grammar_version, generation_seed, parent_ids,
  mutation_history; content-hash identity) -> expansion to integer
  Mechanics (register bank mod 2^16, linear transition ops, optional regime
  switch, stochastic kicks, action delay, per-slot conserved charge with a
  hidden-window yield predicate, 1-2 slots sharing one register bank,
  permuted/corrupted/delayed observation) -> deterministic xorshift64 runtime
  with trace hash. Mutation ops PARAM_PERTURB, PRIMITIVE_INSERT/DELETE,
  REWIRE, BUDGET_MUTATE, INTERFACE_MUTATE. Probe battery of human-shaped
  reference players (noop, const_max, ...), flagged by its own red-team note
  as "HUMAN-SHAPED". [IMPL]
- Later importers: NPE and Bellerophon's toolbox import wforge (Artemis
  REPORT s2.3; not re-verified). [HIST]

### 2.7 Microstructure Hadron Collider (MHC) v0/v1 and prodledger (09-02)
- SerendipityFoundry/worldfoundry/mhc/ (harness, players, qualify, stats,
  ledger, prodledger/). An observatory for "zero becomes not-quite-zero"
  structure: per-block conditional ranks vs matched reference ensembles,
  anytime-valid wealth process, interventional causal depth (flip one obs
  bit, replay the player only), conserved-risk admission-rights ledger with
  cryptographic beacon seal (G9/G14/G15). Production-key set pinned EMPTY:
  "structurally incapable of minting a scientific admission" (85c74304c).
  [IMPL per commit body; code not read line by line]

### 2.8 Incubator / World-0 design (09-02) -- design only
- SerendipityFoundry/incubator/: World-0 design review (BUILD_WITH_REVISIONS),
  OEE research program v0 (OEE failure atlas, E0-E7 observational hierarchy),
  WORLD0_KILL_CRITERIA.prereg.txt (K0-K15), failure_coordinate_schema.v0.json,
  world_phylogeny.schema.v0.json. "No world built, no campaign launched."
  [INTENT]

### 2.9 WOW archaeology, stackvm admission, selection boundary (09-03)
- SerendipityFoundry/wow/ (extract.py, boundary.py, make_queue.py,
  WOW_ADMISSION_QUEUE.jsonl), stackvm_admission/ (canonical_null.py,
  hostile_null.py, provenance.py, VERDICT_ENTROPY_HARNESS.py, FAILED_VERSIONS/),
  selection_boundary/ (selection_provenance.py, selection_replay_audit.py,
  toy_* scripts, FAILED_VERSIONS/). Statistical-admission tooling over the
  D-13 historical corpus. [IMPL per file listing; packets read]

### 2.10 Genesis line (pre-seat, preserved)
- SerendipityFoundry/D6, D6A (src/ 15 py, straight-line Boolean circuits over
  6 inputs per archaeon/docs/expansion/ASSETS.md:151), D7 (17 py; 3-register
  mod-13 machine), D8 (agent_d8, SVM-8 stack VM), D10, D10phase2. All
  committed once in d332658cf and never modified (GENESIS.md "kept as it
  arrived"). [HIST]

### 2.11 The off-repo ancestor: D-9 / D-13 Foundry (F:/SerendipityD)
- 31 commits 2026-08-28..2026-09-01; Python package `foundry/`
  (core, ledger, store, engines{gp/stackvm, gp/treegp, pyshgp_adapter,
  qd/qdax_external}, archives{simple_grid, novelty_archive, pyribs, qdpy},
  search{random_search, objective (tournament GA), novelty, map_elites,
  world_search, selection}, representations Q0-Q5, court, searchphysics,
  worlds{parametric, transducer, consequence}, api /v0). Release
  source_tree_hash 50b5c232 over 211 allowlisted files. [IMPL, off-repo]
- THIS, not SFE, is the code that actually performs serendipity search.
  Daedalus's charter excludes it from his maintenance scope
  (RESPONSIBILITIES.md: "I do not maintain: the live D-13 instrument").
  Atlas does not index it (roles/Atlas/STATUS.md:74: "F:/SerendipityD is
  ignored for now (operator)", ruling 2026-09-19).

## 3. Architecture

What "serendipity search" the SFE does in code -- the brief's direct
question. Answer [IMPL]: NONE. The engine contains no search, mutation,
selection, novelty, QD, or curriculum logic. executors.py says so twice:
"executors EXECUTE and MEASURE; they do not hypothesize or choose
experiments" (module docstring) and, of NK, "It scores ONE candidate; the
search that produces candidates is the caller's, and deliberately so -- an
executor that searched would be measuring itself." A grep of sfe/*.py for
serendip|novelty|mutat|search|explor hits only the package docstring, the
FastAPI title, comments ("This is scoping, not search"), the event name
MUTATION_PROPOSED, and canary.py. The only search loop shipped in the
package is sfe/canary.py, which the architecture doc places outside the
runtime ("a driver/agent that USES the runtime; not part of the runtime").
The serendipity search proper lives (a) in callers (Vivarium, Archaeon,
Proteus, Harmonia) and (b) in the ancestor D-13 Foundry's foundry/search/.

Component-by-component for SFE:
- World: a row in `worlds` (id, client, session, seed_root, sharing_policy,
  topology_group, state machine CREATED/RUNNING/PAUSED/TERMINATED, manifest
  envelope <= 256 KiB from v9, labels, logical_time). It is an isolation
  and provenance namespace, not an environment. [IMPL]
- Organism/player: none. A candidate exists only as an executor payload
  (bits string) or as an opaque artifact blob written by a caller. [IMPL]
- Genotype / phenotype: not represented by the engine; schema 9 offers
  opaque slots (artifacts <= 32 MiB, observations with payload). [IMPL]
- Memory / compute model: SQLite single writer; no simulation step. [IMPL]
- Mutation/search operators: none in runtime; canary uses k-bit flip. [IMPL]
- Selection / admission: no fitness selection. "Admission" exists only as
  provenance gates: prediction must precede observation (sealed hash +
  event_seq), committed_seq closes the prospective window, evidence_class
  ENGINE_WORK_RESULT vs CLIENT_ASSERTED, require_attestation per world,
  family planned_members vs recorded members (best-of-N visible), claims
  with estimand/status. [IMPL]
- Pressure: per-world budgets (enforcement measured|enforced; measured is
  the default and caps nothing -- TODO D6-3), reservations, cost events.
  "Compute scarcity is state" (canary comment) but no ecological pressure.
- Observation / action: none at engine level.
- Reward / fitness: executor-local (fraction matched; NK normalized sum;
  certified solved_status).
- Temporal dynamics: event_seq, logical_time (v9), typed termination.
- Spatial topology: none; "information topology" = sharing policies
  ISOLATED, FAILURES_ONLY, HYPOTHESES_ONLY, FAILURES_AND_HYPOTHESES,
  SUCCESSES_ONLY, FULLY_SHARED, EXPLICIT_IMPORT_ONLY (runtime.py:144-154),
  gated by bilateral topology_group consent (`_may_cross`).
- Reproduction: fork(world, checkpoint, children) by reference -- child
  chain starts on parent's fork-point hash without copying rows; the fork
  records `changed`/interventions. This is world forking, not organism
  reproduction. [IMPL]
- Learning/adaptation: none.
- Communication: artifact import with permanent origin=IMPORTED provenance.
- Cross-world transfer: import_artifact (policy-gated). [IMPL]
- Lineage tracking: lineage_edges (add_lineage_edge, ancestors/descendants),
  fossil ancestry joins (deploy/ANCESTRY_2026-09-12). [IMPL]
- Provenance: per-world hash chain; engine_instance_id names the LEDGER;
  engine_source_hash/build pin; A6 intent journal (attests attempts the
  ledger cannot record because the lock failed); work attestation
  (executed_config_hash vs spec_hash -> config_match). [IMPL]
- Experimental control structure: hypotheses -> predictions -> experiments
  (spec_hash, commit boundary) -> work -> observations (outcome
  FALSIFIED/SURVIVED/INCONCLUSIVE, client supplied) -> claims; families
  group arms with roles; read scopes/grants for cross-seat reading.

Where design and implementation disagree:
- GENESIS/architecture call SFE a "multi-world research operating system";
  the name "Serendipity Foundry" and later program prose (Archaeon charter
  "the petri-dish maker"; 09-21 directive "open-ended foundry for
  generating, selecting, transferring and testing worlds", per Artemis s1.1)
  imply a generator/search engine. Code: a ledger with two toy executors.
  [CORRECTION of the prose]
- Atlas catalog entry `prometheus-sfe-campaigns`
  (roles/Atlas/catalog/ECOSYSTEMS.jsonl line 4) records search "GA with
  mutation walks; transport/import of residue across worlds" and pressure
  "explicit_fitness, quality_diversity". That describes Archaeon/Proteus
  science that used SFE as its ledger, not SFE. Atlas SOURCES.md says SFE is
  "driven by Archaeon, Vivarium, Daedalus". Disagreement recorded. [CORRECTION]
- BitStringExecutor docstring originally claimed every world sharing a seed
  shares the landscape; corrected 2026-09-08 (WP-0a): Vivarium passes the
  repeat-derived seed, so repeats of one world get different landscapes
  (executors.py:73-84). [CORRECTION]
- The canary doc says the canary "can FALSIFY such a claim"; see s9 T1 for
  why its geometry made a null nearly forced. [CODE-INFERRED]

## 4. World capability audit

SFE worlds are namespaces; their "physics" is whatever executor kind the
queue admits. Admitted kinds at HEAD: evaluate_bitstring, nk_landscape_v0,
nondeterministic (executors.py). Artemis records "9 days to the first
non-onemax world" and Herakles "0 of 69 inbox templates build today"
(INBOX_HERAKLES_BITSTRING_EXECUTOR_2026-09-06.md; roles/Archaeon/
TRIAGE_HERAKLES_INBOX_2026-09-06.md:83). [HIST]

Per executor [IMPL]:
- evaluate_bitstring: state = one hidden L-bit string (canary L=24);
  nonspatial; fully static; no partial observability beyond the hidden
  target; action = submit one candidate; horizon 1; no delayed consequences,
  adversaries, agents, resources, ecology or change; separable and
  non-deceptive (onemax-like). Any two worlds are unrelated by construction
  (sha256 target), so expected transfer is exactly zero -- Herakles C-1 "a
  relatedness axis" was the top missing capability. Effectively a toy:
  a fixed 24-bit onemax.
- nk_landscape_v0: N in 8..20 (2^20 = 1,048,576 genotypes max); epistatic
  ruggedness via k; certified optimum; permutation null. Nonspatial, static,
  single query, no agents. Explicitly a "method-evaluation instrument"; the
  20-bit cap exists so solved_status is a fact.
- No executor implements open-endedness, environmental change, task
  diversity, world generation, multi-agent interaction, or transfer.

wforge worlds (not served through SFE as an executor kind in the crawled
code) [IMPL]: 4..12 registers mod 65536, 1 slot (75%) or 2 slots (25%)
writing one shared bank, horizon in {32,64,128,256}, 2..5 linear transition
ops, optional regime switch (period 8..64), optional stochastic kicks,
action delay 0..4, action width 1..3 with values in [0,K), conserved charge
with metabolic cost and a hidden window-predicate yield contested between
slots, observation = permuted subset of registers with optional corruption
and delay. Partially observable, stochastic option, delayed consequences,
2-agent resource contention, world genome mutation and lineage. Still small:
state is at most 12 x 16-bit words; dynamics are linear; horizon <= 256.
Whether wforge worlds were ever executed at scale is UNKNOWN from this
crawl (demo_diversity.py exists; NPE/toolbox import it per Artemis).

Genesis worlds [HIST from reports]: D7 = 3-register machine mod 13 (2,197
states) with a provably unreachable 13-state island; D8 = SVM-8 straight-line
stack VM, max 12 tokens, 26 opcodes, six task families over byte I/O pairs;
D6A = straight-line Boolean circuits over 6 inputs, 64-row truth tables;
D10 = memory-organization interface over the D-9 corpus. All toy-scale by
the charter's definition.

D-13 Foundry worlds [IMPL off-repo]: exact integer-function tasks (synthetic
families, PSB2 loader), plus a "shared causal world" where a program acts as
a controller over integer observations (foundry/worlds/). Apollo's Gen-2
use was f(x)=3x+1 over 12 cases (apollo/cycles/serendipity_slice). The
Search Physics 50-world ecology found no common viable world region for the
three representations (ECOLOGY_REPAIR_VERDICT.md).

## 5. Organism capability audit

SFE has no organism. The only organisms that ever ran through SFE-owned code
are the canary's 24-bit strings: no instruction set, no memory, no control
flow, no sensors or actuators, no learning; "reproduction" is a 2-bit flip
of a parent. Could an organism here exhibit a nontrivial reasoning
primitive? No -- by construction there is nothing to execute. [IMPL]

Organisms that SFE RECORDED (from other seats): Proteus TT programs on the
Proteus VM (Archaeon C1-C5 via the WSE harness), Vivarium H0-H5 rows. Their
capability belongs in the Proteus/Archaeon/Vivarium dossiers. SFE could at
most anchor their genotype diffs by hash and "cannot verify the diff is
complete" (C6 review s0 axis O). [IMPL/INTENT]

Ancestor D-13 stackvm-v1 [IMPL off-repo, vm.py header]: 33 opcodes, 64-bit
wrapping words, stack (max 1024), 8 registers, 256-word memory, absolute and
relative jumps, JZ, bounded LOOP/ENDL (iteration <= 65535, loop stack <= 16),
every byte sequence a legal program, step-metered and bit-deterministic.
Writable memory and loops make it in principle capable of nontrivial
computation. In practice the D-13 corpus shows 7 successes in 71,683
executions, all on stackvm (WOW packet A6/A7), and Apollo's 09-01 ladder
found only identity and x+1 solvable at budget 600, with abs/threshold at
7/12 partial (CALIBRATION.md CAL-08). A fighting chance existed in the
substrate; the search budget and drivers never exercised it. [RESULT-UNVERIFIED]

## 6. Search and pressure mechanism

- SFE: none (s3). Novelty is produced entirely by callers.
- Canary [IMPL]: (mu+lambda) with mu=4, lambda=8, 20 rounds, 2-bit
  mutation (two independent random flips, possibly the same bit), truncation
  to the best 4 of offspring + parents, imports appended to the pool.
- D-13 drivers [IMPL off-repo]: random_search; objective_ga (tournament k=3,
  elites 2, crossover p=0.5 if the engine declares recombine, otherwise pure
  mutation, declared tie-break policy); novelty search with a novelty
  archive; MAP-Elites over any Archive (uniform random elite, mutate,
  offer); world_search. Archives: in-house grid, novelty archive, pyribs and
  qdpy wrappers, QDax via isolated venv.
- Bottlenecks and collapse modes:
  * Canary: identical RNG across worlds plus parity-preserving mutation
    (s9 T1).
  * D-13 objective_ga era: 85 of 87 selection events FULLY TIED --
    "seeded-tie-break drift, not selection" (WOW packet R2). The 0.1.0
    elite tie-break used artifact-id order, so "the same artifact won every
    tie at every seed" (objective.py comment).
  * D-13 genotype length bimodality: 0 of 38,163 length-changing mutations
    crossed <=150 -> >700 bytes; two non-interbreeding populations (WOW R3).
  * Ledger throughput: at evolutionary scale "the ledger is the bottleneck
    of evolution, not the VM" (C6 review s1): ~400-900 events/s, so 1e6
    evaluations per run cannot be one ledger row each.
  * Queue-kind gate: every new world had to become an executor kind first;
    operator correction "do not bend the science around the queue kind"
    (Artemis s1.3/s4). [HIST]

## 7. Measurement / ruler stack

SFE measures the research act, not mechanisms. [IMPL unless marked]
- Ledger integrity: `verify_world` recomputes the hash chain. TODO D6-2:
  `ledger_integrity_ok: true` "on deliberate garbage" -- it verifies the
  chain, never the contents.
- Prediction ordering: prediction seq must strictly precede the observation
  that cites it; experiments must be committed before outcomes.
- Evidence class: ENGINE_WORK_RESULT only when work_id names a COMPLETED work
  item of the same world enqueued for that experiment; otherwise
  CLIENT_ASSERTED (runtime.py ~2395-2455). The class does not read the
  attestation's config_match.
- Attestation (v6): executed_config_hash vs spec_hash -> CONFIG_DIVERGENCE
  finding; blocking only under --science-profile strict; default warn.
- Families: planned_members vs recorded members ("counting, not judgement",
  runtime.py:3684-3688) so best-of-N is visible.
- Budgets: enforcement `measured` (default) records but caps nothing
  (TODO D6-3: limit 2, attempted 6, accepted 6).
- Event counts: 20 identical reposts -> 20 ARTIFACT_CREATED events vs 1
  distinct artifact in the knowledge frontier (TODO D6-4).
- Executors' rulers: bitstring fraction matched with solved at 1.0; NK
  integer sum with certified optimum and integer equality for solved.
- Controls: canary isolated world (W1) as a no-sharing baseline; NK
  permutation null (G1) and k=0 one-scan guarantee (G2); nondeterministic
  executor as a negative control for reproducibility claims (T17).
- Known blind spots: D6-1 "Every epistemic signal stays green on a
  contradicted execution" -- reproduced 09-06: spec arm-A, executor attests
  arm-NOT-A -> HTTP 200, CONFIG_DIVERGENCE finding, but
  observations_engine_attested 1, observations_prospectively_predicted 1,
  claims_surviving 1, and world_status shows nothing (TODO.md D6-1). At HEAD
  the evidence_class assignment still does not consult config_match
  [CODE-INFERRED]; whether production ran strict is UNKNOWN (the pinned
  launcher lives off-repo at D:\Prometheus-data\sfe\; the superseded
  in-repo M2 launcher passes no --science-profile, i.e. warn).
- A6: before 09-12 a lock-timeout 500 left no trace in the ledger ("the
  ledger is silent exactly when the engine is what broke", 8e4fc377a).
- D-13 Court (off-repo, INTENT from README): fail-closed verdict ladder,
  FOSSIL_ONLY default; MHC: per-block conditional ranks, wealth process,
  alpha-wealth charged at family creation, three permanent thresholds and
  UNRESOLVED_WEAK_SIGNAL.

## 8. Experiment inventory (campaigns)

C-D1. Genesis D-series (pre-seat "Serendipity" sessions)
- Dates 2026-08-27..08-30. Question: can accumulated executable history be
  organised by the machine to raise future exact-problem findability?
- D-6A (08-27): organism straight-line Boolean circuits; world 6-input truth
  tables; arms H0..H3, RANDZ, Z0ARM; 24 tasks x 12 seeds x 200k oracle
  calls. Reported: verdict ENDOGENOUS_SIGNAL_FOUND but P3 causal findability
  FAIL (H3-H1 +0.010, CI [-0.010,+0.042], p=0.49), P5 transfer 0/144
  (D6/VERDICT.json, D6A/REPORT_D6A.md). Label: REPORTED NEGATIVE/NULL on
  the primary (with a weak geometry signal: on-manifold submissions 4.2% vs
  0.4%).
- D-7 (08-28): 3-register mod-13 machine (2,197 states), a provably barred
  island; history-conditioned synthesizer H2 finds a crossing in median 23.5
  evals vs 73 for the strongest history-free baseline; "7 independent
  auditors ... SOUND" (D7/README.md). Label: REPORTED POSITIVE. No later
  challenge found in the repo (archaeon/docs/expansion/ASSETS.md:221 lists it
  RUNNABLE_IN_ISOLATION). Toy-scale, designer-built barrier.
- D-8 (08-28): SVM-8, hoard-derived proposal distribution vs GA; verdict S0
  NO_EFFECT (D8/SESSION.md). Label: REPORTED NEGATIVE/NULL. Four
  validation generations, failures preserved.
- D-10 (P1/P2): endogenous relevance keying; Phase 2 decision
  ASSAY_NOT_VIABLE_SYNTAX_ONLY -- relevance structure exists (artifact x task
  interaction 69.3% of variance; oracle 0.042 -> 0.375) but is not
  recoverable through the syntax-only interface (D10/D10_INDEX.md). Label:
  INSTRUMENT FAILURE (the interface, not the hypothesis, was retired).
- Commit: d332658cf (archived as-is).

C-D2. D-9 / D-12 / D-13 Foundry and Search Physics (off-repo, F:/SerendipityD)
- Dates 08-28..08-30. Question: can heterogeneous search systems (stackvm,
  PushGP, tree-GP) be compared in a shared causal consequence space?
- Reported: CROSS_REPRESENTATION_ASSAY_NOT_VIABLE (|W*| = 0 over a frozen
  50-world family) after a ruler repair that removed a manufactured
  searchability gain (max-over-300 vs max-over-12 baseline: +0.0741 vs
  +0.0001 under an equal-budget null) (ECOLOGY_REPAIR_VERDICT.md s3-s4).
- D-9 Phase B never ran: d9/{arms,evidence,results,validation}/ are empty.
- Label: INSTRUMENT FAILURE (then a bounded negative).

C-D3. Gen-2 canary (09-01)
- Five forked worlds x five sharing topologies; 24-bit bitstring; mu=4,
  lambda=8, 20 rounds, seed 20260901.
- Reported: all five worlds best 0.958 (23/24), stdev 0.0; sharing worlds
  reached it one round later with 316 vs 240 evaluations; "Negative
  result" (docs/SERENDIPITY_FOUNDRY_GEN2_CANARY.md).
- Later reinterpretation: this crawl (s9 T1). Label: REPORTED NEGATIVE/NULL
  (geometry-forced; see T1).

C-D4. Isolation audit and onboarding (09-01)
- Six adversarial auditors; two critical cross-tenant breaks (unscoped work
  claim; artifact import by id) fixed fail-closed with regression tests;
  32/32 suite, 12/12 harness, 7/7 live isolation (SESSION_STATE genesis).
  Label: REPORTED POSITIVE (engineering).

C-D5. WOW-0 forensic survey and WOW archaeology (09-02, 09-03)
- Read-only archaeology of the D-13 instrument and corpus: Zeus F's
  reported numbers do not match the server; the World-0 footprint is ~100x
  larger and there are two complete train+hidden successes, not one; the
  release pin is source-only and start-time cached, the hidden-test corpus
  var/tasks.json is outside it; a hidden-test exposure path existed but the
  logs show it was not used (forensics s1). WOW: 183,856 records, 71,683
  executions, 3 engines, 7 successes (all stackvm), 97.7% tied selections,
  89.3% of failures under 100-400 step ceilings, bimodal sterile length
  valley (WOW R1-R3, A6-A8).
- Label: MIXED (strong corrections; "NOTHING CONFIRMED. NOTHING ADMITTED").
  Artemis comms #1133 subject later calls a "stackvm double-solve
  deflationary" (body not read).

C-D6. Incubator World-0, World Foundry v0, MHC v0/v1 (09-02)
- World-0: design only, BUILD_WITH_REVISIONS after review found 3 FATAL
  economic + 4 FATAL methodological defects (17f2b8d3a). World Foundry:
  10 FATALs incorporated, wforge prototype, "Nothing launched" (6efa4f88d).
  MHC v0 qualification campaign (~4 min single core, deterministic): power
  curves, admission FP 0/20 at eps=0, sign test fires 15/15 on an
  operator-coherence artifact vs ranks 0/15, and "HEADLINE BLINDNESS ...
  near-zero power for micro-effects on a base with genuine intrinsic
  structure", frozen observable family blind to the late-onset class 0/12
  (5ceeb5b9b). Prodledger hostile qualification: 7/14 attacks succeeded on
  v1.0, 0/14 on v1.1; 2,000,000 adversarial transitions without a
  conservation violation; an LCG low-bit defect caught (85c74304c).
- Label: INCONCLUSIVE (instrument qualification; no science run).

C-D7. stackvm-v1 admission language (09-03)
- Reported STACKVM_ADMISSION_LANGUAGE_QUALIFIED_WITH_LIMITATIONS
  (5821ee076), retracted 12 minutes later to STACKVM_NULL_COMPROMISED
  (0496968b1): steps observable saturates 44.3%; R1 sampler not
  exchangeable (P(top) 0.0800 vs 0.0625); R1/R2 are selection detectors
  (10/12 hill-climbed reject at nominal 1/200 vs 0/12 unselected); spec-menu
  multiplicity inflates the level to 0.1-1.0.
- Label: LATER OVERTURNED (self-retraction after independent review).

C-D8. Selection boundary (09-03)
- Toy measurements: candidate-conditional randomized tests hold level under
  specimen selection (0.0533 at n=1 vs 0.0647 at n=200,000) but not under
  observable selection (best-of-20 observables rejects at 0.648); exact
  enumeration of 16,320 single-byte mutants: alpha ranges 0.024-0.969;
  random programs ~84% inert (ef504133f).
- Label: MIXED (theory corrected 5 times by review; status "INADMISSIBLE FOR
  LACK OF A BOUNDED SELECTION" for one class).

C-D9. SFE as substrate for Harmonia / Vivarium H0-H5 / Archaeon (09-04..09-15)
- Engineering campaign: v5-v8, D-LOCK-1, claims usable by a machine, Track A
  joint receipt 29/29 (Artemis), A1 client deadline, A6 attestation, C9
  stall diagnosis (disk, not WAL close), ledger moves. Hosted the M1 corpus
  (89,939 experiments, Artemis). Incident: 13 consecutive H5 rows (rules
  143-155) lost in a 17-minute stall without any ledger trace (BACKLOG_H0H5
  A6). Label: MIXED (service matured; instrument-failure episodes).

C-D10. nk_landscape_v0 (09-10)
- Executor + specified climber + three guarantees (b91880a2d); Archaeon's
  permutation-direction ruling still pending at 09-18 (STATUS.md "Blocked").
  Science use through SFE: UNKNOWN in this crawl.

C-D11. Point release 9.0 / 9.0.1 and Campaign 4 readiness (09-16..09-17)
- Schema 9; WAL/checkpointer repair after eight candidate builds and two
  reverted fixes; acceptance 0 5xx and 0 calls > 5 s in four regimes; G1
  long run FAILED at 3h27m on the SMR HDD, rerun on NVMe 15,408 s with 0 5xx;
  restart rehearsal PASS x2 incl. mid-request kill (e7a699099, f4e020414,
  e556c16ba). Label: REPORTED POSITIVE (engineering).

C-D12. Campaign 6 observatory review (09-18)
- Design only: T0 per-evaluation fingerprints must ANCHOR (sidecar segments
  hashed into the ledger), not INGEST; schema-10 delta D1-D9; "nothing
  built". Never executed. Label: INCONCLUSIVE (unexecuted design).

Archaeon Campaigns 1-5 (09-16..09-18) recorded on the M2 engine are other
seats' science; Artemis notes CMP1 fragment-transfer positives "died under
CRN" and imports took over 12/12 regardless of competence (C3-SFE-10, per
Atlas ATLAS_CROSS_ENGINE_SYNTHESIS F3). Not adjudicated here.

## 9. False-positive / false-negative archaeology

T1. Canary topology null -- a null the geometry nearly forced.
- Claim (09-01): no information topology improved best objective; all
  worlds 0.958; "the deliverable is the rigor".
- Evidence: CANARY.md table.
- Challenge (this crawl, CODE-INFERRED): canary.py seeds every world's
  mutation RNG identically (`random.Random(seed_root + 1)`) and gives every
  world the same initial population; worlds that import nothing into the
  pool (W1 ISOLATED and W2 FAILURES_ONLY, whose failure imports never enter
  `pop`) therefore run byte-identical trajectories, and "sharing" worlds
  import peer bests drawn from near-identical trajectories. Separately,
  `_mutate` flips exactly two independently drawn positions, so Hamming
  distance to the target changes by -2, 0 or +2 and its parity is invariant
  along a lineage. A zero-cost inspection (re-deriving target and initial
  population from the seed, no engine run) gives initial distances 9, 13, 16,
  14 -- the leading lineage is odd-parity and can never reach distance 0.
  The universal 23/24 plateau with stdev 0.0 is what this geometry predicts.
  Also: HYPOTHESES_ONLY publishes the same top bits as SUCCESSES_ONLY
  (identical payload, different label), so W3 and W5 are one treatment.
- Status: the null stands as a record of runtime plumbing; as evidence about
  information topology it is uninformative. No artifact in the repo records
  this challenge. [CODE-INFERRED]

T2. Silent ceiling in the bitstring executor (WP-0a).
- Claim: COMPLETED scores for short candidates. Challenge: Herakles F-1
  (09-06) -- a 16-bit candidate scores 0.25 with an achievable ceiling 0.5
  and `solved` unreachable; reachable from a mined template that passed
  every upstream check. Correction: 85d6ff060 (09-08) refuses
  len(bits) != length. Status: fixed; any pre-09-08 rows with mismatched
  length are suspect. [CORRECTION]

T3. Stale shared-landscape claim (docstring), corrected 09-08 (s3). [CORRECTION]

T4. Epistemic counters green on contradicted executions (TODO D6-1).
- Claim: observations attested / prospective / claims surviving. Challenge:
  reproduced 09-06 with arm-A spec vs arm-NOT-A attestation. Correction:
  none in code; strict mode would block, warn is the default. Status: OPEN
  per TODO; production mode UNKNOWN. [HIST + CODE-INFERRED]

T5. Ledger silence during stalls (A6).
- Claim: the ledger is the complete record. Challenge: Vivarium 09-11 --
  13 consecutive H5 rows (143-155) died in a 17-minute stall with no ledger
  event; a contiguous hole on H5's x-axis "is the shape most likely to be
  read as a property of rule space" (BACKLOG_H0H5 A6). Correction: A6
  intent journal + reconciliation (8c53d04e6, 09-12). Status: closed for
  the engine; pre-09-12 gaps remain unattested. [CORRECTION]

T6. Stall cause misattributed (C9).
- Claim H1: WAL close. Challenge: measurement. Correction e031cb4fb "the
  stall is the disk, not the WAL close -- H1 superseded by measurement";
  NVMe move 633.8 s -> 20.5 s on the same shape (4c2fcfbdf). Later the M2
  SMR drive failed the G1 long run (e556c16ba). [CORRECTION]

T7. stackvm admission qualified -> compromised (C-D7). [LATER OVERTURNED]

T8. D-13 "evolution" was drift (WOW R2): 97.7% fully tied selections; the
  failure landscape was mostly a step-ceiling setting (89.3% of failures
  under 100-400 steps). [CORRECTION of the D-13 era record]

T9. Zeus F / World-0 numbers vs the server record: ~100x footprint, two
  successes not one, no client identified as Zeus F (forensics s1, s7).
  [CORRECTION, other-seat record]

T10. Search Physics manufactured searchability gain (max-over-300 vs
  max-over-12), plus dead floors and unmeasured faults coerced to 1.0;
  repaired, then NOT VIABLE. [CORRECTION]

T11. MHC sign-coherence test false under the null (fragility reads as
  structure); replaced before implementation by conditional ranks. [CORRECTION]

T12. "SFE is a live engine" labels. STATUS says PRODUCTION, Atlas
  registers kind=ENGINE and LIVE, the code has no physics, the watchdog was
  disabled and the owner silent from 09-18 (Artemis s0, s2.2). [CORRECTION]

False-negative regimes:
- Every SFE-hosted null is bounded by the executor kinds: onemax-like
  bitstrings with unrelated-by-construction worlds cannot show transfer,
  curriculum or stepping-stone effects (Herakles C-1).
- The D-13 corpus nulls for treegp-deap and push-pyshgp (0 successes) may be
  adapter defects: Apollo found treegp uniformly 0.000 even on identity
  ("SUSPECTED adapter/integration defect", c6a2b2a44).
- MHC states its own headline blindness for micro-effects on structured
  bases and a late-onset class it cannot see.

## 10. Research outputs

- roles/Daedalus/GENESIS.md -- lineage map D6..D10phase2, gen2 -> sfe.
- SerendipityFoundryEngine/docs/SERENDIPITY_FOUNDRY_GEN2_{ARCHITECTURE,
  API, BASELINE, CANARY, INVARIANTS, MIGRATION, TEST_REPORT}.md,
  SCIENTIFIC_PROVENANCE.md, SESSION_AFFINITY.md, RUNNING_M1_VS_M2.md.
- docs/point_release_2026-09/ -- review, interface delta, schema-9
  migration, deployment, restart, long-run report, benchmark, release
  packet, 9.0.1 repair receipt, two review packets, worldlib note. Artemis
  calls this "the most complete qualification record in the repository".
- docs/campaign_6/SFE_C6_OBSERVATORY_REVIEW_2026-09-18.md and
  SFE_C6_INTERFACE_DELTA.md -- measured ledger envelope, tiered T0-T3
  anchoring design.
- roles/Daedalus/sprint_20260904/ -- closure, external review, M2
  deployment and engine-sprint packets; live repair-bar scripts and results.
- roles/Daedalus/{M2_V6_DEPLOYMENT_READINESS, D23_COMPLIANCE,
  DESIGN_A6_ATTESTATION, TRACKA_PART1_JOINT_BUILD, PROPOSAL_ARCHAEON_READ_
  SCOPE}.md.
- SerendipityFoundry/forensics/SFE_WOW0_FORENSIC_SURVEY.{md,txt}.
- SerendipityFoundry/incubator/*.txt and schemas.
- SerendipityFoundry/worldfoundry/{WORLD_FOUNDRY_V0_EXTERNAL_REVIEW_PACKET,
  MICROSTRUCTURE_HADRON_COLLIDER_V0_REVIEW_PACKET}.txt; mhc/*.txt.
- SerendipityFoundry/wow/WOW_ARCHAEOLOGY_REVIEW_PACKET.txt.
- SerendipityFoundry/stackvm_admission/{CONSOLIDATED_EXTERNAL_REVIEW_PACKET,
  VERDICT_CORRECTION, VERDICT_ENTROPY_THEORY, NULL_PATH_TYPE_SYSTEM,
  SUBSTRATE_C_ARCHAEOLOGY}.
- SerendipityFoundry/selection_boundary/{EXTERNAL_REVIEW_PACKET,
  SELECTION_REPLICATING_NULL_THEORY, SELECTION_BOUNDARY_RESULTS}.
- Genesis reports: D6A/REPORT_D6A.md, D7/README.md + reports/, D8/
  REVIEW_PACKET.txt, D10/PHASE1_REPORT.md, D10phase2/PHASE2_REPORT.md.
- Off-repo: F:/SerendipityD/{SEARCH_PHYSICS.md, ECOLOGY_REPAIR_VERDICT.md,
  CLASSIFICATION_DIFF.md, PRE/POST_REPAIR_WORLD_ECOLOGY.*}.
- External retrospective: roles/Artemis/threads/sfe_retrospective/ (09-27).

## 11. Journals, TODOs, pivots, abandoned branches

- Journals: roles/Daedalus/journal/2026-09-11, -12, -16, -17. The 09-11
  entry lists "Three things I got wrong today"; commit subjects of 09-10
  are self-corrections ("I claimed my edit pointed at her SHA, and it
  pointed at a path"; "a 200 that indexed nothing looks exactly like a 200
  that did"; "I offered a green run as evidence for a claim it cannot
  address").
- TODO.md (702 lines): audited current-state ledger D0-D12 with a closure
  record; D6 "What else fails in the direction of looking good?"; D2 deferred
  items with revival triggers; D2-7 constraint DSL REJECTED.
- BACKLOG_H0H5.md: Band A costs (A6 promoted to top by the operator 09-11).
- Prompts: roles/Daedalus/prompts/ (2026-09-11_b1, base_role, boot2,
  kairos01; 2026-09-12 archaeon_blind_tick, candidate_build, ledger_move, s1;
  HARMONIA_SFE_V6_SCIENTIFIC_PROVENANCE_2026-09-05.txt).
- Pivots and why:
  * 09-02/03 incubator excursion: licensed by the MHC admission-rights
    ledger ("discovery may be maximally aggressive because admission is now
    structurally protected", a6f86c3d3); ended without any admission.
  * 09-11 D-23: the live ledger and TLS key were inside the canonical
    checkout (fe2eb85c9); the service was moved out (e99a7b35c). Artemis:
    the D-23 working contract "grew from an SFE incident".
  * 09-15/16: machine handover to M2 "only as a commit message" (ccb26df01,
    journal 2026-09-16); two-day silent outage on M1.
  * 09-18: two decisions that each invalidated the other's premise --
    Campaign 6 measured that SQLite cannot be the per-evaluation store at
    evolutionary scale (schema 10 proposed), and the operator ruled the
    ledger must leave SQLite for shared Postgres (comms #448). Neither
    executed. Activity stops.
- Abandoned / unexecuted: schema 10; Postgres ledger; D-13 engine wrap;
  full replay ("REPLAY_COMPLETE: NO" per Artemis); distributed M1-M4 fabric;
  arena.run (TODO D1-4); M1 archive ledger copy for Archaeon/Harmonia
  (#415/#416 "NOT NOW"); canonical-copy deletion on M2 (STATUS item 5).
- Branches: origin/daedalus/m2-d6ecd70b-boot-2026-09-16 (only a merge commit
  ahead of main); worktrees F:/Prometheus-worktrees/daedalus-d23 (HEAD
  3f31cbcac, 09-12) and daedalus-sfengine (HEAD d5be5ec4b, 09-10, the
  pinned M1 service tree). Both are older than main.

## 12. Lens inventory

L-D1. SFE as a provenance-of-the-research-act lens
- Substrate observed: the research act (predictions, commits, families,
  attestations, imports, forks), not organisms.
- Organisms / worlds / pressures: none of its own.
- Phenomenon family: selection effects, best-of-N, config drift,
  post-hoc prediction, cross-tenant contamination.
- Resolving mechanism: hash chain, sealed predictions with event order,
  family member counting, attestation, evidence_class, A6 journal.
- Resolution ceiling: ~400-900 ledger events/s single writer; per-eval
  recording infeasible beyond ~1e5 evaluations/run without T0 anchoring.
- Noise sources: stalls on slow disks; advisory/warn defaults; event
  inflation; chain integrity mistaken for content integrity.
- Architectural limit: SQLite single writer, REST round trips ("98%
  round-trip overhead" per Artemis), host-pinned certs/ledgers.
- Reusable: the invariants as a portable receipt contract; the
  qualification pattern; isolation tests.
- Toy-grade: none of the provenance machinery; the executors are.
- Unknown: whether any campaign result would have changed had strict mode
  been on; preservation state of both ledgers.

L-D2. NK-landscape method-evaluation lens (nk_landscape_v0)
- Substrate: N <= 20 NK landscapes with certified optima and an executable
  permutation null. Phenomenon: search-method performance under epistasis.
- Ceiling: N = 20 (enumeration); single-candidate scoring; no dynamics.
- Reusable: integer tables, exact solved_status, the null construction.
- Toy-grade: the landscape size. Unknown: whether any campaign used it.

L-D3. D-13 multi-representation search + Search Physics (off-repo)
- Substrate: stackvm-v1 byte programs, PushGP, tree-GP; drivers random,
  GA, novelty, MAP-Elites; Court; Q0-Q5 hoard representations.
- Phenomenon: comparative search physics (displacement, locality,
  heritability, improvement) across representations.
- Current ceiling: no viable common world found (|W*| = 0); two of three
  engines sterile on the corpus; tie-dominated selection in one era.
- Reusable: stackvm (every byte legal, metered, deterministic), selection
  tracing with declared tie-break, capability manifests, observer/experiment
  scope split. Toy-grade: the task corpus (12-case integer functions).
- Unknown: whether treegp/push adapters are correct; whether larger
  budgets reach nontrivial programs. Atlas ignores this tree by ruling.

L-D4. wforge world-genome generator
- Substrate: seeded integer worlds with lineage-carrying genomes and six
  mutation ops. Phenomenon: world diversity, informative-world search.
- Ceiling: <= 12 x 16-bit registers, linear dynamics, horizon <= 256,
  human-shaped probe battery. Reusable: genome/lineage/hash discipline.
  Unknown: execution scale and results.

L-D5. MHC microstructure observatory and admission ledger
- Phenomenon: tiny, distributed, interaction-dependent structure; admission
  under hindsight. Mechanism: conditional ranks, wealth process,
  interventional replay, conserved-risk ledger. Ceiling: stated blindness on
  structured bases and late-onset classes. Never applied to science.

L-D6. Selection-boundary / admission-statistics toolkit
- Phenomenon: valid nulls for already-selected artifacts. Reusable: typed
  null-path provenance (SPEC_DERIVED / PROTOCOL_CONSTANT /
  EXTERNAL_RANDOMNESS), beacon-selected specs, level-at-realized-c.
  Toy-grade: the measurements are on toy samplers and stackvm mutants.

## Open questions / unknowns

1. Preservation and integrity of the M1 (eng_8a37a5d3, SKULLPORT, now
   Nestor's host) and M2 (eng_906356f7, C:\Prometheus-data\sfe) ledgers.
2. Was production ever run with --science-profile strict? (Pinned launcher
   is off-repo.)
3. Did any campaign ever use nk_landscape_v0 or wforge worlds at scale?
4. Is the canary parity/identical-RNG reading (T1) confirmed by a rerun?
   (Deliberately not run here.)
5. Are the treegp-deap and push-pyshgp adapters in F:/SerendipityD correct?
6. What did Artemis #881 (to Daedalus) and #1133 ("stackvm double-solve
   deflationary") contain? Bodies not retrieved.
7. Current liveness of 8811 on M2 and 8799 on M1 (not probed; no network).
8. Seat disposition: no operator decision recorded resuming, freezing or
   retiring SFE.
