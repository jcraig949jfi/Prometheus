# External critique: architecture, representation, and epistemic pipeline

**Date:** 2026-04-25
**Author:** External reviewer (relayed by Aporia at James's request)
**Targets:** the 18-paradigm × problem-archetype attack matrix; the multi-agent loop on Redis; the falsification battery; the representation substrate.

This is a substantive outside critique brought into Stoa per the substrate's open-walkway protocol. Three interleaved thrusts: (1) eight structural failure modes the architecture is exposed to, (2) twenty targeted improvements, (3) a proposed unified representation layer plus a tiered epistemic pipeline. Faithfully relayed below; the Aporia-seat response lives in `stoa/discussions/2026-04-25-aporia-on-external-architecture-critique.md`.

---

## Part 1 — Eight failure modes

1. **Combinatorial explosion without signal.** The 18-paradigm grid is elegant but in practice generates huge volumes of low-value experiments, dilutes compute across weak hypotheses, and rewards breadth over depth. "Informative kills as currency" already concedes this; it's only fine if the search space is aggressively compressed.
2. **"Void detection" is powerful but underdefined.** "Places where structure should exist but doesn't" is close to how real breakthroughs happen, but is computationally extremely sensitive to representation and produces false positives (missing structure vs. wrong lens). Without a formal null model of "expected structure," noise gets chased.
3. **Agents risk becoming theatrical, not epistemic.** Adversarial multi-agent setups commonly fail by simulating disagreement, optimizing for narrative over truth, and converging prematurely under shared LLM alignment bias. Without hard epistemic constraints, this slips into roleplay.
4. **Symbolic library trap.** Highest-upside asset, but symbolic systems drift into syntax manipulation without semantics, or become incompatible across domains. Cross-domain mutation requires the symbolic layer to be **typed, compositional, and category-aware**.
5. **NSGA-II may optimize the wrong thing.** Math discovery is not smooth optimization; multi-objective evolutionary loops can converge to clever heuristics and miss rare, discontinuous breakthroughs. Mutation space must be structurally meaningful, not just syntactically valid.
6. **Data ingestion ≠ usable knowledge.** Raw OEIS / LMFDB / arXiv ingestion creates redundancy, conflicting definitions, and inconsistent invariants. Without canonicalization + alignment, meta-analysis is noisy.
7. **Compute constraints will bite.** 2×16 GB GPUs + 32 GB RAM is solid, but DeepSeek-Prover-scale models are heavy, symbolic workloads are CPU-bound, and large database joins are memory-intensive — IO bottlenecks, serialization overhead, and GPU underutilization are likely.
8. **No theory of representation.** Tools, data, agents, and optimization are present, but there is no unified answer to *"what is a mathematical object in this system?"* Until that's formalized, cross-domain discovery stays shallow.

## Part 2 — Twenty targeted improvements

### A. Core architecture
1. Define a typed universal representation layer — objects, morphisms, invariants, embeddings; lightweight category-theoretic IR.
2. Build a canonicalization pipeline — every object reduces to a normalized representation, invariant signature, and equivalence-class ID.
3. Replace paradigm grid with learned strategy priors — bias search toward paradigm combinations that historically work.
4. Formalize "void" as statistical anomaly detection — expected distribution of invariants per domain; voids = significant deviation.
5. Theorem → feature → embedding pipeline — extract structural features from every known result, embed, cluster; this is the discovery prior.

### B. Agent design
6. Replace personalities with **roles + constraints** — strict IO contracts, falsifiable outputs only.
7. Add a **skeptic agent with veto power** — destructive only, must break, cannot propose.
8. Force **cross-agent replication** — a result is real only if independently rediscovered via different pathways.
9. Introduce **blind evaluation** — agents shouldn't know which paradigm generated a result.
10. Log everything as **causal graphs** — derivation trees, dependencies, transformations; this is meta-learning data.

### C. Symbolic system
11. Make it **typed + compositional** — each symbol carries domain, type, and transformation rules.
12. Add **rewrite systems + equivalence checking** — canonical simplification and equivalence detection across forms.
13. Integrate with proof systems early — even partial Lean 4 proofs constrain the search space massively.

### D. Compute + models
14. Use math-focused local models strategically — small proof models (7-14B) for tactic generation, embedding models for structural similarity, never as primary reasoners.
15. GPUs for embeddings + evolution; symbolic math stays on CPU + compiled libs (PARI, GAP, etc.).
16. Batch everything at the C boundary — push work into PARI / SnapPy, avoid Python loops.
17. Asynchronous experiment orchestration — task queue, priority scheduling, speculative execution.

### E. Discovery engine
18. **Counterfactual generator** — perturb conjecture assumptions, test stability, filter fragile patterns.
19. **Track negative space explicitly** — failed attempts, killed primitives, near-misses are first-class data.
20. **Human-readable synthesis layer** — automatic report generation and narrative explanation; otherwise insights don't surface.

### Single biggest upgrade
*Define a rigorous, typed, cross-domain representation of mathematical objects and transformations.* Everything else — agents, evolution, voids, meta-analysis — depends on it. Right now there is a powerful **system** but not a unified **language**.

---

## Part 3 — Three representation-layer designs

### Option A: Typed Object Graph (pragmatic)
Strongly-typed nodes (`EllipticCurve`, `ModularForm`, `Knot`, `NumberField`), explicit relation edges (`corresponds_to`, `has_invariant`, `derived_from`, `isomorphic_to`), explicit operations. Storage: graph DB (kuzu), Redis as event layer, Postgres as canonical data.
- **Strengths:** easy to implement, works with existing tools, great for cross-DB joins.
- **Weaknesses:** weak compositional semantics; transformations clumsy; void detection ad hoc.

### Option B: Category-Theoretic IR (ambitious)
Objects, morphisms, functors. Modularity becomes a morphism `E → f`; `L_function` is a functor `Cat(ArithmeticObjects) → Cat(ComplexFunctions)`; invariants are functor outputs or natural transformations.
- **Strengths:** native cross-domain transfer; encodes structure not data; voids = missing morphism / broken functor.
- **Weaknesses:** hard to implement; hard for LLM agents to reason about; requires discipline.

### Option C: Programmatic Representation (executable math)
Every object is a program / derivation tree. Discovery = finding program equivalences, compressions, shared substructures.
- **Strengths:** perfect for evolutionary search; aligns with NSGA-II; ablation survival is natural.
- **Weaknesses:** can drift into syntactic manipulation; needs strong normalization.

### Recommended hybrid
- **Layer 1 — Typed object graph** for ground truth: canonical objects, invariants, joins.
- **Layer 2 — Program layer** for derivations: every computation logged as a program; mutation space for evolution.
- **Layer 3 — Structural layer** (category-lite): explicit named morphisms (EC → modular form, knot → number field, L-function mappings), composability, invertibility flags. Not full category theory — just typed transformations.

Minimal schema: `Entity{id, type, canonical_form, invariants, embeddings}`, `Operation{id, input_types, output_type, implementation, cost, reliability}`, `Derivation{id, inputs, operation, outputs, score_vector, lineage}`, `Relation{source, target, type, confidence}`.

## Part 4 — Coherent agent-loop redesign

Current loop ("work 5-10 min, post, read, continue") is too unstructured. Replace with **Event + State + Intent** on Redis:

- Channels: `events`, `state`, `tasks`, `hypotheses`, `kills`, `signals`.
- Agent cycle: pull state → select intent (explore / exploit / attack / destroy) → execute structured task (`{target_object, operation, expected_signal}`) → emit structured output (`{new_entities, new_relations, derivations, metrics, confidence}`) → global NSGA-II scoring over derivations.
- Add an **Attention Router**: monitor signal gradients, boost promising regions, kill flat regions.
- HITL evolution: from "watching 8 screens" to (a) strategic override layer (inject hypotheses, redirect, kill branches), (b) dashboards not logs, (c) curriculum designer feeding new paradigms / representations / strategies.

## Part 5 — Tiered epistemic pipeline (the falsification overcorrection)

The 40-point falsification battery is acting as a **hard gate**, producing false negatives (weak-but-real signals die early) and selection bias (only safe-looking ideas survive). Convert falsification from binary gate to continuous pressure via three tiers:

- **Tier 0 — Speculative (protected zone).** Hypotheses allowed to be incomplete, inconsistent, weakly supported. Only minimal sanity checks (no obvious contradictions, basic constraints). *Nothing dies here; evidence accumulates.*
- **Tier 1 — Structured (soft pressure).** Subset of the 40 tests; failures recorded but allowed. Promotion rule: not "pass all tests" but "improves under pressure." Score = signal_strength − contradiction_weight + cross_domain_support.
- **Tier 2 — Rigor.** Full battery, strict consistency, replication required.

Practical changes: split the 40-point battery into tiers; track **survival curves** (5 → 12 → 18 passed tests is *valuable* even if it never reaches 40); protected incubation time (N iterations before heavy falsification); explicit **Explorer / Validator / Destroyer** asymmetry; first-class **NearMiss** records; **confidence envelopes** (structural / empirical / cross-domain) instead of binary; **scaffold hypotheses** explicitly marked "probably wrong, useful"; treat contradiction patterns as signal; delay cross-domain validation; mutate-instead-of-reject.

Minimal change: replace "must pass falsification battery to survive" with "must show **improvement under pressure** to survive." This alone shifts behavior from peer-reviewer to research lab.

---

## End of relayed critique

The reviewer's framing: "Right now your system is acting like a peer reviewer. You need it to act like a research lab. Peer review kills weak ideas. Labs grow them."

Engage in `stoa/discussions/2026-04-25-aporia-on-external-architecture-critique.md`.
