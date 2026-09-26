"""AETH-03 scout kernels: the shared path is v1, and each variant changes one thing.

The baseline control comes first: `v1g` routes aeth01.v1 through the
variant module's own code and must equal the frozen reference
(`gpu_aeth01.gpu_step`) bit for bit, observer included. Only then does a
difference between a variant and v1 mean what the variant claims.

Each fixture is hand-worked on a tiny torus with perturbation,
maintenance and replenishment off, so the expected bytes follow from the
variant's one-sentence rule and nothing else.
"""

import os
import sys

import numpy as np
import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_AETHER = os.path.dirname(_HERE)
for _p in (_AETHER, os.path.join(_HERE, "reference")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import gpu_aeth01 as K                                   # noqa: E402
from observatory import aeth03_variants as V             # noqa: E402

QUIET = dict(write_cost=1, maintenance_cost=0, replenish_numer=0,
             replenish_amount=0, mut_numer=0)
LIVE = dict(write_cost=1, maintenance_cost=1,
            replenish_numer=int(round(0.125 * (1 << 32))), replenish_amount=8,
            mut_numer=int(round(0.1 * (1 << 32))))


def blank(h=5, w=5, energy=100):
    z = lambda: np.zeros((h, w), dtype=np.uint8)            # noqa: E731
    f = [z(), z(), z(), z(), z()]
    f[0][:] = 7                     # inert background opcode
    f[4][:] = energy
    return f


def run(variant, fields, tick=1, seed=0x5EED, par=QUIET, observer=None):
    h, w = fields[0].shape
    out = V.step(variant, H=h, W=w, seed=seed, tick=tick, opcode=fields[0],
                 arg0=fields[1], arg1=fields[2], payload=fields[3],
                 energy=fields[4], observer=observer, **par)
    return list(out[:5])


def soup(n, rng):
    f = [rng.integers(0, 256, size=(n, n), dtype=np.uint8) for _ in range(5)]
    f[0] = np.where(rng.random((n, n)) < 0.5, np.uint8(1), f[0]).astype(np.uint8)
    return f


@pytest.mark.parametrize("n,ticks,seed", [(8, 20, 1), (13, 15, 2), (32, 10, 3)])
def test_shared_path_is_v1_bit_for_bit(n, ticks, seed):
    rng = np.random.default_rng(seed)
    a = soup(n, rng)
    b = [x.copy() for x in a]
    for t in range(1, ticks + 1):
        obs_a, obs_b = [], []
        out_a = K.gpu_step(H=n, W=n, seed=seed, tick=t, opcode=a[0], arg0=a[1],
                           arg1=a[2], payload=a[3], energy=a[4],
                           observer=obs_a, **LIVE)
        b = run("v1g", b, tick=t, seed=seed, par=LIVE, observer=obs_b)
        a = list(out_a[:5])
        for fa, fb in zip(a, b):
            assert np.array_equal(fa, fb)
        for ea, eb in zip(obs_a, obs_b):
            for xa, xb in zip(ea, eb):
                assert np.array_equal(xa, xb)


def test_v1_label_delegates_to_frozen_kernel():
    rng = np.random.default_rng(9)
    f = soup(16, rng)
    got = run("v1", [x.copy() for x in f], par=LIVE)
    ref = K.gpu_step(H=16, W=16, seed=0x5EED, tick=1, opcode=f[0], arg0=f[1],
                     arg1=f[2], payload=f[3], energy=f[4], **LIVE)
    for g, r in zip(got, ref[:5]):
        assert np.array_equal(g, r)


@pytest.mark.parametrize("variant", ["add", "hys", "chg", "cnd", "str"])
def test_every_variant_differs_from_v1_on_a_live_soup(variant):
    # Guards against a variant whose switch is silently never taken.
    rng = np.random.default_rng(4)
    f = soup(48, rng)
    if variant == "cnd":
        f[0] = np.where(f[0] == 1, np.uint8(V.COND_OPCODE), f[0]).astype(np.uint8)
    a, b = [x.copy() for x in f], [x.copy() for x in f]
    diff = False
    for t in range(1, 6):
        a = run("v1", a, tick=t, par=LIVE)
        b = run(variant, b, tick=t, par=LIVE)
        diff = diff or any(not np.array_equal(x, y) for x, y in zip(a, b))
    assert diff


def writer(f, r, c, direction, field, payload, opcode=1, arg0_hi=0):
    f[0][r, c] = opcode
    f[1][r, c] = direction | (arg0_hi << 2)
    f[2][r, c] = field
    f[3][r, c] = payload


def test_add_combines_with_the_target_instead_of_replacing_it():
    f = blank()
    writer(f, 2, 2, K.EAST, K.PAYLOAD, payload=200)
    f[3][2, 3] = 100
    v1 = run("v1", [x.copy() for x in f])
    add = run("add", [x.copy() for x in f])
    assert v1[3][2, 3] == 200
    assert add[3][2, 3] == (100 + 200) % 256
    # A repeated identical write is a no-op under v1 and a change under add.
    again = run("add", add, tick=2)
    assert again[3][2, 3] == (44 + 200) % 256


def test_hys_prefers_the_contender_that_agrees_with_the_target():
    # Two emitters aim the same (target, field); one carries the target's
    # current value. Under v1 the hash decides tick by tick; under hys the
    # agreeing contender wins every tick.
    wins_v1, wins_hys = set(), set()
    for tick in range(1, 41):
        f = blank()
        writer(f, 1, 2, K.SOUTH, K.PAYLOAD, payload=55)    # agrees
        writer(f, 3, 2, K.NORTH, K.PAYLOAD, payload=99)    # differs
        f[3][2, 2] = 55
        wins_v1.add(int(run("v1", [x.copy() for x in f], tick=tick)[3][2, 2]))
        wins_hys.add(int(run("hys", [x.copy() for x in f], tick=tick)[3][2, 2]))
    assert wins_v1 == {55, 99}
    assert wins_hys == {55}


def test_chg_charges_only_writes_that_would_change_the_target():
    f = blank(energy=50)
    writer(f, 2, 2, K.EAST, K.PAYLOAD, payload=9)
    f[3][2, 3] = 9                                         # redundant write
    writer(f, 0, 0, K.SOUTH, K.PAYLOAD, payload=9)
    f[3][1, 0] = 8                                         # changing write
    v1 = run("v1", [x.copy() for x in f])
    chg = run("chg", [x.copy() for x in f])
    assert v1[4][2, 2] == 49 and chg[4][2, 2] == 50
    assert v1[4][0, 0] == 49 and chg[4][0, 0] == 49
    # Energy proposals always pay under chg.
    g = blank(energy=50)
    writer(g, 2, 2, K.EAST, K.ENERGY, payload=5)
    assert run("chg", [x.copy() for x in g])[4][2, 2] == run("v1", g)[4][2, 2]


def test_cnd_writes_only_when_the_target_matches_its_key():
    for current, key, expect_write in ((0b10, 0b10, True), (0b11, 0b10, False),
                                       (0b110, 0b10, True)):
        f = blank()
        writer(f, 2, 2, K.EAST, K.PAYLOAD, payload=77,
               opcode=V.COND_OPCODE, arg0_hi=key)
        f[3][2, 3] = current
        out = run("cnd", [x.copy() for x in f])
        assert (out[3][2, 3] == 77) == expect_write
        assert out[4][2, 2] == 99                          # pays either way
        # v1 treats 0x02 as inert: no write, no charge.
        v1 = run("v1", [x.copy() for x in f])
        assert v1[3][2, 3] == current and v1[4][2, 2] == 100


def test_str_rotates_direction_by_energy_quartile():
    for energy in (10, 70, 130, 200):
        f = blank(energy=0)
        writer(f, 2, 2, K.NORTH, K.PAYLOAD, payload=33)
        f[4][2, 2] = energy
        out = run("str", [x.copy() for x in f])
        direction = (K.NORTH + (energy >> 6)) % 4
        dr, dc = V._DIR_OFFSET[direction]
        assert out[3][2 + dr, 2 + dc] == 33
        for d2, (r2, c2) in V._DIR_OFFSET.items():
            if d2 != direction:
                assert out[3][2 + r2, 2 + c2] == 0


# ---------------------------------------------------------------- ladder 2

@pytest.mark.parametrize("variant", ["mov", "m4"])
def test_ladder2_variant_differs_from_v1_on_a_live_soup(variant):
    rng = np.random.default_rng(5)
    f = soup(48, rng)
    a, b = [x.copy() for x in f], [x.copy() for x in f]
    diff = False
    for t in range(1, 6):
        a = run("v1", a, tick=t, par=LIVE)
        b = run(variant, b, tick=t, par=LIVE)
        diff = diff or any(not np.array_equal(x, y) for x, y in zip(a, b))
    assert diff


def test_mov_clears_the_payload_of_a_winning_source_only():
    # Two emitters contest one target; the winner's payload moves (is
    # cleared), the loser keeps its payload. Run several ticks so both
    # winners occur.
    seen = set()
    for tick in range(1, 30):
        f = blank()
        writer(f, 1, 2, K.SOUTH, K.ARG1, payload=40)
        writer(f, 3, 2, K.NORTH, K.ARG1, payload=41)
        out = run("mov", [x.copy() for x in f], tick=tick)
        v1 = run("v1", [x.copy() for x in f], tick=tick)
        won = int(out[2][2, 2])
        assert won == int(v1[2][2, 2]) and won in (40, 41)
        winner, loser = ((1, 2), (3, 2)) if won == 40 else ((3, 2), (1, 2))
        assert out[3][winner] == 0
        assert out[3][loser] == (41 if won == 40 else 40)
        seen.add(won)
    assert seen == {40, 41}


def test_mov_keeps_an_incoming_payload_on_a_winning_source():
    # A wins into C's payload while B writes into A's payload: A's payload
    # becomes B's byte, not 0.
    f = blank()
    writer(f, 2, 1, K.EAST, K.PAYLOAD, payload=11)       # A -> (2, 2)
    writer(f, 2, 0, K.EAST, K.PAYLOAD, payload=22)       # B -> A
    out = run("mov", [x.copy() for x in f])
    assert out[3][2, 2] == 11
    assert out[3][2, 1] == 22
    assert out[3][2, 0] == 0                             # B won and is not written


def test_rcv_lets_a_written_inert_site_emit_for_one_tick():
    f = blank()
    writer(f, 2, 1, K.EAST, K.ARG1, payload=3)           # writes into (2, 2)
    f[0][2, 2] = 7                                       # inert opcode
    f[1][2, 2] = K.EAST                                  # aims at (2, 3)
    f[3][2, 2] = 99
    h, w = f[0].shape
    out = V.step("rcv", H=h, W=w, seed=1, tick=1, opcode=f[0], arg0=f[1],
                 arg1=f[2], payload=f[3], energy=f[4],
                 received=np.zeros((h, w), dtype=bool), **QUIET)
    got = list(out[:5])
    rec = out[5]["received"]
    assert rec[2, 2] and not rec[2, 3]
    assert got[2][2, 2] == 3                             # arg1 now selects PAYLOAD
    # Next tick the inert site emits its payload into (2, 3) because it
    # was written; plain v1 would leave (2, 3) alone.
    out2 = V.step("rcv", H=h, W=w, seed=1, tick=2, opcode=got[0], arg0=got[1],
                  arg1=got[2], payload=got[3], energy=got[4], received=rec,
                  **QUIET)
    assert out2[3][2, 3] == 99
    v1 = run("v1", [x.copy() for x in got], tick=2)
    assert v1[3][2, 3] == 0
    # ...and it paid WRITE_COST for doing so.
    assert out2[4][2, 2] == got[4][2, 2] - 1


def test_rcv_without_receipt_is_v1():
    rng = np.random.default_rng(6)
    f = soup(24, rng)
    h, w = f[0].shape
    out = V.step("rcv", H=h, W=w, seed=3, tick=1, opcode=f[0], arg0=f[1],
                 arg1=f[2], payload=f[3], energy=f[4],
                 received=np.zeros((h, w), dtype=bool), **LIVE)
    ref = run("v1", [x.copy() for x in f], seed=3, par=LIVE)
    for a, b in zip(out[:5], ref):
        assert np.array_equal(a, b)


def test_m4_low_bit_flips_of_arg1_leave_the_field_unchanged():
    for arg1 in range(256):
        field = (arg1 >> 3) % 5
        for bit in range(3):
            assert ((arg1 ^ (1 << bit)) >> 3) % 5 == field
    counts = np.bincount([((a >> 3) % 5) for a in range(256)], minlength=5)
    assert sorted(counts.tolist()) == [48, 48, 48, 56, 56]
    f = blank()
    writer(f, 2, 2, K.EAST, (K.PAYLOAD << 3), payload=77)  # field = PAYLOAD under m4
    assert run("m4", [x.copy() for x in f])[3][2, 3] == 77
