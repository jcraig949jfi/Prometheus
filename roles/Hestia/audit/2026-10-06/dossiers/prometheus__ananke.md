# Dossier: prometheus/ananke (PTE, the Packet-Tensor Engine)

Audit group G3. Auditor: Hestia audit worker (read-only). Currency 2026-10-06.

VERDICT: SALVAGE_COMPONENT -- the substrate's evolved "mechanisms" are 1-bit relays and latches found by a plain GA over 16-line register programs that is measured to stall at the first two-stage composition (FLIP 0/290 unseeded searches), but the seat's causal instrument (exact mirror-pair carrier swaps) and its search-limit localization protocol (P/R/V admission + PSEED/BRK/B4X arms) are the best search-vs-physics discriminator in the fleet and should be carried forward.

## 0. Identity

- Code: prometheus/ananke/ (49 tracked files, 20 modules, 6130 lines of .py excluding tests).
- Seat: Ananke. Campaign artefacts: roles/Ananke/pte/ (C1, C1b, C2A, C2B, C2C), research arcs
  roles/Ananke/research/ (SYNTHESIS_2026-09-27, _ARC2, _ARC3, harvest/, harvest/wave2/).
- Census: research-engine (docs/fleet/fleet_state.json at 013e7ce5e, per AUDIT_PLAN s1).
- Tree read: worktree hestia-boot-2026-10-06 at 3fed30ac9; last commit touching
  prometheus/ananke or roles/Ananke = 5bcdb37fe.
- READ IN FULL: engine.py (594 lines), physics.py, search.py, envs.py, assays.py lines 1-120,
  plants.py lines 16-82, roles/Ananke/research/PTE_ENGINE_CARD.md, pte/C1_REPORT.md,
  pte/c2a/RESULT_PTE_C2A.md, pte/c2b/RESULT_PTE_C2B.md, pte/c2c/RESULT_C2BX_C2C.md,
  calibration/LEDGER.md, STATUS.md, research/SYNTHESIS_2026-09-28_ARC3.md lines 1-80,
  research/harvest/wave2/P-1/H6_ADVERSARIAL.md lines 1-60, H-PLANT hp_plants.p_flip.
- SPOT-CHECKED (rows): c1_report/summary.json (keys, A0/A1, cells_per_wave),
  REDUCE_C2A/C2B/C2C.json keys, REDUCE_C2C.json C2BX block, production/rows_C2C.jsonl.gz
  (152 rows; recounted B16X 16/32 and FLIP arms 0/32, 0/32, 0/28, 1/28 -- match the packet).
- NOT READ: c1b.py, c1b_run.py, campaign.py (932 lines), lens.py, lens_swap.py, swap_rel.py,
  oracle.py, report.py, analysis_a0.py, the 26 test files; PREREG texts for C1/C1b/C2A/C2B/C2C
  (only grepped); the C1b packet and CORRECTIONS; most of research/ (W-A..W-L handoffs,
  designed_echoes, the 2026-09-27 spikes log) and most of harvest/wave2. The c1_rows/cells.jsonl.gz
  6596 rows were not re-reduced; C1 numbers below are from summary.json + C1_REPORT.

## 1. Mechanism (what the code does)

1.1 World. B worlds x N sites; one homogeneous program runs at every site
(engine.py:331-337: with rules == 1 every site gets genome rule 0). State is int32 S[B,N,D],
saturating at +-32767 (physics.py:23). There is no organism, no individual, no reproduction
inside the world (PTE_ENGINE_CARD "ENTITY").

1.2 Tick (engine.py:268-472, normative order DESIGN.md s6):
- DELIVERY: the mailbox slot for tick t is summed into the inbox Acc_sum/Acc_cnt
  (engine.py:274-299). Packets SUPERPOSE: arrivals on a channel are added, with no source
  identity (engine.py:296). Receiver caps: aloha erases the slot over cap
  (engine.py:282-286), saturate rescales it (engine.py:287-293).
- ENVIRONMENT: a sparse sense schedule is scatter-added to sensor sites (engine.py:301-303).
  The environment is write-free: the world cannot mark it.
- RUN: a straight-line register program of L instructions, 16 opcodes (NOP MOV ADD SUB MULQ
  ADDI CONST GT SEL MAX SHR XOR MOD RAND SETRULE WIMM), every candidate result computed and
  gathered by opcode (engine.py:342-370). No loops, no branches except SEL/GT arithmetic, no
  calls. Register file = S (D) + 8 temps/outputs + P payload + C*P inbox sums + C counts +
  SENSE, ENERGY, ZERO (engine.py:311-319; plants.regmap).
- ECONOMY, ROUTING WRITE (plastic weights), EMISSION to F neighbours with loss, latency,
  jitter, duplication, noise (engine.py:385-412, _emit 483-549), optional per-site immediate
  mutation (414-420), DECAY S -= S >> k (444-445), READOUT of S0 at one actuator site (447).
- All randomness is a counter hash per named stream, never state-dependent (rng.py; the
  _emit draws at engine.py:490-491). Assay switches (Controls, engine.py:33-88) ablate exactly
  one channel and touch only their own stream.

1.3 Task. envs.py:34 FAMILIES = RELAY, XOR, MAJ, FLIP, HOLD. Every trial is a binary sign
target; S0 at the actuator is scored by sign, S0 == 0 scores 0.5 (envs.py:227-232). Worlds
come in mirror pairs whose targets are exact negations (envs.py:150-153, 190), so every
constant policy scores exactly 0.5. RELAY = carry a cue d hops; HOLD = keep a 1-bit cue
through distractors at one site; MAJ = majority of 5 noisy sensors; XOR = product of two
cues; FLIP = cue times a hidden mapping bit that the teacher reveals and that flips every
block of 4 trials (envs.py:176-182).

1.4 The search (the only thing that "learns"). search.py:81-149 is a truncation-selection
GA: pop 48 default (96 in C1/C2), 25% truncation, 4 elites, per-field resample p=0.04, one
whole-instruction resample p=0.15, a line swap p=0.10, uniform line crossover p=0.30
(search.py:61-79). Fitness = accuracy + 0.10*max(contrast,0) + 0.02*sens_any
(search.py:94), evaluated on M=8 fresh training worlds per generation; champion chosen on
training accuracy only (search.py:124), evaluated once on 64 held-out worlds plus a
zero-communication control (search.py:127-130). The GA is outside the world.

1.5 DOCUMENTED vs CODE. The engine card calls the receiver "a dial" and talks of channel
state, memory, configuration and code change; all of that is present in the code as
described. What the code does NOT contain: any learning rule inside the world (WIMM and
SETRULE are opcodes the program may call, engine.py:372-377; nothing rewards their use),
any modularity, any way to reuse a sub-program, any notion of an individual. "Mechanisms"
(M1 routed relay, M2 delay-line memory, M3 self-modifying MAJ) are labels for what a frozen
16-line program happens to do, inferred from ablation patterns.

## 2. Evidence (tiered)

OBSERVED (rows/reducer outputs on main, spot-checked as noted in s0):
- C1: 6596 rows, 0 failed cells; waves A0 5000, A 352 (48 budget-censored), B 786, B2 270,
  C 132, D 36, E 20 (summary.json cells_per_wave, censor_lines).
- C1 L3 competence by family across evolve cells (C1_REPORT.md:40-42, from summary.json):
  RELAY 50/196 SIGNAL, MAJ 19/162, HOLD 97/155, XOR 0/83, FLIP 0/82. COMM_DEPENDENT in A1:
  8/352 (2.3%) (C1_REPORT.md:108).
- Size-free RELAY laws: held 0.875-0.893 to N=2304 vs 0.500 zero-comm (C1_REPORT.md:17-20);
  every RELAY law collapses to 0.500 on a random graph (C1_REPORT.md:20-21); 0 cross-family
  transfer (summary.json C_transfer rows all TRANSFER_SUPPORT false).
- C2A (362 jobs): at 8 admitted cells (4 multi-hop RELAY, 4 FLIP) where a plant proves the
  task is representable and the ruler works, unseeded search succeeds 1/96 at the C1 budget
  (RELAY-mh 1/48, FLIP 0/48), yet seeded plants are retained 32/32 (RESULT_PTE_C2A.md:21-32).
  Admission funnel: of 200 RELAY-mh candidates 17 admitted, of 200 FLIP candidates 4
  admitted (RESULT_PTE_C2A.md:161-164).
- C2A post-hoc: 0/81 genuinely broken starts recovered; one field edit typically drops the
  plant straight to 0.500 (RESULT_PTE_C2A.md:94-111).
- C2B (248 jobs): RELAY-mh 6/32 new competent lineages at 4x generations, FLIP 0/32; FLIP
  copy/latch stepping stone 0/24 and the stone is an attractor (median acc .675, never B>.75)
  (RESULT_PTE_C2B.md:18-21, 69-71).
- C2BX/C2C (152 jobs): RELAY-mh cumulative 7/32 (4x) -> 10/32 (8x) -> 16/32 (16x),
  arrivals steady at about 0.75 new lineages per 36-generation block (RESULT_C2BX_C2C.md:18-46;
  REDUCE_C2C.json C2BX.pooled; rows recounted 16/32). FLIP under a block operator, a graded
  stone, or both: 0/32, 0/32, 0/28, 1/28 (recounted from rows).
- Unseeded random-start FLIP searches on record: C1 0/82 + C2A BASE/W0/M32 0/112 + C2B B4X
  0/32 + C2C OP0_BASE/OPB_BASE 0/64 = 0/290 (95% upper bound 1.0%, rule of three; scratch
  calculation, see 3a).

CLAIMED (prose, not re-derived here):
- M2 delay-line memory, M3 self-modifying MAJ, the carrier-trajectory taxonomy (W-I, 33
  specimens), "switching compresses, does not expand" (W-H, 5/5), "no nontrivial retention in
  evolved champions" (W-G), aggregation-gain account of receiver semantics (W-J)
  (SYNTHESIS_2026-09-28_ARC3.md:7-80). These rest on C1b/spike rows not re-reduced here.
- Wave-2 adversarial pass P-1 (H6_ADVERSARIAL.md): 36/83 XOR evolve rows are light-cone
  capped below .60; 150/196 RELAY evolve rows only demand one hop; all 19 MAJ SIGNALs are
  one-hop placements. If right, much of C1's "physics map" is a map of task construction.

DESIGNED (not run): the FLIP representation experiment (persistent mapping bit as
first-class state, an alternative teacher-to-mapping instruction, a larger program space)
(RESULT_C2BX_C2C.md:121-127); port-resolved arrival, TTL auto-forwarding, mixed-topology
evolution (C1_REPORT.md:158-159).

Seat's own negatives already on record (calibration/LEDGER.md:10-25): 15 rows, including
prereg causal rules that mislabelled two of the three most interesting mechanisms (row 16),
a census that read only payload component 0 and missed the code (row 23), and reset-drop
read as carriage (row 24). The seat is unusually self-correcting; that matters for trusting
the OBSERVED tier above.

## 3. Matrix

### 3a. Combinatorial explosion and reachability

Genome space (C2 spec: prog_len 16, rules 1, D=2, P=1, C=1; PREREG_PTE_C2A.md:46). Each line
has five byte fields, reduced at engine.py:132-137: op mod 16, dst mod NW=11, a mod NR=16,
field 3 used as b mod 16 and as shift bits (low 4 bits only), imm 256 values. Distinct
lines = 16*11*16*16*256 = 11,534,336 = 2^23.46. Genome = 2^375.4 distinct programs (raw
encoding 2^640). C1 default physics (L=12, D=4, P=2, C=2) gives 2^340.
(scratch: pte_space.py.)

Explored per search: pop 96 x 36 gens = 3456 genome evaluations at the C1 budget; 55,296 at
16x. Fraction of space visited at 16x: 2^-359.6. Single-field neighbourhood of one genome:
16*(15+10+15+15+255) = 4960 one-edit neighbours.

Where it is a desert, by measurement, not by counting:
- The one-edit neighbourhood of a working FLIP or RELAY-mh program is mostly lethal: k=1
  edits keep competence 12/32 (38%), k=2 3/32, k=4 0/32 (RESULT_PTE_C2A.md:133-135).
- P_FLIP uses all 16 of 16 lines (hp_plants.py:38-55). The only known FLIP solution in this
  genome has zero neutral slack; any growth in the solution needs a longer genome, which grows
  the space by 2^23.5 per line.
- FLIP random-start hit rate: 0/290 searches, upper bound ~1% per search. Even granting the
  bound, expected 1 success per ~100 searches of 3456 evals, i.e. >= 3.5e5 genome
  evaluations per FLIP discovery, and C2B shows 4x budget does not move it (0/32).
- RELAY-mh is a rarity barrier, not a wall: per-36-gen-block arrival ~0.75 per 32 searches
  (~2.3% per search-block), sustained to 576 gens. That is consistent with a needle found by
  drift, not a gradient.

What the hit rates imply. The landscape has two kinds of cells: "one-stage" competences
(relay a sign, latch a sign) that random search finds at the C1 budget (one-hop RELAY 8/8
in C2A control; HOLD 97/155 in C1), and "two-stage" competences (a stored bit that gates how
another bit is used: FLIP, XOR) at 0. The exponent is in the number of interacting lines that
must be simultaneously right, and the partial-credit gradient is nil: graded stones at B .6
are won by descendants that lose the partial function (RESULT_C2BX_C2C.md:88-98).

### 3b. Cosplay vs foundation

What does the work called "mechanism", "memory", "integration":
- In the world: a fixed, hand-specified integer physics (packet superposition, decay, loss)
  and a straight-line 16-opcode program. The "reasoning" a champion does is evaluate, once
  per tick, a fixed arithmetic expression of its registers and inbox. There is no state
  machine above that expression except what S and the inbox carry between ticks.
- In the outer loop: a textbook GA over a tiny operator set (field resample, line swap,
  line crossover; plus a mechanism-blind block move in C2C).
- In the analysis: the instruments (mirror-pair swaps, ablations, reach checks) do real
  causal work; they are the strongest part of the engine.

Is it cosplay? Mostly no, in the specific sense that the seat does not dress the results up:
C1_REPORT.md:19-23 and RESULT_C2BX_C2C.md:114-127 state the walls plainly. But the
substrate's demonstrated competence ceiling is concrete and low: every solved task is a
function of at most one stored bit and one transported sign (relay, latch, majority of 1-hop
neighbours). No evolved champion composes two learned sub-functions. Integration beyond one
sensor did not reproduce (M4: 0.789, replicates 0.636 and 0.520; C1_REPORT.md:80-82).

The ceiling stated concretely: within a 16-line program and a mutation/crossover GA at
<= 5.5e4 evaluations per search, PTE reaches "1 bit carried d hops" and "1 bit held at a
site". It does not reach "1 bit that changes how another bit is routed" (FLIP), nor "two
bits combined nonlinearly" (XOR). That is below a 2-input logic gate learned in context.

### 3c. Substrate bottlenecks

- Representation: a straight-line program with global register addressing; no subroutine,
  no loop, no module. Composition requires interleaving two computations in one 16-line
  register space with shared temps; the GA cannot copy a working sub-program into a free
  region (the C2C block operator is mechanism-blind and did not help: 0/32).
- State: D=2 int32 registers per site in C2; the only persistent stores are S, inbox, Kp,
  routing weights, rule pointer. ARC3 found the free decay-free rule register goes unused
  (W-H) and no trial-specific retention evolves (W-G) -- the substrate CAN retain (plants),
  evolution does not find it.
- Addressing: packets superpose with no source identity (engine.py:296). Good for counting
  and majority; destructive for anything that must keep two cues apart (XOR needs exact
  co-arrival plus an |x1+x2| threshold; C1_REPORT.md:119-123).
- Credit assignment: a single scalar accuracy over 8 training worlds (4 independent pairs)
  per generation, plus 0.12 max shaping. A partially working program at B ~.6 is not
  resolvable from noise at that sample size (RESULT_C2BX_C2C.md:96-98); M32 did not help
  from random starts. No intermediate reward for sub-functions exists.
- Homogeneity: one law runs at every site. Good for size-free transfer (N to 2304), bad for
  role differentiation; topology is effectively hard-coded into routing offsets (laws die on
  random graphs; W2 P-1 says this is hop count, not topology).
- I/O: one actuator S0, one sign per trial. The readout bandwidth is 1 bit per trial.

## 4. Deliverable

Discovery Approach. Fix an integer "physics" of lossy, delayed, superposing packets among
identical sites; evolve one homogeneous straight-line program by GA to solve binary sign
tasks that require moving or holding information; then use exact counterfactual
interventions (mirror-pair swaps, ablations) to locate where the information lives
(site, channel, timing). The physics of intelligence is approached as "where can
information reside and travel under constrained communication".

The Brick Walls.
1. Composition wall (FLIP/XOR): 0/290 unseeded FLIP searches, 0/83 XOR evolve cells; the
   only FLIP program known fills 16/16 lines. Search budget, shaping removal, 4x selector
   worlds, a copy/latch stone, a graded stone and a block operator all fail.
2. Needle landscape: one random field edit destroys a working program 62% of the time
   (k=1 retain 12/32), and broken starts recover 0/81 in C2A; RELAY-mh is found at only
   ~2.3% per search per 36-gen block even at 16x budget.
3. Search space vs budget: 2^375 programs vs <= 5.5e4 evaluations per search; any richer
   task needs more lines, each line multiplying the space by 2^23.5, with no reuse operator.
4. Construction confound: most of the C1 candidate space is inadmissible (17/200 RELAY-mh,
   4/200 FLIP admitted in C2A), and Wave-2 P-1 argues much of C1's map reflects env
   construction (light-cone caps, one-hop placements). Population-level C1 rates do not
   identify physics.

Seed Viability. The substrate-plus-GA is not a seed that scales: its walls are measured,
replicated and localized to the search/representation, and the seat's own next step is a
representation change. What survives:
- (a) The exact mirror-pair counterfactual instrument: deterministic, counter-hashed
  physics so that a twin differs only in the cue sign; carrier swaps give FLIP/NO-EFFECT/
  CHANCE without a noise floor. This would detect a real circuit's carrier if one arose.
- (b) The search-limit localization protocol: P (physics ceiling), R (plant passes the
  ruler), V (adversaries fail) admission; then BASE vs PSEED (retention) vs KSEED/BRK
  (recoverability) vs B4X (budget) vs STEP (stepping stone). It separates "unreachable",
  "unretainable", "unrepresentable" and "unmeasurable" cleanly. No other engine in this
  group has it.
- (c) The packet-superposition substrate itself is a reasonable test bed for channel-state
  questions, but it is not a cognitive architecture.

Evolutionary Roadmap (for the salvaged components, and the conditional path for PTE).
1. Representation refactor (the seat's own proposal, made concrete): replace the flat
   16-line program with a typed, compositional program -- a small typed lambda calculus or a
   graph-rewriting genome with named sub-graphs -- with duplication-and-divergence as a
   primary operator (gene duplication then mutate the copy), so that a working RELAY or
   latch sub-program can be copied and specialized rather than re-found. Measure with the
   existing protocol: the FLIP 2-stage composition must become reachable from the one-stage
   competences already found.
2. Credit assignment: add module-level credit (score sub-graphs by counterfactual swap
   contribution, which the instrument already computes) and use it to bias which sub-graph
   is duplicated -- a compositional credit assignment, not a scalar fitness.
3. Curriculum / open-endedness: task families as a ladder (RELAY -> HOLD -> gated RELAY ->
   FLIP -> XOR) with a library of frozen solved modules (an MDL-style library: keep modules
   that shorten later solutions; DreamCoder-style abstraction over the champion archive).
   Track an open-endedness metric (number of distinct reused modules over time).
4. Multi-agent: heterogeneous site laws (2-4 rule types placed by the world) rather than one
   homogeneous law, so specialization can carry a stored bit at one site while another routes.
   The engine already has rules > 1 and SETRULE; the step is to let the world assign them.
5. Statistics: adopt inference.py's studentized pair bootstrap for every SIGNAL call
   (the C1 percentile CI is anti-conservative, inference.py:1-12).

THE ONE decisive experiment. FLIP representation test at the 4 admitted FLIP cells with
frozen plants, rulers and held design: arm A = current genome + GA (control, known ~0/32);
arm B = same budget, genome extended with a first-class 1-bit mapping register plus a
duplication operator that copies a contiguous 4-8 line block into free lines and mutates the
copy; arm C = arm B seeded with a frozen one-hop relay module in the library (no FLIP
content). 32 searches per arm, C1 budget and 4x.
Kill criterion: if arm B and arm C each reach <= 1/32 FLIP-competent (B > .75 on held
worlds) at 4x budget, the compositional route through this substrate is dead and the PTE
line should stop at instrument status. Pass criterion: >= 6/32 in arm C with lineage
attribution to the duplicated module (the swap instrument shows the module carries the
mapping bit).

## 5. What would change this verdict

- Upward to VIABLE_SEED: the decisive experiment passes (>= 6/32 with module attribution),
  i.e. a two-stage composition becomes reachable once the representation supports reuse.
- Downward to DEAD_END for the instrument: an independent reviewer shows the mirror-pair swap
  verdicts are artefacts of mirror-pair identities (cf. the retracted "site_acc + chan_acc = 1"
  identity, ARC3:23-24) in more than a few specimens, or that P/R/V admission leaks
  (plants tuned to the held design).
- Unread modules (campaign.py, lens_swap.py, swap_rel.py) could contain a defect that
  invalidates the swap instrument; I did not read them, so the instrument endorsement rests
  on the seat's tests, its ledger and its external-review pending status (C2B external review
  was still pending, RESULT_PTE_C2B.md:10-12).
