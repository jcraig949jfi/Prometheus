# The Tensor Shortcut — Why Prometheus Can Compete Locally

*Design principle: compute the mathematical structure of the concept space directly. Use LLMs only for interpretation, never for search.*

---

## The Asymmetry

Google has Gemini, TPU pods, and billion-dollar infrastructure. They built AlphaEvolve — an evolutionary coding agent that discovers new algorithms by generating program variants with frontier LLMs, testing them, and iterating. It improved Strassen's matrix multiplication algorithm for the first time in 56 years. It works.

We have one consumer GPU, no budget, and a laptop.

We should not compete on their terms. We should compete on ours.

---

## Two Strategies for Exploring the Same Space

### Google's Strategy: Brute-Force Program Evolution

```
Generate program variant (LLM call, ~5 seconds)
  → Execute and test (~1-10 seconds)
  → Score fitness
  → Select survivors
  → Generate more variants
  → Repeat 10,000+ times
  → Discover something

Cost per discovery: thousands of LLM calls
Speed: limited by inference latency
Bottleneck: LLM throughput
Resource requirement: frontier model + massive compute
```

This works because Google can afford to brute-force a massive search space. Each iteration costs pennies, and they have infinite pennies.

### Prometheus's Strategy: The Tensor Shortcut

```
Encode every concept as a mathematical object (once, ~hours)
  → Compute the full interaction tensor (once, ~seconds)
  → Compress via tensor train decomposition (once, ~seconds)
  → Navigate the compressed structure (continuous, ~microseconds per query)
  → Identify structural hotspots (where novel composition exists)
  → Send ONLY the hotspots to LLM for interpretation (~100 calls, not 100,000)
  → Test the interpreted compositions
  → Update the tensor with results
  → Navigate again

Cost per discovery: ~100 LLM calls (vs thousands)
Speed: limited by linear algebra, not inference
Bottleneck: mathematical structure of the concept space
Resource requirement: numpy + tensorly + one CPU
```

This works because the mathematical structure of concept combinations is COMPUTABLE without asking a language model. The outer product of two organisms' feature tensors reveals their interface geometry. The tensor train decomposition reveals which regions have structure. You don't need GPT-4 to tell you that Topology and Immune Systems share boundary-detection properties — the math shows it directly.

---

## Why This Is Not a Worse Version of AlphaEvolve

It's a fundamentally different strategy.

AlphaEvolve searches PROGRAM SPACE — the space of all possible code implementations. This space is enormous, unstructured, and requires LLMs to navigate because programs are symbolic objects that only language models can meaningfully mutate.

Prometheus searches CONCEPT SPACE — the space of mathematical relationships between ideas. This space has COMPUTABLE STRUCTURE. The relationships between Topology and Chaos Theory aren't hidden in natural language — they're revealed by the mathematical properties of both fields. Tensor operations expose this structure at linear algebra speed.

| | AlphaEvolve | Prometheus |
|---|---|---|
| **Search space** | All possible programs | Mathematical concept combinations |
| **Navigation tool** | LLM inference (~seconds/step) | Tensor operations (~microseconds/step) |
| **What's being searched** | Code syntax and semantics | Mathematical structure and interfaces |
| **Bottleneck** | LLM throughput | Concept encoding quality |
| **Cost per candidate** | ~$0.01-0.10 (API call) | ~$0.00001 (tensor operation) |
| **When LLM is used** | Every step (generation) | End only (interpretation of winners) |
| **Scaling** | More LLM calls = more coverage | Better tensor encoding = smarter search |
| **Unique advantage** | Frontier model intelligence | Mathematical structure computation |

---

## The THOR Advantage

Raw tensors explode in memory. A 95-concept space with 50 feature dimensions and triple interactions is 95³ × 50 = ~43 billion entries. That doesn't fit in RAM.

Tensor trains (THOR, TensorLy) compress this to ~3 million entries at rank 10. The compression preserves the structure — you can still navigate, query, and find hotspots in the compressed representation. You can ask "where is the highest unexplored novelty?" and get an answer in milliseconds by traversing the tensor train cores.

THOR goes further than basic tensor trains:
- Multi-GPU distributed decomposition (when you have the hardware)
- Tensor networks (not just trains) for arbitrarily complex multi-way interactions
- Incremental updates — when a new concept is added, update the decomposition without recomputing from scratch
- Physics-inspired algorithms that are numerically stable at high dimensions

The tensor train IS the Lattice. The Lattice IS the navigable map of all concept combinations. Navigation speed is linear algebra speed, not LLM speed.

---

## The Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1: ENCODE (once, then incremental)                   │
│                                                             │
│  Each concept → mathematical organism                       │
│    Real operations (numpy code)                             │
│    Feature vector (30-50 structural properties)             │
│    Type signatures (input/output compatibility)             │
│                                                             │
│  Source: math libraries, forge tools, published algorithms  │
│  Currently: 18 organisms, 81 operations                    │
│  Target: 95+ organisms, 500+ operations                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 2: COMPUTE (seconds, pure CPU/GPU)                   │
│                                                             │
│  Full interaction tensor:                                   │
│    Pairwise: outer product of feature vectors               │
│    Triplewise: einsum contraction                           │
│    Scoring: novelty, complementarity, resonance             │
│                                                             │
│  Compress via tensor train (TensorLy/THOR):                 │
│    Raw: ~43 billion entries                                 │
│    Compressed: ~3 million entries (rank 10)                 │
│    Navigable: query any region in microseconds              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 3: NAVIGATE (microseconds per query)                 │
│                                                             │
│  Find structural hotspots:                                  │
│    Highest unexplored novelty                               │
│    Strongest emergent properties                            │
│    Deepest complementarity between distant fields           │
│                                                             │
│  Filter:                                                    │
│    Top 100 from ~857,000 candidates                         │
│    In under 1 second                                        │
│    No LLM calls required                                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 4: INTERPRET (LLM, only on winners)                  │
│                                                             │
│  Send top 100 candidates to LLM:                            │
│    "These three concepts have this tensor interface.         │
│     The emergent structure shows X. Can this be coded?       │
│     What algorithm would combine these operations?"          │
│                                                             │
│  ~100 API calls instead of ~100,000                         │
│  ~50 minutes instead of ~285 days                           │
│  Cost: ~$1 instead of ~$1,000                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 5: TEST & UPDATE (close the loop)                    │
│                                                             │
│  Execute the interpreted compositions                       │
│  Score: exploration velocity, reasoning improvement          │
│  Update the tensor with results                             │
│  New hotspots emerge from the updated structure             │
│  Navigate again                                             │
│                                                             │
│  The tensor evolves. The landscape changes.                 │
│  The search accelerates.                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## The Design Principle

**Never use an LLM for search. Use tensors for search. Use LLMs for interpretation.**

The mathematical structure of concept combinations is computable. Computing it is fast (microseconds). Navigating it is fast (tensor train traversal). Finding the interesting regions is fast (top-K over compressed tensors).

What's NOT computable is: "given that these three concepts have this mathematical relationship, what does it MEAN? What algorithm does it suggest? How would you explain it to a human?" That's where the LLM adds value — not in searching, but in translating mathematical structure into human understanding and executable code.

This division of labor — tensor for search, LLM for interpretation — is what makes Prometheus competitive on consumer hardware. We don't need frontier models to search. We need linear algebra to search and ANY model to interpret.

---

## What This Means Practically

### Cost Comparison

| Operation | AlphaEvolve | Prometheus |
|-----------|-------------|------------|
| Search 857K candidates | $8,570 (at $0.01/call) | $0 (tensor operations) |
| Interpret top 100 | $1 | $1 |
| Total per full sweep | ~$8,571 | ~$1 |
| Sweeps per dollar | 0.0001 | 1 |

### Speed Comparison

| Operation | AlphaEvolve | Prometheus |
|-----------|-------------|------------|
| Score one candidate | ~5 seconds | ~10 microseconds |
| Score all 857K | ~50 days | ~8.6 seconds |
| Full sweep cycle | weeks | minutes |

### Hardware Comparison

| Requirement | AlphaEvolve | Prometheus |
|-------------|-------------|------------|
| LLM inference | Gemini (frontier, TPU pods) | Any model (local 7B or API, only 100 calls) |
| Tensor computation | Not used | numpy/tensorly/THOR (CPU) |
| GPU required | Yes (massive) | No (CPU for search, GPU optional for acceleration) |
| Minimum viable | Cloud TPU + Gemini API | Laptop with Python |

---

## The Moat

Google will always have bigger models. They will always have more compute. They will always generate more program variants per dollar.

But they're searching program space with language models. We're searching concept space with tensor mathematics. These are different things. Our search is faster on our hardware because we're not doing what they're doing — we're doing something they HAVEN'T done.

When we find a structural hotspot in the tensor, we can THEN use their models (via API, 100 calls) to interpret it. We get the benefit of their intelligence without paying for their search.

The tensor shortcut isn't a workaround for not having a TPU. It's a fundamentally different approach to exploration that happens to be fast on consumer hardware. If Google wanted to do this too, they'd have the same advantage — but they'd need to encode their concepts as mathematical objects first, which they haven't done because brute-force LLM search works for them at their scale.

At our scale, the tensor shortcut is the only viable path. And it might be the better path even at their scale.

---

## Connection to Exploration Velocity

The tensor shortcut makes exploration velocity MEASURABLE and OPTIMIZABLE:

1. **Velocity = hotspots found / time.** Tensor navigation finds hotspots in microseconds. LLM search finds them in seconds.

2. **The tensor updates with every discovery.** When a composition works, the tensor changes. New hotspots appear. Old hotspots disappear. The landscape evolves.

3. **The encoding improves over time.** As Coeus learns which feature dimensions predict successful compositions, the feature encoding gets better. Better encoding = more accurate tensor = smarter navigation = higher velocity.

4. **The concept library grows.** Each new organism adds new dimensions to the tensor. The interaction space expands. But tensor train compression keeps navigation fast regardless of size.

This is the self-improving loop: better encoding → smarter search → more discoveries → better encoding. The acceleration is inherent in the architecture, not dependent on bigger models or more compute.

---

## The North Star, Restated

Build the substrate (the Lattice of mathematical concepts) and the navigation tool (tensor-compressed search) that lets a reasoning system explore the frontier of knowledge at computational speed, not language speed. Use language only for interpretation, never for search. The system's value comes from the mathematical structure it computes, not from the LLMs it calls.

Google's fire burns with fuel (compute). Our fire burns with structure (tensors). Both produce light. Ours is cheaper to maintain.
