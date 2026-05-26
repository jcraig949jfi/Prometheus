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

# Order matters for round-robin tie-break: lower-tier (S before A)
# get priority. Within a tier, spec_phase order.
_PLUGINS: list[GeneratorPlugin] = [
    IntersectionGenerator(),
    ContrastGenerator(),
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
