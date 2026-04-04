# Cluster Evaluation Design for T2 and T3

Design document for replacing the 12-category cross-eval with reasoning-family clusters.
Pipeline Orchestrator -- 2026-04-03.

---

## Problem Statement

The current T2 evaluation runs every tool against all 12 cross-eval categories
(24 traps across 5 seeds = 120 evaluations). A tool built to solve
`simpson_paradox` must also score on `temporal_scheduling`, `liar_detection`,
`strategic_deception`, etc. Since each tool is a specialist, it can only
score on the ~2-3 categories closest to its home domain. The structural
ceiling is approximately:

    max_possible = (home_categories / 12) * 100%

For a tool covering 3 related categories, that is 25%. For 4, it is 33%.
The 40% pass threshold requires covering ~5 of 12, which no specialist
architecture can do without becoming a mediocre generalist.

**Consequence:** 0/113 candidates passed before threshold recalibration.
Even after recalibration to 40%, only tools at 40-45% pass -- far below
their 80-100% home-category performance.

**Root cause:** The eval conflates "generalize within your reasoning family"
(desirable) with "solve all reasoning families" (a generalist requirement
imposed on specialists).

---

## The 25 T2 Categories (by wave)

For reference, the full T2 battery from `trap_generator_tier2.py`:

**Wave 1 -- Core Computational Primitives (8)**
1. `stateful_register_machine`
2. `epistemic_belief_tracking`
3. `constraint_satisfaction`
4. `recursive_evaluation`
5. `counterfactual_dependency`
6. `multi_step_arithmetic_carried`
7. `bayesian_update`
8. `information_sufficiency`

**Wave 2 -- Structural Reasoning (7)**
9. `defeasible_reasoning`
10. `logical_consistency_checking`
11. `temporal_interval_algebra`
12. `stable_model_finding`
13. `conditional_graph_traversal`
14. `rule_application_order`
15. `compositional_instruction_following`

**Wave 3 -- NL-Heavy (4)**
16. `referent_tracking_anaphora`
17. `closed_world_negation`
18. `argument_structure_analysis`
19. `implicit_constraint_inference`

**Wave 4 -- Formal / Quantitative (5)**
20. `quantifier_scope_ambiguity`
21. `process_simulation`
22. `graph_path_existence`
23. `set_membership_operations`
24. `truth_table_evaluation`

Plus the 12 quarantined cross-eval categories from `trap_generator_t2.py`:
`simpson_paradox`, `causal_counterfactual`, `conjunction_fallacy`,
`strategic_deception`, `perspective_shift`, `temporal_scheduling`,
`argument_strength`, `liar_detection`, `compositional_multi_step`,
`rate_of_change`, `causal_confounding_hard`, `temporal_complex`

Total pool: 36 unique categories available for clustering.

---

## Cluster Definitions

### Cluster A: Causal / Statistical Reasoning

**Core capability:** Decomposing aggregate statistics, identifying confounds,
reasoning about interventions and counterfactuals, updating on evidence.

| Category | Source | Rationale |
|----------|--------|-----------|
| `simpson_paradox` | Cross-eval | Aggregation reversal requires subgroup decomposition |
| `causal_counterfactual` | Cross-eval | Intervention reasoning shares causal graph primitives |
| `causal_confounding_hard` | Cross-eval | Confound identification is the flip side of Simpson's |
| `conjunction_fallacy` | Cross-eval | Joint vs marginal probability -- same statistical substrate |
| `bayesian_update` | Wave 1 | Evidence updating is the computational core of causal reasoning |
| `counterfactual_dependency` | Wave 1 | What-if reasoning under altered assumptions |

**Size:** 6 categories.
**Shared primitives:** d-separation, subgroup decomposition, Bayes rule, causal graph traversal.
**Why these cohere:** All require distinguishing correlation from causation, or computing conditional quantities. A tool with a causal DAG engine should generalize across all six.

---

### Cluster B: Temporal / Scheduling / Simulation

**Core capability:** Reasoning about time intervals, ordering events,
resolving scheduling constraints, tracking state changes over time.

| Category | Source | Rationale |
|----------|--------|-----------|
| `temporal_scheduling` | Cross-eval | Constraint-based scheduling over time slots |
| `temporal_complex` | Cross-eval | Complex temporal arithmetic and conversions |
| `rate_of_change` | Cross-eval | Quantities that change over time |
| `temporal_interval_algebra` | Wave 2 | Allen's interval algebra -- formal temporal reasoning |
| `process_simulation` | Wave 4 | Step-by-step state evolution over time |
| `stateful_register_machine` | Wave 1 | Sequential state tracking (temporal execution model) |

**Size:** 6 categories.
**Shared primitives:** Interval overlap detection, state accumulator, timeline construction, constraint propagation over ordered domains.
**Why these cohere:** All require maintaining and querying a temporal model -- whether it is a schedule, a register machine, or a rate computation. The core operation is "apply ordered transformations to state."

---

### Cluster C: Logic / Constraint / Formal Reasoning

**Core capability:** Evaluating logical validity, satisfying constraints,
checking consistency, applying rules in correct order.

| Category | Source | Rationale |
|----------|--------|-----------|
| `liar_detection` | Cross-eval | Resolving truth-value assignments under constraints |
| `argument_strength` | Cross-eval | Evaluating logical validity of formal arguments |
| `constraint_satisfaction` | Wave 1 | CSP solving -- the computational backbone |
| `logical_consistency_checking` | Wave 2 | Detecting contradictions in statement sets |
| `stable_model_finding` | Wave 2 | Finding consistent models under rules (answer set semantics) |
| `rule_application_order` | Wave 2 | Correct sequencing of logical rules |
| `truth_table_evaluation` | Wave 4 | Direct logical evaluation |

**Size:** 7 categories.
**Shared primitives:** SAT/CSP solver, truth table enumeration, consistency checking, rule chaining.
**Why these cohere:** All reduce to "find a consistent assignment under constraints." A tool with a constraint solver should transfer from liar puzzles to stable models to truth tables.

---

### Cluster D: Theory-of-Mind / Belief / Epistemic

**Core capability:** Modeling what agents know, believe, and intend;
tracking information asymmetry; detecting deception.

| Category | Source | Rationale |
|----------|--------|-----------|
| `perspective_shift` | Cross-eval | What different agents know |
| `strategic_deception` | Cross-eval | Modeling adversaries who misrepresent intentions |
| `epistemic_belief_tracking` | Wave 1 | Tracking who-knows-what across events |
| `information_sufficiency` | Wave 1 | Deciding whether enough is known to answer |
| `referent_tracking_anaphora` | Wave 3 | Tracking entities across discourse (who is "he"?) |
| `defeasible_reasoning` | Wave 2 | Beliefs that can be overridden by new evidence |

**Size:** 6 categories.
**Shared primitives:** Agent belief state, information set tracking, belief revision, perspective projection.
**Why these cohere:** All require maintaining a model of one or more agents' epistemic states. The core operation is "what does agent X know/believe given the information they have access to?"

---

### Cluster E: Compositional / Structural / Graph

**Core capability:** Multi-step inference, graph traversal, set operations,
instruction decomposition, structural pattern matching.

| Category | Source | Rationale |
|----------|--------|-----------|
| `compositional_multi_step` | Cross-eval | Chained reasoning where each step depends on the prior |
| `recursive_evaluation` | Wave 1 | Recursive/iterative computation |
| `multi_step_arithmetic_carried` | Wave 1 | Multi-step arithmetic with carry propagation |
| `conditional_graph_traversal` | Wave 2 | Graph traversal with conditional edges |
| `graph_path_existence` | Wave 4 | Path finding in explicit graphs |
| `set_membership_operations` | Wave 4 | Set algebra (union, intersection, complement) |
| `compositional_instruction_following` | Wave 2 | Decomposing complex instructions into steps |

**Size:** 7 categories.
**Shared primitives:** Graph traversal, recursive descent, set operations, instruction parsing, step chaining.
**Why these cohere:** All require decomposing a complex structure into parts and combining partial results. The core operation is "traverse a structure, accumulate results."

---

### Cluster F: Language / Inference / Ambiguity

**Core capability:** Resolving linguistic ambiguity, scoping quantifiers,
extracting implicit constraints from natural language.

| Category | Source | Rationale |
|----------|--------|-----------|
| `quantifier_scope_ambiguity` | Wave 4 | "Every student read a book" -- scope matters |
| `closed_world_negation` | Wave 3 | Inferring negation from absence (CWA) |
| `argument_structure_analysis` | Wave 3 | Extracting logical structure from NL arguments |
| `implicit_constraint_inference` | Wave 3 | Finding unstated constraints in problem text |

**Size:** 4 categories.
**Shared primitives:** NL parsing, scope resolution, closed-world assumption, constraint extraction.
**Why these cohere:** All require bridging from surface language to formal structure. The core operation is "extract the logical content from ambiguous natural language."

---

## Cluster Summary

| Cluster | Name | Size | Cross-eval cats included | New T2 cats |
|---------|------|-----:|:------------------------:|:-----------:|
| A | Causal / Statistical | 6 | 4 | 2 |
| B | Temporal / Scheduling / Simulation | 6 | 3 | 3 |
| C | Logic / Constraint / Formal | 7 | 2 | 5 |
| D | Theory-of-Mind / Belief | 6 | 2 | 4 |
| E | Compositional / Structural | 7 | 1 | 6 |
| F | Language / Inference / Ambiguity | 4 | 0 | 4 |
| **Total** | | **36** | **12** | **24** |

Every one of the 12 original cross-eval categories is assigned to exactly
one cluster. Every one of the 24 new T2 categories is assigned to exactly
one cluster. No category appears in two clusters.

---

## Category-to-Cluster Mapping for Tools

A tool's **home category** determines its **home cluster**:

```
simpson_paradox          -> Cluster A
causal_counterfactual    -> Cluster A
causal_confounding_hard  -> Cluster A
conjunction_fallacy      -> Cluster A
bayesian_update          -> Cluster A
counterfactual_dependency -> Cluster A

temporal_scheduling      -> Cluster B
temporal_complex         -> Cluster B
rate_of_change           -> Cluster B
temporal_interval_algebra -> Cluster B
process_simulation       -> Cluster B
stateful_register_machine -> Cluster B

liar_detection           -> Cluster C
argument_strength        -> Cluster C
constraint_satisfaction  -> Cluster C
logical_consistency_checking -> Cluster C
stable_model_finding     -> Cluster C
rule_application_order   -> Cluster C
truth_table_evaluation   -> Cluster C

perspective_shift        -> Cluster D
strategic_deception      -> Cluster D
epistemic_belief_tracking -> Cluster D
information_sufficiency  -> Cluster D
referent_tracking_anaphora -> Cluster D
defeasible_reasoning     -> Cluster D

compositional_multi_step -> Cluster E
recursive_evaluation     -> Cluster E
multi_step_arithmetic_carried -> Cluster E
conditional_graph_traversal -> Cluster E
graph_path_existence     -> Cluster E
set_membership_operations -> Cluster E
compositional_instruction_following -> Cluster E

quantifier_scope_ambiguity -> Cluster F
closed_world_negation    -> Cluster F
argument_structure_analysis -> Cluster F
implicit_constraint_inference -> Cluster F
```

---

## Pass Criteria

### Primary gate: Cluster battery

A tool must pass its **home cluster battery** -- the traps generated from
all categories in its cluster.

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `cluster_pass_threshold` | **0.55** | Higher than the current 0.40 global because the tool is only being tested on related categories. A specialist should ace its family. 55% on 6-7 related categories is more meaningful than 40% on 12 unrelated ones. |
| `max_seed_drop` | **0.18** | Tighter than 0.20 because within-cluster variance should be lower (related categories, similar primitives). |
| `min_categories_passed` | **3** | Must pass at least 3 individual categories within the cluster (not just accumulate points on 1-2). This prevents hyper-specialists that only solve their exact home category. |
| Seeds | 5 | Same as current: [42, 0, 1, 99, 9999] |
| Traps per category | 2 | Same as current |

**Battery size per cluster:**
- Cluster A: 6 cats x 2 traps x 5 seeds = 60 evaluations
- Cluster B: 6 cats x 2 traps x 5 seeds = 60 evaluations
- Cluster C: 7 cats x 2 traps x 5 seeds = 70 evaluations
- Cluster D: 6 cats x 2 traps x 5 seeds = 60 evaluations
- Cluster E: 7 cats x 2 traps x 5 seeds = 70 evaluations
- Cluster F: 4 cats x 2 traps x 5 seeds = 40 evaluations

This is a reduction from 120 evaluations (12 cats x 2 traps x 5 seeds) for
most clusters, while being more focused.

### Secondary gates (unchanged)

These remain from the current system:

| Gate | Criterion |
|------|-----------|
| Ablation budget share | No single primitive > 60% of total delta |
| Ablation min impact | Every primitive must affect >= 20% of outputs |
| Diversity | Max call-graph overlap <= 0.40 between tools in the same cluster |
| Seed stability | Max score drop across 5 seeds <= 0.18 |

### Generalist bonus

A tool that passes its home cluster AND scores >= 40% on one or more
**adjacent clusters** earns a generalist bonus. This is recorded in the
verdict but does NOT affect pass/fail. It is used downstream for T3
substrate selection (T3 prefers tools with cross-cluster reach).

| Adjacent cluster score | Bonus tag |
|----------------------:|-----------|
| >= 40% on 1 other cluster | `generalist_1` |
| >= 40% on 2 other clusters | `generalist_2` |
| >= 40% on 3+ other clusters | `generalist_3` |

**Adjacency is not restricted.** Any cluster counts. The bonus is purely
informational -- it captures "this tool has reach beyond its home domain"
without gating on it.

The generalist bonus feeds into:
1. **T3 Nous mining:** Prefer `generalist_1+` tools when selecting T2 substrate pairs.
2. **Coverage tracking:** Coeus weights generalist tools higher when computing effective coverage.
3. **Tiebreaking:** When two tools cover the same home category, prefer the one with a generalist bonus.

---

## T3 Cluster Definitions

T3 categories (from `trap_generator_t3.py`) naturally form clusters that
parallel the T2 structure but require cross-domain fusion:

### T3 Cluster X: Causal-Temporal Fusion
- `causal_temporal_fusion`
- `meta_causal_reasoning`
- `conditional_probability_chain`
- `cascading_inference`

### T3 Cluster Y: Strategic / Game-Theoretic
- `tom_causal_deception`
- `game_theory_sequential`
- `mechanism_design_incentive`
- `strategic_information_revelation`

### T3 Cluster Z: Meta-Reasoning / Self-Reference
- `reasoning_about_reasoning`
- `self_referential_paradox`
- `recursive_computation`
- `insufficient_information_detection`
- `adversarial_framing`

### T3 Cluster W: Compositional / Structural Transfer
- `temporal_tom_scheduling`
- `probabilistic_logic_conflict`
- `hidden_constraint`
- `structural_analogy`
- `abstraction_level_shift`
- `domain_transfer`

T3 pass criteria should use the same cluster_pass_threshold (0.55) and
min_categories_passed (3, or 2 for 4-category clusters) from day one.

---

## Impact Analysis

### Expected changes to existing tools

**Currently passing tools (7):**

| Tool | Home cluster | Expected effect |
|------|-------------|-----------------|
| `simpson_paradox_018_gem` | A | Should pass easily -- already 97.5% overall, causal categories are its strength |
| `temporal_scheduling_007_gem` | B | Should pass -- 96.7% overall, temporal categories are its strength |
| `perspective_shift_017` | D | May need to generalize to `epistemic_belief_tracking` and `information_sufficiency` -- at risk |
| `simpson_paradox_018` | A | Likely passes -- 43.3% but concentrated on causal categories |
| `temporal_scheduling_007` | B | Likely passes -- 40.8% concentrated on temporal |
| `simpson_paradox_003` | A | At risk -- 40% overall, unclear if it covers `bayesian_update` or `counterfactual_dependency` |
| `temporal_scheduling_011` | B | At risk -- 40% overall, same concern |

**Currently failing near-misses:**

| Tool | Home cluster | Expected effect |
|------|-------------|-----------------|
| `liar_detection_012` (38.3%) | C | **Likely promoted.** Currently walled out by causal and temporal categories it cannot solve. Under cluster eval, only needs to score on logic/constraint family. |
| `perspective_shift_019` (39.2%) | D | **Likely promoted.** Same reasoning -- only tested on ToM/belief family. |
| `perspective_shift_005` (44.2%, high seed drop) | D | Seed drop issue remains (25pp > 18pp limit). Cluster eval does not fix instability. |

**Expected net effect:** +2-3 tools promoted from near-miss, 0-2 existing tools at risk of demotion (those that passed the 40% global threshold by accumulating small scores across many categories rather than dominating their cluster).

### Theoretical max for specialists

Under the old system, a single-domain specialist's max was ~37.5% (4.5/12 categories).

Under cluster eval, a specialist covering 4 of 6 categories in its cluster
scores 67% -- well above the 55% threshold. A specialist covering 3 of 6
scores 50% -- close but below threshold, which is the correct behavior
(we want generalization within the family, not single-category tools).

---

## Migration Path

### Phase 1: Implement cluster infrastructure (est. 2 hours)

1. Add `CLUSTER_MAP` dict to `forge/thresholds.py`:
   ```python
   CLUSTER_MAP = {
       "simpson_paradox": "A",
       "causal_counterfactual": "A",
       # ... all 36 categories
   }
   CLUSTER_THRESHOLDS = {
       "cluster_pass_threshold": 0.55,
       "max_seed_drop": 0.18,
       "min_categories_passed": 3,
   }
   ```

2. Add `load_cluster_battery(cluster_id, n_per_category, seed)` to
   `forge/tester.py` that filters the T2 battery to only include
   categories in the specified cluster.

3. Add `run_cluster_eval(tool, home_category, tier, seeds)` that:
   - Looks up the tool's home cluster from `CLUSTER_MAP`
   - Loads cluster battery
   - Runs seed battery
   - Checks `min_categories_passed`
   - Optionally runs adjacent cluster batteries for generalist bonus

### Phase 2: Dual evaluation (est. 1 hour)

Run both old (12-category) and new (cluster) evaluations in parallel for
all 77 existing candidates. Write dual verdicts:

```
forge/verdicts/t2_simpson_paradox_003_verdict.json       # old
forge/verdicts/t2_simpson_paradox_003_verdict_cluster.json  # new
```

Compare pass/fail populations. Verify:
- No tool that passes old eval fails cluster eval (sanity check)
- Near-misses are correctly promoted
- No degenerate tools (single-category only) sneak through

### Phase 3: Cut over (est. 30 min)

Once dual eval confirms expected behavior:

1. Update `evaluate_tool()` in `tester.py` to use cluster eval as primary
2. Keep global eval as a recorded metric (for generalist bonus) but not
   as a gate
3. Update `builder.py` category descriptions to include cluster membership
   so the builder knows which related categories to target
4. Update `thresholds.py` with new cluster thresholds

### Phase 4: T3 launch with clusters from day one

When T3 launches, use T3 clusters (X/Y/Z/W) as the primary evaluation
structure. No 20-category cross-eval. This avoids repeating the T2 mistake.

---

## Open Questions

1. **Cluster F is small (4 categories).** Should `min_categories_passed` be
   reduced to 2 for 4-category clusters? Recommendation: yes.

2. **Should the generalist bonus affect T3 substrate priority?** Current
   recommendation: yes, as a soft signal, not a hard gate.

3. **Trap generator coverage:** The quarantined `trap_generator_t2.py` only
   generates 12 categories. The new `trap_generator_tier2.py` generates 24.
   Cluster eval for A-F needs traps from BOTH generators. Verify that
   `load_battery(tier=2, ...)` pulls from the right generator.

4. **Re-evaluation scope:** Do we re-run all 77 tools through cluster eval,
   or only re-score existing per-category results? Recommendation: re-score
   from existing per-category data where available (the verdicts already
   contain `per_category` breakdowns), re-run only tools that were evaluated
   against the old 12-category battery and need the new categories tested.

---

## Files to Modify

| File | Change |
|------|--------|
| `forge/thresholds.py` | Add `CLUSTER_MAP`, `CLUSTER_THRESHOLDS` |
| `forge/tester.py` | Add `load_cluster_battery()`, `run_cluster_eval()`, modify `evaluate_tool()` |
| `forge/builder.py` | Add cluster membership to `T2_CATEGORIES` descriptions |
| `forge/builder_prompt.py` | Include cluster context so builder targets related categories |
| `agents/hephaestus/src/test_harness.py` | Wire `CATEGORY_DIFFICULTY` into cluster-weighted scoring |

---

*Pipeline Orchestrator -- 2026-04-03. Implements priority action #3 from STATUS_T1_T2_20260403.md.*
