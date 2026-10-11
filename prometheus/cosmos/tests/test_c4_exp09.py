"""H-SPREAD predictor sanity (synthetic knobs only): reduces to ring return without diffusion or jitter."""
from prometheus.cosmos.c4.exp05 import R
from prometheus.cosmos.c4.exp09 import spread_score


def test_spread_reduces_to_return_when_noise_free():
    for k in range(1, 30):
        s = spread_score(0.0, 0.0, 2, 0.0, k)
        assert (s > 0.5) == bool(R(2, k, 16))


def test_v0_sensor_keeps_the_cue_and_decay_shrinks_it():
    assert spread_score(0.0, 0.0, 0, 0.0, 10) == 1.0
    assert spread_score(0.2, 0.0, 0, 0.0, 10) < spread_score(0.1, 0.0, 0, 0.0, 10)
