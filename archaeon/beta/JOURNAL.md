# Archaeon Phase 2-B SFE Beta campaign -- running journal

Directive: roles/Archaeon/prompts/2026-10-06_p2b_sfe_autonomous/ (operator, 2026-10-06, verbatim + MANIFEST).
Branch archaeon/p2b-sfe-2026-10-06; worktree D:\Prometheus-worktrees\archaeon-p2b-defects-2026-10-04 (M2 SPECTREX5).
Format per entry: tried -> happened -> changed my mind -> signal worth following -> killed -> next.
Side records (do not gate science): E-003 BEE verdict of record is preserved as it stands, unresolved (operator, #1044).

## Live hypotheses / branches

| id | question | state |
|---|---|---|
| B01 | W2_K2 ceiling: organism limit or search limit? | ORGANISM NOT THE LIMIT; D failed prediction -> B01b running |
| B02 | shelf -> summit edit path: valley or neutral plateau? | SILENT PLATEAU (done) |
| B01b | one edit from summit: rescued? waiting-time model? | 6/12, all by gen 10 (early-or-never) |
| B04 | H-EROSION (drift erases near-solvers)? | KILLED (1/6 eroded; replay exact) |
| B05 | summits: SLOT2 or GENERAL keyed memory? | instrument ready (controls pass); waits on B03 |
| B03 | BASE vs HEAVY vs RELOC search at equal compute | CLEAN NULL 0/24 each |
| B07 | withdrawn positional scaffold -> content-addressed recall? | NULL 0/36 (cue dispatch itself unreachable) |
| B08 | which primitive is the wall? (ladder) | L4 claim RETRACTED: evolved solvers are delay lines (B08b) |
| B08J | ladder with timing jitter (repaired instrument) | COMPOSITION WALL: 1 value yes, 2 values 0/8 |
| B13 | queue primitive (PUSH/POPF): does the 2-value wall move? | queue arm 0/8 (stock = B08J 0/8): NO |
| B14 | stepping stone: guard organism -> two stored values? | staged; queued for budget |
| B15 | why does L2 force genuine state? | ANALYSIS: wall = conditional write ROUTING to 2 locations (hypothesis) |
| B16 | how do genuine shelves store one value? | 56% LATCH (stop perceiving); 36% continuous perceivers |
| B14' | L4 seeded from perceiving vs latching shelves | NULL 0/5 + 0/5 |
| B18 | graph organisms on the ladder (first world run) | NULL + WORSE: L1 1/4, rest 0/4 (control 1.000) |
| B19 | gen-0 config (tape 4096 + persist tape) as hidden gate? | NO: BIG 0/4 |
| B20 | indexed solver neighbourhood | ISOLATED PEAK (shelf-level .0015) |
| B21 | operand-locality mutation | NULL 0/8 (.82 cell = lag-window exploit) |
| B08K | 0-7 jitter re-score of B08J | L1 7/7, L2 5/5, L3 6/8 genuine; standard now 0-7 |
| B22 | credit the write half, then withdraw | write learned 2/8, lost on withdrawal; recall 0/16 |
| B22b | hold store credit at .2 after g150 | running |
| B23 | re-audit Deep Frontier/C6 elites with jitter/constant-twin/disasm | staged (budget window) |
| B17 | forced perception (echo on PUT) opens the 2-value wall? | staged; controls pass |
| B12 | LONG: W2_K2 with N=500, G=3000 -- is it just time? | STOPPED (compute repair); partial 0/6 to g200-2999 |
| B11 | is the W2_K2 shelf a delay line? | MOSTLY NO: 50/72 genuine memory, 20/72 delay lines |
| B09 | dispatch wall: READ the cue vs SELECT on it | CLEAN NULL 0/24 |
| B10 | SEL opcode (branch-free mux): does the wall move? | CLEAN NULL 0/32 |

## 2026-10-06/07 EXP-1 (opened 2026-10-06T23:48Z)

- Orientation. SFE engine eng_906356f7 is DOWN since 09-25 (watchdog task disabled under the 09-25 hold; ledger
  C:\Prometheus-data\sfe\engine.db intact). The experiments never ran inside the engine: it is the citable ledger.
  Science lanes are archaeon/wse + campaigns 1-6 + frontier (Proteus VM organisms) and z80atlas (byte VM).
  Forensic dossier docs/phase3/intake/sisyphus/seats/Archaeon.md s5: "the ceiling is not shown to be an organism
  limit vs a search limit (both unchanged together)". Cheapest discriminator chosen: B01.
- B01-A (2026-10-07): a hand-written 20-instruction program (two register slots, persist=all) scores held-out
  1.000 on W2_K2 (5/5 seeds, episode mode 1.000). Hand-written one-slot "shelf" program: .51-.56.
  -> CHANGED MY MIND: the organism is NOT the limit. The 0/60 summit record is a search/selection fact.
- B01-B: 2,000 single-op children of the solver: neutral (>=.90) 33.5%, mid 14.7%, shelf 7.7%, below .45 44.1%.
  Prediction (.30-.70 neutral) held. The solver sits on a narrow ridge: nearly half its neighbours are near-lethal.
- B01-D: GA (CMP3 config) seeded with 4 k-damaged solver copies: re-summit 1/3 cells at k=1, 0/3 at k=2,4,8,16.
  PREDICTION FAILED (I said >= 5/6 at k=1-2). Instrument defect in my design: the 4 k=1 copies were 3 lethal +
  1 shelf-level child, so each cell started from ONE plateau organism. Repaired as B01b (condition on plateau
  neighbours by score, measure each one's reversal rate, test a waiting-time model).
- B02: explicit edit chain shelf -> summit (7 programs): every intermediate scores EXACTLY the shelf (.5396 mean
  over 5x48 held-out) and the last edit jumps to 1.000 -- a second, 16-instruction solver. Valley: NO. Plateau: YES.
  The intermediates are behaviourally silent (dead/unused code), so behaviour-based search (novelty, QD,
  per-ask descriptors) is predicted to be as blind as fitness here. Instrument caveat: some chain steps are 2
  grammar edits (an insertion also shifts a jump offset), so the measured proposal rates (0 or 2.5e-4 per 20k)
  overstate per-edit difficulty; the plateau result itself does not depend on this.
- SIGNAL WORTH FOLLOWING: the W2_K2 wall is a silent-plateau needle, and even one edit from the summit the GA
  mostly does not return. Hypothesis H-PLATEAU: summit waiting time = reversal rate x plateau-lineage share x N.
- B01b: 12 plateau neighbours of the solver (held-out .50-.57, one edit away), one GA cell each: 6/12 re-summit,
  ALL by generation 10 (gens 1,3,3,5,7,10); none later in 60. Reversal rates 0 - .0134 per child.
  Spearman(r, summit) = .44 (predicted > .5: PARTIAL, right direction). Early-or-never is the shape worth keeping:
  H-EROSION -- the plateau lineage takes over fast (random gen 0 scores ~0) and then neutral drift erodes the
  near-solver structure, closing the reversal window within ~10 generations. Testable: track the plateau
  population's mean edit distance to the solver per generation.
- DEV finding while building B03: grammar v0.4's length-changing operators never fix up relative jump offsets.
  Neutral share on the solver (B01-B by operator): insertion .223, duplication .152, deletion .009, movement .080,
  splice .070, region_swap .031. The same edits with jump fix-up (archaeon/beta/b03_search_arms.py reloc_child):
  insertion .70, duplication .47, deletion .26 (400-child self-test). Structured code is fragile to growth under
  this grammar for a reason that is about EDIT SEMANTICS, not about the organism or the world.
- B04 (H-EROSION test): deterministic replay of the 12 B01b cells reproduces every summit generation EXACTLY.
  H-EROSION KILLED as the general explanation. Of the 6 unrescued cells: 4 started at instruction-Levenshtein
  distance 2-4 from the solver (a single grammar op -- movement, region_swap, deletion -- is several instruction
  edits, so "one op away" != "one instruction away": my distance ruler did not measure the grammar's metric);
  cell 10 kept 4-8 organisms at distance 1 for all 16 tracked generations and still never summited (waiting time,
  not erosion); only cell 9 eroded (distance-1 count 8 -> 0 at gen 6). Rescued cells 7 and 8 started at distance
  3-4 and returned in 1-3 generations by reversing the SAME op type (movement undoes movement).
  -> What survives: summit = rare reversal (r ~ 1e-3 per child) x few near copies; not drift.
- B05 instrument: hand-written GENERAL control (tag/value table on the tape, linear search) scores 1.000 on K=3/K=4;
  first version scored 0 because I placed the table inside the 112-word read-only code region (writes silently
  dropped) -- caught by the control, fixed (table at 160, tape 256). Hand solvers label SLOT2 (K3 .69, K4 .54).
- B03 CLEAN NULL: 0/24 summits in EACH arm (BASE, HEAVY heavy-tailed edit count, RELOC jump fix-up), N=200,
  G=300, fresh CMP3 gen 0. Predictions BASE<=1, HEAVY<=3 held; RELOC>=3 FAILED. -> jump fix-up is NOT the binding
  constraint; neither is edit count. KILLED: "W2_K2 is limited by variation semantics".
  Side hypothesis (raised mid-run, mine) that the arms never left generation 0 -- KILLED by b03_readout.py: 0/72
  final elites are in gen 0; train best .098 at gen 0 -> ~.69 max; last improvement median gen 134-189. Matching
  held-out values across arms are the coarse grid of 96 asks, not identity.
  Instrument note: max TRAIN best ~.69 vs held-out ~.52 -> E=16 selection rewards episode luck (+.17).
- Pivot (world, not search): B07 environmental SCAFFOLD -- a positional hint word on every ASK, withdrawn over
  generations 100-300. Controls pass: hand hint-dispatcher 1.000/.812/.531 at p=1/.5/0 (plain .573); tag solver
  1.000 everywhere. Launched 3 arms x 12 seeds x G=400 (SCAFFOLD / BASE random third word / ALWAYS).
- B07 partial (~01:00Z): even ALWAYS (permanent exact hint) never reached train >= .90 -> the wall precedes
  content addressing. Pivoted to locating it.
- B08 PRIMITIVE LADDER (same W2_K2 inputs, demand changed; CMP3 search, G=200, 8 seeds; controls pass):
  L1 one value 7/8 | L3 last (shelf) 8/8 | L2 write-once guard 5/8 | L4 TWO SLOTS, fixed ask order 4/8 (gens
  105-129) | L5 two slots + exact positional cue 0/8 | L6 W2_K2 0/8.
  PREDICTION FAILED on L4 (I said <= 1/8): the SECOND SLOT IS REACHABLE. CHANGED MY MIND: the wall is between L4
  and L5 = answering from one of two stored values according to a DATA cue (fixed order needs no selection).
  STRONGEST SIGNAL SO FAR: in this VM+GA, data-dependent selection is the unreachable primitive, while storage,
  guards and a two-slot queue are reachable.
- B09 launched: READ vs SELECT (cue as 3rd word / 2nd word / folded into the kind code). Controls diagonal.
- B07 FINAL: 0/36 reach train >= .90 in ANY arm (SCAFFOLD, BASE, ALWAYS; G=400). Max train .53-.88. Independent
  replication of B08 L5 0/8. KILLED for this VM: "a withdrawn positional scaffold makes recall reachable" -- the
  scaffold's own task (cue dispatch) is the unreachable step, so there is nothing to withdraw from.
- DEV -> B10 (organism change): SEL opcode (op 24, was RND): regs[a] = regs[a] ? regs[b] : regs[c]. Variant VM
  built from proteus/foundry/vm.py's own source with ONLY the op-24 branch replaced (assert count == 1). Controls:
  branch programs score identically on both VMs (L5 1.0/L6 .5729 dispatcher; solver 1.0/1.0); SEL programs
  1.0 on the SEL VM and 0.0 on stock. Launched {stock, sel} x {L5_hint3, L6_w2k2} x 8 seeds, G=200.
- NEW INSTRUMENT archaeon/beta/disasm.py: disassembler + execution trace (tracing copy of the stock VM, one added
  line). Evolved L4 solvers read as DELAY LINES (seed 807: OUT r8; MOV r8,r7; IN r7 -- answer = input 2 ticks ago).
- B08b (timing-jitter check, 0-3 NOISE ticks before each ask): evolved solvers collapse -- L1 7/7 -> .27, L3 8/8 ->
  .27-.38, L4 4/4 -> .19; L2 4/5 SURVIVE (.83-.94) = genuine write-once state; hand slot solver 1.0 everywhere.
  RETRACTION (mine, B08 entry above): "the second slot is reachable (L4 4/8)" is WITHDRAWN -- what was reached is a
  timing shortcut. B08 numbers stand as measured; their meaning was "is there a delay-line solution".
  CHANGED MY MIND, program-level: the GA's default solution is to exploit fixed episode timing; it builds stored
  state only when timing cannot answer (L2). Likely re-read of CMP1-3: the W2_K2 "shelf" (.5, "remembers one value")
  may be a delay line that stores NOTHING, which would make the shelf->summit plateau a non-path by construction.
  To verify on the historical shelf elites (C2-SFE-05 archives) -- queued as B11.
- B11 (72 B03 final elites = the current W2_K2 shelf, plain vs jitter): BIMODAL -- 50/72 robust genuine one-slot
  memory (jitter .55-.57), 20/72 delay lines (-> .05-.18), 2 partial. PREDICTION (>= 90% delay lines) FAILED.
  KILLED (mine, raised one entry above): "the W2_K2 shelf is a delay line that stores nothing". The shelf is mostly
  real stored state; the B02 silent plateau stands as a real feature. Kept: ~28% of shelf organisms are timing
  exploits, so any shelf-based seeding/import experiment (CMP2/CMP3 shelf arms) mixed two mechanisms unknowingly.
- B10 CLEAN NULL: 0/8 in each of {sel, stock} x {L5_hint3, L6_w2k2} (G=200). Max train .53-.75 (sel) vs .25-.88
  (stock). Op-24 instructions in elites: similar counts on both VMs (on stock op 24 is RND) -> no adoption signal.
  PREDICTION (SEL L5 >= 3/8) FAILED. KILLED: "selection is unreachable because it needs an aimed conditional jump".
  CHANGED MY MIND: the barrier sits BELOW selection. Every L5/L6 solver needs two values stored as state, and B08's
  only two-slot solvers were delay lines (B08b). So the candidate wall is now: a SECOND GENUINELY STORED VALUE.
  B08J (jittered ladder, L4 rung) is the direct test -- launched ~02:00Z, 20 workers, G=300.
- B09 CLEAN NULL: 0/8 for the cue as 3rd word, 2nd word, or folded into the kind code (G=200). Max train .59-.94
  (hint3), .22-.63 (hint2: two seeds collapse to .22 -- the cue takes the word position the shelf reads its tag
  from), .59-.81 (kind). Neither READ nor SELECT is the specific barrier: consistent with B10, the wall is below.
- B08J FINAL (jittered ladder, G=300, 8 seeds): L1 7/8, L3 8/8, L2 5/8, L4 0/8 (max held-out .65), L5 0/8, L6 0/8.
  STRONGEST CURRENT FINDING: with timing shortcuts removed, ONE genuinely stored value and a write-once guard are
  reachable; TWO stored values are not -- even in fixed ask order. The pieces (guard: L2; overwrite-store: L3) are
  each reachable; their composition ("store here unless full, else there") is not. Call it the COMPOSITION WALL.
- B13 (organism lane): queue VM -- PUSH (op 24, was RND) / POPF (op 2, was YIELD) on a tape-resident FIFO, head/tail
  in the last two tape words; two branches replaced in the stock VM source (asserted). Control bug caught and fixed:
  my first queue program popped on NOISE ticks (0.32); with a kind==2 check it scores L4 1.000 / L6 .5625 on the
  queue VM and ~0 on stock; slot solver 1.0/1.0 on both. Launched {queue, stock} x {L4, L6} jittered, 8 seeds, G=300.
- 2026-10-07 ~04:15Z PROCESS DEFECT (mine; calibration ledger row 2026-10-07): B03..B13 ran with 15-26 workers
  UNLEASED on shared M2 (~90+ core-h in ~4 h vs MWO-0004 R2's 48 core-h/seat/24 h), crowding another session's
  job. Repair: lease spectrex5:cpu12 lse-bda13648061d for in-flight B13; B12 STOPPED; all later launches <= 12 procs.
- B12 PARTIAL (stopped at the overrun repair, not by its own rule): 6 seeds, N=500, generations reached 200-2999
  (seed 1203 ran to G=3000): 0/6 summits. Elites: 4/6 genuine one-slot memory (held-out .53-.54 = jitter), 2/6 delay
  lines (seed 1202 g2000: .53 -> .20 jitter; seed 1203 g2999: .52 -> .16). Genomes grew to 26-177 instructions.
  Prediction (0/6) held where measured. 10x the generations and 2.5x the population do not cross the wall.
- B13 run 1 INSTRUMENT FAILURE (mine): queue VM indexed past the tape when the genome sits within 2 words of the tape
  end (n - glen - 2 <= 0) -> IndexError in one cell; the harness raised on the first failed future and ALL 32 cells'
  results were lost (~80 min x 20 procs). Repairs: PUSH no-op / POPF reads 0 without a queue region; fuzz() runs
  6,000 gen-0 evaluations incl. tape==genome before every run (passes); per-cell JSONL written as cells finish, a
  crashed cell is a recorded row; default workers 12. Controls unchanged. Lease lse-bda13648061d RELEASED.
  Rerun QUEUED: this seat is over the 48 core-h/24 h envelope until ~2026-10-08 00:00Z (or an operator raise).
- B15 (analysis, no compute): the tick structures settle "why L2 forces state". A k-tick delay line is k registers
  shifted UNCONDITIONALLY each tick. L1/L3 need k=1 (one register), L4 needs k=2 (two registers) -- and the GA built
  exactly that 2-register shift (B08b). L2 is solvable by a 2-tick delay line too, yet 4/5 evolved solvers chose a
  CONDITIONAL write instead (write-once guard). So two-register state IS reachable when it is unconditional, and one
  conditional write IS reachable. REFINED WALL (hypothesis, mine): conditional ROUTING of writes to two different
  locations. Prediction it makes for B13: a queue (write location advances by itself; no routing) dissolves the
  L4 wall; and a "slot select by counter" world would stay walled. Campaign update 1 committed (2dbbb5c8b).
- B13 queue arm (light rule: <= 2 procs, stock arm = B08J L4 0/8): seeds 1301-1303, 1305, 1306 -> 0/5 solved so
  far. WEAK SIGNAL: seed 1303 train .94 / held-out .79 (above any stock L4: B08J max .65), elite 5 PUSH / 1 POPF.
  Instrumented before naming (disasm with the queue patch, executed code only): a 32-instruction STRAIGHT-LINE
  program, every instruction executed every tick, no branch taken; pushes every tick (NOISE included) and pops on a
  cadence. Per-lag profile (k1, k2 NOISE ticks before ask 1, 2): 1.0 on 10/16 combinations, .55 on 5, .12 at (3,3).
  -> a LAG-STRUCTURED TIMING EXPLOIT: the queue supplies a menu of lags covering most of the 0-3 jitter range.
  Not keyed memory; not a summit. RULER LESSON: 0-3 jitter is beatable by queue-shaped lags; memory claims on any
  queue-capable VM need jitter >= 0-7 or a per-lag profile. disasm.executed() now takes a VM patch.
- B13 queue arm 0/7 so far (1304 pending). Reason I now see (mine): a queue solver still needs a three-way dispatch on
  tick KIND (push on PUT, pop on ASK, neither on NOISE); the queue removes write-location routing, not dispatch.
- B16 NEW MECHANISM CLASS -- MEMORY BY SENSORY SHUTDOWN. Disassembly of genuine (jitter-robust) shelf organisms:
  B03_BASE_302 reads input on tick 0 only, then loops emitting the first value forever; _301 sits in a 2-instruction
  busy loop. Measured over all 50 genuine shelf organisms (share of later ticks executing any IN): 19 strict latches
  (0%), 9 near-latches (8%), 4 intermittent (33-40%), 18 continuous perceivers (100%); delay lines and the hand shelf
  perceive 100%. Prediction (>= 70% latches) FAILED at the strict cut (38%; 56% incl. near-latch).
  Reading: the GA's majority route to "one stored value" is to STOP PERCEIVING. A latched organism cannot store a
  second value by construction -- so for those, the composition wall is closed from the start.
  B14 re-scoped: seed L4/W2_K2 from PERCEIVING shelves vs LATCHED shelves (predict only perceivers can extend).
- B13 queue arm FINAL (jittered L4, 8 seeds): 0/8. PREDICTION (>= 5/8) FAILED. The one high cell (1303, .79) is the
  lag exploit above. KILLED (mine, B15): "the wall is write-location routing" -- removing routing with an
  auto-advancing store does not open L4. What a queue solver still needs is a 3-way dispatch on tick kind.
- B17 staged (world lane): ECHO on every PUT tick forces perception, closing the latch route (B16). Controls: slot
  solver / shelf recall 1.0 / .5729 with echo 0 (they never echo); echo+slot control recall 1.0, echo 1.0 on L4E and
  L6E. Queued for the budget window.
- B14' (L4 jittered, seeded from W2_K2 shelves): FROM_PERCEIVER 0/5 (final .53-.61), FROM_LATCH 0/5 (.50-.56).
  PREDICTION (perceiver > latch) FAILED. KILLED: "latching is the binding cause". Latching is real (B16) but organisms
  that keep perceiving do not extend to a second value either. B17 (forced perception) is DEMOTED: B14' already
  shows perception alone does not open the wall; keep it only as a cheap confirmation if budget is idle.
- PIVOT DECISION (2026-10-07 ~06:30Z). The composition wall is robust to: organism (B01), plateau shape (B02), drift
  (B04), edit semantics/count (B03), time+population (B12 partial), scaffold (B07), cue format (B09), branch-free
  selection (B10), queue memory (B13), seeding from guards/stores/perceivers/latches (B14'). Every reachable
  mechanism is a SINGLE module: one latch, one store, one guard, one shift chain. The untested lever the directive
  names is ARCHITECTURE: organisms built from separately evolvable modules whose outputs are combined (Proteus has
  a graph organism with callable modules, PROTEUS-43/47). Next branch B18: is the wall a property of monolithic
  programs? Two-module organisms (each module a Proteus program with its own registers, same input; the organism's
  answer = module selected by a tiny third program, or by ask count) on jittered L4 and W2_K2.
  First step (light, now): read proteus graph_organism to see whether it already provides this before building one.
- CORRECTION (mine, 2026-10-07 ~07:00Z). Reading Proteus's graph keyed-memory witness (state[key] = value) led to a
  hand-written 11-instruction v0 program: IN kind; IN tag; PUT -> IN v; ST [tag], v | ASK -> LD [tag]; OUT. Held-out:
  jittered L4 1.000, jittered W2_K2 1.000, K3 1.000, K4 .995, K6 1.000 (tape 4096, persist tape); tape 256 gives
  .73-.92 (tags fall in the read-only code region). So GENERAL keyed memory needs NO loop, NO slots, NO composition.
  WITHDRAWN: (a) B05's premise that GENERAL requires a table-plus-loop; (b) the name "composition wall" as the
  explanation (the GA also misses a short NON-composed solver). What every unreached solver shares is a COUPLED
  WRITE/READ PAIR whose halves are each silent (ST[tag] without LD[tag] scores nothing, and vice versa) -- B02's
  silent plateau, now with ~3 edits instead of ~5. Hidden-gate candidate: gen 0 (FOUNDRY_C2) draws tape_words
  16..256 and persist uniformly; the indexed solver wants 4096 + tape persistence. -> B19 (light, 2 procs) launched.
- B18 (graph organism) PAUSED: the Proteus graph witness uses a two-channel probe and scores 0 on every WSE rung,
  so there is no graph positive control in the WSE format yet; Evolution._shares also needs a graph-tolerant
  replacement. A null without a positive control would be uninterpretable.
- B20 (light): 2,000 single-op children of the 11-instruction indexed solver (jittered W2_K2): neutral .350,
  below .45 .649, shelf-level .0015 (slot solver B01-B: neutral .335, shelf .077). Prediction (neutral lower) FAILED;
  the informative number is the SHELF share: the indexed solver is an ISOLATED PEAK -- breaking its write/read pair
  sends it to ~0, not to the one-value shelf, so there is no partial-credit path into it from below.
- B19 (jittered W2_K2, G=300, light): BIG (gen-0 tape 4096, persist tape/all) 0/4; C2 0/4. PREDICTION
  (BIG >= 1/4) FAILED. KILLED: "gen-0 configuration is the hidden gate". Side observation: every BIG cell started
  with tape/all persistence and 3/4 elites drifted to regs or none -- selection moves the population toward
  register-based one-value memory and away from the persistence the indexed solver needs.
  Working explanation now: the indexed solver is an ISOLATED PEAK (B20) behind a coupled write/read pair; nothing
  in the search finds it from the shelf or from scratch at these budgets.
- B18 FIRST WORLD RUN OF THE PROTEUS GRAPH ORGANISM (jittered ladder, graph_grammar.v1 via handover, G=300, 4 seeds,
  ~0.8 core-h). Positive control (12-node WSE indexed store, mine) 1.000 on every rung. Evolved: L1 1/4 (gen 215,
  55 nodes), L3 0/4, L2 0/4, L4 0/4, L6 0/4; most cells never leave chance (train .19-.31, held-out ~.06).
  PREDICTION (L1/L3 >= 2/4 each) FAILED. Graph organisms under this search are much WORSE than flat v0 (B08J: L1
  7/8, L3 8/8): they do not even reach the one-value shelf. Consistent with PROTEUS-46 CLIFF_SURVIVES. KILLED for
  now: "the wall is a property of flat, positional programs" -- the graph architecture does not open it and makes the
  climb harder. Open DEV question (not pursued): why graph gen 0 rarely produces output-bearing paths.
- B21 (operand-locality mutation, light): FINAL 0/8 (L4 0/4, L6 0/4); prediction (>= 1/4) FAILED. WEAK SIGNAL L4 seed 2102 held-out .82
  (highest stock-VM L4; B08J max .65). Deterministic replay reproduces .8229 exactly. Instrumented: per-lag profile
  1.0 whenever the first ask comes within 0-2 extra ticks, .55 for every k1 >= 3 -> a LAG-WINDOW TIMING EXPLOIT
  (58 instr, XOR-mixing chain, no tag-addressed store). Not memory.
- B08K RULER REPAIR (second lag exploit beating 0-3 jitter): re-scored every B08J solved elite under 0-7 jitter.
  L1 7/7 genuine, L2 5/5 genuine, L3 6/8 (two at .86 = partial lag exploits). Hand slot + indexed solvers .97-1.0.
  B08J's single-value claims STAND (L3 revised 8 -> 6); L4 0/8 unaffected. STANDARD FROM NOW: memory claims use
  0-7 jitter (archaeon/beta/b08k_wide_jitter_rescore.py wide()).
- B22 STORE-CREDIT SCAFFOLD (partial, 9/16 cells): STRONG SIGNAL -- the tag-addressed WRITE half is learnable once it
  earns credit: STORE L6 2201 store-credit .08 (g50) -> .48 (g75) -> .99 (g100-150); STORE L4 2203 .91 at g125.
  2/4 STORE cells so far. During the scaffold the population TRADES AWAY recall (perfect storers at chance recall).
  After withdrawal (g >= 150) the write is LOST within 25 generations and the population returns to the shelf before
  any matching read appears. CHANGED MY MIND: the isolated peak is not one obstacle but two -- the write is
  reachable with credit; holding it long enough for the read is the obstacle. B22b launched: KEEP arm holds store
  credit at .2 after g150 (G=400, 8 cells, 2 procs).
- B22 FINAL: recall solved 0/4 in every arm (STORE/NONE x L4/L6). Write half learned (max store-credit >= .9) in
  2/8 STORE cells (L6 2201 .99, L4 2203 .91); the other 6 STORE cells never exceed .11. Both learners lost the write
  after withdrawal. PREDICTION (store >= .9 in >= 3/4 per world; recall >= 1/4) FAILED on both counts. Weak but
  real: under credit the write is reachable in ~1/4 of runs within 150 generations.
- PIVOT LANE staged (B23, for the budget window): re-audit the Deep Frontier / C6 record with today's instruments.
  Off-repo evidence exists: D:\Prometheus-worktreesrchaeon-wse-2026-09-16rchaeonrontieruns (2.3 GB;
  16 pursuits incl. C6-blind/-novel5/-unable/-volume, C4-cliff, C5-flat, P-boom, W-artifacts). Question: do the
  frontier's elites and detector firings survive the timing-jitter ruler, constant twins and executed-code
  disassembly? (Phase 2-B posture: no old positive presumed valid.) Read-only on that worktree.
- B08J built (ladder with jitter in train AND held-out); controls unchanged under jitter. Launches when cores free.
- Next: B01b (done) tests H-PLATEAU quantitatively; then B03 = search arms at equal compute from fresh gen 0
  (baseline / heavy-tailed mutation count / behaviour-novelty) -- prediction: only structural-move arms lift 0/60.
