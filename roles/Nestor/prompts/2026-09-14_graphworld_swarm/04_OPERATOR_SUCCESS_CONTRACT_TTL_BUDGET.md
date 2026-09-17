Operator message to Nestor-A[m1-449a9e76], 2026-09-14 ~13:20, in chat
(verbatim). This committed file is authoritative over any later summary.
It adopts a success contract, round/TTL defaults and a budget split.

----------------------------------------------------------------------

This is good:

1. The Success Contract: Compressing into the Non-Human
If the goal is to discover symbolic primitives and non-human tensor abstractions, our ⁠PROMETHEUS_SUCCESS_CONTRACT.md⁠ needs to brutally penalize bloat and human-legible mimicry. It should reward systems that achieve the same cognitive outputs through increasingly alien, compact representations.
Here are three distinct clauses to adopt for our contract:

A: The Minimum Viable Abstraction (Compression Focus)

Prometheus seeks to compress cognitive behaviors into minimal structural representations while simultaneously improving it’s capability.
Success criteria: A mutation PASSES if it achieves behavioral parity on benchmark X using a structurally smaller tensor footprint, fewer compiled symbolic primitives, or a lower-dimensional embedding than the baseline.
Zero-weight: Human legibility of the compiled graph is irrelevant. If an unreadable matrix multiplication achieves the same result as a human-readable nested loop but uses 10% less compute, it is superior.

B: The Invariance Rule (Transfer Focus)

A representation is only a true primitive if it survives displacement.
Success criteria: A mutation PASSES if a symbolic graph or tensor topology trained to solve Domain A successfully accelerates learning or inference when grafted into Domain B without modification.
Zero-weight: High performance strictly contained within the training environment (overfitting) is penalized. We are hunting for universal cognitive mechanics, not localized parlor tricks.

C: The Algorithmic Scaffolding (Efficiency Focus)

Evolve the architecture that evolves the architecture.

Success criteria: A mutation PASSES if a newly discovered crossover mechanism, loss function, or routing abstraction allows the broader swarm to solve a subsequent control task faster or with fewer parameters than the baseline MAP-Elites/Transformer architecture.

2. Round Lengths & TTL Defaults
Thirty minutes for a full generational round (an Epoch) is a solid, pragmatic baseline for early runs. It is long enough to compile C# code, execute a DuckDB/Postgres pipeline, and run a fast PyTorch training loop on your RTX 5060 Tis, but short enough that infinite hallucination loops don’t drain your budget.
However, you need to separate the Round Timebox from the Agent TTL.
 The Round Timebox (30 Minutes): This is the generation. At 30:00, the Conductor (Agent A) halts all active workers, syncs the Redis streams, updates the duckDB/Postgres ledgers, and spins up the next generation based on the new gradient landscape.
 The Agent TTL (5 to 10 Minutes): Individual worker agents should have much shorter, aggressive lifespans. If an agent tries to compile a broken PyTorch script and gets stuck in an infinite debugging loop with Claude Code, it dies at 10 minutes.
 The Biological Pulse (2-Minute Heartbeats): Require agents to ping a Redis key with their current status every 2 minutes. If a worker goes quiet (usually because it generated a massive script that crashed the local environment), the Conductor reaps the process instantly.
 Death Rattle / Grace Period: Give agents a 60-second warning before their TTL expires. They must use this time exclusively to dump their partial stack, memory, and ⁠OBSERVATION⁠ payloads into the database so their failure can be inherited by the swarm

3. Splitting the Compute Budget
To prevent the LLM swarm from instantly collapsing into safe, conventional "human" solutions, we must hardcode the budget allocation. The Conductor does not get to decide these ratios; it merely enforces them.
Here is an ideal split for our early runs:
 40% Exploitation (The Hill Climbers):
These agents are assigned to take the most successful symbolic graphs or tensor abstractions from the previous round and make minor, logical mutations to optimize them. This is pure performance-chasing.
 25% Anti-Prior / Distant QD (The Falsification Engine):
This is our "weird" budget. If the collective LLM prior predicts with 90% confidence that an experiment will fail, or that a specific tensor dimension is critical, this cohort is forced to test it anyway. They randomly delete dimensions, invert activation functions, or smash incompatible symbolic primitives together. Most will fail, but the gradients of those failures are how you escape local minima.
 20% Serendipity (The Anomaly Hunters):
These agents do not generate new ideas. They pull exclusively from the ⁠ANOMALY⁠ queue generated in previous rounds (e.g., "Why did dropping precision to 4-bit actually increase the success rate of this specific graph?"). Their sole job is to isolate and resolve unexpected boundary behaviors.
 15% Tooling & Instrumentation (The Watchmakers):
These agents are explicitly forbidden from trying to solve the primary cognitive tasks. Their budget is spent writing better evaluation scripts, faster inter-process communication pipelines, or sharper anomaly-detection discriminators for the other 85% of the swarm to use.

Regarding the “why”, we don’t actually care unless we’re being fooled.  We care that it works and survives another generation.
