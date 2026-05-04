"""Mutation operator protocol — common interface for all 7 classes.

Per pivot/ergon_learner_proposal_v8.md S3:

Each operator class produces a child Genome from a parent Genome (or
from scratch, for null operators). Every CLAIM resulting from mutation
carries the lineage tag mutation_operator_class.

The protocol is simple: take a parent Genome (or None for from-scratch),
return a child Genome with the operator's class as its lineage tag.

The operator pool used at MVP scope (no neural / external_llm):
  - structural: DAG topology mutation
  - symbolic: argument-value mutation
  - uniform: pure random resample
  - structured_null: type-respecting random
  - anti_prior: anti-correlated with corpus frequency stats

Each ships as its own module with a class implementing MutationOperator.
"""
from __future__ import annotations

import random
from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple

from ergon.learner.genome import (
    Genome,
    MutationOperatorClass,
    NodeRef,
    validate_dag_invariants,
)


class MutationOperator(Protocol):
    """Common interface for all mutation operator classes."""

    operator_class: MutationOperatorClass

    def mutate(
        self,
        parent: Optional[Genome],
        rng: random.Random,
        atom_pool: Dict[str, Any],
    ) -> Genome:
        """Produce a child Genome from the parent (or fresh if None).

        Args:
          parent: parent genome (None for from-scratch construction)
          rng: random.Random instance for reproducibility
          atom_pool: callable_ref -> ArsenalMeta-like (for type-respecting ops)

        Returns:
          A new Genome with content_hash distinct from parent's, tagged
          with this operator's class.
        """
        ...


# ---------------------------------------------------------------------------
# Atom pool helper — minimal MVP-grade atom registry
# ---------------------------------------------------------------------------
#
# At MVP we use a hand-curated atom pool. v0.5 swaps to
# prometheus_math.arsenal_meta.ARSENAL_REGISTRY. The pool's structure is
# {callable_ref: {arity: int, arg_types: tuple, return_type: str}}.


def make_mvp_atom_pool() -> Dict[str, Dict[str, Any]]:
    """Hand-curated MVP atom pool covering 12 representative arsenal callables.

    Each entry:
      arity: number of args
      arg_types: tuple of type-tags (used for type-respecting operators)
      return_type: output type-tag
      cost_tier: log-bucketed cost (for fitness)
      arg_samplers: per-arg distribution name (for symbolic mutation)
    """
    return {
        # Numerics-special — 4 atoms
        "prometheus_math.numerics_special_dilogarithm:dilogarithm": {
            "arity": 1, "arg_types": ("real",), "return_type": "real_scalar",
            "cost_tier": 1, "arg_samplers": ("real_unit_interval",),
        },
        "prometheus_math.numerics_special_dilogarithm:polylogarithm": {
            "arity": 2, "arg_types": ("integer", "real"), "return_type": "real_scalar",
            "cost_tier": 1, "arg_samplers": ("integer_small", "real_unit_interval"),
        },
        "prometheus_math.numerics_special_eta:eta_function": {
            "arity": 1, "arg_types": ("complex",), "return_type": "complex_scalar",
            "cost_tier": 2, "arg_samplers": ("complex_unit_disk",),
        },
        "prometheus_math.numerics_special_theta:theta_3": {
            "arity": 2, "arg_types": ("complex", "complex"), "return_type": "complex_scalar",
            "cost_tier": 2, "arg_samplers": ("complex_unit_disk", "complex_unit_disk"),
        },
        # Number theory — 3 atoms
        "prometheus_math.number_theory:hecke_eigenvalue": {
            "arity": 2, "arg_types": ("integer", "modular_form_label"),
            "return_type": "complex_scalar", "cost_tier": 3,
            "arg_samplers": ("integer_small", "modular_form_label"),
        },
        "prometheus_math.number_theory:euler_phi": {
            "arity": 1, "arg_types": ("integer",), "return_type": "integer",
            "cost_tier": 1, "arg_samplers": ("integer_small",),
        },
        "prometheus_math.number_theory:legendre_symbol": {
            "arity": 2, "arg_types": ("integer", "integer"),
            "return_type": "integer", "cost_tier": 1,
            "arg_samplers": ("integer_small", "integer_small_odd_prime"),
        },
        # Elliptic curves — 2 atoms
        "prometheus_math.elliptic_curves:point_count": {
            "arity": 2, "arg_types": ("ec_label", "integer"),
            "return_type": "integer", "cost_tier": 3,
            "arg_samplers": ("ec_label", "integer_small_prime"),
        },
        "prometheus_math.elliptic_curves:isogeny_class": {
            "arity": 1, "arg_types": ("ec_label",),
            "return_type": "tuple_or_record", "cost_tier": 4,
            "arg_samplers": ("ec_label",),
        },
        # Combinatorics — 2 atoms
        "prometheus_math.combinatorics:partition_function": {
            "arity": 1, "arg_types": ("integer",),
            "return_type": "integer", "cost_tier": 2,
            "arg_samplers": ("integer_small",),
        },
        "prometheus_math.combinatorics_partitions:partition_count_with_parts": {
            "arity": 2, "arg_types": ("integer", "integer"),
            "return_type": "integer", "cost_tier": 2,
            "arg_samplers": ("integer_small", "integer_small"),
        },
        # Optimization — 1 atom
        "prometheus_math.optimization:lehmer_mahler_search": {
            "arity": 2, "arg_types": ("integer", "integer"),
            "return_type": "polynomial", "cost_tier": 4,
            "arg_samplers": ("integer_small", "integer_small"),
        },
    }


# ---------------------------------------------------------------------------
# Argument samplers — deterministic given rng
# ---------------------------------------------------------------------------


def sample_arg(arg_sampler_name: str, rng: random.Random) -> Any:
    """Sample a single argument from the named distribution.

    These are MVP defaults; v0.5 swaps to per-arsenal-atom samplers
    pulled from arsenal_meta.
    """
    if arg_sampler_name == "real_unit_interval":
        return rng.uniform(0.0, 1.0)
    if arg_sampler_name == "complex_unit_disk":
        # Real + imaginary in [-1, 1]
        return (rng.uniform(-1.0, 1.0), rng.uniform(-1.0, 1.0))
    if arg_sampler_name == "integer_small":
        return rng.randint(1, 100)
    if arg_sampler_name == "integer_small_prime":
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]
        return rng.choice(primes)
    if arg_sampler_name == "integer_small_odd_prime":
        primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]
        return rng.choice(primes)
    if arg_sampler_name == "modular_form_label":
        labels = ["11.2.a.a", "23.2.a.a", "37.2.a.a", "37.2.a.b", "37.2.b.a"]
        return rng.choice(labels)
    if arg_sampler_name == "ec_label":
        labels = ["11.a1", "11.a2", "11.a3", "37.a1", "389.a1", "5077.a1"]
        return rng.choice(labels)
    # Unknown sampler: return a small integer as a sensible fallback
    return rng.randint(1, 10)


def sample_args_for_atom(
    callable_ref: str,
    atom_pool: Dict[str, Dict[str, Any]],
    rng: random.Random,
) -> Tuple[Any, ...]:
    """Sample argument values for an atom according to its samplers."""
    atom = atom_pool.get(callable_ref)
    if atom is None:
        return ()
    return tuple(sample_arg(s, rng) for s in atom["arg_samplers"])


def make_node_for_atom(
    callable_ref: str,
    atom_pool: Dict[str, Dict[str, Any]],
    rng: random.Random,
    refs_available: Optional[List[int]] = None,
) -> NodeRef:
    """Create a NodeRef for an atom; bindings are all literals at MVP-scope.

    refs_available: indices of lower-numbered nodes that this node could
    optionally reference. At MVP we use literals exclusively for simplicity;
    structural operator handles ref-vs-literal mixing.
    """
    args = sample_args_for_atom(callable_ref, atom_pool, rng)
    return NodeRef(
        callable_ref=callable_ref,
        arg_bindings=tuple(("literal", v) for v in args),
    )


# ---------------------------------------------------------------------------
# Helper: build a fresh genome from atom_pool
# ---------------------------------------------------------------------------


def fresh_genome(
    atom_pool: Dict[str, Dict[str, Any]],
    rng: random.Random,
    operator_class: MutationOperatorClass,
    n_atoms: int = 3,
    target_predicate: str = "MVP search target",
) -> Genome:
    """Build a fresh chain genome of n_atoms randomly-sampled atoms.

    Used by null operators (uniform, structured_null) and as a fallback
    when other operators have no parent to mutate from.
    """
    callable_refs = list(atom_pool.keys())
    nodes: List[NodeRef] = []
    for i in range(n_atoms):
        cref = rng.choice(callable_refs)
        atom = atom_pool[cref]
        # First node uses literals only; subsequent nodes can ref previous
        # but for MVP simplicity keep literal bindings (structural operator
        # introduces refs explicitly).
        node = make_node_for_atom(cref, atom_pool, rng, refs_available=list(range(i)))
        nodes.append(node)

    g = Genome(
        nodes=tuple(nodes),
        target_predicate=target_predicate,
        mutation_operator_class=operator_class,
    )
    validate_dag_invariants(g)
    return g
