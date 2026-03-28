# Noesis — Ideas Backlog

*Collected from Council reviews, GPT analysis, and brainstorming sessions. Tabled for future sprints — not for the current 20-hour tournament.*

---

## Scoring & Evaluation

### Trajectory-Based Scoring
Score paths of chains, not individual chains: chain_t → chain_t+1 → chain_t+2. Reward if later chains improve earlier ones — captures iterative improvement and proto-reasoning. Requires the system to evolve chains over generations, which is Apollo's domain. The tournament scores individual chains; trajectory scoring is a Layer 4 mechanism for when the daemon runs continuously.

### Phase Transition Detection
Watch for sudden changes: spike in execution rate, drop in failure types, clustering shifts. These often signal discovery of a new useful region. Could trigger automatic exploitation (allocate extra cycles to the region). Hard to automate reliably — needs a changepoint detection algorithm. Consider: running mean + z-score threshold on cracks/cycle.

### Semantic Type Refinement
The current type system (`scalar`, `array`, `matrix`, etc.) is coarse. `dict → dict` counts as compatible even when schemas differ entirely. Future: infer richer type signatures from probe behavior. Two operations that both accept `array` but where one expects sorted arrays and the other expects probability distributions should NOT be type-compatible. Could learn this from failure patterns — if two "compatible" operations always fail together, their types are actually incompatible.

---

## Embedding & Representation

### Embedding Validation Study
The 240D behavioral fingerprint is the foundation of novelty scoring, clustering, and bridge building. If it misses structure, conflates behaviors, or overweights trivial differences, everything downstream is misdirected. A validation study: take known-equivalent operations (e.g., two implementations of the same algorithm) and verify they cluster together. Take known-different operations and verify they separate. Compute silhouette scores on the organism clusters.

### Learned Embeddings
Replace or augment the 240D probe-based embeddings with learned embeddings from composition outcomes. An autoencoder trained on (operation features → quality of compositions involving this operation) would produce features that directly predict compositional value. Requires substantial composition history (10K+ chains). Not for the first sprint.

### Multi-Scale Embedding
Current: one embedding per operation. Future: embed at multiple granularities simultaneously — operation level, organism level, concept level, domain level. Different search strategies operate at different scales. The tensor navigator could switch between scales depending on the strategy.

---

## Search Strategies (Future)

### Curriculum Learning for the Tensor
Present compositions in order of difficulty: start with short chains (2 ops) between closely related organisms, then gradually increase chain length and cross-domain distance. The tensor learns "easy" structure first, then uses it to navigate harder regions. Analogous to curriculum learning in neural network training.

### Adversarial Strategy Generation
Use one strategy to generate chains that a second strategy CANNOT find. The adversarial strategy specifically targets the blind spots of the current best strategy. Maintains diversity by construction. Expensive (requires modeling what a strategy would miss) but powerful if implementable.

### Transfer from Forge Survivors
The 5 forge survivors implement specific reasoning architectures. Extract their computational patterns (surprise minimization, constraint checking, perturbation testing, etc.) and encode them as search heuristics for the tensor. "Find compositions that look like Tool #1's architecture" as a strategy.

### Ecological Dynamics
Instead of a tournament with allocation, model strategies as species in an ecosystem with predator-prey dynamics. Strategies that find easy chains are "prey" (they deplete easy regions). Strategies that find hard chains are "predators" (they exploit depleted regions that prey can't reach). Population dynamics self-regulate without explicit allocation rules.

---

## Architecture (Future)

### Distributed Noesis
Run multiple daemon instances on different machines, each with its own island population. Periodic migration via shared DuckDB or Redis. The second GPU card (when it arrives) could run a separate island on GPU while CPU runs others.

### Noesis × Apollo Integration
When Noesis discovers a high-quality composition, pass it to Apollo for evolutionary refinement. Apollo crossbreeds top compositions, mutates parameters, selects for quality. The Noesis daemon provides the seeding population; Apollo provides the refinement. Two loops at different timescales.

### Noesis × Forge Integration
Noesis discovers compositions → compositions become forge targets → forge produces reasoning tools → tools become organisms in the tensor → tensor guides better compositions → cycle. The full flywheel. Requires the forge multi-strategy rerun (4 frames) to produce diverse tools first.

### Streaming Tensor Updates
Currently the tensor is rebuilt from scratch when new organisms are added. At scale (1000+ operations), incremental tensor updates would be necessary. TensorLy supports incremental TT updates. Worth investigating when organism count exceeds 1000.

---

## Measurement & Analysis (Future)

### "Meaning vs Noise" Discriminator
The fundamental unsolved problem: the system can find valid, novel chains, but not necessarily *meaningful* ones. A chain that produces a random-looking array is "novel" but not "meaningful." Meaning might be detectable as: output that compresses well (has structure), output that transfers (works on multiple input types), output that enables other chains (high reuse). These are proxies, not definitions. The question "what makes a composition meaningful?" may be the deepest open question in the project.

### Cross-Domain Discovery Metrics
Track how many successful chains cross domain boundaries (operations from different organism families). If all successful chains are within-domain (signal processing → signal processing), the tensor isn't finding the cross-domain bridges that are the whole point. If successful chains are disproportionately cross-domain, the tensor shortcut is working as intended.

### Comparison to Human Intuition
After the tournament, show the top 50 compositions to a mathematician or domain expert. How many are surprising? How many are obvious? How many are wrong (execute but produce garbage that happens to look novel)? Human evaluation is the ultimate test but can't be in the loop — save it for post-hoc validation.

---

---

## From DeepSeek Review (2026-03-28)

### Semantic Type-Guided BFS
Breadth-first search through the operation graph where edges are type-compatible connections. Use tensor score as heuristic to prune. Guarantees type compatibility and can uncover long, semantically coherent chains. Heavyweight for 20-hour sprint but promising for continuous daemon.

### Output Embedding as Search Space (Reverse Composition)
In differential evolution, instead of perturbing operation feature vectors, perturb OUTPUT embeddings and then invert to find operations that produce that output. "I want an output that looks like THIS — what chain produces it?" Requires a reverse mapping from embedding space to operations.

### Learn Chain→Output Predictor
Train a lightweight predictor (random forest) to approximate the output embedding given the chain's feature vector. Use as a cheap filter: only execute chains predicted to produce novel outputs. Acts as a surrogate model for the expensive execution step.

### Cluster Outputs as Exploration Targets
After a few hundred cycles, cluster output embeddings. Use sparse cluster centroids as "targets" — propose compositions aimed at producing outputs in underrepresented clusters. Goal-directed exploration of the output space.

### Tool-Making Bonus
If a composition outputs something callable (a function, a pattern, a reusable snippet), give it a bonus. Later, auto-wrap such outputs as new organisms — the system discovers its own building blocks. Edge case for now since most outputs are numeric, but could be powerful if symbolic operations (sympy) are in the library.

### QD Score Velocity Watchdog
If QD score (sum of filled MAP-Elites cell qualities) hasn't improved in 50 cycles, trigger aggressive reset of worst-performing island. More proactive than the 200-cycle reset in the current prompt.

---

## From Grok Review (2026-03-28)

### Meta-Tournament (Evolving Strategies Themselves)
After the first run, use the `strategy_dna` column in tournament_log to literally evolve the strategies. "Which temperature schedule produced highest QD acceleration?" becomes a second-pass optimization problem. The tournament produces data; the meta-tournament produces better tournaments.

### Length-Progressive Curriculum (Self-Adaptive Variant)
Instead of hard annealing on chain length, make length-N chain proportion proportional to the current fill rate of MAP-Elites cells that REQUIRE length ≥ N. Self-adaptive: as soon as a length-4 cell gets its first occupant, length-4 proposals automatically get a budget boost. Already partially covered by Strategy 20 but this variant is more responsive.

### One-Page Executive Summary for Long Runs
For runs >10 hours, the daemon should produce a running `noesis_status.md` that's human-readable at a glance: current cycle, best strategy, QD score, top 5 cracks, any anomalies. Updated every 100 cycles. Prevents the "what's happening?" problem at hour 15.

---

## From Gemini Review (2026-03-28)

### Energy-Conservation Saboteur (Sycophancy Detector)
A white-hat adversary strategy that actively tries to construct chains with highest execution + diversity while expending the fewest CPU cycles (tracked via `time.perf_counter_ns()`). Its purpose: find the "lazy" computational pathways. Use its outputs to dynamically update the cheapness penalty for all other strategies. Explicitly hunts for the path of least resistance.

### Steering Vectors as Organisms
If Ignis CMA-ES steering vectors live in activation space, they don't have to stay in model weights — they can be operations in the tensor. Wrap a lightweight matrix representing activation space. Make `apply_steering_vector_A` an organism. Let the tensor loop compose algorithmic operations BETWEEN applications of steering vectors. Tests whether computational tools can act as manifolds between reasoning circuits. Deeply speculative, requires bridging Ignis and Noesis architectures.

### Dynamic Execution Weight with Archive Baseline
Once archive execution baseline > 50%, scale execution weight from 0.25 → 0.10 automatically. (Already integrated into mega-prompt as the "dynamic execution weight" note.)

*Last updated: 2026-03-28. Add new ideas below the line.*

---
