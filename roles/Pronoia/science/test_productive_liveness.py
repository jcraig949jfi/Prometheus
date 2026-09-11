"""Tests for the productive-liveness semantics.

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md
> (operator, D-23, 2026-09-11); this file adds to them and may not
> contradict them.

Four demonstrations the operator required (section MISSION 2):

    T1  heartbeat without work            != productive
    T2  attempted work without success    != productive
    T3  successful work advances the appropriate evidence
    T4  stale success remains distinguishable from current liveness

Plus the three controls the base role makes constitutional:

    NEGATIVE  no signal        -> does not report productive
    POSITIVE  real signal      -> does report productive (the instrument
                                  can detect the thing it claims to)
    CHEAT     fabricated success injected -> the channel refuses it

And a GROUND-TRUTH replay: the real measured numbers from Pronoia's own
two failures are fed through the function and must come out as failures.
An instrument that cannot fail its own author's work is decoration.

Run:  python -m pytest roles/Pronoia/science/test_productive_liveness.py -q
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from productive_liveness import (  # noqa: E402
    DEFAULT_STALL_MULTIPLE,
    Health,
    WorkEvidence,
    derive_health,
)

HOUR = 3600.0
T0 = datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc)


def at(**kw) -> datetime:
    return T0 + timedelta(**kw)


# ---------------------------------------------------------------------------
# T1 -- heartbeat without work is not productive
# ---------------------------------------------------------------------------

def test_T1_heartbeat_without_any_work_is_not_productive():
    """The Era 1 shape: the process is up, beating, and has observed nothing.

    The heartbeat is as fresh as it can possibly be -- written this very
    instant -- and it buys no credit at all.
    """
    ev = WorkEvidence(
        started_at=at(hours=-10),
        last_heartbeat_at=T0,       # beating RIGHT NOW
        last_attempt_at=None,       # and has never once tried
        last_success_at=None,
    )
    assert derive_health(T0, ev, cadence_sec=HOUR) == Health.NO_WORK_OBSERVED


def test_T1_fresh_heartbeat_cannot_rescue_a_dead_worker():
    """A perfect heartbeat and a dead work thread. The heartbeat must not
    launder the silence into health."""
    ev = WorkEvidence(
        started_at=at(hours=-100),
        last_heartbeat_at=T0,           # perfect liveness
        last_attempt_at=at(hours=-62),  # last tried 62 hours ago
        last_success_at=at(hours=-62),
    )
    assert derive_health(T0, ev, cadence_sec=HOUR) == Health.STALLED


def test_T1_booting_is_not_productive_either():
    """A process that has just started has not yet earned any claim."""
    ev = WorkEvidence(started_at=at(minutes=-5), last_heartbeat_at=T0)
    got = derive_health(T0, ev, cadence_sec=HOUR)
    assert got == Health.BOOTING
    assert got != Health.PRODUCTIVE


# ---------------------------------------------------------------------------
# T2 -- attempted work without success is not productive
# ---------------------------------------------------------------------------

def test_T2_attempting_but_never_succeeding_is_failing_not_productive():
    ev = WorkEvidence(
        started_at=at(hours=-5),
        last_heartbeat_at=T0,
        last_attempt_at=at(minutes=-2),   # trying, recently
        last_success_at=None,             # and never once getting there
    )
    assert derive_health(T0, ev, cadence_sec=HOUR) == Health.FAILING


def test_T2_attempting_with_only_an_old_success_is_failing():
    """Still firing on cadence, but the successes stopped hours ago.
    This is the case that a naive 'did the job run' check calls healthy."""
    ev = WorkEvidence(
        started_at=at(hours=-24),
        last_heartbeat_at=T0,
        last_attempt_at=at(minutes=-1),   # attempts are current
        last_success_at=at(hours=-9),     # successes are not
    )
    assert derive_health(T0, ev, cadence_sec=HOUR) == Health.FAILING


def test_T2_in_flight_attempt_is_working_not_productive():
    """An attempt newer than the last success means work is in flight.
    WORKING is honest; it is not PRODUCTIVE, and the two never merge."""
    ev = WorkEvidence(
        started_at=at(hours=-5),
        last_heartbeat_at=T0,
        last_attempt_at=at(minutes=-1),
        last_success_at=at(minutes=-61),
    )
    got = derive_health(T0, ev, cadence_sec=HOUR)
    assert got == Health.WORKING
    assert got != Health.PRODUCTIVE


# ---------------------------------------------------------------------------
# T3 -- successful work advances the appropriate evidence
# ---------------------------------------------------------------------------

def test_T3_successful_cycle_is_productive():
    ev = WorkEvidence(
        started_at=at(hours=-5),
        last_heartbeat_at=T0,
        last_attempt_at=at(minutes=-10),
        last_success_at=at(minutes=-9),
    )
    assert derive_health(T0, ev, cadence_sec=HOUR) == Health.PRODUCTIVE


def test_T3_success_is_what_moves_the_state_nothing_else():
    """Hold everything constant, advance ONLY last_success_at, and watch the
    verdict change. This is what 'advances the appropriate evidence' means:
    the success field, and only the success field, buys PRODUCTIVE."""
    base = dict(started_at=at(hours=-24), last_heartbeat_at=T0,
                last_attempt_at=at(minutes=-30))

    stale = WorkEvidence(**base, last_success_at=at(hours=-9))
    assert derive_health(T0, WorkEvidence(**base, last_success_at=at(hours=-9)),
                         cadence_sec=HOUR) == Health.FAILING
    assert derive_health(T0, WorkEvidence(**base, last_success_at=at(minutes=-29)),
                         cadence_sec=HOUR) == Health.PRODUCTIVE
    assert stale.last_success_at != at(minutes=-29)   # the fixture really did differ


def test_T3_more_heartbeats_do_not_buy_productivity():
    """Beat a thousand times; without a success it changes nothing."""
    ev_few = WorkEvidence(started_at=at(hours=-10), last_heartbeat_at=at(hours=-1),
                          last_attempt_at=at(hours=-9), last_success_at=at(hours=-9))
    ev_many = WorkEvidence(started_at=at(hours=-10), last_heartbeat_at=T0,
                           last_attempt_at=at(hours=-9), last_success_at=at(hours=-9))
    assert derive_health(T0, ev_few, cadence_sec=HOUR) == Health.STALLED
    assert derive_health(T0, ev_many, cadence_sec=HOUR) == Health.STALLED


# ---------------------------------------------------------------------------
# T4 -- stale success stays distinguishable from current process liveness
# ---------------------------------------------------------------------------

def test_T4_stale_success_with_live_heartbeat_degrades_on_wall_clock_alone():
    """THE CENTRAL TEST OF THIS MODULE.

    Nothing about the evidence changes except `now`. The work fields are
    frozen (the work thread is dead) and the heartbeat is always current
    (the heartbeat thread is not). The verdict must rot by itself.

    If this test ever passes PRODUCTIVE at the far end, Pronoia has rebuilt
    the bug it exists to detect, for the third time.
    """
    frozen = dict(started_at=at(hours=-100),
                  last_attempt_at=at(minutes=-1),
                  last_success_at=at(minutes=-1))

    timeline = [
        (at(minutes=0),   Health.PRODUCTIVE),   # just succeeded
        (at(minutes=60),  Health.PRODUCTIVE),   # one cadence later, tolerated
        (at(minutes=180), Health.STALLED),      # three cadences: attempts stopped
        (at(hours=62),    Health.STALLED),      # Era 2's actual age
        (at(days=30),     Health.STALLED),      # and it never recovers by waiting
    ]
    for now, expected in timeline:
        ev = WorkEvidence(last_heartbeat_at=now, **frozen)  # heartbeat always fresh
        got = derive_health(now, ev, cadence_sec=HOUR)
        assert got == expected, (
            "at now=%s expected %s, got %s -- a frozen worker with a live "
            "heartbeat must not read healthy" % (now.isoformat(), expected, got)
        )


def test_T4_liveness_and_productivity_are_independent_axes():
    """Same work evidence, two very different heartbeats. The health value
    is identical, because health is about WORK. Liveness is reported
    separately (the `status` column) and the two must not be conflated."""
    work = dict(started_at=at(hours=-100),
                last_attempt_at=at(hours=-62), last_success_at=at(hours=-62))
    beating = WorkEvidence(last_heartbeat_at=T0, **work)
    silent = WorkEvidence(last_heartbeat_at=at(hours=-62), **work)
    assert derive_health(T0, beating, cadence_sec=HOUR) == Health.STALLED
    assert derive_health(T0, silent, cadence_sec=HOUR) == Health.STALLED


# ---------------------------------------------------------------------------
# CONTROLS: negative, positive, cheat
# ---------------------------------------------------------------------------

def test_control_NEGATIVE_no_evidence_yields_no_productive_claim():
    """Nothing at all is known. The instrument must not invent a verdict in
    either direction: absence of evidence is its own state."""
    ev = WorkEvidence()
    got = derive_health(T0, ev, cadence_sec=HOUR)
    assert got == Health.NO_WORK_OBSERVED
    assert got != Health.PRODUCTIVE


def test_control_POSITIVE_real_signal_is_detected():
    """The instrument can see a genuinely working loop. Without this, a
    monitor that returns 'not productive' for everything would pass every
    other test in this file."""
    now = T0
    for elapsed_min in (0, 5, 30, 59, 120):
        n = now + timedelta(minutes=elapsed_min)
        ev = WorkEvidence(started_at=at(hours=-48), last_heartbeat_at=n,
                          last_attempt_at=n - timedelta(seconds=90),
                          last_success_at=n - timedelta(seconds=30))
        assert derive_health(n, ev, cadence_sec=HOUR) == Health.PRODUCTIVE


def test_control_CHEAT_success_without_an_attempt_is_refused():
    """Inject success directly, the way a writer that records only its good
    news would. The channel must refuse to read it as productive.

    This is not hypothetical: agora.agent_heartbeats row 'MachineProbe-M4'
    carried last_work_success_at with last_work_attempt_at NULL when this
    seat measured it on 2026-09-11.
    """
    ev = WorkEvidence(started_at=at(hours=-5), last_heartbeat_at=T0,
                      last_attempt_at=None, last_success_at=at(minutes=-1))
    got = derive_health(T0, ev, cadence_sec=HOUR)
    assert got == Health.INCOHERENT
    assert got != Health.PRODUCTIVE


def test_control_CHEAT_future_timestamp_is_refused():
    """The cheapest way to stay green forever is to write tomorrow's date."""
    ev = WorkEvidence(started_at=at(hours=-5), last_heartbeat_at=T0,
                      last_attempt_at=at(hours=+5), last_success_at=at(hours=+5))
    assert derive_health(T0, ev, cadence_sec=HOUR) == Health.INCOHERENT


def test_control_CHEAT_inherited_success_from_a_previous_process_is_refused():
    """Restarting must not inherit the dead incarnation's good news. A
    success that predates this process is not evidence about this process."""
    ev = WorkEvidence(started_at=at(minutes=-10),      # restarted 10 min ago
                      last_heartbeat_at=T0,
                      last_attempt_at=at(hours=-40),
                      last_success_at=at(hours=-40))   # from the last life
    assert derive_health(T0, ev, cadence_sec=HOUR) == Health.INCOHERENT


def test_control_CHEAT_success_long_after_the_last_attempt_is_refused():
    """A success field advancing while the attempt field stands still means
    the attempt field is not tracking the work the success field claims."""
    ev = WorkEvidence(started_at=at(hours=-10), last_heartbeat_at=T0,
                      last_attempt_at=at(hours=-5), last_success_at=at(minutes=-1))
    assert derive_health(T0, ev, cadence_sec=HOUR) == Health.INCOHERENT


# ---------------------------------------------------------------------------
# GROUND TRUTH: Pronoia's own two documented failures must come out failed
# ---------------------------------------------------------------------------

def test_ground_truth_era2_real_numbers_read_stalled():
    """Measured 2026-09-11T16:58Z against the canonical Postgres:

        pid 9620 on M4, status='online', last_heartbeat 2026-09-11 12:58:14-04
        all five pronoia_* stages: 0 rows since 2026-09-09
        newest dashboard push: 2026-09-09T02:15:10Z, 62.6 h earlier

    The heartbeat was seconds old. The work was two and a half days old.
    """
    now = datetime(2026, 9, 11, 16, 58, 0, tzinfo=timezone.utc)
    last_real_work = datetime(2026, 9, 9, 2, 15, 10, tzinfo=timezone.utc)
    ev = WorkEvidence(
        started_at=datetime(2026, 9, 11, 15, 3, 40, tzinfo=timezone.utc),
        last_heartbeat_at=datetime(2026, 9, 11, 16, 58, 14, tzinfo=timezone.utc),
        last_attempt_at=last_real_work,
        last_success_at=last_real_work,
    )
    # Success predates this process incarnation (restarted 11:03 local /
    # 15:03Z) -- the evidence is incoherent BEFORE it is even stale, which is
    # a stronger statement than STALLED and the correct one.
    assert derive_health(now, ev, cadence_sec=4 * HOUR) == Health.INCOHERENT

    # And with the restart ignored (treating it as one continuous process),
    # it is STALLED. Either way it is never PRODUCTIVE.
    ev_continuous = WorkEvidence(
        started_at=datetime(2026, 5, 23, 0, 0, 0, tzinfo=timezone.utc),
        last_heartbeat_at=datetime(2026, 9, 11, 16, 58, 14, tzinfo=timezone.utc),
        last_attempt_at=last_real_work,
        last_success_at=last_real_work,
    )
    assert derive_health(now, ev_continuous, cadence_sec=4 * HOUR) == Health.STALLED


def test_ground_truth_era1_health_report_would_not_pass():
    """Era 1's own report, verbatim: 'Status: HEALTHY / Process Running: Yes
    / Recent Log Lines: 0 / Errors: 0'. Zero log lines is zero work
    evidence, and zero errors is not a success."""
    ev = WorkEvidence(started_at=datetime(2026, 3, 31, 12, 0, tzinfo=timezone.utc),
                      last_heartbeat_at=datetime(2026, 3, 31, 19, 14, tzinfo=timezone.utc),
                      last_attempt_at=None, last_success_at=None)
    now = datetime(2026, 3, 31, 19, 14, tzinfo=timezone.utc)
    assert derive_health(now, ev, cadence_sec=HOUR) == Health.NO_WORK_OBSERVED


# ---------------------------------------------------------------------------
# The instrument's own guard rails
# ---------------------------------------------------------------------------

def test_naive_datetimes_are_refused_not_guessed():
    """A naive timestamp would compare against whatever timezone the host
    happened to be in. Refuse rather than silently depend on the host."""
    ev = WorkEvidence(started_at=datetime(2026, 9, 11, 12, 0),
                      last_attempt_at=datetime(2026, 9, 11, 12, 0))
    with pytest.raises(ValueError, match="naive datetime"):
        derive_health(T0, ev, cadence_sec=HOUR)


def test_cadence_must_be_positive():
    with pytest.raises(ValueError, match="cadence_sec"):
        derive_health(T0, WorkEvidence(), cadence_sec=0)


def test_every_health_value_is_reachable():
    """A vocabulary with an unreachable value is the zero_output detector of
    Era 1 all over again: a branch that could never fire, reported as if it
    were a check. Every state below is produced by a real input."""
    reached = set()
    cases = [
        WorkEvidence(started_at=at(minutes=-5)),                                   # BOOTING
        WorkEvidence(started_at=at(hours=-10)),                                    # NO_WORK_OBSERVED
        WorkEvidence(started_at=at(hours=-5), last_attempt_at=at(minutes=-1),
                     last_success_at=at(minutes=-61)),                             # WORKING
        WorkEvidence(started_at=at(hours=-5), last_attempt_at=at(minutes=-10),
                     last_success_at=at(minutes=-9)),                              # PRODUCTIVE
        WorkEvidence(started_at=at(hours=-5), last_attempt_at=at(minutes=-2)),     # FAILING
        WorkEvidence(started_at=at(hours=-100), last_attempt_at=at(hours=-62),
                     last_success_at=at(hours=-62)),                               # STALLED
        WorkEvidence(started_at=at(hours=-5), last_success_at=at(minutes=-1)),     # INCOHERENT
    ]
    for ev in cases:
        reached.add(derive_health(T0, ev, cadence_sec=HOUR))

    everything = {v for k, v in vars(Health).items() if not k.startswith("_")
                  and isinstance(v, str)}
    assert reached == everything, "unreachable health values: %s" % (everything - reached)


def test_stall_multiple_is_not_tuned_to_let_era2_pass():
    """Guard against the temptation this seat is most at risk of: widening
    the window until its own loop looks fine. Era 2 was 62.6 h stale on a
    4 h cadence -- 15.6 cadences. The default must be far below that."""
    assert DEFAULT_STALL_MULTIPLE < 5.0
    era2_staleness_in_cadences = 62.6 / 4.0
    assert era2_staleness_in_cadences > DEFAULT_STALL_MULTIPLE * 3
