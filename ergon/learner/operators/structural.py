"""structural operator — DAG topology mutation.

Per pivot/ergon_learner_proposal_v8.md:

The structural operator mutates a parent genome's DAG topology:
  - add_node: append a new atom to the DAG
  - remove_node: delete an existing atom (and rewire its consumers)
  - swap_node: replace one atom with another (preserving arity)
  - rewire_edge: change a node's arg_binding from one ref/literal to another

Type-discipline preserved: any "ref" binding always points to a
lower-indexed node (DAG invariant); arg_types are checked against
the source's return_type when available.

Lineage tag: "structural"
"""
from __future__ import annotations

import random
from typing import Any, Dict, Optional

from ergon.learner.genome import (
    Genome,
    MAX_ATOMS,
    MAX_DEPTH,
    MAX_WIDTH,
    NodeRef,
    validate_dag_invariants,
)
from ergon.learner.operators.base import (
    fresh_genome,
    make_node_for_atom,
    sample_args_for_atom,
)


class StructuralOperator:
    """Mutate DAG topology while preserving type-discipline."""

    operator_class = "structural"

    def __init__(self,
                 add_prob: float = 0.4,
                 remove_prob: float = 0.2,
                 swap_prob: float = 0.3,
                 rewire_prob: float = 0.1):
        total = add_prob + remove_prob + swap_prob + rewire_prob
        # Normalize to a probability distribution
        self._mutation_weights = (
            add_prob / total,
            remove_prob / total,
            swap_prob / total,
            rewire_prob / total,
        )

    def mutate(
        self,
        parent: Optional[Genome],
        rng: random.Random,
        atom_pool: Dict[str, Any],
    ) -> Genome:
        """Apply one structural mutation to the parent.

        If parent is None or has 0 nodes, fall back to fresh_genome.
        """
        if parent is None or len(parent.nodes) == 0:
            return fresh_genome(atom_pool, rng, "structural")

        # Choose which kind of structural mutation to apply
        choice = rng.random()
        cumulative = 0.0
        for kind, weight in zip(
            ("add", "remove", "swap", "rewire"),
            self._mutation_weights,
        ):
            cumulative += weight
            if choice < cumulative:
                op = kind
                break
        else:
            op = "swap"  # fallback

        # Apply chosen mutation
        if op == "add" and len(parent.nodes) < MAX_ATOMS:
            child = self._add_node(parent, atom_pool, rng)
        elif op == "remove" and len(parent.nodes) > 1:
            child = self._remove_node(parent, atom_pool, rng)
        elif op == "swap":
            child = self._swap_node(parent, atom_pool, rng)
        elif op == "rewire":
            child = self._rewire_edge(parent, atom_pool, rng)
        else:
            # Operation not applicable; fall back to swap
            child = self._swap_node(parent, atom_pool, rng)

        # If mutation produced an empty genome (shouldn't happen but defensive),
        # fall back to fresh
        if len(child.nodes) == 0:
            return fresh_genome(atom_pool, rng, "structural")

        validate_dag_invariants(child)
        return child

    # ------------------------------------------------------------------
    # Mutation primitives
    # ------------------------------------------------------------------

    def _add_node(
        self,
        parent: Genome,
        atom_pool: Dict[str, Any],
        rng: random.Random,
    ) -> Genome:
        """Append a new atom to the parent's DAG."""
        callable_refs = list(atom_pool.keys())
        new_callable = rng.choice(callable_refs)
        atom = atom_pool[new_callable]
        arity = atom["arity"]

        # New node's arg bindings: mix of literals and refs to existing nodes
        existing_indices = list(range(len(parent.nodes)))
        bindings = []
        for _ in range(arity):
            if existing_indices and rng.random() < 0.5:
                # Use a ref binding
                src = rng.choice(existing_indices)
                bindings.append(("ref", src))
            else:
                # Sample a literal value
                args = sample_args_for_atom(new_callable, atom_pool, rng)
                if args:
                    bindings.append(("literal", args[0]))
                else:
                    bindings.append(("literal", rng.randint(1, 10)))

        new_node = NodeRef(
            callable_ref=new_callable,
            arg_bindings=tuple(bindings),
        )

        return Genome(
            nodes=parent.nodes + (new_node,),
            target_predicate=parent.target_predicate,
            mutation_operator_class="structural",
            parent_hash=parent.content_hash(),
        )

    def _remove_node(
        self,
        parent: Genome,
        atom_pool: Dict[str, Any],
        rng: random.Random,
    ) -> Genome:
        """Remove a node; rewire its consumers to use the lowest-indexed available
        ancestor or a literal fallback. Removing the root replaces it with the
        last remaining node as the new root.
        """
        n = len(parent.nodes)
        # Don't allow removing the only node
        if n <= 1:
            return parent

        idx_to_remove = rng.randint(0, n - 1)

        # Build new node list, skipping idx_to_remove and re-indexing refs
        new_nodes = []
        index_map: Dict[int, int] = {}
        new_idx = 0
        for old_idx, node in enumerate(parent.nodes):
            if old_idx == idx_to_remove:
                continue
            index_map[old_idx] = new_idx
            new_idx += 1

        # Rewrite arg_bindings for surviving nodes
        for old_idx, node in enumerate(parent.nodes):
            if old_idx == idx_to_remove:
                continue
            new_bindings = []
            for kind, value in node.arg_bindings:
                if kind == "ref":
                    src = int(value)
                    if src == idx_to_remove:
                        # Source was deleted; replace with literal
                        new_bindings.append(("literal", rng.randint(1, 10)))
                    elif src < idx_to_remove:
                        # Index unchanged
                        new_bindings.append(("ref", src))
                    else:
                        # Index decremented
                        new_bindings.append(("ref", index_map[src]))
                else:
                    new_bindings.append((kind, value))
            new_nodes.append(NodeRef(
                callable_ref=node.callable_ref,
                arg_bindings=tuple(new_bindings),
            ))

        return Genome(
            nodes=tuple(new_nodes),
            target_predicate=parent.target_predicate,
            mutation_operator_class="structural",
            parent_hash=parent.content_hash(),
        )

    def _swap_node(
        self,
        parent: Genome,
        atom_pool: Dict[str, Any],
        rng: random.Random,
    ) -> Genome:
        """Replace one node's callable_ref with a different atom of compatible arity."""
        if not parent.nodes:
            return parent
        idx = rng.randint(0, len(parent.nodes) - 1)
        old_node = parent.nodes[idx]
        old_arity = len(old_node.arg_bindings)

        # Find an atom of the same arity (if possible)
        candidates = [
            cref for cref, atom in atom_pool.items()
            if atom["arity"] == old_arity and cref != old_node.callable_ref
        ]
        if not candidates:
            # No compatible swap; return parent unchanged with new operator class
            return Genome(
                nodes=parent.nodes,
                target_predicate=parent.target_predicate,
                mutation_operator_class="structural",
                parent_hash=parent.content_hash(),
            )

        new_callable = rng.choice(candidates)
        new_node = NodeRef(
            callable_ref=new_callable,
            arg_bindings=old_node.arg_bindings,  # preserve bindings
        )

        new_nodes = list(parent.nodes)
        new_nodes[idx] = new_node

        return Genome(
            nodes=tuple(new_nodes),
            target_predicate=parent.target_predicate,
            mutation_operator_class="structural",
            parent_hash=parent.content_hash(),
        )

    def _rewire_edge(
        self,
        parent: Genome,
        atom_pool: Dict[str, Any],
        rng: random.Random,
    ) -> Genome:
        """Change one node's arg_binding from ref->literal or literal->ref."""
        if not parent.nodes:
            return parent
        # Find a node with at least one arg-binding
        candidates = [(i, n) for i, n in enumerate(parent.nodes) if n.arg_bindings]
        if not candidates:
            return parent
        node_idx, node = rng.choice(candidates)
        binding_idx = rng.randrange(len(node.arg_bindings))
        old_kind, old_value = node.arg_bindings[binding_idx]

        # Toggle: ref<->literal
        if old_kind == "ref":
            new_binding = ("literal", rng.randint(1, 100))
        else:  # was literal
            available_refs = list(range(node_idx))
            if available_refs:
                new_binding = ("ref", rng.choice(available_refs))
            else:
                # No ref available; resample literal
                new_binding = ("literal", rng.randint(1, 100))

        new_bindings = list(node.arg_bindings)
        new_bindings[binding_idx] = new_binding
        new_node = NodeRef(
            callable_ref=node.callable_ref,
            arg_bindings=tuple(new_bindings),
        )

        new_nodes = list(parent.nodes)
        new_nodes[node_idx] = new_node

        return Genome(
            nodes=tuple(new_nodes),
            target_predicate=parent.target_predicate,
            mutation_operator_class="structural",
            parent_hash=parent.content_hash(),
        )
