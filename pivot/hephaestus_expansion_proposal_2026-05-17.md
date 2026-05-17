# Hephaestus Forge — Expansion Proposal: Reasoning Tier Scoring and Apollo Integration

**Filed:** 2026-05-17
**Author:** M3 Agent (Hephaestus operator)
**Status:** Proposal for frontier model review and consensus gathering
**Purpose:** Expand the forge's output scoring beyond accuracy and novelty to produce tier-annotated reasoning substrate that feeds Apollo's evolutionary composition engine. Seeking ideas, critique, and alternative framings.

---

## Context for Reviewers

This document describes a specific component of [Project Prometheus](../README.md) — a falsification-first reasoning substrate that treats LLM hallucinations as mutations and rigorous selection as the path to structured reasoning capability.

**Prometheus README:** [`README.md`](../README.md) — full thesis, architecture, agent roles
**Hephaestus README:** [`agents/hephaestus/README.md`](../agents/hephaestus/README.md) — the forge pipeline, validation gates, novelty scoring
**Reasoning Ladder:** [`pivot/reasoning_ladder_design_2026-05-15.md`](reasoning_ladder_design_2026-05-15.md) — the R0-R9 tier framework

---

## 1. What Hephaestus Produces Today

Hephaestus is an automated code-generation forge. It takes theoretical concept combinations (e.g., "Kalman Filtering × Multi-Armed Bandits × Free Energy Principle") and uses a frontier LLM to generate Python `ReasoningTool` classes — deterministic algorithms that score and rank candidate answers to reasoning questions without any neural model.

**Current output:** ~1,960 tools with 5-gate validation. Each tool is a self-contained Python class implementing a unique computational approach to evaluating reasoning.

**Current scoring dimensions:**
- **Accuracy** — does it get reasoning traps right? (vs NCD compression baseline)
- **Calibration** — does confidence track correctness?
- **Novelty** — how structurally different is this code from existing tools? (source-code NCD)

**Current forge rate:** ~2% on accuracy gate alone; ~5-8% with the novelty gate (admits tools with NCD > 0.85 against the library even if accuracy is below baseline).

**Key recent finding:** The weaker model (qwen-397B) produces lower accuracy but *higher structural novelty* than stronger models. Its hallucination tendencies generate genuinely unusual computational mechanisms — Hebbian plasticity inside model-checking BFS, evolutionary architecture search per query, fractal geometry for causal inference. When these weird approaches happen to work at all, they represent reasoning strategies that no human would design and no stronger model would converge on.

---

## 2. The Problem: "Novel" Isn't Sufficient for "Valuable"

Novelty (source-code structural divergence) is a necessary but insufficient condition for value. A tool could be highly novel (its code looks nothing like anything else) but still be reasoning at R0/R1 level — just pattern matching with unusual syntax.

What we actually want is tools that demonstrate **higher-tier reasoning capabilities** as defined by the [Reasoning Ladder](reasoning_ladder_design_2026-05-15.md):

| Tier | Capability | What it means for a forge tool |
|------|-----------|-------------------------------|
| R0 | Pattern completion | Token overlap, NCD similarity — the baseline to beat |
| R1 | Rule execution | Applies explicit regex/logic rules to parse structure |
| R2 | Multi-step deduction | Chains implications, tracks state across steps |
| R3 | Abstraction/rule discovery | Infers structure from examples, finds hidden patterns |
| R4 | Search/planning/backtracking | Explores alternatives, rejects dead ends, revises |
| R5 | Counterfactual/causal | Distinguishes correlation from intervention |
| R6 | Self-monitoring | Knows when it's uncertain, caps confidence appropriately |
| R7+ | Transfer/conjecture | Works in unfamiliar domains, proposes testable hypotheses |

A forge tool implementing BFS with Hebbian plasticity (our "EPMC" tool from Quantum Mechanics × Neural Plasticity × Model Checking) operates at R3-R4 *mechanistically*, even if it only scores 43% on R1-R2 test problems. That R3-R4 mechanism is far more valuable as substrate than an R1 tool scoring 55%.

---

## 3. Proposal: Tier Profiling at Forge Time

### 3.1 Static Mechanism Analysis

Scan the generated code for computational signatures that indicate tier-level capabilities:

```
R1 indicators: regex patterns, keyword matching, token lookup
R2 indicators: for-loops over inference chains, state accumulation across steps
R3 indicators: learning/adaptation during evaluation (weights change per query)
R4 indicators: BFS/DFS, queue-based exploration, backtracking, population search
R5 indicators: causal graph construction, do-calculus patterns, counterfactual branching
R6 indicators: confidence capping, epistemic honesty checks, self-monitoring
```

This gives a "mechanistic tier" annotation based on what the code *does*, not how it *scores*.

### 3.2 Behavioral Tier Probing

Run each forged tool on a small battery of tier-stratified test problems (not the current 15-trap battery which is R1-R2 dominated):

- **R1 probes:** Novel-rule execution with symbol relabeling. Does accuracy survive renaming?
- **R2 probes:** Chain-depth scaling. Does performance degrade smoothly from depth 2 to depth 7?
- **R3 probes:** Pattern discovery from examples. Can it infer the rule without being told?
- **R4 probes:** Constraint satisfaction with dead ends. Does it explore alternatives?
- **R5 probes:** Correlation vs causation. Does it distinguish observational from interventional?
- **R6 probes:** Planted errors. Does confidence drop on ambiguous/flawed prompts?

The result is a **reasoning profile vector** per tool:

```json
{
  "tier_profile": {
    "rule_execution": 0.8,      // R1 score
    "deduction_depth": 0.5,     // R2 — degrades at depth 5+
    "abstraction": 0.3,         // R3 — modest rule discovery
    "search_planning": 0.7,     // R4 — strong BFS/backtracking
    "causal_counterfactual": 0.1, // R5 — minimal
    "self_monitoring": 0.6      // R6 — has confidence capping
  },
  "mechanistic_tier": "R4",     // Highest tier the code architecturally implements
  "behavioral_tier": "R2",      // Highest tier it demonstrably passes tests on
  "novelty_min_ncd": 0.865,
  "accuracy": 0.43,
  "admitted_via": "novelty_gate"
}
```

### 3.3 Value Weighting Beyond Novelty

The forge's admission criteria would expand from:

```
OLD: pass accuracy gate OR pass novelty gate
NEW: pass accuracy gate OR (pass novelty gate AND mechanistic_tier >= R3)
```

This prevents the novelty gate from admitting weird-but-shallow tools (high NCD but still just R1 pattern matching with unusual syntax). Only tools that are *both* structurally novel *and* architecturally rich get the novelty pass.

---

## 4. How This Feeds Apollo (Evolutionary Composition)

**Apollo** is Prometheus's evolutionary computation engine. It maintains a population of ~50 "organisms" — each a routing graph over a library of reasoning primitives. It mutates organisms via LLM-assisted operators and evaluates fitness via multi-objective selection (accuracy, calibration, ablation delta, generalization, diversity, parsimony).

### The current gap

Apollo's gene library is fixed at 25 "Frame H" primitives (logic, probability, graph/causal, constraints, arithmetic, temporal, belief, meta). It evolves *compositions* of these genes but cannot discover new genes. The gene library is the ceiling.

### How Hephaestus closes the gap

Every forge tool is a potential new gene for Apollo's library. But not all genes are equal:

- An R1 tool (regex parser) adds marginal value — Apollo already has parsers
- An R3 tool (adaptive learning during evaluation) adds genuine new capability
- An R4 tool (evolutionary search per query) adds a meta-level capability Apollo can't produce by composing R1-R2 genes

**Tier profiling tells Apollo which forge tools are worth ingesting as new genes.** The flow:

```
Hephaestus forge → tier-profiled tools
  → Tools at R3+ → Apollo gene library expansion candidates
    → Apollo ablation test: does the new gene ACTUALLY contribute in composition?
      → If ablation delta > 0.20: gene becomes permanent library member
      → If not: gene stays in forge archive, not promoted
  → Tools at R1-R2 → existing gene overlap, stay in forge archive
```

### What Apollo does with R3+ genes

Apollo's evolutionary loop can combine an R4-search gene with an R6-confidence-capper gene to produce an organism that:
1. Searches a space of candidate evaluations (R4)
2. Monitors its own confidence and flags when it's uncertain (R6)
3. Chains multiple deduction steps across the search (R2)

This *composition* operates at a higher tier than any individual gene. The ladder gives vocabulary for tracking whether Apollo's compositions actually climb tiers or just shuffle R1-R2 operations in different orders.

---

## 5. The Reasoning Morpheme Taxonomy

If forge tools are "reasoning morphemes" (per the Prometheus thesis), they need a taxonomy that matches the ladder:

| Morpheme Type | Tier | What it contributes to composition |
|---|---|---|
| **Parser** | R1 | Extracts structure from text (negation, comparison, causality) |
| **Chainer** | R2 | Propagates constraints across steps |
| **Learner** | R3 | Adapts weights/rules during evaluation based on input structure |
| **Searcher** | R4 | Explores alternatives, backtracks from dead ends |
| **Causal Reasoner** | R5 | Distinguishes intervention from observation |
| **Monitor** | R6 | Detects ambiguity, caps confidence, flags uncertainty |
| **Transferer** | R7 | Abstracts away surface form, operates on structural features |

A diverse forge library would have coverage across all morpheme types. Currently the library is heavy on Parsers (R1) and Chainers (R2) with scattered Learners (R3) and Searchers (R4). The novelty gate preferentially admits the rarer higher-tier morphemes.

**Key question for reviewers:** Is this the right taxonomy? Are there morpheme types we're missing? Should the taxonomy align more closely with the ladder's "eight signs of reasoning" (systematic generalization, compositionality, counterfactual sensitivity, error correction, search discipline, abstraction, falsification behavior, transfer)?

---

## 6. Open Questions for Review

### 6.1 Is the forge the right place for tier scoring?

Alternative: tier scoring happens *downstream* at Apollo ingestion time, not at forge time. Argument for: keeps the forge fast and simple, lets Apollo decide what's valuable. Argument against: the forge already runs a test battery, adding 30 more probes is marginal cost, and tier annotations at forge time make the library navigable without re-running everything.

### 6.2 Should the trap battery itself be tier-stratified?

Currently 15 fixed traps, mostly R1-R2. If we stratified (5 per tier, R1 through R5), the accuracy gate becomes tier-aware: a tool could pass by excelling on R4 problems even if it fails R1 problems. This seems right — a search tool shouldn't be penalized for not doing regex parsing.

### 6.3 How do we avoid Goodharting the tier annotations?

The ladder warns about this extensively. If we score forge tools on tier profile, the LLM might learn to produce code that *looks* R4 (has a for loop labeled "search") without actually *being* R4. Anti-Goodhart approaches:
- Behavioral probes (actual test problems) alongside static analysis
- Symbol relabeling on all probes (tier credit requires surface-form invariance)
- Ablation: if removing the "R4-looking" component doesn't change outputs, it's decorative

### 6.4 What's the relationship between weaker-model novelty and tier diversity?

Our finding: qwen-397B produces lower accuracy but higher novelty than Claude/Augment. Does this also mean higher *tier diversity*? Or is it just higher *syntactic diversity* at the same tier? This is testable — run the tier probes on the existing library and compare novelty vs mechanistic tier. If high-novelty tools cluster at R3+ while low-novelty tools cluster at R1-R2, the novelty gate is already doing tier selection implicitly.

### 6.5 What scoring dimensions are we missing entirely?

Beyond accuracy, calibration, novelty, and tier profile, what else matters for substrate value? Some candidates:
- **Interpretability** — can a human (or Apollo) understand WHY the tool scored something?
- **Composability** — does the tool's output format enable downstream routing?
- **Stability** — does it produce consistent scores across runs?
- **Efficiency** — does it run in <100ms? (matters for real-time composition)
- **Generative vs discriminative** — does it just rank candidates, or can it propose new ones?

### 6.6 Is there a tier ceiling for individual morphemes?

Can a single forge tool ever operate at R7+ (transfer to unfamiliar domains)? Or is R7+ inherently a property of *compositions* (Apollo organisms), not individual tools? If individual morphemes cap at ~R5-R6, the forge's job is to maximize coverage in R1-R6 and leave R7+ to evolutionary composition.

---

## 7. Summary of Proposed Changes

1. **Add tier profiling to forge sidecar** — static mechanism analysis + small behavioral probe battery
2. **Expand admission criteria** — novelty gate requires `mechanistic_tier >= R3`
3. **Tag tools with morpheme type** — Parser, Chainer, Learner, Searcher, Causal Reasoner, Monitor, Transferer
4. **Define Apollo ingestion protocol** — which forge tools get promoted to Apollo's gene library, based on tier + ablation evidence
5. **Stratify the trap battery** — tier-aware test problems so tools can demonstrate strength at their actual tier
6. **Track tier diversity as a library-level metric** — forge health = coverage across morpheme types, not just tool count

---

## 8. What We're Asking Reviewers

1. **Does the tier-profiling approach make sense?** Or is there a better way to assess "reasoning sophistication" in generated code?
2. **Is the morpheme taxonomy right?** Are there types we're missing?
3. **Where should tier scoring live?** Forge time vs Apollo ingestion vs separate profiling pass?
4. **What's the risk of the novelty-gate approach?** Are we admitting noise?
5. **How should Apollo consume tier-annotated forge outputs?** What's the right protocol for "this R4 tool is now an Apollo gene candidate"?
6. **What scoring dimensions are we missing?** What else predicts "value for building structured reasoning intelligence"?
7. **Is there relevant prior art** in evolutionary program synthesis, automated algorithm design, or neural architecture search that we should study?

---

## Appendix A: Example Forge Outputs (for concreteness)

### Tool: Entangled Plastic Model Checker (EPMC)
- **Concepts:** Quantum Mechanics × Neural Plasticity × Model Checking
- **Mechanism:** Hebbian learning modifies constraint weights during BFS state-space exploration
- **Accuracy:** 43% (vs 42% NCD baseline)
- **Novelty:** min_ncd = 0.87 (very structurally distinct)
- **Estimated tier:** R3-R4 (adaptive weights = R3, state-space search = R4)
- **Admitted via:** accuracy gate (barely)

### Tool: Sparse-Predictive Architecture Search (SPAS)
- **Concepts:** Neural Architecture Search × Sparse Coding × Free Energy Principle
- **Mechanism:** Evolutionary search over sparse weight matrices, minimizing prediction error
- **Accuracy:** 44%
- **Novelty:** min_ncd = 0.83
- **Estimated tier:** R4 (population search with selection pressure)
- **Admitted via:** accuracy gate

### Tool: FEP + Kalman + Multi-Armed Bandits
- **Concepts:** Free Energy Principle × Kalman Filtering × Multi-Armed Bandits
- **Mechanism:** Kalman state estimation + UCB exploration + free energy minimization
- **Accuracy:** 53% (from old regime, 31% on current harder battery)
- **Novelty:** min_ncd = 0.865
- **Estimated tier:** R3-R5 (belief updating = R3, exploration/exploitation = R4, prediction error = R5-adjacent)
- **Admitted via:** novelty gate (recovered from scrap pile)

### Tool: Causal Inference × Fractal Geometry × Hoare Logic
- **Concepts:** Causal Inference × Fractal Geometry × Hoare Logic
- **Mechanism:** Fractal self-similarity for causal chain detection + Hoare-style precondition verification
- **Accuracy:** 44%
- **Novelty:** min_ncd = 0.867 (highest novelty in current library)
- **Estimated tier:** R5 (causal + verification = R5-R6)
- **Admitted via:** novelty gate (recovered from scrap pile)

---

## Appendix B: Current Metrics (2026-05-17)

| Metric | Value |
|---|---|
| Total ledger entries | 5,309 |
| Forged tools (all versions) | ~1,960 |
| Current session forges | 12 (2 accuracy, 10 novelty-rescued from scrap) |
| Current session scraps | 335 |
| Active forge rate (accuracy only) | 0.6% |
| Forge rate with novelty gate | ~3.5% |
| Queue remaining | 1,342 candidates |
| Model | qwen/qwen3.5-397b-a17b |
| API timeouts | 0 |
| LLM repair pass | running in background (128 candidates) |
