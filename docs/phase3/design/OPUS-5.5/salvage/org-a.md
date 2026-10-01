# Salvage digest org-a -- Organism machinery A: VM-like substrates

Seat: Epimetheus, Phase 3 independent architect OPUS-5.5. Salvage evaluator, read-only.
Frozen basis: RSE_ARCHITECTURE.md + requirements.jsonl at 77d3c99c3. Date 2026-10-01.
Question asked of every component: does it satisfy a Phase 3 requirement better than rebuilding it?

## 0. Verdict in one paragraph

None of the five VM-like substrates can BE or SEED the primary developmental graph machine (DGM, RSE s3), and none
can serve as its slow reference interpreter. The DGM should be written fresh, from its spec, with the slow Python
reference interpreter written first as the executable spec and the fast kernel differentially tested against it
(CMP-01, REP-02). The nearest candidate, proteus.graph_organism.v1, shares only the word "graph": its nodes are single
operations driven by one program counter (a control-flow-graph interpreter), its structure cannot change during a
lifetime (no ORG-04, no ORG-06), its node ids are renumbered by deletion (fails ORG-08), and it carries a live
calling-convention defect that silently made every node persistent in Archaeon's Campaign 6 evaluators (s3.2,
reproduced in a probe). Proteus v0 and the D-5 machine are clean little interpreters, but neither has a graph,
developmental instructions, a provenance shadow, intervention operators or a lattice harness; adapting them means
rewriting more than 95% of the code and inheriting a manifest ABI that 129 files outside proteus/ import. Crius's VM
fails the ORG-16/ORG-17 admission lint by construction: it ships an "in the head" simulator that runs the world's
own dynamics (PSIM/PMATCH) and a substrate-maintained calibration object. Aphrodite, Apollo and Lexis are not
organism substrates at all (an eval-based fold enumerator, a pipeline of named reasoning primitives, and instruments
over that pipeline). Worth keeping: ONE primitive to EXTRACT (Proteus SplitMix64 keyed streams, REP-07); four
HISTORICAL_CONTROL corpora that are cheap known-answer fixtures for R4 search-policy and reachability qualification
and for DEV-02/DEV-14 plant design (the Proteus witnesses plus the PROTEUS-46 harness, the Crius PARTS landscape plus
its id-clock exploit lineages, the D-5 package, and the Aphrodite order-2 exemplar); and about a dozen design lessons
with file:line evidence (s4) that the fresh DGM spec should encode as tests.

## 1. What the DGM needs, and who has it

DGM requirements (RSE s3; ids from requirements.jsonl). Key: Y = present and usable, P = partial or crude,
N = absent, X = present but disqualifying.

    requirement                                   Proteus v0  Proteus graph  Crius VM  D-5 RM   Aphrodite/Apollo
    graph of register-machine nodes, typed ports  N           P (CFG nodes)  N         N        N
      with delays (s3 state)
    developmental instrs SPAWN/LINK/UNLINK/        N           N              P blocks  N        N
      REWRITE/SET-DECAY/PRUNE (ORG-04)
    modifiable modification as a switch (ORG-06)  P code_wr.  N              N         N        N (improver immutable)
    metered internal ticks vs action (ORG-05)     P           P              P         N        N
    multiple timescales (ORG-09)                  N (4 fixed  P (per-node    N         N        N
                                                    policies)   bool)
    invocable stored structure (ORG-10)           N           Y CALL/RETURN  Y BLK_*   N        N
    self-reference arm (ORG-13)                   P (code on  N              P         N        N
                                                    tape)
    no named cognitive modules (ORG-16/17)        Y           Y              X PSIM,   Y        X (Apollo)
                                                                             calib.
    snapshot/restore bit-identical (ORG-08,       P (state is P              P between N/A      N
      DEV-03)                                       plain dict)               tasks    (pure fn)
    stable ids under rewrite (ORG-08)             N           X renumbered   N         N        N
    material provenance shadow (ORG-08, PRV-10)   N           N (edit lists  P origin  N        N
                                                               genome-level) labels
    intervention operators all carriers           P class-NOP N              P block   N        N
      (CAU-01..09, ORG-19)                          knockout                  ablation
    lattice: switches on one path, RNG-neutral    N           N              X global  X        N
      (ORG-20)                                                               flags
    two encodings (ORG-21)                        N           N              N         N        N
    keyed random streams (REP-07)                 Y derive    Y (same prng)  N 1/run   N        P (Aphrodite keyed
                                                                                                   order, fair.py)
    fast kernel + slow reference, differential    N           N              N         P (r0    P (conformance
      (CMP-01, REP-02)                                                                 only)      gate, own DSL)
    measured throughput (probe, meter on)         0.53M op/s  0.46M exec/s   not meas. Numba    n/a

Totals: no column covers more than 4 of 16 rows usefully, and the rows each candidate covers are the cheap ones
(determinism, keyed streams, plain state). The expensive rows -- developmental instructions as ordinary
instructions, provenance shadow, stable ids, intervention operators per carrier, RNG-neutral lattice switches, two
encodings, fast kernel -- are absent everywhere. Those are exactly the rows the requirements price at build L
(ORG-08 L, ORG-20 L, ORG-14 L, DEV-13 L, DEV-14 L).

## 2. Component verdicts (summary)

    #   component                                      category            slot   cost  decisive reason
    C1  Proteus foundry v0 VM + grammar                RETIRE              --     NA    no graph/dev/shadow/lattice; pos. jumps
    C2  Proteus graph_organism.v1                      RETIRE              --     NA    CFG not RM graph; static; ids renumber;
                                                                                         tick-ABI defect
    C3  Proteus SplitMix64 keyed streams (prng.py)     EXTRACT             R0     S     derive-without-advance; cross-host replay
    C4  Proteus witnesses + PROTEUS-46 harness         HISTORICAL_CONTROL  R4/R2  S     known-answer: plant exists, tie-rejecting
                                                                                         greedy walk cannot reach it
    C5  Proteus mutation-kernel crucibles v0.3-v0.6    HISTORICAL_CONTROL  R4     S     AGR-15 precedent; control that cannot fail
    C6  Crius 8-register VM + workspace + blockstore   RETIRE              --     NA    PSIM/PMATCH + calibration = ORG-16/17 fail;
                                                                                         global flags = ORG-20 fake
    C7  Crius PARTS landscape + exploit lineages       HISTORICAL_CONTROL  R4/R2  M     47-edit plant vs (8+24)x300; id-counter
                                                                                         clocks as cheat plants
    C8  D-5 register machine package (agent_d5_blind)  HISTORICAL_CONTROL  R4/R2  S     R==E known answer; G9 history decomposition
    C9  Aphrodite fold-DSL engine                      HISTORICAL_CONTROL  R2     S     canonical order-2 (library-as-prior) shape;
                                                                                         failure corpus
    C10 Apollo program substrates (DAG, blackboard)    RETIRE              --     NA    named reasoning primitives as genes
    C11 Lexis closure/congruence instruments           RETIRE              --     NA    bound to Apollo's Python operators; two
                                                                                         audit designs port as DGM test specs
    C12 DGM kernel + slow reference interpreter (new)  REBUILD             R3     L     need remains; nothing above is adequate

## 3. Component detail

### 3.1 C1 Proteus foundry v0 VM (proteus/foundry/{vm,affordances,grammar,generate,lineage,probes,signatures}.py)

What it really does. A single-organism bounded tape machine. Genome = list of 32-bit words copied to the front of
the tape and executed in place (vm.py:135-137); instruction = 4 words, op = word mod 25 so every word sequence is a
legal program (vm.py:181; affordances.py:8-12). 25 opcodes, none cognitive (affordances.py:28-54). Persistence is a
manifest-level policy in {none, regs, tape, all} applied at tick boundaries (vm.py:139-147). Self-modification only
by ST into the genome region when code_writable (vm.py:206-213). Jumps are positional immediate offsets
(vm.py:236-249). The world drives run_tick(state, inputs, n_out, rng, meter, budget); RND reads an externally
supplied SplitMix64 (vm.py:278-280). Meter is a resource vector, no fitness field (vm.py:70-117).

Correctness evidence. Tests present and run in a scratch copy (git archive, never the repo): 65 passed, 4 deselected
across test_graph_vm, test_replay, test_mutation, test_keyed_memory_witness, test_graph_witness, test_graph_grammar,
test_wp_b1 (b1b deselected: needs integration/harmonia_arena.py, which carries urlopen/subprocess code). Fixtures are
hand-authored expectations; replay is byte-identical; cross-host replay receipts exist for Windows py311/py312 and
Linux py312 (proteus/v0_3, v0_4 CROSSHOST_*.json.gz, contents not re-verified). There is NO differential test against
an independently written reference interpreter.

Defects. LDC reads its immediate from operand b while the affordance prose says c (vm.py:200-201 vs
affordances.py:12; the seat's T9, unfixable without a runtime-hash change). Meter carries wall_s/cpu_s
(vm.py:85-86, 295-296): the raw meter reproduced 0/40 (seat finding), only a projection is an instrument.
organism_id hashes manifest bytes; because op = word mod N_OPCODES, a 25->26 opcode amendment re-decodes 94.87% of
instructions with the id unchanged (seat STATUS 09-04; mechanism visible at vm.py:181). Positional jumps make insertion
and movement break routing (Archaeon C4-04). HALT and budget exhaustion both reset ip to 0 (vm.py:194, 283-284), an
execution-order channel a closure audit would have to list. Pure Python single core: 0.53M ops/s measured with meter
on (probe s5), about two orders below the DGM's stated target.

Fit to slots. Could it be the DGM? No: no graph, no developmental instructions, no provenance shadow, no stable
substructure ids, intervention only as class-wide knockout to NOP (signatures.py), no lattice harness, one encoding.
Could it be the slow reference interpreter? No: a reference interpreter must implement DGM semantics; this
implements different semantics. Could it be the probe kernel (AGR-07)? No: same model family as the DGM author
(independence class below I2) and the same conventions the probe kernel must deliberately avoid (absolute
addressing, zero-initialised state).

Coupling. Stdlib only inside the package (import set verified); 129 tracked files outside proteus/ import it
(archaeon campaigns 1-6, wse, z80atlas, rie, tests; genesis/harmonia_a; techne; roles/Nestor; vivarium; nyx;
engine/necropolis). Any change is a runtime-hash transition with that blast radius. proteus/workspace.py shells out
to git (D-23 guard), a host assumption.

Category RETIRE (no Phase 3 production role). Keep a frozen copy only as the substrate underneath C4.

### 3.2 C2 Proteus graph_organism.v1 (proteus/graph/{vm,affordances,grammar,generate,lineage,handover,witness}.py)

What it really does. Genome = nodes {kind, params, persist} + data_edges + control_edges + entry + limits
(vm.py:3-9). Each node is ONE operation of 25 kinds (affordances.py:36-62), not a register machine. Execution is a
single cursor `cur` walking control edges (vm.py:218-332): a sequential control-flow-graph interpreter. Data inputs
read other nodes' last values (vm.py:223). ROUTE selects a control port by predicate; CALL/RETURN use a bounded stack
(vm.py:276-299). Nodes not control-reachable from entry are dormant and cost nothing (vm.py:106-118). No instruction
can change nodes or edges; LD/ST only touch a flat state array (vm.py:246-253). Mutation is external and produces
explicit edit lists, child == apply_edits(parent, edits) (grammar.py:1-6, 66-117).

Correctness evidence. test_graph_vm.py (10 tests: replay, dormant, route, call reuse from two sites, yield/halt,
persistence flags, validation, ABI, import hygiene) passed in the scratch run above. No differential test.

Defects (two verified in code, one reproduced by probe).
- TICK-ABI DEFECT (new finding, reproduced). begin_tick applies the persist policy only when st["ticks"] != 0
  (vm.py:196-205), and run_tick never increments st["ticks"] (vm.py:337-341), unlike v0 which does
  (foundry/vm.py:286). Proteus's own tests and witness increment it by hand (test_graph_vm.py:52, witness.py:95).
  handover.py:17 tells consumers the world ABI is identical to v0. Archaeon's evaluators call begin_tick then
  run_tick and never increment (archaeon/campaign6/substrate.py:44-46; archaeon/campaign6/worlds/runtime.py:205-207).
  Under that convention, nodes with persist=false, the state array with persist_state=false, and the call stack all
  persist across ticks. Probe: an accumulator node with persist=false outputs [1,1,1,1,1] under the test convention
  and [1,2,3,4,5] under Archaeon's convention. Every graph-organism result produced through those two evaluators ran
  with all state persistent regardless of genome flags; memory or persistence readings of graph organisms there are
  suspect. (archaeon/frontier was not inspected.) This is precisely the ORG-19 failure class: a persistence channel
  opened by caller convention and invisible to the substrate's unit tests.
- Node ids are not stable under rewrite: remove_nodes renumbers every later index (grammar.py:80-87). Probe: the ADD
  node at index 1 becomes index 0 after deleting node 0. Fails ORG-08 "substructure ids stable under rewrite".
- Dormant-attach operators (NODE_ADD, EDGE_ADD, SUBGRAPH_COPY(_ATTACH), CROSSOVER_SUBGRAPH) are 100% neutral by
  construction (PROTEUS-46 table, per dossier): they cannot by themselves change behaviour.
- Throughput 0.46M node executions/s (probe, meter on).

Fit. As a DGM seed it would need: register files and programs per node, concurrent node execution with delayed
ports, developmental instructions, stable ids, provenance shadow, interventions, lattice, encodings, fast kernel.
That is the whole DGM; the 342-line interpreter would be under 5% of it and brings an ABI, a manifest schema and a
consumer base. Ideas worth carrying (not code): dormant structure as first-class neutral redundancy (ORG-11); edit
lists as the genome-level lineage record (feeds AGR-04 and R4 lineage); a deterministic meter with no timings
(vm.py:121-123, the 0/40 lesson).

Category RETIRE.

### 3.3 C3 Proteus SplitMix64 keyed streams (proteus/foundry/prng.py, 83 lines)

What it really does. 64-bit SplitMix64 in pure integer arithmetic (prng.py:33-47); seed_from(*parts) hashes typed
parts through sha256 (prng.py:19-30); derive(*tags) returns an independent child stream keyed by (current state,
tags) WITHOUT advancing the parent (prng.py:78-80); rejection-sampled randbelow (prng.py:49-56). The V0.6 live kernel
relies on derive-without-advance to make parallel runs byte-identical to serial ones (v0_6/livekernel.py:7-10).

Correctness evidence. Exercised by every Proteus replay test (passed); cross-host receipts as in C1. No published
statistical test battery (not needed for keyed-stream semantics, but REP-07 wants the validator, not the generator).

Defects / hardening. derive keys on the parent's CURRENT state, so the same tag derived before and after any draw
gives different streams; R0 must derive only from untouched roots (arm root, world-instance root, organism root) to
keep arms independent of consumption order. weighted() and unit() use floats (prng.py:58-76): deterministic under
IEEE-754 but should be integer in R0.

Slot R0 (deterministic runner, keyed streams; REP-07, ORG-08 "deterministic execution from keyed seeds"). Category
EXTRACT, cost S: copy, convert weighted() to integer, add a runner-side validator that rejects undeclared shared
streams (REP-07 test). Honest note: rewriting 80 lines is equally cheap; the value is the reviewed design plus
cross-host evidence.

### 3.4 C4 Proteus known-answer search fixtures (proteus/eval/keyed_memory_witness.py, proteus/graph/witness.py,
proteus/round2/falsifier_46.py + PROTEUS-46_PREREGISTRATION.md)

What it really does. A 12-instruction keyed two-value memory under the frozen v0 ISA with negative (one-value) and
cheat (echo) controls (keyed_memory_witness.py:1-36; tests passed), a graph-organism equivalent (graph/witness.py),
and the PROTEUS-46 harness: K=400 single-edit children per operator classified USEFUL/GRADED_DOWN/DESTROYED/NEUTRAL,
plus random and greedy 3-step walks (falsifier_46.py:30-35, 100-135).

Correctness evidence. Witness tests passed. Harness defect verified here and in evidence/atl.md V7: WALK_STEPS = 3
(falsifier_46.py:31) and the greedy walk starts best_key = (cur, 0) and scores children (two_key, -ops)
(falsifier_46.py:120-127), so a neutral child (same two_key, ops >= 1) is never accepted. A 5-edit
duplicate-and-diverge neutral path to 6/6 is reported by Artemis D002-03q (worker claim, unverified). RSE s1 cites
this as the manufactured cliff that suppressed 299,991 rows.

Slot. Known-answer fixture for R4: qualifying a declared search policy and the reachability estimator (PRS-02,
PRS-03, ORG-15 tiers) on a landscape where the plant is known to exist and a strict-improvement policy is known to
miss it. Substrate-independent of the DGM, which is a feature for R4 qualification (the search engine must not be
tuned to one substrate). Not a plant for organism rulers (same author family as the DGM). Category
HISTORICAL_CONTROL, cost S: freeze, verify the D002 path independently, seal the answer, wrap as an R4 fixture.

### 3.5 C5 Proteus mutation-kernel crucibles (proteus/v0_3 .. v0_6; kernel.py, livekernel.py, equilibrium.py, nc5.py)

What it really does. Measures the UNSELECTED variation kernel as a Markov chain over enumerated structural states
(genome length x tape words; 124 then 2,044 states) by executing grammar.mutate on random genomes
(v0_5/kernel.py:1-18, 55-83), then computes probability current J, entropy production, operator attribution, with a
dual-sample noise floor.

Correctness evidence. Preregistered passes; Harmonia 2026-09-18 ruled it ADMITTED AS A DETECTOR, NOT AS AN ABSENCE
INSTRUMENT: the reversible-reference check cannot fail by algebra, and the occupancy-TV floor was quoted, not
computed (dossier s7, s9 T5). `random` is used in v0_6/equilibrium.py:16,171 (seat's T8). Coupled to
proteus.foundry.grammar (kernel.py:24, livekernel.py:20). Tests not run.

Slot. AGR-15 requires every variation operator to publish its unselected variation kernel; PRS-03 needs reachability
under the declared operators. The method (execute the live operator on enumerated states, never model it; attribute
current to operators; dual-sample floor; a control that CAN fail) is the precedent; the code does not transfer to
DGM operators. Category HISTORICAL_CONTROL, cost S (archive with the Harmonia ruling attached as the lesson).

### 3.6 C6 Crius 8-register VM + workspace + block store (crius/vm.py 705, workspace.py 294, artifacts.py 249,
env.py 146)

What it really does. A register bytecode VM over ints and int tuples, about 55 opcodes (vm.py:29-85): arithmetic,
vector get/set, branches with absolute targets, INPUT of task fields, ACT, a costed data workspace (cells, streams,
records, links, alloc, find; workspace.py:50-270) and a block store of executable code blocks with
create/append/patch/copy/compose/delete/invoke and 8 local state slots (artifacts.py:35-233). Registers reset every
task (vm.py:1-7, 263); persistence across tasks only via workspace and blocks. Block invocation is a Python call
(vm.py:287-309) with RecursionError and TaskOver exceptions as control flow (vm.py:275-284; env.py:15-16).

Correctness evidence. 41 tests present; run in a scratch copy: 41 passed in 214 s (replay hashes, receipts, integrity,
C2 typed ops, terminal paired-stream alignment). Strong controls exist at the evaluation layer (FRESH vs ACCUMULATED,
RESET, SCRAMBLE, ABLATION, TRANSPLANT, RECORD_IDS_ONLY; dossier s7).

Defects (verified in code).
- ORG-16/ORG-17 by construction: PSIM/PMATCH apply a stored procedure "in the head" using the WORLD's own transition
  function world_c1.apply_primitive (vm.py:82-84, 490-497, 543-556): a world-supplied forward model. The typed rungs
  maintain a calibration object on the organism's behalf (vm.py:438-472) that gave every acting typed candidate a
  constant reuse_gain of about 7 (dossier). WS_FIND is an associative-search convenience (workspace.py:151-160).
- ORG-20 fake, exactly as written in the requirement: substrate switches are a module-global dict (vm.py:88-93) and a
  module-global op set (search.py:50); one random.Random per run (search.py:261) draws instructions by
  rng.choice over the op list (search.py:54), so turning typed_procedures or psim on changes RNG consumption for every
  later event.
- Organism-visible allocator ids (record ids workspace.py:195-196; block ids artifacts.py:134-135) became clocks: the
  exploit lineages E1-E4 and the C1b record-id clock (dossier s9 timeline 3). An unlisted channel in ORG-19 terms.
- No mid-task snapshot: execution state lives in the Python stack; workspace/block snapshots are deepcopies between
  tasks only (workspace.py:92-116; artifacts.py:91-104). No provenance shadow beyond block origin labels and a capped
  event log (artifacts.py:30-32, 114-126).
- Hot loop dispatches on opcode NAME strings (vm.py:324, 342-414); lambdas per arithmetic op (vm.py:347-351).

Fit. ORG-10's motive cites the Crius workspace, and the block store is the program's best precedent of code-as-data
invocation; but in the DGM invocation is native (nodes, SPAWN templates, REWRITE), so nothing here is needed as code.
Category RETIRE.

### 3.7 C7 Crius PARTS landscape and exploit lineages (crius/parts_c2.py, crius/runs/parts_c2*/PARTS.md,
crius/fixtures/c0_failure_families.json, exploit_probe.py, c2_terminal.py)

What it really does. Hand-written programs P_BASE(19) .. P_REC_INV_PLAN(64) giving a value landscape by construction
(recorder alone -0.001, invoker alone -0.002, pair +1.138, full +15.97 at 47 edits; dossier s6) and the exploit
families (block-id clock, replayed own random walk, workspace-conditioned walk, record-id clock reproduced exactly by
RECORD_IDS_ONLY).

Slot. (a) Known-answer fixture for R4 reachability and concentration-floor estimators (PRS-03, PRS-13): RSE s1 cites
"a 47-edit reuse mechanism against (8+24) x 300" as a plant that existed and was never found; Artemis R-07 (worker,
unverified) reports a 41-neutral-insert path. (b) Design source for MEA-02/MEA-05 cheat plants: "a monotone id
counter in a persistent store satisfies ACC > FRESH by the letter" must be a sealed cheat class in the DGM plant
library, re-expressed in DGM physics. (c) Cross-reference for R1: the RELAY world (crius/world_c1.py) is the closest
existing design to anchor family F5 ("table memoisation provably transfers nothing"); world-forge salvage owns that
verdict. Category HISTORICAL_CONTROL, cost M (freeze + seal for R4; re-expressing clock cheats in DGM physics).

### 3.8 C8 D-5 register machine package (agent_d5_blind/: substrate/rm_vm.py 78, rm_fast.py 127, mutation/physics.py
87, exact_oracle, reachability_oracle, learner/m1.py, navigators/m0.py, task_generators/*, VERDICT.md)

What it really does. A stateless function evaluator: 8 registers, 16-bit words, 14 opcodes, max 24 instructions, 512
steps; inputs loaded into r0..r7, result is r0 (rm_vm.py:19-61). Tasks are input/output tables on 4-64 points
(families.py:23-25). A GA with an immigrant library evolved programs per task (the substrate Ergon's Gen-0..3 retention
lineages consumed). Numba fast path (rm_fast.py) with an equivalence test against the reference.

Correctness evidence. Run in scratch: test_smoke "ALL SMOKE TESTS PASS"; test_equivalence "EQUIVALENCE PASS: 2402
programs x 128 inputs, bit-identical". Weaknesses of that equivalence, verified: the fast path loads only x0, x1
(rm_fast.py:38-40) while the reference loads up to 8 inputs (rm_vm.py:22-23); the test covers arity 1-2 only
(test_equivalence.py:25-26) and compares r0 only, not full register state or step counts (rm_fast.py:105-110).
Probe: program MOV r0,r2 on inputs (1,2,3) gives reference 3, fast path 0. Latent, since every shipped family has
arity <= 2. The mutation-class ablation changes RNG consumption (physics.py:41-42), so it is not lattice-safe.

Fit. Not a DGM seed (no world loop, no persistence, no I/O stream). Its value: (a) the R == E theorem (INSERT-complete
physics makes every expressible witness reachable by an explicit edge-checked path, reachability_oracle/
reachability.py:1-12, 33-62) plus 78 tasks with constructive witnesses and an exact oracle = a known-answer fixture for
the ORG-15 tier estimators and PRS-03; (b) the G9 decomposition (shuffled-history arm retains 100% of a +10.95 pp
advantage, random-library arm 39%; VERDICT.md) is the cleanest historical template for DEV-02 developmental controls
("library content vs developmental correspondence"); (c) the only fast/slow differential pair in this group, and its
gaps define what CMP-01 must demand (full-state, full-arity, step-count equality). Category HISTORICAL_CONTROL, cost S.

### 3.9 C9 Aphrodite fold-DSL engine (roles/Aphrodite/engine/: engine.py 1018, basis_v4.py 345, improver.py 206,
fair.py, conformance.py, tier3*.py, run_s3s4.py, a16-a23)

What it really does. Programs are 4-tuples of Python expression strings ('fold', init, body, final) evaluated with
eval under restricted builtins (basis_v4.py:160-171); the "organism" is an enumerator over a finite space (about
2.26e8 folds) whose only mutable object is a proposal library that reorders enumeration; mutation, fitness and
selection are immutable code (improver.py:1-11). No lifetime, no world interaction, no state.

Correctness evidence. 50 test functions in 6 files (identity, improver, membrane, semantics, slice2b); not run (they
test the semantic-identity layer, not anything a substrate needs). Verified defects: S4 conditions
"4_hostile_evaluation" and "8_no_donor_state" are literal True (run_s3s4.py:391, 420); the positive-control schema
equals the derived schema (dossier, seat's own TH-021). accel/ contains cloud scripts and an env file
(roles/Aphrodite/engine/accel/azure/azure.env) that was listed by name and NOT opened.

Slot. DEV-14 requires planted order-1, order-2 (library as proposal prior), order-3 and maturation-clock organisms.
Aphrodite's improver is the program's canonical order-2 shape: fixed rule plus inherited library that changes search
order but never the rule. It must be re-expressed as a DGM organism to be a plant; the corpus documents what it looks
like when mistaken for recursion. Also a failure corpus for MEA-05/MEA-16 (constant-true gate clauses; positive
control identical to the treatment; tribunal admitting exactly the abstraction's own span). The conformance gate
(conformance.py:1-14; a 21,600 sweep missed an output-ceiling defect later found as 4,501 mismatches) is a lesson for
CMP-01 corpus design. Category HISTORICAL_CONTROL, cost S.

### 3.10 C10 Apollo program substrates (apollo/src/genome.py, blackboard.py, blackboard_ops*.py, blackboard_evolve.py)

What it really does. v2: routing DAGs over 25 fixed "Frame H" primitives named solve_sat, bayesian_update,
sally_anne_test, track_beliefs, confidence_from_agreement, etc. (genome.py:17-27), loaded from
agents/hephaestus/src/forge_primitives (genome.py:50-56). Branch C: a linear pipeline of named operators over a typed
blackboard with slots hypotheses, probabilities, confidence (blackboard.py:19-60). Multiple-choice text tasks.

Correctness evidence. Not run. Historical: home-battery 0.6000 collapsed to 0.0667 on Charon's blind battery (40/42
abstained); the crossover default 0.0 suppressed the only improving operator (blackboard_evolve.py:802; atl C5).

Fit. Fails ORG-16 (named cognitive modules as genes) and ORG-17 (competence supplied by the forge author) by
construction; requirement ORG-17's motive literally cites "Apollo solvers". Category RETIRE. (The blind-battery
collapse and the ablation-wall corpus are failure-corpus material for other groups, not organism machinery.)

### 3.11 C11 Lexis closure and congruence instruments (roles/Lexis/instruments/*.py, about 4.7k lines)

What it really does. Exhaustive product-BFS closure of Apollo's admissible programs over a battery
(product_ceiling*.py), and a congruence audit of Apollo's Python operators: heap aliasing (A-C), hidden module state
(D), escape hatches (E), history independence (F), cross-task contamination by building tables in original vs
reversed order (G) (congruence_audit.py:1-55).

Fit. All bound to Apollo's Python operator set, which is retired. In a DGM whose state is flat integer arrays,
A-E are moot by construction; F and G port as DGM closure-audit test specifications (ORG-19), about 50-100 lines.
Closure enumeration is the method ORG-15 names for proving non-expressibility; the code does not transfer.
Category RETIRE (design notes carried in s4). Not run.

### 3.12 C12 The DGM kernel and slow reference interpreter (new build)

Need: REQUIRED at SLICE (ORG-01..08, ORG-20, CMP-01, REP-01, REP-07) and CORE (REP-02 slow reference). Nothing in this
group is adequate (s1 matrix). Category REBUILD, cost L (30-100M tokens): slow Python reference first as executable
spec (~1.5-3k lines), fast kernel (compiled or Numba) differentially tested on full state, instrument hooks (shadow,
stable ids, per-carrier interventions, trace), lattice harness with regression hashes, two encodings, closure audit.
ORG-08 and ORG-20 alone are priced L in requirements.jsonl.

## 4. Lessons the fresh DGM spec should encode as tests (each with its evidence)

1. Total decoding: every genome decodes to legal instructions without repair (Proteus op = word mod N, vm.py:181).
   Pair it with the identity lesson: hash (genome, basis/affordance table, runtime), never genome bytes alone
   (25->26 opcodes re-decoded 94.87% with id unchanged).
2. The runner, not the caller, owns tick boundaries; persistence semantics are tested THROUGH the production runner
   (Proteus graph tick-ABI defect, graph/vm.py:196-205 and 337-341 vs archaeon/campaign6/substrate.py:44-46).
3. Organism-visible ids are a channel. SPAWN must not return a monotone id the organism can read, or the id counter
   is listed in the ORG-19 closure audit with an intervention operator (Crius id clocks, workspace.py:195-196,
   artifacts.py:134-135). Stable ids exist for instruments; organisms address by ports.
4. Lattice switches are per-instance configuration on one code path; a switch must not change the structure of
   random draws (Crius vm.py:88-93, search.py:50-54, 261; D-5 physics.py:41-42). Regression-hash test: switch
   flipped on a switch-irrelevant run yields identical hashes (ORG-20 test).
5. Deletion must not renumber surviving elements (Proteus graph grammar.py:80-87). Ids are allocated, never
   compacted.
6. No timings in any meter or identity observable (Proteus Meter 0/40 lesson; graph GraphMeter fix, graph/vm.py:121-123).
7. Fast/slow differential testing compares full state (all registers, edges, shadow, step counts, RNG positions) on a
   generated corpus that includes boundary, overflow and maximal-arity programs (D-5 r0-only and 2-input gap;
   Aphrodite's 21,600-case sweep that missed a ceiling defect).
8. Any "simulate in the head" or calibration convenience is an ORG-16/17 lint failure (Crius vm.py:438-556).
9. Neutral structure is first-class (dormant nodes) but neutral-by-construction operators must be reported in the
   operator kernel publication (AGR-15), since they cannot change behaviour alone (PROTEUS-46 table).
10. Execution-order resets (Proteus HALT/budget ip := 0, vm.py:194, 283-284) and call stacks are channels for the
    closure audit.
11. A control that cannot fail is not a control (Harmonia ruling on the Proteus kernel's reversible reference).
12. Search acceptance rules are declared and tested on a known neutral-path fixture before any "cliff" is typed
    (falsifier_46.py:120-127; C4).

## 5. Probes and tests actually run (all from a git-archive copy in the session scratchpad; repository untouched)

    command (cwd = scratch copy, PYTHONDONTWRITEBYTECODE=1, pytest -p no:cacheprovider)        result
    pytest proteus/tests/{test_graph_vm,test_replay,test_mutation,test_keyed_memory_witness,
           test_graph_witness,test_graph_grammar,test_wp_b1} -k "not b1b"                     65 passed, 4 deselected, 11 s
    pytest crius/tests                                                                         41 passed, 214 s
    python agent_d5_blind/substrate/test_smoke.py                                              ALL SMOKE TESTS PASS
    python agent_d5_blind/substrate/test_equivalence.py (NUMBA_CACHE_DIR in scratch)           2402 programs x 128 inputs pass
    probe_orga.py (scratch, written for this digest)
      graph persist=false accumulator, ticks incremented by caller                            [1, 1, 1, 1, 1]
      same, Archaeon convention (begin_tick, no increment)                                    [1, 2, 3, 4, 5]
      node index after remove_nodes([0])                                                      ADD 1 -> 0
      Proteus v0 throughput, meter on                                                         0.53M ops/s
      Proteus graph throughput, meter on                                                      0.46M node-execs/s
      D-5 MOV r0,r2 on (1,2,3): reference vs fast                                             3 vs 0

Not run: Proteus tests that shell out to git or write files (test_workspace, test_pre_t1_gates,
test_rule_table_mint, test_package_import_hygiene); Aphrodite, Apollo, Lexis tests; any experiment or campaign.

## 6. Reading record

Opened: RSE_ARCHITECTURE.md; requirements.jsonl (ids ORG-01..21, DEV-03, DEV-13, DEV-14, REP-01, REP-02, REP-07, CMP-01,
AGR-07, AGR-15, CAU-08, CAU-09, PRV-10 in full); ENGINE_PORTFOLIO.md (grep); evidence/atl.md and idx.md (grep);
intake dossiers Proteus, Crius, Ergon (s1-s6), Aphrodite (s0-s12 head), Apollo (s1-s4), Lexis (s1-s4).
Code read in full: proteus/foundry/vm.py, affordances.py, prng.py; proteus/graph/vm.py, affordances.py;
crius/vm.py, workspace.py, artifacts.py, env.py; agent_d5_blind/substrate/rm_vm.py, rm_fast.py, test_equivalence.py,
test_smoke.py, mutation/physics.py, exact_oracle/oracle.py, reachability_oracle/reachability.py, VERDICT.md (head).
Code read in part: proteus/graph/grammar.py (1-130), proteus/v0_5/kernel.py (1-120), v0_6/livekernel.py (head),
proteus/eval/keyed_memory_witness.py (head), proteus/round2/falsifier_46.py (25-135), proteus/workspace.py (head),
proteus/tests/test_graph_vm.py (1-60), test_wp_b1.py (1-110), archaeon/campaign6/substrate.py (25-60),
archaeon/campaign6/worlds/runtime.py (185-240), crius/search.py (grep), roles/Aphrodite/engine/basis_v4.py (1-120),
fair.py, conformance.py, improver.py (heads), run_s3s4.py (386-422), apollo/src/genome.py (1-80),
apollo/src/blackboard.py (1-60), roles/Lexis/instruments/congruence_audit.py (1-60).
Not opened by rule: roles/Aphrodite/engine/accel/azure/azure.env (env file); roles/Aphrodite/engine/accel/runpod/
runpod_api.py (possible credentials). No holdout or nestor_secrets paths arose in this group.
