"""Composition-aware Stygian loader protocol.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md infra task #37
+ pivot/erebos_design_philosophy_dna_2026-05-26.md P12 (falsification
asymmetry: generators stay un-falsifiable until this layer exists).

The protocol: a CompositionLoader resolves an EREBOS-* problem into
a real battery run by:
1. Parsing the queue row's _queue_payload to extract:
   - the originating plugin_id (g01..g25)
   - the parent problem_id(s)
   - the composition-specific parameters (split metadata,
     substitution invariants, weakening direction, etc.)
2. Loading the parent problem's data via existing BL-C-* loaders.
3. Applying the composition's transformation to the data context
   (binary split / ablation / threshold tightening / etc.).
4. Calling battery_unified.UnifiedBattery with the transformed
   context.
5. Mapping the battery verdict to a kill_pattern that matches the
   plugin's expected_kill_pattern (PROMOTED/REJECTED/UNVERIFIED).

v0.10 SPIKE scope: one concrete loader, EREBOS-G02-* x Lehmer x
Salem/non-Salem split. Validates the contract end-to-end. Other
EREBOS-G<NN>-* problems continue to short-circuit at the executor
until their loaders ship.
"""
from __future__ import annotations

from typing import Any, Callable, Optional, Protocol


class CompositionLoader(Protocol):
    """Each concrete loader matches an (Erebos plugin_id, parent
    problem_id, [composition parameters]) tuple and returns a
    battery-ready input dict."""

    plugin_id: str        # which Erebos plugin this loader handles
    composition_id: str   # short canonical id (e.g., "g02_lehmer_salem")
    description: str

    def applicable(self, queue_payload: dict) -> bool:
        """Does this loader handle the given queue row?"""
        ...

    def build_battery_input(self, queue_payload: dict) -> dict:
        """Return a BatteryLoaderResult-shaped dict ready for
        UnifiedBattery.test_distribution() / test_correlation()."""
        ...


# Registry of composition loaders. Populated lazily; see
# charon/agents/stygian/loaders/composition_registry.py for the
# concrete loaders.
_REGISTRY: list[CompositionLoader] = []


def register(loader: CompositionLoader) -> CompositionLoader:
    """Decorator: register a composition loader."""
    _REGISTRY.append(loader)
    return loader


def find_loader(queue_payload: dict) -> Optional[CompositionLoader]:
    """Return the first registered loader that applies to this queue
    payload, or None if no loader is registered (caller should
    fall back to short-circuit)."""
    for loader in _REGISTRY:
        try:
            if loader.applicable(queue_payload):
                return loader
        except Exception:
            continue
    return None


def all_registered() -> list[CompositionLoader]:
    return list(_REGISTRY)
