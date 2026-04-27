"""Test TAIL_VS_BULK_DECOMPOSITION."""
import sys, os

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.tail_vs_bulk import decompose_spectral


def _promotes(scores):
    return "PROMOTE_SEGMENT_SIGNAL" in scores["pattern_flags"]


def test_strong_tail_flat_bulk_low_agreement():
    signal = np.zeros(100)
    signal[95:] = 8.0

    result = decompose_spectral(signal, n_perms=50, seed=1)

    assert _promotes(result["tail_battery_scores"])
    assert not _promotes(result["bulk_battery_scores"])
    assert result["agreement_score"] == 0.0
    assert result["audit"]["tail_fraction"] == pytest.approx(0.05)


def test_strong_bulk_flat_tail_low_agreement():
    signal = np.zeros(100)
    signal[:95] = 5.0

    result = decompose_spectral(signal, n_perms=50, seed=2)

    assert not _promotes(result["tail_battery_scores"])
    assert _promotes(result["bulk_battery_scores"])
    assert result["agreement_score"] == 0.0
    assert result["audit"]["bulk_fraction"] == pytest.approx(0.95)


def test_tail_and_bulk_strong_high_agreement():
    signal = np.full(100, 5.0)
    signal[95:] = 5.2

    result = decompose_spectral(signal, n_perms=50, seed=3)

    assert _promotes(result["tail_battery_scores"])
    assert _promotes(result["bulk_battery_scores"])
    assert result["agreement_score"] > 0.9


def test_pure_noise_batteries_fail():
    rng = np.random.default_rng(4)
    signal = rng.normal(0.0, 1.0, size=200)

    result = decompose_spectral(signal, n_perms=80, seed=4)

    assert not _promotes(result["tail_battery_scores"])
    assert not _promotes(result["bulk_battery_scores"])
    assert result["tail_battery_scores"]["p_value"] > 0.05
    assert result["bulk_battery_scores"]["p_value"] > 0.05


def test_determinism_same_seed_bit_identical():
    signal = np.linspace(-1.0, 1.0, 128)
    signal[110:] += 4.0

    r1 = decompose_spectral(signal, n_perms=40, seed=99)
    r2 = decompose_spectral(signal, n_perms=40, seed=99)

    assert np.array_equal(r1["tail_signal"], r2["tail_signal"])
    assert np.array_equal(r1["bulk_signal"], r2["bulk_signal"])
    assert r1["tail_battery_scores"] == r2["tail_battery_scores"]
    assert r1["bulk_battery_scores"] == r2["bulk_battery_scores"]
    assert r1["agreement_score"] == r2["agreement_score"]


def test_custom_battery_contract_is_used():
    calls = []

    def battery(signal, mask, rng, n_perms):
        calls.append(int(mask.sum()))
        return {"effect_size": 2.0, "p_value": 0.01, "pattern_flags": ["PROMOTE_SEGMENT_SIGNAL"]}

    result = decompose_spectral(np.arange(20), null_model=battery, n_perms=3)

    assert calls == [1, 19]
    assert result["agreement_score"] == pytest.approx(1.0)
    assert result["audit"]["battery_contract"].startswith("callable(")


if __name__ == '__main__':
    pytest.main([__file__])
