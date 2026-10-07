# Hestia audit dossier -- ludus (board games as worlds; World Foundry)

VERDICT: SALVAGE_COMPONENT -- Ludus contains no organism, learner or reasoning mechanism at all; it is an exact-DP world bench whose worlds are almost all solved by a two-line lookahead rule, but its discriminability instruments (exact retention, depth profile with cheat controls, differential leak audit) and the one-knob FOUNDRY generator are worth carrying forward as the selection-pressure ruler for other seats.

Audit group G4 (world engines). Currency 2026-10-06. Auditor: Hestia worker fork.

## 0. Identity

- Paths: ludus/ (799 tracked files; 732 of them under ludus/atlas_of_worlds/,
  716 of those are crawled per-title markdown dossiers), roles/Ludus/ (35 files).
- Seat: Ludus, "World Foundry" (roles/Ludus/CHARTER_v3_WORLD_FOUNDRY.md s1).
  STATUS.md currency 2026-09-16: ACTIVE; last code commit on these paths
  fb858dd5c (LUDUS-15 rule audit). No Ludus commit after 2026-09-16 seen in
  `git log -- ludus roles/Ludus`.
- Worktree read: C:/Prometheus-worktrees/hestia-boot-2026-10-06 at 3fed30ac9.
- READ (code): ludus/bench/{circuits,compiled,core(1-120),loop}.py,
  ludus/bench/worlds2.py (1-140, FOUNDRY), ludus/arena/core.py (1-140),
  ludus/arena/players.py, ludus/arena/epistemic.py (1-60),
  ludus/depth_profile.py, ludus/atlas_of_worlds/classify.py (334-560),
  ludus/atlas_of_worlds/README.md, one atlas dossier
  (worlds/1861_melbourne_cup.md).
- READ (rows): ludus/atlas/transfer_matrix.json (all 22 columns),
  ludus/atlas/CIRCUIT_MATURITY.md, ludus/ledgers/cycle001_r0002_depth_profile.json,
  ludus/controls/CONTROLS_2026-09-16.json (25 rows),
  roles/Ludus/epistemic_verification_2026-09-01.txt (grep).
- READ (prose): CHARTER_v3_WORLD_FOUNDRY.md (s1-s9), STATUS.md,
  CYCLE_001_ceiling.md (s1-s2), CYCLE_002 (head + annotation),
  CYCLE_005_verdict_demotion.md, CYCLE_004 verdict (grep only),
  journal/2026-09-16.md, ARCHAEOLOGY (L-1..L-3 lines),
  ludus/docs/"Worlds as Part of the Prometheus Strategic Roadmap.md" (head).
- NOT READ: ludus/bench/{worlds.py world bodies, verify.py, audit.py,
  ledger.py, maturity.py, occupancy.py, partner_matrix.py, run.py},
  ludus/arena/{worlds.py bodies, audit.py, verify.py, worlds_epistemic.py},
  ludus/{worlds.py bodies, ceiling1.py, stopgate.py, stopworlds.py,
  baselines.py, r0001_sweep.py, report.py}, crawl/deepen/wikidata/wikipedia
  modules, 715 of 716 atlas dossiers, REVIEW_PACKET_1..8, CYCLE_004 body,
  CHARTER v1/v2, ROLE.md, BACKLOG_H0H5.md, rules_audit.json,
  the canonical Postgres atlas (not reachable read-only from here).
  Nothing was executed.

## 1. Mechanism (what the code does)

### 1.1 Three disjoint layers, three world interfaces

The seat itself records three interfaces in one seat (ARCHAEOLOGY defect L-2,
roles/Ludus/ARCHAEOLOGY_2026-09-11.md:245; CHARTER_v3 s9 P1).

(a) BENCH (ludus/bench/): single-player stochastic accumulate-or-bank MDPs.
Interface is five methods: initial, draws(s)->[(p,draw)], options(s,draw)->[S]
(empty = death), pot(s), forced_end(s) (ludus/bench/core.py:21-26, 67-86).
`compile_world` walks the full reachable graph by DFS into flat dicts with a
hard cap of 4,000,000 states (ludus/bench/compiled.py:46-73, cap at :46, :68-69).
`solve` is exact backward induction V/W (compiled.py:80-105; recursion
documented core.py:36-38). `evaluate` computes the EXACT expected value of a
(select, stop) policy pair (compiled.py:108-132). Every reported number is
exact arithmetic, no sampling (core.py:41-42).

(b) ARENA (ludus/arena/): OpenSpiel-shaped multi-player interface with
current_player in {id, CHANCE=-1, SIMULTANEOUS=-2, TERMINAL=-4}
(ludus/arena/core.py:15-19, 40-43), World/State/Player separation, and
"no hook through which a strategy oracle could be smuggled" (core.py:27-29).
Worlds: TicTacToe, Nim, Pig, RPS, KuhnPoker (ludus/arena/worlds.py:91,156,245,
309,421) plus BallUnderCouch (worlds_epistemic.py:205). Players are controls:
Random, FirstAction, Bouton Nim (players.py:32-51), Pig hold-at-N (:54-74),
Kuhn Nash family (:77-125), memoised Minimax with a documented contract
violation to read full state (:128-171). The epistemic layer is a taxonomy of
13 information classes and a ladder E0..E4 (epistemic.py:28-60), exercised by
one occlusion world.

(c) ATLAS OF WORLDS (ludus/atlas_of_worlds/): a Wikipedia/Wikidata crawler
plus a regex-weighted classifier. `classify` scores keyword hits per field
(classify.py:334-360); luck, rules complexity and strategic depth are
hand-tuned additive formulas over those hits (classify.py:476-549, e.g.
depth = 2.0 + 0.25*strategies + 0.30*algorithms + 0.4 if PERFECT, :535-549).
Output is a markdown dossier per title. Example of what this produces:
worlds/1861_melbourne_cup.md is a horse race ("annual horse race in Melbourne")
classified DEEPENED with "strategic depth 2.25", "luck factor 0.35". It is
text metadata, not an executable world.

### 1.2 What the "circuits" are

The thing the seat calls a reasoning circuit is a hand-written Python
function of 1-10 lines, registered by decorator (ludus/bench/circuits.py:21-30).
The full registry:

- SELECT: r0010 greedy max pot (:37-40), r0011 min capacity consumption
  (:43-46), r0012 one-draw lookahead (:49-52, helper :71-101), r0013 null
  first-option (:55-58), r0014 pot gain per capacity (:61-68).
- STOP: r0003 myopic one-step "stop iff P(death)*pot >= E[gain]" (:108-121),
  r0004 never (:124-127), r0005 always (:130-132), r0007 P(death)>=0.5
  (:135-141), r0015 two-ply myopic (:144-156), fitted threshold T swept per
  world (:159-170), OPTIMAL read off the DP table (:177-199).

No circuit is generated, mutated, learned, or composed by any code in ludus/.
A grep for mutat|evolv|learn|train|genome|population|organism|proteus over
ludus/*.py, arena, bench, controls returns no learner and no organism binding
(only docstring hits). CHARTER_v3 s7 says "LUDUS WRITES THE WORLD-SIDE
BINDING" to Proteus organisms; no such binding exists in code.

### 1.3 Selection of the next world

Deliberately NOT automated: `choose_next_work` only reports mechanical gaps
and defers world choice to a human backlog (ludus/bench/loop.py:92-142). The
docstring states the selector would "maximise a proxy nobody can falsify"
(:99-104). This is honest and correct, and it also means there is no
open-ended world generation loop.

### 1.4 FOUNDRY generator

The only parameterised world family: state (capacity_left, pot,
prereq_claimed, draws_left), knobs gate, decay, arity, capacity, horizon,
p_bust, decoy; four option archetypes (ludus/bench/worlds2.py:50-63, 66-99,
132-135). Purpose stated: move exactly one property at a time (worlds2.py:21-26).
Measured instances have 34-96 states (transfer_matrix.json).

### 1.5 Qualification instruments

- Depth profile r0002: gap(k) = 1 - P[depth-k minimax with the world's own
  score as cutoff eval picks an optimal action], over reachable states with
  branching >= 2, n=250 sample (ludus/depth_profile.py:15-16, 47-49, 52-61,
  71-96). Admission threshold gap(4) >= 0.20 (:94).
- Bench verify (not read in body), arena verify, differential leak audit
  (ludus/arena/audit.py:106 "mutate a private field and see whether ANY
  channel moves", docstring only read).

Documented vs code: the documents describe a "World Foundry" that "creates,
acquires, mutates, validates, classifies" worlds (CHARTER_v3 s1) and a
chopping grammar of ~24 primitives (s4). In code: worlds are hand-authored
classes; mutation of worlds exists only as the FOUNDRY knob grid and the
arena `params` dict (arena/core.py:61-66, 75-80); the chopping grammar is
LUDUS-02, unbuilt (STATUS.md "next executable action: LUDUS-02").

## 2. Evidence (tiered)

OBSERVED (committed rows on main, read by this audit):

- E1. Transfer matrix: 22 world columns x 10 circuits, all exact
  (ludus/atlas/transfer_matrix.json). 15 of 22 columns are FOUNDRY synthetic
  variants of 34-96 states; 7 are reconstructed named games of 3,832 to
  442,368 states (Lucky Numbers to Incan Gold). Total states over all columns
  842,255 (scratchpad calc, numbers below).
- E2. r0003 (one-step myopic stop) retains >= 0.99 of optimal EV in 18 of 22
  columns; r0015 (two-ply myopic) retains >= 0.962 in ALL 22; some hand stop
  rule reaches >= 0.99 in 21 of 22. Exceptions for r0003: LUCKY_NUMBERS 0.667,
  COLORETTO 0.043 (where never-stop r0004 scores 1.0).
- E3. Cycle 001 depth profile on three worlds authored to be strategic
  (LOOM, WEIR, TITHE): gap(4) = 0.000 / 0.012 / 0.040, all fail the 0.20 gate
  (ludus/ledgers/cycle001_r0002_depth_profile.json; CYCLE_001_ceiling.md:3-6:
  "the band is empty").
- E4. Controls (ludus/controls/CONTROLS_2026-09-16.json, 25 rows): positive
  control ORCHARD admitted (gap .793/.616/.468/.345); NEGATIVE result for the
  gate: Nim(3,4,5) exhaustive gap(4)=0.240 and Nim(3,4,5,6) 0.496 are
  ADMITTED although Bouton's 4-line xor rule is optimal on 430/430 and
  4847/4847 N-positions (journal/2026-09-16.md). Bench verify is blind to the
  draw law (one-ray Martian Dice verifies). Key-name leak check silent on 3 of
  4 injected leaks; differential audit fires on 4 of 4.
- E5. Cycle 005 occupancy decomposition (roles/Ludus/CYCLE_005_verdict_demotion.md,
  data ludus/atlas/cycle005_occupancy.json not opened): under reference
  occupancy, circuit main effect 0.8528, circuit x world 0.1021; the cycle-004
  CONTEXTUAL_BASIS_REQUIRED verdict was demoted by the seat itself. Cross-world
  rank tau on reconstructed worlds +0.108 mean, 3 of 6 pairs negative.
- E6. Rule fidelity: W3 rule-audited 2 of 30 executable worlds COMPLETE
  (MARTIAN_DICE, FLIP7), 2 PARTIAL (STATUS.md). Martian Dice audit moved 2
  rules, EV 2.093806 -> 3.110382, and reversed cycle 002's central axis
  reading (CYCLE_002 annotation). Matrix carries both columns (E1).
- E7. Epistemic arena: 25/25 checks on one occlusion world
  (epistemic_verification_2026-09-01.txt lines 6-39). These verify the world
  model's bookkeeping, not any agent.

CLAIMED (prose only, not checked here): arena verify 20/20 and bench verify
4/21 (STATUS.md); 1,338 catalogued titles in Postgres ludus_atlas (5,774 rows
per commit 6fcbf4c09); circuit r0003 survived two prospective worlds after a
registered prediction (CIRCUIT_MATURITY.md, the prediction text in CYCLE_002
s8.1 not opened).

DESIGNED (not run): chopping grammar (CHARTER_v3 s4), W0-W8 ladder above W7,
world x organism matrix with organism phenotypes (s6), Proteus binding (s7),
four-arm learning-cost design (CYCLE_005 consequence 4), automated world
selection (loop.py:111-115 conditions).

Self-recorded negatives the seat already owns: empty band (cycle 001); verdict
demotion (cycle 005); Nim cheat admitted (controls); rules reconstruction
reversed a headline (LUDUS-01). The seat's epistemic hygiene is high; the
problem is not dishonesty, it is that the measured worlds are shallow.

## 3. Matrix

### 3a. Combinatorial explosion and reachability

- Bench worlds: state counts 34 .. 442,368 (log10 max = 5.65). The exact
  compiler caps at 4e6, i.e. 9.0x above the largest world measured
  (compiled.py:46; scratchpad). The method is exact DP, so the wall is
  memory-linear in |S|: any world with log10|S| > ~6.6 is out of the bench.
  For orientation, chess ~10^44, Go ~10^170. Worlds2 already notes one
  permutation-indexed variant "explodes (>2.1GB)" (ludus/bench/worlds2.py:205).
- Policy space the worlds pose: deterministic STOP policies alone are 2^|S|:
  Flip 7 2^5812 = 10^1750; Incan Gold 10^133166; Coloretto 10^89383
  (scratchpad). Policies EXPLORED: 7 hand-written STOP + 5 SELECT + 1 fitted
  scalar threshold per world. Coverage of policy space is effectively 0, but
  that is irrelevant here because the optimum is computed by DP and nobody is
  searching.
- The decisive reachability number is the opposite of a desert: the
  reachable-optimal set is reachable by the cheapest rules. A two-ply myopic
  rule retains >= 96.2% of optimal in 22/22 worlds (E2); one-ply greedy picks
  an optimal action in 85-100% of states in the three "strategic" worlds
  (CYCLE_001 s2). The pressure gradient toward anything deeper than 2-ply is
  at most 3.8% of EV on the bench, and at most 4% action-optimality at depth
  4 in cycle 001 (E3).
- FOUNDRY knob grid: 7 knobs; 15 points measured. The family is a product
  of small integer ranges; its states stay < 100 per instance (34-96), so it
  is a calibration family, not a scaling path.
- Atlas: 1,338 catalogued (STATUS) -> 30 executable (2.2%) -> 2 W3-complete
  (0.15%). The catalogue is not the bottleneck; implementation by a human
  reading a rulebook is (loop.py:7-13 says so explicitly).

### 3b. Cosplay vs foundation

- Who does the "reasoning"? Nobody inside Ludus. The circuits are the
  auditor's own hand-coded heuristics (circuits.py:37-170); the "optimal"
  reference is textbook backward induction (compiled.py:80-105). There is no
  substrate in which a circuit could arise. Calling r0003 a "transferring
  circuit" (circuits.py:109) means: a fixed human formula of one expectation
  over the next draw scores well in many push-your-luck MDPs.
- So Ludus is not cosplay of cognition; it does not claim a learner. Where it
  drifts into cosplay is vocabulary: "circuit maturity ladder" with rungs like
  ABLATION_SUPPORTED and TRANSFER_SUPPORTED (bench/maturity.py:27,
  CIRCUIT_MATURITY.md) applied to 1-line Python functions written by the seat,
  and an Atlas whose classifier assigns "strategic depth" to horse races by
  regex (classify.py:535-549; worlds/1861_melbourne_cup.md).
- The worlds themselves: the bench family is single-agent, fully observed,
  memoryless-optimal MDPs where Bellman optimality is local. In such worlds
  a myopic expectation rule is near-optimal by structure, which E2 confirms.
  The arena worlds (TicTacToe, Nim, Pig, RPS, Kuhn) are all closed-form or
  textbook-solved, used as verification fixtures (players.py:32-125).
- Ceiling, stated concretely: (i) worlds must be enumerable below 4e6 states;
  (ii) the measured selection pressure for anything beyond 2-ply lookahead is
  <= 3.8% EV on 22/22 bench columns; (iii) the admission gate cannot tell
  "needs search" from "has a short closed form" (Nim admitted, E4), so a world
  passing GATE-W1 still does not certify that reasoning is selected for --
  it certifies that bounded minimax with the native score is insufficient.

### 3c. Substrate bottlenecks

- Representation: state is a tuple keyed into Python dicts; circuits see a
  four-field table (pot, forced, trans, cons) and nothing else
  (compiled.py:30-40). This is deliberate (transfer by construction,
  compiled.py:15-19) but it also means no world has structured observations,
  objects, relations or partial observability on the bench side. The only
  hidden-information worlds are in the arena (Kuhn, BallUnderCouch), and no
  agent runs there.
- Memory / credit assignment: not applicable inside Ludus; there is no agent
  with internal state. The bench's worlds are Markov in the visible state, so
  memory is never selected for. CHARTER_v3 s4 lists "memory requirements",
  "credit delay", "counterfactual dependence" as primitives; none is a
  measured knob in any executable world read.
- Compositionality: worlds do not compose. Three incompatible interfaces
  (L-2). The chopping grammar is unbuilt.
- I/O bandwidth to organisms: zero. No Proteus/Vivarium binding exists in
  ludus code (grep, s1.2). Any organism seat that wants Ludus worlds must
  write the adapter.
- Instrument bottleneck: bench verify cannot see the draw law (E4), so rule
  errors in the stochastic part pass silently; W3 by a human is the only
  check, and it already reversed one headline (E6). 28 of 30 worlds are still
  reconstructions from memory.

## 4. Deliverable sections

### Discovery Approach

Ludus tries to map the "physics of intelligence" from the environment side:
build worlds whose fitness landscapes exert measurable pressure, then ask
which cheap mechanisms already harvest that pressure. It measures, exactly,
how much of optimal value a fixed hand-written policy retains in each world,
decomposes that by axis (SELECT vs STOP) and by state occupancy, and gates
world admission on whether bounded search already suffices. It is a
discriminability bench, not a cognitive architecture.

### The Brick Walls

1. The worlds do not select for reasoning. A two-ply myopic rule retains
   >= 96.2% of optimal EV in 22 of 22 bench worlds; the three worlds authored
   to be strategic show gap(4) <= 0.04. Any organism evolved in these worlds
   will be selected for a one-expectation reflex, because that is all the
   landscape pays for.
2. Exactness ceiling. The method that makes every number trustworthy (full
   enumeration + DP) caps worlds at 4e6 states, 10^5.65 is the largest
   measured; worlds hard enough to reward multi-step planning, memory or
   theory-of-mind live far above that, where Ludus's ground truth disappears
   and it must fall back to sampling (which cycle 001 showed inflating a
   reading from 0.412 to 0.900, CYCLE_005 "uniform" paragraph).
3. The admission gate is fooled by closed forms. Nim(3,4,5,6) is admitted
   with gap(4) = 0.496 while a 4-line xor rule is optimal on 4847/4847
   positions (E4). Depth-of-search insufficiency is not evidence that
   reasoning is required; it may only mean the native score is a bad
   heuristic. Ludus currently has no MDL/description-length test that would
   separate "deep" from "has a short program".
4. (Secondary) Throughput of rule-faithful worlds: 2 of 1,338 catalogued
   titles are rule-audited (0.15%); every unaudited column is a claim about a
   reconstruction (E6), and the atlas classifier output is regex metadata with
   no executable consequence.

### Seed Viability

SALVAGE_COMPONENT. There is no reasoning seed in Ludus because there is no
agent. What is worth carrying forward, judged as instruments per AUDIT_PLAN
s3: (a) the exact retention/regret ruler over compiled worlds
(compiled.py:108-132) with reference-occupancy weighting (CYCLE_005), which
would detect a real gain from a new mechanism to four decimals; (b) the
discipline of cheap fitted baselines as the bar (circuits.py:159-170,
loop.py:64-89); (c) the differential leak audit (fires 4/4, E4), the right
tool for any partially-observed world handed to organisms; (d) FOUNDRY's
one-knob-at-a-time generator (worlds2.py:66-135) as the template for world
families with a controllable pressure parameter. The Atlas of Worlds crawler
and classifier is not worth carrying forward as a reasoning instrument.

### Evolutionary Roadmap

Turn Ludus from "a bench of shallow solved MDPs" into "a generator of worlds
whose pressure for a named mechanism is a dial, with a certificate that cheap
programs fail".

1. One interface (adopt arena, CHARTER_v3 P1) with an observation channel ABI
   and an organism-side adapter written by Ludus, so at least one external
   learner (Proteus organism, a tabular Q-learner, and a small evolved
   program population) actually plays.
2. Replace GATE-W1 with a two-sided certificate: (i) depth-k minimax gap
   survives (existing), AND (ii) an MDL / program-length bound: enumerate all
   policies expressible in a small typed DSL over the observation (e.g.
   typed lambda calculus over arithmetic/comparison/xor/aggregates, size
   <= n nodes) and report the smallest program reaching >= 0.99 retention.
   A world is "reasoning-selecting at level n" only if no program of size
   <= n succeeds. Nim then fails correctly (xor program of size ~6).
3. Make the FOUNDRY knobs target mechanisms that myopia cannot harvest:
   delayed credit (pot pays only after h steps), hidden state requiring
   memory of k past draws (POMDP with k-step aliasing), and partner-dependent
   payoff (two-agent coevolution). Each knob gets the s4 perturbation rule.
   Measure the curve "retention of best size-n program vs knob value"; a
   world family is useful when that curve slopes.
4. Above 4e6 states, keep exactness by construction: generate worlds whose
   optimal value has a known closed form or certified bound (planted
   solutions, as in the Cosmos/planted lineage), instead of sampling a DP.
5. Open-endedness: once (2) and (3) exist, run a POET-style paired
   world/organism loop where worlds are mutated to keep the best organism's
   retention in a band (e.g. 0.6-0.9) and the MDL floor rising; report
   novelty and MDL-floor growth as open-endedness metrics.

The ONE decisive experiment next: on the FOUNDRY family extended with a
single "memory" knob m (hidden state aliased over m past draws, m = 0..4),
compute exactly, per m, (a) OPTIMAL EV, (b) the best retention achieved by
ANY policy in a small typed DSL up to size n = 8 (exhaustive), and (c) the
best retention of r0003/r0015. Kill criterion: if for every m <= 4 some DSL
program of size <= 8 that reads only the current observation (no memory
term) retains >= 0.95, then the Foundry cannot be made to select for memory
at enumerable sizes and Ludus should be retired to a pure instrument role
(rulers only, no world-building). Pass: a monotone rise in the minimal
successful program size with m, with memoryless programs falling below 0.8
at some m <= 4 -- the first world family in the repo with a certified,
dialable pressure for a non-reflex mechanism.

## 5. What would change this verdict

- Toward VIABLE_SEED: a committed row in which a non-hand-written policy
  (evolved or learned, by any seat) is run in a Ludus world AND that world
  has a certificate (as in roadmap step 2) that no small memoryless program
  reaches the same retention. That would make Ludus the environment half of a
  real seed.
- Toward DEAD_END: if the ruler components fail their own controls on new
  specimens (e.g. retention ruler disagrees with an independent solver such
  as OpenSpiel on an audited world), or if the decisive experiment above
  kills the Foundry, leaving no world in which cheap programs fail.
- Audit-side uncertainty: I did not read the bench world bodies, verify.py,
  maturity.py or the arena worlds' code; a defect there would change the
  E2 numbers, which are taken from the committed matrix as-is. Cycle 004's
  body and the CYCLE_002 s8.1 prediction were not opened. An independent
  reviewer should re-derive E2 from transfer_matrix.json and check whether
  OPTIMAL SELECT retention 0.0 entries in some FOUNDRY columns
  (e.g. FOUNDRY[gate=1,decay=0,k=3,cap=2,h=6]) are the documented
  partner-mismatch artifact (circuits.py:184-193) or a matrix bug.

## Appendix: side calculations (scratchpad ludus_calc.py, over transfer_matrix.json)

    worlds 22, circuits 10, synthetic FOUNDRY columns 15 (34..96 states)
    states min/max/total: 34 / 442,368 / 842,255
    r0003 retention >= 0.99 in 18 of 22; < 0.9: LUCKY_NUMBERS 0.6667, COLORETTO 0.0429
    r0015 retention min 0.962; >= 0.96 in 22 of 22
    fitted threshold >= 0.99 in 16 of 22, min 0.8963
    some hand STOP rule >= 0.99 in 21 of 22
    deterministic STOP policies 2^|S|: FLIP7 10^1750, CANT_STOP 10^20783,
      COLORETTO 10^89383, INCAN_GOLD 10^133166
    compile cap 4e6 / largest world = 9.04x headroom; log10 max |S| = 5.65
    executable 30/1338 = 2.2%; W3 complete 2/1338 = 0.15%
