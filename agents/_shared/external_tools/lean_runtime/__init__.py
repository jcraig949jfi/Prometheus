"""Layer 1: Lean-specific typed client over `lake exe repl`.

Wraps the generic Layer 0 SubprocessSession with typed requests and
discriminated-union responses, matching the absorption doctrine at
aporia/doctrine/external_tool_interaction_primitives_2026-05-28.md.

Substrate-wide. Every Prometheus agent that drives Lean starts here.
"""
from agents._shared.external_tools.lean_runtime.types import (
    Command,
    ProofStep,
    FileCommand,
    LeanRequest,
    Message,
    Sorry,
    Pos,
    CommandResponse,
    ProofStepResponse,
    LeanError,
    ProofFinished,
    ProofGivenUp,
    SessionCrashed,
    LeanResponse,
)
from agents._shared.external_tools.lean_runtime.session import LeanSession

__all__ = [
    "Command",
    "ProofStep",
    "FileCommand",
    "LeanRequest",
    "Message",
    "Sorry",
    "Pos",
    "CommandResponse",
    "ProofStepResponse",
    "LeanError",
    "ProofFinished",
    "ProofGivenUp",
    "SessionCrashed",
    "LeanResponse",
    "LeanSession",
]
