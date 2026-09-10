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
#: a deliberate, visible act rather than a drift. It was widened once, on
#: 2026-09-09, by exactly one field -- see ADDRESSING below.
FIELDS = ("experiment_id", "spec_json", "spec_hash", "artifact_locators")


class SpecIntegrityError(RuntimeError):
    """The spec and its sealed hash disagree."""


@dataclass(frozen=True)
class ExecutionRequest:
    experiment_id: str
    spec_json: bytes
    spec_hash: str
    #: ADDRESSING, and a third category on purpose. digest -> {source_world,
    #: source_artifact}: where a copy of already-sealed bytes may be found.
    #:
    #: It is not sealed input -- the spec names the bytes and this only says
    #: where they live. It is not provenance either -- created_by and arm_id
    #: describe a decision, and preflight would work identically without them,
    #: whereas without an address nothing resolves at all.
    #:
    #: Widening a deliberately three-field object is not a small act, so here
    #: is the argument that it does not reopen the hole it was built to close.
    #: Preflight verifies every resolved artifact against the digest inside
    #: spec_hash. A locator therefore has two possible effects and no third:
    #: the sealed bytes arrive, or the attempt is REJECTED. It cannot change
    #: what the experiment computes, only whether it computes at all -- and
    #: tests/test_h0h5_artifacts.py asserts exactly that by running the same
    #: spec through two different locators over byte-identical artifacts and
    #: comparing results.
    #:
    #: Keyed by DIGEST rather than by slot name so that dependencies deep in a
    #: closure address the same way roots do, and so that the address book
    #: cannot carry a key the sealed spec never mentions.
    artifact_locators: dict = None

    def __post_init__(self):
        if not isinstance(self.spec_json, bytes):
            raise TypeError("spec_json must be canonical bytes")
        object.__setattr__(self, "artifact_locators",
                           dict(self.artifact_locators or {}))
        for digest, loc in self.artifact_locators.items():
            if not isinstance(digest, str) or not digest.startswith("sha256:"):
                raise SpecIntegrityError(
                    "artifact_locators is keyed by content digest; %r is not "
                    "one" % (digest,))
            if not isinstance(loc, dict):
                raise SpecIntegrityError(
                    "locator for %s must be an object" % digest)
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

        Names exactly four columns. Everything else on the row -- created_by,
        source_reason, source_evidence, family_id, arm_id, candidate_set_id,
        priority, claimed_by -- is deliberately not read, and is unreachable
        from the object this returns.
        """
        spec = row["experiment_spec"]
        sealed = row["spec_hash"]
        canonical = _spec.canonical_bytes(spec)
        # Construction verifies the hash, so a stored spec that no longer
        # hashes to its seal fails HERE, before any engine call.
        # Named EXPLICITLY, like the other three. `.get`-style access on a
        # DB row is how a projection quietly becomes "whatever the row has".
        locators = None
        try:
            locators = row["artifact_locators"]
        except (KeyError, IndexError, TypeError):
            locators = None
        return cls(experiment_id=str(row["experiment_id"]),
                   spec_json=canonical, spec_hash=sealed,
                   artifact_locators=locators)


def field_names() -> tuple:
    return tuple(f.name for f in fields(ExecutionRequest))
