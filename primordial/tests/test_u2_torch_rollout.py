"""U2: linear brain + codebook decode + descriptor counters + torch world == E7.rollout."""
from __future__ import annotations

import numpy as np
import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("redis")

from primordial.nv.cudagraph.rollout import TorchRollout, compare, genomes, linear_logits  # noqa: E402
from primordial.qd import e6_run as E6  # noqa: E402
from primordial.qd import e7_run as E7  # noqa: E402

DEVICES = ["cpu"] + (["cuda"] if torch.cuda.is_available() else [])
WORLD, P = 4, 128


@pytest.mark.parametrize("device", DEVICES)
def test_linear_logits_bitwise_equal_numpy(device):
    g7 = E7.G7(WORLD, "linear")
    (W, b), _ = genomes(g7, 8, seed=1)
    rng = np.random.default_rng(2)
    obs = rng.integers(-40, 65536, size=(8, g7.S, g7.D), dtype=np.int64)      # charge channel can be negative
    gidx = np.repeat(np.arange(8), g7.S)
    for cheat in (False, True):
        ref = g7.fam.logits((W, b), obs.reshape(-1, g7.D), gidx, cheat).reshape(8, g7.S, -1)
        dev = torch.device(device)
        feat_on = (torch.arange(g7.D, device=dev) % 2 == 0) if cheat else None
        got = linear_logits(torch.from_numpy(obs).to(dev), torch.from_numpy(W).to(dev), torch.from_numpy(b).to(dev),
                            feat_on).cpu().numpy()
        assert got.dtype == np.float32
        assert np.array_equal(got.view(np.uint32), ref.astype(np.float32).view(np.uint32))


@pytest.mark.parametrize("device", DEVICES)
def test_rollout_fitness_and_cells_equal_e7_128(device):
    r = compare(WORLD, P, E6.TRAIN, device)
    assert (r["fitness_eq"], r["cells_eq"]) == (P, P)


@pytest.mark.parametrize("device", DEVICES)
def test_cheats_move_the_result(device):
    honest = compare(WORLD, P, E6.TRAIN, device)
    assert honest["fitness_eq"] == P
    g7 = E7.G7(WORLD, "linear")
    g = genomes(g7, P, seed=0)
    ref_fit, ref_cells, _, _ = E7.rollout(g7, g, E6.TRAIN)
    fit_b, cells_b = TorchRollout(g7, device).run(g, E6.TRAIN, cheat=True)
    assert ((fit_b != ref_fit) | (cells_b != ref_cells)).sum() >= P // 2
    fit_w, _ = TorchRollout(g7, device, world_cheat="skip_lin").run(g, E6.TRAIN)
    assert (fit_w != ref_fit).sum() >= P // 2


@pytest.mark.skipif(not torch.cuda.is_available(), reason="no CUDA")
def test_tick_never_syncs_the_host():
    g7 = E7.G7(WORLD, "linear")
    ro = TorchRollout(g7, "cuda")
    ro.load(genomes(g7, 16, seed=0), E6.TRAIN)
    torch.cuda.set_sync_debug_mode("error")
    try:
        for _ in range(8):
            ro.tick()
    finally:
        torch.cuda.set_sync_debug_mode("default")
