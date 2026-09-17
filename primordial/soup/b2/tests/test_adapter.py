"""E-R15-2: graphworld_b2 controllable adapter -- semantics, form equality, skip-mutation cheat, controllability smoke."""
from __future__ import annotations

import numpy as np
import pytest

from primordial.soup.b2 import adapter as AD
from primordial.soup.b2.graphworld import Spec, step_cell
from primordial.soup.b2.oracle import specs


def _cypher_up():
    try:
        from falkordb import FalkorDB
        g = FalkorDB(host=AD.CY_HOST, port=AD.CY_PORT).select_graph("e_b2_probe")
        g.query("RETURN 1")
        return True
    except Exception:
        return False


def test_action_semantics_abstain_moves_and_mod8():
    assert AD.action_dir(0) is None and AD.action_dir(8) is None and AD.action_dir(-8) is None
    assert [AD.action_dir(a) for a in range(1, 8)] == [0, 1, 2, 3, 0, 1, 2]
    s = Spec(L=6, n_pred=1, n_prey=2, n_food=1, ticks=3, seed=0)
    w = AD.RefB2(s, init={0: 0, 1: 14, 2: 21, 3: 35})        # predator far from both prey, food elsewhere
    w.phase12()
    w.phase34([0, 2])                                          # prey 1 abstains, prey 2 steps +y
    assert w.cell[1] == 14 and w.cell[2] == step_cell(6, 21, 1) and w.cell[0] == step_cell(6, 0, 0)
    assert w.charge == {1: 1, 2: 1} and w.moving_actions == 1
    c = AD.RefB2(s, cheat="skip_mutation", init={0: 0, 1: 14, 2: 21, 3: 35})
    c.phase12()
    c.phase34([0, 2])
    assert c.cell[2] == 21 and c.moving_actions == 1          # the action was read; the mutation was skipped


def test_observation_layout_masks_and_food_credit_to_lowest_id():
    s = Spec(L=6, n_pred=1, n_prey=2, n_food=2, ticks=4, seed=0)
    # cell c = y*6 + x. prey 1 and prey 2 share cell 14 with food 3 -> food credited to prey 1 (lowest id).
    # food 4 sits at +x of 14 (15); predator 0 at -y of 14 (8) -> dir 3.
    w = AD.RefB2(s, init={0: 8, 1: 14, 2: 14, 3: 14, 4: 15})
    w.phase12()
    assert 3 not in w.cell and w.charge == {1: AD.FOOD_CREDIT, 2: 0}
    o = w.observe()
    assert o.dtype == np.uint16 and o.shape == (2, AD.W_OBS)
    assert list(o[0]) == [1, 14, 1 << 3, 1 << 0, 1 << AD.SAME, 0, 1, AD.FOOD_CREDIT]
    assert list(o[1]) == [1, 14, 1 << 3, 1 << 0, 1 << AD.SAME, 0, 1, 0]
    assert AD.forager(o, 0).tolist() == [1, 1]                  # food at +x (bit 0) -> action 1


@pytest.mark.parametrize("j", range(6))
def test_graphblas_equals_reference_on_random_and_policy_streams(j):
    s = specs(6)[j]
    table = AD.random_table(s, [1501, j])
    for pol in (AD.table_policy(table), AD.forager):
        ref, gb = AD.episode("ref", s, pol), AD.episode("gb", s, pol)
        assert gb == ref


def test_skip_mutation_cheat_fails_the_hash_wherever_a_live_prey_moved():
    for j, s in enumerate(specs(6)):
        pol = AD.table_policy(AD.random_table(s, [1501, j]))
        ref = AD.episode("ref", s, pol)
        assert ref["moving_actions"] > 0
        for form in ("ref", "gb"):
            assert AD.episode(form, s, pol, cheat="skip_mutation")["hash"] != ref["hash"]


@pytest.mark.skipif(not _cypher_up(), reason="FalkorDB substrate not reachable")
def test_cypher_equals_reference_and_cheat_fails():
    for j, s in enumerate(specs(2)):
        pol = AD.table_policy(AD.random_table(s, [1501, j]))
        ref = AD.episode("ref", s, pol)
        assert AD.episode("cy", s, pol) == ref
        assert AD.episode("cy", s, AD.forager) == AD.episode("ref", s, AD.forager)
        assert AD.episode("cy", s, pol, cheat="skip_mutation")["hash"] != ref["hash"]


def test_rollout_is_deterministic_and_planted_world_is_controllable_smoke():
    seeds = range(30000, 30016)
    fg = AD.rollout(AD.planted, AD.forager, seeds)
    assert np.array_equal(fg, AD.rollout(AD.planted, AD.forager, seeds))
    ab = AD.rollout(AD.planted, AD.abstain, seeds)
    assert np.median(fg) > np.median(ab)                        # smoke only; the oracle is the worker job (O3)
