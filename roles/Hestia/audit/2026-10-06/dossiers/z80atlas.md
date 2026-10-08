# Dossier: z80atlas (prometheus/z80atlas + archaeon/z80atlas) -- Z80-like ISA soups

VERDICT: SALVAGE_COMPONENT -- the soups are a careful, well-controlled Tierra/Avida re-run whose substrate tops out at one-instruction task edits; the component worth carrying forward is the instrument (byte-provenance self-replication classifier plus the contingency-controlled computation->resource->reproduction ledger with YOKED/SHUFFLED/RANDOM_REWARD arms), not the ISA.

Auditor: Hestia audit worker, 2026-10-06, read-only. Group G5(a). Rubric: AUDIT_PLAN.md s2-s4.

## 0. Identity

- Engines (census docs/fleet/fleet_state.json at 013e7ce5e):
  - prometheus/z80atlas, "BEE z80atlas substrate", seat Bellerophon, M2, state ACTIVE (last commit 8a2390d82,
    2026-09-30, register-world axis). 28 files.
  - archaeon/z80atlas, "Archaeon z80atlas world", seat Archaeon, M2, state DORMANT (last commit 863d34a55,
    2026-09-23). 52 files.
  - Both are independent builds of the same 2026-09-19 Nestor "Z80 x Atlas" directive: frozen 72 h factor-grammar
    campaign, byte VM, endogenous vs exogenous reproduction, accessibility manipulations of tasks.
- Worktree C:/Prometheus-worktrees/hestia-boot-2026-10-06 at 3fed30ac9 (origin/main merge).
- READ (code): prometheus/z80atlas/vm.py (all), tasks.py (all), grammar.py (all), world.py (lines 1-700),
  coupling.py (1-176); archaeon/z80atlas/vm.py (1-60 + opcode cites), engine.py (1-80 + grep cites),
  grammar.py FROZEN block (33-75), tasks.py (14-39), census/copier_census.py (1-80), CAMPAIGN_CONTRACT.md.
- READ (results/verdicts): roles/Bellerophon/forensics_2026-09-23/POST_CAMPAIGN_FORENSICS.md (s0-s2, s6),
  GROUNDING_REPORT.md (s4-s6, s8-s9), coupling_2026-09-24/COUPLING_CAMPAIGN_REPORT.md (all),
  multiday_2026-09-26/MULTIDAY_CAMPAIGN_REPORT.md (s0-s7), repl_2026-09-30/RESULT.md (s1-s2), RESULT_02.md (s0-s1),
  STATUS_REPORT_2026-10-01.md, calibration/LEDGER.md (grep); archaeon/z80atlas/census/PREREG.json, RESULTS.json
  (summary + per-stratum counts), denovo/PREREG.json (arms), denovo/RESULTS.json (summary, per_arm),
  postcampaign/Z80ATLAS_POSTCAMPAIGN_ADJUDICATION_2026-09-23.md (s A-B), MOAT_LEDGER.json,
  pivot/Z80ATLAS_REVIEW_2026-09-22.md (s0-s1). roles/Archaeon/CALIBRATION_LEDGER.md (grep: no z80 rows).
- NOT READ: prometheus/z80atlas/{geometry,observatory,scheduler,runner,grounding,robustness,coupling_campaign,
  coupling_supervisor,multiday_*}.py beyond grep; tests/ and golden_v1.json; world.py 700-976 (migration,
  telemetry, summary); archaeon/z80atlas/{scheduler,preflight,packet,denovo/run_denovo}.py; all replay JSON bodies
  (REPLAY_*.json, MOAT_LEDGER_CLOSURE, AUDIT_RECEIPT); CAMPAIGN_PACKET.md/PACKET.json; roles/Bellerophon/{e003,
  atlas_bee,prompts,journal}; roles/Archaeon z80 prompts. Raw run logs are host-local on M2 and not in Git
  (Bellerophon reports say so explicitly: COUPLING_CAMPAIGN_REPORT s6, MULTIDAY_CAMPAIGN_REPORT s4).

## 1. Mechanism (what the code does)

### 1.1 Bellerophon VM (prometheus/z80atlas/vm.py)
- One 256-byte address space, code = data (vm.py:42-45). Own tape [0,L), partner tape in "neighbour window" [L,2L),
  16 input bytes at 0xE0, 16 output bytes at 0xF0 (vm.py:28-33). L = 64 (Z80_64, VM_COPY) or 32 (BYTECODE32)
  (world.py:89-91).
- 50 defined opcodes of 256 byte values (vm.py:48-70); the other 206 (80.5%) execute as NOP (vm.py:256), which
  creates long "NOP slides". Registers A,B,C,D (data), S,T (pointers), flags Z,CF (vm.py:120-124). No stack, no
  CALL/RET, no indirect jump. Absolute jumps (JP/JZ/JNZ/JC) take an 8-bit literal target (vm.py:218-224).
- Copy primitives: LDI, LDIR (real Z80 semantics: bounded by C, one step per byte; with C=0 it sweeps up to 256
  bytes) (vm.py:182-194); COPYALL copies L bytes in one instruction, only for the VM_COPY representation
  (vm.py:195-201).
- execute() is a pure function of (memory, entry, budget, inputs) returning a Trace; default budget 256 steps
  (world.py:58). Registers are zeroed at entry unless the 2026-09-30 register-world axis passes regs
  (vm.py:120-124; world.py:351-366).
- Witnesses are hand-assembled programs: replicator = `LD S,0; LD T,L; LD C,L; LDIR; HALT` (8 bytes,
  vm.py:263-265); task witnesses ECHO/INC/COND_ONE/COND_MULTI/SUM2 are 3-12 bytes (vm.py:272-295).

### 1.2 Bellerophon world (prometheus/z80atlas/world.py, tasks.py, coupling.py)
- 144 cells (grid side 12), half filled at init (world.py:56, 251). Each tick every organism picks a partner by
  topology, executes ONCE on fresh random input, is scored, pays energy, ages (world.py:414-488). Lifespan 40
  (world.py:59).
- Reproduction physics decides what neighbour-window writes mean (world.py:9-18, 540-542): ENDOGENOUS_COPY needs all
  L window bytes written; PARTIAL >= 1 byte; OVERWRITE/CONSTRUCTIVE/PAIR >= L/2. EXTERNAL = population manager
  copies by fitness-weighted choice (world.py:646-684, weights 0.05+score_ema at 686-695).
- Tasks are six single-output byte functions (tasks.py:25, 37-52): CONST k, ECHO x, INC x+1, COND_ONE
  (x<128 ? x : x+1), COND_MULTI, SUM2. Only the FIRST output byte is scored (tasks.py:79). Scoring ATOMIC /
  INCREMENTAL (1 - d/128) / NEUTRAL; read gate FORCED zeroes any output before the first IN (tasks.py:65-83).
- Verified competence = exact on a fixed 16-input panel, tape alone, empty window (tasks.py:150-202).
- Physics v3 coupling (coupling.py:1-31, 92-114): a copy-resource R held in a Python ledger OUTSIDE VM memory.
  Every interaction pays BASE (16 or 40); a correct first output pays BONUS 64 under ON; constructing a child costs
  copy_cost (1) per written window byte, so a 64-byte child costs 64 units (world.py:73-76; coupling.py:6-26).
  Control arms: OFF, SHUFFLED (answer for an unseen input), RANDOM_REWARD (bonus to a random organism), YOKED
  (per-tick bonus total of the matched ON run spread evenly), IRRELEVANT (output 0x5A), DELAYED (coupling.py:9-19).
- Self-replication is classified by byte provenance: a birth is SELF_REPLICATION only if >= 0.9 L window bytes
  were moved by a copy opcode executed from the writer's own tape, from the writer's own tape, with fidelity >= 0.9
  before and after execution (world.py:620-632).
- Frozen factor grammar: 14 axes (grammar.py:221-237), validity constraints (grammar.py:274-304), greedy
  pairwise-coverage sampling (grammar.py:346-363), one-factor mutation (366-378), 12 hand-chosen "collisions"
  (246-259), 8 matched-control flips (262-271).

### 1.3 Archaeon VM and world (archaeon/z80atlas)
- Different ISA: every byte decodes, op = byte & 31, r = (byte>>5)&3, hi = byte>>7; 32 opcodes incl. NOP (0,30)
  and HALT (23,31) (archaeon/z80atlas/vm.py:4-15). Own tape [0,G), window at [128,128+G); writes elsewhere are
  refused and counted `illegal` (vm.py:7-9, 98, 113). COPY (op 20: mem[C]=mem[B]; B++; C++) exists ONLY in the
  `vmcopy` substrate (vm.py:14, 102); the `z80` substrate has no copy primitive at all.
- engine.py: N=128, topologies well_mixed/grid/graph/ring/niches (engine.py:50-75), births under ENDOGENOUS_COPY
  need window coverage >= 0.9 (engine.py:320; grammar FROZEN copy_min_frac 0.9 at grammar.py:36), a runtime
  integrity assertion forbids runner-made births under endogenous physics (engine.py:434). Hard max_age 60
  (grammar.py:36; engine.py:376).
- Tasks: 10 named byte functions (archaeon/z80atlas/tasks.py:14-38).

### 1.4 Documented claims vs code
- CLAIMED (vm.py docstring): "mutation alters algorithm AND architecture". CODE: true only in the trivial sense that
  any byte may be opcode or operand; no instruction creates new instructions, addressing modes or memory regions.
- CLAIMED (world.py:17-18): "an organism persists only by executing writes". CODE: true under v2+. Under v1 the
  NICHES_POLLINATION/RESERVOIR migration path spawned world-made copies (defect P1, median 888 per run;
  POST_CAMPAIGN_FORENSICS s2.4); repaired, v1 kept replayable.
- CLAIMED: "computation -> resource -> reproduction" is a physics. CODE: it is a hand-set exchange rate in a Python
  ledger the organism cannot read or write (coupling.py:3-4). It is a reward function in the reinforcement sense,
  dressed as a conservation law (the ledger balance is asserted, coupling.py:27).

## 2. Evidence (tiered)

Bellerophon 72 h campaign + forensics + grounding:
- OBSERVED (committed receipts; raw runs host-local): 63,247 runs, 49,412 factor-vector families, 1,629 flag events
  in 5 high-value classes; ALL five classes FALSIFIED, DETECTOR_ONLY or INSTRUMENT_FAILURE after adjudication
  (POST_CAMPAIGN_FORENSICS headline; GROUNDING_REPORT s8). Promotion threshold reached by 69% of runs, i.e. the
  promotion rule did not discriminate (forensics s1.3, M8).
- OBSERVED: spontaneous own-code self-replication from random populations, CONFIRMED_CAUSAL in grounding; ~7.2% of
  fresh random endogenous runs contain an origin (CI 4.8-9.6%), ~1,100 origins collapsing to 3 mechanistic routes
  (LDIR 57%, COPYALL 13%, LDI loops) plus a context-dependent class (forensics s2.2). Requires LDIR and the
  undefined-byte NOP slide: ablation abolishes it (GROUNDING_REPORT s8, P8).
- OBSERVED: a uniformly random 64-byte tape self-copies alone with p = 3.0e-5 (Z80_64), 6.5e-5 (VM_COPY)
  (forensics s2.6). Replicator lineages carry NO task computation: paired INC beneficial density 0.0001 for random,
  first-gen and evolved tapes alike (forensics s2.6).
- OBSERVED: reproduction-computation ANTAGONISM. Verified task reached EXTERNAL-only 178 pairs vs ENDOGENOUS-only 2
  (p 2.5e-15); seeded hybrid/INC: external 100/100 vs endogenous 2/100 (GROUNDING_REPORT s6, G3). The grafted LDIR
  with C=0 overwrites the input region and destroys the task witness (GROUNDING_REPORT s4).
- OBSERVED: under IMPLICIT pressure the task is causally inert (G1T identical) -- NOT_ADJUDICABLE (s8).

Bellerophon coupling campaign (physics v3, 11,657 runs, COUPLING_CAMPAIGN_REPORT):
- OBSERVED: P1 (correct computation raises reproductive output, seeded fixtures) 40/40 pairs; P2 competence
  enriched ON vs YOKED 149 vs 0; P4 extinction ON 1/150 vs YOKED 67/150. Seed/control fidelity: replay 341/341.
- OBSERVED (and self-dissented by the seat, s5): P1-P3 are MAINTENANCE of hand-written seeded code; P3
  "heritability" is LDIR copy fidelity (0.999 in all arms). Generality 6/6 tasks is generality of maintenance.
- OBSERVED: random soup acquisition B-rand 0/3,200 in every arm. Only acquisition: pure copiers gaining ECHO,
  29/150 ON vs 6/150 in controls (K40), 7 transplanted CAUSAL_COUPLED candidates.

Bellerophon multi-day campaign (4,160 runs, 20,000 ticks, 561 CPU-h, MULTIDAY_CAMPAIGN_REPORT):
- OBSERVED: ECHO copiers acquire INC ON 58/320 (18.1%) vs 0-1/320 controls. INC is ECHO plus ONE byte (INC_A,
  vm.py:280-281 vs 276-277).
- OBSERVED: INC copiers acquire COND_ONE 0/240 in EVERY arm, both K. This is the decisive wall (section 3a).
- OBSERVED: repair 4.7% ON vs 0 controls, not more common than at 500 ticks. Task robustness +1.2 points
  (survivor-selected, single checkpoint pair). Label audit of acquisitions is host-local (not re-derivable from Git).

Bellerophon register-world (REPL-01/02, 2026-09-30):
- OBSERVED: the "state-free genome" residue under a partial register scaffold DISAPPEARS (K3) and does not
  replicate (RESIDUE_NOT_REPLICATED, M1 dominance 1/50 vs 0/50). Every precommitted expectation was lost
  (RESULT_02 s0). The seat's own calibration ledger records the embargo breach and the "kill needs a planted
  positive on real data" lesson (calibration/LEDGER.md line 21).

Archaeon 72 h campaign + post-campaign:
- OBSERVED: 101,003 runs; verified de novo spontaneous replication = 0. All 26 runs flagged
  spontaneous_replication were transplant verifications whose sources were seeded_replicator runs ("inserted twice
  over") (POSTCAMPAIGN_ADJUDICATION s A). Top-30 family table after correction is a 14-point tie whose ranks are
  dict-order artifacts (s B). Seeded moat_advantage: 828 QUALIFIED / 104 VOID of 932 (MOAT_LEDGER.json).
- OBSERVED (census, 24 M uniform random tapes, COPIER-CENSUS-01): z80 substrate (no copy primitive) 0 exact
  copiers in 12 M tapes (upper 95% 3.7e-7 at G=32); vmcopy32 96 exact-capable in 10 M (9.6e-6), of which 98.96% are
  GATED, i.e. exact self-copy happens only at ONE specific input byte (gating_hist {1: 94}). The campaign's single
  surviving random-origin world (1 of 27,141) is LOTTERY_CONSISTENT (lambda 6.9, CI 4.8-11.1): it is a founder
  lottery winner, not evolution toward replication.
- OBSERVED (DENOVO-01): 0/80 de novo replication, all 80 worlds extinct at epoch 61 (= FROZEN max_age 60 + 1) in
  every arm; zero clean endogenous births (denovo/RESULTS.json per_arm). Controls 6/6 + inserted positives PASS.

## 3. Matrix

### 3a. Combinatorial explosion and reachability (side calcs: scratchpad/z80calc.py)
- Genome space: 256^64 = 10^154.1 (L=64); 256^32 = 10^77.1 (L=32).
- Experiment space (Bellerophon grammar): 268,738,560 raw factor vectors; valid fraction 0.0946 by 200k-sample
  Monte Carlo, ~2.5e7 valid. The 72 h campaign touched 49,412 families = 0.19% of valid vectors, 1,802 factor
  PAIRS covered (forensics s1.5). The grammar explodes in experimental-design space, not in organism space; and
  since every flag class fell, more grammar coverage buys nothing.
- Origin of replication (the one thing these soups do reach): basin per tape 3e-5 (Bellerophon, LDIR + NOP slide:
  `LD T,L ; LDIR` is 3 specific bytes, 256^-3 = 6e-8, multiplied up by the 80% NOP slide and many entry points);
  per population-run ~7%. In Archaeon's chemistry (no NOP majority, gated COPY) the per-tape density drops to
  9.6e-6 with 99% gated to one input value, and to < 3.7e-7 without a copy primitive. Replication access is a
  property of the hand-picked chemistry (two builds of the same directive differ by >= 100x), not of evolution.
- DENOVO-01 was a reachability desert by design. Expected number of its 80 worlds containing even one exact-capable
  founder = 80 x (1 - (1 - 9.6e-6)^76.8) = 0.059 (0.064 with the 84 founders actually drawn). A 95% chance of one
  lottery winner needs ~4,063 worlds. The 0/80 null was the predicted outcome, not information about the arms.
  (The census that supplies 9.6e-6 is dated the same day; I did not verify which was frozen first.)
- Task-ladder wall (the important one). ECHO -> INC is one byte (insert INC_A): acquired 18%. INC -> COND_ONE needs
  a compare plus a conditional jump with an exact operand pair: shortest hand form `IN A; CP A,0x80; JC tgt;
  INC A; OUT A; HALT` (vm.py:284-286) inserts 4 specific bytes (CP, 0x80, JC, target). Under BYTE substitution at
  MED rate 0.008/byte, a specific single byte arrives per copy with p ~ 3.1e-5, a specific 2-byte operand pair
  ~ 9.8e-10, a specific 4-byte block ~ 9.5e-19; the multiday campaign's whole execution budget was <= 1.2e10
  organism-executions (144 x 20,000 x 4,160). Neutral drift through NOP slides lowers this, but the measured outcome
  is 0/960. The seat's own explanation is the reward geometry: INC and ECHO tapes are COND_ONE-correct on ~half of
  inputs and get paid, non-competent-earner share 1.0, so there is no gradient (MULTIDAY s2.1). Both causes
  compound: no stepping-stone reward plus a multi-byte jump.
- Measured hit rates, summarised: random-soup task acquisition 0/3,200; random de novo replication (Archaeon)
  0/101,003 runs and 0/80; one-byte rung 58/320; multi-byte conditional rung 0/960.

### 3b. Cosplay vs foundation
- What is called "reproduction": a hand-written 8-byte LDIR program (seeded) or the shortest LDIR/COPYALL copier
  entered through a NOP slide (de novo). The copying itself is a single macro-instruction in the ISA; "replication"
  is the VM's LDIR doing memmove. This is Tierra (Ray 1991) with a memcpy opcode.
- What is called "computation": byte functions of one or two input bytes, scored on the first output byte. The
  hardest task (COND_MULTI) is a 12-byte straight-line program with one branch (vm.py:289-291). No task needs
  memory across executions, iteration over data, or composition of sub-results.
- What is called "learning / acquisition": selection over random byte substitutions in a population, with the
  reward computed by a Python oracle and paid through a ledger. This is Avida's merit-for-tasks scheme
  (Lenski et al. 2003 used a rewarded ladder of 9 logic tasks to reach EQU). Bellerophon re-derived, with
  excellent controls, that removing the intermediate rewards stops the climb.
- Who does the work: (1) the chemistry author (LDIR + 80% NOP decode is what makes replication reachable; ablation
  abolishes it); (2) the task author (witness programs, panel, read gate); (3) the ledger (contingent payment).
  The population contributes 1-byte local search. No component composes: there is no subroutine, no call stack,
  no relocatable code (the v1 seeded hybrid broke precisely because absolute jumps do not relocate -- defect H1,
  vm.py:298-321), no shared module that two lineages can reuse.
- Ceiling, concretely: single-byte-edit hill climbing over straight-line byte functions of <= 2 input bytes,
  first output only, <= 256 steps, 6-8 bit registers, no persistent state. The measured ceiling is one
  instruction insertion per rung; a two-instruction rung with an exact operand pair is not reached in 20,000 ticks.
- Not cosplay in one respect: the seats did not pretend. Bellerophon's self-dissent (COUPLING s5), forensics
  falsifying 5/5 flag classes, and Archaeon's 26/26 reclassification are honest instruments correctly killing
  their own headlines.

### 3c. Substrate bottlenecks
- Representation: flat 256-byte linear tape; 80% of byte values are NOP (Bellerophon) -- neutral space is large but
  semantically empty; 8-bit absolute jump targets make code position-dependent, so duplication-and-divergence
  (the classic route to new function) breaks control flow.
- State/memory: registers zeroed per execution (default). No persistent memory across interactions except the
  register-world axis, whose only experiment returned DISAPPEARS / NOT_REPLICATED.
- Addressing: 256 bytes total with 2L used by tapes, 32 by I/O -> at L=64 only 96 bytes of scratch.
- Credit assignment: entirely external (score of first output -> ledger units). No internal signal, no
  partial-credit structure the organism can exploit; INCREMENTAL scoring was a ruler artifact (DETECTOR_ONLY).
- Compositionality: none at the ISA level (no CALL/RET, no stack, no indirect jump in Bellerophon's ISA; Archaeon
  has `JP r` but no call stack).
- I/O bandwidth: 1-2 input bytes in, 1 output byte read per execution, 1 execution per tick.
- Copy-task antagonism: the replicator and the task share one address space; LDIR with C=0 sweeps 256 bytes and
  overwrites the input region (GROUNDING s4). Reproduction is an attack on computation in this substrate.

## 4. Deliverable sections

### Discovery Approach
Two seats built byte-VM soups in which tapes execute, write into a neighbour window and are scored on tiny byte
tasks, then ran frozen 72 h combinatorial campaigns over ~14 factor axes (reproduction physics, pressure, topology,
task accessibility) to find which structural combination lets reproduction and computation arise and couple.
After the campaigns' headline flags collapsed under forensics, Bellerophon added an explicit copy-resource ledger
paying for correct answers (physics v3) and tested acquisition up a task ladder over 20,000 ticks; Archaeon
measured the random-tape prior of copiers (census) and ran a de novo replication test.

### The Brick Walls
1. Multi-instruction rung wall: INC -> COND_ONE acquired 0/960 in every arm at 20,000 ticks, while the one-byte rung
   ECHO -> INC reached 18%. A 4-byte specific insertion is ~1e-18 per copy at MED rate.
2. De novo replication is a founder lottery: 0 verified spontaneous replications in 101,003 Archaeon runs; the 1
   surviving random world of 27,141 matches lambda = 6.9 from the census; DENOVO-01 had an expected 0.06 positive
   worlds. Bellerophon's 7% origin rate exists only because LDIR + an 80% NOP decode make a 3-byte copier
   reachable (ablation abolishes it).
3. Copy-compute antagonism and inert tasks: under endogenous physics the task is selected against (178 vs 2) or
   causally inert (IMPLICIT); computation affects reproduction only when a Python ledger pays for it, and then the
   effect is maintenance of seeded code (P1-P3) plus one-byte acquisition.
4. Grammar coverage is not the bottleneck: 0.19% of ~2.5e7 valid experiment vectors were sampled, but all five
   high-value flag classes were falsified; more grammar sampling only multiplies false flags (69% of runs met the
   promotion threshold).

### Seed Viability
The Z80-like soup is a re-run of Tierra/Avida, not a new cognitive substrate. It will not show "primitive reasoning
circuits": its tasks are 1-byte functions, its search is 1-byte edits, and its one measured acquisition is the
insertion of a single INC instruction. The seed worth carrying forward is the INSTRUMENT: (a) byte-provenance
self-replication classification (world.py:620-632) that separates own-code copies from sweeps, smears and captures;
(b) the coupling ledger with matched contingency controls (YOKED preserves supply while breaking individual
contingency; SHUFFLED preserves rule structure while breaking learnability; RANDOM_REWARD breaks the individual
link) (coupling.py:9-19, 92-114); (c) the census-as-prior method (copier_census.py) that turns "it arose once" into
a lottery expectation; (d) the bit-for-bit replay discipline (341/341, 114/114). These would detect a real reasoning
circuit's contingent selection advantage in any substrate. Hence SALVAGE_COMPONENT.

### Evolutionary Roadmap
If anyone continues the substrate at all, it must change in these specific ways; otherwise port the instrument.
1. Measure before running: compute the exact mutational graph from every founder to the nearest task-exact tape
   (BFS over 1-3 byte substitutions/insertions on the 16-input panel). Report edit distance per rung. The multiday
   report admits no distance was measured (MULTIDAY s2.1).
2. Stepping-stone lattice (Avida's lesson made formal): define a task lattice where every rung is one instruction
   from a rewarded predecessor (e.g. SIGN = x>=128 flag -> output, then COND_ONE). Pay only exact panel solvers
   of the configured rung so partial solvers stop earning.
3. Compositional ISA refactor: add CALL/RET with a small stack, relative-only jumps (position-independent code),
   and a module/segment boundary so duplicated code keeps working; this is the precondition for
   duplication-and-divergence and code reuse. Formalism: treat genomes as typed straight-line programs with
   subroutine calls (a tiny typed combinator language) so a mutation operator can splice whole subroutines.
4. Separate the replicator's address space from the computer's (or make the copy primitive bounded and
   non-destructive) to remove the LDIR sweep antagonism.
5. Open-endedness and compression metrics: track MDL of the dominant tape (bytes executed per correct function),
   novelty of functions computed (distinct truth tables over the panel), and an activity statistic
   (Bedau-Packard) so "acquisition" means new functions, not maintained fixtures.
6. Multi-agent dynamics that require composition: tasks whose answer depends on another organism's output
   (message passing via the window with typed slots), so cooperation, not just parasitism, can be selected.
7. Tasks with state: sequence tasks (running sum, parity over a stream of 8 inputs) that require memory across
   steps; the register-world axis is the hook, but give the organism explicit read/write state it controls.

THE ONE DECISIVE EXPERIMENT. "COND_ONE with a stepping stone": physics v3, INC-copier founders, three arms
(ON with stepping stones = SIGN task rewarded then COND_ONE; ON flat = current design but partial solvers unpaid;
YOKED), 240 seeds per arm, 20,000 ticks, the same frozen instrument, with the BFS edit distance from founder to
COND_ONE-exact measured beforehand. KILL CRITERION: if ON-with-stepping-stones acquires COND_ONE in <= 2/240
worlds (not distinguishable from YOKED) then the substrate cannot compose even a 2-instruction function under a
graded curriculum and the ISA line is a DEAD_END; if it acquires >= 10% while flat ON stays ~0, the substrate is
only a curriculum follower (Avida reproduced) and still not a reasoning seed unless rung 3 (COND_MULTI) also falls
without new hand-made stepping stones.

## 5. What would change this verdict
- Upgrade to VIABLE_SEED: a rung that requires >= 2 coordinated instructions (COND_ONE or SUM2 from INC) is acquired
  in >= 10% of ON worlds WITHOUT a designed intermediate reward, with YOKED/SHUFFLED near 0, and the acquired tapes
  show reuse of an existing routine (measured by provenance), not a fresh insertion.
- Downgrade to DEAD_END (for the instrument too): if the contingency controls are shown to pass a planted null
  (e.g. YOKED differs from ON for supply-timing reasons alone; the report itself notes YOKED supply is identical in
  total but not per capita, COUPLING s2), or if the byte-provenance classifier is shown to admit sweeps as
  self-copies on a planted negative.
- INSUFFICIENT_EVIDENCE on acquisition claims: the label-audit counts and per-K splits of the multiday campaign are
  host-local and not re-derivable from Git (MULTIDAY s4); an independent rerun from committed code (561 CPU-h) or
  an archived results.jsonl by hash would settle them.
- Auditor caveat: same model family as the authors; I read the forensics and grounding reports, not the raw
  receipts behind them.
