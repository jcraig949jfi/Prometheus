"""Phase 0 tests for physics v3 (computation -> copy resource -> reproduction). Each test names the directive's
Phase-0 requirement it covers. Coupled worlds use scoring NEUTRAL so the ledger is the ONLY path from task to dynamics."""
from __future__ import annotations

import json
import pickle

import pytest

from prometheus.z80atlas import vm
from prometheus.z80atlas.world import World, Config
from prometheus.z80atlas.coupling import Ledger

REP = vm.replicator(64)
HYB = vm.hybrid_relocated(vm.replicator(64), vm.witness_inc())


def cfg(**kw):
    base = dict(reproduction="ENDOGENOUS_COPY", physics="v3", coupling="ON", scoring="NEUTRAL", task="INC", ticks=40, cells=64,
                base_income=16, bonus=64)
    base.update(kw)
    return Config(**base)


def lone(c, tape, partner=None, seed=1):
    """a world holding exactly one organism (cell 0) and optionally a partner (cell 1)"""
    w = World(c, seed); w.cells = [None] * c.cells
    o = w._spawn(0, bytearray(tape) + bytearray(64 - len(tape)), None, "init")
    p = w._spawn(1, bytearray(partner) + bytearray(64 - len(partner)), None, "init") if partner is not None else None
    return w, o, p


def interact(w, o, partner_cell=1, x=41):
    """one interaction of organism o exactly as World.step performs it (execute, reproduce, evaluate)"""
    from prometheus.z80atlas.tasks import score
    task = w.env.task_for(o.niche); inputs = [x]; expected = task.expected(inputs)
    partner = w.cells[partner_cell]
    mem, tr = w._execute(o, partner.tape if partner is not None else None, inputs)
    o.tape = bytearray(mem[:64])
    if tr.neighbour_writes:
        w._apply_reproduction(o, partner_cell, mem, tr)
    correct = score(task, tr.outputs, expected, "ATOMIC", w.cfg.read_gate, tr.first_out_step, tr.first_in_step) >= 0.999
    w.ledger.after_interaction(w, o, task, inputs, tr.outputs, tr.first_out_step, tr.first_in_step, correct)
    return tr, correct


# ---- earning ---------------------------------------------------------------------------------------------------------
def test_resource_earned_only_from_the_declared_task_output():
    w, o, _ = lone(cfg(), vm.witness_inc())
    tr, ok = interact(w, o)
    assert ok and o.res == 16 + 64
    w2, o2, _ = lone(cfg(), bytes([vm.IN_A, vm.INC_A, vm.INC_A, vm.OUT_A, vm.HALT]))       # x+2: wrong
    tr, ok = interact(w2, o2)
    assert not ok and o2.res == 16                                                       # incorrect -> base only
    w3, o3, _ = lone(cfg(), bytes([vm.HALT]))                                            # zero output
    interact(w3, o3); assert o3.res == 16
    w4, o4, _ = lone(cfg(coupling="OFF"), vm.witness_inc())
    interact(w4, o4); assert o4.res == 16                                                # OFF: correct earns nothing extra


def test_only_the_first_output_is_scored_no_farming_by_repetition():
    t = bytes([vm.IN_A, vm.INC_A, vm.OUT_A, vm.OUT_A, vm.OUT_A, vm.HALT])
    w, o, _ = lone(cfg(), t); interact(w, o)
    assert o.res == 16 + 64 and w.ledger.t["rewarded_events"] == 1


def test_organism_cannot_touch_its_ledger_and_no_evaluator_state_is_in_memory():
    # a tape that overwrites the whole address space: R changes only by the ledger's rules
    t = bytes([vm.LD_S_n, 0, vm.LD_T_n, 1, vm.LDIR, vm.HALT])
    w, o, _ = lone(cfg(), t); o.res = 7
    interact(w, o)
    assert o.res == 7 + 16
    # memory before execution holds exactly: own tape, partner tape, task inputs -- nothing the evaluator computes
    w, o, p = lone(cfg(), vm.witness_inc(), partner=bytes(range(64)))
    seen = {}
    real = vm.execute
    def spy(mem, *a, **k):
        seen["mem"] = bytes(mem); return real(mem, *a, **k)
    vm.execute = spy
    try:
        w._execute(o, p.tape, [41])
    finally:
        vm.execute = real
    m = seen["mem"]
    assert m[:64] == bytes(o.tape) and m[64:128] == bytes(p.tape) and m[vm.IN_BASE] == 41
    assert set(m[128:vm.IN_BASE]) <= {0} and set(m[vm.IN_BASE + 1:]) <= {0}
    assert not any(hasattr(vm, n) for n in ("res", "ledger"))


def test_reproduction_is_never_performed_by_the_evaluator():
    w = World(cfg(ticks=30, init="SEEDED_WITNESS"), 3)              # competent witnesses earn; only copiers' own writes breed
    s = w.run()
    assert s["coupling"]["earned_bonus"] > 0 and s["external_births"] == 0
    assert s["endogenous_births"] == s["coupling"]["paid_births"]    # every birth was paid for by its writer's execution
    assert all(e["parent"] is not None for e in w.events if e["kind"] == "copy")
    witnesses = {o.id for o in w.cells if o is not None and o.mechanism == "seed"}
    assert not any(e["parent"] in witnesses for e in w.events if e["kind"] == "copy")   # the rich non-copiers never 'reproduce'
    with pytest.raises(ValueError):
        World(cfg(reproduction="EXTERNAL"), 1)


def test_copying_is_charged_and_unfunded_births_are_refused():
    w, o, p = lone(cfg(), REP, partner=bytes(range(64)))
    o.res = 63
    interact(w, o)
    assert w.ledger.t["refused_births"] == 1 and w.ledger.t["paid_births"] == 0 and bytes(w.cells[1].tape) == bytes(range(64))
    assert o.res == 63 + 16                                          # refused: nothing charged
    interact(w, o)                                                   # 79 >= 64
    assert w.ledger.t["paid_births"] == 1 and o.res == 79 - 64 + 16 and bytes(w.cells[1].tape[:8]) == REP
    assert w.cells[1].res == 0                                       # a newborn starts at 0


def test_credit_is_spendable_only_after_the_execution_that_earned_it():
    w, o, p = lone(cfg(), HYB, partner=bytes(range(64)))
    o.res = 0
    tr, ok = interact(w, o)
    assert ok and w.ledger.t["refused_births"] == 1 and o.res == 80   # computed AND tried to copy: copy refused, then paid
    interact(w, o)
    assert w.ledger.t["paid_births"] == 1


def test_no_silent_overflow_or_underflow():
    w, o, _ = lone(cfg(resource_cap=100), vm.witness_inc())
    for _ in range(3):
        interact(w, o)
    assert o.res == 100 and w.ledger.t["clamped"] == 3 * 80 - 100
    with pytest.raises(AssertionError):
        w.ledger.pay_birth(o, 200)
    with pytest.raises(ValueError):
        World(cfg(physics="v2"), 1)                                  # coupled physics requires v3


def test_ledger_balances_in_every_mode():
    for mode in ("OFF", "ON", "SHUFFLED", "RANDOM_REWARD", "IRRELEVANT", "DELAYED"):
        s = World(cfg(coupling=mode, ticks=60, init_tapes=(REP.hex(), HYB.hex())), 5).run()
        assert s["coupling"]["balanced"], mode


def test_yoked_distributes_exactly_the_schedule():
    on = World(cfg(ticks=60, init_tapes=(REP.hex(), HYB.hex())), 6).run()["coupling"]
    y = World(cfg(coupling="YOKED", ticks=60, init_tapes=(REP.hex(), HYB.hex()), yoke=tuple(on["bonus_schedule"])), 6)
    s = y.run()["coupling"]
    delivered = s["earned_bonus"] + s["yoke_carry"]
    planned = sum(on["bonus_schedule"][:y.tick + 1])
    assert delivered == planned and s["balanced"]


def test_checkpoint_resume_preserves_balances_exactly():
    c = cfg(ticks=80, init_tapes=(REP.hex(), HYB.hex()))
    a = World(c, 9); a_s = a.run()
    b = World(c, 9)
    for _ in range(35):
        b.step()
    b2 = pickle.loads(pickle.dumps(b))                               # checkpoint mid-run, restore into a new object
    for _ in range(35, c.ticks):
        b2.step()
        if not any(x is not None for x in b2.cells):
            break
    alive = [x for x in b2.cells if x is not None]; b2._snapshot(alive, "final")
    b_s = b2.summary(alive)
    for k in ("coupling", "competence", "endogenous_births", "final_alive", "sr_max_depth"):
        assert json.dumps(a_s[k], sort_keys=True) == json.dumps(b_s[k], sort_keys=True), k


def test_deterministic_replay():
    c = cfg(ticks=60, init_tapes=(REP.hex(), HYB.hex()))
    x = json.dumps(World(c, 11).run(), sort_keys=True, default=str); y = json.dumps(World(c, 11).run(), sort_keys=True, default=str)
    assert x == y


def test_migration_never_duplicates_under_coupling():
    s = World(cfg(world="NICHES", spatial="NICHES_POLLINATION", ticks=60, init="SEEDED_REPLICATOR"), 12).run()
    assert s["world_copies_under_endogenous"] == 0 and s["births_by_mechanism"].get("pollination", 0) == 0


def test_measurement_never_feeds_back():
    c = cfg(ticks=60, init_tapes=(REP.hex(), HYB.hex()))
    a = World(c, 13); a.run()
    b = World(c, 13); b.competence.of = lambda tape: (False, False)     # sabotage the measurement
    b.run()
    assert [t["alive"] for t in a.ticks_log] == [t["alive"] for t in b.ticks_log]
    assert a.ledger.t == b.ledger.t


def test_task_identity_acts_only_through_the_ledger():
    # OFF coupling + NEUTRAL scoring: tasks with the same input count give run-for-run identical worlds
    r = [World(cfg(coupling="OFF", task=t, ticks=60, init_tapes=(REP.hex(), HYB.hex())), 14) for t in ("INC", "ECHO", "COND_ONE")]
    for w in r:
        w.run()
    assert r[0].ticks_log == r[1].ticks_log == r[2].ticks_log or \
        [x["alive"] for x in r[0].ticks_log] == [x["alive"] for x in r[1].ticks_log] == [x["alive"] for x in r[2].ticks_log]
    # ON coupling: the task now matters (INC hybrids are correct only on INC)
    on = [World(cfg(task=t, ticks=60, init_tapes=(REP.hex(), HYB.hex())), 14).run()["coupling"]["earned_bonus"] for t in ("INC", "ECHO")]
    assert on[0] > on[1]


def test_shuffled_verifier_pays_only_chance():
    s = World(cfg(coupling="SHUFFLED", ticks=60, init_tapes=(HYB.hex(),)), 15).run()["coupling"]
    assert s["correct_events"] > 100 and s["rewarded_events"] < 0.05 * s["correct_events"]


def test_delayed_credit_arrives_late_or_never():
    w, o, _ = lone(cfg(coupling="DELAYED", delay=5), vm.witness_inc())
    interact(w, o); assert o.res == 16
    for t in range(6):
        w.tick = t; w.ledger.end_tick(w)
    assert o.res == 16 + 64


def test_v1_v2_untouched_by_v3():
    from prometheus.z80atlas.tests import make_golden_v1 as MG
    gold = json.loads(MG.PATH.read_text(encoding="utf-8"))["rows"][0]
    w, s = MG.run_case(gold["case"])
    assert s["coupling"] is None and s["competence"] is None
    assert {k: json.loads(json.dumps(s, default=str)).get(k) for k in gold["summary"]} == gold["summary"]


def test_campaign_fixtures_have_their_declared_properties():
    from prometheus.z80atlas import coupling_campaign as CC, adjudication as A
    from prometheus.z80atlas.tasks import Task
    sd = 11_000_000_000_005
    for task in ("CONST", "ECHO", "INC", "COND_ONE", "SUM2", "COND_MULTI"):
        F = CC.fixtures(task, sd); c = Config(task=task); t = Task(task, k=CC.task_k(sd))
        d = {n: A.repro_descriptor(bytes.fromhex(F[n]), c, t) for n in F}
        assert d["REP"]["self_copy"] and d["REP"]["task_accuracy"] == 0
        assert d["HYB"]["self_copy"] and d["HYB"]["task_accuracy"] == 1.0
        assert d["NOCOMP"]["self_copy"] and d["NOCOMP"]["task_accuracy"] == 0
        assert not d["NOCOPY"]["self_copy"] and d["NOCOPY"]["task_accuracy"] == 1.0
        assert d["BAD"]["self_copy"] and d["BAD"]["task_accuracy"] == 0
        assert not d["SLIDER"]["self_copy"]
    F = CC.fixtures("INC", sd); c = Config(task="INC")
    assert A.repro_descriptor(bytes.fromhex(F["CORRUPT"]), c, Task("INC"))["task_accuracy"] < 0.1
    assert A.repro_descriptor(bytes.fromhex(F["MULTI"]), c, Task("INC"))["task_accuracy"] == 1.0


def test_campaign_plan_is_deterministic_and_yokes_follow_their_partner():
    from prometheus.z80atlas import coupling_campaign as CC
    P = CC.plan({}); Q = CC.plan({})
    assert CC.plan_hash(P) == CC.plan_hash(Q)
    ids = {p["id"]: i for i, p in enumerate(P)}
    for p in P:
        if p["arm"] == "YOKED":
            on = P[ids[p["depends"]]]
            assert on["arm"] == "ON" and on["seed"] == p["seed"] and on["init_tapes"] == p["init_tapes"] and on["K"] == p["K"]
    seeds = {p["seed"] for p in P}
    assert min(seeds) >= CC.SEED_BASE


def test_amendment1_tail_repair_and_active_runtime(tmp_path):
    from prometheus.z80atlas import coupling_campaign as CC
    rp = tmp_path / "results.jsonl"
    rp.write_bytes(b'{"id": "c000001"}\n{"id": "c0000')
    st = {}
    CC.repair_tail(rp, st)
    assert rp.read_bytes() == b'{"id": "c000001"}\n' and st["tail_repairs"][0]["bytes_removed"] == len(b'{"id": "c0000')
    st = {"active_segments": [[100.0, 4660.0, "pre-OOM"], [9000.0, 9500.0, "seg2"], [20000.0, None, "open"]]}
    assert CC.active_used(st) == 4560.0 + 500.0


def test_supervisor_integrity_detects_identity_corruption(tmp_path):
    import json as _j
    from prometheus.z80atlas import coupling_campaign as CC, coupling_supervisor as SV
    P = CC.plan({}); p = P[0]
    (tmp_path / "results.jsonl").write_text(_j.dumps({k: p[k] for k in ("id", "seed", "lane", "cell", "arm", "K", "k", "pair")}) + "\n")
    inp = tmp_path / "in.json"; inp.write_text("{}")
    assert SV.integrity(tmp_path, inp)["ok"]
    bad = dict({k: p[k] for k in ("id", "seed", "lane", "cell", "arm", "K", "k", "pair")}, seed=p["seed"] + 1)
    (tmp_path / "results.jsonl").write_text(_j.dumps(bad) + "\n")
    assert not SV.integrity(tmp_path, inp)["ok"]
