"""Fossil metabolism S2 phase 1: the inference claim must survive falsification
before any row is emitted. Controls: POSITIVE (bits genuinely fixed),
AMBIGUOUS (many targets), CONTRADICTORY/CHEAT (a tampered score admits no
target), BASELINE (enumeration agrees on every count and every fixed bit),
ORDER INVARIANCE (insertion order changes nothing)."""
import itertools
import random

import pytest

from archaeon.producer import fossil_inference as FI


def _score(x: str, t: str) -> float:
    return sum(a == b for a, b in zip(x, t)) / len(t)


def _fossils(t: str, xs):
    return [FI.Fossil(x, _score(x, t)) for x in xs]


def _fixed_from_enum(targets):
    L = len(targets[0]); fixed = {}
    for j in range(L):
        vals = {tt[j] for tt in targets}
        if len(vals) == 1:
            fixed[j] = int(next(iter(vals)))
    return fixed


def test_one_fossil_fixes_nothing_unless_extreme():
    t = "10110010"; x = "10100011"
    inf = FI.infer(_fossils(t, [x]))
    assert inf.fixed_bits == {} and inf.feasible_targets == len(FI.enumerate_targets(_fossils(t, [x])))
    assert FI.infer([FI.Fossil(t, 1.0)]).fixed_bits == {j: int(c) for j, c in enumerate(t)}          # m = 0: t = x
    comp = "".join("1" if c == "0" else "0" for c in t)
    assert FI.infer([FI.Fossil(comp, 0.0)]).fixed_bits == {j: int(c) for j, c in enumerate(t)}       # m = L: t = complement


def test_positive_two_fossils_one_bit_apart_fix_that_bit_exactly():
    """S1's own geometry: x2 = x1 with one bit flipped; the score difference
    says whether that bit was right. That position is FIXED; no other is."""
    t = "1101001010110001"; x1 = "1001011010100001"
    x2 = x1[:5] + ("1" if x1[5] == "0" else "0") + x1[6:]
    inf = FI.infer(_fossils(t, [x1, x2]))
    assert inf.fixed_bits == {5: int(t[5])}
    cf = FI.two_fossil_closed_form(*_fossils(t, [x1, x2]))
    assert cf["consistent"] and cf["k"] == 1 and cf["D_fixed"] and inf.feasible_targets == cf["feasible_targets"]


def test_positive_full_identification_from_a_basis():
    """L fossils that isolate every position identify the target uniquely."""
    t = "011010"; L = len(t)
    xs = ["000000"] + ["".join("1" if i == j else "0" for i in range(L)) for j in range(L)]
    inf = FI.infer(_fossils(t, xs))
    assert inf.feasible_targets == 1 and inf.status() == "FULLY_IDENTIFIED"
    assert "".join(str(inf.fixed_bits[j]) for j in range(L)) == t
    assert FI.posterior_mode(inf) == t and FI.expected_score(inf, t) == 1.0


def test_ambiguous_two_random_fossils_leave_many_targets_and_counts_only():
    t = "1011000111010010"; x1 = "0000111100001111"; x2 = "1100110011001100"
    fs = _fossils(t, [x1, x2]); inf = FI.infer(fs)
    enum = FI.enumerate_targets(fs)
    assert inf.feasible_targets == len(enum) > 1
    assert inf.fixed_bits == _fixed_from_enum(enum)          # whatever enumeration fixes, the solver fixes, and nothing more
    assert inf.status() in ("AMBIGUOUS", "COUNT_CONSTRAINED_ONLY", "PARTIALLY_IDENTIFIED")


def test_cheat_tampered_score_is_a_contradiction_not_a_guess():
    t = "10110010"; x1 = "10100011"; x2 = "00100011"
    fs = _fossils(t, [x1, x2])
    # CHEAT 1: the same candidate reported at two different distances -- no target is at two
    # Hamming distances from one point. A tampered score for a fossil that already exists.
    bad = fs + [FI.Fossil(fs[1].bits, fs[1].score + 2 / len(t))]
    with pytest.raises(FI.Contradiction):
        FI.infer(bad)
    assert FI.enumerate_targets(bad) == []
    # CHEAT 2: a single tampered score on a second candidate is NOT necessarily a contradiction
    # (it may still be satisfiable by some other target); the solver must say so honestly,
    # agreeing with enumeration in either case rather than declaring a contradiction it cannot prove.
    tam = [fs[0], FI.Fossil(fs[1].bits, fs[1].score + 2 / len(t))]
    enum = FI.enumerate_targets(tam)
    if enum:
        assert FI.infer(tam).feasible_targets == len(enum) and t not in enum       # consistent with SOME targets, never the true one
    else:
        with pytest.raises(FI.Contradiction):
            FI.infer(tam)
    with pytest.raises(FI.Contradiction):
        FI.Fossil("1010", 0.3).mismatches()                        # not an integer distance


def test_baseline_enumeration_agrees_on_random_instances():
    rnd = random.Random(20260912)
    for _ in range(40):
        L = rnd.choice([6, 8, 10, 12]); t = "".join(rnd.choice("01") for _ in range(L))
        n = rnd.choice([1, 2, 3, 4]); xs = list({"".join(rnd.choice("01") for _ in range(L)) for _ in range(n)})
        fs = _fossils(t, xs); inf = FI.infer(fs); enum = FI.enumerate_targets(fs)
        assert inf.feasible_targets == len(enum) >= 1                # the true target is always feasible
        assert t in enum
        assert inf.fixed_bits == _fixed_from_enum(enum)
        # per-position probabilities agree with enumeration frequencies
        for j in range(L):
            assert abs(inf.p_one[j] - sum(tt[j] == "1" for tt in enum) / len(enum)) < 1e-9


def test_order_invariance_and_duplicates():
    t = "110100101101"; xs = ["000011110000", "101010101010", "111100001111", "010101010101"]
    fs = _fossils(t, xs)
    ref = FI.infer(fs)
    for perm in itertools.permutations(fs):
        inf = FI.infer(list(perm))
        assert inf.feasible_targets == ref.feasible_targets and inf.fixed_bits == ref.fixed_bits and inf.p_one == ref.p_one and inf.order_key == ref.order_key
    assert FI.infer(fs + [fs[0]]).feasible_targets == ref.feasible_targets      # a duplicate fossil adds nothing


def test_two_fossil_closed_form_matches_solver():
    rnd = random.Random(7)
    for _ in range(60):
        L = rnd.choice([8, 12, 16, 24]); t = "".join(rnd.choice("01") for _ in range(L))
        x1 = "".join(rnd.choice("01") for _ in range(L)); x2 = "".join(rnd.choice("01") for _ in range(L))
        fs = _fossils(t, [x1, x2]); cf = FI.two_fossil_closed_form(*fs); inf = FI.infer(fs)
        assert cf["consistent"] and cf["feasible_targets"] == inf.feasible_targets
        D = [j for j in range(L) if x1[j] != x2[j]]
        assert all(j in inf.fixed_bits for j in D) == (cf["D_fixed"] and cf["k"] > 0)


def test_expected_score_of_posterior_mode_is_at_least_any_fossil_and_uniform():
    rnd = random.Random(3)
    for _ in range(30):
        L = 12; t = "".join(rnd.choice("01") for _ in range(L)); xs = list({"".join(rnd.choice("01") for _ in range(L)) for _ in range(3)})
        fs = _fossils(t, xs); inf = FI.infer(fs); mode = FI.posterior_mode(inf, tie_break=max(fs, key=lambda f: f.score).bits)
        es = FI.expected_score(inf, mode)
        assert es + 1e-12 >= max(FI.expected_score(inf, f.bits) for f in fs) and es >= 0.5 - 1e-12
