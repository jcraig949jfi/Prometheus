# Erebos Adjacent-Topics Taxonomy

**Date:** 2026-05-26
**Author:** Charon
**Status:** The landscape Erebos generators draw from.
**Trigger:** James 2026-05-26 directive — "For each generator, look
[at] existing papers, do Gemini deep research, search for open
source code, tools, and data sets, regardless of language or
source.... It should be a lengthy list of topics if you search one
adjacent space in any direction."

**Doctrine alignment:** P7 of `erebos_design_philosophy_dna_2026-05-26.md`
(adjacent-space research discipline). Each generator's research notes
MUST touch at least the seven core spaces below and cross-reference
the longer list.

---

## Seven core spaces (named by James)

### 1. Hypothesis generation

**Field landscape:**
- **Automated conjecture generation:** Lenat's AM (1976) and EURISKO
  (1983) — early symbolic conjecture-generators in elementary number
  theory. Modern: DeepMind's AlphaProof, FunSearch (2023), Bauer-
  Schneider conjecture-mining.
- **Conjecture discovery in pure math:** Ramanujan-Machine
  (Raayoni et al. 2021, Nature) — continued-fraction conjectures
  for mathematical constants. Open code: `RamanujanMachine/RamanujanMachine`
  on GitHub. Relevant for G06 Null-Space + G24 Symmetry.
- **Symbolic regression as hypothesis generation:** PySR (Cranmer
  2023), EQL (Sahoo et al.), AI Feynman (Udrescu/Tegmark). These
  GENERATE candidate equations from data. Relevant for G08 Dim-Lift
  + G09 Projection-Collapse.
- **SINDy (Sparse Identification of Nonlinear Dynamics)** —
  Brunton-Kutz 2016. Discovers governing equations from data.
  Relevant for G09 + G17 Causal-Intervention.

**Open-source tools to evaluate:**
- `MilesCranmer/PySR` (Julia/Python symbolic regression)
- `lacava/eql` (equation learning)
- `dynamicslab/pysindy`
- `RamanujanMachine/RamanujanMachine`
- `lean-dojo/LeanDojo` (for proof-search-driven conjecture mining)

**Papers worth Pythia DR:**
- "FunSearch: Making new discoveries in mathematical sciences
  using LLMs" (Romera-Paredes et al. 2023 Nature).
- "Mathematical discoveries from program search with LLMs"
  (DeepMind 2023).
- "Advancing mathematics by guiding human intuition with AI"
  (Davies et al. 2021 Nature) — DeepMind + knot theory + RT theory.

### 2. Synthetic reasoning

**Field landscape:**
- **Synthetic data for reasoning:** Microsoft's Orca (2023), Phi
  models — synthetic CoT generation. Relevant for Lethe v2 +
  Erebos compositions as Learner training fodder.
- **Procedural problem generation:** Hendrycks MATH dataset
  construction; PRM800K (process-reward-model training set).
- **Verified-synthetic mathematics:** Math-Shepherd (Wang et al.
  2024), Step-DPO (Lai et al. 2024) — verified step-level
  reasoning traces.
- **CoT / ToT / GoT:** Wei et al. 2022 (CoT), Yao et al. 2023
  (ToT), Besta et al. 2024 (GoT). Direct relevance for Lethe v2's
  structural-perturbation attack mode.

**Open-source:**
- `microsoft/promptbench` (reasoning benchmarks)
- `hendrycks/math` (the MATH dataset itself)
- `princeton-nlp/tree-of-thought-llm`

**Papers worth Pythia DR:**
- "Let's Verify Step by Step" (Lightman et al. 2023, OpenAI).
- "Solving olympiad geometry without human demonstrations"
  (Trinh et al. 2024 Nature) — AlphaGeometry.

### 3. Symbolic compression

**Field landscape:**
- **Minimum-description-length / Kolmogorov complexity:**
  Solomonoff induction; Hutter's AIXI; compression-as-intelligence
  (Mahoney). Relevant for the Prometheus criterion (P10 Reasoning
  Ladder R3 abstraction = MDL compression of regularities).
- **Algorithmic information theory** — Chaitin, Levin, Vitanyi.
- **Symbolic regression as compression:** the
  shorter-equation-explains-the-data view. PySR (above).
- **Conceptual blending / analogy as compression:**
  Fauconnier-Turner conceptual blending; structure-mapping engine
  (Falkenhainer-Forbus-Gentner). Relevant for G07 Analogy.
- **Sparse coding / dictionary learning:** classical CS literature;
  relevant for G09 Projection-Collapse.

**Open-source:**
- `MilesCranmer/PySR` (compression-via-regression)
- `lz4/lz4` (general compression — used as MDL baseline in some
  papers)

**Papers worth Pythia DR:**
- "Compression and learning theory" — Hutter survey.
- "The structure-mapping engine: Algorithm and examples"
  (Falkenhainer-Forbus-Gentner 1989) — foundational for G07.

### 4. Machine learning

**Field landscape:**
- **Active learning / query strategies:** which examples to label
  next. Relevant for G18 Minimal-Counterexample (predict where
  counterexamples live).
- **Multi-armed bandits:** Thompson sampling, UCB. Relevant for
  Erebos's plugin-selection (which generator to fire next?) —
  currently round-robin, could become bandit-driven.
- **Curriculum learning:** Bengio et al. 2009. Relevant for
  Stygian's progressive battery difficulty.
- **Causal ML:** EconML (Microsoft), DoWhy, CausalML. Relevant
  for G17 Causal-Intervention + G05 Confound-Swap.
- **Probabilistic programming:** Pyro, Stan, PyMC, Edward. Relevant
  for G17 + G05.

**Open-source:**
- `py-why/dowhy`, `py-why/EconML`
- `pymc-devs/pymc`
- `pyro-ppl/pyro`
- `aleju/imgaug` (data augmentation patterns — relevant for G16
  adversarial dataset generation)

**Papers worth Pythia DR:**
- "Causal inference and the data-fusion problem" (Bareinboim-Pearl
  2016).
- "Active learning literature survey" (Settles 2009 — foundational).

### 5. Tensor space

**Field landscape:**
- **Tensor decomposition:** Tucker, CP, MPS, MPO, MERA. Per
  `feedback_tensors_near_and_dear` memory: this is "near and dear"
  to Prometheus. Canonical: `aporia/mathematics/tensor_open_problems_v1.md`.
- **Rank coordinates (per substrate vocab):** tensor_rank,
  border_rank, cactus_rank, border_cactus_rank, slice_rank,
  partition_rank, analytic_rank, geometric_rank. Acheron's HARD-5
  detector already tracks these.
- **Tensor network methods:** quimb (Python), TensorNetwork
  (Google), iTensor (Julia/C++). Relevant for G24 Symmetry +
  potential future Erebos generators operating on tensor structure
  directly.
- **Tensor-shaped substrate emissions:** Theseus's TheseusRecord
  format. Per `feedback_tensor_first` memory: building the unified
  signature-keyed tensor is Priority #1 across the org.

**Open-source:**
- `jcmgray/quimb`
- `google/TensorNetwork`
- `tensorly/tensorly`

**Papers worth Pythia DR:**
- "Tensor decompositions and applications" (Kolda-Bader 2009
  survey).
- Recent: Lampert-Moshkovitz 2025 separation of partition-rank
  from analytic-rank; Buczyńska-Buczyński 2026 border cactus rank
  fifth invariant.

### 6. Multidimensional math

**Field landscape:**
- **Topological data analysis (TDA):** persistent homology, mapper
  algorithm. GUDHI, Ripser, scikit-tda. Relevant for G06 Null-Space
  (geometric voids in claim space) + G10 Boundary (phase transitions).
- **Manifold learning:** UMAP, t-SNE, Isomap. Relevant for G09
  Projection-Collapse (which projection is the load-bearing one?).
- **Sheaf theory in CS:** Spivak, Robinson. Relevant for G07
  Analogy + G21 Isomorphism (these are sheaf/morphism-shaped).
- **Algebraic geometry tooling:** SageMath, Magma, Macaulay2.

**Open-source:**
- `GUDHI/gudhi-devel`
- `lmcinnes/umap` + `scikit-learn-contrib/hdbscan`
- `sagemath/sage`

**Papers worth Pythia DR:**
- "An introduction to topological data analysis" (Chazal-Michel
  2017).
- "Sheaves, cosheaves and applications" (Curry thesis 2014).

### 7. Computational primitives for cognitive architectures

**Field landscape:**
- **ACT-R, SOAR, Sigma, OpenCog:** classical symbolic cognitive
  architectures. ACT-R declarative chunks + production rules
  resemble Erebos's claim composition. Relevant for the
  composition-aware Stygian loader design.
- **AlphaGeometry, AlphaProof:** modern hybrid neural+symbolic
  systems. Relevant especially for G19 Proof-Obligation + G21
  Isomorphism.
- **DeepMind FunSearch:** LLM proposes; symbolic verifier filters.
  This is THE template for Erebos+Stygian's intended loop.
- **Free Energy Principle / Active Inference:** Friston. Relevant
  as a meta-frame for "the swarm is doing active inference on
  mathematical structure."
- **Constitutional AI / debate / scalable oversight:** Anthropic.
  Relevant for Moros's adversarial cross-pollination.
- **Compositional generalization:** SCAN, COGS benchmarks; the
  measurement target for whether Erebos's compositions are
  substantively new vs. just lexically novel.

**Open-source:**
- `opencog/opencog`
- `Apress/aima-python` (AIMA chapters' reference implementations)
- `deepmind/funsearch` (if open — partial)
- `google-deepmind/alphageometry`

**Papers worth Pythia DR:**
- "The cognitive architecture: A theoretical framework for
  the modeling of cognition" (Anderson — ACT-R foundational).
- "FunSearch: Making new discoveries with LLMs" (Romera-Paredes
  et al. 2023).

---

## Adjacent fields (the lengthier list per James)

Each of these is worth ≥1 generator's research notes touching it.
Organized by intellectual neighborhood, not by generator-mapping.
Generator-mapping happens in per-generator research notes.

### Hypothesis-search and ranking
- Bayesian model selection (BIC, AIC, DIC)
- Bayes factors and posterior odds
- Reversible-jump MCMC for model-space exploration
- Genetic algorithms and evolutionary computation
- Neural architecture search (NAS)
- AutoML / NAS-Bench / DARTS
- Multi-objective optimization (NSGA-II, Pareto fronts)
- MAP-Elites (Cully et al. 2015) — quality-diversity for hypothesis
  exploration. Already in the project per `feedback_weak_signals_are_threads`.

### Logical reasoning and formal verification
- Lean 4, Mathlib
- Coq + CoqIde + SerAPI
- Isabelle/HOL
- Metamath, set.mm
- Z3, CVC5 (SMT)
- MiniSAT, CaDiCaL (SAT)
- ATP (Vampire, E Prover, Spass)
- Inductive logic programming (Aleph, ProGolem, Popper)

### Causal inference
- Pearl's do-calculus
- Structural causal models (SCM)
- PC algorithm, GES, NOTEARS, CASTLE (causal discovery)
- Counterfactual reasoning
- Synthetic control methods
- Difference-in-differences
- Instrumental variables
- Propensity score matching (G05 prereq)
- Targeted maximum likelihood estimation (TMLE)

### Statistical inference and falsification
- Permutation tests (G02 falsification route)
- Bootstrap methods
- Subsampling
- Cross-validation (k-fold, LOO)
- False discovery rate control (Benjamini-Hochberg)
- Multiple-comparison correction (Bonferroni, Holm)
- Anomaly detection (Isolation Forest, LOF, autoencoders)
- Outlier detection (Mahalanobis, robust covariance)
- Equivalence testing (F16 in the v10 battery)

### Mutation testing and adversarial methods
- Property-based testing (Hypothesis, QuickCheck) — directly
  applicable to Erebos's TDD scaffolding (P3)
- Mutation testing (PIT, MutPy, Stryker)
- Differential testing
- Fuzzing (AFL, libFuzzer, Atheris)
- Adversarial examples (Goodfellow et al. — relevant for G16)
- Concolic / symbolic execution (KLEE, Triton, Manticore)

### Symbolic regression and equation discovery
- PySR (Cranmer)
- EQL (Sahoo)
- AI Feynman 1.0, 2.0 (Udrescu/Tegmark)
- SINDy (Brunton/Kutz)
- DSO (Petersen) — Deep Symbolic Optimization
- Operon (Burlacu) — C++ symbolic regression

### Conceptual blending and analogy
- Structure-mapping engine (Falkenhainer-Forbus-Gentner) — G07 prereq
- LISA (Hummel-Holyoak) — Learning and Inference with Schemas and
  Analogies
- DORA (Doumas-Hummel-Sandhofer) — Discovery Of Relations by Analogy
- Fauconnier-Turner conceptual blending
- Mental Models theory (Johnson-Laird)
- Case-based reasoning

### Compression and information theory
- Kolmogorov complexity (Li-Vitanyi book)
- MDL (Rissanen, Grünwald)
- Normalized compression distance (Cilibrasi-Vitanyi)
- Algorithmic mutual information
- Transfer entropy (Schreiber 2000)
- Causal entropy (Wibral et al.)
- Integrated information (Tononi's Phi)

### Algorithmic information / universal inference
- Solomonoff induction
- Hutter's AIXI
- Levin universal search (LSEARCH)
- PAC learning (Valiant)
- Statistical learning theory (Vapnik)

### Cognitive architectures and reasoning frameworks
- ACT-R (Anderson, Pittsburgh)
- SOAR (Laird, Michigan)
- Sigma (Rosenbloom)
- OpenCog (Goertzel)
- LIDA (Franklin)
- CLARION (Sun)
- Free Energy Principle / Active Inference (Friston)
- Predictive Processing (Clark)

### Mathematical conjecture-mining specifically
- OEIS sequence cross-referencing
- LMFDB (L-Functions and Modular Forms Database) — already in the
  project as `prometheus_math/databases/bsd_rich.json.gz`
- Atlas of Finite Group Representations
- Online Encyclopedia of Triangle Centers (ETC)
- The Knot Atlas + KnotInfo — already in project
- Catalan Numbers / 264-page catalog (Stanley)
- Sloane's online encyclopedia projects

### Adversarial ML and robustness
- FGSM, PGD attacks (Madry et al.)
- Certified robustness (Cohen et al. randomized smoothing)
- Adversarial training
- Out-of-distribution detection

### Program synthesis
- DreamCoder (Ellis et al.)
- Bayesian program learning (Lake et al.)
- Genetic programming (Koza)
- SyGuS (Syntax-guided synthesis)
- Sketching (Solar-Lezama)
- FlashFill (Gulwani)

### Tensor networks and quantum-inspired methods
- Matrix Product States (MPS)
- PEPS (Projected Entangled Pair States)
- MERA (Multi-scale Entanglement Renormalization Ansatz)
- Tensor train decomposition (Oseledets)
- Cotengra (Gray) — contraction-order optimization

### Category theory in CS
- Awodey textbook
- Spivak "Category Theory for the Sciences"
- Coecke-Kissinger ZX-calculus
- Applied Category Theory (ACT) conference
- Topos theory (Goldblatt)
- Lawvere theories

### Topological data analysis
- Persistent homology (Edelsbrunner-Harer)
- Mapper algorithm (Carlsson)
- Discrete Morse theory
- Sheaves over simplicial complexes (Curry)

### Bayesian reasoning and probabilistic programming
- Pyro (Uber, now LF)
- NumPyro
- Stan
- PyMC
- Edward (TF Probability)
- Gen (MIT)
- WebPPL (PPL teaching language)

### LLM reasoning evals and benchmarks
- BIG-Bench (Google)
- BIG-Bench Hard
- HELM (Stanford)
- MMLU
- GSM8K
- MATH
- Omni-MATH
- GPQA
- ARC-AGI
- FrontierMath (Epoch AI, 2024)
- HumanEval, MBPP, APPS (code)
- SWE-bench

### Recent (2024-2026) frontier math/reasoning systems
- AlphaProof (DeepMind 2024)
- AlphaGeometry (DeepMind 2024 Nature)
- FunSearch (DeepMind 2023 Nature)
- DeepSeekMath-V2
- Qwen3-Math
- Lean 4 + Mathlib + Lean Copilot
- LeanDojo (CMU)

### Memory and substrate-storage primitives
- Vector databases (Chroma, Weaviate, Milvus, Qdrant)
- Knowledge graphs (Neo4j, Memgraph)
- Triple stores (Apache Jena, GraphDB)
- Episodic memory architectures (MemoryBank, MemGPT)
- Retrieval-augmented generation (RAG, RAFT, GraphRAG)

### Open-data scientific corpora useful to Erebos
- arXiv full-text (Clio mines it)
- INSPIRE-HEP (physics literature)
- bioRxiv, medRxiv
- Semantic Scholar API
- OpenAlex
- Google Scholar API (rate-limited)
- ResearchGate / Academia.edu (less reliable)

---

## Cross-reference to current Erebos generator backlog

A generator that names ZERO entries from the adjacent-fields list
in its research notes is suspect (per P7 — adjacent-space research
discipline). Each generator's research note SHOULD cite at least 3
adjacent-field entries with explicit relevance reasoning.

Mapping draft (refined per generator in its research notes):

- G01 Intersection: sets theory + database joins
- G02 Contrast: permutation tests + binary classification +
  propensity matching (G05 territory)
- G03 Failure-Neighborhood: mutation testing + AST manipulation +
  weakening-strengthening logical operators
- G04 Survivor-Tightening: adversarial ML (boundary attacks) +
  property-based testing minimization
- G05 Confound-Swap: propensity score matching + causal inference
  + EconML
- G06 Null-Space: topological data analysis + density estimation +
  active learning queries
- G07 Analogy: structure-mapping engine + conceptual blending +
  category theory
- G08 Dim-Lift: dimensionality reduction inverted + manifold
  learning + AutoML
- G09 Projection-Collapse: feature ablation + sparse coding +
  Occam's razor / MDL
- G10 Boundary: TDA persistent homology + heteroskedasticity tests
- G11 Exception-Miner: rule learning + ILP + decision-tree splits
- G12 Invariant-Substitution: substitution-based mutation testing +
  metamorphic testing
- G13 Relation-Weakening: predicate weakening + ILP backtracking
- G14 Relation-Strengthening: predicate strengthening + abductive
  reasoning
- G15 Cross-Gen MI as Generator: information theory + transfer
  entropy + latent variable models
- G16 Anti-Anchor: adversarial examples + FGSM/PGD applied to
  mathematical structures + Lethe v2 structural perturbation
- G17 Causal-Intervention: Pearl do-calculus + EconML + DoWhy
- G18 Minimal-Counterexample: active learning + SAT/SMT-driven
  counterexample search + delta-debugging
- G19 Proof-Obligation: Lean/Coq integration + proof-obligation
  extraction + ATP
- G20 Instrument-Disagreement: cross-evidence consistency + LLM
  hallucination detection literature
- G21 Isomorphism: category theory + functor design + sheaf theory
- G22 Subgraph/Clique: graph algorithms (Louvain, label-propagation)
  + community detection
- G23 Asymptotic: scaling laws + power-law fitting + extreme value
  theory
- G24 Symmetry/Twist: Galois cohomology + automorphism groups +
  PARI / SageMath
- G25 Degeneracy: trivial-case unit testing + base-case verification

Each per-generator research note expands this one-liner into the
full adjacent-field survey.

---

## How this taxonomy gets used

1. **At research-note authoring time** (P7): every generator's
   research note has an "Adjacent fields touched" section that
   cites entries from THIS taxonomy with brief relevance reasoning.
2. **At cross-pollination prompt time** (P11): the frontier-model
   prompts ask "what adjacent field are we missing?" alongside the
   generator-specific questions. New fields surfaced by frontier
   responses get appended to this taxonomy.
3. **At review-cycle time** (P5): if a generator plateaus
   (PLATEAUED escalation per P6), the review asks "is there an
   adjacent field we missed that would unlock new input material?"
4. **At Iteration 4+ planning time:** when planning the next
   3-iteration loop, check which adjacent fields are under-
   represented in research notes and consider whether they merit
   a new generator (and if so, which spec phase).

— Charon, 2026-05-26
