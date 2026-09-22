"""Campaign 0 controls (PREREG_C0 section 8). Must pass before any result is read."""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import assay as A  # noqa: E402
import worlds as W  # noqa: E402


def test_t_distribution_against_known_values():
    assert abs(A.t_cdf(0.0, 10) - 0.5) < 1e-9
    assert abs(A.t_cdf(2.228, 10) - 0.975) < 1e-3      # t(0.975, 10) = 2.228
    assert abs(A.t_ppf(0.975, 30) - 2.042) < 1e-3
    assert abs(A.t_cdf(-1.697, 30) - 0.05) < 1e-3


def test_holm_is_monotone_and_bounded():
    adj = A.holm({"a": 0.01, "b": 0.02, "c": 0.5})
    assert adj["a"] == 0.03 and adj["b"] == 0.04 and adj["c"] == 0.5


def test_positive_control_huge_transfer_always_flagged():
    w = W.mde_world(2.0)
    hits = sum(A.analyse(W.simulate(w, 16, random.Random(i)))["flags"] == {"TRANSFER"} for i in range(50))
    assert hits >= 48


def test_negative_control_null_rarely_flags_at_64():
    hits = sum(not A.analyse(W.simulate(W.WORLDS["W6"], 64, random.Random(100 + i)))["flags"] for i in range(50))
    assert hits >= 45


def test_cheat_control_pseudoreplication_inflates_false_positives():
    # AMENDMENT 1: on the heterogeneous null W9, where pseudoreplication can bite
    lin = pse = 0
    for i in range(60):
        obs = W.simulate(W.WORLDS["W9"], 16, random.Random(500 + i))
        lin += bool(A.analyse(obs)["flags"])
        pse += bool(A.analyse(obs, method="pseudo")["flags"])
    assert pse > lin


def test_meter_honest_never_flags_cheater_always_does():
    for i in range(20):
        honest = A.analyse(W.simulate(W.WORLDS["W1"], 16, random.Random(900 + i)))
        assert "COMPUTE" not in honest["flags"] and honest["meter_lo"] < 1.05
        cheat = W.simulate(W.WORLDS["W3"], 16, random.Random(950 + i))
        assert A.analyse(cheat)["meter_lo"] > 1.05


def test_analysis_never_sees_the_world_table():
    import inspect
    src = inspect.getsource(A)
    assert "WORLDS" not in src and "kappa" not in src
