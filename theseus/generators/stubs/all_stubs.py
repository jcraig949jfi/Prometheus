"""35 stub generators — scaffolded for batch rotation.

Each class declares identity (generator_id, claim_kind, description)
without implementing next(). The daemon recognizes StubGenerator
instances and skips them in active-set selection.

Lift any stub into its own module under theseus/generators/<gid>_*.py
when implementing.
"""
from __future__ import annotations

from theseus.emit.record_schema import ClaimKind
from theseus.generators.base import StubGenerator, GeneratorStatus


# -- Family A (catalog cross-product) --

class A4RatioInvariance(StubGenerator):
    generator_id = "a4"
    claim_kind = ClaimKind.RATIO_INVARIANCE.value
    def description(self) -> str:
        return "a4: i(a)/j(b) constant-across-population test"


class A5DistributionMatch(StubGenerator):
    generator_id = "a5"
    claim_kind = ClaimKind.DISTRIBUTION_MATCH.value
    def description(self) -> str:
        return "a5: cross-catalog invariant distribution KS-match"


# -- Family B (operator-action) --

class B2CompositionTest(StubGenerator):
    generator_id = "b2"
    claim_kind = ClaimKind.COMPOSITION_TEST.value
    def description(self) -> str:
        return "b2: (op1 ∘ op2)(x) == (op2 ∘ op1)(x) commutativity test"


class B3InverseTest(StubGenerator):
    generator_id = "b3"
    claim_kind = ClaimKind.COMPOSITION_TEST.value
    def description(self) -> str:
        return "b3: op^-1(op(x)) == x inverse test (for invertibles)"


class B4FixedPointHunt(StubGenerator):
    generator_id = "b4"
    claim_kind = ClaimKind.OPERATOR_ROTATION.value
    def description(self) -> str:
        return "b4: op(x) == x non-trivial fixed-point hunt"


# -- Family C (mutation) --

class C3RegionSlide(StubGenerator):
    generator_id = "c3"
    claim_kind = ClaimKind.MUTATION.value
    def description(self) -> str:
        return "c3: coordinate-chart region slide"


class C5Specialization(StubGenerator):
    generator_id = "c5"
    claim_kind = ClaimKind.MUTATION.value
    def description(self) -> str:
        return "c5: add-a-constraint specialization mutation"


# -- Family D (kill-neighborhood) --

class D3TriangulationSeeds(StubGenerator):
    generator_id = "d3"
    claim_kind = ClaimKind.KILL_NEIGHBORHOOD.value
    def description(self) -> str:
        return "d3: INCONCLUSIVE → adjacent precision/method triangulation seeds"


class D4BoundaryCrossing(StubGenerator):
    generator_id = "d4"
    claim_kind = ClaimKind.KILL_NEIGHBORHOOD.value
    def description(self) -> str:
        return "d4: minimum-distance (PASS, KILL) boundary pair generation"


# -- Family E (literature mining) --

class E2ArxivAbstractMining(StubGenerator):
    generator_id = "e2"
    claim_kind = ClaimKind.LITERATURE_MINED.value
    def description(self) -> str:
        return "e2: arXiv abstract mining (paperswithcode/semantic-scholar)"


class E3OEISCommentMining(StubGenerator):
    generator_id = "e3"
    claim_kind = ClaimKind.LITERATURE_MINED.value
    def description(self) -> str:
        return "e3: OEIS sequence-comment mining (1M+ informal claims)"


class E4LMFDBKnowledgeMining(StubGenerator):
    generator_id = "e4"
    claim_kind = ClaimKind.LITERATURE_MINED.value
    def description(self) -> str:
        return "e4: LMFDB knowledge-node mining"


class E5MathWorldWikipediaScrape(StubGenerator):
    generator_id = "e5"
    claim_kind = ClaimKind.LITERATURE_MINED.value
    def description(self) -> str:
        return "e5: Mathworld/Wikipedia conjecture-list scrape"


# -- Family F (probabilistic) --

class F1MonteCarloRandomPairs(StubGenerator):
    generator_id = "f1"
    claim_kind = ClaimKind.INVARIANT_EQUALITY.value
    def description(self) -> str:
        return "f1: uniform-random catalog-pair sampling (anti-recommended)"


class F2AntiFrequencySampling(StubGenerator):
    generator_id = "f2"
    claim_kind = ClaimKind.INVARIANT_EQUALITY.value
    def description(self) -> str:
        return "f2: anti-frequency stratified sampling of under-tested regions"


class F4FrontierPursuit(StubGenerator):
    generator_id = "f4"
    claim_kind = ClaimKind.INVARIANT_EQUALITY.value
    def description(self) -> str:
        return "f4: frontier-pursuit at coverage boundary"


# -- Family G (symmetry/transformation) --

class G1GaloisTwist(StubGenerator):
    generator_id = "g1"
    claim_kind = ClaimKind.SYMMETRY_TRANSFORM.value
    def description(self) -> str:
        return "g1: Galois-twist invariance test"


class G2FunctionalEquation(StubGenerator):
    generator_id = "g2"
    claim_kind = ClaimKind.SYMMETRY_TRANSFORM.value
    def description(self) -> str:
        return "g2: L(s) ↔ L(k-s) functional-equation symmetry"


class G3ModularTransform(StubGenerator):
    generator_id = "g3"
    claim_kind = ClaimKind.SYMMETRY_TRANSFORM.value
    def description(self) -> str:
        return "g3: SL_2(Z) modular-transform test"


class G4ReflectionDuality(StubGenerator):
    generator_id = "g4"
    claim_kind = ClaimKind.SYMMETRY_TRANSFORM.value
    def description(self) -> str:
        return "g4: x↔-x, ζ↔ζ̄ reflection-duality"


class G5ScaleInvariance(StubGenerator):
    generator_id = "g5"
    claim_kind = ClaimKind.SYMMETRY_TRANSFORM.value
    def description(self) -> str:
        return "g5: conformal / scaling-invariance test"


# -- Family H (self-feeding) --

class H2TriangulationProtocol(StubGenerator):
    generator_id = "h2"
    claim_kind = ClaimKind.KILL_NEIGHBORHOOD.value
    def description(self) -> str:
        return "h2: INCONCLUSIVE H5 triangulation protocol generator"


class H3LearnerCuriosity(StubGenerator):
    generator_id = "h3"
    claim_kind = ClaimKind.OTHER.value
    status = GeneratorStatus.STUB_FUTURE
    def description(self) -> str:
        return "h3: Learner-curiosity (FUTURE — depends on Ergon resume)"


class H4BridgeExtension(StubGenerator):
    generator_id = "h4"
    claim_kind = ClaimKind.BRIDGE_EXTENSION.value
    def description(self) -> str:
        return "h4: verified X↔Y → propose X↔Z bridge extension"


# -- Family I (local LLM, Tier 2) --

class I1ConjectureParaphrasing(StubGenerator):
    generator_id = "i1"
    claim_kind = ClaimKind.LITERATURE_MINED.value
    status = GeneratorStatus.STUB_TIER2
    def description(self) -> str:
        return "i1: structured-tuple → NL conjecture paraphrasing (Tier 2)"


class I2DomainAnalogy(StubGenerator):
    generator_id = "i2"
    claim_kind = ClaimKind.BRIDGE_EXTENSION.value
    status = GeneratorStatus.STUB_TIER2
    def description(self) -> str:
        return "i2: domain-analogy proposer (Tier 2 local LLM)"


class I3CounterExampleProposer(StubGenerator):
    generator_id = "i3"
    claim_kind = ClaimKind.OTHER.value
    status = GeneratorStatus.STUB_TIER2
    def description(self) -> str:
        return "i3: counter-example proposer (Tier 2 local LLM)"


class I4TheoremDecomposition(StubGenerator):
    generator_id = "i4"
    claim_kind = ClaimKind.LITERATURE_MINED.value
    status = GeneratorStatus.STUB_TIER2
    def description(self) -> str:
        return "i4: theorem-statement atomic decomposition (Tier 2 local LLM)"


# -- Family J (frontier API, Tier 3) --

class J1TargetedDeepResearch(StubGenerator):
    generator_id = "j1"
    claim_kind = ClaimKind.LITERATURE_MINED.value
    status = GeneratorStatus.STUB_TIER3
    def description(self) -> str:
        return "j1: targeted deep-research (Tier 3 frontier API)"


class J2AdversarialTournament(StubGenerator):
    generator_id = "j2"
    claim_kind = ClaimKind.OTHER.value
    status = GeneratorStatus.STUB_TIER3
    def description(self) -> str:
        return "j2: adversarial counter-example tournament (Tier 3 frontier API)"


class J3BridgeProposal(StubGenerator):
    generator_id = "j3"
    claim_kind = ClaimKind.BRIDGE_EXTENSION.value
    status = GeneratorStatus.STUB_TIER3
    def description(self) -> str:
        return "j3: cross-catalog bridge proposal (Tier 3 frontier API)"
