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

# -- Family B (operator-action) --

# -- Family C (mutation) --

# -- Family D (kill-neighborhood) --

# -- Family E (literature mining) --

# E2 was lifted to theseus/generators/e2_arxiv_abstract_mining.py


# E4 was lifted to theseus/generators/e4_lmfdb_knowledge_mining.py


# E5 was lifted to theseus/generators/e5_mathworld_wikipedia_scrape.py


# -- Family F (probabilistic) --

# F1 was lifted to theseus/generators/f1_monte_carlo_random_pairs.py


# -- Family G (symmetry/transformation) --

# G1 was lifted to theseus/generators/g1_galois_twist.py


# G2 was lifted to theseus/generators/g2_functional_equation.py


class G3ModularTransform(StubGenerator):
    generator_id = "g3"
    claim_kind = ClaimKind.SYMMETRY_TRANSFORM.value
    def description(self) -> str:
        return "g3: SL_2(Z) modular-transform test"


# -- Family H (self-feeding) --

class H3LearnerCuriosity(StubGenerator):
    generator_id = "h3"
    claim_kind = ClaimKind.OTHER.value
    status = GeneratorStatus.STUB_FUTURE
    def description(self) -> str:
        return "h3: Learner-curiosity (FUTURE — depends on Ergon resume)"


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
