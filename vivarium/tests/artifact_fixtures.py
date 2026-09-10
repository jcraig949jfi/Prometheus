"""Shared builders for artifact-consuming specs, and an in-process resolver.

WHAT THE IN-PROCESS RESOLVER IS AND IS NOT FOR. The brief is explicit: "a test
using only an in-memory fake SFE is not the complete vertical-slice receipt".
It is not used for one. The vertical slice runs against a real engine, a real
database and a real PEW namespace in tests/test_h0h5_slice.py, and every
boundary case the order lists is a real execution there.

This resolver exists for the things that are about ARITHMETIC rather than
authority -- the pinned executor fixture, the codec's canonical round-trip, the
closure and limit algebra -- where a network round trip would add nothing but
minutes. Anything that turns on who may read what is tested against the engine,
because only the engine can answer that.
"""
from __future__ import annotations

from viv import artifacts as _a


def input_set(items, *, n_bits=None, dependencies=()):
    """Build a `failure_input_set` object, its canonical bytes and its slot."""
    if n_bits is None:
        n_bits = len(items[0]) if items else 1
    obj = {"artifact_type": "failure_input_set", "schema_version": "1",
           "interface_id": "boolean-inputs-v1", "n_bits": n_bits,
           "items": [list(r) for r in items]}
    if dependencies:
        obj["dependencies"] = [dict(d) for d in dependencies]
    raw = _a.canonical_bytes(obj)
    slot = {"digest": _a.digest_of(raw), "artifact_type": "failure_input_set",
            "schema_version": "1", "codec": "canonical-json-v1",
            "expected_bytes": len(raw), "interface_id": "boolean-inputs-v1"}
    return obj, raw, slot


def probe_spec(slot, *, reduction="xor_positional", seed_root=20260909,
               pew=None,
               hypothesis="the loader hands a kind exactly the bytes its "
                          "sealed digest names"):
    """A valid v3 spec for artifact_probe_v1 consuming `slot`."""
    return {
        "spec_version": 3,
        "world": {"seed_root": seed_root},
        "hypothesis": hypothesis,
        "prediction": None,
        "work": {"kind": "artifact_probe_v1",
                 "payload": {"failure_inputs": dict(slot),
                             "reduction": reduction}},
        "outcome_rule": {"field": "executor", "op": "==",
                         "value": "artifact_probe_v1",
                         "if_true": "SURVIVED", "if_false": "FALSIFIED",
                         "if_indeterminate": "INCONCLUSIVE",
                         "aggregate": "first"},
        "pew": pew,
        "repeat": {"count": 1, "order": "sequential",
                   "seed_derivation": "constant", "state": "reset",
                   "budget": {"max_seconds": 60, "max_observations": 1}},
    }


class LocalResolver:
    """digest -> bytes, behind an explicit authorization set.

    Deliberately shaped like the real one: it can REFUSE, and the refusal it
    raises is the same class the engine's 403 maps to. A double that can only
    succeed would make the loader look correct by never exercising it.
    """

    def __init__(self, store, *, client_id="test-client", world="w-exec",
                 authorized=None):
        #: digest -> (bytes, source_world, source_artifact)
        self.store = dict(store)
        self.client_id = client_id
        self.world = world
        #: worlds this principal may read from; None = all of them
        self.authorized = authorized
        self.calls = 0
        self.seen = []

    @property
    def principal(self):
        return (self.client_id, self.world)

    def resolve(self, digest, locator):
        self.calls += 1
        self.seen.append((digest, dict(locator)))
        entry = self.store.get(digest)
        if entry is None:
            raise _a.PreflightRejected(
                _a.ABSENT, "no such artifact in this store",
                detail={"digest": digest, "locator": dict(locator)})
        raw, world, aid = entry
        if world != locator["source_world"] or aid != locator["source_artifact"]:
            raise _a.PreflightRejected(
                _a.ABSENT, "the locator addresses nothing here",
                detail={"digest": digest, "locator": dict(locator)})
        if self.authorized is not None and world not in self.authorized:
            raise _a.PreflightRejected(
                _a.UNAUTHORIZED,
                "this principal may not read world %s" % world,
                detail={"digest": digest, "locator": dict(locator)})
        return raw, {"execution_world": self.world, "source_world": world,
                     "source_artifact": aid, "origin": "IMPORTED",
                     "authorized_as": self.client_id, "served_from": "engine"}
