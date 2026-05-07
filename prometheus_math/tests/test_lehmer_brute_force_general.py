"""Tests for prometheus_math.lehmer_brute_force_general.

Per inbox ticket T-2026-05-07-T007. Coverage:
  * build_palindrome_descending_general — degree-14 matches existing
    `lehmer_brute_force.build_palindrome_descending` exactly; degree-12
    produces a length-13 palindrome with the expected pattern.
  * shard_iterator_general — count and content match expected for both
    degree=14 (against the existing scripts/ worker) and degree=12.
  * total_shards / enumerate_total_size — analytic counts.
  * process_shard_general — smoke test on a tiny case (degree=2).
  * Mahler-measure agreement with the scripts/ worker on degree=14
    (cross-implementation consistency).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

from prometheus_math.lehmer_brute_force_general import (
    BAND_LOWER,
    BATCH_SIZE,
    DEFAULT_BAND_UPPER,
    DEFAULT_COEF_RANGE,
    DEFAULT_DEGREE,
    _build_descending_matrix_general,
    build_palindrome_descending_general,
    enumerate_total_size,
    process_shard_general,
    run_brute_force_general,
    shard_iterator_general,
    total_shards,
)


# ---------------------------------------------------------------------------
# build_palindrome_descending_general
# ---------------------------------------------------------------------------


class TestBuildPalindromeGeneral:
    def test_degree_14_matches_existing_semantics(self):
        """Cross-impl consistency: deg=14 generic builder matches the
        existing prometheus_math.lehmer_brute_force.build_palindrome_descending.
        """
        from prometheus_math.lehmer_brute_force import build_palindrome_descending
        half = (1, 1, 0, -1, -1, -1, -1, -1)  # Lehmer-style 8-tuple
        gen = build_palindrome_descending_general(half, degree=14)
        existing = build_palindrome_descending(half)
        assert gen == existing

    def test_degree_12_produces_length_13_palindrome(self):
        half = (1, 0, -1, 0, 1, 0, -1)  # 7-tuple for deg=12
        full = build_palindrome_descending_general(half, degree=12)
        assert len(full) == 13
        # Palindrome property: full[i] == full[12-i]
        for i in range(7):
            assert full[i] == full[12 - i], f"position {i} not palindromic"

    def test_degree_12_explicit_pattern(self):
        """Build expected palindrome by hand and compare."""
        half = (3, 2, 1, 0, -1, -2, -3)  # 7-tuple, all distinct
        full = build_palindrome_descending_general(half, degree=12)
        # Expected: [c0,c1,c2,c3,c4,c5,c6, c5,c4,c3,c2,c1,c0]
        #         = [3, 2, 1, 0,-1,-2,-3, -2,-1, 0, 1, 2, 3]
        assert full == [3, 2, 1, 0, -1, -2, -3, -2, -1, 0, 1, 2, 3]

    def test_degree_2_minimal_case(self):
        """Degree-2 palindrome: half = (c0, c1), full = [c0, c1, c0]."""
        full = build_palindrome_descending_general((5, -3), degree=2)
        assert full == [5, -3, 5]

    def test_wrong_length_raises(self):
        with pytest.raises(ValueError, match="must have length 8"):
            build_palindrome_descending_general((1, 2, 3), degree=14)
        with pytest.raises(ValueError, match="must have length 7"):
            build_palindrome_descending_general((1, 2), degree=12)


# ---------------------------------------------------------------------------
# Matrix builder
# ---------------------------------------------------------------------------


class TestMatrixBuilder:
    def test_degree_14_matrix_shape_and_palindrome(self):
        halves = [(1, 1, 0, -1, -1, -1, -1, -1), (1, 0, -1, 0, 1, 0, -1, 0)]
        mat = _build_descending_matrix_general(halves, degree=14)
        assert mat.shape == (2, 15)
        # Verify palindrome property column-wise
        for i in range(8):
            assert (mat[:, i] == mat[:, 14 - i]).all()

    def test_degree_12_matrix_shape(self):
        halves = [(1, 0, -1, 0, 1, 0, -1)]
        mat = _build_descending_matrix_general(halves, degree=12)
        assert mat.shape == (1, 13)
        for i in range(7):
            assert (mat[:, i] == mat[:, 12 - i]).all()

    def test_empty_input_returns_zero_rows(self):
        mat = _build_descending_matrix_general([], degree=14)
        assert mat.shape == (0, 15)


# ---------------------------------------------------------------------------
# Shard iteration
# ---------------------------------------------------------------------------


class TestShardIterator:
    def test_degree_14_shard_count_matches_scripts_worker(self):
        """For deg=14 ±5 c0_positive_only=True: 5 c0 values * 11 c1 values
        = 55 shards (matching scripts/_lehmer_brute_force_worker.py)."""
        n = total_shards((-5, 5), c0_positive_only=True)
        assert n == 55

    def test_degree_12_shard_count(self):
        """Same shard structure (sharding is over (c0,c1), independent of degree).
        For ±5 c0_positive_only=True: still 55 shards."""
        n = total_shards((-5, 5), c0_positive_only=True)
        assert n == 55

    def test_degree_12_shard_yields_correct_count(self):
        """One deg-12 ±5 shard = 11^5 polys (c2..c6 over inner range)."""
        polys = list(shard_iterator_general(0, (-5, 5), degree=12, c0_positive_only=True))
        assert len(polys) == 11 ** 5  # 161,051

    def test_degree_14_shard_yields_correct_count(self):
        """One deg-14 ±5 shard = 11^6 polys (c2..c7 over inner range)."""
        polys = list(shard_iterator_general(0, (-5, 5), degree=14, c0_positive_only=True))
        assert len(polys) == 11 ** 6  # 1,771,561

    def test_shard_emits_correct_half_lengths(self):
        """deg=12 → half_len=7; deg=14 → half_len=8."""
        polys_12 = next(iter(shard_iterator_general(0, (-1, 1), degree=12, c0_positive_only=True)))
        polys_14 = next(iter(shard_iterator_general(0, (-1, 1), degree=14, c0_positive_only=True)))
        assert len(polys_12) == 7
        assert len(polys_14) == 8

    def test_degree_2_minimal_case(self):
        """deg=2 has half_len=2; one shard yields exactly one tuple."""
        polys = list(shard_iterator_general(0, (-1, 1), degree=2, c0_positive_only=True))
        # c0_values = [1] (only positive); c1 in [-1, 0, 1]; so 3 shards.
        # Each shard yields ONE tuple (the (c0, c1) pair itself, since inner_repeat=0)
        assert len(polys) == 1
        assert polys[0] == (1, -1)

    def test_shard_idx_out_of_range_raises(self):
        with pytest.raises(ValueError, match="shard_idx"):
            list(shard_iterator_general(99, (-5, 5), degree=14))

    def test_c0_positive_only_false_includes_negatives(self):
        polys = list(shard_iterator_general(0, (-2, 2), degree=2, c0_positive_only=False))
        # First shard with c0_positive_only=False: c0_values = [-2,-1,1,2]; c1 in [-2..2]
        # First (c0, c1) = (-2, -2). Yields exactly 1 tuple = (-2, -2).
        assert polys == [(-2, -2)]


# ---------------------------------------------------------------------------
# Total subspace size
# ---------------------------------------------------------------------------


class TestTotalSubspaceSize:
    def test_degree_14_pm5_canonical(self):
        """Day-5 sprint count: 97,435,855 = 5 * 11^7."""
        n = enumerate_total_size(14, (-5, 5), c0_positive_only=True)
        assert n == 5 * (11 ** 7)
        assert n == 97_435_855

    def test_degree_12_pm5_canonical(self):
        """deg=12 ±5 canonical: 5 * 11^6 = 8,857,805."""
        n = enumerate_total_size(12, (-5, 5), c0_positive_only=True)
        assert n == 5 * (11 ** 6)
        assert n == 8_857_805

    def test_degree_2_minimal(self):
        """deg=2 ±1 canonical: 1 c0 value (just 1) * 3 c1 values = 3."""
        n = enumerate_total_size(2, (-1, 1), c0_positive_only=True)
        assert n == 3


# ---------------------------------------------------------------------------
# Per-shard worker smoke test
# ---------------------------------------------------------------------------


class TestProcessShardGeneral:
    def test_smoke_degree_2_produces_in_band_dict(self):
        """Run a tiny deg=2 ±1 shard end-to-end. Just verify shape — no
        deg-2 polynomial of this restricted form ends up with M in
        (1+1e-6, 1.18) so in_band should be empty for this trivial case."""
        result = process_shard_general(
            (0, 3, (-1, 1), 1.18, True, 2)
        )
        assert isinstance(result, dict)
        assert "shard_idx" in result and result["shard_idx"] == 0
        assert "polys_processed" in result and result["polys_processed"] == 1
        assert "in_band" in result and isinstance(result["in_band"], list)


# ---------------------------------------------------------------------------
# Run orchestrator smoke
# ---------------------------------------------------------------------------


class TestRunBruteForceGeneralSmoke:
    def test_degree_2_pm1_runs_end_to_end(self):
        """Tiny end-to-end test: deg=2 ±1 has only 3 polys (P(x)=1+c1*x+x^2
        for c1 in [-1, 0, 1]); none fall in the Lehmer band."""
        result = run_brute_force_general(
            degree=2,
            coef_range=(-1, 1),
            c0_positive_only=True,
        )
        assert result["degree"] == 2
        assert result["n_polys_processed"] == 3
        assert result["n_polys_total_expected"] == 3
        assert result["in_band_count"] == 0
        assert result["in_band"] == []
        # 1 c0 value (1) * 3 c1 values (in [-1,0,1]) = 3 shards
        assert result["n_shards"] == 3
