"""
FROZEN THRESHOLDS — Pre-committed before any tool evaluation.
DO NOT MODIFY after first evaluation run.
Commit hash at freeze time should be recorded by runner.py.
"""

THRESHOLDS = {
    "t2": {
        # T2 must substantially beat NCD (~29%) and random chance (~25%).
        # "Substantially" = at least 20 percentage points above max(NCD, random).
        # 29% + 20% = 49%, round up to 50%.
        "pass_threshold": 0.50,

        # Seed stability: score must not drop more than 15pp across 5 seeds.
        # Rationale: 15pp allows legitimate variance in problem difficulty
        # across seeds while catching overfitting to template structure.
        "max_seed_drop": 0.15,

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
