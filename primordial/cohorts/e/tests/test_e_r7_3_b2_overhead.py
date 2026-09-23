"""E-R7-3: B2 search-overhead probe -- genome packing round-trips, parts add up, RefB2 replay of the elites is exact."""
from __future__ import annotations

import numpy as np
import pytest

from primordial.cohorts.e import r7_b2_overhead as O


def _redis_up():
    try:
        import redis
        redis.Redis.from_url(O.ARCHIVE_URL).ping()
        return True
    except Exception:
        return False


def test_pack_unpack_roundtrip_and_glen():
    W, b = O.init(np.random.Generator(np.random.PCG64(1)), 5)
    raw = O.pack(W, b)
    assert raw.shape == (5, O.GLEN) and raw.dtype == np.uint8
    W2, b2 = O.unpack(raw)
    assert np.array_equal(W, W2) and np.array_equal(b, b2)
    Wm, bm = O.mutate(np.random.Generator(np.random.PCG64(2)), W, b, rate=1.0)
    assert not np.array_equal(Wm, W) and np.array_equal(O.unpack(raw)[0], W)       # mutate copies


class _Ctx:
    def __init__(self):
        self.rows = []

    def emit(self, row):
        self.rows.append(row)


@pytest.mark.skipif(not _redis_up(), reason="archive redis 6394 not reachable")
def test_overhead_job_row_parts_and_oracle():
    c = _Ctx()
    O.job(c, gens=3, batch=4, n_train=4, run_seed=99, dev=True)
    (row,) = c.rows
    assert row["kind"] == "b2_search_overhead" and row["status"] == "dev" and row["timed_gens"] == 2
    assert 0.0 <= row["overhead_fraction"] <= 1.0 and row["episodes_per_gen"] == 16
    assert row["oracle_refb2"]["equal"] == row["oracle_refb2"]["checked"] > 0
    assert abs(row["effective_s_per_episode_incl_overhead"] * 16 - row["total_s_per_gen"]) < 1e-12
