# Hestia audit 1 -- dossier: sfe_ecology (SFE / Incubator ecology, audited as one system)

VERDICT: SALVAGE_COMPONENT -- as a reasoning substrate the ecology is a
selection loop over a 25-opcode flat bytecode VM that, in 3.7M+ logged
evaluations, never assembled anything beyond a one-register echo/latch
(two-key memory: 0 summits in 395 runs although a 12-instruction solution
exists), but three instruments are worth carrying forward: the SFE
provenance contract (sealed prediction order, loser-keeping selection
families, attestation), the WSE reachability table with FLOOR/SHELF/SUMMIT
censoring, and the per-operator damage-geometry census.

Auditor: Hestia worker (G6), 2026-10-06. Read-only. Rubric: AUDIT_PLAN s2-4.

## 0. Identity

- Components audited as ONE system (the "Incubator" pipeline, per
  roles/Artemis/threads/sfe_retrospective/REPORT.md s1.1):
  - SerendipityFoundry/SerendipityFoundryEngine (232 tracked files; seat
    Daedalus): the HTTP experiment ledger ("SFE").
  - SerendipityFoundry/worldfoundry (48 files): wforge genome-to-world
    grammar and the MHC (microstructure hadron collider) detector.
  - vivarium/ (128 files; roles/Vivarium, 109 files): execution queue.
  - proteus/ (294 files; roles/Proteus, 71 files): player VM, mutation
    grammar, graph substrate.
  - archaeon/frontier (44 files) and archaeon/wse (258 files) plus
    archaeon/campaign2 (186 files) and roles/Archaeon (221 files).
- Census state: SFE, Vivarium, PEW DORMANT/parked since 2026-09-18 (Artemis
  REPORT s0.7, s2.2; roles/Vivarium/STATUS.md currency 2026-09-17).
  Proteus closed 2026-09-04 (roles/Proteus/PROTEUS_CLOSURE_PACKET_2026-09-04.txt),
  reopened for the graph profile 2026-09-18. Archaeon READY, nothing running
  (roles/Archaeon/STATUS_2026-10-01.md s0).
- Worktree: C:/Prometheus-worktrees/hestia-boot-2026-10-06 at 3fed30ac9.
- Read in full: sfe/executors.py (492 lines); wforge/genome.py, world.py,
  probes.py; proteus/foundry/vm.py, affordances.py; proteus/foundry/
  grammar.py 1-120; proteus/graph/GRAPH_ORGANISM_V1.md;
  proteus/round2/PROTEUS-46_FALSIFIER.md; archaeon/wse/worlds.py 1-140;
  archaeon/wse/evolve.py 1-140; archaeon/wse/reachability.py header;
  archaeon/frontier/DEEP_FRONTIER_CHARTER.md, scheduler.py 1-140,
  loop.py header, digests/DIGEST_2026-09-21T2054Z.md; Archaeon review
  packets CAMPAIGN4, CAMPAIGN5 (s0-4), WSE_V01 (s0-1, s5-6), SSF_C1-3
  (s0), CMP1 (s0); Archaeon CALIBRATION_LEDGER.md, STATUS_2026-10-01.md,
  H0H5_STATUS.md (head); Proteus closure packet s1-3; MHC
  QUALIFICATION_RESULTS_V0.txt, MHC_V0_ADJUDICATION_RECORD.txt s1-2;
  vivarium/viv/kinds.py header, cegis_boolean.py header; Artemis
  sfe_retrospective REPORT.md in full.
- Read in part (by grep / outline only): sfe/runtime.py (5125 lines;
  read register_prediction 2126-2157, record_observation 2361-2420,
  _family_arms/_family_findings 3851-3928, method outline);
  proteus/graph/vm.py (outline); archaeon/campaign2/REACHABILITY.jsonl
  (1,277 rows, tallied by script); frontier registry EVENTS.jsonl (counted
  only).
- NOT read: sfe/api.py, store.py, attestation.py bodies; deploy/ (most of
  the 232 SFE files are deploy receipts and long-run logs); the MHC
  prodledger code; vivarium/viv/runner.py, loop.py, queue.py, daemon.py;
  proteus v0_3..v0_6 crucible/equilibrium code and results (only the
  closure packet's summary); proteus/graph/grammar.py; archaeon/campaign6
  (segment, substrate, detectors) code; frontier DECISIONS.md beyond line
  80; the Artemis notes/A,B,C,E,P files; ops/campaigns C-001..C-003 beyond
  their headers. The "E-003 BEE verdict" lives on branch
  archaeon/attribution-arc-2026-09-28 (9c8cfed55), NOT on main; only its
  commit subjects were read; it concerns BEE (z80atlas, group G5), not this
  ecology. ops/campaigns/C-002/E-003 on main is an Aether assay audit.
  C-001 is the cross-engine causal lens; C-003 is Aphrodite. None of the
  three is SFE-ecology science; they are noted, not audited here.

## 1. Mechanism (what the code does)

The pipeline (Artemis REPORT s0.1): Proteus supplies players, wforge/WSE
supply worlds, Vivarium executes, SFE records, Archaeon proposes and
selects. Component by component:

1.1 SFE engine = a ledger, not a physics. The ONLY science-bearing code is
two executors:
- `BitStringExecutor` (sfe/executors.py:71-122): onemax against a
  SHA-256-derived hidden target; score = fraction of matching bits
  (executors.py:53-68). Default length 24 (executors.py:89).
- `NKLandscapeExecutor` (executors.py:247-371): Kauffman NK, N in 8..20
  (executors.py:137) precisely so the optimum can be certified by brute
  force over 2^N (executors.py:205-235).
- Everything else (runtime.py, 5,125 lines) is provenance machinery:
  sealed predictions whose event_seq must precede the experiment commit
  (runtime.py:2126-2157 and the PROSPECTIVE RULE docstring at
  runtime.py:2361-2405), evidence class ENGINE_WORK_RESULT vs
  CLIENT_ASSERTED, selection families that flag MULTIPLE_SELECTED and
  SELECTION_WITHOUT_ALTERNATIVES (runtime.py:3900-3928), budgets,
  lineage edges, tenant isolation.
- Documented intent agrees: "Intelligence (mutation, selection,
  interpretation) lives in drivers/executors, never in the runtime"
  (Artemis REPORT s1.1 quoting d332658cf).

1.2 wforge (worldfoundry/wforge). A world genome is (grammar_version,
seed, mutation list) (genome.py:30-48). `expand` (world.py:89-165) draws
4-12 registers mod 2^16, 2-5 affine transition ops `r[dst] = a*r[s1] +
b*r[s2] + c mod 2^16` (world.py:233), a yield window predicate on one
register (world.py:238), metabolic costs, optional delay/corruption.
Six mutation ops are seeded parameter edits applied at expansion
(world.py:133-158). The player's action surface is "add amt*251 to a
target register" (world.py:224). Probes are seven hand-written
constant/random/cycle policies plus a 1-step echo (probes.py:81-103).
There is no player that learns inside wforge; it is a generator of
random affine dynamical systems with a reward window.

1.3 Proteus player VM (proteus/foundry). A flat tape machine: 4-word
instructions (op, a, b, c), opcode = word mod 25 (vm.py:181), 2-16
registers, tape up to 4096 words, genome copied to the tape front and
optionally self-writable (vm.py:135-137, 206-213). 25 opcodes in nine
classes (affordances.py:28-54): arithmetic, bitwise, compare, JMP/JZ/JNZ
by relative POSITION (vm.py:236-249), IN/INQ/OUT over integer channels,
RND. The interpreter is TOTAL: every word sequence runs (affordances.py
docstring lines 8-12). Mutation: 12 syntactic operators with frozen
weights (grammar.py:26-62), insertion/deletion/duplication/movement/
splice/etc., none semantic.

1.4 Graph organism v1 (proteus/graph). Nodes of the same 25 kinds,
positional jumps replaced by ROUTE and CALL/RETURN, data and control
edges; 13 connectivity operators (GRAPH_ORGANISM_V1.md s2-4). Built,
never run in a world (GRAPH_ORGANISM_V1.md "status").

1.5 WSE worlds and the selection loop (archaeon/wse). Worlds are an event
stream on input channel 0: PUT/ASK/ASKX/ASK2/ASKO/SETOP/DEF/NOISE
(worlds.py:1-23); every task is a keyed-value bookkeeping task (store
values under tags, answer a query). Reward = exact match of the first
output word to the expected word (evolve.py:121); values default to 8
bits so random guessing scores 1/256 (worlds.py:74). The search is a
plain generational GA: N=200, E=24 episodes, elitism 4, tournament 4
(evolve.py:203, 157), children from Proteus `descend`.

1.6 Vivarium. A Postgres queue whose "kinds" declare an EXACT parameter
set with no defaults (viv/kinds.py:1-30). Two science kinds live here: a
CA density task and `cegis_boolean_v1`, a bounded counterexample-guided
enumeration over Boolean expressions whose enumeration order is fixed
by a sealed seed (cegis_boolean.py:1-40, "the first candidate that
satisfies the target is the same expression in every arm").

1.7 Archaeon Deep Frontier. A lineage/queue scheduler: EXPLORATION /
EXPLOITATION / AUDIT pools with multiplicative share updates
(DEEP_FRONTIER_CHARTER.md s3), branch triggers that append
transformations to a lineage (s1, s7), detectors from a frozen Campaign 6
table (scheduler.py:48-53), and runs executed via Campaign 6 segments over
the same Proteus VM (scheduler.py:81-101). It is a bookkeeping layer over
the same GA; it adds no new variation or credit-assignment mechanism.

Documented vs code. Prose across the ecology speaks of "petri dishes",
"open-ended foundry", "worlds", "organs", "workspace", "exaptation".
The code contains: two textbook fitness functions (onemax, NK), a random
affine-map generator, a 25-op flat VM, a 12-operator syntactic mutation
grammar, a tournament GA, and very large provenance/attestation
machinery. Proteus itself is candid: "none of these 25 primitives is a
'reasoning primitive'" (closure packet s2, "NOT CLAIMED").

## 2. Evidence (tiered)

OBSERVED (committed rows/results on main, looked at):
- E1. PROTEUS-46 falsifier (proteus/round2/PROTEUS-46_FALSIFIER.md):
  single-edit neighbourhood of a one-value memory program and a keyed
  two-value program, K=400 per operator, both substrates. USEFUL 0/4,267
  (v0.4) and 0/4,881 (graph) from the one-value parent; 0/4,246 and
  0/4,872 from the keyed parent. Greedy 3-step search width 50 reached
  6/6 in 0/100 on both substrates. Verdict CLIFF_SURVIVES.
- E2. Reachability table (archaeon/campaign2/REACHABILITY.jsonl, 1,277
  rows, tallied by my script): SUMMIT reached in 175 rows, all on
  single-value cells (W0 42/202, W1_d4 127/300, W1_d1 4/39, W1_d16 2/12).
  W2_K2 (two streams) 0/395 summits (201 footholds = the half-credit
  shelf); W3_K2 0/106; W7_K2 0/40; every K>=4, D>=4, fan-out, DAG,
  bind, interfere and timescale cell 0 summits.
- E3. Frontier digest (archaeon/frontier/digests/DIGEST_2026-09-21T2054Z.md
  line 5): 119 transformations, 3,719,136 evaluations, 13 lineages.
  Detector firings structural_reuse 1,658,614 and detector_disagreement
  1,753,735 (0.45 and 0.47 per evaluation); four detectors
  (unexpected_transfer, regime_persistence, unexplained_gain,
  unexpected_causal_dependence) UNABLE on 1,775,074 = every evaluated
  subject. 0 SURVIVING interpretations; 3 PROVISIONAL.
- E4. Proteus closure packet s1-2: on the frozen probe ensemble 52/56
  players emit nothing; transcript has 3 classes, 87.5% in one; A+B
  composition differs from both parents in 0/200 pairs.
- E5. MHC QUALIFICATION_RESULTS_V0.txt: sealed holdout P5 admitted 0/12
  on all three coordinates (the detector was blind to the planted class);
  ruled "NOT CLEARED FOR SCIENTIFIC SEARCH" (adjudication record s0).

CLAIMED (seat prose with inline numbers; underlying rows partly read or
off-repo):
- C1. WSE survey (REVIEW_PACKET_WSE_V01 s6B): all seven solving elites use
  ONE recurrent register; tape never load-bearing in 126 runs; doubling D
  gives 0.000 (the register holds one value, not a fold); capacity curve
  1/K. s6D: "sum eight words, add one" (W6_f1_n8) not found in 100
  generations; W0 itself found in 2 of 3 seeds.
- C2. SSF cycles 1-3 (REVIEW_PACKET_SSF_C1-3 s0): "No lineage ever held
  more than one value"; de-novo footholds 0/60 at N256 x G120, 2/9 at
  N512 x G200 on the easiest cell; the one adaptation was learning to
  halt early (tick budget 256 -> 16).
- C3. Campaign 4 (REVIEW_PACKET_CAMPAIGN4 s1-2): 0/5,472 single edits
  improved any of 57 parents; loss by radius .522/.664/.834/.930/.989 at
  1/2/4/8/16 edits; 932/932 instruction words outside the opcode table
  in the starting variants (total interpreter, no fault exists);
  selection builds LENGTH and neutrality, no mechanism (C4-08).
- C4. Campaign 5 (REVIEW_PACKET_CAMPAIGN5 s0-4): OLD_SUBSTRATE_EXHAUSTED;
  lateral ecology improved 0/24 cells; a fault-capable encoding produced
  real local recovery (229 replicated) but "first held-out gain over the
  starting best: none in 96 cells"; BOUNDARY_CREATED_NO_DISCOVERY_GAIN.
- C5. CMP1 (REVIEW_PACKET_CMP1 s0): whole mature genotypes seed footholds
  on neighbouring cells (2/3 vs 0/3); recombined "organs" sit at floor
  with their shuffled controls (SFE-08).
- C6. Vivarium postmortem: "The science is 0.1s. The row is 95-193s. 98%+
  is SFE round-trips" (roles/Vivarium/NOTES_POSTMORTEM_2026-09-08_to_09-11.md:157).
- C7. Ledger volume: M1 ledger 89,939 experiments, M2 2,070, both off-repo
  (Artemis REPORT s0.7). H5-1 on 256 ECA rules was "the instrument
  calibrated ... NO evidence about learned evolvability"
  (H0H5_STATUS.md, 2026-09-11 entry).

DESIGNED (not run): graph organism in any world (GRAPH_ORGANISM_V1.md
s7); Deep Frontier's 202 pending EXPLORATION items (digest line 5); SFE
schema 10 and the Postgres ledger (Artemis REPORT s1.2); Proteus Round 2
lanes (proteus/docs/round2/... "DESIGN ONLY").

The seats' own record is mostly negative and honest. Archaeon's
calibration ledger (roles/Archaeon/CALIBRATION_LEDGER.md) lists process
errors; the scientific negatives are in the review packets themselves.

## 3. Matrix

### 3a Combinatorial explosion and reachability

Search space (side calculation, scratchpad g6_calc.py):
- Proteus v0, R=16 registers: decoded non-immediate instructions per slot
  = 3 + 10*16^3 + 7*16^2 + 16 = 42,771 (2^15.4); with 32-bit immediates
  (LDC, jump offsets) about 2^37.6. Raw genome space is 2^(128 L).
  - L=12 (the hand-written keyed-memory witness): 10^55.6 decoded
    programs ignoring immediates.
  - L=19 (mean C4-08 ancestral length): 10^88; L=62 (doubled-load
    descendants): 10^296.
- Evaluations actually spent: frontier 3.72e6 (10^6.57); the full WSE
  reachability table 1,277 runs of order N*G = 200*100 = 2e4 evaluations
  each, about 2.6e7 (10^7.4) total. Fraction of the L=12 space touched:
  < 10^-48. Exhaustive search is irrelevant; everything rests on local
  neighbourhood structure.
- Neighbourhood structure is measured, and it is the brick wall:
  - P(single edit is USEFUL) on the one-value -> keyed step: 0/18,266
    children over both parents and substrates; rule-of-three 95% upper
    bound 1.6e-4 (E1).
  - P(single edit improves any of 57 parents): 0/5,472; upper bound
    5.5e-4 (C3).
  - Destruction rises with radius to .989 at 16 edits (C3), so larger
    jumps do not cross either. The one-value -> two-value step is a
    COORDINATED change with no intermediate the reward can see (E1).
- Reward landscape. WSE reward is exact equality of a 32-bit output to the
  expected value (evolve.py:121), averaged per ask. With K keyed streams,
  an organism that echoes the last value scores 1/K for free (C1). Every
  K>=2 cell therefore has a wide shelf at 1/K and a needle at 1.0; the
  fold (ADD over D values) and multi-slot storage have no graded path.
  This is a reachability desert by construction: 0/395 summits on W2_K2
  is the measured width of that desert at N=200, G=100.
- wforge: about 10^46.9 lin_op configurations alone (side calc), from a
  64-bit seed; worlds are random affine maps mod 2^16, so "diversity" is
  cheap and almost none of it is structured for memory or composition.
- SFE executors: onemax 2^24 = 16.8M points, NK at most 2^20 = 1.05M.
  These are toy landscapes chosen BECAUSE they are certifiable; they
  cannot show reasoning, only search-method calibration.

### 3b Cosplay vs foundation

What is called reasoning/learning, and what does the work:
- "Memory/workspace" in WSE: done by a selection loop over a flat
  25-op VM; the only mechanism evolution found is one recurrent register
  echoing the latest value (C1, 7/7 elites) and, once, a halting
  economy (C2). The ip-as-state reading is a hypothesis in two elites.
  This is a selection loop over a tiny syntactic operator set reaching a
  one-bit/one-word latch. Ceiling as measured: a single stored word;
  no evolved fold, no second slot, no addressable tape use.
- "Exaptation", "lateral rescue", "deep neutral walk": real measurements
  of a neutral network, but C5-01 shows the depth gradient is bought by
  evaluations a random single edit spends at least as well (.0012 per
  evaluation), and lateral ecology improved 0/24 cells (C4).
- "Organs" recombined across lineages: at floor with shuffled controls
  (C5); 0/200 composed pairs behave differently from both parents (E4).
  There is no composition operator with semantics; splice is byte copy.
- "Discovery" in the Deep Frontier: detector firings are measurement
  artifacts at this volume (0.45-0.47 firings per evaluation for
  structural_reuse and detector_disagreement; four detectors UNABLE on
  every subject, E3). A detector that fires on half of all evaluations
  is not a discovery signal.
- wforge "world genome": a fixed hand-coded random generator; mutation is
  parameter perturbation.
- cegis_boolean_v1: a fixed enumeration with a sealed order; by design the
  same expression wins in every arm (cegis_boolean.py header). It
  measures cost, not search intelligence.

Foundation pieces (instruments, not substrates):
- SFE's research-act provenance: prospective-window rule, typed
  replication, loser-keeping families with MULTIPLE_SELECTED and
  SELECTION_WITHOUT_ALTERNATIVES findings (runtime.py:3900-3928). These
  would detect best-of-N and post-hoc prediction, which Artemis REPORT
  s3.3 shows is the ecology-wide failure class.
- WSE reachability table (reachability.py header): FLOOR/SHELF/SUMMIT
  levels, right-censoring, common-random-number dedup, classes
  COMMON..OBSERVED_UNREACHABLE_AT_BUDGET. This is exactly the instrument
  the charter asks for to map reachability deserts.
- Intervention battery (ERASE_REGS / ERASE_TAPE / TRANSPLANT / RESET_IP /
  K-curve; WSE_V01 s5) and the null battery with lagged echoes (s6C):
  they caught the one-register shortcut and a leaked world (W8 VOID).
  These would detect a real stored-state circuit if one arose.
- The damage-geometry census (C4-01/02, PROTEUS-46 per-operator table):
  a reusable measurement of how mutation operators move a program
  through behaviour space.

Ceiling of the substrate as built: flat positional encoding + total
interpreter + syntactic operators + exact-match scalar reward. The
measured ceiling is a single stored value; the expressible ceiling (the
12-instruction keyed program exists, keyed_memory_witness.py:65) is far
above it. The gap is reachability, not expressiveness.

### 3c Substrate bottlenecks

- Representation: positional jumps make insertion/movement break routing
  (P(broken jump | length-changing edit) .423, C4-04); the graph profile
  fixes routing but the neighbourhood stays non-graded (E1: graph DESTR
  .36, NEUTRAL .64, USEFUL 0).
- State: registers dominate; the tape (the only addressable memory) was
  never load-bearing in 126 survey runs (C1). Indirection exists (LD/ST)
  but no evolved program uses it, because it costs a coordinated multi-
  instruction change.
- Addressing: by integer index computed in registers; no content
  addressing, no keys as first-class values; the world's tags are 16-bit
  integers the organism must hash itself.
- Credit assignment: one scalar per episode per organism; no per-
  instruction or per-module credit; selection cannot see which part of
  a program helped. The PROTEUS-46 table is the consequence: no
  intermediate is visible.
- Compositionality: no call/abstraction in v0; CALL/RETURN in the graph
  profile exist but nothing selects for reuse; splice crossover is
  structurally blind (C5/E4).
- I/O bandwidth and infrastructure: 98% of each row was SFE round-trip
  (C6); a 400-900 events/s single-writer SQLite ceiling (Artemis REPORT
  s1.3) made per-evaluation provenance impossible at 1e6 evaluations.
  The science left the service for this reason, not for a scientific one.

## 4. Deliverable sections

### Discovery Approach

Build a factory: many procedurally generated small worlds (wforge, WSE
event grammars), a neutral bytecode organism (Proteus), a GA that
selects players in worlds, an execution queue (Vivarium), and a
tamper-evident ledger (SFE) so that any "bump in a flat landscape of
millions of failures" (World Foundry packet, Artemis s1.1) is recorded
with its losers and its prediction order. Later, a lineage scheduler
(Deep Frontier) to keep exploring neglected branches. The bet is that
the physics of intelligence would appear as rare, certifiable
mechanisms (memory, workspace, reuse) found by blind search and
verified by interventions.

### The Brick Walls

1. Coordinated-change desert. The step from one stored value to two
   (or to a fold over D values) has zero single-edit and zero 3-step
   greedy paths: USEFUL 0/18,266, summit 0/395 on W2_K2. Upper bound on
   per-edit success 1.6e-4; the required change is multi-instruction, so
   success probability scales like p^k for a k-instruction coordinated
   edit, which at any realistic p is beyond 1e7 evaluations.
2. Exact-match scalar reward. Reward is word equality; the 1/K echo
   shelf absorbs selection, and anything between shelf and summit is
   invisible. Measured: 175 summits in 1,277 runs, all on single-value
   cells.
3. Instrument saturation at scale. At 3.72e6 evaluations, detectors fire
   ~0.45 per evaluation and 4 of 11 are UNABLE on all 1.78e6 subjects;
   the frontier produced 0 SURVIVING interpretations. The ledger
   ceiling (400-900 events/s) means the provenance layer cannot follow
   evolution at 1e6 evaluations.
4. Substrate exhaustion is the seats' own verdict: "selection under the
   frozen grammar does not climb these worlds at all" (C5 Phase A);
   "the claim 'connectivity removes the cliff' is dead" (E1).
5. Coupling cost: five seats and three REST services per row; science
   0.1 s, row 95-193 s (C6). The ecology spent most of its 17-day life
   on infrastructure (Artemis REPORT s0.2-0.3).

### Seed Viability

The organisms and worlds are a DEAD_END as a reasoning substrate: flat
syntactic search over a total VM with an exact-match reward will not
leave the one-register basin, and two representation changes (fault
encoding, graph encoding) moved how programs die, not what they reach.
What survives is instrumental:
- (a) SFE's provenance properties as an embeddable contract (Artemis's
  hybrid, REPORT s4) -- the only machinery in the program that makes
  best-of-N and post-hoc prediction mechanically visible;
- (b) the WSE reachability table and intervention/null batteries -- they
  would detect a real stored-state or keyed-memory circuit, and they
  already caught a one-register shortcut and a leaked world;
- (c) the per-operator damage-geometry census as a standard reading of
  any new representation before it is used for search.
Hence SALVAGE_COMPONENT.

### Evolutionary Roadmap

Refactors (in order, each gated by the instruments above):
1. Replace syntactic mutation over a flat tape with typed program
   construction. Use a simply typed lambda calculus or typed combinator
   graph (Store : Key -> Val -> Mem -> Mem, Load : Key -> Mem -> Val,
   fold) so every mutation yields a well-typed program and an
   intermediate like "store one more key" is a single typed edit. This
   attacks wall 1 directly: the coordinated change becomes local.
2. Add library learning (MDL compression of solved programs, Stitch /
   DreamCoder-style abstraction; Techne already pinned stitch_core,
   H0H5_STATUS.md "Tools"). A learned abstraction turns a k-instruction
   coordinated change into one call, which is the only known way to beat
   the p^k barrier without changing the world.
3. Replace exact-match per-ask reward with graded, decomposed credit:
   per-key correctness, bit-level Hamming credit on the output, and a
   lexicase selection over asks so a program that solves key A but not B
   is kept. This removes the 1/K shelf trap (wall 2) without shaping
   toward a named mechanism.
4. Compositional credit assignment: record per-subgraph or per-
   abstraction ablation deltas (the intervention battery already computes
   ERASE_* deltas per elite) and bias mutation toward high-credit
   modules; formally, a Shapley-style or counterfactual ablation credit
   per node.
5. Open-endedness metrics replacing detector firing counts: lineage
   activity statistics (Bedau-Packard evolutionary activity) and
   novelty-of-reachable-behaviour measured against a null ladder, with
   the frontier allocator rewarded only on SURVIVING interpretations.
6. Multi-agent: producer/consumer coevolution where one population
   writes keyed state and another must read it (WSE already has
   ASK/PUT); coevolution supplies a graded curriculum (the reader's
   difficulty moves with the writer) instead of a fixed needle.
7. Infrastructure: per-engine embedded provenance receipts (SFE contract
   as a library, not a service), with batch sealing per generation, so
   1e6 evaluations cost a constant number of ledger writes.

THE ONE DECISIVE EXPERIMENT: "typed keyed-memory reachability".
Re-express the two-value keyed task in a typed program representation
with (i) a typed-edit mutation set and (ii) no learned library, and
measure SUMMIT on W2_K2 under the existing reachability table, same
N=200, G=100, same seeds and common random numbers, versus the 0/395
v0 baseline. Preregister: success = Wilson lower bound of summit rate
>= 0.25 over >= 30 seeds AND an intervention vector showing two keys
held in distinct state (ERASE of slot A drops only asks on key A).
Kill criterion: summit rate 0/30 at 10x the v0 budget (N=200, G=1000),
or summits whose intervention vector is the 1/K echo signature -> the
representation hypothesis is dead and the ecology's organism side
should be retired in favour of library learning (step 2) as the next
and last test.

## 5. What would change this verdict

- To VIABLE_SEED: any committed row in which Proteus v0 or graph
  organisms reach SUMMIT on a K>=2 or D>=2 cell with an intervention
  vector showing two independently erasable stores, reproduced across
  >= 3 seeds; or a frontier lineage whose interpretation is marked
  SURVIVING after replay plus controls (DEEP_FRONTIER_CHARTER s1
  COMPARE).
- To DEAD_END: evidence that the reachability table or intervention
  battery are themselves miscalibrated (e.g. a planted two-register
  organism scored as one-register), which would remove the salvage
  value; or an operator ruling that SFE's provenance contract will not
  be adopted anywhere, leaving it with no consumer.
- Unread material that could matter: proteus v0_3..v0_6 equilibrium
  results and campaign6 detector code (I relied on summaries); the
  off-repo M1/M2 ledgers (89,939 / 2,070 experiments) could contain a
  positive the packets do not mention, though no seat document claims
  one.
- Auditor bias: same model family as the seat authors; an independent
  reviewer should re-tally REACHABILITY.jsonl and PROTEUS-46 rows.
