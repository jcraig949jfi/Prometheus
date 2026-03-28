# Multi-Strategy Forge: Four Worldviews

*Fixing the monoculture at every stage simultaneously*

---

## The Problem

The forge pipeline applies ONE strategy at every stage:
- Nous: Coeus-weighted sampling (amplifies FEP, starves rare concepts)
- Coeus: Single enrichment template ("use structural parsing, NCD fallback")
- Hephaestus: One code gen prompt → one architecture (NCD + regex)
- CAITL: Same 7 dimensions applied uniformly

Result: 1,928 triples → 357 forged → **19 unique behaviors** (95% redundancy)

## The Fix

Four coherent worldviews, each traversing the full pipeline with its own internal logic. Not four independent knobs — four end-to-end biases that perceive the concept space differently.

---

## The Four Frames

### Frame A: Structural Parser
*"Decompose the question into parts and check constraints"*

| Stage | Strategy |
|-------|----------|
| **Nous** | Coeus-weighted (current default). Favors concepts with positive forge effect. |
| **Coeus** | Current enrichment template. "Use structural parsing, NCD as tiebreaker." |
| **Hephaestus** | Current code gen prompt. Structural emphasis. |
| **CAITL** | Current: strengthen concepts, standardize I/O |

This is what we have now. It produced the 4 minimum covering set tools. Keep it — it works for Tier A parsing traps.

### Frame B: Constructive Computer
*"Build the answer through computation, don't just parse the question"*

| Stage | Strategy |
|-------|----------|
| **Nous** | **Exploration-weighted**: uniform random with diversity cap. Oversample rare concepts (Counterfactual Reasoning, Dual Process Theory, Matched Filtering). Undersample FEP/MechDesign. |
| **Coeus** | **Computation-focused enrichment**: "Implement actual mathematical operations. Solve equations, compute probabilities, trace causal graphs. Do NOT fall back to NCD — if you can't compute the answer, return low confidence." |
| **Hephaestus** | **Computation prompt**: "Your tool must CALCULATE answers. Float comparison, Bayesian posteriors, temporal scheduling, rate problems. At least 40% of score must come from computed results. NCD weight max 10%." |
| **CAITL** | **Constructive pass**: "For each failing category, implement the actual computation. Base rate neglect → Bayes formula. Temporal ordering → topological sort. Rate problems → algebraic solver." |

This targets the Tier A gaps: arithmetic, temporal, causal, compositional.

### Frame C: Dynamics Tracker
*"Reasoning is trajectory evolution — track state across steps"*

| Stage | Strategy |
|-------|----------|
| **Nous** | **Dynamics-biased**: 3x weight on Dynamical Systems, Ergodic Theory, Chaos Theory, Neural Oscillations, Phase Transitions, Active Inference, Reinforcement Learning. |
| **Coeus** | **Dynamics enrichment**: "Model the reasoning as a dynamical system. Track how the answer evolves across premises. Use state vectors, trajectory simulation, convergence detection. Reward stability under perturbation." |
| **Hephaestus** | **Dynamics prompt**: "Your tool must maintain internal state across candidates. Use reservoir dynamics, Lyapunov stability, or Markov chain convergence. Score based on trajectory properties, not static features." |
| **CAITL** | **Trajectory pass**: "Add state-tracking methods. Evaluate candidates as sequences, not atoms. Measure reasoning stability under premise reordering." |

This targets: temporal-sequential gaps, rate-of-change, multi-step chains.

### Frame D: Judgment Calibrator
*"Know what you don't know — epistemic honesty over accuracy"*

| Stage | Strategy |
|-------|----------|
| **Nous** | **Judgment-biased**: 3x weight on Theory of Mind, Metacognition, Epistemology, Dialectics, Abductive Reasoning, Falsificationism. |
| **Coeus** | **Judgment enrichment**: "Detect when the question is ambiguous, unanswerable, or contains a presupposition BEFORE scoring candidates. Return low confidence on genuinely uncertain questions. A tool that says 'I don't know' is more valuable than one that guesses." |
| **Hephaestus** | **Judgment prompt**: "Your tool must classify the QUESTION before evaluating answers. Implement _meta_confidence() that detects presupposition, scope ambiguity, false dichotomy, subjectivity. confidence() must reflect question properties, not answer score." |
| **CAITL** | **Honesty pass**: "For each Tier B category the tool fails, add detection patterns. Optimize for epistemic honesty, not accuracy. A tool that correctly returns 0.2 confidence on an ambiguous question is better than one that returns 0.8." |

This targets: complex ToM, strategic deception, argument strength, confidence calibration.

---

## Implementation

### Option 1: Sequential (simplest)
Run Frame A for N hours, then Frame B, then C, then D. Each frame gets its own forge_v{N} directory. After all four, merge the unique tools.

### Option 2: Interleaved (balanced)
Rotate frames every forge attempt: A, B, C, D, A, B, C, D... Each attempt uses the frame's full stack (Nous weights, Coeus enrichment, Hephaestus prompt). Tools from all frames compete on the same battery.

### Option 3: Parallel (fastest)
Run 4 Hephaestus instances simultaneously, each with a different frame. Requires 4 API streams but maximizes throughput.

### Recommended: Option 2 (Interleaved, weighted rotation)
One Hephaestus instance, cycling through frames with weighted allocation:

| Frame | Allocation | Rationale |
|-------|-----------|-----------|
| A (Structural) | **10%** | Control only — 1,928 attempts already saturated this space |
| B (Constructive) | **35%** | Largest gap cluster, clearest success criterion |
| C (Dynamics) | **30%** | Highest-risk/highest-reward, needs more attempts for low yield |
| D (Judgment) | **25%** | Tier B already at 0.993, needs accuracy floor to be useful |

Frame selection: `frame = weighted_choice(['A','B','C','D'], weights=[10,35,30,25])`

---

## What Changes in Code

### Nous (`nous.py`)
Add a `--frame` parameter or cycle through 4 sampling profiles:
- Frame A: current Coeus-weighted
- Frame B: exploration-weighted (uniform + diversity cap)
- Frame C: dynamics-biased (3x on dynamics concepts)
- Frame D: judgment-biased (3x on ToM/metacognition concepts)

### Coeus (`enrichments/`)
Generate 4 enrichment variants per triple instead of 1:
- Frame A: "structural parsing, NCD tiebreaker"
- Frame B: "compute the answer, no NCD fallback, low confidence on uncomputable"
- Frame C: "track state evolution, trajectory stability, convergence"
- Frame D: "classify question first, epistemic honesty, _meta_confidence"

### Hephaestus (`prompts.py`)
4 code gen prompt variants:
- Frame A: current (structural emphasis)
- Frame B: constructive computation emphasis (math, Bayes, temporal)
- Frame C: dynamics emphasis (state, trajectory, reservoir)
- Frame D: judgment emphasis (metacognition, honesty, question classification)

### CAITL
4 improvement pass variants (when we run CAITL on new tools):
- Frame A: concept strengthening + standardization
- Frame B: constructive computation targeting
- Frame C: trajectory/state methods
- Frame D: epistemic honesty + Tier B patterns

---

## Expected Outcomes

| Frame | Expected Tools | Target Categories | Behavioral Profile |
|-------|---------------|-------------------|-------------------|
| A (Structural) | ~20% forge rate | Formal logic, basic parsing | Current 4 minimum set |
| B (Constructive) | ~5% forge rate | Temporal, causal, compositional | New: actual computation |
| C (Dynamics) | ~2% forge rate | Temporal-sequential, rate, stability | New: state tracking |
| D (Judgment) | ~10% forge rate | ToM, meta-reasoning, Tier B | New: epistemic honesty |

Total expected unique profiles: 19 existing + 10-20 new from B/C/D = **30-40 unique profiles**.

---

## Connection to Noesis

This IS the framing mechanism applied to the forge. Each frame is a bias vector that perceives the concept space differently:

```
Frame A = [structural, parsing, constraint, NCD]
Frame B = [computation, algebra, probability, temporal]
Frame C = [dynamics, trajectory, state, convergence]
Frame D = [judgment, honesty, metacognition, ToM]
```

The tensor shortcut principle: search with math, not brute force. The four frames are orthogonal basis vectors in forge-strategy space. Tools produced by different frames will be structurally different because they were built with different biases — just as Noesis organisms explore different regions of concept space when given different framing vectors.

---

## Priority

Build Frame B first (Constructive Computer). It targets the largest gap cluster (temporal, causal, compositional) and the forge survivor proved this architecture can work — it was born from the updated prompt that already includes some Frame B elements. Frame B is the highest-information experiment: if it produces tools that crack the 14 remaining gaps, we know computation was the missing ingredient. If it doesn't, we know the gaps require dynamics (Frame C) or judgment (Frame D).
