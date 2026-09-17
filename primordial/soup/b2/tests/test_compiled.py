"""E-R6-2: compiled/batched B2 rollout == adapter.RefB2 (hash, charges, moving actions), cheat included."""
from __future__ import annotations

import numpy as np
import pytest

from primordial.soup.b2 import adapter as AD
from primordial.soup.b2 import compiled as CB
from primordial.soup.b2.oracle import specs


def _per_episode(policy):
    return lambda obs, t: np.stack([policy(o, t) for o in obs])


@pytest.mark.parametrize("j", range(6))
def test_table_and_cheat_equal_reference(j):
    s = specs(6)[j]
    table = AD.random_table(s, [1501, j])
    ref = AD.episode("ref", s, AD.table_policy(table))
    got = CB.run_table(s, [s.seed], table, record=True)
    assert got["hashes"][0] == ref["hash"] and got["charges"][0].tolist() == ref["charges"]
    assert int(got["moving_actions"][0]) == ref["moving_actions"] > 0
    ch = CB.run_table(s, [s.seed], table, cheat="skip_mutation", record=True)
    assert ch["hashes"][0] == AD.episode("ref", s, AD.table_policy(table), cheat="skip_mutation")["hash"]
    assert ch["hashes"][0] != ref["hash"]


@pytest.mark.parametrize("j", range(4))
def test_forager_through_python_batch_and_linear_equal_reference(j):
    s = specs(4)[j]
    ref = AD.episode("ref", s, AD.forager)
    got = CB.run_policy(s, [s.seed], _per_episode(AD.forager), record=True)
    assert got["hashes"][0] == ref["hash"] and got["charges"][0].tolist() == ref["charges"]
    W, b = CB.random_linear(1, [1601, j])
    ref = AD.episode("ref", s, CB.linear_ref_policy(W, b))
    got = CB.run_linear(s, [s.seed], W, b, record=True)
    assert got["hashes"][0] == ref["hash"] and got["charges"][0].tolist() == ref["charges"]


def test_batch_of_seeds_and_genomes_equal_per_episode_reference():
    seeds = list(range(30000, 30012))
    W, b = CB.random_linear(3, [1602])
    goe = np.arange(len(seeds)) % 3
    got = CB.run_linear(AD.planted(0), seeds, W, b, goe, record=True)
    tables = np.stack([AD.random_table(AD.planted(sd), [1502, sd]) for sd in seeds])
    tab = CB.run_table(AD.planted(0), seeds, tables, record=True)
    for e, sd in enumerate(seeds):
        ref = AD.episode("ref", AD.planted(sd), CB.linear_ref_policy(W, b, int(goe[e])))
        assert got["hashes"][e] == ref["hash"] and int(got["charge"][e]) == ref["charge"]
        ref = AD.episode("ref", AD.planted(sd), AD.table_policy(tables[e]))
        assert tab["hashes"][e] == ref["hash"]


def test_observations_equal_reference_every_tick():
    s = specs(3)[2]
    table = AD.random_table(s, [1503])
    w = AD.RefB2(s)
    bt = CB.Batch(s, [s.seed])
    for t in range(s.ticks):
        w.phase12()
        assert np.array_equal(bt.observe()[0], w.observe())
        w.phase34(table[t])
        bt.step(table[t][None])


def test_digest_detects_a_planted_kernel_defect():
    s = specs(1)[0]
    table = AD.random_table(s, [1501, 0])
    bt = CB.Batch(s, [s.seed], record=True)
    for t in range(s.ticks):
        bt.observe()
        bt.step(table[t][None])
    ref = AD.episode("ref", s, AD.table_policy(table))["hash"]
    assert CB.digest(s, bt.rc[0], bt.ra[0], bt.rch[0]) == ref
    for field in ("rc", "ra", "rch"):                                    # one recorded value off -> the hash moves
        arr = getattr(bt, field)[0].copy()
        t, i = s.ticks // 2, 0
        arr[t, i] = arr[t, i] + 1 if arr[t, i] >= 0 else 0
        args = {"rc": bt.rc[0], "ra": bt.ra[0], "rch": bt.rch[0], field: arr}
        assert CB.digest(s, args["rc"], args["ra"], args["rch"]) != ref
