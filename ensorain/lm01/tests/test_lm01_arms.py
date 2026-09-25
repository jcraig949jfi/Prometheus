"""Audit tests for WTP-LM01 arms, accounting and recoverability (dev synthetic data only; no WTP seeds)."""
import numpy as np
import pytest

from ensorain.lm01.arms import LosslessK, LosslessR, LRCache, LRSubsample, Selective, RandomMerge, Hybrid
from ensorain.lm01.recover import recoverability

DIMS = [8, 8, 8]


def stream(n=600, seed=0, rank=2, noise=0.0):
    rng = np.random.default_rng(seed)
    U, V = rng.normal(size=(8, rank)), rng.normal(size=(64, rank))
    x = (U @ V.T).reshape(DIMS)
    A = np.stack([rng.integers(0, d, n) for d in DIMS], 1)
    y = x[tuple(A.T)] + noise * rng.normal(size=n)
    return A, y, x


def feed(arm, A, y, batch=50):
    for i in range(0, len(y), batch):
        arm.observe(A[i:i + batch], y[i:i + batch])
    return arm


def test_lossless_store_is_bit_exact():
    A, y, _ = stream(noise=0.1)
    arm = feed(LosslessK(DIMS), A, y)
    assert np.array_equal(arm.store.y, y) and np.array_equal(arm.store.A.astype(int), A)
    r = recoverability(arm, A, y, tau=0.0, rng=np.random.default_rng(1))
    assert r["R"] == 1.0


def test_lossless_persistent_bytes_grow_linearly_and_are_measured():
    A, y, _ = stream()
    arm = feed(LosslessK(DIMS), A[:300], y[:300])
    b1 = arm.meter.persistent_bytes
    feed(arm, A[300:], y[300:])
    assert arm.meter.persistent_bytes == 2 * b1 == arm.store.nbytes()


@pytest.mark.parametrize("cls", [LosslessK, LosslessR])
def test_lossless_readouts_read_full_store_and_keep_nothing(cls):
    A, y, _ = stream()
    arm = feed(cls(DIMS), A, y)
    for _ in range(3):
        arm.predict(A[:40])
    m = arm.meter
    assert m.full_read_violations == 0 and m.persist_growth_on_query == 0


def test_lr_refit_is_charged_every_query():
    A, y, _ = stream()
    arm = feed(LosslessR(DIMS), A, y)
    arm.predict(A[:10])
    one = arm.meter.replay_ops
    arm.predict(A[:10])
    assert one > 0 and arm.meter.replay_ops == 2 * one


def test_cheat_fit_cache_is_flagged():                 # R1c
    A, y, _ = stream()
    arm = feed(LRCache(DIMS), A, y)
    arm.predict(A[:10]); arm.predict(A[:10])
    assert arm.meter.persist_growth_on_query >= 1


def test_cheat_subsample_is_flagged():                 # R1d
    A, y, _ = stream()
    arm = feed(LRSubsample(DIMS), A, y)
    arm.predict(A[:10])
    assert arm.meter.full_read_violations >= 1


def test_selective_state_is_bounded_and_lossy():
    A, y, _ = stream(n=1500, noise=0.1)
    arm = feed(Selective("lowrank", DIMS, cap=80), A, y)
    assert arm.meter.peak_persistent <= (80 + 1) * 8
    r = recoverability(arm, A, y, tau=0.05, rng=np.random.default_rng(1))
    assert r["R"] < 1.0


def test_random_merge_HR2_increases_with_bins():
    A, y, _ = stream(n=1500)
    H = [recoverability(feed(RandomMerge(DIMS, B, seed=3), A, y), A, y, tau=0.1, rng=np.random.default_rng(1))["HR2"]
         for B in (4, 64, 512, 4096)]
    assert H[0] < H[1] < H[2] < H[3]


def test_D1_thresholded_R_is_not_monotone():            # the recorded defect stays demonstrated
    A, y, _ = stream(n=1500)
    R = [recoverability(feed(RandomMerge(DIMS, B, seed=3), A, y), A, y, tau=0.1, rng=np.random.default_rng(1))["R"]
         for B in (1, 64)]
    assert R[1] < R[0]


def test_reconstruct_does_not_touch_the_meter():
    A, y, _ = stream()
    arm = feed(LosslessK(DIMS), A, y)
    before = arm.meter.as_dict()
    recoverability(arm, A, y, tau=0.0, rng=np.random.default_rng(1))
    assert arm.meter.as_dict() == before


def test_hybrid_index_ablation_keeps_store():
    A, y, _ = stream()
    arm = feed(Hybrid(DIMS, cap=48), A, y)
    d0 = arm.store.digest()
    arm.ablate_index()
    assert arm.store.digest() == d0 and arm.ablated


def test_HR2_signal_separates_noise_from_signal():       # #627
    A, y, x = stream(n=1500, noise=0.3)
    sig = x[tuple(A.T)]
    arm = feed(Selective("lowrank", DIMS, cap=144), A, y)
    r = recoverability(arm, A, y, tau=0.1, rng=np.random.default_rng(1), signal=sig)
    lk = recoverability(feed(LosslessK(DIMS), A, y), A, y, tau=0.1, rng=np.random.default_rng(1), signal=sig)
    assert r["HR2_signal"] > r["HR2"]           # the selective arm lost noise, not signal
    assert lk["HR2"] == 1.0 and lk["HR2_signal"] < 1.0   # the exact store keeps the noise too
