# Evolutionary Agent Toolkit — Extractable Ideas for Prometheus

*What we can learn from FunSearch, AlphaEvolve, CodeEvolve, OpenEvolve, and OpenELM*

*Repos cloned to: `vault/evolutionary_agents/`*

---

## Source Repos

| Repo | Origin | License | Key Innovation |
|------|--------|---------|---------------|
| **FunSearch** | DeepMind (Nature 2024) | Apache 2.0 | Island-based program evolution, discovered new math (cap set problem, first improvement in 20 years) |
| **AlphaEvolve** | DeepMind (May 2025) | Closed source (paper only) | Improved Strassen's algorithm (first in 56 years), kissing number new lower bound |
| **CodeEvolve** | Inter & Co (Oct 2025) | Apache 2.0 | Open-source, beats AlphaEvolve on 5/6 benchmarks, meta-prompting, inspiration crossover |
| **OpenEvolve** | Community (2025) | Apache 2.0 | Open-source AlphaEvolve implementation, runs with Ollama/vLLM locally, MAP-Elites |
| **OpenELM** | CarperAI (2024) | MIT | Evolution Through Large Models, CVT-MAP-Elites, multi-domain (code, prompts, images) |

---

## Candidate Ideas for Prometheus

### 1. Island-Based Exploration with Reset (from FunSearch)

**What it is:** Instead of one population, maintain 5-10 independent "islands" that evolve separately. Periodically, the best individuals migrate between islands. When an island stagnates (no improvement for N cycles), wipe it and reseed from the best of other islands.

**Why it matters for Prometheus:** Poros currently explores the concept space as one big search. Islands would let it explore different REGIONS of the Lattice independently — one island might focus on number theory × topology compositions while another explores chaos theory × information theory. The migration step cross-pollinates discoveries. The reset prevents any island from getting stuck in a local optimum.

**Where it lives in FunSearch:** `implementation/programs_database.py` — the `_Island` class with `register_program()` and the parent `ProgramsDatabase` managing multiple islands.

**Key detail:** FunSearch uses softmax temperature-based selection within islands, not random selection. Higher-scoring programs are exponentially more likely to be selected as parents. Temperature controls exploration/exploitation tradeoff.

**Adaptation for Poros:**
- Each island is a Siege targeting a different concept or region
- Migration = share the best compositions between Sieges
- Reset = when exploration velocity on an island drops to zero, reseed with high-velocity compositions from other islands
- Temperature parameter controls whether Poros exploits known good compositions or explores novel ones

---

### 2. Meta-Prompting — Evolving the Instructions (from CodeEvolve)

**What it is:** A secondary LLM generates improved PROMPTS by analyzing the current prompt and the solution it produced. The prompt itself evolves alongside the solutions. This creates two parallel evolutionary loops: one over solutions, one over the instructions for generating solutions.

**Why it matters for Prometheus:** Currently, CAITL uses a fixed prompt template ("improve this tool's metacognition"). Meta-prompting would evolve the CAITL instructions themselves. If a particular phrasing of the improvement instructions produces better tools, that phrasing propagates. The system learns HOW to ask for improvements, not just what improvements to make.

**Where it lives in CodeEvolve:** `src/codeevolve/evolution.py` — `run_meta_prompting()` function. Uses a separate LLM call to generate enriched prompts from the parent prompt + parent solution.

**Key detail:** Meta-prompting uses the FLASH (cheaper) model, not the PRO model. The insight: generating good prompts is easier than generating good solutions, so you can use a weaker model for prompt evolution and save the strong model for solution generation.

**Adaptation for Prometheus:**
- CAITL prompt templates become evolvable organisms in the Lattice
- Track which prompt variants produce the highest forge rate / Tier B improvement
- Coeus learns which prompt patterns are causally effective (not just correlated)
- The TITL loop gains a meta-layer: Council responses that produce the best tools have their prompting patterns extracted and evolved

---

### 3. Inspiration-Based Crossover (from CodeEvolve)

**What it is:** Instead of AST-level code splicing (which produces mostly broken offspring), show the LLM multiple high-performing solutions as "inspiration" and let it synthesize a new solution. The LLM performs semantic crossover — understanding what each parent does well and combining those capabilities.

**Why it matters for Prometheus:** Apollo's design includes AST-based crossover (3-8% viability) and LLM-assisted crossover (60-80% viability). Inspiration-based crossover is a specific FORM of LLM crossover that CodeEvolve found works better than direct splicing. Instead of "combine the parsing from A with the scoring from B," you say "here are three high-performing tools — create a new tool inspired by all three."

**Where it lives in CodeEvolve:** `src/codeevolve/evolution.py` — the inspiration mechanism activates "after the first wave of migrations occurs" to prevent premature convergence. Samples a set of high-performing "inspiration" solutions from the population.

**Key detail:** Inspiration crossover is delayed — it doesn't activate until after the first migration (typically epoch 40). Early evolution uses only mutation. This prevents premature convergence by ensuring diversity builds up before crossover starts mixing.

**Adaptation for Prometheus:**
- Apollo Phase 1 (gen 0-50): parameter mutation only (already in design)
- Apollo Phase 2 (gen 50-100): add inspiration crossover from top-performing forge tools
- For Poros: when two organisms compose well individually, show both to the LLM as "inspiration" for a third organism that combines their strengths

---

### 4. Behavioral Signatures for Clustering (from FunSearch)

**What it is:** Each program gets a "signature" — its output vector across a set of test inputs. Programs with identical signatures are behaviorally equivalent even if their code is completely different. This enables deduplication by BEHAVIOR, not by code structure.

**Why it matters for Prometheus:** The CAITL monoculture problem (54 tools with identical behavior despite different names) would have been caught instantly with behavioral signatures. More importantly, for Poros: two different organism chains that produce the same output on the same inputs are redundant — only keep one. This dramatically prunes the search space without losing coverage.

**Where it lives in FunSearch:** `implementation/programs_database.py` — `_get_signature()` function that converts per-test scores into a hashable tuple. Programs with matching signatures are routed to the same cluster.

**Key detail:** Signature is computed from test OUTPUTS, not from code structure. Two programs with completely different implementations but identical test behavior have the same signature. This is a much stronger dedup than AST similarity.

**Adaptation for Prometheus:**
- Every Poros composition gets a behavioral signature = its output vector on the 20 test inputs
- Dedup: if two chains have the same signature, keep the shorter/faster one
- Clustering: group chains by signature similarity to identify "behavioral families"
- Novel chains = chains whose signature is far from all existing signatures (measured by distance in signature space)
- Direct application to forge tool dedup: replace AST similarity with behavioral signatures

---

### 5. Quality-Diversity via MAP-Elites (from OpenEvolve / OpenELM)

**What it is:** Instead of optimizing for a single fitness metric, maintain a MAP (grid) where each cell represents a different behavioral niche. Each cell holds the BEST individual for that niche. Selection pressure pushes toward quality within each niche, while the grid structure ensures diversity across niches.

**Why it matters for Prometheus:** Exploration velocity requires diversity — you can't explore faster by having 100 copies of the same good composition. MAP-Elites naturally prevents monoculture because each cell in the grid holds a different behavioral type. The grid IS the Lattice — each cell is a region of the concept space, and the best composition for that region fills the cell.

**Where it lives in OpenEvolve:** `openevolve/database.py` — `ProgramDatabase` class with feature dimensions for quality-diversity. Each program is placed in the grid based on its behavioral features. OpenELM has `CVTMAPElitesConfig` for more efficient high-dimensional grids.

**Key detail:** CVT-MAP-Elites (from OpenELM) uses Centroidal Voronoi Tessellation to partition the behavioral space, which is more efficient than regular grids for high-dimensional spaces. Our concept space is 30-50 dimensional — regular grids would be astronomically large, but CVT handles it gracefully.

**Adaptation for Prometheus:**
- Poros's Lattice IS a MAP-Elites grid where each cell is a concept-pair or concept-triple
- Quality = exploration velocity contribution
- Diversity dimensions = organism types used, output types produced, chain length, execution time
- CVT partitioning for the high-dimensional concept feature space
- Nemesis grid (already 10x10 MAP-Elites) is the prototype — scale it to the full Lattice

---

### 6. Evolution Tracing — Full Lineage (from OpenEvolve)

**What it is:** Every evolved program carries its complete lineage — which parent it came from, which mutation produced it, at which generation. This creates a searchable history of how discoveries were made.

**Why it matters for Prometheus:** When the system finds a composition that increases exploration velocity, you want to know HOW it was found. Was it a random discovery? A cross-pollination from an unexpected island? A meta-prompted variation? The lineage tells you which exploration STRATEGIES are productive, not just which compositions.

**Where it lives in OpenEvolve:** `openevolve/evolution_trace.py` — `EvolutionTracer` class that records parent→child relationships, mutation types, and fitness trajectories.

**Adaptation for Prometheus:**
- Every Poros composition records: parent chain (if any), mutation type, island of origin, cycle number
- Coeus can analyze lineage data: which mutation operators produce the most cracks? Which islands are the most productive sources of migrants?
- The lineage IS substrate — deposit it into Aletheia as relationship chains

---

### 7. Diff-Based Code Modification (from CodeEvolve)

**What it is:** Instead of generating entire programs, the LLM operates using a SEARCH/REPLACE diff format. It finds a specific section of code and replaces it with a modification. This is more focused than generating from scratch and produces fewer compilation errors.

**Why it matters for Prometheus:** CAITL currently generates complete tool rewrites. Diff-based modification would let CAITL make targeted fixes — "find the `_meta_confidence` function, replace the scope ambiguity pattern with a broader one." This is faster, more precise, and easier to review.

**Where it lives in CodeEvolve:** Throughout the prompt templates. The LLM generates `SEARCH/REPLACE` blocks that are applied to the parent program.

**Adaptation for Prometheus:**
- CAITL v2: instead of full rewrites, generate diffs
- Forge improvement becomes incremental: each CAITL pass makes targeted modifications
- Version control is trivial: the diffs ARE the changelog

---

### 8. Sandboxed Evaluation with Resource Limits (from OpenEvolve / CodeEvolve)

**What it is:** Each candidate program executes in a sandboxed environment with predefined runtime and memory limits. Failed executions return zero fitness plus error logs that inform future generations.

**Why it matters for Prometheus:** Poros hung because `stern_brocot_tree(25)` produced 33 million nodes. Sandboxing would have killed it at the memory limit. More importantly, the ERROR LOGS from failed executions are themselves information — they tell you why a composition failed, which is the waste stream / failure geometry signal.

**Where it lives in CodeEvolve:** `src/codeevolve/evaluator.py` — sandboxed execution with `5GB memory, 360 seconds runtime` limits. Failed solutions get zero fitness AND their logs are fed to future LLM prompts.

**Key detail:** CodeEvolve feeds failure logs back to the LLM. "This solution failed because of a memory overflow at line 47." The LLM uses this to avoid the same mistake. Failures are training data for the next generation.

**Adaptation for Prometheus:**
- Poros `execute_chain()` needs subprocess-based sandboxing with hard resource limits
- Failed chain error messages become Lattice entities (failure geometry)
- Recurring error types become negative signals in the scoring function: "chains involving `stern_brocot_tree` with integer input > 15 always OOM"
- Build a failure knowledge base that Poros consults before trying a chain

---

### 9. Ensemble LLM Strategy (from CodeEvolve)

**What it is:** Use multiple LLMs with weighted selection — 80% cheap/fast (FLASH), 20% expensive/powerful (PRO). Most iterations use the cheap model. Occasionally the expensive model makes a breakthrough the cheap one couldn't.

**Why it matters for Prometheus:** Currently Nous uses one API (NVIDIA NemoClaw 397B). An ensemble strategy with local Qwen-7B (80%) + API 397B (20%) would give unlimited free exploration with occasional high-quality injections. The local model handles volume, the API model handles breakthroughs.

**Adaptation for Prometheus:**
- Hephaestus: 80% local Qwen-7B forge, 20% API 397B forge for the most promising combinations
- CAITL: local 7B for volume passes, Council (TITL) for the top 10
- Nous: local scoring for most combinations, API scoring for the highest-novelty ones
- Budget stays near zero while quality remains high on the best candidates

---

### 10. Problem-Dependent Operator Selection (from CodeEvolve ablation)

**What it is:** CodeEvolve's ablation study showed that different mutation operators work better on different problem types. Meta-prompting is best for diversity-heavy problems. Inspiration crossover is best for geometric/structural problems. The optimal strategy is problem-dependent.

**Why it matters for Prometheus:** Different regions of the concept Lattice may respond to different exploration strategies. Number theory combinations might benefit from meta-prompting (evolving how we ask about primes). Topology-biology combinations might benefit from inspiration crossover (showing successful cross-domain chains). Poros should adapt its strategy per-region.

**Adaptation for Prometheus:**
- Track which exploration strategy produces cracks in which Lattice region
- Coeus learns: "meta-prompting works for abstract math, inspiration crossover works for applied science"
- Poros adapts operator selection per-island based on the island's domain focus
- This is a form of meta-learning: learning which exploration strategy to use where

---

## Integration Priority

| Idea | Effort | Impact | Priority |
|------|--------|--------|----------|
| **Behavioral signatures** (#4) | Low (pure numpy) | High (dedup + novelty measurement) | **P0 — do first** |
| **Island-based exploration** (#1) | Medium (refactor Poros loop) | High (diversity + parallel exploration) | **P1** |
| **Sandboxed evaluation** (#8) | Medium (subprocess + limits) | High (prevents hangs, captures failure data) | **P1** |
| **Quality-diversity MAP-Elites** (#5) | Medium (grid structure) | High (prevents monoculture) | **P1** |
| **Ensemble LLM strategy** (#9) | Low (config change) | Medium (cost reduction) | **P2** |
| **Evolution tracing** (#6) | Low (add lineage fields) | Medium (meta-learning about strategies) | **P2** |
| **Diff-based modification** (#7) | Medium (prompt change) | Medium (CAITL efficiency) | **P2** |
| **Meta-prompting** (#2) | High (second evolutionary loop) | High (CAITL self-improvement) | **P3** |
| **Inspiration crossover** (#3) | Medium (LLM integration) | Medium (Apollo quality) | **P3** |
| **Problem-dependent operators** (#10) | High (per-region adaptation) | High (exploration efficiency) | **P3** |

---

## The Big Picture

These repos validate four things we independently designed:

1. **Apollo's architecture is correct.** AlphaEvolve and FunSearch both use the same pattern: LLM generates program variants, evaluator scores them, evolutionary selection iterates. Apollo independently converged on this. The difference is scale (Gemini vs local 7B) not architecture.

2. **Island-based evolution prevents convergence collapse.** FunSearch, CodeEvolve, and OpenEvolve all use islands. Apollo's design doesn't yet. Add it.

3. **The scoring function matters more than the mutation operator.** CodeEvolve's ablation shows operator choice is problem-dependent, but the evaluator is universal. Our investment in Sphinx (105 categories) and the forge battery is the right priority.

4. **Failure data is training data.** CodeEvolve feeds error logs back to the LLM. FunSearch resets stagnant islands. Both treat failure as information, not waste. This is the Arcanum insight applied to code evolution.

The most important extraction isn't any single algorithm — it's the confirmation that the Prometheus architecture is on the right track, and that the frontier labs are building the same thing with 1000x the resources. We're not behind. We're convergent.
