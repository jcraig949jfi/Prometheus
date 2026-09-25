import numpy as np
import pytest

from ensorain.lm01.families import make_world, FAMILIES, LEVELS


def test_campaign_seed_guard():
    with pytest.raises(AssertionError):
        make_world("F2_latent", "L1", 123)


@pytest.mark.parametrize("fam", FAMILIES)
def test_every_family_builds_below_full_coverage(fam):
    w = make_world(fam, "L1", 9_100_001)
    assert 0 < w["coverage"] < 1 and w["n_unseen"] > 0 and w["tests"]
    for A, y, s in w["train"]:
        assert A.shape[1] == len(w["dims"]) and np.all(A < np.array(w["dims"]))


def test_families_do_not_share_fields():
    a, b = make_world("F2_latent", "L1", 9_100_002), make_world("F5_nuisance", "L1", 9_100_002)
    assert not np.array_equal(a["train"][0][2][:50], b["train"][0][2][:50])


def test_nuisance_mode_predictive_in_train_only():
    w = make_world("F5_nuisance", "L1", 9_100_003)
    A, y, _ = w["train"][0]
    means = [y[A[:, -1] == k].mean() for k in range(4)]
    assert all(np.diff(means) > 0)              # the bin is a monotone function of the observed value
    U, _ = w["tests"]["ood_never_seen"]
    assert len(np.unique(U[:, -1])) > 1


def test_transfer_fields_share_family_component():
    w = make_world("F4_transfer", "L1", 9_100_004)
    (Aa, _, sa), (Ab, _, sb) = w["train"]
    assert len(sb) < len(sa)
