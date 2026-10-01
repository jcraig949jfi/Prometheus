"""W2-8 regression tests: each SEMANTIC check is run on the frozen code (expected to FAIL: that is the defect) and on the
proposed patch (expected to PASS). Design gates are expected to fail on the frozen design whatever the code.

    python -B tests/test_w2_8.py        (from the W2-8 folder; prints a table, exit 0 iff every expectation is met)

No world is run: Runners are constructed and single methods are called. Nothing is written outside this folder.
"""
from __future__ import annotations

import copy
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "demos"))
sys.path.insert(0, str(HERE.parent / "patches"))
import _paths  # noqa: E402,F401
import p11  # noqa: E402
import run_dd  # noqa: E402
import run_ds  # noqa: E402
import tasks  # noqa: E402
import world  # noqa: E402
import world_patch  # noqa: E402
import xtg_patch  # noqa: E402
import z8  # noqa: E402

FFA6 = run_ds.cells()[run_dd.CELLS["ffa6"]]
AE73 = run_ds.cells()[run_dd.CELLS["7ae3"]]


def _org(niche):
    return type("O", (), {"niche": niche})()


# ---------------------------------------------------------------- semantic checks (property must hold)
def t_d1_score_follows_own_task():
    """Two organisms with identical bytes in niches with different tasks are scored on their own tasks."""
    cell = dict(FFA6["cell"], atlas_axis="NONE", pressure="TASK_GATED_INTERACTION")
    r = world.Runner(cell, 31_000_000, tier="M")
    r._env_epoch()
    r.env_pop[0].update(transform="ADD37", read_order="FORCED_READ")
    r.env_pop[1].update(transform="XOR5A", read_order="ANSWER_BEFORE_READ")
    g = r._pad(tasks.witness(r._env_spec_for(_org(0))))
    x, y = r._place(g, 0, niche=0), r._place(g, 1, niche=1)
    r._validate(force=True)
    true1 = tasks.competence(g, r._env_spec_for(_org(1)), seed=r.seed * 7919, held_seed=r.seed * 7919 + 500000)
    return y.held == true1["held"] and x.held != y.held


def _stub_pair(accept):
    saved = (p11.predecessor_accepts, p11.assay, p11.ordinary_diagnostics)
    p11.assay = lambda *k, **kw: {"pass": True, "draws_passed": 3, "draws": [], "C2_majority": True,
                                  "C4_majority": True, "C5_majority": True}
    p11.ordinary_diagnostics = lambda *k, **kw: {}
    p11.predecessor_accepts = accept
    return saved


def _two():
    r = world.Runner(dict(AE73["cell"], atlas_axis="NONE"), 3, tier="S", max_epochs=1)
    r.t["epochs"] = 0
    r.run()
    x, y = [o for o in r.orgs if o.alive][:2]
    x.age = y.age = 40
    return r, x, y


def t_d8_mutual_acceptance_depth_one():
    saved = _stub_pair(lambda *k: True)
    try:
        r, x, y = _two()
        ox, oy = x.oid, y.oid
        r._pair_interact(0, x, y)
        edges = {e["child"]: e["parent"] for e in r.lineage if e["kind"] == "birth"}
        return r._depths(edges)[0] == 1 and set(edges.values()) == {ox, oy}
    finally:
        p11.predecessor_accepts, p11.assay, p11.ordinary_diagnostics = saved


def t_d9_birth_resets_bookkeeping():
    n = {"k": 0}

    def first(*k):
        n["k"] += 1
        return n["k"] == 1
    saved = _stub_pair(first)
    try:
        r, x, y = _two()
        r._pair_interact(0, x, y)
        return r.slot_owner.get(x.slot) == x.oid and x.age == 0 and x.oid in r.birth_niche \
            and r.ct["nonheritable_state_inherited"] == 1
    finally:
        p11.predecessor_accepts, p11.assay, p11.ordinary_diagnostics = saved


def t_d4_slotted_operand_spares_opcodes():
    r = world.Runner(dict(FFA6["cell"], atlas_axis="NONE"), 7, tier="S")
    r.mut_rate = 0.04
    import random
    rng = random.Random(1)
    for _ in range(10):
        g = bytes(rng.randrange(256) for _ in range(64))
        ops = set(r._boundaries(g))
        for _ in range(200):
            m = r._mutate(g)
            if any(g[i] != m[i] and i in ops for i in range(64)):
                return False
    return True


def t_d6_d15_xtg_readout():
    """An ANSWER_BEFORE_READ niche's perfect reader is competent; a regime-ignoring echo of base is not."""
    cell = dict(FFA6["cell"], atlas_axis="NONE", pressure="TASK_GATED_INTERACTION")
    r = world.Runner(cell, 31_000_002, tier="M")
    r._env_epoch()
    r.env_pop[1].update(transform="XOR5A", read_order="ANSWER_BEFORE_READ")
    r.env_pop[0].update(transform="ADD37", read_order="FORCED_READ")
    good = r._place(r._pad(tasks.witness(r._env_spec_for(_org(1)))), 0, niche=1)
    echo, _ = z8.asm("IN\nLD B,A\nIN\nXOR B\nLD B,A\nIN\nLD A,B\nOUT\nHALT")
    bad = r._place(r._pad(echo), 1, niche=0)
    r._validate(force=True)
    return {"frozen": xtg_patch.frozen_competent(r, good) and not xtg_patch.frozen_competent(r, bad),
            "patched": xtg_patch.readout(r, good, tasks)["competent"] and not xtg_patch.readout(r, bad, tasks)["competent"]}


# ---------------------------------------------------------------- design gates (frozen design expected to fail)
def g_d2_h3_arms_differ_in_physics():
    man = json.loads((_paths.C9 / "MANIFEST_FROZEN.json").read_text())
    h3 = next(b for b in man["bundles"] if b["hypothesis_id"] == "H3")
    arms = {x["arm"]: x for x in h3["arms"]}
    rs = []
    for k in ("A_easy_plus_migration", "B_homogeneous_same_migration"):
        x = arms[k]
        r = world.Runner(x["cell"], x["seed"], tier=x["tier"], max_epochs=1, **x.get("kwargs", {}))
        r.t["epochs"] = 0
        r.run()
        for o in r.orgs:
            o.comp = o.held = 0.95 if o.niche == 0 else 0.05   # even maximal competence contrast
        r._pressure_epoch()
        r._pair_epoch()
        r._migrate()
        rs.append(bytes(r.mem))
    return rs[0] != rs[1]


def g_d3_pressure_levels_differ_on_pair_tape():
    base = world.Runner(dict(FFA6["cell"], atlas_axis="NONE"), 5, tier="S", max_epochs=1)
    base.t["epochs"] = 0
    base.run()
    for o in base.orgs:
        o.comp = o.held = 0.9 if o.oid % 2 else 0.1
    mem = {}
    for lv in ("NONE_IMPLICIT", "QUALITY_DIVERSITY", "NOVELTY", "EXEC_TIME_COST"):
        r = copy.deepcopy(base)
        r.cell["pressure"] = lv
        r._pressure_epoch()
        r._pair_epoch()
        mem[lv] = bytes(r.mem)
    return len(set(mem.values())) == len(mem)


def main():
    rows = []
    sem = [("D1 score follows own niche task", t_d1_score_follows_own_task),
           ("D8 mutual acceptance -> depth 1", t_d8_mutual_acceptance_depth_one),
           ("D9 birth resets bookkeeping + counts carried regs", t_d9_birth_resets_bookkeeping),
           ("D4 SLOTTED OPERAND spares opcodes", t_d4_slotted_operand_spares_opcodes)]
    frozen = {name: f() for name, f in sem}
    xtg = t_d6_d15_xtg_readout()
    world_patch.apply_p1(world)
    world_patch.apply_p2(world)
    world_patch.apply_p3(world)
    patched = {name: f() for name, f in sem}
    ok = True
    for name, _f in sem:
        good = (frozen[name] is False) and (patched[name] is True)
        ok &= good
        rows.append((name, frozen[name], patched[name], "OK" if good else "UNEXPECTED"))
    good = xtg["frozen"] is False and xtg["patched"] is True
    ok &= good
    rows.append(("D6/D15 X-TASK-GATE readout", xtg["frozen"], xtg["patched"], "OK" if good else "UNEXPECTED"))
    for name, f in (("GATE D2 H3 arms A/B differ in physics", g_d2_h3_arms_differ_in_physics),
                    ("GATE D3 pair-tape pressure levels differ", g_d3_pressure_levels_differ_on_pair_tape)):
        v = f()
        good = v is False                      # the frozen DESIGN fails the gate; that is the finding
        ok &= good
        rows.append((name, v, "n/a (design)", "OK (design defect reproduced)" if good else "UNEXPECTED"))
    print("%-52s %-8s %-14s %s" % ("check", "frozen", "patched", "expectation"))
    for r_ in rows:
        print("%-52s %-8s %-14s %s" % tuple(str(x) for x in r_))
    return 0 if ok else 1


def test_all():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
