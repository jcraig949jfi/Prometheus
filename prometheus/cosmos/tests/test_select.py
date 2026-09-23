"""Exercise location-aware selection end to end (the quick campaign cannot reach it: its null is too small)."""
import numpy as np

from prometheus.cosmos.campaign0 import build_pools
from prometheus.cosmos.miner import _ser
from prometheus.cosmos.pipeline import Chamber
from prometheus.cosmos.select import candidates, select
from prometheus.cosmos.stress import pool_rows
from prometheus.cosmos.substrates import visible


import pytest


@pytest.mark.slow
def test_select_prefers_the_well_located_ceiling():
    fams = visible()
    pools = pool_rows(fams, build_pools(fams, 300, 7))
    ch = Chamber(list(fams.values()), campaign="t")
    rng = np.random.default_rng(0)
    for f, P in pools.items():
        for i in rng.choice(len(P), 120, replace=False):
            ch.observe(f, P[i]["params"])
    V = lambda n: ("var", n)
    good = [[_ser(("sub", ("mul", V("G"), ("dec", V("N"))), V("C"))), -1.0], [_ser(("mul", V("C"), V("K"))), -1.0]]
    bad = [[_ser(("var", "C")), 1.0], [_ser(("mul", V("C"), V("K"))), -1.0]]          # ceiling ignores G and N
    mined = {"v3": {"p_null": 0.05, "top": [
        {"atoms": bad, "structure": "bad", "score": 0.90, "fold_ba": {}, "passes_worst_gate": True},
        {"atoms": good, "structure": "good", "score": 0.89, "fold_ba": {}, "passes_worst_gate": True}]}}
    cands = candidates(mined, ["v3", "v4"])
    assert len(cands) == 2
    sel = select(cands, ch.rows, fams, pools, np.random.default_rng(1), n_bases=4, episodes=400)
    assert sel["chosen"]["structure"] == "good", [(s["structure"], s["worst_offset"]) for s in sel["scored"]]
    assert len(sel["scored"]) == 2 and sel["chosen"]["law"]["atoms"]
