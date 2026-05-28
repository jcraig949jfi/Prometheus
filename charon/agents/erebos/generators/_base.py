"""Erebos generator-plugin protocol.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md non-negotiable
design rule: 'No conjecture confetti. Every generation must carry
its own falsification route.'

Every plugin MUST implement:
  - id: short canonical id (e.g., 'g01_intersection')
  - name: human-readable name (e.g., 'Intersection Composer')
  - spec_phase: 1-5 per the 25-archetype spec
  - feasibility_tier: 'S' / 'A' / 'B' / 'C' (Charon-swarm-specific
    rank, NOT the spec's intrinsic-difficulty rank)
  - applicable(swarm_state) -> bool: does this generator have valid
    inputs available right now?
  - generate(swarm_state) -> Optional[ComposedClaim]: produce one
    candidate-claim or None if generation isn't possible this tick
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Protocol


@dataclass
class SwarmState:
    """Snapshot of substrate state passed to each plugin per tick.

    Populated once per Erebos tick from the various kill_ledgers and
    artifact reads. Plugins consume from this snapshot rather than
    re-reading sources per call.
    """
    stygian_substantive: list[dict] = field(default_factory=list)
    pollux_substantive: list[dict] = field(default_factory=list)
    hecate_crossgen_canonical: list[str] = field(default_factory=list)
    erebos_self_ledger: list[dict] = field(default_factory=list)
    tried_pairs: set = field(default_factory=set)
    tick_counter: int = 0


@dataclass
class ComposedClaim:
    """Structured output every plugin must produce.

    Mirrors the Erebos Implementation Spec's six required fields
    (input provenance, transformation, output claim text, falsification
    route, expected kill pattern, loader feasibility note). Plus
    routing metadata so Stygian + Hecate consume it correctly.
    """
    # Required structured fields (six-field spec)
    plugin_id: str  # e.g., 'g01_intersection'
    composed_id: str  # unique per emission, e.g., 'EREBOS-G02-BL-C-005-x-CM_vs_nonCM'
    input_provenance: dict  # which input rows/patterns were consumed
    transformation_description: str  # what the plugin did
    output_claim_text: str  # the actual candidate-claim statement
    falsification_route: str  # specific battery shape + restriction
    expected_kill_pattern: str  # label Hecate will see if claim fails
    loader_feasibility_note: str  # what a battery loader would need

    # Routing metadata
    parent_record_ids: list[str] = field(default_factory=list)
    composition_payload: dict = field(default_factory=dict)
    extras: dict = field(default_factory=dict)

    # v3 Phase 0 ITER-25: optional machine-evaluable substrate alongside
    # claim text. M3 -> M4 representation lift on the Reasoning Ladder.
    # See charon/agents/erebos/generators/_predicate_handles.py
    # Type kept as Any to avoid a circular import; PredicateHandle protocol
    # is structurally enforced via duck-typing at consumer sites.
    predicate_handle: Optional[Any] = None

    # v3 Phase 0 ITER-27: epistemic-economy cost/value prices per emission.
    # value_per_tick = sum(info_gain * reuse_value) / sum(costs).
    # generation_cost is set by the daemon when wrapping plugin.generate();
    # falsification_cost is set when the loader executes; information_gain
    # and reuse_value are computed post-hoc by _value_metrics.
    generation_cost_seconds: float = 0.0
    falsification_cost_seconds: Optional[float] = None
    information_gain_nats: Optional[float] = None
    reuse_value_count: int = 0


class GeneratorPlugin(Protocol):
    """Plugin contract. Implementations live in g<NN>_<name>.py."""
    id: str
    name: str
    spec_phase: int
    feasibility_tier: str

    def applicable(self, state: SwarmState) -> bool: ...
    def generate(self, state: SwarmState) -> Optional[ComposedClaim]: ...
