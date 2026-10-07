"""PROP01 known answers for the paired-world causal tracer (hand-built worlds, frozen aeth01.v1 law).

COPY_CHAIN (positive): writers at row 4, cols 1-4, all aimed EAST into the next site's payload. A payload difference
at col 1 must reach col 2 (gen 1), col 3 (gen 2), col 4 (gen 3), col 5 (gen 4) as CARRY, with no UNKNOWN parents,
and the divergence multiplies (all chain sites stay divergent).
CLAMP_B (positive counterfactual): clamping col 2 to CONTROL removes every downstream divergence (cols 3-5).
CLAMP_NON_ANCESTOR (negative counterfactual): clamping an off-chain site leaves the downstream divergence intact.
ISOLATED (negative): a payload difference on a non-WRITE site with no writers aimed at anything stays local.
"""

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "V2B", "PROP01"))
import prop01_run as P  # noqa: E402
import prop01_tree as T  # noqa: E402

n = 8
EAST = 1


def world(chain=True):
    s = [np.full((n, n), 9, dtype=np.uint8), np.zeros((n, n), np.uint8), np.zeros((n, n), np.uint8),
         np.zeros((n, n), np.uint8), np.full((n, n), 255, np.uint8)]
    if chain:
        for c in range(1, 5):
            s[0][4, c] = 1          # WRITE
            s[1][4, c] = EAST       # direction east
            s[2][4, c] = 3          # payload field
        s[3][4, 1] = 10
    return s


def site(r, c):
    return r * n + c


def run(**kw):
    return P.run_unit("cpu", "V1", 0, n, 0, 12, **kw)


def test_copy_chain_reaches_generation_4_as_carry():
    u = run(init=world(), origin=site(4, 1))
    tr = dict(zip(u["tree"]["site"], zip(u["tree"]["gen"], u["tree"]["type"], u["tree"]["parent"])))
    for c, g in ((2, 1), (3, 2), (4, 3), (5, 4)):
        assert tr[site(4, c)][0] == g, (c, tr.get(site(4, c)))
        assert tr[site(4, c)][1] == 2                       # CARRY
        assert tr[site(4, c)][2] == site(4, c - 1)          # parent = upstream neighbour
    assert u["unknown_sites"] == 0 and u["max_gen"] == 4
    assert max(r["div_sites"] for r in u["series"]) >= 5    # divergence multiplies along the chain


def test_clamp_b_removes_downstream():
    base = run(init=world(), origin=site(4, 1))
    b = site(4, 2)
    tick = dict(zip(base["tree"]["site"], base["tree"]["ftick"]))[b]
    u = run(init=world(), origin=site(4, 1), cut_site=b, cut_tick=tick)
    cut = set(u["cut"]["cut_ever_sites"])
    desc = T.descendants(base["tree"], b)
    assert desc == {site(4, 3), site(4, 4), site(4, 5)}
    assert not (desc & cut)                                 # every descendant of B disappears


def test_clamp_non_ancestor_leaves_downstream():
    base = run(init=world(), origin=site(4, 1))
    u = run(init=world(), origin=site(4, 1), cut_site=site(1, 1), cut_tick=1)
    cut = set(u["cut"]["cut_ever_sites"])
    assert {site(4, 3), site(4, 4), site(4, 5)} <= cut


def test_isolated_difference_stays_local():
    u = run(init=world(chain=False), origin=site(2, 2))
    assert u["ever_sites"] == 1 and u["max_gen"] == 0
