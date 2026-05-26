"""Erebos generator-plugin registry.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md: Erebos hosts up
to 25 hypothesis-generator archetypes as plugins. Each plugin
conforms to GeneratorPlugin protocol (charon/agents/erebos/generators
/_base.py) and implements the six-field Erebos Implementation Spec.

This module exposes:
  - REGISTRY: dict[plugin_id, instance]
  - applicable_plugins(state): iterator over plugins whose
    applicable(state) returns True
  - next_plugin_round_robin(state, last_id): pick the next applicable
    plugin in round-robin order, skipping non-applicable

Plugins are added by:
  1. Drop g<NN>_<name>.py in this directory.
  2. Add `from .gNN_name import NameGenerator` below.
  3. Add NameGenerator() to _PLUGINS list.

Registry refuses entries that don't conform to the six-field spec
(checked via Protocol structural typing at instantiation time).
"""
from __future__ import annotations

from typing import Iterator, Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    GeneratorPlugin,
    SwarmState,
)
from charon.agents.erebos.generators.g01_intersection import IntersectionGenerator
from charon.agents.erebos.generators.g02_contrast import ContrastGenerator
from charon.agents.erebos.generators.g04_survivor_tightening import SurvivorTighteningGenerator
from charon.agents.erebos.generators.g09_projection_collapse import ProjectionCollapseGenerator
from charon.agents.erebos.generators.g12_invariant_substitution import InvariantSubstitutionGenerator
from charon.agents.erebos.generators.g13_relation_weakening import RelationWeakeningGenerator
from charon.agents.erebos.generators.g14_relation_strengthening import RelationStrengtheningGenerator
from charon.agents.erebos.generators.g22_subgraph_clique import SubgraphCliqueGenerator
from charon.agents.erebos.generators.g25_degeneracy import DegeneracyGenerator

# Order matters for round-robin tie-break: lower-tier (S before A)
# get priority. Within a tier, spec_phase order. v0.10 ordering:
# Tier S first (G01, G02, G09); then Tier A (G12, G13, G14, G22, G25);
# then Tier B (G04).
_PLUGINS: list[GeneratorPlugin] = [
    IntersectionGenerator(),           # Phase 1, Tier S
    ContrastGenerator(),               # Phase 1, Tier S
    ProjectionCollapseGenerator(),     # Phase 2, Tier S
    InvariantSubstitutionGenerator(),  # Phase 3, Tier A
    RelationWeakeningGenerator(),      # Phase 3, Tier A
    RelationStrengtheningGenerator(),  # Phase 3, Tier A
    SubgraphCliqueGenerator(),         # Phase 5, Tier A
    DegeneracyGenerator(),             # Phase 5, Tier A
    SurvivorTighteningGenerator(),     # Phase 1, Tier B
]

REGISTRY: dict[str, GeneratorPlugin] = {p.id: p for p in _PLUGINS}


def applicable_plugins(state: SwarmState) -> list[GeneratorPlugin]:
    """Return list of plugins whose applicable(state) is True."""
    return [p for p in _PLUGINS if p.applicable(state)]


def next_plugin_round_robin(
    state: SwarmState, last_plugin_id: Optional[str]
) -> Optional[GeneratorPlugin]:
    """Pick the next applicable plugin, advancing past last_plugin_id
    if any. Returns None if no plugin is applicable this tick."""
    applicable = applicable_plugins(state)
    if not applicable:
        return None
    if not last_plugin_id:
        return applicable[0]
    # Find last_plugin_id in the ordered _PLUGINS list and advance
    try:
        idx = next(
            i for i, p in enumerate(_PLUGINS) if p.id == last_plugin_id
        )
    except StopIteration:
        return applicable[0]
    # Walk forward from idx+1 looking for the next applicable
    n = len(_PLUGINS)
    for offset in range(1, n + 1):
        candidate = _PLUGINS[(idx + offset) % n]
        if candidate in applicable:
            return candidate
    return applicable[0]
