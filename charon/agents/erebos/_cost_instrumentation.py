"""Cost-instrumentation helpers — Phase 1B ITER-37 daemon wire.

Per Erebos v3 Phase 0 ITER-27 (cost-instrumentation layer shipped
the FIELDS on ComposedClaim) + Phase 1B ITER-37 (WIRE the daemon
to populate them).

Helpers:
  - time_plugin_generate(plugin, state): brackets plugin.generate
    with time.perf_counter(); populates claim.generation_cost_seconds
    on the returned claim (if any).
  - populate_falsification_cost(result_dict, elapsed_seconds): writes
    falsification_cost_seconds into a stygian executor result dict
    so the daemon can read it back when constructing the kill_ledger
    row.

Why a helper module: keeps the pattern testable in isolation (no
daemon instantiation needed) and consistent across producers. The
daemon calls the helper instead of inlining the bracket so the cost
discipline is auditable in one place.

Doctrine alignment: per Doctrine v1.0 §"closed-loop epistemic
economy" — cost-per-information is one of the substrate-internal
metrics that distinguishes Layer 2 navigation from blind
accumulation. Cannot compute value_per_tick without these fields
populated.
"""
from __future__ import annotations

import time
from typing import Any, Optional, Protocol


# Sentinel that the cost field has not been wired upstream. Kept as a
# string so it serializes through json without surprising None ->
# absent conversions.
_UNINSTRUMENTED = "uninstrumented"


class _ClaimLike(Protocol):
    """Structural type for objects with a generation_cost_seconds field.
    Matches ComposedClaim without an import cycle."""
    generation_cost_seconds: float


class _PluginLike(Protocol):
    id: str
    def generate(self, state: Any) -> Optional[_ClaimLike]: ...


def time_plugin_generate(
    plugin: _PluginLike,
    state: Any,
) -> tuple[Optional[Any], float]:
    """Call plugin.generate(state) under a perf_counter bracket.

    If a claim is returned, populate its generation_cost_seconds
    field with the measured elapsed time. Always returns
    (claim_or_None, elapsed_seconds) so the caller can log timing
    even when the plugin returns None.

    Args:
        plugin: object implementing .generate(state) -> claim_or_None.
        state: opaque state forwarded to plugin.generate.

    Returns:
        (claim_or_None, elapsed_seconds). elapsed_seconds is always
        >= 0 and is set even when claim is None. When claim is not
        None, claim.generation_cost_seconds is set to elapsed_seconds
        as a side effect.
    """
    t0 = time.perf_counter()
    try:
        claim = plugin.generate(state)
    except Exception:
        # Re-raise after recording timing — useful for downstream
        # exception-budget analysis. The cost field cannot be set on
        # a non-existent claim.
        elapsed = time.perf_counter() - t0
        raise
    elapsed = time.perf_counter() - t0
    if claim is not None:
        # ComposedClaim is a non-frozen dataclass — direct attribute
        # assignment is the right pattern here.
        try:
            claim.generation_cost_seconds = elapsed
        except (AttributeError, Exception):
            # If the claim type does not carry this field (legacy
            # producer, custom shape), silently skip rather than
            # crash the daemon. Cost telemetry is observational,
            # not load-bearing.
            pass
    return claim, elapsed


def populate_falsification_cost(
    result_dict: dict,
    elapsed_seconds: float,
) -> dict:
    """Write falsification_cost_seconds into a stygian executor result.

    The stygian executor already brackets loader.build_battery_input()
    with time.time() (see charon/agents/stygian/executor.py:408 ->
    battery_elapsed_sec). This helper standardizes the field name
    that propagates into the kill_ledger row so the daemon can later
    read it back onto the originating ComposedClaim.

    Idempotent: calling twice with different elapsed values overwrites.
    Safe on non-dict input (returns input unchanged).

    Args:
        result_dict: the dict returned by a stygian executor invocation.
        elapsed_seconds: measured falsification time in seconds.

    Returns:
        The same dict with falsification_cost_seconds set. Mutates
        in place (and returns) for caller ergonomics.
    """
    if not isinstance(result_dict, dict):
        return result_dict  # type: ignore[return-value]
    result_dict["falsification_cost_seconds"] = float(elapsed_seconds)
    return result_dict


def is_instrumented(claim_or_dict: Any) -> bool:
    """True iff the given object has a non-default cost field.

    Used by audits / regression tests to verify that the daemon wire
    is producing populated cost telemetry rather than the default 0.0.
    Returns False for non-claim / non-dict objects.
    """
    if claim_or_dict is None:
        return False
    if hasattr(claim_or_dict, "generation_cost_seconds"):
        val = getattr(claim_or_dict, "generation_cost_seconds", 0.0)
        return isinstance(val, (int, float)) and val > 0.0
    if isinstance(claim_or_dict, dict):
        val = claim_or_dict.get("generation_cost_seconds", 0.0) or \
              claim_or_dict.get("falsification_cost_seconds", 0.0)
        return isinstance(val, (int, float)) and val > 0.0
    return False
