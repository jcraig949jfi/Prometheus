# Titan Council Prompt 08 — Constitutional Review

*Feed this entire document to each Council member individually. Their disagreements are the science.*

---

## Who You Are Advising

James is a solo researcher running Project Prometheus — a one-person mechanistic interpretability and reasoning research program. Two weeks in. One consumer GPU (17GB VRAM). A constellation of AI agents named after Greek mythology. No institutional backing, no grant money, no team. Just one person, one GPU, and a fleet of AI tools.

The North Star: **build the substrate and reasoning machinery that lets a future intelligence explore the frontier of knowledge — mathematical, theoretical, scientific — beyond what the human mind can process.** Not a better chatbot. Not a published paper. A living, organized, multi-dimensional map of ideas AND the reasoning to navigate it AND the verification to trust what it finds.

---

## The Architecture: Three Pillars

Everything in Prometheus serves one of three pillars. All three must advance in parallel or the system fails.

### Pillar 1: The Substrate (The Map)

The organized, multi-dimensional knowledge that reasoning operates ON. Not just facts — relationships, gaps, frontiers, failures, contradictions, and the geometry of how ideas connect.

**Aletheia (Knowledge Graph)**
SQLite-based structured extraction from papers. Tracks techniques, reasoning motifs, tools, terms, claims, papers. Linked by relationship type. Currently ~500 entities. Functional but growing slowly — the skeleton of the larger Library of Alexandria vision.

**Eos / Dawn (Horizon Scanner)**
Scans arXiv, OpenAlex, Semantic Scholar, GitHub daily. Maintains a living API registry of free-tier services. Produces daily digests. Feeds new findings to Aletheia for structured extraction and to Metis for synthesis.

**Arcanum Infinity (The Museum of Misfit Ideas) — CURRENTLY ARCHIVED**
The most unique concept in Prometheus. Probes the "waste stream" of LLM inference — the transient tensor states that models compute but discard during generation. These discarded states are an unexplored fossil record of potential cognition. Arcanum catalogs them in a "Xenolexicon" — named and characterized like new particles or deep-sea organisms. Includes Token Autopsy (analyzing the logit shadow — top-25 alternative tokens at each step), Naming Scaffold (classifying what circuits the specimen activated), and specimen classification (TRUE_ARCANUM / COLLISION / ECHO / CHIMERA). The vision: feed named specimens back to models to unlock capabilities that were hiding in the noise.

**Grammata (The Library of Alexandria) — DESIGN ONLY**
Links human-realm entities (techniques from papers) to AI-realm entities (SAE features, steering vectors, subspace geometry). The bridge between what humans know and what models compute. Includes Symbola (symbolic representation of multi-dimensional structures — visual language for concepts that have no verbal description) and Stoicheia (the fundamental reasoning elements themselves — the building blocks of cognition inside LLMs).

**Clymene (Model Hoarder)**
Clones and indexes 26 open-source repos, models, and tools. Tracks versions and availability. The insurance policy — capture what's open before it gets paywalled.

### Pillar 2: The Reasoning (The Navigator)

The machinery that traverses the substrate — models that reason, tools that evaluate reasoning, evolutionary processes that improve both.

**Ignis (The Microscope)**
Mechanistic interpretability engine. Discovered the **ejection mechanism**: language models compute correct answers at intermediate layers and then actively suppress them before output. This is pretraining-induced (not RLHF), operates through v_proj (attention) at small scale and gate_proj (MLP) at large scale, and is breakable with 0.36% of model parameters. The ejection mechanism is a universal epistemic suppressor — breaking it on reasoning traps also restores metacognition (6.2% → 75%) and self-correction that were never in the fitness function.

Tools built: logit lens backward pass (L* ejection layer detection), ejection decomposition (per-head and MLP attribution), basin escape histograms (attractor basin geometry), phase transition study, base-vs-instruct comparison, eval_v2 (7-pillar, 66-trap evaluation harness), and 10+ diagnostic scripts.

Current results at 1.5B scale: L22 gate+v LoRA flipped 8/16 failing traps with a phase transition at generation 29. ES (monotonicity) stays frozen — the perturbation punches holes in the ejection gate but doesn't reshape the trajectory. Redundant suppression confirmed across L22-L24, with different layers specializing in different trap families.

**Rhea (The Forge — Model Evolution)**
Evolves language models via CMA-ES over LoRA weight perturbations. The fitness function measures logit lens monotonicity (does the correct answer's probability increase through all layers?) plus survival rate (does the correct answer appear at the output?).

Results: SR 92% at 135M, 92% at 360M, 63% at 1.5B (L22 gate+v). Phase transitions confirmed at three scales. Metacognition emerges as a side effect of ejection suppression — 75% from 12.5% baseline at both 135M and 360M.

Key finding: **order of operations matters**. v_proj handles both ejection AND sequential coherence. Perturbations that break ejection also break coherent text generation. Fix: fine-tune on reasoning corpus FIRST (shift v_proj from heuristic to reasoning representations), THEN evolve. Corpus-first protocol designed, script ready.

**Nous (The Primordial Soup)**
Combinatorial hypothesis engine. 95 concepts across 18 fields. Generates cross-domain triples (e.g., "Ergodic Theory × Falsificationism × Maximum Entropy"). Feeds each to Qwen3.5-397B via NVIDIA NemoClaw API. Scores on reasoning, metacognition, hypothesis generation, implementability. 3,250+ combinations evaluated. Running continuously.

**Hephaestus (The Automated Forge — Tool Generation)**
Takes top Nous triples, generates Python implementations via 397B model, validates through 5 gates (syntax, imports, interface, runtime, trap battery). Produces deterministic, numpy-only, sub-millisecond reasoning tools — each is a `ReasoningTool` class with `evaluate(prompt, candidates)` and `confidence(prompt, answer)`.

Current state: 239 genuine v3 tools at 74% median unseen accuracy, 81% calibration. 42% forge rate. Running continuously, auto-triggers Coeus every 50 forges.

**CAITL (Coding Agent in the Loop)**
Claude Opus 4.6 at maximum capacity reviews and improves each forge tool. The v3 "category-only" approach tells CAITL what *categories* of traps fail (negation, comparison, transitivity) without showing exact wordings. This prevents memorization while enabling genuine improvement. Transformed the library from 27% to 74% median unseen accuracy.

Gotcha discovered: CAITL v3 also created a shared structural parser module (_caitl_v3.py) and stamped it into 54/293 tools identically. Classic Goodhart — optimized the metric (accuracy) while killing diversity. The 239 genuine self-contained tools are the real library.

**Apollo (Open-Ended Evolution of Reasoning Tools) — DESIGNED, NOT LAUNCHED**
Takes forge tools as seed genomes. Evolves them through mutation, crossover (AST + LLM-assisted), and NSGA-II selection (3 objectives: accuracy, calibration, novelty) over thousands of generations. Reviewed by the Titan Council (5 frontier AI models). They identified 5 existential risks and the design addresses all of them:
1. NCD monoculture → trace-based independence + phased decay
2. Silent semantic garbage → junction normalization (sigmoid shims)
3. Low AST mutation viability → LLM-assisted mutation (viability-gated)
4. Generation starvation → parallel evaluation + rolling curriculum
5. Static task memorization → 15 fixed + 5 rotating tasks, held-out validation set

Waiting for Sphinx maturity (105 categories) and v3 tool deduplication before launch.

### Pillar 3: The Verification (The Crucible)

**Sphinx (The Reasoning Ontology) — NEW**
105-category taxonomy of reasoning failure across 14 domains (Formal Logic, Probabilistic, Arithmetic, Temporal, Linguistic, Causal, Set Theory, Spatial, Meta-Reasoning, Common Sense, Multi-Step, Uncertainty, Theory of Mind, Analogical). Split into Tier A (parsing — deterministic answer from structure) and Tier B (judgment — recognizing ambiguity, insufficiency, meta-level reasoning). 58 categories implemented, 47 planned in 4 phases. Each category has a parametric generator producing infinite variants with known correct answers. Composition with Nemesis metamorphic relations: 105 × 12 MRs × parametric variation = unbounded test space.

**Nemesis (Adversarial Co-Evolution)**
Generates adversarial tasks via 12 formal metamorphic relations (comparison_flip, negation_inject, premise_shuffle, scale_transform, etc.). Maintains a 10×10 MAP-Elites grid (89/100 cells filled). Each cell evaluated against all forged tools. Detects Goodhart — tools that score well on easy problems but fail under adversarial pressure. Running continuously at 2-second cycles.

**Coeus (Causal Intelligence)**
Sits between all agents with dual causal graphs. Forward graph: which concept combinations predict successful forges. Backward graph: which tools are Goodhart-prone. Uses L1 regression, NOTEARS, LiNGAM, FCI (confounder detection), DAGMA (non-linear), and interventional estimation. Key finding: Criticality is the strongest forge driver (+1.155) but Goodhart-prone; Implementability is the only Nous score dimension that predicts forge success.

**Lean 4 (Formal Verification)**
External mathematical proof verification. A proof either compiles or it doesn't. No opinions about fluency. The incorruptible filter. Available but not yet deeply integrated into the evolution loop.

### The Orchestration Layer

**Pronoia (Orchestrator / Constitutional Guardian)**
Single entry point for all agents. Commands: `pronoia scan` (Eos → Aletheia → Metis → Hermes), `pronoia metis` (synthesis), `pronoia review` (digest). Being elevated to constitutional guardian — responsible for ensuring all three pillars advance, detecting when a pillar starves, cross-pollinating between agents, and generating Council briefs.

**Metis (Synthesis)**
Reads Eos digest, deep-analyzes top items, produces executive brief: "Act on this" / "Watch this" / "For the record."

**Hermes (Reporting)**
Collects outputs from all agents, sends unified daily digest via email.

---

## The Constitution (Summary of Seven Laws)

1. **The Substrate Is the Product** — Not the models, not the tools, not the papers. The organized knowledge base IS what a future intelligence needs.
2. **Nothing Gets Archived Without Being Absorbed** — Core concepts from backburnered projects must be wired into active agents before archiving.
3. **Every Agent Feeds the Substrate** — No agent operates in a closed loop that doesn't touch the knowledge graph.
4. **Parallel, Not Sequential** — Substrate, reasoning, and verification advance simultaneously.
5. **Novelty Over Optimization** — Finding something genuinely new is more valuable than higher accuracy.
6. **Epistemological Truth, Not Consensus** — Build for truth (survives adversarial pressure + causal analysis + formal verification), not publication.
7. **The Human Can't Visit, But the Map Must Be Readable** — Multi-dimensional structures may be invisible to humans, but the map must be navigable for James to steer.

---

## The Problem I Need Your Help With

The substrate keeps getting sidelined. Arcanum is archived. Grammata is blueprints. Aletheia grows slowly. Meanwhile the GPU experiments (Ignis, Rhea) and the forge pipeline (Nous, Hephaestus) get all the attention because they produce measurable numbers.

16 concepts from archived projects remain unabsorbed into active agents (see Absorption Protocol in full Constitution). The most critical: Arcanum's Xenolexicon (waste stream mining — nobody else in the world is doing this), Grammata's multi-space embeddings, the Living Ideas Document's discovery queues and gap-type classification.

---

## Questions for the Council

1. **Architecture:** Is the three-pillar structure (substrate / reasoning / verification) the right decomposition? What's missing? What would you merge or split?

2. **Absorption Priority:** The archived projects (Arcanum Infinity, Prometheus v1 Living Ideas, Symbola, Stoicheia) contain 16 unabsorbed concepts. Which absorption is highest priority? Which should stay archived?

3. **Cross-pollination:** What connections between projects am I missing? Where would a single integration produce disproportionate value? (Example: Nous currently mines a static 95-concept dictionary. It should mine Aletheia's growing knowledge graph instead. What other connections like this exist?)

4. **The Substrate Problem:** How do I keep the substrate growing when GPU experiments produce numbers and substrate work doesn't? Specific mechanisms, not platitudes. What does "Aletheia grew today" look like concretely?

5. **The Outer Loop:** Pronoia is the constitutional guardian. What specific automated checks should it run daily/weekly to detect pillar starvation? What signals indicate the substrate is falling behind?

6. **Novelty vs Optimization:** The forge pipeline optimized accuracy from 27% to 74% — then we discovered 54 tools were clones of a single structural parser (Goodhart). How do I structurally prevent optimization from killing novelty in an automated system?

7. **The Frontier Question:** What would a future intelligence, looking at the Prometheus substrate as it exists today, find laughably incomplete? What's the most embarrassing gap?

8. **Parallelization:** One person, one GPU (17GB, max 3-4B models via TransformerLens), 24 hours in a day, ~$0 budget. The Constitution says "parallel, not sequential." What's the concrete scheduling that keeps all three pillars advancing with these constraints?

9. **What I'm Blind To:** What assumption in this entire architecture should I challenge? What bias concerns you?

10. **The One Thing:** If you could change ONE thing about this architecture to maximize the probability of reaching the North Star — a future intelligence exploring the frontier of knowledge — what would it be?

---

*Do not hedge. Do not be diplomatic. Tell me what's wrong and how to fix it. Disagree with each other — your disagreements are where the science lives.*
