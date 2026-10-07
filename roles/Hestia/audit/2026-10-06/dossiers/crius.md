# Hestia audit dossier -- crius (Crius accessibility-frontier engine)

Audit 1, 2026-10-06. Auditor: Hestia audit worker (G5c). Rubric: AUDIT_PLAN.md s2-s4.

VERDICT: SALVAGE_COMPONENT -- the evolving bytecode organism never reached the reuse mechanism (0 of 475,728 candidates), but the assay around it (the RELAY world, the A-J control battery, gate v2, the PARTS valley diagnostic and paired re-evaluation against a neutral-edit null) is the best accessibility ruler in the fleet and should be carried forward.

## 0. Identity

- Paths: crius/ (4114 tracked files: 47 code/design/config/test files, 4067 under crius/runs/). Seat: roles/Crius/ (33 files).
- Census: docs/fleet/fleet_state.json row "crius", kind research-engine, state DORMANT (last commit 7069c0ce6, 2026-09-23). The seat's own STATUS.md: "CLOSED 2026-09-23T10:23:47Z ... Not PARKED" (roles/Crius/STATUS.md:7-10).
- Tree read: worktree hestia-boot-2026-10-06 at 3fed30ac9; last commit touching crius/ or roles/Crius/ = 8ad374ed5.
- Directory census (git ls-files crius | cut -d/ -f1-3): 66 search_* run dirs (c0 x6, c0x x6, c1 x9, c1b x9, c2a/b/c/d x9 each), each ~51-61 files (RUN_META, iterations.jsonl, candidates.jsonl.gz, takeovers.jsonl, LINEAGE.md, PATH.md, REPORT.md, qualify_qual/*.json.gz x30 + SUMMARY.json); plus baselines_c0/c0x/c1/c1b, gate_* and parts_* dirs, and 5 top-level summaries.
- READ IN FULL: crius/world.py, world_c1.py, worlds.py, tasks_c1.py, DESIGN_C0.md, DESIGN_C2.md s0-s5, CRIUS_C2_TERMINAL_REVIEW.md, configs/c2d.json, runs/C2_SUMMARY.md (rungs A-C header), runs/CAMPAIGN_SUMMARY.md, roles/Crius/STATUS.md, calibration/LEDGER.md, RESUME.md s40-86, journal 2026-09-24 and 09-25.
- READ IN PART: vm.py:23-112 (opset), 287-309 (invoke), 419-560 (typed ops); search.py:34-160, 300-370; evaluate.py:29-60, 129-178; env.py:70-100; baselines_c1.py:98-318 (positive control); parts_c2.py:228-345 (planner parts); DESIGN_C1.md s1-s7; REVIEW_PACKET_C0 s0-s1; REVIEW_PACKET_C2_2026-09-19 s5 (exploit fossils E1-E4); essay docs/essays/2026-09-24-accessibility-frontier.md (grep of objections and the controlled-pair section).
- RESULT FILES I OPENED MYSELF: runs/C2_TERMINAL_DISPOSITION.json (parsed: 18 runs x 7208 candidates, verdict block); runs/search_c2c_recombination_s1/qualify_qual/SUMMARY.json (parsed: per-condition solved counts, causal costs); iterations.jsonl line count (300).
- NOT READ: workspace.py and artifacts.py bodies (only signatures), qualify.py, report.py, lineage.py, c2_path.py, c2_terminal.py, gate_c1.py, exploit_probe.py, baselines.py (C0 controls), tests/*.py, configs other than c2d, DESIGN_C2 s6-s9, CRIUS_C2_TERMINAL_PREREG.md, CHARTER_CAMPAIGN_0.md, REVIEW_PACKETs C1/C1B/C2_TERMINAL(+INTERIM), RESEARCH_SLIDE, BACKLOG, journals 09-18/19/23, any of the 4067 run files beyond those named above, the HTML essay. Numbers below attributed to those files are CLAIMED-by-seat unless I say I parsed them.

## 1. Mechanism (code, cited)

### 1.1 Worlds
- C0 world: objects in Z_16^4, six fixed hidden ops (three translations, two parity-conditional translations, one rotation) (crius/world.py:12-53). Tasks: reach target = composition(start), depth 1-4.
- C1/C2 world RELAY: objects in Z_8^4; 12 primitives INC/DEC/SWAP x 4 positions (world_c1.py:95-125); per-stream hidden permutation of the 12 action ids (world_c1.py:153-155, 195-198); per-stream hidden library of K=3 templates of 2-3 (kind, offset) steps, applied relative to an argument position (world_c1.py:128-131, 174-192). Tasks are chains of 1-4 (template, argument) pairs (tasks_c1.py:279-333). Lifetime = 50 tasks in stages A10 B10 C12 D10 E8.
- The world LEAKS its semantics on request: primitive_of_action returns the primitive an action performed (world_c1.py:157-160), exposed to the organism as INPUT last_primitive (env.py:97-98, vm.py:109-110).

### 1.2 The organism (Player VM)
- 8-register bytecode VM, values int or vector, programs <= 64-96 instructions of (opcode, a, b, c) (vm.py:23-26, configs/c2d.json "vm").
- Opset: 47 base opcodes (arith, vector, branch, INPUT, ACT/ACTI, 14 WS_* workspace ops, 13 BLK_* executable-block ops) (vm.py:29-77); rung B adds PREC_BEGIN/PREC_END/PINVOKE (vm.py:78-81), rung C adds PSIM/PMATCH (vm.py:82-83); mutation draws uniformly from the enabled set (vm.py:96-104).
- Persistent state across tasks: a costed Workspace (256 cells + streams/records/links within 4096 bytes) and a 32-block executable BlockStore (DESIGN_C0 s3; workspace.py:50-273 and artifacts.py:35-249 by signature only).
- Rung B substrate does acquisition FOR the organism: every executed action silently writes action-id -> primitive into a substrate-maintained calibration block (vm.py:423-472, "_calibrate"). PREC_END turns the recorded primitives into a typed procedure relative to the first step's position (vm.py:524-535). PINVOKE h,a replays it through the calibration inverse map (vm.py:504-512, 536-547).
- Rung C "mental simulation" is the world's own simulator: PSIM/PMATCH call world_c1.apply_primitive on the recorded steps (vm.py:490-497, 548-558). There is no learned model; the organism gets an exact forward model of its own recorded procedures for free.

### 1.3 Search (the only adaptive loop)
- (mu+lambda) = (8+24) truncation selection, 300 iterations, 1-3 mutations per child from 7 operators (replace / arg / const +-1,2 / insert / delete / swap / duplicate-segment) (search.py:78-155); recombination arm adds a 1-8 instruction segment splice on 30 pct of children, donors = population, plus the frozen PARTS at rung D (search.py:225-237, 311-315).
- Paired common-random streams per iteration and a takeover check on an independent stream before a child may displace an elite (search.py:324-363).
- Fitness (C1/C2): C1_FITNESS = solved + 0.5*(1 - charged/max_cost), unsolved tasks charged full budget (evaluate.py:29-37, 57). Competence is lexicographically first.

### 1.4 Instrument (the part that works)
- Conditions FRESH / ACCUMULATED / WORKSPACE_RESET / WORKSPACE_SCRAMBLED over a lifetime (evaluate.py:129-178); from a stage-D snapshot: ARTIFACT_ABLATION, ARTIFACT_TRANSPLANT, FULL_TRANSPLANT, CODE_ONLY, COMPUTE_MATCHED, STORAGE_MATCHED (evaluate.py:179-252, signatures; DESIGN_C0 s5). reuse_gain is measured exactly by deterministic re-run, not estimated (DESIGN_C0 s1 C4).
- Gate witnesses A-H (QUIT < ENUMERATE, unsolved charged, TABLE_MEMO cannot replay, E: accessibility control ACC >> FRESH, F/G: transplant beats code-only and ablation removes it, H: argument-varied invocation) with negative controls built to fail them (terminal review s1 IV).
- PARTS: hand-written partial mechanisms (recorder only, invoker only, planner only, pairs, whole) measured on 10 streams to map the value landscape by construction (parts_c2.py:25-345).

### 1.5 Documented claim vs code
- Claim "search discovers machinery that makes later learning cheaper" (charter). Code: the only components that make later learning cheaper are HAND-WRITTEN: ProcedureReuseC1 (baselines_c1.py:98-318: hand-coded inverse-model classifier at :107-123, depth-<=3 DFS planner at :255-274, block retire-on-contradiction at :291-293) and P_REC_INV_PLAN (parts_c2.py:305-335). Search never produced one. The seat says exactly this; no overclaim found.
- The positive control's "planning" is exhaustive enumeration of (handle 0..7) x (arg 0..3) pairs to depth 2 with an equality test against the target (parts_c2.py:228-279: nested PH/PA/QH/QA loops, PSIM, EQ). Addressing (L4) is done by brute iteration over small integer handle ids, not by any learned index.

## 2. Evidence (tiered)

OBSERVED (parsed by me from committed files):
- O1. C2_TERMINAL_DISPOSITION.json: 18 runs (c2c, c2d x random/seeded/recombination x s1-s3), 7208 candidates each, 10 qualified labels each; repro_positive = 0 and causal_ok = 0 in all 18; own_invocation_candidates per run 0-51 of 7208. Verdict block: R4_survives true, R5_survives false, c_partial_ok false, d_repro_candidates 0, disposition "CLOSED -- ACCESSIBILITY FRONTIER MAPPED".
- O2. search_c2c_recombination_s1 qualify SUMMARY.json: top1 solves 22/21/22 on sealed streams 201/202/203 under ACCUMULATED, FRESH, RESET and SCRAMBLED alike; causal remainder cost identical under ARTIFACT_TRANSPLANT, CODE_ONLY, ABLATION (51.4/51.9/49.3). Its reuse_gain 7.1-7.3 equals the seed ENUMERATE_VM_C1's (7.1-7.3), i.e. the substrate's calibration object, not organism content. PROCEDURE_REUSE_C1 on the same streams: ACC 48/48/41 vs FRESH 20/19/22, transplant remainder 30.6/30.1/48.1 vs CODE_ONLY 50.4/50.4/47.8. TABLE_MEMO_C1 reuse_gain negative (-14.8 to -16.4). RANDOM_C1 6/6/9.
- O3. CAMPAIGN_SUMMARY.md (C0-C1b, 30 runs x 7208): every C1/C1b run has q_reuse 0.0 except c1b recombination s3 (-5523.9, i.e. harmful); C0 seeded s1 shows 186.5 (the CRIUS-28 block-id clock, per the seat's E1 description); c0x random arms -57.1 to +20.6.
- O4. C2_SUMMARY.md PARTS table at rung C: P_REC dFit -0.001 (0/10 streams), P_INV -0.002 (0/10), P_REC_INV +1.138 (7/10, +1.1 tasks, 26 edits), P_PLAN -0.057 (0/10, 41 edits), P_REC_INV_PLAN +15.974 (10/10, +15.9 tasks, 47 edits from P_BASE, 64 instructions).
- O5. C2_SUMMARY.md rung A random s1: 2800/7208 candidates invoked a block, reuse 4192.4, fitA 7.23 vs fitF 6.20 -- a "reuse" signal from a 7-solve organism (seat classifies such rows as walk/clock exploits E1-E4; I did not read the probe files).

CLAIMED (seat prose I did not re-derive):
- C1. Paired re-evaluation of every recorder/invoker arrival step: rung C 6/13 "selectable" at +0.0004..+0.0011 fitness, 0 solved; rung D 3/6 at +0.001; neutral-edit null 0-3/8 also "selectable" (terminal review s2.3).
- C2. 1,771 PART-fragment splice children at rung D; 63 won takeover; 5 survived into final ancestry; only a bare `CONST R6, 4` paid (s2.4).
- C3. Children newly carrying a recorder improve on parent less often than other edits in 12/12 runs (s2.2).
- C4. Exploit fossils E1 block-id clock, E2 replayed random script (~800 invocations/lifetime, +0/+1/+1 tasks), E3 workspace-conditioned walk, E4 record-id clock reproduced exactly by RECORD_IDS_ONLY (REVIEW_PACKET_C2_2026-09-19 s5).
- C5. C0: the preregistered ratio metric rewarded abstention; a quitter scored 3.00 vs CACHE_REUSE 2.97 (LEDGER row 4).

DESIGNED (not run anywhere): the essay's "controlled pair" (same destination, same payoff, different assembly geometry; options A-G) (essay lines 198-212). RESUME.md names it the natural successor, outside Crius.

Calibration: the seat's LEDGER (roles/Crius/calibration/LEDGER.md) records 14 of its own wrong calls, including two packet counts typed from memory and later corrected by script, and a driver that ran rung C ~20 min under a FAILED gate (receipts deleted). This is unusually honest self-accounting and raises my confidence in the CLAIMED tier.

## 3. Matrix

### 3a. Combinatorial explosion and reachability

Side calculation (scratchpad crius_calc.py, using vm.opcode_names and OPSPEC; immediates in [-20,20], addresses < 96, 11 input fields):

    opcodes        rung A 47, B 50, C 52
    distinct instructions (one slot)   ~1.2e4 - 1.33e4  (log10 4.09-4.12)
    programs of length 19 (seed)       ~10^78
    programs of length 64 (control)    ~10^264
    programs of length 96 (cap)        ~10^396
    world objects RELAY 8^4 = 4096; C0 16^4 = 65536; hidden id permutations 12! = 4.8e8
    arg-normalised templates: 36 (m=2) + 432 (m=3) = 468 per library slot
    mental chain candidates with K=3, L=4: 12 / 144 / 1728 (depth 1/2/3)
    physical brute force to depth 3: 1884 applies; chain-2 needs up to 6 primitives: 3.26e6 sequences
    search effort, whole lane: 66 runs x 7208 = 475,728 candidates (~1e6 edits)

- Where it explodes: not in the world (4096 states is tiny), but in program space. The destination P_REC_INV_PLAN is 47 edits from the 19-instruction seed (O4). With ~1.3e4 instruction choices per slot, even granting a generous 1e-2 chance that a random edit lands in the right functional equivalence class, an unselected 26-edit path (recorder+invoker) has probability ~1e-52 per lineage; the lane explored ~1e6 edits. Without a gradient on the intermediates, the destination is unreachable by four dozen orders of magnitude. The measured hit rates agree: own-object invocations 0-51 per 7208 at rungs C/D (O1), < 2 pct at rung B (LEDGER R3), reproducible content-bearing ACC > FRESH 0/475,728.
- The reachability desert is precisely located (this is the lane's main result): the value landscape by construction is flat or slightly negative for every single link (-0.001, -0.002, -0.057), positive only for the pair (+1.138 at 26 edits) and large only for the whole (+15.97 at 47 edits) (O4). That is reciprocal sign epistasis in the seat's own words; a (8+24) elite with local operators and 300 generations cannot cross it.
- The planner itself explodes. The written planner enumerates (handle, arg) pairs: (H*L)^d with H=8 handles, L=4 args = 32^d mental candidates. d=2: 1,024 (~17k VM steps at ~17 steps per inner iteration, inside the 40,000 step budget); d=3: 32,768 (~650k steps, ~16x over budget). The step budget caps in-head composition at depth 2 for the bytecode control, and the Python control caps at depth 3 (baselines_c1.py:102). Neither can reach the chain-4 qualification family by planning without a heuristic.
- Fitness granularity desert: with 50-interaction chain budgets (configs/c2d.json "interactions_by_depth"), chains are unsolvable by physical trial, so the competence term (+1/task) is only reachable by organisms that already plan in the head; every earlier partial can earn at most the cost term (<= 0.5 per lifetime) (DESIGN_C2 s1). The seat measured the typed-op arrival steps at +0.001, inside the neutral null (C1).

### 3b. Cosplay vs foundation

- What gets called "learning to learn" here is, in every case where it exists, hand-coded: (i) an inverse-model lookup table (calibration) -- written by the substrate itself at rung B+ (vm.py:461-472), or by the Python classifier (baselines_c1.py:107-123); (ii) macro-operator recording (PREC_END, vm.py:524-535); (iii) exhaustive in-head DFS over macros using the world's exact simulator (vm.py:490-497; parts_c2.py:228-279). This is Korf-style macro-operator learning plus breadth-limited search, a 1970s-80s planning recipe. It is a legitimate, correct reuse mechanism; it is not a novel cognitive primitive, and nothing in Crius discovered it.
- What search actually produced: compressed enumerators (seeded arms track the seed: 20.7-22.0 vs seed 19.3 solved, O2/terminal s2.1), random walkers that solve chains by luck under generous budgets (LEDGER row Q3), and four exploit shapes that satisfy the letter of "ACCUMULATED > FRESH" via id clocks and replayed scripts (C4). At rungs C/D, "invocation without content": a full 32-block store invoked 43-49 times per lifetime with zero effect (terminal s2.1).
- Is the search loop a seed? No. It is a selection loop over a 7-operator mutation set with no credit below the lifetime score; its ceiling, measured, is "a better enumeration order". The substrate ladder made each link a single instruction and the ceiling did not move (O1).
- Honest credit: Crius never calls its search output reasoning. The cosplay risk is in the opposite direction -- the substrate quietly does acquisition (auto-calibration) and simulation (PSIM = world simulator), so even a positive result at rung C would have been a selection over pre-built cognitive organs, not their emergence. The seat flagged the calibration object as an instrument confound (reuse_gain +7 for every acting program, O2) but the deeper point -- that PSIM hands over a perfect world model -- is not foregrounded.

### 3c. Substrate bottlenecks

- Representation: linear bytecode with absolute branch targets; the planner is a nested-loop structure that local edits cannot build incrementally (essay line 188 concedes this). Typed links (recorder, invoker) are separate opcodes that must co-occur with matching registers to have any effect.
- Addressing: handles are small monotonic integers (DESIGN_C2 s0 "Block ids remain values"); this both enabled the id-clock exploits (E1, E4) and lets the control "address" by enumeration rather than retrieval. No content-addressed procedure lookup beyond WS_FIND over cells.
- Credit assignment: one scalar per lifetime (evaluate.py:57); no per-block or per-instruction credit, although the instrument already computes per-block ablation deltas (qualify field per_block_ablation_delta) -- the credit signal exists and is not fed to selection.
- Compositionality: BLK_COMPOSE concatenates; typed procedures compose only via PSIM chains inside one program. No higher-order procedures (a procedure that takes a procedure).
- Memory: 4096 bytes, 32 blocks, 64 instructions each -- not binding; capacity was never the limit (blocks filled to 32 only by no-op hoarders).
- World poverty: K=3 templates of 2-3 steps over 12 primitives; the whole reusable content of a stream is ~9 primitive steps. A complete learner saturates it in stage A (ACC 48/50). The world cannot distinguish "procedural reuse" from richer abstraction (no recursion, no parameters beyond one position, no conditionals inside templates).
- I/O: the world reveals what each action did (last_primitive), which removes the hardest part of acquisition (system identification).

## 4. Deliverable sections

### Discovery Approach
Crius asks whether mutation-and-selection over bytecode organisms, living 50-task lifetimes with a persistent workspace and executable block store, will discover machinery that makes later tasks cheaper because of what earlier tasks left behind. It measures that with an exact, deterministic control battery (FRESH vs ACCUMULATED, reset, scramble, ablation, transplant, code-only, compute- and storage-matched), hand-written positive and negative controls, and, in Campaign 2, a substrate ladder that makes each link of the reuse chain a single instruction, plus hand-written PARTS to map the value landscape. Three campaigns (C0, C1/C1b, C2 A-D) were run to preregistered dispositions; the lane is CLOSED.

### The Brick Walls
1. Assembly valley (reciprocal sign epistasis). Single links are worth -0.001 to -0.057; the pair +1.138 at 26 edits; the whole +15.97 at 47 edits (O4). Search: 0 reproducible content-bearing reuse candidates in 475,728 (66 runs). Number: 47 coordinated edits with zero intermediate credit vs ~1e6 edits explored.
2. Lifetime-scalar credit. The only selection signal is one number per 50-task lifetime; typed-op arrivals score +0.0004..+0.0011, inside the neutral-edit null (C1). The instrument computes per-block causal deltas that selection never sees.
3. Planning is brute force with a hard step ceiling. Even the hand-written destination composes by exhaustive (8 x 4)^d enumeration: depth 2 = 1,024 candidates fits, depth 3 = 32,768 (~16x the 40,000-step budget) does not. The "reasoning" at the top of the ladder is BFS over a learned macro table.
4. Metric attack surface. Each preregistered metric was gamed: the C0 ratio metric selected quitting (quitter 3.00 > CACHE_REUSE 2.97); the C1/C2 criterion "ACC > FRESH" was satisfied by record-id and block-id clocks (E1, E4) until a content test was added. Any successor inherits this lesson: the criterion must include synthetic-store and RECORD_IDS_ONLY controls.
5. Substrate does the cognition. Auto-calibration (vm.py:461) and PSIM (vm.py:490) give acquisition and an exact forward model for free; a success at rung C would not have evidenced their emergence.

### Seed Viability
The organism is a DEAD_END as built, by the seat's own preregistered rule and the forbidden-move list (STATUS.md:43-47; terminal review s5, s8), and I agree: the failure shape is identical at every rung and arm, so more budget would test budget, not structure. The SALVAGE is the assay: (a) the RELAY world, which cleanly separates procedure from datum (a solved-pair table transfers nothing; TABLE_MEMO reuse_gain is negative, O2); (b) the A-J control battery with exact reuse_gain and the content tests (synthetic stores, RECORD_IDS_ONLY) that killed four exploits; (c) gate v2 with separate accessibility and causal controls; (d) the PARTS-by-construction value landscape plus paired re-evaluation of arrival steps against a neutral-edit null. Together they form an instrument that WOULD detect a real reuse circuit if one arose in another substrate and would reject the clock/walk/hoarder cosplay that most engines would report as success. Liftable whole (RESUME.md:62-66).

### Evolutionary Roadmap
The seed to scale is the ruler, applied as the essay's controlled pair, with the search substrate replaced rather than tuned.
1. Refactor the instrument into a substrate-agnostic harness: a Player interface (run(env, store)) plus the A-J battery, gate v2 witnesses and PARTS-landscape scorer, with RELAY as the reference world. Remove the two confounds: no substrate auto-calibration and no PSIM backed by the world's simulator; any forward model must be built by the organism from its own observations (or the experiment declares the organ as given).
2. Replace linear bytecode with a representation whose variation operators move semantic units: a typed lambda calculus / typed graph-rewriting genome where a procedure is a first-class closure (procedure, argument) and composition is application. Grow the operator set by MDL-driven library learning over the population's own successful traces (DreamCoder / Stitch-style abstraction: compress repeated subtraces into new primitives when total description length drops). This is option F (one operation creates coupled components) done generically, not by hand-inserting a REC+INV opcode.
3. Feed the instrument's credit to selection: per-block ablation delta and transplant gain as local credit (option E), i.e. compositional credit assignment -- a block is paid for the marginal cost reduction it causes on later tasks, measured by the same counterfactual re-run the battery already performs.
4. Multi-agent dynamics to cross the valley: a two-guild ecology with a shared procedure market -- "recorders" paid when another organism's invocation of their procedure solves a task, "invokers/planners" paid for solving -- so each link is independently the best thing to be in its niche (options A/B). Measure with open-endedness metrics (library growth, reuse depth, MODES-style novelty/complexity of the shared library), not only lifetime fitness.
5. Make the world richer only after (1)-(4): templates with internal conditionals and parameters, so that a macro library plus BFS is no longer sufficient and an abstraction hierarchy pays.

THE ONE DECISIVE EXPERIMENT. Controlled pair on RELAY, same destination (P_REC_INV_PLAN behaviour: ACC solved >= 35/50 with transplant > code-only), same payoff (C1_FITNESS), two assembly geometries: ROUGH = current C2-C bytecode with calibration and PSIM REMOVED from the substrate (organism must build both); SMOOTH = same opset plus a generic MDL library-learning operator (abstraction over the population's own successful action traces, no knowledge of store/lookup/replay) and per-block ablation credit added to fitness. 9 runs per arm (3 seeds x random/seeded/recombination), 300 iterations, 7208 candidates, qualified on sealed streams 201-203 with the full battery, content tests and the neutral-edit null.
Kill criterion: if SMOOTH yields 0/9 runs with a candidate passing gate clauses d-f (reproducible ACC > FRESH by > 5 pct of FRESH cost, transplant > code-only, synthetic stores do not reproduce), the assembly-geometry hypothesis is dead for this destination and the lineage should stop building evolutionary reuse substrates. If SMOOTH >= 3/9 and ROUGH 0/9, geometry decides and the representation in (2) is the seed to scale. Pre-register both before code, as Crius did.

## 5. What would change this verdict

- Toward VIABLE_SEED for the organism: a committed run in which a searched (not hand-written) Crius program passes clauses d-f on sealed streams -- none exists (O1, O3).
- Toward DEAD_END for the instrument: evidence that the battery misclassifies -- e.g. a candidate that passes d-f yet whose gain is reproduced by a synthetic or id-only store not in the battery, or a hand-written reuse control that the battery fails. The terminal review's validity fixtures (tests/test_c2_terminal.py) claim the opposite; I did NOT read the tests, so this rests on the seat's report plus the O2 rows (TABLE_MEMO negative, control strongly positive, enumerator flat).
- Toward INSUFFICIENT_EVIDENCE: if the CLAIMED paired re-evaluation (C1) or PARTS numbers were found not reproducible from the committed receipts (I parsed the disposition JSON and one SUMMARY.json, not the per-step re-evaluations).
- Auditor caveat: same model family as the seat author; the seat's narrative is persuasive and I may have under-attacked it. An independent reviewer should specifically test whether the 47-edit distance (parts_c2.edit_distance) is a fair lower bound on the shortest path, since a shorter spelling of the mechanism would weaken Brick Wall 1.
