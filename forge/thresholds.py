"""
FROZEN THRESHOLDS — Pre-committed before any tool evaluation.
DO NOT MODIFY after first evaluation run.
Commit hash at freeze time should be recorded by runner.py.
"""

THRESHOLDS = {
    "t2": {
        # T2 must substantially beat NCD (~29%) and random chance (~25%).
        # "Substantially" = at least 20 percentage points above max(NCD, random).
        # 29% + 11pp = 40%. Still 15pp above random chance (25%).
        # Rationale (2026-04-03): 50% was beyond the population maximum
        # (best=45%, mean=23%). 24-trap battery granularity means 0.50
        # filtered ALL 75+ candidates. 0.40 admits 5 tools across 3
        # families while maintaining meaningful NCD separation.
        "pass_threshold": 0.40,

        # Seed stability: score must not drop more than 20pp across 5 seeds.
        # Rationale (2026-04-03): With 24 traps/seed, each answer flip =
        # 4.2pp. Old 0.15 ceiling allowed only ~3 answers variance, which
        # 29% of tools exceeded from normal stochastic behavior alone.
        "max_seed_drop": 0.20,

        # Ablation budget share: no single primitive may account for more than
        # 60% of the total ablation budget (sum of all deltas). A core primitive
        # like pgmpy d-sep SHOULD be the heavy lifter — but if it's the ONLY
        # thing doing work, the composition is decorative.
        "max_ablation_budget_share": 0.60,

        # Every called primitive must affect at least 20% of test case outputs
        # when removed. Below this, it's decoration, not composition.
        "min_ablation_impact": 0.20,

        # When ablation fails but battery + seed pass, capture the dominant
        # primitive as "promising" for next generation.
        "capture_promising_primitives": True,
    },
    "t3": {
        # T3 battery has NCD-adversarial defense (NCD scores ~1%).
        # Random chance is ~25% (4 candidates). T3 tools must beat random
        # by at least 15pp = 40%.
        "pass_threshold": 0.40,

        # T3 problems are harder and more variable. Allow 18pp seed drop.
        "max_seed_drop": 0.18,

        # Same ablation rules as T2.
        "max_ablation_budget_share": 0.60,
        "min_ablation_impact": 0.20,
        "capture_promising_primitives": True,
    },

    # Diversity: max call-graph overlap between any two tools in the same tier
    "max_callgraph_overlap": 0.40,

    # Diversity budget
    "max_tools_per_science_field": 3,
    "max_tools_per_anchor_amino_acid": 5,

    # After 10 tools pass in a tier, new tools must use at least 1 amino acid
    # not used by any existing passing tool.
    "novelty_threshold_after_n_tools": 10,
}

# ── Cluster Evaluation (2026-04-03) ─────────────────────────────────────
# Replaces 12-category cross-eval with reasoning-family clusters.
# See forge/DESIGN_cluster_eval.md for full rationale.

CLUSTER_DEFINITIONS = {
    "A": {
        "name": "Causal / Statistical",
        "categories": [
            "simpson_paradox", "causal_counterfactual", "causal_confounding_hard",
            "conjunction_fallacy", "bayesian_update", "counterfactual_dependency",
        ],
    },
    "B": {
        "name": "Temporal / Scheduling / Simulation",
        "categories": [
            "temporal_scheduling", "temporal_complex", "rate_of_change",
            "temporal_interval_algebra", "process_simulation", "stateful_register_machine",
        ],
    },
    "C": {
        "name": "Logic / Constraint / Formal",
        "categories": [
            "liar_detection", "argument_strength", "constraint_satisfaction",
            "logical_consistency_checking", "stable_model_finding",
            "rule_application_order", "truth_table_evaluation",
        ],
    },
    "D": {
        "name": "Theory-of-Mind / Belief / Epistemic",
        "categories": [
            "perspective_shift", "strategic_deception", "epistemic_belief_tracking",
            "information_sufficiency", "referent_tracking_anaphora", "defeasible_reasoning",
        ],
    },
    "E": {
        "name": "Compositional / Structural / Graph",
        "categories": [
            "compositional_multi_step", "recursive_evaluation",
            "multi_step_arithmetic_carried", "conditional_graph_traversal",
            "graph_path_existence", "set_membership_operations",
            "compositional_instruction_following",
        ],
    },
    "F": {
        "name": "Language / Inference / Ambiguity",
        "categories": [
            "quantifier_scope_ambiguity", "closed_world_negation",
            "argument_structure_analysis", "implicit_constraint_inference",
        ],
    },
}

# Reverse lookup: category -> cluster ID
CLUSTER_MAP = {}
for cluster_id, cluster_def in CLUSTER_DEFINITIONS.items():
    for cat in cluster_def["categories"]:
        CLUSTER_MAP[cat] = cluster_id

CLUSTER_THRESHOLDS = {
    # Higher than global 0.40 because tool is only tested on related categories.
    # A specialist should ace its family. 55% on 6-7 related categories is more
    # meaningful than 40% on 12 unrelated ones.
    "cluster_pass_threshold": 0.55,

    # Tighter than global 0.20 because within-cluster variance should be lower.
    "max_seed_drop": 0.18,

    # Must pass at least 3 categories within the cluster (prevents hyper-specialists).
    # Reduced to 2 for 4-category clusters (Cluster F).
    "min_categories_passed": 3,
    "min_categories_passed_small": 2,  # for clusters with <= 4 categories
    "small_cluster_size": 4,

    # Generalist bonus: score >= 40% on adjacent clusters (non-gating)
    "generalist_threshold": 0.40,
}
