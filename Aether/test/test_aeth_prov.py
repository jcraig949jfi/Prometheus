"""prov0 qualification (V2-B DEV-1): the seven known-answer fixtures required by the operator directive of
2026-10-04, plus a rich-soup self-check across laws.

Each fixture is hand-worked on a small inert torus (opcode 7 everywhere, no maintenance or replenishment), so the
expected provenance follows from the law's one-sentence rule and nothing else.
"""
import os
import sys

import numpy as np
import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_AETHER = os.path.dirname(_HERE)
for _p in (_AETHER, os.path.join(_HERE, "reference"), _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import gpu_aeth01 as K                                   # noqa: E402
from observatory import aeth_prov as P                   # noqa: E402

QUIET = dict(write_cost=1, maintenance_cost=0, replenish_numer=0, replenish_amount=0, mut_numer=0, seed=1)
ALWAYS_MUT = dict(QUIET, mut_numer=1 << 32)
LIVE = dict(write_cost=1, maintenance_cost=1, replenish_numer=int(round(0.125 * (1 << 32))), replenish_amount=8,
            mut_numer=int(round(0.1 * (1 << 32))), seed=9)


def blank(n=7, energy=100):
    z = lambda: np.zeros((n, n), dtype=np.uint8)            # noqa: E731
    f = [z(), z(), z(), z(), z()]
    f[0][:] = 7
    f[4][:] = energy
    return f


def writer(f, rc, direction, payload, field=K.PAYLOAD, opcode=None):
    f[0][rc] = K.WRITE_OPCODE if opcode is None else opcode
    f[1][rc] = direction
    f[2][rc] = field
    f[3][rc] = payload


def node_at(pv, rc, field=3):
    return int(pv.cur[field][rc])


def test_1_direct_forwarding_fwd_relay_carries_the_origin_two_hops():
    f = blank()
    writer(f, (3, 1), K.EAST, 21)                           # A writes 21 into B's payload
    f[1][3, 2] = K.EAST; f[2][3, 2] = K.PAYLOAD             # B (inert) aims east at C when it relays
    _out, pv, _h = P.run("fwd", f, QUIET, ticks=2, track=[(3, 1, 3)])
    a0 = pv.origins[0][1]
    c = node_at(pv, (3, 3))
    assert int(pv.column("value")[c]) == 21
    assert a0 in pv.ancestry(c)                              # C's byte descends from A's payload
    assert pv.rung_profile(0)["max_distance"] == 2


def test_2_no_forwarding_v1_leaves_the_far_site_untouched():
    f = blank()
    writer(f, (3, 1), K.EAST, 21)
    f[1][3, 2] = K.EAST; f[2][3, 2] = K.PAYLOAD
    _out, pv, _h = P.run("v1", f, QUIET, ticks=2, track=[(3, 1, 3)])
    c = node_at(pv, (3, 3))
    assert int(pv.column("op")[c]) == P.OP_INIT and pv.ancestry(c) == set()
    assert pv.rung_profile(0)["max_distance"] == 1           # reaches B only, never C


def test_3_transformed_forwarding_add_keeps_ancestry_through_a_value_change():
    f = blank()
    writer(f, (3, 1), K.EAST, 21)
    f[3][3, 2] = 5                                           # B's payload before the write
    _out, pv, _h = P.run("add", f, QUIET, ticks=1, track=[(3, 1, 3)])
    b = node_at(pv, (3, 2))
    assert int(pv.column("value")[b]) == 26 and int(pv.column("op")[b]) == P.OP_ADD
    assert pv.origins[0][1] in pv.ancestry(b)
    assert pv.rung_profile(0)["transformed"] == 1            # descendant value 26 != origin value 21


def test_4_two_parent_composition_add_node_carries_both_lineages():
    f = blank()
    writer(f, (3, 1), K.EAST, 21)
    f[3][3, 2] = 5
    _out, pv, _h = P.run("add", f, QUIET, ticks=1, track=[(3, 1, 3), (3, 2, 3)])
    b = node_at(pv, (3, 2))
    anc = pv.ancestry(b)
    assert pv.origins[0][1] in anc and pv.origins[1][1] in anc
    assert pv.rung_profile(0)["composed"] == 1 and pv.rung_profile(1)["composed"] == 1


def test_5_perturbation_flags_the_node_keeps_the_parent_and_changes_the_value():
    f = blank()
    writer(f, (3, 1), K.EAST, 21)
    _out, pv, _h = P.run("v1", f, ALWAYS_MUT, ticks=1, track=[(3, 1, 3)])
    b = node_at(pv, (3, 2))
    assert int(pv.column("op")[b]) & P.OP_MUT
    assert pv.origins[0][1] in pv.ancestry(b)
    assert int(pv.column("value")[b]) != 21                  # one bit flipped
    assert bin(int(pv.column("value")[b]) ^ 21).count("1") == 1


def test_6_overwritten_ancestry_leaves_the_site():
    f = blank()
    writer(f, (3, 1), K.EAST, 21)
    f[3][3, 2] = 5
    _out, pv, _h = P.run("v1", f, QUIET, ticks=1, track=[(3, 2, 3)])   # track B's own original payload
    assert pv.rung_profile(0)["holders"] == 0                # replaced by A's copy: B's lineage is gone
    assert pv.origins[0][1] not in pv.ancestry(node_at(pv, (3, 2)))


def test_7_arbitration_only_the_winner_is_a_parent():
    f = blank()
    writer(f, (3, 1), K.EAST, 21)                            # A: west of B, aims east
    writer(f, (3, 3), K.WEST, 99)                            # E: east of B, aims west
    _out, pv, _h = P.run("v1", f, QUIET, ticks=1, track=[(3, 1, 3), (3, 3, 3)])
    b = node_at(pv, (3, 2))
    tgt = K.pack_coords_vec(np.array([3]), np.array([2]))
    pa = K.arbitration_priority_vec(QUIET["seed"], 1, tgt, 3, K.pack_coords_vec(np.array([3]), np.array([1])))[0]
    pe = K.arbitration_priority_vec(QUIET["seed"], 1, tgt, 3, K.pack_coords_vec(np.array([3]), np.array([3])))[0]
    winner, loser = (0, 1) if pa > pe else (1, 0)
    anc = pv.ancestry(b)
    assert pv.origins[winner][1] in anc and pv.origins[loser][1] not in anc
    assert int(pv.column("value")[b]) == (21 if winner == 0 else 99)


@pytest.mark.parametrize("variant", ["v1", "rcv", "fwd", "add", "rcv_add", "rcv_str", "rcv_adr", "rcv_sfx",
                                     "cnd", "str", "hys", "chg", "m4", "rcv_cnd"])
def test_rich_soup_self_check_zero_mismatches(variant):
    rng = np.random.default_rng(42)
    f = [rng.integers(0, 256, size=(32, 32), dtype=np.uint8) for _ in range(5)]
    f[0] = np.where(rng.random((32, 32)) < 0.5, np.uint8(1), f[0]).astype(np.uint8)
    P.run(variant, f, LIVE, ticks=40, track=[(5, 5, 3), (20, 20, 3)])   # raises ProvenanceMismatch on any drift


def test_unsupported_variant_is_refused():
    with pytest.raises(ValueError):
        P.Provenance("mov", blank())
