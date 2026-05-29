"""Typed dataclasses for Lean-runtime requests and responses.

Mirrors the lean-repl JSON schema. Discriminated unions for both inputs
(Command vs ProofStep vs FileCommand) and outputs (CommandResponse vs
ProofStepResponse vs LeanError vs ProofFinished vs ProofGivenUp vs
SessionCrashed). See `aporia/doctrine/external_tool_interaction_primitives_2026-05-28.md`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Union


# --------------------------------------------------------------------- #
# Inputs
# --------------------------------------------------------------------- #

@dataclass
class Command:
    """`{"cmd": "...", "env": optional int}` — top-level Lean declaration."""
    cmd: str
    env: int | None = None

    def to_payload(self) -> dict[str, Any]:
        d: dict[str, Any] = {"cmd": self.cmd}
        if self.env is not None:
            d["env"] = self.env
        return d


@dataclass
class ProofStep:
    """`{"tactic": "...", "proofState": int}` — single tactic application."""
    tactic: str
    proof_state: int

    def to_payload(self) -> dict[str, Any]:
        return {"tactic": self.tactic, "proofState": self.proof_state}


@dataclass
class FileCommand:
    """`{"path": "..."}` — load a Lean file."""
    path: Path

    def to_payload(self) -> dict[str, Any]:
        return {"path": str(self.path)}


LeanRequest = Union[Command, ProofStep, FileCommand]


# --------------------------------------------------------------------- #
# Output components
# --------------------------------------------------------------------- #

@dataclass
class Pos:
    line: int
    column: int

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> "Pos | None":
        if d is None:
            return None
        return cls(line=d.get("line", 0), column=d.get("column", 0))


@dataclass
class Message:
    severity: str  # "error" | "warning" | "info"
    pos: Pos | None
    end_pos: Pos | None
    data: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Message":
        return cls(
            severity=d.get("severity", "info"),
            pos=Pos.from_dict(d.get("pos")),
            end_pos=Pos.from_dict(d.get("endPos")),
            data=d.get("data", ""),
        )


@dataclass
class Sorry:
    pos: Pos | None
    end_pos: Pos | None
    goal: str
    proof_state: int

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Sorry":
        return cls(
            pos=Pos.from_dict(d.get("pos")),
            end_pos=Pos.from_dict(d.get("endPos")),
            goal=d.get("goal", ""),
            proof_state=d.get("proofState", -1),
        )


# --------------------------------------------------------------------- #
# Output variants (discriminated union)
# --------------------------------------------------------------------- #

@dataclass
class CommandResponse:
    """Response to a Command. Includes new env id, any messages, any sorries."""
    env: int
    messages: list[Message] = field(default_factory=list)
    sorries: list[Sorry] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(m.severity == "error" for m in self.messages)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "CommandResponse":
        return cls(
            env=d.get("env", -1),
            messages=[Message.from_dict(m) for m in d.get("messages", [])],
            sorries=[Sorry.from_dict(s) for s in d.get("sorries", [])],
        )


@dataclass
class ProofStepResponse:
    """Response to a ProofStep. Includes new proof_state and remaining goals."""
    proof_state: int
    goals: list[str] = field(default_factory=list)
    messages: list[Message] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(m.severity == "error" for m in self.messages)

    @property
    def is_finished(self) -> bool:
        return len(self.goals) == 0

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ProofStepResponse":
        return cls(
            proof_state=d.get("proofState", -1),
            goals=list(d.get("goals", [])),
            messages=[Message.from_dict(m) for m in d.get("messages", [])],
        )


@dataclass
class LeanError:
    """Top-level error from lean-repl itself (not a tactic error)."""
    message: str
    pos: Pos | None = None


@dataclass
class ProofFinished:
    """Sentinel: tactic closed all goals."""
    proof_state: int


@dataclass
class ProofGivenUp:
    """Sentinel: tactic explicitly admitted / gave up."""
    proof_state: int


@dataclass
class SessionCrashed:
    """Subprocess died mid-interaction."""
    detail: str


LeanResponse = Union[
    CommandResponse,
    ProofStepResponse,
    LeanError,
    ProofFinished,
    ProofGivenUp,
    SessionCrashed,
]
