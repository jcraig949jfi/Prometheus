# Apollo Development Journal

---

## 2026-03-26 — Session 1: Design Review & Open-Source Landscape Scan

### Activity
- Read and analyzed `apollo_design.md` in full
- Examined 146 forge tools in `agents/hephaestus/forge/` to understand the gene substrate
- Read representative tools (`active_inference_x_epistemology_x_network_science.py`, `bayesian_inference_x_free_energy_principle_x_sensitivity_analysis.py`) to map the actual code structure to the genome abstraction
- Launched parallel GitHub/web searches for evolutionary computation, quality-diversity, program synthesis, and sandboxing frameworks
- Reviewed existing `reference_toolkits.md` (EvoTorch already flagged as high-value)

### Key Observations from Forge Tool Analysis
- All 146 tools follow identical interface: `ReasoningTool` class with `evaluate(prompt, candidates) -> list[dict]` and `confidence(prompt, answer) -> float`
- Common gene patterns identified: NCD computation, number extraction, negation detection, coherence checking, sigmoid mapping, factor graph construction, variational inference loops
- Tools use only numpy + stdlib (zlib, re, collections, math) — confirms sandbox whitelist is viable
- Typical tool is 100-200 lines, 4-8 methods — gene extraction should yield 4-8 fragments per tool

### Design Review: Questions & Suggestions
*(See main conversation for full discussion)*

### Open-Source Landscape Scan — Results

Scanned GitHub for evolutionary computation, quality-diversity, program synthesis, AST manipulation, and sandboxing frameworks. Organized by function with Apollo-specific relevance notes.

#### Evolutionary Computation Frameworks
| Project | Stars | License | Apollo Role |
|---------|-------|---------|-------------|
| **DEAP** (github.com/DEAP/deap) | ~6.4k | LGPL-3.0 | Battle-tested GP framework. Tree GP, toolbox/creator pattern, built-in NSGA-II, multiprocessing. Core infrastructure candidate. |
| **pymoo** (github.com/anyoptimization/pymoo) | ~2.8k | Apache-2.0 | Best-in-class multi-objective optimization. **NSGA-III reference implementation**, co-developed with Kalyanmoy Deb. This is Apollo's selection engine. |
| **EvoTorch** (github.com/nnaisense/evotorch) | ~1.1k | Apache-2.0 | GPU-accelerated CMA-ES + GA with NSGA-II. Already in our reference_toolkits. Relevant if fitness eval becomes GPU-bound. |
| **geppy** (github.com/ShuhuaGao/geppy) | ~218 | LGPL-3.0 | Gene Expression Programming on DEAP. **Linear chromosomes encoding expression trees** — very close match to Apollo's gene-fragment concept. Strong candidate for genome representation. |
| **EvoGP** (github.com/EMI-Group/evogp) | ~259 | GPL-3.0 | GPU-accelerated tree GP with CUDA kernels. 140x speedup. Tensorized tree representation could represent pipeline DAGs. (GPL license is restrictive.) |
| **LEAP** (github.com/AureumChaos/LEAP) | ~102 | AFL | **Island model migrations** + coevolution support built-in. Directly relevant for parallel sub-populations. |
| **PyPop7** (github.com/Evolutionary-Intelligence/pypop) | ~279 | MIT | **Cooperative coevolution** — evolve different pipeline components in separate populations. Published in JMLR. |
| **EC-KitY** (github.com/EC-KitY/EC-KitY) | ~102 | BSD-3 | Typed GP support — could enforce gene fragment type compatibility at the representation level. |
| **PyGAD** (github.com/ahmedfgad/GeneticAlgorithmPython) | ~2.2k | BSD-3 | Simpler GA alternative. Good for rapid prototyping before committing to DEAP/pymoo. |

#### Program Synthesis / Code Evolution
| Project | Stars | License | Apollo Role |
|---------|-------|---------|-------------|
| **OpenEvolve** (github.com/algorithmicsuperintelligence/openevolve) | ~5.8k | MIT | Open-source AlphaEvolve. **Island-based evolution + MAP-Elites + program database**. Closest existing system to Apollo. Reference architecture. |
| **OpenELM** (github.com/CarperAI/OpenELM) | ~738 | MIT | Pioneer of LLM-driven evolution. MAP-Elites + gVisor sandboxing. Less actively maintained. |
| **CodeEvolve** (github.com/inter-co/science-codeevolve) | ~66 | Apache-2.0 | "Inspiration-based crossover" and "depth-based targeted refinement" — novel operators for pipeline evolution. |
| **gplearn** (github.com/trevorstephens/gplearn) | ~1.8k | BSD-3 | Sklearn-compatible GP. Well-engineered tree GP with bloat control. |
| **TPOT** (github.com/EpistasisLab/tpot) | ~8k+ | LGPL-3.0 | GP for ML pipeline optimization. Proves GP can evolve *pipelines* not just expressions — conceptual validation for Apollo. |

#### Quality-Diversity / Novelty Search
| Project | Stars | License | Apollo Role |
|---------|-------|---------|-------------|
| **pyribs** (github.com/icaros-usc/pyribs) | ~255 | MIT | **Best standalone QD library**. CMA-ME, CMA-MEGA, CMA-MAE. Composable archives + emitters + schedulers. Apollo's diversity engine. |
| **QDPy** (pypi.org/project/qdpy/) | — | — | NSLC (Novelty Search with Local Competition) — rewards behavioral uniqueness + local quality. Prevents single-strategy convergence. |

#### Speciation
| Project | Stars | License | Apollo Role |
|---------|-------|---------|-------------|
| **neat-python** (github.com/CodeReclaimers/neat-python) | ~1.6k | BSD-3 | **Gold standard speciation** via genomic distance. Fitness sharing, innovation tracking, historical markings. Extract speciation logic for Apollo. |

#### AST / Code Manipulation
| Project | Stars | License | Apollo Role |
|---------|-------|---------|-------------|
| **LibCST** (github.com/Instagram/LibCST) | ~1.9k | MIT | **Lossless Concrete Syntax Tree** manipulation. Visitor + Transformer classes. Best choice for gene extraction & recombination. Preserves formatting, comments, metadata. |
| **Google Pasta** (github.com/google/pasta) | ~359 | Apache-2.0 | Simpler AST refactoring with symmetry guarantee. |
| Python stdlib `ast` | built-in | — | Baseline. `ast.parse()` + `ast.unparse()` (3.9+) + `NodeTransformer`. May be sufficient without external deps. |

#### Sandboxing
| Project | Stars | License | Apollo Role |
|---------|-------|---------|-------------|
| **RestrictedPython** (github.com/zopefoundation/RestrictedPython) | ~719 | ZPL-2.1 | **In-process sandboxing**, deny-by-default. No Docker overhead. `compile_restricted()` + custom guards. **Fast inner-loop evaluation**. |
| **E2B** (github.com/e2b-dev/E2B) | ~11.4k | Apache-2.0 | Firecracker microVM sandboxes. Production-grade but heavier. Outer-loop / suspicious organisms. |
| **epicbox** (github.com/StepicOrg/epicbox) | ~200 | MIT | Lightweight Docker sandboxes with resource limits. Simple `epicbox.run()` API. |
| **microsandbox** (github.com/zerocore-ai/microsandbox) | ~3.3k | — | Sub-200ms microVM startup. Middle ground between RestrictedPython and Docker. |

#### Reference / Meta
| Resource | Description |
|----------|-------------|
| **LLM4EC** (github.com/wuxingyu-ai/LLM4EC) | Curated list of LLM + evolutionary computation papers |
| **Tutorial GP-LLM** (github.com/ALFA-group/Tutorial_GP-LLM) | MIT ALFA tutorial on GP + LLM. Covers **lexicase selection** — select parents by per-test-case performance, not aggregate fitness |
| **awesome-genetic-programming** (github.com/hengzhe-zhang/awesome-genetic-programming) | Ongoing GP resource index |
| **awesome-sandbox** (github.com/restyler/awesome-sandbox) | Sandbox comparison decision matrix |

### Recommended Component Stack

Based on the scan, the highest-impact architecture:

| Layer | Primary Pick | Rationale |
|-------|-------------|-----------|
| **Genome Representation** | geppy (GEP on DEAP) | Linear chromosomes → expression trees. Closest match to gene-fragment concept. |
| **Multi-Objective Selection** | pymoo (NSGA-III) | Gold standard. Built by NSGA-III's creator. |
| **Quality-Diversity / Novelty** | pyribs (CMA-ME / MAP-Elites) | Best standalone QD. Composable archive system. |
| **Speciation** | neat-python (extract speciation logic) | Proven genomic-distance speciation + fitness sharing. |
| **Code Manipulation** | LibCST or stdlib `ast` | Lossless transforms for gene extraction/recombination. |
| **Fast Sandbox (inner loop)** | RestrictedPython | In-process, ~0ms overhead, deny-by-default. |
| **Island Model** | LEAP or custom | Built-in migration + coevolution support. |
| **Reference Architecture** | OpenEvolve | Island model + MAP-Elites + program DB. Closest prior art. |

### Design Questions Raised
1. **Compute budget** — 200 organisms x 100 tasks x 10s timeout = 555 hrs/gen. Math doesn't close. Need hierarchical filtering + parallelism.
2. **Ground truth for synthetic tasks** — "No API calls" constraint means tasks must have algorithmically verifiable answers.
3. **Gene granularity** — Methods are tightly coupled. Semantic compatibility vs letting selection handle incoherence?
4. **AST vs string manipulation** — Strong recommendation for AST-level (LibCST or stdlib `ast`).
5. **Selection unit** — Whole class vs method vs sub-method?

### Suggestions Given
1. Warm-start population with 146 existing forge tools
2. Island model for parallelism + diversity
3. Hierarchical fitness evaluation (tournament filter)
4. MAP-Elites complement to NSGA-III (pyribs)
5. Coevolutionary task generation from gen 0
6. Phenotype caching via source hash
7. Evolvable feedback loop iteration cap (1-5, not fixed 3)

### Second Scan Results — New Finds (QD, Open-Ended Evolution, Lineage, Coevolution, Execution)

#### Open-Ended Evolution / LLM-Driven Program Evolution
| Project | Stars | License | Apollo Role |
|---------|-------|---------|-------------|
| **ShinkaEvolve** (github.com/SakanaAI/ShinkaEvolve) | ~989 | — | **Novelty-based rejection sampling** + multi-island architecture + bandit-based LLM selection. Avoids wasting mutation budget on trivial variants. |
| **FunSearch** (github.com/google-deepmind/funsearch) | ~1k | — | DeepMind's LLM + evolutionary search for mathematical discovery. Clean "programs database" concept — sample by quality, combine into prompts, evaluate. Minimal reference architecture. |
| **Lenia** (github.com/Chakazul/Lenia) | ~3.7k | — | Continuous cellular automata, 400+ species. Demonstrates unbounded diversity from simple continuous rules. Aspirational design principle. |
| **ALIEN** (github.com/chrxh/alien) | ~5.4k | — | CUDA-powered artificial life. Metrics for detecting/measuring open-endedness could inform whether Apollo's evolution is genuinely open-ended or converging. |

#### Quality-Diversity — Additional
| Project | Stars | License | Apollo Role |
|---------|-------|---------|-------------|
| **QDax** (github.com/adaptive-intelligent-robotics/QDax) | ~346 | — | JAX-accelerated QD. GPU/TPU MAP-Elites, CVT-MAP-Elites, PGA-MAP-Elites. Orders of magnitude faster for large populations. |
| **EvoGrad** (github.com/uber-research/EvoGrad) | — | — | Uber AI. "Evolvability ES" — explicitly evolves populations for **maximally diverse behaviors**, not just fitness. Directly applicable to preventing epistemic mode collapse. |

#### Lineage Tracking / Phylogenetics
| Project | Stars | License | Apollo Role |
|---------|-------|---------|-------------|
| **phylotrackpy** (github.com/emilydolson/phylotrackpy) | — | — | **Purpose-built for digital evolution phylogenies**. Tracks parent-child, computes topology metrics, handles 10k+ populations. Detects convergent evolution, evolutionary dead ends. |
| **hstrat** (github.com/mmore500/hstrat) | — | JOSS | Hereditary stratigraphy. **64-bit annotation per genome** enables phylogenetic reconstruction in distributed evolution without centralized tracking. |
| **DendroPy** (github.com/jeetsukumaran/DendroPy) | — | — | Mature phylogenetic computing. Tree distances (Robinson-Foulds), simulation, NEXUS/NEWICK/NeXML. Analysis + visualization of Apollo lineage trees. |
| **ETE Toolkit** (github.com/etetoolkit/ete) | ~871 | — | Best-in-class tree visualization. Annotate nodes with fitness, behavioral descriptors, Nemesis scores. Publication-quality evolutionary history renders. |

#### Execution Safety — Additional
| Project | Stars | License | Apollo Role |
|---------|-------|---------|-------------|
| **PyExPool** (github.com/eXascaleInfolab/PyExPool) | ~168 | — | Multi-process pool with per-job timeouts, memory-based rescheduling, CPU affinity. **Middle ground** between RestrictedPython and Docker. |
| **Pebble** (github.com/noxdafox/pebble) | — | — | Enhanced `concurrent.futures` with automatic timeout kill + restart. Simplest API for "run with timeout." |

#### Program Analysis — Additional
| Project | Stars | License | Apollo Role |
|---------|-------|---------|-------------|
| **ast-grep** (ast-grep.github.io) | large | — | Lightning-fast structural code search. Meta-variables (`$VAR`, `$$$`) for pattern matching across forge tools. Find recurring reasoning patterns systematically. |

### Updated Recommended Component Stack

| Layer | Primary Pick | Rationale |
|-------|-------------|-----------|
| **Genome Representation** | geppy (GEP on DEAP) | Linear chromosomes → expression trees. Closest match to gene-fragment concept. |
| **Multi-Objective Selection** | pymoo (NSGA-III) | Gold standard. Built by NSGA-III's creator. |
| **Quality-Diversity / Novelty** | pyribs (CMA-ME / MAP-Elites) | Best standalone QD. Composable archive system. |
| **Speciation** | neat-python (extract speciation logic) | Proven genomic-distance speciation + fitness sharing. |
| **Code Manipulation** | LibCST or stdlib `ast` | Lossless transforms for gene extraction/recombination. |
| **Fast Sandbox (inner loop)** | RestrictedPython + Pebble (timeout) | In-process sandboxing with hard timeout enforcement. |
| **Island Model** | LEAP or custom | Built-in migration + coevolution support. |
| **Lineage Tracking** | phylotrackpy + DendroPy (visualization) | Purpose-built digital evolution phylogenetics. |
| **Reference Architecture** | OpenEvolve + FunSearch | Island model + MAP-Elites + programs database. |

### Round 2: Cross-Referencing MVP Spec vs Design Review

Studied James's MVP answers, the external design review, the actual trap generator (`agents/hephaestus/src/trap_generator.py`), the Nemesis grid (`agents/nemesis/grid/grid.json`), and the Hephaestus ledger (`agents/hephaestus/ledger.jsonl`).

**Key findings from data inspection:**
- Trap generator produces 8 categories of deterministic tasks with `{prompt, candidates, correct, category}` format
- Top ledger tool: 66.7% accuracy (standard traps). Top Nemesis grid tool: 75.0% (adversarial tasks). Different tools top each list.
- Ledger tracks `margin_accuracy` (accuracy minus NCD baseline) — NCD-relative scoring already exists
- 87% of forge tools include NCD — NCD monoculture risk is real and quantified

**Key tensions identified between MVP spec and design review:**
1. Viable offspring rate: James expects 80%+ (AST method swaps), review cites <5% (random AST manipulation) — different operations, but true number is unknown
2. LLM mutation: review says it's essential, James says post-MVP — flagged viability threshold as decision point
3. NCD convergence: warm-start with top 50 tools may be warm-starting with 40+ NCD variants
4. Novelty integration with 2-objective NSGA-II: mechanism unspecified
5. Gene deletion operator absent from MVP — bloat risk
6. Phase 0 parameter evolution: recommended by review, not addressed

**13 questions written to `questions_round_2.md`**, organized as:
- 6 implementation-critical (need answers to code)
- 4 risk mitigations (review concerns not yet addressed)
- 3 architecture decisions (where documents diverge)

### Round 2 Answers — All 14 Decisions Locked

James provided definitive answers to all 13 questions + 1 bonus. Key decisions:

1. `self.param` → `self.params['gene_XX_param']` with flat parameter vector in lineage logs ✓
2. Auto-generate `confidence()` from `evaluate()` ✓
3. Shared context dict with `_gene_trace` injection for reasoning traces ✓
4. **Margin-over-NCD** as fitness metric (non-negotiable for preventing NCD monoculture) ✓
5. **Novelty as 3rd NSGA-II objective** (full Pareto dimension, no decay) ✓
6. Gene deletion at 10% — 6 mutation operators total (point mutate 40%, splice 25%, duplicate 15%, rewire 15%, delete 10%, compound duplicate-and-wire-back 10%) ✓
7. **Viability spike first** — threshold: >40% AST works, 10-40% needs careful warm-start, <10% needs local LLM ✓
8. Held-out trap battery (seed 42 for evolution, seed 137 for validation) ✓
9. Top 30 by accuracy + 20 most structurally diverse (maximin Hamming distance) for seed population ✓
10. **Phase 0 CMA-ES** warmup confirmed (2 days, validates fitness pipeline) ✓
11. AST-only unless viability <10% — then local StarCoder 1B ✓
12. Topological sort crossover with deterministic cycle-breaking (lowest gene_id) ✓
13. Compound duplicate-and-wire-back at 10% — not "let it emerge slowly" when on a 40-day clock ✓
14. Success criterion: held-out trap battery, Nemesis grid is post-MVP generalization check ✓

**Build sequence confirmed:** viability spike (afternoon) → Phase 0 CMA-ES (2 days) → structural evolution (37 days)

### Round 3: Implementation-Level Questions

Analyzed 6 diverse forge tools' method signatures to understand gene extraction patterns. Confirmed:
- Method naming is remarkably consistent across tools: `_extract_*`/`_parse_*` = PARSER, `_compute_*`/`_check_*` = SCORER, `_ncd`/`_get_ncd` = FALLBACK
- Auto-classification by name patterns + return type is feasible for 90%+ of methods
- Key ambiguity remaining: utility functions (`_sigmoid`) → classify as SCORER by default

Checked runtime environment:
- Python 3.11.9 (supports `ast.unparse()`) ✓
- `resource` module **NOT available** on Windows — no `setrlimit` for memory/CPU
- RestrictedPython and pymoo not yet installed
- Windows uses `spawn` for multiprocessing (not fork) — organisms passed as strings

**Critical question identified: the context dict key problem.**
How do genes read each other's outputs? Four models proposed:
- (a) Hardcoded keys + execution order only
- (b) Gene-ID-namespaced outputs with explicit remapping
- (c) Convention-based keys by gene type (simplest, supports self-reference naturally)
- (d) Convention + collision avoidance

This is the foundational compiler architecture decision.

**11 questions written to `questions_round_3.md`:**
- 3 critical wiring/pipeline questions (context dict keys, per-candidate execution, terminal gene)
- 2 runtime constraints (Windows sandbox, RestrictedPython)
- 6 remaining design details (gene classification, calibration metric, error handling, population model, Phase 0 specifics, viability spike scope)

### Round 3 Answers — All 11 Decisions Locked

1. **Two-tier convention keys** — convention keys (genes read/write) + auto-stamped gene-ID keys (compiler injects for analysis). Future upgrade path: post-MVP wiring can specify precise gene-to-gene key reads. ✓
2. **Per-candidate execution** with per-candidate crash isolation ✓
3. **`ctx['score']` terminal** — last SCORER wins, convention key IS the feedback channel ✓
4. **RestrictedPython compile-time only** — don't use runtime guards (safe_globals etc), process isolation handles runtime ✓
5. Defense in depth confirmed — compile gate + process isolation, clean separation ✓
6. **UTILITY type added** — helper methods (sigmoid, normalize) travel with parent gene, not standalone pipeline stages. Detect via "only called by other methods" AST analysis. ✓
7. **Brier score** — (confidence - correct)^2, inverted to 1-brier for maximization, margin over NCD ✓
8. **Gene crash = task 0.0** — organism survives on remaining tasks, log one-line crash summaries ✓
9. **Top-5 elitism** — 5 best by Pareto rank + crowding distance survive unconditionally, 45 slots competitive ✓
10. **Phase 0: per-tool CMA-ES** — 50 independent runs, single-objective (margin accuracy), 50 gens/tool, ~18 hours. Re-rank tools after optimization. Save pre/post deltas. ✓
11. **Two-phase viability spike** — Phase A (raw swap, 1hr), Phase B (with param rewriting, half day). Test functional viability (produces non-zero score on 1+ traps), not just import success. Threshold table determines mutation strategy. ✓

### Consolidated Design Document Written

**`apollo_design_v2.md`** — 20 sections, ~500 lines. Incorporates all decisions from:
- Original design doc (mission, architecture, evolutionary metaphor)
- External review (failure modes, literature, risk analysis)
- Round 1 answers (MVP scope, gene types, self-referential wiring non-negotiable)
- Round 2 answers (14 decisions: parameter rewriting, context dict, margin-over-NCD, NSGA-II 3-obj, etc.)
- Round 3 answers (11 decisions: two-tier keys, elitism, Phase 0 specifics, etc.)

Document structure:
1. Mission → 2. Build Sequence → 3. Architecture → 4. Gene System → 5. Genome Representation → 6. Compiler → 7. Mutation Operators → 8. Crossover → 9. Fitness Evaluation → 10. Selection → 11. Novelty Search → 12. Sandbox → 13. Logging → 14. Seed Population → 15. Phase 0 CMA-ES → 16. Configuration → 17. Success Criteria → 18. Dependencies → 19. Post-MVP Roadmap → 20. Main Loop Pseudocode

### Council Review — CouncilFeedback_1.md

**Reviewers:** ChatGPT, DeepSeek, Gemini, Grok, Claude (council), plus ChatGPT meta-analysis and Apollo Designer meta-analysis.

**Unanimous consensus (all 5 reviewers):**
1. Context dict weakly-typed — needs schema/distributional compatibility
2. NCD will dominate without active counterpressure beyond margin-over-NCD
3. Generation-starved (~1,600 gens insufficient) — need parallel evaluation
4. Static tasks will be memorized — need rolling curriculum
5. Bloat will accumulate — need stronger anti-bloat pressure

**Critical architectural change:** AST-only mutation is insufficient. The designer's meta-analysis: "I was too conservative when I pushed AST-only." Literature (AlphaEvolve, FunSearch, OpenELM) confirms LLM-assisted mutation produces 60-80% viable offspring vs <5% for AST. **Decision: LLM mutation architecture from day one.** Viability spike determines the AST/LLM balance, not whether LLM is used.

**Key additions from council:**
- Junction normalization (Claude council) — sigmoid shim after every SCORER, evolvable gain/bias
- Two-tier gene library (Claude + Gemini) — fine-grained genes + macro-genes for tightly coupled tools
- Trace-based NCD independence (Claude council) — track which gene produced final score, penalize FALLBACK reliance
- Phased FALLBACK decay (Gemini) — NCD contribution decays: 100% at gen 0 → 25% at gen 1500
- Rolling curriculum (all) — rotate 5 tasks every 50 generations
- Parallel evaluation (all) — multiprocessing.Pool across CPU cores, 6x speedup
- Graduated mutation schedule (Claude council) — params only first 50 gens, mild structure 50-100, full suite 100+
- Diversity-only warmup (Grok) — 50 gens novelty-only before accuracy kicks in
- Signal sanity checks (ChatGPT) — discrimination test at compilation
- Anti-bloat hard cap (Claude council) — max 15 genes, parsimony tiebreaker
- Capability step test (ChatGPT meta) — introduce novel task types every 500 gens, measure adaptation speed
- Checkpoint every 10 gens (Claude council, from 50)
- Novelty archive capped at 500 (Claude council)
- Timeout reduced to 0.5s (from 2s)

**LLM model decision point:** Need local coding model on 17GB GPU. Recommended: Qwen2.5-Coder-3B-Instruct (~6GB VRAM, leaves room for sandbox processes). Alternatives: StarCoder2-3B, DeepSeek-Coder-1.3B.

### apollo_design_v3.md Written

22 sections, ~700 lines. Complete rewrite incorporating all council feedback + meta-analyses. Major additions vs v2:
- LLM mutation architecture (Section 4) with model selection, prompt templates, AST validation
- Junction normalization (Section 6.3)
- Two-tier gene library with portability scoring (Section 5)
- NCD counterpressure system (Section 7) — trace-based independence + phased decay
- Rolling task curriculum (Section 10.2)
- Parallel evaluation (Section 13.2)
- Early death indicators dashboard (Section 15)
- Graduated mutation schedule (Section 8.3)
- Diversity-only warmup (Section 11)
- Capability step test as Criterion 4 (Section 19)

### Build & Run — Session 1 (2026-03-26)

**Built all core modules:**
- gene_extractor.py — extracts 821 genes from 187 forge tools (95 PARSER, 380 SCORER, 99 FALLBACK, 247 UTILITY)
- genome.py — whole-tool organism representation (pivoted from method-level genes due to extraction fragility)
- compiler.py — compile/validate/smoke-test organisms
- sandbox.py — threading-based timeout (pivoted from multiprocessing due to Windows spawn issues)
- task_manager.py — rolling curriculum with trap generator integration
- fitness.py — margin-over-NCD accuracy + Brier calibration
- novelty.py — behavioral signatures + capped archive (500)
- selection.py — NSGA-II with crowding distance + parsimony tiebreaker
- mutation.py — point mutate, drift, method swap, crossover
- logger.py + checkpointer.py — JSONL lineage + pickle checkpoints
- apollo.py — main evolutionary loop with viability spike, warmup, graduated schedule

**Key pivot decisions during build:**
1. **Method-level gene extraction → whole-tool organisms.** Extracted methods couldn't survive transplantation due to `self._method()` internal dependencies. 33% compiled but 0% discriminated. Council was right about extraction fragility.
2. **multiprocessing sandbox → threading timeout.** Windows `spawn` method caused crashes. Direct `exec()` with `threading.Timer` works reliably.

**Viability spike results (AST method swap):** 3-8% across multiple runs. Confirms council prediction. Below 10% threshold — **LLM mutation is an MVP requirement**, not post-MVP.

**First evolutionary run (1000 gens target):**
- NCD baseline: 45% on evolution tasks, 33.3% on held-out
- Population: 50 organisms from 187 forge tools
- Speed: ~2.5s/gen = ~35,000 gens/day (excellent)
- Best margin after 190 gens: +0.000 (no organism beats NCD on evolution tasks)
- Held-out best: +0.056 margin (38.9% raw, seed tool, not evolved improvement)
- Archive: 500 (filled during warmup)
- Self-referential organisms: 0 (no recursion detected in seed tools)

**Verdict: MVP pipeline is viable but needs LLM mutation to produce improvement.**
The evolutionary loop runs, selection works, logging works, checkpointing works. But pure AST parameter-mutation and method-swap at 3-8% viability cannot produce organisms that beat NCD. The system confirms exactly what the council predicted: AST-only mutation produces "alive but stagnant" organisms.

**Next steps:**
1. Build mutation_llm.py — load Qwen2.5-Coder-3B-Instruct locally
2. Integrate LLM mutation into the evolutionary loop
3. Re-run with LLM-assisted structural mutations
4. Phase 0 CMA-ES still needed (parameter optimization of seed tools)
5. Let the current run continue as a baseline (AST-only control group)
