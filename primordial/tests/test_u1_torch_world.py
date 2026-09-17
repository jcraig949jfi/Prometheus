"""U1: the B world step as torch integer ops == wforge by trace and obs hash; skip_lin caught."""
from __future__ import annotations

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from primordial.nv.cudagraph.oracle import run  # noqa: E402
from primordial.nv.cudagraph.world import umod, xs_next  # noqa: E402

DEVICES = ["cpu"] + (["cuda"] if torch.cuda.is_available() else [])
WORLDS, ENVS = 16, 4


def np_xs(s):
    with np.errstate(over="ignore"):
        s = s ^ (s << np.uint64(13))
        s = s ^ (s >> np.uint64(7))
        s = s ^ (s << np.uint64(17))
        return s, s * np.uint64(0x2545F4914F6CDD1D)


@pytest.mark.parametrize("device", DEVICES)
def test_xorshift_and_unsigned_mod_match_uint64(device):
    rng = np.random.default_rng(5)
    s = rng.integers(0, 2**64, size=4096, dtype=np.uint64)
    s[:4] = [1, 2**63, 2**64 - 1, 2**63 - 1]
    ts = torch.from_numpy(s.view(np.int64).copy()).to(device)
    for _ in range(3):
        s, out = np_xs(s)
        ts, tout = xs_next(ts)
        assert np.array_equal(ts.cpu().numpy().view(np.uint64), s)
        assert np.array_equal(tout.cpu().numpy().view(np.uint64), out)
        for r in (1, 3, 7, 13, 16, 97, 65536, 2**62 + 3):
            assert np.array_equal(umod(tout, r).cpu().numpy(), (out % np.uint64(r)).astype(np.int64))


@pytest.fixture(scope="module")
def results():
    return {d: run(WORLDS, ENVS, device=d) for d in DEVICES}


@pytest.mark.parametrize("device", DEVICES)
def test_torch_world_equals_wforge(results, device):
    res = results[device]
    assert res["episodes"] == WORLDS * ENVS
    assert res["trace_eq"] == res["episodes"]
    assert res["obs_eq"] == res["episodes"]


def test_sample_exercises_every_mechanic(results):
    rows = results["cpu"]["rows"]
    for key in ("delay", "stoch", "regime", "corrupt", "obs_delay"):
        assert any(r[key] for r in rows), f"no sampled world has {key}; the equality would not cover it"


@pytest.mark.parametrize("device", DEVICES)
def test_skip_lin_is_caught(device):
    res = run(4, ENVS, cheat="skip_lin", device=device)
    assert res["trace_eq"] == 0


@pytest.mark.skipif(not torch.cuda.is_available(), reason="no CUDA")
def test_step_and_observe_never_sync_the_host():
    from primordial.nv.cudagraph.world import TorchWorld
    from primordial.soup.b1.common import action_tensor, episode_seeds, make_world
    for g in range(WORLDS):
        mech, wid = make_world(g)
        w = TorchWorld(mech, wid, device="cuda")
        w.reset(episode_seeds(ENVS, base=7000 + g))
        acts = torch.from_numpy(action_tensor(mech, ENVS, seed=g)).cuda()
        torch.cuda.set_sync_debug_mode("error")
        try:
            for t in range(8):
                w.step(acts[t])
                w.observe()
        finally:
            torch.cuda.set_sync_debug_mode("default")
