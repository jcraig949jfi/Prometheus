"""Pins the API lane C imports (primordial/brain/c1b_load.py: nb_bucket_class(3)(p))
and the kernel's exactness, so lane B cannot silently break lane C."""
from __future__ import annotations

import numpy as np
import pytest

from primordial.brain import tt_policy as tt
from primordial.soup.bounty.c1_cpu import nb_bucket_class


@pytest.mark.parametrize("nchunks", [1, 3, 24])
def test_nb_bucket_matches_np_bucket_on_random_policy(nchunks):
    p = tt.random_policy(obs_dim=4, r=8, A=8, seed=11)
    obs = np.random.default_rng(3).integers(0, 65535, size=(257, 4), dtype=np.uint16, endpoint=True)
    got = nb_bucket_class(nchunks)(p).logits(obs)
    want = tt.NpBucket(p).logits(obs)
    assert got.shape == want.shape == (257, 8)
    assert np.abs(got - want).max() <= 1e-4


def test_nb_bucket_exact_on_additive_positive_control():
    rng = np.random.default_rng(1)
    f = rng.integers(-8, 9, size=(16, 16, 8)).astype(np.float64)
    p = tt.additive_policy(f, r=16)
    obs = rng.integers(0, 65535, size=(500, 4), dtype=np.uint16, endpoint=True)
    be = nb_bucket_class(3)(p)
    assert np.array_equal(be.logits(obs), tt.additive_logits(f, obs).astype(np.float32))
    assert np.array_equal(be.run(be.prepare(obs)), tt.additive_logits(f, obs).argmax(1).astype(np.int32))


def test_skip_half_cheat_is_not_exact():
    rng = np.random.default_rng(1)
    f = rng.integers(-8, 9, size=(16, 16, 8)).astype(np.float64)
    p = tt.additive_policy(f, r=16)
    obs = rng.integers(0, 65535, size=(500, 4), dtype=np.uint16, endpoint=True)
    cheat = nb_bucket_class(3, stride=2, cheat=True)(p)
    assert cheat.cheat and cheat.name == "cheat_nb_bucket_skip_half"
    assert not np.array_equal(cheat.logits(obs), tt.additive_logits(f, obs).astype(np.float32))


def test_class_names_are_what_lane_c_expects():
    assert nb_bucket_class(3).name == "nb_bucket_c3"
    assert nb_bucket_class(3).cheat is False
