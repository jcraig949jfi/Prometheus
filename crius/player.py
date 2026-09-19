"""Players: an executable candidate program, run one task at a time against a Workspace and BlockStore.

VMPlayer runs bytecode (crius/vm.py). PythonPlayer is the base for the
hand-written baselines (crius/baselines.py); a PythonPlayer must keep every
piece of cross-task state in the Workspace or BlockStore it is handed --
instance attributes may not carry state between tasks (tests enforce the
observable consequence: RESET-at-every-task equals FRESH).
"""

from __future__ import annotations

import hashlib

from . import vm, world
from .env import TaskOver, TaskRun


class Player:
    kind = "abstract"
    name = "abstract"

    def spec_hash(self) -> str:
        raise NotImplementedError

    def spec(self) -> dict:
        raise NotImplementedError

    def run(self, env: TaskRun, st: vm.VMState):
        raise NotImplementedError


class VMPlayer(Player):
    kind = "vm"

    def __init__(self, program, name: str = None):
        self.program = list(program)
        self.name = name or ("vm_" + vm.program_hash(self.program))

    def spec_hash(self) -> str:
        return vm.program_hash(self.program)

    def spec(self) -> dict:
        return {"kind": "vm", "program": vm.program_to_json(self.program)}

    def run(self, env, st):
        vm._execute(self.program, st, block_id=-1)


class PythonPlayer(Player):
    kind = "python"

    def spec_hash(self) -> str:
        return hashlib.sha256(("python:" + self.name).encode("ascii")).hexdigest()[:16]

    def spec(self) -> dict:
        return {"kind": "python", "name": self.name}


def run_task(player: Player, task, task_index: int, ws, blocks, step_budget: int = None) -> dict:
    """Run one task. Returns the TaskResult dict (charter s9) plus replay material."""
    env = TaskRun(task, task_index, step_budget=step_budget)
    st = vm.VMState(env, ws, blocks)
    ws_cost0, blk_cost0 = ws.cost, blocks.cost
    blocks.begin_task(task_index)
    n_blocks0 = len(blocks.blocks)
    events0 = len(blocks.events)
    try:
        player.run(env, st)
        if not env.over:
            env.halt()
    except TaskOver:
        pass
    except RecursionError:
        env.over = True
        env.end_reason = "recursion"
    created = sum(1 for e in blocks.events[events0:] if e["kind"] == "create")
    deleted = sum(1 for e in blocks.events[events0:] if e["kind"] == "delete")
    ws_cost = (ws.cost - ws_cost0) + (blocks.cost - blk_cost0)
    return {
        "task_index": task_index,
        "task_id": task.task_id,
        "stage": task.stage,
        "depth": task.depth,
        "family": task.family,
        "starting_performance": env.starting_performance,
        "final_performance": env.best_performance,
        "last_performance": env.final_performance(),
        "interactions_used": env.interactions,
        "interaction_budget": env.interaction_budget,
        "vm_steps_used": env.steps,
        "step_budget": env.step_budget,
        "ws_cost_units": ws_cost,
        "workspace_bytes": ws.bytes_used(),
        "artifact_bytes": blocks.bytes_used(),
        "artifacts_invoked": sum(blocks.task_invocations.values()),
        "artifacts_invoked_distinct": len(blocks.task_invocations),
        "blocks_created": created,
        "blocks_deleted": deleted,
        "blocks_present": len(blocks.blocks),
        "blocks_present_before": n_blocks0,
        "success": env.success,
        "success_in_block": env.success_in_block,
        "end_reason": env.end_reason,
        "resets": env.n_resets,
        "invalid_actions": env.invalid_actions,
        "status_final": env.status,
        "store_trace": dict(st.trace),
        "trajectory": env.trajectory,
    }
