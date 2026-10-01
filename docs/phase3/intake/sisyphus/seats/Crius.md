# Crius -- forensic dossier (Sisyphus crawl)

Seat: Crius
Crawl date: 2026-10-01
Worktree base SHA: 19299e06b (origin/main at crawl time)
Crawler: Sisyphus worker (Opus 5.5), read-only

Coverage statement.
crius/ has 4114 tracked files. Inventory first: 4067 are under crius/runs/ (3357 .gz per-iteration search records,
435 .json, 102 .jsonl, 173 .md); the remaining 47 are code, configs, fixtures, tests and design documents. Runs
enumerate as 66 search runs (configs c0 and c0x x 2 arms, c1, c1b, c2a-d x 3 arms; 3 seeds each),
8 baseline sets, 9 gate receipts, 4 PARTS dirs, 1 calibration dir and 5 top-level summaries.
READ: roles/Crius/RESPONSIBILITIES.md, STATUS.md, RESUME.md, calibration/LEDGER.md (whole), superseded pre-charter
file (head), RESEARCH_SLIDE_2026-09-18.md (head), REVIEW_PACKET_C0 (s0-s1), C1B and C2 packets (exploit sections),
operator directives 2026-09-23 (terminal resolution, first 3k chars) and 2026-09-24 (essay, head);
crius/CRIUS_C2_TERMINAL_REVIEW.md (whole), DESIGN_C0.md (s1, first 80 lines), DESIGN_C1.md (s1 + headings),
world_c1.py (head), vm.py (opcode table, constants), configs/c2c.json (search/vm/budgets/workspace), parts_c2.py
program lengths (assembled, zero-cost import), crius/runs/CAMPAIGN_SUMMARY.md (head); docs/essays/
2026-09-24-accessibility-frontier.md (headings + s8 rulers). Cross-seat: comms #516, #530, #552-#554, #879 (Artemis
R-06/R-07), #1226 (Achilles); roles/Artemis/selftest/runs/R-07/REPORT.md (s1-s3); Artemis INDEX FR-001/FR-003/FR-004;
D004-01 result row; Harmonia ruler digest row in Atlas; Achilles census registry rows; atlas/registry.json engine
entry.
NOT READ: the 3357 gz iteration records and per-run REPORT.md/LINEAGE.md/PATH.md files (relied on the terminal
review's tables and CAMPAIGN_SUMMARY); search.py/evaluate.py/workspace.py/artifacts.py bodies beyond signatures;
DESIGN_C2.md and CRIUS_C2_TERMINAL_PREREG.md bodies (the terminal review quotes them); journals 09-18..09-25;
REVIEW_PACKET_C1 in full; fixtures/c0_failure_families.json.

---

## 1. Identity and purpose

Canonical name: Crius. Instances: Crius[m2-fe63387d] (09-18 research slide), Crius[m2-8d43bbf9] (campaigns and
closure). Host M2 (SPECTREX5); worktree D:\Prometheus-worktrees\crius-base-role, branch
crius/base-role-adopt-2026-09-18, all commits on origin/main. [HIST: STATUS.md, RESUME.md]

History.
- 2026-09-18: seat created with "look at the other roles, set the seat up, receive the charter afterwards"
  (superseded/RESPONSIBILITIES_precharter_2026-09-18.md). Pre-charter output: RESEARCH_SLIDE_2026-09-18.md, a
  deep-research check that "SLIDE" is an OEE name collision and a narrow sparsity reference arm. [HIST]
- 2026-09-19: charter "CAMPAIGN 0 -- ADAPTIVE WORKSPACE SANDBOX" (roles/Crius/prompts/2026-09-19_charter/
  CHARTER_CAMPAIGN_0.md): "put players into a world and see if we can create a fitness function where they are
  rewarded for learning to learn" -- the target is increasing efficiency at converting new experience into reusable
  competence, not task score. Computational vocabulary only (Player, Workspace, Artifact, Task, Lifetime). [INTENT]
- 2026-09-19 (same day): Campaign 0, operator ruling closing C0 and authorising C1, C1, "GO C1B D1 isolation", ruling
  accepting C1b and authorising C2, C2 rungs A/B and a failed rung-C gate -> PARKED (open decision CRIUS-33). [HIST]
- 2026-09-23: operator "terminal resolution" directive (UNPARK or CLOSE; parking forbidden unless infrastructure
  failure); terminal round -> "CLOSED -- ACCESSIBILITY FRONTIER MAPPED" at 10:23:47Z. [HIST]
- 2026-09-24: operator post-closure directive: write a public "Physics of Intelligence" working note; published
  docs/essays/accessibility-frontier.html (commit 391395aac). [HIST]
- 2026-09-25: pre-reboot handoff (RESUME.md); lane CLOSED, no resume pointer. [HIST]

Terminal role: CLOSED seat; experimental lane closed by the operator; any further work is a new charter (different
substrate, selection regime or world). Forbidden rescue moves recorded: lower E/H floors, add E2/H2, more budget,
parts in the population, a C3 rung. [HIST]

Relationships: Crius describes itself as the narrow, instrumented complement to Apollo/Ludus and Aphrodite
(RESPONSIBILITIES s1). C0 design explicitly cites Apollo's earlier "plateau was a search-operator failure" (DESIGN_C0
C1). The essay names Cosmos, BEE, Ensorain, Aether as natural successors for the "controlled pair" experiment
(RESUME). Atlas proposals (ATLAS_EXPERIMENT_TODO RA-4, QD-9, EV-1/EV-8, GEA-4) list Crius as a candidate engine; Atlas
journal 09-21 notes Crius was not yet indexed. atlas/registry.json still lists the crius engine as LIVE; Achilles
flagged it stale (#1226; census registry note). [HIST]

## 2. Engine / system inventory

One engine: the Crius adaptive-workspace sandbox (atlas id "crius", "accessibility-frontier engine"), crius/.

| component | path | role |
|---|---|---|
| C0 world | crius/world.py, tasks.py | 6 hidden ops on Z_16^4 (3 translations, 2 parity-conditional translations, 1 rotation); frozen composition partitions |
| C1/C2 world RELAY | crius/world_c1.py, tasks_c1.py, worlds.py | tuples of 4 ints in Z_8; 12 primitives (INC/DEC/SWAP x position) behind a per-stream hidden permutation; hidden per-stream library of K=3 procedure templates applied relative to an argument; chains of templates |
| streams | crius/streams.py | (namespace, seed) -> (permutation, library, task sequence); sealed qualification namespace |
| workspace | crius/workspace.py | cells, streams, records, links, alloc; 256 cells / 4096 bytes; snapshot/restore/scramble |
| artifacts | crius/artifacts.py | ExecutableBlock store (32 blocks x 64 instr, 8 state slots), create/append/patch/copy/compose/delete/invoke, invocation log |
| VM | crius/vm.py (705 lines) | 8-register bytecode VM over ints and int tuples; ~49 opcodes incl. WS_* and BLK_*; C2 typed ops PSTEP, PREC_BEGIN/END, PINVOKE (rung B) and PSIM/PMATCH (rung C) gated by SUBSTRATE flags |
| env | crius/env.py | TaskRun: interactions vs compute vs store units, budgets, 200-step post-success grace |
| evaluate | crius/evaluate.py | frozen metric; lifetime conditions ACCUMULATED/FRESH/RESET/SCRAMBLED etc. (battery A-J) |
| baselines | crius/baselines.py, baselines_c1.py | controls only: RANDOM, HEURISTIC, ENUMERATE, ENUMERATE_VM, CACHE_REUSE, ADAPTIVE (C0); QUIT, TABLE_MEMO, PROCEDURE_REUSE, PROCEDURE_NOCAL (C1) |
| search | crius/search.py | (mu+lambda)=(8+24) mutation and selection, 7 mutation operators, segment splice, arms random/seeded/recombination, paired streams, takeover check |
| qualify/report | crius/qualify.py, report.py, receipts.py, lineage.py, campaign_summary.py | sealed-stream qualification of top-3/contemporaries/ancestors; ASCII reports; receipts with replay hash |
| gate | crius/gate_c1.py | pre-search gate witnesses A-H; v2 with separate positive (E/H) and causal (F/G) controls |
| PARTS | crius/parts_c2.py | hand-written bytecode programs P_BASE(19 instr), P_REC(25), P_CAL(35), P_INV(37), P_REC_INV(43), P_PLAN(58), P_REC_INV_PLAN(64); value landscape by construction |
| C2 analysis | c2_summary.py, c2_path.py, c2_terminal.py, exploit_probe.py, calibrate_c1b.py | path evidence, paired re-evaluation of partial steps, mechanical disposition scorer, exploit probes |
| tests | crius/tests (test_sandbox, test_c1_integrity, test_c2, test_c2_terminal) | 41 passing at 1f229d79f (RESUME) |
| fixtures | crius/fixtures/c0_failure_families.json | C0 failure families preserved as fixtures |
| configs | c0, c0x (EXPLORATORY), c1, c1b, c2a-c2d | frozen with config hashes |

Execution model: finite CLI commands (python -m crius.search/qualify/report/gate_c1/c2_terminal); multiprocess
evaluation pool; no daemon, no monitor. Persistence: per-iteration gzipped candidate records, per-run REPORT.md,
LINEAGE.md, PATH.md, qualify JSON, probe JSON, receipts carrying code_commit, config_hash, world/partition/
task-sequence fingerprints and a replay hash. [IMPL + HIST]

Scale: 66 search runs x 7208 candidates (8 initial + 24 x 300 iterations) = ~476k candidate evaluations, each on 2
paired streams of 50-task lifetimes plus a takeover stream. The terminal round alone: 18 runs, 129,744 candidates.
[IMPL arithmetic from config; HIST counts]

## 3. Architecture

World (C1/C2 RELAY). State = tuple of 4 integers mod 8 (4096 states). The Player emits action ids 0..11 (plus RESET);
a hidden per-stream permutation maps ids to primitives. A hidden library of 3 templates (2-3 steps each, relative
offsets) generates targets: target = chain of d templates with per-task arguments applied to start. The Player sees
start, target, budgets, number of actions, its own status channel -- never templates, arguments, the permutation or
stage. Lifetime = 50 tasks in stages A10 (single templates, repeated), B10 (new args), C12 (chains of 2), D10
(chains of 3), E8 (chains with a repeated template; qualification adds length 4). Budgets: depth 1 2000
interactions; deeper chains 800/1200/1600 in C1, cut to 50 in C1b/C2 (c2c.json) after walkers exploited generous
budgets. 1 interaction = 100 VM steps in the cost. [IMPL world_c1.py, DESIGN_C1 s1, c2c.json]

Organism (Player). A bytecode program (<= 96 instructions in C2 configs; init length 8-24) for an 8-register VM.
Registers reset every task; persistence across tasks only via the Workspace (data) and the BlockStore (executable
blocks), and in C2 via typed procedures (PREC_BEGIN/END record steps relative to an argument; PINVOKE h, a replays
them) and PSIM/PMATCH (apply a stored procedure "in the head" and compare). A substrate-maintained calibration
artifact exists in typed rungs (gives every acting typed candidate a constant reuse_gain of ~7). [IMPL vm.py, HIST]

Genotype -> phenotype: the program is the genotype; the phenotype is the lifetime trajectory (actions, workspace
writes, blocks created/invoked) over 50 tasks. Deterministic in (program, stream seed). [IMPL/HIST]

Search: (8+24) truncation; children get 1-3 mutations (7 operators, shift-aware insert/delete keeping jump targets) and
with probability 0.3 a 1-8 instruction segment spliced from a donor (population, or in rung D the frozen PARTS). Each
iteration evaluates on rotating stream seeds; parents are re-evaluated; a child must also win an independent takeover
check on a third stream against the member it would displace (ties count as takeover). Arms: random initial
programs, seeded with ENUMERATE_VM (a hand-written enumerator with no workspace/artifact use), recombination. [IMPL
config; HIST terminal review s2.3]

Fitness. C0: C0_EFFICIENCY, a ratio of gained competence to spent budget (rewarded abstention -- LEDGER). C1+:
C1_FITNESS = solved_count + 0.5 * (1 - normalised charged cost), unsolved tasks charged their full budget,
competence first. [IMPL DESIGN_C1 s3; CORRECTION history]

Measurement of the target phenomenon: reuse_gain_t = cost_FRESH_t - cost_ACCUMULATED_t measured exactly (same program,
same task, empty vs accumulated workspace), plus RESET, SCRAMBLE, ABLATION (blocks removed by id), TRANSPLANT
(ARTIFACT vs CODE_ONLY vs ID_ONLY vs RECORD_IDS_ONLY vs synthetic stores). [IMPL/INTENT DESIGN_C0 C4-C5]

Lineage/provenance: CandidateReceipt ancestry per candidate; LINEAGE.md/PATH.md per run; replayable receipts. [IMPL/HIST]

Design vs implementation notes:
- Charter imagined players that "construct, organize, reuse, modify and recombine" state; the implementation offers
  rich store primitives, but the only demonstrated users are hand-written controls. [HIST]
- DESIGN_C0 C7 flags one associative primitive (WS_FIND) as an included convenience. [INTENT]
- Receipts carry code_dirty_crius: true caused by untracked run dirs, not modified code (terminal review s7). [HIST]

## 4. World capability audit

- Dimensions: 4 x Z_8 (RELAY) or 4 x Z_16 (C0). Non-spatial. Fully observed current/target; hidden dynamics
  (permutation and template library) are the learnable structure. [IMPL]
- Stochasticity: per-stream draws only; within a stream deterministic. [IMPL]
- Action complexity: 12 primitive actions + RESET. Temporal horizon: one task <= budget interactions; lifetime 50 tasks.
- Delayed consequences: only in the sense that early acquisition should pay later (the target phenomenon).
- Adversaries, multiple agents, ecology, resources, environmental change, open-endedness: none. Task diversity: one
  task family (reach target via composed hidden templates), varied by stream. World generation: parametric per-stream
  library draws from a frozen generator. Transfer between worlds: across streams (relabelling) by design.
- Toy assessment: a small, deliberately constructed procedure-reuse puzzle. Its distinguishing virtue is that the
  reused object is a FUNCTION (template x argument), not a datum, so table memorisation provably transfers nothing
  (D-witness, TABLE_MEMO fails). Its limitation is that the full reuse mechanism is a specific ~45-instruction
  program shape; the phenomenon space is essentially one mechanism. [IMPL + CODE-INFERRED]

## 5. Organism capability audit

- Instruction set: ~49 opcodes: integer/tuple arithmetic, comparisons, vector get/set, branches, INPUT of task fields,
  ACT/ACTI, workspace cells/streams/records/links/alloc/find, executable-block create/append/patch/copy/compose/delete/
  invoke/state, action recording; plus typed procedure ops in C2. Call depth 4. [IMPL vm.py]
- Memory: 8 volatile registers; persistent workspace (4096 bytes) and up to 32 blocks of 64 instructions. Writable,
  addressable, executable memory exists -- unusually rich for the program.
- Control flow: full branching and loops (programs often non-terminating; Artemis R-07: 52% of one-mutants broken or
  screened, mostly infinite loops). [HIST]
- Self-modification: blocks can be written and invoked (code-as-data), but the main program is fixed per lifetime.
- Internal simulation: PSIM/PMATCH explicitly offered at rung C. Planning: possible in principle (P_PLAN exists).
- Learning/adaptation: only through what the program writes to the workspace/blocks during a lifetime.
- Reproduction/recombination: imposed by search (mutation + splice). Communication, development: none.

Fighting chance: YES in the representational sense -- the substrate demonstrably EXPRESSES the reuse mechanism
(PROCEDURE_REUSE_C1 46.1 vs FRESH 20.7; P_REC_INV_PLAN +15.97 fitness, 10/10 streams). The question was never
capability but accessibility under (8+24) x 300 iterations. Whether a different search (directed, larger, with
neutral drift budget) would reach it is open -- see s9. [HIST + CODE-INFERRED]

## 6. Search and pressure mechanism

Novelty: random mutation, segment splice from population or PARTS donors; seeded arm from an enumerator. No novelty
search, QD, curriculum or LLM proposals. Pressure: the C1_FITNESS lifetime score on paired streams; the "learning to
learn" pressure is indirect (accumulated competence lowers later cost). [IMPL]

Collapse modes found (in order):
- C0: metric rewards abstention (QUIT-like programs win). [CORRECTION, LEDGER]
- C0x (exploratory charge-abstention): better brute-force enumeration orders and hard-coded action scripts memorising
  the search partition. [HIST]
- C1: stride-counter random walkers exploiting generous chain budgets (solve a third of chains by luck). [HIST]
- C1b (budgets cut): compressed counter enumerators; record-id clock (WS_REC_NEW ids leaking a ~5-bit counter). [HIST]
- C2 A/B: exploit lineages E1-E4 (block-id clock, recorded own random walk replayed ~800x, workspace-conditioned walk,
  record-id clock that RECORD_IDS_ONLY reproduces exactly). [HIST]
- C2 C/D: "invocation without content" -- full 32-block stores invoked dozens of times per lifetime with zero effect;
  typed ops persist as neutral hitchhikers. [HIST]
Bottleneck named by the seat: partial mechanisms have zero or slightly negative value (recorder alone -0.001,
invoker alone -0.002, pair +1.138, full +15.97 at 47 edits). Bottleneck named by Artemis R-07: not missing neutral
networks but directionless drift in a very large neutral set. [HIST]

## 7. Measurement / ruler stack

- Gate witnesses A-H before search (gate_c1.py): A QUIT < ENUMERATE; B unsolved charged; C/D integrity
  (TABLE_MEMO replays 0, NOCAL 0); E accumulated beats FRESH by >= 20% of FRESH cost (positive control); F artifact
  transplant beats CODE_ONLY; G ablation == CODE_ONLY; H >= 2 "rich" blocks invoked with >= 3 distinct arguments.
  Gate v2 separates the accessibility control (block control PROCEDURE_REUSE_C1 for E/H) from the causal control
  (P_REC_INV_PLAN for F/G). [IMPL/HIST]
- Qualification on sealed streams 201-203, A-J battery (ACCUMULATED, FRESH, RESET, SCRAMBLED, ABLATION, TRANSPLANT
  variants). [HIST]
- "Reproducible" = reuse_gain > 5% of FRESH charged cost AND ACC solved >= FRESH solved on all 3 sealed streams. [HIST]
- Path rulers (c2_path.py): time to first complete mechanism; survival of partial ops in the elite; selectable-foothold
  rate. Paired re-evaluation of every recorder/invoker step vs a neutral-edit base rate (c2_terminal.py). [IMPL/HIST]
- Exploit probes: TRANSPLANT vs ARTIFACT_only vs CODE_ONLY vs ID_ONLY vs RECORD_IDS_ONLY vs synthetic stores. [HIST]
- Essay rulers (proposed, untrusted by the author): assembly distance, accessible path length, valley depth, foothold
  density, semantic-link survival, accessibility ratio rho = V/(V + d_flat * c). [INTENT]

Known blind spots:
- The invocation log recorded register R0 as the argument for typed PINVOKE (defect; H count wrong on 09-19);
  repaired a3f6a4be0 with a regression test. [CORRECTION]
- The search's own fitness is unpaired across iterations; ties count as takeovers; unpaired foothold rates count
  stream luck (terminal review s2.2-2.3). [HIST]
- The typed calibration artifact gives every typed candidate reuse_gain ~7: "created an object" trivially true. [HIST]
- Empty records are free (zero bytes evade capacity), a value channel (CRIUS-28). [HIST]
- The essay's "accessible path length: undefined; no such path" ruler value is contested by Artemis R-07 (see s9). [CORRECTION]
- Accessibility rulers failed on a second (stdlib proxy) substrate: foothold .421 vs .437, d_flat, rho all ranked arms
  in the wrong direction (Artemis D004-01, #1129). [HIST, cross-seat]

## 8. Experiment inventory (campaigns)

### Campaign 0 -- adaptive workspace sandbox (2026-09-19)
- Question: can search discover programs that make later learning cheaper by acquiring reusable workspace state?
- World C0 (Z_16^4, 6 hidden ops); arms random and seeded (ENUMERATE); 3 seeds; 300 iterations; plus EXPLORATORY c0x
  (abstention charged). Freeze 68cc85ff9, config 65fd4678cbcdd9c5.
- Measurement: frozen C0_EFFICIENCY; controls; reuse_gain.
- Reported: assay valid (CACHE_REUSE/ADAPTIVE positive controls acquire state); search found no learning-to-learn;
  metric rewards abstention (best 5.5/50 tasks); c0x found enumeration orders and action scripts, none acquiring
  state; three named failure shapes (metric, search operator, world). REVIEW_PACKET_C0_2026-09-19.md.
- Later: preregistered predictions P1-P3 wrong (ENUMERATE solved 3/6 depth-4); hidden-scale world proposal withdrawn by
  operator ("a three-valued latent is a datum"). One packet mechanism claim ("BLK_NEW returns -1 -> RESET") was wrong
  (LEDGER). Label: REPORTED NEGATIVE/NULL (with INSTRUMENT FAILURE of the metric).

### Campaign 1 -- RELAY world, procedure reuse (2026-09-19)
- Question: does selection discover persistent machinery whose products reduce cost on novel tasks without losing
  competence? Arms random/seeded/recombination x 3 seeds. Gate PASS.
- Reported: positive control PROCEDURE_REUSE passes; search found stride-counter random walkers (27-31/50 sealed, vs
  predicted 20-24 for enumerators); no acquired-state effect. Q3/Q5 predictions LOST (LEDGER).
- Later: walkers diagnosed as exploiting generous chain budgets -> C1b. Label: REPORTED NEGATIVE/NULL (CONTAMINATED by
  budget exploit, then resolved by C1b).

### Campaign 1b -- D1 isolation (2026-09-19)
- Question: did generous budgets mask a gradient toward acquired state? Chain budgets cut (RANDOM < 5% on chains).
- Reported: NO; nine runs, no reproducible ACC > FRESH, no block invoked, winners are compressed enumerators; a
  record-id clock with negative reuse_gain (-5524). Frozen C1 family CLOSED. REVIEW_PACKET_C1B_2026-09-19.md.
- A packet draft typed counts "from impression" that were wrong (LEDGER); corrected before publication.
- Label: REPORTED NEGATIVE/NULL.

### Campaign 2 rungs A/B (2026-09-19)
- Question: does a substrate ladder that makes each reuse link cheaper (typed procedures + calibration artifact at B)
  expose a gradient? 18 runs.
- Reported: null; exploit lineages E1-E4 (clocks, replayed walk), E4 satisfies "reproducible ACC > FRESH with
  competence kept" by the letter only (RECORD_IDS_ONLY reproduces it). PARTS value landscape: one-link valley at B.
  R2, R3, R6 predictions wrong (LEDGER). REVIEW_PACKET_C2_2026-09-19.md.
- Rung C gate FAILED on E/H; driver nevertheless ran ~20 min of rung-C searches (skip rule checked receipt existence,
  not verdict); receipts deleted. PARKED (CRIUS-33).
- Label: REPORTED NEGATIVE/NULL (with one INSTRUMENT FAILURE caught and purged).

### Campaign 2 terminal round, rungs C/D (2026-09-23)
- Question: is the reuse chain ACCESSIBLE given typed procedures + in-head simulation (C) and the PARTS as splice donors
  (D)? Prereg cbf30a726; instrument repair a3f6a4be0; gate v2 7661050d9; closure 7069c0ce6.
- Arms: rung C and D x random/seeded/recombination x seeds 1-3, 300 iterations (18 runs; D random/seeded byte-identical
  to C, so 12 distinct).
- Reported: 0 reproducible candidates; 0 complete mechanisms; partial-op steps inside the neutral-edit null; R4 (null)
  survives, R5 LOST; of 1,771 PART-fragment children, retained fragments carried constants and digit loops, never a
  working typed link; disposition CLOSED -- ACCESSIBILITY FRONTIER MAPPED (c2_terminal.py from receipts;
  crius/runs/C2_TERMINAL_DISPOSITION_RECEIPT.json).
- Later: Artemis R-07 (worker claim, 09-28) argues the frontier is not an absence of neutral paths: 44% of one-mutants
  around the enumerator are neutral, a 41-neutral-insert path then +1.23 then +13.8 exists to the complete mechanism;
  the barrier is phenotype rarity/direction. The ledge value (+1.138) shrinks to +0.645 on fresh streams. Artemis
  FR-004 ("is the frontier a genotype-phenotype-map artefact?") remains RAW.
- Label: REPORTED NEGATIVE/NULL (the disposition is a mapped null; its mechanistic interpretation is CONTESTED).

### Post-closure essay (2026-09-24)
- "The Accessibility Frontier", docs/essays/accessibility-frontier.html + 2026-09-24-accessibility-frontier.md +
  SOURCES_accessibility-frontier.md; candidate "assembly-geometry principle"; proposed rulers; closing "controlled pair"
  experiment. Not an experiment. Label: n/a (interpretive output; one ruler value later contested).

## 9. False-positive / false-negative archaeology

Timeline 1 -- metric rewards abstention (C0).
claim (frozen C0_EFFICIENCY orders reuse > brute force > quitting) -> evidence (QUIT 3.00 above CACHE_REUSE 2.97;
search optimum solves 5.5/50) -> correction (C1 fitness charges unsolved tasks; c0x exploratory) -> status: a ruler
that inverted the target; caught by the seat's own baselines.

Timeline 2 -- walkers (C1).
claim (seeded arm will find enumerators at 20-24/50) -> evidence (27-31/50 by stride-counter random walks) -> challenge
(budget lets walks solve chains by luck) -> correction (C1b cuts budgets; walkers disappear) -> status: budget exploit;
no acquired state either way.

Timeline 3 -- clocks that look like reuse (C0 block-id clock, C1b record-id clock, C2 E1 and E4).
claim (E1: ACC 15/16/17 vs FRESH 0/0/0; E4: 3/3 sealed streams positive) -> challenge (synthetic empty blocks /
RECORD_IDS_ONLY reproduce the transplant exactly) -> correction (classified exploits; content test added to the
disposition rule as clause f) -> status: a recurring false-positive class: a monotone id counter in a persistent store
is "acquired state" by the letter of ACC > FRESH. Strong example of controls built from the real failure.

Timeline 4 -- rung-C gate H count.
claim (09-19: typed control fails H, rich blocks 0 on stream 302) -> challenge (terminal round audit) -> correction
(invocation log used R0, not parg; repaired a3f6a4be0; 302 shows 2 rich blocks) -> status: instrument defect, the E
failure on 302 was genuine (typed control solves 27/50 there). The gate was then re-split (v2) so a weak typed control
no longer blocks the world-level witness.

Timeline 5 -- searches under a failed gate.
claim (rung-C searches ran) -> challenge (gate verdict FAILED; driver checked receipt existence) -> correction
(receipts deleted, not cited; LEDGER) -> status: purged. Phase 3 relevance: skip rules must read verdict fields.

Timeline 6 -- "no accessible path" (the headline interpretation).
claim (essay s8: accessible path length "undefined; no such path was found to exist"; foothold density 0/19) ->
evidence (terminal review s2.2-2.4, paired re-evaluation vs neutral null) -> challenge (Artemis R-07: a
non-deleterious single-insertion path exists; the map is highly neutral; the barrier is direction/rarity) ->
correction (none applied to the essay; R-07 is a worker claim Artemis labelled unverified; FR-004 RAW) -> status:
CONTESTED. Both readings agree search did not reach the mechanism; they disagree on why.

False-negative regimes:
- Search budget was frozen and forbidden from increase: (8+24) x 300 iterations, ~7k candidates/run. R-07 says the
  doorstep genotypes are a vanishing fraction of a large neutral set; undirected drift at this budget is not expected
  to find them. The null is therefore conditional on a tiny search, which the closure text acknowledges ("further
  search would test search budget, not accessibility") but then treats as answered. [CODE-INFERRED + HIST]
- The neutral-edit null for "selectable partial" uses 8 ancestry steps per top1 and 3 sealed streams; a +0.001 step
  with 0 solved delta cannot be distinguished from a weakly positive foothold at this resolution. [HIST]
- Splice from PARTS took 1-8 instruction segments, while the typed link needs coordinated inserts (R6: 26 and 47
  edits); the donor experiment could only transfer fragments shorter than any working link. [CODE-INFERRED from
  splice_len [1, 8]]
- The ledge (+1.138) is weaker on fresh streams (+0.645, R-07), so the "cliff" geometry itself is measured with
  stream-specific noise. [HIST]

## 10. Research outputs

- crius/DESIGN_C0.md, DESIGN_C1.md, DESIGN_C2.md, CRIUS_C2_TERMINAL_PREREG.md -- preregistrations with dated addenda.
- crius/CRIUS_C2_TERMINAL_REVIEW.md -- terminal review (best single source).
- crius/runs/C2_TERMINAL_DISPOSITION.json/.md, C2_TERMINAL_DISPOSITION_RECEIPT.json -- machine disposition.
- crius/runs/C2_SUMMARY.md, CAMPAIGN_SUMMARY.md -- cross-run tables.
- crius/runs/parts_c2*/PARTS.md -- value landscape by construction.
- roles/Crius/REVIEW_PACKET_C0/C1/C1B/C2_2026-09-19.md, C2_TERMINAL_INTERIM and C2_TERMINAL_2026-09-23.md.
- docs/essays/accessibility-frontier.html, 2026-09-24-accessibility-frontier.md, SOURCES_accessibility-frontier.md.
- roles/Crius/RESEARCH_SLIDE_2026-09-18.md -- pre-charter prior-art check on SLIDE.
- roles/Crius/calibration/LEDGER.md -- 15 rows of wrong calls with changed practice.
- Cross-seat: Artemis selftest R-06/R-07, FR-001/FR-003/FR-004, D004-01; Atlas proposals naming Crius.

## 11. Journals, TODOs, pivots, abandoned branches

- Journals 2026-09-18/19/23/24/25 (not read in full).
- Pivots: C0 -> C1 (operator ruling: metric + world change; hidden-scale world withdrawn); C1 -> C1b (budget
  isolation); C1b -> C2 ladder (operator ruling); C2 -> PARKED (failed rung-C gate, CRIUS-33); PARKED -> CLOSED
  (operator terminal directive forbade parking); CLOSED -> essay (operator).
- BACKLOG_H0H5.md (41 lines) not read in detail; STATUS states no next executable action.
- Open operator questions (RESUME): re-charter vs lift vs retire; essays index; revision permission; broadcast.
  No answer found in the record. Aporia's essay review (#553 offer) -- no reply found after #554.
- No abandoned branches; one seat branch merged.

## 12. Lens inventory

Lens: "accessibility microscope for executable reuse" (Crius sandbox).
- Substrate: register-bytecode programs with persistent data workspace and executable block store (code-as-data).
- Organisms: Players = programs; lifetime of 50 tasks.
- Worlds: RELAY -- hidden relabelled primitives and hidden argument-relative procedure templates on Z_8^4.
- Pressures: lifetime competence-then-cost fitness on paired streams; substrate ladder (typed procedures, PSIM).
- Phenomenon family: acquisition -> retention -> addressing -> invocation -> composition of procedures during a
  lifetime ("learning to learn" in the narrow sense of reusable acquired procedures).
- Resolving mechanism: exact reuse_gain (FRESH vs ACCUMULATED), A-J battery with transplant/ablation/synthetic-store
  content tests, gate witnesses with separated positive and causal controls, paired re-evaluation of partial steps
  against a neutral-edit null, PARTS value landscape by construction.
- Resolution ceiling: one mechanism family; 3 seeds; 300 iterations; 3 sealed streams; partial-step effects of
  +-0.001 unresolvable.
- Noise sources: stream luck (handled by pairing), id-counter channels, the calibration artifact constant, broken
  loops (half of mutants).
- Architectural limitation: the measured phenomenon is one hand-designed mechanism; search is undirected and small;
  the world has one task family.
- Reusable: the A-J control battery and content tests (strongest anti-clock controls seen in this territory), gate v2
  separation of positive vs causal controls, paired re-evaluation vs neutral null, PARTS-by-construction landscape,
  RELAY's function-not-datum design.
- Toy-grade: the world's size and single task family; search scale.
- Unknown: whether the frontier is about neutral-network direction (R-07) or valley geometry (essay); whether any
  larger or directed search reaches the mechanism; whether accessibility rulers generalise (they failed on one proxy).

## Open questions / unknowns

1. Does the R-07 neutral path survive a real verification (not a worker claim), and does a directed or larger search
   follow it?
2. Would a budget sweep (forbidden under the charter) change the disposition, or does drift stay away from the
   doorstep as R-07's walks suggest (edit distance 26 -> 36-37)?
3. Does the "invocation without content" phenotype appear in other engines with executable stores?
4. Was the essay ever reviewed by Aporia or revised after R-07? No record found.
5. Operator questions Q1-Q4 in RESUME.md: unanswered in the record.
