"""Regression test for patches/g12_exempt_controls.NEUTRAL.diff.

G12_STATE_LIVE must judge the NORMAL arm only. On current W2-C code it fires on the zero_comm World of a
recorded C1 SIGNAL cell (a false 'broken experiment' alarm); with the patch it does not. It must still fire on
a normal arm whose readout genuinely goes dead (recorded NULL 89bd6fdb: energy death at tick ~11).

Select the implementation under test with W2O_GUARDS=W2-C (current code: test 1 FAILS) or W2O_GUARDS=W2-O
(patched copy, default: all pass). CPU, eager, ~40 s."""
from __future__ import annotations

import gzip
import json
import os
import pathlib
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ.setdefault("PTE_MUT_THREADS", "2")
HERE = pathlib.Path(__file__).resolve().parent
WAVE2 = HERE.parents[1]
sys.path.insert(0, str(WAVE2 / os.environ.get("W2O_GUARDS", "W2-O")))

from pte_mut import env as _env  # noqa: E402,F401
from pte_mut import guards as G  # noqa: E402

import numpy as np  # noqa: E402
from prometheus.ananke import assays, envs, search  # noqa: E402
from prometheus.ananke.engine import Controls  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402
from prometheus.ananke.rng import H_int  # noqa: E402

ROWS = _env.ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"


def _row(cid):
    for line in gzip.open(ROWS, "rt"):
        r = json.loads(line)
        if r["cell_id"] == cid:
            return r
    raise KeyError(cid)


def _held(cid, arms=("normal", "zero_comm")):
    r = _row(cid)
    ph = Physics.from_dict(r["physics"]).validate()
    env = envs.EnvSpec(**r["env"])
    sp = search.SearchSpec(**r["search"])
    champ = np.asarray(r["result"]["champion"])
    hs = assays.world_seeds(H_int(r["search_seed"], search.HELD_NS), sp.M_held)
    with G.guarded() as g:
        g.champion = champ
        if "normal" in arms:
            rh = assays.evaluate(ph, champ[None], env, hs, device="cpu", graph=False)
            # known-answer: the recorded held accuracy reproduces exactly (otherwise the test is meaningless)
            m = assays.pair_ci(rh.pair_acc()[0])[0]
            assert abs(m - r["result"]["held"]["acc"]) < 1e-12
        if "zero_comm" in arms:
            assays.evaluate(ph, champ[None], env, hs, ctrl=Controls(zero_comm=True), device="cpu", graph=False)
        return set(g.check()), r


def test_g12_silent_on_zero_comm_arm_of_recorded_signal_cell():
    alarms, r = _held("1d88af703d4dab91")          # RELAY smallworld, recorded SIGNAL, held .681
    assert r["labels"]["SIGNAL"] is True
    assert "G12_STATE_LIVE" not in alarms, alarms


def test_g12_still_fires_on_a_dead_normal_arm():
    alarms, r = _held("89bd6fdb1b66ce96", arms=("normal",))   # recorded NULL; emissions stop, E -> 0
    assert "G12_STATE_LIVE" in alarms, alarms
