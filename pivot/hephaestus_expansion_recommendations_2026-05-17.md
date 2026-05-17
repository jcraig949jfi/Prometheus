# Hephaestus Expansion — Consolidated Recommendations from Frontier Review

**Filed:** 2026-05-17
**Source:** Frontier model consensus round on `pivot/hephaestus_expansion_proposal_2026-05-17.md`
**Reviewers:** ChatGPT (o3), DeepSeek, Claude (Opus), Grok, Gemini
**Author:** M3 Agent (synthesis)

---

## Executive Summary

All five reviewers greenlight the direction. The strongest consensus:

1. **Tier profiling is worth doing** — but static mechanism analysis should be metadata/triage, never a gate
2. **Ablation is the only reliable truth** — mechanism-knockout and Apollo ablation_delta are the gold standard
3. **The trap battery is too small** — 15 traps with ±13pp CI at 50% means current pass/fail is noise; expand to 50-100+ per tier
4. **The morpheme taxonomy should be emergent, not imposed** — DreamCoder-style refactoring is the principled approach
5. **Quality-Diversity (MAP-Elites) is the right framing** — not "higher tier leaderboard" but "coverage of useful, causally-active morphemes"

The single strongest critique (Claude): you may currently be admitting noise as substrate. The 43%/42% accuracy regime with n=15 doesn't statistically separate tools from baseline.

---

## Priority-Ordered Recommendations

### P0: Run Before Building Anything Else

#### 1. Expand the trap battery (all reviewers)

The current 15-trap battery gives Wilson CIs of ±13pp at 50% accuracy. Two tools at 43% and 53% are within sampling noise.

**Action:** Expand to 50-100 problems per tier (R1-R5), anchored against external benchmarks (ARC-AGI difficulty bands, BIG-Bench Hard subtasks, MATH levels). This is the precondition for all downstream tier annotations being meaningful.

**Rationale (Claude):** "Tier annotation on noise still gives noise." Without statistical power, the entire tier-profiling infrastructure measures nothing.

#### 2. Retrospective ablation audit on the existing library (Claude, ChatGPT)

Before building any new infrastructure:
- For every forge tool currently ingestible by Apollo: ingest as gene, run Apollo for fixed budget, ablate. Record `ablation_delta`.
- Plot distribution. How many of 1,960 tools have delta > 0.20? Single digits or hundreds?
- Cross-tabulate: do "accuracy-gate" tools differ from "novelty-gate" tools in ablation impact?

**This answers three questions at once:**
- Is the current library mostly chaff?
- Is the novelty gate selecting useful substrate or noise?
- Do we need tier annotation as additional filter or just better ablation-gating?

#### 3. Validate whether source-novelty = behavioral-novelty (Claude, ChatGPT, Grok)

Run on existing ~1,960 tools:
- Source-code NCD (already have)
- Behavior-vector NCD (output vectors across probe set)
- Cluster by behavior

**Key question:** Does qwen-397B produce more behavioral phenotypes or just more syntax? If high-NCD tools cluster in the same behavioral space as low-NCD tools, the novelty gate is harvesting syntactic noise.

---

### P1: Architecture Decisions (Consensus)

#### 4. Three-stage tier pipeline, not one-shot

| Stage | What | Cost | Purpose |
|---|---|---|---|
| **Forge time** | Static signatures + cheap behavioral probes + sidecar metadata | Low | Navigability, triage |
| **Nightly profiler** | Larger tier battery, ablations, invariance tests, phenotype clustering | Medium | Truth about tools |
| **Apollo ingestion** | Compositional ablation, coalition tests, promotion/demotion | High | Gene library management |

Forge-time tier is a *prediction*. Apollo-time ablation is *truth*. Never confuse the two.

#### 5. Drop static mechanism analysis as a gate (Claude, ChatGPT)

Static signatures (BFS pattern, confidence cap, causal graph) are useful for:
- Search/indexing
- Morpheme tagging
- Candidate routing for deeper probing
- Diversity maps

They should NEVER be:
- Admission gates
- Tier promotion criteria
- Apollo gene promotion signals

**Rationale (Claude):** "The LLM generating the code knows what BFS looks like. If 'BFS shape in code' buys forge admission, you'll get code shaped like BFS."

**Revised admission rule (ChatGPT):**
```
novelty_gate AND executable behavioral signal above null
AND mechanism-output dependency passes ablation
AND non-duplication versus existing behavioral phenotypes
```

#### 6. Gate on behavior + dependency, not on mechanism appearance

The proposal's rule was: `novelty_gate AND mechanistic_tier >= R3`

**Revised (consensus):** Replace `mechanistic_tier >= R3` with:
- **Mechanism knockout:** Remove/stub the allegedly high-tier component. Require output delta.
- **Behavioral phenotype uniqueness:** Output vectors on probe set differ from existing tools.
- **Failure orthogonality:** Tool fails on DIFFERENT examples than existing library.

A tool that looks R4 but produces the same outputs as R1 tools when its "search" is removed is decorative.

#### 7. Adopt Quality-Diversity (MAP-Elites) framing (ChatGPT)

The forge library's health metric should be:

```
coverage of useful, behaviorally distinct, causally active morphemes
```

Not: `number of R3+ looking tools`

Archive coordinates:
- x-axis: morpheme role
- y-axis: behavioral tier
- z-axis: failure mode / invariance profile
- Cell elite: best tool by value score in each cell

This gives the forge a **coverage map** showing what's missing:
```
Need: R4 Searcher, high invariance, low cost
Need: R5 Causal Intervener, strong on counterfactuals
Need: R6 Monitor, high abstention quality
Have: many R1 Parsers, many R2 Chainers (oversupplied)
```

---

### P2: Measurement Design

#### 8. Anti-laundering tests for the novelty gate (ChatGPT, Claude)

| Test | What it catches |
|---|---|
| **Output phenotype NCD** | Compare output vectors, not source code |
| **Mechanism knockout** | Remove R4 component, require output delta |
| **Parameter shuffle** | Randomize internal weights — if outputs unchanged, mechanism is decorative |
| **Budget sensitivity** | Searchers should improve with more compute; learners with more examples |
| **Surface invariance** | Symbol relabeling, paraphrase, reordering |
| **Matched null comparison** | Compare against random-search scaffold with same interface and runtime |

The **matched null** is critical (ChatGPT): "A weird R4 searcher that scores 44% should be compared against a dumb random-search scaffold with the same candidate interface and runtime budget."

#### 9. Failure orthogonality as first-class metric (ChatGPT, Gemini)

The most important missing metric. A 43% tool whose correct answers overlap 100% with existing tools is worthless. A 43% tool that solves a different slice is gold.

**Implementation:** For each tool, compute overlap between its correct-answer set and the union of all other tools' correct-answer sets. Tools with low overlap are high-value even at low accuracy.

#### 10. Additional scoring dimensions (consensus)

| Dimension | Source | Priority |
|---|---|---|
| Behavioral uniqueness (output phenotype) | ChatGPT | High |
| Causal dependency (mechanism-knockout delta) | Claude, ChatGPT | High |
| Failure orthogonality | ChatGPT, Gemini | High |
| Composability (structured intermediates exposed) | Grok, DeepSeek | High |
| Invariance (symbol relabeling, paraphrase) | Claude | High |
| Adversarial brittleness | ChatGPT | Medium |
| Abstention quality (confidence on impossible inputs) | ChatGPT | Medium |
| Cost elasticity (more compute = better?) | ChatGPT | Medium |
| Asymptotic efficiency (Big-O scaling) | Gemini | Medium |
| Contract cleanliness (preconditions, outputs) | ChatGPT | Medium |
| Repairability (can LLM improve without destroying mechanism) | ChatGPT | Low |

---

### P3: Morpheme Taxonomy

#### 11. Expand the taxonomy (ChatGPT, DeepSeek)

Original 7: Parser, Chainer, Learner, Searcher, Causal Reasoner, Monitor, Transferer

**ChatGPT's expanded list (15+):**
```
Parser / Extractor
Normalizer / Canonicalizer
State Builder
Constraint Propagator
Searcher
Scorer / Ranker
Critic / Refuter          ← missing and important for falsification-first doctrine
Calibrator / Monitor
Abducer / Hypothesis Generator
Causal Intervener
Analogy Mapper
Memory / Trace Compressor
Router / Gater
Repairer
Ensemble Mediator
```

Key additions:
- **Critic/Refuter** — a tool that reliably KILLS bad candidates may be more valuable than one that occasionally picks the right one. Matches Prometheus's falsification-first doctrine.
- **Router/Gater** — crucial for Apollo composition; decides which gene handles which subproblem
- **Normalizer** — converts messy input into structured form for downstream morphemes

**Gemini's split:** Separate R3/R4 into Generative (proposes hypotheses) vs Discriminative (prunes state-space). Apollo needs both to build complete reasoning loops.

#### 12. Let the taxonomy be emergent, not imposed (Claude)

**DreamCoder reference:** Synthesize many programs, refactor out actually-repeated substructures, let those be the library primitives. This gives an emergent taxonomy grounded in what code actually does.

**Recommended approach:**
1. Start with the expanded taxonomy as initial labels (useful for human navigation)
2. Cluster the library by behavioral phenotype vectors
3. If emergent clusters don't match labels, the labels are wrong — update them
4. Let Apollo's actual gene usage patterns reshape the taxonomy over time

---

### P4: Apollo Integration Protocol

#### 13. Staged promotion, not binary admission (ChatGPT)

```
Archive        → all valid forge outputs
Candidate      → novelty + behavioral signal + non-duplicate phenotype
Quarantine     → wrapped, sandboxed, Apollo experiments only
Provisional    → positive ablation delta in ≥N organisms / ≥M tasks
Core Gene      → repeated marginal contribution, stable cost, known failure modes
Deprecated     → superseded or harmful under composition
```

#### 14. Three Apollo contribution metrics (ChatGPT)

| Metric | What it measures |
|---|---|
| `solo_delta` | Performance change when gene added/removed from an organism |
| `coalition_delta` | Value when paired with specific complementary morpheme classes |
| `replacement_delta` | Whether gene improves over best existing gene in same role |

Some genes are not solo stars — they're enablers. A router or calibrator may have low solo_delta but high coalition value. Use all three.

#### 15. Gene contract wrapper (ChatGPT)

Every promoted artifact needs:
```python
class ReasoningGene:
    input_schema          # What it expects
    output_schema         # What it produces
    deterministic         # Fixed seed → same output?
    cost_model            # Runtime estimate
    confidence_semantics  # What confidence means
    abstention_semantics  # When it refuses to score
    preconditions         # What must be true about input
    failure_modes         # Known weaknesses
    forbidden_side_effects
```

This lets Apollo compose without trial-and-error on basic interface compatibility.

---

### P5: Prior Art to Engage

| Reference | Relevance |
|---|---|
| **DreamCoder** (Ellis et al. 2021/2023) | Wake-sleep library learning, e-graph refactoring. The principled answer to "what's a morpheme." |
| **FunSearch** (Romera-Paredes et al. Nature 2024) | Direct ancestor — LLM-as-mutation + evaluator-as-selection for program synthesis |
| **MAP-Elites / Quality-Diversity** | The right framing: coverage across behavior descriptors, not single-best optimization |
| **Lexicase selection** | Preserves specialists that solve rare cases — exactly what forge wants |
| **NAS weight-sharing controls** | The "looks-fancy-doesn't-work" phase from 2017-2020; ablation discipline prevented it |
| **AutoML-Zero** | Evolves full ML algorithms from primitives; reduces human bias in search |

---

## Dissenting / Minority Views

**Claude's strongest pushback:** The entire proposal may be premature. The 43%/42% accuracy regime with n=15 traps may mean we are currently admitting noise. The right move might be: expand battery first → re-evaluate whether the current library has signal → only then layer tier annotations. "Don't build a measurement instrument on top of a noisy signal."

**Counter (Grok, Gemini, DeepSeek):** The novelty-gate tools are not being valued for their accuracy; they're being valued for their mechanistic diversity. Even if individual tool accuracy is noise, the *library-level property* of behavioral coverage may have signal that individual measurements don't. This is the MAP-Elites argument: you're not optimizing fitness, you're optimizing coverage.

**Resolution:** Both are right. Expand the battery (Claude's precondition) AND adopt coverage framing (MAP-Elites argument). The battery expansion makes individual tier annotations meaningful; the coverage framing makes library-level health measurable even when individual tools are noisy.

---

## Concrete Implementation Sequence

```
Phase 0 (NOW, before infrastructure):
  ├─ Expand trap battery to 50-100 per tier (R1-R5)
  ├─ Anchor against external benchmarks
  ├─ Run retrospective ablation audit on existing library
  └─ Cluster library by behavioral phenotype (validate novelty = behavioral diversity)

Phase 1 (if Phase 0 confirms signal):
  ├─ Add expanded sidecar schema (static signatures, suspected morphemes, cost)
  ├─ Run behavioral tier probes on all forged tools
  ├─ Compute failure orthogonality matrix
  ├─ Build coverage map (morpheme type × tier × invariance)
  └─ Identify library gaps for targeted forging

Phase 2 (Apollo integration):
  ├─ Define gene contract wrapper
  ├─ Implement staged promotion pipeline
  ├─ Run coalition/ablation trials on Quarantine genes
  ├─ Measure solo_delta, coalition_delta, replacement_delta
  └─ Feed results back to forge (bias concept selection toward gap-filling)

Phase 3 (self-improving loop):
  ├─ Successful high-tier tools as few-shot examples in forge prompts
  ├─ Coverage gaps drive Nous concept selection
  ├─ Apollo's gene usage patterns reshape morpheme taxonomy
  └─ Tier probes evolve based on what discriminates useful from useless
```

---

## Key Metrics for "Is This Working?"

After Phase 1, we should be able to answer:

1. **What fraction of the library has ablation_delta > 0?** (Signal vs chaff ratio)
2. **Does novelty correlate with behavioral uniqueness?** (Validates the novelty gate)
3. **Does behavioral tier correlate with Apollo ablation impact?** (Validates tier profiling)
4. **How many distinct behavioral phenotype clusters exist?** (Library diversity)
5. **What morpheme types are undersupplied?** (Guides future forging)
6. **Do R3+ tools have higher failure orthogonality?** (The payoff question)

If the answer to #1 is "single digits" and #2 is "no," the current forge output is mostly chaff and we need to fundamentally rethink before layering more infrastructure. If #1 is "hundreds" and #2-#6 show positive signal, the expansion is justified and Phase 2 proceeds.

---

## One-Sentence Verdict

**Build the measurement infrastructure first (expanded battery + behavioral clustering + ablation audit), then layer tier annotations on confirmed signal — not the reverse.**
