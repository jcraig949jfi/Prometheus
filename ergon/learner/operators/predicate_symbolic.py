"""predicate_symbolic operator — domain-specific symbolic mutation for predicates.

Per Iter 14 (queued from Iter 11): the standard SymbolicOperator only
mutates literal arg values. Predicate atoms in the obstruction-domain
have arity=0 (no literal args) — `predicate:n_steps=5` etc. So
SymbolicOperator is a no-op on predicate atoms.

PredicateSymbolicOperator handles this gap: for predicate-domain genomes,
it mutates by SWAPPING ATOM REFS rather than mutating arg values. E.g.,
swap `predicate:neg_x=3` for `predicate:neg_x=5` (same feature, different
value). Or swap `predicate:n_steps=5` for `predicate:n_steps=4` (different
nearby value).

This restores the symbolic operator's productive role in the predicate-
discovery domain: local exploration of value-space without changing the
predicate's structural shape.

Lineage tag: "symbolic" (engine-compatible — uses the same lineage tag
as the standard symbolic operator since it serves the same role).
"""
from __future__ import annotations

import random
import re
from typing import Any, Dict, List, Optional, Tuple

from ergon.learner.genome import Genome, NodeRef, validate_dag_invariants
from ergon.learner.operators.base import fresh_genome


# Pattern: "predicate:<feature>=<value>"
PREDICATE_ATOM_RE = re.compile(r"^predicate:([a-z_]+)=(.+)$")


class PredicateSymbolicOperator:
    """Symbolic mutation for predicate-domain genomes.

    For each predicate atom node, with mutation_rate probability, swap the
    atom for one with a different value but the same feature.
    """

    operator_class = "symbolic"

    def __init__(self, mutation_rate_per_node: float = 0.5):
        self.mutation_rate = mutation_rate_per_node

    def mutate(
        self,
        parent: Optional[Genome],
        rng: random.Random,
        atom_pool: Dict[str, Any],
    ) -> Genome:
        """Mutate parent by swapping predicate-atom values."""
        if parent is None or not parent.nodes:
            return fresh_genome(atom_pool, rng, "symbolic")

        # Group atoms in the pool by feature
        feature_to_atoms: Dict[str, List[str]] = {}
        for cref in atom_pool.keys():
            m = PREDICATE_ATOM_RE.match(cref)
            if m:
                feat = m.group(1)
                feature_to_atoms.setdefault(feat, []).append(cref)

        # If no predicate atoms in pool, fall back to fresh genome
        if not feature_to_atoms:
            return fresh_genome(atom_pool, rng, "symbolic")

        new_nodes: List[NodeRef] = []
        any_mutation = False

        for node in parent.nodes:
            m = PREDICATE_ATOM_RE.match(node.callable_ref)
            if not m or rng.random() >= self.mutation_rate:
                # Non-predicate atom OR not selected — keep as-is
                new_nodes.append(node)
                continue

            feat = m.group(1)
            candidates = [
                c for c in feature_to_atoms.get(feat, [])
                if c != node.callable_ref
            ]
            if not candidates:
                new_nodes.append(node)
                continue

            new_callable = rng.choice(candidates)
            new_nodes.append(NodeRef(
                callable_ref=new_callable,
                arg_bindings=node.arg_bindings,
            ))
            any_mutation = True

        # If we didn't mutate anything, force-mutate one node to ensure child differs
        if not any_mutation and new_nodes:
            for idx, node in enumerate(new_nodes):
                m = PREDICATE_ATOM_RE.match(node.callable_ref)
                if not m:
                    continue
                feat = m.group(1)
                candidates = [
                    c for c in feature_to_atoms.get(feat, [])
                    if c != node.callable_ref
                ]
                if candidates:
                    new_callable = rng.choice(candidates)
                    new_nodes[idx] = NodeRef(
                        callable_ref=new_callable,
                        arg_bindings=node.arg_bindings,
                    )
                    any_mutation = True
                    break

        child = Genome(
            nodes=tuple(new_nodes),
            target_predicate=parent.target_predicate,
            mutation_operator_class="symbolic",
            parent_hash=parent.content_hash(),
        )
        validate_dag_invariants(child)
        return child
