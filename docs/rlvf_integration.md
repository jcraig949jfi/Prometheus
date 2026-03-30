# RLVF Integration: Forge Tools as Rhea's Reward Signal

*2026-03-29 -- Design Document*

---

## What RLVF Is

Reinforcement Learning from Verification Feedback (RLVF) replaces human preference (RLHF) with computed verification as the reward signal for training Rhea, the reasoning model.

The forge pipeline (Nous + Coeus + Hephaestus) produces evaluation tools -- Python classes that score candidate answers to reasoning questions using only numpy and stdlib. Each tool implements `evaluate(prompt, candidates) -> ranked scores` and `confidence(prompt, answer) -> float`. These tools become the reward function: Rhea generates a response, forge tools score it, and the score drives selection pressure.

The key insight: human preference is expensive, subjective, and gameable. Computed verification is cheap, deterministic, and auditable. A tool that checks whether a candidate satisfies modus tollens or correctly tracks belief states across agents is not expressing a preference -- it is verifying a capability. RLVF replaces "what would a human rate highly" with "does this response demonstrate reasoning."

---

## The Evaluator Library

### Current Inventory

| Directory | Content | Count |
|-----------|---------|-------|
| `agents/hephaestus/forge/` | Original forge-generated tools (v1) | 268 files |
| `agents/hephaestus/forge_v2/` | CAITL-improved tools (v2) | 50 files |
| `agents/hephaestus/forge_v5/` | Mid-era tools | variable |
| `agents/hephaestus/forge_v7/` | Opus-forged tools (breakthrough) | 46 files |

**197 passing tools** across all directories (strictly beat NCD baseline of 20% accuracy / 7% calibration).

### Battery Coverage

- **Tier 1:** 89 categories -- cognitive biases, logical fallacies, causal reasoning, theory of mind, temporal reasoning, compositional reasoning
- **Tier 2:** 19 categories -- stateful computation, recursive evaluation, constraint satisfaction, defeasible reasoning, belief tracking (see `docs/tier2_reasoning_design.md`)
- **Total:** 108 categories across the full battery

### Tool Quality Tiers

| Tier | Description | Examples |
|------|-------------|---------|
| **Elite (>70% accuracy)** | 6 tools, all Opus-forged v7. Multi-frame prompts broke the NCD monoculture. | `causal_inference_x_bayesian_inference_x_information_theory` (74% acc, 70 categories) |
| **Deep reasoning engine** | Frame E computation-first tools | `frame_e_v3_definitive` (0.679 weighted score, 74.8% on hard categories) |
| **Strong (50-70%)** | CAITL-improved v2 tools with real algorithmic implementations | `ergodic_theory_x_fep_x_reinforcement_learning` (73% acc / 80% cal after CAITL) |
| **Baseline (42-50%)** | NCD-backbone tools with structural parsing overlays | Most v1 forge tools |

### Architectural Families

- **Structural Falsification Engines** -- parse prompt for logical structure, check candidates against extracted constraints. Elimination over selection.
- **Computation-first (Frame E/F/G)** -- parse, compute, match. Stateful execution, arithmetic evaluation, graph traversal. 3.5x improvement on hard categories over regex.
- **Active Inference / Free Energy** -- model candidates as hypotheses minimizing expected free energy. Local co-occurrence SVD for distributional semantics.
- **Feature-discovery bandits** -- UCB algorithms that learn which textual features are informative within a batch.
- **Regex tools** -- 74% accuracy on Tier 1 easy/medium, fast, deterministic. Six elite tools.

### Ensemble Strategy

Computation modules handle hard categories (stateful, causal, ToM, compositional). Regex tools handle easy/medium categories (cognitive biases, simple logic, numeric comparison). The ensemble uses max-across-tools, weighted by each tool's known accuracy on that category.

---

## Integration Architecture

### The Training Loop

```
                    +------------------+
                    |  Prompt Generator |
                    |  (108-category   |
                    |   battery)       |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    |      Rhea        |
                    |  (generates      |
                    |   response)      |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    |  Scoring API     |
                    |  tool.evaluate() |
                    |  tool.confidence()|
                    +--------+---------+
                             |
                             v
                    +------------------+
                    |  Reward Signal   |
                    |  weighted score  |
                    |  + confidence    |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    |  Selection       |
                    |  (CMA-ES over   |
                    |   LoRA weights)  |
                    +------------------+
```

### Step-by-Step Flow

1. **Prompt generation.** The prompt generator draws from the 108-category battery. Each prompt targets a specific reasoning capability (e.g., `stateful_register_machine`, `causal_confounding`, `tom_strategic_deception`). Prompts include the question and a set of candidate answers.

2. **Response generation.** Rhea generates a reasoning chain in response to the prompt. This is the artifact being evaluated -- not just the final answer, but the chain of reasoning that produced it.

3. **Tool evaluation.** One or more forge tools score the response via `evaluate(prompt, candidates)`. Each tool returns ranked candidates with scores in [0,1] and a reasoning trace explaining why.

4. **Confidence gating.** Each tool also reports `confidence(prompt, answer)` -- a float in [0,1] indicating how certain the tool is about its evaluation. Low-confidence scores are down-weighted in the reward signal (see Scoring Function below).

5. **Reward computation.** Scores are aggregated across tools and categories into a single reward signal using the weighted scoring function from `agents/hephaestus/src/test_harness.py`.

6. **Selection pressure.** The reward signal drives CMA-ES selection over LoRA weights targeting identified ejection heads in the model. Chains that satisfy more tools across more categories are fitter.

### Data Provenance

The forge pipeline enforces hard provenance gates (see `docs/forge_pipeline.md`, Architectural Invariants):

- `training` -- verified reasoning chains for Rhea fine-tuning
- `evaluation` -- tool scores, battery results (this is where RLVF operates)
- `adversarial` -- Nemesis-generated failure cases (test only, never enters training)

RLVF scores carry the `evaluation` tag. They inform selection pressure but are not training data themselves -- the training data is Rhea's self-generated reasoning chains. The reward signal selects which chains survive; it does not contaminate the chains.

---

## The Scoring Function for RLVF

### Why Per-Category Accuracy Is Wrong

Per-category accuracy (correct/total per category) is binary and noisy -- a tool either got the answer right or wrong on a single instance. As a reward signal, this creates sparse gradients: most updates carry zero signal (correct) or maximum penalty (incorrect) with nothing in between. It also treats all categories equally, which means easy pattern-matching categories dominate the signal.

### Difficulty-Weighted Scoring

From `agents/hephaestus/src/test_harness.py`:

```python
DIFFICULTY_WEIGHTS = {"easy": 0.3, "medium": 0.3, "hard": 0.4}

def compute_weighted_score(trap_results, traps):
    # Group results by difficulty tier
    tier_correct = defaultdict(int)
    tier_total = defaultdict(int)
    for result, trap in zip(trap_results, traps):
        cat = trap.get("category", "")
        difficulty = CATEGORY_DIFFICULTY.get(cat, "medium")
        tier_total[difficulty] += 1
        if result.get("is_correct"):
            tier_correct[difficulty] += 1
    # Weighted average across tiers
    weighted = 0.0
    total_weight = 0.0
    for tier, weight in DIFFICULTY_WEIGHTS.items():
        if tier_total[tier] > 0:
            acc = tier_correct[tier] / tier_total[tier]
            weighted += weight * acc
            total_weight += weight
    return round(weighted / total_weight, 4) if total_weight > 0 else None
```

The 0.3/0.3/0.4 split ensures hard categories (all Tier 2, plus the 25 hardest Tier 1 categories) carry 40% of the reward signal despite being a minority of the battery. This creates selection pressure specifically for computation-first reasoning -- the capabilities that regex tools cannot provide.

### Category Difficulty Distribution

From `CATEGORY_DIFFICULTY` in `test_harness.py`:

| Tier | Count | Weight | Examples |
|------|-------|--------|----------|
| **Easy** | 29 categories | 0.3 | `numeric_comparison`, `transitivity`, `vacuous_truth`, `sunk_cost` |
| **Medium** | 35 categories | 0.3 | `modus_tollens`, `causal_chain_length`, `base_rate_neglect`, `correlation_not_causation` |
| **Hard** | 44 categories (25 Tier 1 + 19 Tier 2) | 0.4 | `stateful_register_machine`, `causal_confounding`, `tom_strategic_deception`, `recursive_evaluation` |

### Ensemble Scoring

For RLVF, a single tool's score is insufficient -- it creates monoculture risk. The ensemble scoring function:

```
reward(response) = max_i [ w_i * S_i(response) * conf_i(response) ]
```

Where:
- `S_i(response)` = score from tool i on this response
- `conf_i(response)` = confidence from tool i
- `w_i` = tool i's known accuracy on this category (from historical battery results)

The `max` aggregation prefers the most capable tool for each category. The confidence weighting prevents overconfident-but-wrong tools from corrupting the signal. The category-specific weight `w_i` ensures tools are only trusted on categories where they have demonstrated competence.

### The Variance Penalty (Goodhart Defense)

From the forge pipeline design:

```
F(T) = sum_i [ w_i * S_i(T) ] - lambda * sigma(S_competent)
```

**Critical: the variance penalty must be scoped to competent tools only.** (Athena review, 2026-03-29)

The naive formulation `sigma(S)` across all tools has a compositional blind spot: when a response legitimately requires a capability only one tool can detect (e.g., `stateful_register_machine` where only Frame E tools are competent), the max aggregation correctly rewards it, but an unscoped variance penalty punishes it because regex tools can't confirm what they can't evaluate.

The fix: compute variance only across tools that are *competent on the category in question*. This means the `category_tool_map` isn't just an optimization — it's **load-bearing for the reward signal's coherence.**

```python
def variance_penalty(scores, category, category_tool_map):
    competent_tools = category_tool_map[category]
    competent_scores = [scores[t] for t in competent_tools if t in scores]
    if len(competent_scores) < 2:
        return 0.0  # single competent tool — no variance to penalize
    return lambda_val * np.std(competent_scores)
```

When only one tool is competent on a category, the variance penalty is zero — the specialist's judgment stands unchallenged. When multiple tools are competent, disagreement between them is a genuine red flag.

---

## Category-to-Capability Mapping

The 108 categories are not arbitrary test items -- they map to specific reasoning capabilities that Rhea needs to develop. This mapping determines what RLVF is actually selecting for.

### Stateful Computation
*The ability to maintain and update internal state through a sequence of operations.*

| Category | Capability Tested | Difficulty |
|----------|-------------------|------------|
| `stateful_register_machine` | Execute sequential register operations (set, add, subtract) | hard |
| `compositional_depth_scaling` | Apply ordered transformations to a value (add, multiply, modular) | hard |
| `recursive_evaluation` | Evaluate nested function calls with recursive structure | hard |
| `multi_step_arithmetic_carried` | Multi-step arithmetic with carry propagation | hard |
| `compositional_arithmetic_temporal` | Arithmetic combined with temporal constraints (speed, distance, time) | hard |
| `order_of_operations` | Standard mathematical precedence rules | easy |
| `modular_arithmetic` | Clock arithmetic, modular residues | medium |

### Causal Reasoning
*The ability to distinguish correlation from causation, handle confounders, and reason counterfactually.*

| Category | Capability Tested | Difficulty |
|----------|-------------------|------------|
| `causal_confounding` | Identify confounding variables in correlational claims | hard |
| `causal_counterfactual` | Evaluate hypothetical scenarios about absent causes | hard |
| `causal_intervention` | Reason about forced interventions (do-calculus intuition) | hard |
| `causal_simpson_paradox` | Detect reversal when aggregating across subgroups | hard |
| `causal_chain_length` | Trace multi-step causal chains | medium |
| `causal_common_cause` | Identify common causes behind correlated effects | hard |
| `correlation_not_causation` | Reject causal claims from correlational evidence | medium |
| `counterfactual_dependency` | Track what depends on what in counterfactual worlds | hard |
| `causal_necessary_sufficient_extended` | Distinguish necessary from sufficient causes | easy |
| `post_hoc` | Reject "after therefore because" reasoning | easy |

### Theory of Mind
*The ability to model other agents' beliefs, knowledge, and intentions as distinct from reality.*

| Category | Capability Tested | Difficulty |
|----------|-------------------|------------|
| `tom_strategic_deception` | Model agent who knows opponent will do opposite | hard |
| `tom_perspective_shift` | Spatial/conceptual perspective transformation | hard |
| `tom_intention_reading` | Infer intent from action in context | hard |
| `tom_information_asymmetry` | Track who knows what when agents have different information | hard |
| `tom_mistaken_belief_chain` | Chain of false beliefs across multiple agents | hard |
| `epistemic_belief_tracking` | Maintain separate belief databases per agent | hard |
| `tom_second_order_belief` | "Alice thinks Bob thinks..." | easy |
| `tom_group_knowledge` | Common knowledge vs individual knowledge | easy |
| `false_belief_task` | Classic Sally-Anne style false belief | medium |
| `knowledge_attribution` | Who knows what based on what they've observed | medium |

### Formal Logic
*The ability to apply deductive rules correctly and resist logical fallacies.*

| Category | Capability Tested | Difficulty |
|----------|-------------------|------------|
| `modus_tollens` | "If P then Q; not Q; therefore not P" | medium |
| `chained_conditional` | Multi-step conditional chains | medium |
| `demorgan` | Negation distribution over AND/OR | medium |
| `defeasible_reasoning` | Conclusions that can be defeated by new information | hard |
| `logical_consistency_checking` | Detect contradictions in a set of statements | hard |
| `transitivity` | A > B, B > C, therefore A > C | easy |
| `affirming_consequent` | Detect the fallacy of affirming the consequent | easy |
| `denying_antecedent` | Detect the fallacy of denying the antecedent | easy |
| `double_negation` | Resolve nested negations | medium |
| `negation_scope` | Determine what a negation applies to | medium |

### Metacognition
*The ability to assess one's own knowledge state -- what is known, unknown, and uncertain.*

| Category | Capability Tested | Difficulty |
|----------|-------------------|------------|
| `confidence_calibration` | Match stated confidence to actual accuracy | hard |
| `information_sufficiency` | Recognize when there isn't enough information to answer | medium |
| `information_sufficiency_t2` | Harder version: subtle missing premises | hard |
| `argument_strength` | Evaluate relative strength of competing arguments | medium |
| `argument_structure_analysis` | Parse argument into premises, inferences, conclusions | hard |
| `base_rate_neglect` | Incorporate base rates into probability judgments | medium |
| `framing_effect` | Recognize equivalent claims presented differently | medium |

### Temporal Reasoning
*The ability to track time, sequence, duration, and rate.*

| Category | Capability Tested | Difficulty |
|----------|-------------------|------------|
| `temporal_frequency_coincidence` | "Every N days" -- find coincidence via LCM | hard |
| `temporal_rate_of_change` | Compute and compare rates from time-series data | hard |
| `temporal_duration_across_midnight` | Duration calculation spanning midnight boundary | hard |
| `temporal_scheduling_conflict` | Detect overlapping time intervals | hard |
| `temporal_age_reasoning` | Chain of age relationships with arithmetic | hard |
| `temporal_relative_day` | "Two days after the day before yesterday" | hard |
| `temporal_sequence_reconstruction` | Reconstruct timeline from partial ordering constraints | hard |
| `temporal_interval_algebra` | Allen's interval algebra (before, during, overlaps) | hard |
| `temporal_ordering` | Simple before/after sequencing | medium |
| `temporal_causal_ordering` | Combine temporal and causal ordering | medium |
| `temporal_concurrent_events` | Track parallel timelines | medium |

### Compositional Reasoning
*The ability to combine multiple reasoning types in a single problem.*

| Category | Capability Tested | Difficulty |
|----------|-------------------|------------|
| `compositional_multi_hop_with_distractor` | Multi-hop deduction with irrelevant premises | hard |
| `compositional_logic_tom` | Logic + belief state tracking | hard |
| `compositional_logic_arithmetic` | Logic + arithmetic evaluation | medium |
| `compositional_temporal_causal` | Temporal + causal reasoning combined | hard |
| `compositional_causal_statistical` | Causal + statistical (Simpson's paradox) | hard |
| `compositional_depth_scaling` | Multi-step state transformation | hard |
| `compositional_instruction_following` | Follow complex multi-part instructions | hard |
| `multi_hop_deduction` | Chain of deductive steps | medium |

### Additional Capabilities (Tier 2)

| Category | Capability Tested | Difficulty |
|----------|-------------------|------------|
| `constraint_satisfaction` | Find assignments satisfying multiple constraints simultaneously | hard |
| `bayesian_update` | Update probability given new evidence | hard |
| `stable_model_finding` | Find stable models under default logic | hard |
| `conditional_graph_traversal` | Navigate graphs with conditional edges | hard |
| `rule_application_order` | Apply rules in correct sequence when order matters | hard |
| `referent_tracking_anaphora` | Track what pronouns and references point to | hard |
| `closed_world_negation` | Infer negation from absence (closed-world assumption) | hard |
| `implicit_constraint_inference` | Derive unstated constraints from problem structure | hard |

---

## Implementation Checklist

### Phase 1: Evaluator Selection and API

- [ ] **Select evaluator set.** Start with the ensemble approach:
  - Frame E computation-first tools for hard categories (0.679 weighted)
  - Top 6 regex tools for easy/medium categories (74% accuracy)
  - `causal_inference_x_bayesian_inference_x_information_theory` as the generalist backbone (74% acc, 70 categories)
  - File locations: `agents/hephaestus/forge_v7/`, `agents/hephaestus/forge_v2/`, `agents/hephaestus/forge/`

- [ ] **Build scoring API.** Standardize the interface:
  ```python
  class RLVFScorer:
      def __init__(self, tool_paths: list[Path], category_tool_map: dict):
          """Load tools, map each category to its best evaluator(s)."""

      def score(self, prompt: str, response: str, category: str) -> dict:
          """Returns {
              "reward": float,       # aggregated score for this response
              "confidence": float,   # tool's confidence in the evaluation
              "tool_used": str,      # which tool(s) produced the score
              "reasoning": str,      # trace of why this score was given
              "difficulty": str,     # easy/medium/hard
          }"""

      def batch_score(self, episodes: list[dict]) -> float:
          """Compute weighted score across a batch using compute_weighted_score."""
  ```
  - Reuse `load_tool_from_file` and `run_trap_battery` from `agents/hephaestus/src/test_harness.py`
  - Reuse `compute_weighted_score` with `CATEGORY_DIFFICULTY` and `DIFFICULTY_WEIGHTS`

- [ ] **Build category-to-tool mapping.** For each of the 108 categories, identify which tool(s) have the highest accuracy. Store as JSON:
  ```json
  {
    "stateful_register_machine": {
      "primary": "frame_e_v3_definitive",
      "fallback": "causal_inference_x_bayesian_inference_x_information_theory",
      "best_accuracy": 0.85
    }
  }
  ```

### Phase 2: Prompt Generation

- [ ] **Design prompt generator.** Each training episode needs:
  - A reasoning prompt drawn from the 108-category battery
  - A set of candidate answers (correct + distractors)
  - Category metadata (for difficulty weighting)
  - Source: expand the existing trap battery in `agents/hephaestus/src/test_harness.py` with parametric generation (variable names, numbers, relationships randomized per instance)

- [ ] **Implement mixed-difficulty curriculum with shifting weights.** (Revised per Athena review, 2026-03-29)

  **Do NOT use staged inclusion** (easy first, then medium, then hard). If the ejection circuit operates as the convergence theory predicts, easy categories are *inside* the model's existing attractor basins. Training on them first deepens heuristic basins before the hard signal that's supposed to escape them ever arrives.

  Instead, use **mixed-difficulty from the start** with the *weighting* shifting over time:
  - Phase 1: all 113 categories present, but weighting is 0.5 easy / 0.3 medium / 0.2 hard
  - Phase 2 (after 50 generations): shift to 0.3 / 0.3 / 0.4 (standard difficulty weighting)
  - Phase 3 (after 100 generations): shift to 0.2 / 0.3 / 0.5 (hard-dominant)

  This ensures the hard signal is always present as a geometric pressure even when the easy signal dominates the reward magnitude. The model never gets a chance to entrench in easy-only basins.

### Phase 3: Training Loop Integration

- [ ] **Integrate with Rhea's CMA-ES loop.** The current Rhea architecture (see `docs/Rhea.md`) evolves LoRA weights via CMA-ES. RLVF replaces the fitness function:
  - Current: fitness = metacognition score on self-generated chains
  - RLVF: fitness = `compute_weighted_score` across forge tool evaluations
  - The LoRA targets remain the same (v_proj on identified ejection heads)

- [ ] **Establish combined baseline (behavioral + geometric).** Before any RLVF training, capture BOTH measurement types on the unmodified model in a single pass. This is the reference point — if you baseline behavioral first and add geometric later, you've lost your reference. (Athena review: sequencing detail, not design gap, but critical to get right.)

  The baseline file must contain both:
  ```
  agents/hephaestus/baselines/rhea_pre_rlvf.json
  {
    "behavioral": {
      "per_category_accuracy": { ... },   // all 113 categories
      "weighted_score": 0.xxx,
      "easy_accuracy": 0.xxx,
      "medium_accuracy": 0.xxx,
      "hard_accuracy": 0.xxx
    },
    "geometric": {
      "delta_cf": 0.xxx,          // counterfactual shift
      "mi_step": 0.xxx,           // mutual information per reasoning step
      "delta_proj": 0.xxx,        // v_proj projection delta from pretrained
      "basin_classification": { ... }  // per-trap basin type (RIDGED/IMPENETRABLE/OPEN)
    },
    "model": "rhea-1.5b-corpus-v1",
    "timestamp": "...",
    "battery_version": "tier1_89_tier2_24"
  }
  ```

  **Both behavioral and geometric baselines must be captured before Generation 0.** Phase 3.5's geometric comparison is meaningless without this reference.

- [ ] **Implement reward logging.** Every RLVF episode should log:
  - Prompt, response, category, tool used, score, confidence, reasoning trace
  - This is the audit trail for detecting reward hacking

### Phase 3.5: Geometric Measurement Protocol (Athena review, 2026-03-29)

**The behavioral score going up is necessary but not sufficient.** RLVF → Rhea requires *geometrically legible* improvement, not just higher accuracy. A model that learns to game the tools' parsing patterns will show behavioral improvement without geometric shift — and that improvement won't transfer.

After each RLVF cycle, before interpreting the behavioral scores:

- [ ] **Run RPH's three proxy metrics on the post-training model:**
  - `Δ_cf` (counterfactual shift) — does the model's internal representation change when the correct answer changes?
  - `MI_step` (mutual information per reasoning step) — does the model accumulate information across steps?
  - `Δ_proj` (projection delta) — has the v_proj geometry shifted from baseline?

- [ ] **Compare to pre-RLVF baseline geometry.** The geometric metrics from `agents/hephaestus/baselines/rhea_pre_rlvf.json` serve as the reference.

- [ ] **Success criterion:** A cycle counts as successful only if BOTH:
  1. Weighted behavioral score increased (standard RLVF metric)
  2. At least one geometric proxy shifted toward the reasoning direction (geometric legibility)

  If behavioral score rises but geometry doesn't shift, the model is Goodharting at the meta level — optimizing for the number you can see while the thing you care about stays unmeasured.

- [ ] **Log geometric measurements** alongside behavioral scores in the RLVF audit trail. This creates the dataset needed to understand the relationship between geometric shift and behavioral improvement.

### Phase 4: Monitoring and Defense

- [ ] **Monitor for reward hacking.** Indicators:
  - Score on RLVF battery increases but score on held-out prompts (Nemesis adversarial set) decreases
  - Score on one tool increases dramatically while others stagnate
  - Response length or formatting converges to a narrow pattern
  - Confidence scores cluster at 0.0 or 1.0 (degenerate landscape)

- [ ] **Implement Nemesis integration.** The variance penalty `lambda * sigma(S)` requires multiple tools scoring each response. Responses where tools disagree are penalized.

- [ ] **Rotate evaluation tools.** Periodically swap which tools evaluate which categories. If Rhea's score drops after rotation, it was overfitting to the previous tool's biases.

---

## Risks

### Reward Hacking
**Risk:** Rhea learns tool-specific patterns instead of reasoning. For example, if a tool rewards responses containing the word "therefore," Rhea learns to insert "therefore" without actually performing deduction.

**Mitigation:** The variance penalty penalizes responses that score high on one tool but low on others. Tool rotation prevents overfitting to any single evaluator. Nemesis adversarial testing catches surface-level pattern exploitation.

### Monoculture
**Risk:** If one tool dominates the ensemble (e.g., the 74% accuracy generalist is used for most categories), Rhea optimizes for that tool's specific parsing patterns and regex templates.

**Mitigation:** Use category-specific tool assignments -- each category uses its best-performing tool, not the overall best. The 197 passing tools provide enough diversity to assign different evaluators to different categories. Monitor per-tool score distributions for convergence.

### Calibration Corruption
**Risk:** Tools that are overconfident on wrong answers (high confidence, wrong score) corrupt the reward signal more than tools that are uncertain. A tool reporting 0.95 confidence on a wrong evaluation sends a strong incorrect gradient.

**Mitigation:** Weight by `score * confidence` so low-confidence evaluations are down-weighted. Flag tools where confidence and accuracy diverge (high confidence, low accuracy on held-out data). The CAITL pass specifically improved `confidence()` methods to compare against null baselines and return near-zero confidence on falsified answers.

### Coverage Gaps
**Risk:** 108 categories don't cover all reasoning types. Notable gaps: analogical reasoning, creative problem solving, spatial reasoning beyond simple perspective shifts, mathematical proof construction, planning under uncertainty.

**Mitigation:** The forge pipeline runs continuously -- Nous mines new concept combinations, Hephaestus forges new tools, and the battery grows. Tier 2 added 19 categories that didn't exist in Tier 1. Tier 3 can add more. The architecture is designed for an ever-growing battery, not a fixed one.

### Training Data Contamination
**Risk:** If RLVF prompts are too similar to the battery traps, Rhea memorizes answers instead of learning reasoning.

**Mitigation:** Parametric prompt generation randomizes variable names, numbers, relationships, and surface structure while preserving the underlying reasoning challenge. The battery's 108 categories are *types* of problems, not fixed instances. Each training episode generates a fresh instance.

### The Goodhart Ceiling
**Risk:** Even with all mitigations, there is a ceiling: Rhea can only become as good at reasoning as the forge tools can detect. If the tools can't distinguish genuine reasoning from sophisticated pattern matching, neither can the reward signal.

**Mitigation:** This is the fundamental limitation of RLVF and the reason the forge pipeline must keep evolving. The Tier 2 design document (`docs/tier2_reasoning_design.md`) lays out the path: tools that parse, compute, and match -- not tools that regex-match. The Frame E/F/G computation-first tools are the beginning of this trajectory. The ceiling rises as the tools get better.

---

## Dependencies

| Component | Location | Status |
|-----------|----------|--------|
| Forge tool library | `agents/hephaestus/forge/`, `forge_v2/`, `forge_v5/`, `forge_v7/` | 197 passing tools |
| Test harness + scoring | `agents/hephaestus/src/test_harness.py` | Implemented (`compute_weighted_score`, `CATEGORY_DIFFICULTY`) |
| Tool loader | `agents/hephaestus/src/test_harness.py` (`load_tool_from_file`) | Implemented |
| Trap battery | `agents/hephaestus/src/test_harness.py` | 108 categories (89 Tier 1 + 19 Tier 2) |
| Rhea training loop | `agents/rhea/` (CMA-ES over LoRA weights) | Implemented, needs fitness function swap |
| Nemesis adversarial set | `agents/nemesis/` | Grid 92/100, adversarial results available |
| Coeus causal weights | `agents/coeus/graphs/concept_scores.json` | Available for tool weighting |
| Provenance gates | `docs/forge_pipeline.md` (Architectural Invariants) | Design documented, needs code enforcement |
