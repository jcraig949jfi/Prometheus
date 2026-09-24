import copy
import numpy as np

from ensorain.wtp2.world2 import run_life, streams, AC
from ensorain.wtp2.genome2 import candidate
from ensorain.wtp2.preflight import preflight, planted_panel
from ensorain.wtp2.detect2 import DETS, fires, refs_from


def _admitted():
    rng = np.random.default_rng(424_242)
    for i in range(20000):
        g = candidate(rng, [], [])
        ok, rec = preflight(g, 8_000_000 + i)
        if ok:
            return g, rec
    raise AssertionError("nothing admitted")


G, REC = _admitted()


def test_admitted_world_passes_every_gate_record():
    assert REC["gate"] == "ADMITTED" and REC["planted_r2"] >= 0.10 and REC["shuffled_r2"] <= 0.05
    assert max(REC["n2_U"]) < 0 and REC["oracle_U"] > 0 and G["resource"]["calibrated"]
    assert REC["n_floats"] <= 0.25 * REC["cells"] + 1


def test_streams_are_named_and_deterministic():
    a, sa = streams(5)
    b, sb = streams(5)
    assert sa == sb and set(a) >= {"world_gen", "world_dyn", "noise", "policy", "learner", "transplant", "controls"}
    assert a["noise"].random() == b["noise"].random()


def test_metric_uses_fixed_reference():
    y = np.array([1.0, -1.0, 2.0])
    assert AC(y, y, 1.0) == 6.0
    assert abs(AC(np.zeros(3), y, 2.0) - (-np.log10(2.0 / 2.0))) < 1e-9


def test_collapse_is_degenerate_not_scored():
    g = copy.deepcopy(G)
    g["transition"]["catastrophe_rate"] = 1.0
    assert run_life(g, 3)["status"] == "DEGENERATE"


def test_twins_share_environment_and_detectors_run():
    u = {tw or "real": run_life(G, 4, **({"twin": tw} if tw else {})) for tw in (None, "shuffled", "frozen", "random")}
    refs = refs_from([u])
    for d in DETS:
        fires(d, u, refs)
    a = run_life(G, 4)
    assert a["event_digest"] == u["real"]["event_digest"]


def test_planted_panel_sees_structure_not_noise():
    rng = np.random.default_rng(0)
    x = np.einsum("a,b,c->abc", rng.normal(size=8), rng.normal(size=8), rng.normal(size=8))
    real, _ = planted_panel(x, 128, 256, 0.0, rng)
    fake, _ = planted_panel(rng.permutation(x.reshape(-1)).reshape(x.shape), 128, 256, 0.0, rng)
    assert real > 0.5 and fake < 0.2
