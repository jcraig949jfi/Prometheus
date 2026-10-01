# Apollo -- forensic dossier (Sisyphus crawl)

- Seat: Apollo ("Evolutionary Architect & Reasoning Species Engineer";
  Gen-2: "Serendipity Ecology Substrate Miner")
- Crawl date: 2026-10-01
- Base SHA of worktree: 19299e06b (F:/Prometheus-worktrees/sisyphus-base-role, origin/main)
- Crawler: Sisyphus worker (seats Daedalus + Apollo)

## Coverage statement

READ (code): apollo/src/genome.py (catalog and structures), fitness.py
(6-objective vector, NCD baseline), task_manager.py (task sets),
blackboard.py (typed state), blackboard_evolve.py (registry, mutation
moves, crossover flag); apollo/configs/config_v2d2b.yaml (key lines);
apollo/archive/v1/design_v1.md (mission/architecture) and v1/journal.md
head; the off-repo D-13 stackvm VM header (F:/SerendipityD), which Apollo
Gen-2 drove.

READ (prose/history): roles/Apollo/ (CHARTER, CHARTER_GEN2, BOOTSTRAP,
STATUS.txt, STARTUP.md in full, CALIBRATION.md, BACKLOG_H0H5.md, journal
2026-09-11 tail); roles/EvolutionaryArchitectAndReasoningSpeciesEngineer/
Apollo_Role_Document.md head; apollo/{README, ARCHITECTURE, RESUME}.md;
pivot/autopsy_apollo_2026-05-13.md; apollo/archive/reports/
evolution_report_2026-04-09_0940.md; apollo/cycles/type_bridge/{LINEAGE.md,
RESULT.json}; apollo/cycles/campaign_20260825/E9_FINDINGS.md (stop-rule
section); S1 pilot run JSONs (numbers extracted); apollo/wall_corpus/
MANIFEST.md head; apollo/pivot/recombination_findings_2026-06-16.md (key
rows); every commit body touching apollo/ or roles/Apollo/ (59 commits,
2026-03-27..2026-09-11); roles/base-role/{RESPONSIBILITIES.md rule 9,
MONITORS.md Apollo and Talos rows}; Atlas inference_harvest_2026-09-30
mentions of Apollo; comms subject lines naming Apollo.

NOT READ, and why: apollo/ROADMAP.md (484 lines; summarised via RESUME and
autopsy), most of apollo/archive/ (284 files: v1 design rounds, v2b/v2c
src trees, 150 evolution reports -- sampled one), the 380-line
pivot/apollo_investigation_2026-05-22.md (read via its commit body),
apollo/src/apollo.py beyond its function index, mutation.py,
mutation_llm.py, the Granite/Qwen server code, dispatch and O1 scripts (read
via commit bodies and findings). Run directories apollo/run_* hold only
novel_discovery.jsonl stubs in git; the raw logs/checkpoints lived on M2
(D:\Prometheus\apollo\...) and are not on this host. The F:/prometheus
canonical checkout on this host has the same 1 KB stubs.

-----------------------------------------------------------------------

## 1. Identity and purpose

- Canonical name: Apollo. Earliest artifacts: apollo/archive/v1 design and
  journal "2026-03-26 -- Session 1" (merged into repo history at 7a037eaf6,
  2026-04-23); first repo commit touching apollo/ is 8af6ba9e5
  (2026-03-27). [HIST]
- Aliases: role directory roles/EvolutionaryArchitectAndReasoningSpecies
  Engineer/ (Apollo_Role_Document.md, RESPONSIBILITIES.md, committed
  2026-04-04 at b56c7401a). apollo/README.md calls Apollo "the model-
  training arm of Prometheus -- an evolutionary pipeline for training small
  LLMs against novel fitness functions"; the code never trains an LLM (LLMs
  are used only as mutation operators). README is stale/incorrect.
  [CORRECTION]
- Original charter [INTENT] (design_v1.md, 2026-03): "a self-contained,
  closed-loop evolutionary system that takes the Prometheus forge library
  (141+ computable reasoning tools) as seed genomes and evolves them ...
  into increasingly sophisticated autonomous reasoning organisms", designed
  to run 40+ days; "Metacognition, novelty exploration, and hypothesis
  generation should emerge from selection pressure, not be designed in."
- Gen-1 identity (roles/Apollo/CHARTER.md): evolve compositions ("molecules")
  of fixed reasoning primitives ("atoms", from Hephaestus/Forge) with an
  ablation gate; deliverable = verified (problem -> primitive_sequence ->
  answer) triples as training data for a future routing network (autopsy
  2026-05-13). Doctrine: falsification-first; report failure SHAPES;
  "Goodhart is the default suspect"; "search-operator before substrate".
- Charter change (2026-09-01): CHARTER_GEN2_serendipity_20260901.md --
  "substrate miner" over Serendipity Foundry worlds; "Apollo proposes;
  independent instrumentation falsifies; the ecology selects." Same day,
  HITL standing disposition s0a: scheduled evolutionary mining SUSPENDED
  after S1 BLOCKED; only ONE Source Viability Gate probe authorised against
  the next Foundry release. [INTENT/HIST]
- Base-role adoption 2026-09-11 (1f0873ea5): BOOTSTRAP.md became the entry
  file; STARTUP.md demoted to Gen-1 history; gate eligibility measured
  INDETERMINATE (no successor /v0 release exists; SFE /v2 has no
  search/evaluate surface).
- Current / terminal role: DORMANT by ruling, silent since 2026-09-11
  (last commit 2b7c6e4fb; no comms post after #22). Operator decisions
  APOLLO-04 (retire scheduled mining vs re-scope the gate) and APOLLO-22
  (seat disposition) were requested; no D-row records either in
  archaeon/docs/expansion/DECISIONS.md. Lexis was recorded BLOCKED on
  Apollo's Task 2 (DECISIONS.md D-25), which never ran. [HIST]
- Relationships: Hephaestus/Forge (upstream primitives: Frame H
  forge_primitives, trap_generator, hephaestus_ops); Charon (independent E9
  battery, roles/Charon/apollo_e9/, 5097b0c8f); Aporia (P153/P155
  replications that falsified two Apollo claims, 3c80230ab); Lexis (26
  declared ops, write-write hazard; state-injection fixture); Harmonia
  (four-lens panel; lane_exhaustion_audit fires on Apollo); Talos (corpus
  daemon expected an apollo/runs stream that "never existed" --
  roles/base-role/MONITORS.md Talos row; base rule 9 cites it); Daedalus
  lineage (the D-13 /v0 Foundry Apollo Gen-2 drove).
- Hosts: Gen-1 on M2 (D:\Prometheus paths, local GPU; Qwen2.5-Coder-7B
  8-bit, later Granite-3.0-2B on :8800, Python312 env note in STARTUP);
  Gen-2 slice ran against the M1 /v0 Foundry (192.168.1.202:8799); the 09-11
  pass booted on SKULLPORT (M1).

## 2. Engine / system inventory

### 2.1 Apollo v1 (March 2026) -- forge-tool gene splicing
- Paths: apollo/archive/v1/{design_v1..v3.md, src/, gene_library.json,
  v3_seed_candidates.json, journal.md, council_feedback_1.md, lineage/}.
- Genome: the 146 forge ReasoningTool classes (evaluate(prompt,
  candidates), confidence) parsed into gene fragments (parsers, scorers,
  NCD computation, number extraction, negation detection) and recompiled
  into chimeric organisms (design_v1.md; journal 03-26). [INTENT; code not
  read]
- Outcome per autopsy: "AST-only mutation stalled at NCD baseline in v1".
  [HIST]

### 2.2 Apollo v2 / v2-beta / v2b / v2c / v2d (April-May 2026)
- Paths: apollo/src/{apollo.py 1,203 lines, genome.py, fitness.py,
  selection.py, racing.py, map_elites.py, novelty.py, aos.py, mutation.py,
  mutation_llm.py, compiler.py, sandbox.py, task_manager.py, ablation.py,
  checkpointer.py, llm_server*.py, deepseek_client.py, ...}; configs/
  config_v2b..v2d3, bakeoff configs; archive/{v2-beta,v2b,v2c,v2d}/.
- Organism [IMPL]: "primitive routing DAGs over 25 Frame H primitives"
  (genome.py) -- solve_sat, modus_ponens, check_transitivity, negate,
  bayesian_update, expected_value, entropy, coin_flip_independence,
  dag_traverse, topological_sort, counterfactual_intervention,
  solve_constraints, pigeonhole_check, fencepost_count, bat_and_ball,
  modular_arithmetic, all_but_n, solve_linear_system, temporal_order,
  direction_composition, track_beliefs, sally_anne_test,
  confidence_from_agreement, information_sufficiency, parity_check; loaded
  from agents/hephaestus/src/forge_primitives.
- Fitness [IMPL]: 6 maximised objectives -- accuracy margin over an NCD
  (zlib compression distance) baseline, calibration (1-Brier, margin),
  ablation delta ("BYPASS KILLER"), held-out generalization, novelty,
  parsimony; NSGA-II then NSGA-III; 2026-05-22 patch caps apparent accuracy
  at 0 when ablation_delta < 0 (fitness.py).
- Tasks [IMPL]: trap batteries from agents/hephaestus/src/trap_generator.py;
  50 fixed reference, 100 evolution (10 rotate every 50 gens), 50 held-out
  refreshed every 500 gens (task_manager.py). Multiple-choice: prompt +
  candidate list.
- Operators: drift (parameter), seed, LLM structural mutation (Qwen-7B-
  Coder local 8-bit, DeepSeek-chat API, later Granite-3.0-2B), adaptive
  operator selection bandit, racing early-kill, MAP-Elites archive (500).
- Scale: population 50; runs to gen 686 (April) and gen ~2960-3551
  (May; commits e94ca44b1, 3ebdad8b4; blackboard.py docstring "gen-3551");
  target 50,000 gens (config max_generations).

### 2.3 Branch C -- blackboard substrate (2026-05-24..08-19)
- Paths: apollo/src/{blackboard.py, blackboard_ops.py (v1 ops),
  blackboard_ops_v2.py, blackboard_ops_r2.py, blackboard_ops_compare.py,
  dataflow_fitness.py, blackboard_evolve.py 817 lines, hephaestus_ops.py};
  apollo/data/clean_canary_v01.json; scripts (composition_gauntlet,
  inference_canary, cross_tier_canary, r2_falsification,
  cross_tier_falsification, recombination_falsification, recombination_ab,
  dispatch_poc, dispatch_falsification, diagnose_0558_wall, run_dispatch_llm,
  type_bridge_cycle, wall_corpus, o1_enumerate, e1_schedule_classes,
  benchmark_attack, replay_harness, e9_score, ...).
- Organism [IMPL]: a linear pipeline of typed operator-steps over a shared
  BlackboardState (slots: numbers, names, relations, quantities,
  question_target, transitive_closure, ordered, counts, evidence,
  probabilities, rules, facts, derived_facts, comparison, extreme_number,
  candidate_scores, selected_answer). Role-tiered registry: ~15 transformers
  (parsers, ordering, aggregation, forward_chain, relations_from_facts,
  comparison parsers), terminal scorers including guarded scorers
  (precondition + on_fail="skip" = dispatch), quarantined v1
  answer-producers. Body length <= 6 (insert guard).
- Fitness: causal_composition_score = clip+(composition lift over best
  single primitive and terminal-only baselines) x clip+(dataflow score);
  MAP-Elites keyed on the LOAD-BEARING CORE (ad574ef72), parsimony
  tiebreak; four in-run abort conditions.
- Mutation: deterministic insert / remove / swap_t / swap_scorer /
  add_guard; LLM mode (Granite JSON-DSL insert_step); one-point
  `recombine()` and `dispatch_merge` (body+guard union) behind
  `--crossover-frac` (CLI default 0.0, blackboard_evolve.py:802).
- Eval battery: canary 50 + synthetic 30 + inference 20 + cross_tier 20 =
  120 tasks (decomposition 30+30+20+20 = 100/120 = 0.8333, 3c80230ab).

### 2.4 Analysis instruments (08-15..08-25)
- O1 exhaustive enumerator (1,737,000 type-correct pipelines), E1 semantic
  schedule-class checker, benchmark attack (13 trivial heuristics), replay
  harness, Tier A ablation-wall corpus (apollo/wall_corpus/, 28 runs, F-answer
  / F-oracle firewall enforced by a validator), e9_score.py.

### 2.5 Gen-2 Serendipity adapter (2026-09-01)
- Paths: apollo/serendipity/{remote.py (vendored /v0 FoundryClient),
  foundry_creds.py, world_adapter.py, eval_adapter.py, fossil.py,
  s1_worlds.py, s1_campaign.py, slice_pilot.py, source_viability_gate.py,
  workspace_guard.py, FOUNDRY_API_NOTES.md}; apollo/cycles/
  {serendipity_slice, S1_archive_value, S1_archive_value_PILOT}.
- It drives the D-13 Foundry's own search drivers (random, map_elites)
  over stackvm-v1 / push-pyshgp / treegp-deap through /v0 search/evaluate;
  Apollo authors tasks, captures genotype + lineage, replays by event_seq,
  emits fossils with a provenance hash. Gate: G1 frontier depth, G2
  population mass, G3 headroom, G4 dead-world discrimination, absolute
  thresholds; s1_campaign refuses to score without a PASS artifact
  (77cc2249b). [IMPL per commit bodies + file list]

## 3. Architecture

- World: v1/v2 -- a battery of multiple-choice reasoning prompts from a
  trap generator; Branch C -- 120 hand-authored/generated prompts in four
  subsets; Gen-2 -- a /v0 Foundry task (e.g. f(x)=3x+1 on 12 cases). There
  is no environment state, no time, no space. [IMPL]
- Organism: v1 spliced tool code; v2 routing DAG over 25 primitives; Branch
  C typed pipeline (genotype = op list + guards; phenotype = execution over
  the blackboard producing selected_answer or abstention). Gen-2: stackvm
  byte programs owned by the Foundry. [IMPL]
- Memory: the blackboard is per-task scratch state; nothing persists across
  tasks; no recurrent state. [IMPL]
- Compute: deterministic Python ops; LLM servers only for mutation.
- Mutation/search: s2. Selection: NSGA-II/III (v2), MAP-Elites archive
  (v2, Branch C). Admission: ablation gate (v2: output-change, then
  accuracy-delta after 05-22), load-bearing core keying (Branch C).
- Pressure: purely task-score pressure plus diversity/parsimony terms; no
  ecology, no resources, no competition between organisms beyond
  selection.
- Reward: accuracy on battery; per-subset; max_acc / best_acc /
  portfolio_coverage / max_routable_acc (metric changed several times --
  see s9).
- Reproduction: clone + mutate; crossover optional.
- Learning/adaptation within lifetime: none.
- Communication: none. Cross-world transfer: none in Gen-1; Gen-2 S1
  tried cross-family transfer and found it not constructible.
- Lineage tracking: v2 lineage.mutations_applied (wiped by a bug, s9 T2);
  Branch C lineage strings, novel_discovery.jsonl, checkpoints; Gen-2
  fossils carry parent ids and replay seq.
- Provenance: Gen-2 fossil provenance_hash; Branch C runs not
  provenance-pinned beyond commit ids; most raw run data off-host.
- Experimental control structure: Branch C campaigns carried preregistration
  files (type_bridge/PREREGISTRATION.md; campaign_20260825/
  PREREGISTRATION.md with a stop rule; S1 PREREGISTRATION kept UNFROZEN).

Design vs implementation disagreements:
- Design rule in blackboard_evolve.py: preconditions keyed on SEMANTIC SLOTS
  "never problem_text surface - that would be memorization". Implementation:
  blackboard_ops_compare.py parse_comparison precondition is
  `problem_text.strip().lower().startswith("is ")` -- the rule held for
  scorers and was violated by transformers (9b00453ca). [CORRECTION]
- v1 design "metacognition ... should emerge"; Branch C's capabilities were
  each added by hand (s9 T6).
- README "training small LLMs" vs code (above).
- Charter target ladder tier "R9" does not exist in the grader (CAL-01).

## 4. World capability audit

- Branch C world [IMPL/HIST]: 120 static text tasks; each a single-shot
  multiple-choice selection; no state, no partial observability beyond the
  text, no stochasticity, horizon 1, no adversaries, agents, resources,
  ecology, environmental change. Task diversity = 4 subsets / ~7-10 named
  categories (numeric_comparison, numeric_stated_premise, transitivity,
  all_but_n, temporal_ordering, vacuous_truth, consistency_check, nth_ranked,
  two_stage_count, ...). Easily memorised: the E9 failure shows parsers
  template-matched the home authorship (s9 T8). Home candidates carried
  padded filler strings ("No as stated as stated precise") that blind
  candidates lacked -- a data smell noted 06-22 and never fixed. Toy-grade.
- v2 world: trap-generator batteries (n_per_category 5-10; reference 50,
  evolution 100, held-out 50). Same single-shot shape.
- Gen-2 world: D-13 integer-function tasks, 12 test cases; Apollo's
  solvability ladder at budget 600 reached only identity and x+1;
  abs/threshold 7/12 partial; modular 5/12 (CAL-08). The S1 pilot used
  budget 80 with a DEAD (random) world, aff_3x+1 and sq.
- Transfer between worlds: none constructible (S1, c6a2b2a44).
- Scaling limitation: battery authorship (one author) and the operator
  registry size (~26 ops; O1 enumerated the whole space in 3,000 s of
  CPU). The world is exhaustively searchable.

## 5. Organism capability audit

- Instruction set: Branch C ~26 hand-written operators, each a complete
  Python function (parse, order, aggregate, forward-chain, compare); v2 25
  puzzle-named primitives (e.g. bat_and_ball, sally_anne_test,
  fencepost_count -- solvers named after the very puzzle categories in the
  battery).
- Control flow: linear pipeline; conditional execution only through guards
  (skip on failed precondition); no loops, no recursion, no branching
  beyond guard skip, no subroutine reuse.
- Memory: typed per-task slots fixed in the dataclass ("Adding a slot is
  intentional, not emergent", blackboard.py). Writable but schema-fixed.
- Sensors/actuators: the problem text and candidate list in; a selected
  answer out.
- Learning, planning, internal simulation, self-modification, development,
  communication, tool use: none.
- Reproduction: copy + edit; crossover splice; no development.
- Abstraction / cross-task reuse: only through guarded dispatch of fixed
  operators.
- Fighting chance for a nontrivial reasoning primitive? Not to CREATE one:
  the organism can only order and gate human-authored operators (RC7, "Apollo
  rearranges human-authored operators, it does not mint them", f91b335ac).
  It could in principle discover a COMPOSITION (routing) that no single
  operator performs, and it did so (cross-tier forward_chain ->
  relations_from_facts -> ordering -> select_nth, 3/5 to 4/5 seeds with
  crossover). The 08-12 strategy document records "all 5 of Apollo's
  widenings were agent-supplied, 0 self-found; search then burns 84% of
  compute after the ceiling" (STARTUP.md 2026-08-12). O1 shows the whole
  reachable space was enumerable; evolution's value was sample efficiency
  (537x fewer evaluations than breadth-first enumeration), not reach.
  [RESULT-UNVERIFIED]

## 6. Search and pressure mechanism

- v1: AST gene splicing + mutation, novelty search, NSGA-III planned.
- v2: NSGA-II/III, racing, MAP-Elites archive (500 cells), AOS bandit, LLM
  structural mutation + parameter drift + annealing (v2d fixes: difficulty
  curriculum, post-mutation annealing, accuracy-only AOS reward, selection
  death logging; ARCHITECTURE.md).
- Branch C: MAP-Elites on load-bearing core, deterministic or Granite
  mutation, optional crossover/dispatch_merge, dispatch guards.
- Gen-2: Foundry-side random and map_elites drivers at budgets 80-600.
- Collapse modes documented:
  * flat landscape (v2c gen 90: 0% raw accuracy population-wide; "Drift
    dominates");
  * AOS reward corrupted (every operator rewarded 1.0 at 0% accuracy);
  * archive saturation with diversity weight 0 (April report);
  * decorative composition satisfying an output-change ablation gate
    (05-22 baseline matrix: 0/5 elites with compositional lift);
  * multi-op fitness valleys single-step mutation cannot cross (0/8000
    walks; 06-16);
  * archive inflation by duplicate-op variants (86 "cells" mostly one
    solver; 2,860 cells at gen 800);
  * LLM mutator adds nothing in the converged regime (llm2 run: 2,152 LLM
    mutations, zero lift);
  * the ceiling is the registry, not the search (O1).

## 7. Measurement / ruler stack

- Accuracy margin over NCD (v2); ablation gate v1 = output_change_fraction
  (gameable), v2 = accuracy_delta (3ebdad8b4); type-wiring warnings.
- Branch C: composition lift vs single-primitive and terminal-only
  baselines; shuffled-state null (corrupt the terminal-read slot); reorder
  breakage; dataflow load-bearing check (composition gauntlet, a5998a139);
  per-branch dispatch ablation; genuine_routing audit flag.
- Headline metrics changed: best_acc (ccs-selected, hid results) -> max_acc
  -> portfolio_coverage (an oracle; dropped after the benchmark attack) ->
  max_routable_acc (excludes canary). Each change is documented.
- Baselines: NCD; best single primitive; 13 trivial heuristics (chance
  0.25, best rule 0.35, tuned router 0.45, oracle over rules 0.925);
  breadth-first enumeration (O1).
- Positive controls: composition gauntlet COMP_A/COMP_C pass and COMP_B
  control fails; O1 known-organism positive control; E1 self-test
  rediscovering a known write-write hazard; wall-corpus validator with a
  planted violation.
- Negative / sham controls: E11 sham primitive (designed, never run);
  dead-world control in S1 (coverage 0.1875 on a structureless world).
- Statistical tests: mostly counts over n=5 seeds; no formal tests in
  Branch C beyond preregistered thresholds; E9 tolerance +-0.15 with a
  mix-adjusted primary.
- Transfer assays: E9 (different author, same categories); S1 cross-family
  transfer (not constructible).
- Known blind spots: plateau telemetry cannot separate "capability absent"
  from "present but mis-wired" (wall corpus MANIFEST s4); archive coverage
  and QD score are unsafe observables (CAL-10).

## 8. Experiment inventory (campaigns)

A-1 v1 gene splicing (2026-03-26..04). Organism: spliced forge tools;
  world: trap battery; measurement: accuracy vs NCD. Reported: stalled at
  NCD baseline (autopsy). Label: REPORTED NEGATIVE/NULL. Artifacts:
  apollo/archive/v1/.

A-2 v2 runs v2_c..v2_d2b (2026-04-04..04-09). Reported: v2_d2b best +0.690
  over NCD, median +0.615; "50/50 Qwen+DeepSeek hybrid outperforming pure
  Qwen"; LLM mutations not surviving to elite (archive/reports/
  evolution_report_2026-04-09_0940.md; autopsy). Later: the "not
  surviving" reading was a lineage-wipe bug (e94ca44b1); the report's own
  column shows 0% DeepSeek calls in the "50/50" runs; baseline matrix found
  0/5 elites with compositional lift (3ebdad8b4). Label: LATER OVERTURNED.

A-3 v2 May resumption to gen ~2960 (2026-05-19..05-22). Granite bake-off
  (Granite >90% validation vs Qwen 1%); after the lineage fix llm_alive
  0 -> 24/50; dominant recipe fencepost_count -> bayesian_update, organism
  size capped at 2. Baseline matrix: decorative. Label: LATER OVERTURNED
  (the representation was abandoned for Branch C).

A-4 Branch C Phase 0 composition gauntlet (05-24..05-29). Hand-built
  compositions pass (COMP_A lift +0.733, COMP_C +0.533), control fails;
  LLM JSON-DSL dry run 100/100 type-valid. Label: REPORTED POSITIVE
  (construct validity, not evolution).

A-5 Branch C Runs 1-2 and R2 (05-29..06-10). Plateau best_acc 0.392 (Run 2
  gen 2668) / 0.42 flat for 481 gens (R2 run); diagnosed as a type-bridge
  gap (no op read derived_facts and wrote relations). Label: REPORTED
  NEGATIVE/NULL, then explained (expressibility).

A-6 Recombination falsification + A/B (06-16). 0/8000 single-step walks
  reach the solver; crossover 6.1% solve rate per op; de novo solver 4/5
  seeds with crossover vs 0/5 without. Replayed 08-19: 3/5 vs 0/5, 8.6x
  slower ("capability replays; search efficiency does not"). Label:
  REPORTED POSITIVE (replicated in direction, n=5).

A-7 Production crossover run run_branch_c_xover (06-16, died at gen 443 of
  3000, cause unrecorded because shell redirection zeroed console logs).
  best_acc 0.392 -> 0.558 at gen 15; novel_multitier 61 (inflated by
  duplicate variants). Label: MIXED.

A-8 0.558 diagnosis (06-22). Plateau = metric artifact (one fixed-terminal
  pipeline scored against a battery needing >= 3 terminals; portfolio
  0.758) + canary floor. Label: INSTRUMENT FAILURE (metric).

A-9 Dispatch arc (06-22..06-28). Dispatch falsification G1-G4 PASS
  (ingredients-seeded, 2-type battery); deterministic 0.558 -> 0.683 ->
  0.708 (boolean primitives + dispatch_merge) -> 0.833 (aggregate guard
  slot fix); llm2 run 800 gens, 24 h: max_acc 0.833 reached at gen 131 then
  669 gens of nothing, "Zero lift from Granite", genuine_routing false.
  Label: REPORTED POSITIVE at the time; LATER OVERTURNED by A-13 (E9).

A-10 Tier A ablation-wall corpus (08-15). 26 walls / 4 classes + 2
  controls; three walls killed by their own telemetry before release.
  Label: REPORTED POSITIVE (corpus delivered) with explicit limitations.

A-11 Type-bridge metabolic cycle (08-19). Preregistered arms A0-A3 (n=5
  each): discovery only with bridge AND crossover (A3 3/5; others 0/5).
  Verdict SUCCESS; classification "search_operator -- crossover
  NECESSARY". Label: REPORTED POSITIVE (small n).

A-12 Benchmark attack + O1 enumeration (08-23). Portfolio-coverage claim
  falls (dumb-rule oracle 0.925 > 0.833); single-organism 0.833 survives vs
  0.35/0.45. O1: evolution 3,144 evals vs enumeration 1,687,896 (537x);
  enumeration ceiling also exactly 0.833 with identical per-subset profile;
  two invalid O1 runs (tail cap 3; 4 orderings) would have produced false
  wins and were archived. Label: MIXED.

A-13 Campaign 2026-08-25 (E1, E9; E3/E11/E5 halted). E1: 86.7% of operator
  pairs commute; O1 sampling covered all behavioural schedule classes
  (SURVIVES). E9 on Charon's blind 42-task battery: mix-adjusted 0.0667 vs
  home 0.6000 (FAIL), 40/42 abstained, 0 guesses; numeric_comparison 0/6,
  numeric_stated_premise 0/6, transitivity 2/6. Stop rule fired; campaign
  halted. Label: REPORTED NEGATIVE/NULL (E9) -- and LATER OVERTURNED for
  every earlier accuracy claim.

A-14 Gen-2 vertical slice (09-01). /v0 Foundry, f(x)=3x+1, budget 300:
  neither map_elites nor random solved (best 0.1); MAP-Elites 11/64 cells
  coverage 0.172; replay 1/1. Label: INCONCLUSIVE (plumbing milestone).

A-15 S1 Archive Value Test pilot + cross-engine calibration + gate
  (09-01). Pilot at budget 80: DEAD (random) world MAP-Elites coverage
  0.1875 and QD 0.833 vs aff_3x+1 coverage 0.1875 and QD 0.083; dead-world
  best fitness 0.167 vs 0.083 on live worlds (run JSONs). Reachable-solve
  set {identity, x+1} on stackvm and pyshgp; treegp 0.000 everywhere
  (suspected adapter defect). Gate on stackvm FAIL (G1: only abs/threshold
  reach 0.5). HITL ruling: S1 BLOCKED/UNSCORED "NO NONTRIVIAL SOURCE
  POPULATION AT FEASIBLE COST"; mining suspended. Label: INSTRUMENT
  FAILURE (substrate cannot host the test) / BLOCKED.

A-16 Gate eligibility (09-11). INDETERMINATE: no eligible input
  (GATE_ELIGIBILITY_2026-09-11.json). Label: UNKNOWN (nothing could fire).

A-17 Legacy Task 2 state injection (raw / oracle / corrupted arms on the
  E9 organisms over Lexis's fixture). Accepted 09-11 (2b7c6e4fb), never
  preregistered or run. Label: UNKNOWN (not run).

## 9. False-positive / false-negative archaeology

T1. "Hybrid LLM strategy was working" (April).
- Claim: autopsy 2026-05-13 calls 50/50 Qwen+DeepSeek outperforming pure
  Qwen "a real positive signal, not noise".
- Evidence: April 9 report best +0.690 vs +0.670, median +0.615 vs +0.375.
- Challenge (this crawl): the same report's run table lists "4400 (0% DS)"
  and "4461 (0% DS)" LLM calls for the two "50/50" runs -- DeepSeek
  contributed no calls; elites came from drift and seed only. Difference of
  0.02 on one run pair.
- Status: unsupported as stated. [CORRECTION, crawl-level]

T2. "LLM mutations do not survive selection" (April -> May).
- Claim: llm_alive=0 for ~870 gens. Correction: drift() replaced
  mutations_applied instead of appending, wiping LLM lineage; fix ->
  24/50 LLM-derived (e94ca44b1, 05-22). Status: instrument artifact.
  [CORRECTION]

T3. "Composition" in v2 (May).
- Claim: fencepost_count -> bayesian_update recipe is a composition passing
  the ablation gate. Challenge: baseline matrix 0/5 elites beat the best
  single primitive; the gate measured output change, not accuracy.
  Correction: accuracy-delta gate (3ebdad8b4). Status: decorative.
  [CORRECTION]

T4. Plateau 0.558 as a capability wall (06-22) -> metric artifact (CAL-05).

T5. "Aggregate sub-pipeline falsified" (06-26) -> guard read a slot nothing
  wrote; fixed, synth 15 -> 30 (CAL-04, 48eb0102b). A false NEGATIVE caused
  by wiring.

T6. Climb to 0.833 as evolutionary discovery.
- Claim: dispatch arc 0.392 -> 0.833. Challenge: O1 (08-23) shows
  enumeration reaches exactly 0.833 with the same profile; "each step was a
  human raising the expressivity ceiling"; 5/5 widenings human-supplied.
  Status: search was sample-efficient, not inventive. [CORRECTION]

T7. Portfolio coverage as "the real capability metric" -> falls to a
  0.925 oracle over 13 dumb rules (3faa49219). [CORRECTION]

T8. 0.833 as capability -> E9 (08-25): 0.0667 on an independent author;
  total non-recognition via problem_text-surface preconditions. "0.833
  measures our task authorship rather than Apollo's capability, and this
  retroactively discounts every accuracy number in the Apollo corpus"
  (9b00453ca). [LATER OVERTURNED]

T9. "0.833 is the substrate's ceiling" (08-23) -> narrowed 08-25: v2's
  blackboard rewrite DROPPED the 25 Frame H primitives; three of four
  unsolved categories had a primitive there ("self-inflicted amputation",
  3c80230ab); then 09-01: the ceiling is of a contaminated battery, while
  the 537x ratio stands because both arms share the evaluator (e367307da).
  [CORRECTION, twice]

T10. "Canary compare tasks unsolvable without a boolean primitive" ->
  falsified by Aporia P153: 10/10 through existing ops (3c80230ab). And the
  "abstaining honest router" rationale was wrong in its stated reason.
  [CORRECTION]

T11. MAP-Elites coverage as differentiation (09-01) -> dead-world control
  matches coverage exactly (0.1875) and beats live worlds on QD (CAL-10).
  [CORRECTION; program lesson "diversity is an unsafe observable"]

T12. Gate population mass read from a non-existent key (CAL-09) -> green
  for the wrong reason, fixed same day.

T13. Atlas buried signal C5 says the crossover "prescribed flag flip was
  never found done" (ATLAS_BURIED_SIGNALS_AND_RESIDUALS.md row C5). The
  CLI default is 0.0 (blackboard_evolve.py:802), but STARTUP.md records
  production runs launched with `--crossover-frac 0.3` (run_branch_c_xover
  06-16; dispatch runs 06-24..06-28) and the type-bridge cycle's A3 arm.
  Atlas's reading is contradicted by the seat's own run commands; the
  default itself was never changed. [CORRECTION of Atlas]

False-negative regimes:
- Gen-2 S1: "no nontrivial source population" was measured at budgets
  80-600 on 12-case integer tasks with drivers that, on the same Foundry,
  had shown tie-dominated selection (Daedalus dossier, WOW R2) and with a
  treegp adapter that could not solve identity. The substrate (stackvm with
  loops and memory) was not shown incapable; the budget, task, and adapter
  were. Commit c6a2b2a44 says so: does "NOT establish that much larger
  budgets or a different world type ... wouldn't host it".
- E9's failure was located in parsers; the downstream routing/inference
  question ("parser failure or capability failure?") was never answered
  because Task 2 never ran.
- LLM mutation was judged useless in a regime where the registry was
  exhausted (ceiling reached at gen 131); it was never tested where the
  search space was not already enumerable.
- v2 runs were judged by an accuracy margin over a zlib NCD baseline that is
  itself a weak floor; the flat-landscape failure (0% accuracy at gen 90)
  was a task/representation mismatch, not evidence about evolution.

## 10. Research outputs

- apollo/archive/v1/{design_v1,v2,v3.md, council_feedback_1.md,
  answers_round_1-3.md, review.md, journal.md} -- the original design and
  council Q&A; external landscape scan (DEAP, pymoo, EvoTorch, geppy, ...).
- apollo/ARCHITECTURE.md (v2_d gradient-recovery diagnosis), ROADMAP.md
  (v2.1, cross-council research, 74+ citations per RESUME), RESUME.md
  (Aporia 05-12).
- charon/research/package_30_apollo_evolutionary_gp/ (Gemini deep research,
  04-04).
- pivot/autopsy_apollo_2026-05-13.md (Aletheia); pivot/apollo_value_
  proposition_2026-05-17.md; pivot/m2_apollo_revival_prompt_2026-05-17.md.
- apollo/pivot/: apollo_forge_handoff_2026-05-29, apollo_forge_reply_
  2026-06-09, r2_run1_findings_2026-06-10, recombination_findings_
  2026-06-16, diagnose_0558_findings_2026-06-22, dispatch_design_2026-06-22,
  dispatch_falsification_findings_2026-06-24, dispatch_arc_writeup_
  2026-06-27, RESUME_apollo_2026-06-15, benchmark_attack_2026-08-23.json,
  replay_claims.json, *_result_*.json; APOLLO_REVIVAL_REVIEW_2026-09-01,
  APOLLO_GEN2_SLICE_REVIEW_2026-09-01, APOLLO_S1_REVIEW_2026-09-01.
- apollo/cycles/type_bridge/{PREREGISTRATION,LINEAGE,RESULT}; campaign_
  20260825/{PREREGISTRATION, E1_RESULT, E9_RESULT, E9_FINDINGS};
  o1_enumeration/; S1_archive_value/{PREREGISTRATION, PILOT_FINDING,
  CALIBRATION_FINDING, RULING_2026-09-01, gate/}.
- apollo/wall_corpus/ (MANIFEST, corpus.jsonl, 26 walls).
- roles/Charon/apollo_e9/ (blind battery and builder).
- External: Harmonia four-lens panel and STRATEGY_2026-08-12 + ADDENDUM_A
  (pivot/, cited from STARTUP; not read here).

## 11. Journals, TODOs, pivots, abandoned branches

- roles/Apollo/STARTUP.md = Gen-1 frontier log 2026-05..08 (dated entries).
- roles/Apollo/journal/2026-09-11.md; apollo/archive/v1/journal.md (03-26).
- roles/Apollo/BACKLOG_H0H5.md (22 rows; APOLLO-04 and -22 XL operator
  decisions; APOLLO-10/11 Task 2).
- roles/Apollo/CALIBRATION.md (CAL-01..CAL-11).
- Pivots and why:
  1. v1 -> v2 (April): AST splicing stalled at NCD baseline; move to
     primitive-routing DAGs with LLM mutation.
  2. ~04-25 -> 05-17 idle (attention pivot per RESUME; "UNKNOWN, most likely
     the April 25 attention pivot"); autopsy recommends reconciling the
     primitive grammar before revival.
  3. 05-22 baseline-matrix falsification -> Branch C blackboard (05-24):
     representation replaced because compositions were decorative.
  4. 06-16 search-operator pivot: crossover added.
  5. 06-22 metric/organism-model pivot: dispatch.
  6. 06-28 -> 08-12 ~6-week break; 08-12 program strategy and four-lens
     panel; 08-13 freeze; R9 re-aim on hold.
  7. 08-23..08-25 external review campaign; E9 kill; stop rule.
  8. 09-01 Gen-2 reassignment to Serendipity substrate mining; S1 blocked;
     mining suspended the same day.
  9. 09-11 base-role adoption; dormant.
- Abandoned: Apollo v2.1 P0 (NSGA-III, stagnation) partially done; the
  50,000-gen continuous daemon; lanes A-D and jobs A-L (never installed --
  MONITORS.md row "NEVER INSTALLED"); E2/E3/E4/E5/E6/E7/E8/E10/E11; E9b
  second battery (requested from Techne/Diomedes, never produced); Task 2;
  the "apollo/runs" stream Talos expected never existed (agents/talos/
  CHARTER.md:96 names apollo/runs or apollo/organism_runs; MONITORS.md:
  "apollo/runs (never existed)").
- Branches/worktrees: F:/Prometheus-worktrees/apollo-base-role (HEAD
  2b7c6e4fb, 09-11); no origin/apollo* branches.

## 12. Lens inventory

L-A1. Composition-over-fixed-operators lens (Branch C blackboard)
- Substrate: typed pipelines of hand-written operators over a blackboard.
- Organisms: op lists with guards. Worlds: static text-task batteries.
- Pressures: accuracy, composition lift, load-bearing dataflow.
- Phenomenon family: compositional routing / dispatch; multi-op valleys
  and the role of recombination in crossing them.
- Resolving mechanism: per-branch ablation, shuffled-slot null, O1
  enumeration (ground truth for the reachable set), E1 schedule classes.
- Resolution ceiling: the registry (enumerable in ~1.7M pipelines); battery
  authorship (E9).
- Noise: parser/battery co-adaptation; padded candidate strings; n=5 seeds;
  metric churn.
- Architectural limit: operators are complete human solvers; no loops,
  memory, or operator minting.
- Reusable: O1-as-ground-truth method, E1 semantic schedule classes, the
  wall-corpus firewall, write-write hazard static check, stop rules.
- Toy-grade: the task battery and the operator library.
- Unknown: whether routing survives semantic (not surface) parsing.

L-A2. Recombination-across-valleys lens
- Phenomenon: single-step vs crossover reachability of multi-op solutions.
- Mechanism: 1-edit neighbourhood census, random walks, A/B with seeds.
- Ceiling: n=5; replay 8.6x slower; one valley shape. Atlas A15 contrasts
  NPE/SFE/CW01 (recombination harmful/null) -- a cross-engine geometry
  worth revisiting, not a result.

L-A3. Archive-value / source-viability gate lens (Gen-2)
- Phenomenon: whether an archive's population is worth mining; absolute
  calibration before relative comparison.
- Mechanism: G1-G4 with dead-world discrimination. Ceiling: depends on an
  external search-capable engine; none exists. Reusable: the dead-world
  control as a negative control for QD coverage claims.

L-A4. Benchmark-attack / independent-authorship lens
- Phenomenon: how much measured capability is authorship or trivial cue.
- Mechanism: trivial-heuristic battery and oracle; blind third-seat
  batteries with mix-adjusted endpoints. Reusable across engines.

## Open questions / unknowns

1. Where are the Gen-1 raw run directories (M2 D:\Prometheus\apollo\run_*,
   checkpoints, evolve_log.jsonl)? Only stubs are in git.
2. Would Task 2 (oracle state injection) show that routing/inference works
   once parsing is given? Never run.
3. Does the transitivity 2/6 on Charon's battery reflect partial semantic
   parsing or chance?
4. Was treegp-deap mis-wired in the D-13 Foundry (shared question with the
   Daedalus dossier)?
5. Operator decisions APOLLO-04 and APOLLO-22: never recorded.
6. Did anything consume Apollo's fossils, wall corpus or E9 artifacts
   (APOLLO-07/08 Evidence Wiki submissions blocked on EW timeouts)?
7. Artemis #872 (to Apollo, 09-28): subject only; body not retrieved.
