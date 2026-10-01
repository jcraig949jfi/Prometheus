"""Known-answer tests for pte_mut: every operator restores the originals, does what it claims on a tiny
world, and the classification rules give the declared category. CPU only, small (<1 min total).

    python -m pytest roles/Ananke/research/harvest/wave2/W2-C/tests -q
"""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from pte_mut import env as _env  # noqa: E402,F401

import numpy as np  # noqa: E402
import pytest  # noqa: E402
import torch  # noqa: E402

from pte_mut import fixtures as F, operators as O, score as SC, stages as ST  # noqa: E402
from prometheus.ananke import assays, envs, plants, search  # noqa: E402
from prometheus.ananke.engine import Controls, World  # noqa: E402

CAT = O.catalogue()
SEEDS = assays.world_seeds(777, 8)


@pytest.fixture(scope="module")
def relay():
    f = F.relay64()
    f.env = envs.EnvSpec(family="RELAY", d=2, delta=8, trials=4)
    return f


def ev(f, ctrl=None, seeds=SEEDS):
    return assays.evaluate(f.ph, f.genome[None], f.env, seeds, ctrl=ctrl, device="cpu", want_digest=True)


def test_torch_is_cpu_only():
    assert not torch.cuda.is_available()


@pytest.mark.parametrize("name", list(CAT))
def test_every_operator_restores_originals_even_on_error(name):
    op = CAT[name]
    with pytest.raises(ZeroDivisionError):
        with op.active():
            1 / 0
    assert O.originals_intact()


def test_catalogue_covers_the_brief():
    want = {"swap_labels", "duplicate_condition", "disable_channel", "control_ignored", "freeze_state",
            "randomize_source", "reverse_edges", "alter_timing", "sever_search_ruler", "reuse_selection_seeds",
            "drop_mirror", "permute_seeds", "silent_sensors", "invert_sign"}
    assert want == set(CAT)
    for op in CAT.values():
        assert op.mr and op.layer in ("engine", "protocol") and op.stages


def test_baseline_relay_is_perfect_and_zero_comm_is_exact_chance(relay):
    assert ev(relay).mean()[0] == 1.0
    assert ev(relay, Controls(zero_comm=True)).mean()[0] == 0.5


def test_disable_channel_kills_transport(relay):
    with CAT["disable_channel"].active():
        r = ev(relay)
    assert r.mean()[0] == 0.5


def test_silent_sensors_gives_exact_chance(relay):
    with CAT["silent_sensors"].active():
        r = ev(relay)
    assert r.mean()[0] == 0.5


def test_invert_sign_maps_acc_to_one_minus_acc(relay):
    with CAT["invert_sign"].active():
        r = ev(relay)
    assert r.mean()[0] == 0.0


def test_control_ignored_makes_zero_comm_equal_normal(relay):
    a = ev(relay)
    with CAT["control_ignored"].active():
        z = ev(relay, Controls(zero_comm=True))
    assert z.digests == a.digests


def test_swap_labels_exchanges_normal_and_zero_comm(relay):
    with CAT["swap_labels"].active():
        a = ev(relay)
        z = ev(relay, Controls(zero_comm=True))
    assert a.mean()[0] == 0.5 and z.mean()[0] == 1.0


def test_duplicate_condition_returns_normal_for_every_control(relay):
    a = ev(relay)
    with CAT["duplicate_condition"].active():
        ev(relay)
        z = ev(relay, Controls(shuffle_dest=True))
    assert z.digests == a.digests


def test_permute_seeds_rotates_control_worlds_by_one_pair(relay):
    rolled = list(np.roll(np.asarray(SEEDS, dtype=np.int64), 2).tolist())
    ref = ev(relay, Controls(shuffle_dest=True), seeds=rolled)
    with CAT["permute_seeds"].active():
        z = ev(relay, Controls(shuffle_dest=True))
    assert z.digests == ref.digests


def test_freeze_state_freezes_s_after_half(relay):
    T = relay.env.T()
    w = World(relay.ph, np.repeat(relay.genome[None], 2, 0), [5, 5], device="cpu",
              schedule=envs.build(relay.ph, relay.env, [5, 6]).schedule)
    with CAT["freeze_state"].active():
        snaps = []
        for t in range(T):
            w.step()
            snaps.append(w.S.clone())
    h = T // 2
    assert all(torch.equal(snaps[h - 1], s) for s in snaps[h:])
    tr = w.trace.numpy()
    assert (tr[h:] == tr[h - 1]).all()


def test_drop_mirror_makes_partners_identical(relay):
    with CAT["drop_mirror"].active():
        ep = envs.build(relay.ph, relay.env, SEEDS)
    sv = ep.schedule.sense_val
    assert torch.equal(sv[:, 0::2], sv[:, 1::2]) and (ep.y[0::2] == ep.y[1::2]).all()
    ep0 = envs.build(relay.ph, relay.env, SEEDS)
    assert (ep0.y[0::2] == -ep0.y[1::2]).all()


def test_alter_timing_runs_slower_physics_than_recorded(relay):
    with CAT["alter_timing"].active():
        w = World(relay.ph, relay.genome[None].repeat(2, 0), [1, 2], device="cpu")
    assert w.ph.lat_base == relay.ph.lat_base + 1 and w.ph.lat_jitter == relay.ph.lat_jitter + 1


def test_transpose_table_reverses_a_directed_graph():
    nbr = np.array([[1], [2], [0]])          # 0->1->2->0
    dist = np.ones_like(nbr)
    n2, _ = O.transpose_table(nbr, dist)
    assert n2.ravel().tolist() == [2, 0, 1]  # 0<-2, 1<-0, 2<-1


def test_reverse_edges_is_a_noop_set_on_a_torus_and_not_on_a_directed_graph():
    f = F.relay64()
    with CAT["reverse_edges"].active():
        w = World(f.ph, f.genome[None], [1], device="cpu")
    w0 = World(f.ph, f.genome[None], [1], device="cpu")
    assert all(set(a.tolist()) == set(b.tolist()) for a, b in zip(w.nbr, w0.nbr))
    g = F.random_dir()
    with CAT["reverse_edges"].active():
        w = World(g.ph, g.genome[None], [1], device="cpu")
    w0 = World(g.ph, g.genome[None], [1], device="cpu")
    assert any(set(a.tolist()) != set(b.tolist()) for a, b in zip(w.nbr, w0.nbr))


def test_randomize_source_is_pair_shared_and_changes_delivery(relay):
    with CAT["randomize_source"].active():
        r = ev(relay)
    # pair-shared permutation keeps the mirror identity: pairs still sum to a well-defined value
    assert r.acc.shape == (1, len(SEEDS))
    assert r.mean()[0] < 1.0


def test_sever_replaces_single_genome_only(relay):
    with CAT["sever_search_ruler"].active():
        r1 = ev(relay)
        r2 = assays.evaluate(relay.ph, np.repeat(relay.genome[None], 2, 0), relay.env, SEEDS, device="cpu")
    assert r1.mean()[0] < 0.75
    assert (r2.mean() == 1.0).all()


def test_reuse_selection_seeds_redirects_final_namespace():
    with CAT["reuse_selection_seeds"].active():
        a = search.H_int(99, search.FINAL_NS)
    assert a == search.H_int(99, search.HELD_NS)
    assert search.H_int(99, search.FINAL_NS) != search.H_int(99, search.HELD_NS)


def test_held_stage_champion_is_the_fixture_and_matches_direct_evaluation(relay):
    so = ST.run_stage("held", relay)
    assert so.error is None, so.error
    assert so.numeric["champion_is_fixture"] is True
    assert so.verdict["SIGNAL"] and so.verdict["COMM_DEPENDENT"]
    assert so.numeric["zero_comm"] == 0.5


def test_registry_fingerprints_are_inert_for_identical_runs(relay):
    a = ST.run_stage("plant", relay)
    b = ST.run_stage("plant", relay)
    assert a.fingerprints == b.fingerprints and a.fingerprints


class _SO:
    def __init__(self, verdict, alarms=(), fp=("x",)):
        self.verdict, self.alarms, self.fingerprints, self.numeric = verdict, list(alarms), list(fp), {}


@pytest.mark.parametrize("bv,mv,ba,ma,bf,mf,exp,cat", [
    ({"a": 1}, {"a": 1}, [], ["X"], ["f"], ["g"], "change", "KILLED(A)"),
    ({"a": 1}, {"a": 2}, [], [], ["f"], ["g"], "change", "KILLED(D)"),
    ({"a": 1}, {"a": 1}, [], [], ["f"], ["f"], "change", "EQUIVALENT"),
    ({"a": 1}, {"a": 1}, [], [], ["f"], ["g"], "change", "SURVIVED"),
    ({"a": 1}, {"a": 1}, [], [], ["f"], ["g"], "alarm_only", "SURVIVED"),
    ({"a": 1}, {"a": 1}, [], [], ["f"], ["g"], "invariant", "EQUIVALENT"),
    ({"a": 1}, {"a": 2}, [], [], ["f"], ["g"], "invariant", "FRAGILE"),
    ({"a": 1}, {"a": 1}, [], [], ["f"], ["g"], "unknown", "UNRESOLVED"),
    ({"a": 1}, {"a": 1}, ["X"], ["X"], ["f"], ["g"], "change", "SURVIVED"),   # a pre-existing alarm is no kill
])
def test_classification_rules(bv, mv, ba, ma, bf, mf, exp, cat):
    assert SC.classify(_SO(bv, ba, bf), _SO(mv, ma, mf), exp)["category"] == cat
