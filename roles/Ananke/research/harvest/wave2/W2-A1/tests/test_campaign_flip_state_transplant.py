"""W2-A1 regression test for patches/campaign_flip_transplant_noop.diff.

campaign.flip_state_transplant builds donor and recipient from the same seeds, genome and schedule, so
they are bit-identical at the boundary and assays.transplant_state ALWAYS raises
RuntimeError('NOT_APPLICABLE: ...'). That exception escapes transplant_battery and run_cell, so any FLIP
adjudication cell would FAIL (and count toward PARK). C1 never adjudicated a FLIP cell (0 FLIP SIGNAL),
so no recorded row is affected. FAILS on current code, PASSES with the patch.
Package root: env W2A1_PKG_ROOT (default: the worktree)."""
from __future__ import annotations

import os
import pathlib
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
WT = pathlib.Path(__file__).resolve().parents[7]
PKG = pathlib.Path(os.environ.get("W2A1_PKG_ROOT", str(WT)))
if not PKG.is_absolute():
    PKG = WT / PKG
sys.path.insert(0, str(PKG))

import torch  # noqa: E402

torch.set_num_threads(2)

from prometheus.ananke import campaign, envs, plants, search  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402

PH = Physics(topology="ring", n_sites=16, radius=1, dest_mode="all", prog_len=12)
ENV = envs.EnvSpec(family="FLIP", d=1, delta=4, trials=8, block=2)
SPEC = {"search_seed": 4242, "search": search.SearchSpec(M_held=8).to_dict()}


def test_flip_state_transplant_does_not_crash():
    out = campaign.flip_state_transplant(PH, plants.plant("relay_flood", PH), ENV, SPEC, "cpu")
    assert out.get("status") == "NOT_APPLICABLE"
    assert "transplanted" not in out          # a no-op must not be reported as an accuracy


def test_flip_transplant_battery_completes():
    res = campaign.transplant_battery(PH, plants.plant("relay_flood", PH), ENV, SPEC, "cpu")
    assert res["state_transplant"]["status"] == "NOT_APPLICABLE"
    assert all(v["status"] in ("RAN", "NOT_APPLICABLE") for k, v in res.items() if k != "state_transplant")
