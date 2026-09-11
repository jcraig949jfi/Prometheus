"""PROBE-01 controls (roles/Polyhymnia/science/PROBE_01_PREREGISTRATION.md s4).

gate      every member passes Archaeon's check_exact; the cheat is REFUSED
positive  the A = 0 member equals h5.direct.v0 on all 4,096 genomes (P5)
planted   hamming: exactly 256 genomes at reach 0 / neutral 12 (P1, the cheat control)
analytic  hamming: max reach <= 11 (P2); preimage components [13,1,1,1] (P3);
          minimum distance 3
invariance scrambled(hamming) has hamming's histogram and mean_neutral (P4)
spread    random#1 and random#2 differ on histogram or mean_neutral
determinism the hamming table sha256 is a constant
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCIENCE = Path(__file__).resolve().parents[1]
if str(SCIENCE) not in sys.path:
    sys.path.insert(0, str(SCIENCE))

import lincode_decoders as L                     # noqa: E402
from archaeon.producer import h5_decoders as H    # noqa: E402
from archaeon.producer import h5_reference as R   # noqa: E402


def test_gate_every_member_has_exactly_16_preimages_per_rule():
    for dec in (L.make_direct_member(), L.make_hamming(), L.make_random(1), L.make_random(2)):
        facts = H.check_exact(dec)
        assert facts["rules_reached"] == 256 and facts["multiplicity"] == 16, facts


def test_gate_refuses_the_nonuniform_cheat():
    with pytest.raises(ValueError):
        H.check_exact(L.cheat_nonuniform)


def test_positive_control_A0_member_is_direct_entry_for_entry():
    a0 = L.make_direct_member()
    assert H.check_exact(a0)["table_sha256"] == H.check_exact(H.direct)["table_sha256"]
    assert all(a0(g) == H.direct(g) for g in range(4096))
    assert R.exact_reference(a0)["reach_histogram"] == {8: 4096}


def test_hamming_has_minimum_distance_3_and_13_correctable_cosets():
    ham = L.make_hamming()
    assert ham.min_distance == 3
    weights = sorted(bin(l).count("1") for l in ham.coset_leaders)
    assert weights == [0] + [1] * 12 + [2] * 3


def test_planted_feature_exactly_256_codewords_are_fully_neutral():
    ham = L.make_hamming()
    ex = R.exact_reference(ham)
    zeros = [g for g in range(4096) if ex["_reach"][g] == 0]
    assert len(zeros) == 256
    assert all(ex["_neutral"][g] == 12 for g in zeros)
    assert sorted(zeros) == sorted(L.codewords(L.HAMMING_ROWS))
    assert ex["reach_histogram"].get(0) == 256


def test_hamming_max_reach_is_at_most_11():
    ex = R.exact_reference(L.make_hamming())
    assert ex["max_reach"] <= 11
    assert ex["min_reach"] == 0


def _internal_degrees(dec, rule):
    nodes = set(H.preimage(dec, rule))
    return sorted(sum(1 for b in range(12) if g ^ (1 << b) in nodes) for g in nodes)


def test_hamming_preimage_is_one_connected_16_with_a_degree_12_center_direct_is_a_4_cube():
    # P3 AS PREREGISTERED ([13,1,1,1]) WAS FALSIFIED by this test on the first
    # run: the three weight-2 satellites c+e_a+e_b are adjacent to the ball's
    # surface points c+e_a and c+e_b, so the preimage is ONE component of 16.
    # The derivation error is in calibration/LEDGER.md. What holds: a center
    # adjacent to 12 of its 15 siblings; direct's cube has degree 4 everywhere.
    ham = L.make_hamming()
    for rule in (0, 30, 90, 110, 184, 255):
        assert L.preimage_components(ham, rule) == [16]
        assert L.preimage_components(H.direct, rule) == [16]
        assert _internal_degrees(ham, rule) == [1] * 8 + [2] * 5 + [3] * 2 + [12]
        assert _internal_degrees(H.direct, rule) == [4] * 16


def test_invariance_scrambling_hamming_preserves_its_adjacency_statistics():
    ham = L.make_hamming()
    exh = R.exact_reference(ham)
    exs = R.exact_reference(H.make_scrambled(ham, 3))
    assert exs["reach_histogram"] == exh["reach_histogram"]
    assert exs["mean_neutral"] == exh["mean_neutral"]


def test_spread_two_random_members_are_not_the_same_observation():
    e1 = R.exact_reference(L.make_random(1))
    e2 = R.exact_reference(L.make_random(2))
    assert (e1["reach_histogram"], e1["mean_neutral"]) != (e2["reach_histogram"], e2["mean_neutral"])


def test_determinism_hamming_table_digest_is_a_constant():
    a = H.check_exact(L.make_hamming())["table_sha256"]
    b = H.check_exact(L.make_lincode(L.HAMMING_ROWS, label="again"))["table_sha256"]
    assert a == b
