"""uniform operator — strawman null. Pure random over atom_pool.

Per pivot/ergon_learner_proposal_v8.md S6.3:

The uniform operator is the substrate's strawman null baseline. Every
mutation is a fresh random genome with no relationship to the parent.
Per minimum-share enforcement (v8 S3.5.4), uniform is guaranteed >=5%
of all proposals regardless of cell-fill-rate selection pressure.

Lineage tag: "uniform"
"""
from __future__ import annotations

import random
from typing import Any, Dict, Optional

from ergon.learner.genome import Genome
from ergon.learner.operators.base import fresh_genome


class UniformOperator:
    """Strawman null: produce a fresh random genome with no parent relationship."""

    operator_class = "uniform"

    def __init__(self, n_atoms_distribution: Optional[tuple] = None):
        """
        n_atoms_distribution: tuple of (min_atoms, max_atoms) for fresh genome
        size. Defaults to (1, 6) — covers the typical Trial 2 search range.
        """
        self.n_atoms_distribution = n_atoms_distribution or (1, 6)

    def mutate(
        self,
        parent: Optional[Genome],  # ignored — uniform is parentless
        rng: random.Random,
        atom_pool: Dict[str, Any],
    ) -> Genome:
        """Produce a fresh random genome.

        Parent is ignored entirely (per the strawman-null specification).
        """
        n_atoms = rng.randint(*self.n_atoms_distribution)
        return fresh_genome(
            atom_pool=atom_pool,
            rng=rng,
            operator_class="uniform",
            n_atoms=n_atoms,
        )
