"""Productive-liveness semantics: separating 'alive' from 'working'.

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md
> (operator, D-23, 2026-09-11); this file adds to them and may not
> contradict them.

Pronoia's charter question is not "is the process alive" but "what
observable consequence should exist if this thing is doing the work we
believe it is doing, and does that consequence exist".

This module is the smallest executable statement of that question. It is
PURE: no database, no clock, no filesystem. `now` is always injected.
That is deliberate -- an instrument that reads the wall clock itself
cannot be tested at an arbitrary time, and an instrument that cannot be
tested is the thing this seat exists to find.

THE LOAD-BEARING PROPERTY
-------------------------
derive_health() takes only TIMESTAMPS. It is never told "I am healthy"
by the code whose health is in question. Consequently a process whose
work thread has died, but whose heartbeat thread still runs, DEGRADES on
wall-clock alone: PRODUCTIVE -> STALLED, with no cooperation from the
dead thread.

That is the exact defect this seat committed twice (roles/Pronoia/
calibration/LEDGER.md PRON-CAL-002 and PRON-CAL-003). Era 1 reported
"HEALTHY / Recent Log Lines: 0"; Era 2 reported status='online' for
62 hours after its last unit of work. Both would have been caught here,
because in both cases the only field that stayed fresh was the one the
monitor wrote about itself.

THE SEVEN LEVELS (the vocabulary the survey uses, recorded here so the
code and the survey cannot drift apart)

    L0  process / heartbeat evidence      the process exists and beats
    L1  eligibility evidence              input existed, work was due
    L2  work-attempt evidence             an attempt actually started
    L3  work-success evidence             the attempt completed its work
    L4  artifact / state-transition       a consequence exists
    L5  downstream consumption            someone received or used it

This module covers L0-L4. L5 is not inferable from a heartbeat and this
module does not pretend otherwise: no state below claims consumption.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

__all__ = [
    "Health",
    "WorkEvidence",
    "derive_health",
    "DEFAULT_STALL_MULTIPLE",
    "DEFAULT_GRACE_MULTIPLE",
]


class Health:
    """The health vocabulary. Every value is a claim about EVIDENCE, not a
    claim about intent, and every value is reachable in a test."""

    BOOTING = "booting"
    # Alive, no attempt yet, still inside the startup grace window.

    NO_WORK_OBSERVED = "no_work_observed"
    # Alive, past the grace window, and has NEVER attempted work.
    # Era 1's failure mode: the monitor was up and observing nothing.

    WORKING = "working"
    # An attempt is in flight: attempted more recently than it succeeded,
    # and the attempt is recent enough to still be plausibly running.

    PRODUCTIVE = "productive"
    # Succeeded within the stall window. The ONLY value that asserts the
    # work is actually being done, and it expires by itself.

    FAILING = "failing"
    # Still attempting inside the stall window, but the last success is
    # older than the stall window (or there has never been one).
    # Distinct from STALLED: the loop is alive AND trying AND not getting there.

    STALLED = "stalled"
    # No ATTEMPT inside the stall window. The work thread has stopped,
    # whatever the heartbeat says. Era 2's failure mode, reached purely by
    # the passage of time.

    INCOHERENT = "incoherent"
    # The evidence contradicts itself: a success with no attempt, a success
    # that precedes the process start, or a timestamp in the future.
    # This is the cheat detector -- see the cheat controls in the tests.
    # It is a statement about the EVIDENCE, never an accusation about the
    # writer; the usual cause is a writer that records success without
    # recording the attempt.


#: How many cadence intervals may pass before a success is considered stale.
#: 2.5 means "you have missed two whole cycles and are half way through a
#: third". Chosen before looking at any agent's data; see the docstring of
#: derive_health for why it is not tuned to make anything pass.
DEFAULT_STALL_MULTIPLE = 2.5

#: Startup grace, in cadence intervals, before a process that has never
#: worked is reported as NO_WORK_OBSERVED rather than BOOTING.
DEFAULT_GRACE_MULTIPLE = 1.5


@dataclass(frozen=True)
class WorkEvidence:
    """The four timestamps a productive-liveness claim may rest on.

    Every field is Optional because ABSENCE IS THE COMMON CASE and must be
    representable without lying. `None` means "no evidence", which is never
    silently upgraded to "no work" or downgraded to "failure" -- it is
    reported as its own state.
    """

    started_at: Optional[datetime] = None
    last_heartbeat_at: Optional[datetime] = None
    last_attempt_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None


def _aware(dt: Optional[datetime]) -> Optional[datetime]:
    """Timestamps from Postgres are tz-aware; ones from tests may not be.
    Comparing the two raises. Normalising here keeps every caller honest
    without making the caller think about it."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        raise ValueError(
            "naive datetime passed to productive_liveness; supply tz-aware "
            "timestamps so that comparisons cannot silently depend on the "
            "local timezone of whichever host happened to run the check"
        )
    return dt


def derive_health(
    now: datetime,
    evidence: WorkEvidence,
    cadence_sec: float,
    stall_multiple: float = DEFAULT_STALL_MULTIPLE,
    grace_multiple: float = DEFAULT_GRACE_MULTIPLE,
    future_tolerance_sec: float = 60.0,
) -> str:
    """Return a Health value from timestamps alone.

    `now` is injected, never read from the clock: the caller supplies it so
    the function is testable at any point in time.

    `cadence_sec` is how often the work is SUPPOSED to happen. It comes from
    the loop's own configuration, not from its observed behaviour -- deriving
    the expected cadence from the observed cadence would make any loop
    healthy at whatever rate it happened to be running, which is the
    throughput-metric-that-satisfies-itself shape this seat was built from.

    The thresholds are deliberately blunt and were fixed before any agent's
    data was read. A gate tuned until the author's own loop passes is not a
    gate (base role, doctrine).
    """
    if cadence_sec <= 0:
        raise ValueError("cadence_sec must be positive; got %r" % (cadence_sec,))

    now = _aware(now)
    started_at = _aware(evidence.started_at)
    attempt = _aware(evidence.last_attempt_at)
    success = _aware(evidence.last_success_at)

    stall_window = timedelta(seconds=cadence_sec * stall_multiple)
    grace_window = timedelta(seconds=cadence_sec * grace_multiple)
    future_slack = timedelta(seconds=future_tolerance_sec)

    # --- coherence first: evidence that cannot be true is never a health
    # claim, however green it looks. ---------------------------------------
    if attempt is not None and attempt > now + future_slack:
        return Health.INCOHERENT
    if success is not None and success > now + future_slack:
        return Health.INCOHERENT
    if success is not None and attempt is None:
        # Succeeded without ever attempting. Causally impossible; the usual
        # real cause is a writer that sets success and never sets attempt.
        return Health.INCOHERENT
    if success is not None and attempt is not None and success > attempt + future_slack:
        # Succeeded strictly after the attempt that produced it began is
        # normal; succeeded LONG after the last recorded attempt means the
        # attempt field is not tracking the work the success field claims.
        return Health.INCOHERENT
    if success is not None and started_at is not None and success < started_at:
        # Success predates this process. It belongs to a previous incarnation
        # and is not evidence about the one that is running now.
        return Health.INCOHERENT

    # --- never attempted -------------------------------------------------
    if attempt is None:
        if started_at is not None and now - started_at <= grace_window:
            return Health.BOOTING
        return Health.NO_WORK_OBSERVED

    attempt_age = now - attempt

    # --- the work thread has stopped -------------------------------------
    # Checked BEFORE success, so that a loop which succeeded once and then
    # died cannot hold PRODUCTIVE. This ordering is the whole point.
    if attempt_age > stall_window:
        return Health.STALLED

    # --- attempting, inside the window -----------------------------------
    if success is None:
        return Health.FAILING

    success_age = now - success
    if success_age > stall_window:
        return Health.FAILING

    if attempt > success:
        return Health.WORKING

    return Health.PRODUCTIVE


PRODUCTIVE_STATES = frozenset({Health.PRODUCTIVE})
"""The only states that assert work is being done. Deliberately a set of
one: callers that want 'roughly fine' must say so explicitly rather than
letting WORKING or BOOTING drift into meaning PRODUCTIVE."""
