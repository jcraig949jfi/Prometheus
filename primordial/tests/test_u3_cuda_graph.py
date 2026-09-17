"""U3: the closed-loop tick captured as a CUDA graph == eager == E7.rollout; reloads are real."""
from __future__ import annotations

import numpy as np
import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("redis")
if not torch.cuda.is_available():
    pytest.skip("no CUDA", allow_module_level=True)

from primordial.nv.cudagraph.graph import GraphRollout  # noqa: E402
from primordial.nv.cudagraph.rollout import TorchRollout, genomes  # noqa: E402
from primordial.qd import e6_run as E6  # noqa: E402
from primordial.qd import e7_run as E7  # noqa: E402

WORLD, P = 4, 128


@pytest.fixture(scope="module")
def g7():
    return E7.G7(WORLD, "linear")


def e7_ref(g7, g, seeds, cheat=False):
    fit, cells, _, _ = E7.rollout(g7, g, np.asarray(seeds, np.int64), cheat=cheat)
    return fit, cells


@pytest.mark.parametrize("K", [1, 7, 10**6])
def test_graph_replay_equals_e7_and_eager_state(g7, K):
    g = genomes(g7, P, seed=0)
    gr = GraphRollout(g7, "cuda", ticks_per_graph=K)
    fit, cells = gr.run(g, E6.TRAIN)
    ref_fit, ref_cells = e7_ref(g7, g, E6.TRAIN)
    assert (fit == ref_fit).sum() == P and (cells == ref_cells).sum() == P
    eager = TorchRollout(g7, "cuda")
    eager.run(g, E6.TRAIN)
    for a, b in zip(gr.state(), eager.state()):
        assert torch.equal(a, b)


def test_reload_new_genomes_and_seeds_into_the_captured_graph(g7):
    gr = GraphRollout(g7, "cuda", ticks_per_graph=1)
    g0, g1 = genomes(g7, P, seed=0), genomes(g7, P, seed=1)
    fit0, _ = gr.run(g0, E6.TRAIN)
    graph = gr.graph
    held = E6.HELD64[8:16]                                  # same shape as TRAIN, different seeds
    fit1, cells1 = gr.run(g1, held)
    assert gr.graph is graph                                # no re-capture: the reload path was exercised
    ref_fit, ref_cells = e7_ref(g7, g1, held)
    assert (fit1 == ref_fit).sum() == P and (cells1 == ref_cells).sum() == P
    assert (fit1 != fit0).sum() >= P // 2                   # a stale replay of g0 would fail here


def test_brain_cheat_recaptures_and_moves_the_result(g7):
    g = genomes(g7, P, seed=0)
    gr = GraphRollout(g7, "cuda")
    gr.run(g, E6.TRAIN)
    fit_c, cells_c = gr.run(g, E6.TRAIN, cheat=True)
    ref_fit, ref_cells = e7_ref(g7, g, E6.TRAIN, cheat=True)
    assert (fit_c == ref_fit).sum() == P and (cells_c == ref_cells).sum() == P
    honest_fit, honest_cells = e7_ref(g7, g, E6.TRAIN)
    assert ((fit_c != honest_fit) | (cells_c != honest_cells)).sum() >= P // 2
