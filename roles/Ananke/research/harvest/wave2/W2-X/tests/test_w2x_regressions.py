"""W2-X regression tests for patches/w2x_levels_leak_and_reading3_degenerate.diff.
Run against a package root on PYTHONPATH (scratch/post = current HEAD code; scratch/fix = patched):
    CUDA_VISIBLE_DEVICES=-1 PYTHONPATH=scratch/post python -m pytest -q tests/test_w2x_regressions.py   # 2 FAIL
    CUDA_VISIBLE_DEVICES=-1 PYTHONPATH=scratch/fix  python -m pytest -q tests/test_w2x_regressions.py   # all PASS
"""
import os
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
import math

import numpy as np

from prometheus.ananke import campaign as C
from prometheus.ananke import inference


def _global_base(dest="all"):
    lv = C.draw_levels(1, C.DIALS)
    lv.update(topology="global", dest_mode=dest)
    ph = C.physics_from_levels(lv, topo_seed=5)       # as _draw_cell / wave_A store it: no copy
    return {"levels": lv, "env_levels": {"d": 1, "delta": 4, "gap": 4, "block": 2},
            "physics": ph.to_dict(), "cell_id": "x"}


def test_topology_transect_from_global_base_runs_the_drawn_dest_mode():
    """dc46fd00f writes the forced 'sample' into the base's levels; _transect_specs re-derives physics
    from those levels, so torus/ring/random/smallworld members silently ran 'sample' (new cell ids)."""
    sp = C._transect_specs(C.CampaignConfig(), "RELAY", _global_base("all"), 0, "topology", "phys", "census", {}, 1)
    ran = {s["physics"]["topology"]: s["physics"]["dest_mode"] for s in sp}
    assert ran["global"] == "sample"
    assert all(ran[t] == "all" for t in ("torus", "ring", "random", "smallworld")), ran


def test_global_record_still_says_what_ran():
    b = _global_base("all")
    assert b["levels"]["dest_mode"] == "sample" == b["physics"]["dest_mode"]


def test_zero_variance_reading_is_not_certified():
    """A forced control gives exactly .5 in every pair (W2-B P1/P5). reading3 must not certify it."""
    r = inference.reading3(np.full(32, 0.5), 0.60, "<=", "hi")
    assert r["status"] not in ("TRUE", "FALSE"), r
    assert not (isinstance(r["keep"], float) and r["keep"] == 1.0 and math.isinf(r["d_se"]))


def test_kill_eligible_refuses_degenerate_normal():
    assert not inference.kill_eligible(np.full(32, 0.9))
