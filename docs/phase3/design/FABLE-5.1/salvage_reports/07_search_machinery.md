# Salvage worker report: scope 7, search, evolution and generation machinery

Deposited by Dionysus[m1-3815a3b9] on 2026-10-01. Extracted by script
(process/deposit_worker_reports.py) from the coordinator's session transcript:
the worker's final message, recorded 2026-10-01T15:35:53.533Z. The text is the worker's,
unchanged except that XML escapes from the notification wrapper are undone
and trailing whitespace is stripped.

The same worker sent an earlier message (2026-10-01T15:24:03.086Z). This one
replaced it after the coordinator's search-rule correction. The earlier text
is not deposited.

Brief: roles/Dionysus/prompts/2026-10-01_salvage_workers/00_COMMON.md and
07_SCOPE_search_machinery.md. Worker model: opus, read-only.
Worker usage as reported by the harness: 648,963 tokens, 206 tool uses, about
39.2 minutes (totals for the worker, all messages).

This is a worker's fact sheet. Its claims are the worker's, graded by its own
VERIFIED BY ME lines. Where SALVAGE_MATRIX.md relies on one, it says so.

----------------------------------------------------------------------

I have everything needed, including a clean recount for Icarus (15 test functions, all in agents/icarus/tests_harness/test_caliber.py). Composing the report.

===BEGIN REPORT===
SALVAGE FACT-FINDING, SCOPE 7: SEARCH, EVOLUTION AND GENERATION MACHINERY
Worker for Dionysus[m1-3815a3b9]. Worktree F:\Prometheus-worktrees\dionysus-base-role at e3d7c7034.
Read only. Nothing was run except git, wc, and Python one-liners that read committed files.
Exclusion compliance: read SURPRISES 1 to 3 first. Two earlier commands reached holdout-named files, which affected one number (now corrected). The mandated exclusion patterns also have two technical gaps.

----------------------------------------------------------------------
COMPONENT 1a: Archaeon WSE GA loop, reachability table, typed disposition ladder
PATHS: archaeon/wse/evolve.py, archaeon/wse/reachability.py, archaeon/wse/states.py, archaeon/wse/worlds.py, archaeon/campaign2/REACHABILITY.jsonl, archaeon/campaign4/c4_05.py
OWNER / DATES: Archaeon. evolve, reachability, states: 2026-09-16 to 2026-09-17. archaeon/wse: 2026-09-16 to 2026-09-26.
WHAT IT REALLY DOES: A generational GA over Proteus player manifests. Elitism 4. Every other slot is a child of a tournament-4 parent and a tournament-4 mate, made by proteus.foundry.lineage.descend (one grammar-v0.4 mutation; splice uses the mate). Children never compete with their parents, so neutral and worse children always enter. The RNG is keyed on (campaign seed, world, regime, cell seed), so arms share streams (CRN). Each generation uses fresh episodes from the "train" family. reachability.py labels each run FLOOR, SHELF or SUMMIT (SUMMIT needs held-out >= 0.90). It then pools runs per (cell, N, G, E, regime, foundry) into COMMON, REACHABLE, RARE or OBSERVED_UNREACHABLE_AT_BUDGET, with Wilson bounds and right-censoring. states.py computes typed states (TARGET_UNREACHABLE, READOUT_CANNOT_EXPRESS, POSITIVE_CONTROL_FAILED, UNDERPOWERED) before any disposition (INCONCLUSIVE < CAPABLE_NEGATIVE < WEAK_POSITIVE < SUPPORTED_POSITIVE). c4_05.py runs bounded neutral walks: an edit is accepted only if the walker stays inside the parent's equivalence band.
SIZE: archaeon/wse 16 files, 3,333 lines (campaign4 4,902; campaign5 3,138). Tests in archaeon/tests: test_wse.py 8, test_campaign2_machine.py 16, test_campaign3_machine.py 6.
DEMONSTRATED CORRECTNESS: test_wse checks survey cells against an independent reference, that positive controls solve and nulls do not, and that run_cell is deterministic. Known defects:
- A no-op child self-loop invalidated v01 ancestry depth (comment at evolve.py:349-350).
- 16-episode training luck: .9375 on training, .53 held-out (reachability.py docstring).
- Pre-solved C4-09/C4-10 worlds, and takeover by incompetent imports (dossier).
INTERFACE: Evolution(spec, regime, campaign_seed, cell_seed, N, E, ...).run(G) returns the elite, its ancestry and a trace. Deterministic. Integer VM, float fitness. No checkpoint. No model call.
THROUGHPUT / SCALE:
- wse-survey-v01 RUN.json: 126 runs x 100 generations x N 200 = 2,520,000 evaluations (24 episodes each) in 1,531.6 s on 24 processes, M2. That is 1,645 evaluations/s (code-inferred).
- REACHABILITY.jsonl: 1,277 rows; sum of N x G = 22,585,600.
COUPLING: imports proteus.foundry (Player, generate, descend, prng). Imported by 7 files outside archaeon/ (Nestor CW01 arch4, Odysseus, evidence_wiki/ew/campaign_ingest.py). Pure Python.
FIT TO SLOT: SEARCH protocol; blind-variation regime.
- Meets as is: SRCH-05 (separate train and held-out episode families).
- Meets in part: SRCH-01 (keeps a population, accepts neutral moves); SRCH-02/04 (budget-indexed reach classes, but the targets are world cells, not planted organisms); SRCH-06/11 (seed-keyed generation 0, origin tags, offspring cap).
- Fails: COMP-01, SRCH-03, SRCH-08, SRCH-09. evaluate() is welded to the Proteus manifest.
MODIFICATION COST: M (organism and world protocols, integer fitness, planted-target curves). Rebuild: the loop is S; reachability plus typed states is M, copying this design.
VERIFIED BY ME: the loop, CRN keying, family split, reach classes, state vocabulary, row and evaluation sums, survey wall time. Campaign outcomes are from the dossier.

COMPONENT 1b: Archaeon Deep Frontier lineage scheduler (and the Z80 x Atlas campaign scheduler)
PATHS: archaeon/frontier/scheduler.py, archaeon/campaign6/segment.py, archaeon/frontier/digest.py, archaeon/frontier/registry/EVENTS.jsonl, archaeon/z80atlas/scheduler.py, archaeon/z80atlas/engine.py, archaeon/z80atlas/grammar.py
OWNER / DATES: Archaeon. frontier 2026-09-18 to 2026-09-26; campaign6 2026-09-18 to 2026-09-19; z80atlas 2026-09-19 to 2026-09-23.
WHAT IT REALLY DOES: The frontier schedules experiment specs ("lineages"); it is not an organism optimiser. Each spec runs campaign6.run_segment: the same GA as 1a (elite 4, tournament 4, descend with mate) at N 32. N 32 is code-inferred: 119,936 evaluations over 3,748 generations in the digest. Segments are checkpointed in and out, and chunk 0 is run twice and digest-compared (replay A, scheduler.py:143-145). Branching follows detector firings.
Z80 x Atlas is different: it samples world, physics and pressure factor vectors (exploration floor 0.30) and runs a 128-cell self-copying byte-VM ecology per spec. It promotes families by flag weights; mutation and crossover act on factor vectors, not on organisms.
SIZE: frontier 18 files, 2,169 lines; campaign6 2,217; z80atlas 3,148. Tests: test_frontier_suppression_logging.py 3; z80atlas tests 33.
DEMONSTRATED CORRECTNESS: segment self-test and replay-A digest equality. Known defects:
- reward_max_over_run is the population's training reward (digest.py:68-74, segment.py:318-320).
- Detectors saturated: structural_reuse fired 1,658,614 times over 3,719,136 evaluations (DIGEST_2026-09-21T2054Z.md).
- run_id was a hidden seed (DF-015), and all 26 of 26 spontaneous-replication flags were transplants (both from the dossier).
INTERFACE: python -m archaeon.frontier.scheduler, or archaeon.z80atlas.scheduler with --start or --resume. Deterministic, resumable, no model.
THROUGHPUT / SCALE:
- Frontier registry: 130 RUN events, 4,099,920 evaluations, 2026-09-18T23:39:59Z to 2026-09-22T19:07:51Z. Per-run wall_s is written under archaeon/frontier/runs/, which is gitignored, so it is not recorded in the repo.
- Z80: 101,003 runs in 71.63 h on 24 workers, M2 (STATUS.json, grammar.py). That is 0.392 runs/s. Each run has a budget of 60,000,000 to 150,000,000 VM steps.
COUPLING: archaeon.wse, archaeon.campaign4, proteus. Windows Task Scheduler on M2. Receipts sit in ignored paths.
FIT TO SLOT: SEARCH protocol, runner side. Meets COMP-02 in part (checkpoint, resume, replay). Fails:
- SRCH-05 for its reported maximum (a training reward).
- PROV-03 (receipts in an ignored path).
- ANTI-02 (the ADMITTED ruler set is a constant at scheduler.py:178, per dossier).
- SRCH-09.
MODIFICATION COST: L (tracked receipts, typed admission, drop promotion-by-flags). Rebuilding a checkpointed segment runner: M.
VERIFIED BY ME: segment GA, replay A, the source of the digest's maximum, registry sums, Z80 status and constants, the gitignore. From the dossier: the ADMITTED tuple and the Z80 transplant defect.

COMPONENT 2: PROTEUS-46 greedy walk, its successor, and the mutation-kernel crucibles
PATHS: proteus/round2/falsifier_46.py, proteus/round2/PROTEUS-46_FALSIFIER.json, proteus/foundry/grammar.py, proteus/foundry/lineage.py, proteus/v0_6/livekernel.py, roles/Artemis/dispatch/D002/scripts/D001-03.py, roles/Artemis/dispatch/D002/RESULT.md
OWNER / DATES: Proteus. falsifier_46.py 2026-09-18 only; proteus/v0_6 2026-09-03 to 2026-09-11. Successor script by an Artemis worker, 2026-09-30.
WHAT IT REALLY DOES: For one hand-written parent per substrate (v0 tape VM, graph organism) it makes 400 children per operator and classifies each on a two-key probe. It then runs 200 random 3-step walks and 100 greedy 3-step paths of width 50 per substrate.
- The greedy step starts at best_key = (cur, 0) and scores children (two_key, -ops). A child with an equal score and ops > 0 can never win, so neutral moves are rejected by construction (lines 117-128).
- The sampled neighbourhood was full of neutral children: graph one_value 3,132 NEUTRAL of 4,881; v0 one_value 1,169 of 4,267 (JSON).
- Nothing in proteus/ replaced the walk. The only successor is D001-03.py (241 lines; neutral-accepting drift walks plus a small truncation population; not run by its author). RESULT.md D002-03q (quick mode): a 5-edit neutral path exists; drift 'score' hit 1 of 50 (step 188), 'strict' 0 of 50, control 0 of 50; a population of 50 x 100 generations never reached 6/6; the full run timed out.
- The crucible (v0_5, v0_6) estimates the unselected grammar's Markov kernel over 2,044 structural states by executing mutate.
SIZE: falsifier_46.py 227 lines; proteus/v0_6 3,484 lines; 363 test functions in proteus (3 for the falsifier).
DEMONSTRATED CORRECTNESS: preregistration committed before any child (eb58691fc, dossier). Defects: neutral rejection; walk length 3 is shorter than the 5-edit path; the kernel's reversible-reference control cannot fail (Harmonia ruling, dossier).
INTERFACE: a script. Deterministic (SplitMix64), integer genomes, no model.
THROUGHPUT / SCALE: 20,000 neighbourhood mutate calls, plus 30,000 greedy child evaluations and 400 walk end points (code-inferred from the parameters). Wall time not recorded. M2.
COUPLING: proteus.foundry, graph and eval only. The frontier suppression PROTEUS-46 still applies (dossier).
FIT TO SLOT: no regime; it fails SRCH-01 by construction. Keep it as a failure fixture. The per-operator census is a reusable single-edit probe for SRCH-03.
MODIFICATION COST: S to fix (accept ties, longer walks), but it is not worth keeping as a regime. Crucible: L to port; rebuild M.
VERIFIED BY ME: walk code, JSON counts, the D002 line, parameters. From the dossier: the ruling and the 299,991 suppression rows.

COMPONENT 3: Crius (8+24) accessibility-frontier search and neutral-path measurements
PATHS: crius/search.py, crius/configs/c2c.json, crius/parts_c2.py, crius/c2_terminal.py, crius/c2_path.py, crius/runs/
OWNER / DATES: Crius (M2); 2026-09-18 to 2026-09-23.
WHAT IT REALLY DOES: (mu+lambda) = (8+24) truncation over bytecode programs for a register VM with a workspace and an executable block store.
- Variation: each child gets 1 to 3 of 7 mutations. In the recombination arm, with probability 0.3 it also gets a 1-8 instruction splice from the population or from frozen PARTS.
- Selection: parents are re-evaluated on each iteration's rotating streams. Ranking is by fitness, then SHORTER length, then hash. Any genotype seen before is skipped. An entering child must also win a third-stream takeover check, where ties count as a takeover.
- Consequence (code-inferred): an equal-fitness child enters only if it is shorter or wins on hash, so neutral insertions are disfavoured.
- Arms: random; seeded (one ENUMERATE founder plus its mutants); recombination.
- c2_terminal.py re-evaluates up to 8 top-1 ancestry steps that add no typed op, as a neutral-edit null.
- parts_c2.py holds 7 frozen designed partial organisms (P_BASE to P_REC_INV_PLAN), with an ancestor map, paired selective value and edit distance.
SIZE: crius/ 5,993 lines; search.py 413; 41 test functions.
DEMONSTRATED CORRECTNESS: gate witnesses A to H before search; sealed qualification streams 201-203; receipts with a replay hash. Defects: PINVOKE logged R0 (repaired a3f6a4be0); rung-C searches were run under a failed gate and then purged (dossier).
INTERFACE: python -m crius.search with --config, --seed, --arm and --workers. Deterministic per seed (code-inferred). Integer VM, float fitness. No model.
THROUGHPUT / SCALE: 66 runs x 7,208 candidates = 475,728. Summed elapsed 49,132.4 s; slowest run 1,805.1 s, fastest 48.6 s. 9.68 candidates/s summed. M2. Worker count not recorded.
COUPLING: self-contained; uses multiprocessing.
FIT TO SLOT: REACH and descent inputs. Meets SRCH-02 in part (designed partials at graded distance) and SRCH-05. Fails:
- SRCH-01: the length tie-break and the seen set work against neutral drift.
- SRCH-04: the budget is frozen at 300 iterations.
- SRCH-06: the seeded arm has one founder.
- COMP-01.
MODIFICATION COST: M to extract the loop and receipts; the loop alone rebuilds in S. Copy the PARTS ladder, the A-J battery and the neutral-null designs (S to M).
VERIFIED BY ME: loop, ranking key, seen set, takeover tie rule, config, PARTS, neutral null, run sums, tests. From the dossier: campaign outcomes and Artemis R-07.

COMPONENT 4: Tyche lexicase selection, graft and fusion, the reserve, the natural-history tracer
PATHS: tyche/ecology.py, tyche/run_v0.py, tyche/lens.py, tyche/v1/eco_v1.py, tyche/v2/eco_v2.py, tyche/v2/history_v2.py, tyche/runs/
OWNER / DATES: Tyche (M2); 2026-09-30 to 2026-10-01.
WHAT IT REALLY DOES: Evolves "lenses": feed-forward register programs of at most 48 ops drawn from 27, over float time series. Each generation:
- Elites: the best lens per (world, ruler) on the 'all' scope, capped at 24.
- Reserve: 14 slots (0.15 x 96). Age-protected members first (3 generations), then 2/3 by novelty (mean L1 distance to the 5 nearest signatures), then 1/3 random.
- Offspring: parents chosen by epsilon-lexicase (MAD epsilon per case) over gains per (world, ruler, organism, scope) on the val split. 25% are grafts (a donor's output cone is appended), the rest mutants.
- Offspring always enter, so neutral moves are accepted.
- Admission uses the conf split (z >= 4); reporting uses the test split, fresh seeds 101/102 and held-out worlds.
history_v2.py traces, per solved slot, the first functional carrier of each hidden precursor (using the answer key, tracer only), the generations it spent at zero utility, and why each ancestor survived.
SIZE: 4,491 lines; 35 test functions.
DEMONSTRATED CORRECTNESS: a cheat control (the LEAD op must be caught) and a causality audit (tyche/audits.py). Defects: v0 manufactured residuals; the v1 V0 arm had an unlogged reserve; BLAS oversubscription (dossier).
INTERFACE: python -m tyche.run_v0 or tyche.v2.run_v2. numpy floats, sklearn organisms, seeded; BLAS pinning is needed for determinism. No model.
THROUGHPUT / SCALE: Block R DONE.json files: 36 runs, 1,800 generations, 162,973 lenses born, 240,206 units, 12,437.3 s summed. 13.1 lenses/s. M2.
COUPLING: hecate/alien/systems.py (read only). Imported by theseus/synth.
FIT TO SLOT: population search with a diversity archive. Meets SRCH-05. Meets SRCH-09 in part (elites per world x ruler; lexicase over a case vector). Meets SRCH-06/11 in part (roots tracked: v0 REPORT gives SURVIVING_LINEAGES 7 and FAILED_LINEAGES_COUNT 85; plus the tracer). Fails integer determinism, COMP-01 and SRCH-02.
MODIFICATION COST: eps_lexicase is 18 lines (S). The reserve and elite logic is inline in run scripts (M). The tracer is M. Rebuild: lexicase S, tracer M.
VERIFIED BY ME: lexicase, reserve, graft rate, replacement rule, splits, Block R sums, tracer docstring, tests. Defects are from the dossier.

COMPONENT 5: Theseus synth QD archive and collision operator
PATHS: theseus/synth/rulers.py (Archive), theseus/synth/ecology.py, theseus/synth/collide.py, theseus/synth/run_v0.py, theseus/synth/analysis.py, theseus/controls/llm_arm_v0/
OWNER / DATES: Theseus seat (host DESKTOP-RUAPVAI, 4 CPUs); 2026-09-30 only.
WHAT IT REALLY DOES: There is no fitness.
- Each generation, per lane x arity, a coalition is chosen (seed weighted 1/(1+uses); partners near, far, under-used or random in an 8-D field) and "collided".
- A collision splices contiguous rule runs with a channel shift, adds a react rule with fixed random per-parent gains, applies 1-3 edits and caps the result at 14 rules (collide.py docstring).
- Viable children join the pool.
- The Archive keeps the most reproducible member (quality = -rep_dist) per cell of 3 grids (7 bins per axis over a 34-dim behavioural fingerprint). It only protects members from fossilisation and is never used to pick parents.
- The same rulers also score one-shot arms (P, B, C), random R, a 60-genome Claude-written arm A, and controls.
SIZE: 3,299 lines; 10 test functions.
DEMONSTRATED CORRECTNESS: X gate 0/40 neutral programs viable; lineage 0 mismatches. HK 20/20 is self-referential (dossier). Defects: in v0, lens parents leaked into DEEP lanes and order depended on PYTHONHASHSEED (amendment 308330aaf). No bitwise rerun has been done.
INTERFACE: python -m theseus.synth.run_v0. float64 dynamics; deterministic with PYTHONHASHSEED=0. No model in the loop (arm A was pre-written).
THROUGHPUT / SCALE: v0_1 REPORT.json phase walls sum to 2,190.1 s (ecology 1,203.0 s). About 2,580 genome evaluations (code-inferred), so about 1.2/s.
COUPLING: tyche.lens; agents/nous/src/concepts.py via git show; hecate programs.
FIT TO SLOT: P8 generator divergence, as a prototype: model-free and model-written arms share one DSL; the statistic is exclusive-cell counts against a 1,000-permutation null plus bootstrap distance CIs (analysis.py hard_test). The archive fails SRCH-09 (keyed by fingerprint, not by certified profile).
MODIFICATION COST: Archive about 50 lines (S). The hard-test statistic is S to M to port. The collision operator is welded (retire). Rebuild the archive: S.
VERIFIED BY ME: Archive, coalition rule, arm construction, REPORT numbers. The collision body is from its docstring only.

COMPONENT 6a: Apollo routing-DAG and blackboard evolvers, crossover, O1 enumerator, E1 schedule analysis
PATHS: apollo/src/blackboard_evolve.py, apollo/scripts/mutation_dryrun.py, apollo/src/apollo.py, apollo/src/task_manager.py, apollo/scripts/o1_enumerate.py, apollo/cycles/o1_enumeration/RESULT.json, apollo/scripts/e1_schedule_classes.py
OWNER / DATES: Apollo (M2). apollo/ 2026-03-27 to 2026-09-11; blackboard_evolve.py 2026-05-29 to 2026-06-27.
WHAT IT REALLY DOES:
- Branch C: MAP-Elites over pipelines of hand-written operators; the descriptor is the load-bearing core. Parents are drawn uniformly from archive occupants. A child replaces a cell's occupant only if strictly better on (composition score, accuracy, shorter), so neutral children in the same cell are dropped.
- Offspring per generation = pop_size (default 20). Moves: insert, remove, swap, swap_scorer, add_guard; optional recombine or dispatch_merge.
- --mode llm: with probability 0.5, mutate_llm asks a local Granite server (localhost:8800, temperature 0.3, 300 tokens) for ONE insert_step in a JSON DSL; otherwise the mutation is deterministic. LLM output is filtered by JSON parse, signature validation and a transformer-only role guard.
- v2: NSGA-II/III with LLM structural mutation.
- O1: exhaustive type-directed enumeration. E1: a static conflict graph plus executed schedule classes.
SIZE: apollo/src plus scripts 17,881 lines; 0 test functions outside the archive.
DEMONSTRATED CORRECTNESS: O1 positive control; E1 must rediscover a known write-write hazard. Defects (dossier): lineage wipe (e94ca44b1); an output-change gate (fixed 3ebdad8b4); blind battery E9 scored 0.0667 against 0.6000 at home.
INTERFACE: python -m blackboard_evolve with --mode deterministic or llm. Seeded random; nondeterministic in llm mode. Logging per generation is llm_used counts and lineage tags like "llm_insert:op@pos". No tokens recorded.
THROUGHPUT / SCALE:
- O1: 1,737,000 pipelines in 3,000.2 s (579/s); 1,687,896 to reach the ceiling, against 3,144 for evolution.
- llm2: 800 generations, 86,156 s, 2,152 LLM mutations (roles/Apollo/STARTUP.md:96-104).
- v2d2b: 1,175 generations, 2026-04-07 to 2026-04-11.
COUPLING: agents/hephaestus/src (forge_primitives, trap generator); a local GPU model server; run directories mostly untracked.
FIT TO SLOT: SRCH-08 in shape: deterministic, crossover, model-guided and exhaustive search all on one battery. ANTI-04 is present in code (llm_fraction 0.5). Selection and reporting use the same battery, so it fails SRCH-05.
MODIFICATION COST: XL to make relevant (the organism is a text-task pipeline). Retire the code; keep the O1 and E1 methods, which rebuild in M.
VERIFIED BY ME: loop, insert rule, LLM path, prompt, O1 result, llm2 record, v2d2b span. v2 details are from the dossier.

COMPONENT 6b: Lexis closure search
PATHS: roles/Lexis/instruments/product_ceiling_fast.py, product_ceiling.py, answer_slice.py, congruence_audit.py
OWNER / DATES: Lexis (M1); 2026-08-24 to 2026-09-11.
WHAT IT REALLY DOES:
- Stage 1, per task: BFS the answer-relevant closure of Apollo's deterministic operators (5,029 states over 120 tasks, at most 104 per task) and build transition tables.
- Stage 2: BFS the joint 120-tuple of task states. The reachable joint set is exactly what any program of any length, order or repetition can induce.
- The ceiling is the best-scoring joint state. There is no heuristic and no model.
SIZE: instruments 3,516 lines; 0 test functions.
DEMONSTRATED CORRECTNESS: two positive controls (the known organism scores 0.8333 both directly and via the tables; SESSION_2026-08-25.md). Defect: the LEX-07 cheat control was never run (dossier).
INTERFACE: a script, read only on apollo/. Deterministic, integers.
THROUGHPUT / SCALE: 484,218 joint states; frontier empty at depth 23. Wall time not recorded.
COUPLING: apollo/ operators and battery.
FIT TO SLOT: not a regime. It fits the REACH and DEMAND side: an exact bound for a fixed operator language (WLD-02 style), and ground truth for SRCH-02/03 calibration. It requires finite per-task closures.
MODIFICATION COST: M to port; rebuild M.
VERIFIED BY ME: method docstring and recorded numbers. I did not read the BFS body.

COMPONENT 7: Ergon E4 GA with a persistent genotype library on the D-5 machine
PATHS: agent_d5_blind/navigators/m0.py, agent_d5_blind/learner/m1.py, agent_d5_blind/developmental_history/run_m1_lineage.py, agent_d5_blind/developmental_history/run_alien_and_ablations.py, agent_d5_blind/substrate/rm_fast.py, ergon/gen1b/gen1_run.py, ergon/gen3/
OWNER / DATES: D-5 by the independent "Agent D-5"; E4 by Ergon (M1 per dossier); 2026-08-27 to 2026-09-11.
WHAT IT REALLY DOES:
- Per task (a 64-row function table): a GA of 32 programs (at most 24 instructions, 8 x 16-bit registers, 14 opcodes). Tournament 3 on Hamming distance, 50% crossover, 10% immigrants.
- Generational with no elitism, so neutral and worse children always enter. The M0a hill climber accepts ties (d <= best).
- In M1, half of the immigrants are mutated library genotypes. After each task the library admits the solver plus up to 4 behaviour-distinct best programs (cap 64; Ergon's arms vary eviction).
- Ablation libraries: size-matched random-walk genotypes (5 to 40 mutations from the seed repertoire), and libraries accumulated over a permuted task order.
- A budget ladder of 1,000 / 3,000 / 10,000 / 30,000 is read off the first-solve index.
SIZE: agent_d5_blind 2,285 lines; ergon gen1b to gen3 about 3,139 lines. Tests: ergon/gen1/tests/test_persistence.py 22; substrate/test_smoke.py 4.
DEMONSTRATED CORRECTNESS: the Numba path is checked equivalent to the reference VM, and every claimed solve is re-verified on the reference VM (assert in _Ctx.d). 290/290 rows reproduced and the cheat plant was detected at n 100 (dossier). Defect: the D-5 analysis script was never committed (dossier).
INTERFACE: m1_rx(view, rng, budget, library) returns solved, first_solve and evals. Deterministic, integer, no model. sys.path entries use Windows separators ('..\\substrate'); code-inferred Windows-only.
THROUGHPUT / SCALE:
- P3: 193,207,377 evaluations summed from the 400 committed row files (8,400 task rows) in 13.9 min on 8 workers (REVIEW_PACKET_P3:128). That is 231,663 evaluations/s.
- Gen-1B: 151,200,000 (the budget-cap product) in 48.6 min.
COUPLING: numba only.
FIT TO SLOT: blind-variation regime. Meets SRCH-04 (per-task budget ladder) and follows the COMP-01 pattern (compiled kernel plus a reference equivalence check). Fails SRCH-06 (every lineage starts from one seed repertoire), SRCH-09 and SRCH-02.
MODIFICATION COST: M (protocolize the physics and FastTask, optional elitism, receipts). Rebuild: S to M.
VERIFIED BY ME: GA, tie rule, admissions, ablation construction, ladder, P3 sums. Verdict numbers and host are from the dossier.

COMPONENT 8: Aphrodite enumerative search with escrow metering and keyed common random numbers
PATHS: roles/Aphrodite/engine/fair.py, engine.py (Escrow), improver.py, basis_v4.py, accel/BACKEND_RUN_cpu_pool3_M4.json, S4_RESULTS_2026-09-23.json
OWNER / DATES: Aphrodite (M4); 2026-09-21 to 2026-09-28.
WHAT IT REALLY DOES:
- Walks a finite integer-fold DSL, first in library order and then through a complete fallback. Each candidate costs one escrow charge; the escrow raises when exhausted.
- Accepts the first program consistent with all dev examples.
- Lists are ordered by sha256(seed, slot, item), so identical libraries walk identical sequences and arms are paired (keyed CRN).
- select() keeps a library only if the one-sided 95% lower bound of its mean paired saving against PRISTINE is above 0.
- No population. The improver is immutable code.
SIZE: engine 14,855 lines; fair.py 185; 50 test functions.
DEMONSTRATED CORRECTNESS: a conformance gate between two evaluators; the accel backend matched the reference on 480/480 rows. Defects: constant-True gate conditions (run_s3s4.py:391 and :420; a16.py:490; a17.py:581, dossier).
INTERFACE: KLib.candidates(seed), Cell.cost(lib), select(). Deterministic, Python integers, no model.
THROUGHPUT / SCALE:
- Accel receipt: 106,839,976 charges in 429.9 s on 3 workers, M4. That is 248,523 charges/s.
- S4_RESULTS: 324,949,606 charges summed over 1,344 rows; no wall time recorded.
COUPLING: stdlib only.
FIT TO SLOT: SEARCH protocol accounting. Meets SRCH-04 (enforced evaluation budgets), COMP-05 at evaluation level, paired CRN for SRCH-08 comparisons, and SRCH-03 (first-hit position under a fixed order). Not a regime for organisms.
MODIFICATION COST: escrow, keyed ordering and paired summary are S to extract; the enumerator is welded to the DSL (L). Rebuild: S.
VERIFIED BY ME: fair.py, Escrow, receipt sums. Defect lines are from the dossier.

COMPONENT 9: Ananke GA (population 96 x 36 generations), shaping terms, plants the search never found
PATHS: prometheus/ananke/search.py, prometheus/ananke/campaign.py, prometheus/ananke/plants.py, roles/Ananke/pte/c1_rows/cells.jsonl.gz, roles/Ananke/pte/C1_ERRATA.md, roles/Ananke/research/harvest/H-PLANT/
OWNER / DATES: Ananke (M1); search.py 2026-09-24.
WHAT IT REALLY DOES:
- Random integer genomes [G, L, 5]; 8 fresh training worlds per generation.
- Fitness = accuracy + 0.10 x max(twin contrast, 0) + 0.02 x sens_any. The shaping terms are used for selection only.
- Truncation 25%, elite 4, uniform crossover 0.30, per-field resample 0.04, whole-instruction resample 0.15, swap 0.10. Children always enter.
- The champion is chosen on training accuracy over 16 fresh worlds, then evaluated once on 64 held-out worlds (disjoint seed namespace) with a zero-communication control.
SIZE: search.py 149 lines; 164 test functions in prometheus/ananke, none dedicated to search.py.
DEMONSTRATED CORRECTNESS: an independent CPU oracle written from the spec; conformance tests. Plants the search never found:
- XOR plant .850 [.819] against the champion's .503 (C1_ERRATA E-W23).
- FLIP plant .978 [.962, .990] (H-PLANT PRINCIPAL_REVIEW) against search .479 (dossier).
Defect: shaping raises sensitivity, not accuracy, and C1 has no shaping-off arm (E-W10, dossier).
INTERFACE: evolve(ph, env, seed, SearchSpec). Deterministic, integer tensors, GPU, no model.
THROUGHPUT / SCALE: C1 has 678 evolve cells x 29,312 = 19,873,536 world-episodes. Summed wall_s is 31,488.4 (cells.jsonl.gz; receipt host SKULLPORT). That is 631 world-episodes/s.
COUPLING: torch CUDA, the PTE engine.
FIT TO SLOT: blind-variation regime. Meets SRCH-05. The plants are evidence for SRCH-02 but there is no curve. Fails SRCH-13 (shaping without an arm that removes it). No genealogy within a run.
MODIFICATION COST: S to generalize; rebuild S. Keep the pattern of plants inside the genome space.
VERIFIED BY ME: search.py, SearchSpec, C1 sums, XOR and FLIP plant numbers.

COMPONENT 10a: Hephaestus forge 1.0, Forge Queue apprentice, xpol_2026 (floors.py, shape.py, knockout_ablation.py)
PATHS: agents/hephaestus/ledger.jsonl, agents/hephaestus/src/knockout_ablation.py, hephaestus/src/apprentice.py, hephaestus/src/closure_test.py, hephaestus/mint_queue/, hephaestus/xpol_2026/
OWNER / DATES: Hephaestus. ledger 2026-03-24 to 2026-08-12; hephaestus/src 2026-09-01 to 2026-09-11; xpol 2026-09-19 to 2026-09-23.
WHAT IT REALLY DOES:
- 1.0: a Nous triple goes to a hosted LLM that writes a ReasoningTool class; a validator and a trap battery then forge or scrap it.
- Forge Queue: a model-free closure gauntlet over frozen primitives routes each wall. Only OPERATOR walls reach the apprentice, which refuses premium models (apprentice.py:26-36).
- xpol: replays 114 packets with Fable 5.1, gemini-3.6-flash and gpt-oss-120b. floors.py computes decoys before any call; shape.py counts regex and NCD "costume" parts per tool from the AST; knockout removes engines one at a time.
SIZE: xpol .py 1,065 lines; knockout 156; no test functions.
DEMONSTRATED CORRECTNESS: floors show a decoy at 0.4032 beats the NCD comparator at 0.3925. Defects: 2,861 of 6,661 ledger rows are api_call_failed; FAIL_ABLATION never fired (dossier).
INTERFACE: per call, xpol logs prompt sha256, served model, tokens in/out/thinking, finish_reason and seconds (replay.py:65-100, 242-255). The 1.0 ledger has no tokens.
THROUGHPUT / SCALE: 6,661 1.0 attempts (M3). Wall time not recorded.
MODEL-FREE ARM: none (the floors are baselines, not generators). MINT-0001 events: the apprentice failed 5 times, the Master Smith (Fable) produced a v3 PASS_DEV, and the model-free closure test then reclassified the wall as Level-1 composition, marking it DORMANT.
COUPLING: prometheus_llm, claude CLI, NIM.
FIT TO SLOT: model-guided proposals. xpol meets INF-03 and INF-06; closure-before-model is a pattern for ANTI-04 and INF-02. Fails INF-02 (no fork tag).
MODIFICATION COST: retire 1.0. Reuse the floors, shape and logging patterns (S). The closure gauntlet is M to port.
VERIFIED BY ME: xpol README, logging code, headers, mint events. Ledger counts are from the dossier.

COMPONENT 10b: Icarus (an LLM rewrites a dispatch file)
PATHS: agents/icarus/daemon.py, agents/icarus/improve.py, agents/icarus/lenses/generator.py, agents/icarus/tier_oracle.py
OWNER / DATES: Icarus; 2026-05-25 to 2026-09-11.
WHAT IT REALLY DOES:
- One lineage, one candidate per cycle. It clones the last STABLE reasoner.py and asks Claude (claude-sonnet-4-6, fallback claude-haiku-4-5, later the CLI) for a patch.
- Prompt: a unified diff of at most 100 lines; touch only reasoner, strategy or generated tests; "make a real reasoning change".
- Acceptance: pytest, the tier oracle on held-out seeds, a falsifier and a lens panel decide STABLE or PARK.
- _maybe_advance_tier moves to the next tier when the held-out frontier reaches the target.
SIZE: improve.py 497, daemon.py 677, generator.py 381. Test functions: 15 (agents/icarus/tests_harness/test_caliber.py), corrected; see SURPRISES 1.
DEMONSTRATED CORRECTNESS: a deterministic sympy/z3 verifier on the algebra tiers. Defects: the R5 payload carries the label and R6 carries the truth (dossier).
INTERFACE: cycle log and typed failure objects. Daily token totals only, not per call. Nondeterministic.
THROUGHPUT / SCALE: 22 cycles; cycle 20 took 442 s (dossier).
MODEL-FREE ARM: none.
FIT TO SLOT: model-guided proposals. Fails ANTI-04, ANTI-07 and INF-02.
MODIFICATION COST: retire; a rebuilt patch-and-test loop is S.
VERIFIED BY ME: model ids, prompt, tier-advance code, test count.

COMPONENT 10c: Nous concept-triple generator
PATHS: agents/nous/src/nous.py, agents/nous/src/scorer.py, agents/nous/src/concepts.py
OWNER / DATES: Nous; 2026-03-24 to 2026-05-13.
WHAT IT REALLY DOES: Samples 3 of 95 concepts and sends one prompt to NVIDIA NIM (nemotron-3-super-120b by default). The prompt asks what scoring algorithm the triple suggests, whether it is novel, and for four 1-10 self-ratings, and it states what succeeds in the pipeline (nous.py:84-87). Ratings are parsed by regex.
SIZE: 1,315 lines; 0 test functions.
DEMONSTRATED CORRECTNESS: none in the engine. "Novel" is returned 92.3% of the time (dossier).
INTERFACE: per-call row with triple, response, score, model and timestamp; no tokens.
THROUGHPUT / SCALE: 5,918 committed rows. Wall time not recorded.
MODEL-FREE ARM: none.
FIT TO SLOT: none. It violates ANTI-10 (the model rates its own output).
MODIFICATION COST: retire; a rebuild is S.
VERIFIED BY ME: prompt, client, log fields.

COMPONENT 10d: prometheus_llm (the model-call layer)
PATHS: prometheus_llm/client.py, prometheus_llm/types.py, prometheus_llm/registry.py, prometheus_llm/cli.py, prometheus_llm/tests/test_offline.py
OWNER / DATES: owner not stated in the files I read; all commits 2026-08-22.
WHAT IT REALLY DOES: complete(prompt, target="provider:model", fallback=...) returns a Completion with provider, served model, finish_reason, empty_content, tokens, cost, latency and attempts. ok means usable content came back. It retries once at 4x the budget on empty content.
SIZE: 1,161 lines including 32 offline tests.
DEMONSTRATED CORRECTNESS: offline tests.
INTERFACE: the audit log is opt-in (PROMETHEUS_LLM_LOG). It records a prompt sha1 and length; the prompt text only if a second flag is set. No fork-type or campaign field. Nondeterministic.
THROUGHPUT / SCALE: not recorded.
COUPLING: 5 importers (4 production modules plus 1 test). 60 other .py files call provider SDKs, provider endpoints or "claude -p" directly (generated tool directories excluded; verified unchanged under full exclusions).
FIT TO SLOT: the call layer under model-guided proposals. Near INF-03 if logging is made mandatory. Fails INF-02.
MODIFICATION COST: S to add mandatory logging and fork and campaign fields; M to route all call sites. Rebuild: S.
VERIFIED BY ME: all of the above.

COMPONENT 11: Metis compose.py
PATHS: roles/Metis/season1/specimen/compose.py, roles/Metis/season1/specimen/test_adversarial.py, roles/Metis/season1/bundles/
OWNER / DATES: Metis; 2026-09-13 only.
WHAT IT REALLY DOES:
- Takes an author-encoded bundle: explanations, evidence with upstream tokens, instruments, and discriminators with an ordinal cost plus the explanations each outcome branch eliminates.
- Filters evidence by cutoff, groups evidence by shared upstream (union-find), applies eliminations and vetoes.
- Returns the cheapest available discriminator whose branches split the live set differently and that is cheaper than the baseline experiment. Ties are broken by id; rejected discriminators are listed with reasons.
- No score and no model.
SIZE: compose.py 442 lines; 13 test functions.
DEMONSTRATED CORRECTNESS: adversarial tests; 5 episodes plus one post-hoc positive control. Defect: 5/5 vetoes cannot be told apart from veto-everything except by that one control (dossier).
INTERFACE: compose(bundle) returns a Result. Deterministic set operations.
THROUGHPUT / SCALE: negligible; not recorded.
COUPLING: stdlib; no importers.
FIT TO SLOT: next-experiment selector. Meets the first half of INF-05 as is, and ANTI-02 (decisions use sets and cost ranks only). Missing: the staircase half, measured costs, a runner hook, and encoding by someone other than the author.
MODIFICATION COST: S; rebuild S.
VERIFIED BY ME: the rule, cost ladder, partition test, tests, importers.

----------------------------------------------------------------------
A. BUDGETS

system                    largest count on record        wall            host           evals/s
Archaeon WSE survey v01   2,520,000 organism evals (x24  1,531.6 s       M2, 24 procs   1,645
                          episodes each)
Archaeon reach. table     sum N x G 22,585,600           not recorded    M2             n/a
Archaeon Deep Frontier    4,099,920 evals                not in repo     M2             not recorded
Archaeon Z80 x Atlas      101,003 ecology runs           71.63 h         M2, 24 wkrs    0.392 runs/s
PROTEUS-46                about 50,400 child evals (ci)  not recorded    M2             n/a
Crius C0-C2               475,728 candidates             49,132.4 s sum  M2             9.68
Tyche Block R             162,973 lenses                 12,437.3 s sum  M2             13.1
Theseus v0_1              about 2,580 genomes (ci)       2,190.1 s       4 CPUs         about 1.2
Apollo O1                 1,737,000 pipelines            3,000.2 s       M2             579
Apollo Branch C llm2      800 generations                86,156 s        M2 + GPU       about 0.19 (ci)
Lexis closure             484,218 joint states           not recorded    M1             n/a
Ergon E4 P3               193,207,377 table evals        834 s           M1, 8 wkrs     231,663
Aphrodite S4              324,949,606 charges            not recorded    M4             n/a
Aphrodite accel receipt   106,839,976 charges            429.9 s         M4, 3 wkrs     248,523
Ananke PTE-C1             19,873,536 world-episodes      31,488.4 s sum  M1 GPU         631
Hephaestus forge 1.0      6,661 LLM attempts             not recorded    M3             n/a
Icarus                    22 LLM cycles                  442 s/cycle     M2             about 0.002
(ci = code-inferred)

Reading against the M1 ceiling: no system records instructions per evaluation, so none of these converts to instructions per second, and the units differ from row to row.
- The lifetime-scale searches top out at about 2e7 evaluations (Ananke).
- At the receipt's planning figure of 4e8 lifetimes per day, that is about 1.2 hours of M1, if each evaluation were one 1e5-instruction lifetime.
- The only counts above 1e8 are tiny-program checks (Aphrodite, Ergon). Those two are also the fastest search loops in scope, at about 2.3e5 to 2.5e5 per second on 8 and 3 workers.

B. ADAPTIVE STAIRCASE
None found.
How I searched: git grep over *.py for staircase, psychometric, up-down, levitt, jnd; then for curriculum; then for adaptive challenge, adaptive difficulty, step up, next rung, advance tier, learning progress.
"Staircase" in code only names Harmonia's fixed tier ladder (harmonia/services/grading_oracle.py). No code estimates a per-organism threshold with a stated resolution (MEAS-12). These threshold-driven rules exist:
- archaeon/campaign1/sfe05.py: steps up the distractor ladder {0,1,2,4,8} when the population mean training reward is >= 0.40, and down when < 0.10. Reported "adaptive +0.155" at n 3 (CAMPAIGN_REPORT.md:85).
- archaeon/campaign3/ladder.py: holds rung 0 until the elite's best reaches 0.5.
- archaeon/wse/evolve.py: a cost ramp scaled by min(1, best/foothold).
- apollo/src/task_manager.py: easy-task share 0.7 / 0.5 / 0.3 / 0.1 by population best accuracy bands < 0.1 / 0.3 / 0.5.
- agents/icarus/daemon.py: _maybe_advance_tier.
- archaeon/z80atlas/engine.py env_coevolve: a niche's environment reproduces when the niche mean score is >= 0.8.
- agents/nemesis/src/map_elites.py ToolDifficultyModel: per tool, targets the categories nearest a 50% pass rate.
None of these is shared code. All except Nemesis key on population statistics.

C. MODEL-GUIDED VERSUS MODEL-FREE ON THE SAME TASK
Yes, in two places, neither at an equal certified level.
(1) Theseus synth v0_1 REPORT.json. Arm A is 60 genomes written by a Claude agent; its rows carry no model id and no token log. It was scored on the same DSL and rulers as the model-free arms.
- Viable: 51 of 60.
- Cells occupied only by that arm (desc / pca / resp grids): A 15/18/7; D 23/21/11; R 27/20/6.
- NOT_REPRODUCED_YET: A 0/10, D 12/20, R 8/10.
- Median best distance over tau: A 1.319, D 2.146, R 3.447.
- The preregistered test is D against pooled A, B, C, R (INDETERMINATE), not A against blind arms, and A shares the builder's model family.
(2) Apollo Branch C, --mode llm against deterministic. The llm mode is itself 50% blind.
- Both reached max_acc 0.833 (STARTUP.md:96-104), which O1 enumeration also reaches.
Partial cases:
- Hephaestus MINT-0001: one wall, where a model-free closure test overruled a model-minted candidate.
- Apollo v2's "hybrid" run, which had 0% DeepSeek calls.
- Lexis G5: LLM singletons against a hand-built pair.
xpol has no model-free generation arm.

----------------------------------------------------------------------
COMPARISON
SLOT / RANK  COMPONENT            REASON
SEARCH PROTOCOL (loop, budgets, receipts, typed outcomes)
 1 Archaeon WSE 1a     CRN, Wilson reach classes, typed states, gen0 provenance
 2 Ergon/D-5 7         exact oracle, compiled kernel with equivalence, budget ladder
 3 Aphrodite 8         enforced escrow, keyed CRN, paired selection rule
 4 Archaeon frontier   checkpoint/replay contract; ignored receipts, saturated rulers
BLIND STRUCTURAL VARIATION
 1 Ergon/D-5 7         fastest, integer, verified; GA is small and generic
 2 Archaeon WSE 1a     neutral-accepting with splice; pure Python
 3 Ananke 9            GPU-batched, held-out discipline; shaping confound
 4 Crius 3             tie-break and seen set suppress neutral drift
 5 PROTEUS-46 2        rejects neutral moves; keep only as a fixture
POPULATION SEARCH WITH DIVERSITY ARCHIVE
 1 Tyche 4             lexicase over a case vector, per-case elites, reserve, tracer
 2 Apollo Branch C 6a  MAP-Elites with crossover; organism irrelevant
 3 Theseus 5           fingerprint archive, protection only, no selection
MODEL-GUIDED PROPOSALS
 1 Apollo llm mode 6a  in-loop, typed insert, 50% blind share, validators
 2 Hephaestus 10a      per-call token logs, cheap-model gate, closure-first
 3 prometheus_llm 10d  call layer; needs fork tag, mandatory log
 4 Icarus 10b          single lineage, leaky ruler
 5 Nous 10c            self-rated; retire
GRADIENT               none in scope (searched; only an ES toy in Aphrodite)
ADAPTIVE STAIRCASE
 1 sfe05 up/down 1a    only up/down rule with an independent evaluation
 2 Nemesis 50% model   per-subject threshold targeting, categorical
 3 Apollo task mix 6a  population bands
 4 Icarus tier 10b     single lineage
P8 GENERATOR DIVERGENCE
 1 Theseus 5           same rulers, model arm present, permutation statistic
 2 Apollo llm2 6a      same battery; saturated space
 3 xpol shape.py 10a   static mechanism fingerprint for code
REACH INPUTS (planted targets, needle size)
 1 Crius PARTS 3       designed partials at graded distance
 2 Ananke plants 9     in-space plants the search missed
 3 Archaeon reach 1a   recovery against budget, per cell
 4 Lexis/Apollo O1     exact enumeration ground truth
NEXT-EXPERIMENT SELECTOR (INF-05)
 1 Metis compose 11    model-free cheapest-split rule; author-encoded inputs

COULD NOT DETERMINE
- Per-run wall time for the Deep Frontier (runs/ is gitignored), the Apollo May runs, Lexis, PROTEUS-46 and Nous: not in the repo.
- Instructions per evaluation for any system, so no instructions-per-second figure can be derived.
- Not opened: Apollo NSGA code; Tyche v1 DE reserve code; the Icarus full-file path; the Theseus collide body; the forge 1.0 generator (hephaestus.py); Proteus v0_6 result files beyond names.
- Not re-derived: the D-5 verdict numbers, the G4 space size, and the Ergon P3 host (the dossier says M1).
- Whether the DeepFrontier scheduled task still runs.
- Whether the holdout-named harmonia file matched "staircase" (SURPRISES 1b).

SURPRISES
1. Holdout exposure (coordinator's request). Two earlier commands reached holdout-named files.
   (a) Command: for d in agents/icarus hephaestus agents/nous; do n=$(timeout 20 git ls-files "$d" | grep -E '(^|/)test_[^/]*\.py$|_test\.py$' | xargs grep -c "def test_" 2>/dev/null | awk -F: '{s+=$2} END {print s+0}'); echo "$d tests: $n"; done
       It had no exclusion, and grep -c opened 2 holdout-named test files in agents/icarus. It returned one summed count, "agents/icarus tests: 21". No content was printed. A clean recount gives 15 (all in test_caliber.py), so 6 of the 21 came from holdout files. I corrected sheet 10b.
   (b) Command: timeout 60 git grep -c -i -E "staircase" -- ':!**/*holdout*/**' ':!**/nestor_secrets/**' | head -40
       It scanned 7 holdout-named files outside holdout directories, including one in harmonia/. It returns per-file counts only. The 40 lines shown contained no holdout path; anything beyond line 40 was not displayed and I did not check it.
   (c) Repo-wide *.py greps with the directory-only pattern scanned 2 holdout-named .py files. Each returned either complete output with no holdout path, or a count unchanged under full exclusions (60).
   (d) My audit itself used name-only listings without exclusions and printed counts only. No file was opened.
2. Pattern gap. ':!**/*holdout*/**' does not exclude a top-level holdout directory, and ':!**/*holdout*' does not exclude a top-level holdout file. Tested on harmless names: 1,816 of 1,818 archaeon paths survived, and README.md survived. A bare ':!*holdout*' covers both cases. Tracked now: 52 holdout paths, 7 of them outside holdout directories, and 0 at top level.
3. Git bug (2.52.0.windows.1). git ls-files with a single positive path plus any exclusion, even ':(exclude)zzqqxx', returns 0 files: prometheus/ananke drops from 49 to 0 and archaeon/wse from 258 to 0. git grep is unaffected. A dummy second positive path restores the correct result. Absence results from ls-files can therefore be false.
4. The PROTEUS-46 greedy walk discarded thousands of available neutral children (sheet 2).
5. Crius breaks fitness ties toward shorter programs and never revisits a genotype. Both work against the reported neutral-insertion path.
6. Apollo's "LLM" mode is a 50/50 mixture with blind mutation, so llm2 compared a 50% LLM share against 0%.
7. The Theseus A-arm numbers are the only existing ANTI-07-shaped data. The model-written genomes sit closest to the known library.
8. The frontier registry records 4,099,920 evaluations, against 3,719,136 in the dossier. The reachability table has 1,277 rows, against 1,265 in the dossier.
9. prometheus_llm is not the single call path: 5 importers against 60 direct callers.
10. The fastest search loop in scope (D-5) has no elitism and uses Windows-only paths.
11. CMP1 SFE-05 contains a real up/down curriculum, and Nemesis targets a 50% pass rate per tool. Neither dossier says so.
===END REPORT===
