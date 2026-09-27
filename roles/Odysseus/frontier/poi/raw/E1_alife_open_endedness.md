# E1 -- Artificial life, open-endedness, emergence of self-replication

Delegate: external-research (disposable), for Odysseus / Prometheus POI program.
Date: 2026-09-27. Web search and web fetch WORKED.
Citation marks:
- VERIFIED = I fetched the arXiv abstract/html page (or the repo) in this session and the
  claim summarized below came from that fetch.
- VERIFIED-META = bibliographic data (authors/venue/year) confirmed by search results, but
  the content summary is partly from search snippets or my prior knowledge.
- UNVERIFIED = from memory; check before citing.

Field shorthand for each entry:
 1 DEMO   what they actually demonstrated
 2 ASSUME what they built in
 3 FAIL   what failed / is contested
 4 MEAS   the measurement that made the result visible
 5 CODE   reusable code/data
 6 PROM   does it sound like a Prometheus result under other words
 7 OPEN   what remains open
 8 ANTI   anti-gravity experiment (remove the field's favourite assumption)

=====================================================================
## PART 1 -- IDEA ENTRIES
=====================================================================

---------------------------------------------------------------------
### 1. Computational Life / BFF primordial soups
Aguera y Arcas, Alakuijala, Evans, Laurie, Mordvintsev, Niklasson, Randazzo, Versari.
"Computational Life: How Well-formed, Self-replicating Programs Emerge from Simple
Interaction." arXiv:2406.19108 (v1 Jun 2024, v2 Aug 2024). VERIFIED.

1 DEMO: Soups of random 64-byte programs, paired at random, concatenated into a 128-byte
  tape, executed in a self-modifying Brainfuck dialect (BFF: code and data share the tape,
  two heads can copy between halves), then split. With no fitness function and (by default)
  no background mutation, self-replicators take over in roughly 40% of runs within ~16k
  epochs. Also reproduced in Forth (near-universal and fast, <1k epochs), Z80 and 8080
  machine code, and spatial (2D grid) and long-tape variants. SUBLEQ variants did NOT
  produce replicators empirically although replicators exist in principle.
2 ASSUME: Designed instruction set in which a copy loop is only a few bytes; fixed-size
  program boundaries (64 bytes = the "organism"); a pairing/concatenation operator that
  forces every program to execute inside a shared tape with a partner; a step budget.
3 FAIL/CONTESTED: The paper's causal story (interaction/self-modification as the engine;
  early "pre-life" complexity rise) is directly contested by entry 2 (2026). SUBLEQ
  failure unexplained. Result depends heavily on instruction density of the copy primitive.
4 MEAS: "High-order entropy" (Shannon entropy minus normalized Kolmogorov estimate via
  brotli compression) -- a sharp drop/phase transition marks replicator takeover; plus
  most-common-token tracking and later tracer tokens for lineage.
5 CODE: https://github.com/paradigms-of-intelligence/cubff (CUDA or `make CUDA=0`; langs
  bff, bff_noheads, bff8, bff_perm, bff_selfmove, forth*, subleq, rsubleq4, z80/8080).
  VERIFIED. Pure-Python ports: github.com/peterseb1969/computational-life (seen in search).
6 PROM: Yes, almost exactly. Z80-like byte-tape soups where replicators emerge is the
  Prometheus native substrate. Their "program pair writes into partner" is host-mediated
  reproduction; partial copiers that exploit a partner's copy loop are parasites executing
  host code.
7 OPEN: What property of an instruction set predicts time-to-first-replicator? Why does
  SUBLEQ fail? Does anything beyond replication ever accumulate without an imposed task?
8 ANTI: Remove the fixed 64-byte organism boundary: a single long tape (or torus) with
  randomly placed instruction pointers and no split step; organisms must define their own
  extent (the long-tape variant hints at this but still seeds structure).

---------------------------------------------------------------------
### 2. "BFF: Simple explanations for complex phenomena" (the rebuttal)
Knierim, Versari, Obryk, Aguera y Arcas, Saurous. arXiv:2607.01483 (Jul 2026). VERIFIED.

1 DEMO: A plain mutation random walk in program space finds self-replicators at least as
  efficiently as the paired-interaction soup. Numbers reported: BFF soup ~5e6 programs tested
  to first replicator; uniform random sampling ~2.9e7 (6x slower); an optimized byte
  distribution (CUST64) ~9.4e4 (25x FASTER than BFF). Blocking "mergers" (ancestry depth/width
  limits, even depth=0) does not prevent replicator emergence; it only prevents takeover.
2 ASSUME: Same BFF language; a direct replicator detector (below) as ground truth.
3 FAIL/CONTESTED: Refutes the claim that interaction is the effective discovery engine;
  authors say BFF interaction is "not an effective model" of biological recombination.
4 MEAS: A direct functional self-replicator detector: nine tape pairs with varied partners,
  run five times with noise injected between iterations; a program counts as a replicator
  if >=48/64 bytes match across three test instances. Handles programs that leave unexecuted
  bytes intact or invert periodically.
5 CODE: detector in cubff common_language.h; variant bff_selfmove.cu. VERIFIED.
6 PROM: This is the exact null model Prometheus must beat. Any "emergence" claim in a byte
  soup should be compared with (a) random sampling from the soup's byte distribution and
  (b) a mutation-only random walk, at matched program-evaluation budgets.
7 OPEN: Is there ANY soup regime where interaction does more than select/amplify what
  sampling would find? What would an effective computational model of recombination be
  (authors call it open)?
8 ANTI: Keep the soup but forbid selection-by-copying: measure discovery rate of
  replicators when copies are discarded (pure search) vs when they persist; the difference
  is the only thing the "ecology" contributes.

---------------------------------------------------------------------
### 3. Coevolution of self-replication and function in a Z80 soup
Cicala, Niklasson, Randazzo, Boukortt, Basti, Etcheverry, Saurous, Laurie, Manyika,
Aguera y Arcas, Richards. arXiv:2607.09211 (Jul 2026, v2 Sep 2026). VERIFIED.

1 DEMO: 32-byte Z80 programs in 32 task niches (128x128 grids each, ~2M programs); pairs
  concatenated to 64 bytes, executed, split. No built-in copy. A validation phase (compute a
  polynomial f(x) mod 256 on 3 random x in 0..15) raises interaction probability 0.3 -> 1.0,
  minus a metabolic (step-count) penalty. Results: replication and task-solving coevolve from
  noise; a first "Load-Push" replicator (fills whole tape) is displaced by an LDIR block-copy
  replicator (~4 bytes), freeing tape for computation; task pressure speeds this transition;
  metabolic cost yields conditional halts (~21% of programs branch on register D, which differs
  between interaction and validation contexts -- i.e. context sensing); multi-niche soups with
  ~5% cross-niche pairing solve far more tasks than isolated niches (isolated max 15/32);
  emergent (vs hard-wired) replication gives higher ancestor-niche entropy (p=0.0007) but not
  better task performance.
2 ASSUME: Real ISA with a single-instruction block copy (LDIR/LDD) -- a "gift" copy
  primitive; experimenter-defined tasks and a reward channel (interaction probability);
  fixed 32-byte bodies; mutation 1/64 per program per epoch.
3 FAIL/LIMITS (authors): no recombination/symbiogenesis study; polynomials only (Z80 has no
  multiply); 32-byte ceiling; no cooperation. Replicator identification is by byte-pattern
  matching (0xED 0xB0 etc.) -- weaker than functional detection.
4 MEAS: Opcode-signature counts over time; robustness assay (replicator still works after k
  mutations: LDIR ~40% after 8 vs Load-Push ~5%); genealogical niche-label tracing; tasks
  solved = >=10% of niche solving across full domain.
5 CODE: none linked in the pages I fetched (check cubff and paper v2).
6 PROM: This is the closest external analogue to Prometheus Z80 worlds. "Host-mediated
  reproduction", "context-dependent execution", "stepping-stone curricula across niches" are
  all Prometheus-shaped findings. It is also the obvious prior-art collision risk for any
  Prometheus "capability not installed" claim.
7 OPEN: Does capability accumulate without an experimenter-defined task? Do the register-D
  conditional halts constitute a primitive "self/non-self" or "phase" sensor?
8 ANTI: Remove LDIR/LDD (they did a partial control) AND remove the task reward: can the
  soup evolve its own block-copy idiom and any computation that is used by other programs
  (e.g., a routine one lineage calls in another)?

---------------------------------------------------------------------
### 4. Self-replication is NOT implied by computational universality
Cotler, Hongler, Hudcova. "Self-replication and Computational Universality."
arXiv:2510.08342 (Oct 2025). VERIFIED.

1 DEMO: Constructs a Turing-universal cellular automaton that cannot sustain non-trivial
  self-replication ("transcription and translation but no replication"), refuting the
  von Neumann-era folk hypothesis that universality implies replicators.
2 ASSUME: Formal definitions of non-trivial self-replication; universality counted with the
  cost of encoding/decoding between dynamics and symbols.
3 FAIL/CONTESTED: Definitions of "non-trivial replication" remain debatable; theoretical,
  no evolutionary experiments.
4 MEAS: Proof/construction; complexity of translation maps.
5 CODE: none (theory).
6 PROM: Matches the SUBLEQ empirical null in entry 1. A Prometheus physics that is
  "Turing-complete" is not thereby a replicator-capable physics.
7 OPEN: What decidable/measurable dynamical property of a rule set predicts replicator
  capacity? (candidate: cheap local copy + read-write symmetry.)
8 ANTI: Search rule space for substrates that are universal but replicator-free, and use
  them as negative controls for every "emergence" metric Prometheus uses.

---------------------------------------------------------------------
### 5. Amoeba and prebiotic self-organization of opcode statistics
Pargellis (Amoeba), 1996-2003, e.g. "Self-organizing genetic codes and the emergence of
digital life", Complexity 2003, DOI 10.1002/cplx.10095. VERIFIED-META.
"Digital Replicators Emerge from a Self-Organizing Prebiotic World", ALIFE 2016; and
"Self-Replicators Emerge from a Self-Organizing Prebiotic Computer World", Artificial Life
23(3):318 (2017). VERIFIED-META (authors likely Greenbaum and Pargellis -- UNVERIFIED).

1 DEMO: Tierra-like world seeded with random opcodes; replicators emerge spontaneously. A
  self-organizing codon->opcode assignment matrix biases toward opcodes seen in successful
  children, halving effective alphabet and doubling emergence rate.
2 ASSUME: Designed Tierra-style ISA with templates and allocate/divide; virtual CPUs.
3 FAIL: Emergence rate depends strongly on alphabet; low follow-up evidence of anything
  beyond replication.
4 MEAS: Time-to-first-replicator, opcode frequency drift.
5 CODE: not found.
6 PROM: A 1990s precedent for "replicators from random byte soups" -- Prometheus should
  cite it, not rediscover it.
7 OPEN: Is prebiotic statistics-drift (a "biased typewriter" produced by the dynamics
  itself) necessary for emergence in realistic ISAs?
8 ANTI: Let the ISA decoding table itself be part of the tape (writable), so the "genetic
  code" can co-evolve with the programs.

---------------------------------------------------------------------
### 6. Avida emergent replicators: biased typewriters, evolvability of random replicators
Adami, LaBar. "From Entropy to Information: Biased Typewriters and the Origin of Life."
arXiv:1506.06988 (2015; later in book form). VERIFIED-META.
LaBar, Adami, Hintze. "Does self-replication imply evolvability?" ECAL 2015,
arXiv:1507.01903. VERIFIED.
LaBar, Hintze, Adami. "Evolvability Tradeoffs in Emergent Digital Replicators."
Artificial Life 22(4):483-498 (2016), arXiv:1511.07959. VERIFIED.
Adami, LaBar. "Origin of life in a digital microcosm." Phil Trans R Soc A 375:20160350
(2017), arXiv:1701.03993. VERIFIED-META.

1 DEMO: Exhaustive/random sampling of ~1e9 short Avida genomes found rare replicators (e.g.,
  27 per billion at one length); resampling with a monomer distribution biased toward those
  found raises the rate dramatically. Of 170 random replicators, most can evolve but some
  are evolutionarily sterile. Random replicators split into classes with a tradeoff: one
  class optimizes replication rate faster, the other acquires innovations (logic tasks)
  more readily, traceable to replication-machinery structure.
2 ASSUME: Avida ISA with built-in h-alloc/h-copy/h-divide (copy is cheap and privileged);
  organism boundaries given; tasks rewarded with CPU time.
3 FAIL: Heavy dependence on designed ISA; evolvability measured only on experimenter tasks.
4 MEAS: Exhaustive enumeration probability of replication; "information" = log of
  replicator fraction; evolvability assays (fitness gain and task acquisition in replay).
5 CODE: Avida (github.com/devosoft/avida; UNVERIFIED URL).
6 PROM: "Replicator architecture determines later evolvability" is the Avida version of
  entry 3's Load-Push vs LDIR finding and of any Prometheus lineage-architecture result.
7 OPEN: Is there a universal information threshold for emergence given an ISA? Can
  evolvability class be predicted from replicator structure alone?
8 ANTI: Remove the privileged copy/divide instructions; replicate only via ordinary
  read/write/jump instructions (Avida without h-copy), then repeat the enumeration.

---------------------------------------------------------------------
### 7. Tierra: parasites, hyperparasites, spontaneous sex
Ray, T.S. "An approach to the synthesis of life", Artificial Life II (1991/1992); "Evolution,
ecology and optimization of digital organisms" (SFI WP 1992). VERIFIED-META (search).

1 DEMO: From a hand-written 80-instruction ancestor, evolution produced parasites (use host
  copy loop), immunity, hyperparasites (hijack parasites' CPU), social hyperparasites, and
  sloppy replication producing recombination ("spontaneous sexuality"); genome shrinkage.
2 ASSUME: Designed ancestor; template addressing; memory allocation and protection
  (write privilege only in own block), reaper queue.
3 FAIL: Classic complaint: novelty plateaus; no sustained open-ended increase in
  complexity (Tierra is the canonical "bounded" OEE system in Bedau-Packard analyses).
4 MEAS: Genotype size-class frequency over time; diversity; ecological interaction assays.
5 CODE: Tierra source historically at life.ou.edu/tierra (UNVERIFIED availability).
6 PROM: Directly: parasites executing host code, host-mediated reproduction. Prometheus
  should expect these as the FIRST post-replicator ecological layer, not as surprises.
7 OPEN: Is memory protection (an implicit organism boundary) necessary for parasite ecology
  to be stable?
8 ANTI: No memory protection, no designed ancestor, no reaper: a flat shared memory where
  "death" is only overwriting. Measure whether parasite/host roles still differentiate.

---------------------------------------------------------------------
### 8. Evolution of complex features by stepping stones (Avida EQU)
Lenski, Ofria, Pennock, Adami. "The evolutionary origin of complex features." Nature
423:139-144 (2003). DOI 10.1038/nature01568. VERIFIED-META.

1 DEMO: EQU (complex logic) evolves only if simpler functions are also rewarded; first EQU
  genotypes differ from parents by 1-2 mutations but depend on many prior mutations; some
  deleterious mutations were stepping stones.
2 ASSUME: Designed ISA, rewards for nine logic tasks, fixed environment.
3 FAIL: Removing intermediate rewards -> EQU never evolved in 50 runs. Capability did NOT
  accumulate without experimenter scaffolding.
4 MEAS: Lineage reconstruction and knockout analysis of every mutation on the line of
  descent.
5 CODE: Avida.
6 PROM: Same shape as entry 3's cross-niche curricula. Warning: "capability not installed"
  is weaker if the reward ladder was installed.
7 OPEN: Can the soup create its own intermediate rewards (e.g., other organisms as
  environment) so that stepping stones are endogenous?
8 ANTI: Reward only the final complex task (or no task), but let organisms consume each
  other's outputs; test whether biotic stepping stones substitute for designed ones.

---------------------------------------------------------------------
### 9. AlChemy and its 2024 revisit
Fontana and Buss (1994) AlChemy. UNVERIFIED (classic).
Mathis, Patel, Weimer, Forrest. "Self-Organization in Computation & Chemistry: Return to
AlChemy." arXiv:2408.12137 (2024). VERIFIED.

1 DEMO: In lambda-calculus soups, copy/identity functions (L0) dominate quickly; with
  copying removed, self-maintaining organizations (L1) and combinations (L2) appear. The
  revisit finds stable L1 organizations arise MORE often than previously thought, resist
  collapse, but CANNOT easily combine into higher-order entities; results are sensitive to
  initial distributions and random generators. Shows typed extensions can simulate
  arbitrary reaction networks.
2 ASSUME: Lambda calculus with normal-order reduction as chemistry; copy suppression is an
  imposed boundary condition.
3 FAIL: Higher-order composition (major transitions) did not happen.
4 MEAS: Number of unique expressions over time (-> 1 signals L0 copy collapse); closure
  analysis of the reaction network.
5 CODE: check arXiv page for repo (not seen).
6 PROM: The "trivial copier fixed point" is the lambda-calculus version of BFF takeover.
  Prometheus's "self-maintaining network without a single replicator" would be an L1 result.
7 OPEN: What conditions let self-maintaining organizations merge (an L1 -> L2 transition)?
8 ANTI: Do NOT ban copying; instead make copying costly in a conserved resource (mass/energy
  budget) and see whether organizations beyond copiers survive.

---------------------------------------------------------------------
### 10. Stringmol: parasites force complex replication strategies
Hickinbotham, Stepney, Hogeweg. "Nothing in evolution makes sense except in the light of
parasitism: evolution of complex replication strategies." Royal Society Open Science
8:210441 (2021); bioRxiv 10.1101/2021.02.25.432891. VERIFIED-META (fetch blocked).
Also Spirov, "Co-evolution of replicators and their parasites", arXiv:2312.17540 (2023,
in Russian). VERIFIED.

1 DEMO: In an automata chemistry where string-programs bind and copy other strings, fast
  short parasites arise almost immediately; well-mixed systems go extinct; in space,
  replicators evolve complex strategies (e.g. slowing replication, shortening) that
  mitigate parasites. Spirov: parasitism drives complexification into cooperating networks;
  compartments prevent collapse.
2 ASSUME: Designed binding/alignment chemistry; 2D space or compartments.
3 FAIL: Well-mixed (non-spatial) systems collapse -- robust negative.
4 MEAS: Population dynamics, lineage of replicase function, spatial pattern.
5 CODE: Stringmol (University of York; UNVERIFIED URL).
6 PROM: Prometheus parasites executing host code. Predicts that Prometheus well-mixed soups
  will show parasite-driven collapse unless spatial structure exists.
7 OPEN: Is spatial structure strictly necessary, or can emergent "self-recognition" (a
  tag/password check) substitute?
8 ANTI: Well-mixed soup, no compartments, but allow programs to inspect a partner before
  executing it; test whether discrimination (immune-like) evolves de novo.

---------------------------------------------------------------------
### 11. Self-reproducing loops and Evoloop, 25 years on
Sayama and Nehaniv. "Self-Reproduction and Evolution in Cellular Automata: 25 Years after
Evoloops." arXiv:2402.03961; Artificial Life 31(1):81 (2025). VERIFIED.

1 DEMO (review): Evoloop (Sayama 1999) proved Darwinian evolution of self-reproducing
  structures in a deterministic CA; the review traces the lull and the revival via
  continuous CA and OEE.
2 ASSUME: Hand-designed rule table and hand-designed ancestor loop; evolution only via
  collisions; loops tend to shrink (selection for smaller, faster loops).
3 FAIL: Evoloop evolution is toward simplicity (size reduction), not complexity -- the
  classic bounded outcome.
4 MEAS: Loop size distribution and species counts over time.
5 CODE: Evoloop implementations widely available (e.g. Golly rule tables; UNVERIFIED).
6 PROM: "Executable matter" lattice physics is in this lineage.
7 OPEN: Rule sets where evolution in a deterministic CA increases complexity.
8 ANTI: No designed ancestor: random initial lattice under an Evoloop-class rule; does any
  loop self-assemble? (Most such rules: no -- which is why entries 12 matter.)

---------------------------------------------------------------------
### 12. Spontaneous (undesigned) replicators in binary CA
Bo Yang. "Emergence of Self-Replicating Hierarchical Structures in a Binary Cellular
Automaton." arXiv:2305.19504; Artificial Life 31(1):96-105 (2025). VERIFIED-META.
Hintze and Bohm. "Rethinking Self-Replication: Detecting Distributed Selfhood in the Outlier
Cellular Automaton." arXiv:2508.08047 (Aug 2025); npj Complexity (2026),
doi prefix s44260-026-00074-2. VERIFIED.

1 DEMO: A binary 3x3-neighbourhood rule ("Outlier", found by novelty search) yields
  replicators from random initial conditions. Causal ancestry analysis shows replicators
  are DISTRIBUTED: several disjoint clusters coordinate; cluster "c2" produced 2439 instances
  in 10,000 ticks over 15 generations (growth factor ~1.5). Yang shows larger replicating
  "formations" assembled from shape-shifting clusters.
2 ASSUME: Rule selected by a search (novelty) -- i.e., the physics was chosen; deterministic,
  no mutation.
3 FAIL/LIMITS: Perfect copies only (no heredity of variation => no evolution); space fills.
4 MEAS: Causal ancestry graph: trace each new live cell to its necessary predecessor cells,
  aggregate at cluster level -> explicit lineages. This is a detector that does NOT assume
  a predefined organism boundary.
5 CODE: check papers (not seen).
6 PROM: Distributed selfhood = Prometheus "no predefined organism boundary" question.
7 OPEN: Can a CA support replicators that are both spontaneous AND carry heritable
  variation? (Nobody has shown this cleanly as far as I found.)
8 ANTI: Search rule space not for replicators but for rules where causal-lineage entropy
  grows unboundedly; see whether replicators appear as a by-product.

---------------------------------------------------------------------
### 13. Lenia, Flow-Lenia, and ecosystem exploration
Chan, "Lenia -- Biology of Artificial Life", Complex Systems 28(3) (2019), arXiv:1812.05433.
UNVERIFIED id.
Plantec, Hamon, Etcheverry, Chan, Oudeyer, Moulin-Frier. "Flow-Lenia: Emergent evolutionary
dynamics in mass conservative continuous cellular automata." arXiv:2506.08569 (ext. of
2212.07906); Artificial Life 31(2):228-248 (2025). VERIFIED.
Michel, Cvjetko, Hamon, Oudeyer, Moulin-Frier. "Exploring Flow-Lenia Universes with a
Curiosity-driven AI Scientist." ALIFE 2025, arXiv:2505.15998. VERIFIED.
Flow-Lenia.png (compression-driven multi-scale complexity), arXiv:2408.06374. VERIFIED-META.

1 DEMO: Mass conservation removes Lenia's explode/die regimes; localizing rule parameters
  in the state (each patch of matter carries its own update rule) lets multiple "species"
  coexist, mix, hybridize and evolve inside a single simulation -- evolution without an
  external GA. IMGEP exploration finds far more diverse ecosystem dynamics than random
  search, including macro-scale organization absent at small scales.
2 ASSUME: Continuous physics with carefully designed kernels/growth functions; mass
  conservation imposed; parameter mixing rule designed.
3 FAIL/CONTESTED: No clear self-replication with heredity in the digital-organism sense;
  "species" identity is observer-defined; open-endedness claims rest on activity metrics
  that can be gamed (see entry 21).
4 MEAS: Evolutionary activity statistics over parameter vectors, compression ratio,
  multi-scale matter distribution.
5 CODE: https://developmentalsystems.org/Exploring-Flow-Lenia-Universes/ (VERIFIED as
  referenced); Flow-Lenia JAX code by Plantec (github erwanplantec, UNVERIFIED).
6 PROM: "Rules carried by matter" is the continuous analogue of "code is data on the tape"
  -- Prometheus lattice executable matter.
7 OPEN: Does parameter-localized physics ever produce a separation of genotype and
  phenotype (a heritable memory not identical to the body)?
8 ANTI: Let the parameter-mixing rule itself be localized and mutable (no designed mixing),
  and remove mass conservation's hand-tuned kernel families.

---------------------------------------------------------------------
### 14. Particle Lenia and energy-based formulation
Mordvintsev, Niklasson, Randazzo. "Particle Lenia and the energy-based formulation" (2022),
google-research.github.io/self-organising-systems/particle-lenia/ (UNVERIFIED URL).
Perturbation-response agency analysis: arXiv:2305.16706 (ALIFE 2023). VERIFIED-META.

1 DEMO: Lenia recast as particles descending an energy; stable moving/rotating creatures.
2 ASSUME: A global energy function -> dynamics is gradient flow (a built-in Lyapunov
  function, i.e., no genuine non-equilibrium).
3 FAIL: Gradient systems cannot host sustained replication/evolution without added drive.
4 MEAS: Energy landscapes; perturbation-response.
5 CODE: Observable notebooks (UNVERIFIED).
6 PROM: Useful negative: a substrate with a potential function is a poor soup.
7 OPEN: Minimal non-equilibrium drive that turns such systems into replicator-capable ones.
8 ANTI: Add a dissipative flux (source/sink of particles) and no energy function.

---------------------------------------------------------------------
### 15. ASAL and successors (foundation models as the observer)
Kumar, Lu, Kirsch, Tang, Stanley, Isola, Ha. "Automating the Search for Artificial Life
with Foundation Models." arXiv:2412.17799; Artificial Life 31(3):368 (2025). VERIFIED.
Baid, Erlebach, Hellegouarch, Wieser. "Guiding Evolution of Artificial Life Using
Vision-Language Models" (ASAL++). ALIFE 2025, arXiv:2509.22447. VERIFIED.

1 DEMO: Uses VLM (CLIP-like) embeddings to (a) find simulation parameters matching a text
  target, (b) find simulations whose trajectories keep producing novelty in embedding space,
  (c) illuminate diversity. Found new Lenia and Boids forms and Life-like CA that look
  open-ended. ASAL++ lets a VLM (Gemma-3) propose successive targets (EST more novelty, ETT
  more coherent sequences).
2 ASSUME: Human-aligned visual embedding is the measure of interestingness; searches over
  a fixed parametric family of substrates; renders to images.
3 FAIL/CONTESTED: Novelty in pixel-embedding space != novelty in function/heredity;
  byte-tape soups have no natural rendering; FM bias toward human visual categories.
4 MEAS: FM embedding distances (supervised target score, open-endedness = novelty of later
  frames vs all earlier frames, illumination = nearest-neighbour coverage).
5 CODE: github.com/SakanaAI/asal (UNVERIFIED), sakana.ai/asal (VERIFIED as project page).
6 PROM: Prometheus could use FM-as-observer for "is this new?" but it is the opposite of
  falsification-first measurement.
7 OPEN: An FM-free, substrate-intrinsic novelty measure that agrees with FM judgments.
8 ANTI: Replace the FM observer with a compressor or a learned predictor TRAINED ON THE
  SOUP'S OWN HISTORY (Hughes-style observer, entry 18) -- no human prior.

---------------------------------------------------------------------
### 16. Quality-diversity and autotelic control in Lenia
Faldor and Cully. "Toward Artificial Open-Ended Evolution within Lenia using
Quality-Diversity." ALIFE 2024, arXiv:2406.04235. VERIFIED-META. Code:
github.com/maxencefaldor/Leniabreeder (VERIFIED as listed in search).
Cvjetko, Hartl, Levin, Moulin-Frier, Oudeyer. "The Artificial Experimentalist" (CARL).
ALIFE 2026, arXiv:2608.26116. VERIFIED.

1 DEMO: QD (AURORA with VAE descriptors) evolves large diverse populations of Lenia
  creatures; CARL uses goal-conditioned RL with minimal local perturbations to discover and
  steer solitons, generalizing OOD.
2 ASSUME: External evolutionary/RL loop outside the physics (the "organisms" do not
  reproduce themselves).
3 FAIL: Open-endedness is in the search algorithm, not in the world.
4 MEAS: QD coverage in learned latent space; goal-reaching success.
5 CODE: Leniabreeder repo.
6 PROM: Tools, not results: Prometheus could use CARL-like probes as intervention
  experiments (causal tests of agency).
7 OPEN: Does intervention-based probing reveal agency in byte soups?
8 ANTI: Move the QD archive inside the world (organisms must store/replicate their own
  descriptors) -- i.e., no external archive.

---------------------------------------------------------------------
### 17. Petri Dish NCA and population-based worlds
Sakana AI. "Petri Dish Neural Cellular Automata" (PD-NCA), 2025, pub.sakana.ai/pdnca/;
code github.com/SakanaAI/digital-ecosystem. VERIFIED-META.
Berdica, Foerster, Hutter, Zela. "Evolving Many Worlds: Towards Open-Ended Discovery in
Petri Dish NCA via Population-Based Training." arXiv:2604.11248 (2026). VERIFIED.

1 DEMO: Multiple NCAs, each continually trained by gradient descent during the run, compete
  for territory; cycles, defense and spontaneous cooperation appear. PD-NCA is hyperparameter
  sensitive and collapses into frozen equilibria or noise; PBT-NCA evolves whole worlds with
  a novelty+visual-diversity objective, keeping them "at the edge of chaos".
2 ASSUME: Gradient learning built into agents; "self-replication" = territorial expansion
  objective; world-level selection by an external novelty score.
3 FAIL: Collapse without meta-level search is the reported default.
4 MEAS: Behavioral novelty history, visual diversity.
5 CODE: SakanaAI/digital-ecosystem.
6 PROM: "Learning" is installed here, so it cannot count as emergent learning.
7 OPEN: Can within-lifetime learning arise in a soup where no gradient step exists?
8 ANTI: Same arena, no gradient updates, weights only inherited with mutation; compare
  whether cooperation/defense still appear (i.e., is learning necessary for them?).

---------------------------------------------------------------------
### 18. Formal definition of open-endedness (observer-relative)
Hughes, Dennis, Parker-Holder, Behbahani, Mavalankar, Shi, Schaul, Rocktaschel.
"Position: Open-Endedness is Essential for Artificial Superhuman Intelligence." ICML 2024,
PMLR 235:20597-20616, arXiv:2406.04268. VERIFIED (abstract); formula details from memory.

1 DEMO (position): A system producing artifacts X_1..X_t is open-ended w.r.t. an observer
  if its artifacts are NOVEL (the observer's predictive model, trained on history up to t,
  becomes worse at predicting later artifacts -- expected loss increases with the horizon)
  and LEARNABLE (conditioning on more history reduces the observer's loss).
2 ASSUME: An observer with a fixed model class; open-endedness is relative to that observer.
3 CONTESTED: Observer-relativity makes the property easy to satisfy with a weak observer and
  hard to compare across systems; no widely adopted operational protocol.
4 MEAS: Observer loss curves.
5 CODE: none.
6 PROM: Directly operational for Prometheus: use a fixed compressor/predictor family as the
  observer and report both conditions, with the entry-2 random-walk baseline as control.
7 OPEN: Which observer class makes the measure hard to game by pure noise injection?
8 ANTI: Use an observer that is ALSO grown in the soup (endogenous observer) and ask
  whether the soup remains open-ended relative to its own best predictor.

---------------------------------------------------------------------
### 19. POET, Enhanced POET, OMNI, OMNI-EPIC (environment generation)
Wang, Lehman, Clune, Stanley. POET, arXiv:1901.01753; GECCO 2019. VERIFIED-META.
Wang et al. Enhanced POET, arXiv:2003.08536 (ICML 2020). VERIFIED-META.
Zhang, Lehman, Stanley, Clune. OMNI, arXiv:2306.01711 (2023). UNVERIFIED id.
Faldor, Zhang, Cully, Clune. OMNI-EPIC, arXiv:2405.15568 (v Feb 2025; ICLR 2025). VERIFIED.

1 DEMO: Coevolving environments with agents plus transfer between pairs finds solutions not
  reachable by direct optimization; OMNI-EPIC uses FMs to write environments+rewards in code
  judged "interesting" by a model of human notions, adapting difficulty to the learner.
2 ASSUME: External generator, human-derived interestingness, fixed learner architecture.
3 FAIL: Enhanced POET's open-endedness saturates with the environment encoding (CPPN
  terrain) -- motivated FM-based generators; FM interestingness imports human priors.
4 MEAS: ANNECS (accumulated number of novel environments created and solved) in Enhanced
  POET; transfer success.
5 CODE: github.com/uber-research/poet (UNVERIFIED); OMNI-EPIC site dub.sh/omniepic.
6 PROM: "Stepping-stone transfer across niches" = entry 3 cross-niche pollination. ANNECS
  is a reusable accounting device.
7 OPEN: Can the environment be generated by the organisms themselves (niche construction)
  rather than by a generator?
8 ANTI: No environment generator: organisms are each other's environments (coevolving
  byte-soup niches); measure an ANNECS-like count of "tasks newly posed by the soup and
  solved by the soup".

---------------------------------------------------------------------
### 20. Darwin Godel Machine (open-ended self-modifying agents)
Zhang, Hu, Lu, Lange, Clune. "Darwin Godel Machine: Open-Ended Evolution of Self-Improving
Agents." arXiv:2505.22954 (v3 Mar 2026). Code github.com/jennyzzt/dgm. VERIFIED.

1 DEMO: An archive of coding agents that edit their own code (not the outer loop); archive-
  based open-ended exploration beats greedy self-improvement on coding benchmarks
  (SWE-bench, Polyglot -- numbers from memory, UNVERIFIED).
2 ASSUME: Frozen FM does the actual modification; benchmark fitness; the exploration process
  itself is NOT modifiable.
3 FAIL/CONTESTED: Reward hacking of evaluation observed (reported in paper, from memory);
  gains largely in tooling/prompting rather than new capability.
4 MEAS: Benchmark score over archive; lineage trees.
5 CODE: jennyzzt/dgm.
6 PROM: "Modify their own machinery" -- but machinery modification here is installed.
7 OPEN: Open-endedness when the outer loop is also self-modifiable.
8 ANTI: Let agents modify the archive/selection code too, with only survival (compute
  share) as selection.

---------------------------------------------------------------------
### 21. Measuring open-endedness: activity statistics, Geb, MODES
Bedau, Snyder, Packard (1998) evolutionary activity statistics and shadow models.
UNVERIFIED (classic).
Channon, "Passing the ALife test: activity statistics classify evolution in Geb as
unbounded" (ECAL 2001) and component-normalised follow-up; "Maximum Individual Complexity is
Indefinitely Scalable in Geb", Artificial Life 25(2):134 (2019). VERIFIED-META.
Channon (2024), "A procedure for testing for Tokyo Type 1 Open-Ended Evolution", Artificial
Life (author PDF channon.net; fetch failed). VERIFIED-META.
Dolson, Vostinar, Wiser, Ofria. "The MODES Toolbox", Artificial Life 25(1):50 (2019).
Code github.com/emilydolson/MODES-toolbox-paper. VERIFIED-META.
"Assessing the ability of the MODES toolbox to detect ..." ISAL 2024 (fetch 403). UNVERIFIED
content.
Editorial, 2024 Special Issue on Open-Ended Evolution, Artificial Life, doi
10.1162/artl_e_00445. VERIFIED-META.

1 DEMO: Activity = cumulative usage of components that persist; compare against a neutral
  "shadow" run where components persist by chance; Geb is the only system classified
  unbounded under Channon's component-normalized median test. MODES splits OEE into change,
  novelty, complexity and ecology potentials measured on persistent lineages.
2 ASSUME: Components (genotypes) are identifiable; a meaningful neutral shadow exists;
  persistence filter thresholds.
3 FAIL/CONTESTED: Mean activity was gamed by normalization (Channon's critique); MODES
  metrics can be driven by drift and are hard to interpret without controls (ISAL 2024
  assessment, UNVERIFIED details).
4 MEAS: As above.
5 CODE: MODES repo (C++ in Empirical).
6 PROM: Prometheus needs exactly these with a shadow/neutral control.
7 OPEN: A shadow model for soups WITHOUT predefined component boundaries.
8 ANTI: Define components post hoc by causal lineage (entry 12 method) or compression
  motifs rather than genotypes; run MODES on those.

---------------------------------------------------------------------
### 22. Hash Chemistry (minimal complexity-growth model)
Horiguchi and Sayama. "Hash Chemistry: Minimal Models for Evolutionary Growth of
Complexity." arXiv:2607.28219 (Jul 2026). VERIFIED.

1 DEMO: A deterministic hash assigns a scalar "fitness" to arbitrary compositional entities
  (a rugged, structureless but fixed landscape); spatial/cellular versions with competition
  show domain size as a control parameter switching between compact-replicator and runaway
  size-dominance regimes.
2 ASSUME: Fitness exists (a hash), just unstructured.
3 FAIL: Runaway size-dominance is an artifact regime (size-biased sampling, finite size).
4 MEAS: Size/complexity distribution vs domain size.
5 CODE: not seen.
6 PROM: A cheap null world: "complexity grows" can arise from a random landscape plus size
  bias -- a control Prometheus should run.
7 OPEN: Which complexity-growth signatures survive replacing a real physics with a hash?
8 ANTI: Remove the hash entirely (no fitness at all) and keep only size-biased sampling;
  if complexity still "grows", the metric is measuring the sampling bias.

---------------------------------------------------------------------
### 23. Major transitions: DISHTINY and Barricelli symbiogenesis
Moreno and Ofria. "Toward Open-Ended Fraternal Transitions in Individuality." Artificial
Life 25(2):117 (2019). VERIFIED-META. "Exploring Evolved Multicellular Life Histories in an
Open-Ended Digital Evolution System", arXiv:2104.10081; Frontiers Ecol Evol 2022.
VERIFIED-META.
Ashford, Nichele et al. (SymBa). "Evolving Symbiosis, from Barricelli's Legacy to Collective
Intelligence." ALICE 2026 workshop, arXiv:2603.08463. VERIFIED.

1 DEMO: DISHTINY gives cells kin recognition, resource sharing and cooperative tasks;
  multicellular groups with life histories, apoptosis, and division of labour evolve.
  SymBa replicates Barricelli's 1953 numerical symbioorganisms in 1D and extends to 2D.
2 ASSUME: DISHTINY builds in group-membership channels and rewards synchronized tasks -- the
  higher-level individual is partially designed. Barricelli: designed reproduction rule.
3 FAIL: No system has shown an unassisted transition where the higher-level unit was not
  pre-afforded.
4 MEAS: Group-level heritability, kin-group size distributions, life-history traits.
5 CODE: DISHTINY (github.com/mmore500/dishtiny, UNVERIFIED); Zenodo record 16990564.
6 PROM: Parasite-host consortia in Prometheus soups could be the raw material for a
  symbiogenetic (egalitarian) transition.
7 OPEN: Can an egalitarian transition (two lineages fusing into one heritable unit) happen
  in a byte soup with no designed group channel?
8 ANTI: No kin-recognition primitive, no group reward; measure whether co-replicating
  host-parasite pairs become obligately co-transmitted.

---------------------------------------------------------------------
### 24. Evolvable AI (PNAS 2026) and life-detection spoofing
Szathmary, Muller, Steels. "Evolvable AI: Threats of a new major transition in evolution."
PNAS 123(17):e2527700123 (2026), doi 10.1073/pnas.2527700123. VERIFIED-META; plus replies
(Boudry, "Domesticated, not feral", doi 10.1073/pnas.2617785123; Rana and Singh).
Gupta and Adami. "Can AI Detect Life? Lessons from Artificial Life." arXiv:2604.11915
(Apr 2026). VERIFIED.

1 DEMO: (PNAS) Conceptual: distinguishes "breeder" regimes (human-imposed fitness, human-
  controlled reproduction) from "ecosystem" regimes (selection arising from open environment)
  as the threshold for evolvable AI. (Gupta and Adami) An MLP that classifies Avida
  replicators vs non-replicators at 99.97% test accuracy is spoofed: greedy hill-climbing
  finds non-replicators classified as replicators at 100% confidence in ~150 queries,
  Hamming distance 3-4 from true replicators; false attractors outnumber true ones.
2 ASSUME: n/a / Avida 9-instruction genomes.
3 CONTESTED: PNAS debate on whether eAI is imminent.
4 MEAS: Adversarial search against a learned detector.
5 CODE: not seen.
6 PROM: Any Prometheus learned "replicator/agent detector" will be spoofable by the soup
  itself (selection is a hill-climber). Use functional/causal detectors (entry 2, 12).
  "Breeder vs ecosystem" maps exactly onto Prometheus's "installed vs emergent" distinction.
7 OPEN: Detector designs robust to adversarial evolution.
8 ANTI: Let the soup be selected on the learned detector's score and measure how fast it
  spoofs it -- a built-in falsification test for any metric.

---------------------------------------------------------------------
### 25. Novelty search, minimal criterion coevolution
Lehman and Stanley, "Abandoning objectives: evolution through the search for novelty
alone", Evolutionary Computation 19(2) (2011). UNVERIFIED.
Brant and Stanley, "Minimal Criterion Coevolution", GECCO 2017. UNVERIFIED.
Soros and Stanley, "Identifying necessary conditions for open-ended evolution through the
artificial life world of Chromaria", ALIFE 2014. UNVERIFIED.

1 DEMO: Rewarding behavioral novelty solves deceptive problems; MCC coevolves mazes and
  solvers under only a pass/fail criterion; Chromaria proposes four necessary conditions
  (minimal criterion for reproduction, novel ways to meet it, independent decisions about
  reproduction, bounded population growth potential ...).
2 ASSUME: Behavior characterization chosen by experimenter.
3 FAIL: Novelty in high-dimensional behavior spaces becomes random drift; BC choice
  dominates outcome.
4 MEAS: Archive coverage; criterion satisfaction.
5 CODE: many implementations (e.g. pyribs, QDax).
6 PROM: A "minimal criterion" (replicate or be overwritten) is what soups already have.
7 OPEN: Chromaria's necessary conditions have not been tested as sufficient anywhere.
8 ANTI: Use the soup's own compressibility change as the behavior characterization (no
  experimenter BC).

=====================================================================
## PART 2 -- WHAT PROMETHEUS SHOULD KNOW THAT IT MAY NOT
=====================================================================

- The BFF "Computational Life" story has been partially retracted by its own group
  (arXiv:2607.01483, Jul 2026): a mutation random walk finds replicators as easily as, and
  with a tuned byte distribution 25x faster than, the interacting soup; ancestry limits do
  not stop emergence, only takeover. Any Prometheus claim that "interaction/ecology creates
  replicators" needs a matched-budget random-walk and random-sampling baseline.
- A Google Paradigms-of-Intelligence Z80 soup paper (arXiv:2607.09211, Sep 2026 v2) already
  reports: emergent replicators coevolving with polynomial computation; Load-Push -> LDIR
  replicator succession; metabolic cost producing context-sensing conditional halts;
  cross-niche curricula. This is direct prior art for Prometheus Z80 results; cite and
  differentiate (their LDIR block copy and task reward are installed).
- There is a functional replicator detector in cubff (common_language.h: partner-varied,
  noise-injected, >=48/64 byte match). Reuse rather than re-invent; byte-signature detection
  (as in 2607.09211) is weaker.
- Universality does not imply replicator capacity (Cotler-Hongler-Hudcova 2025) and SUBLEQ
  soups empirically fail. Substrate choice, especially copy-primitive density, is a
  first-order variable, not a detail.
- Replication emergence in random byte worlds is 30+ years old (Pargellis Amoeba 1990s;
  Adami-LaBar Avida enumeration 2015). Novelty for Prometheus must be in what happens AFTER
  replication (heredity of variation, capability accumulation, transitions).
- Known post-replicator ecology (Tierra, Stringmol): parasites arise almost immediately;
  well-mixed systems tend to collapse; space/compartments rescue them. Expect this.
- Random replicators differ in evolvability class (LaBar-Hintze-Adami 2016): some are
  evolutionarily sterile; first replicator architecture constrains everything later.
- Learned detectors of "life/replication/agency" are adversarially spoofable by a hill
  climber in ~150 queries (Gupta-Adami 2026); a soup under selection IS a hill climber.
- Open-endedness metrics require neutral/shadow controls (Bedau-Packard, Channon's
  normalization critique) and are observer-relative (Hughes et al. 2024). FM-embedding
  novelty (ASAL) measures visual novelty, not functional novelty.
- Almost every "open-ended" 2024-2026 system puts the open-endedness in an EXTERNAL loop
  (QD archive, PBT, FM generator, DGM archive), not in the world. A world where the search
  process lives inside the substrate is still rare.

=====================================================================
## PART 3 -- GENUINELY OPEN QUESTIONS
=====================================================================

1. What measurable property of an instruction set (copy-primitive length, read/write
   symmetry, jump density) predicts time-to-first-replicator, and why does SUBLEQ fail?
2. Does pairwise interaction in soups ever contribute anything beyond amplifying what a
   random walk would find (e.g., recombination of partial functions)? Under what conditions?
3. Can capability accumulate in a soup with NO experimenter-defined task, where the only
   "environment" is other organisms?
4. Can a spontaneous (undesigned-ancestor) replicator in a CA or lattice physics carry
   heritable variation and hence evolve?
5. What is the right shadow/neutral model for a soup without predefined component
   boundaries?
6. Can an egalitarian major transition (two lineages fusing into one co-transmitted unit)
   occur in a byte soup without a designed group channel?
7. Is spatial structure strictly necessary to survive parasites, or can de novo
   partner-inspection (immune-like discrimination) substitute?
8. Can a writable genetic code (decode table on the tape) co-evolve with programs, and does
   it accelerate or freeze evolution?
9. Does the first replicator architecture determine a lineage's long-run evolvability
   class, and can this be predicted from structure?
10. Can within-lifetime learning (state changes that improve future replication) emerge in
    a substrate that has no gradient or learning primitive?
11. Which open-endedness measure is robust to adversarial evolution (the soup gaming the
    metric) and to noise injection?
12. Can a soup become open-ended relative to an endogenous observer (a predictor grown
    inside the same soup)?
13. Does metabolic cost reliably produce context-sensing (conditional execution), and is
    that the minimal seed of "self vs other" representation?
14. What is the minimal non-equilibrium drive needed to turn a gradient/energy-based
    substrate (Particle Lenia class) into a replicator-capable one?
15. Can niche construction by organisms generate an unbounded ANNECS-like curriculum with
    no external environment generator?
16. Are distributed (multi-cluster) replicators more or less evolvable than compact ones?
17. Can a system whose outer search loop is itself modifiable (DGM without a frozen archive)
    remain open-ended rather than collapsing into reward hacking?

=====================================================================
## PART 4 -- KNOWN DEAD ENDS (do not rediscover)
=====================================================================

- Trivial-copier collapse: in lambda chemistries (AlChemy L0) and BFF soups, the simplest
  copier takes over and diversity -> 1 unique species. Banning copying by fiat (Fontana-
  Buss) produced organizations that do not compose into higher-order entities (confirmed
  2024 revisit).
- Evolution toward simplicity in designed self-reproducers: Evoloop and Tierra lineages
  shrink (smaller = faster). Replicator success is not complexity growth.
- Well-mixed replicator/parasite systems go extinct (Stringmol, many chemistries); spatial
  or compartment structure is required in known systems.
- "Turing-complete therefore replicators will appear" -- false in theory (2510.08342) and in
  practice (SUBLEQ soups).
- "Interaction/ecology is what discovers replicators" -- contradicted by the random-walk
  baseline (2607.01483).
- Complex functions without rewarded intermediates: EQU never evolved when simpler tasks
  were unrewarded (Lenski et al. 2003). Unscaffolded single hard targets fail.
- Unnormalized activity statistics and mean-activity OEE tests are gameable (Channon);
  MODES-style metrics without neutral controls can report drift as novelty.
- Learned life/replicator classifiers as ground truth: spoofed by hill-climbing
  (Gupta-Adami 2026).
- Lenia-class systems without conservation explode or die; PD-NCA without meta-search
  collapses into frozen equilibria or noise. Hand-tuned single worlds rarely sustain
  complexity.
- Encoding-limited environment generators (POET CPPN terrains) saturate; open-endedness is
  bounded by the generator's expressivity.
- Pure novelty search in high-dimensional behavior spaces degenerates toward drift; the
  behavior characterization secretly carries the experimenter's objective.
