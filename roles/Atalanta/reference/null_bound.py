"""Reference implementation of the proposed null-bound invariant (ATALANTA-04 Q5).

This is a DEMONSTRATION inside Atalanta's own lane, not an installation.
No other seat's code imports it and nothing schedules it. It exists so the
proposed invariant in roles/Atalanta/PROPOSED_INVARIANT_2026-09-11.md is
executable rather than prose, and so its three controls can be run.

The invariant, in one sentence: a persistent loop declares a bound on
consecutive NON-PRODUCTIVE ticks, parks itself on reaching the bound, and
names the seat that is accountable for unparking it.

The load-bearing detail, and the reason the obvious version does not work:
the counter is keyed to the loop's DECLARED PRODUCTIVITY SIGNAL (base rule
8), never to whether the tick wrote something. Atalanta wrote a
well-formed artifact on every one of its 354 dead ticks. An
artifact-keyed counter would have read 354 productive ticks and never
fired. That is what the cheat control tests.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

#: Terminal states a bounded loop can reach. PARKED is not a failure; it is
#: the loop correctly declining to keep running with nothing to do.
RUNNING = "RUNNING"
PARKED = "PARKED"


class BoundNotDeclared(Exception):
    """Refuse to construct a loop with no bound. A loop whose no-op count is
    unbounded, or whose alarm names no accountable seat, may not be launched."""


@dataclass
class ParkRecord:
    """The typed gate a parked loop leaves behind. Readable without running
    the loop, which is what makes dormancy visible (base rule 7)."""
    loop: str
    reason: str
    consecutive_no_ops: int
    bound: int
    accountable_seat: str
    last_productive_tick: Optional[int]
    unpark_requires: str = "an explicit human or command clearance; a restart does not clear it"

    def as_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass
class BoundedLoop:
    """Wraps a tick function with the three controls.

    tick() must return the loop's DOMAIN productivity for that tick: a
    truthy value (rows produced, state advanced, gate exercised) or a
    falsey value for an explicit no-op. Whether the tick wrote a file,
    logged a row or emitted an artifact is deliberately not consulted.
    """
    name: str
    tick: Callable[[], Any]
    bound: int
    accountable_seat: str
    #: called with (ParkRecord) when the loop parks; in production this is
    #: the comms post that reaches a named seat's queue.
    notify: Optional[Callable[[ParkRecord], None]] = None

    state: str = RUNNING
    consecutive_no_ops: int = 0
    ticks_run: int = 0
    productive_ticks: int = 0
    last_productive_tick: Optional[int] = None
    park_record: Optional[ParkRecord] = None
    notifications: list = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.bound, int) or self.bound < 1:
            raise BoundNotDeclared(
                "{}: a persistent loop must declare an integer bound >= 1 on "
                "consecutive non-productive ticks".format(self.name))
        if not self.accountable_seat or not str(self.accountable_seat).strip():
            raise BoundNotDeclared(
                "{}: a bound with no accountable seat is a bell, not a brake; "
                "name the seat that is obliged to answer".format(self.name))

    def run_tick(self) -> str:
        """One tick. Returns the loop state AFTER the tick."""
        if self.state == PARKED:
            # The brake holds. A parked loop does not tick again on its own,
            # and a restart does not clear the park record.
            return PARKED

        self.ticks_run += 1
        produced = self.tick()

        if produced:
            self.productive_ticks += 1
            self.last_productive_tick = self.ticks_run
            self.consecutive_no_ops = 0
            return RUNNING

        self.consecutive_no_ops += 1
        if self.consecutive_no_ops >= self.bound:
            self._park("consecutive non-productive ticks reached the declared bound")
        return self.state

    def _park(self, reason: str) -> None:
        self.state = PARKED
        self.park_record = ParkRecord(
            loop=self.name,
            reason=reason,
            consecutive_no_ops=self.consecutive_no_ops,
            bound=self.bound,
            accountable_seat=self.accountable_seat,
            last_productive_tick=self.last_productive_tick,
        )
        if self.notify is not None:
            self.notify(self.park_record)
        self.notifications.append(self.park_record)

    def run(self, max_ticks: int) -> str:
        """Run up to max_ticks, stopping early if the loop parks."""
        for _ in range(max_ticks):
            if self.run_tick() == PARKED:
                break
        return self.state
