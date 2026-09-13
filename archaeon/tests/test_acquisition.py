"""S3 phase 2: the probe-scoring oracle on small known worlds. The hidden
target is known to the harness and never given to the selector."""
import itertools
import random

import pytest

from archaeon.producer import acquisition as AQ
from archaeon.producer import fossil_inference as FI


def _score(x, t):
    return sum(a == b for a, b in zip(x, t)) / len(t)


def _fossils(t, xs):
    return [FI.Fossil(x, _score(x, t)) for x in xs]


def test_enumeration_partitions_agree_on_random_worlds():
    rnd = random.Random(2026)
    for _ in range(40):
        L = rnd.choice([6, 8, 10]); t = "".join(rnd.choice("01") for _ in range(L))
        xs = list({"".join(rnd.choice("01") for _ in range(L)) for _ in range(rnd.choice([1, 2, 3]))})
        fs = _fossils(t, xs); st = AQ.feasible(fs)
        for _ in range(6):
            q = "".join(rnd.choice("01") for _ in range(L))
            assert AQ.outcome_partition(st, q) == AQ.brute_partition(fs, q)


def test_positive_a_splitting_probe_outranks_an_unresolving_one():
    """Exactly two feasible targets a = 0100, b = 1000 (fossils 0000 at
    distance 1 and 1100 at distance 1). A probe at different distances from
    a and b splits the set (ER = 1); a probe equidistant from both leaves it
    whole (ER = 2)."""
    fs = [FI.Fossil("0000", 0.75), FI.Fossil("1100", 0.75)]
    st = AQ.feasible(fs); enum = sorted(FI.enumerate_targets(fs))
    assert enum == ["0100", "1000"] and st.feasible_targets == 2
    v_split = AQ.value(st, "0100")        # d(a) = 0, d(b) = 2
    v_same = AQ.value(st, "0011")         # d(a) = 3, d(b) = 3
    assert v_split.expected_remaining == 1.0 and v_same.expected_remaining == 2.0
    assert AQ.select(st, ["0011", "0100"]).probe == "0100"


def test_useless_probe_gets_no_reward_for_distance():
    """A far-away probe whose outcome is identical for every feasible target
    has ER = N: distance is not information."""
    L = 8; t = "11110000"
    fs = _fossils(t, ["11110000"])                    # m = 0: the target is identified... use m = L instead for a real set
    fs = _fossils(t, ["00001111"])                    # complement: also identified. Use a set with 2 targets:
    fs = [FI.Fossil("00000000", 0.5), FI.Fossil("11110000", 1.0 - 2 / 8)]
    st = AQ.feasible(fs); N = st.feasible_targets; assert N > 1
    # a probe that agrees with all fossils on every FIXED/agreeing structure and cannot separate targets: compare
    # the most distant probe from the best fossil against the best probe in the pool
    best = max(fs, key=lambda f: f.score).bits
    far = "".join("1" if c == "0" else "0" for c in best)
    v_far = AQ.value(st, far); v_best = AQ.value(st, best)
    # complement induces the SAME partition as the fossil itself (d -> L - d): identical ER, no bonus for distance
    assert v_far.er_numerator == v_best.er_numerator
    sel = AQ.select(st, AQ.probe_pool(st, fs, random.Random(1)))
    assert sel.value.er_numerator <= v_far.er_numerator


def test_equivalence_same_partition_same_value_and_complement_symmetry():
    rnd = random.Random(5)
    for _ in range(20):
        L = 8; t = "".join(rnd.choice("01") for _ in range(L))
        fs = _fossils(t, list({"".join(rnd.choice("01") for _ in range(L)) for _ in range(2)}))
        st = AQ.feasible(fs); q = "".join(rnd.choice("01") for _ in range(L)); qc = "".join("1" if c == "0" else "0" for c in q)
        pq, pc = AQ.outcome_partition(st, q), AQ.outcome_partition(st, qc)
        assert {L - d: n for d, n in pq.items()} == pc                     # cosmetic representation change, same partition up to relabelling
        assert AQ.value(st, q).er_numerator == AQ.value(st, qc).er_numerator


def test_ambiguity_ties_are_reported_as_a_class_not_a_unique_best():
    L = 6; t = "110100"; fs = _fossils(t, ["000000"])       # one fossil: full symmetry among positions
    st = AQ.feasible(fs); pool = ["100000", "010000", "001000", "000100", "000010", "000001"]
    sel = AQ.select(st, pool)
    assert len(sel.tie_class) == 6 and sel.probe == min(pool)            # all six single-bit probes tie; the name is the lexicographic min


def test_cheat_the_legitimate_selector_never_sees_the_target(monkeypatch):
    """A cheating selector that reads the hidden target always achieves ER = 1
    by probing the target itself; the legitimate path has no argument through
    which the target can flow, and its chosen probe's value is computed from
    fossils alone."""
    L = 8; rnd = random.Random(9); t = "".join(rnd.choice("01") for _ in range(L))
    fs = _fossils(t, ["".join(rnd.choice("01") for _ in range(L)) for _ in range(2)])
    st = AQ.feasible(fs)
    def cheating_selector(hidden_target): return hidden_target            # a selector that reads the answer
    q_cheat = cheating_selector(t)
    realised_remaining = AQ.outcome_partition(st, q_cheat)[0]             # the cell the true target falls in: distance 0 from itself
    assert realised_remaining == 1                                        # cheating identifies the target in one probe, always
    import inspect
    for fn in (AQ.feasible, AQ.outcome_partition, AQ.value, AQ.probe_pool, AQ.select):
        assert "target" not in inspect.signature(fn).parameters and "hidden" not in inspect.signature(fn).parameters
    seen = {}
    real = AQ.outcome_partition
    def spy(state, q): seen.setdefault("calls", []).append(q); return real(state, q)
    monkeypatch.setattr(AQ, "outcome_partition", spy)
    sel = AQ.select(st, AQ.probe_pool(st, fs, random.Random(3), n_random=4))
    assert all(len(q) == L for q in seen["calls"]) and sel.probe in AQ.probe_pool(st, fs, random.Random(3), n_random=4)


def test_order_invariance_of_probe_value():
    L = 8; t = "10010110"; xs = ["00000000", "11110000", "10101010"]
    fs = _fossils(t, xs); q = "11001100"
    ref = AQ.value(AQ.feasible(fs), q).er_numerator
    for perm in itertools.permutations(fs):
        assert AQ.value(AQ.feasible(list(perm)), q).er_numerator == ref


def test_contradiction_fails_closed_before_any_probe():
    fs = [FI.Fossil("0000", 0.5), FI.Fossil("0000", 0.75)]
    with pytest.raises(FI.Contradiction):
        AQ.feasible(fs)


def test_selector_finds_the_oracle_optimum_class_on_small_worlds():
    """The scalable pool must contain a member of the exact optimum class (or
    the test records the gap): the oracle enumerates all 2^L probes."""
    rnd = random.Random(11); hits = 0; n = 0
    for _ in range(12):
        L = 8; t = "".join(rnd.choice("01") for _ in range(L))
        fs = _fossils(t, list({"".join(rnd.choice("01") for _ in range(L)) for _ in range(2)}))
        best_num, cls = AQ.optimum_by_enumeration(fs); st = AQ.feasible(fs)
        sel = AQ.select(st, AQ.probe_pool(st, fs, random.Random(n), n_random=16)); n += 1
        assert sel.value.er_numerator >= best_num                          # the pool can never beat the oracle
        hits += sel.value.er_numerator == best_num
    assert hits >= 6, "the pool reached the oracle optimum on only {} of 12 worlds".format(hits)
