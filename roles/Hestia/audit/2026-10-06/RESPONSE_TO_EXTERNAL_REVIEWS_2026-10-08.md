# Hestia: response to the external reviews of Audit 1, and the stepping
# stones per engine

Currency: 2026-10-08. Instance Hestia[buckkeep-8cd68af4]. Audited tree
origin/main eddf0ae44 plus Theseus's commits of 2026-10-08 (9a329ab29).
Reviews, verbatim: roles/Hestia/prompts/2026-10-08_external_reviews/.
Operator's question (same directory, 01_): are our engines, worlds and
ecosystems too trivial for the north star, and is the higher gear longer
runs, more world complexity, more organism learning, or something else?

This is a model's assessment for the operator. It changes no seat's
charter and runs nothing. Where it cites a number, the number is in a
dossier under dossiers/ or in the named seat's committed verdict file.

----------------------------------------------------------------------
## 0. The short answer

Yes, the engines are too trivial for the north star, and the two reviews
and I agree on why: the worlds do not pay for cognition (W2), the
organisms cannot keep what they find (W3), and selection over flat genomes
with a scalar score cannot assemble parts that are worthless alone (W1).

Longer runs: NO, not yet. The cleanest evidence in the fleet is Ananke
C2C: 16x budget moved multi-hop relay from about 2.3% to 16/32 (a rarity
problem, solved by time) while FLIP stayed 0/290 (a composition problem,
untouched by time). Aether's 256^2 lattice reproduces its 2048^2 bulk
statistics within 0.4%; SFE's 3.7M evaluations produced one register.
Time crosses rarity; it does not cross composition. Extend a run only when
its rate of NEW CERTIFIED MECHANISMS is rising (ChatGPT's 1x/4x/16x rule,
which I adopt as written).

World complexity: YES, but demand, not size. Both reviews say this and
the audit measured it. The gate already exists in the fleet: Ensorain's
null ladder N0-N6 is the "constant / memoryless / window / batch-fit"
baseline ladder ChatGPT proposes. Cosmos's C3 certificate is the "is a
working memory needed" test. Ludus's Nim miss is the MDL rule. Assemble,
do not invent.

Organism learning: YES, and it is the cheapest lever we have not pulled.
Four substrates can host lifetime plasticity with small changes (Ares has
weighted edges; Ananke has writable registers; Odysseus has spikes;
Moonshot is designed for it). Note the mechanism: lifetime learning
smooths the fitness landscape around a partial solution (Hinton-Nowlan),
so it attacks the SAME wall as structured credit. It is escape (a) and
(c) at once.

The one lever the reviews add that I had under-weighted: reachability
archives (Go-Explore). Accepted, with one correction from our own rows:
two engines already run archives (Primordial MAP-Elites, Theseus QD
elites) and both failed, because their behaviour descriptors are flat
fingerprints that reward noise. An archive keyed on CERTIFICATE-DERIVED
descriptors (which bits are carried, which parts are inert) is a
different instrument and has not been tried. That is the stepping stone.

And one safeguard both reviews converge on, which the audit's own cases
justify: the COGNITIVE ACCOUNTING LEDGER (who did the computation:
organism / developmental machinery / search infrastructure / certifier).
Crius's environment calibrated the organism's actions and lent it a
simulator; D-5's "learning" was a cache; Aphrodite's "mechanism" was a
hand-coded menu edit; Tyche's parity was solved by the readout tree;
alien_circuitry read the oracle. Every ladder result reports the four
rows from now on.

----------------------------------------------------------------------
## 1. The reviews, reviewed

ACCEPTED (with the evidence that makes it ours, not just theirs):

A1 "Three interacting problems, not one": worlds, organisms, accumulation.
   Yes. The audit's W1-W4 are those three problems plus credit.
A2 World-Demand Foundry in parallel, not after a compositional seed. I
   wrote "do not open M5 coevolution before a seed exists"; the foundry is
   not coevolution and should start now. Amended (s6).
A3 Longer runs only on cumulative dynamics; 1x/4x/16x. Adopted.
A4 Three timescales (lifetime, consolidation, evolution of learning).
   Adopted as the organism-side program.
A5 Three escapes must be separated causally. That was Part 5 Step 2.
A6 "Seven failures are not one obstruction": different proximate
   bottlenecks. Correct; the table in s2 names each. The shared SHAPE (no
   individual fitness for the parts) stands; the proximate cause differs
   and dictates the stepping stone.
A7 "Nearly a theorem" is too strong. Amended to "strong prior from
   Valiant/Feldman for the tested representations; not a proof for
   population search with recombination, neutrality or learning".
A8 Diagnosis before pivot (expressible? reachable? rewarded? credited?
   detected?). Adopted; Part 5 Step 3 now has a diagnosis column.
A9 Cheap exploration / expensive proof / permanent preservation. Adopted.
   SFE's 95-193 s per row for 0.1 s of science is the case.
A10 Cognitive accounting ledger. Adopted (s0).
A11 Reserve 15-20% for alien lanes not forced into typed primitives.
   Agreed; the lanes are named in s3.
A12 Frontier archive and mechanism library are two different stores.
   Agreed; the fleet already has the library's skeleton (sigma_kernel
   symbols, Nyx organ ledger, Hades's charter) and no frontier archive.
A13 Archived exploration is not autonomous cognition; disable the archive
   at final evaluation. Adopted as a ladder rule.

PUSHED BACK (with evidence):

P1 Gemini: "Go-Explore mechanics are required ... an algorithmic guarantee
   of returning to the fringes". There is no guarantee (ChatGPT's reply is
   right), and in our fleet the two archives that exist lost: Primordial's
   MAP-Elites brains score below a do-nothing policy (107.75 vs 98.76), and
   Theseus's novelty archive fills with programs that random generation
   matches (deep arm +0.32 [-0.33, 0.76] vs random; THESEUS-27 found the
   QD elite set incompatible with its own population cap). The archive is
   only as good as its descriptor. Stepping stone, not foundation.
P2 Gemini: "TT-Cross before symbolic extraction, in Triton kernels". The
   fleet already runs tensor-train organisms (Ensorain's STRUCT panel
   includes 'tt') and a tensor-train cartographer (Harmonia); the TT
   organisms lose to a tuned batch fit 9/9. Nothing in the fleet is
   compute-bound on symbolic extraction, because nothing has produced a
   mechanism to extract. ChatGPT's objection (low-rank approximation
   erases exactly the rare high-order interaction we are looking for) is
   the right one and is testable later, in Harmonia's lane, after a
   mechanism exists. Not now.
P3 Gemini: "PPO clipping". No engine in the audit uses PPO; the baselines
   are the engines' own GAs. ChatGPT already corrected this.
P4 ChatGPT: the 72-hour P3-ESCAPE-01. The questions are right; the clock
   is not. Theseus's 1,011-genome composition sweep took 4.2 CPU-h
   against a prereg estimate under 3; SFE rows cost 95-193 s each; Ananke
   runs 55,296 evaluations per search, 290 searches. A 2x2x2 factorial at
   32 seeds over four ladder rungs is more than 1,000 runs per engine, on
   laptops. ChatGPT concedes this in its own last paragraph. Treat "72
   hours" as "one measured factorial per engine, screening at 8 seeds,
   confirmatory at 32 only for the cells that move". See s5.
P5 ChatGPT cites "Hades's dual-mesh concept". Hades was chartered on
   2026-10-07, after the audit population was frozen; it is unaudited.
   Its charter (CHIASMA: positive memory plus compressed failure
   boundaries; a handcrafted four-organism experiment E1 with a kill
   criterion before any evolution; matched controls) is the right SHAPE
   for the mechanism library with failure boundaries. It has no rows yet.
   I will audit it when E1 has rows, not before.
P6 Both reviews: restructure the fleet into three programs. That is the
   operator's organisational call. The mapping I would use is in s3; it
   differs from ChatGPT's in putting Theseus, z80atlas, Primordial and
   Aether in the alien lane and sigma_kernel, Nyx, Hades in the library
   lane.

----------------------------------------------------------------------
## 2. Which bottleneck dominates each zero (the diagnosis ChatGPT asked
## for)

For each 0-of-N, the five questions: is the mechanism EXPRESSIBLE in the
substrate; is it REACHABLE by the operators; does the world REWARD it;
does the CREDIT signal see partial progress; would the instrument DETECT
it. "yes" = shown by a committed row; "no" = shown; "?" = not measured.

    engine     target      expr  reach  reward  credit  detect  DOMINANT
    Ananke     FLIP        yes   no     part    yes     yes     REACH
               (16/16-line program exists; 4/200 FLIP cells admissible)
    z80atlas   COND_ONE    yes   no     no      no      yes     REACH+REWARD
               (reward paid from a Python ledger outside the VM; copying
               and computing compete for the same tape)
    SFE        W2_K2       yes   no     yes     no      yes     CREDIT
               (12-instruction hand solution; exact match pays echo 1/K)
    Crius      reuse       yes   no     yes     no      yes     CREDIT
               (hand mechanism +15.97; one score per 50-task life)
    Tyche      order-3     yes   no     yes     ?       yes     REACH
               (readout tree does the work; 128^-3 needle)
    Primordial cue read    yes   ?      no      no      yes     REWARD
               (do-nothing wins; 1/74 cells with headroom)
    Aether     combine     no    -      -       -       yes     EXPRESS
               (a winning write replaces the byte; no operator combines)
    Theseus    2-part      no    no     no      -       fixed   EXPRESS+REWARD
               (NEW 2026-10-08: first detector blind, planted 0/40;
               detector v2 passes 40/40 and finds 0/1011; programs have
               zero input channels, so no task can be posed)

Reading: two substrates cannot express a 2-part mechanism at all (Aether,
Theseus); three can express it but cannot reach it (Ananke, Tyche,
z80atlas); two can reach the parts but score them as nothing (SFE,
Crius); one is not paid for it (Primordial). The stepping stones in s4
follow this table, not a single recipe.

----------------------------------------------------------------------
## 3. The levers and who hosts them

    lever                      what it attacks   cheapest hosts
    W  world demand (foundry)  W2 reward         Ensorain N0-N6 gate, Cosmos
                                                 C3 cert, Ludus FOUNDRY m-knob
    C  structured credit       W4, W1(a)         SFE partial credit, Crius
                                                 per-block credit, z80 in-VM
                                                 reward, stepping-stone tasks
    L  lifetime plasticity     W1(c), W4         Ares (edges), Ananke (regs),
                                                 Odysseus (spikes), Moonshot
    P  promotion / modularity  W1(b), W3         Ananke block-dup, Crius
                                                 SMOOTH, Aphrodite typed+MDL,
                                                 incubation D-VM
    A  frontier archive        reachability      Crius (real world states),
                                                 Ananke (genome archive keyed
                                                 on carried-bit certificate)
    X  expressibility repair   W1 at the root    Aether commit operators,
                                                 Theseus input channels
    K  cognitive accounting    instrument truth  every result

Programs, as I would draw them (operator's call):
    WORLD FOUNDRY     Cosmos (certifier), Ensorain (gate + grammar), Ludus
                      (curriculum generator)
    DEVELOPMENTAL     Ananke, Ares, Crius, Aphrodite, Moonshot, Odysseus,
    ORGANISMS         incubation D-VM
    LIBRARY +         sigma_kernel (provenance), Nyx (librarian), Hades
    CERTIFICATION     (boundaries), Tyche + Cosmos C3 + Crius assay +
                      Aphrodite R8 + Ananke swap + Aether twins (rulers)
    ALIEN LANE        Aether, Theseus, z80atlas, Primordial Z8 (15-20%,
    (not typed)       same certification, own representations)
    CONTROLS          forge (cosplay baseline), herakles/evca (field
                      ceiling), D-series ablations, alien_circuitry gates

----------------------------------------------------------------------
## 4. Stepping stones per engine

Format: NOW = cheap and already designed (run first); NEXT = one
structural change toward the reviews' direction; THEN = the move that
would put the engine on the ladder's upper rungs. Letters = levers (s3).
SHOWS = what a pass establishes; KILL = what ends the line. Kill
criteria from REPORT Part 3 stand unless restated.

### 4.1 Aether (X, then W)
NOW   TEST-4 on mob_r1x1e0: does information survive past radius 1.
NEXT  A commit-operator table (old op incoming: xor/add/and; code fields
      protected). Hand-build a gate and a memory cell in the new law as
      the EXPRESSIBILITY positive control. Add the evca-style particle /
      carrier detector before any claim of "circuit".
THEN  Only after a hand-built gate works: an energy economy that pays for
      predicting the injected bit-flip stream (value of information made
      positive), and automatic law screening by information-flow metrics.
SHOWS the physics can compute before asking whether it will. KILL: no
      law in the operator table supports a hand-built gate + cell.
NOT   more GPU scale (256^2 == 2048^2 within 0.4%). Alien lane: do not
      force typed primitives on it.

### 4.2 Primordial / NPE (W, then C)
NOW   The amended X-TASK-GATE with the CT_UA hand-built genome as the
      must-pass control (96 seeds, costly reading).
NEXT  Run the Ensorain N0-N6 gate over the 74 world cells and keep only
      cells where a window/batch baseline leaves headroom (today 1/74).
      Match the brain basis to the world physics (affine mod 2^16 beat the
      hex-digit tensor brain 3/3) or change the physics; co-design them.
THEN  Z8 soup: pay task reward INSIDE the VM as energy, so copying and
      computing stop competing (also z80atlas 4.10). Its MAP-Elites
      archive gets a certificate-keyed descriptor (which bytes carried).
SHOWS a world where cognition beats do-nothing exists before any brain is
      evolved. KILL (swarm): after the gate, no cell has headroom > 0.2 of
      the oracle gap. The heredity instruments move to the ladder either
      way.

### 4.3 Odysseus (L)
NOW   Integer three-factor plasticity (eligibility x reward) + delayed
      match-to-sample, N = 4000, 8 seeds, vs the frozen reservoir with a
      trained linear readout.
NEXT  If plasticity wins: store the plastic synapses shard-locally (32 B
      per neuron is nothing at N = 4000) and put the same circuit on
      ladder rungs R1-R2.
THEN  Only then the distributed scale the engine was built for.
SHOWS escape (c) in a spiking substrate, the cleanest test of it in the
      fleet. Gemini's "UDP mesh choke" describes this engine today, which
      has no learning to choke on.

### 4.4 Ananke / PTE (P, A, L)
NOW   FLIP representation test: current genome vs mapping-bit +
      block-duplication vs the same seeded with a frozen relay module
      (REPORT 3.4; ChatGPT P0).
NEXT  Frontier archive keyed on the counterfactual-swap certificate
      (which bit each program carries, which lines are inert), branch
      from archived partial-FLIP programs, with a random-checkpoint
      archive as control and the archive DISABLED at final evaluation.
THEN  A plastic variant: the mapping is learned within life from reward
      (registers already exist), to test (c) against (b) on one task.
SHOWS whether reachability or representation was the wall. KILL: both
      NOW arms <= 1/32 at 4x AND the certificate-keyed archive adds no
      certified mechanisms over the random archive.

### 4.5 Moonshot / Themis (L; design)
NOW   Define the integer primitive in code. CPU pilot on the CONTEXT-
      FLIPPED delayed cue (the R2 rung, not the latch floor): symbolic /
      fixed-weight neural / plastic neural, 64 populations each.
NEXT  No M4 cluster spend until the plastic arm beats fixed. Fix the
      wforge unpaid-write defect (world.py:216-224) first.
THEN  If plastic wins: evolve the plasticity rule, not the weights (the
      "evolve the learner" branch).
SHOWS whether (c) is real at the cheapest scale. KILL: all three arms
      <= 2/64 at 4x the floor budget.

### 4.6 sigma_kernel (library plumbing)
NOW   Race test + compare-and-set fix (#1734 to Techne).
NEXT  Define the MECHANISM LIBRARY ENTRY as a sigma symbol: executable,
      I/O contract, preconditions, certificate hash, failure boundaries,
      acquisition cost, transplant evidence, lineage of abstractions built
      on it (the schema in ChatGPT review 2, s1B).
THEN  Nyx writes entries; Hades writes boundaries; the ladder reads them.
SHOWS the library is a store with provenance, not a prose list.

### 4.7 Cosmos (W)
NOW   Transfer the C3 P1/P2 certificate unchanged to Aether, a Primordial
      organism and an Ensorain organism (5 planted controls each).
NEXT  Cosmos becomes the Foundry's CERTIFIER: every admitted world carries
      the baseline ladder (constant / reactive / short horizon / fixed
      memory / learner / library / solvability) and the Nim MDL rule.
THEN  Generate worlds whose cue-to-outcome mapping CHANGES during life
      (non-stationary), so a learned mapping, not a stored bit, is what
      pays. These are R2-demanding worlds. Retire the law miner.
SHOWS a world-admission gate that no reflex passes. KILL: the certificate
      misclassifies a planted control on another engine.

### 4.8 Ensorain (W)
NOW   Hidden-state necessity assay (three latent-state families, exact
      Bayes oracles, all 490 menu organisms + N0-N6, 8 seeds).
NEXT  Adopt N0-N6 as the FLEET world-admission ladder. Goldilocks band:
      admit a world only if the best null captures between 0.2 and 0.8
      of the oracle gap. Add latent-state families to the grammar (0
      today) and credit delay > 0 (179/181 worlds have delay 0).
THEN  One stateful organism class in the menu (the menu has none), then
      hand the admitted worlds to the developmental program.
SHOWS worlds that demand memory exist and are reachable by the grammar.
      KILL: no grammar family can be made to need hidden state without
      planting the answer.

### 4.9 Ludus (W)
NOW   Hidden-memory knob m = 0..4 in FOUNDRY; exhaustive typed rule
      search to size 8 as the MDL gate.
NEXT  FOUNDRY as the ladder's CURRICULUM GENERATOR: one world property
      changed at a time gives structured stepping stones R1 -> R2 -> R3
      (lever C for every other engine).
THEN  Host a foreign organism (Ananke's or Aphrodite's) on Ludus worlds;
      Ludus has no learner and should not build one.
SHOWS a world family with certified planning depth > 2. KILL: a size-8
      observation-only rule keeps >= 95% at every m.

### 4.10 z80atlas, both (C, P)
NOW   COND_ONE with a stepping-stone task paid first, YOKED control, 240
      seeds per arm.
NEXT  Pay reward INSIDE the physics (energy for correct output, debited
      per instruction), so copying and computing stop competing.
NEXT  A block-duplication operator (copy a code segment within the tape):
      modularity in the one substrate where it is natural.
THEN  Alien lane with Aether: keep the ISA, measure with the ladder.
SHOWS whether an ISA soup can take a 2-instruction step with credit and
      duplication. KILL: <= 2/240 with stepping stone AND <= 2/240 with
      duplication.

### 4.11 Ares (L first, then P)
NOW   Fix the transplant to map interface edges by TYPE (today random,
      substrate.py:365,377). Parity k = 1, 2, 3 + a latch-seeded arm.
NEXT  Three-factor plasticity on the existing weighted edges: the
      CHEAPEST lifetime-learning test in the fleet, because the organism
      already has weights. Pair it with a law-switch world (Tyche-style)
      so plasticity pays.
THEN  Subgraph freeze with typed ports = promotion in a graph organism.
SHOWS whether plasticity moves k = 2 before promotion does. KILL as in
      REPORT 3.11.

### 4.12 Crius (C, A, K)
NOW   ROUGH vs SMOOTH on RELAY with auto-calibration and the free
      simulator REMOVED (the environment stops doing the organism's work).
NEXT  Per-block credit (a score per task, not per 50-task life).
NEXT  Go-Explore proper: Crius has real world states, so archive world +
      organism state, branch, random-checkpoint control, archive OFF at
      final evaluation. This is where Gemini's proposal fits best.
THEN  Cognitive accounting on every result (environment / organism).
SHOWS whether reuse is reachable once credit sees parts. KILL: SMOOTH
      0/9 with credit AND archive.

### 4.13 SFE ecology (C, then cheap-exploration split)
NOW   Typed W2_K2 with typed-edit mutation (REPORT 3.13).
NEXT  Partial credit replacing exact match (the 1/K echo trap).
NEXT  Split the paths: the Proteus GA runs locally with sketches and
      checkpoints; only candidates that pass a behavioural filter go to
      the SFE ledger for sealed certification (ends 95-193 s per row).
THEN  SFE becomes the certification path of record, not the inner loop.
SHOWS whether the organism side has a future. KILL as in 3.13; then
      retire organisms, keep provenance.

### 4.14 Nyx (P, library)
NOW   Five accepted organs as typed primitives on W2_K2 vs size-matched
      random primitives, 30 seeds, ablation.
NEXT  Nyx becomes the LIBRARIAN: an organ enters the library only with a
      causal certificate from a Prometheus run; "portability YES" requires
      a transplant row. Reading-only organs are references, not organs.
THEN  Organs that pass become ladder material.
SHOWS whether anything disassembled transfers. KILL: no separation from
      random primitives.

### 4.15 Aphrodite (P, then L)
NOW   R8 with typed promotion + MDL acceptance, 20 paired unseen seeds.
NEXT  A second template shape (the fold is the only one), so depth-2
      abstraction is expressible at all.
NEXT  Select the library for the FUTURE DISCOVERIES it enables (R8 as the
      library's fitness), not for validation savings.
THEN  Compression arms (raw / sketch / TT / shuffled) only if NEXT passes.
SHOWS whether inheritance can enable rather than substitute. KILL as in
      3.15.

### 4.16 incubation + D-VM (P)
NOW   MDL-ordered learner M1 vs fixed-order M0 on INDEPENDENTLY written
      worlds (no planted answers).
NEXT  Build the D-VM worlds that were never built: it is the one
      representation in the fleet where a learned transform is data a
      later transform can edit (the promotion operator, native).
THEN  Transform-of-transform at depth 2 as its R4.
SHOWS whether native second-order promotion beats menu selection. KILL as
      in 3.16.

### 4.17 alien_circuitry (ruler)
NOW   Table-free invariant discovery on the 387M-state world.
NEXT  Its gate stack (trap map, lookahead, residual after known invariant,
      leakage) joins the ruler package; the substrate retires.
SHOWS whether anything can be found without the oracle. KILL as in 3.17.

### 4.18 D-series (method only)
NOW   Nothing to run. The shuffled-history and random-library ablations
      become mandatory on every "learning" claim in the ladder protocol.

### 4.19 Theseus (X, then W) -- updated for 2026-10-08
NOW   Done by the seat: detector 23b was blind (planted 0/40); v2 passes
      (40/40, 0 false positives) and finds 0/1011 whole-genome
      compositions; 30c (in-context pairwise epistasis) is preregistered.
      My prediction #18 (some ruler AUC >= 0.75) is scored RIGHT on the
      detector and the substrate result is a confirmed wall, not an
      indeterminate one.
NEXT  Give programs INPUT CHANNELS (zero today) and a task, so a
      mechanism can be selected for rather than only counted. Fix the
      concept compiler (14/95 concepts -> one 2-rule program).
THEN  If 30c finds embedded 2-part epistasis anywhere, that is the first
      certified composition in the fleet; put it under the accounting
      ledger before celebrating. Alien lane; keep its rule language.
KILL  30c finds 0 embedded pairs in every arm at its planted gate passing:
      the primitive set cannot host composition; retire the substrate and
      keep the control harness.

### 4.20 Tyche (ruler first, then L)
NOW   Parity-k ladder (k = 2, 3, 4) with a LINEAR readout only, so the
      lenses, not the tree, must do the work.
NEXT  Run on the 122 catalogued real residuals (0 runs to date); that is
      the engine's reason to exist, and the only dark data in the fleet.
NEXT  Tyche's rulers (marginal-gain, causality audit, interaction-order
      certificate) become the ladder's certification layer.
THEN  Law-switch worlds as the plasticity test bed for Ares and Ananke.
KILL  as in 3.20.

### 4.21 herakles/evca (control + detector)
NOW   Build the domain/particle detector; particle-reuse transfer test.
NEXT  Lend the detector to Aether and the Z8 soups (the only compositional
      structure the evolved-CA field ever found was particles).
SHOWS whether carriers exist in any soup. No search of its own needed.

### 4.22 forge lineage (cosplay baseline)
NOW   Nothing new to evolve. The "pick index 1" decoy (75/186) becomes
      the constant baseline every ladder result must beat.
NEXT  If library learning is tested at all, do it once, in Aphrodite
      (4.15), not twice.

### 4.23 Hades (unaudited; chartered 2026-10-07)
NOW   Run E1 as chartered (four handcrafted organisms, WT-0 known-answer
      gate, kill criterion) before any evolution.
NEXT  Its failure-boundary store is the "boundaries" column of the
      library entry (4.6). Audit when E1 has rows.

----------------------------------------------------------------------
## 5. Compute realism for the escalation campaign

Measured costs on main: Theseus 1,011 genomes = 4.2 CPU-h (prereg said
< 3); SFE 95-193 s per ledger row; Ananke 55,296 evaluations per search,
290 searches for FLIP; Aether 1.6e12 site-ticks over three weeks. The
hosts are laptops (BUCKKEEP is an i7-1260P) plus M1/M2 and RunPod on a
key held by one host.

A 2x2x2 factorial (archive x promotion x plasticity) at 32 seeds on four
rungs is > 1,000 runs per engine. So:
- Stage 0 measures throughput per engine and writes the budget BEFORE the
  factorial is sized (ChatGPT review 2, hours 0-12, as written).
- Screening at 8 seeds per cell; confirmatory 32 seeds only for cells
  whose screening lower bound clears the null.
- One engine per lever first (Ananke for P+A, Ares for L, Crius for C+A,
  Ensorain for W), not all engines on all levers.
- "72 hours" is the operator's deadline for a DESIGN with budgets and
  prereg, not for results. Results take what the measured budget says.

----------------------------------------------------------------------
## 6. Amendments to REPORT.md (annotations, not rewrites)

M1 Part 2 W1: "close to a theorem" -> "a strong prior for the tested
   representations; not a proof for population search with recombination,
   neutrality, spatial structure or lifetime learning". Literature still
   unverified (HESTIA-11).
M2 Part 2: add the diagnosis table (s2 here) and Theseus 30b as the eighth
   row.
M3 Part 5 Step 1: the World-Demand Foundry starts NOW, in parallel with
   the ladder, using Ensorain N0-N6 + Cosmos C3 + Ludus MDL. Only
   coevolution (M5) waits for a seed.
M4 Part 5 Step 3: before any "pivot" branch, the diagnosis column
   (expressible / reachable / rewarded / credited / detected) is filled
   for every failed rung; a substrate is retired for a NAMED bottleneck.
M5 Part 4: add the cognitive accounting ledger (organism / developmental
   / search / certifier) to the ruler package; add "archive disabled at
   final evaluation" and "shuffled history + random library" as mandatory
   controls.
M6 Part 5 STOP list: "custody growth ahead of R1" becomes "cheap
   exploration, expensive proof: certification runs on candidates, not on
   every evaluation".
M7 Part 1: Theseus moves from "dead end, loses to random on 2/3 rulers"
   to "confirmed composition wall with a valid detector; 30c pending".

----------------------------------------------------------------------
## 7. What I would not do

- Not longer runs now (s0).
- Not TT-Cross or Triton kernels now (P2): there is nothing to compress.
- Not a fleet-wide Go-Explore mandate: archives in Crius and Ananke
  first, keyed on certificates, with random-archive controls.
- Not a single architecture for all engines: the alien lane keeps its
  representations and only shares the rulers and the accounting ledger.
- Not a verdict on Hades's dual mesh until E1 has rows.
- Not a scalar "sagacity score". The scorecard in ChatGPT review 1 s10
  (compositional depth, abstraction reuse, learning efficiency, causal
  transfer, adaptive range, compression efficiency, boundary awareness,
  cumulative innovation) is a vector; keep it one.
