"""W3: E's world oracle (brain-recorded and open-loop actions) on the Warp kernel; skip_lin caught."""
from __future__ import annotations

import pytest

wp = pytest.importorskip("warp")
pytest.importorskip("redis")                       # lane E modules import redis at module level

from primordial.nv.warp import replay  # noqa: E402

wp.init()
DEVS = [d.alias for d in wp.get_devices()]


@pytest.mark.parametrize("device", DEVS)
@pytest.mark.parametrize("source", ["e7:linear", "e4", "abstain"])
def test_recorded_actions_replay_exact(source, device):
    row = replay.run_cell(source, gen_seed=4, P=4, device=device)
    assert row["genomes_failing"] == 0
    assert row["episodes_hash_mismatch_wforge"] == row["episodes_hash_mismatch_e_world"] == 0


def test_abstain_floor_runs_long_episodes():
    """The floor policy spends no action charge, so its episodes outlive random actions: a length regime
    W1/W2's random episodes (~20-27 ticks) never exercised."""
    row = replay.run_cell("abstain", gen_seed=4, P=1, device="cpu")
    assert row["mean_episode_ticks"] > 27


def test_skip_lin_fails_brain_recorded_replay():
    row = replay.run_cell("e7:linear", gen_seed=4, P=4, device="cpu", cheat="skip_lin")
    assert row["genomes_failing"] == 4 and row["episodes_hash_mismatch_wforge"] > 0
