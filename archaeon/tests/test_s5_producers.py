"""S5 producer O: exact full-horizon identification policy under the S4 contract and the S5 work budget."""
import inspect
from fractions import Fraction

import pytest

from archaeon.producer import acquisition as AQ, fossil_inference as FI, s4_producers as P, s5_producers as O


def _score(x, t):
    return sum(a == b for a, b in zip(x, t)) / len(t)


def _follow(fossils, producer, **kw):
    """Run the producer to identification for EVERY feasible target; return the exact mean number of probes."""
    targets = FI.enumerate_targets(list(fossils)); steps = []
    for t in targets:
        E = list(fossils); k = 0
        while AQ.feasible(E).feasible_targets > 1:
            p = producer(E, {"lane": "test", "world": 0, "step": k + 1}, **kw); assert p.probe is not None, p.extra
            E.append(FI.Fossil(p.probe, _score(p.probe, t))); k += 1
        steps.append(k)
    return Fraction(sum(steps), len(steps))


COUNTEREXAMPLE = [FI.Fossil("00000000", 5 / 8), FI.Fossil("11110000", 3 / 8)]     # two count-known blocks (1 one in 0..3, 2 ones in 4..7), N 24
SHELL2 = [FI.Fossil("00000000", 6 / 8)]                                             # one fossil, 2 mismatches, N 28


def test_signature_cannot_receive_the_target():
    params = inspect.signature(O.produce_O).parameters
    assert not any(k in ("target", "hidden_target", "t") for k in params)
    assert "fossils" in params and "max_units" in params


def test_exact_values_on_the_two_reference_states_and_policy_consistency():
    O.clear_memo()
    p = O.produce_O(COUNTEREXAMPLE, {"lane": "test", "world": 0, "step": 1})
    assert p.producer_id == "O" and p.extra["outcome"] == "OK" and p.evidence_policy == "PEW_CONSUMING"
    assert abs(p.objective_value - 35 / 12) < 1e-9                                   # exact DP value (scratch s5_state_detail: 2.9167)
    assert p.probe in p.tie_class and len(p.probe) == 8
    # following O's own proposals to identification realises exactly that expectation over every target
    assert _follow(COUNTEREXAMPLE, O.produce_O) == Fraction(35, 12)
    s = O.produce_O(SHELL2, {"lane": "test", "world": 1, "step": 1})
    assert abs(s.objective_value - 97 / 28) < 1e-9 and _follow(SHELL2, O.produce_O) == Fraction(97, 28)


def test_O_is_never_worse_than_greedy_W_and_strictly_better_on_the_shell():
    O.clear_memo()
    eg = _follow(SHELL2, P.produce_W)                # W = exact one-step optimum at L <= 12 (exhaustive pool), lexicographic tie-break
    eo = _follow(SHELL2, O.produce_O)
    assert eo < eg and eo == Fraction(97, 28) and eg == Fraction(106, 28)


def test_memo_is_declared_and_returns_the_identical_proposal_without_work():
    O.clear_memo()
    a = O.produce_O(COUNTEREXAMPLE, {"lane": "test", "world": 0, "step": 1})
    b = O.produce_O(COUNTEREXAMPLE, {"lane": "test", "world": 0, "step": 1})
    assert a.ancestry["fresh_subsets"] > 0 and a.ancestry["work_units"] > 0
    assert b.ancestry["fresh_subsets"] == 0 and b.ancestry["memo_hits"] > 0 and b.ancestry["work_units"] == 0
    assert a.probe == b.probe and a.objective_value == b.objective_value and a.tie_class == b.tie_class


def test_budget_and_scope_outcomes_are_explicit():
    O.clear_memo()
    r = O.produce_O(COUNTEREXAMPLE, {"lane": "test", "world": 0, "step": 1}, max_units=10)
    assert r.probe is None and r.extra["outcome"] == "BUDGET_EXHAUSTED" and r.extra["work"]["phase"] == "dp_subset_probe" and r.extra["work"]["units_used"] > 10
    s = O.produce_O(COUNTEREXAMPLE, {"lane": "test", "world": 0, "step": 1}, max_targets=10)
    assert s.probe is None and s.extra["outcome"] == "SCOPE_EXCEEDED" and s.extra["n_feasible"] == 24
    long = [FI.Fossil("0" * 13, 12 / 13)]
    u = O.produce_O(long, {"lane": "test", "world": 0, "step": 1})
    assert u.probe is None and u.extra["outcome"] == "SCOPE_EXCEEDED" and u.extra["reason"] == "length"


def test_no_target_leaks_through_provenance():
    O.clear_memo()
    t = "10110010"; p = O.produce_O(COUNTEREXAMPLE, {"lane": "test", "world": 0, "step": 1})
    assert t not in repr(p.ancestry) and t not in repr(p.extra) and p.evidence_snapshot_id == P.snapshot_id(COUNTEREXAMPLE)


def test_GH_is_G_with_an_entropy_tie_break_only():
    from archaeon.producer import s5_coordinates as C
    assert not any(k in ("target", "hidden_target", "t") for k in inspect.signature(O.produce_GH).parameters)
    for fn in (C.entropy_disagreement, C.entropy_deficit_bits, C.two_block_proxy, C.two_step_gap, C.all_coordinates):
        assert not any(k in ("target", "hidden_target", "t", "outcome", "winner") for k in inspect.signature(fn).parameters), fn
    si = {"lane": "test", "world": 0, "step": 2}
    N6 = [FI.Fossil("00000000", 6 / 8), FI.Fossil("11110000", 6 / 8)]        # 2 ones among positions 0..3; positions 4..7 fixed 0
    g = P.produce_G(N6, si); h = O.produce_GH(N6, si)
    assert g.ancestry["pool_size"] == h.ancestry["pool_size"] and abs(g.objective_value - h.objective_value) < 1e-12      # same pool, same ER optimum
    assert h.extra["entropy_bits"] > g.extra["entropy_bits"] + 0.2 and h.producer_id == "GH" and h.evidence_policy == "PEW_CONSUMING"
    # and where the ER-optimal class is entropy-homogeneous GH equals G
    sh = [FI.Fossil("00000000", 6 / 8)]
    assert O.produce_GH(sh, si).probe == P.produce_G(sh, si).probe
