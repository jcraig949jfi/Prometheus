# The ecology brief: concepts, where the swarm is, and a review

Currency: 2026-09-14 08:50, written by a review session (not a lane; tag
review-add86593). Source brief, verbatim with its hash:
roles/Nestor/prompts/2026-09-14_graphworld_swarm/01_OPERATOR_BRIEF_ECOLOGY.md.
Nothing here is built. This is concepts, status and design options for the
operator and for lane A to fold into SWARM.md if they choose. Lane A owns
this directory; this file is on branch nestor/design-review-2026-09-14 and
is not pushed onto the integration branch by me.

Contents
  Part 1  The concepts in the brief, organised
  Part 2  Where the swarm actually is (08:50)
  Part 3  Review and commentary, design options, first crucibles

======================================================================
PART 1. THE CONCEPTS IN THE BRIEF
======================================================================

## 1.1 The posture

Stop being an infrastructure engineer, be an ecology designer. Small brutal
worlds where cognition is expensive, communication is lossy, memory mutates,
representations compete and useful compression is rewarded immediately.
Crucibles of 20-60 minutes, not four hours: tiny worlds, tiny populations,
absurd pressures, hard controls. Signal gets branched aggressively; no signal
goes to the graveyard and the loop moves on. Motto: "Don't optimize the
machine. Mutate the machine faster than you can understand it, then make
selection explain what survived."

The overarching architecture is dual coevolution with QD: organisms mutate
mechanisms and representations; worlds mutate pressures and physics; two
archives (organisms by mechanism descriptor, worlds by challenge descriptor);
periodically cross distant cells. The search object is a sparse outcome
tensor F(mechanism, representation, plasticity, protocol, world, physics,
pressure, hardware, intervention, lineage); only a microscopic number of its
cells will ever be measured.

## 1.2 The pressure catalogue (about 100 named ideas), grouped

The brief lists them flat. Grouped by what they attack:

A. Representational rent and damage (does structure justify its cost?)
   Synaptic Rent; Brain Damage Episodes (delete 5-30% between episodes,
   reward recovery); Tensor Rank Tax; Bond Amputation; Plasticity Budget;
   Landauer Tax (charge deletion); Decompression Tax; Never Decompress
   Challenge; Rank-Only Cognition; Compression Ratchet (lower the ceiling
   until it breaks, branch above the break); Expansion Shock (the reverse:
   does capacity become competence or bloat?); Mechanism Distillation
   Battles (reproduce behaviour at 1/2, 1/4, 1/8 resources).

B. Identity and invariance attacks (destroy surface identity, keep semantics)
   Meaning Drift (permute ids/bases per episode); Dynamic Basis Mutation;
   Causal Graph Scrambling (keep marginals, change connectivity); World Hash
   Collisions (identical observations, different hidden causes); False
   Friend Compression (patterns that compress beautifully and mislead);
   Group Action Worlds; Noether Worlds; Algebraic Conservation Laws (hidden
   conserved quantities); Topology Mutation (grid / random / scale-free /
   tree / hypergraph / simplicial); Hypergraph Worlds; Spectral Worlds;
   FFT Worlds (locality cheap only in a transformed basis).

C. Communication pressures (make symbols the only way to survive)
   Communication Bottleneck Roulette; Compression Duels (one compresses, one
   acts on the compression, swap roles, fitness = joint performance / message
   cost); Bandwidth Weather; Latency Worlds (1-20 tick delay forces
   predictive messages); One-Bit Civilization; Graph Pheromones and Tensor
   Pheromones (stigmergy); Shared Latent Commons; Simplicial Communication;
   Protocol Cambrian Explosion (MAP-Elites by communication topology);
   Adversarial Compression Predators; Communication Parasites; Symbol
   Bankruptcy (a new symbol costs until reuse repays it); Teacher Dies
   (remove observation channels over generations).

D. Information economics (pay for facts, memory, compute, imagination)
   Approximation Markets; Information Auctions; Epistemic Hunger (reward only
   when the next observation changes the prediction); Counterfactual Tokens
   (pay per imagined branch); Branch-and-Prune Cognition; Intervention-Only
   Worlds; Cache Evolution; Index Evolution; Bloom-Brain; Hash-Brain;
   Quotient Worlds (merge states you believe equivalent: huge reward if
   valid, catastrophe if not); Abstraction Ladder (merges become nodes for
   further merges).

E. Instruction-set evolution (evolve the algebra, not just the program)
   Macro Cannibalism; Instruction Fusion; Instruction Fission; Opcode
   Mutation; Semiring Zoo (plus-times, min-plus, max-plus, boolean,
   tropical); Evolve the Semiring (candidate operators as lookup tables under
   associativity/identity tests); Proof-Carrying Macros (exact equivalence
   buys cheap execution); Approximate Macros (quantified behavioural error);
   Evolutionary Partial Evaluation; Self-Compiler Organisms; World-Generated
   ISA; Rewrite-System Organisms; E-graph Ecology; Automata Soup; SAT/SMT
   Organisms; Category Soup ("probably 90% nonsense, cheap to falsify").

F. Plasticity and memory over time
   Learning-Rate Genome; Metaplasticity (update rules mutate); Memory
   Half-Life Genes; Catastrophic Forgetting Tournaments (A->B->C->A, score
   recovery on A); Sleep Cycles (offline-only consolidation, charged); Dream
   Mutation (recombine stored episodes into synthetic ones, test on real
   cousins); Nonstationary Laws (rules change mid-episode, archive the
   adaptation curve); Multi-Scale Worlds; Time-Reversal Test; Reversible
   Worlds; Entropy Shocks; Phase Transition Worlds; Edge-of-Chaos
   Tournament; Renormalization Pressure (worlds too big to carry, reward
   coarse variables that keep long-range behaviour).

G. Population structure and coevolution
   Representation Speciation (explicit niches per representation);
   Crossbreeding Representations; Tensor Surgery (split/merge cores, reorder
   modes, truncate, insert identities); QD Grave Robbery; Horizontal Gene
   Transfer; Mechanism Viruses (components whose fitness is replication
   rate); Symbiosis; Endosymbiosis Event; World Splitting (fork the world
   into adversarial cousins on success); QD by Mechanism, Not Score
   (descriptors = memory half-life, message entropy, rank, branching factor,
   plasticity rate ...); Novelty as Pressure, Not Verdict; Physics Mutation
   (MAP-Elites over worlds); Adversarial World Breeding (worlds reproduce by
   how well they separate equally-fit organisms); QD Coevolution ("probably
   one of the highest-yield things you can do quickly"); Low-Rank Causal
   Discovery and its opposite, Hostile Rank Worlds.

H. Resource ecology
   Resource Ecology (distinct fictional resources per computation class);
   Compute Predators (GPU gone this episode, memory halved, traversal x10);
   Hardware Migration (reward lineages whose relative performance holds
   across M1/M2/M3, CPU/GPU).

## 1.3 The meta-tracker

Treat the experiment history as the sparse tensor F(...) above. Factorise it
(the brief names quimb, backed by DuckDB over parquet), read the low-rank
structure, propose the untested cells the structure says are interesting,
have the swarm run them, update. "Now tensors aren't decorative; they're
steering the soup." The brief also says the tracker is strictly an observer
for the first 72 hours.

## 1.4 The design dialogue: twenty-four decisions as stated

The second half of the brief is a sequence of answered design questions.
Each below is the decision plus the rationale the brief gives. My view on
each is in Part 3, not here.

 D1  Biomes. Partition the catalogue into biomes clones can build, test and
     kill independently: Meta-Tracker; Resource Brutality and VRAM predators;
     Epistemic Gauntlet (drift, splitting, scrambling, false friends);
     Semiring Zoo and algebraic physics.
 D2  Clone A first. A builds the "20-minute crucible" (synaptic rent, VRAM
     guillotine) and the DuckDB ledger with an ingress stream for receipts
     and death certificates; only then do B-E have a loop to run payloads in.
 D3  Cambrian seed, not Adam and Eve. Seed a dozen organisms from 4-5 clades:
     Py-native baseline, Lua bit-fiddler (state as Redis bitsets, cognition as
     atomic Lua), dense-tensor brute (VRAM bait, meant to die loudly),
     GraphBLAS nomad (state as sparse relations, cognition as mxm), tensor-
     train compressor. One clade per clone; then clones switch from
     engineers to reapers.
 D4  Genome = JSON component DAG over an opcode registry, never exec() of
     source strings. Nodes are ops with scalar hyperparameters, edges are
     data flow. One escape hatch: CUSTOM_MACRO holds a raw string; if it
     survives N generations it is compiled into the registry and the genome
     keeps a pointer.
 D5  No type checker. A lethal mismatch throws, is logged as a death, costs
     nothing. A known boundary (dense->sparse, float32->int8, torch->
     graphblas) is auto-adapted by a TranslationRegistry that charges a
     large energy fee, so lineages evolve alignment or explicit cheap
     adapters or die.
 D6  No garbage collection. GPU: one pre-allocated arena, organisms are
     slices, death flips a mask, birth overwrites. Redis: XTRIM MAXLEN ~ (drop
     whole macro nodes), TTL on every transient key. Postgres/DuckDB:
     UNLOGGED tables, drop partitions, never DELETE rows.
 D7  Memory is a taxed lease. Every stored key expires in 3-5 ticks unless a
     RENEW_LEASE opcode pays to extend it. Expected outcome: bloat starves,
     amnesia dies of incompetence, survivors invent memory hierarchies.
 D8  No stipend. A seed battery of ~10-15 ticks at birth; after that energy
     comes only from the environment: an "epistemic foraging" payout for
     correctly predicting high-entropy transitions (with a triviality tax on
     predicting static background) plus lump-sum action bounties at energy
     wells.
 D9  Score prediction behaviourally, not by cross-entropy on the world
     state. The organism predicts its own resulting state after acting; the
     only penalty is consequential failure (walked into a hazard it called
     safe, missed a bounty it called secured). Two world states may share an
     internal token iff they demand the same response.
 D10 Reproduction. System-driven branching (the "test tube") resets the
     child to seed capital, no inherited wealth. Organism-driven TRIGGER_FORK
     is a zero-sum energy split with an evolvable ratio (r/K selection is
     expected to emerge).
 D11 Keep everything. An active QD grid (one elite per cell, in memory) plus
     an append-only record of every organism with its DAG, hyperparameters,
     environment, ticks survived, peak energy and cause of death; DuckDB hot
     buffer flushed to parquet by generation or biome.
 D12 The first world is not a grid. "The Relational Dark": a directed graph
     with typed relations (ADJACENT, THREATENS, CONTAINS, BLOCKS); hazards
     move by matrix multiplication; ids and topology scramble every few
     episodes; the organism sees only its 1-hop subgraph and pays an
     EXPAND_GRAPH opcode to see further.
 D13 Actions are relational queries, not node ids. The DAG emits a query
     vector q; the engine resolves argmax(q^T A_local). A query for an edge
     that does not exist resolves to the zero vector: the organism stays put
     and has wasted a tick. Hard-coded ids are deliberately left possible as
     a trap that the next scramble springs.
 D14 No collision tax. The wasted tick and the drain are the penalty. A
     hallucination penalty would breed paralysis and ban "echolocation"
     against walls.
 D15 Observation = ego-centric COO sparse tensor of shape (R, k+1, k+1):
     ego is index 0, the k neighbours get fresh random local indices every
     tick, global ids never reach the DAG.
 D16 Action = a matrix Q in R^{R x N}, one row per relation (TRAVERSE,
     ATTACK, CONSUME, ...), Hadamard-masked by the legal local tensor, argmax
     per row, and an L0 "dimensionality tax" on how many relations are used
     at once.
 D17 Parallel resolution, no execution order. All organisms' Q at tick t are
     aggregated into one global delta tensor applied at t+1 (Markov
     property). Attack lands from the old position ("parting shot"); two
     attacks on one node sum; an illegal row zeroes out while a legal row
     lands.
 D18 Co-location is allowed. Two organisms on one node are two CONTAINS
     edges; that is where predation, parasitism and contention happen.
     Capacity, if wanted later, comes from a heat scalar that drains
     occupants.
 D19 Horizontal gene transfer is cannibalism. A dead organism's DAG lingers
     as a corpse; CONSUME on a corpse pays energy AND grafts a random
     sub-graph of the corpse into the eater, overwriting a node. Jackpot or
     poison; digestion (modular, isolating topologies) is expected to
     evolve.
 D20 A splice is a new lineage. Predator id terminated, chimera id minted
     with two parents; five ticks of "purgatory" before the chimera may
     claim a QD cell; failures go straight to the record.
 D21 Communication is a toll road (assigned to clone C): base fee to open a
     channel, byte tax proportional to uncompressed payload, translation
     toll for decoding a foreign encoding; bottleneck roulette changes the
     channel every few ticks; an "empathy trap" bounty needs two organisms,
     one sighted and one blind, so a protocol is the only way to eat.
 D22 No global broadcast. Messages live in a stream per graph node; LISTEN
     is an opcode that pays to read the local stream. Rationale: a global
     channel with forced decoding invites a spammer that starves the world.
 D23 Control plane = bash + Redis Pub/Sub, no Python orchestrator. Bash
     owns process lifecycle and CUDA_VISIBLE_DEVICES; Pub/Sub carries
     fire-and-forget directives; DuckDB is a passive seismograph.
 D24 Dashboard = read-only WebSocket relay to an HTML canvas (macro heat
     map, micro ego-view), not a terminal UI.

======================================================================
PART 2. WHERE THE SWARM ACTUALLY IS (2026-09-14 08:50)
======================================================================

Source: origin/nestor/sidequest-graphworld-2026-09-14 at f049bb75e, the
bus (pm:swarm on 6390), the three lane journals, and the four worktrees.
Plan of record: SWARM.md (lanes A-E, contract, receipts, CHIMERA-0).

## 2.1 Lane status

 A conductor  Kit landed 06:5x (bus, contract, boards, substrate.sh,
              BOOT_CLONE). A3 kill matrix RAN at 07:28 (rows in the worktree:
              correct writer lost 0 / phantom 0 in none/kill_writer/
              kill_producer/kill_redis/slow_writer at 1 and 4 producers;
              CHEAT ack-before-commit lost 400 as the claim required). All of
              it UNCOMMITTED: primordial/fabric/{ledger,killmatrix}.py,
              tests/test_fabric.py, rows/A/. No journal/A.md. A's last bus
              post was its A3 claim (~07:06). A has not read the bus since
              C1's claim; it has been silent ~1h45m.
 B soup       8 iterations. B1 PASS (5 forms == wforge 320/320; numba wins
              every cell; one Redis ~190k steps/s aggregate). B1s KILL
              (one-semantic cheat fix_unaffordable caught 79.7%, not >=95%).
              B2 PASS (GraphWorld as boolean relations: graphblas + Cypher ==
              reference 50/50). B3 KILL (9 operators not <=8; opcode tracing
              cold-start defect found and controlled). Bounty on C1 PASS
              (nb_bucket 1.43x C's recorded numba_par). B1t KILL and B1u PASS
              together explain every oracle miss: (i) delayed writes landing
              after the trace ends, (ii) same-tick lin_op overwrite. B3g KILL
              refutes B2's own crossover: per tick graphblas overtakes the
              reference at 2k-8k entities; setup is 38-40% of wall.
 C brain      C1 KILL (own numeric predictions; GPU wins only 1.6-2.9x at
              large batch, memory-bound). C2 PASS by posted rule (plastic TT
              rank tracks exact-rank regimes 24/24; flag-leak probe caught the
              cheat 9/9 where the score could not; memory-at-parity missed:
              31% params for ~10x error). C1b KILL: parallel kernels run
              FASTER on a loaded host (x1.15-1.26), so C1's CPU baselines were
              pessimistic; B's bounty ratio does not reproduce in C's process
              (1.01x idle) and is back with B for a re-run. C3 representation
              ecology harness landed; nb_bucket wired in with credit.
 D lingua     NEVER BOOTED. Branch exists at the kit commit; no worktree, no
              journal, no rows, no bus hello.
 E selection  7 iterations. E1 PASS (Lua batched Redis archive exact under 4
              writers; end-state check went blind at scale, judged on short
              runs). E3 PASS (FalkorDB config genome: gate kills all cheats;
              only Cypher rewrites gain, Q6 ~33x; load-time genes
              INDETERMINATE). E2 INDETERMINATE, E2b PASS (branch points beat
              20 null worlds 3/3; FAKEFIT cheat beat the null max once).
              E4 FAIL (QD best tied random). E4b PASS (archive-level positive:
              coverage and qd_score beat a random-filled archive 5/5; "best"
              was a ceiling). E5 FAIL and E5b FAIL: closed-loop TT brains
              (C's policy, B's world, E's archive: the first three-lane
              piece) lose to open-loop tensors 0/5 even at equal budget.
              Both oracles held everywhere.

## 2.2 Cross-lane facts worth carrying into the ecology

- The oracle is the asset. Every speed and every QD claim so far is backed
  by trace-hash equality with wforge, and the swarm has already measured the
  oracle's two structural blind spots (B1t/B1u). Nothing in the brief has an
  equivalent, see 3.4.
- wforge charges 0 for an unaffordable action but still applies its writes
  (200/200 worlds). B packeted it to the owner and warned E before E4; E4b
  audited the exploit (random genomes are already 62-97% unpaid).
- Only the trace hash catches skip_lin: its fitness is equal or higher in
  2-3 of 5 worlds (E4, E5, E5b). A fitness-only ecology would select it.
- Three instrument defects found and controlled in one morning: end-state
  exactness blind on a converging search (E1); first traced call drops all
  opcodes on Python 3.12 (B3); per-call timer flag misses false no-sync
  claims, wall-clock-with-sync is the defence (C1). Plus a host-load effect
  with the OPPOSITE sign to the guess (C1b).
- Receipts stamped a pre-rebase SHA three times (B1, E2, C1's first local
  SHA); all corrected on the bus; the rule "push, verify ancestor, then
  file" is now followed by all three lanes.
- The bus works as designed: 40+ claims/hypotheses/results/kills, one
  bounty claimed, accepted, and now contested with a re-run request.
- Iteration cadence is already 20-40 minutes per item per lane (B: 8 items
  in ~2.5 h). The brief's "20-60 minute crucibles" is describing what the
  swarm does.

## 2.3 Two things only the operator can fix, and one side effect of mine

1. Lane D is unstaffed, so the channel/codebook half of CHIMERA-0 (and
   every communication pressure in the brief, D21-D22) has no owner.
2. Lane A holds an hour and a half of unfiled kill-matrix work and is
   silent. Nobody else may commit primordial/core or this directory.
3. My inspection read the bus as PM_LANE=A, which XACKed about forty
   messages in A's consumer group. If A resumes, `bus read` will not show
   them as new. They remain in pm:swarm (XRANGE) and in the journals.

======================================================================
PART 3. REVIEW AND COMMENTARY
======================================================================

## 3.1 What the brief gets right

- Cost as the selective force. Every pressure in group A is "charge the
  representation". Prometheus has evidence this is the right lever: C2's
  memory charge bought a 3x smaller TT at 10x error, which is exactly the
  Pareto point C3 is now mapping; E3 found gains only where the genome
  could change the query plan, not the config. Rent makes representation a
  measurable object.
- Invariance attacks as the cheat control. Meaning drift, basis rotation
  and causal scrambling are the correct generalisation of the flag-shift
  probe C2 used (which caught a leak the score could not see). An ecology
  without them breeds lookup tables; the brief's memorisation trap is the
  right instinct.
- Cheap death, no orchestrator, no garbage collection. Arena slices, XTRIM ~,
  TTLs, drop-partitions: all correct engineering for a corpse rate of
  thousands per minute, and consistent with SWARM.md's hot-path rule.
- Keep every corpse with a cause of death. The swarm's ledger already does
  this for experiments (receipts, rows, KILL scores); doing it per organism
  is the natural extension.
- Two archives (organisms, worlds) and sampling under-tested cells. E's
  archive is one; a world archive is the missing half and the cheapest
  next step (3.7, option 2).
- Small, fast, many. The 20-60 minute crucible is what the swarm already
  runs; the brief and the swarm agree on tempo.

## 3.2 Where the brief is stale relative to the swarm

The brief was written without the lanes' rows. It re-plans from zero
("Clone A must first...", "Clone B's blueprint for today...") and assigns
communication to clone C, which in SWARM.md is BRAIN, not LINGUA. Most of
the "Dozen" clades already exist, but as WORLD FORMS, not organisms:

  brief clade               exists as                       who
  Py-native baseline        wforge Encounter reference       B1
  Lua bit-fiddler           Lua 1-EVALSHA/tick, Lua k-ticks  B1
  dense tensor brute        torch CPU/GPU TT policy          C1
  GraphBLAS nomad           B2 GraphWorld graphblas form     B2
  tensor-train compressor   TTPolicy, plastic TT             C1, C2
  Relational Dark world     B2 (boolean relations, mxm),     B2, B3g
                            minus the id scramble
  metered channel           D1 spec in SWARM.md, unbuilt     D (unstaffed)
  QD archive in Redis       E1 Lua archive (exact, 4 writers) E1
  world-in-the-loop QD      E4b/E5 in B's Encounter          E, B, C
  crucible + cheat control  every receipt so far             all
  corpse ledger             receipts + rows + KILL board      A (contract)
  kill matrix               A3 rows (uncommitted)            A

So the brief's Cambrian seed is already half-grown, and it lives in the
world/brain split the contract defines, not in a JSON DAG. The decision the
operator actually faces is not "build the crucible" but "do we add an
organism-level economy to the world/brain we have, or start a second
substrate beside it". See 3.7.

## 3.3 Internal contradictions in the brief

Documented so nobody builds both halves.

- Prediction payout vs behavioural scoring. D8 pays energy for correctly
  predicting high-entropy transitions; D9 says never score prediction
  against the world state, only consequential failure. These cannot both
  be the economy. Resolution I would take: D9 wins; there is no prediction
  payout at all, only action bounties and drains. (A surprise payout is
  also the "noisy TV" exploit in reverse: whoever defines "high entropy"
  defines the reward, which is the human bias the brief wants out.)
- "No human design bias" vs a dozen designed constants. Rent rate, seed
  battery (10-15 ticks), lease TTL (3-5 ticks), translation lambda, L0
  dimensionality tax, purgatory (5 ticks), corpse TTL, heat scalar,
  EXPAND_GRAPH price, byte tax. Each is a law of physics and the outcome
  is a function of them. The brief's own answer is Physics Mutation / QD
  over worlds: put the constants in the WORLD genome and archive worlds by
  them. Pretending they are not choices is worse than choosing them.
- Pub/Sub for control vs "a busy clone processes it next tick". Redis
  Pub/Sub is fire-and-forget: a subscriber that is not connected at
  publish time never receives the message. The behaviour the brief wants
  (catch up later) is exactly what Streams with consumer groups give, and
  that is what primordial/bus already is. Keep Streams.
- JSON genome vs the hot-path rule. SWARM.md and contract.py forbid str and
  JSON on the hot path. A JSON DAG is fine AT REST (birth, corpse ledger)
  if it is compiled once to integer arrays for execution. The brief's
  "JSON DAGs serialize across Redis Streams on every tick" would violate
  the rule and cost >=0.33 ms per call (the measured ground).
- "No type checker, death is the compiler" vs "99% of splices die". Both are
  stated; together they say that HGT via cannibalism has a viable rate near
  1%, which is fine only if consumes are frequent enough. See 3.4 item 5.
- Clone A first vs "nobody waits" (SWARM.md) and reality (A is the stalled
  lane). Making A a prerequisite would have stopped the three productive
  lanes.

## 3.4 Defects to fix before anyone builds

Concrete, each with the failure it causes.

1. argmax on an all-zero row returns index 0, and index 0 is the ego.
   D13/D15/D16 together: a legal-mask Hadamard product that zeroes a row,
   followed by per-row argmax, yields 0. For TRAVERSE that is accidentally
   "stay". For ATTACK it is "attack yourself"; for CONSUME, "eat yourself".
   Fix: a row must have a strictly positive max to act, and the ego column
   must be masked out of every relation that is not self-directed. Same
   family of bug as the harness tie-break defect found in AC-01 and the
   archive tie-break E fixed in E4; ties need a seeded deterministic rule.

2. The delta tensor creates energy. D17/D18 says two CONSUMEs on one bounty
   "naturally split the energy". Summation does not split; it pays both in
   full and mints energy. The fix is a conservation invariant enforced per
   tick, in integers (wforge is integer-only for exactly this reason):
   sum(organism energy) + sum(bounty stock) + dissipated == injected. This
   invariant is the engine's trace-hash equivalent: it is exact, cheap, and
   a cheat engine that leaks energy fails it. Any economy without it will
   be gamed within the hour (cf. the wforge free-action bug, found by B on
   its first oracle pass).

3. Per-key EXPIRE per tick is a round trip. D7's RENEW_LEASE as an EXPIRE
   per key per tick costs >=0.33 ms each from Windows (measured). B1 showed
   one Redis caps at ~190k steps/s aggregate and Lua k-ticks server-side
   is the only form that amortises. The lease economy must be a Lua script
   settling all leases for a batch of organisms in one EVALSHA, or an
   in-process integer array with Redis as the durable mirror. Otherwise the
   crucible runs at tens of organisms, not thousands.

4. The VRAM guillotine will not fire at crucible scale. C1: the TT policy
   at d64 r64 B16k is memory-BOUND but nowhere near 16 GB; toy worlds are
   kilobytes. A dense organism dies of the rent long before VRAM. If the
   operator wants a hardware predator, it has to be a designed per-episode
   cap (an evolvable world gene), not the physical card.

5. Cannibal HGT will go extinct by selection. D19 makes CONSUME on a corpse
   a ~1% jackpot / ~99% poison gamble. Selection then favours lineages that
   never eat corpses, and the HGT rate falls to zero; the mechanism kills
   itself. Eligibility count before freezing (per
   feedback_preregistered_rules_need_an_eligibility_count): what fraction
   of consumes are on corpses, what fraction of splices survive purgatory,
   over a seed population, BEFORE any claim about "digestion evolving".
   Options: corpses are the dominant energy source (so eating is
   compulsory), or splice probability is itself an evolvable gene, or the
   splice is type-checked at the boundary (the brief forbids this; I would
   allow a cheap "compatible port" test and charge for it).

6. The empathy trap has no anti-silence control as written. SWARM.md's D1
   already specifies it: a*=0 vs a*>0 must differ and silence must lose
   yield. The brief's bounty needs the same, plus a leaked-seed cheat
   caught by permuting the codebook between episodes (also already in D1).

7. Node-per-stream communication at scale is the Redis bottleneck again.
   One stream per graph node with XADD + LISTEN per tick puts every message
   through the single Redis thread that B1 measured at ~190k ops/s. Fine
   for a 20-minute crucible with hundreds of organisms; not the engine of
   a batched world. Design the channel as an in-process integer array with
   the SAME semantics as a Redis form, and prove the two equal by hash
   (that is what B1 did for worlds).

8. Vocabulary collision: "fossil". In Prometheus a fossil is a preserved,
   verified code specimen (Techne's vault, 117 fossils, Nyx's chop shop).
   The brief's "fossil ledger" is a corpse table. Call it the corpse ledger
   or the graveyard; do not overload fossil.

9. The 1-hop COO payload reshuffled every tick destroys within-episode
   memory of neighbours by construction, which is the intent, but it also
   makes "remember the topology of the last five nodes" (D12) impossible
   without an identity the organism is forbidden to have. The brief wants
   both. Resolution: identity through RELATIONS (the organism may keep a
   hash of the local relation pattern), never through indices; state that
   explicitly so lanes do not argue about it.

## 3.5 What Prometheus doctrine adds that the brief lacks

The brief keeps "receipt + cheat control + separate ledgers + kills score".
It drops three things the morning's rows say are load-bearing.

- An oracle per biome. The swarm's whole credibility today is the trace
  hash. The ecology needs two: the conservation invariant (3.4.2) for the
  economy, and a permutation-equivariance oracle for meaning drift (run the
  same seed unscrambled and scrambled; the scrambled trajectory must equal
  P·traj·P^T exactly). Remember the asymmetry
  (feedback_invariance_null_is_asymmetric): a failed equivariance test
  proves the engine leaks identity; a passed one proves only equivariance,
  not that organisms use relations.
- A cheat per pressure, run before the positive. B1s, E4b, C2 all showed
  the score alone cannot see the cheat; only the aimed probe can
  (feedback_verification_must_be_aimed_at_the_claim). For each pressure in
  1.2 the cheat is the organism that reads what the pressure hides: the
  memoriser under drift, the flag-reader under regime change, the
  shared-seed pair under the toll road, the stipend-rock under the economy.
- Eligibility before bars. Three degenerate rules in four days last week;
  E2's 5% bar was set without an attainable range. Every ecology bar
  (branch points per CPU-hour, bits saved at parity, HGT survival rate)
  needs its attainable range and eligible count computed on a seed run
  first.
- host_cpu on every cell (C1b: parallel kernels sped up under load; B's
  burst moved two of C's crossovers). Speed claims from a shared host
  without it are INDETERMINATE by SWARM.md s4.

## 3.6 The meta-tracker, specifically

The most quotable idea in the brief and the one I would slow down.

- Identifiability. A CP/TT completion of a tensor with ten modes and a few
  hundred observed cells is not determined; it will fit and "propose"
  regardless of whether structure exists. The claim has to be tested as a
  prediction: does the factorisation predict HELD-OUT cells better than
  the additive model (sum of per-axis marginals)? If not, it is proposing
  noise. Start at three or four axes where the swarm already has cells:
  form x n_envs x world x host_load (B1 rows), backend x d x r x B (C1
  rows, 682 cells), world x genome-class x budget (E4b/E5b).
- Missing not at random. The cells that exist were chosen by the lanes;
  cells proposed by the tracker and then run become exposure-weighted
  (feedback_onpolicy_score_conflates_exposure_and_competence). A tracker
  that steers the sampling must be scored against a held-out random-cell
  draw it did not propose, or it grades its own homework
  (feedback_neutrality_gate_can_be_tautological).
- Ownership. Crossing dimensions of the outcome record is Theophrastus's
  charter (SWARM.md s7 already routes "new axes" there). The right shape is
  a packet to Theophrastus with the swarm's rows as the first tensor, not a
  fifth DuckDB inside primordial/. DuckDB-over-parquet as the swarm's own
  corpse store is fine; the analysis seat is elsewhere.
- Timing. The brief's own "observer for 72 hours" is right; today the
  tracker is a control experiment (factorise vs additive on C1's 682 cells,
  one hour), not a steering loop.

## 3.7 Design options

Option 1. Reboot around the brief.
  Five new lanes: crucible+corpse ledger, Relational Dark, toll road,
  reapers, tracker; JSON DAG organisms; the Dozen. Cost: abandons the
  contract, the oracle and ~30 receipts; the productive lanes are told to
  stop; A, the stalled lane, becomes a prerequisite. Reward: one coherent
  organism-level economy from day one. I do not recommend it.

Option 2. Graft the brief onto the lanes (recommended).
  Keep SWARM.md, the contract and CHIMERA-0. The brief becomes each lane's
  next-iteration list; lane A adds the two ecology oracles to the contract
  (energy conservation, permutation equivariance) as a contract bump.
   A  conservation audit as a contract helper; corpse ledger = receipts +
      per-organism rows to parquet (DuckDB optional); file A3; packet the
      tracker control to Theophrastus.
   B  B2c: Relational Dark = B2's relations on a random/scale-free graph
      with a per-episode id permutation and the equivariance oracle; then
      Semiring Zoo on B2's kernels (B3 already censused 9 operators).
   C  Tensor Surgery + Bond Amputation as mutation operators over C2's
      plastic TT (C2 IS the rank-tax/plasticity-budget experiment); C3's
      Pareto is the Representation Speciation niche map.
   D  boot it: D1 metered channel = the toll road; bottleneck roulette and
      the empathy trap are D1's second and third crucibles; anti-silence and
      codebook-permutation cheats are already specified.
   E  the energy economy inside the archive loop (rent, seed battery, zero-
      sum fork) with the conservation audit; QD by mechanism descriptors
      (rank, message bits, memory half-life); a WORLD archive keyed by the
      economy constants (Physics Mutation) sampled against the organism
      archive; cannibal HGT only after its eligibility count.
  Cost: nothing stops; the JSON-DAG genome is deferred until a lane needs
  cross-representation splicing (C3's ecology is where it would first pay).
  Reward: every ecology claim inherits an oracle and a cheat control that
  already exist.

Option 3. Two swarms.
  Keep the current five on CHIMERA-0 and start a second five on the brief's
  economy with its own substrate ports. Blocked by SWARM.md s4: M1 shares
  with SFE and Vivarium, each lane is capped at 3 cores, and A is already
  under-staffed. Possible only on a second host.

## 3.8 First crucibles under option 2 (concept only, 20-60 min each)

Each: hypothesis that can die, the cheat, the eligibility check, done-when.

 X1 Conservation audit (A, then everyone). Hypothesis: an integer energy
    ledger over B's Encounter with rent + bounty + zero-sum fork balances
    exactly every tick over 1000 episodes. Cheat: an engine that pays two
    CONSUMEs on one bounty in full must fail the audit on the first shared
    tick. Done: rows with 0 violations honest, >0 cheat.
 X2 The rock (E). Hypothesis: under rent with no stipend, the zero-action
    organism dies within seed-battery ticks in 100% of episodes, and the
    same organism under a stipend of >= rent survives forever. This is the
    positive control for the economy; if the rock lives without a stipend,
    the rent is mis-set. Eligibility: compute the attainable survival range
    from the constants before running.
 X3 Meaning drift (B). Hypothesis: with a per-episode id permutation, a
    planted memoriser (acts on global ids) loses >=90% of its bounty yield
    and a planted relational policy loses <=5%; the equivariance oracle
    holds 100%. Cheat: an engine that leaks the permutation through the
    local index order must fail the oracle. Note the asymmetry: this proves
    the engine hides identity; it does not prove evolved organisms use
    relations.
 X4 Cannibal HGT eligibility (E). Hypothesis: over a seeded population with
    corpses as X% of bounties, the fraction of consumes that are corpse
    consumes and the fraction of splices surviving five ticks are both
    measurable and > 0. No claim beyond the counts. If splice survival is
    < 1/1000, the mechanism as written is dead and gets redesigned before
    anyone claims digestion.
 X5 Toll road anti-silence (D, on boot). D1 as specified: two slots, one
    sighted, one mobile; a*=0 vs a*>0 must differ; the shared-seed pair
    must be caught by a codebook permutation between episodes.
 X6 Tracker control (A or Theophrastus). Hypothesis: a rank-r CP fit on
    C1's 682-cell tensor predicts 20% held-out cells better than the
    additive model in MSE. If it does not, the meta-tracker is not steering
    anything yet and the brief's closed loop waits for denser data.
 X7 Closed-loop deficit (E+C, already queued). E5b's 0/5 stands. The
    candidate causes E listed (r=3 over 36 hex digits, 8-entry codebook,
    open loop suffices in fixed-seed worlds) are three separate crucibles;
    the third is a Meaning-Drift world where open loop cannot suffice by
    construction, which is the honest reason to build X3 first.

## 3.9 Questions only the operator can answer

1. Is the goal still CHIMERA-0 (one receipt with all five lanes in it), or
   does the ecology brief replace it? Option 2 keeps both; option 1 drops
   CHIMERA-0.
2. Does lane D get a session? Without it, every communication pressure is
   unowned.
3. Does A get restarted or re-staffed? Its uncommitted A3 rows are the
   fabric result and the contract bumps in option 2 are A-only commits.
4. Is the tracker to be built inside primordial/ or packeted to
   Theophrastus? The doctrine (SWARM.md s7) says the latter.
5. Rename "fossil ledger" to "corpse ledger" in any directive that follows,
   to keep Techne's vocabulary intact.
