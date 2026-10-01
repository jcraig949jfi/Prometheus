# PRIOR ART C: Open-Ended Evolution, Automatic Curricula, Quality-Diversity, Coevolution, ALife

Seat: Aphrodite (science of recursive self-improvement)
Compiled: 2026-09-27 by a literature-raid sub-agent (WebSearch/WebFetch).
Scope: cluster C = open-ended evolution (OEE), automatic curriculum / environment
generation (UED), quality-diversity (QD), novelty search, coevolution, artificial
life, theory of open-endedness, LLM-driven open-endedness, self-proposed task
curricula, representation expansion.

## 0. Verification policy and status legend

- [V-abs]  Bibliographic facts and the claim quoted were checked against the arXiv
           abstract page or publisher page during this raid.
- [V-full] The specific claim was checked against the full text (PDF extracted
           and searched) during this raid.
- [V-bib]  Existence/venue/authors verified by search result from a primary or
           index source; the finer claims attributed come from the abstract or
           from well-known content and were NOT re-read in full here.
- UNVERIFIED  Anything not confirmed from a primary source in this raid. Treat as
           a lead, not a citation.

Claims about "what was held fixed" and "failure modes" are the raid's analytical
reading of each work unless tagged [V-full]. Numbers are only given where seen.

---------------------------------------------------------------------------

## 1. Executive summary (decision-relevant)

1. The literature's single most consistent finding: open-ended generation of
   new opportunities stalls when EITHER the opportunity supply is exogenous and
   fixed, OR the representation (encoding of tasks or solutions) is bounded.
   Original POET plateaued (ANNECS flat after ~20k iterations) precisely because
   its hand-coded environment encoding "can only sustain a finite number of
   obstacle types" [V-full, Enhanced POET]. Aphrodite has BOTH limits at once:
   fixed external task supply and a fixed depth-2 DSL.
2. Aphrodite's qualification pipeline (discriminability + hostile tribunal +
   headroom vs pristine) is, in OEE terms, a minimal criterion (MC). Soros,
   Cheney & Stanley (2016) showed MC strictness decides "between complete
   stagnation (both with extreme strictness or complete relaxation) and orderly
   divergence" [V-full]. A pipeline that rejects most draws and only lets
   additive/subtractive families through is a strong candidate for the
   "extreme strictness" regime. This is testable by sweeping strictness.
3. Soros & Stanley's (2014) hypothesized necessary conditions for OEE include
   "the evolution of new individuals should create novel opportunities for
   satisfying the MC" and "potential size and complexity of phenotypes should be
   (in principle) unbounded" [V-bib]. Aphrodite violates both by design. The
   null result (G1 donors only meet tasks G1 explains and re-derive G1) is the
   PREDICTED outcome of this literature, not a surprise.
4. Hughes et al. (2024) define open-endedness as a stream of artifacts that is
   both novel (increasingly unpredictable to an observer's model) and learnable
   (more history makes them more predictable) [V-abs/V-full html]. They state a
   system trained on a FIXED dataset is not open-ended because the observer
   eventually models the whole distribution. Aphrodite's fixed stratified supply
   is a fixed dataset in exactly this sense.
5. Stepping stones must be rewarded. In Avida (Lenski et al. 2003), EQU evolved
   in 23/50 populations when simpler logic functions were also rewarded, and in
   0/50 when only EQU was rewarded [V-bib via Nature abstract + secondary
   sources]. If the qualification filter kills the intermediate families that
   would scaffold a G2 (e.g. multiplicative/modular hybrids), G2 is unreachable
   regardless of improver quality.
6. The "task supply vs improver" question has a standard experimental answer in
   this literature: the direct-optimization control. Enhanced POET showed the
   same optimizer (ES, and PPO) that fails on late-stage environments when
   trained directly CAN solve them when embedded in the open-ended process
   [V-full]. Combine that with planted-target (oracle supply) tests and a 2x2
   (supply regime x improver regime) factorial. Section 7(d).
7. Recent (2025-2026) self-play work converges on the same lesson for LLM
   self-improvement: pure self-generated curricula saturate or collapse (R-Zero
   degrades after a few iterations; pseudo-label accuracy fell to 63.0% by the
   third iteration) [V-abs html]; Liu et al. (2026) argue sustained self-play
   requires asymmetric co-evolution, capacity growth, and proactive intake of
   new information [V-abs]. Aphrodite's exact executor-verification is an
   advantage over label-noise-limited LLM self-play, but it has none of the three.

---------------------------------------------------------------------------

## 2. Per-work entries

Field template per work:
- Generator of new opportunities (and whether it failed)
- Task supply endogenous?
- Representation expanded?
- Held fixed
- Novelty / open-endedness measure
- Failure modes
- Code
- Verification

### 2.1 Theory and definitions of open-endedness

#### Hughes, Dennis, Parker-Holder, Behbahani, Mavalankar, Shi, Schaul, Rocktaschel (2024). "Position: Open-Endedness is Essential for Artificial Superhuman Intelligence." ICML 2024 (PMLR v235). arXiv:2406.04268.
- Definition: "a system is open-ended if and only if the sequence of artifacts it
  produces is both novel and learnable" relative to an observer O with a
  statistical model over artifacts X_t. Novelty: artifacts become increasingly
  unpredictable w.r.t. the observer's model (expected loss on future artifacts
  does not converge down). Learnability: conditioning on a longer history makes
  artifacts more predictable.
- Worked failure cases: a noisy TV (learnable, loses novelty once the
  distribution is learned); randomly switched TV channels (novel, not learnable
  since history does not predict the next channel); AlphaGo is open-ended to a
  human observer (novel moves that humans can learn from). Foundation models
  trained on fixed data are "not open-ended by our definition."
- Why systems stop: task/environment space exhausted (they cite AdA's novelty
  plateau), capability saturating challenge space, observer capacity limits.
- Relevance: gives Aphrodite an OPERATIONAL, observer-relative test. Take the
  observer = the donor's library (or a pristine solver's predictive model of
  which schema explains the next solved task). Novelty = rising surprise of
  newly solved tasks under the library; learnability = surprise falls once those
  tasks are added. G1-re-derivation = zero novelty under a G1 observer.
- Code: none (position paper).
- Verification: [V-abs] arXiv + PMLR; definition and TV examples [V-full html via WebFetch].

#### Banzhaf, Baumgaertner, Beslon, Doursat, Foster, Hu, et al. (2016). "Defining and simulating open-ended novelty: requirements, guidelines, and challenges." Theory in Biosciences 135:131-161.
- Classifies novelty: Type-0 "variation" (new instance within the model),
  Type-1 "innovation" (changes the model), Type-2 "emergence" (changes the
  meta-model).
- Relevance: a "new schema" that is still a depth-2 expression in the fixed DSL
  is Type-0 relative to the DSL, but can be Type-1 relative to the donor's
  library. Aphrodite should state which observer/model level its "genuinely NEW
  schema G2" is novel against. With the DSL fixed, Type-2 is impossible by
  construction.
- Code: none. Verification: [V-bib] Springer + PubMed listing; type names from index summary.

#### Taylor, Bedau, Channon, Ackley, Banzhaf, Beslon, et al. (2016). "Open-Ended Evolution: Perspectives from the OEE Workshop in York." Artificial Life 22(3):408-423.
- Key methodological points: pluralism (more than one kind of OEE) and
  separating observable behavioral HALLMARKS from hypothesized MECHANISMS.
  Hallmarks listed include ongoing adaptive novelty (new properties, new
  interactions, new global patterns), plus (per the paper) ongoing growth of
  complexity, and major transitions. Only the first hallmark was confirmed in
  the snippet read.
- Relevance: Aphrodite's "recursion" claim is a mechanism claim; it needs a
  hallmark measurement (Section 7(c)) independent of the mechanism.
- Verification: [V-bib] MIT Press page; hallmark list beyond "ongoing adaptive
  novelty" is UNVERIFIED in this raid.

#### Packard, Bedau, Channon, Ikegami, Rasmussen, Stanley, Taylor (2019). "An Overview of Open-Ended Evolution: Editorial Introduction to the Open-Ended Evolution II Special Issue." Artificial Life 25(2):93-103. arXiv:1909.04430.
- Provides a "simplified categorization of OEE" (not detailed in abstract).
  Special issue includes MODES (below), Channon's Geb scalability paper, Stanley's
  "Why open-endedness matters", and Hintze's "Open-endedness for the sake of
  open-endedness".
- Verification: [V-abs]. The categorization itself is UNVERIFIED here.

#### Adams, Zenil, Davies, Walker (2017). "Formal Definitions of Unbounded Evolution and Innovation Reveal Universal Mechanisms for Open-Ended Evolution in Dynamical Systems." Scientific Reports 7:997. arXiv:1607.01750.
- Defines unbounded evolution (non-repeating within Poincare recurrence time of
  an isolated system) and innovation (trajectories not observed in isolated
  systems). Tests CA variants whose update rules vary in time: externally
  driven, random rule switching, state-dependent (self-referential).
- Result (quoted): "State-dependent dynamics ... statistically out-performs
  other candidate mechanisms, and is the only mechanism to produce open-ended
  evolution in a scalable manner." Random rule mutation converged to trivial
  oscillations; external driving declined with system size.
- Relevance: Aphrodite's improvement rule and selection rule are fixed and
  external. The one mechanism that scaled here is rules that depend on the
  system's own state. Suggests a variant where the task generator's or the
  schema-proposal rule's parameters are a function of the library state.
- Verification: [V-abs via PMC full text summary].

#### Bedau, Snyder, Packard (1998). "A classification of long-term evolutionary dynamics." Artificial Life VI, MIT Press.
- Evolutionary activity statistics: track each component's (gene/genotype/
  schema) cumulative usage ("activity"), compare against a neutral "shadow" run,
  classify dynamics by cumulative activity, new-activity rate, diversity.
  Classes (as tabulated in MODES Table 1): class 1 none; class 2 "uncreative";
  class 3 bounded (positive novelty, bounded diversity); class 4 unbounded
  (positive novelty, unbounded diversity). Channon's Geb was the first ALife
  system classified unbounded.
- Relevance: directly portable. Components = schemas in the library; activity =
  cumulative number of solved tasks each schema is used in; shadow run = a
  donor whose inherited library is randomly permuted/neutral. Aphrodite's
  current result would plausibly read as class 2/3.
- Verification: [V-bib] (ALife VI citation); class table [V-full] as reproduced in MODES.

#### Dolson, Vostinar, Wiser, Ofria (2019). "The MODES Toolbox: Measurements of Open-Ended Dynamics in Evolving Systems." Artificial Life 25(1):50-73.
- Four hallmarks with metrics: change potential, novelty potential,
  complexity potential, ecological potential. All metrics are computed AFTER a
  persistence filter: only components whose descendants persist t generations
  count ("to focus only on the adaptive products of evolution"); shadow runs are
  an alternative filter. Novelty = count of persistent components never seen
  before in the run. Complexity = max information-theoretic complexity of any
  component. Tested on NK landscapes and Avida.
- Relevance: the persistence filter is exactly the guard Aphrodite needs
  against counting transient "novel" schemas that are not inherited/used.
- Code: https://github.com/emilydolson/MODES-toolbox-paper
- Verification: [V-full] (PDF extracted).

#### Soros & Stanley (2014). "Identifying Necessary Conditions for Open-Ended Evolution through the Artificial Life World of Chromaria." ALIFE 14, MIT Press.
- Four hypothesized necessary conditions: (1) individuals must meet a
  nontrivial minimal criterion (MC) before reproducing; (2) the evolution of new
  individuals should create novel opportunities for satisfying the MC; (3)
  decisions about how and where individuals interact with the world should be
  made by the individuals themselves; (4) the potential size and complexity of
  phenotypes should be (in principle) unbounded. Chromaria stagnates when any
  one is removed.
- Relevance: the most direct checklist against Aphrodite. (1) present
  (qualification + verification). (2) ABSENT: tasks do not arise from solvers.
  (3) ABSENT: donors do not choose which tasks to face. (4) ABSENT: depth-2 DSL.
- Caveat: "necessary" is hypothesized and supported in one ALife world.
- Verification: [V-bib]; the four conditions text via a search-result quote of
  the paper; not re-read in full.

#### Soros, Cheney, Stanley (2016). "How the Strictness of the Minimal Criterion Impacts Open-Ended Evolution." ALIFE 2016.
- Main result (quoted): MC strictness "can profoundly affect open-ended dynamics,
  ultimately deciding between complete stagnation (both with extreme
  strictness or complete relaxation) and orderly divergence." Warns that MCs are
  often implicit and easy to overlook.
- Relevance: Aphrodite's qualification filter is an explicit, very strict MC.
  Sweep it.
- PDF: https://www.uvm.edu/neurobotics/pubs/pdf/2016_SorosCheneyStanley_HowTheStrictnessOfTheMinimalCriterionImpactsOpenEndedEvolution_ALIFE.pdf
- Verification: [V-full].

#### Stanley & Lehman (2015). "Why Greatness Cannot Be Planned: The Myth of the Objective." Springer.
- Thesis: ambitious objectives are deceptive; stepping stones to them rarely
  resemble them; search by novelty/interestingness collects stepping stones.
- Relevance: Aphrodite's headroom-vs-pristine criterion is objective-shaped
  (it asks "does the descendant beat pristine on this task?"). The book predicts
  that stepping stones toward G2 may show zero or negative headroom and be
  filtered out.
- Verification: [V-bib] (Springer/ACM listing; GPEM review).

#### Stanley, Lehman, Soros (2017). "Open-endedness: The last grand challenge you've never heard of." O'Reilly Radar. https://www.oreilly.com/radar/open-endedness-the-last-grand-challenge-youve-never-heard-of/
- Popular overview; restates MC and stepping-stone arguments. [V-bib] (URL seen in search; content not re-read).

#### Maynard Smith & Szathmary (1995). The Major Transitions in Evolution. Oxford University Press.
- Major transitions: new levels of individuality, new ways of storing and
  transmitting information. MODES explicitly welcomes a future metric for
  "potential to produce major transitions in individuality" [V-full in MODES].
- Relevance: the analogue of a major transition for Aphrodite would be the
  library becoming the unit of selection (schemas-of-schemas; a library entry
  becoming a new primitive). Not available in a fixed DSL.
- Verification: book citation UNVERIFIED in this raid (standard reference; not fetched).

### 2.2 Artificial life substrates

#### Ray (1991). "An approach to the synthesis of life." Artificial Life II, SFI Studies XI, Addison-Wesley, 371-408.
- Self-replicating machine-code organisms in shared memory; parasites and
  hyperparasites evolved; parasites act as sloppy replicators that recombine
  genomes. Opportunities generated by other organisms (ecological), not by a
  task list.
- Known limitation (community consensus, not re-verified): Tierra's dynamics
  largely plateau; mostly optimization of replication speed and size.
  UNVERIFIED as stated here.
- Endogenous supply: yes (other organisms are the environment). Representation:
  fixed instruction set, unbounded genome length.
- Code/paper: http://tomray.me/pubs/alife2/Ray1991AnApproachToTheSynthesisOfLife.pdf
- Verification: [V-bib].

#### Lenski, Ofria, Pennock, Adami (2003). "The evolutionary origin of complex features." Nature 423:139-144.
- Avida digital organisms; nine logic functions rewarded with CPU; EQU (most
  complex) evolved in 23 of 50 populations when simpler functions were also
  rewarded, 0 of 50 when only EQU was rewarded. Complex functions built on
  simpler ones; first EQU performers differed from parents by one or two
  mutations; some stepping-stone mutations were deleterious when they appeared.
- Generator: fixed, externally defined reward list (NOT endogenous). Held fixed:
  instruction set, task list, environment. Representation: fixed instruction
  set, variable genome.
- Relevance: this is Aphrodite's closest classic analogue: a fixed task list
  over a fixed instruction set. Its decisive control (reward intermediates vs
  reward only the target) is exactly the experiment Aphrodite lacks. Note the
  intermediate rewards ARE a curriculum designed by the experimenter; Lenski
  et al. argue this is not smuggling because the intermediates are not parts of
  a pre-specified EQU program and EQU arose by many different routes. That is a
  model of how to argue non-smuggling (Section 7(b)).
- Code: https://github.com/devosoft/avida
- Verification: [V-bib] Nature abstract; 23/50 and 0/50 from search summaries
  of the paper and Zaman 2014 (PLOS Bio) which restates 23/50. Recommend reading
  the full text before citing numbers externally.

#### Zaman, Meyer, Devangam, Bryson, Lenski, Ofria (2014). "Coevolution Drives the Emergence of Complex Traits and Promotes Evolvability." PLOS Biology 12(12):e1002023.
- Host-parasite coevolution in Avida greatly increased host complexity (incl.
  EQU) relative to no-parasite controls; a DIVERSITY of coevolving lineages, not
  simple escalation, was required; coevolved hosts were more evolvable.
- Relevance: the cleanest evidence that endogenous, coevolving opportunity
  supply beats a fixed task list, measured on the same complexity target.
- Data: https://datadryad.org/resource/doi:10.5061/dryad.485qq
- Verification: [V-bib] (PLOS page via search summary).

#### Channon (2019). "Maximum Individual Complexity is Indefinitely Scalable in Geb." Artificial Life 25(2):134-. Also Channon (2003/2006) Geb activity statistics.
- Geb classified unbounded by Bedau-Packard activity statistics (component-
  normalised variant). [V-bib] only.

#### Kumar, Lu, Kirsch, Tang, Stanley, Isola, Ha (2024/2025). "Automating the Search for Artificial Life with Foundation Models" (ASAL). arXiv:2412.17799.
- Uses vision-language FMs to (a) find simulations matching targets, (b) find
  simulations with open-ended temporal novelty in FM embedding space, (c)
  illuminate simulation spaces. Substrates: Boids, Particle Life, Game of Life,
  Lenia, NCA.
- Relevance: novelty measured as a trajectory in a learned embedding space - an
  instance of Hughes' observer. Aphrodite could embed schemas/tasks with a fixed
  encoder and track open-ended temporal novelty the same way.
- Verification: [V-abs]. Code URL not confirmed (UNVERIFIED).

#### Other ALife leads seen but not read: "Toward Artificial Open-Ended Evolution within Lenia using Quality-Diversity" arXiv:2406.04235; "Hash Chemistry: Minimal Models for Evolutionary Growth of Complexity" arXiv:2607.28219 (Sayama? author UNVERIFIED); "TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies" arXiv:2603.16910 (Paolo, Warner, Shahrzad, Hodjat, Miikkulainen, Meyerson, 2026) [V-abs; measurement method not stated in abstract].

### 2.3 Novelty search, quality-diversity, complexification

#### Lehman & Stanley (2011). "Abandoning Objectives: Evolution Through the Search for Novelty Alone." Evolutionary Computation 19(2):189-223.
- Rewards only behavioral novelty (distance to k-nearest in population + archive
  in a behavior-characterization space). Beats objective search on deceptive
  mazes and biped walking.
- Failure modes (well known): novelty in a large/uninformative behavior space
  becomes "pathological" (novel but useless); requires a hand-designed behavior
  characterization (BC) - that BC is where domain knowledge (and potentially
  the answer) is smuggled in.
- Relevance: Aphrodite has no novelty pressure at all; selection is headroom.
- Verification: [V-bib]. Paper PDF: https://www.cs.swarthmore.edu/~meeden/DevelopmentalRobotics/lehman_ecj11.pdf

#### Lehman & Stanley (2010). "Revising the evolutionary computation abstraction: minimal criteria novelty search." GECCO 2010.
- MC + novelty. [V-bib] via reference list in Soros et al. 2016.

#### Mouret & Clune (2015). "Illuminating search spaces by mapping elites." arXiv:1504.04909 (MAP-Elites).
- Archive grid over user-defined behavior descriptors; keep best per cell;
  mutate elites. Measures: coverage (cells filled), QD-score (sum of fitness).
- Failure: coverage is bounded by the grid; descriptors are hand-chosen;
  once the grid is full, "novelty" can only be quality improvement.
- Relevance: a QD archive over (top-level operator x depth x uses-first/last x
  constant-set) for SCHEMAS would show immediately whether the process is
  filling new cells or re-filling one.
- Code: https://github.com/resibots/pymap_elites
- Verification: [V-abs].

#### Stanley & Miikkulainen (2002). "Evolving Neural Networks through Augmenting Topologies." Evolutionary Computation 10(2):99-127 (NEAT).
- Starts minimal and complexifies (adds nodes/links) with historical markings
  and speciation protecting new structure. Canonical example of endogenous
  representation expansion. Stanley & Miikkulainen also "Competitive
  Coevolution through Evolutionary Complexification" (JAIR 2004; arXiv:1107.0037).
- Relevance: Aphrodite's DSL depth is fixed at 2; NEAT's lesson is that growth
  from minimal plus protection of new (initially worse) structure is what lets
  complexity rise. Protecting innovation = exempting new schemas from the
  headroom test for a grace period.
- Code (third party): https://github.com/CodeReclaimers/neat-python (cited in E-POET refs).
- Verification: [V-bib].

#### Lehman, Clune, Misevic, et al. (2018/2020). "The Surprising Creativity of Digital Evolution." arXiv:1803.03453; Artificial Life 26(2).
- Anecdote collection incl. specification gaming: evolution exploits
  measurement loopholes. Relevance: hostile tribunal is justified; but see 7(b).
- Verification: [V-bib].

#### Brant & Stanley (2017). "Minimal Criterion Coevolution: A New Approach to Open-Ended Search." GECCO 2017.
- Coevolves mazes and maze-solving agents. Agent reproduces if it solves at
  least one maze; maze reproduces if solved by at least one agent. No fitness,
  no behavior characterization, no novelty archive; mazes grow in size and
  complexity. Follow-ups: "Benchmarking open-endedness in minimal criterion
  coevolution" (GECCO 2019) and "Diversity preservation in minimal criterion
  coevolution through resource limitation" (GECCO 2020; limits how many agents
  may use each maze to prevent convergence).
- Relevance: THE most directly borrowable design for Aphrodite: tasks and
  schema-libraries coevolve under two minimal criteria; add resource
  limitation. Section 8, E2.
- Verification: [V-bib] (UCF STARS + ACM).

### 2.4 POET family and unsupervised environment design (UED)

#### Wang, Lehman, Clune, Stanley (2019). "Paired Open-Ended Trailblazer (POET)." GECCO 2019; arXiv:1901.01753.
- Generator: mutate environments (bipedal walker terrain parameters); keep
  children that pass an MC (not too hard, not too easy for current agents) and
  are novel; pair each env with an agent optimized by ES; periodically attempt
  TRANSFER of agents between envs (goal switching).
- Endogenous supply: yes. Representation: fixed hand-coded env parameters
  (stump height, gap width, roughness) -> bounded.
- Novelty: distance in the same hand-coded parameter space.
- Failure: plateau once encoding is exhausted (documented in E-POET).
- Code: https://github.com/uber-research/poet
- Verification: [V-abs].

#### Wang, Lehman, Rawal, Zhi, Li, Clune, Stanley (2020). "Enhanced POET: Open-Ended Reinforcement Learning through Unbounded Invention of Learning Challenges and their Solutions." ICML 2020; arXiv:2003.08536.
- Four changes: (1) PATA-EC, a domain-general environment characterization:
  evaluate ALL agents (population + archive) in the env, clip scores to MC
  bounds, rank-normalize to [-0.5, 0.5]; novelty = Euclidean distance to kNN
  (k=5) in this ranking space. Insight: "a novel and useful challenge should make
  novel distinctions among agents" (after de Jong & Pollack 2004). (2) cheaper
  transfer heuristic. (3) CPPN-encoded terrain (expressive, open encoding). (4)
  ANNECS: accumulated number of novel environments created and solved; to count,
  an env must pass the MC against all agents ever generated in the run and must
  eventually be solved.
- Key findings [V-full]: original POET "eventually loses its ability to
  innovate, as shown by its ANNECS curve plateauing after 20,000 iterations.
  Such stagnation occurs because the EE for original POET can only sustain a
  finite number of obstacle types with predefined regular shapes and limited
  variations." Enhanced POET's ANNECS rose nearly linearly. And: "the very same
  optimization algorithm, i.e. ES (and PPO too), that cannot solve any late-stage
  environment from POET runs, actually can solve them, but only if it is
  embedded within an open-ended algorithmic context."
- Also: original POET's conflation of EE (encoding) and EC (characterization)
  means "the system's output will be bound to exploration only within such
  prescripted possibilities."
- Relevance: (i) PATA-EC is a principled replacement for Aphrodite's "generator
  discriminability" and it is defined by how the solver POPULATION ranks on the
  task, i.e. endogenous. (ii) ANNECS is a direct open-endedness meter. (iii) The
  direct-optimization control is the supply-vs-improver discriminator.
- Code: https://github.com/uber-research/poet (stated in paper). Compute: 60k
  iterations ~12 days on 750 CPU cores.
- Verification: [V-full].

#### Dennis, Jaques, Vinitsky, Bayen, Russell, Critch, Levine (2020). "Emergent Complexity and Zero-shot Transfer via Unsupervised Environment Design" (PAIRED). NeurIPS 2020; arXiv:2012.02096.
- Adversary designs environments to maximize REGRET = antagonist return minus
  protagonist return; regret is ~0 for unsolvable envs (antagonist also fails),
  so the adversary cannot win by generating impossible tasks - the key control
  against pathological difficulty that a pure minimax adversary suffers.
- Held fixed: env parameterization, agent architecture.
- Code: https://github.com/facebookresearch/dcd (reimplementation of UED family).
- Verification: [V-abs].

#### Jiang, Grefenstette, Rocktaschel (2021). "Prioritized Level Replay" (PLR). ICML 2021; arXiv:2010.03934.
- Curates randomly generated levels; replays by estimated learning potential
  (TD-error / value-loss), with staleness term; induces an emergent curriculum.
- Code: https://github.com/facebookresearch/level-replay
- Verification: [V-abs].

#### Jiang, Dennis, Parker-Holder, Foerster, Grefenstette, Rocktaschel (2021). "Replay-Guided Adversarial Environment Design." NeurIPS 2021; arXiv:2110.02439.
- Dual Curriculum Design (DCD): PLR and PAIRED as special cases; Robust PLR
  trains only on curated replay levels (not on fresh random ones), giving
  minimax-regret guarantees at Nash equilibrium.
- Code: https://github.com/facebookresearch/dcd
- Verification: [V-abs].

#### Parker-Holder, Jiang, Dennis, Samvelyan, Foerster, Grefenstette, Rocktaschel (2022). "Evolving Curricula with Regret-Based Environment Design" (ACCEL). ICML 2022; arXiv:2203.01302.
- PLR + small EDITS (mutations) of high-regret levels -> complexity compounds
  from simple starts. Single agent, not a population.
- Relevance: ACCEL is the minimal "edit the tasks you are currently learning
  from" mechanism. For Aphrodite: mutate currently-headroom-positive tasks by a
  single operator substitution and re-qualify.
- Code: https://github.com/facebookresearch/dcd ; site https://accelagent.github.io/
- Verification: [V-abs].

#### Rutherford, Beukman, Willi, Lacerda, Hawes, Foerster (2024). "No Regrets: Investigating and Improving Regret Approximations for Curriculum Discovery." NeurIPS 2024; arXiv:2408.15099.
- Finding: practical regret approximations (e.g. positive value loss) do NOT
  correlate with true regret but with success rate; "a significant portion of an
  agent's experience comes from environments it has already mastered."
  Proposes Sampling For Learnability (SFL): train on levels with high
  learnability ~ p(1-p) (sometimes but not always solved). Evaluation: an
  adversarial CVaR-like protocol over worst-case levels.
- Relevance: Aphrodite's null result ("G1 donors only met tasks G1 already
  explains") is the same pathology: supply concentrated on already-mastered
  structure. The fix is to select tasks by p(1-p) under the CURRENT donor, not by
  pre-stratified operator family.
- Code: https://github.com/amacrutherford/sampling-for-learnability
- Verification: [V-abs].

#### Racaniere, Lampinen, Santoro, Reichert, Firoiu, Lillicrap (2019/2020). "Automated curricula through setter-solver interactions." ICLR 2020; arXiv:1909.12892.
- Setter proposes goals for solver; shows the importance of three setter
  losses: goal VALIDITY (achievable in principle), FEASIBILITY (appropriate
  difficulty for the current solver), COVERAGE (diversity).
- Relevance: Aphrodite's qualification covers validity and some feasibility
  but not coverage; coverage is exactly what stratification-by-operator tried
  to impose externally and the filter then undid.
- Verification: [V-abs]. (Author list beyond Racaniere UNVERIFIED.)

#### Matiisen, Oliver, Cohen, Schulman (2017). "Teacher-Student Curriculum Learning." arXiv:1707.00183.
- Teacher (bandit) picks subtasks by slope of the student's learning curve,
  using absolute value so forgetting is revisited. [V-bib] via E-POET references.

#### Portelas, Colas, Hofmann, Oudeyer (2019). "Teacher algorithms for curriculum learning of Deep RL in continuously parameterized environments" (ALP-GMM). CoRL 2019; arXiv:1910.07224.
- Continuous bandit over environment parameters; GMM fitted to absolute
  learning progress (ALP); discovers easy/hard/unlearnable regions without prior
  knowledge.
- Code: https://github.com/flowersteam/teachDeepRL
- Verification: [V-abs].

#### Oudeyer, Kaplan, Hafner (2007). "Intrinsic Motivation Systems for Autonomous Mental Development." IEEE Trans. Evolutionary Computation 11:265-286.
- Intelligent Adaptive Curiosity: region-wise learning-progress maximization;
  avoids both already-mastered and unlearnable (noise) regions. The conceptual
  root of LP curricula. [V-bib]. (Volume/pages from search summary; issue
  number UNVERIFIED.)

#### Gaven, Carta, Romac, Colas, Lamprier, Sigaud, Oudeyer (2025). "MAGELLAN: Metacognitive predictions of learning progress guide autotelic LLM agents in large goal spaces." ICML 2025; arXiv:2502.07709.
- LLM agent learns to predict its own competence and LP online, generalizing
  across semantically related goals; only method that fully mastered a large,
  evolving goal space in their testbed; avoids brittle expert-defined goal
  groupings.
- Relevance: Aphrodite's operator-stratification is an "expert-defined goal
  grouping" in MAGELLAN's sense. A learned competence predictor over tasks
  (features: I/O statistics) could replace it.
- Code: https://github.com/flowersteam/MAGELLAN
- Verification: [V-abs].

#### Pourcel, Colas, Molinaro, Oudeyer, Teodorescu (2023/2024). "ACES: Generating Diverse Programming Puzzles with Autotelic Generative Models." NeurIPS 2024; arXiv:2310.10692.
- Programming puzzles labeled by LLM with semantic skill descriptors; goal-
  directed generation targets under-covered descriptor combinations; difficulty
  = decreasing function of a fixed solver's success rate.
- Relevance: closest in spirit to Aphrodite's program world; coverage over
  skill combinations is a QD archive over tasks. Caveat: LLM labelers define the
  space (possible smuggling).
- Verification: [V-abs]. Code UNVERIFIED.

#### Mitsides, Faldor, Cully (2026). "Dreaming in Code for Curriculum Learning in Open-Ended Worlds" (DiCode). ICML 2026; arXiv:2602.08194.
- LLM writes environment-variation code to bridge competence gaps in Craftax;
  +17% mean return over strongest baseline. Project page:
  https://konstantinosmitsides.github.io/dreaming-in-code
- Verification: [V-abs].

### 2.5 LLM-driven open-endedness and models of interestingness

#### Zhang, Lehman, Stanley, Clune (2023/2024). "OMNI: Open-endedness via Models of human Notions of Interestingness." ICLR 2024; arXiv:2306.01711.
- Problem statement (quoted): "An Achilles Heel of open-endedness research is
  the inability to quantify (and thus prioritize) tasks that are not just
  learnable, but also interesting." Learning progress alone admits endless
  minor variants of learned tasks. OMNI uses an FM as a model of
  interestingness (MoI) on top of LP.
- Relevance: G1-rederivation is the "minor variation" failure; LP alone would
  not fix it. But note that the MoI is an external human prior (potential
  smuggling source).
- Project: https://www.jennyzhangzt.com/omni/ ; Verification: [V-abs].

#### Faldor, Zhang, Cully, Clune (2024/2025). "OMNI-EPIC: Open-endedness via Models of human Notions of Interestingness with Environments Programmed in Code." ICLR 2025; arXiv:2405.15568.
- FM writes environment + reward code; archive of successful AND failed tasks
  used as stepping stones (seeded with a few natural-language task seeds); code
  success detector (VLM success detection was not accurate enough); MoI check vs
  most-similar archived tasks (retrieval). Ablations: without archive; without
  MoI (LP only) - both reduce diversity. Metric ANNECS-OMNI: learnable, solved,
  and judged interesting vs previous tasks; "consistently increases."
- Stated limitations: single simulator (PyBullet); "cannot rule out that
  OMNI-EPIC is creating environments similar to those in its training data";
  short runs. Success detector agreed with humans 72.7%.
- Relevance: the "training-data memorization" caveat is the LLM-era form of
  "encoding the answer into the curriculum". Aphrodite's tiny DSL has the
  advantage that no such prior exists - if it uses no LLM proposer.
- Code: https://github.com/maxencefaldor/omni-epic
- Verification: [V-abs] + [V-full html summary].

#### Lehman, Gordon, Jain, Ndousse, Yeh, Stanley (2022). "Evolution through Large Models" (ELM). arXiv:2206.08896.
- LLM (diff model) as mutation operator inside MAP-Elites; Sodarace walkers;
  generated data used to train a new conditional model (bootstrapping to a
  domain unseen in pretraining).
- Code: https://github.com/CarperAI/OpenELM (OpenELM library, Bradley et al.)
- Verification: [V-abs].

#### Lange, Tian, Tang (2024). "Large Language Models As Evolution Strategies" (EvoLLM). GECCO 2024 companion; arXiv:2402.18381.
- LLM prompted with sorted discretized population proposes improved mean;
  in-context black-box optimizer. Improver-side only; no task generation.
- Verification: [V-abs]. Code UNVERIFIED.

#### Wang, Xie, Jiang, Mandlekar, Xiao, Zhu, Fan, Anandkumar (2023). "Voyager: An Open-Ended Embodied Agent with Large Language Models." arXiv:2305.16291.
- Automatic curriculum (GPT-4 proposes next task conditioned on inventory,
  biome, completed and FAILED tasks), ever-growing code skill library,
  iterative prompting with self-verification.
- Ablations [V-html]: random curriculum -> 93% fewer items discovered; manual
  curriculum underperforms (needs Minecraft expertise, ignores agent's live
  state); no skill library -> plateaus in later stages.
- Limitations: curriculum hallucinates unachievable tasks; GPT-4's Minecraft
  knowledge is a strong prior (smuggling concern).
- Relevance: Voyager is structurally Aphrodite's design (a skill library of
  code passed forward) PLUS an endogenous curriculum conditioned on the agent's
  state and failures. The ablation says the curriculum matters more than
  anything else measured.
- Code: https://github.com/MineDojo/Voyager ; site https://voyager.minedojo.org/
- Verification: [V-abs] + [V-html summary].

#### Zhang, Hu, Lu, Lange, Clune (2025). "Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents." ICLR 2026; arXiv:2505.22954.
- Self-modifying coding agents; archive of all agents; parent sampling from the
  archive (open-ended exploration) rather than hill-climbing; empirical
  validation on SWE-bench (20.0% -> 50.0%) and Polyglot (14.2% -> 30.7%);
  "significantly outperforms baselines without self-improvement or open-ended
  exploration."
- Held fixed: foundation model weights, benchmark task supply (external,
  fixed!). So DGM's open-endedness is in the improver, not the tasks; gains are
  bounded by the benchmark.
- Relevance: the DGM ablation pair (no self-improvement; no archive) is the
  template for Aphrodite's improver-side controls. DGM also shows that an
  archive with stepping-stone parents beats greedy descent even with fixed tasks.
- Code: https://github.com/jennyzzt/dgm
- Verification: [V-abs].

#### Lu, Hu, Clune (2025). "Automated Capability Discovery via Foundation Model Self-Exploration" (ACD). arXiv:2502.07577.
- A "scientist" FM proposes open-ended tasks for a "subject" FM (can be itself),
  keeps an archive of discovered capabilities/failures.
- Code: https://github.com/conglu1997/ACD ; Verification: [V-abs].

#### Dharna, Lu, Clune (2024/2025). "Quality-Diversity Self-Play" / "Foundation Model Self-Play: Open-Ended Strategy Innovation via Foundation Models." NeurIPS 2024 workshop; arXiv:2507.06466.
- Plain self-play gets stuck in local optima and lacks diversity; novelty-search
  self-play and QD self-play (FM writes policies as code) produce diverse,
  high-quality strategies (Car Tag; Gandalf jailbreak game).
- Verification: [V-abs].

#### Gurkan, Stonedahl, Wilensky (2026). "Mutation Without Variation: Convergence Dynamics in LLM-Driven Program Evolution." arXiv:2606.05408.
- Without selection, LLM mutation chains in a DSL collapse structurally: "in 87%
  of chains, over 93% of mutations revisit a previously seen structural form";
  variation mostly terminal substitutions inside recurring templates; short
  cycles and self-loops dominate; classical GP subtree mutation does NOT show
  this.
- Relevance: if Aphrodite's schema proposer is LLM-based, the re-derivation of
  G1 may be partly a proposer attractor, not a supply limit. Control: swap in a
  grammar-based subtree mutator and compare revisit rates.
- Code: https://github.com/can-gurkan/lmca
- Verification: [V-abs].

#### Dai, Meinardus, Regan, Tian, Tang (2026). "Discovering Novel LLM Experts via Task-Capability Coevolution" (AC/DC). arXiv:2604.14969.
- Coevolves LLMs (via model merging) and natural-language tasks (synthetic data
  generation) in one run; growing archive of experts. Code not listed.
- Verification: [V-abs].

### 2.6 Self-play / self-proposed task curricula (endogenous task supply)

#### Sukhbaatar, Lin, Kostrikov, Synnaeve, Szlam, Fergus (2017/2018). "Intrinsic Motivation and Automatic Curricula via Asymmetric Self-Play." ICLR 2018; arXiv:1703.05407.
- Alice acts; Bob must reverse (reversible envs) or repeat (resettable envs).
  Alice rewarded when Bob takes long/fails, Bob rewarded for speed ->
  automatic curriculum at the edge of Bob's ability. Tasks are valid by
  construction (Alice demonstrated them).
- Relevance: "valid by construction" is the cleanest non-smuggling task
  generator: a donor's own executed program on fresh inputs defines a task that
  is guaranteed solvable in the DSL. Verification: [V-abs].

#### OpenAI: Plappert, Sampedro, Xu, Akkaya, Kosaraju, Welinder, D'Sa, Petron, Pinto, Paino, Noh, Weng, Yuan, Chu, Zaremba (2021). "Asymmetric self-play for automatic goal discovery in robotic manipulation." arXiv:2101.04882.
- Alice proposes goals by reaching them; Bob must solve; Alice's
  demonstration used for Bob when he fails (ABC). Discovers diverse complex goals
  without human priors; generalizes to unseen goals/objects.
- Site: https://robotics-self-play.github.io ; Verification: [V-abs].

#### Zhao et al. (2025). "Absolute Zero: Reinforced Self-play Reasoning with Zero Data" (AZR). arXiv:2505.03335 (v3 Oct 2025).
- One LLM proposes and solves code-reasoning tasks as (program, input, output)
  triplets: deduction (predict output), abduction (predict input), induction
  (synthesize program from I/O pairs + message, with held-out examples to
  discourage if-else overfitting). Python executor validates, checks
  determinism, and verifies answers.
- Proposer reward (Eq. 4) [V-full]: r_propose = 0 if mean solver success is 0
  (and the paper's text makes trivially solved tasks yield 1 - 1 = 0), else
  1 - mean success over G Monte Carlo solver rollouts. The ONLY seed was the
  identity-function triplet (f(x) = x); the base LLM can start without it.
- Diversity: proposer is shown K past triplets and prompted to generate a
  different one. Logged complexity (ComplexiPy, Halstead) and diversity (AST
  edit distance; answer diversity 1 - p(answer)) rose without being rewarded.
- Failure notes: Llama-3.1-8B produced concerning CoTs ("uh-oh moment").
  Heavy dependence on the pretrained model's prior knowledge of code (task
  supply is endogenous but the representation of possible tasks is Python +
  the LLM's prior).
- Relevance: AZR's triplet formulation maps 1:1 onto Aphrodite's integer fold
  programs; the learnability reward is directly implementable with an exact
  executor. The seed-identity trick is a strong non-smuggling control.
- Code: https://github.com/LeapLabTHU/Absolute-Zero-Reasoner
- Verification: [V-full] for reward, seed, determinism, metrics, uh-oh.

#### Huang et al. (2025). "R-Zero: Self-Evolving Reasoning LLM from Zero Data." ICLR 2026; arXiv:2508.05004.
- Challenger and Solver from one base model; Challenger rewarded by solver
  uncertainty r = 1 - 2|p_hat - 1/2| plus a BLEU-cluster repetition penalty;
  Solver trained on majority-vote pseudo-labels.
- Failure [V-html]: "after multiple iterations, we observe a consistent and
  concerning trend of performance degradation across all models"; pseudo-label
  accuracy dropped from 79.0% to 63.0% by the third iteration; attributed to
  label noise and model collapse from training on self-synthesized data;
  smaller models collapse earlier.
- Relevance: exact verification (Aphrodite's integer executor) removes the
  label-noise channel entirely; what remains is the information channel.
- Code: https://github.com/Chengsong-Huang/R-Zero
- Verification: [V-abs] + [V-html].

#### Liu, Qi, Du, He (2026). "Self-Play Only Evolves When Self-Synthetic Pipeline Ensures Learnable Information Gain." arXiv:2603.02218.
- Claim: sustainable self-evolution needs a self-synthesized data pipeline whose
  learnable information INCREASES across iterations. Three design principles:
  (1) asymmetric co-evolution (proposer / solver / verifier feedback loops);
  (2) capacity growth (parameters and compute scale with learnable information);
  (3) proactive information seeking (introduce external context and new task
  sources to prevent saturation).
- Relevance: maps onto Aphrodite exactly: (1) absent, (2) absent (fixed DSL,
  fixed improver), (3) absent (fixed external supply without novelty intake).
- Verification: [V-abs]. Code not listed.

#### Liu et al. (2025). "SPICE: Self-Play In Corpus Environments Improves Reasoning." arXiv:2510.24684.
- Challenger mines a document corpus to pose tasks; argues ungrounded
  self-play offers "more limited benefits" and corpus grounding supplies "the
  rich, near-inexhaustible external signal necessary for sustained improvement."
- Relevance: an external but UNBOUNDED, un-stratified supply is another way out;
  for integer programs the analogue is a large mined corpus (e.g. OEIS-like
  sequences) rather than a stratified generator.
- Verification: [V-abs]. Code UNVERIFIED.

#### Haluptzok, Bowers, Kalai (2023). "Language models can teach themselves to program better." ICLR 2023.
- Self-generated programming puzzles verified by execution; fine-tune on
  verified solutions. [V-bib] via AZR reference list.

### 2.7 Program-synthesis library learning (representation expansion)

#### Ellis, Wong, Nye, Sable-Meyer, Morales, Hewitt, Cary, Solar-Lezama, Tenenbaum (2021). "DreamCoder: bootstrapping inductive program synthesis with wake-sleep library learning." PLDI 2021; arXiv:2006.08381.
- Wake: solve tasks with current library + neural recognition model. Sleep
  (abstraction): refactor solved programs via E-graph matching and add common
  subexpressions (with lambda-abstracted holes) as NEW PRIMITIVES. Sleep
  (dreaming): train recognition model on replays and fantasies. Library
  deepens: later abstractions are built from earlier ones.
- Held fixed: the TASK CORPUS (external, fixed, curated to span a graded range
  of difficulty), base DSL primitives.
- Relevance (high): Aphrodite's "hole-bearing schemas passed to descendants" is
  DreamCoder's abstraction sleep without (a) promoting schemas to primitives
  that change the effective search depth, and (b) a recognition model. DreamCoder
  gets depth growth because an abstraction counts as one node; in Aphrodite a
  schema inside a depth-2 body cap may give no new reach. DreamCoder also
  depends on a fixed corpus that already contains the stepping stones; its
  library growth stops when the corpus is explained - the same "task supply"
  ceiling Aphrodite hit.
- Follow-ons: LILO (arXiv:2310.19791) and Stitch (compression-based
  abstraction) [V-bib only].
- Code: https://github.com/ellisk42/ec
- Verification: [V-bib] (ACM + search); the "stops when corpus explained"
  statement is the raid's analytical inference, UNVERIFIED as a paper claim.

### 2.8 World-model environment generation

#### Bruce, Dennis, Edwards, Parker-Holder, et al. (2024). "Genie: Generative Interactive Environments." ICML 2024; arXiv:2402.15391.
- 11B foundation world model trained unsupervised from Internet video with a
  latent action model; prompted to generate action-controllable worlds.
  Genie 2 and Genie 3 (Aug 2025; real-time 24 fps, DeepMind blog
  https://deepmind.google/blog/genie-3-a-new-frontier-for-world-models/) extend
  this. Hughes et al. present such models as the environment-generation
  ingredient for open-ended systems.
- Relevance to Aphrodite: low directly; conceptually, the environment
  distribution becomes as broad as the world model's training data - another
  "external but huge" supply. Code: official not released; third-party
  https://github.com/myscience/open-genie
- Verification: [V-abs]; Genie 3 [V-bib] via DeepMind page/news.

### 2.9 AI-GA framing and exploration theory

#### Clune (2019). "AI-GAs: AI-generating algorithms, an alternate paradigm for producing general artificial intelligence." arXiv:1905.10985.
- Three pillars: (1) meta-learning architectures, (2) meta-learning the
  learning algorithms, (3) automatically generating effective learning
  environments. Aphrodite currently has none of the three as learned/endogenous.
- Verification: [V-abs].

#### Jiang, Rocktaschel, Grefenstette (2022/2023). "General Intelligence Requires Rethinking Exploration." Royal Society Open Science 10(6):230539; arXiv:2211.07819.
- The bottleneck shifts from "learning from data" to "learning what data to
  learn from"; proposes "generalized exploration". Directly supports "task
  supply, not the improver" as a first-class research object.
- Verification: [V-abs].

#### Stanley (2019). "Why Open-Endedness Matters." Artificial Life 25(3). DOI 10.1162/artl_a_00294. [V-bib].
#### Hintze (2019). "Open-Endedness for the Sake of Open-Endedness." Artificial Life 25(2):198-. arXiv:2006.03079 (companion). [V-bib].
#### "On Creativity and Open-Endedness" arXiv:2405.18016 (2024). Authors UNVERIFIED in this raid.

---------------------------------------------------------------------------

## 3. Cross-cutting table (compressed)

Work | endogenous supply | repr. expands | selection | measure | observed stall cause
---- | ---- | ---- | ---- | ---- | ----
Tierra | yes (ecology) | genome length only | replication | qualitative | (UNVERIFIED) optimization plateau
Avida/Lenski03 | no (fixed task list) | genome length | CPU reward | task acquisition | target-only reward: 0/50
Avida/Zaman14 | yes (parasites) | genome length | coevolution | complexity, evolvability | needs lineage diversity
Chromaria | yes | per condition 4 | MC | stagnation vs divergence | removal of any of 4 conditions; MC too strict/lax
Novelty search | n/a (fixed task) | NEAT | novelty | BC coverage | BC design; pathological novelty
MAP-Elites | n/a | fixed | per-cell elite | coverage, QD-score | grid full
NEAT | n/a | yes (complexify) | fitness + speciation | - | -
MCC | yes (coevolving mazes) | maze size grows | two MCs | maze complexity | convergence w/o resource limits
POET | yes | NO (fixed params) | MC + novelty + transfer | env novelty | ANNECS plateau ~20k iters (encoding exhausted)
E-POET | yes | yes (CPPN) | MC + PATA-EC novelty | ANNECS | slower growth late
PAIRED/PLR/ACCEL | yes (adversary/replay/edit) | fixed param space | regret proxies | zero-shot transfer | proxies track success rate (Rutherford)
SFL | sampled | fixed | p(1-p) | CVaR eval | -
ALP-GMM/TSCL/MAGELLAN | selection within fixed space | no | learning progress | LP / mastery | bounded by space
OMNI/OMNI-EPIC | yes (FM-written code) | yes (code) | LP + MoI | ANNECS-OMNI | memorization; compute
Voyager | yes (FM curriculum) | yes (skill library) | self-verify | items/tech tree | random curriculum -93%
DGM | NO (fixed benchmarks) | yes (agent code) | benchmark score + archive | benchmark | bounded by benchmark
AZR | yes (self-proposed) | via LLM prior | 1 - p (p in (0,1)) | complexity, AST diversity | safety; relies on prior
R-Zero | yes | no | 1 - 2|p - 1/2| | benchmarks | degradation after ~3 iterations
DreamCoder | no (fixed corpus) | yes (library primitives) | posterior | tasks solved | corpus explained
Aphrodite (current) | NO | NO | headroom vs pristine | re-derivation of G1 | predicted by all of the above

---------------------------------------------------------------------------

## 4. (a) Conditions the literature says are NECESSARY for continued generation of new improvement opportunities

"Necessary" is almost always an empirically-supported hypothesis from ablations
in specific systems, not a theorem. Strength of evidence noted.

A1. Endogenous opportunity creation: new solutions must create new tasks (or
    new niches). Soros & Stanley condition 2; POET/MCC coevolution; Zaman 2014
    (coevolution > fixed tasks on the same complexity target); Hughes (fixed
    dataset => not open-ended); Liu 2026 (asymmetric co-evolution).
    Evidence: strong and convergent across ALife and RL.
A2. An unbounded, or at least expandable, representation for BOTH tasks and
    solutions. Soros & Stanley condition 4; E-POET's direct evidence that a
    finite encoding caused the plateau; NEAT complexification; DreamCoder
    abstractions as new primitives; Banzhaf Type-1/Type-2 novelty; Liu 2026
    capacity growth. Evidence: strong (E-POET is a clean within-system
    ablation).
A3. A minimal criterion / learnability window that is non-trivial but NOT too
    strict: Soros et al. 2016 (both extremes stagnate); POET MC; SFL p(1-p);
    AZR 1 - p on (0,1); R-Zero 1 - 2|p - 1/2|; PAIRED regret (zero for impossible
    tasks). Evidence: strong.
A4. Retention of stepping stones that are not (yet) better on the objective:
    archives (novelty search, MAP-Elites, OMNI-EPIC archive ablation, DGM
    open-ended archive ablation, Voyager skill-library ablation); Lenski's
    deleterious stepping-stone mutations; NEAT speciation protecting
    innovation. Evidence: strong.
A5. Rewarded intermediates / graded difficulty path: Lenski 23/50 vs 0/50;
    ACCEL edits; TSCL/ALP-GMM. Evidence: strong for reachability of complex
    targets.
A6. A domain-general novelty/interestingness criterion defined relative to the
    current population/observer: PATA-EC (novel distinctions among agents);
    OMNI MoI (LP alone admits endless trivial variants); Hughes' observer.
    Evidence: moderate (ablations in E-POET, OMNI-EPIC).
A7. Inflow of new information: Hughes (fixed data), SPICE (corpus grounding),
    Liu 2026 (proactive information seeking), R-Zero collapse. Evidence:
    moderate, mostly LLM-era, several single papers.
A8. Transfer / goal switching across tasks: POET transfer; E-POET "same
    optimizer fails directly, succeeds in open-ended context". Evidence:
    moderate.
A9. Self-referential (state-dependent) generative rules: Adams et al. 2017 -
    only mechanism that scaled. Evidence: theoretical/CA-level only.

Aphrodite satisfies A3 only (and possibly too strictly). A1, A2, A4 (no
protected stepping stones - headroom filter removes them), A5, A6, A7, A8, A9
are absent.

---------------------------------------------------------------------------

## 5. (b) How curricula were generated WITHOUT smuggling the answer - controls used

B1. Target-only vs intermediates control (Lenski 2003): same world, remove
    intermediate rewards; if the complex target never appears, the
    intermediates were necessary, and diversity of routes argues against a
    designed path. Extra guard: intermediates must not be sub-programs of a
    known target solution.
B2. Random-curriculum and manual-curriculum ablations (Voyager: -93% with
    random; manual underperforms). Shows the curriculum mechanism, not the
    content, matters - but does not exclude LLM prior smuggling.
B3. Component ablations of the generator (OMNI-EPIC: no archive, no MoI; DGM:
    no self-improvement, no open-ended archive).
B4. Minimal seeds: AZR starts from the identity triplet only; POET/ACCEL start
    from flat/empty levels; MCC starts from trivial mazes and random agents.
    The less the seed contains, the less can be smuggled.
B5. Valid-by-construction tasks: asymmetric self-play (Alice demonstrates),
    AZR (executor produces the output), MCC (maze counts only if solved by some
    agent). No external answer key exists to leak.
B6. Domain-general novelty characterizations (PATA-EC) instead of hand-coded
    feature spaces: E-POET explicitly argues hand-coded ECs bind exploration to
    "prescripted possibilities".
B7. Regret with an antagonist (PAIRED) so the adversary cannot reward
    impossible or trivially-specified tasks.
B8. Held-out evaluation distributions never used to generate the curriculum
    (UED zero-shot transfer tests; SFL's CVaR adversarial evaluation; AZR
    evaluated on math/coding benchmarks absent from its self-play).
B9. Stated-but-unresolved threat: FM training-data memorization (OMNI-EPIC
    explicitly "cannot rule out" it). The only clean control is a world the FM
    has never seen, or no FM at all. Aphrodite's closed integer DSL is an asset
    here if proposals are generated mechanically.
B10. Persistence / shadow-run filters (MODES, Bedau) to avoid counting spurious
    novelty.

For Aphrodite, the smuggling risk runs in an unusual direction: stratifying
supply by TOP-LEVEL OPERATOR already names the schema space ((acc + {H}) is
literally "top-level operator +"). A curriculum stratified on the same axis the
schemas are defined on partially encodes the answer, and conversely makes the
null result partly definitional. Controls: stratify on an axis orthogonal to
schema structure (I/O statistics, output growth rate, PATA-EC rank vectors), or
do not stratify and let a learnability sampler choose.

---------------------------------------------------------------------------

## 6. (c) Measurable signatures distinguishing open-ended improvement from convergence

Open-ended (sustained):
- ANNECS (or ANNECS-OMNI) keeps rising roughly linearly; E-POET vs POET is the
  reference contrast (POET flat after ~20k iterations).
- Hughes novelty: the observer's loss on newly produced artifacts does not
  decay to a floor; Hughes learnability: that loss drops after the artifacts are
  added to the observer's history. Both must hold.
- MODES: novelty potential (persistent never-seen components) stays > 0;
  complexity potential (max component complexity) keeps rising; ecology
  potential (diversity of coexisting, interacting components) non-decreasing.
- Bedau activity: class 4 (unbounded diversity, positive new activity) vs
  shadow/neutral baseline.
- Archive coverage (MAP-Elites cells over schema descriptors) keeps growing;
  PATA-EC-style distinctness of new tasks stays above threshold.
- Stepping-stone depth: length of the chain of schemas each built from an
  inherited one (the recursion depth Aphrodite actually cares about) grows.
- Transfer/goal-switch events continue (POET).

Convergent (stalled):
- Revisit rate -> 1: new discoveries are structurally identical to library
  entries (Gurkan et al.: >93% revisits in 87% of chains is the LLM-mutation
  attractor signature).
- LP / learnability mass -> 0: fraction of supplied tasks with p in (0,1) under
  the current solver shrinks; most experience on mastered tasks (Rutherford).
- Complexity bounded; archive cells saturated; ANNECS flat.
- R-Zero-type degradation (only when verification is noisy).
- Bedau class 2/3 (activity without novelty, or bounded novelty).

Aphrodite-specific operationalization: log per generation (i) fraction of
qualified tasks whose witness is explained by an inherited schema (explained
fraction), (ii) number of persistent new schemas (persist >= t descendant
generations), (iii) library-conditioned description length of newly solved
tasks (Hughes observer = MDL under the library), (iv) chain depth of schemas.
Open-endedness = (ii) > 0 and (iii) not decaying and (iv) increasing; convergence
= (i) -> 1 and (ii) -> 0.

---------------------------------------------------------------------------

## 7. (d) Distinguishing "task-supply limited" from "improver limited"

No single paper frames it this way; the controls below are assembled from the
literature's ablations.

D1. Oracle-supply (planted target) test. Construct tasks whose minimal
    witness REQUIRES a specific unseen schema G2 at graded distance from G1
    (1 edit, 2 edits, different top-level operator). Give them directly to
    G1-donors and to pristine solvers with equal budget.
    - G1-donor solves and extracts G2 -> the improver CAN recurse; the natural
      supply was limiting (supply-limited).
    - Neither solves -> improver-limited (or DSL-limited) for that distance.
    - Pristine solves, G1-donor does not -> negative transfer / entrenchment
      (library harms search) - an improver defect.
D2. E-POET direct-optimization control inverted: if the planted target fails
    when given directly but succeeds when preceded by a graded ACCEL-style edit
    chain from G1-tasks, the limit was the ABSENCE OF STEPPING STONES in supply,
    not the improver.
D3. 2x2 (or 2x3) factorial: supply {current stratified+filtered, learnability-
    sampled (p(1-p) under current donors), endogenous (donor-proposed, AZR/MCC
    style)} x improver {current, stronger (more search budget / deeper
    enumeration)}. Supply-limited predicts a large main effect of supply and a
    small effect of improver strength under the current supply; improver-limited
    predicts the reverse. An interaction (stronger improver helps only with new
    supply) is the POET-style signature that both must co-evolve.
D4. Headroom accounting (Rutherford-style): for the current supply, measure the
    fraction of qualified tasks already solvable by G1 with p = 1, the fraction
    with p in (0,1), and the fraction with p = 0. If p in (0,1) is near zero,
    supply is limiting BY CONSTRUCTION, whatever the improver.
D5. Filter audit (Soros et al. 2016): sweep qualification strictness (e.g.
    relax tribunal, relax discriminability threshold, relax headroom margin) on
    held-out draws and record (i) survival rate by operator family and (ii)
    whether any survivor requires a non-G1 schema. If G2-requiring tasks exist
    among rejected draws, the FILTER is the supply limit, not the generator.
D6. Exhaustive-space check (possible only because the DSL is tiny): enumerate
    all depth-2 bodies, cluster into schemas, compute which schemas are reachable
    by one hole-fill/edit from G1, and which have at least one qualifying task in
    the generator's support. If the set "reachable AND supplied" is empty, the
    null result is a theorem about the setup, not an empirical finding about
    recursion.
D7. Proposer-attractor check (Gurkan et al.): if an LLM proposes schemas or
    tasks, compare revisit rates with a grammar-based subtree mutator. High LLM
    revisit + low GP revisit -> improver (proposer) limited.

---------------------------------------------------------------------------

## 8. (e) Concrete small-scale designs for the integer-program world

All designs assume exact execution (the DSL evaluator is the verifier), so the
label-noise collapse of R-Zero does not apply.

E1. POET-lite for fold programs.
    - Task = hidden target fold program (possibly from a LARGER generator DSL,
      e.g. depth-3, so the task space is not bounded by the solver DSL) plus
      I/O examples. Population of (task, donor-library) pairs.
    - Task mutation: single operator/constant/subtree edit (ACCEL).
    - MC: task accepted iff 0 < p < 1 for the current donor population
      (or SFL p(1-p) above threshold).
    - Novelty: PATA-EC = rank vector of all donors' (clipped) success on the
      task; accept if kNN distance > threshold.
    - Transfer: periodically try each donor's library on every task.
    - Meter: ANNECS; chain depth of schemas.
    - Controls: (i) same run with task mutation disabled (fixed supply);
      (ii) same run with solver DSL depth fixed vs generator depth 3.
E2. Minimal Criterion Coevolution (Brant & Stanley) with resource limits.
    - Two populations: tasks and donors. A donor reproduces iff it solves >= 1
      task not solved by its parent's library alone; a task reproduces iff
      solved by >= 1 but <= k donors (resource limit, cf. GECCO 2020 follow-up).
    - No fitness, no novelty archive. Log MODES metrics with a persistence
      filter over schemas.
E3. Lenski stepping-stone test (the key causal experiment).
    - Choose G2 targets outside G1's explanatory reach (e.g. multiplicative or
      modular accumulators).
    - Arms: (A) supply only G2-requiring tasks; (B) supply G2-requiring tasks
      plus intermediates (tasks one edit away from G1 toward G2); (C) supply
      intermediates of matched difficulty that are NOT on a path to G2 (the
      anti-smuggling control); (D) supply as now.
    - Supply-limited hypothesis predicts B >> A, C, D in G2 discovery rate.
      Report routes: if B's G2 discoveries arise via diverse schema chains, the
      intermediates did not encode a single answer.
E4. Learnability-sampled supply (SFL/AZR reward) replacing operator strata.
    - Sample a large pool from the generator; score each task by p(1-p) under
      the current donor population; train/evaluate on the top slice. Keep the
      tribunal for validity only; drop headroom as a gate (keep as a metric).
E5. Self-proposed tasks, AZR-style triplets in the integer DSL.
    - Donor proposes (program, input list, output): deduction, abduction
      (predict an input list that yields output), induction (recover program
      from I/O with held-outs). Proposer reward = 1 - mean success when success
      in (0,1), else 0. Seed = identity fold only.
    - Control: random proposer with identical validity checks.
E6. Representation expansion (DreamCoder / NEAT).
    - Promote each accepted schema to a primitive (one node), so the depth-2
      budget reaches effective depth > 2; optionally allow a depth increment
      only after the library explains > X% of current supply (complexify on
      demand). Protect new schemas from the headroom gate for N generations
      (NEAT speciation analogue).
    - Test: with vs without promotion, measure whether G1-as-primitive reaches
      tasks outside depth-2 and whether G2 discoveries build on G1 (true
      recursion signature: G2's minimal form contains G1).
E7. DGM-style ablation matrix for the improver.
    - Arms: {greedy parent = best donor, archive parent sampling} x {inheritance
      on, off}. With fixed supply this isolates improver-side open-endedness
      (DGM showed archive > greedy even with fixed benchmarks).
E8. Strictness sweep (Soros et al. 2016).
    - Vary qualification strictness in 4-5 levels; plot survivors by operator
      family and downstream G2 discovery. Expect an interior optimum if the
      current setting is in the "extreme strictness" stagnation regime.

Minimum viable sequence: D6 (enumerate; hours) -> D4 + D5 (audit; hours) ->
E3 (stepping-stone causal test) -> E4 or E1 (endogenous/learnability supply) ->
E6 (representation expansion) only if E3/E4 show G2 discovery then stalls at a
new plateau.

---------------------------------------------------------------------------

## 9. Challenges to Aphrodite's design

C1. The null result is over-determined. Fixed external supply (violates A1/A7),
    fixed depth-2 DSL (violates A2), no protected stepping stones (A4), a very
    strict MC (A3 at the stagnation extreme). Any one of these is documented
    to stall open-ended systems; with all four the outcome "G1 re-derives G1"
    is expected. The experiment as run cannot attribute the failure to the
    improver OR to supply; it cannot falsify "recursion is possible".
C2. Operator stratification leaks structure. Strata are defined on the same
    axis as the schemas (top-level operator). This both partially encodes
    answers and makes "G1 explains its stratum" nearly tautological. Use
    schema-orthogonal strata or learnability sampling.
C3. The qualification pipeline may be the real supply limiter. Rejecting most
    draws and passing almost only additive/subtractive families is exactly how
    an implicit MC produces stagnation (Soros et al. 2016). Audit (D5) before
    blaming the generator.
C4. Headroom-vs-pristine is an objective, and stepping stones typically have
    no headroom (Lenski deleterious stepping stones; Stanley & Lehman). The gate
    removes the intermediates recursion needs. Keep headroom as a measurement,
    not a filter, or apply it after a protection window.
C5. The DSL may not contain a G2 that is reachable from G1 and supplied.
    Because the space is tiny, compute it (D6). If empty, reframe the result as
    a property of the world rather than of the improver.
C6. "Genuinely new" is undefined relative to an observer. Adopt Hughes'
    observer-relative definition (library as observer; MDL surprise) and
    Banzhaf's Type-0/1/2 so the claim "G2 is new" is checkable.
C7. No coevolution means no arms race and no niche creation; Zaman 2014 shows
    the same complexity target is reached far more often under coevolution,
    and requires lineage DIVERSITY, which a single donor line lacks.
C8. Single-lineage inheritance lacks an archive. DGM, OMNI-EPIC and Voyager
    ablations all show archive/library of stepping stones matters; Aphrodite
    passes one library down a lineage rather than sampling parents from an
    archive of diverse libraries.
C9. If any LLM component proposes schemas, structural-convergence attractors
    (Gurkan et al. 2026) can masquerade as supply limits. Check revisit rates.
C10. Strength of the claim. The operator's suspicion ("task supply, not the
    improver") is well-supported by prior art but is NOT yet shown by Aphrodite's
    data; it needs D1/D3/E3.

---------------------------------------------------------------------------

## 10. What Prometheus may be rediscovering

R1. POET's encoding plateau (2019-2020): a bounded task encoding exhausts
    novelty; fix = expressive encoding (CPPN) + domain-general novelty
    (PATA-EC). Aphrodite's fixed stratified generator + depth-2 DSL is the same
    configuration.
R2. DreamCoder's corpus ceiling: library learning over a fixed task corpus
    grows abstractions until the corpus is explained; the hole-bearing schema
    inheritance is DreamCoder's abstraction step (without primitive promotion).
R3. Lenski's 0/50: complex targets do not evolve when intermediates are not
    rewarded; Aphrodite's filter removes intermediates.
R4. Soros-Stanley conditions 2 and 4, and the MC-strictness U-curve.
R5. Rutherford's "No Regrets": curriculum scores that look like "headroom"
    actually track success rate and spend the budget on mastered tasks.
R6. OMNI's "Achilles heel": learnable-but-uninteresting minor variants
    (re-deriving G1) dominate without an interestingness/novelty criterion.
R7. Hughes' fixed-dataset argument: any system fed a fixed distribution loses
    novelty w.r.t. an observer that has learned it.
R8. Self-play saturation in LLM RSI (R-Zero degradation; Liu et al. 2026
    three principles; SPICE grounding): the 2025-2026 LLM community is
    rediscovering R1-R7 in the language of "learnable information gain".
R9. Bedau/MODES methodology: need a neutral/shadow baseline and a persistence
    filter before calling anything novel. Aphrodite's pristine baseline is a
    partial shadow run.

---------------------------------------------------------------------------

## 11. References (URLs)

Theory / definitions
- Hughes et al. 2024. https://arxiv.org/abs/2406.04268 ; https://proceedings.mlr.press/v235/hughes24a.html
- Banzhaf et al. 2016. https://link.springer.com/article/10.1007/s12064-016-0229-7
- Taylor et al. 2016. https://direct.mit.edu/artl/article/22/3/408/2841/Open-Ended-Evolution-Perspectives-from-the-OEE
- Packard et al. 2019. https://arxiv.org/abs/1909.04430
- Adams et al. 2017. https://www.nature.com/articles/s41598-017-00810-8 ; https://arxiv.org/abs/1607.01750
- Bedau, Snyder, Packard 1998. ALife VI proceedings (no stable URL verified)
- Dolson et al. 2019 (MODES). https://direct.mit.edu/artl/article/25/1/50/2915/The-MODES-Toolbox-Measurements-of-Open-Ended ; code https://github.com/emilydolson/MODES-toolbox-paper
- Soros & Stanley 2014. https://www.semanticscholar.org/paper/Identifying-Necessary-Conditions-for-Open-Ended-the-Soros-Stanley/4671423a1b65f3e35dce603f8746e72ae31193dc
- Soros, Cheney, Stanley 2016. https://www.uvm.edu/neurobotics/pubs/pdf/2016_SorosCheneyStanley_HowTheStrictnessOfTheMinimalCriterionImpactsOpenEndedEvolution_ALIFE.pdf
- Stanley & Lehman 2015 (book). https://link.springer.com/article/10.1007/s10710-015-9250-8 (GPEM review)
- Stanley, Lehman, Soros 2017. https://www.oreilly.com/radar/open-endedness-the-last-grand-challenge-youve-never-heard-of/
- Stanley 2019 "Why open-endedness matters". https://dl.acm.org/doi/10.1162/artl_a_00294
- Jiang, Rocktaschel, Grefenstette 2023. https://arxiv.org/abs/2211.07819
- Clune 2019 (AI-GAs). https://arxiv.org/abs/1905.10985
- Maynard Smith & Szathmary 1995. Oxford UP (UNVERIFIED URL; not fetched)

ALife
- Ray 1991 (Tierra). http://tomray.me/pubs/alife2/Ray1991AnApproachToTheSynthesisOfLife.pdf
- Lenski et al. 2003. https://www.nature.com/articles/nature01568 ; Avida https://github.com/devosoft/avida
- Zaman et al. 2014. https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.1002023
- Channon 2019 (Geb). https://direct.mit.edu/artl/article/25/2/134/2925/Maximum-Individual-Complexity-is-Indefinitely
- Kumar et al. 2024 (ASAL). https://arxiv.org/abs/2412.17799
- Lehman et al. 2018 (Surprising Creativity). https://arxiv.org/abs/1803.03453
- TerraLingua 2026. https://arxiv.org/abs/2603.16910

Novelty / QD / complexification / coevolution
- Lehman & Stanley 2011. https://direct.mit.edu/evco/article-abstract/19/2/189/1365
- Mouret & Clune 2015. https://arxiv.org/abs/1504.04909 ; https://github.com/resibots/pymap_elites
- Stanley & Miikkulainen 2002 (NEAT). https://dl.acm.org/doi/10.1162/106365602320169811 ; https://github.com/CodeReclaimers/neat-python
- Brant & Stanley 2017 (MCC). https://dl.acm.org/doi/10.1145/3071178.3071186 ; follow-ups https://dl.acm.org/doi/10.1145/3321707.3321756 , https://dl.acm.org/doi/abs/10.1145/3377930.3389809

POET / UED / curricula
- POET. https://arxiv.org/abs/1901.01753 ; https://github.com/uber-research/poet
- Enhanced POET. https://arxiv.org/abs/2003.08536 ; https://proceedings.mlr.press/v119/wang20l/wang20l.pdf
- PAIRED. https://arxiv.org/abs/2012.02096
- PLR. https://arxiv.org/abs/2010.03934 ; https://github.com/facebookresearch/level-replay
- Robust PLR / DCD. https://arxiv.org/abs/2110.02439 ; https://github.com/facebookresearch/dcd
- ACCEL. https://arxiv.org/abs/2203.01302 ; https://accelagent.github.io/
- No Regrets / SFL. https://arxiv.org/abs/2408.15099 ; https://github.com/amacrutherford/sampling-for-learnability
- Setter-solver. https://arxiv.org/abs/1909.12892
- TSCL. https://arxiv.org/abs/1707.00183
- ALP-GMM. https://arxiv.org/abs/1910.07224 ; https://github.com/flowersteam/teachDeepRL
- Oudeyer et al. 2007 (IAC). https://www.pyoudeyer.com/ims.pdf
- MAGELLAN. https://arxiv.org/abs/2502.07709 ; https://github.com/flowersteam/MAGELLAN
- ACES. https://arxiv.org/abs/2310.10692
- DiCode. https://arxiv.org/abs/2602.08194

LLM-driven open-endedness
- OMNI. https://arxiv.org/abs/2306.01711
- OMNI-EPIC. https://arxiv.org/abs/2405.15568 ; https://github.com/maxencefaldor/omni-epic
- ELM. https://arxiv.org/abs/2206.08896 ; OpenELM https://github.com/CarperAI/OpenELM
- EvoLLM. https://arxiv.org/abs/2402.18381
- Voyager. https://arxiv.org/abs/2305.16291 ; https://github.com/MineDojo/Voyager
- Darwin Godel Machine. https://arxiv.org/abs/2505.22954 ; https://github.com/jennyzzt/dgm
- ACD. https://arxiv.org/abs/2502.07577 ; https://github.com/conglu1997/ACD
- QDSP / FMSP. https://arxiv.org/abs/2507.06466
- Mutation Without Variation. https://arxiv.org/abs/2606.05408 ; https://github.com/can-gurkan/lmca
- AC/DC task-capability coevolution. https://arxiv.org/abs/2604.14969
- Genie. https://arxiv.org/abs/2402.15391 ; Genie 3 https://deepmind.google/blog/genie-3-a-new-frontier-for-world-models/

Self-play / self-proposed tasks
- Sukhbaatar et al. 2018. https://arxiv.org/abs/1703.05407
- OpenAI asymmetric self-play 2021. https://arxiv.org/abs/2101.04882
- Absolute Zero. https://arxiv.org/abs/2505.03335 ; https://github.com/LeapLabTHU/Absolute-Zero-Reasoner
- R-Zero. https://arxiv.org/abs/2508.05004 ; https://github.com/Chengsong-Huang/R-Zero
- Liu, Qi, Du, He 2026. https://arxiv.org/abs/2603.02218
- SPICE. https://arxiv.org/abs/2510.24684
- Haluptzok et al. 2023. https://openreview.net/forum?id=SaRj2ka1XZ3

Library learning
- DreamCoder. https://dl.acm.org/doi/10.1145/3453483.3454080 ; https://github.com/ellisk42/ec
- LILO. https://arxiv.org/abs/2310.19791

## 12. Known gaps in this raid (UNVERIFIED / not covered)
- Full Taylor et al. 2016 hallmark list; Packard 2019 categorization.
- Exact Lenski numbers should be re-read from the Nature full text before
  external citation (23/50 vs 0/50 seen only in abstract-derived summaries).
- Tierra plateau characterization is community lore here, not verified.
- Code URLs for OMNI, ACES, EvoLLM, SPICE, ASAL not confirmed.
- Did not verify: "On Creativity and Open-Endedness" (arXiv:2405.18016) authors;
  J-Zero (arXiv:2608.26582), G-Zero (arXiv:2605.09959), CODE-SHARP
  (arXiv:2602.10085), BenchEvolver (arXiv:2606.01286) - seen as search results
  only; all are leads for 2026 endogenous-curriculum work.
