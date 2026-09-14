"""O5: GPU lease pm:gpu:lease. Live tests use throwaway db 15 on 6390 and skip without it."""
from __future__ import annotations

import json
import time

import pytest

from primordial.bus import bus


@pytest.fixture
def live(monkeypatch):
    redis = pytest.importorskip("redis")
    url = "redis://127.0.0.1:6390/15"
    r = redis.Redis.from_url(url, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    r.flushdb()
    monkeypatch.setattr(bus, "URL", url)
    monkeypatch.setenv("PM_LANE", "F")
    monkeypatch.setenv("PM_TAG", "t-f")
    yield r
    r.flushdb()


def test_second_holder_blocks_then_gets_it_after_release(live, monkeypatch):
    with bus.gpu_lease("timing A", ttl_s=30, r=live) as rec:
        assert bus.lease_holder(live)["holder"] == "F[t-f]"
        monkeypatch.setenv("PM_LANE", "U")
        monkeypatch.setenv("PM_TAG", "t-u")
        t0 = time.monotonic()
        with pytest.raises(bus.LeaseBusy, match=r"F\[t-f\]"):
            bus.lease_acquire("timing U", ttl_s=30, wait_s=0.6, poll_s=0.2, r=live)
        assert time.monotonic() - t0 >= 0.6                          # it waited, then refused
        assert not rec["lost"]
    assert bus.lease_holder(live) is None
    got = bus.lease_acquire("timing U", ttl_s=30, r=live)
    assert got["holder"] == "U[t-u]" and "took_over" not in got
    assert bus.lease_release(got, r=live)


def test_expired_lease_is_taken_over_and_old_holder_cannot_release_it(live, monkeypatch):
    stale = bus.lease_acquire("crashed harness", ttl_s=30, r=live)
    stale["until"] = round(time.time() - 1, 3)                       # `until` passed; the key lingers
    live.set(bus.GPU_LEASE, bus._lease_val(stale), px=30_000)
    assert bus.lease_holder(live) is None
    monkeypatch.setenv("PM_LANE", "W")
    monkeypatch.setenv("PM_TAG", "t-w")
    new = bus.lease_acquire("timing W", ttl_s=30, r=live)
    assert new["took_over"] == "F[t-f]"
    assert not bus.lease_release(stale, r=live)                      # CAS: the old record is gone
    assert not bus.lease_renew(stale, r=live)
    assert bus.lease_holder(live)["holder"] == "W[t-w]"


def test_redis_ttl_expiry_frees_the_lease(live):
    bus.lease_acquire("short", ttl_s=0.3, r=live)
    time.sleep(0.5)
    assert bus.lease_holder(live) is None
    assert bus.lease_acquire("next", ttl_s=5, r=live)["holder"] == "F[t-f]"


def test_context_manager_renews_past_ttl(live):
    with bus.gpu_lease("long timing", ttl_s=0.6, r=live) as rec:
        time.sleep(1.5)                                              # > 2 TTLs
        assert bus.lease_holder(live)["token"] == rec["token"]
        assert not rec["lost"]
    assert live.get(bus.GPU_LEASE) is None


def test_host_load_records_the_lease_holder(live):
    assert bus.host_load(live)["gpu_lease"] is None
    with bus.gpu_lease("nsight capture", ttl_s=30, r=live):
        hl = bus.host_load(live)
    assert hl["gpu_lease"]["holder"] == "F[t-f]" and hl["gpu_lease"]["purpose"] == "nsight capture"


def test_cli_take_show_release(live, capsys):
    from primordial.bus.__main__ import main
    assert main(["lease", "take", "30", "cli timing"]) == 0
    rec = json.loads(capsys.readouterr().out.strip())
    assert main(["lease", "show"]) == 0 and "cli timing" in capsys.readouterr().out
    assert main(["lease", "take", "30", "second"]) == 1
    capsys.readouterr()
    assert main(["lease", "release", json.dumps(rec)]) == 0
    assert main(["lease", "show"]) == 0 and capsys.readouterr().out.strip().endswith("free")
