"""LeanSession → ProofSystem adapter.

Bridges Layer 1 (LeanSession) to Layer 2 (proof-search engine).
"""
from __future__ import annotations

from agents._shared.external_tools.lean_runtime import (
    LeanSession,
    ProofStepResponse,
    ProofFinished,
    ProofGivenUp,
    LeanError,
    SessionCrashed,
)
from agents._shared.proof_search.types import SearchOutcome, SearchState


class LeanProofSystem:
    """ProofSystem implementation backed by a single LeanSession."""

    def __init__(self, lean: LeanSession):
        self._lean = lean

    def apply_tactic(
        self, state: SearchState, tactic: str, timeout: float | None = None
    ) -> tuple[SearchOutcome, SearchState | None, str | None]:
        if not isinstance(state.state_id, int):
            return (
                SearchOutcome.REJECTED,
                None,
                f"LeanProofSystem expects int state_id; got {type(state.state_id).__name__}",
            )

        resp = self._lean.apply_tactic(tactic, proof_state=state.state_id, timeout=timeout)

        if isinstance(resp, ProofFinished):
            new = SearchState(state_id=resp.proof_state, goals=[])
            return SearchOutcome.FINISHED, new, None

        if isinstance(resp, ProofGivenUp):
            new = SearchState(state_id=resp.proof_state, goals=[])
            return SearchOutcome.GAVE_UP, new, None

        if isinstance(resp, ProofStepResponse):
            if resp.has_errors:
                detail = "; ".join(m.data for m in resp.messages if m.severity == "error")
                return SearchOutcome.REJECTED, None, detail
            new = SearchState(state_id=resp.proof_state, goals=list(resp.goals))
            if new.is_closed:
                return SearchOutcome.FINISHED, new, None
            return SearchOutcome.PROGRESS, new, None

        if isinstance(resp, LeanError):
            return SearchOutcome.REJECTED, None, resp.message

        if isinstance(resp, SessionCrashed):
            return SearchOutcome.CRASHED, None, resp.detail

        return SearchOutcome.REJECTED, None, f"unknown response: {resp!r}"

    def is_alive(self) -> bool:
        return self._lean.is_alive
