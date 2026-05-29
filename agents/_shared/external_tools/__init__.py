"""Shared external-tool interaction primitives.

Layer 0: generic stateful subprocess client. Generalizes across Lean, Isabelle,
Coq, Z3, and any JSON-over-stdio tool Prometheus agents need to drive.

See `aporia/doctrine/external_tool_interaction_primitives_2026-05-28.md`.
"""
from agents._shared.external_tools.subprocess_session import SubprocessSession

__all__ = ["SubprocessSession"]
