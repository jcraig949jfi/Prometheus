"""Controls for the proposed null-bound invariant (ATALANTA-04 Q5).

Base doctrine: every change ships with a POSITIVE control and a CHEAT
control where the change is measured; a NEGATIVE control is welcome but
does not substitute. All three are here, plus the Atalanta replay.

    NEGATIVE  a loop with a live producer must NOT park -- the instrument
              does not manufacture dormancy where there is none
    POSITIVE  a loop with a dead producer MUST park at the bound -- the
              instrument detects the real thing
    CHEAT     a loop that writes an artifact every tick while producing no
              domain output MUST STILL PARK -- the measurement channel is
              actually capable of observing what it claims to measure

The cheat control is the one that matters here. Atalanta wrote a
well-formed artifact on all 354 of its dead ticks. Any bound keyed to
"did the tick emit something" would have scored 354 productive ticks and
never fired. That is not a hypothetical: it is what happened.

Run: python -m pytest roles/Atalanta/reference/test_null_bound.py -q
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from null_bound import PARKED, RUNNING, BoundedLoop, BoundNotDeclared  # noqa: E402


# --------------------------------------------------------------------------
# Construction: a loop with no bound, or no accountable seat, cannot exist
# --------------------------------------------------------------------------

def test_refuses_a_loop_with_no_bound():
    for bad in (0, -1, None, "fifty"):
        with pytest.raises(BoundNotDeclared):
            BoundedLoop(name="unbounded", tick=lambda: False,
                        bound=bad, accountable_seat="Atalanta")


def test_refuses_a_bound_with_no_accountable_seat():
    for bad in ("", "   ", None):
        with pytest.raises(BoundNotDeclared):
            BoundedLoop(name="unaddressed", tick=lambda: False,
                        bound=50, accountable_seat=bad)


# --------------------------------------------------------------------------
# NEGATIVE control: live producer, no park
# --------------------------------------------------------------------------

def test_negative_control_live_producer_never_parks():
    """A loop that produces on every tick must run to max_ticks unparked."""
    loop = BoundedLoop(name="live", tick=lambda: {"rows": 3},
                       bound=50, accountable_seat="Atalanta")
    assert loop.run(max_ticks=500) == RUNNING
    assert loop.park_record is None
    assert loop.ticks_run == 500
    assert loop.productive_ticks == 500
    assert loop.consecutive_no_ops == 0


def test_negative_control_intermittent_producer_never_parks():
    """Real loops are bursty. One productive tick inside the bound resets
    the counter, so a slow-but-alive producer is not parked as dead."""
    n = {"i": 0}

    def tick():
        n["i"] += 1
        return {"rows": 1} if n["i"] % 40 == 0 else None  # produces every 40th

    loop = BoundedLoop(name="bursty", tick=tick, bound=50,
                       accountable_seat="Atalanta")
    assert loop.run(max_ticks=400) == RUNNING
    assert loop.park_record is None
    assert loop.productive_ticks == 10


# --------------------------------------------------------------------------
# POSITIVE control: dead producer, parks exactly at the bound
# --------------------------------------------------------------------------

def test_positive_control_dead_producer_parks_at_the_bound():
    delivered = []
    loop = BoundedLoop(name="dead", tick=lambda: None, bound=50,
                       accountable_seat="Archaeon",
                       notify=delivered.append)
    assert loop.run(max_ticks=500) == PARKED
    assert loop.ticks_run == 50, "must park AT the bound, not after it"
    assert loop.productive_ticks == 0
    r = loop.park_record
    assert r is not None
    assert r.consecutive_no_ops == 50 and r.bound == 50
    assert r.accountable_seat == "Archaeon"
    assert r.last_productive_tick is None
    assert len(delivered) == 1, "exactly one notification, not one per tick"


def test_parked_loop_stays_parked_and_does_not_re_notify():
    """The brake holds: further ticks do nothing and do not re-alarm.
    This is the direct contrast with daemon.py:547, where `>=` with no
    return re-fired the alarm on every subsequent tick."""
    delivered = []
    loop = BoundedLoop(name="dead", tick=lambda: None, bound=5,
                       accountable_seat="Archaeon", notify=delivered.append)
    loop.run(max_ticks=100)
    ticks_at_park = loop.ticks_run
    for _ in range(100):
        assert loop.run_tick() == PARKED
    assert loop.ticks_run == ticks_at_park, "a parked loop must not tick"
    assert len(delivered) == 1, "must not re-notify once parked"


# --------------------------------------------------------------------------
# CHEAT control: the tick emits every time but produces nothing
# --------------------------------------------------------------------------

def test_cheat_control_artifact_every_tick_still_parks(tmp_path):
    """Atalanta's exact shape: a well-formed artifact on every dead tick.

    The loop below WRITES A FILE on every tick and returns no domain
    output. A bound keyed to emission would never fire. The invariant
    keys on the declared productivity signal, so it must still park.
    """
    written = []

    def tick_that_emits_but_produces_nothing():
        p = tmp_path / "upstream_not_found_{}.json".format(len(written))
        p.write_text('{"reason": "upstream_not_found"}', encoding="utf-8")
        written.append(p)
        return None  # the declared productivity signal: nothing produced

    loop = BoundedLoop(name="cheat", tick=tick_that_emits_but_produces_nothing,
                       bound=50, accountable_seat="Archaeon")
    assert loop.run(max_ticks=500) == PARKED
    assert loop.ticks_run == 50
    assert len(written) == 50, "the artifacts were really written"
    # The measurement channel saw through 50 well-formed artifacts.
    assert loop.productive_ticks == 0


def test_cheat_control_emission_keyed_counter_would_have_failed(tmp_path):
    """Shows the cheat is a real cheat: score the same loop by emission
    and it looks perfectly healthy. This test asserts the FAILURE of the
    naive instrument, so the cheat control cannot silently become vacuous."""
    emissions = {"n": 0}

    def naive_productivity_signal():
        emissions["n"] += 1
        return {"artifact_written": True}  # "I emitted, therefore I produced"

    loop = BoundedLoop(name="naive", tick=naive_productivity_signal,
                       bound=50, accountable_seat="Archaeon")
    assert loop.run(max_ticks=354) == RUNNING
    assert loop.park_record is None
    assert loop.productive_ticks == 354
    # 354 dead ticks scored as 354 productive ones. This is the defect.


# --------------------------------------------------------------------------
# Replay: what the invariant would have done to Atalanta
# --------------------------------------------------------------------------

def test_atalanta_replay_bounds_354_ticks_to_50():
    """Measured history: 354 ticks, all non-productive, 305 alarm rows.
    Under the invariant: 50 ticks, one park, one notification."""
    ATALANTA_TICKS = 354
    ATALANTA_ALARM_ROWS = 305
    delivered = []
    loop = BoundedLoop(name="AtalantaPrimitiveHunterLoop", tick=lambda: None,
                       bound=50, accountable_seat="Aporia", notify=delivered.append)
    loop.run(max_ticks=ATALANTA_TICKS)

    assert loop.state == PARKED
    assert loop.ticks_run == 50
    assert len(delivered) == 1

    ticks_avoided = ATALANTA_TICKS - loop.ticks_run
    assert ticks_avoided == 304
    alarms_avoided = ATALANTA_ALARM_ROWS - len(delivered)
    assert alarms_avoided == 304
