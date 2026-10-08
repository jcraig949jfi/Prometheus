import json
from pathlib import Path

import numpy as np

from prometheus.cosmos.c4.families.cosmos_phase import world as W

FAM = Path(W.__file__).parent


def test_selftest_all_pass():
    out = W.selftest()
    assert all(out.values()), out


def test_natural_in_ranges_and_declared():
    native = json.loads((FAM / "NATIVE.json").read_text())["parameters"]
    rng = np.random.default_rng(0)
    for _ in range(200):
        kn = W.sample_natural(rng)
        for f, v in kn.items():
            lo, hi = native[f]["range"]
            assert lo <= v <= hi, (f, v)
        W.build_world(**kn)
