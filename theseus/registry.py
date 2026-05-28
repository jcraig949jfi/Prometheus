"""Theseus generator registry — maps generator_id → Generator class.

Active generators live under theseus/generators/<gid>_*.py.
Stub generators live under theseus/generators/stubs/all_stubs.py.

When a stub is filled in: lift the class out of all_stubs.py into a
dedicated module, then update this registry.
"""
from __future__ import annotations

from typing import Dict, Type

from theseus.generators.base import Generator
from theseus.generators.a1_catalog_cross_product import A1CatalogCrossProductGenerator
from theseus.generators.a2_statistical_correlation import A2StatisticalCorrelationGenerator
from theseus.generators.a3_functional_identity import A3FunctionalIdentityGenerator
from theseus.generators.a4_symbolic_regression import A4SymbolicRegressionGenerator
from theseus.generators.a5_distribution_match import A5DistributionMatchGenerator
from theseus.generators.b1_operator_rotation import B1OperatorRotationGenerator
from theseus.generators.b2_composition_test import B2CompositionTestGenerator
from theseus.generators.b3_inverse_test import B3InverseTestGenerator
from theseus.generators.b4_fixed_point_hunt import B4FixedPointHuntGenerator
from theseus.generators.b5_conservation_law import B5ConservationLawGenerator
from theseus.generators.c1_claim_mutation import C1ClaimMutationGenerator
from theseus.generators.c2_threshold_mutation import C2ThresholdMutationGenerator
from theseus.generators.c3_region_slide import C3RegionSlideGenerator
from theseus.generators.c4_generalization import C4GeneralizationGenerator
from theseus.generators.c5_specialization import C5SpecializationGenerator
from theseus.generators.d1_kill_neighborhood import D1KillNeighborhoodGenerator
from theseus.generators.d2_margin_bracket import D2MarginBracketGenerator
from theseus.generators.d3_triangulation_seeds import D3TriangulationSeedsGenerator
from theseus.generators.d4_boundary_crossing import D4BoundaryCrossingGenerator
from theseus.generators.e1_research_batch_parser import E1ResearchBatchParserGenerator
from theseus.generators.e2_arxiv_abstract_mining import E2ArxivAbstractMiningGenerator
from theseus.generators.e3_oeis_mining import E3OEISMiningGenerator
from theseus.generators.e4_lmfdb_knowledge_mining import E4LMFDBKnowledgeMiningGenerator
from theseus.generators.e5_mathworld_wikipedia_scrape import E5MathWorldWikipediaScrapeGenerator
from theseus.generators.f1_monte_carlo_random_pairs import F1MonteCarloRandomPairsGenerator
from theseus.generators.g1_galois_twist import G1GaloisTwistGenerator
from theseus.generators.g2_functional_equation import G2FunctionalEquationGenerator
from theseus.generators.g3_modular_transform import G3ModularTransformGenerator
from theseus.generators.f2_anti_frequency import F2AntiFrequencyGenerator
from theseus.generators.f3_importance_sampling import F3ImportanceSamplingGenerator
from theseus.generators.f4_frontier_pursuit import F4FrontierPursuitGenerator
from theseus.generators.g4_reflection_duality import G4ReflectionDualityGenerator
from theseus.generators.g5_scale_invariance import G5ScaleInvarianceGenerator
from theseus.generators.h1_self_play_hunter import H1SelfPlayHunterGenerator
from theseus.generators.h2_triangulation_protocol import H2TriangulationProtocolGenerator
from theseus.generators.h4_bridge_extension import H4BridgeExtensionGenerator
# Fire #142 (2026-05-27) — 5 new gens to break the 26-template monoculture.
# See pivot/techne_5gen_plan_2026-05-27.md.
from theseus.generators.k1_typed_bridge import K1TypedBridgeGenerator
from theseus.generators.l1_obstruction import L1ObstructionGenerator
from theseus.generators.m1_minimal_counterexample import (
    M1MinimalCounterexampleGenerator,
)
from theseus.generators.n1_active_disagreement import N1ActiveDisagreementGenerator
from theseus.generators.o1_conjecture_neighborhood import (
    O1ConjectureNeighborhoodGenerator,
)
# 2026-05-28 — 15 more gens from ChatGPT remainder + Sphinx ontology.
# See pivot/techne_15gen_plan_2026-05-28.md.
from theseus.generators.l2_formalization_skeleton import L2FormalizationSkeletonGenerator
from theseus.generators.m2_compression import M2CompressionGenerator
from theseus.generators.p1_modus_ponens_chain import P1ModusPonensChainGenerator
from theseus.generators.q1_modular_varying_p import Q1ModularVaryingPGenerator
from theseus.generators.r1_subset_relation import R1SubsetRelationGenerator
from theseus.generators.s1_triangle_inequality import S1TriangleInequalityGenerator
from theseus.generators.t1_multi_hop_deduction import T1MultiHopDeductionGenerator
from theseus.generators.u1_quantifier_swap import U1QuantifierSwapGenerator
from theseus.generators.v1_counterfactual_invariance import V1CounterfactualInvarianceGenerator
from theseus.generators.w1_closure_under_operation import W1ClosureUnderOperationGenerator
from theseus.generators.x1_partial_information import X1PartialInformationGenerator
from theseus.generators.y1_analogical_transfer import Y1AnalogicalTransferGenerator
from theseus.generators.z1_order_dependence import Z1OrderDependenceGenerator
from theseus.generators.aa1_confidence_calibration import Aa1ConfidenceCalibrationGenerator
from theseus.generators.bb1_false_dichotomy import Bb1FalseDichotomyGenerator
from theseus.generators.stubs.all_stubs import (
    H3LearnerCuriosity,
    I1ConjectureParaphrasing,
    I2DomainAnalogy,
    I3CounterExampleProposer,
    I4TheoremDecomposition,
    J1TargetedDeepResearch,
    J2AdversarialTournament,
    J3BridgeProposal,
)


REGISTRY: Dict[str, Type[Generator]] = {
    # Active
    "a1": A1CatalogCrossProductGenerator,
    "a2": A2StatisticalCorrelationGenerator,
    "a3": A3FunctionalIdentityGenerator,
    "a4": A4SymbolicRegressionGenerator,
    "a5": A5DistributionMatchGenerator,
    "b1": B1OperatorRotationGenerator,
    "b2": B2CompositionTestGenerator,
    "b3": B3InverseTestGenerator,
    "b4": B4FixedPointHuntGenerator,
    "b5": B5ConservationLawGenerator,
    "c1": C1ClaimMutationGenerator,
    "c2": C2ThresholdMutationGenerator,
    "c3": C3RegionSlideGenerator,
    "c4": C4GeneralizationGenerator,
    "c5": C5SpecializationGenerator,
    "d1": D1KillNeighborhoodGenerator,
    "d2": D2MarginBracketGenerator,
    "d3": D3TriangulationSeedsGenerator,
    "d4": D4BoundaryCrossingGenerator,
    "e1": E1ResearchBatchParserGenerator,
    "e2": E2ArxivAbstractMiningGenerator,
    "e3": E3OEISMiningGenerator,
    "e4": E4LMFDBKnowledgeMiningGenerator,
    "e5": E5MathWorldWikipediaScrapeGenerator,
    "f1": F1MonteCarloRandomPairsGenerator,
    "g1": G1GaloisTwistGenerator,
    "g2": G2FunctionalEquationGenerator,
    "g3": G3ModularTransformGenerator,
    "f2": F2AntiFrequencyGenerator,
    "f3": F3ImportanceSamplingGenerator,
    "f4": F4FrontierPursuitGenerator,
    "g4": G4ReflectionDualityGenerator,
    "g5": G5ScaleInvarianceGenerator,
    "h1": H1SelfPlayHunterGenerator,
    "h2": H2TriangulationProtocolGenerator,
    "h4": H4BridgeExtensionGenerator,
    # Fire #142 monoculture-breakers (real, Stages 11-15)
    "k1": K1TypedBridgeGenerator,
    "l1": L1ObstructionGenerator,
    "m1": M1MinimalCounterexampleGenerator,
    "n1": N1ActiveDisagreementGenerator,
    "o1": O1ConjectureNeighborhoodGenerator,
    # 2026-05-28 second batch — ChatGPT remainder + Sphinx ontology (stubs)
    "l2": L2FormalizationSkeletonGenerator,
    "m2": M2CompressionGenerator,
    "p1": P1ModusPonensChainGenerator,
    "q1": Q1ModularVaryingPGenerator,
    "r1": R1SubsetRelationGenerator,
    "s1": S1TriangleInequalityGenerator,
    "t1": T1MultiHopDeductionGenerator,
    "u1": U1QuantifierSwapGenerator,
    "v1": V1CounterfactualInvarianceGenerator,
    "w1": W1ClosureUnderOperationGenerator,
    "x1": X1PartialInformationGenerator,
    "y1": Y1AnalogicalTransferGenerator,
    "z1": Z1OrderDependenceGenerator,
    "aa1": Aa1ConfidenceCalibrationGenerator,
    "bb1": Bb1FalseDichotomyGenerator,
    # Stubs (placeholder, never emit)
    "h3": H3LearnerCuriosity,
    "i1": I1ConjectureParaphrasing,
    "i2": I2DomainAnalogy,
    "i3": I3CounterExampleProposer,
    "i4": I4TheoremDecomposition,
    "j1": J1TargetedDeepResearch,
    "j2": J2AdversarialTournament,
    "j3": J3BridgeProposal,
}


def get_generator_class(gid: str) -> Type[Generator]:
    if gid not in REGISTRY:
        raise KeyError(
            f"Unknown generator '{gid}'. Available: {sorted(REGISTRY.keys())}"
        )
    return REGISTRY[gid]


def list_active() -> list[str]:
    """Return generator_ids whose status is ACTIVE (not stub)."""
    from theseus.generators.base import GeneratorStatus

    return [
        gid
        for gid, cls in REGISTRY.items()
        if getattr(cls, "status", None) == GeneratorStatus.ACTIVE
    ]
