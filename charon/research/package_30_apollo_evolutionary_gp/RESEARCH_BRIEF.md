# Deep Research Brief: Evolutionary Search over Reasoning Primitive DAGs

## Research Question

We are building **Apollo**, an evolutionary system that searches over **directed acyclic graphs (DAGs) of fixed reasoning primitives** to discover routing strategies that outperform compression-based baselines on diverse reasoning tasks. We need a comprehensive literature survey of adjacent work, known failure modes, and practical speedup techniques.

## System Description

Apollo evolves small programs (3-7 nodes) where each node is a fixed Python function (e.g., `bayesian_update`, `solve_sat`, `topological_sort`, `track_beliefs`). Evolution searches over:
1. Which primitives to include
2. How to wire them (DAG edges)
3. A Python "router" function that combines primitive outputs into a final score
4. Continuous parameters (thresholds, weights)

Selection uses **NSGA-II with 6 Pareto objectives**: accuracy margin, calibration, ablation delta (all primitives must be load-bearing), generalization to held-out tasks, novelty (k-NN behavioral distance), and parsimony.

Mutations are **LLM-assisted**: a local Qwen 7B model rewrites router code, suggests wiring changes, and proposes primitive swaps. Fallback to AST-level parameter perturbation when LLM output fails validation.

## What I Need You to Research

### 1. LLM-Guided Genetic Programming (2022-2026)
- Papers that use large language models as mutation/crossover operators in genetic programming
- Specifically: EvoPrompting (Chen et al.), FunSearch (Romera-Paredes et al., DeepMind), LLM-guided program synthesis via evolutionary methods
- How do they handle LLM unreliability? What validation/repair strategies work?
- What LLM sizes work for code mutation? Is 7B sufficient or is there a quality cliff?

### 2. Quality-Diversity Algorithms for Program Spaces
- MAP-Elites applied to program evolution (not just robotics)
- Novelty search + local competition (NSLC)
- Behavioral characterization methods for programs (how to compute meaningful behavioral signatures)
- When does novelty search saturate, and what are the mitigations?

### 3. Multi-Objective Evolutionary Optimization — Scaling and Speedups
- Alternatives to NSGA-II for 6+ objectives (NSGA-III, MOEA/D, reference-point methods)
- **Many-objective optimization** literature — at what dimensionality does Pareto dominance break down?
- Racing algorithms and surrogate-assisted evaluation to reduce fitness evaluation cost
- Adaptive operator selection (which mutation operator to use when)

### 4. Bloat Control and Convergence in Variable-Length GP
- Parsimony pressure vs. lexicographic parsimony vs. multi-objective bloat control
- Known convergence traps in Pareto-based GP
- Techniques for maintaining diversity: island models, niching, speciation
- Early warning signals for evolutionary stagnation

### 5. Practical Libraries and Implementations
- Compare: pymoo, DEAP, EvoTorch, Nevergrad, OpenELM, PushGP for program-space evolution
- Any systems that combine evolutionary search with LLM code generation in a loop
- Sandboxing approaches for running evolved code safely (better than RestrictedPython?)
- Surrogate model approaches for program fitness prediction

### 6. Failure Case Studies
- Published negative results or failure analyses in GP/evolutionary program synthesis
- Known plateau patterns and their causes
- When does increasing population size help vs. hurt?
- Task curriculum design for evolutionary search (static vs. dynamic task batteries)

## Output Format

For each area, provide:
- **Key papers** (title, authors, year, venue, and a 2-3 sentence summary of relevance)
- **Practical recommendations** for our specific system
- **Known pitfalls** to avoid
- **Open questions** the literature hasn't resolved

Prioritize work from 2022-2026, but include seminal older papers where foundational.
