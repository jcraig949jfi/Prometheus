"""C2BX / PTE-C2C known-answer tests (CPU). Run: python -m pytest roles/Ananke/pte/c2c/test_c2c.py -q -p no:cacheprovider"""
import dataclasses
import os
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402

import c2c_common as X  # noqa: E402
B = X.B; C = X.C
from prometheus.ananke import search  # noqa: E402

PH = C.Physics.from_dict(dict(C.Physics().to_dict(), prog_len=16, rules=1, state_dim=2, payload_width=1,
                              channels=1)).validate()
SP = search.SearchSpec(pop=96, M=8, gens=36)


def test_block_move_kinds_lengths_and_tags():
    seen = set()
    for s in range(400):
        g = np.random.default_rng(s)
        a = search.random_genomes(g, 1, PH)[0]
        t = np.zeros(a.shape[:2], bool); t[0, :8] = True
        c, tt, (r, b, st, kind) = X.block_move(g, a, t)
        seen.add((b, kind))
        assert b in X.BLOCK_LENGTHS and 0 <= st <= a.shape[1] - b
        if kind == 1:          # MOVE: a permutation of the same lines, tags travel with lines
            assert sorted(map(tuple, c[0])) == sorted(map(tuple, a[0])) and tt.sum() == t.sum()
        if kind == 2:          # REPLACE: b lines changed source, tags False there
            assert (~tt[0, st:st + b]).all()
        if kind == 0:          # DUPLICATE: the destination equals the source block
            assert (c != a).any(-1).sum() <= b
    assert {k for _, k in seen} == {0, 1, 2} and {b for b, _ in seen} == set(X.BLOCK_LENGTHS)


def test_opb_is_op0_then_optional_block_move():
    """The OPB offspring before its block step is exactly the OP0 offspring (same RNG prefix)."""
    for s in range(100):
        g1, g2 = np.random.default_rng(s), np.random.default_rng(s)
        a = search.random_genomes(np.random.default_rng(999), 1, PH)[0]
        t = np.ones(a.shape[:2], bool)
        c1, _ = B.mutate_tagged(g1, a, t, SP)
        c2, _ = X.mutate_opb(g2, a, t, SP)
        u = g1.random()                          # the draw OPB uses for its block decision
        if u >= X.P_BLOCK:
            assert np.array_equal(c1, c2)


def test_block_operator_is_content_blind():
    """Same RNG state -> same (rule, length, start, kind) regardless of genome content."""
    for s in range(50):
        a = search.random_genomes(np.random.default_rng(1), 1, PH)[0]
        b = search.random_genomes(np.random.default_rng(2), 1, PH)[0]
        t = np.zeros(a.shape[:2], bool)
        _, _, ia = X.block_move(np.random.default_rng(s), a, t)
        _, _, ib = X.block_move(np.random.default_rng(s), b, t)
        assert ia == ib


def test_graded_stone_rule():
    plant = C.PLANTS["FLIP"]["P_FLIP"](PH)
    seq = iter([("TRUE", .9, .95), ("FALSE", .55, .6), ("INDETERMINATE", .7, .78), ("FALSE", .7, .76),
                ("FALSE", .65, .72)])
    g, att = X.graded_stone(PH, None, plant, 31, 0, score=lambda x: next(seq))
    assert [a["qualified"] for a in att] == [False, False, False, False, True] and att[-1]["k"] == 1
    assert int((g != plant).sum()) == 1
    g2, e2 = B.k_edit(plant, 1, np.random.default_rng(C.H_int(X.C2C_NS, X.STONE_KEY, 31, 0, 4)))
    assert np.array_equal(g, g2)
    g3, att3 = X.graded_stone(PH, None, plant, 31, 1, score=lambda x: ("FALSE", .5, .55))
    assert g3 is None and len(att3) == X.MAX_STONE_ATTEMPTS


def test_fresh_seeds():
    for ck in (1, 99, 12345):
        s = {X.search_seed(ck, i) for i in range(8)}
        assert not s & {C.search_seed(ck, i) for i in range(12)} and len(s) == 8
