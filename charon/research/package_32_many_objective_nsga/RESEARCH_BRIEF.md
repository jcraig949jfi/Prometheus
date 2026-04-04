# Deep Research Brief: Many-Objective Optimization Beyond NSGA-II

## Research Question

Apollo uses NSGA-II with 6 Pareto objectives. The many-objective optimization literature warns that Pareto dominance breaks down at 4+ objectives — most individuals become non-dominated, selection pressure collapses, and the search degenerates to random walk. We need to understand whether we're already in this regime and what alternatives exist.

## System Context

Apollo's 6 objectives:
1. **Accuracy margin** — task correctness above NCD baseline
2. **Calibration** — confidence matches actual accuracy
3. **Ablation delta** — all primitives must be load-bearing (bypass-free)
4. **Generalization** — performance on held-out tasks
5. **Novelty** — behavioral distance from archive (k=15 nearest neighbors)
6. **Parsimony** — fewer primitives preferred

Population: 50. Offspring: 50. Selection: top 55 survive.

Current implementation: custom NSGA-II (not library — rolled our own in selection.py). Crowding distance for diversity within Pareto fronts.

## What I Need You to Research

### 1. The Many-Objective Breakdown
- At what objective count does Pareto dominance empirically fail? (Literature suggests 3-5)
- How does population size interact with objective count? Is 50 enough for 6 objectives?
- Empirical studies comparing NSGA-II vs NSGA-III vs MOEA/D at 4-8 objectives on combinatorial problems

### 2. Reference-Point Methods (NSGA-III)
- How does NSGA-III differ from NSGA-II practically?
- Reference point placement for 6 objectives — how many are needed?
- Implementation complexity: can we retrofit NSGA-III into our existing selection loop?
- pymoo NSGA-III implementation — can we swap it in vs maintaining our own?

### 3. Decomposition Methods (MOEA/D, RVEA)
- MOEA/D: decompose many-objective problem into scalar subproblems
- Weight vector adaptation (MOEA/D-AWA)
- Is decomposition appropriate when objectives are heterogeneous (accuracy is continuous, ablation is binary, novelty is computed differently each gen)?
- Theta-DEA for constrained many-objective optimization

### 4. Objective Reduction and Conflict Analysis
- Can we reduce 6 objectives to fewer without losing information?
- Objective conflict detection: which objectives actually conflict vs are redundant?
- Accordion method: dynamically expand/contract objective set
- PCA on the objective space to find the true dimensionality

### 5. Selection Pressure Diagnostics
- How to measure whether selection pressure is adequate in a running evolution
- Hypervolume indicator convergence monitoring
- Dominance resistance solutions (DRS) detection — are organisms surviving by being incomparable rather than good?
- Practical metrics to add to Apollo's per-generation dashboard

### 6. Adaptive Objective Weighting
- Dynamic weight adjustment based on search progress
- Objective prioritization schedules (e.g., accuracy first, then diversity, then ablation)
- Curriculum-like objective activation (Apollo already does this: accuracy at gen 50, ablation at gen 100)
- Multi-criteria decision making for final solution selection from Pareto archive

## Output Format

For each area, provide:
- **Key papers** (title, authors, year, venue, 2-3 sentence relevance summary)
- **Practical recommendations** for our system (6 objectives, pop=50, program genomes)
- **Known pitfalls** to avoid
- **Open questions** the literature hasn't resolved

Prioritize 2022-2026 work. Include seminal older papers where foundational.
