"""N3 exactness: Warp world kernel == wforge (trace hash + final charge), CPU and CUDA; skip_lin caught.
Runs in nv-venv-w; skipped where warp is absent (gw-venv)."""
from __future__ import annotations

import pytest

wp = pytest.importorskip("warp")

from primordial.nv.warp import oracle, smoke  # noqa: E402


def _devices():
    wp.init()
    return [d.alias for d in wp.get_devices()]


DEVICES = ["cpu", pytest.param("cuda:0", marks=pytest.mark.skipif("cuda:0" not in _devices(), reason="no CUDA"))]


def test_smoke_xorshift_exact_on_every_device():
    res = smoke.run(n=512, rounds=4)
    assert res["devices"] and all(v["exact"] for v in res["devices"].values())


@pytest.mark.parametrize("device", DEVICES)
def test_world_episode_exact_vs_wforge(device):
    res = oracle.run(device, worlds=12, envs=6)
    assert res["exact"] == res["episodes"] == 72


@pytest.mark.parametrize("device", DEVICES)
def test_one_tick_per_launch_exact_vs_wforge(device):
    res = oracle.run(device, worlds=6, envs=4, world_base=20, ticks=1)
    assert res["exact"] == res["episodes"] == 24


@pytest.mark.parametrize("device", DEVICES)
def test_skip_lin_cheat_is_caught(device):
    res = oracle.run(device, worlds=12, envs=6, cheat="skip_lin")
    assert res["trace_eq"] == 0 and res["exact"] == 0


def test_sampled_worlds_cover_the_mechanics():
    """The oracle's worlds must exercise delay, stochastic kicks, regime flips and two slots."""
    res = oracle.run("cpu", worlds=12, envs=1)
    rows = res["rows"]
    assert any(r["delay"] > 0 for r in rows) and any(r["stoch"] > 0 for r in rows)
    assert any(r["regime"] > 0 for r in rows) and any(r["n_slots"] == 2 for r in rows)
