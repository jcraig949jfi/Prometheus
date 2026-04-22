"""
Pattern-class auto-sweeps (generator #6).

Three automated filters run before any SIGNATURE lands in the tensor:
- pattern_30: algebraic-identity coupling detection
- pattern_20: pooled-vs-stratified artifact detection
- pattern_19: stale / irreproducible prior measurement

Each sweep emits {verdict: CLEAR|WARN|BLOCK, rationale, raised_by, level?}.
Runner composes them; ingestion path (agora.register_specimen, agora.tensor.push)
calls the runner before committing.

Ships: v1.0 2026-04-20. Non-negotiable companion to every producer generator.
See docs/prompts/gen_06_pattern_autosweeps.md.
"""
from harmonia.sweeps.runner import sweep_signature, SweepVerdict, SweepOutcome

__all__ = ["sweep_signature", "SweepVerdict", "SweepOutcome"]
