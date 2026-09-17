"""U4: tt_digits brain on device -- logits bitwise == E7's numpy forward; eager and CUDA-graph
rollouts == E7.rollout 128/128; the skip-odd-core cheat is caught."""
from __future__ import annotations

import numpy as np
import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("redis")

from primordial.nv.cudagraph.brains import TTDigitsBrain  # noqa: E402
from primordial.nv.cudagraph.rollout import TorchRollout, compare, genomes  # noqa: E402
from primordial.qd import e6_run as E6  # noqa: E402
from primordial.qd import e7_run as E7  # noqa: E402

DEVICES = ["cpu"] + (["cuda"] if torch.cuda.is_available() else [])
WORLD, P, FAM = 4, 128, "tt_digits"


@pytest.fixture(scope="module")
def g7():
    return E7.G7(WORLD, FAM)


@pytest.mark.parametrize("device", DEVICES)
def test_tt_digits_logits_bitwise_equal_numpy(g7, device):
    params, _ = genomes(g7, 8, seed=1)
    rng = np.random.default_rng(3)
    obs = rng.integers(-40, 65536, size=(8, g7.S, g7.D), dtype=np.int64)      # negatives wrap like astype(uint16)
    gidx = np.repeat(np.arange(8), g7.S)
    genv = torch.arange(8, device=device)
    for cheat in (False, True):
        ref = g7.fam.logits(params, obs.reshape(-1, g7.D), gidx, cheat).reshape(8, g7.S, -1)
        got = TTDigitsBrain(params, genv, cheat).logits(torch.from_numpy(obs).to(device)).cpu().numpy()
        assert got.dtype == np.float32
        assert np.array_equal(got.view(np.uint32), ref.astype(np.float32).view(np.uint32))


@pytest.mark.parametrize("device", DEVICES)
def test_tt_digits_rollout_equals_e7_128(device):
    r = compare(WORLD, P, E6.TRAIN, device, fam=FAM)
    assert (r["fitness_eq"], r["cells_eq"]) == (P, P)


@pytest.mark.skipif(not torch.cuda.is_available(), reason="no CUDA")
def test_tt_digits_graph_equals_e7_and_eager_state(g7):
    from primordial.nv.cudagraph.graph import GraphRollout
    g = genomes(g7, P, seed=0)
    ref_fit, ref_cells, _, _ = E7.rollout(g7, g, E6.TRAIN)
    gr = GraphRollout(g7, "cuda", ticks_per_graph=1)
    fit, cells = gr.run(g, E6.TRAIN)
    assert (fit == ref_fit).sum() == P and (cells == ref_cells).sum() == P
    eager = TorchRollout(g7, "cuda")
    eager.run(g, E6.TRAIN)
    for a, b in zip(gr.state(), eager.state()):
        assert torch.equal(a, b)
    fit_c, cells_c = gr.run(g, E6.TRAIN, cheat=True)
    ref_fit_c, ref_cells_c, _, _ = E7.rollout(g7, g, E6.TRAIN, cheat=True)
    assert (fit_c == ref_fit_c).sum() == P and (cells_c == ref_cells_c).sum() == P
    assert ((fit_c != ref_fit) | (cells_c != ref_cells)).sum() >= P // 2
