"""Regression tests for the defects found by the 2026-09-23 post-campaign forensics
(roles/Bellerophon/forensics_2026-09-23/ISSUE_AND_REPAIR_LEDGER.md; issue ids in each test name).

Each test (a) REPRODUCES the defect on the historical v1 surface -- those assertions document the defect and stay
green, because the v1 instrument is kept replayable -- and (b) asserts the REPAIRED property on the v2 surface the
adjudication layer reads (fails before the repair). The v1 golden fixture (golden_v1.json, built from the unmodified
harness) pins the historical behaviour byte-for-byte."""
from __future__ import annotations

import json
import pathlib

import pytest

from prometheus.z80atlas import vm, grammar as G, geometry, scheduler as Sch, controls as C
from prometheus.z80atlas.tasks import Task
from prometheus.z80atlas.world import World, Config

adj = pytest.importorskip("prometheus.z80atlas.adjudication") if False else None   # imported per test so a missing module FAILS


def _adj():
    from prometheus.z80atlas import adjudication
    return adjudication


# ---- the historical instrument stays replayable ------------------------------------------------------------------
def test_v1_golden_replay_is_byte_identical():
    from prometheus.z80atlas.tests import make_golden_v1 as MG
    from prometheus.z80atlas import observatory as O
    gold = json.loads(MG.PATH.read_text(encoding="utf-8"))
    for row in gold["rows"]:
        c = row["case"]
        w, s = MG.run_case(c)
        s = json.loads(json.dumps(s, sort_keys=True, default=str))
        for k, v in row["summary"].items():                       # every historical field, unchanged
            assert s.get(k) == v, (c["vec"], k)
        assert O.triggers(s, c["vec"], 60) == row["triggers"], c["vec"]
        assert json.loads(json.dumps(w.events[:50], default=str)) == row["events_head"], c["vec"]
        assert json.loads(json.dumps(w.ticks_log, default=str)) == [dict(t) for t in row["ticks_log"]] or \
            all(all(t.get(k) == g[k] for k in g) for t, g in zip(w.ticks_log, row["ticks_log"])), c["vec"]


# ---- C1: tail metrics read from the pre-extinction window ----------------------------------------------------------
def test_C1_extinct_world_does_not_report_tail_solvers():
    w = World(Config(reproduction="CONSTRUCTIVE", init="SEEDED_WITNESS", task="INC", ticks=100, cells=64, lifespan=12), 1)
    s = w.run()
    assert s["extinct"] and s["solvers_tail"] > 0                  # v1 defect: a dead world 'has solvers'
    assert s["extinct_tick"] == s["ticks_run"]
    assert s["tail_h"]["solvers"] == 0.0                           # v2: the tail spans the configured horizon
    assert not _adj().task_reached(s)


# ---- C2/C3: a 'solver' is not a solver --------------------------------------------------------------------------------
def test_C2_partial_solvers_are_not_verified_solvers():
    echo = vm.witness_echo().hex()
    w = World(Config(reproduction="EXTERNAL", task="COND_ONE", ticks=60, cells=64, init_tapes=(echo,)), 2)
    s = w.run()
    assert s["solvers_tail"] > 0                                   # v1 defect: ECHO 'solves' COND_ONE by luck
    assert s["verified"]["exact_solvers_final"] == 0               # v2: right on every panel input, or not a solver
    assert not _adj().task_reached(s)


def test_C3_incremental_near_miss_is_not_a_verified_solver():
    t = bytes([vm.IN_A, vm.ADD_A_n, 19, vm.OUT_A, vm.HALT])
    task = Task("ECHO")
    from prometheus.z80atlas.tasks import score
    assert score(task, [(5 + 19) & 0xFF], [5], "INCREMENTAL", "ABR", 2, 1) >= 0.85    # v1: an off-by-19 answer is a 'solver'
    cfg = Config(task="ECHO", scoring="INCREMENTAL")
    assert _adj().verify_tape(t, cfg, Task("ECHO"))["exact"] is False
    assert _adj().verify_tape(vm.witness_echo(), cfg, Task("ECHO"))["exact"] is True


# ---- C4: RESERVOIR's easy niche and its seeded witness ------------------------------------------------------------
def test_C4_reservoir_seeds_and_verifies_the_configured_task():
    v1 = World(Config(reproduction="ENDOGENOUS_COPY", init="SEEDED_WITNESS", world="NICHES", spatial="RESERVOIR", task="COND_MULTI",
                      ticks=5, cells=64), 3)
    seeds = [o for o in v1.cells if o is not None and o.mechanism == "seed"]
    assert seeds and bytes(seeds[0].tape[:3]) == vm.witness_echo()                         # v1 defect: the ECHO witness is seeded
    v2 = World(Config(reproduction="ENDOGENOUS_COPY", init="SEEDED_WITNESS", world="NICHES", spatial="RESERVOIR", task="COND_MULTI",
                      ticks=5, cells=64, physics="v2"), 3)
    seeds = [o for o in v2.cells if o is not None and o.mechanism == "seed"]
    assert seeds and bytes(seeds[0].tape[:len(vm.witness_cond_multi())]) == vm.witness_cond_multi()
    s = v2.run()
    assert s["verified"]["task"]["kind"] == "COND_MULTI"


# ---- C6: beneficial density is unpaired noise ---------------------------------------------------------------------------
def test_C6_paired_scan_has_no_false_beneficial_neighbours():
    L = 64
    tape = vm.witness_echo() + bytes([vm.HALT]) * (L - 3)
    cfg = Config(task="COND_ONE", scoring="ATOMIC")
    task = Task("COND_ONE")
    gains = [geometry.scan(tape, cfg, task, s, n=40)["beneficial_density"] - geometry.scan(tape, cfg, task, s + 1000, n=40)["beneficial_density"]
             for s in range(12)]
    assert max(abs(g) for g in gains) > 0.1                          # v1 defect: the SAME tape shows a 'gain'
    p = geometry.scan_paired(tape, cfg, task, seed=7)
    assert p["null_false_beneficial"] == 0.0                          # v2: an identical 'mutant' is never better
    assert geometry.scan_paired(tape, cfg, task, seed=7) == p         # deterministic


# ---- C8: capture births credited as the writer's replication -----------------------------------------------------------
def _one_write(physics):
    cfg = Config(reproduction="ENDOGENOUS_PARTIAL", cells=16, ticks=5, physics=physics)
    w = World(cfg, 9)
    w.cells = [None] * 16
    writer = w._spawn(0, bytearray(bytes([vm.LD_A_n, 0x77, vm.LD_T_n, 70, vm.LD_pT_A, vm.HALT]) + bytes(58)), None, "init")
    partner = w._spawn(1, bytearray(range(100, 164)), None, "init")
    mem, tr = w._execute(writer, partner.tape, [1])
    writer.tape = bytearray(mem[:64])
    w._apply_reproduction(writer, 1, mem, tr)
    return w, writer


def test_C8_one_byte_capture_is_not_self_replication():
    w, writer = _one_write("v1")
    assert writer.replications == 1 and writer.fidelity_last >= 0.9     # v1 defect: a 1-byte write is 'hifi replication'
    ev = [e for e in w.events if e["kind"] == "copy"][-1]
    assert ev["material"] == "target" and ev["self_copy"] is False       # v2 measurement: classified, not credited
    w2, writer2 = _one_write("v2")
    assert writer2.replications == 0                                     # v2 physics: a capture credits nobody


# ---- C9: 'spontaneous' replication in seeded interventions --------------------------------------------------------------
def test_C9_init_tapes_are_never_spontaneous():
    rep = vm.replicator(64).hex()
    w = World(Config(reproduction="ENDOGENOUS_COPY", init="RANDOM", ticks=40, cells=64, init_tapes=(rep,)), 4)
    s = w.run()
    assert s["self_rep_births"] > 0
    assert not _adj().spontaneous(s, dict(init="RANDOM"), has_init_tapes=True)
    assert s["first_self_replication"]["seeded"] is True


# ---- M1: fidelity against the post-execution tape ---------------------------------------------------------------------
def test_M1_self_smear_is_not_high_fidelity_against_the_pre_execution_tape():
    cfg = Config(reproduction="ENDOGENOUS_COPY", cells=16, ticks=5)
    w = World(cfg, 5); w.cells = [None] * 16
    smear = bytearray(bytes([vm.LD_S_n, 63, vm.LD_T_n, 0, vm.LD_C_n, 128, vm.LDIR, vm.HALT]) + bytes(range(1, 57)))
    o = w._spawn(0, smear, None, "init")
    mem, tr = w._execute(o, None, [1])
    o.tape = bytearray(mem[:64])
    w._apply_reproduction(o, 1, mem, tr)
    ev = [e for e in w.events if e["kind"] == "copy"]
    assert ev and ev[-1]["fidelity"] >= 0.9                              # v1 defect: the smear 'copies itself exactly'
    assert ev[-1]["fidelity_pre"] < 0.9 and ev[-1]["self_copy"] is False


# ---- M2: a bare LDIR at reset 'writes' the whole window without copying anything ------------------------------------------
def test_M2_in_place_sweep_is_a_copy_event_not_self_replication():
    cfg = Config(reproduction="ENDOGENOUS_COPY", cells=16, ticks=5)
    w = World(cfg, 6); w.cells = [None] * 16
    o = w._spawn(0, bytearray(bytes([vm.LDIR, vm.HALT]) + bytes(range(2, 64))), None, "init")
    mem, tr = w._execute(o, None, [1])
    assert sum(1 for a in tr.writes if 64 <= a < 128) == 64            # v1: all 64 window bytes 'written'
    o.tape = bytearray(mem[:64])
    w._apply_reproduction(o, 1, mem, tr)
    ev = [e for e in w.events if e["kind"] == "copy"]
    assert ev and ev[-1]["self_copy"] is False                           # v2: in-place sweep != self-copy


# ---- M5/M6/m1: scheduler identity and seeds -------------------------------------------------------------------------
def test_M5_family_identity_includes_init_tapes(tmp_path):
    c = Sch.Campaign(str(tmp_path), hours=0.01, workers=1, ticks=10, cells=16, seed=1)
    v = G.random_vec(__import__("random").Random(1), {"init": "RANDOM", "reproduction": "ENDOGENOUS_COPY"})
    a = c._spec(v, "exploration", "x"); b = c._spec(v, "intervention", "y", init_tapes=["0840" + "15ff"])
    assert a["family"] != b["family"]


def test_M6_late_matched_controls_carry_their_own_seed(tmp_path):
    c = Sch.Campaign(str(tmp_path), hours=0.01, workers=1, ticks=10, cells=16, seed=1)
    rng = __import__("random").Random(2)
    vecs = [G.random_vec(rng, {"reproduction": "ENDOGENOUS_COPY", "pressure": "GATED_INTERACTION", "scoring": "ATOMIC"}) for _ in range(3)]
    for v in vecs:
        fid = c._family(v, "promoted"); c.s["families"][fid]["promoted"] = True
        c.s["families"][fid]["runs"].append("r0"); c.s["families"][fid]["scores"].append(3)
    specs = c._late_batch(1000)
    by_fam = {}
    for sp in specs:
        if "fresh seed" in sp["reason"]:
            by_fam.setdefault(sp["parents"][0], set()).add(sp["seed"])
    for sp in specs:
        if "matched control" in sp["reason"]:
            assert sp["seed"] in by_fam[sp["parents"][0]], sp["reason"]


def test_m1_duplicate_submissions_are_refused(tmp_path):
    c = Sch.Campaign(str(tmp_path), hours=0.01, workers=1, ticks=10, cells=16, seed=1)
    v = G.random_vec(__import__("random").Random(3))
    a = c._spec(v, "verification", "x", seed=12345)
    assert a is not None
    assert c._spec(v, "verification", "again", seed=12345) is None


# ---- M7: GATED_INTERACTION organisms never age -----------------------------------------------------------------------
def test_M7_gated_organisms_age_under_v2():
    kw = dict(reproduction="EXTERNAL", pressure="GATED_INTERACTION", scoring="INCREMENTAL", ticks=120, cells=64)
    w = World(Config(**kw), 7); w.run()
    ages = [w.tick - o.birth for o in w.cells if o is not None]
    assert max(ages) > w.cfg.lifespan + 1                                # v1 defect: immortals
    w2 = World(Config(physics="v2", **kw), 7); w2.run()
    assert all(w2.tick - o.birth <= w2.cfg.lifespan + 1 for o in w2.cells if o is not None)


# ---- P1: pollination / reservoir copies are exogenous reproduction under ENDOGENOUS physics ------------------------------
def test_P1_pollination_copies_are_counted_and_forbidden_under_v2_endogenous():
    kw = dict(reproduction="ENDOGENOUS_COPY", init="SEEDED_REPLICATOR", world="NICHES", spatial="NICHES_POLLINATION", ticks=60, cells=64)
    s = World(Config(**kw), 8).run()
    assert s["external_births"] == 0 and s["births_by_mechanism"].get("pollination", 0) > 0   # v1 defect: the guard is blind
    assert s["world_copies_under_endogenous"] == s["births_by_mechanism"]["pollination"]
    s2 = World(Config(physics="v2", **kw), 8).run()
    assert s2["births_by_mechanism"].get("pollination", 0) == 0 and s2["world_copies_under_endogenous"] == 0


# ---- m2: COPYALL overruns the step budget -----------------------------------------------------------------------------
def test_m2_copyall_respects_budget_under_v2():
    mem = bytearray(256); mem[:6] = vm.replicator_copyall(64)
    tr = vm.execute(bytearray(mem), 64, 0, 3, [], allow_copyall=True)
    assert tr.steps > 3                                                  # v1 defect
    tr2 = vm.execute(bytearray(mem), 64, 0, 3, [], allow_copyall=True, strict_budget=True)
    assert tr2.steps <= 3


# ---- m4: positive-control grading ---------------------------------------------------------------------------------------
def test_m4_const_witness_check_is_not_vacuous():
    r = C.vm_executes()
    assert r["checks"]["witness_const"] is True
    assert C.witness_check("const", bytes([vm.HALT])) is False           # a program that outputs nothing must fail
