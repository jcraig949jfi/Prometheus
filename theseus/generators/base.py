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
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterator, List, Optional

from theseus.emit.record_schema import TheseusRecord


# Bound on the per-generator `emitted` ring. Capped to prevent unbounded
# memory growth in high-throughput batches (b3 OOM, 2026-05-20).
_EMITTED_RING_MAXLEN = 2000


class GeneratorStatus(str, Enum):
    ACTIVE = "active"
    STUB = "stub"
    STUB_TIER2 = "stub_tier2"
    STUB_TIER3 = "stub_tier3"
    STUB_FUTURE = "stub_future"
    EXHAUSTED = "exhausted"


class GeneratorRole(str, Enum):
    """Substrate-meaningful contribution class per advisory board (Fire #53).

    DISCOVERY        — emissions count toward lifetime discoveries and
                       carry substrate-novel claims worth Learner training.
                       Default for most generators.
    FALSIFICATION    — emissions are kills carrying real falsification
                       signal (not applicability filter or tautology).
    BOUNDARY_MAPPING — emissions trace catalog boundaries / near-misses;
                       moderately discovery-worthy.
    NULL_BASELINE    — explicit null-distribution / uniform random;
                       baseline for measuring sophistication, not for
                       Learner training. F1 by design.
    TAUTOLOGY_CONTROL — emissions are tautologies by construction
                       (e.g. c4 generalization 100% confirmation rate);
                       kept as alive-monitor but EXCLUDED from discovery
                       stats. Per advisory board Fire #53: kills my
                       celebrated c4 finding while preserving the tool.
    INFRA_DIAGNOSTIC — emissions are infrastructure self-tests; not
                       substrate output.
    """
    DISCOVERY = "discovery"
    FALSIFICATION = "falsification"
    BOUNDARY_MAPPING = "boundary_mapping"
    NULL_BASELINE = "null_baseline"
    TAUTOLOGY_CONTROL = "tautology_control"
    INFRA_DIAGNOSTIC = "infra_diagnostic"


# Roles excluded from discovery stats — per advisory board, these
# emissions can be valid as alive-monitors but should not count toward
# lifetime discoveries because they carry near-zero info for the Learner.
NON_DISCOVERY_ROLES = frozenset({
    GeneratorRole.NULL_BASELINE,
    GeneratorRole.TAUTOLOGY_CONTROL,
    GeneratorRole.INFRA_DIAGNOSTIC,
})


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
    # Role classification — controls whether emissions count as
    # substrate discoveries. Default DISCOVERY; override per-gen to
    # NULL_BASELINE / TAUTOLOGY_CONTROL / etc. Per advisory board
    # Fire #53.
    role: GeneratorRole = GeneratorRole.DISCOVERY

    def __init__(self, batch_id: str) -> None:
        self.batch_id = batch_id
        self.attempts = 0
        # Bounded ring (last N record_ids). Generators .append() to it but
        # never read prior contents; an unbounded list was the proximate
        # cause of b3 OOM on 2026-05-20 (28M strings ~ 2GB).
        self.emitted: deque[str] = deque(maxlen=_EMITTED_RING_MAXLEN)

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
