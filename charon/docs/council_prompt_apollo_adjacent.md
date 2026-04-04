# Apollo Adjacent Research — Council Prompt

## Context

We are running **Apollo v2**, an evolutionary search system that evolves **routing DAGs over 25 fixed reasoning primitives** (logic, probability, causal graphs, constraints, belief tracking, metacognition). Each organism is a small program that wires together 3-7 primitives and routes their outputs via Python code to score candidate answers on reasoning tasks.

**Key architectural details:**
- **Genome**: primitive selection + DAG wiring + router code (Python) + float parameters
- **Fitness**: 6-dimensional Pareto via NSGA-II (accuracy margin over NCD baseline, calibration, ablation delta, generalization, novelty, parsimony)
- **Mutation**: 4 operators — LLM-assisted route rewriting (40%), parameter perturbation (25%), LLM-assisted wiring mutation (20%), LLM-assisted primitive swap (15%). Plus 30% crossover.
- **LLM mutator**: Local Qwen2.5-Coder-7B-Instruct (8-bit, on a 17GB GPU)
- **Counterpressures**: NCD baseline decay, discrimination test (kill NCD clones), ablation gate (kill decorative primitives)
- **Population**: 50 organisms, 50 offspring/gen, targeting 50,000 generations over weeks
- **Libraries**: pymoo (NSGA-II), transformers + torch (LLM mutation), RestrictedPython (sandbox), multiprocessing (parallel eval)

**Known bottlenecks and risks:**
1. LLM mutation unreliability — often generates invalid code, falling back to weak AST-only mutations
2. NCD dominance trap — organisms converge to compression-based scoring early on
3. Novelty archive thrashing — random replacement loses valuable diverse organisms
4. Task memorization — static 100-task battery gets memorized by ~gen 300
5. Router fragility — structural mutations break router code, high offspring crash rate
6. Slow evaluation — 0.5s timeout × 100 tasks × 50 organisms = bottleneck

## Questions for the Council

### 1. Adjacent Literature
What published work (2020-2026) is most relevant to what we're doing? We're specifically interested in:
- **Evolutionary program synthesis over DAGs** (not just neural architecture search — we're evolving logic programs)
- **LLM-guided genetic programming** — using language models as mutation operators in evolutionary search
- **Novelty search + quality-diversity** (MAP-Elites, curiosity-driven evolution, etc.) applied to program spaces
- **Multi-objective GP** with Pareto selection over behavioral metrics
- Name specific papers, authors, and venues. Don't be vague.

### 2. Speedup Opportunities
Given our architecture, what are the highest-leverage ways to speed up evolution?
- Are there faster alternatives to pymoo's NSGA-II for 6D Pareto with 50-100 individuals?
- Can we batch LLM mutations more efficiently (currently one organism at a time)?
- Are there smarter evaluation strategies than running all 100 tasks on every organism every generation? (e.g., racing algorithms, adaptive task selection, surrogate-assisted evaluation)
- Any Python libraries we should know about? (EvoTorch, DEAP, Nevergrad, etc. — which ones actually work well for program-space evolution?)

### 3. Failure Modes and Plateaus
What does the GP/evolutionary computation literature say about:
- **Bloat** in variable-length genomes (our DAGs can grow to 25 primitives)
- **Convergence traps** in multi-objective evolutionary search — when does NSGA-II get stuck and what breaks it out?
- **LLM mutation mode collapse** — has anyone studied when LLM-guided mutations converge to a narrow output distribution?
- **Novelty search saturation** — when does the novelty archive stop driving exploration?
- What early warning signals should we monitor to detect plateau before wasting thousands of generations?

### 4. Hybrid Approaches
- Has anyone combined **LLM code generation with evolutionary search** in a tight loop (not just "generate-then-filter" but genuine co-evolution)?
- **Surrogate models for fitness**: can we train a small model to predict fitness from genome features, avoiding full evaluation?
- **Island models / migration**: would splitting into 2-3 sub-populations with periodic migration help maintain diversity on a single GPU?
- **Curriculum learning for evolutionary search**: dynamically changing the task battery as organisms improve?

### 5. Libraries and Tools We Might Be Missing
- Any Python libraries for **program DAG manipulation** (beyond `ast`)?
- Better sandboxing than RestrictedPython for running untrusted evolved code?
- Efficient **behavioral signature** computation (we use k-NN on output vectors)?
- Anything from the **AutoML / neural architecture search** world that transfers to logic-program evolution?

Be specific. Name papers, libraries, GitHub repos, version numbers. We're practitioners, not reviewers — actionable recommendations only.
