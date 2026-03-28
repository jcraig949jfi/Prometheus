# Forge Coverage Map — The Real Library

*As of 2026-03-27. The fog is gone. This is an engineering problem now.*

---

## The Squad

344 tools → 19 unique behavioral profiles → **5 tools cover 68/89 categories (76%)**.

| # | Tool | Categories Covered | Role |
|---|------|-------------------|------|
| 1 | Active Inference + FEP + Model Checking | 40 | The workhorse |
| 2 | Analogical Reasoning + Hebbian + FEP | 7 | Temporal + confidence + ToM gap filler |
| 3 | Analogical Reasoning + Dialectics + Mechanism Design | 1 | Specialist |
| 4 | Active Inference + Kolmogorov + FEP | 1 (correlation≠causation) | Specialist |
| 5 | **Information Theory + Abductive Reasoning + Sensitivity Analysis** | **19 previously uncovered** | **The survivor — born with metacognition** |

Tool #5 is the forge survivor: 1 out of 187 attempts on the 89-category battery. Never CAITL-refined. Born from the updated prompt with Tier B awareness, constructive computation, and epistemic honesty. It nearly doubled the library's coverage on first evaluation.

---

## The 68 Covered Categories

Covered by at least one tool at ≥50% accuracy.

### By the original 4 (minimum covering set):
All 15 original trap categories + formal logic expansion + probabilistic + most Tier B judgment traps.

### Newly covered by the survivor (19 categories):
| Category | Accuracy | Domain |
|----------|----------|--------|
| Affirming Consequent Numeric | 100% | Formal Logic |
| Causal Confounding | 100% | Causal |
| Compositional Causal-Statistical | 100% | Compositional |
| De Morgan | 100% | Formal Logic |
| Empty Set | 100% | Set Theory |
| Knowledge Attribution | 100% | Theory of Mind |
| Premise Contradiction | 100% | Formal Logic |
| Quantifier Inversion | 100% | Formal Logic |
| Base Rate Neglect | 50% | Probabilistic |
| Compositional Depth Scaling | 50% | Compositional |
| Compositional Logic-Arithmetic | 50% | Compositional |
| Compositional Nested ToM-Logic | 50% | Compositional |
| Expected Value | 50% | Probabilistic |
| False Belief Task | 50% | Theory of Mind |
| Information Sufficiency | 50% | Meta-Reasoning |
| Modular Arithmetic | 50% | Arithmetic |
| Subset Inversion | 50% | Set Theory |
| Temporal Frequency Coincidence | 50% | Temporal |
| ToM Mistaken Belief Chain | 50% | Theory of Mind |

---

## The 21 True Gaps

Zero coverage by any tool. Clustered by cognitive capability:

### Cluster 1: Temporal-Sequential (6 categories)
*Requires: maintaining and manipulating ordered state over time*
- temporal_age_reasoning
- temporal_causal_ordering
- temporal_concurrent_events
- temporal_rate_of_change
- temporal_relative_day
- temporal_sequence_reconstruction

**Concept-triple hypothesis:** Temporal Logic + Process Algebra + Dynamical Systems

### Cluster 2: Spatial (2 categories)
*Requires: maintaining reference frames and transforming between them*
- direction_composition
- left_right_reversal

**Concept-triple hypothesis:** Spatial Reasoning + Group Theory + Reference Frames

### Cluster 3: Causal-Interventional (2 categories)
*Requires: Pearl hierarchy rung 2-3 (intervention, counterfactual)*
- causal_intervention ("if we force Y=0, what happens to Z?")
- causal_counterfactual ("if X hadn't happened, would Y have happened?")

**Concept-triple hypothesis:** Do-Calculus + Structural Causal Models + Information Theory

### Cluster 4: Complex ToM (4 categories)
*Requires: recursive modeling of agents modeling other agents*
- tom_strategic_deception
- tom_perspective_shift
- tom_information_asymmetry
- tom_intention_reading

**Concept-triple hypothesis:** Recursive Bayesian Inference + Game Theory + Epistemic Logic

### Cluster 5: Self-Referential (1 category)
*Requires: reasoning about statements that refer to themselves*
- liar_detection (constraint propagation over self-referential graphs)

**Concept-triple hypothesis:** Fixed-Point Theory + Constraint Satisfaction + Formal Verification

### Cluster 6: Miscellaneous (6 categories)
- argument_strength (comparing reasoning quality)
- confidence_calibration (hedging language → probability)
- fencepost (off-by-one counting)
- subject_object (SVO parsing)
- causal_common_cause (identifying third variables)
- compositional_arithmetic_temporal (train catch-up problems)

---

## The Common Thread

All 21 gaps require **stateful multi-step transformation** — maintaining and manipulating internal representations across steps. Whether that state is temporal order, spatial reference frames, causal graphs, belief hierarchies, or self-referential loops, the core capability is the same: hold state, transform it, check constraints, iterate.

This is exactly what the dynamics-first concept families (Chaos Theory, Ergodic Theory, Neural Oscillations) were designed for but were never tested on, because the original battery didn't measure it. The expanded battery exposed the gap; the forge prompt update is producing tools that can start to fill it.

---

## What to Build Next

### Priority 1: CAITL the Survivor
Push the 50% categories toward 80%+. Compositional depth and belief chain reasoning are structural prerequisites for strategic deception and perspective shift. Gains here may cascade into the 21 gaps.

### Priority 2: Forge Targeted Triples
Add the 5 concept-triple hypotheses to Nous's priority queue:
1. Temporal Logic + Process Algebra + Dynamical Systems
2. Do-Calculus + Structural Causal Models + Information Theory
3. Recursive Bayesian Inference + Game Theory + Epistemic Logic
4. Fixed-Point Theory + Constraint Satisfaction + Formal Verification
5. Spatial Reasoning + Group Theory + Reference Frames

### Priority 3: Apollo Seed Selection
Seed from the 5-tool squad + any mass-tier tool that scores >0% on the 21 gaps. A weak tool with 15% on temporal reasoning is more valuable as a crossbreeding parent than an elite at 75% on covered categories.

---

## Files

| File | Content |
|------|---------|
| `forge_v5/minimum_covering_set.json` | The 4-tool minimum set + gap analysis |
| `forge_v5/dedup_analysis.json` | 19 unique, 313 redundant |
| `forge_v5/all_scores_89cat.json` | Full 89-category scores |
| `forge_v5/behavioral_fingerprints.json` | Pairwise disagreement matrix |
| `forge_v5/quartet_compositor.json` | Structure×Measure×Constraint×Dynamics results |
| `forge_v5/family_weights.json` | Per-family RLVF weights |
| `forge_v5/generational_trajectory.json` | v1→v5 fitness curves |
| `forge_v5/tier_aware_honesty.json` | Tier A/B calibration |
| `docs/ad_interface_evolution.md` | Solver×Critic architecture design |
