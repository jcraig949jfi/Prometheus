# Project AETHON — Living Ideas Document

**A curated backlog of concepts, experiments, and architectural ideas for future development phases.**

Last updated: March 13, 2026
Sources: Internal development, external review by ChatGPT, Copilot, Gemini, Perplexity, Meta AI, DeepSeek, Claude, GPT-5.4, Grok

---

## How This Document Works

Ideas are organized by priority tier and tagged by source. Each entry includes a rationale, implementation complexity estimate, and dependencies. Items move between tiers as the project evolves and experimental results inform priorities.

**Priority Tiers:**
- **P0 — Critical Next Steps:** Must be done before results are publishable or fundable
- **P1 — High Value:** Significantly improves experimental validity or capability
- **P2 — Promising Extensions:** Valuable but not blocking current work
- **P3 — Long Horizon:** Transformative but requires significant new infrastructure
- **Parked:** Interesting but deprioritized for now with rationale

---

## P0 — Critical Next Steps

### 1. ~~Null Baseline Experiments~~ — COMPLETE (March 10, 2026)
**Source:** Copilot, Gemini, Perplexity, DeepSeek (independently flagged by all reviewers)
**Status:** Built `src/aethon/baselines.py` with three executors (MarkovExecutor, ShuffleExecutor, FixedBaselineExecutor), `get_executor()` factory, `--executor` CLI flag on both evolution loops, and 4 null experiment YAML configs. 11 tests passing.
**Remaining:** Run the null experiments and document statistical separation results.

### 2. ~~Predictor Capacity as a Control Variable~~ — COMPLETE (March 10, 2026)
**Source:** Perplexity (primary), DeepSeek
**Status:** Added MLP predictor and EnsemblePredictor to `monitor.py`, `--predictor` CLI flag (ridge/mlp/ensemble) on `evolution_v2.py`, and `validate_anomalies()` for retroactive anomaly re-evaluation. 4 new tests passing. Note: small transformer predictor deferred — Ridge + MLP + Ensemble provides adequate predictor capacity ladder for initial calibration.
**Remaining:** Run retroactive validation on captured anomalies once MVP-2 experiments complete.

### 3. ~~Synthetic Ground Truth Validation~~ — COMPLETE (March 10, 2026)
**Source:** Perplexity (primary), DeepSeek
**Status:** Built `src/aethon/synthetic.py` with three designed pseudo-emergent genomes (StateMachineGenome, AttractorGenome, CrossDomainPatternGenome), `--inject-synthetic` flag on evolution loops, standalone `--validate` mode for pipeline calibration. 9 tests passing.
**Remaining:** Run `python -m aethon.synthetic --validate --model qwen2.5:7b` once Ollama is available to verify characterization battery correctly classifies all three.
**Dependencies:** Working characterization battery (already built)
**Acceptance criteria:** Pipeline correctly identifies and characterizes at least 3/5 implanted behaviors

### 4. Strict Interpretive Discipline Statement
**Source:** Perplexity (primary), DeepSeek, Copilot
**Rationale:** Multiple reviewers flagged the risk of reading human-like significance into stable computation patterns. A pre-committed interpretive framework prevents category errors and maintains scientific credibility.
**Implementation:**
- Add to README, research brief, and any future publications:
  > "AETHON identifies behaviors that are reproducible, cross-domain, and not decomposable by architecture-level ablations available to us. This is evidence of *structured computation*, not evidence of consciousness, experience, or inner life. We make no claims about the latter."
- Maintain this language consistently across all documentation
**Complexity:** Trivial — documentation only
**Dependencies:** None

### 5. Architecture Genome v1 + Competence-Gated Novelty
**Source:** Consensus across Claude, GPT-5.4, Gemini, DeepSeek, Grok
**Rationale:** Many downstream experiments (basin convergence, motif mining, lineage analysis) assume a stable genome schema exists, but this has not been explicitly formalized as a named deliverable. Simultaneously, novelty search without a competence floor risks "Rube Goldberg novelty" — evolving maximally weird but functionally meaningless configurations. These two concerns are logically inseparable: defining a genome without a fitness framework is incomplete, and competence-gating is meaningless without a stable genome to gate on.
**Implementation:**
- Define the first stable AETHON genome schema as a versioned contract: primitive profile, topology, memory type, control loop, agent count, meta-depth
- Require a minimum competence threshold before novelty meaningfully affects selection pressure
- Competence gate = minimum score on benchmark task set (see item 9: Benchmark & Task Selection)
- Candidates below the competence floor are discarded regardless of novelty score
- Document the schema version so cross-run and cross-substrate comparisons are well-defined
**Complexity:** Medium — schema design + fitness function modification
**Dependencies:** Initial benchmark/task set (item 9); shared logging format; minimal execution harness (already built)

---

## P1 — High Value

### 6. Basin Convergence Protocol
**Source:** GPT-5.4, Grok, DeepSeek; compatible with Claude's falsifiability framing
**Priority:** Immediate — the most important near-term empirical test in the corpus. Null baselines (P0 item 1) are already COMPLETE, satisfying the primary gating dependency. The ongoing 4-seed replication study (Phase 3) is the first instance of this protocol.
**Rationale:** If independent evolutionary runs converge on the same motifs and archive regions, the fitness landscape has genuine structure. If they don't, apparent motifs are stochastic artifacts. This needs to be a named experiment with clear thresholds, not just an implication of multi-seed runs.
**Implementation:**
- Run 3–5 independent seeds per model with identical configs (only `random_seed` differs)
- Project all elites into a shared embedding space and test whether motifs cluster significantly above null
- Compute inter-seed motif overlap using hypergeometric enrichment tests
- Thresholds: Cohen's κ > 0.65 for motif classification agreement; statistical power > 0.80
- Cross-reference with Anti-Aethon control (item 8): if anti-aethon runs also converge on the same motifs, the convergence is an artifact of the search space, not the fitness landscape
- Output: per-model convergence report with motif frequency tables, cluster visualizations, and enrichment p-values
**Complexity:** Medium — analysis pipeline on existing archive data
**Dependencies:** Null baselines (COMPLETE), 3+ completed seeds per model (Llama: COMPLETE, Qwen: in progress)
**Status:** Active — currently executing as Phase 3 replication study (4 seeds × 2 models).

### 7. Multiple Embedding Families
**Source:** Perplexity
**Rationale:** Selecting for novelty in one embedding space risks "Goodharting your aethon" — evolving outputs that are maximally weird for that specific representation, not intrinsically interesting. Joint surprise across qualitatively different representations is a stronger signal.
**Implementation:**
- Add a code-specialized embedding model alongside current all-MiniLM-L6-v2
- Add a syntactic/structural embedding (parse-tree based or a different model family)
- Require anomalies to be "jointly surprising" across at least 2 of 3 representations
- Anomalies that vanish under a different representation are tagged as "representation artifacts"
- Periodically swap or ensemble embeddings every N generations
**Complexity:** Medium — new embedding models, updated fitness computation
**Dependencies:** Current embedding infrastructure in fitness.py

### 8. Adversarial "Anti-Aethon" Control Experiments
**Source:** Perplexity
**Rationale:** Evolve explicitly *against* emergence — penalize transferability and reproducibility, promote input-specific weirdness. This provides a negative control: what patterns characterize a search pushed toward brittle, non-general anomalies? Comparing against default settings helps distinguish "quirky overfit behavior" from "something systemically new." A natural complement to Basin Convergence testing (item 6): if both normal and anti-aethon runs converge on the same motifs, the convergence is a search-space artifact, not a fitness-landscape property.
**Implementation:**
- Create `configs/experiments/anti_aethon.yaml` with inverted fitness: reward low transfer scores and low reproducibility
- Run through identical analysis pipeline
- Compare characterization profile distributions between normal and anti-aethon runs
**Complexity:** Low — config and fitness weight changes
**Dependencies:** Working characterization battery

### 9. Benchmark & Task Selection
**Source:** DeepSeek (gap G7), synthesis
**Rationale:** No document currently specifies which tasks AETHON should optimize for. Without a defined task set, the competence gate (P0 item 5) and the fitness function lack grounding. The prompt library infrastructure exists, but task selection criteria and difficulty grading have not been formalized. This is a prerequisite for meaningful competence-gating.
**Implementation:**
- Define a minimum benchmark suite (10–20 tasks spanning reasoning, creativity, factual accuracy, and cross-domain transfer)
- Grade tasks by difficulty tier and domain coverage
- Use benchmark performance as the competence floor for the novelty gate
- Periodically rotate or expand the task set to prevent overfitting to a fixed evaluation surface
- Document task provenance and selection rationale for reproducibility
**Complexity:** Medium — task curation and evaluation infrastructure
**Dependencies:** Prompt library infrastructure (already built)

### 10. Specimen Freezer and Borderline Sampling
**Source:** Perplexity, DeepSeek
**Rationale:** Current system only characterizes anomalies above threshold. Mutations may destroy fragile but interesting configurations before they can be probed. Borderline anomalies just below threshold may be the most informative.
**Implementation:**
- Add "specimen freezer" to evolution_v2.py: when anomaly fires, temporarily exempt genome from mutation for N characterization runs before re-entry
- Periodically force-sample and characterize anomalies scoring 80-100% of threshold
- Archive all near-misses with metadata for later analysis with better detectors
**Complexity:** Medium — evolution loop modification
**Dependencies:** Working anomaly detection (already built)

### 11. Cross-Model Coherence Checking
**Source:** Perplexity
**Rationale:** Current coherence metrics are shallow (n-gram repetition, vocab diversity, sentence length). A clever configuration could game these while remaining meaningless. Running candidate outputs through a separate judge model adds a robust coherence gate.
**Implementation:**
- Add a `judge_coherence(output_text, judge_model)` function that sends output to a different Ollama model with a "is this coherent and meaningful reasoning?" prompt
- Integrate as an optional coherence check in the characterization battery
- Also add input perturbation consistency: slight paraphrases of the input shouldn't completely scramble behavior if something structured is happening
**Complexity:** Medium — new evaluation function, additional Ollama calls
**Dependencies:** Second model available in Ollama (already have Llama alongside Qwen)

### 12. Phase-Space Mapping + Phase-Transition Instrumentation
**Source:** Copilot (phase-space mapping), GPT-5.4, Grok, DeepSeek (phase-transition logging)
**Rationale:** Systematically sweep genome parameters (length, temperature, module composition, iteration count) to map where "interesting" behaviors concentrate. Treat cognition as a phase diagram. This produces publishable visualizations and identifies the parameter regions worth exploring more deeply. To make phase diagrams measurable rather than decorative, instrument the evolutionary loop with explicit phase-transition event logging: discrete emergence events such as reflection loops appearing, tool-use loops stabilizing, role specialization emerging, and meta-control transitions.
**Implementation:**
- Build a parameter sweep runner that varies one dimension at a time across a grid
- For each point: run a short evolution (50 gen), measure archive coverage, diversity, and anomaly rate
- Generate heatmap visualizations showing "interesting behavior density" across parameter space
- Define a phase-transition event schema (event type, generation, genome snapshot, fitness delta, behavioral descriptor shift)
- Log discrete transitions: first appearance of a motif, motif fixation in population, motif loss, coverage plateau breaks
- Attach event metadata to lineage records for post-hoc phase boundary identification
**Complexity:** Medium — new runner, visualization, and event logging infrastructure
**Dependencies:** Batch runner (already built), dashboard SVG generation (already built), archive metadata (item 16)

### 13. Human-in-the-Loop Anomaly Triage
**Source:** Copilot, Perplexity, DeepSeek
**Rationale:** Even with automation, the anomaly pool will be noisy. A lightweight human triage step (tagging anomalies as "boring / structurally interesting / philosophically interesting") creates labeled data for training better anomaly ranking models and avoids burning cycles on dull cases.
**Implementation:**
- Build a simple web UI or CLI that presents anomalies one at a time with the characterization report, prompt chain, and output
- Human tags each with a 1-5 rating on interest and a free-text note
- Store ratings alongside anomaly data
- Even 100-200 human-rated cases would be highly informative for tuning detection thresholds
**Complexity:** Low-Medium
**Dependencies:** Captured anomalies from MVP-2 runs

### 14. Cross-Substrate Transfer Testing — **COMPLETE** (March 10, 2026)
**Source:** Grok
**Status:** Built `src/aethon/transfer.py` with `cross_substrate_test()`, `batch_transfer_test()`, CLI entry point. Tests passing.
**Remaining:** Run against completed Qwen and Llama archives.

### 15. Reasoning Trace Embedding — **COMPLETE** (March 10, 2026)
**Source:** Grok (primary), Perplexity (multi-level anomaly descriptions)
**Status:** Built into `execution.py` (reasoning_trace field), `fitness.py` (compute_trace_novelty, archive trace storage), `config.py` (trace_novelty_weight), both evolution CLIs. 12 new tests passing.
**Remaining:** Run experiment with `configs/experiments/trace_novelty.yaml` to test impact on archive diversity.

### 16. Fossil Analysis Pipeline + Archive Contract — `src/aethon/fossil.py`
**Source:** Grok (Round 2 — strategic research framing), DeepSeek (archive schema), synthesis
**Rationale:** The MAP-Elites archive across multiple runs and substrates is a computational fossil record. No existing QD-over-LLMs work performs deep multi-run, multi-substrate structural analysis of genomes and evolutionary dynamics. This module turns raw archives into the core figures for a paper. **The archive format is a first-class research artifact** — not a byproduct of runs, but a primary scientific output. Lineage capture is mandatory, and cross-run export compatibility is part of the deliverable, not an afterthought. Five analyses that produce publishable findings no other system can match:
1. **Convergent evolution signatures** — cluster behavioral cells across substrates, compute genome edit distance for shared cells, measure fraction reached by homologous vs analogous genomes
2. **Recurrent cognitive motifs** — mine frequent sub-sequences in elite genomes, rank by persistence across runs and substrates, compare against null baselines with permutation tests
3. **Phylogenetic lineage reconstruction** — build mutation/crossover trees per run, compute branching factor at novelty spikes, identify "speciation events" when lineages jump behavioral cells
4. **Landscape topography** — coverage growth curves (power-law vs logistic fit), ruggedness metrics, neutral network analysis, cross-substrate alignment via optimal transport distance
5. **Modularity & non-decomposability quantification** — correlate ablation resilience with motif presence, identify super-additive composite motifs
**Archive Contract — Mandatory Fields:**
- `genome`: full module chain with parameters (conforming to Genome v1 schema, P0 item 5)
- `lineage`: parent genome IDs, mutation/crossover provenance, generation born
- `descriptors`: behavioral descriptor vector (output length, vocab diversity, + extended descriptors per item 17)
- `fitness`: composite fitness score and component breakdown
- `trace_embedding`: reasoning trace vector
- `ablation_scores`: per-module ablation resilience scores (when available)
- `substrate_id`: model name and version
- `run_id`: experiment config hash + random seed
- `generation`: generation number within the run
- `output_text`: full LLM output for reproducibility
- `timestamp`: ISO 8601 creation time
**Implementation:**
- Unified dataframe across all archives using the mandatory field schema above
- NetworkX or SQLite for lineage graph storage
- N-gram and gSpan motif mining on linearized genomes
- Sequence alignment (Levenshtein edit distance) for genome comparison
- HTML report with coverage maps, motif clouds, lineage trees, statistical tables
- Cross-run export: `python -m aethon.fossil --export --archive-dir archive/ --format parquet`
- CLI: `python -m aethon.fossil --archive-dir archive/ --output reports/fossil_report.html`
**Complexity:** High — significant analysis module, but builds on existing archive infrastructure
**Dependencies:** Multiple completed runs across substrates (Qwen + Llama archives, null baselines), Genome v1 schema (P0 item 5)

### 17. Improved Behavioral Descriptors
**Source:** Gemini (Round 2 — QD methodology expertise)
**Rationale:** Current MAP-Elites dimensions (output length, vocabulary diversity) are shallow proxies that capture text shape, not reasoning topology. Three upgrades from QD literature:
1. **Unsupervised latent descriptors (AURORA approach)** — run PCA on archive embeddings, use top 2 principal components as grid axes. Grid automatically expands along dimensions of maximum actual behavioral difference.
2. **Reasoning Delta** — cosine distance between trace embedding and output embedding. Separates configurations that genuinely deliberate (high delta) from those that confabulate post-hoc justification (low delta). Infrastructure already exists from trace embedding build.
3. **Epistemic complexity** — ratio of hedging/probabilistic language, discourse tree depth. Separates dogmatic from nuanced reasoning chains.
**Implementation:**
- Add `compute_reasoning_delta(trace_embedding, output_embedding) -> float` to fitness.py
- Add PCA-based descriptor computation to archive.py (periodic recomputation as archive grows)
- Add epistemic complexity scorer to fitness.py using keyword matching + sentence structure analysis
- Make behavioral descriptors pluggable (already partially supported via descriptor_extractors parameter)
**Complexity:** Medium
**Dependencies:** Trace embedding (complete), existing archive infrastructure

### 18. Genome Motif Mining
**Source:** Grok (Round 2), Gemini (Round 2 — sequence alignment methodology)
**Rationale:** Treat evolved genomes as sequences (analogous to DNA) and mine for recurrent sub-patterns. If the same 2-3 gene motifs dominate elites across both Qwen and Llama runs, that's substrate-independent convergent evolution — a publishable finding. Gemini recommends TF-IDF for overrepresentation scoring and Levenshtein edit distance for structural similarity. Grok recommends permutation tests against null baselines.
**Implementation:**
- Extract all 2-gene and 3-gene sub-sequences from elite genomes
- Compute TF-IDF scores: motif frequency in elites vs frequency in initial random populations
- Compare motif frequency across substrates (Qwen vs Llama) and against null baselines
- Permutation test for statistical significance
- Needleman-Wunsch sequence alignment for genome-to-genome structural comparison
- CLI: `python -m aethon.fossil --motifs --archive-dir archive/` (part of fossil.py or standalone)
**Complexity:** Medium
**Dependencies:** Completed Qwen + Llama archives (have these), null baseline data (running overnight)

---

## P2 — Promising Extensions

### 19. Interpretive Guardrails: Unknown Primitives + Biological Comparison
**Source:** GPT-5.4, Claude, DeepSeek, Grok
**Rationale:** Two related risks require explicit guardrails. First, anomalous architectures may resist current decomposition into the 10-module vocabulary — flagging them as "candidate unknown primitives" preserves discovery potential without inflating the ontology too early. Second, biological/animal resemblance (e.g., "this looks like hippocampal replay") can be a useful diagnostic lens but must not become a fitness target, as that would steer AETHON toward anthropocentric rediscovery rather than genuinely novel structures.
**Implementation:**
- Add a "decomposition confidence" score to characterization: how well does the current module vocabulary explain this elite's behavior?
- Elites with low decomposition confidence are flagged as "candidate unknown primitive" and queued for multi-lens review (multiple embedding families, human triage)
- Provisional status only — promotion to a new named primitive requires survival across seeds, substrates, and decomposition schemes
- Biological comparison annotations are permitted in analysis reports but are explicitly excluded from fitness computation or selection pressure
- Add a standing guardrail to the interpretive discipline statement (P0 item 4): "Resemblance to biological cognitive structures is noted for analysis but never rewarded."
**Complexity:** Low-Medium — annotation infrastructure and review protocol
**Dependencies:** Multiple decomposition schemes (item 7: Multiple Embedding Families), human triage (item 13)

### 20. Meta-Evolution of Reward Functions
**Source:** DeepSeek (primary), Copilot
**Rationale:** Currently evolving genomes against fixed novelty + coherence weights. But what if the reward function itself evolved? Let the system discover what's worth optimizing. Start with a population of reward functions (weight vectors over novelty, coherence, transferability, reproducibility) and evolve them alongside genomes. This could unlock behaviors that current fixed rewards miss and is philosophically aligned with the project's core insight about recasting error and reward.
**Implementation:**
- Define a "reward genome" encoding weight vectors over available fitness components
- Outer evolutionary loop evolves reward functions; inner loop evolves reasoning genomes under each reward function
- Meta-fitness of a reward function = quality/diversity of genomes it produces
**Complexity:** High — nested evolutionary loops, significant architectural addition
**Dependencies:** Stable MVP-2 with characterization data to inform meta-fitness definition

### 21. Multi-Level Anomaly Descriptions
**Source:** Perplexity
**Rationale:** Current anomalies are defined at input → output embedding level. But emergent structure might live in intra-trace patterns (stable reasoning "voice" across tasks) or genome dynamics over generations (attractors in module-composition space).
**Implementation:**
- Add "reasoning-style embedding" of the full trace (not just final answer) — embed the intermediate reasoning steps
- Add dynamical analysis over genome space: do runs converge to a small set of structural motifs?
- Track "genome family trees" and identify recurring evolutionary attractors
**Complexity:** Medium-High
**Dependencies:** Sufficient run data to analyze genome dynamics (multiple completed experiments)
**Note:** Partially addressed by P1 Item 15 (Reasoning Trace Embedding). This item covers the broader dynamical analysis component.

### 22. Parallel Evaluation
**Source:** DeepSeek, Meta AI
**Rationale:** Current evaluation is sequential. With multiple Ollama instances or async calls, runtime could be cut dramatically.
**Implementation:**
- Add async evaluation mode to evolution.py and evolution_v2.py using asyncio
- Support multiple Ollama instances on different ports
- Batch evaluations across available instances
**Complexity:** Medium — async refactor of evaluation pipeline
**Dependencies:** Hardware capable of running multiple model instances (or cloud GPU access)
**Note:** Partially addressed by the Redis Streams distributed evaluation architecture (designed, not yet built). This item covers additional within-machine parallelism.

### 23. Surrogate Modeling for Fast Screening
**Source:** DeepSeek
**Rationale:** Train a fast surrogate model to predict novelty scores from genome descriptors alone, without running the LLM. Use for most evaluations, only running real LLM evaluations for promising candidates or periodic validation. Dramatically reduces compute cost.
**Implementation:**
- Train surrogate on accumulated (genome_descriptor → fitness) data
- Use surrogate for initial screening, LLM for top-k candidates per generation
- Periodically retrain surrogate as archive grows
**Complexity:** Medium
**Dependencies:** Sufficient training data from completed runs

### 24. Practical Application: Anomaly Detection in Real Data
**Source:** Meta AI, DeepSeek
**Rationale:** AETHON's architecture — evolving detectors that maximize surprise against a baseline — could be repurposed for network intrusion detection, fraud detection, or scientific anomaly discovery. This provides a practical funding angle alongside the theoretical research.
**Implementation:**
- Adapt the evolutionary pipeline to work with structured data rather than text
- Define domain-specific behavioral descriptors
- Build a demonstration on a public dataset (e.g., CICIDS network intrusion dataset)
**Complexity:** High — significant adaptation of pipeline
**Dependencies:** Core platform stable (already is)

### 25. Aethon as a Creativity Engine
**Source:** Meta AI
**Rationale:** Instead of (or in addition to) looking for emergence, point AETHON at creative domains. Evolve reasoning stacks rewarded for generating novel scientific hypotheses, mathematical conjectures, or artistic styles. The behavioral archive becomes a library of unexplored creative processes.
**Implementation:**
- Add domain-specific prompt libraries for scientific and creative tasks
- Define creativity-relevant behavioral descriptors
- Evaluate outputs with domain-specific judges
**Complexity:** Medium
**Dependencies:** Prompt library infrastructure (already built)

---

## Cross-Project Integration: Project Prometheus

**Status:** Planning phase. No code integration yet. Both projects to be kept mutually informed with shared taxonomy and cross-validation discussed as findings mature.

**Background:** Project Prometheus (the Sovereign Harvest Engine) is a sister project that uses genetic algorithms to evolve prompt strategies, runs them against frontier AI models on coding tasks, and harvests the reasoning patterns behind every successful response. It currently has 13 prompt strategies spanning 7 reasoning topologies (linear, tree, graph, loop, parallel, constrained, inverted), tested across 23 coding tasks on multiple models. Where AETHON evolves reasoning module sequences bottom-up and measures what emerges, Prometheus asks models to reason under different structural constraints top-down and harvests what patterns recur. They are exploring conjugate faces of the same phenomenon.

**Critical observation:** AETHON's convergent motifs (metacognitive_reflection → devils_advocate, chain_of_thought → step_by_step_verification) map directly onto Prometheus's prompt-level reasoning topologies. If Prometheus independently finds that the same functional patterns produce the richest reasoning traces on frontier models — without evolutionary pressure pushing them there — that constitutes convergent evidence from a completely different methodology, different models, different tasks, and different selection mechanisms.

### Integration 1: Shared Taxonomy (Priority: High, Timing: This week)
**What:** Tag Prometheus's harvested reasoning traces with AETHON's 10-module vocabulary. Each reasoning step gets classified as chain_of_thought, socratic_questioning, metacognitive_reflection, etc. Creates a common ontology across both projects.
**Why:** Lets us ask: do frontier models naturally decompose their reasoning into the same module sequences AETHON's evolution converges on? If yes, that's independent confirmation from a completely different methodology.
**Complexity:** Low — labeling exercise on existing Prometheus data, no new experiments needed.
**Dependencies:** None. Can proceed immediately as an analysis pass.
**Near-term milestone (Phase 3):** Once the Qwen 4-seed series completes, apply Prometheus's taxonomy classifier (already demonstrated on qwen_seed2) to all 8 completed archives (4 Llama, 4 Qwen). Compare Prometheus's module distribution profiles against AETHON's internal genome descriptions to test inter-instrument agreement — does an independent classifier see the same convergent motifs AETHON's evolution reports?

### Integration 2: Reasoning Delta in Prometheus (Priority: Medium, Timing: After AETHON Phase 3)
**What:** Add AETHON's reasoning delta metric (cosine distance between trace embedding and output embedding) to Prometheus's extraction pipeline.
**Why:** High-delta Prometheus harvests — where the model's stated reasoning diverges from its actual output — become pre-identified candidates for AETHON's characterization battery. Prometheus becomes a directed scout, saving AETHON enormous evolutionary search time.
**Complexity:** Low — one additional embedding computation per Prometheus harvest.
**Dependencies:** AETHON's trace embedding infrastructure (complete). Should wait until after AETHON's null baseline calibration so the delta metric is validated.

### Integration 3: Temporal Drift Detection (Priority: Parked)
**What:** Run Prometheus's full strategy × task matrix periodically against the same frontier model to detect provider-side model changes.
**Why:** Changes in which strategies succeed on which tasks over time would reveal when providers modify internal reasoning layers — architectural changes never publicly announced. Prometheus becomes a tomographic probe of proprietary model internals.
**Complexity:** Medium — scheduling and comparison infrastructure.
**Status:** Parked. Fascinating but a separate research program. Potentially commercially valuable (model change detection as a service) but doesn't advance AETHON's current goals. Revisit after Phase 4.

### Integration 4: Warm-Starting AETHON from Prometheus (Priority: High, Timing: After AETHON Phase 4)
**What:** Feed Prometheus's empirically top-performing reasoning topologies into AETHON as seed genomes rather than random initialization.
**Why:** If warm-started evolution converges on the same motifs faster, that confirms the motifs are genuine attractors. If warm-starting unlocks new archive regions random initialization never reaches, the landscape has multiple basins requiring directed exploration. Either result is publishable.
**Critical constraint:** Must wait until unseeded AETHON results are fully established (Phase 4 complete, multi-seed replication done). Seeding the population before then would compromise AETHON's claim that evolution discovers structures without human guidance — evolved motifs might be descendants of seeds rather than independent discoveries.

### Cross-Validation Value
The existence of two independent instruments strengthens both projects. AETHON provides evolutionary evidence (bottom-up discovery). Prometheus provides evaluative evidence (top-down confirmation). If both converge on the same reasoning structures, the probability of coincidence drops dramatically. This dual-instrument narrative strengthens funding applications: not one tool, but a research program with complementary validation.

---

## P3 — Long Horizon

### 26. Cognitive Primitive Decomposition
**Source:** Meta AI (primary), DeepSeek
**Rationale:** Current genome elements are high-level (chain-of-thought, self-critique). Evolution might work better with lower-level cognitive primitives: attention gating, working memory read/write, inhibition, pattern completion, associative recall. This lets evolution compose truly alien cognitive architectures from fine-grained building blocks rather than recombining human-designed modules.
**Implementation:**
- Design a new primitive-level genome representation
- Build primitive-to-prompt rendering system
- Potentially requires architectural changes beyond prompt-level evolution (actual model modifications)
**Complexity:** Very High — fundamental redesign of genome representation
**Dependencies:** Results from current module-level experiments to justify the investment

### 27. Co-Evolving Environments
**Source:** Meta AI, DeepSeek
**Rationale:** In biology, organisms and environments co-evolve. Currently the environment (prompt library) is fixed. Genomes that could propose new prompts or modify evaluation conditions would create an arms race driving open-ended complexity — how many artificial life systems achieve unbounded evolution.
**Implementation:**
- Add "environment genes" that modify prompt selection, difficulty, or domain
- Co-evolutionary loop where environment fitness = ability to differentiate genome performance
**Complexity:** Very High
**Dependencies:** Stable results from fixed-environment experiments

### 28. The Cognitive Fossil Record
**Source:** DeepSeek, Grok
**Rationale:** Over many runs, the MAP-Elites archive becomes a dataset of evolved cognitive strategies. Cluster into families, trace evolutionary lineages, identify recurring structural motifs, look for attractors in genome space. Computational paleontology: studying the fossil record of artificial minds. Grok's framing: the archive is already the most valuable artifact the project will produce, even if no "aethon" ever appears.
**Implementation:**
- Build cross-run archive aggregation tools
- Implement clustering over genome descriptors and behavioral features
- Lineage tracking across generations
- Attractor identification in genome space
**Complexity:** Medium-High
**Dependencies:** Multiple completed experimental runs with full genealogy data

### 29. Meta-Predictor Evolution
**Source:** Grok
**Rationale:** Let a second evolutionary loop mutate the anomaly detector's architecture itself — embedding family, predictor type, surprise metric. Genomes that survive against an evolving detector are robustly surprising rather than exploiting a specific measurement instrument. This is the computational version of "the map is not the territory." However, this requires nested evolutionary loops (outer: evolve predictors, middle: evolve rewards, inner: evolve genomes), making compute cost multiplicative. More importantly, you can't meaningfully evolve the predictor until you know what a good predictor looks like, and you don't know that until you've run the predictor capacity ladder against real anomaly data with calibrated instruments. Each layer of knowledge is a prerequisite for the next.
**Implementation:**
- Define a "predictor genome" encoding embedding family, predictor architecture, surprise metric, and threshold
- Outer evolutionary loop over predictor configurations
- Inner loop runs standard genome evolution under each predictor configuration
- Meta-fitness = robustness of anomaly detection (anomalies that persist across predictor variants score higher)
**Complexity:** Very High — nested evolutionary loops, multiplicative compute cost
**Dependencies:** Completed predictor capacity ladder (P0 Item 2), calibrated instruments from Phase 3, substantial compute budget. This is a Phase 6+ item that becomes tractable only after the science of the earlier phases is settled.

### 30. EvoTune-Style RL Consolidation ("Computational Dreaming")
**Source:** Grok, Gemini (Dreams-as-GA exploration), Surina et al. 2025 (arXiv:2504.05108)
**Rationale:** Currently AETHON archives evolved reasoning configurations but the base LLM remains static — it never "learns" from what evolution discovers. EvoTune-style consolidation periodically fine-tunes the base model on high-fitness genomes using DPO (Direct Preference Optimization), so the model internalizes the discovered reasoning patterns. After consolidation, the model should produce the convergent motifs spontaneously without genome prompting — analogous to a brain consolidating dream insights into default waking cognition. The EvoTune paper (Surina et al.) proves this works: forward-KL regularized DPO preserved diversity while improving performance on FunSearch-style tasks.
**Implementation:**
- `src/aethon/consolidation.py` with `build_dpo_dataset(archive)` creating preference pairs (winners = top 10% by novelty + delta + transfer, losers = random from same cell)
- Lightweight LoRA-based DPO fine-tuning on the base model (feasible on 16GB GPU for 7-8B models in 8-bit)
- Forward-KL regularization (β ≈ 0.5-0.8) to prevent mode collapse
- Consolidation every N generations (e.g., 50) or at coverage thresholds
- Post-consolidation test: does the model produce the three convergent motifs spontaneously in normal prompting?
**Key falsifiable prediction:** If consolidation works, the fine-tuned model's natural reasoning traces should show the metacognitive motifs at rates significantly above the pre-consolidation baseline (currently ~0.04% in Prometheus data). If the motifs don't appear spontaneously post-consolidation, the consolidation mechanism isn't capturing what evolution discovered.
**Complexity:** High — requires LoRA/PEFT fine-tuning infrastructure, preference pair construction, careful diversity monitoring
**Dependencies:** Validated motifs from multi-seed replication (Phase 4 complete), sufficient archive data for meaningful preference pairs, GPU compute for fine-tuning. This is Phase 6 work. Do not attempt before Phase 4 replication confirms the motifs are real.
**Risk:** Mode collapse (model loses generative diversity). Mitigated by forward-KL regularization and MAP-Elites diversity archive for sampling. Also risk of "false epiphany" — consolidating noise into the model's weights. Mitigated by only consolidating genomes that pass the full characterization battery.

### 31. PromptBreeder-Style Self-Referential Meta-Evolution
**Source:** Grok, Fernando et al. 2023 (ICML)
**Rationale:** Currently AETHON's mutation operators are fixed (add module, remove module, swap, perturb parameters). PromptBreeder evolves the mutation operators themselves alongside the genomes — a meta-genome layer where the system learns *how* to mutate more effectively. This is the deepest computational analog to the dreams-as-GA hypothesis: not just dreaming up new reasoning strategies, but evolving the dreaming process itself.
**Implementation:**
- Add `mutator_archive` alongside `task_archive` — a separate MAP-Elites archive of mutation strategy genomes
- Each mutator genome encodes rules like "always insert reflection after verification" or "prefer swapping adjacent modules over distant ones"
- Normal evolution uses sampled mutators instead of fixed operators
- Meta-evolution step (every N generations): evaluate which mutators produced the most novel/transferable genomes, breed new mutators from the best
- Two parallel archives to analyze: what reasoning strategies evolve, and what evolutionary strategies evolve to produce them
**Complexity:** Very High — dual-archive system, meta-fitness evaluation, potential for runaway complexity
**Dependencies:** Stable EvoTune consolidation loop (Item 30), validated motif findings (Phase 4), substantial compute. This is Phase 7 at earliest. The current fixed mutation operators are adequate for the discovery phase — meta-evolution only adds value after the basic landscape is mapped.

### 32. Dreams-as-GA In-Silico Modeling Framework
**Source:** Internal (James's insight), Copilot, Gemini, Grok
**Rationale:** The observation that biological dreaming functions as a genetic algorithm over cognitive representations — with REM as variation, emotional salience as fitness, and consolidation as selection — maps directly onto AETHON's architecture. A formal in-silico modeling framework would test this analogy computationally: does an AETHON system with EvoTune consolidation cycles exhibit the same structural properties as human offline cognition (iterative improvement across cycles, motif emergence, transfer to novel tasks)?
**Implementation:**
- Define the formal mapping: REM = evolutionary search, Consolidation = DPO fine-tuning, Emotional salience = composite fitness, Waking baseline = post-consolidation performance
- Run multi-cycle experiments: evolution → consolidation → evolution → consolidation (each cycle = one "night")
- Measure: do motifs emerge faster in later cycles? Does transfer improve? Does the model's default reasoning become progressively more structured?
- Compare cycle dynamics to known sleep-stage properties (progressive deepening, REM rebound, etc.)
**Falsifiable predictions:** (1) Motif frequency in post-consolidation model increases monotonically across cycles. (2) Genomes evolved in later cycles show higher initial fitness than those in earlier cycles. (3) The system exhibits "mode collapse" if consolidation is too aggressive — analogous to cognitive rigidity from sleep deprivation.
**Complexity:** Very High — requires EvoTune infrastructure, multi-cycle orchestration, careful experimental design
**Dependencies:** EvoTune consolidation (Item 30) working and validated. This is the capstone experiment of the entire research program. Phase 7+.
**Funding note:** This framework, if formalized with falsifiable predictions and pilot data from the EvoTune experiments, could be the basis for a standalone grant proposal bridging AI research and computational cognitive science.

---

## Parked

### Safety Containment and Red-Teaming
**Source:** Copilot, Perplexity, DeepSeek
**Rationale:** Important in principle, but at current scale (prompt configurations for 7B models on a laptop), the risk surface is minimal. The system generates text through standard Ollama inference — it can't modify itself, access the internet, or take actions. Worth revisiting if the project scales to larger models or architectural modifications beyond prompt-level evolution.
**Status:** Acknowledged in documentation. Will implement containment measures when scale warrants it.

### Evolving Reward Functions with Full RL
**Source:** Various
**Rationale:** Full reinforcement learning over reward function space is theoretically elegant but computationally prohibitive at current scale. The meta-evolution approach (P2, item 20) captures the core idea at lower cost.
**Status:** Subsumed by meta-evolution of reward functions (item 20).

### Variable-Length Genomes and Primitive-Level Redesign
**Source:** DeepSeek, current P3 items (26, 27)
**Rationale:** Deeper primitive-level redesign (sub-module cognitive operations) and variable-length genomes (allowing evolution to grow or shrink chain length freely) are theoretically attractive but premature. The current fixed-length, module-level genome is adequate for the discovery phase and has already produced replicable convergent motifs. Promoting variable-length genomes before Genome v1 (P0 item 5) and basin convergence testing (P1 item 6) are complete would add complexity without evidence that the current representation is actually limiting discovery.
**Status:** Parked. Revisit only after evidence emerges that fixed-length Genome v1 is constraining the search space (e.g., coverage plateaus despite parameter tuning, motif analysis shows truncation artifacts).

---

## Cross-Cutting Themes from Reviews

Several themes emerged independently across multiple reviewers and are worth noting as guiding principles:

1. **Baselines before claims.** Every reviewer emphasized controlled nulls. No finding is meaningful without a baseline to compare against. (All seven reviewers)

2. **Instrument calibration.** The pipeline itself needs validation — synthetic ground truth, multiple predictor families, multiple embedding spaces. The detector must be trustworthy before its detections are. (Perplexity, DeepSeek, Grok)

3. **Interpretive restraint.** "Interesting computation" ≠ "consciousness." Maintain strict language in all documentation. The value of AETHON is methodological (a new way to search for and characterize unexpected behaviors), not metaphysical. (All seven reviewers)

4. **The human remains essential.** Automated detection is necessary but not sufficient. Human triage, expert review, and judgment calls about what's "interesting" remain irreplaceable — at least until the instruments are calibrated against human-validated ground truth. (Copilot, Perplexity, DeepSeek)

5. **Practical applications strengthen the case.** Funders and collaborators respond to dual-use potential. The same architecture that searches for emergent cognition can detect anomalies in security data, generate creative hypotheses, or discover novel problem-solving strategies. (Meta AI, DeepSeek)

6. **The archive is the product.** Even if no "aethon" ever appears, the MAP-Elites archive of evolved reasoning configurations is a novel dataset. The cognitive fossil record — catalogued by behavioral phenotype, traceable by lineage, comparable across substrates — has independent value for prompt engineering research, reasoning architecture design, and computational cognitive science. (Grok, DeepSeek)

7. **Walk before you run.** Each layer of scientific knowledge is a prerequisite for the next. Null baselines before anomaly claims. Predictor calibration before meta-predictor evolution. Prompt-level results before activation-level experiments. The phased approach isn't just practical caution — it's the epistemically correct order of operations. Skipping ahead produces results you can't interpret. (Internal)

8. **Modest success is still revolutionary.** Even the "small" version of success — discovering stable, self-organizing computational patterns in evolved reasoning configurations, motifs that transfer across models and resist decomposition — would be a significant contribution. Nobody has systematically mapped the space of possible reasoning architectures using evolutionary search with novelty selection. A well-characterized negative result ("we searched exhaustively and here's what the space actually looks like") is also publishable and valuable. The bar for meaningful contribution is lower than the bar for "emergence." (Internal)

9. **Competence before novelty.** Novelty search without a performance floor produces maximally weird but functionally meaningless configurations. Every novelty-driven selection step should be gated on minimum competence. This principle applies at every scale: genome selection (competence gate), motif claims (replication gate), and interpretive claims (multi-lens gate). (Claude, GPT-5.4, Grok, DeepSeek)

10. **Sharpen, don't replace.** The document already covers the right themes. The correct move is to elevate missing backbone items, tighten existing items into clearer experiments, and explicitly park glamorous ideas until infrastructure exists. Resist the temptation to add complexity for its own sake. (Frontier model consensus, March 2026)

---

*This is a living document. Update as experiments produce results, new ideas emerge, and priorities shift.*
