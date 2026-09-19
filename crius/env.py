"""One task's interaction surface: what a Player can observe and do, and what is metered.

TaskRun exposes only the public task fields. Actions are integers: values in
[0, NUM_OPS) apply a hidden operation (one interaction); NUM_OPS returns the
object to the task start (no interaction, DESIGN_C0 C6). Compute is charged
through charge(); the task ends on success, on an exhausted interaction or
step budget, or when the Player halts.
"""

from __future__ import annotations

from . import worlds


class TaskOver(Exception):
    """Raised by TaskRun when the task has ended; Players must stop."""


class TaskRun:
    def __init__(self, task, task_index: int, step_budget: int = None, post_success_steps: int = 200):
        self.task = task
        self.post_success_steps = post_success_steps
        self.grace_left = 0
        self.task_index = task_index
        self.start = task.start
        self.target = task.target
        self.interaction_budget = task.interaction_budget
        self.step_budget = task.step_budget if step_budget is None else step_budget
        self.current = task.start
        self.previous = task.start
        self.interactions = 0
        self.steps = 0
        self.store_units = 0
        self.success = False
        self.over = False
        self.halted = False
        self.end_reason = None
        self.starting_performance = worlds.performance(task.start, task.target)
        self.best_performance = self.starting_performance
        self.last_action = -1
        self.trajectory = []  # (action, resulting object) for the replay hash
        self.n_resets = 0
        self.status = 0
        self.invalid_actions = 0
        self.success_in_block = False
        self.last_primitive = -1   # (kind*L + pos) of the last executed primitive, -1 before any / after reset
        self.post_success_actions = 0
        self.world = worlds.get(getattr(task, "world_id", "c0"))
        self.num_actions = self.world.num_actions(task)
        self.reset_action = self.num_actions

    # ------------------------------------------------------------ observation
    def observation(self) -> dict:
        return {
            "current": self.current,
            "target": self.target,
            "interactions_left": self.interaction_budget - self.interactions,
            "num_ops": self.num_actions,
            "task_index": self.task_index,
            "steps_left": self.step_budget - self.steps - self.store_units,
            "last_delta": tuple((c - p) % self.world.B for c, p in zip(self.current, self.previous)),
            "last_action": self.last_action,
            "last_primitive": self.last_primitive,
        }

    # ------------------------------------------------------------ actions
    def valid_action(self, value) -> bool:
        return isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= self.reset_action

    def act(self, value):
        if self.over:
            raise TaskOver()
        if not self.valid_action(value):
            # DESIGN_C1 s4: nothing but an in-range int is an action; no aliasing, no reset
            self.status = 2
            self.invalid_actions += 1
            return self.current
        if self.success:
            # C2: actions after success are ignored no-ops during the grace (no interaction, no reset), so a
            # program can close a recording after an early success; the grace still bounds compute.
            self.post_success_actions += 1
            self.status = 2
            return self.current
        v = value
        if v == self.reset_action:
            self.previous = self.current
            self.current = self.start
            self.last_primitive = -1
            self.last_action = v
            self.n_resets += 1
            self.trajectory.append((v, self.current))
            return self.current
        if self.interactions >= self.interaction_budget:
            self._end("interaction_budget")
        self.previous = self.current
        self.current = self.world.apply_action(self.task, v, self.current)
        prim = getattr(self.world, "primitive_of_action", None)
        self.last_primitive = prim(self.task, v) if prim else -1
        self.interactions += 1
        self.last_action = v
        self.trajectory.append((v, self.current))
        p = worlds.performance(self.current, self.target)
        if p > self.best_performance:
            self.best_performance = p
        if self.current == self.target:
            self.success = True
            self.end_reason = "success"
            self.grace_left = self.post_success_steps
            return self.current
        if self.interactions >= self.interaction_budget:
            self._end("interaction_budget")
        return self.current

    def charge(self, units: int = 1):
        """Meter compute. Ends the task when the step budget is exhausted."""
        if self.over:
            raise TaskOver()
        self.steps += units
        if self.success:
            self.grace_left -= units
            if self.grace_left <= 0:
                self._end("success")
        if self.steps >= self.step_budget:
            self._end("step_budget")

    def charge_store(self, units: int):
        """Meter workspace/block cost units against the step budget without counting them as VM steps."""
        if self.over:
            raise TaskOver()
        self.store_units += units
        if self.steps + self.store_units >= self.step_budget:
            self._end("step_budget")

    def halt(self):
        self.halted = True
        self._end("halt")

    def _end(self, reason: str):
        if not self.over:
            self.over = True
            if not self.success:
                self.end_reason = reason
        raise TaskOver()

    def final_performance(self) -> float:
        return worlds.performance(self.current, self.target)
