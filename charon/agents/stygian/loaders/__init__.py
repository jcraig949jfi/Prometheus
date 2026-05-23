"""Stygian per-problem battery-input loaders.

Each loader converts an attack-plan-level problem statement (e.g.,
'BL-C-001 Lehmer's conjecture') into the numeric arguments the v10
battery accepts (values arrays, predicted scalars, domain hints).

Contract: each loader module exposes a function `load() -> dict` whose
return value matches BatteryLoaderResult below. Loaders MUST be pure
data accessors -- no LLM calls, no Postgres writes, no battery
invocation. Side-effect-free + reproducible from the same data
snapshot.

Per pivot/stygian_executor_scoping_2026-05-21.md MVP1 scope: BL-C-001
(Lehmer) is the proof-of-life loader. Subsequent BL-C-* loaders follow
the same protocol.
"""
from __future__ import annotations

from typing import Any, Callable, Optional, TypedDict


class BatteryLoaderResult(TypedDict, total=False):
    """Shape consumed by UnifiedBattery.test_distribution / test_correlation.

    Required:
      mode: 'distribution' | 'correlation' | 'full'
      claim: human-readable claim being tested (becomes the kill_ledger
             record's canonical_claim_text)
      data_source: provenance string (becomes the kill_ledger record's
                   provenance pointer)

    Mode-specific:
      distribution mode requires `values` (1D numeric array)
      correlation mode requires `values_a` + `values_b` (1D arrays)

    Optional (forwarded verbatim to the battery method):
      predicted_value, domain_is_multiplicative, synthetic_generator,
      group_labels, confound_values, X_for_regression, Y_for_regression,
      confounds, dose_levels, dose_labels, subgroups, n_hypotheses_tested,
      index_values, notes
    """
    mode: str
    claim: str
    data_source: str
    values: Any
    values_a: Any
    values_b: Any
    predicted_value: Optional[float]
    domain_is_multiplicative: bool
    synthetic_generator: Optional[Callable]
    group_labels: Any
    confound_values: Any
    X_for_regression: Any
    Y_for_regression: Any
    confounds: dict
    dose_levels: Any
    dose_labels: Any
    subgroups: Any
    n_hypotheses_tested: int
    index_values: Any
    notes: str


# Registry: problem_id -> loader module path (lazy import to avoid heavy
# data-module imports unless the loader is actually invoked).
LOADER_REGISTRY: dict[str, str] = {
    "BL-C-001": "charon.agents.stygian.loaders.bl_c_001_lehmer",
}


def get_loader(problem_id: str) -> Optional[Callable[[], BatteryLoaderResult]]:
    """Return the load() callable for a problem_id, or None if no loader
    is registered. Lazy-imports the loader module on first call."""
    mod_path = LOADER_REGISTRY.get(problem_id)
    if not mod_path:
        return None
    import importlib
    mod = importlib.import_module(mod_path)
    return getattr(mod, "load", None)
