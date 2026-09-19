"""Charter section 17: what must be proven before any long search.

Run: python -m pytest crius/tests -q
"""

import copy
import json
import os
import random

import pytest

from crius import artifacts, baselines, evaluate, receipts, tasks, vm, world, workspace
from crius.env import TaskRun, TaskOver
from crius.player import VMPlayer, run_task

HERE = os.path.dirname(os.path.abspath(__file__))
CFG_PATH = os.path.join(HERE, "..", "configs", "c0.json")


@pytest.fixture(scope="module")
def cfg():
    return receipts.load_config(CFG_PATH)


@pytest.fixture(scope="module")
def search_tasks(cfg):
    return tasks.make_lifetime(cfg, 101, "search")


# ---------------------------------------------------------------- 1. replay


def test_same_inputs_and_seed_replay_exactly(cfg, search_tasks):
    for name in ("ENUMERATE_VM", "CACHE_REUSE", "ADAPTIVE", "RANDOM"):
        a = evaluate.run_lifetime(baselines.make_baseline(name), search_tasks, cfg, "ACCUMULATED", seed=101)
        b = evaluate.run_lifetime(baselines.make_baseline(name), search_tasks, cfg, "ACCUMULATED", seed=101)
        assert a["replay_hash"] == b["replay_hash"], name
        assert a["metrics"] == b["metrics"], name
    t1 = tasks.make_lifetime(cfg, 101, "search")
    t2 = tasks.make_lifetime(cfg, 101, "search")
    assert tasks.task_sequence_hash(t1) == tasks.task_sequence_hash(t2)
    assert tasks.task_sequence_hash(t1) != tasks.task_sequence_hash(tasks.make_lifetime(cfg, 102, "search"))


# ---------------------------------------------------------------- 2/3. persistence and reset


def test_workspace_persists_across_tasks_and_resets_between_lifetimes(cfg, search_tasks):
    p = baselines.make_baseline("CACHE_REUSE")
    acc = evaluate.run_lifetime(p, search_tasks, cfg, "ACCUMULATED", seed=101)
    hist = acc["workspace_history"]
    assert hist[0]["cells_written"] > 0
    assert hist[-1]["cells_written"] >= hist[0]["cells_written"]
    # persistence has an observable consequence: fewer interactions than FRESH
    fresh = evaluate.run_lifetime(p, search_tasks, cfg, "FRESH", seed=101)
    assert acc["metrics"]["interactions_total"] < fresh["metrics"]["interactions_total"]
    # a second lifetime with a new Workspace starts empty: identical to the first
    again = evaluate.run_lifetime(baselines.make_baseline("CACHE_REUSE"), search_tasks, cfg, "ACCUMULATED", seed=101)
    assert again["replay_hash"] == acc["replay_hash"]
    # a Python player carries nothing outside the workspace: RESET at every task == FRESH
    cfg2 = copy.deepcopy(cfg)
    cfg2["controls"]["reset_points_stages"] = ["A", "B", "C", "D", "E"]
    every = evaluate.run_lifetime(p, search_tasks, cfg2, "WORKSPACE_RESET", seed=101)
    # reset at stage starts only, so compare the first task of each stage with FRESH
    firsts = tasks.stage_first_indices(search_tasks).values()
    for i in firsts:
        assert every["task_results"][i]["interactions_used"] == fresh["task_results"][i]["interactions_used"]


# ---------------------------------------------------------------- 4. partitions


def test_qualification_partitions_do_not_leak_into_search(cfg):
    parts = tasks.build_partitions(cfg)
    search_comps = set(parts["search_cd_pairs"]) | set(parts["search_e_pairs"]) | set(parts["search_cd_triples"]) | set(parts["search_e_triples"])
    qual_comps = set(parts["qual_pairs"]) | set(parts["qual_triples"])
    assert not (search_comps & qual_comps)
    assert set(parts["reversed_pairs"]) <= qual_comps
    assert set(parts["new_combination_triples"]) <= qual_comps
    seen_in_search = set()
    for seed in range(1, 60):
        for t in tasks.make_lifetime(cfg, seed, "search"):
            if t.depth >= 2:
                seen_in_search.add(t.composition)
                assert 5 not in t.composition, "op5 compositions must be absent from search"
                assert t.depth <= 3
    assert not (seen_in_search & qual_comps)
    q = tasks.make_lifetime(cfg, 201, "heldout_v1")
    fams = {t.family for t in q}
    for f in ("reversed_pair", "heldout_pair", "heldout_triple", "new_combination", "absent_op5_d2", "absent_op5_d3", "depth4"):
        assert f in fams, f
    for t in q:
        if t.depth >= 2 and 5 not in t.composition and t.depth <= 3:
            assert t.composition not in search_comps


# ---------------------------------------------------------------- 5. artifacts deterministic


def test_artifact_invocation_is_deterministic(cfg, search_tasks):
    src = """
        BLK_NEW R0
        CONST R1, 2
        INPUT R2, num_ops
        ; instruction tuple (ACTI 1 0 0) as a vector: build via CONST and VSET is long; use recording
        BLK_REC_BEGIN
        ACTI 1
        ACTI 3
        BLK_REC_END R3
        ACTI 6
        BLK_INVOKE R3
        BLK_INVOKE R3
        HALT
    """
    prog = vm.assemble(src)
    # a depth-3 task that the sequence (1,3) does not solve by coincidence
    task = next(t for t in search_tasks if t.depth == 3 and world.apply_sequence((1, 3), t.start) != t.target
                and world.apply_sequence((1, 3, 1, 3), t.start) != t.target)
    outs = []
    for _ in range(2):
        ws = workspace.Workspace.empty(cfg)
        blocks = artifacts.BlockStore.empty(cfg)
        r = run_task(VMPlayer(prog), task, 0, ws, blocks)
        outs.append((r["trajectory"], r["artifacts_invoked"], blocks.snapshot()))
    assert outs[0] == outs[1]
    traj = [a for a, _ in outs[0][0]]
    assert traj == [1, 3, 6, 1, 3, 1, 3]
    assert outs[0][1] == 2
    assert 1 in outs[0][2]["blocks"] and outs[0][2]["blocks"][1][0] == [(vm.OP["ACTI"], 1, 0, 0), (vm.OP["ACTI"], 3, 0, 0)]


# ---------------------------------------------------------------- 6. deletion and ablation remove effects


def test_artifact_deletion_and_ablation_remove_effects(cfg):
    ws = workspace.Workspace.empty(cfg)
    blocks = artifacts.BlockStore.empty(cfg)
    bid = blocks.create([(vm.OP["ACTI"], 2, 0, 0)])
    task = tasks.make_task(cfg, random.Random(5), (2,), "A", "primitive", 0)
    env = TaskRun(task, 0)
    st = vm.VMState(env, ws, blocks)
    assert vm.invoke_block(bid, st) is True
    assert env.interactions == 1 and env.success
    blocks.delete(bid)
    env2 = TaskRun(task, 0)
    st2 = vm.VMState(env2, ws, blocks)
    assert vm.invoke_block(bid, st2) is False
    assert env2.interactions == 0
    # ablation through the control: removing every block from ADAPTIVE's snapshot changes its remainder
    st_tasks = tasks.make_lifetime(cfg, 101, "search")
    c = evaluate.causal_controls(baselines.make_baseline("ADAPTIVE"), st_tasks, cfg, seed=101)
    assert c["blocks_at_snapshot"]
    assert c["ARTIFACT_ABLATION_ALL"]["artifacts_invoked_total"] < c["ACCUMULATED_remainder"]["artifacts_invoked_total"]
    assert c["ARTIFACT_ABLATION_ALL"]["adaptation_curve"] != c["ACCUMULATED_remainder"]["adaptation_curve"]


# ---------------------------------------------------------------- 7. transplant copies only the requested state


def test_transplant_copies_only_requested_state(cfg, search_tasks):
    p = baselines.make_baseline("ADAPTIVE")
    snap_i = tasks.stage_first_indices(search_tasks)["D"]
    acc = evaluate.run_lifetime(p, search_tasks, cfg, "ACCUMULATED", seed=101, snapshot_index=snap_i)
    snap = acc["snapshot"]
    ws = workspace.Workspace.empty(cfg)
    blocks = artifacts.BlockStore.empty(cfg)
    blocks.restore(snap["blocks"])
    assert ws.bytes_used() == 0 and len(blocks.blocks) == len(snap["blocks"]["blocks"])
    ws2 = workspace.Workspace.empty(cfg)
    ws2.restore(snap["ws"])
    assert ws2.cells == snap["ws"]["cells"]
    # restoring is a copy: mutating the restored store does not touch the snapshot
    ws2.write(0, (9, 9, 9, 9))
    assert snap["ws"]["cells"].get(0) != (9, 9, 9, 9)
    c = evaluate.causal_controls(p, search_tasks, cfg, seed=101)
    assert c["FULL_WORKSPACE_TRANSPLANT"]["adaptation_curve"] == c["ACCUMULATED_remainder"]["adaptation_curve"]
    assert c["ARTIFACT_TRANSPLANT"]["interactions_total"] > c["FULL_WORKSPACE_TRANSPLANT"]["interactions_total"]


# ---------------------------------------------------------------- 8. program code does not change


def test_program_code_does_not_change_during_lifetime(cfg, search_tasks):
    prog = vm.enumerate_program()
    before = json.dumps(vm.program_to_json(prog))
    p = VMPlayer(prog)
    h0 = p.spec_hash()
    evaluate.run_lifetime(p, search_tasks, cfg, "ACCUMULATED", seed=101)
    assert json.dumps(vm.program_to_json(p.program)) == before
    assert p.spec_hash() == h0
    # a block that patches ITSELF changes the block, never the program
    src = """
        BLK_NEW R0
        BLK_REC_BEGIN
        ACTI 0
        BLK_REC_END R1
        BLK_INVOKE R1
        HALT
    """
    prog2 = vm.assemble(src)
    p2 = VMPlayer(prog2)
    before2 = list(p2.program)
    evaluate.run_lifetime(p2, search_tasks[:3], cfg, "ACCUMULATED", seed=1)
    assert p2.program == before2


# ---------------------------------------------------------------- 9. receipts reconstruct the configuration


def test_receipts_reconstruct_the_executed_configuration(cfg, search_tasks, tmp_path):
    meta = receipts.run_meta(cfg, CFG_PATH)
    p = baselines.make_baseline("ENUMERATE_VM")
    life = evaluate.run_lifetime(p, search_tasks, cfg, "ACCUMULATED", seed=101)
    rec = receipts.lifetime_receipt(meta, p, search_tasks, 101, "search", life)
    path = str(tmp_path / "r.json")
    receipts.write_json(path, rec)
    back = receipts.read_json(path)
    assert back["config_hash"] == receipts.config_hash(cfg)
    assert back["world_fingerprint"] == world.world_fingerprint()
    # rebuild the tasks from the receipt's seed and suite and re-run: same replay hash
    t2 = tasks.make_lifetime(cfg, back["seed"], back["search_or_qualification"])
    assert tasks.task_sequence_hash(t2) == back["task_sequence_hash"]
    p2 = VMPlayer(vm.program_from_json(back["candidate_spec"]["program"]))
    assert p2.spec_hash() == back["candidate_hash"]
    life2 = evaluate.run_lifetime(p2, t2, cfg, back["condition"], seed=back["seed"])
    assert life2["replay_hash"] == back["replay_hash"]
    assert life2["metrics"]["C0_EFFICIENCY"] == back["metrics"]["C0_EFFICIENCY"]


# ---------------------------------------------------------------- positive control benefits


def test_positive_control_benefits_from_accumulated_machinery(cfg):
    for seed in cfg["seeds"]["search"]:
        t = tasks.make_lifetime(cfg, seed, "search")
        for name in ("CACHE_REUSE", "ADAPTIVE"):
            bat = evaluate.full_battery(baselines.make_baseline(name), t, cfg, seed=seed)
            a, f = bat["ACCUMULATED"]["metrics"], bat["FRESH"]["metrics"]
            assert a["C0_EFFICIENCY"] > 1.5 * f["C0_EFFICIENCY"], (name, seed)
            assert sum(bat["reuse_gain"]) > 1000, (name, seed)
            assert bat["WORKSPACE_SCRAMBLED"]["metrics"]["C0_EFFICIENCY"] < 0.5 * a["C0_EFFICIENCY"]
            assert bat["causal"]["COMPUTE_MATCHED"]["interactions_total"] > bat["causal"]["ACCUMULATED_remainder"]["interactions_total"]
            assert bat["causal"]["STORAGE_MATCHED"]["interactions_total"] > bat["causal"]["ACCUMULATED_remainder"]["interactions_total"]
        # the brute-force control gains nothing from its workspace
        bat = evaluate.full_battery(baselines.make_baseline("ENUMERATE_VM"), t, cfg, seed=seed)
        assert sum(bat["reuse_gain"]) == 0.0
        assert bat["ACCUMULATED"]["metrics"] == bat["FRESH"]["metrics"]


# ---------------------------------------------------------------- cheat control on the assay itself


def test_cheat_control_workspace_channel_is_observable(cfg, search_tasks):
    """Success deliberately injected through the workspace must be visible to the metric."""
    # A player that writes the answer for task i+1 cannot exist (targets are unknown), so the cheat
    # is a Python player that stores the composition it just used and replays it when the needed
    # delta matches exactly: FRESH must then be strictly worse than ACCUMULATED on repeated deltas.
    class Cheat(baselines.PythonPlayer):
        name = "CHEAT"

        def run(self, env, st):
            ws = st.ws
            need = baselines._delta(env.target, env.start)
            addr = ws.find(need)
            if addr >= 0:
                seq = ws.read(addr + 1)
                env.act(world.RESET_ACTION)
                for op in seq:
                    env.act(op)
                if env.success:
                    return
            import itertools
            for depth in range(1, 4):
                for seq in itertools.product(range(world.NUM_OPS), repeat=depth):
                    env.charge(1)
                    env.act(world.RESET_ACTION)
                    for op in seq:
                        env.act(op)
                    if env.success:
                        base = ws.allocate(2)
                        ws.write(base, need)
                        ws.write(base + 1, tuple(seq))
                        return
            env.halt()

    # repeat the same tasks twice inside one lifetime so exact deltas recur
    doubled = list(search_tasks[:10]) + list(search_tasks[:10])
    acc = evaluate.run_lifetime(Cheat(), doubled, cfg, "ACCUMULATED", seed=1)
    fresh = evaluate.run_lifetime(Cheat(), doubled, cfg, "FRESH", seed=1)
    second_half_acc = sum(acc["metrics"]["adaptation_curve"][10:])
    second_half_fresh = sum(fresh["metrics"]["adaptation_curve"][10:])
    assert second_half_acc < second_half_fresh
    assert acc["metrics"]["C0_EFFICIENCY"] > fresh["metrics"]["C0_EFFICIENCY"]


# ---------------------------------------------------------------- VM bounds


def test_vm_bounds_hold(cfg, search_tasks):
    # an infinite loop is cut by the step budget, never hangs
    prog = vm.assemble("L:\n JMP L")
    ws = workspace.Workspace.empty(cfg)
    blocks = artifacts.BlockStore.empty(cfg)
    r = run_task(VMPlayer(prog), search_tasks[0], 0, ws, blocks)
    assert r["end_reason"] == "step_budget" and r["vm_steps_used"] == search_tasks[0].step_budget
    # recursion depth is bounded
    src = """
        BLK_NEW R0
        CONST R1, 0
        ; block 0 invokes block 0: append (BLK_INVOKE R1) = (opcode, 1, 0, 0)
        CONST R2, %d
        INPUT R3, current
        VSET R3, R1, R2
        CONST R4, 1
        VSET R3, R4, R4
        CONST R5, 2
        CONST R6, 0
        VSET R3, R5, R6
        CONST R5, 3
        VSET R3, R5, R6
        BLK_APPEND R0, R3
        BLK_INVOKE R0
        HALT
    """ % vm.OP["BLK_INVOKE"]
    r = run_task(VMPlayer(vm.assemble(src)), search_tasks[0], 0, workspace.Workspace.empty(cfg), artifacts.BlockStore.empty(cfg))
    assert r["end_reason"] in ("halt", "step_budget")
    assert blocks.max_blocks == cfg["workspace"]["max_blocks"]
    # capacity is bounded: writes beyond capacity fail and are counted
    w = workspace.Workspace(cells=256, capacity_bytes=8)
    assert w.write(0, (1, 2, 3, 4)) and w.write(1, (1, 2, 3, 4))
    assert not w.write(2, 1)
    assert w.failed_writes == 1 and w.bytes_used() == 8
