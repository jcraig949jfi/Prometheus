"""Test OPERATOR_RANK_PARITY_NULL_CONTROL."""
import sys, os

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.rank_parity_null import rank_parity_null_control


def _population(ranks, conductors=None):
    ranks = np.asarray(ranks, dtype=int)
    if conductors is None:
        conductors = np.arange(1, len(ranks) + 1, dtype=float)
    arr = np.zeros(len(ranks), dtype=[("analytic_rank", "i4"), ("conductor", "f8")])
    arr["analytic_rank"] = ranks
    arr["conductor"] = np.asarray(conductors, dtype=float)
    return arr


def _rank_counts_from_perm(pop, perm):
    vals, counts = np.unique(pop["analytic_rank"][np.asarray(perm, dtype=int)], return_counts=True)
    return {int(k): int(v) for k, v in zip(vals, counts)}


def test_synthetic_rank_distribution_preserves_marginals():
    ranks = [0] * 60 + [1] * 30 + [2] * 10
    pop = _population(ranks)

    result = rank_parity_null_control(pop, n_perms=20, seed=1)
    audit = result["rank_parity_audit"]

    assert audit["rank_distribution"] == {0: 60, 1: 30, 2: 10}
    assert audit["parity_distribution"] == {0: 70, 1: 30}
    assert audit["joint_marginal_preserved"] is True
    for perm in result["matched_population_indices"]:
        assert _rank_counts_from_perm(pop, perm) == {0: 60, 1: 30, 2: 10}
    assert np.std(result["null_distribution"]) <= np.sqrt(len(pop))


def test_two_populations_report_rank_distribution_difference():
    pop_a = _population([0] * 80 + [1] * 20)
    pop_b = _population([0] * 20 + [1] * 80)

    result = rank_parity_null_control([pop_a, pop_b], n_perms=5, seed=2)
    comp = result["rank_parity_audit"]["pairwise_population_comparison"]["population_0_vs_1"]

    assert comp["rank_l1_distance"] > 0.5
    assert comp["parity_l1_distance"] > 0.5
    assert comp["rank_parity_asymmetry"] is True
    assert comp["pattern_flag"] == "PATTERN_RANK_PARITY_LEAK_RISK"


def test_three_population_f011_shape_flags_rank_parity_asymmetry():
    non_cm_ec = _population([0] * 70 + [1] * 25 + [2] * 5)
    cm_ec = _population([0] * 92 + [2] * 8)
    g2c_usp4 = _population([0] * 35 + [1] * 45 + [2] * 15 + [3] * 5)

    result = rank_parity_null_control([non_cm_ec, cm_ec, g2c_usp4], n_perms=7, seed=3)
    audit = result["rank_parity_audit"]
    comp = audit["pairwise_population_comparison"]

    assert audit["canonical_use"].startswith("F011")
    assert len(audit["population_audits"]) == 3
    assert all(v["rank_parity_asymmetry"] for v in comp.values())
    assert any(
        v["pattern_flag"] == "PATTERN_RANK_PARITY_LEAK_RISK"
        for v in comp.values()
    )


def test_determinism_same_seed_bit_identical_null():
    pop = _population([0, 1, 2, 3] * 10)

    r1 = rank_parity_null_control(pop, n_perms=12, seed=99)
    r2 = rank_parity_null_control(pop, n_perms=12, seed=99)

    assert np.array_equal(r1["null_distribution"], r2["null_distribution"])
    assert r1["matched_population_indices"] == r2["matched_population_indices"]


def test_single_rank_population_trivial_preservation():
    pop = _population([0] * 25)

    result = rank_parity_null_control(pop, n_perms=6, seed=4)

    assert result["rank_parity_audit"]["rank_distribution"] == {0: 25}
    assert result["rank_parity_audit"]["parity_distribution"] == {0: 25}
    assert result["rank_parity_audit"]["joint_marginal_preserved"] is True
    assert np.allclose(result["null_distribution"], 0.0)


def test_conductor_decile_underdetermined_flags_gracefully():
    pop = _population([0, 1, 0, 1, 2], conductors=[10, 10, 20, 20, 20])

    result = rank_parity_null_control(pop, n_perms=3, seed=5)
    decile_audit = result["rank_parity_audit"]["conductor_decile_audit"]

    assert decile_audit["underdetermined"] is True
    assert "underdetermined" in decile_audit["warning"]
    assert result["rank_parity_audit"]["joint_marginal_preserved"] is True


def test_npz_path_input(tmp_path):
    pop = _population([0, 1, 2, 1])
    path = tmp_path / "pop.npz"
    np.savez(path, data=pop)

    result = rank_parity_null_control(str(path), n_perms=2, seed=6)

    assert result["rank_parity_audit"]["rank_distribution"] == {0: 1, 1: 2, 2: 1}


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
