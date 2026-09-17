"""W2 harness: the exactness gate passes on honest kernels and fails on a planted world cheat,
at sizes on both sides of the numba-log threshold. No timing claim is tested."""
from __future__ import annotations

import pytest

wp = pytest.importorskip("warp")

from primordial.nv.warp import crossover  # noqa: E402

wp.init()
DEVS = tuple(d.alias for d in wp.get_devices())


@pytest.mark.parametrize("n", [1, 7, crossover.NUMBA_LOG_MAX + 3])
def test_gate_passes_on_honest_forms(n):
    row = crossover.bench_cell(g=4, n=n, reps=1, devices=DEVS)
    assert row["gate_ok"], row["gate"]
    assert set(row["median_s"]) >= {"numba", "warp_cpu"}
    assert ("charge_eq_numba" in row["gate"]) == (n <= crossover.NUMBA_LOG_MAX)


def test_gate_fails_on_skip_lin_warp():
    row = crossover.bench_cell(g=4, n=64, reps=1, warp_cheat="skip_lin", devices=DEVS)
    assert not row["gate_ok"]


def test_reset_reproduces_the_episode():
    from primordial.nv.warp.world import WpEncounter
    from primordial.soup.b1.common import action_tensor, episode_seeds, make_world
    mech, wid = make_world(2)
    w = WpEncounter(mech, wid, device="cpu")
    w.prepare(episode_seeds(9, base=7002))
    w.load_actions(action_tensor(mech, 9, seed=2))
    w.run()
    first = (w.final_charge().copy(), w.done_tick.numpy().copy())
    w.reset()
    w.run()
    assert (w.final_charge() == first[0]).all() and (w.done_tick.numpy() == first[1]).all()
