# Salvage worker report: scope 1, program-like organism substrates

Deposited by Dionysus[m1-3815a3b9] on 2026-10-01. The worker's transcript
file is empty on this host, so the text below was copied by Dionysus from the
worker's final message as it arrived in the session. It is meant to be
verbatim; any slip in copying is Dionysus's.

Brief: roles/Dionysus/prompts/2026-10-01_salvage_workers/00_COMMON.md and
01_SCOPE_program_substrates.md. Worker model: opus, read-only.
Worker usage as reported by the harness: 470,533 tokens, 122 tool uses,
about 17.9 minutes.

This is a worker's fact sheet. Its claims are the worker's, graded by its own
VERIFIED BY ME lines. Where SALVAGE_MATRIX.md relies on one, it says so.

----------------------------------------------------------------------

SALVAGE FACT-FINDING, SCOPE 1: program-like organism substrates (slot WM, experiment P3)
Worker for Dionysus[m1-3815a3b9]. Worktree dionysus-base-role at e3d7c7034. Read only. No tests or runs were executed. Every search excluded holdout and nestor_secrets paths.

----------------------------------------------------------------------
COMPONENT: 1a. Proteus v0 player VM (proteus.foundry), grammar v0.4, kernel crucibles
PATHS: proteus/foundry/{vm,affordances,prng,lineage,grammar,signatures}.py; proteus/v0_3/battery.py; proteus/v0_5, proteus/v0_6
OWNER / DATES: Proteus. proteus/foundry runs from 2026-09-02 (20a523289) to 2026-09-03 (d40e1b279) and has been frozen since. proteus/ as a whole ends 2026-09-18 (6a98ef0bb).
WHAT IT REALLY DOES:
- A pure-Python tape machine. The genome is copied to the front of a tape of 32-bit words and executed in place.
- Instruction = 4 words (op,a,b,c). op = word mod 25 and register fields are taken mod n_regs, so every word sequence decodes.
- ISA: NOP HALT YIELD LDC MOV LD ST ADD SUB MUL AND OR XOR NOT SHL SHR EQ LT JMP JZ JNZ IN INQ OUT RND.
- State is tape (16-4096 words), regs (2-16), ip and ticks. A manifest (genome) field persist {none,regs,tape,all} decides what survives a tick. code_writable lets ST rewrite the code region.
- Jumps are positional. Memory addressing is absolute by register value. There is no call/return, no block store, and no create or delete.
SIZE: foundry is 1,396 Python lines. The whole package has 363 test functions in 33 files.
DEMONSTRATED CORRECTNESS:
- test_replay.py has 9 tests, including checkpoint_restore_continues_identically.
- A differential shadow decoder (v0_3/battery.py) matched the VM bit for bit, with 0 divergences.
- Replay showed 0 divergences across 3 runtimes, all on one machine.
- Defects:
  - The docstring says operand c holds LDC's immediate and the jump offsets. vm.py reads slot b for both (affordances.py:11-12 against vm.py:201,237).
  - The PROTEUS-46 greedy walk can never accept a neutral child (round2/falsifier_46.py:119-127).
  - organism_id pins bytes, not execution (dossier).
INTERFACE:
- Player(manifest).run_tick(state, inputs, n_out, rng, meter, budget) returns (outputs, halt|yield|budget).
- Deterministic and integer. RND reads a caller-supplied SplitMix64 keyed by sha256 parts (seed_from/derive).
- lineage.checkpoint/restore is exact.
- The Meter counts ops; nothing is charged. No model call.
THROUGHPUT / SCALE: 3.75e6 ops/s on one core, 50 organisms x 40 ticks, meter on, M2 (roles/Archaeon/journal/2026-09-16_m2-411504ab.md:68). No compiled path.
COUPLING:
- Stdlib only.
- 117 files outside proteus/ import it.
- RUNTIME_HASH covers vm.py and affordances.py, so any edit creates a new runtime for every consumer.
FIT TO SLOT: WM.
- Meets ORG-04, ORG-06 and ORG-08.
- Partial on ORG-01 (no partition, no cost), ORG-02 (persist is genome-owned), ORG-03 (a,c,f; b only as persistent tape; d,e,g absent; h counted only) and REPR-01 (one host).
- Fails COMP-01 (about 27x below 100M/s per core) and DEV-01.
MODIFICATION COST: XL to make it the WM base. Store, tags, call with arguments, create/delete, energy and rent, partition, switches, lifetime structure and a compiled kernel would all be added under a new runtime hash. Rebuilding from scratch: L.
VERIFIED BY ME: ISA, decoding, state, persist, checkpoint and its test, PRNG, meter, both defects, shadow decoder, replay record, throughput lines, importer count. From the dossier, unchecked: organism_id hazard, crucible results.

----------------------------------------------------------------------
COMPONENT: 1b. Proteus graph_organism.v1 (proteus.graph)
PATHS: proteus/graph/{vm,affordances,grammar,lineage}.py; proteus/tests/test_graph_*.py
OWNER / DATES: Proteus. All of it is dated 2026-09-18 (348d12816 to 6a98ef0bb), 3 commits.
WHAT IT REALLY DOES:
- The genome is a node list (25 kinds) plus data edges, control edges, an entry node and limits.
- Kinds: NOP HALT YIELD CONST ID LD ST ADD SUB MUL AND OR XOR NOT SHL SHR EQ LT ROUTE CALL RETURN IN INQ OUT RND.
- ROUTE picks a control port by predicate. CALL pushes its "after" target on a stack bounded by call_depth_max (0-16). RETURN pops.
- No arguments pass beyond the static data edges. There are no positional jumps.
- State is per-node values (per-node persist flag), a 4-1024 word state array (LD/ST by value), a resume point and the stack.
- Nothing can rewrite the graph during life.
SIZE: 1,308 Python lines. 26 test functions in 5 files.
DEMONSTRATED CORRECTNESS: Tests cover byte-identical replay over a random population, dormant nodes costing nothing, CALL reusing one subgraph from two sites, and validation refusals. Its only campaign use is PROTEUS-46 (USEFUL 0/4,881, dossier).
INTERFACE:
- Same run_tick ABI as v0. Deterministic and integer.
- Invalid manifests raise ValueError, so decoding is total only inside the grammar's closure.
- No checkpoint/restore function exists (the state is a plain dict, copyable; code-inferred).
THROUGHPUT / SCALE: Not recorded.
COUPLING: Imports proteus.foundry.prng. Consumed by archaeon/campaign6 (dossier).
FIT TO SLOT: WM.
- ORG-03: c and f yes; d partial (no arguments). e holds only for search edits. b and g are absent.
- Fails COMP-01.
MODIFICATION COST: XL. Rebuilding from scratch: L.
VERIFIED BY ME: Everything above except the PROTEUS-46 rates.

----------------------------------------------------------------------
COMPONENT: 2. Crius VM, workspace, block store and control battery
PATHS: crius/{vm,artifacts,workspace,env,player,evaluate,gate_c1,c2_terminal,exploit_probe,parts_c2}.py
OWNER / DATES: Crius. 2026-09-18 (de2ea2fb2) to 2026-09-23 (7069c0ce6), 29 commits. The seat is CLOSED.
WHAT IT REALLY DOES:
- 8 registers holding ints (wrapped to +-2^20), int tuples or a FAIL object. Instruction = tuple (op,a,b,c). 53 opcodes (the dossier says about 49):
  - Base: CONST MOV ADD SUB MUL DIV MOD EQ LT NOT VGET VSET VLEN BRZ BRNZ JMP HALT INPUT ACT ACTI.
  - Workspace: WS_READ/WRITE/APPEND/SREAD/SLEN/REC_NEW/REC_GET/REC_SET/LINK/LINKS/LINK_GET/ALLOC/FREE/FIND.
  - Blocks: BLK_NEW/APPEND/PATCH/COPY/COMPOSE/DELETE/INVOKE/LEN/COUNT/STATE_GET/STATE_SET/REC_BEGIN/REC_END.
  - Typed: PSTEP PREC_BEGIN PREC_END PINVOKE PSIM PMATCH.
- Registers reset every task.
- The workspace (256 cells, 4,096 units) and the block store (32 blocks x 64 instructions, 8 state slots each) persist across a 50-task lifetime. The program is fixed for the lifetime.
- BLK_INVOKE runs a block in the caller's register file. It returns at block end or HALT, up to depth 4. The argument goes in R0 by convention; only PINVOKE passes one explicitly.
- Block handles come from a counter that never reuses ids.
SIZE: 6,881 Python lines. 41 test functions in 4 files.
DEMONSTRATED CORRECTNESS:
- Replay tests exist.
- The tests show the gate controls failing on the wrong organism.
- Seven designed programs of 19-64 instructions are available as plants.
- Defects:
  - The invocation log read R0 instead of the effective argument (fixed in a3f6a4be0).
  - Latent: BLK_APPEND takes the opcode mod 53 but leaves register fields unbounded, so invoking such a block raises an IndexError that nothing catches (vm.py:608-611; player.py:68-75; code-inferred, untested).
INTERFACE:
- The VM calls env.act/charge, and a task ends by a TaskOver exception.
- Deterministic and integer. Python random.Random with string keys.
- Workspace and BlockStore both have snapshot/restore.
- 1 unit per instruction, plus priced store ops, against a 40,000-step task budget. No rent.
- Module-global switches typed_procedures and psim.
THROUGHPUT / SCALE: A 300-iteration run (7,208 candidates) took 200 s to 1,805 s. The worker count is not recorded. Instructions/s not recorded.
COUPLING: Stdlib only and no outside importers. But vm.py imports the RELAY world, and receipts.py calls git.
FIT TO SLOT: WM.
- ORG-03: a,b,c,f,g yes; d and e partial; h has no rent.
- ORG-02, DEV-01 and DEV-02 are met at store level. evaluate.causal_controls forks from a mid-life snapshot into per-block ablation, transplant, code-only, compute-matched and storage-matched arms (DEV-05).
- Fails:
  - ORG-04 at rungs B-D (vm._calibrate).
  - ORG-05: plant of 64 against a cap of 96.
  - ORG-08 only partly met.
  - COMP-01.
MODIFICATION COST: L to make it the WM base: tags, rent, a total word encoding, world decoupling, a stepwise interface, switches, and a kernel that would effectively be rewritten. Extracting the battery and plants: M. Rebuilding from scratch: L.
VERIFIED BY ME: All of the above. The dossier's search results are not checked.

----------------------------------------------------------------------
COMPONENT: 3. D-5 register machine (RM-D5) and the Ergon E4 genotype library
PATHS: agent_d5_blind/substrate/{rm_vm,rm_fast,test_equivalence,test_smoke}.py; agent_d5_blind/mutation/physics.py; agent_d5_blind/learner/m1.py; ergon/gen1b/gen1_run.py
OWNER / DATES: Built by "Agent D-5", 2026-08-27 (7884e3e3c) to 2026-09-01 (8e7a6f505). Ergon used it to 2026-09-11.
WHAT IT REALLY DOES:
- A pure function from inputs to r0. 8 x 16-bit registers, at most 24 instructions (op,a,b), 512 steps.
- 14 ops: MOV SET(10-constant palette) ADD SUB MUL AND OR XOR SHL SHR MOD SKZ SKG JNZ(back 1-8).
- No memory, store, call or self-modification. Nothing survives between evaluations.
- The "library" belongs to the outer loop: up to 64 genotypes that supply half of the 10% immigrants in a GA of 32.
SIZE: 2,285 Python lines. 4 pytest functions plus the equivalence script. Ergon's test_persistence.py adds 22.
DEMONSTRATED CORRECTNESS:
- The Numba path matched the reference bit for bit on 2,402 programs x 128 inputs.
- Every fast-path solve is re-checked on the reference VM by assertion (m1.py).
- Replay reproduced 290/290 rows and 5/5 libraries.
- Defects:
  - The fast path loads 2 inputs, the reference up to 8 (code-inferred).
  - Five runner files put Windows backslash paths on sys.path.
INTERFACE: run(prog, inputs) returns (r0, steps). Integer. Mutation uses a caller-supplied random.Random. The VM does not check operands; validity comes from the mutation closure. No state, no cost beyond the step count.
THROUGHPUT / SCALE: About 38,000 evaluations/s, and 27.2 s per 42-task lineage (ergon/gen1a/REVIEW_PACKET_GEN1A_2026-09-01.txt:93,246-248). Instructions/s not recorded.
COUPLING: numpy and numba. Imported by ergon/gen0 to gen1b, evidence_wiki and techne.
FIT TO SLOT: WM. ORG-08 within the closure. The only compiled path in scope. Fails ORG-02, ORG-03 (b,d,e,g,h) and DEV-01.
MODIFICATION COST: XL to make it the WM base. Extracting the reference-plus-Numba-plus-equivalence pattern: S.
VERIFIED BY ME: All except the library's evidence numbers.

----------------------------------------------------------------------
COMPONENT: 4a. Nestor Z8 / NPE byte VM and pair-tape world
PATHS: roles/Nestor/campaigns/z80atlas-verify-2026-09-22/{z8,world,grammar,tasks,selftest_z8}.py; roles/Nestor/lib/reset_axis.py; roles/Nestor/campaigns/ancestry-replay-2026-09-28/tracer/
OWNER / DATES: Nestor. The frozen engine dates 2026-09-19 (aa5833488) to 2026-09-24 (ab94f5399); subclasses were used to 2026-09-30.
WHAT IT REALLY DOES:
- A variable-length (1-3 byte) VM over a shared arena. ISA:
  - LD r,r' (0x76 HALT); ALU ADD ADC SUB SBC AND XOR OR CP; INC/DEC r; LD r,n; LD BC/DE/HL,nn; LD via (BC)/(DE).
  - INC/DEC rr; JR plus 4 conditionals; JP plus 4 conditionals; immediate ALU ops; IN; OUT.
  - ED world ops ALLOC BIRTH SELF GETPC SENSE SPLIT LDIR LDDR.
- Undefined bytes are NOPs, so every byte decodes.
- Registers B C D E H L A and flags are carried or reset by a world axis.
- Genome and working memory are the same arena bytes. No call/return, no stack, no tags.
SIZE: 9,522 Python lines. selftest_z8.py has 22 checks. 11 script-style test files; 0 pytest functions.
DEMONSTRATED CORRECTNESS:
- A shadow tracer asserts per-interaction value and RNG-state identity (tracer/observe.py:119-126).
- Gates of 10/10 and 14/14 (dossier).
- W2-8 lists 15 engine defects (dossier).
INTERFACE: z8.run(ctx, pc, budget, ops_enabled). random.Random keyed by seed and cell. Copy errors draw floats; energy is a float (world.py:67,766,915). No snapshot/restore found. ops_enabled disables a world op as a same-length no-op (z8.py:160-166).
THROUGHPUT / SCALE: 52 s and 140 s per run (PREFREEZE_STOP_2026-09-24.md:121); 130-260 s per run (npe-arc3 BASELINE_DESIGN.md:133). Instructions/s not recorded.
COUPLING: Stdlib, script-style sibling imports, subclassed per experiment.
FIT TO SLOT: WM. ORG-03 a,c,f only. Fails ORG-08 (floats) and COMP-01. No genome/store split.
MODIFICATION COST: XL. Rebuilding from scratch: L.
VERIFIED BY ME: ISA, decoding, registers, RNG, energy, switch, tracer assertion, throughput lines.

----------------------------------------------------------------------
COMPONENT: 4b. Bellerophon BEE Z80-like soup (prometheus.z80atlas)
PATHS: prometheus/z80atlas/{vm,world,tasks,coupling}.py; prometheus/z80atlas/tests/
OWNER / DATES: Bellerophon. 2026-09-19 (98b2149a7) to 2026-09-30 (8a2390d82), 17 commits.
WHAT IT REALLY DOES:
- A 256-byte space per execution: own tape [0,L), partner window [L,2L), inputs at 0xE0.
- 50 defined byte values: NOP; LD A/B/C/D/S/T,n; LD via (S)/(T); LDI; LDIR; COPYALL; ADD/SUB/XOR/AND/OR A,B; ADD A,n; INC/DEC A and C; INC S/T; SHL/SHR; CP A,n and A,B; JP JZ JNZ JC JR DJNZ; IN; OUT; 10 register moves; SWAP; HALT.
- The other 206 values are NOPs.
- Registers start at zero unless the 09-30 reg_world axis is set. No call/return.
SIZE: 5,505 Python lines. 88 test functions in 7 files.
DEMONSTRATED CORRECTNESS:
- Golden v1 replay test.
- Cross-host replay of a real task: T-001 on ubu001 matched 74,800/74,800 rows (ops/campaigns/C-001/CAMPAIGN.md:23-27).
- Defect: LDIR with C=0 sweeps 256 bytes (vm.py:169-177). The 34-row v1 ledger is from the dossier.
INTERFACE: execute(mem, L, entry, budget, inputs) is a pure function. World RNG is random.Random. Float energy (world.py:720). Snapshots are telemetry; there is no restore. Switches: ldir on/off/cost4, undefined NOP/HALT, reg_world.
THROUGHPUT / SCALE: 63,247 runs over 592.2 CPU-h, median 25.5 s per run. 500/2000/5000 ticks take 59/641/3049 s. Instructions/s not recorded.
COUPLING: Stdlib. Used by archaeon/causal_lens, Artemis D004 and Bellerophon tools.
FIT TO SLOT: WM. Same as 4a, but with the best REPR-01 record.
MODIFICATION COST: XL. Rebuilding from scratch: L.
VERIFIED BY ME: VM, opcode count, energy, golden test, T-001, throughput.

----------------------------------------------------------------------
COMPONENT: 4c. Archaeon z80atlas byte VM and ecology engine
PATHS: archaeon/z80atlas/{vm,engine,grammar}.py; archaeon/tests/test_z80atlas_*.py
OWNER / DATES: Archaeon. 2026-09-19 (c7610ea19) to 2026-09-23 (863d34a55), 13 commits.
WHAT IT REALLY DOES:
- op = byte & 31, with a 2-bit register field and a direction bit, so every byte decodes.
- 32 slots: NOP LD r,imm, LD A,r/r,A ADD SUB INC DEC XOR AND OR SHL SHR CMP JP JR JZ JNZ JC, LD A,(r)/(r),A, LD (imm), COPY (when copy_prim), IN OUT HALT SWAP NEG, JP r, DJNZ, LD A,LEN, SEAL.
- Four registers are zeroed each execution. JP r is a computed jump with no return.
SIZE: 3,148 Python lines. 33 test functions in 4 files.
DEMONSTRATED CORRECTNESS: 5 positive controls PASS (campaign/STATUS.json). Byte-identical replays (dossier).
INTERFACE:
- execute(tape, nbr, inputs, step_cap, copy_prim, energy, pc0); it never raises on organism content.
- The energy is a float inside the VM loop (vm.py:27,40,48).
- RNG is SplitMix64 from proteus.
- exec_cost 0.004 per step and tape_cost 0.02 per byte per epoch (grammar.py:35).
THROUGHPUT / SCALE: 101,003 runs in 71.63 h on 24 worker processes. Replays took 69.6-440.3 s.
COUPLING: Imports proteus.foundry.prng. Imported by archaeon envgate, attribution and causal_lens.
FIT TO SLOT: WM. As 4a. It does have the only per-step cost plus per-byte rent in scope, but in floats.
MODIFICATION COST: XL. Rebuilding from scratch: L.
VERIFIED BY ME: VM, engine RNG, cost constants, status, tests.

----------------------------------------------------------------------
COMPONENT: 5. Apollo routing-DAG / blackboard evolvers; Lexis closure search
PATHS: apollo/src/{genome,blackboard,blackboard_evolve,blackboard_ops*}.py; roles/Lexis/instructions/
OWNER / DATES: Apollo 2026-03-27 to 2026-09-11. Lexis 2026-08-24 to 2026-09-11.
WHAT IT REALLY DOES:
- Apollo: a list of hand-written Python operators run over a per-task dataclass of strings, lists and floats ("Adding a slot is intentional, not emergent"). Mutation uses the global random module plus optional Granite LLM inserts.
- Lexis: a breadth-first closure over Apollo programs, applied jointly to 120 tasks.
SIZE: Apollo has 0 tests. Lexis instruments are 3,516 lines.
DEMONSTRATED CORRECTNESS: None checked.
INTERFACE: No ISA. Nothing persists across tasks. A model call sits inside mutation.
THROUGHPUT / SCALE: Not recorded.
COUPLING: Hephaestus forge primitives; Granite server.
FIT TO SLOT: Not an organism in WM's sense. Fails ORG-03 and ORG-08. Falls under ORG-13 (REJECTED).
MODIFICATION COST: N/A. Lexis's exact-closure idea costs S to reimplement.
VERIFIED BY ME: blackboard header, mutation paths, absence of tests (Lexis path is roles/Lexis/instruments/).

----------------------------------------------------------------------
COMPARISON

SLOT WM (base)
 1 Crius           only executable lifetime blocks + harness-owned stores; no tags/rent/speed
 2 Proteus v0      total integer words, checkpoint, shadow decoder; lacks every store/call op
 3 Proteus graph   call/return, no positions; no lifetime code, no args, no snapshot
 4 D-5             only compiled path pinned to a reference; no memory
 5 BEE/Nestor/Arch byte soups; no call, tags or store; float energy
 6 Apollo/Lexis    not organisms

SLOT P3 (knockout)
 1 Crius           rung flags + FRESH/RESET/SCRAMBLE/ablate/transplant/matched arms
 2 Nestor Z8       physics op mask, length-preserving no-op, register axis
 3 BEE             ldir/undefined/reg_world chemistry ablations
 4 Proteus v0      class knockout to NOP, code_writable, persist none
 5 Archaeon        copy_prim and neighbour-write only
 6 D-5             mutation-class ablation only

Facts that decide the choice:
- No component meets COMP-01. The only recorded instruction rate is 3.75e6/s (Proteus).
- No component has tag addressing.
- Only Crius has organism-written executable blocks. Its tuple/dict/FAIL values would not carry into a compiled kernel (code-inferred).
- Only Proteus v0 has a total word encoding with exact checkpoint.
- Only D-5 has a reference-checked compiled path.

----------------------------------------------------------------------
COULD NOT DETERMINE
- Instructions/s for every machine except Proteus v0. I searched with git grep for ops/s, evals/s, throughput, wall and elapsed.
- Crius worker counts (RUN_META.json has none).
- Whether the Crius IndexError path ever fired. Running it is forbidden.
- Whether NPE T-003 was compared bit for bit across hosts.
- No cross-host record exists for Crius or D-5 (git grep, as above).
- Not opened in full: Nestor, BEE and Archaeon world/engine files, Proteus grammar bodies, the Crius design docs. All result numbers are taken from the dossiers.

----------------------------------------------------------------------
SURPRISES
1. The D-5 code lives in agent_d5_blind/, not ergon/ as the scope says. Its runner files use Windows-only paths.
2. Crius already implements forked-clone treatments (evaluate.causal_controls). It has 53 opcodes, not about 49.
3. Crius has a latent totality hole and a structural block-id clock. Its typed rungs break ORG-04.
4. BEE's T-001 and T-002 replays off M2 are absent from the Bellerophon dossier.
5. Proteus's "cross-host" replay was three runtimes on one machine.
6. Proteus's speed is recorded only in Archaeon's journal. It is about 140x below the architect's 530M/s toy.
7. All three Z80 machines use float energy. Archaeon depends on Proteus's PRNG.
8. The Proteus graph organism has no restore function.
