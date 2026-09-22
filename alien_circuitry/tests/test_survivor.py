"""Survivor-gate tests on T_5 (3,125 states) and the U-C1 generator family at n=5."""
import random
import numpy as np
import pytest
from alien_circuitry.universe.monoid import build_monoid, kernel_compatible, ecc_region_by_class, rgs_maps
from alien_circuitry.universe.uc1_seed import pch_generators, frozen_rank5_map, FROZEN_MAP, SEED
from alien_circuitry.universe.directed_rewriting import layered_bfs
from alien_circuitry.gate2.observation_monoid import MonoidObserver
from alien_circuitry.gate2 import analysis2 as A
from alien_circuitry.gate2.navigation2 import make_policy, guided_dfs, greedy_walk


@pytest.fixture(scope="module")
def U():
    return build_monoid("PCH5", 5, pch_generators(5), target_rank=2)


def test_seed_is_deterministic_and_rank5():
    assert frozen_rank5_map().tolist() == FROZEN_MAP.tolist() and len(set(FROZEN_MAP.tolist())) == 5 and SEED == 5773439276592744044


def test_kernel_theorem_on_full_monoid(U):
    D = U["D"]; states = np.arange(U["NS"])
    for j, t in enumerate(U["targets"]):
        assert np.array_equal(kernel_compatible(U, states, t), D[:, j] >= 0)


def test_targets_are_canonical_rank2(U):
    F = U["F"]
    for t in U["targets"]:
        row = F[t].tolist(); assert row[0] == 0 and max(row) == 1 and len(set(row)) == 2
    assert len(U["targets"]) == len(rgs_maps(5, 2)) == 15


def test_symmetry_ecc_by_class(U):
    ecc, region, ncls = ecc_region_by_class(U); fi, fx = U["fwd"]; rng = random.Random(2)
    for _ in range(40):
        s = rng.randrange(U["NS"]); dist = np.full(U["NS"], -1, dtype=np.int16); layered_bfs(fi, fx, s, U["NS"], dist)
        assert int(dist.max()) == ecc[s] and int((dist >= 0).sum()) == region[s]


def test_verdict_emulation_matches_real_lookahead(U):
    ecc, region, _ = ecc_region_by_class(U); obs = MonoidObserver(U, ecc, region); rng = random.Random(3)
    for _ in range(300):
        s = rng.randrange(U["NS"]); j = rng.randrange(len(U["targets"])); h = rng.randrange(0, 7)
        v, _, _ = obs.real_lookahead(s, U["targets"][j], h)
        assert v == obs.verdict(s, j, h)


def test_observer_features_are_pairwise_free(U):
    ecc, region, _ = ecc_region_by_class(U); obs = MonoidObserver(U, ecc, region)
    # two states with the same count vector but different kernels must have identical features
    F = U["F"]; C = U["C"]
    s1 = int(np.nonzero((F == np.array([0, 0, 1, 2, 3])).all(axis=1))[0][0]); s2 = int(np.nonzero((F == np.array([0, 1, 0, 2, 3])).all(axis=1))[0][0])
    assert U["kmask"][s1] != U["kmask"][s2] and (C[s1] == C[s2]).all()
    t = U["targets"][0]
    assert obs.features(s1, t) == obs.features(s2, t)


def test_layers_and_traps_consistent(U):
    T = A.trap_edges(U); lay = A.layers(U, T)
    assert lay["R1"] == 0 and lay["R1_traps"] == 0  # full monoid: kernel criterion is exact
    assert lay["R0"] + lay["R1"] + lay["reachable"] == lay["pairs"]
    q = A.q1_exact(U, T, ecc_region_by_class(U)[0]); assert q["traps"] == T["n"]


def test_navigation_solutions_valid(U):
    ecc, region, _ = ecc_region_by_class(U); obs = MonoidObserver(U, ecc, region); D = U["D"]; rng = random.Random(5)
    from alien_circuitry.gate2.observation_monoid import sample_ball_costs
    bc = sample_ball_costs(obs, U, 200, 1)
    live = [(int(s), int(j)) for s, j in np.argwhere(D >= 3)]
    for pol in ("B2", "LA2", "KA"):
        p = make_policy(pol, obs, U, bc)
        for _ in range(30):
            s, j = live[rng.randrange(len(live))]
            d = guided_dfs(obs, p, s, j, D[:, j], budget=5000); g = greedy_walk(obs, p, s, j, D[:, j])
            if d["solved"]: assert d["path_len"] >= int(D[s, j])
            if g["solved"]: assert g["path_len"] >= int(D[s, j]) and not g["catastrophic"]
    pk = make_policy("KA", obs, U, bc)
    for _ in range(30):
        s, j = live[rng.randrange(len(live))]
        assert guided_dfs(obs, pk, s, j, D[:, j], budget=5000)["trap_transitions"] == 0
