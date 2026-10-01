"""[COPY of W2-C/tests/test_guards.py run against the PATCHED W2-O/pte_mut; HERE.parent = W2-O.] Each proposed guard must stay silent on a clean run and FIRE on the corruption it targets
(guard_that_cannot_fire: ask what input makes each assertion fail). Tiny worlds, CPU, ~20 s."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from pte_mut import env as _env  # noqa: E402,F401

import pytest  # noqa: E402

from pte_mut import fixtures as F, guards as G, operators as O  # noqa: E402
from prometheus.ananke import assays, envs  # noqa: E402
from prometheus.ananke.engine import Controls  # noqa: E402

CAT = O.catalogue()
SEEDS = assays.world_seeds(4242, 16)


def _fx():
    f = F.relay64()
    f.env = envs.EnvSpec(family="RELAY", d=2, delta=8, trials=4)
    return f


def mini_protocol(f):
    """normal + zero_comm on the same seeds (the held block's shape), single genome."""
    assays.evaluate(f.ph, f.genome[None], f.env, SEEDS, device="cpu")
    assays.evaluate(f.ph, f.genome[None], f.env, SEEDS, ctrl=Controls(zero_comm=True), device="cpu")


def run(op):
    f = _fx()
    with G.guarded(op) as g:
        mini_protocol(f)
        g.champion = f.genome
        return set(g.check())


CLEAN_ADVISORY = {"G0_DEGENERATE_CONTROL"}     # zero_comm is forced at .5 for a relay: visible on the baseline


def test_clean_run_raises_only_the_advisory():
    assert run(None) == CLEAN_ADVISORY


@pytest.mark.parametrize("op,guard", [
    ("alter_timing", "G1_PHYSICS_PROVENANCE"),
    ("silent_sensors", "G3_SENSE_LIVE"),
    ("drop_mirror", "G4_MIRROR_INVARIANT"),
    ("swap_labels", "G5_CONDITION_PROVENANCE"),
    ("duplicate_condition", "G5_CONDITION_PROVENANCE"),
    ("control_ignored", "G5_CONDITION_PROVENANCE"),
    ("control_ignored", "G6_CONTROL_DISTINGUISHABLE"),
    ("permute_seeds", "G7_CRN_PAIRING"),
    ("sever_search_ruler", "G9_GENOME_PROVENANCE"),
    ("invert_sign", "G10_SCORER_SELFTEST"),
    ("disable_channel", "G11_TRANSPORT_LIVE"),
    ("freeze_state", "G12_STATE_LIVE"),
])
def test_guard_fires_on_its_corruption(op, guard):
    assert guard in run(CAT[op])


def test_reverse_edges_fires_topology_guard_on_a_directed_graph():
    f = F.random_dir()
    f.env = envs.EnvSpec(family="RELAY", d=2, delta=8, trials=4)
    with G.guarded(CAT["reverse_edges"]) as g:
        mini_protocol(f)
        assert "G2_TOPOLOGY_PROVENANCE" in g.check()


def test_held_disjoint_fires_when_selection_and_held_share_worlds():
    f = _fx()
    with G.guarded(None) as g:
        assays.evaluate(f.ph, f.genome[None].repeat(2, 0), f.env, SEEDS, device="cpu")   # selection
        assays.evaluate(f.ph, f.genome[None], f.env, SEEDS, device="cpu")                # 'held'
        assert "G8_HELD_DISJOINT" in g.check()
    with G.guarded(None) as g:
        assays.evaluate(f.ph, f.genome[None].repeat(2, 0), f.env, assays.world_seeds(1, 8), device="cpu")
        assays.evaluate(f.ph, f.genome[None], f.env, SEEDS, device="cpu")
        assert "G8_HELD_DISJOINT" not in g.check()
