# Deep Research Brief: Surrogate-Assisted Fitness Evaluation for Evolutionary Program Synthesis

## Research Question

Apollo evaluates ~150 organisms per generation across 100 tasks (15,000 sandbox executions/gen). As organisms get more complex and the task battery grows, evaluation becomes the bottleneck. We need to understand **surrogate-assisted evolutionary optimization (SAEO)** techniques specifically applicable to program-space evolution, where the genome is variable-length code rather than a fixed-length vector.

## System Context

Apollo evolves small Python programs (DAGs of 3-7 reasoning primitives). Each evaluation runs the program in a sandboxed thread with 0.5s timeout per task. Current throughput: ~10 gens/min. We want 10x-100x speedup without losing selection quality.

Key constraint: fitness is a 6-dimensional Pareto vector (accuracy, calibration, ablation delta, generalization, novelty, parsimony). Surrogates need to approximate multi-objective fitness, not just a scalar.

## What I Need You to Research

### 1. Surrogate Models for Discrete/Variable-Length Genomes
- How do you build a surrogate when the search space is variable-length code, not R^n?
- Approaches: graph neural networks over ASTs, code embeddings (CodeBERT, StarCoder), kernel methods on program behavior
- Comparison of genotype-based surrogates (predict fitness from code structure) vs phenotype-based surrogates (predict fitness from behavioral signature)
- Which works better for multi-objective fitness prediction?

### 2. Pre-Selection / Racing Algorithms
- Use surrogate to filter candidates BEFORE expensive evaluation
- Racing (F-race, iterated F-race): evaluate candidates on a few tasks, statistically eliminate the worst, only fully evaluate survivors
- How much speedup is achievable without degrading Pareto front quality?
- Intersection with multi-armed bandit literature (adaptive task selection)

### 3. Fitness Inheritance and Approximation
- Offspring inheriting parent's fitness as an initial estimate
- Partial evaluation strategies: evaluate on a subset of tasks, use error bounds to decide if full evaluation is needed
- Epsilon-dominance with approximate fitness: how much noise can NSGA-II tolerate before Pareto ranking degrades?

### 4. Transfer Surrogates Across Task Rotations
- Apollo rotates 10/100 tasks every 50 generations
- Can a surrogate trained on one task set transfer to the next? What breaks?
- Literature on dynamic multi-objective optimization with changing fitness landscapes

### 5. Practical Implementations
- Libraries: pymoo surrogate support, SMACv3, Optuna multi-objective, Vizier, BOHB
- Code-level surrogate implementations that handle variable-length genomes
- Any open-source implementations combining program synthesis + surrogate evaluation

### 6. Risk: When Surrogates Mislead Evolution
- Known failure modes: surrogate overfit to simple programs, misranking near the Pareto front
- How to detect surrogate drift (fitness prediction accuracy declining over generations)
- Recovery strategies: periodic surrogate retraining, mixed evaluation (surrogate + real on alternating generations)

## Output Format

For each area, provide:
- **Key papers** (title, authors, year, venue, 2-3 sentence relevance summary)
- **Practical recommendations** for our system (variable-length code genomes, 6-objective NSGA-II, 100-task battery)
- **Known pitfalls** to avoid
- **Open questions** the literature hasn't resolved

Prioritize 2022-2026 work. Include seminal older papers where foundational.
