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


class WrongSession(FoundryError):
    """The presented session key was minted by a DIFFERENT engine instance.

    421 Misdirected Request is the exact HTTP semantic: "the request was
    directed at a server that is not able to produce a response" and the client
    should retry against the correct one. It is chosen over 404 deliberately --
    a 404 says the resource does not exist, which sends an operator hunting for
    missing data when the truth is that they are talking to the wrong machine.
    It is chosen over 500 because nothing failed: the engine answered exactly
    the right question correctly."""
    code = "WRONG_SESSION"
    http_status = 421


class SessionRequired(FoundryError):
    """No session key on a route that requires one (STRICT session)."""
    code = "SESSION_REQUIRED"
    http_status = 428


class SessionMalformed(FoundryError):
    """The header was present but is not a session key at all."""
    code = "SESSION_MALFORMED"
    http_status = 422


class SessionUnknown(FoundryError):
    """Well-formed, names THIS engine, but no such session here. A restore from
    a different backup, a pruned session, or a forgery."""
    code = "SESSION_UNKNOWN"
    http_status = 401


class SessionClosed(FoundryError):
    """The session exists on this engine but its lifecycle is CLOSED."""
    code = "SESSION_CLOSED"
    http_status = 409


class SessionMismatch(FoundryError):
    """A VALID session for this engine, presented against a resource that
    belongs to a different session. Ownership violation -> 403, the same
    status the engine already uses for cross-client access."""
    code = "SESSION_MISMATCH"
    http_status = 403


class PredictionOrderingError(FoundryError):
    """An observation tried to claim a prediction that did not precede it."""
    code = "prediction_ordering_error"
    http_status = 409
