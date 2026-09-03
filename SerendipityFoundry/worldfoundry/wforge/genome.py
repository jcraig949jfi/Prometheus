"""World genome: identity, canonical hashing, lineage, mutation operators.

Invariants (mirrors schemas/world_genome.schema.v0.json):
  * expansion is a pure function of (grammar_version, generation_seed, mutations)
  * worlds are immutable; mutation returns a DESCENDANT genome
  * content hash covers the canonical serialization; world_id = hash prefix
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("ascii")


def content_hash(obj) -> str:
    return hashlib.sha256(_canon(obj)).hexdigest()


@dataclass(frozen=True)
class MutationOp:
    op: str          # PARAM_PERTURB | PRIMITIVE_INSERT | PRIMITIVE_DELETE | REWIRE | BUDGET_MUTATE | INTERFACE_MUTATE
    op_seed: int
    detail: str = ""


@dataclass(frozen=True)
class WorldGenome:
    grammar_version: str
    generation_seed: int
    parent_ids: tuple = ()
    mutation_history: tuple = ()   # tuple[MutationOp]

    def payload(self) -> dict:
        return {
            "schema_version": "worldfoundry.world_genome.v0",
            "grammar_version": self.grammar_version,
            "generation_seed": self.generation_seed,
            "parent_ids": list(self.parent_ids),
            "mutation_history": [asdict(m) for m in self.mutation_history],
        }

    @property
    def world_id(self) -> str:
        return "W" + content_hash(self.payload())[:16]


def de_novo(grammar_version: str, seed: int) -> WorldGenome:
    return WorldGenome(grammar_version=grammar_version, generation_seed=seed)


def mutate(parent: WorldGenome, op: str, op_seed: int, detail: str = "") -> WorldGenome:
    """Descendant genome. NEVER edits the parent. The mutation op is applied at
    EXPANSION time (grammar interprets the history), so re-expansion of the
    descendant reproduces the mutated world bit-for-bit from the genome alone."""
    return WorldGenome(
        grammar_version=parent.grammar_version,
        generation_seed=parent.generation_seed,
        parent_ids=(parent.world_id,),
        mutation_history=parent.mutation_history + (MutationOp(op, op_seed, detail),),
    )
