# 02 -- External research

Scope: what reusable machinery exists outside Prometheus, and what its experiments actually support. This is not a
literature summary. Each entry ends in a decision.

## 0. How to read the sourcing

| Mark | Meaning |
|---|---|
| [V] | Verified in this session: the paper was found by web search, or the repository and its licence were read from the GitHub API on 2026-11-12 |
| [M] | From my memory of the literature. Citation details may be slightly wrong. Verify before quoting externally |

Licences marked [V] are the SPDX identifier GitHub reports for the repository. "NOASSERTION" means GitHub could
not classify the licence file; read the file before depending on the code.

No external code was downloaded or run. Compute figures are the papers' own unless stated.

## 1. The short answer

Three external results change the design, and one external failure constrains it.

1. **Rule inference from observation works and is cheap.** Ruler infers rewrite rules by enumerating small terms,
   grouping them by their values on sample inputs, and keeping a minimal set. It needs no fitness signal and no
   model. This is a route to durable search machinery that does not pass through the composition wall.
2. **Library learning by compression works and is fast,** but its gains flatten after a few rounds, and in LLM
   systems the learned functions are rarely reused at all.
3. **Self-improving agent systems (Darwin Goedel Machine, AlphaEvolve) get their proposals from a frontier
   language model.** Remove the model and what remains is an archive plus an evaluator. They are evidence that an
   archive of stepping stones helps. They are not evidence about model-free self-improvement.
4. **The constraint: Eurisko.** A system that rewrote its own heuristics by mutation worked only as far as its
   representation happened to make small syntactic changes meaningful. That is the historical precedent for
   Prometheus's own composition wall, at the meta level.

## 2. Self-modifying programs and their proofs

### Goedel machine

| Field | Content |
|---|---|
| Source | Schmidhuber, "Goedel Machines: Fully Self-Referential Optimal Universal Self-Improvers", 2003 / 2007 [M] |
| Mechanism | The machine rewrites any part of its own code once it has found a proof that the rewrite raises expected utility |
| Evidence | Theoretical. No implementation has demonstrated a non-trivial proved self-rewrite [M] |
| LLM at runtime | No |
| Reusable machinery | None executable. One principle: a self-change is accepted only against a criterion the change cannot touch |
| Decision | **Adopt the principle, replace proof with measurement** on a sealed practice set. Proof search over real code is not affordable |

### Optimal Ordered Problem Solver and adaptive Levin search

| Field | Content |
|---|---|
| Source | Schmidhuber, "Optimal Ordered Problem Solver", Machine Learning 54, 2004; Schmidhuber, Zhao, Wiering, "Shifting Inductive Bias with Success-Story Algorithm, Adaptive Levin Search, and Incremental Self-Improvement", Machine Learning 28, 1997 [M] |
| Mechanism | Search programs in order of length and runtime. Solutions to earlier problems are frozen and callable by later searches. In the adaptive form, the probability of each instruction is raised when it appears in a solution |
| Evidence | Solved Towers of Hanoi for 30 discs after learning a simpler task first [M]. Small domains only |
| LLM at runtime | No |
| Compute | CPU, modest |
| Limits | The bias shift is a table of instruction probabilities. It reorders a fixed space; it does not change what an instruction means. That is the same ceiling as Aphrodite's fold engine |
| Decision | **Adopt bias-optimal ordering as the baseline search order.** It is not self-modification in the sense required |

### Darwin Goedel Machine and successors

| Field | Content |
|---|---|
| Source | Zhang, Hu, Lu, Lange, Clune, "Darwin Goedel Machine: Open-Ended Evolution of Self-Improving Agents", arXiv:2505.22954 [V] |
| Code | `github.com/jennyzzt/dgm`, Apache-2.0 [V] |
| Mechanism | An archive of coding agents. Sample one, have it edit its own source, benchmark the child, keep it if it runs |
| Evidence | SWE-bench 20.0% to 50.0%; Polyglot 14.2% to 30.7% [V] |
| LLM at runtime | **Yes, essential.** Every edit is written by a frontier model |
| What the experiment supports | That an archive with open-ended sampling beats greedy hill-climbing when the proposer is strong. It says nothing about a proposer that is blind |
| Related | Meta's HyperAgents, `github.com/facebookresearch/HyperAgents` [V, licence NOASSERTION]. Zelikman et al., "Self-Taught Optimizer (STOP)", arXiv:2310.02304 [M]. Aphrodite's ARC3 synthesis notes that these transplant studies lack variance-matched controls |
| Decision | **Adopt the archive, reject the proposer.** Excluded from the runtime by the brief |

### AlphaEvolve

| Field | Content |
|---|---|
| Source | Google DeepMind, "AlphaEvolve: A coding agent for scientific and algorithmic discovery", 2025 [M] |
| Open implementation | OpenEvolve, `github.com/algorithmicsuperintelligence/openevolve`, Apache-2.0 [V] |
| Mechanism | A language model proposes code diffs; automated evaluators score them; an evolutionary database keeps a diverse population |
| LLM at runtime | **Yes** |
| What transfers | The evaluator-decides discipline, which Prometheus already states as Challenge 3 in `docs/phase3/PHASE3_CHALLENGES.md` |
| Decision | **Reject for the runtime.** Useful only as a design-time tool, which the charter already permits |

### AM and Eurisko

| Field | Content |
|---|---|
| Source | Lenat, "AM", 1976; "EURISKO", Artificial Intelligence 21, 1983; Lenat and Brown, "Why AM and EURISKO Appear to Work", Artificial Intelligence 23, 1984 [M] |
| Mechanism | Heuristics that propose concepts, and in Eurisko heuristics that modify heuristics |
| Evidence | AM rediscovered primes and other number-theory concepts, then stalled. The authors' own analysis: AM worked because short Lisp expressions happen to denote interesting mathematics, so small syntactic mutations were often meaningful. Heuristics did not have that property, so mutating them produced little |
| Decision | **This is the most important negative precedent.** It rules out "mutate the improver's code and select" as the primary route. Any meta-level object must be found by induction from evidence, or live in a representation where small changes are meaningful |

## 3. Learned abstraction libraries

### DreamCoder

| Field | Content |
|---|---|
| Source | Ellis et al., "DreamCoder: Bootstrapping Inductive Program Synthesis with Wake-Sleep Library Learning", PLDI 2021, arXiv:2006.08381 [M] |
| Code | `github.com/ellisk42/ec`, MIT [V]. OCaml and Python; last pushed 2023 |
| Mechanism | Wake: solve tasks by enumeration guided by a neural recognition model. Sleep: compress solutions into new library functions, and train the recognition model on replays and on self-generated tasks |
| Evidence | Multi-level libraries in list processing, text editing, graphics and physics-law domains. Learning curves flatten after roughly 10-20 cycles [M] |
| LLM at runtime | No. It trains a small neural network |
| Compute | Tens to hundreds of CPU-hours per domain, 20-100 cores, in the paper [M] |
| What the experiments support | That compression plus a learned search guide compounds for a few levels **on domains chosen to have layered structure**. Not open-ended growth |
| Limits | The compressor (version spaces) is slow. The recognition model does much of the work in ablations [M]. The code base is hard to build |
| Decision | **Adopt the loop shape and "dreaming" (self-generated practice tasks). Do not import the code.** Replace the compressor with a Stitch-style one and the neural guide with learned theory |

### Stitch

| Field | Content |
|---|---|
| Source | Bowers et al., "Top-Down Synthesis for Library Learning", POPL 2023, arXiv:2211.16605 [V] |
| Code | `github.com/mlb2251/stitch`, MIT, Rust [V]. Python bindings `github.com/mlb2251/stitch_bindings`, no licence file detected [V] |
| Mechanism | Searches abstraction bodies top-down, guided by an upper bound on the compression each partial body could achieve |
| Evidence | 3-4 orders of magnitude faster than DreamCoder's compressor with 2 orders less memory, at comparable library quality [V] |
| Integration risk | Rust build on the fleet; lambda-calculus input format differs from TFS-1's contract syntax, so a translator is needed |
| Decision | **Adopt the algorithm.** For M0 keep TFS-1's own `compress.py`, which already passes its planted test. Port or bind Stitch only if compression time becomes the bottleneck |

### babble

| Field | Content |
|---|---|
| Source | Cao et al., "babble: Learning Better Abstractions with E-Graphs and Anti-Unification", POPL 2023 [V] |
| Code | `github.com/dcao/babble`, MIT, Rust [V]. Last pushed 2023 |
| Mechanism | Library learning **modulo an equational theory**: an e-graph holds all programs equivalent under supplied rewrite rules, so abstractions are found across syntactically different but equal programs |
| Evidence | Compresses better than DreamCoder, and better still when given domain equivalences [V] |
| The gap it leaves | The equational theory is an input written by a person |
| Decision | **This is the closest prior art to my proposal's core.** I propose to close the gap: the engine learns the theory that babble takes as given. Beta-04 found the matching defect in TFS-1: extraction mis-cut 3 of 4 stones because it was not invariant to meaning-preserving refactorings |

### LLM skill libraries

| Field | Content |
|---|---|
| Source | Berlot-Attwell, Rudzicz, Si, "Library Learning Doesn't: The Curious Case of the Single-Use 'Library'", arXiv:2410.20274 [V]; "LLM Library Learning Fails: A LEGO-Prover Case Study", arXiv:2504.03048 [V]. Grand et al., "LILO", ICLR 2024 [M] |
| Finding | In LEGO-Prover and TroVE, reuse of learned functions is extremely infrequent. The reported gains come from self-correction and self-consistency [V] |
| Decision | **Adopt as a measurement rule:** count actual reuse of every learned artifact, and attribute gains by ablation. Aphrodite's ARC3 synthesis cites the same paper for the same reason |

## 4. Rule inference and theory exploration

### Ruler and Enumo

| Field | Content |
|---|---|
| Source | Nandi et al., "Rewrite Rule Inference Using Equality Saturation", OOPSLA 2021, Distinguished Paper [V]. Pal et al., "Equality Saturation Theory Exploration a la Carte", OOPSLA 2023 [V] |
| Code | `github.com/uwplse/ruler`, MIT, Rust [V] |
| Mechanism | Enumerate terms up to a size. Give each a characteristic vector of its values on sample inputs. Terms with equal vectors are candidate equations. Validate them. Keep a small set that derives the rest. **Rules already found shrink the space searched for the next ones** |
| Evidence | Rule sets 5.8x smaller, found 25x faster, than a CVC4-based tool, with no loss of proving power [V]. Competitive with hand-written rule sets for rationals in the Herbie numerical tool [M] |
| LLM at runtime | No |
| Compute | Seconds to minutes on one CPU for small domains [M] |
| Limits | Rule quality depends on the sample inputs. Validation is by testing or bounded checking unless a solver exists for the domain. Larger rules are mostly consequences of smaller ones, so a fixed domain's theory saturates |
| Decision | **Adopt the mechanism as the engine's central learning operator.** Implement it in Python over TFS-1 terms for M0 (it is a hash join over value vectors). Consider `egglog` only if derivability checking becomes a bottleneck |

### E-graphs

| Field | Content |
|---|---|
| Source | Willsey et al., "egg: Fast and Extensible Equality Saturation", POPL 2021 [M] |
| Code | `github.com/egraphs-good/egg`, MIT [V]. `github.com/egraphs-good/egglog` and `egglog-python`, MIT [V], actively maintained |
| Use | Compact representation of all terms equal under a rule set; cheap extraction of the smallest |
| Integration risk | A Rust wheel on Windows and Linux nodes. TFS-1 terms have binders; e-graphs handle binders awkwardly |
| Decision | **Optional dependency, not in M0.** A term-rewriting normaliser is enough to start |

### QuickSpec, TheSy and template-based exploration

| Field | Content |
|---|---|
| Source | Claessen, Smallbone, Hughes, "QuickSpec", 2010; Smallbone et al., "Quick Specifications for the Busy Programmer", JFP 2017 [M]. Singher and Itzhaky, "Theory Exploration Powered by Deductive Synthesis" (TheSy), CAV 2021 [M]. Einarsdottir et al., "Template-based Theory Exploration" (RoughSpec), 2021 [M] |
| Code | `github.com/nick8325/quickspec`, Haskell [V, licence NOASSERTION] |
| Mechanism | QuickSpec: discover equations among given functions by testing. RoughSpec: restrict the search to user-supplied law shapes such as commutativity or distributivity, which scales much further |
| The gap | In RoughSpec the templates are written by a person |
| Decision | **Adopt templates, and learn them.** A template abstracted from the engine's own mined rules is a modification of the rule miner itself. This is the proposed second meta-level, and I do not know of a system that closes this loop. That novelty claim is unverified |

## 5. Search over programs

### Bottom-up enumeration with observational equivalence, and its guided variants

| Field | Content |
|---|---|
| Source | Udupa et al., "TRANSIT", PLDI 2013; Albarghouthi et al., "Recursive Program Synthesis" (Escher), CAV 2013 [M]. Barke, Peleg, Polikarpova, "Just-in-Time Learning for Bottom-Up Enumerative Synthesis" (Probe), OOPSLA 2020 [M]. Shi et al., "TF-Coder", 2020 [M] |
| Code | `github.com/shraddhabarke/Probe`, no licence file [V]. `github.com/google-research/tensorflow-coder`, Apache-2.0 [V] |
| Mechanism | Build programs from smaller ones, keeping one representative per behaviour on the examples. Probe re-weights the grammar during one search from partial solutions |
| Status in Prometheus | TFS-1 already has the unguided form with exact charges, and optional per-task observational equivalence |
| Decision | **Already present. Keep it as the strongest no-learning baseline.** Any learned mechanism must beat it at matched total cost |

### Divide and conquer by examples

| Field | Content |
|---|---|
| Source | Alur, Radhakrishna, Udupa, "Scaling Enumerative Program Synthesis via Divide and Conquer" (EUSolver), TACAS 2017 [M] |
| Mechanism | Keep terms that are right on **some** examples and predicates that split the examples; join them with a decision tree |
| Why it matters here | It gives credit per example. Hestia's W4 names scalar credit over a whole lifetime as a bottleneck |
| Decision | **Adopt in M1** as a fixed, disclosed search operator. It is designer-supplied and must be reported as such |

### Deduction and inverse semantics

| Field | Content |
|---|---|
| Source | Polozov and Gulwani, "FlashMeta", OOPSLA 2015; Feser, Chaudhuri, Dillig, "Synthesizing Data Structure Transformations from Input-Output Examples" (lambda-squared), PLDI 2015 [M] |
| Code | `github.com/microsoft/prose` [V, licence NOASSERTION, C#] |
| Mechanism | For an operator with a known inverse, the required output of a missing argument is computed from the target output. A size-n problem becomes smaller problems |
| The gap | The inverse ("witness") functions are written by hand for each operator |
| Decision | **Adopt the mechanism, learn the inverses.** A mined cancellation law such as `(add (sub y a) a) = y` is exactly a witness function. This is where mined theory turns into a new search operator |

### Conflict-driven synthesis

| Field | Content |
|---|---|
| Source | Feng, Martins, Bastani, Dillig, "Program Synthesis using Conflict-Driven Learning" (Neo), PLDI 2018 [M]. Marques-Silva and Sakallah, "GRASP", 1999 [M] |
| Mechanism | When a partial program fails, find the reason and learn a lemma that rules out every other program failing for the same reason |
| Why it matters | It is the clearest case in computer science of failure becoming durable search machinery. The charter's commitment 2 is "failures carry structure" |
| Limits | Needs an abstract specification for each operator to explain a failure. Those are hand-written in Neo |
| Decision | **Candidate C is built on it.** In the selected design, mined property laws stand in for the hand-written specifications |

## 6. Evolutionary and quality-diversity methods

| Method | Source | Code and licence | What its evidence supports | Decision |
|---|---|---|---|---|
| Genetic programming | Koza 1992 [M] | many | Finds small programs with graded fitness. Fails on parity-like targets without modularity. Matches finding F1 | Not the search engine. Keep typed mutation (`tfs1/mutate.py`) as a baseline arm |
| PushGP autoconstruction | Spector and Robinson 2002; Spector et al. 2016 [M] | `github.com/lspector/Clojush`, EPL-1.0 [V] | Programs that build their own offspring can evolve variation operators. Results are mixed and task-bound [M] | Considered for Candidate D and rejected: the Eurisko precedent applies |
| AutoML-Zero | Real et al., ICML 2020, arXiv:2003.03384 [M] | `github.com/google-research/google-research` (automl_zero), Apache-2.0 [V] | Evolution rediscovers gradient descent from basic maths operations, at very large compute (thousands of CPU-days in the paper [M]) | Out of budget. Aphrodite notes such learned improvers overfit their development distribution |
| MAP-Elites and quality diversity | Mouret and Clune, arXiv:1504.04909 [M] | `github.com/icaros-usc/pyribs`, MIT [V] | Keeping the best solution per behaviour cell preserves stepping stones | Adopt the idea for the archive. Beta-04 found its descriptor unvalidated on 10 of 15 families, so descriptors must be qualified first |
| Novelty search | Lehman and Stanley 2011 [M] | -- | Abandoning the objective helps on deceptive problems | Not adopted: Theseus found 63-65% of "weird" random programs pass a viability gate, so novelty rewards noise |
| POET | Wang et al., arXiv:1901.01753 [M] | `github.com/uber-research/poet`, Apache-2.0 [V] | Co-evolving environments with agents yields solutions direct optimisation misses, in one 2-D walker domain | Deferred to M2, as Hestia advises: do not co-evolve worlds against an organism that cannot pass the second rung |

**Theory relevant to F1.** Valiant, "Evolvability", J. ACM 2009, and Feldman, STOC 2008, relate evolution by
selection to learning from correlational statistical queries, a model in which parity-like functions are not
efficiently learnable [M]. The Hestia audit cites the same results from memory and later softened "close to a
theorem" to "strong prior". I use it the same way: selection on a scalar is the wrong tool for parts with no
individual value.

## 7. Meta-learning and self-referential networks

| Work | Source | Evidence | LLM | Decision |
|---|---|---|---|---|
| Self-referential weight matrix | Schmidhuber 1993; Irie et al., "A Modern Self-Referential Weight Matrix That Learns to Modify Itself", ICML 2022 [M] | Competitive few-shot and multi-task results; the outer loop is still gradient descent | No | Basis of Candidate E |
| Fitness monotonic execution | Kirsch and Schmidhuber, "Eliminating Meta Optimization Through Self-Referential Meta Learning", arXiv:2212.14392 [V] | A network modifies itself and "improves its self-modifications" on bandit and control tasks, with no meta-optimiser: better variants simply get more compute [V] | No | The most direct external claim of improver-improves-improver. Evidence is toy-scale. Basis of Candidate E |
| Evolved plasticity | Najarro and Risi, "Meta-Learning through Hebbian Plasticity in Random Networks", NeurIPS 2020 [M] | Evolved local rules let random networks learn control tasks within a lifetime | No | Matches Hestia's escape (c). Predicted weakness, stated in the FABLE-5.1 design: nothing names and calls built structure |
| Learned optimisers | Metz et al., VeLO 2022 [M] | Useful learned optimisers need thousands of GPU-months of meta-training | No | Out of budget |

## 8. Compression, causality, state and memory

| Topic | Source | What is reusable | Decision |
|---|---|---|---|
| Minimum description length | Rissanen 1978; Solomonoff 1964 [M] | A single currency for "is this abstraction worth keeping": bits saved in the corpus minus bits to state the abstraction | Adopt as the acceptance score, replacing TFS-1's size count. Hestia asks for exactly this |
| Automata learning from queries | Angluin, "Learning Regular Sets from Queries and Counterexamples", 1987 [M] | An exact active learner for hidden-state systems, with a query-count bound | Reference learner for hidden-state task families in M2 |
| Predictive state representations | Littman, Sutton, Singh, NIPS 2001 [M] | State defined as predictions of future tests, not as hidden variables | Defines the "characteristic vector" idea already used for terms; relevant to interactive worlds in M2 |
| Causal discovery by intervention | Pearl 2009; Eberhardt on experiment selection [M] | Choose the experiment that best separates live hypotheses | Used in the evaluator (ablation, transplant), and in M2 for input selection |
| Lenski's digital evolution | Lenski et al., Nature 2003 [M] | Complex features evolved only when simpler ones were rewarded; no single intermediate was essential | Supports a curriculum with paid intermediate rungs; warns against naming one required stone |
| Curricula | Wu et al., "When Do Curricula Work?", ICLR 2021 [M] | Curricula help mainly under tight budgets | A curriculum arm needs a shuffled-order control |

On identity and agency I found no external machinery worth importing. The useful notion is operational and
small: a provenance tag on every stored item that says whether it came from the world, from the engine's own
computation, or from a parent. That is a design choice in file 04, not a borrowed result.

## 9. Comparison of the mechanisms that could carry recursion

| Mechanism | Needs fitness gradient | Needs a model | Changes what is expressible | Changes how search runs | Evidence of compounding | Cost |
|---|---|---|---|---|---|---|
| Probability re-weighting (adaptive Levin, Probe) | No | No | No | Order only | One level | Trivial |
| Library learning (DreamCoder, Stitch) | No | Optional | Yes | Shorter programs, wider branching | A few levels, then flat | CPU-hours |
| Rule inference (Ruler) | No | No | No | Prunes; enables inversion | Self-accelerating within one domain, then saturates | CPU-minutes |
| Library learning modulo theory (babble) | No | No | Yes | Finds abstractions across equal programs | One study | CPU-minutes |
| LLM self-editing (DGM, AlphaEvolve) | No | **Yes** | Yes | Yes | Yes, within benchmark | API spend |
| Heuristic mutation (Eurisko, PushGP) | Yes | No | In principle | In principle | Weak | Open-ended |
| Self-referential networks (FME) | Yes | No | Unclear | Yes | Toy tasks | GPU helps |

No row combines "no fitness gradient", "no model", and evidence of compounding beyond a few levels. The realistic
target is therefore to stack the two cheap, gradient-free mechanisms -- library learning and rule inference --
so that each feeds the other, and to measure honestly how many generations the gain lasts.

## 10. What external work does not tell us

1. Whether a learned equational theory keeps paying once a library grows. babble supplies the theory; Ruler
   supplies no library. Nobody I know of has run the closed loop.
2. Whether law templates learned in one primitive basis speed up theory mining in another.
3. How many generations a model-free loop sustains. DreamCoder's flattening is the only data point, and it had a
   neural guide.
4. Whether any of this survives a world that was not chosen for layered structure. Every positive result above
   comes from a domain picked by its authors.

Items 1-3 are what the proposed first experiments measure. Item 4 is why the world-admission gate in file 06 is
mandatory.
