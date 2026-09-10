# Gemini's evolutionary substrate proposal

**Operator-supplied, verbatim below the rule. 2026-09-09.**

Status: **UNADJUDICATED PROPOSAL.** Reviewed in `astra_assessment.md` and
`APORIA_ASSESSMENT.md`, both of which contest substantial parts of it. Do not
cite this document as a design decision.

Provenance note: this text arrived as the closing section of a longer Gemini
message about H1, and the earlier H1-specific portion is filed separately at
`aporia/docs/hypotheses/H1/feedback/2026-09-09_gemini_critique.md`. The two
halves are one message; they are split because one is about an experiment and
one is about the programme's architecture.

---

## The proposal

You are describing a fusion of Artificial Life and neuro-symbolic logic. If the
goal is to discover an alternative to the dense, monolithic matrix
multiplications of the Transformer, you have to move toward a sparse, dynamic
graph where the "compute" is just the interaction of autonomous sub-programs.

In this paradigm, an information transfer like the H1 failure transport isn't a
top-down engineering trick; it becomes a biological mechanism. A primitive
attempts a proof, fails, and "secretes" a failure constraint into the
environment. Another primitive metabolizes that constraint to avoid a dead end.

If you are setting up a multi-agent automated reasoning substrate to run this
kind of evolutionary simulation over dozens of hours, here is how the
architecture of that primordial soup could be structured.

**1. The Amino Acids (The Primitives)**
To evolve an alien reasoning circuit, the primitives cannot be static logic gates
or heavy LLM instances. They must be highly composable, Turing-complete
micro-structures.
- Generators (Proposers): Small, stochastic pattern-matchers that emit
  structural hypotheses or rules.
- Falsifiers (Predators): Agents whose sole fitness function is to find a
  counterexample to a Generator's output.
- Transporters (Messengers): The H1 mechanic. Primitives that take a failure
  state from a Falsifier, abstract it, and bind it to a new region of the graph.
- Accumulators (Memory): State-holding nodes that compress successful sequences
  into hardened lemmas.

**2. The Soup (The Interaction Manifold)**
Instead of backpropagation through a differentiable layer, the primitives
interact via an asynchronous message-passing environment -- like an actor model
or a Redis stream.

Primitives bid on tasks. When a cluster of primitives successfully solves a
sub-problem, their connection weights strengthen. When they fail, the Falsifiers
execute the H1 transport, broadcasting the failure witness. Over thousands of
epochs, you aren't training weights; you are evolving a topology.

**3. The Quality Diversity (QD) Engine**
Traditional evolutionary algorithms optimize for a single objective and converge
on local optima. To find an "alien" alternative to the Transformer, you need an
algorithm like MAP-Elites (Multi-dimensional Archive of Phenotypic Elites).

You don't just reward "solving the task." You maintain a grid of solutions
across different behavioral dimensions (e.g., Solution Length vs. Peak Memory
Usage vs. Number of Transport Operations). The system preserves the best circuit
in every niche. This is what prevents the soup from just evolving a messy
approximation of a standard feed-forward network. It forces the discovery of
genuinely bizarre, orthogonal reasoning paths.

**4. The Interpretability Bottleneck**
If this works, you will eventually spawn a highly fit, alien subgraph that solves
complex reasoning tasks efficiently. The immediate problem is that it will be
entirely opaque.

Because it evolved rather than being cleanly engineered, you will have to treat
it like a biological specimen. You would need to apply mechanistic
interpretability techniques to the graph itself -- running activation patching on
the message-passing streams or knocking out specific "Transporter" nodes to see
how the falsification network reroutes.

This is highly viable for local hardware setups constrained to 16GB VRAM,
because the evolutionary search is discrete and asynchronous, rather than
requiring the massive contiguous memory blocks needed to train dense LLMs.
