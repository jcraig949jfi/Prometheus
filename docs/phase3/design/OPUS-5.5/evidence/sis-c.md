# sis-c evidence digest: Proteus, Ludus, Herakles, Rhadamanthus (+ engine_index census)

Reader: read-only evidence reader for EPIMETHEUS (OPUS-5.5), 2026-10-01.
Worktree: C:/prometheus-worktrees/epimetheus-phase3 (HEAD 4c071e3c5). Nothing executed beyond
read-only python one-liners over committed JSON/JSONL and `git show` of historical blobs.
Independence: nothing under docs/phase3/design/ other than OPUS-5.5/ was opened; nothing under
roles/Dionysus/ was opened; no holdout/secret path was opened.

Epistemic tags: IMPL (read in code/data), INTENT, HIST, REPORTED (unverified result), CORR (later
correction), INFER (my inference from code), UNK. "Confirmed" means I opened the underlying artifact.
Crawler dossiers (docs/phase3/intake/sisyphus/seats/*.md) and engine_index.jsonl are treated as
leads, not truth; where a claim mattered I opened the source and say so.

-------------------------------------------------------------------------------------------------
## 0. Bottom line for the architect (ten lines)

1. None of these four seats ever ran an adaptive organism inside a world that DEMANDED a reasoning
   primitive and could be shown to demand it. Proteus built organisms but owned no world; Ludus built
   exact worlds but never had an organism (no binding, no importer: IMPL, git grep); Herakles built a
   calibrated CA ruler around fixed 1990s genomes and never re-ran the evolution; Rhadamanthus judged
   dead v1 LLM-pipeline software, not ALife lineages. The fossil record here is an INSTRUMENT FOUNDRY,
   not a record of developmental emergence.
2. The strongest positive evidence in the group is known-answer calibration: Herakles reproduced 17/18
   published EvCA cells (maj exactly 0.000 over 16,000 ICs), JP98 15/15, ABK96 4/4 (IMPL, report
   files opened). That proves a ruler and a substrate implementation, not a phenomenon.
3. PROTEUS-46 (the "cliff survives" falsifier that later blocked Deep Frontier transformations) is a
   valid narrow true negative (0 USEFUL single edits around one hand-written witness on both
   substrates) wrapped in a search_insufficiency: verified in code, its greedy walk can only move on a
   strict two_key improvement, so it never moved; the "3-step greedy walk" was in effect 15,000 more
   single-edit samples of the parent (INFER from IMPL falsifier_46.py:113-131). A 5-edit neutral
   duplicate-and-diverge path to 6/6 exists (REPORTED, Artemis D002-03q), and the direct 2-edit fix
   passes through DESTROYED (0/6) intermediates (REPORTED, D002 part A).
4. The mutation-kernel crucible is a genuinely novel lens (measure the probability current of the
   unselected variation operator), but its state space is only (genome_length, tape_words) (IMPL
   kernel.py:6-8), its reversible-reference control cannot fail by algebra (IMPL kernel.py:321-351;
   CORR Harmonia 2026-09-18), and it was admitted as a detector only, never as an absence instrument.
5. Ludus's lasting contribution is the discriminability question ("could this world separate X from a
   four-line heuristic?") and the instruments that answer it, and their measured blind spots: GATE-W1
   admits normal-play Nim although Bouton's xor rule is optimal (IMPL CONTROLS_2026-09-16.json); the
   differential leak audit fired on 4/4 injected leaks where the key-name check fired on 1/4 (IMPL).
6. Most "verdicts" in this group that were later overturned were overturned by RULER or PROVENANCE
   repairs, not by new data about the phenomenon: near-terminal sampling (Ludus 0.900 -> 0.412),
   rules-from-memory (Martian Dice 86% -> reversed), exposure x competence (cycle 004 -> demoted), a
   tie rule that stops at pot=0 (IMPL circuits.py:121), a control that cannot fail (Proteus V0.5),
   a confound by arm asymmetry (HC-T01 beta=0 arm cannot build operators; IMPL corrections file).
7. HC-T01 is the only evolutionary run in the group with a real developmental genotype (string
   rewriting with second-type representational operators). Durable residue: history changes measured
   local accessibility at 24-108x estimator noise (REPORTED, retained after correction). Mechanism
   reading: largely presence of >=1 production rule (RA-2, rank R^2 0.739; IMPL corrections file).
   Prospective value of accessibility: UNANSWERED (RA-1 INDETERMINATE).
8. The Necropolis admissibility ladder (PATH_EXISTS -> IMPORTS -> EXECUTES -> CONTROLLED ->
   ADMISSIBLE) is real data on 93 instruments: 45 admissible, 21 blocked only because their controls
   are author tests (IMPL TOOLS.jsonl tabulated). Its own validator catches 11/11 structural law
   violations but lets 7/8 cheat cases through (IMPL validator_negative_tests_result.json).
9. The Necropolis has no ingestion path from any evolutionary engine (IMPL: the only .py references
   outside engine/necropolis are comments in v1-era/forensic files). The one TRUE_CORPSE ever issued
   (Hephaestus, 9af40af34) disappeared when a fair_test field was introduced (c7340a6ad; IMPL git
   show). No planted fair-test-then-failed grave exists, so whether TRUE_CORPSE is reachable is UNK.
10. Across the whole engine_index (51 engines, REPORTED by the crawler), the maximum cognitive demand
   any world was SHOWN to impose and any organism was SHOWN to meet is roughly a one-bit latch or a
   one-step lookup; richer demands (two-stream keyed memory, procedure reuse, hidden-state composed
   worlds) were posed and not reached, or posed with rulers that saturated (section 6).

-------------------------------------------------------------------------------------------------
## 1. What was really built (engine table, my group)

Fourteen engine rows in engine_index.jsonl for these seats; they match the seat fragments byte for
byte (IMPL: python comparison). Corrected / sharpened against source where I read it.

| engine | organism actually present | world actually present | pressure actually present | ruler | max cognitive demand the world imposed |
|---|---|---|---|---|---|
| proteus.foundry v0 | 25-op total bytecode VM (op = word mod 25, IMPL vm.py:181), regs<=16, tape<=4096, optional self-modification, persist policies; no call/return, positional jumps | none owned; probe ensemble = 4 noise probes, <=3 channels, <=6 ticks, 256 ops/tick, "no task" (IMPL probes.py:20-28) | none (charter R8); 12-op syntactic grammar applied by consumers | transcript hash (degenerate: 3 classes, 4/56 players emit anything, IMPL RESULT_TRANSCRIPT_DEGENERACY.json), knockout vector, meter projection | none inside Proteus; witness tasks (hand-written) up to keyed two-value memory |
| mutation-kernel crucibles V0.3-V0.6 | unselected genomes as Markov states | enumerated structural space (L, T): 124 states (V0.5), 2,044 (V0.6); content marginalised by sampling uniform random genomes (IMPL kernel.py:10-15, 54-87) | none: the null process of variation | J = pi_i P_ij - pi_j P_ji, A/B noise floor, entropy production, reversible reference (cannot fail), dual kernels | none (null-process science) |
| proteus.graph graph_organism.v1 | graph VM: 25 node kinds, data+control edges, ROUTE, CALL/RETURN, dormant nodes; graph_grammar.v1 13 ops with masses (IMPL grammar.py:44-58) | same opaque-channel ABI; only hand-written witnesses + Archaeon consumers | connectivity edits; NODE_ADD and SUBGRAPH_COPY attach dormant BY CONSTRUCTION (IMPL grammar.py:13,21) | PROTEUS-46 classes USEFUL/GRADED_DOWN/DESTROYED/NEUTRAL/NEUTRAL_DIFF; behavior_fingerprint.v1 | two-key probe: keyed 2-slot memory (6 asks) + 16-ask all-keys probe; never reached by search |
| proteus.eval toolkit | v0 and graph organisms | Boolean truth tables (3-4 inputs), keyed-memory witness | none | exhaustive oracle checks; permutation floors (anatomy, uncorrected) | 3-4-input lookup; keyed memory (constructive witness, REPORTED) |
| Ludus cycle-001 | LLM (gpt-oss-120b, n=20/cell) and greedy/depth-k baselines | LOOM/WEIR/TITHE 2-player deterministic perfect-information, exactly solvable | none | r0001 greedy gap; r0002 gap(k) k<=4 with world's own score at cutoff (IMPL depth_profile.py) | <=4-ply lookahead; gap(4) .000/.012/.040 (IMPL CONTROLS regression rows) i.e. essentially greedy lookup |
| Ludus bench | hand-written Python circuits on SELECT/STOP interface | single-agent stochastic stopping/selection; exact V/W backward induction (IMPL core.py:34-42, 115+) | none (authoring, parameter knobs) | exact EV retention, axis decomposition, 400-cell factorial, reference-occupancy regret | one-step EV comparison: myopic rule retains .9991 on Flip 7 (REPORTED CYCLE_002) |
| Ludus arena | Python policies | TTT, Nim, Pig, RPS, Kuhn, Ball-under-couch; chance/simultaneous/observation(i) | none | theory reproduction (Kuhn -1/18, Nim xor, TTT draw), differential leak audit | small equilibria; hidden-state inference only in Kuhn/epistemic world; no organism ever placed |
| Ludus Atlas of Game Worlds | none | 1,338 catalogue rows, 0 executable, 0 audited (HIST) | none | heuristic tags, accuracy never measured | none |
| herakles.evca | ONE fixed 128-bit radius-3 rule table; 6 genomes in library (IMPL genomes.py keys) of 11 recovered | 1-D periodic binary ring, odd N 149/599/999; IC ensembles | none internal | six criteria with measured floors (IMPL CRITERIA.md); reproduction within z*SE | global majority from 7-cell local view: emergent distributed transport (particles); no memory, no input channel |
| herakles.eca | 8-bit Wolfram rule | rings N=7-11, exhaustive ICs | none | terminal-state equivalence classes; block_output | lookup / enumeration |
| herakles.ca_stream | historical density rules as reservoirs | 31-cell ring, one injected port, 256-stream catalogue | none | 32-param linear ridge readout + shift-register/xor/direct/frozen-random controls | delayed recall d<=3, temporal xor d<=1; substrate provably inert so demand never engaged |
| HC-T01 (hct01.c) | egg string + ordered list of <=32 rewrite operators over 8 letters; development T=1 (IMPL hct01.c:1-37) | fixed periodic target phenotype, length 25, period 5 | (mu,lambda)-style selection on target match, lambda 100, 1000 gens; Poisson first-type + second-type mutation | 2000-sample offspring detector per individual per generation; estimator-noise floor; K1-K7; RA-1/RA-2 | target-string matching; the measured phenomenon is evolvability, not cognition |
| Necropolis court | dead v1 Prometheus software agents (48-row roster) | repository history, surviving DB channels | none; separated forensic readers, HITL | nine-layer cause-of-death stack, fair_test, validator | n/a |
| Necropolis workshop | 93 forensic instruments | none | none | admissibility ladder, 194 Keeper controls | n/a |

-------------------------------------------------------------------------------------------------
## 2. Source follow-ups (what I opened and what it showed)

### 2.1 PROTEUS-46 and greedy tie rejection (confirmed, and sharper than the crawler said)

Files: proteus/round2/falsifier_46.py, PROTEUS-46_PREREGISTRATION.md, PROTEUS-46_FALSIFIER.md;
roles/Artemis/dispatch/D002/RESULT.md and scripts/D001-03.py.

- Prereg question (INTENT): does connectivity-level variation change search geometry around programs
  v0.4 sees as a cliff? Parent one_value scores 3/6 on two_key; keyed scores 6/6. K=400 children per
  operator per parent; floor = |batch A - batch B| within substrate; walks secondary, "never move the
  verdict". Self-dissent: the graph one_value is the keyed graph minus two address edges, "two edge
  retargets away by construction".
- Result (IMPL, committed result file): USEFUL 0/4,267 (v0.4) and 0/4,881 (graph); GRADED_DOWN
  .0075 vs .0006; DESTROYED .7047 vs .3567; NEUTRAL .2740 vs .6417. Verdict CLIFF_SURVIVES,
  falsifier_status FALSIFIER_FAILED, neighbourhood_exhausted False, departures "none".
- Greedy walk (IMPL falsifier_46.py:113-131): `best, best_key = m, (cur, 0)`; child key = (two, -ops).
  A child is accepted only if key > best_key. Since -ops <= 0, an equal-score child (NEUTRAL or
  NEUTRAL_DIFF) can never beat the parent's sentinel (cur, 0); graded-down children cannot either.
  Consequence (INFER): the walk moves only on a strict two_key improvement; with USEFUL share 0 it
  never moved (best two_key seen 3 on both substrates), so each "3-step path" was 150 independent
  single-edit draws from the same parent: 15,000 extra single-edit samples per substrate.
- Departure not recorded (INFER): the prereg says "each step: 50 children, keep the best two_key
  score, ties -> lowest ops", which reads as choosing among CHILDREN; the code includes the parent with
  an impossible ops=0 sentinel. The file reports "departures: none". Class: implementation_defect in
  the secondary arm / search_insufficiency.
- Dormant neutrality (IMPL result table + grammar.py): NODE_ADD, EDGE_ADD, SUBGRAPH_COPY,
  SUBGRAPH_COPY_ATTACH, CROSSOVER_SUBGRAPH all NEUTRAL 1.0000 on both parents. For NODE_ADD and
  SUBGRAPH_COPY this is by construction (dormant append). For EDGE_ADD, COPY_ATTACH, CROSSOVER it is an
  empirical 1.0000 on these witnesses (INFER: no live free port / unreached branch on a 12-node
  witness), not a property of the operator in general. These five operators carry 0.29 of the
  graph grammar's mass (.07 + .10 + .04 + .04 + .04, IMPL grammar.py:44-58), so 29% of graph
  proposals could not change behaviour on this witness by a single application.
- Artemis D002-03q (REPORTED; Fabric worker run, frozen rule, quick mode): part A both direct
  single fixes score 0/6 (DESTROYED); part B an explicit 5-edit duplicate-and-diverge path (add ST',
  wire address, wire value, splice, retarget LD) has steps 1-4 NEUTRAL at 3/6 and step 5 at 6/6.
  Neutral-drift walkers: 'score' mode 1/50 hit, 'strict' 0/50, control 0/50 (does not beat control);
  pop 50 x 100 gens never reached 6/6; full 500 x 3000 drift run timed out (no output).
- What the apparatus could reveal: (a) single-edit neighbourhood class shares around ONE hand-written
  witness per substrate on ONE neutral probe: yes, cleanly; (b) whether connectivity editing creates a
  graded path: no, because the only graded paths that exist (per D002) are >= 5 edits through neutral
  intermediates and both the primary statistic (single edit) and the walk (no neutral acceptance) are
  structurally blind to them. (c) Nothing about worlds or evolved organisms (declared limits).
- Downstream: the verdict became a frontier suppression (archaeon/frontier/suppressions/PROTEUS-46.json;
  HIST 299,991 echo rows per comms #735 via dossier). Scope extrapolation from one witness pair to a
  frontier-wide block is a provenance/interpretation failure, not a property of the falsifier, which
  itself declared neighbourhood_exhausted False.

### 2.2 Mutation-kernel crucible (confirmed)

Files: proteus/v0_5/kernel.py, proteus/v0_5/ADJUDICATION_V0_5.json,
roles/Harmonia/rulings/RULING_PROTEUS_CURRENT_INSTRUMENT_AND_R4_2026-09-18.md (sections 0-1).

- State = (genome_length in instructions, tape_words) only; kernel P(i->j) measured from the live
  operator by drawing a fresh uniformly random genome per sample; rejected proposals counted as
  self-loops; truncation folded into self-loop and reported (IMPL kernel.py:1-87). So the instrument
  sees structural drift marginalised over random content; it cannot see content-level directionality
  or anything conditional on a selected (non-random) genome (INFER).
- reversible_reference (IMPL kernel.py:321-351) builds Q_ij = (pi_i P_ij + pi_j P_ji) / (2 pi_i);
  detailed balance holds by algebra, so max |J| ~ 2e-19 measures floating point (CORR Harmonia: "CANNOT
  FAIL"; 0.0 on a synthetic kernel too). Harmonia also: occupancy TV 0.019747 vs a "floor of about
  0.019" is NOT A MEASUREMENT (floor quoted); per-pair rows not committed. Verdict: ADMITTED AS A
  DETECTOR (166/506 pairs above floor 4.156e-05; sigma 9.975e-03), NOT ADMITTED as absence instrument
  until a positive control at declared magnitude (MDC) and a floor guard exist (CORR, confirmed text).
- V0.4 "halt/yield" content discovery: V0.5 confirmatory test v0_4_delta -0.0191, v0_5_delta
  +0.0118, z 1.90, one-sided p .9716, confirmed False; 0 of 350 global-family cells survive (IMPL
  ADJUDICATION_V0_5.json). A clean false_positive caught by a frozen confirmatory replication.
- Length "prior" in V0..V0.2 reclassified to joint boundary geometry by the NC5 symmetric-walk null
  (REPORTED via program packet; NC5 code exists, proteus/v0_4/nc5.py, not re-run).
- What it could reveal: that the authored variation operator is not detailed-balanced in structural
  coordinates (yes, as a detector). What it could not reveal: whether that current matters under any
  selection regime ("operational significance NOT YET ADJUDICATED"; Artemis D004 bias <= .004
  instructions, REPORTED).

### 2.3 Ludus exact worlds, depth, regret, leak audit (confirmed)

Files: ludus/bench/core.py (1-120), ludus/bench/circuits.py (90-150), ludus/depth_profile.py,
ludus/arena/audit.py (1-60), ludus/bench/occupancy.py (1-50), ludus/controls/CONTROLS_2026-09-16.json
(all 25 rows), roles/Ludus/CYCLE_005_verdict_demotion.md (head), CYCLE_001/002 (grep),
roles/Artemis/selftest/runs/R-32/REPORT.md (grep).

- Exactness (IMPL core.py): V(s) = sum_draw p max_options W(s2); W = pot or max(pot, V). Every bench
  number is exact arithmetic, not a sample. This is what made Ludus's negatives trustworthy AND what
  capped world size.
- Depth profile (IMPL depth_profile.py): uniform `rng.sample` of eligible states (LUDUS-34 confirmed:
  not stratified by plies-to-terminal despite the standing rule); the depth-k player takes
  `depth_actions(...)[:1]`, the lexicographically first of tied actions (INFER: tie-break can inflate
  gap(k) when a tied non-first action is optimal; magnitude UNK). Cutoff evaluation is the world's own
  score read early.
- Controls (IMPL, 25 rows): regression rows reproduce LOOM .000 all k, WEIR .012 at k=4, TITHE .040;
  negative CTRL_LEDGER 0 at all k; positive CTRL_ORCHARD gap(4) .3448; CHEAT Nim(3,4,5) gap(4) .2398
  exhaustive (517/517) -> ADMITTED; Nim(3,4,5,6) gap(4) .496 -> ADMITTED. So GATE-W1 cannot see a
  closed-form cheap policy. bench verify catches pot+1, a cycle, a large probability halving; misses a
  halved smallest probability (below 1e-7 tolerance) and a removed die face (blind to the draw law).
  key-name check fires 1/4 injected leaks; differential audit fires 4/4 (3, 4, 4, 9 separating signals)
  and 0 on clean Kuhn.
- r0003 tie rule (IMPL circuits.py:121): `return not (e_gain > p_dead * pot)` stops on equality,
  including pot = 0 with e_gain = 0. Artemis R-32 (REPORTED): tie-continue variant retains >= 0.944 vs
  every partner in 18 worlds, so the 0.0000 cells that triggered cycle 004 were plausibly manufactured.
- Cycle 005 (IMPL doc numbers): under REFERENCE occupancy circuit .8528 / world .0451 / circuit x world
  .1021 vs UNWEIGHTED .2623 / .1155 / .6222. Lesson: an on-policy outcome is exposure x conditional
  competence; per-decision regret against the optimal continuation is partner-free by construction.

### 2.4 Herakles known-answer calibration (confirmed)

Files: herakles/evca/c1e/REPORT.md, herakles/CRITERIA.md, herakles/evca/MAJ_STRUCTURAL_ZERO.md (grep),
herakles/ca_stream/OBSTRUCTION.md (1-70), specimen REPORT.md greps (JP98, ABK96, Capcarrere),
hct01.c header, HC_T01_CORRECTION_2026-09-03.md, HC_T01_REANALYSIS_CORRECTIONS.md,
roles/Elenchus/investigations/2026-09-11_epistemic_debt/LEDGER.md (C-04, C-05).

- C1-e (IMPL report): 17/18 REPRODUCED at Bonferroni band 2.99 SE; maj 0.000 exactly at three N over
  16,000 ICs (an exact prediction with zero tolerance). particle2 N=149: 0.733 vs 0.755 (4.97 SE),
  stable across five 10k-IC samples; suspects horizon, accuracy definition, IC ensemble,
  implementation ELIMINATED; transcription SURVIVES (untestable). The seat explicitly refused to search
  480 single-digit hex variants for one that fits (correct multiple-comparisons discipline).
- IC ensemble is a first-order variable (IMPL report table): under uniform-over-density ICs every rule
  jumps (maj 0.000 -> 0.443, GKL .807 -> .979). Capcarrere's ranking clause holds under Bernoulli(0.5)
  and fails under uniform-density (IMPL REPORT grep). A "pressure" defined by test distribution can
  reorder organisms.
- JP98 15/15 (coev1 0.8548, coev2 0.8574 at N=149 vs GKL 0.819); ABK96 4/4 at 10^6-10^7 ICs (IMPL
  report greps). These are the best-calibrated organisms in the program, and five of them (coev1,
  coev2, abk_gp, das1995, davis1995) are NOT in the executable genomes.py (IMPL: keys are maj, exp,
  par, particle1, particle2, GKL).
- CRITERIA floors (IMPL): at_T gives random tables the single point {0} (40/40), so no search from
  random starts gets gradient on it; cellwise floor 0.5 not 0; cellwise synchronisation is a BAND
  [0.057, 0.307] with a lost prediction kept visible; synchronisation has no solving positive control.
  Rules for adding a criterion: floor, eligible count, SE unit, positive/cheat/negative controls first.
- ca_stream v1 (IMPL OBSTRUCTION; CORR Elenchus C-04 EARNED): all six rules output 0 for every
  neighbourhood of popcount <= 1, so single-port injection from all-zero reset is provably inert:
  0/63,488 non-zero features. Controls on the same code path behave (shift register 1.0 delayed
  recall; shift+xor cell 1.0 xor; frozen random .49). Elenchus C-05 OVERSTATED: "a density classifier
  MUST annihilate a lone minority cell" is false (constructed counterexample), yet that modal claim is
  what barred "different rules" at alpha. v2 was approved (D-18) and never run.
- HC-T01 (IMPL corrections files): verdict downgraded to WEAK_SIGNAL_ONLY because beta=0 populations
  cannot evolve second-type operators (nops identically 0 in every beta=0 row) so the arms differ in
  available machinery; at the K7 window Spearman(current fitness, later gain) = -1.0000 exactly, so K7
  could not have come out otherwise; RA-1 INDETERMINATE; RA-2: md_on 0.341 at 0 ops -> 2.730 at 1 op,
  then +0.44 for all further ops; nops rank R^2 0.739. Durable residue: at identical phenotype and
  fitness the arms have different one-step reachable distributions, history effect 24-108x
  estimator noise, contemporaneous knob effect at or below noise (REPORTED, retained by both
  corrections). Literature claim "missing cell" withdrawn (one-author citation graph).

### 2.5 Necropolis admissibility ladder (confirmed)

Files: engine/necropolis/workshop/TOOLS.jsonl (tabulated), engine/necropolis/tests/
validator_negative_tests_result.json, engine/necropolis/dossiers/hephaestus.dossier.json at
9af40af34 / c7340a6ad / HEAD (git show), erebos.dossier.json (grep).

- Ladder (IMPL, every TOOLS row carries it): path_exists, imports (IMPORT_OK 80 / NOT_MEASURED 12 /
  IMPORT_FAIL 1), executes (KEEPER_CONTROLS 55 / AUTHOR_TESTS_ONLY 24 / NOT_MEASURED 12 / ERROR 2),
  controlled (KEEPER 57 / AUTHOR_ONLY 24 / NONE 12), admissible (45 True: EVIDENCE 38,
  EVIDENCE_WITH_CAVEAT 7; 48 NOT_ADMISSIBLE). Top blocker: "CONTROLLED (author tests only)" 21.
  Each row also carries forbidden_inference (e.g. NT-033 Herakles c3_null_check: "accuracy agreement
  alone cannot buy IDENTICAL"; NT-081 Proteus specimen gate NOT_ADMISSIBLE: "MEANING level is a
  declared check, not semantic truth").
- What the ladder measures: whether an instrument runs and was exercised by Keeper controls. It does
  not by itself certify detectability (planted positive recovered at a declared magnitude). INFER from
  field structure; control_state counts pass/fail but the ladder does not encode effect size or power.
- Validator (IMPL): 11/11 REJECT cases caught (e.g. TRUE_CORPSE with UNFAIR, HYPOTHESIS_FAILURE with
  UNFAIR, VALID with no evidence); 7/8 CHEAT cases pass unchecked (evidence-path existence, measured
  load_bearing, executed-vs-prose not enforced).
- Hephaestus (IMPL git show): disposition TRUE_CORPSE at 9af40af34 with NO fair_test field in that
  schema; at c7340a6ad fair_test UNFAIR, primary INSTRUMENT_ERROR, classification
  NO_FAIR_TEST_ON_RECORD, stack 7/9 layers INVALID. The only TRUE_CORPSE vanished when the
  fair-test vocabulary was added. Ruler change, not new evidence.
- Erebos calibration (IMPL dossier text, executed evidence not re-run): the committed pair-aware
  permutation null on synthetic 699-row ledgers detected 0/3 planted strong linkages; the Cleric's
  lift-only plant detected 1/3 with 1/3 null false positives at observed=2. A historical "signal" at
  observed=2 sat inside its own null. This is a textbook instrument-power result.

-------------------------------------------------------------------------------------------------
## 3. Results with evidence profiles

Axes: Q question could fail; S substrate capacity (constructive proof the organism can instantiate
it); W world demand (world requires it, ablated-capability baseline); R ruler validity (planted
positive / matched negative / error rates); B baseline discrimination; Rep replication (new seeds /
host / reimplementation, not replay); M mechanism (ablation removes, transplant restores).
Where a dimension is not applicable (no organism, no world) it is scored N with a note.

| id | claim (short) | reclassification | Q | S | W | R | B | Rep | M |
|---|---|---|---|---|---|---|---|---|---|
| PRO-01 | V0..V0.2 grammar has upward length prior (runs 1-3 FAIL) | ruler_insufficiency (no geometry null) -> hypothesis false; historic failure = boundary geometry (NC5) | Y | Y | N | P | P | P | P |
| PRO-02 | V0.4 halt/yield share differs at cohort 128 (z 3.53) | false_positive (statistical_insufficiency), killed by frozen confirmatory test | Y | Y | N | P | Y | Y | N |
| PRO-03 | Structural mutation kernel is nonequilibrium with authored current | instrument_positive (detector only); absence use not admitted; consequence unadjudicated | Y | Y | N | P | P | P | P |
| PRO-04 | A+B indistinguishable from parents (0/200) | ruler_insufficiency (transcript observable degenerate) -> composition question OPEN | N | P | N | N | P | N | N |
| PRO-05 | Meter projection discriminates beyond size | instrument_positive (observable qualified with identity, size floor, independent ceiling) | Y | Y | N | Y | Y | P | N |
| PRO-06 | Keyed memory is a 12-instr program; H1 Boolean exhaustive | constructive substrate-capacity proof (REPORTED, not re-run) | Y | Y | N | P | P | N | N |
| PRO-07 | PROTEUS-46: connectivity grammar does not remove the cliff | true_negative for single-edit USEFUL around one witness; search_insufficiency + implementation_defect in walk arm; scope overreach downstream | Y | Y | N | P | P | N | N |
| PRO-08 | ANATOMY_L0: structure of C4 specimens | statistical_insufficiency (24 uncorrected stats; none survive correction) | Y | U | N | P | Y | N | N |
| LUD-01 | Cycle 001: band empty; LLM = greedy | world_insufficiency (authored worlds greedy-decidable); true_negative about these worlds only | Y | P | N | P | Y | N | N |
| LUD-02 | Cycle 001: LLM 0.900 on game value | false_positive (near-terminal sampling; stratified 7/17 = .412) | Y | P | N | N | P | N | N |
| LUD-03 | Cycle 002: Flip 7 not measurable at stop (.9991) | world_insufficiency (true negative on discriminability) | Y | N | N | Y | Y | N | N |
| LUD-04 | Cycle 002: 86% of Martian Dice residual on claim axis | provenance_defect (rules from memory); reversed by publisher audit | Y | N | N | P | Y | N | N |
| LUD-05 | Cycle 003: prospective r0003 >= .97 in unbuilt worlds | survives (prediction held) on partially audited worlds; hand-written circuit transplant, not learning | Y | N | P | P | Y | N | N |
| LUD-06 | Cycle 004: CONTEXTUAL_BASIS_REQUIRED | false_positive: ruler_insufficiency (exposure x competence) + implementation_defect (r0003 tie rule) | Y | N | P | N | P | N | N |
| LUD-07 | Cycle 005: reference-occupancy regret demotes cycle 004 | instrument_positive (confound remedy) | Y | N | P | P | Y | N | P |
| LUD-08 | LUDUS-03 controls: gate admits Nim; verify blind to draw law; key-name 1/4 vs differential 4/4 | instrument findings (ruler_insufficiency measured, by design) | Y | N | N | Y | Y | N | N |
| LUD-09 | Arena reproduces textbook theory 20/20 | instrument_positive (known-answer) | Y | N | N | Y | P | N | N |
| HER-01 | C1-e: 17/18 published EvCA cells reproduced | instrument_positive (known-answer calibration); particle2 survives_as_anomaly (transcription lead) | Y | Y | Y | Y | Y | P | N |
| HER-02 | JP98 15/15, ABK96 4/4, Capcarrere footnote; ranking ensemble-dependent | instrument_positive + IC-ensemble sensitivity finding | Y | Y | Y | Y | Y | P | N |
| HER-03 | Criterion floors: at_T {0} for random tables; sync band | ruler calibration; shows pressure_insufficiency for search from random starts on at_T | Y | Y | Y | Y | Y | P | N |
| HER-04 | ca_stream v1: held rules cannot be stream memory (0/63,488) | world_insufficiency (interface provably inert); substrate hypothesis UNTESTED; modal generalisation overstated | Y | N | P | Y | Y | Y | Y |
| HER-05 | HC-T01: history changes future accessibility (24-108x noise) | survives_as_anomaly (accessibility differs) with confound (arm-asymmetric machinery); mechanism mostly machinery presence; prospective claim INDETERMINATE | Y | Y | N | P | P | P | P |
| HER-06 | C1-e vs Archaeon C3-2: 24/24 agree | statistical_insufficiency (n_ics=100: "no detectable disagreement") | Y | Y | Y | P | P | Y | N |
| HER-07 | Opening thesis: history lacked an accessibility microscope | hypothesis_failure (primary-source literature reads) | Y | N | N | P | N | N | N |
| HER-08 | ECA 256 rules -> 224/236 classes | scope-bound fixture (ring ceiling), terminal-state equivalence only | Y | Y | N | P | P | P | N |
| NEC-01 | Pollux/Erebos/Nous 3/3 UNFAIR, NO_FAIR_TEST_ON_RECORD | ruler_insufficiency of historical instruments shown by calibration (Erebos 0/3 planted); court ruler possibly biased (no planted TRUE_CORPSE) | Y | N | N | P | P | N | N |
| NEC-02 | Hephaestus TRUE_CORPSE -> NO_FAIR_TEST | ruler change (doctrine + schema), provenance not evidence | P | N | N | N | N | N | N |
| NEC-03 | Workshop: 93 tools, 45 admissible; validator 11/11 rejects, 7/8 cheats pass | instrument inventory with measured validator gaps | Y | N | N | P | P | N | N |
| NEC-04 | CR-001 Pollux resurrection plan DEAD_BEFORE_RUN | instrument working (plan killed by own positive control) | Y | N | N | Y | N | N | N |

Notes on scoring. S for Proteus kernel results = Y because the object of study (the operator) exists
and is enumerated. S for Ludus = N because no adaptive organism existed; circuits were hand-written.
W is N almost everywhere: no result in this group used an ablated-capability baseline to show the world
demanded a mechanism, except Herakles's density task (W = Y: the global-majority demand is classical
and the random/constant floors are measured) and ca_stream (P: delayed-recall demand is constructively
shown solvable by a shift register, not shown impossible without memory). M is Y only for ca_stream
(the obstruction is proven mechanistically: popcount<=1 outputs 0, verified independently by Elenchus).

-------------------------------------------------------------------------------------------------
## 4. Failure-shape catalogue (with direction)

| class | instance | direction | cite |
|---|---|---|---|
| search_insufficiency | greedy walk accepts only strict improvements; cannot traverse neutral plateaus; path length 3 < 5 | false negative | proteus/round2/falsifier_46.py:119-128 (IMPL) |
| implementation_defect | prereg "ties -> lowest ops" among children implemented with parent sentinel (cur, 0); departures "none" | false negative | falsifier_46.py:119; PROTEUS-46_PREREGISTRATION.md s2 (INFER) |
| ruler_insufficiency | control that cannot fail (reversible reference, detailed balance by algebra) | false reassurance | proteus/v0_5/kernel.py:321-351; Harmonia ruling s1 |
| ruler_insufficiency | quoted, not computed, floor (occupancy TV) used for an absence claim | false negative | Harmonia ruling s1 |
| ruler_insufficiency | degenerate observable (transcript: 3 classes, 4/56 emit) read as "composition adds nothing" | false negative (caught) | proteus/v0_7/RESULT_TRANSCRIPT_DEGENERACY.json |
| ruler_insufficiency | identity observable polluted by timings (raw meter 0/40 reproducible) | noise | proteus/v0_7/RESULT_METER_FLOOR.json part0 |
| statistical_insufficiency | class-count richness at chance (37 ops classes vs null median 36) | false positive (caught) | RESULT_METER_FLOOR.json part1 |
| statistical_insufficiency | single-coordinate z 3.53 in a 350-cell family | false positive (killed) | proteus/v0_5/ADJUDICATION_V0_5.json |
| ruler_insufficiency | boundary geometry mistaken for directional prior | false positive | dossier T1; proteus/v0_4/nc5.py (exists) |
| ruler_insufficiency | discriminability gate blind to closed-form cheap policies (Nim admitted) | false positive (world admitted) | ludus/controls/CONTROLS_2026-09-16.json |
| ruler_insufficiency | uniform state sampling over-weights near-terminal states (0.900 vs .412) | false positive | roles/Ludus/CYCLE_001_ceiling.md:310-323; depth_profile.py:75 |
| ruler_insufficiency | on-policy outcome conflates exposure and competence | false positive | ludus/bench/occupancy.py docstring; CYCLE_005 |
| implementation_defect | tie rule stops at pot=0 manufacturing 0.0000 cells | false positive (partner dependence) | ludus/bench/circuits.py:121 |
| provenance_defect | game rules reconstructed from memory (Martian Dice EV 2.09 -> 3.11) | false positive (axis claim) | dossier LC2; rules_audit.json (not opened) |
| ruler_insufficiency | verifier blind to the draw law; leak check by key name | false reassurance | CONTROLS_2026-09-16.json |
| world_insufficiency | authored "strategic" worlds greedy-decidable; solitaire stopping worlds near-solved by a one-step rule | true negative about worlds, not about reasoning | CYCLE_001; CYCLE_002 |
| world_insufficiency | interface makes substrate provably inert (single port from zero reset) | false negative for substrate hypothesis | herakles/ca_stream/OBSTRUCTION.md |
| hypothesis_failure (modal overreach) | "density classifier MUST annihilate a lone cell" used to bar alternative rules | false negative (routing) | Elenchus LEDGER C-05 |
| organism_insufficiency / design confound | treatment arm alone can build operator machinery (beta=0 arm nops = 0) | false positive (mechanism language) | HC_T01_REANALYSIS_CORRECTIONS.md s2 |
| ruler_insufficiency | prospective test at a window where outcome is a deterministic function of the conditioner (rho = -1.0000) | uninformative (read as negative) | same, s2-3 |
| ruler_insufficiency | detector reads a count (presence of >=1 operator) | false positive (reorganisation claim) | same, s4 |
| search_insufficiency (literature) | one-author citation graph as population for "nobody did X" | false positive (novelty) | HC_T01_CORRECTION_2026-09-03.md |
| ruler_insufficiency | at_T gives random tables {0}: no gradient from random starts | search stall | herakles/CRITERIA.md |
| statistical_insufficiency | n_ics=100 agreement read as tight agreement | false reassurance | dossier C-HER-10 |
| ruler change | TRUE_CORPSE removed by adding fair_test field | possible bias toward UNFAIR | hephaestus.dossier.json 9af40af34 vs c7340a6ad |
| ruler_insufficiency | validator passes 7/8 cheats (evidence existence, load_bearing measured) | false reassurance | validator_negative_tests_result.json |
| statistical_insufficiency | historical permutation null with 0/3 planted detection at N=699 | uninformative historical signal | erebos.dossier.json |
| provenance_defect | single-witness falsifier propagated into a frontier-wide suppression | scope overreach | archaeon/frontier/suppressions/PROTEUS-46.json (HIST) |

Recurrent pattern: in this group, every overturn I could trace was driven by a ruler, sampler, rule
source or arm-design repair. Not one was driven by new organisms in richer worlds.

-------------------------------------------------------------------------------------------------
## 5. Most informative experimental geometries (what to steal as SHAPES)

1. Dual-substrate single-edit census with per-operator class tables and a seed-batch floor
   (PROTEUS-46): same function, two genotype encodings, K children per operator, five outcome
   classes. Informative because it separates operator damage profiles (deletion .97 destroyed vs
   operand_perturbation .354 on v0; dormant ops 1.0 neutral on graph). Its flaw is scope (one witness)
   and a walk that rejects neutrality; fix both and the geometry is strong.
2. Constructive path witness + neutral-path test (D002-03q): hand-construct the shortest neutral path,
   score every intermediate, then ask whether the search rule can sample it. This turns
   "unreachable" into a measurable property of (operator set, acceptance rule, path length).
3. Null-process thermodynamics of variation (V0.5/V0.6): enumerate a coordinate space, measure the
   live operator's kernel, compute current against a two-sample floor. Must carry a positive control at
   declared magnitude (MDC) and a floor guard (Harmonia P-1/P-2).
4. Matched-pair observable qualification (Proteus T2): identity (must be 0), size floor (padding),
   treatment, order, partner identity, independent ceiling, plus a random-population null for any
   class-count statistic. A general recipe for qualifying any behavioural fingerprint.
5. Exact-solvable world with a cheap-policy ladder and cheat fixtures (Ludus): depth-k gap curve with
   the world's own score as the cutoff heuristic, positive (ORCHARD), negative (LEDGER) and cheat
   (Nim: closed-form optimal) fixtures. The cheat fixture is the key piece: it shows what the gate
   cannot see.
6. Exposure-vs-competence decomposition (Ludus cycle 005): per-decision regret vs the optimal
   continuation, decomposed under reference / self / unweighted occupancy. Directly applicable to any
   "transfer" or "context-dependence" claim in Phase 3.
7. Differential leak audit (Ludus arena): pairs of ontic states differing only in a secret; check every
   player-reachable channel (observation, serialise, hash, legal-action set/order/count, error text,
   chance shape, rewards, repr). Fired 4/4 where name-matching fired 1/4.
8. Known-answer reproduction protocol (Herakles C1-e): frozen decision rule, Bonferroni band, named
   suspects in fixed order, exact rule for published zeros, refusal to fit variants. This is how a
   Phase 3 ruler earns trust before any discovery claim.
9. Operator on/off with frozen-population probe and estimator-noise floor (HC-T01): the
   accessibility detector (2000 offspring per individual per generation) measured against a
   contemporaneous mechanical-effect null. Must add: both arms able to build the same machinery
   (or a machinery-matched control), stratification by machinery count, and eligibility windows for
   prospective tests (RA-1 rule).
10. Reservoir assay with controls on the same code path (ca_stream): shift register (solves recall),
   shift+xor cell (solves xor), direct input, frozen random, leakage probe; plus the declared limit that
   a linear readout cannot express xor.

-------------------------------------------------------------------------------------------------
## 6. engine_index census (51 engines; REPORTED from the crawler index, not verified except my group)

What each world was described as demanding, and whether any organism was reported to meet it.
This is a lead table for the architect, compiled from engine_index.jsonl fields world_type and
major_limitations. Only rows 28-35 and 43-48 (my group) were checked against source.

| demand class (from index text) | engines | reported outcome |
|---|---|---|
| none (ledger, notary, data plane, forensic, catalogue) | Archaeon v0 producer, causal lens; Vivarium data plane; SFE; MHC; ancestry tracer; Necropolis x2; Ludus Atlas; Chiron (design only) | n/a |
| static fitness / lookup (onemax, NK, Boolean 3-input, target string) | Vivarium evaluate_bitstring, cegis_boolean_v1; SFE executors; Gen-2 canary; HC-T01; Archaeon producer bench (exact Hamming feedback) | solved or null; canary null; cegis "H1 relevance inert" |
| one bit across time (latch) | Ares (worlds "demand one bit; solved by a two-edge output self-loop") | reached; mechanism = self-loop |
| single-byte / conditional-byte tasks with replication | Archaeon Z80xAtlas, ENVGATE; Nestor NPE; Bellerophon BEE | replication engineered or artifactual (~95% early replicators splice/write-back artifacts, NPE); task acquisition stalls at COND_ONE (BEE) |
| keyed memory / delay (PUT/ASK, K streams, distractors) | Archaeon WSE C1-C3, C4-C5; Nestor CW01 loop; Proteus witnesses | two-stream keyed memory 0/60 (WSE); "cliff" with count rulers later questioned (CW01 4/7 claims disappeared under Bernoulli(f)) |
| composed worlds with hidden state, hazards, coupling | Archaeon C6 observatory, Deep Frontier | rulers saturated or structurally UNABLE; positive controls weak (25% / 0%) |
| procedure reuse / composition of hidden templates | Crius RELAY | "accessibility frontier mapped"; neutral-path challenge (Artemis R-07) |
| small register economies, partial observation | Daedalus wforge; Nestor Primordial; Bellerophon Worlds Kernel; Nestor CW01 bespoke | Primordial: zero-byte abstain beat all learners in 28/28 cells; CW01: organisms could not express the questions |
| distributed global computation from local rules | Herakles evca; Vivarium ca_density_v0; Theophrastus | only fixed historical rules evaluated; no evolution re-run |
| text / NL multiple-choice batteries | Apollo v1, v2, Branch C; Lexis | decorative compositions; parsers co-adapted with batteries |
| exact game decisions (stopping, small 2-player) | Ludus cycle-001, bench, arena | worlds shown greedy- or myopic-decidable; no organism |

Census reading (INFER, from REPORTED rows): the program repeatedly built worlds whose demand turned out
to be satisfiable by a trivial mechanism (abstain, a self-loop, a myopic rule, a greedy move), and the
few worlds with richer demand lacked either a qualified ruler or an organism/search pair that could
reach the demand. The bottleneck alternates between world_insufficiency and search_insufficiency;
organism expressiveness was repeatedly shown NOT to be the binding constraint where it was tested
(Proteus keyed-memory witness; Ares plasticity; Crius in-head simulation rungs), REPORTED.

-------------------------------------------------------------------------------------------------
## 7. Instruments with demonstrated detectability (planted positive and/or matched negative shown)

| instrument | detects | evidence | cite |
|---|---|---|---|
| Ludus differential leak audit | hidden-information leakage through any player-reachable channel | 4/4 injected leaks fired; 0 on clean Kuhn | ludus/controls/CONTROLS_2026-09-16.json (IMPL) |
| Ludus depth profile gap(k) + GATE-W1 | whether a world requires lookahead beyond k plies | positive ORCHARD fires (.3448), negative LEDGER 0, regression rows exact; BLIND to closed-form policies (Nim admitted) | same |
| Ludus bench verify | structural errors in exact worlds | catches pot+1, cycle, large prob halving; misses small prob and draw-law errors | same |
| Ludus arena theory checks | implementation correctness against known game values | Kuhn -1/18, Nim xor, TTT draw, 20/20 (REPORTED) | dossier LC7 |
| Proteus meter projection | behavioural difference between programs | identity 0.0, size floor 0.0, independent .99, treatment .775; deterministic 40/40 vs raw 0/40 | proteus/v0_7/RESULT_METER_FLOOR.json (IMPL) |
| Proteus kernel current detector | authored nonequilibrium in a variation operator | detector admitted; no MDC at the time; reversible control could not fail; Artemis MDC ~1e-4 (REPORTED) | Harmonia ruling (IMPL text) |
| Proteus V0.5 global multiplicity + frozen confirmatory replication | whether a single-coordinate discovery replicates | killed V0.4 discovery (p .9716) | ADJUDICATION_V0_5.json (IMPL) |
| Herakles C1-e reproduction protocol | fidelity of CA substrate + rule transcription vs published values | 17/18; maj exact 0; flagged anomaly (exp) shown not to replicate; particle2 isolated | herakles/evca/c1e/REPORT.md (IMPL) |
| Herakles CRITERIA floors + controls | criterion floors for random/constant rules; blinker positive; exact-k cheat | measured bands; cheat returns max(k,N-k)/N to 1e-12 | herakles/CRITERIA.md (IMPL) |
| Herakles c3_null_check | symmetry-transform identity (IDENTICAL / NOT_IDENTICAL / INDETERMINATE) with named bug signature | registered READY / EVIDENCE as NT-033 | TOOLS.jsonl (IMPL) |
| Herakles ca_stream control suite | reservoir memory capacity | shift register 1.0 recall; shift+xor 1.0 xor; frozen random at base; linear readout provably cannot express xor | herakles/ca_stream/OBSTRUCTION.md (IMPL) |
| HC-T01 estimator-noise floor | detector noise vs history effect | 20 replicate estimator seeds; history effect 24-108x noise (REPORTED) | HC_T01_CORRECTION (IMPL text) |
| Necropolis validator | structural law violations in dossiers | 11/11 rejects caught; 7/8 cheats pass (detectability of cheats NOT demonstrated) | validator_negative_tests_result.json (IMPL) |
| Erebos pair-aware null (calibrated in Necropolis) | partner-conditioned linkage | 0/3 planted detected at N=699: demonstrated NON-detectability | erebos.dossier.json (IMPL text) |
| PROTEUS-46 harness | single-edit class shares | floor from seed batches; NO planted graded neighbourhood shown detectable; walk arm cannot detect neutral paths | falsifier_46.py (IMPL) |

-------------------------------------------------------------------------------------------------
## 8. Design implications for Phase 3 (each tied to evidence)

1. Every developmental claim needs a constructive path witness and a search-rule audit before a
   "cliff" or "unreachable" verdict is admitted. PROTEUS-46's walk could not move on neutral children
   (falsifier_46.py:119-128) and a 5-edit neutral path exists (D002-03q, REPORTED). Require: shortest
   known path length L, intermediates' classes, and proof that the acceptance rule can traverse
   neutral and mildly deleterious steps with walk length >= L.
2. Score worlds for demand before scoring organisms for competence. Ludus's controls show a gate can
   admit a world that a 4-line rule solves (Nim). Phase 3 worlds should ship with a cheap-policy
   ladder that includes closed-form/lookup policies, an ablated-capability organism, and a cheat
   fixture, so W (world demand) can be scored Y.
3. Rulers must have a positive control at declared magnitude and a floor guard (Harmonia P-1/P-2),
   and absence claims must be stated as NOT_DETECTED_ABOVE(MDC), never "no effect". Two separate
   seats here (Proteus V0.5, Erebos historical null) produced absence-shaped readings from instruments
   that could not detect.
4. Separate exposure from competence in every transfer or context claim (Ludus cycle 005: circuit x
   world .6222 unweighted vs .1021 under reference occupancy).
5. Treat the test distribution as part of the pressure and report it as a variable: IC ensemble
   reorders CA rules (maj 0.000 -> 0.443; Capcarrere ranking flips). A Phase 3 "world" spec must fix
   and declare its input distribution and report sensitivity to it.
6. Arms must be machinery-matched. HC-T01's treatment arm alone could build operator machinery; the
   effect reduced largely to machinery presence (RA-2). Developmental-capacity experiments need either
   equal construction affordances in all arms or explicit machinery-count stratification, plus a
   "current fitness" baseline (K7) evaluated only at windows where the outcome is not a deterministic
   function of the conditioner (RA-1 eligibility rule).
7. Characterise the null process of variation before selection (Proteus kernel lens): mutation
   operators carry authored current; dormant-attach operators are neutral by construction (graph
   grammar). A Phase 3 organism foundry should publish its operator kernel and neutrality profile as
   part of the organism spec, but with content coordinates, not only length/tape.
8. Qualify every behavioural observable with the matched-pair recipe (identity 0, size floor, order,
   partner identity, independent ceiling, random-population null) before using it as a ruler; the
   transcript fingerprint was constant across five structurally distinct conditions including full
   ablation (HIST, Harmonia M2) and would have reported "composition adds nothing".
9. Known-answer calibration is the cheapest trust: reproduce published values with a frozen rule and
   named suspects before any discovery claim (Herakles C1-e). It certifies the ruler and substrate, and
   nothing more; do not let it stand in for phenomenon evidence.
10. Build the failure-record path into the engines, not as a separate court. The Necropolis had the
   right vocabulary (fair_test, nine-layer stack, separated readers) but no ingestion path from any
   evolutionary engine and no planted TRUE_CORPSE control; its only true corpse vanished by schema
   change. A Phase 3 run should emit its own "dead lineage" record with fair_test fields at run time,
   and the adjudicator should be calibrated on planted fair-and-failed cases.
11. Bound the scope of every negative at the point of emission. PROTEUS-46 declared
   neighbourhood_exhausted False and four reopen conditions, yet propagated as a 299,991-row
   suppression (HIST). Verdict files should carry machine-readable scope (witness ids, probe, operator
   set, path length examined) that schedulers must check.
12. Interfaces before worlds before organisms is not enough; the binding must exist. Ludus never wrote
   the Proteus channel binding (no importer anywhere, IMPL), so the exact-world instruments never met an
   organism. Phase 3 needs one organism ABI and one world ABI with a tested binding on day one.

-------------------------------------------------------------------------------------------------
## 9. Open questions (for the architect or later readers)

1. Does long neutral drift on graph_grammar.v1 reach 6/6 at a rate beating an unselected control? The
   full D002-03 run timed out with zero output (REPORTED); quick mode 1/50 vs 0/50.
2. What is the exact one-step probability, under the grammar's own sampler, of each edit on the 5-edit
   neutral path (D001-03 part C)? Not quoted in D002 RESULT.
3. Does the C4 "cliff" that PROTEUS-46 premised survive a Bernoulli(f) damage ruler (Atlas F8 / CW01
   audit, HIST, not my group)?
4. Is TRUE_CORPSE reachable under Necropolis v2 doctrine? A planted fair-test-then-failed grave would
   discriminate; none exists.
5. Would the five unloaded calibrated organisms (coev1, coev2, abk_gp, das1995, davis1995) behave
   differently from the GA rules under cellwise criteria (X-4 never closed)?
6. ca_stream v2 (seeded Bernoulli reset, approved D-18) and rules that preserve a lone cell (Elenchus
   counterexample) were never run; is CA-as-reservoir memory real for any density-capable rule?
7. Does the depth profile's lexicographic tie-break ([:1]) inflate gap(k) on any committed world?
   Magnitude UNK.
8. Is the V0.6 authored current operationally significant under any selection regime (Artemis bias
   <= .004 instructions, REPORTED)?
9. HC-T01: with machinery-matched arms and eligible windows, does accessibility predict acquisition
   beyond current fitness? Unanswered in this substrate.
10. EvCA Stage 1 (re-run the 1990s GA targeting the 7/300 particle-strategy transition) was specified
   and never authorised: is the historical rare transition reproducible?

-------------------------------------------------------------------------------------------------
## 10. Files opened

Intake: docs/phase3/intake/sisyphus/seats/{Proteus,Ludus,Herakles,Rhadamanthus}.md;
seats/_frag/{Proteus,Ludus,Herakles,Rhadamanthus}.{engines,artifacts}.jsonl;
docs/phase3/intake/sisyphus/engine_index.jsonl (all 51 rows).
Proteus: proteus/round2/falsifier_46.py, PROTEUS-46_PREREGISTRATION.md, PROTEUS-46_FALSIFIER.md;
proteus/v0_5/kernel.py, ADJUDICATION_V0_5.json; proteus/v0_7/RESULT_METER_FLOOR.json,
RESULT_TRANSCRIPT_DEGENERACY.json; proteus/graph/grammar.py (1-64); proteus/foundry/vm.py (grep),
probes.py (grep); roles/Harmonia/rulings/RULING_PROTEUS_CURRENT_INSTRUMENT_AND_R4_2026-09-18.md
(1-90); roles/Artemis/dispatch/D002/RESULT.md, PLAN.md (grep), scripts/D001-03.py (1-80).
Ludus: ludus/bench/core.py (1-120), circuits.py (90-150), depth_profile.py, arena/audit.py (1-60),
bench/occupancy.py (1-50), controls/CONTROLS_2026-09-16.json; roles/Ludus/CYCLE_005_verdict_demotion.md
(1-40), CYCLE_001_ceiling.md (grep), CYCLE_002_stochastic_stopping.md (grep);
roles/Artemis/selftest/runs/R-32/REPORT.md (grep).
Herakles: herakles/evca/c1e/REPORT.md, herakles/CRITERIA.md, herakles/evca/MAJ_STRUCTURAL_ZERO.md
(grep), herakles/evca/genomes.py (grep), herakles/ca_stream/OBSTRUCTION.md (1-70),
herakles/specimens/spec-{juille-pollack-1998,andre-bennett-koza-1996,capcarrere-r1-density}/REPORT.md
(grep), spec-toussaint-exploration/derived/hct01.c (1-45),
spec-toussaint-exploration/HC_T01_CORRECTION_2026-09-03.md,
spec-toussaint-exploration/reanalysis/conditional_accessibility_2026-09-03/HC_T01_REANALYSIS_CORRECTIONS.md;
roles/Elenchus/investigations/2026-09-11_epistemic_debt/LEDGER.md (85-124 + grep).
Necropolis: engine/necropolis/workshop/TOOLS.jsonl (tabulated), engine/necropolis/tests/
validator_negative_tests_result.json, engine/necropolis/dossiers/hephaestus.dossier.json (git show at
9af40af34, c7340a6ad, HEAD), engine/necropolis/dossiers/erebos.dossier.json (grep).
Repo-wide: git grep for ludus/herakles/proteus importers and necropolis references in *.py.
