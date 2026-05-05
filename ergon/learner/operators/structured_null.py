"""structured_null operator — type-respecting null.

Per pivot/ergon_learner_proposal_v8.md S6.3:

The structured_null operator is between uniform (no prior, no
selection) and the prior-shaped operators (structural, symbolic,
neural, anti_prior). It samples atoms uniformly but respects type-
discipline: when an atom requires a specific arg_type (integer / real /
modular_form_label / etc.), the sampler chooses from that type's
distribution rather than uniform-over-everything.

This is the "type-respecting random" baseline — answers the question
"does the LLM prior beat type-respecting random?" rather than just
"does the LLM prior beat noise?"

Per minimum-share enforcement (v8 S3.5.4), structured_null is
guaranteed >=5% of all proposals.

Lineage tag: "structured_null"
"""
from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from ergon.learner.genome import Genome, NodeRef, validate_dag_invariants
from ergon.learner.operators.base import sample_args_for_atom


class StructuredNullOperator:
    """Type-respecting null: uniform over atoms, type-respecting over args."""

    operator_class = "structured_null"

    def __init__(self, n_atoms_distribution: Optional[tuple] = None):
        self.n_atoms_distribution = n_atoms_distribution or (1, 6)

    def mutate(
        self,
        parent: Optional[Genome],  # ignored
        rng: random.Random,
        atom_pool: Dict[str, Any],
    ) -> Genome:
        """Produce a fresh genome with type-respecting arg sampling.

        Distinct from uniform: when sampling atom args, uses each arg's
        sampler distribution (rather than uniform-over-everything as in
        uniform's fallback). Also applies type-aware ref-vs-literal
        decisions when atoms can consume previous atoms' outputs.
        """
        callable_refs = list(atom_pool.keys())
        n_atoms = rng.randint(*self.n_atoms_distribution)

        nodes: List[NodeRef] = []
        for i in range(n_atoms):
            cref = rng.choice(callable_refs)
            atom = atom_pool[cref]

            # For each arg, decide whether to use a ref binding (if a
            # type-compatible source exists) or a literal sampled from
            # the atom's per-arg sampler.
            bindings = []
            for arg_idx in range(atom["arity"]):
                arg_type = (
                    atom["arg_types"][arg_idx]
                    if arg_idx < len(atom["arg_types"])
                    else None
                )
                # Find lower-indexed nodes whose return_type matches
                type_compat_refs = [
                    j for j in range(i)
                    if atom_pool.get(nodes[j].callable_ref, {}).get("return_type") == arg_type
                ]

                if type_compat_refs and rng.random() < 0.4:
                    # Use a type-compatible ref binding (40% chance when available)
                    src = rng.choice(type_compat_refs)
                    bindings.append(("ref", src))
                else:
                    # Sample a literal from the atom's per-arg sampler
                    args = sample_args_for_atom(cref, atom_pool, rng)
                    if arg_idx < len(args):
                        bindings.append(("literal", args[arg_idx]))
                    else:
                        bindings.append(("literal", rng.randint(1, 100)))

            nodes.append(NodeRef(
                callable_ref=cref,
                arg_bindings=tuple(bindings),
            ))

        g = Genome(
            nodes=tuple(nodes),
            target_predicate="MVP search target",
            mutation_operator_class="structured_null",
        )
        validate_dag_invariants(g)
        return g
