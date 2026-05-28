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
from charon.agents.erebos.generators.g03_failure_neighborhood import FailureNeighborhoodGenerator
from charon.agents.erebos.generators.g04_survivor_tightening import SurvivorTighteningGenerator
from charon.agents.erebos.generators.g05_confound_swap import ConfoundSwapGenerator
from charon.agents.erebos.generators.g06_null_space import NullSpaceGenerator
from charon.agents.erebos.generators.g07_analogy import AnalogyGenerator
from charon.agents.erebos.generators.g08_dimensional_lift import DimensionalLiftGenerator
from charon.agents.erebos.generators.g09_projection_collapse import ProjectionCollapseGenerator
from charon.agents.erebos.generators.g10_boundary import BoundaryGenerator
from charon.agents.erebos.generators.g11_exception_miner import ExceptionMinerGenerator
from charon.agents.erebos.generators.g12_invariant_substitution import InvariantSubstitutionGenerator
from charon.agents.erebos.generators.g13_relation_weakening import RelationWeakeningGenerator
from charon.agents.erebos.generators.g14_relation_strengthening import RelationStrengtheningGenerator
from charon.agents.erebos.generators.g15_cross_gen_mi import CrossGenMIGenerator
from charon.agents.erebos.generators.g16_anti_anchor import AntiAnchorGenerator
from charon.agents.erebos.generators.g17_causal_intervention import CausalInterventionGenerator
from charon.agents.erebos.generators.g18_minimal_counterexample import MinimalCounterexampleGenerator
from charon.agents.erebos.generators.g19_proof_obligation import ProofObligationGenerator
from charon.agents.erebos.generators.g20_instrument_disagreement import InstrumentDisagreementGenerator
from charon.agents.erebos.generators.g21_isomorphism_functor import IsomorphismFunctorGenerator
from charon.agents.erebos.generators.g22_subgraph_clique import SubgraphCliqueGenerator
from charon.agents.erebos.generators.g23_asymptotic_limit import AsymptoticLimitGenerator
from charon.agents.erebos.generators.g24_symmetry_twist import SymmetryTwistGenerator
from charon.agents.erebos.generators.g25_degeneracy import DegeneracyGenerator

# Order matters for round-robin tie-break: lower-tier (S before A)
# get priority. Within a tier, spec_phase order. v0.12 ordering:
# Tier S first; then Tier A; then Tier B.
_PLUGINS: list[GeneratorPlugin] = [
    IntersectionGenerator(),           # Phase 1, Tier S
    ContrastGenerator(),               # Phase 1, Tier S
    ProjectionCollapseGenerator(),     # Phase 2, Tier S
    InstrumentDisagreementGenerator(), # Phase 4, Tier S
    InvariantSubstitutionGenerator(),  # Phase 3, Tier A
    RelationWeakeningGenerator(),      # Phase 3, Tier A
    RelationStrengtheningGenerator(),  # Phase 3, Tier A
    SubgraphCliqueGenerator(),         # Phase 5, Tier A
    SymmetryTwistGenerator(),          # Phase 5, Tier A
    DegeneracyGenerator(),             # Phase 5, Tier A
    FailureNeighborhoodGenerator(),    # Phase 1, Tier B
    SurvivorTighteningGenerator(),     # Phase 1, Tier B
    DimensionalLiftGenerator(),        # Phase 2, Tier B (new v0.14)
    BoundaryGenerator(),               # Phase 2, Tier B
    ExceptionMinerGenerator(),         # Phase 3, Tier B
    CrossGenMIGenerator(),             # Phase 3, Tier B
    CausalInterventionGenerator(),     # Phase 4, Tier B
    MinimalCounterexampleGenerator(),  # Phase 4, Tier B
    AsymptoticLimitGenerator(),        # Phase 5, Tier B
    AnalogyGenerator(),                # Phase 2, Tier C
    AntiAnchorGenerator(),             # Phase 4, Tier C
    ProofObligationGenerator(),        # Phase 4, Tier C
    IsomorphismFunctorGenerator(),     # Phase 5, Tier C
    ConfoundSwapGenerator(),           # Phase 1, Tier C (new v0.15)
    NullSpaceGenerator(),              # Phase 2, Tier C (new v0.15)
]

REGISTRY: dict[str, GeneratorPlugin] = {p.id: p for p in _PLUGINS}


def applicable_plugins(
    state: SwarmState, *, include_quarantined: bool = False
) -> list[GeneratorPlugin]:
    """Return list of plugins whose applicable(state) is True.

    v3 Phase 0 ITER-28: quarantined plugins are filtered OUT of
    production runs (include_quarantined=False). Test fixtures can
    set include_quarantined=True to invoke quarantined plugins
    explicitly.
    """
    # Lazy import to avoid circular: _quarantine lives in same package
    from charon.agents.erebos._quarantine import is_quarantined
    if include_quarantined:
        return [p for p in _PLUGINS if p.applicable(state)]
    return [
        p for p in _PLUGINS
        if not is_quarantined(p.id) and p.applicable(state)
    ]


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


def _routing_action_to_plugin_id(
    routing_action: str,
) -> Optional[str]:
    """Map a kill_pattern_registry routing_action string to a plugin id.

    routing_action strings follow the convention `g<NN>_<descriptor>`
    (e.g. "g11_with_monte_carlo_g_test", "g25_v2_data_inquiry_
    precondition"). Match the leading `g<NN>_` prefix against the
    plugin id prefix (`gNN_`).

    Returns:
        The matching plugin id (e.g. "g11_exception_miner") or None
        if no plugin matches the prefix. The "none_claim_survives"
        sentinel and any non-`gNN_*` action return None — caller
        should fall back to round-robin.
    """
    if not routing_action or not routing_action.startswith("g"):
        return None
    # Extract leading "gNN_" prefix
    parts = routing_action.split("_", 1)
    if len(parts) < 2:
        return None
    prefix = parts[0] + "_"  # e.g. "g11_"
    if not prefix[1:-1].isdigit():
        return None
    # Match against plugin ids starting with this prefix
    for p in _PLUGINS:
        if p.id.startswith(prefix):
            return p.id
    return None


def next_plugin_kp_routed(
    state: SwarmState,
    last_plugin_id: Optional[str],
    last_kill_pattern: Optional[str],
) -> Optional[GeneratorPlugin]:
    """Pick the next plugin per kill_pattern routing semantics.

    Per Erebos v3 §4.4 + Phase 0 retrospective + Doctrine v1.0
    Layer 1/Seam/Layer 2 routing: when the last verdict carried a
    registered kill_pattern, use kill_pattern_registry.
    routing_action_for(kp) to pick the next plugin. Falls back to
    round-robin when:
      - no kill_pattern was supplied,
      - the kill_pattern is not in the registry,
      - the routing_action doesn't resolve to a known plugin,
      - the routed plugin is quarantined,
      - the routed plugin is not applicable to current state.

    Args:
        state: SwarmState snapshot.
        last_plugin_id: most recent plugin id, used as round-robin
            fallback anchor.
        last_kill_pattern: kp from the most recent ledger entry, or
            None if no prior kp / fresh start.

    Returns:
        Selected plugin (kp-routed if possible, else round-robin),
        or None if no plugin is applicable this tick.
    """
    # Lazy imports keep generators/__init__.py free of erebos-package
    # circular dependencies at module-load time.
    from charon.agents.erebos._kill_pattern_registry import routing_action_for
    from charon.agents.erebos._quarantine import is_quarantined

    if last_kill_pattern:
        action = routing_action_for(last_kill_pattern)
        if action is not None:
            target_id = _routing_action_to_plugin_id(action)
            if target_id and not is_quarantined(target_id):
                target_plugin = REGISTRY.get(target_id)
                if target_plugin is not None and target_plugin.applicable(state):
                    return target_plugin
    # Fall back to round-robin
    return next_plugin_round_robin(state, last_plugin_id)
