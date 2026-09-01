"""Typed errors for Gen-2. Every failure a caller can provoke is a distinct,
catchable type carrying a machine-readable code, so the API can map it to a
deterministic status and so tests assert on the CATEGORY, not a string."""

from __future__ import annotations

from typing import Any, Optional


class FoundryError(Exception):
    code = "foundry_error"
    http_status = 400

    def __init__(self, message: str, **detail: Any):
        self.message = message
        self.detail = dict(detail)
        super().__init__(message)

    def to_detail(self) -> dict:
        return {"error": self.code, "message": self.message, **self.detail}


class NotFound(FoundryError):
    code = "not_found"
    http_status = 404


class AccessDenied(FoundryError):
    """Ownership / isolation boundary. Knowing an id must not grant access."""
    code = "access_denied"
    http_status = 403


class InvalidTransition(FoundryError):
    """A world/work lifecycle transition that the state machine forbids."""
    code = "invalid_transition"
    http_status = 409


class ValidationError(FoundryError):
    code = "validation_error"
    http_status = 422


class ConflictError(FoundryError):
    """A concurrency conflict: lost claim, duplicate completion, stale lease."""
    code = "conflict"
    http_status = 409


class BudgetExhausted(FoundryError):
    code = "budget_exhausted"
    http_status = 409


class IsolationViolation(FoundryError):
    """An attempt to move information across a world boundary that policy
    forbids, or to reference another world's private object."""
    code = "isolation_violation"
    http_status = 403


class LedgerIntegrityError(FoundryError):
    """The event hash chain does not verify: tampering or corruption."""
    code = "ledger_integrity_error"
    http_status = 500


class PredictionOrderingError(FoundryError):
    """An observation tried to claim a prediction that did not precede it."""
    code = "prediction_ordering_error"
    http_status = 409
