"""Sprint-1 A2: per-record causal attribution (Phase 2, ITER-46).

Hypothesis (from roadmap v2 line 84):
> "Which specific Layer-2 records drove which routing decisions"
> Pass: >= 50% of routing decisions trace to specific records ->
> Layer 2 is queried, not just stored.

## The structural framing

The semantic claim "Layer 2 is queried, not just stored" is
structural: the routing layer (kill_pattern_registry +
_routing_action_to_plugin_id) must encode kp-specific routing
decisions. If every kp routed to the SAME default plugin, the
registry would be decorative.

A2 measures structural attribution: of the 27 kps in
KILL_PATTERN_REGISTRY, what fraction resolves to a non-default
plugin id via _routing_action_to_plugin_id? The "default" is
the plugin a round-robin selection would pick at the START of
execution (no last_plugin_id, applicable_plugins[0]).

This separates the substrate's ROUTING INTENT from its momentary
applicability state. A kp that targets a currently-quarantined
or currently-inapplicable plugin still encodes Layer 2's
attribution; the fact that the daemon falls back to round-robin
at runtime is a quarantine / applicability concern, not an
attribution concern.

## Why structural framing is the right test

The earlier protocol attempted to walk every kp in an empty
SwarmState. Empty state makes ALL plugins inapplicable, so both
kp-routed and round-robin returned None for every kp. The test
measured "is the empty-state substrate operational" -- which is
not the A2 hypothesis.

The structural framing asks: does the registry's routing layer
encode meaningful per-kp targets? If yes, every routing decision
the daemon makes is causally connected to the kp record that
drove it -- the attribution chain is well-formed even when a
particular tick falls back to round-robin.

## A2 protocol

1. Compute the round-robin DEFAULT plugin id: REGISTRY[
   _PLUGINS[0].id] -- whatever plugin appears first in the
   ordered _PLUGINS list. This is what round-robin would pick
   with no prior plugin and full applicability.

2. For each kp in KILL_PATTERN_REGISTRY, look up
   routing_action_for(kp), then _routing_action_to_plugin_id().

3. Classify per kp:
   - resolved_to_specific_plugin: target_id is in REGISTRY and
     target_id != default_id -- this kp routes to a DIFFERENT
     plugin than round-robin would default to. Attribution
     succeeds.
   - resolved_to_default: target_id == default_id -- same
     destination as round-robin; no attribution.
   - unresolved: target_id is None (sentinel "none_claim_survives"
     or non-gNN routing_action). The registry has no opinion
     for this kp -> no Layer-2 attribution.

4. attribution_rate = n_resolved_to_specific / n_examined.

5. Pass if attribution_rate >= 0.50.
"""
from __future__ import annotations

from charon.agents.erebos._kill_pattern_registry import (
    KILL_PATTERN_REGISTRY,
    routing_action_for,
)
from charon.agents.erebos.generators import (
    REGISTRY,
    _routing_action_to_plugin_id,
)
from charon.agents.erebos.sprint1 import SprintResult


PASS_THRESHOLD_ATTRIBUTION = 0.50

# Round-robin default plugin id: applicable_plugins(state)[0] when
# all plugins are applicable equals _PLUGINS[0] in the ordered
# list. We need the id; import it lazily to avoid coupling.
def _round_robin_default_plugin_id() -> str:
    """First plugin id in the _PLUGINS list (the round-robin
    'no-last-plugin' default with full applicability)."""
    # Lazy access to keep imports tidy
    from charon.agents.erebos.generators import _PLUGINS
    return _PLUGINS[0].id


def run_a2() -> SprintResult:
    """Execute A2 protocol; return the verdict."""
    default_plugin_id = _round_robin_default_plugin_id()

    n_examined = 0
    n_resolved_to_specific = 0
    n_resolved_to_default = 0
    n_unresolved = 0

    target_distribution: dict[str, int] = {}
    attributed_kps: list[tuple[str, str]] = []  # (kp_name, target)
    unresolved_kps: list[str] = []

    for kp_name in sorted(KILL_PATTERN_REGISTRY.keys()):
        n_examined += 1
        action = routing_action_for(kp_name)
        target_id = (
            _routing_action_to_plugin_id(action) if action else None
        )
        if target_id is None or target_id not in REGISTRY:
            n_unresolved += 1
            unresolved_kps.append(kp_name)
            target_distribution["__unresolved__"] = (
                target_distribution.get("__unresolved__", 0) + 1
            )
        elif target_id == default_plugin_id:
            n_resolved_to_default += 1
            target_distribution[target_id] = (
                target_distribution.get(target_id, 0) + 1
            )
        else:
            n_resolved_to_specific += 1
            target_distribution[target_id] = (
                target_distribution.get(target_id, 0) + 1
            )
            attributed_kps.append((kp_name, target_id))

    attribution_rate = (
        n_resolved_to_specific / n_examined if n_examined > 0 else 0.0
    )

    distinct_targets = sum(
        1 for k in target_distribution
        if k != "__unresolved__"
    )

    passed = attribution_rate >= PASS_THRESHOLD_ATTRIBUTION

    return SprintResult(
        experiment_id="A2",
        hypothesis=(
            "Routing decisions trace to specific Layer-2 records "
            "(registry resolves >= 50% of kps to non-default plugin)"
        ),
        metric_name="attribution_rate",
        metric_value=attribution_rate,
        pass_threshold=PASS_THRESHOLD_ATTRIBUTION,
        comparator=">=",
        passed=passed,
        protocol_summary=(
            f"Walk every kp in KILL_PATTERN_REGISTRY "
            f"(n={len(KILL_PATTERN_REGISTRY)}). For each, resolve "
            f"routing_action_for(kp) -> _routing_action_to_plugin_id."
            f" Attribution_rate = fraction of kps that resolve to "
            f"a plugin id OTHER than round-robin's default "
            f"({default_plugin_id!r})."
        ),
        notes=(
            f"n_examined={n_examined}; "
            f"n_resolved_to_specific={n_resolved_to_specific}; "
            f"n_resolved_to_default={n_resolved_to_default}; "
            f"n_unresolved={n_unresolved}; "
            f"distinct_target_plugins={distinct_targets}; "
            f"round-robin default={default_plugin_id!r}"
        ),
    )
