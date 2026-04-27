"""Test TOOL_TT_SPLICE."""
import sys, os
import warnings

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.tt_splice import PATTERN_WARNING, tt_splice_compatibility


def _save_npz(path, data):
    np.savez(path, data=np.asarray(data, dtype=np.float64))
    return path


def test_shared_low_rank_factor_scores_high(tmp_path):
    rng = np.random.default_rng(11)
    shared = rng.normal(size=(6, 5))
    left_a = rng.normal(size=18)
    left_b = rng.normal(size=18)
    a = left_a[:, None, None] * shared[None, :, :]
    b = left_b[:, None, None] * shared[None, :, :]
    a += 0.01 * rng.normal(size=a.shape)
    b += 0.01 * rng.normal(size=b.shape)

    pa = _save_npz(tmp_path / "a.npz", a)
    pb = _save_npz(tmp_path / "b.npz", b)
    result = tt_splice_compatibility(pa, pb, null_perms=25, seed=7)

    assert 0.0 <= result["compatibility_score"] <= 1.0
    assert result["compatibility_score"] > 0.7
    assert "LOW_RANK_SHARED_FACTOR" in result["bridge_operators"]
    assert result["audit"]["null_perms_run"] == 25


def test_random_gaussian_scores_low_with_non_significant_null(tmp_path):
    rng = np.random.default_rng(2026)
    a = rng.normal(size=(24, 7, 5))
    b = rng.normal(size=(24, 7, 5))

    pa = _save_npz(tmp_path / "rand_a.npz", a)
    pb = _save_npz(tmp_path / "rand_b.npz", b)
    result = tt_splice_compatibility(pa, pb, null_perms=40, seed=17)

    assert result["compatibility_score"] < 0.35
    assert result["audit"]["null_p_value"] > 0.05


def test_self_splice_is_perfect(tmp_path):
    rng = np.random.default_rng(3)
    a = rng.normal(size=(16, 5, 4))
    pa = _save_npz(tmp_path / "self.npz", a)

    result = tt_splice_compatibility(pa, pa, null_perms=10, seed=1)

    assert result["compatibility_score"] == pytest.approx(1.0)
    assert "IDENTITY_SELF_SPLICE" in result["bridge_operators"]


def test_audit_fields_and_prime_warning(tmp_path):
    rng = np.random.default_rng(4)
    a = rng.normal(size=(14, 4, 3))
    b = rng.normal(size=(14, 4, 3))
    pa = _save_npz(tmp_path / "a.npz", a)
    pb = _save_npz(tmp_path / "b.npz", b)

    with warnings.catch_warnings(record=True) as seen:
        warnings.simplefilter("always")
        result = tt_splice_compatibility(pa, pb, prime_detrend=False, null_perms=3)

    assert any(PATTERN_WARNING in str(w.message) for w in seen)
    audit = result["audit"]
    assert audit["prime_detrend_applied"] is False
    assert set(audit["pre_detrend_magnitudes"]) == {"region_a", "region_b"}
    assert set(audit["post_detrend_magnitudes"]) == {"region_a", "region_b"}
    assert audit["null_seed"] == 20260417
    assert "null_p_value" in audit


def test_determinism_same_seed_same_bond_ranks(tmp_path):
    rng = np.random.default_rng(5)
    a = rng.normal(size=(18, 5, 4))
    b = rng.normal(size=(18, 5, 4))
    pa = _save_npz(tmp_path / "a.npz", a)
    pb = _save_npz(tmp_path / "b.npz", b)

    r1 = tt_splice_compatibility(pa, pb, null_perms=12, seed=99)
    r2 = tt_splice_compatibility(pa, pb, null_perms=12, seed=99)

    assert r1["bond_ranks"] == r2["bond_ranks"]
    assert r1["compatibility_score"] == pytest.approx(r2["compatibility_score"])
    assert r1["audit"]["null_p_value"] == pytest.approx(r2["audit"]["null_p_value"])


def test_ergon_tensor_npz_smoke_schema_documented():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'ergon', 'tensor.npz'))
    if not os.path.exists(path):
        pytest.skip("ergon/tensor.npz not present in this checkout")

    with np.load(path, allow_pickle=False) as data:
        assert "data" in data.files
        shape = data["data"].shape

    if len(shape) != 2:
        pytest.skip(f"ergon/tensor.npz schema not supported by smoke test: shape={shape}")
    pytest.skip(
        "ergon/tensor.npz is a large object-feature matrix, not a per-region tensor pair; "
        "self-splice should be run on extracted per-region slices to avoid materializing the full matrix."
    )


if __name__ == '__main__':
    pytest.main([__file__])
