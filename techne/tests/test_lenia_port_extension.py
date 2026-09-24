"""Port extension 2026-09-18 (Harmonia operator-review item (b)): kn 1-4, gn 1-3, fractional rings.
Positive: every core constructs a finite, normalised kernel and steps. Cheat: an unsupported core is
REFUSED by name (never silently mapped to another). Regression: Orbium's kernel is byte-identical to
the pre-extension construction (the seven-arm receipt depends on it)."""
from __future__ import annotations

import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "techne107_asal_observer.py"
spec = importlib.util.spec_from_file_location("port", _p)
port = importlib.util.module_from_spec(spec); spec.loader.exec_module(port)

ORB = {"R": 13, "T": 10, "b": "1", "m": 0.15, "s": 0.015, "kn": 1, "gn": 1}


@pytest.mark.parametrize("kn", [1, 2, 3, 4])
@pytest.mark.parametrize("gn", [1, 2, 3])
@pytest.mark.parametrize("b", ["1", "1/2,1", "1,1/3", "3/4,1,1"])
def test_every_core_and_ring_constructs_and_steps(kn, gn, b):
    sim = port.Lenia2D(64, {**ORB, "kn": kn, "gn": gn, "b": b})
    assert np.isfinite(sim.kernel).all() and abs(sim.kernel.sum() - 1.0) < 1e-9
    A = sim.step(np.random.default_rng(0).random((64, 64)))
    assert A.shape == (64, 64) and np.isfinite(A).all() and A.min() >= 0 and A.max() <= 1


def test_parse_rings_matches_reference_fractions():
    assert np.allclose(port.parse_rings("1/2,1"), [0.5, 1.0])
    assert np.allclose(port.parse_rings("3/4,1,1"), [0.75, 1.0, 1.0])
    assert np.allclose(port.parse_rings(["1", "1/3"]), [1.0, 1 / 3])


def test_cheat_unsupported_core_is_refused_by_name():
    with pytest.raises(ValueError, match="unsupported kn=5"):
        port.Lenia2D(64, {**ORB, "kn": 5})
    with pytest.raises(ValueError, match="gn=4"):
        port.Lenia2D(64, {**ORB, "gn": 4})


def test_orbium_kernel_unchanged_by_the_extension():
    """The pre-extension construction, inlined: quad4 core, single ring, R=13."""
    size, R = 128, 13
    mid = size // 2
    y, x = np.mgrid[0:size, 0:size]
    D = np.sqrt(((x - mid) / R) ** 2 + ((y - mid) / R) ** 2)
    with np.errstate(divide="ignore", invalid="ignore"):
        K = (D < 1) * np.nan_to_num((4 * np.minimum(D % 1, 1) * (1 - np.minimum(D % 1, 1))) ** 4) * 1.0
    K = K / K.sum()
    sim = port.Lenia2D(size, ORB)
    assert np.array_equal(sim.kernel, K)
