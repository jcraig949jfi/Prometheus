"""World registry: a task names its world; the environment dispatches through here.

A world exposes num_actions(task), apply_action(task, action, x) and B
(the modulus). Performance is world-independent (Hamming).
"""

from __future__ import annotations

from . import world as world_c0


class _C0:
    B = world_c0.B

    @staticmethod
    def num_actions(task) -> int:
        return world_c0.NUM_OPS

    @staticmethod
    def apply_action(task, action: int, x: tuple) -> tuple:
        return world_c0.apply_op(action, x)


_REGISTRY = {"c0": _C0}


def register(world_id: str, impl) -> None:
    _REGISTRY[world_id] = impl


def get(world_id: str):
    if world_id == "c1" and "c1" not in _REGISTRY:
        from . import world_c1  # noqa: F401  (registers itself on import)
    return _REGISTRY[world_id]


def performance(x: tuple, target: tuple) -> float:
    return 1.0 - sum(1 for p, q in zip(x, target) if p != q) / float(len(target))
