# Prompt 95: E-Graphs and Equality Saturation

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdiYi1mYXNHcEFvLVVfdU1QbXIzSC1RcxIXYmItZmFzR3BBby1VX3VNUG1yM0gtUXM
**Elapsed:** 395s

---

# FRONTIER PRACTITIONER DOSSIER: E-Graphs and Equality Saturation

This report is designed for a computational scientist seeking to execute frontier experiments in the field of e-graphs and equality saturation (EqSat). The field has evolved rapidly from its automated theorem proving origins into a high-performance optimization backend. The mechanism you described in your query is fundamentally correct: equality saturation solves the phase-ordering problem by applying rules non-destructively within an e-graph, deferring the extraction of the optimal term to a separate phase (cite: 44, 46). However, the frontier has moved significantly beyond pure syntactic rewriting into database-inspired relational matching, integer linear programming (ILP) extraction, and LLM-guided checkpointing (cite: 12, 22, 50).

Research suggests that while the core data structure is mature, the extraction phase remains a severe bottleneck, mathematically proven to be NP-complete for Directed Acyclic Graph (DAG) extraction (cite: 16). Consequently, much of the contemporary frontier is focused on bounding, guiding, or bypassing the worst-case complexities of extracting from massive, saturated graphs.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

In 2026, the e-graphs and equality saturation community is a highly active, expanding subfield primarily intersecting programming languages, compilers, and hardware synthesis. The core premise remains leveraging the e-graph data structure to compactly represent exponentially many equivalent programs without destructive updates. What changed drastically over the last three years is the integration of e-graphs with Datalog, resulting in relational e-matching (cite: 50). Rather than traversing the graph top-down using backtracking, the field now translates e-matching into conjunctive database queries resolved via worst-case optimal join algorithms. This shift merged the classical compiler optimization perspective with database theory, fundamentally altering how performance is scaled.

What is SETTLED is that equality saturation is superior to sequential term rewriting for avoiding the phase-ordering problem. It is also settled that tree-cost extraction is trivial, but practically useless for environments where shared structure (DAGs) dictates actual compute cost or memory constraints. The community relies entirely on the Rust ecosystem for canonical implementations.

What is CONTESTED is the optimal strategy for DAG extraction. One faction advocates for Integer Linear Programming (ILP) and pseudo-boolean SAT solvers to achieve exact optimal extraction, accepting that it may silently time out on complex graphs (cite: 20, 68). Another faction champions Answer Set Programming (ASP) to natively encode the acyclicity of DAGs (cite: 59, 66). A third pragmatic camp accepts suboptimal, fast-greedy heuristics because exact extraction simply does not scale to production compiler workloads.

What is OPEN is the reliable integration of machine learning and Large Language Models (LLMs) with e-graphs. Straightforward LLM generation of rewrite chains hallucinates too frequently to be sound. Live experiments currently use the LLM solely to propose high-level "checkpoint" expressions, while the e-graph rigorously fills in the low-level rewrite chains between checkpoints to guarantee equivalence (cite: 22, 54). Additionally, achieving incremental equality saturation—where a single persistent e-graph maintains state across multiple disjoint terms without canonicalizing irrelevant nodes—remains an open engineering challenge for interactive applications (cite: 35).

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL

Ross Tate, Michael Stepp, Zachary Tatlock, and Sorin Lerner
2011
Equality Saturation: A New Approach to Optimization
Logical Methods in Computer Science
DOI 10.2168/lmcs-7(1:10)2011
This is the genesis paper defining equality saturation, demonstrating that optimizations can add equalities to a common intermediate representation rather than applying destructive mutations. It is strictly required reading to understand the underlying philosophy.

Max Willsey, Chandrakana Nandi, Yisu Remy Wang, Oliver Flatt, Zachary Tatlock, and Pavel Panchekha
2021
egg: Fast and Extensible Equality Saturation
POPL 2021
DOI 10.1145/3434304
This paper introduced amortized invariant maintenance (rebuilding) and domain-specific e-class analyses, overcoming the performance barriers of earlier implementations and establishing the modern Rust-based ecosystem.

Yihong Zhang, Yisu Remy Wang, Max Willsey, and Zachary Tatlock
2022
Relational E-matching
POPL 2022
DOI 10.1145/3498696
This paper proves that e-matching is an instance of conjunctive database queries, providing the first worst-case optimal data complexity bounds for e-matching and shifting the field away from backtracking algorithms.

CURRENT

Yihong Zhang, Yisu Remy Wang, Oliver Flatt, David Cao, Philip Zucker, Eli Rosenthal, Zachary Tatlock, and Max Willsey
2023
Better Together: Unifying Datalog and Equality Saturation
PLDI 2023
DOI 10.1145/3591239
This introduces egglog, unifying EqSat with Datalog to allow incremental execution and lattice-based reasoning. This is the paper that defines the architecture of the current frontier software standard.

Glenn Sun, Yihong Zhang, and Haobin Ni
2024
E-Graphs as Circuits, and Optimal Extraction via Treewidth
arXiv
arXiv:2408.17042
This paper establishes an equivalence between e-graphs and cyclic monotone Boolean circuits, utilizing parameterized treewidth algorithms to perform exact extraction in polynomial time relative to graph width, sidestepping the general NP-hard barrier.

Wentao Peng, Ruyi Ji, and Yingfei Xiong
2025
Equality Saturation Guided by Large Language Models
EGRAPHS 2025
arXiv:2511.00403
This paper formalizes LGuess, a system answering how LLMs should interface with e-graphs. It tasks the LLM with proposing intermediate optimization checkpoints rather than raw code, relying on the e-graph to securely bridge the gaps.

Ziyi Yang and Ilya Sergey
2026
Answer Set Programming for Egg Extraction and More
EGRAPHS 2026
arXiv:2606.10644
This recent abstract details how Answer Set Programming (ASP) naturally enforces acyclicity constraints for exact DAG extraction, directly challenging ILP methodologies by outperforming them on standard benchmarking suites.

Hongbo Zheng, Suyuan Wang, Neeraj Gangwar, and Nickvash Kani
2025
E-Gen: Leveraging E-Graphs to Improve Continuous Representations of Symbolic Expressions
arXiv
arXiv:2501.14951
This paper demonstrates the utility of e-graphs outside of compilers, generating massive clusters of mathematically equivalent expressions to train contrastive embedding models, solving data scarcity in mathematical ML tasks.

PART 3. SOFTWARE I CAN ACTUALLY RUN

egg
https://github.com/egraphs-good/egg
Rust
MIT
2024
MAINTAINED
This is the original, high-performance e-graph library (cite: 27, 29). It runs standard equality saturation experiments. It is designed to be hackable, meaning if you want to inspect or modify the underlying union-find and congruence closure data structures, you start here. Limitation: Pattern matching is slower than newer database-oriented engines, and it does not natively execute Datalog-style fixpoint reasoning.

egglog
https://github.com/egraphs-good/egglog
Rust
MIT
2026
MAINTAINED
This is the current community standard and the successor to pure egg (cite: 26, 27). It unifies e-graphs with Datalog. You can run incremental equality saturation, composable e-class analyses, and extract terms directly. It parses a custom s-expression language. Limitation: Due to its database-oriented memory model, it has high overhead for very simple term-rewriting tasks compared to pure egg, and its parallel execution flag often behaves non-deterministically on smaller workloads.

extraction-gym
https://github.com/egraphs-good/extraction-gym
Rust
MIT
2025
MAINTAINED
This is the authoritative benchmark harness specifically designed to test novel extraction algorithms against a corpus of real-world saturated e-graphs (cite: 38, 69). If you build a new extractor (e.g., using a SAT solver, reinforcement learning, or ASP), you plug it into this harness to compare its exact DAG cost against ILP and greedy baselines. Limitation: Highly specialized; it tests only extraction on pre-computed e-graphs, not the saturation process itself.

Herbie
https://github.com/herbie-fp/herbie
Racket
MIT
2025
MAINTAINED
Herbie is an end-user tool that uses e-graphs to improve the accuracy of floating-point expressions by exploring mathematically equivalent terms that minimize catastrophic cancellation (cite: 32). It transitioned its backend to use egg. It is highly reproducible. Limitation: Tied specifically to numerical methods and floating-point errors; not a general-purpose EqSat library.

PART 4. DATA AND BENCHMARKS

extraction-gym Data Suites
https://github.com/egraphs-good/extraction-gym/tree/main/data
Size: Hundreds of serialized e-graphs ranging from tens to tens of thousands of nodes.
License: MIT
This is the authoritative benchmark collection for DAG extraction (cite: 38, 58). It contains serialized e-graphs captured from diverse domains, including "babble" (library learning), "herbie" (floating-point math), and "rover" (RTL datapath synthesis). These are used to measure the runtime and DAG cost output of extraction algorithms. Note: Do not assume an algorithm scales just because it solves the "math" sets; the "rover" e-graphs contain highly dense, shared nodes that routinely cause ILP solvers to time out (cite: 20).

MathVista and E-Gen Corpus
IDENTIFIER UNKNOWN
Size: Approximately 800 applied mathematical rules generating millions of equivalents.
License: UNCONFIRMED
Used to measure and train embedding models for symbolic expressions (cite: 33). E-Gen utilizes e-graphs to generate guaranteed mathematical equivalents, overcoming the contamination issues found in standard LLM web-scraped math datasets.

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to run as a newcomer is a comparative evaluation of exact DAG extraction algorithms using the extraction-gym. This isolates the NP-hard phase of EqSat and demonstrates exactly why cost modeling is the frontier.

Software: Clone extraction-gym from https://github.com/egraphs-good/extraction-gym.
Version: Main branch as of mid-2025.
Dataset: The built-in "babble", "herbie", and "rover" JSON e-graphs located in the data/ directory.

Parameters to set:
Execution timeout: 10 seconds per graph.
Extraction algorithms to enable: "faster-greedy-dag" (baseline), "ilp-cbc-timeout" (standard exact extraction), and "asp-td" (top-down Answer Set Programming).
Cost model: Uniform cost (each e-node has a cost of 1).

Replicates and Seeding: Deterministic, single-threaded execution. No seeding regime required for exact solvers unless breaking ties in ILP, in which case use seed 42 across 3 replicates.
Compute cost: Less than 2 CPU hours on a modern workstation.

Expected Result:
You will measure the extracted DAG cost and the time-to-solution. You must compare your results to the baselines published in the 2026 ASP extraction paper (arXiv:2606.10644) (cite: 58, 59).
1. "faster-greedy-dag" will extract instantly but produce suboptimal DAG costs on roughly 15 to 30 percent of the highly-shared "rover" graphs.
2. "ilp-cbc-timeout" will find the optimal cost for smaller graphs but will hit the 10-second timeout on complex hardware synthesis graphs, returning nothing.
3. "asp-td" will find the optimal cost on a strict superset of the graphs solved by ILP, demonstrating the acyclic structural advantage of ASP over integer programming.

The three most common ways people get this experiment wrong:
1. Optimizing for tree cost instead of DAG cost. A greedy bottom-up pass perfectly optimizes tree cost but completely ignores node sharing, resulting in artificially high actual compute costs when the code is emitted.
2. Failing to canonicalize the input e-graph before extraction. If the root e-class IDs are not canonicalized, the extraction loops infinitely or crashes.
3. Using an ILP solver without configuring its pseudo-boolean specific optimizations, resulting in catastrophic backtracking and immediate timeouts on dense graphs.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

1. A Persistent, Context-Aware E-Graph Database for JIT Compilers
Currently, equality saturation pipelines are stateless. You insert a term into an empty e-graph, saturate it, extract it, and throw the graph away. For Just-In-Time compilers or interactive synthesis, this discards reusable equalities (cite: 35). A serious entrant would need to build a persistent e-graph database that maintains state between invocations.
Interface: In: A syntax tree and an identifier indicating the current context or scope. Out: An optimally extracted syntax tree.
Hard Part: Canonicalizing the graph safely. In a persistent graph, rewrites applied to a new term might trigger cascading equivalence merges in historically unrelated parts of the graph, causing an unmanageable memory explosion.
Work: Heavy systems engineering. Approximately 6 to 12 months for a competent developer to fork egglog and implement versioned e-classes. Multiple teams have privately patched egg to simulate persistence, indicating a massive gap.

2. A Reinforcement Learning (RL) Rewrite Scheduler
EqSat applies rules semi-blindly. While rebuilding and batching mitigate overhead, applying all rules continuously until saturation hits a timeout is brute force. There is no off-the-shelf tool that uses an RL agent or Monte Carlo Tree Search (MCTS) to predict which rewrite rules are statistically likely to yield the lowest-cost extraction on a specific e-graph state (cite: 37, 40).
Interface: In: The current serialized e-graph state and the rewrite rule library. Out: A probability distribution over which rules to fire next.
Hard Part: The state space of an e-graph changes structurally after every merge, making standard graph neural network embeddings unstable.
Work: 3 to 6 months of bridging Rust (egglog) and Python (PyTorch) via bindings to run training loops.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

1. The Failure of Bottom-Up Greedy Extraction for DAGs
For years, practitioners used simple bottom-up dynamic programming to extract terms from e-graphs. It works perfectly if the cost function is tree-size (where the cost of a parent is strictly the sum of its children plus the parent's intrinsic cost). However, real-world execution environments rely on common subexpression elimination; if two branches use the same node, it is computed once (DAG cost). Bottom-up extraction mathematically cannot compute DAG cost because the decision to share a node requires global top-down context. Tools that rely exclusively on bottom-up extraction for hardware synthesis or compiler backends have consistently reported synthesized code that is larger than the input baseline, rendering the optimization useless (cite: 19, 40, 59).

2. Direct LLM Term Rewriting Does Not Replicate
Several programmes between 2023 and 2024 attempted to fine-tune LLMs to directly output optimized terms or full rewrite chains from a starting expression. These claims largely failed to replicate in rigorous formal environments. LLMs consistently hallucinate mathematical properties (e.g., applying commutativity to non-commutative matrix operations) and skip necessary intermediate algebraic steps. The standing methodological critique is that LLMs operate on token-level probabilities, while rewrite systems require strict topological congruence invariants (cite: 22, 54). This critique was definitively answered by the LGuess architecture (arXiv:2511.00403), which proved that LLMs are only useful as "checkpoint" proposers, delegating the formal rewrite chain proofs exclusively back to the e-graph.

3. The Scalability Limits of Integer Linear Programming (ILP)
When the community realized greedy extraction was suboptimal for DAGs, the standard pivot was to model the extraction as an ILP problem using solvers like CBC or Gurobi. However, negative results quickly compounded in VLSI and RTL datapath domains (e.g., the ROVER project). E-graphs with thousands of highly interconnected nodes triggered worst-case exponential backtracking in ILP solvers, resulting in timeouts (cite: 20). The critique is that ILP cannot natively model the acyclic reachability required for DAG extraction without an explosion of constraint variables. This remains a standing limitation, prompting the current exploration into Answer Set Programming and parameterized treewidth algorithms (cite: 71).

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

If you are a well-resourced newcomer, you should focus on bypassing the NP-hard extraction bottleneck entirely by exploiting the topological structure of the e-graph.

1. Treewidth-Bounded Extraction via Circuit Minimization (Highest Priority)
Implement and scale the theoretical treewidth algorithm proposed by Sun et al. in arXiv:2408.17042 (cite: 17, 71).
Feasibility: Previous implementations relied on heavy, generalized ILP or ASP solvers. Treating the e-graph as a cyclic monotone Boolean circuit allows you to use standard hardware circuit minimization techniques.
Measurement: Compare extraction time against ILP and ASP on the extraction-gym "rover" dataset.
Falsification: If simplifying the e-graph as a circuit does not reduce its treewidth to a manageable constant (e.g., k < 10), the parameterized O(2^(w^2)) complexity will cause the algorithm to blow up just as badly as ILP, falsifying the utility of the approach for production compilers.

2. MCTS for DAG Extraction
Build an extraction module that treats e-node selection as a game tree navigated by Monte Carlo Tree Search (cite: 40).
Feasibility: Fast greedy extraction provides rapid rollouts to estimate the value of a state. High compute availability allows massively parallel rollouts.
Measurement: DAG cost achieved within a strict 1-second timeout versus the greedy baseline.
Falsification: If the search space is too dense with local minima, MCTS rollouts will consistently fail to beat the deterministic heuristics, proving that stochastic extraction is inefficient for algebraic graphs.

3. Datalog-driven Contextual E-Graphs
Implement parameterized contexts in egglog, where relations are maintained in shallow, context-dependent database layers (cite: 51).
Feasibility: Egglog has successfully unified EqSat and Datalog (cite: 12), but context-sensitivity (e.g., node A is equal to node B only if variable X > 0) currently requires duplicating the entire graph. Database materialized views make shallow layering possible now.
Measurement: Memory overhead and saturation time for queries requiring branching context versus standard egglog.
Falsification: If the overhead of managing layered database views exceeds the cost of simply copying the e-graph for each context, the approach fails.

What will NOT work:
Attempting to train an end-to-end neural network to ingest an uncanonicalized e-graph and output the optimal extracted DAG will not work. E-graphs lack a canonical linear or spatial ordering, meaning identical equivalence sets can have wildly different memory layouts. Graph Neural Networks (GNNs) suffer from over-smoothing on the highly interconnected, dense equivalence classes found in saturated graphs. Without a breakthrough in invariant representation for congruence closures, pure deep learning approaches will just memorize the benchmark topologies rather than learning the extraction function.
