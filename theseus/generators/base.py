"""Generator abstract base class.

Every Theseus generator implements:
- generator_id: short string matching inventory.md (e.g. "a1")
- claim_kind: a ClaimKind enum value
- next() -> TheseusRecord | None: emit one record, or None if exhausted
- description() -> str: one-line human-readable identity

Generators are stateful — they remember what they've emitted. They are
single-threaded per instance (one batch = one daemon thread = serial
generator calls). Parallelism happens at the *batch* level: 5 generators
running in 5 separate daemon threads.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterator, List, Optional

from theseus.emit.record_schema import TheseusRecord


class GeneratorStatus(str, Enum):
    ACTIVE = "active"
    STUB = "stub"
    STUB_TIER2 = "stub_tier2"
    STUB_TIER3 = "stub_tier3"
    STUB_FUTURE = "stub_future"
    EXHAUSTED = "exhausted"


@dataclass
class GeneratorResult:
    """Summary of one generator's contribution to a batch."""

    generator_id: str
    claims_attempted: int = 0
    records_emitted: int = 0
    kills: int = 0
    confirmations: int = 0
    inconclusive: int = 0
    errors: int = 0
    error_messages: List[str] = field(default_factory=list)
    wall_seconds: float = 0.0


class Generator(abc.ABC):
    """Abstract base for all Theseus generators."""

    generator_id: str = "UNDEFINED"
    claim_kind: str = "UNDEFINED"
    status: GeneratorStatus = GeneratorStatus.STUB

    def __init__(self, batch_id: str) -> None:
        self.batch_id = batch_id
        self.attempts = 0
        self.emitted: List[str] = []  # record_ids emitted this instance

    @abc.abstractmethod
    def description(self) -> str:
        """One-line human-readable identity."""

    @abc.abstractmethod
    def next(self) -> Optional[TheseusRecord]:
        """Emit next record, or None if exhausted for this batch.

        Implementations should be idempotent across calls (same internal
        state → same next record). The daemon loop calls next() until it
        returns None OR until batch wall-time elapses.
        """

    def __iter__(self) -> Iterator[TheseusRecord]:
        while True:
            r = self.next()
            if r is None:
                return
            yield r


class StubGenerator(Generator):
    """Default implementation for stub modules — does not emit.

    Subclasses can override claim_kind / description() to describe the
    intended generator without yet implementing next(). Daemon skips
    StubGenerator instances when selecting active generators.
    """

    status = GeneratorStatus.STUB

    def description(self) -> str:
        return f"{self.generator_id}: STUB (see inventory.md)"

    def next(self) -> Optional[TheseusRecord]:
        return None
