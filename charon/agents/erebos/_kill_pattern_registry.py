"""Kill-pattern registry — machine-actionable substrate routing.

Per Erebos v3 + DR amendment §4 (kill_pattern semantics layer).
Turns the substrate's 27 named kill_patterns from decorative
annotations into machine-actionable failure gradients. Each entry
declares: repair_class (F-axis), routing_action (which plugin
fires next), confusion_class (frequently-mistaken-for set),
observable_signature (the loader-output condition that triggers
it), assignment_provenance (who/what assigned the label).

The routing layer reads `routing_action_for(kp)` to pick the next
plugin. This is the substrate's "given kill_pattern K, what should
fire next?" answer.

Reading: pivot/erebos_v3_amendment_dr_synthesis_2026-05-27.md §4
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# F-axis tiers from pivot/reasoning_ladder_v01_2026-05-24.md
VALID_REPAIR_CLASSES = {
    "F0", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8",
}

VALID_PROVENANCE = {
    "human", "loader", "model_inferred", "substrate_derived",
}


@dataclass(frozen=True)
class KillPatternSpec:
    """Per-kill_pattern routing specification.

    repair_class: F-axis tier — what kind of repair this kill_pattern
                  implies (F3 local repair, F4 global, F5 strategy,
                  F6 ontology, F7 problem, F8 epistemic).
    routing_action: plugin ID (or plugin-class identifier) the
                  substrate should fire next when this kill_pattern
                  is observed.
    confusion_class: other kill_patterns this one is often mistaken
                  for; downstream consumers should disambiguate.
    observable_signature: the loader-output condition that triggers
                  this kill_pattern. Plain-text for now; future
                  iterations may formalize as predicate.
    assignment_provenance: who assigned this label — "human" (manual
                  override), "loader" (rule-based), "model_inferred"
                  (LLM-tagged), "substrate_derived" (computed from
                  ledger statistics).
    """
    name: str
    repair_class: str
    routing_action: str
    confusion_class: tuple[str, ...]
    observable_signature: str
    assignment_provenance: str

    def __post_init__(self) -> None:
        if self.repair_class not in VALID_REPAIR_CLASSES:
            raise ValueError(
                f"KillPatternSpec {self.name!r}: invalid repair_class "
                f"{self.repair_class!r}; must be one of {VALID_REPAIR_CLASSES}"
            )
        if self.assignment_provenance not in VALID_PROVENANCE:
            raise ValueError(
                f"KillPatternSpec {self.name!r}: invalid "
                f"assignment_provenance {self.assignment_provenance!r}; "
                f"must be one of {VALID_PROVENANCE}"
            )
        if not self.observable_signature:
            raise ValueError(
                f"KillPatternSpec {self.name!r}: observable_signature "
                f"cannot be empty"
            )


# 27-row routing table per v3 amendment §4
KILL_PATTERN_REGISTRY: dict[str, KillPatternSpec] = {
    "permutation_null": KillPatternSpec(
        name="permutation_null",
        repair_class="F3",
        routing_action="g02_with_westfall_young",
        confusion_class=("boundary_collapse",),
        observable_signature="observed_divergence <= null_p95",
        assignment_provenance="loader",
    ),
    "boundary_collapse": KillPatternSpec(
        name="boundary_collapse",
        repair_class="F4",
        routing_action="g03_with_data_driven_epsilon",
        confusion_class=("weakening_too_strict", "permutation_null"),
        observable_signature="trivial_fraction >= TRIVIAL_THRESHOLD",
        assignment_provenance="loader",
    ),
    "weakening_too_strict": KillPatternSpec(
        name="weakening_too_strict",
        repair_class="F5",
        routing_action="g13_with_z3_semantic_weakening",
        confusion_class=("boundary_collapse",),
        observable_signature="trivial_fraction <= NEGLIGIBLE_THRESHOLD",
        assignment_provenance="loader",
    ),
    "strict_threshold_violation": KillPatternSpec(
        name="strict_threshold_violation",
        repair_class="F4",
        routing_action="g04_with_information_optimal_band",
        confusion_class=("permutation_null",),
        observable_signature="band_survival drops sharply at threshold",
        assignment_provenance="loader",
    ),
    "complete_signal_collapse": KillPatternSpec(
        name="complete_signal_collapse",
        repair_class="F6",
        routing_action="g05_with_notears_confounder_discovery",
        confusion_class=("permutation_null",),
        observable_signature="signal collapses under confound stratification",
        assignment_provenance="loader",
    ),
    "universal_rejection": KillPatternSpec(
        name="universal_rejection",
        repair_class="F7",
        routing_action="g06_with_wasserstein_void_selection",
        confusion_class=(),
        observable_signature="all candidates rejected in void region",
        assignment_provenance="loader",
    ),
    "metaphor_collapse": KillPatternSpec(
        name="metaphor_collapse",
        repair_class="F6",
        routing_action="g07_with_cross_domain_dataset_accessor",
        confusion_class=("functor_breaks",),
        observable_signature="analogous test in target domain fails",
        assignment_provenance="loader",
    ),
    "overfitting_goodharting": KillPatternSpec(
        name="overfitting_goodharting",
        repair_class="F5",
        routing_action="g08_with_ergon_held_out",
        confusion_class=("residual_survival",),
        observable_signature="held_out AUC drops vs train AUC",
        assignment_provenance="loader",
    ),
    "residual_survival": KillPatternSpec(
        name="residual_survival",
        repair_class="F3",
        routing_action="g09_with_cc_shapley_attribution",
        confusion_class=("overfitting_goodharting",),
        observable_signature="claim survives single-coord ablation",
        assignment_provenance="loader",
    ),
    "smooth_degradation": KillPatternSpec(
        name="smooth_degradation",
        repair_class="F3",
        routing_action="none_claim_survives",
        confusion_class=("sharp_boundary_detected",),
        observable_signature="smoothness_ratio <= SMOOTH_THRESHOLD",
        assignment_provenance="loader",
    ),
    "sharp_boundary_detected": KillPatternSpec(
        name="sharp_boundary_detected",
        repair_class="F6",
        routing_action="g10_with_bocpd_posterior",
        confusion_class=("smooth_degradation",),
        observable_signature="smoothness_ratio > SMOOTH_THRESHOLD",
        assignment_provenance="loader",
    ),
    "out_of_sample_failure": KillPatternSpec(
        name="out_of_sample_failure",
        repair_class="F5",
        routing_action="g11_with_monte_carlo_g_test",
        confusion_class=("permutation_null",),
        observable_signature="cube heterogeneity chi^2 below threshold",
        assignment_provenance="loader",
    ),
    "invariant_swap_collapses": KillPatternSpec(
        name="invariant_swap_collapses",
        repair_class="F6",
        routing_action="g12_with_learned_similarity",
        confusion_class=("metaphor_collapse",),
        observable_signature="substituted invariant fails original test",
        assignment_provenance="loader",
    ),
    "predicate_collapses_to_trivial": KillPatternSpec(
        name="predicate_collapses_to_trivial",
        repair_class="F4",
        routing_action="g13_with_z3_semantic_weakening",
        confusion_class=("boundary_collapse",),
        observable_signature="weakened predicate satisfied universally",
        assignment_provenance="loader",
    ),
    "strengthening_breaks": KillPatternSpec(
        name="strengthening_breaks",
        repair_class="F5",
        routing_action="g14_with_refinement_type_witness",
        confusion_class=("predicate_collapses_to_trivial",),
        observable_signature="strengthened predicate fails on parent's support",
        assignment_provenance="loader",
    ),
    "uncorrelated_residual_failures": KillPatternSpec(
        name="uncorrelated_residual_failures",
        repair_class="F3",
        routing_action="g15_v2_real_verdict_mi",
        confusion_class=(),
        observable_signature="MI(plugin; kp) below threshold after filter",
        assignment_provenance="loader",
    ),
    "conjecture_survives_adversarial_attack": KillPatternSpec(
        name="conjecture_survives_adversarial_attack",
        repair_class="F4",
        routing_action="g16_with_percentile_adversarial_value",
        confusion_class=("permutation_null",),
        observable_signature="anchor survival in adversarial band >= threshold",
        assignment_provenance="loader",
    ),
    "correlation_survives_intervention": KillPatternSpec(
        name="correlation_survives_intervention",
        repair_class="F6",
        routing_action="g17_with_explicit_do_operator",
        confusion_class=("conjecture_survives_adversarial_attack",),
        observable_signature="intervention divergence > null_p95",
        assignment_provenance="loader",
    ),
    "region_R_exhausted_without_counterexample": KillPatternSpec(
        name="region_R_exhausted_without_counterexample",
        repair_class="F5",
        routing_action="g18_with_voronoi_region_prediction",
        confusion_class=(),
        observable_signature="no counterexample in predicted region after exhaustive search",
        assignment_provenance="loader",
    ),
    "sub_claim_falsified": KillPatternSpec(
        name="sub_claim_falsified",
        repair_class="F3",
        routing_action="g19_v3_lean_well_foundedness",
        confusion_class=(),
        observable_signature="any obligation parent verdict = REJECTED",
        assignment_provenance="loader",
    ),
    "instrument_clash_detected": KillPatternSpec(
        name="instrument_clash_detected",
        repair_class="F8",
        routing_action="g20_v2_when_lethe_v2_ships",
        confusion_class=(),
        observable_signature="lethe verdict != stygian verdict on same conjecture",
        assignment_provenance="substrate_derived",
    ),
    "functor_breaks": KillPatternSpec(
        name="functor_breaks",
        repair_class="F6",
        routing_action="g21_with_morphism_enumerator",
        confusion_class=("metaphor_collapse",),
        observable_signature="F(morphism) fails in target domain",
        assignment_provenance="loader",
    ),
    "counterexample_breaks_master_unification": KillPatternSpec(
        name="counterexample_breaks_master_unification",
        repair_class="F5",
        routing_action="g22_with_leiden_constant_potts",
        confusion_class=(),
        observable_signature="object satisfies M but breaks clique sub-claim",
        assignment_provenance="loader",
    ),
    "error_term_does_not_decay": KillPatternSpec(
        name="error_term_does_not_decay",
        repair_class="F4",
        routing_action="g23_with_broken_power_law_bic",
        confusion_class=("decay_faster_than_1_over_N",),
        observable_signature="log-log slope > -DECAY_SLOPE_TOLERANCE",
        assignment_provenance="loader",
    ),
    "decay_faster_than_1_over_N": KillPatternSpec(
        name="decay_faster_than_1_over_N",
        repair_class="F4",
        routing_action="g23_v2_multi_law",
        confusion_class=("error_term_does_not_decay",),
        observable_signature="log-log slope < -1 - DECAY_SLOPE_TOLERANCE",
        assignment_provenance="loader",
    ),
    "symmetry_breaking": KillPatternSpec(
        name="symmetry_breaking",
        repair_class="F8",
        routing_action="g24_v3_relational_symmetry_gate",
        confusion_class=(),
        observable_signature="twisted Mahler differs from stored beyond tolerance",
        assignment_provenance="loader",
    ),
    "tautological_pass": KillPatternSpec(
        name="tautological_pass",
        repair_class="F8",
        routing_action="g25_v2_data_inquiry_precondition",
        confusion_class=(),
        observable_signature="degeneracy_precondition would have gated this emission",
        assignment_provenance="substrate_derived",
    ),
}


# --------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------

def routing_action_for(kp: str) -> Optional[str]:
    """Return the routing_action string for a kill_pattern, or None
    if the kill_pattern is unregistered."""
    spec = KILL_PATTERN_REGISTRY.get(kp)
    return spec.routing_action if spec else None


def confusion_class_for(kp: str) -> tuple[str, ...]:
    """Return the tuple of confusable kill_patterns for kp.
    Empty tuple if kp is unregistered or has no confusion class."""
    spec = KILL_PATTERN_REGISTRY.get(kp)
    return spec.confusion_class if spec else ()


def repair_class_for(kp: str) -> str:
    """Return the F-axis repair class. Raises KeyError if unknown."""
    if kp not in KILL_PATTERN_REGISTRY:
        raise KeyError(f"kill_pattern {kp!r} not in registry")
    return KILL_PATTERN_REGISTRY[kp].repair_class


def assignment_provenance_for(kp: str) -> Optional[str]:
    """Return who/what assigned this kill_pattern label."""
    spec = KILL_PATTERN_REGISTRY.get(kp)
    return spec.assignment_provenance if spec else None


def observable_signature_for(kp: str) -> Optional[str]:
    """Return the loader-output condition that triggers this kp."""
    spec = KILL_PATTERN_REGISTRY.get(kp)
    return spec.observable_signature if spec else None


def all_registered_kill_patterns() -> list[str]:
    """Return sorted list of all registered kill_patterns."""
    return sorted(KILL_PATTERN_REGISTRY.keys())


def kill_patterns_by_repair_class(repair_class: str) -> list[str]:
    """Return sorted list of kill_patterns at a given F-axis tier."""
    return sorted(
        kp for kp, spec in KILL_PATTERN_REGISTRY.items()
        if spec.repair_class == repair_class
    )
