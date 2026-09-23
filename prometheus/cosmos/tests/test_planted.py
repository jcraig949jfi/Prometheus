"""Planted-truth qualification of the miner (G3 artifact resistance + recovery + no-null pathology).

Each scenario runs the full pipeline: native runs -> certificate -> lineage audit -> mining.
Recovery is judged FUNCTIONALLY (agreement with the planted rule on a fresh dense grid),
because equivalent symbolic forms are not identifiable from finite data.
"""
import itertools

import numpy as np
import pytest

from prometheus.cosmos.independence import lineages
from prometheus.cosmos.miner import law_from_json
from prometheus.cosmos.pipeline import Chamber, mine_rows
from prometheus.cosmos.planted import pa, pb, pc, ps1, ps2

N_PER_FAMILY = 90
WORKERS = 8


def _collect(fams, n=N_PER_FAMILY, seed=0):
    ch = Chamber(fams, episodes=300, campaign="planted")
    rng = np.random.default_rng(seed)
    for f in fams:
        sp = f.space()
        for _ in range(n):
            p = {k: v[rng.integers(len(v))] for k, v in sp.items()}
            ch.observe(f.name, p)
    return ch


def _grid():
    C = np.geomspace(0.02, 1.2, 40)
    N = np.linspace(0, 1.5, 16)
    K = np.array([0, 1, 2, 4, 8])
    G = np.array([0.5, 0.9375])
    pts = np.array(list(itertools.product(C, N, K, G)))
    return {"C": pts[:, 0], "N": pts[:, 1], "K": pts[:, 2], "G": pts[:, 3]}


def _agreement(res, truth):
    L = law_from_json(res["law"])
    X = _grid()
    return float((L.predict(X) == truth(X)).mean())


def test_lineage_audit_merges_shared_code_and_separates_independent():
    lin = lineages({f.name: f.lineage for f in (pa.Planted("shared"), pb.Planted("shared"),
                                                 ps1.Planted(), ps2.Planted())})
    assert lin["ps1:shared"] == lin["ps2:shared"]
    assert len({lin["pa:shared"], lin["pb:shared"], lin["ps1:shared"]}) == 3


def test_visible_substrates_are_three_independent_lineages():
    from prometheus.cosmos.substrates import visible
    fams = visible()
    lin = lineages({n: f.lineage for n, f in fams.items()})
    assert len(set(lin.values())) == 3


@pytest.mark.slow
def test_positive_planted_invariant_recovered():
    res = mine_rows(_collect([m.Planted("positive") for m in (pa, pb, pc)]).rows, workers=WORKERS)
    assert res["verdict"] == "CANDIDATE", res
    assert _agreement(res, lambda X: X["C"] <= 0.30) >= 0.95


@pytest.mark.slow
def test_interaction_boundary_recovered():
    res = mine_rows(_collect([m.Planted("interaction") for m in (pa, pb, pc)], seed=1).rows, workers=WORKERS)
    assert res["verdict"] == "CANDIDATE", res
    assert _agreement(res, lambda X: X["C"] * X["K"] >= 0.5) >= 0.93


@pytest.mark.slow
def test_substrate_artifact_not_promoted():
    res = mine_rows(_collect([m.Planted("artifact") for m in (pa, pb, pc)], seed=2).rows, workers=WORKERS)
    if res["verdict"] == "CANDIDATE":
        assert "N" not in res["law"]["law"].replace("exp(-", "")[:0] + "".join(
            ch for ch in res["law"]["law"] if ch.isalpha() and ch in "CNKG"), res["law"]
        assert _agreement(res, lambda X: X["C"] <= 0.30) >= 0.90


@pytest.mark.slow
def test_broken_universality_returns_none():
    res = mine_rows(_collect([m.Planted("broken") for m in (pa, pb, pc)], seed=3).rows, workers=WORKERS)
    assert res["verdict"] == "NONE", res.get("law")


@pytest.mark.slow
def test_null_world_returns_none():
    res = mine_rows(_collect([m.Planted("null") for m in (pa, pb, pc)], seed=4).rows, workers=WORKERS)
    assert res["verdict"] == "NONE", res.get("law")


@pytest.mark.slow
def test_shared_code_artifact_is_not_universal():
    """ps1+ps2 share a helper that plants N <= 0.4; pa is independent with C <= 0.3.
    Two lineages only: the engine must refuse a universal verdict."""
    fams = [ps1.Planted(), ps2.Planted(), pa.Planted("shared")]
    res = mine_rows(_collect(fams, seed=5).rows, workers=WORKERS)
    assert res["n_lineages"] == 2
    assert res["verdict"] in ("NONE", "INSUFFICIENT_INDEPENDENCE"), res
