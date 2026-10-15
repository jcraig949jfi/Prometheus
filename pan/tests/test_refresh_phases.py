"""PAN-53 refresh phase timings: the Phases helper. No database."""
import pytest

from pan.refresh import Phases


class _Clock:
    def __init__(self):
        self.t = 100.0

    def __call__(self):
        return self.t


def test_phases_record_each_named_block():
    """POSITIVE: each block's wall time is recorded under its name, from the injected clock."""
    clk = _Clock()
    ph = Phases(clock=clk)
    with ph("fetch"):
        clk.t += 2.0
    with ph("upsert"):
        clk.t += 80.0
    assert ph.seconds == {"fetch": 2.0, "upsert": 80.0}


def test_a_repeated_name_accumulates():
    """POSITIVE: catalog_read is used twice in a refresh; both reads count."""
    clk = _Clock()
    ph = Phases(clock=clk)
    with ph("catalog_read"):
        clk.t += 0.5
    with ph("catalog_read"):
        clk.t += 1.0
    assert ph.seconds == {"catalog_read": 1.5}


def test_a_failing_phase_is_still_timed_and_the_error_propagates():
    """NEGATIVE: a phase that raises is recorded and its exception is not swallowed."""
    clk = _Clock()
    ph = Phases(clock=clk)
    with pytest.raises(RuntimeError):
        with ph("commits"):
            clk.t += 7.0
            raise RuntimeError("boom")
    assert ph.seconds == {"commits": 7.0}


def test_untimed_blocks_do_not_appear():
    """CHEAT: a timer that reports names it never measured (or zeros for everything) would pass a key check; the
    clock must have advanced inside the block for a non-zero value, and unused names must be absent."""
    clk = _Clock()
    ph = Phases(clock=clk)
    clk.t += 50.0                       # time outside any phase
    with ph("chunk"):
        pass
    assert ph.seconds == {"chunk": 0.0}
    assert "embed" not in ph.seconds
