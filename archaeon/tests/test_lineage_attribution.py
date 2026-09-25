"""Phase A (operator directive 2026-09-24): the ten required genetic-attribution regression tests + fast-path equivalence."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from archaeon.z80atlas import vm, tasks as T
from archaeon.z80atlas.vm import I
from archaeon.envgate import mechanism as M1
from archaeon.lineage import core as LC
from archaeon.lineage.taint_vm import execute_taint

REPO = Path(__file__).resolve().parents[2]
REPL = T.pad(T.replicator(True), 32)                                                   # hand-written ungated vmcopy copier (a ruler)
RESIDENT15 = bytes.fromhex("c180094094938d528ef73c4ab400de8e7eb7a99cab37f38650832a8d607194a5")  # ENVGATE-01 block-15 U resident (EXACT_UNGATED)
HOST15 = bytes.fromhex("0514643bfb639dee3e6ba2e6bcdd82231909c06b15333d2b273cd63549a8ef09")     # an INERT block-15 founder that hosts it (all 256 inputs)


def _world():
    return LC.World("t", 4, ("t.world", 0), ("t.mut", 0), inputs=lambda w, c, e: [(0,)] * 3)


def _host_input(host, resident):
    for x in range(256):
        r = vm.execute(host, resident, (x,), LC.STEP_CAP, True, -1.0)
        if sum(r["nbr_mask"]) / 32 >= 0.9 and r["nbr_window"] == resident: return x, r
    raise AssertionError("fixture host never emits the resident")


def _birth(w, i, j, x):
    nbr = w.genomes[j] if w.genomes[j] is not None else LC.ZERO
    r = vm.execute(w.genomes[i], nbr, (x,), LC.STEP_CAP, True, -1.0)
    assert sum(r["nbr_mask"]) / 32 >= 0.9
    w._birth(i, j, r["nbr_window"], r, nbr, (x,), 1)
    return w.events[-1]


def test_01_self_copy_executor_is_template_is_genetic_ancestor():
    w = _world(); g = w.insert_ecology(0, REPL, 0, "random_inflow")
    ev = _birth(w, 0, 1, 0)
    assert ev["mechanism"] == "SELF_COPY" and ev["executed_material"] == "self"
    assert ev["executor_glin"] == ev["template_glin"] == ev["child_glin"] == g and ev["contributors"] == [g] and ev["host_glin"] is None


def test_02_inert_host_executing_resident_copier_is_not_the_genetic_ancestor():
    w = _world(); gr = w.insert_ecology(1, RESIDENT15, 0, "random_inflow"); gh = w.insert_ecology(0, HOST15, 0, "random_inflow")
    x, _ = _host_input(HOST15, RESIDENT15)
    ev = _birth(w, 0, 1, x)
    assert ev["executor_glin"] == gh and ev["executed_material"] in ("neighbour", "mixed") and ev["exec_counts"]["nbr"] > 0
    assert ev["child_glin"] == gr and ev["template_glin"] == gr and gh not in ev["contributors"] and ev["host_glin"] == gh
    assert ev["mechanism"].startswith("HOST_EXECUTION")


def test_03_host_mutation_that_contributes_no_bytes_stays_out_of_ancestry():
    w = _world(); gr = w.insert_ecology(1, RESIDENT15, 0, "random_inflow"); gh = w.insert_ecology(0, HOST15, 0, "random_inflow")
    x, _ = _host_input(HOST15, RESIDENT15)
    h = bytearray(HOST15); h[31] ^= 0x01; w.genomes[0] = bytes(h); o = list(w.orig[0]); o[31] = w._new(LC.MUT); w.orig[0] = tuple(o)
    r = vm.execute(w.genomes[0], RESIDENT15, (x,), LC.STEP_CAP, True, -1.0)
    if not (sum(r["nbr_mask"]) / 32 >= 0.9 and r["nbr_window"] == RESIDENT15): pytest.skip("mutation changed hosting behaviour")
    ev = _birth(w, 0, 1, x); child_orig = w.orig[1]; host_fid = w.gl[gh]["founder_oid"]
    assert gh not in ev["contributors"] and not any(m >= 0 and m // 32 == host_fid for m in child_orig) and not any(m == o[31] for m in child_orig)


def _half_half():
    prog = [I(1, 1), 0, I(1, 2), 128, I(1, 3), 16, I(20), I(6, 3), I(16), 0xFC,
            I(1, 1), 144, I(1, 2), 144, I(1, 3), 16, I(20), I(6, 3), I(16), 0xFC, I(23)]
    return T.pad(prog, 32)


def test_04_recombination_both_contributors_recorded():
    w = _world(); rec = _half_half(); gA = w.insert_ecology(0, rec, 0, "random_inflow"); gB = w.insert_ecology(1, RESIDENT15, 0, "random_inflow")
    ev = _birth(w, 0, 1, 0)
    assert ev["copied_exec"] == 16 and ev["copied_nbr"] == 16 and set(ev["contributors"]) == {gA, gB} and "RECOMBINATION" in ev["mechanism"]


def test_05_mutation_byte_is_new_material_not_a_donor():
    w = _world(); g = w.insert_ecology(0, REPL, 0, "random_inflow")
    r = vm.execute(REPL, LC.ZERO, (0,), LC.STEP_CAP, True, -1.0); child = bytearray(r["nbr_window"]); child[5] ^= 0x55
    o, s = w.attribute(0, 1, bytes(child), r, LC.ZERO, (0,))
    assert o[5] < 0 and (-o[5]) % 8 == LC.MUT and all(o[p] == w.orig[0][p] for p in range(32) if p != 5)


def test_06_migration_preserves_genetic_and_ecological_history():
    w = _world(); g = w.insert_ecology(0, REPL, 0, "random_inflow"); _birth(w, 0, 1, 0)
    before = (w.genomes[1], w.orig[1], w.glin[1], w.ggen[1], w.lin[1], w.oid[1], w.ins[1], w.age[1])
    w.migrate(1, 5)
    assert (w.genomes[5], w.orig[5], w.glin[5], w.ggen[5], w.lin[5], w.oid[5], w.ins[5], w.age[5]) == before and w.genomes[1] is None
    ev = _birth(w, 5, 7, 0); assert ev["child_glin"] == g and w.ggen[7] == before[3] + 1


def test_07_random_inflow_origin_survives_descendants():
    from archaeon.lineage.assay_block import run_block
    import itertools
    r = run_block("t7", 1, {"K_chambers": 8, "dwell": 16, "refills": 3}, {"U": M1.ARMS["U"]}, tapes=itertools.repeat(REPL), origin="random_inflow", keep_worlds=True)
    w = r["arms"]["U"]["_world"]; gl = {w.glin[i] for i in range(LC.N) if w.genomes[i] is not None}
    assert gl and all(w.gl[g]["origin"] in ("random_inflow", "originated") and not w.gl[g]["inserted"] for g in gl)
    assert any(w.gl[g]["origin"] == "random_inflow" for g in gl)


def test_08_inserted_control_cannot_become_random_through_hosting():
    w = _world(); gr = w.insert_ecology(1, RESIDENT15, 0, "control_inserted"); gh = w.insert_ecology(0, HOST15, 0, "random_inflow")
    x, _ = _host_input(HOST15, RESIDENT15)
    ev = _birth(w, 0, 1, x)
    assert ev["child_glin"] == gr and w.gl[gr]["inserted"] and w.ins[1]
    w.gl[gr]["root_end"] = 0; w.gl[gr]["alive_at_check"] = True; w.gl[gr]["peak"] = 999
    assert gr not in w.genetic_establishments()


def test_09_block15_host_labels_collapse_to_the_resident_lineage():
    L = json.loads((REPO / "archaeon/envgate/LINEAGES.json").read_text(encoding="utf-8"))["lineages"]
    hosts = [bytes.fromhex(r["founder_tape"]) for r in L if r["block"] == 15 and r["arm"] == "U" and r["founder_class"] == "INERT"]
    w = LC.World("t9", 0, ("t9.w", 0), ("t9.m", 0), inputs=lambda w, c, e: [(0,)] * 3); gr = w.insert_ecology(0, RESIDENT15, 0, "random_inflow")
    child_glins = set(); host_glins = set(); n = 0
    for k, h in enumerate(hosts):
        xs = [x for x in range(256) if (lambda r: sum(r["nbr_mask"]) / 32 >= 0.9 and r["nbr_window"] == RESIDENT15)(vm.execute(h, RESIDENT15, (x,), LC.STEP_CAP, True, -1.0))]
        if not xs: continue
        cell = 1 + (k % 100); gh = w.insert_ecology(cell, h, 0, "random_inflow")
        w.genomes[0] = RESIDENT15
        ev = _birth(w, cell, 0, xs[0]); child_glins.add(ev["child_glin"]); host_glins.add(ev["host_glin"]); n += 1
        w.glin[0] = gr; w.orig[0] = tuple(w.gl[gr]["founder_oid"] * 32 + p for p in range(32)); w.ins[0] = False
    assert n >= 10 and child_glins == {gr} and len(host_glins) == n            # n parent-chain host labels -> ONE genetic lineage


@pytest.mark.skipif(not os.environ.get("Z80ATLAS_SLOW"), reason="replays 14,800 epochs of ENVGATE-01 block 13 (about 20 min)")
def test_10_block13_rescue_is_near_copier_propagation_aided_by_a_foreign_executor():
    from archaeon.lineage.assay_block import run_block
    r = run_block("envgate", 13, {"K_chambers": 2048, "dwell": 64, "refills": 1024}, {"BLOCK_128": M1.ARMS["BLOCK_128"]}, until_epoch=14800, keep_worlds=True)
    w = r["arms"]["BLOCK_128"]["_world"]
    dom = max(w.alive.items(), key=lambda kv: kv[1])[0]; st = w.gl[dom]
    assert st["root"] == "arrival" and st["arrival"] == 447492                      # the near-copier's genome, not the host's
    host_arrival_glins = [g for g, s in w.gl.items() if s.get("arrival") == 446966]
    assert any(h in st["hosts"] for h in host_arrival_glins) or st["births_hosted"] > 0


def test_fast_path_equals_taint_path():
    w = _world(); w.insert_ecology(0, REPL, 0, "random_inflow")
    r = vm.execute(REPL, LC.ZERO, (0,), LC.STEP_CAP, True, -1.0)
    fast, _ = w._labels(0, LC.ZERO, (0,), r, r["nbr_window"])
    res, wl, ex = execute_taint(REPL, LC.ZERO, (0,), LC.STEP_CAP, True, -1.0)
    assert res == r and wl == fast and w.fast_calls == 1


def test_taint_vm_differential_small():
    from proteus.foundry.prng import SplitMix64, seed_from
    rr = SplitMix64(seed_from("test.taint", 3))
    for cp in (True, False):
        for _ in range(3000):
            t = bytes(rr.randbelow(256) for _ in range(32)); nb = bytes(rr.randbelow(256) for _ in range(32)); x = (rr.randbelow(256),)
            assert vm.execute(t, nb, x, 256, cp, -1.0) == execute_taint(t, nb, x, 256, cp, -1.0)[0]
