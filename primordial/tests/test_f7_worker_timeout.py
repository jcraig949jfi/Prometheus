"""F7: an idle worker survives its own blocking read (redis-py 8 defaults socket_timeout to 5 s)."""
from __future__ import annotations

import pytest

from primordial.fabric import worker as W
from primordial.tests._live import live_url


def test_worker_socket_timeout_exceeds_serve_block():
    import inspect
    block_ms = inspect.signature(W.Worker.serve).parameters["block_ms"].default
    assert W.SOCKET_TIMEOUT_S > block_ms / 1000 + 1


def test_idle_blocking_read_does_not_time_out():
    pytest.importorskip("redis")
    r = W._redis(live_url())
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable")
    assert r.connection_pool.connection_kwargs["socket_timeout"] == W.SOCKET_TIMEOUT_S
    key = "pm:test:g-idle-block"
    r.delete(key)
    assert r.xread({key: "$"}, block=5500) in ([], None)      # 5.5 s blocked, no message: must not raise
