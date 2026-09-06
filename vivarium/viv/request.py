"""ExecutionRequest -- the ONLY object that crosses into execution.

The queue row carries three kinds of fact: the sealed execution inputs, the
provenance (who asked, why, under which policy, in which arm), and the result.
Only the first kind may reach the executor. Before this existed, `loop`
handed the whole row to `runner.run()`, so `created_by="archaeon:C_frozen_S17"`
sat inside the object the apparatus held -- and "we checked, it does not look"
is a code review that has to be repeated forever, not a property.

This is that property. An ExecutionRequest has exactly three fields and there
is no way to reach the queue row from one. `runner.run()` accepts nothing else,
so provenance cannot cross the boundary through the supported interface --
which is the claim the blinding test is required to establish, and a stronger
one than "the executor currently ignores provenance".

SELF-VERIFYING. The request holds the spec as CANONICAL BYTES and checks at
construction that they hash to the sealed hash it was handed. A corrupted or
tampered spec therefore cannot be packaged into a request at all, let alone
executed, and `.spec` hands out a fresh parse each time so no caller can mutate
what a later caller sees.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, fields
from typing import Any

from . import spec as _spec

#: The exact field set. tests/test_blinding.py asserts this, so widening it is
#: a deliberate, visible act rather than a drift.
FIELDS = ("experiment_id", "spec_json", "spec_hash")


class SpecIntegrityError(RuntimeError):
    """The spec and its sealed hash disagree."""


@dataclass(frozen=True)
class ExecutionRequest:
    experiment_id: str
    spec_json: bytes
    spec_hash: str

    def __post_init__(self):
        if not isinstance(self.spec_json, bytes):
            raise TypeError("spec_json must be canonical bytes")
        recomputed = "sha256:" + __import__("hashlib").sha256(
            self.spec_json).hexdigest()
        if recomputed != self.spec_hash:
            raise SpecIntegrityError(
                "spec does not hash to its sealed hash: sealed=%s "
                "recomputed=%s" % (self.spec_hash, recomputed))

    @property
    def spec(self) -> dict:
        """A fresh parse every time; mutation cannot propagate."""
        return json.loads(self.spec_json)

    @classmethod
    def from_queue_row(cls, row: Any) -> "ExecutionRequest":
        """The projection, and the only one.

        Names exactly three columns. Everything else on the row -- created_by,
        source_reason, source_evidence, family_id, arm_id, candidate_set_id,
        priority, claimed_by -- is deliberately not read, and is unreachable
        from the object this returns.
        """
        spec = row["experiment_spec"]
        sealed = row["spec_hash"]
        canonical = _spec.canonical_bytes(spec)
        # Construction verifies the hash, so a stored spec that no longer
        # hashes to its seal fails HERE, before any engine call.
        return cls(experiment_id=str(row["experiment_id"]),
                   spec_json=canonical, spec_hash=sealed)


def field_names() -> tuple:
    return tuple(f.name for f in fields(ExecutionRequest))
