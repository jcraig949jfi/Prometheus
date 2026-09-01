"""D-10 task construction: thin, auditable wrappers over the Foundry's
synthetic exact families.

The only D-10 choices are (a) how many train cases the learner sees and
(b) which (family, difficulty) cells are used. Oracles, parameter
sampling, input ranges and the train/test input disjointness all come
from foundry.tasks.synthetic unchanged. The held-out test split is never
visible to any learner, index, organizer or arm: it is used solely by the
oracle-side endpoint check.
"""
from __future__ import annotations

from foundry.core.seeds import derive_seed
from foundry.tasks.base import ExactTask
from foundry.tasks.synthetic import FAMILY_NAMES, sample_task


def build_task(family: str, seed: int, difficulty: int,
               n_train: int) -> ExactTask:
    """A family task whose learner-visible train split is the FIRST
    n_train cases of the canonical 20. The canonical 20-case test split is
    kept whole for the oracle-side endpoint."""
    t = sample_task(family, seed=seed, difficulty=difficulty)
    if n_train >= len(t.train_cases):
        return t
    return ExactTask(
        train_cases=t.train_cases[:n_train],
        test_cases=t.test_cases,
        admin_metadata=dict(t.admin_metadata),
        provenance={**t.provenance, "d10_n_train": n_train},
    )


def task_pool(family: str, difficulty: int, n_train: int, n: int,
              pool_seed: int, tag: str) -> list[ExactTask]:
    """n independently parameterized tasks of one (family, difficulty)."""
    return [build_task(family, derive_seed(pool_seed, "d10", tag, family,
                                           f"d{difficulty}", f"#{i}"),
                       difficulty, n_train)
            for i in range(n)]
