"""0f-b: pinned parity fixtures for every kind whose executor lives here.

A hash per (kind, payload, seed). If an executor's output changes for pinned
inputs, this fails and names which one -- so a refactor that quietly moves a
number cannot pass as a green suite. These are the hashes an external owner's
library must reproduce to claim parity with the wrapper.

Generated 2026-09-08 against WP-0f. Regenerating them is a deliberate act: a
changed hash means the kind now returns something different for the same
declared inputs, which is a contract change and needs saying out loud.
"""
from __future__ import annotations

import hashlib
import json

import pytest

from artifact_fixtures import LocalResolver, input_set, probe_spec
from viv import executors as _ex
from viv import kinds as _kinds
from viv import preflight as _pf
from viv import spec as _spec

#: The pinned CA fixture's payload is a plain dict; an artifact-consuming kind's
#: is not -- its slot's digest depends on bytes, so the fixture has to build the
#: bytes to know what to pin. Fixed content, fixed digest, fixed result.
_PROBE_ITEMS = [[0, 0, 1], [1, 1, 0], [1, 0, 1], [0, 1, 1]]
_PROBE_OBJ, _PROBE_RAW, _PROBE_SLOT = input_set(_PROBE_ITEMS)
_PROBE_PAYLOAD = {"failure_inputs": _PROBE_SLOT, "reduction": "popcount"}

FIXTURES = [
    ("noop_v0", {}, 1, "2d7c17e7a3c9dfabed97aea8baaef615"),
    ("evaluate_bitstring", {"bits": "0" * 24, "length": 24}, 424242,
     "bed9fcf13c7df0827e535728c3027c57"),
    ("evaluate_bitstring", {"bits": "1" * 32, "length": 32}, 7,
     "817fa44dd471435309eabf811c9bfd22"),
    ("random_walk_v0", {"steps": 3, "step_scale": 1.0}, 99,
     "c31ff4d75dc898844fad6b21d4c1767e"),
    ("random_walk_v0", {"steps": 7, "step_scale": 0.25}, 12345,
     "d704de2d9fb0b8ec0f79f22cbb8aa57a"),
    # C1. The strong parity anchor for this kind is the six golden genomes in
    # test_c1_ca_density.py; this pins the WRAPPER's whole result object so the
    # coverage guard below holds for every implemented kind uniformly.
    ("ca_density_v0",
     {"rule_hex": "0504058705000f77037755837bffb77f",   # `par`
      "radius": 3, "n_cells": 21, "steps": 42, "n_ic": 16,
      "ic_density_set": [None], "success_criterion": "at_T"},
     20260908, "0902beb4702815f25760bf9766c6ea9d"),
    # The loader's own kind. Its parity anchor is the executor's arithmetic
    # over a FIXED input artifact: the digest below is the digest of those
    # exact bytes, so a change to the canonical encoding, the interface shape
    # or the fold all land here. Authorization is NOT what this pins -- that is
    # the engine's answer and is tested against a real engine in
    # tests/test_h0h5_slice.py.
    ("artifact_probe_v1", _PROBE_PAYLOAD, 20260909,
     "5661273cec71be885e831a8301e5036e"),
]


def _hydrate_for(kind, payload):
    """The frozen inputs an artifact-consuming kind needs, or None."""
    k = _kinds.get(kind)
    if not k.artifact_slots:
        return None
    slot = payload["failure_inputs"]
    resolver = LocalResolver({slot["digest"]: (_PROBE_RAW, "w-src", "art-1")})
    pf = _pf.Preflight(
        resolver=resolver,
        locators={slot["digest"]: {"source_world": "w-src",
                                   "source_artifact": "art-1"}})
    inputs, _receipt = pf.hydrate({"failure_inputs": slot})
    return inputs


def _spec_for(kind, payload, seed):
    return {"spec_version": 3, "world": {"seed_root": seed},
            "hypothesis": "fixture", "prediction": None,
            "work": {"kind": kind, "payload": payload},
            "outcome_rule": {"field": "executor", "op": "==", "value": kind,
                             "if_true": "SURVIVED", "if_false": "FALSIFIED",
                             "if_indeterminate": "INCONCLUSIVE",
                             "aggregate": "first"},
            "pew": None,
            "repeat": {"count": 1, "order": "sequential",
                       "seed_derivation": "constant", "state": "reset",
                       "budget": {"max_seconds": 60, "max_observations": 1}}}


def _digest(out) -> str:
    blob = json.dumps(out, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode()
    return hashlib.sha256(blob).hexdigest()[:32]


@pytest.mark.parametrize("kind,payload,seed,expected", FIXTURES)
def test_0f_b_the_executor_reproduces_its_pinned_fixture(kind, payload, seed,
                                                         expected):
    spec = _spec_for(kind, payload, seed)
    _spec.validate(spec)
    out = _ex.run(spec, seed=seed, state=_ex.new_state(kind),
                  inputs=_hydrate_for(kind, payload))
    assert _digest(out) == expected, (
        "%s changed for pinned inputs: %s" % (kind, json.dumps(out,
                                                               sort_keys=True)))


@pytest.mark.parametrize("kind,payload,seed,expected", FIXTURES)
def test_0f_b_every_fixture_satisfies_the_declared_result_schema(kind, payload,
                                                                 seed,
                                                                 expected):
    """Parity is only meaningful if the shape is the declared one."""
    spec = _spec_for(kind, payload, seed)
    out = _ex.run(spec, seed=seed, state=_ex.new_state(kind),
                  inputs=_hydrate_for(kind, payload))
    meta = _kinds.get(kind).check_result(dict(out))
    assert meta["validated"] is True


@pytest.mark.parametrize("kind,payload,seed,expected", FIXTURES)
def test_0f_b_re_execution_is_bit_identical(kind, payload, seed, expected):
    """Repeatability under tested conditions -- not a determinism proof, and
    not recorded as one (WP-X2 wording)."""
    spec = _spec_for(kind, payload, seed)
    a = _ex.run(spec, seed=seed, state=_ex.new_state(kind),
                inputs=_hydrate_for(kind, payload))
    b = _ex.run(spec, seed=seed, state=_ex.new_state(kind),
                inputs=_hydrate_for(kind, payload))
    assert _digest(a) == _digest(b) == expected
    assert a.get("reproducibility") == "BIT_DETERMINISTIC"


def test_every_implemented_kind_has_at_least_one_fixture():
    """A kind with an executor and no pinned fixture can drift unobserved."""
    covered = {k for k, _, _, _ in FIXTURES}
    implemented = set(_kinds.implemented())
    assert implemented <= covered, (
        "no parity fixture for %s" % sorted(implemented - covered))
