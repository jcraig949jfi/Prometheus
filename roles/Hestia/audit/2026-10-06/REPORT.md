# Hestia Audit 1 -- The Audit & Roadmap Report

Currency: 2026-10-07. Instance Hestia[buckkeep-8cd68af4]. Base 013e7ce5e;
audited tree origin/main 3fed30ac9 (branch hestia/boot-2026-10-06, worktree
Prometheus-worktrees/hestia-boot-2026-10-06).
Charter: roles/Hestia/prompts/2026-10-06_charter/ (verbatim, MANIFEST).
Plan, frozen before any dossier: AUDIT_PLAN.md (3fed30ac9).
Evidence: 25 engines in 22 dossiers under dossiers/ (7,001 lines, every
mechanism claim cited file:line, every number tiered OBSERVED / CLAIMED /
DESIGNED). This report condenses them; where it and a dossier differ, the
dossier's cited rows win.

STATUS OF THIS DOCUMENT: a model's assessment for the operator. It admits,
retires and promotes nothing and marks no seat dead. "Dead end" below means
the mechanism as built, never the lineage. Conflict of interest: the
auditor is the same model family that wrote most of these engines. It needs
an independent attacker (Part 7).

----------------------------------------------------------------------
## PART 0. The bottom line (one screen)

1. None of the 25 engines contains a reasoning circuit today, and none
   claims to (to their credit, most seats' own verdict documents already
   say so). The operator's word "cosplay" is accurate for the ORGANISMS. It
   is not accurate for the INSTRUMENTS, which are the strongest thing the
   program has built.

2. The program has measured the SAME wall at least seven times in seven
   different substrates, without naming it as one wall:

       Ananke PTE     FLIP (bit-conditioned mapping)     0 / 290 searches
       z80atlas       INC -> COND_ONE (4-byte insert)    0 / 960 runs
       SFE/Proteus    W2_K2 (hold two values)            0 / 395 runs
       Crius          reuse mechanism (26-edit path)     0 / 475,728 cand.
       Tyche          order-3 interaction                0 solves, v0-v2
       Primordial     cue reader under read cost         0, "no reader evolves"
       Aether         input combination (composition)    <= 2/256 every law

   THE COMPOSITION WALL: every engine finds 1-step mechanisms (a latch, a
   relay, one inserted instruction, one held value) and none finds the
   first mechanism made of two parts that are individually worthless. This
   is not bad luck. It is close to a theorem (Part 2, W1).

3. The worlds mostly do not pay for reasoning. In Cosmos, a single register
   is optimal everywhere. In Ensorain, 0 world families need hidden state.
   In Ludus, a 2-step lookahead gets at least 96% of optimal in 22 of 22
   worlds. In Primordial, a do-nothing policy beats every evolved brain.
   Selection cannot find what the world does not reward.

4. Nothing lets a learned unit become a building block. Aphrodite R8 shows
   it directly: inheriting the learned library CUT the next generation's
   own learning from 56 families to 10. The other examples: Nyx has 1 of
   485 organs that is a composition operator, the forge has 0 of 10 cross-
   tier imports, and incubation is a selection from a fixed menu.

5. Verdicts: 0 VIABLE_SEED, 24 SALVAGE_COMPONENT, 1 INSUFFICIENT_EVIDENCE
   (Moonshot), 0 DEAD_END as a whole engine. Splitting SALVAGE honestly:
   - 7 engines carry a LIVE SUBSTRATE LEAD with a designed, unrun, decisive
     test: Aether, Ananke, Ares, Crius, Aphrodite, Tyche, Moonshot.
   - 18 are dead ends AS SUBSTRATES whose value is an instrument.

6. The seed worth scaling is NOT any one organism. It is (a) the shared
   certification stack, the program's real asset, and (b) one bet: that an
   explicit "promote a solved unit to a primitive" operator, or lifetime
   plasticity, gets past the composition wall when blind mutation does
   not. That bet is cheap to test, and Part 5 gives the single cross-
   substrate experiment that decides it.

7. Recommendation: stop building new worlds and organisms of the current
   shape (flat genome, point mutation, scalar fitness, no promotion
   operator). The seven-fold 0 says the next one will hit the same wall.
   Spend the next cycle on the Composition Ladder (Part 5). If it fails
   everywhere, the honest conclusion is that "grow, don't design" does not
   reach compositional reasoning at this scale without a designed
   abstraction mechanism. That is a result, not a funeral.

----------------------------------------------------------------------
## PART 1. Verdict table

    engine              verdict        substrate        headline wall (number)
    ------------------- -------------- ---------------- ---------------------------------
    Aether              SALVAGE        LIVE LEAD        98.7% frozen; composition <=2/256
    primordial (NPE)    SALVAGE        dead end         do-nothing 107.75 > best 98.76
    odysseus            SALVAGE        dead end         no plasticity, no input, no task
    prometheus/ananke   SALVAGE        LIVE LEAD        FLIP 0/290; 2^375 vs 5.5e4 evals
    moonshot (Themis)   INSUFFICIENT   LIVE LEAD (des.) 0 lines of organism/primitive code
    sigma_kernel        SALVAGE        not a substrate  capability race (by reading)
    prometheus/cosmos   SALVAGE        dead end         0/10 laws beat the definition rung
    ensorain            SALVAGE        dead end         N6 batch fit beats 9/9 specimens
    ludus               SALVAGE        dead end (none)  2-step lookahead >=96.2% in 22/22
    z80atlas (both)     SALVAGE        dead end         COND_ONE 0/960; 1e-18 per copy
    ares                SALVAGE        LIVE LEAD        1-bit latch ceiling; transplant 0.019
    crius               SALVAGE        LIVE LEAD        0/475,728; 26-edit path ~1e-52
    sfe_ecology (6)     SALVAGE        dead end         W2_K2 0/395; 0/18,266 useful edits
    nyx                 SALVAGE        not a substrate  0 organs transferred; 542/549 read-only
    Aphrodite engine    SALVAGE        LIVE LEAD        R8: inheritance 56 -> 10 families
    incubation (+_d)    SALVAGE        dead end         menu ceiling 634^k; D-VM never built
    alien_circuitry     SALVAGE        dead end         needs full oracle (5.1e12 at n=10)
    agent_d2..d5        SALVAGE        dead end (none)  shuffled history keeps 100% of gain
    theseus/synth       SALVAGE        dead end         loses to random on 2 of 3 rulers
    tyche               SALVAGE        LIVE LEAD        order-3 needle 4.8e-7; 0 solves
    herakles/evca       SALVAGE        no search exists 2^128 rule space; 0 searched
    forge lineage       SALVAGE        dead end         constant decoy 75/186 >= best tool 74

  "LIVE LEAD" = a named mechanism with a designed, unrun test that could
  move the verdict to VIABLE_SEED or DEAD_END. "dead end" = the substrate,
  as built, is not a route to reasoning; its instrument survives.

----------------------------------------------------------------------
## PART 2. The cross-cutting brick walls (the "physics" this program has
## actually measured)

W1. THE COMPOSITION WALL (selection over flat genomes cannot assemble
    mechanisms whose parts carry no individual fitness).
    Shape: a k-part mechanism whose parts are individually neutral or
    harmful is a needle of probability about p^k per trial. The numbers:
    the Crius partial-mechanism map (each part alone -0.001 / -0.002 /
    -0.057; two parts together +1.14 at 26 edits), the z80atlas COND_ONE
    insert (about 1e-18 per copy), the Ananke 16/16-line FLIP program, the
    Tyche order-3 needle of 128^-3. The expected waiting time is
    exponential in k, and the fleet's budgets (1e4 to 1e7 evaluations) sit
    10 to 40 orders of magnitude short.
    The theory behind it (LITERATURE, cited from memory, not from the repo;
    verify before quoting): Valiant, "Evolvability" (J. ACM 2009), and
    Feldman (STOC 2008) show that evolvability by fitness-proportional
    selection is equivalent to Correlational Statistical Query learning.
    Parity-like functions are not CSQ-learnable in polynomial time. XOR,
    FLIP, COND and order-3 interaction are exactly the parity-like targets
    the engines fail on.
    Caveat: Valiant's model differs from these engines (fixed distribution,
    polynomial representations, no recombination or population structure),
    so this is a strong prior, not a proof about them. But it says what
    is needed: the escapes are (a) a non-CSQ signal (structured partial
    credit or a curriculum that makes each part individually fit), (b)
    modularity, i.e. duplicating and reusing a solved part so that k parts
    cost k searches instead of p^k, or (c) learning within a lifetime,
    which is not bound by the evolutionary CSQ limit.

W2. THE WORLD-DEMAND DEFICIT (the worlds do not select for reasoning).
    Cosmos: 721 worlds collapse to 8 behavioural classes, and one register
    is optimal. Ensorain: 0 grammar families need hidden state, and 179 of
    181 admitted worlds have delay 0. Ludus: shallow lookahead at least
    96.2% in 22/22, and the exact solver is capped at 4e6 states, below
    where planning pays. Primordial: 1 of 74 world cells (1.4%) has
    learnable headroom. Moonshot's floor task is a 1-bit latch.
    Shape: when an optimal policy is a reflex or a latch, any selection
    process converges on the reflex. A world worth evolving in must make
    the reasoning circuit's VALUE OF INFORMATION positive at every rung.
    None was built that way.

W3. THE PROMOTION GAP (no learned unit becomes a primitive).
    Aphrodite R8 (inheritance substitutes for improvement, 56 -> 10),
    Ares transplant (median 0.019 of function recovered, because edges are
    rewired at random: substrate.py:365,377), Nyx (1 of 485 organs is a
    composition operator), forge (0 of 10 imports), incubation (634^k menu).
    Shape: without a typed interface and an operator that freezes a
    solved sub-program into a callable unit, depth of abstraction is
    capped at 1. This is W1's escape (b), and nobody has built it into an
    evolving substrate.

W4. THE SCALAR-CREDIT BOTTLENECK. Crius scores one number per 50-task
    lifetime, so steps that add a new part score +0.0004 to +0.0011,
    inside neutral-edit noise. The SFE exact-match reward pays 1/K for
    free to an echo program. Primordial scores activity and abstention,
    not computation.
    Shape: credit assignment over a whole lifetime throws away exactly
    the signal that W1's escape (a) needs.

W5. INSTRUMENT INFLATION RELATIVE TO PHYSICS. Cosmos: custody and sealing
    code outweighs physics code 5.5:1. SFE: each row takes 95-193 s of
    round-trips for 0.1 s of science, and the ledger caps at 400-900
    events/s. sigma_kernel: about 11k lines of math probes inside a
    kernel. This is not wasted. The instruments caught at least three
    false positives in Aether alone, plus the forge decoy and the D-5
    shuffle. But the program's marginal effort has been going into rulers
    while the organisms stayed one-step.

W6. EVIDENCE OFF THE REPOSITORY. The D-3 results/ folder is gitignored.
    Large z80atlas, ares and crius run rows live on M2 only and are
    referenced by hash. The E-003 BEE verdict is on a branch, not main.
    Several numbers in this audit are therefore CLAIMED, not OBSERVED.

----------------------------------------------------------------------
## PART 3. Per-engine reports

Format per engine: Discovery Approach / The Brick Walls / Seed Viability /
Evolutionary Roadmap (with the one decisive next experiment and its kill
criterion). Full citations are in the named dossier.

### 3.1 Aether (AGE native-circuitry engine) -- dossiers/Aether.md
Discovery Approach: a torus of 5-byte sites under a fixed physics law
  (aeth01.v1). Only one opcode, WRITE, acts. A writer copies its payload
  into one field of one neighbour. Hash arbitration settles contests and
  injected bit-flips add noise. The idea is that "native circuits" will
  appear as persistent causal structure, studied by lesions and by
  one-law-change variants (E-0xx, AIM01/02, TEST-3).
Brick Walls:
  - Frozen and bound to the initial aim: 98.65-98.80% of sites are late-
    frozen under all 4 energy economies, and 92-96% of all change happens
    inside the initial writers' aim (OBSERVED, ER01/AIM01 JSON).
  - No input combination: a winning write REPLACES the target byte
    (aeth01_cpu_oracle.py:185; verified by Hestia). Values per changing
    site are 2.04-2.13, the late-window novelty is 0.0000 new values, and
    composition is at most 2/256 for every law tried.
  - No spontaneous structure: a self-propagating writer chain has about
    9.8e-5 per link, so about 1e-6 expected 3-link chains in a 512^2 soup.
    Scale does not help: 256^2 matches 2048^2 bulk statistics within 0.4%.
Seed Viability: SALVAGE_COMPONENT, LIVE LEAD. The substrate as built is a
  copy-only medium that cannot compute. Worth keeping: the twin-world /
  counterfactual-parent / value-provenance instrument stack, which caught
  three false positives (rcv, add, AIM01), and one lead, the recoil x
  exchange law mob_r1x1e0. Its regime is new, but its composition rate is
  still 2/256.
Evolutionary Roadmap:
  1. NEXT (decisive): TEST-4 as already designed (V2B/TEST-3/
     OPERATOR_REVIEW.md). Plant 8 values per origin, decode at radius 1-6
     against an exchange-only baseline, and test a single-site reset.
     KILL the copy-only radius-1 family if radius-2 decoding does not beat
     the baseline on at least 3/4 seeds, OR the reset removes no more
     divergence than the baseline, OR own-history prediction is >= 0.9.
  2. Add a commit operator table (xor / add / and of old and incoming
     values) and protect code fields from data writes. This is the
     minimum for any gate to exist.
  3. Arbitration with memory (stateful winners), so a contested channel
     can act as a switch.
  4. Re-model the physics as typed graph rewriting / combinator chemistry
     and screen laws automatically by information-flow and open-endedness
     metrics, instead of writing one law at a time.
  5. Hand-build a gate and a memory cell in the surviving law BEFORE any
     more soup search: prove the physics CAN compute before asking
     whether it WILL.

### 3.2 primordial (Nestor Primordial Engine) -- dossiers/primordial.md
Discovery Approach: two mechanisms under one name. (i) A swarm of worlds
  and "tensor brains" (rank-3 tensor trains reading observations as hex
  digits, i.e. a fixed weighted finite automaton, tt_policy.py:1-10),
  tuned by random mutation and MAP-Elites on a Redis bus. (ii) The Z8
  byte soup, where organisms must copy themselves (NPE campaigns).
Brick Walls:
  - Reward desert: abstain scores 107.75, against 98.76 for the best
    evolved brain and 95.56 for a 680-parameter transformer. 1 of 74
    world cells has learnable headroom.
  - Wrong basis: brains read hex digits, but the worlds are affine maps
    mod 2^16. A linear brain beats the tensor brain in 3/3 worlds, and
    transfer loses to a sham graft (-0.662).
  - Encoding lottery: a 6-byte copy chain is about 3.6e-15. Replication
    claims fell from 1,031 runs to 57 under P-11 and to 2 real copiers on
    a functional recheck; 910 were artifacts of the world's own
    recombination splice. Copiers locate themselves only through
    zero-reset registers: 280/280 fail when moved.
Seed Viability: SALVAGE_COMPONENT, dead end as a reasoning substrate.
  Keep the heredity instruments (P-11 causal copy, CVT-R, z8taint byte
  provenance, fire-ability checks) and the cheat-control discipline.
Evolutionary Roadmap: one test before closing. Run the amended X-TASK-
  GATE (frozen, never run, and its frozen version invalidated by its own
  erratum). The hand-built CT_UA genome (copies AND reads the cue) is a
  must-pass positive control; then 96 seeds per arm from random starts,
  with reading made costly. KILL: control passes and 0/96 de novo runs
  produce a CVT-R-certified cue-reading lineage. Then close NPE as a
  reasoning substrate and move the instruments to whichever engine passes
  Part 5.

### 3.3 odysseus (sharded spiking circuit) -- dossiers/odysseus.md
Discovery Approach: a LIF spiking circuit sharded across machines, run in
  lockstep UDP ticks with hash-verified replay, rewind and fork.
  Self-described as "an instrument, not a reasoner". Parked.
Brick Walls:
  - No learning substrate: weights are hash-derived constants (+520 /
    -900) that are never stored (model.py:80-93); the only input is hashed
    noise (model.py:106-110). Behaviour is a period-3 rhythm with 20-30% of
    neurons firing each tick.
  - Forks escape at once: the chance that a spike stays inside its own
    shard is (1/S)^8, about 1.5e-5 at 4 shards (test_fork.py:46).
  - Plasticity is ruled out by design: storing synapses costs 32 B per
    neuron (32 GB at 1e9), and pure Python takes about 600 s per tick at
    that size.
Seed Viability: SALVAGE_COMPONENT. Keep the integer-exact record/replay/
  fork layer (frames.py, player.py) as a fleet instrument.
Evolutionary Roadmap: only if the spiking line is wanted at all. Add an
  integer three-factor rule (eligibility trace times reward) and a delayed
  match-to-sample task, N = 4000, 8 seeds, against a frozen reservoir
  with a trained linear readout. KILL: plasticity fails to beat the
  reservoir by >= 10 pp on 6/8 seeds, or replay stops being bit-
  identical. This is also W1 escape (c) in a second substrate; see Part 5.

### 3.4 prometheus/ananke (PTE packet-tensor substrate) -- dossiers/prometheus__ananke.md
Discovery Approach: 16-line register programs (a primitive VM) evolved by
  a plain GA across a "physics map" of task cells (C1, C1b, C2A-C).
  Counterfactual mirror-pair swaps locate where a bit is carried.
Brick Walls:
  - Composition wall: FLIP 0/290 from random starts, upper bound about 1%
    per search. XOR 0/83. The only known FLIP program uses 16/16 lines.
    More budget, unshaped fitness, 4x worlds, two stepping-stone types
    and a block-move operator all failed (rows recounted by the auditor
    and matching the seat's packet).
  - Needle landscape: one random edit kills a working program 62% of the
    time, and 0/81 broken starts recover.
  - Space: 2^375 programs against at most 55,296 evaluations per search;
    each extra line multiplies the space by 2^23.5. Only 17/200 relay
    cells and 4/200 FLIP cells were admissible, so part of the "physics
    map" is a construction artifact.
Seed Viability: SALVAGE_COMPONENT, LIVE LEAD. The substrate is not a
  cognitive architecture, but it is the cleanest place in the fleet to
  test W1 escape (b). The exact counterfactual tool and the C2A
  "search cannot find vs physics cannot do" protocol are fleet-grade.
Evolutionary Roadmap: NEXT, the FLIP representation test at the 4
  admitted cells. Arms: the current genome; a genome with a first-class
  mapping bit plus a block-duplication operator; and that genome seeded
  with a frozen relay module. KILL: both new arms <= 1/32 at 4x budget.
  PASS: >= 6/32, with success traced to the duplicated module. On a pass,
  generalise duplication into a typed "promote module" operator and climb
  the Part 5 ladder.

### 3.5 Moonshot (Themis, EP-MOONSHOT H2/H3) -- dossiers/moonshot_themis.md
Discovery Approach (designed): survival-only evolution of mechanisms that
  depend on retained hidden information (H2), and an "integer neural
  primitive" claimed to improve discovery under fair accounting (H3).
Brick Walls:
  - Nothing to audit yet: 0 lines of organism, world-task or primitive
    code. The only Moonshot code (about 2,900 lines) is a job-distribution
    layer whose runtime hashes sha256 as busy-work. The primitive is
    never defined in v0.1-v0.3.
  - Trivial floor, desert one rung up: the delayed-cue floor is a 1-bit
    latch (PTE's equivalent HOLD was solved in 97/155 cells, mostly by a
    trivial latch). The context-flipped rung is PTE's FLIP, 0/290.
    Survival-only selection gives a weaker signal than PTE's shaped score.
  - H3 power trap: separating a 5% from a 10% discovery rate needs about
    435 independent populations per arm, and no rung in the design sits
    in that band.
  - The named world engine (wforge) has no cue world, and the review's
    unpaid-write defect is visible in the source (world.py:216-224).
Seed Viability: INSUFFICIENT_EVIDENCE. The primitive is foundational only
  if it is PLASTIC, i.e. updated within a lifetime (W1 escape c). Evolved-
  only integer weights are just more genome fields and inherit W1 whole.
Evolutionary Roadmap: before any cluster spend, a CPU pilot on the
  context-flipped delayed-cue task with a symbolic-only arm, a neural arm
  with fixed weights and a neural arm with plastic weights, 64
  populations each. KILL: all three <= 2/64 at 4x the floor budget
  (Moonshot re-scopes to its instruments). SEED: the plastic arm alone
  reaches >= 8/64 and disabling the primitive returns it to the null.

### 3.6 sigma_kernel (Techne) -- dossiers/sigma_kernel.md
Discovery Approach: not a discovery engine. It is a content-addressed,
  append-only symbol store with single-use capability tokens and three-
  valued gates; "reasoning" opcodes (REWRITE, EQUIV) only RECORD that an
  assertion was made.
Brick Walls:
  - Computes nothing about a symbol's content. The falsifier parses
    `mean OP value` against a caller-supplied number (omega_oracle.py:39-69).
  - DEFECT (confirmed by reading, NOT by a race test): "linear across
    processes" fails for the core opcodes. PROMOTE checks at
    sigma_kernel.py:833, rolls the transaction back at :837, then does an
    unconditional `UPDATE capabilities SET consumed=1 WHERE cap_id=?`
    (:899; same at :995, :1261, :1449). Under the Postgres backend two
    processes can both spend one capability. The extension modules
    already use the safe `AND consumed=0` form (bind_eval.py:565,
    residuals.py:623). Routed to Techne.
  - Scope creep: about 11k lines of math probes inside the kernel.
Seed Viability: SALVAGE_COMPONENT (provenance infrastructure, not a
  substrate). Keep the caveat-in-hash symbol record.
Evolutionary Roadmap: a two-process PROMOTE race test, 1,000 trials on
  Postgres. Any double-spend confirms the defect; after the compare-and-
  set fix it must be 0/1000.

### 3.7 prometheus/cosmos (world physics and law mining) -- dossiers/prometheus__cosmos.md
Discovery Approach: worlds with a delayed-match demand. Three hand-written
  "agents" (cue-only, keep-all, keep-none: contract.py:17-20). A
  certificate asks whether holding the cue pays for its maintenance cost
  (phenomenon.py:32-43), and an exhaustive symbolic-regression grammar
  mines "laws" over author-declared coordinates (miner.py:81-100).
Brick Walls:
  - The miner rediscovers its own label: 0/10 mined laws beat a zero-
    parameter rule written from the certificate's own economics (best
    McNemar p = .125; C3 out of sample tied 42 = 42). The seat downgraded
    these itself (R-0001/2, G-0006).
  - Task poverty: at most 4 bits, one question. 721 worlds collapse to 8
    behaviour classes, and one register is optimal everywhere.
  - Unidentifiable grammar: 13,272 singles and about 3.5e8 conjunctions,
    of which 60 are scored (1.7e-7); laws change with the seed at 30 runs.
  - Custody:physics code is 5.5:1.
Seed Viability: SALVAGE_COMPONENT, dead end as a substrate. Keep the C3
  P1/P2 certificate (decode the cue from state AND swap state between
  paired runs to change behaviour; c3/certify.py, c3/calib.py; 5/5 planted
  controls at v3). It is the best substrate-agnostic "is this a working
  memory?" ruler in the fleet. Also keep the rule that a law must beat the
  zero-parameter definition rung, and leave-one-family-out evaluation.
Evolutionary Roadmap: extract the certificate unchanged and apply it to
  the memory claims of Aether, a Primordial organism and an Ensorain
  organism. KILL: any planted control misclassified in >= 1 of 5 fresh
  seeds, or it cannot tell a passive trace from a working register at
  affordable episode counts.

### 3.8 ensorain (tensor world engine, WTP-01..04) -- dossiers/ensorain.md
Discovery Approach: a World Genome grammar generates tensor worlds; a
  fixed menu of 490 online tensor regressors (10 memories x 7 learning
  rules x 7 policies) competes on one replayed experience stream (the
  WTP-03 collider) against a null ladder N0-N6.
Brick Walls:
  - The organisms lose to a simple baseline: the tuned batch fit N6 beats
    9/9 promoted specimens. The code says "no symbolic-rule substrate
    exists in this engine" (wtp3/collider.py:241; verified).
  - The worlds do not need memory: 0 grammar families need hidden state,
    and 179/181 admitted WTP-03 worlds have delay 0.
  - Reachability: 0/2,000 random candidates admissible; 0 "beyond known
    physics" in about 65,000 candidate worlds; the genome space is about
    6.1e18.
Seed Viability: SALVAGE_COMPONENT, dead end as a substrate. Keep the
  collider (one experience stream replayed to every competitor, the null
  ladder, an exact surrogate, a recombination holdout) and the ARC3
  exact-oracle ladder.
Evolutionary Roadmap: the Hidden-State Necessity Assay. Three latent-
  state world families with exact Bayes oracles, all 490 menu organisms
  plus nulls, window statistics and one stateful candidate, >= 8 seeds.
  KILL: a menu organism or null captures >= 0.6 of the oracle gap in all
  families, or no stateful candidate beats the window statistic by >= 0.10
  of the gap in >= 2 families. These worlds should become rung 1-2 of the
  Part 5 ladder.

### 3.9 ludus (board games as worlds) -- dossiers/ludus.md
Discovery Approach: an exact-DP bench over small games (Atlas of Worlds,
  arena, FOUNDRY generator). Its "circuits" are 1-10 line hand-written
  heuristics (bench/circuits.py:37-170; verified). There is no organism.
Brick Walls:
  - Shallow worlds: a two-step lookahead keeps >= 96.2% of optimal in
    22/22 worlds.
  - Exactness ceiling: full enumeration is capped at 4e6 states (largest
    measured 4.4e5). Worlds hard enough to reward planning sit above it.
  - A gate fooled by short formulas: Nim(3,4,5,6) was admitted although a
    4-line xor rule is optimal on 4,847/4,847 positions.
Seed Viability: SALVAGE_COMPONENT (an instrument bench, not a substrate).
  Keep the exact value-retention ruler, the depth profile with cheat
  controls, the leak audit (4/4 injected leaks caught) and FOUNDRY's
  one-knob world variation.
Evolutionary Roadmap: add a hidden-memory knob m = 0..4 to FOUNDRY and
  exhaustively search a typed rule language up to size 8. KILL (for the
  world family): a size-<=8 rule that reads only the current observation
  keeps >= 95% at every m. Add a minimum-description-length gate so a world
  whose optimum is a short formula (Nim) is not admitted as "deep".

### 3.10 z80atlas (Bellerophon prometheus/z80atlas + Archaeon archaeon/z80atlas) -- dossiers/z80atlas.md
Discovery Approach: a Z80-like instruction-set soup of self-copying tape
  programs (Tierra/Avida lineage), with tasks that are functions of one
  input byte, rewarded through a ledger, plus a de novo census of random
  tapes.
Brick Walls:
  - Two-instruction step: INC -> COND_ONE 0/960 runs in every arm (the
    one-byte ECHO -> INC step: 58/320). COND_ONE needs a specific 4-byte
    insertion, about 1e-18 per copy, against about 1.2e10 organism
    executions in the whole campaign.
  - Spontaneous replication is a lottery: 0 verified in 101,003 runs, and
    the one surviving random-start world out of 27,141 is what the census
    predicts. The 80-world follow-up had an expected 0.06 positives, so
    its 0/80 was predetermined (about 4,063 worlds were needed).
    Bellerophon's ~7% replication-origin rate exists only because of LDIR
    block-copy and 80% no-op bytes; the copy-free ISA had 0 copiers in 12M
    tapes.
  - Copying fights computing: without task reward the task is lost (178
    task-reached without copying vs 2 with). With a reward paid from a
    Python ledger outside the VM, the main effect is that seeded code
    survives. From a random start: 0/3,200.
Seed Viability: SALVAGE_COMPONENT, dead end as a cognitive substrate (a
  careful, well-controlled Tierra re-run). Keep the byte-provenance copy
  classifier, the YOKED / SHUFFLED / RANDOM_REWARD control arms, the census
  as a prior, and the byte-exact replay.
Evolutionary Roadmap: one last test of W1 escape (a). COND_ONE with a
  stepping-stone task rewarded first, partial solvers no longer paid,
  founder-to-solution edit distance measured in advance, YOKED control,
  240 seeds per arm, 20k ticks. KILL: <= 2/240 acquisitions with the
  stepping stone = DEAD_END for this ISA.

### 3.11 ares (graph organism under pressure) -- dossiers/ares.md
Discovery Approach: a 17-node recurrent arithmetic graph organism evolved
  in an isolated sandbox under pressure regimes, with memory-ablation
  instruments (carriers.py) and present/absent/shuffled controls.
Brick Walls:
  - Depth ceiling: every success needs at most one stored bit (a latch,
    in 2/10 champions a single self-loop). Worlds needing two interacting
    state variables fail (CLAIMED from the seat's 3-seed reports).
  - Waiting time (estimate): a useful memory unit appears at about 0.017
    per mutation with no immediate fitness gain, so about 2e5 mutations
    for a 3-part mechanism against 15,360 genomes per run.
  - No reuse: transplants recover a median 0.019 of function because
    outside edges are rewired to random host nodes (substrate.py:365,377;
    verified).
  - All three memory types are hand-built, so "no new memory type
    appeared" was guaranteed. "Recurrence wins" is the textbook bistable-
    vs-leaky difference.
  - Defects: committed sweep_c2/gates.txt still shows the uncorrected
    "GATE C OPEN"; champion selection on the held-out set biases results.
Seed Viability: SALVAGE_COMPONENT, LIVE LEAD (small). Keep the ablation
  instruments and the "widest viable region" rule.
Evolutionary Roadmap: parity over k = 1, 2, 3 hidden bits, 10 seeds at
  4x budget, plus an arm seeded with an evolved latch to test reuse.
  Fix the transplant to map interface edges by type, not at random, first.
  KILL: k = 2 succeeds in < 5/10, or time-to-success grows > 30x from
  k = 1 to k = 2 with k = 3 at 0/10.

### 3.12 crius (adaptive workspace sandbox) -- dossiers/crius.md
Discovery Approach: an evolving bytecode organism in a world/tasks/VM
  sandbox, measuring which machinery makes later learning cheaper (the
  RELAY world, A-J control battery).
Brick Walls:
  - Gradient-free parts: each part alone is worth -0.001 / -0.002 /
    -0.057; two parts +1.14 at 26 edits; the full mechanism +15.97 at 47
    edits. A 26-edit unguided path is about 1e-52 against about 1e6 edits
    explored; 0/475,728 candidates over 66 runs.
  - Scalar credit: one fitness number per 50-task lifetime; steps that
    add a part score +0.0004 to +0.0011 (CLAIMED, the seat's).
  - The environment does the hard parts: auto-calibration of actions
    (vm.py:461) and a free world simulator (vm.py:490), both verified.
    "Planning" is depth-3 brute force, 32,768 candidates. Every metric was
    gamed: a quitting program scored 3.00 against 2.97 for real reuse.
Seed Viability: SALVAGE_COMPONENT, LIVE LEAD. The reuse ASSAY is the best
  "did a later task get cheaper because of a stored mechanism?" ruler in
  the fleet, and it rejects the cheats seen here.
Evolutionary Roadmap: a matched pair on RELAY with auto-calibration and
  the simulator REMOVED. ROUGH = the current bytecode. SMOOTH = add an
  operator that turns successful action traces into new primitives, plus
  per-block credit. 9 runs per arm. KILL: SMOOTH 0/9 ends evolutionary
  reuse substrates for this target. SEED: SMOOTH >= 3/9 with ROUGH 0/9.

### 3.13 SFE ecology (SFE, wforge, Vivarium, Proteus, archaeon/frontier, archaeon/wse) -- dossiers/sfe_ecology.md
Discovery Approach: a provenance-heavy experiment ledger (SFE) hosting
  worlds from a genome-to-world grammar and wforge (random affine maps
  mod 2^16 with a reward window), executed by Vivarium, with Proteus's
  25-opcode flat bytecode players evolved by a tournament GA and
  scheduled as deep-frontier lineages by Archaeon.
Brick Walls:
  - Two-value memory unreachable: 0/18,266 single-edit children useful on
    both flat and graph encodings (PROTEUS-46). W2_K2 full solves 0/395,
    though a 12-instruction hand solution exists. The gap is reachability,
    not expressiveness.
  - Exact-match reward pays an echo 1/K for free, so it parks there. All
    175 full solves in the 1,277-row reachability table are single-value.
  - Detectors saturate: they fire about 0.45-0.47 per evaluation; 4/11
    are UNABLE on all 1,775,074 subjects. SFE itself has only onemax and
    NK scoring (sfe/executors.py:53-371). Each row costs 95-193 s of
    round-trips for 0.1 s of science.
  - Output of 3,719,136 frontier evaluations: one register holding the
    latest value, plus early halting.
Seed Viability: SALVAGE_COMPONENT, dead end as a substrate. Keep the
  provenance contract (sealed predictions, loser-preserving selection
  families, attestation), the WSE reachability table with its batteries,
  and the per-operator damage-geometry census.
Evolutionary Roadmap: re-express W2_K2 in a typed program representation
  with typed-edit mutation; same table, budget and seeds as the 0/395.
  PASS: full-solve rate lower bound >= 0.25 over >= 30 seeds with two
  separately erasable stores. KILL: 0/30 at 10x budget, or solves that
  are 1/K echoes. Retire the organism side if killed.

### 3.14 nyx (ORGAN disassembly) -- dossiers/nyx.md
Discovery Approach: disassemble external and Prometheus machinery into
  "ORGAN" mechanisms with ancestry, for transplant into the SFE ecology.
Brick Walls:
  - Nothing has transferred: 0 organs consumed, 0 mechanisms survived a
    transplant; the one organ a consumer tried came back "interface
    insufficient".
  - Reading, not running: 542/549 organs rest on source reading alone;
    utility is UNKNOWN on 546; "portability YES" is asserted on 533
    without a test. Recent cuts are first-read by a same-family model.
  - No composition: 1/485 accepted organs is a composition operator; the
    665 links are untyped and hand-written.
Seed Viability: SALVAGE_COMPONENT (a reference library, not a substrate).
  Keep the frozen-blind mechanism packets with an outside adjudicator (2/7
  predictions falsified, i.e. the instrument can say no), the knife rules
  K1-K10 and the transplant-gated mechanism ledger.
Evolutionary Roadmap: implement 5 accepted organs as typed primitives and
  give them, and a size-matched random primitive set, to search on W2_K2,
  >= 30 seeds. KILL: no separation, or ablating the organ does not remove
  the gain. Organs that pass become rung material for Part 5.

### 3.15 Aphrodite engine + BETA-02 -- dossiers/roles__Aphrodite__engine.md
Discovery Approach: brute-force enumeration of programs in one hard-coded
  left-fold template (one integer accumulator) to reach hidden target
  "families". A least-general-generalisation step lifts a one-hole
  template from solved bodies into a library that reorders the search
  (fair.py:60-61: every library has "identical expressive power").
Brick Walls:
  - One level only: R8 = NO. Inheriting the learned library cut the next
    generation's own learning from 56 families (pristine) to 10.
    Inheritance substitutes for improvement.
  - Brute-force reachability: the 1M budget covers 0.44% of the base
    grammar's 2.3e8 programs and 0.010% of the depth-3 world's 9.7e9.
    About 7 genuinely non-additive tasks per 10,500 draws.
  - "Memorisation exclusion" deletes the lookup-table candidate from the
    selector's menu (b02.py:139-142). It is a hand-coded prefer-the-
    generalisation bias, not a mechanism. g11@O10 re-derives the additive
    templates (acc+{H} 10x, acc-{H} 7x, {H}+v 3x). The original selector
    picked the lookup table in 11/22 seeds.
Seed Viability: SALVAGE_COMPONENT, LIVE LEAD. Keep the transplant
  membrane, the fair library comparison under identical search order, and
  grouping by whole-program behaviour before generalising (a17.py:396-420).
  The R8 protocol (does inheritance enable or substitute?) is the single
  most important second-order test in the fleet and should be standard.
Evolutionary Roadmap: rerun R8 with each accepted template promoted to a
  TYPED PRIMITIVE and acceptance by description length (MDL), >= 20 paired
  unseen seeds. KILL: no gain over a pristine start (one-sided p >= 0.05
  or sum <= 0) AND abstraction depth 1 in >= 90% of seeds. Then retire the
  fold language and carry the instruments over. This is the DreamCoder
  question asked honestly; it is W1 escape (b) on symbolic programs.

### 3.16 incubation + incubation_d (D-VM) -- dossiers/incubation.md
Discovery Approach: an executable symbolic learning substrate. Does a
  composition learned in one world become a reusable entity that
  cheapens related worlds? incubation_d adds a stack machine (D-VM) where
  transforms are themselves data.
Brick Walls:
  - The menu is the ceiling: 336 words / 634 search programs / 11,050
    groupings, all designer-made; search programs grow as 634^k (about
    2.5e8 at three stages).
  - Planted answers: the worlds were rebuilt 2-5 times until each held the
    answer. Pattern support was 30/30 because the tasks were filtered that
    way. The one working grouping is 1 of 11,050.
  - D-VM desert: 0.037% of length-5 meta-programs are distinct, and a
    transform of a transform needs about 3.8e10 sequences. Its worlds and
    learners were never built.
Seed Viability: SALVAGE_COMPONENT, dead end as built. Keep the control-
  and-census protocol and the D-VM idea (a learned transform is data that
  a later transform can edit), which is the right shape for W3.
Evolutionary Roadmap: an MDL-compression learner whose search order comes
  from its own admitted transforms (M1) against a fixed-order baseline
  (M0), on worlds generated by INDEPENDENTLY written code. KILL: the
  M1/M0 acquisition-cost CI lower bound is >= 0.5, or every admitted
  transform is a single edit, or none builds on an earlier one.

### 3.17 alien_circuitry -- dossiers/alien_circuitry.md
Discovery Approach: asks whether the decision-relevant structure of a huge
  inference frontier occupies a small space that can replace search,
  measured against exact answer tables.
Brick Walls:
  - Oracle-first: the "compression" is a symmetry quotient read off the
    full shortest-distance table (ac01d/v2/orbit_navigation.py:124-143).
    The table is 2.1e9 entries at size 8 and 5.1e12 at size 10; size-7
    runs were already killed by host memory. The receipt itself says "C5
    was therefore not alien circuitry" (AC01D_V2_RECEIPT.md:16; verified).
  - No non-trivial structure in any enumerable world: lookahead exposes
    every trap, or the known invariant explains everything.
  - Path-macros ranked worst of 84 macro sets, and the baseline moves
    about 2x with tie-break order.
Seed Viability: SALVAGE_COMPONENT, dead end as built. Keep the gate stack
  (exact trap map, lookahead, residual after the known invariant, leakage
  check) and verify-symmetry-then-quotient.
Evolutionary Roadmap: invariant discovery WITHOUT the table, on a 387M-
  state world with 1e7 expansions and held-out target types. KILL: < 95%
  of the known pruning recovered, or held-out cost > 10x a hand-coded
  searcher.

### 3.18 agent_d2..d5_blind (August D-series) -- dossiers/agent_d_series.md
Discovery Approach: blind, preregistered experiments on bases,
  accessibility geometry and history-driven findability.
Brick Walls: D-2..D-4 have no learner. D-5's history advantage (M1 80 vs
  M0c 51 solves of 290; +10.95 pp, p 0.0007) is a warm-start cache:
  shuffled history keeps 100% of it (77 solves), and there is no
  developmental trend and no held-out transfer (P5 +5 pp, p 0.26).
  Programs up to the useful size number about 1.38e30 against 9.05e5
  explored. External tasks were 0/48 findable at 10k evaluations. D-3's
  results/ folder is gitignored, so its gate table exists only in prose.
Seed Viability: SALVAGE_COMPONENT (method only). Lessons: separate
  expressible / reachable / findable; count distinct behaviours, not
  programs; require shuffled-history and random-library ablations for any
  "learning" claim. Make those ablations fleet standard.
Evolutionary Roadmap: none for these engines. Fold the ablations into the
  Part 5 protocol.

### 3.19 theseus/synth -- dossiers/theseus__synth.md
Discovery Approach: compile 95 human G0 concepts into primitive rule
  programs, collide them k-way without an LLM, and test whether deep
  descendants reach behaviour no other arm reaches.
Brick Walls:
  - Matches random: the key test came out FAIL, then INDETERMINATE on
    replication (51 programs per arm). The deep arm's distance advantage
    over random is +0.32 [-0.33, 0.76], and random looks MORE novel on
    the mechanistic (8/10 vs 12/20 unexplained) and lens (12/60 vs 5/60)
    rulers.
  - Flat behaviour space: 34 summary numbers binned; 160 of 2,401 bins
    filled by 255 programs; 63-65% of "weird" random programs pass the
    viability gate, so novelty search rewards noise.
  - Degenerate seeds: 14/95 concepts (incl. type theory, causal inference,
    abductive reasoning, program synthesis) compile to the same 2-rule
    program; zero input channels; the concept tensor is a frozen random
    projection whose refresh is never called. Structure space about 1e80,
    with about 2,648 programs per run.
Seed Viability: SALVAGE_COMPONENT, dead end as a substrate. Keep the
  control harness (hidden-known, execution-neutral, matched-random,
  rule-destroyed twins, lineage integrity).
Evolutionary Roadmap: the planted-structure test (the seat's THESEUS-23
  as a gate). 50 programs requiring a 3-step recursive construction vs 50
  matched random. KILL the ecology if no ruler separates them with AUC >=
  0.75. Under 1 CPU-hour, so run it first.

### 3.20 tyche (evolved perceptual lenses) -- dossiers/tyche.md
Discovery Approach: GP over a 27-op DSL evolves "lenses" (features)
  against dark residuals and keeps a lens only for measured marginal
  consequence. A depth-4 decision tree reads the lenses.
Brick Walls:
  - Interaction order 3: a 3-way signal is a 128^-3 (about 4.8e-7)
    needle; v1's 2.5e4 births give about 0.012 expected hits; observed
    order-3 solves across v0-v2: 0.
  - Law switches: adaptation in 1-2 of 72 cells within 30 generations;
    lenses carrying all the parts of the new law are at most 0.0006 of
    the population.
  - The organism does the reasoning: xor and parity are solved by the
    decision tree or lookup table; a "coalition" is column concatenation;
    the 27-op vocabulary mirrors the world generator. The real target,
    122 catalogued residuals from other seats, has had 0 runs.
Seed Viability: SALVAGE_COMPONENT, LIVE LEAD (as an instrument for the
  other engines more than as a substrate). Its measurement stack is the
  best reasoning-circuit DETECTOR in the fleet: a paired marginal-gain
  ruler with twin and keyed-hash negative worlds (0 false gradients), a
  causality audit (cheat caught at z = 54.9), and per-world certificates
  of how many inputs must be seen together.
Evolutionary Roadmap: a parity-k ladder (k = 2, 3, 4) with only a linear
  readout, comparing lexicase selection, a synergy-scored beam search and
  library learning. KILL lens evolution if no arm solves k = 3 in >= 5/10
  seeds. Then run it on the 122 real residuals; that is its reason to
  exist.

### 3.21 herakles/evca (+ HISTORICAL_COLLIDER_V0) -- dossiers/herakles__evca.md
Discovery Approach: a pinned CA executor that reproduces the classic
  evolved-CA density-classification organisms (Das 1995, ABK 1996,
  Juille-Pollack 1998) as hashed specimens. There is NO GA/GP/coevolution
  code in herakles/; the GA reconstruction is parked on the operator.
Brick Walls:
  - Ceiling and space: the radius-3 rule space is 2^128 (about 3.4e38);
    the historical GA searched about 8.8e-33 of it; Prometheus has
    searched none. Thirty years and three search methods moved density
    accuracy from 0.769 to about 0.86 (OBSERVED reproductions). The later
    ~0.89 result and the Land-Belew impossibility of 1.0 are LITERATURE
    recalled by the worker, not repo files; verify before quoting.
  - No signal from random: 40/40 random tables score 0 on density, and
    every held organism scores 0 on synchronisation.
  - Noise: fitness SE at 100 initial conditions is 0.04, above the 0.033
    gap between methods. The throughput estimate is about 1000x too
    optimistic. The streaming wrapper has 0/63,488 non-zero features, and
    there is no domain/particle detector (the one compositional structure
    the field found). The census label "C1-e synchronisation" is wrong.
Seed Viability: SALVAGE_COMPONENT. Keep the pinned executor, scoring with
  measured random floors, and the symmetry checker. The inherited lesson
  is the point: evolved CA computation hit a ceiling in the 1990s, and the
  only composable structure found was particles. Any Prometheus soup
  should measure for particle-like carriers before claiming circuits.
Evolutionary Roadmap: a particle-reuse transfer test (synchronisation
  evolved from particle-based density elites vs block-expanding elites vs
  random tables). KILL: particle elites give < 1.5x speedup. Build the
  particle detector first; it also applies to Aether.

### 3.22 forge lineage (forge, agents/hephaestus, agents/nous, hecate) -- the cosplay control -- dossiers/forge_lineage.md
Discovery Approach: LLM-written Python "reasoning tools" generated from
  Nous concept triples, validated against a trap battery, tiered so that
  each tier's tools become the next tier's primitives. Hecate escalates
  the ore to ENGINE / FOSSIL / REJECT.
Brick Walls:
  - Generator collapse: 95.7% of 1,502 tools use the same zlib
    compression-distance scorer; 96.2% of v5 function lines are
    duplicated across files. Tools regex-match trap wording ("bat and
    ball") or return the battery's fixed answer "No".
  - A constant beats the ruler: always picking option index 1 scores
    75/186, against 74 for the best tool and 73 for plain NCD (SE about
    0.036); at least 14 of 28 trap generators always produce the same
    answer. The "frozen" pass threshold was lowered from 0.50 to 0.40
    after it rejected everything.
  - Tiers do not compose: 0/10 higher-tier tools import a forged lower-
    tier tool; 3 tools passed with zero load-bearing primitives.
  - Hecate: of 16 programs, 14 PARK, 1 PROBING, 1 SPECULATIVE; ENGINE,
    FOSSIL and REJECT are all 0; none of 5 signals survived the first
    falsification pass.
Seed Viability: SALVAGE_COMPONENT. This is what cosplay looks like when
  measured, and it is the control the other engines should be compared
  against. Keep the knockout-ablation protocol, Hecate's probe discipline
  and the 25 hand-written primitives as a typed starting vocabulary.
Evolutionary Roadmap: DreamCoder-style library learning over those 25
  primitives on held-out tasks where the answer must be computed and
  constant baselines sit at chance. KILL: zero learned abstractions
  survive knockout after 5 cycles. (This overlaps 3.15; run one, not two.)

----------------------------------------------------------------------
## PART 4. What is worth salvaging, ranked

The program's real asset is a CERTIFICATION STACK assembled by accident
across seats. Ranked by how much it would matter if a real circuit arose:

  1. Cosmos C3 P1/P2 certificate: decode state AND swap state to change
     behaviour. "Is this a working memory?"
  2. Tyche marginal-gain ruler + causality audit + interaction-order
     certificate. "Does this feature carry an order-k interaction?"
  3. Crius reuse assay (RELAY, A-J controls, neutral-edit rescoring).
     "Did a stored mechanism make later learning cheaper?"
  4. Aphrodite R8 protocol. "Does inherited abstraction ENABLE further
     abstraction, or substitute for it?" The second-order test.
  5. Ananke counterfactual swap + C2A "cannot find vs cannot do".
  6. Aether twin-world / counterfactual-parent / value-provenance stack.
  7. D-series and z80atlas ablations: shuffled history, random library,
     YOKED / SHUFFLED / RANDOM_REWARD reward controls.
  8. Ludus exact value-retention ruler; alien_circuitry gate stack;
     Primordial P-11 and CVT-R heredity certificates.
  9. Provenance infrastructure: SFE sealed predictions, sigma_kernel
     symbol record (after the race fix), Odysseus exact replay.

Recommendation: consolidate 1-7 into ONE fleet ruler package with a
common interface (organism trace in, certificate out) and a planted
positive control and a cheat control per certificate. Today each lives
inside the engine that invented it.

----------------------------------------------------------------------
## PART 5. The program-level evolutionary roadmap

The diagnosis is shared, so the roadmap is shared. Twenty-five separate
roadmaps would mean twenty-five more walls of the same wall.

STEP 1 -- Build the Composition Ladder (one world family, exact oracles).
  Rungs where rung k REQUIRES a k-part mechanism whose parts are
  individually fitness-neutral, with the oracle's value of information
  positive at every rung (fixes W2) and partial credit that is structured
  (fixes W4):
      R0  latch (1 held bit)                    -- every engine already passes
      R1  relay / hold two values (W2_K2)       -- SFE 0/395
      R2  bit-conditioned mapping (FLIP, XOR)   -- Ananke 0/290
      R3  parity-3 / order-3 interaction        -- Tyche 0
      R4  reuse of an R1-R3 unit in a new task  -- Crius 0/475,728; Aphrodite R8 NO
  Sources already exist: the Ensorain hidden-state families, Ludus FOUNDRY
  with the m-knob, the PTE task cells, Tyche's parity worlds. Gate every
  rung with an MDL check so no rung is admissible if a short formula
  solves it (the Nim lesson).

STEP 2 -- Test the three escapes from W1, each in the substrate already
  closest to it, under one protocol (the Part 4 rulers, preregistered,
  with YOKED and shuffled controls):
      E-a  structured credit / stepping stones   z80atlas COND_ONE; Ares parity-k
      E-b  modularity: duplicate + PROMOTE a     Ananke block-dup FLIP;
           solved unit to a typed primitive      Crius SMOOTH; Aphrodite R8-typed+MDL
      E-c  lifetime plasticity                   Moonshot plastic arm;
                                                 Odysseus three-factor
  The common decisive readout is the highest rung reached at >= 5/32
  seeds at 4x budget, certified by the ruler package (not by fitness).

STEP 3 -- Decision rule (freeze before running):
  - If E-b reaches R2 and R4 (a promoted unit is reused) in any
    substrate: that is the seed. Scale the PROMOTION OPERATOR, not the
    substrate: a typed graph-rewriting or combinator genome where a
    certified sub-graph becomes a new node type, with MDL-weighted
    selection and per-module credit. Port it to the other substrates as
    a portability test.
  - If only E-c reaches R2+: the seed is learning within a lifetime, and
    the "evolve the mechanism" framing gives way to "evolve the learner"
    (a meta-learning ecology). Evolution then selects plasticity rules,
    not circuits.
  - If only E-a works: progress is bought by hand-designed curricula. Say
    so plainly; that is designed reasoning with extra steps.
  - If NONE reaches R2 in any substrate: at this scale, "grow, not
    design" does not reach compositional reasoning without a designed
    abstraction mechanism. Pivot to designed-primitive library learning
    under the existing rulers, and keep the soups as phenomenon generators
    only.

STEP 4 -- Multi-agent dynamics, only after a seed exists. Red-Queen
  coevolution (organism vs world generator, as in POET / the Moonshot
  M5 candidate) is the obvious amplifier for an open-ended ladder, but
  coevolving a world against an organism that cannot pass R2 only
  generates harder deserts. Do not open M5 before Step 3 has a positive
  branch.

WHAT TO STOP (recommendations, not rulings):
  - New substrates of the current shape (flat genome, point mutation,
    scalar fitness, no promotion operator). Seven independent 0s predict
    the eighth.
  - New world grammars without an MDL / value-of-information gate.
  - Custody and provenance growth in seats whose organisms have not
    passed R1. Instruments should follow a signal, not precede it by 5:1.
  - Moonshot cluster spend (M4 commodity fabric) before the CPU pilot in
    3.5 exists; the cluster has nothing scientific to run.
  - Claiming "learning" without the shuffled-history and random-library
    ablations (D-5's lesson).

THE SINGLE MOST INFORMATIVE NEXT RUN, if only one: the Ananke FLIP
  representation test (3.4). It is cheap and already designed, with the
  cleanest baseline in the fleet (0/290). It tests E-b directly, and its
  outcome predicts whether Crius SMOOTH and Aphrodite R8-typed are worth
  running. The cheapest is Theseus's planted-structure test (3.19, under
  1 CPU-hour); run it in parallel.

----------------------------------------------------------------------
## PART 6. Defects found in passing (routed to owners, not fixed)

  D1  sigma_kernel capability double-spend race under Postgres
      (sigma_kernel.py:833/837 then :899, :995, :1261, :1449). Confirmed
      by reading; a race test has NOT been run. Owner: Techne.
  D2  ares sweep_c2/gates.txt shows the uncorrected "GATE C OPEN"; champion
      selection on the held-out set. Owner: Ares.
  D3  agent_d3_blind/results/ is untracked (blanket .gitignore), so the D-3
      gate table is prose-only. Owner: Archaeon (gitignore) / historical.
  D4  forge pass threshold lowered 0.50 -> 0.40 after it rejected every
      tool. Historical; recorded so no one cites forge pass counts.
  D5  Census label "C1-e synchronisation" for herakles/evca is wrong (C1-e
      is the density reproduction). Owner: Achilles (census) / Herakles.
  D6  Moonshot: the review's unpaid-write defect is visible at
      wforge world.py:216-224. Owner: Themis.
  D7  Large run rows for z80atlas / ares / crius exist only on M2,
      referenced by hash; the E-003 BEE verdict is on a branch, not main.

----------------------------------------------------------------------
## PART 7. Limits of this audit, and what would falsify it

- Method: 8 parallel read-only workers wrote the dossiers. Some delegated
  further (Ensorain, Ludus, Ares, Crius, incubation, alien_circuitry, the
  D-series, Tyche, Herakles, forge). Hestia spot-checked the key
  citations of every delegated dossier (all checked lines held; one path
  ambiguity and one blurred summary number were found, and the dossier
  text was correct). Hestia did not re-derive every number.
- No engine was run. Every "kill" above is a designed test, not a
  result. Numbers marked CLAIMED in the dossiers rest on seat prose or
  off-repo rows.
- Same-family bias: the auditor shares a model family with most engine
  authors, and the convergence of 24 verdicts on SALVAGE_COMPONENT is
  itself suspicious. The rubric's SALVAGE category may be too easy to
  enter: almost every engine has SOME instrument. Part 1's LIVE LEAD /
  dead end split is the attempt to make the verdicts discriminate.
- W1's theoretical support (Valiant / Feldman) and the evolved-CA
  literature figures (0.89, Land-Belew) are recalled from memory, not
  verified in this pass.
- WHAT WOULD FALSIFY THIS REPORT: any engine reaching R2 (FLIP / XOR /
  parity-3 / two-value hold) from a random start under its current
  representation and blind mutation, with a certified mechanism. That
  would refute W1 as stated, and the "stop" list with it. Second: an
  independent reviewer (different model family or a human) finding a
  dossier's cited line does not say what is claimed.
- Requested: an adversarial review of Parts 0, 2 and 5 by a different
  model family, and by Elenchus on commission.
