"""ergon.learner.genome — typed DAG genomes over arsenal atoms.

Per pivot/ergon_learner_proposal_v8.md §6.1:

A genome is a small typed DAG over arsenal atoms (target depth <=8,
target width <=5), with leaf-node argument values sampled from per-type
distributions. Each genome serializes deterministically to a content
hash. Two genomes with the same DAG topology and same args are the
same individual.

The arsenal is `prometheus_math.arsenal_meta.ARSENAL_REGISTRY` (~85
entries today, ~2,800+ at scale). Each ArsenalMeta entry provides:
- callable_ref ("module.path:function_name")
- arg_types (Tuple[type, ...])
- return_type (type)
- cost_tier (int, log-binned)
- equivalence_class (canonicalizer subclass tag)
- category (coarse domain bucket)

This module's job: define Genome dataclass + serialization + hashing,
PLUS validation (type-discipline preservation under composition) and
PLUS lineage tagging (mutation_operator_class on every CLAIM).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple


# Mutation operator classes — per v8 §3 + §6.3
MutationOperatorClass = Literal[
    "structural",       # Add/remove/swap nodes; rewire edges
    "symbolic",         # Bump arg values within type
    "neural",           # LoRA-fine-tuned policy mutation (v0.5+)
    "external_llm",     # Frontier LLM API mutation (v0.5+)
    "anti_prior",       # Anti-correlated with corpus frequency stats
    "uniform",          # Resample atoms uniformly (strawman null)
    "structured_null",  # Type-respecting uniform (type-respecting null)
]


@dataclass(frozen=True)
class NodeRef:
    """Reference to one atom invocation in the genome's DAG.

    arg_bindings is a list whose length matches the atom's arg_types
    arity. Each entry is either:
    - ("literal", value) — a concrete value sampled at construction
    - ("ref", source_node_index) — output of another DAG node
    """
    callable_ref: str
    arg_bindings: Tuple[Tuple[str, Any], ...]
    # node_index is implicit from position in genome.nodes


@dataclass(frozen=True)
class Genome:
    """A typed DAG genome over arsenal atoms.

    nodes is a tuple of NodeRef in topological order (each node's "ref"
    bindings can only point to lower-indexed nodes, ensuring DAG-ness).
    edges is computed implicitly from arg_bindings — explicitly stored
    only as a denormalization for fast traversal.

    target_predicate is a free-form string naming what the DAG is
    "supposed to produce" (e.g., "polynomial with M < 1.18"). It does
    not constrain the DAG; it's metadata for lineage tracking.

    mutation_operator_class is the lineage tag set when this genome
    was produced by a mutation operator. Inherited via parent_hash from
    the parent it was mutated from (a genome can have at most one
    parent in this MVP; crossover is deferred to v0.5+).
    """
    nodes: Tuple[NodeRef, ...]
    target_predicate: str
    mutation_operator_class: MutationOperatorClass
    parent_hash: Optional[str] = None  # content-hash of the parent genome (if any)
    # Optional metadata — not used for content-hashing
    metadata: Dict[str, Any] = field(default_factory=dict)

    def edges(self) -> Tuple[Tuple[int, int], ...]:
        """Compute the edge set from arg_bindings.

        Returns tuples (source_node_index, dest_node_index) for every
        ref binding.
        """
        out: List[Tuple[int, int]] = []
        for dest_idx, node in enumerate(self.nodes):
            for binding in node.arg_bindings:
                if binding[0] == "ref":
                    src_idx = int(binding[1])
                    out.append((src_idx, dest_idx))
        return tuple(out)

    def depth(self) -> int:
        """Compute longest path from any source to any sink in the DAG.

        Source nodes (no incoming refs) have depth 0; each ref
        increments depth by 1 from its source.
        """
        if not self.nodes:
            return 0
        depths = [0] * len(self.nodes)
        for idx, node in enumerate(self.nodes):
            ref_depths = [
                depths[int(b[1])] + 1
                for b in node.arg_bindings
                if b[0] == "ref"
            ]
            depths[idx] = max(ref_depths) if ref_depths else 0
        return max(depths)

    def width(self) -> int:
        """Maximum number of nodes at any one depth level.

        Nodes at the same depth could theoretically be evaluated in
        parallel; width measures parallelism opportunity.
        """
        if not self.nodes:
            return 0
        depths = [0] * len(self.nodes)
        for idx, node in enumerate(self.nodes):
            ref_depths = [
                depths[int(b[1])] + 1
                for b in node.arg_bindings
                if b[0] == "ref"
            ]
            depths[idx] = max(ref_depths) if ref_depths else 0
        from collections import Counter
        return max(Counter(depths).values())

    def n_atoms(self) -> int:
        """Number of atom invocations (nodes) in the DAG."""
        return len(self.nodes)

    def root_node(self) -> Optional[NodeRef]:
        """The DAG's root output node — the highest-indexed node with no
        outgoing refs. By convention this is the last node in the topological
        sort; its return_type is the genome's overall output type."""
        if not self.nodes:
            return None
        return self.nodes[-1]

    def content_hash(self) -> str:
        """Deterministic content hash over the DAG structure + args.

        Two genomes with the same DAG topology, same arg-bindings,
        same target_predicate, and same operator-class lineage produce
        the same hash. parent_hash is excluded — two children with
        different parents but identical content are the same individual
        for MAP-Elites purposes.

        The metadata field is excluded from hashing — it's purely for
        downstream tooling and may be mutable.
        """
        canonical = self._canonical_form()
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _canonical_form(self) -> str:
        """Canonical JSON serialization for hashing."""
        nodes_serialized = [
            {
                "callable_ref": n.callable_ref,
                "arg_bindings": [
                    [kind, _coerce_for_canonical(value)]
                    for kind, value in n.arg_bindings
                ],
            }
            for n in self.nodes
        ]
        canonical = {
            "nodes": nodes_serialized,
            "target_predicate": self.target_predicate,
            "operator_class": self.mutation_operator_class,
        }
        return json.dumps(canonical, sort_keys=True, ensure_ascii=True)

    def to_dict(self) -> Dict[str, Any]:
        """Full dict serialization including parent_hash and metadata.

        Used for substrate persistence (sigma_proto.genomes table) and
        for inter-process serialization in the agora.
        """
        return {
            "nodes": [
                {
                    "callable_ref": n.callable_ref,
                    "arg_bindings": list(n.arg_bindings),
                }
                for n in self.nodes
            ],
            "target_predicate": self.target_predicate,
            "mutation_operator_class": self.mutation_operator_class,
            "parent_hash": self.parent_hash,
            "metadata": dict(self.metadata),
            "content_hash": self.content_hash(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Genome":
        """Restore from a dict produced by to_dict()."""
        nodes = tuple(
            NodeRef(
                callable_ref=n["callable_ref"],
                arg_bindings=tuple(tuple(b) for b in n["arg_bindings"]),
            )
            for n in data["nodes"]
        )
        return cls(
            nodes=nodes,
            target_predicate=data["target_predicate"],
            mutation_operator_class=data["mutation_operator_class"],
            parent_hash=data.get("parent_hash"),
            metadata=dict(data.get("metadata", {})),
        )


def _coerce_for_canonical(value: Any) -> Any:
    """Coerce arbitrary arg values into JSON-serializable canonical form.

    Falls back to repr() for non-JSON-serializable types (e.g.,
    sympy expressions, numpy arrays). This is acceptable for hashing
    because two equal Python values produce the same repr in a
    consistent process.
    """
    try:
        json.dumps(value)
        return value
    except (TypeError, ValueError):
        return repr(value)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class GenomeValidationError(ValueError):
    """Raised when a genome violates type-discipline or DAG invariants."""


def validate_dag_invariants(genome: Genome) -> None:
    """Check that arg_bindings of type "ref" only reference lower-indexed nodes.

    This guarantees DAG-ness (no cycles). Raises GenomeValidationError on
    violation.
    """
    for idx, node in enumerate(genome.nodes):
        for kind, value in node.arg_bindings:
            if kind == "ref":
                src_idx = int(value)
                if src_idx >= idx:
                    raise GenomeValidationError(
                        f"Node {idx} ({node.callable_ref}) has ref binding to "
                        f"node {src_idx}; refs must point to lower indices "
                        f"(DAG invariant)"
                    )
                if src_idx < 0:
                    raise GenomeValidationError(
                        f"Node {idx} has negative ref index {src_idx}"
                    )


def validate_type_discipline(
    genome: Genome,
    arsenal_lookup: Dict[str, Any],  # callable_ref -> ArsenalMeta-like
) -> None:
    """Check that ref bindings respect type compatibility.

    For each node, each "ref" arg_binding must point to a source node
    whose return_type matches (or is a subtype of) the consumer's
    arg_type at that position.

    This is a v0.5+ refinement; at MVP we accept any ref binding as
    type-compatible (the arsenal's typed-composition discipline is not
    fully enforced until v0.5 when arsenal_meta is wired to provide
    precise type info per arg position).
    """
    # MVP placeholder: no-op. Full implementation in v0.5 once
    # arsenal_meta exposes per-arg type information uniformly.
    _ = (genome, arsenal_lookup)
    return None


# ---------------------------------------------------------------------------
# Constants per v8 §6.1
# ---------------------------------------------------------------------------

MAX_DEPTH = 8   # Target max depth per v6/v8
MAX_WIDTH = 5   # Target max width per v6/v8
MAX_ATOMS = 20  # Soft upper bound on total nodes per genome
