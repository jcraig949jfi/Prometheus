"""C1b assay switches (PREREG_PTE_C1b s5): they cannot move normal physics
or any C1 control, and each one changes exactly the carrier it names.
CPU only (dev fixtures run on hand plants; no specimen, no search)."""
from __future__ import annotations

import json

import numpy as np
import pytest

from prometheus.ananke.engine import Controls, World
from prometheus.ananke.physics import Physics
from prometheus.ananke.tests import golden_controls as gc
from prometheus.ananke.tests.test_conformance import (dense_schedule, forced_emitter_inputs,
                                                      random_physics)


def test_every_c1_control_reproduces_the_frozen_engine_bit_for_bit():
    """Golden digests were written from the engine as frozen for C1
    (commit 3451ae720, before any switch existed)."""
    gold = json.loads(gc.GOLDEN.read_text())
    now = gc.compute()
    assert set(now) == set(gold)
    bad = [k for k in gold if now[k] != gold[k]]
    assert not bad, bad[:5]


def test_golden_is_not_vacuous():
    """The golden comparison can fail: the controls it pins actually
    change state on these configs."""
    gold = json.loads(gc.GOLDEN.read_text())
    moved = {k.split(":", 1)[1] for k, v in gold.items()
             if v["digests"] != gold[k.split(":")[0] + ":none"]["digests"]}
    assert {"zero_comm", "reset_state_at", "drop_packets_at", "no_adapt"} <= moved, moved


def _run(ph, ctrl, seed=7, census=False, T=20, B=3):
    gen, ws, sense = forced_emitter_inputs(ph, B, T, seed)
    w = World(ph, gen, ws, device="cpu", ctrl=ctrl, schedule=dense_schedule(sense, B, ph.n_sites),
              census=census)
    w.run(T, graph=False)
    return w


PH = Physics(topology="ring", n_sites=12, radius=1, fanout=2, prog_len=6, plastic_route=1,
             setrule=1, rules=3, wimm=1, mut_site=0.2, e_income=3, e_max=1000, c_emit=2)


def test_census_is_read_only():
    a = _run(PH, Controls())
    b = _run(PH, Controls(), census=True)
    assert a.digest(per_world=True) == b.digest(per_world=True)
    assert int(b.tel["c_inflight_cnt"].abs().sum()) > 0


def test_default_reset_parts_is_c1_memory_ablation():
    a = _run(PH, Controls(reset_state_at=(5, 11)))
    b = _run(PH, Controls(reset_state_at=(5, 11), reset_parts=("S",)))
    assert a.digest(per_world=True) == b.digest(per_world=True)


@pytest.mark.parametrize("part,arr", [("S", "S"), ("inbox", "Acc_sum"), ("Kp", "Kp"),
                                      ("w", "w"), ("En", "E"), ("r", "r")])
def test_each_reset_part_touches_its_carrier_at_the_tick(part, arr):
    ph = PH.replace(update_mode="async", update_p=0.5)
    ref = _run(ph, Controls(), T=6)
    hit = _run(ph, Controls(reset_state_at=(5,), reset_parts=(part,)), T=6)
    others = [k for k in ref.state_arrays() if k not in (arr, "Acc_cnt" if part == "inbox" else arr)]
    for k in others:
        assert np.array_equal(ref.state_arrays()[k].numpy(), hit.state_arrays()[k].numpy()), (part, k)
    after = hit.state_arrays()[arr].numpy()
    want = {"S": 0, "inbox": 0, "Kp": 0, "w": 16, "En": ph.e_max}.get(part)
    if part == "r":
        assert np.array_equal(after, hit.r0.numpy())
    else:
        assert (after == want).all(), part


def test_flush_empties_every_slot_and_zero_comm_style_stats_unchanged():
    ref = _run(PH, Controls(), T=9)
    fl = _run(PH, Controls(flush_inflight_at=(8,)), T=9)
    assert int(fl.Mcnt.sum()) == 0 and int(fl.Msum.abs().sum()) == 0
    assert int(ref.Mcnt.sum()) > 0
    for k in ("S", "E", "r", "Kp", "w", "Acc_sum", "Acc_cnt"):
        assert np.array_equal(ref.state_arrays()[k].numpy(), fl.state_arrays()[k].numpy()), k


def test_freeze_rule_stops_rule_writes_only():
    def run(ctrl):
        B, T = 3, 20
        gen, ws, sense = forced_emitter_inputs(PH, B, T, 7)
        sense_reg = PH.n_read() - 3
        gen[:, :, 2] = (14, 0, sense_reg, 0, 0)          # SETRULE r := SENSE mod rules
        gen[:, :, 3] = (2, PH.state_dim + 7, sense_reg, sense_reg, 0)   # RVAL := 2*SENSE
        w = World(PH, gen, ws, device="cpu", ctrl=ctrl, census=True,
                  schedule=dense_schedule(sense, B, PH.n_sites))
        w.run(T, graph=False)
        return w
    base = run(Controls())
    fr = run(Controls(freeze_rule=True))
    assert int(base.tel["c_rule_changes"].sum()) > 0
    assert int(fr.tel["c_rule_changes"].sum()) == 0
    assert np.array_equal(fr.r.numpy(), fr.r0.numpy())
    # routing writes still happen under freeze_rule
    assert int(fr.stats["route_writes"].sum()) > 0
