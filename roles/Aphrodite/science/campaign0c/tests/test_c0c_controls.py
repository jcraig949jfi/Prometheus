"""Campaign 0C controls: truth computation, procedure behaviour, independence of stages."""
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import secondary as S  # noqa: E402


def test_true_effect_matches_monte_carlo():
    rng = random.Random(1)
    v, shift = 0.1, 1.0
    n = 200000
    acc = 0.0
    for _ in range(n):
        u = rng.gauss(0, S.SD_U)
        x8 = S.B0 + u + v + shift + rng.gauss(0, S.SD_W) + rng.gauss(0, S.SD_E)
        x0 = S.B0 + u + v + rng.gauss(0, S.SD_E)
        acc += 1 / (1 + math.exp(-x8)) - 1 / (1 + math.exp(-x0))
    assert abs(acc / n - S.true_effect(v, shift)) < 0.003


def test_positive_control_strong_common_discovery_is_found():
    w = S.World("pos", "G", 0.5, 3.0)
    hits = sum(S.procedure(S.simulate(w, 32, random.Random(i)))["discovery"] for i in range(30))
    assert hits >= 29


def test_negative_control_null_rarely_discovers():
    w = S.World("N0", "N0")
    hits = sum(S.procedure(S.simulate(w, 64, random.Random(100 + i)))["discovery"] for i in range(100))
    assert hits <= 3


def test_cheat_control_screen_gamers_are_nominated_but_not_confirmed():
    w = S.World("AS", "AS", 0.2, 2.0)
    nominated_gamers = confirmed_gamers = 0
    for i in range(30):
        lins = S.simulate(w, 64, random.Random(300 + i))
        r = S.procedure(lins)
        gam = {j for j, l in enumerate(lins) if l["truth"]["planted"]}
        nominated_gamers += len(gam & set(r["nominated"]))
        confirmed_gamers += len(gam & set(r["confirmed"]))
    assert nominated_gamers > 50       # the screen sees them (the channel can observe the cheat)
    assert confirmed_gamers <= 2       # fresh confirmation rejects them


def test_screen_width_is_quarter_of_L():
    for L in (32, 64):
        r = S.procedure(S.simulate(S.World("N0", "N0"), L, random.Random(7)))
        assert r["k"] == math.ceil(0.25 * L) and len(r["nominated"]) <= r["k"]
