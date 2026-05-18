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
from theseus.generators.b5_conservation_law import B5ConservationLawGenerator
from theseus.generators.c1_claim_mutation import C1ClaimMutationGenerator
from theseus.generators.d1_kill_neighborhood import D1KillNeighborhoodGenerator
from theseus.generators.e1_research_batch_parser import E1ResearchBatchParserGenerator
from theseus.generators.stubs.all_stubs import (
    A2StatisticalCorrelation,
    A3FunctionalIdentity,
    A4RatioInvariance,
    A5DistributionMatch,
    B1OperatorRotation,
    B2CompositionTest,
    B3InverseTest,
    B4FixedPointHunt,
    C2ThresholdMutation,
    C3RegionSlide,
    C4Generalization,
    C5Specialization,
    D2MarginBracket,
    D3TriangulationSeeds,
    D4BoundaryCrossing,
    E2ArxivAbstractMining,
    E3OEISCommentMining,
    E4LMFDBKnowledgeMining,
    E5MathWorldWikipediaScrape,
    F1MonteCarloRandomPairs,
    F2AntiFrequencySampling,
    F3ImportanceSampling,
    F4FrontierPursuit,
    G1GaloisTwist,
    G2FunctionalEquation,
    G3ModularTransform,
    G4ReflectionDuality,
    G5ScaleInvariance,
    H1MutationFromKill,
    H2TriangulationProtocol,
    H3LearnerCuriosity,
    H4BridgeExtension,
    I1ConjectureParaphrasing,
    I2DomainAnalogy,
    I3CounterExampleProposer,
    I4TheoremDecomposition,
    J1TargetedDeepResearch,
    J2AdversarialTournament,
    J3BridgeProposal,
)


REGISTRY: Dict[str, Type[Generator]] = {
    # Active (v0.1)
    "a1": A1CatalogCrossProductGenerator,
    "b5": B5ConservationLawGenerator,
    "c1": C1ClaimMutationGenerator,
    "d1": D1KillNeighborhoodGenerator,
    "e1": E1ResearchBatchParserGenerator,
    # Stubs
    "a2": A2StatisticalCorrelation,
    "a3": A3FunctionalIdentity,
    "a4": A4RatioInvariance,
    "a5": A5DistributionMatch,
    "b1": B1OperatorRotation,
    "b2": B2CompositionTest,
    "b3": B3InverseTest,
    "b4": B4FixedPointHunt,
    "c2": C2ThresholdMutation,
    "c3": C3RegionSlide,
    "c4": C4Generalization,
    "c5": C5Specialization,
    "d2": D2MarginBracket,
    "d3": D3TriangulationSeeds,
    "d4": D4BoundaryCrossing,
    "e2": E2ArxivAbstractMining,
    "e3": E3OEISCommentMining,
    "e4": E4LMFDBKnowledgeMining,
    "e5": E5MathWorldWikipediaScrape,
    "f1": F1MonteCarloRandomPairs,
    "f2": F2AntiFrequencySampling,
    "f3": F3ImportanceSampling,
    "f4": F4FrontierPursuit,
    "g1": G1GaloisTwist,
    "g2": G2FunctionalEquation,
    "g3": G3ModularTransform,
    "g4": G4ReflectionDuality,
    "g5": G5ScaleInvariance,
    "h1": H1MutationFromKill,
    "h2": H2TriangulationProtocol,
    "h3": H3LearnerCuriosity,
    "h4": H4BridgeExtension,
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
