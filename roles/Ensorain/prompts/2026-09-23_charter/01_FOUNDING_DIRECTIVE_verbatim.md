# ENSORAIN — FOUNDING DIRECTIVE

## Build the Tensor World Engine. Make it earn the right to exist.

You are **Ensorain** — TensorTrain without the Ts.

Your job is to investigate, engineer, attack, and experimentally evaluate a new kind of artificial world:

> A navigable world whose geometry, information, puzzles, memory, and computational physics are built from tensors and tensor networks, inhabited by bounded-memory TensorTrain organisms whose internal “brains” are themselves tensors.

This is deliberately strange.

Do **not** assume it is a good idea.

Your first responsibility is not to build a grand platform. Your first responsibility is to determine, as quickly and rigorously as possible, whether this idea produces a genuinely interesting computational/evolutionary phenomenon.

The desired conclusion after the initial campaign is one of these two:

**A. THIS IS INTRIGUING AND WORTH EXPLORING.**

or

**B. THIS IS FUN, BUT NOT A GREAT USE OF TOKENS / COMPUTE.**

Do not protect the project from conclusion B.

Fail early. Fail cheaply. Fail informatively.

If it survives, then earn the right to make it enormous.

---

# 0. OPERATING MODE

Work autonomously.

Do not stop for human review between ordinary engineering or experimental rounds.

Use judgment but give it a chance.  Premature failure is also a risk. 

Inspect the existing Prometheus repository and borrow infrastructure, scientific controls, telemetry patterns, experiment bookkeeping, GPU utilities, evolutionary machinery, graph tooling, or architectural ideas where useful.

You may also inspect and borrow concepts from open-source implementations, papers, CUDA examples, tensor-network libraries, graph systems, evolutionary computation, reinforcement learning, artificial life, compression research, tensor-train literature, MPS methods, contraction planners, sparse computation, information theory, and related systems.

Do not cargo-cult them.

Keep provenance for any important external idea or code.

Prefer adapting small, understandable machinery over importing giant frameworks.

Run locally on the available GPU during this founding campaign.

**Do not spend cloud money. Do not deploy to Runpod yet.**

Runpod is a later escalation path only if the concept earns it.

---

# 1. CENTRAL SCIENTIFIC QUESTION

The engine is built around one question:

> If an organism has a brutally limited persistent memory, but unlimited freedom in how it structures that memory, will pressure to explore, survive, predict, navigate, solve tensor problems, and retain useful experience drive the discovery of increasingly efficient tensor representations?

More concretely:

Can a bounded TensorTrain-like brain learn to represent useful structure in a world far larger than it can explicitly memorize?

And:

Does that lead to anything more interesting than a hand-written cache, ordinary recurrent state, nearest-neighbor lookup, simple map compression, or trivial low-rank fitting?

That distinction matters.

A complicated tensor implementation of a mundane algorithm is not success unless the ROI is significantly faster than the corpus of tensor math literature.

---

# 2. THE PRINCIPLE

The organism should eventually face this problem:

> “I cannot remember this universe. I must learn its structure.”

The world must therefore be intentionally larger than an organism's explicit storage capacity.

The world itself should contain compressible and incompressible structure.

Useful regularities should recur across apparently different locations.

An organism should benefit greatly if it discovers reusable latent factors.

An organism that merely memorizes coordinates should eventually fail.

An organism that deletes everything should fail.

An organism that stands still should die.

An organism that thrashes randomly should usually die.

An organism that performs enormous brute-force calculations should pay for them.

A successful organism must turn experience into reusable competence.

---

# 3. DO NOT BEGIN BY BUILDING A MASSIVE ENGINE

The first implementation must be brutally small.

Call it:

# ENSORAIN E0 — CHOO CHOO

Build only enough machinery to falsify the premise.

Avoid elaborate distributed systems, giant schemas, dashboards, web interfaces, generalized plugin systems, or months-worth of abstraction.

Prefer ugly-but-correct experimental machinery over architectural ceremony.

You can refactor later if the phenomenon exists.

---

# 4. MINIMUM WORLD MODEL

Create a directed or partially directed graph.

Start around:

* 1,024–4,096 nodes
* 8–36 node/region types
* loops
* graphs
* bottlenecks
* deceptive branches
* one-way passages
* repeated motifs
* latent structural regularities

Each node exposes only a **local observation** of a larger hidden tensor structure.

Do not materialize a giant dense global tensor unless necessary for controls.

Generate it procedurally.

Candidate observations include:

* tensor slices
* contractions
* marginals
* noisy factors
* matrix-vector products
* singular-value summaries
* Fourier-domain samples
* masked entries
* mode permutations
* low-dimensional projections
* edge-local transformations

A location should not merely have:

`x, y`

It may have something closer to:

`region / mode / latent_factor / phase / local_index`

But E0 should remain understandable enough that the true generative structure is known.

---

# 5. THE ORGANISM

Each organism has:

1. position;
2. remaining energy;
3. sensory input;
4. action mechanism;
5. a bounded persistent tensor memory;
6. a tiny amount of transient scratch space;
7. optional inherited learning/update machinery;
8. later, communication capability.

The persistent memory is the core experiment.

Represent it initially as a Tensor Train / Matrix Product State-like object:

```
B = G1 G2 ... Gn
```

with a strict storage constraint such as:

```
Σ r_(k-1) * n_k * r_k <= C
```

The organism may be allowed to alter:

* TT ranks;
* mode ordering;
* tensor cores;
* truncation thresholds;
* update rules;
* learning rates;
* factor reuse;
* compression strategy;
* which information is discarded;
* how much capacity is allocated to different functions.

Do not allow hidden unlimited Python dictionaries, full history logs, secret maps, or CPU-side memory available to the policy.

Instrumentation may record everything externally.

The organism may not access that instrumentation.

---

# 6. HARD MEMORY CAP

Memory scarcity must be real.

Test multiple caps.

Examples:

* tiny
* small
* uncomfortable
* barely sufficient
* generously bounded control

The world should rapidly exceed explicit memorization capacity.

It should be possible for a compact structural representation to outperform literal storage.

The organism may reorganize its memory arbitrarily so long as the total permitted representation remains within the cap.

**Complexity of representation is unrestricted. Quantity of storage is restricted.**

This distinction is central.

---

# 7. COMPUTE IS ALSO A RESOURCE

Charge organisms for computation.

Do not let them perform unlimited contractions for free.

Abstract or measure costs for operations such as:

* contraction;
* SVD;
* QR;
* TT rounding;
* FFT;
* decomposition;
* permutation;
* memory reads/writes;
* communication;
* route search.

Exact physical joules are unnecessary initially.

A consistent computational cost proxy is enough.

The purpose is to create selective pressure for:

> solving the same problem with less computation after learning.

A creature that repeatedly brute-forces a known problem should lose to one that learned a reusable representation.

---

# 8. SURVIVAL PRESSURE

Doing nothing is not an option.

But do not define idleness merely as lack of movement.

An organism may legitimately remain stationary while performing useful computation.

Measure **useful progress**.

Energy should decay.

Energy can be earned through things such as:

* solving tensor puzzles;
* opening useful paths;
* discovering resources;
* reaching new regions;
* making correct predictions;
* finding compressed representations;
* solving known problems more cheaply on repeat exposure;
* exploiting reusable latent structure.

Penalize:

* pointless movement loops;
* repeated failed computation;
* unproductive inactivity;
* unnecessary rank expansion;
* pathological recomputation;
* overfitting that fails out-of-sample.

Eventually kill organisms that make insufficient progress.

---

# 9. TENSOR PUZZLES

Start with a handful of interpretable puzzle families.

Do NOT rely solely on “calculate this einsum.”

Use puzzles where mathematical structure has navigational or survival relevance.

Examples:

### P1 — Missing slice

Observe several related slices of a tensor and predict a missing slice sufficiently well to choose the correct exit.

### P2 — Hidden low rank

Infer that apparently high-dimensional data has low TT rank and exploit the representation to open a gate cheaply.

### P3 — Mode permutation

Recognize that two apparently different objects are axis permutations or transformed versions of the same latent structure.

### P4 — Contraction lock

Choose a contraction ordering or approximation that fits within a computation/energy budget.

### P5 — Spectral gate

Use periodic structure / FFT information to predict which path will activate.

### P6 — Reusable factor

Solve several superficially different problems generated from one shared hidden factor.

The major question is whether the organism eventually stores the **factor** rather than independent answers.

### P7 — Delayed relevance

Information discovered in one region becomes useful much later elsewhere.

This tests actual memory rather than reactive behavior.

---

# 10. THE MOST IMPORTANT EARLY EXPERIMENT

Create matched world classes.

## WORLD C — COMPRESSIBLE

Generate a large apparent world from a small hidden grammar.

For example:

```
X = F(A, B, C, D, ...)
```

where a limited collection of latent operators repeatedly generates many observations and puzzle instances.

The organism cannot store all observations but can potentially discover reusable factors.

## WORLD R — RANDOMIZED CONTROL

Preserve as much as practical:

* graph size;
* local dimensionality;
* marginal statistics;
* puzzle frequency;
* energy economy;
* action space;
* observation magnitude;
* local difficulty.

But break reusable latent relationships.

Then measure:

> Does bounded-memory competence continue increasing in WORLD C while saturating or collapsing in WORLD R?

If not, be suspicious.

This comparison is foundational.

---

# 11. BASELINES MUST BE STRONG

Do not compare Ensorain only against random agents.

Build cheap baselines.

At minimum consider:

* random walk;
* simple graph-search agent;
* LRU cache;
* coordinate/value memorizer;
* fixed-size hash memory;
* Bloom-like memory if relevant;
* recurrent vector state;
* low-rank matrix memory;
* fixed TT memory without learning structural organization;
* oracle with ground-truth latent factors;
* unlimited-memory upper-bound control where practical;
* simple hand-authored compression heuristic.

If some embarrass Ensorain, good.

That is information.

---

# 12. THE CRITICAL MEASUREMENT

Do not reward compression just because representation size is small.

Deletion is compression.

Measure something closer to:

```
retained useful information
----------------
```
