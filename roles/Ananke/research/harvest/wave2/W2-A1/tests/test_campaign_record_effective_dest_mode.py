"""W2-A1 regression test for patches/campaign_record_effective_dest_mode.diff (H-IMPL H7a).

FAILS on current code (recorded levels say dest_mode "all" on global cells that ran "sample"),
PASSES with the patch. The neutrality tests pass on both: physics, cell ids and seeds are unchanged.
Package root: env W2A1_PKG_ROOT (default: the worktree). Patched copy: scratch/patched.
    CUDA_VISIBLE_DEVICES=-1 python -m pytest -q roles/Ananke/research/harvest/wave2/W2-A1/tests/test_campaign_record_effective_dest_mode.py
    W2A1_PKG_ROOT=roles/Ananke/research/harvest/wave2/W2-A1/scratch/patched CUDA_VISIBLE_DEVICES=-1 python -m pytest -q ...
"""
from __future__ import annotations

import copy
import os
import pathlib
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
WT = pathlib.Path(__file__).resolve().parents[7]
PKG = pathlib.Path(os.environ.get("W2A1_PKG_ROOT", str(WT)))
if not PKG.is_absolute():
    PKG = WT / PKG
sys.path.insert(0, str(PKG))

from prometheus.ananke import campaign  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402

CFG = campaign.CampaignConfig(a0_cells=300)


def _specs():
    return campaign.wave_A0(CFG)


def test_package_under_test():
    assert pathlib.Path(campaign.__file__).resolve().is_relative_to(PKG.resolve())


def test_recorded_levels_match_executed_physics():
    specs = _specs()
    glob = [s for s in specs if s["physics"]["topology"] == "global"]
    assert glob, "no global cell drawn: test is vacuous"
    assert any(True for _ in glob)
    bad = [s for s in specs for k, v in s["levels"].items()
           if k in s["physics"] and s["physics"][k] != v]
    assert not bad, f"{len(bad)} specs record a level that did not run (e.g. dest_mode on global)"


def test_neutral_physics_and_ids_unchanged():
    """The patch only rewrites the RECORD: the executed physics equals the pre-patch rule
    (global -> sample) applied to the drawn levels, and cell_id does not hash levels."""
    for s in _specs():
        lv = copy.deepcopy(s["levels"])
        kw = {k: v for k, v in lv.items() if k != "economy"}
        kw.update(campaign.ECONOMY[lv["economy"]])
        if kw["topology"] == "global":
            kw["dest_mode"] = "sample"
        ref = Physics(**kw, topo_seed=s["physics"]["topo_seed"]).to_dict()
        assert ref == s["physics"]
        s2 = dict(s, levels={**s["levels"], "dest_mode": "all"})
        assert campaign.cell_id(s) == campaign.cell_id(s2)


def test_transect_level_index_and_seeds_unchanged():
    """A dest_mode transect at a global base keeps one spec per level index with the same seeds."""
    base_lv = campaign.draw_levels(1, campaign.DIALS)
    base_lv.update(topology="global", dest_mode="all")
    ph = campaign.physics_from_levels(dict(base_lv), topo_seed=5)
    base = {"levels": base_lv, "env_levels": {"d": 1, "delta": 4, "gap": 4, "block": 2},
            "physics": ph.to_dict(), "cell_id": "x"}
    sp = campaign._transect_specs(CFG, "RELAY", base, 0, "dest_mode", "phys", "census", {}, 1)
    assert [s["extra"]["level_index"] for s in sp] == [0, 1]
    assert all(s["physics"]["dest_mode"] == "sample" for s in sp)
