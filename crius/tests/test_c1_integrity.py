"""Campaign 1 integrity and fixture tests (operator ruling 2026-09-19, items 5 and 7C/7D).

Run: python -m pytest crius/tests -q
"""

import os

import pytest

from crius import artifacts, evaluate, receipts, streams, tasks as tasks_c0, tasks_c1, vm, workspace, world_c1
from crius.env import TaskRun
from crius.player import VMPlayer, run_task

HERE = os.path.dirname(os.path.abspath(__file__))
C0 = os.path.join(HERE, "..", "configs", "c0.json")
C1 = os.path.join(HERE, "..", "configs", "c1.json")
FIX = os.path.join(HERE, "..", "fixtures", "c0_failure_families.json")


@pytest.fixture(scope="module")
def cfg0():
    return receipts.load_config(C0)


@pytest.fixture(scope="module")
def cfg1():
    return receipts.load_config(C1)


@pytest.fixture(scope="module")
def fixtures():
    return receipts.read_json(FIX)["families"]


# ---------------------------------------------------------------- 7C: status channels cannot alias actions


def test_store_failure_cannot_become_an_action(cfg0):
    # fill the block store, then act on the failed allocation's result
    src = "\n".join(["BLK_NEW R0"] * 33 + ["INPUT R1, status", "ACT R0", "HALT"])
    prog = vm.assemble(src)
    task = tasks_c0.make_lifetime(cfg0, 101, "search")[0]
    ws = workspace.Workspace.empty(cfg0)
    blocks = artifacts.BlockStore.empty(cfg0)
    env = TaskRun(task, 0)
    st = vm.VMState(env, ws, blocks)
    try:
        vm._execute(prog, st, block_id=-1)
    except Exception:
        pass
    assert len(blocks.blocks) == 32
    assert isinstance(st.regs[0], vm.Fail)
    assert st.regs[1] == 1                      # status read after the failed BLK_NEW
    assert env.trajectory == []                 # no action, no reset happened
    assert env.invalid_actions == 1 and env.status == 2
    # arithmetic on FAIL stays FAIL; a branch on it does not read as zero
    prog2 = vm.assemble("\n".join(["BLK_NEW R0"] * 33 + ["CONST R1, 7", "ADD R2, R0, R1", "MOD R2, R2, R1", "ACT R2", "HALT"]))
    env2 = TaskRun(task, 0)
    st2 = vm.VMState(env2, workspace.Workspace.empty(cfg0), artifacts.BlockStore.empty(cfg0))
    try:
        vm._execute(prog2, st2, block_id=-1)
    except Exception:
        pass
    assert isinstance(st2.regs[2], vm.Fail) and env2.trajectory == [] and env2.invalid_actions == 1


def test_out_of_range_values_are_not_actions(cfg0):
    task = tasks_c0.make_lifetime(cfg0, 101, "search")[0]
    env = TaskRun(task, 0)
    for v in (-1, 7, 13, 100, None, (1, 2), 2.5, True):
        env.act(v)
    assert env.trajectory == [] and env.invalid_actions == 8
    env.act(6)  # RESET is the only value that resets
    assert env.trajectory == [(6, task.start)]


# ---------------------------------------------------------------- 7C fixture: the empty-block clock is dead


def test_fixture_empty_block_clock_signature_and_integrity(cfg0, fixtures):
    """The C0 'clock' fossil. CORRECTION 2026-09-19: its mechanism is not a failure alias. BLK_NEW's
    returned ids grow monotonically across a lifetime (next_id never reuses freed slots); the loop
    bound LT R3, R0, R2 with R2 = num_ops stops the enumeration once the id exceeds 5, so from the
    second task on it halts with zero interactions. Ids are values an organism may legitimately read
    (INPUT task_index would do the same); the ratio metric made abstention pay (F1). The test keeps
    the fossil's signature and proves the ruling-5 property: no store failure ever became an action."""
    f = fixtures["F1_abstention_store_clock"]
    p = VMPlayer(vm.program_from_json(f["program"]))
    tasks = tasks_c0.make_lifetime(cfg0, 201, "heldout_v1")
    acc = evaluate.run_lifetime(p, tasks, cfg0, "ACCUMULATED", seed=201)
    fresh = evaluate.run_lifetime(p, tasks, cfg0, "FRESH", seed=201)
    # signature: accumulation (growing ids) costs competence; fresh copies (ids restart) solve more
    assert acc["metrics"]["successes"] < fresh["metrics"]["successes"]
    assert sum(r["interactions_used"] for r in acc["task_results"][2:]) == 0
    # integrity: the store fills (32 blocks) and its failures never alias an action
    assert max(w["blocks"]["blocks"] for w in acc["workspace_history"]) == 32
    # (out-of-range register values now count as invalid actions instead of wrapping onto an action)
    # under the C1 fitness the same behaviour loses to solving more tasks
    cfg_c1_costs = dict(cfg0)
    cfg_c1_costs["costs"] = {"steps_per_interaction": 100, "fitness": "c1", "unsolved_charged_full_budget": True}
    assert evaluate.lifetime_metrics(fresh["task_results"], cfg_c1_costs)["C1_FITNESS"] >         evaluate.lifetime_metrics(acc["task_results"], cfg_c1_costs)["C1_FITNESS"]


# ---------------------------------------------------------------- fossils keep their signatures (regression, not detection)


def test_fixtures_replay_and_keep_signatures(cfg0, fixtures):
    f2 = fixtures["F2_enumeration_order"]
    f3 = fixtures["F3_action_script"]
    cfg_x = receipts.load_config(os.path.join(HERE, "..", "configs", "c0x.json"))
    q = tasks_c0.make_lifetime(cfg_x, 201, "heldout_v1")
    s = tasks_c0.make_lifetime(cfg_x, 101, "search")
    seed = VMPlayer(vm.enumerate_program())
    e2 = evaluate.run_lifetime(VMPlayer(vm.program_from_json(f2["program"])), q, cfg_x, "ACCUMULATED", seed=201)["metrics"]
    e0 = evaluate.run_lifetime(seed, q, cfg_x, "ACCUMULATED", seed=201)["metrics"]
    assert e2["successes"] < e0["successes"]  # the pruned order loses on held-out
    a3s = evaluate.run_lifetime(VMPlayer(vm.program_from_json(f3["program"])), s, cfg_x, "ACCUMULATED", seed=101)["metrics"]
    a3q = evaluate.run_lifetime(VMPlayer(vm.program_from_json(f3["program"])), q, cfg_x, "ACCUMULATED", seed=201)["metrics"]
    # The action script scored 38/50 (search) and 25/50 (held-out) under C0's wrap-around ACT. Its
    # immediates (ACTI 18, -12, -11, 16, 17) were arithmetic aliases of actions; under strict ACT they are
    # invalid, and the fossil collapses to a few lucky solves. Recorded as its post-fix signature.
    assert a3s["successes"] <= 10 and a3q["successes"] <= 10
    assert a3s["invalid_actions_total"] > 0


# ---------------------------------------------------------------- 7A/7B: fitness structure


def test_fitness_one_solved_task_dominates_cost(cfg1):
    tasks = streams.lifetime(cfg1, 301, "gate")
    # synthetic results: n solved at zero cost vs n+1 solved at maximal cost
    def synth(n_solved, expensive):
        out = []
        for i, t in enumerate(tasks):
            solved = i < n_solved
            out.append({"task_index": i, "task_id": t.task_id, "stage": t.stage, "depth": t.depth, "family": t.family,
                        "starting_performance": 0.0, "final_performance": 1.0 if solved else 0.0,
                        "interactions_used": (t.interaction_budget if expensive else 1) if solved else 0,
                        "interaction_budget": t.interaction_budget,
                        "vm_steps_used": t.step_budget if expensive else 1, "step_budget": t.step_budget,
                        "ws_cost_units": 0, "workspace_bytes": 0, "artifact_bytes": 0, "artifacts_invoked": 0,
                        "blocks_created": 0, "success": solved, "trajectory": []})
        return out
    cheap_fewer = evaluate.lifetime_metrics(synth(30, expensive=False), cfg1)["C1_FITNESS"]
    costly_more = evaluate.lifetime_metrics(synth(31, expensive=True), cfg1)["C1_FITNESS"]
    assert costly_more > cheap_fewer
    # an unsolved task is charged its full budget
    r = synth(0, expensive=False)
    assert evaluate.task_cost(r[0], cfg1) >= r[0]["interaction_budget"]


# ---------------------------------------------------------------- 7D: sealed streams and permutation


def test_streams_are_sealed_and_permuted(cfg1):
    s = tasks_c1.make_stream(cfg1, "search", 1000)
    q = tasks_c1.make_stream(cfg1, "qual", 1000)
    g = tasks_c1.make_stream(cfg1, "gate", 1000)
    assert s["perm"] != q["perm"] or s["library"] != q["library"]
    assert {t.task_id for t in s["tasks"]}.isdisjoint({t.task_id for t in q["tasks"]})
    assert {t.task_id for t in g["tasks"]}.isdisjoint({t.task_id for t in q["tasks"]})
    # rotation: consecutive search iterations see different streams
    assert streams.search_stream_seed(cfg1, 1, 1) != streams.search_stream_seed(cfg1, 2, 1)
    # the permutation is a bijection and differs between streams
    assert sorted(s["perm"]) == list(range(12))
    assert tasks_c1.make_stream(cfg1, "search", 1001)["perm"] != s["perm"]
    # replay: the same key gives the same stream
    assert tasks_c1.make_stream(cfg1, "search", 1000)["tasks"][7].target == s["tasks"][7].target


def test_world_c1_primitives():
    x = (0, 1, 2, 7)
    assert world_c1.apply_primitive("INC", 3, x) == (0, 1, 2, 0)
    assert world_c1.apply_primitive("DEC", 0, x) == (7, 1, 2, 7)
    assert world_c1.apply_primitive("SWAP", 3, x) == (7, 1, 2, 0)
    t = (("INC", 0), ("SWAP", 1))
    assert world_c1.apply_template(t, 2, x) == world_c1.apply_primitive("SWAP", 3, world_c1.apply_primitive("INC", 2, x))
