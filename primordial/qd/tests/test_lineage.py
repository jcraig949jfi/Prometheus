"""E2 lineage archive: every win is streamed with its parent; non-wins are not."""
import numpy as np
import pytest
import redis

from primordial.qd.e2_run import LineageArchive, read_events
from primordial.qd.stubworld import GLEN


@pytest.fixture
def r():
    c = redis.Redis(host="127.0.0.1", port=6394)
    try:
        c.ping()
    except redis.ConnectionError:
        pytest.skip("lane E substrate not running on 6394")
    return c


def _g(*bs):
    return np.array([list(b) for b in bs], np.uint8)


def test_wins_stream_with_parent_and_losses_do_not(r):
    a = LineageArchive(r, "test-lin", GLEN)
    a.clear()
    cells = np.array([3, 3, 9], np.uint32)
    fits = np.array([10, 20, 5], np.int32)
    kids = _g(b"\x01" * 8, b"\x02" * 8, b"\x03" * 8)
    parents = _g(b"\xa1" * 8, b"\xa2" * 8, b"\xa3" * 8)
    assert a.insert_lineage(cells, fits, kids, parents, gen=4) == 2  # within-batch loser (fit 10) never streams
    ev = sorted(read_events(r, a.skey))
    assert ev == [(3, 20, b"\x02" * 8, b"\xa2" * 8, 4), (9, 5, b"\x03" * 8, b"\xa3" * 8, 4)]
    assert a.insert_lineage(np.array([9], np.uint32), np.array([4], np.int32), kids[:1], parents[:1], gen=5) == 0
    assert len(read_events(r, a.skey)) == 2
    a.clear()
