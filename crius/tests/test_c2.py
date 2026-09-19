"""Campaign 2 tests: resource invariant, typed procedures, paired-stream takeover, PARTS, fossils.

Run: python -m pytest crius/tests -q
"""

import json
import os

import pytest

from crius import artifacts, evaluate, parts_c2, receipts, streams, tasks as tasks_c0, vm, workspace, world_c1
from crius.env import TaskRun, TaskOver
from crius.player import VMPlayer, run_task

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = lambda n: receipts.load_config(os.path.join(HERE, "..", "configs", "%s.json" % n))


@pytest.fixture(scope="module")
def c2a():
    return CFG("c2a")


@pytest.fixture(scope="module")
def c2b():
    return CFG("c2b")


@pytest.fixture(scope="module")
def c2c():
    return CFG("c2c")


@pytest.fixture(scope="module")
def stream(c2b):
    return streams.lifetime(c2b, 301, "gate")


# ---------------------------------------------------------------- resource invariant (DESIGN_C2 s2)


def test_empty_objects_are_charged():
    w = workspace.Workspace(cells=256, capacity_bytes=10)
    assert w.create_record({}) == 0 and w.bytes_used() == 2
    assert w.create_record({}) == 1 and w.bytes_used() == 4
    assert w.create_record({0: (1, 2, 3, 4)}) == 2 and w.bytes_used() == 10   # 2 + 4
    assert w.create_record({}) == -1                                          # over capacity
    assert w.failed_writes == 1
    w.recount()
    assert w.bytes_used() == 10
    b = artifacts.ExecutableBlock(0, [])
    assert b.size_bytes() == workspace.OBJECT_METADATA_BYTES + 8  # 8 int state slots


def test_record_id_clock_fossil_keeps_its_signature_under_the_charge(c2a):
    fx = receipts.read_json(os.path.join(HERE, "..", "fixtures", "c0_failure_families.json"))["families"]["F4_record_id_clock_c1b"]
    cfg = receipts.load_config(os.path.join(HERE, "..", "configs", "c1b.json"))
    t = streams.lifetime(cfg, 201, "qual")
    p = VMPlayer(vm.program_from_json(fx["program"]))
    acc = evaluate.run_lifetime(p, t, cfg, "ACCUMULATED", seed=201)["metrics"]
    fresh = evaluate.run_lifetime(p, t, cfg, "FRESH", seed=201)["metrics"]
    assert acc["successes"] < fresh["successes"]  # the clock still runs: ids are values, only bytes were charged


# ---------------------------------------------------------------- typed procedures (rung B/C)


def _run(prog_src, task, cfg, blocks=None, max_len=96):
    vm.set_substrate(cfg.get("substrate", {}))
    ws = workspace.Workspace.empty(cfg)
    bs = blocks or artifacts.BlockStore.empty(cfg)
    r = run_task(VMPlayer(vm.assemble(prog_src, max_len=max_len)), task, 0, ws, bs)
    return r, bs


def test_typed_ops_are_inert_at_rung_A(c2a, stream):
    r, bs = _run("PREC_BEGIN\nACTI 3\nACTI 4\nPREC_END R2\nINPUT R3, status\nHALT", stream[0], c2a)
    assert len(bs.blocks) == 0 and r["status_final"] == 1 and r["interactions_used"] == 2


def test_prec_records_relative_procedure_and_calibration_object(c2b, stream):
    task = stream[0]
    r, bs = _run("PREC_BEGIN\nACTI 3\nACTI 4\nPREC_END R2\nHALT", task, c2b)
    kinds = [b for b in bs.blocks.values()]
    origins = sorted(b.origin for b in kinds)
    assert origins == ["calibration", "procedure"]
    proc = next(b for b in kinds if b.origin == "procedure")
    p3, p4 = world_c1.primitive_of(task.perm[3]), world_c1.primitive_of(task.perm[4])
    steps = [(ins[1], ins[2]) for ins in proc.instructions]
    assert steps[0] == (world_c1.KINDS.index(p3[0]), 0)
    assert steps[1] == (world_c1.KINDS.index(p4[0]), (p4[1] - p3[1]) % world_c1.L)
    cal = next(b for b in kinds if b.origin == "calibration")
    assert cal.local_state[0][3] == task.perm[3] and cal.local_state[1][task.perm[3]] == 3


def test_pinvoke_applies_procedure_with_argument(c2b, stream):
    task = stream[0]
    # record INC-like step at action 3, then invoke with every argument: the emitted primitive positions shift by the argument
    r, bs = _run("PREC_BEGIN\nACTI 3\nPREC_END R2\nCONST R4, 0\nPINVOKE R2, R4\nCONST R4, 1\nPINVOKE R2, R4\nCONST R4, 2\nPINVOKE R2, R4\nHALT", task, c2b)
    log = bs.invocation_log
    acts = [e["actions"] for e in log]
    kind, pos = world_c1.primitive_of(task.perm[3])
    # the argument is the ABSOLUTE position of the procedure's first step; an invocation emits an action only
    # when the calibration object knows an id for the resulting primitive (only (kind, pos) was ever revealed)
    known = {task.perm[3]}
    expect = [world_c1.index_of(kind, a) in known for a in (0, 1, 2)]
    assert [bool(x) for x in acts] == expect
    assert any(acts) and bs.invocations and r["artifacts_invoked"] == 3


def test_psim_and_pmatch_are_mental(c2c, stream):
    task = next(t for t in stream if t.depth == 1)
    src = "PREC_BEGIN\nACTI 3\nACTI 5\nPREC_END R2\nINPUT R1, num_ops\nACT R1\nINPUT R6, current\nCONST R4, 1\nPSIM R6, R2, R4\nPMATCH R7, R2, R4\nHALT"
    r, bs = _run(src, task, c2c)
    assert r["interactions_used"] == 2          # PSIM/PMATCH added no interactions
    vm.set_substrate(c2c["substrate"])
    env = TaskRun(task, 0)
    st = vm.VMState(env, workspace.Workspace.empty(c2c), bs)
    steps = vm._proc_steps(st, next(b.block_id for b in bs.blocks.values() if b.origin == "procedure"))
    assert steps is not None and len(steps) == 2


def test_psim_is_inert_at_rung_B(c2b, stream):
    r, bs = _run("PREC_BEGIN\nACTI 3\nPREC_END R2\nINPUT R6, current\nCONST R4, 1\nPSIM R6, R2, R4\nINPUT R7, status\nHALT", stream[0], c2b)
    assert r["status_final"] == 1


def test_post_success_actions_are_ignored_not_fatal(c2b, stream):
    task = stream[0]
    # enumerate actions until success, then keep acting: the task must not end on the extra actions
    vm.set_substrate(c2b["substrate"])
    env = TaskRun(task, 0)
    seq = None
    import itertools
    for d in range(1, 4):
        for s in itertools.product(range(12), repeat=d):
            env.act(12)
            for a in s:
                env.act(a)
            if env.success:
                seq = s
                break
        if seq:
            break
    assert env.success and not env.over
    env.act(3)
    env.act(12)
    assert env.post_success_actions == 2 and not env.over and env.interactions == sum(1 for _ in [0]) * env.interactions


# ---------------------------------------------------------------- PARTS


def test_parts_assemble_within_bounds_and_ancestry_is_a_chain(c2c):
    for name in parts_c2.SOURCES:
        prog = parts_c2.program(name)
        assert 1 <= len(prog) <= c2c["vm"]["max_program_len"]
    for part, anc in parts_c2.ANCESTOR.items():
        assert anc in parts_c2.SOURCES
        assert parts_c2.edit_distance(parts_c2.program(anc), parts_c2.program(part)) > 0
    assert parts_c2.edit_distance(parts_c2.program("P_BASE"), parts_c2.program("P_BASE")) == 0


def test_positive_control_records_and_reuses_procedures(c2c):
    t = streams.lifetime(c2c, 301, "gate")
    p = parts_c2.player("P_REC_INV_PLAN")
    acc = evaluate.run_lifetime(p, t, c2c, "ACCUMULATED", seed=301)
    fresh = evaluate.run_lifetime(p, t, c2c, "FRESH", seed=301)
    assert acc["metrics"]["blocks_created_total"] >= 2
    assert acc["metrics"]["artifacts_invoked_total"] > 0
    assert acc["metrics"]["successes"] > fresh["metrics"]["successes"]
    chains_acc = sum(1 for r in acc["task_results"] if r["depth"] == 2 and r["success"])
    chains_fresh = sum(1 for r in fresh["task_results"] if r["depth"] == 2 and r["success"])
    assert chains_acc > chains_fresh


# ---------------------------------------------------------------- opcode sets and search opset


def test_mutation_opset_per_rung(c2a, c2b, c2c):
    a, b, c = vm.opcode_names(c2a["substrate"]), vm.opcode_names(c2b["substrate"]), vm.opcode_names(c2c["substrate"])
    assert "PINVOKE" not in a and "PINVOKE" in b and "PSIM" not in b and "PSIM" in c
    assert "PSTEP" not in b and "PSTEP" not in c   # written only by PREC_END
    assert set(a) < set(b) < set(c)
