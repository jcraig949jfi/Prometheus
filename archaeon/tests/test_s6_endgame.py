"""S6: partition statistics, the sealed oracle's separation from candidates, LB2 exactness on the minimal witness,
the blind exact policy value, and the census-permutation adversarial test (the S5 run-1 defect class)."""
import inspect
import random

import numpy as np
import pytest

from archaeon.producer import acquisition as AQ, fossil_inference as FI, s4_producers as P, s5_producers as O5, s6_endgame as S6

N6 = [FI.Fossil("00000000", 6 / 8), FI.Fossil("11110000", 6 / 8)]     # 2 ones among positions 0..3, positions 4..7 fixed 0: N 6


def test_candidates_cannot_receive_target_or_oracle_and_control_must():
    params = inspect.signature(S6.produce_refined).parameters
    assert not any(k in ("target", "hidden_target", "t", "oracle", "target_index", "winner", "outcome") for k in params)
    assert "oracle" in inspect.signature(S6.produce_oracle_control).parameters
    for fn in (S6.statistic, S6.lb2_num, S6.v2_num, S6.partition_cells):
        assert not any(k in ("target", "hidden_target", "t", "oracle") for k in inspect.signature(fn).parameters), fn


WITNESS = [FI.Fossil("00000000", 0.25), FI.Fossil("01010011", 0.5), FI.Fossil("11000000", 0.25)]   # N 6, G {2,2,2} vs oracle {3,2,1} (S6 characterization, evs:1c02f77cec2e4734)


def test_lb2_on_the_minimal_witness_prefers_what_the_oracle_prefers_and_er_does_not():
    S = S6.feasible_ints(WITNESS); L = 8; oracle = S6.SealedOracle(L)
    cells = {q: S6.partition_cells(L, S, q) for q in range(1 << L)}
    q222 = next(q for q, c in cells.items() if c == (2, 2, 2))
    all321 = [q for q, c in cells.items() if c == (3, 2, 1)]
    assert S6.er_num(cells[q222]) < S6.er_num(cells[all321[0]])                 # ER prefers {2,2,2} (12 < 14)
    lb321 = {q: S6.lb2_num(L, S, q, {}) for q in all321}
    q321 = min(all321, key=lambda q: (lb321[q], q)); q321bad = max(all321, key=lambda q: (lb321[q], -q))
    assert S6.lb2_num(L, S, q222, {}) == 1.0                                       # three pairs: each costs exactly one more probe
    assert abs(lb321[q321] - (0.5 * 1.0 + 2 / 6)) < 1e-12                        # triple SHATTERABLE -> 1, pair -> 1, singleton -> 0
    assert abs(lb321[q321bad] - (0.5 * (1 + 2 / 3) + 2 / 6)) < 1e-12              # triple NOT shatterable: best next probe leaves a pair
    # the oracle agrees exactly with LB2 on all three, and ER cannot tell the two {3,2,1} probes apart at all
    assert abs(oracle.Q(S, q222) - 2.0) < 1e-12 and abs(oracle.Q(S, q321) - (1 + 0.5 + 2 / 6)) < 1e-12 and abs(oracle.Q(S, q321bad) - (1 + 0.5 * (1 + 2 / 3) + 2 / 6)) < 1e-12
    assert oracle.Q(S, q321) < oracle.Q(S, q222) < oracle.Q(S, q321bad)
    assert oracle.ledger.fresh_units > 0 and oracle.ledger.calls >= 2         # the oracle pays and says so


def test_refinement_is_inactive_when_the_window_holds_one_probe_and_shares_G_pool():
    si = {"lane": "t", "L": 8, "world": "w", "arm": "G", "step": 1}
    sh = [FI.Fossil("00000000", 7 / 8)]                                      # shell m 1: all pool ER-minimisers are equivalent, tie class -> same shape
    g = P.produce_G(sh, si); c = S6.produce_refined(sh, si, "lb2", 0.0)
    assert c.ancestry["pool_size"] == g.ancestry["pool_size"] and c.objective_value == g.objective_value
    n6 = S6.produce_refined(N6, si, "lb2", 0.0); g6 = P.produce_G(N6, si)
    assert n6.ancestry["active"] and n6.objective_value == g6.objective_value    # exact tie window keeps G's ER value
    assert "probe_scored" in str(n6.ancestry) or n6.compute_seconds >= 0


def test_random_policy_value_is_never_below_the_optimum_and_solves_a_pair():
    S = S6.feasible_ints(N6); L = 8; memo = {}
    r = S6.random_policy_value(L, S, memo); v = S6.SealedOracle(L).V(S)
    assert r >= v - 1e-9 and r > v
    pair = np.array(sorted(S[:2]), dtype=np.int64)
    rp = S6.random_policy_value(L, pair, memo)
    D = O5._dist_matrix(L); sep = sum(1 for q in range(1 << L) if D[q, pair[0]] != D[q, pair[1]])
    assert abs(rp - (1 << L) / sep) < 1e-9                                       # geometric: expected trials until a separating probe


def test_census_permutation_cannot_change_a_candidate_decision():
    """The S5 run-1 defect class: nothing a candidate sees may vary with the target's position in the census.
    Same evidence, any fossil order, any census order -> identical proposal for every candidate and for G."""
    si = {"lane": "s6", "L": 8, "world": "L8_x", "arm": "G", "step": 2}
    E = [FI.Fossil("00000000", 0.75), FI.Fossil("01001011", 0.5), FI.Fossil("11000000", 0.75)]       # a real S5 decision state (N 6)
    assert FI.infer(E).feasible_targets == 6
    ref = {(k, w): S6.produce_refined(E, si, k, w).probe for k in ("lb2", "entropy") for w in (0.0, 0.2)}
    ref["G"] = P.produce_G(E, si).probe
    for perm in (E[::-1], [E[1], E[2], E[0]]):
        for k in ("lb2", "entropy"):
            for w in (0.0, 0.2):
                assert S6.produce_refined(perm, si, k, w).probe == ref[(k, w)]
        assert P.produce_G(perm, si).probe == ref["G"]
    assert "target_index" not in si and "target" not in si


def test_no_oracle_value_leaks_into_candidate_provenance():
    si = {"lane": "t", "L": 8, "world": "w", "arm": "G", "step": 1}
    c = S6.produce_refined(N6, si, "lb2", 0.2)
    s = repr(c.ancestry) + repr(c.extra)
    assert "oracle" not in s and "V_star" not in s and "Q_" not in s and c.evidence_policy == "PEW_CONSUMING"
    ctrl = S6.produce_oracle_control(N6, si, S6.SealedOracle(8), 0.2)
    assert ctrl.evidence_policy == "ORACLE_ASSISTED" and ctrl.extra["oracle_assisted"]
