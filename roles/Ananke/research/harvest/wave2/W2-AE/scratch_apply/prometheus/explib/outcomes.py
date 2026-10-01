"""Shared outcome vocabulary.

Every check in explib returns PASS, FAIL or NOT_VERIFIED. NOT_VERIFIED is never counted as a pass
(fleet memory `check_needs_a_third_outcome`). `all_pass` is the only aggregate offered, and it is
fail-closed: one NOT_VERIFIED makes it False.
"""
from __future__ import annotations

import dataclasses
from typing import Any, Iterable

PASS, FAIL, NOT_VERIFIED = "PASS", "FAIL", "NOT_VERIFIED"


@dataclasses.dataclass(frozen=True)
class Check:
    name: str
    outcome: str                      # PASS / FAIL / NOT_VERIFIED
    detail: Any = None

    def __post_init__(self):
        if self.outcome not in (PASS, FAIL, NOT_VERIFIED):
            raise ValueError(f"bad outcome {self.outcome!r}")

    def as_dict(self) -> dict:
        return {"name": self.name, "outcome": self.outcome, "detail": self.detail}


def all_pass(checks: Iterable[Check]) -> bool:
    cs = list(checks)
    return bool(cs) and all(c.outcome == PASS for c in cs)


def worst(checks: Iterable[Check]) -> str:
    """FAIL beats NOT_VERIFIED beats PASS. An empty list is NOT_VERIFIED."""
    cs = [c.outcome for c in checks]
    if not cs:
        return NOT_VERIFIED
    if FAIL in cs:
        return FAIL
    if NOT_VERIFIED in cs:
        return NOT_VERIFIED
    return PASS
