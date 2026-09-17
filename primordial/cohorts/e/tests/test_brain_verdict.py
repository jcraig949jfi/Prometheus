"""C1: brain_verdict is THE brain oracle for a verdict; skip-odd raises."""
import numpy as np
import pytest

from primordial.cohorts.e import oracles as O
from primordial.qd import e7_run as E7


def _elites(P=4, seed=0):
    g7 = E7.G7(4, "linear")
    return g7, g7.init(np.random.default_rng(seed), P)


@pytest.mark.parametrize("cheat", ["skip_odd", "skip-odd", "", "ablate_top"])
def test_any_cheat_but_powered_raises(cheat):
    g7, g = _elites(P=1)
    with pytest.raises(ValueError, match="cannot back a verdict"):
        O.brain_verdict(g7, g, E7.HELD8[:1], cheat=cheat)


def _fake(honest_mm=0, shift=16, ablate=14, P=16):
    return {"elites": P, "input_invariant_elites": 0, "ablate_top_features": [],
            "honest": {"elites_caught": 0, "mismatched_rows": honest_mm, "clear_rows": 100},
            "skip_odd": {"elites_caught": 0, "mismatched_rows": 0, "clear_rows": 100},
            "ablate_top": {"elites_caught": ablate, "mismatched_rows": ablate, "clear_rows": 50},
            "shift_action": {"elites_caught": shift, "mismatched_rows": 100, "clear_rows": 100}}


@pytest.mark.parametrize("kw,clean", [({}, True), ({"ablate": 16}, True), ({"ablate": 13}, False),
                                      ({"honest_mm": 1}, False), ({"shift": 15}, False),
                                      ({"P": 4, "shift": 4, "ablate": 4}, True),
                                      ({"P": 4, "shift": 4, "ablate": 3}, False)])
def test_powered_rule(monkeypatch, kw, clean):
    monkeypatch.setattr(O, "brain_oracle_cheats", lambda *a, **k: _fake(**kw))
    g7, g = _elites(P=1)
    assert O.brain_verdict(g7, g, E7.HELD8[:1])["clean"] is clean


def test_input_invariant_elites_are_not_clean():
    # W = 0: every action is the bias argmax, no single-feature ablation moves it -> never "caught"
    g7, (p, C) = _elites(P=4, seed=2)
    W, b = p
    W[:] = 0.0
    v = O.brain_verdict(g7, ((W, b), C), E7.HELD8[:2], rows_per_elite=32)
    assert not v["clean"] and v["cheats"]["input_invariant_elites"] == 4
    assert v["cheats"]["shift_action"]["elites_caught"] == 4 and v["cheats"]["honest"]["mismatched_rows"] == 0
