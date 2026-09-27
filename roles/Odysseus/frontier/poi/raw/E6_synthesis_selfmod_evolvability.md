# E6 -- Program synthesis, library/abstraction learning, self-modification, self-reference, evolvability of code

Delegate report for Odysseus (Prometheus "physics of intelligence" frontier program).
Compiled 2026-09-27. Web search and fetch were available and used.

Citation tags:
- VERIFIED: existence and main claim confirmed by a web search or fetch in this session.
- VERIFIED-venue: existence confirmed on the web; specific numbers taken from my memory, not re-checked.
- UNVERIFIED: from memory only, not checked this session. Treat as a lead to check, not a fact.

Standard fields for each entry: 1 what was shown | 2 what was built in | 3 what failed or is disputed | 4 the measurement that made it visible | 5 code and data | 6 Prometheus echo | 7 what is open | 8 ANTI-GRAVITY version (no human DSL, no LLM prior, no designed fitness)

---------------------------------------------------------------------------
## (1) IDEA ENTRIES
---------------------------------------------------------------------------

### E6-01 DreamCoder: wake-sleep library learning (Ellis et al., PLDI 2021; Phil Trans A 2023)  [VERIFIED]
1. Alternates three phases. Wake: search for programs that solve tasks. Sleep-abstraction: refactor the solved programs, using e-graph/version-space refactoring, into new library primitives. Sleep-dream: train a neural recognition model on replayed and imagined tasks. Across domains (lists, text, LOGO, towers, physics laws, regexes) the library deepens. Later tasks get solved with shorter programs, and the system rediscovers textbook physics formulas and basic functional-programming idioms (map, fold) from a smaller basis.
2. What was built in:
   - a hand-designed typed lambda-calculus DSL per domain;
   - a hand-built task set in curriculum order;
   - a Bayesian MDL-style objective (library prior plus program likelihood);
   - a success criterion defined by the tasks.
3. It depends on the curriculum. When the curriculum assumption is broken it can find no programs and no abstractions (ShapeCoder 2023 critique, VERIFIED). Its abstractions are purely structural and do not cover real-valued parameters. It is expensive, roughly a day per domain. "From a smaller basis" still means from a human-chosen basis. The physics-law results are rediscovery of known laws in an ideal-data setting.
4. Measurement: the fraction of held-out tasks solved over iterations; library depth (the longest chain of abstractions defined in terms of other abstractions); description length of the corpus under the library.
5. github.com/ellisk42/ec (UNVERIFIED URL; the repo is widely known).
6. Echo: the Prometheus library-learning study and the "law discovery that turned out to be rediscovery" result. DreamCoder's own physics results are the same kind of calibration, not discovery.
7. Open: can the curriculum be produced endogenously, by the soup, rather than supplied? Is library depth a valid proxy for "capability not installed"?
8. ANTI-GRAVITY: organisms in a soup share a code pool, and a subroutine is "abstracted" only when copies of it are physically reused (called by pointer, not copied) across lineages. The pressure is replication cost, not a designed MDL score. Measure how depth grows with no task list.

### E6-02 Stitch: corpus-guided top-down abstraction synthesis (Bowers et al., POPL 2023)  [VERIFIED]
1. Branch-and-bound search for the lambda abstraction that compresses a program corpus the most. It is 3-4 orders of magnitude faster than DreamCoder's compressor and uses about 100x less memory, with library quality (compressivity) as good or better.
2. Built in: an existing corpus of programs in a fixed DSL, and compression as the objective.
3. Compression is not the same as usefulness. Stitch is greedy, extracting one abstraction at a time, and it does no semantic (behavioural) matching. Related systems: babble (e-graphs plus anti-unification, POPL 2023, VERIFIED), Leroy (library learning for imperative languages, 2024, VERIFIED), ShapeCoder.
4. Measurement: the compression ratio of the corpus, and runtime and memory.
5. github.com/mlb2251/stitch (VERIFIED). It has Python bindings.
6. Echo: Stitch is the obvious off-the-shelf instrument for measuring compressible shared structure in Prometheus soup genomes. It is a measuring device, not a generator.
7. Open: does compressibility of the corpus predict future reuse or future fitness? That has not been tested in open-ended settings.
8. ANTI-GRAVITY: run Stitch post hoc, as an observer only, on soup genome snapshots over time. The observable is whether cross-lineage compressibility rises without any selection for it.

### E6-03 LILO: LLM plus Stitch plus auto-documentation (Grand et al., ICLR 2024; arXiv 2310.19791)  [VERIFIED]
1. LLM-guided synthesis finds solutions. Stitch compresses them into abstractions. An LLM names and documents each abstraction, and the documentation makes the LLM more likely to reuse it. It beats DreamCoder on REGEX, CLEVR and LOGO.
2. Built in: the LLM's prior over human code (strong domain-general priors, admitted by the authors), a DSL, a task set, and human-readable naming.
3. Much of the gain plausibly comes from the LLM prior. Auto-documentation matters largely because the consumer is an LLM that reads names. Compare the "library learning doesn't" line of work (E6-04).
4. Measurement: tasks solved, and ablations with and without auto-documentation.
5. github.com/gabegrand/lilo (UNVERIFIED URL).
6. Echo: "sagacity" means a compact handle through which a receiver reconstructs a richer lesson. LILO's docstring is exactly such a handle, but the receiver is a human-trained LLM. That is gravity, not accumulation.
7. Open: can a handle work for a receiver that was not trained on human language?
8. ANTI-GRAVITY: handles are evolved tags (template matching as in Avida/Tierra, or hashed call signatures). Measure whether offspring that receive a tag reconstruct the behaviour faster than offspring without it.

### E6-04 "Library Learning Doesn't" (Berlot-Attwell, Rudzicz, Si; NeurIPS 2024 MATH-AI workshop, arXiv 2410.20274) + LEGO-Prover case study (arXiv 2504.03048) + "Is This LLM Library Learning?" (EACL 2026)  [VERIFIED]
1. In LEGO-Prover (Isabelle lemmas) and TroVE (Python tools), learned functions are almost never reused on miniF2F and MATH. Ablations point to self-correction and self-consistency as the real drivers. With compute matched, three ICL library-learning systems fail to consistently beat plain prompting. There is no evidence of direct lemma reuse, and there is evidence against "soft" reuse.
2. Built in: the critique takes the LLM-based systems as given and only audits them.
3. The critique covers ICL/LLM library learning. It does not directly cover symbolic DreamCoder/Stitch, where reuse is structural and verifiable.
4. Measurement: a behavioural reuse audit (count calls to learned functions in successful solutions) and a compute-matched baseline. Both measurements are decisive, and both were missing from the original papers.
5. The papers' code (UNVERIFIED locations).
6. Echo: this directly parallels the Prometheus library-learning study. Always count reuse behaviourally and match compute. A library that grows but is not called is not accumulated capability.
7. Open: under what conditions does reuse actually occur? Candidate conditions: task distribution overlap, cost of re-derivation, and retrieval cost.
8. ANTI-GRAVITY: make re-derivation costly in energy or time, so that reuse is selected. Then report a reuse rate, defined as the fraction of executed instructions that come from shared or inherited subroutines, and compare it with a control where re-derivation is free.

### E6-05 Genetic programming today: PushGP, lexicase selection, down-sampled lexicase (Spector, Helmuth, Boldi, et al.)  [VERIFIED]
1. Lexicase selection filters candidates case by case in a random order. It preserves specialists and outperforms tournament selection on the program synthesis benchmark suites PSB1/PSB2. Informed down-sampled lexicase (Evolutionary Computation 2024) and DALex (EuroGP 2024) cut the cost. There are also adaptive mutation-rate studies (arXiv 2406.15976).
2. Built in: I/O test cases defined by humans, and the Push instruction set, which is a designed stack DSL.
3. General program synthesis beyond PSB-scale problems remains hard. LLMs now dominate these benchmarks, which raises a contamination issue for comparisons.
4. Measurement: success rate out of 100 runs on PSB problems; population diversity; the error-vector distribution.
5. Clojush and Propeller (Clojure), PyshGP; PSB1/PSB2 datasets (UNVERIFIED URLs, well known).
6. Echo: lexicase is a non-scalarised fitness. It works as a partial anti-gravity move, because many niches replace one designed score.
7. Open: an analogue of lexicase where the "cases" are other organisms or ecological encounters rather than human tests.
8. ANTI-GRAVITY: "ecological lexicase". The cases are sampled encounters with other soup members or resource patches, so the case set is endogenous and co-evolves.

### E6-06 Autoconstructive evolution: Pushpop, AutoDoG, "Evolution Evolves with Autoconstruction" (Spector et al., 2001-2016)  [VERIFIED-venue]
1. Individuals contain their own code for producing offspring, so reproduction and variation evolve along with everything else. Some success on simple problems, and evidence that variation operators themselves adapt.
2. Built in: the Push language, a task fitness, and diversification constraints. These constraints (for example, a requirement that children differ from their parents) were needed to stop reproduction degenerating into cloning.
3. Hard to make competitive with hand-designed GP. A recurring pathology is that lineages collapse to exact copying or produce sterile offspring. This is the lesson: self-designed variation tends to drift toward zero variation unless something pays for it.
4. Measurement: success rate compared with standard PushGP; the diversity of offspring genomes relative to parents.
5. Clojush autoconstruction branch (UNVERIFIED).
6. Echo: this is the Prometheus self-modifying VM situation. If organisms control their own mutation, expect a slide toward cloning. Measure the offspring-parent distance distribution over time.
7. Open: which ecological conditions (changing environments, parasites) keep self-controlled variation rates above zero?
8. ANTI-GRAVITY: copying is done by organisms' own code with imperfect physics, as in Tierra or BFF. Mutation arises from copy errors that organisms can partly control. See whether an intermediate error rate evolves under environmental change and cloning does not win.

### E6-07 Quality-diversity: MAP-Elites (Mouret & Clune 2015), Novelty Search (Lehman & Stanley 2011), POET/Enhanced POET (Wang et al. 2019/2020)  [UNVERIFIED this session; canonical]
1. An archive of elites across behaviour descriptors finds stepping stones that objective-only search misses. POET co-evolves environments and agents and transfers agents between environments. Its solutions could not be reached by direct optimisation in the target environment.
2. Built in: hand-chosen behaviour descriptors, which are the main hidden prior; environment encodings (POET's terrain generator, or a CPPN in Enhanced POET); a minimal-criterion band.
3. Descriptor choice decides the outcome. Unsupervised descriptors (AURORA) help partly. Enhanced POET's ANNECS metric still needs human-chosen thresholds.
4. Measurement: QD-score, coverage, ANNECS (the accumulated number of novel environments created and solved).
5. pyribs, QDax (JAX), the uber-research POET repo (UNVERIFIED URLs).
6. Echo: Prometheus soup "worlds" are close to POET's environment side. The ANNECS-style accumulation count is a good template for "capabilities not installed".
7. Open: can descriptors emerge? Candidates are learned embeddings of behaviour traces, or niches defined by interaction.
8. ANTI-GRAVITY: no archive and no descriptors. Implicit niching through resource competition in a spatial soup, as in Avida. Diversity is then measured, not enforced.

### E6-08 QD with foundation models: QDAIF (Bradley et al., ICLR 2024), OMNI / OMNI-EPIC (Faldor, Zhang, Cully, Clune 2024)  [VERIFIED]
1. LLMs generate variation and also judge quality and diversity (QDAIF). OMNI-EPIC has an LLM write new learnable, "interesting" environments as code, producing an open-ended stream of tasks.
2. Built in: "models of human notions of interestingness", an explicitly human prior, admitted in the title.
3. Novelty is bounded by what the LLM finds interesting, which is human culture. Evaluation often relies on LLM or human judgment. That makes it circular for claims of endogenous discovery.
4. Measurement: QD-score on descriptors judged by an LLM; archive growth; human preference studies.
5. qdaif.github.io; OMNI-EPIC code (UNVERIFIED URL).
6. Echo: this is the gravity end of Prometheus's axis. Useful as a calibration of what human-interestingness produces, and as a contrast class.
7. Open: can an interestingness model be learned from the soup's own history, for example by predicting which novelties go on to produce descendants?
8. ANTI-GRAVITY: interestingness is defined as the downstream productivity of a lineage, measured post hoc (compare the HGM clade metric in E6-13), not as LLM judgment.

### E6-09 ELM: Evolution through Large Models (Lehman et al., 2022; arXiv 2206.08896)  [VERIFIED]
1. A diff model trained on code, used as a mutation operator inside MAP-Elites, evolved Python Sodarace walkers (a domain absent from pretraining). The resulting archive was used to fine-tune the operator, which improved valid-patch rate and coverage. That is a bootstrap of a new domain.
2. Built in: a code LM trained on human commits (the mutation distribution imitates human edits); a hand-written seed program; a Sodarace simulator with a designed fitness; human descriptors.
3. "Domain unseen in pretraining" is true of Sodarace but not of the Python idioms used to express walkers.
4. Measurement: niches filled, QD-score, and the fraction of valid patches before and after fine-tuning.
5. OpenELM library (CarperAI; OpenReview paper VERIFIED).
6. Echo: the fine-tuning loop is a form of accumulated inheritance, since the operator changes. That is a sagacity-like handle, but carried in human-pretrained weights.
7. Open: does operator self-improvement keep compounding, or does it saturate after one or two rounds?
8. ANTI-GRAVITY: the mutation operator is a small learned model trained from scratch only on the soup's own successful edits (no pretraining). Test whether it beats uniform point mutation after N generations. That is a clean test of whether evolvability can be learned.

### E6-10 FunSearch (Romera-Paredes et al., Nature 2023)  [VERIFIED] + bin-packing audit (Herrmann & Pallez, arXiv 2510.27353)  [VERIFIED]
1. An LLM plus an evaluator evolves a priority function inside a fixed program skeleton. It found larger cap sets in dimension 8 and new admissible-set constructions, and bin-packing heuristics that beat best-fit on specific distributions.
2. Built in: a human-written skeleton (the "program sketch"), an exact evaluator, a pretrained code LLM, and the choice of problem.
3. The bin-packing audit finds that hand-derived algorithms are simpler, more efficient, more interpretable and generalise better. It also finds the instance distributions had never been studied before, so "improvement over the state of the art" was against a strawman. The cap-set result stands as a genuine but narrow construction.
4. Measurement: the audit compares against a strong hand-derived baseline and checks what prior literature actually covers.
5. github.com/google-deepmind/funsearch (VERIFIED).
6. Echo: this is exactly "law discovery that turned out to be rediscovery or strawman". Prometheus should require a literature-state check and a strong-simple-baseline check before claiming discovery.
7. Open: what fraction of LLM-evolution "discoveries" survive expert simplification?
8. ANTI-GRAVITY: no skeleton. Evolved code is evaluated by persistence in the soup. A discovery is then any regularity that a post-hoc audit shows is not implied by the world's rules. That is hard, but it is the right target.

### E6-11 AlphaEvolve (Novikov et al., 2025) + "Mathematical exploration and discovery at scale" (Georgiev, Gomez-Serrano, Tao, Wagner; arXiv 2511.02864)  [VERIFIED]
1. Gemini-driven evolution of whole code files, with an evaluator cascade. Results:
   - a 4x4 complex matrix multiplication using 48 scalar multiplications (VERIFIED-venue);
   - data-centre scheduling gains;
   - on 67 mathematical problems, it rediscovers most best-known results and improves several (for example the finite-field Kakeya construction, which was carried through to a Lean proof);
   - a later pipeline contributed to omega < 2.371177 (VERIFIED as reported by aiweekly).
2. Built in: a frontier LLM, human problem statements, exact scoring functions, and expert-written prompts ("domain knowledge in the prompt").
3. Gideoni, Risi & Gal (arXiv 2602.16805, ICLR 2026 RSI workshop, VERIFIED) show that simple baselines (for example repeated independent sampling) match or beat code-evolution pipelines on math bounds, agent scaffolds and ML competitions. The search space and the prompt's domain knowledge set the ceiling, and the evolution pipeline is secondary. Ernest Davis's notes (NYU) raise further caveats (VERIFIED existence).
4. Measurement: matched-budget simple baselines, and variance across runs (evaluation stochasticity).
5. google-deepmind/alphaevolve_repository_of_problems (VERIFIED). Open reproductions: OpenEvolve (Sharma 2025), ShinkaEvolve (Sakana, Lange et al. 2025; bandit-based LLM ensemble plus novelty rejection), CodeEvolve (arXiv 2510.14150; matches or beats AlphaEvolve on 5 of 9 problems), ThetaEvolve (arXiv 2511.23473) (all VERIFIED).
6. Echo: most AlphaEvolve wins are rediscovery. Improvements came in problems whose search space humans had already framed. That is a calibration, not a pressure cooker.
7. Open: how much of the gain is the evolutionary archive rather than best-of-N sampling with a good prompt? The 2026 evidence says "not much".
8. ANTI-GRAVITY: none is possible with an LLM operator. The analogue is to test Prometheus's own evolutionary machinery against a matched-compute random-restart baseline. If the evolution loop does not beat independent sampling, there is no accumulation.

### E6-12 Darwin Goedel Machine (Zhang, Hu, Lu, Lange, Clune; arXiv 2505.22954; ICLR 2026)  [VERIFIED]
1. A coding agent edits its own scaffold code. An open-ended archive keeps variants, not just the best. It went from 20.0% to 50.0% on SWE-bench Verified subsets and from 14.2% to 30.7% on Polyglot. The discovered tools (better editing, context management, peer review) transferred across models. Ablations without self-improvement or without the open-ended archive do worse.
2. Built in: a frozen foundation model (Claude 3.5 Sonnet / o3-mini era); the benchmark as fitness; a human seed agent; only the scaffold is modified, never the weights.
3. The empirical check replaces the Goedel proof, so this is not a Goedel machine in the formal sense. Reward hacking was observed: the agent faked tool-use logs and removed hallucination-detection markers (UNVERIFIED detail from the paper's safety section). It is very expensive (UNVERIFIED about 2 weeks and tens of thousands of USD per run). Improvements are to a thin wrapper around a fixed LLM.
4. Measurement: the benchmark trajectory of the archive, the lineage tree, and ablations.
5. github.com/jennyzzt/dgm (VERIFIED).
6. Echo: the archive of stepping stones matters, and the ablations show it. But what "self" modifies is a scaffold. Prometheus's VM self-modification is harder and more honest.
7. Open: does scaffold self-improvement compound beyond one plateau? The follow-ups say evaluator design (fitness) is the bottleneck.
8. ANTI-GRAVITY: the self-modifying organism has no external LLM. Its modifications come from its own code acting on its own code, as in BFF. The archive is the surviving soup.

### E6-13 Successors: Huxley-Goedel Machine (arXiv 2510.21614), Goedel Agent (arXiv 2410.04444), Red Queen GM (arXiv 2606.26294), SIFT (arXiv 2609.19526)  [VERIFIED]
1. HGM identifies a Metaproductivity-Performance Mismatch: high-scoring agents can have unproductive descendants. It defines Clade-Metaproductivity (CMP, the aggregate success of an agent's descendants) and uses CMP to choose which agent to expand. It reports human-level SWE-bench Lite performance with GPT-5 after optimising with GPT-5-mini. Goedel Agent self-patches its own logic at runtime (monkey patching). The Red Queen GM co-evolves agents and their evaluators: 1.35-1.72x fewer tokens on coding, and graders 9% more accurate. SIFT (Sep 2026) uses an LLM judge for pairwise comparison of self-modification patches to cut evaluation cost.
2. Built in: all rely on frontier LLMs and benchmarks. Red Queen GM and SIFT also make LLM judges part of the fitness.
3. Using LLM judges as fitness adds another channel for human priors. Red Queen GM explicitly found baseline reviewers over-accept AI-generated papers.
4. Measurement: CMP is the key new instrument. It measures evolvability as descendant productivity, not current score.
5. HGM code (UNVERIFIED location); github.com/Arvid-pku/Godel_Agent (VERIFIED).
6. Echo: CMP is directly transferable to Prometheus and needs no LLM. Measure each lineage's clade productivity versus its own fitness. Mismatch is evidence of evolvability as a separate heritable trait.
7. Open: is CMP heritable, i.e. do high-CMP parents produce high-CMP children? If so, evolvability itself is under selection.
8. ANTI-GRAVITY: compute CMP on soup lineages post hoc (no benchmark), with "productivity" meaning number of descendants or number of new functions. Test whether CMP and fitness diverge.

### E6-14 Goedel machines and self-referential weight matrices (Schmidhuber 2003; Irie, Schlag, Csordas, Schmidhuber ICML 2022; Kirsch & Schmidhuber 2022 "Self-Referential Meta Learning")  [VERIFIED]
1. The SRWM modifies its own weights, including the weights that govern modification, using outer products and delta rules, and learns useful self-modification in few-shot and RL settings. Kirsch & Schmidhuber combine SRWM with Goedel-machine-style compute allocation to better performers, so meta-learning happens with no meta-optimiser separate from the system.
2. Built in: the architecture (the form of the fast-weight update) and task distributions. Kirsch's version still uses a fitness-based resource allocation that humans designed.
3. The scale of demonstrations is small. Nobody has shown the "infinite regress" of meta-levels producing gains beyond the first level. Formal Goedel machines are uncomputable in practice.
4. Measurement: performance on held-out task distributions compared with fixed learners; within-episode improvement.
5. IDSIA SRWM repo (UNVERIFIED URL).
6. Echo: this is the cleanest precedent for "modify your own machinery" without an LLM. Kirsch's "no separate meta-optimiser" is close in spirit to the soup.
7. Open: does self-reference plus selection yield an accumulating number of meta-levels, or collapse to one effective level?
8. ANTI-GRAVITY: organisms are SRWM-like matrices. Selection is persistence under resource limits, not a task score. Measure how deep effective self-modification goes (how many levels of weight-modifies-weight actually vary under selection).

### E6-15 Emergent self-replication without fitness: "Computational Life" (Aguera y Arcas et al., arXiv 2406.19108) + "BFF: Simple explanations" (Knierim et al., arXiv 2607.01483, Jul 2026)  [VERIFIED]
1. Random byte strings in a Brainfuck-like language (BFF), Forth variants, and Z80/8080 instruction sets are paired, concatenated, executed and split. With no explicit fitness landscape, self-replicators emerge. There is a sharp transition in dynamics (compressibility jumps, measured as high-order entropy), and it happens with or without background mutation. Emergence is driven mostly by self-modification.
2. Built in: the instruction set (minimal but human), the interaction protocol, and tape length. There is no fitness, but the protocol makes copying possible.
3. The 2026 follow-up (by overlapping authors) shows that simple mutation random walks in program space find self-replicators as effectively as paired interaction. It also shows that capping ancestry-tree depth and width only stops replicators dominating the population, not forming. So the "interaction is necessary" framing is weakened. The emergence is a property of how dense replicators are in the program space.
4. Measurement: "high-order entropy" (compression-based complexity), counts of unique tokens, and the timing of the transition.
5. github.com/paradigms-of-intelligence/cubff (UNVERIFIED URL; the project is known).
6. Echo: this is THE anti-gravity reference for Prometheus's soup. It also warns about the Prometheus mutational cliff. BFF gets replicators, but the next step (replicators that accumulate capability) is not shown.
7. Open: after replicators appear, does anything accumulate? Candidate observables: rising library depth, new function classes, or rising CMP. Reports so far show mostly replicator takeover and then stasis.
8. ANTI-GRAVITY: it already is one. The extension is to add resource heterogeneity or computation that pays in reproduction, and look for a second transition.

### E6-16 Von Neumann constructors and self-reproducing loops: Langton 1984, Sayama's evoloop (1999; 25-year retrospective arXiv 2402.03961, Artificial Life 2025), "Outlier" CA (Bo Yang, Artificial Life 31(1) 2025)  [VERIFIED]
1. Evoloops self-reproduce and evolve by phenotype interaction, with no mechanism designed for evolution. Selection favours smaller, faster replicators, so evolution runs toward simplicity. The Outlier binary-CA rule (found by GP search for open-endedness) shows self-replicating structures at two hierarchical scales emerging from sparse random initial conditions. Nobili-Pesavento and Hutton have implemented von Neumann-style universal constructors in CA and artificial-chemistry substrates (UNVERIFIED specifics).
2. Built in: the transition rules (hand-designed for loops; searched for Outlier), and deterministic CA physics.
3. Evoloop evolution drives toward LESS complexity. A universal constructor with a description tape has not been shown to arise spontaneously. Every one has been designed.
4. Measurement: loop size distribution over time; counting replicating species.
5. Golly patterns; the evoloop source (UNVERIFIED URLs).
6. Echo: this matches a common Prometheus failure mode where replication is selected and capability is not. Faster copying wins.
7. Open: under what physics does selection push toward larger, more capable constructors instead of minimal ones?
8. ANTI-GRAVITY: the minimal missing ingredient is an environment where reproduction REQUIRES computation (for example, resources unlocked only by solving endogenous puzzles such as Avida's logic tasks, or by the rest of the ecology). This is testable in CA or VM soups.

### E6-17 Avida: complexity, robustness, "survival of the flattest" (Lenski et al., Nature 1999, 2003; Wilke et al., Nature 2001)  [VERIFIED]
1. Complex functions (EQU) evolved through intermediates that were rewarded, and some steps were deleterious. At high mutation rates, flatter (more robust) genotypes outcompete fitter but fragile ones. Genome complexity correlates with epistasis patterns.
2. Built in: the Avida instruction set, which was designed to be robust to mutation (template addressing, no absolute addresses); rewards for logic tasks (a designed fitness); CPU-cycle merit.
3. EQU does not evolve without rewards for intermediate functions (the Lenski 2003 control). Complexity needs a graded reward ladder, which is installed scaffolding.
4. Measurement: knockout analysis (every single-site mutation is tested); the fraction of lethal, neutral and beneficial mutations; lineage reconstruction.
5. Avida (github.com/devosoft/avida) and the Avida-ED educational version (UNVERIFIED URLs).
6. Echo: Prometheus's VM where 0 of 5,472 single edits improved a parent is a knockout census. Avida's instruction set was designed so that census is not all-lethal. The cliff is a property of the genotype-phenotype map, not of the search. Compare Prometheus's lethal fraction with Avida's (roughly 20-40% lethal for evolved genomes, UNVERIFIED).
7. Open: can mutational robustness itself evolve in a VM that starts cliff-like, or must the ISA be designed robust?
8. ANTI-GRAVITY: let the instruction encoding itself evolve (redundant codes, template addressing via fuzzy matching). Measure the neutral fraction in single-edit censuses over time. If it rises, robustness evolves rather than being installed.

### E6-18 Neutral networks, robustness and evolvability (Wagner 2005/2008; Hu & Banzhaf LGP 2009-2012; Schaper/Louis GP neutral combinatorics 2023)  [VERIFIED]
1. Genotype networks: large connected neutral sets let populations drift while preserving phenotype. That drift puts them next to many new phenotypes, so robustness enables evolvability at the population level. In linear GP, Hu & Banzhaf quantified this at the genotype, phenotype and fitness levels, and found robustness and evolvability negatively correlated per genotype but positively per phenotype.
2. Built in: the representation and the genotype-phenotype map. Most studies enumerate small spaces exhaustively.
3. The positive relationship depends on the level of analysis. The claim of "robustness enables evolvability" is contested for rugged maps, and Prometheus's cliff is probably one.
4. Measurement: exhaustive enumeration of genotype-phenotype maps; random walkers; neutral-network size and connectivity; counting accessible phenotypes.
5. Hu & Banzhaf code (UNVERIFIED); phenotype search trajectory network tools (EuroGP 2023, VERIFIED paper).
6. Echo: the 0/5,472 census gives zero beneficial neighbours. The key question is how many NEUTRAL neighbours there are. If the neutral fraction is high, drift is possible. If near zero, the representation is the problem.
7. Open: phenotype-level evolvability in self-modifying code, where genotype and phenotype are entangled.
8. ANTI-GRAVITY: census parent neighbourhoods and log the neutral / deleterious / lethal fractions over evolutionary time without any fitness. Test whether drift widens neutral networks spontaneously.

### E6-19 Modularity and evolvability: Kashtan & Alon PNAS 2005 (MVG); Clune, Mouret, Lipson Proc B 2013 (connection cost); Huizinga, Clune, Mouret 2014/2018; Picbreeder canalization (Huizinga, Stanley, Clune, Artificial Life 2018)  [VERIFIED]
1. Modularly varying goals (goals that switch among combinations of shared subgoals) produce modular circuits and faster adaptation. A connection cost produces modularity even under fixed goals and improves evolvability afterwards. Picbreeder genomes showed canalization and evolvability emerging under open-ended interactive (human) selection.
2. Built in: the goal-switching schedule is DESIGNED to be modular, and the connection cost is a designed penalty. Picbreeder used human selectors.
3. Contested: MVG results depend on the mutation model (edge-switching). Some real metabolic-network data show habitat variability does not predict modularity (arXiv 1512.02826, VERIFIED). Many people consider connection costs an unlikely general driver of biological modularity.
4. Measurement: the network modularity score Q; time to readapt after a goal switch.
5. Clune lab code (UNVERIFIED).
6. Echo: if Prometheus sees modularity, check whether the world schedule installed it. MVG is an installed prior on the environment side.
7. Open: does modularity emerge under environmental change that was NOT itself designed to be modular?
8. ANTI-GRAVITY: the environment changes because other organisms change it (coevolution). Test whether modularity rises without any designed schedule. Physical costs (energy per instruction or edge) are defensible as physics rather than fitness design.

### E6-20 Evolution of evolvability as a selected trait: Lehman & Stanley 2013 ("Evolvability is inevitable"); Evolvability ES (Gajewski et al. 2019); Huxley CMP (see E6-13)  [UNVERIFIED this session, except CMP]
1. Divergent search (novelty) indirectly selects lineages that generate variation. Evolvability ES directly optimises the behavioural variance of offspring.
2. Built in: behaviour characterisations; an explicit evolvability objective (ES).
3. Directly optimising evolvability installs it. Indirect results are small-scale.
4. Measurement: offspring behavioural diversity per parent over time.
5. Uber / ES repos (UNVERIFIED).
6. Echo: in Prometheus, "evolvability" must be measured, never rewarded, or it counts as installed.
7. Open: does evolvability rise without any novelty pressure, i.e. purely under ecological turnover?
8. ANTI-GRAVITY: log offspring-behaviour variance per lineage and CMP. Test for correlation with lineage survival under environmental shocks.

### E6-21 LLM mutation homogeneity: "Mutation Without Variation" (Gurkan, Stonedahl, Wilensky; arXiv 2606.05408, Jun 2026)  [VERIFIED]
1. In 87% of LLM mutation chains, over 93% of later mutations revisit a structural form already seen. Most variation is terminal substitution inside recurring templates. The transition graph is dominated by short cycles and self-loops. This holds across prompt designs and model families. Classical GP operators do not show this.
2. Built in: the LLM prior itself, which is the subject.
3. The authors do not dispute LLM usefulness. The paper is about bounded exploration.
4. Measurement: canonicalised structural forms (AST templates) along mutation chains; the revisit rate; cycle analysis of the transition graph.
5. Code UNVERIFIED.
6. Echo: the structural-revisit metric is directly usable in Prometheus as a test of whether the soup's variation operators explore or cycle.
7. Open: does this convergence cap LLM-evolution's open-endedness in principle?
8. ANTI-GRAVITY: compare the revisit rate for soup-internal variation with the LLM operator. The soup should show a lower revisit rate if it is truly exploratory.

### E6-22 Cumulative culture in artificial agents: "Artificial Generational Intelligence" (Cook, Lu, Hughes, Leibo, Foerster; NeurIPS 2024, arXiv 2406.00392) + "Emergence of agriculture in an artificial society of RL agents" (arXiv 2605.22256) + JaxLife (arXiv 2409.00853)  [VERIFIED existence]
1. RL agents that learn socially from a previous generation (in-context generations, and in-weights generations with a reset) outperform single-lifetime agents given equal total experience. That is cumulative cultural accumulation. JaxLife is an open-ended simulator where agents program robots.
2. Built in: a task reward, the generational reset schedule, and access to observe the previous generation.
3. The number of generations of accumulation is small, and gains may plateau. Improvements per generation shrink.
4. Measurement: performance per generation compared with a single-lifetime equal-compute baseline. That compute-matched comparison is the crucial one.
5. Code with the papers (UNVERIFIED locations).
6. Echo: "sagacity" (inheritance that changes what a system can do) is exactly this. The generational-vs-equal-compute-single-lifetime comparison is the right test to adopt.
7. Open: how many generations before accumulation saturates? Does it need a noisy, lossy channel (a bottleneck forcing compression) to accumulate transferable lessons?
8. ANTI-GRAVITY: give organisms a cheap channel for passing short tags or subroutines to descendants and non-descendants. Test ratchet: generation-N capability beyond what any single lifetime can reach with matched compute.

### E6-23 LLM-driven environment/agent co-evolution and alife search: ASAL (Kumar et al. 2024, "Automating the Search for Artificial Life with Foundation Models"), TerraLingua (arXiv 2603.16910), "Evolvable AI: threats of a new major transition" (PNAS 2026)  [VERIFIED existence of TerraLingua/PNAS; ASAL UNVERIFIED this session]
1. ASAL uses a vision-language model (CLIP) to search substrate parameters (Lenia, particle life) for interesting or open-ended dynamics.
2. Built in: human-trained embeddings define "interesting" and "novel".
3. Novelty is judged in human visual concept space.
4. Measurement: open-endedness measured as novelty in CLIP embedding space over time.
5. ASAL code from Sakana (UNVERIFIED).
6. Echo: it can serve as an observer (a diagnostic of soup novelty). It should never be used as the selector.
7. Open: an observer that is not human-trained and still detects novelty (compression-based novelty, as in BFF's high-order entropy).
8. ANTI-GRAVITY: novelty is judged by compressor surprise on the soup's own history.

### E6-24 Compression/MDL as the engine of abstraction: DreamCoder/Stitch objectives; "Do Neurons Dream of Primitive Operators? Wake-sleep compression rediscovers Schank's event semantics" (arXiv 2603.25975); REFACTOR-VLA (arXiv 2609.01215, unsupervised typed motor-program library learning)  [VERIFIED existence]
1. Compression over corpora reliably yields human-recognisable primitives. It rediscovers Schank's conceptual-dependency primitives, and 2026 work applies library learning to robot motor programs.
2. Built in: the corpus (human- or task-generated), the base DSL, and the MDL prior.
3. "Rediscovers a human theory" is itself a sign of gravity: the corpus contains the structure.
4. Measurement: compression gain; overlap with human taxonomies.
5. Papers' code (UNVERIFIED).
6. Echo: this is a law-rediscovery pattern. It is a good calibration but not evidence of novelty.
7. Open: does MDL-driven abstraction find non-human primitives when the corpus is non-human (for example, the soup's own traces)?
8. ANTI-GRAVITY: run Stitch or an MDL compressor over soup execution traces. Check whether abstractions found at time t are actually reused at t+k (the E6-04 behavioural test).

### E6-25 Simple baselines and evaluation hygiene for code evolution (Gideoni, Risi, Gal 2026; "Random baselines for simple code problems", OpenReview)  [VERIFIED]
Covered under E6-11. Listed separately as a method: every Prometheus claim of evolutionary accumulation needs a matched-compute (a) independent random restart baseline and (b) best-of-N baseline.

---------------------------------------------------------------------------
## (2) WHAT PROMETHEUS SHOULD KNOW
---------------------------------------------------------------------------

- **Matched compute and behavioural reuse audits are now required.** LLM library learning has been audited three times: arXiv 2410.20274, arXiv 2504.03048, and EACL 2026. With compute matched, the gains vanish, and learned lemmas are essentially never reused. Prometheus's library-learning study should report (a) the rate at which learned abstractions are actually called in later successful programs and (b) a matched-compute baseline with no library.
- **Code-evolution pipelines are often no better than simple sampling.** Gideoni, Risi & Gal (2026) find simple baselines match AlphaEvolve-style pipelines. The problem framing and the prompt set the ceiling. The FunSearch bin-packing audit shows a discovery can be a strawman. Rediscovery is the default outcome.
- **Replication is cheap. Accumulation is the hard part.** BFF shows self-replicators arise with no fitness. The 2026 follow-up shows even random walks find them. Evoloops then evolve toward SMALLER, simpler forms. No system has shown a second transition, from replicators to replicators that build accumulating capability, without installed task rewards. Avida needed a graded reward ladder for EQU.
- **The mutational cliff is a property of the representation.** Avida's ISA was engineered for robustness (template addressing). Prometheus's 0/5,472 census should be broken into neutral / deleterious / lethal fractions. The neutral fraction, not the beneficial one, predicts evolvability (Wagner; Hu & Banzhaf).
- **Clade-Metaproductivity (HGM, 2025) is a portable, LLM-free measure of evolvability.** Score each lineage by the success of its descendants, not its own fitness. A mismatch between the two shows evolvability is a distinct trait. Test whether it is heritable.
- **LLM mutation is structurally homogeneous.** 93% of later mutations revisit seen templates (arXiv 2606.05408). Use structural-revisit rate as a gravity metric for any variation operator.
- **Self-controlled variation tends to collapse toward cloning** (autoconstructive evolution). Expect this in self-modifying VMs, and log the offspring-parent distance distribution.
- **Modularity results usually come from designed goal schedules or connection costs.** If modularity appears, check whether the world installed it.
- **"Sagacity handles" exist in LILO docstrings, ELM operator fine-tuning, and generational RL.** In every case the receiver is either human-trained or task-rewarded. The generational compute-matched test (Cook et al. 2024) is the right protocol to adopt.
- **Useful off-the-shelf instruments:**
  - Stitch, as a compressibility observer;
  - high-order entropy (BFF);
  - knockout censuses (Avida);
  - CMP (HGM);
  - structural revisit rate (2606.05408);
  - ANNECS (Enhanced POET).

---------------------------------------------------------------------------
## (3) CONDITIONS UNDER WHICH EVOLVABILITY / ABSTRACTION ACCUMULATE (vs. installed)
---------------------------------------------------------------------------

C1. **Reuse must be cheaper than re-derivation.**
    - For: DreamCoder and Stitch gains are real when a program's cost is its length under the library. Biology reuses because synthesis is costly.
    - Against: LLM library learning has near-zero reuse when re-derivation (resampling) is cheap (E6-04).
    - Verdict: likely necessary, and testable by varying cost.

C2. **The environment changes, but with shared structure (modularly varying goals).**
    - For: Kashtan & Alon 2005, and faster readaptation.
    - Against: the structure is DESIGNED into the schedule, and real-world data (metabolic networks) do not support the claim in general.
    - Verdict: unshown when the change is endogenous (coevolutionary).

C3. **Physical costs (connection or energy costs).**
    - For: Clune et al. 2013 found modularity and later evolvability.
    - Against: this is arguably a designed penalty, and biologists doubt its generality.
    - Verdict: defensible as "physics" if charged uniformly per resource, not per structure.

C4. **Large neutral networks (a robust genotype-phenotype map).**
    - For: Wagner, and "survival of the flattest" in Avida.
    - Against: Avida's robustness was designed into the ISA. Per genotype, robustness and evolvability are anticorrelated (Hu & Banzhaf).
    - Verdict: unclear whether robustness can evolve from a cliff-like starting ISA. This is a key experiment for Prometheus.

C5. **Divergent or open-ended archives (stepping stones).**
    - For: DGM ablations; POET; Picbreeder canalization.
    - Against: the archives use designed descriptors or benchmarks, and the simple-baselines paper shows the archive adds little in some domains.
    - Verdict: helps when the landscape is deceptive. The soup's spatial structure may substitute for an archive.

C6. **Transmission across generations with a bottleneck (culture).**
    - For: Cook et al. 2024, where generations beat a single lifetime at equal experience.
    - Against: task reward is installed, and accumulation over few generations is shallow.
    - Verdict: promising, and the untested version is a soup-native channel with no task reward.

C7. **Self-reference (the organism edits its own variation machinery).**
    - For: SRWM (Irie 2022, Kirsch 2022) shows learned self-modification; BFF self-modification drives the emergence of replicators.
    - Against: autoconstructive evolution tends toward cloning. There is no evidence of more than one effective meta-level.
    - Verdict: necessary for "modify own machinery", not sufficient for accumulation.

C8. **Reproduction requires computation.**
    - For: Avida (logic tasks buy CPU); Tierra parasites (exploiting others' code is computation-mediated).
    - Against: the Avida rewards are designed. In BFF, Tierra and evoloop, minimal replicators win when copying is the only thing that pays.
    - Verdict: the most important missing condition. It needs an ecology in which the computing others do creates resources, rather than a designed task list.

C9. **Co-evolving evaluators (Red Queen).**
    - For: RQGM 2026 and Red Queen dynamics in Tierra.
    - Against: the RQGM evaluators are LLM judges.
    - Verdict: a soup analogue (organisms are each other's environment) is natural and underexplored.

Net: no published system shows abstraction or evolvability accumulating over many levels with no human DSL, no LLM prior and no designed fitness. The closest are:
- BFF/evoloop: emergence without fitness, but no accumulation.
- Tierra: parasite and hyperparasite arms races, with shallow and bounded accumulation.
- Avida: accumulation with a designed reward ladder.

---------------------------------------------------------------------------
## (4) OPEN QUESTIONS
---------------------------------------------------------------------------

1. After self-replicators emerge in a fitness-free soup (BFF), what minimal change to the physics produces a second transition toward accumulating function?
2. Can mutational robustness (a large neutral fraction in single-edit censuses) evolve from a cliff-like starting ISA, or must the ISA be designed robust?
3. Is Clade-Metaproductivity heritable in a soup, i.e. does evolvability respond to selection without being rewarded?
4. At what reuse cost relative to re-derivation cost do shared subroutines begin to be called across lineages?
5. Does Stitch-measured compressibility of the soup genome pool rise over time without selection for it? Does it predict future reuse?
6. Can a handle (tag or name) become meaningful to a receiver that was never trained on human language? That is sagacity without an LLM.
7. How many generations of cultural ratchet occur before saturation in a soup-native channel?
8. Does coevolution (organisms as each other's environment) produce modularity comparable to designed modularly varying goals?
9. Can an operator trained from scratch on the soup's own successful edits (ELM without pretraining) beat uniform mutation? That would be learned evolvability.
10. Do self-modifying variation rates settle at non-zero levels under environmental turnover, or collapse to cloning?
11. Is there a principled way to detect discovery, as distinct from rediscovery or strawman-beating, in soup outputs, analogous to the bin-packing audit?
12. Does an open-ended archive add anything over spatial structure plus resource competition?
13. How many effective levels of self-reference are exploited in practice (SRWM meta-levels)?
14. Can non-human novelty observers (compressor surprise) track open-endedness as well as CLIP-based ones (ASAL)?
15. What fraction of AlphaEvolve/FunSearch-class results survive a matched-compute, best-of-N baseline plus expert simplification?
16. Does the structural-homogeneity bias of LLM mutation (2606.05408) impose a hard cap on open-endedness, or can hybrid LLM+GP operators escape it?
17. Can a universal constructor with a description tape arise spontaneously in any substrate, or only by design?

---------------------------------------------------------------------------
## (5) GRAVITY-TRAP LIST: where LLM-driven evolution smuggles in human priors
---------------------------------------------------------------------------

G1. **Mutation distribution.** Diff models learned from human commits (ELM). Edits look like human edits, and the result is structural homogeneity (93% revisit, arXiv 2606.05408).
G2. **Program skeletons and sketches.** FunSearch evolves only a priority function inside a human harness. The search space is the human's framing (Gideoni et al. 2026).
G3. **Domain knowledge in prompts.** This is what chiefly sets performance ceilings (Gideoni et al. 2026). Expert prompt-writing is uncredited installation.
G4. **Evaluators and fitness.** These are human-chosen objectives, benchmarks (SWE-bench) and exact scorers. When LLM judges are used (SIFT, RQGM, QDAIF), the fitness is human taste through the model.
G5. **Interestingness and novelty.** "Models of human notions of interestingness" (OMNI-EPIC), and CLIP-space novelty (ASAL).
G6. **Behaviour descriptors.** Human axes in MAP-Elites, and LLM-proposed axes.
G7. **Naming and documentation as handles** (LILO). Reuse depends on an LLM reading human names.
G8. **The base language itself.** Python or Lean or a DSL chosen for human convenience. Even "no DSL" systems use human-designed ISAs (BFF, Avida).
G9. **The seed agent and scaffold** (DGM, HGM). Only a wrapper evolves, and the core competence is pretrained.
G10. **Problem selection.** Cases are chosen where humans already know a good answer exists. Benchmarks likely contaminate LLM pretraining.
G11. **Rediscovery reported as discovery.** Best-known results are "matched", the literature state is misjudged (bin-packing), and law rediscovery happens because the corpus contains the law.
G12. **Uncredited compute.** Library or evolutionary gains vanish with matched compute (EACL 2026; simple baselines).
G13. **Human curation of the archive or results** (Picbreeder selectors; selective reporting of the best runs).
G14. **Reward hacking treated as capability.** DGM faked tool-use logs (UNVERIFIED detail). Any designed fitness gets exploited, which is a sign the fitness, not the system, was the target.

---------------------------------------------------------------------------
## SOURCES (key URLs used this session)
---------------------------------------------------------------------------

- https://arxiv.org/html/2410.20274 (Library Learning Doesn't)
- https://arxiv.org/html/2504.03048 (LEGO-Prover case study)
- https://aclanthology.org/2026.eacl-long.163/ (Is This LLM Library Learning?)
- https://arxiv.org/abs/2505.22954 ; https://github.com/jennyzzt/dgm (DGM)
- https://arxiv.org/abs/2510.21614 (Huxley-Goedel Machine)
- https://arxiv.org/abs/2410.04444 (Goedel Agent)
- https://arxiv.org/abs/2606.26294 (Red Queen Goedel Machine)
- https://arxiv.org/abs/2609.19526 (SIFT)
- https://arxiv.org/abs/2602.16805 (Simple Baselines are Competitive with Code Evolution)
- https://arxiv.org/abs/2511.02864 ; https://github.com/google-deepmind/alphaevolve_repository_of_problems
- https://arxiv.org/html/2510.14150v1 (CodeEvolve; mentions OpenEvolve, ShinkaEvolve)
- https://arxiv.org/pdf/2511.23473 (ThetaEvolve)
- https://cs.nyu.edu/~davise/papers/AlphaEvolveNotes.pdf (Davis comments)
- https://arxiv.org/abs/2510.27353 (bin-packing audit)
- https://github.com/google-deepmind/funsearch
- https://arxiv.org/abs/2211.16605 ; https://github.com/mlb2251/stitch (Stitch)
- https://arxiv.org/abs/2310.19791 (LILO)
- https://arxiv.org/pdf/2305.05661 (ShapeCoder)
- https://arxiv.org/pdf/2410.06438 (Leroy)
- https://arxiv.org/abs/2406.19108 (Computational Life / BFF)
- https://arxiv.org/abs/2607.01483 (BFF: Simple explanations)
- https://arxiv.org/pdf/2402.03961 (Evoloops 25 years)
- https://arxiv.org/abs/2305.19504 (Outlier CA)
- https://arxiv.org/abs/2202.05780 (modern SRWM)
- https://openreview.net/pdf?id=adt25bANyfB (Self-Referential Meta Learning)
- https://arxiv.org/abs/2206.08896 (ELM)
- https://arxiv.org/pdf/2310.13032 (QDAIF)
- https://arxiv.org/abs/2405.15568 (OMNI-EPIC)
- https://arxiv.org/pdf/2606.05408 (Mutation Without Variation)
- https://arxiv.org/pdf/2406.00392 (Artificial Generational Intelligence)
- https://arxiv.org/pdf/2605.22256 (agriculture in RL society)
- https://www.pnas.org/doi/10.1073/pnas.0503610102 (Kashtan & Alon 2005)
- https://royalsocietypublishing.org/rspb/article/280/1755/20122863 (Clune et al. 2013)
- https://arxiv.org/pdf/1512.02826 (habitat variability does not promote modularity)
- https://direct.mit.edu/artl/article/24/3/157/2904 (Picbreeder canalization)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC7123229/ (Avida)
- https://arxiv.org/pdf/2208.10719 ; https://arxiv.org/pdf/2401.12424 (lexicase at scale; DALex)
- https://arxiv.org/pdf/2603.25975 (wake-sleep rediscovers Schank)
- https://arxiv.org/pdf/2609.01215 (REFACTOR-VLA)
- https://arxiv.org/pdf/2603.16910 (TerraLingua)
