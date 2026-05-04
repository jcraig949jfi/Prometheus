"""symbolic operator — argument-value mutation.

Per pivot/ergon_learner_proposal_v8.md:

The symbolic operator preserves DAG topology and mutates only the
argument values at leaf nodes. It "bumps" arg values within their type:
  - integer args: bump by ±1, ±2, or resample
  - real args: gaussian perturbation
  - choice-set args (modular_form_label, ec_label): pick a different
    choice from the same set

This is the LOCAL exploration operator — it takes a parent that's in
a productive cell and explores nearby parameter values without changing
the structural composition.

Lineage tag: "symbolic"
"""
from __future__ import annotations

import random
from typing import Any, Dict, List, Optional, Tuple

from ergon.learner.genome import Genome, NodeRef, validate_dag_invariants
from ergon.learner.operators.base import (
    fresh_genome,
    sample_arg,
)


class SymbolicOperator:
    """Mutate argument values while preserving DAG topology."""

    operator_class = "symbolic"

    def __init__(self,
                 mutation_rate_per_arg: float = 0.3,
                 gaussian_sigma: float = 0.1):
        """
        mutation_rate_per_arg: per-argument probability of mutation.
        gaussian_sigma: stddev for real-valued perturbations.
        """
        self.mutation_rate = mutation_rate_per_arg
        self.gaussian_sigma = gaussian_sigma

    def mutate(
        self,
        parent: Optional[Genome],
        rng: random.Random,
        atom_pool: Dict[str, Any],
    ) -> Genome:
        """Mutate parent's argument values; preserve DAG topology."""
        if parent is None or not parent.nodes:
            return fresh_genome(atom_pool, rng, "symbolic")

        new_nodes: List[NodeRef] = []
        any_mutation = False

        for node in parent.nodes:
            atom = atom_pool.get(node.callable_ref)
            arg_samplers = atom["arg_samplers"] if atom else None

            new_bindings: List[Tuple[str, Any]] = []
            for arg_idx, (kind, value) in enumerate(node.arg_bindings):
                if kind != "literal":
                    # Don't mutate ref bindings (those belong to structural)
                    new_bindings.append((kind, value))
                    continue

                # Decide whether to mutate this argument
                if rng.random() >= self.mutation_rate:
                    new_bindings.append((kind, value))
                    continue

                # Mutate this literal value based on its sampler
                sampler_name = (
                    arg_samplers[arg_idx]
                    if arg_samplers and arg_idx < len(arg_samplers)
                    else None
                )
                new_value = self._mutate_value(value, sampler_name, rng)
                new_bindings.append(("literal", new_value))
                any_mutation = True

            new_nodes.append(NodeRef(
                callable_ref=node.callable_ref,
                arg_bindings=tuple(new_bindings),
            ))

        # If we got unlucky and mutated nothing, force-mutate one literal
        # to ensure the child differs from the parent.
        if not any_mutation:
            new_nodes = self._force_one_mutation(new_nodes, atom_pool, rng)

        child = Genome(
            nodes=tuple(new_nodes),
            target_predicate=parent.target_predicate,
            mutation_operator_class="symbolic",
            parent_hash=parent.content_hash(),
        )
        validate_dag_invariants(child)
        return child

    def _mutate_value(
        self,
        old_value: Any,
        sampler_name: Optional[str],
        rng: random.Random,
    ) -> Any:
        """Mutate a single literal value based on its sampler distribution."""
        if isinstance(old_value, int):
            # Integer: bump by ±1, ±2, or resample completely
            roll = rng.random()
            if roll < 0.4:
                delta = rng.choice([-2, -1, 1, 2])
                new = max(1, old_value + delta)
                return new
            else:
                if sampler_name:
                    return sample_arg(sampler_name, rng)
                return rng.randint(1, 100)

        if isinstance(old_value, float):
            # Real: gaussian perturbation
            new = old_value + rng.gauss(0.0, self.gaussian_sigma)
            return new

        if isinstance(old_value, tuple):
            # Complex (real, imag): gaussian both components
            try:
                re, im = old_value
                return (
                    float(re) + rng.gauss(0.0, self.gaussian_sigma),
                    float(im) + rng.gauss(0.0, self.gaussian_sigma),
                )
            except (TypeError, ValueError):
                pass

        if isinstance(old_value, str):
            # Choice-set string (label): resample from sampler
            if sampler_name:
                return sample_arg(sampler_name, rng)
            return old_value

        # Unknown type: resample if possible, else return unchanged
        if sampler_name:
            return sample_arg(sampler_name, rng)
        return old_value

    def _force_one_mutation(
        self,
        nodes: List[NodeRef],
        atom_pool: Dict[str, Any],
        rng: random.Random,
    ) -> List[NodeRef]:
        """Force-mutate one literal binding to ensure the child differs from parent."""
        # Find the first node with a literal binding
        for idx, node in enumerate(nodes):
            for binding_idx, (kind, value) in enumerate(node.arg_bindings):
                if kind == "literal":
                    # Force-mutate this binding
                    atom = atom_pool.get(node.callable_ref)
                    sampler = (
                        atom["arg_samplers"][binding_idx]
                        if atom and binding_idx < len(atom["arg_samplers"])
                        else None
                    )
                    new_value = self._mutate_value(value, sampler, rng)
                    # If still equal (e.g., gaussian on integer), bump it
                    if new_value == value and isinstance(value, (int, float)):
                        new_value = (value + 1) if isinstance(value, int) else (value + 0.001)
                    new_bindings = list(node.arg_bindings)
                    new_bindings[binding_idx] = ("literal", new_value)
                    new_nodes = list(nodes)
                    new_nodes[idx] = NodeRef(
                        callable_ref=node.callable_ref,
                        arg_bindings=tuple(new_bindings),
                    )
                    return new_nodes
        return nodes
