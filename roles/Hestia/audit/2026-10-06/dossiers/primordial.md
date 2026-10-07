# Hestia audit 1 -- dossier: primordial (Nestor Primordial Engine, NPE)

VERDICT: SALVAGE_COMPONENT -- the "tensor brain" swarm is a dead end as a reasoning substrate (evolved brains score below a do-nothing policy and the TT brain loses to a linear one), but the NPE heredity measurement stack (P-11 causal copy, CVT-R, z8taint material provenance, ruler-reachability checks) and the receipt/cheat-control contract are instruments worth carrying forward.

Audit group G2. Auditor: Hestia worker (Claude, same model family as the authors; AUDIT_PLAN s4).
Currency: 2026-10-06. Worktree C:/Prometheus-worktrees/hestia-boot-2026-10-06 at 3fed30ac9.

## 0. Identity

- Census (docs/fleet/fleet_state.json, engines["primordial"]): "Nestor Primordial Engine (NPE)",
  research-engine, ACTIVE (last commit 004a689c4, 2026-09-30), paths ["primordial", "roles/Nestor/campaigns"],
  consumers Atlas (harvests npe rows) and Bellerophon (primordial/core seam).
- This engine is TWO distinct mechanisms under one name. The dossier keeps them apart:
  (S) the Primordial Machine SWARM, primordial/ (789 files): batched worlds, "tensor brains", metered
      channels, MAP-Elites, a Redis-stream bus and receipt ledger; 8 rounds, 2026-09-14 to 09-17.
  (Z) the NPE Z8 SOUP, roles/Nestor/campaigns/ (6,079 files): a Z80-like byte VM in which organisms must
      copy themselves; campaigns z80atlas (72 h), cycle 9, c9x, W1, P2, ARC3, ancestry-replay, frontier,
      2026-09-19 to 10-01. Its substrate code lives at
      roles/Nestor/campaigns/z80atlas-verify-2026-09-22/{world.py 1439 lines, z8.py 658, tasks.py 293}.
      (G5 audits prometheus/z80atlas and archaeon/z80atlas; overlap with Z is lineage, not code identity.)
- Read in full: primordial/README.md, core/contract.py, brain/tt_policy.py (1-200), brain/plastic.py,
  brain/REVIEW_PACKET_round1.txt, soup/b1/np_world.py, roles/Nestor/sidequests/graphworld/SWARM.md,
  roles/Nestor/FINDINGS.md (644 lines), campaigns/npe-p2-endogenous-heredity-2026-09-27/SYNTHESIS.md (s0-s12),
  calibration/LEDGER.md (empty), every receipt's claim+science field in primordial/ledger/{C,D,E,G}.jsonl
  and the R5/R7/B7 rows of B.jsonl, REVIEW_PACKET_ROUND7_2026-09-16.txt (s0-s2), R8_RECOVERED_RESULTS.json,
  finals_r8/{B,H}.json heads.
- Read partially: brain/genomes.py (header), qd/e4_run.py (55-110), qd/e5_run.py (60-120), qd/archive.py
  (inventory), lingua/signal.py (header), world.py (header 1-45, function inventory, 769-830), z8.py
  (header 1-50, opcode table), tasks.py (grep), SerendipityFoundry/worldfoundry/wforge/world.py:93-126
  (world generator), npe-arc3 SYNTHESIS_ARC3.md (headline, s1-s3), inference_harvest NPE_MECHANISTIC_SYNTHESIS
  (wave-2 corrections box), inference_saturation_wave2/W2-10 REPORT.md (table), npe-frontier X-TASK-GATE
  ERRATA, roles/Odysseus/expedition/recert/RESULT.md (s5 grep), EXPEDITION_1_REPORT.md s0.
- NOT read: primordial/nv/ (52 files, GPU precision/warp/cudagraph/tensornet engineering), fabric/ (18),
  ops/ (16), score/ (17), metric/ (48), cohorts/ (89), most of tests/ (114), ledger/rows (most of 294),
  soup/b2-b7 bodies, lingua/d1b; Nestor campaigns' 6,000 row files except via the syntheses; the cw01 and
  z80atlas-forensics campaign bodies; inference_saturation_wave2 except W2-10 and the ledger pointer.
  Numbers from those are taken from the seat's own syntheses and are marked as such.

## 1. Mechanism (code, cited)

### (S) The swarm

- World ("Encounter", wforge semantics, batched in soup/b1/np_world.py). A world is a randomly generated
  affine register machine: 4-12 registers mod 2^16 (wforge/world.py:32, 93), 1-2 slots, horizon
  32/64/128/256 (:94-95), random `lin_ops` dst = a*s1 + b*s2 + c mod 2^16 applied every tick
  (np_world.py:109-114), actions 1-3 nibbles that ADD 251*x to target registers (np_world.py:92-102),
  an optional regime flip that negates a (:110), stochastic kicks, observation corruption, and an economy:
  each tick costs `step_cost`, acting costs `act_cost` per unit, and charge is minted when one yield
  register lies in a window (np_world.py:131-138). Fitness is final clipped charge summed over seeds
  (qd/e4_run.py:78-90). This is the whole "physics".
- "Tensor brain" = TTPolicy (brain/tt_policy.py:1-10, 41-75): each uint16 observation is cut into 4 hex
  digits; with d = 4*obs_dim digits, logits = alpha^T G[0,x0] G[1,x1] ... G[d-1,x_{d-1}] W, rank r
  (r=3 in the QD runs, qd/e5_run.py:69-76), action = argmax over an 8-entry action codebook. Formally this
  is a rank-r weighted finite automaton (a matrix product state) reading digits MSB-first, made
  projectively nonlinear by per-step max-normalisation (e5_run.py:98). It is a fixed parametric function
  class, not a mechanism that grows structure.
- Learning, two kinds:
  (a) Evolution: MAP-Elites with a Redis Lua archive (qd/archive.py, E1). Mutation = 5% of floats get
      +0.2*N(0,1), codebook nibble resample (e5_run.py:78-87). Descriptor = (abstain fraction, action
      magnitude) on a 33x33 grid = 1,089 cells (e4_run.py:35, 71-75). The descriptor is about how much the
      agent acts, not about what it computes.
  (b) Plasticity (C2, brain/plastic.py): online ALS per core (:119-146), grow bond rank on surprise
      (MSE > 4x EWMA, :191-206), TT-rounding under a memory charge (:97-116). Standard tensor-train
      regression; the leak cheat (:244-260) is a good control.
- Channel (lingua/signal.py:1-20): a Lewis signalling game. Slot 0 sees R in [0,256), slot 1 must output
  R >> 5 (3 bits); code genome = (k, enc[256], dec[2^k]); cost alpha*bits + beta*entries; a (1+32) hill
  climber searches it.
- Contract/ledger (core/contract.py): every claim is a receipt with separate engineering/science ledgers
  (:83-105); board eligibility requires a non-empty cheat-control string (:108-112) -- which, as Artemis
  R-08 and Nestor confirmed (FINDINGS.md:633-636), accepts any non-empty string.

### (Z) The NPE Z8 soup

- Organisms are byte strings (64 B in the main cells, world.py:41) executed by a Z80-like VM with dense
  opcode space (undefined bytes are NOPs) and world ops ALLOC, BIRTH, SELF, GETPC, SENSE, SPLIT, LDIR/LDDR
  (z8.py:20-27, 55-56). No runner copies bytes: the only path to a child is the organism executing
  ALLOC, writing, BIRTH (world.py:8-13), except in the PAIR_EXECUTION physics where two genomes share a
  128-byte tape and each runs a time slice on it (world.py:769-830); "heredity" there is one half
  overwriting the other.
- Variation: `_mutate` (world.py:484) per-byte/operand mutation; recombination splice (:552). Selection:
  overwrite by copies, energy/resource pressures, optional task-gated interaction (:769-780).
- The "task" (tasks.py): a one-byte conditional transform of an input value (XOR/ADD with a constant,
  regime cue); competence = answering correctly across episodes; ANSWER_BEFORE_READ is measured
  (z8.py header). This is the only computation-coupled element of NPE.
- Instruments: P-11 causal-copy assay (re-execute the event against a randomized victim), CVT-R (a
  two-generation heredity test, Artemis), z8taint byte provenance, DOM painter screen.

## 2. Evidence (tiered)

Ledger census, primordial/ledger/*.jsonl, 158 receipts: PASS 69, FAIL 25, KILL 18, INDETERMINATE 23,
NULL 23 (my count). Total swarm compute through round 8: 1,962 jobs / 492.9 CPU-hours
(R8_RECOVERED_RESULTS.json accounting_correction).

OBSERVED (receipts with committed rows on main):
- G-M1-floors-w134 PASS: "a 0-byte do-nothing policy beats every w1/w3/w4 held64 baseline and every round 2
  clause A candidate, on held64 and on train; the QD archives never reached it." Abstain held64
  w1 88.28 / w3 122.63 / w4 107.75 vs best evolved 63.94 / 105.58 / 98.76; best fixed action on train is
  abstain in 6/6 cells; rejudged record cells below floor 28/28.
- G-R4-3 stage 1/2: of 74 world x pressure cells, learner below the constant policy on train8 in 37/37;
  64 CULLED, 5 HELD, 1 SURVIVED (w13 train128). R7 packet: 74/74 screened, still exactly one survivor.
  R8 (UNRECEIPTED, recovered from rows): a second survivor w8000036, an L1 neighbour of w13.
- E7b / E9 PASS: linear brain has the best median held-out score in 3/3 worlds; tt_digits held64 w1 runs
  [1.4, 3.27, 11.67] vs linear [16.02, 29.75, 39.58] (vs abstain 88.28). E5/E5b: closed-loop TT brains
  beat open-loop action tapes in 0/5 worlds. E6: 0/3 on held-out seeds.
- E-T2 PASS: a 680-parameter transformer brain reaches held64 95.56 on w4 -- also below abstain 107.75.
- B-R5-1 PASS (the swarm's one Clause A pass): on the single surviving cell, a 16-byte int4 linear brain
  matches the 200-byte float linear baseline (progress 1.59, CI 1.14-1.83). A compression result over a
  linear policy; replication was triggered in R8 and never ran (finals_r8/B.json).
- E-R7-1 Clause B (transfer) FAIL: graft - scratch +0.738 (p .046) but graft - sham -0.662; "the SHAM beat
  the graft ... the gain is not transferred structure" (REVIEW_PACKET_ROUND7 s2.1).
- D-R8-3 (UNRECEIPTED observation): E4b's QD coverage claim holds 5/5 worlds under the genome descriptor and
  1/5 under a behavioural one.
- C2 PASS: plastic rank tracks exact-rank regimes 24/24, but on constructed exactly-low-rank targets
  ("near tautological", disclosed) and at ~10x the error of fixed rank 8. C3 PASS / C3b KILL: in the
  representation ecology, "from <=512 samples only the in-vocab program learns (24/24)".
  C7 line (C7b-C7e): 2 FAIL, 2 KILL, 1 INDET, closed; pre-receipt note "digit TT cannot learn B-world
  regimes: MSE = variance" (REVIEW_PACKET_round1.txt s6).
- D1 KILL, D1b KILL: the code learner misses the analytic optimum (P6 gap > 0.02); escape table 0/3 in 7 of
  10 (alpha, beta) cells at every epsilon; three traps named: operator bundling, width valley, rent valley.
- C-R7-AP-03 "PASS" self-labelled VACUOUS: all 64 runs in both arms returned identical held charge 31.71875.
- NPE (Z), from FINDINGS.md and syntheses, all with committed campaign dirs (I sampled, not re-derived):
  * 72 h z80atlas, 23,471 runs: "spontaneous replication" in 1,031 runs narrowed to 57 under P-11
    (E-3), of which Odysseus' functional recert finds 2 self-copiers, 1 context-dependent, 17 painters,
    37 inert (FINDINGS.md:516-522; roles/Odysseus/expedition/recert/RESULT.md:170-216). Max P-11 depth 2.
    910 of 1,031 were splice artifacts of the world's own recombination operator (Z80A-D05; lesson D-7).
  * E-1: 907 non-pair random-start runs, zero births.
  * E-8 / C-DENSE: 1-byte aliases for ALLOC/LDIR/BIRTH give replication from random bytes 13/40 vs 0/40.
  * E-W1-1 C-DENSE-COPY: donor acquisition 1/64 -> 39/64 with a 1-byte block-copy alias (p = 1e-14);
    P2 re-describes it as availability (PLANT 32/96, SHAM 0/96).
  * E-P2-1 C-ZERO-SPECIFIC: establishment rescued by the ZERO register reset only, 26/48 vs 2/48; 95.7% of
    competent donors are SELF-free offset-64 copiers addressing themselves via never-written zero
    registers (P2 SYNTHESIS s0, s4). Wave-2 (h): the contrast is largely built in by the donor screen.
  * E-A3-1 C-A3-INTERNALIZE: register initialisation internalised in 8/144 runs; self-location never
    (280/280 SELF-free copiers fail when moved >= 16 bytes; 2/332 true locators).
  * Landscape: 0/6,400 random genomes or 1-2-step mutants are competent; copiers sit on neutral networks
    (72-80% of 1-step mutants stay competent); losing the copy instruction is a trap (0/144 recovered).
  * CVT-R: 17-28% of "competent" donors in sets (a)/(b) are constructors whose children do not pass
    variation on (FINDINGS.md:595-614).
  * The task line: C9-H1R, gating the answer on cue consumption when reading costs instructions gives
    competence 0.000 vs 0.200; "ungated competence is carried entirely by answer-before-read guessers and
    no reader ever evolves" (FINDINGS.md:266-279).
CLAIMED (prose only): the "seed" interpretations in the syntheses (internalisation as a general route,
  critical mass); several were themselves withdrawn by wave 2 (NPE_MECHANISTIC_SYNTHESIS corrections a-j).
DESIGNED, never run: X-TASK-GATE, the only experiment coupling endogenous heredity to task competence;
  its freeze is invalidated by its own erratum (Stage 0 cannot fire CD; cache keyed across niches;
  regime-blind readers counted competent). W2-10 showed statically that a 64-byte copier+reader genome
  exists (CT_UA: 6/6 children, 22/24 grandchildren keep both properties) -- a construction, not evolution.

## 3. Matrix

### 3a Combinatorial explosion and reachability (side calculations: scratchpad g2_calc.py)

- Encounter state: up to 12 registers x 16 bits = 2^192. Open-loop action tapes: 16^(T*S*W), from 2^128
  (T=32,S=W=1) to 2^6144 (T=256,S=2,W=3). Reactive policies over 4D hex digits: a tt_digits r=3 brain at
  D=13 has 7,515 float parameters (30 KB) vs 112 for linear.
- The desert is not where the authors looked. The reward landscape of these random affine worlds is
  dominated by the action cost: the empty policy is the optimum among constants in 6/6 cells and beats
  every evolved brain on held-out seeds (ratios evolved/abstain 0.72, 0.86, 0.92 on w1/w3/w4). Of 74
  screened cells, 1 (1.4%) has learnable headroom above that floor; at R8, 2 cells in a larger set. Most
  generated worlds contain no reachable policy better than "do nothing"; search spent there measures
  nothing.
- QD coverage is a measurement artifact of a 1,089-cell activity descriptor (abstain fraction x action
  magnitude): coverage claims reverse 5/5 -> 1/5 under a behavioural descriptor (D-R8-3).
- Signal game: code space (2^k)^256 * 8^(2^k) = 2^792 at k=3, for a problem whose optimum is known
  analytically; the hill climber still stalls in 7 of 10 cost cells (D1b).
- NPE: 64-byte genome space 256^64 = 2^512. A specific 6-byte op chain at a fixed site has probability
  256^-6 = 3.6e-15 (about 2.1e-13 over all sites); at 3 bytes 6.0e-8; at 2 bytes 1.5e-5. The measured
  barrier map matches this arithmetic exactly: replication from random bytes is 0/47 with 6-byte chains and
  appears (13/40) only when chains are shortened by 1-byte aliases (E-8). 0/6,400 random genomes and
  their 1-2-step mutants are competent (95% upper bound 4.7e-4). The soup's "discovery" is a lottery
  whose odds are set by the opcode table the designer writes; changing the table moves the result by
  orders of magnitude (C-DENSE-COPY 1/64 -> 39/64).

### 3b Cosplay vs foundation

- Swarm: the component doing the work called "brain" is a fixed-form multilinear function (WFA/MPS over hex
  digits) tuned by Gaussian-mutation MAP-Elites. Nothing composes: no brain calls another, no structure is
  added except bond rank in C2, which tracks targets that were constructed to be exactly low-rank. When a
  learner "wins" (C3b) it is the program whose vocabulary already contains the target. The swarm's honest
  empirical bottom line, from its own receipts, is: linear beats TT, nothing beats abstain, transfer loses
  to a sham. That is not cosplay in the sense of overclaiming -- the swarm reported every one of these
  against itself -- but it is a hard ceiling: a parametric policy class plus selection on a reward
  dominated by action cost.
- Architectural mismatch named: the worlds are affine maps mod 2^16 (np_world.py:109-114); a function of
  the form a*x + c mod 2^16 propagates carries from low to high digits, so its digit-wise representation
  read MSB-first has high TT rank. The brains were given the wrong basis for the physics, and the seat's
  own pre-receipt note says the digit TT "cannot learn B-world regimes: MSE = variance".
- NPE: the work is done by the VM's copy primitive and by environment constants (zero registers, tape
  offset 0, 128-byte wrap). The "replicators" are mostly offset-64 LDIR copiers whose self-location is
  the world's reset (P2 s4). Internalising register setup (8/144) is a real, small, endogenous
  change, i.e. a selection loop over a short operator set discovering one more instruction. With respect
  to reasoning: the only cognition-like test (read the cue, then answer) produced zero readers under cost;
  competence was carried by guessers. No reasoning circuit has been observed in either half.
- Foundation-grade: the instruments. P-11 + CVT-R + z8taint + the painter screen + Wave-2's ruler
  reachability checks are a genuinely good heredity microscope, and the swarm's oracle/cheat-control
  discipline (skip_lin, skip_odd, leak probes, sham grafts with measured false-PASS rate 0/40) is the
  reason its negatives are believable.

### 3c Substrate bottlenecks

- Representation (S): fixed-shape float tensors; no variable binding, no memory beyond the observation
  (closed-loop brains are reactive; obs_delay is a world property, not a brain state), no composition.
- Reward/credit (S): a single scalar (final charge) over a whole episode; action cost makes inaction a
  dominant attractor; credit assignment is population selection only.
- Descriptor (S): behavioural characterisation measures action volume, not function, so diversity is
  diversity of laziness.
- Control-plane load (S): R7 found 13 of 14 new defects in scheduling/registration/close protocol; the
  packet itself says "the instrument is now the main source of findings". About 493 CPU-h produced
  infrastructure and adjudications, not mechanisms.
- Representation (Z): byte genomes with a 2^512 space and a dense NOP-filled opcode table; heredity is
  hostage to environmental constants; tape-write erosion is ~5%/byte/epoch, ~25x nominal mutation
  (FINDINGS.md:320-327); identity follows organism id while bytes are replaced (C9-D14).
- Coupling (Z): heredity and computation are separate channels. Competence is scored on a private
  validation sandbox with world ops disabled (world.py header, "COST"), cached by genome bytes across
  niches (X-TASK-GATE D1), so selection on computation reaches reproduction only through pressure knobs.
- Throughput (both): pure Python VM and numpy; NPE windows of 10 workers x 12 h.

## 4. Deliverable

Discovery Approach. Two bets. The swarm bet that a chimera -- batched random worlds, tensor-train brains,
metered channels and QD selection on a shared bus -- would yield "branch points" and consequential symbols
under charged pressures. NPE bet that open-ended structure starts with endogenous heredity in a byte-VM
soup, and spent most of its effort mapping exactly which barriers (acquisition, establishment,
descendant competence) block a copier from arising and persisting, with unusually rigorous rulers.

The Brick Walls.
1. Reward desert (S): a 0-byte do-nothing policy beats every evolved brain on held-out seeds (abstain
   107.75 vs best 98.76 on w4; even a 680-parameter transformer gets 95.56); only 1 of 74 generated cells
   (1.4%) has headroom above that floor.
2. Wrong basis (S): TT over MSB-first hex digits vs affine mod 2^16 physics; linear beats TT in 3/3
   worlds (tt_digits w1 median 3.27 vs linear 29.75 held64), transfer loses to a sham graft (-0.662).
3. Encoding lottery (Z): spontaneous copiers need a k-byte op chain at odds 256^-k (6 bytes: 3.6e-15);
   every positive result arrives only when the designer shortens chains (1/64 -> 39/64) or supplies
   self-location through reset constants (26/48 vs 2/48).
4. No coupling to computation (Z): under costly reading, 0.000 competence and "no reader ever evolves";
   the one experiment coupling task to endogenous descent (X-TASK-GATE) was never run and its freeze is
   invalid as written.
5. Measurement fragility: 910/1,031 "replicators" were operator artifacts; 57 P-11 donors are 2 genuine
   self-copiers; 17-28% of "competent" donors fail CVT-R. Every headline needed a ruler upgrade.

Seed Viability. The swarm's brains and worlds: dead end as built -- a fixed function class selected on a
reward where inaction wins. The NPE soup: a well-instrumented replicator-accessibility study; it says a
great deal about why copiers are rare and nothing yet about reasoning. Salvage: (1) the heredity ruler
stack (P-11 -> CVT-R -> z8taint material provenance, ruler-reachability checks, planted positives such as
W2-10's CT_UA); (2) the swarm's oracle/cheat/sham discipline (world trace-hash oracle, skip_lin and
skip_odd cheats, sham-graft transfer control with measured false-PASS rate, floor suite with abstain and
best-constant policies). Both would detect a real reasoning circuit's heritable spread if one arose
elsewhere; neither half has produced one.

Evolutionary Roadmap.
1. Kill the reward desert before any search: generate worlds by construction with a planted policy whose
   value exceeds the abstain/best-constant floor by a known margin and whose information requirement is
   known (a POMDP needing k bits of memory or a cue read before acting). Admit a world only if the floor
   suite and a planted solver separate (the G floor suite already computes the floor; make it a generator
   constraint, not a post-hoc cull).
2. Replace the brain class with a compositional one: typed straight-line programs over the world's own
   algebra (Z/2^16 add, mul-by-constant, compare, branch) with a description-length (MDL) charge, or
   equivalently graph-rewriting over a typed expression DAG. Keep TT only as a baseline. Learn with
   lexicase or novelty+fitness, and characterise behaviour functionally (input-output signatures on probe
   states), not by action volume.
3. In NPE, make computation heritable by construction: score task competence in situ on the live tape
   with the organism's own registers, so that the same bytes that copy also compute; declare the reset
   policy as a world axis (P2 s8 item 5); seed with W2-10-style dual-function genomes and measure whether
   the task routine is maintained (CVT-R on the routine, z8taint on its bytes).
4. Open-endedness metrics (Bedau-Packard evolutionary activity, MODES change/novelty/complexity/ecology)
   computed on CVT-R-certified lineages, not on raw births.
5. Multi-agent dynamics only after 1-3: Lewis signalling in populations with iterated learning, where
   the D1 meter supplies the bottleneck; the D1b traps say single-point operators beat bundled ones.

The ONE decisive experiment. The amended X-TASK-GATE, run as its erratum requires: ffa6-class pair-tape
cell, ATOMIC write-back, in-situ uncached competence on each organism's own niche task, FORCED_READ with a
reading cost, a Stage-0 planted positive (CT_UA) that must reach CD >= 0.10 in >= 3/6 runs, then de novo
arms (random start, and dense-alias start) with task-coupled interaction vs uncoupled, 96 seeds each.
Question: can endogenous descent carry and spread a cue-READING routine against guessers? Kill criterion:
if the planted positive passes Stage 0 but the de novo task-coupled arm yields 0/96 runs with a
CVT-R-certified lineage of readers (held >= 0.5, cue consumed before answer) carried by causal descent,
close NPE as a reasoning substrate and keep only its instruments. (If the planted positive fails Stage 0,
the finding is that task-coupled endogenous descent is unreachable in this physics.)

## 5. What would change this verdict

- Toward VIABLE_SEED: a committed X-TASK-GATE result where readers arise de novo and spread by
  certified descent above the uncoupled control; or a swarm world family generated with planted headroom
  where an evolved compositional brain beats both the floor and a linear policy on held-out worlds.
- Toward DEAD_END: if the heredity rulers turn out not to transfer outside the Z8 VM (they are VM-coupled:
  P-11 re-executes on the Z8 machine), the salvage shrinks to the receipt discipline alone.
- An error in my reading of the floor comparison (e.g. if held64 in G-M1 and E7b were on different scales)
  would weaken brick wall 1; I checked that G-M1's best baseline equals E8's reported closed-loop median
  (63.94 at w1, 128 seeds), so the scales agree.
